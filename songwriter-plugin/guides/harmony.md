# Harmony guide

This guide holds what the plugin knows about chords: how to name a section's tonal system, which corpus base rates may rank an option, how to present choices, and what to avoid. The sources are peer-reviewed rock and pop theory (Everett, Temperley, de Clercq, Doll, Spicer, Richards, Nobile) plus Open Music Theory; the textbook and songwriting-manual authors (Kostka and Payne, Rooksby) were read only as tables of contents. The plugin coaches harmony with menus and never writes the writer's parts. Tags show the evidence level; see sources.md.

Corpus figures describe what songs do, not what they must do (shared rule 6). Quote them as frequencies, name the corpus, and let the writer choose. [design]

## Tonal systems

Classify each section on its own before labelling chords. The labels below simplify Everett's Table 1, which has six numbered systems with nine sub-types, ordered by how far each departs from common-practice harmony and voice leading. The toolkit's `harmony` command reports a system with a confidence, and its reading is a simplified second opinion. [design]

- 1a: major-mode systems with common-practice harmony and voice leading, possibly inflected by minor-mode or chromatic mixture. The greatest share of chart pop falls in Type 1. [verified]
- 1b: the same in minor, possibly inflected by major-mode or chromatic mixture; pure-minor examples are rarer. [verified]
- 2: diatonic modal systems, with common-practice voice leading but harmonic behaviour that sometimes departs from it. [verified]
- 3a: major (or modal) systems with mixture from modal scale degrees, such as borrowed flat-six and flat-seven. [verified]
- 3b: major-mode systems with progressive structures, including modulation and the truck-driver's lift of successive half or whole steps. [verified]
- 4: blues-based rock, minor-pentatonic-inflected major-mode systems. Everett locates structural harmony in the backing, not the vocal blue notes. [verified]
- 5: triad-doubled or power-chord minor-pentatonic systems unique to rock (I, flat-III, IV, V, flat-VII), where common practice is often irrelevant at the surface. [verified]
- 6a and 6b: chromatically inflected systems of early metal (6a) and chromatically related scale degrees with little pentatonic basis (6b). [verified]
- The double-plagal cadence (flat-VII, IV, I) is, for Everett, a chromatic descending-fourths function. It is often wrongly given a modal basis, and long fourth chains such as the one in "Hey Joe" imply no mode. [verified]
- Everett's footnote dates the term "double-plagal" to a 2000 book, not 2008. [verified]
- Everett warns that a truck-driver's modulation can be an arranger salvaging a weak idea. [verified]
- So ask what a lift is for. [design]
- Open Music Theory reports that in recent pop minor, flat-VI, flat-VII, i has largely replaced iv, V, i, and that pop chords are almost always in root position. [verified]
- Open Music Theory's bass-to-chord chart: most of the time the scale degree of the bass is enough to name the chord. [verified]
- Doll: function follows scale-degree content. A chord with degree 6 moves away from home, and chords with degree 7 or 2 pull home. [as reported]
- Doll's rogue dominant is a dominant with a lowered seventh degree (flat-VII, v), not IV; a lead dominant has the major-scale seventh. [as reported]
- Spicer, fragile tonic: the tonic is present but weakened by inversion or mid-phrase placement. [verified]
- Spicer, emergent tonic: the tonic is withheld for a triumphant arrival, usually at the chorus. [verified]
- Spicer, absent tonic: the promised tonic never arrives, as in "Jane Says" and "I'll Be Around"; "Last Friday Night" is not among his examples. [verified]
- Spicer, soul dominant: IV over the fifth degree in the bass, blending subdominant and dominant, especially common in 1970s soul. [verified]
- Spicer adopts Tagg's terms: a shuttle is two chords, a loop is three or more. [verified]
- Spicer on two-chord vamps: the same pair a whole step apart can be I-ii or flat-VII-i, depending on accent, pedal, melody and which chord comes first. [verified]
- Richards, Axis loops: the four rotations of vi, IV, I, V do not suit fixed Roman numerals; Richards labels them with letters. Tonality rests mainly on which tonic-triad notes the melody emphasises, and listeners carry a major-mode bias. [verified]
- Richards, corpus: the G-rotation appears in only 10 of 2,715 Billboard year-end songs (1990 to 2016). [verified]
- Nobile keeps tonic, predominant, dominant, tonic as a section-level functional circuit; initiating verses do not close it and must lead to a chorus. [verified]
- Toolkit ruling: when a section fits plain major or minor and also a mode with the same notes, prefer the plain reading unless the mode clearly outscores it, and show the mode as the dual reading. [design]
- Toolkit ruling: ambiguity is reported, not hidden. A dual reading means the key is a judgment, so say so and suggest settling it by where the melody rests. [design]

## Base rates

Two base rates matter, at different levels. At loop level IV to I is the default motion. At the end of a chorus V to I still wins. Present both as classic. [design]

- The de Clercq and Temperley corpus has 99 songs, not 100: the top 20 per decade from the 1950s to the 1990s of Rolling Stone's 2004 list. [verified]
- Root shares of all chords: I 32.8%, IV 22.6%, V 16.3%, flat-VII 8.1%, VI 7.2%, flat-VI 4.0%. Major and minor are merged. [verified]
- Most common transitions: IV to I (1,162), I to IV (1,052), V to I (788), I to V (710), IV to V (514), I to flat-VII (470), V to IV (392), flat-VII to I (386). [verified]
- The pre-tonic chord, excluding the tonic, is IV about 40% of the time and V about 27%. [verified]
- Chorus-end correction: at sectional cadences in the 200-song set, V is still the most common pre-tonic chord (32% of 200 songs) and IV is second (18.5%). [verified]
- So do not over-promote plagal endings. [design]
- Flat-VII (3.5%), II (3%) and flat-VI (1%) are the next endings; 118 of the 200 songs (59%) have a sectional cadence at all. [verified]
- Only 2 of 37 plagal cadences use minor iv; even in minor-key songs the cadential IV is usually major. [verified]
- Temperley notes the V count is flattered by songs that are rock only by a very broad definition; in his view IV is understated. [verified]
- Temperley's named devices: the plagal stop cadence (instruments stop before I, as in "Barracuda"), the grand plagal near a song's end, the deceptive IV, and the tonicized IV (flat-VII to IV heard as IV to I of IV). [verified]
- Rare roots, for honesty about adventurous moves: flat-II 0.5%, VII 0.4%, sharp-IV or flat-V 0.3%. [verified]
- Country corpus figures (about 82% I, IV and V; 98% of tonics major) come from a presentation text read secondhand. [as reported]
- Doll's frequency claims are intuition, not corpus counts. [as reported]
- Jam-band harmony has no source at all. [unverified]
- Kostka and Payne, Tonal Harmony: no text was read. Keep the function vocabulary, cadence names, secondary dominants and mode mixture; drop as rules "V must go to I", SATB voice-leading bans, "melody notes must fit the chord" and harmonic minor as the default. This keep-and-drop list rests on the rock evidence above, not on the book. [unverified]
- Rooksby's Songwriting Sourcebook contents work as a coaching ladder (three-chord songs, four, five and six chords, flat-degree chords, reverse polarity, majors and minors, minor keys, chord types, key changes), but no advice from it was read and nothing may be quoted. [as reported]
- Rooksby's definition of reverse polarity (swapping a chord's major or minor quality) is secondhand. [as reported]

## Option menu

Coach with menus. Every option says why it works, how it feels and how common it is, and the writer plays and chooses. Never offer a single answer. The feel descriptions are this plugin's wording; frequencies are the corpus figures above. [design]

- Change the chorus's first chord, or its harmonic rhythm, so the chorus differs from the verse at once. Why: contrast must land at the section's first phrase. Feel: a lift or a shift of weight. Common: the corpus gives no rate for this, so say "common practice, not a counted one". [design]
- Withhold the home chord until the chorus (an emergent tonic). Why: the arrival becomes the event. Feel: held breath, then relief. Common: a named device in Spicer, with "She's Gone" and "Little Red Corvette" as his examples. [design]
- End the chorus on V to I. Why: the most common pre-tonic at chorus ends. Feel: a firm, classic close. Common: 32% of 200 songs. [design]
- End the chorus on IV to I. Why: IV to I is the corpus's top transition and the second chorus ending. Feel: softer, "amen" close. Common: 18.5% of 200 songs. [design]
- Plagal stop: IV to I with the instruments dropping out before I. Why: the stop spotlights the return. Feel: a held beat, then a landing. Common: a named device with "Barracuda" as the model. [design]
- Save a deceptive IV for the last chorus. Why: it plays against the expected I once the ear is set. Feel: a late surprise that still sounds natural. Common: Temperley names it but gives no rate. [design]
- Borrowed flat-VI and flat-VII into the tonic (an Aeolian climb). Why: borrowed flat chords give a big arrival. Feel: broad, anthemic. Common: flat-VII 8.1% and flat-VI 4.0% of roots. [design]
- Use a key lift sparingly. Why: it raises energy without new material. Feel: effortful if the song has not earned it. Common: Everett's warning applies, so ask what the lift is for. [design]
- Soul dominant (IV over the fifth in the bass) into the chorus. Why: it blends subdominant and dominant. Feel: pulling home softly. Common: a 1970s soul staple per Spicer. [design]
- Pedal: hold a dominant or tonic bass under changing chords before the chorus. Why: tension without new chord motion. Feel: coiled. Common: no corpus rate; offer it as a texture idea. [design]
- Loop choices: where a loop is the song's engine, offer a rotation of the same four chords to start on a different one. Why: the starting chord sets the key feel. Feel: major, minor or unsettled. Common: Richards counts show the rotations differ widely in use. [design]
- Always include "leave it as it is" as an option. [design]

## Notation

Show each progression in three notations at once: a Roman numeral with case for quality, a Nashville number, and the chord symbol. Store a quality-free root layer internally for matching, so that I, vi, IV, V and I, VI, IV, V find the same schema. [design]

```
Key of G     chords:    G    C    G    D
             Roman:     I    IV   I    V
             Nashville: 1    4    1    5

Key of G     chords:    G    F    C    G      Em
             Roman:     I    bVII IV   I      vi
             Nashville: 1    b7   4    1      6m
```

- Roman numerals follow the bass, with flat signs for chromatic roots (flat-VII, flat-VI, flat-III); minor-key songs are labelled from the minor tonic. [verified]
- Open Music Theory writes roots in uppercase regardless of quality in its older edition, which is verified. [verified]
- Its newer edition reportedly uses lowercase for minor, but that page could not be read, so no single convention is established for pop; say which one is in use. [as reported]
- Nashville numbers count the root's scale degree with the tonic as 1, which lets a chart work in any key; minor is marked with a dash or an m, and "1/5" means the 1 chord over a 5 bass note. [verified]
- Plain-English glosses help: flat-VII is the chord a whole step below home; a double plagal steps home in two fourths; plagal is the "amen" move; the Aeolian cadence is the minor-key climb home. [design]
- Richards's cues for an ambiguous loop: melodic emphasis on tonic-triad notes, the first-chord rule, and a major-mode bias among listeners. [verified]
- For an ambiguous loop show both readings with a confidence, using those cues in order: melodic emphasis, first and last chord, phrase-final notes, then the major-mode bias as tiebreaker. [design]

## Pitfalls

- Do not force common-practice rules onto Types 4 to 6, and do not apply SATB voice-leading rules to pop. [design]
- Everett: the double plagal is a chromatic function, not a modal one. [verified]
- Do not over-claim a mode from a flat-VII. [design]
- Recent pop minor is Aeolian-based, per Open Music Theory. [verified]
- Do not make harmonic minor the default for minor songs. [design]
- An Axis loop's tonality depends on the melody (Richards). [verified]
- Do not state an Axis loop's key with certainty. [design]
- Do not flag a melody that disagrees with the chord as an error. Melodic and harmonic divorce is idiomatic in rock. [design]
- Do not ignore sections and the bass; classify per section and read the bass line. [design]
- Do not give single-answer prescriptions; offer a menu. [design]
- V is still the most common pre-tonic chord at chorus cadences in the corpus. [verified]
- Do not over-promote plagal endings. [design]
- Do not present secondhand examples as fact; label any example the research did not verify. [design]
- Do not name a corpus rate as a rule, and do not cite a genre rate (country, jam) that was not read. [design]
- Name the limit when it matters: some note sets have two valid chord names, and a section's key can be a judgment. [design]
