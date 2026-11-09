---
name: bank
description: Use when a songwriter wants to bank, save, jot down, store or remember an idea for later (a title, line, riff, progression, groove, concept or voice memo) without working on it now, or wants to see, search or pick from their banked ideas. Not when the writer wants to start or continue a song now (newsong).
---

# Bank

Save the idea in seconds, in the writer's words, and get out of the way. Banking is not drafting: no critique, no alternatives, no questions, no song folder.

Read `${CLAUDE_PLUGIN_ROOT}/guides/rulebook.md` first. Then read the "Bank" section of `${CLAUDE_PLUGIN_ROOT}/guides/process.md`.

**Violating the letter of these rules is violating the spirit.** "It's obviously a song, so I'll set up its folder", "a better title came to mind" or "one quick question" does not change them.

## The bank file

`songs/_bank/ideas.md`, one idea per line, exactly:

```
- YYYY-MM-DD [tag] text
```

- **Date:** today's date, from `date +%F`. Never typed from memory.
- **Tag:** one of `title`, `line`, `core`, `riff`, `memo`, `progression`, `groove`, `concept`, chosen by what the writer says the item is. Lowercase, in square brackets, one tag.
- **Text:** the item in the writer's words; a title or line verbatim in double quotes. Anything else the writer said about it (key, tempo, mood, what it might be) follows after a ` | `, in their exact words, hedges included: "maybe a wry breakup thing" is saved as `maybe a wry breakup thing`, never tidied to `wry breakup`. Form: `- 2026-11-02 [riff] "rolling DADGAD thing" | 110 bpm, drony`. Nothing the writer did not say.
- A voice memo or recording cannot be stored here: bank its description and where the writer keeps the file.

## Banking

1. If `songs/_bank/ideas.md` does not exist, create it with the heading `# Idea bank`, a blank line, then the entry.
2. Otherwise append the entry as the last line. Never reorder, edit or remove other lines.
3. Several ideas in one message: one line each.
4. Reply in one or two sentences: the line as saved, and that `/newsong` can start a song from it later. Nothing else: no critique of the idea, no alternative titles, no drafted lines, no question, no plan.
5. Create no song folder and touch no other file, even when the idea is plainly a song.

## Looking through the bank

When the writer asks what is banked, or for ideas with a tag or a word: read `ideas.md` and list the matching lines as they are. No ranking or critique unless asked.

## Promoting an idea into a song

When the writer wants to start a song from a banked idea ("let's start that one"):

1. Find its line in `ideas.md`. Leave the line where it is.
2. Start the song with `/newsong`: invoke the songwriter `newsong` skill, with `entry: banked idea` and the banked item as what the writer brought.
3. If the skill cannot be invoked, read `${CLAUDE_PLUGIN_ROOT}/skills/newsong/SKILL.md` and follow it. Before running any command from it, replace the two `${...}` variables in its text with these paths: CLAUDE_PLUGIN_ROOT is `${CLAUDE_PLUGIN_ROOT}` and CLAUDE_PLUGIN_DATA is `${CLAUDE_PLUGIN_DATA}`.

## Red flags: stop

Each of these was done by an agent without this skill:

| Thought | Reality |
|---|---|
| "Banked" by creating `songs/salt-in-the-coffee/song.md` with `status: seed` | The bank is one line in `songs/_bank/ideas.md`. No folder. |
| A new `songs/ideas.md` with `- **Salt in the Coffee** (title): ...`, no date | Exactly `- YYYY-MM-DD [tag] text` in `songs/_bank/ideas.md`. |
| Promoted with five numbered questions, or with `tone: wry breakup (from the banked idea; not confirmed)` in Core | Promotion goes through `/newsong`: `entry: banked idea`, only the writer's facts saved. |
| "Maybe a wry breakup thing" saved as `wry breakup thing` (an early version of this skill) | The writer's exact words, hedges included. |
