# FLARE Dashboard

スマホ前提・シンプル操作のコミュニティ可視化Webアプリ。  
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
- マイページ（プロフィール画像、生年月日、ブラウザ通知ON/OFF）
- ダッシュボード（**今週のイベント**・**最新お知らせ 5件**）
- イベント一覧/詳細/登録/編集/削除、**ワンタッチ参加表明（トグル）**
- お知らせ登録/一覧/削除（作成者のみ削除可）
- コミュニティチャット（新しい順、投稿者は削除可）
- ブラウザ通知（テスト送信、新規イベント/お知らせ、参加イベントの**24時間前/1時間前**リマインド）
  - 仕様：タブを開いている間は、**Service Worker**経由でネイティブ通知します
  - Web Push（タブ非表示時のサーバープッシュ）は未実装（拡張余地あり）

## 3. デザイン
- 背景：`#262626`
- 強調色（FLARE色）：`#db1280 → #c11e1e → #ed9515` のグラデーション
- チャット画面：Instagram DM風（FLARE色適用）

## 4. 開発メモ
- 永続化: SQLiteは `backend_data` ボリューム。画像は `uploads` ボリューム。
- セッション有効期限：**31日**（1ヶ月以上アクセスがない場合に切れる設計）
- 再起動時のリマインド再登録：将来日付のイベントを読み直してAPSchedulerに再登録します。

## 5. 既知の注意
- ブラウザ通知はタブが完全に閉じている状態では届きません（Web Push拡張が必要）。
- 本番運用時は `SECRET_KEY` を必ず変更し、HTTPSとCookie設定を強化してください。
