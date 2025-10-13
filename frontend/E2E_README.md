# E2E Patch v2 (UIモードの見え方改善 & ルーティング修正)

## ルーティング修正点
- マイページ: `/mypage` → **`/profile`**
- お知らせ: `/news` → **`/announcements`**

## UIモードでテストが1個だけに見える理由
- Playwright UI は **選択中のプロジェクト**だけをリスト表示します。
- 先頭プロジェクトが `setup` だと、UI 初期表示は **setup（1件）** のみになります。  
  → 本パッチでは **`chromium` を先頭**にし、UI で最初からメインのテストが見えるようにしました。
- さらに、`package.json` に以下のスクリプトを追加：
  - `e2e:ui` : `chromium` と `auth-flow` を UI に読み込み
  - `e2e:ui:all` : `setup` も含めた全プロジェクトを UI に読み込み
  - `e2e:login` : セッション作成だけ先に実行（UI起動前の下準備に）

## 実行例
```bash
docker compose up -d   # http://localhost:8080

cd frontend
npm i
npx playwright install

# まずログイン状態を作っておく（UI起動前に一度だけ）
npm run e2e:login

# UIモード（メインのテストのみ表示）
npm run e2e:ui

# すべてのプロジェクトをUIに表示したい場合
npm run e2e:ui:all
```
