#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Download the OFFICIAL bulk datasets behind the coffee demand deck.

Run this on a machine / session with open internet access (the Claude cloud
sandbox that produced v1 of the deck had these hosts blocked):

    python research/coffee-demand/scripts/fetch_official_data.py

Every file lands in research/coffee-demand/data/source_files/ and is logged in
MANIFEST.csv (url, local file, bytes, sha256, UTC timestamp, status), so each
number in the deck can be traced back to a downloaded official file.

Sources
  USDA FAS PSD Online   coffee production / supply / distribution, every country, 1960 -> latest forecast
  World Bank Pink Sheet monthly + annual Arabica & Robusta ($/kg), 1960 -> latest month
  IMF PCPS              monthly Other Mild Arabicas & Robusta (US cents/lb) — same ICO quotes as the Pink Sheet
  FRED (St. Louis Fed)  mirror of the IMF series (backup)
  US Census Bureau      US imports of green coffee (HS 090111) by origin, annual, kg and US$
  UN Comtrade (public)  green coffee imports (HS 090111) of Japan, China, Korea, Russia, Canada, ...
  Eurostat Comext       EU-27 extra-EU imports of CN 0901 11 00 by partner (quantity, 100 kg)

The script never overwrites a good file with a failed download.  URLs that the
sandbox could not test are marked `untested=True`; if one fails, the error
message tells you which official page to download it from by hand.
"""
import csv
import datetime as dt
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "data", "source_files"))
MANIFEST = os.path.join(OUT, "MANIFEST.csv")
UA = {"User-Agent": "Mozilla/5.0 (research; coffee-demand deck)"}

YEARS = list(range(2005, dt.date.today().year + 1))

# ISO numeric codes used by UN Comtrade
COMTRADE_REPORTERS = {
    "Japan": 392, "China": 156, "Korea, Rep.": 410, "Russian Federation": 643, "Canada": 124,
    "Australia": 36, "Algeria": 12, "Saudi Arabia": 682, "Turkiye": 792, "Egypt": 818,
    "United Kingdom": 826, "Switzerland": 757, "Morocco": 504, "Ukraine": 804, "Taiwan (Other Asia nes)": 490,
    "Philippines": 608, "Malaysia": 458, "Thailand": 764, "Israel": 376, "Norway": 578,
}

# Eurostat partner codes (ISO-2) for the main origins of EU green-coffee imports
EU_PARTNERS = ["BR", "VN", "UG", "HN", "CO", "IN", "ID", "PE", "ET", "NI", "GT", "TZ", "CI",
               "KE", "CR", "MX", "SV", "PG", "LA", "CM", "RW", "BI", "EC", "CN"]

SOURCES = [
    dict(key="usda_psd_coffee", untested=False,
         url="https://apps.fas.usda.gov/psdonline/downloads/psd_coffee_csv.zip",
         file="usda_psd_coffee_csv.zip",
         manual="https://apps.fas.usda.gov/psdonline/app/index.html#/app/downloads"),
    dict(key="wb_pinksheet_monthly", untested=False,
         url="https://thedocs.worldbank.org/en/doc/5d903e848db1d1b83e0ec8f744e55570-0350012021/related/CMO-Historical-Data-Monthly.xlsx",
         file="wb_CMO-Historical-Data-Monthly.xlsx",
         manual="https://www.worldbank.org/en/research/commodity-markets"),
    dict(key="wb_pinksheet_annual", untested=False,
         url="https://thedocs.worldbank.org/en/doc/5d903e848db1d1b83e0ec8f744e55570-0350012021/related/CMO-Historical-Data-Annual.xlsx",
         file="wb_CMO-Historical-Data-Annual.xlsx",
         manual="https://www.worldbank.org/en/research/commodity-markets"),
    dict(key="imf_pcps", untested=False,
         url="https://www.imf.org/-/media/Files/Research/CommodityPrices/Monthly/external-data.ashx",
         file="imf_pcps_external-data.xls",
         manual="https://www.imf.org/en/Research/commodity-prices"),
    dict(key="fred_arabica", untested=False,
         url="https://fred.stlouisfed.org/graph/fredgraph.csv?id=PCOFFOTMUSDM",
         file="fred_PCOFFOTMUSDM.csv", manual="https://fred.stlouisfed.org/series/PCOFFOTMUSDM"),
    dict(key="fred_robusta", untested=False,
         url="https://fred.stlouisfed.org/graph/fredgraph.csv?id=PCOFFROBUSDM",
         file="fred_PCOFFROBUSDM.csv", manual="https://fred.stlouisfed.org/series/PCOFFROBUSDM"),
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def log(row):
    new = not os.path.exists(MANIFEST)
    with open(MANIFEST, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["utc", "key", "url", "file", "bytes", "sha256", "status"])
        w.writerow(row)


def download(key, url, fname, tries=3, pause=3):
    dest = os.path.join(OUT, fname)
    tmp = dest + ".part"
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=180) as r, open(tmp, "wb") as f:
                f.write(r.read())
            if os.path.getsize(tmp) < 200:
                raise RuntimeError("file too small (%d bytes)" % os.path.getsize(tmp))
            os.replace(tmp, dest)
            log([dt.datetime.utcnow().isoformat(timespec="seconds"), key, url, fname,
                 os.path.getsize(dest), sha256(dest), "ok"])
            return dest
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(pause * (k + 1))
    if os.path.exists(tmp):
        os.remove(tmp)
    log([dt.datetime.utcnow().isoformat(timespec="seconds"), key, url, fname, "", "", "FAILED: %r" % (last,)])
    return None


def fetch_static():
    ok = {}
    for s in SOURCES:
        print("->", s["key"], end=" ", flush=True)
        p = download(s["key"], s["url"], s["file"])
        ok[s["key"]] = bool(p)
        print("ok" if p else "FAILED  (download by hand from %s)" % s["manual"])
    return ok


def fetch_census_us_imports():
    """US Census international trade API: HS6 090111 imports by country, annual (December YTD)."""
    rows = []
    for y in YEARS:
        month = "12" if y < dt.date.today().year else "%02d" % max(1, dt.date.today().month - 2)
        q = {"get": "CTY_CODE,CTY_NAME,GEN_QY1_YR,GEN_VAL_YR,UNIT_QY1",
             "time": f"{y}-{month}", "COMM_LVL": "HS6", "I_COMMODITY": "090111"}
        url = "https://api.census.gov/data/timeseries/intltrade/imports/hs?" + urllib.parse.urlencode(q)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                data = json.load(r)
            hdr = data[0]
            for rec in data[1:]:
                d = dict(zip(hdr, rec)); d["year"] = y; d["ytd_month"] = month
                rows.append(d)
            print(f"   census {y}: {len(data) - 1} rows")
        except Exception as e:  # noqa: BLE001
            print(f"   census {y}: FAILED {e!r}")
    if rows:
        path = os.path.join(OUT, "census_us_imports_090111.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=sorted({k for r in rows for k in r}))
            w.writeheader(); w.writerows(rows)
        log([dt.datetime.utcnow().isoformat(timespec="seconds"), "census_us_imports",
             "api.census.gov/data/timeseries/intltrade/imports/hs", os.path.basename(path),
             os.path.getsize(path), sha256(path), "ok"])


def fetch_comtrade():
    """UN Comtrade public preview API (no key; max 500 records per call)."""
    rows = []
    for name, code in COMTRADE_REPORTERS.items():
        for chunk in (YEARS[:12], YEARS[12:]):
            if not chunk:
                continue
            q = {"reporterCode": code, "period": ",".join(map(str, chunk)), "partnerCode": 0,
                 "cmdCode": "090111", "flowCode": "M"}
            url = "https://comtradeapi.un.org/public/v1/preview/C/A/HS?" + urllib.parse.urlencode(q)
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                    data = json.load(r).get("data", [])
                for d in data:
                    rows.append({"reporter": name, "reporterCode": code, "period": d.get("period"),
                                 "netWgt_kg": d.get("netWgt"), "qty": d.get("qty"),
                                 "qtyUnitAbbr": d.get("qtyUnitAbbr"), "primaryValue_usd": d.get("primaryValue")})
                print(f"   comtrade {name} {chunk[0]}-{chunk[-1]}: {len(data)} rows")
            except Exception as e:  # noqa: BLE001
                print(f"   comtrade {name}: FAILED {e!r}")
            time.sleep(1.2)  # be polite to the public endpoint
    if rows:
        path = os.path.join(OUT, "comtrade_imports_090111.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
        log([dt.datetime.utcnow().isoformat(timespec="seconds"), "comtrade_imports",
             "comtradeapi.un.org/public/v1/preview", os.path.basename(path),
             os.path.getsize(path), sha256(path), "ok"])


def fetch_eurostat():
    """Eurostat Comext SDMX 2.1 (dataset DS-045409, CN8 09011100, annual, extra-EU imports).
    untested in the sandbox: if it fails, use Easy Comext (https://ec.europa.eu/eurostat/comext/newxtweb/)
    with reporter EU27_2020, product 09011100, flow import, indicator QUANTITY_IN_100KG."""
    base = "https://ec.europa.eu/eurostat/api/comext/dissemination/sdmx/2.1/data/DS-045409/"
    got = 0
    for p in EU_PARTNERS + ["EXT_EU27_2020"]:
        key = f"A.EU27_2020.{p}.09011100.1.QUANTITY_IN_100KG"
        url = base + key + "?format=SDMX-CSV&startPeriod=2005"
        if download("eurostat_" + p, url, f"eurostat_eu27_imports_09011100_{p}.csv", tries=2):
            got += 1
        time.sleep(0.5)
    print(f"   eurostat: {got}/{len(EU_PARTNERS) + 1} partner files")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print("Downloading official coffee datasets into", OUT)
    fetch_static()
    fetch_census_us_imports()
    fetch_comtrade()
    fetch_eurostat()
    print("Done. See", MANIFEST)
    print("Next: python research/coffee-demand/scripts/build_all.py")
