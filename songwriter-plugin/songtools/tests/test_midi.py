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
