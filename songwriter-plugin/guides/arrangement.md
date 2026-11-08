# Arrangement guide

Arrangement is guidance, not parts (shared rule 5). The plugin helps a songwriter decide what each section should do and who should be playing, then leaves the notes to the players. It never writes a bass line, drum pattern, tab or notation. The model is the Nashville head session, where a chart gave the framework and players built their own parts by ear. Tags show the evidence level; see sources.md.

Evidence is uneven. The layer vocabulary and energy trajectories are verified in peer-reviewed articles (Lavengood, Cobb); Owsinski's numbers and Rooksby's book were not readable. Genre-by-genre role sketches are this plugin's synthesis, because no authoritative role table exists. [design]

## Layers

- Owsinski names five arrangement elements in his Mixing Engineer's Handbook: foundation, pad, rhythm, lead and fills. Lavengood's article confirms the five names, not the book itself. [verified]
- Lavengood maps them onto Moore's four functional layers (explicit beat, functional bass, harmonic filler, melodic), where lead is the melodic layer, and adds an optional novelty layer. Moore is known through her mapping only. [as reported]
- The novelty layer carries pitch content but a non-melodic function, often as call and response, is not essential, works best sparingly in intros, outros and interludes, and has timbres that resist blending. [verified]
- Lavengood's examples include the piccolo trumpet in "Penny Lane" and the tin whistle in "My Heart Will Go On". The point is that layers describe what a part does in the texture, not its timbre. [verified]
- Working vocabulary for the plugin: beat and functional bass are the foundation; harmonic filler is a pad, or a rhythm part when it plays a counter-figure; melodic is the lead; novelty is a fill or signature line. [design]
- Default ceiling of four elements at once, with same-rhythm instruments counted as one and a fifth allowed briefly at a peak. [design]
- Owsinski's limit of usually four simultaneous elements, rarely five, with same-rhythm instruments counting as one, is known only from blog snippets, and his posts vary between four and five. [as reported]
- His "Tension and Release" section was never read, so use the general idea but do not credit him with its content. [unverified]
- "Change something every four bars" is not Owsinski's; it is a Deviant Noise rule of thumb that can over-densify a track. [as reported]
- Roles can change by section: bass can be roots in a verse and a moving line in a chorus, keys can be a pad, comping or a signature line, and a second guitar should contrast the writer's part by register, rhythm or sustain, not duplicate the strum. [design]
- Backing vocals can be a pad, a lyric harmony or call and response, staged toward the last chorus. [design]
- Solos and fills answer in the gaps of the vocal and need a defined length and an owner. [design]
- Rooksby's Arranging Songs is known only as a chapter list (guitar, then keys, bass and drums). It supports the workflow of starting from the guitar part and asking what each added player contributes, but that is a reading of a contents page. [unverified]
- Genre idiom sketches are suggestions the plugin labels as such. [design]

## Energy

- Cobb's article situates section-by-section "sonic energy" in Butler, Nobile (initiation, buildup, arrival) and Osborn (riser, drop), with energy trajectories that build momentum across a verse, prechorus, chorus rotation. [verified]
- Osborn, quoted by Cobb: Top-40 EDM songs almost never have a viable contrasting bridge, and producers must balance sonic contrast against thematic memorability; too little contrast makes a song repetitive. [verified]
- Cobb studies late "groove switches" (a dramatic change of texture for the final large section) as another source of contrast, with Billie Eilish's "bad guy" among the cases. [verified]
- So a bridge is optional: when none exists, offer a groove or texture switch. [design]
- Berklee's core arranging course frames arranging as shaping a song's emotional contour through dynamics, articulation and texture. [verified]
- Carter's "rebuild" (a breakdown at the bridge position, then layers returning toward the climax) is known only from an abstract. [unverified]
- A 1 to 5 energy scale and percentage templates are practitioner conventions without a research basis; use the scale as a conversation tool. [design]
- Energy scale used by the plugin: 1 sparse, 2 settled, 3 building, 4 full, 5 peak. [design]
- Levers for changing energy: add or remove a player, register, subdivision, drum voice, attack, vocal stack, stops and space, half-time or double-time, pad in or out, and a groove switch. [design]
- Shapes to offer: staircase, breakdown and rebuild, slow burn, flat and intimate, jam bloom, late groove switch. [design]
- One example among the shapes above, not a default for any genre: intro 2, verse 1 at 2, prechorus 3, chorus 1 at 4, verse 2 at 3, chorus 2 at 4, bridge at 2 or 5, final chorus 5, outro 2 to 3. Fit the shape to the song the writer describes. [design]
- Chorus 1 should leave headroom: if it is already the peak, ask what the last chorus can add. [design]
- The function terms initiation, buildup and arrival (Nobile) explain why a section has its energy; see structure.md for the sources. [verified]
- Contrast and ending are the plugin's own additions to that list, for sections that are neither building nor arriving. [design]

## Road map

One page, plain words, one block per section. The fields below follow the spec. The "left to the players" field is mandatory, so that no road map reads as a set of parts. [design]

```
SECTION: Verse 1   (bars or times through)
FUNCTION: initiation | buildup | arrival | contrast | ending
ENERGY: 2/5 - intimate, room to breathe
WHO'S IN (by role): foundation / pad / rhythm / lead / fill or novelty
WHO'S WAITING: the players or roles not yet in
FEEL: counts and words (see guitar.md)
HOLDS AND PUSHES: e.g. hold the last chord, push into the chorus
TRANSITION: how the next section is entered
PARTS COUNT: 2 of a default maximum of 4 (same rhythm counts as one)
LEFT TO THE PLAYERS: exact bass line, drum pattern, voicings
```

- Function: initiation, buildup and arrival come from Nobile via Cobb. [verified]
- Function, additions: contrast and ending are the plugin's own labels. [design]
- Who's in is written by role, not by written part: "bass: roots" is a role, a bass line is a part. [design]
- Parts count is checked against the default ceiling of four, with same-rhythm instruments counted as one. [design]
- Spoken cues are common usage and no standard: "kick it off from the 5", "hit the 4 on the way down" and "watch me for the 2" are the examples in Wikipedia's account of the Nashville system. [verified]
- Further cue words (drop or lay out, build, break, tag, turnaround, last time, button) are general usage, not from a single source. [unverified]
- Demo advice (leave about 20 percent for the studio, convey form, tempo, feel and core parts, resist dictating exactly what players do) comes from blog and article snippets. [as reported]
- Give players the road map early, because players learn at different speeds. [as reported]

## Number charts

- The Nashville Number System was developed by Matthews in the late 1950s for vocal parts and adapted by McCoy in the early 1960s for rhythm sections. [as reported]
- Williams is the system's historian and author of the standard book (11th edition, 2023), not its originator. [as reported]
- Chords are numbered by the root's scale degree with the tonic as 1, so a chart works in any key; minor is marked with a dash or an m. [verified]
- Charts usually run four measures to a line; several chords in one bar are grouped by underlining, a boxed bar marks a complex measure, and a diamond marks a sustained chord. [verified]
- The symbols are not standardized: individual players notate differently, and the standard book shows one song charted by seven session players to prove it. [verified]
- So any number chart the plugin offers carries a legend of the symbols it uses. [design]
- A chart may be skeletal, leaving parts and voicings to players, with staff notation added only for passages that must be played exactly. A whole song usually fits on one page. [verified]
- Head-session practice: Nashville and Southern sessions built arrangements collectively by ear from the chart's framework, so musicians could rely on their ears rather than a written arrangement. [as reported]
- The chart is optional and the road map is the main output. [design]

## Checks

Critique pass for an arrangement, run on request. Each finding follows the usual pattern: what was found, why it may matter, two to four options, the writer decides. [design]

- More than four elements in any section (more than five even at a peak). [as reported]
- The same rhythm duplicated across guitar, keys and bass. [design]
- A register clash with the vocal, or a crowded low end. [design]
- A first chorus that is already at peak, leaving nowhere to go. [design]
- Missing contrast: does each section change at least one lever? With no bridge, is there a groove or texture switch? Cobb's groove-switch cases are the basis; the lever test is the plugin's. [design]
- Fills or novelty lines outside the gaps in the vocal. [design]
- Unmarked transitions between sections. [design]
- Open-ended solos: give each a length, an owner, an exit cue and a landing. [design]
- An undecided ending. [design]
- The full band starting at bar one, or the band copying the writer's full strum. [design]
- Forcing a bridge when a texture switch would do; Osborn's no-bridge finding and Cobb's groove switches show a bridge is optional. [design]
- Room for the players: roles and feel specified, parts left open. A road map that has no "left to the players" content has started to dictate parts. [design]
- Masking examples (a lead fill under every vocal phrase, a piano in the voice's range) and the mute test come from blog sources of uncertain attribution. [as reported]
