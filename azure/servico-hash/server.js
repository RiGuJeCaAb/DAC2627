'use strict';
// APP DAC2627 · serviço de hash PBKDF2 para a revisão de pedidos (Azure App Service, Node.js, sem dependências).
//   POST /api/hash       {"password"}                              → {"algoritmo","iteracoes","salt","hash"}
//   POST /api/verificar  {"password","salt","hash","iteracoes"}    → {"valido": true|false}
//   GET  /api/estado                                                → {"estado":"ok"}  (sem chave, para a verificação de saúde)
// Autenticação: cabeçalho x-api-key igual à definição DAC_CHAVE_API da aplicação web (nunca no código nem no git).
// As respostas e os registos nunca contêm a password.
const http = require('node:http');
const crypto = require('node:crypto');
const pbkdf2 = require('./pbkdf2');

const CHAVE = process.env.DAC_CHAVE_API || '';
const PORTA = process.env.PORT || 8080;
const MAX_CORPO = 4096;

function responder(res, status, corpo) {
  const json = JSON.stringify(corpo);
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' });
  res.end(json);
}

function chaveValida(req) {
  const recebida = Buffer.from(String(req.headers['x-api-key'] || ''));
  const esperada = Buffer.from(CHAVE);
  if (!CHAVE || recebida.length !== esperada.length) return false;
  return crypto.timingSafeEqual(recebida, esperada);
}

function lerJson(req) {
  return new Promise((resolve) => {
    let dados = '';
    req.on('data', (parte) => {
      dados += parte;
      if (dados.length > MAX_CORPO) { req.destroy(); resolve(null); }
    });
    req.on('end', () => { try { resolve(JSON.parse(dados)); } catch { resolve(null); } });
    req.on('error', () => resolve(null));
  });
}

async function tratar(req, res) {
  const rota = (req.url || '').split('?')[0];
  if (req.method === 'GET' && rota === '/api/estado') return responder(res, 200, { estado: 'ok' });
  if (req.method !== 'POST' || !['/api/hash', '/api/verificar'].includes(rota)) return responder(res, 404, { erro: 'Rota inexistente.' });
  if (!chaveValida(req)) return responder(res, 401, { erro: 'Chave em falta ou inválida.' });
  const corpo = await lerJson(req);
  if (!corpo) return responder(res, 400, { erro: 'O corpo tem de ser JSON (até 4 KB).' });

  if (rota === '/api/hash') {
    const problema = pbkdf2.validarPassword(corpo.password);
    if (problema) return responder(res, 400, { erro: problema });
    const r = pbkdf2.gerar(corpo.password);
    console.log(`hash gerado (${r.algoritmo}, ${r.iteracoes} iterações)`);
    return responder(res, 200, r);
  }
  if (typeof corpo.password !== 'string') return responder(res, 400, { erro: 'Faltam a password, o salt, o hash ou as iterações.' });
  try {
    const valido = pbkdf2.verificar(corpo.password, corpo.salt, corpo.hash, corpo.iteracoes);
    console.log(`verificação: ${valido ? 'válida' : 'inválida'}`);
    return responder(res, 200, { valido });
  } catch (e) {
    return responder(res, 400, { erro: e.message });
  }
}

const servidor = http.createServer((req, res) => {
  tratar(req, res).catch(() => responder(res, 500, { erro: 'Erro interno.' }));
});
if (require.main === module) {
  if (!CHAVE) console.warn('Aviso: DAC_CHAVE_API não está definida, todas as chamadas a /api/hash e /api/verificar devolvem 401.');
  servidor.listen(PORTA, () => console.log(`servico-hash à escuta na porta ${PORTA}`));
}
module.exports = servidor;
