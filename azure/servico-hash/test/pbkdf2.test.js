'use strict';
const test = require('node:test');
const assert = require('node:assert');
const crypto = require('node:crypto');
const p = require('../pbkdf2');

test('gera e verifica a mesma password', () => {
  const r = p.gerar('Ficha04-Teste!');
  assert.strictEqual(r.algoritmo, 'PBKDF2-SHA256');
  assert.strictEqual(r.iteracoes, 600000);
  assert.strictEqual(Buffer.from(r.salt, 'base64').length, 16);
  assert.ok(p.verificar('Ficha04-Teste!', r.salt, r.hash, r.iteracoes));
  assert.ok(!p.verificar('ficha04-teste!', r.salt, r.hash, r.iteracoes));
});

test('o mesmo texto com salts diferentes dá hashes diferentes', () => {
  assert.notStrictEqual(p.gerar('igual12345').hash, p.gerar('igual12345').hash);
});

test('vetor de referência do RFC 7914 (PBKDF2-HMAC-SHA256, 1 iteração)', () => {
  const dk = crypto.pbkdf2Sync('passwd', 'salt', 1, 64, 'sha256').toString('hex');
  assert.strictEqual(dk.slice(0, 32), '55ac046e56e3089fec1691c22544b605');
});

test('valida a password e os parâmetros', () => {
  assert.ok(p.validarPassword('curta'));
  assert.strictEqual(p.validarPassword('comprida1'), null);
  assert.throws(() => p.verificar('x', 'c2FsdHNhbHQ=', 'AAAA', 600000));
  assert.throws(() => p.verificar('x', 'c2FsdHNhbHQ=', Buffer.alloc(32).toString('base64'), 10));
});
