"""HTTP Range replies for the deck media.

A browser fetches a <video> in byte ranges and will neither play nor seek a
file whose server answers a Range request with a plain 200, so whatever serves
the movies has to speak 206. Only the single-range form is handled: it is all a
media element ever sends, and a multipart body would have no caller.
"""
import re

from flask import Response

RANGE_RE = re.compile(r"^bytes=(\d*)-(\d*)$")


def partial_response(data: bytes, mimetype: str, range_header: str | None) -> Response:
    """The whole file, or the requested slice of it as a 206."""
    size = len(data)
    if not range_header:
        return Response(data, mimetype=mimetype, headers={"Accept-Ranges": "bytes"})
    m = RANGE_RE.match(range_header.strip())
    if not m or not (m.group(1) or m.group(2)):
        return _unsatisfiable(size)
    if not m.group(1):  # bytes=-N: the last N bytes
        start, end = max(size - int(m.group(2)), 0), size - 1
    else:
        start = int(m.group(1))
        end = min(int(m.group(2)), size - 1) if m.group(2) else size - 1
    if start >= size or start > end:
        return _unsatisfiable(size)
    return Response(data[start:end + 1], status=206, mimetype=mimetype,
                    headers={"Accept-Ranges": "bytes",
                             "Content-Range": f"bytes {start}-{end}/{size}"})


def _unsatisfiable(size: int) -> Response:
    return Response(status=416, headers={"Accept-Ranges": "bytes",
                                         "Content-Range": f"bytes */{size}"})
