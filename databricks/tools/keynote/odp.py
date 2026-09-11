"""Surgery on the ODP LibreOffice makes from a Keynote file.

LibreOffice's Keynote importer (libetonyek) keeps text, images and layout and
loses everything that moves: every build object is drawn at once, skipped
slides are exported, animations are gone. The PDF the deck needs has one page
per build stage, so this module rewrites the ODP's content.xml before the PDF
export: it drops the pages of skipped slides and replaces each slide with
builds by one copy of its page per stage, with the objects not yet on the
canvas removed.

Objects are matched between the two worlds by geometry. Keynote and the ODP
share the 1920x1080-point canvas (the importer writes centimetres; 1 cm is
72/2.54 points), and the importer keeps the object's origin exactly: a shape
with a label comes out as a `draw:path` and a `draw:frame` at the shape's
box, a line as `draw:line` endpoints, and a zero-size Keynote text shape (an
auto-sized label) as a frame of the text's real size at the same origin. So an
ODP element belongs to the drawable whose origin it shares, size agreeing
where the drawable has one; failing that, to the smallest drawable whose box
contains it. Nothing is matched by index: the importer emits more elements
than Keynote has drawables, and the surplus is not evenly spread.

Two importer habits are patched on the way through, both measured on the
course decks: an empty `text:bullet-char` where Keynote draws a bullet, and
bullet glyphs sized at 45% of the text where Keynote draws them full size.

Tables: the importer writes a Keynote table as a `draw:frame` holding a
`table:table` with the right columns and rows but every cell empty and
unstyled, which is why they rendered as blank rectangles. `fill_table` puts
the decoded cell text back (tables.py) and styles the cells the way Keynote
did: fills, font, size, weight, colour, and gridlines when the table shows
them. The styles go into `office:automatic-styles` under names of their own.
"""

from __future__ import annotations

import copy
import math
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

from keynote.model import Drawable, Slide, Table
from keynote.stages import Stage
from keynote.tables import Look

NS = {
    "draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
    "svg": "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "presentation": "urn:oasis:names:tc:opendocument:xmlns:presentation:1.0",
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "fo": "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
    "xlink": "http://www.w3.org/1999/xlink",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
}
for _prefix, _uri in NS.items():
    ET.register_namespace(_prefix, _uri)


def _q(name: str) -> str:
    prefix, local = name.split(":")
    return f"{{{NS[prefix]}}}{local}"


POINTS_PER = {"pt": 1.0, "cm": 72 / 2.54, "mm": 72 / 25.4, "in": 72.0, "px": 0.75}
LENGTH_RE = re.compile(r"^\s*(-?[\d.]+)\s*([a-z]+)\s*$")

# Origins agree to the importer's rounding (three decimals of a centimetre is
# under a third of a point) except for shape outlines, whose path box can sit
# two points off the Keynote frame; objects on these slides are never that
# close together.
TOLERANCE_PT = 3.0


def points(length: str) -> float:
    m = LENGTH_RE.match(length)
    if not m:
        raise ValueError(f"not a length: {length!r}")
    return float(m.group(1)) * POINTS_PER[m.group(2)]


@dataclass(frozen=True)
class Box:
    x: float
    y: float
    width: float
    height: float

    def contains(self, other: "Box", tol: float = TOLERANCE_PT) -> bool:
        return (self.x - tol <= other.x and self.y - tol <= other.y
                and other.x + other.width <= self.x + self.width + tol
                and other.y + other.height <= self.y + self.height + tol)

    @property
    def area(self) -> float:
        return self.width * self.height


def element_box(node) -> Box | None:
    """The element's box in points, or None for an element without geometry."""
    get = node.get
    if get(_q("svg:x1")) is not None:
        xs = [points(get(_q("svg:x1"))), points(get(_q("svg:x2")))]
        ys = [points(get(_q("svg:y1"))), points(get(_q("svg:y2")))]
        return Box(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
    if get(_q("svg:x")) is not None:
        return Box(points(get(_q("svg:x"))), points(get(_q("svg:y"))),
                   points(get(_q("svg:width"))), points(get(_q("svg:height"))))
    children = [box for box in map(element_box, node) if box is not None]
    if not children:
        return None
    x = min(b.x for b in children)
    y = min(b.y for b in children)
    return Box(x, y, max(b.x + b.width for b in children) - x,
               max(b.y + b.height for b in children) - y)


def drawable_box(drawable: Drawable) -> Box:
    """The drawable's axis-aligned box on the canvas.

    Keynote stores the unrotated frame and an angle; the importer writes the
    rotated result (a rotated line becomes endpoints, so a vertical line is
    a zero-width box). Rotation is about the frame's centre.
    """
    if not drawable.angle:
        return Box(drawable.x, drawable.y, drawable.width, drawable.height)
    cx, cy = drawable.x + drawable.width / 2, drawable.y + drawable.height / 2
    cos, sin = math.cos(math.radians(drawable.angle)), math.sin(math.radians(drawable.angle))
    corners = [(cx + dx * cos - dy * sin, cy + dx * sin + dy * cos)
               for dx in (-drawable.width / 2, drawable.width / 2)
               for dy in (-drawable.height / 2, drawable.height / 2)]
    xs, ys = [x for x, _ in corners], [y for _, y in corners]
    return Box(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))


def _close(a: float, b: float, tol: float = TOLERANCE_PT) -> bool:
    return abs(a - b) <= tol


def match_element(box: Box, drawables) -> Drawable | None:
    """The drawable an ODP element renders, by the rule in the module docstring."""
    boxes = {d.identifier: drawable_box(d) for d in drawables}
    at_origin = [d for d in drawables
                 if _close(boxes[d.identifier].x, box.x) and _close(boxes[d.identifier].y, box.y)]
    if at_origin:
        sized = [d for d in at_origin
                 if _close(boxes[d.identifier].width, box.width)
                 and _close(boxes[d.identifier].height, box.height)]
        pool = sized or [d for d in at_origin if d.width == 0 and d.height == 0] or at_origin
        return min(pool, key=lambda d: boxes[d.identifier].area)
    around = [d for d in drawables if boxes[d.identifier].contains(box)]
    return min(around, key=lambda d: boxes[d.identifier].area) if around else None


def page_elements(page):
    """The drawn children of a page: everything but the presenter notes."""
    return [node for node in page if node.tag != _q("presentation:notes")]


def match_page(page, slide: Slide) -> dict[str, list]:
    """{drawable identifier: the page elements that render it}."""
    rendered: dict[str, list] = {}
    for node in page_elements(page):
        box = element_box(node)
        drawable = match_element(box, slide.drawables) if box else None
        if drawable is not None:
            rendered.setdefault(drawable.identifier, []).append(node)
    return rendered


def trim_paragraphs(node, keep: int) -> None:
    """Leave the first `keep` paragraphs of a text frame in place, remove the rest.

    Paragraphs are `text:p` leaves in document order, whether direct children
    of the text box or inside `text:list-item`s; a list item or list emptied
    by the trim goes too, so no orphan bullet is drawn.
    """
    for box in node.iter(_q("draw:text-box")):
        parents = {child: parent for parent in box.iter() for child in parent}
        for index, paragraph in enumerate(list(box.iter(_q("text:p")))):
            if index < keep:
                continue
            victim = paragraph
            while victim is not box:
                parent = parents[victim]
                parent.remove(victim)
                if len(parent) or parent is box:
                    break
                victim = parent


def stage_page(page, slide: Slide, stage: Stage, rendered: dict[str, list]):
    """A copy of `page` showing only what `stage` has on the canvas."""
    clone = copy.deepcopy(page)
    copies = dict(zip(page_elements(page), page_elements(clone)))
    for drawable in slide.drawables:
        nodes = [copies[node] for node in rendered.get(drawable.identifier, ())]
        if drawable.identifier not in stage.visible:
            for node in nodes:
                clone.remove(node)
        elif drawable.identifier in stage.paragraphs:
            for node in nodes:
                trim_paragraphs(node, stage.paragraphs[drawable.identifier])
    return clone


# ------------------------------------------------------------------ tables

CELL_PADDING = "0.12cm"
GRIDLINE = "0.5pt solid #b8b8b8"


def _style(root, name: str, family: str, properties: str, **attributes) -> str:
    """Append one automatic style and return its name."""
    styles = root.find("office:automatic-styles", NS)
    style = ET.SubElement(styles, _q("style:style"),
                          {_q("style:name"): name, _q("style:family"): family})
    ET.SubElement(style, _q(properties), {_q(k): v for k, v in attributes.items()})
    return name


def _cell_styles(root, prefix: str, look: Look, gridlines: bool) -> tuple[str, str]:
    """(cell style, paragraph style) for cells drawn with `look`."""
    cell = {"fo:padding": CELL_PADDING, "style:vertical-align": "middle",
            "fo:border": GRIDLINE if gridlines else "none"}
    if look.fill:
        cell["fo:background-color"] = look.fill
    cell_name = _style(root, f"{prefix}c", "table-cell", "style:table-cell-properties", **cell)
    styles = root.find("office:automatic-styles", NS)
    paragraph = ET.SubElement(styles, _q("style:style"),
                              {_q("style:name"): f"{prefix}p", _q("style:family"): "paragraph"})
    ET.SubElement(paragraph, _q("style:paragraph-properties"), {_q("fo:text-align"): "start"})
    ET.SubElement(paragraph, _q("style:text-properties"), {
        _q("fo:font-size"): f"{look.font_size:g}pt", _q("fo:color"): look.color,
        _q("fo:font-family"): look.font,
        _q("fo:font-weight"): "bold" if look.bold else "normal"})
    return cell_name, f"{prefix}p"


def fill_table(root, frame, table: Table, prefix: str) -> bool:
    """Put the cell text and Keynote's look into the importer's empty table.

    Returns False when the frame holds no table of the expected shape, so the
    caller can report the loss instead of drawing a wrong table.
    """
    grid = table.grid
    node = frame.find("table:table", NS)
    if grid is None or node is None:
        return False
    rows = node.findall("table:table-row", NS)
    if len(rows) != len(grid.cells):
        return False
    styles: dict[Look, tuple[str, str]] = {}
    for row_index, (row, cells) in enumerate(zip(rows, grid.cells)):
        # Keynote's stored height is the row's floor; the text may need more.
        row.set(_q("table:style-name"), _style(
            root, f"{prefix}r{row_index}", "table-row", "style:table-row-properties",
            **{"style:min-row-height": f"{grid.row_heights[row_index]:.2f}pt",
               "style:use-optimal-row-height": "true"}))
        nodes = [c for c in row if c.tag == _q("table:table-cell")]
        for node_cell, cell in zip(nodes, cells):
            if cell.look not in styles:
                styles[cell.look] = _cell_styles(root, f"{prefix}s{len(styles)}", cell.look, grid.gridlines)
            cell_style, paragraph_style = styles[cell.look]
            node_cell.set(_q("table:style-name"), cell_style)
            for child in list(node_cell):
                node_cell.remove(child)
            for line in cell.text.split("\n"):
                paragraph = ET.SubElement(node_cell, _q("text:p"), {_q("text:style-name"): paragraph_style})
                paragraph.text = line
    return True


def fill_tables(root, page, slide: Slide, rendered: dict[str, list]) -> list[dict]:
    """Fill every table on the page; the losses are the tables that could not be."""
    losses = []
    for index, table in enumerate(slide.tables):
        frames = [n for n in rendered.get(table.drawable, ()) if n.find("table:table", NS) is not None]
        prefix = f"kt{slide.number}_{index}"
        if not frames or not fill_table(root, frames[0], table, prefix):
            losses.append({"slide": slide.number, "kind": "table",
                           "detail": f"{table.rows}x{table.columns} table has no matching frame"})
    return losses


@dataclass(frozen=True)
class PageRecord:
    """One page of the rewritten deck: which slide and stage it shows."""
    slide: int
    stage: int
    stages: int


def expand(content_root, slides, stage_lists) -> tuple[list[PageRecord], list[dict]]:
    """Rewrite the presentation in place: skipped slides out, stages in.

    `slides` and `stage_lists` run parallel and cover every slide the importer
    exported, skipped ones included, in show order. Returns the page records
    of the rewritten deck and the losses found on the way: a table with no
    frame to fill, a build target the importer drew nothing for (its stage
    would be a blank click) and a stage that came out identical to the one
    before it (dropped).
    """
    presentation = content_root.find("office:body/office:presentation", NS)
    pages = presentation.findall("draw:page", NS)
    if len(pages) != len(slides):
        raise ValueError(f"the ODP has {len(pages)} pages for {len(slides)} slides")

    records: list[PageRecord] = []
    losses: list[dict] = []
    for page, slide, stages in zip(pages, slides, stage_lists):
        if slide.skipped:
            presentation.remove(page)
            continue
        rendered = match_page(page, slide) if slide.tables or len(stages) > 1 else {}
        losses.extend(fill_tables(content_root, page, slide, rendered))
        if len(stages) == 1:
            records.append(PageRecord(slide.number, 0, 1))
            continue
        built = {event.drawable for chunk in slide.chunks for event in chunk}
        for missing in sorted(built - set(rendered)):
            losses.append({"slide": slide.number, "kind": "build target",
                           "detail": f"drawable {missing} has no rendered element"})
        name = page.get(_q("draw:name"))
        clones, seen = [], []
        for index, stage in enumerate(stages):
            clone = stage_page(page, slide, stage, rendered)
            signature = ET.tostring(clone)
            if signature in seen:
                losses.append({"slide": slide.number, "kind": "stage",
                               "detail": f"stage {index} renders identically to an earlier one"})
                continue
            seen.append(signature)
            clones.append(clone)
        position = list(presentation).index(page)
        presentation.remove(page)
        for offset, clone in enumerate(clones):
            clone.set(_q("draw:name"), f"{name}-s{offset}")
            presentation.insert(position + offset, clone)
        records.extend(PageRecord(slide.number, index, len(clones))
                       for index in range(len(clones)))
    return records, losses


BULLET_SIZE_RE = re.compile(
    r'(<text:list-level-style-bullet[^>]*>.*?<style:text-properties[^>]*?)fo:font-size="45%"',
    re.S)


def patch_bullets(xml: str) -> str:
    """The importer's empty bullet characters and 45% bullet glyphs, corrected."""
    xml = xml.replace('text:bullet-char=""', 'text:bullet-char="•"')
    return BULLET_SIZE_RE.sub(r'\1fo:font-size="100%"', xml)


def read_content(odp: Path):
    with zipfile.ZipFile(odp) as archive:
        return ET.fromstring(patch_bullets(archive.read("content.xml").decode("utf-8")))


def write_odp(source: Path, target: Path, content_root) -> None:
    """`source` with its content.xml replaced (and styles.xml bullet-patched)."""
    content = ET.tostring(content_root, encoding="unicode", xml_declaration=True)
    with zipfile.ZipFile(source) as zin, zipfile.ZipFile(target, "w") as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "content.xml":
                data = content.encode("utf-8")
            elif item.filename == "styles.xml":
                data = patch_bullets(data.decode("utf-8")).encode("utf-8")
            compression = zipfile.ZIP_STORED if item.filename == "mimetype" else zipfile.ZIP_DEFLATED
            zout.writestr(item, data, compress_type=compression)
