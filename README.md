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
2. **Editorial content is deliberately absent.** `src/docs/`, `src/blog/`, `src/plans/` and `src/langs/`
   do not exist in this tree - they lived at the repository root and were removed by ruling. So every
   link the templates still make to `/blog/` (5), `/docs/` (11) and `/downloads` (4) is a 404 on our host.
3. **Upstream-operated destinations still linked:** `github.com/simplex-chat` 101 occurrences in 35 files,
   donation links 58 in 30, TestFlight 8 in 8, F-Droid wording 337 in 39. The app-link page the relay
   serves goes further: it links upstream's TestFlight join code, upstream's APK asset and upstream's
   donation page, and its Google Play button carries the title "Public iOS preview on TestFlight".
4. **One build reach outside the tree:** `.eleventy.js:87` reads `../docs/GLOSSARY.md` unconditionally and
   that file is not in this fork; `../docs/LINKS.md` (line 18) is already guarded by `existsSync`. Either
   write our own glossary or guard the read.

## Naming to apply while editing

- The iOS product is named **POPOPX** (ruling 2026-11-16), store record
  `https://apps.apple.com/us/app/popopx-chat/id6799146157` - that URL is the one already used by this fork.
  The record's live title could not be read from this network: the request is redirected to
  `https://apps.apple.com/cn/iphone/today`, which also means the app is not yet publicly reachable here.
- Android applicationId `com.popopxchat.popopx`; we publish no APK and run no F-Droid repository, so a
  link to either would be a link to upstream's build.
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
- `src/wefunder.html`, `src/crowdfunding*.html` and `src/llms/wefunder.njk` still
  advertise a crowdfunding campaign that no longer exists in the app (ruling 删除众筹).

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
   # /usr/local/bin/popopx-deploy  (nginx document root -> /srv/popopx.chat)
   git -C /srv/popopx.chat-web fetch --quiet origin gh-pages
   git -C /srv/popopx.chat-web reset --hard --quiet origin/gh-pages
   rsync -a --delete /srv/popopx.chat-web/ /srv/popopx.chat/
   ```

   Serve `/srv/popopx.chat` with the `.well-known` content-type rule in
   `website/src/.well-known/README.md`; without `default_type application/json` for
   `apple-app-site-association`, iOS rejects the response and no link opens in the app.

A repository *webhook* (Settings -> Webhooks, or `gh api repos/popopx-chat/popopx.chat-web/hooks -f url=… -f content_type=json -f 'events[]=push' -f secret=…`)
is the same idea without Actions: GitHub POSTs the push event straight to the host. Prefer
the workflow, because it builds first and never publishes a red build; register a raw
webhook only if the host should learn about a push before Actions finishes.

## Deploying on CentOS (the popopx.chat host)

The host answers `server: nginx/1.14.1` and `x-powered-by: PHP/7.2.24`, which is the
EPEL/Remi combination of **CentOS 7 / RHEL 7**. That matters for one decision: **do not
build the site on the server.** EL7 is past its maintenance window and has no Node 20
package, while this build needs Node >= 20 (Eleventy 1.x + Tailwind 3.3). Build in GitHub
Actions (or on a workstation) and ship only the static `_site`.

One-time setup, as root:

```sh
yum install -y nginx rsync git policycoreutils-python python3        # EPEL already present
useradd -r -s /sbin/nologin -G nginx webdeploy
mkdir -p /opt/popopx /srv/popopx.chat /srv/popopx.chat-src /etc/popopx /var/log
git clone --depth 1 -b gh-pages https://github.com/popopx-chat/popopx.chat-web.git /srv/popopx.chat-src
install -m 0644 deploy/nginx/popopx.chat.conf /etc/nginx/conf.d/
install -m 0755 deploy/receiver.py /opt/popopx/deploy/receiver.py   # mkdir -p /opt/popopx/deploy first
install -m 0644 deploy/systemd/*.service deploy/systemd/*.timer /etc/systemd/system/
umask 077; head -c 32 /dev/urandom | openssl base64 > /etc/popopx/deploy_secret
chown root:webdeploy /etc/popopx/deploy_secret && chmod 640 /etc/popopx/deploy_secret
echo 'webdeploy ALL=(root) NOPASSWD: /usr/bin/systemctl start popopx-sync.service' > /etc/sudoers.d/popopx-deploy
visudo -cf /etc/sudoers.d/popopx-deploy
printf '# deployed from %s\n' "$(cat /srv/popopx.chat-src/.git/HEAD)" >/dev/null   # sanity
rsync -a --delete /srv/popopx.chat-src/ /srv/popopx.chat/
```

SELinux is what actually breaks a first deploy on CentOS: a document root outside
`/var/www` is not readable by nginx until it is labelled, and the symptom is a `403`
that looks like a permissions bug.

```sh
semanage fcontext -a -t httpd_sys_content_t "/srv/popopx\.chat(/.*)?"
restorecon -RFv /srv/popopx.chat
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
