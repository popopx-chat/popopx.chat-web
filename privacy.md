# Privacy

This is POPOPX's own document. It is not a translation or a copy of SimpleX Chat Ltd's privacy
policy - [their policy is theirs](https://simplex.chat/privacy/) and describes the service they
operate. POPOPX distributes a fork of the SimpleX Chat application and this site; the rest of this
page describes what **we** do and what **the application you download here** sends.

## Who publishes this

**POPOPX**, contact **chat@popopx.chat**. This site (`popopx.chat`) and the source repositories under
[`github.com/popopx-chat`](https://github.com/popopx-chat) are ours. The upstream project, its
relays and its blog are operated by SimpleX Chat Ltd; where a page here links to their material we
say so and link to their site rather than claiming it.

## This website

- It is a static site: pre-built HTML, CSS and images served by nginx. There are no accounts, no
  sign-up or contact forms, no search, no server-side code and no database behind these pages.
- It sets **no cookies** and makes no third-party analytics request. The upstream build sent a
  page-view beacon to `api.simplex.chat`; we removed it, and the published pages contain no
  reference to any analytics endpoint.
- It uses browser storage twice: your light/dark **theme choice** (`localStorage`) and, if you
  arrived through a `utm_source`/`utm_campaign` link, those **campaign tags** for the rest of the
  browsing session (`sessionStorage`) so download links keep them. Nothing is sent anywhere from
  either; clearing your browser storage removes both.
- nginx serves these files and keeps its standard access log (requested path, IP address, user
  agent, referrer). We add no other collection on the server side.
- Some pages link to upstream's blog posts, audit reports and documentation on `simplex.chat`.
  Once you follow such a link you are on their site, under their policy.

## The application

The protocol carries no profile: there is no account, no phone number, no email address and no
contact graph on any server. Message routing metadata is separated per connection, so no single
server the app talks to learns both who you talk to and what you say. The protocol-level detail is
upstream's own document, published here unmodified as [docs/SIMPLEX.md](https://popopx.chat/docs/simplex.md); the
security document is likewise theirs - [docs/SECURITY.md](https://popopx.chat/security/index.html) - so the report address
and the OpenPGP fingerprint it names are SimpleX Chat Ltd's, not ours. Report a POPOPX issue to
**chat@popopx.chat**.

The iOS and Android builds bundle no analytics or crash-reporting SDK - no Firebase, Sentry,
Segment or equivalent appears in the app dependency manifests - and no push service is used to
deliver messages, so a message is only ever stored on the relays your app is configured against.
If a future release adds either, it is described here before it ships.

## The servers the app is configured to use on first run

They are **third parties**. The fork inherits one preset operator, unchanged from upstream:

| Operator (trade name) | Legal name in source | Domains | Consent |
|---|---|---|---|
| SimpleX Chat | SimpleX Chat Ltd | `simplex.im` | the app requires you to accept *their* conditions before using these relays |

POPOPX operates no relays of its own, so it cannot offer its own terms in their place. Operator
names, their legal names, the relay addresses and the consent requirement are one decision in the
source - they move together, never one at a time.

A second set of relay addresses (`smp://…@smpN.simplexonflux.com`) remains in the source for one
reason only: previously issued short links encode the host they were created on, so removing those
entries would make other people's links unresolvable. InFlux Technologies Limited **is not an
operator of this fork** - it is not offered, not described and not linked from the app, and no
traffic is configured to it on first run.

## What POPOPX holds

Nothing. This project publishes no backend for user data, no push gateway, no update server and no
telemetry collector. If POPOPX later operates the link-unfurling proxy, the badge service, the
directory, an F-Droid/APK distribution endpoint or a push gateway, each of them gets a section here
describing what it stores and for how long, before it is enabled in the app.

## Contact

**chat@popopx.chat** - privacy and security contact for this fork and this site.
