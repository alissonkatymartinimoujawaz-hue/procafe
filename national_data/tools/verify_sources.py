# -*- coding: utf-8 -*-
"""Presence check of the national CSVs against the raw source files.

Every value of mexico_siap.csv, peru_midagri.csv, uganda_ucda.csv and indonesia_bps.csv is searched in the text of
the files under raw/<source>/ (PDF text via pdftext2, .xls/.xlsx cell values, .html/.txt), in the usual printed
forms (1,234,567 / 1 234 567 / 1.234.567 / 1234,5 ...; thousands with one decimal); spreadsheet cells also match
numerically (cell x 1, x 1000 or / 1000, rounded to the CSV value's decimals). faostat.csv is compared value by value
(and flag by flag) with raw/faostat/. Unmatched rows are printed for manual review (see VERIFICATION.md).
PDF text is cached in .cache/ (git-ignored).  Usage: python3 tools/verify_sources.py
"""
import csv, glob, json, os, re, sys, zipfile, xml.etree.ElementTree as ET
ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ND, "tools"))
from pdftext2 import lines
import xls_biff
CACHE = os.path.join(ND, ".cache")
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def xlsx_values(path):
    z = zipfile.ZipFile(path)
    sst = []
    if "xl/sharedStrings.xml" in z.namelist():
        sst = ["".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])) for si in
               ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS)]
    out = []
    for n in z.namelist():
        if re.match(r"xl/worksheets/sheet\d+\.xml$", n):
            for c in ET.fromstring(z.read(n)).iter("{%s}c" % NS["m"]):
                v = c.find("m:v", NS)
                if v is not None and v.text is not None:
                    out.append(sst[int(v.text)] if c.get("t") == "s" else v.text)
    return out


def pdf_pages(path):
    os.makedirs(CACHE, exist_ok=True)
    dst = os.path.join(CACHE, os.path.basename(path) + ".json")
    if not os.path.exists(dst):
        try:
            pages = [["  ".join(t for x, t in ln) for ln in pg] for pg in lines(path)]
        except Exception as e:                     # e.g. the AES-encrypted Planeación PDF (see raw/mexico_siap/decrypt.py)
            pages = [[f"EXTRACTION FAILED: {e!r}"]]
        json.dump(pages, open(dst, "w"))
    return json.load(open(dst))


def numbers(sub):
    """Numeric cells of the spreadsheets of raw/<sub>/."""
    out = []
    for f in glob.glob(os.path.join(ND, "raw", sub, "**", "*"), recursive=True):
        vals = xlsx_values(f) if f.endswith(".xlsx") else [v for cells in xls_biff.parse(f).values() for v in cells.values()] \
            if f.endswith(".xls") else []
        for v in vals:
            try:
                out.append(float(v))
            except (TypeError, ValueError):
                pass
    return out


def numeric_match(v, nums):
    d = len(v.split(".")[1]) if "." in v else 0
    x = float(v)
    return any(round(n * k, d) == round(x, d) for n in nums for k in (1, 1000, 0.001))


def corpus(sub):
    out = {}
    for f in glob.glob(os.path.join(ND, "raw", sub, "**", "*"), recursive=True):
        b = os.path.basename(f)
        if f.endswith(".pdf"):
            for i, pg in enumerate(pdf_pages(f)):
                out[f"{b} p{i + 1}"] = "\n".join(pg)
        elif f.endswith((".txt", ".html")):
            out[b] = open(f, encoding="utf-8", errors="replace").read()
        elif f.endswith(".xlsx"):
            out[b] = "\n".join(xlsx_values(f))
        elif f.endswith(".xls"):
            out[b] = "\n".join(repr(v) if isinstance(v, float) else str(v)
                               for cells in xls_biff.parse(f).values() for v in cells.values())
    return out


def forms(s):
    out, x = {s}, float(s)
    if x == int(x) and abs(x) >= 1000:
        c = f"{int(x):,}"
        out |= {c, c.replace(",", " "), c.replace(",", "."), c.replace(",", " "), repr(float(int(x)))}
    if "." in s:
        ip, dp = s.split(".")
        out |= {ip + "," + dp, repr(float(s)), s.rstrip("0").rstrip(".")}
        if len(ip) > 3:
            c = f"{int(ip):,}"
            out |= {c + "." + dp, c.replace(",", " ") + "," + dp, c.replace(",", " ") + "." + dp, c.replace(",", ".") + "," + dp}
    return {f for f in out if f}


def found(v, texts):
    fs = forms(v)
    return [k for k, t in texts.items() if any(re.search(r"(?<![\d.,])" + re.escape(f) + r"(?![\d])", t) for f in fs)]


def check_fao():
    raw = {}
    for r in csv.DictReader(open(os.path.join(ND, "raw", "faostat", "QCL_coffee_green_656_5countries.csv"), encoding="utf-8")):
        el = {"Area harvested": "area_harvested", "Production": "production", "Yield": "yield"}.get(r["Element"])
        if el:
            raw[(r["Area"], el, r["Year"])] = (float(r["Value"]), r["Flag"])
    bad = []
    rows = list(csv.DictReader(open(os.path.join(ND, "faostat.csv"), encoding="utf-8")))
    for r in rows:
        v, flag = raw[(r["country"], r["indicator"], r["period"])]
        if abs(v - float(r["value"])) > 1e-6 or re.search(r"flag (\w)", r["notes"]).group(1) != flag:
            bad.append(r)
    print(f"faostat.csv: {len(rows) - len(bad)}/{len(rows)} values and flags identical to raw/faostat")
    for r in bad:
        print("   MISMATCH:", r["country"], r["indicator"], r["period"], r["value"])


def main():
    check_fao()
    for fn, sub in (("mexico_siap.csv", "mexico_siap"), ("peru_midagri.csv", "peru_midagri"),
                    ("uganda_ucda.csv", "uganda_ucda"), ("indonesia_bps.csv", "indonesia_bps")):
        texts, nums = corpus(sub), numbers(sub)
        rows = list(csv.DictReader(open(os.path.join(ND, fn), encoding="utf-8")))
        miss = []
        for r in rows:
            v, x = r["value"], float(r["value"])
            hit = found(v, texts)
            if not hit and r["unit"] in ("t", "ha") and x >= 1000:
                hit = found(f"{x / 1000:.1f}", texts) or found(f"{x / 1000:.3f}", texts)
            if not hit and numeric_match(v, nums):
                hit = ["spreadsheet cell"]
            if not hit:
                miss.append(r)
        print(f"{fn}: {len(rows) - len(miss)}/{len(rows)} values found in raw/{sub}")
        for r in miss:
            print("   not found:", r["indicator"], r["unit"], r["period"], r["value"], "|", r["notes"][:110])


if __name__ == "__main__":
    main()
