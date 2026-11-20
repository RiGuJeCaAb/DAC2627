// Ficha 04 · Melhoramento — cria na solução DAC2627 as referências de ligação e os três fluxos.
// Correr num separador aberto em https://org0f43a370.crm4.dynamics.com (sessão do utilizador).
const API = '/api/data/v9.2/';
const H = { 'Content-Type': 'application/json; charset=utf-8', 'OData-MaxVersion': '4.0', 'OData-Version': '4.0', Accept: 'application/json', 'MSCRM.SolutionUniqueName': 'DAC2627', Prefer: 'return=representation' };
const log = [];
const get = (u) => fetch(API + u, { headers: { Accept: 'application/json' } }).then((r) => r.json());
async function post(p, b) {
  const r = await fetch(API + p, { method: 'POST', headers: H, body: JSON.stringify(b) });
  const t = await r.text();
  if (!r.ok) throw new Error(p + ' ' + r.status + ' ' + t.slice(0, 500));
  return JSON.parse(t);
}

// 1 · Referências de ligação (apontam para ligações já existentes do utilizador)
const REFS = {
  dv: { nome: 'dac_DAC2627Dataverse', mostra: 'DAC2627 · Dataverse', api: 'shared_commondataserviceforapps', ligacao: 'shared-commondataser-b4a77cc8-a523-4f0f-9049-c8a3ef85ac81' },
  ol: { nome: 'dac_DAC2627Outlook', mostra: 'DAC2627 · Office 365 Outlook', api: 'shared_office365', ligacao: 'shared-office365-68f89ed7-5d2d-4894-9b08-189a454f66d2' },
};
for (const r of Object.values(REFS)) {
  const ex = await get(`connectionreferences?$select=connectionreferenceid&$filter=connectionreferencelogicalname eq '${r.nome.toLowerCase()}'`);
  if (ex.value.length) { log.push('ref existe ' + r.nome); continue; }
  await post('connectionreferences', { connectionreferencelogicalname: r.nome.toLowerCase(), connectionreferencedisplayname: r.mostra, connectorid: '/providers/Microsoft.PowerApps/apis/' + r.api, connectionid: r.ligacao });
  log.push('ref criada ' + r.nome);
}
const ref = (k) => ({ [REFS[k].api]: { runtimeSource: 'embedded', connection: { connectionReferenceLogicalName: REFS[k].nome.toLowerCase() }, api: { name: REFS[k].api } } });

// Peças comuns
const AUTH = "@parameters('$authentication')";
const host = (k, op) => ({ connectionName: REFS[k].api, operationId: op, apiId: '/providers/Microsoft.PowerApps/apis/' + REFS[k].api });
const T = 774300000; // prefixo das opções do editor DAC CC MB
const TR = { porProcessar: T, automatico: T + 1, revisao: T + 2, erro: T + 3 };
const DEC = { aguarda: T, aprovado: T + 1, rejeitado: T + 2 };
const LIMITE = 'Limite de revisão dos pedidos (dac_LimiteRevisao)';
const APROVADOR = 'Email do aprovador dos pedidos (dac_AprovadorEmail)';
const baseParams = { $connections: { defaultValue: {}, type: 'Object' }, $authentication: { defaultValue: {}, type: 'SecureObject' } };
const RUN = "@{workflow()?['run']?['name']}";
const atualizar = (idExpr, campos, runAfter = {}) => ({
  runAfter, type: 'OpenApiConnection',
  inputs: { host: host('dv', 'UpdateOnlyRecord'), parameters: { entityName: 'dac_pedidos', recordId: idExpr, ...Object.fromEntries(Object.entries(campos).map(([k, v]) => ['item/' + k, v])) }, authentication: AUTH },
});
const def = (params, triggers, actions) => ({ $schema: 'https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#', contentVersion: '1.0.0.0', parameters: { ...baseParams, ...params }, triggers, actions });

// 2 · Fluxo automatizado: classificar o pedido
const ID = "@triggerOutputs()?['body/dac_pedidoid']";
const VALOR = "triggerOutputs()?['body/dac_valor']";
const classificar = def(
  { [LIMITE]: { defaultValue: 500, type: 'Float', metadata: { schemaName: 'dac_LimiteRevisao', description: 'Valor acima do qual o pedido vai para Revisão' } } },
  {
    Quando_um_pedido_e_criado_ou_o_valor_muda: {
      type: 'OpenApiConnectionWebhook',
      inputs: { host: host('dv', 'SubscribeWebhookTrigger'), parameters: { 'subscriptionRequest/message': 4, 'subscriptionRequest/entityname': 'dac_pedido', 'subscriptionRequest/scope': 4, 'subscriptionRequest/filteringattributes': 'dac_valor' }, authentication: AUTH },
    },
  },
  {
    Ja_processado_com_este_valor: {
      runAfter: {}, type: 'If',
      expression: { and: [{ equals: ["@triggerOutputs()?['body/dac_processado']", true] }, { equals: ["@triggerOutputs()?['body/dac_valorprocessado']", '@' + VALOR] }] },
      actions: { Terminar_nada_a_fazer: { runAfter: {}, type: 'Terminate', inputs: { runStatus: 'Succeeded' } } },
      else: { actions: {} },
    },
    Tentar: {
      runAfter: { Ja_processado_com_este_valor: ['Succeeded'] }, type: 'Scope',
      actions: {
        Valor_em_falta: {
          runAfter: {}, type: 'If',
          expression: { equals: ['@' + VALOR, null] },
          actions: {
            Marcar_dados_invalidos: atualizar(ID, {
              dac_tratamento: TR.erro, dac_processado: true, dac_dataprocessamento: '@utcNow()', dac_idexecucao: RUN,
              dac_observacoesprocessamento: 'Dados inválidos: o pedido não tem valor. Corrigir o Valor para o fluxo voltar a classificar.',
            }),
          },
          else: {
            actions: {
              Valor_acima_do_limite: {
                runAfter: {}, type: 'If',
                expression: { greater: ['@float(' + VALOR + ')', `@parameters('${LIMITE}')`] },
                actions: {
                  Marcar_revisao: atualizar(ID, {
                    dac_tratamento: TR.revisao, dac_processado: true, dac_dataprocessamento: '@utcNow()', dac_idexecucao: RUN,
                    dac_valorprocessado: '@' + VALOR, dac_decisao: DEC.aguarda,
                    dac_observacoesprocessamento: `Revisão: o valor @{${VALOR}} é superior ao limite de @{parameters('${LIMITE}')}. Aguarda decisão humana.`,
                  }),
                },
                else: {
                  actions: {
                    Marcar_automatico: atualizar(ID, {
                      dac_tratamento: TR.automatico, dac_processado: true, dac_dataprocessamento: '@utcNow()', dac_idexecucao: RUN,
                      dac_valorprocessado: '@' + VALOR,
                      dac_observacoesprocessamento: `Automático: o valor @{${VALOR}} não é superior ao limite de @{parameters('${LIMITE}')}.`,
                    }),
                  },
                },
              },
            },
          },
        },
      },
    },
    Tratar_erro: {
      runAfter: { Tentar: ['Failed', 'TimedOut'] }, type: 'Scope',
      actions: {
        Marcar_erro: atualizar(ID, {
          dac_tratamento: TR.erro, dac_processado: true, dac_dataprocessamento: '@utcNow()', dac_idexecucao: RUN,
          dac_observacoesprocessamento: `Falha técnica no processamento (execução ${RUN}). Consultar o histórico do fluxo e usar Reprocessar.`,
        }),
        Terminar_com_falha: { runAfter: { Marcar_erro: ['Succeeded', 'Failed'] }, type: 'Terminate', inputs: { runStatus: 'Failed', runError: { code: 'ProcessamentoFalhou', message: 'O bloco Tentar falhou. O pedido ficou com Tratamento = Erro.' } } },
      },
    },
  },
);

// 3 · Fluxo instantâneo: reprocessar a partir da Canvas app (gatilho Power Apps V2)
const PID = "@triggerBody()['text']";
const responder = (res, msg, runAfter) => ({
  runAfter, type: 'Response', kind: 'PowerApp',
  inputs: { statusCode: 200, body: { resultado: res, mensagem: msg }, schema: { type: 'object', properties: { resultado: { title: 'resultado', type: 'string', 'x-ms-dynamically-added': true }, mensagem: { title: 'mensagem', type: 'string', 'x-ms-dynamically-added': true } } } },
});
const reprocessar = def({},
  {
    manual: {
      type: 'Request', kind: 'PowerAppV2',
      inputs: { schema: { type: 'object', properties: { text: { title: 'PedidoId', type: 'string', description: 'GUID do pedido a reprocessar', 'x-ms-content-hint': 'TEXT', 'x-ms-dynamically-added': true } }, required: ['text'] } },
    },
  },
  {
    Validar_e_ler: {
      runAfter: {}, type: 'Scope',
      actions: {
        Ler_pedido: { runAfter: {}, type: 'OpenApiConnection', inputs: { host: host('dv', 'GetItem'), parameters: { entityName: 'dac_pedidos', recordId: PID, $select: 'dac_pedidoid,dac_valor,dac_numeropedido' }, authentication: AUTH } },
        Repor_e_voltar_a_disparar: atualizar("@outputs('Ler_pedido')?['body/dac_pedidoid']", {
          dac_tratamento: TR.porProcessar, dac_processado: false, dac_valorprocessado: null, dac_decisao: null,
          dac_observacoesprocessamento: `Reprocessamento pedido na app (execução ${RUN}).`,
          dac_valor: "@outputs('Ler_pedido')?['body/dac_valor']",
        }, { Ler_pedido: ['Succeeded'] }),
      },
    },
    Responder_ok: responder('ok', "Pedido @{outputs('Ler_pedido')?['body/dac_numeropedido']} enviado para reprocessamento.", { Validar_e_ler: ['Succeeded'] }),
    Responder_erro: responder('erro', 'O pedido indicado não existe ou não pôde ser atualizado.', { Validar_e_ler: ['Failed', 'TimedOut', 'Skipped'] }),
  },
);

// 4 · Fluxo automatizado: aprovação humana dos pedidos em Revisão
const AID = "@triggerOutputs()?['body/dac_pedidoid']";
const decidir = (valor, rotulo) => atualizar(AID, {
  dac_decisao: valor, dac_datadecisao: '@utcNow()',
  dac_comentariodecisao: `${rotulo} por email por @{parameters('${APROVADOR}')}.`,
});
const aprovar = def(
  { [APROVADOR]: { defaultValue: '', type: 'String', metadata: { schemaName: 'dac_AprovadorEmail', description: 'Quem aprova os pedidos em Revisão' } } },
  {
    Quando_um_pedido_passa_a_revisao: {
      type: 'OpenApiConnectionWebhook',
      inputs: { host: host('dv', 'SubscribeWebhookTrigger'), parameters: { 'subscriptionRequest/message': 3, 'subscriptionRequest/entityname': 'dac_pedido', 'subscriptionRequest/scope': 4, 'subscriptionRequest/filteringattributes': 'dac_tratamento', 'subscriptionRequest/filterexpression': `dac_tratamento eq ${TR.revisao}` }, authentication: AUTH },
    },
  },
  {
    Ler_requerente: { runAfter: {}, type: 'OpenApiConnection', inputs: { host: host('dv', 'GetItem'), parameters: { entityName: 'systemusers', recordId: "@triggerOutputs()?['body/_createdby_value']", $select: 'internalemailaddress,fullname' }, authentication: AUTH } },
    // O conector Aprovações (shared_approvals) está bloqueado pela política de dados do tenant
    // («Advanced Connector Policy», BlockedConnector): a decisão é um email com opções do Office 365 Outlook.
    Pedir_aprovacao: {
      runAfter: { Ler_requerente: ['Succeeded'] }, type: 'OpenApiConnectionWebhook',
      inputs: {
        host: host('ol', 'SendMailWithOptions'),
        parameters: {
          'optionsEmailSubscription/Message/To': `@parameters('${APROVADOR}')`,
          'optionsEmailSubscription/Message/Subject': "Aprovação: pedido @{triggerOutputs()?['body/dac_numeropedido']} em revisão (@{triggerOutputs()?['body/dac_valor']} €)",
          'optionsEmailSubscription/Message/Options': 'Aprovar, Rejeitar',
          'optionsEmailSubscription/Message/HeaderText': 'Ficha 04 · Melhoramento · decisão sobre um pedido em Revisão',
          'optionsEmailSubscription/Message/SelectionText': 'Escolha uma opção',
          'optionsEmailSubscription/Message/Body': "Pedido: @{triggerOutputs()?['body/dac_numeropedido']}\nValor: @{triggerOutputs()?['body/dac_valor']} €\nDescrição: @{triggerOutputs()?['body/dac_descricao']}\nMotivo: @{triggerOutputs()?['body/dac_observacoesprocessamento']}",
          'optionsEmailSubscription/Message/Importance': 'Normal',
          'optionsEmailSubscription/Message/UseOnlyHTMLMessage': false,
          'optionsEmailSubscription/Message/HideHTMLMessage': false,
          'optionsEmailSubscription/Message/ShowHTMLConfirmationDialog': false,
        },
        authentication: AUTH,
      },
    },
    Aprovado: {
      runAfter: { Pedir_aprovacao: ['Succeeded'] }, type: 'If',
      expression: { equals: ["@outputs('Pedir_aprovacao')?['body/SelectedOption']", 'Aprovar'] },
      actions: { Gravar_aprovado: decidir(DEC.aprovado, 'Aprovado') },
      else: { actions: { Gravar_rejeitado: decidir(DEC.rejeitado, 'Rejeitado') } },
    },
    Notificar_requerente: {
      runAfter: { Aprovado: ['Succeeded'] }, type: 'OpenApiConnection',
      inputs: {
        host: host('ol', 'SendEmailV2'),
        parameters: {
          'emailMessage/To': "@outputs('Ler_requerente')?['body/internalemailaddress']",
          'emailMessage/Subject': "Pedido @{triggerOutputs()?['body/dac_numeropedido']}: @{if(equals(outputs('Pedir_aprovacao')?['body/SelectedOption'],'Aprovar'),'aprovado','rejeitado')}",
          'emailMessage/Body': "<p>O pedido <b>@{triggerOutputs()?['body/dac_numeropedido']}</b> foi @{if(equals(outputs('Pedir_aprovacao')?['body/SelectedOption'],'Aprovar'),'aprovado','rejeitado')}.</p><p>Pode consultar o estado na APP DAC2627, Ficha 04 · Melhoramento.</p>",
        },
        authentication: AUTH,
      },
    },
  },
);

// 5 · Criar (ou atualizar) os fluxos
const FLUXOS = [
  { nome: 'DAC2627_Pedido_Classificar', desc: 'Ficha 04 · Melhoramento. Classifica o pedido quando é criado ou quando o Valor muda: Automático até ao limite, Revisão acima dele, Erro se faltar o valor ou se o processamento falhar.', refs: { ...ref('dv') }, def: classificar },
  { nome: 'DAC2627_Pedido_Reprocessar', desc: 'Ficha 04 · Melhoramento. Chamado pela Canvas app (Power Apps V2): repõe o pedido em Por processar e volta a escrever o Valor para disparar o fluxo Classificar.', refs: { ...ref('dv') }, def: reprocessar },
  { nome: 'DAC2627_Pedido_Aprovar', desc: 'Ficha 04 · Melhoramento. Quando um pedido passa a Revisão, envia ao aprovador um email com as opções Aprovar e Rejeitar, grava a decisão no pedido e notifica quem o criou.', refs: { ...ref('dv'), ...ref('ol') }, def: aprovar },
];
const ids = {};
for (const f of FLUXOS) {
  const clientdata = JSON.stringify({ properties: { connectionReferences: f.refs, definition: f.def, templateName: null }, schemaVersion: '1.0.0.0' });
  const ex = await get('workflows?$select=workflowid,statecode&$filter=' + encodeURIComponent(`category eq 5 and name eq '${f.nome}'`));
  if (ex.value.length) {
    const id = ex.value[0].workflowid;
    if (ex.value[0].statecode === 1) await fetch(API + `workflows(${id})`, { method: 'PATCH', headers: H, body: JSON.stringify({ statecode: 0, statuscode: 1 }) });
    const r = await fetch(API + `workflows(${id})`, { method: 'PATCH', headers: H, body: JSON.stringify({ clientdata, description: f.desc }) });
    log.push('fluxo atualizado ' + f.nome + ' ' + r.status); ids[f.nome] = id;
  } else {
    const w = await post('workflows', { name: f.nome, description: f.desc, category: 5, type: 1, primaryentity: 'none', clientdata });
    log.push('fluxo criado ' + f.nome); ids[f.nome] = w.workflowid;
  }
}
// 6 · Ativar
for (const [nome, id] of Object.entries(ids)) {
  const r = await fetch(API + `workflows(${id})`, { method: 'PATCH', headers: H, body: JSON.stringify({ statecode: 1, statuscode: 2 }) });
  log.push('ativar ' + nome + ' ' + r.status + (r.ok ? '' : ' ' + (await r.text()).slice(0, 400)));
}
({ log, ids });
