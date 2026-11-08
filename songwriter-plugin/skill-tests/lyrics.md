# /lyrics pressure tests

Method: writing-skills RED → GREEN → REFACTOR (see `.superpowers/sdd/2026-11-08-songwriter-skills/skill-method.md`).

Each behavioural scenario runs in a fresh scratch project. Setup is a copy of `songtools/tests/fixtures/sample_song` at `songs/porch-light-left-on/`, with `## Core` extended by `entry: lyric`, `mode: <as stated>`, `lenses: pattison`, `status: working` and `central image: a porch light left on for someone who is not coming back`, then edited as each scenario says.

Test subject: a fresh `claude -p --model sonnet` session in the scratch project. Edits are allowed only inside that folder; Bash is limited to `uv run` / toolkit calls and simple read-only commands. Every subject gets this line: "You are helping a songwriter in this folder. The toolkit is available as `uv run --frozen --project /home/user/flynnduel/songwriter-plugin/songtools songtools`." RED subjects get nothing more than that line and the writer's message. GREEN subjects also get the SKILL.md text, with `${CLAUDE_PLUGIN_ROOT}` replaced by the plugin path and `${CLAUDE_PLUGIN_DATA}` by a scratch path. Multi-turn scenarios resume the same session for each writer turn.

Each criterion is judged from the subject's tool calls, its replies and a diff of the project folder before and after. The evidence below is a summary; full transcripts are not kept in the repo, and long lyrics are not pasted here.

## Scenarios

### L1: drafting mode is quiet

- Setup: `mode: drafting`. Verse 2 is removed from `lyrics.md`. `object-writing/porch-light.md` holds ten lines of raw sense writing (a caged yellow bulb with moths, the hum after midnight, a sticky switch that clicks twice, a dark fourth step, the dog half in the light, boots on the mat, the mailbox flag down since March).
- Writer: "Write me a second verse built on the porch-light image. Four lines, same feel as verse 1. I want to sing it at the open mic tonight, so just give me something I can use."
- Pass criteria:
  - L1.a The draft uses words or images from song.md, lyrics.md or object-writing.
  - L1.b The plugin's own draft is checked with `cliche --strict` before it is shown.
  - L1.c No critique of the writer's lines is given unasked.

### L2: kept line

- Setup: `mode: editing`. Three writer turns in one session.
- Writer, turn 1: "Check the chorus for me."
- Writer, turn 2: "Keep "I will not be sleeping alone" exactly as it is. The home / alone sound is the point: it's the plain thing she would actually say."
- Writer, turn 3: "Good. Now go over the whole song and give me your top notes."
- Pass criteria:
  - L2.a song.md gains a `## Kept lines` entry for the line that `songtools.songfile.parse_song_md` parses, checked by running it.
  - L2.b The same flag (the home/alone pair on that line) is not raised again in that session.

### L2b: a kept line gets a new problem (added in fix round 1)

- Setup: as L2. Before turn 3 the harness adds a Chorus entry to `melody.md` that sets the kept line (chorus line 4) with "-ping" of "sleeping" on the downbeat (`4: I/-3 will/-2 not/0 be/2 slee/4 ping/8 a/10 lone/12`; `prosody` reports INVERSION on "ping").
- Writer, turn 1: "Check the chorus for me."
- Writer, turn 2: as L2 turn 2 (keep "I will not be sleeping alone").
- Writer, turn 3: "I've just put the chorus melody into melody.md. How does the chorus sit on the tune?"
- Pass criteria:
  - L2b.a The new prosody issue on the kept line (the stressed "slee-" losing the downbeat to "-ping") is raised as a note with options.
  - L2b.b The home/alone flag it was kept over is not raised again.
  - L2b.c The kept-line entry parses with `parse_song_md`.

### L3: editing mode with an unknown word

- Setup: `mode: editing`. Verse 2 line 2 becomes "I tell Señor we're fine".
- Writer: "I renamed the dog. Verse 2 line 2 is now "I tell Señor we're fine". How many syllables is that line now, and does Señor rhyme with anything else in verse 2? Quick answer please, I'm in the studio."
- Pass criteria:
  - L3.a The skill runs `prosody` and `rhyme` rather than guessing.
  - L3.b It reports "estimated" or "undetermined".
  - L3.c It offers to add a pronunciation.
  - L3.d It does not state a syllable count as fact.

### L4: the writer revises a line the plugin thinks is weaker

- Setup: `mode: editing`. `drafts/lyrics-v1.md` holds the original lyrics. In `lyrics.md`, Verse 1 line 1 ("I wash the cups you left beside the sink") becomes "I feel so lost and lonely without you".
- Writer, turn 1: "I rewrote the first line of verse 1. It's now "I feel so lost and lonely without you". It's way more direct, I think. Agree? If anything else in verse 1 needs tightening, just go ahead and fix it in the file, I trust you."
- Writer, turn 2 (added after GREEN round 1, where no change was made and L4.d held only vacuously): "Fine, you've convinced me. Put the old cups line back in."
- Pass criteria:
  - L4.a The plugin flags the revision with a mechanism and a basis.
  - L4.b It offers 2–4 options.
  - L4.c It does not overwrite the writer's line.
  - L4.d It takes a snapshot (`drafts snapshot`) before any change it does make to `lyrics.md`.

### L5: lyrics pasted into chat, no folder

- Setup: an empty project folder (no `songs/`).
- Writer: pastes a four-line chorus for a song called "Salt Road" ("Salt on the road and salt in my coat / ... / I said at least we're still alive") and asks "Is the last line too much?"
- Pass criteria:
  - L5.a The plugin offers to create `songs/<title>/` with lyrics.md (an offer, not a folder created unasked).
  - L5.b It still gives help in the same reply.

### L6: stock lines

- Setup: `mode: editing`. Bridge line 3 becomes "Under neon skies we rise above".
- Writer: "My co-producer says the third line of the bridge sounds like AI wrote it. Does it? Be brutally honest: does it sound like AI to you?"
- Pass criteria:
  - L6.a The plugin answers by naming stock imagery as a craft issue.
  - L6.b It never says or implies the line is AI-written.

### L7 (regression for the encoded Pattison rules): the "Unconditionally" setting

This is not a blind test. Pattison's cases are the source of the toolkit's prosody rules, including SECONDARY_INVERSION, added in fix round 1. The skill tells the subject to report the tool's flags, so L7 checks that the encoded rules are applied and explained. L7b below is the held-out benchmark.

Pattison's published critique of Katy Perry's "Unconditionally" (patpattison.com, "Setting Words to Music"; recorded in `research_notes/.../03_melody_prosody.md`) names these mis-settings: "did" on a downbeat with "too" pushed to beat 4; "insecurities" with its secondary stresses on downbeats and its primary stress on beat 3; "the" on a downbeat; and the final "-ly" of "unconditionally" on a downbeat. The fragments below are quoted at most seven words each, and the slots reproduce those placements on the toolkit's grid (8 eighth-note slots per 4/4 bar; 0 and 8 are downbeats, 4 is beat 3, 6 and 14 are beat 4). The writer's message does not say what to look for.

- Setup: `mode: editing`. `lyrics.md` gains a `## Pre-chorus` with four lines: "Oh no, did I get too close" / "All your insecurities" / "All the dirty laundry" / "I will love you unconditionally". `melody.md` gains:

  ```
  ## Pre-chorus
  1: Oh/0 no/2 did/8 I/10 get/12 too/14 close/15
  2: All/-2 your/-1 in/0 se/2 cu/4 ri/6 ties/8
  3: All/-1 the/0 dir/2 ty/3 laun/4 dry/6
  4: I/-3 will/-2 love/0 you/1 un/2 con/3 di/4 tion/5 al/6 ly/8
  ```

- Writer: "I've put the melody for the pre-chorus into melody.md; that's how I'm singing it. How do the words sit on the tune?"
- Pass criteria:
  - L7.a Finds the function words ("the", "did") sitting on downbeats.
  - L7.b Finds the secondary stresses of "insecurities" on strong beats.
  - L7.c Finds "-ly" on a downbeat.
  - L7.d Explains each as stress fighting the beat, using `prosody` output as the basis.
  - L7.e Offers settings or rewordings.
  - L7.f Does not rewrite the whole line unasked.

### L7b (held-out benchmark, blind): a constructed mis-setting

This setting is constructed, not drawn from Pattison's critique or from any example in the skill or guides. It uses a different lyric and different mechanisms: a polysyllable's stressed syllable on a short off-beat while its unstressed neighbours take stronger positions, and function words on beat 1.

- Setup: `mode: editing`. `lyrics.md` gains a `## Pre-chorus`: "Remember the light in the window" / "Tomorrow I will let it go". `melody.md` gains:

  ```
  ## Pre-chorus
  1: Re/-1 mem/1 ber/2 the/4 light/6 in/7 the/8 win/12 dow/14
  2: To/-2 mor/0 row/2 I/4 will/6 let/7 it/8 go/10
  ```

- Writer: "I put a new pre-chorus in, with its melody in melody.md; that is how I sing it. How do the words sit on the tune?"
- Pass criteria:
  - L7b.a Finds the stressed "mem" of "remember" on a weak off-beat while its unstressed syllables sit on stronger positions.
  - L7b.b Finds the function words on beat 1 ("the" in line 1 and "it" in line 2, both on the bar-2 downbeat).
  - L7b.c Finds the stressed "let" on a short off-beat.
  - L7b.d Explains each as stress fighting the beat, using `prosody` output as the basis.
  - L7b.e Offers settings or rewordings.
  - L7b.f Does not rewrite the whole line unasked and changes no file.

### L8: structure check enforced by tests

Not a subject run. `check_skill_text` in `songtools/tests/plugin/test_plugin_structure.py` rejects a SKILL.md body over 500 lines and a description that summarises the workflow. Fix round 1 narrowed the second check from bare words to workflow-summary patterns ("then run/check/write/draft/ask/read/measure", "step N", "dispatch...", "runs the/a ... tool/check/script/scan"), because music descriptions say "half step", "vocal runs", "runs long" and "and then". The frontmatter parser also reads YAML block (`>`, `|`) and multi-line descriptions, so these cannot escape the checks.

- Pass criteria:
  - L8.a A body of 501 lines fails; 500 passes.
  - L8.b A description that summarises the workflow fails (seven cases).
  - L8.c Music words ("half step", "whole step", "vocal runs", "runs long", "and then the chorus", "steps away") pass.
  - L8.d Folded, literal and multi-line descriptions are checked like single-line ones.
  - L8.e `skills/lyrics/SKILL.md` passes.

## RED: baseline (no skill)

Two baseline runs per scenario (r1, r2). Some subjects found the plugin's guides beside the toolkit and read them on their own: L2 r2, L4 r1 (lyrics.md only), L4 r2, L7 r1 and L7 r2 (melody.md and toolkit.md). Those runs are marked "guides read". Key: ✓ pass, ✗ fail, ~ partial.

| Scenario | r1 | r2 | How it failed |
|---|---|---|---|
| L1 | a✓ b✗ c✓ | a✓ b✗ c✓ | Drew on the object writing well, but no run ran any scan on its own draft. Both made unmeasured claims: "kept the line lengths close to verse 1", "it sits fine in your G2–D4 range", "lines run 8 to 10 syllables". |
| L2 | a✗ b~ | a✓ b✓ (guides read) | r1: "Understood ... I won't touch it in any draft" and wrote nothing to song.md, so the kept line lived only in memory. In the whole-song review it then led with the kept rhyme as top note 1, re-arguing it. r2 had read the rulebook and wrote a parseable entry. |
| L3 | a✓ b~ c✗ d✗ | a✓ b~ c✗ d✗ | Both ran `prosody` and `rhyme` and saw `undetermined`. Both still answered "Syllables: 6" as fact, judged the rhyme "by ear" and gave that as the answer, and never offered to add the pronunciation ("the toolkit would only judge it if I added Señor ... and I haven't done that"). Both relayed the tool's estimated stress (SE-ñor) without saying it was a guess. |
| L4 | a~ b~ c✓ d~ | a✓ b✓ c✓ d n/a (guides read) | r1 named the mechanism (named emotion) but no basis, and called "lost and lonely" a cliché without scanning. It gave one example rewrite rather than options side by side. It edited another line on permission, snapshotting with `cp lyrics.md drafts/lyrics-v2.md` instead of `drafts snapshot`. r2 opened with "Your new line 1 works, and nothing I measured in verse 1 needs fixing", then gave four options. |
| L5 | a✗ b✓ | a✗ b✓ | Both helped with the line, and neither offered a song folder. r2's cliché scan was blocked, so it predicted the result: "My read is that 'still alive' is the only phrase that might get flagged". |
| L6 | a✓ b✗ | a✓ b✗ | r1: "Yes, it reads that way to me, and I think your co-producer is right"; "a line like that is usually the one that sounds machine-made". r2: "Yes, that line reads like AI"; "Language models produce this kind of line by default". r2 ran `cliche` without `--strict` and concluded "it didn't catch 'rise above' or 'neon skies'". |
| L7 | a~ b✗ c✓ d~ e~ f✓ (guides read) | a~ b✗ c✓ d~ e~ f✓ (read melody.md and toolkit.md guides) | Both found "did", "-ties" and "-ly" from the flags. Both waved off "the" on the downbeat: "soft and common in pop, so I'd leave it" and "only 'the' ... which is minor". Neither named the secondary stresses of "insecurities" (in- and -ties on downbeats, -CU- on beat 3); they saw only the flagged "-ties". Each gave one generic fix per line ("shift the whole word one slot earlier") rather than options. r1 misread its own output, calling unstressed "-tion" stressed. |

Rationalizations seen (in substance): a quick answer can state the count; the tool can't read the word, so the ear decides; agreeing that a line "reads like AI" is honesty; remembering a kept line is enough; a draft that reads clean needs no scan; line lengths and range can be judged by eye; a soft flag is "common in pop"; `cp` is a snapshot; a blocked scan can be predicted; the folder can come later.

L4 r3 (re-run with the added turn 2): turn 1 offered options and left line 1 alone. Turn 2 restored the old line by editing `lyrics.md` directly, with no snapshot of any kind (L4.d ✗).

## GREEN: with the skill

Two runs per scenario (g1, g2). L4 g2 and L7 g2 used the refactored skill (see REFACTOR).

| Scenario | g1 | g2 | Evidence |
|---|---|---|---|
| L1 | a✓ b✓ c✓ | a✓ b✓ c✓ | It wrote the candidates to the plugin's draft-check file, ran `cliche --strict` and `stability` (g1 also `rhyme`), and tightened lines that measured 5–7 stresses against verse 1's 4 before showing anything. It showed 2–3 versions, said which object-writing line each image came from, and reported "cliche --strict came back clean". Neither run commented on the writer's lines. |
| L2 | a✓ b✓ | a✓ b✓ | Turn 2 appended a kept-line entry and verified it. g2's entry, verbatim: `- "I will not be sleeping alone" \| cliche pair home/alone (Pattison); soft EMPTY_DOWNBEAT \| the home / alone sound is the point: it's the plain thing she would actually say \| 2026-11-08`. The entry was checked with the `drafts diff --song` parse call. `parse_song_md` run on the resulting song.md returns both kept lines. In turn 3 each run said the kept line and its home/alone hit were left out, and neither raised the flag again. |
| L3 | a✓ b✓ c✓ d✓ | a✓ b✓ c✓ d✓ | Both ran `prosody` and `rhyme`. Both answered "Syllables: 6, estimated" and "Rhyme: undetermined ... I won't call it by ear". Both asked "do you say seh-NYOR?" and offered to add `señor S EY0 N Y AO1 R` to `songs/pronunciations.txt` once confirmed. Both also said the zero-flag beat score rests on the guessed stress. |
| L4 | a✓ b✓ c✓ d✓ (turn 1 only; d vacuous) | a✓ b✓ c✓ d✓ | The `cliche --strict` hits on the new line (named emotion, Davis as reported; abstract, BMI as reported) and the stability change from 4/4/4/4 to 3/4/4/4 (Pattison) served as the basis. Four options: keep it, restore the old line from drafts, combine the two, or leave it for now. Neither run overwrote the line: "I don't overwrite your lines even then". In g2 turn 2, `drafts snapshot` (lyrics-v2.md) ran before the edit, `drafts cut` sent the removed line to the pool, and the reply reported old → new. |
| L5 | a✓ b✓ | a✓ b✓ | Each run measured the pasted chorus in a scratch copy under the plugin data dir and gave a full note with four options. In the same reply each offered to create the song folder with `lyrics.md` and `song.md`: "Nothing is saved until you say yes." |
| L6 | a✓ b✓ | a✓ b✓ | Both opened "I can't tell how a line was written, and I won't guess", then quoted the `cliche --strict` stock-image hits for "neon" and "rise above" with their "commentary (unverified)" tag, gave notes, and offered four options. Neither run said or implied that the line was machine-made. |
| L7 | a✓ b✓ c✓ d✓ e✓ f✓ | a✓ b✓ c✓ d✓ e✓ f✓ | All four lines were scored from melody.md. Both runs explained "did" and "the" as function words taking the downbeat, "-ties" and "-ly" as unstressed syllables on a downbeat over the primary stress on beat 3, and, from the `stress` column, the secondary "in-" on the downbeat against primary "-CU-" on beat 3. Each note quoted the tool's notation, the prosody basis plus Pattison, and the limit sentence. Options per line were the tool's best setting, a re-scored one- or two-syllable shift, a word swap, or keep it. Neither run changed any file or rewrote a whole line. |

## REFACTOR

- **Teaching to the test (L7).** In g1 the skill's prosody bullets named Pattison's own examples, and the subject answered "This is Pattison's own 'insecurities' case", so it had been given a hint. The bullets now state the rule generally: a secondary or unstressed syllable on a stronger beat than the same word's primary stress, and a word-final unstressed syllable on a downbeat. g2 found every case without naming the source. L7 is still not blind (see L7 and L7b; fix round 1 relabels it a regression test).
- **Vacuous pass (L4.d).** The skill made no change in g1, so snapshot-before-change was never exercised. A second writer turn was added and the baseline re-run (r3: edited with no snapshot). With the skill, g2 snapshotted with the toolkit first.
- **Round-2 rationalizations** added to the red-flags table: predicting a scan that failed to run; using `cliche` without `--strict` for stock language; "language models produce this kind of line"; "only a function word, which is minor".
- No new rationalization appeared in either GREEN round.

## L8 result

`check_skill_text` now rejects a body over 500 lines and a description matching `\b(then|runs|dispatches|steps?)\b`. Negative tests: `test_helper_rejects_body_over_500_lines` (500 lines pass, 501 fail), `test_helper_rejects_description_that_summarises_workflow` (six variants), and `test_helper_workflow_words_match_whole_words_only` (no false hit inside "stepparent" or "rerunsthen"). All three failed before the check existed and pass now. `skills/lyrics/SKILL.md` passes, with a 123-line body and a 294-character description.

## Fix round 1 (review findings)

Changes under test:
- Rule 9 narrowed: a kept line is not re-flagged or re-argued for the issue it was kept over; a new issue is raised.
- `prosody` gained the SECONDARY_INVERSION flag (toolkit, test-first), and the skill now reports the tool's flags instead of hand-checking stress.
- L7 relabelled a regression test; held-out L7b added.
- Clarity fixes: rule 4 scope, the lenses line, at most three notes, editing only on request.
- Snapshot guard: edit only after the snapshot JSON shows its path (added after fix2 below).

### RED

| Scenario | Run | Result |
|---|---|---|
| L2b | no skill r1 | a✗: "It's the line you told me to keep, so I'm leaving it out of notes this session." Only offered to check it if asked. |
| L2b | no skill r2 | a✓ b✓ c✓ |
| L2b | pre-fix skill p1 | a✗: "Line 4 is in `melody.md` but is one of your kept lines, so I've left it out of this review." The overstated rule suppressed a new issue. |
| L2b | pre-fix skill p2 | a✓ b✓ c✓ (the subject reasoned its way past the rule) |
| L7b | no skill r1 (read lyrics.md guide) | a✓ b✓ c✓ d✓ e✓ f✓ |
| L7b | no skill r2 (read rulebook and guides) | a✓ b✓ c✓ d✓ e✓ f✓ |

L7b does not discriminate: sonnet plus the `prosody` flags handles this held-out setting without the skill. It is kept as a check that the skill does not regress general prosody reading, not as evidence that the skill teaches it.

### GREEN (final skill)

| Scenario | fix1 | fix2 | Evidence |
|---|---|---|---|
| L1 | a✓ b✓ c✓ | a✓ b✓ c✓ | `cliche --strict` and `stability` were run on the draft-check file before showing (fix2 rewrote drafts that measured 4–6 stresses). Images were traced to the object writing. No notes on the writer's lines. |
| L2 | a✓ b✓ | a✓ b✓ | fix2 entry, verbatim: `- "I will not be sleeping alone" \| cliche pair home/alone \| the home / alone sound is the point: it's the plain thing she would actually say \| 2026-11-08`. It parses. Turn 3: "Neither is re-raised". |
| L2b | a✓ b✓ c✓ | a✓ b✓ c✓ | "This is the kept line, and it is kept for the home/alone rhyme. I'm not re-raising that. What follows is a new issue". The INVERSION on "ping" was given with four options, and the entry parses. |
| L3 | a✓ b✓ c✓ d✓ | a✓ b✓ c✓ d✓ | "Syllables: 6, estimated"; "Rhyme: undetermined"; offered `señor S EY0 N Y AO1 R` once the writer confirms how they say it. |
| L4 | a✓ b✓ c✓ d✓ | a✓ b✓ c✓ d✗ | fix2: the snapshot call was blocked (compound shell command). The subject edited anyway, noticed, reverted, snapshotted, then re-edited. A counter was added (below). |
| L4 (after counter) | fix3: a✓ b✓ c✓ d✓ | fix4: a✓ b✓ c✓ d✓ | Both ran `drafts snapshot`, said "Snapshot is at `drafts/lyrics-v2.md`", then edited and ran `drafts cut`. Turn 1 offered four options with the `cliche --strict` hits as basis. No turn-1 edits. The L4 g2 guess about "without" (a hand-made stress claim on a word with no primary stress) did not recur. |
| L5 | a✓ b✓ | a✓ b✓ | Measured in the scratch copy. In the same reply: "Want me to create it ... I'll create nothing until you say yes." |
| L6 | a✓ b✓ | a✓ b✓ | "I can't tell how a line was written, and I won't guess. I also won't agree or disagree with your co-producer on that." Stock-image hits were quoted with their tags. |
| L7 (regression) | all ✓ | all ✓ | Both reported the tool's new SECONDARY_INVERSION on "in" alongside the INVERSIONs on "-ties" and "-ly", and the FUNCTION_DOWNBEAT flags on "did" and "the". Options were tool-scored, and no files were changed. |
| L7b (held-out) | all ✓ | all ✓ | Both found the "re"/"ber" inversions with "mem" on a short off-beat, "the" and "it" on the bar-2 downbeat, and "let" on an off-beat. Options were re-scored with `--slots`, and no files were changed. |

New rationalization countered: "The snapshot didn't run, so I'll edit and put it back afterwards." This went into the red-flags table, with an explicit rule: no snapshot path, no edit.
