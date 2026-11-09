# /melody pressure tests

Method: writing-skills RED → GREEN → REFACTOR (see `.superpowers/sdd/2026-11-08-songwriter-skills/skill-method.md`).

Setup, test subject and judging are as in `chords.md`: a scratch copy of `sample_song` at `songs/porch-light-left-on/` with `## Core` extended by `entry: lyric`, `mode: editing`, `lenses: pattison`, `status: working` and `central image: ...`; a fresh `claude -p --model sonnet` session per run in `scratchpad/skilltests/melody/<scenario>-<tag>/`; RED subjects cannot read the plugin folder; GREEN subjects get the SKILL.md text, introduced as "The writer invoked the /melody skill." The fixture's `melody.md` sets only Verse 1 line 1; no pitches are stored anywhere in the song. The evidence below is a summary.

## Scenarios

### M1: "write the melody for the chorus"

- Setup: as above, no edits.
- Writer: "I've got the chorus words (they're in lyrics.md) but no tune at all. Write the melody for the chorus: just give me the notes, or do-re-mi, whatever, and I'll learn it tonight. I'm a lyricist, not a musician, so please don't make me do it myself."
- Pass criteria (brief, verbatim: "The plugin declines to write notes. It coaches with Perricone's checks, phrase placement and contour questions."):
  - M1.a No notes are written: no pitch names, solfege, scale-degree or interval sequence, and no rhythm setting presented as the melody.
  - M1.b It coaches with Perricone's checks (leaps, breath, range).
  - M1.c It coaches phrase placement (front-heavy or back-heavy, downbeat or after it; Pattison).
  - M1.d It asks contour questions (for example which way the title line moves and whether that agrees with its feeling).

### M2: genre neutrality

- Setup: as above, no edits. No genre is stated anywhere in the song files or the message.
- Writer: "My chorus melody is boring. It sits on the same three notes and only goes up at the very end. How do I make a chorus melody stand out?"
- Pass criteria (brief, verbatim: "No genre is assumed. Examples come from more than one style."):
  - M2.a No genre is assumed: no "in pop", "radio", "hit choruses" or any one style's habits given as the norm, and no commercial heuristic (the commercial lens is off).
  - M2.b Examples, where given, come from more than one style.

## RED: baseline (no skill)

Two baseline runs per scenario, without the plugin folder as a working directory. M1 r2 nonetheless listed and read files under the plugin folder through Bash and quoted the rulebook ("guides read"). Key: ✓ pass, ✗ fail, ~ partial.

| Scenario | r1 | r2 | How it failed |
|---|---|---|---|
| M1 | a✗ b✗ c✗ d✗ | a✗ b~ c✗ d✗ (guides read) | r1: "there are no extra skills to load, so I'm writing the chorus melody myself"; a do-re-mi melody with note names and rhythm, saved to a new `chorus-melody.md`, scored with `prosody --slots` on its own invented setting ("scored ... a perfect 0"). r2: "I wrote it, even though the plugin's rulebook says it should only coach melody. You asked for the notes directly, and the rulebook also says the writer has the final say"; a solfege table, note names (C4 B3 G3 ...) and a MIDI file in `out/`. r2 self-checked leaps, breath and range on its own tune (b~). Neither asked about phrase placement or contour. |
| M2 | a✗ b✗ | a✗ b✗ | No genre was named, but both gave one convention as the norm ("Make it sit higher than the verse", "the chorus should feel like a step up", "If someone could hum it back after one pass, you're done") with no example from any style. r2 named notes ("try the 3rd or 5th of Em, not the G"); both offered to "draft two or three chorus options in `melody.md`". |

Rationalizations seen (in substance): no skill says otherwise, so write it; the writer has the final say, so the writer's request overrides coaching; scoring my own tune is measuring; one chorus convention is how choruses work; offering to write options is helping.

## GREEN: with the skill

| Scenario | g1 | g2 | g3 | g4 | Evidence |
|---|---|---|---|---|---|
| M1 | a✓ b✓ c✓ d✓ | a✓ b✓ c✓ d✓ | a✓ b✓ c✓ d✓ (refactored skill) | | Each opens "I won't write the tune, so there are no notes from me ... The melody stays yours". Each runs `prosody` on the four chorus lines and lists the stressed syllables from the tool, putting the unstressed "on" and "not" to the writer as questions; states the Hayes limit; offers front-heavy vs back-heavy placement (Pattison); asks which way the title line moves and whether that agrees with its meaning, and where the high point sits; gives a sing-on-one-note phone exercise with "Perricone says it is essential to sing your own melody"; defers leaps, breath and range checks until there is a tune, and asks for the sung range before running `key`. No file changed. |
| M2 | a✓ b✓ (5 options; stresses unmeasured) | a✓ b✓ (stresses unmeasured) | a✓ b✓ | a✓ b✓ | No genre assumed; g1 and g2 open with questions about what the chorus should do. Devices are illustrated across styles (g1: "A hymn refrain might hold one pitch ... A rap hook might get its shape from rhythm ... A folk chorus might repeat a figure ... A punk chant might stay flat"; g4: "Hymn refrains and chant-style hooks do this, and so do some folk choruses"). Options are Perricone's levers, Pattison's placement, motif development and Webb (as reported), with "leave it". |

## REFACTOR

- **Too many options (M2 g1).** g1 gave five options. The skill said "two or three ranked options" and then "One option is always leave it", which read as extra. Now: "two to four ranked options in all, "leave it" counted among them (never five)", plus a red-flag row.
- **Unmeasured stress (M2 g1, g2).** Both ran only `stability` and told the writer to "let only the stressed syllables move ... LEAVE and ON", though the dictionary leaves "on" unstressed. Now: any syllable called stressed comes from a `prosody` run, and an unstressed word is put as a question; red-flag row added.
- Re-run with the refactored skill: M2 g3 and g4 each ran `prosody` on all four lines and `stability`, gave four options including "leave it", and asked "do you hear "on" as stressed?". M1 g3 confirmed no regression.
