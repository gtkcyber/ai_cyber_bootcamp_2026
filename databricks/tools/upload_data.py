#!/usr/bin/env python3
"""Mirror the course dataset onto the Unity Catalog volume.

Usage (from the course repo root):
    .venv/bin/python databricks/tools/upload_data.py [--dry-run] [--workers 16]

Uploads data/ as-is, plus the fingerprint images extracted from their zip, plus the
one ai_examples skill Module 11.2 reads. Idempotent: a remote file whose size already
matches the local one is skipped, so a re-run after a partial upload is cheap.
"""

import argparse
import os
import shutil
import sys
import tempfile
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import NotFound

PROFILE = "gtk-workspace"
VOLUME = "/Volumes/ai_cyber_bootcamp/course/data"
FINGERPRINT_ZIP = "data/fingerprints/fingerprint_train_data.zip"
FINGERPRINT_DEST = "fingerprints/train_data"
SKILLS_SRC = "ai_examples/skills"
SKILLS_DEST = "skills"


def local_files(root: str) -> list:
    """(absolute path, size, destination-relative path) for every file under root."""
    out = []
    for base, _dirs, names in os.walk(root):
        for name in sorted(names):
            path = os.path.join(base, name)
            out.append((path, os.path.getsize(path), os.path.relpath(path, root)))
    return sorted(out)


def remote_sizes(w, prefix: str) -> dict:
    """Every file already on the volume under prefix, by relative path -> size."""
    sizes = {}
    stack = [f"{VOLUME}/{prefix}".rstrip("/")]
    while stack:
        here = stack.pop()
        try:
            entries = list(w.files.list_directory_contents(here))
        except NotFound:
            continue
        for entry in entries:
            if entry.is_directory:
                stack.append(entry.path)
            else:
                rel = entry.path[len(VOLUME) + 1:]
                sizes[rel] = entry.file_size
    return sizes


def upload_one(w, local: str, dest_rel: str) -> tuple:
    for attempt in range(3):
        try:
            with open(local, "rb") as fh:
                w.files.upload(f"{VOLUME}/{dest_rel}", fh, overwrite=True)
            return dest_rel, None
        except Exception as exc:  # noqa: BLE001 - report, retry, then give up
            if attempt == 2:
                return dest_rel, str(exc)
            time.sleep(2 * (attempt + 1))


def plan_uploads(scratch: str) -> list:
    """(local path, destination-relative path) for everything that should be on the volume."""
    jobs = [(p, rel) for p, _s, rel in local_files("data")]

    extracted = os.path.join(scratch, "train_data")
    os.makedirs(extracted, exist_ok=True)
    with zipfile.ZipFile(FINGERPRINT_ZIP) as zf:
        zf.extractall(scratch)
    # The zip contains a top-level train_data/ directory; tolerate either shape.
    root = extracted if os.listdir(extracted) else scratch
    jobs += [(p, f"{FINGERPRINT_DEST}/{rel}") for p, _s, rel in local_files(root)]

    jobs += [(p, f"{SKILLS_DEST}/{rel}") for p, _s, rel in local_files(SKILLS_SRC)]
    return jobs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--workers", type=int, default=16)
    args = ap.parse_args()

    w = WorkspaceClient(profile=PROFILE)
    scratch = tempfile.mkdtemp(prefix="bootcamp_upload_")
    try:
        jobs = plan_uploads(scratch)
        already = remote_sizes(w, "")
        todo = [(p, rel) for p, rel in jobs
                if already.get(rel) != os.path.getsize(p)]
        total_bytes = sum(os.path.getsize(p) for p, _ in todo)
        print(f"PLAN {len(jobs)} files total, {len(todo)} to upload, "
              f"{total_bytes / 1e6:.1f} MB", flush=True)
        if args.dry_run:
            return 0

        done = errors = 0
        t0 = time.time()
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futs = [ex.submit(upload_one, w, p, rel) for p, rel in todo]
            for fut in as_completed(futs):
                rel, err = fut.result()
                done += 1
                if err:
                    errors += 1
                    print(f"ERROR {rel}: {err}", flush=True)
                if done % 200 == 0 or done == len(todo):
                    print(f"PROGRESS {done}/{len(todo)} {errors} errors "
                          f"{time.time() - t0:.0f}s", flush=True)
        print(f"DONE {done} uploaded, {errors} errors, "
              f"{(time.time() - t0) / 60:.1f} min", flush=True)
        return 1 if errors else 0
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
