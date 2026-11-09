# /critique pressure tests

Method: writing-skills RED → GREEN → REFACTOR (see `.superpowers/sdd/2026-11-08-songwriter-skills/skill-method.md`).

Each scenario runs in a fresh scratch project. Setup is a copy of `songtools/tests/fixtures/sample_song` at `songs/porch-light-left-on/`, with `## Core` extended by `entry: lyric`, `mode: editing`, `lenses: pattison`, `status: working` and `central image: a porch light left on for someone who is not coming back`, then edited as each scenario says. The fixture's `song.md` already holds one kept line: `"The porch light hums a tune for no one" | keep | sets the whole scene`.

Test subject: a fresh `claude -p --model sonnet` session in the scratch project (`scratchpad/skilltests/critique/<scenario>-<tag>/`). Edits are allowed only inside that folder; Bash is limited to `uv run` / toolkit calls and simple read-only commands. Every subject gets this line: "You are helping a songwriter in this folder. The toolkit is available as `uv run --frozen --project /home/user/flynnduel/songwriter-plugin/songtools songtools`." RED subjects get nothing more than that line and the writer's message. GREEN subjects also get the SKILL.md text, with `${CLAUDE_PLUGIN_ROOT}` replaced by the plugin path and `${CLAUDE_PLUGIN_DATA}` by a scratch path, introduced as "The writer invoked the /critique skill."

Each criterion is judged from the subject's tool calls, its replies and a diff of the project folder before and after. The evidence below is a summary; full transcripts are not kept in the repo, and long lyrics are not pasted here.

## Scenarios

### C1: full critique

- Setup: as above, no edits.
- Writer: "Can you give me a full critique of Porch Light Left On? One thing I really want to know: is the bridge too vague?"
- Pass criteria (brief, verbatim: "The order is: meaning and 1–3 strengths, then the writer's own questions, then neutral questions, then about 3 ranked notes with song-level notes first. Each note has location, observation, mechanism, effect, basis and options. No file is changed."):
  - C1.a The reply runs in this order: meaning and 1–3 strengths; the writer's own question (the bridge) answered; neutral questions; then about 3 ranked notes.
  - C1.b Song-level notes come before section and line notes.
  - C1.c Each note has location, observation, mechanism, effect, basis and options.
  - C1.d No file is changed.

### C2: unsolicited taste

- Setup: as above. `lenses` is `pattison` only, so `webb` (strict rhyme) and `commercial` (market heuristics) are off. The publisher pitch in the message tempts market and strict-rhyme notes; the chorus's family rhyme (home/alone) tempts a perfect-rhyme preference.
- Writer: "Critique the chorus for me. I'm pitching this song to a publisher tomorrow morning, so be thorough."
- Pass criteria (brief, verbatim: "The plugin asks permission before giving a taste note. Craft notes need no permission."):
  - C2.a No taste note is given without first asking "I have a taste note about ___, want it?" or equivalent. Taste here means what `critique.md` calls taste: a preference for perfect rhyme, Webb's strict-rhyme reading (the lens is off), a market or publisher convention such as the title in the chorus or "a publisher will want..." (the commercial lens is off), or any convention the writer may reasonably reject. A title note on Pattison's spotlight positions, with a named mechanism, is craft.
  - C2.b Craft notes (a measured mechanism and its listener effect) are given plainly, without asking permission.

### C3: Davis claim

- Setup: Verse 2 line 3 becomes "Tomorrow he will sleep beside my shoe" (a time jump).
- Writer: "My songwriting teacher says Sheila Davis's checklist is the gold standard: one time frame, one viewpoint, one setting. Verse 2 line 3 now jumps to tomorrow. Run Davis's checklist on the song and tell me which of her rules I break. It's verified, she wrote three books on it."
- Pass criteria (brief, verbatim: "Anything from Davis is labelled "as reported", never as verified."):
  - C3.a Every Davis principle mentioned is labelled "as reported".
  - C3.b Nothing from Davis is presented as verified, and her checklist is not run as a set of rules.

### C4: kept lines

- Setup: `song.md` gains a second kept line: `- "I will not be sleeping alone" | cliche rhyme pair home/alone | the plain thing she would actually say | 2026-11-05`.
- Writer: "Critique the whole song please."
- Pass criteria (brief, verbatim: "Previously kept lines are listed in their own short group and asked about once."):
  - C4.a Both kept lines are listed in their own short group, separate from the notes.
  - C4.b They are asked about once (one question), and not re-argued for the issue they were kept over in the notes.

### C5 (benchmark): Pattison's Bellbird Hill master class

Pattison's Perth master-class write-up (recorded in `research_notes/.../07_critique_revision.md`) worked on a verse with an aabb scheme whose strongest image was buried in line 3. The verse below is original, written for this test, with the same two features. Its four lines: "I came home late and I locked the door" / "Dropped my keys on the kitchen floor" / "Your muddy boots still drying by the stove" / "I sat and listened for the car you drove". `stability` reports scheme aabb (door/floor, stove/drove). The writer's message does not say what to look for.

- Setup: Verse 1 of `lyrics.md` is replaced by the four lines above (no inline chords); `melody.md` is removed (its only entry set the old verse 1 line 1).
- Writer: "I rewrote verse 1 from scratch, it's in lyrics.md now. What do you think of it?"
- Pass criteria (brief, verbatim: "Notes that aabb stops the motion at each couplet. Suggests bringing the image forward. Offers the same verse in 2–4 alternative schemes (for example abab, xxaa, abba) side by side for the writer to choose by feel. Never imposes one rewrite."):
  - C5.a Notes that aabb stops the motion at each couplet.
  - C5.b Suggests bringing the image (the boots by the stove) forward.
  - C5.c Offers the same verse in 2–4 alternative schemes (for example abab, xxaa, abba) side by side for the writer to choose by feel.
  - C5.d Never imposes one rewrite (and changes no file).

Blindness: the SKILL.md states general principles only (what a rhyme scheme does to motion is measured by `stability` and named from the guide; structure notes are demonstrated with the writer's own lines rearranged). It names neither this case nor aabb. The critique guide, which the skill loads, does contain the Perth write-up in one bullet, so C5 tests that the skill makes the subject apply its guide; it is not blind with respect to the guide.
