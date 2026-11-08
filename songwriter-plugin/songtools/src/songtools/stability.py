"""Pattison section stability and chorus contrast."""

import argparse
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Literal

from songtools.cli import SongtoolsError
from songtools.phonemes import VOWELS
from songtools.pron import Lexicon, load_lexicon, word_class
from songtools.rhyme import classify
from songtools.songfile import Line, Section, end_word, parse_lyrics, read_text

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
    # per line: rhyme type against its partner (the most recent earlier line with the
    # same scheme letter); None for x lines and first occurrences of a letter;
    # "undetermined" for ? lines (end word pronunciation estimated)
    end_rhyme_types: list[str | None]
    verdict: Literal["stable", "unstable", "undetermined"]
    reasons: list[str]


@dataclass
class Contrast:
    contrasts: bool
    differences: list[str]
    notes: list[str] = field(default_factory=list)


def _words(lyric: str) -> list[str]:
    # keep a leading apostrophe so word_class can tell 'cause from cause
    return [w.rstrip("'") for w in _WORD.findall(lyric.lower().replace("’", "'")) if w.strip("'")]


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


def _estimated(word: str, lex: Lexicon) -> bool:
    return all(p.estimated for p in lex.lookup(word))


def _scheme(words: list[str], lex: Lexicon) -> str:
    """Letters per line; x = no partner, ? = rhyme undetermined (estimated pronunciation)."""
    n = len(words)
    rhymes = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if classify(words[i], words[j], lex).type in _RHYMING:
                rhymes[i][j] = rhymes[j][i] = True
    letters: list[str] = []
    next_letter = iter("abcdefghijklmnopqrstuvwyz")  # x is reserved for unpartnered lines
    for i in range(n):
        if _estimated(words[i], lex):
            letters.append("?")
            continue
        if not any(rhymes[i]):
            letters.append("x")
            continue
        earlier = next((letters[j] for j in range(i) if rhymes[i][j] and letters[j] not in "x?"), None)
        letters.append(earlier or next(next_letter))
    return "".join(letters)


def analyze_section(section: Section, lex: Lexicon) -> SectionStability:
    lines = _sung(section)
    if not lines:
        return SectionStability(section.name, 0, [], True, "", [], "undetermined",
                                ["no sung lines"])
    words = [end_word(l) for l in lines]
    stresses = [stresses_in(l.lyric, lex) for l in lines]
    matched = len(set(stresses)) == 1
    scheme = _scheme(words, lex)
    partner_types: list[str | None] = []
    for i, letter in enumerate(scheme):
        if letter == "?":
            partner_types.append("undetermined")
            continue
        j = next((k for k in range(i - 1, -1, -1) if scheme[k] == letter), None) \
            if letter != "x" else None
        partner_types.append(classify(words[j], words[i], lex).type if j is not None else None)
    reasons: list[str] = []
    if len(lines) % 2:
        reasons.append(f"odd phrase count ({len(lines)})")
    if not matched:
        reasons.append(f"phrase lengths not matched (stresses {stresses})")
    # With a ? line the scheme is not known, so the scheme-shape rules do not fire.
    undetermined = "?" in scheme
    if not undetermined and scheme in _OPEN_SCHEMES:
        reasons.append(f"open rhyme scheme ({scheme})")
    if not undetermined and scheme.endswith("x"):
        reasons.append("final line unrhymed (x)")
    if partner_types[-1] in ("assonance", "consonance"):
        reasons.append(f"final line rhymes by {partner_types[-1]} (remote rhyme)")
    verdict = "unstable" if reasons else "undetermined" if undetermined else "stable"
    for w in dict.fromkeys(w for w, letter in zip(words, scheme) if letter == "?"):
        reasons.append(f"rhyme undetermined (estimated pronunciation): {w}")
    return SectionStability(section.name, len(lines), stresses, matched, scheme, partner_types,
                            verdict, reasons)


def _mode(values: list):
    counts = Counter(values)
    best = max(counts.values())
    return next(v for v in values if counts[v] == best)


def chorus_contrast(verse: Section, chorus: Section, lex: Lexicon) -> Contrast:
    vlines, clines = _sung(verse), _sung(chorus)
    if not vlines or not clines:
        return Contrast(False, [], ["no sung lines to compare"])
    first = clines[0]
    diffs: list[str] = []
    notes: list[str] = []
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
    if not got_v or not vowels:
        notes.append("end vowel not compared (estimated pronunciation)")
    else:
        norm_v = _mode(vowels)
        if got_v != norm_v:
            diffs.append(f"end vowel {norm_v} vs {got_v}")
    return Contrast(bool(diffs), diffs, notes)


def _first(sections: list[Section], kind: str) -> tuple[Section | None, bool]:
    """First section of this kind that has sung lines; flag says whether any section of the kind exists."""
    of_kind = [s for s in sections if s.kind == kind]
    return next((s for s in of_kind if _sung(s)), None), bool(of_kind)


def _handler(args: argparse.Namespace):
    lex = load_lexicon(args.pron)
    path = args.lyrics_file
    text = read_text(path, "lyrics file")
    sections = parse_lyrics(text, str(path))
    chosen = sections
    if args.section:
        chosen = [s for s in sections if s.name.lower() == args.section.lower()]
        if not chosen:
            raise SongtoolsError(str(path), None, f"no section named {args.section!r}")
    verse, has_verse = _first(sections, "verse")
    chorus, has_chorus = _first(sections, "chorus")
    if verse is None:
        note = "verse has no lines to compare" if has_verse else "no verse to compare"
        contrast = {"contrast": None, "note": note}
    elif chorus is None:
        note = "chorus has no lines to compare" if has_chorus else "no chorus to compare"
        contrast = {"contrast": None, "note": note}
    else:
        c = chorus_contrast(verse, chorus, lex)
        contrast = {"contrast": {"contrasts": c.contrasts, "differences": c.differences,
                                 "notes": c.notes},
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
        lines += [f"  note: {n}" for n in c["notes"]]
    return "\n".join(lines)


def register(subparsers) -> None:
    from pathlib import Path
    p = subparsers.add_parser("stability", help="section stability and chorus contrast")
    p.add_argument("lyrics_file", type=Path)
    p.add_argument("--section", default=None, metavar="NAME")
    p.set_defaults(handler=_handler)
