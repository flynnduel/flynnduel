"""Parsers for the song file formats (lyrics.md, song.md, music.md, melody.md)."""

import re
from dataclasses import dataclass
from pathlib import Path

from songtools.cli import SongtoolsError

KINDS = ("verse", "prechorus", "chorus", "postchorus", "bridge", "intro",
         "outro", "refrain", "hook", "tag")


@dataclass
class Line:
    number: int
    text: str
    lyric: str
    chords: list[tuple[int, str]]


@dataclass
class Section:
    name: str
    kind: str
    lines: list[Line]


@dataclass
class KeptLine:
    text: str
    flag: str
    reason: str
    date: str


@dataclass
class Split:
    name: str
    roles: list[str]
    percent: float


@dataclass
class SongRecord:
    title: str
    core: dict[str, str]
    sections: dict[str, str]
    kept: list[KeptLine]
    splits: list[Split]


def file_error(path: Path | str, action: str, e: Exception) -> SongtoolsError:
    """A user-facing error for a file that could not be read or written; action e.g. "cannot read lyrics file"."""
    if isinstance(e, UnicodeDecodeError):
        reason = f"not valid UTF-8 ({e.reason})"
    elif isinstance(e, FileNotFoundError):
        reason = "not found"
    elif isinstance(e, IsADirectoryError):
        reason = "is a directory"
    elif isinstance(e, NotADirectoryError):
        reason = "a parent is not a directory"
    elif isinstance(e, FileExistsError):
        reason = "exists and is not a directory"
    else:
        reason = getattr(e, "strerror", None) or type(e).__name__
    return SongtoolsError(str(path), None, f"{action}: {reason}")


def read_text(path: Path | str, what: str = "file") -> str:
    """Read a UTF-8 text file; any OS or decoding failure becomes a SongtoolsError naming the file."""
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise file_error(path, f"cannot read {what}", e) from None


def _numbered_lines(text: str):
    """Yield (1-based number, line) with HTML comments blanked (may span lines)."""
    in_comment = False
    for number, raw in enumerate(text.splitlines(), start=1):
        out = []
        rest = raw
        while rest:
            if in_comment:
                end = rest.find("-->")
                if end < 0:
                    rest = ""
                else:
                    in_comment = False
                    rest = rest[end + 3:]
            else:
                start = rest.find("<!--")
                if start < 0:
                    out.append(rest)
                    rest = ""
                else:
                    out.append(rest[:start])
                    in_comment = True
                    rest = rest[start + 4:]
        yield number, "".join(out).rstrip()


def _heading(line: str) -> str | None:
    m = re.match(r"^##\s+(.*?)\s*#*\s*$", line)
    return m.group(1) if m else None


def _section_kind(name: str) -> str:
    words = re.findall(r"[A-Za-z][A-Za-z-]*", name.lower())
    if not words:
        return "other"
    first = words[0].replace("-", "")
    if first in KINDS:
        return first
    if len(words) > 1 and first + words[1].replace("-", "") in KINDS:
        return first + words[1].replace("-", "")
    return "other"


def _split_chords(raw: str, file: str, number: int) -> tuple[str, list[tuple[int, str]]]:
    lyric: list[str] = []
    chords: list[tuple[int, str]] = []
    i = 0
    length = 0
    while i < len(raw):
        ch = raw[i]
        if ch == "[":
            end = raw.find("]", i + 1)
            if end < 0:
                raise SongtoolsError(file, number, "unclosed chord bracket '['")
            symbol = raw[i + 1:end].strip()
            if not symbol:
                raise SongtoolsError(file, number, "empty chord bracket '[]'")
            chords.append((length, symbol))
            i = end + 1
        else:
            lyric.append(ch)
            length += 1
            i += 1
    return "".join(lyric), chords


def parse_lyrics(text: str, file: str = "lyrics.md") -> list[Section]:
    sections: list[Section] = []
    for number, line in _numbered_lines(text):
        name = _heading(line)
        if name is not None:
            sections.append(Section(name, _section_kind(name), []))
            continue
        if not line.strip():
            continue
        if not sections:
            raise SongtoolsError(file, number, "lyric line before any '## Section' heading")
        lyric, chords = _split_chords(line.strip(), file, number)
        sections[-1].lines.append(Line(number, line.strip(), lyric, chords))
    return sections


def end_word(line: Line) -> str:
    for token in reversed(line.lyric.lower().replace("\u2019", "'").split()):
        for piece in reversed(re.split("[\u2014\u2013\\-\u2026]+", token)):
            word = re.sub(r"[^\w']", "", piece).lstrip("'").replace("_", "")
            if re.search(r"\w", word):
                return word
    return ""


def _sections_of(text: str):
    """Yield (heading or None, [(number, line)]) groups, comments removed."""
    current: tuple[str | None, list[tuple[int, str]]] = (None, [])
    for number, line in _numbered_lines(text):
        name = _heading(line)
        if name is not None:
            yield current
            current = (name, [])
        else:
            current[1].append((number, line))
    yield current


def parse_song_md(text: str, file: str = "song.md") -> SongRecord:
    rec = SongRecord("", {}, {}, [], [])
    for name, body in _sections_of(text):
        if name is None:
            for _, line in body:
                m = re.match(r"^#\s+(.*?)\s*$", line)
                if m and not rec.title:
                    rec.title = m.group(1)
            continue
        key = name.lower()
        if key == "core":
            seen: dict[str, int] = {}
            for number, line in body:
                if not line.strip():
                    continue
                k, sep, v = line.partition(":")
                if not sep or not k.strip():
                    raise SongtoolsError(file, number, "expected 'key: value'")
                k = k.strip().lower()
                if k in seen:
                    # a second line would silently replace the first; make the writer choose
                    raise SongtoolsError(file, number,
                                         f"duplicate ## Core key {k!r} (first on line {seen[k]})")
                seen[k] = number
                rec.core[k] = v.strip()
        elif key == "split sheet":
            for number, line in body:
                if line.lstrip().startswith("-"):
                    rec.splits.append(_parse_split(line, file, number))
        elif key == "kept lines":
            for number, line in body:
                if line.lstrip().startswith("-"):
                    rec.kept.append(_parse_kept(line, file, number))
        else:
            rec.sections[name] = "\n".join(l for _, l in body).strip("\n")
    return rec


def _parse_split(line: str, file: str, number: int) -> Split:
    parts = [p.strip() for p in line.lstrip()[1:].split("|")]
    if len(parts) != 3 or not parts[0]:
        raise SongtoolsError(file, number, "expected '- Name | roles | percent'")
    roles = [r.strip() for r in parts[1].split(",") if r.strip()]
    try:
        percent = float(parts[2].rstrip("%").strip())
    except ValueError:
        raise SongtoolsError(file, number, f"bad split percent {parts[2]!r}") from None
    return Split(parts[0], roles, percent)


def _parse_kept(line: str, file: str, number: int) -> KeptLine:
    m = re.match(r'^\s*-\s*["“](.*?)["”]\s*\|(.*)$', line)
    if not m:
        raise SongtoolsError(file, number, "expected '- \"line text\" | flag | reason | date'")
    rest = [p.strip() for p in m.group(2).split("|")]
    if len(rest) != 3:
        raise SongtoolsError(file, number, "expected '- \"line text\" | flag | reason | date'")
    return KeptLine(m.group(1), rest[0], rest[1], rest[2])


def parse_music_md(text: str, file: str = "music.md") -> dict[str, list[tuple[str, float]]]:
    result: dict[str, list[tuple[str, float]]] = {}
    section = None
    for number, line in _numbered_lines(text):
        name = _heading(line)
        if name is not None:
            section = name
            result.setdefault(section, [])
            continue
        m = re.match(r"^\s*progression\s*:(.*)$", line)
        if not m:
            continue
        if section is None:
            raise SongtoolsError(file, number, "progression before any '## Section' heading")
        for token in m.group(1).split():
            symbol, sep, beats = token.rpartition(":")
            try:
                value = float(beats)
            except ValueError:
                value = 0.0
            if not sep or not symbol or value <= 0:
                raise SongtoolsError(file, number, f"bad progression token {token!r} (expected chord:beats)")
            result[section].append((symbol, value))
    return result


def parse_melody_md(text: str, file: str = "melody.md") -> dict[tuple[str, int], list[tuple[str, int]]]:
    result: dict[tuple[str, int], list[tuple[str, int]]] = {}
    section = None
    for number, line in _numbered_lines(text):
        name = _heading(line)
        if name is not None:
            section = name
            continue
        if not line.strip():
            continue
        m = re.match(r"^\s*(\d+)\s*:(.*)$", line)
        if not m or int(m.group(1)) < 1:
            raise SongtoolsError(file, number, "expected '<line number>: syllable/slot ...'")
        if section is None:
            raise SongtoolsError(file, number, "melody line before any '## Section' heading")
        syllables = []
        for token in m.group(2).split():
            label, sep, slot = token.rpartition("/")
            try:
                value = int(slot)
            except ValueError:
                value = None
            if not sep or not label or value is None:
                raise SongtoolsError(file, number, f"bad syllable token {token!r} (expected syllable/slot)")
            syllables.append((label, value))
        result[(section, int(m.group(1)))] = syllables
    return result


def format_melody_entry(index: int, syllables: list[tuple[str, int]]) -> str:
    return f"{index}: " + " ".join(f"{label}/{slot}" for label, slot in syllables)


# `songtools song SONG_MD`: read song.md on its own and print what the parser sees.
def _song_handler(args):
    from dataclasses import asdict
    path = args.song_md
    rec = parse_song_md(read_text(path, "song file"), Path(path).name)
    return {"title": rec.title, "core": rec.core, "kept": [asdict(k) for k in rec.kept],
            "splits": [asdict(s) for s in rec.splits], "sections": list(rec.sections)}, _song_text


def _song_text(r: dict) -> str:
    lines = [f"# {r['title']}"] + [f"{k}: {v}" for k, v in r["core"].items()]
    lines.append(f"kept lines: {len(r['kept'])}; split sheet entries: {len(r['splits'])}")
    return "\n".join(lines)


def register(subparsers) -> None:
    p = subparsers.add_parser("song", help="parse song.md and print its core, kept lines and splits")
    p.add_argument("song_md", type=Path)
    p.set_defaults(handler=_song_handler)
