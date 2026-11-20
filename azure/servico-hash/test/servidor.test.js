'use strict';
const test = require('node:test');
const assert = require('node:assert');
process.env.DAC_CHAVE_API = 'chave-de-teste-local';
const servidor = require('../server');

let base;
test.before(() => new Promise((r) => servidor.listen(0, () => { base = `http://127.0.0.1:${servidor.address().port}`; r(); })));
test.after(() => servidor.close());

const post = (rota, corpo, chave = 'chave-de-teste-local') =>
  fetch(base + rota, { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-api-key': chave }, body: JSON.stringify(corpo) });

test('estado responde sem chave', async () => {
  const r = await fetch(base + '/api/estado');
  assert.strictEqual(r.status, 200);
});

test('sem chave ou com chave errada devolve 401', async () => {
  assert.strictEqual((await post('/api/hash', { password: 'abcdefgh1' }, '')).status, 401);
  assert.strictEqual((await post('/api/hash', { password: 'abcdefgh1' }, 'errada')).status, 401);
});

test('hash e verificação de ponta a ponta', async () => {
  const h = await (await post('/api/hash', { password: 'Revisao-2026' })).json();
  assert.strictEqual(h.iteracoes, 600000);
  assert.ok(!JSON.stringify(h).includes('Revisao-2026'));
  const ok = await (await post('/api/verificar', { password: 'Revisao-2026', salt: h.salt, hash: h.hash, iteracoes: h.iteracoes })).json();
  const ko = await (await post('/api/verificar', { password: 'revisao-2026', salt: h.salt, hash: h.hash, iteracoes: h.iteracoes })).json();
  assert.deepStrictEqual([ok.valido, ko.valido], [true, false]);
});

test('password curta e corpo inválido devolvem 400', async () => {
  assert.strictEqual((await post('/api/hash', { password: 'curta' })).status, 400);
  const r = await fetch(base + '/api/hash', { method: 'POST', headers: { 'x-api-key': 'chave-de-teste-local' }, body: 'não é json' });
  assert.strictEqual(r.status, 400);
});
