# POPOPX website artwork

Everything under `website/src/img/` that carried SimpleX brand artwork was
redrawn as POPOPX artwork and installed **in place**, so no template, CSS rule
or translation needed a path change. The licence reason is in
[`ASSETS_LICENSE.md`](ASSETS_LICENSE.md): upstream's artwork is not AGPL, it is
a separate proprietary grant that a rebrand voids — so a fork that renames the
product must not keep the pictures.

`git log --oneline -- website/src/img | head` shows the commits that installed them;
this file is the method, the gate and the holds. The per-file truth is
[`MANIFEST.tsv`](MANIFEST.tsv) (315 rows: path, original pixel size, class,
status, master, bytes — regenerate it with `tools/manifest_img.py`).

## Reference commit

`9839bd1` — the last commit in which **every** file under `website/src/img/` was
byte-identical to upstream. Every tool here takes it as `REF` (override:
`python3 tools/audit_img.py <ref>`), and "replaced" always means *digest differs
from REF*, never "looks different".

## Method

1. **Masters** live in `branding/source-svg/`, named by the target's path
   relative to `website/src/img` with `/` escaped as `__`. Raster targets get a
   `<escaped>.src.svg` master; SVG targets get the escaped path as-is. So
   `hero/light/2fps/frame_0001.png` ← `hero__light__2fps__frame_0001.png.src.svg`
   and `icons/popupx.svg` ← `icons__popupx.svg`.
2. **`tools/map_masters.py`** derives the mapping by unescaping, and reports
   `unresolved` / `ambiguous` rather than guessing. It writes `/tmp/imgmap.json`,
   which the installer and the manifest both read — regenerate it after adding
   masters; it is not committed.
3. **`tools/install_assets.py`** is the single installer. It routes by target
   extension, renders SVG masters with the local renderer, converts to WebP
   where the target is WebP, and **refuses** any target whose digest already
   differs from REF (see the trap below). Render geometry comes from the target,
   so output size matches the original pixel size.
   The renderer is `/Users/elliot/popopx-chat/tools/r7/svg2png` (a Swift
   `CoreSVG`-style converter; `swiftc -o svg2png svg2png.swift` rebuilds it).
   It encodes JPEG only for `.jpg`/`.jpeg` and PNG otherwise — it cannot write
   WebP, which is why the WebP step is separate.
4. **`tools/audit_img.py`** is the delivery gate. **`tools/manifest_img.py`**
   regenerates `MANIFEST.tsv`.

Run them in this order:

```
python3 tools/map_masters.py
python3 tools/install_assets.py --plan          # dry run: what would move, and why not
python3 tools/install_assets.py
./build.sh                                      # the real entrypoint, not npm run build
python3 tools/audit_img.py
python3 tools/manifest_img.py
```

## Gate

`audit_img.py` fails the tier unless all of these hold:

- magic bytes match the extension (a PNG payload in a `.jpg` name is a broken
  asset even though it displays in most browsers);
- full-size decode succeeds for every raster we installed;
- pixel dimensions equal the REF bytes' dimensions — nothing may drift;
- every installed SVG parses;
- no installed SVG still contains the string `simplex`;
- the `upstream remaining` list is exactly the held set below, by directory.

Current state: `targets=315 ours=255 upstream=60 deleted=0`, with 0 integrity
failures, and the 60 decompose as: flags 18, `(root)` 15, `design_3` 12, `new` 6,
messengers 5, icons 4. (`MANIFEST.tsv` was regenerated after the campaign tier
came down, which removed the 18-file `img/crowdfunding/` tree and an orphaned
F-Droid QR from the 334 this tier started at.)

## Holds — why something is still upstream's

| Group | Files | Reason |
|---|---|---|
| `img/flags/` | 18 | Country flag geometry. Not brand artwork and not ours to redesign; the drawing is the fact being depicted. |
| press / publication marks — `heise`, `kuketz-blog`, `optout`, `privacy-guides`, `trail-of-bits`, `whonix` light+dark in `(root)`, plus `design_3/publications/` | 17 | Third-party logos used as citations of coverage of the upstream project. Redrawing them would misrepresent who published what. |
| store badges — `apple_store.svg`, `f_droid.svg`, `testflight.png` in `(root)`, `new/{apple_store,f_droid,f_droid_icon,google_play,testflight}`, `design_3/testflight-dark.png` | 9 | Each is a distribution program's own badge with its own usage rules. Drawing a private imitation would be a false claim that we are listed there. |
| service / OS marks — `design_3/socials/{apple,linux,windows}.png`, `new/gitHub.svg`, `icons/{github,linkedin,reddit,twitter}.svg` | 8 | Same rule: they identify the platform, not us. |
| other-messenger marks — `messengers/{briar,cwtch,element,session,signal}` | 5 | Those are Signal's, Briar's, Element's artwork. A comparison page names them nominatively; a POPOPX-styled version of their logo is worse than theirs. |
| `design_3/cover.webp`, `design_3/cover-light.webp` | 2 | App-design covers: they show the product's own screens (their `.jpg` twins were replaced). An honest replacement means rendering our app, not illustrating a guess, so they wait for real screenshots. |
| `topbar.svg` | 1 | Master-less: the file is a generic three-dot ornament whose `viewBox` is `0 0 0 0`. No brand content to move. |

Total 60. If one of these groups becomes actionable — e.g. we are actually
listed on a store — the correct change is to use that program's **official**
badge asset, not to invent artwork. (The deleted `new/fdroid-qrcode.png` was
this kind of thing too: a QR encoding a link to someone else's listing, with
nothing in the site pointing at it.)

`website/src/img/icons/` is a special case: nothing in `website/src` references
`img/icons/` at all (and the only `content-copy.svg` hit is inside an HTML
comment pointing at `/img/new/`), so the whole 8-file directory is orphan bytes
in a published site — 4 upstream third-party marks among them. Deleting it is
the fix; the census above is measured with the directory still present.

## Re-rendering the hero frames

The 78 `hero/` frames are generated, not hand-drawn: one `frame_svg(theme,
phase, w, h)` in `branding/tools_hero.py` feeds the 4 loops (`light`/`dark` ×
`10fps`/`2fps`) through the installer with `master_name(rel) =
rel.replace("/", "__") + ".src.svg"`. It only writes masters that are missing,
and `--dry-run` prints the per-group PASS table (n / xml / aspect / brand /
unique). Regenerate the frames, then re-run the install + audit sequence.

## WebP bootstrap

`install_assets.py` needs Pillow with WebP support. Nothing is installed
system-wide here; it is unpacked per machine into `/tmp/pylibs`, which does not
survive a reboot:

```
env -u ALL_PROXY -u HTTPS_PROXY python3 -m pip install --quiet \
    --target /tmp/pylibs Pillow          # the ambient proxy can be the dead path
PYTHONPATH=/tmp/pylibs python3 -c 'import PIL.features as f; print(f.check("webp"))'
```

Probe with `PIL.features.check("webp")`, not `Image.core.encoder_exists`.
Encoding is `quality=90, method=6` from an RGBA-converted PNG.

## Traps already paid for

- **Staging extension.** Rendering every raster as `.png` and renaming gave 14
  `.jpg` targets PNG bytes. The installer stages by target extension
  (`stage_ext`), and the audit's magic-byte check is what proves it.
- **"Already replaced" is also a skip.** The installer holds any target whose
  digest differs from REF, which silently skipped a re-render of files that had
  already been replaced once. To re-render, restore the target from REF first
  (`git checkout 9839bd1 -- <path>`) and re-plan.
- **Do not shrink to test.** `sips --resampleWidth 2` reports `Error 13` on
  valid 8-bit RGBA PNGs; that is a verifier artifact, not a bad asset. The audit
  decodes at full size.
- **`git ls-tree -r -z` is `<mode> <type> <sha>\t<path>`.** Unpacking it as
  `mode, sha, _` makes every file compare as identical to upstream.
- **Provenance needs the brand-restored path.** Comparing same-path-only
  over-claimed which files were upstream's.
