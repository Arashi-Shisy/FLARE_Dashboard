def test_chat_post_list_delete_permission(client, auth_headers):
    h1 = auth_headers("talker","pw"); h2 = auth_headers("other","pw")
    r = client.post("/api/chat", headers=h1, json={"content":"hello"}); assert r.status_code == 200
    mid = r.json["id"]
    r = client.get("/api/chat", headers=h1); assert any(i["id"] == mid for i in r.json["items"])
    assert client.delete(f"/api/chat/{mid}", headers=h2).status_code == 403
    assert client.delete(f"/api/chat/{mid}", headers=h1).status_code == 200
