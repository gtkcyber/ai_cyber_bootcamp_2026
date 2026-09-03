"""Unit tests for upload_data.py against a fake WorkspaceClient — no network, no
Databricks workspace. Every test builds its own tiny data/ tree under tmp_path so
nothing depends on the real course dataset."""

import sys
import zipfile
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import upload_data as u


class FakeEntry:
    def __init__(self, path, is_directory, file_size=0):
        self.path = path
        self.is_directory = is_directory
        self.file_size = file_size


class FakeFilesAPI:
    """In-memory stand-in for WorkspaceClient().files, keyed by full volume path."""

    def __init__(self, initial: dict | None = None):
        self.contents = dict(initial or {})  # full path -> size
        self.uploaded = []  # [(full path, bytes written)]
        self.fail_paths = set()
        self.fail_until_attempt = {}

    def list_directory_contents(self, path):
        prefix = path.rstrip("/") + "/"
        seen_dirs = set()
        out = []
        for full, size in self.contents.items():
            if not full.startswith(prefix):
                continue
            rest = full[len(prefix):]
            if "/" in rest:
                d = prefix + rest.split("/", 1)[0]
                if d not in seen_dirs:
                    seen_dirs.add(d)
                    out.append(FakeEntry(d, is_directory=True))
            else:
                out.append(FakeEntry(full, is_directory=False, file_size=size))
        return out

    def upload(self, path, fh, overwrite=True):
        attempt = self.fail_until_attempt.get(path, 0)
        if path in self.fail_paths and attempt > 0:
            self.fail_until_attempt[path] = attempt - 1
            raise RuntimeError(f"simulated failure for {path}")
        data = fh.read()
        self.contents[path] = len(data)
        self.uploaded.append((path, len(data)))


class FakeWorkspaceClient:
    def __init__(self, files: FakeFilesAPI):
        self.files = files


def _write(path: Path, content: bytes = b"x"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


@pytest.fixture
def course_repo(tmp_path, monkeypatch):
    """A minimal course repo tree with data/, the fingerprint zip, and ai_examples/skills."""
    monkeypatch.chdir(tmp_path)
    _write(tmp_path / "data" / "a.csv", b"1,2,3")
    _write(tmp_path / "data" / "sub" / "b.csv", b"4,5,6,7")

    zip_path = tmp_path / u.FINGERPRINT_ZIP
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("train_data/0001_01.bmp", b"bmpbytes")
        zf.writestr("train_data/0001_02.bmp", b"bmpbytes2")

    _write(tmp_path / u.SKILLS_SRC / "triage-suspicious-url" / "SKILL.md", b"# skill")
    return tmp_path


def test_local_files_lists_everything_under_root_sorted(course_repo):
    files = u.local_files("data")
    rels = [rel for _p, _s, rel in files]
    assert rels == sorted(rels)
    assert ("a.csv" in rels) and (str(Path("sub") / "b.csv") in rels)
    sizes = {rel: size for _p, size, rel in files}
    assert sizes["a.csv"] == 5


def test_remote_sizes_walks_nested_directories():
    files = FakeFilesAPI({
        f"{u.VOLUME}/a.csv": 5,
        f"{u.VOLUME}/sub/b.csv": 7,
    })
    w = FakeWorkspaceClient(files)
    sizes = u.remote_sizes(w, "")
    assert sizes == {"a.csv": 5, "sub/b.csv": 7}


def test_remote_sizes_on_a_missing_prefix_is_empty():
    from databricks.sdk.errors import NotFound

    class RaisingFiles(FakeFilesAPI):
        def list_directory_contents(self, path):
            raise NotFound("nope")

    w = FakeWorkspaceClient(RaisingFiles())
    assert u.remote_sizes(w, "") == {}


def test_plan_uploads_covers_data_fingerprints_and_skills(course_repo, tmp_path):
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    jobs = u.plan_uploads(str(scratch))
    dests = {rel for _p, rel in jobs}
    assert "a.csv" in dests
    assert str(Path("sub") / "b.csv") in dests
    assert f"{u.FINGERPRINT_DEST}/0001_01.bmp" in dests
    assert f"{u.FINGERPRINT_DEST}/0001_02.bmp" in dests
    assert f"{u.SKILLS_DEST}/triage-suspicious-url/SKILL.md" in dests


def test_upload_one_succeeds_and_records_bytes(course_repo, tmp_path):
    files = FakeFilesAPI()
    w = FakeWorkspaceClient(files)
    local = str(tmp_path / "data" / "a.csv")
    rel, err = u.upload_one(w, local, "a.csv")
    assert err is None
    assert rel == "a.csv"
    assert files.contents[f"{u.VOLUME}/a.csv"] == 5


def test_upload_one_retries_then_succeeds(course_repo, tmp_path, monkeypatch):
    monkeypatch.setattr(u.time, "sleep", lambda _s: None)
    files = FakeFilesAPI()
    dest = f"{u.VOLUME}/a.csv"
    files.fail_paths.add(dest)
    files.fail_until_attempt[dest] = 2  # fails twice, succeeds on the 3rd attempt
    w = FakeWorkspaceClient(files)
    local = str(tmp_path / "data" / "a.csv")
    rel, err = u.upload_one(w, local, "a.csv")
    assert err is None
    assert dest in files.contents


def test_upload_one_gives_up_after_three_failures(course_repo, tmp_path, monkeypatch):
    monkeypatch.setattr(u.time, "sleep", lambda _s: None)
    files = FakeFilesAPI()
    dest = f"{u.VOLUME}/a.csv"
    files.fail_paths.add(dest)
    files.fail_until_attempt[dest] = 99  # always fails
    w = FakeWorkspaceClient(files)
    local = str(tmp_path / "data" / "a.csv")
    rel, err = u.upload_one(w, local, "a.csv")
    assert err is not None
    assert dest not in files.contents


def test_main_dry_run_reports_plan_and_uploads_nothing(course_repo, monkeypatch, capsys):
    files = FakeFilesAPI()
    monkeypatch.setattr(u, "WorkspaceClient", lambda profile: FakeWorkspaceClient(files))
    monkeypatch.setattr(sys, "argv", ["upload_data.py", "--dry-run"])
    rc = u.main()
    assert rc == 0
    assert files.uploaded == []
    out = capsys.readouterr().out
    assert out.startswith("PLAN ")


def test_main_uploads_everything_not_already_on_the_volume(course_repo, monkeypatch, capsys):
    files = FakeFilesAPI()
    monkeypatch.setattr(u, "WorkspaceClient", lambda profile: FakeWorkspaceClient(files))
    monkeypatch.setattr(sys, "argv", ["upload_data.py", "--workers", "2"])
    rc = u.main()
    assert rc == 0
    uploaded_rels = {full[len(u.VOLUME) + 1:] for full, _size in files.uploaded}
    assert "a.csv" in uploaded_rels
    assert f"{u.SKILLS_DEST}/triage-suspicious-url/SKILL.md" in uploaded_rels
    out = capsys.readouterr().out
    assert "DONE" in out and "0 errors" in out


def test_main_second_run_uploads_nothing_new(course_repo, monkeypatch, capsys):
    files = FakeFilesAPI()
    monkeypatch.setattr(u, "WorkspaceClient", lambda profile: FakeWorkspaceClient(files))
    monkeypatch.setattr(sys, "argv", ["upload_data.py"])
    u.main()
    files.uploaded.clear()
    monkeypatch.setattr(sys, "argv", ["upload_data.py", "--dry-run"])
    rc = u.main()
    assert rc == 0
    out = capsys.readouterr().out
    assert "0 to upload" in out
