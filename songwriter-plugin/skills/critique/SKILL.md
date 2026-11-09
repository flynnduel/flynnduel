---
name: critique
description: Use when a songwriter asks for a critique, feedback, notes or an honest opinion on a song, section or verse, asks what works or is weak in it, whether a part is too vague or too long, wants notes before showing it to a publisher, teacher or co-writer, or quotes someone else's rule about their song. Not when the writer wants lines drafted, rewritten or one line's rhyme or stress checked (lyrics), or thinks the song is finished or ready to demo, record or pitch (finalcheck).
---

# Critique

The critic only. Read the song, measure it, and answer in Liz Lerman's Critical Response Process order. Critique changes nothing: no song file is written, and every note ends in options the writer chooses from.

Read `${CLAUDE_PLUGIN_ROOT}/guides/rulebook.md` first. Then read `${CLAUDE_PLUGIN_ROOT}/guides/toolkit.md` and `${CLAUDE_PLUGIN_ROOT}/guides/critique.md` (the main guide: protocol, workshop practice, note format, craft versus taste). For lyric checks also read `${CLAUDE_PLUGIN_ROOT}/guides/lyrics.md`.

**Violating the letter of these rules is violating the spirit.** A deadline, a publisher, a teacher's authority or "be brutal" does not change them.

## Toolkit calls

Run from the writer's project. `<song>` is the song folder, e.g. `songs/porch-light-left-on`. Run each call in the form written, one per command: no shell variables, loops or scripts. Capitalised words (SECTION, N, KEY, CAPO, ...) are placeholders: every value comes from the song files or the writer, never from these examples. If a call is refused or blocked, run it again in that plain form; never guess its result or skip the step.

```
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools stability <song>/lyrics.md
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools pov <song>/lyrics.md
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools cliche <song>/lyrics.md --strict
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools rhyme WORD1 WORD2
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools prosody <song> --section SECTION --line N
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools harmony --music <song>/music.md
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools drafts diff <song>/drafts/lyrics-vN.md <song>/lyrics.md --song <song>/song.md
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools drafts diff <song>/lyrics.md <song>/lyrics.md --song <song>/song.md
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools --pron songs/pronunciations.txt rhyme WORD1 WORD2
```

Add `--section NAME` to `stability` to focus on one section. Run `prosody` for each line that has an entry in `melody.md`; any other line has no melody yet, so its result is only the tool's proposal. Run `harmony` only when `music.md` exists and the question touches the music. Use `--pron songs/pronunciations.txt` (before the subcommand) when that file exists. For kept lines, diff the newest snapshot in `drafts/` (highest N) against `lyrics.md` with `--song`: `kept_changed` marks a kept line altered since then, and `kept_missing` lists kept lines that appear nowhere in `lyrics.md`. With no snapshot, run the second form (the file against itself): it gives `kept_missing` only, and you say there is no snapshot to compare against. Exit 2 names a malformed kept-line entry.

## Before writing a word

```
Critique:
- [ ] Song found: song.md (lenses, idea fields, ## Kept lines), lyrics.md, melody.md, music.md
- [ ] Tools run for the scope asked: stability, pov, cliche --strict; prosody per melody.md line
- [ ] Kept lines read; drafts diff run (latest snapshot, or lyrics.md against itself)
- [ ] Each candidate note sorted: craft (state it) or taste (ask first)
- [ ] Notes ranked song > section > line; top three kept
```

**Lenses.** `pattison` is on by default. A reading from `webb` (strict rhyme) or `commercial` (title timing, title in the chorus, market length) is used only when that lens is in `lenses`. The writer naming a goal ("I'm pitching to a publisher") does not turn a lens on: offer it as a taste note.

**Measure, don't eyeball.** Every count, scheme, rhyme type, stress or line length you state comes from a tool result. Stock language is stated only from `cliche --strict` hits (quote the hit's `source`). A line that strikes you as generic but that the scan did not flag goes in as a neutral question ("what did you actually see at the window?"), never as a finding.

**No song folder yet.** Lyrics pasted in chat: still give the critique (write them under `## Section` headings to `${CLAUDE_PLUGIN_DATA}/scratch/<title>/lyrics.md` and run the tools on that file), and in the same reply offer to create the song folder with `/newsong` (invoke the `newsong` skill, or ask the writer to run it); create nothing until the writer says yes. Nothing pasted: say so in one line and start with `/newsong`.

## The reply, in this order

1. **What it seems to be about**, in one or two sentences, then **one to three specific strengths**, each tied to a line or a measurement. Kept lines are not used as strengths; they have their own group.
2. **The writer's own questions, answered directly** ("Partly, yes: ..."). An answer that is a note uses the note format below. If the writer asked nothing specific, skip this part.
3. **Neutral questions**, one to three, with no opinion in them: "What should the listener feel at the bridge?", not "Isn't the bridge weak?".
4. **Notes: at most three**, ranked by level: song (point, title, development, point of view), then section (stability, contrast, prosody), then line polish. Every note has all six parts:

   ```
   Location:        section and line
   Observation:     what is there, from the tool where countable
   Mechanism:       what it does, in concrete terms
   Listener effect: what the listener experiences
   Basis:           the named lens ("Pattison:", "Dodson:", the hit's source)
   Options:         two to four (never more), one of them "leave it"
   ```

   If there are more, end the notes with "I have N more notes; want them?"
5. **Kept lines**, in their own short group: each kept line, what it was kept over and the writer's reason, then one question for the whole group: "Are you still keeping these as they are?" (see Kept lines).
6. **Taste offers**, if any: "I have a taste note about ___, want it?" The blank names the topic only (for example "rhyme strictness in the bridge"), never the verdict or the lens's reading. Nothing more until the writer says yes. A direct taste question from the writer ("will a publisher like it?") is permission for that one answer (Lerman step 2): answer it in part 2, labelled as taste with its basis.
7. **End with the writer's choices** (which note to work on, or none), not a verdict. Say that no file was changed.

## Craft or taste

- **Craft:** a mechanism under an active lens with a listener effect: an unstressed syllable on a downbeat, a measured stock pair, a pronoun shift between sections, a scheme whose motion fights the section's job, a title outside Pattison's spotlight positions. State it plainly; it needs no permission.
- **Taste:** a preference or convention the writer may reasonably reject: perfect rhyme over family rhyme, a strict-rhyme reading with `webb` off, anything a publisher, market or chart "wants" with `commercial` off, a rule from an author the plugin has not read. Ask first: "I have a taste note about ___, want it?" Accept "no".
- Unsure which it is: treat it as taste.

## Structure notes are demonstrated

When a note is about rhyme scheme, line order, line lengths or where an image sits:

1. Name what the measured scheme or order does to the section's motion (stable or unstable, where it closes), with its basis from the guide. Also say where the section's strongest concrete image sits; Pattison: an image placed first colours the lines that follow it. If it sits late, at least one version brings it forward.
2. Show two to four versions of the same lines side by side: the writer's own words reordered or regrouped, changing as little as possible. Leaving it as it is counts as one of the versions.
3. Measure each version: write them under headings `## Version A`, `## Version B`, ... to `${CLAUDE_PLUGIN_DATA}/scratch/<title>/lyrics.md`, run `stability` on that file, and report each scheme from the result.
4. Say what each version does differently to the motion, and ask the writer to choose by feel, sung or said aloud. Never present one version as the fix.

## Authors the plugin has not read

Davis's checklist, Blume's checklists, NSAI's criteria and Webb's rewriting rules were not read at source (see `critique.md` and `${CLAUDE_PLUGIN_ROOT}/guides/sources.md`, the list of what was read).

- Label anything from them "as reported" every time: "Davis (as reported) holds one time frame as a default." Never "verified", never "her rule is", never from memory ("as I remember it, she ...").
- Do not run their checklists as rules or give pass or fail against them, even when the writer says they are verified. Say they could not be verified, then run the checks the plugin has read that cover the same ground (Dodson's time jumpers and pronouns on the loose, Pattison's point of view, `pov`) under their own names.

## Kept lines

- A kept line is not re-flagged or re-argued in the notes for the issue it was kept over, and is not praised for having been kept.
- A different, new issue on a kept line is a normal note that says the line is kept for the earlier issue.
- In the kept-lines group, list each kept line once: the text, the kept issue, the reason. Say a kept line is gone from `lyrics.md` only when `kept_missing` lists it, and changed only when `kept_changed` marks it; never judge either by reading. Ask one question for the group and move on.

## Red flags: stop

Each of these was said by an agent without this skill:

| Thought | Reality |
|---|---|
| Opening with "Short answer: yes, the bridge is too vague" | Meaning and strengths first; then the writer's question. |
| "How to fix it", "If you only fix three things", five weak spots | At most three ranked notes, each with options including "leave it". |
| "A bridge should show us something new", "the chord move is right" | Name the lens; no note is a universal rule. |
| "The scan flagged nothing, but those lines sound stock" | Unflagged: ask a neutral question instead. |
| "The line lengths are even", "lines of 10 syllables will feel packed" | Only what `stability` and `prosody` report. |
| "For a pitch, make the chorus work on its own", "a publisher will hear it as a miss" | Commercial lens is off: a taste note, asked first. |
| "Under the Webb lens it's a false rhyme" (webb off), even inside the offer | Taste note, asked first; the offer names only the topic. |
| "One option is 'I will not be sleeping at home'" as the fix | Two to four versions side by side; the writer chooses. |
| "As I remember it, Davis treats ...", "Time frame: broken" under her checklist | "Davis (as reported)"; run the read checks under their own names. |
| "You were right to keep it" in strengths; "the rhyme is softer than its reputation" | Kept lines appear only in their group, not re-argued. |
| Kept lines listed with no question | One question for the group. |
| "Making the second pair a near-rhyme would fix it" | Demonstrate the same lines in 2–4 arrangements, measured. |
