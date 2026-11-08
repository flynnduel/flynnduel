"""Lint and content tests for the songwriter plugin guides.

Lint design choice: the brief limits the tag rule to bullets under `## Rules`, `## Checks` and
`## Prompts` headings. The lyrics guide needs topical `##` sections (Rhyme, Stability, ...), so the
rule is applied more strictly: EVERY bullet line anywhere in a guide (`- `, `* `, `1. `) must end with
a source tag. sources.md (link lists) and fenced code blocks are exempt from the bullet rule.
"""
import re
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[3]

TAGS = ("[verified]", "[as reported]", "[unverified]", "[design]")
KNOWN_AUTHORS = [
    "Pattison", "Webb", "Davis", "Perricone", "Blume", "Everett", "Temperley", "de Clercq", "Doll", "Spicer",
    "Richards", "Nobile", "Summach", "Stroud", "Osborn", "Hayes", "Kaun", "Smith", "Lerman", "Dodson", "Stolpe",
    "Owsinski", "Moore", "Lavengood", "Cobb", "Greene", "Hober", "Rooksby", "Kostka", "Payne", "Tweedy", "Zollo",
    "Murphy", "Léveillé Gauvin", "Duinker", "Carter", "Matthews", "McCoy", "Williams",
]
BULLET = re.compile(r"^\s*(?:[-*]|\d+\.)\s+")
QUOTE = re.compile(r'"([^"]*)"|“([^”]*)”')


def _sources_headings(guides_dir: Path) -> str:
    src = guides_dir / "sources.md"
    if not src.exists():
        return ""
    return "\n".join(l for l in src.read_text().splitlines() if l.startswith("## "))


def lint_guide(path) -> list[str]:
    path = Path(path)
    name = path.name
    problems: list[str] = []
    text = path.read_text()
    if "${CLAUDE_PLUGIN_" in text:
        problems.append(f"{name}: contains a ${{CLAUDE_PLUGIN_ variable")
    headings = _sources_headings(path.parent)
    in_fence = False
    for n, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for m in QUOTE.finditer(line):
            if len((m.group(1) or m.group(2)).split()) > 14:
                problems.append(f"{name}:{n}: quote longer than 14 words")
        if name == "sources.md":
            continue
        if BULLET.match(line) and not line.rstrip().endswith(TAGS):
            problems.append(f"{name}:{n}: rule line has no source tag")
        for author in KNOWN_AUTHORS:
            if author in line and author not in headings:
                problems.append(f"{name}:{n}: author {author} has no entry in sources.md")
    return problems


def test_lint_flags_untagged_rule(tmp_path):
    p = tmp_path / "g.md"
    p.write_text("## Rules\n- Put the title first\n")
    assert lint_guide(p) == ["g.md:2: rule line has no source tag"]


def test_lint_flags_long_quote(tmp_path):
    p = tmp_path / "g.md"
    p.write_text('## Rules\n- He said "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen" [verified]\n')
    assert any("quote" in m for m in lint_guide(p))


def test_lint_flags_unlisted_author_and_variable(tmp_path):
    (tmp_path / "sources.md").write_text("## Webb\nRead: x\n")
    p = tmp_path / "g.md"
    p.write_text("## Rules\n- Pattison says so [verified]\n- ok ${CLAUDE_PLUGIN_ROOT} [design]\n")
    out = lint_guide(p)
    assert any("Pattison" in m for m in out) and any("CLAUDE_PLUGIN_" in m for m in out)


def test_lint_ignores_fenced_code(tmp_path):
    p = tmp_path / "g.md"
    p.write_text("```\n- untagged in code\n```\n")
    assert lint_guide(p) == []


@pytest.mark.parametrize("guide", ["sources", "lyrics", "drafting"])   # extended by Tasks 3-5
def test_guide_is_clean(guide):
    assert lint_guide(PLUGIN_ROOT / f"guides/{guide}.md") == []


def test_sources_entries_have_read_status_links():
    t = (PLUGIN_ROOT / "guides/sources.md").read_text()
    entries = [e for e in re.split(r"^## ", t, flags=re.M)[1:]]
    assert len(entries) >= 13
    for e in entries:
        for k in ("Read:", "Status:", "Links:"):
            assert k in e, e.splitlines()[0]
    davis = next(e for e in entries if e.startswith("Davis"))
    assert "as reported" in davis.lower()


def test_lyrics_guide_has_core_sections():
    t = (PLUGIN_ROOT / "guides/lyrics.md").read_text()
    for h in ["## Rhyme", "## Stability", "## Title and verse development", "## Point of view",
              "## Metaphor", "## Object writing", "## Lenses", "## Misattributions"]:
        assert h in t


def test_drafting_guide_covers_spec_section_8():
    t = (PLUGIN_ROOT / "guides/drafting.md").read_text().lower()
    for k in ["writer's material", "particular", "self-audit", "cliché pairs", "irregularity",
              "song's voice", "any size", "never"]:
        assert k in t, k
