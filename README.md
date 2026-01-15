# DynamoDB アーキテクト学習用チュートリアル（FastAPI）

このプロジェクトは、ブログ + アクティビティという小さな題材を使って、
「DynamoDB を使うときの設計上のメリット / 勘所」を体感するためのチュートリアルです。

## 何を学ぶか（アーキテクト視点）

- アクセスパターン起点の設計  
  - 先に「どんなクエリを投げたいか（アクセスパターン）」を列挙し、そこから PK / SK・GSI を決める
- PK / SK ＝ クエリ条件そのもの  
  - JOIN で自由に組み合わせるのではなく、同じ PK に「一緒に取りたいもの」を集約し、SK の範囲指定で読む
- GSI の位置づけ  
  - 「追加の入口」を増やす代わりに、コストと制約が増えることを前提に設計する
- 競合と整合性の扱い  
  - アトミックカウンタ・条件付き更新・冪等な更新単位の設計
- ホットパーティションの回避  
  - アクセスが集中しうるキー（例: 人気記事）の設計と分散戦略
- TTL を使ったライフサイクル設計  
  - セッションや一時ログなど、消してよいデータは自動削除で管理する
- RDB と DynamoDB の分業  
  - 正規化された業務データは RDB、イベント / ログ / 高頻度更新・時系列は DynamoDB に寄せる

## このアプリでの役割分担

- SQLite
  - ブログ投稿（タイトル / 本文 / 著者 / 作成日時）など、素直な CRUD 用の構造化データ
- DynamoDB
  - 「アクセス形がはっきりしている」データを担当
  - アクティビティ（閲覧・いいね・コメントなどの時系列ログ）
  - いいね数（競合しやすいカウンタをアトミックに更新）
  - コメント（投稿単位の集合 + スレッド構造）
  - セッション（TTL 付きの短命データ）

## DynamoDB テーブル設計のポイント

- activities テーブル
  - PK: user_id / SK: timestamp  
    - ユーザーごとの直近 N 件アクティビティを、範囲クエリで高速取得
  - GSI: ActivityTypeIndex (PK: activity_type, SK: timestamp)  
    - 「いいねだけ」「コメントだけ」など種別ごとの最近 N 件を取る
  - GSI: PostActivityIndex (PK: post_id, SK: timestamp)  
    - 特定の投稿に対するアクティビティの時系列を取る

- likes テーブル
  - PK: post_id  
  - ADD 演算子を使ったアトミックカウンタで「いいね数」と「ユーザーごとの状態」を更新

- comments テーブル
  - PK: post_id / SK: comment_id（タイムスタンプ + ランダム）  
  - 「ある投稿のコメント一覧」を 1 パーティション内に集約し、並び順とスレッド構造をアプリ側で組み立てる

- sessions テーブル
  - PK: session_id  
  - TTL を有効化して、一定時間で自動削除されるセッションを表現

> 補足: 「全件の最近のアクティビティ」を取るために Scan を使っている箇所があります。  
> あえて Scan を使うことで、「学習用としては便利だが、本番ではアクセスパターン設計で避けるべき」という対比も体験できます。

## 最小の起動手順

前提: Docker / Docker Compose が使えること。

```bash
docker compose up -d

# DynamoDB テーブル作成
docker compose exec app ./cli/init_dynamodb.py

# ブログ初期データ投入
docker compose exec app ./cli/init_data.py
```

- アプリ: http://localhost:8000
- DynamoDB Admin（GUI）: http://localhost:4567

# 参考リンク

- DynamoDB Developer Guide https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/
- DynamoDB Best Practices https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html

# Appendix

<details>
<summary>このプロジェクトを生成したLLMへのプロンプト</summary>

```md
WebサービスにおけるDynamoDBの用途を学習したい。典型的なユースケースを身に着けることができる簡単なサンプルアプリケーションを作って
NoSQLの特性をきちんと考慮して考えてね

RDBが登場してもいいけど、目的はDynamoDBだから必要最小限にしてね

使用するスタックはこんな感じ

* 言語、フレームワーク: Python/FastAPI, htmx
* RDB: PostgreSQL、sqlite3
* SDK: boto3
* DynamoDB: コンテナイメージを使用する（amazon/dynamodb-local）
```

</details>
