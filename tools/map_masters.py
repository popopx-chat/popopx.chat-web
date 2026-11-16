import os, subprocess, collections, json, sys

ROOT = "/Users/elliot/popopx-chat/popopx.chat-site"
os.chdir(ROOT)

targets = [p for p in subprocess.check_output(
    ["git", "ls-files", "website/src/img"]).decode().split("\n") if p]
by_rel = {}
dupes = []
for t in targets:
    rel = t[len("website/src/img/"):]
    (dupes.append(rel) if rel in by_rel else by_rel.__setitem__(rel, t))

dup_dir = collections.defaultdict(list)
for t in targets:
    dup_dir[os.path.basename(t)].append(t)

masters = sorted(
    os.path.join(r, f)
    for r, _, fs in os.walk("branding/source-svg")
    for f in fs if f.endswith(".svg")
)

rows, unresolved, ambiguous = [], [], []
for m in masters:
    b = os.path.basename(m)
    cand = []
    if b.endswith(".src.svg"):
        cand.append(b[:-len(".src.svg")])
        cand.append(b[:-len(".src.svg")] + ".svg")
    else:
        cand.append(b)
        cand.append(b[:-len(".svg")] + ".svg")
    hit = None
    for c in cand:
        rel = c.replace("__", "/")
        if rel in by_rel:
            hit = by_rel[rel]
            break
    if hit:
        rows.append((hit, m))
    else:
        unresolved.append((m, cand))

out = [{"target": t, "master": m, "ext": os.path.splitext(t)[1].lower()} for t, m in rows]
json.dump({"pairs": out,
           "unresolved": unresolved,
           "ambiguous": ambiguous,
           "targets_total": len(targets)},
          open("/tmp/imgmap.json", "w"), indent=1)

n = collections.Counter(p["ext"] for p in out)
print("targets=%d masters=%d mapped=%d unresolved=%d ambiguous=%d"
      % (len(targets), len(masters), len(rows), len(unresolved), len(ambiguous)))
print("mapped by target ext:", dict(n))
print("unmapped targets:", len(targets) - len(rows))
for u in unresolved[:5]:
    print("  UNRESOLVED", u)
for a in ambiguous[:5]:
    print("  AMBIGUOUS", a)
