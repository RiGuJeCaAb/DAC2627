'use strict';
// Gera localmente o hash e o salt de uma password, para criar o primeiro Admin à mão na tabela Utilizador
// (antes de haver um Admin não há quem chame o fluxo DefinirPassword). A password é lida do teclado, sem eco,
// para não ficar no histórico do terminal. Uso: node gerar_hash.js
const readline = require('node:readline');
const pbkdf2 = require('./pbkdf2');

const rl = readline.createInterface({ input: process.stdin, output: process.stdout, terminal: true });
rl._writeToOutput = (s) => { if (s.includes('Password')) process.stdout.write(s); };
rl.question('Password (8 a 128 caracteres): ', (password) => {
  rl.close();
  process.stdout.write('\n');
  const problema = pbkdf2.validarPassword(password);
  if (problema) { console.error(problema); process.exit(1); }
  const r = pbkdf2.gerar(password);
  console.log(`Algoritmo:  ${r.algoritmo}\nIterações:  ${r.iteracoes}\nSalt:       ${r.salt}\nHash:       ${r.hash}`);
});
