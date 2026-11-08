"""Ordinary user mistakes end as exit 2 with {"error": ...} on stderr, never a traceback."""

import json
import shutil
from pathlib import Path

import pytest

from songtools.cli import main

FIXTURE = Path(__file__).parent / "fixtures" / "sample_song"
BAD_UTF8 = b"## Verse\nhello \xff world\n"


@pytest.fixture
def song(tmp_path):
    dest = tmp_path / "song"
    shutil.copytree(FIXTURE, dest)
    return dest


def _error(argv, capsys) -> str:
    assert main(argv) == 2
    return json.loads(capsys.readouterr().err)["error"]


@pytest.mark.parametrize("cmd", ["stability", "pov", "cliche"])
def test_lyrics_arg_is_a_directory(cmd, tmp_path, capsys):
    assert str(tmp_path) in _error([cmd, str(tmp_path)], capsys)


@pytest.mark.parametrize("cmd", ["stability", "pov", "cliche"])
def test_lyrics_arg_not_utf8(cmd, tmp_path, capsys):
    f = tmp_path / "lyrics.md"
    f.write_bytes(BAD_UTF8)
    assert "lyrics.md" in _error([cmd, str(f)], capsys)


@pytest.mark.parametrize("name,argv", [
    ("lyrics.md", ["chart", "{d}"]),
    ("music.md", ["midi", "{d}"]),
    ("song.md", ["chart", "{d}"]),
    ("lyrics.md", ["prosody", "{d}", "--section", "Verse 1", "--line", "1"]),
])
def test_song_dir_file_not_utf8(name, argv, song, capsys):
    (song / name).write_bytes(BAD_UTF8)
    assert name in _error([a.format(d=song) for a in argv], capsys)


def test_harmony_music_not_utf8(tmp_path, capsys):
    f = tmp_path / "music.md"
    f.write_bytes(BAD_UTF8)
    assert "music.md" in _error(["harmony", "--music", str(f)], capsys)


@pytest.mark.parametrize("cmd", ["chart", "midi"])
def test_out_exists_as_a_file(cmd, song, capsys):
    (song / "out").write_text("not a directory")
    assert "out" in _error([cmd, str(song)], capsys)


def test_pron_is_a_directory(tmp_path, capsys):
    assert str(tmp_path) in _error(["--pron", str(tmp_path), "rhyme", "line", "time"], capsys)


def test_pron_not_utf8(tmp_path, capsys):
    f = tmp_path / "pron.txt"
    f.write_bytes(b"word W ER1 D \xff\n")
    assert "pron.txt" in _error(["--pron", str(f), "rhyme", "line", "time"], capsys)


def test_drafts_diff_inputs_unreadable(song, tmp_path, capsys):
    bad = tmp_path / "bad.md"
    bad.write_bytes(BAD_UTF8)
    assert "bad.md" in _error(["drafts", "diff", str(bad), str(song / "lyrics.md")], capsys)
    assert str(tmp_path) in _error(["drafts", "diff", str(tmp_path), str(song / "lyrics.md")], capsys)


def test_cliche_extra_is_a_directory(song, tmp_path, capsys):
    assert str(tmp_path) in _error(["cliche", str(song / "lyrics.md"), "--extra", str(tmp_path)], capsys)


def test_snapshot_reads_source_before_creating_drafts(song, capsys, monkeypatch):
    calls = []
    real_mkdir = Path.mkdir

    def boom(self):
        calls.append("read")
        raise PermissionError(13, "Permission denied")

    def mkdir(self, *a, **k):
        calls.append("mkdir")
        return real_mkdir(self, *a, **k)

    monkeypatch.setattr(Path, "read_bytes", boom)
    monkeypatch.setattr(Path, "mkdir", mkdir)
    assert "lyrics.md" in _error(["drafts", "snapshot", str(song)], capsys)
    assert calls == ["read"] and not (song / "drafts").exists()


def test_cut_tolerates_non_utf8_cuts_file(song, capsys):
    (song / "cuts").mkdir()
    (song / "cuts" / "cuts.md").write_bytes(b"## old \xff entry\nline")
    assert main(["drafts", "cut", str(song), "a cut line", "--reason", "too long"]) == 0
    data = (song / "cuts" / "cuts.md").read_bytes()
    assert data.startswith(b"## old \xff entry\nline\n\n## ") and data.endswith(b"a cut line\n")


def test_partial_capo_mask_must_match_tuning_strings(monkeypatch, capsys):
    from songtools import fretboard

    four = fretboard.Tuning("four", [43, 48, 52, 57])
    monkeypatch.setattr(fretboard, "load_tuning", lambda name: four)
    err = _error(["guitar", "identify", "x32010", "--capo", "2", "--partial-capo", "111100"], capsys)
    assert "--partial-capo" in err and "4" in err


@pytest.mark.parametrize("argv", [
    ["prosody", ".", "--section", "Verse", "--line", "two"],
    ["chord", "spell", "G7"],
    ["no-such-command"],
    [],
])
def test_usage_errors_are_json(argv, capsys):
    assert main(argv) == 2
    captured = capsys.readouterr()
    err = json.loads(captured.err)
    assert set(err) == {"error"} and err["error"]
    assert "usage:" not in captured.err
