#!/usr/bin/env python3
"""VICE CITY DAILY — one image summing up the world news of
Tuesday 25 November 2026, drawn in a GTA VI / Vice City style:
neon sunset, synthwave sun, palm silhouettes and a glowing grid floor.

Built with Pillow only; saves entry.png (1024x1024).
"""

import math

from PIL import Image, ImageDraw, ImageFont

SIZE = 1024
SKY_TOP = (24, 6, 46)
SKY_MID = (122, 24, 112)
SKY_LOW = (255, 92, 88)
FLOOR = (10, 5, 24)
PANEL = (14, 10, 34)
WHITE = (255, 255, 255)
BODY_GREY = (208, 204, 220)
PINK = (255, 60, 180)
CYAN = (0, 224, 255)
SUN_TOP = (255, 214, 90)
SUN_BOT = (255, 84, 150)
SILHOUETTE = (12, 4, 22)

FONT_DIR = "/usr/share/fonts/truetype/liberation"
SANS = f"{FONT_DIR}/LiberationSans-Regular.ttf"
SANS_BOLD = f"{FONT_DIR}/LiberationSans-Bold.ttf"


def fnt(path, size):
    return ImageFont.truetype(path, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sky_gradient(img, horizon):
    """Vertical sunset bands from deep purple down to the horizon."""
    d = ImageDraw.Draw(img)
    for y in range(horizon):
        if y < horizon * 0.55:
            col = lerp(SKY_TOP, SKY_MID, y / (horizon * 0.55))
        else:
            col = lerp(SKY_MID, SKY_LOW, (y - horizon * 0.55) /
                       (horizon * 0.45))
        d.line([0, y, SIZE, y], fill=col)


def synth_sun(cx, cy, r):
    """A striped synthwave sun: warm gradient disc with slits cut
    through its lower half, growing thicker toward the bottom."""
    sun = Image.new("RGBA", (2 * r, 2 * r), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun)
    slits = [(int(r * 1.18), 3), (int(r * 1.38), 5),
             (int(r * 1.58), 7), (int(r * 1.78), 9)]
    for yy in range(2 * r):
        if any(a <= yy < a + w for a, w in slits):
            continue
        t = yy / (2 * r)
        col = lerp(SUN_TOP, SUN_BOT, t)
        dy = yy - r
        half = int(math.sqrt(max(0, r * r - dy * dy)))
        if half > 0:
            sd.line([r - half, yy, r + half, yy], fill=col + (255,))
    return sun


def grid_floor(d, horizon):
    """Perspective neon grid from the horizon to the bottom edge."""
    d.rectangle([0, horizon, SIZE, SIZE], fill=FLOOR)
    d.line([0, horizon, SIZE, horizon], fill=PINK, width=3)
    vanish = (SIZE // 2, horizon)
    for i in range(-8, 9):
        x_bottom = SIZE // 2 + i * 170
        d.line([vanish[0] + i * 42, horizon, x_bottom, SIZE],
               fill=CYAN, width=2)
    y = horizon
    step = 6
    while y < SIZE:
        d.line([0, y, SIZE, y], fill=CYAN, width=2)
        step = int(step * 1.55) + 2
        y += step


def palm(d, base_x, base_y, height, lean=1):
    """A palm silhouette: curved trunk with a crown of drooping fronds."""
    cx = base_x + lean * int(height * 0.16)
    cy = base_y - height
    trunk_pts = []
    for i in range(13):
        t = i / 12
        x = base_x + (cx - base_x) * t * t + lean * 6 * math.sin(t * 2.2)
        y = base_y - height * t
        trunk_pts.append((x, y))
    d.line(trunk_pts, fill=SILHOUETTE, width=6, joint="curve")
    for k in range(7):
        ang = math.radians(-165 + k * 27)
        tip_x = cx + math.cos(ang) * height * 0.52
        tip_y = cy + math.sin(ang) * height * 0.42 + height * 0.16
        mid_x = cx + math.cos(ang) * height * 0.30
        mid_y = cy + math.sin(ang) * height * 0.26 - height * 0.06
        d.line([(cx, cy), (mid_x, mid_y), (tip_x, tip_y)],
               fill=SILHOUETTE, width=4, joint="curve")
    d.ellipse([cx - 6, cy - 2, cx + 6, cy + 10], fill=SILHOUETTE)
    d.ellipse([cx + 4, cy + 2, cx + 14, cy + 12], fill=SILHOUETTE)


def wrapped_lines(draw, text, f, max_width):
    """Split text into lines that fit max_width in the given font."""
    lines = []
    line = ""
    for word in text.split():
        trial = word if line == "" else line + " " + word
        if line == "" or draw.textlength(trial, font=f) <= max_width:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def paragraph(draw, x, y, text, path, size, max_width, fill=WHITE, step=None):
    f = fnt(path, size)
    if step is None:
        step = round(size * 1.3)
    out = []
    for line in wrapped_lines(draw, text, f, max_width):
        out.append(line)
        draw.text((x, y), line, font=f, fill=fill)
        y += step
    return y


def story_card(d, x, y, w, h, tag, headline, body, border):
    d.rectangle([x, y, x + w, y + h], fill=PANEL, outline=border, width=2)
    d.text((x + 12, y + 12), tag, font=fnt(SANS_BOLD, 12), fill=PINK)
    hy = paragraph(d, x + 12, y + 34, headline, SANS_BOLD, 17, w - 24,
                   step=21)
    paragraph(d, x + 12, max(y + 106, hy + 4), body, SANS, 12, w - 24,
              fill=BODY_GREY, step=15)


LEAD = ("HORMUZ  •  ENERGY SECURITY",
        "TWO TANKERS HIT MINES IN THE STRAIT OF HORMUZ",
        "Two oil tankers struck mines and caught fire in the approaches "
        "to the strait early on Tuesday. Iran's navy said the ships "
        "were on an unauthorised route with navigation systems "
        "switched off.")

STORIES = [
    ("SPACE", "PAKISTAN'S FIRST ASTRONAUT REACHES TIANGONG",
     "Shenzhou-24 launched at 08:18 Beijing time and docked with "
     "Tiangong hours later. Muhammad Zeeshan Ali, 40, is the first "
     "Pakistani astronaut aboard."),
    ("PACIFIC", "AUSTRALIA SIGNS SECURITY TREATY WITH SOLOMON ISLANDS",
     "Albanese and Wale signed the treaty in Canberra, making "
     "Australia the Solomons' primary security partner, with "
     "A$740m over 10 years."),
    ("COLOMBIA", "ALL HOSTAGES FREED AFTER CARTAGENA SUPERMARKET SIEGE",
     "Security forces stormed an Exito supermarket in Cartagena "
     "after a 17-hour standoff, freeing the last 20 hostages and "
     "killing one gunman."),
    ("DHAKA", "BANGLADESH GARMENT WAGE RISES 36%",
     "The wage board raised the garment minimum wage from 12,500 to "
     "17,500 taka a month (about US$136), effective December. "
     "Workers had demanded 30,000 taka."),
    ("UKRAINE", "112 DRONES IN OVERNIGHT ATTACK ON UKRAINE",
     "Russia launched 112 drones overnight; defences shot down 88. "
     "A supermarket burned in Kyiv region, killing one; a minibus "
     "was hit in Kharkiv region, injuring seven."),
    ("BERLIN", "MERZ: RUSSIA 'WANTS MORE THAN UKRAINE'",
     "Friedrich Merz told the Bundestag that Russia 'wants more "
     "than Ukraine' and Europe will do everything to deter Moscow. "
     "Defence spending hits €139.4bn in 2027."),
    ("TECH", "HUAWEI GUILTY ON 10 OF 12 US CHARGES",
     "A Brooklyn jury found Huawei and three units guilty on 10 of "
     "12 criminal counts, including bank fraud, trade-secret theft "
     "and sanctions breaches."),
    ("FOOTBALL", "SENEGAL HANDED BACK AFRICA CUP TITLE",
     "The Court of Arbitration for Sport upheld Senegal's appeal, "
     "overturning the ruling that gave the 2025 Africa Cup final "
     "3-0 to Morocco. The original 1-0 win stands."),
    ("GAZA", "STORM THREATENS 1.76 MILLION IN GAZA TENTS",
     "Gaza's media office warned a powerful storm threatens 1.76 "
     "million displaced Palestinians living in tents. A storm on "
     "6 November already flooded 70,000 tents."),
]


def build_page():
    img = Image.new("RGB", (SIZE, SIZE), SKY_TOP)
    sky_gradient(img, 560)
    d = ImageDraw.Draw(img)
    grid_floor(d, 560)
    sun = synth_sun(880, 120, 110)
    img.paste(sun, (880 - 110, 120 - 110), sun)
    d = ImageDraw.Draw(img)
    palm(d, 985, 300, 150, lean=-1)
    palm(d, 80, 1015, 190, lean=1)

    d.text((44, 34), "VICE CITY DAILY", font=fnt(SANS_BOLD, 62), fill=PINK)
    d.text((40, 30), "VICE CITY DAILY", font=fnt(SANS_BOLD, 62), fill=WHITE)
    d.text((40, 108), "WEDNESDAY  •  25 NOVEMBER 2026",
           font=fnt(SANS_BOLD, 20), fill=CYAN)
    d.text((40, 140), "THE WORLD TODAY — IN ONE PICTURE",
           font=fnt(SANS, 14), fill=BODY_GREY)
    d.line([40, 168, 984, 168], fill=PINK, width=2)

    tag, headline, body = LEAD
    d.rectangle([40, 196, 984, 364], fill=PANEL, outline=CYAN, width=3)
    d.text((56, 208), tag, font=fnt(SANS_BOLD, 13), fill=CYAN)
    hy = paragraph(d, 56, 232, headline, SANS_BOLD, 27, 912, step=33)
    paragraph(d, 56, max(308, hy + 6), body, SANS, 15, 912,
              fill=BODY_GREY, step=19)

    cw, chh, gap = 301, 172, 16
    for i, (tag, headline, body) in enumerate(STORIES):
        story_card(d, 40 + (i % 3) * (cw + gap),
                   380 + (i // 3) * (chh + gap), cw, chh, tag, headline,
                   body, PINK if i % 2 == 0 else CYAN)

    d.rectangle([0, 940, SIZE, 968], fill=(8, 4, 20))
    foot = ("Compiled from Reuters, Al Jazeera, Dawn, Channel News Asia, "
            "Straits Times and others  •  25 November 2026")
    ff = fnt(SANS, 12)
    d.text(((SIZE - d.textlength(foot, font=ff)) / 2, 946), foot, font=ff,
           fill=BODY_GREY)
    return img


if __name__ == "__main__":
    page = build_page()
    page.save("entry.png", optimize=True)
    print("saved entry.png", page.size)
