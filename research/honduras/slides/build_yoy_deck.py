"""Honduras coffee year by year: productivity, fertiliser, rust and varieties, financing, lempira. Data: research/honduras/yoy/data_yoy.py
(same numbers as excel/Honduras_YoY_productivity_inputs_finance_fx.xlsx). Writes a PPTX with native charts and PNG previews."""
import math, os, sys
from deckkit import Page, save, fr, pct, esc, NAVY, BLUE, ORANGE, GREY, INK, LIGHT, HERE, K, AXIS, GRID
sys.path.insert(0, HERE + '../yoy')
import data_yoy as D
from build_yield_deck import gbars, RED, GREEN, AMBER, PALE

FV = D.FV
R = {r['year']: r for r in D.build()}
YRS = D.YEARS
lab = lambda t: '%02d/%02d' % (t % 100, (t + 1) % 100)
ch = lambda a, b: pct(100 * (a / b - 1), 0) if a and b else '–'
yld = lambda t: R[t]['prod_kbags'] / R[t]['bear_kha']
kgt = lambda t: R[t]['prod_kbags'] * 60 / R[t]['trees_m'] / 1000
ureaL = lambda t: R[t]['urea_wb'] * R[t]['fx']
avg = lambda f, ys: sum(f(t) for t in ys) / len(ys)
sp = lambda v: format(round(v), ',').replace(',', ' ')
P0, P1 = (2016, 2017, 2018), (2022, 2023, 2024)


def slide_productivity():
    p = Page()
    p.title('Productivity really fell: −30 % per hectare and −48 % per tree since 2016–18')
    p.bullets(['Area and trees rose (+2 % and +39 % between 2016–18 and 2022–24) while output fell 28 %: yield per bearing hectare went from 25,7 to 18,2 bags.',
               'The IHCAFE registry says the same (16,6–17,7 bags/ha in 2022–24). 2025/26 recovers to about 19,5 on the export-implied crop.'], h=0.8, sz=10)
    cats = [lab(t) for t in YRS]
    vals = [yld(t) for t in YRS]
    colors = [PALE if t == 2026 else BLUE for t in YRS]
    px, py, pw, ph, Y = p.bars(0.45, 1.95, 7.7, 4.6, cats, vals, colors, 30, 5, labels=[fr(v, 1) for v in vals], lay=(0.06, 0.05, 0.93, 0.84),
                               ylab='Bags of 60 kg per bearing hectare', label_sz=7.5, xlab_every=1)
    n = len(YRS)
    xi = lambda t: px + pw * (YRS.index(t) + 0.5) / n
    for t in (2022, 2023, 2024):
        g = D.REG[t]
        p.dot(xi(t), Y(g['bags'] / g['ha']), 0.13, GREEN, geom='diamond')
    p.dot(xi(2025), Y(D.PROD_EXPORT_IMPLIED[2025] / D.BEAR[2025]), 0.15, ORANGE, hollow=True)
    p.legend(0.95, 6.62, [(BLUE, 'USDA production ÷ bearing area', 'box'), (GREEN, 'IHCAFE registry (harvested ha)', 'box'), (ORANGE, '2025/26 on export-implied crop', 'box'), (PALE, '2026/27 USDA forecast', 'box')], sz=8.5)
    rows = [['', '2016–18', '2022–24', 'Change']]
    spec = [('Bearing area (kha)', lambda t: R[t]['bear_kha'], 0), ('Bearing trees (M)', lambda t: R[t]['trees_m'], 0), ('Trees per ha', lambda t: R[t]['trees_m'] * 1000 / R[t]['bear_kha'], 0),
            ('Production (M bags)', lambda t: R[t]['prod_kbags'] / 1000, 2), ('Bags per ha', yld, 1), ('kg green per tree', kgt, 2),
            ('Nitrogen use, all crops (kt)', lambda t: R[t]['n_t'] / 1000, 0), ('N per bearing coffee ha (kg)', lambda t: R[t]['n_t'] / R[t]['bear_kha'], 0),
            ('Urea (L per t)', ureaL, 0), ('kg urea per kg coffee', lambda t: R[t]['arabica'] * 1000 / R[t]['urea_wb'], 1)]
    for nm, f, d in spec:
        a, b = avg(f, P0), avg(f, P1)
        c = RED if (b / a - 1) < -0.1 else (GREEN if (b / a - 1) > 0.1 else INK)
        rows.append([nm, fr(a, d), fr(b, d), [(pct(100 * (b / a - 1), 0), dict(b=True, color=c))]])
    p.table(8.45, 1.95, [2.35, 0.75, 0.75, 0.7], 0.34, rows, sz=8.3)
    p.text(8.45, 5.8, 4.55, 0.8, ['Per tree the fall looks worse because USDA counts 6 000 trees per hectare instead of 4 400: denser, younger plantings that are not yet at full crop.'], sz=8.3, fill='F2F5F8')
    p.source('USDA PSD (production, July 2026) and USDA FAS Coffee Annual Honduras 2011–2026 (bearing area and trees, attaché estimates); IHCAFE Coffee Statistics Reports 2022/23–2024/25 as printed by USDA; '
             'FAOSTAT nitrogen (all crops); World Bank urea and arabica; BCH lempira rate. 2025/26 export-implied: forecast workbook, Exports_nowcast.', y=6.95)
    return p


def slide_fert():
    p = Page()
    p.title('Growers did not use much less fertiliser; they paid up to 4 times more for it in lempiras')
    ys = [t for t in YRS if R[t]['n_t']]
    gbars(p, 0.45, 1.3, 6.3, 4.5, [lab(t) for t in ys], [dict(name='Nitrogen use', values=[R[t]['n_t'] / 1000 for t in ys], color='7F9F3F'),
                                                        dict(name='Urea imports', values=[(R[t]['urea_imp_t'] or 0) / 1000 if R[t]['urea_imp_t'] else None for t in ys], color=NAVY)],
          0, 200, 50, lay=(0.08, 0.04, 0.9, 0.86), xlab_every=2)
    p.text(0.45, 1.05, 6.3, 0.26, [('Thousand tonnes, all crops (FAOSTAT; 2022 imputed by FAO, no urea figure)', dict(color=GREY))], sz=8.8)
    p.legend(0.9, 5.92, [('7F9F3F', 'nitrogen use (t N)', 'box'), (NAVY, 'urea imports (t product)', 'box')], sz=8.5)
    cats = [lab(t) for t in YRS]
    vals = [ureaL(t) / 1000 for t in YRS]
    p.bars(7.0, 1.3, 5.9, 4.5, cats, vals, [RED if v > 10 else ORANGE for v in vals], 18, 3, labels=[fr(v, 1) if t in (2016, 2021, 2022, 2024, 2025, 2026) else '' for t, v in zip(YRS, vals)],
           lay=(0.08, 0.04, 0.9, 0.86), label_sz=8, xlab_every=2)
    p.text(7.0, 1.05, 5.9, 0.26, [('Urea, thousand lempiras per tonne (World Bank price × BCH rate; 2026 = Jan–Aug)', dict(color=GREY))], sz=8.8)
    b = D.BONO
    p.text(0.45, 6.15, 12.45, 0.75, ['Nitrogen 2022–24: 105 000 t a year, 4 % below 2016–18; the one-year cuts (2019 −30 %) line up with output. Urea in lempiras: 4 400 L/t in 2016, 17 100 in 2022, 8 400 in 2024, 14 900 in 2026. '
                                     'Bono Cafetalero (state gift): 25 188 t in 2020 (USDA), 216 223 qq in 2022, 300 000 qq in 2025, about 400 000 planned for 2026 (press, read) ≈ 8 % of urea imports by weight.'], sz=8.5, fill='F2F5F8')
    p.source('FAOSTAT Inputs / Fertilizers by nutrient and by product (bulk download Sep 2026); World Bank Pink Sheet (urea, Black Sea / Middle East); BCH daily reference rate; USDA GAIN 2021 (Bono 2020); '
             'La Prensa 27 Jul 2022 and El Heraldo 14 Feb 2026 (Bono, read).', y=6.95)
    return p


def slide_rust():
    p = Page()
    p.title('Rust: no yearly series is published openly, but every figure points to a comeback since 2020')
    rows = [['Year', 'When', 'Rust %', 'What it measures', 'Source']]
    for d in D.RUST:
        v = ('' if d['value'] is None else (fr(d['value'], 2 if d['value'] < 10 and d['value'] != int(d['value']) else 0)))
        if d.get('lo'):
            v = '%d–%d' % (d['lo'], d['hi'])
        rows.append([str(d['year']), d['when'], [(v + (' ⚠' if d['status'] == 'PRESS' else ''), dict(b=True, color=RED if d['status'] == 'PRESS' else INK))],
                     d['measure'], d['src'].replace('web search summary', 'search summary')])
    yy = p.table(0.45, 1.15, [0.55, 1.0, 0.75, 5.8, 1.7], [0.34] + [0.325] * (len(rows) - 1), rows, sz=7.3)
    p.text(0.45, yy + 0.08, 9.8, 0.55, ['IHCAFE rule: rust damage of 15 % ≈ 20 % less production (USDA 2017). Thresholds: 0–5 % low, 5–20 % medium. The monthly IHCAFE early-warning bulletins (about 1 200 farms) are no longer on ihcafe.hn: old links return the home page.'], sz=8.2)
    x0, w0 = 10.45, 2.45
    lines = [('Resistant varieties', dict(b=True, color=NAVY, sz=10)),
             ('Released by IHCAFE', dict(b=True, sz=8.8)),
             'IHCAFE 90 (1990), Lempira (1998), Parainema (2004); Ihcatú 75, Anacafé 14, Obatá (2024)',
             ('Share planted (resistant)', dict(b=True, sz=8.8))]
    for a in FV.ADOPTION:
        if a['status'] in ('USDA', 'DOC'):
            sc = {'Jun 2013': 'of area', 'since 2012': 'of area', 'Apr 2014': 'of producers', '2014': 'of farms, 5 depts', '24 Aug 2017': 'of plants'}.get(a['when'], '')
            lines.append('%s: %s %% %s' % (a['when'], fr(a['resistant'], 0), sc))
    lines += [('No national figure after 2017 (a 2020 "60 %" is only a web extract).', dict(color=GREY, sz=8)),
              ('Lempira, the main one, lost its resistance in 2016/17: part of the 60 % is susceptible again.', dict(b=True, color=RED, sz=8.5))]
    p.text(x0, 1.2, w0, 5.4, lines, sz=8.3, fill='F2F5F8')
    p.source('USDA FAS Coffee Annual Honduras 2013–2026; El Heraldo 13 May 2025 and 15 Feb 2026, La Prensa/EFE 1 Nov 2022 and El Heraldo 23 Jun 2024 (read); La Prensa 24 Aug 2017 (read); Morales & Grajeda (IHCAFE) PROMECAFE 2019 (read). ⚠ = search summary, page not read.', y=6.95)
    return p


def slide_finance():
    p = Page()
    p.title('Financing: one-off rescue programmes after each shock, no steady bank credit series')
    rows = [['Year', 'Programme', 'US$ M', 'L M', 'Terms / who', 'Status']]
    SHORT = {'Government loan to all growers (coffee crisis)': ('Government loan to all growers (price crisis)', '20 years; all producers'),
             'Coffee trust fund (Law of Financial Reactivation, 2003)': ('Coffee trust fund (law of 2003)', 'US$13,25/qq held back at sale; 87 000 producers (2011)'),
             'Rust credit made available (banks, BCH, BANHPROVI, BANADESA, IHCAFE)': ('Rust credit offered (banks, BCH, BANHPROVI, BANADESA, IHCAFE)', '10 %, 7 years; only L335 M used by Apr 2014'),
             'IHCAFE fertiliser credit line': ('IHCAFE fertiliser credit line', 'fertiliser at cost, 1 year, no interest'),
             'PAPP (IHCAFE + National Coffee Fund) and PEPP (BANADESA)': ('PAPP / PEPP replanting (IHCAFE, BANADESA)', '1 manzana per grower, no interest; 23 000 small growers'),
             'Decreto 93-2018: IHCAFE loan to growers (low prices, rust)': ('Decree 93-2018: IHCAFE loan (low prices, rust)', 'L200 per qq produced in 2016/17; repaid 1,50 $/qq'),
             'Fondo para el Sector Cafetero (BANHPROVI)': ('BANHPROVI guarantee fund for coffee', 'backs refinancing of growers\' debt'),
             'Bono Cafetalero (PCM 030-2020): free fertiliser': ('Bono Cafetalero: free fertiliser', '25 188 t to 91 778 growers'),
             'Bono Cafetalero extension (PCM 031-2021)': ('Bono Cafetalero extension', 'fertiliser; state credit at 5 % and guarantees'),
             'IHCAFE renovation programme 2023–2027': ('IHCAFE renovation programme 2023–2027', 'target 7,0–7,5 M qq of production'),
             'Bono Cafetalero 2025': ('Bono Cafetalero 2025', '300 000 qq of fertiliser (read, El Heraldo 2026); L350 M not verified')}
    for f in FV.FINANCE:
        usd = f.get('usd_m') or ((f['lps_m'] / D.FX[f['year']]) if f.get('lps_m') and f.get('conv') else None)
        st = 'read' if f['status'] in ('USDA', 'DOC') else '⚠ extract'
        nm, terms = SHORT.get(f['name'], (f['name'], (f.get('terms') or f.get('who') or '')))
        rows.append([str(f['year']), nm, fr(usd, 0) if usd else '–', fr(f['lps_m'], 0) if f.get('lps_m') else '–', terms, [(st, dict(color=GREEN if st == 'read' else RED, b=True))]])
    rows.append(['2021', 'Debt of growers to banks, cooperatives and IHCAFE', fr(FV.DEBT['lps_m'] / D.FX[2021], 0), fr(FV.DEBT['lps_m'], 0), 'stock of debt, June 2021', [('⚠ extract', dict(color=RED, b=True))]])
    yy = p.table(0.45, 1.2, [0.55, 4.6, 0.7, 0.75, 5.0, 0.85], 0.36, rows, sz=7.8)
    cr = D.CREDIT
    c26 = D.CREDIT_2026
    p.text(0.45, yy + 0.1, 12.45, 0.8, ['Pattern: money arrives after the damage (2002 price crisis, 2013 rust, 2018 low prices, 2020–21 Covid and hurricanes, 2025 Bono) and mostly as fertiliser or refinancing; '
                                        'in 2013 only L335 M of L1 715 M offered was taken. Bank credit to all agriculture (BCH; coffee not separated): new loans L%s M in 2018, L%s M in 2020 (−8 %%), L%s M in 2025 (+12 %%); '
                                        'Jan–Jul 2026 L%s M, +%s %% on Jan–Jul 2025.' % (sp(cr[1]['new']), sp(cr[3]['new']), sp(cr[8]['new']), sp(c26['new']), fr(100 * (c26['new'] / c26['new_jul25'] - 1), 0))],
           sz=8.3, fill='F2F5F8')
    p.source('USDA FAS Coffee Annual Honduras 2011–2021; El Heraldo 7 Apr 2014 and 29 Aug 2018 (read); Decreto 93-2018; La Tribuna 25 Jun 2021 (debt, search summary); BCH loans by activity (xlsx, read). Lempiras converted at the BCH yearly mean rate.', y=6.95)
    return p


def slide_fx():
    p = Page()
    p.title('The lempira: 18,9 per dollar until 2011, 26,6 in 2026; small next to the coffee price swings')
    ys = YRS[1:]
    gbars(p, 0.45, 1.3, 12.45, 4.6, [lab(t)[:2] and str(t) for t in ys],
          [dict(name='Lempiras per US$', values=[100 * (R[t]['fx'] / R[t - 1]['fx'] - 1) for t in ys], color=NAVY),
           dict(name='Arabica in US$', values=[100 * (R[t]['arabica'] / R[t - 1]['arabica'] - 1) for t in ys], color=PALE),
           dict(name='Arabica in lempiras', values=[100 * (R[t]['arabica'] * R[t]['fx'] / (R[t - 1]['arabica'] * R[t - 1]['fx']) - 1) for t in ys], color=ORANGE)],
          -40, 80, 20, lay=(0.05, 0.04, 0.94, 0.86), suffix=' %')
    p.text(0.45, 1.05, 12.45, 0.26, [('Change on the year before, % (calendar years; 2026 = Jan–Aug for coffee, 1 Jan–25 Sep for the lempira)', dict(color=GREY))], sz=8.8)
    p.legend(0.9, 6.0, [(NAVY, 'lempiras per US$ (+ = lempira weaker)', 'box'), (PALE, 'arabica in US$', 'box'), (ORANGE, 'arabica in lempiras', 'box')], sz=8.5)
    fx = D.FX
    p.text(0.45, 6.3, 12.45, 0.6, ['Lempiras per US$: %s (2005) → %s (2011) → %s (2019) → %s (2024) → %s (2025, +4,7 %%) → %s (2026 to 25 Sep, +2,6 %%; %s on 25 Sep). '
                                   'A weaker lempira adds 2–5 %% a year to the price growers get, and to the cost of imported urea (+36 %% in lempiras in 2026).' % (
                                       fr(fx[2005], 2), fr(fx[2011], 2), fr(fx[2019], 2), fr(fx[2024], 2), fr(fx[2025], 2), fr(fx[2026], 2), fr(D.FX_DAILY[D.FX_LAST], 2))], sz=8.5, fill='F2F5F8')
    p.source('Banco Central de Honduras, Precio Promedio del Dólar, serie diaria 2000–2026 (reference rate, buying; file saved in raw/ihcafe_docs2/023); World Bank Pink Sheet arabica (other milds). FAOSTAT rates agree to 0,01.', y=6.95)
    return p


def slide_table():
    p = Page()
    p.title('Everything year on year, crop years 2015/16 – 2026/27')
    cols = ['Crop year', 'Area', 'Trees', 'Output', 'Bags/ha', 'kg/tree', 'N use', 'Urea L/t', 'Arabica $', 'Arabica L', 'L per $', 'Rust (national, %)']
    rust = {2017: '3 (Lempira plants)', 2020: '15–25 (5 depts)', 2022: '5,4 (Apr); 20 % of crop', 2023: '5,8 (May)', 2024: '7,4 (Mar) ⚠', 2025: '5,7 (Q1)', 2026: '8,4 (Jan)'}
    rows = [cols]
    for t in range(2015, 2027):
        q = t - 1

        def c(a, b):
            if not a or not b:
                return '–'
            v = a / b - 1
            return [('0 %' if abs(v) < 0.005 else pct(100 * v, 0), dict(color=GREEN if v >= 0.005 else (RED if v <= -0.005 else INK)))]
        r, s = R[t], R[q]
        rows.append([lab(t), c(r['bear_kha'], s['bear_kha']), c(r['trees_m'], s['trees_m']), c(r['prod_kbags'], s['prod_kbags']), c(yld(t), yld(q)), c(kgt(t), kgt(q)),
                     c(r['n_t'], s['n_t']), c(ureaL(t), ureaL(q)), c(r['arabica'], s['arabica']), c(r['arabica'] * r['fx'], s['arabica'] * s['fx']), c(r['fx'], s['fx']),
                     rust.get(t, '–')])
    yy = p.table(0.45, 1.2, [1.0, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 1.05, 1.05, 1.05, 0.95, 1.65], 0.37, rows, sz=8.3)
    p.text(0.45, yy + 0.1, 12.45, 0.9, ['Green = up, red = down, on the year before. Area, trees, output: USDA (2026/27 = forecast). N use: FAOSTAT all crops (2022 imputed, none yet for 2025–26). Prices: calendar year of the crop\'s fertiliser and fruit fill. '
                                        'Rust: the national figure of that year when one exists (different months and measures; see the Disease sheet).'], sz=8.3)
    p.source('Workbook Honduras_YoY_productivity_inputs_finance_fx.xlsx, sheet YoY (formulas). Sources on each sheet.', y=6.95)
    return p


SLIDES = [('productivity', slide_productivity), ('fert', slide_fert), ('rust', slide_rust), ('finance', slide_finance), ('fx', slide_fx), ('table', slide_table)]

if __name__ == '__main__':
    only = sys.argv[1:]
    pages = []
    for name, fn in SLIDES:
        pg = fn()
        pages.append(pg.s)
        if not only or name in only:
            pg.render(HERE + 'preview_yoy_%s.png' % name)
            print('preview', name)
    out = HERE + 'Honduras_YoY_productivity_inputs_finance_fx.pptx'
    save(pages, out, 'Honduras coffee year by year')
    print('saved', out)
