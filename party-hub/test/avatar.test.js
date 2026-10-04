const test = require('node:test');
const assert = require('node:assert/strict');
const { validateAvatar, renderDicebear } = require('../server/avatar');

const jpeg = (n) => 'data:image/jpeg;base64,' + Buffer.alloc(n, 1).toString('base64');

test('validateAvatar accepts dicebear and keeps whitelisted options only', () => {
  const r = validateAvatar({ kind: 'dicebear', style: 'lorelei', seed: 'abc', options: { hair: ['variant01'], evil: 'x', hairColor: ['ff0000'], backgroundColor: ['00ff00'] } });
  assert.equal(r.ok, true);
  assert.deepEqual(Object.keys(r.avatar.options).sort(), ['backgroundColor', 'hair', 'hairColor']);
  assert.equal(validateAvatar({ kind: 'dicebear', style: 'notionists', seed: 's' }).ok, true);
});

test('validateAvatar rejects bad dicebear', () => {
  assert.equal(validateAvatar({ kind: 'dicebear', style: 'bottts', seed: 'a' }).ok, false);
  assert.equal(validateAvatar({ kind: 'dicebear', style: 'lorelei', seed: 'x'.repeat(33) }).ok, false);
  assert.equal(validateAvatar({ kind: 'dicebear', style: 'lorelei', seed: 5 }).ok, false);
  assert.equal(validateAvatar(null).ok, false);
  assert.equal(validateAvatar({ kind: 'nope' }).ok, false);
});

test('validateAvatar accepts small jpeg photo, rejects png, oversize, junk', () => {
  const ok = validateAvatar({ kind: 'photo', data: jpeg(1000) });
  assert.equal(ok.ok, true);
  assert.equal(ok.avatar.kind, 'photo');
  assert.equal(validateAvatar({ kind: 'photo', data: jpeg(40 * 1024) }).ok, true);
  assert.equal(validateAvatar({ kind: 'photo', data: 'data:image/png;base64,AAAA' }).ok, false);
  assert.equal(validateAvatar({ kind: 'photo', data: jpeg(40 * 1024 + 1) }).ok, false);
  assert.equal(validateAvatar({ kind: 'photo', data: 'data:image/jpeg;base64,@@@' }).ok, false);
  assert.equal(validateAvatar({ kind: 'photo', data: 42 }).ok, false);
});

test('renderDicebear returns svg for both styles', () => {
  for (const style of ['lorelei', 'notionists']) {
    assert.match(renderDicebear({ kind: 'dicebear', style, seed: 'zed', options: {} }), /<svg/);
  }
});
