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
