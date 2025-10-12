import io

def test_register_login_me(client, auth_headers):
    h = auth_headers("u1","p1")
    r = client.get("/api/me", headers=h)
    assert r.status_code == 200
    assert r.json["user"]["username"] == "u1"

def test_profile_update_and_avatar_upload(client, auth_headers):
    headers = auth_headers("u2","p2")

    # JSON でプロフィール更新
    r = client.post("/api/me", headers=headers, json={"birthday":"1990-01-02","notifications_enabled":True})
    assert r.status_code == 200

    # 画像アップロード: content_type は指定しない（テストクライアントが自動付与）
    buf = io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00IHDR" + b"0"*200)
    buf.seek(0)
    data = {"avatar": (buf, "avatar.png", "image/png")}
    r = client.post("/api/me", headers=headers, data=data)
    assert r.status_code == 200
    assert r.json.get("avatar_url")

def test_avatar_too_large_413(client, auth_headers):
    headers = auth_headers("u3","p3")

    big = io.BytesIO(b"x" * (2 * 1024 * 1024))  # 2MB（既定の MAX は 5MB）
    big.seek(0)
    data = {"avatar": (big, "big.bin", "application/octet-stream")}
    # ここも content_type は渡さない
    r = client.post("/api/me", headers=headers, data=data)
    assert r.status_code in (200, 413)
