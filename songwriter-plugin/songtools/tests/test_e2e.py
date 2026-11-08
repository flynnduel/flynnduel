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


def test_installed_size_under_budget():
    import importlib.metadata as md

    runtime = {"pychord", "reportlab", "mido", "songtools"}
    total = sum(f.locate().stat().st_size for d in md.distributions()
                if d.metadata["Name"].lower() in runtime for f in d.files or [] if f.locate().exists())
    assert total < 25_000_000
