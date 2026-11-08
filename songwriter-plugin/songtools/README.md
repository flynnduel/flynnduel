# songtools

An offline command-line toolkit for songwriters: rhyme, stability, point of view, clichés, prosody,
chords, fretboard, harmony, key fitting, drafts, ChordPro charts and MIDI guides. It backs the
songwriting Claude Code plugin but runs on its own. No network is used at runtime.

Run from this directory with `uv run --frozen songtools <command> ...`. Output is JSON by default;
put `--text` before the command for readable text. Errors print `{"error": "<file>:<line>: <message>"}`
on stderr and exit with code 2. `--pron FILE` (or env `SONGTOOLS_PRON`) names a personal
pronunciations file.

## Rule: the toolkit never invents a result

When something cannot be determined, the output says `undetermined` or carries `"estimated": true`
(for example a word missing from the pronunciation dictionary). Every method names its source in a
`basis` field.

## Commands

| Command | What it does | Example |
|---|---|---|
| `rhyme` | Classify a rhyme pair (Pattison or Webb lens) or list candidates | `songtools rhyme line time` |
| `stability` | Section stability (phrase lengths, rhyme scheme) and chorus contrast | `songtools stability lyrics.md --section Chorus` |
| `pov` | Point-of-view classification per section and for the song | `songtools pov lyrics.md` |
| `cliche` | Scan lyrics for clichés; `--strict` adds stock images and named emotions | `songtools cliche lyrics.md --strict` |
| `prosody` | Score a line's setting on the beat grid and propose a setting | `songtools prosody song/ --section "Verse 1" --line 1` |
| `chord` | Spell, parse, name and transpose chords | `songtools chord transpose G 2 --key A` |
| `guitar` | Fretboard: `identify`, `verify`, `vsystem`, `joni`, `capo`, `voicings` | `songtools guitar identify x32010` |
| `harmony` | Key, Everett system, Roman and Nashville numerals | `songtools harmony --music music.md` |
| `key` | Fit a melody to a voice range; capo pairings | `songtools key --melody-low A2 --melody-high E4 --voice-low G2 --voice-high D4 --key G` |
| `drafts` | `snapshot` lyrics, `cut` to the pool, `diff` drafts against kept lines | `songtools drafts snapshot song/` |
| `chart` | Write ChordPro charts (`--concert` applies the capo, `--pdf` renders lead sheets) | `songtools chart song/ --concert --pdf` |
| `midi` | Write `out/guide.mid` from `music.md` (your chords only) | `songtools midi song/ --tempo 96` |
| `version` | Print the version | `songtools version` |

## File formats

A song directory holds these files; all are plain Markdown. HTML comments (`<!-- ... -->`) are ignored.

**song.md** - title, core facts, kept lines, optional split sheet:

```
# Porch Light Left On

## Core
key: G
capo: 2
tempo: 96
time: 4/4
voice low: G2
voice high: D4

## Kept lines
- "The porch light hums a tune for no one" | keep | sets the whole scene | 2026-11-01

## Split sheet
- Ann Writer | lyrics, melody | 100
```

**lyrics.md** - `## Section` headings (Verse, Chorus, Pre-chorus, Bridge, ...), one lyric line per
line, chords inline in square brackets before the syllable they fall on:

```
## Verse 1
[G]I wash the cups you left beside the [C]sink
```

**music.md** - per section, a progression of `chord:beats` tokens:

```
## Verse 1
progression: G:4 C:4 G:4 D:4
```

**melody.md** - confirmed melody lines: `<line number>: syllable/slot ...`, one slot (an eighth-note
position, 0 = first downbeat, negative = pickup) per syllable, so the slot count equals the line's
syllable count:

```
## Verse 1
1: I/-3 wash/-2 the/-1 cups/0 you/1 left/2 be/3 side/4 the/5 sink/6
```

Generated output goes to `out/` (`chart.cho`, `chart-concert.cho`, `chart.pdf`, `chart-concert.pdf`,
`guide.mid`), draft snapshots to `drafts/`, cuts to `cuts/cuts.md`.

## Prosody limit

Scoring is a simplified version of Hayes (2005), whose model matched listeners' preferred settings about 70% of the time on folk-song data.

## Data sources and licences

| Data | Source | Licence |
|---|---|---|
| Pronunciations (`../data/cmudict`) | CMU Pronouncing Dictionary | BSD-style |
| Guitar chords (`../data/chords-db`) | tombatossals/chords-db | MIT |
| Fonts (`../data/fonts`) | Lato | SIL Open Font License 1.1 |
| Word ranks (`../data/word_rank.tsv`) | derived from wordfreq 3.1.1 | CC BY-SA 4.0 |
| Tunings (`../data/tunings.json`) | facts from Wikipedia's guitar tunings list; no text copied | see `../data/ATTRIBUTION.md` |

`../data/word_rank.tsv` is share-alike: any redistribution or adaptation of that file must credit wordfreq
and be released under CC BY-SA 4.0 or a compatible licence.

Runtime libraries: pychord (MIT), reportlab (BSD), mido (MIT). Their dependencies: pillow (MIT-CMU, via reportlab), charset-normalizer (MIT, via reportlab), packaging (Apache-2.0 OR BSD-2-Clause, via mido), as read from the installed package metadata. Dev-only tools (pytest, music21,
wordfreq) are never imported from `src/`. No GPL-family dependencies.

## Tests

```
uv run --frozen pytest
```

Sockets are disabled during tests. `tests/test_e2e.py` runs every subcommand on the original sample
song in `tests/fixtures/sample_song`, in JSON and text modes, and checks the installed size of the
runtime dependency closure plus the shipped data directory stays under 40 MB.

Measured footprint: 32,874,776 bytes (pillow 20.4 MB, data 6.1 MB, reportlab 4.9 MB, charset-normalizer 0.8 MB, packaging 0.5 MB, mido 0.15 MB, pychord 0.04 MB).
