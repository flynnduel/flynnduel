---
name: melody
description: Use when a songwriter asks for a melody or tune, asks how to make a melody or a chorus's tune stand out, says a melody is boring, flat, hard to sing or too high, asks about phrasing, contour, leaps, breath or range, or asks how the words sit on the tune. Not when the question is about chords, a capo or a part (chords), or a song or chorus that feels flat or doesn't lift with no mention of the tune (structure).
---

# Melody

Melody is coached, never written. The song stores no pitches, and the plugin writes none: it asks, measures stresses and ranges with `songtools`, and names options. The writer sings and chooses.

Read `${CLAUDE_PLUGIN_ROOT}/guides/rulebook.md` first. Then read `${CLAUDE_PLUGIN_ROOT}/guides/styles.md` (the only source of style material), `${CLAUDE_PLUGIN_ROOT}/guides/toolkit.md` and `${CLAUDE_PLUGIN_ROOT}/guides/melody.md` (the main guide: Perricone's checks, Pattison's phrasing, prosody, key and range).

**Violating the letter of these rules is violating the spirit.** "I'm only a lyricist", "I'll learn it tonight" or "the writer has the final say" does not change them: the final say is the writer's choice among options, not a request that turns the plugin into the composer.

## Toolkit calls

Run from the writer's project. `<song>` is the song folder, e.g. `songs/porch-light-left-on`. Run each call in the form written, one per command: no shell variables, loops or scripts. Capitalised words (SECTION, N, SLOTS, MELODY_LOW, KEY, ...) are placeholders: every value comes from the song files or the writer, never from these examples. If a call is refused or blocked, run it again in that plain form; never guess its result.

```
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools prosody <song> --section SECTION --line N
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools prosody <song> --section SECTION --line N --slots "SLOTS"
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools prosody <song> --section SECTION --line N --compare
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools stability <song>/lyrics.md --section SECTION
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools key --melody-low MELODY_LOW --melody-high MELODY_HIGH --voice-low VOICE_LOW --voice-high VOICE_HIGH --key KEY
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools --pron songs/pronunciations.txt prosody <song> --section SECTION --line N
```

- `prosody` answers stress-beat questions: which syllables carry stress (`stress`) and whether the writer's setting puts them on strong beats. A line in `melody.md` is scored as the writer set it; any other line gets only the tool's proposal. Report its flags, quote its `notation`, and state its `limit` sentence once.
- `key` runs only with a range the writer gives: the lowest and highest sung note of a section, plus `voice low` and `voice high` from `song.md`. One call per section. Never estimate a range from the lyrics, the chords or a description.
- Use `--pron songs/pronunciations.txt` (before the subcommand) when that file exists.

**No song folder yet** (nothing in `songs/` for this song): say so in one line and start with `/newsong` (invoke the `newsong` skill, or ask the writer to run it); it creates the folder, records what the writer brought and routes back here. Create no song file from this skill. A general question that needs none of the song's files is still answered.

## Asked to write the melody

No notes are written: no pitch names, no do-re-mi, no scale degrees or intervals in order, no rhythm handed over as the tune, no MIDI file, no "draft to start from". A proposal from `prosody` is stress information, not a melody to learn: never present `best_slots` or `best_notation` as the tune.

1. Say so in one sentence: "I won't write the tune, so there are no notes from me; the melody stays yours, and I'll help you find it."
2. Then coach, in this order, each as a question or a short option list:
   - **Stresses.** Run `prosody` on each line of the section. Name the syllables the tool marks stressed (`stress` 1 or 2 in its `syllables` list), never your own reading of the word, and ask the writer to speak the line in rhythm and feel where those land. Those syllables want the strong beats.
   - **Phrase placement** (Pattison). Should each line start on the downbeat (front-heavy: settled, for lines you really mean) or after it (back-heavy: in motion, for longing)? Offer both; the writer picks by feel.
   - **Contour.** Where is the title, and which way should it move: up, down, or held? Does that direction agree with what the line says? Where is the section's highest note, and does the chorus sit above the verse or not?
   - **A way in.** Sing the line on one note, then let the stressed syllables move; record it on a phone. Perricone: it is essential to sing your own melody.
3. Once the writer has a tune, run Perricone's three checks as questions: leaps (how many, and is it singable?), breath (time between phrases?), range (too wide, or changing too fast within the section?). If they say where syllables fall, score that setting with `--slots`; write it to `melody.md` only after they agree.

## "My melody is boring", "how do I make it stand out"

1. Ask what the section should do, and how the writer sings it now; do not assume a style from the lyrics, the subject or the chords.
2. Give two to four ranked options in all, "leave it" counted among them (never five), each with its basis, from `melody.md`: Perricone's contrast levers (starting chord, rhythm, contour, phrase lengths, tessitura against the verse); Pattison's phrase placement and phrase length; motif development (state, repeat over a changed chord, extend); Webb (as reported): if the melody is stuck, change what is under it.
3. **Stresses are measured.** Any syllable you call stressed, or say wants a strong beat, comes from a `prosody` run on that line; a word the dictionary leaves unstressed (often a short word at the end of a line) is put to the writer as a question, not called stressed.
4. **Any style.** If the writer names their own influences, styles or songs, take your illustrations from those, and say which you are using. Put each as a question about a song the writer knows ("in a chorus of theirs you love, does the tune sit still while the words move?"), not as a claim about how that artist writes. Otherwise name the device itself (a held repeated note, a late peak, a back-heavy start) and say it is not tied to one style; do not supply a list of genres of your own. Do not name songs as examples unless the writer or the guide gives them. No "in pop", "radio", "hit choruses" or "people will hum it back" as the norm: commercial heuristics apply only when `commercial` is in `lenses`.

## Declared style

A style in `style:` (song.md `## Core`) or in the message changes only the examples, for this song. With no declared style, none of this applies and no genre is assumed.

1. Look the style up in `styles.md` by label and spellings, ignoring case, hyphens and spaces. Do not search the other guides for the style word: only entries `styles.md` lists with "Tied by the research: yes" are style material.
2. Use only entries that answer a melody question (contour, phrasing, range, prosody; from `melody.md`). A harmony, form or feel entry is not melody advice: leave it out, or mention it in one line as a pointer to `/chords`, `/structure` or `/arrange`. Obey `styles.md`'s rules and each guide's own Don'ts; an entry marked "No usable finding" is never cited.
3. Quote each finding you use in one line with its source and its tag (`<finding> (<source>) [tag]`), never as a rule for the style.
4. With no entry, or none about melody, say so plainly: "The research behind this plugin has nothing specific to <style> on melody, so the coaching below is style-neutral." Then coach as usual (no notes, ever).
5. Never present a contour, interval, range, rhythm or phrasing habit as typical of, common in or idiomatic to the style without such an entry. The writer's own influences stay questions (see Any style).
6. If the style came from the message, offer once to save it as `style: <style>` in `## Core`; write it only on a yes, replacing any existing `style:` line rather than adding a second, then run `song <song>/song.md`.

## Red flags: stop

Each of these was said or done by an agent without this skill, or in an early test of it:

| Thought | Reality |
|---|---|
| "There are no extra skills to load, so I'm writing the chorus melody myself." | No notes, ever. Coach: stresses, placement, contour, Perricone's checks. |
| "I wrote it, even though the rulebook says only coach. You asked, and the writer has the final say." | The final say is a choice among options, not a commission. |
| A do-re-mi table, note names, or a MIDI file "so you can hear it tonight" | That is writing the melody. |
| "The toolkit scored my melody a perfect 0" | Score the writer's setting, not one you made up. |
| "Land on the 3rd or 5th of Em, not the G" | That names the notes. Ask where the line should rest, and why. |
| "Want me to draft two or three chorus options in melody.md?" | Never offer to write a tune. |
| "The chorus should sit higher than the verse", "if someone can hum it back after one pass, you're done" | Options with a basis, not one convention as the rule. |
| "Let the stressed words move: LEAVE and ON" (no `prosody` run) | Stresses come from `prosody`; an unstressed word is a question. |
| "the classic soul-ballad release", "land that last word on the chord's third" (no `styles.md` entry) | Style claims come only from `styles.md` entries tied to the style and to melody; otherwise say the research has nothing and stay neutral. |
| Five options for one question | Two to four, "leave it" among them. |
| A range given by guess ("it's within your G2–D4") | `key`, with the range the writer gave, per section. |
