"""LibreOffice and ffmpeg, run inside the project's Docker image.

Nothing is installed on the host: the image in docker/ carries Impress with
its Keynote importer, the decks' fonts and ffmpeg. Every call bind-mounts one
working directory at /work and runs as the invoking user, so the files it
writes are the user's; LibreOffice needs a writable HOME for its profile,
hence HOME=/tmp inside the container.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

IMAGE = "bootcamp-keynote"
DOCKER_DIR = Path(__file__).resolve().parent / "docker"


def ensure_image() -> None:
    """Build the image the first time; a later change to docker/ needs a rebuild by hand."""
    probe = subprocess.run(["docker", "image", "inspect", IMAGE],
                           capture_output=True, text=True)
    if probe.returncode == 0:
        return
    subprocess.run(["docker", "build", "-t", IMAGE, str(DOCKER_DIR)], check=True)


def run(workdir: Path, command: list[str]) -> subprocess.CompletedProcess:
    """Run `command` in the image with `workdir` mounted at /work."""
    return subprocess.run(
        ["docker", "run", "--rm", "--user", f"{os.getuid()}:{os.getgid()}",
         "-e", "HOME=/tmp", "-v", f"{Path(workdir).resolve()}:/work", "-w", "/work",
         IMAGE, *command],
        check=True, capture_output=True, text=True)


def _convert(source: Path, target_format: str) -> Path:
    """`soffice --convert-to` into the source's own directory."""
    source = Path(source)
    run(source.parent, ["soffice", "--headless", "--norestore",
                        "--convert-to", target_format, "--outdir", "/work", source.name])
    target = source.with_suffix(f".{target_format}")
    if not target.is_file():
        raise RuntimeError(f"LibreOffice produced no {target.name}")
    return target


def key_to_odp(flat_key: Path) -> Path:
    return _convert(flat_key, "odp")


def odp_to_pdf(odp: Path) -> Path:
    return _convert(odp, "pdf")


def video_codecs(media: Path) -> list[str]:
    """Codec names of the file's streams, video first."""
    out = run(Path(media).parent, [
        "ffprobe", "-v", "error", "-show_entries", "stream=codec_name",
        "-of", "csv=p=0", Path(media).name])
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


def to_mp4(source: Path, target_name: str) -> Path:
    """An MP4 browsers play: a remux when the streams already are H.264/AAC,
    a transcode otherwise (GIFs, ProRes, PCM audio...). Even dimensions and
    yuv420p because that is what every browser decoder accepts."""
    source = Path(source)
    codecs = video_codecs(source)
    if codecs and codecs[0] == "h264" and all(c in ("h264", "aac") for c in codecs):
        recode = ["-c", "copy"]
    else:
        recode = ["-c:v", "libx264", "-preset", "medium", "-crf", "23", "-pix_fmt", "yuv420p",
                  "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-c:a", "aac"]
    run(source.parent, ["ffmpeg", "-v", "error", "-y", "-i", source.name,
                        *recode, "-movflags", "+faststart", target_name])
    return source.parent / target_name


def first_frame(video: Path, target_name: str) -> Path:
    """The first frame as a PNG, for a movie Keynote stored no poster for."""
    video = Path(video)
    run(video.parent, ["ffmpeg", "-v", "error", "-y", "-i", video.name,
                       "-frames:v", "1", target_name])
    return video.parent / target_name
