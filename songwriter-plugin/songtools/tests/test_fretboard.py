import json

import pytest

from songtools.cli import SongtoolsError, main
from songtools.fretboard import (Capo, Tuning, capo_options, identify, joni_code, load_tuning, parse_shape,
                                 sounding, verify, vsystem, voicings)

STD = load_tuning("standard")


def test_open_c_sounds_and_identifies():
    sh = parse_shape("x32010")
    assert sounding(sh, STD) == [None, 48, 52, 55, 60, 64]
    assert identify(sh, STD)[0] == "C"


def test_capo_two_am_shape_is_bm():
    assert identify(parse_shape("x02210"), STD, Capo(2))[0] == "Bm"


def test_partial_capo_esus():                          # A, D, G strings clamped at 2
    assert "Esus4" in identify(parse_shape("000000"), STD, Capo(2, (False, True, True, True, False, False)))


def test_verify_reports_extra_tone_and_alternative():
    v = verify(parse_shape("x32000"), "C", STD)
    assert not v.ok and v.extra == ["B"] and "Cmaj7" in v.alternatives


def test_verify_allows_missing_fifth():
    assert verify(parse_shape("x3201x"), "C", STD).ok


def test_verify_missing_third_not_allowed():
    v = verify(parse_shape("x3x01x"), "C", STD)       # C G C: no third
    assert not v.ok and v.missing == ["E"]
    assert verify(parse_shape("x32x1x"), "C", STD).ok  # C E C: fifth omitted


def test_verify_missing_root_cases():
    sh = parse_shape("xx20xx")                        # E3, G3 only: C is missing
    v = verify(sh, "C", STD)
    assert not v.ok and v.missing == ["C"]
    assert verify(sh, "C", STD, band_bass=True).ok


def test_verify_slash_chord_needs_bass():
    assert verify(parse_shape("032010"), "C/E", STD).ok
    assert not verify(parse_shape("x32010"), "C/E", STD).ok


def test_verify_flat_root_spelling():
    v = verify(parse_shape("x13331"), "Bb", STD)
    assert v.ok
    v = verify(parse_shape("x1333x"), "Bbm", STD)
    assert not v.ok and v.extra == ["D"] and v.missing == ["Db"]


def test_verify_bad_name():
    with pytest.raises(SongtoolsError):
        verify(parse_shape("x32010"), "Hmaj", STD)


def test_parse_shape_forms():
    assert parse_shape("x32010") == [None, 3, 2, 0, 1, 0]
    assert parse_shape("x 10 12 12 12 10") == [None, 10, 12, 12, 12, 10]
    assert parse_shape("x,10,12,12,12,10") == [None, 10, 12, 12, 12, 10]


@pytest.mark.parametrize("bad", ["x3201", "x3201q", "", "x 3 2 0 1 0 0", "-1 3 2 0 1 0 0"])
def test_parse_shape_errors(bad):
    with pytest.raises(SongtoolsError):
        parse_shape(bad)


@pytest.mark.parametrize("notes,group", [
    ([60, 64, 67, 71], "V-1"), ([55, 60, 64, 71], "V-2"), ([52, 60, 67, 71], "V-4"),
    ([48, 55, 64, 71], "V-5"), ([56, 63, 64, 71], "V-2")])   # last: Hober's Emaj7 example
def test_vsystem_groups(notes, group):
    assert vsystem(notes) == group


@pytest.mark.parametrize("notes,group", [
    ([36, 52, 55, 59], "V-6"), ([48, 52, 67, 71], "V-13"), ([48, 52, 55, 71], "V-14"),
    ([52, 60, 67, 83], "V-11")])
def test_vsystem_wide_gaps(notes, group):
    assert vsystem(notes) == group


def test_vsystem_needs_four_distinct_pcs():
    assert vsystem([48, 52, 55, 60]) is None


def test_vsystem_ignores_input_order():
    assert vsystem([71, 60, 64, 67]) == "V-1"


@pytest.mark.parametrize("name,code", [("standard", "E55545"), ("dadgad", "D75525"), ("open_g", "D57543")])
def test_joni_codes(name, code):
    assert joni_code(load_tuning(name)) == code


def test_load_tuning_notes_and_errors():
    t = load_tuning("D2 A2 D3 G3 A3 D4")
    assert t == Tuning("D2 A2 D3 G3 A3 D4", load_tuning("dadgad").strings)
    assert load_tuning("Open G").strings == load_tuning("open_g").strings
    for bad in ("nonsense", "E2 A2 D3", "E2 A2 D3 G3 B3 H4"):
        with pytest.raises(SongtoolsError):
            load_tuning(bad)


def test_capo_search_finds_open_shapes_for_flat_keys():
    top = capo_options(["Bb", "Eb", "F"], STD)[0]
    assert top.fret in (1, 3) and top.open_shapes == 3


def test_capo_options_sorted_and_noted():
    opts = capo_options(["G", "C", "D"], STD, max_fret=8)
    assert opts[0].fret == 0 and opts[0].open_shapes == 3
    assert [(o.open_shapes, -o.fret) for o in opts] == sorted([(o.open_shapes, -o.fret) for o in opts], reverse=True)
    assert all(o.note == "" for o in opts if o.fret < 7)
    assert all("soft heuristic" in o.note for o in opts if o.fret >= 7)
    assert opts[0].shapes == ["G", "C", "D"]


def test_voicings_from_chords_db():
    assert "x32010" in voicings("C", STD)
    assert len(voicings("C", STD, limit=2)) == 2


def test_voicings_alt_tuning_generated():
    dadgad = load_tuning("dadgad")
    vs = voicings("Dsus4", dadgad)
    assert vs and all(identify(parse_shape(v), dadgad)[0] == "Dsus4" for v in vs)


def test_cli_roundtrip(capsys):
    assert main(["guitar", "identify", "x02210", "--capo", "2"]) == 0
    assert json.loads(capsys.readouterr().out)["names"][0] == "Bm"
    assert main(["guitar", "identify", "000000", "--capo", "2", "--partial-capo", "011100"]) == 0
    assert "Esus4" in json.loads(capsys.readouterr().out)["names"]
    assert main(["guitar", "verify", "x32000", "C"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["ok"] is False and out["extra"] == ["B"]
    assert main(["guitar", "vsystem", "60", "64", "67", "71"]) == 0
    assert json.loads(capsys.readouterr().out)["group"] == "V-1"
    assert main(["guitar", "joni", "--tuning", "dadgad"]) == 0
    assert json.loads(capsys.readouterr().out)["code"] == "D75525"
    assert main(["guitar", "capo", "Bb", "Eb", "F"]) == 0
    assert json.loads(capsys.readouterr().out)["options"][0]["open_shapes"] == 3
    assert main(["guitar", "voicings", "C", "--limit", "3"]) == 0
    assert len(json.loads(capsys.readouterr().out)["voicings"]) == 3
    assert main(["--text", "guitar", "verify", "x32000", "C"]) == 0
    assert "B" in capsys.readouterr().out


def test_cli_errors(capsys):
    assert main(["guitar", "identify", "x3201"]) == 2
    assert main(["guitar", "identify", "x32010", "--tuning", "bogus"]) == 2
    assert main(["guitar", "identify", "x32010", "--partial-capo", "0111"]) == 2
    assert main(["guitar", "verify", "x32010", "Hx"]) == 2


def test_partial_capo_unclamped_frets_are_physical():
    cap = Capo(2, (True, False, False, False, False, False))
    assert sounding(parse_shape("010000"), STD, cap) == [42, 46, 50, 55, 59, 64]
    assert sounding(parse_shape("032000"), STD, cap) == [42, 48, 52, 55, 59, 64]


def test_sounding_validates_mask_length_even_without_open_strings():
    with pytest.raises(ValueError):
        sounding(parse_shape("x32010"), STD, Capo(2, (True, False, True)))
    with pytest.raises(ValueError):
        sounding(parse_shape("111111"), STD, Capo(2, (True,) * 7))


@pytest.mark.parametrize("n", ["-1", "13"])
def test_cli_capo_range(n, capsys):
    assert main(["guitar", "identify", "x32010", "--capo", n]) == 2
