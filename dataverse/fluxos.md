# Fluxos Power Automate da Ficha 04 · Melhoramento

Três fluxos de cloud na solução DAC2627 (o terceiro passou a `DAC2627_Pedido_Notificar` na v1.6.0), criados a 20/11/2026 por `dataverse/melhoramento_fluxos.js` (Web API, com o separador aberto na organização). As referências de ligação também são da solução: `dac_dac2627dataverse` (Microsoft Dataverse) e `dac_dac2627outlook` (Office 365 Outlook). A definição completa de cada fluxo fica em `solution/Workflows/` depois de `dac sincronizar`.

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

## DAC2627_Pedido_Notificar (automatizado, desde a v1.6.0)

Até à v1.5.0 chamava-se `DAC2627_Pedido_Aprovar` e pedia a decisão por email com os botões Aprovar e Rejeitar (Office 365 Outlook, *Send email with options*), porque a política de dados do tenant («Advanced Connector Policy») bloqueia o conector Aprovações (`shared_approvals`, `BlockedConnector`). Na v1.6.0 o mesmo fluxo (o mesmo identificador) passou a só avisar, e a decisão faz-se na app, com perfis.

- Gatilho: Dataverse, tipo **Modified**, âmbito Organization, coluna vigiada `dac_decisao`, filtro de linhas `dac_tratamento eq 774300002` (Revisão).
- `Conforme_a_decisao` (Switch): **Aguarda decisão** avisa os Gestores ativos, **Proposta: aprovar** e **Proposta: rejeitar** avisam os Admins ativos, e a decisão final (**Aprovado** ou **Rejeitado**) avisa quem registou o pedido (Registado por) ou, se o pedido não veio do ecrã de revisão, quem o criou.
- Os destinatários vêm da tabela Utilizador (perfil e Ativo). Cada email leva a ligação à app, lida da variável de ambiente `dac_LigacaoApp`.
- O Reprocessar repõe o pedido em Por processar e apaga a Decisão: com Tratamento diferente de Revisão o filtro não deixa o fluxo correr. Quando o Classificar volta a pôr o pedido em Revisão, os Gestores recebem um aviso novo.

# Fluxos da Ficha 04 · Revisão (v1.6.0)

Criados a 20/11/2026 por `dataverse/revisao_fluxos.js`. Os três primeiros têm o gatilho Power Apps (V2) e respondem à app com o mesmo esquema: `resultado` ("ok" ou "erro"), `mensagem`, `token`, `nome`, `perfil`, `utilizadorid` e `clienteid`. O gatilho e as ações que tocam em passwords, hashes ou testemunhos têm as entradas e saídas protegidas (*secure inputs/outputs*), e o histórico de execuções mostra-as ocultas.

O serviço de hash é chamado pelo conector personalizado **DAC2627-ServicoHash** (`connector/servico_hash.swagger.json`, operações `GerarHash` e `VerificarPassword`), com a referência de ligação `dac_DAC2627ServicoHash`. A chave do serviço está na ligação, nunca no fluxo nem na solução.

## DAC2627_Utilizador_Entrar

- Entradas: `Email` e `Password`.
- Procura o utilizador pelo email. Se não existir, estiver inativo ou não tiver password, responde «Email ou password incorretos.»: a mesma mensagem da password errada, para não revelar que emails existem.
- Se `Bloqueado até` ainda não passou, responde que a conta está bloqueada.
- `Verificar` chama `VerificarPassword` com a password, o salt, o hash e as iterações. Certa: zera as tentativas, grava o último acesso, gera o testemunho (`replace(concat(guid(),guid()),'-','')`, 64 carateres) com validade de 8 horas e devolve-o com o nome, o perfil, o identificador do utilizador e o do cliente. Errada: soma uma tentativa, e à quinta bloqueia 15 minutos.
- O testemunho é gerado na própria atualização (protegida) e lido da resposta dela, porque uma ação Compose não aceita a proteção dos dados.

## DAC2627_Utilizador_DefinirPassword

- Entradas: `Token`, `UtilizadorId` (vazio = o próprio), `NovaPassword` e `PasswordAtual`.
- Lê a sessão pelo testemunho (válido, não expirado, utilizador ativo). O próprio tem de enviar a password atual, que é verificada no serviço. Para outro utilizador, só um Admin.
- `GerarHash` devolve o hash e um salt novo, gravados com as iterações e o algoritmo. As tentativas falhadas e o bloqueio são repostos. Quando é um Admin a definir a password de outro, as sessões abertas desse utilizador deixam de valer.

## DAC2627_Pedido_Decidir

- Entradas: `Token`, `PedidoId`, `Acao` (`propor_aprovar`, `propor_rejeitar`, `aprovar`, `rejeitar`) e `Comentario`.
- `Validar` (Switch) recusa, por esta ordem: o perfil Cliente, um pedido que não está em Revisão, um pedido com decisão final, uma ação desconhecida, uma proposta feita por quem não é Gestor, uma decisão final tomada por quem não é Admin e uma rejeição sem justificação.
- Proposta: grava a Decisão «Proposta: …», Proposta por, Comentário da proposta e Data da proposta. Decisão final: grava Aprovado ou Rejeitado, Decidido por, ComentarioDecisao (com o nome do Admin) e DataDecisao.
- O perfil vem da sessão no Dataverse. A app só mostra os botões certos a cada perfil, mas não é ela que decide quem pode, porque o que vem da app pode ser forjado.

## Testes de 20/11/2026

| Pedido | Valor | Resultado |
|---|---|---|
| PED-1179 | 100 | Automático, «o valor 100 não é superior ao limite de 500» |
| PED-1180 | 500 | Automático (fronteira: a condição é estritamente superior) |
| PED-1181 | 750 | Revisão, Decisao = Aguarda decisão, email de decisão enviado |
| PED-1182 | sem valor (Web API) | Erro, «Dados inválidos: o pedido não tem valor» |
| PED-1179 | 100 outra vez (PATCH) | execução de 0,5 s que termina em `Terminar_nada_a_fazer`, sem mexer no pedido |
| PED-1183 | 900, registado em nome do Cliente Demo (Web API) | Revisão, Aguarda decisão. O Notificar caiu no ramo Aguarda e enviou o aviso ao Gestor Demo |
