"""Prosody: syllables, an eighth-note metric grid, ranked-constraint scoring and setting proposals."""

import argparse
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from songtools.cli import SongtoolsError
from songtools.pron import Lexicon, load_lexicon, word_class
from songtools.songfile import Section, parse_lyrics, parse_melody_md, read_text

BASIS = ("Hayes 2005 ranked constraints (simplified approximation); "
         "Pattison stress-to-beat rules (verified); Smith 2024 syncopation exemption")

LIMIT = ("Scoring is a simplified version of Hayes (2005), whose model matched "
         "listeners' preferred settings about 70% of the time on folk-song data.")

# Ranked constraints: rule -> (weight, severity). Order is the report order.
RULES: dict[str, tuple[int, Literal["strong", "soft"]]] = {
    "INVERSION": (100, "strong"),
    "STRESSED_OFFBEAT": (10, "soft"),
    # A word's secondary stress on a stronger beat than its own primary (Pattison's
    # "insecurities" case). Soft: weaker than a stressed off-beat, since secondary
    # stress is real stress, but stronger than an unstressed polysyllable on a downbeat.
    "SECONDARY_INVERSION": (8, "soft"),
    "UNSTRESSED_DOWNBEAT": (6, "soft"),
    "LAPSE": (5, "soft"),
    "FUNCTION_DOWNBEAT": (3, "soft"),
    "EMPTY_DOWNBEAT": (1, "soft"),
}
_ORDER = {r: i for i, r in enumerate(RULES)}
LOWEST_SLOT = -3  # proposals may start up to three eighths before the first downbeat
MAX_BARS = 8      # settings span at most 8 bars of 4/4 eighths
HIGHEST_SLOT = MAX_BARS * 8 - 1


@dataclass
class Syl:
    word: str
    label: str
    index_in_word: int
    word_len: int
    stress: int
    word_class: str
    estimated: bool


@dataclass
class Flag:
    rule: str
    syllable: int
    slot: int
    weight: int
    severity: Literal["strong", "soft"]
    message: str


@dataclass
class ProsodyReport:
    score: int
    flags: list[Flag]
    best_score: int
    best_slots: list[int]
    notation: str
    limit: str


# ---------------------------------------------------------------- syllables

_TOKEN = re.compile(r"[\w']+")
_VOWEL_LETTERS = "aeiouy"
_KEEP_TOGETHER_BEFORE = {"th", "sh", "ch", "ph", "wh"}  # mo-ther
_KEEP_TOGETHER_AFTER = {"ck", "ng"}                     # pock-et, sing-er


def _vowel_groups(w: str) -> list[tuple[int, int]]:
    groups: list[tuple[int, int]] = []
    i = 0
    while i < len(w):
        if w[i] in _VOWEL_LETTERS and not (i == 0 and w[i] == "y"):
            j = i
            while j < len(w) and w[j] in _VOWEL_LETTERS:
                j += 1
            groups.append((i, j))
            i = j
        else:
            i += 1
    return groups


def _even_split(w: str, k: int) -> list[str]:
    parts = [w[i * len(w) // k:(i + 1) * len(w) // k] for i in range(k)]
    return [p or "~" for p in parts]


def _split_labels(w: str, k: int) -> list[str]:
    """Display spellings for k syllables: split between vowel groups, else evenly."""
    if k <= 1:
        return [w or "~"]
    groups = _vowel_groups(w)
    if len(groups) > k and re.search(r"[^aeiouy](e|es|ed)$", w) and not w.endswith("le"):
        groups = groups[:-1]  # silent final e (before, hoped, hopes)
    if len(groups) != k:
        return _even_split(w, k)
    cuts = []
    for (_, end), (start, _) in zip(groups, groups[1:]):
        cluster = w[end:start]
        if len(cluster) == 1 or cluster in _KEEP_TOGETHER_BEFORE:
            cuts.append(end)
        elif cluster in _KEEP_TOGETHER_AFTER:
            cuts.append(start)
        else:
            cuts.append(end + 1)
    bounds = [0] + cuts + [len(w)]
    return [w[a:b] for a, b in zip(bounds, bounds[1:])]


def syllabify(lyric: str, lex: Lexicon) -> list[Syl]:
    out: list[Syl] = []
    for token in _TOKEN.findall(lyric.replace("’", "'").lower()):
        word = token.strip("'_").replace("_", "")
        if not word:
            continue
        pron = lex.lookup(token)[0]
        n = pron.syllables
        estimated = pron.estimated
        if n < 1:  # no vowel in the entry (hmm, mm, shh): sung as one syllable
            n, estimated = 1, True
        cls = word_class(token)
        if n == 1:
            stresses = [0 if cls == "function" else 1]
        else:
            stresses = list(pron.stresses)
            if cls == "function" and n == 2:
                stresses = [2 if s == 1 else s for s in stresses]
        for i, label in enumerate(_split_labels(word, n)):
            out.append(Syl(word, label, i, n, stresses[i], cls, estimated))
    return out


# ---------------------------------------------------------------- metric grid

def strength(slot: int) -> int:
    if slot % 8 == 0:
        return 4
    if slot % 8 == 4:
        return 3
    return 2 if slot % 2 == 0 else 1


def _eff(slot: int, nxt: int) -> int:
    """Effective slot: an odd slot held past the next eighth anticipates the next beat."""
    return slot + 1 if slot % 2 and nxt - slot > 1 else slot


def _local_rules(x: Syl, slot: int, nxt: int, last: bool) -> list[str]:
    """Rules that depend only on this syllable's slot and the next onset."""
    g = strength(_eff(slot, nxt))
    fired = []
    if x.stress == 1 and g == 1 and nxt - slot < 2:
        fired.append("STRESSED_OFFBEAT")
    if x.stress == 0 and x.word_len > 1 and g == 4:
        fired.append("UNSTRESSED_DOWNBEAT")
    if not last and nxt - slot - 1 >= 3:
        fired.append("LAPSE")
    if x.word_class == "function" and x.word_len == 1 and g == 4:
        fired.append("FUNCTION_DOWNBEAT")
    return fired


def _words(syls: list[Syl]) -> list[range]:
    starts = [i for i, x in enumerate(syls) if x.index_in_word == 0 or i == 0]
    return [range(a, b) for a, b in zip(starts, starts[1:] + [len(syls)])]


def _validate(syls: list[Syl], slots: list[int]) -> None:
    if len(slots) != len(syls):
        raise ValueError(f"{len(slots)} slots for {len(syls)} syllables")
    if any(b <= a for a, b in zip(slots, slots[1:])):
        raise ValueError("slots must be strictly increasing")


def score(syls: list[Syl], slots: list[int], line_slots: int = 16) -> tuple[int, list[Flag]]:
    _validate(syls, slots)
    n = len(syls)
    if n == 0:
        return 0, []
    nxts = list(slots[1:]) + [line_slots]
    effs = [_eff(s, x) for s, x in zip(slots, nxts)]
    found: list[tuple[str, int, int, str]] = []  # rule, syllable, slot, message
    for word in _words(syls):
        if len(word) < 2:
            continue
        stressed = [j for j in word if syls[j].stress == 1]
        if not stressed:
            continue
        top = max(stressed, key=lambda j: strength(effs[j]))
        for j in word:
            if syls[j].stress == 0 and strength(effs[j]) > strength(effs[top]):
                found.append(("INVERSION", j, slots[j],
                              f"unstressed '{syls[j].label}' sits on a stronger beat than "
                              f"stressed '{syls[top].label}' in '{syls[j].word}'"))
            elif syls[j].stress == 2 and strength(effs[j]) > strength(effs[top]):
                found.append(("SECONDARY_INVERSION", j, slots[j],
                              f"secondary stress '{syls[j].label}' sits on a stronger beat than "
                              f"primary '{syls[top].label}' in '{syls[j].word}'"))
    for i, (x, s, nxt) in enumerate(zip(syls, slots, nxts)):
        for rule in _local_rules(x, s, nxt, i == n - 1):
            msg = {
                "STRESSED_OFFBEAT": f"stressed '{x.label}' on a short off-beat note",
                "UNSTRESSED_DOWNBEAT": f"unstressed '{x.label}' of '{x.word}' on a downbeat",
                "LAPSE": f"{nxt - s - 1} empty slots after '{x.label}'",
                "FUNCTION_DOWNBEAT": f"function word '{x.word}' on a downbeat",
            }[rule]
            found.append((rule, i, s, msg))
    if 0 not in effs:
        after = next((i for i, s in enumerate(slots) if s > 0), n - 1)
        found.append(("EMPTY_DOWNBEAT", after, 0,
                      "no syllable on, or anticipating, the downbeat (slot 0)"))
    found.sort(key=lambda f: (f[1], _ORDER[f[0]]))
    flags = [Flag(r, i, s, RULES[r][0], RULES[r][1], m) for r, i, s, m in found]
    return sum(f.weight for f in flags), flags


# ---------------------------------------------------------------- proposals
#
# Exact DP over syllables x slots. The cost of syllable i depends on (s_i, s_{i+1}),
# so it is charged on the transition i -> i+1 (the last syllable uses line_slots as
# its next onset). EMPTY_DOWNBEAT is also a pair cost: effective slots are
# non-decreasing, so slot 0 is covered iff, at the unique pair (s_i, s_{i+1}) that
# crosses from < 0 to >= 0, either s_{i+1} == 0 is a real onset or s_i == -1
# (which then always anticipates into 0).
# INVERSION couples all syllables of a word. The state carries a word state
# (M, reached): M is a guess of the strongest strength among the word's stress-1
# syllables (0 = word has no INVERSION constraint). Stress-1 syllables must not
# exceed M and one must equal it (checked at the word's last syllable); every
# stress-0 syllable stronger than M costs 100 immediately, and every stress-2
# syllable stronger than M costs SECONDARY_INVERSION's weight. Exactly one guess is
# valid for any slot list, so the DP is exact. State per syllable: (slot, M, reached).
# Ties: the stated cost leaves anticipations free, so equally scored settings are
# ranked first by fewest anticipated (syncopated) syllables, then by the
# lexicographically smallest slot list. Costs are scaled by _TIE so the anticipation
# count is a strict secondary key and never outweighs a rule weight.
_TIE = 1024


def _initial_states(syls: list[Syl], i: int) -> list[tuple[int, bool]]:
    word = syls[i:i + syls[i].word_len]
    if syls[i].word_len > 1 and any(x.stress == 1 for x in word):
        return [(m, False) for m in (1, 2, 3, 4)]
    return [(0, True)]


def propose(syls: list[Syl], bars: int = 2) -> list[int]:
    n = len(syls)
    if n == 0:
        return []
    if not 1 <= bars <= MAX_BARS:
        raise ValueError(f"bars must be 1..{MAX_BARS}, got {bars}")
    lo, hi, line = LOWEST_SLOT, bars * 8 - 1, bars * 8
    if n > hi - lo + 1:
        raise ValueError(f"{n} syllables do not fit in {bars} bars of eighth notes")
    last_in_word = [i == n - 1 or syls[i + 1].index_in_word == 0 for i in range(n)]
    states: list[list[tuple[int, bool]]] = []
    for i in range(n):
        if syls[i].index_in_word == 0 or i == 0:
            states.append(_initial_states(syls, i))
        else:
            m_vals = {m for m, _ in states[-1]}
            states.append(sorted({(m, r) for m in m_vals for r in (False, True)}
                                 if m_vals != {0} else {(0, True)}))

    def base(i: int, s: int, nxt: int) -> tuple[int, int]:
        """Cost of syllable i's local rules plus the slot-0 crossing; and its strength."""
        last = i == n - 1
        c = sum(RULES[r][0] for r in _local_rules(syls[i], s, nxt, last))
        if s < 0 <= nxt and not (s == -1 or (nxt == 0 and not last)):
            c += RULES["EMPTY_DOWNBEAT"][0]
        e = _eff(s, nxt)
        return c * _TIE + (e != s), strength(e)

    def step(i: int, ws: tuple[int, bool], g: int):
        """Word-state update for syllable i at strength g: (extra cost, new state) or None."""
        m, reached = ws
        extra = 0
        if m:
            st = syls[i].stress
            if st == 1:
                if g > m:
                    return None
                reached = reached or g == m
            elif st == 0 and g > m:
                extra = RULES["INVERSION"][0] * _TIE
            elif st == 2 and g > m:
                extra = RULES["SECONDARY_INVERSION"][0] * _TIE
            if last_in_word[i] and not reached:
                return None
        return extra, (m, reached)

    def successors(i: int, ws_after: tuple[int, bool]) -> list[tuple[int, bool]]:
        return [ws_after] if not last_in_word[i] else states[i + 1]

    def rng(i: int) -> range:
        return range(lo + i, hi - (n - 1 - i) + 1)

    # value[i][(slot, ws)] = minimal cost of syllables i..n-1 (and the crossing) given state
    value: list[dict[tuple[int, tuple[int, bool]], int]] = [{} for _ in range(n)]
    for s in rng(n - 1):
        c, g = base(n - 1, s, line)
        for ws in states[n - 1]:
            r = step(n - 1, ws, g)
            if r is not None:
                value[n - 1][(s, ws)] = c + r[0]
    for i in range(n - 2, -1, -1):
        nxt_range = rng(i + 1)
        for s in rng(i):
            bases = [(nxt, *base(i, s, nxt)) for nxt in nxt_range if nxt > s]
            for ws in states[i]:
                best = None
                for nxt, c, g in bases:
                    r = step(i, ws, g)
                    if r is None:
                        continue
                    for ws2 in successors(i, r[1]):
                        v = value[i + 1].get((nxt, ws2))
                        if v is not None and (best is None or c + r[0] + v < best):
                            best = c + r[0] + v
                if best is not None:
                    value[i][(s, ws)] = best

    def start_cost(s: int) -> int:
        return RULES["EMPTY_DOWNBEAT"][0] * _TIE if s > 0 else 0

    opt = min(start_cost(s) + v for (s, _), v in value[0].items())
    # Forward pass: the smallest slot that keeps some optimal path alive, at every step.
    for s in rng(0):
        cands = [(ws, start_cost(s)) for ws in states[0]
                 if (s, ws) in value[0] and start_cost(s) + value[0][(s, ws)] == opt]
        if cands:
            slots = [s]
            break
    for i in range(n - 1):
        s = slots[-1]
        for nxt in rng(i + 1):
            if nxt <= s:
                continue
            c, g = base(i, s, nxt)
            alive = []
            for ws, pre in cands:
                r = step(i, ws, g)
                if r is None:
                    continue
                for ws2 in successors(i, r[1]):
                    v = value[i + 1].get((nxt, ws2))
                    if v is not None and pre + c + r[0] + v == opt:
                        alive.append((ws2, pre + c + r[0]))
            if alive:
                slots.append(nxt)
                cands = alive
                break
    return slots


def check(syls: list[Syl], slots: list[int] | None, bars: int = 2) -> ProsodyReport:
    if not 1 <= bars <= MAX_BARS:
        raise ValueError(f"bars must be 1..{MAX_BARS}, got {bars}")
    if slots is not None:
        _validate(syls, slots)
        if slots and not (LOWEST_SLOT <= slots[0] and slots[-1] <= HIGHEST_SLOT):
            raise ValueError(f"slots must lie in {LOWEST_SLOT}..{HIGHEST_SLOT}")
    bars = max(bars, -(-(len(syls) + LOWEST_SLOT) // 8))  # room for every syllable
    if slots:
        bars = max(bars, max(slots) // 8 + 1)
    if bars > MAX_BARS:
        raise ValueError(f"{len(syls)} syllables do not fit in {MAX_BARS} bars of eighth notes")
    line = bars * 8
    best = propose(syls, bars)
    best_score = score(syls, best, line)[0]
    if slots is None:
        slots = best
    total, flags = score(syls, slots, line)
    if total < best_score:  # given slots outside the proposal range can beat it
        best, best_score = list(slots), total
    return ProsodyReport(total, flags, best_score, best, notation(syls, slots), LIMIT)


def notation(syls: list[Syl], slots: list[int]) -> str:
    text = ""
    prev = None
    for i, (x, s) in enumerate(zip(syls, slots)):
        label = x.label.upper() if s % 2 == 0 else x.label
        if prev is None:
            text = ("| " if s >= 0 else "") + label
        else:
            bars = sum(1 for m in range(prev + 1, s + 1) if m % 8 == 0)
            if x.index_in_word > 0:
                text += "-" + (" |" * bars + " " if bars else "") + label
            else:
                text += " " + "| " * bars + label
        prev = s
    return text


def compare_lines(a: list[Syl], b: list[Syl]) -> dict:
    pa = "".join("1" if x.stress >= 1 else "0" for x in a)
    pb = "".join("1" if x.stress >= 1 else "0" for x in b)
    return {"syllables": [len(a), len(b)], "stress_pattern": [pa, pb],
            "matches": len(a) == len(b) and pa == pb}


# ---------------------------------------------------------------- CLI

def _read(path: Path) -> str:
    return read_text(path, path.name)


def _find_section(sections: list[Section], name: str, file: str) -> Section:
    for s in sections:
        if s.name.lower() == name.lower():
            return s
    raise SongtoolsError(file, None, f"no section named {name!r}")


def _syl_dict(x: Syl) -> dict:
    return {"label": x.label, "word": x.word, "stress": x.stress,
            "word_class": x.word_class, "estimated": x.estimated}


def _handler(args: argparse.Namespace):
    lex = load_lexicon(args.pron)
    song = Path(args.song_dir)
    lyrics_path = song / "lyrics.md"
    sections = parse_lyrics(_read(lyrics_path), str(lyrics_path))
    sec = _find_section(sections, args.section, str(lyrics_path))
    if not 1 <= args.line <= len(sec.lines):
        raise SongtoolsError(str(lyrics_path), None,
                             f"section {sec.name!r} has no line {args.line} "
                             f"({len(sec.lines)} lines)")
    line = sec.lines[args.line - 1]
    syls = syllabify(line.lyric, lex)
    if not syls:
        raise SongtoolsError(str(lyrics_path), line.number, "line has no syllables")

    slots: list[int] | None = None
    source = "proposal"
    if args.slots is not None:
        try:
            slots = [int(t) for t in args.slots.split()]
        except ValueError:
            raise SongtoolsError(None, None, "--slots must be space-separated integers") from None
        source, err_file, err_line = "slots", str(lyrics_path), line.number
    else:
        melody_path = song / "melody.md"
        if melody_path.exists():
            melody = parse_melody_md(_read(melody_path), str(melody_path))
            entry = next((v for (name, idx), v in melody.items()
                          if name.lower() == sec.name.lower() and idx == args.line), None)
            if entry is not None:
                slots = [slot for _, slot in entry]
                source, err_file, err_line = "melody", str(melody_path), None
    if slots is not None:
        if len(slots) != len(syls):
            raise SongtoolsError(err_file, err_line,
                                 f"{len(slots)} slots given for {len(syls)} syllables "
                                 f"in {sec.name!r} line {args.line}")
        if any(b <= a for a, b in zip(slots, slots[1:])):
            raise SongtoolsError(err_file, err_line, "slots must be strictly increasing")
        if not (LOWEST_SLOT <= slots[0] and slots[-1] <= HIGHEST_SLOT):
            raise SongtoolsError(err_file, err_line,
                                 f"slots must lie in {LOWEST_SLOT}..{HIGHEST_SLOT} "
                                 f"(3 pickup eighths, at most {MAX_BARS} bars)")

    try:
        rep = check(syls, slots)
    except ValueError as e:  # e.g. more syllables than fit in MAX_BARS
        raise SongtoolsError(str(lyrics_path), line.number, str(e)) from None
    shown = slots if slots is not None else rep.best_slots
    result = {
        "section": sec.name, "line": args.line, "lyric": line.lyric,
        "syllables": [_syl_dict(x) for x in syls],
        "source": source, "slots": shown,
        "score": rep.score, "flags": [asdict(f) for f in rep.flags],
        "notation": rep.notation,
        "best_score": rep.best_score, "best_slots": rep.best_slots,
        "best_notation": notation(syls, rep.best_slots),
        "estimated": any(x.estimated for x in syls),
        "limit": rep.limit, "basis": BASIS,
    }
    if args.compare:
        rows = []
        for other in sections:
            if other is sec or other.kind != sec.kind:
                continue
            if args.line > len(other.lines):
                rows.append({"section": other.name, "lyric": None,
                             "note": f"no line {args.line}"})
                continue
            o = other.lines[args.line - 1]
            rows.append({"section": other.name, "lyric": o.lyric,
                         **compare_lines(syls, syllabify(o.lyric, lex))})
        result["compare"] = rows
    return result, to_text


def to_text(r: dict) -> str:
    out = [f"{r['section']} line {r['line']}: {r['lyric']}",
           f"  {r['source']}: {r['notation']}  (score {r['score']})"]
    for f in r["flags"]:
        out.append(f"  - {f['rule']} ({f['severity']}, {f['weight']}) at slot {f['slot']}: "
                   f"{f['message']}")
    out.append(f"  best: {r['best_notation']}  (score {r['best_score']}, "
               f"slots {' '.join(map(str, r['best_slots']))})")
    if r["estimated"]:
        words = sorted({s["word"] for s in r["syllables"] if s["estimated"]})
        out.append(f"  note: estimated pronunciation for {', '.join(words)}")
    for c in r.get("compare", []):
        if c["lyric"] is None:
            out.append(f"  compare {c['section']}: {c['note']}")
        else:
            verdict = "matches" if c["matches"] else "differs"
            out.append(f"  compare {c['section']}: {verdict} (syllables {c['syllables'][0]}/"
                       f"{c['syllables'][1]}, stresses {c['stress_pattern'][0]}/"
                       f"{c['stress_pattern'][1]})")
    out.append(f"Limit: {r['limit']}")
    return "\n".join(out)


def register(subparsers) -> None:
    p = subparsers.add_parser("prosody", help="score a lyric line's setting on the beat grid")
    p.add_argument("song_dir", type=Path)
    p.add_argument("--section", required=True, metavar="NAME")
    p.add_argument("--line", required=True, type=int, metavar="N",
                   help="1-based line index within the section")
    p.add_argument("--slots", default=None, metavar='"0 1 2 ..."',
                   help="eighth-note slot per syllable (8 per 4/4 bar, 0 = first downbeat)")
    p.add_argument("--compare", action="store_true",
                   help="compare with the same line in every section of the same kind")
    p.set_defaults(handler=_handler)
