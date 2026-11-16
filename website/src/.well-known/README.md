# .well-known

These two files let POPOPX Chat links (one-time invitations, contact addresses, groups) open in the
mobile app instead of the browser. They must be served from **`https://popopx.chat`** — the origin a
mobile OS checks is the one named in the app, so a copy on any other host does nothing.

## Where every value comes from

Neither file was written by hand; each value was read from the build that consumes it.

| Value | Source |
| --- | --- |
| `package_name` `com.popopxchat.popopx` | `apps/multiplatform/android/build.gradle.kts:15` (`applicationId`) |
| `sha256_cert_fingerprints` | the release certificate `CN=com.popopxchat.popopx`, `openssl x509 -noout -fingerprint -sha256` |
| `appIDs` `PDBA6XRBQT.com.popopxchat.popopx` | the application target's `PRODUCT_BUNDLE_IDENTIFIER` (Debug and Release both) in `apps/ios/POPOPX.xcodeproj/project.pbxproj`, plus our Apple team id |
| the six path shapes and their prefixes | `apps/multiplatform/android/src/main/AndroidManifest.xml:110-121` (`android:path` / `android:pathPrefix`) and `apps/ios/Shared/ContentView.swift:484` |

The fingerprint list has **one** entry. Upstream's file lists three (Play Store, the APK in GitHub
releases, F-Droid) because those are three different signing keys; we have one release key and
publish no APK, so naming the other three would assert an authorization we do not hold. When we sign
a Play upload with a second key, its fingerprint is added here - until then Android link verification
only works for an APK signed by the key above.

The manifest's `autoVerify` block also names `smp4.simplex.im` … `smp19.simplex.im`. Those are relays
operated by SimpleX Chat Ltd; their `assetlinks.json` is theirs to serve, not ours, and nothing in
this directory affects them. `www.popopx.chat` is claimed by the iOS entitlements but not by the
Android manifest, so only `popopx.chat` needs the Android file.

## Serving them

Both files are plain static content, but each has a condition its reader enforces:

- **`assetlinks.json`** - served with any JSON content type; Digital Asset Links fetches it over HTTPS
  and follows redirects.
- **`apple-app-site-association`** - Apple requires `Content-Type: application/json` (charset allowed)
  and rejects a response that is not JSON. nginx gives an extensionless file
  `application/octet-stream`, so name it explicitly:

  ```nginx
  location = /.well-known/apple-app-site-association {
      default_type application/json;
  }
  ```

  (Upstream's site kept this file as `apple-app-site-association/index.json` instead, because GitHub
  Pages cannot set a header per path. This host is nginx, so the direct name is used and no redirect
  is involved.)

Check after deploying - both must answer 200 with a JSON body and the header shown:

```sh
curl -sSI https://popopx.chat/.well-known/apple-app-site-association | sed -n '1p;/content-type/Ip'
curl -sSI https://popopx.chat/.well-known/assetlinks.json            | sed -n '1p;/content-type/Ip'
```

Measured **2026-11-15**: both still return `404`, while `https://popopx.chat/` returns 200 - the files
exist only in this directory until they are deployed. TLS covers `popopx.chat` and `www.popopx.chat`.

## What this host answers today (re-measured 2026-11-16, direct egress)

| Probe | Result |
| --- | --- |
| `https://popopx.chat/` and `https://www.popopx.chat/` | `200`, both resolve to one address, `server: nginx/1.14.1`, `x-powered-by: PHP/7.2.24` |
| `/.well-known/assetlinks.json` on both hosts | `404` |
| `/.well-known/apple-app-site-association`, `.json`, `/apple-app-site-association`, `/.well-known/assetlinks` | `404` - nothing of this kind is served under any spelling |
| `/.well-known/security.txt`, `/robots.txt`, `/sitemap.xml`, `/.env` | `404` - so a hidden-directory rule cannot be told apart from absence; if the files land and still answer `404`, look for `location ~ /\.` in the nginx config before changing the files |

Both hosts need the AASA, not just one: `apps/ios/POPOPX (iOS).entitlements` claims
`applinks:popopx.chat` **and** `applinks:www.popopx.chat`, while the Android manifest's `autoVerify`
claims only `popopx.chat`. So the deployment is two files on `popopx.chat` and one on `www.popopx.chat`.

This directory is **not** the deployed site: the live page is an 18 KB PHP-rendered document, this
`index.html` is 52 KB. Publishing these files says nothing about the rest of this directory, and the
live page already renders POPOPX branding (its only `SimpleX` string is "SimpleX Messaging Protocol",
the protocol's own name, which is ruled keep).
