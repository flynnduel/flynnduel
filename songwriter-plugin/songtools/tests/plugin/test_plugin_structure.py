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


def check_skill_text(text: str, name: str) -> list[str]:
    """Return a list of problems found in a SKILL.md text (empty list = ok)."""
    errs: list[str] = []
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        return ["missing frontmatter"]
    fm_text, body = m.groups()
    fm = {}
    for line in fm_text.splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')
    if fm.get("name") != name:
        errs.append("name != folder")
    desc = fm.get("description", "")
    if not (desc.startswith("Use when") and len(desc) <= 1024):
        errs.append("bad description")
    subs = set(real_subcommands())

    def check_call(cand: str) -> None:
        c = cand.strip()
        if c.startswith("$ "):
            c = c[2:].strip()
        if not c.startswith(INVOKE):
            errs.append(f"INVOKE prefix missing: {cand.strip()}")
            return
        toks = c[len(INVOKE):].split()
        i = 0
        while i < len(toks) and toks[i] in ("--text", "--pron"):
            i += 2 if toks[i] == "--pron" else 1
        if i < len(toks) and not toks[i].startswith("-") and toks[i] not in subs:
            errs.append(f"unknown subcommand: {cand.strip()}")

    in_fence = False
    for line in body.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            if "songtools" in line:
                check_call(line)
        else:
            for span in re.findall(r"`([^`]*)`", line):
                if re.search(r"songtools [a-z]", span):
                    check_call(span)
            if INVOKE in line and not re.search(r"`[^`]*" + re.escape(INVOKE), line):
                check_call(line)
    for g in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/guides/([\w-]+\.md)", body):
        if not (PLUGIN_ROOT / "guides" / g).exists():
            errs.append(f"missing guide {g}")
    rb = "${CLAUDE_PLUGIN_ROOT}/guides/rulebook.md"
    first = body.find(rb)
    if first < 0:
        errs.append("rulebook path missing")
    else:
        others = [m.start() for m in re.finditer(r"guides/(?!rulebook\.md)[\w-]+\.md", body)]
        if INVOKE in body:
            others.append(body.index(INVOKE))
        if any(o < first for o in others):
            errs.append("rulebook not read first")
    return errs


@pytest.mark.parametrize("name", _skill_params())
def test_skill_frontmatter_and_invocation(name):
    path = PLUGIN_ROOT / "skills" / name / "SKILL.md"
    assert path.exists(), path
    assert check_skill_text(path.read_text(), name) == []


FM = "---\nname: x\ndescription: Use when testing.\n---\n"
RB = "Read ${CLAUDE_PLUGIN_ROOT}/guides/rulebook.md first.\n"
GOOD = FM + RB + "```\n" + INVOKE + " rhyme a b\n```\n"


def _bad(body, needle):
    errs = check_skill_text(FM + body, "x")
    assert any(needle in e for e in errs), (needle, errs)


def test_helper_positive():
    assert check_skill_text(GOOD, "x") == []
    assert check_skill_text(FM + RB + "`" + INVOKE + " rhyme a b`\nsongtools is offline.\n", "x") == []
    assert check_skill_text(FM + RB + "$ " + INVOKE + " --pron p.txt --text rhyme a b\n", "x") == []
    assert check_skill_text(FM + RB + "Then ${CLAUDE_PLUGIN_ROOT}/guides/toolkit.md.\n", "x") == []


def test_helper_rejects_bare_and_misprefixed_invocations():
    _bad(RB + "```\nuv run songtools rhyme a b\n```\n", "INVOKE")
    _bad(RB + "```\n$ songtools rhyme a b\n```\n", "INVOKE")
    _bad(RB + '```\nUV_PROJECT_ENVIRONMENT="x/venv" uv run --frozen --project X songtools rhyme\n```\n', "INVOKE")
    _bad(RB + "Run `songtools rhyme a b` now.\n", "INVOKE")
    _bad(RB + "Run `uv run songtools rhyme a b` now.\n", "INVOKE")


def test_helper_rejects_unknown_subcommand_even_after_global_flags():
    _bad(RB + INVOKE + " bogus a\n", "subcommand")
    _bad(RB + INVOKE + " --pron p.txt --text bogus a\n", "subcommand")


def test_helper_rulebook_first():
    _bad("Read ${CLAUDE_PLUGIN_ROOT}/guides/toolkit.md.\n" + RB, "rulebook")
    _bad("Intro.\n" + INVOKE + " version\n" + RB, "rulebook")
    _bad("No guide here.\n", "rulebook")
    _bad("Read guides/rulebook.md first.\n", "rulebook")
