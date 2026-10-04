'use strict';
const { validateAvatar } = require('./avatar');

const MAX_PLAYERS = 12;
const MAX_NAME = 16;
const MAX_CHAT = 140;
const CHAT_KEEP = 50;
const CHAT_GAP_MS = 1000;
const NOT_NOW = { ok: false, error: 'Not now' };

class Room {
  constructor({ code, rng = Math.random, now = Date.now } = {}) {
    this.code = code;
    this.rng = rng;
    this.now = now;
    this.players = new Map(); // id -> player
    this.hostId = null;
    this.emptySince = null; // Rooms.create stamps it so never-joined rooms get swept too
    this.chatLog = [];
    this.chatPaused = false; // later tasks flip this during talk phases
    this.fx = [];
    this._nextId = 1;
    this._lastChatAt = new Map();
  }

  _err(error) {
    return { ok: false, error };
  }

  _byToken(token) {
    if (typeof token !== 'string' || !token) return null;
    for (const p of this.players.values()) if (p.token === token) return p;
    return null;
  }

  _connectedCount() {
    let n = 0;
    for (const p of this.players.values()) if (p.connected) n++;
    return n;
  }

  _ensureHost() {
    const host = this.players.get(this.hostId);
    if (host && host.connected) return;
    let best = null;
    for (const p of this.players.values()) {
      if (p.connected && (!best || p.joinedAt < best.joinedAt)) best = p;
    }
    if (best) this.hostId = best.id; // otherwise keep the old host seat until someone connects
  }

  _uniqueName(p) {
    const taken = new Set();
    for (const o of this.players.values()) if (o !== p && o.connected) taken.add(o.name.toLowerCase());
    if (!taken.has(p.name.toLowerCase())) return p.name;
    for (let n = 2; ; n++) {
      const suffix = ' ' + n;
      const cand = p.name.slice(0, MAX_NAME - suffix.length).trimEnd() + suffix;
      if (!taken.has(cand.toLowerCase())) return cand;
    }
  }

  _markConnected(p) {
    if (!p.connected) p.name = this._uniqueName(p);
    p.connected = true;
    this.emptySince = null;
    this._ensureHost();
  }

  join({ name, token, avatar } = {}) {
    const existing = this._byToken(token);
    if (existing) {
      this._markConnected(existing);
      return { ok: true, playerId: existing.id };
    }
    if (typeof token !== 'string' || !token) return this._err('Missing token');
    const clean = typeof name === 'string' ? name.trim() : '';
    if (clean.length < 1 || clean.length > MAX_NAME) return this._err('Name must be 1-16 characters');
    const lower = clean.toLowerCase();
    for (const p of this.players.values()) {
      if (p.connected && p.name.toLowerCase() === lower) return this._err('That name is taken');
    }
    if (this.players.size >= MAX_PLAYERS) return this._err('Room is full');
    const av = avatar == null ? null : validateAvatar(avatar);
    if (av && !av.ok) return this._err(av.error);
    const player = {
      id: 'p' + this._nextId++,
      token,
      name: clean,
      avatar: av ? av.avatar : { kind: 'dicebear', style: 'lorelei', seed: clean.slice(0, 32), options: {} },
      connected: true,
      joinedAt: this.now(),
      team: null,
      spectator: false,
      points: 0,
    };
    this.players.set(player.id, player);
    this._markConnected(player);
    return { ok: true, playerId: player.id };
  }

  disconnect(id) {
    const p = this.players.get(id);
    if (!p) return NOT_NOW;
    if (!p.connected) return { ok: true };
    p.connected = false;
    if (this._connectedCount() === 0) this.emptySince = this.now();
    this._ensureHost();
    return { ok: true };
  }

  reconnect(token) {
    const p = this._byToken(token);
    if (!p) return this._err('Not now');
    this._markConnected(p);
    return { ok: true, playerId: p.id };
  }

  setAvatar(id, avatar) {
    const p = this.players.get(id);
    if (!p) return NOT_NOW;
    const v = validateAvatar(avatar);
    if (!v.ok) return this._err(v.error);
    p.avatar = v.avatar;
    return { ok: true };
  }

  chat(id, text) {
    const p = this.players.get(id);
    if (!p) return NOT_NOW;
    if (this.chatPaused) return this._err('Chat is paused — talk it out!');
    const clean = typeof text === 'string' ? text.trim() : '';
    if (clean.length < 1 || clean.length > MAX_CHAT) return this._err('Message must be 1-140 characters');
    const t = this.now();
    const last = this._lastChatAt.get(id);
    if (last !== undefined && t - last < CHAT_GAP_MS) return this._err('Slow down!');
    this._lastChatAt.set(id, t);
    this.chatLog.push({ from: id, name: p.name, text: clean, at: t });
    if (this.chatLog.length > CHAT_KEEP) this.chatLog.splice(0, this.chatLog.length - CHAT_KEEP);
    return { ok: true };
  }

  isHost(id) {
    return id === this.hostId && this.players.has(id);
  }

  getPhoto(id) {
    const p = this.players.get(id);
    return p && p.avatar.kind === 'photo' ? p.avatar.data : null;
  }

  // Extension points for later tasks: effects to broadcast, timer wake-up, timer tick.
  takeFx() {
    const out = this.fx;
    this.fx = [];
    return out;
  }

  nextWakeAt() {
    return null;
  }

  tick() {
    return false;
  }

  // Extension point: later tasks add lobby/game actions here.
  act(id, action) {
    if (!this.players.has(id) || !action || typeof action !== 'object') return NOT_NOW;
    switch (action.type) {
      case 'chat': return this.chat(id, action.text);
      case 'setAvatar': return this.setAvatar(id, action.avatar);
      default: return NOT_NOW;
    }
  }

  // Extension point: later tasks add lobby/game state to the view.
  viewFor(id) {
    const me = this.players.get(id);
    if (!me) return null;
    return {
      code: this.code,
      me: { id: me.id, name: me.name, isHost: this.isHost(id) },
      players: [...this.players.values()].map((p) => ({
        id: p.id,
        name: p.name,
        avatarKind: p.avatar.kind,
        connected: p.connected,
        isHost: this.isHost(p.id),
      })),
      chat: this.chatLog.map((m) => ({ ...m })),
    };
  }
}

module.exports = { Room, MAX_PLAYERS };
