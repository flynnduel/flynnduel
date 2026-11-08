"""ARPAbet phoneme tables: vowels, diphthongs and Pattison consonant families."""

import json
from functools import lru_cache
from typing import Literal

from songtools.paths import data_dir

VOWELS = frozenset("AA AE AH AO AW AY EH ER EY IH IY OW OY UH UW".split())
DIPHTHONGS = {
    "AY": ("AA", "IY"),
    "EY": ("EH", "IY"),
    "OY": ("AO", "IY"),
    "AW": ("AA", "UW"),
    "OW": ("AO", "UW"),
}

Family = Literal["plosive", "fricative", "nasal"]
_FRICATIVE_COMPANIONS = {True: ["Z", "ZH", "JH", "DH"], False: ["S", "SH", "CH", "TH"]}


@lru_cache(maxsize=1)
def _table() -> dict:
    return json.loads((data_dir() / "consonants.json").read_text(encoding="utf-8"))


def family(c: str) -> Family | None:
    t = _table()
    for fam in ("plosive", "fricative", "nasal"):
        if c in t[fam]["voiced"] or c in t[fam]["unvoiced"]:
            return fam  # type: ignore[return-value]
    return None


def voiced(c: str) -> bool:
    t = _table()
    return any(c in t[fam]["voiced"] for fam in ("plosive", "fricative", "nasal"))


def _partner(c: str) -> str | None:
    p = _table()["partners"]
    if c in p:
        return p[c]
    for k, v in p.items():
        if v == c:
            return k
    return None


def relatives(c: str) -> list[str]:
    """Other consonants of the same family, closest first."""
    fam = family(c)
    if fam is None:
        return []
    t = _table()[fam]
    members = t["voiced"] + t["unvoiced"]
    if fam == "nasal":
        return [m for m in members if m != c]
    partner = _partner(c)
    same_voice = t["voiced"] if voiced(c) else t["unvoiced"]
    if fam == "plosive":
        order = [partner] + [m for m in same_voice if m != c]
    else:
        order = [m for m in _FRICATIVE_COMPANIONS[voiced(c)] if m != c] + [partner]
    out: list[str] = []
    for m in order + members:
        if m != c and m is not None and m not in out:
            out.append(m)
    return out
