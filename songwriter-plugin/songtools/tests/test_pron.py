import pytest

from songtools.cli import SongtoolsError
from songtools.pron import load_lexicon, word_class


def test_cmu_lookup_with_stress():
    p = load_lexicon().lookup("river")[0]
    assert p.phones == ["R", "IH1", "V", "ER0"] and p.stresses == [1, 0] and not p.estimated


def test_alternate_pronunciations_returned():
    assert len(load_lexicon().lookup("read")) >= 2


def test_unknown_word_is_estimated_not_crash():
    p = load_lexicon().lookup("zorbletastic")[0]
    assert p.estimated and p.phones is None and p.syllables == 4


@pytest.mark.parametrize("w", ["walkin'", "Walkin',", "walkin'!", "'walkin'", "\u2018walkin\u2019", "(walkin')"])
def test_dropped_g_resolves_to_ing_form(w):
    lex = load_lexicon()
    p = lex.lookup(w)[0]
    assert not p.estimated and p.phones == lex.lookup("walking")[0].phones


@pytest.mark.parametrize("w", ["zoomie", "wuzzie", "flibbie", "kyree", "jaxxee", "gatsbye"])
def test_unknown_vowel_plus_e_keeps_syllable(w):
    p = load_lexicon().lookup(w)[0]
    assert p.estimated and p.syllables == 2


def test_override_without_stress_digit_errors(tmp_path):
    f = tmp_path / "p.txt"
    f.write_text("ok R IY1\nbad R IY V\n")
    with pytest.raises(SongtoolsError) as e:
        load_lexicon(f)
    assert e.value.line == 2


def test_override_line_without_phones_errors(tmp_path):
    f = tmp_path / "p.txt"
    f.write_text("river\n")
    with pytest.raises(SongtoolsError) as e:
        load_lexicon(f)
    assert e.value.line == 1


def test_override_missing_file_errors(tmp_path):
    with pytest.raises(SongtoolsError):
        load_lexicon(tmp_path / "nope.txt")


def test_override_bad_encoding_errors(tmp_path):
    f = tmp_path / "p.txt"
    f.write_bytes(b"caf\xe9 K AE1 F EY1\n")
    with pytest.raises(SongtoolsError):
        load_lexicon(f)


def test_number_is_estimated():
    assert load_lexicon().lookup("4")[0].estimated


def test_override_file_wins(tmp_path):
    f = tmp_path / "pron.txt"
    f.write_text("river R IY1 V ER0\n")
    assert load_lexicon(f).lookup("river")[0].phones[1] == "IY1"


def test_rank_common_before_rare():
    lex = load_lexicon()
    # "lugubrious" is absent from word_rank.tsv (rank None); use a rare ranked word.
    assert lex.rank("love") < lex.rank("dardanelles")
    assert lex.rank("lugubrious") is None


def test_word_class():
    assert word_class("the") == "function" and word_class("before") == "function"
    assert word_class("river") == "content"
