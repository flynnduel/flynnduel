# /newsong pressure tests

Method: writing-skills RED → GREEN → REFACTOR (see `.superpowers/sdd/2026-11-08-songwriter-skills/skill-method.md`).

Each scenario runs in a fresh scratch project (`scratchpad/skilltests/newsong/<scenario>-<tag>/`). Setup is a copy of `songtools/tests/fixtures/sample_song` at `songs/porch-light-left-on/`, with `## Core` extended by `entry: lyric`, `mode: editing`, `lenses: pattison`, `status: working` and `title: Porch Light Left On`, then edited as each scenario says. "Idea fields" means the scenario also adds `point`, `singer`, `listener`, `moment`, `central image`, `unresolved`, `pov` and `form`.

Test subject: a fresh `claude -p --model sonnet` session in the scratch project. Edits are allowed only inside that folder; Bash is limited to `uv run` / toolkit calls (including the `UV_PROJECT_ENVIRONMENT=... uv run` form, checked to be allowed: no run had a permission denial) and simple read-only commands (`ls`, `cat`, `grep`, `find`, `date`, `mkdir`). Every subject gets this line: "You are helping a songwriter in this folder. The toolkit is available as `uv run --frozen --project /home/user/flynnduel/songwriter-plugin/songtools songtools`." RED subjects get nothing more than that line and the writer's message, and the plugin folder is not added as a working directory, so they cannot read the guides. GREEN subjects also get the SKILL.md text, with `${CLAUDE_PLUGIN_ROOT}` replaced by the plugin path and `${CLAUDE_PLUGIN_DATA}` by a scratch path, introduced as "The writer invoked the /newsong skill." Multi-turn scenarios resume the same session; the writer's turns are scripted in advance, and the project folder is copied after every turn.

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
