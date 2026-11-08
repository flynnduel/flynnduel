"""songtools command-line entry point."""

import argparse
import importlib
import json
import os
import sys
from pathlib import Path

from songtools import __version__
from songtools.output import emit

# Later tasks append module names (each exposes register(subparsers)).
MODULES: tuple[str, ...] = ("songtools.rhyme", "songtools.stability")


class SongtoolsError(Exception):
    def __init__(self, file: str | None, line: int | None, message: str):
        super().__init__(message)
        self.file = file
        self.line = line
        self.message = message

    def __str__(self) -> str:
        prefix = str(self.file) if self.file is not None else ""
        if self.line is not None:
            prefix = f"{prefix}:{self.line}" if prefix else str(self.line)
        return f"{prefix}: {self.message}" if prefix else self.message


def _version_handler(args: argparse.Namespace) -> tuple[dict, None]:
    return {"version": __version__}, None


def _register_version(subparsers) -> None:
    p = subparsers.add_parser("version", help="print the songtools version")
    p.set_defaults(handler=_version_handler)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="songtools")
    parser.add_argument("--text", action="store_true", help="readable text output")
    parser.add_argument("--pron", type=Path, default=None, metavar="FILE",
                        help="personal pronunciations file (env SONGTOOLS_PRON)")
    sub = parser.add_subparsers(dest="command", required=True)
    _register_version(sub)
    for name in MODULES:
        importlib.import_module(name).register(sub)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.pron is None and os.environ.get("SONGTOOLS_PRON"):
        args.pron = Path(os.environ["SONGTOOLS_PRON"])
    try:
        # Handlers return (result, to_text); to_text may be None.
        result, to_text = args.handler(args)
        emit(result, args.text, to_text)
    except SongtoolsError as e:
        json.dump({"error": str(e)}, sys.stderr, ensure_ascii=False)
        sys.stderr.write("\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
