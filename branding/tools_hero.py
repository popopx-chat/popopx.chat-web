#!/usr/bin/env python3
"""Author POPOPX master SVGs for the hero frame sequences (website/src/img/hero/**).

One design function, `frame_svg(theme, phase)`, drives every frame: the frame index
becomes a normalised phase in [0,1) and every moving element reads that phase, so the
sequence animates (thread rows arriving one by one, an outgoing bubble growing, dots
travelling the relay arcs, pennant wave, pulse rings) instead of 68 identical stills.

Master naming convention (tools/map_masters.py depends on it):
    website/src/img/hero/light/10fps/0005.webp
      -> branding/source-svg/hero__light__10fps__0005.webp.src.svg

Usage:  python3 branding/tools_hero.py [--dry-run]
Only writes new files; an existing master is never overwritten.
"""

import hashlib
import math
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "website", "src", "img")
OUT = os.path.join(ROOT, "branding", "source-svg")
SRC_SUFFIX = ".src.svg"

# group -> (period in frames, palette theme).  Period is the length of the source
# sequence, so phase wraps exactly once over the loop.
GROUPS = [
    ("hero/light/10fps", 21, "light"),
    ("hero/light/2fps", 40, "light"),
    ("hero/dark/10fps", 21, "dark"),
    ("hero/dark/2fps", 40, "dark"),
]

# ---------------------------------------------------------------- brand palette
# Purple #792BBC -> #3E0A6F gradient, PopopxBlue #0088FF, cyan #70F0F9,
# teal #1298A5, ink #062A3A.  Frames keep a transparent background (the upstream
# webp frames carry alpha) so only the artwork itself is opaque.
THEME = {
    "light": {
        "edge": "#062A3A",      # phone outline / ink strokes
        "screen": "#FFFFFF",
        "chrome": "#DCEFFA",    # quiet fills
        "muted": "#6E8A99",     # placeholder text
        "soft": "#EAF7FF",      # incoming bubble
        "line": "#A9DDF0",      # bubble hairline
        "accent": "#0088FF",
        "ripple": "#1298A5",
        "word": "#062A3A",
    },
    "dark": {
        "edge": "#EAF7FF",
        "screen": "#0A3040",
        "chrome": "#12455C",
        "muted": "#7FA8BA",
        "soft": "#124055",
        "line": "#2A6F8C",
        "accent": "#70F0F9",
        "ripple": "#0088FF",
        "word": "#EAF7FF",
    },
}

DEFS = (
    '<defs>'
    '<linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0" stop-color="#792BBC"/><stop offset="1" stop-color="#3E0A6F"/></linearGradient>'
    '<linearGradient id="g2" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0" stop-color="#7A2BBE"/><stop offset="1" stop-color="#3D0A6D"/></linearGradient>'
    '<linearGradient id="g3" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0" stop-color="#0088FF"/><stop offset="1" stop-color="#1298A5"/></linearGradient>'
    '<linearGradient id="g4" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0" stop-color="#0088FF"/><stop offset="1" stop-color="#70F0F9"/></linearGradient>'
    "</defs>"
)


# ---------------------------------------------------------------- primitives
def n(v):
    """Round to 2 dp and trim, so diffs between frames stay readable."""
    s = "%.2f" % v
    return s.rstrip("0").rstrip(".") if "." in s else s


def rect(x, y, w, h, rx, fill="none", stroke=None, sw=None, op=None):
    a = 'x="%s" y="%s" width="%s" height="%s" rx="%s"' % (n(x), n(y), n(max(w, 0.1)), n(max(h, 0.1)), n(rx))
    a += ' fill="%s"' % fill
    if stroke:
        a += ' stroke="%s" stroke-width="%s"' % (stroke, n(sw or 8))
    if op is not None:
        a += ' opacity="%s"' % n(max(min(op, 1.0), 0.0))
    return "<rect %s/>" % a


def circle(cx, cy, r, fill="none", stroke=None, sw=None, op=None, dash=None):
    a = 'cx="%s" cy="%s" r="%s"' % (n(cx), n(cy), n(max(r, 0.1)))
    a += ' fill="%s"' % fill
    if stroke:
        a += ' stroke="%s" stroke-width="%s"' % (stroke, n(sw or 8))
        if dash:
            a += ' stroke-dasharray="%s %s"' % (n(dash[0]), n(dash[1]))
    if op is not None:
        a += ' opacity="%s"' % n(max(min(op, 1.0), 0.0))
    return "<circle %s/>" % a


def path(d, fill="none", stroke=None, sw=None, op=None, cap="butt", join="miter"):
    a = 'd="%s"' % d
    a += ' fill="%s"' % fill
    if stroke:
        a += ' stroke="%s" stroke-width="%s" stroke-linecap="%s" stroke-linejoin="%s"' % (
            stroke, n(sw or 8), cap, join)
    if op is not None:
        a += ' opacity="%s"' % n(max(min(op, 1.0), 0.0))
    return "<path %s/>" % a


# ---------------------------------------------------------------- easing helpers
def clamp(v, lo=0.0, hi=1.0):
    return lo if v < lo else hi if v > hi else v


def ease(v):
    v = clamp(v)
    return v * v * (3 - 2 * v)


def wave(p):
    """0..1..0 triangle that is continuous across the loop seam."""
    return math.sin(math.pi * p)


def spin(p):
    """Signed sine that matches value and slope at p=0 and p=1 (seamless loop)."""
    return math.sin(2 * math.pi * p)


def shift(p, k, total):
    return (p + float(k) / total) % 1.0


# ---------------------------------------------------------------- wordmark
# "POPOPX" drawn from primitives (no <text>, no transforms: the render pipeline is fed
# plain geometry).  Glyphs live on a 100-unit em, cap band y 10..90.
GLYPH_ADVANCE = {"P": 68, "O": 86, "X": 82}


def glyph(word, s, tx, ty, color, sw=17):
    out = []
    x = 0.0
    for ch in word:
        w = sw * s
        if ch == "O":
            out.append(circle(tx + (x + 42) * s, ty + 50 * s, 31 * s,
                              fill="none", stroke=color, sw=w))
        elif ch == "P":
            d = ("M %s %s L %s %s L %s %s A %s %s 0 0 1 %s %s L %s %s" % (
                n(tx + (x + 22) * s), n(ty + 90 * s),
                n(tx + (x + 22) * s), n(ty + 10 * s),
                n(tx + (x + 50) * s), n(ty + 10 * s),
                n(21 * s), n(21 * s),
                n(tx + (x + 50) * s), n(ty + 52 * s),
                n(tx + (x + 22) * s), n(ty + 52 * s)))
            out.append(path(d, stroke=color, sw=w, cap="round", join="round"))
        elif ch == "X":
            d = ("M %s %s L %s %s M %s %s L %s %s" % (
                n(tx + (x + 16) * s), n(ty + 12 * s), n(tx + (x + 66) * s), n(ty + 88 * s),
                n(tx + (x + 66) * s), n(ty + 12 * s), n(tx + (x + 16) * s), n(ty + 88 * s)))
            out.append(path(d, stroke=color, sw=w, cap="round"))
        x += GLYPH_ADVANCE[ch] + 14
    return out, x * s


# ---------------------------------------------------------------- geometry constants
# Shared with the already-authored hero masters (10fps 0000-0004) so the whole
# sequence keeps one phone, one mark and one palette.
PHONE = (302.4, 32.4, 475.2, 1015.2, 85.5)
SCREEN = (330.9, 78.1, 418.2, 913.7, 47.5)
LX, RX = 368.5, 712.6                      # chat gutter inside the screen
PEER = (63.5, 245.1, 175.4, 157.9)          # peer bubble, left of the phone
MARK = (848.1, 683.4, 161.4, 145.2)         # white speech bubble holding the P pennant
ARC = {"cx": 928.85, "cy": 359.4, "r": 100.3, "a0": math.radians(225.5),
       "a1": math.radians(314.5)}           # the relay arcs, top-right


def pennant(x, y, h, s, phase):
    """Flag mast + waving triangular pennant inside the mark bubble."""
    mast = rect(x, y, 13.7 * s, h, 5.5 * s, fill="url(#g1)")
    tip_y = y + h * 0.45 + spin(phase) * h * 0.10
    mid_y = y + h * 0.22 - spin(phase) * h * 0.06
    d = "M %s %s L %s %s L %s %s L %s %s Z" % (
        n(x + 13.4 * s), n(y), n(x + 13.4 * s + 58 * s), n(mid_y),
        n(x + 13.4 * s + 58 * s), n(tip_y + h * 0.10), n(x + 13.4 * s), n(y + h * 0.46))
    return mast + path(d, fill="url(#g1)")


def relay_dot(u, r_scale=1.0):
    """Point travelling along the middle relay arc, u in [0,1)."""
    a = ARC["a0"] + (ARC["a1"] - ARC["a0"]) * u
    return ARC["cx"] + ARC["r"] * r_scale * math.cos(a), ARC["cy"] + ARC["r"] * r_scale * math.sin(a)


# ---------------------------------------------------------------- the design function
def frame_svg(theme, phase, w=1080, h=1080):
    """Single still of the loop at `phase` in [0,1).  w/h come from the real target."""
    c = THEME[theme]
    p = phase % 1.0
    e = []
    add = e.append

    # ---- phone shell
    add(rect(*PHONE[:4], PHONE[4], fill="#FFFFFF", stroke=c["edge"], sw=14.3))
    add(rect(*SCREEN[:4], SCREEN[4], fill=c["screen"]))
    add(rect(464.0, 50.7, 152.1, 14.2, 7.1, fill=c["chrome"]))

    # ---- app bar: title bar + presence dot that breathes once per loop
    add(rect(LX, 123.8, 142.2, 20.1, 10.1, fill=c["muted"], op=0.5))
    add(circle(700.5, 132.9, 11.0 + 2.4 * spin(p), fill=c["accent"],
               op=0.55 + 0.35 * clamp(wave(p))))

    # ---- chat thread: 5 beats, each sliding in on its own slice of the loop,
    #      the whole thread clearing before the seam so the loop is continuous.
    beats = [
        ("in", 196.0, 118.0), ("out", 336.0, 92.0),
        ("in", 450.0, 118.0), ("out", 590.0, 92.0),
        ("in", 704.0, 118.0),
    ]
    span, stagger = 0.17, 0.13
    clear = 1.0 - ease((p - 0.87) / 0.11)      # thread fades out at the end of the loop
    pending = [k for k in range(len(beats)) if p < k * stagger]
    next_y = beats[pending[0]][1] if pending else beats[-1][1] + beats[-1][2] + 22.0
    for k, (kind, y, hh) in enumerate(beats):
        q = ease((p - k * stagger) / span) * clear
        if q <= 0.004:
            continue
        slide = (1 - ease((p - k * stagger) / span)) * 46.0
        if kind == "in":
            add(circle(400.5 - slide, y + hh / 2, 30.0, fill=c["chrome"], op=q))
            add(rect(440.0 - slide, y, 228.0, hh, 31.1, fill=c["soft"], op=q))
            add(rect(462.0 - slide, y + hh * 0.30, 178.0 * (0.45 + 0.55 * q), 12.0, 6.0,
                     fill=c["muted"], op=0.62 * q))
            add(rect(462.0 - slide, y + hh * 0.58, 128.0 * (0.35 + 0.65 * q), 12.0, 6.0,
                     fill=c["muted"], op=0.40 * q))
        else:
            bw = 200.0 * (0.4 + 0.6 * q)
            add(rect(RX - bw, y - slide, bw, hh, 31.1, fill="url(#g1)", op=q))
            add(rect(RX - bw + 24, y - slide + hh * 0.34, 130.0 * (0.4 + 0.6 * q),
                     12.0, 6.0, fill="#FFFFFF", op=0.62 * q))
            if q > 0.72:  # tail and delivered tick land at the end of the beat
                t = (q - 0.72) / 0.28
                add(path("M %s %s L %s %s L %s %s Z" % (
                    n(RX - 30), n(y - slide + hh - 12), n(RX - 6),
                    n(y - slide + hh - 12), n(RX - 2), n(y - slide + hh + 20 * t)),
                    fill="url(#g1)", op=t))
                add(path("M %s %s l %s %s l %s %s" % (
                    n(RX - bw - 48), n(y - slide + hh * 0.52),
                    n(9 * t), n(9 * t), n(17 * t), n(-19 * t)),
                    stroke=c["accent"], sw=7.3, op=t, cap="round", join="round"))

    # ---- typing indicator: three dots phase-shifted by a third, sitting in the lane
    #      of the row that has not arrived yet
    ty = next_y
    add(rect(LX, ty, 118.0, 58.0, 29.0, fill=c["soft"], op=clear))
    for j in range(3):
        r = 7.0 + 4.5 * clamp(math.sin(2 * math.pi * shift(p, j, 3)) * 0.5 + 0.5)
        add(circle(LX + 30 + j * 29, ty + 29, r, fill=c["muted"],
                   op=(0.40 + 0.45 * wave(shift(p, j, 3))) * clear))

    # ---- peer bubble (gradient) with a ripple that expands once per half loop
    px, py, pw, ph = PEER
    add(rect(px, py, pw, ph, 47.4, fill="url(#g1)", op=0.9))
    add(path("M %s %s L %s %s L %s %s Z" % (px + 55.0, py + ph - 6.0,
                                            px + 88.0, py + ph - 6.0,
                                            px + 66.0, py + ph + 30.0),
             fill="url(#g1)", op=0.9))
    for j in range(2):
        u = shift(p, j, 2)
        add(rect(px - 10 * u, py - 9 * u, pw + 20 * u, ph + 18 * u, 47.4 + 12 * u,
                 fill="none", stroke=c["ripple"], sw=5.0, op=0.5 * (1 - u)))
    add(rect(px + 30, py + 44, 116.0, 14.0, 7.0, fill="#FFFFFF", op=0.75))
    add(rect(px + 30, py + 74, 78.0, 14.0, 7.0, fill="#FFFFFF", op=0.45))

    # ---- the mark: white speech bubble holding a P pennant (brand mark)
    mx, my, mw, mh = MARK
    add(rect(mx, my, mw, mh, 43.6, fill="#FFFFFF", stroke=c["line"], sw=8.8))
    add(path("M %s %s L %s %s L %s %s Z" % (mx + 52.0, my + mh - 7.0,
                                            mx + 84.0, my + mh - 7.0,
                                            mx + 60.0, my + mh + 29.0),
             fill="#FFFFFF"))
    add(pennant(mx + 49.6, my + 25, 88.7, 1.0, p))

    # ---- relay arcs + dots travelling them (the "message on the wire" beat)
    for j, rr in enumerate((50.2, 100.3, 150.5)):
        half = rr * 1.4
        y0 = 262.7 + j * 25.05
        op = (0.35 + 0.5 * wave(shift(p, j, 3)))
        add(path("M %s %s a %s %s 0 0 1 %s 0" % (
            n(928.85 - half / 2), n(y0), n(rr), n(rr), n(half)),
            stroke=c["accent"], sw=10.5, op=op, cap="round", join="round"))
    for j in range(2):
        u = shift(p, j, 2)
        dx, dy = relay_dot(u)
        add(circle(dx, dy, 9.5, fill=c["accent"], op=0.25 + 0.75 * wave(u)))
        add(circle(dx, dy, 17.0, fill="none", stroke=c["accent"], sw=4.0,
                   op=0.35 * wave(u)))

    # ---- the two linked hops (chain of relays), bottom-left, with a running spark
    for k, bx in enumerate((26.1, 131.0)):
        add(rect(bx, 758.9, 145.2, 80.7, 40.3, fill="none", stroke=c["edge"], sw=12.3))
        lit = ease((p * 2 - 0.15 - k * 0.45) / 0.35)
        if lit > 0.001:
            add(rect(bx + 22, 782.0, 101.2, 34.5, 17.2, fill=c["accent"],
                     op=0.85 * wave(clamp(lit)) + 0.05))
    sp = shift(p, 0, 1)
    add(circle(26.1 + 145.2 + 104.6 * sp, 799.2, 7.5, fill=c["accent"], op=wave(sp)))

    # ---- POPOPX wordmark, bottom-left free space (static: it is the lockup)
    _w, _ww = glyph("POPOPX", 0.44, 26.0, 899.0, c["word"])
    e.extend(_w)
    add(circle(26.0 + _ww + 16.0, 921.0, 7.5 + 2.0 * spin(p), fill="url(#g3)"))

    vb = 'viewBox="0 0 %s %s"' % (n(w), n(h))
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="%s" %s>'
            '<title>POPOPX - private chat, no phone number</title>%s<g>%s</g></svg>'
            % (n(w), n(h), vb, DEFS, "".join(e)))


# ---------------------------------------------------------------- targets / io
def master_name(rel):
    return rel.replace("/", "__") + SRC_SUFFIX


def sips_dims(path_):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", path_],
                         capture_output=True, text=True).stdout
    d = dict(re.findall(r"pixel(Width|Height)\s*:\s*(\d+)", out))
    if not d:
        raise SystemExit("sips returned no dims for %s" % path_)
    return int(d["Width"]), int(d["Height"])


def missing_frames():
    """(group, frame_index, target_abs, master_abs) for every hero frame without a master."""
    jobs = []
    for group, period, theme in GROUPS:
        gdir = os.path.join(IMG, group)
        if not os.path.isdir(gdir):
            print("  GROUP ABSENT (no such directory): %s" % group)
            continue
        for fn in sorted(os.listdir(gdir)):
            if not fn.lower().endswith(".webp"):
                continue
            rel = os.path.join(group, fn)
            master = os.path.join(OUT, master_name(rel))
            if os.path.exists(master):
                continue
            try:
                idx = int(os.path.splitext(fn)[0])
            except ValueError:
                print("  UNNUMBERED FRAME, skipped: %s" % rel)
                continue
            jobs.append((group, idx, period, theme, os.path.join(IMG, rel), master))
    return jobs


def viewbox_of(text):
    """Parse a master and return (w, h, root).  Refuses DTD/entity payloads."""
    if "<!DOCTYPE" in text or "<!ENTITY" in text or "&" in text:
        raise ValueError("master contains a DTD or an entity reference")
    root = ET.fromstring(text)
    vb = root.get("viewBox")
    if vb:
        p = [float(x) for x in re.split(r"[,\s]+", vb.strip())]
        if len(p) == 4:
            return p[2], p[3], root
    raise ValueError("no usable viewBox")


def main():
    dry = "--dry-run" in sys.argv
    os.makedirs(OUT, exist_ok=True)
    jobs = missing_frames()
    print("targets without a master: %d" % len(jobs))
    if not jobs:
        print("nothing to do")
        return 0

    written, stats, failures = 0, {}, []
    for group, idx, period, theme, target, master in jobs:
        w, h = sips_dims(target)
        svg = frame_svg(theme, idx / float(period), w, h)
        st = stats.setdefault(group, {"n": 0, "xml": 0, "aspect": 0, "brand": 0,
                                      "bodies": set()})
        st["n"] += 1
        try:
            mw, mh, root = viewbox_of(svg)
            st["xml"] += 1
            if root.tag.split("}")[-1] != "svg":
                failures.append((master, "root element is %r" % root.tag))
        except Exception as ex:
            failures.append((master, "XML/viewBox: %s" % ex))
            continue
        if abs(mw / mh - w / h) <= 0.02:
            st["aspect"] += 1
        else:
            failures.append((master, "aspect master %gx%g vs target %dx%d" % (mw, mh, w, h)))
        if "simplex" not in svg.lower() and "<title>POPOPX" in svg:
            st["brand"] += 1
        else:
            failures.append((master, "brand check: upstream name present, or no POPOPX title"))
        st["bodies"].add(hashlib.sha256(svg.encode()).hexdigest())
        if not dry:
            tmp = master + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(svg)
            os.replace(tmp, master)
        written += 1

    print("\n%-18s %5s %5s %7s %6s %8s" % ("group", "n", "xml", "aspect", "brand", "unique"))
    ok = True
    for group, _, _ in GROUPS:
        st = stats.get(group)
        if not st:
            continue
        distinct = len(st["bodies"])
        good = st["xml"] == st["n"] == st["aspect"] == st["brand"] and distinct == st["n"]
        ok = ok and good
        print("%-18s %5d %5d %7d %6d %8d   %s" % (
            group, st["n"], st["xml"], st["aspect"], st["brand"], distinct,
            "PASS" if good else "FAIL"))
    total = sum(s["n"] for s in stats.values())
    passed = sum(1 for s in stats.values())
    print("\nwrote %d master%s%s" % (written, "s" if written != 1 else "",
                                     " (dry-run)" if dry else ""))
    print("verification: %d groups checked, aspect gate within 2%% of target px" % passed)
    for m, why in failures[:20]:
        print("  FAIL %s | %s" % (os.path.basename(m), why))
    print("PASS/FAIL: %d masters pass, %d fail" % (total - len(failures), len(failures)))
    return 0 if ok and not failures else 1


if __name__ == "__main__":
    sys.exit(main())
