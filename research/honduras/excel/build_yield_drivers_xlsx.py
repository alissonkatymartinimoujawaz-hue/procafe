"""Honduras coffee: what drives production and yield, and how to forecast 2026/27.
Data and test results from research/honduras/yield_drivers/ (analysis.py, robustness.py). Inputs in blue, formulas in black
(cached values written, checked by research/indonesia/excel/verify_xlsx.py). Standard library only."""
import json, os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
sys.path.insert(0, HERE + '../../indonesia/excel')
sys.path.insert(0, HERE + '../yield_drivers')
from xlsxw import Workbook, Style, ref, col_letter
import analysis as AN
import nowcast as NC

R = json.load(open(HERE + '../yield_drivers/results.json'))
J = json.load(open(HERE + '../yield_drivers/robustness.json'))
OUT = HERE + 'Honduras_yield_drivers_forecast.xlsx'

H = Style(bold=True, color='FFFFFF', fill='1F3864', halign='center', wrap=True)
TITLE = Style(bold=True, size=14, color='1F3864')
SUB = Style(italic=True, color='595959')
B = Style(bold=True)
WRAP = Style(wrap=True)
IN0, IN1, IN2, IN3 = (Style(color='0000FF', fmt=f) for f in ('#,##0', '#,##0.0', '0.00', '0.000'))
F0, F1, F2, F3 = (Style(fmt=f) for f in ('#,##0', '#,##0.0', '0.00', '0.000'))
PY2, PY3 = (Style(color='7030A0', fmt=f) for f in ('0.00', '0.000'))          # computed in Python (permutation tests, regressions)
PCT, PCTB = Style(fmt='0.0%'), Style(fmt='0.0%', bold=True)
INPCT = Style(color='0000FF', fmt='0.0%')
PYPCT = Style(color='7030A0', fmt='0.0%')
OK = Style(color='2E7D32', bold=True)
WARN = Style(color='C00000', bold=True)
AMB = Style(color='C55A11', bold=True)

wb = Workbook('Arial')
Y0, Y1 = 1970, 2026
ROW0 = 6                                   # first data row in Data and Changes (year 1970)
rowof = lambda t: ROW0 + t - Y0


def lab(t):
    return '%d/%02d' % (t, (t + 1) % 100)


# ------------------------------------------------------------------ README
rd = wb.add('README')
lines = [
    ('Honduras coffee: what drives production and yield, and how to forecast 2026/27', TITLE),
    ('Built 25 Sep 2026 by research/honduras/excel/build_yield_drivers_xlsx.py. Tests run in research/honduras/yield_drivers/analysis.py and robustness.py (Python, standard library).', SUB),
    ('', None),
    ('Answer in one line', B),
    ('Year-to-year output moves with one-off shocks that do not repeat (not an on/off biennial cycle), with fertiliser use (the tightest link: r = +0.75), with heat in Sep-Oct just before the harvest '
     '(r = -0.45, exploratory) and with three documented crises (rust 2012/13, price slump 2019/20, rust after hurricanes Eta/Iota 2021/22). ENSO and seasonal rain show no reliable national effect. '
     'Some USDA "yield" jumps are bearing-area revisions.', WRAP),
    ('2026/27: IHCAFE exports put 2025/26 near 6.0 M bags (USDA 5.53). From there, mean reversion and the record September heat point to about 5.5 M bags (range 4.9-6.1) for 2026/27, below USDA 6.03. '
     'Without the heat term: about 6.0 M.', WRAP),
    ('', None),
    ('Colours', B),
    ('Blue = input read from a file (source given on the sheet). Black = Excel formula. Purple = computed in Python (permutation p-values, regressions, simulated bands): not an Excel formula, re-run the scripts to reproduce.', None),
    ('', None),
    ('Crop year', B),
    ('Crop year t = October t to September t+1 (label t/t+1). Harvest Nov t - Mar t+1; flowering Feb - Apr t; fertiliser and fruit fill May - Oct t. '
     'World prices, urea and FAO nitrogen use are calendar-year t values, the year the crop t is fertilised and filled.', WRAP),
    ('', None),
    ('Sheets', B),
    ('Data: every series by crop year 1970/71 - 2026/27.  Changes: year-on-year log changes (formulas).  Tests: one driver at a time, Pearson r (Excel CORREL check), permutation p, Holm-corrected p.', None),
    ('Biennial: is there an on/off cycle?  Yield_split: yield change = production change - area change.  Fertiliser: nitrogen use vs output and what moves nitrogen.', None),
    ('Weather: El Nino / La Nina years, driest seasons, coffee-zone temperature (ERA5-Land).  Backtest: forecast errors 2000/01 - 2025/26 of simple methods and of the USDA May forecast.', None),
    ('Exports_nowcast: IHCAFE monthly export profile, what the 2025/26 exports imply for the 2025/26 crop.  Forecast_2026_27: scorecard and range.', None),
    ('', None),
    ('Sources', B),
    ('IHCAFE Resumen Informe 2020-2021 (exports 1970/71-2020/21, 46-kg bags, export unit price) - raw/ihcafe_docs2/040. IHCAFE Boletin Estadistico de Comercializacion 30-08-2022 and 07-02-2023 (monthly exports) - raw/ihcafe_docs2/051, 052.', WRAP),
    ('USDA PSD online (production, 1 000 60-kg bags, download July 2026) and USDA FAS Coffee Annual Honduras 2011-2026 (bearing area; May forecasts) - data/area_trees_attache.json, raw/usda_gain/.', WRAP),
    ('World Bank Pink Sheet monthly (arabica = ICO other milds, urea) - research/indonesia/raw/worldbank_cmo_monthly.xlsx. FAOSTAT nitrogen use (t N, all crops) - data/faostat_inputs_land_labour.json.', WRAP),
    ('GPCC monthly rain at Santa Rosa de Copan, Nueva Ocotepeque, Comayagua (Full V2022 to 2019, Monitoring, First Guess 2026) - raw/rain_check/. NOAA CPC ONI. ERA5-Land (Open-Meteo archive) at 13 coffee points - raw/coffee_zones/.', WRAP),
    ('Press figures for 2025/26 exports and 2026/27 outlooks: see Exports_nowcast and Forecast_2026_27, with status per line.', WRAP),
]
for i, (t, s) in enumerate(lines, 1):
    rd.set(i, 1, t, s)
rd.widths = {1: 190}

# ------------------------------------------------------------------ Data
da = wb.add('Data')
da.set(1, 1, 'Data by crop year (t = October t to September t+1)', TITLE)
da.set(2, 1, 'Blue = input, black = formula. Rain = total of the window / 1991-2020 normal of the same months (1.00 = normal). ONI = NOAA Oceanic Nino Index of the 3-month season.', SUB)
hd = ['Crop year', 't', 'IHCAFE exports (46-kg bags)', 'IHCAFE export price (US$ / 46 kg)', 'USDA production (1 000 60-kg bags)', 'USDA bearing area (kha)',
      'Yield (60-kg bags / bearing ha)', 'Arabica, calendar t (US$/kg)', 'Urea, calendar t (US$/t)', 'kg urea bought by 1 kg coffee', 'FAO nitrogen use, calendar t (t N)',
      'Rain Dec(t-1)-Mar t / normal (GPCC)', 'Rain Apr-May t / normal', 'Rain Jun-Oct t / normal', 'ONI DJF t', 'ONI JJA t', 'ONI OND t',
      'Coffee-zone max. temperature Sep-Oct, deg C vs 1991-2020 (ERA5-Land)']
for j, h in enumerate(hd, 1):
    da.set(ROW0 - 1, j, h, H)
HEATS = J['coffee_zone_tmax']['sep_oct']
for t in range(Y0, Y1 + 1):
    r = rowof(t)
    da.set(r, 1, lab(t))
    da.set(r, 2, t)
    if t in AN.EXP:
        da.set(r, 3, AN.EXP[t], IN0)
        da.set(r, 4, AN.EXPPRICE[t], IN2)
    if t in AN.PSD:
        da.set(r, 5, AN.PSD[t], IN0)
    if t in AN.BEAR:
        da.set(r, 6, AN.BEAR[t], IN0)
        da.set(r, 7, AN.PSD[t] / AN.BEAR[t], F1, 'E%d/F%d' % (r, r))
    if AN.ARA.get(t):
        da.set(r, 8, AN.ARA[t], IN3)
    if AN.UREA.get(t):
        da.set(r, 9, AN.UREA[t], IN1)
        da.set(r, 10, AN.ARA[t] * 1000 / AN.UREA[t], F1, 'H%d*1000/I%d' % (r, r))
    if AN.NUSE.get(t):
        da.set(r, 11, AN.NUSE[t], IN0)
    for c, W in ((12, AN.W_DRY), (13, AN.W_FLOWER), (14, AN.W_WET)):
        v = AN.rain_window(t, W)
        if v is not None:
            da.set(r, c, math.exp(v), IN2)
    for c, m in ((15, 1), (16, 7), (17, 11)):
        if (t, m) in AN.ONI:
            da.set(r, c, AN.ONI[(t, m)], IN2)
    if str(t) in HEATS:
        da.set(r, 18, HEATS[str(t)], IN2)
da.set(rowof(Y1) + 2, 1, 'Notes', B)
notes = ['2026/27: USDA production and area are the USDA forecast (May 2026); arabica, urea = Jan-Aug 2026 mean; rain Jun-Oct 2026 not complete (see Weather).',
         'IHCAFE exports stop at 2020/21 in the IHCAFE report read; 2021/22 = 6 131 226 bags of 46 kg (bulletin 07-02-2023, not used in the tests).',
         'FAO nitrogen use is for all crops (coffee is not separated); it runs to 2024 and the 2022 value is imputed by FAO (flag I).']
for i, n in enumerate(notes):
    da.set(rowof(Y1) + 3 + i, 1, n)
da.widths = {1: 10, 2: 6, **{c: 14 for c in range(3, 19)}}
da.freeze = (ROW0, 3)

# ------------------------------------------------------------------ Changes
ch = wb.add('Changes')
ch.set(1, 1, 'Year-on-year changes (natural log: 0.10 = about +10 %)', TITLE)
ch.set(2, 1, 'All black cells are formulas on the Data sheet. "Last year" columns = the same column one row up (the biennial / mean-reversion test).', SUB)
CH = ['Crop year', 't', 'Exports', 'USDA production', 'Yield', 'Bearing area', 'Arabica price', 'Coffee/urea ratio', 'Nitrogen use',
      'Rain Dec-Mar (log of ratio)', 'Rain Apr-May', 'Rain Jun-Oct', 'ONI DJF', 'ONI JJA', 'Last year: production change', 'Last year: exports change',
      'Coffee-zone max. temperature Sep-Oct (deg C vs normal)']
for j, h in enumerate(CH, 1):
    ch.set(ROW0 - 1, j, h, H)
CV = {}                                   # cached values for CORREL checks: (col, t) -> value


def put(sh, r, c, v, f, st=F3):
    sh.set(r, c, v, st, f)
    CV[(c, r)] = v


for t in range(Y0, Y1 + 1):
    r = rowof(t)
    ch.set(r, 1, lab(t))
    ch.set(r, 2, t)
    if t - 1 < Y0:
        continue
    for c, dc, S in ((3, 'C', AN.EXP), (4, 'E', AN.PSD), (6, 'F', AN.BEAR), (9, 'K', AN.NUSE)):
        if S.get(t) and S.get(t - 1):
            put(ch, r, c, math.log(S[t] / S[t - 1]), 'LN(Data!%s%d/Data!%s%d)' % (dc, r, dc, r - 1))
    if t in AN.YLD and t - 1 in AN.YLD:
        put(ch, r, 5, math.log(AN.YLD[t] / AN.YLD[t - 1]), 'LN(Data!G%d/Data!G%d)' % (r, r - 1))
    put(ch, r, 7, math.log(AN.ARA[t] / AN.ARA[t - 1]), 'LN(Data!H%d/Data!H%d)' % (r, r - 1))
    put(ch, r, 8, math.log(AN.ARA[t] / AN.UREA[t] / (AN.ARA[t - 1] / AN.UREA[t - 1])), 'LN(Data!J%d/Data!J%d)' % (r, r - 1))
    for c, dc, W in ((10, 'L', AN.W_DRY), (11, 'M', AN.W_FLOWER), (12, 'N', AN.W_WET)):
        v = AN.rain_window(t, W)
        if v is not None:
            put(ch, r, c, math.log(math.exp(v)), 'LN(Data!%s%d)' % (dc, r))
    for c, dc, m in ((13, 'O', 1), (14, 'P', 7)):
        if (t, m) in AN.ONI:
            put(ch, r, c, AN.ONI[(t, m)], 'Data!%s%d' % (dc, r), F2)
    if (4, r - 1) in CV:
        put(ch, r, 15, CV[(4, r - 1)], 'D%d' % (r - 1))
    if (3, r - 1) in CV:
        put(ch, r, 16, CV[(3, r - 1)], 'C%d' % (r - 1))
    if str(t) in HEATS:
        put(ch, r, 17, HEATS[str(t)], 'Data!R%d' % r, F2)
ch.widths = {1: 10, 2: 6, **{c: 13 for c in range(3, 18)}}
ch.freeze = (ROW0, 3)


def correl(c1, c2, t0, t1):
    pr = [(CV[(c1, rowof(t))], CV[(c2, rowof(t))]) for t in range(t0, t1 + 1) if (c1, rowof(t)) in CV and (c2, rowof(t)) in CV]
    x, y = zip(*pr)
    return AN.pearson(x, y), 'CORREL(Changes!%s%d:%s%d,Changes!%s%d:%s%d)' % (
        col_letter(c1), rowof(t0), col_letter(c1), rowof(t1), col_letter(c2), rowof(t0), col_letter(c2), rowof(t1)), len(pr)


# ------------------------------------------------------------------ Tests
ts = wb.add('Tests')
ts.set(1, 1, 'One driver at a time: does it move with output the same year?', TITLE)
ts.set(2, 1, 'r = Pearson correlation of year-on-year changes. p = share of 5 000 random shuffles giving |r| at least as large (purple, Python). Holm p = corrected for testing 14 drivers on the same sample: '
             'below 0.05 = survives. Excel check = the same r recomputed with CORREL where the driver is a column of Changes.', SUB)
DRV_COL = {"biennial: last year's change": {'psd': 15, 'exports': 16}, 'price change, year t vs t-1 (flowering year)': 7, 'coffee/urea ratio change, t vs t-1': 8,
           'rain, dry season Dec-Mar': 10, 'rain, flowering Apr-May': 11, 'rain, rainy season Jun-Oct': 12, 'ENSO, ONI Dec-Feb before flowering': 13,
           'ENSO, ONI Jun-Aug': 14, 'N fertiliser use change (FAO, all crops)': 9}
FR = {"biennial: last year's change": 'Last year\'s change (biennial / mean reversion)', 'price change, year t vs t-1 (flowering year)': 'World arabica price change, year t',
      'price change, year t-1 vs t-2': 'World arabica price change, year t-1', 'price level, year t-1 (log, detrended 5y)': 'Price level t-1 vs its 5-year mean',
      'coffee/urea ratio change, t vs t-1': 'Coffee/urea price ratio change', 'coffee/urea ratio, year t (log, vs 5y mean)': 'Coffee/urea ratio vs its 5-year mean',
      'rain, dry season Dec-Mar': 'Rain Dec-Mar (dry season, before flowering)', 'rain, flowering Apr-May': 'Rain Apr-May (flowering, fruit set)',
      'rain, rainy season Jun-Oct': 'Rain Jun-Oct (fruit fill)', 'rain, previous rainy season May-Oct t-1': 'Rain May-Oct t-1 (wood for this crop)',
      'ENSO, ONI Dec-Feb before flowering': 'ENSO: ONI Dec-Feb', 'ENSO, ONI Jun-Aug': 'ENSO: ONI Jun-Aug', 'Tmax anomaly Mar-May (NASA)': 'Max temperature Mar-May (NASA POWER)',
      'N fertiliser use change (FAO, all crops)': 'Nitrogen use change (FAO)'}
row = 4
for tag, depc, t0, t1, key, title in (('psd_1982_2025', 4, 1982, 2025, 'psd', 'A. USDA production, crop years 1982/83 - 2025/26'),
                                      ('exports_1982_2020', 3, 1982, 2020, 'exports', 'B. IHCAFE measured exports, 1982/83 - 2020/21'),
                                      ('yield_2006_2025', 5, 2006, 2025, 'psd', 'C. USDA yield per bearing hectare, 2006/07 - 2025/26')):
    ts.set(row, 1, title, B)
    row += 1
    ts.row(row, 1, ['Driver', 'n', 'r (Python)', 'p (permutation)', 'Holm p', 'Verdict', 'Excel check r'], H)
    row += 1
    for d in J['screens'][tag]:
        ts.set(row, 1, FR.get(d['driver'], d['driver']))
        ts.set(row, 2, d['n'])
        ts.set(row, 3, d['r'], PY2)
        ts.set(row, 4, d['p'], PY3)
        ts.set(row, 5, d['p_holm'], PY3)
        v = 'robust' if d['p_holm'] < 0.05 else ('weak (p<0.05 alone)' if d['p'] < 0.05 else ('hint (p<0.10)' if d['p'] < 0.10 else 'no link'))
        ts.set(row, 6, v, OK if v == 'robust' else AMB if v != 'no link' else None)
        c = DRV_COL.get(d['driver'])
        if isinstance(c, dict):
            c = c[key]
        if c:
            rr, f, n = correl(depc, c, t0, t1)
            ts.set(row, 7, rr, F2, f)
        row += 1
    row += 1
ts.set(row, 1, 'Reading: only "last year\'s change" (mean reversion) and nitrogen use survive the correction on the long samples. Price, the coffee/urea ratio and dry-season rain pass only one by one. '
               'ENSO, flowering rain, rainy-season rain and temperature: no link.', WRAP)
ts.widths = {1: 44, 2: 5, 3: 11, 4: 13, 5: 9, 6: 20, 7: 13}

# ------------------------------------------------------------------ Biennial
bi = wb.add('Biennial')
bi.set(1, 1, 'Is there an on/off (biennial) cycle, or only one-off shocks?', TITLE)
bi.set(2, 1, 'If output = trend + independent yearly shocks, the correlation between this year\'s change and last year\'s is -0.50 by construction and the direction flips 2 years in 3. '
             'An on/off cycle gives less than -0.50 and more flips; lasting shocks give more than -0.50.', SUB)
bi.row(4, 1, ['Series', 'n', 'r(change t, change t-1)', 'Implied year-to-year link of the level (phi = 1 + 2r)', '95 % band if shocks are independent (low)', '(high)', 'Direction flips', 'Verdict'], H)
for i, (d, (dc, lc, t0, t1)) in enumerate(zip(J['biennial'], ((3, 16, 1972, 2020), (4, 15, 1982, 2025), (5, None, 2007, 2025)))):
    r = 5 + i
    bi.set(r, 1, d['series'])
    bi.set(r, 2, d['n'])
    if lc:
        rr, f, n = correl(dc, lc, t0, t1)
        bi.set(r, 3, rr, F2, f)
        bi.set(r, 4, 1 + 2 * rr, F2, '1+2*C%d' % r)
    else:
        bi.set(r, 3, d['r'], PY2)
        bi.set(r, 4, 1 + 2 * d['r'], F2, '1+2*C%d' % r)
    bi.set(r, 5, d['iid_lo'], PY2)
    bi.set(r, 6, d['iid_hi'], PY2)
    bi.set(r, 7, d['flips'], PYPCT)
    bi.set(r, 8, 'independent shocks, no on/off cycle', OK)
bi.set(9, 1, 'What it means for a forecast', B)
bi.set(10, 1, 'A big crop is followed by a smaller one and a small crop by a bigger one, but only because the shock is not repeated: the crop goes back to its trend, it does not swing below it. '
              'Forecast from the multi-year level (trend), not from last year\'s number and not from an assumed "on/off" year.', WRAP)
bi.set(11, 1, 'Python checks the exports and production rows over slightly different spans (first change 1971 and 1981); the Excel check uses the rows available in Changes.', SUB)
bi.widths = {1: 40, 2: 5, 3: 14, 4: 20, 5: 16, 6: 10, 7: 12, 8: 34}

# ------------------------------------------------------------------ Yield_split
ys = wb.add('Yield_split')
ys.set(1, 1, 'Yield change = production change - bearing-area change', TITLE)
ys.set(2, 1, 'USDA yield = USDA production / attache bearing area. Both are estimates; area revisions move the yield without any change in the trees.', SUB)
ys.row(4, 1, ['Crop year', 'Production change', 'Bearing-area change', 'Yield change', 'Check: production - area', 'Area moved yield by more than 8 points?'], H)
YD = J['yield_decomposition']
for i, d in enumerate(YD['rows']):
    r, rr = 5 + i, rowof(d['year'])
    ys.set(r, 1, lab(d['year']))
    ys.set(r, 2, d['dP'], F3, 'Changes!D%d' % rr)
    ys.set(r, 3, d['dA'], F3, 'Changes!F%d' % rr)
    ys.set(r, 4, d['dY'], F3, 'Changes!E%d' % rr)
    ys.set(r, 5, d['dP'] - d['dA'], F3, 'B%d-C%d' % (r, r))
    ys.set(r, 6, 'yes' if abs(d['dA']) > 0.08 else 'no', None, 'IF(ABS(C%d)>0.08,"yes","no")' % r)
r = 5 + len(YD['rows']) + 1
ys.set(r, 1, 'Variance of yield changes', B)
ys.set(r, 2, YD['var_dY'], Style(color='7030A0', fmt='0.0000'))
ys.set(r + 1, 1, 'of production changes')
ys.set(r + 1, 2, YD['var_dP'], Style(color='7030A0', fmt='0.0000'))
ys.set(r + 2, 1, 'of area changes')
ys.set(r + 2, 2, YD['var_dA'], Style(color='7030A0', fmt='0.0000'))
ys.set(r + 3, 1, '-2 x covariance')
ys.set(r + 3, 2, YD['minus2cov'], Style(color='7030A0', fmt='0.0000'))
ys.set(r + 5, 1, 'Reading (log changes above; in plain %): area revisions of more than 8 % (2006/07 +25 %, 2012/13 +9 %, 2013/14 -20 %, 2016/17 +17 %) move the yield by themselves. The 2013/14 yield rebound (+17 %) is an area cut, not better trees.', WRAP)
ys.widths = {1: 30, 2: 14, 3: 14, 4: 12, 5: 14, 6: 18}

# ------------------------------------------------------------------ Fertiliser
fe = wb.add('Fertiliser')
fe.set(1, 1, 'Nitrogen: the tightest link with output (FAOSTAT, t N, all crops)', TITLE)
fe.set(2, 1, 'Nitrogen bought in calendar year t is spread May-Oct t on the crop harvested from November t. The link is with the same crop year, not the next one.', SUB)
fe.row(4, 1, ['Crop year', 'N use (t)', 'N use change', 'USDA production change', 'Arabica (US$/kg)', 'Urea (US$/t)'], H)
FE = J['fertiliser']
for i, d in enumerate(FE['rows']):
    r, rr = 5 + i, rowof(d['year'])
    fe.set(r, 1, lab(d['year']))
    fe.set(r, 2, d['n_use_t'], F0, 'Data!K%d' % rr)
    fe.set(r, 3, d['dN'], F3, 'Changes!I%d' % rr)
    fe.set(r, 4, d['dP'], F3, 'Changes!D%d' % rr)
    fe.set(r, 5, AN.ARA[d['year']], F2, 'Data!H%d' % rr)
    fe.set(r, 6, AN.UREA[d['year']], F0, 'Data!I%d' % rr)
r0, r1 = 5, 4 + len(FE['rows'])
r = r1 + 2
fe.set(r, 1, 'r(N use change, production change)', B)
fe.set(r, 3, AN.pearson([d['dN'] for d in FE['rows']], [d['dP'] for d in FE['rows']]), F2, 'CORREL(C%d:C%d,D%d:D%d)' % (r0, r1, r0, r1))
fe.set(r + 1, 1, 'Smallest r when any one year is left out (Python)')
fe.set(r + 1, 3, FE['drop_one_min_r'], PY2)
fe.row(r + 3, 1, ['What moves nitrogen use?', 'n', 'r', 'p (permutation)', 'Verdict'], H)
for i, d in enumerate(FE['tests']):
    fe.set(r + 4 + i, 1, d['test'])
    fe.set(r + 4 + i, 2, d['n'])
    fe.set(r + 4 + i, 3, d['r'], PY2)
    fe.set(r + 4 + i, 4, d['p'], PY3)
    fe.set(r + 4 + i, 5, 'yes' if d['p'] < 0.05 else ('hint' if d['p'] < 0.10 else 'no'), OK if d['p'] < 0.05 else AMB if d['p'] < 0.10 else None)
r = r + 5 + len(FE['tests'])
for k, t in enumerate(['Reading: nitrogen and output rise and fall together, in plain % (2011 +53 % / +41 %, 2016 +27 % / +42 %, 2019 -30 % / -27 %, 2020 +49 % / +25 %, 2021 -18 % / -26 %).',
                       'Nitrogen does not follow the world price of the same year; it follows (weakly) the export price received for the previous crop (cash in hand), and state programmes: '
                       'Bono Cafetalero 2020 = 25 188 t of fertiliser to 91 778 producers (USDA 2021), the year nitrogen use jumped 49 %.',
                       'Caution: part of the link can run the other way - growers fertilise more when flowering promises a big crop. For forecasting both readings point the same way: '
                       'fertiliser bought Apr-Sep is a leading signal of the crop harvested from November. FAOSTAT stops in 2024 (2022 imputed): for 2025-26 track fertiliser imports and urea prices instead.']):
    fe.set(r + k, 1, t, WRAP)
fe.widths = {1: 62, 2: 10, 3: 12, 4: 16, 5: 12, 6: 10}

# ------------------------------------------------------------------ Weather
we = wb.add('Weather')
we.set(1, 1, 'Weather: El Nino, La Nina and the driest seasons against output', TITLE)
we.set(2, 1, 'Production change of the crop filled during the event (t) and of the next crop (t+1), flowered in the dry season that follows. USDA production, log change.', SUB)
we.row(4, 1, ['El Nino (ONI Oct-Dec >= 1.0)', 'ONI OND', 'Change crop t', 'Change crop t+1'], H)
r = 5
for d in J['enso']['el_nino']:
    we.set(r, 1, lab(d['year']))
    we.set(r, 2, d['oni_ond'], IN2)
    if d['dP_t'] is not None:
        we.set(r, 3, d['dP_t'], F3, 'Changes!D%d' % rowof(d['year']))
    if d['dP_t1'] is not None:
        we.set(r, 4, d['dP_t1'], F3, 'Changes!D%d' % rowof(d['year'] + 1))
    r += 1
e0, e1 = 5, r - 1
we.set(r, 1, 'Average', B)
we.set(r, 3, st_mean := sum(d['dP_t'] for d in J['enso']['el_nino']) / len(J['enso']['el_nino']), F3, 'AVERAGE(C%d:C%d)' % (e0, e1))
vals1 = [d['dP_t1'] for d in J['enso']['el_nino'] if d['dP_t1'] is not None]
we.set(r, 4, sum(vals1) / len(vals1), F3, 'AVERAGE(D%d:D%d)' % (e0, e1))
r += 2
we.row(r, 1, ['La Nina (ONI Oct-Dec <= -1.0)', 'ONI OND', 'Change crop t', 'Change crop t+1'], H)
r += 1
l0 = r
for d in J['enso']['la_nina']:
    we.set(r, 1, lab(d['year']))
    we.set(r, 2, d['oni_ond'], IN2)
    we.set(r, 3, d['dP_t'], F3, 'Changes!D%d' % rowof(d['year']))
    if d['dP_t1'] is not None:
        we.set(r, 4, d['dP_t1'], F3, 'Changes!D%d' % rowof(d['year'] + 1))
    r += 1
we.set(r, 1, 'Average', B)
we.set(r, 3, sum(d['dP_t'] for d in J['enso']['la_nina']) / len(J['enso']['la_nina']), F3, 'AVERAGE(C%d:C%d)' % (l0, r - 1))
v1 = [d['dP_t1'] for d in J['enso']['la_nina'] if d['dP_t1'] is not None]
we.set(r, 4, sum(v1) / len(v1), F3, 'AVERAGE(D%d:D%d)' % (l0, r - 1))
r += 2
for key, title in (('dry_season', 'Driest dry seasons Dec(t-1)-Mar t (GPCC, 3 towns)'), ('rainy_season', 'Driest rainy seasons Jun-Oct t')):
    we.row(r, 1, [title, 'Rain vs normal', 'Change crop t', 'Change crop t+1'], H)
    r += 1
    for d in J['driest'][key]:
        we.set(r, 1, lab(d['year']))
        we.set(r, 2, d['rain_pct'] / 100, PYPCT)
        we.set(r, 3, d['dP_t'], F3, 'Changes!D%d' % rowof(d['year']))
        if d['dP_t1'] is not None:
            we.set(r, 4, d['dP_t1'], F3, 'Changes!D%d' % rowof(d['year'] + 1))
        r += 1
    r += 1
we.row(r, 1, ['2026 so far (crop 2026/27)', 'GPCC 3 towns', 'ERA5-Land 13 coffee points'], H)
r += 1
for k in ('dry Dec-Mar', 'flowering Apr-May', 'Jun-Aug'):
    we.set(r, 1, 'Rain ' + k + ' vs 1991-2020 normal')
    we.set(r, 2, J['rain_2026'][k] / 100, PYPCT)
    r += 1
CT = J['coffee_zone_tmax']
for k, v in CT['anom_2026'].items():
    we.set(r, 1, k + ', deg C vs 1991-2020 (ERA5-Land coffee zones)')
    we.set(r, 3, v, PY2)
    r += 1
we.set(r, 1, 'Tmax 1-18 Sep 2026, deg C vs September normal (warmer than any full September since 1981)')
we.set(r, 3, CT['sep_2026_to_18'], PY2)
r += 2
we.row(r, 1, ['Max. temperature (ERA5-Land, mean of %d coffee points) vs output' % len(CT['points']), 'Output', 'n', 'r', 'p (permutation)'], H)
r += 1
for d in CT['tests'] + CT['extra_tests']:
    we.row(r, 1, [d['window'], d['dep'], d['n']])
    we.set(r, 4, d['r'], PY2)
    we.set(r, 5, d['p'], PY3)
    r += 1
rr_, f_, n_ = correl(4, 17, 1982, 2025)
we.set(r, 1, 'Excel check: CORREL(production change, Sep-Oct max. temperature), 1982/83-2025/26')
we.set(r, 4, rr_, F2, f_)
r += 1
we.set(r, 1, 'Points: ' + ', '.join(CT['points']) + '. Open-Meteo returned no rain for ERA5-Land; Lempira, Intibuca and Olancho points not obtained (daily quota).', SUB)
r += 2
we.row(r, 1, ['Hottest Sep-Oct (coffee zones)', 'deg C vs normal', 'Output change, crop t'], H)
r += 1
for d in CT['hottest_sep_oct']:
    we.set(r, 1, lab(d['year']))
    we.set(r, 2, d['anom'], PY2)
    we.set(r, 3, d['dP_t'], F3, 'Changes!D%d' % rowof(d['year']))
    r += 1
r += 1
for t in ['Reading: in El Nino years output rose as often as it fell, and the average change is close to zero. 1982, 1997 and 2015 (the three strongest before 2026) gave '
          '+25 %/-13 %, +27 %/-14 % and +4 %/+42 % (crop t / t+1, plain %).',
          'Dry seasons: of the 7 driest Dec-Mar, 4 were followed by a fall of 14 % or more (1985, 1998, 2002, 2019) - the only weather window with a hint, and it does not survive the correction for 14 tests.',
          'Jun-Aug 2026 is the driest in the 1981-2026 record at the three GPCC towns (August at about a fifth of normal). History has no year this dry, so the tests above cannot say how much it will cost.',
          'Heat is different: maximum temperature in Sep-Oct, the two months before the harvest starts, moves against output (r = -0.45; -0.44 once the warming trend is removed; 4 of the 6 hottest Sep-Oct '
          'years saw falls). Found after trying 4 windows, so exploratory - but it also improves the out-of-sample back-test.']:
    we.set(r, 1, t, WRAP)
    r += 1
we.widths = {1: 58, 2: 18, 3: 16, 4: 16, 5: 14}

# ------------------------------------------------------------------ Backtest
bt = wb.add('Backtest')
bt.set(1, 1, 'How well can output be forecast? Errors 2000/01 - 2025/26 (forecast made with data up to the year before)', TITLE)
bt.set(2, 1, 'Actual = USDA production (July 2026 data). Averages and last-year are Excel formulas; the trend and the regressions are refitted each year in Python (purple).', SUB)
M = {d['method']: d for d in J['backtest']['methods']}
cols = ['Last year (random walk)', 'Average of last 2 years', 'Average of last 3 years', 'Average of last 4 years', 'Linear trend, last 8 years',
        'Model: mean reversion + price + dry-season rain', 'Average of last 4 years + price + dry-season rain', 'Combination: mean of (last 2 years) and the model']
bt.row(4, 1, ['Crop year', 'Actual'] + cols + ['Error: ' + c for c in cols], H)
TGT = [p['year'] for p in M[cols[0]]['path']]
for i, t in enumerate(TGT):
    r = 5 + i
    rr = rowof(t)
    bt.set(r, 1, lab(t))
    bt.set(r, 2, AN.PSD[t], F0, 'Data!E%d' % rr)
    fv = {c: next(p['forecast'] for p in M[c]['path'] if p['year'] == t) for c in cols}
    bt.set(r, 3, fv[cols[0]], F0, 'Data!E%d' % (rr - 1))
    for k, c in ((2, 4), (3, 5), (4, 6)):
        f = 'EXP((%s)/%d)' % ('+'.join('LN(Data!E%d)' % (rr - j) for j in range(1, k + 1)), k)
        bt.set(r, c, fv[cols[k - 1]], F0, f)
    for c in (7, 8, 9):
        bt.set(r, c, fv[cols[c - 3]], Style(color='7030A0', fmt='#,##0'))
    bt.set(r, 10, fv[cols[7]], F0, 'SQRT(D%d*H%d)' % (r, r))
    for j in range(len(cols)):
        c = 3 + j
        e = fv[cols[j]] / AN.PSD[t] - 1
        bt.set(r, 3 + len(cols) + j, abs(e), PCT, 'ABS(%s%d/B%d-1)' % (col_letter(c), r, r))
r1 = 4 + len(TGT)
r = r1 + 1
bt.set(r, 1, 'Mean abs. error', B)
for j, c in enumerate(cols):
    cc = 3 + len(cols) + j
    bt.set(r, cc, M[c]['mape'], PCTB, 'AVERAGE(%s5:%s%d)' % (col_letter(cc), col_letter(cc), r1))
r += 3
bt.set(r, 1, 'USDA attache first forecast of the coming crop (Coffee Annual, May of year t), 1 000 60-kg bags', B)
r += 1
bt.row(r, 1, ['Crop year', 'USDA May forecast', 'Actual', 'Abs. error', 'Direction right?'], H)
U = J['backtest']['usda']
u0 = r + 1
for d in U['rows']:
    r += 1
    rr = rowof(d['year'])
    bt.set(r, 1, lab(d['year']))
    bt.set(r, 2, d['usda_may'], IN0)
    bt.set(r, 3, d['actual'], F0, 'Data!E%d' % rr)
    bt.set(r, 4, abs(d['usda_may'] / d['actual'] - 1), PCT, 'ABS(B%d/C%d-1)' % (r, r))
    right = (d['usda_may'] > AN.PSD[d['year'] - 1]) == (d['actual'] > AN.PSD[d['year'] - 1])
    bt.set(r, 5, 'yes' if right else 'no', None, 'IF((B%d>Data!E%d)=(C%d>Data!E%d),"yes","no")' % (r, rr - 1, r, rr - 1))
r += 1
bt.set(r, 1, 'Mean abs. error', B)
bt.set(r, 4, U['mape'], PCTB, 'AVERAGE(D%d:D%d)' % (u0, r - 1))
r += 1
bt.set(r, 1, 'Same 11 years, best simple method (average of last 2 years)')
bt.set(r, 4, U['same_years']['Average of last 2 years'], PYPCT)
r += 2
for t in ['Not used: 2019 (report not found); May 2022, 2023, 2024 reports forecast the crop then being harvested, not the next one.',
          'Reading: every method misses by 12-15 % on average; the USDA May forecast (field information: flowering, rust surveys, IHCAFE) does best at 11.6 %. '
          'Price and rain add nothing out of sample. The edge is in-season tracking (exports, fertiliser, rust bulletins), not a better formula.']:
    bt.set(r, 1, t, WRAP)
    r += 1
bt.widths = {1: 12, 2: 10, **{c: 13 for c in range(3, 3 + 2 * len(cols))}}
bt.freeze = (5, 3)

# ------------------------------------------------------------------ Exports_nowcast
ex = wb.add('Exports_nowcast')
ex.set(1, 1, 'What the 2025/26 exports say about the 2025/26 crop', TITLE)
ex.set(2, 1, 'Export volumes in quintales (bags of 46 kg), as IHCAFE and the press give them. 1 bag of 60 kg = 60/46 quintales. Crop year from 1 October.', SUB)
ex.row(4, 1, ['Cumulative exports to', '2025/26 (quintales)', '2024/25 same date', 'Change', 'Source (read, raw/coffee_zones/)', 'Quote'], H)
for i, (d, v, v0, src, q) in enumerate(NC.CHECKPOINTS):
    r = 5 + i
    ex.set(r, 1, d)
    ex.set(r, 2, v, IN0)
    if v0 is not None:
        if i == 0:
            ex.set(r, 3, v0, F0, 'B%d-28603.67' % r)
        else:
            ex.set(r, 3, v0, IN0)
        ex.set(r, 4, v / v0 - 1, PCT, 'B%d/C%d-1' % (r, r))
    ex.set(r, 5, src, OK)
    ex.set(r, 6, q)
rc = 5 + len(NC.CHECKPOINTS)
R1JUL, R14JUL = 5 + 3, 5 + 4
ex.set(rc + 1, 1, '2024/25 full season (quintales)', B)
ex.set(rc + 1, 2, NC.PREV_FULL, IN0)
ex.set(rc + 1, 5, 'press/04 La Prensa 15 Jul 2026', OK)
ex.set(rc + 2, 1, 'Still to ship at 14 July (sales registered), quintales')
ex.set(rc + 2, 2, NC.PENDING_14JUL, IN0)
ex.set(rc + 2, 5, 'press/04', OK)
ex.set(rc + 3, 1, 'Expected July and August shipments, upper case, each month')
ex.set(rc + 3, 2, NC.JULAUG_HI, IN0)
ex.set(rc + 3, 5, 'press/03 (310 000 - 340 000)', OK)
r = rc + 5
ex.row(r, 1, ['Full-year 2025/26 exports', 'Quintales', '1 000 60-kg bags', 'vs 2024/25'], H)
lo_q = NC.CHECKPOINTS[4][1] + NC.PENDING_14JUL
hi_q = NC.CHECKPOINTS[3][1] + 2 * NC.JULAUG_HI
mid_q = (lo_q + hi_q) / 2
for k, (nm, v, f) in enumerate((('Low: to 14 July + still to ship', lo_q, 'B%d+B%d' % (R14JUL, rc + 2)),
                                ('High: to 1 July + July + August at the upper case', hi_q, 'B%d+2*B%d' % (R1JUL, rc + 3)),
                                ('Middle', mid_q, 'AVERAGE(B%d:B%d)' % (r + 1, r + 2)))):
    rr = r + 1 + k
    ex.set(rr, 1, nm, B if k == 2 else None)
    ex.set(rr, 2, v, F0, f)
    ex.set(rr, 3, v * 46 / 60 / 1000, F0, 'B%d*46/60/1000' % rr)
    ex.set(rr, 4, v / NC.PREV_FULL - 1, PCT, 'B%d/B$%d-1' % (rr, rc + 1))
RMID = r + 3
r = RMID + 2
ex.row(r, 1, ['2025/26 production implied (1 000 60-kg bags)', 'Value', 'How'], H)
exp60 = mid_q * 46 / 60 / 1000
p1 = exp60 + NC.DOMESTIC
p2 = AN.PSD[2024] * mid_q / NC.PREV_FULL
ex.set(r + 1, 1, 'USDA domestic consumption 2025/26')
ex.set(r + 1, 2, NC.DOMESTIC, IN0)
ex.set(r + 2, 1, 'Stock change assumed (0 = everything exported or used came from the crop)')
ex.set(r + 2, 2, 0, IN0)
ex.set(r + 3, 1, 'A. Balance: exports + domestic use + stock change')
ex.set(r + 3, 2, p1, F0, 'C%d+B%d+B%d' % (RMID, r + 1, r + 2))
ex.set(r + 4, 1, 'B. USDA 2024/25 production x IHCAFE export growth')
ex.set(r + 4, 2, p2, F0, 'Data!E%d*B%d/B%d' % (rowof(2024), RMID, rc + 1))
ex.set(r + 5, 1, 'Export-implied 2025/26 production (average of A and B)', B)
base_x = (p1 + p2) / 2
ex.set(r + 5, 2, base_x, Style(bold=True, fmt='#,##0'), 'AVERAGE(B%d:B%d)' % (r + 3, r + 4))
ex.set(r + 6, 1, 'USDA estimate of 2025/26 production (May 2026)')
ex.set(r + 6, 2, AN.PSD[2025], F0, 'Data!E%d' % rowof(2025))
ex.set(r + 7, 1, 'Export-implied minus USDA', B)
ex.set(r + 7, 2, base_x / AN.PSD[2025] - 1, PCTB, 'B%d/B%d-1' % (r + 5, r + 6))
ex.set(r + 8, 1, 'USDA export estimate 2025/26 (1 000 bags) and change on 2024/25')
ex.set(r + 8, 2, 5028, IN0)
ex.set(r + 8, 3, 5028 / 4958 - 1, PCT, 'B%d/4958-1' % (r + 8))
NOWCAST_CELL = 'Exports_nowcast!B%d' % (r + 5)
NOWCAST_VAL = base_x
r += 10
ex.row(r, 1, ['Share of the year shipped by the end of month', '2020/21', '2021/22'], H)
for i, m in enumerate(['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']):
    rr = r + 1 + i
    ex.set(rr, 1, m)
    for c, y in ((2, '2020/21'), (3, '2021/22')):
        ex.set(rr, c, sum(NC.MONTHLY[y][:i + 1]) / sum(NC.MONTHLY[y]), PCT)
ex.set(r + 13, 1, 'IHCAFE bulletins 30-08-2022 and 07-02-2023 (monthly exports, read). In 2025/26, 3 March already held about 42 % of the middle full-year figure, against 24-32 % by end February in 2020/21-2021/22: a front-loaded year.', SUB)
r += 15
for t in NC.NOTES:
    ex.set(r, 1, t, WRAP)
    r += 1
ex.widths = {1: 58, 2: 16, 3: 16, 4: 11, 5: 32, 6: 110}

# ------------------------------------------------------------------ Forecast_2026_27
fc = wb.add('Forecast_2026_27')
fc.set(1, 1, 'Crop 2026/27 (harvest Nov 2026 - Mar 2027): scorecard and range', TITLE)
fc.set(2, 1, 'Each line: the 2026 value, what history says it does, and the direction for 2026/27. Production in 1 000 60-kg bags.', SUB)
fc.row(4, 1, ['Driver', '2025 (or before)', '2026', 'Change', 'Evidence (this workbook)', 'Direction for 2026/27'], H)
I = J['inputs_2026']
rows = [
    ('World arabica, US$/kg (World Bank, 2026 = Jan-Aug)', I['arabica_2025'], I['arabica_2026'], 'Data!H%d' % rowof(2025), 'Data!H%d' % rowof(2026),
     'price change alone: weak (Tests); still 32 % above 2024', 'neutral to slightly negative'),
    ('Urea, US$/t', I['urea_2025'], I['urea_2026'], 'Data!I%d' % rowof(2025), 'Data!I%d' % rowof(2026), 'fertiliser is the tightest link (Fertiliser)', 'negative: dearer nitrogen'),
    ('kg urea bought by 1 kg coffee', I['ratio_2025'], I['ratio_2026'], 'Data!J%d' % rowof(2025), 'Data!J%d' % rowof(2026), 'back to the 2014-2015 level (12.7-14.3)', 'negative vs 2025, normal vs history'),
]
r = 5
for name, a_, b_, fa, fb, ev_, dirn in rows:
    fc.set(r, 1, name)
    fc.set(r, 2, a_, F2, fa)
    fc.set(r, 3, b_, F2, fb)
    fc.set(r, 4, b_ / a_ - 1, PCT, 'C%d/B%d-1' % (r, r))
    fc.set(r, 5, ev_)
    fc.set(r, 6, dirn, AMB)
    r += 1
for name, a_, b_, st_, ev_, dirn, sty in NC.SCORE_TEXT:
    fc.set(r, 1, name)
    if a_ is not None:
        fc.set(r, 2, a_, IN2 if abs(a_) < 100 else IN0)
    if b_ is not None:
        fc.set(r, 3, b_, IN2 if abs(b_) < 100 else IN0)
    fc.set(r, 5, ev_)
    fc.set(r, 6, dirn, {'neg': WARN, 'pos': OK, 'amb': AMB}[sty])
    r += 1
r += 1
# inputs of the two models
fc.set(r, 1, 'Model inputs', B)
fc.row(r + 1, 1, ['Input', 'Value', 'Source'], H)
inp = {}
dpc = math.log(AN.ARA[2026] / AN.ARA[2025])
dry26 = math.exp(AN.rain_window(2026, AN.W_DRY))
HM = J['heat_model']['coef']
cf = R['model_psd_1982_2025_M5 M2 + dry-season rain']['coef']
items = [('base_u', 'USDA production 2025/26', AN.PSD[2025], F0, 'Data!E%d' % rowof(2025)),
         ('base_x', 'Export-implied production 2025/26', NOWCAST_VAL, F0, NOWCAST_CELL),
         ('p24', 'USDA production 2024/25', AN.PSD[2024], F0, 'Data!E%d' % rowof(2024)),
         ('dpc', 'World price change 2026 vs 2025 (log)', dpc, F3, 'LN(Data!H%d/Data!H%d)' % (rowof(2026), rowof(2025))),
         ('dry', 'Rain Dec 2025 - Mar 2026 / normal', dry26, F2, 'Data!L%d' % rowof(2026)),
         ('a0', 'Model without heat: intercept', cf['intercept'], None, None),
         ('a1', "  last year's change", cf["biennial: last year's change"], None, None),
         ('a2', '  price change', cf['price change, year t vs t-1 (flowering year)'], None, None),
         ('a3', '  rain Dec-Mar (log)', cf['rain, dry season Dec-Mar'], None, None),
         ('b0', 'Model with heat: intercept', HM['intercept'], None, None),
         ('b1', "  last year's change", HM['last_change'], None, None),
         ('b2', '  price change', HM['price_change'], None, None),
         ('b3', '  rain Dec-Mar (log)', HM['dry_rain_log'], None, None),
         ('b4', '  max. temperature Sep-Oct, deg C vs normal', HM['tmax_sep_oct'], None, None)]
rr = r + 2
for key, nm, v, sty, f in items:
    fc.set(rr, 1, nm)
    fc.set(rr, 2, v, sty if f else Style(color='7030A0', fmt='0.0000'), f)
    fc.set(rr, 3, 'formula' if f else 'Python fit, USDA production 1983/84-2025/26 (robustness.py / analysis.py)')
    inp[key] = 'B%d' % rr
    rr += 1
r = rr + 1
H26 = J['coffee_zone_tmax']['sep_2026_to_18']
JA26 = J['coffee_zone_tmax']['anom_2026']['Tmax Jun-Aug (fruit fill)']
fc.row(r, 1, ['Sep-Oct 2026 heat scenario (deg C above 1991-2020)', 'Value', 'Why'], H)
scen = [('Mild: Sep-Oct like Jun-Aug 2026', JA26, 'Jun-Aug 2026 coffee-zone anomaly (ERA5-Land)'),
        ('Central: 1-18 Sep so far, October like Jun-Aug', (H26 + JA26) / 2, 'average of the two'),
        ('Hot: October as hot as 1-18 September', H26, '1-18 Sep 2026 anomaly, warmer than any full September since 1981')]
srow = {}
for k, (nm, v, why) in enumerate(scen):
    fc.set(r + 1 + k, 1, nm)
    if k == 1:
        fc.set(r + 1 + k, 2, v, F2, 'AVERAGE(B%d,B%d)' % (r + 1, r + 3))
    else:
        fc.set(r + 1 + k, 2, v, IN2)
    fc.set(r + 1 + k, 3, why)
    srow[k] = 'B%d' % (r + 1 + k)
r += 5
fc.row(r, 1, ['2026/27 production by method (1 000 60-kg bags)', 'On USDA base', 'On export-implied base', 'Change vs export-implied 2025/26', 'Back-test miss', 'Note'], H)
r += 1


def m5v(base):
    return base * math.exp(cf['intercept'] + cf["biennial: last year's change"] * math.log(base / AN.PSD[2024]) + cf['price change, year t vs t-1 (flowering year)'] * dpc
                           + cf['rain, dry season Dec-Mar'] * math.log(dry26))


def m5f(bc):
    return '%s*EXP(%s+%s*LN(%s/%s)+%s*%s+%s*LN(%s))' % (bc, inp['a0'], inp['a1'], bc, inp['p24'], inp['a2'], inp['dpc'], inp['a3'], inp['dry'])


def m7v(base, h):
    return base * math.exp(HM['intercept'] + HM['last_change'] * math.log(base / AN.PSD[2024]) + HM['price_change'] * dpc + HM['dry_rain_log'] * math.log(dry26) + HM['tmax_sep_oct'] * h)


def m7f(bc, hc):
    return '%s*EXP(%s+%s*LN(%s/%s)+%s*%s+%s*LN(%s)+%s*%s)' % (bc, inp['b0'], inp['b1'], bc, inp['p24'], inp['b2'], inp['dpc'], inp['b3'], inp['dry'], inp['b4'], hc)


BU, BX = inp['base_u'], inp['base_x']
bu, bx = AN.PSD[2025], NOWCAST_VAL
ma2 = lambda b: math.sqrt(AN.PSD[2024] * b)
Hc = (H26 + JA26) / 2
meth = [('USDA (May 2026)', 6030, None, None, None, 0.116, 'IHCAFE-based; assumes 2025/26 = 5 530'),
        ('A. Average of last 2 years', ma2(bu), ma2(bx), 'SQRT(%s*%s)' % (inp['p24'], BU), 'SQRT(%s*%s)' % (inp['p24'], BX), M['Average of last 2 years']['mape'], 'best simple method'),
        ('B. Model: mean reversion + price + Dec-Mar rain', m5v(bu), m5v(bx), m5f(BU), m5f(BX), M['Model: mean reversion + price + dry-season rain']['mape'], 'does not see the heat or the Jun-Aug drought'),
        ('C. Model B + Sep-Oct heat, mild scenario', m7v(bu, JA26), m7v(bx, JA26), m7f(BU, srow[0]), m7f(BX, srow[0]), M['Model + Sep-Oct heat (coffee zones)']['mape'], ''),
        ('C. Model B + Sep-Oct heat, central scenario', m7v(bu, Hc), m7v(bx, Hc), m7f(BU, srow[1]), m7f(BX, srow[1]), M['Model + Sep-Oct heat (coffee zones)']['mape'], 'best back-test (10.5 %)'),
        ('C. Model B + Sep-Oct heat, hot scenario', m7v(bu, H26), m7v(bx, H26), m7f(BU, srow[2]), m7f(BX, srow[2]), M['Model + Sep-Oct heat (coffee zones)']['mape'], ''),
        ('Combination A and C central', math.sqrt(ma2(bu) * m7v(bu, Hc)), math.sqrt(ma2(bx) * m7v(bx, Hc)), 'SQRT(B{a}*B{c})', 'SQRT(C{a}*C{c})',
         M['Combination: last 2 years and model + heat']['mape'], 'central forecast'),
        ('Last year (random walk)', bu, bx, BU, BX, M['Last year (random walk)']['mape'], 'worst direction score (38 %)')]
m0 = r
for k, (name, vu, vx, fu, fx_, err, note) in enumerate(meth):
    if fu and '{a}' in fu:
        fu, fx_ = fu.format(a=m0 + 1, c=m0 + 4), fx_.format(a=m0 + 1, c=m0 + 4)
    fc.set(r, 1, name, B if name.startswith('Combination') else None)
    fc.set(r, 2, vu, IN0 if fu is None else F0, fu)
    if vx is not None:
        fc.set(r, 3, vx, Style(bold=True, fmt='#,##0') if name.startswith('Combination') else F0, fx_)
        fc.set(r, 4, vx / bx - 1, PCT, 'C%d/%s-1' % (r, BX))
    fc.set(r, 5, err, PYPCT)
    fc.set(r, 6, note)
    r += 1
CB = M['Combination: last 2 years and model + heat']['mape']
central = math.sqrt(ma2(bx) * m7v(bx, Hc))
fc.set(r, 1, 'Range = central +/- its back-test miss')
fc.set(r, 2, central * (1 - CB), F0, 'C%d*(1-E%d)' % (m0 + 6, m0 + 6))
fc.set(r, 3, central * (1 + CB), F0, 'C%d*(1+E%d)' % (m0 + 6, m0 + 6))
FC_OUT = dict(base_usda=bu, base_exports=bx, exports_q=dict(lo=lo_q, hi=hi_q, mid=mid_q), balance=p1, ratio=p2, heat=dict(mild=JA26, central=Hc, hot=H26),
              methods={m[0]: dict(usda_base=m[1], export_base=m[2], mape=m[5]) for m in meth}, central=central, lo=central * (1 - CB), hi=central * (1 + CB), mape=CB,
              no_heat=dict(model=m5v(bx), comb=math.sqrt(ma2(bx) * m5v(bx))))
json.dump(FC_OUT, open(HERE + '../yield_drivers/forecast_2026_27.json', 'w'), indent=1)
r += 2
for t in NC.FORECAST_NOTES:
    fc.set(r, 1, t, WRAP)
    r += 1
fc.widths = {1: 58, 2: 16, 3: 18, 4: 16, 5: 46, 6: 36}

wb.save(OUT)
print('saved', OUT)
