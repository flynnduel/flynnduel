"""PDF lead sheet rendering (reportlab, Lato OFL): US Letter, chords above lyrics."""

import io
import re
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


def render_pdf(song: ChordProSong, out: Path) -> Path:
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(render_pdf_bytes(song))
    return out


def render_pdf_bytes(song: ChordProSong) -> bytes:
    _register_fonts()
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter
    y = height - MARGIN

    def need(h: float) -> None:
        nonlocal y
        if y - h < MARGIN:
            c.showPage()
            y = height - MARGIN

    title = song.meta.get("title", "")
    c.setTitle(title or "Lead sheet")
    if title:
        c.setFont(BOLD, 18)
        y -= 18
        c.drawString(MARGIN, y, title)
        y -= 6
    info = [f"{label}: {song.meta[k]}" for k, label in (("key", "Key"), ("capo", "Capo"), ("tempo", "Tempo"))
            if song.meta.get(k)]
    if info:
        c.setFont(REGULAR, 10)
        y -= 12
        c.drawString(MARGIN, y, "   ".join(info))
    y -= 10

    for section in song.sections:
        need(14 + 28)
        y -= 10
        if section.label or section.kind != "other":
            c.setFont(BOLD, 11)
            y -= 13
            c.drawString(MARGIN, y, section.label or section.kind.capitalize())
            y -= 4
        for line in section.lines:
            if line.startswith("{"):
                continue
            lyric, chords = chord_positions(line, REGULAR, 11)
            need(14 + (12 if chords else 0))
            if chords:
                y -= 12
                c.setFont(BOLD, 10)
                x_min = 0.0
                for x, sym in chords:
                    x = max(x, x_min)
                    c.drawString(MARGIN + x, y, sym)
                    x_min = x + pdfmetrics.stringWidth(sym, BOLD, 10) + 4
            if lyric.strip():
                y -= 14 if chords else 15
                c.setFont(REGULAR, 11)
                c.drawString(MARGIN, y, lyric)
            y -= 2
    c.save()
    return buf.getvalue()
