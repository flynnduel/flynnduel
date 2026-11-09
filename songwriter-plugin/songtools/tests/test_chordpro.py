import json

import pytest

from songtools.chordpro import BASIS, ChordProSong, CPSection, concert_pitch, from_song, parse, write
from songtools.cli import SongtoolsError, main
from songtools.songfile import parse_lyrics, parse_song_md

CANON = ("{title: River}\n{key: G}\n{capo: 2}\n{tempo: 96}\n\n"
         "{start_of_verse: Verse 1}\n[G]I was walking [C]down\n{end_of_verse}\n\n"
         "{start_of_chorus: Chorus}\n[D]Hold on\n{end_of_chorus}\n")


def test_roundtrip_canonical():
    assert write(parse(CANON)) == CANON


def test_short_directives_parse():
    s = parse("{t: X}\n{soc}\n[G]hi\n{eoc}\n")
    assert s.meta["title"] == "X" and s.sections[0].kind == "chorus"


def test_concert_pitch_moves_chords_and_key():
    c = concert_pitch(parse(CANON))
    assert "capo" not in c.meta and c.meta["key"] == "A" and c.sections[0].lines[0].startswith("[A]")


def test_concert_pitch_does_not_mutate_input():
    s = parse(CANON)
    concert_pitch(s)
    assert s.meta["capo"] == "2" and s.sections[0].lines[0].startswith("[G]")


def test_concert_pitch_flat_key_and_nc():
    s = parse("{key: F}\n{capo: 2}\n{soc}\n[F]a [N.C.]b [Bb/D]c\n{eoc}\n")
    c = concert_pitch(s)
    assert c.meta["key"] == "G" and c.sections[0].lines[0] == "[G]a [N.C.]b [C/E]c"
    s = parse("{key: Em}\n{capo: 3}\n{soc}\n[Em]a\n{eoc}\n")
    assert concert_pitch(s).meta["key"] == "Gm"
    s = parse("{key: G}\n{capo: 3}\n{soc}\n[G]a\n{eoc}\n")
    c = concert_pitch(s)
    assert c.meta["key"] == "Bb" and c.sections[0].lines[0] == "[Bb]a"


def test_concert_pitch_without_capo_is_unchanged():
    s = parse("{key: G}\n{soc}\n[G]a\n{eoc}\n")
    assert write(concert_pitch(s)) == write(s)


def test_from_song_builds_sections():
    secs = parse_lyrics("## Verse 1\n[G]I was walking\n## Intro\nhum\n")
    rec = parse_song_md("# River\n## Core\nkey: G\n")
    out = write(from_song(secs, rec))
    assert "{start_of_verse: Verse 1}" in out and "{comment: Intro}" in out


def test_from_song_reinserts_chords_and_meta():
    secs = parse_lyrics("## Verse 1\n[G]I was walking [C]down\n## Pre-Chorus\n[D]hold [N.C.]on\n")
    rec = parse_song_md("# River\n## Core\nkey: G\ncapo: 2\ntempo: 96\ntime: 4/4\nartist: Ann\n")
    s = from_song(secs, rec)
    assert s.meta == {"title": "River", "artist": "Ann", "key": "G", "capo": "2", "tempo": "96", "time": "4/4"}
    out = write(s)
    assert out.startswith("{title: River}\n{artist: Ann}\n{key: G}\n{capo: 2}\n{tempo: 96}\n{time: 4/4}\n\n")
    assert "[G]I was walking [C]down" in out
    assert "{comment: Pre-Chorus}\n[D]hold [N.C.]on\n" in out
    assert parse(out).sections[1].kind == "other"


def test_unknown_directives_kept_and_written_back():
    s = parse("{title: X}\n{foo: bar}\n{soc}\n[G]a\n{eoc}\n")
    assert s.meta["_unknown"] == ["{foo: bar}"]
    assert write(s) == "{title: X}\n{foo: bar}\n\n{start_of_chorus}\n[G]a\n{end_of_chorus}\n"


def test_defines_and_comment_sections():
    text = "{title: X}\n{define: Am0 base-fret 1}\n\n{comment: Intro}\nhum\n\n{start_of_bridge: B}\n[C]x\n{end_of_bridge}\n"
    s = parse(text)
    assert s.defines == ["Am0 base-fret 1"]
    assert s.sections[0] == CPSection("other", "Intro", ["hum"])
    assert write(s) == text


def test_unbalanced_raises_with_line():
    with pytest.raises(SongtoolsError) as e:
        parse("{title: X}\n{soc}\n[G]a\n")
    assert "start_of_chorus" in str(e.value)
    with pytest.raises(SongtoolsError) as e:
        parse("{title: X}\n{eov}\n")
    assert ":2:" in str(e.value)
    with pytest.raises(SongtoolsError) as e:
        parse("{sov}\n{soc}\n")
    assert ":2:" in str(e.value)


def test_chart_cli_writes_files(tmp_path, capsys):
    (tmp_path / "song.md").write_text("# River\n## Core\nkey: G\ncapo: 2\n")
    (tmp_path / "lyrics.md").write_text("## Verse 1\n[G]I was walking\n")
    assert main(["chart", str(tmp_path), "--concert"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert (tmp_path / "out" / "chart.cho").is_file()
    assert "{capo: 2}" in (tmp_path / "out" / "chart.cho").read_text()
    conc = (tmp_path / "out" / "chart-concert.cho").read_text()
    assert "{key: A}" in conc and "[A]I was walking" in conc
    assert len(out["written"]) == 2 and out["basis"] == BASIS


def test_chart_cli_without_concert_and_missing(tmp_path, capsys):
    (tmp_path / "song.md").write_text("# R\n## Core\nkey: G\n")
    assert main(["chart", str(tmp_path)]) == 2
    assert "lyrics.md" in capsys.readouterr().err
    (tmp_path / "lyrics.md").write_text("## Verse\n[G]a\n")
    assert main(["chart", str(tmp_path)]) == 0
    assert not (tmp_path / "out" / "chart-concert.cho").exists()


def test_concert_annotation_passthrough_and_directive_lines_untouched():
    s = parse("{key: G}\n{capo: 2}\n{soc}\n{comment: Play [G] softly}\n[*Riff]a [G]b\n{eoc}\n")
    c = concert_pitch(s)
    assert c.sections[0].lines == ["{comment: Play [G] softly}", "[*Riff]a [A]b"]


def test_concert_bad_chord_and_key_raise():
    with pytest.raises(SongtoolsError) as e:
        concert_pitch(parse("{key: G}\n{capo: 2}\n{soc}\n[Hold]on\n{eoc}\n"))
    assert "Hold" in str(e.value)
    with pytest.raises(SongtoolsError) as e:
        concert_pitch(parse("{key: G major}\n{capo: 2}\n{soc}\n[G]a\n{eoc}\n"))
    assert "G major" in str(e.value)


def test_chart_concert_failure_writes_nothing(tmp_path, capsys):
    (tmp_path / "song.md").write_text("# R\n## Core\nkey: G\ncapo: 2\n")
    (tmp_path / "lyrics.md").write_text("## Verse\n[Hold]on\n")
    assert main(["chart", str(tmp_path), "--concert"]) == 2
    assert not (tmp_path / "out" / "chart.cho").exists()


def _check_song(tmp_path, lyrics, music):
    (tmp_path / "song.md").write_text("# R\n## Core\nkey: G\ncapo: 2\n")
    (tmp_path / "lyrics.md").write_text(lyrics)
    if music is not None:
        (tmp_path / "music.md").write_text(music)


def _run_check(tmp_path, capsys):
    assert main(["chart", str(tmp_path), "--check"]) == 0
    return json.loads(capsys.readouterr().out)


def test_chart_check_matching_sections_write_nothing(tmp_path, capsys):
    _check_song(tmp_path, "## Verse 1\n[G]one [C]two\n[G]three [D]four\n[G]five [C]six\n[G]seven [D]eight\n",
                "## Verse 1\nprogression: G:4 C:4 G:4 D:4\n")
    out = _run_check(tmp_path, capsys)
    v = out["sections"]["Verse 1"]
    assert v["lyrics"] == ["G", "C", "G", "D", "G", "C", "G", "D"] and v["music"] == ["G", "C", "G", "D"]
    assert v["matches"] is True and v["only_lyrics"] == [] and v["only_music"] == []
    assert out["matches"] is True and not (tmp_path / "out").exists()
    assert out["chart"] == {"exists": False, "older_than_lyrics": None}
    assert out["basis"]


def test_chart_check_reports_mismatch_and_missing_sections(tmp_path, capsys):
    _check_song(tmp_path, "## Verse 1\n[G]a [C]b\n[D]c\n\n## Chorus\n[C]d [Em]e\n\n## Bridge\nno chords here\n",
                "## Verse 1\nprogression: G:4 C:4 G:4 D:4\n\n## Outro\nprogression: G:8\n")
    out = _run_check(tmp_path, capsys)
    v = out["sections"]["Verse 1"]
    assert v["lyrics"] == ["G", "C", "D"] and v["matches"] is False
    assert out["sections"]["Chorus"]["music"] is None and out["sections"]["Chorus"]["matches"] is False
    assert out["only_in_lyrics"] == ["Chorus"] and out["only_in_music"] == ["Outro"]
    assert "Bridge" not in out["sections"]  # a section with no inline chords is not compared
    assert out["matches"] is False


def test_chart_check_chord_sets_and_repeats_collapse(tmp_path, capsys):
    _check_song(tmp_path, "## Verse\n[G]a [G]b [Am]c\n", "## Verse\nprogression: G:4 C:4\n")
    v = _run_check(tmp_path, capsys)["sections"]["Verse"]
    assert v["lyrics"] == ["G", "Am"] and v["only_lyrics"] == ["Am"] and v["only_music"] == ["C"]


def test_chart_check_stale_chart(tmp_path, capsys):
    import os
    _check_song(tmp_path, "## Verse\n[G]a\n", "## Verse\nprogression: G:4\n")
    assert main(["chart", str(tmp_path)]) == 0
    capsys.readouterr()
    chart = tmp_path / "out" / "chart.cho"
    os.utime(chart, (1_000_000, 1_000_000))
    out = _run_check(tmp_path, capsys)
    assert out["chart"] == {"exists": True, "older_than_lyrics": True}
    os.utime(chart, (4_000_000_000, 4_000_000_000))
    assert _run_check(tmp_path, capsys)["chart"]["older_than_lyrics"] is False


def test_chart_check_without_music_md_is_an_error(tmp_path, capsys):
    _check_song(tmp_path, "## Verse\n[G]a\n", None)
    assert main(["chart", str(tmp_path), "--check"]) == 2
    assert "music.md" in capsys.readouterr().err


def test_chart_check_excludes_writing_flags(tmp_path, capsys):
    _check_song(tmp_path, "## Verse\n[G]a\n", "## Verse\nprogression: G:4\n")
    assert main(["chart", str(tmp_path), "--check", "--pdf"]) == 2
    assert not (tmp_path / "out").exists()
