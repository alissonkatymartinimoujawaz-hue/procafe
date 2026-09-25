"""Arabica price since 2005 (World Bank Pink Sheet, ICO other milds, monthly), one slide in the house format
plus a PNG preview. Standard library only (ooxml.py from research/indonesia/slides)."""
import json, os, sys, subprocess, decimal
HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
sys.path.insert(0, HERE + '../../indonesia/slides')
from ooxml import Slide, run, para, line_chart, save

D = json.load(open(HERE + '../data/worldbank_prices.json'))
M = D['monthly']
KS = sorted(k for k in M if k >= '2005M01')
VAL = [M[k]['arabica'] for k in KS]
ANN = D['annual']
MN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
MN_FR = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.']
N = len(KS)
LB = 2.20462
NAVY, LINE, GREY, INK, BAND, BANDTXT = '1F3864', '2E75B6', '7F7F7F', '262626', 'FCE4D6', 'C55A11'


def label(k):
    y, m = int(k[:4]), int(k[5:])
    return str(y) if m == 1 else '%s %d' % (MN[m - 1], y)


def pt(k):
    return KS.index(k), M[k]['arabica']


def fr(v, d=2):
    q = decimal.Decimal(repr(v)).quantize(decimal.Decimal(1).scaleb(-d), rounding=decimal.ROUND_HALF_UP)  # 2.925 -> 2,93
    return str(q).replace('.', ',')


a11, a13, a19, a25 = ANN['2011']['arabica'], ANN['2013']['arabica'], ANN['2019']['arabica'], ANN['2025']['arabica']
POINTS = [('2011M04', 'Apr 2011 peak', 'above'), ('2013M11', 'Nov 2013 low', 'below'), ('2019M05', 'May 2019 low', 'below'),
          ('2025M02', 'Feb 2025 record', 'above'), (KS[-1], label(KS[-1]) + ', latest', 'leader')]
TITLE = 'Arabica price since 2005: halved between 2011 and 2013, the rust years'
BULLETS = [
    'Annual average %s $/kg in 2011 → %s $/kg in 2013 (%s %%). Honduras declared a rust emergency on 24 Jan 2013: the disease hit when farmers had the least cash for fungicide and fertiliser' % (fr(a11), fr(a13), fr(100 * (a13 / a11 - 1), 1).replace('-', '−')),
    '2018: %s $/kg, 2019: %s $/kg, below Honduran production costs, area fell. 2025: record year at %s $/kg on average (peak %s $/kg in Feb 2025)' % (fr(ANN['2018']['arabica']), fr(a19), fr(a25), fr(M['2025M02']['arabica'])),
    'Latest: %s $/kg in %s (%.0f US¢/lb), %s %% on a year earlier' % (fr(VAL[-1]), label(KS[-1]), VAL[-1] / LB * 100, fr(100 * (VAL[-1] / M[KS[-13]]['arabica'] - 1), 1).replace('-', '−'))]
SRC = ('Source: World Bank Commodity Price Data (Pink Sheet), "Coffee, Arabica" = ICO indicator price for other mild arabicas (Honduras\'s group), ex-dock, monthly averages, '
       'January 2005 – %s (update of 2 September 2026). 1 $/kg = 45.4 US¢/lb. Rust epidemic in Central America: 2012–2013 (USDA; Avelino et al., 2015).' % label(KS[-1]))

# ---------------- PPTX ----------------
s = Slide()
s.text(0.45, 0.22, 12.4, 0.55, [para(run(TITLE, 24, True, color=NAVY))])
s.text(0.75, 0.78, 11.9, 0.95, [para(run(b, 10.5, color=INK, hl='FFFF00'), bullet=True, after=1) for b in BULLETS])
CX, CY, CW, CH = 0.45, 1.85, 12.4, 5.0
LX, LY, LW, LH = 0.055, 0.05, 0.93, 0.82          # inner plot area as a share of the chart frame
PX0, PY0, PW, PH = CX + CW * LX, CY + CH * LY, CW * LW, CH * LH
YMAX = 10.0
X = lambda i: PX0 + PW * (i + 0.5) / N
Yp = lambda v: PY0 + PH * (1 - v / YMAX)
i0, i1 = KS.index('2012M01'), KS.index('2013M12')
s.rect(PX0 + PW * i0 / N, PY0, PW * (i1 - i0 + 1) / N, PH, fill=BAND)
s.text(PX0 + PW * i0 / N, PY0 + 0.03, PW * (i1 - i0 + 1) / N, 0.45, [para(run('Rust epidemic', 9, True, color=BANDTXT), algn='ctr'), para(run('2012–13', 9, True, color=BANDTXT), algn='ctr')])
cats = [label(k) for k in KS]
xml = line_chart(cats, [{'name': 'Arabica, ICO other milds ($/kg)', 'values': VAL, 'color': LINE, 'width': 2.0}], mn=0, mx=YMAX, unit=2, fmt='0', skip=12, legend=False)
lay = '<c:layout><c:manualLayout><c:layoutTarget val="inner"/><c:xMode val="edge"/><c:yMode val="edge"/><c:x val="%s"/><c:y val="%s"/><c:w val="%s"/><c:h val="%s"/></c:manualLayout></c:layout>' % (LX, LY, LW, LH)
xml = xml.replace('<c:plotArea><c:layout/>', '<c:plotArea>' + lay, 1)
xml = xml.replace('</c:valAx></c:plotArea>', '</c:valAx><c:spPr><a:noFill/><a:ln><a:noFill/></a:ln></c:spPr></c:plotArea>', 1)
s.chart(CX, CY, CW, CH, xml)
s.text(CX, CY - 0.28, 3, 0.26, [para(run('US$ per kg', 9, color=GREY))])
for k, name, pos in POINTS:
    i, v = pt(k)
    x, y = X(i), Yp(v)
    s.rect(x - 0.055, y - 0.055, 0.11, 0.11, fill=NAVY, line='FFFFFF', geom='ellipse', lw=1)
    w = 1.9
    if pos == 'leader':
        ty = Yp(3.55)                                   # below the 2023-24 trough (min 4.05 $/kg), clear of the line
        s.rect(x - 0.006, y + 0.06, 0.012, ty - y - 0.06, fill=GREY)
    else:
        ty = y - 0.52 if pos == 'above' else y + 0.1
    tx = min(max(x - w / 2, PX0), PX0 + PW - w)
    s.text(tx, ty, w, 0.44, [para(run(name, 9, True, color=INK), algn='ctr'),
                             para(run('%s $/kg · %.0f ¢/lb' % (fr(v), v / LB * 100), 9, color=INK), algn='ctr')])
s.text(0.45, 7.02, 12.4, 0.42, [para(run(SRC, 7.5, color=GREY))])
out = HERE + 'Arabica_price_2005_2026.pptx'
save([s], out, 'Arabica price since 2005')
print('saved', out)

# ---------------- PNG preview (HTML + SVG rendered by Chromium) ----------------
W, H = 1600, 900
k_ = 120  # px per inch, same geometry as the slide


def sx(v):
    return v * k_


esc = lambda t: t.replace('&', '&amp;').replace('<', '&lt;')
parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Arial" style="position:absolute;left:0;top:0">' % (W, H)]
parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#%s"/>' % (sx(PX0 + PW * i0 / N), sx(PY0), sx(PW * (i1 - i0 + 1) / N), sx(PH), BAND))
cxb = sx(PX0 + PW * (i0 + i1 + 1) / 2 / N)
parts.append('<text x="%.1f" y="%.1f" font-size="15" font-weight="700" fill="#%s" text-anchor="middle">Rust epidemic</text><text x="%.1f" y="%.1f" font-size="15" font-weight="700" fill="#%s" text-anchor="middle">2012–13</text>' % (cxb, sx(PY0) + 18, BANDTXT, cxb, sx(PY0) + 36, BANDTXT))
for g in range(0, 11, 2):
    yy = sx(Yp(g))
    parts.append('<line x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" stroke="#E3E8EB"/>' % (sx(PX0), sx(PX0 + PW), yy, yy))
    parts.append('<text x="%.1f" y="%.1f" font-size="13" fill="#5B6770" text-anchor="end">%d</text>' % (sx(PX0) - 8, yy + 4, g))
parts.append('<text x="%.1f" y="%.1f" font-size="15" fill="#%s">US$ per kg</text>' % (sx(CX), sx(CY - 0.1), GREY))
for i, k in enumerate(KS):
    if k.endswith('M01'):
        parts.append('<text x="%.1f" y="%.1f" font-size="13" fill="#5B6770" text-anchor="middle">%s</text>' % (sx(X(i)), sx(PY0 + PH) + 20, k[:4]))
parts.append('<polyline fill="none" stroke="#%s" stroke-width="3" stroke-linejoin="round" points="%s"/>' % (LINE, ' '.join('%.1f,%.1f' % (sx(X(i)), sx(Yp(v))) for i, v in enumerate(VAL))))
for k, name, pos in POINTS:
    i, v = pt(k)
    x, y = sx(X(i)), sx(Yp(v))
    if pos == 'leader':
        ty = sx(Yp(3.55)) + 16
        parts.append('<line x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" stroke="#%s" stroke-width="1.5"/>' % (x, x, y + 8, ty - 16, GREY))
    else:
        ty = y - 40 if pos == 'above' else y + 30
    parts.append('<circle cx="%.1f" cy="%.1f" r="7" fill="#%s" stroke="#fff" stroke-width="2"/>' % (x, y, NAVY))
    x = min(max(x, sx(PX0) + 110), sx(PX0 + PW) - 110)
    parts.append('<text x="%.1f" y="%.1f" font-size="15" font-weight="700" fill="#%s" text-anchor="middle">%s</text>' % (x, ty, INK, esc(name)))
    parts.append('<text x="%.1f" y="%.1f" font-size="15" fill="#%s" text-anchor="middle">%s $/kg · %.0f ¢/lb</text>' % (x, ty + 18, INK, fr(v), v / LB * 100))
parts.append('</svg>')
head = ('<div style="position:absolute;left:%dpx;top:%dpx;width:%dpx;font:700 32px Arial;color:#%s">%s</div>' % (sx(0.45), sx(0.2), sx(12.4), NAVY, esc(TITLE)) +
        '<div style="position:absolute;left:%dpx;top:%dpx;width:%dpx;font:17.5px/1.45 Arial;color:#%s">%s</div>' % (
            sx(0.75), sx(0.8), sx(11.9), INK, ''.join('<div>• <span style="background:#FFFF00">%s</span></div>' % esc(b) for b in BULLETS)) +
        '<div style="position:absolute;left:%dpx;top:%dpx;width:%dpx;font:12.5px/1.35 Arial;color:#%s">%s</div>' % (sx(0.45), sx(7.02), sx(12.4), GREY, esc(SRC)))
html = HERE + '_price_preview.html'
open(html, 'w').write('<html><head><meta charset="utf-8"></head><body style="margin:0;position:relative;width:%dpx;height:%dpx;background:#fff">%s%s</body></html>' % (W, H, ''.join(parts), head))
png = HERE + 'Arabica_price_2005_2026.png'
# headless Chromium keeps 87 px of window chrome: open a taller window so the viewport is W x H, then keep the top H rows
subprocess.run(['/opt/pw-browsers/chromium', '--headless', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', '--window-size=%d,%d' % (W, H + 87), '--screenshot=' + png, 'file://' + html],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def crop_png_rows(path, h):
    """Keep the first h scanlines (filters only look upwards, so no unfiltering is needed)."""
    import zlib, struct
    b = open(path, 'rb').read()
    pos, chunks = 8, []
    while pos < len(b):
        n = struct.unpack('>I', b[pos:pos + 4])[0]
        chunks.append((b[pos + 4:pos + 8], b[pos + 8:pos + 8 + n]))
        pos += 12 + n
    ihdr = dict(chunks)[b'IHDR']
    w, h0, depth, ctype = struct.unpack('>IIBB', ihdr[:10])
    assert depth == 8 and h0 >= h, (depth, h0)
    bpp = {2: 3, 6: 4, 0: 1, 4: 2}[ctype]
    raw = zlib.decompress(b''.join(d for t, d in chunks if t == b'IDAT'))[:h * (1 + w * bpp)]
    chunk = lambda t, d: struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    open(path, 'wb').write(b[:8] + chunk(b'IHDR', struct.pack('>II', w, h) + ihdr[8:]) + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))


crop_png_rows(png, H)
os.remove(html) if not os.environ.get("KEEP") else None
print('saved', png)
