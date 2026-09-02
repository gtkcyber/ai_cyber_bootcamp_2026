from flask import Blueprint, Flask

from tutor.fallback import build_fallback_blueprint, setup_or_fallback


def test_fallback_blueprint_answers_503_json_on_any_get_route():
    app = Flask(__name__)
    app.register_blueprint(build_fallback_blueprint("index not found"), url_prefix="/api/tutor")
    client = app.test_client()

    resp = client.get("/api/tutor/scopes")
    assert resp.status_code == 503
    assert resp.get_json() == {"message": "The tutor is unavailable: index not found"}


def test_fallback_blueprint_answers_503_on_post_and_delete_too():
    app = Flask(__name__)
    app.register_blueprint(build_fallback_blueprint("boom"), url_prefix="/api/tutor")
    client = app.test_client()

    assert client.post("/api/tutor/chat", json={}).status_code == 503
    assert client.delete("/api/tutor/conversations/abc123abc123").status_code == 503
    assert client.get("/api/tutor/").status_code == 503


def test_setup_or_fallback_returns_the_real_blueprint_on_success():
    real = Blueprint("tutor", __name__)

    @real.route("/me")
    def me():
        return {"user": "x"}

    result = setup_or_fallback(lambda: real)
    assert result is real


def test_setup_or_fallback_falls_back_and_logs_on_any_exception(caplog):
    def _boom():
        raise RuntimeError("index not found at /Volumes/x/tutor/index")

    with caplog.at_level("ERROR", logger="tutor.fallback"):
        bp = setup_or_fallback(_boom)

    assert "tutor setup failed" in caplog.text

    app = Flask(__name__)
    app.register_blueprint(bp, url_prefix="/api/tutor")
    resp = app.test_client().get("/api/tutor/scopes")
    assert resp.status_code == 503
    assert "index not found at /Volumes/x/tutor/index" in resp.get_json()["message"]
