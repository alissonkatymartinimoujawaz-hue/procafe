"""Minimal XLSX writer (standard library only): inline strings, numbers, dates, formulas with cached values,
styles (font, fill, number format, alignment, border), column widths, frozen panes, merged cells."""
import zipfile, datetime
from xml.sax.saxutils import escape


def esc(t):
    return escape(str(t), {'"': '&quot;'})


def col_letter(c):  # 1-based
    s = ''
    while c:
        c, r = divmod(c - 1, 26)
        s = chr(65 + r) + s
    return s


def ref(r, c, abs_=False):
    return ('$%s$%d' if abs_ else '%s%d') % (col_letter(c), r)


EPOCH = datetime.date(1899, 12, 30)


def serial(d):
    return (d - EPOCH).days


class Style:
    def __init__(self, bold=False, color='000000', size=10, fill=None, fmt=None, halign=None, wrap=False, italic=False, border=False):
        self.key = (bold, color, size, fill, fmt, halign, wrap, italic, border)


class Workbook:
    def __init__(self, font='Arial'):
        self.font = font
        self.sheets = []
        self.styles = [Style().key]
        self.fmts = {}

    def style_id(self, st):
        if st is None:
            return 0
        k = st.key if isinstance(st, Style) else st
        if k not in self.styles:
            self.styles.append(k)
        return self.styles.index(k)

    def add(self, name):
        s = Sheet(self, name)
        self.sheets.append(s)
        return s

    def _styles_xml(self):
        fonts, fills, numfmts, xfs = [], ['<fill><patternFill patternType="none"/></fill>', '<fill><patternFill patternType="gray125"/></fill>'], [], []
        fmt_ids = {}
        for (bold, color, size, fill, fmt, halign, wrap, italic, border) in self.styles:
            f = '<font>%s%s<sz val="%s"/><color rgb="FF%s"/><name val="%s"/></font>' % ('<b/>' if bold else '', '<i/>' if italic else '', size, color, self.font)
            if f not in fonts:
                fonts.append(f)
            fi = 0
            if fill:
                fx = '<fill><patternFill patternType="solid"><fgColor rgb="FF%s"/><bgColor indexed="64"/></patternFill></fill>' % fill
                if fx not in fills:
                    fills.append(fx)
                fi = fills.index(fx)
            nid = 0
            if fmt:
                if fmt not in fmt_ids:
                    fmt_ids[fmt] = 164 + len(fmt_ids)
                    numfmts.append('<numFmt numFmtId="%d" formatCode="%s"/>' % (fmt_ids[fmt], esc(fmt)))
                nid = fmt_ids[fmt]
            al = ''
            if halign or wrap:
                al = '<alignment%s%s vertical="top"/>' % (' horizontal="%s"' % halign if halign else '', ' wrapText="1"' if wrap else '')
            xfs.append('<xf numFmtId="%d" fontId="%d" fillId="%d" borderId="%d" xfId="0"%s%s%s%s>%s</xf>' % (
                nid, fonts.index(f), fi, 1 if border else 0, ' applyNumberFormat="1"' if nid else '', ' applyFont="1"', ' applyFill="1"' if fi else '',
                ' applyAlignment="1"' if al else '', al))
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                '%s<fonts count="%d">%s</fonts><fills count="%d">%s</fills>'
                '<borders count="2"><border><left/><right/><top/><bottom/><diagonal/></border>'
                '<border><left/><right/><top/><bottom style="thin"><color rgb="FFBFBFBF"/></bottom><diagonal/></border></borders>'
                '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="%d">%s</cellXfs>'
                '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>') % (
            ('<numFmts count="%d">%s</numFmts>' % (len(numfmts), ''.join(numfmts))) if numfmts else '', len(fonts), ''.join(fonts), len(fills), ''.join(fills), len(xfs), ''.join(xfs))

    def save(self, path):
        z = zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED)
        n = len(self.sheets)
        z.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
                   '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                   '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
                   + ''.join('<Override PartName="/xl/worksheets/sheet%d.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' % (i + 1) for i in range(n))
                   + '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
                   '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/></Types>')
        z.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
                   '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
                   '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/></Relationships>')
        z.writestr('docProps/core.xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
                   'xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>Sumatra weather by ENSO season</dc:title></cp:coreProperties>')
        z.writestr('docProps/app.xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>Microsoft Excel</Application></Properties>')
        z.writestr('xl/workbook.xml', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                   'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><bookViews><workbookView activeTab="0"/></bookViews><sheets>'
                   + ''.join('<sheet name="%s" sheetId="%d" r:id="rId%d"/>' % (esc(s.name), i + 1, i + 1) for i, s in enumerate(self.sheets))
                   + '</sheets><calcPr calcId="191029" fullCalcOnLoad="1"/></workbook>')
        z.writestr('xl/_rels/workbook.xml.rels', '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   + ''.join('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet%d.xml"/>' % (i + 1, i + 1) for i in range(n))
                   + '<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>' % (n + 1))
        for i, s in enumerate(self.sheets):
            z.writestr('xl/worksheets/sheet%d.xml' % (i + 1), s.xml())
        z.writestr('xl/styles.xml', self._styles_xml())
        z.close()


class Sheet:
    def __init__(self, wb, name):
        self.wb, self.name = wb, name
        self.cells = {}
        self.widths = {}
        self.freeze = None
        self.merges = []

    def set(self, r, c, value=None, style=None, formula=None):
        """value: number, str, date, None. formula: Excel formula without '=' (value = cached result)."""
        self.cells[(r, c)] = (value, formula, self.wb.style_id(style))

    def row(self, r, c0, values, style=None):
        for k, v in enumerate(values):
            self.set(r, c0 + k, v, style)

    def xml(self):
        rows = {}
        for (r, c), v in self.cells.items():
            rows.setdefault(r, []).append((c, v))
        out = []
        for r in sorted(rows):
            cs = []
            for c, (val, f, sid) in sorted(rows[r]):
                a = ref(r, c)
                s = ' s="%d"' % sid if sid else ''
                if isinstance(val, datetime.date):
                    val = serial(val)
                if f is not None:
                    if isinstance(val, str):
                        cs.append('<c r="%s"%s t="str"><f>%s</f><v>%s</v></c>' % (a, s, esc(f), esc(val)))
                    elif val is None:
                        cs.append('<c r="%s"%s t="str"><f>%s</f><v></v></c>' % (a, s, esc(f)))
                    elif isinstance(val, bool):
                        cs.append('<c r="%s"%s t="b"><f>%s</f><v>%d</v></c>' % (a, s, esc(f), 1 if val else 0))
                    else:
                        cs.append('<c r="%s"%s><f>%s</f><v>%s</v></c>' % (a, s, esc(f), repr(float(val)) if isinstance(val, float) else val))
                elif val is None:
                    cs.append('<c r="%s"%s/>' % (a, s))
                elif isinstance(val, str):
                    cs.append('<c r="%s"%s t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>' % (a, s, esc(val)))
                else:
                    cs.append('<c r="%s"%s><v>%s</v></c>' % (a, s, repr(float(val)) if isinstance(val, float) else val))
            out.append('<row r="%d">%s</row>' % (r, ''.join(cs)))
        cols = ''
        if self.widths:
            cols = '<cols>%s</cols>' % ''.join('<col min="%d" max="%d" width="%s" customWidth="1"/>' % (c, c, w) for c, w in sorted(self.widths.items()))
        pane = ''
        if self.freeze:
            fr, fc = self.freeze
            pane = ('<sheetViews><sheetView workbookViewId="0"><pane%s%s topLeftCell="%s" activePane="bottomRight" state="frozen"/></sheetView></sheetViews>' % (
                ' xSplit="%d"' % (fc - 1) if fc > 1 else '', ' ySplit="%d"' % (fr - 1) if fr > 1 else '', ref(fr, fc)))
            if fc == 1:
                pane = pane.replace('activePane="bottomRight"', 'activePane="bottomLeft"')
            elif fr == 1:
                pane = pane.replace('activePane="bottomRight"', 'activePane="topRight"')
        mg = ''
        if self.merges:
            mg = '<mergeCells count="%d">%s</mergeCells>' % (len(self.merges), ''.join('<mergeCell ref="%s"/>' % m for m in self.merges))
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">%s<sheetFormatPr defaultRowHeight="13.2"/>%s<sheetData>%s</sheetData>%s</worksheet>') % (
            pane, cols, ''.join(out), mg)
