"""What drives Honduran coffee output and yield, year to year? Standard library only.

Two samples, both as year-on-year log changes (so the long-run trend in area drops out):
  A. IHCAFE measured exports, crop years 1971/72-2020/21 (n = 50), a proxy for production;
  B. USDA yield per bearing hectare, crop years 2006/07-2025/26 (n = 20); C. USDA production 1982/83-2025/26.
Crop year t = October t to September t+1 (harvest Nov t - Mar t+1, flowering Feb-Apr t, fruit fill May-Oct t).
Candidate drivers are tested one by one (Pearson r, permutation p-value), then in small regressions
checked by leave-one-out prediction. Writes dataset.json and results.json next to this file."""
import json, csv, math, random, re, os, glob, collections, zipfile, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
HN = HERE + '../'
IND = HERE + '../../indonesia/'
random.seed(7)

# ---------------------------------------------------------------- data
# A. IHCAFE exports (46-kg bags) and export unit price (US$ per 46-kg bag), crop years 1970/71-2020/21
txt = open(glob.glob(HN + 'raw/ihcafe_docs2/040_*.txt')[0], encoding='utf-8', errors='replace').read()
seg = re.sub(r'\s+', ' ', txt[txt.find('Exportaciones de Café de 1970'):][:9000])
EXP, EXPPRICE = {}, {}
for n_, y1, y2, vol, usd, lps, p_l, p_usd in re.findall(r'(\d{1,2}) (\d{4})/(\d{2}) ([\d,]+) ([\d,]+) ([\d,]+) ([\d,.]+) ([\d,.]+)', seg):
    EXP[int(y1)] = float(vol.replace(',', ''))
    EXPPRICE[int(y1)] = float(p_usd.replace(',', ''))
assert len(EXP) == 51 and EXP[2016] == 9509895

# B. USDA production, bearing area
A = json.load(open(HN + 'data/area_trees_attache.json'))
PSD = {int(k): v for k, v in A['psd_full']['Arabica Production'].items()}
BEAR = dict(zip(A['years'], A['bearing_kha']))
NONB = dict(zip(A['years'], A['nonbearing_kha']))
YLD = {y: PSD[y] / BEAR[y] for y in BEAR}

# World Bank monthly prices 1960-2026 (arabica $/kg, urea $/t)
z = zipfile.ZipFile(IND + 'raw/worldbank_cmo_monthly.xlsx')
strs = [re.sub(r'<[^>]+>', '', m) for m in re.findall(r'<si>(.*?)</si>', z.read('xl/sharedStrings.xml').decode('utf8'), re.S)]
WBM = {}
for rn, body in re.findall(r'<row [^>]*r="(\d+)"[^>]*>(.*?)</row>', z.read('xl/worksheets/sheet2.xml').decode(), re.S):
    c = {}
    for col, attr, v in re.findall(r'<c r="([A-Z]+)\d+"([^>]*)>(?:<f>.*?</f>)?<v>([^<]*)</v>', body):
        c[col] = strs[int(v)] if 't="s"' in attr else v
    if re.match(r'^\d{4}M\d\d$', c.get('A', '')):
        try:
            WBM[c['A']] = (float(c['M']), float(c['BI']))
        except (KeyError, ValueError):
            pass
def wb_year(y, i):
    v = [WBM['%dM%02d' % (y, m)][i] for m in range(1, 13) if '%dM%02d' % (y, m) in WBM]
    return sum(v) / len(v) if len(v) >= 6 else None
ARA = {y: wb_year(y, 0) for y in range(1960, 2027)}
UREA = {y: wb_year(y, 1) for y in range(1960, 2027)}

# GPCC monthly rain, mean of the 3 towns, 1981-2026
G = collections.defaultdict(dict)
for r in csv.DictReader(open(HN + 'raw/rain_check/gpcc_1981_2026_monthly.csv')):
    if r['rain_mm'] != '':
        G[(int(r['year']), int(r['month']))][r['town']] = float(r['rain_mm'])
RAIN = {k: st.mean(v.values()) for k, v in G.items() if len(v) == 3}
NORM = {m: st.mean(RAIN[(y, m)] for y in range(1991, 2021)) for m in range(1, 13)}
def rain_window(t, months):
    """months: list of (year offset, month). Returns log(total / normal total) or None."""
    ks = [(t + dy, m) for dy, m in months]
    if not all(k in RAIN for k in ks):
        return None
    return math.log(sum(RAIN[k] for k in ks) / sum(NORM[m] for _, m in months))
W_DRY = [(-1, 12), (0, 1), (0, 2), (0, 3)]               # dry season before flowering
W_FLOWER = [(0, 4), (0, 5)]                              # first rains, flowering / fruit set
W_WET = [(0, m) for m in range(6, 11)]                   # main rainy season, fruit fill
W_PREV = [(-1, m) for m in range(5, 11)]                 # previous rainy season (wood for this crop)

# ONI (NOAA CPC), season centred on month m
ONI = {}
for line in open(IND + 'raw/oni.ascii.txt'):
    p = line.split()
    if len(p) == 4 and p[1].isdigit():
        ONI[(int(p[1]), ['DJF', 'JFM', 'FMA', 'MAM', 'AMJ', 'MJJ', 'JJA', 'JAS', 'ASO', 'SON', 'OND', 'NDJ'].index(p[0]) + 1)] = float(p[3])

# NASA POWER daily Tmax, mean of 3 towns (temperature only; March-May = flowering heat)
TX = collections.defaultdict(list)
for t_ in ('comayagua', 'ocotepeque', 'copan'):
    d = json.load(open(HN + 'raw/nasa_power_daily_%s.json' % t_))['properties']['parameter']['T2M_MAX']
    for k, v in d.items():
        if v > -99:
            TX[(int(k[:4]), int(k[4:6]))].append(v)
TXM = {k: st.mean(v) for k, v in TX.items()}
TXN = {m: st.mean(TXM[(y, m)] for y in range(1991, 2021)) for m in range(1, 13)}
def tmax_anom(t, months):
    ks = [(t, m) for m in months]
    return st.mean(TXM[k] - TXN[k[1]] for k in ks) if all(k in TXM for k in ks) else None

# FAO nitrogen use (t N, all crops)
FAO = {int(k): v for k, v in json.load(open(HN + 'data/faostat_inputs_land_labour.json')).items()}
NUSE = {y: v['N'] for y, v in FAO.items() if v.get('N')}

# ---------------------------------------------------------------- variables per crop year t
def lg(a, b):
    return math.log(a / b) if a and b else None

def drivers(t, dep):
    d = {}
    d['biennial: last year\'s change'] = dep.get(t - 1)
    d['price change, year t vs t-1 (flowering year)'] = lg(ARA.get(t), ARA.get(t - 1))
    d['price change, year t-1 vs t-2'] = lg(ARA.get(t - 1), ARA.get(t - 2))
    d['price level, year t-1 (log, detrended 5y)'] = (math.log(ARA[t - 1]) - st.mean(math.log(ARA[t - k]) for k in range(1, 6))) if all(ARA.get(t - k) for k in range(1, 6)) else None
    d['coffee/urea ratio change, t vs t-1'] = lg(ARA.get(t) / UREA[t] if UREA.get(t) else None, ARA.get(t - 1) / UREA[t - 1] if UREA.get(t - 1) else None)
    d['coffee/urea ratio, year t (log, vs 5y mean)'] = (math.log(ARA[t] / UREA[t]) - st.mean(math.log(ARA[t - k] / UREA[t - k]) for k in range(1, 6))) if all(ARA.get(t - k) and UREA.get(t - k) for k in range(0, 6)) else None
    d['rain, dry season Dec-Mar'] = rain_window(t, W_DRY)
    d['rain, flowering Apr-May'] = rain_window(t, W_FLOWER)
    d['rain, rainy season Jun-Oct'] = rain_window(t, W_WET)
    d['rain, previous rainy season May-Oct t-1'] = rain_window(t, W_PREV)
    d['ENSO, ONI Dec-Feb before flowering'] = ONI.get((t, 1))
    d['ENSO, ONI Jun-Aug'] = ONI.get((t, 7))
    d['Tmax anomaly Mar-May (NASA)'] = tmax_anom(t, [3, 4, 5])
    d['N fertiliser use change (FAO, all crops)'] = lg(NUSE.get(t), NUSE.get(t - 1))
    return d

DEP_E = {t: math.log(EXP[t] / EXP[t - 1]) for t in EXP if t - 1 in EXP}
LAST = 2025                                   # 2026/27 = USDA forecast, not an outcome: kept out of every test
DEP_Y = {t: math.log(YLD[t] / YLD[t - 1]) for t in YLD if t - 1 in YLD and t <= LAST}
DEP_P = {t: math.log(PSD[t] / PSD[t - 1]) for t in PSD if t - 1 in PSD and 1981 <= t <= LAST}


def pearson(x, y):
    mx, my = st.mean(x), st.mean(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / math.sqrt(sxx * syy) if sxx and syy else 0.0


def perm_p(x, y, n=5000):
    r0 = abs(pearson(x, y))
    yy = list(y)
    hits = 0
    for _ in range(n):
        random.shuffle(yy)
        if abs(pearson(x, yy)) >= r0 - 1e-12:
            hits += 1
    return (hits + 1) / (n + 1)


def ols(X, y):
    """X: list of rows (with intercept column). Returns coefficients (Gauss-Jordan on normal equations)."""
    k = len(X[0])
    M = [[sum(X[i][a] * X[i][b] for i in range(len(X))) for b in range(k)] + [sum(X[i][a] * y[i] for i in range(len(X)))] for a in range(k)]
    for c in range(k):
        p = max(range(c, k), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        piv = M[c][c]
        M[c] = [v / piv for v in M[c]]
        for r in range(k):
            if r != c:
                f = M[r][c]
                M[r] = [a - f * b for a, b in zip(M[r], M[c])]
    return [M[i][k] for i in range(k)]


def fit(rows, names, dep):
    X = [[1.0] + [r[n] for n in names] for r in rows]
    y = [r[dep] for r in rows]
    b = ols(X, y)
    pred = [sum(bi * xi for bi, xi in zip(b, x)) for x in X]
    ssr = sum((a - p) ** 2 for a, p in zip(y, pred))
    sst = sum((a - st.mean(y)) ** 2 for a in y)
    loo = []
    for i in range(len(rows)):
        Xi, yi = X[:i] + X[i + 1:], y[:i] + y[i + 1:]
        bi = ols(Xi, yi)
        loo.append(sum(c * v for c, v in zip(bi, X[i])))
    press = sum((a - p) ** 2 for a, p in zip(y, loo))
    # sign hit rate of the LOO prediction
    hit = sum(1 for a, p in zip(y, loo) if (a > 0) == (p > 0)) / len(y)
    return dict(coef=dict(zip(['intercept'] + names, b)), r2=1 - ssr / sst, loo_r2=1 - press / sst, loo_sign_hits=hit, n=len(y),
                fitted=pred, loo=loo, years=[r['year'] for r in rows], actual=y)


def screen(dep, years, label):
    rows = []
    for t in years:
        d = drivers(t, dep)
        d['year'] = t
        d['y'] = dep[t]
        rows.append(d)
    out = []
    for name in rows[0]:
        if name in ('year', 'y'):
            continue
        pairs = [(r[name], r['y']) for r in rows if r[name] is not None]
        if len(pairs) < 12:
            continue
        x, y = zip(*pairs)
        out.append(dict(driver=name, n=len(x), r=round(pearson(x, y), 3), p=round(perm_p(x, y), 4)))
    out.sort(key=lambda d: d['p'])
    return rows, out


def main():
    res = {}
    rowsE, scrE = screen(DEP_E, [t for t in sorted(DEP_E) if t >= 1982], 'exports')
    rowsY, scrY = screen(DEP_Y, sorted(DEP_Y), 'yield')
    rowsP, scrP = screen(DEP_P, [t for t in sorted(DEP_P) if t >= 1982], 'psd')
    res['screen_exports_1982_2020'] = scrE
    res['screen_yield_2006_2025'] = scrY
    res['screen_psd_production_1982_2025'] = scrP

    # pre-registered small models
    MODELS = {
        'M1 biennial only': ["biennial: last year's change"],
        'M2 biennial + price': ["biennial: last year's change", 'price change, year t vs t-1 (flowering year)'],
        'M3 biennial + price + coffee/urea': ["biennial: last year's change", 'price change, year t vs t-1 (flowering year)', 'coffee/urea ratio change, t vs t-1'],
        'M4 M2 + rainy-season rain': ["biennial: last year's change", 'price change, year t vs t-1 (flowering year)', 'rain, rainy season Jun-Oct'],
        'M5 M2 + dry-season rain': ["biennial: last year's change", 'price change, year t vs t-1 (flowering year)', 'rain, dry season Dec-Mar'],
        'M6 weather only': ['rain, dry season Dec-Mar', 'rain, flowering Apr-May', 'rain, rainy season Jun-Oct'],
    }
    for tag, rows in (('exports_1982_2020', rowsE), ('yield_2006_2025', rowsY), ('psd_1982_2025', rowsP)):
        for mname, names in MODELS.items():
            rr = [r for r in rows if all(r[n] is not None for n in names)]
            if len(rr) < 12:
                continue
            f = fit(rr, names, 'y')
            res['model_%s_%s' % (tag, mname)] = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in f.items() if k not in ('fitted', 'loo', 'years', 'actual')}
            res['model_%s_%s' % (tag, mname)]['coef'] = {k: round(v, 4) for k, v in f['coef'].items()}

    # dataset for the workbook / slides
    ds = []
    for t in range(1970, 2027):
        d = drivers(t, DEP_E) if t >= 1972 else {}
        ds.append(dict(year=t, exports_46kg=EXP.get(t), export_price_usd_46kg=EXPPRICE.get(t), psd_kbags=PSD.get(t), bearing_kha=BEAR.get(t), nonbearing_kha=NONB.get(t),
                       yield_bags_ha=YLD.get(t), arabica_usd_kg=ARA.get(t), urea_usd_t=UREA.get(t), n_use_t=NUSE.get(t),
                       rain_dry=d.get('rain, dry season Dec-Mar'), rain_flower=d.get('rain, flowering Apr-May'), rain_wet=d.get('rain, rainy season Jun-Oct'),
                       oni_djf=ONI.get((t, 1)), oni_jja=ONI.get((t, 7)), tmax_mam=d.get('Tmax anomaly Mar-May (NASA)')))
    json.dump(ds, open(HERE + 'dataset.json', 'w'), indent=1)
    json.dump(res, open(HERE + 'results.json', 'w'), indent=1, ensure_ascii=False)
    for k, v in res.items():
        print('==', k)
        if isinstance(v, list):
            for d in v:
                print('   %-50s n=%2d r=%+.2f p=%.4f' % (d['driver'], d['n'], d['r'], d['p']))
        else:
            print('   R2=%.2f  LOO-R2=%.2f  sign hits=%.0f%%  n=%d  %s' % (v['r2'], v['loo_r2'], 100 * v['loo_sign_hits'], v['n'], v['coef']))


if __name__ == '__main__':
    main()
