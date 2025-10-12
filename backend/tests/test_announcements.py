def test_announcement_crud_and_permission(client, auth_headers):
    h1 = auth_headers("owner","pw")
    h2 = auth_headers("other","pw")

    r = client.post("/api/announcements", headers=h1, json={"text":"hello"})
    assert r.status_code == 200
    ann_id = r.json["id"]

    r = client.get("/api/announcements", headers=h1)
    assert r.status_code == 200
    assert any(i["id"] == ann_id for i in r.json["items"])

    r = client.delete(f"/api/announcements/{ann_id}", headers=h2); assert r.status_code == 403
    r = client.delete(f"/api/announcements/{ann_id}", headers=h1); assert r.status_code == 200
