# shots.py から、撮影リスト（../撮影リスト.md）を作る（手で書かない）。
#   python3 gen_shotlist.py
import pathlib
from marks import NUMBERS, normalize_mark
from shots import SHOTS

out = pathlib.Path(__file__).resolve().parent.parent / "撮影リスト.md"
groups = {}
for s in SHOTS:
    groups.setdefault(s["name"].split("/")[0], []).append(s)

lines = ["""# スクリーンショット撮影リスト（フロントエンド編）

フロントエンド（Vaadin）資料（[フロントエンド/](/フロントエンド/)）に埋め込む画像の一覧です。**このファイルは、`capture/gen_shotlist.py` が、`capture/shots.py` から作ります**（手で書き換えません）。

## 撮影の方法

| 方法 | 対象 | やり方 |
|---|---|---|
| **自動** | サンプルアプリの画面（`parts/`、`screens/`） | サンプルを**本番モード**で起動し、[`capture/`](/images/frontend/capture/README.md) のスクリプトを実行する |
| **手動** | 外部サイト・IDE の画面（`setup/`、`ide/`） | 他の撮影リストと同じ。赤枠（2px 程度）・番号は、自分で付ける |

## 撮影の条件

- 形式：PNG。**device_scale_factor=2**（画像のピクセル数 = 実寸の 2 倍）。章には、**実寸の幅**（`width`）で貼る（`capture/fix_img_widths.py`）
- 部品の画像（`parts/`）：見本の画面の 1 つの部品を**切り抜く**。画面の画像（`screens/`）：幅 900〜1100px（GitHub の本文の幅に、ほぼ収まる）
- テーマ：Lumo（`@StyleSheet(Lumo.STYLESHEET)`）。比較の画像だけ、Aura
- 赤枠は、**章の本文が説明する部品だけ**に付ける。番号は、章の「番号｜説明」の表（`capture/gen_legend.py`）と対応する
- 個人情報：撮影用の仮のデータだけ（`teacher01`、`student01`、架空の学生）

## 一覧（自動撮影）
"""]
total = 0
titles = {"parts": "部品の切り抜き（`images/frontend/app/parts/`）", "screens": "画面（`images/frontend/app/screens/`）"}
for g, items in groups.items():
    lines.append(f"\n### {titles.get(g, g)}（{len(items)} 枚）\n")
    lines.append("| 保存パス | 画面（URL） | 操作 | 番号の説明 |")
    lines.append("|---|---|---|---|")
    for s in items:
        marks = [normalize_mark(m) for m in s.get("marks", [])]
        numbered = "、".join(f"{NUMBERS[m['n'] - 1]}{m['label'].split('（')[0]}" for m in sorted(
            (m for m in marks if m["n"]), key=lambda m: m["n"])) or "（番号なし）"
        steps = "、".join(f"{st[0]}:{st[-1] if st[0] != 'fill' else st[1]}" for st in s.get("steps", [])) or "—"
        base = "（別アプリ）" if s.get("base") else ""
        lines.append(f"| `/images/frontend/app/{s['name']}.png` | `{s['path']}`{base} | {steps} | {numbered} |")
        total += 1
lines.append(f"\n合計：**{total} 枚**（自動）\n")
lines.append("""## 一覧（手動撮影）

| 保存パス | 画面 | 強調 |
|---|---|---|
| `/images/frontend/setup/vdn-02-01-vaadin-start.png` | [Vaadin Start](https://start.vaadin.com/) で、Flow・Maven・Java 25 を選び、ダウンロード直前の状態 | プロジェクトの種類、Java のバージョン、ダウンロードのボタンを、赤枠で囲み、番号①〜③ |
""")
out.write_text("\n".join(lines))
print("書きました:", out, f"({total} 枚)")
