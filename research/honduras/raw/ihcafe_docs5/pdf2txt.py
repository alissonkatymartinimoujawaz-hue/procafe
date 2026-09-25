"""Minimal PDF -> text extractor, standard library only (pypdf could not be installed: PyPI blocked).

Handles: FlateDecode streams, object streams (PDF 1.5), page tree order, fonts with /ToUnicode CMaps
(1- and 2-byte codes), simple fonts without CMaps (read as cp1252), Tj / TJ / ' / " operators, and line
breaks from Td / TD / Tm / T*. Scanned (image-only) pages yield no text.
Usage: python3 pdf2txt.py file.pdf [...]   -> writes file.txt next to each PDF.
"""
import re, sys, zlib

WS = b' \t\r\n\f\x00'
DELIM = b'()<>[]{}/%'


class Ref:
    def __init__(self, n): self.n = n
    def __repr__(self): return 'R%d' % self.n


class Name(str):
    pass


class Op(str):
    pass


def tokens(data, i=0):
    n = len(data)
    while i < n:
        c = data[i:i + 1]
        if c in (b' ', b'\t', b'\r', b'\n', b'\f', b'\x00'):
            i += 1
        elif c == b'%':
            while i < n and data[i:i + 1] not in (b'\r', b'\n'):
                i += 1
        elif c == b'(':
            depth, j, out = 1, i + 1, bytearray()
            while j < n and depth:
                ch = data[j]
                if ch == 0x5C:  # backslash
                    j += 1
                    e = data[j:j + 1]
                    m = {b'n': b'\n', b'r': b'\r', b't': b'\t', b'b': b'\b', b'f': b'\f'}.get(e)
                    if m is not None:
                        out += m; j += 1
                    elif e in (b'\r', b'\n'):
                        j += 1
                        if e == b'\r' and data[j:j + 1] == b'\n':
                            j += 1
                    elif e.isdigit():
                        k = j
                        while k < j + 3 and data[k:k + 1].isdigit() and data[k:k + 1] < b'8':
                            k += 1
                        out.append(int(data[j:k], 8) & 255); j = k
                    else:
                        out += e; j += 1
                    continue
                if ch == 0x28:
                    depth += 1
                elif ch == 0x29:
                    depth -= 1
                    if not depth:
                        break
                out.append(ch); j += 1
            yield bytes(out); i = j + 1
        elif c == b'<':
            if data[i + 1:i + 2] == b'<':
                yield Op('<<'); i += 2
            else:
                j = data.find(b'>', i)
                h = re.sub(rb'[^0-9A-Fa-f]', b'', data[i + 1:j])
                if len(h) % 2:
                    h += b'0'
                yield bytes.fromhex(h.decode()); i = j + 1
        elif c == b'>':
            yield Op('>>'); i += 2
        elif c in (b'[', b']', b'{', b'}'):
            yield Op(c.decode()); i += 1
        elif c == b'/':
            j = i + 1
            while j < n and data[j:j + 1] not in WS and data[j:j + 1] not in DELIM:
                j += 1
            nm = re.sub(rb'#([0-9A-Fa-f]{2})', lambda m: bytes([int(m.group(1), 16)]), data[i + 1:j])
            yield Name(nm.decode('latin-1')); i = j
        else:
            j = i
            while j < n and data[j:j + 1] not in WS and data[j:j + 1] not in DELIM:
                j += 1
            if j == i:
                j += 1
            w = data[i:j]
            try:
                yield float(w) if (b'.' in w) else int(w)
            except ValueError:
                yield Op(w.decode('latin-1'))
            i = j


def parse_obj(it, first=None):
    t = next(it) if first is None else first
    if isinstance(t, Op) and t in ('<<', '['):
        end = '>>' if t == '<<' else ']'
        items = []
        for x in it:
            if isinstance(x, Op) and x == end:
                break
            if isinstance(x, Op) and x in ('<<', '['):
                items.append(parse_obj(it, x))
            elif isinstance(x, Op) and x == 'R' and len(items) >= 2 and type(items[-1]) is int and type(items[-2]) is int:
                items.pop(); items[-1] = Ref(items[-1])
            else:
                items.append(x)
        if end == ']':
            return items
        return {items[k]: items[k + 1] for k in range(0, len(items) - 1, 2)}
    return t


class PDF:
    def __init__(self, data):
        self.data, self.objs = data, {}
        for m in re.finditer(rb'(?<![0-9])(\d+)\s+(\d+)\s+obj\b', data):
            self.objs[int(m.group(1))] = ('raw', m.end())
        for n, (_, _) in list(self.objs.items()):
            try:
                o = self.get(n)
            except Exception:
                continue
            if isinstance(o, tuple) and o[0].get('Type') == 'ObjStm':
                try:
                    self.load_objstm(o)
                except Exception:
                    pass

    def load_objstm(self, o):
        d, raw = o
        s = decode(d, raw, self)
        first, cnt = self.r(d['First']), self.r(d['N'])
        hdr = [int(x) for x in s[:first].split()[:2 * cnt]]
        for k in range(cnt):
            num, off = hdr[2 * k], hdr[2 * k + 1]
            if num not in self.objs or self.objs[num][0] == 'raw' and False:
                pass
            if num not in self.objs:
                try:
                    self.objs[num] = ('val', parse_obj(tokens(s, first + off)))
                except Exception:
                    pass

    def get(self, n):
        kind, v = self.objs.get(n, ('val', None))
        if kind == 'val':
            return v
        it = tokens(self.data, v)
        o = parse_obj(it)
        if isinstance(o, dict):
            m = re.compile(rb'\s*stream\r?\n').match(self.data, self.after_dict(v))
            if m:
                start = m.end()
                ln = o.get('Length')
                ln = self.r(ln) if ln is not None else None
                if not isinstance(ln, int) or self.data[start + ln:start + ln + 20].find(b'endstream') < 0:
                    ln = self.data.find(b'endstream', start) - start
                o = (o, self.data[start:start + ln])
        self.objs[n] = ('val', o)
        return o

    def after_dict(self, pos):
        i = self.data.find(b'<<', pos)
        depth = 0
        while i < len(self.data):
            if self.data.startswith(b'<<', i):
                depth += 1; i += 2
            elif self.data.startswith(b'>>', i):
                depth -= 1; i += 2
                if not depth:
                    return i
            elif self.data[i:i + 1] == b'(':
                j, d2 = i + 1, 1
                while d2 and j < len(self.data):
                    if self.data[j] == 0x5C:
                        j += 2; continue
                    d2 += {0x28: 1, 0x29: -1}.get(self.data[j], 0); j += 1
                i = j
            else:
                i += 1
        return i

    def r(self, x):
        seen = 0
        while isinstance(x, Ref) and seen < 20:
            x = self.get(x.n); seen += 1
        return x


def decode(d, raw, pdf):
    f = pdf.r(d.get('Filter'))
    fl = f if isinstance(f, list) else ([f] if f else [])
    for x in fl:
        x = pdf.r(x)
        if x in ('FlateDecode', 'Fl'):
            try:
                raw = zlib.decompress(raw)
            except zlib.error:
                raw = zlib.decompressobj().decompress(raw)
        elif x in ('ASCIIHexDecode', 'AHx'):
            raw = bytes.fromhex(re.sub(rb'[^0-9A-Fa-f]', b'', raw.split(b'>')[0]).decode())
        elif x in ('ASCII85Decode', 'A85'):
            import base64
            raw = base64.a85decode(raw.strip().split(b'~>')[0] + b'~>', adobe=True)
        else:
            return b''  # images etc.
    return raw


def parse_cmap(s):
    m, nb = {}, 1
    cs = re.search(rb'begincodespacerange\s*<([0-9A-Fa-f]+)>', s)
    if cs:
        nb = len(cs.group(1)) // 2
    uni = lambda h: bytes.fromhex(h.decode()).decode('utf-16-be', 'replace')
    for blk in re.findall(rb'beginbfchar(.*?)endbfchar', s, re.S):
        for a, b in re.findall(rb'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]*)>', blk):
            m[int(a, 16)] = uni(b)
    for blk in re.findall(rb'beginbfrange(.*?)endbfrange', s, re.S):
        for a, b, rest in re.findall(rb'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*(<[0-9A-Fa-f]*>|\[[^\]]*\])', blk):
            lo, hi = int(a, 16), int(b, 16)
            if rest.startswith(b'['):
                for k, h in enumerate(re.findall(rb'<([0-9A-Fa-f]*)>', rest)):
                    m[lo + k] = uni(h)
            else:
                h = rest[1:-1]
                base = bytes.fromhex(h.decode())
                for k in range(min(hi - lo + 1, 65536)):
                    v = int.from_bytes(base, 'big') + k
                    m[lo + k] = v.to_bytes(len(base), 'big').decode('utf-16-be', 'replace')
    return m, nb


class Font:
    def __init__(self, pdf, fd):
        fd = pdf.r(fd) or {}
        self.two = fd.get('Subtype') == 'Type0'
        self.map = None
        tu = fd.get('ToUnicode')
        if isinstance(tu, Ref):
            o = pdf.r(tu)
            if isinstance(o, tuple):
                try:
                    self.map, nb = parse_cmap(decode(o[0], o[1], pdf))
                    self.two = nb == 2 or (self.two and nb != 1)
                except Exception:
                    self.map = None
        self.diff = {}
        enc = pdf.r(fd.get('Encoding'))
        if isinstance(enc, dict) and isinstance(enc.get('Differences'), list):
            code = 0
            for x in enc['Differences']:
                if isinstance(x, int):
                    code = x
                else:
                    self.diff[code] = GLYPHS.get(str(x), None); code += 1

    def text(self, b):
        if self.two:
            codes = [int.from_bytes(b[k:k + 2], 'big') for k in range(0, len(b) - 1, 2)]
        else:
            codes = list(b)
        out = []
        for c in codes:
            if self.map is not None and c in self.map:
                out.append(self.map[c])
            elif not self.two and self.diff.get(c):
                out.append(self.diff[c])
            elif not self.two:
                out.append(bytes([c]).decode('cp1252', 'replace'))
        return ''.join(out)


GLYPHS = {'space': ' ', 'aacute': 'á', 'eacute': 'é', 'iacute': 'í', 'oacute': 'ó', 'uacute': 'ú', 'ntilde': 'ñ',
          'Aacute': 'Á', 'Eacute': 'É', 'Iacute': 'Í', 'Oacute': 'Ó', 'Uacute': 'Ú', 'Ntilde': 'Ñ', 'udieresis': 'ü',
          'hyphen': '-', 'period': '.', 'comma': ',', 'colon': ':', 'percent': '%', 'quoteright': '’', 'bullet': '•',
          'endash': '–', 'emdash': '—', 'quotedblleft': '“', 'quotedblright': '”', 'degree': '°', 'ordfeminine': 'ª',
          'ordmasculine': 'º', 'questiondown': '¿', 'exclamdown': '¡', 'slash': '/', 'parenleft': '(', 'parenright': ')'}


def pages(pdf):
    root = None
    for m in re.finditer(rb'/Root\s+(\d+)\s+\d+\s+R', pdf.data):
        root = int(m.group(1))
    out = []

    def walk(node, inh, depth=0):
        node = pdf.r(node)
        if isinstance(node, tuple):
            node = node[0]
        if not isinstance(node, dict) or depth > 50:
            return
        inh = dict(inh)
        if 'Resources' in node:
            inh['Resources'] = node['Resources']
        if node.get('Type') == 'Pages' or 'Kids' in node:
            for k in pdf.r(node.get('Kids')) or []:
                walk(k, inh, depth + 1)
        else:
            out.append((node, inh.get('Resources')))

    cat = pdf.r(Ref(root)) if root is not None else None
    if isinstance(cat, dict):
        walk(cat.get('Pages'), {})
    if not out:  # fallback: every /Type /Page object in file order
        for n in sorted(pdf.objs):
            try:
                o = pdf.get(n)
            except Exception:
                continue
            if isinstance(o, dict) and o.get('Type') == 'Page':
                out.append((o, o.get('Resources')))
    return out


def page_text(pdf, page, res, depth=0):
    res = pdf.r(res) or {}
    fonts = {k: Font(pdf, v) for k, v in (pdf.r(res.get('Font')) or {}).items()}
    xobj = pdf.r(res.get('XObject')) or {}
    cont = pdf.r(page.get('Contents')) if isinstance(page, dict) else None
    parts = []
    if isinstance(cont, tuple):
        parts = [decode(cont[0], cont[1], pdf)]
    elif isinstance(cont, list):
        for c in cont:
            c = pdf.r(c)
            if isinstance(c, tuple):
                parts.append(decode(c[0], c[1], pdf))
    return run(pdf, b'\n'.join(parts), fonts, xobj, depth)


def run(pdf, data, fonts, xobj, depth):
    out, stack, font, last_y = [], [], None, None
    it = tokens(data)
    for t in it:
        if isinstance(t, Op) and t not in ('[', ']', '<<', '>>'):
            if t == 'Tf' and len(stack) >= 2:
                font = fonts.get(stack[-2])
            elif t == 'Tj' and stack and font:
                out.append(font.text(stack[-1]) if isinstance(stack[-1], bytes) else '')
            elif t in ("'", '"') and stack and font:
                out.append('\n' + (font.text(stack[-1]) if isinstance(stack[-1], bytes) else ''))
            elif t == 'TJ' and stack and isinstance(stack[-1], list) and font:
                s = ''
                for x in stack[-1]:
                    if isinstance(x, bytes):
                        s += font.text(x)
                    elif isinstance(x, (int, float)) and x < -180:
                        s += ' '
                out.append(s)
            elif t in ('Td', 'TD') and len(stack) >= 2:
                dy = stack[-1]
                if isinstance(dy, (int, float)) and abs(dy) > 0.5:
                    out.append('\n')
                elif isinstance(stack[-2], (int, float)) and stack[-2] > 0:
                    out.append(' ')
            elif t == 'Tm' and len(stack) >= 6:
                y = stack[-1]
                out.append('\n' if last_y is None or abs(y - last_y) > 0.5 else ' ')
                last_y = y
            elif t == 'T*':
                out.append('\n')
            elif t == 'ET':
                out.append(' ')
            elif t == 'Do' and stack and depth < 3:
                xo = pdf.r(xobj.get(stack[-1]))
                if isinstance(xo, tuple) and xo[0].get('Subtype') == 'Form':
                    r2 = pdf.r(xo[0].get('Resources')) or {}
                    f2 = dict(fonts); f2.update({k: Font(pdf, v) for k, v in (pdf.r(r2.get('Font')) or {}).items()})
                    out.append(run(pdf, decode(xo[0], xo[1], pdf), f2, pdf.r(r2.get('XObject')) or {}, depth + 1))
            elif t == 'BI':
                j = data.find(b'EI', 0)
            stack = []
        elif t == '[':
            arr = []
            for x in it:
                if x == ']':
                    break
                arr.append(x)
            stack.append(arr)
        else:
            stack.append(t)
    txt = ''.join(out)
    txt = re.sub(r'[ \t]+', ' ', txt)
    return re.sub(r' *\n[ \n]*', '\n', txt).strip()


def extract(path):
    pdf = PDF(open(path, 'rb').read())
    res = []
    for k, (pg, rs) in enumerate(pages(pdf), 1):
        try:
            t = page_text(pdf, pg, rs)
        except Exception as e:
            t = '[page %d: extraction error %s]' % (k, e)
        res.append('=== page %d ===\n%s' % (k, t))
    return '\n\n'.join(res)


if __name__ == '__main__':
    for p in sys.argv[1:]:
        t = extract(p)
        open(re.sub(r'\.pdf$', '', p) + '.txt', 'w', encoding='utf-8').write(t + '\n')
        print(len(t), p)
