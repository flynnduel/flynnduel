"""JSON (default) or readable text output."""

import json
import sys
from typing import Callable


def emit(result: dict, text: bool, to_text: Callable[[dict], str] | None) -> None:
    if text and to_text is not None:
        sys.stdout.write(to_text(result).rstrip("\n") + "\n")
    else:
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
