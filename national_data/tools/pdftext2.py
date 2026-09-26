# -*- coding: utf-8 -*-
"""Minimal PDF text extractor (stdlib only) with per-font ToUnicode decoding and line layout.

Variant of pdftext.py: adds Form XObject (Do) recursion, multi-char bfrange fix and Standard-security (RC4/AESV2, empty user password) decryption via ctypes libcrypto. Good enough for BPS publications.
of (x, text) chunks sorted left to right. `python3 pdftext.py file.pdf` prints tab-joined lines.
"""
import re, sys, zlib

OBJ_RE = re.compile(rb"(\d+)\s+(\d+)\s+obj\b(.*?)\bendobj", re.S)


import hashlib
PAD = bytes.fromhex("28BF4E5E4E758A4164004E56FFFA01082E2E00B6D0683E802F0CA9FE6453697A")
DEC = {"key": None, "aes": True}


def setup_crypt(data):
    m = re.search(rb"/Encrypt\s+(\d+)\s+0\s+R", data)
    if not m:
        return
    em = re.search(rb"\n" + m.group(1) + rb"\s+0\s+obj(.*?)endobj", data, re.S).group(1)
    O = _unescape(re.search(rb"/O\s*\((.*?)\)/U", em, re.S).group(1)) if b"/O(" in em or b"/O (" in em else bytes.fromhex(re.search(rb"/O\s*<([0-9A-Fa-f]+)>", em).group(1).decode())
    P = int(re.search(rb"/P\s+(-?\d+)", em).group(1))
    R = int(re.search(rb"/R\s+(\d+)", em).group(1))
    L = int(re.search(rb"/Length\s+(\d+)", em).group(1)) // 8 if re.search(rb"/Length\s+(\d+)", em) else 5
    ID0 = bytes.fromhex(re.search(rb"/ID\s*\[\s*<([0-9A-Fa-f]+)>", data).group(1).decode())
    h = hashlib.md5(PAD + O[:32] + (P & 0xffffffff).to_bytes(4, "little") + ID0)
    if R >= 4 and b"/EncryptMetadata false" in em:
        h.update(b"\xff\xff\xff\xff")
    k = h.digest()
    if R >= 3:
        for _ in range(50):
            k = hashlib.md5(k[:L]).digest()
    DEC["key"] = k[:L]
    DEC["aes"] = b"AESV2" in em


def decrypt(raw, num, gen=0):
    if DEC["key"] is None:
        return raw
    k = DEC["key"] + num.to_bytes(3, "little") + gen.to_bytes(2, "little") + (b"sAlT" if DEC["aes"] else b"")
    ok = hashlib.md5(k).digest()[:min(len(DEC["key"]) + 5, 16)]
    if DEC["aes"]:
        if len(raw) < 32:
            return b""
        raw = raw[:len(raw) - (len(raw) - 16) % 16]
        out = _aes_cbc(ok, raw[:16], raw[16:])
        return out[:-out[-1]] if out and out[-1] <= 16 else out
    S = list(range(256)); j = 0
    for i in range(256):
        j = (j + S[i] + ok[i % len(ok)]) % 256; S[i], S[j] = S[j], S[i]
    out, i, j = bytearray(), 0, 0
    for c in raw:
        i = (i + 1) % 256; j = (j + S[i]) % 256; S[i], S[j] = S[j], S[i]
        out.append(c ^ S[(S[i] + S[j]) % 256])
    return bytes(out)


_LC = None


def _aes_cbc(key, iv, data):
    global _LC
    import ctypes, ctypes.util
    if _LC is None:
        _LC = ctypes.CDLL(ctypes.util.find_library("crypto"))
        _LC.EVP_CIPHER_CTX_new.restype = ctypes.c_void_p
        _LC.EVP_aes_128_cbc.restype = ctypes.c_void_p
        _LC.EVP_DecryptInit_ex.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
        _LC.EVP_CIPHER_CTX_set_padding.argtypes = [ctypes.c_void_p, ctypes.c_int]
        _LC.EVP_DecryptUpdate.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int), ctypes.c_char_p, ctypes.c_int]
        _LC.EVP_CIPHER_CTX_free.argtypes = [ctypes.c_void_p]
    ctx = _LC.EVP_CIPHER_CTX_new()
    _LC.EVP_DecryptInit_ex(ctx, _LC.EVP_aes_128_cbc(), None, key, iv)
    _LC.EVP_CIPHER_CTX_set_padding(ctx, 0)
    buf = ctypes.create_string_buffer(len(data) + 32); n = ctypes.c_int(0)
    _LC.EVP_DecryptUpdate(ctx, buf, ctypes.byref(n), data, len(data))
    _LC.EVP_CIPHER_CTX_free(ctx)
    return buf.raw[:n.value]


def _stream(body, num=0):
    m = re.search(rb"stream\r?\n", body)
    if not m:
        return None
    raw = body[m.end():]
    end = raw.rfind(b"endstream")
    raw = raw[:end] if end >= 0 else raw
    lm = re.search(rb"/Length\s+(\d+)(?!\s+\d+\s+R)", body[:m.start()])
    if lm and int(lm.group(1)) <= len(raw):
        raw = raw[:int(lm.group(1))]
    if b"/XRef" not in body[:m.start()]:
        raw = decrypt(raw, num)
    head = body[:m.start()]
    if b"FlateDecode" in head:
        try:
            return zlib.decompress(raw)
        except zlib.error:
            try:
                return zlib.decompressobj().decompress(raw)
            except zlib.error:
                return b""
    return raw


class PDF:
    def __init__(self, data):
        self.objs, self.streams = {}, {}
        DEC["key"] = None
        setup_crypt(data)
        for m in OBJ_RE.finditer(data):
            n, body = int(m.group(1)), m.group(3)
            self.objs[n] = body
            s = _stream(body, n)
            if s is not None:
                self.streams[n] = s
        # objects stored inside object streams (PDF 1.5+)
        for n, body in list(self.objs.items()):
            if b"/ObjStm" in body[:300] and n in self.streams:
                s = self.streams[n]
                first = int(re.search(rb"/First\s+(\d+)", body).group(1))
                hdr = s[:first].split()
                offs = [(int(hdr[i]), int(hdr[i + 1])) for i in range(0, len(hdr) - 1, 2)]
                for k, (on, off) in enumerate(offs):
                    end = offs[k + 1][1] if k + 1 < len(offs) else len(s) - first
                    self.objs.setdefault(on, s[first + off:first + end])
        self.cmaps = {}

    def ref(self, body, key):
        m = re.search(rb"/" + key + rb"\s+(\d+)\s+0\s+R", body)
        return int(m.group(1)) if m else None

    def dict_inline_or_ref(self, body, key):
        """Return the bytes of a sub-dictionary given inline (<<...>>) or by reference."""
        r = self.ref(body, key)
        if r is not None:
            return self.objs.get(r, b"")
        i = body.find(b"/" + key)
        if i < 0:
            return b""
        j = body.find(b"<<", i)
        depth, k = 0, j
        while k < len(body):
            if body[k:k + 2] == b"<<":
                depth += 1; k += 2; continue
            if body[k:k + 2] == b">>":
                depth -= 1; k += 2
                if depth == 0:
                    return body[j:k]
                continue
            k += 1
        return body[j:]

    def pages(self):
        root = self.ref(self.objs[min(n for n, b in self.objs.items() if b"/Catalog" in b)], b"Pages")
        out = []

        def walk(n, inherited):
            body = self.objs[n]
            res = self.dict_inline_or_ref(body, b"Resources") if b"/Resources" in body else inherited
            if re.search(rb"/Type\s*/Pages\b", body):
                kids = re.search(rb"/Kids\s*\[(.*?)\]", body, re.S).group(1)
                for k in re.findall(rb"(\d+)\s+0\s+R", kids):
                    walk(int(k), res)
            else:
                out.append((n, res))
        walk(root, b"")
        return out

    def cmap(self, font_obj):
        if font_obj in self.cmaps:
            return self.cmaps[font_obj]
        body = self.objs.get(font_obj, b"")
        mp, two_byte = {}, b"/Type0" in body
        tu = self.ref(body, b"ToUnicode")
        if tu is not None and tu in self.streams:
            st = self.streams[tu]
            for blk in re.findall(rb"beginbfchar(.*?)endbfchar", st, re.S):
                for a, b in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", blk):
                    mp[int(a, 16)] = bytes.fromhex(b.decode()).decode("utf-16-be", "ignore")
            for blk in re.findall(rb"beginbfrange(.*?)endbfrange", st, re.S):
                for a, b, c in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", blk):
                    lo, hi, base = int(a, 16), int(b, 16), int(c, 16)
                    for i in range(hi - lo + 1):
                        mp[lo + i] = bytes.fromhex(c.decode()).decode('utf-16-be','ignore')[:-1] + chr(ord(bytes.fromhex(c.decode()).decode('utf-16-be','ignore')[-1:] or ' ') + i) if len(c)>4 else chr(base + i)
        self.cmaps[font_obj] = (mp, two_byte)
        return self.cmaps[font_obj]


def _unescape(lit):
    out, i = bytearray(), 0
    while i < len(lit):
        ch = lit[i]
        if ch == 0x5C and i + 1 < len(lit):
            n = lit[i + 1]
            esc = {ord("n"): 10, ord("r"): 13, ord("t"): 9, ord("b"): 8, ord("f"): 12}
            if n in esc:
                out.append(esc[n]); i += 2
            elif 0x30 <= n <= 0x37:
                m = re.match(rb"[0-7]{1,3}", lit[i + 1:i + 4])
                out.append(int(m.group(0), 8) & 0xFF); i += 1 + len(m.group(0))
            elif n in (10, 13):
                i += 2
            else:
                out.append(n); i += 2
        else:
            out.append(ch); i += 1
    return bytes(out)


TOK = re.compile(rb"\((?:\\.|[^\\)])*\)|<[0-9A-Fa-f\s]*>|\[|\]|/[^\s/\[\]()<>]+|[-+]?\d*\.?\d+|[A-Za-z'\"*]+", re.S)


def _decode(raw, mp, two_byte):
    if two_byte:
        codes = [int.from_bytes(raw[i:i + 2], "big") for i in range(0, len(raw) - 1, 2)]
    else:
        codes = list(raw)
    return "".join(mp.get(c, bytes([c]).decode("cp1252", "replace") if c < 256 and not two_byte else "") for c in codes)


def _mul(a, b):
    return [a[0] * b[0] + a[1] * b[2], a[0] * b[1] + a[1] * b[3],
            a[2] * b[0] + a[3] * b[2], a[2] * b[1] + a[3] * b[3],
            a[4] * b[0] + a[5] * b[2] + b[4], a[4] * b[1] + a[5] * b[3] + b[5]]


def page_items(pdf, page_obj, resources, content=None, ctm0=None, depth=0):
    body = pdf.objs[page_obj] if content is None else b""
    xobjs = {}
    xd = pdf.dict_inline_or_ref(resources, b"XObject")
    for name, n in re.findall(rb"/([^\s/<>\[\]]+)\s+(\d+)\s+0\s+R", xd):
        xobjs[name] = int(n)
    fonts = {}
    fdict = pdf.dict_inline_or_ref(resources, b"Font")
    for name, n in re.findall(rb"/([^\s/<>\[\]]+)\s+(\d+)\s+0\s+R", fdict):
        fonts[name] = int(n)
    m = re.search(rb"/Contents\s*\[(.*?)\]", body, re.S) if content is None else None
    refs = [int(x) for x in re.findall(rb"(\d+)\s+0\s+R", m.group(1))] if m else [pdf.ref(body, b"Contents")]
    if content is None:
        content = b"\n".join(pdf.streams.get(r, b"") for r in refs if r is not None)
    items, stack, ops = [], [], []
    ctm0 = ctm0 or [1, 0, 0, 1, 0, 0]
    ctm, tm, tlm, lead = ctm0[:], [1, 0, 0, 1, 0, 0], [1, 0, 0, 1, 0, 0], 0.0
    font = (dict(), False)
    for t in TOK.findall(content):
        c = t[:1]
        if c in b"(<[]/" or re.fullmatch(rb"[-+]?\d*\.?\d+", t):
            ops.append(t); continue
        op = t
        nums = lambda k: [float(x) for x in ops[-k:]]
        try:
            if op == b"q": stack.append(ctm[:])
            elif op == b"Q": ctm = stack.pop() if stack else ctm
            elif op == b"cm": ctm = _mul(nums(6), ctm)
            elif op == b"BT": tm, tlm = [1, 0, 0, 1, 0, 0], [1, 0, 0, 1, 0, 0]
            elif op == b"Tm": tm = nums(6); tlm = tm[:]
            elif op in (b"Td", b"TD"):
                tx, ty = nums(2)
                if op == b"TD": lead = -ty
                tlm = _mul([1, 0, 0, 1, tx, ty], tlm); tm = tlm[:]
            elif op == b"TL": lead = nums(1)[0]
            elif op == b"T*": tlm = _mul([1, 0, 0, 1, 0, -lead], tlm); tm = tlm[:]
            elif op == b"Do" and depth < 5:
                xn = xobjs.get(ops[-1][1:])
                if xn is not None and xn in pdf.streams and b"/Form" in pdf.objs[xn][:2000]:
                    xb = pdf.objs[xn][:pdf.objs[xn].find(b"stream")]
                    mm = re.search(rb"/Matrix\s*\[([^\]]*)\]", xb)
                    mat = [float(v) for v in mm.group(1).split()] if mm else [1, 0, 0, 1, 0, 0]
                    xres = pdf.dict_inline_or_ref(xb, b"Resources") if b"/Resources" in xb else resources
                    items += page_items(pdf, xn, xres, pdf.streams[xn], _mul(mat, ctm), depth + 1)
            elif op == b"Tf": font = pdf.cmap(fonts.get(ops[-2][1:], -1))
            elif op in (b"Tj", b"'", b'"', b"TJ"):
                if op in (b"'", b'"'):
                    tlm = _mul([1, 0, 0, 1, 0, -lead], tlm); tm = tlm[:]
                parts = []
                seq = ops[ops.index(b"[") + 1:] if op == b"TJ" and b"[" in ops else ops[-1:]
                for p in seq:
                    if p.startswith(b"("):
                        parts.append(_decode(_unescape(p[1:-1]), *font))
                    elif p.startswith(b"<"):
                        parts.append(_decode(bytes.fromhex(re.sub(rb"\s", b"", p[1:-1]).decode()), *font))
                    elif p != b"]" and re.fullmatch(rb"[-+]?\d*\.?\d+", p) and float(p) < -250:
                        parts.append(" ")
                txt = "".join(parts)
                if txt.strip():
                    m2 = _mul(tm, ctm)
                    items.append((m2[4], m2[5], txt))
        except (IndexError, ValueError):
            pass
        ops = []
    return items


def lines(path, ytol=2.0):
    pdf = PDF(open(path, "rb").read())
    pages = []
    for pobj, res in pdf.pages():
        items = sorted(page_items(pdf, pobj, res), key=lambda it: (-it[1], it[0]))
        rows = []
        for x, y, t in items:
            if rows and abs(rows[-1][0] - y) <= ytol:
                rows[-1][1].append((x, t))
            else:
                rows.append([y, [(x, t)]])
        pages.append([sorted(r[1]) for r in rows])
    return pages


if __name__ == "__main__":
    for i, pg in enumerate(lines(sys.argv[1]), 1):
        print(f"=== page {i}")
        for ln in pg:
            print("\t".join(t for _, t in ln))
