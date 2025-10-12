from datetime import datetime, timedelta

def iso(dt): return dt.strftime("%Y-%m-%dT%H:%M:%S") + "Z"

def test_event_create_get_list_attend_attendees(client, auth_headers):
    h_creator = auth_headers("creator","pw")
    start = datetime.utcnow() + timedelta(days=1)
    end = start + timedelta(hours=2)
    r = client.post("/api/events", headers=h_creator, json={
        "name":"FLARE Meetup","start_at":iso(start),"end_at":iso(end),
        "description":"desc","location":"online","url":"https://ex"
    })
    assert r.status_code == 200
    eid = r.json["id"]

    r = client.get(f"/api/events/{eid}", headers=h_creator); assert r.status_code == 200
    assert r.json["event"]["attendee_count"] == 1  # creator auto-join

    h_user = auth_headers("bob","pw")
    r = client.post(f"/api/events/{eid}/attend", headers=h_user); assert r.json["going"] is True
    r = client.get(f"/api/events/{eid}/attendees", headers=h_creator); assert r.json["count"] == 2
    r = client.post(f"/api/events/{eid}/attend", headers=h_user); assert r.json["going"] is False
    r = client.get(f"/api/events/{eid}/attendees", headers=h_creator); assert r.json["count"] == 1

def test_event_update_and_delete_permission(client, auth_headers):
    h1 = auth_headers("alice","pw"); h2 = auth_headers("eve","pw")
    start = datetime.utcnow() + timedelta(days=2); end = start + timedelta(hours=1)
    r = client.post("/api/events", headers=h1, json={"name":"X","start_at":iso(start),"end_at":iso(end)}); eid = r.json["id"]
    assert client.put(f"/api/events/{eid}", headers=h2, json={"name":"Y"}).status_code == 403
    assert client.delete(f"/api/events/{eid}", headers=h2).status_code == 403
    assert client.put(f"/api/events/{eid}", headers=h1, json={"name":"Y"}).status_code == 200
    assert client.delete(f"/api/events/{eid}", headers=h1).status_code == 200
