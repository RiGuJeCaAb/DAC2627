// Ficha 04 · Revisão (v1.6.0) — cria na solução DAC2627 a referência de ligação ao serviço de hash, a variável de ambiente
// com a ligação à app e os fluxos Entrar, DefinirPassword, Decidir e Notificar (este último substitui o DAC2627_Pedido_Aprovar).
// Correr num separador aberto em https://org0f43a370.crm4.dynamics.com. Antes: criar a ligação ao conector DAC2627-ServicoHash
// (com a chave) e pôr o nome dela em LIGACAO_HASH. Idempotente: atualiza o que já existe.
const LIGACAO_HASH = '0e7166e38df8420292b6917dc771161c'; // nome da ligação ao conector DAC2627-ServicoHash (make.powerautomate.com › Ligações)
const API = '/api/data/v9.2/';
const H = { 'Content-Type': 'application/json; charset=utf-8', 'OData-MaxVersion': '4.0', 'OData-Version': '4.0', Accept: 'application/json', 'MSCRM.SolutionUniqueName': 'DAC2627', Prefer: 'return=representation' };
const log = [];
const get = (u) => fetch(API + u, { headers: { Accept: 'application/json' } }).then((r) => r.json());
async function post(p, b) {
  const r = await fetch(API + p, { method: 'POST', headers: H, body: JSON.stringify(b) });
  const t = await r.text();
  if (!r.ok) throw new Error(p + ' ' + r.status + ' ' + t.slice(0, 500));
  return t ? JSON.parse(t) : {};
}

// 1 · Referências de ligação
const HASH_API = 'shared_dac-5fdac2627-2dservicohash-5f8e4ce826bfe060bc';
const REFS = {
  dv: { nome: 'dac_DAC2627Dataverse', api: 'shared_commondataserviceforapps' },
  ol: { nome: 'dac_DAC2627Outlook', api: 'shared_office365' },
  hs: { nome: 'dac_DAC2627ServicoHash', mostra: 'DAC2627 · Serviço de hash', api: HASH_API, ligacao: LIGACAO_HASH },
};
{
  const r = REFS.hs;
  const ex = await get(`connectionreferences?$select=connectionreferenceid&$filter=connectionreferencelogicalname eq '${r.nome.toLowerCase()}'`);
  if (ex.value.length) log.push('ref existe ' + r.nome);
  else {
    if (LIGACAO_HASH === 'PREENCHER') throw new Error('Falta o nome da ligação ao conector DAC2627-ServicoHash.');
    await post('connectionreferences', { connectionreferencelogicalname: r.nome.toLowerCase(), connectionreferencedisplayname: r.mostra, connectorid: '/providers/Microsoft.PowerApps/apis/' + r.api, connectionid: r.ligacao });
    log.push('ref criada ' + r.nome);
  }
}
const ref = (k) => ({ [REFS[k].api]: { runtimeSource: 'embedded', connection: { connectionReferenceLogicalName: REFS[k].nome.toLowerCase() }, api: { name: REFS[k].api } } });

// 2 · Variável de ambiente: ligação à app (usada nos emails). Muda de ambiente para ambiente, por isso não fica no fluxo.
const LIGACAO_APP = 'https://apps.powerapps.com/play/e/94d3a652-b3a8-e2dd-9b54-025090fe6659/a/4d44e8f5-1133-45cf-891b-4df1004409d6?tenantId=eddfb62c-28e3-470f-86ca-3c1ee2fae35c';
{
  const ex = await get("environmentvariabledefinitions?$select=environmentvariabledefinitionid&$filter=schemaname eq 'dac_LigacaoApp'");
  if (ex.value.length) log.push('variável existe dac_LigacaoApp');
  else {
    await post('environmentvariabledefinitions', { schemaname: 'dac_LigacaoApp', displayname: 'Ligação à APP DAC2627', description: 'Endereço de reprodução da Canvas app, usado nos emails de notificação dos pedidos', type: 100000000, defaultvalue: LIGACAO_APP });
    log.push('variável criada dac_LigacaoApp');
  }
}

// Peças comuns
const AUTH = "@parameters('$authentication')";
const host = (k, op) => ({ connectionName: REFS[k].api, operationId: op, apiId: '/providers/Microsoft.PowerApps/apis/' + REFS[k].api });
const T = 774300000;
const PERFIL = { admin: T, gestor: T + 1, cliente: T + 2 };
const TR_REVISAO = T + 2;
const DEC = { aguarda: T, aprovado: T + 1, rejeitado: T + 2, proporAprovar: T + 3, proporRejeitar: T + 4 };
const APP = 'Ligação à APP DAC2627 (dac_LigacaoApp)';
const baseParams = { $connections: { defaultValue: {}, type: 'Object' }, $authentication: { defaultValue: {}, type: 'SecureObject' } };
const def = (params, triggers, actions) => ({ $schema: 'https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#', contentVersion: '1.0.0.0', parameters: { ...baseParams, ...params }, triggers, actions });
const SEGURO = { secureData: { properties: ['inputs', 'outputs'] } }; // o histórico de execuções não mostra passwords, hashes nem testemunhos
const SEGURO_ENTRADAS = { secureData: { properties: ['inputs'] } };
const dv = (op, parameters, runAfter = {}, runtimeConfiguration) => ({ runAfter, type: 'OpenApiConnection', inputs: { host: host('dv', op), parameters, authentication: AUTH }, ...(runtimeConfiguration ? { runtimeConfiguration } : {}) });
const atualizarUtilizador = (idExpr, campos, runAfter = {}, seguro = false) => dv('UpdateOnlyRecord', { entityName: 'dac_utilizadors', recordId: idExpr, ...Object.fromEntries(Object.entries(campos).map(([k, v]) => ['item/' + k, v])) }, runAfter, seguro ? SEGURO_ENTRADAS : undefined);
const terminar = (runAfter) => ({ runAfter, type: 'Terminate', inputs: { runStatus: 'Succeeded' } });
const texto = (titulo, desc) => ({ title: titulo, type: 'string', description: desc, 'x-ms-content-hint': 'TEXT', 'x-ms-dynamically-added': true });
const gatilhoApp = (campos) => ({
  manual: {
    type: 'Request', kind: 'PowerAppV2', runtimeConfiguration: { secureData: { properties: ['outputs'] } },
    inputs: { schema: { type: 'object', properties: Object.fromEntries(campos.map(([t, d], i) => [i ? 'text_' + i : 'text', texto(t, d)])), required: campos.map((_, i) => (i ? 'text_' + i : 'text')) } },
  },
});
const ENTRADA = (i) => `triggerBody()?['${i ? 'text_' + i : 'text'}']`;
const aspas = (expr) => `replace(${expr},'''','''''')`; // escapar ' dentro de um filtro OData

// Resposta à app: o mesmo esquema em todas as respostas do fluxo, para a app ver sempre os mesmos campos
const CAMPOS = ['resultado', 'mensagem', 'token', 'nome', 'perfil', 'utilizadorid', 'clienteid'];
const responder = (valores, runAfter, seguro = false) => ({
  runAfter, type: 'Response', kind: 'PowerApp', ...(seguro ? { runtimeConfiguration: SEGURO_ENTRADAS } : {}),
  inputs: {
    statusCode: 200,
    body: Object.fromEntries(CAMPOS.map((c) => [c, valores[c] ?? ''])),
    schema: { type: 'object', properties: Object.fromEntries(CAMPOS.map((c) => [c, { title: c, type: 'string', 'x-ms-dynamically-added': true }])) },
  },
});
// os nomes das ações têm de ser únicos no fluxo inteiro, por isso cada recusa leva o nome do ramo
const recusar = (msg, ramo) => ({ actions: { [`Responder_${ramo}`]: responder({ resultado: 'erro', mensagem: msg }, {}), [`Terminar_${ramo}`]: terminar({ [`Responder_${ramo}`]: ['Succeeded'] }) } });

// Sessão: o testemunho devolvido pelo fluxo Entrar identifica quem chama. Os fluxos que alteram dados
// leem o perfil daqui, nunca do que a app diz, porque o que vem da app pode ser forjado.
const SESSAO = "first(outputs('Ler_sessao')?['body/value'])";
const lerSessao = (iToken) => dv('ListRecords', {
  entityName: 'dac_utilizadors', $top: 1,
  $select: 'dac_utilizadorid,dac_nome,dac_email,dac_perfil,dac_passwordhash,dac_passwordsalt,dac_iteracoes',
  $filter: `dac_sessaotoken eq '@{${aspas(ENTRADA(iToken))}}' and dac_sessaoexpira gt @{utcNow()} and dac_ativo eq true`,
}, {}, SEGURO);
const semSessao = {
  runAfter: { Ler_sessao: ['Succeeded'] }, type: 'If',
  expression: { equals: ["@length(outputs('Ler_sessao')?['body/value'])", 0] },
  ...recusar('Sessão inválida ou expirada. Entrar de novo.', 'sem_sessao'), else: { actions: {} },
};
const erroTecnico = (msg) => ({ Tratar_erro: { runAfter: { Tentar: ['Failed', 'TimedOut'] }, type: 'Scope', actions: { Responder_erro: responder({ resultado: 'erro', mensagem: msg }, {}) } } });

// 3 · Fluxo Entrar
const U = "first(outputs('Procurar')?['body/value'])";
const INVALIDO = 'Email ou password incorretos.'; // a mesma mensagem para email inexistente e password errada
const entrar = def({}, gatilhoApp([['Email', 'Email do utilizador'], ['Password', 'Password (não fica guardada nem no histórico)']]), {
  Tentar: {
    runAfter: {}, type: 'Scope',
    actions: {
      Procurar: dv('ListRecords', {
        entityName: 'dac_utilizadors', $top: 1,
        $select: 'dac_utilizadorid,dac_nome,dac_perfil,dac_ativo,dac_passwordhash,dac_passwordsalt,dac_iteracoes,dac_tentativasfalhadas,dac_bloqueadoate,_dac_cliente_value',
        $filter: `dac_email eq '@{${aspas(`toLower(trim(${ENTRADA(0)}))`)}}'`,
      }, {}, SEGURO),
      Inexistente_ou_inativo: {
        runAfter: { Procurar: ['Succeeded'] }, type: 'If',
        expression: { or: [
          { equals: ["@length(outputs('Procurar')?['body/value'])", 0] },
          { not: { equals: [`@${U}?['dac_ativo']`, true] } },
          { equals: [`@empty(${U}?['dac_passwordhash'])`, true] },
        ] },
        ...recusar(INVALIDO, 'inexistente'), else: { actions: {} },
      },
      Bloqueado: {
        runAfter: { Inexistente_ou_inativo: ['Succeeded'] }, type: 'If',
        expression: { greater: [`@ticks(coalesce(${U}?['dac_bloqueadoate'],'1900-01-01T00:00:00Z'))`, '@ticks(utcNow())'] },
        ...recusar('Conta bloqueada por 5 tentativas falhadas. Tentar de novo dentro de 15 minutos.', 'bloqueado'), else: { actions: {} },
      },
      Verificar: {
        runAfter: { Bloqueado: ['Succeeded'] }, type: 'OpenApiConnection', runtimeConfiguration: SEGURO,
        inputs: { host: host('hs', 'VerificarPassword'), parameters: { 'body/password': `@${ENTRADA(1)}`, 'body/salt': `@${U}?['dac_passwordsalt']`, 'body/hash': `@${U}?['dac_passwordhash']`, 'body/iteracoes': `@${U}?['dac_iteracoes']` }, authentication: AUTH },
      },
      Password_certa: {
        runAfter: { Verificar: ['Succeeded'] }, type: 'If',
        expression: { equals: ["@body('Verificar')?['valido']", true] },
        actions: {
          Gerar_testemunho: { runAfter: {}, type: 'Compose', inputs: "@replace(concat(guid(),guid()),'-','')", runtimeConfiguration: SEGURO },
          Abrir_sessao: atualizarUtilizador(`@${U}?['dac_utilizadorid']`, {
            dac_tentativasfalhadas: 0, dac_bloqueadoate: null, dac_ultimoacesso: '@utcNow()',
            dac_sessaotoken: "@outputs('Gerar_testemunho')", dac_sessaoexpira: '@addHours(utcNow(),8)',
          }, { Gerar_testemunho: ['Succeeded'] }, true),
          Responder_ok: responder({
            resultado: 'ok', mensagem: `Bem-vindo, @{${U}?['dac_nome']}.`, token: "@{outputs('Gerar_testemunho')}", nome: `@{${U}?['dac_nome']}`,
            perfil: `@{if(equals(${U}?['dac_perfil'],${PERFIL.admin}),'Admin',if(equals(${U}?['dac_perfil'],${PERFIL.gestor}),'Gestor','Cliente'))}`,
            utilizadorid: `@{${U}?['dac_utilizadorid']}`, clienteid: `@{coalesce(${U}?['_dac_cliente_value'],'')}`,
          }, { Abrir_sessao: ['Succeeded'] }, true),
        },
        else: {
          actions: {
            Contar_falhas: { runAfter: {}, type: 'Compose', inputs: `@add(coalesce(${U}?['dac_tentativasfalhadas'],0),1)` },
            Quinta_falha: {
              runAfter: { Contar_falhas: ['Succeeded'] }, type: 'If',
              expression: { greaterOrEquals: ["@outputs('Contar_falhas')", 5] },
              actions: {
                Bloquear: atualizarUtilizador(`@${U}?['dac_utilizadorid']`, { dac_tentativasfalhadas: 0, dac_bloqueadoate: '@addMinutes(utcNow(),15)' }),
                Responder_quinta_falha: responder({ resultado: 'erro', mensagem: 'Conta bloqueada por 5 tentativas falhadas. Tentar de novo dentro de 15 minutos.' }, { Bloquear: ['Succeeded'] }),
              },
              else: {
                actions: {
                  Registar_falha: atualizarUtilizador(`@${U}?['dac_utilizadorid']`, { dac_tentativasfalhadas: "@outputs('Contar_falhas')" }),
                  Responder_invalido: responder({ resultado: 'erro', mensagem: INVALIDO }, { Registar_falha: ['Succeeded'] }),
                },
              },
            },
          },
        },
      },
    },
  },
  ...erroTecnico('Não foi possível validar a entrada. Tentar de novo dentro de momentos.'),
});

// 4 · Fluxo DefinirPassword: o próprio (com a password atual) ou um Admin (para outro utilizador)
const ALVO = "outputs('Alvo')";
const PROPRIO = `equals(toLower(${ALVO}),toLower(${SESSAO}?['dac_utilizadorid']))`;
const definirPassword = def({}, gatilhoApp([
  ['Token', 'Testemunho de sessão devolvido pelo fluxo Entrar'],
  ['UtilizadorId', 'GUID do utilizador a alterar (vazio = o próprio)'],
  ['NovaPassword', 'Nova password, entre 8 e 128 caracteres'],
  ['PasswordAtual', 'Password atual (obrigatória quando é o próprio)'],
]), {
  Tentar: {
    runAfter: {}, type: 'Scope',
    actions: {
      Ler_sessao: lerSessao(0),
      Sem_sessao: semSessao,
      Alvo: { runAfter: { Sem_sessao: ['Succeeded'] }, type: 'Compose', inputs: `@if(empty(trim(coalesce(${ENTRADA(1)},''))),${SESSAO}?['dac_utilizadorid'],trim(${ENTRADA(1)}))` },
      Tamanho_invalido: {
        runAfter: { Alvo: ['Succeeded'] }, type: 'If',
        expression: { or: [{ less: [`@length(coalesce(${ENTRADA(2)},''))`, 8] }, { greater: [`@length(coalesce(${ENTRADA(2)},''))`, 128] }] },
        ...recusar('A nova password tem de ter entre 8 e 128 caracteres.', 'tamanho'), else: { actions: {} },
      },
      E_o_proprio: {
        runAfter: { Tamanho_invalido: ['Succeeded'] }, type: 'If',
        expression: { equals: [`@${PROPRIO}`, true] },
        actions: {
          Verificar_atual: {
            runAfter: {}, type: 'OpenApiConnection', runtimeConfiguration: SEGURO,
            inputs: { host: host('hs', 'VerificarPassword'), parameters: { 'body/password': `@coalesce(${ENTRADA(3)},'')`, 'body/salt': `@${SESSAO}?['dac_passwordsalt']`, 'body/hash': `@${SESSAO}?['dac_passwordhash']`, 'body/iteracoes': `@${SESSAO}?['dac_iteracoes']` }, authentication: AUTH },
          },
          Atual_errada: {
            runAfter: { Verificar_atual: ['Succeeded'] }, type: 'If',
            expression: { not: { equals: ["@body('Verificar_atual')?['valido']", true] } },
            ...recusar('A password atual não está certa.', 'atual_errada'), else: { actions: {} },
          },
        },
        else: {
          actions: {
            Nao_e_admin: {
              runAfter: {}, type: 'If',
              expression: { not: { equals: [`@${SESSAO}?['dac_perfil']`, PERFIL.admin] } },
              ...recusar('Só um Admin define a password de outro utilizador.', 'nao_admin'), else: { actions: {} },
            },
          },
        },
      },
      Gerar_hash: {
        runAfter: { E_o_proprio: ['Succeeded'] }, type: 'OpenApiConnection', runtimeConfiguration: SEGURO,
        inputs: { host: host('hs', 'GerarHash'), parameters: { 'body/password': `@${ENTRADA(2)}` }, authentication: AUTH },
      },
      Gravar_hash: atualizarUtilizador(`@${ALVO}`, {
        dac_passwordhash: "@body('Gerar_hash')?['hash']", dac_passwordsalt: "@body('Gerar_hash')?['salt']",
        dac_iteracoes: "@body('Gerar_hash')?['iteracoes']", dac_algoritmo: "@body('Gerar_hash')?['algoritmo']",
        dac_tentativasfalhadas: 0, dac_bloqueadoate: null,
        // reposta por um Admin: as sessões abertas do utilizador deixam de valer
        dac_sessaotoken: `@if(${PROPRIO},${SESSAO}?['dac_sessaotoken'],null)`,
      }, { Gerar_hash: ['Succeeded'] }, true),
      Responder_ok: responder({ resultado: 'ok', mensagem: 'Password definida.' }, { Gravar_hash: ['Succeeded'] }),
    },
  },
  ...erroTecnico('Não foi possível definir a password. Confirmar o utilizador e tentar de novo.'),
});
// o testemunho da sessão também é lido para o manter quando é o próprio
definirPassword.actions.Tentar.actions.Ler_sessao.inputs.parameters.$select += ',dac_sessaotoken';

// 5 · Fluxo Decidir: o Gestor propõe, o Admin decide. O perfil vem da sessão.
const P = "outputs('Ler_pedido')?['body']";
const ACAO = `toLower(trim(coalesce(${ENTRADA(2)},'')))`;
const COMENT = `trim(coalesce(${ENTRADA(3)},''))`;
const PERF = `${SESSAO}?['dac_perfil']`;
const QUEM = `${SESSAO}?['dac_utilizadorid']`;
const atualizarPedido = (campos, runAfter) => dv('UpdateOnlyRecord', { entityName: 'dac_pedidos', recordId: `@${P}?['dac_pedidoid']`, ...Object.fromEntries(Object.entries(campos).map(([k, v]) => ['item/' + k, v])) }, runAfter);
const decidirPedido = def({}, gatilhoApp([
  ['Token', 'Testemunho de sessão devolvido pelo fluxo Entrar'],
  ['PedidoId', 'GUID do pedido'],
  ['Acao', 'propor_aprovar, propor_rejeitar, aprovar ou rejeitar'],
  ['Comentario', 'Justificação (obrigatória para rejeitar)'],
]), {
  Tentar: {
    runAfter: {}, type: 'Scope',
    actions: {
      Ler_sessao: lerSessao(0),
      Sem_sessao: semSessao,
      Ler_pedido: dv('GetItem', { entityName: 'dac_pedidos', recordId: `@${ENTRADA(1)}`, $select: 'dac_pedidoid,dac_numeropedido,dac_tratamento,dac_decisao' }, { Sem_sessao: ['Succeeded'] }),
      Validar: {
        runAfter: { Ler_pedido: ['Succeeded'] }, type: 'Switch',
        expression: `@if(equals(${PERF},${PERFIL.cliente}),'cliente',if(not(equals(${P}?['dac_tratamento'],${TR_REVISAO})),'nao_revisao',if(or(equals(${P}?['dac_decisao'],${DEC.aprovado}),equals(${P}?['dac_decisao'],${DEC.rejeitado})),'ja_decidido',if(not(contains(createArray('propor_aprovar','propor_rejeitar','aprovar','rejeitar'),${ACAO})),'acao',if(and(startsWith(${ACAO},'propor'),not(equals(${PERF},${PERFIL.gestor}))),'so_gestor',if(and(not(startsWith(${ACAO},'propor')),not(equals(${PERF},${PERFIL.admin}))),'so_admin',if(and(endsWith(${ACAO},'rejeitar'),empty(${COMENT})),'comentario','ok')))))))`,
        cases: {
          cliente: { case: 'cliente', ...recusar('O perfil Cliente regista pedidos mas não decide.', 'cliente') },
          nao_revisao: { case: 'nao_revisao', ...recusar('Só os pedidos em Revisão são decididos.', 'nao_revisao') },
          ja_decidido: { case: 'ja_decidido', ...recusar('Este pedido já tem decisão final.', 'ja_decidido') },
          acao: { case: 'acao', ...recusar('Ação desconhecida.', 'acao') },
          so_gestor: { case: 'so_gestor', ...recusar('A proposta é do Gestor. O Admin decide diretamente com Aprovar ou Rejeitar.', 'so_gestor') },
          so_admin: { case: 'so_admin', ...recusar('A decisão final é do Admin. O Gestor propõe.', 'so_admin') },
          comentario: { case: 'comentario', ...recusar('Para rejeitar é preciso escrever a justificação.', 'comentario') },
        },
        default: { actions: {} },
      },
      E_proposta: {
        runAfter: { Validar: ['Succeeded'] }, type: 'If',
        expression: { equals: [`@startsWith(${ACAO},'propor')`, true] },
        actions: {
          Gravar_proposta: atualizarPedido({
            dac_decisao: `@if(equals(${ACAO},'propor_aprovar'),${DEC.proporAprovar},${DEC.proporRejeitar})`,
            'dac_PropostaPor@odata.bind': `/dac_utilizadors(@{${QUEM}})`,
            dac_comentarioproposta: `@{${COMENT}}`, dac_dataproposta: '@utcNow()',
          }, {}),
        },
        else: {
          actions: {
            Gravar_decisao: atualizarPedido({
              dac_decisao: `@if(equals(${ACAO},'aprovar'),${DEC.aprovado},${DEC.rejeitado})`,
              'dac_DecididoPor@odata.bind': `/dac_utilizadors(@{${QUEM}})`,
              dac_comentariodecisao: `@{if(empty(${COMENT}),'Sem comentário.',${COMENT})} (@{${SESSAO}?['dac_nome']}, Admin)`, dac_datadecisao: '@utcNow()',
            }, {}),
          },
        },
      },
      Responder_ok: responder({
        resultado: 'ok',
        mensagem: `Pedido @{${P}?['dac_numeropedido']}: @{if(equals(${ACAO},'aprovar'),'aprovado',if(equals(${ACAO},'rejeitar'),'rejeitado',if(equals(${ACAO},'propor_aprovar'),'proposta de aprovação registada','proposta de rejeição registada')))}.`,
      }, { E_proposta: ['Succeeded'] }),
    },
  },
  ...erroTecnico('Não foi possível gravar a decisão. O pedido existe e ainda está em Revisão?'),
});

// 6 · Fluxo Notificar (substitui o Aprovar): o email só avisa, a decisão é na app
const N = "triggerOutputs()?['body']";
const emailsDe = (nome, perfil, runAfter) => ({
  [`Ler_${nome}`]: dv('ListRecords', { entityName: 'dac_utilizadors', $select: 'dac_email', $filter: `dac_perfil eq ${perfil} and dac_ativo eq true` }, runAfter),
  [`Emails_${nome}`]: { runAfter: { [`Ler_${nome}`]: ['Succeeded'] }, type: 'Select', inputs: { from: `@outputs('Ler_${nome}')?['body/value']`, select: "@item()?['dac_email']" } },
});
const enviar = (nome, para, assunto, corpo, runAfter) => ({
  runAfter, type: 'If', expression: { greater: [`@length(${para})`, 0] },
  actions: { [`Enviar_${nome}`]: { runAfter: {}, type: 'OpenApiConnection', inputs: { host: host('ol', 'SendEmailV2'), parameters: { 'emailMessage/To': `@join(${para},';')`, 'emailMessage/Subject': assunto, 'emailMessage/Body': corpo }, authentication: AUTH } } },
  else: { actions: {} },
});
const LIGACAO = `<p><a href="@{parameters('${APP}')}">Abrir a APP DAC2627</a> › Ficha 04 · Revisão.</p>`;
const RESUMO = `<p>Pedido <b>@{${N}?['dac_numeropedido']}</b>, valor @{${N}?['dac_valor']} €.<br>@{${N}?['dac_observacoesprocessamento']}</p>`;
const FINAL = `@{if(equals(${N}?['dac_decisao'],${DEC.aprovado}),'aprovado','rejeitado')}`;
const ASSUNTO_FINAL = `Pedido @{${N}?['dac_numeropedido']}: ${FINAL}`;
const CORPO_FINAL = `<p>O pedido <b>@{${N}?['dac_numeropedido']}</b> foi ${FINAL}.</p><p>@{${N}?['dac_comentariodecisao']}</p>${LIGACAO}`;
const notificar = def(
  { [APP]: { defaultValue: LIGACAO_APP, type: 'String', metadata: { schemaName: 'dac_LigacaoApp', description: 'Endereço da app nos emails' } } },
  {
    Quando_a_decisao_de_um_pedido_em_revisao_muda: {
      type: 'OpenApiConnectionWebhook',
      inputs: { host: host('dv', 'SubscribeWebhookTrigger'), parameters: { 'subscriptionRequest/message': 3, 'subscriptionRequest/entityname': 'dac_pedido', 'subscriptionRequest/scope': 4, 'subscriptionRequest/filteringattributes': 'dac_decisao', 'subscriptionRequest/filterexpression': `dac_tratamento eq ${TR_REVISAO}` }, authentication: AUTH },
    },
  },
  {
    Conforme_a_decisao: {
      runAfter: {}, type: 'Switch', expression: `@string(coalesce(${N}?['dac_decisao'],-1))`,
      cases: {
        Aguarda: {
          case: String(DEC.aguarda),
          actions: {
            ...emailsDe('gestores', PERFIL.gestor, {}),
            Avisar_gestores: enviar('gestores', "body('Emails_gestores')", `Revisão: pedido @{${N}?['dac_numeropedido']} aguarda proposta`, `${RESUMO}<p>Um Gestor deve propor a decisão (aprovar ou rejeitar).</p>${LIGACAO}`, { Emails_gestores: ['Succeeded'] }),
          },
        },
        Proposta_aprovar: {
          case: String(DEC.proporAprovar),
          actions: {
            ...emailsDe('admins_aprovar', PERFIL.admin, {}),
            Avisar_admins_aprovar: enviar('admins_aprovar', "body('Emails_admins_aprovar')", `Revisão: proposta de aprovação do pedido @{${N}?['dac_numeropedido']}`, `${RESUMO}<p>Proposta do Gestor: <b>aprovar</b>. @{${N}?['dac_comentarioproposta']}</p><p>A decisão final é do Admin.</p>${LIGACAO}`, { Emails_admins_aprovar: ['Succeeded'] }),
          },
        },
        Proposta_rejeitar: {
          case: String(DEC.proporRejeitar),
          actions: {
            ...emailsDe('admins_rejeitar', PERFIL.admin, {}),
            Avisar_admins_rejeitar: enviar('admins_rejeitar', "body('Emails_admins_rejeitar')", `Revisão: proposta de rejeição do pedido @{${N}?['dac_numeropedido']}`, `${RESUMO}<p>Proposta do Gestor: <b>rejeitar</b>. @{${N}?['dac_comentarioproposta']}</p><p>A decisão final é do Admin.</p>${LIGACAO}`, { Emails_admins_rejeitar: ['Succeeded'] }),
          },
        },
      },
      default: {
        actions: {
          Decisao_final: {
            runAfter: {}, type: 'If',
            expression: { or: [{ equals: [`@${N}?['dac_decisao']`, DEC.aprovado] }, { equals: [`@${N}?['dac_decisao']`, DEC.rejeitado] }] },
            actions: {
              Tem_registo: {
                // cada ramo envia o seu email: referir a saída de uma ação saltada faz falhar a execução
                runAfter: {}, type: 'If', expression: { equals: [`@empty(${N}?['_dac_registadopor_value'])`, false] },
                actions: {
                  Ler_registo: dv('GetItem', { entityName: 'dac_utilizadors', recordId: `@${N}?['_dac_registadopor_value']`, $select: 'dac_email' }),
                  Avisar_registo: enviar('registo', "createArray(outputs('Ler_registo')?['body/dac_email'])", ASSUNTO_FINAL, CORPO_FINAL, { Ler_registo: ['Succeeded'] }),
                },
                else: {
                  actions: {
                    Ler_criador: dv('GetItem', { entityName: 'systemusers', recordId: `@${N}?['_createdby_value']`, $select: 'internalemailaddress' }),
                    Avisar_criador: enviar('criador', "createArray(outputs('Ler_criador')?['body/internalemailaddress'])", ASSUNTO_FINAL, CORPO_FINAL, { Ler_criador: ['Succeeded'] }),
                  },
                },
              },
            },
            else: { actions: {} },
          },
        },
      },
    },
  },
);

// 7 · Criar ou atualizar os fluxos (o DAC2627_Pedido_Aprovar passa a DAC2627_Pedido_Notificar, com o mesmo identificador)
const FLUXOS = [
  { nome: 'DAC2627_Utilizador_Entrar', antigo: null, desc: 'Ficha 04 · Revisão. Chamado pela app: verifica a password no serviço de hash (PBKDF2), bloqueia 15 minutos à quinta falha e devolve um testemunho de sessão válido 8 horas.', refs: { ...ref('dv'), ...ref('hs') }, def: entrar },
  { nome: 'DAC2627_Utilizador_DefinirPassword', antigo: null, desc: 'Ficha 04 · Revisão. Chamado pela app: o próprio muda a password (com a atual) ou um Admin define a de outro utilizador. Guarda só o hash e o salt.', refs: { ...ref('dv'), ...ref('hs') }, def: definirPassword },
  { nome: 'DAC2627_Pedido_Decidir', antigo: null, desc: 'Ficha 04 · Revisão. Chamado pela app: o Gestor propõe aprovar ou rejeitar, o Admin decide. O perfil vem da sessão, não da app.', refs: { ...ref('dv') }, def: decidirPedido },
  { nome: 'DAC2627_Pedido_Notificar', antigo: 'DAC2627_Pedido_Aprovar', desc: 'Ficha 04 · Revisão. Avisa por email quando a decisão de um pedido em Revisão muda: Gestores (aguarda proposta), Admins (proposta) e quem registou o pedido (decisão final). A decisão é na app.', refs: { ...ref('dv'), ...ref('ol') }, def: notificar },
];
const ids = {};
for (const f of FLUXOS) {
  const clientdata = JSON.stringify({ properties: { connectionReferences: f.refs, definition: f.def, templateName: null }, schemaVersion: '1.0.0.0' });
  const nomes = [f.nome, f.antigo].filter(Boolean).map((n) => `name eq '${n}'`).join(' or ');
  const ex = await get('workflows?$select=workflowid,statecode&$filter=' + encodeURIComponent(`category eq 5 and (${nomes})`));
  if (ex.value.length) {
    const id = ex.value[0].workflowid;
    if (ex.value[0].statecode === 1) await fetch(API + `workflows(${id})`, { method: 'PATCH', headers: H, body: JSON.stringify({ statecode: 0, statuscode: 1 }) });
    const r = await fetch(API + `workflows(${id})`, { method: 'PATCH', headers: H, body: JSON.stringify({ name: f.nome, clientdata, description: f.desc }) });
    log.push('fluxo atualizado ' + f.nome + ' ' + r.status + (r.ok ? '' : ' ' + (await r.text()).slice(0, 300))); ids[f.nome] = id;
  } else {
    const w = await post('workflows', { name: f.nome, description: f.desc, category: 5, type: 1, primaryentity: 'none', clientdata });
    log.push('fluxo criado ' + f.nome); ids[f.nome] = w.workflowid;
  }
}
for (const [nome, id] of Object.entries(ids)) {
  const r = await fetch(API + `workflows(${id})`, { method: 'PATCH', headers: H, body: JSON.stringify({ statecode: 1, statuscode: 2 }) });
  log.push('ativar ' + nome + ' ' + r.status + (r.ok ? '' : ' ' + (await r.text()).slice(0, 400)));
}
({ log, ids });
