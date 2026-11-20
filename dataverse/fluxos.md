# Fluxos Power Automate da Ficha 04 · Melhoramento

Três fluxos de cloud na solução DAC2627, criados a 20/11/2026 por `dataverse/melhoramento_fluxos.js` (Web API, com o separador aberto na organização). As referências de ligação também são da solução: `dac_dac2627dataverse` (Microsoft Dataverse) e `dac_dac2627outlook` (Office 365 Outlook). A definição completa de cada fluxo fica em `solution/Workflows/` depois de `dac sincronizar`.

## DAC2627_Pedido_Classificar (automatizado)

- Gatilho: Dataverse *When a row is added, modified or deleted*, tabela Pedido, tipo de alteração **Added or Modified**, âmbito **Organization**, colunas vigiadas `dac_valor`. A lista de colunas só vale para as alterações, por isso a criação dispara sempre e uma edição só dispara quando o pedido traz o Valor.
- `Ja_processado_com_este_valor`: se Processado = Sim e ValorProcessado = Valor, termina sem fazer nada. É o teste de idempotência, porque o gatilho dispara mesmo quando o valor enviado é igual ao guardado (o formulário da Ficha 04 envia o Valor ao guardar).
- `Tentar` (âmbito): sem Valor, marca **Erro** com «Dados inválidos». Com Valor, compara `float(Valor)` com a variável de ambiente `dac_LimiteRevisao`: estritamente superior dá **Revisão** (e Decisao = Aguarda decisão), igual ou inferior dá **Automático**. Em todos os ramos escreve Processado = Sim, DataProcessamento = `utcNow()`, ObservacoesProcessamento, IdExecucao = `workflow()?['run']?['name']` e ValorProcessado.
- `Tratar_erro` (âmbito, corre depois de `Tentar` falhar ou expirar): marca **Erro** com «Falha técnica» e o identificador da execução, e termina a execução como falhada, para ficar visível no histórico.
- O fluxo escreve na própria linha que o disparou mas não volta a disparar, porque nunca escreve no Valor.

## DAC2627_Pedido_Reprocessar (instantâneo, chamado pela app)

- Gatilho: Power Apps (V2), entrada de texto `PedidoId` (o GUID do pedido).
- `Validar_e_ler` (âmbito): lê o pedido e repõe Tratamento = Por processar, Processado = Não, ValorProcessado e Decisao vazios, e volta a escrever o Valor que lá estava. É essa escrita que dispara o Classificar.
- Responde logo à app, com `resultado` ("ok" ou "erro") e `mensagem`, muito abaixo do limite de 120 s de uma chamada síncrona. Um GUID que não existe cai no ramo de erro.
- Na app: `DAC2627_Pedido_Reprocessar.Run(Text(locL4cPedido.Pedido))`, no botão Reprocessar do `scrL4Melhoramento`.

## DAC2627_Pedido_Aprovar (automatizado, decisão humana)

- Gatilho: Dataverse, tipo **Modified**, âmbito Organization, coluna vigiada `dac_tratamento`, filtro de linhas `dac_tratamento eq 774300002` (Revisão).
- Lê quem criou o pedido (`systemusers`) e envia ao aprovador (variável `dac_AprovadorEmail`) um email com as opções **Aprovar** e **Rejeitar** (Office 365 Outlook, *Send email with options*). A execução fica à espera da resposta, no máximo 30 dias.
- Grava Decisao, DataDecisao e ComentarioDecisao no pedido e notifica quem o criou por email.
- **Porque não o conector Aprovações.** A ativação com a ação *Start and wait for an approval* foi recusada a 20/11/2026: a política de dados do tenant «Advanced Connector Policy» bloqueia o conector `shared_approvals` (`ApiPolicyApiGroupViolation`, tipo `BlockedConnector`). O email com opções faz o mesmo papel e passa na política.
- Um pedido que volte a Revisão (Valor alterado ou Reprocessar) recebe um pedido de decisão novo. Um pedido de decisão anterior ainda por responder fica sem efeito prático, porque a resposta grava sobre a decisão do pedido.

## Testes de 20/11/2026

| Pedido | Valor | Resultado |
|---|---|---|
| PED-1179 | 100 | Automático, «o valor 100 não é superior ao limite de 500» |
| PED-1180 | 500 | Automático (fronteira: a condição é estritamente superior) |
| PED-1181 | 750 | Revisão, Decisao = Aguarda decisão, email de decisão enviado |
| PED-1182 | sem valor (Web API) | Erro, «Dados inválidos: o pedido não tem valor» |
| PED-1179 | 100 outra vez (PATCH) | execução de 0,5 s que termina em `Terminar_nada_a_fazer`, sem mexer no pedido |
