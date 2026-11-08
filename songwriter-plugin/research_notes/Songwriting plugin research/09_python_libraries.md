# Python libraries and formats for an offline songwriting toolkit ("songtools")

Method: PyPI JSON API metadata pulled 2026-11-07; packages installed into a scratch uv venv (uv 0.11.32 locally, Python 3.13.18) at `/tmp/claude-0/-home-user-flynnduel/72ea8edc-1b04-51bc-af27-a9c5bdf06526/scratchpad/libcheck/.venv`, with test scripts in `.../libcheck/t/`. "Hands-on" in this file means I ran it in that venv. **Caveat on offline tests:** I unset the proxy environment variables, but g2p_en still downloaded NLTK data, so the sandbox was **not** fully network-isolated. A missing download is therefore not proof that a library makes no network calls. I relied on code inspection where I could. The GitHub API (gh) and chordpro.org, metacpan.org and docs.astral.sh were blocked in this session. ChordPro docs and uv docs were read from their GitHub sources via raw.githubusercontent.com instead.

## Pronunciation / stress data: pronouncing, cmudict, nltk, g2p_en (OOV handling, licenses)

### Takeaway
`pronouncing` 0.3.0 plus `cmudict` 1.1.3 do ship stress-marked CMUdict data offline: 126,052 entries, with no download at runtime. Both are effectively dictionary-only, though: an out-of-vocabulary (OOV) word returns `[]`. The license picture is also not what we assumed. The **`cmudict` PyPI wrapper is GPL-3.0-or-later**, while the CMU data itself carries a BSD-style license. The usual OOV fallback, g2p_en 2.1.0 (2019, unmaintained), **downloads NLTK data at import time**, which violates the no-network rule unless we pre-provision that data.

### Cited Findings
- pronouncing latest is 0.3.0, uploaded 2026-04-17 after a gap since 0.2.0 (2018-07-02). It has 7 releases in total, requires Python >=3.9, is licensed MIT, and depends on `cmudict>=0.4.0` — [PyPI pronouncing](https://pypi.org/project/pronouncing/) (JSON metadata; dist-info METADATA inspected hands-on)
- pronouncing's source has no data of its own. It reads `cmudict.dict_stream()`. Its API: `phones_for_word`, `stresses`, `stresses_for_word`, `syllable_count`, `rhyming_part`, `rhymes`, `search`, `search_stresses` — hands-on (inspect of `pronouncing/__init__.py`); [repo](https://github.com/aparrish/pronouncingpy)
- cmudict (PyPI) latest is 1.1.3, uploaded 2026-01-03. It requires Python >=3.9,<4.0. The wheel's License metadata is **GPL-3.0-or-later**, and the dist-info `licenses/LICENSE` file is the GNU GPL v3 — [PyPI cmudict](https://pypi.org/project/cmudict/); [repo prosegrinder/python-cmudict](https://github.com/prosegrinder/python-cmudict); hands-on dist-info inspection
- The cmudict wheel bundles `data/cmudict.dict`, `cmudict.phones`, `cmudict.symbols`, `cmudict.vp` and a separate data `LICENSE`. `cmudict.license_string()` returns "Copyright (C) 1993-2015 Carnegie Mellon University. All rights reserved. Redistribution and use in source and binary forms, with or without modification, are permitted..." (BSD-style). `cmudict.dict()` has 126,052 entries. Installed size is about 3.5 MB — hands-on; [python-cmudict README](https://raw.githubusercontent.com/prosegrinder/python-cmudict/main/README.md)
- Stress is included: `phones_for_word("fire")` → `['F AY1 ER0', 'F AY1 R']`, and `stresses("desire")` → `010` — hands-on
- OOV handling is a dictionary miss only: `phones_for_word("yeet")` → `[]` and `phones_for_word("flynnduel")` → `[]`. "instagram" happens to be present (`IH2 N S T AH0 G R AE2 M`) — hands-on
- g2p-en latest is 2.1.0, uploaded 2019-12-31, with no `requires_python` and an Apache license. Its source calls `nltk.download('averaged_perceptron_tagger')` and `nltk.download('cmudict')` if they aren't found. Under the current NLTK it also fetched `averaged_perceptron_tagger_eng` into `/root/nltk_data` **at first import** — [PyPI g2p-en](https://pypi.org/project/g2p-en/); hands-on (`g2p_en/g2p.py` lines 22-28; the download was observed)
- After those downloads, g2p_en gives plausible OOV output: "flynnduel" → `F L IH1 N JH UW0`, "yeet" → `Y IY1 T`, "heartbreaker" → `HH AA1 R T B IY2 K ER0`. That last one is wrong: the "ea" was read as /iy/. Its neural model ships in the wheel (`checkpoint20.npz`), about 3.3 MB, and it pulls in nltk 3.10.4, numpy, inflect and distance — hands-on
- nltk latest is 3.10.4, uploaded 2026-10-21, requires Python >=3.10, Apache-2.0. Its `cmudict` corpus is not in the wheel and needs `nltk.download` — [PyPI nltk](https://pypi.org/project/nltk/); hands-on (it was downloaded at runtime by g2p_en)
- Other G2P options on PyPI: phonemizer 3.6.0 (2026-11-02, GPL-3.0+, needs the external espeak-ng binary) and epitran 1.35.3 (2026-10-08, MIT-Modern-Variant; English needs the external `lex_lookup`/Flite tool per its docs) — [PyPI phonemizer](https://pypi.org/project/phonemizer/); [PyPI epitran](https://pypi.org/project/epitran/). Not tested hands-on.
- pyphen 0.18.1 (2026-08-14; GPL-2.0+/LGPL-2.0+/MPL triple license per its classifiers) does hyphenation-based syllabification. It is orthographic and has no stress information — [PyPI pyphen](https://pypi.org/project/pyphen/)

### Inferences
- Shipping the `cmudict` PyPI package means distributing GPLv3 code. Vendoring the raw `cmudict.dict` file (BSD-style CMU license) and writing roughly 50 lines of lookup code, which is all pronouncing is, avoids that and removes two dependencies. Alternatively, accept GPL for the plugin.
- For OOV words, a rule-based fallback we write ourselves (letter-to-sound plus a syllable heuristic, flagged as "estimated") is more predictable than g2p_en. If we use g2p_en, we must vendor NLTK's `averaged_perceptron_tagger_eng` and `cmudict` into the plugin, point `NLTK_DATA` at them, and guard against `nltk.download` being called.

### Gaps
- I could not read the upstream cmusphinx/cmudict repo license file directly (GitHub API blocked). The license text cited is the copy bundled in the wheel.
- Not verified: whether pronouncing 0.3.0 changed behaviour beyond packaging (no changelog read).

## Rhyme detection (perfect / slant / multisyllable; Pattison families)

### Takeaway
Off-the-shelf support is only *perfect* rhyme. `pronouncing.rhymes()` matches the rhyming part from the last stressed vowel onward exactly. Nothing found implements Pattison's family, additive, subtractive, assonance or consonance categories, so we must build them ourselves on top of CMUdict phones.

### Cited Findings
- `pronouncing.rhymes("love")` returns 13 words: above, belove, deneuve, dove, glove, gov, labov, labove, o'glove, of, shove, thereof, vanhove. That includes proper names and junk entries, and `rhymes("orange")` → `[]`. `rhyming_part()` and regex `search()` over phone strings are available as building blocks — hands-on; [pronouncing docs/repo](https://github.com/aparrish/pronouncingpy)
- rhymetagger 1.0.0 (2025-06-25, MIT) is a statistical rhyme *tagger* for poetry corpora (detecting which lines rhyme), not a rhyme-candidate generator — [PyPI rhymetagger](https://pypi.org/project/rhymetagger/). Not tested hands-on.

### Inferences
- What to implement: (1) perfect: identical stressed vowel and everything after it; (2) family: same vowel, final consonants in the same phonetic class (plosives voiced/unvoiced, fricatives, nasals); (3) additive/subtractive: one side adds or drops a trailing consonant; (4) assonance: vowel match only; (5) consonance: final consonant match with a different vowel; (6) multisyllabic: compare the last N syllables' vowel sequence with a stress mask. Each needs a frequency filter (word lists contain names like "labov"), which is the reason for wordfreq or an equivalent.
- I found no maintained Python library that covers slant or multisyllable rhyme with a permissive license. This is a negative result from limited PyPI probing, not an exhaustive survey.

### Gaps
- I did not survey GitHub for unpublished rhyme libraries (GitHub search was unavailable).

## wordfreq maintenance, data license, offline use

### Takeaway
wordfreq still works fully offline, with data bundled in a 58 MB install. But it is frozen: the last release is 3.1.1 (2023-11-21), and in September 2024 the author announced the data will not be updated. The data is **CC BY-SA 4.0**, which brings attribution and share-alike obligations.

### Cited Findings
- wordfreq latest is 3.1.1, uploaded 2023-11-21. It requires Python >=3.8,<4. Code is Apache-2.0 — [PyPI wordfreq](https://pypi.org/project/wordfreq/)
- SUNSET.md (Sept 2024): "the wordfreq data will not be updated". Reasons: generative AI has polluted web text ("I don't think anyone has reliable information about post-2021 language usage by humans"), Twitter and Reddit data has become unavailable or expensive, and the author no longer wants to work in the field. The README says she "continue[s] to make packaging updates, but the data is unlikely to be updated again" — [SUNSET.md](https://github.com/rspeer/wordfreq/blob/master/SUNSET.md); [README](https://raw.githubusercontent.com/rspeer/wordfreq/master/README.md)
- License: the code is Apache, and the data files "may be redistributed under a Creative Commons Attribution-ShareAlike 4.0 license". Sources include Google Books Ngrams, Leeds Internet Corpus, Twitter and others — [README License section](https://raw.githubusercontent.com/rspeer/wordfreq/master/README.md) (also in installed METADATA)
- Offline: data ships as 66 files in `wordfreq/data/*.msgpack.gz` (`large_en.msgpack.gz` and others; 42 languages). Results: `zipf_frequency('love','en')`=5.82, `'heartbreak'`=3.39, OOV = 0.0. `top_n_list('en',10)` worked with no download. Dependencies: msgpack, langcodes, regex, ftfy, locate — hands-on

### Inferences
- "Unmaintained data" matters little for rhyme ranking: 2021-era English frequencies are fine. The real costs are the 58 MB footprint and CC BY-SA. A slimmer option is to ship a derived English-only rank list (e.g. top 100k words to Zipf bucket) generated once from wordfreq. Under CC BY-SA, that derived file must keep attribution and be released under the same license.

### Gaps
- Alternatives such as SUBTLEX-US (research-only terms) and `wordfreq`-derived lists were not verified this session.

## music21 vs pytheory vs pychord (vs mingus): chords, Roman numerals, key, transposition, fretboard

### Takeaway
music21 10.5.2 (BSD-3-Clause) is the most capable. It parsed every test chord, gives mode-aware Roman numerals and key detection, and handles transposition. Its costs: **flats must be written "-" (B-, not Bb)**, it is heavy (about 101 MB package plus matplotlib, numpy and requests), and it requires Python >=3.11. pytheory 0.57.13 (MIT) **failed on Cadd9, G/B, Dsus4, C6 and E7#9** and spells Bb as A#. It has rich fretboard, capo and fingering features but drags in scipy and sounddevice. pychord 1.4.3 (MIT, tiny, active) is a good lightweight parser but has enharmonic bugs on transposition. Only pytheory covers the fretboard.

### Cited Findings
- music21 latest is 10.5.2, uploaded 2026-10-28 (10.5.1 on 2026-10-22; 11.0.0b14 beta on 2026-10-31; 58 releases). It requires Python >=3.11 and is BSD-3-Clause — [PyPI music21](https://pypi.org/project/music21/)
- music21 hard dependencies: chardet, joblib, jsonpickle, matplotlib, more-itertools, numpy>=1.26.4, requests, webcolors. The `music21/` package is 101 MB, of which the bundled `corpus/` is 67 MB. `environment['autoDownload']` defaults to `'ask'`. Corpus code references a "virtual" online corpus — hands-on (METADATA, du, `corpus/corpora.py`)
- Hands-on music21 `harmony.ChordSymbol` results:
  - Cadd9 → C E G D
  - G/B → B D G (bass B)
  - Dsus4 → D G A
  - Am7 → A C E G
  - C6 → C E G A (Am7 and C6 have the same pitch-class set)
  - E7#9 → E G# B D F## (correct spelling; guitarists say "G")
  - Bm/A → bass A
  - D7sus4 and C5 OK
  - F#m7b5 → F# A C E, but `chordKind` reports "minor-seventh" with the b5 as an alteration
  - **"Bb" and "Ebdim7" raise "Invalid chord abbreviation 'b'"**; "B-" and "E-dim7" work
- Reverse identification with `chordSymbolFigureFromChord`: [A C E G] → "Am7", [C E G A] → "Am7/C" (prefers Am7 over C6), and [E G# B D G] → "E7addG" (fails to name E7#9) — hands-on
- Roman numerals against `key.Key("G")` (major): F → **bVII**, B- → bIII, C → IV, D → V, Am → ii, Em → vi. Against `key.Key("G","mixolydian")`: F → **VII**, Dm → **v**, G → I. `RomanNumeral("bVII", G)` → F A C — hands-on
- Transposition: G/B up M2 → A/C# (correct). E7#9 down 4 semitones → figure "C7 add #9", which is a correct chord but an awkward label. `stream.analyze('key')` on G D Em C G D C G → G major (alternatives e minor, C major, D major) — hands-on
- pytheory latest is 0.57.13, uploaded 2026-07-07 (122 releases, very bursty). It requires Python >=3.10, MIT, author Kenneth Reitz. Dependencies are **sounddevice, scipy, rich>=14.3.3**; scipy alone is 92 MB installed — [PyPI pytheory](https://pypi.org/project/pytheory/); hands-on
- pytheory `Chord.from_name`: Cadd9, G/B, Dsus4, C6, E7#9 → `ValueError Unknown chord`. Am7 → A C E G. Bb → "A# major" [A#, D, F]. It has `Fretboard.guitar()` (E2 A2 D3 G3 B3 E4) with `capo`, `fingering`, `chord`, `tab`, `scale_shapes`, many instrument tunings, `analyze_progression`, `detect_secondary_dominant` and `save_midi` — hands-on
- pychord latest is 1.4.3, uploaded 2026-11-03 (releases on 2026-10-09, 10-31 and 11-03). It requires Python >=3.11, MIT, and its package is 64 KB — [PyPI pychord](https://pypi.org/project/pychord/)
- Hands-on pychord results:
  - All test chords parse: Cadd9, G/B, Dsus4, Am7, C6, E7#9 (spelled F##), Bb, F#m7b5, Ebdim7, C5, Bm/A
  - `find_chords_from_notes(C E G A)` → [C6, Am7/C], and (A C E G) → [Am7, C6/A]; it is bass-aware
  - **Bug:** `Chord("G/B").transpose(2)` → "A/Db" instead of A/C#
  - It has no Roman numeral analysis or key detection
- mingus latest is 0.6.1 (2020-12-31), GPLv3. It is stale — [PyPI mingus](https://pypi.org/project/mingus/). Not tested hands-on.
- chordparser 0.4.2 (2023-03-26, MIT) — [PyPI chordparser](https://pypi.org/project/chordparser/). Not tested.

### Inferences
- For pop labels such as bVII in mixolydian songs, analyze against the parallel *major* key (music21 gives bVII). Use the mode-relative label (VII) only as a secondary display.
- music21 needs a thin normalization layer: Bb → B-, plus a mapping from `chordKind` to display names (m7b5 → ø). Its size (about 100 MB + matplotlib) is a real cost for a plugin.
- A hybrid is viable: pychord for parsing/spelling (with our own enharmonic fix keyed on the target key's accidental preference), plus our own small Roman numeral and key-scoring code. Alternatively, accept music21's footprint. pytheory is not recommended as the core: weak parsing, an audio dependency stack, and unstable versioning.
- None of these libraries offers a "guitar-friendly voicing chooser" that respects open shapes and capo suggestions. The ChordPro chord database (below) or our own table is better for diagrams.

### Gaps
- I did not verify that music21 makes zero network calls for ChordSymbol/RomanNumeral work. Code inspection shows network use only around corpus/autoDownload and URL parsing; it was not traced.
- Not tested: whether pytheory imports without PortAudio on macOS/Windows. On this Linux box it imported fine.

## PDF rendering: reportlab vs fpdf2 vs weasyprint vs typst

### Takeaway
All candidates work offline. reportlab 5.1.0 (BSD) handled chord-over-lyric layout easily via `stringWidth` and bundles Vera TTFs. fpdf2's core fonts reject non-Latin-1 characters (em dash, smart quotes), so it needs an embedded TTF. typst-py 0.15.2 compiled a test document offline using its bundled default fonts. It is a strong option if we want templated layout, but it is an 81 MB wheel.

### Cited Findings
- reportlab latest is 5.1.0, uploaded 2026-10-22. It requires Python >=3.9,<4. License is "BSD license (see license.txt)". Dependencies are pillow and charset-normalizer, with optional `shaping` (uharfbuzz) and `bidi` extras. The package is 5.1 MB and bundles Vera.ttf, VeraBd.ttf and others plus Type1 AFM/PFB fonts — [PyPI reportlab](https://pypi.org/project/reportlab/); hands-on
- reportlab hands-on: measured chord x-offsets with `pdfmetrics.stringWidth` over "I [G]walked the [C]line to[D]night" and drew the chords 13 pt above the lyric line. The PDF was written (1.5 KB) — hands-on (`t/t6.py`, `out/rl.pdf`)
- fpdf2 latest is 2.9.0, uploaded 2026-10-29. It requires Python >=3.11 and is **LGPL-3.0-only**. Dependencies are Pillow and fonttools. Core "helvetica" raised `FPDFUnicodeEncodingException` on "—"; the error says to use a Unicode font — [PyPI fpdf2](https://pypi.org/project/fpdf2/); hands-on
- weasyprint latest is 70.0 (2026-09-08), requires Python >=3.10, BSD classifier. It needs Pango system libraries — [PyPI weasyprint](https://pypi.org/project/weasyprint/). Not installed; the system-library requirement is from prior knowledge of its docs and was not re-verified this session.
- typst (Python bindings) latest is 0.15.2, uploaded 2026-11-05, requires Python >=3.9; the PyPI license field is blank. Installed size is 81 MB. `typst.compile('s.typ', output='s.pdf')` with `font: "Libertinus Serif"` produced a 9.5 KB PDF offline — [PyPI typst](https://pypi.org/project/typst/); hands-on
- The ChordPro reference implementation itself renders PDF natively (see the ChordPro section) — [ChordPro README](https://raw.githubusercontent.com/ChordPro/chordpro/master/README.md)

### Inferences
- reportlab remains a sound default: permissive license, small, and precise control for column and chord alignment. Ship a TTF such as DejaVu or Noto (check its license) for full Unicode coverage. Note that Typst `@preview` packages are fetched from the network, so the plugin must avoid `#import "@preview/..."`.

### Gaps
- typst-py license not confirmed (PyPI field blank; repo not reachable). weasyprint not tested.

## MIDI: mido vs pretty_midi vs miditoolkit

### Takeaway
mido 1.3.3 (MIT, pure Python, no dependencies) wrote a valid type-1 MIDI file with tempo and key-signature meta events. Its last release was 2024-10-25: stable but quiet. pretty_midi (MIT) is higher-level but pulls in numpy. miditoolkit is stale (2023).

### Cited Findings
- mido latest is 1.3.3, uploaded 2024-10-25, requires Python ~=3.7, MIT (45 releases) — [PyPI mido](https://pypi.org/project/mido/)
- mido hands-on: `set_tempo(bpm2tempo(96))`, `key_signature key='G'`, two block chords. The file re-read with length 5.0 s. Package is 228 KB — hands-on
- pretty_midi latest is 0.2.11.post0 (2026-07-28), MIT. It depends on numpy, mido>=1.1.16, six and importlib_resources — [PyPI pretty_midi](https://pypi.org/project/pretty_midi/); hands-on import OK
- miditoolkit latest is 1.0.1 (2023-11-23), MIT classifier — [PyPI miditoolkit](https://pypi.org/project/miditoolkit/)
- music21 and pytheory (`save_midi`) can also write MIDI — hands-on API listing

### Inferences
- mido is enough for chord-pad and click demos. Setting `requires-python ~=3.7` is harmless under uv.

### Gaps
- None material.

## ChordPro format, Python parsers, reference implementation

### Takeaway
The current language is **ChordPro version 6**. The reference implementation is Perl, at version **6.101.0 (Changes dated 2026-04-30)**, under the **Artistic License 2.0**. All the directives we need exist (title, subtitle, artist, key, capo, tempo, time, the start_of_ environments, define/chord, comment, transpose). No maintained Python ChordPro parser was found, so we write our own.

### Cited Findings
- "This program implements ChordPro language version 6." It renders PDF natively and supports Unicode, markup, annotations and ABC. "You can redistribute it and/or modify it under the terms of the Artistic License 2.0" — [ChordPro README](https://raw.githubusercontent.com/ChordPro/chordpro/master/README.md); [LICENSE](https://raw.githubusercontent.com/ChordPro/chordpro/master/LICENSE)
- `lib/ChordPro/Version.pm`: `$VERSION = "6.101.0"`. The Changes file shows 6.101 on 2026-04-30 ("Change LICENSE to match Artistic 2.0") and 6.100.0 on 2026-04-21 ("Reworked Keys and Transpositions", new `keys.force-common`/`keys.flats`, an updated guitar chord library) — [Version.pm](https://raw.githubusercontent.com/ChordPro/chordpro/master/lib/ChordPro/Version.pm); [Changes](https://raw.githubusercontent.com/ChordPro/chordpro/master/Changes)
- Directive pages in the docs source include title, subtitle, artist, composer, lyricist, album, year, copyright, key, capo, tempo, time, duration, meta, comment, chord, define, transpose, new_page, columns, column_break, image, tag, and the environments chorus/verse/bridge/tab/grid/abc/ly/svg/textblock — [ChordPro-Directives.md (docs source)](https://raw.githubusercontent.com/ChordPro/chordpro/master/docs/content/ChordPro-Directives.md)
- `{key: C}`: multiple keys are allowed, each applying from where it appears. With `{capo: 2}` the player's key stays C, and the auto metadata `_key` gives the sounding key D — [Directives-key](https://raw.githubusercontent.com/ChordPro/chordpro/master/docs/content/Directives-key.md); [Directives-capo](https://raw.githubusercontent.com/ChordPro/chordpro/master/docs/content/Directives-capo.md)
- `{tempo: 120}` is in BPM, and multiple tempos are allowed — [Directives-tempo](https://raw.githubusercontent.com/ChordPro/chordpro/master/docs/content/Directives-tempo.md)
- `{start_of_chorus}` (abbreviation `soc`) takes an optional label, e.g. `{start_of_chorus: Chorus 2}`, and ends with `{end_of_chorus}` (`eoc`). `{chorus}` recalls the chorus — [Directives-env_chorus](https://raw.githubusercontent.com/ChordPro/chordpro/master/docs/content/Directives-env_chorus.md)
- `{define: name base-fret offset frets pos … [fingers …]}` defines a chord for string instruments. "The chord definition is not transposed or transcoded unless..." — [Directives-define](https://raw.githubusercontent.com/ChordPro/chordpro/master/docs/content/Directives-define.md)
- Python ChordPro packages on PyPI: pychordpro/pyChordPro 0.1 (2021-02-14, MIT, "simple package to create, edit, compile files in the ChordPro file format") is the only hit. "chordpro", "chordsheet" and "chordpro-parser" don't exist on PyPI — PyPI JSON probes (e.g. [pychordpro](https://pypi.org/project/pychordpro/))

### Inferences
- Write a small parser covering only the directive subset we emit and read. Validate it by round-tripping, and optionally against the Perl `chordpro` CLI if the user has it installed. Don't depend on pychordpro (one release, 2021).

### Gaps
- chordpro.org could not be fetched (DNS blocked). I took the spec from the docs source in the GitHub repo master branch, which may be slightly ahead of the published site. The CPAN release date of 6.101 was not verified (metacpan blocked).

## uv pinning and Claude Code plugin packaging/invocation

### Takeaway
Use a uv project with a committed `uv.lock` and run it with `uv run --frozen` (or `--locked`), or use PEP 723 inline-script metadata with `uv lock --script` and `exclude-newer`. Claude Code plugins ship as a directory with an optional `.claude-plugin/plugin.json` plus `skills/`, `commands/`, `hooks/` and `bin/`. `${CLAUDE_PLUGIN_ROOT}` points at the installed (versioned) plugin directory, and `${CLAUDE_PLUGIN_DATA}` is persistent storage for installed dependencies.

### Cited Findings
- uv latest on PyPI is 0.13.7 (2026-11-03), MIT OR Apache-2.0 — [PyPI uv](https://pypi.org/project/uv/). (The scratch machine has 0.11.32.)
- "To disable automatic locking, use the `--locked` option: `uv run --locked`"; "To use the lockfile without checking if it is up-to-date, use the `--frozen` option" — [uv docs: projects/sync](https://raw.githubusercontent.com/astral-sh/uv/main/docs/concepts/projects/sync.md)
- Scripts can declare `# /// script` metadata with `requires-python` and `dependencies`. "uv supports an `exclude-newer` field in the `tool.uv` section of inline script metadata to limit uv to only considering distributions released before a specific date" — [uv docs: guides/scripts](https://raw.githubusercontent.com/astral-sh/uv/main/docs/guides/scripts.md)
- Plugin manifest: "Save the manifest at `.claude-plugin/plugin.json` under the plugin root. Put every other plugin file at the plugin root". `name` is the only required key. "The manifest is optional" — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)
- Standard layout: `skills/<name>/SKILL.md`; `commands/` (flat .md; "Prefer `skills/` for new plugins"); `agents/`; `hooks/hooks.json`; `.mcp.json`; `bin/`, where "Files here are on the Bash tool's `PATH` while the plugin is enabled... claude.ai and Cowork don't install a plugin that has this directory" — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)
- `${CLAUDE_PLUGIN_ROOT}` is the "Absolute path of the plugin's installed version"; it "changes when the plugin updates, so don't write state there". `${CLAUDE_PLUGIN_DATA}` is `~/.claude/plugins/data/<id>/`, "kept across plugin updates", for "Installed dependencies such as `node_modules`, generated code, and caches". It is deleted on the last uninstall by default — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)
- "The variables aren't present in the environment of commands Claude runs through the Bash tool... In skill, command, and agent content, write the `${...}` reference in the Markdown body instead, and Claude Code substitutes the path inline" — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)
- Setting `version` in plugin.json "pins the plugin to that version until you change it" — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)

### Inferences
- Recommended invocation from SKILL.md: `UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}" songtools <subcmd>`. This keeps the venv out of the versioned root, so it survives updates and is rebuilt from the lock. Installing happens on first run, which is allowed; the scripts themselves stay offline. A `bin/songtools` wrapper is convenient, but it blocks claude.ai/Cowork distribution, so prefer the SKILL.md substitution.
- Pin `requires-python = ">=3.11"` because music21, pychord and fpdf2 require 3.11+. Use `uv python pin 3.12` or 3.13.
- Total venv in this test was 584 MB with every candidate installed. A lean set (reportlab, mido, pychord, vendored cmudict data, slim word list) would be about 15 MB. Adding music21 adds about 150 MB+ (including matplotlib/numpy).

### Gaps
- I did not verify the exact `UV_PROJECT_ENVIRONMENT` interaction with `--project` hands-on. The flags are documented, but the combination was not run. I also didn't read the separate plugins/components and loading pages.

## Implications for the plugin

**Recommended dependency list** (pin in `uv.lock`; Python >=3.11, target 3.12/3.13):

| Purpose | Package | Version (2026-11-07) | License | Notes |
|---|---|---|---|---|
| PDF | reportlab | 5.1.0 | BSD | plus a bundled OFL TTF (e.g. DejaVu/Noto) for Unicode |
| MIDI | mido | 1.3.3 | MIT | no dependencies |
| Chord parsing/spelling | pychord | 1.4.3 | MIT | add our own enharmonic fix after transpose |
| Theory (optional, heavy) | music21 | 10.5.2 | BSD-3-Clause | only if Roman numerals and key detection justify about 150 MB; normalize Bb→B- |
| Word frequency | wordfreq | 3.1.1 | Apache-2.0 code / CC BY-SA 4.0 data | or ship a derived English rank file (CC BY-SA, with attribution) |
| Pronunciation | **vendored `cmudict.dict`** (CMU BSD-style) | data from cmudict 1.1.3 wheel | BSD-style | avoids the GPL-3.0+ `cmudict` wrapper; `pronouncing` 0.3.0 (MIT) is optional and still pulls in that wrapper |

**What we must implement ourselves:** slant, family, additive, subtractive, assonance, consonance and multisyllable rhyme scoring over CMUdict phones; an OOV syllable/stress estimator, since nothing usable is offline by default; a ChordPro parser/writer for our directive subset (title, subtitle, artist, key, capo, tempo, time, soc/eoc, sov/eov, sob/eob, comment, define, chord, transpose); chord-over-lyric layout; enharmonic spelling by key; pop-style Roman numerals (bVII and similar, relative to the parallel major) if we skip music21; capo and fretboard suggestions (no lightweight library does this; pytheory does but is heavy and unreliable at parsing).

**Corrections to prior assumptions:**
1. *"pronouncing+cmudict bundled offline"*: **True for the data, but there are caveats.** The `cmudict` PyPI package is **GPL-3.0-or-later**; only the CMU data is BSD-style. OOV words return `[]`. The g2p_en fallback downloads NLTK data at runtime and has been unmaintained since 2019.
2. *"wordfreq offline"*: **True** (58 MB of bundled data), but the data is **frozen** (the Sept 2024 sunset, last release 2023-11-21) and **CC BY-SA 4.0**.
3. *"music21 preferred over pytheory"*: **Confirmed.** pytheory failed 5 of 7 test chords, spells Bb as A#, and pulls in scipy and sounddevice. But music21 needs the `-` flat syntax and adds about 150 MB. pychord is a lighter option for parsing.
4. *"reportlab for PDF"*: **Confirmed** (BSD, small, offline fonts). Bundle a Unicode TTF; fpdf2 is LGPL-3.0 and has the same Unicode-font requirement.
5. *"mido for MIDI"*: **Confirmed** (MIT, pure Python). It is quiet but stable; last release 2024-10-25.
