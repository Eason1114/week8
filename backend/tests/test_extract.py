from backend.app.services.extract import extract_action_items, extract_action_items_detailed


def test_extract_action_items():
    text = """
    This is a note
    - TODO: write tests
    - ACTION: review PR
    - Ship it!
    Not actionable
    """.strip()
    items = extract_action_items(text)
    assert "TODO: write tests" in items
    assert "ACTION: review PR" in items
    assert "Ship it!" in items
    assert not any("Not actionable" in item for item in items)


def test_extract_recognizes_fixme_and_followup_keywords():
    text = """
    FIXME: broken build
    Follow-up: circle back with design
    followup email design team
    """.strip()
    items = extract_action_items(text)
    assert "FIXME: broken build" in items
    assert "Follow-up: circle back with design" in items
    assert "followup email design team" in items


def test_extract_recognizes_markdown_checkboxes():
    text = """
    - [ ] Buy milk
    - [x] Already done, should not appear
    * [ ] Call the vet
    """.strip()
    items = extract_action_items(text)
    assert "Buy milk" in items
    assert "Call the vet" in items
    assert not any("Already done" in item for item in items)


def test_extract_is_case_insensitive_on_keywords():
    text = "todo: lowercase should still match"
    assert extract_action_items(text) == ["todo: lowercase should still match"]


def test_extract_dedupes_repeated_lines():
    text = """
    TODO: write tests
    TODO: write tests
    """.strip()
    assert extract_action_items(text) == ["TODO: write tests"]


def test_extract_ignores_plain_lines_without_signal():
    text = """
    Just a regular sentence.
    Another regular sentence without punctuation
    """.strip()
    assert extract_action_items(text) == []


def test_extract_action_items_detailed_reports_metadata():
    text = "TODO: write tests\nShip it!\n- [ ] Buy milk\n- [x] done already"
    detailed = extract_action_items_detailed(text)

    by_text = {item.text: item for item in detailed}
    assert by_text["TODO: write tests"].keyword == "todo"
    assert by_text["Ship it!"].urgent is True
    assert by_text["Buy milk"].keyword is None
    assert "done already" not in by_text
