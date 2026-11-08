import json

import pytest

from songtools import chords
from songtools.chords import (QUALITIES, is_no_chord, names_for, parse_chord, spell, transpose)
from songtools.cli import main


def test_flat_input_and_key_aware_spelling():
    assert parse_chord("Bb").tones == ["Bb", "D", "F"]
    assert spell(10, "F") == "Bb" and spell(10, "E") == "A#"


def test_slash_chord_transposition_fixes_pychord_bug():
    assert transpose("G/B", 2) == "A/C#"
    assert transpose("C/Bb", 2, key="D") == "D/C"


@pytest.mark.parametrize("sym,pcs", [("Cadd9", {0, 4, 7, 2}), ("Dsus4", {2, 7, 9}),
                                     ("E7#9", {4, 8, 11, 2, 7}), ("Bbmaj7", {10, 2, 5, 9}),
                                     ("Gsus", {7, 0, 2})])
def test_parse_qualities(sym, pcs):
    assert parse_chord(sym).pcs == frozenset(pcs)


def test_gsus_is_sus4():
    assert parse_chord("Gsus").quality == "sus4"


def test_am7_and_c6_share_notes():
    names = names_for({9, 0, 4, 7}, bass_pc=9)
    assert names[0] == "Am7" and "C6/A" in names


def test_open_c_shape_x32210_names():
    names = names_for({0, 4, 9}, bass_pc=0)
    assert "Am/C" in names and "C6(no5)" in names


def test_names_deterministic_and_bass_root_first():
    a = names_for({0, 4, 7}, bass_pc=4)
    assert a == names_for({7, 4, 0}, bass_pc=4)
    assert "C/E" in a


def test_invalid_and_no_chord():
    assert is_no_chord("N.C.") and is_no_chord("NC") and is_no_chord("N/C")
    assert not is_no_chord("Am")
    for bad in ["H7", "", "C/", "Cxyz", "C/9"]:
        with pytest.raises(ValueError):
            parse_chord(bad)


def test_unicode_accidentals():
    c = parse_chord("B♭m7/F")
    assert c.root == "Bb" and c.bass == "F" and c.symbol == "Bbm7/F"


def test_fallback_to_qualities_table(monkeypatch):
    def boom(q):
        raise ValueError("no")
    monkeypatch.setattr(chords, "_pychord_intervals", boom)
    assert parse_chord("Gsus").pcs == frozenset({7, 0, 2})
    assert parse_chord("C7#9").pcs == frozenset({0, 4, 7, 10, 3})
    with pytest.raises(ValueError):
        parse_chord("Cm9")


def test_qualities_cover_brief():
    for q in ["", "m", "5", "6", "m6", "7", "maj7", "m7", "m7b5", "dim", "dim7", "aug", "sus2",
              "sus4", "add9", "9", "7#9", "7sus4", "69", "mmaj7", "11", "13"]:
        assert q in QUALITIES
    assert QUALITIES[""] == (0, 4, 7)


def test_cli_transpose_and_names(capsys):
    assert main(["chord", "transpose", "G/B", "2"]) == 0
    assert json.loads(capsys.readouterr().out)["result"] == "A/C#"
    assert main(["chord", "names", "C", "E", "A", "--bass", "C"]) == 0
    assert "Am/C" in json.loads(capsys.readouterr().out)["names"]
    assert main(["chord", "spell", "10", "--key", "F"]) == 0
    assert json.loads(capsys.readouterr().out)["name"] == "Bb"
    assert main(["chord", "parse", "Cadd9"]) == 0
    assert json.loads(capsys.readouterr().out)["tones"] == ["C", "E", "G", "D"]
    assert main(["--text", "chord", "parse", "Am7"]) == 0
    capsys.readouterr()


def test_cli_invalid_symbol_exit_2(capsys):
    assert main(["chord", "parse", "H7"]) == 2
    assert "H7" in capsys.readouterr().err


def test_music21_oracle_agrees_on_spelling():
    import music21
    for sym in ["Cadd9", "G/B", "Dsus4", "Am7", "C6", "E7#9", "Bm/A"]:
        ours = parse_chord(sym).pcs
        m21 = frozenset(p.pitchClass for p in music21.harmony.ChordSymbol(sym).pitches)
        assert ours == m21, sym


@pytest.mark.parametrize("sym,tones", [
    ("Cm", ["C", "Eb", "G"]), ("Fm", ["F", "Ab", "C"]), ("Gm7", ["G", "Bb", "D", "F"]),
    ("Dm7b5", ["D", "F", "Ab", "C"]), ("C7b9", ["C", "E", "G", "Bb", "Db"]),
    ("Cm9", ["C", "Eb", "G", "Bb", "D"]), ("C7b5", ["C", "E", "Gb", "Bb"]),
    ("E7#9", ["E", "G#", "B", "D", "G"]), ("Caug", ["C", "E", "G#"]),
    ("Bm", ["B", "D", "F#"]), ("F#m", ["F#", "A", "C#"]),
])
def test_tones_spelled_by_interval_letter(sym, tones):
    assert parse_chord(sym).tones == tones


def test_names_for_key_spelling():
    assert names_for({10, 2, 5, 9}, bass_pc=10, key="F")[0] == "Bbmaj7"
    assert names_for({10, 2, 5, 9}, bass_pc=10)[0] == "A#maj7"
    assert "Gm/Bb" in names_for({10, 2, 7}, bass_pc=10, key="F")


def test_transpose_no_chord_unchanged():
    assert transpose("N.C.", 3) == "N.C."
    assert transpose("NC", -2, key="F") == "NC"


@pytest.mark.parametrize("sym,same_as", [
    ("C+", "Caug"), ("Caug7", "C7#5"), ("C°7", "Cdim7"), ("C°", "Cdim"), ("Cø", "Cm7b5"),
    ("C6/9", "C69"), ("C7sus", "C7sus4"), ("C(9)", "Cadd9"), ("C6/9/E", "C69/E"),
])
def test_chart_aliases(sym, same_as):
    a, b = parse_chord(sym), parse_chord(same_as)
    assert a.pcs == b.pcs and a.quality == b.quality and a.symbol == b.symbol
