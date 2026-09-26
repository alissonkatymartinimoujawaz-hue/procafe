# -*- coding: utf-8 -*-
"""Extract embedded images from a PDF (stdlib only): JPEG streams as .jpg, Flate bitmaps as .png.

Usage: python3 pdfimages.py file.pdf outdir [min_width]
"""
import os, re, struct, sys, zlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdftext import PDF


def png(path, w, h, ncomp, rows):
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    ctype = {1: 0, 3: 2, 4: 6}[ncomp]
    raw = b"".join(b"\x00" + r for r in rows)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, ctype, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))


def unpredict(data, w, ncomp, bpc, pred):
    stride = (w * ncomp * bpc + 7) // 8
    if pred < 10:
        return [data[i * stride:(i + 1) * stride] for i in range(len(data) // stride)]
    bpp = max(1, ncomp * bpc // 8)
    rows, prev, i = [], bytearray(stride), 0
    while i + stride + 1 <= len(data):
        ft, line = data[i], bytearray(data[i + 1:i + 1 + stride])
        for k in range(stride):
            a = line[k - bpp] if k >= bpp else 0
            b = prev[k]
            c = prev[k - bpp] if k >= bpp else 0
            if ft == 1: line[k] = (line[k] + a) & 255
            elif ft == 2: line[k] = (line[k] + b) & 255
            elif ft == 3: line[k] = (line[k] + (a + b) // 2) & 255
            elif ft == 4:
                p = a + b - c; pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[k] = (line[k] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(bytes(line)); prev = line; i += stride + 1
    return rows


def extract(pdf_path, outdir, min_w=300):
    pdf = PDF(open(pdf_path, "rb").read())
    raw = open(pdf_path, "rb").read()
    os.makedirs(outdir, exist_ok=True)
    out = []
    for n, body in sorted(pdf.objs.items()):
        head = body[:600]
        if not re.search(rb"/Subtype\s*/Image", head):
            continue
        w = int(re.search(rb"/Width\s+(\d+)", head).group(1))
        h = int(re.search(rb"/Height\s+(\d+)", head).group(1))
        if w < min_w:
            continue
        base = os.path.join(outdir, f"img{n}")
        if b"/DCTDecode" in head:
            m = re.search(rb"stream\r?\n", body)
            data = body[m.end():body.rfind(b"endstream")]
            open(base + ".jpg", "wb").write(data)
            out.append((base + ".jpg", w, h))
            continue
        data = pdf.streams.get(n)
        if data is None:
            continue
        cs = re.search(rb"/ColorSpace\s*(/\w+|\[[^\]]*\]|\d+\s+0\s+R)", head)
        cs = cs.group(1) if cs else b"/DeviceRGB"
        if re.match(rb"\d+\s+0\s+R", cs):
            cs = pdf.objs.get(int(cs.split()[0]), b"")
        ncomp = 1 if b"Gray" in cs else 4 if b"CMYK" in cs else 3
        if b"ICCBased" in cs:
            ref = re.search(rb"ICCBased\s+(\d+)\s+0\s+R", cs)
            nn = re.search(rb"/N\s+(\d)", pdf.objs.get(int(ref.group(1)), b"")) if ref else None
            ncomp = int(nn.group(1)) if nn else 3
        if b"Indexed" in cs:
            continue
        bpc = int(re.search(rb"/BitsPerComponent\s+(\d+)", head).group(1))
        if bpc != 8:
            continue
        pm = re.search(rb"/Predictor\s+(\d+)", head)
        rows = unpredict(data, w, ncomp, bpc, int(pm.group(1)) if pm else 1)[:h]
        if ncomp == 4:  # CMYK -> RGB
            rows = [bytes(v for i in range(0, len(r), 4) for v in (
                255 - min(255, r[i] + r[i + 3]), 255 - min(255, r[i + 1] + r[i + 3]), 255 - min(255, r[i + 2] + r[i + 3])))
                for r in rows]
            ncomp = 3
        png(base + ".png", w, len(rows), ncomp, rows)
        out.append((base + ".png", w, h))
    return out


if __name__ == "__main__":
    for p, w, h in extract(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 300):
        print(p, w, h)
