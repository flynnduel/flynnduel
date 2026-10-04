'use strict';
const { createAvatar } = require('@dicebear/core');
const { lorelei, notionists } = require('@dicebear/collection');

const STYLES = { lorelei, notionists };
const MAX_SEED = 32;
const MAX_PHOTO_BYTES = 40 * 1024;
const PHOTO_PREFIX = 'data:image/jpeg;base64,';
const BASE64_RE = /^[A-Za-z0-9+/]*={0,2}$/;
// Option families we let players customise: hair, eyes, mouth/lips, glasses, beard, brows, background.
const OPTION_FAMILY_RE = /^(hair|eyes|eyebrows|brows|mouth|lips|glasses|beard)/;
const SAFE_STRING_RE = /^[A-Za-z0-9#_-]{1,32}$/;

function allowedKeys(style) {
  const keys = Object.keys(style.schema.properties).filter((k) => OPTION_FAMILY_RE.test(k));
  keys.push('backgroundColor');
  return keys;
}

function cleanValue(v) {
  const scalar = (x) => (typeof x === 'string' ? SAFE_STRING_RE.test(x) : typeof x === 'number' ? Number.isFinite(x) : typeof x === 'boolean');
  if (Array.isArray(v)) return v.length <= 8 && v.every(scalar) ? v : undefined;
  return scalar(v) ? v : undefined;
}

function validateAvatar(a) {
  if (!a || typeof a !== 'object') return { ok: false, error: 'Bad avatar' };
  if (a.kind === 'dicebear') {
    if (!Object.hasOwn(STYLES, a.style)) return { ok: false, error: 'Bad avatar style' };
    if (typeof a.seed !== 'string' || a.seed.length < 1 || a.seed.length > MAX_SEED) return { ok: false, error: 'Bad avatar seed' };
    const allowed = allowedKeys(STYLES[a.style]);
    const options = {};
    const given = a.options && typeof a.options === 'object' && !Array.isArray(a.options) ? a.options : {};
    for (const key of allowed) {
      if (!Object.hasOwn(given, key)) continue;
      const v = cleanValue(given[key]);
      if (v !== undefined) options[key] = v;
    }
    return { ok: true, avatar: { kind: 'dicebear', style: a.style, seed: a.seed, options } };
  }
  if (a.kind === 'photo') {
    const d = a.data;
    if (typeof d !== 'string' || !d.startsWith(PHOTO_PREFIX)) return { ok: false, error: 'Photo must be a JPEG' };
    const b64 = d.slice(PHOTO_PREFIX.length);
    if (b64.length === 0 || b64.length > Math.ceil((MAX_PHOTO_BYTES * 4) / 3) + 4) return { ok: false, error: 'Photo is too big' };
    if (b64.length % 4 !== 0 || !BASE64_RE.test(b64)) return { ok: false, error: 'Bad photo data' };
    const pad = b64.endsWith('==') ? 2 : b64.endsWith('=') ? 1 : 0;
    if ((b64.length / 4) * 3 - pad > MAX_PHOTO_BYTES) return { ok: false, error: 'Photo is too big' };
    return { ok: true, avatar: { kind: 'photo', data: d } };
  }
  return { ok: false, error: 'Bad avatar' };
}

function renderDicebear(avatar) {
  const style = STYLES[avatar.style];
  return createAvatar(style, { ...(avatar.options || {}), seed: avatar.seed }).toString();
}

module.exports = { validateAvatar, renderDicebear };
