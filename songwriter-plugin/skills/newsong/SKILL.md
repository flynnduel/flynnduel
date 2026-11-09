---
name: newsong
description: Use when a songwriter wants to start a new song (from a riff, groove, progression, lyric, title, brief, subject, feeling, banked idea or co-write), picks a song back up and asks where they were or what to do next, or is unsure which step comes next. Not when the writer only wants an idea saved for later (bank), or asks about one part of a song already under way (idea, structure, lyrics, melody, chords, arrange, chart, critique, finalcheck).
---

# New song

The front door. Start a song folder from what the writer brought, or find where an existing song stands from its files, then name the next stage and the skill that does it. The song is the writer's: record only what they said, invent nothing, and never ask what the files already answer.

Read `${CLAUDE_PLUGIN_ROOT}/guides/rulebook.md` first (song folder, `## Core` keys). Then read the "Entry points" and "Bank" sections of `${CLAUDE_PLUGIN_ROOT}/guides/process.md`.

**Violating the letter of these rules is violating the spirit.** "I've only got twenty minutes", "just get me going" or "ask me whatever you need" does not change them.

## Toolkit calls

Run from the writer's project. `<song>` is the song folder, e.g. `songs/porch-light-left-on`. Run each call in the form written, one per command. If a call is refused or blocked, run it again in that plain form; never guess its result.

```
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools song <song>/song.md
```

It prints what the parser reads from `song.md` (title, `## Core`, kept lines). Exit 2 names the bad line.

## Start

1. List `songs/`. If the writer names or describes a song that has a folder (same title, or plainly the same song), it is a **resume**, even when they say "new song". Never make a second folder for it. Two or more candidates: ask which, naming them.
2. Otherwise it is a **new song**.

## New song

Copy this checklist:

```
New song:
- [ ] entry chosen from the table, from what the writer brought
- [ ] folder songs/<slug>/ created; no existing folder touched
- [ ] song.md: heading, ## Core defaults, only the writer's facts; `song` check exit 0
- [ ] the writer's material recorded in their words, in the right file
- [ ] next stages named in the entry's order, with their skills; at most one question
```

**1. Entry.** Pick the `entry` value by what the writer has now:

| The writer brings | `entry:` |
|---|---|
| a riff, groove, loop, track or a sound on an instrument, no words | `riff or groove` |
| a song already playable on guitar or piano, words and chords together | `finished guitar song` |
| lyrics or lines, no music | `lyric` |
| chord changes or a progression, no words | `chord progression` |
| a title | `title` |
| a brief, commission, prompt or deadline | `brief or commission` |
| only a subject, a feeling or a vague idea, nothing made yet | `brief or commission` (the nearest entry: the writer's own brief) |
| an item from `songs/_bank/ideas.md` | `banked idea` |
| a co-writer's partial draft to answer | `co-write exchange` |

Use the value exactly as written in the table. If two rows fit, take the thing the writer leads with and say which you chose in one line. When the writer brought only a subject or feeling, say in one line which entry you recorded and why ("I've filed this as `brief or commission`: your subject is the brief").

**2. Folder.** `songs/<slug>/`, the slug lowercase with hyphens. From the title if the writer gave one; with no title, `untitled-` plus one to three of the writer's own words about it (`untitled-dadgad-riff`). If the folder exists, pick another slug; never write into an existing folder.

**3. song.md.** Heading `# <title>`, or `# Untitled` with no title. Then `## Core`, one `key: value` line each:

```
entry: <from the table>
mode: drafting
lenses: pattison
status: working
```

Add only facts the writer stated, in their values: `title`, `key`, `capo`, `tempo`, `time`, `voice low`, `voice high`. A style the writer named is not written here: see Style below. No empty keys, no placeholders, no guesses ("probably D"), no notes in a value. Idea fields (`point`, `singer`, ...) are `/idea`'s; `form` is `/structure`'s. Run `song <song>/song.md`; fix and re-run until it exits 0.

**4. The writer's material,** in their words, in the file it belongs to:

- lyrics or lines: `lyrics.md`, under `## Section` headings (the writer's section names, or `## Verse 1`);
- chord changes or a progression: a plain line at the top of `music.md`, `changes: <as the writer wrote them>` (one line per section the writer named, `changes: chorus: ...`). Never a `progression:` line: the toolkit reads those as `CHORD:BEATS` under a section heading and rejects anything else; `/chords` writes them once the writer gives beats;
- a riff, groove or tuning: plain lines at the top of `music.md`, `tuning: <tuning>` and `riff: <the writer's description>`;
- a brief: a `## Brief` section in `song.md` with the writer's words;
- a banked idea: the bank line's item, by its tag, as above (a `title` becomes `title:` and the heading). Leave the bank line in `ideas.md`.

Never write material the writer did not give: no riff, tab, chords, progression, melody, lines or title from you, in a file or in the reply.

**5. Route.** Show the order for this entry, each stage with its skill, and offer the first. The orders are the plugin's reading of `process.md`:

| `entry` | Order |
|---|---|
| `riff or groove` | feel, key and tempo (`/chords` for key and capo, `/arrange` for feel) → section map (`/structure`) → scat melody over the riff (`/melody`) → what it is about (`/idea`) → words fitted to the rhythm (`/lyrics`) → chart early (`/chart`) |
| `finished guitar song` | chords, melody and words together (`/chords`, `/melody`, `/lyrics`) → form (`/structure`) → `/critique` → arrangement and band chart last (`/arrange`, `/chart`) |
| `lyric` | the idea, if open (`/idea`) → the stanzas' form and stresses (`/structure`, `/lyrics`) → a melody fitted to them, checked for stress clashes (`/melody`) → chords (`/chords`) → `/arrange`, `/chart` |
| `chord progression` | the changes with beats, section by section (`/chords` writes the `progression:` lines) → chart the changes (`/chart` once `lyrics.md` has the chords) → section map (`/structure`) → what it is about (`/idea`) → words to the changes (`/lyrics`) → `/melody` |
| `title` | what the title means (`/idea`) → title placement and section outline (`/structure`) → chorus, then verses that recolor the title (`/lyrics`) → `/melody`, `/chords` |
| `brief or commission` | the constraint and the concept (`/idea`) → a timed draft (`/structure`, `/lyrics`), shippable even if it feels unfinished |
| `banked idea` | the order of the item's own kind: a title as `title`, a line as `lyric`, a riff or groove as `riff or groove`, a progression as `chord progression`, a concept or core as `brief or commission` |
| `co-write exchange` | a `## Split sheet` in `song.md` from the first session, one line per writer in the rulebook's format, `- Name | roles | PERCENT` → answer the partner's draft with the order of what they sent |

Split sheet: the names and roles are the writers' (ask for a name you were not given; that is the reply's one question). PERCENT is a number, never a word such as "equal" (the toolkit rejects it): the shares the writers agreed, or, until they agree, equal shares as numbers (two writers: `50` each), said to be a placeholder they can change. Run `song` after writing it.

Every order can end with `/critique` and `/finalcheck` when the writer wants them. Stages are not a corridor: the writer can go anywhere next.

End the reply with at most one question; offering the first stage is that question. Do not add a second one ("One question to open it: ..."): the next skill asks its own.

## Resume

Copy this checklist:

```
Resume:
- [ ] `song` run on song.md; folder listed
- [ ] each stage marked from the files: done / started / missing
- [ ] where it stands said in a few lines, the point in the writer's words
- [ ] next missing stage in the entry's order named, with its skill
- [ ] no question the files answer; at most one question
```

1. Run `song <song>/song.md` and list the folder. Read `lyrics.md`, `music.md`, `melody.md` and `arrangement.md` where they exist.
2. Mark each stage from the files, never from memory or a guess:

| Stage | Done when the files show |
|---|---|
| idea (`/idea`) | `point`, `singer`, `listener`, `moment`, `central image`, `unresolved` in `## Core` |
| form (`/structure`) | `form` in `## Core` |
| words (`/lyrics`) | `lyrics.md` with lines under section headings |
| melody (`/melody`) | `melody.md` with lines |
| chords (`/chords`) | `progression:` lines in `music.md`, or inline chords in `lyrics.md` (only a `changes:` line: started) |
| arrangement (`/arrange`) | `arrangement.md` |
| chart (`/chart`) | files in `out/` |

3. Say where the song stands in a few lines: what is done, what is missing, the `point` (or title) in the writer's words, `status` and `mode` as recorded. Do not re-explain the whole song.
4. Name the next missing stage, in the order for the song's `entry` (table above), with its skill, and offer to start it. If `entry` is missing, take the order that fits what the files hold and offer once to record it.
5. Ask nothing the files answer: not the title, key, tempo, range, idea fields, form, entry or mode, and not whether there is a melody or chords (the files say). At most one question, and only about what the files cannot tell (for example, which stage to start on). "Ask me whatever you need" is not a reason to ask more.
6. No critique and no checks on a resume unless the writer asks; the next skill does that work. Change no file.
7. `status` is `done` or `done for now`: say so and ask whether to reopen it. Only the writer changes `status`.

## Style

A style the writer names ("it's a folk song"), when starting a song or resuming one, is never written unasked, not even with the other facts at creation. Offer once, as one plain line that is not a question ("You called it a folk song: say 'save the style' and I'll record it"); on a yes, write `style: <their words>` in `## Core`, replacing any existing `style:` line, then run `song`. With no style named, say nothing about style and assume none. This skill gives no style advice: style material comes only from `styles.md`, which the stage skills read.

## Red flags: stop

Each of these was said or done by an agent without this skill, unless marked:

| Thought | Reality |
|---|---|
| `entry: music`, `status: sketch`, "I guessed key D" | `entry` from the table, `status: working`, only the writer's facts. |
| `title: `, `point: `, `form: ` written empty "to fill the blanks" | No empty keys. Open fields stay out of `song.md`. |
| A song folder at the project root with `notes.md` and a `# Lyrics (none yet)` file | `songs/<slug>/song.md`, plus only the writer's material in its file. |
| "A rolling 110 bpm riff usually wants long, open lines, so look for a first line of about 6–8 syllables" | No invented targets. Name the next stage and its skill. |
| A twenty-minute plan of steps with no skill named | Show the entry's order, each stage with its skill. |
| "Do you have a melody or guitar idea for the chorus yet?" (no `music.md`, no `melody.md`) | The files answer it: say chords and melody are missing. |
| Four or five numbered questions, "You can answer only the ones you remember" | At most one question, about what the files cannot tell. |
| "Want to start with `/idea`? One question to open it: ..." (said with this skill) | One question per reply. The offer is the question. |
| Notes on the bridge and the chorus wording on a resume nobody asked to critique | No critique on a resume. Name the next stage. |
| `progression: Am, F, C, G` at the top of music.md (an early version of this skill; `harmony --music` then fails with "progression before any '## Section' heading") | Beat-less changes go on a `changes:` line. `progression:` lines are `/chords`'s. |
