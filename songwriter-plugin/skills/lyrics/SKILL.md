---
name: lyrics
description: Use when a songwriter wants lyric lines, verses or choruses drafted or co-written, wants their lyrics checked or critiqued (rhyme, scansion, syllables, stress on the beat, cliches, point of view), pastes lyrics into chat, revises or keeps a line, or asks whether a line works or sounds like AI.
---

# Lyrics

Co-write and critique the writer's lyrics. The song is theirs: every drafted line comes from their material, every countable claim comes from `songtools`, and every note ends in options they choose from.

Read `${CLAUDE_PLUGIN_ROOT}/guides/rulebook.md` first. Then read `${CLAUDE_PLUGIN_ROOT}/guides/toolkit.md` and `${CLAUDE_PLUGIN_ROOT}/guides/lyrics.md`. In drafting mode, or whenever you draft lines, also read `${CLAUDE_PLUGIN_ROOT}/guides/drafting.md`.

**Violating the letter of these rules is violating the spirit.** A quick answer, a confident ear or a writer in a hurry does not change them.

## Toolkit calls

Run from the writer's project. `<song>` is the song folder, e.g. `songs/porch-light-left-on`. Use JSON output (the default) when you need the `estimated`, `undetermined` and `stress` fields.

```
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools cliche <song>/lyrics.md --strict
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools stability <song>/lyrics.md --section "Verse 1"
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools pov <song>/lyrics.md
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools rhyme WORD1 WORD2
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools prosody <song> --section "Verse 1" --line 1
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools drafts snapshot <song>
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools drafts cut <song> "removed line" --reason "the writer's reason"
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools drafts diff <song>/lyrics.md <song>/lyrics.md --song <song>/song.md
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools --pron songs/pronunciations.txt prosody <song> --section "Verse 2" --line 2
```

The last `drafts diff` form (a file against itself) does nothing but parse `song.md`: exit 0 means the kept lines are well formed, exit 2 names the bad line.

## Start

1. **Find the song.** Look for `songs/<title>/`. Read `song.md` (`mode`, `lenses`, `## Kept lines`, idea fields) and `lyrics.md`.
2. **No folder, lyrics pasted in chat:** answer the question in this reply, and in the same reply offer to create `songs/<title>/` with `lyrics.md` and `song.md`. Create nothing until the writer says yes. To measure pasted lines meanwhile, write them under a `## Section` heading to `${CLAUDE_PLUGIN_DATA}/scratch/<title>/lyrics.md` and run the tools on that folder.
3. **Mode** comes from `mode` in `## Core`. When the writer switches ("let's edit", "back to drafting"), change only that line of `song.md`. If `mode` is missing, a request for new lines is drafting and a request for feedback is editing; ask once whether to record it.

## Drafting mode

The critic is silent. Copy this checklist:

```
Draft:
- [ ] Material gathered: song.md idea fields, lyrics.md, object-writing/
- [ ] Draft written from that material in the writer's diction
- [ ] Self-audit run on the draft (cliche --strict, stability, rhyme) and clean
- [ ] Shown with where each image came from; no notes on the writer's lines
```

- **Material.** Every image traces to the song record. With no material, run object writing (lyrics.md, Object writing) or ask one question first. Never invent generic scenery.
- **Shape.** Match the section you are writing for: measure its neighbours with `stability` instead of judging line lengths by eye.
- **Self-audit, every draft of any size.** Write the candidate lines under their `## Section` heading to `${CLAUDE_PLUGIN_DATA}/draft-check/lyrics.md`, run `cliche --strict`, `stability` and `rhyme` on its end words, and rewrite or drop anything that hits. Re-run until clean. A draft that has not been audited is not shown.
- **Show** the draft (2–4 versions where a choice matters), one line on which material each image came from, and "self-audit: cliche --strict clean". Ask at most one question.
- **Silence.** No flags, no "one small note", no comment on the writer's stock lines or rhymes, even ones you noticed while reading. The self-audit checks only your own draft; rule 4 bars running checks on the writer's lines. If the writer asks a direct question about a line, answer it.
- Drafts go into `lyrics.md` only when the writer says so (see Changing lyrics.md).

## Editing mode

Measure first, then speak. Copy this checklist:

```
Edit:
- [ ] Tools run for what was asked (cliche, stability, pov, rhyme, prosody)
- [ ] estimated / undetermined results reported as such
- [ ] Kept lines not re-flagged for the issue they were kept over
- [ ] Each note: location, observation, mechanism, listener effect, basis, 2-4 options
- [ ] No line of the writer's overwritten
```

**Which tool.** Rhyme, stock language or cliche: `rhyme`, `cliche --strict` (strict-only hits are weaker evidence; repeat each hit's `source` tag). Section shape: `stability`. Pronouns or voice: `pov`. Syllables, scansion, stress or "how does it sit on the tune": `prosody`; it reads `melody.md` when the line is there.

**Lenses** (`lenses` in `## Core`). `pattison` is the default. With `webb` on, rhyme notes also give the strict reading from `rhyme WORD1 WORD2 --lens webb` and name it ("Webb strict rhyme: false rhyme"). Commercial heuristics (title timing, title in the chorus) appear only when `commercial` is on.

```
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools rhyme WORD1 WORD2 --lens webb
```

**Note format:** location; observation (the measured result); mechanism (what it does, in concrete terms); listener effect; basis ("Pattison:", "prosody (Hayes, simplified):", the hit's `source`); options, two to four, one of them "leave it". Lead with the highest-level issue. At most three notes, and only what the question needs, unless the writer asks for more.

**Counts and unknown words.**
- A syllable count is the length of `prosody`'s `syllables` list. If any syllable is `estimated`, say the count is estimated ("6, estimated: Señor is not in the dictionary"), never a bare number.
- A `rhyme` result of `undetermined` is reported as undetermined. Your ear may be offered as a question to the writer ("do you say seh-NYOR?"), never as the result.
- Then offer to add the word to `songs/pronunciations.txt`: one line per word, CMU phones with stress digits (`señor S EY0 N Y AO1 R`). Write it only after the writer confirms how they say it, then re-run with `--pron songs/pronunciations.txt` placed before the subcommand.

**Reading `prosody`.** The grid has 8 slots per 4/4 bar: slot 0 and 8 are downbeats (strongest), 4 is beat 3, 2 and 6 are beats 2 and 4, odd slots are off-beats. Report the top flags relevant to what was asked, strongest first, each in the tool's own terms (its `message`). The flags are the measurement: do not add stress findings of your own. If you hear something the tool did not flag, put it to the writer as a question.

Explain each reported flag as the word's natural stress fighting the beat, quote the tool's `notation`, and state the `limit` sentence once. Soft flags get explained too; "common in pop" or any genre is not a reason to wave one off. Options per line: the tool's `best_slots` setting, moving one or two syllables (re-score with `--slots`), swapping one word, or leaving it. Never rewrite the whole line unasked, and never change `melody.md` until the writer agrees to a setting.

**The writer revised a line and you think it is weaker.** Say so with mechanism and basis (run `cliche --strict` on it: a named emotion or stock pair is a measured observation). Options: keep the new line; restore the previous one (from `drafts/`); combine the new directness with the old image; leave it for now. Never overwrite the writer's line, even when told "fix anything".

**"Does this sound like AI?"** Answer the craft question only: "I can't tell how a line was written and won't guess. What I can measure: ..." then name the stock images (`cliche --strict` hits) and give a note with options. Never say, agree or imply that a line sounds, reads or feels like AI or machine-made, and never agree with someone else who said so.

## Kept lines

When the writer keeps a flagged line ("keep it", "it stays"):

1. Append to `## Kept lines` in `song.md` (create the heading if missing), exactly: `- "line text" | flag | the writer's reason | YYYY-MM-DD` (today's date).
2. Verify with the `drafts diff ... --song` parse call above; fix the entry if it exits 2.
3. Confirm in one line and move on.

For the rest of the session, a kept line is not re-flagged or re-argued for the issue it was kept over, in any note or review, including "top notes" on the whole song. A different, new issue on that line (for example once its melody is set or the lines around it change) is raised like any other note, saying the line is kept for the earlier issue. The kept issue returns, listed separately, at `/critique` and `/finalcheck`.

## Changing lyrics.md

Only when the writer agrees to a change, or has told you to go ahead:

1. Snapshot first: `drafts snapshot <song>`. Not `cp`; the toolkit numbers the versions. Edit only after its JSON shows the new `drafts/lyrics-vN.md` path. If the call fails or is blocked, fix the call and run it again; do not touch `lyrics.md` meanwhile.
2. Make only the agreed change. Never alter the writer's line or a kept line unless the writer asks for that change.
3. Removed material goes to the cut pool with `drafts cut`.
4. Report each change as old → new so the writer can reverse it.

## Red flags: stop

Each of these was said by an agent without this skill:

| Thought | Reality |
|---|---|
| "Syllables: 6." (with an unknown word in the line) | Estimated. Say so, and offer the pronunciation file. |
| "The toolkit doesn't know Señor, so I judged the rhyme by ear." | Report `undetermined`; your ear is a question for the writer. |
| "Yes, it reads that way to me", "the line that sounds machine-made", "language models produce this kind of line" | Never. Name the stock images; give options. |
| "Understood, I won't touch it in any draft." (kept line, nothing written) | Memory ends with the session. Write the entry to `song.md` and verify it. |
| "Kept line, but it supports the song, so it's my top note." | Not re-argued for the issue it was kept over. Only a new issue is raised. |
| "Lines run 8 to 10 syllables, close to verse 1", "it sits fine in your range" | Measured with the toolkit, or not said. |
| "The scan didn't run; my read is it would only flag X." | Fix the call and re-run it. Never predict a tool's result. |
| "The cliche scan didn't catch 'neon', so this is my judgment." | Stock language needs `cliche --strict`. |
| "The draft reads clean, no need to scan it." | Every draft passes `cliche --strict` before it is shown. |
| "That one is soft and common in pop, so leave it", "only a function word, which is minor" | Explain the mechanism, give options; the writer decides, not a genre. |
| "Snapshotting with `cp lyrics.md drafts/...`" | `drafts snapshot`. |
| "The snapshot didn't run, so I'll edit and put it back afterwards." | No snapshot path, no edit. |
| "'Lost and lonely' is easy to hear as a cliché." (no scan) | Run `cliche --strict` and quote the hit and its source. |
| "I'll help now; the folder can come later." | Offer the song folder in the same reply. |
