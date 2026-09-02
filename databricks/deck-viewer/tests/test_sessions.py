import json

from tutor.files import LocalFiles
from tutor.sessions import SessionStore, user_slug


def test_user_slug_lowercases_and_replaces_unsafe_chars():
    assert user_slug("Curtis.W@Example.com") == "curtis.w_example.com"


def test_create_then_get_round_trips(tmp_path):
    store = SessionStore(LocalFiles(tmp_path), "/Volumes/c/s/v/tutor_state")
    conv = store.create("student@example.com", "course")
    assert store.get("student@example.com", conv["id"]) == conv
    assert conv["messages"] == []


def test_list_is_newest_first(tmp_path, monkeypatch):
    store = SessionStore(LocalFiles(tmp_path), "/state")
    ticks = iter(["2026-01-01T00:00:00+00:00", "2026-01-02T00:00:00+00:00"])
    monkeypatch.setattr("tutor.sessions._now_iso", lambda: next(ticks))
    older = store.create("s@example.com", "course")
    newer = store.create("s@example.com", "course")
    listing = store.list("s@example.com")
    assert [c["id"] for c in listing] == [newer["id"], older["id"]]
    assert set(listing[0]) == {"id", "title", "scope", "updated"}


def test_append_adds_user_and_assistant_turns_and_sets_title(tmp_path):
    store = SessionStore(LocalFiles(tmp_path), "/state")
    conv = store.create("s@example.com", "course")
    question = "  What   is   PageRank?  " + ("x" * 80)
    citations = [{"id": "slide:06-x:1"}]
    updated = store.append("s@example.com", conv["id"], question, "It is a centrality measure.", citations)
    assert len(updated["messages"]) == 2
    user_turn, assistant_turn = updated["messages"]
    assert user_turn["role"] == "user"
    assert user_turn["content"] == question
    assert user_turn["citations"] == []
    assert assistant_turn["role"] == "assistant"
    assert assistant_turn["content"] == "It is a centrality measure."
    assert assistant_turn["citations"] == citations
    assert len(updated["title"]) <= 60
    assert updated["title"] == " ".join(question.split())[:60]
    assert updated["updated"] >= updated["created"]
    # persisted, not just returned
    assert store.get("s@example.com", conv["id"]) == updated


def test_second_append_does_not_overwrite_title(tmp_path):
    store = SessionStore(LocalFiles(tmp_path), "/state")
    conv = store.create("s@example.com", "course")
    store.append("s@example.com", conv["id"], "first question", "answer one", [])
    updated = store.append("s@example.com", conv["id"], "second question", "answer two", [])
    assert updated["title"] == "first question"
    assert len(updated["messages"]) == 4


def test_get_of_another_users_conversation_is_none(tmp_path):
    store = SessionStore(LocalFiles(tmp_path), "/state")
    conv = store.create("owner@example.com", "course")
    assert store.get("intruder@example.com", conv["id"]) is None


def test_delete_then_get_is_none(tmp_path):
    store = SessionStore(LocalFiles(tmp_path), "/state")
    conv = store.create("s@example.com", "course")
    store.delete("s@example.com", conv["id"])
    assert store.get("s@example.com", conv["id"]) is None


def test_list_for_user_with_no_directory_is_empty(tmp_path):
    store = SessionStore(LocalFiles(tmp_path), "/state")
    assert store.list("nobody@example.com") == []


def test_get_rejects_a_conv_id_that_is_a_path_traversal(tmp_path):
    store = SessionStore(LocalFiles(tmp_path), "/state")
    victim = store.create("victim@example.com", "course")
    # the attacker's own directory must already exist for the OS to resolve
    # the ".." at all -- reproduces the real scenario, where the attacker is
    # a registered user who has already asked the tutor a question.
    store.create("attacker@example.com", "course")
    traversal_id = f"../{user_slug('victim@example.com')}/{victim['id']}"
    assert store.get("attacker@example.com", traversal_id) is None


def test_get_rejects_a_conv_id_that_is_not_twelve_hex_chars(tmp_path):
    store = SessionStore(LocalFiles(tmp_path), "/state")
    store.create("s@example.com", "course")
    assert store.get("s@example.com", "not-a-real-id") is None
    assert store.get("s@example.com", "abc") is None
    assert store.get("s@example.com", "ABCDEF012345") is None  # uppercase hex is not the shape create() produces


def test_delete_with_a_path_traversal_conv_id_does_not_touch_another_users_file(tmp_path):
    store = SessionStore(LocalFiles(tmp_path), "/state")
    victim = store.create("victim@example.com", "course")
    store.create("attacker@example.com", "course")
    traversal_id = f"../{user_slug('victim@example.com')}/{victim['id']}"
    store.delete("attacker@example.com", traversal_id)  # must not raise
    assert store.get("victim@example.com", victim["id"]) == victim


def test_delete_with_an_invalid_conv_id_is_a_harmless_noop(tmp_path):
    store = SessionStore(LocalFiles(tmp_path), "/state")
    store.delete("s@example.com", "../../etc/passwd")  # must not raise


def test_list_skips_corrupt_json_file(tmp_path):
    store = SessionStore(LocalFiles(tmp_path), "/state")
    good = store.create("s@example.com", "course")
    LocalFiles(tmp_path).write(f"/state/{user_slug('s@example.com')}/broken.json", b"{not valid json")
    listing = store.list("s@example.com")
    assert [c["id"] for c in listing] == [good["id"]]


def test_list_skips_a_conversation_file_missing_a_required_key(tmp_path):
    store = SessionStore(LocalFiles(tmp_path), "/state")
    good = store.create("s@example.com", "course")
    LocalFiles(tmp_path).write(
        f"/state/{user_slug('s@example.com')}/deadbeefcafe.json",
        json.dumps({"id": "deadbeefcafe", "scope": "course"}).encode(),  # missing title/updated
    )
    listing = store.list("s@example.com")
    assert [c["id"] for c in listing] == [good["id"]]


def test_get_of_corrupt_json_file_is_none_and_logged(tmp_path, caplog):
    store = SessionStore(LocalFiles(tmp_path), "/state")
    # a validly-shaped id so the read is attempted at all (id validation is
    # a separate concern, covered by the path-traversal tests below).
    conv_id = "0123456789ab"
    LocalFiles(tmp_path).write(f"/state/{user_slug('s@example.com')}/{conv_id}.json", b"{not valid json")
    with caplog.at_level("WARNING", logger="tutor.sessions"):
        assert store.get("s@example.com", conv_id) is None
    assert conv_id in caplog.text
