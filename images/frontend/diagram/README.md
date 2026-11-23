# フロントエンド編の図（SVG）

フロントエンド（Vaadin）資料の図（SVG）です。図の形式の使い分け（PlantUML、SVG、Mermaid）と、色、貼り方の決まりは、[資料作成ルール](/共通/資料作成ルール.md)にあります。単純な図（5 行ほどの流れ図）は、章の中の Mermaid のままにしています。

| ファイル | 内容 | 章 |
|---|---|---|
| `dia-00-01-structure` | 資料の構成 | 00 |
| `dia-01-01-browser-server` | ブラウザとサーバーのやりとり（シーケンス） | 01 |
| `dia-01-02-compare` | 画面を作る 3 つの方式の比較（SVG を直接書いた） | 01 |
| `dia-02-01-rest-to-vaadin` | REST から Vaadin へ | 02 |
| `dia-03-01-app-layout` | AppLayout の構造（SVG を直接書いた） | 03 |
| `dia-05-01-notification-positions` | Notification の位置 | 05 |
| `dia-06-01-click-flow` | ボタンを押してから、画面が更新されるまで（シーケンス） | 06 |
| `dia-07-01-lazy-loading` | Grid の遅延読み込み（シーケンス） | 07 |
| `dia-08-01-binder` | Binder の役割 | 08 |
| `dia-09-01-rest-vs-vaadin` | REST と Vaadin の対比 | 09 |
| `dia-10-01-login-flow` | ログインの流れ（シーケンス） | 10 |
| `dia-11-01-users-er` | users テーブルと、学生・履修の関係 | 11 |
| `dia-12-01-csrf` | CSRF の流れ（シーケンス） | 12 |
| `dia-A3-01-oidc` | OpenID Connect のログインの流れ（シーケンス） | A3 |

## 作り方

`.puml`（PlantUML）が、ソースです。リポジトリの直下で、共通の変換スクリプトを実行して、`.svg` を作ります（詳しくは、[資料作成ルール](/共通/資料作成ルール.md#4-plantuml-の図を作る)）。

```bash
bash tools/build-diagrams.sh images/frontend/diagram
```

`bash images/frontend/diagram/build.sh` でも同じです。

- 共通の見た目は、`_common.iuml`（フォント、色、線の太さ）。色は、4 層編と同じ（Presentation = 青、Application・Domain = 緑、Infrastructure・外部 = 黄）
- `dia-01-02-compare.svg` と `dia-03-01-app-layout.svg` は、長方形を並べるだけの図なので、PlantUML ではなく、SVG を直接書いている（`.puml` はない）
- SVG の文字は、見る人の環境の**フォント**で描かれる。そこで、変換スクリプトが、フォントの候補（Noto Sans CJK JP、Hiragino Sans、Yu Gothic、Meiryo、sans-serif）を、SVG に書き込む。日本語のフォントが 1 つもない環境では、文字が崩れる
- 章には、`<img src="…svg" alt="…" width="…">` で貼る（幅は、SVG の幅）
