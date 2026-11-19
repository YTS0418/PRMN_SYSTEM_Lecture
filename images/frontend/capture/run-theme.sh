#!/bin/bash
# 別のテーマ（Lumo など）で、サンプルのアプリを起動する（テーマの比較の撮影用。フロントエンド編 13 章）。
# 使い方： bash run-theme.sh <テーマ> <ポート> [サンプルの grades-vaadin のパス]
#   テーマ：aura / lumo-compact（Lumo のコンパクト版）。サンプルの既定は Lumo
#   例    ：bash run-theme.sh aura 8081 ~/PRMN_SYSTEM_Sample/frontend/grades-vaadin
# 環境変数 DB_PASSWORD（と、必要なら SPRING_DATASOURCE_URL）を、先に設定しておく。
# サンプルを、一時フォルダにコピーして、起動クラスのテーマの指定だけを書き換える（元のサンプルは変更しない）。
set -eu
THEME=${1:?テーマ（lumo / lumo-compact）を指定してください}
PORT=${2:?ポートを指定してください}
SRC=${3:-../../../../PRMN_SYSTEM_Sample/frontend/grades-vaadin}
WORK=$(mktemp -d)
echo "作業フォルダ: $WORK"
(cd "$SRC" && tar --exclude=target --exclude=node_modules --exclude=generated -cf - .) | tar -xf - -C "$WORK"
APP=$(ls "$WORK"/src/main/java/grades/*アプリ.java)
case "$THEME" in
  aura)         sed -i "s/import com.vaadin.flow.theme.lumo.Lumo;/import com.vaadin.flow.theme.aura.Aura;/; s/Lumo.STYLESHEET/Aura.STYLESHEET/" "$APP" ;;
  lumo-compact) sed -i "s/Lumo.STYLESHEET/Lumo.COMPACT_STYLESHEET/" "$APP" ;;
  *) echo "未知のテーマです: $THEME" >&2; exit 1 ;;
esac
cd "$WORK"
./mvnw -q -Pproduction -DskipTests clean package
exec java -jar target/*.jar --server.port="$PORT"
