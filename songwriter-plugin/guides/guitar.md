# Guitar guide

Guitar is the writer's main instrument, so the plugin's role here is to read, verify and describe what the writer plays. It never writes a part, a tab or a fingering for them (shared rule 5). It takes a shape such as `x32010`, works out the sounding pitches from tuning and capo, checks them against the chord name and reports every valid name, because some shapes have two (Am7 and C6 share notes). Shapes are facts about notes, not playing instructions. [design]

Evidence is uneven. The V-System is verified from Hober's reconstruction of Greene's methods; tuning and capo mechanics come from Wikipedia and a Berklee page; Rooksby's guitar advice was never read. Tags show the evidence level; see sources.md.

## Role

- Read: parse the shape, ChordPro `{define}` or chords-db style data the writer supplies, and compute the sounding pitches per string from tuning plus capo. [design]
- Verify: check the pitches against the chord name; report missing and extra notes and every valid name instead of picking one silently. [design]
- Describe: say what the voicing is (spacing group, open strings, bass note) and what it sounds like, in plain words. [design]
- Never write parts: do not compose a pattern, voicing or fingering for the writer. "Same chord, new colour" moves are offered as a menu grounded in the chord they already play. [design]
- A "second guitar" suggestion is a register or rhythm contrast to the writer's part, described in words, never written out. [design]
- Rooksby's guitar advice is entirely unverified, and only the contents of his Chord Master are confirmed, including a 37-entry chord matrix that is useful as a parser-coverage checklist. [as reported]

## Voicings

The V-System (Greene, as reconstructed by Hober) sorts four-note chords into 14 groups by spacing, not by string set. It is a tool for band-context upper-string voicings, not six-string open strums. [verified]

- Scope: four-note chords with four distinct pitches (no unison or octave doublings), standard tuning, normal technique; no alternate tunings. The chord may be rootless, altered or stretched. [verified]
- A chord is classified by its spacing, not by the strings it is played on; each group tends to sit on certain string sets (V-4 on strings 5-3-2-1 and 6-4-3-2, for example). [verified]
- Method 1, the one Greene thought most important: label the voices bass, tenor, alto, soprano from low to high, walk the chord tones in ascending chromatic order, write which voice holds each, and look the formula up in the master table. [verified]
- Worked example from the source: first-inversion Emaj7 on strings 4-3-2-1 gives the formula ABST, which is V-2. [verified]
- Groups in brief (Hober's descriptions): V-1 is close position and always spans less than an octave; V-2 and V-4 hold most stock jazz chords; V-3 bunches the lower notes under an isolated soprano and can sound muddy low on the neck; V-5 to V-14 grow in stretch, with V-11 to V-14 fairly obscure. [verified]
- Conversions that stay inside the system: dropping the alto an octave takes V-1 to V-2 (Greene preferred "drop alto" to "drop 2"), and dropping the soprano two octaves takes any V-2 to V-4. [verified]
- String transfer (moving a chord to the middle or lower string set), transposition, systematic inversion and spacing-preserving quality changes all keep a chord in its group. [verified]
- Greene counted 43 four-note qualities, treated pairs such as m7 and 6 as homonyms, and wrote add9 as "/9". [verified]
- Greene mostly used fretted notes; when he used an open string it was most often an E or A bass, and the system handles open strings only with care. [verified]
- Mapping of the common jazz drop names onto groups (drop-2 to V-2, drop-3 to V-4, drop-2-and-4 to V-5, starting from close position) is the research team's own derivation. [design]
- The toolkit's `guitar vsystem` returns a group of `null` when a voicing is not a four-note V-System voicing; say so and describe it by pitch set and bass note instead. [design]
- Hober reconstructed Methods 1 and 3 from Greene's notes because Greene never published them; cite as "Greene via Hober". [verified]
- For strummed open chords use pitch-set and bass analysis, not V-groups. [design]
- The chords-db dataset (MIT licence; 828 chords and 3,283 positions) is safe to bundle. [verified]
- The GuitarSet repository shows no licence, so any claim that it is MIT is unconfirmed. [unverified]

## Tunings

- Wikipedia lists the seed tunings low to high: Drop D (D A D G B E), DADGAD (D A D G A D), Open G (D G D G B D), Open D (D A D F# A D), Open E (E B E G# B E) and Open C (C G C G C E). [verified]
- DADGAD's open strings form an open D suspended-fourth chord, neither major nor minor; Davey Graham popularised it. [verified]
- Open E needs light strings because three strings are raised; a variant (E G# B E B E) avoids raising any. [verified]
- Joni Mitchell notation: a letter for the open lowest string, then the fret offsets between each pair of adjacent strings. Standard tuning is E55545. [verified]
- Tunings with the same code are transpositions of each other, so a shape maps one-to-one between them, possibly through a capo. [design]
- Codes the toolkit computes: Drop D is D75545, DADGAD is D75525, Open G is D57543, Open D is D75435, Open E is E75435 (the same family as Open D) and Open C is C75754. [design]
- Berklee describes retuning to an open tuning by fret-matching strings, and the "fret two strings, let the rest drone" approach to shapes in open tunings. [verified]
- Nick Drake used alternate tunings to make cluster chords that are hard in standard tuning; this is verified, but his song-by-song tunings are contested (for "Pink Moon", sources give CGCFCE with a capo at 2, DADGDF#, and Berklee's open D), so never state one as fact. [verified]
- Mitchell's total tuning count is given as "over 50" and "about 60" by different sources. [as reported]

## Capo

- A capo works like retuning every string up by the same amount, but only open notes change; the seventh fret of the low E string still plays B. [verified]
- It shortens the scale length, which changes timbre and is often used for brightness. [verified]
- Partial capos clamp a subset of strings; some products can clamp any of 63 string combinations. A five-string capo at fret 2 leaving the low string open works like drop D raised a tone. [verified]
- Partial capo convention in the toolkit: strings under the clamp count frets from the capo, and free strings count from the nut. If a shape was typed in the other convention it will read wrong, so confirm which one the writer means. [design]
- ChordPro keeps the `{key}` directive as the shape key under `{capo}`, and a concert-pitch version transposes the chords instead. [verified]
- Capo search ranks capo positions and shape keys by how many chords become open shapes, and also offers a concert-pitch chart for the band. [design]
- The fret-7 rule: the toolkit adds a note from fret 7 upward that the tone thins high on the neck. No source supports a fret-7 ceiling and no pedagogy ties a fret to a timbre change; treat it as a soft heuristic and say it has no source. [unverified]
- Real high-capo issues reported on forums and retailer pages are intonation and strings pulling sharp, so retune after clamping and place the capo just behind the fret. [as reported]
- Open strings ring "jangly" under a capo (search snippet only). [as reported]
- A capo can only raise pitch, so lowering the key for a singer means a different shape key, not a capo. [as reported]

## Feel

Describe feel in counts and words, offered as options, never as instructions. [design]

- Count sixteenths as 1-e-and-a, 2-e-and-a: numbers for quarters, the word "and" for eighths, and "e" and "a" for the other sixteenths; triplets count as 1-tri-ple. Other counting systems exist. [verified]
- Strum patterns are often made by subtracting strokes from a straight-eighth base; in funk the strumming hand keeps a steady sixteenth motion while the fretting hand damps strokes. [verified]
- Swing is labelled soft (between 1:1 and 2:1), triplet (2:1), hard (between 2:1 and 3:1) or dotted (3:1); real ratios are subtler than the label, and funk often swings sixteenths. [verified]
- Travis picking combines alternating bass fingerpicking with a syncopated melody, usually on steel-string acoustic. [verified]
- Pendulum strumming keeps the hand moving down and up and takes its rhythm from which passes touch the strings. [as reported]
- A shuffle delays the "ands" while the beats stay put. [as reported]
- Berklee's touch vocabulary: control a strum through touch, tone, dynamics and register; playing over the fingerboard (sul tasto) sounds sweeter and rounder, near the bridge brighter. [verified]
- Half-time feel moves the backbeat to beat three; applying it to guitar is an inference. [unverified]
- Template for a feel line: the grid (eighths or sixteenths, straight or swung), which slots sound, where the accents lean, hand position and touch, and bass motion. Example wording: "sixteenths, hand always moving; hit 1, the and of 2, and 4." [design]
