"""Pattison section stability and chorus contrast."""

import argparse
import re
from collections import Counter
from dataclasses import dataclass
from typing import Literal

from songtools.cli import SongtoolsError
from songtools.phonemes import VOWELS
from songtools.pron import Lexicon, load_lexicon, word_class
from songtools.rhyme import classify
from songtools.songfile import Line, Section, end_word, parse_lyrics

BASIS = "Pattison stability elements (verified)"

# Types that share a scheme letter. "identical" (same word repeated) is a repeat, not a
# rhyme, but it sits in the same slot, so it shares the letter without any extra reason.
_RHYMING = {"perfect", "family", "additive", "subtractive", "assonance", "consonance",
            "identical"}
_OPEN_SCHEMES = {"abba", "xxaa", "xaxa", "xxxa"}
_WORD = re.compile(r"[\w']+")


@dataclass
class SectionStability:
    section: str
    phrase_count: int
    stresses_per_line: list[int]
    lengths_matched: bool
    rhyme_scheme: str
    end_rhyme_types: list[str]
    verdict: Literal["stable", "unstable", "undetermined"]
    reasons: list[str]


@dataclass
class Contrast:
    contrasts: bool
    differences: list[str]


def _words(lyric: str) -> list[str]:
    return [w.strip("'") for w in _WORD.findall(lyric.lower().replace("’", "'")) if w.strip("'")]


def stresses_in(lyric: str, lex: Lexicon) -> int:
    """Stress-1 syllables in polysyllables plus content monosyllables."""
    total = 0
    for w in _words(lyric):
        if word_class(w) == "function":
            continue
        pron = lex.lookup(w)[0]
        if pron.syllables >= 2:
            total += sum(1 for s in pron.stresses if s == 1)
        else:
            total += 1
    return total


def _syllables_in(lyric: str, lex: Lexicon) -> int:
    return sum(lex.lookup(w)[0].syllables for w in _words(lyric))


def _end_vowel(line: Line, lex: Lexicon) -> str | None:
    word = end_word(line)
    if not word:
        return None
    pron = lex.lookup(word)[0]
    if not pron.phones:
        return None
    stressed = [p[:-1] for p in pron.phones if p[:-1] in VOWELS and p[-1] in "12"]
    return stressed[-1] if stressed else None


def _sung(section: Section) -> list[Line]:
    return [l for l in section.lines if end_word(l)]


def _scheme(words: list[str], lex: Lexicon) -> str:
    n = len(words)
    rhymes = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if classify(words[i], words[j], lex).type in _RHYMING:
                rhymes[i][j] = rhymes[j][i] = True
    letters: list[str] = []
    next_letter = iter("abcdefghijklmnopqrstuvwyz")  # x is reserved for unpartnered lines
    for i in range(n):
        if not any(rhymes[i]):
            letters.append("x")
            continue
        earlier = next((letters[j] for j in range(i) if rhymes[i][j] and letters[j] != "x"), None)
        letters.append(earlier or next(next_letter))
    return "".join(letters)


def analyze_section(section: Section, lex: Lexicon) -> SectionStability:
    lines = _sung(section)
    if not lines:
        return SectionStability(section.name, 0, [], True, "", [], "undetermined", [])
    words = [end_word(l) for l in lines]
    stresses = [stresses_in(l.lyric, lex) for l in lines]
    matched = len(set(stresses)) == 1
    scheme = _scheme(words, lex)
    adjacent = [classify(a, b, lex).type for a, b in zip(words, words[1:])]
    reasons: list[str] = []
    if len(lines) % 2:
        reasons.append(f"odd phrase count ({len(lines)})")
    if not matched:
        reasons.append(f"phrase lengths not matched (stresses {stresses})")
    if scheme in _OPEN_SCHEMES:
        reasons.append(f"open rhyme scheme ({scheme})")
    if scheme.endswith("x"):
        reasons.append("final line unrhymed (x)")
    if adjacent and adjacent[-1] in ("assonance", "consonance"):
        reasons.append(f"final pair rhymes by {adjacent[-1]} (remote rhyme)")
    return SectionStability(section.name, len(lines), stresses, matched, scheme, adjacent,
                            "unstable" if reasons else "stable", reasons)


def _mode(values: list):
    counts = Counter(values)
    best = max(counts.values())
    return next(v for v in values if counts[v] == best)


def chorus_contrast(verse: Section, chorus: Section, lex: Lexicon) -> Contrast:
    vlines, clines = _sung(verse), _sung(chorus)
    if not vlines or not clines:
        return Contrast(False, [])
    first = clines[0]
    diffs: list[str] = []
    norm = _mode([stresses_in(l.lyric, lex) for l in vlines])
    got = stresses_in(first.lyric, lex)
    if got != norm:
        diffs.append(f"stresses {norm} vs {got}")
    norm = _mode([_syllables_in(l.lyric, lex) for l in vlines])
    got = _syllables_in(first.lyric, lex)
    if got != norm:
        diffs.append(f"syllables {norm} vs {got}")
    vowels = [v for v in (_end_vowel(l, lex) for l in vlines) if v]
    got_v = _end_vowel(first, lex)
    if vowels and got_v:
        norm_v = _mode(vowels)
        if got_v != norm_v:
            diffs.append(f"end vowel {norm_v} vs {got_v}")
    return Contrast(bool(diffs), diffs)


def _first(sections: list[Section], kind: str) -> Section | None:
    return next((s for s in sections if s.kind == kind), None)


def _handler(args: argparse.Namespace):
    lex = load_lexicon(args.pron)
    path = args.lyrics_file
    try:
        text = path.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError) as e:
        raise SongtoolsError(str(path), None, f"cannot read lyrics file ({type(e).__name__})") from None
    sections = parse_lyrics(text, str(path))
    chosen = sections
    if args.section:
        chosen = [s for s in sections if s.name.lower() == args.section.lower()]
        if not chosen:
            raise SongtoolsError(str(path), None, f"no section named {args.section!r}")
    verse, chorus = _first(sections, "verse"), _first(sections, "chorus")
    if verse is None:
        contrast = {"contrast": None, "note": "no verse to compare"}
    elif chorus is None:
        contrast = {"contrast": None, "note": "no chorus to compare"}
    else:
        c = chorus_contrast(verse, chorus, lex)
        contrast = {"contrast": {"contrasts": c.contrasts, "differences": c.differences},
                    "verse": verse.name, "chorus": chorus.name}
    out = []
    for s in chosen:
        r = analyze_section(s, lex)
        out.append({"section": r.section, "phrase_count": r.phrase_count,
                    "stresses_per_line": r.stresses_per_line,
                    "lengths_matched": r.lengths_matched, "rhyme_scheme": r.rhyme_scheme,
                    "end_rhyme_types": r.end_rhyme_types, "verdict": r.verdict,
                    "reasons": r.reasons})
    return {"sections": out, **contrast, "basis": BASIS}, to_text


def to_text(r: dict) -> str:
    lines = []
    for s in r["sections"]:
        lines.append(f"{s['section']}: {s['verdict']} ({s['phrase_count']} phrases, "
                     f"scheme {s['rhyme_scheme'] or '-'}, stresses {s['stresses_per_line']})")
        lines += [f"  - {x}" for x in s["reasons"]]
    if r["contrast"] is None:
        lines.append(f"Contrast: {r['note']}")
    else:
        c = r["contrast"]
        lines.append(f"Contrast ({r['verse']} vs {r['chorus']}): "
                     + ("; ".join(c["differences"]) if c["contrasts"] else "none"))
    return "\n".join(lines)


def register(subparsers) -> None:
    from pathlib import Path
    p = subparsers.add_parser("stability", help="section stability and chorus contrast")
    p.add_argument("lyrics_file", type=Path)
    p.add_argument("--section", default=None, metavar="NAME")
    p.set_defaults(handler=_handler)
