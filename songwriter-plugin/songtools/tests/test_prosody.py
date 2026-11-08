import itertools
import json

import pytest

from songtools.cli import main
from songtools.pron import load_lexicon
from songtools.prosody import (
    LIMIT,
    check,
    compare_lines,
    notation,
    propose,
    score,
    strength,
    syllabify,
)

LEX = load_lexicon()


def syls(t): return syllabify(t, LEX)


def test_three_tier_stress():
    s = syls("before the river")
    assert [x.stress for x in s] == [0, 2, 0, 1, 0]    # be-FORE demoted, "the" function, RIV-er


def test_strength_hierarchy():
    assert [strength(i) for i in range(8)] == [4, 1, 2, 1, 3, 1, 2, 1]


def test_proposal_puts_stresses_on_beats():
    s = syls("I was walking down to the river")
    slots = propose(s)
    assert all(slot % 2 == 0 for x, slot in zip(s, slots) if x.stress == 1)


def test_unconditionally_inversion_is_strong():           # Pattison, verified example
    s = syls("unconditionally")                          # un-con-DI-tion-al-ly
    _, flags = score(s, [1, 2, 3, 5, 6, 8])              # "di" on slot 3, "-ly" on slot 8 (downbeat)
    assert any(f.rule == "INVERSION" and f.severity == "strong" for f in flags)


def test_function_word_on_downbeat_flagged():
    s = syls("the river")
    _, flags = score(s, [0, 2, 3])
    assert any(f.rule == "FUNCTION_DOWNBEAT" for f in flags)


def test_accented_syncopation_not_flagged():
    s = syls("bad guy")
    _, flags = score(s, [3, 7])                            # long notes on off-beats
    assert not [f for f in flags if f.rule == "STRESSED_OFFBEAT"]


def test_anticipation_counts_as_beat():
    s = syls("river")
    _, flags = score(s, [7, 9])                            # "riv" one eighth before slot 8
    assert not [f for f in flags if f.rule == "STRESSED_OFFBEAT"]


def test_report_includes_limit_and_best():
    r = check(syls("I was walking down to the river"), None)
    assert r.limit == LIMIT and r.score == r.best_score and "|" in r.notation


def test_compare_lines_mismatch():
    c = compare_lines(syls("I was walking down to the river"), syls("She ran away"))
    assert not c["matches"] and c["syllables"] == [9, 4]


def test_long_line_is_fast():
    import time; t = time.perf_counter()
    propose(syls("and every single morning I am walking down along the muddy river"), bars=3)
    assert time.perf_counter() - t < 1.0


def test_estimated_word_marked():
    assert any(x.estimated for x in syls("zorbletastic river"))


# --- additional coverage ---

def test_limit_sentence_verbatim():
    assert LIMIT == ("Scoring is a simplified version of Hayes (2005), whose model matched "
                     "listeners' preferred settings about 70% of the time on folk-song data.")


def test_labels_and_word_positions():
    s = syls("walking river")
    assert [x.label for x in s] == ["wal", "king", "ri", "ver"]
    assert [(x.index_in_word, x.word_len) for x in s] == [(0, 2), (1, 2), (0, 2), (1, 2)]


def test_stressed_offbeat_short_note_flagged():
    s = syls("bad guy")
    _, flags = score(s, [-1, 0])                           # "bad" a short note on an off-beat
    assert [f.rule for f in flags if f.syllable == 0] == ["STRESSED_OFFBEAT"]


def test_unstressed_downbeat_and_lapse():
    total, flags = score(syls("river"), [0, 8])           # "-er" alone on bar 2's downbeat
    assert sorted(f.rule for f in flags) == ["LAPSE", "UNSTRESSED_DOWNBEAT"]
    assert total == 5 + 6


def test_inversion_two_syllables():
    total, flags = score(syls("river"), [2, 4])            # "-er" (strength 3) beats "riv" (2)
    assert [(f.rule, f.syllable) for f in flags] == [("EMPTY_DOWNBEAT", 0), ("INVERSION", 1)]
    assert total == 101


def test_empty_downbeat_alone():
    assert [f.rule for f in score(syls("bad guy"), [2, 4])[1]] == ["EMPTY_DOWNBEAT"]


def test_pickup_anticipation_covers_downbeat():
    s = syls("the river")
    _, flags = score(s, [-1, 2, 4])                        # "the" at -1 runs into slot 0
    assert not [f for f in flags if f.rule == "EMPTY_DOWNBEAT"]


def test_score_rejects_length_mismatch():
    with pytest.raises(ValueError):
        score(syls("river"), [0])


def _anticipations(slots, line):
    return sum(1 for s, x in zip(slots, list(slots[1:]) + [line]) if s % 2 and x - s > 1)


def _brute(s, bars):
    """Lowest score, then fewest anticipations, then lexicographically smallest slots."""
    line = bars * 8
    best = None
    for combo in itertools.combinations(range(-3, line), len(s)):
        key = (score(s, list(combo), line)[0], _anticipations(combo, line))
        if best is None or key < best[0]:          # combinations are lexicographic
            best = (key, list(combo))
    return best[0][0], best[1]


@pytest.mark.parametrize("text", ["the river", "unconditionally", "she ran away",
                                  "before the river", "bad guy"])
def test_propose_is_exact_and_lexicographic(text):
    s = syls(text)
    slots = propose(s, bars=1)
    assert (score(s, slots, 8)[0], slots) == _brute(s, 1)


def test_propose_too_many_syllables():
    with pytest.raises(ValueError):
        propose(syls("unconditionally unconditionally"), bars=1)


def test_notation_bars_and_case():
    s = syls("the river")
    assert notation(s, [-1, 0, 1]) == "the | RI-ver"
    assert notation(s, [6, 8, 9]) == "| THE | RI-ver"
    assert notation(syls("walking"), [7, 8]) == "| wal- | KING"


def test_compare_lines_match():
    c = compare_lines(syls("walking down"), syls("talking round"))
    assert c == {"syllables": [3, 3], "stress_pattern": ["101", "101"], "matches": True}


def _song(tmp_path, melody=None):
    (tmp_path / "lyrics.md").write_text(
        "## Verse 1\nI was walking down to the river\nThe water cold\n\n"
        "## Verse 2\nShe ran away\nAnd every night\n\n## Chorus\nHold on\n")
    if melody is not None:
        (tmp_path / "melody.md").write_text(melody)
    return str(tmp_path)


def test_cli_proposal_when_no_melody(tmp_path, capsys):
    d = _song(tmp_path)
    assert main(["prosody", d, "--section", "verse 1", "--line", "1"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["source"] == "proposal" and out["limit"] == LIMIT
    assert out["slots"] == out["best_slots"] and out["score"] == out["best_score"]
    assert "basis" in out


def test_cli_reads_melody(tmp_path, capsys):
    d = _song(tmp_path, "## Verse 1\n2: the/-1 wa/0 ter/1 cold/2\n")
    assert main(["prosody", d, "--section", "Verse 1", "--line", "2"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["source"] == "melody" and out["slots"] == [-1, 0, 1, 2]


def test_cli_slots_argument_and_text(tmp_path, capsys):
    d = _song(tmp_path)
    assert main(["--text", "prosody", d, "--section", "Verse 2", "--line", "1",
                 "--slots", "0 2 4 6"]) == 0
    out = capsys.readouterr().out
    assert "score" in out and LIMIT in out


def test_cli_slot_count_mismatch_is_error(tmp_path, capsys):
    d = _song(tmp_path)
    assert main(["prosody", d, "--section", "Verse 2", "--line", "1", "--slots", "0 2"]) == 2
    assert "4 syllables" in json.loads(capsys.readouterr().err)["error"]


def test_cli_bad_line_is_error(tmp_path, capsys):
    d = _song(tmp_path)
    assert main(["prosody", d, "--section", "Chorus", "--line", "5"]) == 2
    assert main(["prosody", d, "--section", "Bridge", "--line", "1"]) == 2


def test_cli_compare(tmp_path, capsys):
    d = _song(tmp_path)
    assert main(["prosody", d, "--section", "Verse 1", "--line", "1", "--compare"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert [c["section"] for c in out["compare"]] == ["Verse 2"]
    assert out["compare"][0]["syllables"] == [9, 4] and out["compare"][0]["matches"] is False


# --- fix round 1 ---

def test_vowelless_word_is_one_estimated_syllable():
    s = syls("hmm the river")                             # CMU: hmm HH M (no vowel)
    assert len(s) == 4
    assert (s[0].word, s[0].word_len, s[0].stress, s[0].estimated) == ("hmm", 1, 1, True)


def test_cli_counts_vowelless_word(tmp_path, capsys):
    (tmp_path / "lyrics.md").write_text("## Verse\nHmm the river\n")
    (tmp_path / "melody.md").write_text("## Verse\n1: hmm/0 the/2 ri/4 ver/6\n")
    assert main(["prosody", str(tmp_path), "--section", "Verse", "--line", "1"]) == 0
    assert json.loads(capsys.readouterr().out)["slots"] == [0, 2, 4, 6]
    assert main(["prosody", str(tmp_path), "--section", "Verse", "--line", "1",
                 "--slots", "0 2 4"]) == 2
    assert "4 syllables" in json.loads(capsys.readouterr().err)["error"]


def test_cli_rejects_out_of_range_slots(tmp_path, capsys):
    d = _song(tmp_path)
    assert main(["prosody", d, "--section", "Verse 2", "--line", "1",
                 "--slots", "100000 100001 100002 100003"]) == 2
    assert "-3" in json.loads(capsys.readouterr().err)["error"]
    assert main(["prosody", d, "--section", "Verse 2", "--line", "1",
                 "--slots", "-4 0 2 4"]) == 2
    capsys.readouterr()
    assert main(["prosody", d, "--section", "Verse 2", "--line", "1",
                 "--slots", "0 2 4 63"]) == 0


def test_library_caps_bars_and_slots():
    s = syls("river")
    with pytest.raises(ValueError):
        propose(s, bars=9)
    with pytest.raises(ValueError):
        check(s, None, bars=9)
    with pytest.raises(ValueError):
        check(s, [100000, 100001])
    assert check(s, [0, 63]).score >= 0


def test_cli_non_integer_slots(tmp_path, capsys):
    d = _song(tmp_path)
    assert main(["prosody", d, "--section", "Verse 2", "--line", "1",
                 "--slots", "0 two 4 6"]) == 2
    assert "integers" in json.loads(capsys.readouterr().err)["error"]


def test_cli_non_increasing_slots(tmp_path, capsys):
    d = _song(tmp_path)
    assert main(["prosody", d, "--section", "Verse 2", "--line", "1",
                 "--slots", "0 4 4 6"]) == 2
    assert "strictly increasing" in json.loads(capsys.readouterr().err)["error"]
