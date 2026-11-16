"""Audit website/src/img against REF (the last commit where every image was
still upstream's) and report, per target: replaced vs not, and for replaced
rasters whether the file really decodes at the original pixel size."""
import collections
import hashlib
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = "/Users/elliot/popopx-chat/popopx.chat-site"
os.chdir(ROOT)
REF = sys.argv[1] if len(sys.argv) > 1 else "9839bd1"

targets = subprocess.check_output(["git", "ls-files", "website/src/img"]).decode().split()
ours, upstream, missing = [], [], []
for t in targets:
    if not os.path.exists(t):
        missing.append(t)
        continue
    try:
        ref = subprocess.check_output(["git", "show", "%s:%s" % (REF, t)])
    except subprocess.CalledProcessError:
        ref = None
    now = open(t, "rb").read()
    (ours if ref is None or hashlib.sha256(now).hexdigest() != hashlib.sha256(ref).hexdigest()
     else upstream).append(t)


def dims(path):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", path],
                         capture_output=True, text=True).stdout
    d = dict(re.findall(r"pixel(Width|Height)\s*:\s*(\d+)", out))
    return (int(d["Width"]), int(d["Height"])) if d else None


MAGIC = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG", ".webp": "Web/P",
         ".ico": "icon", ".gif": "GIF", ".pdf": "PDF"}
bad_magic, bad_dims, bad_decode, bad_xml, brand_hits = [], [], [], [], []
for t in ours:
    ext = os.path.splitext(t)[1].lower()
    magic = subprocess.run(["file", "-b", t], capture_output=True, text=True).stdout.strip()
    want = MAGIC.get(ext)
    if want and want.lower() not in magic.lower():
        bad_magic.append((t, ext, magic[:50]))
    if ext in (".svg",):
        try:
            ET.parse(t)
        except Exception as e:
            bad_xml.append((t, str(e)[:60]))
    elif ext != ".pdf":
        # Full-size decode, not a resample: sips cannot write a 2px destination, which
        # is a verifier artifact and was previously reported as a bad asset.
        r = subprocess.run(["sips", "-s", "format", "png", t, "--out",
                            "/tmp/_aud.png"], capture_output=True)
        if r.returncode != 0:
            bad_decode.append((t, r.stderr.decode().strip()[:70]))
            continue
    if ext in (".png", ".jpg", ".jpeg", ".webp", ".ico"):
        tmp = "/tmp/_ref%s" % ext
        open(tmp, "wb").write(subprocess.check_output(["git", "show", "%s:%s" % (REF, t)]))
        if dims(t) != dims(tmp):
            bad_dims.append((t, dims(tmp), dims(t)))
    body = open(t, "rb").read()
    if re.search(rb"simplex", body, re.I) and ext in (".svg",):
        brand_hits.append(t)

print("targets=%d ours=%d upstream=%d deleted=%d" % (len(targets), len(ours), len(upstream), len(missing)))
print("magic wrong for ext: %d  dimension drift: %d  decode failure: %d  svg unparsable: %d"
      % (len(bad_magic), len(bad_dims), len(bad_decode), len(bad_xml)))
for x in (bad_magic + bad_dims + bad_decode + bad_xml)[:8]:
    print("   BAD", x)
print("replaced SVG still containing 'simplex': %d %s" % (len(brand_hits), brand_hits[:4]))
print("upstream remaining by dir:", dict(collections.Counter(
    (t.split("/")[3] if t.count("/") > 3 else "(root)") for t in upstream).most_common()))
print("upstream remaining by ext:", dict(collections.Counter(
    os.path.splitext(t)[1].lower() for t in upstream).most_common()))
