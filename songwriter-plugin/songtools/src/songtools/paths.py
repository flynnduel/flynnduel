"""Locations of vendored data files."""

import os
from pathlib import Path


def data_dir() -> Path:
    env = os.environ.get("SONGTOOLS_DATA")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[3] / "data"
