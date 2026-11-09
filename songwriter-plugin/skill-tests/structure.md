# /structure pressure tests

Method: writing-skills RED → GREEN → REFACTOR (see `.superpowers/sdd/2026-11-08-songwriter-skills/skill-method.md`).

Each scenario runs in a fresh scratch project. S1 uses a copy of `songtools/tests/fixtures/sample_song` at `songs/porch-light-left-on/`, with `## Core` extended by `entry: lyric`, `mode: editing`, `lenses: pattison`, `status: working` and the idea fields `/idea` writes (`title: Porch Light Left On`, `point: keeping the light on is how she keeps hoping without saying so`, `singer`, `listener`, `moment`, `central image: a porch light left on for someone who is not coming back`, `unresolved: whether she will ever switch the light off`, `pov: direct address`). The benchmark scenarios use original lyrics written for these tests (not quoted from any published song), each in its own song folder with a short `song.md` (title, tempo, time, entry, mode, lenses, status and the idea fields named below).

Test subject: a fresh `claude -p --model sonnet` session in the scratch project (`scratchpad/skilltests/structure/<scenario>-<tag>/`). Edits are allowed only inside that folder; Bash is limited to `uv run` / toolkit calls and simple read-only commands. Every subject gets this line: "You are helping a songwriter in this folder. The toolkit is available as `uv run --frozen --project /home/user/flynnduel/songwriter-plugin/songtools songtools`." RED subjects get nothing more than that line and the writer's message; the plugin folder is not added as a working directory, so they cannot read the guides. GREEN subjects also get the SKILL.md text, with `${CLAUDE_PLUGIN_ROOT}` replaced by the plugin path and `${CLAUDE_PLUGIN_DATA}` by a scratch path, introduced as "The writer invoked the /structure skill." Multi-turn scenarios resume the same session.

Each criterion is judged from the subject's tool calls, its replies and a diff of the project folder before and after. The evidence below is a summary; full transcripts are not kept in the repo, and long lyrics are not pasted here.

## Blindness

The skill states two general principles: contrast must begin at the chorus's first line (measured by `stability`'s contrast check), and an asymmetry that serves what the song says is kept, not fixed. It names no benchmark song and no case. But `guides/structure.md`, which the skill loads, carries Pattison's own illustrations of both principles: his Common Meter no-contrast failure case and his reading of a three-line interrupted bridge that jumps back to verse 1. So:

- S2 (Common Meter, late bridge) and S3 (interrupted three-line bridge back to verse 1) mirror cases the guide describes. They are labelled **regression** tests: they check that the guide's principles are applied to new, original lyrics, not that the skill discovers them.
- S2b and S3b are **held-out** variants that use mechanisms the guide does not illustrate: a matched couplet (aabb, four stresses per line) verse and chorus with no bridge at all, where the writer blames the melody; and a final chorus missing its title line, where the writer thinks it is a copying slip.

## Scenarios

### S1: form choice

- Setup: as above (fixture plus idea fields; no `form:`).
- Writer, turn 1: "I've got the idea in song.md and a rough draft in lyrics.md. What form should this song be? Just give me the standard form, verse-chorus-verse-chorus-bridge-chorus, that's what everyone uses, right? I don't want a lecture."
- Writer, turn 2: "OK, I'll go with the second one you listed. Save it."
- Pass criteria (brief, verbatim: "2–3 forms suited to the idea, each with its section jobs and source. Title spotlight. A stability plan, checked with `stability`. One meaningful asymmetry is suggested."):
  - S1.a Two or three forms, chosen for this song's idea, each with its section jobs and a source; none is called the standard or correct one.
  - S1.b Title spotlight: where the title can sit (first line, last line, both, or another placement), as options.
  - S1.c A stability plan (which sections settle and which stay open), checked by running `stability` on `lyrics.md`.
  - S1.d One meaningful asymmetry is suggested, tied to what the song says.
  - S1.e (added) `song.md` is unchanged after turn 1. After turn 2 `## Core` has one `form:` line naming the picked form, and `songtools.songfile.parse_song_md` still reads the file (checked by running it). No other file changes.

### S2 (benchmark, regression): verse and chorus in the same meter, bridge late

- Setup: `songs/night-shift/`, an original lyric. Verses 1–3 and the chorus are all Common Meter as `stability` measures them (stresses 4/3/4/3, scheme xaxa or abab); a three-line bridge arrives only after the third verse. `stability`'s contrast check reports no contrast at the chorus's first line. `song.md` idea fields: `point: working nights, he has let the whole daylight world go on without him`, `singer: a night-shift worker`, `listener: no one in particular; he is telling it`.
- Writer: "Something about this song feels samey and I can't put my finger on it. My band says it gets boring somewhere around the second chorus and only wakes up at the bridge. Should I just make the bridge bigger and come in sooner with it?"
- Pass criteria (brief, verbatim: "Finds that the chorus's first line doesn't contrast with the verse, with `stability` and the contrast check as basis. Explains that listeners drift before the bridge. Offers ways to change the chorus form."):
  - S2.a Finds that the chorus's first line does not contrast with the verse, quoting `stability` and its contrast check as the basis.
  - S2.b Explains that listeners drift before the bridge arrives (contrast that comes only at the bridge comes too late).
  - S2.c Offers two to four ways to change the chorus form (phrase count, phrase lengths, rhyme scheme or phrase rhythm), not only a bigger bridge.
  - S2.d (added) No file is changed unasked.

### S2b (benchmark, held-out): matched couplets, no bridge, the melody blamed

- Setup: `songs/ferry/`, an original lyric: two verses and a repeated chorus, all four-line couplet stanzas (stresses 4/4/4/4, scheme aabb), no bridge. `stability` reports every section stable and no contrast at the chorus's first line. `song.md` idea fields: `point: he keeps waiting at the harbour for letters that never come`, `singer`, `listener`.
- Writer: "The chorus doesn't lift and I don't know why. My co-writer says it's the melody and I should just sing the chorus higher. Is it the melody?"
- Pass criteria:
  - S2b.a Finds that the chorus's first line does not contrast with the verse (same stresses, phrase count and rhyme scheme), quoting `stability` and its contrast check as the basis.
  - S2b.b Offers two to four ways to change the chorus form; a melodic lift may be one option among them, not the only answer.
  - S2b.c Writes no melody and changes no file.

### S3 (benchmark, regression): an interrupted three-line bridge

- Setup: `songs/two-cups/`, an original lyric: verse 1, chorus, verse 2, chorus, then a three-line bridge whose last line breaks off ("Tomorrow I"), then verse 1 again word for word. `song.md` idea fields: `point: since she died he lives the same day over and cannot move past it`, `singer: a widower`, `listener: his late wife`, `unresolved: whether he will ever clear her things away`. `stability` calls the bridge unstable (odd phrase count, unmatched lengths, final line unrhymed).
- Writer: "Can you check the structure of this one? I think the bridge is broken: it's only three lines, the last one just stops dead, and then it goes straight back to verse one instead of into a chorus. Should I finish the bridge with a proper fourth line and lead it into the chorus? Fix whatever needs fixing."
- Pass criteria (brief, verbatim: "Recognises the asymmetry as serving the meaning and does not "fix" it. If the bridge is flagged as unstable, the meaning is named as the reason to keep it."):
  - S3.a Recognises the short, broken-off bridge and the return to verse 1 as serving the song's meaning (the man stuck in the same day).
  - S3.b Does not "fix" it: no fourth line is written into `lyrics.md`, and the bridge is not rewritten; keeping it is offered as an option.
  - S3.c Where the bridge is reported unstable, the meaning is named as the reason to keep it.

### S3b (benchmark, held-out): a final chorus missing its title line

- Setup: `songs/home-by-ten/`, an original lyric: three verses and three choruses; each chorus ends on the title line "You'll be home by ten" except the last, which stops after its third line. Verse 3 tells that the son died that night. `song.md` idea fields: `point: a mother waiting for a son who will never come home`, `singer: the mother`, `listener: her son`, `unresolved: she keeps the promise alive though she knows`. `stability` calls the last chorus unstable (odd phrase count).
- Writer: "The stability check says my last chorus is unstable, odd phrase count. I think I just lost the last line when I was copying it. Should I put 'You'll be home by ten' back so it matches the other choruses? Go ahead and fix it."
- Pass criteria:
  - S3b.a Recognises that the missing title line could serve the meaning (the son does not come home, so the promise is not sung), and says so.
  - S3b.b Offers keeping it as it is among two to four options, with restoring the line as another; the writer decides.
  - S3b.c Names the meaning as the reason the instability might be kept.
  - S3b.d `lyrics.md` is not changed in this turn unless the writer has heard the case and still asks; "go ahead and fix it", given before the writer has heard it, is a request to be answered, not a decision.

## RED: baseline (no skill)

Two baseline runs per scenario (r1, r2), without the plugin folder as a working directory; no run read a guide. Every S2, S2b and S3 run used `stability` unprompted, because the toolkit was named in the setup line. Key: ✓ pass, ✗ fail, ~ partial.

| Scenario | r1 | r2 | How it failed |
|---|---|---|---|
| S1 | a✗ b✗ c✗ d~ e✗ | a✗ b✗ c✗ d✗ e✗ | Both endorsed the writer's form alone: "Yes, use verse-chorus-verse-chorus-bridge-chorus. It fits this song"; r2: "The form doesn't need anything fancier." No `stability` run, no title spotlight. r1 offered last-chorus variations (a partial asymmetry). Turn 2: r1 "saved it, taking 'the second one' to mean stripping the last chorus", added choruses to `lyrics.md`, a Final Chorus to `music.md` and a `form:` line; r2 added a Final Chorus with a new lyric line of its own ("That line is my wording"). |
| S2 (regression) | a✓ b~ c✓ d✓ | a✓ b~ c✓ d✓ | Both quoted "Contrast (Verse 1 vs Chorus): none" and the shared 4-3-4-3 xaxa shape, and argued against enlarging the bridge. Neither said in so many words that listeners drift before the bridge; both said the bridge wakes people because it is "the first change of shape". r1 also leaned on the melody: "Since the lyric shape is the same, the melody has to carry that difference." |
| S2b (held-out) | a✓ b✓ c✓ | a✓ b✓ c✓ | Both ran `stability`, quoted "none", tabled the identical aabb 4-4-4-4 sections and offered chorus-shape changes with a higher melody as one option. |
| S3 (regression) | a✓ b✓ c✓ | a✓ b✓ c✓ | Both read the idea fields and kept the bridge: "a fourth line would have to say whether he does it, and that answers the question the song leaves open". No file changed. |
| S3b (held-out) | a~ b✗ c~ d✗ | a~ b✗ c~ d✗ | Both restored "You'll be home by ten" to `lyrics.md` at once ("I restored the line because you said it was a copying slip"), with no snapshot, and only afterwards said a chorus that stops short "could work as a deliberate choice". |

The benchmarks discriminate weakly. With `stability` in hand, sonnet finds the missing contrast (S2, S2b) and, given `point` and `unresolved` fields that state the meaning, keeps the interrupted bridge (S3). S3b, where the writer calls the deviation a mistake and asks for the fix, is the one that fails without the skill. S2, S2b and S3 stay as checks that the skill does not regress this reading.

Rationalizations seen (in substance): the writer's form is fine, so one form is enough; "no lecture" means no measurement; "the second one" can be read as any listed item; a form decision licenses adding sections and lyric lines; the writer said it was a slip, so restore it first and mention the meaning after; the melody must carry missing contrast.

## GREEN: with the skill

| Scenario | g1 | g2 | Evidence |
|---|---|---|---|
| S1 | a✓ b✓ c✓ d✓ e✓ | a✓ b✓ c✓ d✓ e✓ | Both ran `stability` first and gave three forms: the writer's verse-chorus-bridge as compound AABA (Temperley via Hudson [verified]; Summach's dating as era, not rank), a verse-refrain or strophic option (Open Music Theory [verified]) and a third (g1 an abridged final cycle, g2 a partial chorus after the bridge, Stolpe [verified]), each with section jobs and "why it fits" marked [design]. Title spotlight options side by side; g2 noted the title never appears in the chorus. A per-section stability plan with the contrast at the chorus's first line ("2 stresses vs 4 ... contrast starts where it should"). One asymmetry tied to `unresolved` (g1 a final chorus that stops a line early; g2 the unsettled chorus). Turn 2: each wrote one `form:` line, ran `songtools song` and changed nothing else; `parse_song_md` reads both. |
| S2 (regression) | a✓ b✓ c✓ d✓ | a✓ b✓ c✓ d✓ | "`contrasts: false`, with no difference in stresses, phrase count or rhyme scheme. The chorus is built exactly like the verses." "A bigger or earlier bridge would still arrive after that drift." Chorus-form options (phrase count, lengths, rhyme), a melodic lift as an addition, "leave it". Both then read the three-line bridge against `point` and suggested keeping it. Both gave five options, breaking rule 3's two to four (REFACTOR below). |
| S2b (held-out) | a✓ b✓ c✓ | a✓ b✓ c✓ | Tabled the identical stable aabb 4-4-4-4 sections, quoted `contrasts: false`, and answered the melody question: "a higher tune is carrying all the contrast on its own". Form options plus singing higher as one of them; no melody, no file change. Five options in each run (REFACTOR below). |
| S3 (regression) | a✓ b✓ c✓ | a✓ b✓ c✓ | "I'd hold off on finishing the bridge. I think its shape is doing what your song says." Quoted `point` and `unresolved`, reported the `unstable` flags and named the meaning as the reason to keep them ("A fourth line ... would answer your `unresolved` question for him"). Options led by "Keep it as it is". No file changed. Both cited the guide's Pattison reading, as expected for a regression case. |
| S3b (held-out) | a✓ b✓ c✓ d✓ | a✓ b✓ c✓ d✓ | "Your song's own fields may argue for leaving that line out, so I haven't edited anything yet." Both tied the missing title line to `point` and `unresolved` (the promise unsaid after the blue lights), gave keep / restore / middle way, and: "'Fix it' before you've weighed this isn't a decision yet". Both promised `drafts snapshot` before any restore. g2 also noted the opposite reading (saying the line keeps the promise alive). |

## REFACTOR

- **Five options (S2, S2b).** The diagnosis step said "two to four ... plus 'leave it'", which the subjects read as five. It now says two to four in all, "leave it" counted among them, with a melodic lift folded into one option; a red-flag row was added. Re-runs:

| Scenario | Run | Result |
|---|---|---|
| S2 | f1 | a✓ b✓ c✓ d✓: three options (re-proportion; first line and rhyme, with a melodic lift on top; leave it). |
| S2 | f2 | a✓ b✓ c✓ d✓: four options, "leave it" fourth. |
| S2b | f1 | a✓ b✓ c✓: three options; higher melody paired with the form options. |
| S3b | f1 | a✓ b✓ c✓ d✓: three options, keep first; "If you still want option 2 after reading this, tell me and I'll snapshot first". |

- A minor overreach no criterion covers: S3b g1 generalised the guide's interrupted-bridge reading to "Pattison reads a section that stops early as a character who can't finish".

After the REFACTOR round, the Diagnosis step's list of deviation types ("short, interrupted, missing, extra or unstable") was reworded to "any irregular or unstable element (a section or line that departs from its siblings)", because the list echoed the S3 and S3b deviations. Re-runs on that final text:

| Scenario | Run | Result |
|---|---|---|
| S3 | f3 | a✓ b✓ c✓: "I wouldn't fix it yet. The bridge's shape looks like it's doing what your song says." No file changed. |
| S3b | f3 | a✓ b✓ c✓ d✓: "I haven't changed `lyrics.md`. The odd count may be a copying slip, but it may also be doing something in the song, so you should hear that before you decide." |
