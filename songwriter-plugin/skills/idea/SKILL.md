---
name: idea
description: Use when a songwriter with a song under way wants to work out what it is about, who sings it to whom, its moment, central image, title or point of view, has only a subject, feeling or vague idea for it, or asks Claude to fill in or decide the song's idea. Not when no song exists yet, even with only a subject or feeling to start from (newsong), or the writer wants lines drafted or checked (lyrics) or a form chosen (structure).
---

# Idea

Draw out the song's core from the writer, one question at a time, and record it in their words. The idea is theirs: Claude asks, reflects back and offers options built from what the writer said, and never supplies the loss, the person, the scene or the image.

Read `${CLAUDE_PLUGIN_ROOT}/guides/rulebook.md` first. Then read the "Point of view" and "Title and verse development" sections of `${CLAUDE_PLUGIN_ROOT}/guides/lyrics.md` and the "Receive, then edit" section of `${CLAUDE_PLUGIN_ROOT}/guides/process.md`. For the `pov` output read its entry in `${CLAUDE_PLUGIN_ROOT}/guides/toolkit.md`.

**Violating the letter of these rules is violating the spirit.** "Just fill it in", "whatever sounds good" or "I'm writing tonight" does not change them: an idea Claude invents is a song the writer did not have.

## Toolkit calls

Run from the writer's project. `<song>` is the song folder, e.g. `songs/porch-light-left-on`. Run each call in the form written, one per command. If a call is refused or blocked, run it again in that plain form; never guess its result.

```
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools pov <song>/lyrics.md
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools song <song>/song.md
```

`pov` runs only when `lyrics.md` has lines. `song` checks that `song.md` still parses after you write to it.

## The fields

Each field is done when it passes its test. Until then it is open, and open fields are not saved.

| Key in `## Core` | Concrete when |
|---|---|
| `point` | one sentence the writer has said or agreed to: what the song is saying, not its subject ("loss" is a subject) |
| `singer` | a particular person in a particular situation |
| `listener` | who is being sung to (a person, a group, no one), in the writer's words |
| `moment` | a time and place the song stands in |
| `central image` | one thing that can be seen, heard, touched or smelled, from the writer's life or invention |
| `unresolved` | the question the song leaves open |
| `pov` | the writer's pick among the four points of view, after seeing all four |
| `title` | a title the writer chose; otherwise leave the key out |

## Asking

Copy this checklist and keep it current:

```
Idea:
- [ ] song.md read: which fields exist, which are open
- [ ] one question per reply, drawn from the writer's last answer
- [ ] point, singer, listener, moment, central image, unresolved concrete
- [ ] POV: all four shown side by side, writer picked
- [ ] title: the writer's, or options from their words, or left open
- [ ] saved on the writer's say-so, one key: value line each; `song` check exit 0
```

1. **Find the song.** Read `songs/<title>/song.md`. Skip fields that are already concrete; say which are open. **No song folder yet** (nothing in `songs/` for this song): say so in one line and start with `/newsong` (invoke the `newsong` skill, or ask the writer to run it); it creates the folder, records what the writer brought and routes back here. Create no song file from this skill.
2. **One question per reply.** Exactly one question mark addressed to the writer, about the most important open field (point and singer before image, image before title). Build it from their last answer: "You cleared his workshop: which thing in that room do you still see?" A list of questions, "a few quick questions" or "answer any of these" is several questions.
3. **"Fill it in for me", "you pick".** Do not invent the idea. Say in one sentence that the idea has to come from them, then ask the one question. You may offer two to four directions only when each is built from something the writer has already said; with nothing said yet, ask.
4. **Reflect, don't add.** When the writer answers, say back what you heard in their words and name which field it fills. Your own reading (a tension, a turn, a hook) is an option for the writer to accept, not a field value.
5. **Stop when the six are concrete.** Do not keep asking about details the fields do not need (tone, objects for the verses): those belong to `/lyrics`.

## Point of view

Once singer and listener are concrete, and before `pov` is saved, run the POV check (Pattison: try the song in all four points of view). If `lyrics.md` has lines, run `pov` first and report its reading as the current POV. Then show all four side by side, each written for this song from the writer's material, one line on what it does:

```
Direct address (I to you):        <singer> sings to <listener>
Second-person narrative (you):    ...
First-person narrative (I, she):  ...
Third-person narrative (she, he): ...
```

The writer picks; even when they have already said "I'm singing it to him", show all four once and ask them to confirm.

## Title

If the writer gives a title, record it. Otherwise offer two to four candidates taken from their own words and say where each came from, or leave it open. Never save a title the writer has not chosen; `# Untitled` stays until they do. When the writer chooses one, save it as `title:` and change the `# ` heading on line 1 of `song.md` to the same title, because the toolkit reads the song's title from that heading. The song folder's name stays as it is unless the writer asks.

## Saving to song.md

Only when the writer says to save, or agrees when you offer:

1. Write each concrete field as one line in `## Core`, exactly `key: value`, value on the same line, in the writer's words, without notes, labels or "(proposed)". Keep every other line. If the key is already there, replace that line; never add a second line for the same key (the toolkit rejects a duplicate key). Do not add a new section, and do not write open fields or your own proposals.
2. Run `song <song>/song.md`. Exit 2 names the bad line: fix it and run it again.
3. Show the saved lines and list any field still open.

## Red flags: stop

Each of these was said or done by an agent without this skill:

| Thought | Reality |
|---|---|
| "Three quick questions would let me write something true to you" (a numbered list of four) | One question per reply. |
| "If you'd rather I just pick, say 'surprise me' and I'll write it up" | The idea is the writer's. Ask; options only from their words. |
| Premise, turn, hook and title ideas written into song.md "marked as proposals" | Only the writer's concrete answers are saved. Proposals stay in the reply. |
| A first-pass point saved after one answer | Open fields are not saved. |
| A new `## Idea` section with paragraphs; "(confirmed)" notes inside a value | One `key: value` line per field in `## Core`, then the `song` check. |
| Listener set to "Dad, directly" with no POV comparison | Show all four points of view before `pov` is saved. |
| "Working title ideas: Workshop / March / Everything Must Go" written into song.md | Candidates from the writer's words go in the reply; only the title they pick is saved. |
