# 09. SQL：基本操作

[📖 データベースの目次](./00_はじめに.md#目次) ｜ [🏠 全体の目次](../README.md#目次)

[← 前へ：08 SQL：テーブルの作成（DDL）](08_SQL_DDL.md) ｜ [次へ：10 SQL：応用 →](10_SQL_応用.md)

## この章のゴール
- `INSERT`・`SELECT`・`UPDATE`・`DELETE` を使って、データを操作できる
- `WHERE` で、条件に合う行だけを対象にできる
- `NULL` の扱い（`IS NULL`、3 値論理）を理解している
- 制約に違反したときのエラーを読み取れる
- `WHERE` の付け忘れの危険性を知り、実行前に確認する習慣がある

## 目次

1. [準備：サンプルデータを入れる](#1-準備サンプルデータを入れる)
2. [INSERT：行を追加する](#2-insert行を追加する)
3. [SELECT：行を取り出す](#3-select行を取り出す)
4. [WHERE：条件で絞り込む](#4-where条件で絞り込む)
5. [NULL の扱い](#5-null-の扱い)
6. [ORDER BY / LIMIT：並べ替えと件数の制限](#6-order-by--limit並べ替えと件数の制限)
7. [式と CASE](#7-式と-case)
8. [UPDATE：行を更新する](#8-update行を更新する)
9. [DELETE：行を削除する](#9-delete行を削除する)
10. [制約違反のエラー](#10-制約違反のエラー)
11. [自動採番の位置を合わせる](#11-自動採番の位置を合わせる)
12. [よくあるミス](#12-よくあるミス)

---

## 1. 準備：サンプルデータを入れる

08 章で作ったテーブルに、サンプルデータを入れます。

```bash
psql -U postgres -d grades_db -f db/02_seed.sql
```

> 📦 **サンプル**：[`db/02_seed.sql`](https://github.com/<ORG>/PRMN_SYSTEM_Sample/blob/main/db/02_seed.sql)

入るデータの概要です。

| テーブル | 件数 | 内容 |
|---|---|---|
| departments | 3 | 情報システム学科、電子工学科、応用化学科 |
| teachers | 4 | 佐藤 健、鈴木 恵、高橋 誠、田中 優子 |
| students | 6 | Taro、Hanako、Jiro、Sakura、Ken、Yuki |
| courses | 5 | プログラミング基礎、データベース、線形代数、電気回路、有機化学 |
| enrollments | 15 | 履修記録（うち 3 件は、点数が NULL の「履修中」） |

> 💡 もう一度やり直したいときは、`01_schema.sql` → `02_seed.sql` の順に流し直せば、最初の状態に戻ります。

## 2. INSERT：行を追加する

```sql
INSERT INTO students (name, department_id, enrolled_year)
VALUES ('Mika', 3, 2025);
```

- 追加する**列を、テーブル名の後ろに明示する**（列の順序が変わっても壊れない）
- 自動採番の `student_id` は**書かない**（省略すると、自動で振られる）
- 文字列は**シングルクォート** `'...'` で囲む

### 複数行をまとめて追加する

```sql
INSERT INTO students (name, department_id, enrolled_year) VALUES
    ('Aki', 1, 2025),
    ('Ren', 2, 2025);
```

### 採番された ID を受け取る

追加した行の ID は、`RETURNING` で受け取れます。Java から使うときに便利です（12 章）。

```sql
INSERT INTO students (name, department_id, enrolled_year)
VALUES ('Mika', 3, 2025)
RETURNING student_id;
```

## 3. SELECT：行を取り出す

もっとも基本の形です。

```sql
SELECT * FROM students;                  -- すべての列
SELECT name, enrolled_year FROM students; -- 必要な列だけ
```

<!-- 📷 SS: ../images/database/pgadmin/pga-09-01-select-result.png -->
> 📷 **スクショ指定：`pga-09-01-select-result.png`**
> - 画面：Query Tool で `SELECT * FROM students;` を実行し、6 行の結果が表示された状態
> - 強調：実行した SQL と、結果の列見出し（student_id / name / department_id / enrolled_year）を赤枠で囲む

| 書き方 | 意味 |
|---|---|
| `SELECT *` | すべての列。学習中は便利だが、**アプリケーションのコードでは列を明示する**（列が増えても影響を受けない） |
| `SELECT 列名, 列名` | 指定した列だけ |
| `AS` | 列に別名を付ける。`SELECT name AS 学生名 FROM students` |
| `DISTINCT` | 重複を除く。`SELECT DISTINCT academic_year FROM enrollments` |

## 4. WHERE：条件で絞り込む

`WHERE` に条件を書くと、**条件に合う行だけ**が対象になります。

```sql
SELECT name, enrolled_year FROM students WHERE department_id = 1;
```

| name | enrolled_year |
|---|---|
| Taro | 2024 |
| Hanako | 2024 |
| Ken | 2025 |

### 条件の書き方

| 種類 | 書き方 | 例 |
|---|---|---|
| 比較 | `=` `<>`（等しくない） `<` `<=` `>` `>=` | `score >= 60` |
| 範囲 | `BETWEEN a AND b`（a 以上 b 以下） | `academic_year BETWEEN 2024 AND 2025` |
| 候補 | `IN (a, b, ...)` | `department_id IN (1, 2)` |
| 文字列の部分一致 | `LIKE` （`%` は任意の文字列、`_` は任意の 1 文字） | `title LIKE 'プログラ%'` |
| 組み合わせ | `AND` `OR` `NOT` | `score >= 60 AND academic_year = 2024` |

> 💡 SQL の `=` は**比較**です（Java の `==` にあたる）。代入ではありません。等しくない場合は `<>` と書きます（`!=` も使えます）。

`AND` と `OR` を混ぜるときは、**括弧で優先順位を明示**します。

```sql
SELECT * FROM enrollments
WHERE academic_year = 2025 AND (score >= 90 OR score < 60);
```

## 5. NULL の扱い

`NULL` は「**値がない**」ことを表す特別な値で、0 や空文字とは違います。成績管理では、`score` が NULL の行が「履修中」を表します。

### NULL は `=` で比較できない

```sql
SELECT * FROM enrollments WHERE score = NULL;       -- ✕ 1 件も返らない
SELECT * FROM enrollments WHERE score IS NULL;      -- ○ 履修中の 3 件
SELECT * FROM enrollments WHERE score IS NOT NULL;  -- ○ 評価済みの 12 件
```

NULL に対する `=` や `<` などの比較は、結果が真でも偽でもなく「**不明**」になり、`WHERE` に合致しません。NULL かどうかは、**必ず `IS NULL` / `IS NOT NULL`** で調べます。

### 3 値論理

NULL を含む比較では、結果が「真・偽・**不明**」の 3 つになります。`WHERE` は「真」の行だけを返します。

| 条件 | 返る件数（15 件中） |
|---|---|
| `score >= 60` | 10 件 |
| `score < 60` | 2 件 |
| `score >= 60 OR score < 60` | **12 件**（NULL の 3 件は含まれない） |

「60 以上か、60 未満」と書いても、**15 件全部にはなりません**。NULL の行は、どちらでもないからです。

### NULL を別の値に置き換える

```sql
SELECT student_id, course_id, COALESCE(score, 0) AS score FROM enrollments;
```

`COALESCE(a, b)` は、「`a` が NULL なら `b`」です。ただし、**「履修中」を 0 点として扱う**ことになるので、意味を考えて使います。

> [!WARNING]
> **NULL を含む計算は NULL になります**（`score + 10` は、`score` が NULL なら NULL）。集計関数（`AVG` など）は、NULL の行を**無視**します（10 章）。

## 6. ORDER BY / LIMIT：並べ替えと件数の制限

```sql
SELECT student_id, course_id, score FROM enrollments
WHERE score IS NOT NULL
ORDER BY score DESC
LIMIT 3;
```

| student_id | course_id | score |
|---|---|---|
| 2 | 1 | 95 |
| 4 | 3 | 91 |
| 2 | 2 | 88 |

| 句 | 意味 |
|---|---|
| `ORDER BY 列 [ASC / DESC]` | 並べ替え。`ASC` が昇順（既定）、`DESC` が降順。複数列も指定できる（`ORDER BY enrolled_year, name`） |
| `LIMIT n` | 最大 n 件まで |
| `OFFSET m` | 先頭 m 件を飛ばす（`LIMIT n OFFSET m` でページ送りになる） |

> [!WARNING]
> **`ORDER BY` を書かないと、行の順序は保証されません**。「普段は入れた順に出るから」と期待してはいけません。

> 💡 PostgreSQL では、**NULL は最も大きい値として扱われます**。そのため、`ORDER BY score DESC` では**NULL の行が先頭**に来ます。上の例のように `WHERE score IS NOT NULL` で除くか、`ORDER BY score DESC NULLS LAST` と指定します。

## 7. 式と CASE

`SELECT` では、列の値を使った計算や、条件による分岐もできます。

```sql
SELECT student_id, course_id, score,
       CASE
           WHEN score IS NULL THEN '履修中'
           WHEN score >= 60   THEN '合格'
           ELSE                    '不合格'
       END AS result
FROM enrollments;
```

`CASE` は、Java の `if - else if - else` に近い式です。この例は、4層アーキテクチャ編の `Enrollment.isPassed()`（60 点以上が合格）と同じ判定を、SQL で書いたものです。

> 💡 **同じルールが、Java（Domain 層）と SQL の両方に現れる**ことになります。合格点を変える場合に両方を直す必要が出てきます。こうした重複を避けるため、判定は Domain 層に集め、SQL は**データの取り出しに専念させる**設計が基本です。

## 8. UPDATE：行を更新する

```sql
UPDATE enrollments
SET score = 85
WHERE student_id = 2 AND course_id = 3 AND academic_year = 2025;
```

履修中だった Hanako の線形代数に、点数 85 を入れる例です。`SET` で複数の列をまとめて変更するときは、`SET a = 1, b = 2` とカンマで区切ります。

> [!WARNING]
> **`WHERE` を付け忘れると、テーブルの全行が更新されます。** `UPDATE enrollments SET score = 85;` は、全員の全科目の点数を 85 にしてしまいます。

### 実行前に確認する習慣

`UPDATE` や `DELETE` を実行する前に、**同じ `WHERE` で `SELECT` を実行して、対象の行を確認**します。

```sql
SELECT * FROM enrollments WHERE student_id = 2 AND course_id = 3 AND academic_year = 2025;   -- 1 件だけか確認
```

1 件だけと確認できたら、`SELECT *` の部分を `UPDATE ... SET ...` に書き換えて実行します。さらに安全にするには、トランザクション（11 章）の中で実行し、結果を確認してから確定します。

## 9. DELETE：行を削除する

```sql
DELETE FROM enrollments
WHERE student_id = 3 AND course_id = 4 AND academic_year = 2024;
```

> [!WARNING]
> **`DELETE` も、`WHERE` がないと全行が消えます。** 必ず `SELECT` で対象を確認してから実行してください。

> 🔒 **セキュリティの視点**：データは、操作のミスだけでなく、攻撃でも失われます。代表的なのが**ランサムウェア**（データを暗号化して使えなくし、元に戻す代わりに身代金を要求する攻撃）で、IPA の「情報セキュリティ10大脅威 2026」（組織編）の 1 位です（[IPA](https://www.ipa.go.jp/security/10threats/10threats2026.html)、閲覧日：2026-11-08）。定期的に**バックアップ**を取り（PostgreSQL では [`pg_dump`](https://www.postgresql.jp/document/18/html/app-pgdump.html)）、**普段つながっている場所だけに置かない**ようにします。
> 実例：2025 年のアスクルの被害では、サーバーと同じデータセンターにあったバックアップも暗号化され、削除もされたため、復旧が長引きました（[アスクル 第 13 報](https://pdf.irpocket.com/C0032/PDLX/O3bg/N4O3.pdf)、2025-12-12、閲覧日：2026-11-08）。

### 外部キーの動作を確かめる

06 章で決めた `ON DELETE` の動作を、実際に確かめてみましょう。

| 操作 | 結果 | 理由 |
|---|---|---|
| `DELETE FROM courses WHERE course_id = 1;` | **エラー**になる | `enrollments.course_id` は `ON DELETE RESTRICT`。履修記録がある科目は消せない |
| `DELETE FROM students WHERE student_id = 1;` | 学生が消え、その**履修記録も一緒に消える** | `enrollments.student_id` は `ON DELETE CASCADE` |
| `DELETE FROM departments WHERE department_id = 1;` | **エラー**になる | 学生・教員が所属している（既定は RESTRICT） |

> 💡 行の `DELETE` と、テーブルの `DROP TABLE`（08 章）は別物です。`DELETE` はテーブルの構造を残し、行だけを消します。

## 10. 制約違反のエラー

制約に反する操作は、DBMS がエラーにして**拒否**します。エラーメッセージを読めるようになりましょう。

| 操作 | エラーメッセージ（要点） | 違反した制約 |
|---|---|---|
| 存在しない学科 99 の学生を追加 | `violates foreign key constraint "students_department_id_fkey"` | 外部キー |
| 点数 150 を登録 | `violates check constraint "enrollments_score_check"` | CHECK |
| 同じ学生・科目・年度の履修を二重に登録 | `duplicate key value violates unique constraint ...` | UNIQUE |
| 名前を NULL で学生を追加 | `null value in column "name" ... violates not-null constraint` | NOT NULL |

メッセージには、**どの制約に違反したか**（制約名）と、**どの値が問題か**（`DETAIL` 行）が書かれています。

> 💡 これらのエラーは、Java からは例外として届きます（12 章）。Domain 層の検査で多くは防げますが、**最後の砦としてデータベースが止めてくれる**ことを、ここで体験しておきましょう（06 章）。

## 11. 自動採番の位置を合わせる

`02_seed.sql` の末尾には、`setval` を呼ぶ行があります。

```sql
SELECT setval(pg_get_serial_sequence('students', 'student_id'), (SELECT MAX(student_id) FROM students));
```

サンプルデータは **ID を指定して**投入しました（06 章の `GENERATED BY DEFAULT`）。この場合、自動採番の「次の番号」は進まないため、そのままだと次の `INSERT` が **1 番から始まって、既存の ID とぶつかってエラー**になります。`setval` で、次の番号を「現在の最大値の次」に合わせています。

| 状況 | 何が起きるか |
|---|---|
| ID を指定せずに INSERT | 自動採番が進む（通常の使い方） |
| ID を**指定して** INSERT | 自動採番は進まない。`setval` で合わせないと、あとで重複エラー |

## 12. よくあるミス

| ミス | 原因・対処 |
|---|---|
| `UPDATE` / `DELETE` で `WHERE` を付け忘れ、全行が変わった | 必ず事前に `SELECT` で対象を確認する。トランザクション（11 章）の中で実行する |
| `WHERE score = NULL` と書いて 1 件も出ない | NULL は `IS NULL` で調べる |
| `score >= 60 OR score < 60` で全件が出ると思う | NULL の行は含まれない（3 値論理） |
| 文字列に `"` を使う | 文字列は `'...'`。`"` は名前を囲む記号 |
| `ORDER BY` を書かずに、順序を期待する | 順序は保証されない。必要なら必ず指定する |
| `ORDER BY score DESC` で NULL が先頭に来る | PostgreSQL は NULL を最大値扱い。`NULLS LAST` を指定する |
| `AND` と `OR` を混ぜて、意図と違う結果になる | 括弧で優先順位を明示する |
| ID を指定して INSERT したあと、通常の INSERT が重複エラーになる | `setval` で採番の位置を合わせる |
| `SELECT *` をアプリケーションのコードに書く | 列を明示する。列が増減しても影響を受けにくい |

---

[← 前へ：08 SQL：テーブルの作成（DDL）](08_SQL_DDL.md) ｜ [次へ：10 SQL：応用 →](10_SQL_応用.md)

[📖 データベースの目次](./00_はじめに.md#目次) ｜ [🏠 全体の目次](../README.md#目次)
