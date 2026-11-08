import pytest

from songtools.cli import main
from songtools.pron import load_lexicon
from songtools.rhyme import STABILITY_RANK, candidates, classify, lens_verdict

LEX = load_lexicon()


@pytest.mark.parametrize("b,expected", [
    ("hat", "perfect"), ("hack", "family"), ("rats", "additive"),
    ("laugh", "assonance"), ("spot", "consonance")])
def test_pattison_ladder_from_cat(b, expected):        # Pattison, verified
    assert classify("cat", b, LEX).type == expected


def test_subtractive():
    assert classify("rats", "cat", LEX).type == "subtractive"


def test_wichita_lineman_line_time_lenses():          # Pattison vs Webb, verified
    r = classify("line", "time", LEX)
    assert r.type == "family"
    assert lens_verdict(r, "pattison") == "family" and lens_verdict(r, "webb") == "false rhyme"


def test_eye_rhyme_and_identical():
    assert classify("dough", "rough", LEX).type == "eye"
    assert classify("night", "night", LEX).type == "identical"


def test_multisyllable_flag():
    assert classify("river", "giver", LEX).multisyllable
    assert not classify("cat", "hat", LEX).multisyllable


def test_estimated_word_is_undetermined():
    assert classify("cat", "zorbletastic", LEX).type == "undetermined"


def test_webb_lens_values():
    assert lens_verdict(classify("cat", "hat", LEX), "webb") == "true rhyme"
    assert lens_verdict(classify("dough", "rough", LEX), "webb") == "eye rhyme"


def test_candidates_order_stable_then_common():
    c = candidates("cat", LEX, limit=30)
    assert [x.type for x in c] == sorted([x.type for x in c], key=STABILITY_RANK.get)
    perfect = [x for x in c if x.type == "perfect"]
    assert perfect[0].rank <= perfect[-1].rank
    assert "cat" not in [x.word for x in c]


def test_candidates_fast():
    import time; t = time.perf_counter(); candidates("river", LEX); assert time.perf_counter() - t < 2.0


def test_cli_json(capsys):
    assert main(["rhyme", "line", "time", "--lens", "webb"]) == 0
    assert '"false rhyme"' in capsys.readouterr().out


def test_cli_candidates(capsys):
    assert main(["rhyme", "cat", "--candidates", "5"]) == 0
    assert '"candidates"' in capsys.readouterr().out


def test_cli_single_word_needs_candidates(capsys):
    assert main(["rhyme", "cat"]) == 2
