# フロントエンド資料の画面を自動撮影する（赤枠と番号つき）。
# 使い方は README.md を参照。Playwright（Python）が必要。
import argparse
import os
import pathlib
import sys

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from shots import SHOTS

OUT_DIR = pathlib.Path(__file__).resolve().parent.parent / "app"
NUMBERS = "①②③④⑤⑥⑦⑧⑨"

# アニメーションを止める CSS
NO_ANIMATION = "*, *::before, *::after { transition: none !important; animation: none !important; }"

# 赤枠と番号を付ける（ページに注入するスクリプト）。矩形はビューポート内の座標（position: fixed）で描く。
MARK_JS = """
(args) => {
  const [rect, label] = args;
  const box = document.createElement('div');
  box.className = '__mark';
  box.style.cssText = `position:fixed;left:${rect.x - 2}px;top:${rect.y - 2}px;`
    + `width:${rect.width + 4}px;height:${rect.height + 4}px;`
    + 'border:3px solid #d32f2f;border-radius:4px;pointer-events:none;z-index:2147483647;'
    + 'margin:0;padding:0;background:transparent;overflow:visible;inset:auto;';
  box.style.left = `${rect.x - 2}px`; box.style.top = `${rect.y - 2}px`;
  if (label) {
    const n = document.createElement('div');
    n.textContent = label;
    n.style.cssText = 'position:absolute;left:-14px;top:-14px;width:24px;height:24px;'
      + 'border-radius:50%;background:#d32f2f;color:#fff;font:bold 14px sans-serif;'
      + 'display:flex;align-items:center;justify-content:center;';
    box.appendChild(n);
  }
  document.body.appendChild(box);
  // ダイアログや通知は「最前面（top layer）」に出るので、赤枠も、最前面に出す
  box.popover = 'manual';
  box.showPopover();
}
"""


def login(page, base_url, user):
    password = os.environ.get("CAPTURE_PASSWORD")
    if not password:
        sys.exit("環境変数 CAPTURE_PASSWORD（撮影用の仮のパスワード）を設定してください")
    page.goto(f"{base_url}/login")
    page.get_by_label("ユーザー名").fill(user)
    page.get_by_label("パスワード", exact=True).fill(password)
    page.get_by_role("button", name="ログイン").click()
    page.wait_for_url(lambda url: "/login" not in url, timeout=15000)
    page.wait_for_load_state("networkidle")


def run_steps(page, steps):
    for step in steps:
        kind = step[0]
        if kind == "fill":                     # ("fill", ラベル, 値)
            page.get_by_label(step[1], exact=True).fill(step[2])
        elif kind == "choose":                   # ("choose", ラベル, 選択肢の文字)  Select / ComboBox
            page.get_by_label(step[1], exact=True).click()
            page.get_by_role("option", name=step[2]).first.click()
        elif kind == "click":                    # ("click", ボタンの文字)
            page.get_by_role("button", name=step[1]).first.click()
        elif kind == "wait":                     # ("wait", ミリ秒)
            page.wait_for_timeout(step[1])
        else:
            sys.exit(f"未知の操作です: {kind}")


def shoot(browser, base_urls, shot):
    context = browser.new_context(
        viewport={"width": shot.get("width", 1280), "height": shot.get("height", 800)},
        locale="ja-JP",
        color_scheme="light",
        device_scale_factor=2,           # 画像を見る人のために、高解像度で撮る
    )
    page = context.new_page()
    base_url = base_urls[shot.get("base", "main")]
    try:
        if shot["user"]:
            login(page, base_url, shot["user"])
        page.goto(base_url + shot["path"])
        page.wait_for_load_state("networkidle")
        page.add_style_tag(content=NO_ANIMATION)
        page.wait_for_timeout(shot.get("settle", 800))      # Web Components の描画を待つ
        run_steps(page, shot["steps"])
        page.wait_for_timeout(300)
        for selector, number in shot["marks"]:
            try:
                rect = page.locator(selector).first.bounding_box(timeout=4000)
            except PlaywrightTimeoutError:
                rect = None
            if rect is None:
                raise RuntimeError(f"見つかりません: {selector}")
            label = NUMBERS[number - 1] if number else None
            page.evaluate(MARK_JS, [rect, label])
        target = page.locator(shot["clip"]) if shot.get("clip") else page
        target.screenshot(path=str(OUT_DIR / f"{shot['name']}.png"))
        print("撮影:", shot["name"])
    finally:
        context.close()


def main():
    parser = argparse.ArgumentParser(description="資料用の画面を自動撮影する")
    parser.add_argument("--base-url", default="http://localhost:8080", help="サンプルのアプリの URL")
    parser.add_argument("--alt-url", action="append", default=[], metavar="名前=URL",
                        help="別の設定で起動したアプリ（例：lumo=http://localhost:8081）")
    parser.add_argument("--only", help="この名前（前方一致）の撮影だけを行う")
    args = parser.parse_args()

    base_urls = {"main": args.base_url.rstrip("/")}
    for item in args.alt_url:
        name, _, url = item.partition("=")
        base_urls[name] = url.rstrip("/")

    shots = [s for s in SHOTS if not args.only or s["name"].startswith(args.only)]
    shots = [s for s in shots if s.get("base", "main") in base_urls]
    if not shots:
        sys.exit("対象の撮影が見つかりません")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        # Playwright の Chromium がなければ、インストール済みの Chrome を使う（CAPTURE_BROWSER_CHANNEL=chrome）
        channel = os.environ.get("CAPTURE_BROWSER_CHANNEL")
        browser = p.chromium.launch(channel=channel) if channel else p.chromium.launch()
        failed = []
        for shot in shots:
            try:
                shoot(browser, base_urls, shot)
            except Exception as e:                       # 1 枚の失敗で、ほかの撮影を止めない
                failed.append(shot["name"])
                print(f"失敗: {shot['name']}: {str(e).splitlines()[0]}")
        browser.close()
    if failed:
        sys.exit(f"{len(failed)} 枚の撮影に失敗しました")


if __name__ == "__main__":
    main()
