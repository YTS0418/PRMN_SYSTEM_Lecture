#!/bin/bash
# 図（.puml）から、SVG を作る。共通のスクリプト（tools/build-diagrams.sh）を呼ぶ。
# このフォルダ、またはリポジトリの直下で実行する： bash images/frontend/diagram/build.sh
set -eu
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
bash "$ROOT/tools/build-diagrams.sh" "$ROOT/images/frontend/diagram"
