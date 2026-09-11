"""Build one course deck from its Keynote file.

    flatten .key -> decode (model.py) -> LibreOffice ODP (render.py)
      -> one page per build stage, skipped slides out (odp.py)
      -> PDF -> slides/<Module>.pdf
      + decks/<slug>/media/ (media.py) + databricks/keynote/<slug>.json
      -> build_decks.build_deck

The manifest is what build_decks.py reads to group stage pages into one
reveal slide and to place the movies and embeds; its `losses` list is what
the render could not reproduce (a table without a frame to fill, a build
object the importer drew nothing for), so nobody has to compare
the deck with Keynote by eye to know what is missing. Native tables are
filled back into the importer's empty table frames on the way (odp.py).
"""

from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from pathlib import Path

from build_decks import build_deck, manifest_path, slug_for
from keynote import media, odp, render
from keynote.model import load_deck
from keynote.package import flatten
from keynote.stages import stages


def flat_key(flat_dir: Path, target: Path) -> Path:
    """The flattened package zipped back into one .key LibreOffice can open."""
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(flat_dir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(flat_dir).as_posix())
    return target


def replace_pdf(root: Path, slug: str, pdf: Path, name: str) -> Path:
    """Install the new PDF as slides/<name> and drop any older export of the
    same deck, whatever it was called: two PDFs for one slug would leave
    build_decks reading whichever sorts first."""
    slides = root / "slides"
    slides.mkdir(exist_ok=True)
    for old in slides.glob("*.pdf"):
        if old.name != name and slug_for(old.name) == slug:
            old.unlink()
    target = slides / name
    shutil.copyfile(pdf, target)
    return target


def build(key_path: Path, root: Path, workdir: Path | None = None) -> dict:
    """Everything above for one deck; returns build_deck's summary plus the losses."""
    key_path, root = Path(key_path), Path(root)
    slug = slug_for(key_path.name)
    workdir = Path(workdir) if workdir else Path(tempfile.mkdtemp(prefix=f"keynote-{slug}-"))
    render.ensure_image()

    flat_dir = flatten(key_path, workdir / "flat")
    deck = load_deck(key_path, workdir=workdir / "model")
    source_odp = render.key_to_odp(flat_key(flat_dir, workdir / key_path.with_suffix(".key").name))

    content = odp.read_content(source_odp)
    stage_lists = [stages([d.identifier for d in slide.drawables], slide.chunks)
                   for slide in deck.slides]
    records, losses = odp.expand(content, deck.slides, stage_lists)
    staged = workdir / "staged.odp"
    odp.write_odp(source_odp, staged, content)
    pdf = replace_pdf(root, slug, render.odp_to_pdf(staged), key_path.stem + ".pdf")

    media_dir = root / "decks" / slug / "media"
    if media_dir.exists():
        shutil.rmtree(media_dir)
    entries = []
    for slide in deck.slides:
        if not slide.skipped:
            entries += media.movie_entries(slide, workdir, media_dir)
            entries += media.youtube_entries(slide)

    manifest = {
        "slug": slug, "source": key_path.name, "pdf": pdf.name,
        "page_count": len(records),
        "pages": [{"page": number, "slide": r.slide, "stage": r.stage, "stages": r.stages}
                  for number, r in enumerate(records, start=1)],
        "media": entries,
        "losses": sorted(losses, key=lambda l: (l["slide"], l["kind"])),
    }
    path = manifest_path(root, slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    result = build_deck(root, pdf)
    result["losses"] = manifest["losses"]
    result["workdir"] = workdir
    return result
