#!/bin/bash
# PlantUML の図（.puml）から、SVG を作る。
#
# 使い方（リポジトリの直下で実行する）：
#   bash tools/build-diagrams.sh images/database/diagram          # そのフォルダの .puml をすべて変換
#   bash tools/build-diagrams.sh images/database/diagram er-03-01-uml.puml   # 1 つだけ変換
#
# 必要なもの：plantuml コマンド、または plantuml.jar（環境変数 PLANTUML_JAR で場所を指定。
# VSCode の PlantUML 拡張に入っている jar は、自動で探す）。Java と Graphviz（dot）も必要。
#
# 日本語のフォントは、閲覧する環境のものが使われる。そこで、フォントの候補（代替の一覧）を SVG に書き込む。
# `_` で始まる .puml / .iuml（共通の設定ファイル）は、変換しない。
set -eu

if [ $# -lt 1 ]; then
  echo "使い方: bash tools/build-diagrams.sh <フォルダ> [ファイル.puml ...]" >&2
  exit 1
fi

DIR="$1"; shift
cd "$DIR"

if command -v plantuml >/dev/null 2>&1; then
  PUML=(plantuml)
else
  JAR="${PLANTUML_JAR:-}"
  if [ -z "$JAR" ]; then
    JAR=$(ls -d "$HOME"/.vscode/extensions/jebbs.plantuml-*/plantuml.jar 2>/dev/null | tail -n 1 || true)
  fi
  if [ -z "$JAR" ] || [ ! -f "$JAR" ]; then
    echo "plantuml が見つかりません。plantuml をインストールするか、PLANTUML_JAR に plantuml.jar のパスを指定してください。" >&2
    exit 1
  fi
  PUML=(java -Djava.awt.headless=true -jar "$JAR")
fi

if [ $# -gt 0 ]; then FILES=("$@"); else FILES=(*.puml); fi

FALLBACK="'Noto Sans CJK JP', 'Hiragino Sans', 'Hiragino Kaku Gothic ProN', 'Yu Gothic', 'Meiryo', sans-serif"
"${PUML[@]}" -charset UTF-8 -tsvg "${FILES[@]}"

for f in "${FILES[@]}"; do
  svg="${f%.puml}.svg"
  # sed -i は macOS と GNU で書き方が違うので、一時ファイルを経由する
  sed "s/font-family=\"Noto Sans CJK JP\"/font-family=\"$FALLBACK\"/g" "$svg" > "$svg.tmp" && mv "$svg.tmp" "$svg"
done
echo "${#FILES[@]} 個の SVG を作りました（${DIR}）"
