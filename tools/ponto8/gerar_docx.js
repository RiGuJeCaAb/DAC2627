// Gera o documento do ponto 8 do Lab 4 (SharePoint, Dataverse e SQL) a partir de conteudo/ponto8.yaml.
// Chamado por `python -m tools.ponto8`, que converte o YAML para JSON e calcula as citações APA.
// Formatação RETA ESTGL 2022: Times New Roman 12, espaçamento 1,5, justificado, avanço de 1,25 cm,
// margens 3 cm (superior e esquerda) e 2,5 cm (inferior e direita), capítulos em página nova.
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, LevelFormat, Footer, PageNumber, PageBreak, TableLayoutType,
} = require("docx");

const [, , entrada, saida] = process.argv;
const d = JSON.parse(fs.readFileSync(entrada, "utf8"));

const CM = 567; // DXA por centímetro
const FONTE = "Times New Roman";
const corpoLargura = Math.round((21 - 3 - 2.5) * CM); // A4 menos as margens laterais

const p = (texto, extra = {}) => new Paragraph({
  alignment: AlignmentType.JUSTIFIED,
  indent: { firstLine: Math.round(1.25 * CM) },
  spacing: { line: 360, after: 120 },
  keepLines: true,
  children: [new TextRun({ text: texto, font: FONTE, size: 24 })],
  ...extra,
});
const centro = (texto, { size = 24, bold = false, before = 0, after = 0 } = {}) => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { before, after },
  children: [new TextRun({ text: texto, font: FONTE, size, bold })],
});
const titulo = (texto, nivel, novaPagina = false) => new Paragraph({
  heading: nivel, pageBreakBefore: novaPagina, keepNext: true, keepLines: true,
  children: [new TextRun({ text: texto, font: FONTE, bold: true, size: nivel === HeadingLevel.HEADING_1 ? 28 : 24 })],
});
const item = (texto) => new Paragraph({
  numbering: { reference: "pontos", level: 0 }, alignment: AlignmentType.JUSTIFIED,
  spacing: { line: 360, after: 60 }, keepLines: true,
  children: [new TextRun({ text: texto, font: FONTE, size: 24 })],
});
// Uma frase por parágrafo (regra de escrita do projeto)
const frases = (texto) => texto.replace(/\s+/g, " ").trim().match(/[^.!?]+[.!?]+(\s|$)/g).map((f) => f.trim());

const cap = [];
// ---- Capa
cap.push(
  centro("Instituto Politécnico de Viseu", { size: 28, bold: true }),
  centro("Escola Superior de Tecnologia e Gestão de Lamego", { size: 26, after: 120 }),
  centro("Curso Técnico Superior Profissional em Computação Cloud", { size: 24 }),
  centro("Desenvolvimento de Aplicações na Cloud", { size: 24, after: 2400 }),
  centro(d.capa.titulo, { size: 36, bold: true, after: 240 }),
  centro(d.capa.subtitulo, { size: 28, after: 2400 }),
  centro(`Autor: ${d.capa.autor}`, { size: 24 }),
  centro(`Docente: ${d.capa.docente}`, { size: 24, after: 2400 }),
  centro(d.capa.local_data, { size: 24 }),
);

// ---- Introdução (sem numeração)
cap.push(titulo("INTRODUÇÃO", HeadingLevel.HEADING_1, true));
for (const f of d.introducao) cap.push(p(f));

// ---- Um capítulo por serviço
const romanos = ["I", "II", "III", "IV", "V", "VI"];
d.servicos.forEach((s, i) => {
  const r = romanos[i];
  cap.push(titulo(`${r}. ${s.nome.toUpperCase()}`, HeadingLevel.HEADING_1, true));
  cap.push(titulo(`${r}.1. O que é`, HeadingLevel.HEADING_2));
  const fs_ = frases(s.oque);
  // a citação vai na frase da definição (a primeira), que é a que vem das fontes
  fs_.forEach((f, k) => cap.push(p(k === 0 ? f.replace(/\.$/, ` ${s.citacao}.`) : f)));
  cap.push(titulo(`${r}.2. Fatores positivos`, HeadingLevel.HEADING_2));
  cap.push(p(`Do lado positivo, ${s.nome_curto} apresenta os seguintes fatores:`));
  s.favor.forEach((t, k) => cap.push(item(k === s.favor.length - 1 ? t.replace(/\.$/, ` ${s.citacao}.`) : t)));
  cap.push(titulo(`${r}.3. Fatores menos positivos`, HeadingLevel.HEADING_2));
  cap.push(p(`Do lado menos positivo, há a ter em conta:`));
  s.contra.forEach((t, k) => cap.push(item(k === s.contra.length - 1 ? t.replace(/\.$/, ` ${s.citacao}.`) : t)));
});

// ---- Comparação
const rIV = romanos[d.servicos.length];
cap.push(titulo(`${rIV}. COMPARAÇÃO POR CRITÉRIO`, HeadingLevel.HEADING_1, true));
for (const f of d.comparacao_intro) cap.push(p(f));
cap.push(new Paragraph({
  alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 120 },
  children: [new TextRun({ text: d.tabela_legenda, font: FONTE, size: 22, bold: true })],
}));
const larg = [Math.round(corpoLargura * 0.19)];
const resto = corpoLargura - larg[0];
larg.push(Math.floor(resto / 3), Math.floor(resto / 3), resto - 2 * Math.floor(resto / 3));
const borda = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
const bordas = { top: borda, bottom: borda, left: borda, right: borda };
const celula = (texto, k, { cab = false } = {}) => new TableCell({
  width: { size: larg[k], type: WidthType.DXA }, borders: bordas,
  shading: cab ? { type: ShadingType.CLEAR, fill: "D9D9D9", color: "auto" } : undefined,
  margins: { top: 60, bottom: 60, left: 100, right: 100 },
  children: [new Paragraph({
    alignment: cab ? AlignmentType.CENTER : AlignmentType.LEFT, keepNext: true, keepLines: true,
    children: [new TextRun({ text: texto, font: FONTE, size: 20, bold: cab || k === 0 })],
  })],
});
const linhas = [new TableRow({
  tableHeader: true, cantSplit: true,
  children: ["Critério", ...d.servicos.map((s) => s.nome)].map((t, k) => celula(t, k, { cab: true })),
})];
for (const c of d.criterios) {
  linhas.push(new TableRow({ cantSplit: true, children: [c.criterio, c.Sp, c.Dv, c.Sql].map((t, k) => celula(t, k)) }));
}
cap.push(new Table({ width: { size: corpoLargura, type: WidthType.DXA }, columnWidths: larg, layout: TableLayoutType.FIXED, rows: linhas }));
cap.push(new Paragraph({
  alignment: AlignmentType.LEFT, spacing: { before: 120, after: 240 },
  children: [new TextRun({ text: d.tabela_fonte, font: FONTE, size: 20 })],
}));

// ---- Questões de análise: a comparação aplicada a dois casos
if (d.questoes && d.questoes.length) {
  const rV = romanos[d.servicos.length + 1];
  cap.push(titulo(`${rV}. QUESTÕES DE ANÁLISE`, HeadingLevel.HEADING_1, true));
  d.questoes.forEach((q, i) => {
    cap.push(titulo(`${rV}.${i + 1}. ${q.pergunta}`, HeadingLevel.HEADING_2));
    q.resposta.forEach((f, k) => cap.push(p(k === q.resposta.length - 1 ? f.replace(/\.$/, ` ${q.citacao}.`) : f)));
  });
}

// ---- Conclusão (sem numeração)
cap.push(titulo("CONCLUSÃO", HeadingLevel.HEADING_1, true));
for (const f of d.conclusao) cap.push(p(f));

// ---- Referências (APA 7.ª edição): ordem alfabética, um ponto abaixo do corpo, avanço suspenso
cap.push(titulo("REFERÊNCIAS BIBLIOGRÁFICAS", HeadingLevel.HEADING_1, true));
for (const ref of d.referencias) {
  cap.push(new Paragraph({
    alignment: AlignmentType.LEFT, spacing: { line: 240, after: 240 },
    indent: { left: Math.round(1.25 * CM), hanging: Math.round(1.25 * CM) },
    children: [
      new TextRun({ text: `${ref.autor} (${ref.ano}). `, font: FONTE, size: 22 }),
      new TextRun({ text: ref.titulo, font: FONTE, size: 22, italics: true }),
      new TextRun({ text: `. ${ref.site}. ${ref.recuperado}`, font: FONTE, size: 22 }),
    ],
  }));
}

const doc = new Document({
  creator: d.capa.autor, title: d.capa.titulo, description: d.capa.subtitulo,
  styles: {
    default: { document: { run: { font: FONTE, size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONTE, size: 28, bold: true, color: "000000" },
        paragraph: { spacing: { before: 0, after: 240 }, keepNext: true, keepLines: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONTE, size: 24, bold: true, color: "000000" },
        paragraph: { spacing: { before: 240, after: 120 }, keepNext: true, keepLines: true, outlineLevel: 1 } },
    ],
  },
  numbering: {
    config: [{ reference: "pontos", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: Math.round(1.25 * CM), hanging: 360 } } } }] }],
  },
  sections: [{
    properties: {
      titlePage: true,
      page: { size: { width: 11906, height: 16838 },
        margin: { top: 3 * CM, left: 3 * CM, bottom: Math.round(2.5 * CM), right: Math.round(2.5 * CM) } },
    },
    footers: {
      default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
        children: [new TextRun({ children: [PageNumber.CURRENT], font: FONTE, size: 20 })] })] }),
      first: new Footer({ children: [new Paragraph({ children: [] })] }),
    },
    children: cap,
  }],
});

Packer.toBuffer(doc).then((b) => { fs.writeFileSync(saida, b); console.log("docx:", saida); });
