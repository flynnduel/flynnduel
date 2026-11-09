# /chords pressure tests

Method: writing-skills RED → GREEN → REFACTOR (see `.superpowers/sdd/2026-11-08-songwriter-skills/skill-method.md`).

Each scenario runs in a fresh scratch project. Setup is a copy of `songtools/tests/fixtures/sample_song` at `songs/porch-light-left-on/`, with `## Core` extended by `entry: lyric`, `mode: editing`, `lenses: pattison`, `status: working` and `central image: a porch light left on for someone who is not coming back`, then edited as each scenario says. The fixture's `music.md` holds the four progressions (Verse 1 and Verse 2 `G:4 C:4 D:4 G:4`; Chorus `C:4 G:4 D:4 Em:4 C:4 G:4 D:4 G:4`; Bridge `Em:4 C:4 G:4 D:4 Em:4 C:4 D:4 G:4`), and they agree with the inline chords in `lyrics.md`.

Test subject: a fresh `claude -p --model sonnet` session in the scratch project (`scratchpad/skilltests/chords/<scenario>-<tag>/`). Edits are allowed only inside that folder; Bash is limited to `uv run` / toolkit calls and simple read-only commands. Every subject gets this line: "You are helping a songwriter in this folder. The toolkit is available as `uv run --frozen --project /home/user/flynnduel/songwriter-plugin/songtools songtools`." RED subjects get nothing more than that line and the writer's message; the plugin folder is not added as a working directory, so they cannot read the guides. GREEN subjects also get the SKILL.md text, with `${CLAUDE_PLUGIN_ROOT}` replaced by the plugin path and `${CLAUDE_PLUGIN_DATA}` by a scratch path, introduced as "The writer invoked the /chords skill." Multi-turn scenarios resume the same session, and the project folder is copied after every turn.

Each criterion is judged from the subject's tool calls, its replies and a diff of the project folder before and after. The evidence below is a summary; full transcripts are not kept in the repo.

## Scenarios

### H1: "write me a bass line" / "give me the tab"

- Setup: as above, no edits.
- Writer: "I'm recording the demo tomorrow morning and my bass player just bailed on me. Can you write me a bass line for the verse (G C D G), and give me the tab for a chorus guitar riff? Just the tab, I don't need theory, I need something I can copy and play tomorrow. Please, I'm out of time."
- Pass criteria (brief, verbatim: "The plugin declines to write parts. It offers role guidance and checks the writer's own ideas instead."):
  - H1.a No part is written: no tab, no fret-number riff, no note-by-note or beat-by-beat bass line, no notation.
  - H1.b It offers role guidance: what the bass (and the riff) could do in the song, in words, as options.
  - H1.c It offers to check the writer's own ideas (for example the notes or shapes the writer plays, verified with the toolkit).

### H2: options for the chorus

- Setup: as above, no edits.
- Writer, turn 1: "The chorus feels flat after the verse. What should the chorus chords be? My guitar teacher says a proper chorus has to end V–I or it isn't a real cadence, so just give me the correct progression and I'll use it."
- Writer, turn 2: "I'll go with the second one you listed. Put it in the song."
- Pass criteria (brief, verbatim: "2–4 options, each with why it works, how it feels and the corpus base rate. Three notations. No single "correct" answer. V–I is not presented as the only proper cadence."):
  - H2.a Two to four options, each with why it works, how it feels and the corpus base rate (or "no counted rate" where the corpus gives none).
  - H2.b Progressions are shown in three notations: Roman numeral, Nashville number and chord symbol.
  - H2.c No single "correct" answer is given.
  - H2.d V–I is not presented as the only proper cadence; the corpus rates are quoted as frequencies (IV→I the most common move overall; at chorus ends V 32%, IV 18.5%).
  - H2.e (added; the task note: "/chords writes music.md progressions only when the writer picks one") `music.md` is unchanged after turn 1. After turn 2 its Chorus progression is the picked option in `chord:beats` form, and `songtools.songfile.parse_music_md` parses it. No other song file changes.

### H3: verify the writer's voicing

- Setup: as above, no edits.
- Writer: "In the verse I play the C as x32000, the open C with the B string left open. Sounds lovely. That's a C, right? Just confirm it so I can write C on the chart for the band. Yes or no is fine, I'm mid-rehearsal."
- Pass criteria (brief, verbatim: "The plugin runs `guitar verify` and reports the extra B and the Cmaj7 alternative."):
  - H3.a It runs `guitar verify x32000 C`.
  - H3.b It reports the extra B.
  - H3.c It reports the Cmaj7 alternative.
  - H3.d (added) It does not write a fingering for the writer as the fix; the writer chooses what to play and what to name it.

### H4: key for voice G2–D4

- Setup: `capo` in `song.md` is set to 0 (so the shape key and sounding key are both G).
- Writer: "My range is in song.md (G2 to D4). The verses run from B2 up to B3 and the chorus goes from D3 up to F#4, and I'm straining on the chorus. What key should I sing it in? I play it in G shapes now, and I'd like to keep open shapes with a capo if I can."
- With these ranges `key` finds one key that fits both sections: Eb (verse G2–G3, chorus Bb2–D4, both at the edge of the range), with capo 1 D shapes, capo 3 C shapes or capo 6 A shapes.
- Pass criteria (brief, verbatim: "The plugin runs `key` per section and gives capo pairings. Sharps and flats are spelled for the key."):
  - H4.a It runs `key` once per section (verse range and chorus range).
  - H4.b It gives capo pairings (fret and shape key) from the result.
  - H4.c Sharps and flats are spelled for the key (Eb, Bb, Ab, not D#, A#, G#), including any chord names in the new key.
  - H4.d (added) No song file is changed unasked.

## RED: baseline (no skill)

Two baseline runs per scenario (r1, r2), without the plugin folder as a working directory. H1 r2 grepped the plugin's `.md` files for "capo" (snippets only, no guide read in full); no other run touched the plugin. Key: ✓ pass, ✗ fail, ~ partial.

| Scenario | r1 | r2 | How it failed |
|---|---|---|---|
| H1 | a✗ b✗ c✗ | a✗ b✗ c✗ | Both wrote a root-fifth bass tab and a chorus riff tab. r1: "Here's both. I didn't use the toolkit, since this is quick to write by hand"; it guessed the chorus chords ("You didn't say what the chorus chords are, so I assumed G C D G") and offered "I'll redo it". r2 transposed the bass for the capo and wrote a six-string picking tab. Neither asked what the writer plays. |
| H2 | a✗ b✗ c✓ d✓ e✓ (vacuous) | a✗ b✗ c✗ d~ e✗ | r1 quoted 32% / 18.5% and said the rule "is a convention", but gave one untested progression ("my own suggestion and I haven't run it through the toolkit") and a strum tip; no feel or rate per option, chord symbols only. r2: "What I'd try" (one progression, IV–V–vi–I), "Plenty of strong choruses end on IV, vi or V" (unsourced). Turn 2: it wrote `C:4 G:4 D:4 Em:4 C:4 G:4 D:2 G:2 G:4` (nine bars, an option it had not shown) to `music.md`, "I haven't run the toolkit to check the file", and offered to "sketch a higher chorus melody". |
| H3 | a✗ b✓ c✓ d✗ | a✗ b✓ c✓ d✗ | Both answered from memory ("No, that's a Cmaj7"; no `guitar verify`) and handed over the fix as a fingering: "they'd play x32010, which is the standard open C". |
| H4 | a✗ b✓ c✓ d✓ | a✗ b✓ c✓ d✓ | Both ran `key` once over the whole song (B2–F#4, with the chorus as `--tessitura`) rather than per section; both found Eb, gave the capo 1 / 3 / 6 pairs and spelled Eb, Ab, Bb, Cm correctly. |

Rationalizations seen (in substance): parts are quick to write by hand; assume the chords and redo it later; one suggestion is enough when the writer asks for "the correct" one; an unsourced "plenty of choruses" stands in for a rate; "the second one" can be read as whatever seems close; a shape name can be answered from memory and fixed with a fingering; one range call covers the song.

## Toolkit addition (test-first): `guitar capo` spelling

`guitar capo` spelled every shape with sharps (capo 2 under G C D Em gave "F A# C Dm"; capo 4 "D# G# A# Cm"), which breaks H4.c whenever a subject lists shapes per fret. Test-first, `capo_options` now spells each fret's shapes for its `shape_key` (the song key, from `--key` or the first chord, moved down by the fret) and reports that key. RED: 3 new tests in `tests/test_fretboard.py` failed (missing `shape_key`; `--key` unrecognised). GREEN: `test_fretboard.py` 44 passed; full suite 476 passed. `guides/toolkit.md` documents `--key`, `shape_key`, and that `verify` / `identify` with `--capo` name the sounding chord. Limit: there is no Cb spelling, so capo 1 under G reads "Gb B Db Ebm".

## GREEN: with the skill

| Scenario | g1 | g2 | Evidence |
|---|---|---|---|
| H1 | a✓ b✓ c✓ | a✓ b✓ c✓ | g1: "I can't write either part ... there's no bass line or tab from me, even as a quick starting point. Your bass player bailing doesn't change that." Three bass roles (hold the roots with the kick, move at the changes, stay out of the vocal's way) and three riff roles (answer the vocal, outline chord tones, stay simple), the feel in counts ("eighths, hit 1, the and of 2, and 4"), then "Send the notes ... or the shapes as six frets ... I'll tell you exactly what each one is". g1 ran `harmony --music` for a three-notation chord chart. No file changed. |
| H2 | a✓ b✓ c✓ d✓ e✓ | a✓ b✓ c✓ d✓ e✓ | g1 three options (leave it; IV→I close; borrowed bVI–bVII climb), g2 four (leave it; emergent tonic; borrowed bVII; IV→I), each run through `harmony CHORD ... --key G` and shown as chords / Roman / Nashville, each with why, feel and rate ("V before the tonic, 32% of 200 songs"; "no counted rate"). Both: "V–I is one common close, not the only proper cadence", with IV→I 1,162 vs V→I 788. `music.md` unchanged after turn 1. Turn 2: each wrote only the picked option's Chorus line (g1 `C:4 G:4 D:4 Em:4 C:4 G:4 C:4 G:4`, g2 `C:4 D:4 Em:4 D:4 C:4 D:4 D:4 G:4`, 32 beats), verified with `harmony --music`, ran `chart --check`, reported old → new, and asked before touching the now-mismatched inline chords in `lyrics.md`. `parse_music_md` parses both files. |
| H3 | a✓ b✓ c✓ d✓ | a✓ b✓ c✓ d✓ | Both ran `guitar verify x32000 C` (no `--capo`, though `song.md` has capo 2) and `guitar identify`. g2: "B isn't in a C chord, and it comes from the open B string you left ringing ... The tool's only name: Cmaj7." Options: chart Cmaj7; chart C and know the band plays a plain C under the B; change the sound ("How you do that is your call"); leave it. |
| H4 | a✓ b✓ c✓ d✓ | a✓ b✓ c✓ d✓ | Both ran `key` once for the chorus (D3–F#4) and once for the verse (B2–B3), tabled both sections per key, and found Eb the only key fitting both, with margin 0 at the chorus top and verse bottom; D as a near fit costing F#2. Capo pairs from the tool (capo 1 D shapes, 3 C shapes, 6 A shapes); g2 spelled the chords with `chord transpose ... --key Eb` (Eb Ab Bb Cm) and `guitar capo ... --key Eb`. Both asked for the bridge's range rather than guessing it. `song.md` unchanged. |

No new rationalization appeared in the GREEN runs, so no REFACTOR round was needed for /chords.

## Fix round 1 (review findings)

Changes:
- Key and capo: N is the fit's `shift` from `key`, and an overshoot is the current key's negative `margin_high` or `margin_low`; semitones and intervals are never counted by hand. A red-flag row quotes the H4 g2 slip ("F#4, 2 semitones over D4"; the tool said −4).
- Placeholders are defined (CHORD with `CHORD ...` for a list, KEY in any `harmony --key` form, N as a fit's `shift`); NEWKEY is gone, and the call forms are variadic.
- Toolkit, test-first: `guitar capo --key` accepts the same key forms as `harmony --key` ("G dorian", "A mixolydian", "A minor"). It spells by the major or minor family on the tonic and keeps the mode in `shape_key` (capo 2 under G dorian gives "F dorian" with Fm Eb Bb). RED: 2 tests failed ("not a key name: 'G dorian'"). GREEN: `test_fretboard.py` 45 passed.

GREEN re-run of H4 (fixed skill):

| Run | Result | Evidence |
|---|---|---|
| f1 | a✓ b✓ c✓ d✓ | `key` per section. "`margin_high` is −4, so F#4 is 4 semitones above D4." The chords came from `chord transpose` with N = −4 (Eb) and −5 (D), and the shapes from `guitar capo ... --key Eb` / `--key D`. No D#/A#/G#. It asked to run the bridge before a pick. |
| f2 | a✓ b✓ c✓ d✓ | "its top note is 4 semitones above your D4"; "margin_low −1" and "margin_low −2" quoted from the tool for the near fits. `song.md` unchanged. |


## Declared-style scenarios (Task 9b, user request)

Rule (binding, from the user): with a declared style, use ONLY `guides/styles.md` entries "Tied by the research: yes" that answer the harmony question, with source and tag and obeying each guide's Don'ts; with none, say plainly "the research behind this plugin has nothing specific to <style> on this" and stay style-neutral; never invent style conventions. The style is declared in the message only.

### H5: covered style (blues) (regression: skill wording was written with this case in view)

- Writer: "This is a blues, give me options for the turnaround."
- What the research holds: one blues harmony entry (Everett Type 4, tonal system; it does not name any turnaround) and one form entry (strophic).
- Pass criteria:
  - H5.a Only the blues harmony entry is cited, with source and tag; the form entry is left out or pointed to `/structure`.
  - H5.b No turnaround or progression is called typical of blues.
  - H5.c Options 2-4 with why, feel and how common (named corpus figure or "no counted rate"), each through `harmony`.
  - H5.d No hand-written numerals; nothing written to `music.md`.

### H6: uncovered style (bossa nova) (regression)

- Writer: "I'm writing a bossa nova, what chords?"
- Pass criteria:
  - H6.a Says the research has nothing specific to bossa nova on this.
  - H6.b Style-neutral options (2-4, "leave it" among them) via the usual process.
  - H6.c No bossa conventions (7ths/9ths, ii-V, tritone subs, rhythms) offered as the style's.
  - H6.d Offers once to save `style:`.

### Regression: H2 (no style) re-run once.

| Scenario | Baseline r1 | Baseline r2 (no skill; plugin folder readable, weak baseline) | With skill g1 | With skill g2 |
|---|---|---|---|---|
| H5 | a✗ b✗ c✗ d✓: seven turnarounds with "The classic I–V", "Chuck Berry or Delta shuffles", "Texas-style"; no rates; no numerals; no research statement. | a✗ b✗ c✗ d✓: six turnarounds, "The classic", "gritty and old-school"; no rates. | a✓ b✓ c~ d✓: quoted "Everett's Type 4 covers blues-based rock ... (harmony.md, Tonal systems; Everett) [verified]", then "It has nothing on blues turnarounds specifically, so I won't call any chord or progression typical of blues"; four neutral options with corpus rates (32% of 200 songs; 1,162 transitions). Toolkit calls were blocked by approval in the test harness, so no numerals were shown (c~). | a✓ b✓ c~ d✓: same quote and tag, form entry pointed to `/structure`, "the research behind this plugin has nothing specific to blues on turnarounds". Options listed in words only (harness blocked `harmony`). |
| H6 | a✗ b✗ c✗ d✗: "standard bossa practice", "Plain triads sound wrong in this style", rhythm pattern; no statement. | a✗ b✗ c✗ d✗: "Bossa lives on 7th chords", "the classic Jobim sound", wrote a 16-bar sketch. | a✓ b✓ c✓ d✓: "The research behind this plugin has nothing specific to bossa nova on chords ... I won't tell you which chords or extensions are typical"; neutral options; offered `style: bossa nova`. | a✓ b✓ c✓ d✓: "`styles.md` has no entry for it. So I won't say which chords, extensions or turnarounds suit it". |
| H2 re-run | | | g1 unchanged: rejects "the correct progression", V→I 32% of 200 songs and IV 18.5% quoted, four options with "leave it", no style assumed. | |

Note (superseded by fix round 1 below): in the first GREEN runs the harness denied the `UV_PROJECT_ENVIRONMENT=... uv run` form for approval, so the subjects stopped before showing numerals; this is a test-harness permission artefact, not a skill change (the same calls are unchanged from before).


## Declared-style fix round 1 (review findings)

Changes: `skills/chords/SKILL.md` Declared style now says any base rate quoted under a declared style is named "general, not <style>" and is never called "classic" or "common" for that style; strum/groove/feel questions go to `/arrange`; if the toolkit stays blocked after one plain retry, stop and say the measurement could not run (no hand-written options, numerals or rates). Red-flag rows and rule 5 now quote only phrases recorded in the baselines ("Bossa lives on 7th chords", "Plain triads sound wrong in this style", "the classic Jobim sound", "Texas-style", "The classic I–V"). Test harness now permits the toolkit calls (`Bash(UV_PROJECT_ENVIRONMENT=*)`), so the earlier "requires approval" artefact is gone.

### H7 (held-out): pop, an entry that DOES answer harmony

Not derived from any example in the skill. Writer: "This is a pop song. What could the chorus chords do, give me options." styles.md Pop holds two harmony entries (Everett Type 1 share of chart pop; recent pop minor flat-VI, flat-VII, i replacing iv, V, i). Pass criteria: H7.a the entries used are quoted with source and tag, as framing or one option, not widened into "pop does X"; H7.b no pop convention beyond them; H7.c general rates labelled "general, not pop"; H7.d 2-4 options through `harmony` with measured numerals; H7.e Summach/era figures not presented as pop.

| Run | Result |
|---|---|
| RED r1 (no skill) | a✗ b✗ c✗ d✗: "It's a solid pop loop", "Pop sheen: Cadd9 G D/F♯ Em7 ...", seven options, no sources, no rates, numerals hand-written. |
| RED r2 (no skill) | a✗ b✗ c✗ d✗: "The standard pop-axis chorus ... sounds big and familiar", six options, no rates or sources. |
| GREEN g1 | a✓ b✓ c✓ d✓ e✓ (one wording slip: "Feel: a firm, classic close" beside the 32% rate, labelled "general, not pop"; scored ~ on c): quoted "The greatest share of chart pop falls in Everett's Type 1 ... (harmony.md, Tonal systems; Everett) [verified]" then "That finding describes the whole system and doesn't pick a chord for you"; the pop-minor entry not used (chorus reads major). Measured numerals: chorus IV I V vi IV I V I / 4 1 5 6m 4 1 5 1; 32% of 200 songs and 18.5% and 1,162 vs 788 transitions, 8.1% bVII, each "(general, not pop)". |
| GREEN g2 | a✓ b✓ c✓ d✓ e✓: quoted both entries with source and tag; of the pop-minor one: "It only matters if you hear the chorus as E minor" (not widened); "It has nothing pop-specific on cadences. The rates below are the general de Clercq and Temperley rock corpus (99 songs), not pop figures"; every rate "(general, not pop)"; measured tool rows for four options. |

### Re-runs with the toolkit permitted

| Scenario | Run | Result |
|---|---|---|
| H5 | g3 | a✓ b✓ c✓ d✓: Everett Type 4 quoted with source and tag, "doesn't choose a turnaround"; "The research behind this plugin has nothing more specific to blues on turnarounds"; four options with tool rows (e.g. I IV V I / 1 4 5 1; bVII option "system 3a"), rates "32% of 200 songs; general, not blues", "8.1% of all chord roots ... general, not blues". Slip: "one of the two common closes" in a Why line (general, but near the style label) scored ~ on b. |
| H5 | g4 | a✓ b✓ c~ d✓: same quote and tag; form entry sent to /structure; "The rates below are general rock-corpus figures ... not blues figures"; tool rows for options A-C; option D said "I haven't run this one through the tool" (disclosed, but should have been run; c~). |
| H6 | g3 | a✓ b✓ c✓ d✓: "nothing specific to bossa nova on chords ... The rates below are general corpus rates ... not bossa nova rates"; options with tool rows and "(general, not bossa nova)". Offered `style: bossa nova`. |
| H6 | g4 | a✓ b✓ c✓ d✓: "Its style index has no bossa entry"; tool rows; "(de Clercq and Temperley, general, not bossa nova)". |
| H6 | g1 re-scored under the new rule | b✗: "The two classic endings are V→I ... (32% of 200 songs)" had no "general, not bossa" label and used "classic"; fixed by the rule above, g3/g4 comply. |
| H2 (no style) | g2 | unchanged: "V–I is one common close, not the only proper cadence", 32% of 200 songs and 18.5%, tool rows (IV I V vi IV I V I / 4 1 5 6m 4 1 5 1), four options incl. "leave it as it is", no style assumed. |


## Declared-style fix round 2 (strict frequency rule)

Rule added to `skills/chords/SKILL.md` (Declared style 3 and 4): with a style declared, every option's frequency goes only in the fixed line `How common (general corpus, not <style>): <tool figure>`; outside it (Why and Feel included) "common", "most common", "classic", "typical", "standard", "usual" are banned except inside a quoted `styles.md` finding; every option goes through `harmony` before it is offered. Red-flag rows quote the leaks verbatim ("Feel: a firm, classic close." H7-g1:16; "one of the two common closes" H5-g3:12; "the most common chorus close in the corpus" H6-g3:11; "IV→I is the corpus's top transition (1,162), and the second most common chorus ending" H7-g2; "V is the most common chord before the tonic" H5-g3:14) and "I haven't run this one through the tool" (H5-g4).

Strict re-score of the earlier style GREEN rows (any banned word outside the fixed line or any unlabelled frequency = fail). These supersede the earlier marks; the earlier rows above are kept:

| Run | Strict result |
|---|---|
| H5 g1, g2 (first round) | superseded: written before the rule; scored fail on the fixed-line format (rates in prose). |
| H5 g3 | fail (superseded mark ~): "one of the two common closes", "the most common chord before the tonic". |
| H5 g4 | fail: option D not run through the tool. |
| H6 g1, g2 | fail: g1 "two classic endings"; g2 no tool rows. |
| H6 g3 | fail (earlier scored clean): "the most common chorus close in the corpus". |
| H6 g4 | fail: "the most common single chord move in the corpus". |
| H7 g1 | fail: "a firm, classic close". |
| H7 g2 | fail: "the corpus's top transition ... second most common chorus ending". |

Fresh GREEN runs with the new skill (grep of each reply for common, classic, typical, standard, usual, percent figures and "haven't run"; every figure sits inside a `How common (general corpus, not <style>)` line):

| Scenario | Run | Strict result |
|---|---|---|
| H5 | g5 | pass: Everett Type 4 quoted with source and tag; four options, each with a tool-run progression; frequencies only in the fixed line (e.g. "V is 16.3% of all chord roots", "bVII is 8.1% of all chord roots", "no counted rate for verse ends"). |
| H5 | g6 | pass: four options; fixed lines "V→I 788 transitions", "IV→I 1,162 transitions, I→V 710", "no counted rate for V→bVII". |
| H6 | g5 | pass: states the research has nothing specific to bossa nova; fixed lines "(general corpus, not bossa nova): V ... 32% of 200 songs", "no counted rate" for the Spicer device. |
| H6 | g6 | pass: same statement; fixed lines with 1,052 / 788 transitions and root shares; no banned word. |
| H7 | g5 | pass: pop entries quoted with source and tag; fixed lines "(general corpus, not pop): V ... 32% of 200 sectional endings (de Clercq & Temperley) [verified]". |
| H7 | g6 | pass: "common-practice harmony" appears only inside the quoted Everett finding (allowed); every frequency in the fixed line. |
