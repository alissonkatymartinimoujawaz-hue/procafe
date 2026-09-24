import json, math, statistics as st, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from ooxml import Slide, run, para, bar_chart, line_chart, scatter_chart, combo_bar, multi_line, save

HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
js = open(BASE + 'weather_data.js').read()
D = json.loads(js[js.index('{'):js.rindex('}') + 1])
MON, ONI, DMI = D['monthly'], D['oni'], D['dmi']
U = {int(k): v for k, v in D['usda_robusta'].items()}
TOWNS = [('pagar_alam', 'Pagar Alam', 'South Sumatra, highland'), ('lahat', 'Lahat', 'South Sumatra, foothills'),
         ('muaradua', 'Muaradua', 'South Sumatra (OKU Selatan), lowland–foothills'), ('liwa', 'Liwa', 'Lampung (Lampung Barat)'),
         ('kepahiang', 'Kepahiang', 'Bengkulu, highland')]
ALL5 = [t[0] for t in TOWNS]
SS3 = ['pagar_alam', 'lahat', 'muaradua']

NAVY, EN, LN, NEU, RED, GREY, INK = '1F3864', 'ED7D31', '2E75B6', '7F7F7F', 'C00000', '7F7F7F', '262626'
PH_COL = {'pos': EN, 'neg': LN, 'neu': NEU}
PH_NAME = {'pos': 'El Niño', 'neg': 'La Niña', 'neu': 'Neutral'}
MONTHS = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
CAL = [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6]
SEASON_COLS = ['1F77B4', 'FF7F0E', '2CA02C', '9467BD', '8C564B', 'E377C2', '17BECF', 'BCBD22', '7F7F7F', 'AEC7E8']


def idx(src, y):
    v = [src.get('%d-%02d' % (y, m)) for m in (8, 9, 10, 11)]
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if len(v) >= 3 else None


def phase(y):
    e = idx(ONI, y)
    if e is None:  # current season: last available ONI
        ks = sorted(k for k in ONI if k.startswith(str(y)))
        e = ONI[ks[-1]] if ks else 0
    return 'pos' if e >= 0.5 else 'neg' if e <= -0.5 else 'neu'


def iod(y):
    d = idx(DMI, y)
    return None if d is None else ('pos' if d >= 0.4 else 'neg' if d <= -0.4 else 'neu')


def mval(towns, y, m, k):
    """mean over towns of monthly value k (0 rain, 1 t2m); None if any month incomplete"""
    vals = []
    for t in towns:
        v = MON[t].get('%d-%02d' % (y, m))
        if not v or not v[3] or v[k] is None:
            return None
        vals.append(v[k])
    return sum(vals) / len(vals)


def fr(v, d=1, plus=False):
    s = ('%.*f' % (d, v))
    if plus and v > 0:
        s = '+' + s
    return s


def header(s, title, bullets=(), src=None):
    s.text(0.45, 0.22, 12.4, 0.55, [para(run(title, 24 if len(title) <= 62 else 20, True, color=NAVY))], anchor='t')
    if bullets:
        s.text(0.75, 0.78, 11.9, 0.26 * len(bullets) + 0.05,
               [para(run(b, 10.5, color=INK, hl='FFFF00'), bullet=True, after=1) for b in bullets])
    if src:
        s.text(0.45, 7.12, 9.0, 0.3, [para(run(src, 7.5, color=GREY))])


slides = []

# ---------------- 0. title ----------------
s = Slide()
s.text(0.8, 2.3, 11.5, 1.0, [para(run('Indonesia Robusta: weather, ENSO and the 2027/28 crop', 32, True, color=NAVY))])
s.text(0.8, 3.35, 11.5, 0.9, [para(run('South Sumatra, Lampung and Bengkulu robusta belt · USDA PSD production · NASA POWER weather checked against GPCC rain gauges', 15, color='404040'))])
s.text(0.8, 4.4, 11.5, 0.4, [para(run('24 September 2026', 12, color=GREY))])
slides.append(s)

# ---------------- 1. production and ENSO ----------------
mys = list(range(2010, 2027))
prod = [U[y] / 1000 for y in mys] + [10.2]
yoy = [100 * (U[y] / U[y - 1] - 1) for y in mys] + [100 * (10.2 / (U[2026] / 1000) - 1)]
labels = ['%d/%s' % (y, str(y + 1)[2:]) for y in mys] + ['2027/28F']
s = Slide()
header(s, 'Indonesia Robusta production and ENSO', [
    'After La Niña flowering years, output fell in 6 of 10 crops (median −1.9 %); the two worst crops followed La Niña: 2011/12 (−16 %) and 2023/24 (−28 %)',
    'After El Niño flowering years: median +2.0 %; the loss came with the extreme 2015 drought (2016/17 −12 %)',
    '2026: El Niño (ONI Jun–Aug +1.8) and a positive IOD likely → 2027/28 forecast ≈ 10.2 M bags (±1.0)'],
    'Sources: USDA PSD (production, marketing year Apr–Mar; flowering the year before); NOAA CPC ONI. YoY by flowering-year phase, 1991–2026. 2027/28F: area × yield method, research note.')
rows = [[{'t': 'Marketing year', 'b': True, 'fill': NAVY, 'color': 'FFFFFF', 'sz': 8}] + [{'t': l, 'b': True, 'fill': NAVY, 'color': 'FFFFFF', 'sz': 8, 'algn': 'ctr'} for l in labels],
        [{'t': 'M bags', 'b': True, 'sz': 9}] + [{'t': fr(v, 2), 'sz': 9, 'algn': 'ctr', 'fill': 'DDEBF7' if i == len(prod) - 1 else None, 'b': i == len(prod) - 1} for i, v in enumerate(prod)],
        [{'t': 'YoY %', 'b': True, 'sz': 9}] + [{'t': fr(v, 1, True) + ' %', 'sz': 9, 'algn': 'ctr', 'color': 'C00000' if v < 0 else '00A050', 'fill': 'DDEBF7' if i == len(yoy) - 1 else None} for i, v in enumerate(yoy)]]
s.table(0.45, 1.72, [1.0] + [0.63] * len(labels), 0.3, rows)
oks = sorted(k for k in ONI if '2010-01' <= k <= '2026-12')
cats = [k[:4] for k in oks]
s.text(0.45, 2.78, 9, 0.35, [para(run('ONI (°C)   El Niño ≥ +0.5  /  La Niña ≤ −0.5', 13, True, color=NAVY))])
s.chart(0.35, 3.05, 12.6, 4.05, multi_line(cats, [
    {'name': 'ONI (3-month mean, NOAA CPC)', 'values': [ONI[k] for k in oks], 'color': '2E75B6', 'width': 2.25},
    {'name': '+0.5', 'values': [0.5] * len(oks), 'color': RED, 'width': 1.25},
    {'name': '−0.5', 'values': [-0.5] * len(oks), 'color': RED, 'width': 1.25, 'dash': 'dash'}],
    mn=-2.0, mx=2.5, unit=0.5, fmt='0.0', skip=12, legend=True, legend_sz=8))
slides.append(s)

# ---------------- 2. yield impact ----------------
def anom(my):
    nb = sorted(U[x] for x in U if x != my and abs(x - my) <= 3)
    m = len(nb) // 2
    med = nb[m] if len(nb) % 2 else (nb[m - 1] + nb[m]) / 2
    return 100 * (U[my] / med - 1)

mys2 = list(range(2006, 2027))
cats2 = ['%d/%s' % (y, str(y + 1)[2:]) for y in mys2]
ph2 = [phase(y - 1) for y in mys2]
an = [anom(y) for y in mys2]
yy = [100 * (U[y] / U[y - 1] - 1) for y in mys2]
allph = {'pos': [], 'neg': [], 'neu': []}
for my in range(1991, 2027):
    allph[phase(my - 1)].append(anom(my))
avg = {k: st.mean(v) for k, v in allph.items()}
s = Slide()
header(s, 'Indonesia Crop Year 2027/28: Yield', [
    'Δ yield, average impact vs neighbouring crops (1991–2026): El Niño %s %%, La Niña %s %%, Neutral %s %%' % (fr(avg['pos'], 1, True), fr(avg['neg'], 1, True), fr(avg['neu'], 1, True)),
    'ENSO alone explains little; what matters is the flowering rain: 3–5 towns with a flowering trigger → +4 %; none → −10 % (r = 0.47, p = 0.002)',
    '2026 flowering: trigger rain in 4 of 5 towns (not yet Liwa) → no La Niña-type washout; risk = drought after flowering in Lampung'],
    'Robusta production (USDA PSD) with area ~stable, used as a yield proxy. Colour = ENSO phase of the flowering year (ONI Aug–Nov). Neighbouring crops = median of the crops within ±3 years.')
def split(vals):
    return [{'name': PH_NAME[k], 'color': PH_COL[k], 'values': [round(v, 1) if p == k else None for v, p in zip(vals, ph2)]} for k in ('pos', 'neg', 'neu')]
s.text(0.45, 1.75, 6.2, 0.3, [para(run('Production vs neighbouring crops (%)', 12, True, color=NAVY))])
s.chart(0.35, 2.02, 6.35, 5.05, combo_bar(cats2, split(an), lines=[
    {'name': 'Average El Niño: %s %%' % fr(avg['pos'], 1, True), 'values': [round(avg['pos'], 2)] * len(cats2), 'color': EN, 'width': 1.5},
    {'name': 'Average La Niña: %s %%' % fr(avg['neg'], 1, True), 'values': [round(avg['neg'], 2)] * len(cats2), 'color': LN, 'width': 1.5}],
    mn=-30, mx=25, unit=10, fmt='0', label_fmt='+0;-0;0', overlap=100, gap=40, skip=2))
s.text(6.85, 1.75, 6.2, 0.3, [para(run('Production, year-over-year change (%)', 12, True, color=NAVY))])
s.chart(6.75, 2.02, 6.35, 5.05, combo_bar(cats2, split(yy), mn=-30, mx=50, unit=10, fmt='0', label_fmt='+0;-0;0', overlap=100, gap=40, skip=2))
slides.append(s)

# ---------------- 3. monthly anomalies by ENSO state ----------------
def monthly_comp(towns):
    out = {k: {'r': [[] for _ in range(12)], 't': [[] for _ in range(12)]} for k in ('pos', 'neg', 'neu')}
    clim_r = {m: st.mean(x for x in (mval(towns, y, m, 0) for y in range(2000, 2026)) if x is not None) for m in range(1, 13)}
    clim_t = {m: st.mean(x for x in (mval(towns, y, m, 1) for y in range(2000, 2026)) if x is not None) for m in range(1, 13)}
    for y in range(2000, 2026):
        for m in range(1, 13):
            o = ONI.get('%d-%02d' % (y, m))
            r, t = mval(towns, y, m, 0), mval(towns, y, m, 1)
            if o is None or r is None or t is None:
                continue
            k = 'pos' if o >= 0.5 else 'neg' if o <= -0.5 else 'neu'
            out[k]['r'][m - 1].append(100 * (r / clim_r[m] - 1))
            out[k]['t'][m - 1].append(t - clim_t[m])
    return out
mc = monthly_comp(ALL5)
mn_ = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
def comp_series(key, d):
    return [{'name': '%s (months with ONI %s)' % (PH_NAME[k], '≥ +0.5' if k == 'pos' else '≤ −0.5' if k == 'neg' else 'between'), 'color': PH_COL[k],
             'values': [round(st.mean(v), d) if v else None for v in mc[k][key]]} for k in ('pos', 'neg', 'neu')]
rs, ts = comp_series('r', 0), comp_series('t', 2)
jas = lambda ser: st.mean(ser['values'][i] for i in (6, 7, 8, 9))
s = Slide()
header(s, 'South Sumatra robusta belt | What El Niño and La Niña do to the weather', [
    'El Niño: rainfall %s %% below average in Jul–Oct, the dry season that sets flowering' % fr(-jas(rs[0]), 0),
    'La Niña: rainfall %s %% above average in Jul–Oct; temperatures slightly below average' % fr(jas(rs[1]), 0),
    'Effects are strongest from July to November; in the wet season (Dec–Mar) ENSO changes little'],
    'NASA POWER daily, mean of Pagar Alam, Lahat, Muaradua, Liwa and Kepahiang, 2000–2025. Each month classed by its own ONI value (NOAA CPC). Anomaly vs 2000–2025 average of the same month.')
s.text(0.45, 1.65, 6.2, 0.3, [para(run('Rainfall anomaly vs 2000–2025 average (%)', 12, True, color=NAVY))])
s.chart(0.35, 1.92, 6.35, 5.15, bar_chart(mn_, rs, mn=-80, mx=80, unit=20, fmt='0', labels=False, legend=True, gap=50, overlap=0).replace('<c:legendPos val="t"/>', '<c:legendPos val="b"/>'))
s.text(6.85, 1.65, 6.2, 0.3, [para(run('Temperature anomaly vs 2000–2025 average (°C)', 12, True, color=NAVY))])
s.chart(6.75, 1.92, 6.35, 5.15, bar_chart(mn_, ts, mn=-0.8, mx=0.8, unit=0.2, fmt='0.0', labels=False, legend=True, gap=50, overlap=0).replace('<c:legendPos val="t"/>', '<c:legendPos val="b"/>'))
slides.append(s)

# ---------------- 4-9. town panels ----------------
def season_vals(towns, S, k):
    return [None if (v := mval(towns, S + (1 if i >= 6 else 0), m, k)) is None else round(v, 2 if k == 1 else 0) for i, m in enumerate(CAL)]

def panel_slide(towns, name, sub):
    s = Slide()
    header(s, '%s | Temperature and rainfall' % name, src='NASA POWER daily (T2M, PRECTOTCORR), %s. Seasons July–June since 2006, classed by ONI Aug–Nov of the first year (±0.5). Black dashed = average of the seasons shown; red = 2026/27 so far (complete months only).' % sub)
    groups = {'pos': [], 'neg': [], 'neu': []}
    for S in range(2006, 2027):
        groups[phase(S)].append(S)
    allt = [x for S in range(2006, 2027) for x in season_vals(towns, S, 1) if x is not None]
    allr = [x for S in range(2006, 2027) for x in season_vals(towns, S, 0) if x is not None]
    tmn, tmx = math.floor(min(allt) * 2) / 2, math.ceil(max(allt) * 2) / 2
    rmx = math.ceil(max(allr) / 100) * 100
    cw, gx, x0 = 4.1, 0.12, 0.35
    for c, k in enumerate(('pos', 'neg', 'neu')):
        x = x0 + c * (cw + gx)
        seasons = groups[k]
        n_done = len([S for S in seasons if S < 2026])
        s.text(x + 0.05, 0.78, cw, 0.32, [para(run('%s (%d seasons)' % (PH_NAME[k], n_done), 13, True, color=PH_COL[k]))])
        for row, (key, lab, mn, mx, unit, fmt) in enumerate(((1, 'Mean temperature, °C', tmn, tmx, 0.5, '0.0'), (0, 'Monthly rainfall, mm', 0, rmx, 100 if rmx <= 600 else 200, '0'))):
            y = 1.12 + row * 3.0
            s.text(x + 0.05, y, cw, 0.25, [para(run(lab, 9.5, True, color='404040'))])
            ser = []
            done = [S for S in seasons if S < 2026]
            for j, S in enumerate(done):
                ser.append({'name': '%d/%s' % (S, str(S + 1)[2:]), 'values': season_vals(towns, S, key), 'color': SEASON_COLS[j % len(SEASON_COLS)], 'width': 1.1})
            av = []
            for i in range(12):
                v = [q['values'][i] for q in ser if q['values'][i] is not None]
                av.append(round(st.mean(v), 2 if key == 1 else 0) if v else None)
            if 2026 in seasons:
                ser.append({'name': '2026/27', 'values': season_vals(towns, 2026, key), 'color': RED, 'width': 2.5})
            ser.append({'name': 'Average', 'values': av, 'color': '000000', 'width': 2.25, 'dash': 'dash'})
            s.chart(x, y + 0.22, cw, 2.72 if row == 0 else 2.66, multi_line(MONTHS, ser, mn=mn, mx=mx, unit=unit, fmt=fmt, legend=(row == 1), legend_sz=7))
    return s

slides.append(panel_slide(SS3, 'South Sumatra (mean of 3 towns)', 'mean of Pagar Alam, Lahat and Muaradua'))
for tid, nm, sub in TOWNS:
    slides.append(panel_slide([tid], '%s' % nm, '%s (%s)' % (nm, sub)))

# ---------------- 10. year on year, coffee year Apr–Mar ----------------
def cy(towns, N):
    r = [mval(towns, N + (1 if m <= 3 else 0), m, 0) for m in (4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3)]
    t = [mval(towns, N + (1 if m <= 3 else 0), m, 1) for m in (4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3)]
    if any(v is None for v in r + t):
        return None, None
    return sum(r), st.mean(t)
Ns = list(range(2006, 2026))
ph10 = [phase(N) for N in Ns]
dt, dr = [], []
for N in Ns:
    r1, t1 = cy(ALL5, N)
    r0, t0 = cy(ALL5, N - 1)
    dt.append(round(t1 - t0, 2)); dr.append(round(100 * (r1 / r0 - 1), 1))
cats10 = ['%d/%s' % (N, str(N + 1)[2:]) for N in Ns]
def split10(vals):
    return [{'name': PH_NAME[k], 'color': PH_COL[k], 'values': [v if p == k else None for v, p in zip(vals, ph10)]} for k in ('pos', 'neg', 'neu')]
mean_ph = lambda vals, k: st.mean(v for v, p in zip(vals, ph10) if p == k)
s = Slide()
header(s, 'South Sumatra | Temperature and rainfall, year on year (coffee year Apr–Mar)', [
    'El Niño years: rainfall %s %% on the previous coffee year on average; La Niña years: %s %%' % (fr(mean_ph(dr, 'pos'), 0, True), fr(mean_ph(dr, 'neg'), 0, True)),
    'Temperature: El Niño %s °C, La Niña %s °C on the previous year on average' % (fr(mean_ph(dt, 'pos'), 2, True), fr(mean_ph(dt, 'neg'), 2, True)),
    '2026/27 (El Niño) is not complete; Jun 1–Sep 19 rainfall: 79 % of normal at Pagar Alam, 35–57 % in Lahat, Muaradua and Liwa, 93 % at Kepahiang'],
    'NASA POWER daily, mean of the 5 towns. Coffee year = USDA marketing year (April–March). Colour = ONI phase (Aug–Nov) of the year the coffee year starts.')
s.text(0.45, 1.75, 6.2, 0.3, [para(run('Mean temperature, year-on-year (°C)', 12, True, color=NAVY))])
s.chart(0.35, 2.02, 6.35, 5.05, combo_bar(cats10, split10(dt), mn=-0.8, mx=1.0, unit=0.2, fmt='0.0', label_fmt='+0.0;-0.0;0.0', overlap=100, gap=35, skip=2))
s.text(6.85, 1.75, 6.2, 0.3, [para(run('Rainfall, year-on-year (% on previous coffee year)', 12, True, color=NAVY))])
s.chart(6.75, 2.02, 6.35, 5.05, combo_bar(cats10, split10(dr), mn=-40, mx=60, unit=20, fmt='0', label_fmt='+0;-0;0', overlap=100, gap=35, skip=2))
slides.append(s)

# ---------------- 11. rainfall check ----------------
DS = json.load(open(HERE + 'deck_series.json'))
s = Slide()
header(s, 'Rainfall check | NASA POWER vs rain gauges (GPCC)', [
    'June–October rainfall, 5-town mean: correlation 0.93 (1981–2019, GPCC 0.25°) and 0.99 (2012–2025, GPCC 1°); same wet/dry sign in 34 of 39 years',
    'Confirmed: 2010, 2013, 2016, 2020–22, 2025 very wet; 1994, 1997, 2015, 2019, 2023 very dry; 2011 dry despite La Niña (NASA 79 %, gauges 85 %)',
    'Only real disagreement: 2007 (NASA 84 %, gauges 105 %). Levels in mm differ by town: always compare % of normal, never raw mm across sources'],
    'GPCC Full Data v2020 (0.25°, to 2019) and GPCC First Guess (1°, 2020–2025), via NOAA PSL; NASA POWER PRECTOTCORR. % of each source\'s own normal.')
s.text(0.45, 1.75, 8.3, 0.3, [para(run('June–October rainfall, % of normal (mean of 5 towns)', 12, True, color=NAVY))])
s.chart(0.35, 2.02, 8.5, 5.05, multi_line([str(y) for y in DS['yrs']], [
    {'name': 'NASA POWER', 'values': DS['nasa'], 'color': '2E75B6', 'width': 2.0},
    {'name': 'Rain gauges (GPCC)', 'values': DS['gpcc'], 'color': EN, 'width': 2.0},
    {'name': 'Normal = 100', 'values': [100] * len(DS['yrs']), 'color': '000000', 'width': 1.0, 'dash': 'dash'}],
    mn=0, mx=250, unit=50, fmt='0', skip=4, legend=True, legend_sz=9))
tr = [[{'t': 'Town', 'b': True, 'fill': NAVY, 'color': 'FFFFFF', 'sz': 9}, {'t': 'r 1981–2019', 'b': True, 'fill': NAVY, 'color': 'FFFFFF', 'sz': 9, 'algn': 'ctr'},
       {'t': 'Same sign', 'b': True, 'fill': NAVY, 'color': 'FFFFFF', 'sz': 9, 'algn': 'ctr'}, {'t': 'r 2012–25', 'b': True, 'fill': NAVY, 'color': 'FFFFFF', 'sz': 9, 'algn': 'ctr'}]]
for nm, a, b_, c in (('Pagar Alam', '0.86', '31/39', '0.97'), ('Lahat', '0.85', '32/39', '0.99'), ('Muaradua', '0.89', '34/39', '0.98'), ('Liwa', '0.93', '37/39', '0.96'), ('Kepahiang', '0.88', '30/39', '0.97'), ('5-town mean', '0.93', '34/39', '0.99')):
    bold = nm.startswith('5')
    tr.append([{'t': nm, 'sz': 9, 'b': bold}, {'t': a, 'sz': 9, 'algn': 'ctr', 'b': bold}, {'t': b_, 'sz': 9, 'algn': 'ctr', 'b': bold}, {'t': c, 'sz': 9, 'algn': 'ctr', 'b': bold}])
s.table(9.05, 2.2, [1.3, 0.95, 0.85, 0.85], 0.33, tr)
slides.append(s)

# ---------------- 12. ENSO + IOD composites and key years ----------------
s = Slide()
header(s, 'Why 2011 was dry | The Indian Ocean Dipole matters as much as ENSO', [
    'La Niña: 136 % of normal Jun–Oct on average, but not always wet: 2011 was dry (IOD slightly positive)',
    'All 8 positive-IOD dry seasons were dry (51 %); all 6 negative-IOD seasons were wet (145 %). Correlation: ONI −0.67, IOD −0.73',
    '2026: El Niño + positive IOD likely (BOM, 15 Sep 2026) = the driest combination: 7 seasons since 1981, 51 % on average, from 10 % (1997) to 94 % (2018)'],
    'June–October rainfall, mean of 5 towns, % of the 1991–2020 normal (NASA POWER 1981–2025; GPCC 1981–2019). Phases from ONI and DMI averaged Aug–Nov (±0.5 / ±0.4).')
s.text(0.45, 1.75, 6.2, 0.3, [para(run('June–October rainfall by phase (% of normal)', 12, True, color=NAVY))])
s.chart(0.35, 2.02, 6.35, 5.05, bar_chart(['La Niña', 'Neutral', 'El Niño', 'IOD negative', 'IOD positive'],
    [{'name': 'NASA POWER (1981–2025)', 'values': [136, 115, 67, 145, 51], 'color': '2E75B6'},
     {'name': 'Rain gauges GPCC (1981–2019)', 'values': [130, 112, 71, 139, 50], 'color': EN}],
    mn=0, mx=175, unit=25, fmt='0', labels=True, legend=True, gap=70, overlap=-5).replace('<c:legendPos val="t"/>', '<c:legendPos val="b"/>'))
kr = [[{'t': h, 'b': True, 'fill': NAVY, 'color': 'FFFFFF', 'sz': 9, 'algn': 'l' if i in (0, 5) else 'ctr'} for i, h in enumerate(('Year', 'ENSO', 'IOD', 'NASA', 'Gauges', 'Reading'))]]
key = [(1997, 'El Niño', 'positive', 10, 26, 'Extreme drought'), (2007, 'La Niña', 'neutral', 84, 105, 'Uncertain'),
       (2010, 'La Niña', 'neutral', 206, 186, 'Very wet: 2011 crop lost'), (2011, 'La Niña', 'neutral (+0.31)', 79, 85, 'Dry despite La Niña'),
       (2013, 'Neutral', 'neutral', 159, 146, 'Too wet'), (2015, 'El Niño', 'positive', 43, 36, 'Drought'),
       (2016, 'Neutral', 'negative', 133, 127, 'Wet'), (2019, 'Neutral', 'positive', 52, 41, 'Dry'),
       (2022, 'La Niña', 'neutral (−0.38)', 198, 174, 'Very wet'), (2023, 'El Niño', 'positive', 70, 55, 'Dry'),
       (2025, 'Neutral', 'neutral (−0.40)', 176, 146, 'Very wet')]
for y, e_, i_, a, g, rd in key:
    col = lambda v: 'DDEBF7' if v >= 115 else ('FBE5D6' if v <= 85 else None)
    kr.append([{'t': str(y), 'sz': 9, 'b': True}, {'t': e_, 'sz': 9, 'algn': 'ctr', 'color': PH_COL['pos'] if e_ == 'El Niño' else PH_COL['neg'] if e_ == 'La Niña' else '404040'},
               {'t': i_, 'sz': 9, 'algn': 'ctr'}, {'t': '%d %%' % a, 'sz': 9, 'algn': 'ctr', 'fill': col(a)}, {'t': '%d %%' % g, 'sz': 9, 'algn': 'ctr', 'fill': col(g)}, {'t': rd, 'sz': 9}])
s.table(6.85, 2.05, [0.55, 0.8, 1.2, 0.7, 0.75, 2.1], 0.36, kr)
slides.append(s)

out = HERE + 'Indonesia_robusta_weather_ENSO.pptx'
save(slides, out, 'Indonesia Robusta: weather, ENSO and the 2027/28 crop')
print('saved', out, len(slides), 'slides')
