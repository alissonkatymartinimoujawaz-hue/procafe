// Cerrado — climate data store (monthly report tables)
// Same structure as sul_de_minas.js. Historical baseline here is 61/90
// (1961–1990), unlike Sul de Minas' 74/25.
// To add a month: copy a period block, change the key "YYYY-MM" and the numbers.
// The "Average" row is computed automatically in the page — do NOT store it here.

window.CERRADO_DATA = {
  climate_monthly: {
    section_title: "1 – LOCATION / CLIMATE & PHENOLOGICAL DATA OF THE COFFEE TREE",
    hist_label: "61/90",
    footnotes: [
      "Historical average over the 1961–1990 period",
      "Thornthwaite & Mather method"
    ],
    periods: {
      "2025-01": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 21.7, temp_cur: 22.6, prec_hist: 296.0, prec_cur: 166.2, etp: 104.1, arm: 81.6,  exc: 80.6,  def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 21.9, temp_cur: 22.6, prec_hist: 233.0, prec_cur: 202.6, etp: 104.4, arm: 63.4,  exc: 134.7, def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 23.0, temp_cur: 23.1, prec_hist: 274.0, prec_cur: 254.4, etp: 109.6, arm: 100.0, exc: 20.1,  def: 0.0 }
        ]
      },
      "2025-02": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 22.2, temp_cur: 23.5, prec_hist: 187.0, prec_cur: 96.8, etp: 100.6, arm: 25.0, exc: 52.8, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 21.9, temp_cur: 23.8, prec_hist: 209.5, prec_cur: 87.2, etp: 105.0, arm: 14.8, exc: 30.7, def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 23.0, temp_cur: 24.4, prec_hist: 228.0, prec_cur: 81.2, etp: 110.7, arm: 7.9,  exc: 62.6, def: 0.0 }
        ]
      },
      "2025-03": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 22.0, temp_cur: 23.5, prec_hist: 169.0, prec_cur: 94.2,  etp: 107.1, arm: 12.1, exc: 0.0, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 21.9, temp_cur: 23.6, prec_hist: 189.0, prec_cur: 135.2, etp: 109.6, arm: 40.4, exc: 0.0, def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 22.9, temp_cur: 24.7, prec_hist: 203.0, prec_cur: 41.8,  etp: 121.3, arm: 0.0,  exc: 0.0, def: 71.6 }
        ]
      },
      "2025-04": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 20.7, temp_cur: 21.9, prec_hist: 99.0, prec_cur: 104.4, etp: 83.2, arm: 33.3, exc: 0.0, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 20.7, temp_cur: 21.9, prec_hist: 76.5, prec_cur: 125.2, etp: 82.6, arm: 83.0, exc: 0.0, def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 22.0, temp_cur: 22.9, prec_hist: 79.0, prec_cur: 181.2, etp: 93.0, arm: 16.6, exc: 0.0, def: 0.0 }
        ]
      },
      "2025-05": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 19.2, temp_cur: 19.1, prec_hist: 44.0, prec_cur: 0.8, etp: 59.0, arm: 0.0,  exc: 0.0, def: 24.9 },
          { city: "patrocinio", sup: null, temp_hist: 18.5, temp_cur: 19.1, prec_hist: 23.0, prec_cur: 0.0, etp: 61.1, arm: 21.9, exc: 0.0, def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 20.1, temp_cur: 20.9, prec_hist: 22.0, prec_cur: 0.0, etp: 73.7, arm: 0.0,  exc: 0.0, def: 57.1 }
        ]
      },
      "2025-06": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 17.9, temp_cur: 18.8, prec_hist: 17.0, prec_cur: 0.0, etp: 54.0, arm: 0.0, exc: 0.0, def: 78.9 },
          { city: "patrocinio", sup: null, temp_hist: 17.0, temp_cur: 18.3, prec_hist: 6.0,  prec_cur: 1.6, etp: 51.2, arm: 0.0, exc: 0.0, def: 27.7 },
          { city: "araguari",   sup: null, temp_hist: 18.7, temp_cur: 20.1, prec_hist: 8.0,  prec_cur: 6.0, etp: 63.2, arm: 0.0, exc: 0.0, def: 114.3 }
        ]
      },
      "2025-07": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 17.5, temp_cur: 18.4, prec_hist: 21.0, prec_cur: 0.0, etp: 52.3, arm: 0.0, exc: 0.0, def: 131.2 },
          { city: "patrocinio", sup: null, temp_hist: 16.6, temp_cur: 17.9, prec_hist: 8.0,  prec_cur: 0.0, etp: 49.6, arm: 0.0, exc: 0.0, def: 77.3 },
          { city: "araguari",   sup: null, temp_hist: 18.8, temp_cur: 20.2, prec_hist: 7.0,  prec_cur: 0.0, etp: 66.0, arm: 0.0, exc: 0.0, def: 180.3 }
        ]
      },
      "2025-08": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 19.4, temp_cur: 19.8, prec_hist: 20.0, prec_cur: 7.2, etp: 65.2, arm: 0.0, exc: 0.0, def: 189.2 },
          { city: "patrocinio", sup: null, temp_hist: 18.9, temp_cur: 19.3, prec_hist: 8.5,  prec_cur: 3.2, etp: 61.1, arm: 0.0, exc: 0.0, def: 135.2 },
          { city: "araguari",   sup: null, temp_hist: 20.9, temp_cur: 21.7, prec_hist: 6.0,  prec_cur: 0.0, etp: 82.7, arm: 0.0, exc: 0.0, def: 263.0 }
        ]
      },
      "2025-09": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 20.5, temp_cur: 22.4, prec_hist: 67.0, prec_cur: 75.2, etp: 89.6,  arm: 0.0, exc: 0.0, def: 203.6 },
          { city: "patrocinio", sup: null, temp_hist: 20.7, temp_cur: 22.5, prec_hist: 37.0, prec_cur: 28.2, etp: 90.1,  arm: 0.0, exc: 0.0, def: 197.1 },
          { city: "araguari",   sup: null, temp_hist: 23.0, temp_cur: 24.4, prec_hist: 37.0, prec_cur: 8.6,  etp: 110.2, arm: 0.0, exc: 0.0, def: 364.6 }
        ]
      },
      "2025-10": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 21.4, temp_cur: 22.6, prec_hist: 154.0, prec_cur: 39.2, etp: 98.8,  arm: 0.0, exc: 0.0, def: 263.2 },
          { city: "patrocinio", sup: null, temp_hist: 21.4, temp_cur: 22.4, prec_hist: 144.0, prec_cur: 23.6, etp: 96.8,  arm: 0.0, exc: 0.0, def: 270.3 },
          { city: "araguari",   sup: null, temp_hist: 23.8, temp_cur: 24.1, prec_hist: 145.0, prec_cur: 62.4, etp: 115.4, arm: 0.0, exc: 0.0, def: 417.6 }
        ]
      },
      "2025-11": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 21.3, temp_cur: 23.1, prec_hist: 208.0, prec_cur: 99.0,  etp: 104.7, arm: 0.0, exc: 0.0, def: 268.9 },
          { city: "patrocinio", sup: null, temp_hist: 21.9, temp_cur: 23.2, prec_hist: 197.0, prec_cur: 85.6,  etp: 105.9, arm: 0.0, exc: 0.0, def: 290.6 },
          { city: "araguari",   sup: null, temp_hist: 23.2, temp_cur: 24.2, prec_hist: 253.0, prec_cur: 129.8, etp: 116.7, arm: 0.0, exc: 0.0, def: 404.5 }
        ]
      },
      "2022-01": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 21.7, temp_cur: 21.2, prec_hist: 296.0, prec_cur: 373.0, etp: 89.1,  arm: 100.0, exc: 283.9, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 21.9, temp_cur: 21.6, prec_hist: 233.0, prec_cur: 353.0, etp: 93.1,  arm: 100.0, exc: 259.9, def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 23.0, temp_cur: 22.4, prec_hist: 274.0, prec_cur: 401.4, etp: 102.1, arm: 97.3,  exc: 301.9, def: 0.0 }
        ]
      },
      "2022-02": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 22.2, temp_cur: 20.8, prec_hist: 187.0, prec_cur: 447.0, etp: 75.7, arm: 80.4, exc: 390.9, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 21.9, temp_cur: 21.7, prec_hist: 209.5, prec_cur: 275.0, etp: 83.0, arm: 75.8, exc: 216.2, def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 23.0, temp_cur: 22.7, prec_hist: 228.0, prec_cur: 336.0, etp: 92.6, arm: 72.5, exc: 268.3, def: 0.0 }
        ]
      },
      "2022-03": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 22.0, temp_cur: 22.0, prec_hist: 169.0, prec_cur: 115.2, etp: 92.2,  arm: 72.8, exc: 30.7, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 21.9, temp_cur: 22.1, prec_hist: 189.0, prec_cur: 131.8, etp: 85.1,  arm: 84.3, exc: 38.3, def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 22.9, temp_cur: 24.1, prec_hist: 203.0, prec_cur: 45.2,  etp: 114.0, arm: 3.7,  exc: 0.0,  def: 0.0 }
        ]
      },
      "2022-04": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 20.7, temp_cur: 21.0, prec_hist: 99.0, prec_cur: 70.2, etp: 76.0,  arm: 54.0, exc: 13.0, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 20.7, temp_cur: 21.0, prec_hist: 76.5, prec_cur: 65.6, etp: 75.4,  arm: 62.1, exc: 12.4, def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 22.0, temp_cur: 23.9, prec_hist: 79.0, prec_cur: 17.2, etp: 102.6, arm: 0.0,  exc: 0.0,  def: 81.7 }
        ]
      },
      "2022-05": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 19.2, temp_cur: 18.1, prec_hist: 44.0, prec_cur: 32.6, etp: 52.4, arm: 34.2, exc: 0.0, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 18.5, temp_cur: 17.1, prec_hist: 23.0, prec_cur: 26.4, etp: 44.6, arm: 43.9, exc: 0.0, def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 20.1, temp_cur: 19.8, prec_hist: 22.0, prec_cur: 30.4, etp: 65.1, arm: 0.0,  exc: 0.0, def: 116.4 }
        ]
      },
      "2022-06": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 17.9, temp_cur: 18.2, prec_hist: 17.0, prec_cur: 0.0, etp: 50.3, arm: 0.0, exc: 0.0, def: 16.1 },
          { city: "patrocinio", sup: null, temp_hist: 17.0, temp_cur: 17.2, prec_hist: 6.0,  prec_cur: 3.4, etp: 42.9, arm: 4.4, exc: 0.0, def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 18.7, temp_cur: 20.2, prec_hist: 8.0,  prec_cur: 1.0, etp: 64.1, arm: 0.0, exc: 0.0, def: 179.5 }
        ]
      },
      "2022-07": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 17.5, temp_cur: 18.5, prec_hist: 21.0, prec_cur: 0.0, etp: 53.2, arm: 0.0, exc: 0.0, def: 69.3 },
          { city: "patrocinio", sup: null, temp_hist: 16.6, temp_cur: 17.1, prec_hist: 8.0,  prec_cur: 0.0, etp: 44.0, arm: 0.0, exc: 0.0, def: 39.6 },
          { city: "araguari",   sup: null, temp_hist: 18.8, temp_cur: 20.9, prec_hist: 7.0,  prec_cur: 0.0, etp: 72.1, arm: 0.0, exc: 0.0, def: 251.6 }
        ]
      },
      "2022-08": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 19.4, temp_cur: 17.7, prec_hist: 20.0, prec_cur: 9.4, etp: 50.4, arm: 0.0, exc: 0.0, def: 110.3 },
          { city: "patrocinio", sup: null, temp_hist: 18.9, temp_cur: 19.0, prec_hist: 8.5,  prec_cur: 1.4, etp: 58.8, arm: 0.0, exc: 0.0, def: 97.0 },
          { city: "araguari",   sup: null, temp_hist: 20.9, temp_cur: 21.9, prec_hist: 6.0,  prec_cur: 2.4, etp: 83.7, arm: 0.0, exc: 0.0, def: 332.9 }
        ]
      },
      "2022-09": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 20.5, temp_cur: 22.0, prec_hist: 67.0, prec_cur: 82.8, etp: 86.0,  arm: 0.0, exc: 0.0, def: 113.5 },
          { city: "patrocinio", sup: null, temp_hist: 20.7, temp_cur: 21.6, prec_hist: 37.0, prec_cur: 57.0, etp: 81.8,  arm: 0.0, exc: 0.0, def: 121.8 },
          { city: "araguari",   sup: null, temp_hist: 23.0, temp_cur: 23.8, prec_hist: 37.0, prec_cur: 93.0, etp: 104.1, arm: 0.0, exc: 0.0, def: 344.0 }
        ]
      },
      "2022-10": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 21.4, temp_cur: 22.4, prec_hist: 154.0, prec_cur: 90.2,  etp: 96.8,  arm: 0.0, exc: 0.0, def: 120.1 },
          { city: "patrocinio", sup: null, temp_hist: 21.4, temp_cur: 22.0, prec_hist: 144.0, prec_cur: 100.6, etp: 85.7,  arm: 0.0, exc: 0.0, def: 106.9 },
          { city: "araguari",   sup: null, temp_hist: 23.8, temp_cur: 24.0, prec_hist: 145.0, prec_cur: 92.0,  etp: 114.8, arm: 0.0, exc: 0.0, def: 366.8 }
        ]
      },
      "2022-11": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 21.3, temp_cur: 21.2, prec_hist: 208.0, prec_cur: 109.4, etp: 85.8,  arm: 0.0, exc: 0.0, def: 96.5 },
          { city: "patrocinio", sup: null, temp_hist: 21.9, temp_cur: 21.6, prec_hist: 197.0, prec_cur: 166.4, etp: 88.9,  arm: 0.0, exc: 0.0, def: 29.4 },
          { city: "araguari",   sup: null, temp_hist: 23.2, temp_cur: 23.4, prec_hist: 253.0, prec_cur: 62.0,  etp: 108.2, arm: 0.0, exc: 0.0, def: 413.0 }
        ]
      },
      "2023-01": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 21.7, temp_cur: 21.3, prec_hist: 296.0, prec_cur: 467.0, etp: 90.3, arm: 96.7,  exc: 380.0, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 21.9, temp_cur: 21.2, prec_hist: 233.0, prec_cur: 509.4, etp: 89.6, arm: 98.8,  exc: 421.1, def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 23.0, temp_cur: 22.0, prec_hist: 274.0, prec_cur: 360.0, etp: 97.0, arm: 100.0, exc: 116.6, def: 0.0 }
        ]
      },
      "2023-02": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 22.2, temp_cur: 22.5, prec_hist: 187.0, prec_cur: 178.6, etp: 90.2,  arm: 86.2, exc: 98.9,  def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 21.9, temp_cur: 21.9, prec_hist: 209.5, prec_cur: 195.8, etp: 84.2,  arm: 81.9, exc: 128.6, def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 23.0, temp_cur: 23.7, prec_hist: 228.0, prec_cur: 136.4, etp: 103.0, arm: 86.4, exc: 47.0,  def: 0.0 }
        ]
      },
      "2023-03": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 22.0, temp_cur: 22.7, prec_hist: 169.0, prec_cur: 269.4, etp: 98.0,  arm: 69.9,  exc: 187.7, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 21.9, temp_cur: 21.7, prec_hist: 189.0, prec_cur: 187.6, etp: 88.5,  arm: 100.0, exc: 81.0,  def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 22.9, temp_cur: 23.6, prec_hist: 203.0, prec_cur: 109.0, etp: 108.5, arm: 43.6,  exc: 43.4,  def: 0.0 }
        ]
      },
      "2023-04": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 20.7, temp_cur: 20.9, prec_hist: 99.0, prec_cur: 108.8, etp: 74.2, arm: 76.1, exc: 28.4,  def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 20.7, temp_cur: 20.2, prec_hist: 76.5, prec_cur: 228.4, etp: 70.0, arm: 89.0, exc: 169.4, def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 22.0, temp_cur: 21.9, prec_hist: 79.0, prec_cur: 72.2,  etp: 82.2, arm: 33.6, exc: 0.0,   def: 0.0 }
        ]
      },
      "2023-05": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 19.2, temp_cur: 18.7, prec_hist: 44.0, prec_cur: 13.2, etp: 56.1, arm: 33.2, exc: 0.0, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 18.5, temp_cur: 17.7, prec_hist: 23.0, prec_cur: 0.0,  etp: 49.0, arm: 40.0, exc: 0.0, def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 20.1, temp_cur: 21.1, prec_hist: 22.0, prec_cur: 9.6,  etp: 75.5, arm: 0.0,  exc: 0.0, def: 32.3 }
        ]
      },
      "2023-06": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 17.9, temp_cur: 17.5, prec_hist: 17.0, prec_cur: 1.4, etp: 44.6, arm: 0.0, exc: 0.0, def: 10.0 },
          { city: "patrocinio", sup: null, temp_hist: 17.0, temp_cur: 16.6, prec_hist: 6.0,  prec_cur: 1.0, etp: 39.5, arm: 1.5, exc: 0.0, def: 1.5 },
          { city: "araguari",   sup: null, temp_hist: 18.7, temp_cur: 19.9, prec_hist: 8.0,  prec_cur: 1.4, etp: 61.6, arm: 0.0, exc: 0.0, def: 92.5 }
        ]
      },
      "2023-07": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 17.5, temp_cur: 18.6, prec_hist: 21.0, prec_cur: 10.4, etp: 53.5, arm: 0.0, exc: 0.0, def: 53.1 },
          { city: "patrocinio", sup: null, temp_hist: 16.6, temp_cur: 17.2, prec_hist: 8.0,  prec_cur: 3.4,  etp: 44.5, arm: 0.0, exc: 0.0, def: 42.6 },
          { city: "araguari",   sup: null, temp_hist: 18.8, temp_cur: 21.1, prec_hist: 7.0,  prec_cur: 0.4,  etp: 73.3, arm: 0.0, exc: 0.0, def: 165.4 }
        ]
      },
      "2023-08": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 19.4, temp_cur: 20.9, prec_hist: 20.0, prec_cur: 52.8, etp: 74.3, arm: 0.0, exc: 0.0, def: 74.6 },
          { city: "patrocinio", sup: null, temp_hist: 18.9, temp_cur: 19.9, prec_hist: 8.5,  prec_cur: 28.6, etp: 66.2, arm: 0.0, exc: 0.0, def: 80.2 },
          { city: "araguari",   sup: null, temp_hist: 20.9, temp_cur: 22.9, prec_hist: 6.0,  prec_cur: 21.2, etp: 93.4, arm: 0.0, exc: 0.0, def: 237.6 }
        ]
      },
      "2023-09": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 20.5, temp_cur: 24.5, prec_hist: 67.0, prec_cur: 34.0, etp: 111.9, arm: 0.0, exc: 0.0, def: 152.5 },
          { city: "patrocinio", sup: null, temp_hist: 20.7, temp_cur: 24.1, prec_hist: 37.0, prec_cur: 28.2, etp: 107.0, arm: 0.0, exc: 0.0, def: 159.0 },
          { city: "araguari",   sup: null, temp_hist: 23.0, temp_cur: 26.1, prec_hist: 37.0, prec_cur: 24.0, etp: 130.6, arm: 0.0, exc: 0.0, def: 344.2 }
        ]
      },
      "2023-10": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 21.4, temp_cur: 24.2, prec_hist: 154.0, prec_cur: 237.8, etp: 117.0, arm: 0.0, exc: 0.0, def: 31.7 },
          { city: "patrocinio", sup: null, temp_hist: 21.4, temp_cur: 23.6, prec_hist: 144.0, prec_cur: 162.4, etp: 110.2, arm: 0.0, exc: 0.0, def: 106.8 },
          { city: "araguari",   sup: null, temp_hist: 23.8, temp_cur: 26.1, prec_hist: 145.0, prec_cur: 153.0, etp: 141.8, arm: 0.0, exc: 0.0, def: 333.0 }
        ]
      },
      "2023-11": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 21.3, temp_cur: 24.5, prec_hist: 208.0, prec_cur: 174.2, etp: 122.5, arm: 20.0, exc: 0.0, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 21.9, temp_cur: 23.9, prec_hist: 197.0, prec_cur: 64.2,  etp: 114.2, arm: 0.0,  exc: 0.0, def: 156.8 },
          { city: "araguari",   sup: null, temp_hist: 23.2, temp_cur: 26.4, prec_hist: 253.0, prec_cur: 114.8, etp: 145.0, arm: 0.0,  exc: 0.0, def: 363.2 }
        ]
      },
      "2023-12": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 21.1, temp_cur: 24.1, prec_hist: 293.0, prec_cur: 209.6, etp: 123.2, arm: 100.0, exc: 6.4, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 21.7, temp_cur: 23.6, prec_hist: 276.5, prec_cur: 192.8, etp: 116.7, arm: 0.0,   exc: 0.0, def: 80.7 },
          { city: "araguari",   sup: null, temp_hist: 22.8, temp_cur: 25.7, prec_hist: 344.0, prec_cur: 87.4,  etp: 142.6, arm: 0.0,   exc: 0.0, def: 418.4 }
        ]
      },
      "2024-01": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 21.7, temp_cur: 23.0, prec_hist: 296.0, prec_cur: 285.6, etp: 109.4, arm: 78.3, exc: 197.9, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 21.9, temp_cur: 22.7, prec_hist: 233.0, prec_cur: 200.6, etp: 105.3, arm: 81.4, exc: 76.8,  def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 23.0, temp_cur: 24.2, prec_hist: 274.0, prec_cur: 126.0, etp: 122.6, arm: 33.4, exc: 0.0,   def: 0.0 }
        ]
      },
      "2024-02": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 22.2, temp_cur: 22.8, prec_hist: 187.0, prec_cur: 185.0, etp: 93.7,  arm: 84.4, exc: 85.2, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 21.9, temp_cur: 22.4, prec_hist: 209.5, prec_cur: 115.2, etp: 88.8,  arm: 78.2, exc: 29.6, def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 23.0, temp_cur: 23.6, prec_hist: 228.0, prec_cur: 95.2,  etp: 101.5, arm: 27.1, exc: 0.0,  def: 0.0 }
        ]
      },
      "2024-03": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 22.0, temp_cur: 23.4, prec_hist: 169.0, prec_cur: 275.6, etp: 106.7, arm: 98.7,  exc: 154.6, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 21.9, temp_cur: 22.8, prec_hist: 189.0, prec_cur: 288.8, etp: 99.6,  arm: 100.0, exc: 167.4, def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 22.9, temp_cur: 24.0, prec_hist: 203.0, prec_cur: 252.0, etp: 113.8, arm: 88.6,  exc: 76.8,  def: 0.0 }
        ]
      },
      "2024-04": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 20.7, temp_cur: 22.9, prec_hist: 99.0, prec_cur: 52.6, etp: 92.6,  arm: 47.1, exc: 11.6, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 20.7, temp_cur: 21.9, prec_hist: 76.5, prec_cur: 44.4, etp: 83.1,  arm: 53.9, exc: 7.3,  def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 22.0, temp_cur: 24.2, prec_hist: 79.0, prec_cur: 12.8, etp: 105.9, arm: 0.0,  exc: 0.0,  def: 4.5 }
        ]
      },
      "2024-05": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 19.2, temp_cur: 20.7, prec_hist: 44.0, prec_cur: 2.2, etp: 72.3, arm: 0.0, exc: 0.0, def: 23.0 },
          { city: "patrocinio", sup: null, temp_hist: 18.5, temp_cur: 20.0, prec_hist: 23.0, prec_cur: 0.0, etp: 66.6, arm: 0.0, exc: 0.0, def: 12.7 },
          { city: "araguari",   sup: null, temp_hist: 20.1, temp_cur: 22.8, prec_hist: 22.0, prec_cur: 0.0, etp: 92.0, arm: 0.0, exc: 0.0, def: 96.5 }
        ]
      },
      "2024-06": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 17.9, temp_cur: 19.1, prec_hist: 17.0, prec_cur: 0.0, etp: 55.6, arm: 0.0, exc: 0.0, def: 78.6 },
          { city: "patrocinio", sup: null, temp_hist: 17.0, temp_cur: 18.1, prec_hist: 6.0,  prec_cur: 0.0, etp: 49.8, arm: 0.0, exc: 0.0, def: 62.5 },
          { city: "araguari",   sup: null, temp_hist: 18.7, temp_cur: 21.4, prec_hist: 8.0,  prec_cur: 0.0, etp: 74.0, arm: 0.0, exc: 0.0, def: 170.5 }
        ]
      },
      "2024-07": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 17.5, temp_cur: 19.0, prec_hist: 21.0, prec_cur: 0.0, etp: 56.7, arm: 0.0, exc: 0.0, def: 135.3 },
          { city: "patrocinio", sup: null, temp_hist: 16.6, temp_cur: 17.9, prec_hist: 8.0,  prec_cur: 0.0, etp: 49.6, arm: 0.0, exc: 0.0, def: 112.1 },
          { city: "araguari",   sup: null, temp_hist: 18.8, temp_cur: 21.5, prec_hist: 7.0,  prec_cur: 0.0, etp: 77.6, arm: 0.0, exc: 0.0, def: 248.1 }
        ]
      },
      "2024-08": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 19.4, temp_cur: 20.0, prec_hist: 20.0, prec_cur: 0.0, etp: 67.2, arm: 0.0, exc: 0.0, def: 202.5 },
          { city: "patrocinio", sup: null, temp_hist: 18.9, temp_cur: 19.0, prec_hist: 8.5,  prec_cur: 0.0, etp: 83.7, arm: 0.0, exc: 0.0, def: 195.8 },
          { city: "araguari",   sup: null, temp_hist: 20.9, temp_cur: 21.9, prec_hist: 6.0,  prec_cur: 0.0, etp: 84.2, arm: 0.0, exc: 0.0, def: 332.3 }
        ]
      },
      "2024-09": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 20.5, temp_cur: 24.5, prec_hist: 67.0, prec_cur: 0.0, etp: 111.7, arm: 0.0, exc: 0.0, def: 314.2 },
          { city: "patrocinio", sup: null, temp_hist: 20.7, temp_cur: 23.7, prec_hist: 37.0, prec_cur: 2.6, etp: 103.1, arm: 0.0, exc: 0.0, def: 296.3 },
          { city: "araguari",   sup: null, temp_hist: 23.0, temp_cur: 26.5, prec_hist: 37.0, prec_cur: 7.2, etp: 134.7, arm: 0.0, exc: 0.0, def: 459.8 }
        ]
      },
      "2024-12": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 21.1, temp_cur: 22.0, prec_hist: 293.0, prec_cur: 471.0, etp: 98.7,  arm: 100.0, exc: 118.6, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 21.7, temp_cur: 22.5, prec_hist: 276.5, prec_cur: 424.8, etp: 103.4, arm: 100.0, exc: 81.7,  def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 22.8, temp_cur: 23.1, prec_hist: 344.0, prec_cur: 379.8, etp: 111.0, arm: 0.0,   exc: 0.0,   def: 24.7 }
        ]
      },
      "2024-11": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 21.3, temp_cur: 22.7, prec_hist: 208.0, prec_cur: 223.0, etp: 100.8, arm: 0.0, exc: 0.0, def: 153.7 },
          { city: "patrocinio", sup: null, temp_hist: 21.9, temp_cur: 22.3, prec_hist: 197.0, prec_cur: 190.2, etp: 95.7,  arm: 0.0, exc: 0.0, def: 139.7 },
          { city: "araguari",   sup: null, temp_hist: 23.2, temp_cur: 22.9, prec_hist: 253.0, prec_cur: 334.0, etp: 102.0, arm: 0.0, exc: 0.0, def: 293.5 }
        ]
      },
      // Dec-2013 report uses a different historical baseline: 74/12 (1974–2012)
      "2013-12": {
        hist_label: "74/12",
        rows: [
          { city: "araxa",      sup: null, temp_hist: 21.1, temp_cur: 21.7, prec_hist: 293.0, prec_cur: 240.8, etp: 81.1, arm: 100.0, exc: 137.1, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 21.7, temp_cur: 22.5, prec_hist: 276.5, prec_cur: 279.2, etp: 89.1, arm: 100.0, exc: 78.0,  def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 22.8, temp_cur: 22.5, prec_hist: 344.0, prec_cur: 392.2, etp: 88.6, arm: 97.8,  exc: 0.0,   def: 0.0 }
        ]
      },
      "2015-12": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 21.1, temp_cur: 21.9, prec_hist: 293.0, prec_cur: 217.5, etp: 97.6,  arm: 96.1, exc: 116.4, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 21.7, temp_cur: 23.4, prec_hist: 276.5, prec_cur: 118.0, etp: 113.7, arm: 0.0,  exc: 0.0,   def: 56.9 },
          { city: "araguari",   sup: null, temp_hist: 22.8, temp_cur: 23.3, prec_hist: 344.0, prec_cur: 216.2, etp: 113.0, arm: 51.3, exc: 0.0,   def: 0.0 }
        ]
      },
      "2017-12": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 21.1, temp_cur: 22.1, prec_hist: 293.0, prec_cur: 205.0, etp: 100.4, arm: 83.0, exc: 112.4, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 21.7, temp_cur: 21.9, prec_hist: 276.5, prec_cur: 264.2, etp: 97.1,  arm: 99.9, exc: 25.2,  def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 22.8, temp_cur: 22.5, prec_hist: 344.0, prec_cur: 251.8, etp: 103.5, arm: 88.8, exc: 158.5, def: 0.0 }
        ]
      },
      "2018-12": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 21.1, temp_cur: 21.7, prec_hist: 293.0, prec_cur: 203.4, etp: 95.3,  arm: 100.0, exc: 103.5, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 21.7, temp_cur: 22.4, prec_hist: 276.5, prec_cur: 261.2, etp: 101.9, arm: 98.3,  exc: 143.7, def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 22.8, temp_cur: 23.1, prec_hist: 344.0, prec_cur: 177.6, etp: 110.6, arm: 100.0, exc: 56.2,  def: 0.0 }
        ]
      },
      "2020-12": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 21.1, temp_cur: 21.5, prec_hist: 208.0, prec_cur: 264.2, etp: 92.7,  arm: 48.5, exc: 0.0,   def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 21.7, temp_cur: 22.1, prec_hist: 276.5, prec_cur: 421.6, etp: 99.0,  arm: 88.7, exc: 162.3, def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 22.8, temp_cur: 23.3, prec_hist: 344.0, prec_cur: 346.0, etp: 112.4, arm: 7.7,  exc: 0.0,   def: 0.0 }
        ]
      },
      "2022-12": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 21.1, temp_cur: 21.5, prec_hist: 293.0, prec_cur: 378.6, etp: 92.3,  arm: 100.0, exc: 89.8, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 21.7, temp_cur: 21.3, prec_hist: 276.5, prec_cur: 305.4, etp: 90.0,  arm: 100.0, exc: 86.0, def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 22.8, temp_cur: 22.2, prec_hist: 344.0, prec_cur: 466.6, etp: 100.0, arm: 0.0,   exc: 0.0,  def: 46.4 }
        ]
      },
      "2026-07": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 17.5, temp_cur: 17.5, prec_hist: 21.0, prec_cur: 0.0,  etp: 51.4, arm: 0.0, exc: 0.0, def: 117.6 },
          { city: "patrocinio", sup: null, temp_hist: 16.6, temp_cur: 18.2, prec_hist: 8.0,  prec_cur: 9.6,  etp: 55.5, arm: 0.0, exc: 0.0, def: 43.2 },
          { city: "araguari",   sup: null, temp_hist: 18.8, temp_cur: 20.6, prec_hist: 7.0,  prec_cur: 10.0, etp: 69.6, arm: 0.0, exc: 0.0, def: 165.2 }
        ]
      },
      // Jan-2026 report's column header prints "2025" (report typo) — values match the 2026 curves.
      "2026-01": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 21.7, temp_cur: 21.8, prec_hist: 296.0, prec_cur: 318.0, etp: 96.0,  arm: 99.0,  exc: 123.0, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 21.9, temp_cur: 21.6, prec_hist: 233.0, prec_cur: 342.0, etp: 93.1,  arm: 100.0, exc: 148.9, def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 23.0, temp_cur: 22.4, prec_hist: 274.0, prec_cur: 426.3, etp: 101.7, arm: 99.5,  exc: 225.1, def: 0.0 }
        ]
      },
      "2026-02": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 22.2, temp_cur: 22.3, prec_hist: 187.0, prec_cur: 271.2, etp: 96.0, arm: 90.6, exc: 183.6, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 21.9, temp_cur: 21.7, prec_hist: 209.5, prec_cur: 427.0, etp: 83.0, arm: 96.7, exc: 347.3, def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 23.0, temp_cur: 22.9, prec_hist: 228.0, prec_cur: 288.6, etp: 94.3, arm: 93.7, exc: 200.1, def: 0.0 }
        ]
      },
      "2026-03": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 22.0, temp_cur: 22.4, prec_hist: 169.0, prec_cur: 256.0, etp: 89.5,  arm: 83.9, exc: 173.2, def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 21.9, temp_cur: 21.3, prec_hist: 189.0, prec_cur: 188.2, etp: 84.2,  arm: 74.1, exc: 126.6, def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 22.9, temp_cur: 23.0, prec_hist: 203.0, prec_cur: 223.6, etp: 101.7, arm: 61.8, exc: 128.0, def: 0.0 }
        ]
      },
      "2026-04": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 20.7, temp_cur: 21.9, prec_hist: 99.0, prec_cur: 20.8, etp: 90.2, arm: 14.5, exc: 0.0,  def: 0.0 },
          { city: "patrocinio", sup: null, temp_hist: 20.7, temp_cur: 21.4, prec_hist: 76.5, prec_cur: 85.2, etp: 78.8, arm: 52.8, exc: 27.8, def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 22.0, temp_cur: 23.5, prec_hist: 79.0, prec_cur: 10.8, etp: 98.8, arm: 0.0,  exc: 0.0,  def: 26.2 }
        ]
      },
      "2026-05": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 19.2, temp_cur: 20.8, prec_hist: 44.0, prec_cur: 0.0, etp: 72.5, arm: 0.0, exc: 0.0, def: 58.0 },
          { city: "patrocinio", sup: null, temp_hist: 18.5, temp_cur: 20.6, prec_hist: 23.0, prec_cur: 6.2, etp: 70.9, arm: 0.0, exc: 0.0, def: 11.9 },
          { city: "araguari",   sup: null, temp_hist: 20.1, temp_cur: 22.0, prec_hist: 22.0, prec_cur: 0.0, etp: 83.9, arm: 0.0, exc: 0.0, def: 110.1 }
        ]
      },
      "2026-06": {
        rows: [
          { city: "araxa",      sup: null, temp_hist: 17.9, temp_cur: 17.7, prec_hist: 17.0, prec_cur: 38.0, etp: 46.2, arm: 0.0, exc: 0.0, def: 66.2 },
          { city: "patrocinio", sup: null, temp_hist: 17.0, temp_cur: 17.7, prec_hist: 6.0,  prec_cur: 61.0, etp: 46.4, arm: 2.7, exc: 0.0, def: 0.0 },
          { city: "araguari",   sup: null, temp_hist: 18.7, temp_cur: 19.8, prec_hist: 8.0,  prec_cur: 65.2, etp: 60.7, arm: 0.0, exc: 0.0, def: 105.6 }
        ]
      }
    }
  }
};
