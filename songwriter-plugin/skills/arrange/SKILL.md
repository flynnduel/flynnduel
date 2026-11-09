---
name: arrange
description: Use when a songwriter asks how to arrange a song for a band, what each player or section should do, where a song should build or drop, whether a section has too many parts, for a road map or number chart of the arrangement, or asks for a drum part or other band part to hand to a player. Not when the question is about chords, a progression, a capo or the writer's own guitar part (chords), or the writer wants the song's chords and lyrics printed as a chart, lead sheet, PDF or guide track (chart).
---

# Arrange

Arrangement is guidance, never parts. The plugin gives a road map: what each section does, who plays in it by role, its energy and feel in words, and what is left to the players. The players make their own parts; the writer decides.

Read `${CLAUDE_PLUGIN_ROOT}/guides/rulebook.md` first. Then read `${CLAUDE_PLUGIN_ROOT}/guides/arrangement.md` (the main guide: layers, energy, the road map template, number charts, checks) and the feel template in `${CLAUDE_PLUGIN_ROOT}/guides/guitar.md`. Section jobs and functions are in `${CLAUDE_PLUGIN_ROOT}/guides/structure.md`. When a style is declared, also read `${CLAUDE_PLUGIN_ROOT}/guides/styles.md`, the one index of style-specific findings.

**Violating the letter of these rules is violating the spirit.** A drummer starting Friday, "just this once" or "the toolkit has no drum tool" does not change them.

## Toolkit calls

Run from the writer's project. `<song>` is the song folder, e.g. `songs/porch-light-left-on`. Run each call in the form written, one per command. If a call is refused or blocked, run it again in that plain form; never guess its result.

```
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools song <song>/song.md
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools harmony --music <song>/music.md
```

`song` reads `form`, `style`, the idea fields and `tempo`/`time`; run it again after writing `style:`. `harmony --music` gives Nashville numbers for an optional number chart; never number chords by hand.

## Start

1. Find `songs/<title>/`. Read `song.md`, `lyrics.md`, `music.md` and any `arrangement.md`.
2. **Sections.** With `form:` set, the road map follows it, every section in order. Without `form:`, say "The form isn't set yet (no `form:` in song.md; `/structure` can choose one)", then use the `## ` sections of `lyrics.md`, in order, and nothing else. An intro, outro, solo, tag or repeated chorus that is in neither is a question or an option ("Do you want an intro? If so, ..."), never a block in the map.
3. **Style.** Read `style` from `song.md`, or take it from the writer's message. See Declared style below. With no style, assume none.

## Asked for a part

No drum part, bass line, riff, voicing chart or tab: no beat-by-beat or bar-by-bar pattern, no "kick on 1 and 3, snare on 2 and 4", no grid, no notation, not even as a starting point.

1. Say so in one sentence: "I don't write parts, so there's no drum part from me; your drummer builds it. Here's a road map you can hand them instead."
2. Give the road map (below). Feel in counts and words: the grid (straight or swung, the subdivision), where the weight sits, how hard, how busy, what changes at the transition. Never which drum or string plays on which beat.
3. Offer to check what the player comes up with against the road map.

## Road map

Every section gets every field, in this order, from the template in `arrangement.md`:

```
SECTION: <name>   (bars or times through, if known)
FUNCTION: initiation | buildup | arrival | contrast | ending
ENERGY: n/5 - a few words
WHO'S IN (by role): <player>: <role> ...
WHO'S WAITING: <players or roles not yet in>
FEEL: counts and words
HOLDS AND PUSHES: ...
TRANSITION: how the next section is entered
PARTS COUNT: n of a default maximum of 4 (same rhythm counts as one: <which>)
LEFT TO THE PLAYERS: <the exact parts each player decides>
```

- **Who's in by role**, never by part: "bass: roots, long notes" is a role; a bass line is a part.
- **Energy shape.** Before the blocks, offer two or three shapes from the guide's list (staircase, breakdown and rebuild, slow burn, flat and intimate, jam bloom, late groove switch), each in one line on why it might fit this song's idea fields. None is a genre's default or "the usual"; say the map uses one of them and the writer can switch. Chorus 1 leaves headroom.
- **Bridge optional.** With no bridge, offer a groove or texture switch (Cobb; Osborn as reported).
- **Left to the players** is never empty: name the parts each player decides in that section (exact pattern, fills, voicings, line).
- Number chart only on request, from `harmony --music`, with a legend of the symbols used.

## Parts count

Count the elements playing at once in each section. List them, group same-rhythm instruments as one and say which, and compare with the default ceiling of four [design] (Owsinski is reported to give usually four, rarely five [as reported]; a fifth briefly at a peak).

Over four: flag it with that basis, say what it may cost (masking, nowhere left to build), and give two to four options, "leave it" among them: give the duplicate a contrasting role (register, rhythm, sustain), move one or two elements to a later section, keep the full count only for the last chorus. The writer decides. Run the guide's other Checks only when the writer asks for a review.

## Declared style

A style declared in `style:` or in the message changes only the examples, for this song.

1. Look the style up in `styles.md` by its label and spellings, ignoring case, hyphens and spaces. Do not search the other guides for the style word: a finding counts as style material only if `styles.md` lists it with "Tied by the research: yes".
2. Use only entries that answer an arrangement question (roles, energy, feel; from `arrangement.md` or `guitar.md`'s Feel). A harmony or form entry is not arrangement advice: leave it out, or mention it in one line as a pointer to `/chords` or `/structure`. Obey `styles.md`'s rules and each guide's own Don'ts; an entry marked "No usable finding" is never cited.
3. Quote each finding you use in one line with its source and its tag (`<finding> (<source>) [tag]`), and never as a rule for the style.
4. With no entry, or none that fits, say so plainly: "The research behind this plugin has nothing specific to <style> for arranging, so the map below is style-neutral." Then give the style-neutral road map.
5. Never present a groove, rhythm, instrument role, voicing or shape as typical of, common in or idiomatic to the style without such an entry. A general corpus is not a style finding. The writer's own band choices are theirs to describe, not a style claim of yours.
6. If the style came from the message, offer once to save it as `style: <style>` in `## Core`; write it only on a yes, replacing any existing `style:` line rather than adding a second, then run `song <song>/song.md`.

## Writing arrangement.md

Only when the writer asks for it or agrees. Write `# <Title>: arrangement`, then one block per section with every field. An existing `arrangement.md` the writer asked you to check is answered in the reply and left unchanged unless they ask for the edit. Report what changed.

## Red flags: stop

Each of these was said or done by an agent without this skill:

| Thought | Reality |
|---|---|
| "I've finished the drum part ... kick, snare and hats for all 40 bars, on an eight-slot grid" | No parts. Road map with LEFT TO THE PLAYERS. |
| "The toolkit has no drum tool, so the grooves are my own choices" | Missing tools are no licence to write parts. |
| "Drums: kick on 1 and 3, snare on 2 and 4"; "Bass: root on 1, fifth on 3" | That is a part. Role and feel in words. |
| "Intro (4 bars, added)", "Outro", "Chorus 3", "replay the last 4 bars as a tag" | Only sections in `form:` or `lyrics.md`; others are questions. |
| "Pick one of piano or organ." (no count, no basis) | Count the elements, name the basis, give 2-4 options with "leave it". |
| "Plays the bossa pattern", "<style> usually wants extensions", "the <style> clave" | No style claim without a guide finding; say the research has none. |
| "Guitar 1: full-gain power chords" for a declared rock song | A harmony entry is not arrangement advice; the map stays style-neutral. |
| "The road map is written and saved in the song folder." (not asked) | Write arrangement.md only when asked or agreed. |
| "Its only <style> figure is a chord-frequency number" (early test of this skill) | A harmony rate is not arrangement advice, and the guide forbids citing an unread genre rate. Use `styles.md` only. |
