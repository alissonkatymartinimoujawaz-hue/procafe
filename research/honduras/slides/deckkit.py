"""Small helper that writes each slide twice: native PowerPoint (ooxml.py, editable charts) and an HTML/SVG preview
rendered to PNG by headless Chromium, with the same geometry (inches). Standard library only."""
import os, sys, subprocess, zlib, struct
HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
sys.path.insert(0, HERE + '../../indonesia/slides')
import ooxml
from ooxml import Slide, run, para, save

K = 120                     # preview pixels per inch (13.333 x 7.5 in -> 1600 x 900)
W, H = 1600, 900
NAVY, BLUE, ORANGE, GREY, INK, LIGHT = '1F3864', '2E75B6', 'C55A11', '7F7F7F', '262626', 'BDD7EE'
GRID, AXIS = 'E3E8EB', '5B6770'


def esc(t):
    return str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def fr(v, d=2):
    """French decimal comma, half-up rounding (4.425 -> 4,43)."""
    import decimal
    q = decimal.Decimal(repr(float(v))).quantize(decimal.Decimal(1).scaleb(-d), rounding=decimal.ROUND_HALF_UP)
    s = str(q).replace('.', ',')
    return s.replace('-', '−')


def pct(v, d=1, sign=True):
    s = fr(v, d)
    return ('+' + s if sign and v > 0 else s) + ' %'


class Page:
    def __init__(self):
        self.s = Slide()
        self.svg = []
        self.html = []

    # ---- text -------------------------------------------------------------------------------------------------
    def title(self, t, sub=None):
        self.s.text(0.45, 0.22, 12.4, 0.55, [para(run(t, 24, True, color=NAVY))])
        self.html.append('<div style="position:absolute;left:%dpx;top:%dpx;width:%dpx;font:700 32px/1.15 Arial;color:#%s">%s</div>'
                         % (0.45 * K, 0.2 * K, 12.4 * K, NAVY, esc(t)))

    def bullets(self, items, x=0.75, y=0.78, w=11.9, h=0.95, sz=10.5):
        self.s.text(x, y, w, h, [para(run(b, sz, color=INK, hl='FFFF00'), bullet=True, after=1) for b in items])
        self.html.append('<div style="position:absolute;left:%dpx;top:%dpx;width:%dpx;font:%.1fpx/1.45 Arial;color:#%s">%s</div>' % (
            x * K, y * K + 2, w * K, sz * K / 72, INK, ''.join('<div>• <span style="background:#FFFF00">%s</span></div>' % esc(b) for b in items)))

    def source(self, t, y=7.02):
        self.s.text(0.45, y, 12.4, 0.42, [para(run(t, 7.5, color=GREY))])
        self.html.append('<div style="position:absolute;left:%dpx;top:%dpx;width:%dpx;font:12.5px/1.35 Arial;color:#%s">%s</div>' % (0.45 * K, y * K, 12.4 * K, GREY, esc(t)))

    def text(self, x, y, w, h, lines, sz=9, color=INK, algn='l', bold=False, fill=None, anchor='t'):
        """lines: list of str or (str, dict(b=, color=, sz=))"""
        ps, hs = [], []
        for ln in lines:
            t, o = (ln, {}) if isinstance(ln, str) else ln
            b, c, z = o.get('b', bold), o.get('color', color), o.get('sz', sz)
            ps.append(para(run(t, z, b, color=c), algn=algn))
            hs.append('<div style="font:%s %.1fpx/1.25 Arial;color:#%s">%s</div>' % ('700' if b else '400', z * K / 72, c, esc(t)))
        self.s.text(x, y, w, h, ps, anchor=anchor, fill=fill, inset=(0.04, 0.03, 0.04, 0.03) if fill else (0, 0, 0, 0))
        ta = {'l': 'left', 'ctr': 'center', 'r': 'right'}[algn]
        js = {'t': 'flex-start', 'ctr': 'center', 'b': 'flex-end'}[anchor]
        self.html.append('<div style="position:absolute;left:%dpx;top:%dpx;width:%dpx;height:%dpx;text-align:%s;display:flex;flex-direction:column;justify-content:%s;%s">%s</div>' % (
            x * K, y * K, w * K, h * K, ta, js, ('background:#%s;padding:4px 5px;box-sizing:border-box;' % fill) if fill else '', ''.join(hs)))

    def rect(self, x, y, w, h, fill, line=None, geom='rect'):
        self.s.rect(x, y, w, h, fill=fill, line=line, geom=geom)
        r = 'border-radius:50%;' if geom == 'ellipse' else ''
        self.html.append('<div style="position:absolute;left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx;background:#%s;%s%s"></div>' % (
            x * K, y * K, w * K, h * K, fill, ('border:1px solid #%s;box-sizing:border-box;' % line) if line else '', r))

    def table(self, x, y, colw, rowh, rows, sz=8.5, head_fill=NAVY, zebra='F2F5F8'):
        """rows: list of lists of str; first row is the header. Written as shapes so both outputs match."""
        yy = y
        for i, r in enumerate(rows):
            xx = x
            hh = rowh[i] if isinstance(rowh, (list, tuple)) else rowh
            for j, c in enumerate(r):
                fill = head_fill if i == 0 else (zebra if i % 2 == 0 else 'FFFFFF')
                col = 'FFFFFF' if i == 0 else INK
                self.text(xx, yy, colw[j], hh, [c] if isinstance(c, str) else c, sz=sz, color=col, bold=(i == 0), fill=fill, anchor='ctr',
                          algn='l' if j == 0 else 'ctr')
                xx += colw[j]
            yy += hh
        return yy

    # ---- charts ------------------------------------------------------------------------------------------------
    def plot_frame(self, x, y, w, h, lay):
        lx, ly, lw, lh = lay
        return x + w * lx, y + h * ly, w * lw, h * lh

    def bars(self, x, y, w, h, cats, vals, colors, ymax, unit, fmt='0.00', labels=None, lay=(0.05, 0.05, 0.93, 0.83),
             ymin=0, ylab=None, label_sz=8, xlab_every=1, series_name='value', line=None):
        """One bar series (native chart) + optional line series on the same axis. labels: list of str drawn above bars."""
        xml = ooxml.bar_chart(cats, [{'name': series_name, 'values': vals, 'color': colors[0] if isinstance(colors, list) else colors,
                                      'point_colors': colors if isinstance(colors, list) else None}],
                              mn=ymin, mx=ymax, unit=unit, fmt=fmt.replace('0.00', '0.0') if False else '0', labels=False, legend=False, gap=45, overlap=0)
        if line:
            ln = ('<c:lineChart><c:grouping val="standard"/><c:varyColors val="0"/><c:ser><c:idx val="1"/><c:order val="1"/><c:tx>%s</c:tx>'
                  '<c:spPr><a:ln w="28575" cap="rnd"><a:solidFill><a:srgbClr val="%s"/></a:solidFill><a:round/></a:ln></c:spPr>'
                  '<c:marker><c:symbol val="circle"/><c:size val="6"/><c:spPr><a:solidFill><a:srgbClr val="%s"/></a:solidFill><a:ln><a:noFill/></a:ln></c:spPr></c:marker>'
                  '<c:cat>%s</c:cat><c:val>%s</c:val><c:smooth val="0"/></c:ser><c:marker val="1"/><c:axId val="50010"/><c:axId val="50020"/></c:lineChart>') % (
                ooxml._strcache('Sheet1!$C$1', [line['name']]), line['color'], line['color'],
                ooxml._strcache('Sheet1!$A$2:$A$%d' % (len(cats) + 1), cats),
                ooxml._numref('Sheet1!$C$2:$C$%d' % (len(cats) + 1), [v if v is not None else '' for v in line['values']]))
            xml = xml.replace('</c:barChart>', '</c:barChart>' + ln, 1)
        self._native(x, y, w, h, xml, lay)
        px, py, pw, ph = self.plot_frame(x, y, w, h, lay)
        n = len(cats)
        Y = lambda v: py + ph * (1 - (v - ymin) / (ymax - ymin))
        self._grid(px, py, pw, ph, ymin, ymax, unit, fmt_axis='%g')
        bw = pw / n * (1 / 1.45)
        for i, v in enumerate(vals):
            if v is None:
                continue
            c = colors[i] if isinstance(colors, list) else colors
            bx = px + pw * (i + 0.5) / n - bw / 2
            self.svg.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#%s"/>' % (bx * K, Y(v) * K, bw * K, (Y(ymin) - Y(v)) * K, c))
        for i, c in enumerate(cats):
            if i % xlab_every == 0:
                self.svg.append('<text x="%.1f" y="%.1f" font-size="13" fill="#%s" text-anchor="middle">%s</text>' % ((px + pw * (i + 0.5) / n) * K, (py + ph) * K + 18, AXIS, esc(c)))
        if line:
            pts = [((px + pw * (i + 0.5) / n) * K, Y(v) * K) for i, v in enumerate(line['values']) if v is not None]
            self.svg.append('<polyline fill="none" stroke="#%s" stroke-width="3" points="%s"/>' % (line['color'], ' '.join('%.1f,%.1f' % p for p in pts)))
            for p in pts:
                self.svg.append('<circle cx="%.1f" cy="%.1f" r="4.5" fill="#%s"/>' % (p[0], p[1], line['color']))
        if labels:
            for i, (v, lb) in enumerate(zip(vals, labels)):
                if v is None or not lb:
                    continue
                self.text(px + pw * (i + 0.5) / n - 0.4, Y(v) - 0.24, 0.8, 0.22, [lb], sz=label_sz, algn='ctr', anchor='b')
        if ylab:
            self.text(x, y - 0.26, 3.5, 0.24, [ylab], sz=9, color=GREY)
        return px, py, pw, ph, Y

    def lines(self, x, y, w, h, cats, series, ymin, ymax, unit, lay=(0.05, 0.05, 0.93, 0.83), ylab=None, xlab_every=1, fmt_axis='%g'):
        xml = ooxml.line_chart(cats, [dict(name=s['name'], values=[v if v is not None else '' for v in s['values']], color=s['color'],
                                           width=s.get('width', 2.25), marker=s.get('marker', True), dash=s.get('dash'))
                                      for s in series], mn=ymin, mx=ymax, unit=unit, fmt='0', legend=False)
        self._native(x, y, w, h, xml, lay)
        px, py, pw, ph = self.plot_frame(x, y, w, h, lay)
        n = len(cats)
        Y = lambda v: py + ph * (1 - (v - ymin) / (ymax - ymin))
        self._grid(px, py, pw, ph, ymin, ymax, unit, fmt_axis)
        for i, c in enumerate(cats):
            if i % xlab_every == 0:
                self.svg.append('<text x="%.1f" y="%.1f" font-size="13" fill="#%s" text-anchor="middle">%s</text>' % ((px + pw * (i + 0.5) / n) * K, (py + ph) * K + 18, AXIS, esc(c)))
        for s in series:
            pts = [((px + pw * (i + 0.5) / n) * K, Y(v) * K) for i, v in enumerate(s['values']) if v is not None]
            dash = ' stroke-dasharray="8,5"' if s.get('dash') else ''
            self.svg.append('<polyline fill="none" stroke="#%s" stroke-width="%.1f"%s stroke-linejoin="round" points="%s"/>' % (
                s['color'], s.get('width', 2.25) * 1.4, dash, ' '.join('%.1f,%.1f' % p for p in pts)))
            if s.get('marker', True):
                for p in pts:
                    self.svg.append('<circle cx="%.1f" cy="%.1f" r="4.5" fill="#%s"/>' % (p[0], p[1], s['color']))
        if ylab:
            self.text(x, y - 0.26, 4, 0.24, [ylab], sz=9, color=GREY)
        return px, py, pw, ph, Y

    def _grid(self, px, py, pw, ph, ymin, ymax, unit, fmt_axis='%g'):
        v = ymin
        while v <= ymax + 1e-9:
            yy = (py + ph * (1 - (v - ymin) / (ymax - ymin))) * K
            self.svg.append('<line x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" stroke="#%s"/>' % (px * K, (px + pw) * K, yy, yy, GRID))
            self.svg.append('<text x="%.1f" y="%.1f" font-size="13" fill="#%s" text-anchor="end">%s</text>' % (px * K - 8, yy + 4, AXIS, (fmt_axis % v).replace('.', ',')))
            v += unit

    def _native(self, x, y, w, h, xml, lay):
        lx, ly, lw, lh = lay
        m = ('<c:layout><c:manualLayout><c:layoutTarget val="inner"/><c:xMode val="edge"/><c:yMode val="edge"/>'
             '<c:x val="%s"/><c:y val="%s"/><c:w val="%s"/><c:h val="%s"/></c:manualLayout></c:layout>') % (lx, ly, lw, lh)
        xml = xml.replace('<c:plotArea><c:layout/>', '<c:plotArea>' + m, 1)
        xml = xml.replace('</c:valAx></c:plotArea>', '</c:valAx><c:spPr><a:noFill/><a:ln><a:noFill/></a:ln></c:spPr></c:plotArea>', 1)
        self.s.chart(x, y, w, h, xml)

    def dot(self, x, y, d, fill, geom='ellipse', hollow=False, line=None):
        """Marker centred on (x, y) inches, diameter d. hollow = white fill with coloured border (unverified values)."""
        f, ln = ('FFFFFF', fill) if hollow else (fill, line or 'FFFFFF')
        self.s.rect(x - d / 2, y - d / 2, d, d, fill=f, line=ln, geom=geom, lw=1.75 if hollow else 1)
        if geom == 'diamond':
            self.svg.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#%s" stroke="#%s" stroke-width="%.1f" transform="rotate(45 %.1f %.1f)"/>' % (
                (x - d / 2.8) * K, (y - d / 2.8) * K, d / 1.4 * K, d / 1.4 * K, f, ln, 2.5 if hollow else 1.2, x * K, y * K))
        elif geom == 'rect':
            self.svg.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#%s" stroke="#%s" stroke-width="%.1f"/>' % (
                (x - d / 2) * K, (y - d / 2) * K, d * K, d * K, f, ln, 2.5 if hollow else 1.2))
        else:
            self.svg.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#%s" stroke="#%s" stroke-width="%.1f"/>' % (x * K, y * K, d / 2 * K, f, ln, 2.5 if hollow else 1.2))

    def hline(self, x0, x1, y, color, w=0.02, dash=False):
        self.s.rect(x0, y - w / 2, x1 - x0, w, fill=color)
        self.svg.append('<line x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" stroke="#%s" stroke-width="%.1f"%s/>' % (
            x0 * K, x1 * K, y * K, y * K, color, w * K, ' stroke-dasharray="6,4"' if dash else ''))

    def vline(self, x, y0, y1, color, w=0.015):
        self.s.rect(x - w / 2, y0, w, y1 - y0, fill=color)
        self.svg.append('<line x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" stroke="#%s" stroke-width="%.1f"/>' % (x * K, x * K, y0 * K, y1 * K, color, w * K))

    def band(self, x0, x1, y0, y1, fill, label=None, color=ORANGE):
        """Shaded background band in inches (drawn before the chart so it sits behind it)."""
        self.s.rect(x0, y0, x1 - x0, y1 - y0, fill=fill)
        self.svg.insert(0, '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#%s"/>' % (x0 * K, y0 * K, (x1 - x0) * K, (y1 - y0) * K, fill))
        if label:
            self.text(x0, y0 + 0.03, x1 - x0, 0.4, [(l, dict(b=True, color=color)) for l in label], sz=8.5, algn='ctr')

    def legend(self, x, y, items, sz=9):
        """items: list of (color, label, kind) kind='box'|'line'"""
        xx = x
        for c, lb, kind in items:
            if kind == 'line':
                self.rect(xx, y + 0.08, 0.3, 0.04, c)
            else:
                self.rect(xx + 0.05, y + 0.03, 0.18, 0.14, c)
            self.text(xx + 0.36, y - 0.01, 3.2, 0.22, [lb], sz=sz)
            xx += 0.45 + len(lb) * sz * 0.0068

    # ---- output ------------------------------------------------------------------------------------------------
    def render(self, png):
        html = png[:-4] + '_preview.html'
        body = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Arial" style="position:absolute;left:0;top:0">%s</svg>'
                % (W, H, ''.join(self.svg))) + ''.join(self.html)
        open(html, 'w').write('<html><head><meta charset="utf-8"></head><body style="margin:0;position:relative;width:%dpx;height:%dpx;background:#fff;overflow:hidden">%s</body></html>' % (W, H, body))
        # headless Chromium keeps 87 px of window chrome: open a taller window, keep the top H rows
        subprocess.run(['/opt/pw-browsers/chromium', '--headless', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', '--window-size=%d,%d' % (W, H + 87),
                        '--screenshot=' + png, 'file://' + html], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        crop_png_rows(png, H)
        if not os.environ.get('KEEP'):
            os.remove(html)


def crop_png_rows(path, h):
    """Keep the first h scanlines (PNG filters only look upwards, so no unfiltering is needed)."""
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
