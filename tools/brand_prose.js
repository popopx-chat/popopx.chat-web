// The residue census (brand_census.js) counts every "simplex" token, so it is dominated by
// identifiers (.simplex-preview-* classes, "simplex-private-card-1-title" keys, simplexAddressRegexp)
// that are not brand voice and cannot move without moving every reader.
// This one keeps only PROSE: a SimpleX token that stands alone (not glued to word chars, -, _ or .)
// and is not inside a URL, printed with its surrounding phrase so the brand decision is reviewable.
const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '..');
const SRC = path.join(root, 'website/src');
const SRC_DOCS = path.join(SRC, 'docs');
const LANGS = path.join(root, 'website/langs');

// Token must be the exact word "SimpleX" (capital S, capital X) so scheme strings like
// "simplex:" and hosts like simplex.chat never qualify.
const PROSE = /(?<![A-Za-z0-9_.\-])SimpleX(?![A-Za-z0-9_.\-])([\s\u00a0]*(?:Chat|chat|Ltd|Chat Ltd|limited)?)?/g;
const URLish = /https?:\/\/\S+|smp:\/\/\S+|xftp:\/\/\S+|mailto:\S+|\b[\w.-]*simplex\.(chat|im|org|io|com)\b/g;

function walk(dir, out = []) {
  if (!fs.existsSync(dir)) return out;
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out);
    else if (/\.(md|html|js|json|njk|css|txt|sh|yml|yaml)$/.test(e.name)) out.push(p);
  }
  return out;
}

function phrases(files) {
  const byPhrase = new Map();
  const byFile = new Map();
  for (const f of files) {
    const text = fs.readFileSync(f, 'utf8');
    const spans = [];
    for (const m of text.matchAll(URLish)) spans.push([m.index, m.index + m[0].length]);
    const inUrl = (i) => spans.some(([a, b]) => i >= a && i < b);
    let n = 0;
    for (const m of text.matchAll(PROSE)) {
      if (inUrl(m.index)) continue;
      const line = text.slice(0, m.index).split('\n').length;
      const tail = (m[1] || '').replace(/\s+/g, ' ').trim();
      const phrase = tail ? `SimpleX ${tail}` : 'SimpleX';
      const ctx = text.slice(Math.max(0, m.index - 34), m.index + phrase.length + 24).replace(/\s+/g, ' ');
      byPhrase.set(phrase, (byPhrase.get(phrase) || 0) + 1);
      n++;
      const list = byFile.get(path.relative(root, f)) || [];
      if (list.length < Number(process.argv[2] || 6)) list.push(`    L${line}: …${ctx}…`);
      byFile.set(path.relative(root, f), list);
    }
    if (!n) byFile.delete(path.relative(root, f));
  }
  return { byPhrase, byFile };
}

function report(name, files) {
  const { byPhrase, byFile } = phrases(files);
  const total = [...byPhrase.values()].reduce((a, b) => a + b, 0);
  console.log(`\n=== ${name}: ${total} prose tokens in ${byFile.size} files`);
  for (const [p, c] of [...byPhrase].sort((a, b) => b[1] - a[1])) console.log(String(c).padStart(5), p);
  for (const [f, ex] of byFile) { console.log(`  ${f}`); ex.forEach((e) => console.log(e)); }
}

// Everything under src/ that copy_sources.js emits, plus every .js that web.sh regenerates
// from a sibling .jsc - editing those is a no-op at the next build.
const GENERATED_DIRS = ['blog', 'images', 'link-images', 'file-assets'].map((d) => path.join(SRC, d));
const isGenerated = (f) =>
  f === path.join(SRC, 'privacy.md') ||
  GENERATED_DIRS.some((d) => f.startsWith(d + path.sep)) ||
  (f.endsWith('.js') && fs.existsSync(f.replace(/\.js$/, '.jsc')));

report('publishedDocs', walk(SRC_DOCS));
report('chrome', walk(SRC).filter((f) => !f.startsWith(SRC_DOCS + path.sep) && !isGenerated(f)));
report('langs', walk(LANGS));
