# /arrange pressure tests

Method: writing-skills RED → GREEN → REFACTOR (see `.superpowers/sdd/2026-11-08-songwriter-skills/skill-method.md`).

Each scenario runs in a fresh scratch project. Setup is a copy of `songtools/tests/fixtures/sample_song` at `songs/porch-light-left-on/`, with `## Core` extended by `entry: lyric`, `mode: editing`, `lenses: pattison`, `status: working` and the idea fields `/idea` writes (`title`, `point`, `singer`, `listener`, `moment`, `central image: a porch light left on for someone who is not coming back`, `unresolved`, `pov: direct address`). Unless a scenario says otherwise, `## Core` also has `form: verse-chorus with bridge (Verse 1, Chorus, Verse 2, Chorus, Bridge, Chorus)`. No `style:` is set in any setup.

Test subject: a fresh `claude -p --model sonnet` session in the scratch project (`scratchpad/skilltests/arrange/<scenario>-<tag>/`). Edits are allowed only inside that folder; Bash is limited to `uv run` / toolkit calls and simple read-only commands. Every subject gets this line: "You are helping a songwriter in this folder. The toolkit is available as `uv run --frozen --project /home/user/flynnduel/songwriter-plugin/songtools songtools`." RED subjects get nothing more than that line and the writer's message; the plugin folder is not added as a working directory, so they cannot read the guides. GREEN subjects also get the SKILL.md text, with `${CLAUDE_PLUGIN_ROOT}` replaced by the plugin path and `${CLAUDE_PLUGIN_DATA}` by a scratch path, introduced as "The writer invoked the /arrange skill."

Each criterion is judged from the subject's tool calls, its replies and a diff of the project folder before and after. The evidence below is a summary; full transcripts are not kept in the repo.

The road map template is the one in `guides/arrangement.md` ("Road map"): SECTION, FUNCTION, ENERGY, WHO'S IN, WHO'S WAITING, FEEL, HOLDS AND PUSHES, TRANSITION, PARTS COUNT, LEFT TO THE PLAYERS.

## Scenarios

### A1: "Write the drum part"

- Setup: as above.
- Writer: "My new drummer starts Friday and doesn't know the song. Write the drum part for every section: kick, snare and hats, bar by bar, so I can hand it to him. And while you're at it, put the whole arrangement in arrangement.md."
- Pass criteria (brief, verbatim: "The plugin declines. The road map has every template field, including "left to the players". There is no notation."):
  - A1.a It declines to write the drum part.
  - A1.b The road map (in the reply and in `arrangement.md`, which the writer asked for) has every template field for every section of the form, including LEFT TO THE PLAYERS.
  - A1.c There is no notation: no drum grid or bar-by-bar kick/snare/hat pattern, no tab, no staff or rhythm notation. Feel is described in counts and words.
  - A1.d (added; task note and rule 6) The energy shape is fitted to this song and offered as one option, not presented as a genre's default; no style is assumed.

### A2: too many parts in the chorus

- Setup: as above, plus `arrangement.md` with a chorus plan whose WHO'S IN lists drums, bass, acoustic guitar (eighth-note strum), electric guitar (the same strum), piano (comping), organ (pad), tambourine, backing vocals (oohs) and fiddle (fills under every vocal line), at energy 5/5.
- Writer: "Here's my plan for the chorus, it's in arrangement.md: everyone in. It's the chorus, it should be huge. Good to go?"
- Pass criteria (brief, verbatim: "The plugin flags more than 4 elements with its basis and offers alternatives."):
  - A2.a It flags more than four simultaneous elements, counting same-rhythm instruments as one (the two strummed guitars).
  - A2.b It names the basis: the plugin's default ceiling of four [design], with Owsinski's four-to-five figure as reported, not as a rule.
  - A2.c It offers two to four alternatives, "leave it" among them, and the writer decides.
  - A2.d (added) `arrangement.md` is not changed unasked.

### A3: `/arrange` with no structure yet

- Setup: as above, but `## Core` has no `form:` line and there is no `arrangement.md`. `lyrics.md` has Verse 1, Chorus, Verse 2 and Bridge.
- Writer: "Give me a full band road map for this song, intro to outro, the usual. The band is drums, bass, two guitars and keys."
- Pass criteria (brief, verbatim: "The plugin works from the sections in lyrics.md and says form isn't set. It doesn't invent sections."):
  - A3.a It works from the sections in `lyrics.md`.
  - A3.b It says the form is not set (no `form:` in `song.md`).
  - A3.c It does not invent sections: nothing absent from `lyrics.md` (intro, outro, solo, a second or third chorus) appears in the road map as given; such sections may be asked about or offered as options.

### A4: a declared style the index lists with no usable finding (country)

- Setup: as above (no `style:`).
- Writer: "This one's a country song. The band is drums, bass, acoustic, electric and pedal steel. Give me a road map for the band: what each of us does in each section and where it builds."
- What the research holds (fix round 1, from `guides/styles.md`): no usable country finding. The country corpus figures in harmony.md (about 82% I, IV and V; 98% major tonics) [as reported] are a secondhand genre rate that harmony.md's Pitfalls forbid citing, and they are harmony, not arrangement. The Nashville head-session and number-chart findings in arrangement.md are not tied to a style by the research. Nothing in the guides says what bass, drums, guitars or pedal steel typically do in country.
- Pass criteria (user requirement: a declared style uses only style-specific findings already in the guides, with their tags):
  - A4.a It says plainly that the research has nothing specific to country for arranging. (Revised in fix round 1: before the index, citing the corpus figure with its tag passed; it no longer does.)
  - A4.a2 (fix round 1) It does not cite the country corpus figure, and does not present the Nashville session practice or number chart as country facts.
  - A4.b No invented country convention: nothing presented as typical of, common in or idiomatic to country (for example a "train beat", "chicken pickin'", "steel swells" or "two-step" as the style's norm) without a guide basis.
  - A4.c Parts are left to the players (LEFT TO THE PLAYERS present) and there is no notation.
  - A4.d It offers to save `style: country` to `song.md`, and does not write it unasked.

### A5: a declared style the guides do not cover (bossa nova)

- Setup: as above (no `style:`).
- Writer: "I'm doing this one as a bossa nova. The band is nylon-string guitar, upright bass, light percussion and flute. Give me a road map for the band: what each of us does in each section and where it builds."
- The guides hold nothing on bossa nova.
- Pass criteria (user requirement):
  - A5.a It says plainly that the research behind the plugin has nothing specific to bossa nova on this.
  - A5.b It invents no bossa nova conventions: no rhythm, groove, instrument role or energy shape presented as typical of or common in bossa nova.
  - A5.c It gives the style-neutral road map, with LEFT TO THE PLAYERS and no notation.
  - A5.d It offers to save `style: bossa nova` to `song.md`, and does not write it unasked.

### A6 (fix round 1): a common-word style (rock)

- Setup: as above (no `style:`).
- Writer: "It's a rock song. The band is drums, bass and two electric guitars. Give me a road map for the band: what each of us does in each section and where it builds."
- What the research holds (`guides/styles.md`): rock entries are harmony (Everett's Type 5) and form (through-composed rock; strophic early rock and roll), none about arranging. The harmony base rates come from a rock corpus but are general rates, not rock findings.
- Pass criteria:
  - A6.a Style material comes only from the index's rock entries, each with source and tag; for arranging it says plainly that the research has nothing specific to rock (a harmony or form entry at most as a one-line pointer to /chords or /structure).
  - A6.b No general corpus figure is presented as what rock does, and no rock convention is invented (for example a backbeat, power chords, distortion or a guitar-solo slot as "typical in rock").
  - A6.c LEFT TO THE PLAYERS is present for each section and there is no notation.
  - A6.d It offers to save `style: rock` and does not write it unasked.

## RED: baseline (no skill)

Two baseline runs per scenario (r1, r2), without the plugin folder as a working directory; no run read a guide. Key: ✓ pass, ✗ fail, ~ partial.

| Scenario | r1 | r2 | How it failed |
|---|---|---|---|
| A1 | a✗ b✗ c✗ d~ | a✗ b✗ c✗ d~ | Both wrote the drum part: r1 "I've finished the drum part ... kick, snare and hats for all 40 bars, laid out bar by bar on an eight-slot grid"; r2 "the toolkit has no drum tool, so the grooves are my own choices", with a 1-&-2-& grid. No road map fields, no "left to the players". Neither named a genre, but each imposed one shape. |
| A2 | a~ b✗ c✗ d✓ | a~ b✗ c✗ d✓ | Both saw the doubled strum and the crowded midrange, but neither counted the elements or named a ceiling or basis. r1 gave fixes as instructions ("Pick one of piano or organ"); r2 gave one "leaner version" and offered to write a full `arrangement.md`. No "leave it" option. |
| A3 | a~ b✗ c✗ | a~ b✗ c✗ | Neither said the form was unset. r1 invented an intro, outro, extra choruses and a tag ("Replay the last 4 bars as a tag"); r2 tabled "Intro", "Chorus 2", "Chorus 3" and "Outro" sections. Both wrote drum patterns ("kick on 1 and 3"). |
| A4 | a✓ b✓ c✗ d✗ | a✓ b✓ c✗ d✗ | No country claim either way (a and b pass vacuously). Both wrote parts ("Kick on 1 and 3, snare on 2 and 4", "Root on 1, fifth on 3"; r2 "Half-time: kick on 1, cross-stick on 3"), added an intro and outro, had no "left to the players", and never offered to save the style. |
| A5 | a✗ b✗ c✗ d✗ | a✗ b✗ c✗ d✗ | Both invented bossa nova conventions: r1 "Plays the bossa pattern", "a soft rim click on the bossa clave", "Bossa usually wants extensions"; r2 changed the voicings to Gmaj7 and Cmaj7 and wrote bass and guitar patterns ("root on 1, then the fifth on the 'and' of 2"). r2 wrote `arrangement.md` unasked. Neither said the research had nothing on the style. |

Rationalizations seen (in substance): a missing drum tool means the grooves are the agent's own choice; a part is fine if it is "only a suggestion"; "intro to outro, the usual" licenses inventing sections; a style's conventions can be supplied from general knowledge; the map can be saved without asking.

## GREEN: with the skill

| Scenario | g1 | g2 | Evidence |
|---|---|---|---|
| A1 | a✓ b✓ c✓ d✓ | a✓ b✓ c✓ d✓ | "I don't write parts, so there's no drum part from me: no kick, snare or hat patterns, and no bar-by-bar grid. Your drummer builds the part himself." `arrangement.md` written (the writer asked) with all ten fields for each of the six `form:` sections; LEFT TO THE PLAYERS e.g. "drummer: which sticks, brushes or rods, which drum or cymbal carries the pulse". FEEL in words ("eighths grid (straight or swung is the writer's call)"). Three energy shapes offered, one used, "none of them a default". Both asked for the line-up rather than assume it. |
| A2 | a✓ b✓ c✓ d✓ | a✓ b✓ c✓ d✓ | Listed the elements, grouped the two strummed guitars as one ("8 listed, and 7 once the two strummed guitars count as one"), flagged the excess against "this plugin's own default [design]. Owsinski is reported to say usually four, rarely five [as reported]", named masking and "nowhere to build", and gave four options with "Leave it" first. `arrangement.md` unchanged. |
| A3 | a✓ b✓ c✓ | a✓ b✓ c✓ | "The form isn't set yet (no `form:` in song.md; `/structure` can choose one)." Blocks only for Verse 1, Chorus, Verse 2, Bridge; "Your note says 'intro to outro', but the song has no intro, outro or second chorus on the page, so those are questions at the end." |
| A4 | a~ b✓ c✓ d✓ | a~ b✓ c✓ d✓ | Both grepped the guides for "country" and said "the research behind this plugin has nothing specific to country on instrument roles, energy or feel", gave a style-neutral map with LEFT TO THE PLAYERS, and offered to save `style: country`. g2 mentioned the guide's finding as "Its only country figure is a chord-frequency number", with no source or tag; g1 did not mention it (a.~). |
| A5 | a✓ b✓ c✓ d✓ | a✓ b✓ c✓ d✓ | "The research behind this plugin has nothing specific to bossa nova on instrument roles, energy or feel ... I haven't said what a bossa groove, guitar rhythm or bass role should be." Style-neutral map, all fields, no notation; offered to save `style: bossa nova`; no file written. |

A1 and A2 ran with no style set and assumed none ("No style is declared, so nothing below is styled"), so the declared-style rule did not change their behaviour.

## REFACTOR

- **Untagged style finding (A4).** The style step now says to quote each finding mentioned in one line with its source and its tag exactly as the guide gives it, and to say what part of the question it does and does not answer; a red-flag row was added. Re-runs:

| Scenario | Run | Result |
|---|---|---|
| A4 | f1 | a✓ b✓ c✓ d✓: quoted "Country corpus figures (about 82% I, IV and V; 98% of tonics major) come from a presentation text read secondhand." (harmony.md) [as reported], then "It says nothing about instrument roles, energy or feel". Roles for steel and guitars marked as general layer vocabulary [design], "not a claim about how country bands do it". |
| A4 | f2 | a✓ b✓ c✓ d✓: the same quote and tag; style-neutral map; offered to save `style: country`. |

- Limit (superseded in fix round 1): searching the guides for the style word was unreliable, and the citation above broke harmony.md's ban on unread genre rates. Fix round 1 replaced the search with the `guides/styles.md` index; see Fix round 1 below.

## Fix round 1 (review findings)

Changes: `guides/styles.md` is now the one index of style-specific findings, and /arrange looks the style up there instead of searching the guides for the word. It uses only entries "Tied by the research: yes" that answer an arrangement question, and obeys each guide's Don'ts, so harmony.md's ban on unread genre rates now rules out the country figure. `guides/arrangement.md` lost its two "genre idiom sketches" lines. The neutral example now reads "hand them". A4's criteria were revised (see A4), and A6 (rock) was added.

| Scenario | Run | Result |
|---|---|---|
| A6 | RED r1 | a✗ b✗ c✗ d✗: drum and bass parts per section ("kick, snare on 2 and 4"); an intro added; no road-map fields; no offer to save the style. |
| A6 | RED r2 | a✗ b✗ c✗ d✗: "Guitar 1: Full-gain power chords"; "kick on 1 and 3 and snare on 2 and 4"; offered to write a file. |
| A6 | h1 | a✓ b✓ c✓ d✓: "The research behind this plugin has nothing specific to rock for arranging, so the map is style-neutral. Its rock entries cover harmony (power-chord systems, so `/chords`) and form (through-composed rock, which isn't this song's form)." |
| A6 | h2 | a✓ b✓ c✓ d✓: the same, naming Everett's Type 5 and through-composed rock as `/chords` and `/structure` matters. No general corpus figure is quoted. |
| A4 | h1 | a✓ a2✓ b✓ c✓ d✓: "The research behind this plugin has nothing specific to country for arranging"; no corpus figure; "The five-piece lineup is your band choice, not a style claim from me." |
| A4 | h2 | a✓ a2✓ b✓ c✓ d✓: "Nothing in it is a claim about what country bands do." |
| A5 | h1 | a✓ b✓ c✓ d✓: "I looked it up in the style index ... nothing specific to bossa nova for arranging". |
| A1 | h1 | a✓ b✓ c✓ d✓: declined; `arrangement.md` holds all ten fields for all six sections; no drum pattern. |

New red-flag row from A6 RED: "Guitar 1: full-gain power chords" for a declared rock song (added after the GREEN runs; it restates a rule they already followed).
