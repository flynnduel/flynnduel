"""The repo's .claude/skills/ copies (for cloud sessions) match the plugin skills."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
SRC = REPO / "songwriter-plugin" / "skills"
DST = REPO / ".claude" / "skills"


def expected(text: str) -> str:
    return text.replace("${CLAUDE_PLUGIN_ROOT}", "songwriter-plugin").replace(
        "${CLAUDE_PLUGIN_DATA}", ".songwriter-data")


def test_project_skill_copies_are_in_sync():
    stale = [d.name for d in sorted(SRC.iterdir()) if d.is_dir()
             and (DST / d.name / "SKILL.md").read_text() != expected((d / "SKILL.md").read_text())]
    assert not stale, f"run songwriter-plugin/scripts/sync-project-skills: {stale}"
