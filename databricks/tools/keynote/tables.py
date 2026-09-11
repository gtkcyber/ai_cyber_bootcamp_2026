"""Keynote table cells and their look, out of the TST archives.

A table's `TST.TableModelArchive.baseDataStore` points at everything: the
string table (`TST.TableDataList`, key -> text), the rich-text table (key ->
`TST.RichTextPayloadArchive` -> `TSWP.StorageArchive`), the row and column
header buckets (`TST.HeaderStorageBucket`, one entry per row/column with its
size in points) and the tiles (`TST.Tile`, whose `rowInfos` carry the cell
bytes). Those archives sit in Index/Tables/, so the registry has to include
that directory (model.build_registry does).

A row's cells are one buffer plus an int16 offset per column (-1 for an empty
cell). Each cell starts with a version byte (5, the only one Keynote writes
now), a type byte and a uint32 of flags at offset 8 that says which fields
follow, in a fixed order: decimal128, double, datetime, string id, rich-text
id, cell style id, text style id, then format ids this module does not need.
Cell types: 0 empty, 2 number (in the decimal128), 3 text (string id), 9 rich
text (rich id); everything else is rendered as its type name so a surprise is
visible rather than blank. The style ids are keys into the data store's
`styleTable`, whose entries reference a `TST.CellStyleArchive` (fill) or a
`TSWP.ParagraphStyleArchive` (font); a cell without one takes the table's
body or header style. The layout is the one numbers-parser
(https://github.com/masaccio/numbers-parser) documents and decodes for Numbers
files; Keynote shares the TST archives with Numbers.

The look is read from the archives Keynote itself styles cells with: font
size, weight and colour from the body and header-row paragraph styles, fills
from the cell styles, and whether the table draws its gridlines.
"""

from __future__ import annotations

import base64
import struct
from array import array
from dataclasses import dataclass

DECIMAL128_BIAS = 0x1820
TYPE_EMPTY, TYPE_NUMBER, TYPE_TEXT, TYPE_RICH = 0, 2, 3, 9


@dataclass(frozen=True)
class Look:
    """How one kind of cell (body or header) is drawn."""
    font_size: float
    bold: bool
    color: str
    fill: str | None
    font: str


def _bytes(value) -> bytes:
    """keynote_parser hands bytes fields over base64-encoded."""
    if not value:
        return b""
    return base64.b64decode(value) if isinstance(value, str) else bytes(value)


def decimal128(buffer: bytes) -> float:
    exponent = (((buffer[15] & 0x7F) << 7) | (buffer[14] >> 1)) - DECIMAL128_BIAS
    mantissa = buffer[14] & 1
    for index in range(13, -1, -1):
        mantissa = mantissa * 256 + buffer[index]
    value = mantissa * 10 ** exponent
    return float(-value if buffer[15] & 0x80 else value)


def format_number(value: float) -> str:
    return str(int(value)) if value == int(value) else f"{value:g}"


def row_cells(row_info: dict, columns: int) -> list[bytes | None]:
    """The raw cell buffers of one row, None where the cell is empty."""
    buffer = _bytes(row_info.get("cellStorageBuffer"))
    offsets = array("h", _bytes(row_info.get("cellOffsets"))).tolist()
    if row_info.get("hasWideOffsets"):
        offsets = [offset * 4 for offset in offsets]
    cells: list[bytes | None] = []
    for column in range(columns):
        start = offsets[column] if column < len(offsets) else -1
        if start < 0:
            cells.append(None)
            continue
        later = [offset for offset in offsets[column + 1:] if offset >= 0]
        cells.append(buffer[start:later[0] if later else len(buffer)])
    return cells


@dataclass(frozen=True)
class RawCell:
    kind: int
    number: float | None
    string_id: int | None
    rich_id: int | None
    cell_style_id: int | None
    text_style_id: int | None


def parse_cell(cell: bytes) -> RawCell:
    flags = struct.unpack("<I", cell[8:12])[0]
    offset = 12
    values = {}
    for bit, name, size in ((0x1, "number", 16), (0x2, None, 8), (0x4, None, 8),
                            (0x8, "string_id", 4), (0x10, "rich_id", 4),
                            (0x20, "cell_style_id", 4), (0x40, "text_style_id", 4)):
        if not flags & bit:
            continue
        if name == "number":
            values[name] = decimal128(cell[offset:offset + 16])
        elif name:
            values[name] = struct.unpack("<i", cell[offset:offset + 4])[0]
        offset += size
    return RawCell(kind=cell[1], number=values.get("number"), string_id=values.get("string_id"),
                   rich_id=values.get("rich_id"), cell_style_id=values.get("cell_style_id"),
                   text_style_id=values.get("text_style_id"))


def cell_text(raw: RawCell | None, strings: dict, rich: dict) -> str:
    if raw is None or raw.kind == TYPE_EMPTY:
        return ""
    if raw.kind == TYPE_TEXT:
        return strings.get(raw.string_id, "")
    if raw.kind == TYPE_RICH:
        return rich.get(raw.rich_id, "")
    if raw.kind == TYPE_NUMBER and raw.number is not None:
        return format_number(raw.number)
    return f"<cell type {raw.kind}>"


def _color(color: dict | None) -> str | None:
    if not color or color.get("a", 1.0) == 0:
        return None
    return "#" + "".join(f"{round(color.get(channel, 0.0) * 255):02x}" for channel in "rgb")


def _property(registry: dict, ref: dict | None, group: str, name: str):
    """A style property, inherited up the `super.parent` chain when the
    style itself does not override it (Keynote styles are variations of a
    stylesheet's presets and only store their overrides)."""
    seen = set()
    while ref and ref.get("identifier") not in seen:
        seen.add(ref["identifier"])
        style = registry.get(ref["identifier"], {})
        value = style.get(group, {}).get(name)
        if value is not None:
            return value
        ref = style.get("super", {}).get("parent")
    return None


def _look(registry: dict, text: dict | None, cell: dict | None, bold_default: bool) -> Look:
    """The look of a cell drawn with these text and cell style references."""
    bold = _property(registry, text, "charProperties", "bold")
    fill = _property(registry, cell, "cellProperties", "cellFill") or {}
    return Look(font_size=_property(registry, text, "charProperties", "fontSize") or 18.0,
                bold=bold_default if bold is None else bold,
                color=_color(_property(registry, text, "charProperties", "fontColor")) or "#000000",
                fill=_color(fill.get("color")),
                font=_property(registry, text, "charProperties", "fontName") or "Titillium Web")


def _sizes(registry: dict, buckets, count: int, default: float) -> tuple[float, ...]:
    sizes = [default] * count
    for bucket in buckets:
        for header in registry.get(bucket.get("identifier"), {}).get("headers", []):
            if header.get("index", count) < count and header.get("size"):
                sizes[header["index"]] = header["size"]
    return tuple(sizes)


@dataclass(frozen=True)
class Cell:
    text: str
    look: Look


@dataclass(frozen=True)
class Grid:
    cells: tuple[tuple[Cell, ...], ...]
    column_widths: tuple[float, ...]
    row_heights: tuple[float, ...]
    body: Look
    header: Look
    gridlines: bool


def decode(registry: dict, model: dict) -> Grid:
    """Everything the render needs for one TST.TableModelArchive."""
    store = model["baseDataStore"]
    rows, columns = model.get("numberOfRows") or 0, model.get("numberOfColumns") or 0
    strings = {entry["key"]: entry.get("string", "")
               for entry in registry.get(store["stringTable"]["identifier"], {}).get("entries", [])}
    rich = {}
    for entry in registry.get(store.get("richTextTable", {}).get("identifier"), {}).get("entries", []):
        payload = registry.get(entry.get("richTextPayload", {}).get("identifier"), {})
        storage = registry.get(payload.get("storage", {}).get("identifier"), {})
        rich[entry["key"]] = "".join(storage.get("text", []))

    style_refs = {entry["key"]: entry.get("reference")
                  for entry in registry.get(store.get("styleTable", {}).get("identifier"), {}).get("entries", [])}

    row_buffers: list[list[bytes | None]] = []
    for tile in store.get("tiles", {}).get("tiles", []):
        for row_info in registry.get(tile["tile"]["identifier"], {}).get("rowInfos", []):
            row_buffers.append(row_cells(row_info, columns))
    stored_row = {}
    for bucket in store.get("rowHeaders", {}).get("buckets", []):
        for header in registry.get(bucket["identifier"], {}).get("headers", []):
            stored_row[header["index"]] = len(stored_row)

    header_rows = model.get("numberOfHeaderRows") or 0
    header_columns = model.get("numberOfHeaderColumns") or 0
    body = _look(registry, model.get("bodyTextStyle"), model.get("bodyCellStyle"), False)
    header = _look(registry, model.get("headerRowTextStyle"), model.get("headerRowStyle"), True)

    def cell_at(row: int, column: int) -> Cell:
        buffers = row_buffers[stored_row[row]] if row in stored_row and stored_row[row] < len(row_buffers) else []
        raw = parse_cell(buffers[column]) if column < len(buffers) and buffers[column] else None
        is_header = row < header_rows or column < header_columns
        default = header if is_header else body
        if raw is None or (raw.cell_style_id is None and raw.text_style_id is None):
            return Cell(cell_text(raw, strings, rich), default)
        text_ref = style_refs.get(raw.text_style_id) or model.get(
            "headerRowTextStyle" if is_header else "bodyTextStyle")
        cell_ref = style_refs.get(raw.cell_style_id) or model.get(
            "headerRowStyle" if is_header else "bodyCellStyle")
        return Cell(cell_text(raw, strings, rich), _look(registry, text_ref, cell_ref, is_header))

    table_style = registry.get(model.get("tableStyle", {}).get("identifier"), {}).get("tableProperties", {})
    return Grid(
        cells=tuple(tuple(cell_at(row, column) for column in range(columns)) for row in range(rows)),
        column_widths=_sizes(registry, [store.get("columnHeaders", {})], columns,
                             model.get("defaultColumnWidth") or 100.0),
        row_heights=_sizes(registry, store.get("rowHeaders", {}).get("buckets", []), rows,
                           model.get("defaultRowHeight") or 30.0),
        body=body,
        header=header,
        gridlines=bool(table_style.get("hStrokesVisible") or table_style.get("vStrokesVisible")),
    )
