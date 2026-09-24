"""Rough HTML preview of a PPTX written by ooxml.py (text boxes, shapes, tables, bar/line charts)."""
import sys, zipfile, re, html
import xml.dom.minidom as md

PX = 100 / 914400  # 100 px per inch
path, out = sys.argv[1], sys.argv[2]
z = zipfile.ZipFile(path)


def ch(n, tag):
    return [c for c in n.childNodes if c.nodeType == 1 and c.tagName == tag]


def first(n, tag):
    r = n.getElementsByTagName(tag)
    return r[0] if r else None


def xfrm(n):
    o, e = first(n, 'a:off'), first(n, 'a:ext')
    return int(o.getAttribute('x')) * PX, int(o.getAttribute('y')) * PX, int(e.getAttribute('cx')) * PX, int(e.getAttribute('cy')) * PX


def color(n):
    c = first(n, 'a:srgbClr') if n else None
    return '#' + c.getAttribute('val') if c else None


def paras(tx):
    out = ''
    for p in tx.getElementsByTagName('a:p'):
        ppr = first(p, 'a:pPr')
        algn = {'ctr': 'center', 'r': 'right'}.get(ppr.getAttribute('algn') if ppr else 'l', 'left')
        bul = ppr is not None and first(ppr, 'a:buChar') is not None
        runs = ''
        for r in p.getElementsByTagName('a:r'):
            rp = first(r, 'a:rPr')
            sz = int(rp.getAttribute('sz') or 1800) / 100 * 100 / 72
            fill = [c for c in rp.childNodes if c.nodeType == 1 and c.tagName == 'a:solidFill']
            col = '#' + first(fill[0], 'a:srgbClr').getAttribute('val') if fill else '#000'
            hl = first(rp, 'a:highlight')
            bg = 'background:#' + first(hl, 'a:srgbClr').getAttribute('val') + ';' if hl else ''
            t = ''.join(x.data for x in first(r, 'a:t').childNodes)
            runs += '<span style="font-size:%.1fpx;color:%s;%s%s">%s</span>' % (sz, col, 'font-weight:700;' if rp.getAttribute('b') == '1' else '', bg, html.escape(t))
        out += '<div style="text-align:%s;%s">%s%s</div>' % (algn, 'padding-left:18px;text-indent:-12px;' if bul else '', '• ' if bul else '', runs)
    return out


def scatter_svg(d, w, h):
    axes = d.getElementsByTagName('c:valAx')
    rng = []
    for ax in axes:
        mn, mx = first(ax, 'c:min'), first(ax, 'c:max')
        rng.append((float(mn.getAttribute('val')), float(mx.getAttribute('val'))))
    (x0, x1), (y0, y1) = rng
    L, R, T, B = 40, 10, 10, 50
    pw, ph = w - L - R, h - T - B
    X = lambda v: L + pw * (v - x0) / (x1 - x0)
    Yf = lambda v: T + ph * (1 - (v - y0) / (y1 - y0))
    svg = ['<svg width="%d" height="%d" style="position:absolute;left:0;top:0">' % (w, h)]
    for k in range(6):
        v = y0 + (y1 - y0) * k / 5
        svg.append('<line x1="%d" x2="%d" y1="%.1f" y2="%.1f" stroke="#e3e8eb"/><text x="%d" y="%.1f" font-size="9" text-anchor="end" fill="#555">%g</text>' % (L, L + pw, Yf(v), Yf(v), L - 3, Yf(v) + 3, v))
        u = x0 + (x1 - x0) * k / 5
        svg.append('<text x="%.1f" y="%.1f" font-size="9" text-anchor="middle" fill="#555">%g</text>' % (X(u), T + ph + 12, u))
    lx = L
    for s in d.getElementsByTagName('c:ser'):
        name = first(first(s, 'c:tx'), 'c:v').firstChild.data
        col = color(first(s, 'c:marker'))
        xs = {int(p.getAttribute('idx')): float(first(p, 'c:v').firstChild.data) for p in first(s, 'c:xVal').getElementsByTagName('c:pt')}
        ys = {int(p.getAttribute('idx')): float(first(p, 'c:v').firstChild.data) for p in first(s, 'c:yVal').getElementsByTagName('c:pt')}
        lb = {}
        for dl in s.getElementsByTagName('c:dLbl'):
            lb[int(first(dl, 'c:idx').getAttribute('val'))] = first(dl, 'a:t').firstChild.data
        for i in xs:
            svg.append('<circle cx="%.1f" cy="%.1f" r="4" fill="%s"/><text x="%.1f" y="%.1f" font-size="8" fill="#555">%s</text>' % (X(xs[i]), Yf(ys[i]), col, X(xs[i]) + 5, Yf(ys[i]) + 3, lb.get(i, '')))
        svg.append('<rect x="%d" y="%d" width="8" height="8" fill="%s"/><text x="%d" y="%d" font-size="8">%s</text>' % (lx, h - 20, col, lx + 11, h - 13, html.escape(name)))
        lx += 20 + 5 * len(name)
    svg.append('</svg>')
    return ''.join(svg)


def chart_svg(cx, w, h):
    d = md.parseString(cx)
    if d.getElementsByTagName('c:scatterChart'):
        return scatter_svg(d, w, h)
    horiz = any(x.getAttribute('val') == 'bar' for x in d.getElementsByTagName('c:barDir'))
    cats = [v.firstChild.data for v in first(first(d, 'c:cat'), 'c:strCache').getElementsByTagName('c:v')] if first(d, 'c:cat') else []
    n = len(cats)
    sers = []
    for kind in ('c:barChart', 'c:lineChart'):
        for blk in d.getElementsByTagName(kind):
            for s in ch(blk, 'c:ser'):
                name = first(first(s, 'c:tx'), 'c:v').firstChild.data
                sp = first(s, 'c:spPr')
                col = color(sp) or '#888'
                pcs = {}
                for dp in ch(s, 'c:dPt'):
                    pcs[int(first(dp, 'c:idx').getAttribute('val'))] = color(dp) or col
                vals = [None] * n
                nc = first(first(s, 'c:val'), 'c:numCache')
                for pt in nc.getElementsByTagName('c:pt'):
                    vals[int(pt.getAttribute('idx'))] = float(first(pt, 'c:v').firstChild.data)
                dash = first(s, 'a:prstDash') is not None
                sers.append((kind, name, col, vals, dash, pcs))
    va = [a for a in d.getElementsByTagName('c:valAx')][0]
    mx, mn = first(va, 'c:max'), first(va, 'c:min')
    allv = [v for s in sers for v in s[3] if v is not None]
    lo = float(mn.getAttribute('val')) if mn else min(allv + [0])
    hi = float(mx.getAttribute('val')) if mx else max(allv)
    L, R, T, B = (200 if horiz else 34), 6, 8, 50
    pw, ph = w - L - R, h - T - B
    Y = lambda v: T + ph * (1 - (v - lo) / (hi - lo))
    X = lambda i: L + pw * (i + 0.5) / n
    svg = ['<svg width="%d" height="%d" style="position:absolute;left:0;top:0">' % (w, h)]
    for k in range(6):
        v = lo + (hi - lo) * k / 5
        svg.append('<line x1="%d" x2="%d" y1="%.1f" y2="%.1f" stroke="#e3e8eb"/><text x="%d" y="%.1f" font-size="9" text-anchor="end" fill="#555">%s</text>' % (L, L + pw, Y(v), Y(v), L - 3, Y(v) + 3, ('%.1f' % v).rstrip('0').rstrip('.')))
    bars = [s for s in sers if s[0] == 'c:barChart']
    ov = first(d, 'c:overlap')
    stackish = ov is not None and ov.getAttribute('val') == '100'
    nb = 1 if stackish else max(1, len(bars))
    bw = pw / n * 0.6 / nb
    for j, (_, name, col, vals, _, pcs) in enumerate(bars):
        for i, v in enumerate(vals):
            if v is None:
                continue
            c_ = pcs.get(i, col)
            if horiz:
                ybar = T + ph * (1 - (i + 0.5) / n) - ph / n * 0.3 + j * (ph / n * 0.6 / nb)
                xv = lambda v_: L + pw * (v_ - lo) / (hi - lo)
                x0_, x1_ = xv(max(lo, 0)), xv(v)
                svg.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>' % (min(x0_, x1_), ybar, abs(x1_ - x0_), ph / n * 0.6 / nb, c_))
                continue
            x = X(i) - pw / n * 0.3 + (0 if stackish else j) * bw
            y0, y1 = Y(max(lo, 0)), Y(v)
            svg.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>' % (x, min(y0, y1), bw, abs(y1 - y0), c_))
    for kind, name, col, vals, dash, _ in sers:
        if kind != 'c:lineChart':
            continue
        pts = ' '.join('%.1f,%.1f' % (X(i), Y(v)) for i, v in enumerate(vals) if v is not None)
        svg.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.5" %s/>' % (pts, col, 'stroke-dasharray="5 3"' if dash else ''))
    skip = first(d, 'c:tickLblSkip')
    sk = int(skip.getAttribute('val')) if skip else 1
    if horiz:
        L2 = 200
        for i, c in enumerate(cats):
            svg.append('<text x="%d" y="%.1f" font-size="8" text-anchor="start" fill="#555">%s</text>' % (2, T + ph * (1 - (i + 0.5) / n) + 3, html.escape(c)))
        cats = []
    for i, c in enumerate(cats):
        if i % sk == 0:
            svg.append('<text x="%.1f" y="%.1f" font-size="8" text-anchor="middle" fill="#555">%s</text>' % (X(i), T + ph + 11, html.escape(c)))
    leg = first(d, 'c:legend')
    if leg:
        lx = L
        for kind, name, col, vals, dash, _ in sers:
            svg.append('<rect x="%d" y="%d" width="10" height="6" fill="%s"/><text x="%d" y="%d" font-size="8" fill="#222">%s</text>' % (lx, h - 22, col, lx + 13, h - 16, html.escape(name)))
            lx += 16 + 5 * len(name)
    svg.append('</svg>')
    return ''.join(svg)


pres = md.parseString(z.read('ppt/presentation.xml'))
nsl = len(pres.getElementsByTagName('p:sldId'))
page = ['<html><body style="margin:0;background:#666;font-family:Arial">']
for k in range(1, nsl + 1):
    sx = md.parseString(z.read('ppt/slides/slide%d.xml' % k))
    rels = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', z.read('ppt/slides/_rels/slide%d.xml.rels' % k).decode()))
    bg = color(first(sx, 'p:bgPr')) or '#fff'
    page.append('<div style="position:relative;width:1333px;height:750px;background:%s;margin:0 0 12px 0;overflow:hidden">' % bg)
    tree = first(sx, 'p:spTree')
    for node in tree.childNodes:
        if node.nodeType != 1:
            continue
        if node.tagName == 'p:sp':
            x, y, w, h = xfrm(node)
            sp = first(node, 'p:spPr')
            fill = [c for c in sp.childNodes if c.nodeType == 1 and c.tagName == 'a:solidFill']
            f = 'background:%s;' % ('#' + first(fill[0], 'a:srgbClr').getAttribute('val')) if fill else ''
            tx = first(node, 'p:txBody')
            page.append('<div style="position:absolute;left:%.0fpx;top:%.0fpx;width:%.0fpx;height:%.0fpx;%soutline:1px dashed rgba(255,0,0,.25);line-height:1.2">%s</div>' % (x, y, w, h, f, paras(tx) if tx else ''))
        elif node.tagName == 'p:graphicFrame':
            x, y, w, h = xfrm(first(node, 'p:xfrm'))
            tbl = first(node, 'a:tbl')
            if tbl:
                cols = [int(g.getAttribute('w')) * PX for g in tbl.getElementsByTagName('a:gridCol')]
                rows = ''
                for tr in tbl.getElementsByTagName('a:tr'):
                    rh = int(tr.getAttribute('h')) * PX
                    tds = ''
                    for j, tc in enumerate(tr.getElementsByTagName('a:tc')):
                        tcp = first(tc, 'a:tcPr')
                        fl = [c for c in tcp.childNodes if c.nodeType == 1 and c.tagName == 'a:solidFill']
                        bgc = '#' + first(fl[0], 'a:srgbClr').getAttribute('val') if fl else 'transparent'
                        tds += '<td style="width:%.0fpx;height:%.0fpx;background:%s;border-top:1px solid #d5dde1;padding:0 6px">%s</td>' % (cols[j], rh, bgc, paras(first(tc, 'a:txBody')))
                    rows += '<tr>%s</tr>' % tds
                page.append('<table style="position:absolute;left:%.0fpx;top:%.0fpx;border-collapse:collapse;table-layout:fixed">%s</table>' % (x, y, rows))
            else:
                rid = first(node, 'c:chart').getAttribute('r:id')
                target = 'ppt/' + rels[rid].replace('../', '')
                page.append('<div style="position:absolute;left:%.0fpx;top:%.0fpx;width:%.0fpx;height:%.0fpx;outline:1px solid #ccc">%s</div>' % (x, y, w, h, chart_svg(z.read(target), w, h)))
    page.append('</div>')
page.append('</body></html>')
open(out, 'w').write(''.join(page))
print('preview', nsl, 'slides')
