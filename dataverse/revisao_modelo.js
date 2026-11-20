// Ficha 04 · Revisão (v1.6.0) — modelo de dados na solução DAC2627: tabela Utilizador e colunas de decisão no Pedido.
// Correr num separador aberto em https://org0f43a370.crm4.dynamics.com (sessão do utilizador). Idempotente: o que já existe é saltado.
const API = '/api/data/v9.2/';
const H = { 'Content-Type': 'application/json; charset=utf-8', 'OData-MaxVersion': '4.0', 'OData-Version': '4.0', Accept: 'application/json', 'MSCRM.SolutionUniqueName': 'DAC2627' };
const log = [];
const T = 774300000; // prefixo das opções do editor DAC CC MB
const PT = 2070;     // código de idioma português (Portugal)
const lbl = (t) => ({ '@odata.type': 'Microsoft.Dynamics.CRM.Label', LocalizedLabels: [{ '@odata.type': 'Microsoft.Dynamics.CRM.LocalizedLabel', Label: t, LanguageCode: PT }] });
const req = (n) => ({ Value: n ? 'ApplicationRequired' : 'None', CanBeChanged: true, ManagedPropertyLogicalName: 'canmodifyrequirementlevelsettings' });
async function chamar(metodo, p, b) {
  const r = await fetch(API + p, { method: metodo, headers: H, body: b ? JSON.stringify(b) : undefined });
  const t = await r.text();
  if (!r.ok) throw new Error(metodo + ' ' + p + ' ' + r.status + ' ' + t.slice(0, 600));
  return t ? JSON.parse(t) : {};
}
const existe = (p) => fetch(API + p, { headers: { Accept: 'application/json' } }).then((r) => r.ok);

// Colunas (AttributeMetadata). secured = segurança ao nível da coluna: só quem tem um perfil de segurança de campos
// (ou o administrador do sistema) lê o valor. É o caso do hash, do salt e do testemunho de sessão.
const texto = (nome, mostra, max, o = {}) => ({ '@odata.type': 'Microsoft.Dynamics.CRM.StringAttributeMetadata', SchemaName: nome, DisplayName: lbl(mostra), Description: lbl(o.desc || mostra), RequiredLevel: req(o.obrig), MaxLength: max, FormatName: { Value: o.formato || 'Text' }, IsSecured: !!o.secured });
const memo = (nome, mostra, max, desc) => ({ '@odata.type': 'Microsoft.Dynamics.CRM.MemoAttributeMetadata', SchemaName: nome, DisplayName: lbl(mostra), Description: lbl(desc || mostra), RequiredLevel: req(false), MaxLength: max, Format: 'TextArea' });
const inteiro = (nome, mostra, desc, min = 0, max = 2147483647) => ({ '@odata.type': 'Microsoft.Dynamics.CRM.IntegerAttributeMetadata', SchemaName: nome, DisplayName: lbl(mostra), Description: lbl(desc || mostra), RequiredLevel: req(false), MinValue: min, MaxValue: max, Format: 'None' });
const data = (nome, mostra, desc) => ({ '@odata.type': 'Microsoft.Dynamics.CRM.DateTimeAttributeMetadata', SchemaName: nome, DisplayName: lbl(mostra), Description: lbl(desc || mostra), RequiredLevel: req(false), Format: 'DateAndTime', DateTimeBehavior: { Value: 'UserLocal' } });
const simNao = (nome, mostra, def, desc) => ({ '@odata.type': 'Microsoft.Dynamics.CRM.BooleanAttributeMetadata', SchemaName: nome, DisplayName: lbl(mostra), Description: lbl(desc || mostra), RequiredLevel: req(false), DefaultValue: def, OptionSet: { TrueOption: { Value: 1, Label: lbl('Sim') }, FalseOption: { Value: 0, Label: lbl('Não') } } });
const escolha = (nome, mostra, opcoes, def, desc) => ({ '@odata.type': 'Microsoft.Dynamics.CRM.PicklistAttributeMetadata', SchemaName: nome, DisplayName: lbl(mostra), Description: lbl(desc || mostra), RequiredLevel: req(true), DefaultFormValue: def, OptionSet: { '@odata.type': 'Microsoft.Dynamics.CRM.OptionSetMetadata', IsGlobal: false, OptionSetType: 'Picklist', Options: opcoes.map((t, i) => ({ Value: T + i, Label: lbl(t) })) } });

// 1 · Tabela Utilizador
if (!(await existe("EntityDefinitions(LogicalName='dac_utilizador')"))) {
  await chamar('POST', 'EntityDefinitions', {
    '@odata.type': 'Microsoft.Dynamics.CRM.EntityMetadata', SchemaName: 'dac_Utilizador',
    DisplayName: lbl('Utilizador'), DisplayCollectionName: lbl('Utilizadores'),
    Description: lbl('Utilizadores da revisão de pedidos da APP DAC2627 (Ficha 04 · Revisão). A password nunca é guardada: só o hash PBKDF2 e o salt.'),
    OwnershipType: 'UserOwned', HasActivities: false, HasNotes: false, IsActivity: false,
    PrimaryNameAttribute: 'dac_nome',
    Attributes: [{ ...texto('dac_Nome', 'Nome', 100, { obrig: true }), IsPrimaryName: true }],
  });
  log.push('tabela dac_utilizador criada');
}
const UTIL = "EntityDefinitions(LogicalName='dac_utilizador')";
const colunasUtilizador = [
  texto('dac_Email', 'Email', 100, { obrig: true, formato: 'Email', desc: 'Email de entrada (único)' }),
  escolha('dac_Perfil', 'Perfil', ['Admin', 'Gestor', 'Cliente'], T + 2, 'Admin: gere utilizadores e decide. Gestor: CRUD de clientes e pedidos e propõe a decisão. Cliente: regista pedidos.'),
  texto('dac_PasswordHash', 'Hash da password', 100, { secured: true, desc: 'PBKDF2-SHA256 em Base64, calculado pelo serviço de hash' }),
  texto('dac_PasswordSalt', 'Salt da password', 100, { secured: true, desc: 'Salt aleatório de 16 bytes em Base64' }),
  inteiro('dac_Iteracoes', 'Iterações', 'Iterações PBKDF2 usadas neste hash', 0, 10000000),
  texto('dac_Algoritmo', 'Algoritmo', 30, { desc: 'Algoritmo do hash (PBKDF2-SHA256)' }),
  simNao('dac_Ativo', 'Ativo', true, 'Um utilizador inativo não entra'),
  inteiro('dac_TentativasFalhadas', 'Tentativas falhadas', 'Entradas falhadas seguidas (5 bloqueiam 15 minutos)', 0, 100),
  data('dac_BloqueadoAte', 'Bloqueado até', 'Fim do bloqueio depois de 5 tentativas falhadas'),
  data('dac_UltimoAcesso', 'Último acesso'),
  texto('dac_SessaoToken', 'Testemunho de sessão', 64, { secured: true, desc: 'Gerado pelo fluxo Entrar, válido até Sessão expira' }),
  data('dac_SessaoExpira', 'Sessão expira'),
];
for (const c of colunasUtilizador) {
  const ln = c.SchemaName.toLowerCase();
  if (await existe(`${UTIL}/Attributes(LogicalName='${ln}')`)) { log.push('existe ' + ln); continue; }
  await chamar('POST', `${UTIL}/Attributes`, c);
  log.push('coluna ' + ln);
}

// Chave alternativa: um email só pode existir uma vez
if (!(await existe(`${UTIL}/Keys(LogicalName='dac_chave_email')`))) {
  await chamar('POST', `${UTIL}/Keys`, { SchemaName: 'dac_chave_email', DisplayName: lbl('Email único'), KeyAttributes: ['dac_email'] });
  log.push('chave alternativa dac_chave_email');
}

// 2 · Pesquisas (relações 1:N)
async function pesquisa(relacao, entidade, nome, mostra, referenciada, desc) {
  if (await existe(`RelationshipDefinitions(SchemaName='${relacao}')`)) { log.push('existe ' + relacao); return; }
  await chamar('POST', 'RelationshipDefinitions', {
    '@odata.type': 'Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata', SchemaName: relacao,
    ReferencedEntity: referenciada, ReferencingEntity: entidade,
    CascadeConfiguration: { Assign: 'NoCascade', Delete: 'RemoveLink', Merge: 'NoCascade', Reparent: 'NoCascade', Share: 'NoCascade', Unshare: 'NoCascade' },
    Lookup: { '@odata.type': 'Microsoft.Dynamics.CRM.LookupAttributeMetadata', SchemaName: nome, DisplayName: lbl(mostra), Description: lbl(desc || mostra), RequiredLevel: req(false) },
  });
  log.push('pesquisa ' + nome);
}
await pesquisa('dac_Cliente_Utilizador', 'dac_utilizador', 'dac_Cliente', 'Cliente', 'dac_cliente', 'Cliente associado a um utilizador com o perfil Cliente');
await pesquisa('dac_Utilizador_Pedido_Registado', 'dac_pedido', 'dac_RegistadoPor', 'Registado por', 'dac_utilizador', 'Utilizador que registou o pedido no ecrã de revisão');
await pesquisa('dac_Utilizador_Pedido_Proposta', 'dac_pedido', 'dac_PropostaPor', 'Proposta por', 'dac_utilizador', 'Gestor que propôs a decisão (escrito pelo fluxo Decidir)');
await pesquisa('dac_Utilizador_Pedido_Decisao', 'dac_pedido', 'dac_DecididoPor', 'Decidido por', 'dac_utilizador', 'Admin que tomou a decisão final (escrito pelo fluxo Decidir)');

// 3 · Pedido: colunas da proposta
const PED = "EntityDefinitions(LogicalName='dac_pedido')";
for (const c of [
  memo('dac_ComentarioProposta', 'Comentário da proposta', 2000, 'Justificação do Gestor (escrito pelo fluxo Decidir)'),
  data('dac_DataProposta', 'Data da proposta', 'Escrito pelo fluxo Decidir'),
]) {
  const ln = c.SchemaName.toLowerCase();
  if (await existe(`${PED}/Attributes(LogicalName='${ln}')`)) { log.push('existe ' + ln); continue; }
  await chamar('POST', `${PED}/Attributes`, c);
  log.push('coluna ' + ln);
}

// 4 · Pedido: duas opções novas na Decisão (Proposta: aprovar, Proposta: rejeitar)
const dec = await (await fetch(API + `${PED}/Attributes(LogicalName='dac_decisao')/Microsoft.Dynamics.CRM.PicklistAttributeMetadata?$select=LogicalName&$expand=OptionSet($select=Options)`, { headers: { Accept: 'application/json' } })).json();
const valores = dec.OptionSet.Options.map((o) => o.Value);
for (const [v, t] of [[T + 3, 'Proposta: aprovar'], [T + 4, 'Proposta: rejeitar']]) {
  if (valores.includes(v)) { log.push('opção existe ' + v); continue; }
  await chamar('POST', 'InsertOptionValue', { EntityLogicalName: 'dac_pedido', AttributeLogicalName: 'dac_decisao', Value: v, Label: lbl(t), SolutionUniqueName: 'DAC2627' });
  log.push('opção ' + v + ' ' + t);
}

await chamar('POST', 'PublishXml', { ParameterXml: '<importexportxml><entities><entity>dac_utilizador</entity><entity>dac_pedido</entity></entities></importexportxml>' });
log.push('publicado');
log;
