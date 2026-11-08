import json

import pytest

from songtools.cli import main
from songtools.pov import classify_pov, classify_sections
from songtools.songfile import parse_lyrics


@pytest.mark.parametrize("text,pov", [
    ("I love you", "direct_address"), ("You walk alone tonight", "second_narrative"),
    ("I walked her home", "first_narrative"), ("She walked him home", "third_narrative"),
    ('She said "I love you"', "third_narrative"),
    ("She said “I love you”", "third_narrative"),
    ("I’m on my way", "first_narrative"),
    ("You’re not alone", "second_narrative")])
def test_four_pattison_povs(text, pov):
    assert classify_pov(text).pov == pov


def test_counts():
    r = classify_pov("I told him you were mine")
    assert (r.i_count, r.you_count, r.third_count) == (2, 1, 1)


def test_generic_you_flag():
    assert classify_pov("I wonder, you never know").generic_you
    assert not classify_pov("I wonder, you there").generic_you


def test_shift_across_sections():
    secs = parse_lyrics("## Verse 1\nI walked her home\n## Verse 2\nYou walk alone\n")
    r = classify_sections(secs)
    assert r["shift"]
    assert r["sections"]["Verse 1"].pov == "first_narrative"


def test_no_shift_when_consistent():
    secs = parse_lyrics("## Verse 1\nI walked home\n## Chorus\nMy road is long\n")
    assert not classify_sections(secs)["shift"]


def test_cli_json(tmp_path, capsys):
    f = tmp_path / "lyrics.md"
    f.write_text("## Verse 1\nI walked her home\n## Verse 2\nYou walk alone\n", encoding="utf-8")
    assert main(["pov", str(f)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["shift"] is True
    assert out["song"]["pov"] == "direct_address"
    assert out["sections"]["Verse 2"]["pov"] == "second_narrative"
    assert "Pattison" in out["basis"]
