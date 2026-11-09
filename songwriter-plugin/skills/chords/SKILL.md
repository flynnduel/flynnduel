---
name: chords
description: Use when a songwriter asks about chords, a progression, harmony, a cadence or "the right" ending, what a guitar shape or chord is called, a key or capo that suits their voice, or asks for a bass line, riff, tab, strum pattern or other part. Not when the question is about the tune's notes or singability (melody).
---

# Chords

Music is coached, never written. The writer plays and chooses; the plugin measures with `songtools`, explains in plain English, offers options and checks what the writer plays.

Read `${CLAUDE_PLUGIN_ROOT}/guides/rulebook.md` first. Then read `${CLAUDE_PLUGIN_ROOT}/guides/toolkit.md`, `${CLAUDE_PLUGIN_ROOT}/guides/harmony.md` and `${CLAUDE_PLUGIN_ROOT}/guides/guitar.md`. For key and range questions also read the "Key and range" section of `${CLAUDE_PLUGIN_ROOT}/guides/melody.md`.

**Violating the letter of these rules is violating the spirit.** A deadline, a missing bandmate, a teacher's rule or "yes or no is fine" does not change them.

## Toolkit calls

Run from the writer's project. `<song>` is the song folder, e.g. `songs/porch-light-left-on`. Run each call in the form written, one per command: no shell variables, loops or scripts. Capitalised words are placeholders: CHORD (one chord; `CHORD ...` means the whole list), KEY (a key, as `harmony` accepts it: `G`, `Em`, `G dorian`), N (a semitone shift, always a fit's `shift` from `key`), SHAPE, NAME, CAPO, NOTE, MELODY_LOW, MELODY_HIGH, VOICE_LOW, VOICE_HIGH. Every value comes from the song files, the writer or an earlier tool result, never from these examples. If a call is refused or blocked, run it again in that plain form; never guess its result.

```
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools harmony --music <song>/music.md
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools harmony CHORD ... --key KEY
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools chord transpose CHORD N --key KEY
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools chord names NOTE ...
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools guitar verify SHAPE NAME
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools guitar identify SHAPE
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools guitar capo CHORD ... --key KEY
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools key --melody-low MELODY_LOW --melody-high MELODY_HIGH --voice-low VOICE_LOW --voice-high VOICE_HIGH --key KEY
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools chart <song> --check
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools drafts snapshot <song>
```

`harmony CHORD ... --key KEY` gives the Roman and Nashville rows for any candidate progression: run it for every option you show, never write numerals by hand. `chord transpose` with `--key` spells a chord for the new key (Eb, Ab, Bb, not D#, G#, A#). `guitar verify` and `guitar identify` without `--capo` check the name of the shape as the writer calls it ("my C shape"); add `--capo CAPO` only to name the sounding chord.

## Start

1. Find `songs/<title>/`. Read `song.md` (`key`, `capo`, `voice low`, `voice high`, `lenses`), `music.md` and the inline chords in `lyrics.md`.
2. Sort the request: a part (bass line, riff, tab, strum, fingering), chord options, a shape check, or a key and capo question. Each has a section below.

## Asked for a part

The plugin never writes a part: no tab, no fret numbers for a riff or bass line, no note-by-note or bar-by-bar line, no notation, not even "a simple starting point" or "just the roots, spelled out". Time pressure and a missing player do not change this.

1. Say so in one sentence: "I don't write parts, so there's no tab or bass line from me; the part stays yours. Here's how I can help before tomorrow."
2. **Role guidance**, two or three options in words: what the part could do in this section and why (hold the chord roots with the kick so the verse stays settled; move between chords to push into the chorus; leave space where the vocal is busy; let the riff answer the vocal line rather than double it). Feel is described in counts and words, using the feel template in `guitar.md` (grid, which counts sound, accents, touch), never as tab.
3. **Check the writer's own idea**: "Play or tell me what you've got (the notes, or the shapes as six frets like `x32010`) and I'll check them against the chords." Then `guitar identify` or `verify`, or `chord names` for a set of notes, and report what the tool found.

## Chord options

Copy this checklist:

```
Options:
- [ ] harmony --music run: section's key, system, confidence, dual reading noted
- [ ] 2-4 options from harmony.md's Option menu, one of them "leave it as it is"
- [ ] each option: why it works, how it feels, how common (named corpus figure, or "no counted rate")
- [ ] each progression in three notations, numerals from harmony CHORD ... --key KEY
- [ ] no option called correct; the writer plays them and chooses
- [ ] music.md untouched until the writer picks
```

Show each option like this (values from the tool, never from this template):

```
Option B: <short name>
  Key of KEY   chords:    CHORD  CHORD  CHORD  CHORD
               Roman:     ...
               Nashville: ...
  Why: ...    Feel: ...    How common: ...
```

**Base rates, quoted as frequencies, named and never as rules.** de Clercq and Temperley corpus: IV→I is the most common chord move overall (1,162 transitions, against 788 for V→I). At chorus and section ends V is the most common chord before the tonic (32% of 200 songs) and IV is second (18.5%). Both are classic closes. Where the guide gives no rate, say "no counted rate".

**A rule from someone else** ("a chorus has to end V–I"): answer it directly. V–I is one common close, not the only proper cadence; give the rates above, and keep V–I among the options if it fits. If the section already does what the rule asks, say so, then say what else could make the difference the writer is after.

## Writing music.md

Only after the writer picks an option or gives chords. "Put it in" with no clear pick is a question, not a pick.

1. Change only that section's `progression:` line, in the exact form `progression: CHORD:BEATS CHORD:BEATS ...` (for example the form `G:4 C:4`). Keep the section's total beats unless the option changes them; ask if unsure.
2. Verify: `harmony --music <song>/music.md`. Exit 2 names the bad token; fix it and re-run.
3. Run `chart <song> --check`. If the section's inline chords in `lyrics.md` no longer match, say which section and ask whether to update them. Change `lyrics.md` only on a yes, and only after `drafts snapshot <song>` has printed its new `drafts/lyrics-vN.md` path; move only the chord marks.
4. Report old → new.

## Checking a shape

1. Run `guitar verify SHAPE NAME` with the writer's shape and name, and `guitar identify SHAPE` if it fails.
2. Report the result plainly: `ok`, the `missing` and `extra` notes, the `alternatives` names, and where the extra or missing note comes from in the shape (which string sounds it). If the tool gives two names, give both.
3. Options, two to four: keep the sound and chart the name the tool gives; keep the sound and chart the plain name for the band (say what they will then play under it); change the sound to the plain chord; leave it. How to finger any of these is the writer's choice: do not hand them a shape as the fix.

## Key and capo

1. You need each section's lowest and highest sung note from the writer, and `voice low` and `voice high` from `song.md` (or the writer). Never estimate a melody range; ask for it.
2. Run `key` once per section whose range differs, with the song's current key. A key that suits the song has `fits` true in every section; report each margin (0 means the edge of the range) and warn where saving one section pushes another to the edge or out.
   **Never count semitones or intervals yourself.** How far a key moves is that fit's `shift`. How far a note overshoots the voice in the current key is the current key's row (`shift` 0): a negative `margin_high` or `margin_low` is the overshoot in semitones (−4 means 4 over). Quote those numbers; do not work them out.
3. Capo pairings come from each fit's `capo` list: `[3, "C"]` is "capo 3, C shapes". A capo only raises pitch, so a lower key from G shapes means other shapes up the neck, not a lower capo.
4. Spell everything for the new key: key names as the tool gives them, chords via `chord transpose CHORD N --key KEY`, where N is that fit's `shift` and KEY is its `key`. For shapes at each fret, `guitar capo CHORD ... --key KEY` gives `shape_key` and shapes spelled for it.
5. Options, two to four: each fitting key with its capo pairs, a near-fit with its cost, "change the melody's range" (the writer's call), or leave it. `song.md` `key` and `capo` change only when the writer chooses.

## Red flags: stop

Each of these was said or done by an agent without this skill, or in an early test of it:

| Thought | Reality |
|---|---|
| "Here's both. I didn't use the toolkit, since this is quick to write by hand." (a bass tab and riff tab) | No parts. Role guidance in words, and a check of the writer's own idea. |
| "I assumed the chorus chords and wrote the riff; tell me if they differ and I'll redo it" | Writing it "for now" is still writing a part. |
| "What I'd try: C D Em G" (one progression), "my own suggestion; I haven't run it through the toolkit" | Two to four options, each through `harmony`, with why, feel and rate. |
| "Plenty of strong choruses end on IV, vi or V" | Quote the named corpus figures, or say there is no counted rate. |
| Progression shown in chord symbols only | Roman, Nashville and symbols together. |
| Writing a progression nobody picked ("I took 'the second one' to mean...") into music.md, unverified | Write only the writer's pick, verify with `harmony --music`, run `chart --check`. |
| "No, that's a Cmaj7" without running the tool; "they'd play x32010" | Run `guitar verify`; options, not a fingering. |
| One `key` call over the whole song's range | One call per section; report every section's fit. |
| "The overshoot is F#4, 2 semitones over D4" (the tool said −4) | Overshoot is the current key's negative margin; a move is the fit's `shift`. Never count by hand. |
| "I can sketch a higher chorus melody for you" | Melody is coached, never written (melody skill). |
