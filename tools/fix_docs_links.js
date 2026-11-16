// Repairs the two link classes the imported docs tree cannot resolve on its own:
// - blog posts: only upstream's site has them (this repo never had a blog/ tree)
// - app-repo files: they live in popopx-chat/popopx-chat, not in this site repo
// Run with --apply to write; default is a dry run.
const fs = require('fs');
const path = require('path');
const docsDir = path.resolve(__dirname, '../docs');
const apply = process.argv.includes('--apply');

const APP = 'https://github.com/popopx-chat/popopx-chat';
const blogSlugs = [
  '20220404-simplex-chat-instant-notifications',
  '20221108-simplex-chat-v4.2-security-audit-new-website',
  '20221206-simplex-chat-v4.3-voice-messages',
  '20230103-simplex-chat-v4.4-disappearing-messages',
  '20230301-simplex-file-transfer-protocol',
  '20230422-simplex-chat-vision-funding-v5-videos-files-passcode',
  '20231125-simplex-chat-v5-4-link-mobile-desktop-quantum-resistant-better-groups',
  '20240314-simplex-chat-v5-6-quantum-resistance-signal-double-ratchet-algorithm',
  '20240404-why-i-joined-simplex-chat-esraa-al-shafei',
  '20240604-simplex-chat-v5.8-private-message-routing-chat-themes',
  '20240814-simplex-chat-vision-funding-v6-private-routing-new-user-experience',
  '20241014-simplex-network-v6-1-security-review-better-calls-user-experience',
];

// Only the pages that are actually published (copy_sources.js excludes rfcs/,
// contributing/, dependencies/, LINKS.md, DOWNLOADS.md, lang/*/README.md).
const files = [
  'CLI.md', 'DIRECTORY.md', 'FAQ.md', 'SECURITY.md', 'SERVER.md',
  'TRADEMARK.md', 'TRADEMARK-POPOPX.md', 'TRANSPARENCY.md',
  'guide/README.md', 'guide/app-settings.md', 'guide/notifications.md',
  'guide/privacy-security.md', 'guide/send-messages.md',
  'protocol/channels-overview.md', 'protocol/channels-protocol.md',
  'lang/cs/CLI.md', 'lang/cs/SERVER.md',
  'lang/fr/CLI.md', 'lang/fr/SERVER.md',
  'lang/pl/CLI.md', 'lang/pl/SERVER.md',
];

const blogRe = new RegExp(
  '\\]\\((?:\\.\\./)+blog/(' + blogSlugs.join('|') + ')\\.md(#[^)]*)?\\)', 'g');
const absBlogRe = new RegExp(
  '\\]\\(/blog/(' + blogSlugs.join('|') + ')\\.md(#[^)]*)?\\)', 'g');
const appTargets = [
  ['/Dockerfile', `${APP}/blob/master/Dockerfile`],
  ['../NOTICE', `${APP}/blob/master/NOTICE`],
  ['../FORK.md', `${APP}/blob/master/FORK.md`],
  ['../ASSETS_LICENSE-POPOPX.md', `${APP}/blob/master/ASSETS_LICENSE-POPOPX.md`],
  ['../assets/ASSETS_LICENSE.md', `${APP}/blob/master/assets/ASSETS_LICENSE.md`],
  ['../LICENSE', `${APP}/blob/master/LICENSE`],
  ['../../README.md', `${APP}/blob/master/README.md`],
  ['../media-logos/', `${APP}/tree/master/media-logos`],
];

let blogEdits = 0, appEdits = 0;
for (const rel of files) {
  const abs = path.join(docsDir, rel);
  const before = fs.readFileSync(abs, 'utf8');
  let after = before
    .replace(blogRe, (m, slug, frag = '') => { blogEdits++; return `](https://simplex.chat/blog/${slug}${frag})`; })
    .replace(absBlogRe, (m, slug, frag = '') => { blogEdits++; return `](https://simplex.chat/blog/${slug}${frag})` });
  for (const [from, to] of appTargets) {
    const re = new RegExp('\\]\\(' + from.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\)', 'g');
    after = after.replace(re, () => { appEdits++; return `](${to})`; });
  }
  if (after !== before) {
    const n = before.split('\n').filter((l, i) => l !== (after.split('\n')[i] || '')).length;
    console.log(`${rel}: ${n} lines`);
    if (apply) fs.writeFileSync(abs, after, 'utf8');
  }
}
console.log(apply ? 'APPLIED' : 'DRY RUN', '- blog rewrites:', blogEdits, ' app-repo rewrites:', appEdits);
