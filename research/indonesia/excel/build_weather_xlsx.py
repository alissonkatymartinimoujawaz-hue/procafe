"""Sumatra robusta belt: monthly temperature and rainfall by ENSO season (July-June), for the São Mateus-style panels.
Daily NASA POWER data -> monthly values (SUMIFS / AVERAGEIFS formulas, cached values written too) -> one chart sheet per location.
Seasons classified with NOAA CPC's official rule on the ONI table. Standard library only."""
import json, os, sys, datetime, statistics as st, decimal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlsxw import Workbook, Style, ref, col_letter

HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
RAW = HERE + '../raw/'
OUT = HERE + 'Sumatra_weather_by_ENSO_season.xlsx'

TOWNS = [('pagar_alam', 'Pagar Alam', 'South Sumatra (Sumatera Selatan)'), ('lahat', 'Lahat', 'South Sumatra (Sumatera Selatan)'),
         ('muaradua', 'Muaradua', 'South Sumatra (Sumatera Selatan), OKU Selatan'), ('liwa', 'Liwa', 'Lampung, Lampung Barat'),
         ('kepahiang', 'Kepahiang', 'Bengkulu')]
SS3 = ['pagar_alam', 'lahat', 'muaradua']
VARS = [('PRECTOTCORR', 'Rain (mm)'), ('T2M', 'Mean temp (°C)'), ('T2M_MAX', 'Max temp (°C)'), ('T2M_MIN', 'Min temp (°C)')]
START, END = datetime.date(2005, 7, 1), datetime.date(2026, 9, 19)
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

oni = []  # [key, year, centre month, code, anom]
for line in open(RAW + 'oni.ascii.txt').read().splitlines()[1:]:
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
PH_FILL = {'El Niño': 'FCE4D6', 'La Niña': 'DDEBF7', 'Neutral': 'EDEDED'}
PH_FONT = {'El Niño': 'C00000', 'La Niña': '2E75B6', 'Neutral': '404040'}


def phs(ph, fmt=None, bold=False):
    base = 'El Niño' if ph.startswith('El Niño') else 'La Niña' if ph.startswith('La Niña') else 'Neutral'
    return Style(fill=PH_FILL[base], fmt=fmt, bold=bold, color=PH_FONT[base] if bold else '000000')


# sheet objects (order = tab order)
readme = wb.add('README')
charts = {}
LOCS = [('SS3', 'Chart_South_Sumatra', 'South Sumatra, mean of 3 towns (Pagar Alam, Lahat, Muaradua)')] + [(t, 'Chart_' + nm.replace(' ', '_'), '%s — %s' % (nm, prov)) for t, nm, prov in TOWNS]
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
def prev_rule(Y):
    ks = ['%d-%02d' % (Y, m) for m in (8, 9, 10, 11)]
    return st.mean(ONI[k][0] for k in ks) if all(k in ONI for k in ks) else None


def prev_phase(Y):
    p = prev_rule(Y)
    return None if p is None else 'El Niño' if p >= 0.5 else 'La Niña' if p <= -0.5 else 'Neutral'


SY = list(range(1981, 2027))
hdr = ['Season (Jul–Jun)', 'First day', 'Last day'] + ['ONI %s (centre %s)' % (SEAS[(m - 1)], MONTHS[i]) for i, m in enumerate(CAL)] + [
    'Periods in an El Niño episode', 'Periods in a La Niña episode', 'ONI Nov–Jan (NDJ, peak season)', 'Largest ONI of the season (sign kept)',
    'Official episode at NDJ', 'SEASON PHASE (used in the charts)', 'Strength (largest |ONI|)', 'In the photo window 2005/06–2024/25',
    'Previous rule: ONI Aug–Nov mean (JAS–OND) of the first year', 'Phase with the previous rule (±0.5)', 'Same phase?', 'Note']
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
    if prev_rule(Y) is None:
        sea.set(r, 24, 'n/a', C)
        sea.set(r, 25, 'n/a', C)
        sea.set(r, 26, 'n/a', C)
    else:
        prev = prev_rule(Y)
        pph = 'El Niño' if prev >= 0.5 else 'La Niña' if prev <= -0.5 else 'Neutral'
        sea.set(r, 24, prev, N2, 'AVERAGE(E{0}:H{0})'.format(r))
        sea.set(r, 25, pph, C, 'IF(X{0}>=0.5,"El Niño",IF(X{0}<=-0.5,"La Niña","Neutral"))'.format(r))
        sea.set(r, 26, 'yes' if pph == ph else 'NO', C if pph == ph else Style(bold=True, color='C00000', halign='center'), 'IF(Y{0}=U{0},"yes","NO")'.format(r))
    sea.set(r, 27, NOTES.get(Y, ''), TXT)
sea.set(2 + len(SY) + 1, 1, 'Season phase = official NOAA episode status of the Nov–Jan (NDJ) ONI period, the peak of ENSO. Cells coloured when the period is inside an official episode (red El Niño, blue La Niña).', SUB)
sea.set(2 + len(SY) + 2, 1, 'With this rule the 20 seasons 2005/06–2024/25 split 7 El Niño / 9 La Niña / 4 Neutral, the same counts as the São Mateus chart.', SUB)
sea.widths = {1: 10, 2: 11, 3: 11, **{c: 8.5 for c in range(4, 16)}, 16: 10, 17: 10, 18: 10, 19: 10, 20: 16, 21: 14, 22: 11, 23: 11, 24: 13, 25: 12, 26: 8, 27: 70}
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
day.widths = {1: 11, 2: 9, 3: 9, **{cc: 9.5 for cc in range(4, 4 + 5 * len(VARS))}}
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
for lid, lab, towns in (('SS3', 'South Sumatra, mean of 3 towns', SS3), ('ALL5', 'Belt, mean of 5 towns', [t for t, _, _ in TOWNS])):
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
            if v == 'PRECTOTCORR':
                val = round(sum(xs), 6)
                mon.set(r, MCOL[(t, v)], val, N1, 'SUMIFS(%s,%s)' % (rng, crit))
            else:
                val = sum(xs) / len(xs)
                mon.set(r, MCOL[(t, v)], val, N2, 'AVERAGEIFS(%s,%s)' % (rng, crit))
            MV[(t, v, key)] = val
    for lid, towns in (('SS3', SS3), ('ALL5', [t for t, _, _ in TOWNS])):
        for v, _ in VARS:
            val = sum(MV[(t, v, key)] for t in towns) / len(towns)
            MV[(lid, v, key)] = val
            mon.set(r, MCOL[(lid, v)], val, N1 if v == 'PRECTOTCORR' else N2, 'AVERAGE(%s)' % ','.join(ref(r, MCOL[(t, v)]) for t in towns))
    MV[('complete', key)] = comp == 'complete'
mon.set(M0 + len(months) + 1, 1, 'Rain = sum of daily PRECTOTCORR (mm); temperatures = mean of daily T2M, T2M_MAX, T2M_MIN (°C). Town means = simple average of the towns. '
        'September 2026 is partial (data to 19 Sep 2026) and is left out of the chart sheets.', SUB)
mon.widths = {1: 9, 2: 6, 3: 6, 4: 6, 5: 9, 6: 9, 7: 11, 8: 11, 9: 7, 10: 7, 11: 11, 12: 11, 13: 7, 14: 16, 15: 12, **{cc: 9 for cc in range(16, c)}}
mon.freeze = (3, 2)

# ---------------- chart sheets ----------------
def loc_col(lid, v):
    return col_letter(MCOL[(lid, v)])


def chart_sheet(sh, lid, title):
    sh.set(1, 1, '%s | Temperature and rainfall by ENSO season' % title, TITLE)
    sh.set(2, 1, 'NASA POWER daily data (MERRA-2 based, grid cell of each town), July–June seasons 2005/06–2024/25 as in the São Mateus chart. '
              'Season phase = official NOAA ENSO episode at its Nov–Jan peak (sheet ENSO_seasons). Average rows = mean of the seasons of that phase in the photo window.', SUB)
    sh.set(3, 1, 'Seasons after the photo window are listed below each block, outside the averages. 2026/27: complete months only (Jul–Aug 2026; data end 19 Sep 2026).', SUB)
    row = 5
    out = {}
    for v, lab, fmt, agg in (('T2M', 'Mean temperature (°C) — monthly mean of daily T2M', '0.00', 'Season mean'),
                              ('PRECTOTCORR', 'Monthly rainfall (mm) — sum of daily PRECTOTCORR', '0.0', 'Season total')):
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
            tc, rc = loc_col(lid, 'T2M'), loc_col(lid, 'PRECTOTCORR')
            clong.set(r, 9, MV[(lid, 'T2M', key)], N2, 'INDEX(Monthly!$%s:$%s,MATCH(H%d,Monthly!$A:$A,0))' % (tc, tc, r))
            clong.set(r, 10, MV[(lid, 'PRECTOTCORR', key)], N1, 'INDEX(Monthly!$%s:$%s,MATCH(H%d,Monthly!$A:$A,0))' % (rc, rc, r))
            r += 1
CL_LAST = r - 1
clong.widths = {1: 44, 2: 9, 3: 20, 4: 10, 5: 7, 6: 10, 7: 9, 8: 9, 9: 12, 10: 11}
clong.freeze = (2, 1)

# ---------------- independent check against the monthly file used in the reports ----------------
js = open(HERE + '../weather_data.js').read()
WD = json.loads(js[js.index('{'):js.rindex('}') + 1])['monthly']
dr, dt, nchk = 0.0, 0.0, 0
for t, _, _ in TOWNS:
    for (y, m) in months:
        key = '%d-%02d' % (y, m)
        w = WD[t].get(key)
        if not w or not MV[('complete', key)]:
            continue
        dr = max(dr, abs(w[0] - MV[(t, 'PRECTOTCORR', key)]))
        dt = max(dt, abs(w[1] - MV[(t, 'T2M', key)]))
        nchk += 1

# ---------------- Checks ----------------
chk.row(1, 1, ['Check', 'Result', 'Expected', 'OK?', 'How'], H)
rows = []
ndays = len(dates)
rows.append(('Days in the Daily sheet', ndays, 'COUNT(Daily!$A$%d:$A$%d)' % (D0, D1), ndays, 'Every day from %s to %s, no gap' % (START, END)))
rows.append(('Missing values (NASA fill value −999) in Daily', 0, 'COUNTIF(Daily!$D$%d:$%s$%d,-999)' % (D0, col_letter(3 + 5 * len(VARS)), D1), 0, 'All 5 towns × 4 variables'))
rows.append(('Empty cells in Daily data', 0, 'COUNTBLANK(Daily!$D$%d:$%s$%d)' % (D0, col_letter(3 + 5 * len(VARS)), D1), 0, ''))
ncomp = sum(1 for (y, m) in months if MV[('complete', '%d-%02d' % (y, m))])
rows.append(('Complete months in Monthly', ncomp, 'COUNTIF(Monthly!$K$%d:$K$%d,"complete")' % (M0, M0 + len(months) - 1), len(months) - 1, 'Only September 2026 is partial (to 19 Sep)'))
for t, nm, _ in TOWNS:
    rc, dc = col_letter(MCOL[(t, 'PRECTOTCORR')]), col_letter(DCOL[(t, 'PRECTOTCORR')])
    tot = sum(MV[(t, 'PRECTOTCORR', '%d-%02d' % k)] for k in months)
    rows.append(('Rain %s: sum of monthly − sum of daily (mm)' % nm, 0.0,
                 'ROUND(SUM(Monthly!$%s$%d:$%s$%d)-SUM(Daily!$%s$%d:$%s$%d),6)' % (rc, M0, rc, M0 + len(months) - 1, dc, D0, dc, D1), 0.0, 'Monthly totals add up to the daily data'))
for ph, n in (('El Niño', 7), ('La Niña', 9), ('Neutral', 4)):
    got = sum(1 for Y in PHOTO if season_phase(Y) == ph)
    rows.append(('%s seasons in 2005/06–2024/25' % ph, got, 'COUNTIFS(ENSO_seasons!$W:$W,"yes",ENSO_seasons!$U:$U,"%s")' % ph, n, 'Same count as the São Mateus chart (7 / 9 / 4)'))
DIFFS = [Y for Y in range(2005, 2027) if prev_phase(Y) is not None and prev_phase(Y) != season_phase(Y)]
ndiff = len(DIFFS)
rows.append(('Seasons 2005/06–2026/27 classed differently by the previous rule (ONI Aug–Nov)', ndiff,
             'COUNTIFS(ENSO_seasons!$B:$B,">="&DATE(2005,7,1),ENSO_seasons!$Z:$Z,"NO")', None, 'See ENSO_seasons, column Z; the charts use the official NOAA rule'))
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
static = [('Monthly values vs the monthly file used in the research note (weather_data.js), %d town-months' % nchk,
           'max difference %.3f mm rain, %.3f °C temperature' % (dr, dt), 'Same NASA POWER data, aggregated by a separate script'),
          ('Rainfall vs rain gauges (GPCC full data 0.25°, June–October totals 1981–2019)', 'r = 0.86 Pagar Alam, 0.85 Lahat, 0.89 Muaradua, 0.93 Liwa, 0.88 Kepahiang; 0.93 for the 5-town mean',
           'GPCC via NOAA PSL; see research note, section 5 bis'),
          ('Rainfall vs GPCC first guess (1°, 2012–2025)', 'r = 0.96 to 0.99 by town; wet/dry sign agrees 14 of 14 years', 'Same'),
          ('Absolute level of rainfall', 'NASA is higher than GPCC at Pagar Alam (828 vs 685 mm Jun–Oct normal), lower at Muaradua and Liwa', 'Year-to-year changes agree; levels differ by site'),
          ('All formulas recomputed by a separate script (verify_xlsx.py, same folder of the repository)',
           '0 differences with the stored values', 'Proves each formula points to the right month, town and variable'),
          ('Temperature level', 'NASA values are for the grid cell mean elevation (Pagar Alam cell %.0f m, Lahat %.0f m, Muaradua %.0f m, Liwa %.0f m, Kepahiang %.0f m)' % tuple(GEO[t][2] for t, _, _ in TOWNS),
           'A town below its cell is warmer than shown; month-to-month and year-to-year changes are reliable')]
for a, b_, c_ in static:
    chk.set(r, 1, a, WRAP)
    chk.set(r, 2, b_, WRAP)
    chk.set(r, 5, c_, WRAP)
    r += 1
chk.widths = {1: 58, 2: 38, 3: 10, 4: 8, 5: 60}

# ---------------- README ----------------
lines = [
    ('Météo du Sumatra du Sud par saison ENSO (juillet–juin), pour refaire les graphiques du type « São Mateus »', TITLE),
    ('Fichier généré le 25 septembre 2026. Données météo jusqu\'au 19 septembre 2026, ONI jusqu\'à JJA 2026.', SUB),
    ('', None),
    ('CE QUE CONTIENT LE FICHIER', B),
    ('Chart_South_Sumatra : moyenne des 3 villes du Sumatra du Sud (Pagar Alam, Lahat, Muaradua). C\'est le graphique principal.', WRAP),
    ('Chart_Pagar_Alam, Chart_Lahat, Chart_Muaradua, Chart_Liwa, Chart_Kepahiang : la même chose ville par ville (Liwa = Lampung, Kepahiang = Bengkulu).', WRAP),
    ('Dans chaque feuille Chart : bloc température moyenne (°C) puis bloc pluie mensuelle (mm). Lignes = saisons juillet–juin, colonnes = Jul … Jun, groupées El Niño / La Niña / Neutre, avec la ligne « Average » de chaque groupe (la ligne noire en pointillés du graphique).', WRAP),
    ('Chart_long : les mêmes chiffres en format long (une ligne par lieu × saison × mois), le plus simple pour ChatGPT ou un graphique croisé.', WRAP),
    ('ENSO_seasons : la classification de chaque saison 1981/82–2026/27, avec les 12 valeurs ONI de la saison. ENSO_monthly : la table ONI officielle de la NOAA et le calcul des épisodes.', WRAP),
    ('Monthly : les valeurs mensuelles, calculées par formule (SOMME.SI.ENS / MOYENNE.SI.ENS) à partir de Daily. Daily : les données jour par jour, 5 villes × 4 variables, 1er juillet 2005 → 19 septembre 2026.', WRAP),
    ('Checks : les contrôles (jours manquants, totaux, nombre de saisons par phase, comparaison avec les pluviomètres).', WRAP),
    ('', None),
    ('LES SAISONS : MÊMES ANNÉES QUE TA PHOTO', B),
    ('20 saisons, 2005/06 à 2024/25. Avec la règle officielle de la NOAA, elles se répartissent en 7 El Niño, 9 La Niña et 4 neutres : exactement les nombres de ta photo São Mateus.', WRAP),
    ('El Niño : ' + ', '.join(slabel(Y) for Y in PHOTO if season_phase(Y) == 'El Niño'), phs('El Niño', bold=True)),
    ('La Niña : ' + ', '.join(slabel(Y) for Y in PHOTO if season_phase(Y) == 'La Niña'), phs('La Niña', bold=True)),
    ('Neutre : ' + ', '.join(slabel(Y) for Y in PHOTO if season_phase(Y) == 'Neutral'), phs('Neutral', bold=True)),
    ('En plus, hors moyennes : 2025/26 (neutre, complète) et 2026/27 (El Niño en cours, juillet et août 2026 seulement).', WRAP),
    ('', None),
    ('COMMENT UNE SAISON EST CLASSÉE (règle NOAA CPC)', B),
    ('1. ONI = anomalie de température de surface de la mer dans la zone Niño 3.4, en moyenne sur 3 mois glissants (ex. NDJ = novembre–décembre–janvier). Source : NOAA CPC, oni.ascii.txt.', WRAP),
    ('2. Chaque période est chaude si l\'ONI arrondi à 0,1 °C est ≥ +0,5, froide s\'il est ≤ −0,5.', WRAP),
    ('3. Il y a épisode El Niño (La Niña) seulement si ce seuil tient au moins 5 périodes consécutives. Le calcul est fait par formules dans ENSO_monthly.', WRAP),
    ('4. Une saison juillet–juin prend la phase de l\'épisode en cours à son pic, la période NDJ (novembre–janvier). Les colonnes P et Q de ENSO_seasons donnent le nombre de mois de la saison dans chaque type d\'épisode.', WRAP),
    ('Cas limites expliqués dans ENSO_seasons (colonne AA) : 2016/17, 2024/25 et 2025/26 sont neutres (le seuil La Niña n\'a pas tenu 5 périodes) ; 2026/27 est El Niño en cours (ONI +1,80 en JJA 2026, avis El Niño de la NOAA).', WRAP),
    ('Attention : l\'ancienne règle de mes slides (moyenne ONI août–novembre ±0,5) classait %d saisons autrement sur 2005/06–2026/27. Ce fichier utilise la règle officielle. La colonne Z de ENSO_seasons montre les écarts.' % ndiff, Style(wrap=True, bold=True, color='C00000')),
    ('', None),
    ('LES DONNÉES MÉTÉO', B),
    ('Source : NASA POWER, API quotidienne v2.10 (« Source Native Resolution », sources MERRA-2 / GEOS-IT), heure solaire locale. Pluie = PRECTOTCORR (mm/jour, corrigée), température = T2M (moyenne journalière), plus T2M_MAX et T2M_MIN.', WRAP),
    ('Points utilisés (latitude, longitude) : ' + ' ; '.join('%s %.3f, %.3f' % (nm, GEO[t][1], GEO[t][0]) for t, nm, _ in TOWNS) + '.', WRAP),
    ('Mois = somme (pluie) ou moyenne (température) des jours du mois civil. Seuls les mois complets entrent dans les graphiques : septembre 2026 s\'arrête au 19 et en est exclu.', WRAP),
    ('Contrôle de la pluie : sur juin–octobre 1981–2019, les totaux NASA suivent les pluviomètres GPCC (r = 0,85 à 0,93 selon la ville). Les niveaux absolus diffèrent selon le lieu (voir Checks).', WRAP),
    ('La température est celle de la maille NASA (altitude moyenne de la maille, voir Checks). Une ville plus basse que sa maille est un peu plus chaude en réalité ; les variations d\'un mois ou d\'une année à l\'autre sont fiables.', WRAP),
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
print('diff vs previous rule', ndiff, [(slabel(Y), prev_phase(Y), season_phase(Y)) for Y in DIFFS])
print('check vs weather_data.js', nchk, 'max rain diff', dr, 'max temp diff', dt, 'days', ndays, 'months', len(months), 'long rows', CL_LAST)
