"""Indonesia robusta 2027/28: the forecast chain, link by link, with the data behind each link.
Reads proof_series.json (FAOSTAT, ministry, USDA, NASA POWER series) and ../forecast_dataset.csv."""
import json, math, random, statistics as st, sys, os, csv
sys.path.insert(0, os.path.dirname(__file__))
from ooxml import Slide, run, para, bar_chart, scatter_chart, combo_bar, multi_line, yield_chart, solid, hatch, save

HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
S = json.load(open(HERE + 'proof_series.json'))
FAO, ROWS = S['fao'], S['rows']
Y = FAO['yrs']
FD = {int(r['recolte_annee_N']): r for r in csv.DictReader(open(BASE + 'forecast_dataset.csv'))}

NAVY, EN, LN, NEU, RED, GREY, INK = '1F3864', 'ED7D31', '2E75B6', '7F7F7F', 'C00000', '7F7F7F', '262626'
COF, COC, ROB = '7B4A2D', 'E3A33B', '2E75B6'
GOOD, BAD, LIGHT = '3A8D5B', 'C00000', 'BFBFBF'
PCT = '+0.0"%";-0.0"%";0.0"%"'


# ---------- statistics ----------
def yoy(a):
    return [None] + [100 * (a[i] / a[i - 1] - 1) if a[i] is not None and a[i - 1] is not None else None for i in range(1, len(a))]


def pairs(x, y):
    return [(a, b) for a, b in zip(x, y) if a is not None and b is not None]


def corr(x, y):
    p = pairs(x, y)
    xs, ys = zip(*p)
    mx, my = st.mean(xs), st.mean(ys)
    sx = math.sqrt(sum((a - mx) ** 2 for a in xs))
    sy = math.sqrt(sum((b - my) ** 2 for b in ys))
    return sum((a - mx) * (b - my) for a, b in p) / (sx * sy)


def perm_p(x, y, n=4000, seed=1):
    """two-sided permutation p-value of Pearson r"""
    p = pairs(x, y)
    xs, ys = list(zip(*p))
    r0 = abs(corr(xs, ys))
    ys = list(ys)
    rnd = random.Random(seed)
    hit = 0
    for _ in range(n):
        rnd.shuffle(ys)
        if abs(corr(xs, ys)) >= r0 - 1e-12:
            hit += 1
    return hit / n


def blank(a, years):
    return [None if Y[i] in years else a[i] for i in range(len(Y))]


def lag(a, k):
    return [None] * k + a[:len(a) - k]


def cagr(a, y0, y1):
    return 100 * ((a[Y.index(y1)] / a[Y.index(y0)]) ** (1 / (y1 - y0)) - 1)


def fr(v, d=1, plus=False):
    s = '%.*f' % (d, v)
    if plus and v > 0:
        s = '+' + s
    return s.replace('-', '−')


def pfmt(p):
    return 'p < 0.001' if p < 0.001 else 'p = %.3f' % p if p < 0.01 else 'p = %.2f' % p


# ---------- layout helpers ----------
def header(s, title, bullets=(), src=None):
    s.text(0.45, 0.22, 12.4, 0.55, [para(run(title, 24 if len(title) <= 62 else 20, True, color=NAVY))], anchor='t')
    if bullets:
        s.text(0.75, 0.78, 11.9, 0.26 * len(bullets) + 0.05,
               [para(run(b, 10.5, color=INK, hl='FFFF00'), bullet=True, after=1) for b in bullets])
    if src:
        s.text(0.45, 7.02, 12.4, 0.42, [para(run(src, 7.5, color=GREY))])


def label(s, x, y, w, t, sz=11, color='404040', algn='l', b=True):
    s.text(x, y, w, 0.3, [para(run(t, sz, b, color=color), algn=algn)])


def box(s, x, y, w, h, title, lines, color=NAVY, sz=9.5):
    s.rect(x, y, w, h, fill='F3F6F9', line=color, lw=1.25)
    ps = [para(run(title, sz + 1.5, True, color=color), after=3)]
    for ln in lines:
        ps.append(para(ln if isinstance(ln, str) and ln.startswith('<a:r>') else run(ln, sz, color=INK), after=2))
    s.text(x + 0.12, y + 0.08, w - 0.24, h - 0.16, ps)


def th(t, sz=9, algn='l'):
    return {'t': t, 'b': True, 'fill': NAVY, 'color': 'FFFFFF', 'sz': sz, 'algn': algn}


def td(t, sz=9, algn='l', color=INK, fill=None, b=False):
    return {'t': t, 'sz': sz, 'algn': algn, 'color': color, 'fill': fill, 'b': b}


def hbar(cats, series, mn, mx, unit, fmt='0.0', legend=False):
    """horizontal clustered bars: bar_chart with swapped axes (first category drawn at the bottom)"""
    x = bar_chart(cats, series, mn=mn, mx=mx, unit=unit, fmt=fmt, labels=True, legend=legend, gap=40, overlap=0)
    x = x.replace('<c:barDir val="col"/>', '<c:barDir val="bar"/>')
    x = x.replace('<c:axId val="50010"/><c:scaling><c:orientation val="minMax"/></c:scaling><c:delete val="0"/><c:axPos val="b"/>',
                  '<c:axId val="50010"/><c:scaling><c:orientation val="minMax"/></c:scaling><c:delete val="0"/><c:axPos val="l"/>')
    x = x.replace('<c:delete val="0"/><c:axPos val="l"/><c:majorGridlines>', '<c:delete val="0"/><c:axPos val="b"/><c:majorGridlines>')
    return x


def bins_of(rows, key, edges_names):
    out = []
    for lo, hi, name in edges_names:
        g = [r for r in rows if r[key] is not None and lo <= r[key] < hi]
        out.append(dict(name=name, n=len(g), mean=st.mean(r['anom'] for r in g), med=st.median(r['anom'] for r in g),
                        down=sum(1 for r in g if r['anom'] < 0), yrs=[r['N'] for r in g]))
    return out


def bin_chart(s, x, y, w, h, bins, hi_idx, title, mn, mx, unit=5):
    hi_idx = hi_idx if isinstance(hi_idx, (list, tuple)) else [hi_idx]
    cats = ['%s (n=%d)' % (b['name'], b['n']) for b in bins]
    cols = [(NAVY if i in hi_idx else (GOOD if b['mean'] >= 0 else BAD)) for i, b in enumerate(bins)]
    label(s, x, y - 0.3, w, title, 11)
    s.chart(x, y, w, h, combo_bar(cats, [{'name': 'Mean crop vs trend', 'color': LIGHT, 'values': [round(b['mean'], 1) for b in bins], 'point_colors': cols}],
                                  mn=mn, mx=mx, unit=unit, fmt='+0;-0;0', label_fmt=PCT, legend=False, gap=60, label_sz=10))


slides = []

# ======================================================================
# computations: area
# ======================================================================
A, YL, R = FAO['area'], FAO['yld'], FAO['rev']
PLANT = FAO['planted']
BRK = {2003, 2006, 2008}  # FAO cocoa area: series breaks (+24 %, −22 %, +54 %)
ac, ak, ap = yoy(A['coffee']), yoy(A['cocoa']), yoy(PLANT)
ak_c = blank(ak, BRK)
ac_c = blank(ac, BRK)
r_area = corr(ac_c, ak_c)
p_area = perm_p(ac_c, ak_c)
opp = [(Y[i], ac[i], ak[i]) for i in range(len(Y)) if ac_c[i] is not None and ak_c[i] is not None]
n_opp = sum(1 for _, a, b in opp if a * b < 0)
r_area_pl = corr(blank(ap, BRK), ak_c)
p_area_pl = perm_p(blank(ap, BRK), ak_c)

price = {k: [R[k][i] / YL[k][i] * 1000 if R[k][i] is not None and YL[k][i] else None for i in range(len(Y))] for k in ('coffee', 'cocoa')}
rc, rk = yoy(R['coffee']), yoy(R['cocoa'])
pc, pk = yoy(price['coffee']), yoy(price['cocoa'])
yc, yk = yoy(YL['coffee']), yoy(YL['cocoa'])
r_rev, p_rev = corr(rc, rk), perm_p(rc, rk)
r_rev24, p_rev24 = corr(rc[:25], rk[:25]), perm_p(rc[:25], rk[:25])
r_px, p_px = corr(pc, pk), perm_p(pc, pk)
r_yl, p_yl = corr(yc, yk), perm_p(yc, yk)


def var_share(k):
    lr = [math.log(R[k][i] / R[k][i - 1]) for i in range(1, 25)]
    lp = [math.log(price[k][i] / price[k][i - 1]) for i in range(1, 25)]
    cov = st.mean(a * b for a, b in zip(lr, lp)) - st.mean(lr) * st.mean(lp)
    return 100 * cov / st.pvariance(lr)


sh_cof, sh_coc = var_share('coffee'), var_share('cocoa')
same = [(Y[i], rc[i], rk[i]) for i in range(len(Y)) if rc[i] is not None and rk[i] is not None]
n_same = sum(1 for _, a, b in same if a * b > 0)
rnd = random.Random(2)
xs_, ys_ = [a for _, a, _ in same], [b for _, _, b in same]
hit = 0
for _ in range(4000):
    rnd.shuffle(ys_)
    hit += sum(1 for a, b in zip(xs_, ys_) if a * b > 0) >= n_same
p_same = hit / 4000
big_both = [y for y, a, b in same if a >= 30 and b >= 30]

rel_rev = [R['coffee'][i] / R['cocoa'][i] for i in range(len(Y))]
lags = {k: (corr(lag(rel_rev, k), ap), perm_p(lag(rel_rev, k), ap)) for k in (1, 2, 3)}
d_rel = yoy(rel_rev)
r_drel = corr(lag(d_rel, 1), ap)
p_drel = perm_p(lag(d_rel, 1), ap)
reg = [(Y[i], rel_rev[i - 1], ap[i]) for i in range(1, len(Y)) if ap[i] is not None]
lo_reg = [g for _, rr, g in reg if rr < 1]
hi_reg = [g for _, rr, g in reg if rr >= 1]
r_ay, p_ay = corr(ac, yc), perm_p(ac, yc)
rob_y = yoy(FAO['rob_yld'])
r_py, p_py = corr(ap, rob_y), perm_p(ap, rob_y)

# ======================================================================
# computations: yield study
# ======================================================================
FEAT = [('trig', 'Flowering trigger, towns (0–5)'), ('trig_high', 'Trigger, highland towns (0–2)'), ('rain_JJASO', 'Rain Jun–Oct'),
        ('dry_JJAS', 'Rain Jun–Sep (dry season)'), ('rain_ASO', 'Rain Aug–Oct'), ('rain_SON', 'Rain Sep–Nov'), ('rain_high_ASO', 'Rain Aug–Oct, highland'),
        ('rain_low_ASO', 'Rain Aug–Oct, lowland'), ('dryspell', 'Longest dry spell Jun–Oct'), ('tmax_JASO', 'Max temperature Jul–Oct'),
        ('tmean_JASO', 'Mean temperature Jul–Oct'), ('fill_rain', 'Rain Dec–Mar (bean filling)'), ('fill_tmax', 'Max temp. Dec–Mar (bean filling)'),
        ('harv_rain', 'Rain Apr–Aug (harvest)'), ('annual_rain_F', 'Rain, whole flowering year'), ('oni', 'ENSO (ONI) Aug–Nov'),
        ('dmi', 'IOD (DMI) Aug–Nov'), ('prev', 'Previous crop vs trend')]
anom = [r['anom'] for r in ROWS]
yoyp = [r['yoy'] for r in ROWS]
FR = {}
for k, name in FEAT:
    v = [r[k] for r in ROWS]
    FR[k] = dict(name=name, r=corr(v, anom), p=perm_p(v, anom, 3000), ry=corr(v, yoyp), py=perm_p(v, yoyp, 3000))

F26 = S['flowering2026']['mean']
OBS26 = S['flowering2026']['observed_to_19sep']
TRIG26 = sum(1 for t in S['triggers'] if S['triggers'][t].get('2026'))


def ols(X, y):
    n = len(X[0])
    M = [[sum(r[i] * r[j] for r in X) for j in range(n)] for i in range(n)]
    b = [sum(r[i] * v for r, v in zip(X, y)) for i in range(n)]
    for i in range(n):
        for k in range(i + 1, n):
            f = M[k][i] / M[i][i]
            M[k] = [a - f * c for a, c in zip(M[k], M[i])]
            b[k] -= f * b[i]
    x = [0] * n
    for i in reversed(range(n)):
        x[i] = (b[i] - sum(M[i][j] * x[j] for j in range(i + 1, n))) / M[i][i]
    return x


B0, B1 = ols([[1, r['trig']] for r in ROWS], anom)
W26 = B0 + B1 * TRIG26
W26_5 = B0 + B1 * 5
analog = [r for r in ROWS if r['trig'] >= 3 and 50 <= r['rain_JJASO'] <= 100 and -0.2 <= r['tmax_JASO'] <= 1.3]
an_sorted = sorted(r['anom'] for r in analog)
an_med = st.median(an_sorted)
an_q1, an_q3 = an_sorted[len(an_sorted) // 4], an_sorted[(3 * len(an_sorted)) // 4]

# back-test: base = median of the 3 previous USDA crops; + trigger model fitted without the year
js = open(BASE + 'weather_data.js').read()
UA = {int(k): v / 1000 for k, v in json.loads(js[js.index('{'):js.rindex('}') + 1])['usda_robusta'].items()}
e_naive, e_model = [], []
for i, r in enumerate(ROWS):
    N = r['N']
    base = st.median([UA[N - 1], UA[N - 2], UA[N - 3]])
    tr = [x for j, x in enumerate(ROWS) if j != i]
    b0, b1 = ols([[1, x['trig']] for x in tr], [x['anom'] for x in tr])
    e_naive.append(100 * (UA[N] / base - 1))
    e_model.append(100 * (UA[N] / (base * (1 + (b0 + b1 * r['trig']) / 100)) - 1))
rmse = lambda e: math.sqrt(st.mean(x * x for x in e))
RM_NAIVE, RM_MODEL = rmse(e_naive), rmse(e_model)

# forecast arithmetic
AREA27 = float(FD[2027]['surface_productive_ha'])
AREA26 = float(FD[2026]['surface_productive_ha'])
YLD3 = [float(FD[y]['rendement_usda_sacs_par_ha']) for y in (2024, 2025, 2026)]
TY = st.median(YLD3)
BASE27 = AREA27 * TY / 1e6
Y27 = TY * (1 + W26 / 100)
P27 = AREA27 * Y27 / 1e6
P27_lo, P27_hi = BASE27 * (1 + an_q1 / 100), BASE27 * (1 + an_q3 / 100)
P27_s_lo, P27_s_hi = P27 * (1 - RM_MODEL / 100), P27 * (1 + RM_MODEL / 100)
ENIOD = [r for r in ROWS if r['oni'] is not None and r['dmi'] is not None and r['oni'] >= 0.5 and r['dmi'] >= 0.4]
EN_IOD = st.mean(r['anom'] for r in ENIOD)
P27_dry = BASE27 * (1 + EN_IOD / 100)
P27_liwa = BASE27 * (1 + W26_5 / 100)

# ======================================================================
# 1. title
# ======================================================================
s = Slide()
s.text(0.8, 2.1, 11.8, 1.2, [para(run('Indonesia Robusta 2027/28: the forecast chain, link by link, with proof', 32, True, color=NAVY))])
s.text(0.8, 3.45, 11.5, 0.9, [para(run('Production = productive area × yield. For each link: the data, the calculation, the chart and the number it gives.', 15, color='404040'))])
s.text(0.8, 4.2, 11.5, 0.9, [para(run('Area: FAOSTAT, ministry of agriculture, coffee vs cocoa, 2000–2026 · Yield: 45 USDA crops (1982–2026) against NASA POWER weather in 5 robusta towns', 12, color='595959'))])
s.text(0.8, 5.0, 11.5, 0.4, [para(run('24 September 2026 · weather observed to 19 September 2026, normal weather assumed after', 12, color=GREY))])
slides.append(s)

# ======================================================================
# 2. the chain on one page
# ======================================================================
s = Slide()
header(s, 'The chain: %s ha × %s bags/ha = %s M bags' % (format(round(AREA27), ','), fr(Y27, 2), fr(P27, 1)), [
    'Area and yield are two separate engines: area follows which crop pays more, slowly; yield follows the weather of the flowering season (slide 7)',
    'The 2027 productive area is already fixed by past plantings: only the yield is still open, and weather explains about a quarter of it',
    'Normal weather from 20 September assumed: trigger rain came on time in 4 of 5 towns → yield +%s %% above trend' % fr(W26, 1)],
    'Slide numbers refer to the proof for each link. Bags of 60 kg. Trend yield = median of the USDA yields of the last 3 crops.')
bx = [(0.45, 'AREA · 709,158 ha', COF, [
    '1. World price × rupiah → farm-gate price (slides 4–5)',
    '2. Revenue per ha of coffee vs cocoa: farmers plant the crop that paid more 1–3 years before (slide 6)',
    '3. Coffee and cocoa share the same land: when one gains, the other loses (slide 3)',
    '4. Land is closing: permanent crops grow 4× slower than in the 2000s (slide 8)',
    '→ productive area %s ha in 2027, +%s %% on 2026 (slide 8)' % (format(round(AREA27), ','), fr(100 * (AREA27 / AREA26 - 1), 1))]),
      (4.72, 'YIELD · %s bags/ha' % fr(Y27, 2), LN, [
    '1. Trend: median of the last 3 USDA yields = %s bags/ha (13.27, 15.64, 14.16)' % fr(TY, 2),
    '2. Flowering trigger rain is the #1 weather signal: r = %s over 45 crops (slide 10–11)' % fr(FR['trig']['r'], 2, True),
    '3. A normal year: trigger in 2–3 towns out of 5, Jul–Aug (slide 9)',
    '4. 2026: 4 of 5 towns, Jun–Oct rain %s %% of normal, heat +%s °C (slide 14)' % (fr(F26['rain_JJASO'], 0), fr(F26['tmax'], 1)),
    '→ weather effect %s %% → %s bags/ha (slide 15)' % (fr(W26, 1, True), fr(Y27, 2))]),
      (8.99, 'PRODUCTION · %s M bags' % fr(P27, 1), NAVY, [
    'Trend production: %s ha × %s = %s M bags' % (format(round(AREA27), ','), fr(TY, 2), fr(BASE27, 2)),
    'With normal weather from now: %s M bags (+%s %% on 2026/27)' % (fr(P27, 2), fr(100 * (P27 / (float(FD[2026]['production_usda_M_sacs'])) - 1), 1)),
    'Half of the analog years fell in %s–%s M bags' % (fr(P27_lo, 1), fr(P27_hi, 1)),
    'Dry Oct–Nov (El Niño + positive IOD, the risk this year): %s M bags' % fr(P27_dry, 1),
    'Error of the method in back-test: ±%s %% (1 in 3 years outside)' % fr(RM_MODEL, 0)])]
for x, t, c, ls in bx:
    box(s, x, 1.95, 3.9, 3.1, t, ls, c, 11)
s.text(4.33, 3.2, 0.4, 0.5, [para(run('×', 28, True, color=GREY), algn='ctr')])
s.text(8.6, 3.2, 0.4, 0.5, [para(run('=', 28, True, color=GREY), algn='ctr')])
TY_mean = st.mean(YLD3)
sens = [('Productive area ±1 %', '±%s' % fr(P27 * 0.01, 2)),
        ('One town more or less with trigger rain (±%s %%)' % fr(B1, 1), '±%s' % fr(BASE27 * B1 / 100, 2)),
        ('Trend yield = mean, not median, of 2024–2026', '%s' % fr(AREA27 * TY_mean * (1 + W26 / 100) / 1e6 - P27, 2, True)),
        ('Dry Oct–Nov, El Niño + positive IOD (%s %%)' % fr(EN_IOD, 1), '%s' % fr(P27_dry - P27, 2, True))]
label(s, 0.45, 5.3, 12.4, 'What moves the 2027/28 number (M bags, from %s)' % fr(P27, 2), 11)
s.table(0.45, 5.65, [2.35, 0.75] * 4, 0.6, [[c for nm, v in sens for c in (td(nm, 9), td(v, 10.5, 'ctr', b=True, color=(BAD if v.startswith('−') else INK)))]])
slides.append(s)

# ======================================================================
# 3. area: coffee vs cocoa, year over year
# ======================================================================
s = Slide()
cc0, cc1 = cagr(A['cocoa'], 2000, 2012), cagr(A['cocoa'], 2012, 2024)
cf0, cf1 = cagr(A['coffee'], 2000, 2012), cagr(A['coffee'], 2012, 2024)
pl0, pl1 = cagr(PLANT, 2004, 2012), cagr(PLANT, 2012, 2023)
header(s, 'Area: coffee and cocoa move in opposite directions', [
    'Year over year, coffee area and cocoa area are negatively correlated: r = %s (%s, %d years, FAO break years left out)' % (fr(r_area, 2), pfmt(p_area), len(opp)),
    'They moved in opposite directions in %d of %d years. 2000–2012: cocoa +%s %%/yr, robusta −%s %%/yr. 2012–2024: cocoa %s %%/yr, robusta flat' % (n_opp, len(opp), fr(cc0, 1), fr(-pl0, 1), fr(cc1, 1)),
    'It is not a common trend: it is the same land and the same farmers switching crops. A gain for cocoa is a loss for coffee, and back'],
    'FAOSTAT QCL, area harvested, Indonesia (coffee = arabica + robusta). Ministry of Agriculture (Ditjenbun): robusta planted area, 2004–2023. '
    'Cocoa 2003, 2006 and 2008 left blank: FAO series breaks (+24 %, −22 %, +54 %). r without the breaks; permutation test.')
cats = [str(y) for y in Y[1:25]]
bars = [{'name': 'Coffee area (FAO)', 'color': COF, 'values': [None if v is None else round(v, 1) for v in ac_c[1:25]], 'lfmt': ';;;'},
        {'name': 'Cocoa area (FAO)', 'color': COC, 'values': [None if v is None else round(v, 1) for v in ak_c[1:25]], 'lfmt': ';;;'}]
lines = [{'name': 'Robusta planted area (ministry)', 'color': ROB, 'values': [None if v is None else round(v, 1) for v in ap[1:25]], 'dash': 'solid', 'width': 2.25}]
label(s, 0.4, 1.72, 8.4, 'Area, change on the year before (%)', 11)
s.chart(0.3, 2.0, 8.6, 4.95, yield_chart(cats, bars, lines, mn=-10, mx=15, unit=5, fmt='+0;-0;0', layout=(0.06, 0.04, 0.93, 0.8), overlap=0, gap=40))
rows = [[th('Average change per year'), th('2000–2012', algn='ctr'), th('2012–2024', algn='ctr')],
        [td('Cocoa area (FAO)'), td(fr(cc0, 1, True) + ' %', algn='ctr', color=GOOD), td(fr(cc1, 1, True) + ' %', algn='ctr', color=BAD)],
        [td('Coffee area (FAO)'), td(fr(cf0, 1, True) + ' %', algn='ctr'), td(fr(cf1, 1, True) + ' %', algn='ctr')],
        [td('Robusta planted (ministry)'), td(fr(pl0, 1, True) + ' %*', algn='ctr', color=BAD), td(fr(pl1, 2, True) + ' %**', algn='ctr')],
        [td('Coffee ÷ cocoa revenue per ha'), td('0.39–0.98', algn='ctr'), td('0.93–1.88', algn='ctr')]]
s.table(9.1, 2.05, [1.95, 1.0, 1.0], 0.36, rows)
s.text(9.1, 3.9, 3.95, 0.3, [para(run('* 2004–2012   ** 2012–2023', 8, color=GREY))])
box(s, 9.1, 4.3, 3.95, 1.75, 'How to read it', [
    'r = −1: they always move against each other; 0: no link.',
    'r = %s with a %s %% chance of luck (%s).' % (fr(r_area, 2), fr(100 * p_area, 1), pfmt(p_area)),
    'Robusta planted vs cocoa: r = %s (%s).' % (fr(r_area_pl, 2), pfmt(p_area_pl)),
    'The switch came in 2012, when a hectare of coffee started to pay more than a hectare of cocoa (slide 6).'], NAVY, 9.5)
slides.append(s)

# ======================================================================
# 4. revenue per ha: year over year
# ======================================================================
s = Slide()
header(s, 'Revenue per hectare: coffee and cocoa rise and fall together, because prices do', [
    'Revenue per ha, year over year: r = %s (%s, 2001–2026). Farm-gate prices: r = %s (%s). Yields: r = %s (%s), no link' % (
        fr(r_rev, 2, True), pfmt(p_rev), fr(r_px, 2, True), pfmt(p_px), fr(r_yl, 2, True), pfmt(p_yl)),
    'Coffee revenue swings are %s %% price, %s %% yield. Cocoa: %s %% price, %s %% yield (cocoa yields fell from 850 kg/ha in 2006 to 350–480 since 2015)' % (
        fr(sh_cof, 0), fr(100 - sh_cof, 0), fr(sh_coc, 0), fr(100 - sh_coc, 0)),
    'So the link is the price (same rupiah, same commodity cycle), not the yield and not the area'],
    'Revenue per ha = FAO producer price (USD/t) × FAO yield, Indonesia. Hatched: 2025 estimated with the FAO producer price index, 2026 with Jan–Aug world prices '
    '(World Bank), yields held at 2024. Price and yield split on 2001–2024 (log changes).')
cats = [str(y) for y in Y[1:]]
fills_c = [hatch(COF) if y >= 2025 else None for y in Y[1:]]
fills_k = [hatch(COC) if y >= 2025 else None for y in Y[1:]]
bars = [{'name': 'Coffee revenue per ha', 'color': COF, 'values': [round(v, 1) for v in rc[1:]], 'fills': fills_c, 'lfmt': ';;;'},
        {'name': 'Cocoa revenue per ha', 'color': COC, 'values': [round(v, 1) for v in rk[1:]], 'fills': fills_k, 'lfmt': ';;;'}]
label(s, 0.4, 1.72, 8.4, 'Revenue per hectare, change on the year before (%)', 11)
s.chart(0.3, 2.0, 8.6, 4.95, yield_chart(cats, bars, (), mn=-50, mx=100, unit=25, fmt='+0;-0;0', layout=(0.06, 0.04, 0.93, 0.8), overlap=0, gap=40))
rows = [[th('Year-over-year link, coffee vs cocoa'), th('r', algn='ctr'), th('chance', algn='ctr')],
        [td('Revenue per ha, 2001–2026'), td(fr(r_rev, 2, True), algn='ctr', b=True), td(pfmt(p_rev), algn='ctr')],
        [td('Revenue per ha, 2001–2024 (FAO only)'), td(fr(r_rev24, 2, True), algn='ctr'), td(pfmt(p_rev24), algn='ctr')],
        [td('Farm-gate price, 2001–2024'), td(fr(r_px, 2, True), algn='ctr', b=True), td(pfmt(p_px), algn='ctr')],
        [td('Yield, 2001–2024'), td(fr(r_yl, 2, True), algn='ctr'), td(pfmt(p_yl), algn='ctr')]]
s.table(9.1, 2.05, [2.35, 0.7, 0.9], 0.36, rows)
box(s, 9.1, 4.0, 3.95, 2.3, 'What drives revenue per ha', [
    run('Coffee: ', 9.5, True, color=COF) + run('price %s %%, yield %s %%. Coffee yields are stable (±5 %% a year), prices are not (±16 %%).' % (fr(sh_cof, 0), fr(100 - sh_cof, 0)), 9.5, color=INK),
    run('Cocoa: ', 9.5, True, color='B07A1A') + run('price %s %%, yield %s %%. Cocoa yields swing by ±14 %% a year and fell from 850 kg/ha (2006) to 350–480.' % (fr(sh_coc, 0), fr(100 - sh_coc, 0)), 9.5, color=INK),
    'For the area forecast, follow prices in rupiah: they carry most of the revenue signal.'], NAVY, 9.5)
slides.append(s)

# ======================================================================
# 5. common or uncommon?
# ======================================================================
s = Slide()
header(s, 'Is it common? Same direction only half the time; big moves together are rare', [
    'Coffee and cocoa revenue moved in the same direction in %d of %d years: no better than a coin toss (%s)' % (n_same, len(same), pfmt(p_same)),
    'But the big moves come together: both above +30 %% only in %s. 2024–2025 is the largest joint boom since 2000' % ', '.join(map(str, big_both)),
    '2026 (estimated): both fall, cocoa −43 %, coffee −20 % → coffee pays about 1.4× cocoa per ha again, as in 2019–2023'],
    'Same data as slide 4. Chance of %d or more same-direction years by luck: permutation of years (4,000 draws). 2025–2026 estimated.' % n_same)
pts = {'same': [], 'opp': [], 'recent': []}
for y, a, b in same:
    k = 'recent' if y >= 2024 else ('same' if a * b > 0 else 'opp')
    pts[k].append((a, b, str(y)))
ser = [{'name': 'Same direction', 'color': GOOD, 'xs': [round(a, 1) for a, _, _ in pts['same']], 'ys': [round(b, 1) for _, b, _ in pts['same']], 'labels': [l for _, _, l in pts['same']]},
       {'name': 'Opposite directions', 'color': '8C969B', 'xs': [round(a, 1) for a, _, _ in pts['opp']], 'ys': [round(b, 1) for _, b, _ in pts['opp']], 'labels': [l for _, _, l in pts['opp']]},
       {'name': '2024–2026', 'color': RED, 'xs': [round(a, 1) for a, _, _ in pts['recent']], 'ys': [round(b, 1) for _, b, _ in pts['recent']], 'labels': [l for _, _, l in pts['recent']]}]
label(s, 0.4, 1.72, 7.5, 'Revenue per ha, change on the year before: coffee (across) vs cocoa (up)', 11)
s.chart(0.3, 2.0, 7.6, 4.95, scatter_chart(ser, -30, 60, 10, -50, 100, 25, xfmt='+0"%";-0"%";0"%"', yfmt='+0"%";-0"%";0"%"', legend=True))
both_up = sum(1 for _, a, b in same if a > 0 and b > 0)
both_dn = sum(1 for _, a, b in same if a < 0 and b < 0)
rows = [[th('Revenue per ha, 2001–2026'), th('years', algn='ctr')],
        [td('Both up'), td(str(both_up), algn='ctr')],
        [td('Both down'), td(str(both_dn), algn='ctr')],
        [td('Coffee up, cocoa down'), td(str(sum(1 for _, a, b in same if a > 0 > b)), algn='ctr')],
        [td('Coffee down, cocoa up'), td(str(sum(1 for _, a, b in same if a < 0 < b)), algn='ctr')],
        [td('Both above +30 %', b=True), td(', '.join(map(str, big_both)), algn='ctr', b=True)]]
s.table(8.2, 2.05, [2.9, 1.95], 0.34, rows)
box(s, 8.2, 4.25, 4.85, 2.35, 'So what', [
    'Small moves: each crop has its own story (cocoa yields, coffee weather).',
    'Big moves: one story, the world commodity cycle and the rupiah. 2024–2025 was one of these: both crops paid a record, so neither gained land on the other.',
    '2026 breaks the tie: cocoa prices fell twice as fast as robusta. On the rule of slide 6, that favours coffee planting from 2027 (area effect from 2029–2030).'], NAVY, 9.5)
slides.append(s)

# ======================================================================
# 6. relative revenue level -> robusta area
# ======================================================================
s = Slide()
header(s, 'What moves the area: which crop paid more, 1 to 3 years before', [
    'When coffee paid less than cocoa the year before, robusta area fell %s %%/yr (%d years). When it paid as much or more: %s %%/yr (%d years)' % (
        fr(st.mean(lo_reg), 1), len(lo_reg), fr(st.mean(hi_reg), 1), len(hi_reg)),
    'Coffee ÷ cocoa revenue vs robusta area growth: r = %s one year later, %s two years, %s three years' % (fr(lags[1][0], 2, True), fr(lags[2][0], 2, True), fr(lags[3][0], 2, True)),
    'The one-year change in revenue does not predict area (r = %s): farmers react to a lasting gap, not to one good year. Caution: 2 regimes, few years' % fr(r_drel, 2, True)],
    'Revenue per ha: FAOSTAT price × yield (2025–2026 estimated). Robusta planted area: Ministry of Agriculture (Ditjenbun), 2004–2023. '
    'Regime colour uses the ratio of the year before. With only 19 years and one switch (2012), the link is a regime, not a year-by-year rule.')
yrs6 = list(range(2004, 2027))
cats = [str(y) for y in yrs6]
label(s, 0.4, 1.72, 8.4, 'Revenue per ha, coffee ÷ cocoa (1 = same revenue)', 11)
s.chart(0.3, 1.95, 8.6, 2.45, multi_line(cats, [
    {'name': 'Coffee ÷ cocoa', 'values': [round(rel_rev[Y.index(y)], 2) for y in yrs6], 'color': COF, 'width': 2.5},
    {'name': 'Equal revenue', 'values': [1.0] * len(yrs6), 'color': GREY, 'width': 1.0, 'dash': 'dash'}], mn=0, mx=2, unit=0.5, fmt='0.0', legend=False))
g = [ap[Y.index(y)] for y in yrs6]
cols = [None if v is None else (BAD if rel_rev[Y.index(y) - 1] < 1 else GOOD) for y, v in zip(yrs6, g)]
label(s, 0.4, 4.4, 8.4, 'Robusta planted area, change on the year before (%)', 11)
s.chart(0.3, 4.65, 8.6, 2.35, combo_bar(cats, [{'name': 'Robusta area', 'color': LIGHT, 'values': [None if v is None else round(v, 1) for v in g], 'point_colors': cols}],
                                        mn=-8, mx=4, unit=4, fmt='+0;-0;0', label_fmt='+0.0;-0.0;0.0', legend=False, gap=40, label_sz=7))
rows = [[th('Coffee ÷ cocoa, year before'), th('years', algn='ctr'), th('robusta area', algn='ctr')],
        [td('below 1 (cocoa pays more)', color=BAD), td(str(len(lo_reg)), algn='ctr'), td(fr(st.mean(lo_reg), 1, True) + ' %/yr', algn='ctr', color=BAD, b=True)],
        [td('1 or more (coffee pays more)', color=GOOD), td(str(len(hi_reg)), algn='ctr'), td(fr(st.mean(hi_reg), 1, True) + ' %/yr', algn='ctr', color=GOOD, b=True)]]
s.table(9.1, 2.05, [2.15, 0.7, 1.1], 0.36, rows)
rows = [[th('Test'), th('r', algn='ctr'), th('chance', algn='ctr')],
        [td('Ratio 1 year before'), td(fr(lags[1][0], 2, True), algn='ctr', b=True), td(pfmt(lags[1][1]), algn='ctr')],
        [td('Ratio 2 years before'), td(fr(lags[2][0], 2, True), algn='ctr'), td(pfmt(lags[2][1]), algn='ctr')],
        [td('Ratio 3 years before'), td(fr(lags[3][0], 2, True), algn='ctr'), td(pfmt(lags[3][1]), algn='ctr')],
        [td('Change in ratio, 1 year before'), td(fr(r_drel, 2, True), algn='ctr'), td(pfmt(p_drel), algn='ctr')]]
s.table(9.1, 3.35, [2.15, 0.7, 1.1], 0.34, rows)
box(s, 9.1, 5.2, 3.95, 1.45, 'Reading for 2027', [
    'Coffee pays more than cocoa since 2012 (1.02 in 2025, ~1.4 in 2026): the rule says no loss of robusta area.',
    'New plantings of 2026–2027 only produce from 2029.'], NAVY, 9.5)
slides.append(s)

# ======================================================================
# 7. link matrix: which links are real
# ======================================================================
s = Slide()
LINKS = [('Coffee area vs cocoa area (YoY)', r_area, p_area, 'Real: they compete for land', BAD),
         ('Coffee vs cocoa revenue per ha (YoY)', r_rev, p_rev, 'Real, via prices', GOOD),
         ('Coffee vs cocoa farm-gate price (YoY)', r_px, p_px, 'Real: same rupiah, same cycle', GOOD),
         ('Coffee vs cocoa yield (YoY)', r_yl, p_yl, 'No link', LIGHT),
         ('Coffee ÷ cocoa revenue → robusta area, 1 yr later', lags[1][0], lags[1][1], 'Real, as a regime', GOOD),
         ('Change in that ratio → robusta area, 1 yr later', r_drel, p_drel, 'No link', LIGHT),
         ('Coffee area vs coffee yield (YoY)', r_ay, p_ay, 'No link', LIGHT),
         ('Robusta planted vs robusta yield (YoY)', r_py, p_py, 'No link', LIGHT)]
header(s, 'Which links are real: area and yield are two separate engines', [
    'Real links: coffee and cocoa areas trade off (r = %s); prices and so revenues move together (r = %s); area follows the revenue gap with a lag' % (fr(r_area, 2), fr(r_px, 2, True)),
    'No link between area and yield: new or abandoned land does not show in the yield (r = %s and %s)' % (fr(r_ay, 2, True), fr(r_py, 2, True)),
    'So the forecast can take the two separately: area from the land and revenue history, yield from the weather'],
    'r = correlation (−1 to +1). Chance = permutation test (4,000 draws): share of random reorderings of the years that give a link as strong. '
    'Below 5 % = unlikely to be luck. Data as slides 3–6.')
cats = [l[0] for l in LINKS][::-1]
vals = [round(l[1], 2) for l in LINKS][::-1]
cols = [(l[4] if l[2] < 0.1 else LIGHT) for l in LINKS][::-1]
label(s, 0.4, 1.72, 7.6, 'Correlation r (bar) and verdict', 11)
s.chart(0.3, 1.95, 7.6, 5.0, hbar(cats, [{'name': 'r', 'color': LIGHT, 'values': vals, 'point_colors': cols}], -1, 1, 0.5, '+0.00;-0.00;0.00'))
rows = [[th('Link'), th('r', algn='ctr'), th('chance', algn='ctr'), th('verdict')]]
for name, r_, p_, v, c in LINKS:
    rows.append([td(name, 8.5), td(fr(r_, 2, True), 8.5, 'ctr', b=True), td(pfmt(p_), 8.5, 'ctr'), td(v, 8.5, color=(INK if p_ < 0.1 else GREY), b=p_ < 0.1)])
s.table(8.05, 2.0, [2.35, 0.55, 0.8, 1.35], 0.5, rows)
slides.append(s)

# ======================================================================
# 8. 2027 productive area
# ======================================================================
s = Slide()
PCR = {int(k): v for k, v in S['permanent_crops_kha'].items()}
g1 = (PCR[2010] - PCR[2000]) / 10 / 1000
g2 = (PCR[2020] - PCR[2010]) / 10 / 1000
g3 = (PCR[2024] - PCR[2020]) / 4 / 1000
pa_yrs = list(range(2013, 2028))
pa = [float(FD[y]['surface_productive_ha']) for y in pa_yrs]
est = [FD[y]['surface_productive_estimee'] == 'oui' for y in pa_yrs]
gr = 100 * ((pa[pa_yrs.index(2022)] / pa[pa_yrs.index(2013)]) ** (1 / 9) - 1)
header(s, '2027 productive area is already fixed: %s ha (+%s %%)' % (format(round(AREA27), ','), fr(100 * (AREA27 / AREA26 - 1), 1)), [
    'Productive robusta area grew %s %%/yr from 2013 to 2022 (ministry). Same pace applied to 2023–2027 → %s ha in 2027' % (fr(gr, 2, True), format(round(AREA27), ',')),
    'A tree planted in 2026 bears from 2028–2029: the 2027 harvest area was decided by plantings up to 2024. Error ±1 % ≈ ±0.1 M bags',
    'Land is closing: permanent crops in Indonesia grew +%s M ha/yr in 2000–2010, +%s in 2010–2020, +%s in 2020–2024. Parks are now enforced (≈50,000 ha seized in Lampung Barat, 2025)' % (fr(g1, 2), fr(g2, 2), fr(g3, 2))],
    'Ministry of Agriculture (Ditjenbun / Outlook Kopi): productive robusta area 2013–2023; 2023–2027 hatched = extrapolated at the 2013–2022 rate. '
    'FAOSTAT land use: permanent crops, Indonesia (oil palm, rubber, coffee, cocoa, coconut…). Satgas PKH seizure: press, 2025.')
label(s, 0.4, 1.72, 7.4, 'Productive robusta area (thousand ha)', 11)
s.chart(0.3, 1.95, 7.6, 5.0, yield_chart([str(y) for y in pa_yrs], [{'name': 'Productive area', 'color': ROB, 'values': [round(v / 1000, 1) for v in pa],
                                                                     'fills': [hatch(ROB) if e_ else None for e_ in est], 'lfmt': '0'}],
                                      (), mn=640, mx=720, unit=20, fmt='0', label_sz=8, legend=False, layout=(0.08, 0.04, 0.9, 0.84), overlap=0, gap=40))
label(s, 8.2, 1.72, 4.8, 'Permanent crops, net new land (M ha per year)', 11)
s.chart(8.1, 1.95, 4.95, 2.6, combo_bar(['2000–2010', '2010–2020', '2020–2024'], [{'name': 'M ha/yr', 'color': GREY, 'values': [round(g1, 2), round(g2, 2), round(g3, 2)],
                                                                                   'point_colors': ['7F7F7F', 'A6A6A6', BAD]}], mn=0, mx=0.7, unit=0.2, fmt='0.0', label_fmt='0.00', legend=False, gap=60, label_sz=10))
box(s, 8.1, 4.75, 4.95, 1.6, 'Calculation', [
    '2026 productive area: %s ha' % format(round(AREA26), ','),
    '× (1 + %s %%) = %s ha in 2027' % (fr(100 * (AREA27 / AREA26 - 1), 2), format(round(AREA27), ',')),
    'If the recent high prices had added 1 % of new productive area by 2027 (unlikely before 2029), production would be +0.1 M bags.'], NAVY, 9.5)
slides.append(s)

# ======================================================================
# 9. a normal year: flowering, trigger rain
# ======================================================================
s = Slide()
NM = S['normal']
MN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
T5 = ['pagar_alam', 'lahat', 'muaradua', 'liwa', 'kepahiang']
TN = {'pagar_alam': 'Pagar Alam (highland)', 'lahat': 'Lahat (foothills)', 'muaradua': 'Muaradua (lowland)', 'liwa': 'Liwa (Lampung)', 'kepahiang': 'Kepahiang (highland)'}
r26 = [st.mean(NM['rain2026_mm'][t][m] for t in T5) for m in range(8)]
TRG = S['triggers']
from datetime import date, timedelta


def doy_str(d):
    return (date(2001, 1, 1) + timedelta(d - 1)).strftime('%d %b')


trows = []
for t in T5:
    ds = [v for k, v in TRG[t].items() if v and 1981 <= int(k) <= 2025]
    nyr = sum(1 for k in TRG[t] if 1981 <= int(k) <= 2025)
    doy = sorted(date.fromisoformat(d).timetuple().tm_yday for d in ds)
    v26 = TRG[t].get('2026')
    trows.append((TN[t], len(ds), nyr, doy_str(doy[len(doy) // 2]), doy_str(doy[len(doy) // 4]), doy_str(doy[3 * len(doy) // 4]),
                  date.fromisoformat(v26).strftime('%d %b') if v26 else 'not yet'))
cnt = [sum(1 for t in T5 if TRG[t].get(str(y))) for y in range(1981, 2026)]
dry = st.mean(NM['mean_mm'][5:9])
wet = st.mean(NM['mean_mm'][i] for i in (0, 1, 2, 3, 10, 11))
header(s, 'What a normal year looks like: dry Jun–Sep, trigger rain in Jul–Aug', [
    'Normal rain: %d mm/month in the dry season (Jun–Sep) against %d mm/month in Nov–Apr. Lampung and the lowland are drier (Liwa: 65 mm in August)' % (round(dry), round(wet)),
    'Flowering needs a dry spell (11 days < 0.6 mm/day) then one rainy day > 10 mm. In a normal year this happens in %s of 5 towns (median %d), in each town 1 year in 2' % (fr(st.mean(cnt), 1), st.median(cnt)),
    'Normal date: 18 Jul (Liwa) to 17 Aug (Lahat). 2026: 22 Jul and 16 Aug in 4 towns, on time; Liwa not yet. Harvest comes 9–11 months after flowering (Apr–Aug)'],
    'NASA POWER daily rainfall (PRECTOTCORR), 1991–2020 normals per month; 2026 = January–August observed. Trigger: first day > 10 mm after 11 days averaging < 0.6 mm/day, June–October, 1981–2025.')
cats = MN
label(s, 0.4, 1.72, 7.4, 'Rainfall per month, mm', 11)
s.chart(0.3, 1.95, 7.5, 5.0, combo_bar(cats, [{'name': 'Normal, 5-town mean (1991–2020)', 'color': '9DC3E6', 'values': [round(v) for v in NM['mean_mm']],
                                              'point_colors': ['F4B183' if 5 <= i <= 8 else None for i in range(12)]}],
                                       lines=[{'name': 'Liwa normal (driest)', 'color': EN, 'values': [round(v) for v in NM['clim_mm']['liwa']], 'dash': 'dash', 'width': 1.5},
                                              {'name': 'Pagar Alam normal (wettest)', 'color': NAVY, 'values': [round(v) for v in NM['clim_mm']['pagar_alam']], 'dash': 'dash', 'width': 1.5},
                                              {'name': '2026, 5-town mean', 'color': RED, 'values': [round(v) for v in r26] + [None] * 4, 'dash': 'solid', 'width': 2.5}],
                                       mn=0, mx=400, unit=100, fmt='0', label_fmt='0', legend=True, gap=40, label_sz=8))
s.text(3.25, 2.1, 2.5, 0.3, [para(run('dry season = flowering window', 9, True, color='C55A11'), algn='ctr')])
rows = [[th('Town', 8.5), th('trigger years', 8.5, 'ctr'), th('normal date', 8.5, 'ctr'), th('half of years', 8.5, 'ctr'), th('2026', 8.5, 'ctr')]]
for name, n, ny, med, q1, q3, v26 in trows:
    rows.append([td(name, 8.5), td('%d of %d' % (n, ny), 8.5, 'ctr'), td(med, 8.5, 'ctr', b=True), td('%s – %s' % (q1, q3), 8.5, 'ctr'),
                 td(v26, 8.5, 'ctr', color=(GOOD if v26 != 'not yet' else BAD), b=True)])
s.table(8.0, 2.0, [1.65, 0.8, 0.8, 1.15, 0.65], 0.36, rows)
dist = {k: cnt.count(k) for k in range(6)}
rows = [[th('Towns with a trigger in a year', 8.5)] + [th(str(k), 8.5, 'ctr') for k in range(6)],
        [td('Years, 1981–2025', 8.5)] + [td(str(dist[k]), 8.5, 'ctr', fill=('DDEBF7' if k == TRIG26 else None), b=k == TRIG26) for k in range(6)]]
s.table(8.0, 4.35, [2.05] + [0.5] * 6, 0.32, rows)
box(s, 8.0, 5.2, 5.05, 1.55, 'Normal year, in numbers', [
    '%d mm/month Jun–Sep · trigger in 2–3 towns · Jul–Aug · 15–20 mm on the trigger day · max temperature peaks at 29 °C in Sep–Oct' % round(dry),
    '2026: 4 towns (only %d years of 45 had 4) · rain Jun–Aug %d %% of normal · hotter (%s °C in Jul–Sep)' % (dist[4], round(100 * st.mean(r26[5:8]) / st.mean(NM['mean_mm'][5:8])), fr(st.mean(OBS26['tmax_anom'].values()), 1, True))], NAVY, 9.5)
slides.append(s)

# ======================================================================
# 10. which weather matters
# ======================================================================
s = Slide()
order = sorted(FEAT, key=lambda f: abs(FR[f[0]]['r']))
cats = [FR[k]['name'] for k, _ in order]
header(s, 'Which weather matters: 18 factors tested on 45 crops (1982–2026)', [
    'Strongest: flowering trigger rain (r = %s, %s). The more towns get their dry spell then trigger rain, the bigger the crop' % (fr(FR['trig']['r'], 2, True), pfmt(FR['trig']['p'])),
    'Too much rain in Jun–Oct hurts (r = %s): no dry spell, no synchronised flowering. Rain in Aug–Oct matters most year over year (r = %s)' % (fr(FR['rain_JJASO']['r'], 2), fr(FR['rain_ASO']['ry'], 2)),
    'ENSO alone (r = %s) and harvest rain (r = %s) explain nothing. The previous crop does not predict the level, only the rebound (slide 13)' % (fr(FR['oni']['r'], 2, True), fr(FR['harv_rain']['r'], 2, True))],
    'Crop N = USDA robusta production, marketing year N/N+1; weather of the flowering year N−1 (bean filling Dec–Mar, harvest Apr–Aug of year N). Vs trend = production vs median of crops N−3..N+3. '
    'Dark bars: chance < 5 % (permutation test). NASA POWER, 5 towns.')
ser = [{'name': 'vs trend', 'color': LIGHT, 'values': [round(FR[k]['r'], 2) for k, _ in order], 'point_colors': [(NAVY if FR[k]['p'] < 0.05 else 'B4C7E7') for k, _ in order]},
       {'name': 'year over year', 'color': LIGHT, 'values': [round(FR[k]['ry'], 2) for k, _ in order], 'point_colors': [(EN if FR[k]['py'] < 0.05 else 'F8CBAD') for k, _ in order]}]
label(s, 0.4, 1.72, 8.5, 'Correlation with the crop: vs trend (blue) and year over year (orange); dark = significant', 11)
s.chart(0.3, 1.95, 8.6, 5.05, hbar(cats, ser, -0.8, 0.6, 0.2, '+0.00;-0.00;0.00'))
top = [('trig', 'Trigger towns'), ('rain_JJASO', 'Rain Jun–Oct'), ('dry_JJAS', 'Rain Jun–Sep'), ('rain_ASO', 'Rain Aug–Oct'), ('fill_rain', 'Rain Dec–Mar'),
       ('tmax_JASO', 'Max temp. Jul–Oct'), ('dmi', 'IOD'), ('oni', 'ENSO'), ('prev', 'Previous crop')]
rows = [[th('Factor', 8.5), th('vs trend', 8.5, 'ctr'), th('year over year', 8.5, 'ctr')]]
for k, nme in top:
    f = FR[k]
    rows.append([td(nme, 8.5), td('%s (%s)' % (fr(f['r'], 2, True), pfmt(f['p'])), 8.5, 'ctr', b=f['p'] < 0.05),
                 td('%s (%s)' % (fr(f['ry'], 2, True), pfmt(f['py'])), 8.5, 'ctr', b=f['py'] < 0.05)])
s.table(9.1, 2.0, [1.25, 1.35, 1.35], 0.32, rows)
box(s, 9.1, 5.3, 3.95, 1.2, 'Honest limit', [
    'The best single factor explains %d %% of the swings (r² = %s). The weather tells the direction more often than not, not the exact number.' % (round(100 * FR['trig']['r'] ** 2), fr(FR['trig']['r'] ** 2, 2))], NAVY, 9.5)
slides.append(s)

# ======================================================================
# 11. thresholds: trigger towns and Jun-Oct rain
# ======================================================================
s = Slide()
tb = bins_of(ROWS, 'trig', [(0, 1, '0 towns'), (1, 3, '1–2 towns'), (3, 6, '3–5 towns')])
rb = bins_of(ROWS, 'rain_JJASO', [(0, 50, '< 50 %'), (50, 80, '50–80 %'), (80, 120, '80–120 %'), (120, 150, '120–150 %'), (150, 999, '> 150 %')])
combo_good = [r for r in ROWS if r['trig'] >= 3 and r['rain_JJASO'] <= 120]
combo_bad = [r for r in ROWS if r['trig'] <= 2 and r['rain_JJASO'] > 120]
header(s, 'The two thresholds: trigger rain in 3+ towns, and Jun–Oct rain below 150 %', [
    'Trigger in 3–5 towns: crop %s %% vs trend (%d of %d up). No trigger at all: %s %% (%d of %d down: 1995, 2011, 2023…)' % (
        fr(tb[2]['mean'], 1, True), tb[2]['n'] - tb[2]['down'], tb[2]['n'], fr(tb[0]['mean'], 1), tb[0]['down'], tb[0]['n']),
    'Jun–Oct rain above 150 %% of normal: %s %% vs trend, %d of %d crops down. Between 80 and 120 %%: %s %%' % (fr(rb[4]['mean'], 1), rb[4]['down'], rb[4]['n'], fr(rb[2]['mean'], 1, True)),
    'Both good (3+ towns, rain ≤ 120 %%): %s %% (%d years, %d up). Both bad (≤ 2 towns, rain > 120 %%): %s %% (%d years). 2026: 4 towns, %s %% → good side' % (
        fr(st.mean(r['anom'] for r in combo_good), 1, True), len(combo_good), sum(r['anom'] > 0 for r in combo_good),
        fr(st.mean(r['anom'] for r in combo_bad), 1), len(combo_bad), fr(F26['rain_JJASO'], 0))],
    'Mean of production vs trend (median of crops N−3..N+3), USDA 1982–2026, grouped by the weather of the flowering year. Navy bar = where the 2026 flowering sits '
    '(Jun–Oct rain: observed to 19 Sep, normal after). n = number of crops.')
bin_chart(s, 0.4, 2.3, 5.2, 4.6, tb, 2, 'Crop vs trend, by towns with trigger rain', -12, 8, 4)
bin_chart(s, 5.9, 2.3, 7.1, 4.6, rb, 1, 'Crop vs trend, by Jun–Oct rain (% of normal)', -12, 8, 4)
slides.append(s)

# ======================================================================
# 12. heat and ENSO
# ======================================================================
s = Slide()
tb2 = bins_of(ROWS, 'tmax_JASO', [(-9, -0.7, '≤ −0.7 °C'), (-0.7, 0, '−0.7–0'), (0, 0.7, '0–+0.7'), (0.7, 1.2, '+0.7–1.2'), (1.2, 9, '> +1.2 °C')])
ob = bins_of(ROWS, 'oni', [(-9, -1.0, 'La Niña ≤ −1'), (-1.0, -0.5, 'La Niña weak'), (-0.5, 0.5, 'Neutral'), (0.5, 1.5, 'El Niño'), (1.5, 9, 'El Niño ≥ 1.5')])
iodp = [r for r in ROWS if r['dmi'] is not None and r['dmi'] >= 0.4]
ob.append(dict(name='IOD +', n=len(iodp), mean=st.mean(r['anom'] for r in iodp), down=sum(r['anom'] < 0 for r in iodp)))
ob.append(dict(name='El Niño + IOD +', n=len(ENIOD), mean=EN_IOD, down=sum(r['anom'] < 0 for r in ENIOD)))
t26 = F26['tmax']
header(s, 'Heat and ENSO: weak on their own, bearish together', [
    'Max temperature Jul–Oct: a cool season hurts (≤ −0.7 °C: %s %%, %d of %d down, wet years). 0 to +1.2 °C is best (%s / %s %%); above +1.2 °C it turns negative' % (
        fr(tb2[0]['mean'], 1), tb2[0]['down'], tb2[0]['n'], fr(tb2[2]['mean'], 1, True), fr(tb2[3]['mean'], 1, True)),
    'ENSO alone: every bin within ±3.5 %%. Strong El Niño (ONI ≥ 1.5): %s %%, 4 crops. El Niño with a positive IOD: %s %%, %d of %d down (1995 −19 %%, 2007 −12 %%)' % (
        fr(ob[4]['mean'], 1), fr(EN_IOD, 1), ob[-1]['down'], ob[-1]['n']),
    '2026: heat +%s °C (observed to 19 Sep, normal after), strong El Niño and a positive IOD likely (BoM, 15 Sep) → the risk to watch is a dry Oct–Nov' % fr(t26, 1)],
    'Temperature: NASA POWER T2M_MAX, 5 towns, anomaly vs 1991–2020. ENSO: NOAA CPC ONI, Aug–Nov mean of the flowering year. IOD: DMI (NOAA PSL, HadISST), Aug–Nov, positive ≥ +0.4. Navy bars = where 2026 sits.')
bin_chart(s, 0.4, 2.3, 5.9, 4.6, tb2, 2 if t26 < 0.7 else 3, 'Crop vs trend, by max temperature Jul–Oct', -8, 8, 4)
bin_chart(s, 6.6, 2.3, 6.45, 4.6, ob, [4, 6], 'Crop vs trend, by ENSO and IOD of the flowering year', -8, 8, 4)
slides.append(s)

# ======================================================================
# 13. on / off years
# ======================================================================
s = Slide()
alt = sum(1 for i in range(1, len(ROWS)) if ROWS[i]['yoy'] * ROWS[i - 1]['yoy'] < 0)
hi_prev = [r for r in ROWS if r['prev'] is not None and r['prev'] > 8]
lo_prev = [r for r in ROWS if r['prev'] is not None and r['prev'] < -8]
nm_prev = [r for r in ROWS if r['prev'] is not None and -8 <= r['prev'] <= 8]
rnd = random.Random(3)
sims = []
yy = [r['yoy'] for r in ROWS]
for _ in range(4000):
    rnd.shuffle(yy)
    sims.append(sum(1 for i in range(1, len(yy)) if yy[i] * yy[i - 1] < 0))
p_alt = sum(1 for v in sims if v >= alt) / len(sims)
header(s, 'No on/off cycle in Indonesia, but a big crop is followed by a smaller one', [
    'Up, down, up, down would give 44 changes of direction in 45 crops. Indonesia has %d, random order gives %s on average (%s): no biennial cycle, unlike Brazil' % (alt, fr(st.mean(sims), 1), pfmt(p_alt)),
    'After a crop more than 8 %% above trend, the next is %s %% on the year (%d cases). After a crop more than 8 %% below: %s %% (%d cases)' % (
        fr(st.mean(r['yoy'] for r in hi_prev), 1), len(hi_prev), fr(st.mean(r['yoy'] for r in lo_prev), 1, True), len(lo_prev)),
    'That is a return to trend, not a cycle: vs trend the next crop is %s %% and %s %%. The forecast starts from the trend, so no extra correction' % (
        fr(st.mean(r['anom'] for r in hi_prev), 1, True), fr(st.mean(r['anom'] for r in lo_prev), 1))],
    'USDA PSD robusta production, 1982/83–2026/27. Change of direction = the sign of the year-over-year change flips. Random order: 4,000 shuffles of the same changes.')
cats = [str(r['N'])[2:] for r in ROWS]
cols = [(GOOD if r['yoy'] > 0 else BAD) for r in ROWS]
label(s, 0.4, 1.72, 8.5, 'Robusta production, change on the year before (%)', 11)
s.chart(0.3, 1.95, 8.6, 5.0, combo_bar(cats, [{'name': 'YoY', 'color': LIGHT, 'values': [round(r['yoy'], 1) for r in ROWS], 'point_colors': cols}],
                                       mn=-40, mx=60, unit=20, fmt='+0;-0;0', labels=False, legend=False, gap=30))
rows = [[th('Previous crop vs trend'), th('crops', algn='ctr'), th('next YoY', algn='ctr'), th('next vs trend', algn='ctr')],
        [td('above +8 %'), td(str(len(hi_prev)), algn='ctr'), td(fr(st.mean(r['yoy'] for r in hi_prev), 1, True) + ' %', algn='ctr', color=BAD, b=True), td(fr(st.mean(r['anom'] for r in hi_prev), 1, True) + ' %', algn='ctr')],
        [td('−8 to +8 %'), td(str(len(nm_prev)), algn='ctr'), td(fr(st.mean(r['yoy'] for r in nm_prev), 1, True) + ' %', algn='ctr'), td(fr(st.mean(r['anom'] for r in nm_prev), 1, True) + ' %', algn='ctr')],
        [td('below −8 %'), td(str(len(lo_prev)), algn='ctr'), td(fr(st.mean(r['yoy'] for r in lo_prev), 1, True) + ' %', algn='ctr', color=GOOD, b=True), td(fr(st.mean(r['anom'] for r in lo_prev), 1, True) + ' %', algn='ctr')]]
s.table(9.1, 2.05, [1.6, 0.6, 0.85, 0.9], 0.38, rows)
box(s, 9.1, 3.85, 3.95, 1.95, 'Reading for 2027', [
    '2026/27 (10.0 M bags) sits %s %% above its trend: the next crop tends to be lower year over year.' % fr(ROWS[-1]['anom'], 0),
    'But the forecast of slide 15 already starts from the trend (median of 2024–2026), so this is included: no extra cut.',
    'Correlation of the year-over-year change with the previous crop: r = %s.' % fr(FR['prev']['ry'], 2)], NAVY, 9.5)
slides.append(s)

# ======================================================================
# 14. 2026 scorecard vs a normal year
# ======================================================================
s = Slide()
TOWN26 = S['flowering2026']['towns']
header(s, '2026 flowering season against a normal year', [
    'Better than normal: trigger rain in 4 towns (normal 2–3), on the normal dates. That is the strongest positive signal in the data',
    'Drier and hotter than normal so far (El Niño): Jun–mid-Sep rain %s–%s %% of normal. With normal rain from now, Jun–Oct ends at %s %%, still in the good range' % (fr(min(OBS26['rain_pct'].values()), 0), fr(max(OBS26['rain_pct'].values()), 0), fr(F26['rain_JJASO'], 0)),
    'Risk: El Niño + positive IOD can keep Oct–Nov dry. Liwa (Lampung) has not flowered yet; young fruit can drop'],
    'NASA POWER daily to 19 Sep 2026; after 19 Sep the 1991–2020 daily normal is used ("normal from now"). Signal = mean crop vs trend in past years of the same class (slides 11–12). '
    'ONI: NOAA CPC (Jun–Aug 2026 +1.8). IOD: Bureau of Meteorology outlook, 15 Sep 2026.')
GR, AM, RD = 'E2F0D9', 'FFF2CC', 'F8CBAD'
rows = [[th('Indicator'), th('Normal year', algn='ctr'), th('2026 observed (to 19 Sep)', algn='ctr'), th('2026, normal from now', algn='ctr'), th('Past crops in that class', algn='ctr')],
        [td('Towns with trigger rain', b=True), td('2.6 of 5 (median 3)', algn='ctr'), td('4 of 5 (22 Jul, 16 Aug)', algn='ctr', fill=GR), td('4–5 of 5', algn='ctr', fill=GR),
         td('3–5 towns: %s %%, %d crops' % (fr(tb[2]['mean'], 1, True), tb[2]['n']), algn='ctr', color=GOOD, b=True)],
        [td('Trigger date', b=True), td('18 Jul – 17 Aug', algn='ctr'), td('22 Jul – 16 Aug', algn='ctr', fill=GR), td('Liwa: Oct?', algn='ctr', fill=AM), td('on time', algn='ctr')],
        [td('Rain Jun–Oct, % of normal', b=True), td('100 %', algn='ctr'), td('%s %% (Jun 1–Sep 19)' % fr(st.mean(OBS26['rain_pct'].values()), 0), algn='ctr', fill=AM),
         td('%s %%' % fr(F26['rain_JJASO'], 0), algn='ctr', fill=GR), td('50–80 %%: %s %%; >150 %%: %s %%' % (fr(rb[1]['mean'], 1, True), fr(rb[4]['mean'], 1)), algn='ctr', color=GOOD, b=True)],
        [td('Rain by town, Jun–Oct', b=True), td('100 %', algn='ctr'),
         td(' · '.join('%s %d' % (n, round(OBS26['rain_pct'][t])) for t, n in zip(T5, ['PA', 'LA', 'MU', 'LI', 'KE'])), 8, algn='ctr', fill=AM),
         td(' · '.join('%s %d' % (n, round(TOWN26[t]['rain_JJASO'])) for t, n in zip(T5, ['PA', 'LA', 'MU', 'LI', 'KE'])), 8, algn='ctr', fill=GR), td('dry lowland: watch Liwa', algn='ctr')],
        [td('Max temperature Jul–Oct', b=True), td('0 °C', algn='ctr'), td('%s °C (Jul 1–Sep 19)' % fr(st.mean(OBS26['tmax_anom'].values()), 1, True), algn='ctr', fill=AM), td('%s °C' % fr(t26, 1, True), algn='ctr', fill=GR),
         td('0 to +1.2 °C: +6 %', algn='ctr', color=GOOD, b=True)],
        [td('ENSO (ONI Aug–Nov)', b=True), td('−0.5 to +0.5', algn='ctr'), td('+1.8 (Jun–Aug)', algn='ctr', fill=AM), td('≥ +1.5 (NOAA)', algn='ctr', fill=AM),
         td('≥ 1.5: %s %%, 4 crops' % fr(ob[4]['mean'], 1), algn='ctr')],
        [td('IOD (DMI Aug–Nov)', b=True), td('−0.4 to +0.4', algn='ctr'), td('positive likely (BoM)', algn='ctr', fill=RD), td('positive', algn='ctr', fill=RD),
         td('El Niño + IOD+: %s %%, %d of %d down' % (fr(EN_IOD, 1), ob[-1]['down'], ob[-1]['n']), algn='ctr', color=BAD, b=True)]]
s.table(0.45, 1.95, [2.3, 1.75, 3.2, 2.9, 2.3], 0.56, rows)
s.text(0.45, 6.55, 12.4, 0.3, [para(run('Green: better than or as good as normal · yellow: off normal, not yet harmful · red: risk', 9, color=GREY))])
slides.append(s)

# ======================================================================
# 15. the 2027/28 calculation
# ======================================================================
s = Slide()
prod26 = float(FD[2026]['production_usda_M_sacs'])
header(s, '2027/28 with a normal end of season: %s M bags (+%s %% on 2026/27)' % (fr(P27, 1), fr(100 * (P27 / prod26 - 1), 0)), [
    'Area × trend yield = %s M bags. Weather effect of a 4-town trigger: %s %% (regression on 45 crops); 9 analog years: median %s %%' % (fr(BASE27, 2), fr(W26, 1, True), fr(an_med, 1, True)),
    'Half of the analog years fall between %s and %s M bags. Back-test error of the method: ±%s %% (the weather cuts it from ±%s %%)' % (fr(P27_lo, 1), fr(P27_hi, 1), fr(RM_MODEL, 0), fr(RM_NAIVE, 0)),
    'If Oct–Nov stay dry (El Niño + positive IOD): %s M bags. If Liwa also flowers with normal rain: %s M bags' % (fr(P27_dry, 1), fr(P27_liwa, 1))],
    'Productive area: ministry trend (slide 8). Trend yield: median of USDA yields per productive ha 2024–2026. Weather effect: least squares of crop vs trend on trigger towns, 1982–2026. '
    'Analogs: trigger ≥ 3 towns, Jun–Oct rain 50–100 %, max temp. −0.2 to +1.3 °C. Back-test: 45 crops, base = median of the 3 previous crops.')
rows = [[th('Step'), th('Number', algn='r'), th('Source')],
        [td('Productive area 2027'), td(format(round(AREA27), ',') + ' ha', algn='r', b=True), td('slide 8', color=GREY)],
        [td('× trend yield (median 2024–2026)'), td(fr(TY, 2) + ' bags/ha', algn='r', b=True), td('13.27 · 15.64 · 14.16', color=GREY)],
        [td('= trend production'), td(fr(BASE27, 2) + ' M bags', algn='r', b=True), td('')],
        [td('× weather: 4 towns triggered'), td(fr(W26, 1, True) + ' %', algn='r', b=True, color=GOOD), td('%s + %s × 4 towns' % (fr(B0, 1), fr(B1, 2)), color=GREY)],
        [td('= forecast yield'), td(fr(Y27, 2) + ' bags/ha', algn='r', b=True), td('')],
        [td('= 2027/28 production', b=True), td(fr(P27, 2) + ' M bags', algn='r', b=True, fill='DDEBF7'), td('normal weather from 20 Sep', color=GREY)],
        [td('50 % range (analog years)'), td('%s – %s' % (fr(P27_lo, 1), fr(P27_hi, 1)), algn='r'), td('%s to %s %%' % (fr(an_q1, 1), fr(an_q3, 1, True)), color=GREY)],
        [td('2 in 3 range (back-test)'), td('%s – %s' % (fr(P27_s_lo, 1), fr(P27_s_hi, 1)), algn='r'), td('±%s %%' % fr(RM_MODEL, 1), color=GREY)],
        [td('Dry Oct–Nov (El Niño + IOD+)'), td(fr(P27_dry, 2), algn='r', color=BAD, b=True), td('%s %%, 7 crops' % fr(EN_IOD, 1), color=GREY)]]
s.table(0.45, 1.95, [2.75, 1.5, 1.85], 0.43, rows)
hy = list(range(2015, 2027))
vals = [UA[y] for y in hy] + [round(P27, 2)]
cats = ['%s/%s' % (str(y)[2:], str(y + 1)[2:]) for y in hy] + ['27/28F']
fills = [None] * len(hy) + [hatch(NAVY)]
label(s, 6.8, 1.72, 6.2, 'USDA robusta production and the 2027/28 forecast (M bags)', 11)
s.chart(6.7, 1.95, 6.35, 3.5, yield_chart(cats, [{'name': 'Production', 'color': '8EB4E3', 'values': [round(v, 2) for v in vals], 'fills': fills, 'lfmt': '0.0'}],
                                          [{'name': 'Trend 2027', 'color': GREY, 'values': [round(BASE27, 2)] * len(cats), 'dash': 'dash', 'width': 1.25,
                                            'label': {'idx': 1, 'text': 'trend %s' % fr(BASE27, 1), 'pos': 't', 'sz': 8}}],
                                          mn=6, mx=12, unit=1, fmt='0', label_sz=8, legend=False, layout=(0.07, 0.06, 0.91, 0.8), overlap=0, gap=40))
box(s, 6.7, 5.55, 6.35, 1.1, 'For the trader', [
    'Normal end of season: a crop close to 2026/27 or slightly above (%s M). The downside is weather after flowering (Oct–Nov rain, Lampung), not area. '
    'Watch: Oct–Nov rain, the IOD, fires in South Sumatra.' % fr(P27, 1)], NAVY, 9.5)
slides.append(s)

out = HERE + 'Indonesia_robusta_2027_forecast_chain.pptx'
save(slides, out, 'Indonesia robusta 2027/28: forecast chain with proof')
print('saved', out, len(slides), 'slides')
print('area r', round(r_area, 2), round(p_area, 3), 'rev', round(r_rev, 2), round(p_rev, 3), 'px', round(r_px, 2), 'yl', round(r_yl, 2), 'same', n_same, len(same), round(p_same, 2), 'big', big_both)
print('lags', {k: (round(v[0], 2), round(v[1], 3)) for k, v in lags.items()}, 'drel', round(r_drel, 2), 'ay', round(r_ay, 2), round(r_py, 2))
print('trig r', round(FR['trig']['r'], 2), FR['trig']['p'], 'W26', round(W26, 2), 'W26_5', round(W26_5, 2), 'analog med', round(an_med, 1), an_q1, an_q3)
print('rmse naive', round(RM_NAIVE, 1), 'model', round(RM_MODEL, 1), 'AREA27', AREA27, 'TY', TY, 'BASE27', round(BASE27, 3), 'P27', round(P27, 3), 'dry', round(P27_dry, 2), 'liwa', round(P27_liwa, 2))
print('ranges', round(P27_lo, 2), round(P27_hi, 2), round(P27_s_lo, 2), round(P27_s_hi, 2), 'EN_IOD', round(EN_IOD, 1), 'alt', alt, round(st.mean(sims), 1), p_alt)
