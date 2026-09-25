"""Honduras coffee towns (Comayagua, Ocotepeque, Copán): monthly temperature and rainfall by ENSO season (July-June),
same seasons, months, ENSO rule and checks as research/indonesia/excel/build_weather_xlsx.py.
Daily NASA POWER data -> monthly values (SUMIFS / AVERAGEIFS formulas, cached values written too) -> one chart sheet per location.
Seasons classified with NOAA CPC's official rule on the ONI table. Standard library only."""
import json, os, sys, datetime, statistics as st, decimal, csv, math, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../../indonesia/excel')
from xlsxw import Workbook, Style, ref, col_letter

HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
RAW = HERE + '../raw/'
ONI_FILE = HERE + '../../indonesia/raw/oni.ascii.txt'   # the same ONI file as the Indonesia workbook
OUT = HERE + 'Honduras_weather_by_ENSO_season.xlsx'

TOWNS = [('comayagua', 'Comayagua', 'Comayagua department, town of Comayagua'), ('ocotepeque', 'Ocotepeque', 'Ocotepeque department, town of Nueva Ocotepeque'),
         ('copan', 'Copán', 'Copán department, town of Santa Rosa de Copán')]
SS3 = ['comayagua', 'ocotepeque', 'copan']
NT = len(TOWNS)
VARS = [('RAIN_CPC', 'Rain, CPC gauges (mm)'), ('T2M', 'Mean temp (°C)'), ('T2M_MAX', 'Max temp (°C)'), ('T2M_MIN', 'Min temp (°C)'), ('PRECTOTCORR', 'NASA rain, not used (mm)')]
RAIN = {'RAIN_CPC', 'PRECTOTCORR'}
START = datetime.date(2005, 7, 1)
PHOTO = list(range(2005, 2025))           # seasons 2005/06 ... 2024/25, the 20 seasons of the São Mateus chart
EXTRA = [2025, 2026]                       # after the photo window
MONTHS = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
CAL = [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6]
MNAME = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
SEAS = ['DJF', 'JFM', 'FMA', 'MAM', 'AMJ', 'MJJ', 'JJA', 'JAS', 'ASO', 'SON', 'OND', 'NDJ']


def season_of(y, m):
    return y if m >= 7 else y - 1


def slabel(Y):
    return '%d/%s' % (Y, str(Y + 1)[2:])


def rnd1(x):  # Excel ROUND(x,1): half away from zero
    return float(decimal.Decimal(repr(x)).quantize(decimal.Decimal('0.1'), rounding=decimal.ROUND_HALF_UP))


# ---------------- load data ----------------
DAY, GEO = {}, {}
for t, _, _ in TOWNS:
    j = json.load(open(RAW + 'nasa_power_daily_%s.json' % t))
    DAY[t] = j['properties']['parameter']
    GEO[t] = j['geometry']['coordinates']
    HDR = j['header']
# rain: CPC Global Unified Gauge-Based daily analysis (NOAA PSL), nearest 0.5° cell; NASA PRECTOTCORR drifts +34-42 % after 2020 here
CPC_FILLED = []
for t in DAY:
    DAY[t]['RAIN_CPC'] = {}
for row in csv.DictReader(open(RAW + 'independent/cpc_precip_daily.csv')):
    k = row['date'].replace('-', '')
    if row['precip_mm'] == '':
        continue
    DAY[row['town']]['RAIN_CPC'][k] = float(row['precip_mm'])
for t in DAY:
    for k in DAY[t]['PRECTOTCORR']:
        if k >= '20050101' and k not in DAY[t]['RAIN_CPC'] and k <= max(DAY[t]['RAIN_CPC']):
            DAY[t]['RAIN_CPC'][k] = DAY[t]['PRECTOTCORR'][k]
            CPC_FILLED.append((t, k))
LASTDAY = min(min(max(DAY[t]['T2M']) for t in DAY), min(max(DAY[t]['RAIN_CPC']) for t in DAY))
END = datetime.date(int(LASTDAY[:4]), int(LASTDAY[4:6]), int(LASTDAY[6:]))
dates = []
d = START
while d <= END:
    dates.append(d)
    d += datetime.timedelta(days=1)
for t in DAY:
    for v, _ in VARS:
        for d in dates:
            x = DAY[t][v][d.strftime('%Y%m%d')]
            assert x != -999.0, (t, v, d)

# Copán: the CPC cell loses its gauge in January 2024 (CPC 49 % and 41 % of normal in 2024 and 2025, while GPCC says 92 % and 103 %
# and NASA 122 % and 75 %). From that month on, Copán rain = GPCC monthly x (CPC / GPCC ratio of the same calendar month, 2005-2019),
# which keeps the series on the CPC level. Daily sheet keeps the raw CPC values.
GPC = collections.defaultdict(dict)
for row in csv.DictReader(open(RAW + 'rain_check/gpcc_1981_2026_monthly.csv')):
    GPC[row['town']][(int(row['year']), int(row['month']))] = float(row['rain_mm'])
GSRC = {(int(row['year']), int(row['month'])): row['source'] for row in csv.DictReader(open(RAW + 'rain_check/gpcc_1981_2026_monthly.csv'))}
REPL_FROM = {'copan': (2024, 1)}
KCP = {}
for t in REPL_FROM:
    cm = collections.defaultdict(float)
    for k, v in DAY[t]['RAIN_CPC'].items():
        if '2005' <= k[:4] <= '2019':
            cm[(int(k[:4]), int(k[4:6]))] += v
    KCP[t] = {m: sum(cm[(y, m)] for y in range(2005, 2020)) / sum(GPC[t][(y, m)] for y in range(2005, 2020)) for m in range(1, 13)}
REPLACED = {}  # (town, 'YYYY-MM') -> (raw CPC, GPCC, factor, value used)
REPLS = Style(fmt='0.0', color='0000FF', fill='FFF2CC')

oni = []  # [key, year, centre month, code, anom]
for line in open(ONI_FILE).read().splitlines()[1:]:
    if not line.strip():
        continue
    code, yr, tot, an = line.split()
    m = SEAS.index(code) + 1
    oni.append(['%s-%02d' % (yr, m), int(yr), m, code, float(an)])
# official episodes: rounded ONI >= +0.5 / <= -0.5 for 5+ consecutive overlapping periods
state = ['warm' if rnd1(o[4]) >= 0.5 else 'cold' if rnd1(o[4]) <= -0.5 else 'neutral' for o in oni]
n_oni = len(oni)
up, down = [0] * n_oni, [0] * n_oni
for i in range(n_oni):
    up[i] = up[i - 1] + 1 if i and state[i] == state[i - 1] else 1
for i in reversed(range(n_oni)):
    down[i] = down[i + 1] + 1 if i < n_oni - 1 and state[i] == state[i + 1] else 1
episode = []
for i in range(n_oni):
    run = up[i] + down[i] - 1
    if state[i] == 'neutral':
        episode.append('—')
    elif run >= 5:
        episode.append('El Niño' if state[i] == 'warm' else 'La Niña')
    elif i + down[i] - 1 == n_oni - 1:
        episode.append('El Niño (ongoing)' if state[i] == 'warm' else 'La Niña (ongoing)')
    else:
        episode.append('—')
ONI = {o[0]: (o[4], o[3], episode[k]) for k, o in enumerate(oni)}
LAST_ONI = oni[-1]


def season_phase(Y):
    k = '%d-12' % Y
    if k not in ONI:  # NDJ not yet published: current season
        return 'El Niño' if episode[-1].startswith('El Niño') else 'La Niña' if episode[-1].startswith('La Niña') else 'Neutral'
    e = ONI[k][2]
    return 'El Niño' if e.startswith('El Niño') else 'La Niña' if e.startswith('La Niña') else 'Neutral'


# ---------------- styles ----------------
wb = Workbook('Arial')
H = Style(bold=True, color='FFFFFF', fill='1F3864', halign='center', wrap=True)
HL = Style(bold=True, color='FFFFFF', fill='1F3864', wrap=True)
TITLE = Style(bold=True, size=14, color='1F3864')
SUB = Style(italic=True, color='595959')
B = Style(bold=True)
TXT = Style()
WRAP = Style(wrap=True)
DATE = Style(fmt='yyyy-mm-dd', halign='center')
C = Style(halign='center')
N1 = Style(fmt='0.0')
N2 = Style(fmt='0.00')
N0 = Style(fmt='0')
RED = Style(bold=True, color='C00000')
PH_FILL = {'El Niño': 'FCE4D6', 'La Niña': 'DDEBF7', 'Neutral': 'EDEDED'}
PH_FONT = {'El Niño': 'C00000', 'La Niña': '2E75B6', 'Neutral': '404040'}


def phs(ph, fmt=None, bold=False):
    base = 'El Niño' if ph.startswith('El Niño') else 'La Niña' if ph.startswith('La Niña') else 'Neutral'
    return Style(fill=PH_FILL[base], fmt=fmt, bold=bold, color=PH_FONT[base] if bold else '000000')


# sheet objects (order = tab order)
readme = wb.add('README')
charts = {}
LOCS = [('SS3', 'Chart_Mean_3', 'Honduras, mean of 3 towns (Comayagua, Ocotepeque, Copán)')] + [(t, 'Chart_' + nm.replace('á', 'a'), '%s — %s' % (nm, prov)) for t, nm, prov in TOWNS]
for lid, sname, _ in LOCS:
    charts[lid] = wb.add(sname)
clong = wb.add('Chart_long')
sea = wb.add('ENSO_seasons')
mon = wb.add('Monthly')
day = wb.add('Daily')
em = wb.add('ENSO_monthly')
chk = wb.add('Checks')

# ---------------- ENSO_monthly ----------------
em.row(1, 1, ['Key (year-centre month)', 'Year', 'Centre month', 'NOAA period', 'Months covered', 'ONI (°C, as published)', 'ONI rounded to 0.1 (as in the NOAA table)',
              'Threshold state (±0.5)', 'Periods in run, counted forward', 'Periods in run, counted back', 'Run length (periods)', 'Official ENSO episode', 'Coffee season (Jul–Jun) of the centre month'], H)
EM_ROW = {}
first_em, last_em = 2, 1 + n_oni
for k, o in enumerate(oni):
    r = 2 + k
    key, yr, m, code, an = o
    EM_ROW[key] = r
    m0 = (m - 2) % 12 + 1
    m1 = m % 12 + 1
    y0 = yr - 1 if m == 1 else yr
    y1 = yr + 1 if m == 12 else yr
    cover = '%s %d – %s %d' % (MNAME[m0 - 1], y0, MNAME[m1 - 1], y1)
    em.set(r, 1, key, C)
    em.set(r, 2, yr, C)
    em.set(r, 3, m, C)
    em.set(r, 4, code, C)
    em.set(r, 5, cover)
    em.set(r, 6, an, N2)
    em.set(r, 7, rnd1(an), N1, 'ROUND(F%d,1)' % r)
    em.set(r, 8, state[k], C, 'IF(G{0}>=0.5,"warm",IF(G{0}<=-0.5,"cold","neutral"))'.format(r))
    em.set(r, 9, up[k], C, '1' if k == 0 else 'IF(H{0}=H{1},I{1}+1,1)'.format(r, r - 1))
    em.set(r, 10, down[k], C, '1' if k == n_oni - 1 else 'IF(H{0}=H{1},J{1}+1,1)'.format(r, r + 1))
    em.set(r, 11, up[k] + down[k] - 1, C, 'I{0}+J{0}-1'.format(r))
    em.set(r, 12, episode[k], phs(episode[k]) if episode[k] != '—' else C,
           'IF(H{0}="neutral","—",IF(K{0}>=5,IF(H{0}="warm","El Niño","La Niña"),IF(ROW()+J{0}-1={1},IF(H{0}="warm","El Niño (ongoing)","La Niña (ongoing)"),"—")))'.format(r, last_em))
    em.set(r, 13, slabel(season_of(yr, m)), C)
em.set(last_em + 2, 1, 'Source: NOAA CPC, oni.ascii.txt (https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt), downloaded September 2026, last period %s %d = %+.2f.' % (LAST_ONI[3], LAST_ONI[1], LAST_ONI[4]), SUB)
em.set(last_em + 3, 1, 'Rule (NOAA CPC): warm/cold when the ONI, rounded to 0.1 °C, is ≥ +0.5 / ≤ −0.5; an El Niño or La Niña episode needs at least 5 consecutive overlapping 3-month periods. A run that reaches the last published period is marked "ongoing".', SUB)
em.widths = {1: 12, 2: 7, 3: 8, 4: 8, 5: 20, 6: 11, 7: 13, 8: 11, 9: 11, 10: 11, 11: 10, 12: 18, 13: 12}
em.freeze = (2, 2)

# ---------------- ENSO_seasons ----------------
SY = list(range(1981, 2027))
hdr = ['Season (Jul–Jun)', 'First day', 'Last day'] + ['ONI %s (centre %s)' % (SEAS[(m - 1)], MONTHS[i]) for i, m in enumerate(CAL)] + [
    'Periods in an El Niño episode', 'Periods in a La Niña episode', 'ONI Nov–Jan (NDJ, peak season)', 'Largest ONI of the season (sign kept)',
    'Official episode at NDJ', 'SEASON PHASE (used in the charts)', 'Strength (largest |ONI|)', 'In the photo window 2005/06–2024/25', 'Note']
sea.row(1, 1, hdr, H)
SEA_ROW = {}
NOTES = {2016: 'ONI SON −0.51 and OND −0.49 round to −0.5, but only 2 periods: no official La Niña (NOAA did not declare one on the ONI).',
         2024: 'La Niña conditions announced by NOAA in Jan 2025, but the ONI reached −0.5 only in DJF (−0.46): not an official episode.',
         2025: 'ONI ≤ −0.5 for 3 periods only (SON −0.57, OND −0.61, NDJ −0.60): not an official La Niña. El Niño builds from MAM 2026.',
         2026: 'In progress. ONI ≥ +0.5 since MAM 2026 (4 periods to JJA 2026: +0.46→+0.5, +0.95, +1.39, +1.80); NOAA El Niño Advisory in force. Classed El Niño.',
         2005: 'Weak La Niña: OND 2005 to FMA 2006 (5 periods).', 2014: 'Weak El Niño from SON 2014 (+0.51); the same run continues into the very strong 2015/16 event.',
         2019: 'Weak El Niño: SON 2019 to FMA 2020 (6 periods, peak +0.75).', 2022: 'La Niña Jul 2022–Jan 2023; El Niño starts AMJ 2023 (in 2023/24).'}
for k, Y in enumerate(SY):
    r = 2 + k
    SEA_ROW[Y] = r
    ph = season_phase(Y)
    sea.set(r, 1, slabel(Y), phs(ph, bold=True))
    sea.set(r, 2, datetime.date(Y, 7, 1), DATE)
    sea.set(r, 3, datetime.date(Y + 1, 6, 30), DATE)
    vals = []
    for i, m in enumerate(CAL):
        key = '%d-%02d' % (Y + (1 if m < 7 else 0), m)
        if key in ONI:
            v = ONI[key][0]
            vals.append(v)
            e = ONI[key][2]
            sea.set(r, 4 + i, v, phs(e, '0.00') if e != '—' else N2, 'INDEX(ENSO_monthly!$F:$F,MATCH("%s",ENSO_monthly!$A:$A,0))' % key)
        else:
            sea.set(r, 4 + i, 'n/a', C)
    en = sum(1 for m in CAL if ONI.get('%d-%02d' % (Y + (1 if m < 7 else 0), m), (0, 0, '—'))[2].startswith('El Niño'))
    ln = sum(1 for m in CAL if ONI.get('%d-%02d' % (Y + (1 if m < 7 else 0), m), (0, 0, '—'))[2].startswith('La Niña'))
    sea.set(r, 16, en, C, 'COUNTIFS(ENSO_monthly!$M:$M,A{0},ENSO_monthly!$L:$L,"El Niño*")'.format(r))
    sea.set(r, 17, ln, C, 'COUNTIFS(ENSO_monthly!$M:$M,A{0},ENSO_monthly!$L:$L,"La Niña*")'.format(r))
    kdec = '%d-12' % Y
    if kdec in ONI:
        sea.set(r, 18, ONI[kdec][0], N2, 'I%d' % r)
        pk = max(vals, key=abs)
        sea.set(r, 19, pk, N2, 'IF(MAX(D{0}:O{0})>=-MIN(D{0}:O{0}),MAX(D{0}:O{0}),MIN(D{0}:O{0}))'.format(r))
        sea.set(r, 20, ONI[kdec][2], C, 'INDEX(ENSO_monthly!$L:$L,MATCH("%s",ENSO_monthly!$A:$A,0))' % kdec)
        sea.set(r, 21, ph, phs(ph, bold=True), 'IF(LEFT(T{0},7)="El Niño","El Niño",IF(LEFT(T{0},7)="La Niña","La Niña","Neutral"))'.format(r))
        a = abs(rnd1(pk))
        strength = '' if ph == 'Neutral' else 'weak' if a < 1.0 else 'moderate' if a < 1.5 else 'strong' if a < 2.0 else 'very strong'
        sea.set(r, 22, strength, C, 'IF(U{0}="Neutral","",IF(ABS(ROUND(S{0},1))<1,"weak",IF(ABS(ROUND(S{0},1))<1.5,"moderate",IF(ABS(ROUND(S{0},1))<2,"strong","very strong"))))'.format(r))
    else:
        sea.set(r, 18, 'n/a', C)
        pk = max(vals, key=abs)
        sea.set(r, 19, pk, N2, 'IF(MAX(D{0}:O{0})>=-MIN(D{0}:O{0}),MAX(D{0}:O{0}),MIN(D{0}:O{0}))'.format(r))
        sea.set(r, 20, 'not yet published', C)
        sea.set(r, 21, ph, phs(ph, bold=True))
        sea.set(r, 22, 'in progress', C)
    sea.set(r, 23, 'yes' if Y in PHOTO else 'no', C)
    sea.set(r, 24, NOTES.get(Y, ''), TXT)
sea.set(2 + len(SY) + 1, 1, 'Season phase = official NOAA episode status of the Nov–Jan (NDJ) ONI period, the peak of ENSO. Cells coloured when the period is inside an official episode (red El Niño, blue La Niña).', SUB)
sea.set(2 + len(SY) + 2, 1, 'With this rule the 20 seasons 2005/06–2024/25 split 7 El Niño / 9 La Niña / 4 Neutral, the same counts as the São Mateus chart.', SUB)
sea.widths = {1: 10, 2: 11, 3: 11, **{c: 8.5 for c in range(4, 16)}, 16: 10, 17: 10, 18: 10, 19: 10, 20: 16, 21: 14, 22: 11, 23: 11, 24: 70}
sea.freeze = (2, 2)

# ---------------- Daily ----------------
day.set(1, 1, 'Date', H)
day.set(1, 2, 'Month key', H)
day.set(1, 3, 'Coffee season', H)
day.set(2, 1, '(local solar time)', SUB)
DCOL = {}
c = 4
for t, nm, _ in TOWNS:
    day.set(1, c, nm, H)
    for j, (v, lab) in enumerate(VARS):
        day.set(1, c + j, nm, H)
        day.set(2, c + j, lab, H)
        DCOL[(t, v)] = c + j
    day.merges.append('%s:%s' % (ref(1, c), ref(1, c + len(VARS) - 1)))
    c += len(VARS)
D0 = 3
D1 = D0 + len(dates) - 1
for i, d in enumerate(dates):
    r = D0 + i
    day.set(r, 1, d, DATE)
    day.set(r, 2, d.strftime('%Y-%m'), C)
    day.set(r, 3, slabel(season_of(d.year, d.month)), C)
    ds = d.strftime('%Y%m%d')
    for t, _, _ in TOWNS:
        for v, _ in VARS:
            day.set(r, DCOL[(t, v)], DAY[t][v][ds])
day.widths = {1: 11, 2: 9, 3: 9, **{cc: 9.5 for cc in range(4, 4 + NT * len(VARS))}}
day.freeze = (3, 2)

# ---------------- Monthly ----------------
months = []
y, m = START.year, START.month
while (y, m) <= (END.year, END.month):
    months.append((y, m))
    y, m = (y + 1, 1) if m == 12 else (y, m + 1)
mhdr = ['Month key', 'Year', 'Month', 'Month name', 'Coffee season (Jul–Jun)', 'Month of the season (Jul = 1)', 'First day', 'Last day', 'Days in month',
        'Days with data', 'Complete?', 'ONI of the 3-month period centred on this month', 'NOAA period', 'Official ENSO state of this month', 'Phase of the season']
mon.row(2, 1, mhdr, H)
MCOL = {}
c = len(mhdr) + 1
for t, nm, _ in TOWNS:
    for j, (v, lab) in enumerate(VARS):
        mon.set(1, c + j, nm, H)
        mon.set(2, c + j, lab, H)
        MCOL[(t, v)] = c + j
    mon.merges.append('%s:%s' % (ref(1, c), ref(1, c + len(VARS) - 1)))
    c += len(VARS)
for lid, lab, towns in (('SS3', 'Mean of 3 towns', SS3),):
    for j, (v, vl) in enumerate(VARS):
        mon.set(1, c + j, lab, H)
        mon.set(2, c + j, vl, H)
        MCOL[(lid, v)] = c + j
    mon.merges.append('%s:%s' % (ref(1, c), ref(1, c + len(VARS) - 1)))
    c += len(VARS)
M0 = 3
MROW = {}
MV = {}  # cached monthly values
for i, (y, m) in enumerate(months):
    r = M0 + i
    key = '%d-%02d' % (y, m)
    MROW[key] = r
    first = datetime.date(y, m, 1)
    last = (datetime.date(y + (m == 12), m % 12 + 1, 1) - datetime.timedelta(days=1))
    dd = [d for d in dates if d.year == y and d.month == m]
    S = season_of(y, m)
    ph = season_phase(S)
    mon.set(r, 1, key, C)
    mon.set(r, 2, y, C)
    mon.set(r, 3, m, C)
    mon.set(r, 4, MNAME[m - 1], C)
    mon.set(r, 5, slabel(S), C)
    mon.set(r, 6, CAL.index(m) + 1, C)
    mon.set(r, 7, first, DATE)
    mon.set(r, 8, last, DATE)
    mon.set(r, 9, (last - first).days + 1, C, 'H{0}-G{0}+1'.format(r))
    mon.set(r, 10, len(dd), C, 'COUNTIF(Daily!$B${1}:$B${2},A{0})'.format(r, D0, D1))
    comp = 'complete' if len(dd) == (last - first).days + 1 else 'partial (%d days)' % len(dd)
    mon.set(r, 11, comp, C if comp == 'complete' else Style(bold=True, color='C00000', halign='center'), 'IF(J{0}=I{0},"complete","partial ("&J{0}&" days)")'.format(r))
    if key in ONI:
        mon.set(r, 12, ONI[key][0], N2, 'INDEX(ENSO_monthly!$F:$F,MATCH(A{0},ENSO_monthly!$A:$A,0))'.format(r))
        mon.set(r, 13, ONI[key][1], C, 'INDEX(ENSO_monthly!$D:$D,MATCH(A{0},ENSO_monthly!$A:$A,0))'.format(r))
        e = ONI[key][2]
        mon.set(r, 14, e, phs(e) if e != '—' else C, 'INDEX(ENSO_monthly!$L:$L,MATCH(A{0},ENSO_monthly!$A:$A,0))'.format(r))
    else:
        mon.set(r, 12, 'not published yet', C)
        mon.set(r, 13, '', C)
        mon.set(r, 14, 'not published yet', C)
    mon.set(r, 15, ph, phs(ph, bold=True), 'INDEX(ENSO_seasons!$U:$U,MATCH(E{0},ENSO_seasons!$A:$A,0))'.format(r))
    for t, _, _ in TOWNS:
        for v, _ in VARS:
            xs = [DAY[t][v][d.strftime('%Y%m%d')] for d in dd]
            dc = col_letter(DCOL[(t, v)])
            rng = 'Daily!${0}${1}:${0}${2}'.format(dc, D0, D1)
            crit = 'Daily!$B${0}:$B${1},$A{2}'.format(D0, D1, r)
            if v == 'RAIN_CPC' and t in REPL_FROM and (y, m) >= REPL_FROM[t] and (y, m) in GPC[t] and comp == 'complete':
                raw_ = round(sum(xs), 6)
                val = GPC[t][(y, m)] * KCP[t][m]
                REPLACED[(t, key)] = (raw_, GPC[t][(y, m)], KCP[t][m], val)
                mon.set(r, MCOL[(t, v)], val, REPLS)
            elif v in RAIN:
                val = round(sum(xs), 6)
                mon.set(r, MCOL[(t, v)], val, N1, 'SUMIFS(%s,%s)' % (rng, crit))
            else:
                val = sum(xs) / len(xs)
                mon.set(r, MCOL[(t, v)], val, N2, 'AVERAGEIFS(%s,%s)' % (rng, crit))
            MV[(t, v, key)] = val
    for lid, towns in (('SS3', SS3),):
        for v, _ in VARS:
            val = sum(MV[(t, v, key)] for t in towns) / len(towns)
            MV[(lid, v, key)] = val
            mon.set(r, MCOL[(lid, v)], val, N1 if v in RAIN else N2, 'AVERAGE(%s)' % ','.join(ref(r, MCOL[(t, v)]) for t in towns))
    MV[('complete', key)] = comp == 'complete'
PARTIAL = [k for k in MROW if not MV[('complete', k)]]
mon.set(M0 + len(months) + 1, 1, 'Rain = sum of daily CPC gauge rainfall (mm); NASA rain shown for reference only. Temperatures = mean of daily NASA T2M, T2M_MAX, T2M_MIN (°C). Mean of 3 towns = simple average. '
        'Partial month(s) %s (data end %s) are left out of the chart sheets.' % (', '.join(PARTIAL) or 'none', END), SUB)
mon.widths = {1: 9, 2: 6, 3: 6, 4: 6, 5: 9, 6: 9, 7: 11, 8: 11, 9: 7, 10: 7, 11: 11, 12: 11, 13: 7, 14: 16, 15: 12, **{cc: 9 for cc in range(16, c)}}
mon.freeze = (3, 2)

# ---------------- chart sheets ----------------
def loc_col(lid, v):
    return col_letter(MCOL[(lid, v)])


def chart_sheet(sh, lid, title):
    sh.set(1, 1, '%s | Temperature and rainfall by ENSO season' % title, TITLE)
    sh.set(2, 1, 'Rain: NOAA CPC gauge analysis (daily, 0.5°). Temperature: NASA POWER daily (grid cell of each town). July–June seasons 2005/06–2024/25 as in the São Mateus chart. '
              'Season phase = official NOAA ENSO episode at its Nov–Jan peak (sheet ENSO_seasons). Average rows = mean of the seasons of that phase in the photo window.', SUB)
    sh.set(3, 1, 'Seasons after the photo window are listed below each block, outside the averages. 2026/27: complete months only (data end %s).' % END, SUB)
    row = 5
    out = {}
    for v, lab, fmt, agg in (('T2M', 'Mean temperature (°C) — monthly mean of daily T2M', '0.00', 'Season mean'),
                              ('RAIN_CPC', 'Monthly rainfall (mm) — sum of daily rainfall from rain gauges (NOAA CPC)', '0.0', 'Season total')):
        sh.set(row, 1, lab, Style(bold=True, size=12, color='1F3864'))
        row += 1
        sh.row(row, 1, ['Season', 'Phase'] + MONTHS + [agg], H)
        row += 1
        vc = loc_col(lid, v)
        for ph in ('El Niño', 'La Niña', 'Neutral'):
            ss = [Y for Y in PHOTO if season_phase(Y) == ph]
            sh.set(row, 1, '%s (%d seasons)' % (ph, len(ss)), phs(ph, bold=True))
            row += 1
            r_first = row
            for Y in ss:
                sh.set(row, 1, slabel(Y), phs(ph))
                sh.set(row, 2, ph, phs(ph))
                vals = []
                for i, m in enumerate(CAL):
                    key = '%d-%02d' % (Y + (1 if m < 7 else 0), m)
                    val = MV[(lid, v, key)]
                    vals.append(val)
                    sh.set(row, 3 + i, val, Style(fmt=fmt), 'INDEX(Monthly!$%s:$%s,MATCH("%s",Monthly!$A:$A,0))' % (vc, vc, key))
                    out.setdefault((lid, v), {})[(Y, i)] = val
                a = sum(vals) / 12 if v == 'T2M' else sum(vals)
                sh.set(row, 15, a, Style(fmt=fmt, bold=True), ('AVERAGE(C{0}:N{0})' if v == 'T2M' else 'SUM(C{0}:N{0})').format(row))
                row += 1
            r_last = row - 1
            sh.set(row, 1, 'Average %s' % ph, phs(ph, bold=True))
            sh.set(row, 2, '%d seasons' % len(ss), phs(ph, bold=True))
            av = []
            for i in range(12):
                val = st.mean(out[(lid, v)][(Y, i)] for Y in ss)
                av.append(val)
                cl = col_letter(3 + i)
                sh.set(row, 3 + i, val, phs(ph, fmt, True), 'AVERAGE(%s%d:%s%d)' % (cl, r_first, cl, r_last))
            sh.set(row, 15, st.mean(av) if v == 'T2M' else sum(av), phs(ph, fmt, True), ('AVERAGE(C{0}:N{0})' if v == 'T2M' else 'SUM(C{0}:N{0})').format(row))
            row += 2
        sh.set(row, 1, 'After the photo window (not in the averages)', B)
        row += 1
        for Y in EXTRA:
            ph = season_phase(Y)
            sh.set(row, 1, slabel(Y), phs(ph))
            sh.set(row, 2, ph + (' (in progress)' if Y == 2026 else ''), phs(ph))
            vals = []
            for i, m in enumerate(CAL):
                key = '%d-%02d' % (Y + (1 if m < 7 else 0), m)
                if key in MROW and MV[('complete', key)]:
                    val = MV[(lid, v, key)]
                    vals.append(val)
                    sh.set(row, 3 + i, val, Style(fmt=fmt), 'INDEX(Monthly!$%s:$%s,MATCH("%s",Monthly!$A:$A,0))' % (vc, vc, key))
            if len(vals) == 12:
                sh.set(row, 15, sum(vals) / 12 if v == 'T2M' else sum(vals), Style(fmt=fmt, bold=True), ('AVERAGE(C{0}:N{0})' if v == 'T2M' else 'SUM(C{0}:N{0})').format(row))
            row += 1
        row += 2
    sh.widths = {1: 30, 2: 18, **{cc: 8 for cc in range(3, 15)}, 15: 11}
    sh.freeze = (5, 3)


for lid, sname, title in LOCS:
    chart_sheet(charts[lid], lid, title)

# ---------------- Chart_long ----------------
clong.row(1, 1, ['Location', 'Season', 'Phase', 'In photo window', 'Month', 'Month order (Jul = 1)', 'Calendar year', 'Month key', 'Mean temperature (°C)', 'Rainfall (mm)'], H)
r = 2
for lid, sname, title in LOCS:
    for Y in PHOTO + EXTRA:
        ph = season_phase(Y)
        for i, m in enumerate(CAL):
            yy = Y + (1 if m < 7 else 0)
            key = '%d-%02d' % (yy, m)
            if key not in MROW or not MV[('complete', key)]:
                continue
            clong.row(r, 1, [title, slabel(Y), ph + (' (in progress)' if Y == 2026 else ''), 'yes' if Y in PHOTO else 'no', MONTHS[i], i + 1, yy, key])
            tc, rc = loc_col(lid, 'T2M'), loc_col(lid, 'RAIN_CPC')
            clong.set(r, 9, MV[(lid, 'T2M', key)], N2, 'INDEX(Monthly!$%s:$%s,MATCH(H%d,Monthly!$A:$A,0))' % (tc, tc, r))
            clong.set(r, 10, MV[(lid, 'RAIN_CPC', key)], N1, 'INDEX(Monthly!$%s:$%s,MATCH(H%d,Monthly!$A:$A,0))' % (rc, rc, r))
            r += 1
CL_LAST = r - 1
clong.widths = {1: 44, 2: 9, 3: 20, 4: 10, 5: 7, 6: 10, 7: 9, 8: 9, 9: 12, 10: 11}
clong.freeze = (2, 1)

# ---------------- independent check against the monthly file used in the reports ----------------
def pearson(a, b):
    ma, mb = st.mean(a), st.mean(b)
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))


def monthly_sum(src, t):
    acc = collections.defaultdict(list)
    for k, v in DAY[t][src].items():
        if k >= '20050101':
            acc[(int(k[:4]), int(k[4:6]))].append(v)
    return {k: sum(v) for k, v in acc.items() if len(v) >= 28}


GPC = collections.defaultdict(dict)
for row in csv.DictReader(open(RAW + 'rain_check/gpcc_1981_2026_monthly.csv')):
    GPC[row['town']][(int(row['year']), int(row['month']))] = float(row['rain_mm'])


def rain_cmp(a, b, y0, y1):
    ks = sorted(k for k in a if k in b and y0 <= k[0] <= y1)
    xa, xb = [a[k] for k in ks], [b[k] for k in ks]
    return sum(xa) / sum(xb), pearson(xa, xb), len(ks)


RC = {}
for t, nm, _ in TOWNS:
    cpc, nas = monthly_sum('RAIN_CPC', t), monthly_sum('PRECTOTCORR', t)
    for lab, (x, yv) in (('CPC ÷ GPCC', (cpc, GPC[t])), ('NASA ÷ GPCC', (nas, GPC[t])), ('NASA ÷ CPC', (nas, cpc))):
        RC[(t, lab)] = (rain_cmp(x, yv, 2005, 2019), rain_cmp(x, yv, 2020, 2026))
GH = collections.defaultdict(dict)
for row in csv.DictReader(open(RAW + 'independent/ghcncams_tmean_monthly.csv')):
    if row['tmean_c']:
        GH[row['town']][(int(row['year']), int(row['month']))] = float(row['tmean_c'])
CT = collections.defaultdict(lambda: collections.defaultdict(list))
for fn, var in (('cpc_tmax_daily.csv', 'tmax_c'), ('cpc_tmin_daily.csv', 'tmin_c')):
    for row in csv.DictReader(open(RAW + 'independent/' + fn)):
        if row[var]:
            CT[(row['town'], var)][(int(row['date'][:4]), int(row['date'][5:7]))].append(float(row[var]))
TANN = {}
for y in range(2005, 2026):
    nas = st.mean(st.mean(v for k, v in DAY[t]['T2M'].items() if k.startswith(str(y))) for t in SS3)
    gh = st.mean(st.mean(GH[t][(y, m)] for m in range(1, 13)) for t in SS3)
    cp = st.mean(st.mean((st.mean(CT[(t, 'tmax_c')][(y, m)]) + st.mean(CT[(t, 'tmin_c')][(y, m)])) / 2 for m in range(1, 13)) for t in SS3)
    TANN[y] = (nas, gh, cp)


# ---------------- Rain anomaly ----------------
ano = wb.add('Rain_anomaly')
PCTS = Style(fmt='0%', halign='center')
PCTB = Style(fmt='0%', halign='center', bold=True, fill='BDD7EE')
PCTR = Style(fmt='0%', halign='center', bold=True, fill='F8CBAD')
INP = Style(fmt='0%', halign='center', color='0000FF')
ano.set(1, 1, 'Rain as % of normal (CPC gauges): the wet and dry years that the ENSO-season charts do not show', TITLE)
ano.set(2, 1, 'Normal = average of the same calendar month over 2005–2019 (Jan–Jun: 2006–2019, as the file starts in July 2005). 100 % = normal, 200 % = twice the normal. '
              'The ENSO-season charts compare La Niña seasons with other La Niña seasons; La Niña is wet in Honduras, so a very wet La Niña year does not stand out there.', SUB)
LOCN = [(t, nm) for t, nm, _ in TOWNS] + [('SS3', 'Mean of 3 towns')]
MSET = set(months)
# normals (needed by the two tables below)
NR0 = 30
ano.set(NR0 - 1, 1, 'Monthly normals, mm (average 2005–2019 of the Monthly sheet)', B)
ano.row(NR0, 1, ['Month', 'Month no.'] + [nm for _, nm in LOCN], H)
NORM = {}
for m in range(1, 13):
    r = NR0 + m
    ano.set(r, 1, MNAME[m - 1], B)
    ano.set(r, 2, m, C)
    for j, (lid, _) in enumerate(LOCN):
        mc = col_letter(MCOL[(lid, 'RAIN_CPC')])
        vals = [MV[(lid, 'RAIN_CPC', '%d-%02d' % (y, m))] for y in range(2005, 2020) if (y, m) in MSET]
        NORM[(lid, m)] = sum(vals) / len(vals)
        ano.set(r, 3 + j, NORM[(lid, m)], N1, 'AVERAGEIFS(Monthly!$%s:$%s,Monthly!$C:$C,$B%d,Monthly!$B:$B,">=2005",Monthly!$B:$B,"<=2019")' % (mc, mc, r))
r = NR0 + 13
ano.set(r, 1, 'Year', B)
for j, (lid, _) in enumerate(LOCN):
    cl = col_letter(3 + j)
    ano.set(r, 3 + j, sum(NORM[(lid, m)] for m in range(1, 13)), N0, 'SUM(%s%d:%s%d)' % (cl, NR0 + 1, cl, NR0 + 12))
NYEAR = r
# annual table
AR0 = 4
ano.set(AR0 - 1, 1, 'Calendar year: rain as % of normal. CPC = gauge grid 0.5° used in this file; GPCC = independent gauge analysis 1° (blue, for comparison, normal 2005–2019 of GPCC itself)', B)
hdr = ['Year', 'ENSO phase of the season starting in July']
for _, nm in LOCN:
    hdr += [nm + ' rain (mm)', nm + ' % of normal (CPC)']
hdr += [nm + ' % of normal (GPCC)' for _, nm in LOCN[:3]]
ano.row(AR0, 1, hdr, H)
GN = {t: {m: st.mean(GPC[t][(y, m)] for y in range(2005, 2020)) for m in range(1, 13)} for t in SS3}
YRS = [y for y in range(2006, END.year) if all((y, m) in MSET for m in range(1, 13))]
for i, y in enumerate(YRS):
    r = AR0 + 1 + i
    ano.set(r, 1, y, C)
    ph = season_phase(y) if y in PHOTO + EXTRA else ''
    ano.set(r, 2, ph, phs(ph) if ph else C)
    for j, (lid, _) in enumerate(LOCN):
        mc = col_letter(MCOL[(lid, 'RAIN_CPC')])
        tot = sum(MV[(lid, 'RAIN_CPC', '%d-%02d' % (y, m))] for m in range(1, 13))
        ano.set(r, 3 + 2 * j, tot, N0, 'SUMIFS(Monthly!$%s:$%s,Monthly!$B:$B,$A%d)' % (mc, mc, r))
        p_ = tot / sum(NORM[(lid, m)] for m in range(1, 13))
        ano.set(r, 4 + 2 * j, p_, PCTB if p_ >= 1.2 else PCTR if p_ <= 0.8 else PCTS, '%s%d/%s$%d' % (col_letter(3 + 2 * j), r, col_letter(3 + j), NYEAR))
    for j, t in enumerate(SS3):
        g = sum(GPC[t][(y, m)] for m in range(1, 13)) / sum(GN[t].values())
        ano.set(r, 3 + 2 * len(LOCN) + j, g, INP)
AEND = AR0 + len(YRS)
ano.set(AEND + 1, 1, 'Blue fill = at least 120 % of normal; red fill = 80 % or less. 2010 and 2011 are the wet years before the 2012–13 rust epidemic (La Niña).', SUB)
# monthly table
MR0 = NYEAR + 4
ano.set(MR0 - 1, 1, 'Month by month: rain, normal and % of normal', B)
hdr = ['Month key', 'Coffee season', 'Phase of the season']
for _, nm in LOCN:
    hdr += [nm + ' rain (mm)', nm + ' normal (mm)', nm + ' % of normal']
ano.row(MR0, 1, hdr, H)
for i, (y, m) in enumerate(months):
    r = MR0 + 1 + i
    key = '%d-%02d' % (y, m)
    ano.set(r, 1, key, C)
    ano.set(r, 2, slabel(season_of(y, m)), C)
    ph = season_phase(season_of(y, m)) if season_of(y, m) in PHOTO + EXTRA else ''
    ano.set(r, 3, ph, phs(ph) if ph else C)
    for j, (lid, _) in enumerate(LOCN):
        mc = col_letter(MCOL[(lid, 'RAIN_CPC')])
        c0 = 4 + 3 * j
        v = MV[(lid, 'RAIN_CPC', key)]
        n_ = NORM[(lid, m)]
        ano.set(r, c0, v, N1, 'INDEX(Monthly!$%s:$%s,MATCH($A%d,Monthly!$A:$A,0))' % (mc, mc, r))
        ano.set(r, c0 + 1, n_, N1, 'INDEX(%s$%d:%s$%d,%d)' % (col_letter(3 + j), NR0 + 1, col_letter(3 + j), NR0 + 12, m))
        p_ = v / n_ if n_ else 0
        ano.set(r, c0 + 2, p_, PCTB if p_ >= 1.5 else PCTR if p_ <= 0.5 else PCTS, 'IF(%s%d>0,%s%d/%s%d,0)' % (col_letter(c0 + 1), r, col_letter(c0), r, col_letter(c0 + 1), r))
ano.widths = {1: 11, 2: 22, 3: 12, **{c: 11 for c in range(4, 4 + 3 * len(LOCN) + 3)}}
ano.freeze = (MR0 + 1, 2)

# ---------------- Checks ----------------
chk.row(1, 1, ['Check', 'Result', 'Expected', 'OK?', 'How'], H)
rows = []
ndays = len(dates)
rows.append(('Days in the Daily sheet', ndays, 'COUNT(Daily!$A$%d:$A$%d)' % (D0, D1), ndays, 'Every day from %s to %s, no gap' % (START, END)))
rows.append(('Missing values (NASA fill value −999) in Daily', 0, 'COUNTIF(Daily!$D$%d:$%s$%d,-999)' % (D0, col_letter(3 + NT * len(VARS)), D1), 0, 'All 3 towns × 5 variables'))
rows.append(('Empty cells in Daily data', 0, 'COUNTBLANK(Daily!$D$%d:$%s$%d)' % (D0, col_letter(3 + NT * len(VARS)), D1), 0, ''))
ncomp = sum(1 for (y, m) in months if MV[('complete', '%d-%02d' % (y, m))])
rows.append(('Complete months in Monthly', ncomp, 'COUNTIF(Monthly!$K$%d:$K$%d,"complete")' % (M0, M0 + len(months) - 1), len(months) - len(PARTIAL), 'Partial: %s (data end %s)' % (', '.join(PARTIAL) or 'none', END)))
for t, nm, _ in TOWNS:
    rc, dc = col_letter(MCOL[(t, 'RAIN_CPC')]), col_letter(DCOL[(t, 'RAIN_CPC')])
    tot = sum(MV[(t, 'RAIN_CPC', '%d-%02d' % k)] for k in months)
    if t in REPL_FROM:
        ry, rm = REPL_FROM[t]
        ml = months.index((ry - 1, 12) if rm == 1 else (ry, rm - 1))
        dl = dates.index(datetime.date(ry, rm, 1)) - 1
        rows.append(('Rain %s: sum of monthly − sum of daily (mm), up to %d-%02d' % (nm, *months[ml]), 0.0,
                     'ROUND(SUM(Monthly!$%s$%d:$%s$%d)-SUM(Daily!$%s$%d:$%s$%d),6)' % (rc, M0, rc, M0 + ml, dc, D0, dc, D0 + dl), 0.0,
                     'From %d-%02d Copán rain is the adjusted GPCC value (CPC gauge lost), see "Rain breaks" below' % (ry, rm)))
        continue
    rows.append(('Rain %s: sum of monthly − sum of daily (mm)' % nm, 0.0,
                 'ROUND(SUM(Monthly!$%s$%d:$%s$%d)-SUM(Daily!$%s$%d:$%s$%d),6)' % (rc, M0, rc, M0 + len(months) - 1, dc, D0, dc, D1), 0.0, 'Monthly totals add up to the daily data'))
for ph, n in (('El Niño', 7), ('La Niña', 9), ('Neutral', 4)):
    got = sum(1 for Y in PHOTO if season_phase(Y) == ph)
    rows.append(('%s seasons in 2005/06–2024/25' % ph, got, 'COUNTIFS(ENSO_seasons!$W:$W,"yes",ENSO_seasons!$U:$U,"%s")' % ph, n, 'Same count as the São Mateus chart (7 / 9 / 4)'))

r = 2
for name, val, f, exp, how in rows:
    chk.set(r, 1, name)
    chk.set(r, 2, val, None, f)
    if exp is not None:
        chk.set(r, 3, exp)
        chk.set(r, 4, 'OK' if abs(val - exp) < 1e-6 else 'CHECK', Style(bold=True, color='3A8D5B' if abs(val - exp) < 1e-6 else 'C00000'), 'IF(ABS(B{0}-C{0})<0.000001,"OK","CHECK")'.format(r))
    chk.set(r, 5, how)
    r += 1
r += 1
chk.set(r, 1, 'Independent checks (computed outside the workbook)', B)
r += 1
static = [('All formulas recomputed by a separate script (verify_xlsx.py, research/indonesia/excel)', '0 differences with the stored values',
           'Proves each formula points to the right month, town and variable'),
          ('Missing CPC rain days filled with the NASA value of that day', '%d cells (%s)' % (len(CPC_FILLED), ', '.join(sorted(set(k for _, k in CPC_FILLED)))),
           'Fill value in the CPC source file; NASA rain agrees with the gauges before 2020'),
          ('Temperature level', 'NASA values are for the grid cell mean elevation (%s)' % ', '.join('%s cell %.0f m' % (nm, GEO[t][2]) for t, nm, _ in TOWNS),
           'A town below its cell is warmer than shown; month-to-month and year-to-year changes are more reliable than levels')]
for a, b_, c_ in static:
    chk.set(r, 1, a, WRAP)
    chk.set(r, 2, b_, WRAP)
    chk.set(r, 5, c_, WRAP)
    r += 1
r += 1
chk.set(r, 1, 'Why rain comes from rain gauges (NOAA CPC) and not from NASA: monthly totals compared, total ratio and correlation', B)
r += 1
chk.row(r, 1, ['Town, comparison', '2005–2019 ratio', '2005–2019 r', '2020–2026 ratio', '2020–2026 r'], H)
r += 1
for t, nm, _ in TOWNS:
    for lab in ('CPC ÷ GPCC', 'NASA ÷ GPCC', 'NASA ÷ CPC'):
        (r1, c1, n1), (r2, c2, n2) = RC[(t, lab)]
        bad = lab.startswith('NASA') and r2 > 1.15
        chk.row(r, 1, ['%s, %s' % (nm, lab), round(r1, 2), round(c1, 2), round(r2, 2), round(c2, 2)], RED if bad else None)
        r += 1
chk.set(r, 1, 'GPCC = gauge analysis, 1° (Full v2020 to 2019, Monitoring after; First Guess for 2026). CPC = gauge analysis, 0.5°, daily. Two independent gauge products agree with each other in both periods; NASA agrees with them until 2019, then reads 30–40 % wetter with a weaker correlation. NASA POWER appends GEOS-IT to MERRA-2 for recent data.', WRAP)
r += 2
chk.set(r, 1, 'Why temperature stays NASA: annual mean of the 3 towns (°C) in three products', B)
r += 1
chk.row(r, 1, ['Year', 'NASA T2M (used)', 'GHCN_CAMS stations', 'CPC stations (Tmax+Tmin)/2', 'ONI Nov–Jan'], H)
r += 1
for y in range(2005, 2026):
    k = '%d-12' % y
    chk.row(r, 1, [y, round(TANN[y][0], 2), round(TANN[y][1], 2), round(TANN[y][2], 2), round(ONI[k][0], 2) if k in ONI else ''])
    r += 1
chk.set(r, 1, 'GHCN_CAMS drops 0.8 °C in one step in 2014 and stays low while the region warms; CPC rises 2 °C in ten years. Both follow changes in the few stations of western Honduras. '
        'NASA shows cool La Niña years (2008, 2011–2012, 2021–2022) and warm El Niño years (2015, 2019, 2023–2024): it is the most consistent of the three. '
        'Caution: from March 2025, NASA temperatures step down against the station grids (seen in all 5 Indonesian towns too, about −0.4 °C there), so 2025/26 and 2026/27 may read cool.', WRAP)
r += 1
r += 2
chk.set(r, 1, 'Rain breaks found in the September 2026 review: each product as % of its own 2005–2019 normal (same months)', B)
r += 1
chk.row(r, 1, ['Town, year', 'CPC (raw)', 'GPCC', 'NASA', 'Reading'], H)
r += 1
def _msum(dct, t, y, m):
    return sum(v for k, v in dct.items() if k.startswith('%d%02d' % (y, m)) and v >= 0)
for t, nm, _ in TOWNS:
    cpcm = {(y, m): _msum(DAY[t]['RAIN_CPC'], t, y, m) for y in range(2005, 2027) for m in range(1, 13)}
    nasm = {(y, m): _msum(DAY[t]['PRECTOTCORR'], t, y, m) for y in range(2005, 2027) for m in range(1, 13)}
    for y in range(2018, END.year + 1):
        ms = [m for m in range(1, 13) if (y, m) in GPC[t] and (y, m) in MSET and MV[('complete', '%d-%02d' % (y, m))]]
        if not ms:
            continue
        def pc(D):
            return sum(D[(y, m)] for m in ms) / sum(st.mean(D[(yy, m)] for yy in range(2005, 2020)) for m in ms)
        c_, g_, n_ = pc(cpcm), pc(GPC[t]), pc(nasm)
        bad = c_ < 0.6 * g_ and c_ < 0.6 * n_
        note = 'CPC far below both others: gauge lost, replaced' if (t in REPL_FROM and (y, 1) >= REPL_FROM[t]) else ('CPC far below both others' if bad else '')
        if y == END.year:
            note = (note + '; ' if note else '') + '%d months' % len(ms)
        chk.row(r, 1, ['%s %d' % (nm, y), round(c_, 2), round(g_, 2), round(n_, 2), note], RED if bad else None)
        r += 1
r += 1
chk.set(r, 1, 'Copán months replaced (Monthly sheet, blue on yellow): value used = GPCC × (CPC ÷ GPCC of the same calendar month, 2005–2019)', B)
r += 1
chk.row(r, 1, ['Month', 'CPC raw (mm)', 'GPCC (mm)', 'Factor', 'Value used (mm)'], H)
r += 1
for (t, key), (raw_, g_, f_, v_) in sorted(REPLACED.items()):
    chk.row(r, 1, ['%s %s' % (t.capitalize(), key), round(raw_, 1), round(g_, 1), round(f_, 3), round(v_, 1)])
    r += 1
chk.set(r, 1, 'GPCC source by month: Full v2020 to 2019, Monitoring v2020 after, First Guess for 2026 (1° cell). Ocotepeque CPC also reads low in 2024 (0.81 of GPCC) and 2026, '
        'but stays inside its 2005–2023 range (0.78–1.33), so it is kept.', WRAP)
r += 2
c455 = DAY['comayagua']['RAIN_CPC'].get('20260406')
if c455 and c455 > 200:
    chk.set(r, 1, 'Suspect day: Comayagua 6 April 2026, CPC %.0f mm in one day (NASA %.0f mm the same day; GPCC first guess %.0f mm for the whole month). '
            'Kept as delivered by CPC; it only affects the 2025/26 season, which is outside the 20-season charts.' % (
                c455, DAY['comayagua']['PRECTOTCORR']['20260406'], GPC['comayagua'].get((2026, 4), float('nan'))), RED)
    r += 1
chk.widths = {1: 58, 2: 38, 3: 12, 4: 14, 5: 60}

# ---------------- README ----------------
MR = {lab: (st.mean(RC[(t, lab)][0][0] for t in SS3), st.mean(RC[(t, lab)][1][0] for t in SS3)) for lab in ('CPC ÷ GPCC', 'NASA ÷ GPCC', 'NASA ÷ CPC')}
lines = [
    ('Météo des zones caféières du Honduras (Comayagua, Ocotepeque, Copán) par saison ENSO (juillet–juin), pour refaire les graphiques du type « São Mateus »', TITLE),
    ('Même méthode, mêmes saisons, mêmes mois et même classement El Niño / La Niña que le fichier du Sumatra du Sud. Données météo jusqu\'au %s, ONI jusqu\'à JJA 2026.' % END, SUB),
    ('', None),
    ('CE QUE CONTIENT LE FICHIER', B),
    ('Chart_Mean_3 : moyenne des 3 lieux (Comayagua, Ocotepeque, Copán). Chart_Comayagua, Chart_Ocotepeque, Chart_Copan : la même chose lieu par lieu.', WRAP),
    ('Dans chaque feuille Chart : bloc température moyenne (°C) puis bloc pluie mensuelle (mm). Lignes = saisons juillet–juin, colonnes = Jul … Jun, groupées El Niño / La Niña / Neutre, avec la ligne « Average » de chaque groupe (la ligne noire en pointillés du graphique).', WRAP),
    ('Chart_long : les mêmes chiffres en format long (une ligne par lieu × saison × mois), le plus simple pour ChatGPT ou un graphique croisé.', WRAP),
    ('ENSO_seasons et ENSO_monthly : exactement la même table ONI (NOAA CPC) et le même calcul que pour l\'Indonésie, donc les mêmes saisons El Niño / La Niña / Neutre.', WRAP),
    ('Monthly : les valeurs mensuelles, calculées par formule à partir de Daily. Daily : les données jour par jour, 3 lieux × 5 variables (pluie des pluviomètres, 3 températures, pluie NASA pour comparaison), 1er juillet 2005 → %s.' % END, WRAP),
    ('Checks : les contrôles (jours manquants, totaux, nombre de saisons par phase), et pourquoi la pluie vient des pluviomètres et la température de la NASA.', WRAP),
    ('Rain_anomaly : pluie en % de la normale (moyenne 2005–2019 du même mois), par année civile et par mois, pour les 3 villes et leur moyenne, avec GPCC en comparaison. C\'est là qu\'on voit les années humides 2008, 2010 et 2011 (La Niña) avant la rouille de 2012–2013 : les graphiques par phase ENSO comparent des années La Niña entre elles et ne les font pas ressortir.', WRAP),
    ('CORRECTION (septembre 2026) : à Copán, la maille CPC perd son pluviomètre en janvier 2024 (49 % puis 41 % de la normale en 2024 et 2025, alors que GPCC donne 92 % et 103 %). De janvier 2024 à août 2026, la pluie de Copán est donc la valeur GPCC ajustée au niveau CPC (cellules bleues sur fond jaune dans Monthly, détail dans Checks). La feuille Daily garde les valeurs CPC brutes.', Style(wrap=True, bold=True, color='C00000')),
    ('', None),
    ('LES SAISONS : LES MÊMES QUE TA PHOTO ET QUE LE FICHIER INDONÉSIE', B),
    ('20 saisons, 2005/06 à 2024/25 : 7 El Niño, 9 La Niña, 4 neutres (règle officielle NOAA).', WRAP),
    ('El Niño : ' + ', '.join(slabel(Y) for Y in PHOTO if season_phase(Y) == 'El Niño'), phs('El Niño', bold=True)),
    ('La Niña : ' + ', '.join(slabel(Y) for Y in PHOTO if season_phase(Y) == 'La Niña'), phs('La Niña', bold=True)),
    ('Neutre : ' + ', '.join(slabel(Y) for Y in PHOTO if season_phase(Y) == 'Neutral'), phs('Neutral', bold=True)),
    ('En plus, hors moyennes : 2025/26 (neutre) et 2026/27 (El Niño en cours, mois complets seulement).', WRAP),
    ('Attention : au Honduras l\'année caféière USDA va d\'octobre à septembre et la floraison suit les premières pluies de mars–mai. Les saisons restent juillet–juin, comme demandé, pour être comparables à ta photo et au fichier Indonésie ; Chart_long permet d\'autres découpages.', Style(wrap=True, bold=True, color='C00000')),
    ('', None),
    ('COMMENT UNE SAISON EST CLASSÉE (règle NOAA CPC)', B),
    ('1. ONI = anomalie de température de surface de la mer dans la zone Niño 3.4, en moyenne sur 3 mois glissants (ex. NDJ = novembre–décembre–janvier). Source : NOAA CPC, oni.ascii.txt.', WRAP),
    ('2. Chaque période est chaude si l\'ONI arrondi à 0,1 °C est ≥ +0,5, froide s\'il est ≤ −0,5.', WRAP),
    ('3. Il y a épisode El Niño (La Niña) seulement si ce seuil tient au moins 5 périodes consécutives. Le calcul est fait par formules dans ENSO_monthly.', WRAP),
    ('4. Une saison juillet–juin prend la phase de l\'épisode en cours à son pic, la période NDJ (novembre–janvier).', WRAP),
    ('Cas limites expliqués dans ENSO_seasons : 2016/17, 2024/25 et 2025/26 sont neutres (le seuil La Niña n\'a pas tenu 5 périodes) ; 2026/27 est El Niño en cours.', WRAP),
    ('', None),
    ('LES DONNÉES MÉTÉO', B),
    ('PLUIE = pluviomètres, analyse quotidienne NOAA CPC (Global Unified Gauge-Based, 0,5°), maille la plus proche de chaque lieu. Pas la NASA : au Honduras, la pluie NASA suit les pluviomètres jusqu\'en 2019 (ratio %.2f), puis lit %.0f %% plus humide depuis 2020, avec une corrélation qui chute (détail dans Checks). Les deux produits de pluviomètres (CPC et GPCC) concordent entre eux sur toute la période.' % (MR['NASA ÷ GPCC'][0], 100 * (MR['NASA ÷ GPCC'][1] - 1)), Style(wrap=True, bold=True, color='C00000')),
    ('TEMPÉRATURE = NASA POWER (MERRA-2 puis GEOS-IT), T2M moyenne journalière, plus T2M_MAX et T2M_MIN. Les deux grilles de stations ont des ruptures au Honduras (GHCN_CAMS −0,8 °C en 2014, CPC +2 °C en dix ans) ; la NASA est la plus cohérente (années La Niña fraîches, El Niño chaudes). Attention : depuis mars 2025 la NASA baisse d\'environ 0,4 °C face aux stations (vu aussi en Indonésie), donc 2025/26 et 2026/27 peuvent lire trop frais.', WRAP),
    ('Points utilisés (latitude, longitude, altitude de la maille NASA) : ' + ' ; '.join('%s %.3f, %.3f, %.0f m' % (nm, GEO[t][1], GEO[t][0], GEO[t][2]) for t, nm, _ in TOWNS) + '. Copán = Santa Rosa de Copán, chef-lieu du département.', WRAP),
    ('Mois = somme (pluie) ou moyenne (température) des jours du mois civil. Seuls les mois complets entrent dans les graphiques.', WRAP),
    ('Contrôle de la pluie retenue : CPC ÷ GPCC = %.2f en 2005–2019 et %.2f en 2020–2026 (moyenne des 3 lieux) : pas de rupture.' % MR['CPC ÷ GPCC'], WRAP),
    ('La température est celle de la maille NASA (altitude moyenne de la maille). Un lieu plus bas que sa maille est plus chaud en réalité ; les variations d\'un mois ou d\'une année à l\'autre sont fiables.', WRAP),
    ('', None),
    ('POUR REFAIRE LE GRAPHIQUE', B),
    ('Pour chaque phase (El Niño, La Niña, Neutre) : un graphique en lignes de la température (une ligne par saison, Jul → Jun) et un de la pluie, plus la ligne Average en noir pointillé. Les valeurs sont dans les feuilles Chart_…, ou dans Chart_long (filtre Location, Phase, In photo window = yes).', WRAP),
    ('Formules : toutes les feuilles de calcul se recalculent à l\'ouverture dans Excel ; les valeurs sont aussi enregistrées dans le fichier, donc lisibles sans recalcul (Python, ChatGPT).', WRAP),
]
for i, (t, s) in enumerate(lines, 1):
    readme.set(i, 1, t, s)
readme.widths = {1: 150}

wb.save(OUT)
print('saved', OUT)
print('photo seasons', {ph: [slabel(Y) for Y in PHOTO if season_phase(Y) == ph] for ph in ('El Niño', 'La Niña', 'Neutral')})
print('rain ratios', MR, 'filled', CPC_FILLED)
print('end', END, 'partial', PARTIAL, 'days', ndays, 'months', len(months), 'long rows', CL_LAST, 'grid', GEO)
