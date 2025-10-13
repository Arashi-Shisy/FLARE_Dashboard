# E2E Patch (Playwright) - Login Setup + Split Specs

## 使い方
1. プロジェクト直下にこの ZIP を展開し、`frontend/` の差分を反映
2. アプリ起動（http://localhost:8080）
   ```bash
   docker compose up -d
   ```
3. 依存インストール & Playwright セットアップ
   ```bash
   cd frontend
   npm i
   npx playwright install
   ```
4. 実行
   ```bash
   npm run e2e           # ヘッドレス
   npm run e2e:headed    # ヘッドあり
   npm run e2e:ui        # UI モード
   ```

## ログインセットアップの仕組み
- `projects.setup` が最初に `e2e/setup/auth.setup.e2e.js` を実行し、
  - 新規ユーザーを登録
  - `e2e/.auth/user.json` に storageState を保存
- 以降のシナリオ（Chromium プロジェクト）はこの storageState を再利用して **常にログイン済み** で開始します。
- 例外として `01_auth_flow.e2e.spec.js` は **未ログイン前提のリダイレクト/登録フロー** を確認するために、
  - 別プロジェクト `auth-flow` として `storageState: undefined` で実行します。

## 備考
- 画面遷移は安定性のため一部で `page.goto('/path')` を用いています。
- 削除操作は confirm ダイアログが出るため、直前に `page.once('dialog', d => d.accept())` で承認しています。
