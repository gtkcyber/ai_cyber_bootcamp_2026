import json
import sys
from pathlib import Path

from flask import Flask

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from tutor.files import LocalFiles  # noqa: E402
from tutor.llm import Answer  # noqa: E402
from tutor.routes import make_blueprint  # noqa: E402
from tutor.sessions import SessionStore  # noqa: E402
from tutor.skills import CourseMaterial, SkillLibrary  # noqa: E402
from tutor.throttle import Throttle  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"
HOST = "https://example.cloud.databricks.com"
LABS = "/Workspace/Users/curtis@gtkcyber.com/ai-cyber-bootcamp/notebooks"
DECK = "04-supervised-machine-learning"


class FakeTutor:
    def __init__(self, answer=None, error=None):
        self._answer = answer or Answer(text="Because the classes are imbalanced.",
                                        sources=[{"kind": "skill", "name": "ds-evaluate"}],
                                        usage={"prompt_tokens": 4000, "completion_tokens": 90,
                                               "turns": 2},
                                        tool_calls=["load_skill:ds-evaluate"])
        self._error = error
        self.messages = None
        self.toolbox = type("Box", (), {"sources": []})()

    def answer(self, messages):
        self.messages = messages
        if self._error:
            raise self._error
        return self._answer


def build(tmp_path, tutor=None, throttle=None, lab_exists=lambda p: False):
    app = Flask(__name__)
    library = SkillLibrary.load(LocalFiles(FIXTURES), "/skills")
    material = CourseMaterial(files=LocalFiles(FIXTURES), labs_path="/labs",
                              answers_path="/answers", decks_path="/decks",
                              deck_files=LocalFiles(FIXTURES))
    store = SessionStore(LocalFiles(tmp_path), "/state")
    app.register_blueprint(
        make_blueprint(library, material, tutor or FakeTutor(), store,
                       throttle or Throttle(), dev_user="dev@example.com",
                       workspace_host=HOST, labs_shared=LABS,
                       home_labs_dir="AI Cyber Bootcamp 2026", lab_exists=lab_exists),
        url_prefix="/api/tutor")
    return app.test_client(), store


def frames(response):
    out = {}
    for block in response.get_data(as_text=True).split("\n\n"):
        if not block.strip():
            continue
        event = data = None
        for line in block.splitlines():
            if line.startswith("event:"):
                event = line[6:].strip()
            elif line.startswith("data:"):
                data = json.loads(line[5:].strip())
        out.setdefault(event, []).append(data)
    return out


def chat(client, **body):
    body.setdefault("deck", DECK)
    body.setdefault("slide", 2)
    body.setdefault("message", "which metric?")
    return client.post("/api/tutor/chat", json=body)


# --- identity and conversations -----------------------------------------

def test_me_falls_back_to_the_dev_user(tmp_path):
    client, _ = build(tmp_path)
    assert client.get("/api/tutor/me").get_json() == {"user": "dev@example.com"}


def test_me_prefers_the_forwarded_email(tmp_path):
    client, _ = build(tmp_path)
    got = client.get("/api/tutor/me", headers={"X-Forwarded-Email": "s@x.com"}).get_json()
    assert got == {"user": "s@x.com"}


def test_scopes_and_slide_routes_are_gone(tmp_path):
    client, _ = build(tmp_path)
    assert client.get("/api/tutor/scopes").status_code == 404
    assert client.get("/api/tutor/slide?deck_id=x&h=0&v=0").status_code == 404


def test_a_conversation_is_created_and_listed(tmp_path):
    client, _ = build(tmp_path)
    created = client.post("/api/tutor/conversations", json={"scope": DECK}).get_json()
    assert client.get("/api/tutor/conversations").get_json()[0]["id"] == created["id"]


def test_a_conversation_is_readable_and_deletable(tmp_path):
    client, _ = build(tmp_path)
    conv = client.post("/api/tutor/conversations", json={"scope": DECK}).get_json()
    assert client.get(f"/api/tutor/conversations/{conv['id']}").status_code == 200
    assert client.delete(f"/api/tutor/conversations/{conv['id']}").status_code == 204
    assert client.get(f"/api/tutor/conversations/{conv['id']}").status_code == 404


def test_one_user_cannot_read_another_users_conversation(tmp_path):
    client, _ = build(tmp_path)
    mine = client.post("/api/tutor/conversations", json={"scope": DECK},
                       headers={"X-Forwarded-Email": "a@x.com"}).get_json()
    other = client.get(f"/api/tutor/conversations/{mine['id']}",
                       headers={"X-Forwarded-Email": "b@x.com"})
    assert other.status_code == 404


# --- chat ----------------------------------------------------------------

def test_chat_streams_meta_token_sources_and_done(tmp_path):
    client, _ = build(tmp_path)
    got = frames(chat(client))
    assert list(got) == ["meta", "token", "sources", "done"]
    assert got["token"][0]["text"] == "Because the classes are imbalanced."
    assert got["sources"][0] == [{"kind": "skill", "name": "ds-evaluate"}]


def test_chat_passes_the_open_deck_and_slide_into_the_prompt(tmp_path):
    tutor = FakeTutor()
    client, _ = build(tmp_path, tutor=tutor)
    frames(chat(client))  # the answer only happens when the stream is read
    user_block = tutor.messages[-1]["content"]
    assert DECK in user_block
    assert "slide 2" in user_block.lower()
    # The pinned slide's own note leads, before the whole deck's notes.
    pinned = user_block.split("Speaker notes for the whole open deck")[0]
    assert "split that leaks" in pinned


def test_chat_puts_the_skill_index_in_the_system_message(tmp_path):
    tutor = FakeTutor()
    client, _ = build(tmp_path, tutor=tutor)
    frames(chat(client))  # the answer only happens when the stream is read
    assert "ds-evaluate" in tutor.messages[0]["content"]


def test_chat_with_no_deck_open_still_answers(tmp_path):
    client, _ = build(tmp_path)
    got = frames(chat(client, deck=None, slide=None))
    assert got["done"]


def test_chat_with_an_unknown_deck_answers_without_notes(tmp_path):
    """A deck the volume does not have must not 500 the question."""
    tutor = FakeTutor()
    client, _ = build(tmp_path, tutor=tutor)
    got = frames(chat(client, deck="99-nope"))
    assert got["done"]
    assert "Speaker notes" not in tutor.messages[-1]["content"]


def test_chat_persists_the_exchange(tmp_path):
    client, store = build(tmp_path)
    conv_id = frames(chat(client))["meta"][0]["conversation_id"]
    conv = store.get("dev@example.com", conv_id)
    assert [m["role"] for m in conv["messages"]] == ["user", "assistant"]
    assert conv["messages"][0]["content"] == "which metric?"
    assert conv["scope"] == DECK


def test_chat_continues_an_existing_conversation(tmp_path):
    client, store = build(tmp_path)
    first = frames(chat(client))["meta"][0]["conversation_id"]
    second = frames(chat(client, conversation_id=first))["meta"][0]["conversation_id"]
    assert second == first
    assert len(store.get("dev@example.com", first)["messages"]) == 4


def test_chat_rejects_a_conversation_id_with_a_slash(tmp_path):
    client, _ = build(tmp_path)
    assert chat(client, conversation_id="../victim/abc").status_code == 404


def test_chat_rejects_an_unknown_conversation_id(tmp_path):
    client, _ = build(tmp_path)
    assert chat(client, conversation_id="a" * 12).status_code == 404


def test_an_empty_message_is_refused(tmp_path):
    client, _ = build(tmp_path)
    assert chat(client, message="   ").status_code == 400


def test_a_tutor_failure_becomes_an_error_frame_not_a_500(tmp_path):
    client, _ = build(tmp_path, tutor=FakeTutor(error=RuntimeError("endpoint down")))
    got = frames(chat(client))
    assert "error" in got and "done" not in got
    assert "endpoint down" not in json.dumps(got)  # no internals leak to the student


def test_a_second_question_does_not_inherit_the_first_questions_sources(tmp_path):
    tutor = FakeTutor()
    client, _ = build(tmp_path, tutor=tutor)
    tutor.toolbox.sources.append({"kind": "skill", "name": "stale"})
    frames(chat(client))
    assert tutor.toolbox.sources == []


def test_the_throttle_window_returns_429(tmp_path):
    client, _ = build(tmp_path, throttle=Throttle(per_user=1, window_s=600))
    assert chat(client).status_code == 200
    assert chat(client).status_code == 429


def test_the_concurrency_cap_returns_503(tmp_path):
    throttle = Throttle(per_user=99, concurrent=1)
    client, _ = build(tmp_path, throttle=throttle)
    with throttle.acquire("someone-else"):
        assert chat(client).status_code == 503


def test_a_permit_is_released_after_a_successful_answer(tmp_path):
    throttle = Throttle(per_user=99, concurrent=1)
    client, _ = build(tmp_path, throttle=throttle)
    chat(client)
    with throttle.acquire("anyone"):
        pass  # would raise Busy if the permit had leaked


def test_a_permit_is_released_after_a_tutor_failure(tmp_path):
    throttle = Throttle(per_user=99, concurrent=1)
    client, _ = build(tmp_path, tutor=FakeTutor(error=RuntimeError("boom")), throttle=throttle)
    chat(client)
    with throttle.acquire("anyone"):
        pass


# --- lab links -----------------------------------------------------------

def test_lab_link_falls_back_to_the_shared_copy(tmp_path):
    client, _ = build(tmp_path)
    url = client.get("/api/tutor/lab-link?notebook=Worksheet_4.2_Tuning_Your_Classifier.ipynb").get_json()["url"]
    assert url.startswith(f"{HOST}/#workspace{LABS}/")


def test_lab_link_prefers_the_students_own_copy(tmp_path):
    client, _ = build(tmp_path, lab_exists=lambda p: p.startswith("/Workspace/Users/dev@example.com/"))
    url = client.get("/api/tutor/lab-link?notebook=Worksheet_4.2_Tuning_Your_Classifier.ipynb").get_json()["url"]
    assert "/Workspace/Users/dev@example.com/AI%20Cyber%20Bootcamp%202026/" in url


def test_lab_link_refuses_a_traversal(tmp_path):
    client, _ = build(tmp_path)
    assert client.get("/api/tutor/lab-link?notebook=../../etc/passwd").status_code == 400
