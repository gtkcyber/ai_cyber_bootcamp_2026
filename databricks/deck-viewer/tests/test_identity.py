from werkzeug.datastructures import Headers

from tutor.identity import FORWARDED, current_user


def test_forwarded_constant_order():
    assert FORWARDED == ("X-Forwarded-Email", "X-Forwarded-Preferred-Username", "X-Forwarded-User")


def test_prefers_email_over_preferred_username_and_user():
    headers = Headers([
        ("X-Forwarded-User", "user-header"),
        ("X-Forwarded-Preferred-Username", "preferred-header"),
        ("X-Forwarded-Email", "email-header"),
    ])
    assert current_user(headers, fallback="fallback@example.com") == "email-header"


def test_falls_back_through_preferred_username_to_user():
    headers = Headers([("X-Forwarded-User", "user-header")])
    assert current_user(headers, fallback=None) == "user-header"


def test_header_lookup_is_case_insensitive():
    headers = Headers([("x-forwarded-email", "lower-case-header")])
    assert current_user(headers, fallback=None) == "lower-case-header"


def test_uses_fallback_when_no_forwarded_headers():
    assert current_user(Headers(), fallback="dev@example.com") == "dev@example.com"


def test_anonymous_when_no_headers_and_no_fallback():
    assert current_user(Headers(), fallback=None) == "anonymous"


def test_blank_header_value_is_skipped_like_absent():
    headers = Headers([("X-Forwarded-Email", ""), ("X-Forwarded-User", "user-header")])
    assert current_user(headers, fallback=None) == "user-header"


def test_trust_boundary_is_the_apps_proxy_not_this_function():
    """Documents, does not enforce: current_user cannot distinguish a header
    the Apps proxy set from one a client forged -- it trusts whichever
    X-Forwarded-* value it is handed. Every per-user boundary in the tutor
    (conversation list/read/delete, throttle window, /lab-link's workspace
    path probe) rests entirely on the Apps proxy replacing, not appending,
    client-supplied copies of these headers before a request reaches this
    function. If that assumption ever breaks -- an append-mode proxy, or the
    app reached other than through it -- this same header a client sends
    directly is read as fact, exactly as this test shows."""
    forged = Headers([("X-Forwarded-Email", "victim@example.com")])
    assert current_user(forged, fallback=None) == "victim@example.com"
