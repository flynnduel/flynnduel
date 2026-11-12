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

## RED: baseline (no skill)

Four baseline runs per scenario. In r1 and r2 the subject could read the plugin folder (it was added as a working directory), and most of them found `guides/critique.md` beside the toolkit and read it. Those runs are marked "guides read" and are weak baselines. For r3 and r4 the plugin folder was no longer added. The toolkit still ran through `uv run --project`, but the guides could not be read. These r3/r4 runs are the real RED. Key: ✓ pass, ✗ fail, ~ partial.

| Scenario | r1 (guides read) | r2 (guides read) | r3 | r4 |
|---|---|---|---|---|
| C1 full critique | a✓ b✓ c✓ d✓ | a✓ b✓ c✓ d✓ | a✗ b✗ c✗ d✓ | a✗ b✗ c✗ d✓ |
| C2 unsolicited taste | a✓ b✓ | a✓ b✓ | a✗ b✓ | a✗ b✓ |
| C3 Davis claim | a✓ b✓ | a✓ b✓ | a✗ b✗ | a✗ b~ |
| C4 kept lines | a✓ b✗ | a✓ b✗ | a✗ b✗ | a✗ b✗ |
| C5 Bellbird Hill (BM) | a~ b✗ c~ d✓ | a~ b✗ c✗ d✓ | a✗ b✗ c✗ d✓ | a~ b✗ c✗ d~ |

How the clean baselines failed (in substance):
- **C1.** r3 and r4 open with "Short answer: yes, the bridge is too vague". There is no statement of meaning before it and no neutral questions. Notes are loose lists ("How to fix it:", "What to look at", five items) with no location, basis or options. Rules are stated as universal ("A bridge should show us something new"). Both judge stock language by ear: "The cliché scan flagged nothing, but those two lines … sound weaker."
- **C2.** r3 says "the title is never sung … pull 'porch light' into one chorus line, or retitle the song" and "a publisher's demo or chart will expose the inconsistency". r4 says "Under the Webb lens it comes out as a false rhyme. A publisher who hears it as a miss will notice" (the webb lens is off) and "For a pitch, make the chorus work if someone hears only that section". It imposes one fix: "I will not be sleeping at home". Neither asks permission. Craft notes are given plainly in both.
- **C3.** r3 runs the checklist as rules ("Time frame: broken"), with no "as reported" label. r4 says "As I remember it, she treats consistency of time, place and viewpoint as part of lyric unity". That is from memory, unlabelled, and it applies "the three criteria as you stated them".
- **C4.** r3 puts the kept line among the strengths ("you were right to keep it") and re-argues home/alone ("the rhyme is softer than the cliché's reputation suggests"). r4 calls the kept lines "the song's best" and adds an "About home/alone" section. Neither has a separate group or asks a question. The guides-read runs listed both kept lines in their own group but never asked about them.
- **C5.** No clean run says that aabb stops the motion at each couplet; the nearest is r4: "four perfect rhymes in a row sound settled". No run brings the boots image forward or lays out alternative schemes side by side. Each offers one fix ("making the second pair a near-rhyme"). r4 says "the line lengths are even" by eye, while `stability` reports 5/4/5/4. The guides-read r1 lists "Try abab or abba" as an option but does not show either.

## GREEN: with the skill

| Scenario | g1 | g2 | g3 | g4 | g5 | g6/g7 |
|---|---|---|---|---|---|---|
| C1 | ✓ | ✓ | ✓ | ✓ | (usage limit, no reply) | g7 ✓ |
| C2 | ✓ | a✗ b✓ | ✓ | ✓ | ✓ | g6 ✓ |
| C3 | ✓ | ✓ | ✓ | ✓ | ✓ | |
| C4 | ✓ | ✓ | ✓ | ✓ | (usage limit) | g7 ✓ |
| C5 | a✓ b✗ c✓ d✓ | a✓ b~ c✓ d✓ | ✓ | ✓ | ✓ | |

Round 1 (g1, g2) used the first SKILL.md. g3 and g4 used the first refactor (taste-offer, image-placement and option-count counters). g5 to g7 used the final text, which adds the plain-call counter and a neutral taste example. Runs marked "usage limit" ended without a reply because the account hit its usage limit, and were rerun as g7.

Evidence, in summary:
- **C1.** Every with-skill reply follows this order: "What it seems to be about" with 1–3 strengths tied to measurements; then "Your question: is the bridge too vague?" answered "Partly, yes" as a six-part note; then neutral questions ("What should the listener feel at the bridge: doubt, or a decision?"); then two or three ranked notes, point of view (song level) first and the home/alone pair (line level) last. Each note has Location, Observation, Mechanism, Listener effect, Basis and Options with "leave it". The diff of the project folder is empty in every run. The "vagueness" reading is labelled as the subject's reading, since the scan did not flag it.
- **C2.** Craft notes are given plainly: the point-of-view shift, chorus stability with measured reorderings, and the `cliche --strict` home/alone hit. In g1, g3 and g4 the publisher and strict-rhyme points appear only as offers ("I have a taste note about how a publisher might hear the chorus, want it?"), and g1 adds that the pitch "doesn't switch on the commercial lens". g2 failed C2.a: its offer gave the verdict ("Under Webb's lens, a family rhyme like this would be a false rhyme"). After the refactor, g5 and g6 name only the topic.
- **C3.** "I can't run it or give you a pass or fail against it. The plugin has not read her checklist at source … Davis (as reported) holds one time frame, one viewpoint and one setting as defaults." The time jump is then raised under "Dodson: time jumpers (verified)", with "Davis (as reported)" as a secondary mention only. No run calls Davis verified.
- **C4.** A "Kept lines" group lists both lines with their kept issue and reason, then asks once: "Are you still keeping these as they are?" No strength or note re-argues home/alone. g2 raised a new issue on the chorus scheme, saying that "the home/alone pair is kept for its cliché; this note is only about how the scheme moves" (rule 9: a new issue is allowed).
- **C5.** g1 and g2 wrote "aabb closes at each couplet, so the section stops twice" and showed the writer's own lines reordered as abab and abba side by side, each measured with `stability` on a scratch file, ending "choose by feel". But neither named the buried image (C5.b ✗/~). After the refactor, g3, g4 and g5 say "the strongest image comes third … Pattison: an image placed first colours the lines after it". Their versions bring the boots line first or second (abab, abba, and aabb with the boots first). No file is changed and no single rewrite is imposed. Every with-skill run also noticed that the kept porch-light line is no longer in `lyrics.md` and asked about it.

## REFACTOR

New failures seen in GREEN round 1, and their counters:
- C2 g2 put the taste verdict inside the offer. Counter: "The blank names the topic only …, never the verdict or the lens's reading." The skill's example was first copied from this scenario ("strict rhyme on home/alone"), so it was replaced with a neutral one ("rhyme strictness in the bridge") to avoid teaching to the test.
- C5 g1 and g2 did not name image placement. Counter, a general principle under "Structure notes are demonstrated": "say where the section's strongest concrete image sits; Pattison: an image placed first colours the lines that follow it. If it sits late, at least one version brings it forward." The skill names neither aabb nor this verse.
- C3 g2 gave five options. Counter: "two to four (never more)".
- Harness: parallel runs shared one scratch directory, and one subject found its file overwritten. Each run now gets its own `${CLAUDE_PLUGIN_DATA}`.
- The finalcheck F1 g4 block (below) led to a counter in both skills: run each call as written, one per command; if a call is refused, rerun it in that plain form, and never guess.

Blindness of C5: the skill states only general principles. The critique guide that the skill loads holds the Perth write-up in one bullet. C5 therefore shows that the skill makes the subject apply its guide; it is not a held-out test of the guide.

## Fix round 1

Changes: `drafts diff --song` now reports `kept_missing`, added test-first. Kept lines are diffed as the newest snapshot against `lyrics.md`; with no snapshot, `lyrics.md` is diffed against itself, the subject says so, and presence comes from `kept_missing`. Call blocks use placeholders. The writing says "no song file is written". A direct taste question counts as permission for that one answer (Lerman step 2). The description now separates critique from finalcheck.

| Scenario | g9 |
|---|---|
| C1 | ✓. Order, six-part notes, empty diff; the kept line is listed with "There is no draft snapshot". |
| C2 | ✓. Both offers name only the topic ("what a publisher may look for in a chorus", "rhyme strictness in the last line"); craft notes are plain. |
| C4 | ✓. "Both are still in `lyrics.md` (`kept_missing` is empty). There is no `drafts/` snapshot, so I couldn't check whether either was altered." One question for the group. |
| C5 | ✓. aabb "comes to rest at each couplet"; "an image placed first colours the lines after it"; four measured versions (aabb with the boots first, two abab orders, and the original). The kept line is reported from `kept_missing`, not by reading. |

## Regression from the end-to-end run (B2)

`skill-tests/end-to-end.md`, stage 10: the "What it seems to be about" summary added a detail no file holds. Step 1 now builds the summary only from the files and the writer; red flag added. Re-run once: summary traced to `song.md` and `lyrics.md`.
