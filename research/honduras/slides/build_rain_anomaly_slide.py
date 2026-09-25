"""Rain as % of normal before the 2012-13 rust: values read from the Rain_anomaly sheet of
excel/Honduras_weather_by_ENSO_season.xlsx (cached results of its formulas), so the slide and the workbook match."""
import re, zipfile
from deckkit import Page, save, fr, NAVY, BLUE, ORANGE, GREY, INK, LIGHT, HERE

XL = HERE + '../excel/Honduras_weather_by_ENSO_season.xlsx'


def read_sheet(path, name):
    z = zipfile.ZipFile(path)
    wbx = z.read('xl/workbook.xml').decode()
    rid = [r for n, r in re.findall(r'<sheet [^>]*name="([^"]+)"[^>]*r:id="(rId\d+)"', wbx) if n == name][0]
    rels = z.read('xl/_rels/workbook.xml.rels').decode()
    tgt = {re.search(r'Id="([^"]+)"', m.group(0)).group(1): re.search(r'Target="([^"]+)"', m.group(0)).group(1)
           for m in re.finditer(r'<Relationship [^>]*>', rels)}[rid]
    x = z.read('xl/' + tgt.replace('/xl/', '').lstrip('/')).decode()
    out = {}
    for rn, body in re.findall(r'<row r="(\d+)"[^>]*>(.*?)</row>', x, re.S):
        out[int(rn)] = {c: (v or t) for c, v, t in re.findall(r'<c r="([A-Z]+)\d+"[^>]*>(?:<f>.*?</f>)?(?:<v>([^<]*)</v>|<is><t[^>]*>([^<]*)</t></is>)', body)}
    return out


S = read_sheet(XL, 'Rain_anomaly')
hdr = [r for r in S if S[r].get('A') == 'Year'][0]
ANN = {}
r = hdr + 1
while S.get(r, {}).get('A', '').isdigit():
    row = S[r]
    ANN[int(row['A'])] = dict(com=float(row['D']), oco=float(row['F']), cop=float(row['H']), mean=float(row['J']),
                              g=[float(row[c]) for c in 'KLM'])
    r += 1
mh = [r for r in S if S[r].get('A') == 'Month key'][0]
MON = {}
r = mh + 1
while S.get(r, {}).get('A'):
    row = S[r]
    MON[row['A']] = dict(com_mm=float(row['D']), com_norm=float(row['E']), com=float(row['F']))
    r += 1

p = Page()
A = ANN
gm = {y: sum(A[y]['g']) / 3 for y in A}
p.title('Rain was not normal before the rust: 2008, 2010 and 2011 were the wet years (La Niña)')
p.bullets([
    'Mean of the 3 towns, calendar year: 2008 %s %%, 2010 %s %%, 2011 %s %% of the 2005–2019 normal (independent GPCC gauges: %s, %s and %s %%)'
    % (fr(A[2008]['mean'] * 100, 0), fr(A[2010]['mean'] * 100, 0), fr(A[2011]['mean'] * 100, 0), fr(gm[2008] * 100, 0), fr(gm[2010] * 100, 0), fr(gm[2011] * 100, 0)),
    'Comayagua: %s %% in 2010 and %s %% in 2011; July 2010 %s %%, July 2011 %s %% (%s mm vs a %s mm normal), April 2010 %s %%'
    % (fr(A[2010]['com'] * 100, 0), fr(A[2011]['com'] * 100, 0), fr(MON['2010-07']['com'] * 100, 0), fr(MON['2011-07']['com'] * 100, 0),
       fr(MON['2011-07']['com_mm'], 0), fr(MON['2011-07']['com_norm'], 0), fr(MON['2010-04']['com'] * 100, 0)),
    'The ENSO-season charts hide it: 2010/11 and 2011/12 sit among the other La Niña seasons, which are wet too, and each calendar year is split over two July–June seasons'])
# left: annual bars, mean of 3 towns
YRS = sorted(A)
cats = ["'%02d" % (y % 100) for y in YRS]
vals = [round(A[y]['mean'] * 100, 1) for y in YRS]
cols = [NAVY if v >= 120 else 'C00000' if v <= 80 else LIGHT for v in vals]
X, Y0, WW, HH = 0.4, 2.15, 6.3, 4.55
lay = (0.09, 0.07, 0.89, 0.8)
px, py, pw, ph = p.plot_frame(X, Y0, WW, HH, lay)
n = len(YRS)
i12 = YRS.index(2012)
p.band(px + pw * i12 / n, px + pw * (i12 + 2) / n, py, py + ph, 'FCE4D6')
px, py, pw, ph, Y = p.bars(X, Y0, WW, HH, cats, vals, cols, 150, 25, labels=[fr(v, 0) if (v >= 120 or v <= 80) else '' for v in vals], lay=lay,
                           ylab='Rain, % of normal, mean of the 3 towns (CPC)', label_sz=7.5,
                           line=dict(name='GPCC', values=[round(gm[y] * 100, 1) for y in YRS], color=ORANGE))
p.hline(px, px + pw, Y(100), GREY, 0.012, dash=True)
p.text(px + pw * (i12 + 1) / n - 0.6, py + 0.02, 1.2, 0.2, [('rust 2012–13', dict(b=True, color=ORANGE))], sz=7.5, algn='ctr')
p.legend(X + 0.5, Y0 + HH + 0.05, [(NAVY, '≥ 120 %', 'box'), ('C00000', '≤ 80 %', 'box'), (LIGHT, 'other years', 'box'), (ORANGE, 'GPCC (independent)', 'line')], sz=8)
# right: Comayagua monthly 2010-2012
keys = ['%d-%02d' % (y, m) for y in (2010, 2011, 2012) for m in range(1, 13)]
mv = [round(MON[k]['com'] * 100, 1) for k in keys]
mc = [NAVY if v >= 150 else 'C00000' if v <= 50 else BLUE for v in mv]
mcats = [('J' if k[5:] == '01' else '') + (k[:4] if k[5:] == '01' else ['', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'][int(k[5:]) - 1]) for k in keys]
mcats = [k[:4] if k.endswith('-01') else '' for k in keys]
X2, W2 = 7.0, 6.0
lay2 = (0.09, 0.07, 0.89, 0.8)
px2, py2, pw2, ph2, Y2 = p.bars(X2, Y0, W2, HH, mcats, [min(v, 300) for v in mv], mc, 300, 50, lay=lay2,
                                ylab='Comayagua, rain % of normal by month (CPC), 2010–2012', label_sz=7)
p.hline(px2, px2 + pw2, Y2(100), GREY, 0.012, dash=True)
nn = len(keys)
for k, lab in (('2010-04', 'Apr 2010'), ('2010-07', 'Jul 2010'), ('2011-02', 'Feb 2011*'), ('2011-07', 'Jul 2011'), ('2012-04', 'Apr 2012')):
    i = keys.index(k)
    v = MON[k]['com'] * 100
    p.text(px2 + pw2 * (i + 0.5) / nn - 0.45, Y2(min(v, 300)) - 0.36, 0.9, 0.34, [(lab, dict(b=True, color=NAVY)), fr(v, 0) + ' %'], sz=7, algn='ctr', anchor='b')
p.text(X2 + 0.5, Y0 + HH + 0.02, 5.4, 0.3, [('Bars capped at 300 %%. *Feb 2011 = %s mm in the dry season (normal %s mm): large %% but small amount.' % (fr(MON['2011-02']['com_mm'], 0), fr(MON['2011-02']['com_norm'], 0)), dict(color=GREY))], sz=7.5)
p.source('Source: Honduras_weather_by_ENSO_season.xlsx, sheet Rain_anomaly (NOAA CPC gauge analysis 0.5°, normal = 2005–2019 average of the same month; GPCC 1° for comparison). '
         'Copán from 2024 = adjusted GPCC (CPC gauge lost). The 2012–13 rust also followed low prices and a cooler, more humid 2012 with a smaller day–night range (sheet Rust_2012 of the area-drivers workbook).')
p.render(HERE + 'Rain_anomaly_2005_2025.png')
save([p.s], HERE + 'Rain_anomaly_2005_2025.pptx', 'Honduras rain anomaly')
print('saved', HERE + 'Rain_anomaly_2005_2025.pptx')
