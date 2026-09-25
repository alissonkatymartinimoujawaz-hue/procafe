"""Honduras arabica: what moves bearing / non-bearing area and trees, with prices, fertiliser, costs, margin, land and labour.
One row per marketing year (Oct N - Sep N+1). Inputs in blue, formulas in black, cached values written so the file reads
without recalculation. Standard library only (xlsxw.py from research/indonesia/excel)."""
import json, os, sys, csv, statistics as st, datetime, collections
HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
sys.path.insert(0, HERE + '../../indonesia/excel')
from xlsxw import Workbook, Style, col_letter

DATA = HERE + '../data/'
OUT = HERE + 'Honduras_area_drivers.xlsx'
A = json.load(open(DATA + 'area_trees_attache.json'))
WB = json.load(open(DATA + 'worldbank_prices.json'))['annual']
FAO = {int(k): v for k, v in json.load(open(DATA + 'faostat_inputs_land_labour.json')).items()}
WX = json.load(open(DATA + 'rust_2012_weather.json')) if os.path.exists(DATA + 'rust_2012_weather.json') else None
Y = A['years']
PSD = {int(k): v for k, v in A['psd_production_kbags'].items()}
# IHCAFE registered farms (IHCAFE coffee statistics reports, as tabled in the USDA attaché reports)
IHC = {2022: dict(ha=209202 + 79764.38 + 26764.73, small=90522, bags=2907394 + 1820667 + 848578, src='USDA HO2024-0002, table 1 (IHCAFE 2022/23)'),
       2023: dict(ha=193092 + 62494 + 24511, small=87136, bags=2502386 + 1400613 + 747355, src='USDA HO2025-0002, table 1 (IHCAFE Coffee Statistics Report 2023/24)'),
       2024: dict(ha=179271 + 85040 + 21246, small=86895, bags=2627164 + 1661733 + 515533, src='USDA HO2026-0002, table 1 (IHCAFE Coffee Statistics Report 2024/25)')}
REGIME = {**{y: '1 · 2005–2009 flat prices' for y in range(2005, 2010)}, **{y: '2 · 2010–2012 price boom' for y in range(2010, 2013)},
          2013: '3 · 2013 rust + price crash', **{y: '4 · 2014–2017 renovation' for y in range(2014, 2018)},
          **{y: '5 · 2018–2019 price below cost' for y in (2018, 2019)}, **{y: '6 · 2020–2021 recovery' for y in (2020, 2021)},
          **{y: '7 · 2022–2026 high prices' for y in range(2022, 2027)}}

wb = Workbook('Arial')
H = Style(bold=True, color='FFFFFF', fill='1F3864', halign='center', wrap=True)
TITLE = Style(bold=True, size=14, color='1F3864')
SUB = Style(italic=True, color='595959')
B = Style(bold=True)
WRAP = Style(wrap=True)
IN0 = Style(color='0000FF', fmt='#,##0')
IN1 = Style(color='0000FF', fmt='#,##0.0')
IN2 = Style(color='0000FF', fmt='0.00')
F0 = Style(fmt='#,##0')
F1 = Style(fmt='#,##0.0')
F2 = Style(fmt='0.00')
FP = Style(fmt='+#,##0;-#,##0;0')
FPC = Style(fmt='+0.0%;-0.0%;0.0%')
C = Style(halign='center')
RED = Style(bold=True, color='C00000', wrap=True)

readme = wb.add('README')
an = wb.add('Annual')
rg = wb.add('Regimes')
mg = wb.add('Margin')
rw = wb.add('Rust_2012')
qt = wb.add('USDA_quotes')

# ---------------- Annual ----------------
cols = [('Year (MY start)', None), ('Marketing year', None), ('Bearing area (1000 ha)', 'bear'), ('Non-bearing area (1000 ha)', 'nonb'),
        ('Total planted area (1000 ha)', 'tot'), ('Total area, change (1000 ha)', 'dtot'), ('Bearing area, change (1000 ha)', 'dbear'),
        ('Non-bearing area, change (1000 ha)', 'dnonb'), ('Bearing trees (million)', 'btree'), ('Non-bearing trees (million)', 'ntree'),
        ('Trees per ha, bearing', 'dens_b'), ('Trees per ha, non-bearing', 'dens_n'), ('Production, USDA PSD (1000 bags 60 kg)', 'prod'),
        ('Yield (bags 60 kg per bearing ha)', 'yld'), ('Production, change %', 'dprod'), ('Arabica, World Bank "Other Milds" ($/kg, calendar year N)', 'ara'),
        ('Arabica ($/lb)', 'ara_lb'), ('Urea, World Bank ($/t)', 'urea'), ('DAP ($/t)', 'dap'), ('Potassium chloride ($/t)', 'kcl'),
        ('kg urea bought by 1 kg arabica', 'ratio'), ('Fertiliser use Honduras: N (t, FAO)', 'N'), ('P2O5 (t, FAO)', 'P'), ('K2O (t, FAO)', 'K'),
        ('N+P2O5+K2O (t)', 'NPK'), ('Urea import price Honduras ($/t, FAO trade)', 'urea_imp'), ('Forest land (1000 ha, FAO)', 'forest'),
        ('Permanent crops (1000 ha, FAO)', 'perm'), ('Pastures (1000 ha, FAO)', 'past'), ('Employment in agriculture (1000, ILO model via FAO)', 'emp'),
        ('IHCAFE registered harvested area (ha)', 'ihc_ha'), ('IHCAFE registered small producers', 'ihc_small'), ('Price regime', 'regime')]
CI = {k: i + 1 for i, (_, k) in enumerate(cols) if k}
an.row(1, 1, [c for c, _ in cols], H)
R0 = 2
V = {}
for i, y in enumerate(Y):
    r = R0 + i
    L = lambda k: col_letter(CI[k])
    an.set(r, 1, y, C)
    an.set(r, 2, '%d/%s' % (y, str(y + 1)[2:]), C)
    an.set(r, CI['bear'], A['bearing_kha'][i], IN0)
    an.set(r, CI['nonb'], A['nonbearing_kha'][i], IN0)
    tot = A['bearing_kha'][i] + A['nonbearing_kha'][i]
    an.set(r, CI['tot'], tot, F0, '%s%d+%s%d' % (L('bear'), r, L('nonb'), r))
    V[('tot', y)] = tot
    if i:
        for k, src in (('dtot', 'tot'), ('dbear', 'bear'), ('dnonb', 'nonb')):
            prev = {'tot': V[('tot', y - 1)], 'bear': A['bearing_kha'][i - 1], 'nonb': A['nonbearing_kha'][i - 1]}[src]
            cur = {'tot': tot, 'bear': A['bearing_kha'][i], 'nonb': A['nonbearing_kha'][i]}[src]
            an.set(r, CI[k], cur - prev, FP, '%s%d-%s%d' % (L(src), r, L(src), r - 1))
    an.set(r, CI['btree'], A['bearing_trees_m'][i], IN0)
    an.set(r, CI['ntree'], A['nonbearing_trees_m'][i], IN0)
    an.set(r, CI['dens_b'], A['bearing_trees_m'][i] / A['bearing_kha'][i] * 1000, F0, '%s%d/%s%d*1000' % (L('btree'), r, L('bear'), r))
    an.set(r, CI['dens_n'], A['nonbearing_trees_m'][i] / A['nonbearing_kha'][i] * 1000, F0, '%s%d/%s%d*1000' % (L('ntree'), r, L('nonb'), r))
    an.set(r, CI['prod'], PSD[y], IN0)
    an.set(r, CI['yld'], PSD[y] / A['bearing_kha'][i], F1, '%s%d/%s%d' % (L('prod'), r, L('bear'), r))
    if i:
        an.set(r, CI['dprod'], PSD[y] / PSD[y - 1] - 1, FPC, '%s%d/%s%d-1' % (L('prod'), r, L('prod'), r - 1))
    w = WB[str(y)]
    an.set(r, CI['ara'], w['arabica'], IN2)
    an.set(r, CI['ara_lb'], w['arabica'] / 2.20462, F2, '%s%d/2.20462' % (L('ara'), r))
    an.set(r, CI['urea'], w['urea'], IN0)
    an.set(r, CI['dap'], w['dap'], IN0)
    an.set(r, CI['kcl'], w['kcl'], IN0)
    an.set(r, CI['ratio'], w['arabica'] * 1000 / w['urea'], F1, '%s%d*1000/%s%d' % (L('ara'), r, L('urea'), r))
    f = FAO.get(y, {})
    for k, key in (('N', 'N'), ('P', 'P2O5'), ('K', 'K2O'), ('urea_imp', 'urea_imp_usd_t'), ('forest', 'forest_kha'), ('perm', 'perm_crops_kha'), ('past', 'pasture_kha'), ('emp', 'agri_employment_k')):
        if f.get(key) is not None:
            an.set(r, CI[k], f[key], IN0)
    if all(f.get(k) is not None for k in ('N', 'P2O5', 'K2O')):
        an.set(r, CI['NPK'], f['N'] + f['P2O5'] + f['K2O'], F0, '%s%d+%s%d+%s%d' % (L('N'), r, L('P'), r, L('K'), r))
    if y in IHC:
        an.set(r, CI['ihc_ha'], IHC[y]['ha'], IN0)
        an.set(r, CI['ihc_small'], IHC[y]['small'], IN0)
    an.set(r, CI['regime'], REGIME[y], C)
RL = R0 + len(Y) - 1
n = RL + 2
notes = ['Sources. Areas and trees: USDA attaché, Coffee Annual reports from Tegucigalpa (latest revision of each year; non-bearing area = area planted − area harvested). '
         'Production: USDA PSD online, Honduras arabica, marketing year Oct–Sep. Prices: World Bank Pink Sheet, update 2 Sep 2026 (2026 = Jan–Aug). '
         'Fertiliser use, urea import value ÷ quantity, land use, employment: FAOSTAT bulk files (Sep 2026). IHCAFE registry: tables reproduced in the USDA reports.',
         'Read with care: the USDA tree numbers are estimates (1,049 million every year 2006–2010; a fixed ~4,250 trees/ha until 2017, then ~6,400/ha). '
         'FAO flags Honduras coffee area as imputed after 2012 and producer prices as estimated, so neither is used here. FAO 2022 fertiliser use repeats 2021.',
         'Blue = input copied from the source; black = formula.']
for t in notes:
    an.set(n, 1, t, SUB)
    n += 1
an.widths = {1: 8, 2: 9, **{c: 12 for c in range(3, len(cols) + 1)}, CI['regime']: 26}
an.freeze = (2, 3)

# ---------------- Regimes ----------------
rg.set(1, 1, 'Area change by price regime (averages per year, from the Annual sheet)', TITLE)
rg.row(3, 1, ['Price regime', 'Years', 'Arabica ($/kg)', 'kg urea per kg arabica', 'Total area change (1000 ha/yr)', 'Bearing area change (1000 ha/yr)',
              'Non-bearing area change (1000 ha/yr)', 'Production change (%/yr)'], H)
regs = sorted(set(REGIME.values()))
rr = 4
for reg in regs:
    ys = [y for y in Y if REGIME[y] == reg]
    rng = lambda k: 'Annual!$%s$%d:$%s$%d' % (col_letter(CI[k]), R0, col_letter(CI[k]), RL)
    crit = 'Annual!$%s$%d:$%s$%d,$A%d' % (col_letter(CI['regime']), R0, col_letter(CI['regime']), RL, rr)
    rg.set(rr, 1, reg, B)
    rg.set(rr, 2, len(ys), C, 'COUNTIF(%s)' % crit)
    vals = {
        'ara': st.mean(WB[str(y)]['arabica'] for y in ys),
        'ratio': st.mean(WB[str(y)]['arabica'] * 1000 / WB[str(y)]['urea'] for y in ys),
        'dtot': st.mean(V[('tot', y)] - V[('tot', y - 1)] for y in ys if y > 2005) if any(y > 2005 for y in ys) else 0,
        'dbear': st.mean(A['bearing_kha'][Y.index(y)] - A['bearing_kha'][Y.index(y) - 1] for y in ys if y > 2005) if any(y > 2005 for y in ys) else 0,
        'dnonb': st.mean(A['nonbearing_kha'][Y.index(y)] - A['nonbearing_kha'][Y.index(y) - 1] for y in ys if y > 2005) if any(y > 2005 for y in ys) else 0,
        'dprod': st.mean(PSD[y] / PSD[y - 1] - 1 for y in ys if y > 2005) if any(y > 2005 for y in ys) else 0}
    for j, (k, fmt) in enumerate((('ara', F2), ('ratio', F1), ('dtot', FP), ('dbear', FP), ('dnonb', FP), ('dprod', FPC))):
        rg.set(rr, 3 + j, vals[k], fmt, 'AVERAGEIFS(%s,%s)' % (rng(k), crit))
    rr += 1
rg.set(rr + 1, 1, 'Averages skip 2005 for the changes (no 2004 row). The regimes are defined by the arabica price path and the 2012–2013 rust.', SUB)
rg.widths = {1: 32, 2: 7, 3: 12, 4: 12, 5: 14, 6: 14, 7: 14, 8: 12}

# ---------------- Margin ----------------
mg.set(1, 1, 'Indicative producer margin per quintal (100 lb = 45.36 kg) and per hectare', TITLE)
mg.set(2, 1, 'An estimate, not a measured margin: edit the blue cells. Farm-gate factor and costs come from the few dated figures below (IHCAFE, press).', SUB)
mg.set(4, 1, 'Farm-gate price ÷ international "Other Milds" price', B)
mg.set(4, 4, 0.78, Style(color='0000FF', fmt='0.00', fill='FFFF00'))
mg.set(4, 5, 'Calibration: 2021/22 IHCAFE producer average L4,584.61 = $187.85/qq vs World Bank 2022 $255/qq → 0.74; 2024 producers paid L5,270/qq ≈ $212/qq vs $255/qq → 0.83 (press, unverified).', WRAP)
mg.row(6, 1, ['Year', 'Arabica Other Milds ($/lb)', 'Farm-gate estimate ($/lb)', 'Cost of production ($/lb)', 'Cost basis', 'Margin ($ per quintal)',
              'Yield (quintals per bearing ha)', 'Margin ($ per bearing ha)', 'kg urea per kg arabica'], H)
BENCH = {2012: (1.50, 'IHCAFE: a price over $150/qq is favourable (USDA May 2012) — upper bound'),
         2019: (1.20, 'Press, Jul 2019: producers about $20 below a cost near $120/qq; exporters said the market needed ≥ $135 (unverified)'),
         2022: (1.30, 'Press on 2022–23: cost about $130/qq; fertiliser bags doubled to L1,200–1,500 (unverified)'),
         2023: (1.30, 'Same as 2022 (unverified)')}
def cost_for(y):
    ks = sorted(BENCH)
    if y in BENCH:
        return BENCH[y][0], 'benchmark'
    if y < ks[0]:
        return None, 'no cost data'
    if y > ks[-1]:
        return BENCH[ks[-1]][0], 'held at 2023 level (2026 picking wages +67%, urea +32%: cost understated)'
    lo = max(k for k in ks if k < y)
    hi = min(k for k in ks if k > y)
    return BENCH[lo][0] + (BENCH[hi][0] - BENCH[lo][0]) * (y - lo) / (hi - lo), 'interpolated %d–%d' % (lo, hi)
r = 7
for i, y in enumerate(Y):
    ara_lb = WB[str(y)]['arabica'] / 2.20462
    mg.set(r, 1, y, C)
    mg.set(r, 2, ara_lb, F2, 'Annual!%s%d' % (col_letter(CI['ara_lb']), R0 + i))
    mg.set(r, 3, ara_lb * 0.78, F2, 'B%d*$D$4' % r)
    cst, basis = cost_for(y)
    yq = PSD[y] / A['bearing_kha'][i] * 60 / 45.3592
    mg.set(r, 7, yq, F1, 'Annual!%s%d*60/45.3592' % (col_letter(CI['yld']), R0 + i))
    mg.set(r, 9, WB[str(y)]['arabica'] * 1000 / WB[str(y)]['urea'], F1, 'Annual!%s%d' % (col_letter(CI['ratio']), R0 + i))
    if cst is not None:
        mg.set(r, 4, cst, Style(color='0000FF', fmt='0.00', bold=y in BENCH))
        mg.set(r, 5, basis if y not in BENCH else 'benchmark', Style(color='404040'))
        m = (ara_lb * 0.78 - cst) * 100
        mg.set(r, 6, m, FP, '(C%d-D%d)*100' % (r, r))
        mg.set(r, 8, m * yq, FP, 'F%d*G%d' % (r, r))
    else:
        mg.set(r, 5, 'no cost data', Style(color='808080'))
    r += 1
r += 1
mg.set(r, 1, 'Cost benchmarks and sources', B)
r += 1
for y, (v, s) in sorted(BENCH.items()):
    mg.set(r, 1, y, C)
    mg.set(r, 2, v, IN2)
    mg.set(r, 3, s, WRAP)
    r += 1
for t in ['Other dated figures (press, unverified): picking paid L60 per lata in 2025, L100 in Feb 2026; pickers earn L200–400 a day; exporters pay producers L5,270/qq (2024).',
          'Yield in quintals uses USDA production ÷ USDA bearing area (60-kg bags converted to 100-lb quintals).']:
    mg.set(r, 1, t, SUB)
    r += 1
mg.widths = {1: 8, 2: 13, 3: 13, 4: 13, 5: 40, 6: 13, 7: 13, 8: 14, 9: 12}

# ---------------- Rust_2012 ----------------
rw.set(1, 1, 'Weather before and during the 2012–2013 rust epidemic: mean of Comayagua, Ocotepeque and Copán', TITLE)
if WX:
    rw.set(2, 1, WX['note'], SUB)
    rw.row(4, 1, WX['header'], H)
    for k, row in enumerate(WX['rows']):
        for j, v in enumerate(row):
            rw.set(5 + k, 1 + j, v, C if j == 0 else (Style(fmt='0') if isinstance(v, (int, float)) and 'rain' in WX['header'][j].lower() else F2))
    rw.widths = {1: 10, **{c: 14 for c in range(2, len(WX['header']) + 1)}}
else:
    rw.set(2, 1, 'Station data not yet added.', SUB)

# ---------------- Production since 1960 ----------------
pl = wb.add('Production_1960_2026')
PF = {int(k): v for k, v in A['psd_full']['Arabica Production'].items()}
EX = {int(k): v for k, v in A['psd_full']['Bean Exports'].items()}
pl.row(1, 1, ['Marketing year (Oct N – Sep N+1)', 'Year N', 'Production (1000 bags 60 kg)', 'Change on the year before', 'Bean exports (1000 bags)'], H)
for k, y in enumerate(sorted(PF)):
    r = 2 + k
    pl.set(r, 1, '%d/%s' % (y, str(y + 1)[2:]), C)
    pl.set(r, 2, y, C)
    pl.set(r, 3, PF[y], IN0)
    if k:
        pl.set(r, 4, PF[y] / PF[y - 1] - 1 if PF[y - 1] else None, FPC, 'IF(C%d=0,"",C%d/C%d-1)' % (r - 1, r, r - 1))
    pl.set(r, 5, EX.get(y), IN0)
pl.set(2 + len(PF) + 1, 1, A['psd_note'] + '. 2025/26 and 2026/27 are USDA estimates and forecasts.', SUB)
pl.widths = {1: 16, 2: 8, 3: 16, 4: 14, 5: 14}
pl.freeze = (2, 1)

# ---------------- USDA quotes ----------------
QUOTES = [
    ('May 2011', 'Land', 'Higher prices are motivating landholders with other crops or in other professions to convert larger portions of their lands to coffee growing.', 'Coffee Annual 4-18-2011'),
    ('May 2012', 'Inputs', 'Producers used more inputs such as fertilizer, new seeds, the improvement of planting density, and soil conservation techniques to increase yields.', 'Coffee Annual 5-9-2012'),
    ('May 2012', 'Cost', 'IHCAFE estimates that even though coffee prices are going down, there is still an incentive to the producer since a price over US$150 per quintal is favorable.', 'Coffee Annual 5-9-2012'),
    ('Jun 2013', 'Rust', 'On January 24, 2013, Honduras became the fourth Central American country to declare a state of emergency due to coffee rust. 25 percent (~71,000 ha) affected: more than 14,000 ha completely devastated, ~57,000 ha heavily affected.', 'Coffee Annual 6-20-2013'),
    ('Jun 2013', 'Rust', 'About 50 percent of the total area of coffee production is still planted with rust-susceptible varieties. The decrease is attributed to coffee leaf rust and low coffee prices.', 'Coffee Annual 6-20-2013'),
    ('Jun 2013', 'Area', 'Areas planted and harvested in 2013/14 and 2012/13 will remain below 2011/12 due to the rust and the renovation and rehabilitation of plantations; bearing trees have decreased.', 'Coffee Annual 6-20-2013'),
    ('May 2014', 'Renovation', 'The renovation and re-planting of new trees started five years ago and continues to rehabilitate the farms damaged by the rust. April 2014 national survey: rust incidence 12 percent; 62 percent of farms with resistant varieties.', 'Coffee Annual HO1402 5-30-2014'),
    ('Apr 2015', 'Rust', 'About 22,000 hectares (10,000 families) had a total loss of their farms; 58,000 ha (20,000 families) saw production fall by 50 percent. Restoration depended on the producer\'s access to credit.', 'Coffee Annual 4-20-2015'),
    ('Apr 2016', 'Renovation', 'New planted area with bean-bearing trees will be harvested for the first time since the rust; PAPP funds small producers to replant one manzana (0.71 ha), about 23,000 producers, interest-free.', 'Coffee Annual 4-26-2016'),
    ('May 2017', 'Genetics', 'In April 2017 IHCAFE confirmed the loss of resistance of the Lempira variety to coffee leaf rust.', 'Coffee Annual 5-24-2017'),
    ('May 2018', 'Cost', 'Producers face increased production costs to prevent rust and a decline in international coffee prices; many still repay the 2012 rust loans, due by 2019.', 'Coffee Annual 5-22-2018'),
    ('May 2020', 'Fertiliser', 'Coffee Bonus: the government distributes about $12 million of fertilizer (25,000+ t) to 91,462 small and medium producers (84–87 percent of production).', 'Coffee Annual 05-15-2020'),
    ('May 2022', 'Yield', 'Expected cyclical decline in productivity after a widespread re-planting effort ten years ago; Russia supplies ~20 percent of world ammonium, raising fertilizer prices.', 'Coffee Annual HO2022-0005'),
    ('May 2023', 'Area', 'Production rise causes: positive biennial harvest, improved plant nutrition, better farm practices, increase in new coffee areas, new coffee plants entering production.', 'Coffee Annual HO2023-0003'),
    ('Apr 2024', 'Labour', 'The decrease in production is attributed to high incidence of coffee rust and an ongoing labor shortage; a program addresses migration with workforce professionalization, new pay schemes and semi-mechanized harvest.', 'Coffee Annual HO2024-0002'),
    ('May 2025', 'Genetics', 'Area growth in MY 2025/26 is driven by the introduction of the Parainema variety (rust-resistant); production rises on less rust, improved labor availability and an 81 percent price rise.', 'Coffee Annual HO2025-0002'),
    ('Apr 2026', 'Area', 'IHCAFE: growth driven by improved plant nutrition, favorable biennial cycles, expansion of productive area, enhanced pruning and crop management, and maturation of newly established plantations. IHCAFE helps growers meet the EU Deforestation Regulation.', 'Coffee Annual HO2026-0002'),
]
qt.row(1, 1, ['Report date', 'Topic', 'What the USDA attaché report says (close to the original English)', 'Report'], H)
for k, q in enumerate(QUOTES):
    qt.row(2 + k, 1, list(q), WRAP)
qt.widths = {1: 10, 2: 11, 3: 110, 4: 28}

# ---------------- README ----------------
lines = [
    ('Honduras arabica : ce qui fait bouger la surface et les arbres (2005–2026)', TITLE),
    ('Une ligne par campagne (octobre N – septembre N+1). Chiffres en bleu = copiés des sources ; en noir = formules. Les feuilles se recalculent dans Excel.', SUB),
    ('', None),
    ('Annual : surfaces en production / pas encore en production, total, variations, arbres, densité, production, rendement, prix de l\'arabica et des engrais, usage d\'engrais au Honduras, forêts, cultures permanentes, pâturages, emploi agricole, registre IHCAFE.', WRAP),
    ('Regimes : variation moyenne de la surface par phase de prix (boom 2010–2012, rouille 2013, rénovation 2014–2017, crise 2018–2019, prix hauts 2022–2026).', WRAP),
    ('Margin : marge indicative par quintal et par hectare. C\'est une estimation : le coût vient de quelques chiffres datés (IHCAFE, presse, non vérifiés). Modifie les cellules bleues.', WRAP),
    ('Rust_2012 : la météo de 2011–2013 dans les 3 zones (pluie des pluviomètres GPCC, températures des stations), pour voir ce qui a favorisé la rouille.', WRAP),
    ('USDA_quotes : ce que disent les rapports de l\'attaché USDA, année par année (rouille, rénovation, terres, main-d\'œuvre, variétés, engrais).', WRAP),
    ('Production_1960_2026 : la production USDA du Honduras depuis 1960/61, avec la variation d\'une année sur l\'autre.', WRAP),
    ('', None),
    ('À SAVOIR AVANT D\'INTERPRÉTER', B),
    ('Les nombres d\'arbres de l\'USDA sont des estimations : 1 049 millions chaque année de 2006 à 2010, puis une densité fixe d\'environ 4 250 arbres/ha jusqu\'en 2017, et 6 400/ha depuis 2023. Depuis 2020, les deux tiers de la hausse des arbres viennent de cette densité, pas de nouvelles surfaces.', RED),
    ('La FAO marque la surface de café du Honduras comme imputée depuis 2013 et le prix producteur comme estimé : non utilisés.', WRAP),
    ('Le registre de l\'IHCAFE (surface récoltée des fermes inscrites) baisse de 315 700 ha (2022/23) à 280 100 (2023/24) puis 285 600 ha (2024/25), alors que l\'USDA l\'augmente : la hausse récente de la surface est incertaine.', WRAP),
]
for i, (t, s) in enumerate(lines, 1):
    readme.set(i, 1, t, s)
readme.widths = {1: 150}

wb.save(OUT)
print('saved', OUT)
