"""Byte-range replies for the movies."""
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from ranges import partial_response  # noqa: E402

DATA = b"0123456789"


def test_no_range_header_is_the_whole_file_and_advertises_ranges():
    r = partial_response(DATA, "video/mp4", None)
    assert r.status_code == 200
    assert r.get_data() == DATA
    assert r.headers["Accept-Ranges"] == "bytes"
    assert r.mimetype == "video/mp4"


def test_a_closed_range_is_a_206_with_that_slice():
    r = partial_response(DATA, "video/mp4", "bytes=2-4")
    assert r.status_code == 206
    assert r.get_data() == b"234"
    assert r.headers["Content-Range"] == "bytes 2-4/10"


def test_an_open_range_runs_to_the_end():
    r = partial_response(DATA, "video/mp4", "bytes=7-")
    assert r.get_data() == b"789"
    assert r.headers["Content-Range"] == "bytes 7-9/10"


def test_an_end_past_the_file_is_clipped():
    r = partial_response(DATA, "video/mp4", "bytes=8-500")
    assert r.get_data() == b"89"
    assert r.headers["Content-Range"] == "bytes 8-9/10"


def test_a_suffix_range_is_the_last_bytes():
    r = partial_response(DATA, "video/mp4", "bytes=-3")
    assert r.get_data() == b"789"
    assert r.headers["Content-Range"] == "bytes 7-9/10"


def test_a_start_past_the_end_is_416_with_the_size():
    r = partial_response(DATA, "video/mp4", "bytes=10-")
    assert r.status_code == 416
    assert r.headers["Content-Range"] == "bytes */10"


def test_a_malformed_range_is_416():
    assert partial_response(DATA, "video/mp4", "bytes=-").status_code == 416
    assert partial_response(DATA, "video/mp4", "items=1-2").status_code == 416
    assert partial_response(DATA, "video/mp4", "bytes=5-2").status_code == 416
