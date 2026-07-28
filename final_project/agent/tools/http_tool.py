"""Reference tool: HTTP request with session management.

Reference implementation — read this to understand what a well-designed tool
looks like before writing your own. You MAY edit this file, but you do not
have to; extending it via a subclass or a new tool is usually cleaner.
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from pydantic import BaseModel, Field

from .base import tool


_client: httpx.Client | None = None


def _get_client() -> httpx.Client:
    """Singleton HTTP client so cookies persist across calls."""
    global _client
    if _client is None:
        base = os.environ.get("TARGET_URL", "http://localhost:3000")
        _client = httpx.Client(
            base_url=base,
            timeout=15.0,
            follow_redirects=True,
            headers={"User-Agent": "gtkcyber-pentest-agent/1.0"},
        )
    return _client


def reset_session() -> None:
    """Drop and recreate the HTTP session. Useful between runs."""
    global _client
    if _client is not None:
        _client.close()
    _client = None


class HttpParams(BaseModel):
    method: str = Field(
        ..., description="HTTP verb: GET, POST, PUT, PATCH, DELETE, OPTIONS"
    )
    path: str = Field(
        ..., description="Path or full URL relative to the target (e.g. '/rest/user/login')"
    )
    headers: dict[str, str] | None = Field(
        default=None, description="Extra request headers (merged onto defaults)"
    )
    json_body: dict[str, Any] | None = Field(
        default=None, description="JSON body to send. Mutually exclusive with form_body."
    )
    form_body: dict[str, str] | None = Field(
        default=None,
        description="Form-encoded body. Mutually exclusive with json_body.",
    )
    params: dict[str, str] | None = Field(
        default=None, description="Query-string parameters"
    )


@tool(
    description=(
        "Send an HTTP request to the target application with session cookies "
        "preserved across calls. Use this as the foundation for any web "
        "interaction. Returns status code, response headers, and body (truncated "
        "to ~8KB to conserve context)."
    ),
    params=HttpParams,
)
def http_request(
    method: str,
    path: str,
    headers: dict[str, str] | None = None,
    json_body: dict[str, Any] | None = None,
    form_body: dict[str, str] | None = None,
    params: dict[str, str] | None = None,
) -> dict[str, Any]:
    client = _get_client()
    try:
        response = client.request(
            method=method.upper(),
            url=path,
            headers=headers or None,
            json=json_body,
            data=form_body,
            params=params,
        )
    except httpx.RequestError as e:
        return {"error": f"{type(e).__name__}: {e}", "path": path}

    body = response.text
    truncated = False
    if len(body) > 8000:
        body = body[:8000]
        truncated = True

    return {
        "status": response.status_code,
        "headers": dict(response.headers),
        "body": body,
        "body_truncated": truncated,
        "url": str(response.url),
    }
