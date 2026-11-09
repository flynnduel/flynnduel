import json

import mido
import pytest

from songtools.cli import main
from songtools.midi import write_midi


def test_midi_tempo_and_notes(tmp_path):
    out = write_midi([("G", 4), ("N.C.", 2), ("C", 4)], 96, tmp_path / "g.mid", key="G")
    mf = mido.MidiFile(out)
    msgs = [m for t in mf.tracks for m in t]
    assert any(m.type == "set_tempo" and m.tempo == mido.bpm2tempo(96) for m in msgs)
    assert any(m.type == "key_signature" for m in msgs)
    ons = [m.note for m in msgs if m.type == "note_on" and m.velocity > 0]
    assert ons == [43, 67, 71, 62, 36, 60, 64, 67]
    assert mf.ticks_per_beat == 480
    assert sum(m.time for m in msgs) == 10 * 480


def test_midi_slash_and_fractional(tmp_path):
    out = write_midi([("C/E", 1.5)], 100, tmp_path / "s.mid")
    msgs = [m for t in mido.MidiFile(out).tracks for m in t]
    assert [m.note for m in msgs if m.type == "note_on"] == [40, 60, 64, 67]
    assert sum(m.time for m in msgs) == 720


def _song(tmp_path, tempo=True, music="## Verse\nprogression: G:4 C:4\n## Chorus\nprogression: D:2 N.C.:2\n"):
    (tmp_path / "song.md").write_text("# T\n\n## Core\nkey: G\n" + ("tempo: 90\n" if tempo else ""))
    (tmp_path / "music.md").write_text(music)


def test_midi_cli(tmp_path, capsys):
    _song(tmp_path)
    assert main(["midi", str(tmp_path)]) == 0
    r = json.loads(capsys.readouterr().out)
    assert r["tempo"] == 90 and r["chords"] == 4 and r["beats"] == 12
    assert (tmp_path / "out" / "guide.mid").is_file()
    assert main(["midi", str(tmp_path), "--tempo", "120"]) == 0
    assert json.loads(capsys.readouterr().out)["tempo"] == 120


def test_midi_cli_errors(tmp_path, capsys):
    _song(tmp_path, tempo=False)
    assert main(["midi", str(tmp_path)]) == 2
    _song(tmp_path, music="## Verse\nprogression: Hx:4\n")
    assert main(["midi", str(tmp_path), "--tempo", "90"]) == 2
    err = capsys.readouterr().err
    assert "Hx" in err and "Verse" in err


def _notes(path):
    return [m.note for t in mido.MidiFile(path).tracks for m in t if m.type == "note_on" and m.velocity > 0]


def test_midi_concert_applies_capo(tmp_path, capsys):
    (tmp_path / "song.md").write_text("# T\n\n## Core\nkey: G\ncapo: 2\ntempo: 90\n")
    (tmp_path / "music.md").write_text("## Verse\nprogression: G:4 N.C.:2 C/E:4\n")
    assert main(["midi", str(tmp_path)]) == 0
    shape = json.loads(capsys.readouterr().out)
    assert shape["path"].endswith("guide.mid") and shape["capo_applied"] == 0
    assert main(["midi", str(tmp_path), "--concert"]) == 0
    r = json.loads(capsys.readouterr().out)
    assert r["path"].endswith("guide-concert.mid") and r["capo_applied"] == 2 and r["key"] == "A"
    assert r["chords"] == 3 and r["beats"] == 10
    assert [n % 12 for n in _notes(r["path"])] == [(n + 2) % 12 for n in _notes(shape["path"])]
    keys = [m.key for t in mido.MidiFile(r["path"]).tracks for m in t if m.type == "key_signature"]
    assert keys == ["A"]


def test_midi_concert_without_capo_is_unchanged(tmp_path, capsys):
    _song(tmp_path)
    assert main(["midi", str(tmp_path), "--concert"]) == 0
    r = json.loads(capsys.readouterr().out)
    assert r["capo_applied"] == 0 and r["key"] == "G"
    assert main(["midi", str(tmp_path)]) == 0
    capsys.readouterr()
    assert _notes(tmp_path / "out" / "guide-concert.mid") == _notes(tmp_path / "out" / "guide.mid")


def test_midi_concert_bad_capo(tmp_path, capsys):
    (tmp_path / "song.md").write_text("# T\n\n## Core\nkey: G\ncapo: two\ntempo: 90\n")
    (tmp_path / "music.md").write_text("## Verse\nprogression: G:4\n")
    assert main(["midi", str(tmp_path), "--concert"]) == 2
    assert "capo" in capsys.readouterr().err


def _concert(tmp_path, capsys, core, music):
    (tmp_path / "song.md").write_text("# T\n\n## Core\n" + core, encoding="utf-8")
    (tmp_path / "music.md").write_text(music, encoding="utf-8")
    assert main(["midi", str(tmp_path)]) == 0
    shape = json.loads(capsys.readouterr().out)
    assert main(["midi", str(tmp_path), "--concert"]) == 0
    return shape, json.loads(capsys.readouterr().out)


def _key_sigs(path):
    return [m.key for t in mido.MidiFile(path).tracks for m in t if m.type == "key_signature"]


def test_midi_concert_flat_key(tmp_path, capsys):
    # D shapes, capo 1: the band hears Eb (a flat key, spelled with flats)
    shape, r = _concert(tmp_path, capsys, "key: D\ncapo: 1\ntempo: 90\n", "## Verse\nprogression: D:4 G:4 A/C#:4\n")
    assert r["key"] == "Eb" and r["capo_applied"] == 1 and shape["key"] == "D"
    assert _key_sigs(r["path"]) == ["Eb"]
    assert [n % 12 for n in _notes(r["path"])] == [(n + 1) % 12 for n in _notes(shape["path"])]
    assert _notes(r["path"])[:4] == [36 + 3, 60 + 3, 60 + 7, 60 + 10]  # Eb major over an Eb bass


def test_midi_concert_minor_key(tmp_path, capsys):
    # Em shapes, capo 3: the band hears Gm
    shape, r = _concert(tmp_path, capsys, "key: Em\ncapo: 3\ntempo: 90\n", "## Verse\nprogression: Em:4 C:2 B7:2\n")
    assert r["key"] == "Gm" and r["capo_applied"] == 3
    assert _key_sigs(r["path"]) == ["Gm"] and _key_sigs(shape["path"]) == ["Em"]
    assert [n % 12 for n in _notes(r["path"])] == [(n + 3) % 12 for n in _notes(shape["path"])]


def test_midi_concert_capo_without_key(tmp_path, capsys):
    shape, r = _concert(tmp_path, capsys, "capo: 2\ntempo: 90\n", "## Verse\nprogression: G:4 Em:4\n")
    assert r["key"] is None and r["capo_applied"] == 2 and shape["key"] is None
    assert _key_sigs(r["path"]) == []
    assert [n % 12 for n in _notes(r["path"])] == [(n + 2) % 12 for n in _notes(shape["path"])]


def test_midi_unicode_key_and_chords(tmp_path, capsys):
    shape, r = _concert(tmp_path, capsys, "key: B♭\ncapo: 1\ntempo: 90\n", "## Verse\nprogression: B♭:4 E♭:4\n")
    assert shape["key"] == "Bb" and r["key"] == "B"
    assert _key_sigs(shape["path"]) == ["Bb"] and _key_sigs(r["path"]) == ["B"]
