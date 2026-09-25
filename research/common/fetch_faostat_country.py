"""Download FAOSTAT bulk files (normalized) and keep one country's rows. Standard library only.
Usage: python3 fetch_faostat_country.py AREA_CODE OUTDIR PREFIX
Example: python3 fetch_faostat_country.py 95 research/honduras/raw/faostat honduras"""
import urllib.request, zipfile, csv, io, os, sys, json, time
area, outdir, prefix = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(outdir, exist_ok=True)
BASE = 'https://bulks-faostat.fao.org/production/'
FILES = [('qcl', 'Production_Crops_Livestock_E_All_Data_(Normalized).zip'),
         ('prices', 'Prices_E_All_Data_(Normalized).zip'),
         ('landuse', 'Inputs_LandUse_E_All_Data_(Normalized).zip'),
         ('fert_nutrient', 'Inputs_FertilizersNutrient_E_All_Data_(Normalized).zip'),
         ('fert_product', 'Inputs_FertilizersProduct_E_All_Data_(Normalized).zip'),
         ('exchange', 'Exchange_rate_E_All_Data_(Normalized).zip'),
         ('employment', 'Employment_Indicators_Agriculture_E_All_Data_(Normalized).zip'),
         ('price_indices', 'Prices_Indices_E_All_Data_(Normalized).zip')]
log = open(os.path.join(outdir, 'fetch_log.jsonl'), 'a')
for key, fn in FILES:
    url = BASE + urllib.parse.quote(fn) if hasattr(urllib, 'parse') else BASE + fn
    tmp = os.path.join(outdir, '_tmp.zip')
    t = time.time()
    try:
        import urllib.parse
        url = BASE + urllib.parse.quote(fn)
        with urllib.request.urlopen(url, timeout=600) as r, open(tmp, 'wb') as f:
            while True:
                b = r.read(1 << 20)
                if not b:
                    break
                f.write(b)
        size = os.path.getsize(tmp)
        z = zipfile.ZipFile(tmp)
        inner = [n for n in z.namelist() if n.endswith('.csv') and 'All_Data' in n and 'Flags' not in n and 'Symboles' not in n]
        n_out = 0
        with z.open(inner[0]) as raw, open(os.path.join(outdir, '%s_%s.csv' % (prefix, key)), 'w', newline='', encoding='utf-8') as out:
            rd = csv.reader(io.TextIOWrapper(raw, encoding='latin-1'))
            hdr = next(rd)
            w = csv.writer(out)
            w.writerow(hdr)
            ai = hdr.index('Area Code')
            for row in rd:
                if row[ai] == area:
                    w.writerow(row)
                    n_out += 1
        log.write(json.dumps(dict(file=fn, url=url, status=200, bytes=size, inner=inner[0], rows_kept=n_out, secs=round(time.time() - t, 1))) + '\n')
        print(key, 'ok', size, 'bytes,', n_out, 'rows')
    except Exception as e:
        log.write(json.dumps(dict(file=fn, url=url, status=repr(e)[:300], secs=round(time.time() - t, 1))) + '\n')
        print(key, 'FAILED', repr(e)[:200])
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    log.flush()
