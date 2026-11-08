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
