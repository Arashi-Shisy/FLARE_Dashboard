# FLARE Dashboard

スマホ前提・シンプル操作のコミュニティ可視化 Web アプリ。  
**Frontend:** Vue 3 + Vite / **Backend:** Flask + Socket.IO + APScheduler / **DB:** SQLite  
**Docker:** `backend` (8000), `frontend` (nginx static, 80), `nginx` (gateway, 8080)

---

## 1. 起動方法（Docker）

```bash
# 初回
docker compose build
docker compose up -d

# 更新時
docker compose build frontend
docker compose build frontend --no-cache
docker compose up -d

docker compose build backend
docker compose up -d

# ログ確認
docker compose logs backend -f
```

アクセス: http://localhost:8080

- `/` … フロントエンド（Vue）
- `/api/*` … REST API（Flask）
- WebSocket … `/socket.io` （ログイン済みで受信）

## 2. 機能

- ユーザー登録/ログイン/ログアウト（ユーザー名＋パスワードのみ）
- マイページ（プロフィール画像、生年月日、ブラウザ通知 ON/OFF）
- ダッシュボード（**今週のイベント**・**最新お知らせ 5 件**）
- イベント一覧/詳細/登録/編集/削除、**ワンタッチ参加表明（トグル）**
- お知らせ登録/一覧/削除（作成者のみ削除可）
- コミュニティチャット（新しい順、投稿者は削除可）
- ブラウザ通知（テスト送信、新規イベント/お知らせ、参加イベントの**24 時間前/1 時間前**リマインド）
  - 仕様：タブを開いている間は、**Service Worker**経由でネイティブ通知します
  - Web Push（タブ非表示時のサーバープッシュ）は未実装（拡張余地あり）

## 3. デザイン

- 背景：`#262626`
- 強調色（FLARE 色）：`#db1280 → #c11e1e → #ed9515` のグラデーション
- チャット画面：Instagram DM 風（FLARE 色適用）

## 4. 開発メモ

- 永続化: SQLite は `backend_data` ボリューム。画像は `uploads` ボリューム。
- セッション有効期限：**31 日**（1 ヶ月以上アクセスがない場合に切れる設計）
- 再起動時のリマインド再登録：将来日付のイベントを読み直して APScheduler に再登録します。

## 5. 既知の注意

- ブラウザ通知はタブが完全に閉じている状態では届きません（Web Push 拡張が必要）。
- 本番運用時は `SECRET_KEY` を必ず変更し、HTTPS と Cookie 設定を強化してください。

## 6. テスト

- Backend UT

```bash
cd backend
$env:DISABLE_SCHEDULER="1"
pytest
```

- Frontend UT

```bash
cd frontend
npm run test         # = vitest --run (UTのみ)
npm run test:watch   # ウォッチ
npm run test:ui      # Vitest UI
```

- E2E

```bash
docker compose up -d   # http://localhost:8080

cd frontend
npm run e2e
npm run e2e:ui
```

## 7. デプロイ

1.  ローカルからサーバーに SSH 接続
    cd "C:\Users\user\.ssh"
    ssh -i .\kagoya-login.key ubuntu@133.18.110.66

2.  サーバー上で git pull
    cd ~/apps/flare/FLARE_Dashboard/FLARE_Dashboard.git
    git pull

3.  起動中のコンテナに反映（本番専用起動コマンド）
    docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod up -d
