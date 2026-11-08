import json

import pytest

from songtools.cli import SongtoolsError, main
from songtools.cliche import load_cliches, scan
from songtools.songfile import parse_lyrics


def test_cliche_rhyme_pair_pattison():
    secs = parse_lyrics("## Verse\nMy heart is on fire\nBurning with desire\n")
    hits = scan(secs, load_cliches())
    assert any(h.kind == "rhyme_pair" and h.match == "fire/desire" and "Pattison" in h.source for h in hits)


def test_rhyme_pair_alternate_lines_and_order_insensitive():
    secs = parse_lyrics("## Verse\nWe built a house of stone\nDesire\nA wall of ice\nOn fire\n")
    hits = [h for h in scan(secs, load_cliches()) if h.kind == "rhyme_pair"]
    assert [h.match for h in hits] == ["fire/desire"]
    assert hits[0].line_number == 5


def test_rhyme_pair_not_across_sections_or_distance():
    secs = parse_lyrics("## Verse\nFire\nx\ny\nDesire\n## Chorus\nlove\n## Bridge\ndove\n")
    assert not [h for h in scan(secs, load_cliches()) if h.kind == "rhyme_pair"]


def test_stock_image_only_in_strict():
    secs = parse_lyrics("## Verse\nUnder neon light we ran\n")
    assert not [h for h in scan(secs, load_cliches()) if h.kind == "stock_image"]
    assert [h for h in scan(secs, load_cliches(), strict=True) if h.kind == "stock_image"]


def test_emotion_naming_strict_multiword():
    secs = parse_lyrics("## Verse\nI feel so tired\n")
    assert not scan(secs, load_cliches())
    hits = scan(secs, load_cliches(), strict=True)
    assert [h.kind for h in hits] == ["emotion_naming"]
    assert hits[0].source == "Davis (as reported)"


def test_word_boundaries():
    secs = parse_lyrics("## Verse\nThe sadness of Saddleback\n")
    assert not [h for h in scan(secs, load_cliches()) if h.match == "sad"]


def test_case_insensitive_abstract():
    secs = parse_lyrics("## Verse\nSo SAD tonight\n")
    hits = scan(secs, load_cliches())
    assert [(h.kind, h.match, h.source) for h in hits] == [("abstract", "sad", "BMI (as reported)")]


def test_extra_file_merged(tmp_path):
    extra = tmp_path / "mine.json"
    extra.write_text(json.dumps({"phrases": [{"text": "road less traveled", "source": "me"}]}))
    secs = parse_lyrics("## Verse\nThe road less traveled\n")
    hits = scan(secs, load_cliches(extra=extra))
    assert [(h.kind, h.source) for h in hits] == [("phrase", "me")]
    assert load_cliches()["rhyme_pairs"]  # defaults kept


def test_cli(tmp_path, capsys):
    f = tmp_path / "lyrics.md"
    f.write_text("## Verse\nMy heart is on fire\nBurning with desire\n", encoding="utf-8")
    assert main(["cliche", str(f)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["hits"][0]["match"] == "fire/desire"
    assert out["strict"] is False and "Pattison" in out["basis"]


def test_cli_bad_extra(tmp_path, capsys):
    f = tmp_path / "lyrics.md"
    f.write_text("## Verse\nhello\n", encoding="utf-8")
    assert main(["cliche", str(f), "--extra", str(tmp_path / "nope.json")]) == 2


def test_extra_entry_missing_text(tmp_path):
    extra = tmp_path / "bad.json"
    extra.write_text('{"phrases": [{"source": "x"}]}')
    with pytest.raises(SongtoolsError):
        load_cliches(extra=extra)
