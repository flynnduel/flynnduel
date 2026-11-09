"""End-to-end: every subcommand on one original sample song, JSON and --text."""

import json
import shutil
from pathlib import Path

import pytest

from songtools.cli import main

FIXTURE = Path(__file__).parent / "fixtures" / "sample_song"

SUBCOMMANDS = [
    ["stability", "{d}/lyrics.md"], ["pov", "{d}/lyrics.md"], ["cliche", "{d}/lyrics.md", "--strict"],
    ["prosody", "{d}", "--section", "Verse 1", "--line", "1"], ["rhyme", "line", "time"],
    ["harmony", "--music", "{d}/music.md"],
    ["key", "--melody-low", "A2", "--melody-high", "E4",
     "--voice-low", "G2", "--voice-high", "D4", "--key", "G"],
    ["guitar", "identify", "x32010"], ["chart", "{d}", "--concert", "--pdf"], ["midi", "{d}"],
    ["drafts", "snapshot", "{d}"],
]


@pytest.fixture
def sample_dir(tmp_path):
    dest = tmp_path / "song"
    shutil.copytree(FIXTURE, dest)
    return dest


@pytest.mark.parametrize("argv", SUBCOMMANDS, ids=lambda a: a[0] + (" " + a[1] if a[0] == "guitar" else ""))
@pytest.mark.parametrize("text", [False, True])
def test_every_subcommand_runs_on_sample(argv, text, sample_dir, capsys):
    args = [a.format(d=sample_dir) for a in argv]
    assert main((["--text"] if text else []) + args) == 0
    out = capsys.readouterr().out
    if not text:
        json.loads(out)
    else:
        assert out.strip() and not out.lstrip().startswith("{")


def test_outputs_written(sample_dir):
    assert main(["chart", str(sample_dir), "--concert", "--pdf"]) == 0
    assert main(["midi", str(sample_dir)]) == 0
    for f in ["chart.cho", "chart-concert.cho", "chart.pdf", "chart-concert.pdf", "guide.mid"]:
        assert (sample_dir / "out" / f).exists()


def test_malformed_file_error_has_location(tmp_path, capsys):
    (tmp_path / "lyrics.md").write_text("## Verse\n[G broken\n")
    assert main(["stability", str(tmp_path / "lyrics.md")]) == 2
    assert "lyrics.md:2:" in capsys.readouterr().err


LIMIT = ("Scoring is a simplified version of Hayes (2005), whose model matched listeners' "
         "preferred settings about 70% of the time on folk-song data.")


def _json(argv, capsys):
    assert main(argv) == 0
    return json.loads(capsys.readouterr().out)


def test_prosody_values(sample_dir, capsys):
    argv = ["prosody", str(sample_dir), "--section", "Verse 1", "--line", "1"]
    r = _json(argv, capsys)
    assert len(r["slots"]) == 10 and r["source"] == "melody" and r["limit"] == LIMIT
    assert main(["--text"] + argv) == 0
    assert LIMIT in capsys.readouterr().out


def test_key_and_harmony_values(sample_dir, capsys):
    r = _json(["key", "--melody-low", "A2", "--melody-high", "E4", "--voice-low", "G2",
               "--voice-high", "D4", "--key", "G"], capsys)
    assert r["fits"][0]["key"] == "F" and r["fits"][0]["fits"] is True
    h = _json(["harmony", "--music", str(sample_dir / "music.md")], capsys)
    assert h["sections"]["Verse 1"]["key"]["tonic"] == "G"
    assert h["sections"]["Verse 1"]["key"]["mode"] == "major"
    assert h["sections"]["Verse 1"]["numerals"] == ["I", "IV", "V", "I"]
    assert h["sections"]["Chorus"]["dual_reading"]["tonic"] == "E"


def test_chart_check_on_fixture_matches_every_section(sample_dir, capsys):
    r = _json(["chart", str(sample_dir), "--check"], capsys)
    assert set(r["sections"]) == {"Verse 1", "Chorus", "Verse 2", "Bridge"}
    assert all(s["matches"] for s in r["sections"].values()) and r["matches"] is True
    assert r["only_in_lyrics"] == [] and r["only_in_music"] == []
    assert not (sample_dir / "out").exists()


def test_chart_and_midi_contents(sample_dir):
    assert main(["chart", str(sample_dir), "--concert", "--pdf"]) == 0
    assert main(["midi", str(sample_dir)]) == 0
    out = sample_dir / "out"
    plain, concert = (out / "chart.cho").read_text(), (out / "chart-concert.cho").read_text()
    assert plain != concert and "{capo: 2}" in plain and "{capo" not in concert
    for name in ("chart.pdf", "chart-concert.pdf"):
        assert (out / name).read_bytes().startswith(b"%PDF")
    assert (out / "guide.mid").read_bytes().startswith(b"MThd")


def test_guitar_and_chord_outputs_have_basis(capsys):
    assert "basis" in _json(["guitar", "identify", "x32010"], capsys)
    assert "basis" in _json(["chord", "parse", "Am7"], capsys)


def _closure(roots):
    import importlib.metadata as md
    from packaging.requirements import Requirement

    seen, todo = {}, list(roots)
    while todo:
        name = todo.pop().lower().replace("_", "-")
        if name in seen:
            continue
        dist = md.distribution(name)
        seen[name] = dist
        for r in dist.requires or []:
            req = Requirement(r)
            if req.marker is None or req.marker.evaluate({"extra": ""}):
                todo.append(req.name)
    return seen


def test_installed_size_under_budget():
    """Runtime dependency closure (extras excluded) plus the shipped data directory.

    Measured total: 32,874,776 bytes (pillow 20.4 MB, data 6.1 MB, reportlab 4.9 MB, rest <1.5 MB)."""
    from songtools.paths import data_dir

    dists = _closure(["pychord", "reportlab", "mido", "songtools"])
    assert {"pillow", "charset-normalizer", "packaging"} <= set(dists)
    total = sum(f.locate().stat().st_size for d in dists.values() for f in d.files or []
                if f.locate().exists() and f.locate().is_file())
    total += sum(p.stat().st_size for p in data_dir().rglob("*") if p.is_file())
    assert total < 40_000_000
