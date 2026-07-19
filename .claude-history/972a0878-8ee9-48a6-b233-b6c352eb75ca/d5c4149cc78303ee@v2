const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, BorderStyle, WidthType, PageBreak,
} = require("docx");

// DXA helpers
const CM = 567;
const PT = 20;

const PAGE_TOP = Math.round(3.7 * CM);
const PAGE_BOTTOM = Math.round(3.5 * CM);
const PAGE_LEFT = Math.round(2.8 * CM);
const PAGE_RIGHT = Math.round(2.6 * CM);
const PAGE_WIDTH = 11906;  // A4
const PAGE_HEIGHT = 16838;
const CONTENT_WIDTH = PAGE_WIDTH - PAGE_LEFT - PAGE_RIGHT;
const INDENT_2CHAR = Math.round(2 * 16 * PT);
const LINE_SPACING_28 = Math.round((28 / 12) * 240);

const SIZE_22 = 44; // 二号
const SIZE_16 = 32; // 三号
const SIZE_14 = 28; // 四号
const SIZE_12 = 24; // 小四

function bp(text) {
  return new Paragraph({
    spacing: { line: LINE_SPACING_28 },
    indent: { firstLine: INDENT_2CHAR },
    children: [new TextRun({ text, font: "仿宋", size: SIZE_16 })],
  });
}

function hp(text) {
  return new Paragraph({
    spacing: { line: LINE_SPACING_28, before: 120, after: 60 },
    indent: { firstLine: INDENT_2CHAR },
    children: [new TextRun({ text, font: "黑体", size: SIZE_16, bold: true })],
  });
}

const children = [];

// Document number
children.push(new Paragraph({
  alignment: AlignmentType.RIGHT,
  spacing: { line: 360, after: 120 },
  children: [new TextRun({ text: "印尼金川WP公司装备能源部〔" +
    "2026〕XX号", font: "仿宋", size: SIZE_16 })],
}));

// Title
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { line: 400, after: 200 },
  children: [new TextRun({ text: "码头堆棚施工领料确认函",
    font: "黑体", size: SIZE_22, bold: true })],
}));

// Salutation
children.push(new Paragraph({
  spacing: { line: LINE_SPACING_28, after: 60 },
  children: [new TextRun({ text: "上海实默实业有限公司：",
    font: "仿宋", size: SIZE_16 })],
}));

// Intro
children.push(bp(
  "关于贵公司承建的我司码头堆棚建设项目" +
  "（下称“本项目”），在施工期间（2024年9月" +
  "至2026年3月），我司根据施工需要向贵公司" +
  "提供了施工所需的部分材料。现就材料领用" +
  "及费用确认事宜致函如下："
));

// Section 1
children.push(hp("一、材料领用概况"));
children.push(bp(
  "施工期间，贵公司从我司陆续领用施工" +
  "材料共计柒佰一拾五项（715项），涵盖钢材" +
  "、五金工具、电气配件、焊接材料、安全" +
  "防护用品等类别，具体详见附件《码头堆棚" +
  "施工领料明细表》。"
));

// Section 2
children.push(hp("二、费用确认"));
children.push(bp(
  "上述领用材料按我司采购成本计价，折合" +
  "美元合计为捌万四千二百三十二美元五角" +
  "四分（USD 84,232.54）。该费用已在本项目费用结算" +
  "中一并列明。"
));

// Section 3
children.push(hp("三、确认事项"));
children.push(bp("请贵公司对以下内容予以书面确认："));

const listItems = [
  "1. 附件所列材料明细与贵公司实际领用情况一致；",
  "2. 领用材料的数量、规格型号准确无误；",
  "3. 对上述材料费金额无异议。",
];
listItems.forEach(item => {
  children.push(new Paragraph({
    spacing: { line: LINE_SPACING_28 },
    indent: { firstLine: INDENT_2CHAR },
    children: [new TextRun({ text: item, font: "仿宋", size: SIZE_16 })],
  }));
});

// Section 4
children.push(hp("四、确认方式"));
children.push(bp(
  "请贵公司在本函及附件上加盖公章并签字" +
  "确认，扫描后回复我司。如对明细有异议，" +
  "请于收到本函后7个工作日内书面反馈。"
));

// Blank line
children.push(new Paragraph({ spacing: { line: LINE_SPACING_28 }, children: [] }));

// Attachment
children.push(new Paragraph({
  spacing: { line: LINE_SPACING_28 },
  indent: { left: INDENT_2CHAR },
  children: [new TextRun({
    text: "附件：《码头堆棚施工领料明细表》",
    font: "仿宋", size: SIZE_16 })],
}));

// Spacing before sender
children.push(new Paragraph({ spacing: { line: LINE_SPACING_28 }, children: [] }));
children.push(new Paragraph({ spacing: { line: LINE_SPACING_28 }, children: [] }));
children.push(new Paragraph({ spacing: { line: LINE_SPACING_28 }, children: [] }));

// Sender
["发函单位：印尼金川WP公司装备能源部",
 "经办人：",
 "日    期：2026年    月    日",
].forEach(line => {
  children.push(new Paragraph({
    alignment: AlignmentType.RIGHT,
    spacing: { line: LINE_SPACING_28 },
    children: [new TextRun({ text: line, font: "仿宋", size: SIZE_16 })],
  }));
});

// Page break
children.push(new Paragraph({ children: [new PageBreak()] }));

// Confirmation receipt title
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { line: 400, after: 200 },
  children: [new TextRun({ text: "确  认  回  执", font: "黑体", size: SIZE_16, bold: true })],
}));

children.push(bp(
  "本单位已收到并核对上述《码头堆棚施工" +
  "领料确认函》及附件，经核实："
));

children.push(new Paragraph({
  spacing: { line: LINE_SPACING_28 },
  indent: { firstLine: INDENT_2CHAR },
  children: [new TextRun({
    text: "□  确认材料明细及费用金额无误",
    font: "仿宋", size: SIZE_16 })],
}));
children.push(new Paragraph({
  spacing: { line: LINE_SPACING_28 },
  indent: { firstLine: INDENT_2CHAR },
  children: [new TextRun({
    text: "□  有异议，详见书面说明",
    font: "仿宋", size: SIZE_16 })],
}));

children.push(new Paragraph({ spacing: { line: LINE_SPACING_28 }, children: [] }));

// Confirmation info table
const cBorder = { style: BorderStyle.NONE };
const cMargins = { top: 80, bottom: 80, left: 120, right: 120 };
const col1 = Math.round(CONTENT_WIDTH * 0.3);
const col2 = CONTENT_WIDTH - col1;

const rows = [
  ["确认单位：", "上海实默实业有限公司"],
  ["确认人：", ""],
  ["日    期：", "2026年    月    日"],
  ["公    章：", ""],
];

const confirmTable = new Table({
  width: { size: CONTENT_WIDTH, type: WidthType.DXA },
  columnWidths: [col1, col2],
  rows: rows.map(([label, val]) => new TableRow({
    children: [
      new TableCell({
        borders: cBorder, width: { size: col1, type: WidthType.DXA }, margins: cMargins,
        children: [new Paragraph({ children: [new TextRun({ text: label, font: "仿宋", size: SIZE_14 })] })],
      }),
      new TableCell({
        borders: cBorder, width: { size: col2, type: WidthType.DXA }, margins: cMargins,
        children: [new Paragraph({ children: [new TextRun({ text: val, font: "仿宋", size: SIZE_14 })] })],
      }),
    ],
  })),
});

children.push(confirmTable);

// ── Assemble ──
const doc = new Document({
  styles: {
    default: { document: { run: { font: "仿宋", size: SIZE_16 } } },
  },
  sections: [{
    properties: {
      page: {
        size: { width: PAGE_WIDTH, height: PAGE_HEIGHT },
        margin: { top: PAGE_TOP, bottom: PAGE_BOTTOM, left: PAGE_LEFT, right: PAGE_RIGHT },
      },
    },
    children,
  }],
});

const outputPath = "D:\\second-brain\\submissions\\码头堆棚施工领料确认函.docx";
Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(outputPath, buf);
  console.log("OK: " + outputPath);
  console.log("Size: " + buf.length + " bytes");
});
