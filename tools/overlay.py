#!/usr/bin/env python3
"""Subtitle / lower-third / logo overlays for Bible Director films (1920x1080).

Layout matches automation/references/subtitle-layout-example-jonah-2.png:
lower-third bar along the bottom, "<BOOK> <CH>:<A>-<B>" + "KING JAMES VERSION" left of the gold divider,
verse text (Cormorant Garamond, white, max 3 lines) right of it, channel logo top-right at 40 % opacity.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
GOLD = (233, 160, 74, 255)
WHITE = (250, 246, 238, 255)
TEXT_X, TEXT_R = 332, 1790          # verse text column
INNER_TOP, INNER_BOT = 856, 1036     # between the bar's gold lines
VERSE_SIZE, LINE_H, MAX_LINES = 46, 58, 3

def _font(fonts, weight, size):
    return ImageFont.truetype(os.path.join(fonts, f"CormorantGaramond_{weight}.ttf"), size)

def base_overlay(refs, fonts, reference, logo=True, logo_opacity=0.40, bar_opacity=0.80):
    """Static layer: bar (80 % opacity so the picture shows through) + reference block (+ logo)."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bar = Image.open(os.path.join(refs, "lower-third.png")).convert("RGBA").resize((W, 1280), Image.LANCZOS)
    bar.putalpha(bar.getchannel("A").point(lambda v: int(v * bar_opacity)))
    img.alpha_composite(bar.crop((0, 0, W, H - 311)), (0, 311))
    d = ImageDraw.Draw(img)
    f1 = _font(fonts, "600SemiBold", 34); f2 = _font(fonts, "500Medium", 19)
    cx, cy = 156, 944
    d.text((cx, cy), reference.upper(), font=f1, fill=GOLD, anchor="ms")
    d.text((cx, cy + 27), "KING JAMES VERSION", font=f2, fill=WHITE, anchor="ms")
    if logo:
        lg = Image.open(os.path.join(refs, "logo-can-you-behold-him.png")).convert("RGBA")
        lg = lg.crop(lg.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox())
        w = 265; lg = lg.resize((w, round(lg.height * w / lg.width)), Image.LANCZOS)
        a = lg.getchannel("A").point(lambda v: int(v * logo_opacity)); lg.putalpha(a)
        img.alpha_composite(lg, (W - w - 30, 26))
    return img

def logo_layer(refs, logo_opacity=0.40):
    """Logo only (used for the calm ending after the subtitles have faded away)."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lg = Image.open(os.path.join(refs, "logo-can-you-behold-him.png")).convert("RGBA")
    lg = lg.crop(lg.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox())
    w = 265; lg = lg.resize((w, round(lg.height * w / lg.width)), Image.LANCZOS)
    lg.putalpha(lg.getchannel("A").point(lambda v: int(v * logo_opacity)))
    img.alpha_composite(lg, (W - w - 30, 26))
    return img

def wrap(text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if font.getlength(t) <= width or not cur: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def fits(text, fonts):
    return len(wrap(text, _font(fonts, "500Medium", VERSE_SIZE), TEXT_R - TEXT_X)) <= MAX_LINES

def verse_layer(text, fonts):
    """Transparent layer with the verse text, vertically centred between the bar lines."""
    f = _font(fonts, "500Medium", VERSE_SIZE)
    lines = wrap(text, f, TEXT_R - TEXT_X)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    total = LINE_H * len(lines); y0 = (INNER_TOP + INNER_BOT) / 2 - total / 2 + LINE_H * 0.78
    ds, d = ImageDraw.Draw(sh), ImageDraw.Draw(img)
    for i, ln in enumerate(lines):
        ds.text((TEXT_X + 2, y0 + i * LINE_H + 2), ln, font=f, fill=(0, 0, 0, 200), anchor="ls")
        d.text((TEXT_X, y0 + i * LINE_H), ln, font=f, fill=WHITE, anchor="ls")
    sh = sh.filter(ImageFilter.GaussianBlur(2))
    sh.alpha_composite(img)
    return sh, len(lines)

def split_verse(prefix, text, fonts):
    """Split a long verse into parts that each fit 3 lines: '[V2] start…', '[V2] …end'."""
    words = text.split()
    for parts in range(2, 6):
        n = len(words); cuts = [round(n * k / parts) for k in range(1, parts)]
        # move each cut to the nearest word ending with punctuation (within 5 words)
        adj = []
        for c in cuts:
            best = c
            for dlt in range(0, 6):
                for cc in (c - dlt, c + dlt):
                    if 0 < cc < n and words[cc - 1][-1] in ",;:.?!":
                        best = cc; break
                else: continue
                break
            adj.append(best)
        bounds = [0] + adj + [n]
        chunks = [" ".join(words[a:b]) for a, b in zip(bounds, bounds[1:])]
        out = []
        for i, c in enumerate(chunks):
            t = f"{prefix} " + ("…" if i else "") + c + ("…" if i < len(chunks) - 1 else "")
            out.append(t)
        if all(fits(t, fonts) for t in out):
            return out, [len(" ".join(words[:b])) / max(len(text), 1) for b in bounds[1:-1]]
    return [f"{prefix} {text}"], []
