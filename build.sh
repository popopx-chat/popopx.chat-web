#!/bin/bash
# Build the POPOPX site into website/_site. Mirrors upstream's website/web.sh,
# minus `npm install`, plus the two local deviations documented in README.md.
set -e
cd "$(dirname "$0")/website"
export NODE_OPTIONS=--max-old-space-size=4096

rm -rf _site                             # eleventy does not prune passthrough deletions
node copy_sources.js                      # repo docs|blog|images -> src/ (silently skips absent trees)
cp node_modules/lottie-web/build/player/lottie.min.js src/js
cp node_modules/ethers/dist/ethers.umd.min.js src/js
cp node_modules/ethers/dist/ethers.umd.js.map src/js
mkdir -p src/file-assets
cp node_modules/@simplex-chat/xftp-web/dist-web/assets/index.js src/file-assets/
cp node_modules/@simplex-chat/xftp-web/dist-web/assets/index.css src/file-assets/
cp node_modules/@simplex-chat/xftp-web/dist-web/assets/crypto.worker.js src/file-assets/
node merge_translations.js                # generates translations.json (required by .eleventy.js)

# Per-language copies: this loop is what produces the localized pages.
for file in langs/*.json; do
  lang=$(basename "$file" .json)
  mkdir -p "src/$lang"
  for page in index old messaging contact invitation fdroid why downloads file; do
    cp "src/$page.html" "src/$lang/"
  done
  echo "{\"lang\":\"$lang\"}" > "src/$lang/$lang.json"
done

npm run build:js                          # copies qrcode.js in, then copy_call.sh vendors the call assets; the .jsc step needs them
for f in src/js/*.jsc; do
  [ -f "$f" ] && { cpp -P -traditional-cpp "$f" "${f%.jsc}.js" 2>/dev/null || cpp -P -traditional "$f" "${f%.jsc}.js"; }
done
npm run build:eleventy
npm run build:tailwind                    # writes _site/css/tailwind.css

for file in langs/*.json; do
  rm -rf "src/$(basename "$file" .json)"
done

echo "OK: $(find _site -name '*.html' | wc -l | tr -d ' ') html pages, $(find _site -type f | wc -l | tr -d ' ') files in website/_site"
