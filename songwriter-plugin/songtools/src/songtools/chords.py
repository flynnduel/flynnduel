"""Chord spelling, parsing, naming and key-aware transposition."""

import argparse
import re
from dataclasses import asdict, dataclass

from pychord import Chord as _PyChord

from songtools.cli import SongtoolsError

BASIS = "chord spelling (standard theory); pychord quality parser"

NOTE_PC: dict[str, int] = {}
for _letter, _pc in zip("CDEFGAB", (0, 2, 4, 5, 7, 9, 11)):
    NOTE_PC[_letter] = _pc
    for _sharp in ("#", "♯"):
        NOTE_PC[_letter + _sharp] = (_pc + 1) % 12
    for _flat in ("b", "♭"):
        NOTE_PC[_letter + _flat] = (_pc - 1) % 12

SHARPS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FLATS = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
FLAT_KEYS = frozenset({"F", "Bb", "Eb", "Ab", "Db", "Gb", "Dm", "Gm", "Cm", "Fm", "Bbm", "Ebm"})

# Intervals from the root; the order is the fixed order used by names_for.
QUALITIES: dict[str, tuple[int, ...]] = {
    "": (0, 4, 7),
    "m": (0, 3, 7),
    "5": (0, 7),
    "6": (0, 4, 7, 9),
    "m6": (0, 3, 7, 9),
    "7": (0, 4, 7, 10),
    "maj7": (0, 4, 7, 11),
    "m7": (0, 3, 7, 10),
    "m7b5": (0, 3, 6, 10),
    "dim": (0, 3, 6),
    "dim7": (0, 3, 6, 9),
    "aug": (0, 4, 8),
    "sus2": (0, 2, 7),
    "sus4": (0, 5, 7),
    "add9": (0, 2, 4, 7),
    "9": (0, 2, 4, 7, 10),
    "7#9": (0, 3, 4, 7, 10),
    "7sus4": (0, 5, 7, 10),
    "69": (0, 2, 4, 7, 9),
    "mmaj7": (0, 3, 7, 11),
    "11": (0, 2, 4, 5, 7, 10),
    "13": (0, 2, 4, 5, 7, 9, 10),
}

_SYMBOL = re.compile(r"^([A-G][#b♯♭]?)(.*?)(?:/([A-G][#b♯♭]?))?$")
_NO_CHORD = {"N.C.", "N.C", "NC", "N/C"}


@dataclass
class Chord:
    symbol: str
    root: str
    quality: str
    bass: str | None
    pcs: frozenset[int]
    tones: list[str]


def _norm(note: str) -> str:
    return note.replace("♯", "#").replace("♭", "b")


def _flat_key(key: str | None) -> bool:
    return key is not None and _norm(key.strip()) in FLAT_KEYS


def spell(pc: int, key: str | None = None) -> str:
    """Name a pitch class: flats in flat keys, sharps otherwise."""
    return (FLATS if _flat_key(key) else SHARPS)[pc % 12]


def _spell_flat(pc: int, flat: bool) -> str:
    return (FLATS if flat else SHARPS)[pc % 12]


def _pc_of(note: str) -> int:
    try:
        return NOTE_PC[note]
    except KeyError:
        raise ValueError(f"not a note name: {note!r}") from None


def _pychord_intervals(quality: str) -> tuple[str, tuple[int, ...]]:
    """Parse the quality with pychord on a C root; returns (quality, intervals)."""
    pc = _PyChord("C" + quality)  # raises ValueError on unknown qualities
    out = []
    for comp in pc.components():
        m = re.fullmatch(r"([A-G])([#b]*)", comp)
        if not m:
            raise ValueError(f"unexpected component {comp!r}")
        out.append((NOTE_PC[m.group(1)] + m.group(2).count("#") - m.group(2).count("b")) % 12)
    return pc.quality.quality, tuple(out)


def _quality_intervals(quality: str) -> tuple[str, tuple[int, ...]]:
    """Canonical quality and intervals: pychord first, QUALITIES table as fallback."""
    try:
        _, ivs = _pychord_intervals(quality)
        return ("sus4" if quality == "sus" else quality), ivs
    except Exception:
        pass
    alias = "sus4" if quality == "sus" else quality
    if alias in QUALITIES:
        return alias, QUALITIES[alias]
    raise ValueError(f"unknown chord quality: {quality!r}")


def parse_chord(symbol: str) -> Chord:
    m = _SYMBOL.match(symbol.strip()) if isinstance(symbol, str) else None
    if not m or "/" in m.group(2):
        raise ValueError(f"invalid chord symbol: {symbol!r}")
    root, quality, bass = _norm(m.group(1)), _norm(m.group(2)), m.group(3)
    bass = _norm(bass) if bass else None
    try:
        quality, ivs = _quality_intervals(quality)
    except ValueError:
        raise ValueError(f"invalid chord symbol: {symbol!r}") from None
    root_pc = _pc_of(root)
    flat = "b" in root or (bass is not None and "b" in bass)
    pcs = frozenset((root_pc + i) % 12 for i in ivs)
    tones = [root] + [_spell_flat((root_pc + i) % 12, flat) for i in ivs[1:]]
    if bass is not None:
        pcs = pcs | {_pc_of(bass)}
    text = root + quality + (f"/{bass}" if bass else "")
    return Chord(text, root, quality, bass, pcs, tones)


def is_no_chord(symbol: str) -> bool:
    return symbol.strip().upper() in _NO_CHORD


def transpose(symbol: str, semitones: int, key: str | None = None) -> str:
    """Move root and bass separately; respell for the key (or keep flats if written)."""
    c = parse_chord(symbol)
    flat = _flat_key(key) if key is not None else ("b" in c.root or (c.bass is not None and "b" in c.bass))
    root = _spell_flat(_pc_of(c.root) + semitones, flat)
    out = root + c.quality
    if c.bass:
        out += "/" + _spell_flat(_pc_of(c.bass) + semitones, flat)
    return out


def names_for(pcs: set[int], bass_pc: int | None = None) -> list[str]:
    """Chord names whose pitch classes equal pcs (or equal it with the fifth missing).

    Returns [] when bass_pc is given but is not among pcs.
    """
    target = frozenset(p % 12 for p in pcs)
    if bass_pc is not None:
        bass_pc %= 12
        if bass_pc not in target:
            return []
    found = []
    for qi, (q, ivs) in enumerate(QUALITIES.items()):
        for root in range(12):
            full = frozenset((root + i) % 12 for i in ivs)
            if full == target:
                no5 = 0
            elif 7 in ivs and len(ivs) > 3 and (full - {(root + 7) % 12}) == target:
                no5 = 1
            else:
                continue
            name = SHARPS[root] + q + ("(no5)" if no5 else "")
            if bass_pc is not None and bass_pc != root:
                name += "/" + SHARPS[bass_pc]
            found.append((bass_pc is None or bass_pc != root, no5, qi, root, name))
    found.sort()
    return [f[-1] for f in found]


def to_text(result: dict) -> str:
    if "names" in result:
        return "\n".join(result["names"]) or "(no matching chord names)"
    if "tones" in result:
        return f"{result['symbol']}: {' '.join(result['tones'])}"
    if "result" in result:
        return f"{result['symbol']} -> {result['result']}"
    return result["name"]


def _wrap(fn):
    try:
        return fn()
    except ValueError as e:
        raise SongtoolsError(None, None, str(e)) from None


def _note(name: str) -> int:
    return _wrap(lambda: _pc_of(_norm(name)))


def _h_spell(args: argparse.Namespace):
    return {"pc": args.pc % 12, "key": args.key, "name": spell(args.pc, args.key)}, to_text


def _h_transpose(args: argparse.Namespace):
    res = _wrap(lambda: transpose(args.symbol, args.semitones, args.key))
    return {"symbol": args.symbol, "semitones": args.semitones, "key": args.key, "result": res}, to_text


def _h_names(args: argparse.Namespace):
    pcs = {_note(n) for n in args.notes}
    bass = _note(args.bass) if args.bass else None
    return {"pcs": sorted(pcs), "bass": args.bass, "names": names_for(pcs, bass)}, to_text


def _h_parse(args: argparse.Namespace):
    c = _wrap(lambda: parse_chord(args.symbol))
    d = asdict(c)
    d["pcs"] = sorted(c.pcs)
    return d, to_text


def register(subparsers) -> None:
    p = subparsers.add_parser("chord", help="chord spelling, parsing, naming and transposition")
    sub = p.add_subparsers(dest="chord_command", required=True)
    s = sub.add_parser("spell", help="spell a pitch class (0-11)")
    s.add_argument("pc", type=int)
    s.add_argument("--key", default=None)
    s.set_defaults(handler=_h_spell)
    t = sub.add_parser("transpose", help="transpose a chord symbol")
    t.add_argument("symbol")
    t.add_argument("semitones", type=int)
    t.add_argument("--key", default=None)
    t.set_defaults(handler=_h_transpose)
    n = sub.add_parser("names", help="chord names for a set of notes")
    n.add_argument("notes", nargs="+", metavar="NOTE")
    n.add_argument("--bass", default=None, metavar="NOTE")
    n.set_defaults(handler=_h_names)
    q = sub.add_parser("parse", help="parse a chord symbol")
    q.add_argument("symbol")
    q.set_defaults(handler=_h_parse)
