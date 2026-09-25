"""In-season numbers: IHCAFE monthly export profile, 2025/26 exports to date, and the 2026/27 scorecard text.
Monthly exports: IHCAFE Boletin Estadistico de Comercializacion (raw/ihcafe_docs2/051 = 30-08-2022, 052 = 07-02-2023).
2025/26 checkpoints: Honduran press quoting IHCAFE, pages saved in raw/coffee_zones/press/ (read).
All export volumes in quintales = bags of 46 kg."""

# 46-kg bags, October ... September
MONTHLY = {
    '2020/21': [26622.31, 72458.07, 264081.74, 607142.14, 837062.85, 1053268.63, 978104.32, 1087113.12, 1020196.11, 862744.12, 545315.51, 306587.16],
    '2021/22': [104775.99, 135584.84, 386789.92, 660603.36, 655462.18, 959016.50, 761820.83, 681974.54, 734881.33, 509500.02, 319871.16, 220945.30],
}
assert round(sum(MONTHLY['2020/21'])) == 7660696 and round(sum(MONTHLY['2021/22'])) == 6131226   # totals printed in the bulletins

# cumulative 2025/26 exports since 1 October: (date, 2025/26, 2024/25 same date or None, source file, quote)
CHECKPOINTS = [
    ('31 Oct 2025', 51183.91, 51183.91 - 28603.67, 'press/01 La Prensa 5 Nov 2025', '51,183.91 sacos de 46 kilogramos durante octubre ... alza interanual del 126.7%, equivalente a 28,603.67 sacos más'),
    ('3 Mar 2026', 3023652, 1918225, 'press/02 La Prensa 4 Mar 2026', '3,023,652 sacos (de 46 kilogramos) ... 57.6% ... cuando envió al exterior 1,918,225 sacos'),
    ('30 Apr 2026', 4970000, 3600000, 'press/06 El Heraldo 4 May 2026', '4.97 millones de sacos de 46 kilogramos ... comparado a los 3.60 millones de sacos registrados durante el período 2024-2025'),
    ('1 Jul 2026', 6663920, 5773579, 'press/03 La Prensa 3 Jul 2026', 'se exportaron 6,663,920 sacos de 46 kilogramos ... cuando se exportaron 5,773,579 sacos'),
    ('14 Jul 2026', 6853390.59, 5510000, 'press/04 La Prensa 15 Jul 2026', 'se exportaron 6,853,390.59 quintales de 46 kilogramos ... comparado con 5.51 millones registrados en igual período de 2024-2025'),
]
PREV_FULL = 6117313.13          # 2024/25 full season, quintales (press/04: "En la temporada anterior, Honduras exportó 6,117,313.13 quintales")
PENDING_14JUL = 290000          # press/04: "pendiente la exportación de alrededor de 290,000 quintales"
JULAUG_HI = 340000              # press/03: "durante julio y agosto ... las exportaciones oscilarán entre 310,000 y 340,000 sacos" (read as per month: upper case)
DOMESTIC = 380                  # USDA domestic consumption 2025/26, 1 000 60-kg bags (PSD)

NOTES = [
    'The 2024/25 comparisons in the press do not all agree (5 773 579 by 1 July in one article, 5.51 M by 14 July in another); the 2025/26 figures are used, the 2024/25 total (6 117 313) only as the base.',
    'The pace was front-loaded: +127 % in October, +58 % to 3 March, +38 % to 30 April, +24 % to 14 July. Growers sold faster at record prices, so early-season growth overstated the crop. '
    'Do not extrapolate the Oct-Dec 2026 pace for 2026/27 either.',
    'Low case = exports to 14 July + the 290 000 quintales still to ship (sales already registered). High case = exports to 1 July + 340 000 in July and in August. '
    'September shipments and stocks carried in from 2024/25 are not measured; coffee crossing from neighbouring countries is not measured either.',
]

# 2026/27 scorecard lines not taken from the Data sheet: (driver, earlier value, 2026 value, status, evidence, direction, style)
SCORE_TEXT = [
    ('Max. temperature Sep 2026 (1-18), coffee zones, deg C vs normal', None, 2.03, 'data', 'Sep-Oct heat: r = -0.45 with output (exploratory); hottest September since 1981', 'negative: heat before harvest', 'neg'),
    ('Rain Jun - Aug 2026 / normal (GPCC, 3 towns)', None, 0.55, 'data', 'Jun-Oct rain: no reliable link; 2026 is the driest Jun-Aug since 1981', 'downside risk, size unknown', 'neg'),
    ('Rain Dec 2025 - Mar 2026 / normal', None, 1.43, 'data', 'only rain window with a hint (p = 0.02 alone, not robust)', 'positive: moisture before flowering', 'pos'),
    ('Rust, national average incidence % (IHCAFE, end Jan 2026)', 7.57, 8.44, 'DOC', '2012/13: rust on 25 % of the area, output -16 %', 'mild negative (yellow alert, level 4)', 'amb'),
    ('ONI Jun-Aug 2026 (NOAA): very strong El Nino forecast for Oct-Dec', None, 1.80, 'DOC', 'ONI: no link to national output 1982-2025', 'through heat, not rain; main risk also for 2027/28 flowering', 'amb'),
    ('Export revenue 2025/26 to 14 July, US$ million', None, 2158.5, 'DOC', 'nitrogen follows the export price of the crop before (r = +0.47, p = 0.06)', 'positive: cash for fertiliser and harvest labour', 'pos'),
]

FORECAST_NOTES = [
    'Reading: USDA puts 2026/27 at 6 030 (+9 %) from a 2025/26 base of 5 530. IHCAFE exports say 2025/26 was about 6 000: on that base a +9 % year is not what history gives. '
    'Without the heat term the best back-tested mix gives about 5 600-6 000; with the Sep-Oct heat seen so far it gives about 5 500.',
    'The heat term was found in this study after trying 4 temperature windows (Dec-Feb, Mar-May, Jun-Aug, Sep-Oct). It survives removing the warming trend and it improves the out-of-sample back-test '
    '(12.5 % -> 10.5 %), but treat it as a strong hint, not a proven law. Sep 2026 = 1-18 September only (ERA5-Land preliminary data).',
    'Watch, in order: ERA5 / station temperatures for the rest of September and October 2026; the final 2025/26 export total; IHCAFE exports Nov 2026 - Feb 2027 (remember 2025/26 was front-loaded); '
    'IHCAFE rust bulletins; fertiliser imports and the urea price; rain Dec 2026 - Apr 2027 for the 2027/28 flowering (El Nino).',
]
