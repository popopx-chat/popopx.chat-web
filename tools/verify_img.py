import subprocess, os, hashlib, re, sys
ROOT = "/Users/elliot/popopx-chat/popopx.chat-site"
os.chdir(ROOT)

def sips_dims(path_or_bytes, tmp):
    if isinstance(path_or_bytes, bytes):
        open(tmp, "wb").write(path_or_bytes)
        p = tmp
    else:
        p = path_or_bytes
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", p],
                         capture_output=True, text=True).stdout
    d = dict(re.findall(r"pixel(Width|Height)\s*:\s*(\d+)", out))
    return (int(d["Width"]), int(d["Height"])) if d else None

files = subprocess.check_output(
    ["git", "diff", "--name-only", "--", "website/src/img"]).decode().split("\n")
files = [f for f in files if f]
print("differing from HEAD:", len(files))

raster = [f for f in files if re.search(r"\.(png|jpe?g|webp)$", f, re.I)]
svg = [f for f in files if f.lower().endswith(".svg")]
print("  svg:", len(svg), " raster:", len(raster))

mismatch, bad_magic, identical = [], [], []
PNG = b"\x89PNG\r\n\x1a\n"
JPG = b"\xff\xd8\xff"
for f in raster:
    now = open(f, "rb").read()
    head = subprocess.check_output(["git", "show", "HEAD:" + f])
    if hashlib.sha256(now).hexdigest() == hashlib.sha256(head).hexdigest():
        identical.append(f)
    dn = sips_dims(now, "/tmp/_n.bin")
    dh = sips_dims(head, "/tmp/_h.bin")
    if dn != dh:
        mismatch.append((f, dh, dn))
    ext = os.path.splitext(f)[1].lower()
    magic_ok = (now[:8] == PNG) if ext == ".png" else (now[:3] == JPG) if ext in (".jpg", ".jpeg") else True
    if not magic_ok:
        bad_magic.append((f, now[:8]))

print("digest identical to HEAD (should be 0):", len(identical))
print("dimension drift vs HEAD (should be 0):", len(mismatch))
for m in mismatch[:10]:
    print("   ", m)
print("wrong magic for extension (should be 0):", len(bad_magic), bad_magic[:5])
kept_svg = [f for f in svg if re.search(b"simplex", open(f, "rb").read(), re.I)]
print("svg still containing the string 'simplex':", len(kept_svg), kept_svg[:5])
