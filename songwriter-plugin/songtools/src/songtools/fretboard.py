"""Guitar fretboard: tunings, capo, fingering verification, V-System, capo search, voicings.

Reads and verifies what the guitarist plays; it never writes parts.

chords-db suffix -> songtools quality (see `_db_symbol`): "major" -> "", "minor" -> "m", "sus" -> "sus4";
every other suffix (7, maj7, m7, sus2, add9, dim, aug, 6, m6, 9, 69 ...) is used as written, slash
suffixes ("/E", "m/B") become slash chords, and any suffix `parse_chord` cannot read is skipped.
Shapes are matched to chord names by pitch-class set (plus bass), never by name string.

JSON shapes (CLI, default output):
  identify: {shape, tuning, capo, partial_capo, sounding: [midi|null x6], notes: [name|null x6], names: [..]}
  verify:   {shape, name, tuning, capo, ok, missing: [..], extra: [..], alternatives: [..], note}
  vsystem:  {midi: [..], group: "V-n" | null}
  joni:     {tuning, strings: [midi..], code}
  capo:     {chords: [..], tuning, options: [{fret, shapes: [..], open_shapes, note}]}
  voicings: {name, tuning, voicings: [shape strings, frets absolute from the nut]}
"""

import argparse
import itertools
import json
import re
from dataclasses import asdict, dataclass
from functools import lru_cache

from songtools.chords import (FLAT_KEYS, NOTE_PC, SHARPS, is_no_chord, names_for, parse_chord, spell,
                              transpose)
from songtools.cli import SongtoolsError
from songtools.paths import data_dir

BASIS = "Ted Greene V-System Method 1 via Hober (verified); tunings per Wikipedia (verified); chords-db (MIT)"

_SOFT_NOTE = "soft heuristic: tone thins high on the neck (no source)"


# --- tunings and capo -------------------------------------------------------------------------------

@dataclass
class Tuning:
    name: str
    strings: list[int]  # MIDI numbers, low to high


@dataclass
class Capo:
    fret: int
    strings: tuple[bool, ...] | None = None  # None: clamps every string; else True = clamped


_NOTE_OCT = re.compile(r"^([A-Ga-g][#b]?)(-?\d)$")


def _note_midi(text: str) -> int:
    m = _NOTE_OCT.match(text)
    if not m:
        raise SongtoolsError(None, None, f"not a note with octave (like E2 or F#3): {text!r}")
    name = m.group(1)[0].upper() + m.group(1)[1:]
    return 12 * (int(m.group(2)) + 1) + NOTE_PC[name]


@lru_cache(maxsize=1)
def _tunings() -> dict[str, str]:
    return json.loads((data_dir() / "tunings.json").read_text(encoding="utf-8"))["tunings"]


def load_tuning(name_or_notes: str) -> Tuning:
    """A name from tunings.json (case, spaces, hyphens ignored) or six notes like "D2 A2 D3 G3 A3 D4"."""
    key = re.sub(r"[\s-]+", "_", name_or_notes.strip().lower())
    table = _tunings()
    if key in table:
        notes = table[key]
        label = key
    else:
        notes = name_or_notes.replace(",", " ")
        label = " ".join(notes.split())
    parts = notes.split()
    if len(parts) != 6 or key == "":
        raise SongtoolsError(None, None, f"unknown tuning {name_or_notes!r}: use one of "
                             f"{', '.join(sorted(table))} or six notes such as 'D2 A2 D3 G3 A3 D4'")
    return Tuning(label, [_note_midi(p) for p in parts])


def parse_shape(s: str) -> list[int | None]:
    """"x32010" (single digits) or "x 10 12 12 12 10" (spaces or commas); x/X is muted. Frets are
    relative to the capo, 0 is open (or the capo'd string)."""
    text = s.strip()
    if not text:
        raise SongtoolsError(None, None, "empty fingering")
    if re.search(r"[\s,]", text):
        tokens = [t for t in re.split(r"[\s,]+", text) if t]
    else:
        tokens = list(text)
    out: list[int | None] = []
    for t in tokens:
        if t in ("x", "X"):
            out.append(None)
        elif t.isdigit():
            out.append(int(t))
        else:
            raise SongtoolsError(None, None, f"bad fret {t!r} in fingering {s!r}")
    if len(out) != 6:
        raise SongtoolsError(None, None, f"fingering {s!r} has {len(out)} strings, expected 6")
    return out


def sounding(shape: list[int | None], tuning: Tuning, capo: Capo = Capo(0)) -> list[int | None]:
    """MIDI note per string (None = muted). On a clamped string frets are relative to the capo (0 = the
    capo fret): tuning + capo + fret. On an unclamped string (partial capo) frets are physical: tuning + fret,
    0 = open. A full capo (strings=None) clamps every string."""
    n = len(tuning.strings)
    if len(shape) != n:
        raise SongtoolsError(None, None, f"fingering has {len(shape)} strings, tuning has {n}")
    if capo.strings is not None and len(capo.strings) != n:
        raise ValueError(f"partial capo needs {n} entries, got {len(capo.strings)}")
    out: list[int | None] = []
    for i, (f, open_midi) in enumerate(zip(shape, tuning.strings)):
        if f is None:
            out.append(None)
        elif capo.strings is None or capo.strings[i]:
            out.append(open_midi + capo.fret + f)
        else:
            out.append(open_midi + f)
    return out


# --- identify / verify ------------------------------------------------------------------------------

def _notes(shape, tuning, capo) -> list[int]:
    return [m for m in sounding(shape, tuning, capo) if m is not None]


def identify(shape: list[int | None], tuning: Tuning, capo: Capo = Capo(0), key: str | None = None) -> list[str]:
    notes = _notes(shape, tuning, capo)
    if not notes:
        return []
    return names_for({m % 12 for m in notes}, min(notes) % 12, key)


@dataclass
class Verify:
    ok: bool
    missing: list[str]
    extra: list[str]
    alternatives: list[str]
    note: str


def verify(shape: list[int | None], name: str, tuning: Tuning, capo: Capo = Capo(0),
           band_bass: bool = False, key: str | None = None) -> Verify:
    """Does the fingering sound the named chord? Compared by pitch class. A missing fifth is fine; a
    missing root is fine with `band_bass`; a slash chord needs its bass lowest unless `band_bass`."""
    try:
        chord = parse_chord(name)
    except ValueError as e:
        raise SongtoolsError(None, None, str(e)) from None
    notes = _notes(shape, tuning, capo)
    if not notes:
        return Verify(False, [], [], [], "no sounding strings")
    spell_key = key if key is not None else chord.root
    alternatives = names_for({m % 12 for m in notes}, min(notes) % 12, spell_key)
    have = {m % 12 for m in notes}
    root = NOTE_PC[chord.root]
    want = set(chord.pcs)
    tone_name = {NOTE_PC[t]: t for t in chord.tones}
    if chord.bass:
        tone_name.setdefault(NOTE_PC[chord.bass], chord.bass)
    absent = want - have
    missing = [tone_name.get(pc) or spell(pc, spell_key) for pc in sorted(absent, key=lambda p: (p - root) % 12)]
    extra = [spell(pc, spell_key) for pc in sorted(have - want, key=lambda p: (p - root) % 12)]
    notes_out = []
    blocking = set()
    for pc in absent:
        if pc == (root + 7) % 12 and len(want) > 2:
            notes_out.append(f"{tone_name[pc]} (fifth) omitted: allowed")
        elif pc == root and band_bass:
            notes_out.append(f"root {tone_name[pc]} left to the band bass")
        else:
            blocking.add(pc)
    if chord.bass and NOTE_PC[chord.bass] in have and not band_bass \
            and min(notes) % 12 != NOTE_PC[chord.bass]:
        blocking.add(NOTE_PC[chord.bass])
        notes_out.append(f"bass {chord.bass} is not the lowest note")
    ok = not extra and not blocking
    if extra:
        notes_out.append(f"extra tone(s) {', '.join(extra)} are not in {chord.symbol}")
    if blocking and not any("bass" in n for n in notes_out):
        notes_out.append(f"missing {', '.join(missing)}")
    return Verify(ok, missing, extra, alternatives, "; ".join(notes_out))


# --- Ted Greene V-System ---------------------------------------------------------------------------

_GROUPS = {
    "V-1": "BTAS SBTA ASBT TASB", "V-2": "TABS STAB BSTA ABST", "V-3": "ABTS SABT TSAB BTSA",
    "V-4": "STBA ASTB BAST TBAS", "V-5": "BATS SBAT TSBA ATSB", "V-8": "TBSA ATBS SATB BSAT",
}
_FORMULA = {f: g for g, fs in _GROUPS.items() for f in fs.split()}
# Adjacent gap of 12+ semitones: (pair index, group) -> group. Pairs: 0 = B-T, 1 = T-A, 2 = A-S.
_WIDE = {(0, "V-1"): "V-6", (0, "V-2"): "V-7", (0, "V-3"): "V-12",
         (1, "V-1"): "V-13", (1, "V-2"): "V-10",
         (2, "V-1"): "V-14", (2, "V-2"): "V-9", (2, "V-4"): "V-11"}


def vsystem(midi: list[int]) -> str | None:
    """V-System group (Greene Method 1, per Hober) of a four-voice voicing, or None unless it has
    exactly four notes on four distinct pitch classes. Wide-gap rules are applied B-T, then T-A, then A-S
    to the group as updated so far."""
    notes = sorted(midi)
    if len(notes) != 4 or len({n % 12 for n in notes}) != 4:
        return None
    voices = list(zip("BTAS", notes))
    bass_pc = notes[0] % 12
    formula = "".join(v for v, n in sorted(voices, key=lambda vn: (vn[1] - bass_pc) % 12))
    group = _FORMULA[formula]
    for i in range(3):
        if notes[i + 1] - notes[i] >= 12:
            group = _WIDE.get((i, group), group)
    return group


def joni_code(tuning: Tuning) -> str:
    """Lowest string's note name, then the semitone gap between each adjacent pair of strings."""
    s = tuning.strings
    return SHARPS[s[0] % 12] + "".join(str(b - a) for a, b in zip(s, s[1:]))


# --- chords-db -------------------------------------------------------------------------------------

_STANDARD = [40, 45, 50, 55, 59, 64]
_DB_ROOT = {"Csharp": "C#", "Fsharp": "F#"}
_DB_QUALITY = {"major": "", "minor": "m", "sus": "sus4"}


def _db_symbol(key: str, suffix: str) -> str:
    return _DB_ROOT.get(key, key) + _DB_QUALITY.get(suffix, suffix)


def _chord_key(c) -> tuple[int, frozenset[int], int]:
    root = NOTE_PC[c.root]
    return root, c.pcs, NOTE_PC[c.bass] if c.bass else root


@lru_cache(maxsize=1)
def _db_index() -> dict[tuple[int, frozenset[int], int], list[dict]]:
    raw = json.loads((data_dir() / "chords-db" / "guitar.json").read_text(encoding="utf-8"))["chords"]
    index: dict[tuple[int, frozenset[int], int], list[dict]] = {}
    for key, entries in raw.items():
        for entry in entries:
            try:
                c = parse_chord(_db_symbol(key, entry["suffix"]))
            except ValueError:
                continue
            bucket = index.setdefault(_chord_key(c), [])
            for pos in entry["positions"]:
                frets = [None if f < 0 else (f if f == 0 else pos["baseFret"] + f - 1) for f in pos["frets"]]
                if not any(p["frets"] == frets for p in bucket):
                    bucket.append({"frets": frets, "open": pos["baseFret"] == 1 and 0 in frets})
    return index


def _db_positions(name: str) -> list[dict]:
    try:
        return _db_index().get(_chord_key(parse_chord(name)), [])
    except ValueError:
        return []


def _format_shape(frets: list[int | None]) -> str:
    cells = ["x" if f is None else str(f) for f in frets]
    return ",".join(cells) if any(f is not None and f >= 10 for f in frets) else "".join(cells)


# --- generated voicings (non-standard tunings) -------------------------------------------------------

def _generate(tuning: Tuning, name: str):
    """Yield fingerings (capo 0) in frets 0-5 within a 4-fret span whose pitch classes are the chord's
    (fifth optional for chords of 4+ tones) with the root (or slash bass) lowest."""
    c = parse_chord(name)
    root, want, bass = _chord_key(c)
    optional = [(root + 7) % 12] if len(want) > 3 and (root + 7) % 12 in want and bass != (root + 7) % 12 else []
    seen = set()
    for lo in (1, 2):
        options = []
        for open_midi in tuning.strings:
            opts = [None] + [f for f in [0, *range(lo, lo + 4)] if (open_midi + f) % 12 in want]
            options.append(opts)
        for combo in itertools.product(*options):
            if combo in seen:
                continue
            played = [(tuning.strings[i] + f, f) for i, f in enumerate(combo) if f is not None]
            if len(played) < 3 or min(m for m, _ in played) % 12 != bass:
                continue
            pcs = {m % 12 for m, _ in played}
            if pcs != want and pcs != want - set(optional):
                continue
            seen.add(combo)
            yield list(combo)


@lru_cache(maxsize=256)
def _generated(strings: tuple[int, ...], name: str) -> tuple[tuple[int | None, ...], ...]:
    t = Tuning("", list(strings))
    shapes = [tuple(s) for s in _generate(t, name)]
    shapes.sort(key=lambda s: (-sum(f is not None for f in s), max(f or 0 for f in s), tuple(f if f is not None else -1 for f in s)))
    return tuple(shapes)


def voicings(name: str, tuning: Tuning, limit: int = 8) -> list[str]:
    """Shape strings (absolute frets from the nut, capo 0). Standard tuning: from chords-db, in its
    order. Other tunings: generated (frets 0-5, 4-fret span), fuller and lower shapes first."""
    try:
        parse_chord(name)
    except ValueError as e:
        raise SongtoolsError(None, None, str(e)) from None
    if tuning.strings == _STANDARD:
        shapes = [p["frets"] for p in _db_positions(name)]
    else:
        shapes = [list(s) for s in _generated(tuple(tuning.strings), name)]
    return [_format_shape(s) for s in shapes[:limit]]


# --- capo search -------------------------------------------------------------------------------------

@dataclass
class CapoOption:
    fret: int
    shapes: list[str]
    open_shapes: int
    note: str


def _is_open(name: str, tuning: Tuning) -> bool:
    """Open shape: chords-db first-position shape (baseFret 1) with an open string; other tunings: any
    generated voicing with an open string. A name chords-db does not know is not open."""
    if is_no_chord(name):
        return False
    if tuning.strings == _STANDARD:
        return any(p["open"] for p in _db_positions(name))
    return any(0 in s for s in _generated(tuple(tuning.strings), name))


def capo_options(chords: list[str], tuning: Tuning, max_fret: int = 7) -> list[CapoOption]:
    for ch in chords:
        if not is_no_chord(ch):
            try:
                parse_chord(ch)
            except ValueError as e:
                raise SongtoolsError(None, None, str(e)) from None
    out = []
    for fret in range(max_fret + 1):
        shapes = [transpose(ch, -fret) for ch in chords]
        out.append(CapoOption(fret, shapes, sum(_is_open(s, tuning) for s in shapes),
                              _SOFT_NOTE if fret >= 7 else ""))
    out.sort(key=lambda o: (-o.open_shapes, o.fret))
    return out


# --- CLI ---------------------------------------------------------------------------------------------

def _capo(args, tuning: Tuning) -> Capo:
    if not 0 <= args.capo <= 12:
        raise SongtoolsError(None, None, f"--capo must be 0-12, got {args.capo}")
    mask = getattr(args, "partial_capo", None)
    if mask is None:
        return Capo(args.capo)
    n = len(tuning.strings)
    if not re.fullmatch(rf"[01]{{{n}}}", mask):
        raise SongtoolsError(None, None, f"--partial-capo needs {n} characters of 0/1 (low to high), got {mask!r}")
    if args.capo < 1:
        raise SongtoolsError(None, None, "--partial-capo needs --capo N (the fret, 1 or higher)")
    return Capo(args.capo, tuple(c == "1" for c in mask))


def _shape_arg(args) -> list[int | None]:
    return parse_shape(args.shape)


def _midi_arg(text: str) -> int:
    try:
        return int(text)
    except ValueError:
        return _note_midi(text)


def _common(p: argparse.ArgumentParser, capo: bool = True) -> None:
    p.add_argument("--tuning", default="standard", metavar="NAME_OR_NOTES")
    if capo:
        p.add_argument("--capo", type=int, default=0, metavar="N")
        p.add_argument("--partial-capo", default=None, metavar="MASK",
                       help="6 chars of 0/1, low to high; 1 = string clamped (needs --capo N)")


def _meta(args, tuning: Tuning, capo: Capo) -> dict:
    return {"tuning": tuning.name, "capo": capo.fret,
            "partial_capo": None if capo.strings is None else "".join("1" if c else "0" for c in capo.strings)}


def _h_identify(args):
    tuning = load_tuning(args.tuning)
    capo = _capo(args, tuning)
    shape = _shape_arg(args)
    snd = sounding(shape, tuning, capo)
    return {"shape": args.shape, **_meta(args, tuning, capo), "sounding": snd,
            "notes": [None if m is None else SHARPS[m % 12] for m in snd],
            "names": identify(shape, tuning, capo, args.key)}, to_text


def _h_verify(args):
    tuning = load_tuning(args.tuning)
    capo = _capo(args, tuning)
    v = verify(_shape_arg(args), args.name, tuning, capo, args.band_bass, args.key)
    return {"shape": args.shape, "name": args.name, **_meta(args, tuning, capo), **asdict(v)}, to_text


def _h_vsystem(args):
    midi = [_midi_arg(n) for n in args.notes]
    return {"midi": midi, "group": vsystem(midi)}, to_text


def _h_joni(args):
    t = load_tuning(args.tuning)
    return {"tuning": t.name, "strings": t.strings, "code": joni_code(t)}, to_text


def _h_capo(args):
    t = load_tuning(args.tuning)
    return {"chords": args.chords, "tuning": t.name,
            "options": [asdict(o) for o in capo_options(args.chords, t, args.max_fret)]}, to_text


def _h_voicings(args):
    t = load_tuning(args.tuning)
    return {"name": args.name, "tuning": t.name, "voicings": voicings(args.name, t, args.limit)}, to_text


def to_text(result: dict) -> str:
    if "options" in result:
        lines = []
        for o in result["options"]:
            lines.append(f"capo {o['fret']}: {' '.join(o['shapes'])} ({o['open_shapes']} open)"
                         + (f" - {o['note']}" if o["note"] else ""))
        return "\n".join(lines)
    if "voicings" in result:
        return "\n".join(result["voicings"]) or "(no voicings found)"
    if "code" in result:
        return f"{result['tuning']}: {result['code']}"
    if "group" in result:
        return result["group"] or "(needs four notes on four distinct pitch classes)"
    if "ok" in result:
        head = "OK" if result["ok"] else "NOT OK"
        lines = [f"{head}: {result['shape']} as {result['name']}"]
        if result["missing"]:
            lines.append("missing: " + " ".join(result["missing"]))
        if result["extra"]:
            lines.append("extra: " + " ".join(result["extra"]))
        if result["note"]:
            lines.append(result["note"])
        if result["alternatives"]:
            lines.append("sounds like: " + ", ".join(result["alternatives"]))
        return "\n".join(lines)
    return ", ".join(result["names"]) or "(no matching chord name)"


def _with_basis(handler):
    def run(args):
        result, text = handler(args)
        return {**result, "basis": BASIS}, text
    return run


def register(subparsers) -> None:
    g = subparsers.add_parser("guitar", help="fretboard: identify, verify, V-System, capo, voicings")
    sub = g.add_subparsers(dest="guitar_command", required=True)

    p = sub.add_parser("identify", help="chord names for a fingering (frets relative to the capo)")
    p.add_argument("shape", help="e.g. x32010, or quoted 'x 10 12 12 12 10'")
    p.add_argument("--key", default=None, help="song key, for flat spelling")
    _common(p)
    p.set_defaults(handler=_with_basis(_h_identify))

    p = sub.add_parser("verify", help="does this fingering sound this chord?")
    p.add_argument("shape")
    p.add_argument("name", help="chord symbol, e.g. C or Am7")
    p.add_argument("--band-bass", action="store_true", help="a bass player covers the root")
    p.add_argument("--key", default=None)
    _common(p)
    p.set_defaults(handler=_with_basis(_h_verify))

    p = sub.add_parser("vsystem", help="Ted Greene V-System group of a four-note voicing")
    p.add_argument("notes", nargs="+", metavar="NOTE", help="MIDI numbers or notes like C4")
    p.set_defaults(handler=_with_basis(_h_vsystem))

    p = sub.add_parser("joni", help="Joni Mitchell-style tuning code")
    _common(p, capo=False)
    p.set_defaults(handler=_with_basis(_h_joni))

    p = sub.add_parser("capo", help="capo positions ranked by open shapes")
    p.add_argument("chords", nargs="+", metavar="CHORD")
    p.add_argument("--max-fret", type=int, default=7)
    _common(p, capo=False)
    p.set_defaults(handler=_with_basis(_h_capo))

    p = sub.add_parser("voicings", help="fingerings for a chord")
    p.add_argument("name")
    p.add_argument("--limit", type=int, default=8)
    _common(p, capo=False)
    p.set_defaults(handler=_with_basis(_h_voicings))
