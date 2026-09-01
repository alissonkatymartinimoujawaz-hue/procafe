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
  columns: [
    { key: "my",            label: "Market Year",            unit: "",                    type: "text",  align: "left" },
    { key: "status",        label: "Status",                 unit: "",                    type: "text",  align: "left" },
    { key: "cycle",         label: "Biennial Cycle",         unit: "",                    type: "text",  align: "left" },
    { key: "areaPlanted",   label: "Area Planted",           unit: "(1,000 HA)",          type: "int" },
    { key: "areaHarvested", label: "Area Harvested",         unit: "(1,000 HA)",          type: "int" },
    { key: "yieldBags",     label: "Yield",                  unit: "(BAGS/HA)",           type: "dec2" },
    { key: "bearing",       label: "Bearing Trees",          unit: "(MILLION TREES)",     type: "int" },
    { key: "nonBearing",    label: "Non-Bearing Trees",      unit: "(MILLION TREES)",     type: "int" },
    { key: "totalTrees",    label: "Total Tree Population",  unit: "(MILLION TREES)",     type: "int" },
    { key: "begStocks",     label: "Beginning Stocks",       unit: "(1,000 60 KG BAGS)",  type: "int" },
    { key: "arabica",       label: "Arabica Production",     unit: "(1,000 60 KG BAGS)",  type: "int" },
    { key: "robusta",       label: "Robusta Production",     unit: "(1,000 60 KG BAGS)",  type: "int" },
    { key: "otherProd",     label: "Other Production",       unit: "(1,000 60 KG BAGS)",  type: "int" },
    { key: "production",    label: "Total Production",       unit: "(1,000 60 KG BAGS)",  type: "calc" },
    { key: "beanImp",       label: "Bean Imports",           unit: "(1,000 60 KG BAGS)",  type: "int" },
    { key: "rgImp",         label: "Roast & Ground Imports", unit: "(1,000 60 KG BAGS)",  type: "int" },
    { key: "solImp",        label: "Soluble Imports",        unit: "(1,000 60 KG BAGS)",  type: "int" },
    { key: "totalImp",      label: "Total Imports",          unit: "(1,000 60 KG BAGS)",  type: "calc" },
    { key: "totalSupply",   label: "Total Supply",           unit: "(1,000 60 KG BAGS)",  type: "calc" },
    { key: "beanExp",       label: "Bean Exports",           unit: "(1,000 60 KG BAGS)",  type: "int" },
    { key: "rgExp",         label: "Rst-Ground Exports",     unit: "(1,000 60 KG BAGS)",  type: "int" },
    { key: "solExp",        label: "Soluble Exports",        unit: "(1,000 60 KG BAGS)",  type: "int" },
    { key: "totalExp",      label: "Total Exports",          unit: "(1,000 60 KG BAGS)",  type: "calc" },
    { key: "rgDom",         label: "Rst,Ground Dom. Consum", unit: "(1,000 60 KG BAGS)",  type: "int" },
    { key: "solDom",        label: "Soluble Dom. Cons.",     unit: "(1,000 60 KG BAGS)",  type: "int" },
    { key: "domCons",       label: "Domestic Consumption",   unit: "(1,000 60 KG BAGS)",  type: "calc" },
    { key: "endStocks",     label: "Ending Stocks",          unit: "(1,000 60 KG BAGS)",  type: "int" },
    { key: "totalDist",     label: "Total Distribution",     unit: "(1,000 60 KG BAGS)",  type: "calc" },
    { key: "balance",       label: "Balance Check",          unit: "(1,000 60 KG BAGS)",  type: "calc" }
  ],

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

  // Balance-sheet attributes still to be loaded from PSD Online (psd_coffee.csv).
  // Key = market year; any subset of the keys below is accepted and the table
  // fills in immediately. Only cells confirmed against an official USDA release
  // are present today.
  balanceSheet: {
    // Every value below comes from the SAME USDA vintage (June 2026 release:
    // Brazil Coffee Annual BR2026-0025 + Coffee: World Markets and Trade), so the
    // rows stay internally coherent. Attributes from other release vintages are
    // deliberately not mixed in.
    "2025/26": {
      endStocks: 3895,
      _src: "USDA FAS, June 2026 release (Coffee Annual BR2026-0025 / Coffee: World Markets & Trade)"
    },
    "2026/27": {
      begStocks: 3895, totalExp: 49070, domCons: 22390, endStocks: 4425,
      _src: "USDA FAS, June 2026 release (Coffee Annual BR2026-0025 / Coffee: World Markets & Trade)"
    }
  }
};
