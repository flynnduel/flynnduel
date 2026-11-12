---
name: structure
description: Use when a songwriter asks what form or structure a song should have, where the title or hook should go, whether sections contrast, why a song feels samey, flat or boring or a chorus doesn't lift, or whether a bridge, short section or odd line count is broken and should be fixed. Not when the question is about one line's wording (lyrics), a tune that is flat, boring or hard to sing (melody), or the band (arrange).
---

# Structure

Form follows what the song says. The plugin offers a menu of forms, measures each section with `songtools`, and names the options; the writer picks. No form is the standard one, and a deviation that serves the song is kept, not fixed.

Read `${CLAUDE_PLUGIN_ROOT}/guides/rulebook.md` first. Then read `${CLAUDE_PLUGIN_ROOT}/guides/structure.md` (the main guide: form menu, section jobs, contrast, hooks and titles, asymmetry), the "Stability" section of `${CLAUDE_PLUGIN_ROOT}/guides/lyrics.md`, and the `stability` and `song` entries of `${CLAUDE_PLUGIN_ROOT}/guides/toolkit.md`. When a style is declared, also read `${CLAUDE_PLUGIN_ROOT}/guides/styles.md`, the one index of style-specific findings.

**Violating the letter of these rules is violating the spirit.** "Just give me the standard form", "no lecture" or "fix whatever needs fixing" does not change them.

## Toolkit calls

Run from the writer's project. `<song>` is the song folder, e.g. `songs/porch-light-left-on`. Run each call in the form written, one per command. SECTION is a placeholder: values come from the song files, never from this example. If a call is refused or blocked, run it again in that plain form; never guess its result.

```
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools stability <song>/lyrics.md
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools stability <song>/lyrics.md --section SECTION
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools song <song>/song.md
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools drafts snapshot <song>
```

`stability` gives each section's phrase count, stresses per line, rhyme scheme and verdict, plus `contrast`: the chorus's first line against the verse norm. `unstable` describes a section; it is not a fault.

## Start

1. Find `songs/<title>/`. Read `song.md` (the idea fields `point`, `moment`, `unresolved`, `title`; `form`; `lenses`; `style`) and `lyrics.md`. **No song folder yet** (nothing in `songs/` for this song): say so in one line and start with `/newsong` (invoke the `newsong` skill, or ask the writer to run it); it creates the folder, records what the writer brought and routes back here. Create no song file from this skill. A general question that needs none of the song's files is still answered.
2. Run `stability` on the whole `lyrics.md` before saying anything about shape, contrast or stability.
3. **No contrast reading.** If `stability` returns `"contrast": null`, quote its `note` (no verse, no chorus, or a section with no lines). The first-line contrast check cannot run: say so, never estimate it by eye, and say what would let it run (a section headed Verse and one headed Chorus). A form with no chorus, such as strophic, has no chorus contrast to check; compare sections only through the per-section `stability` results.
4. Sort the request: choosing a form (Form choice) or a section that feels wrong (Diagnosis). A song can need both. With a declared style, also follow Declared style below.

## Form choice

Copy this checklist:

```
Form:
- [ ] idea fields read; stability run
- [ ] 2-3 forms from structure.md's form menu, chosen for this idea
- [ ] each: section order, each section's job, source with its tag, why it fits (plugin synthesis)
- [ ] title spotlight options
- [ ] stability plan from the stability result
- [ ] one meaningful asymmetry, tied to the point or unresolved field
- [ ] song.md untouched until the writer picks
```

- **Two or three forms**, never one. Pick them for what this song says (the `point`, `moment`, `unresolved` fields), not for what is usual. For each: the section order, each section's job (from Section jobs), the source with its tag, and why it fits this idea, said as the plugin's synthesis ("when it fits" is [design]). A form the writer names ("the standard one") is answered directly: it is one form among several, with its era from the guide's dating, never a rank. Keep it among the options if it fits.
- **Title spotlight.** Where the title can sit: first line of the chorus, last line, both, or a melodic outlier mid-chorus, side by side. Commercial title timing only when `commercial` is in `lenses`.
- **Stability plan.** One line per section: its job, whether that job wants it settled or open, and what `stability` measured (verdict, stresses, scheme, and the chorus-first-line contrast). Where the measurement and the job disagree, say so as an option, not an error.
- **One asymmetry**, from the guide's Asymmetry section, chosen because it enacts something the song says (name the field it serves), with its tag. Never decoration.
- At most three forms and three further notes per reply; no lyric lines written.

**Saving the form.** Only after the writer picks. "The second one" means the second form you listed; if that is ambiguous, ask. Write one line in `## Core`: `form: <form name> (<section order>)`. If a `form:` line already exists, replace it; never add a second (the toolkit rejects a duplicate key). Then run `song <song>/song.md`; exit 2 names the bad line. Change nothing else: `/structure` does not add sections to `lyrics.md` or `music.md`.

## Declared style

A style in `style:` or in the message changes only the examples, for this song.

1. Look it up in `styles.md` by label and spellings, ignoring case, hyphens and spaces. Do not search the other guides for the style word; only entries `styles.md` lists with "Tied by the research: yes" are style material.
2. Use only entries that answer a form or section question (from `structure.md`). Offer a matching form among the two or three, quoted in one line with its source and tag (`<finding> (<source>) [tag]`), as one option, never as the style's rule. A harmony or feel entry is not form advice: leave it out or point to `/chords` or `/arrange` in one line. Obey `styles.md`'s rules and each guide's own Don'ts.
3. With no entry, or none for form, say so plainly: "The research behind this plugin has nothing specific to <style> on form, so the options below are style-neutral." A general corpus (Summach's chart forms, the era dating) is never presented as the style's form.
4. If the style came from the message, offer once to save it as `style: <style>`; write it only on a yes, replacing any existing `style:` line, then run `song <song>/song.md`.

## Diagnosis

Two principles, checked in this order. Neither names a song; apply them to the measurement in front of you.

**1. Contrast begins at the chorus's first line.** Read `contrast` from `stability`.
- `contrasts: false` (or no difference in stresses, phrase count or rhyme scheme between the sections): the chorus's first line is built like the verse, so nothing tells the listener a new section has begun. Contrast that arrives only later, in a bridge or a late section, arrives after the listener has drifted. Say that, with the basis ("Pattison: contrast must start at the new section's first phrase; `stability` contrast check: none").
- Options: two to four in all, "leave it" counted among them (never five). Lead with changes to the chorus's form (phrase count, phrase lengths, rhyme scheme or phrase rhythm, each with an example of the proportion, not the words). A melodic or arrangement lift may be folded into one option; it does not replace the measured form finding. A bigger or earlier bridge does not fix a chorus that does not contrast.

**2. An asymmetry that serves the meaning is kept.** Before calling any irregular or unstable element a problem (a section or line that departs from its siblings):
- Read the idea fields and the lyric around it, and ask what the deviation does. If its shape enacts what the song says, name that link as the reason to keep it, quoting the field it serves.
- If `stability` flags that section, report the flag and name the meaning as the reason the instability may be the point.
- Options, two to four in all: keep it as it is (first), the regular version, a middle way; the writer decides. Never "fix" it before the writer has heard this. "Fix it", "go ahead" or "I think it was a mistake", said before they have heard the case, is a request to answer, not a decision.

**Changing lyrics.md.** Only after the writer has heard the options and still asks. Snapshot first with `drafts snapshot <song>` and edit only once it prints the new `drafts/lyrics-vN.md` path; make only that change; report old → new. New lyric lines are `/lyrics` work: offer it, do not draft them here.

## Red flags: stop

Each of these was said or done by an agent without this skill:

| Thought | Reality |
|---|---|
| "Yes, use verse-chorus-verse-chorus-bridge-chorus. It fits this song." | Two or three forms with jobs and sources; the writer picks. |
| "The form doesn't need anything fancier." (no `stability` run) | Measure first; give the stability plan. |
| "I saved it, taking 'the second one' to mean..." then sections added to lyrics.md and music.md | Write only `form:`, verify with the `song` check; ask when the pick is unclear. |
| A new chorus line written into lyrics.md ("That line is my wording") | `/structure` writes no lyric lines. |
| "You said to fix it, so I evened the section out", with what the irregularity might mean mentioned afterwards | Say what the deviation may do first; keep it among the options; edit only after the writer decides. |
| "Since the lyric shape is the same, the melody has to carry that difference." | The measured finding is the form; offer form changes, with a melodic lift as one option. |
| Five options: three form changes, a melodic lift and "leave it" (early test of this skill) | Two to four in all, "leave it" among them. |
| "A rap verse needs 16 bars" | Not in the style index: no style convention without a `styles.md` entry. |
