"""Who is asking: the user key from Databricks Apps' forwarded identity headers.

Every per-user boundary in the tutor is this function: which conversations a
request can list, read, or delete, whose throttle window it spends, and which
workspace path /lab-link probes. current_user has no way to tell a header the
Apps proxy set from one a client forged -- it trusts the first non-empty
X-Forwarded-* header unconditionally. Isolation depends entirely on the Apps
proxy replacing, not appending, client-supplied copies of these headers
before a request ever reaches this function. A local run, a port-forward, or
any host that is not that proxy is single-identity via TUTOR_DEV_USER, not
authenticated multi-user.
"""

FORWARDED = ("X-Forwarded-Email", "X-Forwarded-Preferred-Username", "X-Forwarded-User")


def current_user(headers, fallback: str | None) -> str:
    """First non-empty forwarded header, else the caller's fallback, else "anonymous"."""
    for name in FORWARDED:
        value = headers.get(name)
        if value:
            return value
    return fallback or "anonymous"
