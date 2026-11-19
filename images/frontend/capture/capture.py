# フロントエンド資料の画面を自動撮影する（赤枠と番号つき）。
# 使い方は README.md を参照。Playwright（Python）が必要。
import argparse
import os
import pathlib
import sys

from playwright.sync_api import sync_playwright

from shots import SHOTS

OUT_DIR = pathlib.Path(__file__).resolve().parent.parent / "app"
NUMBERS = "①②③④⑤⑥⑦⑧⑨"

# アニメーションを止める CSS
NO_ANIMATION = "*, *::before, *::after { transition: none !important; animation: none !important; }"

# 赤枠と番号を付ける（ページに注入するスクリプト）。矩形はビューポート内の座標で描く。
MARK_JS = """
(args) => {
  const [rect, label] = args;
  const box = document.createElement('div');
  box.className = '__mark';
  box.style.cssText = `position:fixed;left:${rect.x - 4}px;top:${rect.y - 4}px;`
    + `width:${rect.width + 8}px;height:${rect.height + 8}px;`
    + 'border:3px solid #d32f2f;border-radius:4px;pointer-events:none;z-index:2147483647;';
  if (label) {
    const n = document.createElement('div');
    n.textContent = label;
    n.style.cssText = 'position:absolute;left:-14px;top:-14px;width:24px;height:24px;'
      + 'border-radius:50%;background:#d32f2f;color:#fff;font:bold 14px sans-serif;'
      + 'display:flex;align-items:center;justify-content:center;';
    box.appendChild(n);
  }
  document.body.appendChild(box);
}
"""


def login(page, base_url, user):
    password = os.environ.get("CAPTURE_PASSWORD")
    if not password:
        sys.exit("環境変数 CAPTURE_PASSWORD（撮影用の仮のパスワード）を設定してください")
    page.goto(f"{base_url}/login")
    page.fill("input[name=username]", user)
    page.fill("input[name=password]", password)
    page.click("vaadin-login-form vaadin-button")
    page.wait_for_load_state("networkidle")


def run_steps(page, steps):
    for step in steps:
        kind = step[0]
        if kind == "fill":
            page.get_by_label(step[1]).fill(step[2])
        elif kind == "click":
            page.get_by_role("button", name=step[1]).click()
        elif kind == "wait":
            page.wait_for_timeout(step[1])
        else:
            sys.exit(f"未知の操作です: {kind}")


def shoot(browser, base_url, shot):
    context = browser.new_context(
        viewport={"width": shot.get("width", 1280), "height": 800},
        locale="ja-JP",
        color_scheme="light",
        device_scale_factor=2,           # 画像を見る人のために、高解像度で撮る
    )
    page = context.new_page()
    try:
        if shot["user"]:
            login(page, base_url, shot["user"])
        page.goto(base_url + shot["path"])
        page.wait_for_load_state("networkidle")
        page.add_style_tag(content=NO_ANIMATION)
        run_steps(page, shot["steps"])
        for selector, number in shot["marks"]:
            rect = page.locator(selector).first.bounding_box()
            if rect is None:
                sys.exit(f"{shot['name']}: 見つかりません: {selector}")
            label = NUMBERS[number - 1] if number else None
            page.evaluate(MARK_JS, [rect, label])
        target = page.locator(shot["clip"]) if shot.get("clip") else page
        target.screenshot(path=str(OUT_DIR / f"{shot['name']}.png"))
        print("撮影:", shot["name"])
    finally:
        context.close()


def main():
    parser = argparse.ArgumentParser(description="資料用の画面を自動撮影する")
    parser.add_argument("--base-url", default="http://localhost:8080")
    parser.add_argument("--only", help="この名前の 1 枚だけ撮影する")
    args = parser.parse_args()

    shots = [s for s in SHOTS if not args.only or s["name"] == args.only]
    if not shots:
        sys.exit("対象の撮影が見つかりません")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for shot in shots:
            shoot(browser, args.base_url.rstrip("/"), shot)
        browser.close()


if __name__ == "__main__":
    main()
