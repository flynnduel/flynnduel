"""MIDI reference track: plays only the writer's own chords at their tempo, nothing added.

Each chord sounds its bass (36 + root pitch class, or the slash bass) with its chord tones
stacked from 60 + pc (anything above 71 drops an octave), velocity 80, for its beat count.
N.C. is a rest. 480 ticks per beat.

CLI: songtools midi SONG_DIR [--tempo N] [--concert] -> {"path", "tempo", "chords", "beats", "key",
"capo_applied", "basis"}. --concert writes out/guide-concert.mid instead, every chord moved up by
song.md's capo (the sounding pitch the band hears), with the sounding key.
"""

import argparse
from pathlib import Path

import mido

from songtools.chords import NOTE_PC, ascii_accidentals, is_no_chord, parse_chord, transpose
from songtools.cli import SongtoolsError
from songtools.songfile import file_error, parse_music_md, parse_song_md, read_text

BASIS = "reference track of the writer's own chords (mido)"
TICKS = 480
VELOCITY = 80


def _voicing(symbol: str) -> list[int]:
    chord = parse_chord(symbol)
    bass = NOTE_PC[chord.bass or chord.root]
    notes = [36 + bass]
    for tone in chord.tones:
        n = 60 + NOTE_PC[tone]
        notes.append(n - 12 if n > 71 else n)
    return notes


def write_midi(progression: list[tuple[str, float]], tempo_bpm: int, out: Path,
               key: str | None = None, time: str = "4/4") -> Path:
    voicings = [None if is_no_chord(s) else _voicing(s) for s, _ in progression]  # validate first
    num, _, den = time.partition("/")
    mf = mido.MidiFile(ticks_per_beat=TICKS)
    track = mido.MidiTrack()
    mf.tracks.append(track)
    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(tempo_bpm)))
    track.append(mido.MetaMessage("time_signature", numerator=int(num), denominator=int(den)))
    if key:
        try:
            track.append(mido.MetaMessage("key_signature", key=key))
        except ValueError:
            pass  # not a key mido can notate; the track still plays
    rest = 0
    for (_, beats), notes in zip(progression, voicings):
        ticks = round(beats * TICKS)
        if notes is None:
            rest += ticks
            continue
        for i, n in enumerate(notes):
            track.append(mido.Message("note_on", note=n, velocity=VELOCITY, time=rest if i == 0 else 0))
        for i, n in enumerate(notes):
            track.append(mido.Message("note_off", note=n, velocity=0, time=ticks if i == 0 else 0))
        rest = 0
    track.append(mido.MetaMessage("end_of_track", time=rest))
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    mf.save(out)
    return out


def to_text(result: dict) -> str:
    return f"{result['path']} ({result['tempo']} bpm, {result['chords']} chords, {result['beats']} beats)"


def _read(path: Path) -> str:
    return read_text(path, path.name)


def _h_midi(args: argparse.Namespace):
    d = Path(args.song_dir)
    song_path, music_path = d / "song.md", d / "music.md"
    record = parse_song_md(_read(song_path), file=str(song_path))
    sections = parse_music_md(_read(music_path), file=str(music_path))
    tempo = args.tempo
    if tempo is None:
        raw = record.core.get("tempo", "")
        try:
            tempo = int(float(raw))
        except ValueError:
            raise SongtoolsError(str(song_path), None,
                                 "no tempo: pass --tempo or set tempo in song.md core") from None
    if tempo <= 0:
        raise SongtoolsError(None, None, f"tempo must be positive, got {tempo}")
    key = ascii_accidentals(record.core.get("key", "")) or None  # reported and notated with # and b
    capo = 0
    if args.concert:
        from songtools.chordpro import _sounding_key
        capo_text = record.core.get("capo", "")
        try:
            capo = int(capo_text) if capo_text else 0
        except ValueError:
            raise SongtoolsError(str(song_path), None, f"bad capo value {capo_text!r}") from None
        if key and capo:
            key = _sounding_key(key, capo)
    progression = []
    for name, chords in sections.items():
        for symbol, beats in chords:
            if not is_no_chord(symbol):
                try:
                    parse_chord(symbol)
                except ValueError:
                    raise SongtoolsError(str(music_path), None,
                                         f"cannot parse chord {symbol!r} in section {name!r}") from None
            if capo and not is_no_chord(symbol):
                symbol = transpose(symbol, capo, key)
            progression.append((symbol, beats))
    out = d / "out" / ("guide-concert.mid" if args.concert else "guide.mid")
    try:
        path = write_midi(progression, tempo, out, key=key, time=record.core.get("time") or "4/4")
    except ValueError as e:
        raise SongtoolsError(str(song_path), None, f"cannot build MIDI: {e}") from None
    except OSError as e:
        raise file_error(out, "cannot write MIDI", e) from None
    return {"path": str(path), "tempo": tempo, "chords": len(progression),
            "beats": sum(b for _, b in progression), "key": key, "capo_applied": capo,
            "basis": BASIS}, to_text


def register(subparsers) -> None:
    p = subparsers.add_parser("midi", help="write out/guide.mid from music.md (your chords only)")
    p.add_argument("song_dir", type=Path, metavar="SONG_DIR")
    p.add_argument("--tempo", type=int, default=None, help="beats per minute (default: song.md tempo)")
    p.add_argument("--concert", action="store_true",
                   help="write out/guide-concert.mid with the capo applied (sounding pitch)")
    p.set_defaults(handler=_h_midi)
