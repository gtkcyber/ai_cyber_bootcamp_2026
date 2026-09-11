"""The movies and YouTube embeds a deck carries, as the manifest wants them.

LibreOffice draws a movie's frame blank, so the deck overlays a <video> on
the finished page instead: build_decks.py places it by the manifest's `box`
(the drawable's frame as fractions of the 1920x1080 canvas). Each movie is
written next to the page images as decks/<slug>/media/slide-NNN.mp4 with a
.webp poster -- Keynote's own poster image when it stored one, else the
first frame -- so the volume upload that carries the deck carries its movies.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image

from keynote import render
from keynote.model import Slide

CANVAS = (1920.0, 1080.0)


def box_of(slide: Slide, drawable_id: str) -> list[float]:
    drawable = next(d for d in slide.drawables if d.identifier == drawable_id)
    return [round(drawable.x / CANVAS[0], 4), round(drawable.y / CANVAS[1], 4),
            round(drawable.width / CANVAS[0], 4), round(drawable.height / CANVAS[1], 4)]


def _poster(source: Path, target: Path) -> None:
    with Image.open(source) as image:
        image.convert("RGB").save(target, "WEBP", quality=82, method=6)


def movie_entries(slide: Slide, workdir: Path, media_dir: Path) -> list[dict]:
    """Convert the slide's movies into media_dir; one manifest entry each."""
    entries = []
    for index, movie in enumerate(slide.movies):
        if movie.data_path is None:
            continue
        name = f"slide-{slide.number:03d}" + (f"-{index + 1}" if index else "")
        staged = workdir / (name + "-source" + movie.data_path.suffix)
        shutil.copyfile(movie.data_path, staged)
        mp4 = render.to_mp4(staged, name + ".mp4")
        if movie.poster_path is not None:
            frame = movie.poster_path
        else:
            frame = render.first_frame(mp4, name + ".png")
        media_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(mp4, media_dir / mp4.name)
        _poster(frame, media_dir / (name + ".webp"))
        entries.append({"slide": slide.number, "kind": "movie",
                        "src": f"media/{name}.mp4", "poster": f"media/{name}.webp",
                        "box": box_of(slide, movie.drawable)})
    return entries


def youtube_entries(slide: Slide) -> list[dict]:
    return [{"slide": slide.number, "kind": "youtube", "id": video.video_id,
             "box": box_of(slide, video.drawable)}
            for video in slide.web_videos if video.video_id]
