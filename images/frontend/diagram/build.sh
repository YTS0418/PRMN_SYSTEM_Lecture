#!/bin/bash
# 図（.puml）から、SVG を作る。このフォルダで実行する： bash build.sh
# 日本語のフォントは、閲覧する環境のものが使われる。そこで、フォントの候補（代替の一覧）を、SVG に書き込む。
set -eu
cd "$(dirname "$0")"
FALLBACK="'Noto Sans CJK JP', 'Hiragino Sans', 'Hiragino Kaku Gothic ProN', 'Yu Gothic', 'Meiryo', sans-serif"
plantuml -tsvg dia-*.puml
for f in dia-*.svg; do
  sed -i "s/font-family=\"Noto Sans CJK JP\"/font-family=\"$FALLBACK\"/g" "$f"
done
ls dia-*.svg | wc -l
