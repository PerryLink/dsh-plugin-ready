#!/usr/bin/env python3
"""README visuals for dsh-plugin-ready — v5 (1440x576 hero + 1100x660 flow).

Two assets, both derived from what `src/ready.js` actually does:

  docs/assets/dsh-plugin-ready-hero-{zh,en}-{light,dark}.webp   (Pillow)
      Left: kicker / title / two value lines / sub / meta / footer.
      Right, the tool's own semantic picture: a `package.json` manifest card
      is read row by row (R1-R18), the results fall into three severity
      rails (16 pass / 1 warn / 0 fail), the run ends in a `static:` verdict
      bar with an `exit` terminal, and the four `notClaimed` disclaimers are
      struck through underneath. All right-hand labels are report tokens, so
      only the four prose strings are localised.

  docs/assets/dsh-plugin-ready-flow-v5-{light,dark}.svg          (hand SVG)
      A state machine, not a row of boxes: S0 entry -> S1 R1 gate ->
      S2 body (R2-R18, grouped in four surfaces) -> three verdict states,
      each with a double-outline EXIT terminal. R1 failing is an early
      return (dashed edge + callout: report holds one check, package null);
      `--out` is the only write and is drawn as a self-loop on S2;
      `--host` is the optional S3 sub-machine on its own lane.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow (pip install pillow)
"""
from __future__ import annotations

import os
from html import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'docs', 'assets')

FONT_CJK = r'C:\Windows\Fonts\msyh.ttc'
FONT_CJK_BOLD = r'C:\Windows\Fonts\msyhbd.ttc'
FONT_MONO = r'C:\Windows\Fonts\consola.ttf'
FONT_EN = r'C:\Windows\Fonts\segoeui.ttf'
FONT_EN_BOLD = r'C:\Windows\Fonts\segoeuib.ttf'
for _p in (FONT_CJK, FONT_CJK_BOLD, FONT_MONO, FONT_EN, FONT_EN_BOLD):
    if not os.path.exists(_p):
        raise SystemExit(f'FATAL: font missing: {_p}  (CJK must never render '
                         f'as tofu boxes; install the font and re-run)')

# --- palette: family accent + the two mandated page backgrounds -------------
SKIN = {
    'light': dict(bg_from='#f9f6fd', bg_to='#e4eaf8', card='#ffffff',
                  card_edge='#e4e1ee', zone='#f7f5fc', text='#141419',
                  sub='#4d5261', faint='#8f94a4', accent='#4B67B4',
                  accent2='#16a34a', ok='#16a34a', warn='#bc4c00',
                  fail='#cf222e',
                  pill='#ece7f9', grid='#e7e4f0', shadow=(32, 26, 64)),
    'dark': dict(bg_from='#131a2a', bg_to='#0c1016', card='#1b2231',
                 card_edge='#2e374b', zone='#202839', text='#f0f3f9',
                 sub='#a8b1c4', faint='#737b8d', accent='#8496f5',
                 accent2='#3fb950', ok='#3fb950', warn='#d29922',
                 fail='#f85149',
                 pill='#242d42', grid='#2a3348', shadow=(0, 0, 0)),
}

KIND = {'cjk': FONT_CJK, 'cjk_bold': FONT_CJK_BOLD, 'mono': FONT_MONO,
        'en': FONT_EN, 'en_bold': FONT_EN_BOLD}


def font(size: int, kind: str = 'cjk_bold') -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(KIND[kind], size)


def hx(s: str) -> tuple[int, int, int]:
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def gradient(w: int, h: int, c1: str, c2: str) -> Image.Image:
    img = Image.new('RGB', (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = 0.2 * (y / h) + 0.8 * (y / h) ** 1.5
        d.line([(0, y), (w, y)],
               fill=tuple(int(p + (q - p) * t) for p, q in zip(hx(c1), hx(c2))))
    return img


def glow(img: Image.Image, cx: int, cy: int, r: int, color, alpha: int = 40):
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(9, 0, -1):
        rr = r * i / 9
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                  fill=color + (int(alpha * (1 - i / 10)),))
    return Image.alpha_composite(img.convert('RGBA'),
                                 layer).convert('RGB')


def card(img, box, skin, radius=20, shadow=18, fill=None, edge=None,
         width=2):
    """Rounded card with a soft, offset shadow."""
    x0, y0, x1, y1 = box
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for i in range(shadow, 0, -2):
        sd.rounded_rectangle([x0 - i // 5, y0 + i // 2, x1 + i // 5, y1 + i],
                             radius=radius + i // 4,
                             fill=skin['shadow'] + (int(7 * (1 - i / shadow)),))
    base = Image.alpha_composite(img.convert('RGBA'),
                                 sh.filter(ImageFilter.GaussianBlur(9)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, fill=hx(fill or skin['card']),
                        outline=hx(edge or skin['card_edge']), width=width)
    return base.convert('RGB')


def pill(img, xy, text, skin, size=17, fg=None, bg=None, kind='cjk_bold'):
    d = ImageDraw.Draw(img)
    f = font(size, kind)
    tw = d.textlength(text, font=f)
    x, y = xy
    h = size + 16
    d.rounded_rectangle([x, y, x + tw + 28, y + h], radius=h // 2,
                        fill=hx(bg or skin['pill']))
    d.text((x + 14, y + 6), text, font=f, fill=hx(fg or skin['accent']))


def wrap(d, text, f, maxw):
    if ' ' in text:
        words, lines, cur = text.split(' '), [], ''
        for wd in words:
            cand = f'{cur} {wd}' if cur else wd
            if d.textlength(cand, font=f) <= maxw or not cur:
                cur = cand
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines
    lines, cur = [], ''
    for ch in text:
        if d.textlength(cur + ch, font=f) <= maxw or not cur:
            cur += ch
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


# --- hero copy --------------------------------------------------------------
HERO = {
    'zh': dict(kicker='DeepSeek Harness · 静态预检',
               title='dsh-plugin-ready',
               value=['装插件之前先验包', '18 项检查一次出结论'],
               sub=['读 package.json、patch 与 README/LICENSE，',
                    '逐条判 pass / warn / fail；不安装、不启动宿主。'],
               meta='零依赖 · 只读 · Node ≥24.9.0 · exit 0 / 2 / 3',
               foot='Apache-2.0 · 社区命令行工具，与 DeepSeek 官方无关',
               rails=[('16', 'pass', '18 项里 16 项通过'),
                      ('1', 'warn', '--strict 下升级为失败'),
                      ('0', 'fail', '有一条即整体 fail')],
               sample='样例夹具 16 / 1 / 0',
               verdict='static: pass-with-warnings',
               exit='exit 0',
               claimed='notClaimed',
               claims=['not a host install', 'not a security audit',
                       'not a performance measurement',
                       'not a certification']),
    'en': dict(kicker='DeepSeek Harness · static preflight',
               title='dsh-plugin-ready',
               value=['Preflight the package', 'before anyone installs it'],
               sub=['Reads package.json, the patch file and README/LICENSE,',
                    'scores each check pass / warn / fail. Installs nothing.'],
               meta='zero dependencies · read-only · Node >=24.9.0 · exit 0 / 2 / 3',
               foot='Apache-2.0 · community CLI, not affiliated with DeepSeek',
               rails=[('16', 'pass', 'of 18 checks'),
                      ('1', 'warn', 'fails under --strict'),
                      ('0', 'fail', 'one fail sinks it')],
               sample='fixture 16 / 1 / 0',
               verdict='static: pass-with-warnings',
               exit='exit 0',
               claimed='notClaimed',
               claims=['not a host install', 'not a security audit',
                       'not a performance measurement',
                       'not a certification']),
}

# The manifest card mirrors the keys the checker really reads, in R order.
MANIFEST_ROWS = [
    ('name', 'pass'),
    ('version', 'pass'),
    ('exports["."]', 'pass'),
    ('dsh.bundle', 'pass'),
    ('bundle.patch', 'pass'),
    ('dsh.client', 'warn'),
    ('engines.dsh', 'pass'),
]


def hero(lang: str, skin: str) -> None:
    s = SKIN[skin]
    W, H = 1440, 576
    img = gradient(W, H, s['bg_from'], s['bg_to'])
    img = glow(img, 1180, 80, 360, hx(s['accent']),
               26 if skin == 'light' else 40)
    img = glow(img, 160, 560, 260, hx(s['accent2']),
               10 if skin == 'light' else 16)
    H_ = HERO[lang]
    m = 60

    pill(img, (m, 54), H_['kicker'], s, size=17)
    d = ImageDraw.Draw(img)

    # title: mono wordmark, kept wide enough to stay >= 48px at 880px display
    tsize = 80
    while tsize > 60 and d.textlength(H_['title'],
                                      font=font(tsize, 'mono')) > 708:
        tsize -= 2
    d.text((m - 2, 106), H_['title'], font=font(tsize, 'mono'),
           fill=hx(s['text']))

    vkind = 'en_bold' if lang == 'en' else 'cjk_bold'
    vy = 240
    for line in H_['value']:
        d.text((m, vy), line, font=font(38, vkind), fill=hx(s['text']))
        vy += 54

    skind = 'en' if lang == 'en' else 'cjk'
    fsub = font(25, skind)
    lines = []
    for para in H_['sub']:
        lines += wrap(d, para, fsub, 700)
    for i, ln in enumerate(lines):
        d.text((m + 1, 360 + i * 34), ln, font=fsub, fill=hx(s['sub']))

    meta_y = 360 + len(lines) * 34 + 16
    d.text((m + 1, meta_y), H_['meta'],
           font=font(20, 'mono' if lang == 'en' else 'cjk'),
           fill=hx(s['faint']))
    d.line([m + 1, meta_y + 40, m + 566, meta_y + 40],
           fill=hx(s['grid']), width=2)
    d.text((m + 1, meta_y + 54), H_['foot'], font=font(17, skind),
           fill=hx(s['faint']))

    # ---------------- right: manifest -> rails -> verdict -> notClaimed ----
    # package.json card
    img = card(img, (800, 84, 1136, 356), s)
    d = ImageDraw.Draw(img)
    d.text((824, 103), 'package.json', font=font(17, 'mono'),
           fill=hx(s['text']))
    d.text((1112, 106), '18 checks', font=font(11.5, 'mono'), anchor='ra',
           fill=hx(s['faint']))
    d.line([824, 132, 1112, 132], fill=hx(s['grid']), width=2)
    # highlight the one warning row first, then write every row once on top
    warn_i = next(i for i, (_, st) in enumerate(MANIFEST_ROWS) if st == 'warn')
    warn_y = 160 + warn_i * 28
    hl = Image.new('RGBA', img.size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(hl)
    hd.rounded_rectangle([812, warn_y - 18, 1124, warn_y + 8], radius=8,
                         fill=hx(s['warn']) + (26,))
    img = Image.alpha_composite(img.convert('RGBA'), hl).convert('RGB')
    d = ImageDraw.Draw(img)
    for i, (key, state) in enumerate(MANIFEST_ROWS):
        yy = 160 + i * 28
        d.text((824, yy - 11), key, font=font(16, 'mono'),
               fill=hx(s['text'] if state == 'pass' else s['warn']))
        d.text((1112, yy - 9), state, font=font(12, 'mono'), anchor='ra',
               fill=hx(s['ok'] if state == 'pass' else s['warn']))

    # severity rails
    rail_colors = ['ok', 'warn', 'fail']
    note_kind = 'mono' if lang == 'en' else 'cjk'
    for i, (count, label, note) in enumerate(H_['rails']):
        top = 84 + i * 88
        col = hx(s[rail_colors[i]])
        img = card(img, (1156, top, 1390, top + 78), s, radius=18,
                   fill=s['card'])
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([1156, top + 14, 1162, top + 64], radius=3,
                            fill=col)
        d.text((1178, top + 10), count, font=font(34, 'mono'), fill=col)
        d.text((1242, top + 25), label, font=font(14, 'mono'),
               fill=hx(s['sub']))
        d.text((1178, top + 55), note, font=font(13, note_kind),
               fill=hx(s['faint']))

    d = ImageDraw.Draw(img)
    d.text((1158, 358), H_['sample'],
           font=font(13, 'mono' if lang == 'en' else 'cjk'),
           fill=hx(s['faint']))

    # verdict bar + exit terminal
    bar_fill = '#eef1fb' if skin == 'light' else '#1d2438'
    img = card(img, (800, 372, 1390, 428), s, radius=18, fill=bar_fill,
               edge=s['accent'], width=2)
    d = ImageDraw.Draw(img)
    d.text((824, 387), H_['verdict'], font=font(18, 'mono'),
           fill=hx(s['accent']))
    d.rounded_rectangle([1300, 384, 1372, 416], radius=10,
                        outline=hx(s['ok']), width=2)
    d.rounded_rectangle([1304, 388, 1368, 412], radius=8,
                        outline=hx(s['ok']), width=1)
    d.text((1336, 400), H_['exit'], font=font(13.5, 'mono'), anchor='mm',
           fill=hx(s['ok']))

    # notClaimed strip: the four disclaimers, struck through
    img = card(img, (800, 444, 1390, 532), s, radius=18, fill=s['zone'],
               edge=s['grid'], width=1)
    d = ImageDraw.Draw(img)
    d.text((824, 457), H_['claimed'], font=font(13, 'mono'),
           fill=hx(s['accent']))
    fm = font(14, 'mono')
    for i, item in enumerate(H_['claims']):
        cx = 824 + (i % 2) * 292
        cy = 488 + (i // 2) * 22
        d.text((cx, cy), item, font=fm, fill=hx(s['sub']))
        tw = d.textlength(item, font=fm)
        d.line([cx - 1, cy + 7, cx + tw + 1, cy + 7],
               fill=hx(s['faint']), width=1)

    img.save(os.path.join(OUT, f'dsh-plugin-ready-hero-{lang}-{skin}.webp'),
             'WEBP', quality=92, method=6)
    print(f'dsh-plugin-ready-hero-{lang}-{skin}.webp')


# --- flow (hand-written SVG): the verdict / exit state machine --------------
FLOW = {
    'light': dict(bg='#ffffff', dots='#f0edf7', card='#ffffff',
                  zone='#f7f5fc', edge='#e6e3f0', grid='#efedf6',
                  text='#141419', sub='#4d5261', faint='#8f94a4',
                  accent='#4B67B4', ok='#16a34a', warn='#bc4c00',
                  fail='#cf222e', pill='#ece7f9', solid='0.10'),
    'dark': dict(bg='#0d1117', dots='#1b2231', card='#161b26',
                 zone='#1c2333', edge='#2a3142', grid='#222a3b',
                 text='#f0f3f9', sub='#a8b1c4', faint='#737b8d',
                 accent='#8496f5', ok='#3fb950', warn='#d29922',
                 fail='#f85149', pill='#242d42', solid='0.55'),
}
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
SANS = "ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif"

# 17 body checks (R1 is the S1 gate), grouped by the surface they read.
BANDS = [
    ('META', 4, [('R2', 'name', 'fail'), ('R3', 'version', 'fail'),
                 ('R4', 'description', 'warn'), ('R5', 'license', 'warn')]),
    ('ENTRY', 4, [('R6', 'exports["."]', 'fail'), ('R7', 'dsh.bundle', 'fail'),
                  ('R8', 'bundle.patch', 'fail'), ('R9', 'client pair', 'fail')]),
    ('COMPAT', 4, [('R10', 'engines.dsh', 'warn'),
                   ('R11', 'engines.node', 'warn'),
                   ('R12', 'manifest=1', 'warn'), ('R18', 'engines/peer', 'warn')]),
    ('HYGIENE', 5, [('R13', 'repository', 'warn'), ('R14', 'README.md', 'warn'),
                    ('R15', 'LICENSE', 'warn'), ('R16', 'grade/score', 'fail'),
                    ('R17', 'standards', 'warn')]),
]

VERDICTS = [
    # x, title, sub, note, exit text, colour key
    (44, 'static: fail', 'fail &#8805; 1 &#8594; overall fail',
     'R1 short-circuit lands here', 'exit 2', 'fail'),
    (376, 'static: pass-with-warnings', 'fail = 0, warn &#8805; 1',
     '--strict upgrades to exit 2', 'exit 0', 'ok'),
    (708, 'static: pass', 'fail = 0, warn = 0', '18 checks clean',
     'exit 0', 'ok'),
]

HOSTS = [('not-run', 'default, exit unchanged', 'faint'),
         ('pass', 'exit 0', 'ok'),
         ('blocked', 'exit 3', 'warn'),
         ('fail', 'exit 2', 'fail')]


def t(x, y, txt, size, fill, fam=MONO, weight=None, anchor=None,
      opacity=None, spacing=None):
    a = [f'<text x="{x}" y="{y}" fill="{fill}" font-family="{fam}"',
         f'font-size="{size}"']
    if weight:
        a.append(f'font-weight="{weight}"')
    if anchor:
        a.append(f'text-anchor="{anchor}"')
    if opacity:
        a.append(f'opacity="{opacity}"')
    if spacing:
        a.append(f'letter-spacing="{spacing}"')
    a.append(f'>{txt}</text>')
    return ' '.join(a)


def flow_svg(skin: str) -> str:
    s = FLOW[skin]
    W, H = 1100, 660
    p: list[str] = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="dsh-plugin-ready state machine: S0 entry, S1 R1 gate, S2 seventeen checks, three verdict states with exit terminals, and the optional --host sub-machine">
<title>dsh-plugin-ready state machine</title>
<defs>
  <filter id="soft" x="-40%" y="-40%" width="180%" height="200%">
    <feDropShadow dx="0" dy="9" stdDeviation="12" flood-color="#1b1735" flood-opacity="{s['solid']}"/>
  </filter>
  <pattern id="dots" width="28" height="28" patternUnits="userSpaceOnUse">
    <circle cx="1.3" cy="1.3" r="1.3" fill="{s['dots']}"/>
  </pattern>
  <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0 0 L10 5 L0 10 z" fill="{s['accent']}"/>
  </marker>
  <marker id="arrFail" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0 0 L10 5 L0 10 z" fill="{s['fail']}"/>
  </marker>
  <marker id="arrFaint" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0 0 L10 5 L0 10 z" fill="{s['faint']}"/>
  </marker>
</defs>
<rect width="{W}" height="{H}" fill="{s['bg']}"/>
<rect width="{W}" height="{H}" fill="url(#dots)" opacity=".55"/>
''']

    p.append(t(44, 50, 'dsh-plugin-ready', 30, s['text'], weight='700'))
    p.append(t(44, 78, '18 static checks on one plugin dir &#183; three-valued '
                       'verdict &#183; exit 0 | 2 | 3 &#183; read-only, '
                       'zero dependency', 15, s['sub'], fam=SANS))

    # ---- S0 entry ---------------------------------------------------------
    p.append(f'<rect x="44" y="108" width="286" height="76" rx="16" '
             f'fill="{s["card"]}" stroke="{s["edge"]}" filter="url(#soft)"/>')
    p.append(t(64, 130, 'S0 &#183; entry', 12.5, s['accent'], weight='700'))
    p.append(t(64, 156, 'dsh-ready &lt;dir&gt;', 17, s['text'], weight='700'))
    p.append(t(64, 174, 'read-only &#183; no install', 11, s['sub']))

    # ---- transition S0 -> S1 ---------------------------------------------
    p.append(f'<path d="M187 184V196" stroke="{s["accent"]}" stroke-width="2" '
             f'marker-end="url(#arr)"/>')
    p.append(t(196, 198, 'read', 11, s['faint']))

    # ---- S1 R1 gate ------------------------------------------------------
    p.append(f'<rect x="44" y="202" width="286" height="96" rx="16" '
             f'fill="{s["card"]}" stroke="{s["accent"]}" stroke-width="1.6" '
             f'filter="url(#soft)"/>')
    p.append(t(64, 222, 'S1 &#183; R1 gate', 12.5, s['accent'], weight='700'))
    p.append(t(64, 250, 'package.json', 17, s['text'], weight='700'))
    p.append(t(64, 271, 'parses as JSON?', 11, s['sub']))
    p.append(t(64, 289, 'first of 18 checks', 11, s['faint']))

    # ---- early return: R1 fail short-circuits R2-R18 ---------------------
    p.append(f'<path d="M84 298V420" stroke="{s["fail"]}" stroke-width="1.8" '
             f'stroke-dasharray="5 4" marker-end="url(#arrFail)"/>')
    p.append(f'<rect x="108" y="320" width="236" height="76" rx="12" '
             f'fill="{s["zone"]}" stroke="{s["edge"]}" stroke-dasharray="4 4"/>')
    p.append(t(122, 344, 'R1 fail &#8594; early return', 11.5, s['fail'],
               weight='700'))
    p.append(t(122, 364, 'report holds 1 check,', 11, s['sub']))
    p.append(t(122, 382, 'package: null &#183; R2-R18 skipped', 11, s['sub']))

    # ---- transition S1 -> S2 --------------------------------------------
    p.append(f'<path d="M330 250H352" stroke="{s["accent"]}" stroke-width="2" '
             f'marker-end="url(#arr)"/>')
    p.append(t(334, 242, 'ok', 11, s['faint']))

    # ---- S2 body: 17 checks in four surfaces ----------------------------
    p.append(f'<rect x="360" y="108" width="664" height="292" rx="18" '
             f'fill="{s["card"]}" stroke="{s["edge"]}" filter="url(#soft)"/>')
    p.append(t(382, 132, 'S2 &#183; R2-R18 &#183; 17 checks', 13.5, s['accent'],
               weight='700'))
    p.append(f'<circle cx="628" cy="128" r="4" fill="{s["fail"]}"/>')
    p.append(t(640, 132, 'fail &#8594; overall fail', 11, s['sub']))
    p.append(f'<circle cx="792" cy="128" r="4" fill="{s["warn"]}"/>')
    p.append(t(804, 132, 'warn &#8594; ok unless --strict', 11, s['sub']))
    p.append(f'<line x1="382" y1="144" x2="1002" y2="144" '
             f'stroke="{s["grid"]}" stroke-width="2"/>')

    col_x = [382, 544, 706, 868]
    for bi, (name, count, items) in enumerate(BANDS):
        x = col_x[bi]
        p.append(t(x, 168, f'{name} &#183; {count}', 11.5, s['faint'],
                   weight='700', spacing='0.6'))
        for ri, (rid, label, level) in enumerate(items):
            y = 180 + ri * 42
            p.append(f'<rect x="{x}" y="{y}" width="146" height="34" rx="10" '
                     f'fill="{s["zone"]}" stroke="{s["edge"]}"/>')
            p.append(f'<circle cx="{x + 13}" cy="{y + 17}" r="3.6" '
                     f'fill="{s[level]}"/>')
            p.append(t(x + 25, y + 21, rid, 11.5, s['text'], weight='700'))
            p.append(t(x + 52, y + 21, escape(label), 11, s['sub']))

    # ---- S2 self-loop: --out is the only write --------------------------
    p.append(t(382, 372, 'R17 is emitted only when dsh.standards.entry.status '
                         'is self-reported', 11, s['faint']))
    p.append(f'<path d="M960 108C960 86 1004 86 1004 108" '
             f'stroke="{s["accent"]}" stroke-width="1.6" fill="none" '
             f'marker-end="url(#arr)"/>')
    p.append(t(950, 100, '--out only', 11, s['accent'], anchor='end'))

    # ---- S2 -> verdict states -------------------------------------------
    p.append(f'<path d="M380 400C380 414 320 410 320 422" '
             f'stroke="{s["accent"]}" stroke-width="1.8" fill="none" '
             f'marker-end="url(#arr)"/>')
    p.append(f'<path d="M549 400V422" stroke="{s["accent"]}" stroke-width="1.8" '
             f'marker-end="url(#arr)"/>')
    p.append(f'<path d="M891 400V422" stroke="{s["accent"]}" stroke-width="1.8" '
             f'marker-end="url(#arr)"/>')
    p.append(t(1024, 420, 'V &#183; verdict states', 11, s['accent'],
               anchor='end'))

    # ---- verdict states + EXIT terminals --------------------------------
    for x, title, sub, note, exit_txt, ckey in VERDICTS:
        p.append(f'<rect x="{x}" y="428" width="316" height="90" rx="16" '
                 f'fill="{s["card"]}" stroke="{s[ckey]}" stroke-width="1.6" '
                 f'filter="url(#soft)"/>')
        p.append(t(x + 20, 454, escape(title), 14, s[ckey], weight='700'))
        p.append(t(x + 20, 476, sub, 11, s['sub']))
        p.append(t(x + 20, 494, note, 11, s['faint']))
        cx = x + 202
        p.append(f'<rect x="{cx}" y="474" width="96" height="32" rx="10" '
                 f'fill="{s["bg"]}" stroke="{s[ckey]}" stroke-width="1.6"/>')
        p.append(f'<rect x="{cx + 3}" y="477" width="90" height="26" rx="8" '
                 f'fill="none" stroke="{s[ckey]}" stroke-width="1"/>')
        p.append(t(cx + 48, 494, exit_txt, 12.5, s[ckey], weight='700',
                   anchor='middle'))

    # ---- S3 --host sub-machine ------------------------------------------
    p.append(f'<rect x="44" y="540" width="980" height="80" rx="16" '
             f'fill="{s["card"]}" stroke="{s["accent"]}" stroke-width="1.6" '
             f'stroke-dasharray="7 5"/>')
    p.append(t(64, 568, 'S3 &#183; --host', 13, s['accent'], weight='700'))
    p.append(t(64, 588, 'optional &#183; default not-run', 11, s['sub']))
    for i, (name, note, ckey) in enumerate(HOSTS):
        x = 320 + i * 172
        p.append(f'<rect x="{x}" y="552" width="160" height="40" rx="10" '
                 f'fill="{s["zone"]}" stroke="{s["edge"]}"/>')
        p.append(t(x + 14, 572, name, 12.5, s['text'], weight='700'))
        p.append(t(x + 14, 588, note, 11, s[ckey]))
    p.append(t(64, 610, 'dsh-clinic --only X &#183; X is a contract check, '
                        'not C3 &#183; blocked &#8800; pass', 11, s['faint']))

    # ---- transition S2 -> S3 (right-hand channel) -----------------------
    p.append(f'<path d="M1024 300H1064V580H1032" stroke="{s["faint"]}" '
             f'stroke-width="1.6" fill="none" stroke-dasharray="6 4" '
             f'marker-end="url(#arrFaint)"/>')
    p.append(f'<text x="0" y="0" transform="translate(1080 430) rotate(90)" '
             f'fill="{s["faint"]}" font-family="{MONO}" font-size="11">'
             f'--host</text>')

    # ---- footer ----------------------------------------------------------
    p.append(t(44, 644, 'only write: --out &lt;file&gt; &#183; schema '
                        'dsh-plugin-ready/1', 11, s['faint']))
    p.append(t(1024, 644, 'verdict covers the static surface only &#183; '
                          '--host X is a contract check', 11, s['faint'],
               anchor='end'))
    p.append('</svg>')

    path = os.path.join(OUT, f'dsh-plugin-ready-flow-v5-{skin}.svg')
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(p) + '\n')
    print(f'dsh-plugin-ready-flow-v5-{skin}.svg')


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for skin in ('light', 'dark'):
        for lang in ('zh', 'en'):
            hero(lang, skin)
    for skin in ('light', 'dark'):
        flow_svg(skin)


if __name__ == '__main__':
    main()
