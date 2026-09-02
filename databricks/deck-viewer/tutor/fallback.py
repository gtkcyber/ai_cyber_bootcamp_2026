"""A stand-in tutor blueprint that answers 503 on every route.

app.py registers this in place of the real tutor blueprint when setting up
the tutor (loading the index, building the model client, opening the
session store) fails at startup. The tutor is an add-on to the slide viewer,
which is the course's primary deliverable: a tutor-side failure -- a
missing or mid-upload index, a grant not yet propagated, a bad endpoint
name -- must not take the whole app down with it. The failure stays loud
(logged here, and surfaced as the panel's error message) while the deck
routes keep serving.
"""
import logging

from flask import Blueprint, jsonify

logger = logging.getLogger(__name__)


def build_fallback_blueprint(reason: str) -> Blueprint:
    bp = Blueprint("tutor", __name__)
    message = f"The tutor is unavailable: {reason}"

    def _unavailable(*_args, **_kwargs):
        return jsonify({"message": message}), 503

    bp.add_url_rule("/", "unavailable_root", _unavailable, methods=["GET", "POST", "DELETE"])
    bp.add_url_rule("/<path:_ignored>", "unavailable", _unavailable, methods=["GET", "POST", "DELETE"])
    return bp


def setup_or_fallback(setup):
    """Run `setup` (a zero-arg callable returning a Blueprint). On any
    exception, log it and return a fallback blueprint answering 503 on every
    route instead -- so the caller always has something registerable."""
    try:
        return setup()
    except Exception as e:
        logger.exception("tutor setup failed; the deck viewer will keep serving decks without it")
        return build_fallback_blueprint(str(e))
