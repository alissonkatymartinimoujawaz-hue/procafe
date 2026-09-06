#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch Cecafé's "Resumo Diário" (daily summary of Brazilian coffee exports) and
append it to volumes/cecafe_daily.csv.

Page: https://www.cecafe.com.br/dados-estatisticos/exportacoes-brasileiras/resumo-diario/
It shows, per unit (Santos, Vitória, Rio de Janeiro, Salvador, REDEX/EADI Minas Gerais,
others, totals) and per type (arabica, conilon, soluble, total), three stages of the
export pipeline:
    certificates : certificates of origin issued
    customs      : customs clearance
    shipment     : sea and road shipments
each with three blocks: movement of the day, month-to-date cumulative, previous month.

Usage:
    python volumes/fetch_cecafe.py                    # fetch live page, append today's position
    python volumes/fetch_cecafe.py --file page.html   # parse a saved copy instead (offline)
    python volumes/fetch_cecafe.py --date 2026-09-04  # force the reference date
    python volumes/fetch_cecafe.py --print            # show what was parsed, do not write

Stdlib only. Rows already present (same date, table, unit) are replaced.
"""
import argparse, csv, os, re, sys, time, urllib.request
from datetime import date, datetime
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "cecafe_daily.csv")
URL = "https://www.cecafe.com.br/dados-estatisticos/exportacoes-brasileiras/resumo-diario/"

FIELDS = ["date", "table", "unit", "unit_label",
          "arabica_day", "conilon_day", "soluble_day", "total_day",
          "arabica_cum", "conilon_cum", "soluble_cum", "total_cum",
          "arabica_prev", "conilon_prev", "soluble_prev", "total_prev"]

TABLE_KEYS = [  # (keywords in the heading, key)
    (("certificate", "certificado"), "certificates"),
    (("customs", "desembara"), "customs"),
    (("shipment", "embarque"), "shipment"),
]
UNIT_KEYS = [
    (("santos",), "santos"),
    (("victory", "vitoria", "vitória"), "vitoria"),
    (("rio de janeiro",), "rio"),
    (("salvador",), "salvador"),
    (("redex", "eadi", "minas"), "minas"),
    (("others", "outros", "demais"), "others"),
    (("total",), "total"),
]


class Grab(HTMLParser):
    """Document-order stream of ('text', str) and ('table', rows) items."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items, self.table, self.row, self.cell = [], None, None, None
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        elif tag == "table":
            self.table = []
        elif tag == "tr" and self.table is not None:
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
        elif tag in ("td", "th") and self.cell is not None:
            self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            if self.row:
                self.table.append(self.row)
            self.row = None
        elif tag == "table" and self.table is not None:
            self.items.append(("table", self.table))
            self.table = None

    def handle_data(self, data):
        if self.skip:
            return
        if self.cell is not None:
            self.cell.append(data)
        elif self.table is None:
            t = " ".join(data.split())
            if t:
                self.items.append(("text", t))


def to_int(s):
    s = s.strip().replace(".", "").replace(" ", "").replace(" ", "")
    if s in ("", "-", "–"):
        return 0
    s = s.replace(",", "")
    return int(float(s))


def key_of(text, table):
    t = text.lower()
    for kws, k in table:
        if any(kw in t for kw in kws):
            return k
    return None


def find_date(items, html):
    """Reference date on the page: prefer text near 'posição'/'position'/'data', else any dd/mm/yyyy."""
    texts = [t for kind, t in items if kind == "text"]
    pat = re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})")
    for t in texts:
        if re.search(r"posi|position|data|date|atualiza|update", t, re.I):
            m = pat.search(t)
            if m:
                return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    for t in texts:
        m = pat.search(t)
        if m:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    return None


def parse(html):
    g = Grab(); g.feed(html)
    out, last_title = [], None
    for kind, val in g.items:
        if kind == "text":
            k = key_of(val, TABLE_KEYS)
            if k and len(val) < 80:
                last_title = k
            continue
        rows = [r for r in val if len(r) >= 13 and key_of(r[0], UNIT_KEYS)]
        if not rows:
            continue
        # A caption/heading may sit inside the table: check the first cells too
        title = last_title
        for r in val[:3]:
            k = key_of(" ".join(r), TABLE_KEYS)
            if k:
                title = k; break
        if not title:
            continue
        for r in rows:
            try:
                nums = [to_int(x) for x in r[-12:]]
            except ValueError:
                continue
            out.append({"table": title, "unit": key_of(r[0], UNIT_KEYS), "unit_label": r[0], "nums": nums})
        last_title = None
    return out, find_date(g.items, html)


def fetch(url, tries=3):
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (procafe volumes tracker)"})
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
            for enc in ("utf-8", "latin-1"):
                try:
                    return raw.decode(enc)
                except UnicodeDecodeError:
                    pass
        except Exception as e:  # noqa
            last = e; time.sleep(3 * (k + 1))
    sys.exit(f"fetch failed: {last!r}")


def load_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", help="parse a saved HTML copy instead of fetching")
    ap.add_argument("--date", help="reference date YYYY-MM-DD (default: date found on the page, else today)")
    ap.add_argument("--print", action="store_true", help="print parsed rows, do not write the CSV")
    ap.add_argument("--out", default=CSV)
    a = ap.parse_args()

    html = open(a.file, encoding="utf-8", errors="replace").read() if a.file else fetch(URL)
    rows, page_date = parse(html)
    if not rows:
        sys.exit("no table recognised on the page (layout changed?) — save the HTML and open an issue")
    d = datetime.strptime(a.date, "%Y-%m-%d").date() if a.date else (page_date or date.today())
    if not a.date and not page_date:
        print("  WARN: no date found on the page, using today", d)

    recs = []
    for r in rows:
        rec = {"date": d.isoformat(), "table": r["table"], "unit": r["unit"], "unit_label": r["unit_label"]}
        rec.update(dict(zip(FIELDS[4:], r["nums"])))
        recs.append(rec)
    tables = sorted({r["table"] for r in recs})
    print(f"parsed {len(recs)} rows for {d}: tables {tables}")
    if a.print:
        for r in recs:
            print("  ", r["table"], r["unit"].ljust(8), r["total_day"], "/", r["total_cum"], "/", r["total_prev"])
        return

    old = load_csv(a.out)
    key = lambda r: (r["date"], r["table"], r["unit"])
    new_keys = {key(r) for r in recs}
    merged = [r for r in old if key(r) not in new_keys] + recs
    merged.sort(key=lambda r: (r["date"], r["table"], r["unit"]))
    with open(a.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(merged)
    print(f"wrote {os.path.relpath(a.out)} ({len(merged)} rows, {len(recs)} added or replaced for {d})")


if __name__ == "__main__":
    main()
