# 画像に振った番号と、章の「番号の説明の表」を、そろえる。
#   python3 gen_legend.py --write   shots.py の label から、章の表を作る（書き換える）
#   python3 gen_legend.py --check   画像の番号と、章の表が、一致しているかを調べる（食い違いがあれば、終了コード 1）
#
# 章の中の、次の印の間が、表の場所：
#   <!-- legend:parts/confirm-dialog-basic -->
#   （ここが、自動で作られる）
#   <!-- /legend -->
# 規則：番号を振った画像には、必ず、表を付ける。番号のない画像には、表を付けない。alt テキストに、番号を入れない。
import argparse
import pathlib
import re
import sys

from marks import NUMBERS, normalize_mark
from shots import SHOTS

ROOT = pathlib.Path(__file__).resolve().parents[3]
CHAPTERS = ROOT / "フロントエンド"
LEGEND = re.compile(r"<!-- legend:(?P<name>[\w/.\-]+) -->\n(?P<body>.*?)<!-- /legend -->", re.S)
IMAGE = re.compile(r"(?:!\[(?P<alt>[^\]]*)\]\(|<img src=\")\.\./images/frontend/(?:app/)?(?P<name>[\w/\-]+)\.png(?:\)|\" alt=\"(?P<alt2>[^\"]*)\" width=\"\d+\">)")


def numbered_marks():
    """画像の名前 → [(番号, 説明)]。番号を振ったものだけ。"""
    result = {}
    for shot in SHOTS:
        marks = [normalize_mark(m) for m in shot.get("marks", [])]
        items = sorted((m["n"], m["label"]) for m in marks if m["n"] is not None)
        if items:
            result[shot["name"]] = items
    return result


def table(items):
    lines = ["| 番号 | 説明 |", "|---|---|"]
    lines += [f"| {NUMBERS[n - 1]} | {label} |" for n, label in items]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true")
    args = ap.parse_args()

    marks = numbered_marks()
    problems = []
    for md in sorted(CHAPTERS.glob("*.md")):
        text = md.read_text()
        legends = {m.group("name"): m for m in LEGEND.finditer(text)}
        images = list(IMAGE.finditer(text))
        # 番号を振った画像には、表が必要。番号のない画像に、表は不要
        for im in images:
            name = im.group("name")
            if re.search(f"[{NUMBERS}]", im.group("alt") or im.group("alt2") or ""):
                problems.append(f"{md.name}: alt テキストに番号が入っています: {name}")
            if name in marks and name not in legends:
                problems.append(f"{md.name}: 番号を振った画像に、説明の表がありません: {name}")
        for name, m in legends.items():
            if name not in marks:
                problems.append(f"{md.name}: 番号のない画像に、説明の表があります: {name}")
            elif m.group("body") != table(marks[name]) and not args.write:
                problems.append(f"{md.name}: 説明の表が、shots.py と食い違っています: {name}")
        if args.write:
            def rep(m):
                name = m.group("name")
                if name not in marks:
                    return m.group(0)
                return f"<!-- legend:{name} -->\n{table(marks[name])}<!-- /legend -->"
            new = LEGEND.sub(rep, text)
            if new != text:
                md.write_text(new)
                print("更新:", md.name)
    if problems:
        print("\n".join(problems))
        sys.exit(1)
    print("OK" if args.check else "完了")


if __name__ == "__main__":
    main()
