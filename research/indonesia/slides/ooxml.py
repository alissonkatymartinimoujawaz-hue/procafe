"""Minimal PPTX writer (standard library only): shapes, text, tables, native charts with cached data."""
import zipfile
from xml.sax.saxutils import escape

NS_A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
NS_R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
NS_P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
NS_C = 'http://schemas.openxmlformats.org/drawingml/2006/chart'
EMU = 914400
W, H = 12192000, 6858000


def e(v):
    return int(round(v * EMU))


def esc(t):
    return escape(str(t), {'"': '&quot;'})


# ---------- text ----------
def run(t, sz=14, b=False, i=False, color='1F2A30', font='Arial', hl=None):
    return ('<a:r><a:rPr lang="en-GB" sz="%d"%s%s dirty="0"><a:solidFill><a:srgbClr val="%s"/></a:solidFill>%s'
            '<a:latin typeface="%s"/><a:cs typeface="%s"/></a:rPr><a:t>%s</a:t></a:r>') % (
        int(sz * 100), ' b="1"' if b else '', ' i="1"' if i else '', color, ('<a:highlight><a:srgbClr val="%s"/></a:highlight>' % hl) if hl else '', font, font, esc(t))


def para(runs, algn='l', after=0, before=0, bullet=False, line=None, indent=0.22):
    ppr = '<a:pPr algn="%s"%s>' % (algn, (' marL="%d" indent="-%d"' % (e(indent), e(indent))) if bullet else ' marL="0" indent="0"')
    if line:
        ppr += '<a:lnSpc><a:spcPct val="%d"/></a:lnSpc>' % int(line * 1000)
    ppr += '<a:spcBef><a:spcPts val="%d"/></a:spcBef><a:spcAft><a:spcPts val="%d"/></a:spcAft>' % (int(before * 100), int(after * 100))
    ppr += '<a:buFont typeface="Arial"/><a:buChar char="&#8226;"/>' if bullet else '<a:buNone/>'
    ppr += '</a:pPr>'
    if isinstance(runs, str) and not runs.startswith('<a:r>'):
        runs = run(runs)
    elif isinstance(runs, (list, tuple)):
        runs = ''.join(runs)
    return '<a:p>%s%s</a:p>' % (ppr, runs)


class Slide:
    def __init__(self, bg='FFFFFF'):
        self.bg = bg
        self.items = []
        self.charts = []  # chart xml strings
        self.nid = 2

    def _id(self):
        self.nid += 1
        return self.nid

    def rect(self, x, y, w, h, fill=None, line=None, geom='rect', radius=None, lw=1):
        i = self._id()
        av = '<a:avLst><a:gd name="adj" fmla="val %d"/></a:avLst>' % radius if radius is not None else '<a:avLst/>'
        f = '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>' % fill if fill else '<a:noFill/>'
        ln = '<a:ln w="%d"><a:solidFill><a:srgbClr val="%s"/></a:solidFill></a:ln>' % (int(lw * 12700), line) if line else '<a:ln><a:noFill/></a:ln>'
        self.items.append('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="Shape %d"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
                          '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="%s">%s</a:prstGeom>%s%s</p:spPr></p:sp>'
                          % (i, i, e(x), e(y), e(w), e(h), geom, av, f, ln))

    def text(self, x, y, w, h, paras, anchor='t', fill=None, inset=(0, 0, 0, 0), autofit=False):
        i = self._id()
        f = '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>' % fill if fill else '<a:noFill/>'
        body = ''.join(paras)
        self.items.append('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="TextBox %d"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
                          '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>%s<a:ln><a:noFill/></a:ln></p:spPr>'
                          '<p:txBody><a:bodyPr wrap="square" lIns="%d" tIns="%d" rIns="%d" bIns="%d" anchor="%s" rtlCol="0">%s</a:bodyPr><a:lstStyle/>%s</p:txBody></p:sp>'
                          % (i, i, e(x), e(y), e(w), e(h), f, e(inset[0]), e(inset[1]), e(inset[2]), e(inset[3]), anchor,
                             '<a:normAutofit/>' if autofit else '<a:noAutofit/>', body))

    def table(self, x, y, colw, rowh, rows):
        """rows: list of list of cells; cell = dict(t, sz, b, color, fill, algn)"""
        i = self._id()
        grid = ''.join('<a:gridCol w="%d"/>' % e(c) for c in colw)
        trs = ''
        for r in rows:
            tcs = ''
            for c in r:
                txt = para(run(c.get('t', ''), c.get('sz', 11), c.get('b', False), False, c.get('color', '1F2A30')), c.get('algn', 'l'))
                fill = '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>' % c['fill'] if c.get('fill') else '<a:noFill/>'
                ln = lambda tag, show: ('<a:%s w="6350"><a:solidFill><a:srgbClr val="D5DDE1"/></a:solidFill></a:%s>' % (tag, tag)) if show else ('<a:%s w="0"><a:noFill/></a:%s>' % (tag, tag))
                tcs += ('<a:tc><a:txBody><a:bodyPr/><a:lstStyle/>%s</a:txBody><a:tcPr marL="%d" marR="%d" marT="%d" marB="%d" anchor="ctr">%s%s%s%s%s</a:tcPr></a:tc>'
                        % (txt, e(0.08), e(0.08), e(0.03), e(0.03), ln('lnL', False), ln('lnR', False), ln('lnT', True), ln('lnB', True), fill))
            trs += '<a:tr h="%d">%s</a:tr>' % (e(rowh), tcs)
        self.items.append('<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="%d" name="Table %d"/><p:cNvGraphicFramePr><a:graphicFrameLocks noGrp="1"/></p:cNvGraphicFramePr><p:nvPr/></p:nvGraphicFramePr>'
                          '<p:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></p:xfrm><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table">'
                          '<a:tbl><a:tblPr firstRow="1" bandRow="0"/><a:tblGrid>%s</a:tblGrid>%s</a:tbl></a:graphicData></a:graphic></p:graphicFrame>'
                          % (i, i, e(x), e(y), e(sum(colw)), e(rowh * len(rows)), grid, trs))

    def chart(self, x, y, w, h, chart_xml):
        i = self._id()
        self.charts.append(chart_xml)
        rid = 'rId%d' % (len(self.charts) + 1)
        self.items.append('<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="%d" name="Chart %d"/><p:cNvGraphicFramePr/><p:nvPr/></p:nvGraphicFramePr>'
                          '<p:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></p:xfrm><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/chart">'
                          '<c:chart xmlns:c="%s" r:id="%s"/></a:graphicData></a:graphic></p:graphicFrame>' % (i, i, e(x), e(y), e(w), e(h), NS_C, rid))

    def xml(self):
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<p:sld xmlns:a="%s" xmlns:r="%s" xmlns:p="%s"><p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="%s"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>'
                '<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
                '%s</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>') % (NS_A, NS_R, NS_P, self.bg, ''.join(self.items))


# ---------- charts ----------
def _txpr(sz=11, color='5B6770', b=False):
    return ('<c:txPr><a:bodyPr/><a:lstStyle/><a:p><a:pPr><a:defRPr sz="%d" b="%d"><a:solidFill><a:srgbClr val="%s"/></a:solidFill>'
            '<a:latin typeface="Arial"/><a:cs typeface="Arial"/></a:defRPr></a:pPr><a:endParaRPr lang="fr-FR"/></a:p></c:txPr>') % (int(sz * 100), 1 if b else 0, color)


def _strcache(ref, vals):
    return '<c:strRef><c:f>%s</c:f><c:strCache><c:ptCount val="%d"/>%s</c:strCache></c:strRef>' % (
        ref, len(vals), ''.join('<c:pt idx="%d"><c:v>%s</c:v></c:pt>' % (k, esc(v)) for k, v in enumerate(vals)))


def _numref(ref, vals, fmt='General'):
    pts = ''.join('<c:pt idx="%d"><c:v>%s</c:v></c:pt>' % (k, v) for k, v in enumerate(vals) if v is not None)
    return '<c:numRef><c:f>%s</c:f><c:numCache><c:formatCode>%s</c:formatCode><c:ptCount val="%d"/>%s</c:numCache></c:numRef>' % (ref, fmt, len(vals), pts)


def _col(n):
    return chr(ord('A') + n)


def _ax_val(axid, cross, pos, mn=None, mx=None, unit=None, fmt='0', grid=True, title=None, delete=False, crosses='autoZero', between=True):
    sc = '<c:scaling><c:orientation val="minMax"/>%s%s</c:scaling>' % ('<c:max val="%s"/>' % mx if mx is not None else '', '<c:min val="%s"/>' % mn if mn is not None else '')
    g = '<c:majorGridlines><c:spPr><a:ln w="6350"><a:solidFill><a:srgbClr val="E3E8EB"/></a:solidFill></a:ln></c:spPr></c:majorGridlines>' if grid else ''
    tt = ''
    if title:
        tt = ('<c:title><c:tx><c:rich><a:bodyPr rot="%d" vert="horz"/><a:lstStyle/><a:p><a:pPr><a:defRPr sz="1000" b="0"><a:solidFill><a:srgbClr val="5B6770"/></a:solidFill><a:latin typeface="Arial"/></a:defRPr></a:pPr>'
              '<a:r><a:rPr lang="fr-FR" sz="1000" b="0"><a:solidFill><a:srgbClr val="5B6770"/></a:solidFill><a:latin typeface="Arial"/></a:rPr><a:t>%s</a:t></a:r></a:p></c:rich></c:tx><c:overlay val="0"/></c:title>') % (
            -5400000 if pos == 'l' else 0, esc(title))
    cr = '<c:crosses val="%s"/>' % crosses if not crosses.startswith('at:') else '<c:crossesAt val="%s"/>' % crosses[3:]
    return ('<c:valAx><c:axId val="%d"/>%s<c:delete val="%d"/><c:axPos val="%s"/>%s%s<c:numFmt formatCode="%s" sourceLinked="0"/><c:majorTickMark val="none"/><c:minorTickMark val="none"/>'
            '<c:tickLblPos val="low"/><c:spPr><a:ln w="6350"><a:solidFill><a:srgbClr val="%s"/></a:solidFill></a:ln></c:spPr>%s<c:crossAx val="%d"/>%s<c:crossBetween val="%s"/>%s</c:valAx>') % (
        axid, sc, 1 if delete else 0, pos, g, tt, esc(fmt), 'B7C0C5' if pos == 'b' else 'FFFFFF', _txpr(8), cross, cr, 'between' if between else 'midCat',
        '<c:majorUnit val="%s"/>' % unit if unit else '')


def _ax_cat(axid, cross, skip=None):
    return ('<c:catAx><c:axId val="%d"/><c:scaling><c:orientation val="minMax"/></c:scaling><c:delete val="0"/><c:axPos val="b"/><c:numFmt formatCode="General" sourceLinked="0"/>'
            '<c:majorTickMark val="none"/><c:minorTickMark val="none"/><c:tickLblPos val="low"/><c:spPr><a:ln w="9525"><a:solidFill><a:srgbClr val="B7C0C5"/></a:solidFill></a:ln></c:spPr>%s'
            '<c:crossAx val="%d"/><c:crosses val="autoZero"/><c:auto val="1"/><c:lblAlgn val="ctr"/><c:lblOffset val="100"/>%s<c:noMultiLvlLbl val="0"/></c:catAx>') % (
        axid, _txpr(8), cross, '<c:tickLblSkip val="%d"/>' % skip if skip else '')


def _wrap(plot, legend=True, legend_pos='b', legend_sz=8):
    leg = '<c:legend><c:legendPos val="%s"/><c:overlay val="0"/>%s</c:legend>' % (legend_pos, _txpr(legend_sz, '1F2A30')) if legend else ''
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><c:chartSpace xmlns:c="%s" xmlns:a="%s" xmlns:r="%s"><c:roundedCorners val="0"/>'
            '<c:chart><c:autoTitleDeleted val="1"/><c:plotArea><c:layout/>%s</c:plotArea>%s<c:plotVisOnly val="1"/><c:dispBlanksAs val="gap"/></c:chart>'
            '<c:spPr><a:noFill/><a:ln><a:noFill/></a:ln></c:spPr>%s</c:chartSpace>') % (NS_C, NS_A, NS_R, plot, leg, _txpr(10))


def _dlbls(pos='outEnd', sz=10, color='1F2A30', fmt='0'):
    return ('<c:dLbls><c:numFmt formatCode="%s" sourceLinked="0"/><c:spPr><a:noFill/><a:ln><a:noFill/></a:ln></c:spPr>%s<c:dLblPos val="%s"/><c:showLegendKey val="0"/><c:showVal val="1"/>'
            '<c:showCatName val="0"/><c:showSerName val="0"/><c:showPercent val="0"/><c:showBubbleSize val="0"/></c:dLbls>') % (esc(fmt), _txpr(sz, color, True), pos)


def bar_chart(cats, series, mn=0, mx=None, unit=None, fmt='0', labels=True, legend=True, gap=60, overlap=-8, ytitle=None):
    """series: list of dict(name, values, color, point_colors=optional list)"""
    ser = ''
    for k, s in enumerate(series):
        dpts = ''
        for j, pc in enumerate(s.get('point_colors') or []):
            dpts += '<c:dPt><c:idx val="%d"/><c:invertIfNegative val="0"/><c:bubble3D val="0"/><c:spPr><a:solidFill><a:srgbClr val="%s"/></a:solidFill></c:spPr></c:dPt>' % (j, pc)
        ser += ('<c:ser><c:idx val="%d"/><c:order val="%d"/><c:tx>%s</c:tx><c:spPr><a:solidFill><a:srgbClr val="%s"/></a:solidFill></c:spPr><c:invertIfNegative val="0"/>%s%s'
                '<c:cat>%s</c:cat><c:val>%s</c:val></c:ser>') % (
            k, k, _strcache('Sheet1!$%s$1' % _col(k + 1), [s['name']]), s['color'], dpts, _dlbls('outEnd', 10, '1F2A30', fmt) if labels else '',
            _strcache('Sheet1!$A$2:$A$%d' % (len(cats) + 1), cats), _numref('Sheet1!$%s$2:$%s$%d' % (_col(k + 1), _col(k + 1), len(cats) + 1), s['values']))
    plot = ('<c:barChart><c:barDir val="col"/><c:grouping val="clustered"/><c:varyColors val="0"/>%s<c:gapWidth val="%d"/><c:overlap val="%d"/><c:axId val="50010"/><c:axId val="50020"/></c:barChart>'
            % (ser, gap, overlap)) + _ax_cat(50010, 50020) + _ax_val(50020, 50010, 'l', mn, mx, unit, fmt, True, ytitle)
    return _wrap(plot, legend)


def line_chart(cats, series, mn=None, mx=None, unit=None, fmt='0', skip=None, legend=True, ytitle=None):
    ser = ''
    for k, s in enumerate(series):
        dash = '<a:prstDash val="dash"/>' if s.get('dash') else ''
        mk = ('<c:marker><c:symbol val="circle"/><c:size val="5"/><c:spPr><a:solidFill><a:srgbClr val="%s"/></a:solidFill><a:ln><a:noFill/></a:ln></c:spPr></c:marker>' % s['color']) if s.get('marker') else '<c:marker><c:symbol val="none"/></c:marker>'
        ser += ('<c:ser><c:idx val="%d"/><c:order val="%d"/><c:tx>%s</c:tx><c:spPr><a:ln w="%d" cap="rnd"><a:solidFill><a:srgbClr val="%s"/></a:solidFill>%s<a:round/></a:ln></c:spPr>%s'
                '<c:cat>%s</c:cat><c:val>%s</c:val><c:smooth val="0"/></c:ser>') % (
            k, k, _strcache('Sheet1!$%s$1' % _col(k + 1), [s['name']]), int(s.get('width', 2.25) * 12700), s['color'], dash, mk,
            _strcache('Sheet1!$A$2:$A$%d' % (len(cats) + 1), cats), _numref('Sheet1!$%s$2:$%s$%d' % (_col(k + 1), _col(k + 1), len(cats) + 1), s['values']))
    plot = ('<c:lineChart><c:grouping val="standard"/><c:varyColors val="0"/>%s<c:marker val="1"/><c:axId val="60010"/><c:axId val="60020"/></c:lineChart>' % ser) + \
        _ax_cat(60010, 60020, skip) + _ax_val(60020, 60010, 'l', mn, mx, unit, fmt, True, ytitle)
    return _wrap(plot, legend)


def scatter_chart(series, xmn, xmx, xunit, ymn, ymx, yunit, xfmt='0.0', yfmt='0', xtitle=None, ytitle=None, legend=True):
    """series: dict(name, xs, ys, color, labels=list or None)"""
    ser = ''
    for k, s in enumerate(series):
        n = len(s['xs'])
        dl = ''
        if s.get('labels'):
            lbls = ''.join(('<c:dLbl><c:idx val="%d"/><c:tx><c:rich><a:bodyPr/><a:lstStyle/><a:p><a:r><a:rPr lang="fr-FR" sz="800"><a:solidFill><a:srgbClr val="5B6770"/></a:solidFill><a:latin typeface="Arial"/></a:rPr><a:t>%s</a:t></a:r></a:p></c:rich></c:tx>'
                            '<c:spPr><a:noFill/><a:ln><a:noFill/></a:ln></c:spPr><c:dLblPos val="r"/><c:showLegendKey val="0"/><c:showVal val="0"/><c:showCatName val="0"/><c:showSerName val="0"/><c:showPercent val="0"/><c:showBubbleSize val="0"/></c:dLbl>') % (j, esc(lb))
                           for j, lb in enumerate(s['labels']) if lb)
            dl = ('<c:dLbls>%s<c:spPr><a:noFill/><a:ln><a:noFill/></a:ln></c:spPr><c:showLegendKey val="0"/><c:showVal val="0"/><c:showCatName val="0"/><c:showSerName val="0"/><c:showPercent val="0"/><c:showBubbleSize val="0"/></c:dLbls>' % lbls)
        ser += ('<c:ser><c:idx val="%d"/><c:order val="%d"/><c:tx>%s</c:tx><c:spPr><a:ln w="19050"><a:noFill/></a:ln></c:spPr>'
                '<c:marker><c:symbol val="circle"/><c:size val="8"/><c:spPr><a:solidFill><a:srgbClr val="%s"/></a:solidFill><a:ln w="9525"><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></a:ln></c:spPr></c:marker>%s'
                '<c:xVal>%s</c:xVal><c:yVal>%s</c:yVal><c:smooth val="0"/></c:ser>') % (
            k, k, _strcache('Sheet1!$%s$1' % _col(2 * k + 1), [s['name']]), s['color'], dl,
            _numref('Sheet1!$%s$2:$%s$%d' % (_col(2 * k), _col(2 * k), n + 1), s['xs']), _numref('Sheet1!$%s$2:$%s$%d' % (_col(2 * k + 1), _col(2 * k + 1), n + 1), s['ys']))
    plot = ('<c:scatterChart><c:scatterStyle val="lineMarker"/><c:varyColors val="0"/>%s<c:axId val="70010"/><c:axId val="70020"/></c:scatterChart>' % ser) + \
        _ax_val(70010, 70020, 'b', xmn, xmx, xunit, xfmt, False, xtitle, crosses='at:%s' % ymn, between=False) + \
        _ax_val(70020, 70010, 'l', ymn, ymx, yunit, yfmt, True, ytitle, crosses='at:%s' % xmn, between=False)
    return _wrap(plot, legend)


# ---------- package ----------
THEME = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><a:theme xmlns:a="%s" name="Mousson"><a:themeElements>
<a:clrScheme name="Mousson"><a:dk1><a:srgbClr val="1F2A30"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="123A46"/></a:dk2><a:lt2><a:srgbClr val="EEF4F7"/></a:lt2>
<a:accent1><a:srgbClr val="2F7FC1"/></a:accent1><a:accent2><a:srgbClr val="D9622B"/></a:accent2><a:accent3><a:srgbClr val="8C969B"/></a:accent3><a:accent4><a:srgbClr val="1E9E6A"/></a:accent4><a:accent5><a:srgbClr val="123A46"/></a:accent5><a:accent6><a:srgbClr val="E8A33D"/></a:accent6>
<a:hlink><a:srgbClr val="2F7FC1"/></a:hlink><a:folHlink><a:srgbClr val="5B6770"/></a:folHlink></a:clrScheme>
<a:fontScheme name="Mousson"><a:majorFont><a:latin typeface="Cambria"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme>
<a:fmtScheme name="Mousson"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>
<a:lnStyleLst><a:ln w="6350"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="12700"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="19050"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst>
<a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>
<a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme>
</a:themeElements><a:objectDefaults/><a:extraClrSchemeLst/></a:theme>''' % NS_A

MASTER = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sldMaster xmlns:a="%s" xmlns:r="%s" xmlns:p="%s"><p:cSld><p:bg><p:bgRef idx="1001"><a:schemeClr val="bg1"/></p:bgRef></p:bg><p:spTree>'
          '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>'
          '<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>'
          '<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle><a:lvl1pPr marL="0" algn="l" defTabSz="914400" rtl="0" eaLnBrk="1" latinLnBrk="0" hangingPunct="1"><a:defRPr sz="1800" kern="1200"><a:solidFill><a:schemeClr val="tx1"/></a:solidFill><a:latin typeface="+mn-lt"/><a:ea typeface="+mn-ea"/><a:cs typeface="+mn-cs"/></a:defRPr></a:lvl1pPr></p:titleStyle><p:bodyStyle><a:lvl1pPr marL="0" algn="l" defTabSz="914400" rtl="0" eaLnBrk="1" latinLnBrk="0" hangingPunct="1"><a:defRPr sz="1800" kern="1200"><a:solidFill><a:schemeClr val="tx1"/></a:solidFill><a:latin typeface="+mn-lt"/><a:ea typeface="+mn-ea"/><a:cs typeface="+mn-cs"/></a:defRPr></a:lvl1pPr></p:bodyStyle><p:otherStyle><a:lvl1pPr marL="0" algn="l" defTabSz="914400" rtl="0" eaLnBrk="1" latinLnBrk="0" hangingPunct="1"><a:defRPr sz="1800" kern="1200"><a:solidFill><a:schemeClr val="tx1"/></a:solidFill><a:latin typeface="+mn-lt"/><a:ea typeface="+mn-ea"/><a:cs typeface="+mn-cs"/></a:defRPr></a:lvl1pPr></p:otherStyle></p:txStyles></p:sldMaster>') % (NS_A, NS_R, NS_P)

LAYOUT = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:sldLayout xmlns:a="%s" xmlns:r="%s" xmlns:p="%s" type="blank" preserve="1"><p:cSld name="Vide"><p:spTree>'
          '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>'
          '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>') % (NS_A, NS_R, NS_P)


def rels(items):
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">%s</Relationships>'
            % ''.join('<Relationship Id="%s" Type="%s" Target="%s"/>' % it for it in items))


RT = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/'


def save(slides, path, title='Présentation'):
    z = zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED)
    ct = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>',
          '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>',
          '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>',
          '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>',
          '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>',
          '<Override PartName="/ppt/presProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"/>',
          '<Override PartName="/ppt/viewProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"/>',
          '<Override PartName="/ppt/tableStyles.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml"/>',
          '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
          '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>']
    chart_no = 0
    pres_rels = [('rId1', RT + 'slideMaster', 'slideMasters/slideMaster1.xml')]
    sld_ids = ''
    for n, s in enumerate(slides, 1):
        ct.append('<Override PartName="/ppt/slides/slide%d.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>' % n)
        srels = [('rId1', RT + 'slideLayout', '../slideLayouts/slideLayout1.xml')]
        for k, cx in enumerate(s.charts):
            chart_no += 1
            z.writestr('ppt/charts/chart%d.xml' % chart_no, cx)
            ct.append('<Override PartName="/ppt/charts/chart%d.xml" ContentType="application/vnd.openxmlformats-officedocument.drawingml.chart+xml"/>' % chart_no)
            srels.append(('rId%d' % (k + 2), RT + 'chart', '../charts/chart%d.xml' % chart_no))
        z.writestr('ppt/slides/slide%d.xml' % n, s.xml())
        z.writestr('ppt/slides/_rels/slide%d.xml.rels' % n, rels(srels))
        pres_rels.append(('rId%d' % (n + 1), RT + 'slide', 'slides/slide%d.xml' % n))
        sld_ids += '<p:sldId id="%d" r:id="rId%d"/>' % (255 + n, n + 1)
    k = len(slides) + 2
    pres_rels += [('rId%d' % k, RT + 'theme', 'theme/theme1.xml'), ('rId%d' % (k + 1), RT + 'presProps', 'presProps.xml'),
                  ('rId%d' % (k + 2), RT + 'viewProps', 'viewProps.xml'), ('rId%d' % (k + 3), RT + 'tableStyles', 'tableStyles.xml')]
    ct.append('</Types>')
    z.writestr('[Content_Types].xml', ''.join(ct))
    z.writestr('_rels/.rels', rels([('rId1', RT + 'officeDocument', 'ppt/presentation.xml'),
                                    ('rId2', 'http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties', 'docProps/core.xml'),
                                    ('rId3', RT + 'extended-properties', 'docProps/app.xml')]))
    z.writestr('docProps/core.xml', ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
                                     'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                                     '<dc:title>%s</dc:title><dc:language>fr-FR</dc:language></cp:coreProperties>') % esc(title))
    z.writestr('docProps/app.xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>Microsoft Office PowerPoint</Application><Slides>%d</Slides></Properties>' % len(slides))
    z.writestr('ppt/presentation.xml', ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:presentation xmlns:a="%s" xmlns:r="%s" xmlns:p="%s" saveSubsetFonts="1">'
                                        '<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst><p:sldIdLst>%s</p:sldIdLst>'
                                        '<p:sldSz cx="%d" cy="%d"/><p:notesSz cx="6858000" cy="9144000"/></p:presentation>') % (NS_A, NS_R, NS_P, sld_ids, W, H))
    z.writestr('ppt/_rels/presentation.xml.rels', rels(pres_rels))
    z.writestr('ppt/slideMasters/slideMaster1.xml', MASTER)
    z.writestr('ppt/slideMasters/_rels/slideMaster1.xml.rels', rels([('rId1', RT + 'slideLayout', '../slideLayouts/slideLayout1.xml'), ('rId2', RT + 'theme', '../theme/theme1.xml')]))
    z.writestr('ppt/slideLayouts/slideLayout1.xml', LAYOUT)
    z.writestr('ppt/slideLayouts/_rels/slideLayout1.xml.rels', rels([('rId1', RT + 'slideMaster', '../slideMasters/slideMaster1.xml')]))
    z.writestr('ppt/theme/theme1.xml', THEME)
    z.writestr('ppt/presProps.xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:presentationPr xmlns:a="%s" xmlns:r="%s" xmlns:p="%s"/>' % (NS_A, NS_R, NS_P))
    z.writestr('ppt/viewProps.xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><p:viewPr xmlns:a="%s" xmlns:r="%s" xmlns:p="%s"><p:normalViewPr><p:restoredLeft sz="15620"/><p:restoredTop sz="94660"/></p:normalViewPr><p:gridSpacing cx="76200" cy="76200"/></p:viewPr>' % (NS_A, NS_R, NS_P))
    z.writestr('ppt/tableStyles.xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><a:tblStyleLst xmlns:a="%s" def="{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}"/>' % NS_A)
    z.close()


def combo_bar(cats, series, lines=(), mn=None, mx=None, unit=None, fmt='0', labels=True, label_fmt=None, legend=True, legend_pos='b', gap=40, overlap=-5, skip=None, label_sz=7):
    """bars (each series can carry point_colors) + optional constant/reference lines on the same axes"""
    ser = ''
    k = 0
    for s_ in series:
        dpts = ''.join('<c:dPt><c:idx val="%d"/><c:invertIfNegative val="0"/><c:bubble3D val="0"/><c:spPr><a:solidFill><a:srgbClr val="%s"/></a:solidFill></c:spPr></c:dPt>' % (j, pc)
                       for j, pc in enumerate(s_.get('point_colors') or []) if pc)
        ser += ('<c:ser><c:idx val="%d"/><c:order val="%d"/><c:tx>%s</c:tx><c:spPr><a:solidFill><a:srgbClr val="%s"/></a:solidFill></c:spPr><c:invertIfNegative val="0"/>%s%s'
                '<c:cat>%s</c:cat><c:val>%s</c:val></c:ser>') % (
            k, k, _strcache('Sheet1!$%s$1' % _col(k + 1), [s_['name']]), s_['color'], dpts, _dlbls('outEnd', label_sz, '1F2A30', label_fmt or fmt) if labels else '',
            _strcache('Sheet1!$A$2:$A$%d' % (len(cats) + 1), cats), _numref('Sheet1!$%s$2:$%s$%d' % (_col(k + 1), _col(k + 1), len(cats) + 1), s_['values']))
        k += 1
    plot = '<c:barChart><c:barDir val="col"/><c:grouping val="clustered"/><c:varyColors val="0"/>%s<c:gapWidth val="%d"/><c:overlap val="%d"/><c:axId val="50010"/><c:axId val="50020"/></c:barChart>' % (ser, gap, overlap)
    if lines:
        lser = ''
        for l in lines:
            dash = '<a:prstDash val="%s"/>' % l.get('dash', 'dash') if l.get('dash', 'dash') else ''
            lser += ('<c:ser><c:idx val="%d"/><c:order val="%d"/><c:tx>%s</c:tx><c:spPr><a:ln w="%d" cap="rnd"><a:solidFill><a:srgbClr val="%s"/></a:solidFill>%s<a:round/></a:ln></c:spPr><c:marker><c:symbol val="none"/></c:marker>'
                     '<c:cat>%s</c:cat><c:val>%s</c:val><c:smooth val="0"/></c:ser>') % (
                k, k, _strcache('Sheet1!$%s$1' % _col(k + 1), [l['name']]), int(l.get('width', 1.5) * 12700), l['color'], dash,
                _strcache('Sheet1!$A$2:$A$%d' % (len(cats) + 1), cats), _numref('Sheet1!$%s$2:$%s$%d' % (_col(k + 1), _col(k + 1), len(cats) + 1), l['values']))
            k += 1
        plot += '<c:lineChart><c:grouping val="standard"/><c:varyColors val="0"/>%s<c:marker val="1"/><c:axId val="50010"/><c:axId val="50020"/></c:lineChart>' % lser
    plot += _ax_cat(50010, 50020, skip) + _ax_val(50020, 50010, 'l', mn, mx, unit, fmt, True, None)
    return _wrap(plot, legend, legend_pos)


def multi_line(cats, series, mn=None, mx=None, unit=None, fmt='0', skip=None, legend=True, legend_pos='b', legend_sz=7):
    ser = ''
    for k, s_ in enumerate(series):
        dash = '<a:prstDash val="%s"/>' % s_['dash'] if s_.get('dash') else ''
        ser += ('<c:ser><c:idx val="%d"/><c:order val="%d"/><c:tx>%s</c:tx><c:spPr><a:ln w="%d" cap="rnd"><a:solidFill><a:srgbClr val="%s"/></a:solidFill>%s<a:round/></a:ln></c:spPr><c:marker><c:symbol val="none"/></c:marker>'
                '<c:cat>%s</c:cat><c:val>%s</c:val><c:smooth val="0"/></c:ser>') % (
            k, k, _strcache('Sheet1!$%s$1' % _col(k + 1), [s_['name']]), int(s_.get('width', 1.25) * 12700), s_['color'], dash,
            _strcache('Sheet1!$A$2:$A$%d' % (len(cats) + 1), cats), _numref('Sheet1!$%s$2:$%s$%d' % (_col(k + 1), _col(k + 1), len(cats) + 1), s_['values']))
    plot = ('<c:lineChart><c:grouping val="standard"/><c:varyColors val="0"/>%s<c:marker val="1"/><c:axId val="60010"/><c:axId val="60020"/></c:lineChart>' % ser) + \
        _ax_cat(60010, 60020, skip) + _ax_val(60020, 60010, 'l', mn, mx, unit, fmt, True, None)
    return _wrap(plot, legend, legend_pos, legend_sz)
