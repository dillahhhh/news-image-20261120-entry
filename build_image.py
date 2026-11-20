#!/usr/bin/env python3
"""Build entry.png for make.fun news-image-20261120.

Front-page broadsheet, 1024x1024, flat vector, warm paper, navy ink,
limited red accent. All text drawn with PIL (DejaVu) — no baked AI text.
Run: python3 build_image.py  -> writes entry.png next to this file.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

W = H = 1024
PAPER = (247, 241, 222)
NAVY = (20, 38, 78)
NAVY_SOFT = (40, 54, 90)
RED = (192, 57, 43)
GRAY = (72, 72, 82)
GRAY_DARK = (45, 45, 55)   # darker sub grey (rev4: legible at ~300px)
RULE = (20, 38, 78)

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap by pixel width. Returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_font(draw, text, path, start_size, max_w, min_size=10):
    size = start_size
    while size > min_size:
        fnt = font(path, size)
        if draw.textlength(text, font=fnt) <= max_w:
            return fnt
        size -= 1
    return font(path, min_size)


def white_to_alpha(img):
    """White background -> transparent, soft threshold on min channel."""
    img = img.convert("RGBA")
    r, g, b, _ = img.split()
    m = ImageChops.darker(ImageChops.darker(r, g), b)
    lut = [0 if v >= 250 else 255 if v <= 200 else int((250 - v) * 255 / 50)
           for v in range(256)]
    img.putalpha(m.point(lut))
    return img


def cover_crop(img, tw, th):
    """Resize + center-crop to exactly tw x th."""
    sw, sh = img.size
    scale = max(tw / sw, th / sh)
    img = img.resize((round(sw * scale), round(sh * scale)), Image.LANCZOS)
    x = (img.width - tw) // 2
    y = (img.height - th) // 2
    return img.crop((x, y, x + tw, y + th))


def contain_fit(img, tw, th):
    """Scale to fit inside tw x th (no crop), centered on transparent canvas.

    Used for the hero ICJ art (rev4): cover_crop clipped the gavel handle
    at the right edge; contain keeps the whole drawing visible.
    """
    sw, sh = img.size
    scale = min(tw / sw, th / sh)
    img = img.resize((round(sw * scale), round(sh * scale)), Image.LANCZOS)
    canvas = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    canvas.paste(img, ((tw - img.width) // 2, (th - img.height) // 2))
    return canvas


def band_crop(img, tw, th, y0_frac, y1_frac, x0_frac=0.0, x1_frac=1.0):
    """Take the [x0,x1]x[y0,y1] region of the image, cover-crop to tw x th."""
    sw, sh = img.size
    x0, x1 = int(sw * x0_frac), int(sw * x1_frac)
    y0, y1 = int(sh * y0_frac), int(sh * y1_frac)
    band = img.crop((x0, y0, x1, y1))
    return cover_crop(band, tw, th)


def letterspaced(draw, xy, text, fnt, fill, tracking=4):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking
    return x


# ---------------------------------------------------------------- icons
def draw_market_chart(d, box):
    """Falling market line (red), PIL-drawn. No green tick (rev4: read as artifact)."""
    x0, y0, x1, y1 = box
    pad = 8
    # axes
    d.line([(x0 + pad, y1 - pad), (x1 - pad, y1 - pad)], fill=NAVY, width=3)
    d.line([(x0 + pad, y0 + pad), (x0 + pad, y1 - pad)], fill=NAVY, width=3)
    # descending line (red), jagged
    pts = [(x0 + 16, y0 + 18), (x0 + 60, y0 + 30), (x0 + 95, y0 + 26),
           (x0 + 135, y0 + 48), (x0 + 175, y0 + 44), (x0 + 215, y0 + 62),
           (x0 + 255, y0 + 58), (x0 + 295, y0 + 78)]
    d.line(pts, fill=RED, width=5, joint="curve")
    for p in pts:
        d.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], fill=RED)


def draw_gamepad(d, box):
    """Simple flat gamepad, navy with red buttons."""
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    w, h = (x1 - x0) * 0.86, (y1 - y0) * 0.62
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2],
                        radius=int(h * 0.45), fill=NAVY)
    # grips
    d.ellipse([cx - w / 2 - 6, cy + h * 0.05, cx - w / 2 + 26, cy + h * 0.55],
              fill=NAVY)
    d.ellipse([cx + w / 2 - 26, cy + h * 0.05, cx + w / 2 + 6, cy + h * 0.55],
              fill=NAVY)
    # d-pad (left)
    dx = cx - w * 0.28
    d.rectangle([dx - 5, cy - 16, dx + 5, cy + 16], fill=PAPER)
    d.rectangle([dx - 16, cy - 5, dx + 16, cy + 5], fill=PAPER)
    # buttons (right): 4 dots, one red
    bx = cx + w * 0.28
    for ox, oy, col in [(-12, -10, PAPER), (12, -10, PAPER),
                        (-12, 10, PAPER), (12, 10, RED)]:
        d.ellipse([bx + ox - 6, cy + oy - 6, bx + ox + 6, cy + oy + 6],
                  fill=col)
    # sticks
    d.ellipse([cx - 26, cy + 12, cx - 14, cy + 24], fill=PAPER)
    d.ellipse([cx + 14, cy + 12, cx + 26, cy + 24], fill=PAPER)


def draw_tower(d, box):
    """Stylised wide skyscraper with window grid, red crack, thin smoke."""
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    # tower body (wide, flat top with a small peak)
    bx0, bx1 = cx - 62, cx + 62
    by0, by1 = y0 + 16, y1 - 4
    d.polygon([(bx0, by0 + 10), (cx, by0), (bx1, by0 + 10),
               (bx1, by1), (bx0, by1)], fill=NAVY)
    # window grid (cream)
    for r in range(5):
        for c in range(6):
            wx = bx0 + 10 + c * 18
            wy = by0 + 20 + r * 13
            d.rectangle([wx, wy, wx + 10, wy + 7], fill=PAPER)
    # red crack near the top
    d.line([(cx + 18, by0 + 8), (cx + 12, by0 + 16), (cx + 20, by0 + 24),
            (cx + 12, by0 + 32)], fill=RED, width=3)
    # thin smoke wisp rising from the top
    sx, sy = cx + 30, by0 - 2
    d.line([(sx, sy), (sx + 8, sy - 6), (sx + 2, sy - 12), (sx + 10, sy - 18)],
           fill=NAVY_SOFT, width=2)
    d.line([(sx + 16, sy + 2), (sx + 22, sy - 4), (sx + 16, sy - 10)],
           fill=GRAY, width=2)


def draw_medal(d, box):
    """Sports medal: red ribbon + navy disc with red star (rev4, replaces IMF debt bars)."""
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2 + 6
    # ribbon straps (red) from the top edge down to the medal
    d.polygon([(cx - 16, y0 + 2), (cx - 2, y0 + 2),
               (cx - 14, cy - 22), (cx - 28, cy - 22)], fill=RED)
    d.polygon([(cx + 2, y0 + 2), (cx + 16, y0 + 2),
               (cx + 28, cy - 22), (cx + 14, cy - 22)], fill=RED)
    # medal disc (navy) with paper ring
    r = 34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=NAVY)
    d.ellipse([cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8], fill=PAPER)
    # red five-point star in the middle
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = 20 if i % 2 == 0 else 8
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    d.polygon(pts, fill=RED)


# ---------------------------------------------------------------- page
def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    MX = 24                      # outer margin
    CW = W - 2 * MX              # 976 content width

    # ---- masthead (y 24..148) ----
    label_fnt = font(BOLD, 25)
    lw = sum(d.textlength(c, font=label_fnt) + 5 for c in "THE WORLD IN ONE DAY")
    letterspaced(d, (MX + (CW - lw) // 2, 30), "THE WORLD IN ONE DAY",
                 label_fnt, NAVY, tracking=5)
    date = "FRIDAY, 20 NOVEMBER 2026"
    date_fnt = fit_font(d, date, BOLD, 66, CW)
    dw = d.textlength(date, font=date_fnt)
    d.text((MX + (CW - dw) / 2, 62), date, font=date_fnt, fill=NAVY)
    d.rectangle([MX, 140, MX + CW, 145], fill=NAVY)
    d.rectangle([MX, 148, MX + CW, 149], fill=NAVY)

    # ---- hero: ICJ (y 160..498) ----
    hy0, hy1 = 160, 498
    d.rectangle([MX, hy0, MX + CW, hy1], outline=NAVY, width=2)
    icj = Image.open(os.path.join(ASSETS, "media-generation-icj-0-ba260889-322a-46a9-9f76-3a9e85942e74.png"))
    icj = white_to_alpha(icj)
    icj = contain_fit(icj, 452, hy1 - hy0 - 16)   # rev4: no crop, gavel handle intact
    img.paste(icj, (MX + 8, hy0 + 8), icj)
    tx = MX + 478
    tw = MX + CW - tx - 16
    d.text((tx, hy0 + 22), "THE HAGUE", font=font(BOLD, 20), fill=RED)
    head_fnt = font(BOLD, 42)
    lines = wrap(d, "ICJ RULES MYANMAR COMMITTED GENOCIDE", head_fnt, tw)
    y = hy0 + 54
    for ln in lines:
        d.text((tx, y), ln, font=head_fnt, fill=NAVY)
        y += 50
    sub_fnt = font(REG, 22)
    # rev5: "9-6 judges" (Claude: bare "9-6" is meaningless); "ruling"
    # dropped so the line stays 2 lines (bottom 480, frame 498).
    slines = wrap(d, "Thu 19 Nov • 9–6 judges • First ICJ genocide finding against a state",
                  sub_fnt, tw)
    y += 10
    for ln in slines:
        d.text((tx, y), ln, font=sub_fnt, fill=NAVY_SOFT)
        y += 28

    # ---- grid: 2 rows x 3 cols (y 512..1000) ----
    gy0, gy1 = 512, 1000
    gutter = 12
    pw = (CW - 2 * gutter) // 3          # 317
    ph = (gy1 - gy0 - gutter) // 2       # 238
    cols = [MX + i * (pw + gutter) for i in range(3)]
    rows = [gy0, gy0 + ph + gutter]

    summit = white_to_alpha(Image.open(os.path.join(
        ASSETS, "media-generation-summit-0-a2405d40-72a4-4a1a-95ad-8cfa0a4d509e.png")))
    kyiv = white_to_alpha(Image.open(os.path.join(
        ASSETS, "media-generation-kyiv-0-3f29e11e-6fe5-41d1-9f7f-0a1d5b4e4a55.png")))
    riyadh = white_to_alpha(Image.open(os.path.join(
        ASSETS, "media-generation-riyadh-0-03bfc5b7-1ef1-46c9-bb82-aabe04311fe9.png")))

    panels = [
        # (row, col, icon_kind, headline, sub, icon_h, sub_size)
        # rev5: subs at 18px except Kyiv (17px — its 3-line sub overflows
        # the tile at 18px); leading = sub_size + 3 (20 at 17px, as rev4).
        (0, 0, ("img", summit, 0.06, 0.55),
         "TRUMP, XI & PUTIN HOLD FIRST THREE-WAY SUMMIT",
         "Shenzhen • Thu 19 Nov", 102, 18),
        (0, 1, ("img", kyiv, 0.52, 1.0),
         "RUSSIA STRIKES KYIV; POLAND AIRSPACE BREACHED",
         ["8 killed, 28 injured (reports)",
          "Poland says 2 missiles + 1 drone entered airspace"], 80, 17),
        (0, 2, ("chart", None, None, None),
         "NIKKEI −5.1% IN TOKYO",
         # rev5: single-index headline (Claude: "ASIA SLUMP" is wider than
         # the evidence shown); Anthropic clause dropped (unexplained).
         "Fri: Nikkei −5.1% • Thu: S&P −2.0%", 88, 18),
        (1, 0, ("tower", None, None, None),
         "HOUTHI MISSILE DAMAGES SAUDI WEALTH-FUND TOWER",
         # rev5: icon 102 -> 94 — the 3-line headline needs the headroom
         # (at 102 the sub's last line ended 1px past the tile bottom).
         "Thu 19 Nov • Saudi Civil Defense confirms damage", 94, 18),
        (1, 1, ("pad", None, None, None),
         "GTA 6 EST. DAY-ONE SALES $2.36BN",
         "Launched Thu 19 Nov • Sensor Tower estimate", 102, 18),
        (1, 2, ("medal", None, None, None),
         "MARATHON CHAMP BANNED 3 YEARS FOR DOPING",
         # split into two balanced lines (rev4): one-string wrap orphans "Nov"
         # rev5: icon 102 -> 94 lifts the sub 8px off the bottom rule (Claude).
         ["Peres Jepchirchir • EPO", "Thu 19 Nov"], 94, 18),
    ]

    hfnt = font(BOLD, 22)
    for (r, c, icon, head, sub, icon_h, sub_size) in panels:
        x0, y0 = cols[c], rows[r]
        x1, y1 = x0 + pw, y0 + ph
        # icon zone (Kyiv's is shorter so its 2-line sub fits)
        ix0, iy0, ix1, iy1 = x0 + 6, y0 + 6, x1 - 6, y0 + 6 + icon_h
        kind = icon[0]
        if kind == "img":
            im, f0, f1 = icon[1], icon[2], icon[3]
            crop = band_crop(im, ix1 - ix0, iy1 - iy0, f0, f1,
                             icon[4] if len(icon) > 4 else 0.0,
                             icon[5] if len(icon) > 5 else 1.0)
            img.paste(crop, (ix0, iy0), crop)
        elif kind == "chart":
            draw_market_chart(d, (ix0, iy0, ix1, iy1))
        elif kind == "tower":
            draw_tower(d, (ix0, iy0, ix1, iy1))
        elif kind == "pad":
            draw_gamepad(d, (ix0, iy0, ix1, iy1))
        elif kind == "medal":
            draw_medal(d, (ix0, iy0, ix1, iy1))
        # headline + sub
        ty = iy1 + 8
        for ln in wrap(d, head, hfnt, pw - 12):
            d.text((x0 + 6, ty), ln, font=hfnt, fill=NAVY)
            ty += 27
        ty += 2
        sfnt = font(REG, sub_size)
        sub_lines = sub if isinstance(sub, list) else [sub]
        for s in sub_lines:
            for ln in wrap(d, s, sfnt, pw - 12):
                d.text((x0 + 6, ty), ln, font=sfnt, fill=GRAY_DARK)
                ty += sub_size + 3

    # broadsheet rules between panels
    for i in (1, 2):
        vx = cols[i] - gutter // 2
        d.line([(vx, gy0), (vx, gy1)], fill=NAVY, width=1)
    hy = rows[1] - gutter // 2
    d.line([(MX, hy), (MX + CW, hy)], fill=NAVY, width=1)
    d.rectangle([MX, gy1, MX + CW, gy1 + 2], fill=NAVY)

    out = os.path.join(HERE, "entry.png")
    img.save(out, optimize=True)
    print("saved", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
