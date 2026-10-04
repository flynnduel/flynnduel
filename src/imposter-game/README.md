# Imposter

A party game for 3–12 friends in the same room. Everyone gets the secret word
except the imposter, who has to bluff. Each person plays on their own phone or
laptop; one computer runs the game.

## Run it

You need [Node.js](https://nodejs.org) 20 or newer.

```bash
cd imposter-game
npm install      # first time only
npm start
```

The terminal prints a link like `http://192.168.1.23:3000` and a QR code.

- **Everyone, including you,** opens that link in a browser and types a name.
  If you're the host and only have the computer, open the link in a browser tab
  there and play like everyone else.
- Everyone must be on the **same Wi-Fi** as the computer running the game.
- The first person to join is the **leader** (👑). They pick the settings and press
  Start, Start the vote, and Next round. Everything else happens on each person's
  own screen.
- Tap **?** at any time to see the rules.

## Settings

- **Clue rounds:** how many times everyone gives a clue before the vote (1–3, default 2).
- **Points to win:** first to this score wins (3–30, default 10).

## Make it yours

`server/words.js` holds every word. The secret **Inside Jokes** category
(`SECRET.insideJokes.words`) turns up about 1 round in 40. Replace its words
with your group's own references, then restart the game.

## Troubleshooting

- **Friends can't connect:** make sure they're on the same Wi-Fi, and allow Node
  through your firewall if your computer asks.
- **Port already in use:** `PORT=3001 npm start` (on Windows PowerShell:
  `$env:PORT=3001; npm start`).
- **Someone's phone fell asleep:** just reopen the link. They come back with the
  same role and score.
- Stopping the server (Ctrl+C) ends the game and clears scores.

## Development

```bash
npm test
```

Game logic lives in `server/game.js` and `server/rules.js`; `server/view.js` is the
only place that decides what each player is allowed to see.
