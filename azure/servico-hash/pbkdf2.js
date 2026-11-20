'use strict';
// PBKDF2-HMAC-SHA256, só com o módulo crypto do Node (sem dependências externas).
// 600 000 iterações: valor recomendado pela OWASP para PBKDF2-HMAC-SHA256 (Password Storage Cheat Sheet).
const crypto = require('node:crypto');

const ALGORITMO = 'PBKDF2-SHA256';
const ITERACOES = 600000;
const BYTES_SALT = 16;
const BYTES_HASH = 32;
const MIN_ITERACOES = 100000;
const MAX_ITERACOES = 2000000;

function validarPassword(password) {
  if (typeof password !== 'string') return 'A password tem de ser texto.';
  if (password.length < 8) return 'A password tem de ter pelo menos 8 caracteres.';
  if (password.length > 128) return 'A password não pode ter mais de 128 caracteres.';
  return null;
}

function gerar(password) {
  const salt = crypto.randomBytes(BYTES_SALT);
  const hash = crypto.pbkdf2Sync(password, salt, ITERACOES, BYTES_HASH, 'sha256');
  return { algoritmo: ALGORITMO, iteracoes: ITERACOES, salt: salt.toString('base64'), hash: hash.toString('base64') };
}

function verificar(password, saltB64, hashB64, iteracoes) {
  const it = Number(iteracoes);
  if (!Number.isInteger(it) || it < MIN_ITERACOES || it > MAX_ITERACOES) throw new Error('Número de iterações inválido.');
  const salt = Buffer.from(String(saltB64), 'base64');
  const esperado = Buffer.from(String(hashB64), 'base64');
  if (salt.length < 8 || esperado.length !== BYTES_HASH) throw new Error('Salt ou hash inválidos.');
  const calculado = crypto.pbkdf2Sync(password, salt, it, BYTES_HASH, 'sha256');
  // comparação em tempo constante, para o tempo de resposta não revelar quantos bytes coincidem
  return crypto.timingSafeEqual(calculado, esperado);
}

module.exports = { ALGORITMO, ITERACOES, validarPassword, gerar, verificar };
