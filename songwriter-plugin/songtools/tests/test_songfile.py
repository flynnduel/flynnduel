import pytest

from songtools.cli import SongtoolsError
from songtools.songfile import (
    KeptLine,
    Split,
    end_word,
    format_melody_entry,
    parse_lyrics,
    parse_melody_md,
    parse_music_md,
    parse_song_md,
)


def test_sections_and_inline_chords():
    secs = parse_lyrics("## Verse 1\n[G]I was walking [C]down to the river\n\n## Chorus\nHold on\n")
    assert [s.kind for s in secs] == ["verse", "chorus"]
    ln = secs[0].lines[0]
    assert ln.lyric == "I was walking down to the river"
    assert ln.chords == [(0, "G"), (14, "C")]
    assert ln.number == 2


def test_prechorus_name_variants():
    assert parse_lyrics("## Pre-Chorus\nx\n")[0].kind == "prechorus"
    assert parse_lyrics("## Pre Chorus 2\nx\n")[0].kind == "prechorus"
    assert parse_lyrics("## Coda\nx\n")[0].kind == "other"


def test_comments_ignored_and_line_numbers_kept():
    secs = parse_lyrics("## Verse\n<!-- note -->\n<!--\nmulti\n-->\nreal line <!-- x -->\n")
    assert [(l.number, l.lyric) for l in secs[0].lines] == [(6, "real line")]


def test_end_word_strips_punctuation_and_curly_quotes():
    ln = parse_lyrics("## Verse\nShe said “goodbye,” —\n")[0].lines[0]
    assert end_word(ln) == "goodbye"
    ln = parse_lyrics("## Verse\nKeep on goin’\n")[0].lines[0]
    assert end_word(ln) == "goin'"


def test_unclosed_chord_bracket_reports_file_and_line():
    with pytest.raises(SongtoolsError) as e:
        parse_lyrics("## Verse\nfine\n[G broken\n")
    assert (e.value.file, e.value.line) == ("lyrics.md", 3)


def test_song_md_core_kept_and_splits():
    rec = parse_song_md('# River\n## Core\nkey: G\ncapo: 2\n## Split sheet\n- Ana | words, music | 50\n'
                        '## Kept lines\n- "down to the river" | cliche | echoes bridge | 2026-11-08\n')
    assert rec.title == "River" and rec.core["capo"] == "2"
    assert rec.kept[0] == KeptLine("down to the river", "cliche", "echoes bridge", "2026-11-08")
    assert rec.splits[0] == Split("Ana", ["words", "music"], 50.0)


def test_song_md_other_sections_verbatim_and_bad_split():
    rec = parse_song_md("# T\n## Notes\nfree text\nmore\n")
    assert rec.sections["Notes"] == "free text\nmore"
    with pytest.raises(SongtoolsError) as e:
        parse_song_md("# T\n## Split sheet\n- Ana | words | lots\n")
    assert (e.value.file, e.value.line) == ("song.md", 3)


def test_music_md_progression():
    assert parse_music_md("## Verse 1\nprogression: G:4 C:2.5\n") == {"Verse 1": [("G", 4.0), ("C", 2.5)]}


def test_music_md_bad_token():
    with pytest.raises(SongtoolsError) as e:
        parse_music_md("## Verse 1\nprogression: G:4 C\n")
    assert (e.value.file, e.value.line) == ("music.md", 2)


def test_melody_roundtrip():
    entry = parse_melody_md("## Verse 1\n3: i/-2 was/-1 walk/0\n")
    assert entry[("Verse 1", 3)] == [("i", -2), ("was", -1), ("walk", 0)]
    assert format_melody_entry(3, entry[("Verse 1", 3)]) == "3: i/-2 was/-1 walk/0"


def test_melody_bad_token():
    with pytest.raises(SongtoolsError) as e:
        parse_melody_md("## Verse 1\n3: i/x\n")
    assert (e.value.file, e.value.line) == ("melody.md", 2)


def _end(lyric):
    return end_word(parse_lyrics(f"## Verse\n{lyric}\n")[0].lines[0])


@pytest.mark.parametrize("lyric,expected", [
    ("Down To The RIVER", "river"),
    ("down to the river—oh", "oh"),
    ("down to the river--oh", "oh"),
    ("Heart-Break!", "break"),
    ("stray ] bracket here]", "here"),
    ("and then...", "then"),
    ("and then (maybe)", "maybe"),
    ("wait…", "wait"),
    ("[G] [C]", ""),
    ("so — ", "so"),
])
def test_end_word_messy_text(lyric, expected):
    assert _end(lyric) == expected


def test_empty_chord_bracket_error():
    with pytest.raises(SongtoolsError) as e:
        parse_lyrics("## Verse\nfine\nbad [] chord\n")
    assert (e.value.file, e.value.line) == ("lyrics.md", 3)


def test_lyric_before_heading_error():
    with pytest.raises(SongtoolsError) as e:
        parse_lyrics("oops\n## Verse\nx\n")
    assert (e.value.file, e.value.line) == ("lyrics.md", 1)


def test_malformed_kept_line_error():
    with pytest.raises(SongtoolsError) as e:
        parse_song_md('# T\n## Kept lines\n- no quotes | cliche | r | d\n')
    assert (e.value.file, e.value.line) == ("song.md", 3)


# `songtools song SONG_MD`: parse check for song.md alone (no lyrics file needed), so a skill
# that writes `## Core` fields (/idea, /structure) can verify the file still parses.
def test_song_cli_reads_core_kept_and_splits(tmp_path, capsys):
    import json
    from songtools.cli import main
    p = tmp_path / "song.md"
    p.write_text("# Workshop\n\n## Core\nkey: G\ncentral image: a pencil line on the doorframe\n"
                 "form: verse-chorus: V C V C B C\n\n## Kept lines\n"
                 '- "I left it there" | keep | plain | 2026-11-09\n\n## Split sheet\n- Ann | lyrics | 100\n')
    assert main(["song", str(p)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["title"] == "Workshop"
    assert out["core"]["central image"] == "a pencil line on the doorframe"
    assert out["core"]["form"] == "verse-chorus: V C V C B C"
    assert out["kept"] == [{"text": "I left it there", "flag": "keep", "reason": "plain", "date": "2026-11-09"}]
    assert out["splits"] == [{"name": "Ann", "roles": ["lyrics"], "percent": 100.0}]


def test_song_cli_rejects_core_line_without_colon(tmp_path, capsys):
    import json
    from songtools.cli import main
    p = tmp_path / "song.md"
    p.write_text("# U\n\n## Core\nkey: G\nthe point is loss\n")
    assert main(["song", str(p)]) == 2
    err = json.loads(capsys.readouterr().err)["error"]
    assert "song.md:5" in err and "key: value" in err


def test_song_cli_missing_file(tmp_path, capsys):
    from songtools.cli import main
    assert main(["song", str(tmp_path / "nope.md")]) == 2


def test_song_cli_text_output(tmp_path, capsys):
    from songtools.cli import main
    p = tmp_path / "song.md"
    p.write_text("# U\n\n## Core\nform: strophic\n")
    assert main(["--text", "song", str(p)]) == 0
    assert "form: strophic" in capsys.readouterr().out
