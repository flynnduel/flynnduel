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
