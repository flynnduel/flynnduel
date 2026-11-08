"""Cliche scanner: rhyme pairs, stock phrases, abstractions, stock images, named emotions."""

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from songtools.cli import SongtoolsError
from songtools.paths import data_dir
from songtools.songfile import Section, end_word, parse_lyrics, read_text

BASIS = "Pattison rhyme pairs (verified); other lists tagged per entry"

Kind = Literal["rhyme_pair", "phrase", "abstract", "stock_image", "emotion_naming"]
# (data key, hit kind, strict only)
_TEXT_LISTS: tuple[tuple[str, Kind, bool], ...] = (
    ("phrases", "phrase", False),
    ("abstract", "abstract", False),
    ("stock_image", "stock_image", True),
    ("emotion_naming", "emotion_naming", True),
)


@dataclass
class ClicheHit:
    line_number: int  # for a rhyme pair, the later of the two lines
    kind: Kind
    match: str
    source: str


def _read_json(path: Path) -> dict:
    text = read_text(path, "cliche file")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise SongtoolsError(str(path), e.lineno, f"cliche file is not valid JSON ({e.msg})") from None
    if not isinstance(data, dict):
        raise SongtoolsError(str(path), None, "cliche file must be a JSON object")
    return data


_LISTS = ("rhyme_pairs", "phrases", "abstract", "stock_image", "emotion_naming")


def _nonempty(v) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _check_entry(key: str, e, file: str) -> None:
    if key == "rhyme_pairs":
        ok = isinstance(e, dict) and isinstance(e.get("pair"), list) \
            and len(e["pair"]) == 2 and all(_nonempty(w) for w in e["pair"])
        if not ok:
            raise SongtoolsError(file, None, "each 'rhyme_pairs' entry needs 'pair': "
                                 "a list of two non-empty strings")
    elif not (isinstance(e, dict) and _nonempty(e.get("text"))):
        raise SongtoolsError(file, None, f"each {key!r} entry needs a non-empty string 'text'")
    if "source" in e and not isinstance(e["source"], str):
        raise SongtoolsError(file, None, f"{key!r} entry 'source' must be a string")


def load_cliches(path: Path | None = None, extra: Path | None = None) -> dict:
    """Load the data file (default data/cliches.json); entries of `extra` are appended per list."""
    data = _read_json(path or data_dir() / "cliches.json")
    if extra is not None:
        for key, entries in _read_json(extra).items():
            if key not in _LISTS:
                raise SongtoolsError(str(extra), None, f"unknown list {key!r}")
            if not isinstance(entries, list):
                raise SongtoolsError(str(extra), None, f"{key!r} must be a list")
            for e in entries:
                _check_entry(key, e, str(extra))
                e.setdefault("source", "user list")
            data.setdefault(key, []).extend(entries)
    return data


def _pattern(text: str) -> re.Pattern:
    words = [re.escape(w) for w in text.lower().replace("’", "'").split()]
    return re.compile(r"(?<![\w'])" + r"\s+".join(words) + r"(?![\w'])")


def scan(sections: list[Section], cliches: dict, strict: bool = False) -> list[ClicheHit]:
    hits: list[ClicheHit] = []
    lists = [(k, kind) for k, kind, strict_only in _TEXT_LISTS if strict or not strict_only]
    compiled = {k: [(e["text"], e.get("source", ""), _pattern(e["text"]))
                    for e in cliches.get(k, [])] for k, _ in lists}
    pairs = [("/".join(e["pair"]), {w.lower() for w in e["pair"]}, e.get("source", ""))
             for e in cliches.get("rhyme_pairs", [])]
    for section in sections:
        lines = [l for l in section.lines if l.lyric.strip()]
        for line in lines:
            lyric = line.lyric.lower().replace("’", "'")
            for key, kind in lists:
                for text, source, pat in compiled[key]:
                    if pat.search(lyric):
                        hits.append(ClicheHit(line.number, kind, text, source))
        for i, later in enumerate(lines):
            wl = end_word(later)
            for gap in (1, 2):
                if i - gap < 0:
                    continue
                wb = end_word(lines[i - gap])
                for label, words, source in pairs:
                    if wl != wb and {wl, wb} == words:
                        hits.append(ClicheHit(later.number, "rhyme_pair", label, source))
    hits.sort(key=lambda h: h.line_number)
    return hits


def _handler(args: argparse.Namespace):
    path = args.lyrics_file
    text = read_text(path, "lyrics file")
    cliches = load_cliches(extra=args.extra)
    hits = scan(parse_lyrics(text, str(path)), cliches, args.strict)
    return {"hits": [asdict(h) for h in hits], "strict": args.strict, "basis": BASIS}, to_text


def to_text(r: dict) -> str:
    if not r["hits"]:
        return "No cliches found"
    return "\n".join(f"line {h['line_number']}: {h['kind']} {h['match']!r} [{h['source']}]"
                     for h in r["hits"])


def register(subparsers) -> None:
    p = subparsers.add_parser("cliche", help="scan lyrics for cliches")
    p.add_argument("lyrics_file", type=Path)
    p.add_argument("--strict", action="store_true", help="also scan stock images and named emotions")
    p.add_argument("--extra", type=Path, default=None, metavar="FILE",
                   help="user JSON file merged into the cliche lists")
    p.set_defaults(handler=_handler)
