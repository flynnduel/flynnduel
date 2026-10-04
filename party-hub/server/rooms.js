'use strict';
const { Room } = require('./room');

const LETTERS = 'ABCDEFGHJKLMNPQRSTUVWXYZ';
const EMPTY_TTL_MS = 1_800_000;

class Rooms {
  constructor({ rng = Math.random, now = Date.now } = {}) {
    this.rng = rng;
    this.now = now;
    this.rooms = new Map();
  }

  _newCode() {
    let code;
    do {
      code = '';
      for (let i = 0; i < 4; i++) code += LETTERS[Math.floor(this.rng() * LETTERS.length) % LETTERS.length];
    } while (this.rooms.has(code));
    return code;
  }

  create() {
    const room = new Room({ code: this._newCode(), rng: this.rng, now: this.now });
    room.emptySince = this.now();
    this.rooms.set(room.code, room);
    return room;
  }

  get(code) {
    if (typeof code !== 'string') return null;
    return this.rooms.get(code.trim().toUpperCase()) || null;
  }

  sweep() {
    const t = this.now();
    for (const [code, room] of this.rooms) {
      if (room.emptySince != null && t - room.emptySince >= EMPTY_TTL_MS) this.rooms.delete(code);
    }
  }
}

module.exports = { Rooms };
