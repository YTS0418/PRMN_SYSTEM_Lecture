# 資料のコードと、サンプルの見本のコードが、同じかを調べる。
#   python3 check_snippets.py [--sample サンプルの java のフォルダ]
#
# サンプルの側：   // snippet: 名前   〜   // end snippet   の間のコード
# 資料の側    ：   <!-- snippet: 名前 -->   の次の ```java ブロック
# 比べるとき、コメント・空白・インデントの違いは、無視する。違いがあれば、差分を表示して、終了コード 1。
import argparse
import difflib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
CHAPTERS = ROOT / "フロントエンド"
DEFAULT_SAMPLE = ROOT.parent / "PRMN_SYSTEM_Sample/frontend/grades-vaadin/src/main/java"

SAMPLE_REGION = re.compile(r"//\s*snippet:\s*(?P<id>[\w\-]+)\s*\n(?P<body>.*?)//\s*end snippet", re.S)
DOC_BLOCK = re.compile(r"<!-- snippet: (?P<id>[\w\-]+) -->\s*\n```java\n(?P<body>.*?)```", re.S)


def normalize(code):
    """コメントと、空白の違いを、取り除く。"""
    lines = []
    for line in code.splitlines():
        line = re.sub(r"//.*$", "", line)          # 行末までのコメント（文字列の中の // は、このサンプルでは使わない）
        line = line.strip()
        if line:
            lines.append(line)
    return re.sub(r"\s+", " ", " ".join(lines))


def pretty(code):
    return [re.sub(r"//.*$", "", l).strip() for l in code.splitlines() if re.sub(r"//.*$", "", l).strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", default=str(DEFAULT_SAMPLE), help="サンプルの Java のフォルダ")
    args = ap.parse_args()

    sample = {}
    for f in pathlib.Path(args.sample).rglob("*.java"):
        for m in SAMPLE_REGION.finditer(f.read_text()):
            sample[m.group("id")] = (f.name, m.group("body"))
    if not sample:
        sys.exit(f"サンプルに snippet が見つかりません: {args.sample}")

    bad = 0
    used = set()
    for md in sorted(CHAPTERS.glob("*.md")):
        for m in DOC_BLOCK.finditer(md.read_text()):
            sid = m.group("id")
            used.add(sid)
            if sid not in sample:
                print(f"{md.name}: サンプルに、snippet がありません: {sid}")
                bad += 1
                continue
            fname, body = sample[sid]
            if normalize(body) != normalize(m.group("body")):
                bad += 1
                print(f"{md.name}: コードが、サンプル（{fname}）と違います: {sid}")
                for d in difflib.unified_diff(pretty(body), pretty(m.group("body")), "サンプル", "資料", lineterm="", n=0):
                    print("   " + d)
    unused = sorted(set(sample) - used)
    if unused:
        print("資料で使っていない snippet（情報）:", ", ".join(unused))
    print(f"確認した snippet: {len(used)} 個、違い: {bad} 個")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
