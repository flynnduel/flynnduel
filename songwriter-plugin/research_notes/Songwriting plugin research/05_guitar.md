# The Guitar as a Songwriting Tool: Voicings, Capo, Open Strings, Alternate Tunings, Rhythm Feel

Scope note (researcher, re-verification pass, 7 Nov 2026): This version replaces the earlier pass. Newly readable this time, so these are now **verified from primary text**: tedgreene.com V-System PDFs (Introduction, Method 1 – How to Recognize, Conversion), Wikipedia (List of guitar tunings, Guitar tunings, DADGAD, Capo (musical device), Partial capo, Fingerstyle guitar/Travis picking, Nick Drake, Strum, Counting (music), Swing), Berklee Online's acoustic-techniques excerpt, archive.org catalogue metadata for Rooksby's books, and mirdata's GuitarSet loader (GitHub raw). **Still unreachable**: soundonsound.com and www.soundonsound.com (DNS-refused despite being listed), jonimitchell.com, zenodo.org, the archive.org book servers (ia*.us.archive.org, so no page text or search-inside for the lending copies of Rooksby or Greene). The only archive.org copy of *Chord Chemistry* is an apparent unauthorized "kupdf" upload, which I did not use. Tags used here: "(via search snippet)" means only a search-engine summary was seen; "[unverified]" means general knowledge with no source checked; "[researcher derivation]" means my own arithmetic or logic from cited definitions.

## 1. Ted Greene's V-System: the 14 groups, string transfer, naming conventions

### Takeaway
The V-System classifies **four-note chords with four distinct pitches** by **spacing**, not by string set. It has 14 voicing groups. Six of them (V-1, 2, 3, 4, 5, 8) are defined by a "Chronological Voice Formula" table. The other eight are those six with one voice displaced by an extra octave. String transfer, transposition, systematic inversion and quality changes all leave a chord's group unchanged. "Drop" operations, which Greene called "drop alto" and the like rather than "drop 2", move a chord to another group.

### Cited Findings
- **Scope restrictions**: the system covers only four-note chords with no unison or octave doublings. The chord may be rootless, altered or stretched. It assumes normal technique and **standard tuning**, possibly pitched down a half or whole step: no special tunings, no right-hand tapping, no thumb-over chords. Greene called it his "pet system" — [James Hober, "The V-System Introduction," tedgreene.com](https://tedgreene.com/images/lessons/v_system/02_V-System_Introduction.pdf)
- **Spacing, not string set**: "V" stands for voicing or voicing group, and "voicing and spacing are essentially the same thing". A chord is classified "by its spacing, not by what strings it is played on." Each group does tend to fall on certain string sets; for example, V-4 sits comfortably on 5-3-2-1 and 6-4-3-2 — [V-System Introduction](https://tedgreene.com/images/lessons/v_system/02_V-System_Introduction.pdf)
- **String transfer**: in *Chord Chemistry* and *Modern Chord Progressions* Greene described "string transfer" (also "string transference"): moving a chord from the top four strings to the middle four or bottom four, or transferring only one note. The notes don't change, though the tone may — [V-System Introduction](https://tedgreene.com/images/lessons/v_system/02_V-System_Introduction.pdf)
- **String naming by sound**: Greene, like most guitarists, named strings by pitch, so "top four strings" means the thin strings, i.e. the "4-3-2-1 string set" — [V-System Introduction](https://tedgreene.com/images/lessons/v_system/02_V-System_Introduction.pdf)
- **Group character, per Hober**:
  - V-1 is close position, with no chord tone able to fit between voices, and always spans less than an octave. These are "piano chords" that need stretches on guitar.
  - V-6 is V-1 with the bass down an octave.
  - V-2 and V-4 hold most "stock" jazz chords. V-2s are "Wes chords" and good for comping on the top-four and middle-four sets. V-4s include "Freddie Green" big-band rhythm chords.
  - V-3 bunches the bottom three notes with the soprano isolated, which can sound muddy and is best used higher up the neck.
  - From V-5 to V-14 the trend is toward bigger stretches. V-11 to V-14 are "fairly obscure", included for completeness.
  — [V-System Introduction](https://tedgreene.com/images/lessons/v_system/02_V-System_Introduction.pdf)
- **Method 1** (Greene, 1970s; the one he considered most important): label the voices B, T, A, S (bass, tenor, alto, soprano, low to high). Walk the "Chord Tone Path" in ascending chromatic order of chord tones (1 b2 2 b3 3 4 b5 5 #5 6 b7 7). Treat 9 as 2, 11 as 4 and 13 as 6, and write down which voice holds each tone; the result is the Chronological Voice Formula. Look that formula up in the Master Formula Table. The path is circular, so you may start on any chord tone — [Hober, "Method 1 – How to Recognize," tedgreene.com](https://tedgreene.com/images/lessons/v_system/03_Method1_HowToRecognize.pdf)
- **Master Formula Table**, exact entries from the source:
  - V-1 = BTAS, SBTA, ASBT, TASB
  - V-2 = TABS, STAB, BSTA, ABST
  - V-3 = ABTS, SABT, TSAB, BTSA
  - V-4 = STBA, ASTB, BAST, TBAS
  - V-5 = BATS, SBAT, TSBA, ATSB
  - V-8 = TBSA, ATBS, SATB, BSAT
  - Octave-displaced groups:
    - Extra octave between B and T: V-1→V-6, V-2→V-7, V-3→V-12.
    - Extra octave between T and A: V-1→V-13, V-2→V-10.
    - Extra octave between A and S: V-1→V-14, V-2→V-9, V-4→V-11.
  - Worked example from the source: first-inversion Emaj7 on strings 4-3-2-1 is G# D# E B, i.e. 3 7 1 5. That gives formula ABST, which is V-2.
  — [Method 1 – How to Recognize](https://tedgreene.com/images/lessons/v_system/03_Method1_HowToRecognize.pdf)
- **Method 2** (created by Hober in the late 1980s): count how many chord tones fit in the gap between each pair of adjacent voices. Example gap signatures: V-3 = 0 1 2, V-4 = 2 1 0. **Method 3** (Greene, very late 1980s) uses the outer-voice interval plus the B–T and A–S intervals. Hober says Greene's table, even once Hober completed it in 2010, "doesn't funnel" to a single group. Hober reconstructed Methods 1 and 3 from Greene's notes, because Greene never revealed the methods while alive — [V-System Introduction](https://tedgreene.com/images/lessons/v_system/02_V-System_Introduction.pdf); [Hober, "Conversion," tedgreene.com](https://tedgreene.com/images/lessons/v_system/20_Conversion_.pdf)
- **Conversion and "drop" naming**:
  - Dropping the alto an octave turns V-1 into V-2; arrangers call this "drop-2". Greene "seemed to prefer saying 'drop alto'". Drop alto also takes V-2 to V-3, V-7 to V-8, V-8 to V-9 and V-13 to V-14.
  - Dropping the soprano two octaves turns any V-2 into a V-4. Greene "loved this particular conversion". Dropping the soprano one octave turns V-8 into V-4.
  - Dropping the tenor or bass two octaves always gives an unreachable chord.
  — [Conversion](https://tedgreene.com/images/lessons/v_system/20_Conversion_.pdf); [V-System Introduction](https://tedgreene.com/images/lessons/v_system/02_V-System_Introduction.pdf)
- **Invariants**: string transfer, transposition, systematic inversion and spacing-preserving quality changes do not change a chord's group — [V-System Introduction](https://tedgreene.com/images/lessons/v_system/02_V-System_Introduction.pdf)
- **Quality naming**: a quality is the chord name with the root removed (maj7, 6, m7…). Greene counted **43** possible four-note qualities, treating homonyms as one; m7 and 6, for example, share shapes. His "Seven Basic Qualities" sheets exist for many groups and treat homonyms as separate. He wrote add9 as **"/9"** (e.g. "D/9") — [V-System Introduction](https://tedgreene.com/images/lessons/v_system/02_V-System_Introduction.pdf); [Method 1](https://tedgreene.com/images/lessons/v_system/03_Method1_HowToRecognize.pdf)
- **Open strings**: Greene mostly used fretted notes so that progressions transpose easily. When he did use an open string, it was most often an E or A bass. The V-System works with open-string chords only "sometimes", and you have to be careful to identify which note is the soprano or bass — [Method 1](https://tedgreene.com/images/lessons/v_system/03_Method1_HowToRecognize.pdf)
- The site's per-group pages (e.g. V-6) host Greene's own sheets: "Seven Basic Qualities and Their Systematic Inversions", "Gradual Program for Absorption of V-6 Chord Colors", and progressions for hearing V-6 chords — [tedgreene.com V-6 page](https://tedgreene.com/teaching/v_system_V6.asp)
- *Chord Chemistry* contents, per retailer listings: fingerboard chart and string relationships; chord formulas and families; polytonal chords; reference charts; chord substitutions; about 109 pp. — [Goodreads](https://www.goodreads.com/book/show/525946); [Boosey & Hawkes](https://boosey.com/shop/prod/Greene-Chord-Chemistry/911209)
- Leon White's free "Trail Guide to Chord Chemistry" is a common companion to the book (via search snippet) — [tedgreene.com newsletter 2016](https://tedgreene.com/news/news_archive2016.asp)

### Inferences
- [researcher derivation] Mapping common jazz "drop" names onto the table, using C maj7 with close position C4 E4 G4 B4:
  - Drop 2 (G3 C4 E4 B4) reads path 1-3-5-7 as T,A,B,S = **TABS → V-2**, which matches Hober's statement.
  - Drop 3 (E3 C4 G4 B4) gives T,B,A,S = **TBAS → V-4**.
  - Drop 2&4 (C3 G3 E4 B4) gives B,A,T,S = **BATS → V-5**.
  - So the drop-2 / drop-3 / drop-2&4 jazz vocabulary is a subset: V-2, V-4 and V-5 respectively, as long as the source chord is V-1.
- Method 1 is easy to implement: sort the four pitches, assign B T A S, order the voices by the chord tones' position in the ascending chromatic order, look up the rotation class, then check adjacent-voice gaps above an octave to assign V-6 through V-14. The plugin can label any four-distinct-note voicing.
- Because the system excludes doublings and alternate tunings, and treats open strings with caution, it fits **band-context upper-string voicings** better than six-string open strums. For strummed open chords, use pitch-set and bass analysis (§4) rather than V-groups.
- Store `quality` separately from `root` (Greene's convention). Flag homonym pairs such as m7/6 so a verifier accepts either name.

### Gaps
- I did not read the remaining V-System PDFs (Method 1 "How to Build", Method 2 and Method 3 tables), the 43-qualities list, or any *Chord Chemistry* / *Modern Chord Progressions* page text. No legitimate full-text preview was reachable.
- Greene's chord-symbol conventions beyond "/9" (e.g. how he wrote altered dominants) are unverified.

## 2. Rikky Rooksby: open chords, capo, drones, sus/add voicings, alternate tunings

### Takeaway
I still cannot verify Rooksby's actual advice. The archive.org lending copies exist but their text servers are blocked, and no allowed site quotes him on capo, drones or tunings. What is now verified is his books' bibliographic facts and the **full table of contents of *Chord Master*** (from archive.org catalogue metadata). That table of contents shows his organizing frame: chords by function ("chords for songwriters", "chords for musical styles", "chords from famous songs") plus a "chord matrix" that covers inversions explicitly. Mechanics of capo, drones and tunings below come from other sources.

### Cited Findings
- *How to Write Songs on Guitar* (Backbeat Books, San Francisco, 2000; 192 pp.; ISBN 0879306114): subtitled on the cover "A guitar-playing and songwriting course". It includes discographical references (pp. 174–177) — [archive.org catalogue record](https://archive.org/details/howtowritesongso0000rook). A later edition (ISBN 9781493051762) is described as drawing on 1,500+ songs and adding chords, scales, modes, tunings and recording — [Perlego](https://www.perlego.com/book/5124281/how-to-write-songs-on-guitar-a-guitarplaying-and-songwriting-course-pdf); [World of Books](https://www.worldofbooks.com/en-au/products/how-to-write-songs-on-guitar-book-rikky-rooksby-9781493051762)
- *Chord Master: How to Choose and Play the Right Guitar Chords* (Backbeat, 2003; 208 pp.; companion CD of 20 tracks)
  - **Contents**: Chord questions and answers; Chords for beginners; Triads; Moveable shapes; Chords for songwriters; Chords for musical styles; Chords from famous songs; Chord progressions on the CD; The chord matrix; A chord miscellany; Appendix (chord notes and slash chords).
  - **Chord matrix**: Major plus its first and second inversions; Minor plus its inversions; aug; dim; maj7; 7; m7; m/maj7; maj7b5; maj7#5; 7b5; 7#5; m7b5; dim7; 5th; sus2; sus4; 7sus4; 6; 6/9; m6; m6/9; 7b9; 7#9; add9; maj9; 9; m(add9); m9; m9/maj7; maj11; 11; m11; maj13; 13; m7add13.
  — [archive.org catalogue record](https://archive.org/details/chordmasterhowto0000rook)
- Other Rooksby titles held on archive.org: *The Songwriting Sourcebook: How to Turn Chords into Great Songs* (2003); *Riffs* (2010); *Melody* (2004); *Lyrics* (2006); *Arranging Songs* (2007); *How to Write Songs on Keyboards* (2005) — [archive.org search, creator: Rooksby](https://archive.org/advancedsearch.php?q=creator%3A%28Rooksby%29&fl%5B%5D=identifier&fl%5B%5D=title&rows=40&output=json)
- *How to Write Songs in Altered Guitar Tunings* (Backbeat, 2010; 208 pp.; ISBN 9780879309534) covers common and less-common altered tunings, with players from Keith Richards to Nick Drake (retailer copy) — [Presto Music](https://prestoclassical.co.uk/books/products/7081272--how-to-write-songs-in-alt-guitar-tunings). It is not on archive.org under Rooksby's name.
- **Drones in open tunings (Berklee, not Rooksby)**: in open D, the diatonic shapes are fretted on the 5th and 3rd strings, "using the rest of the strings as open drones". The unfretted strings stay in the strum. Two movable shapes ("Wedge", "Brick") cover the scale up to fret 12. The source also describes alternate tunings as changing the "accessible fingerings (most notably chord voicings)" — [Abigail Aronson Zocher, Berklee Online Take Note](https://online.berklee.edu/takenote/acoustic-guitar-techniques-to-move-past-beginner-level/)
- **Partial capos as drone tools**: partial capos offer options similar to alternate tunings, "with drone strings and new chord voicings". They change open strings by shortening string length, not by changing pitch — [Wikipedia, Partial capo](https://en.wikipedia.org/wiki/Partial_capo)
- Sus2 vs add9: sus2 replaces the 3rd, add9 keeps it. Open-position shapes use open strings wherever possible — [Guitar.com Chord Clinic](https://guitar.com/articles/tuition-chord-clinic-part-1/). Rooksby's matrix lists sus2 and add9 as separate entries, consistent with this — [archive.org](https://archive.org/details/chordmasterhowto0000rook)

### Inferences
- *Chord Master*'s matrix (37 qualities with explicit inversions) works as a checklist for the plugin's chord-quality parser and suggestion vocabulary. Every entry there should be parseable and verifiable.
- Rooksby's frame of chords "for songwriters" and "for styles" suggests the plugin should tag voicings by use (colour, style), not only by theory.

### Gaps
- **No Rooksby text was verified on open chords, capo-as-colour, drones, sus/add voicings or alternate tunings.** The writer must not attribute specific advice to him. Text is available only through archive.org's controlled lending, whose servers are blocked here.
- The chapter list of *How to Write Songs in Altered Guitar Tunings* is unverified.

## 3. Alternate tunings: exact notes, Joni Mitchell notation, Nick Drake

### Takeaway
Exact notes for the common tunings are now verified (low to high): Drop D = D A D G B E; DADGAD = D2 A2 D3 G3 A3 D4 (an open Dsus4); Open G = D G D G B D; Open D = D A D F# A D; Open E = E B E G# B E; Open C = C G C G C E. Joni Mitchell's shorthand is one bass-note letter plus the fret offsets between adjacent strings, so standard tuning = E55545. Nick Drake tunings are **contested between sources**. CGCFCE and BEBEBE appear in tab and fan sources and in Wikipedia's unsourced list, and his use of alternate tunings to make cluster chords is well attested.

### Cited Findings
- Drop D: D-A-D-G-B-E, standard tuning with the 6th string dropped a whole step. Most guitarists get there by detuning the low E — [Wikipedia, List of guitar tunings](https://en.wikipedia.org/wiki/List_of_guitar_tunings)
- DADGAD: low to high D2 A2 D3 G3 A3 D4. From standard, the 1st, 2nd and 6th strings go down a whole tone. The open strings form "an open D, suspended fourth chord", neither major nor minor. It was popularized by Davey Graham after he heard an oud player in Morocco. It is associated with Celtic music and was used on Led Zeppelin's "Kashmir" and "Black Mountain Side" — [Wikipedia, DADGAD](https://en.wikipedia.org/wiki/DADGAD)
- Open G: D-G-D-G-B-D, also called "Spanish" or "Chicago" tuning. Joni Mitchell used the variant G-G-D-G-B-D on "Electricity", "For the Roses" and "Hunter". Keith Richards uses five-string G-D-G-B-D on "Honky Tonk Women", "Brown Sugar" and "Start Me Up" — [Wikipedia, Guitar tunings](https://en.wikipedia.org/wiki/Guitar_tunings); [List of guitar tunings](https://en.wikipedia.org/wiki/List_of_guitar_tunings)
- Open D: D-A-D-F#-A-D, also called "Vestapol". Used by Joni Mitchell ("Big Yellow Taxi") and Nick Drake ("Place To Be") — [List of guitar tunings](https://en.wikipedia.org/wiki/List_of_guitar_tunings). Berklee gives retuning steps by fret-matching and lists "Pink Moon" (Drake) and "You Turn Me On, I'm a Radio" (Mitchell) as open-D songs — [Berklee Online](https://online.berklee.edu/takenote/acoustic-guitar-techniques-to-move-past-beginner-level/)
- Open E: E-B-E-G#-B-E. Use light-gauge strings, because three strings must be raised. The variant E-G#-B-E-B-E avoids raising strings — [List of guitar tunings](https://en.wikipedia.org/wiki/List_of_guitar_tunings)
- Open C: C-G-C-G-C-E (William Ackerman, John Fahey). Overtone variant: C-C-G-C-E-G — [List of guitar tunings](https://en.wikipedia.org/wiki/List_of_guitar_tunings)
- Drop and double-drop: drop D lowers the 6th string to D, and double drop D lowers both the 6th and 1st to D. Open tunings retune strings so that the open strings sound a chord — [Berklee Online](https://online.berklee.edu/takenote/acoustic-guitar-techniques-to-move-past-beginner-level/)
- **Joni Mitchell notation**: "one letter naming the note of the open lowest string, followed by the relative fret (half-step) offsets between adjacent strings"; standard = **E55545** — [Wikipedia, Guitar tunings](https://en.wikipedia.org/wiki/Guitar_tunings), citing jonimitchell.com "Notation". The tuning-family example (DAEF#AD and BF#C#D#F#B both "77235") is still via search snippet only — [jonimitchell.com tuning patterns](https://jonimitchell.com/music/tuningpatterns.cfm)
- **Nick Drake, verified**: he was self-taught and used alternate tunings "to create cluster chords" hard to get in standard tuning; many melodies rest on chord extensions. He often paused to retune between songs on stage — [Wikipedia, Nick Drake](https://en.wikipedia.org/wiki/Nick_Drake)
- **Nick Drake, unsourced or contested**:
  - Wikipedia's list has "Drake's Drone: B-E-B-E-B-E" ("Man in a Shed", "From the Morning"), but marked [citation needed] — [List of guitar tunings](https://en.wikipedia.org/wiki/List_of_guitar_tunings)
  - For "Pink Moon", sources split between CGCFCE (capo 2) and DADGDF#. A player's list also gives DADGDF# with capo 1 (via search snippet) — [guitartabs.cc Nick Drake tunings](https://guitartabs.cc/tabs/d/drake_nick/tunings_tab.html); [ragajunglism.org Pink Moon](https://ragajunglism.org/tunings/menu/pink-moon/); [Guitar World Nick Drake lesson](https://guitarworld.com/uncategorized/hole-notes-unsung-acoustic-artistry-nick-drake)
  - Berklee lists "Pink Moon" as open D, a third claim. [researcher derivation] CGCFCE capoed at 2 sounds D A D G D F#, so the "CGCFCE capo 2" and "DADGDF#" claims agree on sounding pitch. Berklee's open D (D A D F# A D) differs.
- Count of Joni's tunings: "over 50" vs "about 60" — [Roadie Music](https://www.roadiemusic.com/blog/joni-mitchells-alternative-tunings/)

### Inferences
- [researcher derivation] Joni codes for the seed tunings:
  - Drop D = D 75545
  - DADGAD = D 75525
  - Open G = D 57543
  - Open D = D 75435
  - Open E = E 75435 (same family as Open D, so it transposes)
  - Open C = C 75754
  - CGCFCE = C 75574
- Store sounding pitches **and** the Joni code. Same-code tunings are transpositions of each other, so shapes map between them one-to-one, possibly via a capo.

### Gaps
- No primary source (Drake's estate, Joe Boyd, or a magazine transcription on an allowed host) confirmed the song-by-song Drake tunings. Treat them as contested.
- jonimitchell.com was blocked, so the family example remains via snippet.

## 4. Capo mechanics and practical limits

### Takeaway
A capo is equivalent to retuning every string up the same amount, but only the open notes change. Wikipedia notes that shorter scale length changes timbre and that capos are used partly for brightness. Partial capos clamp subsets of strings (the Esus type: strings A, D, G). **No source found states a fret-7 ceiling or describes timbre "above fret 7"**; that remains a heuristic. Real high-capo issues are intonation and pulling strings sharp (forum and retailer sources).

### Cited Findings
- A capo shortens the playable length of all strings and raises pitch. It is "the same musical effect as retuning all strings up", but only open notes are affected; for example, the 7th fret of the E string still plays B — [Wikipedia, Capo (musical device)](https://en.wikipedia.org/wiki/Capo_(musical_device))
- "The scale length of the strings… affects the timbre", so a capo "may alter the tone". Capos are also used to bring down-tuned guitars, such as 12-strings, back up to standard pitch. Folk, flamenco and Irish styles use capos often; classical and jazz rarely do — [Wikipedia, Capo (musical device)](https://en.wikipedia.org/wiki/Capo_(musical_device))
- A standard capo is used "to achieve a brighter timbre or to transpose" — [Wikipedia, Partial capo](https://en.wikipedia.org/wiki/Partial_capo)
- **Partial capos**:
  - A 5-string capo leaving the low E open, at fret 2, mimics drop D raised a tone; it is marketed as a "drop D capo". Unlike retuning, the fretted 6th string is unaffected.
  - The Esus style clamps A, D and G. At fret 2 it forms Esus; flipped, it forms A.
  - The Third Hand and SpiderCapo can clamp any of the **63** string combinations.
  - Shubb and Kyser make 3-string "E-sus" and 5-string "Drop-E" capos.
  - Harvey Reid popularized partial capos; his 1980 book *A New Frontier in Guitar* gives 25 uses of the Third Hand Capo.
  — [Wikipedia, Partial capo](https://en.wikipedia.org/wiki/Partial_capo)
- Intonation at higher capo positions: forum reports of strings going sharp when capoed from fret 3–4 upward, the advice to retune after clamping, and placing the capo just behind the fret (via search summary; forum-grade) — [Gibson forum](https://forum.gibson.com/topic/109099-intonation-when-capod-southern-jumbo/); [Andertons, Capo intonation](https://blog.andertons.co.uk/learn/capo-intonation)
- Open strings ring differently, more "jangly", when capoed (via search snippet) — [Yamaha Hub](https://hub.yamaha.com/guitars/g-how-to/the-art-of-using-a-capo)
- Sound On Sound's "Alternative Guitar Tunings for the Studio" reportedly covers capo repositioning and "Nashville" high stringing (via search snippet only; host unreachable) — [SOS](https://www.soundonsound.com/techniques/alternative-guitar-tunings-studio)
- ChordPro convention: `{key}` stays as the shape key under `{capo: n}`, "because guitar players consider the key relative to the chord shapes"; `decapo` transposes chords to concert pitch — [ChordPro docs, capo](https://raw.githubusercontent.com/ChordPro/chordpro/master/docs/content/Directives-capo.md); [config](https://raw.githubusercontent.com/ChordPro/chordpro/master/docs/content/ChordPro-Configuration-Generic.md)

### Inferences
- `sounding = shape + capo (semitones)`, applied per string for partial capos. A string clamped at fret c cannot be fretted below c.
- **Fret-7 limit = heuristic.** Present it as a soft warning ("high capo: brighter and thinner, frets cramped, check tuning"), not a rule.
- The Esus partial capo at fret 2 on EADGBE gives open strings E B E A B E [researcher derivation]. This matches the four-string-capo caption on Wikipedia, F#BEABE, which places the capo on strings 5–2 rather than the 3-string Esus.

### Gaps
- No authoritative measurement or pedagogy text ties a specific fret to timbre change.
- The SOS article text remains unread.

## 5. Fingering representation, verification and open datasets

### Takeaway
Unchanged from the prior pass, where it was verified against GitHub raw files: chords-db (MIT; 828 chords / 3,283 positions, standard tuning) and tonal (MIT; multi-candidate `Chord.detect`). **GuitarSet is now better pinned down**: 360 excerpts of about 30 s, 6 players × 2 modes (comp/solo) × 5 styles × 3 progressions, hexaphonic plus mic audio, 16 JAMS annotations per excerpt. Its Zenodo record (3371780, v1.1.0) is about 8.2 GB (via search snippet). The CC BY 4.0 notice found is the **ISMIR paper's** licence; the data licence is still not confirmed from Zenodo directly.

### Cited Findings
- **chords-db**:
  - Fields: `frets` (−1 = muted), `fingers`, `baseFret`, `barres`, `capo`, `midi`.
  - Example: C major `[-1,3,2,0,1,0]` → midi [48,52,55,60,64].
  - Standard tuning E2 A2 D3 G3 B3 E4, `fretsOnChord: 4`.
  - Researcher count: 12 keys × 86 suffixes = 828 chords, 3,283 positions. MIT, © 2016 David Rubert.
  — [chords-db guitar.json](https://raw.githubusercontent.com/tombatossals/chords-db/master/lib/guitar.json); [LICENSE](https://raw.githubusercontent.com/tombatossals/chords-db/master/LICENSE)
- **tonal**: `Chord.detect(["E","G#","B","C#"]) → ["E6","C#m7/E"]`; `assumePerfectFifth` allows a missing 5th; MIT — [tonal chord-detect README](https://raw.githubusercontent.com/tonaljs/tonal/main/packages/chord-detect/README.md); [npm](https://registry.npmjs.org/tonal/latest)
- **ChordPro `{define}`**: `base-fret N frets …`, with `x`/`N`/`-1` = muted and frets relative to base-fret — [ChordPro define](https://raw.githubusercontent.com/ChordPro/chordpro/master/docs/content/Directives-define.md)
- **GuitarSet contents**:
  - 360 excerpts "close to 30 seconds".
  - 6 players; comping and soloing; styles Rock, Singer-Songwriter, Bossa Nova, Jazz, Funk; progressions 12-bar blues, Autumn Leaves, Pachelbel Canon; key sampled at random.
  - Hexaphonic pickup plus a Neumann U-87 reference mic. Audio variants: hex, hex_cln, mic, mix.
  - 16 JAMS annotations per excerpt, including 6 per-string pitch contours plus "instructed" and "performed" chord annotations.
  — [mirdata guitarset.py (GitHub raw)](https://raw.githubusercontent.com/mir-dataset-loaders/mirdata/master/mirdata/datasets/guitarset.py)
- **GuitarSet hosting and size**: Zenodo record 3371780, v1.1.0, published 20 Aug 2019, about 8.2 GB; v1.0.1 was about 7.5 GB (via search snippet). mirdata also references a newer index on Zenodo record 14007634 — [Zenodo 3371780](https://zenodo.org/record/3371780); [mirdata](https://raw.githubusercontent.com/mir-dataset-loaders/mirdata/master/mirdata/datasets/guitarset.py)
- **GuitarSet licence**: the GitHub repo has no licence detected by the GitHub API (the earlier note's "MIT" claim for the repo is not confirmed; correct it). The ISMIR 2018 paper carries a CC BY 4.0 notice (via search snippet) — [GitHub API marl/GuitarSet](https://api.github.com/repos/marl/GuitarSet); [ISMIR 2018 paper](https://ismir2018.ismir.net/doc/pdfs/188_Paper.pdf)
- **GuitarSet known errata**: incorrect timings in two annotations, and a duplicated note in one MIDI annotation — [GuitarSet README](https://raw.githubusercontent.com/marl/GuitarSet/master/README.md)
- Researcher-verified arithmetic: `x32010` = C; `x02210` = Am; `x02010` = Am7; `x32210` = {C,E,A}, read as Am/C or C6(no5). Am7 and C6 share a pitch-class set, and Greene treats such pairs as "homonyms" — [V-System Introduction](https://tedgreene.com/images/lessons/v_system/02_V-System_Introduction.pdf)

### Inferences
- The verification pipeline is unchanged (see Implications). GuitarSet's "instructed vs performed chord" pair is a ready-made test set for "did the player play the chord on the chart?". Use it only after the data licence is confirmed.

### Gaps
- GuitarSet's data licence is not confirmed on Zenodo (host blocked).
- No openly licensed **alternate-tuning** fingering dataset was found.
- Other guitar datasets (e.g. IDMT-SMT-Guitar, EGDB) were not checked this pass.

## 6. Describing strum and picking feel in words and counts

### Takeaway
Verified vocabulary:
- **Counting**: 1 & 2 & for eighths, 1 e & a for sixteenths, "1 tri-ple" for triplets.
- **Patterns by subtraction**: a steady base stroke grid with strokes removed.
- **Swing**: long-short pairs, nominally 2:1 "triplet" swing, though in practice the ratio is subtler and ranges from soft to hard swing.
- **Funk**: a steady 16th-note hand with fretting-hand damping.
- **Travis picking**: an alternating bass under syncopated melody.
- **Tone and touch**: Berklee's "sul tasto" / "sul ponticello" placement and touch vocabulary.

### Cited Findings
- Counting: sixteenths in 4/4 are counted "1 e & a 2 e & a…", using numbers for quarters, "&" for eighths and "e"/"a" for sixteenths. Triplets: "1 tri ple 2 tri ple". There are competing systems (e.g. Eastman: "1 te", "1 ti te ta") — [Wikipedia, Counting (music)](https://en.wikipedia.org/wiki/Counting_(music))
- Strumming: start from a straight-eighths base, and "many patterns are created through subtracting beats from this base". Example: drop the 2nd and 5th of eight. Swung eights resemble "the first and third notes in a triplet". In funk the strumming hand keeps a steady 16th motion while the fretting hand damps strokes. Reggae and ska use a few staccato "chops" per bar — [Wikipedia, Strum](https://en.wikipedia.org/wiki/Strum)
- Swing ratios: the first note is "often understood to be twice as long", but in practice the ratio is "much more subtle". Labels: soft (between 1:1 and 2:1), triplet (2:1), hard (between 2:1 and 3:1), dotted (3:1). In funk, swing is often applied to sixteenths — [Wikipedia, Swing (jazz performance style)](https://en.wikipedia.org/wiki/Swing_(jazz_performance_style))
- Travis picking: named after Merle Travis, it combines "alternate-bass fingerpicking and syncopated melodies", usually on steel-string acoustic. It belongs with "pattern picking", meaning preset right-hand patterns — [Wikipedia, Fingerstyle guitar § Travis picking](https://en.wikipedia.org/wiki/Fingerstyle_guitar#Travis_picking)
- Fender: on a C shape the thumb alternates between the 5th and 4th strings, and fingers are added later — [Fender](https://www.fender.com/articles/techniques/travis-picking-on-guitar)
- Pendulum strumming: constant down-up motion, with rhythm coming from which passes contact the strings — [Guitar World](https://www.guitarworld.com/lessons/beginner-lessons/pendulum-strumming); [TrueFire](https://blog.truefire.com/guitar-lessons/guitar-syncopation-explained/)
- Shuffle: the "ands" land later while beats stay put — [JustinGuitar](https://justinguitar.com/guitar-lessons/shuffle-grooves-strumming-bg-1302)
- Berklee on strumming texture:
  - Control a strum through "touch, tone, dynamics, balance, registers, melodic lines, and bass lines".
  - *Sul tasto* (over the fingerboard) is "sweeter and rounder"; the bridge side is brighter.
  - The strum path can be straight or angled.
  - Touch character: slow or quick through the strings, light or heavy.
  - Listening examples: Richie Havens "Freedom", Michael Hedges "Ritual Dance".
  — [Berklee Online, Zocher](https://online.berklee.edu/takenote/acoustic-guitar-techniques-to-move-past-beginner-level/)
- Half-time feel (drums): the backbeat moves to beat 3. Applying this to guitar is an inference — [Cruise Ship Drummer](https://cruiseshipdrummer.com/2012/09/17/half-time-feel-rock-using-syncopation/)

### Inferences
- A word-and-count feel description can be generated from five parameters:
  - grid: 8ths or 16ths, straight or swung, with a swing ratio from soft to hard
  - which grid slots sound (the subtraction mask)
  - accents relative to the backbeat
  - hand location and touch (Berklee terms)
  - bass motion (alternating root-5th for Travis)
- Example output: "16ths, keep the hand moving; hit 1, the & of 2, and 4; lean on 2 and 4; play over the soundhole, light touch." Use these as options, not rules.

### Gaps
- No Acoustic Guitar magazine or Sound On Sound text on wording feel was reachable (SOS blocked; acousticguitar.com not allowed).

## Implications for the plugin

**Data model**
- `Tuning { id, name, strings: [MIDI low→high], joni_code }`. Seed with the verified tunings: Standard E2 A2 D3 G3 B3 E4; Drop D DADGBE; DADGAD D2 A2 D3 G3 A3 D4; Open G DGDGBD; Open D DADF#AD; Open E EBEG#BE; Open C CGCGCE ([Wikipedia tunings list](https://en.wikipedia.org/wiki/List_of_guitar_tunings), [DADGAD](https://en.wikipedia.org/wiki/DADGAD)). Add CGCFCE and BEBEBE flagged "contested/unsourced". Compute Joni codes (standard = E55545, [Wikipedia](https://en.wikipedia.org/wiki/Guitar_tunings)) and use them to detect same-family tunings.
- `Capo { per_string: [int] }`. Full capo is uniform. Model partial capos per string (Esus = clamp strings 5, 4, 3; "drop-D" 5-string = all but string 6) ([Partial capo](https://en.wikipedia.org/wiki/Partial_capo)).
- `Fingering { frets, base_fret, fingers?, barres?, tuning_id, capo }`. Accept `x32010`, ChordPro `{define}` and chords-db JSON.
- Derived fields: `pitches`, `pitch_classes`, `bass`, `open_string_count`, `span`, and for four distinct notes, a **`v_group`** (Greene V-1…V-14 via Method 1; [tedgreene.com](https://tedgreene.com/images/lessons/v_system/03_Method1_HowToRecognize.pdf)) with a `drop_alias` (drop-2 = V-2, drop-3 = V-4, drop-2&4 = V-5 from close position; researcher derivation).

**Verification algorithm**
1. Absolute frets → pitches = tuning + capo[i] + fret. Reject a fretted note below a clamped capo.
2. Pitch-class set plus bass vs the parsed chord (required / optional / tension tones). Accept an omitted 5th, and a rootless voicing in band mode.
3. On ambiguity, return all candidates (tonal-style), including Greene "homonyms" (m7 ↔ 6, Am/C ↔ C6(no5)).
4. Playability: span ≤ 4 frets (soft 5); ≤ 4 fingers, with a barre counting as 1.
5. Parser coverage target: every quality in Rooksby's *Chord Master* matrix, including inversions, 6/9, m6/9, m9/maj7 and m7add13 ([archive.org](https://archive.org/details/chordmasterhowto0000rook)). Accept Greene's "/9" as a synonym for add9.

**Capo and transpose**
- Sounding = shape + capo. Search capo 0–7 and rank shape keys by open-string count. Above fret 7, show a **heuristic** soft warning (brighter and thinner, cramped, retune; no authoritative source for the threshold). Wikipedia supports only that capo position changes timbre and brightness ([Capo](https://en.wikipedia.org/wiki/Capo_(musical_device))).
- Output a ChordPro shape key + `{capo}` for the player and a decapo concert-pitch chart for the band ([ChordPro](https://raw.githubusercontent.com/ChordPro/chordpro/master/docs/content/Directives-capo.md)).

**Voicing suggestions**
- Drone continuity: prefer voicings that keep shared open strings ringing. In open tunings, offer "fret two strings, let the rest drone" shapes ([Berklee](https://online.berklee.edu/takenote/acoustic-guitar-techniques-to-move-past-beginner-level/)). Keep sus2 and add9 distinct.
- Band mode: four-note voicings on the top or middle string sets, labelled by V-group. Offer **string transfer** (same group, different set) and **conversions** ("drop alto" V-1→V-2; "drop soprano two octaves" V-2→V-4) as the "same chord, new colour/register" moves ([tedgreene.com Conversion](https://tedgreene.com/images/lessons/v_system/20_Conversion_.pdf)). Do not apply V-groups to doubled six-string strums or alternate tunings, which are outside the system's scope.
- Second guitar: same sounding key, different capo and shape pair.
- Do **not** attribute any of this advice to Rikky Rooksby. His specific views remain unverified.

**Coaching language for feel**
- Generate descriptions from: grid (counted "1 e & a"), the subtraction mask, swing ratio named soft/triplet/hard, accents vs the backbeat, hand placement and touch (sul tasto = sweeter and rounder), and bass motion (Travis = alternating bass plus syncopated melody) ([Counting](https://en.wikipedia.org/wiki/Counting_(music)), [Strum](https://en.wikipedia.org/wiki/Strum), [Swing](https://en.wikipedia.org/wiki/Swing_(jazz_performance_style)), [Fingerstyle](https://en.wikipedia.org/wiki/Fingerstyle_guitar#Travis_picking), [Berklee](https://online.berklee.edu/takenote/acoustic-guitar-techniques-to-move-past-beginner-level/)). Phrase everything as options.

**Licensed offline data**
- Bundle chords-db (MIT) and tonal (MIT). Generate alternate-tuning shapes algorithmically, since no open dataset was found. Use GuitarSet (about 8.2 GB, 360 excerpts) only as an evaluation set, and only after confirming its data licence on Zenodo. The CC BY 4.0 notice seen applies to the paper, and the GitHub repo shows no licence.
