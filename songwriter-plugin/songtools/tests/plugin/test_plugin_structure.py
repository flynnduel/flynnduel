"""Structure tests for the songwriter plugin (manifest, marketplace, guides, skills)."""
import json
import re
from pathlib import Path

import pytest
from songtools.cli import build_parser

PLUGIN_ROOT = Path(__file__).resolve().parents[3]

INVOKE = 'UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools'
SKILLS = ["newsong", "idea", "structure", "lyrics", "melody", "chords", "arrange", "chart", "critique", "finalcheck", "bank"]
# Skills not written yet; each skill task removes its own name from this set.
SKILLS_PENDING = {"newsong", "idea", "structure", "lyrics", "melody", "chords", "arrange", "chart", "critique",
                  "finalcheck", "bank"}


def real_subcommands() -> list[str]:
    import argparse
    parser = build_parser()
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return list(action.choices)
    raise AssertionError("no subparsers found")


def test_manifest():
    m = json.loads((PLUGIN_ROOT / ".claude-plugin/plugin.json").read_text())
    assert m["name"] == "songwriter" and m["version"] and m["description"]


def test_no_bin_dir():
    assert not (PLUGIN_ROOT / "bin").exists()


def test_marketplace_points_at_plugin():
    mk = json.loads((PLUGIN_ROOT.parent / ".claude-plugin/marketplace.json").read_text())
    assert any(p["source"] == "./songwriter-plugin" and p["name"] == "songwriter" for p in mk["plugins"])


def test_rulebook_has_the_nine_rules_and_uv_fallback():
    t = (PLUGIN_ROOT / "guides/rulebook.md").read_text()
    for phrase in ["Measure, don't guess", "Name the basis", "accept the writer's call", "Drafting mode is quiet",
                   "Music is coached", "No genre bias", "never say a line sounds like AI", "State limits",
                   "Kept is not silenced", "install uv"]:
        assert phrase.lower() in t.lower(), phrase


def test_guides_have_no_plugin_variables():
    for g in (PLUGIN_ROOT / "guides").glob("*.md"):
        assert "${CLAUDE_PLUGIN_" not in g.read_text(), g.name


def test_toolkit_guide_documents_every_subcommand():
    t = (PLUGIN_ROOT / "guides/toolkit.md").read_text()
    for sub in real_subcommands():
        assert f"### {sub}" in t, sub


def test_toolkit_guide_has_prosody_limit_and_behaviours():
    t = (PLUGIN_ROOT / "guides/toolkit.md").read_text()
    assert "Scoring is a simplified version of Hayes (2005), whose model matched listeners' preferred settings about 70% of the time on folk-song data." in t
    assert "## Behaviours to explain" in t


def _skill_params():
    return [pytest.param(n, marks=pytest.mark.xfail(reason="skill not written yet", strict=False))
            if n in SKILLS_PENDING else n for n in SKILLS]


@pytest.mark.parametrize("name", _skill_params())
def test_skill_frontmatter_and_invocation(name):
    path = PLUGIN_ROOT / "skills" / name / "SKILL.md"
    assert path.exists(), path
    text = path.read_text()
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    assert m, "missing frontmatter"
    fm_text, body = m.groups()
    fm = {}
    for line in fm_text.splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')
    assert fm.get("name") == name
    desc = fm.get("description", "")
    assert desc.startswith("Use when") and len(desc) <= 1024
    subs = set(real_subcommands())
    for line in body.splitlines():
        if "songtools " not in line:
            continue
        stripped = line.strip().lstrip("`-*$ ").strip()
        if INVOKE in line:
            assert stripped.startswith(INVOKE), line
            after = line.split(INVOKE, 1)[1].split()
            toks = [t for t in after if not t.startswith("-")]
            if toks:
                assert toks[0] in subs, line
        else:
            # prose: only a backticked `songtools <sub>` is a command reference
            for sub in re.findall(r"`songtools ([a-z]+)", line):
                assert sub in subs, line
    for g in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/guides/([\w-]+\.md)", body):
        assert (PLUGIN_ROOT / "guides" / g).exists(), g
    assert re.search(r"guides/rulebook\.md", body), "body must send Claude to guides/rulebook.md"
    first_read = body.find("guides/rulebook.md")
    other = [body.find(f"guides/{x}.md") for x in ("toolkit",) if f"guides/{x}.md" in body]
    assert all(first_read < o for o in other), "rulebook must be read first"
