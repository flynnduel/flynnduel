# Toolkit guide

`songtools` is an offline command-line toolkit. This guide lists every subcommand, its arguments and the JSON it returns. Examples were captured by running each command on the toolkit's sample song (`Porch Light Left On`) and are trimmed where marked `...`. For the call prefix and the uv fallback see `rulebook.md`, section "Running the toolkit".

Conventions: [design]

- Output is JSON by default. `--text` (before the command) prints readable text. `--pron FILE` (or env `SONGTOOLS_PRON`) names a personal pronunciations file, also placed before the command. [design]
- Errors print `{"error": "<file>:<line>: <message>"}` on stderr and exit with code 2. Usage errors take the same form. [design]
- Every successful result carries a `basis` string naming its source. Quote it when naming the basis of a note (rulebook rule 2). [design]
- The toolkit never invents a result. When something cannot be determined the output says `undetermined`; when a pronunciation was guessed it carries `"estimated": true`. Report both to the writer. [design]
- `<song>` means a song folder such as `songs/Porch Light Left On`. Commands that take a lyrics file use `lyrics.md`. [design]

## Limits

- Prosody limit, stated whenever prosody is used: Scoring is a simplified version of Hayes (2005), whose model matched listeners' preferred settings about 70% of the time on folk-song data. [verified]
- Rhyme classification reads dictionary pronunciations. A word missing from the dictionary gets an estimated pronunciation, or the pair comes back `undetermined`. [design]
- Harmony readings are simplified from Everett's systems and often ambiguous; `dual_reading` and `notes` say so. [design]
- No network is used at runtime. [design]

## Commands

### rhyme

`rhyme WORD [WORD2] [--lens pattison|webb] [--candidates N]`

With two words, classifies the pair. With one word, lists up to N candidates ranked common to fresh (the default lens is `pattison`). [design]

```
$ songtools rhyme line time
{"a": "line", "b": "time", "type": "family", "multisyllable": false,
 "detail": "same vowel AY; codas differ only within a family (N/M)",
 "lens": "pattison", "verdict": "family",
 "basis": "Pattison rhyme types (verified); Webb strict-rhyme lens (verified)"}
```

`type` is one of perfect, family, additive, subtractive, assonance, consonance, identical or `undetermined`. `verdict` is the lens's reading: under `--lens webb` the same pair returns `"verdict": "false rhyme"`. [design]

One word with `--candidates 4`:

```
{"word": "night", "lens": "pattison", "basis": "...", "undetermined": false, "reason": null,
 "candidates": [{"word": "right", "type": "perfect", "rank": 113, "verdict": "perfect"}, ...]}
```

When a word is missing from the dictionary, the pair comes back undetermined:

```
$ songtools rhyme zzxqv blorp
{"type": "undetermined", "detail": "zzxqv and blorp are not in the dictionary; add to the personal pronunciations file",
 "verdict": "undetermined", ...}
```

With one word, `undetermined` is `true` and `reason` says why. A candidates list is not a list of cliche pairs; those come from `cliche` (see Behaviours to explain). [design]

### stability

`stability LYRICS_FILE [--section NAME]`

Per section: phrase count, stresses per line, whether lengths match, rhyme scheme, end-rhyme types, a verdict and reasons; plus the verse-to-chorus contrast check at the chorus's first line. [design]

```
$ songtools stability song/lyrics.md --section Chorus
{"sections": [{"section": "Chorus", "phrase_count": 4, "stresses_per_line": [2, 4, 2, 2],
   "lengths_matched": false, "rhyme_scheme": "abaa",
   "end_rhyme_types": [null, null, "identical", "consonance"], "verdict": "unstable",
   "reasons": ["phrase lengths not matched (stresses [2, 4, 2, 2])",
               "final line rhymes by consonance (remote rhyme)"]}],
 "contrast": {"contrasts": true,
   "differences": ["stresses 4 vs 2", "syllables 10 vs 6", "end vowel IH vs AA"], "notes": []},
 "verse": "Verse 1", "chorus": "Chorus",
 "basis": "Pattison stability elements (verified)"}
```

In `rhyme_scheme`, `x` means no partner and `?` means the rhyme is undetermined (estimated pronunciation); the reasons then say so. `unstable` is a description, not a fault: a section may be unstable on purpose. [design]

### pov

`pov LYRICS_FILE`

Point of view per section and for the song: `direct_address`, `second_narrative`, `first_narrative` or `third_narrative`. Quoted speech is excluded. `generic_you` flags a general "you". `shift` is true when sections differ. [design]

```
{"song": {"pov": "direct_address", "i_count": 9, "you_count": 2, "third_count": 2, "generic_you": false},
 "sections": {"Verse 1": {"pov": "direct_address", "i_count": 2, "you_count": 1, "third_count": 0,
                           "generic_you": false}, ...},
 "shift": true, "basis": "Pattison four points of view (verified)"}
```

A section with no pronouns (for example chord-only) counts as `third_narrative` and can raise a false shift; say so when it applies. [design]

### cliche

`cliche LYRICS_FILE [--strict] [--extra FILE]`

Scans for cliche rhyme pairs, abstract filler and, with `--strict`, stock images and named emotions. `--extra` merges a writer's own JSON lists. [design]

```
$ songtools cliche song/lyrics.md --strict
{"hits": [{"line_number": 11, "kind": "rhyme_pair", "match": "home/alone", "source": "Pattison (verified)"}],
 "strict": true, "basis": "Pattison rhyme pairs (verified); other lists tagged per entry"}
```

Each hit's `source` carries its own tag; repeat it. Matching is whole-word, so inflections (whisper / whispers) can be missed. [design]

### prosody

`prosody SONG_DIR --section NAME --line N [--slots "0 1 2 ..."] [--compare]`

Scores how one line sits on the beat grid and proposes the most natural setting. `--line` is 1-based within the section. `--slots` gives an eighth-note slot per syllable (8 per 4/4 bar, 0 is the first downbeat, negative is a pickup). Without `--slots`, the setting comes from `melody.md` if the line is there (`"source": "melody"`), otherwise it is a proposal (`"source": "proposal"`). `--compare` compares the line's stress pattern with the same line in every section of the same kind. [design]

```
$ songtools prosody song --section "Verse 1" --line 1
{"section": "Verse 1", "line": 1, "lyric": "I wash the cups you left beside the sink",
 "syllables": [{"label": "i", "word": "i", "stress": 0, "word_class": "function", "estimated": false},
               {"label": "wash", "word": "wash", "stress": 1, "word_class": "content", "estimated": false}, ...],
 "source": "melody", "slots": [-3, -2, -1, 0, 1, 2, 3, 4, 5, 6], "score": 0, "flags": [],
 "notation": "i WASH the | CUPS you LEFT be-SIDE the SINK",
 "best_score": 0, "best_slots": [-3, ...], "best_notation": "i WASH the | CUPS you LEFT be-SIDE the SINK",
 "estimated": false,
 "limit": "Scoring is a simplified version of Hayes (2005), whose model matched listeners' preferred settings about 70% of the time on folk-song data.",
 "basis": "Hayes 2005 ranked constraints (simplified approximation); Pattison stress-to-beat rules (verified); Smith 2024 syncopation exemption"}
```

`stress` is 0 (unstressed), 1 (primary) or 2 (secondary). `score` is 0 when nothing is flagged; `flags` is a ranked list of problems, strongest first (a word's own stress inverted). `notation` is a human-readable setting: capitals are stressed syllables on strong slots, `|` is the bar line. With `--compare`, a `compare` list is added:

```
"compare": [{"section": "Verse 1", "lyric": "I wash the cups ...", "syllables": [10, 10],
             "stress_pattern": ["0101010001", "0101010101"], "matches": false}]
```

If any syllable's pronunciation was guessed, that syllable and the top-level `estimated` are `true`. Always repeat the limit sentence in `limit`. A confirmed setting goes into `melody.md` only after the writer agrees. [design]

### chord

`chord spell PC [--key KEY]`, `chord transpose SYMBOL SEMITONES [--key KEY]`, `chord names NOTE [NOTE ...] [--bass NOTE]`, `chord parse SYMBOL`

Key-aware spelling, transposing, naming a set of notes and parsing a symbol. Flat or sharp spelling follows `--key`. [design]

```
$ songtools chord spell 1 --key G
{"pc": 1, "key": "G", "name": "C#", "basis": "chord spelling (standard theory); pychord quality parser"}

$ songtools chord transpose G 2 --key A
{"symbol": "G", "semitones": 2, "key": "A", "result": "A", "basis": "..."}

$ songtools chord names C E G
{"pcs": [0, 4, 7], "bass": null, "names": ["C"], "basis": "..."}

$ songtools chord parse Am7/G
{"symbol": "Am7/G", "root": "A", "quality": "m7", "bass": "G", "pcs": [0, 4, 7, 9],
 "tones": ["A", "C", "E", "G"], "basis": "..."}
```

`names` may return more than one name: some note sets have two valid names. Say so rather than picking silently. An unknown symbol returns `{"error": "invalid chord symbol: 'Hxyz'"}`. [design]

### guitar

`guitar identify SHAPE`, `guitar verify SHAPE NAME`, `guitar vsystem NOTE [NOTE ...]`, `guitar joni [--tuning NOTES]`, `guitar capo CHORD [CHORD ...]`, `guitar voicings NAME`

Fretboard checks. `identify` and `verify` take `--key`, `--tuning NAME_OR_NOTES`, `--capo N` and `--partial-capo MASK` (six characters of 0 or 1, low string to high, 1 = clamped; needs `--capo`); `verify` also takes `--band-bass` (a bass player covers the root). A shape is six frets such as `x32010` (x = muted) or a quoted `'x 10 12 12 12 10'`. Frets are relative to the capo. `capo` takes `--max-fret` and `--tuning`; `voicings` takes `--limit` and `--tuning`. [design]

```
$ songtools guitar identify x32010
{"shape": "x32010", "tuning": "standard", "capo": 0, "partial_capo": null,
 "sounding": [null, 48, 52, 55, 60, 64], "notes": [null, "C", "E", "G", "C", "E"],
 "names": ["C"], "basis": "Ted Greene V-System Method 1 via Hober (verified); tunings per Wikipedia (verified); chords-db (MIT)"}

$ songtools guitar verify x32010 C
{"shape": "x32010", "name": "C", "tuning": "standard", "capo": 0, "partial_capo": null,
 "ok": true, "missing": [], "extra": [], "alternatives": ["C"], "note": "", "basis": "..."}

$ songtools guitar capo G C D
{"chords": ["G", "C", "D"], "tuning": "standard",
 "options": [{"fret": 0, "shapes": ["G", "C", "D"], "open_shapes": 3, "note": ""},
             {"fret": 5, "shapes": ["D", "G", "A"], "open_shapes": 3, "note": ""},
             {"fret": 7, "shapes": ["C", "F", "G"], "open_shapes": 2,
              "note": "soft heuristic: tone thins high on the neck (no source)"}, ...], "basis": "..."}

$ songtools guitar voicings G --limit 2
{"name": "G", "tuning": "standard", "voicings": ["320003", "355433"], "basis": "..."}

$ songtools guitar vsystem C3 G3 E4 C5
{"midi": [48, 55, 64, 72], "group": null, "basis": "..."}

$ songtools guitar joni --tuning "D2 A2 D3 G3 A3 D4"
{"tuning": "D2 A2 D3 G3 A3 D4", "strings": [38, 45, 50, 55, 57, 62], "code": "D75525", "basis": "..."}
```

`verify` reports `ok` false with `missing` and `extra` notes when the shape does not sound the chord. `group` in `vsystem` is `null` when the voicing is not a four-note V-System voicing. `joni` needs notes with octaves; bare letters give an error. Shapes are facts about notes, not playing instructions: use them to check the writer's fingering, never to write one for them. A `note` that says "soft heuristic" has no source; say so. [design]

### harmony

`harmony [CHORD ...] [--key KEY] [--music FILE]`

Reads a chord list or every section of a `music.md`. Gives the key, the Everett system with confidence, Roman numerals, Nashville numbers and chord symbols together, and a `dual_reading` when the loop is ambiguous. [design]

```
$ songtools harmony --music song/music.md
{"sections": {"Verse 1": {"key": {"tonic": "G", "mode": "major", "score": 8.0}, "confidence": 0.5,
    "system": "1a", "system_label": "1a — functional major (simplified from Everett 2004, Table 1)",
    "numerals": ["I", "IV", "I", "V"], "nashville": ["1", "4", "1", "5"], "symbols": ["G", "C", "G", "D"],
    "notes": ["Ambiguous key: also reads as D mixolydian; both are valid, so choose by where the melody rests."],
    "dual_reading": {"tonic": "D", "mode": "mixolydian", "score": 8, "numerals": ["IV", "bVII", "IV", "I"]},
    "errors": []}, ...},
 "modulations": [], "skipped": {},
 "corpus": {"root_share": {"I": 32.8, "IV": 22.6, "V": 16.3, ...}, "chorus_cadence_pre_tonic": {"V": 32.0, "IV": 18.5}},
 "basis": "Everett 2004 tonal systems (simplified); de Clercq & Temperley corpus (verified); Richards loop major bias (verified)"}
```

With a chord list the output is one section's object (the same fields, plus `corpus`). `confidence` low or `dual_reading` set means the key is a judgment, not a fact; say so. `corpus` figures are frequencies in a corpus, not rules (rulebook rule 6). [design]

### key

`key --melody-low NOTE --melody-high NOTE --voice-low NOTE --voice-high NOTE --key KEY [--tessitura LOW HIGH]`

Fits a melody's range to the writer's comfortable range and pairs each candidate key with capo options. [design]

```
$ songtools key --melody-low A2 --melody-high E4 --voice-low G2 --voice-high D4 --key G
{"current_key": "G", "melody": ["A2", "E4"], "voice": ["G2", "D4"], "tessitura": null,
 "fits": [{"key": "F", "shift": -2, "fits": true, "low": "G2", "high": "D4",
           "margin_low": 0, "margin_high": 0, "tessitura_offset": 0.0,
           "capo": [[1, "E"], [3, "D"], [5, "C"]]}, ...],
 "basis": "tessitura-based key choice (vocal pedagogy, Wikipedia: verified)"}
```

`fits` lists candidate keys (13 here) best first; each `capo` pair is `[fret, shape key]`. A negative margin means the melody falls outside the voice by that many semitones. `--tessitura LOW HIGH` supplies the range where the melody mostly lives, which refines the choice. [design]

### drafts

`drafts snapshot SONG_DIR`, `drafts cut SONG_DIR TEXT --reason REASON`, `drafts diff OLD NEW [--song SONG_MD]`

Draft history and the cut pool. `snapshot` copies `lyrics.md` to `drafts/lyrics-vN.md`. `cut` appends text to `cuts/cuts.md` with the date and reason. `diff` compares two drafts line by line; with `--song` it marks changed kept lines. [design]

```
$ songtools drafts snapshot song
{"path": "song/drafts/lyrics-v1.md", "version": 1, "basis": "draft history and cut pool (design rule)"}

$ songtools drafts cut song "Rain is tapping softly on the glass" --reason "swapped for a fresher image"
{"path": "song/cuts/cuts.md", "date": "2026-11-08", "basis": "..."}

$ songtools drafts diff song/drafts/lyrics-v2.md song/drafts/lyrics-v3.md --song song/song.md
{"changes": [{"section": "Verse 1", "index": 2, "old": "The porch light hums a tune for no one",
              "new": "The porch light hums a song for no one", "kept_changed": true}],
 "kept_changed_count": 1, "basis": "..."}
```

`kept_changed` true means a kept line was altered: ask before leaving it that way. `index` is the line's position in the section. These commands write to the song folder; snapshot before changing `lyrics.md`. [design]

### chart

`chart SONG_DIR [--concert] [--pdf]`

Writes ChordPro lead charts from `lyrics.md` and `song.md`. `--concert` also writes the concert-pitch version with the capo applied; `--pdf` renders PDF lead sheets. [design]

```
$ songtools chart song --concert --pdf
{"written": ["song/out/chart.cho", "song/out/chart-concert.cho", "song/out/chart.pdf", "song/out/chart-concert.pdf"],
 "basis": "ChordPro 6 directive subset (chordpro.org, verified)"}
```

Charts hold the writer's own chords and lyrics only. [design]

### midi

`midi SONG_DIR [--tempo BPM]`

Writes `out/guide.mid`, a reference track of the writer's own chords (block chords, nothing added). The tempo defaults to the one in `song.md`. [design]

```
$ songtools midi song --tempo 96
{"path": "song/out/guide.mid", "tempo": 96, "chords": 16, "beats": 64.0,
 "basis": "reference track of the writer's own chords (mido)"}
```

### version

`version`

```
$ songtools version
{"version": "0.1.0"}
```

## Behaviours to explain

When the writer sees one of these results, explain it rather than letting it confuse them. [design]

- Webb's lens calls homophones and identical words "false rhyme" (the same pair is `perfect` or `identical` under Pattison). Name the lens. [design]
- Prosody proposals often start in pickup slots (negative slot numbers): the line's first unstressed syllables sit before the first downbeat. That is a normal setting, not an error. [design]
- Multisyllable rhymes are undercounted: unstressed vowels are compared strictly, so a pair like beautiful / dutiful reads as assonance, not perfect. Treat a low result on a long rhyme as a prompt to listen, not a verdict. [design]
- The PDF font has no sharp or flat glyphs, so charts use `#` and `b` in the PDF. [design]
- An explicit key reports confidence 1.0 because the key was supplied. Say "key given", not "the tool is certain". [design]
- Cliche pairs come from `cliche`, not `rhyme`; `rhyme` classifies and suggests but does not flag cliche pairs. [design]
- `key` is called once per section: it fits one melody range at a time, so run it for each section whose range differs. [design]
- `midi` plays each section once, in the order the sections appear in the file; repeats and form are not expanded. [design]
