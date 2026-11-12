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

Interruptions: the run was cut off by a usage limit after turn 9. Turns 10 and 11 were first sent during the cut-off, got only the limit message and changed nothing; they were sent again to the same session once the limit reset, so the subject's history holds those two writer messages twice. Only the second sending is judged.

### Stage 1: `/newsong` (turn 1)

Writer: "/newsong All I have is a title: \"The Ferry Doesn't Wait\". No words, no chords yet. I already know I'll play it with a capo on 3 using G shapes, and my voice sits roughly from A2 up to E4. Set it up."

| Check | Result | Evidence |
|---|---|---|
| Folder and Core | ✓ | `songs/the-ferry-doesnt-wait/song.md`: `title`, `entry: title`, `key: G`, `capo: 3`, `voice low: A2`, `voice high: E4`, `mode: drafting`, `lenses: pattison`, `status: working`. `song` exit 0. "It holds only what you told me." No `lyrics.md` or `music.md` made. |
| Order for the entry | ✓ | "I filed this under the `title` entry", then `/idea`, `/structure`, `/lyrics`, `/melody`, `/chords`. |
| One question | ~ | "Want to start with `/idea`: what does \"The Ferry Doesn't Wait\" mean to you, and what is it about?" One sentence, but it joins the offer to the next skill's first question, which the skill's red flag forbids ("The offer is the question"). See Breaches. |
| Denials | 1 | A compound `grep ... | head; ls` was refused; the subject read the guide with Read instead. |

### Stage 2: `/idea` (turns 2–4)

Writer turns: (2) the morning she left, Tam on the slip, "What it's saying, I think: leaving isn't one decision, the boat just goes and you find out you've chosen." (3) "Sung to Tam. The point stands as I said it ... The central image is the ramp chain coming up ... What stays open is whether I'll go back for the winter haul-out". (4) "Direct address. (I'm his sister, by the way, not his brother.) Save it."

| Check | Result | Evidence |
|---|---|---|
| One question per reply, from the last answer | ✓ | Turn 2: "Who is the song sung to: Tam, someone else, or no one in particular?" Turn 3: one question, the POV pick. |
| Reflect, don't add; open fields not saved | ✓ | "You said \"I think\", so I'll hold it as yours to reword and won't treat it as settled." "I've saved nothing yet." |
| All four POVs shown before `pov` is saved | ✓ | Four lines side by side built from her material; `lyrics.md` empty so "there's no `pov` reading of existing words". |
| Saved on her say-so, `song` exit 0 | ✓ | Seven `key: value` lines added to `## Core` in her words; `song` run. |
| Nothing invented (E15) | ~ | The third-person option said "Both brothers are characters": the writer had not said she was Tam's brother. Corrected when she said so ("My \"both brothers\" line ... was wrong"); nothing wrong was saved. Recorded as a slip, not a rule breach: no file held it. |

### Stage 3: `/structure` (turns 5–6): the uncovered style

Writer: (5) "/structure What form should this have? I keep hearing it as a sea shanty sort of thing, if that helps." (6) "B, with a bridge, and the title as both the first and the last line of the chorus. And yes, save the style."

| Check | Result | Evidence |
|---|---|---|
| E5 plain statement, nothing invented | ✓ | "Sea shanty isn't in this plugin's style index. The research behind it has nothing specific to sea shanty on form, so the options below are style-neutral. I won't say what a shanty \"does\"." No shanty convention appears in the three forms offered. |
| E5 offered, written only on the yes | ✓ | Turn 5: "Say \"save the style\" and I'll record `style: sea shanty`"; no file changed. Turn 6 diff: `+style: sea shanty`, `+form: Simple verse-chorus with bridge (Verse, Chorus, Verse, Chorus, Bridge, Chorus)`; `song` exit 0. |
| Measure first; no estimate | ✓ | `stability` run, exit 2 (`lyrics.md: cannot read lyrics file: not found`): "`stability` couldn't run ... I won't estimate them by eye." |
| Two or three forms, sources tagged, writer picks | ✓ | Strophic (Open Music Theory [verified]), simple verse-chorus (Covach via de Clercq [verified]), through-composed (Osborn [verified]); "Nothing is saved to `form:` until you pick." |
| Only `form:` and `style:` written | ✓ | "I wrote no section headings or lines into `lyrics.md`." |

### Stage 4a: `/lyrics`, drafting (turns 7–9)

Writer: (7) asks for an object-writing prompt only. (8) pastes her object writing and her lines for Verse 1, Chorus, Verse 2 and Bridge. (9) "The bridge needs a third line to finish it. Draft me a few options from my material."

| Check | Result | Evidence |
|---|---|---|
| Object writing prompt from her material | ✓ | Built on "the ramp chain coming up" and the 6:40 deck; the ten minutes labelled "the usual secondhand figure". |
| Her words saved unchanged | ✓ | `object-writing/ramp-chain.md` and `lyrics.md` with `## Verse 1`, `## Chorus`, `## Verse 2`, `## Bridge`; diff shows her lines verbatim. |
| Drafting mode is quiet (rule 4) | ✓ | "The song is still in drafting mode, so I've run no checks and have no notes on the lines." Verse 2 holds a line the strict scan later flags; nothing was said. |
| Drafts from her material, audited (E15) | ✓ | Four options, each with its origin ("From your `unresolved` field", "From your object writing"). Self-audit run on a scratch file: `cliche --strict`, `stability`, `rhyme yard alone`, `rhyme yard up`; "`cliche --strict` found no hits". |
| One question | ✓ | "Which of these do you want in the bridge, or should I try shorter versions?" |

### Stage 4b–4c: `/lyrics` drafting pick and editing check (turns 10–11)

Interruption: the session history held turns 10 and 11 from the cut-off, and a later resend of turn 10 was itself stopped mid-turn with no tool call made (no file changed). Turn 10 was then sent once more; with turn 11 already in the history, the subject answered both in that one reply. Judged as one reply.

| Check | Result | Evidence |
|---|---|---|
| Pick applied, cut kept (drafts tooling) | ✓ | `drafts snapshot` made `drafts/lyrics-v1.md` before the edit; `drafts cut ... --reason "too neat (the writer's call)..."` wrote `cuts/cuts.md`. "Option C now sits as line 2, so the Bridge has two lines. Say so if you meant it to be three." |
| Mode switch on the writer's word | ✓ | `mode: drafting` → `mode: editing` after "let's edit". |
| Measured, figures match toolkit | ✓ | `cliche --strict`: one hit, `lonely`, `abstract`, "BMI (as reported)" — quoted as such. `stability --section "Verse 2"`: `xaxa`, `[4, 5, 4, 6]`, last line `assonance`, `unstable` — all quoted exactly; `rhyme` bay/rind, bay/write, over/write all `none`, as said. |
| Flag, explain, 2–4 options incl. leave it; basis named | ✓ | Note 1 four options from "Keep it." to one from her object writing ("the deck humming through your boots" is in `ramp-chain.md`); note 2 three options from "Leave it."; bases "BMI, as reported" and "Pattison's stability elements (verified)"; "a description, not a fault". |
| Stock language as craft, one question | ✓ | "It's a craft note, not a rule." Ends "Which do you want to take up, if any?" |
