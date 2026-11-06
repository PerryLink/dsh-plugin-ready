#!/usr/bin/env python3
"""Generate README image assets for dsh-plugin-ready (docs/assets/).

Outputs (idempotent overwrite):
  dsh-plugin-ready-flow-light.svg / dsh-plugin-ready-flow-dark.svg
      Hero pipeline diagram. Two hand-written SVG files (vector — never
      rasterized to webp). Every label is a command token (`dsh-ready <dir>`,
      `R1-R18`, `--json`, `dsh-clinic --only X`, ...), so all five README
      languages share the same pair.
  No raster assets: this repo ships no benchmark data and no UI, so there is
  no evidence chart and nothing to screenshot.

The Pillow + CJK-font probe mirrors the PerryLink family pipeline
(dsh-mask/scripts/gen-readme-assets.py): Chinese must never be rendered as
tofu boxes, and the checkout aborts loudly when no CJK font is installed.
The SVG labels themselves stay ASCII tokens so the hero is language-neutral.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow (pip install pillow)
"""
from __future__ import annotations

import os
import sys

from PIL import ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

# --- palette: PerryLink family (accent) + GitHub page backgrounds ----------
FAMILY = "#4B67B4"   # family accent (badges labelColor family uses #2B3245)
GREEN = {"light": "#16a34a", "dark": "#3fb950"}
ORANGE = {"light": "#bc4c00", "dark": "#d29922"}
SKIN = {
    "light": dict(bg="#ffffff", box="#f6f8fa", border="#d0d7de",
                  text="#1f2328", sub="#57606a", track="#eaeef2"),
    "dark": dict(bg="#0d1117", box="#161b22", border="#30363d",
                 text="#f0f6fc", sub="#8b949e", track="#21262d"),
}

# --- CJK font probe: Chinese must never render as tofu boxes ----------------
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",      # Microsoft YaHei
    r"C:\Windows\Fonts\simhei.ttf",    # SimHei
    r"C:\Windows\Fonts\Deng.ttf",      # DengXian
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
]
FONT_PATH = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)
if FONT_PATH is None:
    sys.exit("FATAL: no CJK font found (looked for msyh.ttc, simhei.ttf, "
             "Deng.ttf, Noto Sans CJK, PingFang). Refusing to render Chinese "
             "as tofu boxes; install one of the probed fonts and re-run.")


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size)


# Fail early if the probed font cannot actually be loaded at a body size.
font(16)

MONO = ("ui-monospace,SFMono-Regular,Menlo,Consolas,"
        "'Liberation Mono',monospace")
SANS = "ui-sans-serif,system-ui,-apple-system,'Segoe UI',sans-serif"

# Pipeline tokens only: no prose, no per-language copy.
MAIN_NODES = [
    ("dsh-ready &lt;dir&gt;", "npm i -g &#183; npx"),
    ("package.json", "name &#183; version &#183; entry"),
    ("R1-R18", "static checks"),
    ("static: pass", "warn &#183; fail &#183; --strict"),
    ("exit 0 | 2", "report JSON"),
]


def _arrow(x1: int, y: int, x2: int, color: str) -> list[str]:
    return [
        f'<path d="M{x1} {y}H{x2 - 10}" stroke="{color}" stroke-width="2.5"/>',
        f'<path d="M{x2 - 14} {y - 6}l8 6-8 6" fill="none" stroke="{color}" '
        f'stroke-width="2.5" stroke-linecap="round" '
        f'stroke-linejoin="round"/>',
    ]


def flow_svg(skin: str) -> str:
    s = SKIN[skin]
    w, h = 1200, 450
    nw, nh, gap = 192, 104, 40
    y0 = 150
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" '
        f'aria-label="dsh-plugin-ready static preflight pipeline">',
        '<title>dsh-plugin-ready static preflight pipeline</title>',
        f'<rect width="{w}" height="{h}" rx="18" fill="{s["bg"]}"/>',
        f'<text x="56" y="62" fill="{s["text"]}" font-family="{SANS}" '
        f'font-size="30" font-weight="700">dsh-plugin-ready</text>',
        f'<text x="56" y="94" fill="{s["sub"]}" font-family="{MONO}" '
        f'font-size="15">static preflight &#183; dsh-ready &lt;dir&gt; '
        f'&#8594; package.json &#8594; R1-R18 &#8594; report</text>',
        f'<line x1="56" y1="116" x2="1144" y2="116" stroke="{s["border"]}"/>',
    ]

    for i, (label, sub) in enumerate(MAIN_NODES):
        x = 50 + i * (nw + gap)
        if i == 0:
            accent = FAMILY
        elif i == len(MAIN_NODES) - 1:
            accent = GREEN[skin]
        else:
            accent = s["border"]
        parts.append(
            f'<rect x="{x}" y="{y0}" width="{nw}" height="{nh}" rx="14" '
            f'fill="{s["box"]}" stroke="{accent}" stroke-width="2"/>')
        parts.append(
            f'<text x="{x + nw // 2}" y="{y0 + 44}" fill="{s["text"]}" '
            f'text-anchor="middle" font-family="{MONO}" font-size="16" '
            f'font-weight="700">{label}</text>')
        parts.append(
            f'<text x="{x + nw // 2}" y="{y0 + 74}" fill="{s["sub"]}" '
            f'text-anchor="middle" font-family="{MONO}" font-size="11.5">'
            f'{sub}</text>')
        if i < len(MAIN_NODES) - 1:
            parts.extend(_arrow(x + nw + 5, y0 + nh // 2,
                                x + nw + gap - 2, s["sub"]))

    # Optional --host branch: dashed container under the pipeline.
    bx, by, bw, bh = 50, 292, 1120, 100
    parts.append(
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="14" '
        f'fill="{s["box"]}" stroke="{FAMILY}" stroke-width="2" '
        f'stroke-dasharray="6 5"/>')
    parts.append(
        f'<path d="M610 {y0 + nh}v{by - y0 - nh}" stroke="{FAMILY}" '
        f'stroke-width="2" stroke-dasharray="5 5"/>')
    parts.append(
        f'<text x="74" y="{by + 34}" fill="{FAMILY}" font-family="{MONO}" '
        f'font-size="16" font-weight="700">--host</text>')
    parts.append(
        f'<text x="74" y="{by + 58}" fill="{s["sub"]}" font-family="{MONO}" '
        f'font-size="11.5">optional</text>')
    parts.append(
        f'<text x="180" y="{by + 38}" fill="{s["text"]}" '
        f'font-family="{MONO}" font-size="13">dsh-clinic --repo '
        f'&lt;dir&gt; --only X</text>')
    parts.extend(_arrow(470, by + 33, 500, s["sub"]))
    parts.append(
        f'<text x="515" y="{by + 38}" fill="{s["text"]}" '
        f'font-family="{MONO}" font-size="13">host: pass | blocked | '
        f'fail</text>')
    parts.append(
        f'<text x="760" y="{by + 38}" fill="{s["sub"]}" '
        f'font-family="{MONO}" font-size="12">blocked &#8594; exit 3 '
        f'&#183; fail &#8594; exit 2</text>')
    parts.append(
        f'<text x="180" y="{by + 72}" fill="{s["sub"]}" '
        f'font-family="{MONO}" font-size="12">default: host not-run '
        f'&#183; X is a contract check, not C3</text>')
    parts.append(
        f'<text x="650" y="{by + 72}" fill="{s["sub"]}" '
        f'font-family="{MONO}" font-size="12">static pass &#8800; install / '
        f'audit / certification</text>')

    parts.append(
        f'<text x="56" y="428" fill="{s["sub"]}" font-family="{MONO}" '
        f'font-size="12">--json &#183; --out &lt;file&gt; &#183; '
        f'--strict &#183; --host &#183; exit 0 | 2 | 3</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for skin_name in ("light", "dark"):
        path = os.path.join(OUT, f"dsh-plugin-ready-flow-{skin_name}.svg")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(flow_svg(skin_name))
    print(f"font: {FONT_PATH}")
    print("wrote 2 SVG assets to docs/assets/")


if __name__ == "__main__":
    main()
