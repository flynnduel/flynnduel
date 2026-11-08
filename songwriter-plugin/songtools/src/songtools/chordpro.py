"""ChordPro 6 directive subset: reader, canonical writer, song.md/lyrics.md import, concert pitch.

Supported directives: title|t, artist, key, capo, tempo, time, comment|c, define,
start_of_{verse,chorus,bridge} / end_of_... (short forms sov/eov, soc/eoc, sob/eob) with an
optional label. Unknown directives are kept as raw strings (e.g. "{foo: bar}") in
meta["_unknown"] and written back after the known meta. Comments outside a block open an
"other" section (label = comment text) holding the plain lines that follow, up to a blank line
or the next directive. Blank lines inside blocks are dropped; non-end directives inside a block
stay verbatim in its lines. Other start_of_X blocks (tab, grid) are not understood: their
directives are kept as unknown and their body as plain lines.

Capo: {key} stays the shape key; the band hears it `capo` semitones higher. concert_pitch
transposes every chord up by capo, drops {capo} and sets {key} to the sounding key.

CLI: songtools chart SONG_DIR [--concert] [--pdf] -> {"written": [paths], "basis": str}.
--pdf also renders out/chart.pdf (and out/chart-concert.pdf with --concert) via songtools.pdf.
Every output is built in memory first; nothing is written if any build fails.
"""

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path

from songtools.chords import FLAT_KEYS, is_no_chord, transpose
from songtools.cli import SongtoolsError
from songtools.songfile import Section, SongRecord, parse_lyrics, parse_song_md

BASIS = "ChordPro 6 directive subset (chordpro.org, verified)"

_META_ORDER = ("title", "artist", "key", "capo", "tempo", "time")
_META_ALIASES = {"t": "title", "title": "title", "artist": "artist", "key": "key",
                 "capo": "capo", "tempo": "tempo", "time": "time"}
_BLOCK_SHORT = {"v": "verse", "c": "chorus", "b": "bridge"}
_BLOCKS = ("verse", "chorus", "bridge")
_DIRECTIVE = re.compile(r"^\{\s*([A-Za-z_]+)\s*(?::\s*(.*?))?\s*\}$")


@dataclass
class CPSection:
    kind: str  # verse | chorus | bridge | other
    label: str
    lines: list[str] = field(default_factory=list)


@dataclass
class ChordProSong:
    meta: dict = field(default_factory=dict)
    sections: list[CPSection] = field(default_factory=list)
    defines: list[str] = field(default_factory=list)


def _block(name: str) -> tuple[str, str] | None:
    """('start'|'end', kind) for a block directive name, else None."""
    m = re.fullmatch(r"(start|end)_of_(\w+)", name)
    if m and m.group(2) in _BLOCKS:
        return m.group(1), m.group(2)
    m = re.fullmatch(r"(so|eo)([vcb])", name)
    if m:
        return ("start" if m.group(1) == "so" else "end"), _BLOCK_SHORT[m.group(2)]
    return None


def parse(text: str, file: str = "chordpro") -> ChordProSong:
    song = ChordProSong()
    open_block: tuple[CPSection, int] | None = None
    loose: CPSection | None = None
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        m = _DIRECTIVE.match(line)
        name = m.group(1).lower() if m else None
        value = (m.group(2) or "") if m else ""
        blk = _block(name) if m else None
        if blk:
            loose = None
            action, kind = blk
            if action == "start":
                if open_block:
                    raise SongtoolsError(file, number, f"{{start_of_{kind}}} inside an open "
                                         f"{{start_of_{open_block[0].kind}}} (line {open_block[1]})")
                open_block = (CPSection(kind, value), number)
                song.sections.append(open_block[0])
            else:
                if not open_block or open_block[0].kind != kind:
                    raise SongtoolsError(file, number, f"{{end_of_{kind}}} without a matching start")
                open_block = None
            continue
        if open_block:
            if line:
                open_block[0].lines.append(line)
            continue
        if not line:
            loose = None
        elif not m:
            if loose is None:
                loose = CPSection("other", "")
                song.sections.append(loose)
            loose.lines.append(line)
        elif name in ("comment", "c"):
            loose = CPSection("other", value)
            song.sections.append(loose)
        else:
            loose = None
            if name == "define":
                song.defines.append(value)
            elif name in _META_ALIASES:
                song.meta[_META_ALIASES[name]] = value
            else:
                song.meta.setdefault("_unknown", []).append(line)
    if open_block:
        raise SongtoolsError(file, open_block[1], f"{{start_of_{open_block[0].kind}}} is never closed")
    return song


def _directive(name: str, value: str) -> str:
    return f"{{{name}: {value}}}" if value else f"{{{name}}}"


def write(song: ChordProSong) -> str:
    head = [_directive(k, str(song.meta[k])) for k in _META_ORDER if k in song.meta]
    head += list(song.meta.get("_unknown", []))
    head += [_directive("define", d) for d in song.defines]
    blocks = []
    for s in song.sections:
        if s.kind in _BLOCKS:
            body = [_directive(f"start_of_{s.kind}", s.label), *s.lines, f"{{end_of_{s.kind}}}"]
        else:
            body = ([_directive("comment", s.label)] if s.label else []) + list(s.lines)
        blocks.append("\n".join(body))
    parts = (["\n".join(head)] if head else []) + blocks
    return "\n\n".join(parts) + "\n" if parts else ""


def _inline(lyric: str, chords: list[tuple[int, str]]) -> str:
    out, pos = [], 0
    for offset, symbol in sorted(chords, key=lambda c: c[0]):
        out.append(lyric[pos:offset] + f"[{symbol}]")
        pos = offset
    out.append(lyric[pos:])
    return "".join(out)


def from_song(sections: list[Section], record: SongRecord) -> ChordProSong:
    meta: dict = {}
    if record.title:
        meta["title"] = record.title
    for k in ("artist", "key", "capo", "tempo", "time"):
        if record.core.get(k):
            meta[k] = record.core[k]
    out = []
    for s in sections:
        lines = [_inline(l.lyric, l.chords) for l in s.lines]
        out.append(CPSection(s.kind if s.kind in _BLOCKS else "other", s.name, lines))
    return ChordProSong(meta, out, [])


def _sounding_key(key: str, capo: int) -> str:
    try:
        sharp = transpose(key, capo, "C")
        flat = transpose(key, capo, "F")
    except ValueError:
        raise SongtoolsError(None, None, f"cannot transpose {{key: {key}}}: not a key like G or Em") from None
    return flat if flat in FLAT_KEYS else sharp


def _shift_line(line: str, capo: int, key: str | None) -> str:
    if line.startswith("{"):  # directive line: never transpose
        return line

    def sub(m: re.Match) -> str:
        sym = m.group(1).strip()
        if is_no_chord(sym) or sym.startswith("*"):  # N.C. and ChordPro annotations
            return m.group(0)
        try:
            return f"[{transpose(sym, capo, key)}]"
        except ValueError:
            raise SongtoolsError(None, None, f"cannot transpose chord [{sym}] in line: {line}") from None
    return re.sub(r"\[([^\]]*)\]", sub, line)


def concert_pitch(song: ChordProSong) -> ChordProSong:
    """Copy with every chord moved up by capo, {capo} removed and {key} set to the sounding key.

    [*Annotation] chords and directive lines pass through; other unparseable chords or keys raise.
    """
    capo_text = song.meta.get("capo", "")
    try:
        capo = int(capo_text) if capo_text else 0
    except ValueError:
        raise SongtoolsError(None, None, f"bad capo value {capo_text!r}") from None
    meta = {k: (list(v) if isinstance(v, list) else v) for k, v in song.meta.items() if k != "capo"}
    key = song.meta.get("key")
    sounding = _sounding_key(key, capo) if key and capo else key
    if key and capo:
        meta["key"] = sounding
    sections = [CPSection(s.kind, s.label, [_shift_line(l, capo, sounding) if capo else l for l in s.lines])
                for s in song.sections]
    return ChordProSong(meta, sections, list(song.defines))


def to_text(result: dict) -> str:
    return "\n".join(result["written"])


def _read(path: Path) -> str:
    if not path.is_file():
        raise SongtoolsError(str(path), None, f"{path.name} not found")
    return path.read_text(encoding="utf-8")


def _h_chart(args: argparse.Namespace):
    d = Path(args.song_dir)
    song_path, lyrics_path = d / "song.md", d / "lyrics.md"
    record = parse_song_md(_read(song_path), file=str(song_path))
    sections = parse_lyrics(_read(lyrics_path), file=str(lyrics_path))
    song = from_song(sections, record)
    out = d / "out"
    variants = [("chart", song)]
    if args.concert:
        variants.append(("chart-concert", concert_pitch(song)))
    outputs = [(out / f"{name}.cho", write(s)) for name, s in variants]
    if args.pdf:
        from songtools.pdf import render_pdf_bytes  # lazy: reportlab only when asked
        outputs += [(out / f"{name}.pdf", render_pdf_bytes(s)) for name, s in variants]
    out.mkdir(exist_ok=True)  # only after every output built: a failure writes nothing
    for path, body in outputs:
        if isinstance(body, bytes):
            path.write_bytes(body)
        else:
            path.write_text(body, encoding="utf-8")
    written = [p for p, _ in outputs]
    return {"written": [str(p) for p in written], "basis": BASIS}, to_text


def register(subparsers) -> None:
    p = subparsers.add_parser("chart", help="write a ChordPro chart from song.md and lyrics.md")
    p.add_argument("song_dir", type=Path, metavar="SONG_DIR")
    p.add_argument("--concert", action="store_true", help="also write out/chart-concert.cho (capo applied)")
    p.add_argument("--pdf", action="store_true", help="also render PDF lead sheets (out/chart.pdf)")
    p.set_defaults(handler=_h_chart)
