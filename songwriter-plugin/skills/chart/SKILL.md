---
name: chart
description: Use when a songwriter wants a chord chart, lead sheet, ChordPro file, printable PDF or MIDI guide track of their song, a chart for the band or a concert-pitch copy for a capo song, or asks whether the chart still matches the lyrics. Not when the writer wants a road map of what each player does (arrange) or chords chosen or changed (chords).
---

# Chart

Charts are made by `songtools` from the writer's own files, never by hand. The plugin runs the toolkit, reports what it wrote, explains the capo copies, and relays any error exactly as printed.

Read `${CLAUDE_PLUGIN_ROOT}/guides/rulebook.md` first. Then read the `chart` and `midi` entries and "Behaviours to explain" in `${CLAUDE_PLUGIN_ROOT}/guides/toolkit.md`.

**Violating the letter of these rules is violating the spirit.** "Rehearsal in an hour", "just a quick one" or "the toolkit is being difficult" does not change them: a chart typed by hand is a chart the files do not back.

## Toolkit calls

Run from the writer's project. `<song>` is the song folder, e.g. `songs/porch-light-left-on`. Run each call in the form written, one per command: no `cd`, `&&`, loops or shell variables. If a call is refused or blocked, run it again in that plain form; never guess its result.

```
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools chart <song> --check
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools chart <song> --concert --pdf
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools midi <song>
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools midi <song> --concert
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools midi <song> --tempo BPM
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools midi <song> --concert --tempo BPM
UV_PROJECT_ENVIRONMENT="${CLAUDE_PLUGIN_DATA}/venv" uv run --frozen --project "${CLAUDE_PLUGIN_ROOT}/songtools" songtools drafts snapshot <song>
```

BPM is a placeholder: use `--tempo` only when `song.md` has no `tempo` and the writer gives one, and then on both the shape and the `--concert` call.

## Making the chart

Copy this checklist:

```
Chart:
- [ ] song.md read: key, capo, tempo; lyrics.md has inline chords; music.md present or not
- [ ] chart --check run (when music.md exists); mismatches put to the writer
- [ ] chart --concert --pdf run; every path in "written" reported, or the error relayed
- [ ] midi run (and midi --concert with a capo); paths reported, or "no guide track" when it reports chords: 0
- [ ] capo convention stated
```

1. **Read the song.** `song.md` (`key`, `capo`, `tempo`) and `lyrics.md`. The chart is built from `lyrics.md`'s inline chords; the guide track from `music.md`. With no inline chords the chart is lyrics only: say so, and point to `/chords`. With no `music.md`, skip `--check` and `midi` and say why. **No song folder yet** (nothing in `songs/` for this song): say so in one line and start with `/newsong` (invoke the `newsong` skill, or ask the writer to run it); it creates the folder, records what the writer brought and routes back here. Create no song file from this skill.
2. **Accidentals.** The toolkit writes `♯` and `♭` as `#` and `b` in every chart file. If the song files use `♯` or `♭`, say so in one line ("your B♭ prints as Bb"). Nothing to respell; change no file.
3. **Check.** Run `chart <song> --check`. `"matches": true` goes in the report in one line. For each section with `"matches": false`, name it with its `only_lyrics` and `only_music` chords and ask which file is right. A mismatch does not block the chart: make it, and put the question first in the reply.
4. **Chart.** Run `chart <song> --concert --pdf`. On exit 0 list every path in `written`. On exit 2 see Toolkit errors.
5. **Guide track.** Run `midi <song>`. With a `capo`, also run `midi <song> --concert`. Report each `path`, its `key` and `tempo`. Say what the track is: the writer's chords from `music.md` as block chords, each section once in file order (repeats are not expanded), nothing added. If `midi` reports `"chords": 0`, `music.md` has no `progression:` lines and the file it wrote is silent: say there is no guide track yet and why, do not list that file as one, skip `midi --concert`, and point to `/chords` for the progressions.
6. **Reply** with the paths, the capo convention, the check result and any question. No chart, chord list or song form typed out in the reply: the files are the chart.

## The capo convention

When `song.md` has a `capo`, say this every time, with the values from the files:

- `out/chart.cho` and `out/chart.pdf`: the shape chords, as the guitarist plays them with capo CAPO (`key` in `song.md` is the shape key).
- `out/chart-concert.cho` and `out/chart-concert.pdf`: the same chart in sounding pitch, for the band (bass, keys, horns, anyone not using the capo). Name its key: read the `{key: ...}` line of `out/chart-concert.cho` once it is written and give the value ("concert key: X"). Before the chart exists, say the key will be read from that file.
- `out/guide.mid` plays the shape chords, so it sounds CAPO semitones lower than the band; `out/guide-concert.mid` sounds with the band. Each track's key is the `key` in its `midi` output.

Never transpose a chord or a key yourself, even one: every concert chord or key you name is read from the toolkit's files or output. With no capo, say the two charts are the same and either can go to the band.

## Toolkit errors

An error prints `{"error": "..."}` and exits 2.

1. Quote the message exactly as printed, in a code span. Do not paraphrase it.
2. Say in one sentence what it points at (file, line, chord).
3. Offer the fix as a question with two to four options taken from the files ("music.md has Em there: use Em? Or tell me the chord you meant."). Never edit `lyrics.md` or `music.md` unasked. On a yes, run `drafts snapshot` before any edit to a chord symbol (a fix or a respelling, in either file), change only what the writer agreed, then re-run the failed call.
4. Never produce the chart another way: no `.cho` or PDF written by hand, no chart in the reply, no partial chart by dropping `--concert` or `--pdf` to get around the error. Say what was not written. A `midi` run that does not depend on the failing file may still run; say which files exist.

## Red flags: stop

Each of these was said or done by an agent without this skill, unless marked:

| Thought | Reality |
|---|---|
| Ran `chart --pdf` only; "If you play with a capo, I can add a version" (capo 2 in song.md) | Read `song.md`. Always `--concert --pdf`, and state the capo convention. |
| "The B♭ in the bridge ... sounds as C in A" | Never transpose by hand. Concert chords come from `chart-concert.cho`. |
| "Its pitches match chart-concert.pdf (A), not the capo'd shapes" (guide.mid) | `guide.mid` plays the shapes. Report each track's `key` from the `midi` output; run `midi --concert` for the band. |
| B♭ in the files, charts handed out with no word about how it prints | The toolkit writes it as `Bb` in the charts. Say so in one line. |
| `--concert` failed, so `chart --pdf` alone was run and handed out | No workaround around an error. Relay it, ask, re-run once fixed. |
| "The toolkit failed on Hm7" | Quote the error message exactly as printed. |
| The whole song form and chord list typed into the reply | The files are the chart. Report the paths. |
| "Its key is on the `{key: ...}` line of `chart-concert.cho`" (said with this skill, value never given) | Read that line and give the key itself. |
| A silent `guide.mid` (`"chords": 0`) reported as the guide track | No `progression:` lines, no guide track. Say so; `/chords` writes them. |
