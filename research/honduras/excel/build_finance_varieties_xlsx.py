"""Honduras coffee: price 2005-2026, farm-gate price, cost of production, rust-resistant varieties, rust surveys,
financing programmes and yields. Every row has its source and a status (read in the document, or web-search extract
not verified). Inputs in blue, formulas in black (cached values written). Standard library only."""
import json, os, sys, csv
HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
sys.path.insert(0, HERE + '../../indonesia/excel')
sys.path.insert(0, HERE + '../data')
from xlsxw import Workbook, Style
import finance_varieties as FV

OUT = HERE + 'Honduras_price_cost_finance_varieties.xlsx'
D = json.load(open(HERE + '../data/worldbank_prices.json'))
MON = D['monthly']
AREA = json.load(open(HERE + '../data/area_trees_attache.json'))
FX, FG = FV.fx(), FV.farmgate()
YEARS = list(range(2005, 2027))

H = Style(bold=True, color='FFFFFF', fill='1F3864', halign='center', wrap=True)
TITLE = Style(bold=True, size=14, color='1F3864')
SUB = Style(italic=True, color='595959')
B = Style(bold=True)
WRAP = Style(wrap=True)
IN0, IN1, IN2, IN3 = (Style(color='0000FF', fmt=f) for f in ('#,##0', '#,##0.0', '0.00', '0.000'))
F0, F1, F2, F3 = (Style(fmt=f) for f in ('#,##0', '#,##0.0', '0.00', '0.000'))
PCT = Style(fmt='0.0%')
OK = Style(color='2E7D32', bold=True)
WARN = Style(color='C00000', bold=True)
TAG = {'USDA': ('✔ USDA report (read)', OK), 'FAO': ('✔ FAOSTAT (read)', OK), 'PRESS': ('⚠ web extract, NOT verified', WARN)}

wb = Workbook('Arial')

# ------------------------------------------------------------------ README
rd = wb.add('README')
lines = [('Honduras coffee: price, farm-gate, cost, varieties, rust, financing, yield (2005 → 2026)', TITLE),
         ('Built 25 Sep 2026 by research/honduras/excel/build_finance_varieties_xlsx.py from files saved in research/honduras/.', SUB),
         ('', None),
         ('Status column', B),
         ('✔ USDA report (read) = quoted from a USDA FAS Coffee Annual Honduras report saved in research/honduras/raw/usda_gain/ (2011-2018, 2020-2026; the 2019 report was not found).', None),
         ('✔ FAOSTAT (read) = FAOSTAT bulk file saved in research/honduras/raw/faostat/ (official "A" values only; exchange rates flag X = IMF).', None),
         ('⚠ web extract, NOT verified = seen only in a web-search summary. The page itself (IHCAFE, World Coffee Research, PROMECAFE, ICO, BCH, Honduran press) '
          'could not be opened: the network policy of this environment blocks those hosts. Check these before quoting them.', WARN),
         ('', None),
         ('Units', B),
         ('qq = quintal oro = 46 kg = 100 lb of green coffee.  Bag = 60 kg.  1 manzana = 0.7 ha.  L = lempira.  Lempira amounts are converted with the FAOSTAT annual average rate of the same year.', None),
         ('World price = World Bank Pink Sheet "Coffee, Arabica" (ICO other milds, ex-dock), annual mean of monthly prices; 2026 = Jan-Aug.', None),
         ('', None),
         ('Sheets', B),
         ('Price_annual: world price, YoY, farm-gate price (FAOSTAT), share of the world price, exchange rate.', None),
         ('Price_vs_cost: every cost figure found, against the world price and the Honduran export price of the same year.', None),
         ('Varieties, Adoption: rust-resistant varieties released by IHCAFE, resistance status, share planted.', None),
         ('Rust: IHCAFE / early-warning survey results as printed by USDA.', None),
         ('Finance: programmes, amounts (US$ million), beneficiaries, terms.', None),
         ('Yield: USDA production / bearing area, and the IHCAFE registry by farm size.', None),
         ('Web_extracts: every unverified extract collected, with the URL to check.', None),
         ('', None),
         ('Not found anywhere we could reach: yield by variety, a yearly series of bank credit to coffee (BCH), a yearly farm-gate series 2009-2021, '
          'official IHCAFE cost-of-production studies.', B)]
for i, (t, s) in enumerate(lines, 1):
    rd.set(i, 1, t, s)
rd.widths = {1: 160}

# ------------------------------------------------------------------ Price_annual
pa = wb.add('Price_annual')
pa.set(1, 1, 'World arabica price and Honduran farm-gate price, annual', TITLE)
pa.set(2, 1, 'Blue = input. Farm-gate: FAOSTAT "Coffee, green" producer price, official values only (2009-2021 and 2025 not published). '
             '2024: the FAOSTAT USD cell repeats 2023, so US$/t = lempiras / rate.', SUB)
hdr = ['Year', 'World price $/kg', 'YoY', 'World price $/qq', 'Farm-gate L/t (FAOSTAT)', 'L per US$ (FAOSTAT)', 'Farm-gate $/t', 'Farm-gate $/qq',
       'Farm-gate / world price', 'Note']
pa.row(4, 1, hdr, H)
ROW = {}
for k, y in enumerate(YEARS):
    r = 5 + k
    ROW[y] = r
    v = [MON['%dM%02d' % (y, m)]['arabica'] for m in range(1, 13) if '%dM%02d' % (y, m) in MON]
    a = sum(v) / len(v)
    pa.set(r, 1, y, B)
    pa.set(r, 2, a, IN3)
    if k:
        prev = sum(MON['%dM%02d' % (y - 1, m)]['arabica'] for m in range(1, 13)) / 12
        pa.set(r, 3, a / prev - 1, PCT, 'B%d/B%d-1' % (r, r - 1))
    pa.set(r, 4, a * 46, F1, 'B%d*46' % r)
    if y in FX:
        pa.set(r, 6, FX[y], IN2)
    if y in FG:
        pa.set(r, 5, FG[y]['LCU'], IN0)
        usd_t = FG[y]['LCU'] / FX[y] if y == 2024 else FG[y]['USD']
        if y == 2024:
            pa.set(r, 7, usd_t, F1, 'E%d/F%d' % (r, r))
        else:
            pa.set(r, 7, usd_t, IN1)
        pa.set(r, 8, usd_t * 0.046, F1, 'G%d*0.046' % r)
        pa.set(r, 9, usd_t * 0.046 / (a * 46), PCT, 'H%d/D%d' % (r, r))
    note = {2014: 'mean 4.425 $/kg (Brazil drought)', 2012: 'rust epidemic', 2013: 'rust epidemic', 2025: 'record year',
            2026: 'Jan-%s only' % ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][len(v) - 1],
            2024: 'FAOSTAT 2024 row inconsistent (USD = 2023 value): farm-gate from lempiras'}.get(y, '')
    pa.set(r, 10, note)
pa.widths = {1: 7, 2: 11, 3: 8, 4: 11, 5: 13, 6: 11, 7: 11, 8: 11, 9: 12, 10: 60}
pa.freeze = (5, 2)

# ------------------------------------------------------------------ Price_vs_cost
pc = wb.add('Price_vs_cost')
pc.set(1, 1, 'Cost of production against the price, US$ per quintal oro (46 kg)', TITLE)
pc.set(2, 1, 'World price looked up in Price_annual. Export price = Honduran average export price printed by USDA for the crop year ending that year.', SUB)
pc.row(4, 1, ['Year', 'What the figure is', 'Cost or threshold $/qq', 'Same in $/kg', 'World price $/qq', 'Honduran export price $/qq',
              'Export price − cost', 'Status', 'Source', 'Quote / extract'], H)
exq = {int(e['crop'][-2:]) + 2000: e['usd_qq'] for e in FV.EXPORT_PRICE}
r = 5
for c in FV.COSTS:
    pc.set(r, 1, c['year'] if c['year'] else 'n.d.', B)
    pc.set(r, 2, c['kind'], WRAP)
    pc.set(r, 3, c['usd_qq'], IN1)
    if c.get('lo'):
        pc.set(r, 2, c['kind'] + ' (range %d-%d; upper bound used)' % (c['lo'], c['usd_qq']), WRAP)
    pc.set(r, 4, c['usd_qq'] / 46, F2, 'C%d/46' % r)
    if c['year']:
        wr = ROW[c['year']]
        wv = sum(MON['%dM%02d' % (c['year'], m)]['arabica'] for m in range(1, 13)) / 12 * 46
        pc.set(r, 5, wv, F1, "INDEX(Price_annual!D5:D26,MATCH(A%d,Price_annual!A5:A26,0))" % r)
        if c['year'] in exq:
            pc.set(r, 6, exq[c['year']], IN2)
            pc.set(r, 7, exq[c['year']] - c['usd_qq'], F1, 'F%d-C%d' % (r, r))
    t, s = TAG[c['status']]
    pc.set(r, 8, t, s)
    pc.set(r, 9, c['src'], WRAP)
    pc.set(r, 10, c['quote'], WRAP)
    r += 1
r += 1
pc.set(r, 1, 'Honduran average export price (USDA)', B)
r += 1
pc.row(r, 1, ['Crop year', 'US$ per 46-kg bag', '$/kg', 'Source', 'Quote', 'Note'], H)
for e in FV.EXPORT_PRICE:
    r += 1
    pc.set(r, 1, e['crop'], B)
    pc.set(r, 2, e['usd_qq'], IN2)
    pc.set(r, 3, e['usd_qq'] / 46, F2, 'B%d/46' % r)
    pc.set(r, 4, e['src'] + ' (' + FV.GAIN[e['src']] + ')', WRAP)
    pc.set(r, 5, e['quote'], WRAP)
    pc.set(r, 6, e.get('note', ''), WRAP)
pc.widths = {1: 9, 2: 42, 3: 12, 4: 10, 5: 12, 6: 13, 7: 12, 8: 24, 9: 40, 10: 70}

# ------------------------------------------------------------------ Varieties / Adoption
va = wb.add('Varieties')
va.set(1, 1, 'Rust-resistant varieties released by IHCAFE', TITLE)
va.set(2, 1, 'Resistance status is read in USDA reports; release years are web extracts (the IHCAFE and World Coffee Research pages could not be opened).', SUB)
va.row(4, 1, ['Variety', 'Family', 'Released', 'Release year status', 'Resistance status', 'Year resistance lost', 'Source', 'Note'], H)
for i, v in enumerate(FV.VARIETIES, 5):
    va.row(i, 1, [v['name'], v['family'], v['released'], TAG[v['year_status']][0], v['resistance'], v['broke'] or '', v['src'], v['note']], WRAP)
    va.set(i, 1, v['name'], B)
va.set(11, 1, 'Count', B)
va.set(12, 1, '1990-2004: 3 varieties bred by IHCAFE (IHCAFE 90, Lempira, Parainema). 2005-2023: none found. 2024: 3 bred abroad and released by IHCAFE (Ihcatú 75, Anacafé 14 SHN, Obatá SHN, ⚠). 2026: 2 more in release process (⚠).')
va.set(13, 1, 'Yield by variety: no official figure found. Web extract: Obatá about 20 % more productive than Caturra (⚠). PAPP target 5 → 45 qq per manzana (USDA 2017).')
va.widths = {1: 30, 2: 30, 3: 11, 4: 24, 5: 55, 6: 10, 7: 55, 8: 55}

ad = wb.add('Adoption')
ad.set(1, 1, 'Share planted with rust-resistant varieties', TITLE)
ad.row(3, 1, ['When', 'Scope', 'Resistant share %', 'Lempira share %', 'Status', 'Source', 'Quote / extract'], H)
for i, a in enumerate(FV.ADOPTION, 4):
    ad.set(i, 1, a['when'], B)
    ad.set(i, 2, a['scope'], WRAP)
    if a.get('resistant') is not None:
        ad.set(i, 3, a['resistant'], IN0)
    if a.get('lempira'):
        ad.set(i, 4, a['lempira'], IN2)
    t, s = TAG[a['status']]
    ad.set(i, 5, t, s)
    ad.set(i, 6, a['src'], WRAP)
    ad.set(i, 7, a['quote'], WRAP)
ad.widths = {1: 10, 2: 40, 3: 12, 4: 12, 5: 24, 6: 36, 7: 90}

# ------------------------------------------------------------------ Rust
ru = wb.add('Rust')
ru.set(1, 1, 'Coffee leaf rust in Honduras: surveys and events (IHCAFE, as printed by USDA)', TITLE)
ru.set(2, 1, FV.RUST_RULE, SUB)
ru.row(4, 1, ['When', 'Value', 'Unit / what', 'Status', 'Source', 'Quote'], H)
for i, x in enumerate(FV.RUST, 5):
    ru.set(i, 1, x['when'], B)
    val = x.get('n') or x.get('value')
    if val is not None:
        ru.set(i, 2, val, IN2)
    ru.set(i, 3, x['unit'] + (' (range %d-%d %%)' % (x['lo'], x['hi']) if x.get('lo') else ''), WRAP)
    t, s = TAG[x['status']]
    ru.set(i, 4, t, s)
    ru.set(i, 5, x['src'] + ' (' + FV.GAIN[x['src']] + ')', WRAP)
    ru.set(i, 6, x['quote'], WRAP)
ru.widths = {1: 10, 2: 8, 3: 45, 4: 22, 5: 45, 6: 90}

# ------------------------------------------------------------------ Finance
fi = wb.add('Finance')
fi.set(1, 1, 'Financing programmes for Honduran coffee growers', TITLE)
fi.set(2, 1, 'US$ used = amount stated in US$, otherwise lempiras / FAOSTAT rate of that year (looked up in Price_annual).', SUB)
fi.row(4, 1, ['Year', 'Programme', 'US$ M stated', 'Lempiras M', 'L per US$', 'US$ M used', 'Who', 'Terms', 'Status', 'Source', 'Quote / extract'], H)
r = 5
for f in FV.FINANCE:
    fi.set(r, 1, f['year'], B)
    fi.set(r, 2, f['name'], WRAP)
    if f.get('usd_m'):
        fi.set(r, 3, f['usd_m'], IN1)
    if f.get('lps_m'):
        fi.set(r, 4, f['lps_m'], IN0)
    if f['year'] in FX and f['year'] >= 2005:
        fi.set(r, 5, FX[f['year']], F2, 'INDEX(Price_annual!F5:F26,MATCH(A%d,Price_annual!A5:A26,0))' % r)
    if f.get('usd_m'):
        fi.set(r, 6, f['usd_m'], F1, 'C%d' % r)
    elif f.get('lps_m'):
        fi.set(r, 6, f['lps_m'] / FX[f['year']], F1, 'D%d/E%d' % (r, r))
    fi.set(r, 7, f['who'], WRAP)
    fi.set(r, 8, f['terms'], WRAP)
    t, s = TAG[f['status']]
    fi.set(r, 9, t, s)
    fi.set(r, 10, f['src'], WRAP)
    fi.set(r, 11, f['quote'], WRAP)
    r += 1
r += 1
fi.set(r, 1, 'Debt', B)
fi.set(r + 1, 1, FV.DEBT['when'])
fi.set(r + 1, 2, 'Growers owed banks, co-ops and IHCAFE', WRAP)
fi.set(r + 1, 4, FV.DEBT['lps_m'], IN0)
fi.set(r + 1, 5, FX[2021], F2, 'INDEX(Price_annual!F5:F26,MATCH(2021,Price_annual!A5:A26,0))')
fi.set(r + 1, 6, FV.DEBT['lps_m'] / FX[2021], F1, 'D%d/E%d' % (r + 1, r + 1))
fi.set(r + 1, 9, TAG['PRESS'][0], WARN)
fi.set(r + 1, 10, FV.DEBT['src'], WRAP)
fi.set(r + 3, 1, 'Ratios', B)
fi.set(r + 4, 2, 'Bono 2020: US$ per producer')
fi.set(r + 4, 6, 12e6 / 91778, F0, '12000000/91778')
fi.set(r + 5, 2, 'Decree 93-2018: L200 per qq in US$ (2018 rate)')
fi.set(r + 5, 6, 200 / FX[2018], F2, '200/INDEX(Price_annual!F5:F26,MATCH(2018,Price_annual!A5:A26,0))')
fi.set(r + 6, 2, '… as a share of the 2018/19 export price (106.89 $/qq)')
fi.set(r + 6, 6, 200 / FX[2018] / 106.89, PCT, 'F%d/106.89' % (r + 5))
fi.widths = {1: 8, 2: 40, 3: 10, 4: 11, 5: 9, 6: 10, 7: 34, 8: 45, 9: 24, 10: 40, 11: 70}

# ------------------------------------------------------------------ Yield
yi = wb.add('Yield')
yi.set(1, 1, 'Yield: USDA production per bearing hectare, and the IHCAFE registry by farm size', TITLE)
yi.set(2, 1, 'Marketing year Oct-Sep (e.g. 2012 = 2012/13). Production: USDA PSD, 1 000 60-kg bags. Bearing area: USDA attaché tables, 1 000 ha. Last year = USDA forecast.', SUB)
yi.row(4, 1, ['Marketing year', 'Production (1 000 bags)', 'Bearing area (1 000 ha)', 'Bags per bearing ha', 'qq oro per manzana'], H)
for k, y in enumerate(AREA['years']):
    r = 5 + k
    p_ = AREA['psd_full']['Arabica Production'][str(y)]
    b_ = AREA['bearing_kha'][k]
    yi.set(r, 1, '%d/%02d' % (y, (y + 1) % 100), B)
    yi.set(r, 2, p_, IN0)
    yi.set(r, 3, b_, IN0)
    yi.set(r, 4, p_ / b_, F1, 'B%d/C%d' % (r, r))
    yi.set(r, 5, p_ / b_ * 60 * 0.7 / 46, F1, 'D%d*60*0.7/46' % r)
r = 5 + len(AREA['years']) + 1
yi.set(r, 1, 'IHCAFE registry (Coffee Statistics Reports, table 1 of USDA reports 2024-2026)', B)
r += 1
yi.row(r, 1, ['Crop year / size', 'Farmers', 'Hectares harvested', '60-kg bags', 'Bags per ha', 'Source'], H)
for cy, d in FV.REGISTRY.items():
    for sz in ('small', 'medium', 'large'):
        r += 1
        f_, h_, b_ = d[sz]
        yi.set(r, 1, '%s %s' % (cy, sz), B)
        yi.set(r, 2, f_, IN0)
        yi.set(r, 3, h_, IN0)
        yi.set(r, 4, b_, IN0)
        yi.set(r, 5, b_ / h_, F1, 'D%d/C%d' % (r, r))
        yi.set(r, 6, d['src'])
yi.widths = {1: 18, 2: 14, 3: 14, 4: 14, 5: 12, 6: 30}

# ------------------------------------------------------------------ Web extracts
we = wb.add('Web_extracts')
we.set(1, 1, 'Web-search extracts collected on 25 Sep 2026: NOT verified (pages blocked by the network policy)', TITLE)
src = HERE + '../raw/varieties_finance/snippets_unverified.csv'
rows = list(csv.reader(open(src, encoding='utf-8')))
we.row(3, 1, rows[0], H)
for i, rw in enumerate(rows[1:], 4):
    we.row(i, 1, rw, WRAP)
we.widths = {1: 7, 2: 22, 3: 70, 4: 16, 5: 16, 6: 9, 7: 22, 8: 30, 9: 60}

wb.save(OUT)
print('saved', OUT)
