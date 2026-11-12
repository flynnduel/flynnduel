# Songwriter

A songwriting partner for Claude Code. It co-writes and critiques lyrics, coaches the music, gives arrangement guidance, and measures what can be measured (rhyme, stress, stability, point of view, chords, key) with `songtools`, an offline toolkit that ships with the plugin.

## What it does and doesn't do

It does:

- start a song from wherever you are (a riff, a lyric, a title, a progression, a brief, a banked idea, a co-write) and pick it up again later from the files;
- draft lyric lines from your own material, and check its drafts for stock language before you see them;
- measure instead of guessing: syllables, stresses, rhyme types, section shape, chord names and key fit all come from the toolkit;
- give every note with its basis ("Pattison:", "corpus:", "Davis (as reported):") and two to four options, one of them "leave it";
- make a chord chart (ChordPro and PDF), a concert-pitch copy for a capo song, and a block-chord MIDI guide track.

It doesn't:

- write melodies, bass lines, drum parts, riffs, tab or notation. Music is coached; arrangement is guidance; the playing is yours;
- assume a genre. A style changes the examples only when you declare one, and only with findings the research holds for that style (`guides/styles.md`). Where the research has nothing, it says so;
- apply commercial rules (title timing, title in the chorus) unless you turn the `commercial` lens on;
- say a line "sounds like AI", or guess how a line was written. Stock language is treated as a craft issue;
- decide a song is finished. Only you set the status;
- generate audio, or listen to it.

## Installing

You need [Claude Code](https://claude.com/claude-code) and [`uv`](https://docs.astral.sh/uv/), which runs the toolkit:

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

In Claude Code, add this repository's marketplace and install the plugin, named `songwriter`:

```
/plugin marketplace add flynnduel/flynnduel
/plugin install songwriter@flynnduel
```

The first toolkit call installs the toolkit's pinned Python packages once (this needs the network); after that everything runs offline. Python 3.11 or newer is fetched by `uv` if you don't have it.

## Try it on your own song

Until the plugin is merged, install it from its branch, `claude/dazzling-feynman-furauz` of `flynnduel/flynnduel`:

1. Install `uv` (above) and check that `uv --version` prints a version.
2. Open Claude Code in the folder where you keep your songs, or an empty one. The plugin writes only inside `songs/` there.
3. Run these two commands in Claude Code, then restart it or run `/reload-plugins`:

   ```
   /plugin marketplace add flynnduel/flynnduel#claude/dazzling-feynman-furauz
   /plugin install songwriter@flynnduel
   ```

4. Type `/songwriter:` to see the eleven commands. Plugin commands carry the plugin's name, so `/newsong` below is typed `/songwriter:newsong` (typing `/newsong` finds it).

**From a phone (Claude Code cloud session):** `/plugin` is not available there, so the repo carries copies of the skills in `.claude/skills/`, which cloud sessions load. Start a session on `flynnduel/flynnduel`, branch `claude/dazzling-feynman-furauz`, and type `/newsong` (no `songwriter:` prefix). A cloud session's files are lost when it ends: ask Claude to commit and push your `songs/` folder before you finish. After editing a skill in `skills/`, run `scripts/sync-project-skills` to refresh the copies (a test fails until you do).

Commands to try first, on a song or a draft of your own:

1. `/newsong` followed by what you have: "I've got a verse and a chorus, no music yet", and paste them. It creates `songs/<title>/` and names the next step. (Or skip the folder: paste lyrics after `/lyrics` or `/critique` and it will work on them directly and offer the folder.)
2. `/lyrics` with a question about particular lines: "does line 3 of the chorus scan?", "is this rhyme a cliche?", "draft two options for the second verse's last line".
3. `/critique` with what you want to know: "what's weak in verse 2?". It changes nothing.
4. `/chords` with a progression or a shape: "the chorus is G, D, Em, C, four beats each; what else could the last bar do?", or "what is x32033 called?".

Judge each reply as you would a co-writer's: would you take that note? Anything generic, wrong or unhelpful is worth reporting back word for word.

## The commands

| Command | What it is for | Example |
|---|---|---|
| `/newsong` | Start a song from what you have, or resume one | `/newsong I've got a riff in DADGAD, about 110 bpm, no words` |
| `/idea` | What the song is about: point, singer, listener, moment, central image, what stays unresolved, point of view, title | `/idea I know it's about my dad's workshop but not what it's saying` |
| `/structure` | Form options, where the title sits, contrast between sections, whether an odd section is a fault | `/structure the chorus doesn't lift, why?` |
| `/lyrics` | Object writing, drafting, and line checks (rhyme, stress, stock language, point of view) | `/lyrics check the rhymes in verse 2` |
| `/melody` | Coaching on a tune you sing: stresses, phrase placement, contour, leaps, breath, range | `/melody the chorus tune feels flat, what can I try?` |
| `/chords` | Progression options in three notations, shape checks, key and capo for your voice | `/chords is x32013 really a C7?` |
| `/arrange` | A road map for the band: each section's job, energy, who plays, what is left to the players | `/arrange road map for a four-piece, drummer joins Friday` |
| `/chart` | ChordPro and PDF charts, a concert-pitch copy, a MIDI guide track | `/chart make the charts for rehearsal` |
| `/critique` | Feedback in a fixed order: strengths, your questions, neutral questions, at most three ranked notes | `/critique be honest about the bridge` |
| `/finalcheck` | The ten-step final review; you choose the status | `/finalcheck I think this one is finished` |
| `/bank` | Save an idea in one line for later, or look through the bank | `/bank title: "Salt in the Coffee"` |

Any stage can be reached at any time; `/newsong` suggests an order but nothing enforces it.

## The song folder

Songs live in your project, never inside the plugin. Everything is plain text you can read and edit.

```
songs/
├── _bank/ideas.md        dated, tagged ideas from /bank
├── pronunciations.txt    your own pronunciations for words the dictionary lacks
└── <title>/
    ├── song.md           the song record: ## Core, ## Kept lines, ## Split sheet
    ├── lyrics.md         "## Verse 1" headings; chords inline as [G]word
    ├── melody.md         where each syllable of a checked line falls on the beat
    ├── music.md          each section's progression, as chord:beats
    ├── arrangement.md    the band road map
    ├── object-writing/   raw sense writing
    ├── cuts/             cut lines and verses; nothing is deleted
    ├── drafts/           a snapshot before every lyrics change
    └── out/              chart.cho, chart.pdf, chart-concert.cho, chart-concert.pdf,
                          guide.mid, guide-concert.mid
```

`song.md` holds the song's facts under `## Core` (`key`, `capo`, `tempo`, `time`, `voice low`, `voice high`, the idea fields, `form`, `entry`, `mode`, `lenses`, `status`, and `style` if you declare one), the lines you chose to keep under `## Kept lines`, and the writers' shares under `## Split sheet` (`- Name | roles | percent`).

With a capo, `key` is the key of the shapes you play. `chart.*` shows those shapes; `chart-concert.*` and `guide-concert.mid` are at sounding pitch for the band.

## Modes and lenses

- **Mode** (`mode` in `song.md`): `drafting` or `editing`. In drafting mode the critic is silent: no flags and no unasked opinions. Say "let's edit" to switch, or ask a direct question at any time.
- **Lenses** (`lenses`): `pattison` is on by default (rhyme types, stability, prosody). `webb` adds the strict-rhyme reading. `commercial` adds title timing and title-in-the-chorus checks. The last two are off until you turn them on.
- **Kept lines**: when you keep a line the plugin flagged, it records the line, the flag, your reason and the date. It does not raise that issue again during the session, raises a new issue on the line like any other, and brings each kept line back once at `/critique` and `/finalcheck`.
- **Status** (`status`): `working`, `done for now` or `done`. You set it; the plugin never declares a song finished.

## Sources and their tags

The guides in `guides/` condense the research behind the plugin. Every rule, check and prompt in them ends with a tag:

| Tag | Meaning |
|---|---|
| `[verified]` | the source itself was read |
| `[as reported]` | known only secondhand; always cited as "(as reported)" |
| `[unverified]` | no usable source; offered as a labelled heuristic or left out |
| `[design]` | this plugin's own choice, not a claim about songwriting |

[`guides/sources.md`](guides/sources.md) lists, author by author, what was read and what the plugin may therefore say in that author's name. The main ones are Pattison (lyric craft, the default lens), Webb (strict rhyme), Perricone (melody checks), Lerman (the critique order), Dodson and Stolpe (rewrite checks), Hayes (the prosody model), Everett, de Clercq and Temperley (harmony), Summach, Nobile and Osborn (form), and Zollo's interviews (process).

Limits the plugin states when they matter: the prosody scoring is a simplified version of Hayes (2005), whose model matched listeners' preferred settings about 70% of the time on folk-song data; some chord shapes have two valid names; a word outside the pronouncing dictionary is estimated until you add it to `songs/pronunciations.txt`.

## Open items

Not yet verified by hand, because the books could not be read online. Until they are, these are cited by title or "as reported", and their checklists are not run as rules:

- Davis's checklists;
- Webb's *Tunesmith* (rhyming dictionaries, rewriting);
- Perricone's *Great Songwriting Techniques* and his range figure;
- Rooksby on capo, tunings and arranging;
- Owsinski's element ceiling and his tension-and-release section;
- Pattison's own definitions of additive, subtractive and partial rhyme.

Also unverified: the GuitarSet data licence (testing use only once confirmed). NSAI's criteria and Blume's checklists are left out of the final check for the same reason.

## The toolkit

`songtools/` is a Python command-line toolkit (run through `uv` with a committed lockfile; no network at run time). The skills call it for you; [`songtools/README.md`](songtools/README.md) and [`guides/toolkit.md`](guides/toolkit.md) document every command if you want to run it yourself. Data attributions are in [`data/ATTRIBUTION.md`](data/ATTRIBUTION.md).

To run the tests:

```
cd songtools && uv run --frozen pytest -q
```
