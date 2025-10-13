# Backend リファクタリング概要（日本語）

本バックエンドは Flask を **Blueprint** と **Application Factory** で再構成しています。  
既存の API URL やレスポンス仕様は維持しつつ、関心の分離と可読性を高めました。

## ディレクトリ構成
```text
backend/
  app.py                 # Flaskアプリの生成・Blueprint登録（既存互換: app, init_db を公開）
  extensions.py          # 共有インスタンス（db / socketio / scheduler）
  models.py              # SQLAlchemy モデル定義
  blueprints/
    auth.py              # 認証・プロフィール更新（/api/register, /api/login, /api/logout, /api/me）
    announcements.py     # お知らせ（/api/announcements）
    events.py            # イベント（/api/events 系, 参加トグルは going を返却）
    chat.py              # チャット（/api/chat 系）
    files.py             # 画像配信・アップロード（/api/avatar/*）
    misc.py              # ダッシュボード情報・ヘルスチェック（/api/home, /api/health）
  utils/
    common.py            # 日付変換・シリアライザ共通化
```

## 互換ポイント
- 既存のエンドポイント・URLは変更していません。
- `/api/me` は **JSON と multipart（avatar）** の両方を受け付けます（テスト互換のため）。
- イベント参加トグルは `{"going": true/false}` を返します。

## 環境変数
- `DATABASE_URL`（例: `sqlite:///flaredb.sqlite`）
- `SECRET_KEY`
- `MAX_UPLOAD_MB`（既定 5MB）
- `DISABLE_SCHEDULER=1` で APScheduler を無効化
