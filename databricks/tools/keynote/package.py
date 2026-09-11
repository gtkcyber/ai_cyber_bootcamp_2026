"""Flatten a Keynote (.key) file into the layout keynote_parser.codec.IWAFile
can read directly: real Index/*.iwa files on disk (Data/ and Metadata/ copied
alongside), with three undecodable archives dropped.

Apple's Keynote ships a .key in one of two shapes on disk:

* A directory package. Index/ is stored as one entry, Index.zip, inside the
  package -- the .iwa files sit at "Index/..." paths *inside* that zip, not
  loose on disk. This is the normal, editable form; every course deck ships
  this way except the one noted below.
* A single-file .key ("Advanced > Save as single file" in Keynote, or an
  AirDrop/attachment export). This is itself one zip, already carrying
  "Index/...", "Data/..." and "Metadata/..." at the top level -- there is no
  nested Index.zip to unwrap. `Module 14 - Red Teaming AI.key` is the one
  deck in this course saved this way.

Three archives are dropped in both cases: Index/OperationStorage.iwa,
Index/ActivityStream.iwa and Index/AnnotationAuthorStorage.iwa. keynote_parser
cannot decode them -- they use protobuf message types absent from its bundled
schema -- and none of the three carries slide content; they log editing and
collaboration history, not the document itself.
"""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

SKIP_ARCHIVES = frozenset({
    "Index/OperationStorage.iwa",
    "Index/ActivityStream.iwa",
    "Index/AnnotationAuthorStorage.iwa",
})


def _extract(zf: zipfile.ZipFile, dest: Path, prefixes: frozenset[str] | None) -> None:
    """Write every member of `zf` under `dest`, applying the archive skip list.

    `prefixes`, when given, additionally restricts extraction to members
    whose path starts with one of them -- used for a single-file .key, whose
    zip also carries preview*.jpg and other top-level clutter this package
    has no use for.
    """
    for name in zf.namelist():
        if name.endswith("/") or name in SKIP_ARCHIVES:
            continue
        if prefixes is not None and not any(name.startswith(p) for p in prefixes):
            continue
        target = dest / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(zf.read(name))


def flatten(key_path: Path, workdir: Path) -> Path:
    """Flatten `key_path` (directory package or single-file .key) into `workdir`.

    Idempotent and network-free: `workdir` is wiped and rebuilt from `key_path`
    every call, so re-running never leaves stale files from a previous decode
    of a different (or since-edited) source. Returns `workdir`.
    """
    key_path = Path(key_path)
    workdir = Path(workdir)
    if workdir.exists():
        shutil.rmtree(workdir)
    workdir.mkdir(parents=True)

    if key_path.is_dir():
        with zipfile.ZipFile(key_path / "Index.zip") as index_zip:
            _extract(index_zip, workdir, prefixes=None)
        for name in ("Data", "Metadata"):
            source = key_path / name
            if source.is_dir():
                shutil.copytree(source, workdir / name)
    else:
        with zipfile.ZipFile(key_path) as bundle:
            _extract(bundle, workdir, prefixes=frozenset({"Index/", "Data/", "Metadata/"}))

    return workdir
