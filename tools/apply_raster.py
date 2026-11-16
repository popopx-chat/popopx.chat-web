import json, os, re, shutil, subprocess, hashlib, sys

ROOT = "/Users/elliot/popopx-chat/popopx.chat-site"
os.chdir(ROOT)
SVG2PNG = "/Users/elliot/popopx-chat/tools/r7/svg2png"
STAGE = "/tmp/rstage"
APPLY = "--apply" in sys.argv
os.makedirs(STAGE, exist_ok=True)

pairs = json.load(open("/tmp/imgmap.json"))["pairs"]
raster = [p for p in pairs if p["ext"] in (".png", ".jpg", ".jpeg")]


def dims(p):
    out = subprocess.check_output(["sips", "-g", "pixelWidth", "-g", "pixelHeight", p]).decode()
    d = dict(re.findall(r"pixel(Width|Height)\s*:\s*(\d+)", out))
    return int(d["Width"]), int(d["Height"])


def viewBox(p):
    head = open(p, encoding="utf-8", errors="replace").read(4000)
    m = re.search(r'viewBox\s*=\s*"([^"]+)"', head)
    if m:
        n = [float(x) for x in re.split(r"[,\s]+", m.group(1).strip())]
        if len(n) == 4:
            return n[2], n[3]
    m = re.search(r'\bwidth\s*=\s*"([\d.]+)', head)
    n = re.search(r'\bheight\s*=\s*"([\d.]+)', head)
    return (float(m.group(1)), float(n.group(1))) if m and n else None


jobs, held, report = [], [], []
for p in raster:
    t, m = p["target"], p["master"]
    ext = os.path.splitext(t)[1].lower()
    try:
        w, h = dims(t)
    except Exception as e:
        held.append((t, "cannot read target dims"))
        continue
    mv, tv = viewBox(m), None
    if not mv or not all(mv):
        held.append((t, "master has no usable viewBox"))
        continue
    if abs(mv[0] / mv[1] - w / h) > 0.02:
        held.append((t, "aspect mismatch master %gx%g vs target %dx%d" % (mv[0], mv[1], w, h)))
        continue
    out = os.path.join(STAGE, re.sub(r"[^A-Za-z0-9.-]", "_", t) + ext)
    jobs.append((m, out, w, h, t))

with open("/tmp/raster_jobs.tsv", "w") as f:
    for m, out, w, h, t in jobs:
        f.write("%s\t%s\t%d\t%d\n" % (m, out, w, h))

print("raster targets=%d queued=%d held=%d" % (len(raster), len(jobs), len(held)))
for t, why in held:
    print("  HELD", t, "|", why)

if not APPLY:
    sys.exit(0)

rc = subprocess.call([SVG2PNG, "--jobs", "/tmp/raster_jobs.tsv"])
ok, bad = [], []
for m, out, w, h, t in jobs:
    if not os.path.exists(out):
        bad.append((t, "no output"))
        continue
    try:
        ow, oh = dims(out)
    except Exception:
        bad.append((t, "output unreadable"))
        continue
    before = hashlib.sha256(subprocess.check_output(["git", "show", "HEAD:%s" % t])).hexdigest()[:16]
    if (ow, oh) != (w, h):
        bad.append((t, "dims %dx%d != %dx%d" % (ow, oh, w, h)))
        continue
    after = hashlib.sha256(open(out, "rb").read()).hexdigest()[:16]
    if after == before:
        bad.append((t, "digest unchanged vs HEAD"))
        continue
    shutil.copyfile(out, t)
    ok.append("%s\t%d x %d\t%s\t%s" % (t, w, h, before, after))

print("RENDERED+INSTALLED %d  rejected %d" % (len(ok), len(bad)))
for t, why in bad:
    print("  BAD", t, "|", why)
open("/tmp/raster_swap_report.tsv", "w").write("\n".join(ok) + "\n")
