#!/usr/bin/env python3
"""VELMARA — travel poster for a place that isn't there.

Generates a 1024x1024 travel poster for Velmara, an invented archipelago
of floating islands drifting above a twilight sea under twin moons.

Stdlib only. No network, no timestamps, fixed seed: two runs produce
byte-identical PNG output.

Usage:
    python3 main.py            # writes /output/entry.png
    MAKEFUN_OUTPUT_DIR=/tmp/o python3 main.py
"""

import math
import os
import random
import struct
import zlib

W, H = 1024, 1024
SEED = 20261121

# ---------------------------------------------------------------- palette
INK = (24, 18, 58)          # deep indigo (text / banner)
CREAM = (250, 238, 205)     # poster text
GOLD = (232, 184, 96)       # frame + accents
SKY_TOP = (26, 20, 66)
SKY_MID = (96, 58, 138)
SKY_LOW = (255, 166, 104)
MOON = (250, 240, 210)
MOON_SHADE = (214, 196, 160)
MOUNTAIN_FAR = (74, 52, 110)
MOUNTAIN_NEAR = (48, 34, 84)
SEA_TOP = (44, 92, 128)
SEA_BOT = (18, 40, 74)
ISLAND_TOP = (58, 96, 74)
ISLAND_ROCK = (52, 40, 74)
WATERFALL = (178, 222, 235)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 characters, '#' = ink pixel.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
}

# ---------------------------------------------------------------- canvas
px = bytearray(W * H * 3)


def set_pixel(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = color


def blend_pixel(x, y, color, alpha):
    """Alpha-blend color over the existing pixel (alpha 0..1)."""
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i] = int(px[i] * (1 - alpha) + color[0] * alpha)
        px[i + 1] = int(px[i + 1] * (1 - alpha) + color[1] * alpha)
        px[i + 2] = int(px[i + 2] * (1 - alpha) + color[2] * alpha)


def fill_rect(x0, y0, x1, y1, color):
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(W, x1), min(H, y1)
    for y in range(y0, y1):
        base = (y * W + x0) * 3
        for x in range(x0, x1):
            i = base + (x - x0) * 3
            px[i], px[i + 1], px[i + 2] = color


def hline(x0, x1, y, color):
    for x in range(max(0, x0), min(W, x1)):
        set_pixel(x, y, color)


def vline(x, y0, y1, color):
    for y in range(max(0, y0), min(H, y1)):
        set_pixel(x, y, color)


def circle(cx, cy, r, color):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                set_pixel(x, y, color)


def ellipse(cx, cy, rx, ry, color):
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                set_pixel(x, y, color)


def triangle(x0, y0, x1, y1, x2, y2, color):
    """Filled triangle via scanlines."""
    pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
    (ax, ay), (bx, by), (cx, cy) = pts
    if ay == cy:
        return
    for y in range(ay, cy + 1):
        if y < by:
            t1 = (y - ay) / (by - ay) if by != ay else 0.0
            xa = ax + (bx - ax) * t1
        else:
            t1 = (y - by) / (cy - by) if cy != by else 0.0
            xa = bx + (cx - bx) * t1
        t2 = (y - ay) / (cy - ay)
        xb = ax + (cx - ax) * t2
        hline(int(min(xa, xb)), int(max(xa, xb)) + 1, y, color)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---------------------------------------------------------------- text
def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(s, cx, y, scale, color):
    """Draw string s centred on cx, top edge at y."""
    total = text_width(s, scale)
    x = cx - total // 2
    for ch in s:
        glyph = FONT.get(ch.upper(), FONT[" "])
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "#":
                    fill_rect(x + gx * scale, y + gy * scale,
                              x + (gx + 1) * scale, y + (gy + 1) * scale,
                              color)
        x += 6 * scale


# ---------------------------------------------------------------- scene
def sky_color_at(y):
    """Sky gradient colour at row y (matches draw_sky)."""
    if y < 380:
        return lerp(SKY_TOP, SKY_MID, y / 380.0)
    return lerp(SKY_MID, SKY_LOW, (y - 380) / 280.0)


def draw_sky(rng):
    for y in range(0, 660):
        hline(0, W, y, sky_color_at(y))
    # stars in the upper sky
    for _ in range(140):
        x = rng.randrange(40, W - 40)
        y = rng.randrange(40, 330)
        r = rng.choice([1, 1, 1, 2])
        bright = rng.choice([CREAM, CREAM, GOLD])
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r:
                    blend_pixel(x + dx, y + dy, bright, 0.85)


def draw_moons():
    # large full moon, upper right
    circle(790, 190, 86, MOON)
    circle(760, 165, 14, MOON_SHADE)
    circle(815, 210, 20, MOON_SHADE)
    circle(795, 150, 9, MOON_SHADE)
    circle(830, 165, 7, MOON_SHADE)
    # small crescent moon, upper left — the bite is painted with the
    # local sky colour so the crescent blends into the gradient
    circle(180, 150, 46, MOON)
    for yy in range(150 - 40, 150 + 40):
        for xx in range(198 - 40, 198 + 40):
            if (xx - 198) ** 2 + (yy - 138) ** 2 <= 40 * 40:
                set_pixel(xx, yy, sky_color_at(yy))
    # halo rings
    for r in (92, 98):
        for a in range(0, 360, 2):
            x = int(790 + r * math.cos(math.radians(a)))
            y = int(190 + r * math.sin(math.radians(a)))
            blend_pixel(x, y, MOON, 0.25)


def draw_mountains():
    # far ridge
    for x in range(W):
        h = (math.sin(x * 0.011 + 1.7) * 46
             + math.sin(x * 0.004 + 0.4) * 70
             + math.sin(x * 0.031) * 14)
        top = int(560 + h)
        vline(x, top, 664, MOUNTAIN_FAR)
    # near ridge, darker
    for x in range(W):
        h = (math.sin(x * 0.017 + 4.2) * 34
             + math.sin(x * 0.006 + 2.1) * 52
             + math.sin(x * 0.043 + 1.0) * 10)
        top = int(600 + h)
        vline(x, top, 664, MOUNTAIN_NEAR)


def draw_floating_island(cx, cy, rx, ry, rng, with_tower=False):
    """A floating island: grassy top, tapering rock underside, waterfall."""
    ellipse(cx, cy, rx, ry, ISLAND_TOP)
    # rock underside tapering to a point
    triangle(cx - rx + 8, cy + ry // 2, cx + rx - 8, cy + ry // 2,
             cx, cy + ry + int(rx * 0.9), ISLAND_ROCK)
    # grass highlight
    ellipse(cx, cy - 3, rx - 6, max(4, ry - 8), (74, 124, 92))
    # little trees
    for tx in (cx - rx // 2, cx + rx // 3, cx - rx // 6):
        triangle(tx, cy - ry - 26, tx - 9, cy - ry + 2,
                 tx + 9, cy - ry + 2, (30, 66, 48))
    # waterfall from the island's edge (two parallel threads)
    wx = cx + rx // 2
    for y in range(cy + ry // 2, cy + ry + int(rx * 0.55)):
        if y % 2 == 0:
            set_pixel(wx, y, WATERFALL)
            set_pixel(wx + 3, y, WATERFALL)
            set_pixel(wx + 1, y + 1, WATERFALL)
    if with_tower:
        # small lighthouse tower on the main island
        fill_rect(cx - 12, cy - ry - 58, cx + 12, cy - ry, CREAM)
        fill_rect(cx - 16, cy - ry - 66, cx + 16, cy - ry - 58, GOLD)
        fill_rect(cx - 6, cy - ry - 52, cx + 6, cy - ry - 40, GOLD)
        triangle(cx - 18, cy - ry - 66, cx + 18, cy - ry - 66,
                 cx, cy - ry - 84, (150, 52, 64))
        # little cottage beside the lighthouse, warm window lit
        fill_rect(cx + 44, cy - ry - 26, cx + 76, cy - ry, (232, 196, 150))
        triangle(cx + 40, cy - ry - 26, cx + 80, cy - ry - 26,
                 cx + 60, cy - ry - 44, (150, 52, 64))
        fill_rect(cx + 55, cy - ry - 18, cx + 65, cy - ry - 8, GOLD)


def draw_sea(rng):
    for y in range(664, H):
        t = (y - 664) / (H - 664)
        hline(0, W, y, lerp(SEA_TOP, SEA_BOT, t))
    # moon reflection: narrow column of short broken dashes under the moon
    for y in range(668, 800, 6):
        wob = int(10 * math.sin(y * 0.05) + rng.randrange(-5, 6))
        half = 12 + rng.randrange(0, 10)
        for x in range(790 - half + wob, 790 + half + wob):
            blend_pixel(x, y, MOON, 0.4)
    # horizontal shimmer streaks
    for _ in range(90):
        x = rng.randrange(30, W - 200)
        y = rng.randrange(680, 790)
        ln = rng.randrange(20, 90)
        for dx in range(ln):
            blend_pixel(x + dx, y, CREAM, 0.18)


def draw_birds():
    birds = [(300, 250, 14), (350, 220, 11), (420, 280, 13),
             (620, 300, 12), (660, 260, 10)]
    for bx, by, s in birds:
        for i in range(s):
            set_pixel(bx - i, by - i // 2, INK)
            set_pixel(bx + i, by - i // 2, INK)


def draw_banner():
    # deep banner band across the lower poster for the title
    fill_rect(96, 806, 928, 972, INK)
    hline(96, 928, 806, GOLD)
    hline(96, 928, 807, GOLD)
    hline(96, 928, 971, GOLD)
    hline(96, 928, 972, GOLD)


def draw_frame():
    # double decorative border
    for x in range(24, 1000):
        for y in (24, 25, 26, 997, 998, 999):
            set_pixel(x, y, GOLD)
    for y in range(24, 1000):
        for x in (24, 25, 26, 997, 998, 999):
            set_pixel(x, y, GOLD)
    for x in range(40, 984):
        for y in (40, 983):
            set_pixel(x, y, CREAM)
    for y in range(40, 984):
        for x in (40, 983):
            set_pixel(x, y, CREAM)
    # corner diamonds
    for cx, cy in ((24, 24), (999, 24), (24, 999), (999, 999)):
        for d in range(-10, 11):
            set_pixel(cx + d, cy, GOLD)
            set_pixel(cx, cy + d, GOLD)
            set_pixel(cx + d // 2, cy + d // 2, GOLD)


def build_poster():
    rng = random.Random(SEED)
    draw_sky(rng)
    draw_moons()
    draw_mountains()
    # floating islands above the sea
    draw_floating_island(300, 470, 150, 34, rng, with_tower=True)
    draw_floating_island(700, 400, 105, 26, rng)
    draw_floating_island(880, 520, 80, 20, rng)
    draw_birds()
    draw_sea(rng)
    draw_banner()
    draw_text("VELMARA", 512, 824, 9, CREAM)
    draw_text("WHERE THE SKY KEEPS ITS ISLANDS", 512, 906, 3, GOLD)
    draw_text("VISIT THE UNREACHABLE", 512, 938, 2, CREAM)
    draw_frame()


# ---------------------------------------------------------------- PNG writer
def chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw.extend(px[y * W * 3:(y + 1) * W * 3])
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    build_poster()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(path)
    print(f"wrote {path} ({size} bytes, {W}x{H})")


if __name__ == "__main__":
    main()
