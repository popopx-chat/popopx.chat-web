import json, os, re, subprocess, sys, hashlib, xml.etree.ElementTree as ET

ROOT = "/Users/elliot/popopx-chat/popopx.chat-site"
os.chdir(ROOT)
APPLY = "--apply" in sys.argv
map_ = json.load(open("/tmp/imgmap.json"))["pairs"]

NUM = r"[-+]?[0-9]*\.?[0-9]+"


def box(text):
    """Return (w,h) from an svg element's attrs, or None."""
    root = ET.fromstring(text)
    vb = root.get("viewBox")
    if vb:
        p = re.split(r"[,\s]+", vb.strip())
        if len(p) == 4:
            return float(p[2]), float(p[3])
    w, h = root.get("width"), root.get("height")
    if w and h:
        fw = re.match(NUM, w.strip())
        fh = re.match(NUM, h.strip())
        if fw and fh:
            return float(fw.group()), float(fh.group())
    return None


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


svg = [p for p in map_ if p["ext"] == ".svg"]
skipped, todo = [], []
for p in svg:
    t, m = p["target"], p["master"]
    try:
        mt = open(m, encoding="utf-8").read()
        mb = box(mt)
    except Exception as e:
        skipped.append((t, "master unparsable: %s" % e))
        continue
    if mb is None:
        skipped.append((t, "master has no viewBox/width+height"))
        continue
    tb = None
    try:
        tb = box(open(t, encoding="utf-8").read())
    except Exception:
        tb = None  # not XML (compressed/doctype) -> ratio unknown, still swappable
    if not all(mb):
        skipped.append((t, "master has a zero dimension: %gx%g" % tuple(mb)))
        continue
    if tb and not all(tb):
        tb = None  # degenerate target box -> ratio uncheckable
    if tb and abs((mb[0] / mb[1]) - (tb[0] / tb[1])) > 0.02:
        skipped.append((t, "aspect mismatch master %gx%g vs target %gx%g" % (mb + tb)))
        continue
    if sha(m) == sha(t):
        skipped.append((t, "master identical to target"))
        continue
    todo.append((t, m, tb, mb))

print("svg targets=%d pass-gate=%d skipped=%d  (dry-run)" % (len(svg), len(todo), len(skipped)))
for t, why in skipped:
    print("  SKIP", t, "|", why)

if APPLY:
    report = open("/tmp/svg_swap_report.tsv", "w")
    for t, m, tb, mb in todo:
        head = subprocess.check_output(["git", "show", "HEAD:%s" % t]).decode()
        before = hashlib.sha256(head.encode()).hexdigest()[:16]
        data = open(m, "rb").read()
        with open(t, "wb") as f:
            f.write(data)
        after = sha(t)
        assert after != before, t
        report.write("%s\t%s\t%g x %g\t%s\t%s\n" % (
            t, m, *(tb or mb or (0, 0))[:2], before, after))
    report.close()
    print("WROTE %d files" % len(todo))
