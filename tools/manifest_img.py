"""Emit branding/MANIFEST.tsv: one row per src/img target, with the original pixel
size, the brand master that produced it (if any), and its replaced/held status.

Status is decided against REF (the last commit where every image was still
upstream's), so re-running after any replacement restates the truth rather than
restating a note. class comes from the path, which is how the tier was planned.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = "/Users/elliot/popopx-chat/popopx.chat-site"
os.chdir(ROOT)
REF = sys.argv[1] if len(sys.argv) > 1 else "9839bd1"
OUT = "branding/MANIFEST.tsv"

try:
    pairs = {p["target"]: p["master"] for p in json.load(open("/tmp/imgmap.json"))["pairs"]}
except Exception:
    pairs = {}
    sys.stderr.write("no /tmp/imgmap.json: master column will be empty\n")

GROUPS = {
    "hero": "hero animation frame",
    "design_3": "design page artwork",
    "flags": "country flag geometry",
    "icons": "third-party service mark",
    "messengers": "other-messenger mark",
    "crowdfunding": "campaign artwork",
    "new": "whats-new illustration",
}

rows = []
for t in subprocess.check_output(["git", "ls-files", "website/src/img"]).decode().split():
    rel = t.split("website/src/img/")[1]
    ext = os.path.splitext(t)[1].lower()
    parts = rel.split("/")
    group = parts[0] if len(parts) > 1 else "(root)"
    cls = GROUPS.get(group, "brand mark" if group == "(root)" else "illustration")
    if not os.path.exists(t):
        rows.append((rel, "", cls, "missing", "", ""))
        continue
    try:
        ref = subprocess.check_output(["git", "show", "%s:%s" % (REF, t)])
    except subprocess.CalledProcessError:
        ref = None
    now = open(t, "rb").read()
    status = "ours" if ref is None or hashlib.sha256(ref).hexdigest() != hashlib.sha256(now).hexdigest() else "upstream"
    if ext == ".svg":
        m = re.search(rb'viewBox="([\d.\-\s]+)"', now)
        d = [p for p in m.group(1).split()] if m else []
        dims = "%sx%s" % (d[2], d[3]) if len(d) == 4 else ""
    elif ext == ".pdf":
        dims = ""
    else:
        o = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", t],
                           capture_output=True, text=True).stdout
        g = dict(re.findall(r"pixel(Width|Height)\s*:\s*(\d+)", o))
        dims = "%sx%s" % (g.get("Width", "?"), g.get("Height", "?"))
    rows.append((rel, dims, cls, status, pairs.get(t, ""), os.path.getsize(t)))

with open(OUT, "w") as f:
    f.write("target\toriginal_px\tclass\tstatus\tmaster\tbytes\n")
    for r in sorted(rows):
        f.write("\t".join(str(x) for x in r) + "\n")

print("%s: %d rows, ours=%d upstream=%d, masters known=%d"
      % (OUT, len(rows), sum(1 for r in rows if r[3] == "ours"),
         sum(1 for r in rows if r[3] == "upstream"), sum(1 for r in rows if r[4])))
