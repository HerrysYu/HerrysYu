#!/usr/bin/env python3
"""Cute vertical short starring the Grok Bot round-ball avatar.

Official avatar language, from the Grok Bot design system: one simple shape,
two black eyes, glossy color. This film uses the circle — the round ball —
and an original melody. The hook borrows the meme phrase models say,
当然可以，好问题, without using anyone else's recording.
"""

from __future__ import annotations

import math
import subprocess
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
FONT_PATH = ROOT / "fonts" / "ZCOOLKuaiLe-Regular.ttf"
MEDIA = ROOT / "media"
OUT = MEDIA / "grok-keyi.mp4"
WAV = MEDIA / "score.wav"
POSTER = MEDIA / "poster.jpg"

W, H = 1080, 1920
FPS = 30
DURATION = 20.0
SR = 44100

BLUE = (16, 132, 254)
PINK = (255, 48, 156)
PURPLE = (145, 89, 254)
TEAL = (0, 188, 166)
ORANGE = (255, 152, 0)
INK = (74, 42, 96)

MOTIFS = [
    (0.2, 180, 420, 36, (255, 120, 170), "heart"),
    (1.4, 900, 360, 28, (255, 190, 90), "spark"),
    (2.8, 140, 820, 22, (150, 190, 255), "spark"),
    (4.0, 940, 760, 34, (190, 140, 255), "heart"),
    (6.2, 120, 560, 26, (255, 150, 190), "heart"),
    (8.6, 960, 500, 30, (255, 214, 120), "spark"),
    (11.8, 200, 340, 44, (255, 90, 150), "heart"),
    (12.4, 860, 300, 40, (255, 126, 186), "heart"),
    (13.1, 320, 260, 24, (255, 220, 140), "spark"),
    (13.6, 760, 240, 30, (186, 150, 255), "spark"),
    (15.2, 150, 300, 36, (255, 112, 168), "heart"),
    (16.0, 930, 340, 32, (120, 210, 255), "spark"),
    (18.2, 250, 390, 28, (255, 170, 200), "heart"),
    (18.8, 830, 360, 26, (255, 210, 130), "spark"),
]


def shade(rgb: tuple[int, int, int]) -> tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]:
    light = tuple(min(255, int(c + (255 - c) * 0.78)) for c in rgb)
    dark = tuple(max(0, int(c * 0.52)) for c in rgb)
    return light, rgb, dark


def make_ball(rgb: tuple[int, int, int], radius: int = 250, expr: str = "idle") -> Image.Image:
    size = radius * 2 + 80
    light, mid, dark = shade(rgb)
    yy, xx = np.mgrid[0:size, 0:size]
    cx = cy = (size - 1) / 2.0
    dx = (xx - cx) / radius
    dy = (yy - cy) / radius
    dist = np.sqrt(dx * dx + dy * dy)
    light_amt = np.clip(1.15 - ((dx + 0.38) ** 2 * 1.15 + (dy + 0.46) ** 2 * 1.35), 0, 1)
    rim = np.clip((dist - 0.62) / 0.38, 0, 1) ** 1.15
    spec = np.exp(-((dx + 0.36) ** 2) * 28 - ((dy + 0.46) ** 2) * 36)
    spec2 = np.exp(-((dx + 0.08) ** 2) * 10 - ((dy + 0.52) ** 2) * 14) * 0.18
    t = np.clip(light_amt, 0, 1)[:, :, None]
    col = np.array(dark) * (1 - t) + np.array(light) * t
    col = col * (1 - 0.55 * rim[:, :, None]) + np.array(dark) * (0.55 * rim[:, :, None])
    col = col + (spec * 150 + spec2 * 80)[:, :, None]
    warm = np.clip(-dy, 0, 1) * np.clip(1 - dist, 0, 1)
    col = col + warm[:, :, None] * np.array([18, 6, 4])
    col = np.clip(col, 0, 255)
    dist_px = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    alpha = np.clip((radius + 0.75 - dist_px) * 220, 0, 255)
    img = np.dstack([col, alpha]).astype(np.uint8)
    ball = Image.fromarray(img, "RGBA")
    draw_face(ball, expr, radius)
    return ball


def capsule(base: Image.Image, cx: float, cy: float, w: float, h: float, angle: float) -> None:
    pad = int(max(w, h) + 8)
    chip = Image.new("RGBA", (pad * 2, pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(chip)
    x0, y0 = pad - w / 2, pad - h / 2
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=min(w, h) / 2, fill=(18, 16, 24, 255))
    chip = chip.rotate(angle, resample=Image.Resampling.BICUBIC, center=(pad, pad))
    base.alpha_composite(chip, (int(cx - pad), int(cy - pad)))


def draw_face(ball: Image.Image, expr: str, radius: int) -> None:
    cx = cy = ball.size[0] / 2
    gap = radius * 0.30
    ey = cy + radius * 0.10
    blush = Image.new("RGBA", ball.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(blush)
    blush_a = 78 if expr in {"happy", "wink", "shy", "excited"} else 46
    br = radius * 0.16
    for sx in (-1, 1):
        bx = cx + sx * radius * 0.46
        by = cy + radius * 0.30
        bd.ellipse([bx - br, by - br * 0.62, bx + br, by + br * 0.62], fill=(255, 122, 168, blush_a))
    ball.alpha_composite(blush)

    if expr == "happy":
        capsule(ball, cx - gap, ey, radius * 0.28, radius * 0.095, 16)
        capsule(ball, cx + gap, ey, radius * 0.28, radius * 0.095, -16)
    elif expr == "excited":
        capsule(ball, cx - gap, ey - radius * 0.02, radius * 0.17, radius * 0.32, 6)
        capsule(ball, cx + gap, ey - radius * 0.02, radius * 0.17, radius * 0.32, -6)
    elif expr == "wink":
        capsule(ball, cx - gap, ey, radius * 0.16, radius * 0.30, 8)
        capsule(ball, cx + gap, ey + radius * 0.02, radius * 0.28, radius * 0.08, -8)
    elif expr == "shy":
        capsule(ball, cx - gap * 0.92, ey + radius * 0.08, radius * 0.145, radius * 0.32, 4)
        capsule(ball, cx + gap * 0.92, ey + radius * 0.08, radius * 0.145, radius * 0.32, -4)
    elif expr == "blink":
        capsule(ball, cx - gap, ey, radius * 0.24, radius * 0.06, 8)
        capsule(ball, cx + gap, ey, radius * 0.24, radius * 0.06, -8)
    else:
        capsule(ball, cx - gap, ey, radius * 0.145, radius * 0.23, 0)
        capsule(ball, cx + gap, ey, radius * 0.145, radius * 0.23, 0)


def make_heart(size: int, rgb: tuple[int, int, int]) -> Image.Image:
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    pts = []
    for i in range(90):
        t = i / 90 * math.tau
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((x, y))
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    pad = size * 0.12
    span = max(maxx - minx, maxy - miny)
    mapped = [
        (
            pad + (p[0] - minx) / span * (size - 2 * pad),
            pad + (p[1] - miny) / span * (size - 2 * pad),
        )
        for p in pts
    ]
    ImageDraw.Draw(im).polygon(mapped, fill=rgb + (235,))
    return im


def make_spark(size: int, rgb: tuple[int, int, int]) -> Image.Image:
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cx = cy = size / 2
    pts = []
    for i in range(8):
        ang = -math.pi / 2 + i * math.pi / 4
        r = size * (0.48 if i % 2 == 0 else 0.14)
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    ImageDraw.Draw(im).polygon(pts, fill=rgb + (240,))
    return im


def make_shadow() -> Image.Image:
    sh = Image.new("RGBA", (560, 160), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((30, 36, 530, 124), fill=(150, 90, 130, 120))
    return sh.filter(ImageFilter.GaussianBlur(16))


def blit(dst: Image.Image, src: Image.Image, x: float, y: float) -> None:
    xi, yi = int(x), int(y)
    dw, dh = dst.size
    sw, sh = src.size
    if xi >= dw or yi >= dh or xi + sw <= 0 or yi + sh <= 0:
        return
    sx0 = max(0, -xi)
    sy0 = max(0, -yi)
    dx0 = max(0, xi)
    dy0 = max(0, yi)
    dx1 = min(dw, xi + sw)
    dy1 = min(dh, yi + sh)
    crop = src.crop((sx0, sy0, sx0 + (dx1 - dx0), sy0 + (dy1 - dy0)))
    dst.alpha_composite(crop, (dx0, dy0))


def transform(sprite: Image.Image, scale_x: float, scale_y: float, angle: float) -> Image.Image:
    w = max(2, int(sprite.width * scale_x))
    h = max(2, int(sprite.height * scale_y))
    img = sprite.resize((w, h), Image.Resampling.LANCZOS)
    if abs(angle) > 0.2:
        img = img.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    return img


def ease_out_back(p: float) -> float:
    p = min(1.0, max(0.0, p))
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (p - 1) ** 3 + c1 * (p - 1) ** 2


def expression_at(t: float) -> str:
    blinks = (2.35, 6.55, 11.15, 16.05)
    if any(b <= t <= b + 0.12 for b in blinks):
        return "blink"
    if 14.55 <= t < 17.15:
        return "wink" if (t * 1.6) % 1.7 < 1.15 else "happy"
    if 9.55 <= t < 11.45:
        return "shy"
    if 11.7 <= t < 14.55:
        return "excited" if int(t * 4) % 2 == 0 else "happy"
    if t >= 17.55:
        return "shy" if t < 19.15 else "wink"
    if t >= 4.15:
        return "happy"
    return "idle"


def pose_at(t: float) -> tuple[float, float, float, float]:
    """Return center_y offset, scale_x, scale_y, rotation degrees."""
    if t < 1.05:
        p = t / 1.05
        if p < 0.72:
            u = p / 0.72
            y = -780 * (1 - u * u)
            return y, 1.0, 1.04, 0.0
        u = (p - 0.72) / 0.28
        squash = math.sin(u * math.pi)
        return 18 * squash, 1 + 0.16 * squash, 1 - 0.14 * squash, 0.0

    phase = (t * 2) % 1  # 120 bpm
    hop = max(0.0, math.sin(math.pi * phase)) ** 1.2
    y = -hop * 34
    sx, sy, ang = 1.0, 1.0, math.sin(t * 1.3) * 2.2
    if phase < 0.12:
        land = math.sin(phase / 0.12 * math.pi)
        sx += 0.07 * land
        sy -= 0.07 * land
    else:
        sy += 0.045 * hop
        sx -= 0.03 * hop
    if 6.15 <= t < 9.15:
        ang += math.sin((t - 6.15) * 7.2) * 9
    if 9.55 <= t < 11.45:
        hug = math.sin((t - 9.55) / 1.9 * math.pi)
        sx += 0.20 * hug
        sy -= 0.14 * hug
        y += 10 * hug
    if 11.7 <= t < 14.6:
        y -= hop * 28
    return y, sx, sy, ang


LYRICS = [
    (1.05, 4.15, "当然可以，好问题", 96),
    (4.15, 8.15, "你一问，我就亮眼睛", 80),
    (8.15, 11.70, "先点点头，再抱一抱", 80),
    (11.70, 14.55, "当然可以", 132),
    (14.55, 17.55, "好问题", 148),
    (17.55, 20.05, "圆球接住啦", 92),
]

BUBBLES = [
    (1.25, 3.35, "嗯？"),
    (3.40, 5.90, "当然可以"),
    (8.30, 11.20, "抱抱"),
    (17.70, 19.85, "嘿嘿"),
]


def active_span(spans, t):
    for a, b, *rest in spans:
        if a <= t < b:
            return (a, b, *rest)
    return None


def build_background() -> Image.Image:
    yy = np.linspace(0, 1, H)[:, None]
    top = np.array([255, 214, 236])
    mid = np.array([255, 246, 232])
    bot = np.array([214, 236, 255])
    col = np.where(yy < 0.55, top + (mid - top) * (yy / 0.55), mid + (bot - mid) * ((yy - 0.55) / 0.45))
    rgb = np.repeat(col[:, None, :], W, axis=1).astype(np.uint8)
    img = Image.fromarray(rgb).convert("RGBA")
    blobs = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(blobs)
    spots = [
        (80, 260, 340, (255, 170, 205, 90)),
        (860, 180, 280, (255, 214, 150, 80)),
        (140, 1500, 420, (186, 220, 255, 90)),
        (900, 1280, 360, (214, 190, 255, 80)),
        (540, 1680, 260, (255, 255, 255, 50)),
    ]
    for x, y, r, c in spots:
        d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    blobs = blobs.filter(ImageFilter.GaussianBlur(28))
    img.alpha_composite(blobs)
    return img


def render_frame(
    t: float,
    bg: Image.Image,
    balls: dict[str, Image.Image],
    minis: dict[tuple[str, str], Image.Image],
    hearts: dict[tuple[int, int, int], Image.Image],
    sparks: dict[tuple[int, int, int], Image.Image],
    shadow: Image.Image,
    font_cache: dict[int, ImageFont.FreeTypeFont],
) -> Image.Image:
    frame = bg.copy()
    yoff, sx, sy, ang = pose_at(t)
    expr = expression_at(t)
    ball = balls[expr]
    shown = transform(ball, 1.22 * sx, 1.22 * sy, ang)
    cx, cy = 540, 860 + yoff
    hop = max(0.0, -yoff / 70)
    sh = shadow
    sh_w = int(sh.width * (1.05 - 0.28 * min(hop, 1)))
    sh_h = int(sh.height * (0.86 - 0.18 * min(hop, 1)))
    sh_r = sh.resize((max(2, sh_w), max(2, sh_h)), Image.Resampling.BILINEAR)
    arr = np.array(sh_r)
    arr[..., 3] = (arr[..., 3].astype(np.float32) * (0.45 + 0.55 * (1 - min(hop, 1)))).astype(np.uint8)
    blit(frame, Image.fromarray(arr, "RGBA"), cx - sh_r.width / 2, 1126 - sh_r.height / 2)

    # little friends arrive for the last bow
    friends = [
        (-460, PINK, 0.0),
        (-300, PURPLE, 0.10),
        (300, TEAL, 0.18),
        (460, ORANGE, 0.28),
    ]
    if t >= 17.45:
        for dx, color, delay in friends:
            p = ease_out_back((t - 17.45 - delay) / 0.55)
            if p <= 0:
                continue
            fexpr = "happy" if (t + delay) % 0.5 < 0.36 else "idle"
            sprite = minis[(color, fexpr)]
            phase = (t * 2 + delay * 3) % 1
            fh = max(0.0, math.sin(math.pi * phase)) ** 1.2
            fs = transform(sprite, 0.62 * p, 0.62 * p * (1 + 0.05 * fh), math.sin(t * 3 + dx) * 4)
            blit(frame, fs, cx + dx - fs.width / 2, 1120 - fh * 18 - fs.height / 2)

    blit(frame, shown, cx - shown.width / 2, cy - shown.height / 2)

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # drifting sparkles and hearts
    for i, (t0, x, y, size, rgb, kind) in enumerate(MOTIFS):
        life = 3.4 if kind == "heart" else 2.4
        if not (t0 <= t <= t0 + life):
            continue
        u = (t - t0) / life
        alpha_k = max(0.0, math.sin(min(1.0, u) * math.pi)) ** 0.8
        yy = y - u * (160 if kind == "heart" else 90)
        xx = x + math.sin(t * 1.4 + i) * 16
        sprite = hearts[rgb] if kind == "heart" else sparks[rgb]
        sp = sprite.resize((size, size), Image.Resampling.LANCZOS)
        if alpha_k < 0.98:
            a = np.array(sp)
            a[..., 3] = (a[..., 3].astype(np.float32) * alpha_k).astype(np.uint8)
            sp = Image.fromarray(a, "RGBA")
        blit(overlay, sp, xx, yy)

    # top identity pill
    pill = ImageFont.truetype(str(FONT_PATH), 40)
    label = "Grok Bot"
    lw = pill.getlength(label)
    px, py, pw, ph = 64, 78, lw + 108, 72
    draw.rounded_rectangle([px, py, px + pw, py + ph], radius=36, fill=(255, 255, 255, 214))
    mini = balls["happy"].resize((52, 52), Image.Resampling.LANCZOS)
    blit(overlay, mini, px + 12, py + 10)
    draw.text((px + 74, py + 14), label, font=pill, fill=INK + (255,))

    bub = active_span(BUBBLES, t)
    if bub:
        a, b, text = bub
        u = (t - a) / max(0.001, b - a)
        pop = ease_out_back(min(1.0, (t - a) / 0.28))
        fade = 1 if u < 0.82 else max(0, 1 - (u - 0.82) / 0.18)
        bf = font_cache[54]
        tw = bf.getlength(text)
        bw, bh = tw + 56, 78
        bx = min(760, cx + 150)
        by = cy - 340
        bubble = Image.new("RGBA", (int(bw + 20), int(bh + 28)), (0, 0, 0, 0))
        bd = ImageDraw.Draw(bubble)
        bd.rounded_rectangle([0, 0, bw, bh], radius=32, fill=(255, 255, 255, int(235 * fade)))
        bd.polygon([(28, bh - 2), (58, bh - 2), (18, bh + 20)], fill=(255, 255, 255, int(235 * fade)))
        bd.text((28, 16), text, font=bf, fill=(255, 79, 140, int(255 * fade)))
        bubble = bubble.resize((max(2, int(bubble.width * pop)), max(2, int(bubble.height * pop))), Image.Resampling.LANCZOS)
        blit(overlay, bubble, bx, by)

    line = active_span(LYRICS, t)
    if line:
        a, b, text, size = line
        u = (t - a) / (b - a)
        pop = ease_out_back(min(1.0, (t - a) / 0.26))
        font = font_cache[size]
        kicker_font = font_cache[36]
        kicker = "官方圆球 · 可爱版"
        tw = font.getlength(text)
        kw = kicker_font.getlength(kicker)
        plate_w = max(tw, kw) + 120
        plate_h = size + 108
        plate = Image.new("RGBA", (int(plate_w), int(plate_h)), (0, 0, 0, 0))
        pd = ImageDraw.Draw(plate)
        pd.rounded_rectangle([0, 0, plate_w - 1, plate_h - 1], radius=46, fill=(255, 255, 255, 196))
        pd.text(((plate_w - kw) / 2, 22), kicker, font=kicker_font, fill=(150, 110, 160, 255))
        sung_n = max(1, int(math.ceil(u * len(text) - 1e-6)))
        x = (plate_w - tw) / 2
        baseline = 64
        for i, ch in enumerate(text):
            col = (255, 70, 138, 255) if i < sung_n else (196, 176, 206, 255)
            pd.text((x, baseline), ch, font=font, fill=col)
            x += font.getlength(ch)
        plate = plate.resize((max(2, int(plate.width * pop)), max(2, int(plate.height * pop))), Image.Resampling.LANCZOS)
        blit(overlay, plate, (W - plate.width) / 2, 1768 - plate.height)

    frame.alpha_composite(overlay)

    if t < 0.28:
        veil = Image.new("RGBA", (W, H), (255, 246, 250, int(255 * (1 - t / 0.28))))
        frame.alpha_composite(veil)
    if t > 19.55:
        a = int(255 * min(1, (t - 19.55) / 0.45))
        frame.alpha_composite(Image.new("RGBA", (W, H), (255, 246, 250, a)))
    return frame


def midi(n: float) -> float:
    return 440.0 * 2 ** ((n - 69) / 12)


def render_audio() -> np.ndarray:
    n = int(SR * DURATION)
    mix = np.zeros(n, dtype=np.float64)

    def add(samples: np.ndarray, start: float, vol: float = 1.0) -> None:
        i = int(start * SR)
        j = min(n, i + len(samples))
        if j > i:
            mix[i:j] += samples[: j - i] * vol

    def pluck(freq: float, dur: float) -> np.ndarray:
        m = int(SR * dur)
        tt = np.arange(m) / SR
        env = np.exp(-tt * 3.4) * (1 - np.exp(-tt * 80))
        wave_s = (
            np.sin(2 * math.pi * freq * tt)
            + 0.28 * np.sin(2 * math.pi * freq * 2 * tt)
            + 0.08 * np.sin(2 * math.pi * freq * 3 * tt)
            + 0.18 * np.sin(2 * math.pi * freq * 1.005 * tt)
        )
        return wave_s * env

    def kick() -> np.ndarray:
        m = int(SR * 0.16)
        tt = np.arange(m) / SR
        freq = 150 * np.exp(-tt * 22) + 52
        phase = 2 * math.pi * np.cumsum(freq) / SR
        return np.sin(phase) * np.exp(-tt * 16)

    def hat() -> np.ndarray:
        m = int(SR * 0.05)
        tt = np.arange(m) / SR
        noise = np.random.default_rng(3).standard_normal(m)
        noise = np.diff(noise, prepend=0)
        return noise * np.exp(-tt * 55)

    # quarters of a candy melody, 120 bpm
    lead = [
        (0.00, 76, 0.42),
        (0.50, 79, 0.42),
        (1.00, 81, 0.48),
        (1.50, 79, 0.40),
        (2.00, 76, 0.42),
        (2.50, 72, 0.46),
        (3.00, 76, 0.40),
        (3.50, 79, 0.70),
        (4.00, 76, 0.40),
        (4.50, 79, 0.40),
        (5.00, 81, 0.46),
        (5.50, 84, 0.42),
        (6.00, 81, 0.40),
        (6.50, 79, 0.42),
        (7.00, 76, 0.46),
        (7.50, 72, 0.70),
        (8.00, 81, 0.36),
        (8.50, 84, 0.36),
        (9.00, 81, 0.40),
        (9.50, 79, 0.42),
        (10.00, 76, 0.36),
        (10.50, 79, 0.36),
        (11.00, 81, 0.80),
        (12.00, 84, 0.42),
        (12.50, 84, 0.36),
        (13.00, 81, 0.40),
        (13.50, 79, 0.42),
        (14.00, 76, 0.36),
        (14.50, 79, 0.36),
        (15.00, 84, 0.55),
        (15.50, 88, 0.40),
        (16.00, 81, 0.40),
        (16.50, 79, 0.40),
        (17.00, 76, 0.46),
        (17.50, 74, 0.40),
        (18.00, 72, 0.50),
        (18.50, 76, 0.45),
        (19.00, 79, 0.95),
    ]
    for start, note, dur in lead:
        vol = 0.20 if start < 11.7 else 0.26
        add(pluck(midi(note), dur + 0.12), start, vol)
        if start >= 11.7:
            add(pluck(midi(note - 12), dur + 0.2), start, 0.07)

    # bass on the downbeat, a fifth softer on the off-downbeat
    for i in range(40):
        start = i * 0.5
        root = 48 if start < 8 or start >= 16 else 53 if start < 12 else 48
        if i % 2 == 0:
            add(pluck(midi(root), 0.42), start, 0.16)
        elif i % 4 == 1:
            add(pluck(midi(root + 7), 0.28), start, 0.07)
        if i % 2 == 0:
            add(kick(), start, 0.34 if start >= 11.5 else 0.22)
        else:
            add(hat(), start, 0.05 if start >= 4 else 0.03)

    # landing boing
    m = int(SR * 0.45)
    tt = np.arange(m) / SR
    f = 180 + 420 * np.exp(-tt * 7)
    boing = np.sin(2 * math.pi * np.cumsum(f) / SR) * np.exp(-tt * 5.5)
    add(boing, 0.78, 0.18)

    fade_in = int(SR * 0.05)
    fade_out = int(SR * 0.45)
    mix[:fade_in] *= np.linspace(0, 1, fade_in)
    mix[-fade_out:] *= np.linspace(1, 0, fade_out)
    peak = np.max(np.abs(mix)) or 1
    mix = mix / peak * 0.9
    left = mix
    right = np.concatenate([np.zeros(90), mix[:-90]]) * 0.94
    return np.stack([left, right], axis=1)


def save_wav(stereo: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = np.clip(stereo, -1, 1)
    with wave.open(str(path), "w") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(SR)
        interleaved = pcm.reshape(-1)
        handle.writeframes((interleaved * 32767).astype(np.int16).tobytes())


def load_assets():
    exprs = ["idle", "happy", "excited", "wink", "shy", "blink"]
    balls = {e: make_ball(BLUE, 250, e) for e in exprs}
    colors = [PINK, PURPLE, TEAL, ORANGE]
    minis = {}
    for c in colors:
        for e in ("idle", "happy"):
            minis[(c, e)] = make_ball(c, 120, e)
    hearts = {rgb: make_heart(96, rgb) for *_, rgb, kind in MOTIFS if kind == "heart"}
    sparks = {rgb: make_spark(96, rgb) for *_, rgb, kind in MOTIFS if kind == "spark"}
    fonts = {s: ImageFont.truetype(str(FONT_PATH), s) for s in (36, 40, 54, 80, 92, 96, 132, 148)}
    return balls, minis, hearts, sparks, make_shadow(), fonts


def render_previews() -> None:
    balls, minis, hearts, sparks, shadow, fonts = load_assets()
    bg = build_background()
    out = MEDIA / "preview"
    out.mkdir(parents=True, exist_ok=True)
    for t in (0.55, 2.1, 5.4, 10.1, 13.05, 15.4, 18.7):
        frame = render_frame(t, bg, balls, minis, hearts, sparks, shadow, fonts)
        path = out / f"t{t:.2f}.jpg"
        frame.convert("RGB").save(path, quality=90)
        print(path)


def render_video() -> None:
    balls, minis, hearts, sparks, shadow, fonts = load_assets()
    bg = build_background()
    MEDIA.mkdir(parents=True, exist_ok=True)
    audio = render_audio()
    save_wav(audio, WAV)
    frames = int(DURATION * FPS)
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{W}x{H}",
        "-r",
        str(FPS),
        "-i",
        "-",
        "-i",
        str(WAV),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-crf",
        "18",
        "-preset",
        "veryfast",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        "-movflags",
        "+faststart",
        str(OUT),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.stdin is not None
    poster_saved = False
    try:
        for i in range(frames):
            t = i / FPS
            frame = render_frame(t, bg, balls, minis, hearts, sparks, shadow, fonts).convert("RGB")
            if not poster_saved and t >= 13.0:
                frame.save(POSTER, quality=92)
                poster_saved = True
            proc.stdin.write(frame.tobytes())
            if i % 60 == 0:
                print(f"frame {i}/{frames}", flush=True)
    finally:
        proc.stdin.close()
    err = proc.stderr.read().decode("utf-8", "replace") if proc.stderr else ""
    code = proc.wait()
    if code != 0:
        raise SystemExit(err[-2000:])
    print(OUT)


if __name__ == "__main__":
    import sys

    if "--preview" in sys.argv:
        render_previews()
    else:
        render_video()
