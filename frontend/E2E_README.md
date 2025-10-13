# E2E test (Playwright)

## 前提
- Docker で `docker compose up -d` を実行し、`http://localhost:8080` でアプリ（NGINX 経由で frontend+backend）が稼働していること。

## 使い方
```bash
cd frontend
npm i
npx playwright install
npm run e2e
```

- BASE_URL を変えたい場合：
```bash
BASE_URL=http://localhost:5173 npm run e2e
```

## テスト内容
- `/` にアクセスすると、未ログインのため `/login` にリダイレクトされる
- ログイン画面から「ユーザー登録」に移動し、ランダム生成のユーザー名+固定パスワードで登録
- 登録完了後、Dashboard（`/`）に遷移し、見出し「今週のイベント」「最新のお知らせ」の表示を確認
