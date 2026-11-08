"""Pattison rhyme-type classifier with a Webb strict-rhyme lens, plus candidate search."""

import argparse
import re
from dataclasses import dataclass
from typing import Literal

from songtools.cli import SongtoolsError
from songtools.phonemes import VOWELS, relatives
from songtools.pron import Lexicon, Pron, load_lexicon

BASIS = "Pattison rhyme types (verified); Webb strict-rhyme lens (verified)"

RHYME_TYPES = ["identical", "perfect", "family", "additive", "subtractive",
               "assonance", "consonance", "eye", "none", "undetermined"]
# Pattison: lower is more stable.
STABILITY_RANK = {"perfect": 0, "family": 1, "additive": 2, "subtractive": 2,
                  "assonance": 3, "consonance": 4}

Lens = Literal["pattison", "webb"]
# (phones before the stressed vowel, stressed vowel, phones after it), stress digits stripped
Parts = tuple[tuple[str, ...], str, tuple[str, ...]]


@dataclass
class RhymeResult:
    a: str
    b: str
    type: str
    multisyllable: bool
    detail: str


@dataclass
class Candidate:
    word: str
    type: str
    rank: int | None


def _strip(p: str) -> str:
    return p.rstrip("012")


def _parts(pron: Pron) -> Parts | None:
    """Split at the last stressed vowel (stress 1), else the last vowel."""
    if pron.phones is None:
        return None
    idx = [i for i, p in enumerate(pron.phones) if _strip(p) in VOWELS]
    if not idx:
        return None
    primary = [i for i in idx if pron.phones[i].endswith("1")]
    i = (primary or idx)[-1]
    s = [_strip(p) for p in pron.phones]
    return tuple(s[:i]), s[i], tuple(s[i + 1:])


def _is_multi(pa: Parts, pb: Parts) -> bool:
    return all(sum(1 for p in x[2] if p in VOWELS) >= 1 for x in (pa, pb))


def _same_family(ca: tuple[str, ...], cb: tuple[str, ...]) -> bool:
    return len(ca) == len(cb) and all(x == y or y in relatives(x) for x, y in zip(ca, cb))


def _extends(short: tuple[str, ...], long: tuple[str, ...]) -> bool:
    return (len(long) > len(short) and long[:len(short)] == short
            and all(p not in VOWELS for p in long[len(short):]))


def _classify_parts(pa: Parts, pb: Parts) -> tuple[str, str]:
    (oa, va, ca), (ob, vb, cb) = pa, pb
    if va == vb:
        if ca == cb:
            if oa == ob:
                return "identical", "same sounds (homophone)"
            return "perfect", f"{va} + {' '.join(ca) or 'open ending'} match, onsets differ"
        if _same_family(ca, cb):
            diff = [f"{x}/{y}" for x, y in zip(ca, cb) if x != y]
            return "family", f"same vowel {va}; codas differ only within a family ({', '.join(diff)})"
        if _extends(ca, cb):
            return "additive", f"same vowel {va}; second adds {' '.join(cb[len(ca):])}"
        if _extends(cb, ca):
            return "subtractive", f"same vowel {va}; second drops {' '.join(ca[len(cb):])}"
        return "assonance", f"same vowel {va}; codas differ"
    if ca == cb and ca:
        return "consonance", f"vowels {va}/{vb} differ; codas {' '.join(ca)} match"
    return "none", "no shared vowel or coda"


def _order(t: str) -> int:
    return -1 if t == "identical" else STABILITY_RANK.get(t, 8)


def classify(a: str, b: str, lex: Lexicon) -> RhymeResult:
    na, nb = a.strip().lower(), b.strip().lower()
    pas, pbs = lex.lookup(a), lex.lookup(b)
    if any(p.estimated for p in pas + pbs):
        return RhymeResult(a, b, "undetermined", False,
                           "a word is not in the dictionary; add it to the personal pronunciations file")
    best: tuple[str, str, bool] | None = None
    for x in pas:
        for y in pbs:
            xp, yp = _parts(x), _parts(y)
            if xp is None or yp is None:
                continue
            t, d = _classify_parts(xp, yp)
            multi = t in ("perfect", "family") and _is_multi(xp, yp)
            if best is None or _order(t) < _order(best[0]):
                best = (t, d, multi)
    if na == nb:
        return RhymeResult(a, b, "identical", best[2] if best else False, "same word")
    if best is None:
        return RhymeResult(a, b, "undetermined", False, "no vowels in pronunciation")
    t, d, multi = best
    if t == "none" and len(na) >= 3 and len(nb) >= 3 and na[-3:] == nb[-3:]:
        return RhymeResult(a, b, "eye", False, f"spelled alike ending -{na[-3:]}, sounds differ")
    return RhymeResult(a, b, t, multi, d)


def lens_verdict(result: RhymeResult, lens: Lens) -> str:
    if lens == "pattison":
        return result.type
    if result.type == "perfect":
        return "true rhyme"
    if result.type == "eye":
        return "eye rhyme"
    return "false rhyme"


_Entry = tuple[str, Parts]
_INDEX: dict[int, tuple[dict[str, list[_Entry]], dict[tuple[str, ...], list[_Entry]]]] = {}


def _index(lex: Lexicon):
    """Lazy index: stressed vowel -> entries, and coda -> entries (for consonance)."""
    got = _INDEX.get(id(lex))
    if got is not None:
        return got
    by_vowel: dict[str, list[_Entry]] = {}
    by_coda: dict[tuple[str, ...], list[_Entry]] = {}
    for w in lex.words():
        for pron in lex.lookup(w):
            parts = _parts(pron)
            if parts is None:
                continue
            by_vowel.setdefault(parts[1], []).append((w, parts))
            if parts[2]:
                by_coda.setdefault(parts[2], []).append((w, parts))
    _INDEX[id(lex)] = (by_vowel, by_coda)
    return _INDEX[id(lex)]


def candidates(word: str, lex: Lexicon, types: list[str] | None = None,
               limit: int = 50) -> list[Candidate]:
    if limit < 1:
        raise ValueError(f"limit must be at least 1, got {limit}")
    bad = sorted(set(types or []) - set(STABILITY_RANK))
    if bad:
        raise ValueError(f"unsupported candidate types {bad}; choose from {sorted(STABILITY_RANK)}")
    wanted = set(types) if types else set(STABILITY_RANK)
    target = word.strip().lower()
    by_vowel, by_coda = _index(lex)
    best: dict[str, str] = {}
    for pron in lex.lookup(word):
        parts = _parts(pron)
        if parts is None:
            continue
        pools = [by_vowel.get(parts[1], [])]
        if parts[2]:
            pools.append(by_coda.get(parts[2], []))
        for pool in pools:
            for w, wp in pool:
                if w == target:
                    continue
                t, _ = _classify_parts(parts, wp)
                if t in wanted and (w not in best or _order(t) < _order(best[w])):
                    best[w] = t
    out = [Candidate(w, t, lex.rank(w)) for w, t in best.items()]
    out.sort(key=lambda c: (STABILITY_RANK[c.type], c.rank is None, c.rank or 0, c.word))
    return out[:limit]


def _handler(args: argparse.Namespace):
    lex = load_lexicon(args.pron)
    if args.word2 is None:
        if args.candidates is None:
            raise SongtoolsError(None, None, "give a second word, or --candidates N for one word")
        if args.candidates < 1:
            raise SongtoolsError(None, None, "--candidates must be at least 1")
        found = candidates(args.word, lex, limit=args.candidates)
        return {
            "word": args.word, "lens": args.lens, "basis": BASIS,
            "candidates": [{"word": c.word, "type": c.type, "rank": c.rank,
                            "verdict": lens_verdict(RhymeResult(args.word, c.word, c.type, False, ""),
                                                    args.lens)}
                           for c in found],
        }, _candidates_text
    r = classify(args.word, args.word2, lex)
    return {"a": r.a, "b": r.b, "type": r.type, "multisyllable": r.multisyllable,
            "detail": r.detail, "lens": args.lens, "verdict": lens_verdict(r, args.lens),
            "basis": BASIS}, _pair_text


def _pair_text(r: dict) -> str:
    multi = " (multisyllable)" if r["multisyllable"] else ""
    return f"{r['a']} / {r['b']}: {r['verdict']}{multi}\n  {r['type']}: {r['detail']}"


def _candidates_text(r: dict) -> str:
    lines = [f"{r['word']}: {len(r['candidates'])} candidates ({r['lens']} lens)"]
    lines += [f"  {c['word']}\t{c['verdict']}" for c in r["candidates"]]
    return "\n".join(lines)


def register(subparsers) -> None:
    p = subparsers.add_parser("rhyme", help="classify a rhyme pair or list rhyme candidates")
    p.add_argument("word")
    p.add_argument("word2", nargs="?", default=None)
    p.add_argument("--lens", choices=["pattison", "webb"], default="pattison")
    p.add_argument("--candidates", type=int, default=None, metavar="N",
                   help="with one word: list up to N rhyming candidates")
    p.set_defaults(handler=_handler)
