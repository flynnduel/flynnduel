import json

import pytest

from songtools.cli import main
from songtools.drafts import BASIS, Change, cut, diff, snapshot
from songtools.songfile import KeptLine


def test_snapshot_versions(tmp_path):
    (tmp_path / "lyrics.md").write_text("## Verse\nA\n")
    assert snapshot(tmp_path).name == "lyrics-v1.md" and snapshot(tmp_path).name == "lyrics-v2.md"


def test_snapshot_uses_highest_plus_one_and_keeps_old(tmp_path):
    (tmp_path / "lyrics.md").write_text("new\n")
    (tmp_path / "drafts").mkdir()
    (tmp_path / "drafts" / "lyrics-v5.md").write_text("five\n")
    p = snapshot(tmp_path)
    assert p.name == "lyrics-v6.md" and p.read_text() == "new\n"
    assert (tmp_path / "drafts" / "lyrics-v5.md").read_text() == "five\n"


def test_snapshot_missing_lyrics(tmp_path):
    with pytest.raises(Exception) as e:
        snapshot(tmp_path)
    assert "lyrics.md" in str(e.value)


def test_cut_appends_never_overwrites(tmp_path):
    cut(tmp_path, "old verse", "too long", "2026-11-08"); cut(tmp_path, "other", "cliche", "2026-11-09")
    body = (tmp_path / "cuts" / "cuts.md").read_text()
    assert "old verse" in body and "other" in body
    assert "## 2026-11-08 — too long\nold verse\n" in body
    assert body.index("old verse") < body.index("other")


def test_cut_preserves_existing_file(tmp_path):
    (tmp_path / "cuts").mkdir()
    (tmp_path / "cuts" / "cuts.md").write_text("# my cuts\nhand-written\n")
    cut(tmp_path, "x", "y", "2026-11-08")
    assert (tmp_path / "cuts" / "cuts.md").read_text().startswith("# my cuts\nhand-written\n")


def test_diff_flags_changed_kept_line():
    kept = [KeptLine("Down to the river", "cliche", "echo", "2026-11-08")]
    ch = diff("## Verse\nDown to the river,\n", "## Verse\nDown to the water\n", kept)
    assert ch == [Change("Verse", 1, "Down to the river,", "Down to the water", True)]


def test_diff_added_removed_unchanged_and_new_sections():
    old = "## Verse\nA\nB\nC\n## Chorus\nX\n"
    new = "## Verse\nA\nBee\n## Bridge\nZ\n"
    assert diff(old, new, []) == [
        Change("Verse", 2, "B", "Bee", False),
        Change("Verse", 3, "C", None, False),
        Change("Chorus", 1, "X", None, False),
        Change("Bridge", 1, None, "Z", False),
    ]


def test_diff_kept_case_punct_and_unchanged_kept():
    kept = [KeptLine("down, to the RIVER!", "x", "r", "d")]
    assert diff("## V\nDown to the river\nkeep\n", "## V\nDown to the river\nkeep2\n", kept)[0].kept_changed is False
    ch = diff("## V\nDown to the river\n", "## V\nUp\n", kept)
    assert ch[0].kept_changed is True
    assert diff("## V\nDown to the river\n", "## V\nDown to the river\n", kept) == []


def test_cli_roundtrip(tmp_path, capsys):
    (tmp_path / "lyrics.md").write_text("## Verse\nA\n")
    assert main(["drafts", "snapshot", str(tmp_path)]) == 0
    assert json.loads(capsys.readouterr().out)["path"].endswith("lyrics-v1.md")
    assert main(["drafts", "cut", str(tmp_path), "gone", "--reason", "slow"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["path"].endswith("cuts.md") and out["basis"] == BASIS
    a, b = tmp_path / "a.md", tmp_path / "b.md"
    a.write_text("## Verse\nDown to the river\n"); b.write_text("## Verse\nDown to the water\n")
    song = tmp_path / "song.md"
    song.write_text("# Title\n\n## Kept lines\n- \"Down to the river\" | cliche | echo | 2026-11-08\n")
    assert main(["drafts", "diff", str(a), str(b), "--song", str(song)]) == 0
    res = json.loads(capsys.readouterr().out)
    assert res["changes"][0]["kept_changed"] is True and res["kept_changed_count"] == 1


def test_cli_errors(tmp_path, capsys):
    assert main(["drafts", "snapshot", str(tmp_path)]) == 2
    assert "lyrics.md" in capsys.readouterr().err
    assert main(["drafts", "diff", str(tmp_path / "no.md"), str(tmp_path / "no2.md")]) == 2
    assert "error" in capsys.readouterr().err


def test_inserting_above_a_kept_line_does_not_flag_it():
    kept = [KeptLine("Down to the river", "x", "r", "d")]
    ch = diff("## Verse\nDown to the river\nI go\n", "## Verse\nA new first line\nDown to the river\nI go\n", kept)
    assert ch and not any(c.kept_changed for c in ch)


def test_kept_line_moved_out_of_a_removed_section_is_not_flagged():
    kept = [KeptLine("Down to the river", "x", "r", "d")]
    ch = diff("## Bridge\nDown to the river\n", "## Verse\nDown to the river\n", kept)
    assert not any(c.kept_changed for c in ch)


def test_kept_line_moved_to_another_existing_section_is_flagged():
    kept = [KeptLine("Down to the river", "x", "r", "d")]
    ch = diff("## Verse\nDown to the river\n## Chorus\nHey\n", "## Verse\nOther\n## Chorus\nHey\nDown to the river\n",
              kept)
    assert [c.kept_changed for c in ch if c.section == "Verse"] == [True]


def test_cli_diff_parse_error_names_the_file(tmp_path, capsys):
    (tmp_path / "old.md").write_text("## Verse\nA\n")
    (tmp_path / "new.md").write_text("## Verse\n[G broken\n")
    assert main(["drafts", "diff", str(tmp_path / "old.md"), str(tmp_path / "new.md")]) == 2
    assert "new.md:2:" in json.loads(capsys.readouterr().err)["error"]
