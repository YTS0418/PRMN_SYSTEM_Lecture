# 撮影の設定の一覧（capture.py が読む）。
# 資料の📷スクショ指定ブロックと、images/frontend/撮影リスト.md に対応させる。
#
# 各要素のキー：
#   name     : 保存するファイル名（拡張子なし）。../app/ に保存される
#   path     : 撮影する画面の URL のパス（base-url からの相対）
#   user     : ログインするユーザー名（None のときはログインしない）
#   width    : ビューポートの幅（省略時は 1280）
#   steps    : 撮影の前に行う操作（下の「操作」を参照）
#   marks    : 赤枠と番号を付ける場所。(Playwright のセレクタ, 番号) の並び。番号が None なら枠だけ
#   clip     : 画像を切り取る場所のセレクタ（None のときは、画面全体）
#
# 操作（steps）：
#   ("fill", ラベル, 値)      ラベルの入力欄に値を入れる
#   ("click", ボタンの文字)   ボタンを押す
#   ("wait", ミリ秒)          待つ
#
# セレクタの例：
#   "vaadin-text-field:has(label:text-is('氏名'))"   ラベルが「氏名」のテキストフィールド
#   "vaadin-button:text-is('登録')"                   文字が「登録」のボタン
# ※ここに書いたセレクタは仮置き。サンプルが出来たら、実際の画面で確かめて直す。

SHOTS = [
    {
        "name": "app-02-01-first-view",
        "path": "/",
        "user": "teacher01",
        "steps": [],
        "marks": [],
    },
    {
        "name": "app-03-01-app-layout",
        "path": "/students",
        "user": "teacher01",
        "steps": [],
        "marks": [("vaadin-side-nav", 1), ("vaadin-app-layout::part(navbar)", 2), ("main", 3)],
    },
    {
        "name": "app-08-01-validation-error",
        "path": "/students/register",
        "user": "teacher01",
        "steps": [
            ("fill", "入学年度", "1999"),
            ("click", "登録"),
            ("wait", 500),
        ],
        "marks": [("vaadin-text-field:has(label:text-is('氏名'))", 1),
                  ("vaadin-integer-field:has(label:text-is('入学年度'))", 2)],
    },
    {
        "name": "app-10-01-login",
        "path": "/login",
        "user": None,
        "steps": [],
        "marks": [("vaadin-login-form input[name=username]", 1),
                  ("vaadin-login-form input[name=password]", 2),
                  ("vaadin-login-form vaadin-button", 3)],
    },
    # …残りの撮影は、撮影リストに従って、同じ形で追加する（全 18 枚）。
]
