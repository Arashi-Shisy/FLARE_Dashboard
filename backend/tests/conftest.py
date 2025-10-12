# backend/tests/conftest.py
import os
import sys
import shutil
import pathlib
import pytest

BACKEND_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# テスト既定環境
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("UPLOAD_DIR", str(BACKEND_DIR / "tmp_test_uploads"))
os.environ.setdefault("DISABLE_SCHEDULER", "1")
os.environ.setdefault("SOCKETIO_ASYNC_MODE", "threading")

@pytest.fixture(scope="function", autouse=True)
def _reset_fs():
    up = pathlib.Path(os.environ["UPLOAD_DIR"])
    up.mkdir(parents=True, exist_ok=True)
    yield
    shutil.rmtree(up, ignore_errors=True)

@pytest.fixture(scope="function")
def app_instance():
    from app import app, db, init_db
    with app.app_context():
        db.drop_all()
        db.create_all()
        init_db()
    yield app

@pytest.fixture(scope="function")
def client(app_instance):
    # Cookie Jar を無効化して、毎回ヘッダで Cookie を明示的に切り替える
    return app_instance.test_client(use_cookies=False)

def iso(dt):
    return dt.replace(microsecond=0).isoformat() + "Z"

@pytest.fixture
def auth_headers(client):
    def _login(username="alice", password="pass1234"):
        # 明示的に毎回新しいセッションCookieを取り直す
        client.post("/api/logout")
        r = client.post("/api/register", json={"username": username, "password": password})
        if r.status_code == 400:
            r = client.post("/api/login", json={"username": username, "password": password})
        assert r.status_code == 200
        cookie = r.headers.get("Set-Cookie")
        assert cookie, "Set-Cookie が取得できませんでした"
        return {"Cookie": cookie}
    return _login
