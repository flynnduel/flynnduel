"""Draft snapshots, the cut pool and a kept-line-aware diff.

JSON shapes (CLI):
  drafts snapshot -> {"path": str, "version": int, "basis": str}
  drafts cut      -> {"path": str, "date": str, "basis": str}
  drafts diff     -> {"changes": [{"section", "index", "old", "new", "kept_changed"}],
                      "kept_changed_count": int, "basis": str}
Sections are matched by name (repeated names by occurrence), lines by 1-based index within the
section; an added line has old = null, a removed line new = null. Lines compare by lyric text
(inline chords ignored). Kept-line matching ignores case and punctuation.
"""

import argparse
import re
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

from songtools.cli import SongtoolsError
from songtools.songfile import KeptLine, file_error, parse_lyrics, parse_song_md, read_text

BASIS = "draft history and cut pool (design rule)"
_VERSION_RE = re.compile(r"^lyrics-v(\d+)\.md$")


def snapshot(song_dir: Path) -> Path:
    song_dir = Path(song_dir)
    src = song_dir / "lyrics.md"
    try:
        data = src.read_bytes()  # read before creating anything: a bad source writes nothing
    except OSError as e:
        raise file_error(src, "cannot read lyrics.md", e) from None
    drafts = song_dir / "drafts"
    try:
        drafts.mkdir(exist_ok=True)
        versions = [int(m.group(1)) for p in drafts.iterdir() if (m := _VERSION_RE.match(p.name))]
    except OSError as e:
        raise file_error(drafts, "cannot use drafts directory", e) from None
    dest = drafts / f"lyrics-v{max(versions, default=0) + 1}.md"
    try:
        with open(dest, "xb") as f:  # exclusive create: never overwrite a version
            f.write(data)
    except OSError as e:
        raise SongtoolsError(str(dest), None, f"cannot write snapshot: {e.strerror}") from None
    return dest


def cut(song_dir: Path, text: str, reason: str, today: str) -> Path:
    path = Path(song_dir) / "cuts" / "cuts.md"
    try:
        path.parent.mkdir(exist_ok=True)
        entry = f"## {today} — {reason}\n{text}\n"
        if path.exists() and path.stat().st_size:
            with open(path, "rb") as f:  # last byte only: the pool need not be valid UTF-8
                f.seek(-1, 2)
                last = f.read(1)
            entry = ("\n" if last == b"\n" else "\n\n") + entry
        with open(path, "a", encoding="utf-8") as f:  # append only
            f.write(entry)
    except OSError as e:
        raise file_error(path, "cannot write cut", e) from None
    return path


@dataclass
class Change:
    section: str
    index: int
    old: str | None
    new: str | None
    kept_changed: bool


def _norm(s: str) -> str:
    return " ".join(re.sub(r"[^\w\s]", "", s.lower().replace("_", "")).split())


def _by_section(text: str) -> dict[tuple[str, int], list[str]]:
    out: dict[tuple[str, int], list[str]] = {}
    seen: dict[str, int] = {}
    for sec in parse_lyrics(text):
        n = seen[sec.name] = seen.get(sec.name, 0) + 1
        out[(sec.name, n)] = [ln.lyric for ln in sec.lines]
    return out


def diff(old_text: str, new_text: str, kept: list[KeptLine]) -> list[Change]:
    kept_norm = {_norm(k.text) for k in kept}
    old, new = _by_section(old_text), _by_section(new_text)
    changes = []
    for key in [*old, *(k for k in new if k not in old)]:
        a, b = old.get(key, []), new.get(key, [])
        for i in range(max(len(a), len(b))):
            o = a[i] if i < len(a) else None
            n = b[i] if i < len(b) else None
            if o != n:
                changes.append(Change(key[0], i + 1, o, n, o is not None and _norm(o) in kept_norm))
    return changes


def _read(path: Path) -> str:
    return read_text(path, Path(path).name)


def to_text(result: dict) -> str:
    if "changes" in result:
        lines = []
        for c in result["changes"]:
            flag = "  [KEPT LINE CHANGED]" if c["kept_changed"] else ""
            lines.append(f"{c['section']} #{c['index']}: {c['old']!r} -> {c['new']!r}{flag}")
        return "\n".join(lines) or "no differences"
    return f"wrote {result['path']}"


def _h_snapshot(args: argparse.Namespace):
    p = snapshot(args.song_dir)
    return {"path": str(p), "version": int(_VERSION_RE.match(p.name).group(1)), "basis": BASIS}, to_text


def _h_cut(args: argparse.Namespace):
    today = date.today().isoformat()
    return {"path": str(cut(args.song_dir, args.cut_text, args.reason, today)), "date": today,
            "basis": BASIS}, to_text


def _h_diff(args: argparse.Namespace):
    kept = parse_song_md(_read(args.song), str(args.song)).kept if args.song else []
    old_text, new_text = _read(args.old), _read(args.new)
    changes = diff(old_text, new_text, kept)
    return {"changes": [asdict(c) for c in changes],
            "kept_changed_count": sum(c.kept_changed for c in changes), "basis": BASIS}, to_text


def register(subparsers) -> None:
    p = subparsers.add_parser("drafts", help="draft snapshots, cut pool, kept-line diff")
    sub = p.add_subparsers(dest="drafts_command", required=True)
    s = sub.add_parser("snapshot", help="copy lyrics.md to drafts/lyrics-vN.md")
    s.add_argument("song_dir", type=Path, metavar="SONG_DIR")
    s.set_defaults(handler=_h_snapshot)
    c = sub.add_parser("cut", help="append text to cuts/cuts.md")
    c.add_argument("song_dir", type=Path, metavar="SONG_DIR")
    c.add_argument("cut_text", metavar="TEXT")
    c.add_argument("--reason", required=True)
    c.set_defaults(handler=_h_cut)
    d = sub.add_parser("diff", help="line diff between two lyrics drafts")
    d.add_argument("old", type=Path, metavar="OLD")
    d.add_argument("new", type=Path, metavar="NEW")
    d.add_argument("--song", type=Path, default=None, metavar="SONG_MD", help="song.md for kept lines")
    d.set_defaults(handler=_h_diff)
