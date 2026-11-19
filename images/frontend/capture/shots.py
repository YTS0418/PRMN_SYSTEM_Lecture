# 撮影の設定の一覧（capture.py が読む）。
# 資料の📷スクショ指定ブロックと、images/frontend/撮影リスト.md に対応させる。
#
# 各要素のキー：
#   name   : 保存するファイル名（拡張子なし）。../app/ に保存される
#   path   : 撮影する画面の URL のパス（base-url からの相対）
#   user   : ログインするユーザー名（None のときはログインしない）
#   width  : ビューポートの幅（省略時は 1280）。height も同様（既定 800）
#   base   : アプリの URL の名前（省略時は main。--alt-url で渡したもの）
#   steps  : 撮影の前に行う操作（下の「操作」を参照）
#   marks  : 赤枠と番号を付ける場所。(Playwright のセレクタ, 番号) の並び。番号が None なら枠だけ
#   clip   : 画像を切り取る場所のセレクタ（省略時は、画面全体）
#
# 操作（steps）：
#   ("fill", ラベル, 値)             ラベルの入力欄に値を入れる
#   ("choose", ラベル, 選択肢)        Select / ComboBox で、選択肢を選ぶ
#   ("click", ボタンの文字)           ボタンを押す
#   ("wait", ミリ秒)                 待つ

# 画面の部品を指すセレクタ（Playwright は、Web Components の中身も探せる）
def 欄(ラベル):
    return f"vaadin-text-field:has(label:text-is('{ラベル}')), vaadin-integer-field:has(label:text-is('{ラベル}')), vaadin-select:has(label:text-is('{ラベル}')), vaadin-combo-box:has(label:text-is('{ラベル}')), vaadin-date-picker:has(label:text-is('{ラベル}'))"

def ボタン(文字):
    return f"vaadin-button:text-is('{文字}')"

SHOTS = [
    # ---- 部品単体の切り抜き（通知・確認ダイアログ：05 章）。番号は、本文が各部を説明するものだけ ----
    {"name": "parts/notification-default", "path": "/demo/feedback", "user": "teacher01",
     "steps": [("click", "通知（種類なし）")], "clip": "vaadin-notification-card"},
    {"name": "parts/notification-info", "path": "/demo/feedback", "user": "teacher01",
     "steps": [("click", "通知（情報）")], "clip": "vaadin-notification-card"},
    {"name": "parts/notification-success", "path": "/demo/feedback", "user": "teacher01",
     "steps": [("click", "通知（成功）")], "clip": "vaadin-notification-card"},
    {"name": "parts/notification-warning", "path": "/demo/feedback", "user": "teacher01",
     "steps": [("click", "通知（警告）")], "clip": "vaadin-notification-card"},
    {"name": "parts/notification-error", "path": "/demo/feedback", "user": "teacher01",
     "steps": [("click", "通知（エラー）")], "clip": "vaadin-notification-card"},
    {"name": "parts/lumo-notification-default", "path": "/demo/feedback", "user": "teacher01", "base": "lumo",
     "steps": [("click", "通知（種類なし）")], "clip": "vaadin-notification-card"},
    {"name": "parts/lumo-notification-info", "path": "/demo/feedback", "user": "teacher01", "base": "lumo",
     "steps": [("click", "通知（情報）")], "clip": "vaadin-notification-card"},
    {"name": "parts/lumo-notification-success", "path": "/demo/feedback", "user": "teacher01", "base": "lumo",
     "steps": [("click", "通知（成功）")], "clip": "vaadin-notification-card"},
    {"name": "parts/lumo-notification-warning", "path": "/demo/feedback", "user": "teacher01", "base": "lumo",
     "steps": [("click", "通知（警告）")], "clip": "vaadin-notification-card"},
    {"name": "parts/lumo-notification-error", "path": "/demo/feedback", "user": "teacher01", "base": "lumo",
     "steps": [("click", "通知（エラー）")], "clip": "vaadin-notification-card"},
    {"name": "parts/confirm-dialog-basic", "path": "/demo/feedback", "user": "teacher01",
     "steps": [("click", "確認ダイアログ（基本）")],
     "clip": {"sel": "vaadin-confirm-dialog-overlay [part=overlay]", "pad": 36},
     "marks": [
         {"sel": "vaadin-confirm-dialog h3[slot=header]", "how": "text", "n": 1, "label": "題名（`setHeader`）"},
         {"sel": "vaadin-confirm-dialog > div", "how": "text", "n": 2, "label": "本文（`setText`）"},
         {"sel": "vaadin-confirm-dialog vaadin-button[slot=cancel-button]", "n": 3, "label": "キャンセルのボタン（`setCancelable`、`setCancelText`）"},
         {"sel": "vaadin-confirm-dialog vaadin-button[slot=confirm-button]", "n": 4, "label": "確認のボタン（`setConfirmText`）"},
     ]},
    {"name": "parts/dialog-basic", "path": "/demo/feedback", "user": "teacher01",
     "steps": [("click", "ダイアログ（基本）")],
     "clip": {"sel": "vaadin-dialog-overlay [part=overlay]", "pad": 36},
     "marks": [
         {"sel": "vaadin-dialog h2[slot=title]", "how": "text", "n": 1, "label": "題名（`setHeaderTitle`）"},
         {"sel": "vaadin-dialog vaadin-integer-field", "n": 2, "label": "本文（`add` で追加した部品）"},
         {"sel": ["vaadin-dialog [slot=footer] vaadin-button:nth-child(1)", "vaadin-dialog [slot=footer] vaadin-button:nth-child(2)"], "n": 3, "label": "フッターのボタン（`getFooter().add` で追加）"},
     ]},
    {"name": "parts/confirm-dialog-danger", "path": "/demo/feedback", "user": "teacher01",
     "steps": [("click", "確認ダイアログ（削除）")],
     "clip": {"sel": "vaadin-confirm-dialog-overlay [part=overlay]", "pad": 12}},

    # ---- 以下は、これまでの撮影（順に、切り抜き＋必要な番号だけに作り直す） ----
    {"name": "app-02-01-first-view", "path": "/", "user": "teacher01",
     "steps": [], "marks": []},

    {"name": "app-03-01-app-layout", "path": "/students", "user": "teacher01", "steps": [],
     "marks": [("vaadin-side-nav", 1), ("vaadin-app-layout [slot=navbar]", 2), ("vaadin-grid", 3)]},

    {"name": "app-04-01-layouts", "path": "/demo/components", "user": "teacher01", "steps": [],
     "marks": [("vaadin-app-layout > vaadin-vertical-layout", 1), ("#buttons", 2)]},

    {"name": "app-04-02-form-layout-01", "path": "/demo/components", "user": "teacher01", "steps": [],
     "marks": [(欄("氏名"), 1), (欄("所属学科"), 2), (欄("入学年度"), 2)]},
    {"name": "app-04-02-form-layout-02", "path": "/demo/components", "user": "teacher01", "width": 480,
     "steps": [], "marks": [("#form-layout", None)]},

    {"name": "app-05-01-input-components", "path": "/demo/components", "user": "teacher01", "steps": [],
     "marks": [("#form-layout vaadin-text-field [slot=label]", 1), ("#form-layout vaadin-text-field input", 2),
               ("#form-layout vaadin-text-field [slot=helper]", 3), ("#form-layout vaadin-text-field [part=required-indicator]", 4)]},

    {"name": "app-05-02-buttons", "path": "/demo/components", "user": "teacher01", "steps": [],
     "marks": [(ボタン("登録する"), 1), (ボタン("キャンセル"), 2), (ボタン("削除する"), 3)]},

    {"name": "app-05-03-dialogs-01", "path": "/demo/components", "user": "teacher01",
     "steps": [("click", "確認ダイアログを開く"), ("wait", 600)],
     "marks": [("vaadin-confirm-dialog-overlay [part=header]", 1),
               ("vaadin-confirm-dialog vaadin-button[slot=confirm-button]", 2),
               ("vaadin-confirm-dialog vaadin-button[slot=cancel-button]", 3)]},
    {"name": "app-05-03-dialogs-02", "path": "/demo/components", "user": "teacher01",
     "steps": [("click", "通知を出す"), ("wait", 600)],
     "marks": [("vaadin-notification-card", 1)]},

    {"name": "app-07-01-grid", "path": "/students", "user": "teacher01", "steps": [],
     "marks": [("vaadin-grid thead tr, vaadin-grid-cell-content:text-is('氏名')", 1),
               ("vaadin-grid-cell-content:text-is('Taro')", 2), ("vaadin-grid-sorter", 3)]},

    {"name": "app-07-02-transcript-view", "path": "/students/2/transcript", "user": "teacher01", "steps": [],
     "marks": [("h2:has-text('さんの成績')", 1), ("vaadin-grid-cell-content:text-is('履修中')", 2),
               ("span:has-text('平均点')", 3)]},

    {"name": "app-08-01-validation-error", "path": "/students/register", "user": "teacher01",
     "steps": [("fill", "入学年度", "1999"), ("click", "登録する"), ("wait", 600)],
     "marks": [("vaadin-text-field [slot=error-message]", 1), ("vaadin-integer-field [slot=error-message]", 2)]},

    {"name": "app-08-02-register-form", "path": "/students/register", "user": "teacher01", "steps": [],
     "marks": [(欄("氏名"), 1), (ボタン("登録する"), 2)]},

    {"name": "app-09-01-enrollment-form", "path": "/enrollments/register", "user": "teacher01",
     "steps": [("choose", "学生", "1 Taro"), ("choose", "科目", "プログラミング基礎"),
               ("fill", "点数", "150"), ("click", "登録する"), ("wait", 800)],
     "marks": [(欄("点数"), 1), ("vaadin-notification-card", 2)]},

    {"name": "app-10-01-login", "path": "/login", "user": None, "steps": [],
     "marks": [("vaadin-login-form vaadin-text-field", 1), ("vaadin-login-form vaadin-password-field", 2), ("vaadin-login-form vaadin-button", 3)]},

    {"name": "app-10-02-login-error", "path": "/login?error", "user": None, "steps": [],
     "marks": [("vaadin-login-form [part=error-message]", None)]},

    {"name": "app-10-03-header-logout", "path": "/students", "user": "teacher01", "steps": [],
     "marks": [("vaadin-app-layout [slot=navbar] span", 1), (ボタン("ログアウト"), 2)],
     "clip": "vaadin-app-layout [slot=navbar]"},

    {"name": "app-11-01-menu-teacher", "path": "/students", "user": "teacher01", "steps": [],
     "marks": [("vaadin-side-nav", None)]},

    {"name": "app-11-02-menu-student", "path": "/", "user": "student01", "steps": [],
     "marks": [("vaadin-side-nav", None)]},

    # テーマの比較は、別のテーマで起動したアプリが必要（README の「テーマの比較」）
    {"name": "app-13-01-theme-compare-01", "path": "/students/register", "user": "teacher01", "base": "lumo",
     "steps": [], "marks": [(ボタン("登録する"), 1), (欄("氏名"), 2)]},
    {"name": "app-13-01-theme-compare-02", "path": "/students/register", "user": "teacher01",
     "steps": [], "marks": [(ボタン("登録する"), 1), (欄("氏名"), 2)]},
]
