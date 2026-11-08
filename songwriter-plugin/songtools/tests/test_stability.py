from songtools.cli import main
from songtools.pron import load_lexicon
from songtools.songfile import Section, parse_lyrics
from songtools.stability import analyze_section, chorus_contrast, stresses_in

LEX = load_lexicon()


def sec(text):
    return parse_lyrics("## Verse\n" + text)[0]


def test_abab_four_matched_is_stable():
    s = analyze_section(sec("I walked out in the night\nThe river took the day\nI chased the golden light\nAnd begged the dark to stay\n"), LEX)
    assert s.rhyme_scheme == "abab" and s.verdict == "stable"


def test_xxaa_is_open():
    s = analyze_section(sec("Looking through the window\nCoffee on the table\nMorning coming cold\nEverything is old\n"), LEX)
    assert s.rhyme_scheme == "xxaa" and s.verdict == "unstable" and any("open" in r for r in s.reasons)


def test_odd_phrase_count_unstable():
    s = analyze_section(sec("I walked out in the night\nThe river took the day\nI chased the golden light\n"), LEX)
    assert s.verdict == "unstable" and any("odd" in r for r in s.reasons)


def test_one_line_and_empty_sections_do_not_crash():
    assert analyze_section(sec("Just one line here\n"), LEX).verdict == "unstable"
    assert analyze_section(Section("Verse", "verse", []), LEX).verdict == "undetermined"


def test_chorus_contrast_on_first_line():
    v = sec("I walked out in the night again\nThe river took the light away\n")
    c = parse_lyrics("## Chorus\nHold on\nHold on to me\n")[0]
    r = chorus_contrast(v, c, LEX)
    assert r.contrasts and any(d.startswith("stresses") for d in r.differences)


def test_cli_handles_chorus_without_verse(tmp_path, capsys):
    f = tmp_path / "lyrics.md"
    f.write_text("## Chorus\nHold on\nHold on to me\n")
    assert main(["stability", str(f)]) == 0
    assert "no verse" in capsys.readouterr().out


def test_stresses_in_function_words_count_zero():
    assert stresses_in("before the", LEX) == 0
    assert stresses_in("river night", LEX) == 2


def test_cli_section_filter_and_contrast(tmp_path, capsys):
    f = tmp_path / "lyrics.md"
    f.write_text("## Verse\nI walked out in the night\nThe river took the day\n\n## Chorus\nHold on\nHold on to me\n")
    assert main(["--text", "stability", str(f), "--section", "Verse"]) == 0
    assert "Verse" in capsys.readouterr().out


def test_undetermined_section_carries_reason():
    s = analyze_section(Section("Verse", "verse", []), LEX)
    assert s.verdict == "undetermined" and s.reasons == ["no sung lines"]
    chord_only = parse_lyrics("## Verse\n[C] [G]\n")[0]
    assert analyze_section(chord_only, LEX).reasons == ["no sung lines"]


def test_remote_rhyme_fires_for_abab():
    s = analyze_section(sec("I walked out in the night\nThe river took the lane\nI chased the golden light\nAnd begged the dark to save\n"), LEX)
    assert s.rhyme_scheme == "abab"
    assert s.end_rhyme_types == [None, None, "perfect", "assonance"]
    assert s.verdict == "unstable" and any("remote rhyme" in r for r in s.reasons)


def test_contrast_skips_header_only_verse(tmp_path, capsys):
    import json
    f = tmp_path / "lyrics.md"
    f.write_text("## Verse\n\n## Verse 2\nI walked out in the night again\nThe river took the light away\n\n## Chorus\nHold on\nHold on to me\n")
    assert main(["stability", str(f)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["verse"] == "Verse 2" and out["contrast"]["contrasts"] is True


def test_contrast_header_only_verse_gives_note(tmp_path, capsys):
    import json
    f = tmp_path / "lyrics.md"
    f.write_text("## Verse\n\n## Chorus\nHold on\nHold on to me\n")
    assert main(["stability", str(f)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["contrast"] is None and out["note"] == "verse has no lines to compare"


def test_estimated_end_word_skips_end_vowel():
    v = sec("I walked out in the night again\nThe river took the light away\n")
    c = parse_lyrics("## Chorus\nHold on to zorbletastic\n")[0]
    r = chorus_contrast(v, c, LEX)
    assert not any(d.startswith("end vowel") for d in r.differences)
    assert "end vowel not compared (estimated pronunciation)" in r.notes


def test_estimated_end_word_is_question_mark_not_x():
    s = analyze_section(sec("I walked out in the night\nThe river took the day\n"
                            "I chased the golden light\nThe river took the zorbletastic\n"), LEX)
    assert s.rhyme_scheme == "axa?"
    assert "rhyme undetermined (estimated pronunciation): zorbletastic" in s.reasons
    assert not any("unrhymed" in r or "open" in r for r in s.reasons)
    assert s.verdict == "undetermined"
    assert s.end_rhyme_types[-1] == "undetermined"


def test_question_mark_does_not_hide_real_instability():
    s = analyze_section(sec("I walked out in the night\nThe river took the day\nAnd begged the zorbletastic\n"), LEX)
    assert s.rhyme_scheme.endswith("?")
    assert s.verdict == "unstable" and any("odd" in r for r in s.reasons)
