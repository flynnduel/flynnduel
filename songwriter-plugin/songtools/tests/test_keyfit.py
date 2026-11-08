import json

import pytest

from songtools.cli import SongtoolsError, main
from songtools.keyfit import BASIS, KeyFit, capo_for, fit_keys, midi_to_note, note_to_midi


def test_note_midi_roundtrip():
    assert note_to_midi("A2") == 45 and midi_to_note(61, "F") == "Db4"


def test_note_to_midi_rejects_garbage():
    with pytest.raises(ValueError):
        note_to_midi("H2")
    with pytest.raises(ValueError):
        note_to_midi("C")


def test_lower_voice_moves_key_down():
    top = fit_keys("A2", "E4", "G2", "D4", "G")[0]
    assert (top.key, top.shift, top.fits) == ("F", -2, True)
    assert (top.low, top.high, top.margin_low, top.margin_high) == ("G2", "D4", 0, 0)


def test_minor_suffix_and_spelling():
    top = fit_keys("A2", "E4", "G2", "D4", "Em")[0]
    assert top.key == "Dm"
    sharps = [f.key for f in fit_keys("A2", "E4", "G2", "D4", "Em")]
    assert "C#m" in sharps and "Dbm" not in sharps
    assert "Bb" in [f.key for f in fit_keys("A2", "E4", "G2", "D4", "G")]


def test_fits_sort_before_distance_and_tessitura_used():
    fits = fit_keys("A2", "E4", "C2", "C6", "G")
    assert all(f.fits for f in fits) and len(fits) == 13
    assert fits[0].shift == 0 or abs(fits[0].tessitura_offset) <= abs(fits[1].tessitura_offset)
    # tessitura (midpoint 62.0 vs voice midpoint 62.0 at shift -2) overrides the melody midpoint
    up = fit_keys("A2", "E4", "C2", "C6", "G", tessitura=("C4", "E4"))[0]
    base = fit_keys("A2", "E4", "C2", "C6", "G")[0]
    assert (up.shift, up.tessitura_offset) == (-2, 0.0) and base.shift != up.shift


def test_capo_options_for_f():
    assert {(1, "E"), (3, "D"), (5, "C")} <= set(capo_for("F"))
    assert (0, "G") in capo_for("G") and all(0 <= f <= 7 for f, _ in capo_for("F"))
    assert capo_for("Bbm") == [(1, "Am"), (6, "Em")]


def test_nothing_fits_is_reported_not_hidden():
    fits = fit_keys("C2", "C5", "G2", "D4", "G")
    assert not any(f.fits for f in fits) and fits[0].margin_high < 0
    assert isinstance(fits[0], KeyFit)


def test_cli_key(capsys):
    assert main(["key", "--melody-low", "A2", "--melody-high", "E4", "--voice-low", "G2",
                 "--voice-high", "D4", "--key", "G"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["fits"][0]["key"] == "F" and out["fits"][0]["capo"]
    assert out["basis"] == BASIS


def test_cli_key_text_and_error(capsys):
    assert main(["--text", "key", "--melody-low", "A2", "--melody-high", "E4", "--voice-low", "G2",
                 "--voice-high", "D4", "--key", "G", "--tessitura", "C3", "A3"]) == 0
    assert "F" in capsys.readouterr().out
    assert main(["key", "--melody-low", "Z9", "--melody-high", "E4", "--voice-low", "G2",
                 "--voice-high", "D4", "--key", "G"]) == 2
    assert "error" in capsys.readouterr().err
