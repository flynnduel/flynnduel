"""Tessitura-based key fitting with capo pairing.

Spelling rule for result keys: the target pitch class is named with a flat root when that
flat key is a flat key in `songtools.chords.FLAT_KEYS` (F, Bb, Eb, Ab, Db, Gb; Dm, Gm, Cm, Fm,
Bbm, Ebm), otherwise with a sharp root (so minor C#m, F#m, G#m, D#m, A#m). The minor suffix "m"
is kept when current_key is minor. Note names inside a key (low/high) are spelled for that key.
"""

import argparse
import re
from dataclasses import asdict, dataclass

from songtools.chords import FLATS, NOTE_PC, spell
from songtools.cli import SongtoolsError

BASIS = "tessitura-based key choice (vocal pedagogy, Wikipedia: verified)"

SHAPES = ("C", "G", "D", "A", "E", "Am", "Em", "Dm")
_NOTE_RE = re.compile(r"^([A-Ga-g][#b♯♭]?)(-?\d+)$")


def note_to_midi(n: str) -> int:
    m = _NOTE_RE.match(n.strip())
    if not m or m.group(1)[0].upper() + m.group(1)[1:] not in NOTE_PC:
        raise ValueError(f"not a note with octave (e.g. A2): {n!r}")
    name = m.group(1)[0].upper() + m.group(1)[1:]
    return 12 * (int(m.group(2)) + 1) + NOTE_PC[name]


def midi_to_note(m: int, key: str | None = None) -> str:
    return f"{spell(m % 12, key)}{m // 12 - 1}"


@dataclass
class KeyFit:
    key: str
    shift: int
    fits: bool
    low: str
    high: str
    margin_low: int
    margin_high: int
    tessitura_offset: float


def _split_key(key: str) -> tuple[int, bool]:
    k = key.strip().replace("♯", "#").replace("♭", "b")
    minor = k.endswith("m") and len(k) > 1
    root = k[:-1] if minor else k
    if root not in NOTE_PC:
        raise ValueError(f"not a key name: {key!r}")
    return NOTE_PC[root], minor


def _key_name(pc: int, minor: bool) -> str:
    suffix = "m" if minor else ""
    return spell(pc, FLATS[pc % 12] + suffix) + suffix


def fit_keys(melody_low: str, melody_high: str, voice_low: str, voice_high: str, current_key: str,
             tessitura: tuple[str, str] | None = None) -> list[KeyFit]:
    """Try shifts -6..+6. Sorted: fits first, then |tessitura (or melody) midpoint - voice
    midpoint|, then |shift|. tessitura is given in the melody's current key."""
    ml, mh = note_to_midi(melody_low), note_to_midi(melody_high)
    vl, vh = note_to_midi(voice_low), note_to_midi(voice_high)
    pc, minor = _split_key(current_key)
    ref = (note_to_midi(tessitura[0]) + note_to_midi(tessitura[1])) / 2 if tessitura else (ml + mh) / 2
    voice_mid = (vl + vh) / 2
    fits = []
    for s in range(-6, 7):
        key = _key_name((pc + s) % 12, minor)
        mlow, mhigh = ml + s, mh + s
        ml_margin, mh_margin = mlow - vl, vh - mhigh
        fits.append(KeyFit(key, s, ml_margin >= 0 and mh_margin >= 0, midi_to_note(mlow, key),
                           midi_to_note(mhigh, key), ml_margin, mh_margin, ref + s - voice_mid))
    fits.sort(key=lambda f: (not f.fits, abs(f.tessitura_offset), abs(f.shift)))
    return fits


def capo_for(key: str) -> list[tuple[int, str]]:
    """(fret, shape) with shape + capo = key, frets 0-7; (0, key) when key is itself a shape."""
    pc, minor = _split_key(key)
    out = []
    for fret in range(8):
        for shape in SHAPES:
            spc, smin = _split_key(shape)
            if smin == minor and (spc + fret) % 12 == pc:
                out.append((fret, shape))
    return out


def to_text(result: dict) -> str:
    lines = [f"{'key':<5} {'shift':>5}  fits  {'range':<9} margins(lo/hi)  capo"]
    for f in result["fits"]:
        capo = ", ".join(f"{fr}:{sh}" for fr, sh in f["capo"]) or "-"
        lines.append(f"{f['key']:<5} {f['shift']:>+5}  {'yes' if f['fits'] else 'no ':<4}  "
                     f"{f['low'] + '-' + f['high']:<9} {f['margin_low']:>+4}/{f['margin_high']:<+4}      {capo}")
    if not any(f["fits"] for f in result["fits"]):
        lines.append("No key fits the whole melody in this voice range.")
    lines.append(f"basis: {result['basis']}")
    return "\n".join(lines)


def _handler(args: argparse.Namespace):
    tess = tuple(args.tessitura) if args.tessitura else None
    try:
        fits = fit_keys(args.melody_low, args.melody_high, args.voice_low, args.voice_high, args.key, tess)
        rows = [{**asdict(f), "capo": [list(c) for c in capo_for(f.key)]} for f in fits]
    except ValueError as e:
        raise SongtoolsError(None, None, str(e)) from None
    return {"current_key": args.key, "melody": [args.melody_low, args.melody_high],
            "voice": [args.voice_low, args.voice_high], "tessitura": list(tess) if tess else None,
            "fits": rows, "basis": BASIS}, to_text


def register(subparsers) -> None:
    p = subparsers.add_parser("key", help="fit a melody to a voice range; capo pairings")
    p.add_argument("--melody-low", required=True, metavar="NOTE")
    p.add_argument("--melody-high", required=True, metavar="NOTE")
    p.add_argument("--voice-low", required=True, metavar="NOTE")
    p.add_argument("--voice-high", required=True, metavar="NOTE")
    p.add_argument("--key", required=True, help="current key, e.g. G or Em")
    p.add_argument("--tessitura", nargs=2, metavar=("LOW", "HIGH"), default=None)
    p.set_defaults(handler=_handler)
