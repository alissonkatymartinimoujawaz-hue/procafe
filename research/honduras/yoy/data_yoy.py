"""Honduras coffee, year by year 2005-2026: productivity, fertiliser, disease, varieties, finance, exchange rate.
Every series comes from a file in research/honduras/ (source and status on each line). Standard library only.
Status: USDA = read in a USDA FAS Coffee Annual; FAO = FAOSTAT bulk file; BCH = Banco Central de Honduras file;
WB = World Bank Pink Sheet; DOC = read in a downloaded document (IHCAFE, press); PRESS = web-search extract, page not read."""
import json, os, sys, csv, re, glob, zipfile, datetime, statistics as st, collections

HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
HN = HERE + '../'
sys.path.insert(0, HN + 'data')
sys.path.insert(0, HN + 'yield_drivers')
import finance_varieties as FV

YEARS = list(range(2005, 2027))

# ---------------------------------------------------------------- area, trees, production (USDA attache + PSD)
A = json.load(open(HN + 'data/area_trees_attache.json'))
BEAR = dict(zip(A['years'], A['bearing_kha']))
NONB = dict(zip(A['years'], A['nonbearing_kha']))
TREES = dict(zip(A['years'], A['bearing_trees_m']))
NTREES = dict(zip(A['years'], A['nonbearing_trees_m']))
PSD = {int(k): v for k, v in A['psd_full']['Arabica Production'].items()}
FC = json.load(open(HN + 'yield_drivers/forecast_2026_27.json'))
PROD_EXPORT_IMPLIED = {2025: FC['base_exports']}            # 2025/26 production implied by IHCAFE exports (Exports_nowcast sheet)
REG = {int(k[:4]): dict(ha=sum(v[s][1] for s in ('small', 'medium', 'large')), bags=sum(v[s][2] for s in ('small', 'medium', 'large')),
                         producers=sum(v[s][0] for s in ('small', 'medium', 'large')), src=v['src']) for k, v in FV.REGISTRY.items()}

# IHCAFE exports, 46-kg bags (crop years); 1970/71-2020/21 from the IHCAFE 2020-2021 report, 2021/22 from bulletin 052,
# 2024/25 and 2025/26 from the press pages read in raw/coffee_zones/press
import analysis as AN
EXPORTS = {t: AN.EXP[t] for t in AN.EXP if t >= 2005}
EXPORTS[2021] = 6131225.97
EXPORTS[2022] = 6900000          # El Heraldo 23 Jun 2024 (ihcafe_docs4/022): '6.9 millones de sacos ... exportados' Oct 2022 - Sep 2023 (rounded)
EXPORTS[2024] = 6117313.13
EXPORTS_EST = {2025: FC['exports_q']['mid']}

# ---------------------------------------------------------------- fertiliser (FAOSTAT)
FAO = {int(k): v for k, v in json.load(open(HN + 'data/faostat_inputs_land_labour.json')).items()}
FERT_FLAG = {}
for r in csv.DictReader(open(HN + 'raw/faostat/honduras_fert_nutrient.csv', encoding='utf-8-sig')):
    if r['Element'] == 'Import quantity' and r['Item'].startswith('Nutrient nitrogen'):
        FERT_FLAG[int(r['Year'])] = r['Flag']
ARA, UREA = AN.ARA, AN.UREA


def wb_col(col):
    """annual mean of a World Bank monthly column (DAP = BG, KCl = BJ)"""
    z = zipfile.ZipFile(HN + '../indonesia/raw/worldbank_cmo_monthly.xlsx')
    strs = [re.sub(r'<[^>]+>', '', m) for m in re.findall(r'<si>(.*?)</si>', z.read('xl/sharedStrings.xml').decode('utf8'), re.S)]
    out = collections.defaultdict(list)
    for rn, body in re.findall(r'<row [^>]*r="(\d+)"[^>]*>(.*?)</row>', z.read('xl/worksheets/sheet2.xml').decode(), re.S):
        c = {}
        for cc, attr, v in re.findall(r'<c r="([A-Z]+)\d+"([^>]*)>(?:<f>.*?</f>)?<v>([^<]*)</v>', body):
            c[cc] = strs[int(v)] if 't="s"' in attr else v
        if re.match(r'^\d{4}M\d\d$', c.get('A', '')) and col in c:
            try:
                out[int(c['A'][:4])].append(float(c[col]))
            except ValueError:
                pass
    return {y: st.mean(v) for y, v in out.items() if len(v) >= 6}


DAP = wb_col('BG')

# ---------------------------------------------------------------- exchange rate (BCH daily reference rate, buying)
def bch_fx():
    f = glob.glob(HN + 'raw/ihcafe_docs2/023_*.xlsx')[0]
    z = zipfile.ZipFile(f)
    ss = [re.sub(r'<[^>]+>', '', m) for m in re.findall(r'<si>(.*?)</si>', z.read('xl/sharedStrings.xml').decode('utf8'), re.S)]
    D = {}
    for rn, body in re.findall(r'<row [^>]*r="(\d+)"[^>]*>(.*?)</row>', z.read('xl/worksheets/sheet1.xml').decode(), re.S):
        c = {}
        for col, attr, v in re.findall(r'<c r="([A-Z]+)\d+"([^>]*)>(?:<f>.*?</f>)?<v>([^<]*)</v>', body):
            c[col] = ss[int(v)] if 't="s"' in attr else v
        try:
            s = float(c.get('A', 'x'))
        except ValueError:
            continue
        if 30000 < s < 50000 and 'B' in c:
            D[datetime.date(1899, 12, 30) + datetime.timedelta(days=int(s))] = float(c['B'])
    Y = collections.defaultdict(list)
    for d, v in D.items():
        Y[d.year].append(v)
    return {y: st.mean(v) for y, v in Y.items()}, max(D), D


FX, FX_LAST, FX_DAILY = bch_fx()

# ---------------------------------------------------------------- disease (rust = roya); national figures only unless said
RUST = [
    dict(year=2012, when='2012/13 crop', value=25.0, measure='% of coffee AREA affected (71 000 ha)', status='USDA', src='GAIN 2013, 2014'),
    dict(year=2014, when='Apr 2014', value=12.0, measure='national average incidence (first national survey)', status='USDA', src='GAIN 2014'),
    dict(year=2017, when='Apr 2017', value=3.0, measure='% of LEMPIRA plants with rust (Lempira lost its resistance in 2016/17)', status='USDA', src='GAIN 2017, 2018'),
    dict(year=2020, when='end 2020', value=20.0, lo=15, hi=25, measure='incidence in 5 departments after hurricanes Eta and Iota', status='USDA', src='GAIN 2021'),
    dict(year=2020, when='Nov 2020', value=None, measure='Eta and Iota: > 4 200 ha of coffee farms hit, > 150 000 qq lost', status='DOC', src='La Prensa / EFE 1 Nov 2022 (read)'),
    dict(year=2022, when='2022/23 crop', value=20.0, measure='% of PRODUCTION affected by rust (IHCAFE director)', status='DOC', src='La Prensa / EFE 1 Nov 2022 (read)'),
    dict(year=2022, when='Apr 2022', value=5.42, measure='national average incidence (66 % of farms low, 29 % medium, 5 % high)', status='USDA', src='GAIN 2022'),
    dict(year=2023, when='May 2023', value=5.8, measure='national average incidence (La Paz 9.7 %, Fco. Morazan 8.2 %)', status='USDA', src='GAIN 2023 (repeated in GAIN 2024)'),
    dict(year=2024, when='Mar 2024', value=7.38, measure='national average incidence', status='PRESS', src='web search summary (La Prensa / El Heraldo)'),
    dict(year=2024, when='Apr 2024', value=None, measure='76 % of sampled farms low, 19 % medium, 5 % high', status='USDA', src='GAIN 2025'),
    dict(year=2024, when='2024', value=None, measure='BCH: exports about 500 000 qq lower than 2023 "due to high rust incidence and labour shortage"', status='DOC', src='El Heraldo 23 Jun 2024 (read)'),
    dict(year=2025, when='Jan-Mar 2025', value=5.71, measure='national average (13 of 15 departments hit; Santa Barbara 9.29 %, El Paraiso 7.91 %, Comayagua 7.20 %; worst varieties Obata and Catuai)',
         status='DOC', src='El Heraldo 13 May 2025 (read)'),
    dict(year=2025, when='Apr 2025', value=None, measure='sampled farms: 16.7 % medium (5-10 %), 7.8 % high (10-15 %), 21.6 % very high (> 15 %)', status='USDA', src='GAIN 2026'),
    dict(year=2026, when='end Jan 2026', value=8.44, measure='national average incidence (from 7.57 %); departments 2.06-14.08 %; ~30 % of farms > 10 %', status='DOC', src='El Heraldo 15 Feb 2026 (read); GAIN 2026'),
]
RUST_RULE = FV.RUST_RULE

# qualitative disease / weather / input notes by crop year, read in USDA reports
NOTES_USDA = {
    2015: 'El Nino drought: "Producers did not apply fertilizer due to the drought" (GAIN 2016).',
    2016: 'First crop from plantings renewed after the 2012-14 rust (GAIN 2016).',
    2017: 'Drought forecast; "Small farmers lack the resources to apply fertilizers" (GAIN 2017). Lempira hit by rust in 2016/17 (GAIN 2018).',
    2019: 'Price 2.88 $/kg, lowest since 2007.',
    2020: 'Bono Cafetalero: 25 188 t of fertiliser to 91 778 producers (GAIN 2021); hurricanes Eta and Iota in November.',
    2021: '"cyclical decline in productivity after a widespread re-planting effort ten years ago" and rust (GAIN 2022); fertiliser prices up (Russia) (GAIN 2022).',
    2022: 'Less rust and "coffee drill bit" (berry borer) expected; high fertiliser costs (GAIN 2023).',
    2023: '"high incidence of coffee rust and ongoing labor shortage" (GAIN 2024).',
    2024: 'Less rust, better labour availability, prices +81 % (GAIN 2025).',
    2025: 'Parainema plantings harvested; rust up to 8.44 % by Jan 2026; fertiliser supply risk (Persian Gulf) (GAIN 2026).',
}

# ---------------------------------------------------------------- Bono Cafetalero (state fertiliser gift) by year
BONO = [
    dict(year=2020, fert_qq=25188 * 1000 / 46, fert_t=25188, producers=91778, lps_m=None, usd_m=12, status='USDA', src='GAIN 2021'),
    dict(year=2021, fert_qq=None, fert_t=None, producers=91500, lps_m=None, usd_m=12.5, status='USDA', src='GAIN 2021 (extension to Dec 2021)'),
    dict(year=2022, fert_qq=216223, fert_t=216223 * 46 / 1000, producers=83273, lps_m=250, usd_m=None, status='DOC', src='La Prensa 27 Jul 2022 (read): 2-5 qq per grower, formula 17-3-17'),
    dict(year=2023, fert_qq=253032, fert_t=253032 * 46 / 1000, producers=95000, lps_m=None, usd_m=None, status='PRESS', src='Gobierno Solidario (search summary)'),
    dict(year=2024, fert_qq=186000, fert_t=186000 * 46 / 1000, producers=None, lps_m=None, usd_m=None, status='PRESS', src='TNH (search summary: "mas de 186 mil sacos")'),
    dict(year=2025, fert_qq=300000, fert_t=300000 * 46 / 1000, producers=None, lps_m=None, usd_m=None, status='DOC', src='El Heraldo 14 Feb 2026 (read): "pasando de 300 mil quintales a cerca de 400 mil"'),
    dict(year=2026, fert_qq=400000, fert_t=400000 * 46 / 1000, producers=85600, lps_m=None, usd_m=None, status='DOC', src='El Heraldo 14 Feb 2026 (read): plan "cerca de 400 mil quintales", > 85 600 producers'),
]
PRODUCERS = [dict(year=2018, value=130000, registered=110000, status='DOC', src='El Heraldo 5 Sep 2018 (read)'),
             dict(year=2022, value=100000, registered=None, status='DOC', src='La Prensa / EFE 1 Nov 2022 (read): "mas de 100,000 productores"')]

# ---------------------------------------------------------------- BCH bank credit to agriculture (all farming, coffee not separated)
# "Prestamos de las Otras Sociedades de Depositos al Sector Privado por Actividad", millions of lempiras (raw/ihcafe_docs5)
BCH_AGRI = {}
for r in csv.DictReader(open(HN + 'raw/ihcafe_docs5/bch_prestamos_agropecuaria.csv')):
    BCH_AGRI[(r['sheet'], r['date'][:7])] = (float(r['agropecuaria_mill_L']), float(r['total_mill_L']))
CREDIT = []
for y in range(2017, 2026):
    s_, n_ = BCH_AGRI[('Pres sobre saldos', '%d-12' % y)], BCH_AGRI[('Pres Nuevos', '%d-12' % y)]
    CREDIT.append(dict(year=y, label='%d (Dec)' % y, stock=s_[0], stock_total=s_[1], new=n_[0], new_total=n_[1]))
s_, n_ = BCH_AGRI[('Pres sobre saldos', '2026-07')], BCH_AGRI[('Pres Nuevos', '2026-07')]
n25 = BCH_AGRI[('Pres Nuevos', '2025-07')]
s25 = BCH_AGRI[('Pres sobre saldos', '2025-07')]
CREDIT_2026 = dict(stock=s_[0], stock_total=s_[1], new=n_[0], new_total=n_[1], new_jul25=n25[0], stock_jul25=s25[0])

# ---------------------------------------------------------------- heat (coffee zones) for context
RB = json.load(open(HN + 'yield_drivers/robustness.json'))
HEAT = {int(k): v for k, v in RB['coffee_zone_tmax']['sep_oct'].items()}


def build():
    rows = []
    for t in YEARS:
        r = dict(year=t, bear_kha=BEAR.get(t), nonbear_kha=NONB.get(t), trees_m=TREES.get(t), ntrees_m=NTREES.get(t), prod_kbags=PSD.get(t),
                 prod_export_implied=PROD_EXPORT_IMPLIED.get(t), exports_q=EXPORTS.get(t), exports_q_est=EXPORTS_EST.get(t),
                 reg_ha=REG.get(t, {}).get('ha'), reg_bags=REG.get(t, {}).get('bags'), reg_producers=REG.get(t, {}).get('producers'),
                 n_t=FAO.get(t, {}).get('N'), p_t=FAO.get(t, {}).get('P2O5'), k_t=FAO.get(t, {}).get('K2O'), n_flag=FERT_FLAG.get(t),
                 urea_imp_t=FAO.get(t, {}).get('urea_imp_t'), urea_imp_usd_t=FAO.get(t, {}).get('urea_imp_usd_t'),
                 urea_wb=UREA.get(t), dap_wb=DAP.get(t), arabica=ARA.get(t), fx=FX.get(t), heat_sep_oct=HEAT.get(t))
        rows.append(r)
    return rows


if __name__ == '__main__':
    for r in build():
        print(r)
    print('FX last day', FX_LAST, FX_DAILY[FX_LAST])
