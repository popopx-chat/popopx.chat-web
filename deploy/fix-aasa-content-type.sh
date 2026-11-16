#!/usr/bin/env bash
# Repairs the one header iOS rejects: nginx types the extensionless
# apple-app-site-association as application/octet-stream, and Apple requires
# application/json. Idempotent; backs up every file it touches; reloads only if
# `nginx -t` passes and restores the backups if it does not.
#
#   sudo bash fix-aasa-content-type.sh
set -euo pipefail

command -v nginx >/dev/null || { echo "nginx not found on this host"; exit 1; }
confs=$(nginx -T 2>/dev/null | awk '/^# configuration file /{f=$4} /server_name[^;]*popopx\.chat/{print f}' | sort -u)
[ -n "$confs" ] || { echo "no server block names popopx.chat - refusing to guess"; exit 1; }
echo "config files defining popopx.chat:"; echo "$confs" | sed 's/^/  /'

stamp=$(date +%Y%m%d-%H%M%S)
for f in $confs; do
  if grep -q 'apple-app-site-association' "$f"; then
    echo "  $f already handles the AASA - leaving it alone; if the type is still wrong, read the note at the end"; continue
  fi
  cp -a "$f" "$f.bak-$stamp"
  python3 - "$f" <<'PY'
import io, sys
p = sys.argv[1]
loc = "    location = /.well-known/apple-app-site-association {\n        default_type application/json;\n    }\n"
out = []
done = False
for line in io.open(p, encoding="utf-8"):
    out.append(line)
    if not done and "server_name" in line and "popopx.chat" in line and line.rstrip().endswith(";"):
        out.append(loc)
        done = True
if not done:
    sys.stderr.write("no terminating server_name line for popopx.chat in %s\n" % p)
    sys.exit(3)
io.open(p, "w", encoding="utf-8").writelines(out)
print("  inserted the exact-match location into", p)
PY
done

if ! nginx -t; then
  for f in $confs; do [ -f "$f.bak-$stamp" ] && mv -f "$f.bak-$stamp" "$f"; done
  echo "nginx -t failed - restored every file, nothing reloaded"; exit 1
fi
nginx -s reload
sleep 1
echo "--- verify (expect: content-type: application/json) ---"
curl -sSI -H 'Host: popopx.chat' http://127.0.0.1/.well-known/apple-app-site-association | sed -n '1p;/[Cc]ontent-[Tt]ype/p'
