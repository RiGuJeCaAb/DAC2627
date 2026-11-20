# Serviço de hash da APP DAC2627 (Ficha 04 · Revisão)

Aplicação Node.js sem dependências que calcula e verifica hashes de passwords com **PBKDF2-HMAC-SHA256**, 600 000 iterações (o valor da OWASP para este algoritmo) e um salt aleatório de 16 bytes por password. A comparação é feita em tempo constante (`crypto.timingSafeEqual`), para o tempo de resposta não revelar quantos bytes coincidem.

| Rota | Corpo | Resposta |
|---|---|---|
| `POST /api/hash` | `{"password"}` | `{"algoritmo", "iteracoes", "salt", "hash"}` |
| `POST /api/verificar` | `{"password", "salt", "hash", "iteracoes"}` | `{"valido": true \| false}` |
| `GET /api/estado` | — | `{"estado": "ok"}`, sem chave |

As duas primeiras exigem o cabeçalho `x-api-key` igual à definição `DAC_CHAVE_API` da aplicação web. A chave não está no código nem no repositório: foi gerada na Cloud Shell (`openssl rand -hex 32`) e está só na definição da aplicação web e na ligação do conector personalizado `DAC2627-ServicoHash`. As respostas e os registos nunca contêm a password.

## Onde está

Azure App Service `dac2627-hash-2060`, grupo de recursos `rg-dac2627`, plano `plan-dac2627` (Linux, **F1 gratuito**), região `spaincentral`, Node 22, só HTTPS, TLS 1.2 no mínimo, FTP desligado.

**Porque não uma Azure Function.** A subscrição «Azure para Estudantes Iniciante» só autoriza alguns fornecedores de recursos (`Microsoft.Web` sim, `Microsoft.Storage` não), e qualquer Function App precisa de uma conta de armazenamento. A política da subscrição também limita as regiões a `spaincentral`, `swedencentral`, `norwayeast`, `germanywestcentral` e `francecentral`. O App Service é PaaS (a plataforma corre a aplicação web), a Function seria FaaS (a plataforma corre a função a pedido). Para este serviço o resultado é o mesmo. O F1 tem 60 minutos de CPU por dia e adormece sem uso: a primeira chamada depois de uma pausa demora alguns segundos.

## Publicar (Cloud Shell, Bash)

```bash
RG=rg-dac2627; LOC=spaincentral; APP=dac2627-hash-$RANDOM
az provider register -n Microsoft.Web --wait
az group create -n $RG -l $LOC -o none
az appservice plan create -g $RG -n plan-dac2627 --sku F1 --is-linux -l $LOC -o none
az webapp create -g $RG -p plan-dac2627 -n $APP --runtime "NODE:22-lts" -o none
az webapp update -g $RG -n $APP --https-only true -o none
az webapp config set -g $RG -n $APP --ftps-state Disabled --min-tls-version 1.2 -o none
az webapp config appsettings set -g $RG -n $APP --settings DAC_CHAVE_API=$(openssl rand -hex 32) -o none
git clone --depth 1 https://github.com/RiGuJeCaAb/DAC2627.git && cd DAC2627/azure/servico-hash
zip -q ~/s.zip package.json server.js pbkdf2.js
az webapp deploy -g $RG -n $APP --src-path ~/s.zip --type zip
curl -s https://$APP.azurewebsites.net/api/estado
```

## Testes

```bash
npm test          # 8 testes: vetor do RFC 7914, salts diferentes, validações, 401 sem chave, ponta a ponta
node gerar_hash.js   # hash e salt de uma password, lida sem eco, para criar o primeiro Admin à mão
```
