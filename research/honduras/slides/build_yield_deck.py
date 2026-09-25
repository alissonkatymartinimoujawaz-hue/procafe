"""Honduras coffee: what drives production and yield, and how to forecast 2026/27.
Numbers come from research/honduras/yield_drivers/ (analysis.py, robustness.py, nowcast.py) and the workbook
excel/Honduras_yield_drivers_forecast.xlsx. Writes a PPTX with native charts and one PNG preview per slide."""
import json, math, os, sys
from deckkit import Page, save, fr, pct, esc, NAVY, BLUE, ORANGE, GREY, INK, LIGHT, HERE, K, AXIS, GRID
import ooxml
sys.path.insert(0, HERE + '../yield_drivers')
import analysis as AN
import nowcast as NC

RED, GREEN, AMBER, PALE = 'C00000', '2E7D32', 'C55A11', 'D9D9D9'
J = json.load(open(HERE + '../yield_drivers/robustness.json'))
FC = json.load(open(HERE + '../yield_drivers/forecast_2026_27.json'))
lab = lambda t: '%02d/%02d' % (t % 100, (t + 1) % 100)
PC = lambda v: pct(100 * (math.exp(v) - 1), 0)          # log change shown as a plain % change
SRC_PSD = 'USDA PSD (production, 1 000 60-kg bags, crop year Oct–Sep, July 2026 download); '


# ---------------------------------------------------------------- chart helpers (native chart + SVG preview)
def gbars(p, x, y, w, h, cats, series, ymin, ymax, unit, lay=(0.06, 0.04, 0.93, 0.84), fmt_axis='%g', xlab_every=1, suffix=''):
    xml = ooxml.bar_chart(cats, [dict(name=s['name'], values=[v if v is not None else '' for v in s['values']], color=s['color']) for s in series],
                          mn=ymin, mx=ymax, unit=unit, fmt='0', labels=False, legend=False, gap=60, overlap=0)
    p._native(x, y, w, h, xml, lay)
    px, py, pw, ph = p.plot_frame(x, y, w, h, lay)
    Y = lambda v: py + ph * (1 - (v - ymin) / (ymax - ymin))
    v = ymin
    while v <= ymax + 1e-9:
        yy = Y(v) * K
        p.svg.append('<line x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" stroke="#%s"/>' % (px * K, (px + pw) * K, yy, yy, 'B7C0C5' if abs(v) < 1e-9 else GRID))
        p.svg.append('<text x="%.1f" y="%.1f" font-size="13" fill="#%s" text-anchor="end">%s</text>' % (px * K - 8, yy + 4, AXIS, (fmt_axis % v).replace('.', ',') + suffix))
        v += unit
    n, m = len(cats), len(series)
    slot = pw / n
    bw = slot / (1 + 0.6) / m
    for i in range(n):
        x0 = px + slot * i + (slot - bw * m) / 2
        for k, s in enumerate(series):
            val = s['values'][i]
            if val is None:
                continue
            y0, y1 = sorted((Y(0), Y(val)))
            p.svg.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#%s"/>' % ((x0 + bw * k) * K, y0 * K, bw * K, max(0.5, (y1 - y0) * K), s['color']))
        if i % xlab_every == 0:
            p.svg.append('<text x="%.1f" y="%.1f" font-size="12" fill="#%s" text-anchor="middle">%s</text>' % ((px + slot * (i + 0.5)) * K, (py + ph) * K + 17, AXIS, esc(cats[i])))
    return px, py, pw, ph, Y


def scatter(p, x, y, w, h, pts, labels, xmn, xmx, xu, ymn, ymx, yu, color=BLUE, lay=(0.09, 0.04, 0.88, 0.82), suffix=' %'):
    xml = ooxml.scatter_chart([dict(name='crop years', xs=[a for a, _ in pts], ys=[b for _, b in pts], color=color, labels=labels)],
                              xmn, xmx, xu, ymn, ymx, yu, xfmt='0', yfmt='0', legend=False)
    p._native(x, y, w, h, xml, lay)
    px, py, pw, ph = p.plot_frame(x, y, w, h, lay)
    X = lambda v: px + pw * (v - xmn) / (xmx - xmn)
    Y = lambda v: py + ph * (1 - (v - ymn) / (ymx - ymn))
    v = ymn
    while v <= ymx + 1e-9:
        p.svg.append('<line x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" stroke="#%s"/>' % (px * K, (px + pw) * K, Y(v) * K, Y(v) * K, 'B7C0C5' if abs(v) < 1e-9 else GRID))
        p.svg.append('<text x="%.1f" y="%.1f" font-size="13" fill="#%s" text-anchor="end">%s</text>' % (px * K - 8, Y(v) * K + 4, AXIS, ('%g' % v) + suffix))
        v += yu
    v = xmn
    while v <= xmx + 1e-9:
        if abs(v) < 1e-9:
            p.svg.append('<line x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" stroke="#B7C0C5"/>' % (X(v) * K, X(v) * K, py * K, (py + ph) * K))
        p.svg.append('<text x="%.1f" y="%.1f" font-size="13" fill="#%s" text-anchor="middle">%s</text>' % (X(v) * K, (py + ph) * K + 18, AXIS, ('%g' % v) + suffix))
        v += xu
    for (a, b), lb in zip(pts, labels):
        p.svg.append('<circle cx="%.1f" cy="%.1f" r="6" fill="#%s" stroke="#FFFFFF" stroke-width="1.2"/>' % (X(a) * K, Y(b) * K, color))
        if lb:
            p.svg.append('<text x="%.1f" y="%.1f" font-size="11.5" fill="#5B6770">%s</text>' % (X(a) * K + 8, Y(b) * K + 4, esc(lb)))
    return X, Y


def verdict(d):
    if d['p_holm'] < 0.05:
        return ('robust', GREEN)
    if d['p'] < 0.05:
        return ('weak: passes alone only', AMBER)
    if d['p'] < 0.10:
        return ('hint (p < 0,10)', AMBER)
    return ('no link', GREY)


NAMES = {"biennial: last year's change": "Last year's change (mean reversion)", 'price change, year t vs t-1 (flowering year)': 'World arabica price change, year t',
         'price change, year t-1 vs t-2': 'Price change a year earlier', 'price level, year t-1 (log, detrended 5y)': 'Price level vs its 5-year mean',
         'coffee/urea ratio change, t vs t-1': 'Coffee / urea price ratio change', 'coffee/urea ratio, year t (log, vs 5y mean)': 'Coffee / urea ratio vs 5-year mean',
         'rain, dry season Dec-Mar': 'Rain Dec–Mar (before flowering)', 'rain, flowering Apr-May': 'Rain Apr–May (flowering, fruit set)', 'rain, rainy season Jun-Oct': 'Rain Jun–Oct (fruit fill)',
         'rain, previous rainy season May-Oct t-1': 'Rain May–Oct of the year before', 'ENSO, ONI Dec-Feb before flowering': 'El Niño index Dec–Feb',
         'ENSO, ONI Jun-Aug': 'El Niño index Jun–Aug', 'Tmax anomaly Mar-May (NASA)': 'Max. temperature Mar–May', 'N fertiliser use change (FAO, all crops)': 'Nitrogen use change (FAOSTAT)'}


# ---------------------------------------------------------------- 1. the answer
def slide_answer():
    p = Page()
    p.title('Output follows fertiliser, one-off shocks and pre-harvest heat, not rain or El Niño')
    p.bullets(['Tested on 44 crop years (1982/83–2025/26): each driver against the change in output the same crop year; "robust" = survives the correction for testing 14 drivers.',
               'Two drivers survive: nitrogen use (+0,75) and last year\'s change (−0,52: a shock is not repeated). Price and dry-season rain pass alone only. Added after: heat in Sep–Oct in the coffee zones (−0,45).'], h=0.8, sz=10)
    rows = [['Driver (same crop year as the output)', 'n', 'r', 'p', 'Holm p', 'Verdict']]
    cols = []
    for d in J['screens']['psd_1982_2025']:
        v, c = verdict(d)
        rows.append([NAMES.get(d['driver'], d['driver']), str(d['n']), fr(d['r'], 2), fr(d['p'], 3) if d['p'] >= 0.001 else '< 0,001', fr(min(d['p_holm'], 1), 2), [(v, dict(b=True, color=c))]])
    zt = next(d for d in J['coffee_zone_tmax']['tests'] if d['window'] == 'Tmax Sep-Oct' and d['dep'] == 'USDA production')
    rows.append([[('Max. temperature Sep–Oct, coffee zones (added)', dict(b=True))], str(zt['n']), fr(zt['r'], 2), fr(zt['p'], 3), '–', [('strong hint: tried 4 windows', dict(b=True, color=AMBER))]])
    p.table(0.45, 1.72, [3.55, 0.45, 0.65, 0.7, 0.7, 1.75], [0.34] + [0.29] * (len(rows) - 1), rows, sz=8.3)
    x0, w0 = 8.6, 4.3
    p.text(x0, 1.72, w0, 0.3, [('The chain, crop year t (harvest Nov t – Mar t+1)', dict(b=True, color=NAVY))], sz=10.5)
    boxes = [('1  Cash', 'price received for the last crop (r = +0,47 with nitrogen, p = 0,06) and state programmes (Bono 2020: 25 188 t of fertiliser)', LIGHT),
             ('2  Fertiliser, Apr–Sep t', 'nitrogen use and output move together: r = +0,75, still +0,69 with any year left out', LIGHT),
             ('3  Fruit set and fill, May–Oct t', 'rain: no reliable link in 44 years; heat in Sep–Oct, just before harvest: r = −0,45', 'FBE5D6'),
             ('4  Shocks', 'rust 2012/13 (−16 %), price slump 2019/20 (−27 %), rust after Eta/Iota 2021/22 (−26 %)… then back to trend', 'FBE5D6'),
             ('5  What USDA calls yield', 'production ÷ bearing area: area re-counts (2006, 2012, 2013, 2016) move it on their own', 'F2F2F2')]
    yy = 2.08
    for hd, tx, fill in boxes:
        p.text(x0, yy, w0, 0.78, [(hd, dict(b=True, sz=9.5, color=NAVY)), (tx, dict(sz=8.8))], fill=fill)
        yy += 0.86
    p.source('Tests: research/honduras/yield_drivers/analysis.py and robustness.py. r = Pearson correlation of year-on-year log changes; p = 5 000 random shuffles; Holm = correction for 14 tests. '
             + SRC_PSD + 'FAOSTAT nitrogen use (all crops, 2004–2024); World Bank Pink Sheet; GPCC rain at 3 coffee towns; NOAA ONI; NASA POWER; ERA5-Land max. temperature at 10 coffee points. Bono: USDA GAIN 2021.', y=6.95)
    return p


# ---------------------------------------------------------------- 2. production and the three crises
def slide_production():
    p = Page()
    p.title('Each big fall has a documented cause, and each was followed by a rebound')
    yrs = list(range(2005, 2027))
    vals = [AN.PSD[t] / 1000 for t in yrs]
    crisis = {2012: 'rust', 2019: 'price', 2021: 'rust + Eta/Iota'}
    colors = [RED if t in crisis else (PALE if t == 2026 else BLUE) for t in yrs]
    labels = [(PC(math.log(AN.PSD[t] / AN.PSD[t - 1]))) if t in crisis or t in (2011, 2016, 2020, 2022) else '' for t in yrs]
    px, py, pw, ph, Y = p.bars(0.45, 1.25, 9.0, 5.3, [lab(t) for t in yrs], vals, colors, 8, 1, labels=labels, lay=(0.06, 0.05, 0.93, 0.85),
                               ylab='USDA production, million 60-kg bags', label_sz=8.5)
    n = len(yrs)
    xi = lambda t: px + pw * (yrs.index(t) + 0.5) / n
    p.dot(xi(2025), Y(FC['base_exports'] / 1000), 0.16, ORANGE, hollow=True)
    p.text(xi(2025) - 1.55, Y(FC['base_exports'] / 1000) - 0.52, 1.5, 0.45, [('2025/26 implied by exports: ' + fr(FC['base_exports'] / 1000, 1), dict(color=ORANGE, b=True))], sz=8, algn='r')
    x0, w0 = 9.75, 3.15
    p.text(x0, 1.25, w0, 0.3, [('What happened', dict(b=True, color=NAVY))], sz=10.5)
    notes = [('2011/12  +41 %', 'price 5,98 $/kg (record at the time), nitrogen +53 %', BLUE),
             ('2012/13  −16 %', 'leaf rust on 25 % of the area (71 000 ha); price −31 %', RED),
             ('2016/17  +42 %', 'plantings renewed after the rust come into bearing (USDA); nitrogen +27 %; urea 194 $/t', BLUE),
             ('2019/20  −27 %', 'price 2,88 $/kg, lowest since 2007, under most cost estimates; nitrogen −30 %', RED),
             ('2020/21  +25 %', 'Bono Cafetalero: 25 188 t of free fertiliser; nitrogen +49 %', BLUE),
             ('2021/22  −26 %', 'rust after hurricanes Eta and Iota (15–25 % incidence in 5 departments); nitrogen −18 %', RED),
             ('2025/26', 'record prices; IHCAFE exports about +18 % on 2024/25, USDA output only +6 %', ORANGE)]
    yy = 1.6
    for hd, tx, c in notes:
        p.text(x0, yy, w0, 0.62, [(hd, dict(b=True, color=c, sz=9)), (tx, dict(sz=8.3))])
        yy += 0.68
    p.legend(0.95, 6.62, [(BLUE, 'crop year', 'box'), (RED, 'documented crisis', 'box'), (PALE, '2026/27 = USDA forecast', 'box')], sz=8.5)
    p.source(SRC_PSD + 'causes: USDA GAIN 2014, 2016, 2017, 2020, 2021, 2022 (rust area, Bono, Eta/Iota incidence); World Bank arabica (calendar year); FAOSTAT nitrogen use (calendar year = the year the crop is fertilised). '
             '2025/26 export-implied: Exports_nowcast sheet (IHCAFE exports as printed by La Prensa, 15 Jul 2026).', y=6.95)
    return p


# ---------------------------------------------------------------- 3. no on/off cycle
def slide_biennial():
    p = Page()
    p.title('No on/off cycle: after a big year the crop returns to trend, it does not slump')
    ys = [t for t in sorted(AN.DEP_P) if t >= 1982 and t - 1 in AN.DEP_P]
    pts = [(100 * AN.DEP_P[t - 1], 100 * AN.DEP_P[t]) for t in ys]
    show = {2011, 2012, 2013, 2016, 2019, 2020, 2021, 2022, 1999, 1998, 2025}
    X, Y = scatter(p, 0.45, 1.2, 7.4, 5.35, pts, [lab(t) if t in show else '' for t in ys], -40, 40, 20, -40, 40, 20)
    # least-squares line
    xs, yv = zip(*pts)
    b = AN.ols([[1, a] for a in xs], list(yv))
    p.svg.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#%s" stroke-width="2.5" stroke-dasharray="7,5"/>' % (
        X(-35) * K, Y(b[0] + b[1] * -35) * K, X(35) * K, Y(b[0] + b[1] * 35) * K, ORANGE))
    p.text(0.95, 6.62, 7, 0.25, [('x: change in output last crop year · y: change this crop year (USDA production, 1982/83–2025/26, n = %d) · dashed: fitted line' % len(pts), dict(color=GREY))], sz=8)
    d = next(v for v in J['biennial'] if v['series'].startswith('USDA production'))
    e = next(v for v in J['biennial'] if v['series'].startswith('IHCAFE'))
    x0, w0 = 8.3, 4.6
    p.text(x0, 1.2, w0, 0.3, [('How to tell a cycle from one-off shocks', dict(b=True, color=NAVY))], sz=10.5)
    rows = [['', 'USDA production', 'IHCAFE exports'],
            ['Correlation this year / last year', fr(d['r'], 2), fr(e['r'], 2)],
            ['If shocks are one-off: −0,50, 95 % band', '%s to %s' % (fr(d['iid_lo'], 2), fr(d['iid_hi'], 2)), '%s to %s' % (fr(e['iid_lo'], 2), fr(e['iid_hi'], 2))],
            ['Implied link between yearly levels', fr(d['implied_phi'], 2), fr(e['implied_phi'], 2)],
            ['Direction flips (one-off: 67 %)', pct(100 * d['flips'], 0, False), pct(100 * e['flips'], 0, False)],
            ['Years', '1981–2025', '1971–2020']]
    p.table(x0, 1.58, [2.5, 1.05, 1.05], 0.36, rows, sz=8.5)
    p.text(x0, 3.9, w0, 2.1, [('Reading', dict(b=True, color=NAVY, sz=9.5)),
                              'An on/off cycle would give a correlation below −0,50 and flips more than 2 years in 3. The data sit exactly on the one-off value: the level of one year says nothing about the next (link ≈ 0).',
                              'So a record crop is followed by a smaller one only because the shock (price, fertiliser, weather, rust) is not repeated.',
                              ('For a forecast: start from the trend (average of recent years), not from last year\'s number and not from an "on" or "off" label.', dict(b=True))],
           sz=9, fill='F2F5F8')
    p.source('Python: robustness.py (4 000 simulated series of one-off shocks give the band). ' + SRC_PSD + 'IHCAFE Resumen Informe 2020-2021 (exports 1970/71–2020/21, 46-kg bags).', y=6.95)
    return p


# ---------------------------------------------------------------- 4. yield = production / area
def slide_yield():
    p = Page()
    p.title('Some "yield" jumps are USDA re-counting the area, not trees producing more')
    rows = J['yield_decomposition']['rows']
    cats = [lab(d['year']) for d in rows]
    gbars(p, 0.45, 1.3, 8.9, 4.9, cats, [dict(name='Production change', values=[100 * (math.exp(d['dP']) - 1) for d in rows], color=NAVY),
                                        dict(name='Bearing-area change', values=[100 * (math.exp(d['dA']) - 1) for d in rows], color=ORANGE)],
          -30, 50, 10, suffix=' %', xlab_every=1)
    p.legend(0.95, 6.35, [(NAVY, 'production change', 'box'), (ORANGE, 'bearing-area change', 'box')], sz=9)
    x0, w0 = 9.7, 3.2
    YD = J['yield_decomposition']
    p.text(x0, 1.3, w0, 0.3, [('Yield = production ÷ bearing area', dict(b=True, color=NAVY))], sz=10.5)
    big = [d for d in rows if abs(d['dA']) > 0.08]
    tr = [['Crop year', 'Output', 'Area', 'Yield']] + [[lab(d['year']), PC(d['dP']), PC(d['dA']), PC(d['dY'])] for d in big]
    yy = p.table(x0, 1.68, [0.95, 0.75, 0.75, 0.75], 0.33, tr, sz=8.5)
    p.text(x0, yy + 0.15, w0, 2.0, ['Variance of the yearly yield change: %s; of the area change alone: %s (%s of it).' % (fr(YD['var_dY'], 4), fr(YD['var_dA'], 4), pct(100 * YD['var_dA'] / YD['var_dY'], 0, False)),
                                    '2013/14: yield +17 % while output fell 7 %: the area was cut by 20 %.',
                                    ('Use production (and IHCAFE exports) to forecast; treat the USDA yield as a derived number.', dict(b=True))], sz=9, fill='F2F5F8')
    p.source(SRC_PSD + 'USDA FAS Coffee Annual Honduras 2011–2026 (bearing area, kha). Changes in %; the table lists the years when the bearing area moved by more than 8 %.', y=6.95)
    return p


# ---------------------------------------------------------------- 5. fertiliser
def slide_fert():
    p = Page()
    p.title('Nitrogen is the tightest link: output moves with fertiliser use (r = +0,75)')
    F = J['fertiliser']
    rows = F['rows']
    gbars(p, 0.45, 1.3, 8.2, 4.9, [lab(d['year']) for d in rows], [dict(name='Nitrogen use change', values=[100 * (math.exp(d['dN']) - 1) for d in rows], color='7F9F3F'),
                                                                 dict(name='Production change', values=[100 * (math.exp(d['dP']) - 1) for d in rows], color=NAVY)],
          -40, 80, 20, suffix=' %')
    p.legend(0.95, 6.35, [('7F9F3F', 'nitrogen use change (FAOSTAT, calendar year t)', 'box'), (NAVY, 'production change, crop t', 'box')], sz=9)
    x0, w0 = 8.95, 3.95
    p.text(x0, 1.3, w0, 0.3, [('What moves nitrogen use? (2005–2024)', dict(b=True, color=NAVY))], sz=10.5)
    short = {'N use change vs output change, same crop year': 'Output, same crop year', 'N use change vs output change of the crop before (income)': 'Output of the crop before',
             'N use change vs world arabica price change, same calendar year': 'World arabica price, same year', 'N use change vs coffee/urea price ratio change': 'Coffee / urea price ratio',
             'N use change vs urea price change': 'Urea price', 'N use change vs IHCAFE export price change of the crop before': 'Export price of the crop before'}
    tr = [['Nitrogen change vs', 'r', 'p']] + [[short[d['test']], fr(d['r'], 2), fr(d['p'], 3) if d['p'] >= 0.001 else '< 0,001'] for d in F['tests']]
    yy = p.table(x0, 1.68, [2.55, 0.7, 0.7], 0.33, tr, sz=8.5)
    p.text(x0, yy + 0.12, w0, 2.4, ['Nitrogen does not track the world price of the year; it follows (weakly) the price received for the previous crop, i.e. cash in hand, and state help (Bono 2020: nitrogen +49 %).',
                                    'Part of the link can run backwards: growers fertilise more when the flowering promises a big crop. Either way fertiliser bought Apr–Sep is a leading sign of the crop.',
                                    ('FAOSTAT runs to 2024 (2022 imputed): for 2025–26 watch fertiliser imports and the urea price (+33 % in Jan–Aug 2026).', dict(b=True))], sz=8.8, fill='F2F5F8')
    p.source('FAOSTAT Inputs/Fertilizers by nutrient (nitrogen, t N, all crops: coffee not separated). ' + SRC_PSD + 'World Bank Pink Sheet (arabica, urea). IHCAFE export price: Resumen Informe 2020-2021. '
             'Smallest r with any one year left out: ' + fr(F['drop_one_min_r'], 2) + '.', y=6.95)
    return p


# ---------------------------------------------------------------- 6. weather
def slide_weather():
    p = Page()
    p.title('Rain and El Niño do not track output; heat just before harvest does')
    en = J['enso']['el_nino']
    tr = [['El Niño (ONI Oct–Dec ≥ 1)', 'ONI', 'Crop t', 'Crop t+1']] + [[lab(d['year']), fr(d['oni_ond'], 1), PC(d['dP_t']) if d['dP_t'] is not None else '–',
                                                                         PC(d['dP_t1']) if d['dP_t1'] is not None else '–'] for d in en]
    tr[0][0] = 'El Niño year (ONI Oct–Dec ≥ 1)'
    yy = p.table(0.45, 1.2, [1.9, 0.6, 0.8, 0.8], 0.24, tr, sz=8)
    p.text(0.45, yy + 0.02, 4.1, 0.3, ['Crop t filled during the event, t+1 flowered after it: rises and falls alike.'], sz=7.8)
    sc = {d['driver']: d for d in J['screens']['psd_1982_2025']}
    CT = J['coffee_zone_tmax']
    tests = [['vs output change, 1982–2025', 'r', 'p']]
    for k in ('rain, dry season Dec-Mar', 'rain, flowering Apr-May', 'rain, rainy season Jun-Oct', 'ENSO, ONI Dec-Feb before flowering', 'ENSO, ONI Jun-Aug'):
        tests.append([NAMES[k].replace(' (before flowering)', '').replace(' (flowering, fruit set)', '').replace(' (fruit fill)', ''), fr(sc[k]['r'], 2), fr(sc[k]['p'], 2)])
    zt = {d['window']: d for d in CT['tests'] if d['dep'] == 'USDA production'}
    for w, nm in (('Tmax Mar-May (flowering)', 'Max. temp. Mar–May'), ('Tmax Jun-Aug (fruit fill)', 'Max. temp. Jun–Aug'), ('Tmax Sep-Oct', 'Max. temp. Sep–Oct')):
        d = zt[w]
        tests.append([[(nm, dict(b=w == 'Tmax Sep-Oct'))], [(fr(d['r'], 2), dict(b=w == 'Tmax Sep-Oct', color=RED if w == 'Tmax Sep-Oct' else INK))], fr(d['p'], 3)])
    ex = CT['extra_tests'][0]
    tests.append([[('Sep–Oct, warming trend removed', dict(b=True))], [(fr(ex['r'], 2), dict(b=True, color=RED))], fr(ex['p'], 3)])
    p.table(0.45, yy + 0.36, [2.9, 0.6, 0.6], 0.235, tests, sz=7.8)
    # scatter heat vs output
    SO = {int(k): v for k, v in CT['sep_oct'].items()}
    ys = [t for t in sorted(AN.DEP_P) if t >= 1982 and t in SO]
    pts = [(SO[t], 100 * (math.exp(AN.DEP_P[t]) - 1)) for t in ys]
    show = {2019, 2021, 2023, 2009, 2011, 2016, 1999, 1986, 2004}
    X, Y = scatter(p, 4.85, 1.2, 4.9, 4.55, pts, [lab(t) if t in show else '' for t in ys], -1.5, 2.5, 0.5, -40, 60, 20, color=ORANGE, lay=(0.12, 0.04, 0.85, 0.84), suffix='')
    xs, yv = zip(*pts)
    b = AN.ols([[1, a_] for a_ in xs], list(yv))
    p.svg.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#%s" stroke-width="2.5" stroke-dasharray="7,5"/>' % (
        X(-1.2) * K, Y(b[0] + b[1] * -1.2) * K, X(2.2) * K, Y(b[0] + b[1] * 2.2) * K, NAVY))
    h26 = CT['sep_2026_to_18']
    p.vline(4.85 + 4.9 * 0.12 + 4.9 * 0.85 * (h26 + 1.5) / 4.0, 1.2 + 4.55 * 0.04, 1.2 + 4.55 * 0.88, RED, w=0.02)
    p.text(4.85 + 4.9 * 0.12 + 4.9 * 0.85 * (h26 + 1.5) / 4.0 - 1.45, 1.3, 1.4, 0.45, [('1–18 Sep 2026: +' + fr(h26, 1) + ' °C', dict(b=True, color=RED))], sz=8, algn='r')
    p.text(4.85, 5.8, 4.9, 0.45, [('x: max. temperature Sep–Oct, °C vs 1991–2020 (ERA5-Land, %d coffee points) · y: output change, %% · dashed: fitted line' % len(CT['points']), dict(color=GREY))], sz=7.8)
    r26 = J['rain_2026']
    A26 = CT['anom_2026']
    hot = CT['hottest_sep_oct']
    p.text(10.0, 1.2, 2.9, 5.35, [('2026 so far (crop 2026/27)', dict(b=True, color=NAVY, sz=10)),
                                  ('Rain vs normal (GPCC, 3 towns)', dict(b=True, sz=8.8)),
                                  'Dec–Mar %s · Apr–May %s' % (pct(r26['dry Dec-Mar'], 0), pct(r26['flowering Apr-May'], 0)),
                                  ('Jun–Aug %s: driest since 1981' % pct(r26['Jun-Aug'], 0), dict(b=True, color=RED)),
                                  ('Max. temperature vs normal (coffee zones)', dict(b=True, sz=8.8)),
                                  'Dec–Feb %s °C · Mar–May %s °C' % (fr(A26['Tmax Dec-Feb'], 1), fr(A26['Tmax Mar-May (flowering)'], 1)),
                                  'Jun–Aug +%s °C (4th hottest)' % fr(A26['Tmax Jun-Aug (fruit fill)'], 1),
                                  ('1–18 Sep +%s °C: warmer than any full September since 1981' % fr(h26, 1), dict(b=True, color=RED)),
                                  ('Hottest Sep–Oct before', dict(b=True, sz=8.8))] +
                                 ['%s  +%s °C → output %s' % (lab(d['year']), fr(d['anom'], 1), PC(d['dP_t'])) for d in hot[:4]] +
                                 [('Why it can matter: heat and drought in the last weeks of fruit fill speed up ripening and lighten the beans. Found after trying 4 windows: a strong hint, not a law.', dict(sz=8, color=GREY))],
           sz=8.6, fill='FBE5D6')
    p.source('NOAA CPC ONI; ' + SRC_PSD + 'GPCC 1° monthly (First Guess for 2026) at 3 coffee towns; ERA5-Land daily max. temperature (Open-Meteo archive) at 10 coffee municipalities '
             '(El Paraíso ×2, Comayagua ×2, La Paz, Santa Bárbara, Copán, Ocotepeque, Yoro, Fco. Morazán), 1981 – 18 Sep 2026; 2026 values preliminary. p = 5 000 shuffles.', y=6.95)
    return p


def slide_backtest():
    p = Page()
    p.title('Nobody forecasts Honduras better than ±10–12 %: add in-season heat and exports')
    B = J['backtest']
    order = ['Last year (random walk)', 'Linear trend, last 8 years', 'Average of last 3 years', 'Average of last 2 years',
             'Model: mean reversion + price + dry-season rain', 'Model + Sep-Oct heat (coffee zones)', 'Combination: last 2 years and model + heat']
    short = {'Last year (random walk)': 'Last year', 'Linear trend, last 8 years': 'Trend 8 y', 'Average of last 3 years': 'Avg 3 y',
             'Average of last 2 years': 'Avg 2 y', 'Model: mean reversion + price + dry-season rain': 'Model*', 'Model + Sep-Oct heat (coffee zones)': 'Model+heat',
             'Combination: last 2 years and model + heat': 'Mix'}
    M = {d['method']: d for d in B['methods']}
    vals = [100 * M[k]['mape'] for k in order] + [100 * B['usda']['mape']]
    cats = [short[k] for k in order] + ['USDA May']
    colors = [BLUE] * 5 + [ORANGE, GREEN, NAVY]
    p.bars(0.45, 1.3, 7.6, 4.6, cats, vals, colors, 16, 4, labels=[fr(v, 1) + ' %' for v in vals], lay=(0.07, 0.05, 0.92, 0.84),
           ylab='Average miss of the production forecast, % (crop years 2000/01–2025/26; USDA: 11 years)', label_sz=9)
    p.text(0.45, 6.02, 7.6, 0.85, ['* Model = last year\'s change + world price change + Dec–Mar rain; "+heat" adds coffee-zone max. temperature in Sep–Oct (known by early November, before the harvest). '
                                   'Mix = average of Avg 2 y and Model+heat. All refitted each year with past data only.',
                                   'The heat window and the combinations were chosen after seeing the data: treat 10,5–10,9 %% as optimistic. On USDA\'s 11 years: model + heat %s, USDA %s.' % (
                                       pct(100 * B['usda']['same_years']['Model + Sep-Oct heat (coffee zones)'], 1, False), pct(100 * B['usda']['mape'], 1, False))], sz=8)
    x0 = 8.4
    U = B['usda']
    tr = [['Crop year', 'USDA May', 'Actual', 'Miss']] + [[lab(d['year']), fr(d['usda_may'] / 1000, 1), fr(d['actual'] / 1000, 2), pct(100 * (d['usda_may'] / d['actual'] - 1), 0)] for d in U['rows']]
    p.text(x0, 1.3, 4.5, 0.3, [('USDA first forecast of the coming crop, M bags', dict(b=True, color=NAVY))], sz=10)
    yy = p.table(x0, 1.64, [1.1, 1.1, 1.1, 1.0], 0.3, tr, sz=8.5)
    p.text(x0, yy + 0.1, 4.45, 1.3, ['Misses of 14–30 % came in the turning years: 2011/12 (price boom), 2016/17 and 2017/18 (renewed plantings), 2013/14 and 2021/22 (rust).',
                                     ('Price and rain add nothing out of sample; Sep–Oct heat does. The rest of the edge is in-season information: exports, rust surveys, fertiliser.', dict(b=True))], sz=8.5, fill='F2F5F8')
    p.source('Back-test: robustness.py and the Backtest sheet. Actual = USDA production (July 2026 data), itself revised. USDA May forecasts read in USDA FAS Coffee Annual Honduras 2011–2021, 2025 '
             '(2019 not found; the 2022–2024 reports forecast the crop being harvested, not the next one).', y=6.95)
    return p


def slide_nowcast():
    p = Page()
    p.title('2025/26 is bigger than USDA says: IHCAFE exports +%s, USDA exports +1 %%' % pct(100 * (FC['exports_q']['mid'] / NC.PREV_FULL - 1), 0, False))
    cats = [c[0] for c in NC.CHECKPOINTS] + ['Full year']
    v25 = [c[1] / 1e6 for c in NC.CHECKPOINTS] + [FC['exports_q']['mid'] / 1e6]
    v24 = [c[2] / 1e6 for c in NC.CHECKPOINTS] + [NC.PREV_FULL / 1e6]
    px, py, pw, ph, Y = gbars(p, 0.45, 1.35, 7.6, 4.6, cats, [dict(name='2024/25', values=v24, color=PALE), dict(name='2025/26', values=v25, color=NAVY)], 0, 8, 1,
                              lay=(0.07, 0.04, 0.91, 0.86))
    p.text(0.45, 1.1, 7.6, 0.26, [('Cumulative exports since 1 October, million quintales (46 kg)', dict(color=GREY))], sz=9)
    n = len(cats)
    for i in range(n):
        g = v25[i] / v24[i] - 1
        p.text(px + pw * (i + 0.5) / n - 0.5, Y(v25[i]) - 0.3, 1.0, 0.24, [('+' + fr(100 * g, 0) + ' %', dict(b=True, color=NAVY))], sz=8.5, algn='ctr')
    xi = px + pw * (n - 0.5) / n + 0.12
    p.vline(xi, Y(FC['exports_q']['hi'] / 1e6), Y(FC['exports_q']['lo'] / 1e6), INK, w=0.02)
    p.legend(0.95, 6.35, [(PALE, '2024/25 same date', 'box'), (NAVY, '2025/26 (last bar: estimate, low–high)', 'box')], sz=9)
    x0, w0 = 8.35, 4.55
    q2b = lambda q: q * 46 / 60 / 1e6
    rows = [['Step', 'M bags of 60 kg'],
            ['Exports to 14 Jul 2026 (IHCAFE via La Prensa)', fr(q2b(NC.CHECKPOINTS[4][1]), 2)],
            ['Full year, low (+ 290 000 qq still to ship)', fr(q2b(FC['exports_q']['lo']), 2)],
            ['Full year, high (+ 340 000 qq in Jul and Aug)', fr(q2b(FC['exports_q']['hi']), 2)],
            ['A. Exports (middle) + domestic use 0,38', fr(FC['balance'] / 1000, 2)],
            ['B. USDA 2024/25 × export growth', fr(FC['ratio'] / 1000, 2)],
            [[('Production 2025/26 implied (A, B average)', dict(b=True))], [(fr(FC['base_exports'] / 1000, 2), dict(b=True))]],
            ['USDA production 2025/26 (May 2026)', fr(AN.PSD[2025] / 1000, 2)],
            ['USDA exports 2025/26 (May 2026)', '5,03']]
    yy = p.table(x0, 1.35, [3.35, 1.2], 0.32, rows, sz=8.5)
    p.text(x0, yy + 0.1, w0, 2.0, [('Implied − USDA: ' + pct(100 * (FC['base_exports'] / AN.PSD[2025] - 1), 0), dict(b=True, color=ORANGE, sz=10)),
                                   'The year was front-loaded (+127 % in October, +58 % to March, +24 % to mid-July): early-season growth overstated the crop. Do not extrapolate Oct–Dec 2026 either.',
                                   ('USDA\'s "+9 % in 2026/27" starts from a 2025/26 base that is about 9 % too low.', dict(b=True))], sz=8.5, fill='F2F5F8')
    p.source('Pages read in raw/coffee_zones/press: La Prensa 5 Nov 2025, 4 Mar, 3 Jul, 15 Jul 2026; El Heraldo 4 May 2026 (all quoting IHCAFE). 2024/25 same-date figures as printed; two of them disagree '
             '(see Exports_nowcast). USDA: PSD and Coffee Annual Honduras, May 2026. 1 bag of 60 kg = 1,304 quintales.', y=6.95)
    return p


def slide_forecast():
    p = Page()
    p.title('2026/27: about %s M bags (%s–%s), %s on 2025/26; heat is the swing factor' % (
        fr(FC['central'] / 1000, 1), fr(FC['lo'] / 1000, 1), fr(FC['hi'] / 1000, 1), pct(100 * (FC['central'] / FC['base_exports'] - 1), 0)))
    I = J['inputs_2026']
    r26 = J['rain_2026']
    CT = J['coffee_zone_tmax']
    rows = [['Driver, 2026', 'Value', 'Evidence', 'For 2026/27'],
            ['2025/26 shock (IHCAFE exports)', pct(100 * (FC['base_exports'] / AN.PSD[2024] - 1), 0) + ' output', 'mean reversion: robust', [('− part does not repeat', dict(b=True, color=RED))]],
            ['Heat, coffee zones, 1–18 Sep', '+' + fr(CT['sep_2026_to_18'], 1) + ' °C (above any Sep)', 'Sep–Oct: r = −0,45', [('− heat before harvest', dict(b=True, color=RED))]],
            ['Rain Jun–Aug (fruit fill)', pct(r26['Jun-Aug'], 0), 'no link in history', [('− outside history', dict(b=True, color=RED))]],
            ['Fertiliser: urea price', fr(I['urea_2026'], 0) + ' $/t (' + pct(100 * (I['urea_2026'] / I['urea_2025'] - 1), 0) + ')', 'nitrogen: tightest link', [('− dearer nitrogen', dict(b=True, color=RED))]],
            ['Cash: export revenue to 14 Jul', '2 158 M$ (record)', 'weak link (p = 0,06)', [('+ money for inputs', dict(b=True, color=GREEN))]],
            ['Rain Dec–Mar (before flowering)', pct(r26['dry Dec-Mar'], 0), 'weak alone', [('+ moist flowering', dict(b=True, color=GREEN))]],
            ['Rust incidence (end Jan 2026)', '8,44 % (7,57 before)', '2012/13: 25 % of area', [('− mild, yellow alert', dict(b=True, color=AMBER))]],
            ['El Niño (ONI Jun–Aug)', fr(I['oni_last'].get('2026-07', 1.8), 1) + ', very strong by Dec', 'acts through heat', [('≈ bigger risk for 2027/28', dict(b=True, color=AMBER))]]]
    yy = p.table(0.45, 1.2, [2.35, 1.85, 1.65, 1.9], 0.34, rows, sz=8.2)
    Mx = FC['methods']
    cats = ['USDA', 'Avg 2 y', 'No heat', 'Mild', 'Central', 'Hot', 'Mix']
    keys = ['USDA (May 2026)', 'A. Average of last 2 years', 'B. Model: mean reversion + price + Dec-Mar rain', 'C. Model B + Sep-Oct heat, mild scenario',
            'C. Model B + Sep-Oct heat, central scenario', 'C. Model B + Sep-Oct heat, hot scenario', 'Combination A and C central']
    vals = [(Mx[k]['export_base'] or Mx[k]['usda_base']) / 1000 for k in keys]
    px, py, pw, ph, Y = p.bars(8.35, 1.5, 4.55, 3.4, cats, vals, [PALE, BLUE, BLUE, ORANGE, ORANGE, ORANGE, GREEN], 7, 1, labels=None,
                               lay=(0.1, 0.05, 0.88, 0.8), label_sz=8)
    for i, v in enumerate(vals):
        p.text(px + pw * (i + 0.5) / len(vals) - 0.3, Y(v) + 0.05, 0.6, 0.22, [(fr(v, 2), dict(b=True, color=INK if i == 0 else 'FFFFFF'))], sz=8, algn='ctr')
    p.text(8.35, 1.2, 4.55, 0.26, [('2026/27 production, M bags (on the export-implied base)', dict(color=GREY))], sz=8.8)
    p.hline(px, px + pw, Y(FC['base_exports'] / 1000), NAVY, w=0.02, dash=True)
    p.text(8.35, 4.95, 4.55, 1.2, ['Dashed: 2025/26 implied by exports, %s. Orange: model with Sep–Oct heat at +%s / +%s / +%s °C. Mix = Avg 2 y and central (back-test miss %s = the range).' % (
        fr(FC['base_exports'] / 1000, 2), fr(FC['heat']['mild'], 1), fr(FC['heat']['central'], 1), fr(FC['heat']['hot'], 1), pct(100 * FC['mape'], 1, False)),
        'Without the heat term the mix gives %s.' % fr(FC['no_heat']['comb'] / 1000, 2)], sz=8.2)
    p.text(0.45, yy + 0.1, 7.75, 1.3, [('What to watch, in order', dict(b=True, color=NAVY, sz=9.5)),
                                       '1. Temperatures for the rest of Sep and Oct 2026 in the coffee zones · 2. the final 2025/26 export total · 3. IHCAFE exports Nov 2026–Feb 2027 (2025/26 was front-loaded) · '
                                       '4. IHCAFE rust bulletins · 5. fertiliser imports and urea price · 6. rain Dec 2026–Apr 2027 for the 2027/28 flowering (El Niño).'], sz=8.4, fill='F2F5F8')
    p.source('Forecast_2026_27 and Exports_nowcast sheets. World Bank Pink Sheet (Jan–Aug 2026); GPCC First Guess 2026; ERA5-Land (Open-Meteo, to 18 Sep 2026, preliminary); El Heraldo 15 Feb 2026 (rust); '
             'La Prensa 15 Jul 2026 (revenue); NOAA CPC ENSO discussion 10 Sep 2026; USDA Coffee Annual Honduras May 2026 (6,03 M).', y=6.95)
    return p


SLIDES = [('answer', slide_answer), ('production', slide_production), ('biennial', slide_biennial), ('yield', slide_yield), ('fert', slide_fert),
          ('weather', slide_weather), ('backtest', slide_backtest), ('nowcast', slide_nowcast), ('forecast', slide_forecast)]

if __name__ == '__main__':
    only = sys.argv[1:]
    pages = []
    for name, fn in SLIDES:
        pg = fn()
        pages.append(pg.s)
        if not only or name in only:
            pg.render(HERE + 'preview_yield_%s.png' % name)
            print('preview', name)
    out = HERE + 'Honduras_yield_drivers_forecast.pptx'
    save(pages, out, 'Honduras coffee: what drives output, and 2026/27')
    print('saved', out)
