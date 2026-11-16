// Census of every markdown/html link in the imported docs tree, classified with
// the same rules website/.eleventy.js:replaceLink applies at build time.
const fs = require('fs');
const path = require('path');
const siteRoot = path.resolve(__dirname, '..');
const srcDocs = path.join(siteRoot, 'website/src/docs');
const uri = require(path.join(siteRoot, 'website/node_modules/fast-uri'));

function walk(dir, out = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out);
    else if (e.name.endsWith('.md')) out.push(p);
  }
  return out;
}

const linkRe = /\]\(([^)\s]+)(?:\s+"[^"]*")?\)|href=["']([^"']+)["']/g;
const cats = {};
const broken = [];
const github = [];
const files = walk(srcDocs);
for (const hostFile of files) {
  const text = fs.readFileSync(hostFile, 'utf8');
  let m;
  while ((m = linkRe.exec(text))) {
    const link = m[1] || m[2];
    if (!link || link.startsWith('#') || /^(mailto:|tel:|data:)/.test(link)) continue;
    let parsed;
    try { parsed = uri.parse(link); } catch { continue; }
    if (parsed.scheme || parsed.host) { cats.external = (cats.external || 0) + 1; continue; }
    let linkFile = path.resolve(hostFile, '..', parsed.path);
    if (parsed.path.startsWith('/')) {
      const srcIndex = hostFile.indexOf('/src');
      if (srcIndex !== -1) linkFile = path.join(hostFile.slice(0, srcIndex + 4), parsed.path);
    }
    if (fs.existsSync(linkFile) && fs.statSync(linkFile).isFile()) {
      cats['website-file'] = (cats['website-file'] || 0) + 1;
    } else if (!fs.existsSync(linkFile)) {
      const stripped = linkFile.replace('/website/src', '');
      if (fs.existsSync(stripped)) {
        cats['project-file->upstream-github'] = (cats['project-file->upstream-github'] || 0) + 1;
        github.push([path.relative(srcDocs, hostFile), parsed.path, path.relative(siteRoot, stripped)]);
      } else {
        cats.BROKEN = (cats.BROKEN || 0) + 1;
        broken.push([path.relative(srcDocs, hostFile), parsed.path]);
      }
    }
  }
}
console.log('md files:', files.length);
console.log(JSON.stringify(cats, null, 2));
const byTarget = {};
for (const [f, l] of broken) { byTarget[l] = byTarget[l] || []; byTarget[l].push(f); }
console.log('--- BROKEN by target ---');
Object.entries(byTarget).sort((a, b) => b[1].length - a[1].length).forEach(([t, fs_]) =>
  console.log(String(fs_.length).padStart(3), t, '|', fs_.slice(0, 3).join(', ')));
console.log('--- BROKEN full list ---');
broken.forEach(([f, l]) => console.log(f, '=>', l));
console.log('--- project-file links that would be rewritten to UPSTREAM github ---', github.length);
github.forEach(g => console.log('  ', g.join('  ->  ')));
