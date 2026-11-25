#!/usr/bin/env python3
"""Draw the 25 November 2026 world-news summary image, GTA VI / Vice City style.

Pure Pillow. Deterministic: same input -> same bytes every run.
Output: entry.png, 1024x1024, under 1 MiB.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(size, stops):
    """Vertical gradient through a list of (pos, color) stops."""
    img = Image.new("RGB", size)
    px = img.load()
    h = size[1]
    for y in range(h):
        t = y / max(1, h - 1)
        col = stops[-1][1]
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                f = 0.0 if p1 == p0 else (t - p0) / (p1 - p0)
                col = lerp(c0, c1, f)
                break
        for x in range(size[0]):
            px[x, y] = col
    return img


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_palm(draw, bx, by, s, flip, col):
    """A palm-tree silhouette rooted at (bx, by), height ~s."""
    # trunk: a gentle curve made of short segments
    pts = []
    steps = 12
    for i in range(steps + 1):
        t = i / steps
        x = bx + (s * 0.18 if flip else -s * 0.18) * t * t
        y = by - s * t
        pts.append((x, y))
    draw.line(pts, fill=col, width=max(3, int(s * 0.045)))
    tx, ty = pts[-1]
    # fronds: arcs drooping from the crown
    for ang in range(-160, 161, 40):
        rad = math.radians(ang if not flip else 180 - ang)
        ex = tx + math.cos(rad) * s * 0.42
        ey = ty + math.sin(rad) * s * 0.30 + s * 0.10
        mx = tx + math.cos(rad) * s * 0.22
        my = ty + math.sin(rad) * s * 0.16 - s * 0.06
        draw.line([(tx, ty), (mx, my), (ex, ey)], fill=col,
                  width=max(2, int(s * 0.02)))
    # coconuts
    draw.ellipse([tx - 5, ty + 2, tx + 5, ty + 12], fill=col)


# ---------------------------------------------------------------- stories
# (tag, colour, headline, one-line fact) — each verified against 2+ sources
# for Wednesday 25 November 2026.
STORIES = [
    ("HORMUZ", (255, 90, 60),
     "TANKERS HIT MINES, EXPLODE",
     "IRGC Navy: two oil tankers struck naval mines and caught fire in the Strait of Hormuz."),
    ("SPACE", (0, 229, 255),
     "PAKISTAN'S FIRST ASTRONAUT",
     "Shenzhou-24 lifts Zeeshan Ali to Tiangong, the first foreigner aboard China's station."),
    ("PACIFIC", (0, 255, 190),
     "SOLOMONS PICK AUSTRALIA",
     "Canberra signs treaty as primary security partner; no foreign bases; A$740m over 10 years."),
    ("COLOMBIA", (255, 214, 0),
     "HOSTAGES FREED IN CARTAGENA",
     "Forces storm an Exito supermarket after a 17-hour siege; one captor killed."),
    ("DHAKA", (140, 255, 120),
     "GARMENT PAY UP 36%",
     "Wage board lifts the minimum to 17,500 taka a month after weeks of protests."),
    ("UKRAINE", (90, 160, 255),
     "112 DRONES HIT UKRAINE",
     "Strikes kill two in Kyiv and Kharkiv regions; a bus is hit near Fedorivka."),
    ("BERLIN", (200, 120, 255),
     "MERZ: RUSSIA WANTS MORE",
     "Germany to lift defence to \u20ac139.4bn in the 2027 budget, 3.7% of GDP by 2030."),
    ("HUAWEI", (255, 80, 180),
     "HUAWEI GUILTY, 10 OF 12",
     "Brooklyn jury convicts on trade-secret theft and Iran sanctions; acquits on racketeering."),
    ("FOOTBALL", (190, 255, 60),
     "SENEGAL WIN AFCON BACK",
     "CAS restores the 2025 title, overturning CAF's 3-0 forfeit to Morocco."),
    ("GAZA", (255, 150, 40),
     "STORM THREATENS 1.76M IN TENTS",
     "Gaza officials warn of imminent disaster as a winter storm nears the Strip."),
]


def main():
    img = vgrad((W, H), [
        (0.00, (26, 4, 64)),     # deep violet night
        (0.30, (120, 16, 110)),  # magenta dusk
        (0.52, (255, 46, 136)),  # hot pink
        (0.68, (255, 110, 60)),  # orange sunset
        (0.80, (255, 190, 80)),  # golden horizon
        (1.00, (30, 4, 60)),     # dark floor
    ])
    d = ImageDraw.Draw(img, "RGBA")

    # ---- synthwave sun setting on the horizon, bottom centre
    cx, cy, r = 512, 1045, 150
    sun = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun)
    for yy in range(cy - r, cy + r + 1):
        t = (yy - (cy - r)) / (2 * r)
        col = lerp((255, 224, 102), (255, 60, 140), t)
        half = int(math.sqrt(max(0, r * r - (yy - cy) ** 2)))
        sd.line([(cx - half, yy), (cx + half, yy)], fill=col + (255,))
    img = Image.alpha_composite(img.convert("RGBA"), sun)
    d = ImageDraw.Draw(img, "RGBA")

    # ---- neon grid floor
    floor_y = 800
    for i in range(9):
        y = floor_y + i * i * 3 + i * 8
        if y < H:
            d.line([(0, y), (W, y)], fill=(255, 46, 136, 90), width=2)
    for gx in range(-W, 2 * W, 86):
        d.line([(W // 2 + gx, floor_y), (W // 2 + gx * 3, H)],
               fill=(0, 229, 255, 70), width=2)

    # ---- palm silhouettes
    draw_palm(d, 60, 1010, 300, False, (12, 2, 32))
    draw_palm(d, 990, 1015, 260, True, (12, 2, 32))
    draw_palm(d, 150, 1020, 170, False, (20, 4, 48))

    # ---- header
    d.rectangle([0, 0, W, 196], fill=(10, 2, 32, 110))
    d.line([(0, 196), (W, 196)], fill=(0, 229, 255, 255), width=4)

    def fit_font(text, start, path, max_w):
        size = start
        while size > 10:
            f = font(path, size)
            if d.textlength(text, font=f) <= max_w:
                return f
            size -= 2
        return font(path, 10)

    title = "VICE CITY DAILY"
    title_f = fit_font(title, 92, FONT_BOLD, 960)
    tw = d.textlength(title, font=title_f)
    x0 = (W - tw) / 2
    # neon glow: cyan offsets behind, pink face
    for ox, oy in [(-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2)]:
        d.text((x0 + ox, 18 + oy), title, font=title_f, fill=(0, 229, 255, 255))
    d.text((x0, 18), title, font=title_f, fill=(255, 46, 136, 255),
           stroke_width=2, stroke_fill=(255, 255, 255, 255))
    sub = "WEDNESDAY  \u2022  25 NOVEMBER 2026  \u2022  THE WORLD TODAY"
    sub_f = fit_font(sub, 34, FONT_BOLD, 980)
    sw = d.textlength(sub, font=sub_f)
    d.text(((W - sw) / 2, 128), sub, font=sub_f, fill=(255, 255, 255, 255))

    # ---- story panels: 2 columns x 5 rows
    tag_f = font(FONT_BOLD, 21)
    head_f = font(FONT_BOLD, 25)
    fact_f = font(FONT_REG, 17)
    px0, py0 = 16, 212
    pw, ph, gap = 488, 128, 12
    for i, (tag, col, head, fact) in enumerate(STORIES):
        col_i, row_i = i % 2, i // 2
        x = px0 + col_i * (pw + gap)
        y = py0 + row_i * (ph + gap)
        d.rounded_rectangle([x, y, x + pw, y + ph], radius=10,
                            fill=(8, 2, 28, 215), outline=col + (255,), width=3)
        # number + tag chip
        chip = f"{i + 1:02d}  {tag}"
        cw = d.textlength(chip, font=tag_f) + 18
        d.rounded_rectangle([x + 12, y + 10, x + 12 + cw, y + 38], radius=6,
                            fill=col + (255,))
        d.text((x + 21, y + 12), chip, font=tag_f, fill=(10, 2, 32, 255))
        # headline: one line, shrunk to fit
        hf = head_f
        while d.textlength(head, font=hf) > pw - 24 and hf.size > 16:
            hf = font(FONT_BOLD, hf.size - 1)
        d.text((x + 12, y + 46), head, font=hf, fill=(255, 255, 255, 255))
        # fact, up to 2 lines, below the headline
        flines = wrap(d, fact, fact_f, pw - 24)
        fy = y + 80
        for ln in flines[:2]:
            d.text((x + 12, fy), ln, font=fact_f, fill=(220, 220, 235, 255))
            fy += 19

    # ---- footer
    foot_f = font(FONT_BOLD, 20)
    foot = "make.fun  \u2022  SUM UP 25 NOVEMBER'S WORLD NEWS IN ONE IMAGE"
    fw = d.textlength(foot, font=foot_f)
    d.text(((W - fw) / 2, 982), foot, font=foot_f, fill=(255, 255, 255, 255),
           stroke_width=2, stroke_fill=(10, 2, 32, 255))

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
