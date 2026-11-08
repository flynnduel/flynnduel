"""Harmony analysis: key scoring, simplified Everett system classification, numerals.

Labels honestly and flags ambiguity; it never claims one "correct" reading.
"""

import argparse
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from songtools.chords import NOTE_PC, Chord, is_no_chord, parse_chord
from songtools.cli import SongtoolsError

BASIS = ("Everett 2004 tonal systems (simplified); de Clercq & Temperley corpus (verified); "
         "Richards loop major bias (verified)")

# de Clercq & Temperley corpus base rates (percent).
CORPUS = {"root_share": {"I": 32.8, "IV": 22.6, "V": 16.3, "bVII": 8.1, "VI": 7.2, "bVI": 4.0},
          "chorus_cadence_pre_tonic": {"V": 32.0, "IV": 18.5}}

Mode = Literal["major", "minor", "mixolydian", "dorian"]
MODES: tuple[str, ...] = ("major", "minor", "mixolydian", "dorian")  # also the tie-break order
SCALES: dict[str, tuple[int, ...]] = {
    "major": (0, 2, 4, 5, 7, 9, 11),
    "minor": (0, 2, 3, 5, 7, 8, 10),
    "mixolydian": (0, 2, 4, 5, 7, 9, 10),
    "dorian": (0, 2, 3, 5, 7, 9, 10),
}
_MODE_WORDS = {"": "major", "major": "major", "maj": "major", "m": "minor", "min": "minor", "minor": "minor",
               "aeolian": "minor", "mixolydian": "mixolydian", "dorian": "dorian"}
_MAJOR_NAMES = ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
_MINOR_NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "Bb", "B"]
_PENTATONIC_MINOR = frozenset({0, 3, 5, 7, 10})

_ROMAN = ["I", "bII", "II", "bIII", "III", "IV", "#IV", "V", "bVI", "VI", "bVII", "VII"]
_ARABIC = ["1", "b2", "2", "b3", "3", "4", "#4", "5", "b6", "6", "b7", "7"]
_DOMINANT_QUALITIES = frozenset({"7", "9", "11", "13", "7#9", "7sus4", "7#5"})

_LABELS = {
    "5": "5 — power-chord / minor-pentatonic rock",
    "4": "4 — blues-based I7–IV7",
    "1b": "1b — functional minor",
    "3a": "3a — functional major with modal mixture",
    "1a": "1a — functional major",
    "2": "2 — modal (mixolydian / dorian / aeolian without V)",
    "6a": "6a — chromatic / other",
}
_LABEL_TAIL = " (simplified from Everett 2004, Table 1)"
_DOUBLE_PLAGAL = "double-plagal ♭VII–IV–I (Everett: chromatic descending fourths, not modal)"
_CADENCE_NOTE = "V–I is still the most common chorus-ending cadence (32%); IV–I 18.5%"
_DUAL_WINDOW = 0.15


@dataclass
class KeyCandidate:
    tonic: str
    mode: Mode
    score: float


@dataclass
class HarmonyAnalysis:
    key: KeyCandidate
    confidence: float
    system: str
    system_label: str
    numerals: list[str]
    nashville: list[str]
    symbols: list[str]
    notes: list[str]
    dual_reading: dict | None
    errors: list[str]


def _pc(note: str) -> int:
    return NOTE_PC[note]


def _is_minor(chord: Chord) -> bool:
    """Minor-family quality: lower-case numeral (dim / half-dim included)."""
    q = chord.quality
    return q.startswith("m") and not q.startswith("maj") or q.startswith("dim")


def _numeral_suffix(quality: str) -> str:
    if quality == "m7b5":
        return "ø"
    if quality == "dim":
        return "°"
    if quality == "dim7":
        return "°7"
    if quality == "aug":
        return "+"
    if quality.startswith("m") and not quality.startswith("maj"):
        return quality[1:]  # m, m6, m7, mmaj7 -> "", 6, 7, maj7 (case carries the minor)
    return quality


def _interval(note: str, tonic: str) -> int:
    return (_pc(note) - _pc(tonic)) % 12


def numeral(chord: Chord, tonic: str) -> str:
    """Roman numeral relative to the parallel major of `tonic`.

    Case from quality (minor -> lower, dim -> °, m7b5 -> ø), extensions kept (V7, Imaj7, IVsus4).
    A slash bass is appended as "/" + its Nashville degree relative to the tonic (C/E in C -> I/3).
    """
    base = _ROMAN[_interval(chord.root, tonic)]
    if _is_minor(chord):
        base = re.sub(r"[IV]+", lambda m: m.group().lower(), base)
    out = base + _numeral_suffix(chord.quality)
    if chord.bass and chord.bass != chord.root:
        out += "/" + _ARABIC[_interval(chord.bass, tonic)]
    return out


def nashville(chord: Chord, tonic: str) -> str:
    """Nashville number: degree + quality (6m, b7, 57); power chords as 1(5); bass degree is tonic-relative."""
    q = chord.quality
    q = {"dim": "°", "dim7": "°7", "m7b5": "ø", "aug": "+", "5": "(5)"}.get(q, q)
    out = _ARABIC[_interval(chord.root, tonic)] + q
    if chord.bass and chord.bass != chord.root:
        out += "/" + _ARABIC[_interval(chord.bass, tonic)]
    return out


def _tonic_name(pc: int, mode: str) -> str:
    return (_MAJOR_NAMES if mode in ("major", "mixolydian") else _MINOR_NAMES)[pc]


def _parse_key(key: str) -> tuple[str, str]:
    m = re.match(r"^\s*([A-Ga-g][#b♯♭]?)\s*([A-Za-z]*)\s*$", key or "")
    if m:
        note = m.group(1)[0].upper() + m.group(1)[1:]
        mode = _MODE_WORDS.get(m.group(2).lower())
        if mode and note in NOTE_PC:
            return note.replace("♯", "#").replace("♭", "b"), mode
    raise SongtoolsError(None, None, f"invalid key {key!r} (examples: G, Am, 'A dorian', 'D mixolydian')")


def _score(chords: list[Chord], tonic_pc: int, mode: str) -> int:
    scale = {(tonic_pc + i) % 12 for i in SCALES[mode]}
    roots = [_pc(c.root) for c in chords]
    s = 2 * (roots[0] == tonic_pc) + 3 * (roots[-1] == tonic_pc)
    s += sum(c.pcs <= scale for c in chords) + sum(r == tonic_pc for r in roots)
    return s


def _diatonic(chords: list[Chord], tonic: str, mode: str) -> bool:
    scale = {(_pc(tonic) + i) % 12 for i in SCALES[mode]}
    return all(c.pcs <= scale for c in chords)


def _classify(chords: list[Chord], tonic: str, mode: str) -> str:
    iv = [(_interval(c.root, tonic), _is_minor(c), c.quality) for c in chords]
    pent = {(_pc(tonic) + i) % 12 for i in _PENTATONIC_MINOR}
    if all(c.quality == "5" and _pc(c.root) in pent for c in chords):
        return "5"
    if any(i == 0 and q in _DOMINANT_QUALITIES for i, _, q in iv) and \
            any(i == 5 and q in _DOMINANT_QUALITIES for i, _, q in iv):
        return "4"
    major_v = any(i == 7 and not minor and not q.startswith("dim") for i, minor, q in iv)
    if mode == "minor" and major_v:
        return "1b"
    if mode == "major":
        mixture = any((i in (10, 8, 3) and not minor) or (i == 5 and minor) for i, minor, _ in iv)
        if major_v and mixture:
            return "3a"
        if _diatonic(chords, tonic, "major"):
            return "1a"
    elif _diatonic(chords, tonic, mode):
        return "2"
    return "6a"


def _contains(seq: list[str], sub: list[str]) -> bool:
    return any(seq[i:i + len(sub)] == sub for i in range(len(seq) - len(sub) + 1))


def _notes(chords: list[Chord], numerals: list[str], tonic: str) -> list[str]:
    notes = []
    base = [n.split("/")[0] for n in numerals]
    if _contains(base, ["bVII", "IV", "I"]):
        notes.append(_DOUBLE_PLAGAL)
    if len(chords) >= 2:
        a, b = chords[-2], chords[-1]
        if _interval(b.root, tonic) == 0 and not _is_minor(b) and not _is_minor(a) \
                and _interval(a.root, tonic) in (5, 7):
            notes.append(_CADENCE_NOTE)
    return notes


def analyze(chords: list[str], key: str | None = None) -> HarmonyAnalysis:
    parsed: list[Chord] = []
    errors: list[str] = []
    for sym in chords:
        if is_no_chord(sym):
            continue
        try:
            parsed.append(parse_chord(sym))
        except ValueError:
            errors.append(sym)
    if not parsed:
        raise SongtoolsError(None, None, "no valid chords to analyse")
    ranked = sorted(((-_score(parsed, pc, m), MODES.index(m), pc, m) for pc in range(12) for m in MODES))
    cands = [(-neg, m, pc) for neg, _, pc, m in ranked]
    if key is not None:
        tonic, mode = _parse_key(key)
        score = _score(parsed, _pc(tonic), mode)
        top, confidence, dual = (score, mode, _pc(tonic)), 1.0, None  # an explicit key is not second-guessed
    else:
        top = cands[0]
        confidence = top[0] / (top[0] + cands[1][0]) if top[0] + cands[1][0] else 0.5
        tonic, mode = _tonic_name(top[2], top[1]), top[1]
        dual = None
        # Prefer the relative major/minor (same pitch set) as the competing reading, else the best other tonic.
        relative = (top[2] + (9 if top[1] == "major" else 3)) % 12
        others = [c for c in cands[1:] if c[2] != top[2]]
        rel = next((c for c in others if c[2] == relative and {c[1], top[1]} == {"major", "minor"}), None)
        other = rel if rel and top[0] / (top[0] + rel[0]) - 0.5 <= _DUAL_WINDOW else others[0]
        # "Within 15%": the confidence share is within 0.15 of a coin flip.
        if other[0] > 0 and top[0] / (top[0] + other[0]) - 0.5 <= _DUAL_WINDOW:
            o_tonic = _tonic_name(other[2], other[1])
            dual = {"tonic": o_tonic, "mode": other[1], "score": other[0],
                    "numerals": [numeral(c, o_tonic) for c in parsed]}
    numerals = [numeral(c, tonic) for c in parsed]
    system = _classify(parsed, tonic, mode)
    notes = _notes(parsed, numerals, tonic)
    if key is None and cands[1][2] == top[2] and cands[1][0] == top[0]:
        notes.append(f"Mode is ambiguous: {tonic} {cands[1][1]} fits equally well; "
                     f"{mode} is chosen because listeners lean major (Richards).")
    if dual:
        notes.append(f"Ambiguous key: also reads as {dual['tonic']} {dual['mode']}; "
                     "both are valid, so choose by where the melody rests.")
    return HarmonyAnalysis(KeyCandidate(tonic, mode, float(top[0])), round(confidence, 3), system,
                           _LABELS[system] + _LABEL_TAIL, numerals,
                           [nashville(c, tonic) for c in parsed], [c.symbol for c in parsed],
                           notes, dual, errors)


def _is_chorus(name: str) -> bool:
    return "chorus" in name.lower()


def analyze_song(progressions: dict[str, list[tuple[str, float]]]) -> dict:
    """Analyse each section, then list song-level modulations.

    Returns {"sections": {name: analysis dict}, "modulations": [str], "skipped": [names with no chords],
    "corpus": CORPUS, "basis": BASIS}.
    """
    sections: dict[str, HarmonyAnalysis] = {}
    skipped: list[str] = []
    for name, prog in progressions.items():
        try:
            sections[name] = analyze([c for c, _ in prog])
        except SongtoolsError:
            skipped.append(name)
    mods: list[str] = []
    names = list(sections)
    choruses = [n for n in names if _is_chorus(n)]
    lift_pair = None
    if len(choruses) >= 2:
        prev, last = choruses[-2], choruses[-1]
        d = (_pc(sections[last].key.tonic) - _pc(sections[prev].key.tonic)) % 12
        if d in (1, 2):
            lift_pair = (prev, last)
            mods.append(f"truck-driver lift (Everett 3b): {prev} in {sections[prev].key.tonic} -> "
                        f"{last} in {sections[last].key.tonic} (+{d} semitone{'s' if d > 1 else ''})")
    for a, b in zip(names, names[1:]):
        ka, kb = sections[a], sections[b]
        if (a, b) == lift_pair or _pc(ka.key.tonic) == _pc(kb.key.tonic):
            continue
        if ka.dual_reading or kb.dual_reading or min(ka.confidence, kb.confidence) <= 0.65:
            continue  # ambiguous readings: do not claim a key change
        mods.append(f"possible key change: {a} in {ka.key.tonic} {ka.key.mode} -> "
                    f"{b} in {kb.key.tonic} {kb.key.mode}")
    return {"sections": {n: asdict(a) for n, a in sections.items()}, "modulations": mods,
            "skipped": skipped, "corpus": CORPUS, "basis": BASIS}


def to_text(result: dict) -> str:
    def block(a: dict, indent: str = "") -> list[str]:
        k = a["key"]
        lines = [f"{indent}Key: {k['tonic']} {k['mode']} (confidence {a['confidence']})",
                 f"{indent}System: {a['system_label']}",
                 f"{indent}Roman:     {' '.join(a['numerals'])}",
                 f"{indent}Nashville: {' '.join(a['nashville'])}"]
        if a["dual_reading"]:
            d = a["dual_reading"]
            lines.append(f"{indent}Also reads as {d['tonic']} {d['mode']}: {' '.join(d['numerals'])}")
        lines += [f"{indent}Note: {n}" for n in a["notes"]]
        if a["errors"]:
            lines.append(f"{indent}Skipped invalid: {' '.join(a['errors'])}")
        return lines

    if "sections" in result:
        out: list[str] = []
        for name, a in result["sections"].items():
            out += [f"[{name}]"] + block(a, "  ")
        out += [f"Modulation: {m}" for m in result["modulations"]]
        out += [f"Skipped (no chords): {', '.join(result['skipped'])}"] if result["skipped"] else []
        return "\n".join(out)
    return "\n".join(block(result))


def _handler(args: argparse.Namespace):
    if bool(args.chords) == bool(args.music):
        raise SongtoolsError(None, None, "give either CHORD... or --music FILE")
    if args.music:
        if args.key:
            raise SongtoolsError(None, None, "--key applies to CHORD... only; --music detects each section's key")
        from songtools.songfile import parse_music_md
        path = Path(args.music)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as e:
            raise SongtoolsError(str(path), None, f"cannot read file: {e.strerror or e}") from None
        return analyze_song(parse_music_md(text, str(path))), to_text
    result = asdict(analyze(args.chords, args.key))
    result["corpus"], result["basis"] = CORPUS, BASIS
    return result, to_text


def register(subparsers) -> None:
    p = subparsers.add_parser("harmony", help="key, Everett system, Roman and Nashville numerals")
    p.add_argument("chords", nargs="*", metavar="CHORD")
    p.add_argument("--key", default=None, help="fix the key, e.g. G, Am, 'A dorian'")
    p.add_argument("--music", default=None, metavar="FILE", help="analyse every section of a music.md")
    p.set_defaults(handler=_handler)
