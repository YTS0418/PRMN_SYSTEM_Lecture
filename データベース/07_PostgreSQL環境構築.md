# 07. PostgreSQL環境構築

[📖 データベースの目次](./00_はじめに.md#目次) ｜ [🏠 全体の目次](../README.md#目次)

[← 前へ：06 物理設計](06_物理設計.md) ｜ [次へ：08 SQL：テーブルの作成（DDL） →](08_SQL_DDL.md)

## この章のゴール
- PostgreSQL をインストールして、起動を確認できる
- コマンドラインツール（psql）と GUI ツール（pgAdmin）で接続できる
- 学習用のデータベース `grades_db` を作成できる
- サンプルの SQL ファイルを実行できる

## 目次

1. [全体像](#1-全体像)
2. [PostgreSQL のインストール（Windows）](#2-postgresql-のインストールwindows)
3. [他の方法：macOS / Docker](#3-他の方法macos--docker)
4. [psql で接続する](#4-psql-で接続する)
5. [pgAdmin で接続する](#5-pgadmin-で接続する)
6. [データベースを作成する](#6-データベースを作成する)
7. [サンプルの SQL を実行する](#7-サンプルの-sql-を実行する)
8. [psql が見つからないときの対処（PATH の設定）](#8-psql-が見つからないときの対処path-の設定)
9. [よくあるミス](#9-よくあるミス)

---

## 1. 全体像

用意するものは、**PostgreSQL のサーバー**と、それを操作する**クライアント**です。

```mermaid
flowchart LR
    subgraph C["クライアント（操作する側）"]
        psql["psql<br>（コマンドライン）"]
        pga["pgAdmin 4<br>（GUI）"]
        java["Java アプリ<br>（JDBC：12 章）"]
    end
    srv[("PostgreSQL サーバー<br>ポート 5432")]
    psql --> srv
    pga --> srv
    java --> srv
```

| 名前 | 役割 |
|---|---|
| **PostgreSQL サーバー** | データを保管し、SQL を実行する本体（常に起動しておく） |
| **psql** | コマンドラインから SQL を実行するツール。インストーラに付属 |
| **pgAdmin 4** | ブラウザ風の画面で、データベースを操作できる GUI ツール。インストーラに付属 |

この資料では、**SQL を試すときは psql か pgAdmin のどちらか**を使います。使いやすいほうで構いません。

> [!NOTE]
> サーバーは、パソコンの中で動く**常駐プログラム**です。インストールすると、Windows の起動時に自動で立ち上がるのが普通です。

## 2. PostgreSQL のインストール（Windows）

1. [PostgreSQL 公式サイトのダウンロードページ](https://www.postgresql.org/download/windows/)から、Windows 用のインストーラ（EDB 提供）をダウンロードする
2. ダウンロードしたインストーラを実行する
3. 画面の案内に従って進める。**次の 3 か所だけ注意**してください

### コンポーネントの選択

次の 3 つにチェックを入れます（Stack Builder は不要です）。

![インストーラの Select Components の画面](../images/database/postgres/pg-07-01-installer-components.png)

### パスワードの設定

`postgres` ユーザー（データベースの管理者）の**パスワード**を決めます。

![インストーラの Password 画面](../images/database/postgres/pg-07-02-installer-password.png)

> [!WARNING]
> **このパスワードは忘れないでください**。接続のたびに必要です。学習用のパソコンでも、推測されにくいものにしましょう。

> [!CAUTION]
> **セキュリティの視点**：Docker の例（3 節）の `postgres` のような簡単なパスワードは、**自分のパソコンの中から接続する**ときに限って使います。設定ファイル（`postgresql.conf` の `listen_addresses`、`pg_hba.conf`）を書き換えて、**ほかのコンピュータからの接続を許可しない**でください。

### ポート番号

通常は、既定の **5432** のままにします。

![インストーラの Port 画面](../images/database/postgres/pg-07-03-installer-port.png)

それ以外（インストール先、ロケールなど）は、既定のままで構いません。インストールが終わると、サーバーが自動で起動します。

## 3. 他の方法：macOS / Docker

### macOS

Homebrew が使える場合の例です。

```bash
brew install postgresql@18
brew services start postgresql@18
```

### Docker

Docker が使える場合、1 つのコマンドでサーバーを用意できます（パスワードは学習用の例です）。

```bash
docker run --name grades-pg -e POSTGRES_PASSWORD=postgres -p 127.0.0.1:5432:5432 -d postgres:18
```

> [!NOTE]
> この方法は、**クライアント（psql など）は別に用意**します。動作確認は行っていません。公式のドキュメントも確認してください。

> [!CAUTION]
> **セキュリティの視点**：`-p 5432:5432` のように書くと、**同じネットワークにあるほかのコンピュータからも**接続できる状態になります。Docker の公式ドキュメントも、ポートの公開は既定では安全でないと注意しています。上の例のように `127.0.0.1:` を付けると、そのパソコンからしか接続できません（[Docker Docs「Port publishing and mapping」](https://docs.docker.com/engine/network/port-publishing/)、閲覧日：2026-11-08）。簡単なパスワードのデータベースを外から接続できる状態にすると、自動で探し回るプログラムに見つかり、データを盗まれたり消されたりするおそれがあります。

## 4. psql で接続する

ターミナル（Windows ではコマンドプロンプトや PowerShell）で、次のコマンドを実行します。

```bash
psql -U postgres
```

パスワードを聞かれるので、インストール時に決めたものを入力します（入力しても画面には表示されません）。

![ターミナルの実行画面](../images/database/postgres/pg-07-04-psql-login.png)

```sql
SELECT version();
```

### psql のメタコマンド

`\`（バックスラッシュ）で始まるものは、SQL ではなく **psql 自身のコマンド**で、`;` は不要です。

| コマンド | 内容 |
|---|---|
| `\l` | データベースの一覧 |
| `\c データベース名` | 別のデータベースに接続し直す |
| `\dt` | テーブルの一覧 |
| `\d テーブル名` | テーブルの構造（列・制約・インデックス） |
| `\i ファイル名` | SQL ファイルを実行する |
| `\?` | コマンドの一覧（ヘルプ） |
| `\q` | psql を終了する |

> [!TIP]
> `psql` が「コマンドが見つかりません」と表示される場合は、PostgreSQL の `bin` フォルダ（例：`C:\Program Files\PostgreSQL\18\bin`）を、環境変数 `PATH` に追加します。手順は [8 節](#8-psql-が見つからないときの対処path-の設定)で説明します。

## 5. pgAdmin で接続する

1. スタートメニューから **pgAdmin 4** を起動する（初回は、pgAdmin 自身のマスターパスワードを求められることがある）
2. 左の「Servers」を右クリック → **Register → Server...** を選ぶ
3. 「General」タブで名前を付ける（例：`local-postgres`）
4. 「Connection」タブで、次を入力する

| 項目 | 値 |
|---|---|
| Host name/address | `localhost` |
| Port | `5432` |
| Maintenance database | `postgres` |
| Username | `postgres` |
| Password | インストール時のパスワード |

![pgAdmin　の Register - Server Connection タブ](../images/database/pgadmin/pga-07-01-register-server.png)

5. 「Save」を押すと、左のツリーにサーバーが表示される

> [!NOTE]
> pgAdmin の画面は、既定では英語です。この資料の説明も、英語の表示に合わせています。

## 6. データベースを作成する

PostgreSQL は、1 つのサーバーの中に**複数のデータベース**を持てます。学習用に、`grades_db` という名前のデータベースを作ります。

### psql の場合

```sql
CREATE DATABASE grades_db;
```

作成したら、`\c grades_db` で接続先を切り替えます。

### pgAdmin の場合

1. 左のツリーで **Databases** を右クリック → **Create → Database...**
2. Database に `grades_db` と入力して「Save」

![grades_db が作成されている Object Explorer 画面](../images/database/pgadmin/pga-07-02-object-tree.png)

### Query Tool を開く

`grades_db` を選択した状態で、上部の **Query Tool** ボタン（または右クリック → Query Tool）を開くと、SQL を入力して実行できる画面になります。

![grades_db にて SELECT version(); を実行した画面](../images/database/pgadmin/pga-07-03-query-tool.png)

> [!TIP]
> Query Tool では、SQL を書いて **F5**（または ▶ ボタン）を押すと実行されます。複数の文があるときは、実行したい部分を選択してから実行します。

## 7. サンプルの SQL を実行する

サンプルリポジトリの `db/` フォルダに、テーブル定義とサンプルデータがあります。

| ファイル | 内容 | 使う章 |
|---|---|---|
| `db/01_schema.sql` | テーブルの定義 | 08 章 |
| `db/02_seed.sql` | サンプルデータ | 09・10 章 |

> [!NOTE]
> **サンプル**：[`db/`](https://github.com/YTS0418/PRMN_SYSTEM_Sample/tree/main/db)

### psql で実行する

ファイルのあるフォルダに移動して、次を実行します。

```bash
psql -U postgres -d grades_db -f db/01_schema.sql
```

`-d` は接続するデータベース、`-f` は実行する SQL ファイルです。すでに psql に入っている場合は、`\i db/01_schema.sql` でも実行できます。

### pgAdmin で実行する

Query Tool の「Open File」ボタンでファイルを開き、実行します。

> [!NOTE]
> 08 章では、`01_schema.sql` の中身を読み解きながら実行します。ここでは、まず**動くことの確認**だけで構いません。

## 8. psql が見つからないときの対処（PATH の設定）

Windows では、インストーラが `psql` の場所を `PATH` に**自動では追加しません**。そのため、インストール直後に `psql -U postgres` を実行すると、次のようなエラーになる人が多くいます。**受講者の多くが一度は遭遇する**ので、落ち着いて次の手順で対処してください。

| 使っているツール | 表示されるメッセージの例 |
|---|---|
| コマンドプロンプト | `'psql' は、内部コマンドまたは外部コマンド、操作可能なプログラムまたはバッチ ファイルとして認識されていません。` |
| PowerShell | `psql : 用語 'psql' は、コマンドレット、関数、スクリプト ファイル、または操作可能なプログラムの名前として認識されません。` |
| macOS / Linux（bash・zsh） | `command not found: psql` |

> [!NOTE]
> **PATH とは**：コマンド名だけを打ったときに、Windows が実行ファイルを探しに行くフォルダの一覧です。`psql.exe` は PostgreSQL の `bin` フォルダの中にあり、その場所が一覧に無いので「見つからない」と言われます。**PostgreSQL が壊れているわけではありません**（再インストールは不要です）。

対処は、次の 3 つのどれかを選びます。**手順 A で `bin` フォルダの場所を確認**してから、手順 B（その場しのぎ）か手順 C（恒久対応）に進んでください。

### 手順 A：`bin` フォルダの場所を確認する

1. エクスプローラーで `C:\Program Files\PostgreSQL\` を開く
2. バージョン番号のフォルダ（例：`18`）を開く
3. その中の `bin` フォルダを開き、`psql.exe` があることを確認する
4. エクスプローラー上部のアドレスバーをクリックし、表示されたパスをコピーしておく（例：`C:\Program Files\PostgreSQL\18\bin`）

> [!TIP]
> `C:\Program Files\PostgreSQL\` が見つからない場合は、インストールが完了していない、または別の場所にインストールした可能性があります。インストール時に指定した場所を確認してください。

### 手順 B：フルパスで実行する（設定を変えたくないとき）

パスをすべて書けば、`PATH` の設定なしで実行できます。スペースを含むので、**ダブルクォート `"` で囲みます**。

**コマンドプロンプトの場合**

```bat
"C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres
```

**PowerShell の場合**（先頭に `&` が必要です）

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres
```

> [!WARNING]
> PowerShell で `&` を付け忘れると、文字列として扱われてエラーになります。また、毎回この長いコマンドを打つ必要があるので、学習を続けるなら手順 C をおすすめします。

### 手順 C：環境変数 PATH に追加する（おすすめ）

一度設定すれば、以後は `psql` だけで実行できます。

1. Windows の**スタートメニュー**で「環境変数」と入力し、**「システム環境変数の編集」**を開く
2. 「システムのプロパティ」の下部にある**「環境変数(N)...」**ボタンを押す
3. 上の **「ユーザー環境変数」** の一覧から `Path` を選び、**「編集(E)...」**を押す
4. **「新規(N)」**を押し、手順 A でコピーしたパス（例：`C:\Program Files\PostgreSQL\18\bin`）を貼り付ける
5. **「OK」**を押して、開いたウィンドウをすべて閉じる（途中で「キャンセル」や × で閉じると保存されません）
6. **開いていたコマンドプロンプト / PowerShell / VS Code のターミナルをすべて閉じ、開き直す**
7. 次のコマンドで、バージョンが表示されれば成功

```bash
psql --version
```

```text
psql (PostgreSQL) 18.x
```

> [!WARNING]
> **よくある失敗**
> - **ターミナルを開いたまま**にしている：PATH の変更は、**新しく開いたターミナルにしか反映されません**。必ず開き直してください。
> - 既存の `Path` の中身を**消して上書き**してしまう：必ず「新規」で 1 行追加します。既存の行は触りません。
> - パスの**末尾に `\psql.exe` まで書いてしまう**：登録するのは `bin` フォルダまでです（`...\18\bin`）。
> - バージョン番号のフォルダ名を**間違えている**：手順 A で、実際のフォルダ名を確認します。
> - VS Code や IntelliJ のターミナルで直らない：アプリ自体を**終了して起動し直す**必要があります。

### それでも直らないときの確認

| 確認すること | 方法 |
|---|---|
| `PATH` に登録できているか | コマンドプロンプトで `echo %PATH%`、PowerShell で `$env:Path` を実行し、`...\PostgreSQL\18\bin` が含まれているか確認する |
| どの `psql` が使われているか | コマンドプロンプトで `where psql`、PowerShell で `Get-Command psql` を実行する。何も表示されなければ、まだ見つかっていない |
| `bin` の中に `psql.exe` があるか | 手順 A に戻って確認する。無い場合は、インストール時に「Command Line Tools」のチェックが外れていた可能性がある。インストーラをもう一度実行して追加する |
| 管理者権限が無くて編集できない | 手順 C の「ユーザー環境変数」は、管理者権限が無くても編集できる。「システム環境変数」しか編集できない場合は、手順 B を使う |

### macOS（Homebrew）の場合

`brew install postgresql@18` は、他のバージョンと区別するために `PATH` を自動では通さないことがあります。インストール後のメッセージ（または `brew info postgresql@18`）に表示される `PATH` の案内に従って、次のように設定します。

```bash
echo 'export PATH="$(brew --prefix postgresql@18)/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
psql --version
```

> [!NOTE]
> macOS で `zsh` 以外のシェルを使っている場合は、`~/.zshrc` をそのシェルの設定ファイル（例：`~/.bash_profile`）に読み替えてください。

### Docker の場合

Docker の例（3 節）では、**パソコン側に `psql` は入りません**。コンテナの中の `psql` を使うか、別途クライアントをインストールします。

```bash
docker exec -it grades-pg psql -U postgres
```

> [!NOTE]
> この方法で `.sql` ファイルを実行する場合は、ファイルをコンテナに渡す必要があります。迷うときは、pgAdmin を使うのが簡単です。

## 9. よくあるミス

| ミス | 原因・対処 |
|---|---|
| `psql` が見つからない | `bin` フォルダが `PATH` に無い。環境変数に追加するか、フルパスで実行する（[8 節](#8-psql-が見つからないときの対処path-の設定)に手順あり） |
| `connection refused`（接続が拒否された） | サーバーが起動していない、またはポートが違う。Windows の「サービス」で `postgresql-x64-18` のようなサービスが実行中か確認する |
| `password authentication failed` | パスワードが違う。インストール時に決めたものを確認する |
| SQL を入力しても、何も実行されない | 文末の `;` を忘れている。psql は `;` が来るまで入力が続くと考える |
| `database "grades_db" does not exist` | 作成していない、またはスペルミス。`\l` で一覧を確認する |
| 日本語が文字化けする、または `.sql` ファイルを流すと一部の `INSERT` が失敗して外部キーのエラーになる（Windows の psql） | コンソールの文字コードの違い。対話画面では `\encoding UTF8` を実行する。`-f` でファイルを流すときは、先に環境変数 `PGCLIENTENCODING` を `UTF8` にする（コマンドプロンプトは `set PGCLIENTENCODING=UTF8`、PowerShell は `$env:PGCLIENTENCODING = 'UTF8'`）。それでも直らない場合は pgAdmin を使う |
| 5432 番ポートが使用中 | 別の PostgreSQL がすでに動いている。ポートを変えるか、もう一方を停止する |
| `postgres` ユーザーのパスワードを忘れた | 再設定には手順が必要。学習用なら、再インストールが早い場合もある |

---

[← 前へ：06 物理設計](06_物理設計.md) ｜ [次へ：08 SQL：テーブルの作成（DDL） →](08_SQL_DDL.md)

[📖 データベースの目次](./00_はじめに.md#目次) ｜ [🏠 全体の目次](../README.md#目次)
