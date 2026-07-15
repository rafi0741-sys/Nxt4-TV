#!/usr/bin/env python3
"""Generate the full NXTV Android launcher icon set at build time.

Draws the stacked  N [crossed-remotes] / T4  mark in brand colors using Pillow
(no browser needed), then writes every density's legacy + round + adaptive
foreground PNGs, plus the adaptive-icon XML and background color resource,
directly into the Android res tree.

Usage: python3 gen_icons.py <android_res_dir>
   e.g. python3 gen_icons.py android/app/src/main/res
"""
import os, sys, glob, math
from PIL import Image, ImageDraw, ImageFont

BG   = (20, 37, 27)     # #14251B dark green
MINT = (232, 240, 232)  # #E8F0E8
LIME = (195, 236, 63)   # #C3EC3F

def find_font():
    cands = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for c in cands:
        if os.path.exists(c):
            return c
    hits = glob.glob("/usr/share/fonts/**/*Bold*.ttf", recursive=True)
    return hits[0] if hits else None

def draw_remote(d, cx, cy, size, angle, body):
    """Draw one remote (rounded body + power dot + button grid + d-pad), rotated."""
    # Render remote upright on its own layer then rotate+paste for clean edges.
    S = size
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    w = S * 0.30
    h = S * 0.86
    x0 = (S - w) / 2
    y0 = (S - h) / 2
    r = w / 2
    ld.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=r, fill=body)
    # power dot (accent unless body is lime)
    dot = LIME if body == MINT else BG
    pr = w * 0.20
    pcx = S / 2
    pcy = y0 + h * 0.16
    ld.ellipse([pcx - pr, pcy - pr, pcx + pr, pcy + pr], fill=dot)
    # 2x2 button grid (bg-colored)
    br = w * 0.11
    gx = w * 0.22
    gy1 = y0 + h * 0.42
    gy2 = y0 + h * 0.55
    for bx in (pcx - gx, pcx + gx):
        for by in (gy1, gy2):
            ld.ellipse([bx - br, by - br, bx + br, by + br], fill=BG)
    # d-pad pill near bottom
    dw = w * 0.34
    dh = h * 0.14
    dcx = pcx
    dcy = y0 + h * 0.80
    ld.rounded_rectangle([dcx - dw/2, dcy - dh/2, dcx + dw/2, dcy + dh/2],
                         radius=dw/2, fill=dot)
    layer = layer.rotate(angle, resample=Image.BICUBIC, center=(S/2, S/2))
    return layer

def draw_t_remote(size):
    """Draw the B2 'T-shaped remote' on a transparent size×size layer.
    Wide rounded crossbar on top + narrow remote body below = a T silhouette."""
    S = size
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    # scale the 150x190 design into S with a little vertical margin
    def sx(v): return v / 150.0 * S
    def sy(v): return v / 190.0 * S
    # crossbar (wide top)
    ld.rounded_rectangle([sx(12), sy(8), sx(138), sy(54)], radius=sx(16), fill=MINT)
    # remote body (narrow stem)
    ld.rounded_rectangle([sx(54), sy(46), sx(96), sy(184)], radius=sx(20), fill=MINT)
    # lime power dot on crossbar
    def circ(cx, cy, r, fill):
        ld.ellipse([sx(cx)-sx(r), sy(cy)-sy(r), sx(cx)+sx(r), sy(cy)+sy(r)], fill=fill)
    circ(118, 31, 10, LIME)
    # 2x2 button grid (bg colored)
    for cx in (66, 84):
        for cy in (86, 108):
            circ(cx, cy, 5, BG)
    # lime d-pad pill
    ld.rounded_rectangle([sx(64), sy(140), sx(86), sy(170)], radius=sx(11), fill=LIME)
    return layer

def make_master(px, with_bg=True):
    """Render the master icon at px×px. Transparent bg if with_bg=False."""
    img = Image.new("RGBA", (px, px), BG + (255,) if with_bg else (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font_path = find_font()
    # Single row: N  ×  [T-remote]  4. Keep it inside the circular safe zone.
    fs = int(px * 0.30)
    font = ImageFont.truetype(font_path, fs) if font_path else ImageFont.load_default()
    xfont = ImageFont.truetype(font_path, int(fs * 0.72)) if font_path else font

    def tw(s, fnt=font):
        bb = d.textbbox((0, 0), s, font=fnt)
        return bb[2] - bb[0], bb[3] - bb[1], bb

    nW, nH, nbb = tw("N")
    xW, xH, xbb = tw("\u00d7", xfont)
    vW, vH, vbb = tw("V")
    rem = int(fs * 1.02)          # T-remote glyph box
    remW = int(rem * 0.82)        # visual width narrower than box

    g = int(px * 0.015)           # gap between glyphs
    total_w = nW + g + xW + g + remW + g + vW
    x = (px - total_w) / 2
    midY = px / 2

    # N
    d.text((x - nbb[0], midY - nH/2 - nbb[1]), "N", font=font, fill=MINT)
    x += nW + g
    # ×
    d.text((x - xbb[0], midY - xH/2 - xbb[1] - fs*0.04), "\u00d7", font=xfont, fill=MINT)
    x += xW + g
    # T-remote (vertically centered on the row)
    tr = draw_t_remote(rem)
    img.alpha_composite(tr, (int(x - (rem-remW)/2), int(midY - rem/2)))
    x += remW + g
    # V
    d.text((x - vbb[0], midY - vH/2 - vbb[1]), "V", font=font, fill=LIME)

    return img

def main():
    res = sys.argv[1] if len(sys.argv) > 1 else "android/app/src/main/res"
    os.makedirs(res, exist_ok=True)

    master = make_master(512, with_bg=True)
    master_fg = make_master(512, with_bg=False)

    legacy = {"mdpi":48,"hdpi":72,"xhdpi":96,"xxhdpi":144,"xxxhdpi":192}
    adaptive = {"mdpi":108,"hdpi":162,"xhdpi":216,"xxhdpi":324,"xxxhdpi":432}

    for d, px in legacy.items():
        folder = os.path.join(res, "mipmap-" + d)
        os.makedirs(folder, exist_ok=True)
        sq = master.resize((px, px), Image.LANCZOS).convert("RGB")
        sq.save(os.path.join(folder, "ic_launcher.png"))
        mask = Image.new("L", (px, px), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, px, px), fill=255)
        rnd = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        rnd.paste(master.resize((px, px), Image.LANCZOS), (0, 0), mask)
        rnd.save(os.path.join(folder, "ic_launcher_round.png"))

    for d, px in adaptive.items():
        folder = os.path.join(res, "mipmap-" + d)
        os.makedirs(folder, exist_ok=True)
        canvas = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        inner = int(px * 0.62)
        logo = master_fg.resize((inner, inner), Image.LANCZOS)
        off = (px - inner) // 2
        canvas.alpha_composite(logo, (off, off))
        canvas.save(os.path.join(folder, "ic_launcher_foreground.png"))

    anydpi = os.path.join(res, "mipmap-anydpi-v26")
    os.makedirs(anydpi, exist_ok=True)
    adaptive_xml = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
        '    <background android:drawable="@color/ic_launcher_background" />\n'
        '    <foreground android:drawable="@mipmap/ic_launcher_foreground" />\n'
        '</adaptive-icon>\n'
    )
    open(os.path.join(anydpi, "ic_launcher.xml"), "w").write(adaptive_xml)
    open(os.path.join(anydpi, "ic_launcher_round.xml"), "w").write(adaptive_xml)

    values = os.path.join(res, "values")
    os.makedirs(values, exist_ok=True)
    open(os.path.join(values, "ic_launcher_background.xml"), "w").write(
        '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
        '    <color name="ic_launcher_background">#14251B</color>\n</resources>\n'
    )
    print("NXTV icon set generated into", res)

if __name__ == "__main__":
    main()
