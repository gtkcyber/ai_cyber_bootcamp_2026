"""The tutor's HTTP surface: per-user conversations and one answered question.

Two routes the reference had are gone with the retrieval index: /scopes (there
are no scopes) and /slide (there is no chunk to look a slide up in). Everything
else -- identity, conversation CRUD, lab links, and the throttle's permit
discipline -- is the reference's, unchanged in behaviour.
"""
import json
import logging
import urllib.parse

from flask import Blueprint, Response, jsonify, request

from tutor.files import MissingFile
from tutor.identity import current_user
from tutor.prompt import build_messages
from tutor.sessions import CONV_ID_RE
from tutor.throttle import Busy, TooManyRequests

logger = logging.getLogger(__name__)

TOO_MANY_REQUESTS_MESSAGE = "You've asked a lot of questions in the last few minutes. Wait a bit and try again."
BUSY_MESSAGE = "The tutor is answering other questions right now. Try again in a moment."
UNKNOWN_CONVERSATION_MESSAGE = "That conversation was not found."
INVALID_NOTEBOOK_MESSAGE = "That notebook path is not valid."
EMPTY_QUESTION_MESSAGE = "Ask a question first."
ANSWER_ERROR_MESSAGE = "Something went wrong answering that. Ask again."
SETUP_ERROR_MESSAGE = "Something went wrong getting ready to answer that. Try again."
HISTORY_TURNS = 8


def _sse(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def make_blueprint(library, material, tutor, store, throttle, *, dev_user: str | None,
                   workspace_host: str, labs_shared: str, home_labs_dir: str,
                   lab_exists) -> Blueprint:
    bp = Blueprint("tutor", __name__)

    def _user() -> str:
        return current_user(request.headers, dev_user)

    @bp.route("/me", methods=["GET"])
    def me():
        return jsonify({"user": _user()})

    @bp.route("/conversations", methods=["GET"])
    def list_conversations():
        return jsonify(store.list(_user()))

    @bp.route("/conversations", methods=["POST"])
    def create_conversation():
        body = request.get_json(force=True, silent=True) or {}
        return jsonify(store.create(_user(), body.get("scope"))), 201

    @bp.route("/conversations/<conv_id>", methods=["GET"])
    def get_conversation(conv_id):
        conv = store.get(_user(), conv_id)
        if conv is None:
            return jsonify({"message": UNKNOWN_CONVERSATION_MESSAGE}), 404
        return jsonify(conv)

    @bp.route("/conversations/<conv_id>", methods=["DELETE"])
    def delete_conversation(conv_id):
        store.delete(_user(), conv_id)
        return "", 204

    @bp.route("/lab-link", methods=["GET"])
    def lab_link():
        notebook = request.args.get("notebook", "")
        if ".." in notebook.split("/"):
            return jsonify({"message": INVALID_NOTEBOOK_MESSAGE}), 400
        own = f"/Workspace/Users/{_user()}/{home_labs_dir}/{notebook}"
        path = own if lab_exists(own) else f"{labs_shared}/{notebook}"
        # "@" stays literal: it is a legal path character and the workspace UI
        # addresses a user folder by the email as written, not percent-encoded.
        return jsonify({"url": f"{workspace_host}/#workspace{urllib.parse.quote(path, safe='/@')}"})

    @bp.route("/chat", methods=["POST"])
    def chat():
        user = _user()
        body = request.get_json(force=True, silent=True) or {}
        conversation_id = body.get("conversation_id")
        deck = body.get("deck")
        slide = body.get("slide")
        question = (body.get("message") or "").strip()

        if not question:
            return jsonify({"message": EMPTY_QUESTION_MESSAGE}), 400

        throttle_cm = throttle.acquire(user)
        try:
            throttle_cm.__enter__()
        except TooManyRequests:
            return jsonify({"message": TOO_MANY_REQUESTS_MESSAGE}), 429
        except Busy:
            return jsonify({"message": BUSY_MESSAGE}), 503

        # One Toolbox lives for the life of the process, so its record of what
        # it served would otherwise accumulate across every question this
        # worker ever answers and each answer would cite the last one's sources.
        toolbox = getattr(tutor, "toolbox", None)
        if toolbox is not None:
            toolbox.sources.clear()

        released = False

        def release():
            nonlocal released
            if not released:
                released = True
                throttle_cm.__exit__(None, None, None)

        # Everything from here to the stream's start can raise and must still
        # release the permit it took above: a leaked permit locks every later
        # request in this process out with Busy.
        try:
            if conversation_id:
                # conversation_id arrives in a JSON body, where "/" is legal --
                # unlike the URL-path routes above, where Flask's converter will
                # not match one. SessionStore validates the same shape
                # independently; this is the belt on top of that suspender.
                if not isinstance(conversation_id, str) or not CONV_ID_RE.match(conversation_id):
                    release()
                    return jsonify({"message": UNKNOWN_CONVERSATION_MESSAGE}), 404
                conv = store.get(user, conversation_id)
                if conv is None:
                    release()
                    return jsonify({"message": UNKNOWN_CONVERSATION_MESSAGE}), 404
            else:
                conv = store.create(user, deck)

            deck_notes = pinned_note = None
            if deck:
                try:
                    deck_notes = material.render_deck_notes(deck)
                    if slide is not None:
                        pinned_note = material.note_for_slide(deck, int(slide))
                except (MissingFile, TypeError, ValueError):
                    # A deck the volume does not have, or a nonsense slide
                    # number, costs the question its grounding -- not the answer.
                    logger.warning("no notes for deck=%r slide=%r", deck, slide)

            messages = build_messages(
                question, index_entries=library.index(), deck=deck, slide=slide,
                deck_notes=deck_notes, pinned_note=pinned_note,
                history=conv["messages"][-HISTORY_TURNS:],
            )
        except Exception:
            release()
            logger.exception("tutor chat setup failed (user=%s)", user)
            return jsonify({"message": SETUP_ERROR_MESSAGE}), 500

        def gen():
            try:
                yield _sse("meta", {"conversation_id": conv["id"]})
                answer = tutor.answer(messages)
                logger.info("tutor answered user=%s deck=%s tools=%s usage=%s",
                            user, deck, answer.tool_calls, answer.usage)
                yield _sse("token", {"text": answer.text})
                yield _sse("sources", answer.sources)
                store.append(user, conv["id"], question, answer.text, answer.sources)
                yield _sse("done", {})
            except Exception:
                logger.exception("tutor answer failed (user=%s conversation=%s)", user, conv["id"])
                yield _sse("error", {"message": ANSWER_ERROR_MESSAGE})
            finally:
                release()

        resp = Response(gen(), mimetype="text/event-stream",
                        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
        # Belt on top of the generator's own finally: a generator handed to the
        # WSGI server and never advanced even once (the client disconnects before
        # the first read) has no suspended frame, so its close() runs no code.
        # call_on_close always fires; release's own flag makes a second call a
        # no-op.
        resp.call_on_close(release)
        return resp

    return bp
