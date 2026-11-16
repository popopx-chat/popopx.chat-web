# popopx.chat-web
popopx.chat 网站

# popopx.chat website content

Local store of the files that are to become the popopx.chat website. Nothing here is served yet: the
host answers only its current PHP page, and writing to it needs the server credentials, which stay
with the user (see `/Users/elliot/popopx-chat/popopx.chat/.well-known/README.md`).

## Where these files come from

`website/` is **this fork's own rebranded copy**, extracted from git history, not upstream's raw tree:

```sh
git -C /Users/elliot/popopx-chat/popopx-chat archive 9c8df8f09 website | tar -x -C .
```

`9c8df8f09` is the parent of `9996634ee` ("Remove the upstream editorial content from this fork",
2026-11-13) - the last commit that carried the site, already carrying the rulings applied to it
(`526823a5e`, `a83ea58be`: the site's own self-declarations moved to popopx.chat).

Measured against upstream `simplex-chat@f8776692d` (local clone, 2026-11-10):

| | |
| --- | --- |
| files here / files upstream | 585 / 585, same path set, none only on one side |
| byte-identical to upstream | 514 |
| changed by our rebrand | 71 - `.eleventy.js`, `channel_sample.html`, the 32 `langs/*.json`, and the rest of the 33 text files |
| `src/img/**` changed by us | **0 of 334** |

## What still blocks publishing it

1. **Brand artwork.** All 334 files under `src/img/` are upstream's bytes - SimpleX logos, symbols and
   illustrations. `ASSETS_LICENSE.md` puts those outside the AGPL grant and `TRADEMARK.md` requires
   dropping SimpleX from branding, so the site cannot be published over them; they must be redrawn or
   the pages that use them dropped. (Same finding for the relay's own page: 24 of its 25 `media/` files
   are upstream's bytes - proven by `sha256` in `site-link-sources/MANIFEST.tsv`.)
2. **Editorial content is deliberately absent - and the navigation no longer promises it.** `src/docs/`,
   `src/blog/`, `src/plans/` and `src/langs/` do not exist in this tree: they lived at the repository root
   and were removed by ruling. The menus still offered them anyway - the Guide and Reference dropdowns
   pointed into `/docs/**`, and `/faq/ /about/ /jobs/ /privacy/ /security/ /transparency/ /reproduce/` had
   no source at all, so our own navbar and footer sent visitors to 404s. Those entries are removed from
   `_includes/navbar.html`, `_includes/footer.html`, `downloads.html` and `docs_dropdown.json`;
   `guide_dropdown.json` and the empty Guide menu went with it, because a menu that opens onto nothing is
   its own bug. `/docs/glossary.html` stays: the glossary is ours, it builds, and the file-transfer page's
   tooltips read it. What is left here is the content decision, not the links. The command that measures
   whether the site still links to anything the build does not produce (run from the repository root after
   `bash build.sh`) is:

   ```sh
   python3 - <<'PY'
   import os, re
   root, href = "website/_site", re.compile(r'''href\s*=\s*["']([^"'#?]*)''')
   weblike, scheme = re.compile(r'^(https?:)?//'), re.compile(r'^([a-zA-Z][a-zA-Z0-9+.-]*):')
   def built(p):
       p = p.strip("/")
       return any(os.path.exists(os.path.join(root, c)) for c in (p, p + ".html", os.path.join(p, "index.html")))
   dead = {}
   for d, _, fs in os.walk(root):
       for f in fs:
           if not f.endswith(".html"): continue
           for m in href.finditer(open(os.path.join(d, f), encoding="utf-8", errors="replace").read()):
               u = m.group(1).strip()
               if not u or u.startswith("#") or weblike.match(u): continue
               sm = scheme.match(u)
               if sm and sm.group(1).lower() != "http": continue   # mailto:, tel:, ethereum:, data:, ...
               p = u if u.startswith("/") else os.path.normpath(os.path.join(os.path.relpath(d, root), u))
               if not built(p): dead[p] = dead.get(p, 0) + 1
   print(f"{len(dead)} dead internal href targets, {sum(dead.values())} occurrences")
   for t, n in sorted(dead.items(), key=lambda kv: -kv[1]): print(f"  {n:5d}  /{t}")
   PY
   ```

   It prints `0 dead internal href targets, 0 occurrences`, and that number is meaningful only because the
   controls say so: `/fdroid`, `/downloads`, `/docs/glossary.html` and `/de/fdroid` each resolve, a made-up
   `/no-such-page-xyz` does not. There is no broken-link check in the build itself - nothing in `website/`
   prints a `Broken link:` line - so this scan is the only measurement.

   **The snippet as first written here was inert.** It skipped a target with `u.lower().startswith(skip)`
   over a tuple that ended in `""`, and `startswith("")` is true for every string, so every href was skipped,
   nothing was ever tested, and the scan could only ever report 0 - which is exactly what it reported while
   real dead links existed. The guard above names the schemes instead (`mailto:`, `tel:`, `data:`,
   `javascript:`, and the cryptocurrency URIs the donation pages use are not internal targets) and keeps the
   host-relative ones (`//…`) out. Run the controls whenever you change it: a green 0 with no positive
   control passing is a broken scanner, not a clean site.

3. **Upstream-operated destinations still linked:** `github.com/simplex-chat` 101 occurrences in 35 files,
   donation links 58 in 30, TestFlight 8 in 8, F-Droid wording 337 in 39. The app-link page the relay
   serves goes further: it links upstream's TestFlight join code, upstream's APK asset and upstream's
   donation page, and its Google Play button carries the title "Public iOS preview on TestFlight".
4. **One build reach outside the tree:** `.eleventy.js:87` reads `../docs/GLOSSARY.md` unconditionally and
   that file is not in this fork; `../docs/LINKS.md` (line 18) is already guarded by `existsSync`. Either
   write our own glossary or guard the read.

## Naming to apply while editing

- The iOS product is named **POPOPX** (ruling 2026-11-16). Its App Store record
  `https://apps.apple.com/us/app/popopx-chat/id6799146157` does not resolve: `itunes.apple.com/lookup`
  answers `resultCount: 0` for us/cn/jp and the web page 404s. **Ruling (i) of 2026-11-16: no App Store,
  Google Play or APK badge or link is rendered by this site until each record resolves** - the number
  stays here as the record, and must not go back into a template until `lookup` returns a row.
- Android applicationId `com.popopxchat.popopx`; its Play listing 404s, we publish no APK and run no
  F-Droid repository, so a link to any of the three would be a link to upstream's build.
  **Ruling of 2026-11-16 (#129): the F-Droid badge is gone, our `/fdroid/` page stays.** The artwork carries
  the literal text "GET IT ON F-Droid" while the page it opened is titled "POPOPX is not on F-Droid", so the
  two contradicted each other and the badge was the false half. Deleted as one unit: the badge rows in
  `_includes/hero.html`, `_includes/sections/join_simplex.html`, `contact_page.html` (2 rows) and
  `file.html`, the `.f-droid-btn` anchor and its `f_droid_icon.svg` preload in `index.html`, the
  store-badge block in `js/script.js`, the >=1016px `display:flex !important` rules in `css/design3.css`,
  the `index-f-droid-title` key in all 24 locale files and `downloads-fdroid-repo` in its 6 holders. The
  link text is now the new `downloads-not-on-fdroid` ("Not on F-Droid — why") pointing at `/fdroid/` from
  `downloads.html` and `_includes/downloads_hero.html`; where the badge sat inside a sentence the sentence
  stays and the anchor goes, so `contact_page.html` (2 rows) and `file.html` now render only `get-simplex`
  as plain text, and `channel-preview.jsc`'s `renderAppBadges`
  emits a single `https://popopx.chat/downloads` anchor inside the unchanged `simplex-preview-badges`
  container, because the CSS keys on that class name.
  Two couplings had to move with the markup. `js/design3.js`'s `initializePage()` queried the button that
  was being removed, and its early return would have switched off the communities strip
  (`showPromotedGroups()`) on every homepage without any error; `js/script.js`'s load-time block was
  already inert (it un-hid classes no template emitted) but would have re-displayed store badges had any
  anchor survived, so it is deleted rather than left as a live hazard.
  Measured on the rebuilt tree (308 pages): `f-droid-btn`, `apple-store-btn`, `google-play-btn`,
  `f_droid_icon.svg`, `BADGE_FDROID`, `index-f-droid-title` and `downloads-fdroid-repo` all 0 occurrences;
  all 25 homepages still carry `.desktop-app-btn`, so the guard passes and the strip still runs; the only
  two surviving `f_droid.svg` strings are the `sodipodi:docname` metadata inside the asset files
  themselves - 0 references from any page or script (control: `desktop-app-btn` = 26 files by the same
  grep), and the files are kept because `ARTWORK.md:80` and `branding/MANIFEST.tsv:63/213/214` are their
  other readers, so their orphan status is #124's to settle, not this ruling's. The 250 "F-Droid
  repository" strings are `/fdroid/`'s own denial prose across its 25 pages and their `.md` mirrors, held.
  **Follow-up the same day: `/fdroid/` got a homepage route back.** Deleting the badge left the denial page
  reachable only from `/downloads/`, so the hero now carries a text link rather than artwork - a
  `<p class="cover-note">` in `src/index.html` after the lead paragraph, labelled by the existing
  `downloads-not-on-fdroid` key (the i18n filter falls back per key, so the single English value renders in
  all 24 locale dirs; no translations were invented). Three things about that placement are load-bearing:
  it is a *sibling* of `.cover-stats`, never a child of `.socials`/`.cover-stats`/`.security-btns`, because
  a ResizeObserver in `index.html` writes those overlays' `offsetWidth` into `--cover-socials-w` /
  `--cover-stats-w` and the sale-banner transform consumes the first, so markup inside them moves the hero;
  its size is set in `css/design3.css` (`--sec-vwu` × 1.55 desktop, × 2.9 mobile - the same ~72% of the lead
  paragraph in both) and not with `text-sm`, because `section.cover div.content p` (0,2,3) and its
  `html:not(.dark)` twin (0,3,4) outrank any Tailwind utility (0,1,0); and the underline is explicit because
  preflight makes links inherit their colour. Measured on the rebuilt tree: 25 files carry
  `class="cover-note"` (24 locale dirs + root), the href is `/fdroid` for root and `/<lang>/fdroid` for the
  locales, the badge residue above is still 0, the corrected link scan is still
  `0 dead internal href targets, 0 occurrences`, and desktop light/dark plus mobile light renders show the
  line below the lead with nothing colliding.
- The fork and app are POPOPX / POPOPX Chat; "SimpleX Messaging Protocol", "SMP" and the relay hosts
  SimpleX Chat Ltd operates keep their own names.
- Connection links open the app through the `popopx:` scheme (`popopxchat:` and the inherited
  `simplexchat:` are app-link schemes only) - read from `media/contact.js` and
  `apps/multiplatform/spec/client/navigation.md`.

## The four link paths that are not website content

`/a`, `/c`, `/g`, `/i` are claimed by the apps' `autoVerify` / AASA path lists but are served by the
**relay**, from `popopxmq:apps/common/Web/static/link.html` (already rebranded to POPOPX, 23 of its own
strings). Reference copies of it, its `media/`, upstream's `contact.html` / `invitation.html` /
`contact_page.html` / `contact.js` / `qrcode.js` and upstream's five `.well-known` files are stored in
`/Users/elliot/popopx-chat/site-link-sources/` with `MANIFEST.tsv` recording sha256 and source path.

---

# Running the website

## Build

```sh
cd website && npm install          # Node >= 20; ~507 packages
cd .. && bash build.sh             # -> website/_site
```

`build.sh` is the whole pipeline (a clone of upstream's `website/web.sh` without the
`npm install` line). It does, in order: `copy_sources.js` (copies repo-level `docs/`,
`blog/`, `images/`, `PRIVACY.md` into `website/src/`, silently skipping any that are
absent), the `lottie`/`ethers`/`xftp-web` runtime copies, `merge_translations.js`
(generates `translations.json`, which `.eleventy.js` `require`s), the per-language
directory copies, `cpp` preprocessing of `src/js/*.jsc`, then `npm run build`
(`build:js` + `eleventy` + `tailwindcss`). The language directories are removed again
at the end, so a second build starts clean.

`NODE_OPTIONS=--max-old-space-size=4096` is load-bearing: Eleventy OOMs on the default
2 GB heap with this many pages x 23 languages.

Verified **2026-11-16** on this tree: exit 0, **244 HTML pages / 881 files**, 22
language directories.

## Serve locally

```sh
cd website && npx eleventy --serve        # http://localhost:8080
# or, against an existing build:
python3 -m http.server -d _site 8080
```

The static output is complete; any static host works. Two things only work over HTTPS
with the real origin, so they cannot be exercised on localhost: the mobile deep-link
handoff (`.well-known` verification, below) and the `/contact` `/invitation` pages'
`popopx:/…` URI anchors, which need a POPOPX app installed.

## Deploy

Publish `_site` at the root of **`https://popopx.chat`**. The `.well-known` files are
part of `_site` (passthrough copy of `src/.well-known`) and are what makes app links
work; each has a content-type condition, see `.well-known/README.md` in the deployment
directory for the nginx rule and the post-deploy `curl` checks.

Note which paths the apps claim but this site does **not** serve: `/a`, `/c`, `/g`, `/i`
are answered by the relay (`popopxmq:apps/common/Web/static/link.html`, served by
`chat-relay` on its own origin), not by the website. `/contact` and `/invitation` **are**
website pages. Reference copies of both sides are in `../site-link-sources/`.

## What this build does not contain

- `/docs/**`, `/blog/**` and `/llms-full.txt` - their inputs are upstream's editorial
  text, which the fork deleted by ruling. `src/llms/llms-full.njk` is therefore renamed
  `llms-full.njk.off`; the other `src/llms/*` pages (robots, sitemap, facts, agents,
  answers, timeline, docs index) do build.
- Glossary tooltips are inert. `.eleventy.js:88` reads `../docs/GLOSSARY.md`
  unconditionally, and `docs/GLOSSARY.md` here is a one-line placeholder, so the 31
  terms in `website/src/_data/glossary.json` resolve to themselves. Real definitions are
  required before publishing.
- `website/src/img/**` is 334 upstream brand images, unreplaced - see the blockers above.
- The crowdfunding campaign is deleted (ruling 删除众筹): `src/crowdfunding.html`,
  `src/wefunder.html`, `src/llms/wefunder.njk`, `src/_includes/llms/wefunder.md`,
  `src/_includes/blog_previews/20260820.html` and `src/img/crowdfunding/` (18 files,
  the pitch deck among them) are gone, with every link to them removed from
  `index.html`, `navbar.html`, `footer.html`, `utm.js`, `downloads_hero.html`,
  `markdown_pages.js`, `_data/llms_facts.json`, the `llms/*` includes, `token.md` and
  `langs/*.json`. `/credits` and `/llms/answers` now state that there is no campaign.

# Changes made in this repo relative to the extracted tree

Everything below is a deliberate edit, not upstream's bytes; `git log` on the initial
commit shows them as one unit.

1. `website/src/.well-known/assetlinks.json` replaced with the file verified against
   `AndroidManifest.xml` + our release certificate. The extracted copy carried **our**
   `package_name` with **upstream's three signing fingerprints** (Play, the GitHub APK,
   F-Droid), which would have made Android link verification accept only APKs signed by
   SimpleX Chat Ltd's keys and asserted an authorization we do not hold. Ours lists the
   one fingerprint of the key we actually sign with.
2. `website/src/.well-known/apple-app-site-association` replaces upstream's
   `apple-app-site-association/index.json` directory form: same 12 `components` and the
   same `PDBA6XRBQT.com.popopxchat.popopx` appID, but served under the exact name Apple
   requests. Upstream used the directory form only because GitHub Pages cannot set a
   header per path; on nginx use `default_type application/json` for it.
3. Deleted `website/src/.well-known/nostr.json` (upstream's Nostr identity and relays)
   and `org.flathub.VerifiedApps.txt` (upstream's Flatpak app-id verification token).
   Both are per-origin authorizations for things SimpleX Chat Ltd operates; serving them
   from popopx.chat claims their verification on our origin and does nothing for us.
   `simplex.json` is kept emptied - its path is an RFC 8615 protocol value, so the name
   cannot move.
4. `website/src/llms/llms-full.njk` -> `llms-full.njk.off`, because it assembles
   `src/docs/{WHY,SIMPLEX,FAQ,protocol/*}.md`, trees that no longer exist in the fork.
5. `build.sh` added; `.gitignore` added for the generated trees.
 (Seed the popopx.chat site from this fork's rebranded website tree)

# Automated updates

`.github/workflows/deploy.yml` runs on every push to `main`: `npm ci` -> `build.sh` ->
a guard that the build produced >200 pages **and** that both link-verification files are
present with our `package_name` / `appID` -> uploads a `site` artifact -> force-publishes
`_site` to the `gh-pages` branch -> and POSTs to the deploy hook when one is configured.

Two ways the built site reaches the host; they are not alternatives, use either or both.

1. **Nothing to configure.** Enable Pages on the repo (Settings -> Pages -> Source:
   `gh-pages` branch) and `https://popopx-chat.github.io/popopx.chat-web/` updates itself
   on every push. This is a preview only: the mobile apps verify links against
   `popopx.chat`, so deep links stay inert until the same content is served there.
2. **The real host.** Set two repository secrets and the last step fires automatically:

   ```sh
   gh secret set DEPLOY_WEBHOOK_URL      --repo popopx-chat/popopx.chat-web   # https://<host>/popopx-deploy
   gh secret set DEPLOY_WEBHOOK_SECRET   --repo popopx-chat/popopx.chat-web   # a shared random string
   ```

   The receiver on the server gets `{"ref":"main","sha":…,"run":…}` with header
   `x-popopx-signature: sha256=<hmac-sha256 of the raw body, keyed by DEPLOY_WEBHOOK_SECRET>`.
   It must verify the HMAC before acting, then pull the commit and swap the document root:

   ```sh
   # /usr/local/bin/popopx-deploy  (nginx document root -> /var/www/popopx.chat-web)
   git -C /var/www/popopx.chat-src fetch --quiet origin gh-pages
   git -C /var/www/popopx.chat-src reset --hard --quiet origin/gh-pages
   rsync -a --delete --exclude=.git/ --exclude=.well-known/acme-challenge/ \
       /var/www/popopx.chat-src/ /var/www/popopx.chat-web/
   ```

   `--delete` is not cosmetic: the docroot accumulated pages this build no longer emits
   (`/crowdfunding/`, `/blog/`, `/news/`, `/livestream/`, `/wefunder/`), and without it
   they stay published next to the new ones. Run the same command with `-n -i --delete`
   first and read the deletion list before you drop `-n`.

   Serve `/var/www/popopx.chat-web` with the `.well-known` content-type rule in
   `website/src/.well-known/README.md`; without `default_type application/json` for
   `apple-app-site-association`, iOS rejects the response and no link opens in the app.

A repository *webhook* (Settings -> Webhooks, or `gh api repos/popopx-chat/popopx.chat-web/hooks -f url=… -f content_type=json -f 'events[]=push' -f secret=…`)
is the same idea without Actions: GitHub POSTs the push event straight to the host. Prefer
the workflow, because it builds first and never publishes a red build; register a raw
webhook only if the host should learn about a push before Actions finishes.

## Deploying on CentOS (the popopx.chat host)

Measured on the host (2026-11-16): the nginx document root is **`/var/www/popopx.chat-web`**
and there is no `/srv` directory. The gh-pages checkout that the units below pull is a
*separate* directory (`/var/www/popopx.chat-src`) so that the docroot never holds a `.git`.

The host answers `server: nginx/1.14.1` and `x-powered-by: PHP/7.2.24`, which is the
EPEL/Remi combination of **CentOS 7 / RHEL 7**. That matters for one decision: **do not
build the site on the server.** EL7 is past its maintenance window and has no Node 20
package, while this build needs Node >= 20 (Eleventy 1.x + Tailwind 3.3). Build in GitHub
Actions (or on a workstation) and ship only the static `_site`.

### Option A - push the build from a workstation (nothing on the server has to reach GitHub)

This is the shortest path and the one to use for the first deploy: build locally, ship the
static tree over ssh. `website/_site` is the whole site; nginx needs no restart for it.

```sh
bash build.sh
rsync -an -i --delete --exclude=.well-known/acme-challenge/ website/_site/ root@<host>:/var/www/popopx.chat-web/
#   ^ dry run: read the deletion list. It should name the upstream-era pages
#     (crowdfunding/, blog/, news/, livestream/, wefunder/, old docs/*) and nothing else.
rsync -a  --delete --exclude=.well-known/acme-challenge/ website/_site/ root@<host>:/var/www/popopx.chat-web/
```

Keep `--exclude=.well-known/acme-challenge/` in every variant: that is where Certbot puts
its HTTP-01 tokens, and `--delete` without it revokes your ability to renew.

Then verify from outside (a `200` for a page you deleted means the old tree is still being
served - something else writes into that docroot):

```sh
for p in / /downloads/ /crowdfunding/ /blog/; do
  printf '%-16s %s\n' "$p" "$(curl -sS -o /dev/null -w '%{http_code}' https://popopx.chat$p)"
done
```

### Option B - the server pulls `gh-pages` (timer or webhook)

One-time setup, as root:

```sh
yum install -y nginx rsync git policycoreutils-python python3        # EPEL already present
useradd -r -s /sbin/nologin -G nginx webdeploy
mkdir -p /opt/popopx /var/www/popopx.chat-web /var/www/popopx.chat-src /etc/popopx /var/log
git clone --depth 1 -b gh-pages https://github.com/popopx-chat/popopx.chat-web.git /var/www/popopx.chat-src
install -m 0644 deploy/nginx/popopx.chat.conf /etc/nginx/conf.d/
install -m 0755 deploy/receiver.py /opt/popopx/deploy/receiver.py   # mkdir -p /opt/popopx/deploy first
install -m 0644 deploy/systemd/*.service deploy/systemd/*.timer /etc/systemd/system/
umask 077; head -c 32 /dev/urandom | openssl base64 > /etc/popopx/deploy_secret
chown root:webdeploy /etc/popopx/deploy_secret && chmod 640 /etc/popopx/deploy_secret
echo 'webdeploy ALL=(root) NOPASSWD: /usr/bin/systemctl start popopx-sync.service' > /etc/sudoers.d/popopx-deploy
visudo -cf /etc/sudoers.d/popopx-deploy
printf '# deployed from %s\n' "$(cat /var/www/popopx.chat-src/.git/HEAD)" >/dev/null   # sanity
rsync -an -i --delete --exclude=.git/ --exclude=.well-known/acme-challenge/ \
    /var/www/popopx.chat-src/ /var/www/popopx.chat-web/              # READ the list, then:
rsync -a  --delete --exclude=.git/ --exclude=.well-known/acme-challenge/ \
    /var/www/popopx.chat-src/ /var/www/popopx.chat-web/
```

`/var/www` is the standard labelled location, so SELinux is unlikely to bite here; it bites
when the docroot is moved somewhere else. The symptom is a `403` that looks like a
permissions bug, and the fix is:

```sh
semanage fcontext -a -t httpd_sys_content_t "/var/www/popopx\.chat-web(/.*)?"
restorecon -RFv /var/www/popopx.chat-web
setsebool -P httpd_can_network_connect 1        # nginx -> 127.0.0.1:8099 proxy
getenforce                                       # Enforcing
```

Then start everything and check the two files every mobile OS fetches:

```sh
systemctl enable --now nginx popopx-deploy popopx-sync.timer
nginx -t && systemctl reload nginx
firewall-cmd --permanent --add-service=https --add-service=http && firewall-cmd --reload
curl -sSI https://popopx.chat/.well-known/assetlinks.json            | sed -n '1p;/content-type/Ip'
curl -sSI https://popopx.chat/.well-known/apple-app-site-association | sed -n '1p;/content-type/Ip'
```

Both must be `200` with `Content-Type: application/json`. A `404` means the file is not
in the document root; a `403` is SELinux; `application/octet-stream` on the AASA means
the `default_type` block was not reloaded. The same two probes must also be made against
**`www.popopx.chat`**, because `apps/ios/POPOPX (iOS).entitlements` claims
`applinks:popopx.chat` *and* `applinks:www.popopx.chat` while Android's `autoVerify`
claims only `popopx.chat` - so the AASA is needed on both hosts and `assetlinks.json`
only on the bare one.

### Current live state (measured 2026-11-16, with the command that measures each)

`bash build.sh` prints the tree it produced (currently `OK: 237 html pages, 834 files`),
and the deploy workflow publishes exactly that, so the `gh-pages` branch tracks the build -
re-measure it rather than trusting a stored number:

```sh
git ls-tree -r --name-only origin/gh-pages | wc -l
git ls-tree -r --name-only origin/gh-pages | grep -cE '^(crowdfunding|blog|news|livestream|wefunder)/'
```

Measured 2026-11-16: 838 files at the last publish (the 4-file difference is the orphan CSS
this build no longer emits) and **0** of `crowdfunding/ blog/ news/ livestream/ wefunder/`.
So the branch is right.

What `popopx.chat` serves is only partly that branch:

| Probe (`curl -sSI`) | Live | Expected |
|---|---|---|
| `/.well-known/assetlinks.json` | 200, 399 B, `content-type: application/json`, contains `com.popopxchat.popopx` (and not `chat.simplex.app`) | ours - correct |
| `/.well-known/apple-app-site-association` | 200, 778 B, `content-type: application/json` | ours - correct |
| `/` | 200, 77346 B, `<title>POPOPX Chat: private and secure messenger…` | correct |
| `/crowdfunding/` | **200**, 85010 B, `<title>Invest in SimpleX Chat` | **410** - gone from the build |
| `/blog/`, `/news/`, `/livestream/`, `/wefunder/` | **200** | **410** |
| `/docs/glossary.html` | 200, 55676 B, **empty** title | 200, 71447 B, `Glossary - POPOPX Chat` |
| `/api/`, `/api/health`, `/.git/config`, `/receiver.py` | 404 | correct (no badge backend deployed) |

The docroot therefore holds an **older published tree alongside** our files, and `--delete`
is what removes it. Do it deliberately: run the sync with `-n -i --delete`, check that the
listed removals are exactly those upstream-era paths, then run it for real. If something on
the host republishes the old tree (a cron or an older service writing into
`/var/www/popopx.chat-web`), find it before you delete, or the pages come back -
`last-modified` on the live `/crowdfunding/` was *after* our 2026-11-16 deploys, which is
how this was spotted.

### Updating after a push

Nothing on the server watches GitHub unless you point it there. Two options, either is
fine and they can both be on:

- **Timer only (no inbound port, nothing to secure):** `popopx-sync.timer` pulls
  `gh-pages` every 15 minutes. A push is live within 15 minutes with zero attack surface.
- **Webhook receiver:** the `Notify the host` step in `.github/workflows/deploy.yml`
  POSTs an HMAC-signed body to `http://127.0.0.1:8099` through nginx; expose it as
  `location = /popopx-deploy { proxy_pass http://127.0.0.1:8099; access_log off; }` in the
  443 server block, then `gh secret set DEPLOY_WEBHOOK_URL --repo popopx-chat/popopx.chat-web`
  with that URL and `DEPLOY_WEBHOOK_SECRET` with the contents of `/etc/popopx/deploy_secret`.
  The receiver verifies the signature before it is allowed to start the sync unit, and
  does nothing else.

To change what is deployed, edit this repository and push to `main`; never edit
`gh-pages` by hand - the workflow force-publishes it, so manual commits there are lost.
