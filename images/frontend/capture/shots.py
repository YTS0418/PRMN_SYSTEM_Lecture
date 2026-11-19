# 撮影の設定の一覧（capture.py が読む）。
# 資料のコードブロック・番号の説明の表・撮影リスト（images/frontend/撮影リスト.md）と、対応させる。
#
# 各要素のキー：
#   name   : 保存するファイル名（拡張子なし）。../app/ に保存される（parts/ = 部品の切り抜き、screens/ = 画面）
#   path   : 撮影する画面の URL のパス（base-url からの相対）
#   user   : ログインするユーザー名（None のときはログインしない）
#   width  : ビューポートの幅（既定 1280）。height も同様（既定 800）。画面全体の画像は、幅 900 にする
#   base   : アプリの URL の名前（省略時は main。--alt-url で渡したもの）
#   steps  : 撮影の前に行う操作（下の「操作」を参照）
#   clip   : 切り抜く範囲。セレクタ、(セレクタ, 余白 px)、または {"sel":…, "pad":…}。省略すると、画面全体
#   marks  : 赤枠を付ける場所。既定は、番号なし。**章の本文が説明するものだけ**に、n（番号）と label（説明）を付ける
#            {"sel": セレクタ（リストなら、全体を囲む）, "how": "box" | "text" | "part:名前", "n": 番号, "label": "説明"}
#
# 操作（steps）：
#   ("fill", ラベル, 値) / ("choose", ラベル, 選択肢) / ("click", ボタンの文字（完全一致）) / ("click_css", セレクタ)
#   ("hover", セレクタ) / ("press", キー) / ("wait", ミリ秒)


def 部品(name, path, id_, pad=12, marks=None, steps=None, **kw):
    """見本の画面にある、id つきの入れ物を、切り抜いて撮る。"""
    d = {"name": f"parts/{name}", "path": path, "user": "teacher01", "steps": steps or [],
         "width": 1100, "height": 1500,                       # 縦に長い画面でも、切り抜きが、見える範囲に収まるように
         "clip": {"sel": f"#{id_}", "pad": pad}, "marks": marks or []}
    d.update(kw)
    return d


def 通知(name, ボタン):
    return {"name": f"parts/notification-{name}", "path": "/demo/feedback", "user": "teacher01",
            "steps": [("click", ボタン)], "hide": ["vaadin-app-layout"],
            "clip": {"sel": "vaadin-notification-card", "how": "part:overlay", "pad": 16}}


def 画面(name, path, user="teacher01", **kw):
    d = {"name": f"screens/{name}", "path": path, "user": user, "width": 900, "height": 600, "steps": [], "marks": []}
    d.update(kw)
    return d


def 欄(ラベル):
    return ", ".join(f"{t}:has(label:text-is('{ラベル}'))" for t in
                     ("vaadin-text-field", "vaadin-integer-field", "vaadin-select", "vaadin-combo-box", "vaadin-date-picker"))


INPUT = "/demo/input"
BUTTON = "/demo/button"
LAYOUT = "/demo/layout"
GRID = "/demo/grid"
FORM = "/demo/form"

SHOTS = [
    # ===== 通知・ダイアログ（05 章）=====
    通知("default", "通知（種類なし）"), 通知("info", "通知（情報）"), 通知("success", "通知（成功）"),
    通知("warning", "通知（警告）"), 通知("error", "通知（エラー）"),
    {"name": "parts/confirm-dialog-basic", "path": "/demo/feedback", "user": "teacher01", "hide": ["vaadin-app-layout"],
     "steps": [("click", "確認ダイアログ（基本）")],
     "clip": {"sel": "vaadin-confirm-dialog-overlay [part=overlay]", "pad": 36},
     "marks": [
         {"sel": "vaadin-confirm-dialog h3[slot=header]", "how": "text", "n": 1, "label": "題名（`setHeader`）"},
         {"sel": "vaadin-confirm-dialog > div", "how": "text", "n": 2, "label": "本文（`setText`）"},
         {"sel": "vaadin-confirm-dialog vaadin-button[slot=cancel-button]", "n": 3, "label": "キャンセルのボタン（`setCancelable`、`setCancelText`）"},
         {"sel": "vaadin-confirm-dialog vaadin-button[slot=confirm-button]", "n": 4, "label": "確認のボタン（`setConfirmText`）"},
     ]},
    {"name": "parts/confirm-dialog-danger", "path": "/demo/feedback", "user": "teacher01", "hide": ["vaadin-app-layout"],
     "steps": [("click", "確認ダイアログ（削除）")],
     "clip": {"sel": "vaadin-confirm-dialog-overlay [part=overlay]", "pad": 12}},
    {"name": "parts/dialog-basic", "path": "/demo/feedback", "user": "teacher01", "hide": ["vaadin-app-layout"],
     "steps": [("click", "ダイアログ（基本）")],
     "clip": {"sel": "vaadin-dialog-overlay [part=overlay]", "pad": 36},
     "marks": [
         {"sel": "vaadin-dialog h2[slot=title]", "how": "text", "n": 1, "label": "題名（`setHeaderTitle`）"},
         {"sel": "vaadin-dialog vaadin-integer-field", "n": 2, "label": "本文（`add` で追加した部品）"},
         {"sel": ["vaadin-dialog [slot=footer] vaadin-button:nth-child(1)", "vaadin-dialog [slot=footer] vaadin-button:nth-child(2)"],
          "n": 3, "label": "フッターのボタン（`getFooter().add` で追加）"},
     ]},

    # ===== 入力コンポーネント（05 章）=====
    部品("input-text-all", INPUT, "input-text-all", pad=36, marks=[
        {"sel": "#input-text-all [slot=label]", "how": "text", "tight": True, "n": 1, "label": "ラベル（コンストラクタの引数。必須のときは、横に印が付く）"},
        {"sel": "#input-text-all vaadin-text-field", "how": "part:input-field", "tight": True, "n": 2, "label": "入力欄（空のときは、プレースホルダーが薄く表示される）"},
        {"sel": "#input-text-all [slot=helper]", "how": "text", "tight": True, "n": 3, "label": "ヘルパーテキスト（`setHelperText`）"},
    ]),
    部品("input-text-basic", INPUT, "input-text-basic"),
    部品("input-text-placeholder", INPUT, "input-text-placeholder"),
    部品("input-text-helper", INPUT, "input-text-helper"),
    部品("input-text-required", INPUT, "input-text-required"),
    部品("input-text-error", INPUT, "input-text-error"),
    部品("input-text-readonly", INPUT, "input-text-readonly"),
    部品("input-text-disabled", INPUT, "input-text-disabled"),
    部品("input-integer", INPUT, "input-integer"),
    部品("input-password", INPUT, "input-password"),
    部品("input-date", INPUT, "input-date"),
    部品("input-select", INPUT, "input-select"),
    部品("input-combo", INPUT, "input-combo"),
    部品("input-radio", INPUT, "input-radio"),
    部品("input-checkbox-group", INPUT, "input-checkbox-group"),

    # ===== ボタン（05 章）=====
    部品("button-default", BUTTON, "button-default"),
    部品("button-primary", BUTTON, "button-primary"),
    部品("button-tertiary", BUTTON, "button-tertiary"),
    部品("button-error", BUTTON, "button-error"),
    部品("button-success", BUTTON, "button-success"),
    部品("button-warning", BUTTON, "button-warning"),
    部品("button-small", BUTTON, "button-small"),
    部品("button-large", BUTTON, "button-large"),
    部品("button-icon", BUTTON, "button-icon"),
    部品("button-disabled", BUTTON, "button-disabled"),

    # ===== レイアウト（04 章）=====
    部品("layout-vertical", LAYOUT, "layout-vertical"),
    部品("layout-horizontal", LAYOUT, "layout-horizontal"),
    部品("layout-no-padding", LAYOUT, "layout-no-padding"),
    部品("layout-justify-between", LAYOUT, "layout-justify-between"),
    部品("layout-justify-center", LAYOUT, "layout-justify-center"),
    部品("layout-align-center", LAYOUT, "layout-align-center"),
    部品("layout-expand", LAYOUT, "layout-expand"),
    部品("layout-wrap", LAYOUT, "layout-wrap"),
    部品("layout-form-wide", LAYOUT, "layout-form-wide"),
    部品("layout-form-narrow", LAYOUT, "layout-form-narrow"),

    # ===== Grid（07 章）=====
    部品("grid-basic", GRID, "grid-basic"),
    部品("grid-sortable", GRID, "grid-sortable", pad=36, marks=[
        {"sel": "#grid-sortable vaadin-grid-sorter:has-text('氏名')", "how": "text", "n": 1, "label": "列の見出し（`setHeader`）"},
        {"sel": "#grid-sortable vaadin-grid-cell-content:text-is('Hanako')", "n": 2, "label": "セル（1 行・1 列分のデータ）"},
        {"sel": "#grid-sortable vaadin-grid-sorter:has-text('氏名')", "how": "part:indicators", "n": 3, "label": "並べ替えの矢印（`setSortable(true)`）"},
    ]),
    部品("grid-component-column", GRID, "grid-component-column"),
    部品("grid-selection-multi", GRID, "grid-selection-multi"),

    # ===== フォーム・入力チェック（08 章）=====
    部品("form-required", FORM, "form-required"),
    部品("form-range", FORM, "form-range"),
    部品("form-status-label", FORM, "form-status-label"),


    # ===== 追加の部品（05 章の表示部品、03 ナビゲーション、06 イベント、10 ログイン、12 セキュリティ、13 テーマ）=====
    部品("input-text-area", INPUT, "input-text-area"),
    部品("input-email", INPUT, "input-email"),
    部品("input-number", INPUT, "input-number"),
    部品("input-checkbox", INPUT, "input-checkbox"),
    部品("input-multi-combo", INPUT, "input-multi-combo"),
    部品("layout-tabs", LAYOUT, "layout-tabs"),
    部品("layout-details", LAYOUT, "layout-details"),
    部品("display-headings", "/demo/display", "display-headings"),
    部品("display-paragraph", "/demo/display", "display-paragraph"),
    部品("display-icon", "/demo/display", "display-icon"),
    部品("display-avatar", "/demo/display", "display-avatar"),
    部品("display-progress", "/demo/display", "display-progress"),
    部品("nav-router-link", "/demo/navigation", "nav-router-link"),
    部品("nav-side-nav", "/demo/navigation", "nav-side-nav"),
    部品("events-value-change", "/demo/events", "events-value-change"),
    部品("login-default", "/demo/login", "login-default"),
    部品("login-japanese", "/demo/login", "login-japanese"),
    部品("login-error", "/demo/login", "login-error"),
    部品("security-span", "/demo/security", "security-span"),
    部品("security-html", "/demo/security", "security-html"),
    部品("theme-class", "/demo/theme", "theme-class"),
    部品("theme-variable", "/demo/theme", "theme-variable"),
    部品("theme-dark", "/demo/theme", "theme-dark"),


    # ===== 09 章（例外の表示）、A2（開発モードと本番モード）、A4（アップロード・Signals）、11 章（アクセス拒否）=====
    {"name": "parts/usecase-success", "path": "/demo/feedback", "user": "teacher01", "steps": [("click", "例外の表示（成功）")],
     "hide": ["vaadin-app-layout"], "clip": {"sel": "vaadin-notification-card", "how": "part:overlay", "pad": 16}},
    {"name": "parts/usecase-domain-error", "path": "/demo/feedback", "user": "teacher01", "steps": [("click", "例外の表示（Domain）")],
     "hide": ["vaadin-app-layout"], "clip": {"sel": "vaadin-notification-card", "how": "part:overlay", "pad": 16}},
    {"name": "parts/usecase-not-found", "path": "/demo/feedback", "user": "teacher01", "steps": [("click", "例外の表示（見つからない）")],
     "hide": ["vaadin-app-layout"], "clip": {"sel": "vaadin-notification-card", "how": "part:overlay", "pad": 16}},
    部品("advanced-upload-default", "/demo/advanced", "advanced-upload-default"),
    部品("advanced-upload-japanese", "/demo/advanced", "advanced-upload-japanese"),
    部品("advanced-signal", "/demo/advanced", "advanced-signal"),
    画面("access-denied", "/students/register", user="student01", width=520, height=120),
    画面("mode-production", "/students"),
    画面("mode-development", "/students", base="dev"),

    # ===== 画面（幅 900。要所だけ）=====
    画面("app-layout", "/students", width=1100, height=640, marks=[
        {"sel": ["vaadin-side-nav-item:first-of-type", "vaadin-side-nav-item:last-of-type"], "how": "text", "n": 1, "label": "メニュー（`SideNav`）"},
        {"sel": "vaadin-app-layout [slot=navbar]", "inset": True, "n": 2, "label": "上のバー（`addToNavbar`）"},
        {"sel": "vaadin-app-layout vaadin-vertical-layout", "inset": True, "n": 3, "label": "ビューの内容"},
    ]),
    画面("students", "/students"),
    画面("register", "/students/register"),
    画面("transcript", "/students/2/transcript", marks=[
        {"sel": "h2:has-text('さんの成績')", "how": "text", "n": 1, "label": "誰の成績か"},
        {"sel": "vaadin-grid-cell-content:text-is('履修中')", "n": 2, "label": "履修中の行（点数がないので、「履修中」と表示）"},
        {"sel": "span:has-text('平均点')", "how": "text", "n": 3, "label": "平均点（点数のある履修だけの平均）"},
    ]),
    画面("enrollment-error", "/enrollments/register", steps=[
        ("choose", "学生", "1 Taro"), ("choose", "科目", "プログラミング基礎"),
        ("fill", "点数", "150"), ("click", "登録する"), ("wait", 600)], marks=[
        {"sel": 欄("点数"), "n": 1, "label": "範囲外の点数（150）を入力した欄"},
        {"sel": "vaadin-notification-card", "how": "part:overlay", "n": 2, "label": "Domain の検査のメッセージ（エラーの通知）"},
    ]),
    画面("login", "/login", user=None, marks=[
        {"sel": "vaadin-login-form vaadin-text-field", "how": "part:input-field", "n": 1, "label": "ユーザー名"},
        {"sel": "vaadin-login-form vaadin-password-field", "how": "part:input-field", "n": 2, "label": "パスワード"},
        {"sel": "vaadin-login-form vaadin-button", "n": 3, "label": "ログインのボタン"},
    ]),
    画面("login-error", "/login?error", user=None, clip={"sel": "vaadin-login-form", "pad": 12}),
    画面("header-logout", "/students", clip={"sel": "vaadin-app-layout [slot=navbar]", "pad": 4}),
    画面("menu-teacher", "/students", width=1100, height=640, clip={"sel": "vaadin-side-nav", "pad": 8}),
    画面("menu-student", "/", user="student01", width=1100, height=640, clip={"sel": "vaadin-side-nav", "pad": 8}),

    # ===== テーマの比較（13 章）。Aura は、別のテーマで起動したアプリ（--alt-url aura=…）=====
    {"name": "parts/theme-lumo", "path": "/students/register", "user": "teacher01",
     "clip": {"sel": "vaadin-app-layout vaadin-vertical-layout", "pad": 8}, "width": 900, "height": 600, "steps": []},
    {"name": "parts/theme-aura", "path": "/students/register", "user": "teacher01", "base": "aura",
     "clip": {"sel": "vaadin-app-layout vaadin-vertical-layout", "pad": 8}, "width": 900, "height": 600, "steps": []},

    # ===== 手動撮影（Claude in Chrome で撮影し、赤枠と番号は、画像の加工で付ける）。capture.py は撮影しない =====
    {"name": "setup/vdn-02-01-vaadin-start", "manual": True, "path": "https://start.vaadin.com/", "marks": [
        {"sel": "", "n": 1, "label": "Java のバージョン（この資料は、**Java 25 LTS**。既定のままでよい）"},
        {"sel": "", "n": 2, "label": "テーマ（この資料は、**Lumo**。既定は Aura）"},
        {"sel": "", "n": 3, "label": "グループ ID とアーティファクト ID（プロジェクトの名前）"},
        {"sel": "", "n": 4, "label": "ダウンロードのボタン（zip が、ダウンロードされる）"},
    ]},
]
