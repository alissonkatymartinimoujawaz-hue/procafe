"""Honduras coffee, year by year 2005-2026 with year-on-year changes: area, trees, production, yield per hectare and per tree,
fertiliser, rust, varieties, financing, exchange rate. Data from research/honduras/yoy/data_yoy.py. Inputs blue, formulas black
(cached values written, checked by research/indonesia/excel/verify_xlsx.py). Standard library only."""
import json, os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
sys.path.insert(0, HERE + '../../indonesia/excel')
sys.path.insert(0, HERE + '../yoy')
from xlsxw import Workbook, Style, col_letter
import data_yoy as D
FV = D.FV

OUT = HERE + 'Honduras_YoY_productivity_inputs_finance_fx.xlsx'
H = Style(bold=True, color='FFFFFF', fill='1F3864', halign='center', wrap=True)
H2 = Style(bold=True, color='FFFFFF', fill='2E75B6', halign='center', wrap=True)
TITLE = Style(bold=True, size=14, color='1F3864')
SUB = Style(italic=True, color='595959')
B = Style(bold=True)
WRAP = Style(wrap=True)
IN0, IN1, IN2, IN3 = (Style(color='0000FF', fmt=f) for f in ('#,##0', '#,##0.0', '0.00', '0.000'))
F0, F1, F2, F3 = (Style(fmt=f) for f in ('#,##0', '#,##0.0', '0.00', '0.000'))
PCT = Style(fmt='+0.0%;-0.0%;0.0%')
PCTB = Style(fmt='+0.0%;-0.0%;0.0%', bold=True)
OK = Style(color='2E7D32', bold=True)
WARN = Style(color='C00000', bold=True)
TAG = {'USDA': ('✔ USDA report (read)', OK), 'FAO': ('✔ FAOSTAT', OK), 'BCH': ('✔ BCH file', OK), 'WB': ('✔ World Bank', OK),
       'DOC': ('✔ document read', OK), 'PRESS': ('⚠ web extract, not read', WARN)}
lab = lambda t: '%d/%02d' % (t, (t + 1) % 100)
ROWS = D.build()
R0 = 6
rowof = lambda t: R0 + t - D.YEARS[0]

wb = Workbook('Arial')

# ------------------------------------------------------------------ README
rd = wb.add('README')
lines = [
    ('Honduras coffee, year by year 2005 - 2026, with the change on the year before', TITLE),
    ('Built 25 Sep 2026 by research/honduras/excel/build_yoy_xlsx.py (data: research/honduras/yoy/data_yoy.py).', SUB),
    ('', None),
    ('Question: area and trees go up - so is productivity really falling? Did growers use less fertiliser? How much disease? Which varieties? Which financing? What did the lempira do?', B),
    ('', None),
    ('Sheets', B),
    ('YoY: every yearly series side by side, each followed by its change on the year before (formulas).', None),
    ('Productivity: output per bearing hectare and per bearing tree, trees per hectare, the IHCAFE registry, and the 2016-18 vs 2022-24 comparison.', None),
    ('Fertiliser: FAOSTAT nitrogen / phosphate / potash use, urea imports, urea price in US$ and in lempiras, kg of urea bought by 1 kg of coffee, Bono Cafetalero.', None),
    ('Disease: every rust (roya) figure found, by year, and the USDA remarks on rust, berry borer, drought and fertiliser.', None),
    ('Varieties: resistant varieties released, and every figure on the share planted.', None),
    ('Finance: state and bank programmes by year, debt, Bono Cafetalero, BCH bank credit to agriculture 2017-2026.', None),
    ('FX: lempiras per US$ (BCH daily reference rate, annual mean), coffee and urea prices in lempiras.', None),
    ('', None),
    ('Crop year t = October t to September t+1 (label t/t+1). Calendar-year series (FAOSTAT, World Bank, BCH) are put on the crop year that starts in that year.', None),
    ('Colours: blue = input with its source; black = formula. Status: ✔ read in the source file; ⚠ web-search extract, page not read.', None),
    ('Units: bag = 60 kg of green coffee; quintal (qq) = 46 kg; lempira = L; kha = thousand hectares.', None),
]
for i, (t, s) in enumerate(lines, 1):
    rd.set(i, 1, t, s)
rd.widths = {1: 180}

# ------------------------------------------------------------------ YoY master table
yo = wb.add('YoY')
yo.set(1, 1, 'Year by year and change on the year before', TITLE)
yo.set(2, 1, 'Each series is followed by its change on the year before (black formula). Blank = no data. 2026/27: USDA forecast (area, trees, production); prices = Jan-Aug 2026; lempira = Jan - 25 Sep 2026.', SUB)
SER = [  # key, header, style, source
    ('bear_kha', 'Bearing area (kha)', IN0, 'USDA attache'),
    ('trees_m', 'Bearing trees (million)', IN0, 'USDA attache'),
    ('nonbear_kha', 'Non-bearing area (kha)', IN0, 'USDA attache'),
    ('prod_kbags', 'Production (1 000 bags)', IN0, 'USDA PSD'),
    ('yield', 'Yield (bags / bearing ha)', F1, 'formula'),
    ('kg_tree', 'Green coffee per bearing tree (kg)', F3, 'formula'),
    ('density', 'Bearing trees per ha', F0, 'formula'),
    ('exports_q', 'IHCAFE exports (1 000 qq of 46 kg)', IN0, 'IHCAFE'),
    ('n_t', 'Nitrogen use, all crops (t N)', IN0, 'FAOSTAT'),
    ('urea_imp_t', 'Urea imports (t)', IN0, 'FAOSTAT'),
    ('urea_wb', 'Urea world price (US$/t)', IN1, 'World Bank'),
    ('urea_hnl', 'Urea price (L per t)', F0, 'formula'),
    ('arabica', 'Arabica world price (US$/kg)', IN2, 'World Bank'),
    ('arabica_hnl_qq', 'Arabica in lempiras (L per qq)', F0, 'formula'),
    ('ratio', 'kg urea bought by 1 kg coffee', F1, 'formula'),
    ('fx', 'Lempiras per US$ (BCH)', IN3, 'BCH'),
]
yo.set(4, 1, 'Crop year', H)
col = 2
COL = {}
for key, hd, sty, src in SER:
    yo.set(4, col, hd + ' [' + src + ']', H)
    yo.set(4, col + 1, 'change', H2)
    COL[key] = col
    col += 2
yo.set(5, 1, '')
C = lambda k: col_letter(COL[k])
for r_ in ROWS:
    t = r_['year']
    r = rowof(t)
    yo.set(r, 1, lab(t))
    val = {}
    for key, hd, sty, src in SER:
        c = COL[key]
        v = None
        if key == 'yield' and r_['prod_kbags'] and r_['bear_kha']:
            v = r_['prod_kbags'] / r_['bear_kha']
            yo.set(r, c, v, sty, '%s%d/%s%d' % (C('prod_kbags'), r, C('bear_kha'), r))
        elif key == 'kg_tree' and r_['prod_kbags'] and r_['trees_m']:
            v = r_['prod_kbags'] * 60 / r_['trees_m'] / 1000
            yo.set(r, c, v, sty, '%s%d*60/%s%d/1000' % (C('prod_kbags'), r, C('trees_m'), r))
        elif key == 'density' and r_['trees_m'] and r_['bear_kha']:
            v = r_['trees_m'] * 1000 / r_['bear_kha']
            yo.set(r, c, v, sty, '%s%d*1000/%s%d' % (C('trees_m'), r, C('bear_kha'), r))
        elif key == 'urea_hnl' and r_['urea_wb'] and r_['fx']:
            v = r_['urea_wb'] * r_['fx']
            yo.set(r, c, v, sty, '%s%d*%s%d' % (C('urea_wb'), r, C('fx'), r))
        elif key == 'arabica_hnl_qq' and r_['arabica'] and r_['fx']:
            v = r_['arabica'] * 46 * r_['fx']
            yo.set(r, c, v, sty, '%s%d*46*%s%d' % (C('arabica'), r, C('fx'), r))
        elif key == 'ratio' and r_['arabica'] and r_['urea_wb']:
            v = r_['arabica'] * 1000 / r_['urea_wb']
            yo.set(r, c, v, sty, '%s%d*1000/%s%d' % (C('arabica'), r, C('urea_wb'), r))
        elif key == 'exports_q' and r_['exports_q']:
            v = r_['exports_q'] / 1000
            yo.set(r, c, v, sty)
        elif key in r_ and r_[key] is not None:
            v = r_[key]
            yo.set(r, c, v, sty)
        val[key] = v
        prev = PREV.get(key) if t > D.YEARS[0] else None
        if v is not None and prev is not None:
            yo.set(r, c + 1, v / prev - 1, PCT, '%s%d/%s%d-1' % (C(key), r, C(key), r - 1))
    PREV = val
    if t == D.YEARS[0]:
        PREV = val
r = rowof(2026) + 2
for t in ['Notes: bearing trees and area are the USDA attache estimates (IHCAFE data); the tree count jumps from 1 375 M (2021) to 2 100 M (2026) while the bearing area rises 20 %: check before quoting per-tree numbers.',
          'IHCAFE exports: 2005/06 - 2020/21 IHCAFE report 2020-2021; 2021/22 bulletin 07-02-2023; 2024/25 La Prensa 15 Jul 2026. 2025/26 estimate: 7 244 000 qq (Exports_nowcast of the forecast workbook) - not in this column.',
          'FAOSTAT nitrogen = imports - exports of nitrogen in all fertilisers (all crops, coffee not separated); 2022 is imputed by FAO (flag I).',
          'Lempira column: BCH daily reference rate (buying), mean of the days of the year; 2026 = 1 Jan - 25 Sep.']:
    yo.set(r, 1, t, WRAP)
    r += 1
yo.widths = {1: 10, **{c: 11 for c in range(2, col)}}
yo.freeze = (5, 2)

# ------------------------------------------------------------------ Productivity
pr = wb.add('Productivity')
pr.set(1, 1, 'Is productivity really falling while area and trees go up?', TITLE)
pr.set(2, 1, 'Averages of 2016/17-2018/19 (peak) against 2022/23-2024/25 (last three crops with an outcome). Formulas on the YoY sheet.', SUB)
pr.row(4, 1, ['Series', '2016/17-2018/19', '2022/23-2024/25', 'Change'], H)
comp = [('Bearing area (kha)', 'bear_kha', F0), ('Bearing trees (million)', 'trees_m', F0), ('Production (1 000 bags)', 'prod_kbags', F0),
        ('Yield (bags / bearing ha)', 'yield', F1), ('Green coffee per bearing tree (kg)', 'kg_tree', F3), ('Bearing trees per ha', 'density', F0),
        ('Nitrogen use, all crops (t N)', 'n_t', F0), ('Urea imports (t)', 'urea_imp_t', F0), ('Urea price (L per t)', 'urea_hnl', F0),
        ('kg urea bought by 1 kg coffee', 'ratio', F1), ('Lempiras per US$', 'fx', F2)]


def avg_val(key, ys):
    vs = []
    for t in ys:
        rr = next(x for x in ROWS if x['year'] == t)
        if key == 'yield':
            vs.append(rr['prod_kbags'] / rr['bear_kha'])
        elif key == 'kg_tree':
            vs.append(rr['prod_kbags'] * 60 / rr['trees_m'] / 1000)
        elif key == 'density':
            vs.append(rr['trees_m'] * 1000 / rr['bear_kha'])
        elif key == 'urea_hnl':
            vs.append(rr['urea_wb'] * rr['fx'])
        elif key == 'ratio':
            vs.append(rr['arabica'] * 1000 / rr['urea_wb'])
        elif rr.get(key) is not None:
            vs.append(rr[key])
    return sum(vs) / len(vs)


for i, (nm, key, sty) in enumerate(comp):
    r = 5 + i
    pr.set(r, 1, nm)
    a_, b_ = avg_val(key, (2016, 2017, 2018)), avg_val(key, (2022, 2023, 2024))
    cc = C(key)
    pr.set(r, 2, a_, sty, 'AVERAGE(YoY!%s%d:%s%d)' % (cc, rowof(2016), cc, rowof(2018)))
    pr.set(r, 3, b_, sty, 'AVERAGE(YoY!%s%d:%s%d)' % (cc, rowof(2022), cc, rowof(2024)))
    pr.set(r, 4, b_ / a_ - 1, PCTB, 'C%d/B%d-1' % (r, r))
r = 5 + len(comp) + 1
pr.row(r, 1, ['IHCAFE registry (farms registered with IHCAFE)', 'Harvested ha', '60-kg bags', 'Bags per ha', 'Producers', 'Source'], H)
for k, t in enumerate((2022, 2023, 2024)):
    rr = r + 1 + k
    g = D.REG[t]
    pr.set(rr, 1, lab(t))
    pr.set(rr, 2, g['ha'], IN0)
    pr.set(rr, 3, g['bags'], IN0)
    pr.set(rr, 4, g['bags'] / g['ha'], F1, 'C%d/B%d' % (rr, rr))
    pr.set(rr, 5, g['producers'], IN0)
    pr.set(rr, 6, g['src'] + ' (IHCAFE Coffee Statistics Report)', OK)
r += 4
for k, g in enumerate(D.PRODUCERS):
    pr.set(r + k, 1, 'Coffee producers %d: about %s%s (%s)' % (g['year'], format(g['value'], ','), ', %s registered with IHCAFE' % format(g['registered'], ',') if g['registered'] else '', g['src']))
r += len(D.PRODUCERS) + 1
pr.set(r, 1, '2025/26: production implied by IHCAFE exports %s thousand bags on %s kha = %s bags per ha (USDA estimate: %s).' % (
    format(round(D.PROD_EXPORT_IMPLIED[2025]), ','), D.BEAR[2025], round(D.PROD_EXPORT_IMPLIED[2025] / D.BEAR[2025], 1), round(D.PSD[2025] / D.BEAR[2025], 1)), WRAP)
r += 2
for t in ['Reading: yes, output per hectare fell by about 30 % from the 2016-18 peak (25.7 to 18.2 bags per ha), and the IHCAFE registry (16.6-17.7 bags per ha in 2022-24) says the same as USDA. '
          'Output per tree fell by about half (0.35 to 0.18 kg) because USDA counts about 40 % more trees on about the same area (6 000 instead of 4 400 trees per ha: denser, younger plantings).',
          'Fertiliser does not explain it on its own: national nitrogen use in 2022-24 was only 4 % below 2016-18 (5 % per bearing coffee hectare), small next to the 30 % fall in yield. What changed: the 2012-15 renewal wave aged ("cyclical decline in productivity after a widespread re-planting effort ten years ago", USDA 2022), '
          'rust came back (Lempira lost its resistance in 2016/17; 15-25 % incidence after Eta/Iota in 2020; 5-8 % since 2022), fertiliser became dearer in lempiras (2021-22), the 2019-20 price slump cut care, '
          'labour ran short (USDA 2024) and Sep-Oct heat was higher (see the forecast workbook).']:
    pr.set(r, 1, t, WRAP)
    r += 1
pr.widths = {1: 60, 2: 16, 3: 16, 4: 12, 5: 12, 6: 50}

# ------------------------------------------------------------------ Fertiliser
fe = wb.add('Fertiliser')
fe.set(1, 1, 'Fertiliser: how much, how dear, and the state gift (Bono Cafetalero)', TITLE)
fe.set(2, 1, 'FAOSTAT: agricultural use = imports - exports of the nutrient in all fertilisers (all crops). Flag I = imputed by FAO. Urea imports: FAOSTAT fertilisers by product.', SUB)
hd = ['Year', 'N (t)', 'change', 'P2O5 (t)', 'change', 'K2O (t)', 'change', 'FAO flag (N imports)', 'Urea imports (t)', 'change', 'Urea import unit value (US$/t)',
      'Urea world (US$/t)', 'change', 'Urea (L/t)', 'change', 'N per bearing coffee ha (kg, all-crop N)', 'Coffee bags per t of N']
fe.row(4, 1, hd, H)
for rr_ in ROWS:
    t = rr_['year']
    r = rowof(t) - 1
    fe.set(r, 1, t)
    prev = next((x for x in ROWS if x['year'] == t - 1), None)
    for c, key, sty in ((2, 'n_t', IN0), (4, 'p_t', IN0), (6, 'k_t', IN0), (9, 'urea_imp_t', IN0), (12, 'urea_wb', IN1)):
        if rr_.get(key) is not None:
            fe.set(r, c, rr_[key], sty)
            if prev and prev.get(key):
                fe.set(r, c + 1, rr_[key] / prev[key] - 1, PCT, '%s%d/%s%d-1' % (col_letter(c), r, col_letter(c), r - 1))
    if rr_.get('n_flag'):
        fe.set(r, 8, rr_['n_flag'])
    if rr_.get('urea_imp_usd_t'):
        fe.set(r, 11, rr_['urea_imp_usd_t'], IN0)
    if rr_.get('urea_wb') and rr_.get('fx'):
        fe.set(r, 14, rr_['urea_wb'] * rr_['fx'], F0, 'L%d*YoY!%s%d' % (r, C('fx'), rowof(t)))
        if prev and prev.get('urea_wb') and prev.get('fx'):
            fe.set(r, 15, rr_['urea_wb'] * rr_['fx'] / (prev['urea_wb'] * prev['fx']) - 1, PCT, 'N%d/N%d-1' % (r, r - 1))
    if rr_.get('n_t') and rr_.get('bear_kha'):
        fe.set(r, 16, rr_['n_t'] / rr_['bear_kha'], F0, 'B%d/YoY!%s%d' % (r, C('bear_kha'), rowof(t)))
    if rr_.get('n_t') and rr_.get('prod_kbags'):
        fe.set(r, 17, rr_['prod_kbags'] * 1000 / rr_['n_t'], F1, 'YoY!%s%d*1000/B%d' % (C('prod_kbags'), rowof(t), r))
r = rowof(2026) + 2
fe.row(r, 1, ['Bono Cafetalero (fertiliser given by the state)', 'Fertiliser (qq of 46 kg)', 'Fertiliser (t)', 'Producers', 'Lempiras (M)', 'US$ (M)', 'Status', 'Source'], H)
for k, b in enumerate(D.BONO):
    rr = r + 1 + k
    fe.set(rr, 1, b['year'])
    if b['fert_qq']:
        fe.set(rr, 2, b['fert_qq'], IN0 if b['status'] != 'USDA' else F0, None if b['status'] != 'USDA' else 'C%d*1000/46' % rr)
    if b['fert_t']:
        fe.set(rr, 3, b['fert_t'], IN0 if b['status'] == 'USDA' else F0, None if b['status'] == 'USDA' else 'B%d*46/1000' % rr)
    for c, key in ((4, 'producers'), (5, 'lps_m'), (6, 'usd_m')):
        if b[key]:
            fe.set(rr, c, b[key], IN0 if key != 'usd_m' else IN1)
    fe.set(rr, 7, *TAG[b['status']])
    fe.set(rr, 8, b['src'])
r += len(D.BONO) + 3
for t in ['Reading: national nitrogen use in 2021-24 (about 105 000 t) is below the 2018 and 2020 peaks (123 000 and 128 000 t) but above 2016 (96 000 t), the year before the record crop. '
          'Per bearing coffee hectare it is 5 % below 2016-18. The fall in yield since 2019 is therefore not a fall in national fertiliser use; the big one-year cuts (2019: -30 %) do line up with output.',
          'What did change is the price in lempiras: urea cost L 4 400/t in 2016 and L 17 100/t in 2022 (4 times more), L 8 400/t in 2024 and about L 14 900/t in Jan-Aug 2026. '
          'Coffee bought 18.6 kg of urea per kg in 2016, 8.0 in 2022, 13.2 in 2026.',
          'The Bono Cafetalero gives 2-5 qq per small or medium grower: 25 188 t in 2020, 216 223 qq in 2022, 300 000 qq in 2025, about 400 000 qq planned for 2026. '
          '300 000 qq = 13 800 t of product, about 8 % of national urea imports by weight (it is not all urea).']:
    fe.set(r, 1, t, WRAP)
    r += 1
fe.widths = {1: 8, **{c: 12 for c in range(2, 18)}}
fe.freeze = (5, 2)

# ------------------------------------------------------------------ Disease
di = wb.add('Disease')
di.set(1, 1, 'Rust (roya) and other problems, every figure found', TITLE)
di.set(2, 1, 'There is no published yearly series in the files we could reach: IHCAFE early-warning bulletins (monthly, about 1 200 farms) are behind the blocked ihcafe.hn host. Figures below are those printed by USDA or the press.', SUB)
di.row(4, 1, ['Year', 'When', 'Value (%)', 'What it measures', 'Status', 'Source'], H)
for k, d in enumerate(D.RUST):
    r = 5 + k
    di.set(r, 1, d['year'])
    di.set(r, 2, d['when'])
    if d['value'] is not None:
        di.set(r, 3, d['value'], IN2)
    di.set(r, 4, d['measure'])
    di.set(r, 5, *TAG[d['status']])
    di.set(r, 6, d['src'])
r = 5 + len(D.RUST) + 1
di.set(r, 1, 'IHCAFE rule of thumb', B)
di.set(r + 1, 1, D.RUST_RULE, WRAP)
di.set(r + 2, 1, 'IHCAFE thresholds: 0-5 % low, 5-20 % medium (USDA 2022-2025).', WRAP)
r += 4
di.row(r, 1, ['Crop year', 'What USDA wrote that year (drought, disease, fertiliser, labour)'], H)
for k, (t, txt) in enumerate(sorted(D.NOTES_USDA.items())):
    di.set(r + 1 + k, 1, lab(t))
    di.set(r + 1 + k, 2, txt)
di.widths = {1: 8, 2: 110, 3: 10, 4: 70, 5: 24, 6: 50}

# ------------------------------------------------------------------ Varieties
va = wb.add('Varieties')
va.set(1, 1, 'Rust-resistant varieties: releases and share planted', TITLE)
va.row(3, 1, ['Variety', 'Released', 'Type', 'Status now', 'Source'], H)
r = 4
for v in FV.VARIETIES:
    va.row(r, 1, [v.get('name'), str(v.get('year')), v.get('type', ''), v.get('now', v.get('resistance', '')), v.get('src', '')])
    r += 1
r += 1
va.row(r, 1, ['When', 'Scope', 'Resistant share (%)', 'Status', 'Source', 'Quote'], H)
for a in FV.ADOPTION:
    r += 1
    va.set(r, 1, a['when'])
    va.set(r, 2, a['scope'])
    va.set(r, 3, a['resistant'], IN1)
    va.set(r, 4, *TAG[a['status']])
    va.set(r, 5, a['src'])
    va.set(r, 6, a['quote'])
r += 2
for t in ['Reading: about half the area was resistant in 2013 and about 60-65 % from 2014-2017 on; no later national figure was found. Lempira, the main resistant variety, lost its resistance in 2016/17, '
          'so part of that 60 % became susceptible again. Parainema (2004) plantings are now being harvested (USDA 2025, 2026). Three more (Ihcatu 75, Anacafe 14, Obata) were released in 2024.',
          'Not found: yield by variety, and any share after 2020.']:
    va.set(r, 1, t, WRAP)
    r += 1
va.widths = {1: 16, 2: 36, 3: 14, 4: 24, 5: 44, 6: 110}

# ------------------------------------------------------------------ Finance
fi = wb.add('Finance')
fi.set(1, 1, 'Financing: state, IHCAFE and banks, by year', TITLE)
fi.set(2, 1, 'No yearly series of bank credit to coffee could be reached (BCH credit by activity is not in the files). The programmes and amounts below are those read in USDA reports, decrees and the press.', SUB)
fi.row(4, 1, ['Year', 'Programme', 'US$ M', 'Lempiras M', 'Who', 'Terms', 'Status', 'Source'], H)
r = 5
for f in FV.FINANCE:
    fi.set(r, 1, f['year'])
    fi.set(r, 2, f['name'])
    if f.get('usd_m'):
        fi.set(r, 3, f['usd_m'], IN1)
    elif f.get('lps_m') and f.get('conv') and D.FX.get(f['year']):
        fi.set(r, 3, f['lps_m'] / D.FX[f['year']], F1, 'D%d/YoY!%s%d' % (r, C('fx'), rowof(f['year'])))
    if f.get('lps_m'):
        fi.set(r, 4, f['lps_m'], IN0)
    fi.set(r, 5, f.get('who', ''))
    fi.set(r, 6, f.get('terms', ''))
    fi.set(r, 7, *TAG[f['status']])
    fi.set(r, 8, f.get('src', ''))
    r += 1
r += 1
fi.set(r, 1, 2021)
fi.set(r, 2, 'Debt of growers to banks, cooperatives and IHCAFE')
fi.set(r, 4, FV.DEBT['lps_m'], IN0)
fi.set(r, 3, FV.DEBT['lps_m'] / D.FX[2021], F1, 'D%d/YoY!%s%d' % (r, C('fx'), rowof(2021)))
fi.set(r, 7, *TAG[FV.DEBT['status']])
fi.set(r, 8, FV.DEBT['src'])
r += 3
fi.set(r, 1, 'Bank credit to agriculture (BCH, all farming: coffee is not separated), millions of lempiras', B)
fi.row(r + 1, 1, ['Year', 'Loans outstanding, December', 'change', 'New loans in the year', 'change', 'Share of all new loans', 'Loans outstanding in US$ M', 'Source'], H)
c0 = r + 2
for k, cr in enumerate(D.CREDIT):
    rr = c0 + k
    fi.set(rr, 1, cr['year'])
    fi.set(rr, 2, cr['stock'], IN0)
    fi.set(rr, 4, cr['new'], IN0)
    if k:
        fi.set(rr, 3, cr['stock'] / D.CREDIT[k - 1]['stock'] - 1, PCT, 'B%d/B%d-1' % (rr, rr - 1))
        fi.set(rr, 5, cr['new'] / D.CREDIT[k - 1]['new'] - 1, PCT, 'D%d/D%d-1' % (rr, rr - 1))
    fi.set(rr, 6, cr['new'] / cr['new_total'], Style(fmt='0.0%'))
    fi.set(rr, 7, cr['stock'] / D.FX[cr['year']], F0, 'B%d/YoY!%s%d' % (rr, C('fx'), rowof(cr['year'])))
    fi.set(rr, 8, 'BCH, Prestamos de las Otras Sociedades de Depositos por Actividad (xlsx read, raw/ihcafe_docs5)', OK)
rr = c0 + len(D.CREDIT)
c26 = D.CREDIT_2026
fi.set(rr, 1, '2026 Jan-Jul')
fi.set(rr, 2, c26['stock'], IN0)
fi.set(rr + 1, 1, '2025 Jan-Jul')
fi.set(rr + 1, 2, c26['stock_jul25'], IN0)
fi.set(rr, 3, c26['stock'] / c26['stock_jul25'] - 1, PCT, 'B%d/B%d-1' % (rr, rr + 1))
fi.set(rr, 4, c26['new'], IN0)
fi.set(rr + 1, 4, c26['new_jul25'], IN0)
fi.set(rr, 5, c26['new'] / c26['new_jul25'] - 1, PCT, 'D%d/D%d-1' % (rr, rr + 1))
fi.set(rr + 3, 1, 'Reading: credit to agriculture grew slower than total credit (its share of new loans fell from 6.1 % in 2018 to 3.4 % in 2024) and fell in 2020 (-8 %). '
                  'It picked up in 2024-2025 (+11 %, +12 % new loans) and jumped in 2026: new loans Jan-Jul +84 % on Jan-Jul 2025, with average lending rates down 3.8 points (BCH communique, June 2026). '
                  'Coffee is not separated in BCH data.', WRAP)
fi.widths = {1: 7, 2: 60, 3: 9, 4: 11, 5: 40, 6: 60, 7: 24, 8: 50}
FIN_LAST = r

# ------------------------------------------------------------------ FX
fx = wb.add('FX')
fx.set(1, 1, 'Lempira against the dollar, and what it did to coffee and urea prices in lempiras', TITLE)
fx.set(2, 1, 'BCH reference rate (buying), mean of the daily values; 2026 = 1 Jan - 25 Sep. Coffee = World Bank arabica (other milds, ex-dock) x 46 kg x rate: a world price in lempiras, not the farm-gate price.', SUB)
fx.row(4, 1, ['Year', 'L per US$', 'change', 'Arabica (US$/kg)', 'change', 'Arabica (L per qq)', 'change', 'Urea (US$/t)', 'Urea (L per t)', 'change',
              'FAOSTAT farm-gate (L per t, official only)', 'change'], H)
FG = FV.farmgate()
for rr_ in ROWS:
    t = rr_['year']
    r = rowof(t) - 1
    fx.set(r, 1, t)
    prev = next((x for x in ROWS if x['year'] == t - 1), None)
    fx.set(r, 2, rr_['fx'], F3, 'YoY!%s%d' % (C('fx'), rowof(t)))
    if prev:
        fx.set(r, 3, rr_['fx'] / prev['fx'] - 1, PCT, 'B%d/B%d-1' % (r, r - 1))
    fx.set(r, 4, rr_['arabica'], F2, 'YoY!%s%d' % (C('arabica'), rowof(t)))
    if prev:
        fx.set(r, 5, rr_['arabica'] / prev['arabica'] - 1, PCT, 'D%d/D%d-1' % (r, r - 1))
    fx.set(r, 6, rr_['arabica'] * 46 * rr_['fx'], F0, 'D%d*46*B%d' % (r, r))
    if prev:
        fx.set(r, 7, rr_['arabica'] * rr_['fx'] / (prev['arabica'] * prev['fx']) - 1, PCT, 'F%d/F%d-1' % (r, r - 1))
    fx.set(r, 8, rr_['urea_wb'], F1, 'YoY!%s%d' % (C('urea_wb'), rowof(t)))
    fx.set(r, 9, rr_['urea_wb'] * rr_['fx'], F0, 'H%d*B%d' % (r, r))
    if prev:
        fx.set(r, 10, rr_['urea_wb'] * rr_['fx'] / (prev['urea_wb'] * prev['fx']) - 1, PCT, 'I%d/I%d-1' % (r, r - 1))
    if FG.get(t, {}).get('LCU'):
        fx.set(r, 11, FG[t]['LCU'], IN0)
        if t - 1 >= D.YEARS[0] and FG.get(t - 1, {}).get('LCU'):
            fx.set(r, 12, FG[t]['LCU'] / FG[t - 1]['LCU'] - 1, PCT, 'K%d/K%d-1' % (r, r - 1))
r = rowof(2026) + 2
for t in ['Reading: the lempira lost value slowly: 18.9 per US$ in 2005-2011 (fixed band), then 2-5 % more lempiras per dollar each year to 24.5 in 2019, flat 2019-2024 (24.0-24.8), then +4.7 % in 2025 (25.95) and +2.6 % so far in 2026 (26.64; 26.89 on 25 Sep).',
          'For growers paid in lempiras the depreciation adds a few % a year to the dollar price; it is small next to the swings of the coffee price itself (-31 % in 2012, +81 % in 2024-25 in US$).',
          'The same depreciation makes imported urea dearer in lempiras: +33 % in US$ and +36 % in lempiras in 2026.']:
    fx.set(r, 1, t, WRAP)
    r += 1
fx.widths = {1: 8, **{c: 13 for c in range(2, 13)}}
fx.freeze = (5, 2)

wb.save(OUT)
print('saved', OUT)
