"""Honduras coffee after the rust: price 2005-2026, rust incidence, varieties, financing, yields and costs.
Every number is read from a file in research/honduras/ (see SOURCES in each slide). Writes a PPTX with native charts
and one PNG preview per slide."""
import json, os, sys
from deckkit import Page, save, fr, pct, NAVY, BLUE, ORANGE, GREY, INK, LIGHT, HERE
sys.path.insert(0, HERE + '../data')
import finance_varieties as FV
FX = FV.fx()
FG = FV.farmgate()
RED, GREEN, VER = 'C00000', '2E7D32', '7F7F7F'
AREA = json.load(open(HERE + '../data/area_trees_attache.json'))

D = json.load(open(HERE + '../data/worldbank_prices.json'))
ANN, MON = D['annual'], D['monthly']
YEARS = list(range(2005, 2027))
LAST = sorted(MON)[-1]                                   # latest month published
N_2026 = int(LAST[5:])
MN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def ann(y):
    """Annual mean of the monthly Pink Sheet values (2026 = months published so far)."""
    v = [MON['%dM%02d' % (y, m)]['arabica'] for m in range(1, 13) if '%dM%02d' % (y, m) in MON]
    return sum(v) / len(v)


def slide_price():
    p = Page()
    A = {y: ann(y) for y in YEARS}
    for y in YEARS[:-1]:
        assert abs(A[y] - ANN[str(y)]['arabica']) < 0.001, y      # same as the annual file
    ch = lambda a, b: 100 * (A[b] / A[a] - 1)
    p.title('Arabica price, annual average 2005–2026: ×2,4 to 2011, halved by 2013, +44 % in 2014')
    p.bullets([
        '2005 → 2011: %s → %s $/kg (%s). 2011 → 2013: %s, down to %s $/kg, the rust years. 2014: %s $/kg (%s), Brazil drought'
        % (fr(A[2005]), fr(A[2011]), pct(ch(2005, 2011), 0), pct(ch(2011, 2013)), fr(A[2013]), fr(A[2014]), pct(ch(2013, 2014))),
        '2015–2019: between %s and %s $/kg; 2018 (%s) and 2019 (%s) were the lowest annual averages since 2007. 2020–2022: back up to %s $/kg'
        % (fr(min(A[y] for y in range(2015, 2020))), fr(max(A[y] for y in range(2015, 2020))), fr(A[2018]), fr(A[2019]), fr(A[2022])),
        '2025: record %s $/kg (%s). 2026 so far (Jan–%s): %s $/kg, %s on 2025'
        % (fr(A[2025]), pct(ch(2024, 2025)), MN[N_2026 - 1], fr(A[2026]), pct(ch(2025, 2026)))])
    cats = [str(y) if y < 2026 else '2026*' for y in YEARS]
    vals = [round(A[y], 3) for y in YEARS]
    cols = [ORANGE if y in (2012, 2013) else NAVY if y == 2014 else LIGHT if y == 2026 else BLUE for y in YEARS]
    X, Y0, WW, HH = 0.45, 1.95, 12.4, 4.55
    lay = (0.045, 0.1, 0.945, 0.74)
    px, py, pw, ph = p.plot_frame(X, Y0, WW, HH, lay)
    n = len(YEARS)
    i0 = YEARS.index(2012)
    p.band(px + pw * i0 / n, px + pw * (i0 + 2) / n, py, py + ph, 'FCE4D6', ['Rust epidemic', '2012–13'])
    px, py, pw, ph, Y = p.bars(X, Y0, WW, HH, cats, vals, cols, 10, 2, labels=[fr(v) for v in vals], lay=lay, ylab='US$ per kg (annual average)', label_sz=9)
    # year-on-year change under the axis
    for i, y in enumerate(YEARS[1:], 1):
        c = ch(y - 1, y)
        p.text(px + pw * (i + 0.5) / n - 0.3, py + ph + 0.26, 0.6, 0.2, [(pct(c, 0 if abs(c) >= 1 else 1), dict(color='2E7D32' if c > 0 else 'C00000'))], sz=8, algn='ctr')
    p.text(X - 0.05, py + ph + 0.26, 0.6, 0.2, ['YoY'], sz=8, color=GREY)
    i14 = YEARS.index(2014)
    p.text(px + pw * (i14 + 0.5) / n - 0.75, Y(A[2014]) - 0.62, 1.5, 0.36, [('Brazil drought', dict(b=True, color=NAVY))], sz=8.5, algn='ctr', anchor='b')
    i25 = YEARS.index(2025)
    p.text(px + pw * (i25 + 0.5) / n - 0.75, Y(A[2025]) - 0.62, 1.5, 0.36, [('Record', dict(b=True, color=NAVY))], sz=8.5, algn='ctr', anchor='b')
    p.source('Source: World Bank Pink Sheet (update of 2 Sep 2026), "Coffee, Arabica" = ICO other milds (Honduras\'s group), ex-dock; annual average = mean of the 12 monthly prices. '
             '*2026 = Jan–%s. 2014: mean 4,425 $/kg, shown rounded half-up (4,43). YoY = change on the previous year.' % MN[N_2026 - 1])
    return p


def status_tag(st):
    return {'USDA': 'USDA report (read)', 'FAO': 'FAOSTAT (read)', 'DOC': 'document read', 'PRESS': 'press, NOT verified'}[st]


def slide_cost():
    p = Page()
    A = {y: ann(y) for y in YEARS}
    QQ = 46.0                                                 # kg per quintal oro
    ex = {int(e['crop'][-2:]) + 2000: e for e in FV.EXPORT_PRICE}   # 2011/12 plotted at 2012
    fg = {}
    for y, v in FG.items():
        if 2005 <= y <= 2024:
            usd_t = v['LCU'] / FX[y] if y == 2024 else v['USD']      # FAOSTAT 2024 USD cell repeats 2023: use LCU / rate
            fg[y] = usd_t / 1000 * QQ
    shares = {y: fg[y] / (A[y] * QQ) * 100 for y in fg if y != 2024}
    c19 = [c for c in FV.COSTS if c['year'] == 2019]
    p.title('2018–19: Honduras sold coffee at ~107 $ per quintal, below every cost estimate (117–160 $)')
    p.bullets([
        'Cost of a quintal oro (46 kg): 117 $ (undated), ~120–127 $ (2019), 130 $ (2023), 160 $ full cost (PROMECAFE 2018). IHCAFE 2012: above 150 $/qq is "favourable"',
        '2018/19 export price %s $/qq (USDA): %s–%s $ under those costs, before the 13,25 $/qq deduction. 2012/13: %s $/qq, under the 150 $ mark as rust cut yields'
        % (fr(ex[2019]['usd_qq']), fr(117 - ex[2019]['usd_qq'], 0), fr(160.5 - ex[2019]['usd_qq'], 0), fr(ex[2013]['usd_qq'], 0)),
        'Growers get %s–%s %% of the world price (FAOSTAT official farm-gate price, 2005–08 and 2022–23)' % (fr(min(shares.values()), 0), fr(max(shares.values()), 0))])
    X, Y0, WW, HH = 0.35, 2.15, 8.5, 4.6
    lay = (0.075, 0.06, 0.9, 0.8)
    cats = [("'%02d" % (y % 100)) for y in YEARS]
    wb = [round(A[y] * QQ, 1) for y in YEARS]
    px, py, pw, ph, Y = p.lines(X, Y0, WW, HH, cats, [dict(name='Arabica other milds, $/qq', values=wb, color=BLUE, marker=False, width=2.5)],
                                0, 400, 50, lay=lay, ylab='US$ per quintal oro (46 kg)')
    n = len(YEARS)
    XX = lambda y: px + pw * (YEARS.index(y) + 0.5) / n
    for y, e in ex.items():
        p.dot(XX(y), Y(e['usd_qq']), 0.15, NAVY, 'diamond')
    for y, v in fg.items():
        p.dot(XX(y), Y(v), 0.13, GREEN, 'ellipse', hollow=(y == 2024))
    for c in FV.COSTS:
        if c['year'] is None:
            continue
        v = (c['usd_qq'] + c['lo']) / 2 if c.get('lo') else c['usd_qq']
        p.dot(XX(c['year']) + (0.12 if c['usd_qq'] == 135 else 0), Y(v), 0.13, RED, 'rect', hollow=(c['status'] == 'PRESS'))
    # labels for the key points
    p.text(XX(2019) - 0.2, Y(ex[2019]['usd_qq']) + 0.05, 1.3, 0.2, [('export %s' % fr(ex[2019]['usd_qq'], 0), dict(b=True, color=NAVY))], sz=8)
    p.text(XX(2019) + 0.2, Y(135) - 0.3, 1.2, 0.2, [('cost 120–135', dict(b=True, color=RED))], sz=8)
    p.text(XX(2018) - 0.62, Y(160.5) - 0.3, 1.3, 0.2, [('full cost 160', dict(b=True, color=RED))], sz=8)
    p.text(XX(2012) - 0.75, Y(150) + 0.06, 1.5, 0.2, [('"favourable" 150', dict(b=True, color=RED))], sz=8)
    p.text(XX(2013) - 0.2, Y(ex[2013]['usd_qq']) + 0.06, 1.2, 0.2, [('export 140', dict(b=True, color=NAVY))], sz=8)
    p.text(XX(2023) - 0.25, Y(130) + 0.08, 1.2, 0.2, [('cost 130', dict(b=True, color=RED))], sz=8)
    p.text(XX(2006) - 0.1, Y(fg[2005]) + 0.04, 1.4, 0.2, [('farm-gate 81–109', dict(b=True, color=GREEN))], sz=8)
    p.text(XX(2022) - 1.0, Y(fg[2022]) - 0.1, 0.9, 0.2, [('farm-gate', dict(b=True, color=GREEN))], sz=8, algn='r')
    p.legend(X + 2.55, Y0 - 0.27, [(BLUE, 'World price (other milds)', 'line'), (NAVY, 'Honduras export price (USDA)', 'box'),
                                           (GREEN, 'Farm-gate (FAOSTAT)', 'box'), (RED, 'Cost (hollow = not verified)', 'box')], sz=8)
    # table on the right
    rows = [['Cost or threshold', '$ / qq', 'Source']]
    for c in FV.COSTS:
        v = ('%s–%s' % (fr(c['lo'], 0), fr(c['usd_qq'], 0))) if c.get('lo') else fr(c['usd_qq'], 0 if c['usd_qq'] == int(c['usd_qq']) else 1)
        rows.append([('%s: %s' % (c['year'] or 'n.d.', c['kind'])), v, ('✔ USDA 2012' if c['status'] == 'USDA' else '⚠ ' + c['src'].split(' (')[0].split(';')[0].split(',')[0])])
    p.table(9.05, 2.05, [2.2, 0.55, 1.35], 0.52, rows, sz=7)
    p.text(9.05, 2.05 + 0.52 * len(rows) + 0.05, 4.1, 0.6, [('✔ = read in the document   ⚠ = web-search extract, page not accessible', dict(color=GREY)),
                                                           ('1 qq = 1 quintal oro = 46 kg = 100 lb of green coffee', dict(color=GREY))], sz=7.5)
    p.source('Sources: World Bank Pink Sheet (arabica other milds, annual mean ×46); USDA FAS Coffee Annual Honduras 2012, 2014, 2020 (export prices, plotted at the second year of the crop); '
             'FAOSTAT producer price of green coffee, official values only (2024: lempira value ÷ FAOSTAT exchange rate, the USD cell repeats 2023, hollow); cost figures as listed.')
    return p


def slide_varieties():
    p = Page()
    AMBER, PALE = 'ED7D31', 'A9D18E'
    oct17 = [a for a in FV.ADOPTION if a['when'] == 'Oct 2017'][0]
    p.title('IHCAFE bred 3 rust-resistant varieties (1990–2004), none new until 2024; Lempira failed in 2016')
    p.bullets([
        'Released 1990, 1998, 2004 (IHCAFE study 2019 ✔, World Coffee Research ✔). Feb 2024: Ihcatú 75, Anacafé 14, Obatá, bred abroad and released by IHCAFE ✔',
        'Planted: resistant varieties = 65 % of the area since 2012, mostly Lempira (IHCAFE ✔); USDA: 50 % of the area in 2013, 60 % of producers in 2014',
        'Lempira: tolerant from 2002, susceptible in 2016, nationwide by 2019 (IHCAFE ✔). IHCAFE 90: 20 % of plants susceptible from 2016. Parainema: resistant to 2019–21'])
    x0, x1, yT = 0.45, 8.45, 2.0           # timeline 1988 -> 2027
    Y0, Y1 = 1988, 2027
    T = lambda y: x0 + 2.0 + (x1 - x0 - 2.0) * (y - Y0) / (Y1 - Y0)
    for y in range(1990, 2027, 5):
        p.vline(T(y), yT + 0.35, yT + 4.05, 'E3E8EB', 0.012)
        p.text(T(y) - 0.3, yT + 4.07, 0.6, 0.2, [str(y)], sz=8, color=GREY, algn='ctr')
    p.band(T(2012), T(2014), yT + 0.35, yT + 4.05, 'FCE4D6')
    p.text(T(2013) - 0.6, yT + 0.12, 1.2, 0.2, [('rust 2012–13', dict(b=True, color=ORANGE))], sz=7.5, algn='ctr')
    E = 2026.7
    rows = [('IHCAFE 90', 'Catimor', 1990, [(1990, 2016, GREEN), (2016, E, AMBER)], '1990', 'resistant 1990–2015; ~20 % of plants susceptible from 2016'),
            ('Lempira', 'Catimor', 1998, [(1998, 2002, GREEN), (2002, 2016, AMBER), (2016, E, RED)], '1998', 'tolerant 2002–15 (rust seen from 2007); susceptible 2016'),
            ('Parainema', 'Sarchimor', 2004, [(2004, 2021.4, GREEN), (2021.4, E, PALE)], '2004', 'resistant in IHCAFE tests to 2019, per USDA to 2021'),
            ('Ihcatú 75, Anacafé 14, Obatá', 'bred in Brazil / Guatemala', 2024, [(2024.15, E, GREEN)], 'Feb 2024', 'seed for ≥ 1 500 manzanas in 2024')]
    for k, (nm, fam, ry, segs, rtxt, note) in enumerate(rows):
        yy = yT + 0.6 + k * 0.85
        p.text(x0, yy - 0.05, 2.0, 0.4, [(nm, dict(b=True)), (fam, dict(color=GREY, sz=7.5))], sz=8.5)
        for a, b, c in segs:
            p.rect(T(a), yy + 0.02, T(b) - T(a), 0.2, c)
        p.text(T(ry) - 0.55, yy + 0.24, 1.1, 0.18, [rtxt], sz=7, color=GREY, algn='ctr')
        p.text(T(ry) if ry < 2020 else T(E) - 3.4, yy - 0.21, 3.4, 0.2, [note], sz=7.5, color=INK, algn='l' if ry < 2020 else 'r')
    for y in (2018.3, 2019.3):
        p.vline(T(y), yT + 0.35, yT + 4.05, '8497B0', 0.012)
    p.text(T(2018.3) - 1.75, yT + 3.62, 1.7, 0.4, [('Apr 2018: 4 new strains', dict(color=NAVY, b=True)), ('Apr 2019: 16 new strains', dict(color=NAVY, b=True))], sz=7.5, algn='r')
    p.legend(x0 + 0.2, yT + 4.35, [(GREEN, 'resistant', 'box'), (AMBER, 'tolerant / partly susceptible', 'box'), (RED, 'susceptible', 'box'),
                                   (PALE, 'no statement after 2021', 'box')], sz=8)
    rows = [['When', 'Share with resistant varieties', 'Source']]
    what = {'Jun 2013': '%d %% of the coffee area', 'since 2012': '%d %% of the area, mostly Lempira', 'Apr 2014': '%d %% of producers (national)',
            '2014': '%d %% of farms, 5 departments', '24 Aug 2017': '%d %% of the park (IHCAFE adviser)', '~2020': '%d %% of cultivation'}
    for a in FV.ADOPTION:
        if a['when'] == 'Oct 2017':
            txt = 'Lempira = %s %% of monitored farms → still resistant ≈ %s %%' % (fr(a['lempira'], 0), fr(a['resistant'], 0))
        else:
            txt = what[a['when']] % a['resistant']
        src_ = a['src'].split(' (')[0].replace('GAIN', 'USDA').replace('Morales & Grajeda ', '')
        rows.append([a['when'], txt, ('✔ ' if a['status'] in ('USDA', 'DOC') else '⚠ ') + src_])
    yb = p.table(8.75, 2.05, [0.8, 2.25, 1.3], [0.32] + [0.4] * (len(rows) - 1), rows, sz=7.5)
    p.text(8.75, yb + 0.08, 4.35, 1.1, [('Count of releases', dict(b=True, color=NAVY)),
                                        ('Bred by IHCAFE: 1990, 1998, 2004 · none 2005–2023', {}),
                                        ('Sep 2023: "at least 4" announced → Feb 2024: 3 presented (bred abroad)', {}),
                                        ('⚠ = page not downloadable (IHCAFE bulletin Oct 2017, 2020 article)', dict(color=GREY, sz=7))], sz=8)
    p.source('✔ Morales & Grajeda (IHCAFE), "Durabilidad de la resistencia genética a la roya … al 2019", PROMECAFE symposium 2019; World Coffee Research variety pages; '
             'El Heraldo 29 Feb 2024; La Prensa 24 Aug 2017 and 29 Sep 2023; USDA Coffee Annual 2013–2021. The IHCAFE study also lists the Icatu 75 line as susceptible since 2016 and Obatá as 20 % susceptible.')
    return p


def slide_rust():
    p = Page()
    pts = [r for r in FV.RUST if r['unit'].startswith('national average')]
    p.title('Rust since the epidemic: national incidence 12 % in 2014, 2,9–5,8 % in 2022–25, 8,4 % in March 2026')
    p.bullets([
        '2012/13: rust hit 25 % of the coffee area (71 000 ha); 22 000 ha were lost entirely (10 000 families) and 58 000 ha lost half their crop (20 000 families)',
        'April 2014 survey: national incidence 12 %, 1 % of farms severely hit. After hurricanes Eta and Iota: 15–25 % in five departments (end 2020)',
        'March 2026: 8,44 % (from 7,57 %), the highest national average USDA reports since 2014; Comayagua 14,1 %. IHCAFE rule: 15 % damage ≈ −20 % production'])
    cats = [r['when'] + (' (fcst)' if 'forecast' in r['unit'] else '') for r in pts]
    vals = [r['value'] for r in pts]
    cols = [LIGHT if 'forecast' in r['unit'] else (RED if r['when'] == 'Mar 2026' else BLUE) for r in pts]
    X, Y0, WW, HH = 0.45, 2.25, 6.6, 4.5
    p.bars(X, Y0, WW, HH, cats, vals, cols, 15, 5, labels=[fr(v, 2 if v != int(v) else 0) + ' %' for v in vals], lay=(0.08, 0.06, 0.9, 0.82),
           ylab='National average rust incidence, % (IHCAFE surveys)', label_sz=9)
    rows = [['When', 'Other rust facts (not comparable with the bars)']]
    for r in FV.RUST:
        if r['unit'].startswith('national average'):
            continue
        if r.get('n'):
            txt = '%d new rust strains identified' % r['n']
        elif r['value'] is None:
            txt = '22 000 ha total loss; 58 000 ha −50 % of production'
        elif r.get('lo'):
            txt = '%d–%d %% incidence in 5 departments (after Eta and Iota)' % (r['lo'], r['hi'])
        else:
            txt = '%s %s' % (fr(r['value'], 0), r['unit'])
        rows.append([r['when'], txt])
    rows.append(['Apr 2022', 'farms: 66 % low, 29 % medium, 5 % high'])
    rows.append(['Apr 2024', 'farms: 76 % low, 19 % medium, 5 % high'])
    rows.append(['Apr 2025', 'farms: 16,7 % medium, 7,8 % high, 21,6 % very high (> 15 %)'])
    p.table(7.45, 2.1, [0.85, 4.55], 0.34, rows, sz=7.5)
    p.source('Source: USDA FAS Coffee Annual Honduras 2014–2026, quoting IHCAFE and its early-warning system (SAT). The 2024/25 bar is the IHCAFE forecast average for Jul 2024–Aug 2025. '
             'The 2023 value (5,8 %) is repeated word for word in the 2024 report, so it is shown once.')
    return p


def slide_finance():
    p = Page()
    items = [f for f in FV.FINANCE if f.get('usd_m') or f.get('lps_m')]
    def usd(f):
        return f['usd_m'] if f.get('usd_m') else f['lps_m'] / FX[f['year']]
    per_prod = 12e6 / 91778
    l200 = 200 / FX[2018]
    p.title('Money for growers: rust credit in 2013, a 77 M$ loan in 2018, free fertiliser since 2020, mostly debt')
    p.bullets([
        'Growers pay in too: 13,25 $ per quintal sold since 2004 (9 $ trust fund, returned if no debt; 1 $ old 1999–2001 loans; 3,25 $ IHCAFE, roads, 2002 loan)',
        '2012–13 rust loans (10 %%, 7 years) were due by 2019, when prices were 2,9 $/kg. 2018 loan: L200/qq ≈ %s $ (%s %% of the 107 $ export price), repaid at 1,50 $/qq'
        % (fr(l200, 1), fr(l200 / 106.89 * 100, 0)),
        '2020–21 fertiliser bonus: 12 + 12,5 M$ for ~91 800 producers ≈ %s $ per producer a year. June 2021: growers owed ≈ L5 565 M (%s M$) ⚠'
        % (fr(per_prod, 0), fr(FV.DEBT['lps_m'] / FX[2021], 0))])
    short = {id(f): f['lab'].replace(' · ', '\\n') for f in items}
    cats = [short[id(f)].replace('\\n', ' ') for f in items]
    vals = [round(usd(f), 1) for f in items]
    cols = [NAVY if f['status'] in ('USDA', 'DOC') else 'A6A6A6' for f in items]
    X, Y0, WW, HH = 0.45, 2.3, 6.2, 4.4
    px, py, pw, ph, Y = p.bars(X, Y0, WW, HH, ['' for _ in cats], vals, cols, 100, 20, labels=[fr(v, 0 if v >= 20 else 1) for v in vals], lay=(0.07, 0.05, 0.92, 0.72),
                               ylab='US$ million (lempiras ÷ FAOSTAT rate of the year)', label_sz=9)
    n = len(cats)
    for i, f in enumerate(items):
        a, b = short[id(f)].split('\\n')
        p.text(px + pw * (i + 0.5) / n - 0.4, py + ph + 0.05, 0.8, 0.4, [(a, dict(b=True)), b], sz=7.5, algn='ctr')
    p.legend(X + 0.4, Y0 + HH + 0.02, [(NAVY, 'amount read (USDA report or article)', 'box'), ('A6A6A6', 'press extract, not verified ⚠', 'box')], sz=8)
    rows = [['Year', 'Programme', 'Who / terms']]
    for f in FV.FINANCE:
        rows.append([str(f['year']), ('⚠ ' if f['status'] == 'PRESS' else '') + f['name'], f['who'] + ('; ' + f['terms'] if f['terms'] and len(f['terms']) < 60 else '')])
    p.table(6.95, 2.05, [0.45, 2.4, 3.0], [0.3] + [0.4] * (len(rows) - 1), rows, sz=6.5)
    p.source('*2013: L1 715 M made available at 10 %%, 7 years, but only L335 M (≈ %s M$) used by April 2014 (El Heraldo, 7 Apr 2014, read). ' % fr(335 / FX[2014], 0) + 'Sources: USDA FAS Coffee Annual Honduras 2011, 2015–2017, 2020, 2021, 2024 (amounts, terms, deductions); FAOSTAT exchange rates (L per US$: 2013 %s, 2019 %s, 2025 %s). '
             '⚠ = web-search extract, page not opened (2025 bono, 2021 debt). Decree 93-2018 terms read in El Heraldo, 29 Aug 2018: L200 per quintal oro (USDA wrote "about $25 per 100 pounds", which is wrong).'
             % (fr(FX[2013]), fr(FX[2019]), fr(FX[2025])))
    return p


def slide_yield():
    p = Page()
    yrs = AREA['years']
    prod = AREA['psd_full']['Arabica Production']
    yl = [round(prod[str(y)] / b, 2) for y, b in zip(yrs, AREA['bearing_kha'])]
    Yd = dict(zip(yrs, yl))
    reg = {}
    for cy, d in FV.REGISTRY.items():
        reg[cy] = {k: d[k][2] / d[k][1] for k in ('small', 'medium', 'large')}
        tot = [sum(d[k][i] for k in ('small', 'medium', 'large')) for i in range(3)]
        reg[cy]['all'] = tot[2] / tot[1]
    r25 = reg['2024/25']
    pk = max(yrs, key=lambda y: Yd[y])
    p.title('Yield: 17–20 bags/ha since 2021, a third below the 2016/17 peak; large farms get 1,7× small ones')
    p.bullets([
        'Yield per bearing ha (USDA production ÷ bearing area): %s in 2011/12, %s in 2012/13 (rust), peak %s in %d/%02d, %s in 2025/26 (60-kg bags; 18 bags/ha ≈ 16 qq/mz)'
        % (fr(Yd[2011], 1), fr(Yd[2012], 1), fr(Yd[pk], 1), pk, (pk + 1) % 100, fr(Yd[2025], 1)),
        'IHCAFE registry 2024/25: small farms %s bags/ha, medium %s, large %s. Small farms hold %s %% of the area'
        % (fr(r25['small'], 1), fr(r25['medium'], 1), fr(r25['large'], 1), fr(FV.REGISTRY['2024/25']['small'][1] / sum(FV.REGISTRY['2024/25'][k][1] for k in ('small', 'medium', 'large')) * 100, 0)),
        'The PAPP replanting target, 45 qq per manzana (≈ 49 bags/ha), is %s× today\'s national yield' % fr(45 * 46 / 0.7 / 60 / Yd[2025], 1)])
    cats = ['%02d/%02d' % (y % 100, (y + 1) % 100) for y in yrs]
    X, Y0, WW, HH = 0.45, 2.2, 8.2, 4.5
    px, py, pw, ph, Y = p.lines(X, Y0, WW, HH, cats, [dict(name='Yield, 60-kg bags per bearing ha', values=yl, color=BLUE, width=2.5)], 10, 30, 5,
                                lay=(0.06, 0.06, 0.92, 0.82), ylab='60-kg bags per bearing hectare', xlab_every=2)
    n = len(yrs)
    for y in (2011, 2012, pk, 2025):
        i = yrs.index(y)
        p.text(px + pw * (i + 0.5) / n - 0.4, Y(Yd[y]) + (0.08 if y == 2012 else -0.3), 0.8, 0.22, [(fr(Yd[y], 1), dict(b=True, color=NAVY))], sz=9, algn='ctr')
    # registry bars as a small table-chart on the right
    rows = [['IHCAFE registry', 'Small', 'Medium', 'Large', 'All']]
    for cy in FV.REGISTRY:
        rows.append([cy] + [fr(reg[cy][k], 1) for k in ('small', 'medium', 'large', 'all')])
    rows.append(['Farmers 2024/25'] + ['{:,}'.format(FV.REGISTRY['2024/25'][k][0]).replace(',', ' ') for k in ('small', 'medium', 'large')] +
                ['{:,}'.format(sum(FV.REGISTRY['2024/25'][k][0] for k in ('small', 'medium', 'large'))).replace(',', ' ')])
    p.table(8.95, 2.3, [1.3, 0.72, 0.72, 0.72, 0.72], 0.4, rows, sz=8)
    p.text(8.95, 2.3 + 0.4 * len(rows) + 0.05, 4.2, 0.3, [('60-kg bags per harvested hectare, registered farms', dict(color=GREY))], sz=7.5)
    ks = ('small', 'medium', 'large')
    v25 = [round(r25[k], 2) for k in ks]
    p.bars(9.0, 5.05, 4.1, 1.8, ['Small', 'Medium', 'Large'], v25, [LIGHT, BLUE, NAVY], 30, 10, labels=[fr(v, 1) for v in v25],
           lay=(0.1, 0.08, 0.88, 0.72), ylab='2024/25, bags per ha', label_sz=9)
    p.source('Sources: USDA PSD (production, 1 000 bags, marketing year Oct–Sep) and USDA FAS Coffee Annual Honduras (bearing area, kha); IHCAFE Coffee Statistics Reports 2022/23–2024/25 as printed in '
             'USDA reports 2024–2026 (table 1). Last point (26/27) = USDA forecast. PAPP target: USDA 2017. 1 manzana = 0,7 ha; 1 qq = 46 kg.')
    return p


SLIDES = [('price', slide_price), ('cost', slide_cost), ('varieties', slide_varieties), ('rust', slide_rust), ('finance', slide_finance), ('yield', slide_yield)]

if __name__ == '__main__':
    import sys
    only = sys.argv[1:]
    pages = []
    for name, fn in SLIDES:
        pg = fn()
        pages.append(pg.s)
        if not only or name in only:
            pg.render(HERE + 'preview_%s.png' % name)
            print('preview', name)
    out = HERE + 'Honduras_price_finance_varieties.pptx'
    save(pages, out, 'Honduras coffee: price, rust, varieties, finance')
    print('saved', out)
