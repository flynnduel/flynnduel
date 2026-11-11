# End-to-end run: one new song through all eleven skills

One test subject takes one original song from `/newsong` to `/finalcheck` in a single session. This file holds the scripted writer turns, the pass criteria, and the results stage by stage with short quoted evidence. Full transcripts are not kept in the repo, and the song's lyrics are quoted only a line at a time.

## Method

- Test subject: one `claude -p --model sonnet` session, resumed for every writer turn (`--resume`), in a fresh scratch project that starts with an empty `songs/` folder.
- The subject gets the setup line used by every skill test ("You are helping a songwriter in this folder. The toolkit is available as `uv run --frozen --project /home/user/flynnduel/songwriter-plugin/songtools songtools`."), then: "The songwriter plugin is installed. Its eleven skills follow. When the writer invokes a skill as /name, follow that skill's instructions. When a message names no skill, follow the skill whose description fits it." and the eleven SKILL.md texts, each in a `<skill name="...">` block, with `${CLAUDE_PLUGIN_ROOT}` replaced by the plugin path and `${CLAUDE_PLUGIN_DATA}` by a scratch path. This is passed as an appended system prompt on every turn, so it survives a long session.
- Permissions are those of the earlier skill tests: Read, Write and Edit; Bash limited to commands starting `uv run` or `UV_PROJECT_ENVIRONMENT=` (the toolkit forms) and to `ls`, `mkdir`, `printf`, `echo`, `date`; `cat`, `grep`, `find`, `head`, `tail`, Glob and Grep disallowed; the plugin folder readable except `skill-tests/`, `docs/`, `reports/`, `research_notes/` and `README.md`.
- The writer's turns are scripted below in advance. The controller plays the writer and may reword a turn only to answer the question the subject actually asked; the wording as sent is what is recorded. The project folder is copied after every turn, and each criterion is judged from the subject's tool calls, its replies and the folder diff.
- The song is original (written for this test; nothing published). The writer's material is the controller's.
- To rebuild: make an empty project with `songs/`, send the turns below in order to one resumed session with the system prompt above. The scratch project of the recorded run lived at `scratchpad/e2e/project/` and is not kept.

## Scripted writer turns

| # | Stage | Writer |
|---|---|---|
| 1 | `/newsong` | Only a title, "The Ferry Doesn't Wait"; capo 3 with G shapes; voice A2 to E4. (Non-default entry: `title`; a capo, so the concert chart and `midi --concert` are exercised.) |
| 2–4 | `/idea` | Answers one question at a time: the morning she left the island, her brother Tam on the slip; the point; listener Tam; central image the ramp chain; unresolved the winter haul-out; picks direct address; "save it". |
| 5–6 | `/structure` | "What form should this have? I keep hearing it as a sea shanty sort of thing." (a style `styles.md` does not cover). Then picks a form and says yes to saving the style. |
| 7–8 | `/lyrics` (drafting) | Asks for an object-writing prompt; pastes object writing to save, and her own Verse 1, Chorus, Verse 2 and two bridge lines for `lyrics.md`. |
| 9–10 | `/lyrics` (drafting) | Asks for options for a third bridge line from her material; picks one; has one bridge line cut "but don't lose it". |
| 11–12 | `/lyrics` (editing) | "Let's edit. Check verse 2: rhyme and any stock language." Keeps the flagged line ("And the lonely sound of the Marianne turning over") with a reason. |
| 13–14 | `/melody` | "Write me the melody for the chorus." Then gives her own setting of the kept line, which puts a stressed syllable off the beat, and agrees to record it. |
| 15–17 | `/chords` | Gives her chords with beats for every section; says the song is really soul (a style `styles.md` covers), asks for other ways to end the chorus, and says yes to saving the style; picks or keeps a close. Then: "write me a bass line for the verse". |
| 18 | split sheet | "My co-writer Dana Okafor wrote the bridge with me. Split sheet: me, Rhys Calloway, words and music, 70; Dana, words, 30." |
| 19 | `/arrange` | Road map for a four-piece; save it. |
| 20 | `/chart` | Charts and guide tracks for rehearsal. |
| 21 | `/bank` | Banks an unrelated line for another song. |
| 22 | `/critique` | Asks for notes on the whole song. |
| 23–24 | `/finalcheck` | "I think it's finished." Then chooses the status herself. |

## Pass criteria

From the brief:

- E1 Every file in spec section 4 exists and parses with `songtools`: `song.md`, `lyrics.md`, `melody.md`, `music.md`, `arrangement.md`, `object-writing/`, `cuts/`, `drafts/`, `out/`, `songs/_bank/ideas.md`.
- E2 `out/` holds `chart.cho`, `chart-concert.cho`, `chart.pdf`, `chart-concert.pdf` and `guide.mid` (and, with the capo, `guide-concert.mid`).
- E3 No rule in the rulebook is broken anywhere in the transcript.
- E4 The writer sets the status.

From deferred review items:

- E5 Uncovered style (sea shanty): a plain statement that the research has nothing on it; no convention invented; saving offered, and written only on the yes.
- E6 Covered style (soul): only `styles.md` material is used as style material, each finding with its source and tag; under the declared style every frequency claim sits only in the fixed line `How common (general corpus, not <style>): ...`.
- E7 The yes to saving the second style replaces the `style:` line (one `style:` line in `song.md`; `songtools song` exits 0).
- E8 The kept line is written to `## Kept lines` in the register format and parses; it is not re-flagged for the kept issue.
- E9 A new issue on the kept line (its melody setting) is raised as a normal note that says the line is kept for the earlier issue.
- E10 `/critique` and `/finalcheck` each bring the kept line back once, in its own group, without re-arguing it.
- E11 The split sheet has numeric percentages and `songtools song` accepts it.
- E12 Asked for the chorus melody: declined in one sentence, coaching offered, no notes or rhythm handed over.
- E13 Asked for a bass line: declined, role guidance in words offered, no tab or note list.
- E14 `/finalcheck` shows all ten steps, gives no verdict, and changes `status` only after the writer chooses, to exactly her value.
- E15 Nothing invented: lyric drafts trace to the writer's material; every toolkit figure quoted in a reply matches the toolkit's output; no genre assumed.

## Results

Appended stage by stage as the run proceeds. Key: ✓ pass, ✗ fail, ~ partial.
