"""Robustness tests and forecast back-test for Honduran coffee output. Standard library only.

Builds on analysis.py (same data). Tests:
  1. Is there a biennial (on/off) cycle, or just one-off shocks around a trend?
  2. How much of the USDA yield swing is production and how much is bearing-area revisions?
  3. Does USDA production agree with IHCAFE measured exports?
  4. Fertiliser chain: N use vs output, and what moves N use.
  5. Weather: El Nino / La Nina years, driest seasons, coffee-zone rain (ERA5-Land, 13 points) when present.
  6. Multiple testing: Holm correction of the single-driver screens.
  7. Back-test 2000/01-2025/26 of simple forecast methods and of the USDA May forecast.
Writes robustness.json next to this file."""
import json, math, random, os, csv, collections, statistics as st
from analysis import (HERE, HN, EXP, EXPPRICE, PSD, BEAR, NONB, YLD, ARA, UREA, NUSE, ONI, RAIN, NORM, rain_window,
                      W_DRY, W_FLOWER, W_WET, W_PREV, DEP_E, DEP_P, DEP_Y, pearson, perm_p, ols, screen)

random.seed(11)
OUT = {}


def dlog(S, years):
    return {t: math.log(S[t] / S[t - 1]) for t in years if t in S and t - 1 in S}


# ---------------------------------------------------------------- 1. biennial cycle or one-off shocks?
# If log output = trend + independent yearly shocks, the change this year vs the change last year has
# correlation -0.5 by construction and the sign of the change flips 2 times in 3. A true on/off cycle
# gives a correlation below -0.5 and more flips; persistent shocks give a correlation above -0.5.
def iid_band(n, sims=4000):
    out = []
    for _ in range(sims):
        e = [random.gauss(0, 1) for _ in range(n + 1)]
        d = [e[i] - e[i - 1] for i in range(1, n + 1)]
        out.append(pearson(d[:-1], d[1:]))
    out.sort()
    return out[int(.025 * sims)], out[int(.975 * sims)]


bi = []
for name, S, years in (('IHCAFE exports 1970/71-2020/21', EXP, range(1971, 2021)),
                       ('USDA production 1980/81-2025/26', PSD, range(1981, 2026)),
                       ('USDA yield per bearing ha 2005/06-2025/26', YLD, range(2006, 2026))):
    D = dlog(S, years)
    ts = [t for t in sorted(D) if t - 1 in D]
    x, y = [D[t - 1] for t in ts], [D[t] for t in ts]
    r = pearson(x, y)
    lo, hi = iid_band(len(ts) + 1)
    flips = sum(1 for a, b in zip(x, y) if (a > 0) != (b > 0)) / len(x)
    bi.append(dict(series=name, n=len(ts), r=r, implied_phi=1 + 2 * r, iid_lo=lo, iid_hi=hi, flips=flips))
OUT['biennial'] = bi

# ---------------------------------------------------------------- 2. yield = production / bearing area
yrs = range(2006, 2026)
dP, dA, dY = dlog(PSD, yrs), dlog(BEAR, yrs), dlog(YLD, yrs)
mP, mA = st.mean(dP.values()), st.mean(dA.values())
OUT['yield_decomposition'] = dict(
    var_dY=st.pvariance(list(dY.values())), var_dP=st.pvariance(list(dP.values())), var_dA=st.pvariance(list(dA.values())),
    minus2cov=-2 * sum((dP[t] - mP) * (dA[t] - mA) for t in dP) / len(dP),
    rows=[dict(year=t, dP=dP[t], dA=dA[t], dY=dY[t]) for t in yrs])

# ---------------------------------------------------------------- 3. USDA production vs IHCAFE exports
c = [t for t in range(1982, 2021) if t in DEP_E and t in DEP_P]
OUT['psd_vs_exports'] = dict(r_changes=pearson([DEP_P[t] for t in c], [DEP_E[t] for t in c]), n=len(c),
                             rows=[dict(year=t, psd_kbags=PSD[t], exports_60kg_k=EXP[t] * 46 / 60 / 1000) for t in range(2000, 2021)])

# ---------------------------------------------------------------- 4. fertiliser chain
ny = [t for t in range(2005, 2023) if NUSE.get(t) and NUSE.get(t - 1)]
dN = {t: math.log(NUSE[t] / NUSE[t - 1]) for t in ny}
EV = {t: EXP[t] * EXPPRICE[t] for t in EXP}
chain = []
for lab, f in (('N use change vs output change, same crop year', lambda t: DEP_P.get(t)),
               ('N use change vs output change of the crop before (income)', lambda t: DEP_P.get(t - 1)),
               ('N use change vs world arabica price change, same calendar year', lambda t: math.log(ARA[t] / ARA[t - 1])),
               ('N use change vs coffee/urea price ratio change', lambda t: math.log(ARA[t] / UREA[t] / (ARA[t - 1] / UREA[t - 1]))),
               ('N use change vs urea price change', lambda t: math.log(UREA[t] / UREA[t - 1])),
               ('N use change vs IHCAFE export price change of the crop before', lambda t: math.log(EXPPRICE[t - 1] / EXPPRICE[t - 2]) if t - 2 in EXPPRICE and t - 1 in EXPPRICE else None)):
    pts = [(f(t), dN[t]) for t in ny if f(t) is not None]
    x, y = zip(*pts)
    chain.append(dict(test=lab, n=len(x), r=pearson(x, y), p=perm_p(x, y, 5000)))
ys = [t for t in ny if t in DEP_P]
x, y = [dN[t] for t in ys], [DEP_P[t] for t in ys]
OUT['fertiliser'] = dict(tests=chain, drop_one_min_r=min(pearson(x[:i] + x[i + 1:], y[:i] + y[i + 1:]) for i in range(len(x))),
                         rows=[dict(year=t, n_use_t=NUSE[t], dN=dN[t], dP=DEP_P.get(t), arabica=ARA[t], urea=UREA[t]) for t in ny])

# ---------------------------------------------------------------- 5. weather
def enso_rows(sign):
    rows = []
    for y0 in range(1982, 2025):
        o = ONI.get((y0, 11))
        if o is not None and ((sign > 0 and o >= 1.0) or (sign < 0 and o <= -1.0)):
            rows.append(dict(year=y0, oni_ond=o, dP_t=DEP_P.get(y0), dP_t1=DEP_P.get(y0 + 1)))
    return rows


def extremes(W, k=7):
    w = sorted((rain_window(t, W), t) for t in range(1982, 2026) if rain_window(t, W) is not None and t in DEP_P)
    return [dict(year=t, rain_pct=100 * (math.exp(v) - 1), dP_t=DEP_P[t], dP_t1=DEP_P.get(t + 1)) for v, t in w[:k]]


OUT['enso'] = dict(el_nino=enso_rows(1), la_nina=enso_rows(-1))
OUT['driest'] = dict(dry_season=extremes(W_DRY), rainy_season=extremes(W_WET))
OUT['rain_2026'] = {k: (100 * (math.exp(rain_window(2026, W)) - 1) if rain_window(2026, W) is not None else None)
                    for k, W in (('dry Dec-Mar', W_DRY), ('flowering Apr-May', W_FLOWER), ('Jun-Aug', [(0, 6), (0, 7), (0, 8)]))}

# coffee-zone ERA5-Land temperature (10 coffee municipalities; Open-Meteo returned no rain for this model, see raw/coffee_zones/NOTES.md)
CZ = HN + 'raw/coffee_zones/monthly.csv'
if os.path.exists(CZ):
    Z = collections.defaultdict(dict)
    for r in csv.DictReader(open(CZ)):
        if r['tmax_mean_c'] not in ('', 'None'):
            Z[(int(r['year']), int(r['month']))][r['key']] = float(r['tmax_mean_c'])
    keys = sorted({k for v in Z.values() for k in v})
    ZT = {ym: st.mean(v.values()) for ym, v in Z.items() if len(v) == len(keys)}
    ZN = {m: st.mean(ZT[(y, m)] for y in range(1991, 2021)) for m in range(1, 13)}

    def zan(t, months):
        ks = [(t + dy, m) for dy, m in months]
        return st.mean(ZT[k] - ZN[k[1]] for k in ks) if all(k in ZT for k in ks) else None
    WIN = (('Tmax Dec-Feb', [(-1, 12), (0, 1), (0, 2)]), ('Tmax Mar-May (flowering)', [(0, 3), (0, 4), (0, 5)]),
           ('Tmax Jun-Aug (fruit fill)', [(0, 6), (0, 7), (0, 8)]), ('Tmax Sep-Oct', [(0, 9), (0, 10)]))
    zs = []
    for lab_, W in WIN:
        for dep_name, DEP in (('USDA production', DEP_P), ('IHCAFE exports', DEP_E)):
            pts = [(zan(t, W), DEP[t]) for t in sorted(DEP) if t >= 1982 and zan(t, W) is not None]
            x, y = zip(*pts)
            zs.append(dict(window=lab_, dep=dep_name, n=len(x), r=pearson(x, y), p=perm_p(x, y, 5000)))
    SO = {t: zan(t, [(0, 9), (0, 10)]) for t in range(1981, 2026)}
    SO_2026_SEP = ZT[(2026, 9)] - ZN[9]                          # 1-18 Sep 2026 only
    yy = [t for t in DEP_P if t >= 1982 and all(SO.get(t - k) is not None for k in range(0, 11))]
    det = {t: SO[t] - st.mean(SO[t - k] for k in range(1, 11)) for t in yy}
    dd = [t for t in DEP_P if t >= 1983 and SO.get(t) is not None and SO.get(t - 1) is not None]
    extra = [dict(window='Tmax Sep-Oct, vs mean of the 10 years before (removes warming)', dep='USDA production', n=len(yy),
                  r=pearson([det[t] for t in yy], [DEP_P[t] for t in yy]), p=perm_p([det[t] for t in yy], [DEP_P[t] for t in yy], 5000)),
             dict(window='Tmax Sep-Oct, change on the year before', dep='USDA production', n=len(dd),
                  r=pearson([SO[t] - SO[t - 1] for t in dd], [DEP_P[t] for t in dd]), p=perm_p([SO[t] - SO[t - 1] for t in dd], [DEP_P[t] for t in dd], 5000)),
             dict(window='Rain Sep-Oct (GPCC)', dep='USDA production', n=len([t for t in DEP_P if t >= 1982 and rain_window(t, [(0, 9), (0, 10)]) is not None]),
                  r=pearson(*zip(*[(rain_window(t, [(0, 9), (0, 10)]), DEP_P[t]) for t in sorted(DEP_P) if t >= 1982 and rain_window(t, [(0, 9), (0, 10)]) is not None])),
                  p=perm_p(*zip(*[(rain_window(t, [(0, 9), (0, 10)]), DEP_P[t]) for t in sorted(DEP_P) if t >= 1982 and rain_window(t, [(0, 9), (0, 10)]) is not None]), n=5000))]
    hot = sorted(((zan(t, WIN[2][1]), t) for t in range(1982, 2027) if zan(t, WIN[2][1]) is not None), reverse=True)
    OUT['coffee_zone_tmax'] = dict(points=keys, tests=zs,
                                   anom_2026={lab_: zan(2026, W) for lab_, W in WIN if zan(2026, W) is not None},
                                   hottest_jun_aug=[dict(year=t, anom=v, dP_t=DEP_P.get(t)) for v, t in hot[:6]],
                                   monthly_2026={m: dict(tmax=ZT.get((2026, m)), normal=ZN[m]) for m in range(1, 13)},
                                   extra_tests=extra, sep_oct={t: SO[t] for t in SO if SO[t] is not None}, sep_2026_to_18=SO_2026_SEP,
                                   hottest_sep_oct=[dict(year=t, anom=SO[t], dP_t=DEP_P.get(t)) for t in sorted(SO, key=lambda t: -SO[t])[:6]])

# ---------------------------------------------------------------- 6. multiple testing (Holm), per sample
def holm(scr):
    m = len(scr)
    out, running = [], 0
    for i, d in enumerate(sorted(scr, key=lambda d: d['p'])):
        running = max(running, min(1, (m - i) * d['p']))
        out.append(dict(d, p_holm=running))
    return out


OUT['screens'] = {}
for tag, dep, years in (('exports_1982_2020', DEP_E, [t for t in sorted(DEP_E) if t >= 1982]),
                        ('psd_1982_2025', DEP_P, [t for t in sorted(DEP_P) if t >= 1982]),
                        ('yield_2006_2025', DEP_Y, sorted(DEP_Y))):
    OUT['screens'][tag] = holm(screen(dep, years, tag)[1])

# ---------------------------------------------------------------- 7. forecast back-test, crop years 2000/01-2025/26
L = {t: math.log(v) for t, v in PSD.items()}


def ma(t, k):
    return st.mean(L[t - i] for i in range(1, k + 1))


def dry(t):
    return rain_window(t, W_DRY)


def dpr(t):
    return math.log(ARA[t] / ARA[t - 1])


def trend(t, n):
    xs = list(range(t - n, t))
    b = ols([[1, x] for x in xs], [L[x] for x in xs])
    return b[0] + b[1] * t


def m5(t):
    rows = [s for s in range(1983, t) if dry(s) is not None]
    b = ols([[1, L[s - 1] - L[s - 2], dpr(s), dry(s)] for s in rows], [L[s] - L[s - 1] for s in rows])
    return L[t - 1] + b[0] + b[1] * (L[t - 1] - L[t - 2]) + b[2] * dpr(t) + b[3] * dry(t)


def ma_sig(t, k=4):
    rows = [s for s in range(1987, t) if dry(s) is not None]
    b = ols([[1, dpr(s), dry(s)] for s in rows], [L[s] - ma(s, k) for s in rows])
    return ma(t, k) + b[0] + b[1] * dpr(t) + b[2] * dry(t)


HEAT = OUT.get('coffee_zone_tmax', {}).get('sep_oct', {})


def m7(t, h=None):
    rows = [s_ for s_ in range(1983, t) if dry(s_) is not None]
    b = ols([[1, L[s_ - 1] - L[s_ - 2], dpr(s_), dry(s_), HEAT[s_]] for s_ in rows], [L[s_] - L[s_ - 1] for s_ in rows])
    return L[t - 1] + b[0] + b[1] * (L[t - 1] - L[t - 2]) + b[2] * dpr(t) + b[3] * dry(t) + b[4] * (HEAT[t] if h is None else h)


METHODS = {
    'Last year (random walk)': lambda t: L[t - 1],
    'Average of last 2 years': lambda t: ma(t, 2),
    'Average of last 3 years': lambda t: ma(t, 3),
    'Average of last 4 years': lambda t: ma(t, 4),
    'Linear trend, last 8 years': lambda t: trend(t, 8),
    'Model: mean reversion + price + dry-season rain': m5,
    'Average of last 4 years + price + dry-season rain': ma_sig,
    'Combination: mean of (last 2 years) and the model': lambda t: (ma(t, 2) + m5(t)) / 2,
}
if HEAT:
    METHODS['Model + Sep-Oct heat (coffee zones)'] = m7
    METHODS['Combination: last 2 years and model + heat'] = lambda t: (ma(t, 2) + m7(t)) / 2
TGT = list(range(2000, 2026))
bt = []
for name, f in METHODS.items():
    e = [f(t) - L[t] for t in TGT]
    hits = sum(1 for t in TGT if (f(t) - L[t - 1] > 0) == (L[t] - L[t - 1] > 0))
    bt.append(dict(method=name, mape=st.mean(abs(math.exp(x) - 1) for x in e), bias=st.mean(math.exp(x) - 1 for x in e),
                   direction_hits=hits / len(TGT), n=len(TGT), f2026=math.exp(f(2026)) if 'heat' not in name else None,
                   path=[dict(year=t, forecast=math.exp(f(t)), actual=PSD[t]) for t in TGT]))
bt.sort(key=lambda d: d['mape'])
# USDA attache first forecast of the coming crop, read in the May Coffee Annual of each year (1000 60-kg bags).
# 2019 report not held; the 2022-2024 reports forecast the crop then being harvested, not the next one, so they are left out.
USDA_MAY = {2011: 3900, 2012: 5000, 2013: 5100, 2014: 5000, 2015: 5900, 2016: 6100, 2017: 6500, 2018: 7300, 2020: 6100, 2021: 5500, 2025: 5800}
uy = sorted(USDA_MAY)
usda = dict(years=uy, mape=st.mean(abs(USDA_MAY[t] / PSD[t] - 1) for t in uy),
            direction_hits=sum(1 for t in uy if (USDA_MAY[t] > PSD[t - 1]) == (PSD[t] > PSD[t - 1])) / len(uy),
            rows=[dict(year=t, usda_may=USDA_MAY[t], actual=PSD[t]) for t in uy],
            same_years={name: st.mean(abs(math.exp(f(t) - L[t]) - 1) for t in uy) for name, f in METHODS.items()},
            f2026=6030)
OUT['backtest'] = dict(methods=bt, usda=usda)
if HEAT:
    rows = [s_ for s_ in range(1983, 2026) if dry(s_) is not None]
    X = [[1, L[s_ - 1] - L[s_ - 2], dpr(s_), dry(s_), HEAT[s_]] for s_ in rows]
    y = [L[s_] - L[s_ - 1] for s_ in rows]
    b = ols(X, y)
    pred = [sum(c * v for c, v in zip(b, x)) for x in X]
    OUT['heat_model'] = dict(coef=dict(zip(['intercept', 'last_change', 'price_change', 'dry_rain_log', 'tmax_sep_oct'], b)), n=len(rows),
                             r2=1 - sum((a - q) ** 2 for a, q in zip(y, pred)) / sum((a - st.mean(y)) ** 2 for a in y))
OUT['inputs_2026'] = dict(arabica_2025=ARA[2025], arabica_2026=ARA[2026], urea_2025=UREA[2025], urea_2026=UREA[2026],
                          ratio_2025=ARA[2025] * 1000 / UREA[2025], ratio_2026=ARA[2026] * 1000 / UREA[2026],
                          psd_2024=PSD[2024], psd_2025=PSD[2025], psd_2026=PSD[2026], oni_last={'%d-%02d' % k: ONI[k] for k in sorted(ONI)[-4:]})

json.dump(OUT, open(HERE + 'robustness.json', 'w'), indent=1, ensure_ascii=False, default=float)

if __name__ == '__main__':
    for d in bi:
        print('%-45s n=%d r=%+.2f phi=%+.2f iid band [%+.2f,%+.2f] flips %.0f%%' % (d['series'], d['n'], d['r'], d['implied_phi'], d['iid_lo'], d['iid_hi'], 100 * d['flips']))
    y = OUT['yield_decomposition']
    print('var dY %.4f dP %.4f dA %.4f -2cov %.4f' % (y['var_dY'], y['var_dP'], y['var_dA'], y['minus2cov']))
    for d in chain:
        print('%-70s n=%d r=%+.2f p=%.3f' % (d['test'], d['n'], d['r'], d['p']))
    print('drop-one min r', round(OUT['fertiliser']['drop_one_min_r'], 2))
    for tag, s in OUT['screens'].items():
        print(tag, [(d['driver'][:30], round(d['p'], 4), round(d['p_holm'], 3)) for d in s[:4]])
    if 'coffee_zone_tmax' in OUT:
        for d in OUT['coffee_zone_tmax']['tests']:
            print('zone %-28s %-16s n=%d r=%+.2f p=%.3f' % (d['window'], d['dep'], d['n'], d['r'], d['p']))
        print('zone Tmax anomalies 2026', OUT['coffee_zone_tmax']['anom_2026'], 'hottest Jun-Aug', OUT['coffee_zone_tmax']['hottest_jun_aug'])
    print('GPCC rain 2026', OUT['rain_2026'])
    for d in bt:
        print('%-52s MAPE %4.1f%% bias %+5.1f%% dir %3.0f%% 2026/27 %s' % (d['method'], 100 * d['mape'], 100 * d['bias'], 100 * d['direction_hits'], '%5.0f' % d['f2026'] if d['f2026'] else 'needs Sep-Oct 2026'))
    print('USDA May forecast n=%d MAPE %.1f%% dir %.0f%%' % (len(uy), 100 * usda['mape'], 100 * usda['direction_hits']), {k: round(100 * v, 1) for k, v in usda['same_years'].items()})
