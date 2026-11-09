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
SKILLS_PENDING = {"newsong", "idea", "structure", "melody", "chords", "arrange", "chart", "bank"}


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


def test_rulebook_folder_tree_lists_pronunciations_file():
    t = (PLUGIN_ROOT / "guides/rulebook.md").read_text()
    tree = t.split("## Song folder", 1)[1].split("```")[1]
    assert "pronunciations.txt" in tree
    assert "--pron" in tree


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


# Skill-authoring standards (writing-skills; Anthropic best practices): the body stays under
# 500 lines, and the description says when to use the skill without summarizing its process.
MAX_BODY_LINES = 500
# Workflow-summary patterns, not bare words: music descriptions legitimately say
# "half step", "vocal runs", "runs long" or "and then the chorus".
_VERBS = r"(?:run|check|write|draft|ask|read|measure|dispatch)\w*"
WORKFLOW_WORDS = re.compile(
    r"\bthen,? " + _VERBS
    + r"|\bsteps? \d"
    + r"|\bdispatch\w*"
    + r"|\bruns? (?:the|a|an|each|every) (?:\w+ )?(?:tools?|checks?|scripts?|scans?)\b",
    re.I)


def parse_frontmatter(fm_text: str) -> dict[str, str]:
    """Top-level keys of simple YAML frontmatter, including block (> |) and multi-line plain scalars."""
    fm: dict[str, str] = {}
    key, style, parts = None, None, []

    def close():
        if key is not None:
            sep = "\n" if style and style.startswith("|") else " "
            fm[key] = sep.join(p for p in parts if p).strip().strip('"')

    for line in fm_text.splitlines():
        if line[:1] in (" ", "\t") and key is not None:
            parts.append(line.strip())
            continue
        if ":" in line:
            close()
            k, v = line.split(":", 1)
            key, v = k.strip(), v.strip()
            style = v if v in (">", "|", ">-", "|-", ">+", "|+") else None
            parts = [] if style else [v]
    close()
    return fm


def check_skill_text(text: str, name: str) -> list[str]:
    """Return a list of problems found in a SKILL.md text (empty list = ok)."""
    errs: list[str] = []
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        return ["missing frontmatter"]
    fm_text, body = m.groups()
    fm = parse_frontmatter(fm_text)
    if fm.get("name") != name:
        errs.append("name != folder")
    desc = fm.get("description", "")
    if not (desc.startswith("Use when") and len(desc) <= 1024):
        errs.append("bad description")
    if WORKFLOW_WORDS.search(desc):
        errs.append("description summarizes workflow (say when to use, not how it works)")
    if len(body.splitlines()) > MAX_BODY_LINES:
        errs.append(f"body over {MAX_BODY_LINES} lines")
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


def test_helper_rejects_body_over_500_lines():
    filler = "".join(f"line {i}\n" for i in range(500 - GOOD[len(FM):].count("\n")))
    ok = GOOD + filler
    assert ok[len(FM):].count("\n") == 500
    assert check_skill_text(ok, "x") == []
    errs = check_skill_text(ok + "one more\n", "x")
    assert any("500 lines" in e for e in errs), errs


def _desc(desc: str) -> str:
    return f"---\nname: x\ndescription: {desc}\n---\n" + RB


@pytest.mark.parametrize("desc", [
    "Use when drafting lyrics; reads the song, then runs the checks.",
    "Use when drafting lyrics, then check each line.",
    "Use when editing. Then write the notes.",
    "Use when editing: step 1 measure, step 2 note.",
    "Use when planning; dispatches a subagent per section.",
    "Use when checking rhyme; runs the tool on every line.",
    "Use when checking rhyme and run a check per verse.",
])
def test_helper_rejects_description_that_summarises_workflow(desc):
    errs = check_skill_text(_desc(desc), "x")
    assert any("workflow" in e for e in errs), errs


@pytest.mark.parametrize("desc", [
    "Use when a melody moves by a half step or a whole step.",
    "Use when vocal runs crowd the line or the song runs long.",
    "Use when the verse builds and then the chorus drops.",
    "Use when a writer steps away from a song and comes back.",
])
def test_helper_allows_music_words_in_description(desc):
    assert check_skill_text(_desc(desc), "x") == []


@pytest.mark.parametrize("style", [">", "|", ">-", "|-"])
def test_helper_reads_block_scalar_descriptions(style):
    good = f"---\nname: x\ndescription: {style}\n  Use when testing\n  block descriptions.\n---\n" + RB
    assert check_skill_text(good, "x") == []
    bad = f"---\nname: x\ndescription: {style}\n  Use when testing;\n  then run the checks.\n---\n" + RB
    assert any("workflow" in e for e in check_skill_text(bad, "x"))
    wrong = f"---\nname: x\ndescription: {style}\n  Helps with lyrics.\n---\n" + RB
    assert "bad description" in check_skill_text(wrong, "x")


def test_helper_reads_plain_multiline_description():
    bad = "---\nname: x\ndescription: Use when testing,\n  then run the checks.\n---\n" + RB
    assert any("workflow" in e for e in check_skill_text(bad, "x"))
