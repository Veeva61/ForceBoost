"""Draws the ForceBoost icon variants (256x256) for Thunderstore. Usage: python make_icons.py <out_dir>"""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = sys.argv[1]
K = 4
W = 256 * K


def font(size):
    for f in ("C:/Windows/Fonts/impact.ttf", "C:/Windows/Fonts/arialbd.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def title(im, text, color, y=196, size=46):
    d = ImageDraw.Draw(im)
    f = font(size)
    w = d.textlength(text, font=f)
    x = (256 - w) / 2
    for ox in range(-3, 4):
        for oy in range(-3, 4):
            if ox * ox + oy * oy <= 9:
                d.text((x + ox, y + oy), text, font=f, fill=(12, 14, 26))
    d.text((x, y), text, font=f, fill=color)


def bg(top, bottom):
    im = Image.new("RGB", (W, W))
    d = ImageDraw.Draw(im)
    for y in range(W):
        t = y / W
        d.line([0, y, W, y], fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return im


def glow(im, draw_fn, radius):
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    blurred = layer.filter(ImageFilter.GaussianBlur(radius))
    im.paste(blurred, (0, 0), blurred)
    im.paste(layer, (0, 0), layer)


def hand(d, cx, cy, s, col):
    """Open palm facing the viewer, fingers up (stylised)."""
    r = lambda v: v * s * K
    d.rounded_rectangle([cx - r(30), cy - r(10), cx + r(30), cy + r(48)], radius=r(16), fill=col)
    for i, (dx, h) in enumerate([(-22, 46), (-7, 56), (8, 54), (23, 42)]):
        d.rounded_rectangle([cx + r(dx) - r(7), cy - r(h), cx + r(dx) + r(7), cy + r(4)], radius=r(7), fill=col)
    # thumb
    d.rounded_rectangle([cx - r(52), cy + r(2), cx - r(26), cy + r(16)], radius=r(7), fill=col)
    d.polygon([(cx - r(30), cy + r(2)), (cx - r(26), cy + r(30)), (cx - r(40), cy + r(16))], fill=col)
    # wrist
    d.rectangle([cx - r(22), cy + r(40), cx + r(22), cy + r(80)], fill=col)


def crate(d, cx, cy, s, rot=0.0):
    r = s * K / 2
    pts = []
    for a in (45, 135, 225, 315):
        ang = math.radians(a + rot)
        pts.append((cx + r * 1.41 * math.cos(ang), cy + r * 1.41 * math.sin(ang)))
    d.polygon(pts, fill=(176, 120, 62), outline=(96, 60, 28), width=3 * K)
    d.line([pts[0], pts[2]], fill=(120, 78, 38), width=4 * K)
    d.line([pts[1], pts[3]], fill=(120, 78, 38), width=4 * K)


def finish(im, name, label, color):
    im = im.resize((256, 256), Image.LANCZOS)
    title(im, label, color)
    im.save(os.path.join(OUT, name))
    print("saved", name)


# A: hand pulling a crate with energy rings
im = bg((18, 16, 48), (44, 18, 72))
CX, CY = 76 * K, 130 * K


def rings(d):
    for i, rr in enumerate((30, 48, 66, 84)):
        a = 230 - i * 40
        d.arc([CX + 40 * K - rr * K, CY - 40 * K - rr * K, CX + 40 * K + rr * K, CY - 40 * K + rr * K],
              200, 320, fill=(120, 200, 255, a), width=5 * K)
    for i in range(7):
        y = CY - 70 * K + i * 12 * K
        d.line([110 * K, y, 205 * K, y - 34 * K], fill=(140, 220, 255, 150), width=2 * K)


glow(im, rings, 6 * K)
d = ImageDraw.Draw(im)
crate(d, 196 * K, 72 * K, 54, rot=14)
glow(im, lambda dd: hand(dd, CX, CY, 1.05, (235, 238, 245, 255)), 4 * K)
finish(im, "icon_A.png", "FORCE x10", (120, 210, 255))

# B: big glowing palm, objects flying in from all sides
im = bg((10, 22, 40), (6, 10, 22))
CX, CY = 128 * K, 104 * K


def aura(d):
    for rr, a in ((110, 60), (85, 90), (60, 140)):
        d.ellipse([CX - rr * K, CY - rr * K, CX + rr * K, CY + rr * K], outline=(90, 180, 255, a), width=6 * K)


glow(im, aura, 10 * K)
random.seed(4)
d = ImageDraw.Draw(im)
for ang, dist, sz in ((200, 100, 30), (330, 96, 26), (20, 100, 24), (150, 104, 22)):
    a = math.radians(ang)
    x, y = CX + dist * K * math.cos(a), CY + dist * K * math.sin(a)
    # speed streak toward the hand
    d.line([x, y, x + 34 * K * math.cos(a), y + 34 * K * math.sin(a)], fill=(110, 190, 255), width=3 * K)
    crate(d, x, y, sz, rot=ang)
glow(im, lambda dd: hand(dd, CX, CY + 6 * K, 0.95, (240, 244, 250, 255)), 6 * K)
finish(im, "icon_B.png", "FORCE", (255, 205, 60))

# C: minimal - magnet-style arrow into a fist/palm, bold x10
im = bg((40, 14, 14), (14, 6, 10))
CX, CY = 70 * K, 112 * K
d = ImageDraw.Draw(im)
hand(d, CX, CY, 0.9, (240, 240, 245))


def arrow(d):
    for i, x in enumerate((210, 168, 126)):
        a = 255 - i * 60
        d.polygon([(x * K, 64 * K), ((x - 30) * K, 92 * K), (x * K, 120 * K), ((x - 12) * K, 92 * K)],
                  fill=(255, 120, 60, a))


glow(im, arrow, 5 * K)
d = ImageDraw.Draw(im)
f = font(64 * K)
d.text((150 * K, 120 * K), "x10", font=f, fill=(255, 200, 70), stroke_width=4 * K, stroke_fill=(20, 8, 8))
finish(im, "icon_C.png", "FORCE BOOST", (255, 160, 70))
