"""Build data/word_rank.tsv from wordfreq (dev-only dependency)."""

import re
from pathlib import Path

from wordfreq import top_n_list

OUT = Path(__file__).resolve().parents[2] / "data" / "word_rank.tsv"
PATTERN = re.compile(r"^[a-z']+$")


def main() -> None:
    words = [w for w in top_n_list("en", 60000) if PATTERN.match(w)]
    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        for rank, word in enumerate(words, start=1):
            f.write(f"{word}\t{rank}\n")
    print(f"wrote {len(words)} words to {OUT}")


if __name__ == "__main__":
    main()
