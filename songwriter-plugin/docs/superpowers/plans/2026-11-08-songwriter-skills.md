# Songwriter Plugin: Guides, Skills and Packaging Implementation Plan (Plan 2 of 2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the finished `songtools` toolkit into an installable Claude Code plugin. The plugin has research-based guides and eleven slash-command skills (`/newsong`, `/idea`, `/structure`, `/lyrics`, `/melody`, `/chords`, `/arrange`, `/chart`, `/critique`, `/finalcheck`, `/bank`), each tested against real failure cases before it counts as done.

**Architecture:** Skills are written as Markdown instructions (`skills/<name>/SKILL.md`). Each one loads a shared rulebook and only the guides its stage needs, and calls `songtools` for anything countable. Guides condense the verified research into rules and checks, each tagged with how well it is sourced. Two kinds of check apply. A pytest suite checks the plugin's structure: manifest, frontmatter, the invocation line, guide references, subcommand names and guide tagging. Each skill is also pressure-tested with the writing-skills method: a baseline run without the skill, then a run with it, against written pass criteria.

**Tech Stack:** Claude Code plugin format (`.claude-plugin/plugin.json`, `skills/`), Markdown, the existing `songtools` uv project (Python ≥ 3.11, pytest 9.2.0) for the structure tests.

**Spec:** `songwriter-plugin/docs/superpowers/specs/2026-11-08-songwriter-plugin-design.md` (sections 2, 3, 4, 6, 7, 8, 9 skills part, 11 steps 4–6, 12). Toolkit interfaces: `songwriter-plugin/songtools/README.md` and module docstrings. Research: `songwriter-plugin/reports/Songwriting plugin research.md` and `songwriter-plugin/research_notes/Songwriting plugin research/0*.md`. Toolkit decisions that skills must respect: `songwriter-plugin/docs/superpowers/plans/2026-11-08-songtools-toolkit-execution-log.md`.

## Global Constraints

- Plugin root: `songwriter-plugin/`. Manifest at `songwriter-plugin/.claude-plugin/plugin.json` with `"name": "songwriter"`. **No `bin/` directory**, because it would block installing on claude.ai and Cowork.
- Every toolkit call in a SKILL.md uses exactly this prefix: `UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools`. Guide paths in SKILL.md are written `${CLAUDE_PLUGIN_ROOT}/guides/<name>.md`. Only SKILL.md bodies get variable substitution, so guides never contain these variables.
- SKILL.md frontmatter: `name` equals the folder name. `description` starts with "Use when", is at most 1024 characters, and says when to use the skill, not how it works.
- Songs live in the writer's project at `songs/<title>/`, never inside the plugin. The file formats are exactly those in `songtools/README.md`. Additional `## Core` keys that skills read and write: `entry`, `mode` (`drafting` | `editing`), `lenses` (comma list, default `pattison`; options `webb`, `commercial`), `status` (`working` | `done for now` | `done`).
- The shared rules from the spec (section 2), verbatim in meaning. Every skill obeys all nine:
  1. Measure, don't guess.
  2. Name the basis.
  3. Flag, explain, offer 2–4 options, accept the writer's call.
  4. Drafting mode is quiet.
  5. Lyrics are co-written; music is coached; arrangement is guidance (no parts, tabs or notation).
  6. No genre bias; commercial heuristics apply only when declared.
  7. Stock language is a craft issue; never say a line "sounds like AI".
  8. State limits.
  9. Kept is not silenced.
- Guides paraphrase and never copy. Quotes are at most 14 words. Every rule or check line ends with one tag: `[verified]`, `[as reported]`, `[unverified]` or `[design]`. Authors whose texts were not read (Davis, *Tunesmith*, Perricone's *Great Songwriting Techniques*, Rooksby, Owsinski's numbers) appear only as `[as reported]`, or are left out.
- `songtools` is changed only where a skill task needs it, with a failing test first, and the full songtools suite stays green.
- Commit trailer: the Co-Authored-By and Claude-Session lines from the committing agent's own system context (session `https://claude.ai/code/session_018mK5aRJ1Ar8bEKdNKeqjr9`).
- Skill pressure tests: implementers of skill tasks **may** dispatch *test-subject* subagents to run scenarios, which is the writing-skills method. They never dispatch reviewers or helpers.

## Review Focus

1. **`uv` missing on the writer's machine:** the skill should say, in one line, how to install `uv` and stop, not fail with a raw shell error. Pinned in Task 1 (rulebook text plus a structure test).
2. **A stage run before its inputs exist** (for example `/finalcheck` with no `music.md`, `/arrange` with no form): the skill should work from what exists and say what's missing. It must never invent missing files. Pinned in scenarios F2 (Task 7) and A3 (Task 9).
3. **Lyrics pasted into chat with no song folder:** the skill should offer to create `songs/<title>/` and still help. Pinned in scenario L5 (Task 6).
4. **`undetermined` or `estimated` results from the toolkit:** the skill should relay them plainly and offer to add a pronunciation, not cover them up. Pinned in scenario L3 (Task 6).
5. **The writer keeps a flagged line:** the skill writes the kept line to `song.md` in the exact format `parse_song_md` reads, and revisits it at `/critique` and `/finalcheck`. Pinned in scenario L2 (Task 6, automated parse check) and scenarios C4 and F1 (Task 7).

---

## File structure

```
songwriter-plugin/
├── .claude-plugin/plugin.json
├── README.md                         (plugin user guide)
├── guides/
│   ├── rulebook.md   toolkit.md   sources.md   drafting.md
│   ├── lyrics.md     structure.md melody.md    harmony.md
│   ├── guitar.md     arrangement.md critique.md process.md
├── skills/
│   └── newsong/ idea/ structure/ lyrics/ melody/ chords/ arrange/ chart/ critique/ finalcheck/ bank/
│       └── SKILL.md
├── skill-tests/<skill>.md            (scenarios, baseline transcript summary, with-skill result)
└── songtools/tests/plugin/
    ├── test_plugin_structure.py
    └── test_guides.py
.claude-plugin/marketplace.json        (repo root /home/user/flynnduel)
```

---

### Task 1: Plugin scaffold, toolkit invocation, rulebook and toolkit guide

**Files:**
- Create: `songwriter-plugin/.claude-plugin/plugin.json`, `/home/user/flynnduel/.claude-plugin/marketplace.json`, `songwriter-plugin/guides/rulebook.md`, `songwriter-plugin/guides/toolkit.md`, `songwriter-plugin/songtools/tests/plugin/__init__.py`, `songwriter-plugin/songtools/tests/plugin/test_plugin_structure.py`

**Interfaces:**
- Produces:
  - `INVOKE` — the exact prefix string from Global Constraints. Defined once in `test_plugin_structure.py` and asserted present in every SKILL.md that calls the toolkit.
  - `guides/rulebook.md` — the nine shared rules, the kept-lines rule, the modes, the lenses, the song-folder layout and the `## Core` keys.
  - `guides/toolkit.md` — the command list, the JSON shape for each subcommand, the limits, and the deferred behaviours skills must explain.
  - The `PLUGIN_ROOT` test fixture, which is `Path(__file__).resolve().parents[3]`.

- [ ] **Step 1: Verify the invocation hands-on.** In a scratch directory, set `CLAUDE_PLUGIN_ROOT=/home/user/flynnduel/songwriter-plugin` and `CLAUDE_PLUGIN_DATA=<scratch>/data`. Run the `INVOKE` prefix with `version`, then with `--text stability /home/user/flynnduel/songwriter-plugin/songtools/tests/fixtures/sample_song/lyrics.md`, from a working directory **outside** the plugin.
  Expected: exit 0 both times; `<scratch>/data/venv` exists; `songtools/.venv` is untouched. If the combination fails, record the working alternative in the report as a ruling and use it as `INVOKE` everywhere.

- [ ] **Step 2: Write the failing structure tests**

```python
INVOKE = 'UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools'
SKILLS = ["newsong","idea","structure","lyrics","melody","chords","arrange","chart","critique","finalcheck","bank"]

def test_manifest():
    m = json.loads((PLUGIN_ROOT/".claude-plugin/plugin.json").read_text())
    assert m["name"] == "songwriter" and m["version"] and m["description"]

def test_no_bin_dir():
    assert not (PLUGIN_ROOT/"bin").exists()

def test_marketplace_points_at_plugin():
    mk = json.loads((PLUGIN_ROOT.parent/".claude-plugin/marketplace.json").read_text())
    assert any(p["source"] == "./songwriter-plugin" and p["name"] == "songwriter" for p in mk["plugins"])

def test_rulebook_has_the_nine_rules_and_uv_fallback():
    t = (PLUGIN_ROOT/"guides/rulebook.md").read_text()
    for phrase in ["Measure, don't guess", "Name the basis", "accept the writer's call", "Drafting mode is quiet",
                   "Music is coached", "No genre bias", "never say a line sounds like AI", "State limits",
                   "Kept is not silenced", "install uv"]:
        assert phrase.lower() in t.lower(), phrase

def test_toolkit_guide_documents_every_subcommand():
    t = (PLUGIN_ROOT/"guides/toolkit.md").read_text()
    for sub in real_subcommands():          # from songtools.cli.build_parser()
        assert f"### {sub}" in t, sub

@pytest.mark.parametrize("name", SKILLS)
def test_skill_frontmatter_and_invocation(name):   # xfail until each skill task lands
    ...
```

`real_subcommands()` reads the subparser choices from `songtools.cli.build_parser()`. The parametrized skill test asserts:
- the file exists;
- the frontmatter `name` equals the folder name;
- the description starts with `Use when` and is at most 1024 characters;
- every line containing `songtools ` that is not prose starts with `INVOKE`;
- every `${CLAUDE_PLUGIN_ROOT}/guides/X.md` it names exists;
- every `songtools <sub>` it names is in `real_subcommands()`;
- the body tells Claude to read `guides/rulebook.md` first.

Mark it `xfail(strict=False)` with reason "skill not written yet" for the skills not yet present. Each skill task removes that skill from the xfail set.

- [ ] **Step 3: Run to verify failure** — `cd songwriter-plugin/songtools && uv run --frozen pytest tests/plugin -v`. Expected: the manifest, marketplace, rulebook and toolkit-guide tests FAIL (files missing); the skill tests are xfail.

- [ ] **Step 4: Write the files**
  - `plugin.json`: `name` "songwriter", `version` "0.1.0", a one-sentence description, `author` from git config.
  - `marketplace.json`: `name` "flynnduel", `owner`, and `plugins: [{"name": "songwriter", "source": "./songwriter-plugin", "description": …}]`.
  - `rulebook.md`, with these sections:
    - `## The nine rules`: each rule plus one example of doing it and one of breaking it.
    - `## Kept lines`: the register format `- "text" | flag | reason | YYYY-MM-DD` under `## Kept lines` in song.md; don't re-flag in the same session; re-check when neighbours change; always return once at /critique and /finalcheck.
    - `## Modes and lenses`
    - `## Song folder`: copy the layout from spec section 4 and the README formats.
    - `## Running the toolkit`: `INVOKE` written with literal `${…}` placeholders and a note that skills carry the real line. If `uv` is not found, tell the writer "install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`" and stop. The first run installs packages once.
    - `## Never do`: write parts or tab, declare a song finished, accuse a writer of using AI, or present a secondhand claim as verified.
  - `toolkit.md`: one `### <subcommand>` section per subcommand. Each gives its arguments, the JSON shape (captured by running it on the sample song), what `undetermined` and `estimated` look like, and the stated limits (the prosody limit sentence verbatim).
  - Add a `## Behaviours to explain` section covering:
    - Webb's lens calls homophones "false rhyme";
    - prosody proposals often start in pickup slots;
    - multisyllable rhymes are undercounted;
    - the PDF font has no ♯ or ♭, so charts use `#` and `b`;
    - an explicit key reports confidence 1.0, so say "key given";
    - cliché pairs come from `cliche`, not `rhyme`;
    - `key` is called once per section;
    - `midi` plays each section once in file order.

- [ ] **Step 5: Run to verify pass** — the same command. Expected: all non-xfail tests PASS; the songtools suite (`uv run --frozen pytest -q`) is still green.

- [ ] **Step 6: Commit** — `git commit -m "feat(plugin): scaffold, marketplace, rulebook and toolkit guide"`

---

### Task 2: Guide lint and the lyrics, drafting and sources guides

**Files:**
- Create: `songwriter-plugin/guides/{sources,lyrics,drafting}.md`, `songwriter-plugin/songtools/tests/plugin/test_guides.py`

**Interfaces:**
- Consumes: `PLUGIN_ROOT` from Task 1.
- Produces:
  - `TAGS = ("[verified]", "[as reported]", "[unverified]", "[design]")`.
  - `lint_guide(path) -> list[str]`, which returns problems (an empty list means clean). The rules:
    - every bullet under a `## Rules`, `## Checks` or `## Prompts` heading ends with a tag;
    - every quoted run (`"…"` or `“…”`) is at most 14 words;
    - every author named in a `[verified]` or `[as reported]` line has an entry in `sources.md`;
    - no `${CLAUDE_PLUGIN_` text appears.
  - `guides/sources.md`: one `## <Author>` entry per source, giving what was read, the tag, and the links. It's built from the report's evidence table.

Guide content comes only from the research report and notes, paraphrased.
- `lyrics.md`: Pattison's rhyme ladder, consonant families, four stability elements, title spotlights and recoloring, four POVs and the POV check, metaphor types, object writing, productive repetition; Webb's strict lens; Davis as reported; misattributions to avoid.
- `drafting.md`: spec section 8 items 1–8, each turned into a check.

- [ ] **Step 1: Write the failing tests**

```python
def test_lint_flags_untagged_rule(tmp_path):
    p = tmp_path/"g.md"; p.write_text("## Rules\n- Put the title first\n")
    assert lint_guide(p) == ["g.md:2: rule line has no source tag"]

def test_lint_flags_long_quote(tmp_path):
    p = tmp_path/"g.md"; p.write_text('## Rules\n- He said "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen" [verified]\n')
    assert any("quote" in m for m in lint_guide(p))

@pytest.mark.parametrize("guide", ["sources", "lyrics", "drafting"])   # extended by Tasks 3-5
def test_guide_is_clean(guide):
    assert lint_guide(PLUGIN_ROOT/f"guides/{guide}.md") == []

def test_lyrics_guide_has_core_sections():
    t = (PLUGIN_ROOT/"guides/lyrics.md").read_text()
    for h in ["## Rhyme", "## Stability", "## Title and verse development", "## Point of view",
              "## Metaphor", "## Object writing", "## Lenses", "## Misattributions"]:
        assert h in t

def test_drafting_guide_covers_spec_section_8():
    t = (PLUGIN_ROOT/"guides/drafting.md").read_text().lower()
    for k in ["writer's material", "particular", "self-audit", "cliché pairs", "irregularity",
              "song's voice", "any size", "never"]:
        assert k in t, k
```

- [ ] **Step 2: Run to verify failure** — `uv run --frozen pytest tests/plugin/test_guides.py -v` → FAIL.
- [ ] **Step 3: Implement `lint_guide` and write the three guides.**
- [ ] **Step 4: Run to verify pass**, plus the full songtools suite.
- [ ] **Step 5: Commit** — `git commit -m "feat(plugin): guide lint, lyrics, drafting and sources guides"`

---

### Task 3: Structure and melody guides

**Files:**
- Create: `songwriter-plugin/guides/{structure,melody}.md`
- Modify: `songwriter-plugin/songtools/tests/plugin/test_guides.py` (add both to the clean-guide list, plus a section test)

**Interfaces:**
- Consumes: `lint_guide` and `sources.md` from Task 2. Add a `sources.md` entry for any author new to these guides.

Content:
- `structure.md`: the form menu (spec section 6 structure row), each form with its section jobs and a source. It also covers:
  - Summach's prechorus data, Nobile's initiation/buildup/arrival and telos/anti-telos, Stroud's postchorus types, de Clercq's blends;
  - Pattison's first-line contrast;
  - verified asymmetry techniques;
  - hook and title placement, with commercial timing marked as a market heuristic.
- `melody.md`: Perricone's singability checks and bridge levers; Pattison's front- and back-heavy phrases, roadmaps and stress rules; Hayes and Smith limits; key choice by tessitura.

- [ ] **Step 1: Write the failing test**

```python
def test_structure_and_melody_sections():
    s = (PLUGIN_ROOT/"guides/structure.md").read_text(); m = (PLUGIN_ROOT/"guides/melody.md").read_text()
    for h in ["## Form menu", "## Section jobs", "## Contrast", "## Hooks and titles", "## Asymmetry", "## Market heuristics"]:
        assert h in s
    for h in ["## Singability", "## Phrasing", "## Prosody", "## Key and range", "## Limits"]:
        assert h in m
    assert "70%" in m          # the Hayes limit is stated
```

- [ ] **Step 2: Run to verify failure.** **Step 3: Write the guides.** **Step 4: Run to verify pass (lint clean).** **Step 5: Commit** — `git commit -m "feat(plugin): structure and melody guides"`

---

### Task 4: Harmony, guitar and arrangement guides

**Files:**
- Create: `songwriter-plugin/guides/{harmony,guitar,arrangement}.md`
- Modify: `test_guides.py`

Content:
- `harmony.md`:
  - Everett's systems (simplified), the corpus base rates, and the chorus-cadence correction;
  - Doll's rogue dominant, Spicer's absent and soul-dominant tonics, Richards' loops with their major bias;
  - the option-menu format (each option gives why it works, how it feels, and how common it is);
  - the pitfalls list;
  - three notations shown side by side.
- `guitar.md`: V-System groups and conversions; tunings with Joni codes; capo and partial-capo conventions (matching the toolkit ruling); the fret-7 rule marked `[unverified]` as a heuristic; feel vocabulary (counts, swing types, Travis, strum subtraction); and "read, verify, describe — never write parts".
- `arrangement.md`: Owsinski–Moore–Lavengood layers; Cobb's energy and groove switch; the Nashville head session; the road-map template (fields as in spec section 6); critique checks; Nashville number chart symbols with the "not standardized" note.

- [ ] **Step 1: Write the failing test**

```python
def test_music_guides_sections():
    h = (PLUGIN_ROOT/"guides/harmony.md").read_text()
    g = (PLUGIN_ROOT/"guides/guitar.md").read_text()
    a = (PLUGIN_ROOT/"guides/arrangement.md").read_text()
    for x in ["## Tonal systems", "## Base rates", "## Option menu", "## Pitfalls"]: assert x in h
    assert "32%" in h and "18.5%" in h
    for x in ["## Voicings", "## Tunings", "## Capo", "## Feel"]: assert x in g
    for x in ["## Layers", "## Energy", "## Road map", "## Checks"]: assert x in a
    assert "left to the players" in a.lower()
```

- [ ] **Step 2–4:** fail, write, pass (lint clean). **Step 5: Commit** — `git commit -m "feat(plugin): harmony, guitar and arrangement guides"`

---

### Task 5: Critique and process guides

**Files:**
- Create: `songwriter-plugin/guides/{critique,process}.md`
- Modify: `test_guides.py`

Content:
- `critique.md`:
  - Lerman's Critical Response Process (4 steps, with opinions allowed in direct answer to the writer's own questions);
  - Pattison's workshop practice (start from strengths, offer 2–4 variants);
  - Dodson's four rewrite checks; Stolpe's listener questions;
  - the note format: location → observation → mechanism → listener effect → basis → options;
  - craft notes versus taste notes;
  - the final check's 10 steps exactly as in spec section 7;
  - the status choices.
- `process.md`: the eight entry points and how each reorders the stages; the receive-then-edit stance (Zollo interviews, verified); Tweedy's verified habits; King's walk-away; the bank; versions and the cut pool; a split sheet with a non-performing lyricist allowed.

- [ ] **Step 1: Write the failing test**

```python
def test_critique_and_process():
    c = (PLUGIN_ROOT/"guides/critique.md").read_text(); p = (PLUGIN_ROOT/"guides/process.md").read_text()
    for x in ["## Critical Response Process", "## Note format", "## Craft versus taste", "## Final check"]: assert x in c
    assert c.count("\n| ") >= 11          # 10-step final-check table + header
    for x in ["## Entry points", "## Receive, then edit", "## Getting unstuck", "## Versions and cuts"]: assert x in p
    for e in ["riff", "guitar song", "lyric", "progression", "title", "brief", "bank", "co-write"]: assert e in p.lower()
```

- [ ] **Step 2–4:** fail, write, pass. **Step 5: Commit** — `git commit -m "feat(plugin): critique and process guides"`

---

### Skill tasks (6–11): the shared method

Every skill task follows the writing-skills RED → GREEN → REFACTOR loop:

1. **Scenarios first.** Write `songwriter-plugin/skill-tests/<skill>.md` with the task's scenarios. Each scenario has:
   - a setup: a copy of `songtools/tests/fixtures/sample_song` into a scratch `songs/porch-light-left-on/`, edited as the scenario says;
   - the writer's message;
   - pass criteria, written as checkable statements.
2. **RED (baseline).** Dispatch a test-subject subagent (model: sonnet) for each scenario. Give it the scenario setup, the writer's message, and this line: "You are helping a songwriter in this folder. The toolkit is available as `uv run --frozen --project /home/user/flynnduel/songwriter-plugin/songtools songtools`." Do not give it the skill. Record in the file which pass criteria it broke, and how.
3. **GREEN.** Write `skills/<skill>/SKILL.md`. It contains frontmatter, "Read `${CLAUDE_PLUGIN_ROOT}/guides/rulebook.md` first", the guides to load, the stage steps, the exact toolkit calls with `INVOKE`, and a short "Red flags" list taken from the baseline failures. Re-run each scenario with a test subject that is given the SKILL.md text, with `${CLAUDE_PLUGIN_ROOT}` replaced by `/home/user/flynnduel/songwriter-plugin` and `${CLAUDE_PLUGIN_DATA}` by a scratch path. Every pass criterion must hold. Record the result.
4. **REFACTOR.** For any criterion that still fails, or a new rationalization the subject used, add an explicit counter to the skill and re-run that scenario.
5. **Professional benchmarks (where the task lists a `BM` scenario).** These come from Pat Pattison's published worked critiques, which the research read in full. Notes are in `research_notes/…/03_melody_prosody.md`, `07_critique_revision.md` and `02_structure_hooks.md`. Use only the short fragments recorded in the notes (each quote 14 words or fewer). Where the notes describe a structure but don't quote the lyric, write an **original** lyric with that same structure. Never reproduce a published lyric at length. The test subject gets the input with no hint of what to look for. It passes only if it finds the same problem Pattison found, for the same reason (the same mechanism), and offers options rather than one fix. The baseline (RED) and with-skill (GREEN) results are recorded side by side.
6. Remove the skill from the structure test's xfail set. Run `uv run --frozen pytest tests/plugin -v` and the full songtools suite; both must pass.
7. Commit the skill file and its scenario file together.

---

### Task 6: `/lyrics` skill

**Files:** Create `skills/lyrics/SKILL.md`, `skill-tests/lyrics.md`; modify `test_plugin_structure.py` (xfail set).

**Interfaces:**
- Consumes:
  - the `rulebook`, `lyrics`, `drafting` and `toolkit` guides;
  - `songtools` `prosody`, `rhyme`, `stability`, `pov`, `cliche` (`--strict` on the plugin's own drafts) and `drafts snapshot` / `drafts cut`.
- Produces:
  - the kept-line write format;
  - the mode switch (`mode:` in `## Core`);
  - snapshot-before-change, which later skills rely on.

Scenarios (each one's pass criteria in brackets):
- **L1 — Drafting mode is quiet.** `mode: drafting`. The writer asks for a second verse built on the porch-light image. [The draft uses words or images from song.md, lyrics.md or object-writing. The plugin's own draft is checked with `cliche --strict` before it's shown. No critique of the writer's lines is given unasked.]
- **L2 — Kept line.** The writer says "keep it" about a flagged line. [song.md gains a `## Kept lines` entry that `songtools.songfile.parse_song_md` parses, checked by running it. The same flag is not raised again in that session.]
- **L3 — Editing mode with an unknown word.** A line contains "Señor". [The skill runs `prosody` and `rhyme` rather than guessing. It reports "estimated" or "undetermined" and offers to add a pronunciation. It doesn't state a syllable count as fact.]
- **L4 — Writer revises a line; the plugin thinks it's weaker.** [The plugin flags it with a mechanism and a basis, offers 2–4 options, does not overwrite the line, and takes a snapshot before any change it does make.]
- **L5 — Lyrics pasted into chat, no folder.** [The plugin offers to create `songs/<title>/` with lyrics.md and still gives help in the same reply.]
- **L6 — Stock lines.** The writer asks "does this sound like AI?" about a line with "neon" and "we rise above". [The plugin answers by naming stock imagery as a craft issue and never says or implies the line is AI-written.]
- **L7 (BM) — Pattison's "Unconditionally" setting.** Editing mode. Give the fragments and their beat placements as recorded in the melody/prosody notes. [Finds the function words ("the", "did") sitting on downbeats, the secondary stresses of "insecurities" on strong beats, and "-ly" on a downbeat. Explains each as stress fighting the beat, using `prosody` output as the basis. Offers settings or rewordings. Doesn't rewrite the whole line unasked.]
- **L8 — Structure check also enforced by tests.** Extend `check_skill_text` in `test_plugin_structure.py`: a SKILL.md body over 500 lines fails, and a description containing workflow verbs that summarize the process ("then", "runs", "dispatches", "step") fails. Add negative tests for both.

- [ ] **Step 1:** Write the scenarios. **Step 2:** Run the baselines (RED) and record them. **Step 3:** Write the SKILL.md and run with it (GREEN). **Step 4:** Refactor until every criterion passes. **Step 5:** Update the xfail set and run both suites. **Step 6:** Commit — `git commit -m "feat(plugin): /lyrics skill with pressure tests"`

---

### Task 7: `/critique` and `/finalcheck` skills

**Files:** Create `skills/critique/SKILL.md`, `skills/finalcheck/SKILL.md`, `skill-tests/critique.md`, `skill-tests/finalcheck.md`; modify the xfail set.

**Interfaces:** Consumes the `critique`, `rulebook` and `toolkit` guides and every analysis subcommand, plus `drafts diff --song` for kept lines. Neither skill changes song files, except that `/finalcheck` writes `status:` when the writer chooses.

Scenarios:
- **C1 — Full critique.** [The order is: meaning and 1–3 strengths, then the writer's own questions, then neutral questions, then about 3 ranked notes with song-level notes first. Each note has location, observation, mechanism, effect, basis and options. No file is changed.]
- **C2 — Unsolicited taste.** [The plugin asks permission before giving a taste note. Craft notes need no permission.]
- **C3 — Davis claim.** [Anything from Davis is labelled "as reported", never as verified.]
- **C4 — Kept lines.** [Previously kept lines are listed in their own short group and asked about once.]
- **F1 — Final check.** [All 10 steps, big to small, with a basis for each. Kept lines are revisited. The irritant scan is asked. The writer chooses done, done for now, or keep working. The plugin never declares the song finished, and `status:` is written only after the writer's choice.]
- **F2 — Missing music.md.** [Steps 5 and 7 are reported as "not run: no music.md". There is no invented chord check.]
- **C5 (BM) — Pattison's Bellbird Hill master class.** Use an original four-line verse with the same features recorded in the critique notes: an aabb scheme, and the strongest image buried in line 3. [Notes that aabb stops the motion at each couplet. Suggests bringing the image forward. Offers the same verse in 2–4 alternative schemes (for example abab, xxaa, abba) side by side for the writer to choose by feel. Never imposes one rewrite.]

- [ ] Steps 1–6 as in the shared method. Commit — `git commit -m "feat(plugin): /critique and /finalcheck skills with pressure tests"`

---

### Task 8: `/chords` and `/melody` skills

**Files:** Create `skills/chords/SKILL.md`, `skills/melody/SKILL.md`, `skill-tests/chords.md`, `skill-tests/melody.md`; modify the xfail set.

**Interfaces:** Consumes the `harmony`, `guitar`, `melody`, `rulebook` and `toolkit` guides and `songtools` `harmony`, `chord`, `guitar` and `key`. `/chords` writes `music.md` progressions only when the writer picks one.

Scenarios:
- **H1 — "Write me a bass line" / "give me the tab".** [The plugin declines to write parts. It offers role guidance and checks the writer's own ideas instead.]
- **H2 — Options for the chorus.** [2–4 options, each with why it works, how it feels and the corpus base rate. Three notations. No single "correct" answer. V–I is not presented as the only proper cadence.]
- **H3 — Verify the writer's voicing `x32000` named C.** [The plugin runs `guitar verify` and reports the extra B and the Cmaj7 alternative.]
- **H4 — Key for voice G2–D4.** [The plugin runs `key` per section and gives capo pairings. Sharps and flats are spelled for the key.]
- **M1 — "Write the melody for the chorus".** [The plugin declines to write notes. It coaches with Perricone's checks, phrase placement and contour questions.]
- **M2 — Genre neutrality.** The writer gives no genre. [No genre is assumed. Examples come from more than one style.]

- [ ] Steps 1–6. Commit — `git commit -m "feat(plugin): /chords and /melody skills with pressure tests"`

---

### Task 9: `/idea`, `/structure` and `/arrange` skills

**Files:** Create `skills/{idea,structure,arrange}/SKILL.md`, `skill-tests/{idea,structure,arrange}.md`; modify the xfail set.

**Interfaces:** Consumes the `process`, `lyrics` (POV), `structure`, `arrangement` and `rulebook` guides and `songtools` `stability` and `pov`. `/idea` writes the idea fields to song.md; `/structure` writes `form:`; `/arrange` writes `arrangement.md`.

Scenarios:
- **I1 — Vague idea "a song about loss".** [Questions continue one at a time until the point, singer and listener, moment, image and the unresolved element are concrete. The POV check offers all four POVs. Results are saved to song.md.]
- **S1 — Form choice.** [2–3 forms suited to the idea, each with its section jobs and source. Title spotlight. A stability plan, checked with `stability`. One meaningful asymmetry is suggested.]
- **A1 — "Write the drum part".** [The plugin declines. The road map has every template field, including "left to the players". There is no notation.]
- **A2 — Too many parts in the chorus.** [The plugin flags more than 4 elements with its basis and offers alternatives.]
- **A3 — `/arrange` with no structure yet.** [The plugin works from the sections in lyrics.md and says form isn't set. It doesn't invent sections.]
- **S2 (BM) — Pattison's "Southern Comfort" problem.** An original song whose verses and chorus share the same meter and rhyme pattern (Common Meter throughout), with a bridge arriving late. [Finds that the chorus's first line doesn't contrast with the verse, with `stability` and the contrast check as basis. Explains that listeners drift before the bridge. Offers ways to change the chorus form.]
- **S3 (BM) — Pattison's "Valentine" bridge.** An original song with a deliberately interrupted three-line bridge that snaps back to verse 1 to show the character stuck. [Recognises the asymmetry as serving the meaning and does not "fix" it. If the bridge is flagged as unstable, the meaning is named as the reason to keep it.]

- [ ] Steps 1–6. Commit — `git commit -m "feat(plugin): /idea, /structure and /arrange skills with pressure tests"`

---

### Task 10: `/newsong`, `/bank` and `/chart` skills

**Files:** Create `skills/{newsong,bank,chart}/SKILL.md`, `skill-tests/{newsong,bank,chart}.md`; modify the xfail set.

**Interfaces:**
- `/newsong` creates `songs/<slug>/` with `song.md` (`## Core` including `entry`, `mode: drafting`, `lenses: pattison`, `status: working`), routes to the next stage skill by name, and resumes from song.md.
- `/bank` appends `- YYYY-MM-DD [tag] text` to `songs/_bank/ideas.md` and can promote an idea into `/newsong`.
- `/chart` runs `chart --concert --pdf` and `midi`, then checks that the chart matches lyrics.md.

Scenarios:
- **N1 — "I've got a riff in DADGAD".** [The entry is set to riff. Next steps are reordered (music first). The song folder is created with the correct core keys.]
- **N2 — Resume.** An existing song with status working and lyrics but no music. [The plugin finds where the song stands from the files and proposes the next missing stage. Nothing is re-asked.]
- **B1 — Bank a title.** [One-line entry in `songs/_bank/ideas.md` in the exact format. No folder is created.]
- **K1 — Chart.** [Runs the toolkit. Reports the written paths. States the capo convention (shape chords plus a concert copy for the band). On a toolkit error, relays the message, never a fabricated chart.]

- [ ] Steps 1–6. Commit — `git commit -m "feat(plugin): /newsong, /bank and /chart skills with pressure tests"`

---

### Task 11: End-to-end run, plugin README and release check

**Files:** Create `songwriter-plugin/README.md`, `skill-tests/end-to-end.md`; modify `test_plugin_structure.py` (remove the xfail set entirely).

- [ ] **Step 1: Write the failing test** — with the xfail removed, `test_skill_frontmatter_and_invocation` must pass for all 11 skills. Add:

```python
def test_readme_lists_every_command():
    t = (PLUGIN_ROOT/"README.md").read_text()
    for s in SKILLS: assert f"/{s}" in t
    assert "install" in t.lower() and "uv" in t

def test_every_guide_is_used_by_some_skill():
    bodies = " ".join((PLUGIN_ROOT/f"skills/{s}/SKILL.md").read_text() for s in SKILLS)
    for g in (PLUGIN_ROOT/"guides").glob("*.md"):
        assert f"guides/{g.name}" in bodies, g.name
```

- [ ] **Step 2: Run to verify failure** (README is missing).
- [ ] **Step 3: End-to-end pressure run.** One test subject is given all eleven SKILL.md texts (variables substituted) and a fresh scratch project. It takes a new original song from `/newsong` through `/idea`, `/structure`, `/lyrics`, `/chords`, `/arrange`, `/chart`, `/critique` and `/finalcheck`, with the controller-scripted writer replies recorded in `skill-tests/end-to-end.md`. Pass criteria:
  - every file in spec section 4 exists and parses with `songtools`;
  - `out/` holds `chart.cho`, `chart-concert.cho`, `chart.pdf`, `chart-concert.pdf` and `guide.mid`;
  - no rule in the rulebook is broken anywhere in the transcript;
  - the writer sets the status.
- [ ] **Step 4: Write `README.md`:** what the plugin does and doesn't do; installing (add the marketplace, install `songwriter`, `uv` is required); the 11 commands with one example each; the song-folder layout; the lenses and modes; the sources and their tags (link `guides/sources.md`); the open items from spec section 12.
- [ ] **Step 5: Run both suites** — `uv run --frozen pytest -q` (songtools plus plugin). Expected: all pass.
- [ ] **Step 6: Writer acceptance review (the human gate).** The controller stops here and asks the writer (the user) to install the plugin from the branch and run it on one of their own songs or drafts: at least `/newsong` or `/lyrics`, `/critique` and `/chords`. The writer judges each response by whether they would take that advice from a professional co-writer. Every response the writer marks as generic, wrong or unhelpful is logged in `skill-tests/acceptance.md` (what was asked, what came back, what the writer said) and fixed in the skill that produced it, with a new scenario reproducing it (RED then GREEN). The plan is complete only when the writer accepts.
- [ ] **Step 7: Commit and push** — `git commit -m "feat(plugin): README and end-to-end run"`, then `git push -u origin claude/dazzling-feynman-furauz`.
