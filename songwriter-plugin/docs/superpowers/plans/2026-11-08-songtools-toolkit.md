# songtools Toolkit Implementation Plan (Plan 1 of 2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `songtools`, the offline Python CLI that every songwriter-plugin skill calls for anything countable: prosody, rhyme, stability, POV, clichés, chords, guitar, harmony, key fitting, drafts, charts and MIDI.

**Architecture:** A uv-managed package at `songwriter-plugin/songtools/` with one module per subcommand, sharing a song-file parser and a pronunciation lexicon. Vendored data lives in `songwriter-plugin/data/`. Every subcommand prints JSON by default and readable text with `--text`. Plan 2 (guides, skills, packaging) is written after this plan ships, against these interfaces.

**Tech Stack:** Python ≥ 3.11, uv, pychord 1.4.3, reportlab 5.1.0, mido 1.3.3; dev only: pytest 9.2.0, music21 10.5.2 (test oracle), wordfreq 3.1.1 (builds the rank file).

**Spec:** `songwriter-plugin/docs/superpowers/specs/2026-11-08-songwriter-plugin-design.md` (sections 4, 5, 9, 10, 11 steps 1–3). Research basis: `songwriter-plugin/reports/Songwriting plugin research.md`.

## Global Constraints

- Python `>=3.11`. All dependency versions pinned with `==` in `pyproject.toml`; `uv.lock` committed; run everything with `uv run --frozen`.
- Runtime dependencies are exactly: `pychord==1.4.3`, `reportlab==5.1.0`, `mido==1.3.3`. Dev only: `pytest==9.2.0`, `music21==10.5.2`, `wordfreq==3.1.1`. music21 and wordfreq are never imported from `src/`.
- No GPL, LGPL or AGPL code anywhere in the environment. The CMU dictionary is vendored as a data file; the `cmudict` and `pronouncing` packages are not used.
- No network calls at runtime. The test suite runs with sockets disabled.
- Output: JSON on stdout (`ensure_ascii=False`, `indent=2`); `--text` gives readable text. Errors: exit code 2, JSON `{"error": "<file>:<line>: <message>"}` on stderr.
- `songtools` never invents a result. When it cannot decide, it returns `"undetermined"` or marks the item `"estimated": true`.
- Every module that implements a published method carries a `BASIS` string naming its source, matching the spec's attribution (e.g. `"Pattison (verified)"`, `"Hayes 2005 (approximation)"`).
- The prosody limit statement, verbatim: `"Scoring is a simplified version of Hayes (2005), whose model matched listeners' preferred settings about 70% of the time on folk-song data."`
- Commit after every task with the attribution lines:
  ```
  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_018mK5aRJ1Ar8bEKdNKeqjr9
  ```

## Review Focus

1. **Words missing from the CMU dictionary** (names, slang, `walkin'`, `rock'n'roll`, numbers like `4`): expect an `estimated` syllable count and no crash; dropped-g forms resolve to the `-ing` word. Pinned in Task 3.
2. **Messy lyric text** (curly quotes, trailing punctuation, mixed case, em dashes, stray inline-chord brackets): expect clean end-word extraction, and a file:line error for an unclosed `[`. Pinned in Task 2.
3. **Thin or odd song structure** (one-line section, a chorus with no verse, empty section): expect an explanatory result, not an exception. Pinned in Task 5.
4. **Unusual or invalid chord symbols** (`Bbmaj7`, `C/Bb`, `Gsus`, `N.C.`, `H7`): expect valid ones parsed, `N.C.` skipped, invalid ones reported per chord while analysis continues. Pinned in Tasks 9 and 11.
5. **Non-ASCII text in charts** (`Señor`, `—`, `“quoted”`): expect the PDF to render with the bundled Lato font. Pinned in Task 15.

---

## File structure

```
songwriter-plugin/
├── data/
│   ├── cmudict/cmudict.dict, LICENSE          (vendored, CMU BSD-style)
│   ├── chords-db/guitar.json, LICENSE         (vendored, MIT)
│   ├── fonts/Lato-Regular.ttf, Lato-Bold.ttf, OFL.txt
│   ├── word_rank.tsv, ATTRIBUTION.md          (built from wordfreq, CC BY-SA 4.0)
│   ├── consonants.json                        (Task 3)
│   ├── function_words.txt                     (Task 3)
│   ├── cliches.json                           (Task 7)
│   └── tunings.json                           (Task 10)
└── songtools/
    ├── pyproject.toml, uv.lock
    ├── scripts/build_word_rank.py
    ├── src/songtools/
    │   ├── __init__.py   cli.py   paths.py   output.py
    │   ├── songfile.py   pron.py   phonemes.py
    │   ├── rhyme.py   stability.py   pov.py   cliche.py   prosody.py
    │   ├── chords.py   fretboard.py   harmony.py   keyfit.py
    │   ├── drafts.py   chordpro.py   pdf.py   midi.py
    └── tests/
        ├── conftest.py   fixtures/sample_song/…
        └── test_<module>.py (one per module)   test_guards.py   test_e2e.py
```

Each module exposes its functions plus `register(subparsers) -> None`, which adds its CLI subcommand and sets a handler `handler(args) -> dict`, and `to_text(result: dict) -> str`.

---

### Task 1: Project scaffold, vendored data, guards and CLI skeleton

**Files:**
- Create: `songtools/pyproject.toml`, `songtools/uv.lock`, `src/songtools/{__init__,cli,paths,output}.py`, `tests/conftest.py`, `tests/test_guards.py`, `scripts/build_word_rank.py`
- Create: everything under `data/cmudict/`, `data/chords-db/`, `data/fonts/`, plus `data/word_rank.tsv` and `data/ATTRIBUTION.md`

**Interfaces:**
- Produces: `paths.data_dir() -> pathlib.Path` (env `SONGTOOLS_DATA`, else `Path(__file__).resolve().parents[3] / "data"`); `output.emit(result: dict, text: bool, to_text) -> None`; `cli.main(argv: list[str] | None = None) -> int`; `cli.SongtoolsError(file: str | None, line: int | None, message: str)`; console script `songtools = "songtools.cli:main"`.

- [ ] **Step 1: Create the uv project**

Run from `songwriter-plugin/songtools`: `uv init --package --name songtools --python ">=3.11"`, then `uv add pychord==1.4.3 reportlab==5.1.0 mido==1.3.3` and `uv add --dev pytest==9.2.0 music21==10.5.2 wordfreq==3.1.1`.
Expected: `uv.lock` exists; `uv run --frozen python -c "import pychord, reportlab, mido"` exits 0.

- [ ] **Step 2: Vendor the data files**

Download into `songwriter-plugin/data/`:
- `https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict` and `.../LICENSE` → `data/cmudict/`
- `https://raw.githubusercontent.com/tombatossals/chords-db/master/lib/guitar.json` and `.../LICENSE` → `data/chords-db/`
- `https://raw.githubusercontent.com/google/fonts/main/ofl/lato/Lato-Regular.ttf`, `Lato-Bold.ttf`, `OFL.txt` → `data/fonts/`

Expected: `grep -c "" data/cmudict/cmudict.dict` > 120000; `guitar.json` has top-level keys `main, tunings, keys, suffixes, chords`.

- [ ] **Step 3: Build the word-rank file**

`scripts/build_word_rank.py`: `wordfreq.top_n_list("en", 60000)`, keep entries matching `^[a-z']+$`, write `data/word_rank.tsv` as `word<TAB>rank` (rank starts at 1). Write `data/ATTRIBUTION.md` crediting wordfreq 3.1.1 data under CC BY-SA 4.0 with a link to its repository, and noting the share-alike terms apply to `word_rank.tsv`.
Run: `uv run --frozen python scripts/build_word_rank.py`. Expected: `head -1 data/word_rank.tsv` prints `the	1`.

- [ ] **Step 4: Write the guard tests**

```python
# tests/test_guards.py
import importlib.metadata as md, urllib.request, pytest
from songtools.cli import main

def test_network_is_disabled_in_tests():
    with pytest.raises(RuntimeError, match="network disabled"):
        urllib.request.urlopen("https://example.com", timeout=2)

def test_no_gpl_family_licenses_installed():
    bad = []
    for d in md.distributions():
        meta = d.metadata
        lic = " ".join(filter(None, [meta.get("License-Expression"), meta.get("License")] +
                              [c for c in meta.get_all("Classifier") or [] if c.startswith("License")]))
        if "GPL" in lic.upper():
            bad.append(meta["Name"])
    assert bad == []

def test_version_subcommand(capsys):
    assert main(["version"]) == 0
    assert '"version"' in capsys.readouterr().out
```

`tests/conftest.py`: an autouse fixture that monkeypatches `socket.socket.connect` and `socket.create_connection` to raise `RuntimeError("network disabled in tests")`.

- [ ] **Step 5: Run tests to verify they fail**

Run: `uv run --frozen pytest tests/test_guards.py -v`. Expected: `test_version_subcommand` FAILS (no `main`).

- [ ] **Step 6: Implement `cli.main`, `paths.data_dir`, `output.emit`, `SongtoolsError`**

`main` builds an argparse parser with global flags `--text` and `--pron FILE` (personal pronunciations; also env `SONGTOOLS_PRON`, exposed to handlers as `args.pron: Path | None`), calls `register(subparsers)` for every module listed in a `MODULES` tuple (empty except a built-in `version` subcommand returning `{"version": songtools.__version__}`), runs the handler, emits output, returns 0. A `SongtoolsError` returns exit code 2 with `{"error": "<file>:<line>: <message>"}` on stderr (omit file or line parts when `None`).

- [ ] **Step 7: Run tests to verify they pass**

Run: `uv run --frozen pytest -v`. Expected: 3 passed.

- [ ] **Step 8: Commit**

`git add songwriter-plugin/data songwriter-plugin/songtools && git commit -m "feat(songtools): scaffold toolkit with vendored data and guards"`

---

### Task 2: Song file formats and parser

**Files:**
- Create: `src/songtools/songfile.py`, `tests/test_songfile.py`

**Interfaces:**
- Produces:
  - `@dataclass Line(number: int, text: str, lyric: str, chords: list[tuple[int, str]])`. `number` is the 1-based line in the file; `lyric` has chords removed; each chord is `(char offset in lyric, symbol)`.
  - `@dataclass Section(name: str, kind: str, lines: list[Line])`. `kind` ∈ `verse, prechorus, chorus, postchorus, bridge, intro, outro, refrain, hook, tag, other`.
  - `parse_lyrics(text: str, file: str = "lyrics.md") -> list[Section]`
  - `end_word(line: Line) -> str` (lowercase, punctuation and curly quotes stripped, apostrophes kept)
  - `@dataclass KeptLine(text: str, flag: str, reason: str, date: str)`; `@dataclass Split(name: str, roles: list[str], percent: float)`
  - `@dataclass SongRecord(title: str, core: dict[str, str], sections: dict[str, str], kept: list[KeptLine], splits: list[Split])`
  - `parse_song_md(text: str, file: str = "song.md") -> SongRecord`
  - `parse_music_md(text: str, file: str = "music.md") -> dict[str, list[tuple[str, float]]]`
  - `parse_melody_md(text: str, file: str = "melody.md") -> dict[tuple[str, int], list[tuple[str, int]]]` keyed by (section name, line index within section, 1-based) → list of (syllable label, slot)
  - `format_melody_entry(index: int, syllables: list[tuple[str, int]]) -> str`

File formats, fixed by this task:

```
lyrics.md     ## Verse 1            ← heading = section; kind from the name's first word
              [G]I was walking [C]down to the river
              <!-- comments ignored -->
song.md       # Title
              ## Core               ← "key: value" lines (key, capo, tempo, time, tuning,
              key: G                   voice_low, voice_high, mode, status, lenses, entry)
              ## Split sheet        ← "- Name | words, music | 50"
              ## Kept lines         ← '- "line text" | flag | reason | 2026-11-08'
              (any other ## section kept verbatim in SongRecord.sections)
music.md      ## Verse 1
              progression: G:4 C:4 D:2 C:2
melody.md     ## Verse 1
              3: i/-2 was/-1 walk/0 ing/1 down/2 to/3 the/4 riv/6 er/7
```

Melody slots are eighth notes: 8 per 4/4 bar, slot 0 is the first downbeat, negative slots are pickups.

- [ ] **Step 1: Write the failing tests**

```python
def test_sections_and_inline_chords():
    secs = parse_lyrics("## Verse 1\n[G]I was walking [C]down to the river\n\n## Chorus\nHold on\n")
    assert [s.kind for s in secs] == ["verse", "chorus"]
    ln = secs[0].lines[0]
    assert ln.lyric == "I was walking down to the river"
    assert ln.chords == [(0, "G"), (14, "C")]
    assert ln.number == 2

def test_prechorus_name_variants():
    assert parse_lyrics("## Pre-Chorus\nx\n")[0].kind == "prechorus"

def test_end_word_strips_punctuation_and_curly_quotes():
    ln = parse_lyrics("## Verse\nShe said “goodbye,” —\n")[0].lines[0]
    assert end_word(ln) == "goodbye"

def test_unclosed_chord_bracket_reports_file_and_line():
    with pytest.raises(SongtoolsError) as e:
        parse_lyrics("## Verse\nfine\n[G broken\n")
    assert (e.value.file, e.value.line) == ("lyrics.md", 3)

def test_song_md_core_kept_and_splits():
    rec = parse_song_md('# River\n## Core\nkey: G\ncapo: 2\n## Split sheet\n- Ana | words, music | 50\n'
                        '## Kept lines\n- "down to the river" | cliche | echoes bridge | 2026-11-08\n')
    assert rec.title == "River" and rec.core["capo"] == "2"
    assert rec.kept[0] == KeptLine("down to the river", "cliche", "echoes bridge", "2026-11-08")
    assert rec.splits[0] == Split("Ana", ["words", "music"], 50.0)

def test_music_md_progression():
    assert parse_music_md("## Verse 1\nprogression: G:4 C:2.5\n") == {"Verse 1": [("G", 4.0), ("C", 2.5)]}

def test_melody_roundtrip():
    entry = parse_melody_md("## Verse 1\n3: i/-2 was/-1 walk/0\n")
    assert entry[("Verse 1", 3)] == [("i", -2), ("was", -1), ("walk", 0)]
    assert format_melody_entry(3, entry[("Verse 1", 3)]) == "3: i/-2 was/-1 walk/0"
```

- [ ] **Step 2: Run to verify failure** — `uv run --frozen pytest tests/test_songfile.py -v` → FAIL (module missing).
- [ ] **Step 3: Implement the parser functions in `songfile.py`** with the signatures above. Raise `SongtoolsError(file, line, msg)` for malformed lines (unclosed `[`, bad `progression:` token, bad `syllable/slot` token).
- [ ] **Step 4: Run to verify pass** — same command → all PASS.
- [ ] **Step 5: Commit** — `git commit -m "feat(songtools): song file formats and parser"`

---

### Task 3: Pronunciation lexicon and phoneme tables

**Files:**
- Create: `src/songtools/pron.py`, `src/songtools/phonemes.py`, `data/consonants.json`, `data/function_words.txt`, `tests/test_pron.py`, `tests/test_phonemes.py`

**Interfaces:**
- Produces:
  - `@dataclass Pron(phones: list[str] | None, syllables: int, stresses: list[int], estimated: bool)`. ARPAbet phones with stress digits; `stresses` holds one digit per vowel.
  - `class Lexicon`: `lookup(word: str) -> list[Pron]` (always ≥ 1 entry), `rank(word: str) -> int | None`, `words() -> Iterable[str]`
  - `load_lexicon(overrides: Path | None = None) -> Lexicon`, cached per overrides path. Override file lines use cmudict format and take precedence.
  - `word_class(word: str) -> Literal["function", "content"]`
  - `phonemes.VOWELS: frozenset[str]` (AA AE AH AO AW AY EH ER EY IH IY OW OY UH UW)
  - `phonemes.DIPHTHONGS: dict[str, tuple[str, str]]` = `{"AY": ("AA","IY"), "EY": ("EH","IY"), "OY": ("AO","IY"), "AW": ("AA","UW"), "OW": ("AO","UW")}`
  - `phonemes.family(c: str) -> Literal["plosive","fricative","nasal"] | None`; `phonemes.voiced(c: str) -> bool`; `phonemes.relatives(c: str) -> list[str]` (closest first)

Data fixed by this task:
- `consonants.json`, from Pattison's families (verified):
  - plosive: voiced `B D G`, unvoiced `P T K`
  - fricative: voiced `V DH Z ZH JH`, unvoiced `F TH S SH CH`
  - nasal: `M N NG`
  - partners: `B-P D-T G-K V-F DH-TH Z-S ZH-SH JH-CH`
- `relatives` order:
  - Plosives: partner, then same-voicing companions, then the rest.
  - Fricatives: same-voicing companions in the order `S SH CH TH` (or `Z ZH JH DH` for voiced), then the partner, then the rest.
  - Nasals: the other nasals.
- `function_words.txt`: English closed-class words (articles, pronouns, auxiliaries, prepositions, conjunctions, determiners), one per line. Two-syllable function words such as `before`, `into`, `upon`, `about`, `over` and `under` are included.

- [ ] **Step 1: Write the failing tests**

```python
def test_cmu_lookup_with_stress():
    p = load_lexicon().lookup("river")[0]
    assert p.phones == ["R", "IH1", "V", "ER0"] and p.stresses == [1, 0] and not p.estimated

def test_alternate_pronunciations_returned():
    assert len(load_lexicon().lookup("read")) >= 2

def test_unknown_word_is_estimated_not_crash():
    p = load_lexicon().lookup("zorbletastic")[0]
    assert p.estimated and p.phones is None and p.syllables == 4

def test_dropped_g_resolves_to_ing_form():
    assert load_lexicon().lookup("walkin'")[0].phones == load_lexicon().lookup("walking")[0].phones

def test_number_is_estimated():
    assert load_lexicon().lookup("4")[0].estimated

def test_override_file_wins(tmp_path):
    f = tmp_path / "pron.txt"; f.write_text("river R IY1 V ER0\n")
    assert load_lexicon(f).lookup("river")[0].phones[1] == "IY1"

def test_rank_common_before_rare():
    lex = load_lexicon()
    assert lex.rank("love") < lex.rank("lugubrious")

def test_word_class():
    assert word_class("the") == "function" and word_class("before") == "function"
    assert word_class("river") == "content"

def test_plosive_partner_first_then_companions():
    r = relatives("T")
    assert r[0] == "D" and set(r[1:3]) == {"K", "P"} and set(r[3:5]) == {"B", "G"}

def test_fricative_companions_before_partner():
    r = relatives("F")
    assert r[:3] == ["S", "SH", "CH"] and r.index("V") > r.index("TH")

def test_nasal_family():
    assert family("M") == "nasal" and set(relatives("N")) == {"M", "NG"}
```

- [ ] **Step 2: Run to verify failure** — `uv run --frozen pytest tests/test_pron.py tests/test_phonemes.py -v` → FAIL.
- [ ] **Step 3: Implement `pron.py` and `phonemes.py`.**
  - Strip `(2)`-style alternate markers and `#` comments while loading.
  - Normalize lookups: lowercase, strip surrounding punctuation and curly quotes.
  - `in'` maps to `ing`.
  - Estimated syllable count is the number of vowel groups (`[aeiouy]+`), less one for a silent final `e`, minimum 1. Estimated entries get `stresses=[1] + [0]*(n-1)`.
- [ ] **Step 4: Run to verify pass.**
- [ ] **Step 5: Commit** — `git commit -m "feat(songtools): pronunciation lexicon and consonant families"`

---

### Task 4: Rhyme classifier, lenses and candidates

**Files:**
- Create: `src/songtools/rhyme.py`, `tests/test_rhyme.py`

**Interfaces:**
- Consumes: `Lexicon`, `phonemes.relatives/family/DIPHTHONGS/VOWELS`.
- Produces:
  - `RHYME_TYPES = ["identical","perfect","family","additive","subtractive","assonance","consonance","eye","none","undetermined"]`
  - `STABILITY_RANK = {"perfect":0,"family":1,"additive":2,"subtractive":2,"assonance":3,"consonance":4}`. Pattison: lower is more stable.
  - `@dataclass RhymeResult(a: str, b: str, type: str, multisyllable: bool, detail: str)`
  - `classify(a: str, b: str, lex: Lexicon) -> RhymeResult`. Tries every pronunciation pair and returns the most stable result.
  - `lens_verdict(result: RhymeResult, lens: Literal["pattison","webb"]) -> str`. `pattison` returns `result.type`. `webb` returns `"true rhyme"` only for `perfect`, `"eye rhyme"` for `eye`, and `"false rhyme"` otherwise.
  - `@dataclass Candidate(word: str, type: str, rank: int | None)`; `candidates(word: str, lex: Lexicon, types: list[str] | None = None, limit: int = 50) -> list[Candidate]`. Sorted by `STABILITY_RANK`, then common to fresh (rank ascending, `None` last).
  - CLI: `songtools rhyme WORD [WORD2] [--lens pattison|webb] [--candidates N]`

Classification algorithm. The rhyme part is the last stressed vowel (stress 1, or the last vowel if none) plus everything after it. Comparing a and b with vowels Va, Vb and codas Ca, Cb:
- **identical**: the same word.
- **perfect**: Va == Vb, Ca == Cb, and the onsets before the vowel differ.
- **family**: Va == Vb, equal coda lengths, and every differing coda consonant is in the same family (`relatives`).
- **additive**: Va == Vb and Cb is Ca plus one or more extra consonants. **subtractive** is the reverse.
- **assonance**: Va == Vb otherwise.
- **consonance**: Va != Vb and Ca == Cb, with Ca not empty.
- **eye**: the spellings share their last 3 or more letters but none of the above holds.
- **none**: otherwise. **undetermined**: either word is estimated.
- `multisyllable = True` when both rhyme parts contain two or more vowels and the type is perfect or family.

- [ ] **Step 1: Write the failing tests**

```python
LEX = load_lexicon()
@pytest.mark.parametrize("b,expected", [
    ("hat","perfect"), ("hack","family"), ("rats","additive"),
    ("laugh","assonance"), ("spot","consonance")])
def test_pattison_ladder_from_cat(b, expected):        # Pattison, verified
    assert classify("cat", b, LEX).type == expected

def test_subtractive():
    assert classify("rats", "cat", LEX).type == "subtractive"

def test_wichita_lineman_line_time_lenses():          # Pattison vs Webb, verified
    r = classify("line", "time", LEX)
    assert r.type == "family"
    assert lens_verdict(r, "pattison") == "family" and lens_verdict(r, "webb") == "false rhyme"

def test_eye_rhyme_and_identical():
    assert classify("dough", "rough", LEX).type == "eye"
    assert classify("night", "night", LEX).type == "identical"

def test_multisyllable_flag():
    assert classify("river", "giver", LEX).multisyllable

def test_estimated_word_is_undetermined():
    assert classify("cat", "zorbletastic", LEX).type == "undetermined"

def test_candidates_order_stable_then_common():
    c = candidates("cat", LEX, limit=30)
    assert [x.type for x in c] == sorted([x.type for x in c], key=STABILITY_RANK.get)
    perfect = [x for x in c if x.type == "perfect"]
    assert perfect[0].rank <= perfect[-1].rank

def test_candidates_fast():
    import time; t = time.perf_counter(); candidates("river", LEX); assert time.perf_counter() - t < 2.0

def test_cli_json(capsys):
    assert main(["rhyme", "line", "time", "--lens", "webb"]) == 0
    assert '"false rhyme"' in capsys.readouterr().out
```

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement `rhyme.py`.** Build a lazy index from rhyme-part vowel to words, so `candidates` scans one vowel bucket plus consonance buckets. Register the `rhyme` subcommand and add it to `cli.MODULES`.
- [ ] **Step 4: Run to verify pass.**
- [ ] **Step 5: Commit** — `git commit -m "feat(songtools): Pattison rhyme classifier with Webb lens"`

---

### Task 5: Section stability and chorus contrast

**Files:**
- Create: `src/songtools/stability.py`, `tests/test_stability.py`

**Interfaces:**
- Consumes: `Section`, `end_word`, `classify`, `Lexicon`, `word_class`.
- Produces:
  - `stresses_in(lyric: str, lex: Lexicon) -> int`. Counts stress-1 syllables in polysyllables plus content monosyllables. Two-syllable function words count 0.
  - `@dataclass SectionStability(section: str, phrase_count: int, stresses_per_line: list[int], lengths_matched: bool, rhyme_scheme: str, end_rhyme_types: list[str], verdict: Literal["stable","unstable","undetermined"], reasons: list[str])`
  - `analyze_section(section: Section, lex: Lexicon) -> SectionStability`
  - `@dataclass Contrast(contrasts: bool, differences: list[str])`; `chorus_contrast(verse: Section, chorus: Section, lex: Lexicon) -> Contrast`
  - CLI: `songtools stability LYRICS_FILE [--section NAME]`. Prints every section and the contrast between the first verse and the first chorus.

Rules (Pattison, verified):
- **Rhyme scheme:** lines whose end words classify as perfect, family, additive, subtractive, assonance or consonance share a letter. A line with no partner is `x`.
- **Unstable reasons**, each adding a line to `reasons`:
  - odd `phrase_count`
  - `not lengths_matched` (stresses differ)
  - scheme in `{"abba","xxaa","xaxa","xxxa"}` (open)
  - a final line marked `x` (unrhymed ending)
  - a final pair rhyming by assonance or consonance (remote rhyme)
- **Verdict:** `stable` when there are no reasons, otherwise `unstable`. `undetermined` for an empty section.
- **Contrast** compares the chorus's first line with the verse norm (the mode of the verse lines) on stress count, syllable count, and end vowel. `contrasts` is True if any of them differs. Each difference is reported in the form `"stresses 2 vs 4"`.

- [ ] **Step 1: Write the failing tests**

```python
def sec(text): return parse_lyrics("## Verse\n" + text)[0]

def test_abab_four_matched_is_stable():
    s = analyze_section(sec("I walked out in the night\nThe river took the day\nI followed every light\nAnd begged the dark to stay\n"), LEX)
    assert s.rhyme_scheme == "abab" and s.verdict == "stable"

def test_xxaa_is_open():
    s = analyze_section(sec("Looking through the window\nCoffee on the table\nMorning coming cold\nEverything is old\n"), LEX)
    assert s.rhyme_scheme == "xxaa" and s.verdict == "unstable" and any("open" in r for r in s.reasons)

def test_odd_phrase_count_unstable():
    s = analyze_section(sec("I walked out in the night\nThe river took the day\nI followed every light\n"), LEX)
    assert s.verdict == "unstable" and any("odd" in r for r in s.reasons)

def test_one_line_and_empty_sections_do_not_crash():
    assert analyze_section(sec("Just one line here\n"), LEX).verdict == "unstable"
    assert analyze_section(Section("Verse", "verse", []), LEX).verdict == "undetermined"

def test_chorus_contrast_on_first_line():
    v = sec("I walked out in the night again\nThe river took the light away\n")
    c = parse_lyrics("## Chorus\nHold on\nHold on to me\n")[0]
    r = chorus_contrast(v, c, LEX)
    assert r.contrasts and any(d.startswith("stresses") for d in r.differences)

def test_cli_handles_chorus_without_verse(tmp_path, capsys):
    f = tmp_path / "lyrics.md"; f.write_text("## Chorus\nHold on\nHold on to me\n")
    assert main(["stability", str(f)]) == 0
    assert "no verse" in capsys.readouterr().out
```

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement `stability.py`** and register the subcommand. When there's no verse or no chorus, the contrast output is `{"contrast": null, "note": "no verse to compare"}` or the matching chorus wording.
- [ ] **Step 4: Run to verify pass.**
- [ ] **Step 5: Commit** — `git commit -m "feat(songtools): Pattison stability analysis and chorus contrast"`

---

### Task 6: Point-of-view classifier

**Files:**
- Create: `src/songtools/pov.py`, `tests/test_pov.py`

**Interfaces:**
- Produces:
  - `@dataclass PovResult(pov: Literal["direct_address","second_narrative","first_narrative","third_narrative"], i_count: int, you_count: int, third_count: int, generic_you: bool)`
  - `classify_pov(text: str) -> PovResult`
  - `classify_sections(sections: list[Section]) -> dict` with keys `song: PovResult`, `sections: dict[str, PovResult]`, `shift: bool` (True when sections disagree)
  - CLI: `songtools pov LYRICS_FILE`

Rules (Pattison, verified). Text inside straight or curly double quotes is removed first.
- **I-words:** `i me my mine myself i'm i've i'll i'd we us our ours ourselves we're we've we'll`
- **You-words:** `you your yours yourself yourselves you're you've you'll you'd ya`
- **Third-words:** `he him his she her hers they them their theirs`
- **Result:** I and you → direct_address; you only → second_narrative; I only → first_narrative; neither → third_narrative.
- **generic_you** is True if the text contains any of `you never know`, `you know`, `you can't`, `you gotta`, `you have to`, `you get`.

- [ ] **Step 1: Write the failing tests**

```python
@pytest.mark.parametrize("text,pov", [
    ("I love you", "direct_address"), ("You walk alone tonight", "second_narrative"),
    ("I walked her home", "first_narrative"), ("She walked him home", "third_narrative"),
    ('She said "I love you"', "third_narrative")])
def test_four_pattison_povs(text, pov):
    assert classify_pov(text).pov == pov

def test_generic_you_flag():
    assert classify_pov("I wonder, you never know").generic_you

def test_shift_across_sections():
    secs = parse_lyrics("## Verse 1\nI walked her home\n## Verse 2\nYou walk alone\n")
    assert classify_sections(secs)["shift"]
```

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement `pov.py`** and register the subcommand.
- [ ] **Step 4: Run to verify pass.**
- [ ] **Step 5: Commit** — `git commit -m "feat(songtools): four-way POV classifier"`

---

### Task 7: Cliché scanner

**Files:**
- Create: `src/songtools/cliche.py`, `data/cliches.json`, `tests/test_cliche.py`

**Interfaces:**
- Consumes: `Section`, `end_word`.
- Produces:
  - `@dataclass ClicheHit(line_number: int, kind: Literal["rhyme_pair","phrase","abstract","stock_image","emotion_naming"], match: str, source: str)`
  - `load_cliches(path: Path | None = None) -> dict`. Defaults to `data/cliches.json`; a user file passed with `--extra` is merged in.
  - `scan(sections: list[Section], cliches: dict, strict: bool = False) -> list[ClicheHit]`
  - CLI: `songtools cliche LYRICS_FILE [--strict] [--extra FILE]`

`data/cliches.json` seed. Each entry carries a `source`:
- `rhyme_pairs`, source `"Pattison (verified)"`: love/dove, love/above, fire/desire, hand/understand, eyes/realize, home/roam, home/alone.
- `abstract`, source `"BMI (as reported)"`: sad, beautiful, special, amazing, wonderful, perfect, happy, lonely, pain, feelings.
- `stock_image`, source `"commentary (unverified)"`: neon, echoes, shadows, whisper, city lights, rise above, broken wings, heart of gold.
- `emotion_naming`, source `"Davis (as reported)"`: the phrases `i feel so`, `my heart is breaking`, `i'm so lonely`, `filled with joy`.
- `phrases`: empty list, for the writer to add to.

The `strict` setting:
- **Normal** scans rhyme_pairs (adjacent and alternate end words), phrases and abstract.
- **Strict** adds stock_image and emotion_naming. Strict is used on the plugin's own drafts.

- [ ] **Step 1: Write the failing tests**

```python
def test_cliche_rhyme_pair_pattison():
    secs = parse_lyrics("## Verse\nMy heart is on fire\nBurning with desire\n")
    hits = scan(secs, load_cliches())
    assert any(h.kind == "rhyme_pair" and h.match == "fire/desire" and "Pattison" in h.source for h in hits)

def test_stock_image_only_in_strict():
    secs = parse_lyrics("## Verse\nUnder neon light we ran\n")
    assert not [h for h in scan(secs, load_cliches()) if h.kind == "stock_image"]
    assert [h for h in scan(secs, load_cliches(), strict=True) if h.kind == "stock_image"]

def test_word_boundaries():
    secs = parse_lyrics("## Verse\nThe sadness of Saddleback\n")
    assert not [h for h in scan(secs, load_cliches()) if h.match == "sad"]
```

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement `cliche.py`** (case-insensitive, whole-word matching) and register the subcommand.
- [ ] **Step 4: Run to verify pass.**
- [ ] **Step 5: Commit** — `git commit -m "feat(songtools): cliché scanner with strict mode"`

---

### Task 8: Prosody: syllables, metric grid, scoring and proposals

**Files:**
- Create: `src/songtools/prosody.py`, `tests/test_prosody.py`

**Interfaces:**
- Consumes: `Lexicon`, `word_class`, `Line`, `parse_melody_md`, `format_melody_entry`.
- Produces:
  - `@dataclass Syl(word: str, label: str, index_in_word: int, word_len: int, stress: int, word_class: str, estimated: bool)`. `stress` follows the three tiers: CMU digit inside polysyllables; 1 for content monosyllables; 0 for function monosyllables; a two-syllable function word's primary stress demoted to 2.
  - `syllabify(lyric: str, lex: Lexicon) -> list[Syl]`. `label` is a syllable spelling for display; when the split is ambiguous, split the letters evenly.
  - `strength(slot: int) -> int`: 4 if `slot % 8 == 0`, 3 if `% 8 == 4`, 2 if even, otherwise 1.
  - `@dataclass Flag(rule: str, syllable: int, slot: int, weight: int, severity: Literal["strong","soft"], message: str)`
  - `@dataclass ProsodyReport(score: int, flags: list[Flag], best_score: int, best_slots: list[int], notation: str, limit: str)`
  - `score(syls: list[Syl], slots: list[int], line_slots: int = 16) -> tuple[int, list[Flag]]`
  - `propose(syls: list[Syl], bars: int = 2) -> list[int]`
  - `check(syls: list[Syl], slots: list[int] | None, bars: int = 2) -> ProsodyReport`. With `slots=None`, reports the proposal.
  - `notation(syls: list[Syl], slots: list[int]) -> str`. A `|` before every slot that is a multiple of 8, labels upper-case on even slots, joined with spaces, word-internal syllables joined with `-`.
  - `compare_lines(a: list[Syl], b: list[Syl]) -> dict` with keys `syllables: [int, int]` and `stress_pattern: [str, str]` ("1" for stress ≥ 1, else "0"), plus `matches: bool`.
  - `LIMIT`: the Global Constraints limit sentence.
  - CLI: `songtools prosody SONG_DIR --section NAME --line N [--slots "0 1 2 …"] [--compare]`. Reads `lyrics.md`, and `melody.md` when no `--slots` is given. `--compare` checks the same line index in every section of the same kind.

Ranked constraints (simplified from Hayes 2005; weights fixed here). An **effective slot** is the syllable's slot, except that a syllable on an odd slot whose next onset is more than one slot later counts at slot + 1 (an anticipation, per Pattison and Temperley). **Duration** is the gap to the next onset; the last syllable runs to `line_slots`.

| Rule | Weight | Severity | Fires when |
|---|---|---|---|
| `INVERSION` | 100 | strong | inside one polysyllabic word, a stress-0 syllable has a higher `strength` than the word's stress-1 syllable |
| `STRESSED_OFFBEAT` | 10 | soft | a stress-1 syllable sits at effective strength 1, unless its duration is 2 slots or more (accented syncopation, per Smith 2024) |
| `UNSTRESSED_DOWNBEAT` | 6 | soft | a stress-0 syllable of a polysyllabic word sits at effective strength 4 |
| `LAPSE` | 5 | soft | 3 or more empty slots between consecutive onsets |
| `FUNCTION_DOWNBEAT` | 3 | soft | a function monosyllable sits at effective strength 4 |
| `EMPTY_DOWNBEAT` | 1 | soft | slot 0 has no onset and no anticipation into it |

`propose` uses dynamic programming over syllables × slots, with slots from −3 to `bars*8 − 1`, strictly increasing. The cost is the sum of the weights above; lapse and anticipation depend only on consecutive pairs. Break ties with the lexicographically smallest slot list.

- [ ] **Step 1: Write the failing tests**

```python
def syls(t): return syllabify(t, LEX)

def test_three_tier_stress():
    s = syls("before the river")
    assert [x.stress for x in s] == [0, 2, 0, 1, 0]    # be-FORE demoted, "the" function, RIV-er

def test_strength_hierarchy():
    assert [strength(i) for i in range(8)] == [4, 1, 2, 1, 3, 1, 2, 1]

def test_proposal_puts_stresses_on_beats():
    s = syls("I was walking down to the river")
    slots = propose(s)
    assert all(slot % 2 == 0 for x, slot in zip(s, slots) if x.stress == 1)

def test_unconditionally_inversion_is_strong():           # Pattison, verified example
    s = syls("unconditionally")                          # un-con-DI-tion-al-ly
    _, flags = score(s, [1, 2, 3, 5, 6, 8])              # "di" on slot 3, "-ly" on slot 8 (downbeat)
    assert any(f.rule == "INVERSION" and f.severity == "strong" for f in flags)

def test_function_word_on_downbeat_flagged():
    s = syls("the river")
    _, flags = score(s, [0, 2, 3])
    assert any(f.rule == "FUNCTION_DOWNBEAT" for f in flags)

def test_accented_syncopation_not_flagged():
    s = syls("bad guy")
    _, flags = score(s, [3, 7])                            # long notes on off-beats
    assert not [f for f in flags if f.rule == "STRESSED_OFFBEAT"]

def test_anticipation_counts_as_beat():
    s = syls("river")
    _, flags = score(s, [7, 9])                            # "riv" one eighth before slot 8
    assert not [f for f in flags if f.rule == "STRESSED_OFFBEAT"]

def test_report_includes_limit_and_best():
    r = check(syls("I was walking down to the river"), None)
    assert r.limit == LIMIT and r.score == r.best_score and "|" in r.notation

def test_compare_lines_mismatch():
    c = compare_lines(syls("I was walking down to the river"), syls("She ran away"))
    assert not c["matches"] and c["syllables"] == [9, 4]

def test_long_line_is_fast():
    import time; t = time.perf_counter()
    propose(syls("and every single morning I am walking down along the muddy river"), bars=3)
    assert time.perf_counter() - t < 1.0

def test_estimated_word_marked():
    assert any(x.estimated for x in syls("zorbletastic river"))
```

Adjust the expected syllable counts in `test_compare_lines_mismatch` only if CMU gives a different count for these exact words, and record the CMU entry in a comment.

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement `prosody.py`** with the signatures and constraint table above, and register the subcommand. The JSON output always includes `limit`.
- [ ] **Step 4: Run to verify pass.**
- [ ] **Step 5: Commit** — `git commit -m "feat(songtools): Hayes-style prosody scorer and setting proposals"`

---

### Task 9: Chord spelling, parsing, naming and transposition

**Files:**
- Create: `src/songtools/chords.py`, `tests/test_chords.py`

**Interfaces:**
- Produces:
  - `NOTE_PC: dict[str, int]`, accepting `C C# Db … B` with `#`, `b`, `♯` and `♭`
  - `spell(pc: int, key: str | None = None) -> str`. Flat keys `F Bb Eb Ab Db Gb Dm Gm Cm Fm Bbm Ebm` use flats; otherwise sharps.
  - `@dataclass Chord(symbol: str, root: str, quality: str, bass: str | None, pcs: frozenset[int], tones: list[str])`
  - `QUALITIES: dict[str, tuple[int, ...]]` with intervals from the root, covering at least: `"": (0,4,7)`, `m`, `5`, `6`, `m6`, `7`, `maj7`, `m7`, `m7b5`, `dim`, `dim7`, `aug`, `sus2`, `sus4`, `add9`, `9`, `7#9`, `7sus4`, `69`, `mmaj7`, `11`, `13`
  - `parse_chord(symbol: str) -> Chord`. Uses pychord for the quality parse, with our own root and bass handling. Raises `ValueError` for invalid symbols. `Gsus` is read as `Gsus4`.
  - `transpose(symbol: str, semitones: int, key: str | None = None) -> str`. Root and bass are moved separately and respelled for the key.
  - `names_for(pcs: set[int], bass_pc: int | None = None) -> list[str]`. Every root × quality whose pitch-class set equals `pcs`, or equals it with the fifth missing (named with the suffix `(no5)`). A slash is added when the bass isn't the root. Names whose root is the bass come first.
  - `is_no_chord(symbol: str) -> bool` for `N.C.`, `NC` and `N/C`
  - CLI: `songtools chord spell|transpose|names …`, for example `chord transpose G/B 2`, `chord names C E A --bass C`

- [ ] **Step 1: Write the failing tests**

```python
def test_flat_input_and_key_aware_spelling():
    assert parse_chord("Bb").tones == ["Bb", "D", "F"]
    assert spell(10, "F") == "Bb" and spell(10, "E") == "A#"

def test_slash_chord_transposition_fixes_pychord_bug():
    assert transpose("G/B", 2) == "A/C#"
    assert transpose("C/Bb", 2, key="D") == "D/C"

@pytest.mark.parametrize("sym,pcs", [("Cadd9", {0,4,7,2}), ("Dsus4", {2,7,9}),
                                     ("E7#9", {4,8,11,2,7}), ("Bbmaj7", {10,2,5,9}), ("Gsus", {7,0,2})])
def test_parse_qualities(sym, pcs):
    assert parse_chord(sym).pcs == frozenset(pcs)

def test_am7_and_c6_share_notes():
    names = names_for({9, 0, 4, 7}, bass_pc=9)
    assert names[0] == "Am7" and "C6/A" in names

def test_open_c_shape_x32210_names():                    # C E A over C
    names = names_for({0, 4, 9}, bass_pc=0)
    assert "Am/C" in names and "C6(no5)" in names

def test_invalid_and_no_chord():
    assert is_no_chord("N.C.")
    with pytest.raises(ValueError): parse_chord("H7")

def test_music21_oracle_agrees_on_spelling():
    import music21
    for sym in ["Cadd9", "G/B", "Dsus4", "Am7", "C6", "E7#9", "Bm/A"]:
        ours = parse_chord(sym).pcs
        m21 = frozenset(p.pitchClass for p in music21.harmony.ChordSymbol(sym).pitches)
        assert ours == m21, sym
```

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement `chords.py`** and register the `chord` subcommand group.
- [ ] **Step 4: Run to verify pass.**
- [ ] **Step 5: Commit** — `git commit -m "feat(songtools): chord parsing, naming and key-aware transposition"`

---

### Task 10: Guitar fretboard: tunings, capo, verification, V-System, capo search

**Files:**
- Create: `src/songtools/fretboard.py`, `data/tunings.json`, `tests/test_fretboard.py`

**Interfaces:**
- Consumes: `names_for`, `parse_chord`, `transpose`, `NOTE_PC`, `data/chords-db/guitar.json`.
- Produces:
  - `@dataclass Tuning(name: str, strings: list[int])`, MIDI numbers low to high; `load_tuning(name_or_notes: str) -> Tuning`, accepting a name from `tunings.json` or six note names such as `"D2 A2 D3 G3 A3 D4"`
  - `@dataclass Capo(fret: int, strings: tuple[bool, ...] | None = None)`. `None` means all strings.
  - `parse_shape(s: str) -> list[int | None]`. Single digits (`x32010`), or separated by spaces or commas when any fret is 10 or higher. Frets are relative to the capo.
  - `sounding(shape, tuning, capo=Capo(0)) -> list[int | None]`
  - `identify(shape, tuning, capo=Capo(0)) -> list[str]`, using `names_for` with the bass as the lowest sounding note
  - `@dataclass Verify(ok: bool, missing: list[str], extra: list[str], alternatives: list[str], note: str)`; `verify(shape, name, tuning, capo=Capo(0), band_bass: bool = False) -> Verify`. A missing fifth is allowed; a missing root is allowed when `band_bass`.
  - `vsystem(midi: list[int]) -> str | None`
  - `joni_code(tuning: Tuning) -> str`
  - `@dataclass CapoOption(fret: int, shapes: list[str], open_shapes: int, note: str)`; `capo_options(chords: list[str], tuning: Tuning, max_fret: int = 7) -> list[CapoOption]`
  - `voicings(name: str, tuning: Tuning, limit: int = 8) -> list[str]`. From chords-db in standard tuning; otherwise generated.
  - CLI: `songtools guitar identify|verify|vsystem|joni|capo|voicings …` (with `--tuning`, `--capo N`, `--partial-capo 011100`)

Data and algorithms:
- `tunings.json` (Wikipedia, verified):
  - standard `E2 A2 D3 G3 B3 E4`
  - drop_d `D2 A2 D3 G3 B3 E4`
  - dadgad `D2 A2 D3 G3 A3 D4`
  - open_g `D2 G2 D3 G3 B3 D4`
  - open_d `D2 A2 D3 F#3 A3 D4`
  - open_e `E2 B2 E3 G#3 B3 E4`
  - open_c `C2 G2 C3 G3 C4 E4`
- **chords-db:** `frets` are relative to `baseFret`. A fret value f > 0 means the absolute fret `baseFret + f − 1`, and −1 means muted. Keys `Csharp` and `Fsharp` mean C# and F#.
- **`vsystem`** (Greene Method 1, as reconstructed by Hober; verified table). It needs 4 distinct pitch classes, otherwise returns None.
  1. Sort the pitches and label them B, T, A, S from low to high.
  2. Order the voices by their chord-tone position in ascending chromatic order, starting from the bass's pitch class.
  3. Look the 4-letter formula up in:
     - `V-1: BTAS SBTA ASBT TASB`
     - `V-2: TABS STAB BSTA ABST`
     - `V-3: ABTS SABT TSAB BTSA`
     - `V-4: STBA ASTB BAST TBAS`
     - `V-5: BATS SBAT TSBA ATSB`
     - `V-8: TBSA ATBS SATB BSAT`
  4. Then adjust for adjacent gaps of 12 semitones or more: B–T: V-1→V-6, V-2→V-7, V-3→V-12. T–A: V-1→V-13, V-2→V-10. A–S: V-1→V-14, V-2→V-9, V-4→V-11.
- **`joni_code`:** the lowest string's note name (no octave), then the semitone gap between each pair of adjacent strings.
- **`capo_options`:**
  1. For each fret 0 to `max_fret`, transpose every chord down by that fret.
  2. Count the shapes that have a chords-db position with `baseFret == 1` and at least one open string.
  3. Sort by `open_shapes` descending, then by fret ascending.
  4. For frets ≥ 7, add the note `"soft heuristic: tone thins high on the neck (no source)"`.

- [ ] **Step 1: Write the failing tests**

```python
STD = load_tuning("standard")

def test_open_c_sounds_and_identifies():
    sh = parse_shape("x32010")
    assert sounding(sh, STD) == [None, 48, 52, 55, 60, 64]
    assert identify(sh, STD)[0] == "C"

def test_capo_two_am_shape_is_bm():
    assert identify(parse_shape("x02210"), STD, Capo(2))[0] == "Bm"

def test_partial_capo_esus():                          # A, D, G strings clamped at 2
    assert "Esus4" in identify(parse_shape("000000"), STD, Capo(2, (False, True, True, True, False, False)))

def test_verify_reports_extra_tone_and_alternative():
    v = verify(parse_shape("x32000"), "C", STD)
    assert not v.ok and v.extra == ["B"] and "Cmaj7" in v.alternatives

def test_verify_allows_missing_fifth():
    assert verify(parse_shape("x3201x"), "C", STD).ok

@pytest.mark.parametrize("notes,group", [
    ([60, 64, 67, 71], "V-1"), ([55, 60, 64, 71], "V-2"), ([52, 60, 67, 71], "V-4"),
    ([48, 55, 64, 71], "V-5"), ([56, 63, 64, 71], "V-2")])   # last: Hober's Emaj7 example
def test_vsystem_groups(notes, group):
    assert vsystem(notes) == group

def test_vsystem_needs_four_distinct_pcs():
    assert vsystem([48, 52, 55, 60]) is None

@pytest.mark.parametrize("name,code", [("standard", "E55545"), ("dadgad", "D75525"), ("open_g", "D57543")])
def test_joni_codes(name, code):
    assert joni_code(load_tuning(name)) == code

def test_capo_search_finds_open_shapes_for_flat_keys():
    top = capo_options(["Bb", "Eb", "F"], STD)[0]
    assert top.fret in (1, 3) and top.open_shapes == 3

def test_voicings_from_chords_db():
    assert "x32010" in voicings("C", STD)
```

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement `fretboard.py`** and register the `guitar` subcommand group. For alternate tunings, `voicings` searches frets 0 to 5 within a 4-fret span and keeps the shapes whose `identify` result begins with the requested name.
- [ ] **Step 4: Run to verify pass.**
- [ ] **Step 5: Commit** — `git commit -m "feat(songtools): fretboard verification, V-System, capo search"`

---

### Task 11: Harmony analysis

**Files:**
- Create: `src/songtools/harmony.py`, `tests/test_harmony.py`

**Interfaces:**
- Consumes: `parse_chord`, `is_no_chord`, `spell`.
- Produces:
  - `@dataclass KeyCandidate(tonic: str, mode: Literal["major","minor","mixolydian","dorian"], score: float)`
  - `@dataclass HarmonyAnalysis(key: KeyCandidate, confidence: float, system: str, system_label: str, numerals: list[str], nashville: list[str], symbols: list[str], notes: list[str], dual_reading: dict | None, errors: list[str])`
  - `numeral(chord: Chord, tonic: str) -> str`, relative to the parallel major. Upper case for major, lower case for minor, `°` for diminished, `ø` for half-diminished, with accidentals such as `bVII` and `bVI`; an extension suffix such as `7` is kept.
  - `nashville(chord: Chord, tonic: str) -> str`, for example `1 4 5 6m b7 1/3`
  - `analyze(chords: list[str], key: str | None = None) -> HarmonyAnalysis`
  - `analyze_song(progressions: dict[str, list[tuple[str, float]]]) -> dict`. Analyses each section, then adds a song-level `modulations` list. A last-chorus tonic raised by 1 or 2 semitones is noted as a `"truck-driver lift (Everett 3b)"`.
  - `CORPUS = {"root_share": {"I": 32.8, "IV": 22.6, "V": 16.3, "bVII": 8.1, "VI": 7.2, "bVI": 4.0}, "chorus_cadence_pre_tonic": {"V": 32.0, "IV": 18.5}}` (de Clercq & Temperley, verified)
  - CLI: `songtools harmony CHORD… [--key K]`, or `songtools harmony --music FILE`

**Key scoring.** For each of the 12 tonics × 4 modes:

```
score = 2*[first chord root == tonic] + 3*[last chord root == tonic]
      + sum over chords of [chord pcs ⊆ mode scale] + sum over chords of [root == tonic]
```

- Ties go to major (the listener bias Richards reports).
- `confidence = top / (top + second)`.
- `dual_reading` is set when a second candidate with a different tonic is within 15% of the top. It holds that candidate's tonic, mode and numerals.
- An explicit `key` fixes the tonic and mode.

**System classification** is a simplified version of Everett's Table 1, and the label says so. The first matching rule wins:

| System | Rule |
|---|---|
| `5` | every chord is a power chord (`…5`) with its root in the tonic's minor pentatonic |
| `4` | I7 and IV7 both present |
| `1b` | minor tonic and a major V present |
| `3a` | major tonic, V present, and at least one of bVII, bVI, bIII or iv present |
| `1a` | major tonic, every chord diatonic to the major scale |
| `2` | every chord diatonic to the selected mode (mixolydian, dorian, or aeolian minor without V) |
| `6a` | otherwise (chromatic) |

**Notes.** Add each of these when it applies:
- `"double-plagal ♭VII–IV–I (Everett: chromatic descending fourths, not modal)"` when that subsequence occurs.
- `"V–I is still the most common chorus-ending cadence (32%); IV–I 18.5%"` when the last two numerals are IV–I or V–I.

Invalid symbols are skipped and recorded in `errors`. `N.C.` is skipped silently.

- [ ] **Step 1: Write the failing tests**

```python
def test_major_functional():
    a = analyze(["G", "C", "D", "G"])
    assert (a.key.tonic, a.key.mode, a.system) == ("G", "major", "1a")
    assert a.numerals == ["I", "IV", "V", "I"] and a.nashville == ["1", "4", "5", "1"]

def test_mixolydian_double_plagal():
    a = analyze(["G", "F", "C", "G"])
    assert a.numerals == ["I", "bVII", "IV", "I"] and a.system == "2"
    assert any("double-plagal" in n for n in a.notes)

def test_mixture_with_dominant():
    assert analyze(["G", "F", "C", "G", "D", "G"], key="G").system == "3a"

def test_axis_loop_dual_reading_major_bias():
    a = analyze(["C", "G", "Am", "F"])
    assert a.key.tonic == "C" and a.dual_reading and a.dual_reading["tonic"] == "A"

def test_blues_and_power_chord_systems():
    assert analyze(["A7", "D7", "A7", "E7"]).system == "4"
    assert analyze(["E5", "G5", "A5", "E5"]).system == "5"

def test_invalid_chords_reported_and_nc_skipped():
    a = analyze(["G", "N.C.", "H7", "C", "G"])
    assert a.errors == ["H7"] and a.numerals == ["I", "IV", "I"]

def test_truck_driver_lift():
    r = analyze_song({"Chorus 1": [("C", 4), ("F", 4), ("G", 4), ("C", 4)],
                      "Chorus 2": [("D", 4), ("G", 4), ("A", 4), ("D", 4)]})
    assert any("truck-driver" in m for m in r["modulations"])

def test_music21_oracle_numerals_in_major():
    import music21
    rn = music21.roman.romanNumeralFromChord(music21.chord.Chord(["F", "A", "C"]), music21.key.Key("G"))
    assert rn.figure in ("bVII", "-VII") and numeral(parse_chord("F"), "G") == "bVII"
```

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement `harmony.py`** and register the subcommand.
- [ ] **Step 4: Run to verify pass.**
- [ ] **Step 5: Commit** — `git commit -m "feat(songtools): harmony analysis with Everett systems and corpus base rates"`

---

### Task 12: Key fitting

**Files:**
- Create: `src/songtools/keyfit.py`, `tests/test_keyfit.py`

**Interfaces:**
- Consumes: `NOTE_PC`, `spell`, `transpose`.
- Produces:
  - `note_to_midi(n: str) -> int` (`"A2"` → 45) and `midi_to_note(m: int, key: str | None = None) -> str`
  - `@dataclass KeyFit(key: str, shift: int, fits: bool, low: str, high: str, margin_low: int, margin_high: int, tessitura_offset: float)`
  - `fit_keys(melody_low: str, melody_high: str, voice_low: str, voice_high: str, current_key: str, tessitura: tuple[str, str] | None = None) -> list[KeyFit]`. Tries shifts −6 to +6 and sorts by `fits` first, then by the absolute distance between the tessitura midpoint (or the melody midpoint) and the voice midpoint, then by the absolute shift.
  - `capo_for(key: str) -> list[tuple[int, str]]`. Capo frets 0 to 7 paired with shape keys from `C G D A E Am Em Dm`, where shape + capo = key.
  - CLI: `songtools key --melody-low A2 --melody-high E4 --voice-low G2 --voice-high D4 --key G [--tessitura LOW HIGH]`

- [ ] **Step 1: Write the failing tests**

```python
def test_note_midi_roundtrip():
    assert note_to_midi("A2") == 45 and midi_to_note(61, "F") == "Db4"

def test_lower_voice_moves_key_down():
    top = fit_keys("A2", "E4", "G2", "D4", "G")[0]
    assert (top.key, top.shift, top.fits) == ("F", -2, True)

def test_capo_options_for_f():
    assert {(1, "E"), (3, "D"), (5, "C")} <= set(capo_for("F"))

def test_nothing_fits_is_reported_not_hidden():
    fits = fit_keys("C2", "C5", "G2", "D4", "G")
    assert not any(f.fits for f in fits) and fits[0].margin_high < 0
```

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement `keyfit.py`** and register the subcommand.
- [ ] **Step 4: Run to verify pass.**
- [ ] **Step 5: Commit** — `git commit -m "feat(songtools): tessitura-based key fitting with capo pairing"`

---

### Task 13: Drafts, cuts and kept lines

**Files:**
- Create: `src/songtools/drafts.py`, `tests/test_drafts.py`

**Interfaces:**
- Consumes: `parse_lyrics`, `parse_song_md`, `KeptLine`.
- Produces:
  - `snapshot(song_dir: Path) -> Path`. Copies `lyrics.md` to `drafts/lyrics-v{N}.md`, with N one higher than the largest existing version.
  - `cut(song_dir: Path, text: str, reason: str, today: str) -> Path`. Appends `## {today} — {reason}\n{text}\n` to `cuts/cuts.md`.
  - `@dataclass Change(section: str, index: int, old: str | None, new: str | None, kept_changed: bool)`
  - `diff(old_text: str, new_text: str, kept: list[KeptLine]) -> list[Change]`. Matches sections by name and lines by index within the section. `kept_changed` is True when `old` matches a kept line's text, compared case-insensitively with punctuation stripped.
  - CLI: `songtools drafts snapshot SONG_DIR`, `drafts cut SONG_DIR TEXT --reason R`, `drafts diff OLD NEW [--song SONG_MD]`

- [ ] **Step 1: Write the failing tests**

```python
def test_snapshot_versions(tmp_path):
    (tmp_path / "lyrics.md").write_text("## Verse\nA\n")
    assert snapshot(tmp_path).name == "lyrics-v1.md" and snapshot(tmp_path).name == "lyrics-v2.md"

def test_cut_appends_never_overwrites(tmp_path):
    cut(tmp_path, "old verse", "too long", "2026-11-08"); cut(tmp_path, "other", "cliche", "2026-11-09")
    body = (tmp_path / "cuts" / "cuts.md").read_text()
    assert "old verse" in body and "other" in body

def test_diff_flags_changed_kept_line():
    kept = [KeptLine("Down to the river", "cliche", "echo", "2026-11-08")]
    ch = diff("## Verse\nDown to the river,\n", "## Verse\nDown to the water\n", kept)
    assert ch == [Change("Verse", 1, "Down to the river,", "Down to the water", True)]
```

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement `drafts.py`** and register the subcommand group. `today` defaults to `date.today().isoformat()` in the CLI only.
- [ ] **Step 4: Run to verify pass.**
- [ ] **Step 5: Commit** — `git commit -m "feat(songtools): draft snapshots, cut pool, kept-line diff"`

---

### Task 14: ChordPro reader and writer

**Files:**
- Create: `src/songtools/chordpro.py`, `tests/test_chordpro.py`

**Interfaces:**
- Consumes: `Section`, `SongRecord`, `transpose`.
- Produces:
  - `@dataclass CPSection(kind: str, label: str, lines: list[str])`. `kind` ∈ `verse, chorus, bridge, other`, and the lines are raw ChordPro lines with `[C]` chords.
  - `@dataclass ChordProSong(meta: dict[str, str], sections: list[CPSection], defines: list[str])`
  - `parse(text: str) -> ChordProSong`. Supports `{title|t}`, `{artist}`, `{key}`, `{capo}`, `{tempo}`, `{time}`, `{comment|c}`, `{define}`, and `{start_of_X|soX}` / `{end_of_X|eoX}` for verse, chorus and bridge with an optional label (`{start_of_verse: Verse 1}`). Unknown directives are kept in `meta` under `_unknown`.
  - `write(song: ChordProSong) -> str`. The canonical form uses the long directive names in the order `title, artist, key, capo, tempo, time`, then the defines, then the sections separated by one blank line.
  - `from_song(sections: list[Section], record: SongRecord) -> ChordProSong`. Kinds outside verse, chorus and bridge use `{comment: <name>}` with plain lines.
  - `concert_pitch(song: ChordProSong) -> ChordProSong`. Moves every chord up by `capo`, removes `{capo}`, and sets `{key}` to the sounding key.
  - CLI: `songtools chart SONG_DIR [--concert] [--pdf]`. Writes `out/chart.cho` (and `out/chart-concert.cho`), plus the PDFs once Task 15 lands.

- [ ] **Step 1: Write the failing tests**

```python
CANON = ("{title: River}\n{key: G}\n{capo: 2}\n{tempo: 96}\n\n"
         "{start_of_verse: Verse 1}\n[G]I was walking [C]down\n{end_of_verse}\n\n"
         "{start_of_chorus: Chorus}\n[D]Hold on\n{end_of_chorus}\n")

def test_roundtrip_canonical():
    assert write(parse(CANON)) == CANON

def test_short_directives_parse():
    s = parse("{t: X}\n{soc}\n[G]hi\n{eoc}\n")
    assert s.meta["title"] == "X" and s.sections[0].kind == "chorus"

def test_concert_pitch_moves_chords_and_key():
    c = concert_pitch(parse(CANON))
    assert "capo" not in c.meta and c.meta["key"] == "A" and c.sections[0].lines[0].startswith("[A]")

def test_from_song_builds_sections():
    secs = parse_lyrics("## Verse 1\n[G]I was walking\n## Intro\nhum\n")
    rec = parse_song_md("# River\n## Core\nkey: G\n")
    out = write(from_song(secs, rec))
    assert "{start_of_verse: Verse 1}" in out and "{comment: Intro}" in out
```

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement `chordpro.py`** and register the `chart` subcommand (ChordPro output only).
- [ ] **Step 4: Run to verify pass.**
- [ ] **Step 5: Commit** — `git commit -m "feat(songtools): ChordPro subset reader/writer with concert pitch"`

---

### Task 15: PDF lead sheet and MIDI reference track

**Files:**
- Create: `src/songtools/pdf.py`, `src/songtools/midi.py`, `tests/test_pdf.py`, `tests/test_midi.py`
- Modify: `src/songtools/chordpro.py`, so that the `chart --pdf` handler calls `render_pdf`

**Interfaces:**
- Consumes: `ChordProSong`, `parse_music_md`, `parse_chord`, `data/fonts/`.
- Produces:
  - `chord_positions(line: str, font: str, size: float) -> tuple[str, list[tuple[float, str]]]`. Returns the lyric text and the x-offset of each chord, measured with `reportlab.pdfbase.pdfmetrics.stringWidth`.
  - `render_pdf(song: ChordProSong, out: Path) -> Path`. US Letter, Lato registered as a TTF. The title in bold at 18 pt; the key, capo and tempo line at 10 pt; section labels in bold at 11 pt; chords in bold at 10 pt above the lyrics at 11 pt; a new page when the content runs past the bottom margin.
  - `write_midi(progression: list[tuple[str, float]], tempo_bpm: int, out: Path, key: str | None = None, time: str = "4/4") -> Path`. 480 ticks per beat. Each chord plays its root at `36 + root_pc` together with its chord tones stacked upward from `60 + pc` (wrapping above 71 down an octave), velocity 80, held for its beat count. Includes `set_tempo`, `time_signature`, and `key_signature` when the key is given. `N.C.` becomes a rest.
  - CLI: `songtools midi SONG_DIR [--tempo N]` (default from `song.md` core `tempo`), writing `out/guide.mid` from `music.md` sections in file order.

- [ ] **Step 1: Write the failing tests**

```python
def test_chord_positions_monotonic():
    text, pos = chord_positions("[G]I was walking [C]down", "Lato", 11)
    assert text == "I was walking down" and pos[0] == (0.0, "G") and pos[1][0] > 0

def test_render_pdf_with_unicode(tmp_path):
    s = parse("{title: Señor — “Test”}\n{start_of_verse}\n[G]Ñandú — “quoted”\n{end_of_verse}\n")
    out = render_pdf(s, tmp_path / "c.pdf")
    data = out.read_bytes()
    assert data.startswith(b"%PDF") and data.count(b"/Type /Page") >= 1

def test_midi_tempo_and_notes(tmp_path):
    import mido
    out = write_midi([("G", 4), ("N.C.", 2), ("C", 4)], 96, tmp_path / "g.mid", key="G")
    mf = mido.MidiFile(out)
    msgs = [m for t in mf.tracks for m in t]
    assert any(m.type == "set_tempo" and m.tempo == mido.bpm2tempo(96) for m in msgs)
    ons = [m.note for m in msgs if m.type == "note_on" and m.velocity > 0]
    assert ons == [43, 67, 71, 62, 36, 60, 64, 67]       # G: root 36+7, tones from 60+pc; rest; C
```

- [ ] **Step 2: Run to verify failure.**
- [ ] **Step 3: Implement `pdf.py` and `midi.py`.** Wire `chart --pdf` to write `out/chart.pdf` (and `out/chart-concert.pdf` with `--concert`), and register `midi`.
- [ ] **Step 4: Run to verify pass.**
- [ ] **Step 5: Commit** — `git commit -m "feat(songtools): PDF lead sheets and MIDI reference tracks"`

---

### Task 16: End-to-end sample song, text output and toolkit README

**Files:**
- Create: `tests/fixtures/sample_song/{song.md,lyrics.md,music.md,melody.md}`, `tests/test_e2e.py`, `songtools/README.md`
- Modify: every module's `to_text`, if a test below shows it missing

**Interfaces:**
- Consumes: every subcommand.

The sample song is original, with two verses, a chorus and a bridge in G with capo 2, tempo 96, and inline chords. `melody.md` has one confirmed line, and `song.md` has one kept line. Write the lyric fresh for the fixture and don't reuse any line from a published song.

- [ ] **Step 1: Write the failing end-to-end tests**

```python
SUBCOMMANDS = [
    ["stability", "{d}/lyrics.md"], ["pov", "{d}/lyrics.md"], ["cliche", "{d}/lyrics.md", "--strict"],
    ["prosody", "{d}", "--section", "Verse 1", "--line", "1"], ["rhyme", "line", "time"],
    ["harmony", "--music", "{d}/music.md"], ["key", "--melody-low", "A2", "--melody-high", "E4",
     "--voice-low", "G2", "--voice-high", "D4", "--key", "G"],
    ["guitar", "identify", "x32010"], ["chart", "{d}", "--concert", "--pdf"], ["midi", "{d}"],
    ["drafts", "snapshot", "{d}"]]

@pytest.mark.parametrize("argv", SUBCOMMANDS)
@pytest.mark.parametrize("text", [False, True])
def test_every_subcommand_runs_on_sample(argv, text, sample_dir, capsys):
    args = [a.format(d=sample_dir) for a in argv]
    assert main((["--text"] if text else []) + args) == 0
    out = capsys.readouterr().out
    if not text:
        json.loads(out)
    else:
        assert out.strip() and not out.lstrip().startswith("{")

def test_outputs_written(sample_dir):
    main(["chart", str(sample_dir), "--concert", "--pdf"]); main(["midi", str(sample_dir)])
    for f in ["chart.cho", "chart-concert.cho", "chart.pdf", "chart-concert.pdf", "guide.mid"]:
        assert (sample_dir / "out" / f).exists()

def test_malformed_file_error_has_location(tmp_path, capsys):
    (tmp_path / "lyrics.md").write_text("## Verse\n[G broken\n")
    assert main(["stability", str(tmp_path / "lyrics.md")]) == 2
    assert "lyrics.md:2:" in capsys.readouterr().err

def test_installed_size_under_budget():
    import importlib.metadata as md, pathlib
    runtime = {"pychord", "reportlab", "mido", "songtools"}
    total = sum(f.locate().stat().st_size for d in md.distributions()
                if d.metadata["Name"].lower() in runtime for f in d.files or [] if f.locate().exists())
    assert total < 25_000_000
```

`sample_dir` is a fixture that copies `tests/fixtures/sample_song` into `tmp_path`.

- [ ] **Step 2: Run to verify failure.** Expect `to_text` gaps or path issues.
- [ ] **Step 3: Fill the gaps and write `songtools/README.md`.** The README covers the command list, file formats (copied from Task 2), the data sources with their licences, the prosody limit sentence, and the rule that the toolkit never invents a result.
- [ ] **Step 4: Run the full suite** — `uv run --frozen pytest -v`. Expected: all pass, network disabled, no GPL-family licences.
- [ ] **Step 5: Commit and push** — `git commit -m "test(songtools): end-to-end sample song and README"` then `git push -u origin claude/dazzling-feynman-furauz`

---

## After this plan

Plan 2 (guides, skills and packaging, spec build steps 4–6) is written once this plan ships. It will consume these subcommands and their JSON shapes, and its first task checks the `UV_PROJECT_ENVIRONMENT` + `--project` invocation from inside a skill.
