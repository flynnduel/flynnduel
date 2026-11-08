# Melody guide

The plugin coaches melody and never writes or "corrects" notes. This guide holds the questions it asks and the numbers it may quote: Perricone's singability checks and bridge levers, Pattison's phrase placement, roadmaps and stress rules, the limits of the Hayes and Smith text-setting work, and key choice by tessitura. The writer plays and chooses; the plugin asks, measures and names options. [design]

Attribution matters here. Perricone's Melody in Songwriting excerpt and his own song analysis were read; his Great Songwriting Techniques was not. The front-heavy and back-heavy definitions below are Pattison's. Tags show the evidence level; see sources.md.

## Singability

- Perricone's phrase definition: a phrase usually completes a musical statement and ends by resting, holding or reaching resolution, and in vocal music it is tied to natural breathing places. [verified]
- Most vocal melody is conjunct (moves by step), and leaps give a melody character and a memorable profile; a mix usually works. [verified]
- Perricone's character list: rhythmic structure, contour, tonal makeup and intervallic content. [verified]
- Perricone says it is essential to sing your own melody. [verified]
- Check 1, leaps: how many are there, and is it too disjunct to sing? [verified]
- Check 2, breath: does the singer have time to breathe between phrases? [verified]
- Check 3, range: is the range too wide, and does it change too quickly within a section? [verified]
- Melody written at an instrument, especially piano, can be hard or impossible to sing. [verified]
- So ask the writer to sing the melody. [design]
- Computable descriptors for these checks, all asked as questions: share of intervals larger than a step, rests or long holds between phrases, total range, and range change per section. [design]
- Phrase endings: ask which phrases end on stable tones (1, 3, 5) and which on unstable ones (2, 4, 6, 7), and whether an open ending is resolved by the next section. The stable/unstable split is standard tonal theory, not read in Perricone's tendency table. [design]
- Perricone's own song resolves an unstable scale degree 4 at the end of the bridge to degree 3 at the next A. [verified]
- Motif development: state a one-bar idea, repeat it over a changed chord, then extend it. His phrase lengths run 1, 1, 2, 4 and 4 bars, and a phrase ending on the downbeat of the third bar leaves room to breathe. [verified]
- Contour against meaning: he raised his title melody to match a positive lyric. [verified]
- Ask whether the title line's direction agrees with its feeling. [design]
- Bridge contrast has five levers in his example: a different starting chord (IV, not I), plainer rhythm, plainer contour, more uniform phrasing (2+2+4 bars) and a middle-register tessitura against a wider A section. [verified]
- A bridge still has to belong to the song; his shares the key, earlier harmonies and the lyric's point of view. [verified]
- Berklee's melody course (taught by Kachulis, not Perricone) starts with phrase beginnings and stressed words and moves to chord-tone melodies; titles only were read. [verified]
- Perricone's book-level material on stable and unstable tones, tone tendencies and tonally open and closed phrases is known from tables of contents. [as reported]
- Webb: no melody rule of his could be verified. Use him only for the prompt "if the melody is stuck, change what is under it". [as reported]

## Phrasing

- Pattison: a phrase that starts on the downbeat, or picks up to it, is front-heavy and feels solid and stable; one that starts after the downbeat is back-heavy and feels in motion, and the later it starts the less stable. [verified]
- In 4/4 a phrase starting after beat 3 usually acts as a pickup to the next downbeat; such phrases count as front-heavy. [verified]
- Strong and weak bars alternate. Phrasing in the weak bar (strong bar left empty) feels floaty like back-heavy phrasing, and back-heavy in a weak bar is floatier still. [verified]
- Pattison suggests looking for downbeats and strong bars for lines you really mean, and back-heavy or weak-bar phrasing for regret or longing. [verified]
- Offer these as options, not rules. [design]
- Doubling a phrase's length while moving its placement is one of Pattison's section-contrast examples. [verified]
- Roadmaps: a melody that repeats a two-part phrase sets up two independent ideas, and if the lyric's ideas break somewhere else the result is confusion. [verified]
- Pattison's roadmap fixes: change the lyric, change the music, or repeat a word from the end of one line at the start of the next. [verified]
- Offer them side by side. [design]
- Check: find melodic breaks (rests, long holds, repeated units) and ask whether each lyric clause crosses one, or each break splits a grammatical unit. [design]
- Perricone's own definitions of front-heavy and back-heavy were not read, so name Pattison as the source and say only that Perricone uses the same terms. [as reported]
- Stolpe's worked contrast pattern ties phrasing to feeling: short post-downbeat phrases for uncertainty, a long downbeat phrase for security, and two-bar pickup phrases for the chorus. [verified]
- Line length and rhyme set stability in the lyric (see lyrics.md). [verified]
- Melody and lyric should agree on whether a section is settled or moving; that is Pattison's prosody idea applied by the plugin. [design]

## Prosody

- The core rule: put stressed syllables on stressed positions. A mismatch breaks no law but sounds unnatural and deflates the line. [verified]
- In 4/4, beats 1 and 3 are strong and 2 and 4 weak, and the strong-weak pattern repeats at every subdivision; in a strong pair the first half note outweighs the second. [verified]
- Anticipation: an onset just ahead of a strong beat borrows that beat's strength; an anticipated downbeat can be the strongest position in the phrase. A tied note from far away does not inherit the beat. [verified]
- Other things that create a stressed position in Pattison's Berklee syllabus: isolating a note, a rest before it, shorter notes before it, and anticipating it; length adds punch. [verified]
- Three-tier stress lexicon: dictionary stress inside words of two or more syllables; monosyllables stressed by job: nouns, verbs, adjectives and adverbs carry stress and function words do not; two-syllable function words such as "before" demoted to medium positions. [verified]
- Context changes stress: intensifiers and negatives take stress, and the same word flips with its grammar, as interrogative "what's" is stressed and relative "what's" is not. [verified]
- Gray areas in strings of monosyllables are settled by meaning and some trial and error, and the writer can always mark contrastive focus. [verified]
- "Traffic signs, not cargo" is a third-party paraphrase; Pattison's own images are workers who work hard and signs that direct traffic. [verified]
- Do not quote the paraphrase as his. [design]
- Matching later verses: line up stressed and unstressed syllables, and also put the important words in the same places. Allow a syllable of slack for pickups and words like fire or every that can be sung as one or two. [verified]
- His published critique of a hit lists test cases: an unstressed word on a downbeat, a secondary stress of a long word on a strong beat, and a final weak suffix on a downbeat. [verified]
- Rhythmic variation: arrange natural stresses against the established pattern instead of wrenching words to keep one meter. [verified]
- Flag order for the toolkit, soft and ranked: a stress inversion inside a word first, then a content word on a weak position beside a function word on a strong one, then a lapse of three empty positions, then extreme compression. Flags in a chorus count for more than in a verse. [design]
- Never output pass or fail per syllable; show the writer's setting against the best-scoring alternative and treat a flag as a question. [design]

## Key and range

- Tessitura is the heart of a range, the share of it used most, not its extremes. [verified]
- Perricone's A section spans an octave and a sixth while his bridge sits mainly in the middle of the voice, a deliberate tessitura contrast. [verified]
- Ask about three numbers: the singer's comfortable low, comfortable high, and best-tone ceiling (the highest note sung with the tone wanted). [as reported]
- Method: per section, find the lowest note, the highest note and a duration-weighted centre, keep keys whose peak is at or under the ceiling and whose low is at or above the floor, and rank by how the tessitura sits in the comfortable zone. The weighting is the research team's own method; no source quantifies tessitura this way. [design]
- Warn when lowering the key to save a chorus peak pushes the verse lows out of reach. [design]
- A capo only raises pitch (non-primary sources). The fret-7 limit is an unsourced heuristic (see guitar.md). [unverified]
- A typical comfortable span is about an octave for almost anyone and an octave to an octave and a third for most singers, from a search snippet. [as reported]
- Perricone's octave-and-a-fifth guideline exists only in unofficial copies, and his own octave-and-a-sixth section shows it is not a cap. [as reported]
- Vowel and singability advice is informal voice pedagogy that disagrees with itself; do not attribute it to the authors above. [unverified]

## Limits

- Hayes's text-setting grammar uses ten ranked, violable constraints and matched native speakers' favourite setting 70% of the time (70.6%) against 23.1% for the older Halle and Lerdahl algorithm. Hayes himself calls that not good enough. [verified]
- State this limit whenever a prosody result is given. [design]
- The 70% figure is from English folksong data, not pop. [verified]
- So treat the check as a second opinion. [design]
- A 16-position line has at most about 13,000 possible settings. [verified]
- That is few enough for the toolkit to enumerate every setting. [design]
- Good settings often sacrifice a stress match to avoid a lapse. [verified]
- So treat a mismatch as a question, not an error. [design]
- Hayes and Kaun add four stress levels, prosodic-phrase effects and duration matching, and a setting can win despite a stress mismatch when its rivals do worse elsewhere. [verified]
- Smith: phrasal stress is the only way to explain mismatches on monosyllables, and a mismatch inside a word usually hurts more than extra emphasis on a word. [verified]
- Smith separates syncopation (text against the meter) from prosodic dissonance (text against the melody's own accents): a syllable off the beat that gets a longer note or a pitch peak is not flagged. [verified]
- Smith finds dissonances cluster in verses more than choruses, and cautions against strict numeric scoring. [verified]
- The pronunciation dictionary gives citation stress only: no phrasal stress, no function-word demotion, no dialect, and single-syllable words unmarked. [verified]
- Words missing from the dictionary are estimated, and the writer can add pronunciations. [design]
- Never write melodies, name "correct" pitches or rewrite the writer's tune. [design]
