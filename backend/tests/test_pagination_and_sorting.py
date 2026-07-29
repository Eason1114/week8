"""Coverage for pagination (`skip`/`limit`) and `sort` across list endpoints.

The existing tests only ever passed pagination/sort params without checking
that they actually affected ordering or which records came back. These tests
assert on actual order and on page boundaries instead.
"""


def _create_notes(client, titles):
    ids = []
    for title in titles:
        r = client.post("/notes/", json={"title": title, "content": f"content for {title}"})
        assert r.status_code == 201, r.text
        ids.append(r.json()["id"])
    return ids


def _create_items(client, descriptions):
    ids = []
    for description in descriptions:
        r = client.post("/action-items/", json={"description": description})
        assert r.status_code == 201, r.text
        ids.append(r.json()["id"])
    return ids


# ---- Notes: sorting ----------------------------------------------------


def test_notes_sort_by_title_ascending_and_descending(client):
    _create_notes(client, ["Charlie", "Alpha", "Bravo"])

    r = client.get("/notes/", params={"sort": "title", "limit": 200})
    ordered = [n["title"] for n in r.json() if n["title"] in {"Alpha", "Bravo", "Charlie"}]
    assert ordered == ["Alpha", "Bravo", "Charlie"]

    r = client.get("/notes/", params={"sort": "-title", "limit": 200})
    ordered = [n["title"] for n in r.json() if n["title"] in {"Alpha", "Bravo", "Charlie"}]
    assert ordered == ["Charlie", "Bravo", "Alpha"]


def test_notes_default_sort_is_newest_first(client):
    ids = _create_notes(client, ["Order-First", "Order-Second", "Order-Third"])

    r = client.get("/notes/", params={"limit": 200})
    returned_ids = [n["id"] for n in r.json() if n["id"] in ids]
    assert returned_ids == list(reversed(ids))


def test_notes_invalid_sort_field_falls_back_instead_of_erroring(client):
    r = client.get("/notes/", params={"sort": "this_is_not_a_column"})
    assert r.status_code == 200


# ---- Notes: pagination ---------------------------------------------------


def test_notes_pagination_pages_partition_the_filtered_result(client):
    _create_notes(client, [f"Paged-Note-{i}" for i in range(5)])
    limit = 2

    full = client.get("/notes/", params={"q": "Paged-Note-", "sort": "title", "limit": 200}).json()
    assert [n["title"] for n in full] == [f"Paged-Note-{i}" for i in range(5)]

    collected = []
    skip = 0
    while skip < len(full):
        page = client.get(
            "/notes/", params={"q": "Paged-Note-", "sort": "title", "limit": limit, "skip": skip}
        ).json()
        assert len(page) == min(limit, len(full) - skip)
        collected.extend(page)
        skip += limit

    assert [n["id"] for n in collected] == [n["id"] for n in full]
    assert len(collected) == len(full)


def test_notes_skip_beyond_result_count_returns_empty_list(client):
    _create_notes(client, ["Only-One-Match"])

    r = client.get("/notes/", params={"q": "Only-One-Match", "skip": 10})
    assert r.status_code == 200
    assert r.json() == []


def test_notes_limit_is_capped_at_200(client):
    r = client.get("/notes/", params={"limit": 201})
    assert r.status_code == 422


# ---- Action items: sorting ------------------------------------------------


def test_action_items_sort_by_id_matches_creation_order(client):
    ids = _create_items(client, ["First item", "Second item", "Third item"])

    r = client.get("/action-items/", params={"sort": "id", "limit": 200})
    returned_ids = [i["id"] for i in r.json() if i["id"] in ids]
    assert returned_ids == ids

    r = client.get("/action-items/", params={"sort": "-id", "limit": 200})
    returned_ids = [i["id"] for i in r.json() if i["id"] in ids]
    assert returned_ids == list(reversed(ids))


def test_action_items_completed_filter_combines_with_sort(client):
    ids = _create_items(client, ["Not done A", "Done B", "Not done C"])
    client.put(f"/action-items/{ids[1]}/complete")

    r = client.get("/action-items/", params={"completed": True, "sort": "-id", "limit": 200})
    descriptions = {i["description"] for i in r.json()}
    assert "Done B" in descriptions
    assert "Not done A" not in descriptions
    assert "Not done C" not in descriptions

    r = client.get("/action-items/", params={"completed": False, "sort": "-id", "limit": 200})
    descriptions = {i["description"] for i in r.json()}
    assert {"Not done A", "Not done C"} <= descriptions
    assert "Done B" not in descriptions


# ---- Action items: pagination ---------------------------------------------


def test_action_items_pagination_pages_partition_the_full_result(client):
    _create_items(client, [f"Paged item {i}" for i in range(7)])
    limit = 3

    full = client.get("/action-items/", params={"sort": "id", "limit": 200}).json()
    total = len(full)

    collected = []
    skip = 0
    while skip < total:
        page = client.get("/action-items/", params={"sort": "id", "limit": limit, "skip": skip}).json()
        assert len(page) == min(limit, total - skip)
        collected.extend(page)
        skip += limit

    assert [i["id"] for i in collected] == [i["id"] for i in full]


def test_action_items_limit_is_capped_at_200(client):
    r = client.get("/action-items/", params={"limit": 500})
    assert r.status_code == 422
