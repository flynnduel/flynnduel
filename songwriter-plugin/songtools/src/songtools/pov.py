"""Point-of-view classifier (Pattison's four points of view)."""

import argparse
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from songtools.cli import SongtoolsError
from songtools.songfile import Section, parse_lyrics

BASIS = "Pattison four points of view (verified)"

_I = frozenset("i me my mine myself i'm i've i'll i'd we us our ours ourselves we're we've we'll".split())
_YOU = frozenset("you your yours yourself yourselves you're you've you'll you'd ya".split())
_THIRD = frozenset("he him his she her hers they them their theirs".split())
_GENERIC = re.compile(
    r"\b(?:you never know|you know|you can't|you gotta|you have to|you get)\b")
# Single-line only: an unbalanced quote must not swallow the lines after it.
_QUOTED = re.compile(r'"[^"\n]*"|“[^”\n]*”')
_WORD = re.compile(r"[\w']+")

Pov = Literal["direct_address", "second_narrative", "first_narrative", "third_narrative"]


@dataclass
class PovResult:
    pov: Pov
    i_count: int
    you_count: int
    third_count: int
    generic_you: bool


def classify_pov(text: str) -> PovResult:
    plain = _QUOTED.sub(" ", text).lower().replace("’", "'")
    words = [w.strip("'") if w.endswith("'") or w.startswith("'") else w
             for w in _WORD.findall(plain)]
    i = sum(w in _I for w in words)
    you = sum(w in _YOU for w in words)
    third = sum(w in _THIRD for w in words)
    if i and you:
        pov: Pov = "direct_address"
    elif you:
        pov = "second_narrative"
    elif i:
        pov = "first_narrative"
    else:
        pov = "third_narrative"
    return PovResult(pov, i, you, third, bool(_GENERIC.search(plain)))


def classify_sections(sections: list[Section]) -> dict:
    """{"song": PovResult, "sections": {name: PovResult}, "shift": bool}.

    Repeated section names get " (2)", " (3)" ... so none is lost. Sections with no
    lines are omitted and do not count toward a shift.
    """
    per: dict[str, PovResult] = {}
    seen: dict[str, int] = {}
    for s in sections:
        if not s.lines:
            continue
        seen[s.name] = seen.get(s.name, 0) + 1
        key = s.name if seen[s.name] == 1 else f"{s.name} ({seen[s.name]})"
        per[key] = classify_pov("\n".join(l.lyric for l in s.lines))
    song = classify_pov("\n".join(l.lyric for s in sections for l in s.lines))
    return {"song": song, "sections": per, "shift": len({r.pov for r in per.values()}) > 1}


def _handler(args: argparse.Namespace):
    path = args.lyrics_file
    try:
        text = path.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError) as e:
        raise SongtoolsError(str(path), None, f"cannot read lyrics file ({type(e).__name__})") from None
    r = classify_sections(parse_lyrics(text, str(path)))
    return {"song": asdict(r["song"]),
            "sections": {k: asdict(v) for k, v in r["sections"].items()},
            "shift": r["shift"], "basis": BASIS}, to_text


def to_text(r: dict) -> str:
    def row(label: str, p: dict) -> str:
        return (f"{label}: {p['pov']} (I {p['i_count']}, you {p['you_count']}, "
                f"third {p['third_count']})" + (", generic you" if p["generic_you"] else ""))
    lines = [row("Song", r["song"])] + [row(k, v) for k, v in r["sections"].items()]
    lines.append("POV shifts between sections" if r["shift"] else "POV consistent across sections")
    return "\n".join(lines)


def register(subparsers) -> None:
    p = subparsers.add_parser("pov", help="point-of-view classification")
    p.add_argument("lyrics_file", type=Path)
    p.set_defaults(handler=_handler)
