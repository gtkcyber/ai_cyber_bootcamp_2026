"""Reference tool: basic endpoint enumerator.

Simpler reference tool than http_tool.py. Demonstrates how to wrap deterministic
reconnaissance logic behind a tool-call interface so the LLM can delegate it
rather than reasoning about it token-by-token.
"""

from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from .base import tool
from .http_tool import _get_client


class ReconParams(BaseModel):
    path: str = Field(
        default="/",
        description="Starting path to scan (usually '/' for the SPA entry point).",
    )


@tool(
    description=(
        "Enumerate endpoints by fetching a page and scanning its HTML + linked "
        "JavaScript for API paths, forms, and links. Returns deduplicated lists "
        "of endpoints, forms, and URLs. Use this early to understand the attack "
        "surface before targeted probing."
    ),
    params=ReconParams,
)
def recon_endpoints(path: str = "/") -> dict[str, Any]:
    client = _get_client()
    try:
        page = client.get(path)
    except Exception as e:
        return {"error": f"failed to fetch {path}: {e}"}

    html = page.text
    soup = BeautifulSoup(html, "html.parser")

    links: set[str] = set()
    for a in soup.find_all("a", href=True):
        links.add(a["href"])
    scripts = [s.get("src") for s in soup.find_all("script", src=True)]

    forms: list[dict[str, Any]] = []
    for form in soup.find_all("form"):
        forms.append(
            {
                "action": form.get("action"),
                "method": (form.get("method") or "GET").upper(),
                "inputs": [
                    {"name": i.get("name"), "type": i.get("type")}
                    for i in form.find_all("input")
                ],
            }
        )

    api_paths: set[str] = set()
    api_pattern = re.compile(r"""["']((?:/api|/rest)/[A-Za-z0-9_/\-{}:]+)["']""")
    api_paths.update(api_pattern.findall(html))

    for script_src in scripts:
        if not script_src or script_src.startswith(("http://", "https://")):
            continue
        try:
            resp = client.get(script_src)
            api_paths.update(api_pattern.findall(resp.text))
        except Exception:
            continue

    return {
        "page": path,
        "links": sorted(links),
        "forms": forms,
        "scripts": scripts,
        "api_paths": sorted(api_paths),
    }
