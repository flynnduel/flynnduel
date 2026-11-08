import json

import pytest

from songtools.chords import parse_chord
from songtools.cli import SongtoolsError, main
from songtools.harmony import BASIS, CORPUS, analyze, analyze_song, nashville, numeral


def test_major_functional():
    a = analyze(["G", "C", "D", "G"])
    assert (a.key.tonic, a.key.mode, a.system) == ("G", "major", "1a")
    assert a.numerals == ["I", "IV", "V", "I"] and a.nashville == ["1", "4", "5", "1"]
    assert "simplified" in a.system_label and "Everett 2004, Table 1" in a.system_label


def test_mixolydian_double_plagal():
    a = analyze(["G", "F", "C", "G"])
    assert a.numerals == ["I", "bVII", "IV", "I"] and a.system == "2"
    assert any("double-plagal" in n for n in a.notes)


def test_mixture_with_dominant():
    assert analyze(["G", "F", "C", "G", "D", "G"], key="G").system == "3a"


def test_axis_loop_dual_reading_major_bias():
    a = analyze(["C", "G", "Am", "F"])
    assert a.key.tonic == "C" and a.key.mode == "major"
    assert a.dual_reading and a.dual_reading["tonic"] == "A"
    assert a.dual_reading["mode"] == "minor" and a.dual_reading["numerals"][0] == "i"


def test_blues_and_power_chord_systems():
    assert analyze(["A7", "D7", "A7", "E7"]).system == "4"
    assert analyze(["E5", "G5", "A5", "E5"]).system == "5"


def test_minor_with_major_v_is_1b():
    a = analyze(["Am", "Dm", "E", "Am"])
    assert (a.key.tonic, a.key.mode, a.system) == ("A", "minor", "1b")
    assert a.numerals == ["i", "iv", "V", "i"]


def test_aeolian_without_v_is_system_2_and_chromatic_6a():
    a = analyze(["Am", "F", "G", "Am"])
    assert a.key.mode == "minor" and a.system == "2" and a.numerals[1:3] == ["bVI", "bVII"]
    assert analyze(["C", "E", "A", "Eb", "C"], key="C").system == "6a"


def test_invalid_chords_reported_and_nc_skipped():
    a = analyze(["G", "N.C.", "H7", "C", "G"])
    assert a.errors == ["H7"] and a.numerals == ["I", "IV", "I"]


def test_cadence_note_and_ambiguity_flag():
    a = analyze(["G", "C", "D", "G"])
    assert any(n.startswith("V–I is still the most common chorus-ending cadence (32%)") for n in a.notes)
    assert not any("double-plagal" in n for n in a.notes)


def test_explicit_key_and_bad_key():
    a = analyze(["Am", "G"], key="A dorian")
    assert (a.key.tonic, a.key.mode, a.confidence, a.dual_reading) == ("A", "dorian", 1.0, None)
    assert analyze(["Em", "D"], key="Em").key.mode == "minor"
    for bad in ("H", "G lydian", ""):
        with pytest.raises(SongtoolsError):
            analyze(["G"], key=bad)
    with pytest.raises(SongtoolsError):
        analyze(["N.C."])


def test_numeral_and_nashville_forms():
    cases = {
        "Am": ("vi", "6m"), "G7": ("V7", "57"), "Cmaj7": ("Imaj7", "1maj7"), "Bdim": ("vii°", "7°"),
        "Bm7b5": ("viiø", "7ø"), "Bb": ("bVII", "b7"), "Ab": ("bVI", "b6"), "Fsus4": ("IVsus4", "4sus4"),
        "C/E": ("I/3", "1/3"), "F#dim": ("#iv°", "#4°"), "Eb": ("bIII", "b3"), "Db": ("bII", "b2"),
    }
    for sym, (rn, nn) in cases.items():
        c = parse_chord(sym)
        assert numeral(c, "C") == rn, sym
        assert nashville(c, "C") == nn, sym
    assert numeral(parse_chord("F"), "G") == "bVII"
    assert nashville(parse_chord("E5"), "E") == "1(5)"


def test_corpus_and_basis():
    assert CORPUS["root_share"]["I"] == 32.8 and CORPUS["chorus_cadence_pre_tonic"] == {"V": 32.0, "IV": 18.5}
    assert "Richards loop major bias" in BASIS


def test_truck_driver_lift():
    r = analyze_song({"Chorus 1": [("C", 4), ("F", 4), ("G", 4), ("C", 4)],
                      "Chorus 2": [("D", 4), ("G", 4), ("A", 4), ("D", 4)]})
    assert any("truck-driver lift (Everett 3b)" in m for m in r["modulations"])
    assert r["sections"]["Chorus 2"]["key"]["tonic"] == "D"


def test_analyze_song_skips_empty_sections():
    r = analyze_song({"Verse": [("G", 4), ("C", 4), ("D", 4), ("G", 4)], "Bridge": [("N.C.", 4)]})
    assert list(r["sections"]) == ["Verse"] and r["skipped"] == ["Bridge"]


def test_music21_oracle_numerals_in_major():
    music21 = pytest.importorskip("music21")
    rn = music21.roman.romanNumeralFromChord(music21.chord.Chord(["F3", "A3", "C4"]),
                                                  music21.key.Key("G"))  # octaves: bare names get an arbitrary inversion
    assert rn.figure in ("bVII", "-VII") and numeral(parse_chord("F"), "G") == "bVII"


def test_cli_chords_and_music_file(capsys, tmp_path):
    assert main(["harmony", "G", "C", "D", "G", "--key", "G"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["numerals"] == ["I", "IV", "V", "I"] and out["corpus"]["root_share"]["I"] == 32.8
    assert out["key"]["tonic"] == "G" and out["basis"] == BASIS
    f = tmp_path / "music.md"
    f.write_text("## Verse\nprogression: G:4 C:4 D:4 G:4\n")
    assert main(["harmony", "--music", str(f)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["sections"]["Verse"]["system"] == "1a" and out["modulations"] == []
    assert main(["--text", "harmony", "C", "G", "Am", "F"]) == 0
    assert "C major" in capsys.readouterr().out


def test_cli_errors(capsys, tmp_path):
    assert main(["harmony", "G", "--key", "H"]) == 2
    assert main(["harmony"]) == 2
    assert main(["harmony", "G", "--music", str(tmp_path / "x.md")]) == 2
    assert main(["harmony", "--music", str(tmp_path / "missing.md")]) == 2
