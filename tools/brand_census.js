// Brand-residue census over what the site actually publishes:
//  - website/src/docs/**  (the 68 md that copy_sources.js emits, = docs/** minus excludes)
//  - website/src minus src/docs (chrome, includes, js, _data)
//  - website/langs (the 31 language copies)
// Splitting each hit into "inside a reachable URL/host" (held) and "used as a word"
// (the brand decision) is what makes the count actionable.
const fs = require('fs');
const path = require('path');
const root = path.resolve(__dirname, '..');
const URLish = /https?:\/\/[^\s)"'<>]+|smp:\/\/[^\s)"'<>]+|xftp:\/\/[^\s)"'<>]+|mailto:[^\s)"'<>]+|\b[\w.-]*simplex\.(chat|im|org|io|com)\b/g;

function walk(dir, out = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out);
    else if (/\.(md|html|js|json|njk|css|txt|sh|yml|yaml)$/.test(e.name)) out.push(p);
  }
  return out;
}
function rows(files, base) {
  const out = [];
  for (const f of files) {
    const text = fs.readFileSync(f, 'utf8');
    const hits = text.match(/SimpleX|SIMPLEX|simplex/g) || [];
    if (!hits.length) continue;
    const urls = (text.match(URLish) || []).length;
    out.push({ rel: path.relative(base, f), total: hits.length, urls, words: Math.max(0, hits.length - urls) });
  }
  return out.sort((a, b) => b.words - a.words);
}
const srcDocs = path.join(root, 'website/src/docs');
const src = path.join(root, 'website/src');
const chrome = walk(src).filter(f => !f.startsWith(srcDocs + path.sep));
const langs = walk(path.join(root, 'website/langs'));
const groups = { publishedDocs: rows(walk(srcDocs), srcDocs), chrome: rows(chrome, src), langs: rows(langs, path.join(root, 'website')) };
for (const [name, list] of Object.entries(groups)) {
  const t = list.reduce((s, r) => s + r.total, 0), u = list.reduce((s, r) => s + r.urls, 0);
  console.log(`\n### ${name}: ${list.length} files, ${t} occurrences, ${u} in URLs, ${t - u} as words`);
  list.slice(0, Number(process.argv[2] || 25)).forEach(r => console.log(String(r.words).padStart(5), String(r.urls).padStart(5), r.rel));
}
