"""PDF lead sheet rendering (reportlab, Lato OFL): US Letter, chords above lyrics."""

import io
import re
from dataclasses import dataclass
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from songtools.chordpro import ChordProSong
from songtools.paths import data_dir

BASIS = "lead sheet rendering (reportlab, Lato OFL)"
REGULAR, BOLD = "Lato", "Lato-Bold"
MARGIN = 54
_CHORD = re.compile(r"\[([^\]]*)\]")


def _register_fonts() -> None:
    if REGULAR not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(REGULAR, str(data_dir() / "fonts" / "Lato-Regular.ttf")))
    if BOLD not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(BOLD, str(data_dir() / "fonts" / "Lato-Bold.ttf")))


def chord_positions(line: str, font: str, size: float) -> tuple[str, list[tuple[float, str]]]:
    """Lyric text and (x offset, chord) pairs; x is the width of the lyric before the chord."""
    _register_fonts()
    lyric, positions, pos = [], [], 0
    for m in _CHORD.finditer(line):
        lyric.append(line[pos:m.start()])
        positions.append((m.group(1).strip(), len("".join(lyric))))
        pos = m.end()
    lyric.append(line[pos:])
    text = "".join(lyric)
    return text, [(float(pdfmetrics.stringWidth(text[:off], font, size)), sym) for sym, off in positions]


def _chord_offsets(line: str) -> list[str]:
    """Lyric prefix before each chord, parallel to chord_positions' chords."""
    out, pos, acc = [], 0, ""
    for m in _CHORD.finditer(line):
        acc += line[pos:m.start()]
        out.append(acc)
        pos = m.end()
    return out


@dataclass
class Op:
    x: float
    y: float
    text: str
    font: str
    size: float


_COMMENTS = {"comment", "c", "comment_italic", "ci", "comment_box", "cb"}
_DIRECTIVE = re.compile(r"^\{\s*([A-Za-z_]+)\s*(?::\s*(.*?))?\s*\}$")
TEXT_W = letter[0] - 2 * MARGIN


def _width(text: str, font: str, size: float) -> float:
    return float(pdfmetrics.stringWidth(text, font, size))


def _segments(text: str, maxw: float, font: str, size: float) -> list[tuple[int, int]]:
    """(start, end) character spans, each at most maxw wide; breaks at spaces when it can."""
    spans, start = [], 0
    while True:
        if _width(text[start:].rstrip(), font, size) <= maxw:
            spans.append((start, len(text)))
            return spans
        end = start + 1
        while end < len(text) and _width(text[start:end + 1].rstrip(), font, size) <= maxw:
            end += 1
        space = text.rfind(" ", start + 1, end + 1)
        if space > start:
            end = space
        nxt = end
        while nxt < len(text) and text[nxt] == " ":
            nxt += 1
        spans.append((start, nxt))
        start = nxt


def layout_song(song: ChordProSong) -> list[list[Op]]:
    """Pages of positioned text (origin bottom-left); render_pdf_bytes just draws these."""
    _register_fonts()
    height = letter[1]
    pages: list[list[Op]] = [[]]
    y = height - MARGIN

    def new_page() -> None:
        nonlocal y
        pages.append([])
        y = height - MARGIN

    def need(h: float) -> None:
        if y - h < MARGIN:
            new_page()

    def put(x: float, text: str, font: str, size: float) -> None:
        pages[-1].append(Op(MARGIN + x, y, text, font, size))

    title = song.meta.get("title", "")
    if title:
        size = 18.0
        while size > 10 and _width(title, BOLD, size) > TEXT_W:
            size -= 1
        lines = [title]
        if _width(title, BOLD, size) > TEXT_W:
            lines = [title[a:b].rstrip() for a, b in _segments(title, TEXT_W, BOLD, size)]
        for t in lines:
            y -= size
            put(0, t, BOLD, size)
        y -= 6
    info = [f"{label}: {song.meta[k]}" for k, label in (("key", "Key"), ("capo", "Capo"), ("tempo", "Tempo"))
            if song.meta.get(k)]
    if info:
        y -= 12
        put(0, "   ".join(info), REGULAR, 10)
    y -= 10

    for section in song.sections:
        need(14 + 28)
        y -= 10
        if section.label or section.kind != "other":
            y -= 13
            put(0, section.label or section.kind.capitalize(), BOLD, 11)
            y -= 4
        for line in section.lines:
            m = _DIRECTIVE.match(line)
            if m:
                name = m.group(1).lower()
                if name in ("new_page", "np"):
                    new_page()
                elif name in _COMMENTS and m.group(2):
                    need(15)
                    y -= 15
                    put(0, m.group(2), REGULAR, 10)
                    y -= 2
                continue  # other directives are metadata
            lyric, chords = chord_positions(line, REGULAR, 11)
            offsets = [len(t) for t in _chord_offsets(line)]
            spans = _segments(lyric, TEXT_W, REGULAR, 11)
            for si, (a, b) in enumerate(spans):
                last = si == len(spans) - 1
                row = [(_width(lyric[a:off], REGULAR, 11), sym)
                       for (_, sym), off in zip(chords, offsets)
                       if a <= off < b or (last and off >= b)]
                need(14 + (12 if row else 0))
                if row:
                    y -= 12
                    x_min = 0.0
                    for x, sym in row:
                        face = REGULAR if sym.startswith("*") else BOLD
                        label = sym.lstrip("*").strip()
                        w = _width(label, face, 10)
                        x = max(min(x, TEXT_W - w), x_min)
                        put(x, label, face, 10)
                        x_min = x + w + 4
                seg = lyric[a:b].rstrip()
                if seg.strip():
                    y -= 14 if row else 15
                    put(0, seg, REGULAR, 11)
                y -= 2
    return pages


def render_pdf(song: ChordProSong, out: Path) -> Path:
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(render_pdf_bytes(song))
    return out


def render_pdf_bytes(song: ChordProSong, compress: bool = True) -> bytes:
    pages = layout_song(song)
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, pageCompression=1 if compress else 0)
    c.setTitle(song.meta.get("title") or "Lead sheet")
    for i, page in enumerate(pages):
        if i:
            c.showPage()
        for op in page:
            c.setFont(op.font, op.size)
            c.drawString(op.x, op.y, op.text)
    c.save()
    return buf.getvalue()
