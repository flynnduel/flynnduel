# /newsong pressure tests

Method: writing-skills RED → GREEN → REFACTOR (see `.superpowers/sdd/2026-11-08-songwriter-skills/skill-method.md`).

Each scenario runs in a fresh scratch project (`scratchpad/skilltests/newsong/<scenario>-<tag>/`). Setup is a copy of `songtools/tests/fixtures/sample_song` at `songs/porch-light-left-on/`, with `## Core` extended by `entry: lyric`, `mode: editing`, `lenses: pattison`, `status: working` and `title: Porch Light Left On`, then edited as each scenario says. "Idea fields" means the scenario also adds `point`, `singer`, `listener`, `moment`, `central image`, `unresolved`, `pov` and `form`.

Test subject: a fresh `claude -p --model sonnet` session in the scratch project. Edits are allowed only inside that folder; Bash is limited to commands that start with `uv run` or `UV_PROJECT_ENVIRONMENT=` (the toolkit forms) and to `ls`, `mkdir`, `printf`, `echo` and `date`. `cat`, `grep`, `find`, `head`, `tail`, Glob and Grep are disallowed (files are read with the Read tool), and a compound command (`;`, `&&`, `cd`, a pipe, a shell variable) is refused whatever it starts with. Permission denials did happen: 25 of the 26 runs recorded in Task 10's first round had at least one. Most were refused `cat`, `grep`, `find` or compound commands, which the subject redid with Read or as a plain command. Three GREEN runs had a toolkit call refused: B1-g1 and B1-g2 ran `song` with `${CLAUDE_PLUGIN_DATA}` left unsubstituted in the promotion turn, and N1-g3 added `; echo exit $?`; each re-ran the same call in an allowed form and got its result. RED subjects had compound toolkit calls refused (`... | tail`, `$T chart ...`, `cd ... &&`) and re-ran them plain; RED attempts to list or read the plugin folder were refused by design. A plain toolkit call in either allowed form was never refused. The fix round's denials are listed with its results below. Every subject gets this line: "You are helping a songwriter in this folder. The toolkit is available as `uv run --frozen --project /home/user/flynnduel/songwriter-plugin/songtools songtools`." RED subjects get nothing more than that line and the writer's message, and the plugin folder is not added as a working directory, so they cannot read the guides. GREEN subjects also get the SKILL.md text, with `${CLAUDE_PLUGIN_ROOT}` replaced by the plugin path and `${CLAUDE_PLUGIN_DATA}` by a scratch path, introduced as "The writer invoked the /newsong skill." Multi-turn scenarios resume the same session; the writer's turns are scripted in advance, and the project folder is copied after every turn.

Each criterion is judged from the subject's tool calls, its replies and a diff of the project folder before and after. The evidence below is a summary; full transcripts are not kept in the repo. Today's date in every run is 2026-11-09.

## Scenarios

### N1: "I've got a riff in DADGAD"

- Setup: the porch-light song with idea fields (an unrelated song already in the project). No other song.
- Writer: "I've got a riff in DADGAD, a rolling, droning thing, roughly 110 bpm. No words and no title yet. Set up a new song for it and get me going, I've only got twenty minutes before I have to head out."
- Pass criteria (brief, verbatim: "The entry is set to riff. Next steps are reordered (music first). The song folder is created with the correct core keys."):
  - N1.a A new folder `songs/<slug>/` is created, `songs/porch-light-left-on/` is untouched, and the new `song.md` has `entry: riff or groove` (the rulebook's name for the riff entry).
  - N1.b The new `## Core` has `mode: drafting`, `lenses: pattison`, `status: working` and the writer's tempo (110), one `key: value` line each, and no key, capo or voice range the writer did not give; `songtools song` exits 0 on it (run by the subject and re-checked).
  - N1.c The next steps are music first, in the riff order of process.md (feel, key and tempo; section map; melody; words fitted to the rhythm; the chart early), and the next stage is named by its skill (`/chords`, `/structure`, `/melody`, ...).
  - N1.d (added; rule 5) No riff, tab, progression, lyric or title is invented, in the reply or in a file; the tuning and the riff are recorded in the writer's words.
  - N1.e (added; "never re-asks what the files already answer") At most one question to the writer, and none about something the writer already said (tuning, tempo, words, title).

### N2: resume

- Setup: the porch-light song with idea fields and `status: working`; `music.md` and `melody.md` removed and the inline chords stripped from `lyrics.md`, so it has lyrics but no music (`key`, `capo`, `tempo` and the voice range stay in `## Core`).
- Writer: "New song session: Porch Light Left On. I've been away from it for a couple of weeks and honestly can't remember where I got to. Ask me whatever you need and let's get going."
- Pass criteria (brief, verbatim: "The plugin finds where the song stands from the files and proposes the next missing stage. Nothing is re-asked."):
  - N2.a It reads the song's files and states where the song stands from them: idea fields and form set, lyrics in all sections, no chords, no melody, no `music.md`.
  - N2.b It proposes the next missing stage, music, fitted to the existing lyrics (entry `lyric`), naming the skill (`/melody` or `/chords`).
  - N2.c Nothing is re-asked: no question whose answer is in the files (title, point, singer, listener, form, key, tempo, voice range, entry, mode).
  - N2.d (added) No new folder or duplicate song is created and no song file changes (a "new song" for an existing title resumes it).

## RED: baseline (no skill)

A first RED round was discarded: those subjects could read the plugin folder, and one read this file's pass criteria. In the recorded round the harness denies Read on `/home/user/flynnduel/**` and removes Glob and Grep, so no RED subject read a guide or a skill. Key: ✓ pass, ✗ fail, ~ partial.

| Scenario | r1 | r2 | How it failed |
|---|---|---|---|
| N1 | a✗ b✗ c~ d~ e✗ | a✗ b✗ c~ d✓ e✓ | r1 wrote `songs/dadgad-riff/song.md` with `entry: music`, `status: sketch`, no `lenses`, "I guessed key D", and empty `title: `, `point: `, `form: ` lines; a twenty-minute plan with no skill named; four questions plus a closing one. r2 made `untitled-dadgad-riff/` at the project root (outside `songs/`), a song.md with no `## Core`, `status: riff only, no words, no title`, plus `notes.md` and a `# Lyrics (none yet)` file; it advised "a first line of about 6–8 syllables"; one question, no skill named. Both put music first. |
| N2 | a✓ b✗ c✗ d✓ | a~ b✗ c✗ d✓ | Both summarised song.md well, then asked numbered question lists (r1 four, r2 five) instead of proposing the next stage. Both asked whether there is a melody or a guitar idea ("Do you have a melody or guitar idea for the chorus yet, or is this still words only?"), which the missing `music.md` and `melody.md` already answer. Both critiqued the bridge and chorus unasked. r2 never said the music was missing. |

Rationalizations seen (in substance): a guessed key or status is fine if flagged; blank keys "fill the blanks"; a list of questions "answer only the ones you remember" is lighter than one; a plan in minutes replaces naming the next stage.

## GREEN: with the skill

Several first GREEN runs were cut off by a usage limit and re-run unchanged (N1-g2, N2-g1); the evidence below is from complete runs only.

| Scenario | g1 | g2 | Evidence |
|---|---|---|---|
| N1 | a✓ b✓ c✓ d✓ e✓ | a✓ b✓ c✓ d✓ e✓ | Both created `songs/untitled-dadgad-riff/` with `# Untitled` and Core `entry: riff or groove`, `mode: drafting`, `lenses: pattison`, `status: working`, `tempo: 110` (nothing else), and `music.md` holding `tuning: DADGAD` and `riff: a rolling, droning thing`; `songtools song` exit 0 (re-checked with `parse_song_md`). Both listed the riff order with skills (`/chords` and `/arrange`, `/structure`, `/melody`, `/idea`, `/lyrics`, `/chart`) and recommended `/chords`. "I haven't written any riff, chords, words or title." One question each (g1 "Which do you want to start with?", g2 "what key does the riff sit in, or should we find it together?"). porch-light untouched. |
| N2 | a✓ b✓ c✓ d✓ | a✓ b✓ c✓ d✓ | Both ran `songtools song`, listed the folder and marked stages: idea and form done, words in four sections, "Melody: missing. There's no `melody.md`", "Chords: missing. There's no `music.md`, and `lyrics.md` has no inline chords". Both named `/melody` next in the lyric-first order, then `/chords`, `/arrange`, `/chart`, with one question. No file changed. |

## REFACTOR

A /bank promotion run (B1-g2, which follows this skill) ended "Want to start with `/idea`? One question to open it: ...", two questions. Added: "End the reply with at most one question; offering the first stage is that question", and a red-flag row. Re-run: N1-g3 a✓ b✓ c✓ d✓ e✓ (one question, "Want to go there?"); B1-g3 and B1-g4 turn 2 each end with the single offer.

## Fix round 1 (review findings)

Harness as above, with one change for RED runs of an earlier skill version: the subject is given that version's SKILL.md (commit `eec373f`) and, for N3 and K2, the guides of the same commit from a scratch `git worktree`, so that a guide edited in this round cannot leak the fix. A first batch of GREEN runs was lost (the harness script was edited while they ran and they produced no output); it was re-run whole and only the re-run (tag f2) is recorded. Every run below had one or two permission denials, all of them compound or disallowed commands (`ls -R songs | head -50`, `ls ...; cat ...`, `grep -n "key" ...`, `mkdir ... && cd ... && printf ... && uv run ...`) that the subject redid with Read or as plain commands; no plain toolkit call was refused.

### N3: chord progression, no beats (added)

- Setup: as N1.
- Writer: "New song. I've got a chord progression I keep looping on the guitar: Am, F, C, G, round and round. No words yet and no title. Set it up so I can get going."
- Pass criteria:
  - N3.a A new folder with `entry: chord progression`, `mode: drafting`, `lenses: pattison`, `status: working`, and no key, tempo or other fact the writer did not give; `songtools song` exits 0.
  - N3.b `music.md` holds the changes in the writer's words and the toolkit accepts the file: `harmony --music <song>/music.md` exits 0, and so does `chart <song> --check` (run by the judge after adding a one-line `lyrics.md`, which `--check` needs).
  - N3.c No beats, key or section invented; the order names `/chords` for the beats.
  - N3.d At most one question.

| Run | Result | Evidence |
|---|---|---|
| RED r1 (no skill) | a✗ b~ c✗ d✓ | `songs/untitled-loop/` with `key: Am`, `status: sketch`, `entry: music`, and `## Loop` / `progression: Am:4 F:4 C:4 G:4`: the beats, the section and the key are invented ("I set Am because that's where you start the loop"). The file parses only because of the invented beats. |
| RED old2 (skill and guides at `eec373f`) | a✓ b✗ c✓ d✓ | Wrote `progression: Am, F, C, G` at the top of `music.md`, as that version told it to. `harmony --music` and `midi` then exit 2: `music.md:1: progression before any '## Section' heading`. |
| GREEN f2 | a✓ b✓ c✓ d✓ | `songs/untitled-am-f-c-g/`, Core defaults only, `music.md` is `changes: Am F C G`. "It has no beats yet because you haven't given any." `harmony --music` exit 0; `chart --check` exit 0; `midi` reports `"chords": 0`. Order starts "The changes with beats, section by section: `/chords`"; one question ("Want to start with `/chords` and give the changes their beats?"). |

A run of the `eec373f` skill against this round's rulebook (N3-old) wrote `changes: Am F C G` because the edited rulebook already said so; it is not counted as RED.

### N4: only a subject, with a style named (added)

- Setup: as N1.
- Writer: "I want to write a song about loss. It's about my dad's workshop after he died. A folk song, probably. Nothing written yet, not even a title. Can you get me started?"
- Pass criteria:
  - N4.a A new folder; the reply says in one line which `entry` was recorded.
  - N4.b No `style:` line is written; saving it is offered once; no style advice is given.
  - N4.c At most one question.

| Run | Result | Evidence |
|---|---|---|
| RED old (skill at `eec373f`) | a✓ b✓ c✗ | Filed `brief or commission` and wrote no `style:`, but asked two questions: "Do you want me to save that as `style: folk` in the song file?" and "Want to start with `/idea`?" |
| GREEN f2 | a✓ b✓ c✓ | "I filed this as `brief or commission`. You brought a subject and a feeling with nothing made yet, so the subject is the brief." `## Brief` holds the writer's two sentences. "Style: you called it a folk song. Say \"save the style\" and I'll record it." One question ("Want to start with `/idea`?"). The reply dropped the writer's "probably"; nothing was saved, so no file is wrong. |

### I0: /idea with no song folder (added; the front door)

- Setup: as N1 (only the unrelated porch-light song exists). The subject is given the /idea skill.
- Writer: "I want to write a song about loss. It's about my dad's workshop after he died. Nothing written yet, not even a title. Help me work out what it's really about."
- Pass criteria: I0.a it says there is no song folder and starts with `/newsong`; I0.b it writes no file.

| Run | Result | Evidence |
|---|---|---|
| RED old (/idea at `eec373f`) | a✗ b✓ | "there's no folder yet for your dad's workshop. Nothing gets saved until you say so", then straight into the first idea question; `/newsong` is never named, so the song has nowhere to be saved. |
| GREEN f2 | a✓ b✓ | "There's no song folder for this one yet. ... Start with `/newsong`. It creates the folder, records what you've told me ... and sends you back to `/idea`." No file written. |

### N1 and N2 re-run

| Scenario | f2 | Evidence |
|---|---|---|
| N1 | a✓ b✓ c✓ d✓ e✓ | `songs/untitled-dadgad-riff/`, Core `entry: riff or groove`, `mode: drafting`, `lenses: pattison`, `status: working`, `tempo: 110`; `music.md` has `tuning: DADGAD` and `riff: a rolling, droning thing, roughly 110 bpm`; `song` exit 0. Riff order with skills, `/chords` first; "I haven't written any tab, chords or melody." One question. |
| N2 | a✓ b✓ c✓ d✓ | Ran `song`, listed the folder, marked idea and form done, words drafted, "Melody (`/melody`): missing. There's no `melody.md`", chords missing; "The melody is next. Shall we start on `/melody`?" No file changed. |

### Routing check (descriptions)

All eleven descriptions and the 32 messages below were given to sonnet with no tools, three times: "the project has songs/porch-light-left-on/ (lyrics, chords, capo 2) and songs/_bank/ideas.md. Answer with exactly one skill name per message." Messages 1–18 are the first round's set; 19–32 were added for the overlaps named in review (bass line, chorus lift, lyrics against critique, idea and structure, finalcheck, and a vague idea with no song).

| # | Message | Expected |
|---|---|---|
| 1 | I've got a riff in DADGAD, set up a new song for it. | newsong |
| 2 | Quick, bank this title before I forget: "Salt in the Coffee". | bank |
| 3 | Back on Porch Light Left On after two weeks. Where was I? | newsong |
| 4 | I want to write a song about loss. Help me work out what it's about. (no song folder yet) | newsong |
| 5 | Make me a PDF chart of Porch Light for the band. | chart |
| 6 | What should the drummer do in the second chorus of Porch Light? | arrange |
| 7 | Let's start that Salt in the Coffee song from my bank. | newsong |
| 8 | Can you check the chorus of Porch Light for cliches? | lyrics |
| 9 | I need a concert-pitch copy for the bass player, I play with capo 2. | chart |
| 10 | Here are some lyrics I wrote, I want to turn them into a song: "..." | newsong |
| 11 | What's next for Porch Light? | newsong |
| 12 | Jot down this line for later: "the kettle knows I'm lying". | bank |
| 13 | Is Porch Light ready to demo? | finalcheck |
| 14 | What chord should go under "home" in the chorus? | chords |
| 15 | Make me a road map for the band for Porch Light. | arrange |
| 16 | Show me the titles I've banked. | bank |
| 17 | Make me a MIDI guide track of the chords. | chart |
| 18 | Is my chart still matching the lyrics after I changed verse 2? | chart |
| 19 | Can you write me a bass line for the chorus of Porch Light? | chords |
| 20 | I need a drum part to hand to my drummer for Porch Light. | arrange |
| 21 | The chorus of Porch Light doesn't lift. Why? | structure |
| 22 | How do I make the chorus melody of Porch Light stand out? | melody |
| 23 | Give me honest feedback on the whole lyric of Porch Light. | critique |
| 24 | Do "sink" and "think" rhyme properly in verse 1 of Porch Light, and does the stress fall right in line 2? | lyrics |
| 25 | Draft me a second verse for Porch Light. | lyrics |
| 26 | I'm not sure what Porch Light is really about any more. Help me pin down its point. | idea |
| 27 | Should Porch Light have a bridge, or just go verse, chorus, verse? | structure |
| 28 | Porch Light is still in progress, but can I get notes on verse 2 before I show my co-writer? | critique |
| 29 | I think Porch Light is finished. Give it a last look. | finalcheck |
| 30 | I just have a feeling I want to write about: homesickness. There's no song yet. | newsong |
| 31 | Porch Light feels flat and samey all the way through. | structure |
| 32 | The melody of Porch Light is flat and boring. | melody |

- RED (descriptions at `eec373f`): 90 of 96 answers as expected. Messages 4 and 30 went to `idea` in all three runs: a vague idea with no song folder bypassed `/newsong`. (In the first round message 4 was expected at `idea`; the review changed that.)
- GREEN (descriptions of this round, each with a reciprocal "Not when ... (skill)" clause): 96 of 96 as expected, all three runs identical.
- The structure test `test_description_is_short_and_says_when_not_to_use_it` holds every description under 500 characters with a "Not when" clause that names other skills, and `test_overlapping_skills_exclude_each_other` checks eleven overlapping pairs in both directions. Both failed before the descriptions were edited (9 failures).

