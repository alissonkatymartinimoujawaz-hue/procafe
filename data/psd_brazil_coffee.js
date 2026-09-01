// USDA PSD-style balance sheet — BRAZIL, GREEN COFFEE
// Layout mirrors the USDA FAS "Production, Supply and Distribution" country table.
//
// SOURCES
//  - Area (planted / harvested = bearing), tree population, yield, arabica &
//    robusta production: USDA (FAS/PSD, cross-checked with CONAB) — the series
//    supplied in the working sheet, MY 2005/06 -> 2026/27.
//  - Trade / stocks / consumption attributes: USDA FAS PSD Online
//    (psd_coffee.csv). NOT yet loaded — this session's network policy blocks
//    apps.fas.usda.gov, so those cells are left null on purpose rather than
//    filled with estimates. Drop the official numbers in and the whole sheet
//    (Total Supply, Total Distribution, Balance Check) recomputes itself.
//
// UNITS
//  area = 1,000 HA · trees = MILLION TREES · yield = 60 KG BAGS / HA
//  every other column = 1,000 60 KG BAGS
//
// Market year = July/June (Brazil coffee MY).

window.PSD_BRAZIL_COFFEE = {
  country: "Brazil",
  commodity: "Coffee, Green",
  marketYear: "July - June",
  updated: "2026-09-01",

  // Order of the columns, exactly as rendered.
  // Displayed columns. Detail attributes (bean / R&G / soluble splits) are still
  // accepted as inputs and roll up into the aggregates below.
  columns: [
    { key: "my",            label: "Market Year",           unit: "",                    type: "text",  align: "left" },
    { key: "status",        label: "Status",                unit: "",                    type: "text",  align: "left" },
    { key: "cycle",         label: "Biennial Cycle",        unit: "",                    type: "text",  align: "left" },
    { key: "areaPlanted",   label: "Area Planted",          unit: "(1,000 HA)",          type: "int" },
    { key: "areaHarvested", label: "Area Harvested",        unit: "(1,000 HA)",          type: "int" },
    { key: "yieldBags",     label: "Yield",                 unit: "(BAGS/HA)",           type: "dec2" },
    { key: "bearing",       label: "Bearing Trees",         unit: "(MILLION TREES)",     type: "int" },
    { key: "nonBearing",    label: "Non-Bearing Trees",     unit: "(MILLION TREES)",     type: "int" },
    { key: "begStocks",     label: "Beginning Stocks",      unit: "(1,000 60 KG BAGS)",  type: "int" },
    { key: "arabica",       label: "Arabica Production",    unit: "(1,000 60 KG BAGS)",  type: "int" },
    { key: "robusta",       label: "Robusta Production",    unit: "(1,000 60 KG BAGS)",  type: "int" },
    { key: "totalExp",      label: "Total Exports",         unit: "(1,000 60 KG BAGS)",  type: "int" },
    { key: "domCons",       label: "Domestic Consumption",  unit: "(1,000 60 KG BAGS)",  type: "int" },
    { key: "endStocks",     label: "Ending Stocks",         unit: "(1,000 60 KG BAGS)",  type: "int" },
    { key: "balance",       label: "Balance Check",         unit: "(1,000 60 KG BAGS)",  type: "calc" }
  ],

  // Rows before this market year are kept in the file but not displayed.
  startYear: "2010/11",

  // rows: [ MY, status, cycle, areaPlanted, areaHarvested(bearing), yield,
  //         bearingTrees, nonBearingTrees, totalTrees, arabica, robusta ]
  rows: [
    ["2005/06", "Historical", "OFF", 2458, 2305, 18.92, 5255,  466, 5721, 34300,  9300],
    ["2006/07", "Historical", "ON",  2471, 2305, 15.66, 5220,  513, 5733, 26000, 10100],
    ["2007/08", "Historical", "OFF", 2431, 2235, 20.89, 5720,  679, 6399, 36000, 10700],
    ["2008/09", "Historical", "ON",  2424, 2223, 16.91, 5890,  677, 6567, 26300, 11300],
    ["2009/10", "Historical", "OFF", 2395, 2151, 20.83, 5725,  873, 6598, 33000, 11800],
    ["2010/11", "Historical", "ON",  2409, 2175, 25.06, 5820,  815, 6635, 41800, 12700],
    ["2011/12", "Historical", "OFF", 2410, 2150, 22.88, 5760,  835, 6595, 34700, 14500],
    ["2012/13", "Historical", "ON",  2387, 2105, 26.65, 5860, 1000, 6860, 41100, 15000],
    ["2013/14", "Historical", "OFF", 2442, 2135, 25.53, 5810, 1055, 6865, 39500, 15000],
    ["2014/15", "Historical", "ON",  2437, 2090, 25.98, 5770, 1185, 6955, 37300, 17000],
    ["2015/16", "Historical", "OFF", 2410, 2070, 23.86, 5735, 1125, 6860, 36100, 13300],
    ["2016/17", "Historical", "ON",  2410, 2070, 27.10, 5735, 1125, 6860, 45600, 10500],
    ["2017/18", "Historical", "OFF", 2400, 2020, 25.20, 5640, 1300, 6940, 38500, 12400],
    ["2018/19", "Historical", "ON",  2395, 2060, 31.46, 5740, 1150, 6890, 48200, 16600],
    ["2019/20", "Historical", "OFF", 2390, 2040, 28.43, 5700, 1230, 6930, 39900, 18100],
    ["2020/21", "Historical", "ON",  2420, 2100, 32.33, 6200, 1050, 7250, 47800, 20100],
    ["2021/22", "Historical", "OFF", 2480, 2010, 28.91, 6010, 1500, 7510, 36400, 21700],
    ["2022/23", "Historical", "ON",  2495, 2020, 30.99, 6100, 1510, 7610, 39800, 22800],
    ["2023/24", "Historical", "OFF", 2510, 2030, 32.66, 6150, 1324, 7474, 44900, 21400],
    ["2024/25", "Historical", "ON",  2235, 1881, 34.56, 6577, 1306, 7883, 44000, 21000],
    ["2025/26", "Estimate",   "OFF", 2255, 1859, 33.89, 6482, 1440, 7922, 38000, 25000],
    ["2026/27", "Forecast",   "ON",  2342, 1941, 37.04, 6876, 1461, 8337, 47500, 24400]
  ],

  // ---------------------------------------------------------------------------
  // PSD attributes, stored the way USDA publishes them: one entry per GAIN
  // release, each release carrying up to three market years, each year with a
  // "USDA Official" column (the PSD database) and a "New Post" column (the
  // attache's revision). Newest release first.
  //
  // An all-zero "USDA Official" column means the year is not in PSD yet; those
  // are simply not entered. Every column below balances on its own:
  // beginning stocks + production + imports = exports + consumption + ending stocks.
  // ---------------------------------------------------------------------------
  releases: [
    {
      id: "BR2026-0025", label: "Coffee Annual, June 2026", date: "2026-06",
      years: {
        "2024/25": {
          official: { begStocks:2085, arabica:44000, robusta:21000, otherProd:0,
                      beanImp:0, rgImp:75, solImp:0, beanExp:41000, rgExp:50, solExp:3700,
                      rgDom:21000, solDom:970, endStocks:440 },
          post:     { begStocks:2085, arabica:44500, robusta:21000, otherProd:0,
                      beanImp:0, rgImp:90, solImp:0, beanExp:41000, rgExp:50, solExp:3700,
                      rgDom:21000, solDom:970, endStocks:955 }
        },
        "2025/26": {
          official: { begStocks:440, arabica:38000, robusta:25000, otherProd:0,
                      beanImp:0, rgImp:75, solImp:0, beanExp:37000, rgExp:50, solExp:3700,
                      rgDom:21300, solDom:980, endStocks:485 },
          post:     { begStocks:955, arabica:38000, robusta:25000, otherProd:0,
                      beanImp:0, rgImp:90, solImp:0, beanExp:34000, rgExp:70, solExp:3800,
                      rgDom:21300, solDom:980, endStocks:3895 }
        },
        "2026/27": {
          post:     { begStocks:3895, arabica:47500, robusta:24400, otherProd:0,
                      beanImp:0, rgImp:90, solImp:0, beanExp:45000, rgExp:70, solExp:4000,
                      rgDom:21400, solDom:990, endStocks:4425 }
        }
      }
    },
    {
      id: "BR2025-0013", label: "Coffee Annual, May 2025", date: "2025-05",
      years: {
        "2023/24": {
          official: { begStocks:4620, arabica:44900, robusta:21400, otherProd:0,
                      beanImp:0, rgImp:75, solImp:0, beanExp:43100, rgExp:50, solExp:3600,
                      rgDom:21600, solDom:960, endStocks:1685 },
          post:     { begStocks:4620, arabica:44900, robusta:21400, otherProd:0,
                      beanImp:0, rgImp:75, solImp:0, beanExp:43100, rgExp:50, solExp:3600,
                      rgDom:21200, solDom:960, endStocks:2085 }
        },
        "2024/25": {
          official: { begStocks:1685, arabica:45400, robusta:21000, otherProd:0,
                      beanImp:0, rgImp:75, solImp:0, beanExp:40500, rgExp:50, solExp:3700,
                      rgDom:21700, solDom:970, endStocks:1240 },
          post:     { begStocks:2085, arabica:43700, robusta:21000, otherProd:0,
                      beanImp:0, rgImp:75, solImp:0, beanExp:40500, rgExp:50, solExp:3700,
                      rgDom:21000, solDom:970, endStocks:640 }
        },
        "2025/26": {
          post:     { begStocks:640, arabica:40900, robusta:24100, otherProd:0,
                      beanImp:0, rgImp:75, solImp:0, beanExp:38000, rgExp:50, solExp:3700,
                      rgDom:21300, solDom:980, endStocks:1685 }
        }
      }
    },
    {
      id: null, label: "Coffee Annual, May 2024", date: "2024-05",
      years: {
        "2022/23": {
          official: { begStocks:540, arabica:39800, robusta:22800, otherProd:0,
                      beanImp:0, rgImp:75, solImp:0, beanExp:32200, rgExp:45, solExp:3900,
                      rgDom:21500, solDom:950, endStocks:4620 },
          post:     { begStocks:540, arabica:39800, robusta:22800, otherProd:0,
                      beanImp:0, rgImp:75, solImp:0, beanExp:32200, rgExp:45, solExp:3900,
                      rgDom:21500, solDom:950, endStocks:4620 }
        },
        "2023/24": {
          official: { begStocks:4620, arabica:44900, robusta:21400, otherProd:0,
                      beanImp:0, rgImp:75, solImp:0, beanExp:39500, rgExp:50, solExp:4300,
                      rgDom:21600, solDom:960, endStocks:4585 },
          post:     { begStocks:4620, arabica:44900, robusta:21400, otherProd:0,
                      beanImp:0, rgImp:75, solImp:0, beanExp:41500, rgExp:50, solExp:4000,
                      rgDom:21600, solDom:960, endStocks:2885 }
        },
        "2024/25": {
          post:     { begStocks:2885, arabica:48200, robusta:21700, otherProd:0,
                      beanImp:0, rgImp:75, solImp:0, beanExp:42500, rgExp:51, solExp:4100,
                      rgDom:21700, solDom:970, endStocks:3539 }
        }
      }
    },
    {
      id: "BR2023-0011", label: "Coffee Annual, May 2023", date: "2023-05",
      years: {
        "2021/22": {
          area: { areaPlanted:2480, areaHarvested:2010, bearing:6010, nonBearing:1500, totalTrees:7510 },
          official: { begStocks:4390, arabica:36400, robusta:21700, otherProd:0,
                      beanImp:0, rgImp:75, solImp:0, beanExp:35576, rgExp:54, solExp:4055,
                      rgDom:21400, solDom:940, endStocks:540 },
          post:     { begStocks:4390, arabica:36400, robusta:21700, otherProd:0,
                      beanImp:0, rgImp:75, solImp:0, beanExp:35576, rgExp:54, solExp:4055,
                      rgDom:21400, solDom:940, endStocks:540 }
        },
        "2022/23": {
          area: { areaPlanted:2495, areaHarvested:2020, bearing:6100, nonBearing:1510, totalTrees:7610 },
          official: { begStocks:540, arabica:39800, robusta:22800, otherProd:0,
                      beanImp:0, rgImp:75, solImp:0, beanExp:33000, rgExp:45, solExp:3600,
                      rgDom:21500, solDom:950, endStocks:4120 },
          post:     { begStocks:540, arabica:39800, robusta:22800, otherProd:0,
                      beanImp:0, rgImp:75, solImp:0, beanExp:33000, rgExp:45, solExp:3600,
                      rgDom:21500, solDom:950, endStocks:4120 }
        },
        "2023/24": {
          area: { areaPlanted:2510, areaHarvested:2030, bearing:6150, nonBearing:1100, totalTrees:7250 },
          post:     { begStocks:4120, arabica:44700, robusta:21700, otherProd:0,
                      beanImp:0, rgImp:75, solImp:0, beanExp:41000, rgExp:50, solExp:4300,
                      rgDom:21600, solDom:960, endStocks:2685 }
        }
      }
    },
    {
      id: null, label: "Coffee Annual, May 2022", date: "2022-05",
      years: {
        "2020/21": {
          area: { areaPlanted:2420, areaHarvested:2100, bearing:6200, nonBearing:1050, totalTrees:7250 },
          official: { begStocks:2373, arabica:49700, robusta:20200, otherProd:0,
                      beanImp:0, rgImp:72, solImp:0, beanExp:41687, rgExp:32, solExp:3954,
                      rgDom:22360, solDom:947, endStocks:3365 },
          post:     { begStocks:2373, arabica:49700, robusta:20200, otherProd:0,
                      beanImp:0, rgImp:72, solImp:0, beanExp:41689, rgExp:32, solExp:3954,
                      rgDom:21350, solDom:930, endStocks:4390 }
        },
        "2021/22": {
          area: { areaPlanted:2480, areaHarvested:2010, bearing:6010, nonBearing:1500, totalTrees:7510 },
          official: { begStocks:3365, arabica:35000, robusta:21300, otherProd:0,
                      beanImp:0, rgImp:74, solImp:0, beanExp:30000, rgExp:20, solExp:3200,
                      rgDom:22705, solDom:950, endStocks:2864 },
          post:     { begStocks:4390, arabica:36400, robusta:21700, otherProd:0,
                      beanImp:0, rgImp:73, solImp:0, beanExp:34000, rgExp:42, solExp:3950,
                      rgDom:21400, solDom:940, endStocks:2231 }
        },
        "2022/23": {
          area: { areaPlanted:2495, areaHarvested:2020, bearing:6100, nonBearing:1510, totalTrees:7610 },
          post:     { begStocks:2231, arabica:41500, robusta:22800, otherProd:0,
                      beanImp:0, rgImp:75, solImp:0, beanExp:35000, rgExp:45, solExp:4000,
                      rgDom:21500, solDom:950, endStocks:5111 }
        }
      }
    },
    {
      id: null, label: "Coffee Annual, May 2021", date: "2021-05",
      years: {
        "2019/20": {
          official: { areaPlanted:2390, areaHarvested:2040, bearing:5700, nonBearing:1230,
                      totalTrees:6930, begStocks:5056, arabica:42000, robusta:18500, otherProd:0,
                      beanImp:0, rgImp:67, solImp:0, beanExp:36175, rgExp:26, solExp:4039,
                      rgDom:22350, solDom:1180, endStocks:1853 },
          post:     { areaPlanted:2390, areaHarvested:2040, bearing:5700, nonBearing:1230,
                      totalTrees:6930, begStocks:5056, arabica:42000, robusta:18500, otherProd:0,
                      beanImp:0, rgImp:67, solImp:0, beanExp:36190, rgExp:26, solExp:4040,
                      rgDom:22065, solDom:929, endStocks:2373 }
        },
        "2020/21": {
          official: { areaPlanted:2420, areaHarvested:2100, bearing:6200, nonBearing:1050,
                      totalTrees:7250, begStocks:1853, arabica:47800, robusta:20100, otherProd:0,
                      beanImp:0, rgImp:67, solImp:0, beanExp:37000, rgExp:20, solExp:4000,
                      rgDom:22350, solDom:1180, endStocks:5270 },
          post:     { areaPlanted:2420, areaHarvested:2100, bearing:6200, nonBearing:1050,
                      totalTrees:7250, begStocks:2373, arabica:49700, robusta:20200, otherProd:0,
                      beanImp:0, rgImp:72, solImp:0, beanExp:41000, rgExp:26, solExp:4000,
                      rgDom:22360, solDom:947, endStocks:4012 }
        },
        "2021/22": {
          post:     { areaPlanted:2480, areaHarvested:2010, bearing:6010, nonBearing:1500,
                      totalTrees:7510, begStocks:4012, arabica:35000, robusta:21300, otherProd:0,
                      beanImp:0, rgImp:74, solImp:0, beanExp:32000, rgExp:20, solExp:3200,
                      rgDom:22705, solDom:950, endStocks:1511 }
        }
      }
    },
    {
      id: null, label: "Coffee Annual, May 2020", date: "2020-05",
      years: {
        "2018/19": {
          official: { areaPlanted:2395, areaHarvested:2060, bearing:5740, nonBearing:1150,
                      totalTrees:6890, begStocks:1919, arabica:48200, robusta:16600, otherProd:0,
                      beanImp:0, rgImp:67, solImp:0, beanExp:37376, rgExp:23, solExp:4023,
                      rgDom:22020, solDom:1180, endStocks:2164 },
          post:     { areaPlanted:2395, areaHarvested:2060, bearing:5740, nonBearing:1150,
                      totalTrees:6890, begStocks:1919, arabica:48200, robusta:16600, otherProd:0,
                      beanImp:0, rgImp:67, solImp:0, beanExp:37379, rgExp:24, solExp:4023,
                      rgDom:22020, solDom:1180, endStocks:2160 }
        },
        "2019/20": {
          official: { areaPlanted:2390, areaHarvested:2040, bearing:5700, nonBearing:1230,
                      totalTrees:6930, begStocks:2164, arabica:39900, robusta:18100, otherProd:0,
                      beanImp:0, rgImp:67, solImp:0, beanExp:32000, rgExp:20, solExp:3300,
                      rgDom:22350, solDom:1180, endStocks:1381 },
          post:     { areaPlanted:2390, areaHarvested:2040, bearing:5700, nonBearing:1230,
                      totalTrees:6930, begStocks:2160, arabica:41000, robusta:18300, otherProd:0,
                      beanImp:0, rgImp:67, solImp:0, beanExp:32700, rgExp:24, solExp:3900,
                      rgDom:22350, solDom:1180, endStocks:1373 }
        },
        "2020/21": {
          post:     { areaPlanted:2420, areaHarvested:2100, bearing:6200, nonBearing:1050,
                      totalTrees:7250, begStocks:1373, arabica:47800, robusta:20100, otherProd:0,
                      beanImp:0, rgImp:67, solImp:0, beanExp:37000, rgExp:24, solExp:4000,
                      rgDom:22350, solDom:1180, endStocks:4786 }
        }
      }
    },
    {
      id: null, label: "Coffee Annual, May 2019", date: "2019-05",
      years: {
        "2017/18": {
          official: { areaPlanted:2400, areaHarvested:2020, bearing:5640, nonBearing:1300,
                      totalTrees:6940, begStocks:3828, arabica:38500, robusta:12400, otherProd:0,
                      beanImp:0, rgImp:61, solImp:0, beanExp:26936, rgExp:20, solExp:3494,
                      rgDom:21275, solDom:1145, endStocks:1919 },
          post:     { areaPlanted:2400, areaHarvested:2020, bearing:5640, nonBearing:1300,
                      totalTrees:6940, begStocks:3828, arabica:38500, robusta:12400, otherProd:0,
                      beanImp:0, rgImp:61, solImp:0, beanExp:26936, rgExp:20, solExp:3494,
                      rgDom:21275, solDom:1145, endStocks:1919 }
        },
        "2018/19": {
          official: { areaPlanted:2395, areaHarvested:2060, bearing:5740, nonBearing:1150,
                      totalTrees:6890, begStocks:1919, arabica:46900, robusta:16500, otherProd:0,
                      beanImp:0, rgImp:65, solImp:0, beanExp:32000, rgExp:30, solExp:3300,
                      rgDom:22020, solDom:1180, endStocks:6854 },
          post:     { areaPlanted:2395, areaHarvested:2060, bearing:5740, nonBearing:1150,
                      totalTrees:6890, begStocks:1919, arabica:48200, robusta:16600, otherProd:0,
                      beanImp:0, rgImp:65, solImp:0, beanExp:36000, rgExp:20, solExp:3700,
                      rgDom:22020, solDom:1180, endStocks:3864 }
        },
        "2019/20": {
          post:     { areaPlanted:2390, areaHarvested:2040, bearing:5700, nonBearing:1230,
                      totalTrees:6930, begStocks:3864, arabica:41000, robusta:18300, otherProd:0,
                      beanImp:0, rgImp:65, solImp:0, beanExp:33500, rgExp:20, solExp:3300,
                      rgDom:22350, solDom:1180, endStocks:2879 }
        }
      }
    },
    {
      id: null, label: "Coffee Annual, May 2018", date: "2018-05",
      years: {
        "2016/17": {
          official: { areaPlanted:2410, areaHarvested:2070, bearing:5735, nonBearing:1125,
                      totalTrees:6860, begStocks:2372, arabica:45600, robusta:10500, otherProd:0,
                      beanImp:0, rgImp:62, solImp:0, beanExp:29325, rgExp:31, solExp:3725,
                      rgDom:20400, solDom:1125, endStocks:3928 },
          post:     { areaPlanted:2410, areaHarvested:2070, bearing:5735, nonBearing:1125,
                      totalTrees:6860, begStocks:2372, arabica:45600, robusta:10500, otherProd:0,
                      beanImp:0, rgImp:62, solImp:0, beanExp:29325, rgExp:31, solExp:3725,
                      rgDom:20500, solDom:1125, endStocks:3828 }
        },
        "2017/18": {
          official: { areaPlanted:2400, areaHarvested:2020, bearing:5640, nonBearing:1300,
                      totalTrees:6940, begStocks:3928, arabica:38800, robusta:12400, otherProd:0,
                      beanImp:0, rgImp:65, solImp:0, beanExp:27200, rgExp:30, solExp:3200,
                      rgDom:21050, solDom:1145, endStocks:2568 },
          post:     { areaPlanted:2400, areaHarvested:2020, bearing:5640, nonBearing:1300,
                      totalTrees:6940, begStocks:3828, arabica:38500, robusta:12400, otherProd:0,
                      beanImp:0, rgImp:61, solImp:0, beanExp:27200, rgExp:22, solExp:3200,
                      rgDom:21150, solDom:1145, endStocks:2072 }
        },
        "2018/19": {
          post:     { areaPlanted:2395, areaHarvested:2060, bearing:5740, nonBearing:1150,
                      totalTrees:6890, begStocks:2072, arabica:44500, robusta:15700, otherProd:0,
                      beanImp:0, rgImp:65, solImp:0, beanExp:32000, rgExp:30, solExp:3300,
                      rgDom:21820, solDom:1180, endStocks:4007 }
        }
      }
    },
    {
      id: null, label: "Coffee Annual, May 2017", date: "2017-05",
      years: {
        "2015/16": {
          official: { areaPlanted:2410, areaHarvested:2070, bearing:5735, nonBearing:1125,
                      totalTrees:6860, begStocks:9305, arabica:36100, robusta:13300, otherProd:0,
                      beanImp:0, rgImp:65, solImp:0, beanExp:31870, rgExp:28, solExp:3645,
                      rgDom:19400, solDom:1110, endStocks:2717 },
          post:     { areaPlanted:2410, areaHarvested:2070, bearing:5735, nonBearing:1125,
                      totalTrees:6860, begStocks:9305, arabica:36100, robusta:13300, otherProd:0,
                      beanImp:0, rgImp:65, solImp:0, beanExp:31870, rgExp:28, solExp:3645,
                      rgDom:19400, solDom:1050, endStocks:2777 }
        },
        "2016/17": {
          official: { begStocks:2717, arabica:45600, robusta:10500, otherProd:0, beanImp:0,
                      rgImp:65, solImp:0, beanExp:31000, rgExp:30, solExp:3200, rgDom:19400,
                      solDom:1110, endStocks:4142 },
          post:     { areaPlanted:2410, areaHarvested:2070, bearing:5735, nonBearing:1125,
                      totalTrees:6860, begStocks:2777, arabica:45600, robusta:10500, otherProd:0,
                      beanImp:0, rgImp:64, solImp:0, beanExp:29400, rgExp:30, solExp:3600,
                      rgDom:19450, solDom:1050, endStocks:5411 }
        },
        "2017/18": {
          post:     { areaPlanted:2400, areaHarvested:2020, bearing:5640, nonBearing:1300,
                      totalTrees:6940, begStocks:5411, arabica:40500, robusta:11600, otherProd:0,
                      beanImp:0, rgImp:65, solImp:0, beanExp:29400, rgExp:30, solExp:3600,
                      rgDom:19550, solDom:1110, endStocks:3886 }
        }
      }
    },
    {
      id: null, label: "Coffee Annual, May 2016", date: "2016-05",
      years: {
        "2014/15": {
          official: { areaPlanted:2437, areaHarvested:2090, bearing:5770, nonBearing:1185,
                      totalTrees:6955, begStocks:11946, arabica:37300, robusta:17000,
                      otherProd:0, beanImp:0, rgImp:52, solImp:0, beanExp:33051, rgExp:28,
                      solExp:3491, rgDom:19250, solDom:1080, endStocks:9398 },
          post:     { areaPlanted:2437, areaHarvested:2090, bearing:5770, nonBearing:1185,
                      totalTrees:6955, begStocks:11946, arabica:37300, robusta:17000,
                      otherProd:0, beanImp:0, rgImp:52, solImp:0, beanExp:33051, rgExp:28,
                      solExp:3494, rgDom:19325, solDom:1095, endStocks:9305 }
        },
        "2015/16": {
          official: { areaPlanted:2410, areaHarvested:2070, bearing:5735, nonBearing:1125,
                      totalTrees:6860, begStocks:9398, arabica:36100, robusta:13300, otherProd:0,
                      beanImp:0, rgImp:60, solImp:0, beanExp:30000, rgExp:30, solExp:3300,
                      rgDom:19250, solDom:1080, endStocks:5198 },
          post:     { areaPlanted:2410, areaHarvested:2070, bearing:5735, nonBearing:1125,
                      totalTrees:6860, begStocks:9305, arabica:36100, robusta:13300, otherProd:0,
                      beanImp:0, rgImp:60, solImp:0, beanExp:32720, rgExp:30, solExp:3250,
                      rgDom:19400, solDom:1110, endStocks:2255 }
        },
        "2016/17": {
          post:     { areaPlanted:2410, areaHarvested:2070, bearing:5735, nonBearing:1125,
                      totalTrees:6860, begStocks:2255, arabica:43850, robusta:12100, otherProd:0,
                      beanImp:0, rgImp:65, solImp:0, beanExp:32000, rgExp:30, solExp:3200,
                      rgDom:19400, solDom:1110, endStocks:2530 }
        }
      }
    },
    {
      id: null, label: "Coffee Annual, May 2015", date: "2015-05",
      years: {
        "2013/14": {
          official: { areaPlanted:2442, areaHarvested:2135, bearing:5810, nonBearing:1055,
                      totalTrees:6865, begStocks:9068, arabica:39500, robusta:15000, otherProd:0,
                      beanImp:0, rgImp:0, solImp:0, beanExp:30593, rgExp:30, solExp:3507,
                      rgDom:19000, solDom:1100, endStocks:9338 },
          post:     { areaPlanted:2442, areaHarvested:2135, bearing:5810, nonBearing:1055,
                      totalTrees:6865, begStocks:9068, arabica:40600, robusta:15400, otherProd:0,
                      beanImp:0, rgImp:34, solImp:0, beanExp:30600, rgExp:30, solExp:3516,
                      rgDom:19130, solDom:1080, endStocks:10746 }
        },
        "2014/15": {
          official: { areaPlanted:2437, areaHarvested:2090, bearing:5770, nonBearing:1185,
                      totalTrees:6955, begStocks:9338, arabica:34200, robusta:17000, otherProd:0,
                      beanImp:0, rgImp:0, solImp:0, beanExp:30000, rgExp:30, solExp:3500,
                      rgDom:19000, solDom:1100, endStocks:6908 },
          post:     { areaPlanted:2437, areaHarvested:2090, bearing:5770, nonBearing:1185,
                      totalTrees:6955, begStocks:10746, arabica:34200, robusta:17000,
                      otherProd:0, beanImp:0, rgImp:38, solImp:0, beanExp:32500, rgExp:27,
                      solExp:3370, rgDom:19250, solDom:1080, endStocks:5757 }
        },
        "2015/16": {
          post:     { areaPlanted:2410, areaHarvested:2070, bearing:5735, nonBearing:1125,
                      totalTrees:6860, begStocks:5757, arabica:38000, robusta:14400, otherProd:0,
                      beanImp:0, rgImp:42, solImp:0, beanExp:30000, rgExp:30, solExp:3300,
                      rgDom:19500, solDom:1080, endStocks:4289 }
        }
      }
    },
    {
      id: null, label: "Coffee Annual, May 2014", date: "2014-05",
      years: {
        "2012/13": {
          official: { areaPlanted:2387, areaHarvested:2105, bearing:5860, nonBearing:1000,
                      totalTrees:6860, begStocks:2238, arabica:41100, robusta:15000, otherProd:0,
                      beanImp:0, rgImp:0, solImp:0, beanExp:27143, rgExp:31, solExp:3486,
                      rgDom:19495, solDom:1120, endStocks:7063 },
          post:     { areaPlanted:2387, areaHarvested:2105, bearing:5860, nonBearing:1000,
                      totalTrees:6860, begStocks:2238, arabica:42100, robusta:15500, otherProd:0,
                      beanImp:0, rgImp:0, solImp:0, beanExp:27143, rgExp:31, solExp:3486,
                      rgDom:19000, solDom:1110, endStocks:9068 }
        },
        "2013/14": {
          official: { areaPlanted:2442, areaHarvested:2135, bearing:5810, nonBearing:1055,
                      totalTrees:6865, begStocks:7063, arabica:39200, robusta:13900, otherProd:0,
                      beanImp:0, rgImp:0, solImp:0, beanExp:27500, rgExp:40, solExp:3500,
                      rgDom:20020, solDom:1130, endStocks:7973 },
          post:     { areaPlanted:2442, areaHarvested:2135, bearing:5810, nonBearing:1055,
                      totalTrees:6865, begStocks:9068, arabica:39400, robusta:14300, otherProd:0,
                      beanImp:0, rgImp:0, solImp:0, beanExp:30000, rgExp:25, solExp:3350,
                      rgDom:19000, solDom:1100, endStocks:9293 }
        },
        "2014/15": {
          post:     { areaPlanted:2437, areaHarvested:2090, bearing:5770, nonBearing:1185,
                      totalTrees:6955, begStocks:9293, arabica:33100, robusta:16400, otherProd:0,
                      beanImp:0, rgImp:0, solImp:0, beanExp:29000, rgExp:25, solExp:3350,
                      rgDom:19000, solDom:1100, endStocks:6318 }
        }
      }
    },
    {
      id: null, label: "Coffee Annual, May 2013", date: "2013-05",
      years: {
        "2011/12": {
          official: { areaPlanted:2410, areaHarvested:2150, bearing:5760, nonBearing:835,
                      totalTrees:6595, begStocks:2906, arabica:34700, robusta:14500, otherProd:0,
                      beanImp:0, rgImp:0, solImp:0, beanExp:26556, rgExp:51, solExp:3236,
                      rgDom:18900, solDom:1080, endStocks:2283 },
          post:     { areaPlanted:2410, areaHarvested:2150, bearing:5760, nonBearing:835,
                      totalTrees:6595, begStocks:2906, arabica:34700, robusta:14500, otherProd:0,
                      beanImp:0, rgImp:0, solImp:0, beanExp:26556, rgExp:51, solExp:3236,
                      rgDom:18905, solDom:1120, endStocks:2238 }
        },
        "2012/13": {
          official: { areaPlanted:2398, areaHarvested:2130, bearing:5865, nonBearing:950,
                      totalTrees:6815, begStocks:2283, arabica:40200, robusta:15700, otherProd:0,
                      beanImp:0, rgImp:0, solImp:0, beanExp:29600, rgExp:50, solExp:3300,
                      rgDom:19580, solDom:1110, endStocks:4543 },
          post:     { areaPlanted:2387, areaHarvested:2105, bearing:5860, nonBearing:1000,
                      totalTrees:6860, begStocks:2238, arabica:41100, robusta:15000, otherProd:0,
                      beanImp:0, rgImp:0, solImp:0, beanExp:27465, rgExp:35, solExp:3500,
                      rgDom:19495, solDom:1120, endStocks:6723 }
        },
        "2013/14": {
          post:     { areaPlanted:2442, areaHarvested:2135, bearing:5810, nonBearing:1055,
                      totalTrees:6865, begStocks:6723, arabica:38500, robusta:15200, otherProd:0,
                      beanImp:0, rgImp:0, solImp:0, beanExp:27500, rgExp:40, solExp:3500,
                      rgDom:20020, solDom:1130, endStocks:8233 }
        }
      }
    },
    {
      id: null, label: "Coffee Annual, May 2011", date: "2011-05",
      years: {
        "2009/10": {
          official: { areaPlanted:2395, areaHarvested:2151, bearing:5725, nonBearing:873,
                      totalTrees:6598, begStocks:6576, arabica:33000, robusta:11800, otherProd:0,
                      beanImp:0, rgImp:0, solImp:0, beanExp:26580, rgExp:80, solExp:3120,
                      rgDom:17730, solDom:1020, endStocks:2846 },
          post:     { areaPlanted:2395, areaHarvested:2151, bearing:5725, nonBearing:873,
                      totalTrees:6598, begStocks:6576, arabica:33000, robusta:11800, otherProd:0,
                      beanImp:0, rgImp:0, solImp:0, beanExp:26580, rgExp:80, solExp:3120,
                      rgDom:17720, solDom:1040, endStocks:2836 }
        },
        "2010/11": {
          official: { areaPlanted:2409, areaHarvested:2175, bearing:5820, nonBearing:815,
                      totalTrees:6635, begStocks:2846, arabica:41800, robusta:12700, otherProd:0,
                      beanImp:0, rgImp:0, solImp:0, beanExp:28600, rgExp:100, solExp:3300,
                      rgDom:18470, solDom:1030, endStocks:5846 },
          post:     { areaPlanted:2409, areaHarvested:2175, bearing:5820, nonBearing:815,
                      totalTrees:6635, begStocks:2836, arabica:41800, robusta:12700, otherProd:0,
                      beanImp:0, rgImp:0, solImp:0, beanExp:30630, rgExp:70, solExp:3300,
                      rgDom:18470, solDom:1030, endStocks:3836 }
        },
        "2011/12": {
          post:     { areaPlanted:2410, areaHarvested:2150, bearing:5760, nonBearing:835,
                      totalTrees:6595, begStocks:3836, arabica:34700, robusta:14500, otherProd:0,
                      beanImp:0, rgImp:0, solImp:0, beanExp:24930, rgExp:70, solExp:3000,
                      rgDom:19020, solDom:1080, endStocks:4936 }
        }
      }
    }
  ]
};
