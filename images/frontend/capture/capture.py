# フロントエンド資料の画面を自動撮影する（番号つきの赤枠は、必要なものだけ）。
# 使い方は README.md を参照。Playwright（Python）が必要。
#
# 枠のずれを防ぐための仕組み：
#   1. アニメーション・フォントの読み込みが終わるまで待ってから、測る（shadow DOM の中も対象）
#   2. 測り方を、箱（box）・テキストの範囲（text）・shadow の part（part:名前）から選ぶ
#   3. 枠は、測った箱の外側に描く（余白の追加はしない）。番号の丸は、箱の外の、ほかと重ならない位置に置く
#   4. 撮影のあとに、自動で検査する（測り直し・範囲内・重なり・画像の中の赤い線）。失敗した画像は出力しない
import argparse
import os
import pathlib
import sys
import tempfile

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from marks import DEFAULT_PAD, NUMBERS, normalize_clip, normalize_mark
from shots import SHOTS

HERE = pathlib.Path(__file__).resolve().parent
OUT_DIR = HERE.parent / "app"
CHECK_DIR = HERE / "_check"                   # 確認用の画像（Git で管理しない）

RED = (211, 47, 47)                           # 枠の色（#d32f2f）
BORDER = 3                                    # 枠の太さ（px）
GAP = 1                                       # 対象と枠の間（px）
BADGE = 22                                    # 番号の丸の直径（px）

# 準備ができるまで待つ（フォント、アニメーション。無限に続くものは除く）
READY_JS = """
async () => {
  await document.fonts.ready;
  const finite = document.getAnimations({subtree: true})
    .filter(a => { try { return a.effect.getComputedTiming().iterations !== Infinity; } catch (e) { return false; } });
  await Promise.race([
    Promise.all(finite.map(a => a.finished.catch(() => {}))),
    new Promise(r => setTimeout(r, 3000)),
  ]);
}
"""

# 対象の箱を測る。el は対象の要素、how は測り方
MEASURE_JS = """
(el, how) => {
  let r;
  if (how === 'box') {
    r = el.getBoundingClientRect();
  } else if (how === 'text') {
    const range = document.createRange();
    range.selectNodeContents(el);
    r = range.getBoundingClientRect();
  } else if (how.startsWith('part:')) {
    const p = el.shadowRoot && el.shadowRoot.querySelector(`[part~="${how.slice(5)}"]`);
    if (!p) return null;
    r = p.getBoundingClientRect();
  } else {
    return null;
  }
  return {x: r.x, y: r.y, width: r.width, height: r.height};
}
"""

# 枠と番号の丸を描く（最前面＝top layer に出す。ダイアログや通知の上にも出るように）
DRAW_JS = """
(items) => {
  document.querySelectorAll('.__mark').forEach(e => e.remove());
  for (const it of items) {
    const box = document.createElement('div');
    box.className = '__mark';
    box.style.cssText = 'position:fixed;box-sizing:border-box;border-radius:3px;pointer-events:none;'
      + 'margin:0;padding:0;background:transparent;overflow:visible;inset:auto;'
      + `width:${it.box.w}px;height:${it.box.h}px;border:${it.bw}px solid #d32f2f;`;
    box.style.left = it.box.x + 'px'; box.style.top = it.box.y + 'px';
    box.popover = 'manual';
    document.body.appendChild(box);
    box.showPopover();
    if (it.badge) {
      const n = document.createElement('div');
      n.className = '__mark';
      n.textContent = it.badge.text;
      n.style.cssText = 'position:fixed;box-sizing:border-box;border-radius:50%;background:#d32f2f;color:#fff;'
        + 'font:bold 14px/1 sans-serif;display:flex;align-items:center;justify-content:center;'
        + 'margin:0;padding:0;border:0;inset:auto;overflow:visible;pointer-events:none;'
        + `width:${it.badge.d}px;height:${it.badge.d}px;`;
      n.style.left = it.badge.x + 'px'; n.style.top = it.badge.y + 'px';
      n.popover = 'manual';
      document.body.appendChild(n);
      n.showPopover();
    }
  }
}
"""


# ---------- ブラウザの操作 ----------

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


def wait_ready(page, settle=150):
    page.wait_for_load_state("networkidle")
    page.evaluate(READY_JS)
    page.wait_for_timeout(settle)


def run_steps(page, steps):
    for step in steps:
        kind = step[0]
        if kind == "fill":                       # ("fill", ラベル, 値)
            page.get_by_label(step[1], exact=True).fill(step[2])
        elif kind == "choose":                   # ("choose", ラベル, 選択肢の文字)  Select / ComboBox
            page.get_by_label(step[1], exact=True).click()
            page.get_by_role("option", name=step[2]).first.click()
        elif kind == "click":                    # ("click", ボタンの文字)
            page.get_by_role("button", name=step[1], exact=True).first.click()
        elif kind == "click_css":                # ("click_css", セレクタ)
            page.locator(step[1]).first.click()
        elif kind == "hover":                    # ("hover", セレクタ)
            page.locator(step[1]).first.hover()
        elif kind == "press":                    # ("press", キー)
            page.keyboard.press(step[1])
        elif kind == "wait":                     # ("wait", ミリ秒)
            page.wait_for_timeout(step[1])
        else:
            raise RuntimeError(f"未知の操作です: {kind}")
        wait_ready(page, settle=100)


def measure(page, sel, how):
    """sel が、リストのときは、それぞれを測って、全体を囲む 1 つの箱にする。"""
    if isinstance(sel, (list, tuple)):
        rs = [measure(page, s, how) for s in sel]
        x0 = min(r["x"] for r in rs); y0 = min(r["y"] for r in rs)
        x1 = max(r["x"] + r["width"] for r in rs); y1 = max(r["y"] + r["height"] for r in rs)
        return {"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0}
    loc = page.locator(sel).first
    try:
        # 箱を持たない要素（slot で置かれた文字など）もあるので、text / part は「存在する」だけを待つ
        loc.wait_for(state="visible" if how == "box" else "attached", timeout=5000)
    except PlaywrightTimeoutError:
        raise RuntimeError(f"見つかりません: {sel}")
    r = loc.evaluate(MEASURE_JS, how)
    if r is None:
        raise RuntimeError(f"測れません（{how}）: {sel}")
    return r


# ---------- 枠と番号の配置 ----------

def inflate(r, d):
    return {"x": r["x"] - d, "y": r["y"] - d, "width": r["width"] + 2 * d, "height": r["height"] + 2 * d}


def intersects(a, b):
    return a["x"] < b["x"] + b["width"] and b["x"] < a["x"] + a["width"] \
        and a["y"] < b["y"] + b["height"] and b["y"] < a["y"] + a["height"]


def inside(a, area):
    return a["x"] >= area["x"] - 0.01 and a["y"] >= area["y"] - 0.01 \
        and a["x"] + a["width"] <= area["x"] + area["width"] + 0.01 \
        and a["y"] + a["height"] <= area["y"] + area["height"] + 0.01


def place_badges(frames, area):
    """番号の丸を、枠の外の、ほかの枠・丸と重ならない位置に置く。"""
    placed = []
    result = {}
    for i, f in enumerate(frames):
        if f["n"] is None:
            continue
        o = f["outer"]
        d = BADGE
        cands = [                             # 枠の外側に、丸が収まる位置（左上、右上、左下、右下、左、上）
            (o["x"] - d, o["y"] - d), (o["x"] + o["width"], o["y"] - d),
            (o["x"] - d, o["y"] + o["height"]), (o["x"] + o["width"], o["y"] + o["height"]),
            (o["x"] - d, o["y"] + o["height"] / 2 - d / 2), (o["x"] + o["width"] / 2 - d / 2, o["y"] - d),
        ]
        chosen = None
        for (x, y) in cands:
            b = {"x": x, "y": y, "width": d, "height": d}
            if not inside(b, area):
                continue
            if any(intersects(b, g["outer"]) for j, g in enumerate(frames) if j != i):
                continue
            if any(intersects(b, p) for p in placed):
                continue
            chosen = b
            break
        if chosen is None:
            raise RuntimeError(f"番号 {NUMBERS[f['n'] - 1]} を置ける場所がありません（切り抜きの余白を広げてください）")
        placed.append(chosen)
        result[i] = chosen
    return result


# ---------- 撮影 ----------

def shoot(browser, base_urls, shot, make_sheet):
    ctx = browser.new_context(
        viewport={"width": shot.get("width", 1280), "height": shot.get("height", 800)},
        locale="ja-JP", color_scheme=shot.get("color_scheme", "light"), device_scale_factor=2)
    page = ctx.new_page()
    base_url = base_urls[shot.get("base", "main")]
    name = shot["name"]
    try:
        if shot.get("user"):
            login(page, base_url, shot["user"])
        page.goto(base_url + shot["path"])
        wait_ready(page, settle=shot.get("settle", 600))
        run_steps(page, shot.get("steps", []))
        wait_ready(page, settle=shot.get("settle_after", 300))

        vw, vh = shot.get("width", 1280), shot.get("height", 800)
        viewport = {"x": 0, "y": 0, "width": vw, "height": vh}

        # 切り抜く範囲
        clip = normalize_clip(shot.get("clip"))
        if clip:
            cr = measure(page, clip["sel"], clip["how"])
            a = inflate(cr, clip["pad"])
            x0, y0 = max(a["x"], 0), max(a["y"], 0)
            x1, y1 = min(a["x"] + a["width"], vw), min(a["y"] + a["height"], vh)
            area = {"x": x0, "y": y0, "width": x1 - x0, "height": y1 - y0}
        else:
            area = viewport

        # 枠を付ける対象を測る
        marks = [normalize_mark(m) for m in shot.get("marks", [])]
        frames = []
        for m in marks:
            r = measure(page, m["sel"], m["how"])
            if r["width"] <= 0 or r["height"] <= 0:
                raise RuntimeError(f"大きさが 0 です: {m['sel']}（{m['how']}）")
            frames.append({"m": m, "rect": r, "outer": inflate(r, GAP + BORDER), "n": m["n"]})

        # 検査 1：重なり（入れ子を許したもの以外）
        for i in range(len(frames)):
            for j in range(i + 1, len(frames)):
                if intersects(frames[i]["outer"], frames[j]["outer"]) \
                        and not (frames[i]["m"]["nested_ok"] and frames[j]["m"]["nested_ok"]):
                    raise RuntimeError(f"枠が重なっています: {frames[i]['m']['sel']} と {frames[j]['m']['sel']}")
        # 検査 2：切り抜きの範囲内
        for f in frames:
            if not inside(f["outer"], area):
                raise RuntimeError(f"枠が切り抜きの外に出ます: {f['m']['sel']}（余白を広げてください）")

        badges = place_badges(frames, area)

        items = []
        for i, f in enumerate(frames):
            o = f["outer"]
            it = {"box": {"x": o["x"], "y": o["y"], "w": o["width"], "h": o["height"]}, "bw": BORDER}
            if i in badges:
                b = badges[i]
                it["badge"] = {"x": b["x"], "y": b["y"], "d": BADGE, "text": NUMBERS[f["n"] - 1]}
            items.append(it)
        page.evaluate(DRAW_JS, items)

        # 検査 3：描いたあとに測り直して、同じ位置か（動いていないか）
        for f in frames:
            r2 = measure(page, f["m"]["sel"], f["m"]["how"])
            for k in ("x", "y", "width", "height"):
                if abs(r2[k] - f["rect"][k]) > 1.0:
                    raise RuntimeError(f"撮影の前後で、位置が動きました: {f['m']['sel']}（{k}: {f['rect'][k]:.1f} → {r2[k]:.1f}）")

        # 撮影（検査 4 に通ったときだけ、保存先へ移す）
        out = OUT_DIR / f"{name}.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmp:
            tmp_png = pathlib.Path(tmp) / "shot.png"
            page.screenshot(path=str(tmp_png), clip=area)
            problems = verify_pixels(tmp_png, frames, area)
            if problems:
                raise RuntimeError("画像の中に、枠が見つかりません: " + ", ".join(problems))
            out.write_bytes(tmp_png.read_bytes())
        if make_sheet and frames:
            save_sheet(out, frames, area, name)
        print("撮影:", name)
    finally:
        ctx.close()


def verify_pixels(png, frames, area):
    """画像の中で、枠の線の中心に、赤い色があるか（各辺の中央の 1 点ずつ）を調べる。"""
    from PIL import Image
    im = Image.open(png).convert("RGB")
    s = im.width / area["width"]              # 画像の倍率（device_scale_factor）
    bad = []
    for f in frames:
        o = f["outer"]
        c = BORDER / 2
        pts = [(o["x"] + o["width"] / 2, o["y"] + c), (o["x"] + o["width"] / 2, o["y"] + o["height"] - c),
               (o["x"] + c, o["y"] + o["height"] / 2), (o["x"] + o["width"] - c, o["y"] + o["height"] / 2)]
        hits = 0
        for (x, y) in pts:
            px = int(round((x - area["x"]) * s))
            py = int(round((y - area["y"]) * s))
            if 0 <= px < im.width and 0 <= py < im.height:
                p = im.getpixel((px, py))
                if all(abs(p[k] - RED[k]) <= 40 for k in range(3)):
                    hits += 1
        if hits < 4:
            bad.append(f["m"]["sel"])
    return bad


def save_sheet(png, frames, area, name):
    """目で確認するための画像：各枠の周囲を、保存する（_check/）。"""
    from PIL import Image
    CHECK_DIR.mkdir(exist_ok=True)
    im = Image.open(png).convert("RGB")
    s = im.width / area["width"]
    for i, f in enumerate(frames):
        o = f["outer"]
        m = 24
        box = (int((o["x"] - m - area["x"]) * s), int((o["y"] - m - area["y"]) * s),
               int((o["x"] + o["width"] + m - area["x"]) * s), int((o["y"] + o["height"] + m - area["y"]) * s))
        box = (max(box[0], 0), max(box[1], 0), min(box[2], im.width), min(box[3], im.height))
        im.crop(box).save(CHECK_DIR / f"{name.replace('/', '__')}__{i + 1}.png")


def main():
    parser = argparse.ArgumentParser(description="資料用の画面を自動撮影する")
    parser.add_argument("--base-url", default="http://localhost:8080", help="サンプルのアプリの URL")
    parser.add_argument("--alt-url", action="append", default=[], metavar="名前=URL",
                        help="別の設定で起動したアプリ（例：lumo=http://localhost:8081）")
    parser.add_argument("--only", help="この名前（前方一致）の撮影だけを行う")
    parser.add_argument("--sheet", action="store_true", help="枠の周囲の確認用の画像も、_check/ に保存する")
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
    failed = []
    with sync_playwright() as p:
        # Playwright の Chromium がなければ、インストール済みの Chrome を使う（CAPTURE_BROWSER_CHANNEL=chrome）
        channel = os.environ.get("CAPTURE_BROWSER_CHANNEL")
        browser = p.chromium.launch(channel=channel) if channel else p.chromium.launch()
        for shot in shots:
            try:
                shoot(browser, base_urls, shot, args.sheet)
            except Exception as e:                       # 1 枚の失敗で、ほかの撮影を止めない
                failed.append(shot["name"])
                print(f"失敗: {shot['name']}: {str(e).splitlines()[0]}")
        browser.close()
    if failed:
        sys.exit(f"{len(failed)} 枚の撮影に失敗しました")


if __name__ == "__main__":
    main()
