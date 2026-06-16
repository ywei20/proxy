from app.utils.json_extract import extract_json_payload


def test_extracts_plain_json_object() -> None:
    assert extract_json_payload('{"answer":"ok"}') == {"answer": "ok"}


def test_extracts_json_from_markdown_fence() -> None:
    assert extract_json_payload('```json\n{"answer":"ok"}\n```') == {"answer": "ok"}


def test_extracts_first_embedded_json_payload() -> None:
    assert extract_json_payload('before {"answer":"ok"} after') == {"answer": "ok"}


def test_returns_original_when_no_json_exists() -> None:
    assert extract_json_payload("plain text") == "plain text"
