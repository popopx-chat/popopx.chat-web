"""Install POPOPX branding masters over website/src/img targets.

Routes by target format: .svg takes the master source directly, .png/.jpg are
rasterised by tools/r7/svg2png at the target's own pixel size, .webp goes
through that PNG and is transcoded by Pillow (svg2png cannot write WebP).
Every swap is gated and then re-verified against the pre-rebrand bytes.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = "/Users/elliot/popopx-chat/popopx.chat-site"
os.chdir(ROOT)
SVG2PNG = "/Users/elliot/popopx-chat/tools/r7/svg2png"
REF = "9839bd1"          # last commit where every src/img file was still upstream's
PIL_PATH = "/tmp/pylibs"  # Pillow unpacked here by hand; nothing is installed system-wide
STAGE = "/tmp/astage"
APPLY = "--apply" in sys.argv

sys.path.insert(0, PIL_PATH)
try:
    from PIL import Image, features
    HAVE_WEBP = bool(features.check("webp"))
except Exception:
    Image, HAVE_WEBP = None, False


def ref_bytes(path):
    return subprocess.check_output(["git", "show", "%s:%s" % (REF, path)])


def dims_from_bytes(b, tmp):
    open(tmp, "wb").write(b)
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", tmp],
                         capture_output=True, text=True).stdout
    d = dict(re.findall(r"pixel(Width|Height)\s*:\s*(\d+)", out))
    return (int(d["Width"]), int(d["Height"])) if d else None


def box(svg_text):
    root = ET.fromstring(svg_text)
    vb = root.get("viewBox")
    if vb:
        p = re.split(r"[,\s]+", vb.strip())
        if len(p) == 4:
            return float(p[2]), float(p[3])
    w, h = root.get("width"), root.get("height")
    if w and h:
        mw, mh = re.match(r"[-+]?[0-9]*\.?[0-9]+", w), re.match(r"[-+]?[0-9]*\.?[0-9]+", h)
        if mw and mh:
            return float(mw.group()), float(mh.group())
    return None


pairs = json.load(open("/tmp/imgmap.json"))["pairs"]
plan, held = [], []
for p in pairs:
    t, m, ext = p["target"], p["master"], p["ext"]
    if not os.path.exists(t):
        held.append((t, "target absent"))
        continue
    if hashlib.sha256(open(t, "rb").read()).hexdigest() != hashlib.sha256(ref_bytes(t)).hexdigest():
        held.append((t, "already replaced"))
        continue
    try:
        mb = box(open(m, encoding="utf-8").read())
    except Exception as e:
        held.append((t, "master unparsable: %s" % e))
        continue
    if not mb or not all(mb):
        held.append((t, "master has no usable viewBox: %r" % (mb,)))
        continue
    if ext in (".png", ".jpg", ".jpeg", ".webp", ".ico"):
        try:
            tb = dims_from_bytes(ref_bytes(t), "/tmp/_r.bin")
        except Exception:
            tb = None
        if tb and (tb[0] < 1 or tb[1] < 1):
            held.append((t, "target unreadable"))
            continue
        if tb and abs(mb[0] / mb[1] - tb[0] / tb[1]) > 0.02:
            held.append((t, "aspect master %gx%g vs target %dx%d" % (mb + tb)))
            continue
        if ext == ".ico" or (ext == ".webp" and not HAVE_WEBP):
            held.append((t, "no route for %s here" % ext))
            continue
        plan.append((t, m, ext, tb))
    else:  # .svg -> direct source swap, aspect gate only if the target parses
        try:
            tb = box(open(t, encoding="utf-8").read())
        except Exception:
            tb = None
        if tb and tb != (0, 0) and abs(mb[0] / mb[1] - tb[0] / tb[1]) > 0.02:
            held.append((t, "aspect master %gx%g vs target %gx%g" % (mb + tb)))
            continue
        plan.append((t, m, ".svg", tb))

print("mapped=%d planned=%d held=%d  webp encoder=%s" % (len(pairs), len(plan), len(held), HAVE_WEBP))
for t, why in held:
    print("  HELD", t, "|", why)
if not APPLY:
    sys.exit(0)

os.makedirs(STAGE, exist_ok=True)
raster = [(t, m, ext, tb) for t, m, ext, tb in plan if ext != ".svg"]
jobs = []
for i, (t, m, ext, tb) in enumerate(raster):
    w, h = tb
    stage_ext = ".png" if ext in (".png", ".webp") else ext
    jobs.append((m, os.path.join(STAGE, "%04d%s" % (i, stage_ext)), w, h, t, ext))
with open("/tmp/astage.tsv", "w") as f:
    for m, out, w, h, t, ext in jobs:
        f.write("%s\t%s\t%d\t%d\n" % (m, out, w, h))

print(subprocess.run([SVG2PNG, "--jobs", "/tmp/astage.tsv"], capture_output=True, text=True).stdout.strip())

done, fails = [], []
for m, out, w, h, t, ext in jobs:
    if not os.path.exists(out):
        fails.append((t, "renderer produced nothing"))
        continue
    data = open(out, "rb").read()
    if ext == ".webp":
        img = Image.open(out).convert("RGBA")
        tmp = out + ".webp"
        img.save(tmp, "WEBP", quality=90, method=6)
        data = open(tmp, "rb").read()
    before = hashlib.sha256(ref_bytes(t)).hexdigest()
    after = hashlib.sha256(data).hexdigest()
    got = dims_from_bytes(data, "/tmp/_g.bin")
    if after == before:
        fails.append((t, "digest unchanged"))
        continue
    if got != (w, h):
        fails.append((t, "dims %r != %r" % (got, (w, h))))
        continue
    open(t, "wb").write(data)
    real = dims_from_bytes(open(t, "rb").read(), "/tmp/_v.bin")
    dec = subprocess.run(["sips", "-s", "format", "png", "--resampleWidth", "2", t,
                          "--out", "/tmp/_dec.png"], capture_output=True)
    if real != (w, h) or dec.returncode != 0:
        fails.append((t, "post-install verify failed dims=%r decode_rc=%d" % (real, dec.returncode)))
        continue
    done.append((t, w, h, before[:12], after[:12]))

for t, m, ext, tb in [x for x in plan if x[2] == ".svg"]:
    before = hashlib.sha256(ref_bytes(t)).hexdigest()
    data = open(m, "rb").read()
    open(t, "wb").write(data)
    after = hashlib.sha256(data).hexdigest()
    (fails if after == before else done).append((t, "svg", "", before[:12], after[:12]))

print("INSTALLED %d  FAILED %d" % (len(done), len(fails)))
for f in fails:
    print("  FAIL", f)
open("/tmp/installed.tsv", "w").write("\n".join("\t".join(str(x) for x in d) for d in done) + "\n")
