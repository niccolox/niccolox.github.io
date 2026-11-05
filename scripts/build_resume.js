// Build the resume Word and PDF downloads from content/resume/resume.json.
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');
const {
  AlignmentType, BorderStyle, Document, ExternalHyperlink, LevelFormat, Packer,
  Paragraph, TabStopType, TextRun,
} = require('docx');

const ROOT = path.join(__dirname, '..');
const OUT = path.join(ROOT, 'site', 'assets', 'downloads');
const STEM = 'Nicholas-Roberts-Resume';
const resume = JSON.parse(fs.readFileSync(path.join(ROOT, 'content', 'resume', 'resume.json'), 'utf8'));

const FONT = 'Arial';
const INK = '1F2933';
const ACCENT = '1F4E79';
const MARGIN = 900;
const TEXT_WIDTH = 12240 - 2 * MARGIN;

const run = (text, options = {}) => new TextRun({ text, font: FONT, size: 18, color: INK, ...options });
const link = ({ text, url }) => new ExternalHyperlink({
  link: url,
  children: [run(text, { color: ACCENT, underline: {} })],
});
const bullet = (text) => new Paragraph({
  numbering: { reference: 'bullets', level: 0 },
  spacing: { after: 15, line: 228 },
  children: [run(text)],
});
const sectionHeading = (text) => new Paragraph({
  spacing: { before: 120, after: 50 },
  keepNext: true,
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: ACCENT, space: 2 } },
  children: [run(text, { bold: true, size: 21, color: ACCENT })],
});

const children = [
  new Paragraph({ spacing: { after: 10 }, children: [run(resume.name, { bold: true, size: 38, color: ACCENT })] }),
  new Paragraph({ spacing: { after: 20 }, children: [run(resume.title, { bold: true, size: 23 })] }),
  new Paragraph({ spacing: { after: 30 }, children: [run(resume.focus)] }),
  new Paragraph({ spacing: { after: 30 }, children: [run(resume.statement, { italics: true })] }),
  new Paragraph({
    spacing: { after: 60 },
    children: resume.contact.flatMap((item, index) => [
      ...(index ? [run('  |  ')] : []),
      item.url ? link(item) : run(item.text),
    ]),
  }),
  sectionHeading('Summary'),
  ...resume.summary.map(bullet),
  sectionHeading('Professional experience'),
];

for (const job of resume.experience) {
  children.push(new Paragraph({
    spacing: { before: 70 },
    keepNext: true,
    tabStops: [{ type: TabStopType.RIGHT, position: TEXT_WIDTH }],
    children: [run(job.company, { bold: true, size: 19 }), run(`\t${job.dates}`)],
  }));
  children.push(new Paragraph({
    spacing: { after: 15 },
    keepNext: true,
    children: [run(job.role, { italics: true })],
  }));
  children.push(...job.bullets.map(bullet));
}

children.push(sectionHeading('Civic activism and education'));
for (const item of resume.other) {
  children.push(new Paragraph({
    spacing: { after: 25, line: 228 },
    children: [
      run(`${item.heading}: `, { bold: true }),
      run(item.text),
      ...(item.link ? [run(' '), link(item.link)] : []),
    ],
  }));
}

const doc = new Document({
  creator: resume.name,
  title: `${resume.name} - ${resume.title}`,
  subject: 'Resume',
  styles: { default: { document: { run: { font: FONT, size: 18 } } } },
  numbering: {
    config: [{
      reference: 'bullets',
      levels: [{
        level: 0,
        format: LevelFormat.BULLET,
        text: '•',
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 220, hanging: 170 } } },
      }],
    }],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 720, bottom: 640, left: MARGIN, right: MARGIN },
      },
    },
    children,
  }],
});

Packer.toBuffer(doc).then((buffer) => {
  const docxPath = path.join(OUT, `${STEM}.docx`);
  fs.writeFileSync(docxPath, buffer);
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'resume-soffice-'));
  execFileSync('soffice', [
    `-env:UserInstallation=file://${profile}`, '--headless',
    '--convert-to', 'pdf:writer_pdf_Export:{"UseTaggedPDF":{"type":"boolean","value":"true"}}',
    '--outdir', OUT, docxPath,
  ], { stdio: 'ignore' });
  fs.rmSync(profile, { recursive: true, force: true });
  console.log(`Wrote ${STEM}.docx and ${STEM}.pdf`);
});
