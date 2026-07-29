def test_create_list_get_delete_tag(client):
    r = client.post("/tags/", json={"name": "work"})
    assert r.status_code == 201, r.text
    tag = r.json()
    assert tag["name"] == "work"

    r = client.get("/tags/")
    assert r.status_code == 200
    assert any(t["name"] == "work" for t in r.json())

    r = client.get(f"/tags/{tag['id']}")
    assert r.status_code == 200
    assert r.json()["name"] == "work"

    r = client.delete(f"/tags/{tag['id']}")
    assert r.status_code == 204

    r = client.get(f"/tags/{tag['id']}")
    assert r.status_code == 404


def test_create_tag_rejects_duplicate_name(client):
    r = client.post("/tags/", json={"name": "dup"})
    assert r.status_code == 201

    r = client.post("/tags/", json={"name": "dup"})
    assert r.status_code == 409


def test_create_tag_rejects_empty_name(client):
    r = client.post("/tags/", json={"name": ""})
    assert r.status_code == 422


def test_get_and_delete_missing_tag(client):
    r = client.get("/tags/999999")
    assert r.status_code == 404

    r = client.delete("/tags/999999")
    assert r.status_code == 404


def test_attach_and_detach_tag_to_note(client):
    note = client.post("/notes/", json={"title": "N", "content": "C"}).json()
    tag = client.post("/tags/", json={"name": "important"}).json()

    r = client.post(f"/tags/{tag['id']}/notes/{note['id']}")
    assert r.status_code == 200

    r = client.get(f"/notes/{note['id']}")
    assert r.status_code == 200
    tag_names = [t["name"] for t in r.json()["tags"]]
    assert "important" in tag_names

    # Attaching twice is idempotent, not an error.
    r = client.post(f"/tags/{tag['id']}/notes/{note['id']}")
    assert r.status_code == 200

    r = client.delete(f"/tags/{tag['id']}/notes/{note['id']}")
    assert r.status_code == 200

    r = client.get(f"/notes/{note['id']}")
    assert r.json()["tags"] == []


def test_attach_tag_to_note_missing_ids(client):
    note = client.post("/notes/", json={"title": "N", "content": "C"}).json()
    tag = client.post("/tags/", json={"name": "x"}).json()

    r = client.post(f"/tags/999999/notes/{note['id']}")
    assert r.status_code == 404

    r = client.post(f"/tags/{tag['id']}/notes/999999")
    assert r.status_code == 404


def test_list_notes_filtered_by_tag(client):
    note_a = client.post("/notes/", json={"title": "A", "content": "C"}).json()
    note_b = client.post("/notes/", json={"title": "B", "content": "C"}).json()
    tag = client.post("/tags/", json={"name": "filter-me"}).json()
    client.post(f"/tags/{tag['id']}/notes/{note_a['id']}")

    r = client.get("/notes/", params={"tag": "filter-me"})
    assert r.status_code == 200
    ids = [n["id"] for n in r.json()]
    assert note_a["id"] in ids
    assert note_b["id"] not in ids
