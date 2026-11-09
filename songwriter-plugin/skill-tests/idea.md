# /idea pressure tests

Method: writing-skills RED → GREEN → REFACTOR (see `.superpowers/sdd/2026-11-08-songwriter-skills/skill-method.md`).

Each scenario runs in a fresh scratch project. Test subject: a fresh `claude -p --model sonnet` session in the scratch project (`scratchpad/skilltests/idea/<scenario>-<tag>/`). Edits are allowed only inside that folder; Bash is limited to `uv run` / toolkit calls and simple read-only commands. Every subject gets this line: "You are helping a songwriter in this folder. The toolkit is available as `uv run --frozen --project /home/user/flynnduel/songwriter-plugin/songtools songtools`." RED subjects get nothing more than that line and the writer's message; the plugin folder is not added as a working directory, so they cannot read the guides. GREEN subjects also get the SKILL.md text, with `${CLAUDE_PLUGIN_ROOT}` replaced by the plugin path and `${CLAUDE_PLUGIN_DATA}` by a scratch path, introduced as "The writer invoked the /idea skill." Multi-turn scenarios resume the same session; the writer's turns are scripted in advance, and the project folder is copied after every turn.

Each criterion is judged from the subject's tool calls, its replies and a diff of the project folder before and after. The evidence below is a summary; full transcripts are not kept in the repo.

## Scenarios

### I1: vague idea "a song about loss"

- Setup: a new song folder `songs/untitled/` holding only `song.md` with `# Untitled` and a `## Core` of `entry: brief or commission`, `mode: drafting`, `lenses: pattison`, `status: working`. No `lyrics.md`.
- Writer, six scripted turns (each is sent whatever the subject asked last):
  1. "I want to write a song about loss. That's all I've got, honestly. Can you just fill in the idea stuff in song.md for me so I can start writing lyrics tonight? Whatever sounds good."
  2. "Ugh, okay. It's my dad. He died last winter, and in March we sold his house and I had to clear out his workshop."
  3. "I don't know. I suppose I'm singing it to him? Not to my family. Just to him."
  4. "The last afternoon in the workshop. Sweeping sawdust off his bench before the buyers came. There's a pencil line on the doorframe where he measured me every birthday, and I left it there."
  5. "I still don't know if I should have taken the bench. It's in a stranger's garage now. That's the thing I can't settle."
  6. "I think the point is that he measured me growing up, and I left the marks behind for strangers. Talking straight to him feels right. Go ahead and save it."
- Pass criteria (brief, verbatim: "Questions continue one at a time until the point, singer and listener, moment, image and the unresolved element are concrete. The POV check offers all four POVs. Results are saved to song.md."):
  - I1.a Questions come one at a time: no reply asks more than one question of the writer.
  - I1.b Questions continue until the point, singer, listener, moment, central image and unresolved element are concrete; nothing is saved while one is still vague.
  - I1.c The POV check offers all four points of view (direct address, second-person narrative, first-person narrative, third-person narrative) before the POV is saved.
  - I1.d The results are saved to `song.md`'s `## Core`, one `key: value` line per field, and `songtools.songfile.parse_song_md` still reads the file (checked by running it).
  - I1.e (added; rule 5 and drafting.md "never invent generic scenery") No idea field is filled with content the writer did not give: turn 1's "fill it in for me, whatever sounds good" gets a question, not an invented idea. A title the writer has not given is offered as options or left open, not saved as settled.

## RED: baseline (no skill)

Two baseline runs (r1, r2), without the plugin folder as a working directory; neither read a guide. Key: ✓ pass, ✗ fail, ~ partial.

| Scenario | r1 | r2 | How it failed |
|---|---|---|---|
| I1 | a✗ b✗ c✗ d✗ e~ | a✗ b✗ c✗ d✓ e✗ | Turn 1 of both declined to invent the loss, but asked several questions at once (r1: "Three quick questions would let me write something true to you", plus "say 'surprise me' and I'll write it up"; r2: four numbered questions). r1 wrote to `song.md` from turn 2 on, into a new `## Idea` section of paragraphs: a premise, a turn, hook candidates and "Working title ideas: Workshop / March / Everything Must Go", labelled "proposed". r2 saved "a first-pass point" in turn 2, marked as a proposal, and set the listener to "Dad, directly" in turn 3. Neither ever showed the four points of view. r2's `## Core` lines carry notes inside the values ("(writer's own words; confirmed)") and still parse. |

Rationalizations seen (in substance): several questions at once are quicker; "surprise me" licenses inventing the idea; proposals are fine in the record if labelled; a field can be saved early and revised; the listener settles the point of view without comparing the four.

## GREEN: with the skill

| Scenario | g1 | g2 | Evidence |
|---|---|---|---|
| I1 | a✓ b✓ c✓ d✓ e✓ | a✓ b✓ c✓ d✓ e✓ | Turn 1, both: "I won't fill them in. A loss I invent would be my song, not yours", then one question ("who or what is gone?"). Every later reply asked one question (g1 turn 5: "Does that come close ..., or how would you put it in your own words?", one question with an alternative). Each reply reflected the answer in the writer's words and named the field it filled; readings were offered "as an option, not a field value". g1 held `singer` open after "I suppose". Nothing was written before turn 6. g2 showed all four points of view in turn 3, built from the writer's material, and asked for confirmation; g1 showed all four in turn 6 and saved the six concrete fields with `pov` left open until the writer confirms. Both wrote one `key: value` line per field in `## Core`, ran `songtools song` (exit 0), left the title open (g2 offered "Pencil Line", "The Bench", "Before the Buyers Came", each traced to a field). `parse_song_md` reads both files (g2 core includes `pov: direct address`). |

No new rationalization appeared, so no REFACTOR round was needed for /idea.

## Toolkit addition (test-first): `songtools song`

`/idea` writes to `song.md` before any `lyrics.md` exists, and no subcommand parsed `song.md` on its own (`drafts diff ... --song` needs a lyrics file: "song.md:1: lyric line before any '## Section' heading"). Test-first, `songtools song SONG_MD` prints the title, `## Core`, kept lines, split sheet and other section names, and exits 2 naming a bad line. RED: 3 of 4 new tests in `tests/test_songfile.py` failed ("invalid choice: 'song'"). GREEN: 28 passed in `test_songfile.py`. `guides/toolkit.md` documents it; `/idea`, `/structure` and `/arrange` use it.

## Fix round 1 (review findings)

Changes: saving replaces an existing key's line instead of adding a second (the toolkit now rejects a duplicate `## Core` key). A chosen title also updates the `# ` heading. I1 re-run on the changed skill:

| Scenario | Run | Result |
|---|---|---|
| I1 | h1 | a✓ b✓ c✓ d✓ e✓: one question per reply; nothing saved before turn 6; six concrete fields saved as single lines, `songtools song` exit 0; the four points of view shown in turn 6 with `pov` held open; title left open, so the heading stayed `# Untitled`. |
