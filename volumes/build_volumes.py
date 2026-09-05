#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coffee depot / storage volume tracker — Minas Gerais & Espírito Santo.

What it does
------------
1. Reads volumes/daily_log.csv — YOUR daily entries, one line per site per day:
       date,state,site,inflow_bags,outflow_bags,stock_bags,source,note
   * inflow_bags / outflow_bags : bags (60 kg) that entered / left the depot that day
   * stock_bags (optional)      : measured stock at end of day. When given it overrides
                                  the running balance (previous stock + inflow - outflow).
   Lines starting with '#' and blank lines are ignored.

2. (optional, --exports) Downloads the official Comex Stat bulk CSVs (MDIC) and builds
   the MONTHLY export series of coffee (NCM 0901) shipped from MG and ES — the only
   official "outflow" series that exists for the two states. Files are cached in
   volumes/cache/ (they are big: ~100-200 MB per year).

3. Writes data/volumes.js  ->  window.VOLUMES, consumed by volumes.html.

Usage (from the repo root, any Python 3.8+, no extra packages):
    python volumes/build_volumes.py                       # daily log only, no network
    python volumes/build_volumes.py --exports             # + Comex Stat, current & previous year
    python volumes/build_volumes.py --exports --years 2023 2024 2025 2026
    python volumes/build_volumes.py --exports --refresh   # re-download cached CSVs
"""
import argparse, csv, io, json, os, sys, time, urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOG = os.path.join(HERE, "daily_log.csv")
CACHE = os.path.join(HERE, "cache")
OUT = os.path.join(ROOT, "data", "volumes.js")

STATES = {"MG": "Minas Gerais", "ES": "Espírito Santo"}
BAG_KG = 60.0

# Comex Stat bulk files (Ministério do Desenvolvimento, Indústria, Comércio e Serviços)
# Layout NCM file : CO_ANO;CO_MES;CO_NCM;CO_UNID;CO_PAIS;SG_UF_NCM;CO_VIA;CO_URF;QT_ESTAT;KG_LIQUIDO;VL_FOB
# Layout MUN file : CO_ANO;CO_MES;SH4;CO_PAIS;SG_UF_MUN;CO_MUN;KG_LIQUIDO;VL_FOB
COMEX_NCM = "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/EXP_{y}.csv"
COMEX_MUN = "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/mun/EXP_{y}_MUN.csv"
COMEX_UFMUN = "https://balanca.economia.gov.br/balanca/bd/tabelas/UF_MUN.csv"


# --------------------------------------------------------------------------- daily log
def num(s):
    s = (s or "").strip().replace(" ", "").replace(",", ".")
    if s == "":
        return None
    return float(s)


def read_log(path):
    if not os.path.exists(path):
        sys.exit(f"missing {path} — create it (see volumes/README.md)")
    rows, problems = [], []
    with open(path, encoding="utf-8-sig", newline="") as f:
        lines = [l for l in f if l.strip() and not l.lstrip().startswith("#")]
    rd = csv.DictReader(lines)
    need = {"date", "state", "site", "inflow_bags", "outflow_bags", "stock_bags", "source", "note"}
    missing = need - set(rd.fieldnames or [])
    if missing:
        sys.exit(f"daily_log.csv header is missing columns: {sorted(missing)}")
    for i, r in enumerate(rd, start=2):
        try:
            d = datetime.strptime(r["date"].strip(), "%Y-%m-%d").date()
        except Exception:
            problems.append(f"line {i}: bad date {r['date']!r} (use YYYY-MM-DD)"); continue
        st = (r["state"] or "").strip().upper()
        if st not in STATES:
            problems.append(f"line {i}: state must be MG or ES, got {r['state']!r}"); continue
        site = (r["site"] or "").strip()
        if not site:
            problems.append(f"line {i}: empty site"); continue
        try:
            inflow, outflow, stock = num(r["inflow_bags"]), num(r["outflow_bags"]), num(r["stock_bags"])
        except ValueError:
            problems.append(f"line {i}: non-numeric bags value"); continue
        rows.append({"date": d, "state": st, "site": site,
                     "inflow": inflow or 0.0, "outflow": outflow or 0.0, "stock": stock,
                     "source": (r["source"] or "").strip(), "note": (r["note"] or "").strip()})
    for p in problems:
        print("  WARN", p)
    rows.sort(key=lambda r: (r["site"], r["date"]))
    return rows


def daterange(d0, d1):
    while d0 <= d1:
        yield d0
        d0 += timedelta(days=1)


def build_series(rows):
    """Per-site daily series over the full date span, then state totals and grand total.
       Stock is carried forward on days without an entry; inflow/outflow are 0 there."""
    if not rows:
        return None
    d0 = min(r["date"] for r in rows)
    d1 = max(r["date"] for r in rows)
    dates = list(daterange(d0, d1))
    idx = {d: i for i, d in enumerate(dates)}
    n = len(dates)

    by_site = defaultdict(list)
    for r in rows:
        by_site[r["site"]].append(r)

    sites = {}
    for site, rs in by_site.items():
        inflow, outflow = [0.0] * n, [0.0] * n
        stock = [None] * n
        measured = [False] * n
        state = rs[-1]["state"]
        # same site + same day: sums flows, last measured stock wins
        per_day = defaultdict(lambda: {"in": 0.0, "out": 0.0, "stock": None})
        for r in rs:
            p = per_day[r["date"]]
            p["in"] += r["inflow"]; p["out"] += r["outflow"]
            if r["stock"] is not None:
                p["stock"] = r["stock"]
        s = 0.0
        first = min(per_day)
        for d in dates:
            i = idx[d]
            p = per_day.get(d)
            if p:
                inflow[i], outflow[i] = p["in"], p["out"]
                if p["stock"] is not None:
                    s = p["stock"]; measured[i] = True
                else:
                    s = s + p["in"] - p["out"]
            stock[i] = None if d < first else round(s, 1)
        sites[site] = {"state": state, "inflow": inflow, "outflow": outflow,
                       "stock": stock, "measured": measured}

    def total(keys):
        inflow, outflow, stock = [0.0] * n, [0.0] * n, [0.0] * n
        for k in keys:
            sv = sites[k]
            for i in range(n):
                inflow[i] += sv["inflow"][i]; outflow[i] += sv["outflow"][i]
                stock[i] += sv["stock"][i] or 0.0
        return {"inflow": [round(v, 1) for v in inflow], "outflow": [round(v, 1) for v in outflow],
                "stock": [round(v, 1) for v in stock]}

    states = {}
    for st in STATES:
        keys = [k for k, v in sites.items() if v["state"] == st]
        if keys:
            states[st] = total(keys)
            states[st]["sites"] = sorted(keys)
    return {"dates": [d.isoformat() for d in dates], "sites": sites,
            "states": states, "all": total(list(sites))}


# --------------------------------------------------------------------------- Comex Stat
def download(url, dest, refresh=False, tries=3):
    if os.path.exists(dest) and not refresh and os.path.getsize(dest) > 0:
        print(f"  cached  {os.path.basename(dest)}")
        return dest
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    last = None
    for k in range(tries):
        try:
            print(f"  GET {url}", flush=True)
            req = urllib.request.Request(url, headers={"User-Agent": "procafe-volumes/1.0"})
            with urllib.request.urlopen(req, timeout=180) as r, open(dest + ".part", "wb") as w:
                got = 0
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    w.write(chunk); got += len(chunk)
                    if got % (20 << 20) < (1 << 20):
                        print(f"     {got / 1e6:.0f} MB", flush=True)
            os.replace(dest + ".part", dest)
            return dest
        except Exception as e:  # noqa
            last = e
            time.sleep(3 * (k + 1))
    print(f"  FAILED {url}: {last!r}")
    return None


def open_text(path):
    """MDIC files are ISO-8859-1; fall back to it only if the file is not valid UTF-8."""
    with open(path, "rb") as f:
        head = f.read(1 << 16)
    try:
        head.decode("utf-8"); enc = "utf-8"
    except UnicodeDecodeError:
        enc = "latin-1"
    return open(path, encoding=enc, newline="")


def parse_ncm(path, acc):
    """acc[uf][YYYY-MM][cat] += kg   cat in {'green','roasted','total'}"""
    with open_text(path) as f:
        rd = csv.reader(f, delimiter=";")
        head = next(rd)
        col = {h.strip('"'): i for i, h in enumerate(head)}
        iN, iU, iY, iM, iK = col["CO_NCM"], col["SG_UF_NCM"], col["CO_ANO"], col["CO_MES"], col["KG_LIQUIDO"]
        for row in rd:
            ncm = row[iN]
            if not ncm.startswith("0901"):
                continue
            uf = row[iU]
            if uf not in STATES:
                continue
            key = f"{row[iY]}-{int(row[iM]):02d}"
            kg = float(row[iK])
            a = acc[uf][key]
            a["total"] += kg
            if ncm[:6] in ("090111", "090112"):
                a["green"] += kg
            elif ncm[:6] in ("090121", "090122"):
                a["roasted"] += kg


def parse_mun(path, acc):
    """acc[uf][YYYY-MM][CO_MUN] += kg  (SH4 == 0901, i.e. all coffee)"""
    with open_text(path) as f:
        rd = csv.reader(f, delimiter=";")
        head = next(rd)
        col = {h.strip('"'): i for i, h in enumerate(head)}
        iS, iU, iY, iM, iK, iC = col["SH4"], col["SG_UF_MUN"], col["CO_ANO"], col["CO_MES"], col["KG_LIQUIDO"], col["CO_MUN"]
        for row in rd:
            if row[iS] != "0901":
                continue
            uf = row[iU]
            if uf not in STATES:
                continue
            key = f"{row[iY]}-{int(row[iM]):02d}"
            acc[uf][key][row[iC]] += float(row[iK])


def load_mun_names(path):
    names = {}
    if not path:
        return names
    with open_text(path) as f:
        rd = csv.reader(f, delimiter=";")
        head = next(rd)
        col = {h.strip('"'): i for i, h in enumerate(head)}
        ic = col.get("CO_MUN_GEO", col.get("CO_MUN"))
        iname = col.get("NO_MUN_MIN", col.get("NO_MUN"))
        for row in rd:
            names[row[ic]] = row[iname]
    return names


def build_exports(years, refresh):
    ncm_acc = defaultdict(lambda: defaultdict(lambda: {"green": 0.0, "roasted": 0.0, "total": 0.0}))
    mun_acc = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    ok_years = []
    for y in years:
        p = download(COMEX_NCM.format(y=y), os.path.join(CACHE, f"EXP_{y}.csv"), refresh)
        if p:
            parse_ncm(p, ncm_acc); ok_years.append(y)
        pm = download(COMEX_MUN.format(y=y), os.path.join(CACHE, f"EXP_{y}_MUN.csv"), refresh)
        if pm:
            parse_mun(pm, mun_acc)
    if not ok_years:
        return None
    names = load_mun_names(download(COMEX_UFMUN, os.path.join(CACHE, "UF_MUN.csv"), refresh))

    monthly = {}
    for uf in STATES:
        monthly[uf] = {k: {c: round(v / BAG_KG) for c, v in d.items()}
                       for k, d in sorted(ncm_acc[uf].items())}
    municipal = {}
    for uf in STATES:
        tot = defaultdict(float)
        for k, d in mun_acc[uf].items():
            for m, kg in d.items():
                tot[m] += kg
        top = sorted(tot.items(), key=lambda kv: -kv[1])[:20]
        municipal[uf] = [{"code": m, "name": names.get(m, m), "bags": round(kg / BAG_KG),
                          "monthly": {k: round(mun_acc[uf][k].get(m, 0.0) / BAG_KG)
                                      for k in sorted(mun_acc[uf])}}
                         for m, kg in top]
    return {"source": "Comex Stat / MDIC — bulk CSV (NCM 0901, UF of origin)",
            "unit": "bags of 60 kg (KG_LIQUIDO / 60)",
            "years": ok_years, "monthly": monthly, "municipal": municipal}


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--exports", action="store_true", help="also fetch Comex Stat monthly exports for MG/ES")
    ap.add_argument("--years", nargs="*", type=int, help="years for --exports (default: previous + current)")
    ap.add_argument("--refresh", action="store_true", help="re-download cached Comex Stat files")
    args = ap.parse_args()

    print("reading", os.path.relpath(LOG, ROOT))
    rows = read_log(LOG)
    print(f"  {len(rows)} entries, {len({r['site'] for r in rows})} sites")
    series = build_series(rows)

    exports = None
    if args.exports:
        years = args.years or [date.today().year - 1, date.today().year]
        print("Comex Stat exports for", years)
        exports = build_exports(years, args.refresh)

    # keep previously fetched exports if this run did not fetch them
    if exports is None and os.path.exists(OUT):
        try:
            with open(OUT, encoding="utf-8") as f:
                txt = f.read()
            prev = json.loads(txt[txt.index("=") + 1:].rstrip().rstrip(";"))
            exports = prev.get("exports")
            if exports:
                print("  keeping exports from previous data/volumes.js")
        except Exception:
            pass

    payload = {
        "generated": date.today().isoformat(),
        "unit": "bags of 60 kg",
        "states": STATES,
        "log": [{"date": r["date"].isoformat(), "state": r["state"], "site": r["site"],
                 "inflow": r["inflow"], "outflow": r["outflow"], "stock": r["stock"],
                 "source": r["source"], "note": r["note"]} for r in rows],
        "series": series,
        "exports": exports,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("// AUTO-GENERATED by volumes/build_volumes.py — do not edit by hand.\n")
        f.write("window.VOLUMES = ")
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    print("wrote", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
