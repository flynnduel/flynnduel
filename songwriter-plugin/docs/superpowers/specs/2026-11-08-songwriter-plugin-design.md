# Songwriter Plugin — Design Spec

Date: 2026-11-08
Status: Draft for review
Research basis: `reports/Songwriting plugin research.md` and `research_notes/Songwriting plugin research/`

## 1. Purpose

A Claude Code plugin that helps a professional singer-songwriter write original songs. It is genre-neutral, treats guitar as the main writing instrument, and supports writing for a full band.

The plugin co-writes and critiques lyrics, coaches the music, and gives arrangement guidance. It never writes musical parts. The writer always has the final say.

### Success criteria

- The writer can start a song from any point (riff, lyric, title, progression, brief) and resume it later.
- Every countable claim (syllables, stress, rhyme type, chord notes, key) comes from code, not from a guess.
- Every critique note names its basis and gives options. Authors whose texts were not read are cited only "as reported."
- Drafted lyrics are built from the writer's own material and pass the same stock-language checks as the writer's lines, with a stricter threshold.
- The toolkit runs fully offline with pinned dependencies and no GPL code.

### Non-goals

- Audio generation or prompts for audio generators.
- Writing melodies, bass lines, drum parts, riffs, tab or notation.
- Deciding when a song is finished.
- Genre-specific defaults.
- Audio input (singing into a memo). Possible later spike; not in scope.

## 2. Core principles (the shared rulebook)

Every skill follows these rules.

1. **Measure, don't guess.** Anything countable runs through `songtools`.
2. **Name the basis.** Each note states its lens: "Pattison:", "Webb strict rhyme:", "corpus:", "Davis (as reported):". No note claims to be a universal rule.
3. **Flag, explain, offer 2–4 options, accept the writer's call.** Options appear side by side, as in Pattison's master classes. One imposed rewrite is never the only choice.
4. **Drafting mode is quiet.** The critic speaks only in editing mode or when asked.
5. **Lyrics are co-written. Music is coached. Arrangement is guidance.** No parts, tabs or notation.
6. **No genre bias.** Commercial heuristics (title timing, title-in-chorus) apply only when the writer declares a commercial goal.
7. **Stock language is a craft issue.** The plugin never says a line "sounds like AI."
8. **State limits.** Examples: the prosody model agrees with listeners about 70% of the time on folk data; some chords have two valid names.
9. **Kept is not silenced.** A line the writer keeps is not re-flagged for the same issue in the same session. It is checked again when its surroundings change, and it always returns once at `/critique` and `/finalcheck`.

## 3. Plugin layout

```
songwriter-plugin/
├── .claude-plugin/plugin.json   manifest
├── skills/                      one folder per command, plus the shared rulebook
├── guides/                      research condensed per area; claims tagged
│                                verified / as reported
├── data/                        CMU dictionary data, consonant-family table,
│                                cliché list, chords-db shapes, tunings
└── songtools/                   Python toolkit (uv, committed lockfile, tests)
```

- Commands are implemented as skills (recommended by the plugin reference).
- No `bin/` directory; it would block installation on claude.ai and Cowork.
- Skills call the toolkit with `uv run --frozen` against the committed lock. The virtual environment lives under `${CLAUDE_PLUGIN_DATA}` so it survives plugin updates. Python ≥ 3.11.
- The exact `UV_PROJECT_ENVIRONMENT` + `--project` invocation is unverified and is the first thing the build checks.

### Commands

| Command | Job |
|---|---|
| `/newsong` | Asks where the song starts; reorders the next steps; resumes existing songs |
| `/idea` | Point, singer and listener, moment, central image, what stays unresolved, POV, title |
| `/structure` | Form menu, title and hook placement, stability plan, contrast check |
| `/lyrics` | Object writing, then drafting mode and editing mode |
| `/melody` | Coaching only: singability, phrase placement, contour, phrase alignment |
| `/chords` | Key and capo, harmony system, progression options, voicing checks |
| `/arrange` | Band road map; guidance only |
| `/chart` | ChordPro, PDF, optional MIDI |
| `/critique` | Critic only, in Critical Response Process order |
| `/finalcheck` | Final review; the writer decides the status |
| `/bank` | Quick idea capture; promote an idea into a song |

Entry points for `/newsong`: riff or groove, finished guitar song, lyric, chord progression, title, brief or commission, banked idea, co-write exchange.

## 4. Song data

Songs live in the writer's project, never inside the plugin.

```
songs/
├── _bank/ideas.md        tagged, dated ideas from /bank
└── <title>/
    ├── song.md           the song record (below)
    ├── lyrics.md         "## Verse 1" headings; optional inline chords [G]word
    ├── melody.md         confirmed beat placements for checked lines
    ├── music.md          harmony system, progressions, choices made
    ├── arrangement.md    band road map
    ├── object-writing/   raw sense writing
    ├── cuts/             cut lines and verses; never deleted
    ├── drafts/           snapshot before every lyrics change
    └── out/              generated: chart.cho, chart.pdf, guide.mid
```

`song.md` holds:

- **Entry point** — which of the eight starts.
- **Core** — the idea fields, form, key, tempo, capo, vocal range.
- **Mode** — drafting or editing.
- **Lenses** — Pattison on by default; Webb strict rhyme and commercial heuristics off.
- **Status** — working, done for now, done. Only the writer sets it.
- **Split sheet** — roles (words, music), percentages (equal by default), non-performing lyricist allowed as a full member.
- **Kept-lines register** — line, flag, reason, date.

### Data flow

1. A skill reads `song.md` to find the song's state.
2. It runs `songtools` on the song files. One shared parser reads all of them.
3. `songtools` returns JSON.
4. The skill explains the findings and offers options; the writer decides.
5. Before `lyrics.md` changes, a snapshot goes to `drafts/`. Removed material goes to `cuts/`.

### Melody input for prosody

Prosody checks run only on lines the writer asks about. For each line, `prosody` proposes the most natural setting, for example `| i was WALK-ing | DOWN to the RIV-er |`. The writer confirms it or corrects only what differs. Corrections are saved to `melody.md`, and the checker looks hardest where the writer's setting departs from natural speech. Without input, the checker only compares stress patterns across matching lines.

## 5. The songtools toolkit

One CLI with subcommands. JSON by default; `--text` for people. Fully offline.

| Subcommand | Behavior | Basis |
|---|---|---|
| `prosody` | Enumerates possible settings and proposes the best; scores a confirmed setting with ranked, graded flags. Strongest flag: a word's own stress inverted. Anticipations count as on the beat. Syncopation the melody accents is not flagged. Compares matching lines across verses. Three-tier stress lexicon: CMU stress inside words, word class for monosyllables, demotion for two-syllable function words. | Hayes 2005; Pattison; Smith 2024 |
| `rhyme` | Classifies end-rhyme pairs: perfect, family (partner and companion order per consonant family), additive, subtractive, assonance (including diphthong components), consonance, multisyllable. Suggests candidates ranked common to fresh. Flags cliché pairs. Optional Webb strict lens. | Pattison; Webb |
| `stability` | Per section: number of phrases, stresses per line, phrase rhythm, rhyme arrangement, plus rhyme type as a fifth dial. Checks contrast at the chorus's first line. | Pattison |
| `pov` | Four-way classifier (direct address; 2nd, 1st, 3rd person narrative). Excludes quoted speech; flags generic "you". | Pattison |
| `cliche` | Editable seeded list: Pattison's cliché rhyme pairs, abstract filler, stock imagery. | Pattison; others tagged |
| `chord` | Key-aware spelling. Fingering check: frets → pitches through tuning and capo (partial capos included) → all valid names. V-System labels for four-note voicings. Joni Mitchell tuning codes. Capo search ranked by open strings. | Greene; chords-db; tuning references |
| `harmony` | Classifies each section by Everett system with confidence. Roman numerals, Nashville numbers and chord symbols together. Options ranked by corpus frequency. Dual readings for ambiguous loops. | Everett; Temperley; Richards |
| `key` | Fits melody peak and tessitura per section to the writer's comfortable range; pairs keys with capo options. | Tessitura |
| `diff` | Compares drafts; tracks `cuts/`; notes kept lines. | — |
| `chart` | In-house ChordPro subset reader and writer. Shape chords with `{capo}`, plus a concert-pitch version for the band. PDF via reportlab with an open-licensed TTF. | ChordPro spec |
| `midi` | Block chords at the song's tempo. Nothing added. | — |

### Dependencies

All pinned in `uv.lock`.

| Purpose | Package | License | Note |
|---|---|---|---|
| Pronunciation | CMU dictionary data, vendored | BSD-style | Avoids the GPL `cmudict` wrapper |
| Chord parsing | pychord 1.4.3 | MIT | Add key-aware enharmonics; fix slash-chord transposition |
| PDF | reportlab 5.1.0 + OFL font | BSD | |
| MIDI | mido 1.3.3 | MIT | |
| Word ranking | rank file derived from wordfreq 3.1.1 | CC BY-SA 4.0 data | Attribution and share-alike kept |
| Test oracle only | music21 10.5.2 | BSD-3 | Checks spelling and Roman numerals in tests; not shipped |

Unknown words are marked *estimated*. The writer can add pronunciations to a personal file that every tool uses.

## 6. Skills

| Skill | Behavior |
|---|---|
| **newsong** | Asks the entry point, skips what exists, proposes the next step, resumes. Any stage is reachable at any time. |
| **idea** | Questions until the core is clear; runs the POV check (try all four). |
| **structure** | Form menu (strophic, AABA, verse-chorus, with prechorus or postchorus, compound AABA′, verse-hook, terminal climax, open jam section labelled heuristic). Title spotlights, stability plan, chorus first-line contrast, one meaningful asymmetry. |
| **lyrics** | Object writing (seven senses), drafting mode, editing mode. Checks rhyme, stability, POV, prosody on request, clichés, and whether each verse recolors the chorus. Suggests productive repetition. |
| **melody** | Coaching only. Perricone's singability checks, front- and back-heavy phrase starts, contour against meaning, lyric-and-melody phrase alignment, bridge contrast. |
| **chords** | Key and capo, harmony system, three notations, option menu with why, feel, and frequency, voicing checks. Feel described in counts and words. |
| **arrange** | Road map per section: function (initiation, buildup, arrival, contrast, ending), energy, who's in, who's waiting, feel, holds and pushes, transition, parts count against a default ceiling of four, and a "left to the players" field. Bridge optional; groove or texture switch offered instead. Optional Nashville number chart with a symbol legend. |
| **chart** | Generates outputs; verifies the chart against `lyrics.md`. |
| **critique** | Lerman order: meaning and strengths; the writer's questions answered; neutral questions; about three ranked notes, song level before line level; taste opinions only with permission. Kept lines listed separately. Changes nothing. |
| **finalcheck** | The ten steps in section 7. |
| **bank** | Saves an idea in seconds; can promote it into a song. |

## 7. Final check

Big to small, so no time goes into polishing a line in a verse that may be cut.

| # | Check | Basis |
|---|---|---|
| 1 | Point clear; title in a spotlight; each verse recolors the chorus | Pattison (verified) |
| 2 | Pronoun drift, time jumps, missing backstory, twin verses | Dodson (verified) |
| 3 | Chorus first line contrasts; stability where intended | Pattison (verified) |
| 4 | Remaining prosody flags, ranked, with limits stated | Pattison; Hayes (verified) |
| 5 | Leaps, breathing room, range and range changes within sections | Perricone (verified) |
| 6 | Listener test: words audible, chorus start clear, singable after one listen, music matches mood | Stolpe (verified) |
| 7 | Voicings verified; chart matches lyrics; capo and key correct | toolkit |
| 8 | Each kept line returns once | design rule |
| 9 | Irritant scan: does anything still bother you? | Simon via Zollo (verified) |
| 10 | Writer chooses: done, done for now, keep working. Writing done is separate from demo done. | Zollo; Webb (verified) |

NSAI criteria, Davis's checklist and Blume's checklist are excluded until verified.

## 8. Keeping drafted lyrics from sounding generic

Published evidence on "AI-sounding" lyrics is anecdotal. The measures below are established craft principles applied more strictly to the plugin's own drafts than to the writer's lines.

1. **Draft from the writer's material.** Every drafted line must draw on something in the song record: the idea fields, the central image, object writing, or the writer's own lines. With no material, the plugin runs object writing or asks a question first. It does not invent generic scenery.
2. **Particular over general.** Drafts favor concrete nouns, sensory detail, and the specific moment from `/idea`. Lines that name the emotion instead of showing it are flagged. (Davis, as reported; Pattison's imagery and metaphor tools, verified.)
3. **Self-audit before showing.** The plugin runs `cliche`, `rhyme`, and `stability` on its own drafts and rewrites or drops anything that fails. Its threshold is stricter than the threshold for the writer's lines.
4. **Rhyme for meaning, not convenience.** Cliché pairs (love/dove, fire/desire, eyes/realize) are rejected in drafts. Family rhyme and assonance are preferred where they serve the section's stability goal. (Pattison, verified.)
5. **Purposeful irregularity.** Line lengths and rhyme schemes follow the stability plan rather than a default even meter. (Pattison, verified.) Perfectly uniform meter is treated as a warning sign. (Inference, unverified.)
6. **Match the song's voice.** Drafts follow the diction and register already in the writer's lines for this song.
7. **Any size the writer wants.** The plugin drafts full lines, couplets or whole sections. Where a choice matters, it offers 2–4 versions side by side. Every draft passes the self-audit in item 3 before the writer sees it.
8. **Tested.** Skill pressure tests include drafting scenarios. Baseline drafts written without the skill are recorded, and the skill must beat them on the stock-language and specificity checks.

The rule from section 2 still holds: the plugin flags stock language as craft and never accuses the writer of using AI.

## 9. Testing

### Toolkit (test-driven)

Each subcommand starts with a failing test built from a research case.

- **rhyme:** cat/hat, cat/hack, cat/rats, cat/laugh, cat/spot; partner and companion order per family; line/time as a strong family rhyme under Pattison and a false rhyme under Webb.
- **prosody:** Pattison's "Unconditionally" cases ("the" and "did" on downbeats, "-ly" on a downbeat); accented syncopation not flagged.
- **stability and POV:** abab vs aabb vs xxaa; one lyric per POV.
- **chord:** x32210 returns Am/C and C6 (no 5th); Am7 and C6 both recognized; G/B up a whole step gives A/C#.
- **harmony:** F is ♭VII in G; ♭VII–IV–I labelled double-plagal, not modal; dual readings for a four-chord loop.
- **chart:** ChordPro round trip; capo shown correctly in shape and concert versions.
- **Oracle:** music21 cross-checks chord spelling and Roman numerals.
- **Guards:** networking disabled during tests; license check fails on any GPL dependency.

### Skills (writing-skills method)

For each skill: run the scenario without it and record the failure; write the skill; rerun until it passes. Failure cases:

- Rewriting a kept line without asking
- Writing a bass line or tab when asked about chords
- Giving a taste opinion in `/critique` without permission
- Critiquing in drafting mode
- Presenting a secondhand Davis claim as verified
- Saying a lyric "sounds like AI"
- Declaring the song finished
- Treating V–I as the only correct cadence
- Adding genre assumptions
- Guessing a syllable count instead of running the tool
- Drafting generic lines not drawn from the writer's material

### End to end

One sample song runs from `/newsong` to `/finalcheck`, with every file checked.

## 10. Error handling

- Unknown words: marked *estimated*; writer can add a pronunciation.
- Ambiguous chords: all valid names returned.
- Malformed song files: error names the file and line.
- Missing stage: the skill says which stage to run.
- `songtools` never invents a result. When it cannot decide, it says so.

## 11. Build order

1. Toolkit foundation: song parser, CMU data, rhyme, stability, POV, cliché, prosody.
2. Chord, harmony, key.
3. Chart, MIDI, diff.
4. Guides: each research area condensed, claims tagged verified or as reported.
5. Skills, each pressure-tested.
6. Packaging and the end-to-end test.

## 12. Open items

To verify by hand before release (books unreadable online): Davis's checklists; Webb's *Tunesmith* (rhyming dictionaries, rewriting); Perricone's *Great Songwriting Techniques* and his range figure; Rooksby on capo, tunings and arranging; Owsinski's element ceiling and tension-and-release section; Pattison's own definitions of additive, subtractive and partial rhyme. Until then these are cited by title or "as reported."

Also unverified: the GuitarSet data license (testing use only once confirmed).
