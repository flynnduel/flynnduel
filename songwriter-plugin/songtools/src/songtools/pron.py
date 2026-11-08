"""Pronunciation lexicon: CMU dictionary lookup with estimated fallback."""

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Literal

from songtools.cli import SongtoolsError
from songtools.paths import data_dir
from songtools.phonemes import VOWELS
from songtools.songfile import read_text


@dataclass
class Pron:
    phones: list[str] | None
    syllables: int
    stresses: list[int]
    estimated: bool


_ALT = re.compile(r"\(\d+\)$")
_QUOTES = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'})


_PUNCT = "\"`.,;:!?()[]{}-_*/\\ "


def _normalize(word: str) -> str:
    w = word.translate(_QUOTES).lower().strip().strip(_PUNCT)
    w = w.lstrip("'").strip(_PUNCT)
    if len(w) > 3 and w.endswith("in'"):
        return w[:-3] + "ing"
    return w.rstrip("'").strip(_PUNCT)


def _from_phones(phones: list[str]) -> Pron:
    stresses = [int(p[-1]) for p in phones if p[:-1] in VOWELS and p[-1].isdigit()]
    return Pron(phones, len(stresses), stresses, False)


def _estimate(word: str) -> Pron:
    w = word.lower()
    n = len(re.findall(r"[aeiouy]+", w))
    if n > 1 and re.search(r"[^aeiouy]e$", w) and not re.search(r"[^aeiouy]le$", w):
        n -= 1
    n = max(n, 1)
    return Pron(None, n, [1] + [0] * (n - 1), True)


def _parse(path: Path, strict: bool = False) -> dict[str, list[Pron]]:
    out: dict[str, list[Pron]] = {}
    text = read_text(path, "pronunciation file")
    for n, line in enumerate(text.splitlines(), 1):
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            raise SongtoolsError(str(path), n, f"expected 'word PHONES...', got {line!r}")
        phones = parts[1:]
        if strict and not any(p[:-1] in VOWELS and p[-1] in "012" for p in phones):
            raise SongtoolsError(
                str(path), n, "phones need at least one vowel with a stress digit (e.g. IY1)"
            )
        out.setdefault(_ALT.sub("", parts[0]).lower(), []).append(_from_phones(phones))
    return out


class Lexicon:
    def __init__(self, entries: dict[str, list[Pron]], ranks: dict[str, int]):
        self._entries = entries
        self._ranks = ranks

    def lookup(self, word: str) -> list[Pron]:
        w = _normalize(word)
        found = self._entries.get(w)
        if found:
            return list(found)
        return [_estimate(w)]

    def rank(self, word: str) -> int | None:
        return self._ranks.get(_normalize(word))

    def words(self) -> Iterable[str]:
        return self._entries.keys()


@lru_cache(maxsize=None)
def _load(overrides: Path | None) -> Lexicon:
    d = data_dir()
    entries = _parse(d / "cmudict" / "cmudict.dict")
    if overrides is not None:
        entries.update(_parse(overrides, strict=True))
    ranks: dict[str, int] = {}
    rank_file = d / "word_rank.tsv"
    if rank_file.exists():
        with rank_file.open(encoding="utf-8") as f:
            for line in f:
                w, _, r = line.rstrip("\n").partition("\t")
                if r.strip().isdigit():
                    ranks.setdefault(w.lower(), int(r))
    return Lexicon(entries, ranks)


def load_lexicon(overrides: Path | None = None) -> Lexicon:
    return _load(Path(overrides) if overrides is not None else None)


@lru_cache(maxsize=1)
def _function_words() -> frozenset[str]:
    text = (data_dir() / "function_words.txt").read_text(encoding="utf-8")
    return frozenset(w.strip().lower() for w in text.splitlines() if w.strip())


def word_class(word: str) -> Literal["function", "content"]:
    """Curly apostrophes count as straight ones; a leading-apostrophe entry ('cause) matches only
    that spelling, so "cause" stays content."""
    words = _function_words()
    raw = word.translate(_QUOTES).lower().strip(_PUNCT)
    return "function" if raw in words or _normalize(word) in words else "content"
