from songtools.chordpro import parse
from songtools.pdf import chord_positions, render_pdf


def test_chord_positions_monotonic():
    text, pos = chord_positions("[G]I was walking [C]down", "Lato", 11)
    assert text == "I was walking down" and pos[0] == (0.0, "G") and pos[1][0] > 0


def test_render_pdf_with_unicode(tmp_path):
    s = parse("{title: Señor — “Test”}\n{start_of_verse}\n[G]Ñandú — “quoted”\n{end_of_verse}\n")
    out = render_pdf(s, tmp_path / "c.pdf")
    data = out.read_bytes()
    assert data.startswith(b"%PDF") and data.count(b"/Type /Page") >= 1


def test_render_pdf_paginates_and_edge_lines(tmp_path):
    lines = "\n".join(f"[G]line {i} [*Slowly]here" for i in range(120)) + "\n[C] [D]\nplain"
    s = parse(f"{{title: Long}}\n{{key: G}}\n{{capo: 2}}\n{{tempo: 90}}\n{{start_of_verse: V}}\n{lines}\n{{end_of_verse}}\n")
    out = render_pdf(s, tmp_path / "long.pdf")
    assert out.read_bytes().count(b"/Type /Page\n") + out.read_bytes().count(b"/Type /Page ") >= 2


def test_chart_pdf_cli(tmp_path):
    from songtools.cli import main
    (tmp_path / "song.md").write_text("# T\n\n## Core\nkey: G\ncapo: 2\ntempo: 90\ntime: 4/4\n")
    (tmp_path / "lyrics.md").write_text("## Verse 1\n[G]hello [C]world\n")
    assert main(["chart", str(tmp_path), "--concert", "--pdf"]) == 0
    assert (tmp_path / "out" / "chart.pdf").read_bytes().startswith(b"%PDF")
    assert (tmp_path / "out" / "chart-concert.pdf").is_file()


import re

from songtools.pdf import MARGIN, layout_song, render_pdf_bytes
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics


def _ops(src):
    return [op for page in layout_song(parse(src)) for op in page]


def test_comment_cues_rendered_and_new_page():
    src = ("{title: T}\n{start_of_verse: V}\n{comment: Play softly}\n{ci: Whisper}\n{cb: Boxed}\n"
           "[G]one\n{new_page}\n[C]two\n{key: D}\n{end_of_verse}\n")
    pages = layout_song(parse(src))
    texts = [op.text for page in pages for op in page]
    assert {"Play softly", "Whisper", "Boxed"} <= set(texts)
    assert len(pages) == 2 and "two" in [op.text for op in pages[1]]


def test_annotation_no_asterisk_regular_face():
    ops = _ops("{start_of_verse}\n[G]hi [*Slowly]there\n{end_of_verse}\n")
    ann = [op for op in ops if op.text == "Slowly"]
    assert ann and ann[0].font == "Lato"
    assert not any("*" in op.text for op in ops)
    assert [op.font for op in ops if op.text == "G"] == ["Lato-Bold"]


def test_long_lines_wrap_within_margin_and_keep_chords():
    words = " ".join(f"word{i}" for i in range(60))
    ops = _ops("{title: " + "Very long title " * 8 + "}\n{start_of_verse}\n[G]" + words
               + " [C]tail\n{end_of_verse}\n")
    right = letter[0] - MARGIN + 0.01
    for op in ops:
        assert op.x + pdfmetrics.stringWidth(op.text, op.font, op.size) <= right, op.text
    assert [op.text for op in ops if op.font == "Lato-Bold" and op.size == 10 and len(op.text) == 1] == ["G", "C"]
    tail = next(op for op in ops if op.text == "C")
    assert any(o.text.endswith("tail") and o.y == tail.y - 14 for o in ops)


def test_pdf_embeds_lato_and_counts_pages(tmp_path):
    s = parse("{title: Señor}\n{start_of_verse}\n" + "\n".join(f"[G]l{i}" for i in range(150))
              + "\n{end_of_verse}\n")
    data = render_pdf_bytes(s, compress=False)
    assert b"Lato" in data and b"/FontFile2" in data
    assert len(re.findall(rb"/Type /Page(?!s)", data)) >= 2


def test_pdf_never_drops_an_accidental():
    # Lato has no sharp or flat glyph: a dropped one prints B for B♭ on the band's chart
    ops = _ops("{title: B♭ blues}\n{key: B♭}\n{start_of_verse: In E♭}\n{comment: to F♯}\n"
               "[B♭]one [F♯m7]two [A♭/E♭]three ♭ and ♯\n{end_of_verse}\n")
    texts = [op.text for op in ops]
    assert not any("♭" in t or "♯" in t for t in texts)
    assert {"Bb", "F#m7", "Ab/Eb", "Bb blues", "Key: Bb", "In Eb", "to F#"} <= set(texts)
    assert "one two three b and #" in texts


def test_pdf_accidental_chords_keep_their_place():
    plain = _ops("{start_of_verse}\n[Bb]one [F#m]two\n{end_of_verse}\n")
    uni = _ops("{start_of_verse}\n[B♭]one [F♯m]two\n{end_of_verse}\n")
    assert [(o.x, o.y, o.text) for o in uni] == [(o.x, o.y, o.text) for o in plain]
