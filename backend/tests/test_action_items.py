def test_create_complete_list_and_patch_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["completed"] is False
    assert "created_at" in item and "updated_at" in item

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()
    assert done["completed"] is True

    r = client.get("/action-items/", params={"completed": True, "limit": 5, "sort": "-created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.patch(f"/action-items/{item['id']}", json={"description": "Updated"})
    assert r.status_code == 200
    patched = r.json()
    assert patched["description"] == "Updated"


def test_create_action_item_validation_error(client):
    r = client.post("/action-items/", json={"description": ""})
    assert r.status_code == 422


def test_patch_action_item_requires_a_field(client):
    r = client.post("/action-items/", json={"description": "Ship it"})
    item_id = r.json()["id"]

    r = client.patch(f"/action-items/{item_id}", json={})
    assert r.status_code == 400


def test_patch_action_item_not_found(client):
    r = client.patch("/action-items/999999", json={"description": "Updated"})
    assert r.status_code == 404


def test_get_and_delete_action_item(client):
    r = client.post("/action-items/", json={"description": "Ship it"})
    item_id = r.json()["id"]

    r = client.get(f"/action-items/{item_id}")
    assert r.status_code == 200
    assert r.json()["id"] == item_id

    r = client.delete(f"/action-items/{item_id}")
    assert r.status_code == 204

    r = client.get(f"/action-items/{item_id}")
    assert r.status_code == 404

    r = client.delete(f"/action-items/{item_id}")
    assert r.status_code == 404


def test_list_action_items_rejects_invalid_sort_field(client):
    r = client.get("/action-items/", params={"sort": "not_a_real_field"})
    assert r.status_code == 400

    r = client.get("/action-items/", params={"sort": "-completed"})
    assert r.status_code == 200


