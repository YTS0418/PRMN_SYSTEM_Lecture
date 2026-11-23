# 章の画像を、「実寸」の幅で表示する形（<img … width="…">）にそろえる。
#   python3 fix_img_widths.py --write   Markdown の画像 ![説明](…png) を、<img> に書き換え、width を、画像の実寸（ピクセル数の半分）にする
#   python3 fix_img_widths.py --check   width が、画像の実寸と合っているかを調べる（違いがあれば、終了コード 1）
# 理由：画像は、device_scale_factor=2 で撮っているので、そのまま貼ると、2 倍の大きさで表示される。
#       実寸で表示すると、どの画像でも、ボタンや文字の大きさが、同じに見える。GitHub の幅より広いときは、自動で縮む。
import argparse
import pathlib
import re
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
CHAPTERS = ROOT / "フロントエンド"
MD_IMG = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<path>\.\./images/frontend/app/[\w/\-]+\.png)\)")
HTML_IMG = re.compile(r'<img src="(?P<path>\.\./images/frontend/app/[\w/\-]+\.png)" alt="(?P<alt>[^"]*)" width="(?P<w>\d+)">')


def css_width(png: pathlib.Path) -> int:
    with open(png, "rb") as f:
        head = f.read(24)
    return struct.unpack(">I", head[16:20])[0] // 2


def tag(path, alt, md):
    w = css_width((md.parent / path).resolve())
    return f'<img src="{path}" alt="{alt}" width="{w}">'


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true")
    args = ap.parse_args()
    bad = []
    for md in sorted(CHAPTERS.glob("*.md")):
        text = md.read_text()
        if args.write:
            new = MD_IMG.sub(lambda m: tag(m.group("path"), m.group("alt"), md), text)
            new = HTML_IMG.sub(lambda m: tag(m.group("path"), m.group("alt"), md), new)
            if new != text:
                md.write_text(new)
                print("更新:", md.name)
        else:
            for m in MD_IMG.finditer(text):
                bad.append(f"{md.name}: Markdown の画像のまま（<img> に直す）: {m.group('path')}")
            for m in HTML_IMG.finditer(text):
                want = css_width((md.parent / m.group("path")).resolve())
                if int(m.group("w")) != want:
                    bad.append(f"{md.name}: width が実寸と違います（{m.group('w')} → {want}）: {m.group('path')}")
    if bad:
        print("\n".join(bad))
        sys.exit(1)
    print("OK" if args.check else "完了")


if __name__ == "__main__":
    main()
