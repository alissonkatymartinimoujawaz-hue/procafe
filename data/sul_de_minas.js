// Sul de Minas — data store
// ---------------------------------------------------------------------------
// TAB 1  "climate_monthly" : one entry per month/year (from the monthly report
//         table screenshots). The "Média" row is computed in the page.
// TABS 2-5 (one per city) : each city's "graphs" block feeds 4 charts:
//         (1) soil water availability, (2) mean temperature,
//         (3) monthly rainfall, (4) accumulated rainfall (computed from monthly).
//
// ⚠ The graph series are DIGITIZED (read off the source chart images) and are
//    therefore APPROXIMATE — flagged in the UI. Correct any value here directly.
// ---------------------------------------------------------------------------

window.SUL_DE_MINAS_DATA = {

  climate_monthly: {
    section_title: "1 – LOCATION / CLIMATE & PHENOLOGICAL DATA OF THE COFFEE TREE",
    hist_label: "74/25",
    footnotes: [
      "Historical average over the 1974–2025 period – Varginha",
      "Thornthwaite & Mather method",
      "Average over the 2010–2025 period",
      "Average over the 2015–2025 period"
    ],
    periods: {
      // 2024 reports: baseline 74/23; 4th city Muzambinho.
      "2024-01": {
        hist_label: "74/23",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 22.5, temp_cur: 23.1, prec_hist: 274.8, prec_cur: 189.6, etp: 110.8, arm: 86.2, exc: 60.2,  def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 21.2, temp_cur: 21.5, prec_hist: 294.7, prec_cur: 302.8, etp: 83.0,  arm: 94.0, exc: 214.9, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 23.5, temp_cur: 24.1, prec_hist: 241.1, prec_cur: 215.4, etp: 123.6, arm: 74.1, exc: 53.7,  def: 0.0 },
          { city: "muzambinho",     sup: null, temp_hist: 21.8, temp_cur: 22.4, prec_hist: 250.9, prec_cur: 237.0, etp: 103.1, arm: 97.5, exc: 86.5,  def: 0.0 }
        ]
      },
      "2024-02": {
        hist_label: "74/23",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 22.6, temp_cur: 23.9, prec_hist: 190.3, prec_cur: 142.0, etp: 108.8, arm: 97.2, exc: 22.2,  def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 21.3, temp_cur: 20.7, prec_hist: 178.8, prec_cur: 165.6, etp: 73.5,  arm: 89.8, exc: 96.3,  def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 23.6, temp_cur: 24.2, prec_hist: 162.9, prec_cur: 135.8, etp: 108.6, arm: 73.4, exc: 27.9,  def: 0.0 },
          { city: "muzambinho",     sup: null, temp_hist: 21.4, temp_cur: 21.8, prec_hist: 259.0, prec_cur: 173.0, etp: 84.1,  arm: 81.4, exc: 105.0, def: 0.0 }
        ]
      },
      "2024-03": {
        hist_label: "74/23",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 22.2, temp_cur: 23.2, prec_hist: 168.7, prec_cur: 209.0, etp: 105.6, arm: 95.9,  exc: 104.7, def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 20.6, temp_cur: 20.9, prec_hist: 160.1, prec_cur: 154.6, etp: 81.4,  arm: 96.5,  exc: 66.5,  def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 23.1, temp_cur: 24.5, prec_hist: 140.3, prec_cur: 211.0, etp: 119.7, arm: 95.6,  exc: 69.1,  def: 0.0 },
          { city: "muzambinho",     sup: null, temp_hist: 21.2, temp_cur: 21.8, prec_hist: 189.4, prec_cur: 193.0, etp: 88.8,  arm: 100.0, exc: 85.6,  def: 0.0 }
        ]
      },
      "2024-04": {
        hist_label: "74/23",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 20.8, temp_cur: 22.1, prec_hist: 73.6, prec_cur: 16.0, etp: 85.0, arm: 26.9, exc: 0.0, def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 19.0, temp_cur: 19.6, prec_hist: 57.9, prec_cur: 38.0, etp: 63.1, arm: 71.4, exc: 0.0, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 21.7, temp_cur: 23.4, prec_hist: 53.6, prec_cur: 41.6, etp: 97.6, arm: 39.6, exc: 0.0, def: 0.0 },
          { city: "muzambinho",     sup: null, temp_hist: 19.7, temp_cur: 20.8, prec_hist: 71.1, prec_cur: 30.0, etp: 73.0, arm: 57.0, exc: 0.0, def: 0.0 }
        ]
      },
      "2024-05": {
        hist_label: "74/23",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 17.9, temp_cur: 20.5, prec_hist: 48.8, prec_cur: 10.8, etp: 70.2, arm: 0.0,  exc: 0.0, def: 32.5 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 16.5, temp_cur: 18.3, prec_hist: 42.7, prec_cur: 31.8, etp: 53.0, arm: 50.2, exc: 0.0, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 19.0, temp_cur: 21.7, prec_hist: 39.7, prec_cur: 11.6, etp: 80.4, arm: 0.0,  exc: 0.0, def: 29.2 },
          { city: "muzambinho",     sup: null, temp_hist: 17.0, temp_cur: 18.9, prec_hist: 48.3, prec_cur: 32.0, etp: 57.0, arm: 32.0, exc: 0.0, def: 0.0 }
        ]
      },
      "2024-06": {
        hist_label: "74/23",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 16.8, temp_cur: 18.4, prec_hist: 33.1, prec_cur: 0.8, etp: 49.8, arm: 0.0,  exc: 0.0, def: 81.5 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 15.9, temp_cur: 16.0, prec_hist: 33.9, prec_cur: 0.0, etp: 35.6, arm: 14.6, exc: 0.0, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 17.8, temp_cur: 19.2, prec_hist: 26.7, prec_cur: 2.0, etp: 55.6, arm: 0.0,  exc: 0.0, def: 82.8 },
          { city: "muzambinho",     sup: null, temp_hist: 16.6, temp_cur: 16.7, prec_hist: 29.9, prec_cur: 0.0, etp: 39.8, arm: 0.0,  exc: 0.0, def: 7.8 }
        ]
      },
      "2024-07": {
        hist_label: "74/23",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 16.4, temp_cur: 18.3, prec_hist: 16.2, prec_cur: 3.0,  etp: 51.2, arm: 0.0, exc: 0.0, def: 129.7 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 15.6, temp_cur: 15.9, prec_hist: 21.1, prec_cur: 18.0, etp: 36.1, arm: 0.0, exc: 0.0, def: 3.5 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 17.8, temp_cur: 19.3, prec_hist: 9.1,  prec_cur: 0.0,  etp: 58.4, arm: 0.0, exc: 0.0, def: 141.2 },
          { city: "muzambinho",     sup: null, temp_hist: 15.9, temp_cur: 17.6, prec_hist: 12.0, prec_cur: 9.0,  etp: 46.8, arm: 0.0, exc: 0.0, def: 45.6 }
        ]
      },
      "2024-08": {
        hist_label: "74/23",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 18.5, temp_cur: 19.3, prec_hist: 19.0, prec_cur: 5.2,  etp: 60.5, arm: 0.0, exc: 0.0, def: 185.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 17.0, temp_cur: 16.5, prec_hist: 19.0, prec_cur: 30.0, etp: 41.0, arm: 0.0, exc: 0.0, def: 14.5 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 19.4, temp_cur: 20.1, prec_hist: 12.4, prec_cur: 0.0,  etp: 67.4, arm: 0.0, exc: 0.0, def: 208.6 },
          { city: "muzambinho",     sup: null, temp_hist: 17.4, temp_cur: 17.9, prec_hist: 19.9, prec_cur: 3.0,  etp: 50.4, arm: 0.0, exc: 0.0, def: 93.0 }
        ]
      },
      "2024-09": {
        hist_label: "74/23",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 20.3, temp_cur: 23.6, prec_hist: 70.7, prec_cur: 18.6, etp: 110.8, arm: 0.0, exc: 0.0, def: 277.2 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 19.3, temp_cur: 20.7, prec_hist: 69.5, prec_cur: 5.6,  etp: 73.5,  arm: 0.0, exc: 0.0, def: 82.4 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 22.2, temp_cur: 24.6, prec_hist: 46.1, prec_cur: 35.4, etp: 112.1, arm: 0.0, exc: 0.0, def: 285.3 },
          { city: "muzambinho",     sup: null, temp_hist: 20.7, temp_cur: 22.2, prec_hist: 65.9, prec_cur: 6.0,  etp: 87.1,  arm: 0.0, exc: 0.0, def: 174.1 }
        ]
      },
      "2024-10": {
        hist_label: "74/23",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 21.1, temp_cur: 22.7, prec_hist: 109.4, prec_cur: 219.6, etp: 99.9,  arm: 0.0,  exc: 0.0,  def: 157.5 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 20.1, temp_cur: 20.1, prec_hist: 137.2, prec_cur: 280.4, etp: 73.9,  arm: 92.4, exc: 31.7, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 23.1, temp_cur: 23.8, prec_hist: 115.5, prec_cur: 226.4, etp: 112.6, arm: 0.0,  exc: 0.0,  def: 171.5 },
          { city: "muzambinho",     sup: null, temp_hist: 21.5, temp_cur: 22.4, prec_hist: 159.6, prec_cur: 313.0, etp: 97.1,  arm: 41.8, exc: 0.0,  def: 0.0 }
        ]
      },
      "2024-11": {
        hist_label: "74/23",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 21.9, temp_cur: 21.9, prec_hist: 174.1, prec_cur: 223.2, etp: 92.4,  arm: 0.0,  exc: 0.0,   def: 26.7 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 19.8, temp_cur: 19.4, prec_hist: 197.4, prec_cur: 272.8, etp: 68.8,  arm: 93.6, exc: 202.8, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 22.6, temp_cur: 22.9, prec_hist: 177.0, prec_cur: 196.4, etp: 104.1, arm: 0.0,  exc: 0.0,   def: 79.2 },
          { city: "muzambinho",     sup: null, temp_hist: 20.8, temp_cur: 21.0, prec_hist: 190.1, prec_cur: 295.0, etp: 84.1,  arm: 69.8, exc: 182.9, def: 0.0 }
        ]
      },
      "2024-12": {
        hist_label: "74/23",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 22.2, temp_cur: 22.5, prec_hist: 259.7, prec_cur: 306.0, etp: 104.4, arm: 100.0, exc: 74.9,  def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 20.9, temp_cur: 19.9, prec_hist: 253.9, prec_cur: 513.6, etp: 77.1,  arm: 100.0, exc: 430.1, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 23.4, temp_cur: 23.5, prec_hist: 235.3, prec_cur: 341.8, etp: 116.1, arm: 100.0, exc: 46.5,  def: 0.0 },
          { city: "muzambinho",     sup: null, temp_hist: 21.4, temp_cur: 21.0, prec_hist: 256.9, prec_cur: 286.0, etp: 88.7,  arm: 94.2,  exc: 172.9, def: 0.0 }
        ]
      },
      // 2023 reports: baseline 74/22; 4th city Muzambinho.
      "2023-01": {
        hist_label: "74/22",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 22.5, temp_cur: 21.1, prec_hist: 265.2, prec_cur: 496.4, etp: 89.2,  arm: 100.0, exc: 407.2, def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 21.4, temp_cur: 19.2, prec_hist: 285.4, prec_cur: 416.2, etp: 70.7,  arm: 98.4,  exc: 345.5, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 23.6, temp_cur: 22.4, prec_hist: 214.1, prec_cur: 593.0, etp: 102.6, arm: 96.3,  exc: 494.1, def: 0.0 },
          { city: "muzambinho",     sup: null, temp_hist: 22.0, temp_cur: 20.1, prec_hist: 225.6, prec_cur: 504.0, etp: 79.2,  arm: 100.0, exc: 424.8, def: 0.0 }
        ]
      },
      "2023-02": {
        hist_label: "74/22",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 22.7, temp_cur: 22.1, prec_hist: 184.6, prec_cur: 273.2, etp: 89.3,  arm: 94.3,  exc: 189.6, def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 21.4, temp_cur: 20.1, prec_hist: 171.6, prec_cur: 273.6, etp: 68.6,  arm: 100.0, exc: 203.4, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 23.6, temp_cur: 23.5, prec_hist: 162.7, prec_cur: 166.0, etp: 101.5, arm: 67.9,  exc: 92.9,  def: 0.0 },
          { city: "muzambinho",     sup: null, temp_hist: 21.5, temp_cur: 20.3, prec_hist: 242.3, prec_cur: 426.0, etp: 70.5,  arm: 90.2,  exc: 365.4, def: 0.0 }
        ]
      },
      "2023-03": {
        hist_label: "74/22",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 22.2, temp_cur: 22.2, prec_hist: 168.0, prec_cur: 146.2, etp: 93.0,  arm: 80.1, exc: 67.4,  def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 20.7, temp_cur: 19.9, prec_hist: 159.1, prec_cur: 173.8, etp: 71.4,  arm: 96.6, exc: 105.9, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 23.1, temp_cur: 23.7, prec_hist: 139.7, prec_cur: 148.6, etp: 109.1, arm: 37.5, exc: 69.9,  def: 0.0 },
          { city: "muzambinho",     sup: null, temp_hist: 21.1, temp_cur: 22.2, prec_hist: 196.9, prec_cur: 115.0, etp: 93.1,  arm: 48.5, exc: 63.7,  def: 0.0 }
        ]
      },
      "2023-04": {
        hist_label: "74/22",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 20.8, temp_cur: 20.2, prec_hist: 73.1, prec_cur: 97.0,  etp: 67.8, arm: 76.4, exc: 33.0, def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 19.1, temp_cur: 17.8, prec_hist: 52.7, prec_cur: 125.0, etp: 50.0, arm: 83.9, exc: 87.7, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 21.8, temp_cur: 21.5, prec_hist: 51.1, prec_cur: 85.4,  etp: 79.4, arm: 43.5, exc: 0.0,  def: 0.0 },
          { city: "muzambinho",     sup: null, temp_hist: 19.7, temp_cur: 19.8, prec_hist: 65.5, prec_cur: 127.0, etp: 65.0, arm: 91.3, exc: 19.2, def: 0.0 }
        ]
      },
      // 2022 reports: baseline 74/21; 4th city Muzambinho.
      "2022-01": {
        hist_label: "74/21",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 22.5, temp_cur: 21.9, prec_hist: 261.1, prec_cur: 462.8, etp: 98.1,  arm: 100.0, exc: 364.7, def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 21.4, temp_cur: 20.8, prec_hist: 272.8, prec_cur: 436.5, etp: 86.0,  arm: 100.0, exc: 350.5, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 23.6, temp_cur: 23.2, prec_hist: 208.1, prec_cur: 285.8, etp: 112.5, arm: 88.8,  exc: 184.5, def: 0.0 },
          { city: "muzambinho",     sup: null, temp_hist: 22.0, temp_cur: 22.1, prec_hist: 217.9, prec_cur: 295.0, etp: 100.5, arm: 100.0, exc: 194.5, def: 0.0 }
        ]
      },
      "2022-02": {
        hist_label: "74/21",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 22.7, temp_cur: 22.6, prec_hist: 186.6, prec_cur: 229.6, etp: 93.9, arm: 71.6, exc: 164.1, def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 21.4, temp_cur: 21.3, prec_hist: 169.6, prec_cur: 195.0, etp: 78.6, arm: 71.2, exc: 145.2, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 23.6, temp_cur: 22.8, prec_hist: 158.3, prec_cur: 215.0, etp: 94.5, arm: 68.2, exc: 141.1, def: 0.0 },
          { city: "muzambinho",     sup: null, temp_hist: 21.5, temp_cur: 21.7, prec_hist: 247.2, prec_cur: 198.0, etp: 83.7, arm: 62.2, exc: 152.2, def: 0.0 }
        ]
      },
      "2022-04": {
        hist_label: "74/21",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 20.8, temp_cur: 21.0, prec_hist: 74.1, prec_cur: 31.2, etp: 75.1, arm: 32.2, exc: 0.0, def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 19.1, temp_cur: 19.3, prec_hist: 54.3, prec_cur: 33.0, etp: 61.1, arm: 56.5, exc: 1.4, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 21.7, temp_cur: 22.4, prec_hist: 53.9, prec_cur: 17.4, etp: 87.9, arm: 0.0,  exc: 0.0, def: 14.3 },
          { city: "muzambinho",     sup: null, temp_hist: 19.6, temp_cur: 19.9, prec_hist: 68.7, prec_cur: 37.0, etp: 65.6, arm: 47.9, exc: 0.0, def: 0.0 }
        ]
      },
      "2022-05": {
        hist_label: "74/21",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 18.0, temp_cur: 17.1, prec_hist: 49.4, prec_cur: 27.0, etp: 45.1, arm: 14.1, exc: 0.0, def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 16.7, temp_cur: 15.0, prec_hist: 44.1, prec_cur: 28.6, etp: 32.2, arm: 52.9, exc: 0.0, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 19.1, temp_cur: 18.0, prec_hist: 44.1, prec_cur: 15.4, etp: 51.5, arm: 0.0,  exc: 0.0, def: 50.4 },
          { city: "muzambinho",     sup: null, temp_hist: 17.2, temp_cur: 15.3, prec_hist: 53.6, prec_cur: 30.0, etp: 34.4, arm: 43.5, exc: 0.0, def: 0.0 }
        ]
      },
      "2022-06": {
        hist_label: "74/21",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 16.8, temp_cur: 17.0, prec_hist: 33.4, prec_cur: 9.2,  etp: 41.4, arm: 0.0,  exc: 0.0, def: 18.1 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 16.0, temp_cur: 15.5, prec_hist: 35.6, prec_cur: 10.8, etp: 33.1, arm: 30.6, exc: 0.0, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 17.9, temp_cur: 17.7, prec_hist: 29.2, prec_cur: 5.2,  etp: 45.8, arm: 0.0,  exc: 0.0, def: 91.0 },
          { city: "muzambinho",     sup: null, temp_hist: 16.7, temp_cur: 16.9, prec_hist: 30.3, prec_cur: 6.0,  etp: 40.6, arm: 8.9,  exc: 0.0, def: 0.0 }
        ]
      },
      "2021-03": {
        hist_label: "74/20",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 22.2, temp_cur: 22.4, prec_hist: 172.3, prec_cur: 79.2,  etp: 95.9,  arm: 57.9, exc: 22.8,  def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 20.7, temp_cur: 20.4, prec_hist: 164.6, prec_cur: 157.0, etp: 75.3,  arm: 94.6, exc: 85.0,  def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 22.9, temp_cur: 23.6, prec_hist: 141.3, prec_cur: 155.8, etp: 108.6, arm: 42.9, exc: 101.1, def: 0.0 },
          { city: "muzambinho",     sup: null, temp_hist: 21.0, temp_cur: 21.4, prec_hist: 204.2, prec_cur: 136.0, etp: 85.6,  arm: 71.9, exc: 76.1,  def: 0.0 }
        ]
      },
      "2021-04": {
        hist_label: "74/20",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 20.8, temp_cur: 19.6, prec_hist: 75.3, prec_cur: 11.6, etp: 63.0, arm: 6.5,  exc: 0.0, def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 19.2, temp_cur: 17.5, prec_hist: 58.3, prec_cur: 10.6, etp: 47.4, arm: 57.8, exc: 0.0, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 21.8, temp_cur: 20.9, prec_hist: 58.4, prec_cur: 4.6,  etp: 74.3, arm: 0.0,  exc: 0.0, def: 26.8 },
          { city: "muzambinho",     sup: null, temp_hist: 19.8, temp_cur: 18.5, prec_hist: 76.0, prec_cur: 10.0, etp: 55.7, arm: 26.2, exc: 0.0, def: 0.0 }
        ]
      },
      "2021-05": {
        hist_label: "74/20",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 17.9, temp_cur: 18.3, prec_hist: 50.0, prec_cur: 44.0, etp: 52.3, arm: 0.0,  exc: 0.0, def: 1.8 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 16.7, temp_cur: 16.5, prec_hist: 45.0, prec_cur: 34.0, etp: 40.7, arm: 51.1, exc: 0.0, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 19.0, temp_cur: 19.5, prec_hist: 46.9, prec_cur: 13.4, etp: 61.4, arm: 0.0,  exc: 0.0, def: 74.8 },
          { city: "muzambinho",     sup: null, temp_hist: 17.2, temp_cur: 17.4, prec_hist: 56.0, prec_cur: 34.0, etp: 46.2, arm: 14.0, exc: 0.0, def: 0.0 }
        ]
      },
      "2021-06": {
        hist_label: "74/20",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 16.8, temp_cur: 17.0, prec_hist: 33.8, prec_cur: 34.2, etp: 41.4, arm: 0.0,  exc: 0.0, def: 9.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 16.1, temp_cur: 15.1, prec_hist: 37.3, prec_cur: 16.2, etp: 31.0, arm: 36.3, exc: 0.0, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 17.9, temp_cur: 17.7, prec_hist: 29.9, prec_cur: 21.2, etp: 46.0, arm: 0.0,  exc: 0.0, def: 99.6 },
          { city: "muzambinho",     sup: null, temp_hist: 16.7, temp_cur: 16.3, prec_hist: 31.5, prec_cur: 20.0, etp: 37.4, arm: 0.0,  exc: 0.0, def: 3.4 }
        ]
      },
      "2021-07": {
        hist_label: "74/20",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 16.4, temp_cur: 15.5, prec_hist: 16.9, prec_cur: 1.0, etp: 34.3, arm: 0.0,  exc: 0.0, def: 42.3 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 15.8, temp_cur: 13.4, prec_hist: 25.2, prec_cur: 8.0, etp: 24.2, arm: 20.1, exc: 0.0, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 17.8, temp_cur: 16.0, prec_hist: 11.1, prec_cur: 0.0, etp: 37.0, arm: 0.0,  exc: 0.0, def: 136.6 },
          { city: "muzambinho",     sup: null, temp_hist: 16.0, temp_cur: 14.2, prec_hist: 14.7, prec_cur: 5.0, etp: 27.4, arm: 0.0,  exc: 0.0, def: 25.8 }
        ]
      },
      "2021-08": {
        hist_label: "74/20",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 18.4, temp_cur: 19.0, prec_hist: 19.2, prec_cur: 0.8, etp: 59.6, arm: 0.0, exc: 0.0, def: 101.1 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 17.0, temp_cur: 16.7, prec_hist: 19.7, prec_cur: 7.2, etp: 43.4, arm: 0.0, exc: 0.0, def: 16.1 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 19.3, temp_cur: 19.7, prec_hist: 11.1, prec_cur: 2.2, etp: 65.3, arm: 0.0, exc: 0.0, def: 199.7 },
          { city: "muzambinho",     sup: null, temp_hist: 17.3, temp_cur: 18.4, prec_hist: 22.3, prec_cur: 4.6, etp: 54.7, arm: 0.0, exc: 0.0, def: 75.9 }
        ]
      },
      "2021-09": {
        hist_label: "74/20",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 20.2, temp_cur: 23.1, prec_hist: 71.8, prec_cur: 32.8, etp: 95.9,  arm: 0.0, exc: 0.0, def: 164.2 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 19.2, temp_cur: 20.6, prec_hist: 71.4, prec_cur: 27.2, etp: 72.4,  arm: 0.0, exc: 0.0, def: 61.3 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 22.0, temp_cur: 24.1, prec_hist: 50.3, prec_cur: 14.4, etp: 107.3, arm: 0.0, exc: 0.0, def: 292.6 },
          { city: "muzambinho",     sup: null, temp_hist: 20.4, temp_cur: 22.5, prec_hist: 73.4, prec_cur: 39.6, etp: 90.8,  arm: 0.0, exc: 0.0, def: 127.1 }
        ]
      },
      "2021-10": {
        hist_label: "74/20",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 21.1, temp_cur: 21.0, prec_hist: 105.8, prec_cur: 202.2, etp: 82.3, arm: 0.0,   exc: 0.0,  def: 44.3 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 20.2, temp_cur: 18.5, prec_hist: 107.7, prec_cur: 303.0, etp: 60.4, arm: 100.0, exc: 81.3, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 23.2, temp_cur: 21.7, prec_hist: 76.1,  prec_cur: 456.0, etp: 89.7, arm: 73.7,  exc: 0.0,  def: 0.0 },
          { city: "muzambinho",     sup: null, temp_hist: 21.6, temp_cur: 19.8, prec_hist: 119.8, prec_cur: 361.8, etp: 71.9, arm: 100.0, exc: 62.8, def: 0.0 }
        ]
      },
      "2021-11": {
        hist_label: "74/20",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 21.1, temp_cur: 21.0, prec_hist: 105.8, prec_cur: 141.2, etp: 89.2,  arm: 7.7,   exc: 0.0,   def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 19.9, temp_cur: 19.3, prec_hist: 203.0, prec_cur: 192.2, etp: 68.4,  arm: 100.0, exc: 123.8, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 22.5, temp_cur: 22.7, prec_hist: 196.2, prec_cur: 113.4, etp: 101.9, arm: 83.3,  exc: 1.9,   def: 0.0 },
          { city: "muzambinho",     sup: null, temp_hist: 20.9, temp_cur: 20.3, prec_hist: 185.9, prec_cur: 138.0, etp: 76.8,  arm: 100.0, exc: 61.2,  def: 0.0 }
        ]
      },
      "2021-12": {
        hist_label: "74/20",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 22.3, temp_cur: 21.2, prec_hist: 258.3, prec_cur: 303.0, etp: 90.6,  arm: 100.0, exc: 120.1, def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 21.2, temp_cur: 19.3, prec_hist: 223.5, prec_cur: 372.0, etp: 71.6,  arm: 100.0, exc: 300.4, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 23.3, temp_cur: 22.4, prec_hist: 224.3, prec_cur: 268.2, etp: 103.7, arm: 100.0, exc: 147.8, def: 0.0 },
          { city: "muzambinho",     sup: null, temp_hist: 21.5, temp_cur: 20.8, prec_hist: 246.1, prec_cur: 305.0, etp: 86.1,  arm: 100.0, exc: 218.9, def: 0.0 }
        ]
      },
      "2022-07": {
        hist_label: "74/21",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 16.4, temp_cur: 17.0, prec_hist: 16.9, prec_cur: 0.0, etp: 43.2, arm: 0.0, exc: 0.0, def: 61.3 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 15.6, temp_cur: 16.2, prec_hist: 23.7, prec_cur: 1.8, etp: 38.2, arm: 0.0, exc: 0.0, def: 5.8 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 17.7, temp_cur: 18.4, prec_hist: 10.2, prec_cur: 0.6, etp: 52.4, arm: 0.0, exc: 0.0, def: 142.8 },
          { city: "muzambinho",     sup: null, temp_hist: 15.8, temp_cur: 16.5, prec_hist: 13.6, prec_cur: 0.0, etp: 39.8, arm: 0.0, exc: 0.0, def: 30.9 }
        ]
      },
      "2022-08": {
        hist_label: "74/21",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 18.4, temp_cur: 18.4, prec_hist: 19.2, prec_cur: 18.4, etp: 54.8, arm: 0.0, exc: 0.0, def: 97.7 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 17.0, temp_cur: 16.5, prec_hist: 18.7, prec_cur: 21.8, etp: 41.0, arm: 0.0, exc: 0.0, def: 25.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 19.3, temp_cur: 19.1, prec_hist: 10.3, prec_cur: 23.0, etp: 58.9, arm: 0.0, exc: 0.0, def: 178.7 },
          { city: "muzambinho",     sup: null, temp_hist: 17.4, temp_cur: 16.5, prec_hist: 20.3, prec_cur: 13.0, etp: 41.7, arm: 0.0, exc: 0.0, def: 59.6 }
        ]
      },
      "2022-09": {
        hist_label: "74/21",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 20.3, temp_cur: 19.9, prec_hist: 70.8, prec_cur: 110.6, etp: 66.3, arm: 0.0,  exc: 0.0, def: 53.4 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 19.3, temp_cur: 18.4, prec_hist: 67.8, prec_cur: 127.6, etp: 55.1, arm: 47.5, exc: 0.0, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 22.2, temp_cur: 21.0, prec_hist: 47.3, prec_cur: 65.6,  etp: 76.2, arm: 0.0,  exc: 0.0, def: 189.3 },
          { city: "muzambinho",     sup: null, temp_hist: 20.6, temp_cur: 19.2, prec_hist: 69.6, prec_cur: 69.0,  etp: 61.4, arm: 0.0,  exc: 0.0, def: 52.0 }
        ]
      },
      "2022-10": {
        hist_label: "74/21",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 21.1, temp_cur: 21.7, prec_hist: 104.0, prec_cur: 109.6, etp: 90.3,  arm: 0.0,  exc: 0.0, def: 34.1 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 20.0, temp_cur: 20.0, prec_hist: 124.0, prec_cur: 121.0, etp: 74.0,  arm: 94.5, exc: 0.0, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 23.0, temp_cur: 23.0, prec_hist: 107.7, prec_cur: 139.0, etp: 103.4, arm: 0.0,  exc: 0.0, def: 153.7 },
          { city: "muzambinho",     sup: null, temp_hist: 21.4, temp_cur: 21.5, prec_hist: 146.7, prec_cur: 157.0, etp: 87.8,  arm: 17.2, exc: 0.0, def: 0.0 }
        ]
      },
      "2022-11": {
        hist_label: "74/21",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 21.9, temp_cur: 20.0, prec_hist: 173.3, prec_cur: 104.2, etp: 75.3, arm: 0.0,   exc: 0.0,  def: 5.2 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 19.8, temp_cur: 17.7, prec_hist: 202.1, prec_cur: 136.8, etp: 55.3, arm: 100.0, exc: 76.0, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 22.5, temp_cur: 21.0, prec_hist: 189.3, prec_cur: 153.2, etp: 85.7, arm: 0.0,   exc: 0.0,  def: 86.2 },
          { city: "muzambinho",     sup: null, temp_hist: 20.8, temp_cur: 19.2, prec_hist: 180.6, prec_cur: 210.0, etp: 67.5, arm: 100.0, exc: 59.7, def: 0.0 }
        ]
      },
      "2022-12": {
        hist_label: "74/21",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 22.2, temp_cur: 20.9, prec_hist: 253.3, prec_cur: 381.4, etp: 87.3,  arm: 100.0, exc: 188.9, def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 21.0, temp_cur: 18.6, prec_hist: 235.9, prec_cur: 579.4, etp: 65.5,  arm: 98.4,  exc: 515.5, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 23.2, temp_cur: 22.7, prec_hist: 228.0, prec_cur: 375.0, etp: 106.8, arm: 100.0, exc: 82.0,  def: 0.0 },
          { city: "muzambinho",     sup: null, temp_hist: 21.4, temp_cur: 20.6, prec_hist: 252.7, prec_cur: 447.0, etp: 84.3,  arm: 100.0, exc: 362.7, def: 0.0 }
        ]
      },
      // 2021 reports: baseline 74/20; 4th city Muzambinho.
      "2021-01": {
        hist_label: "74/20",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 22.5, temp_cur: 23.0, prec_hist: 266.2, prec_cur: 270.6, etp: 110.0, arm: 39.9,  exc: 212.9, def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 21.5, temp_cur: 21.3, prec_hist: 281.7, prec_cur: 175.2, etp: 90.7,  arm: 100.0, exc: 81.5,  def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 23.6, temp_cur: 24.1, prec_hist: 212.2, prec_cur: 163.2, etp: 123.5, arm: 0.0,   exc: 0.0,   def: 22.3 },
          { city: "muzambinho",     sup: null, temp_hist: 22.0, temp_cur: 21.8, prec_hist: 221.5, prec_cur: 189.4, etp: 95.9,  arm: 43.6,  exc: 132.1, def: 0.0 }
        ]
      },
      "2021-02": {
        hist_label: "74/20",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 22.7, temp_cur: 21.7, prec_hist: 187.1, prec_cur: 218.4, etp: 83.8, arm: 97.5, exc: 77.0,  def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 21.5, temp_cur: 19.8, prec_hist: 160.0, prec_cur: 275.5, etp: 66.7, arm: 97.9, exc: 210.9, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 23.7, temp_cur: 22.7, prec_hist: 146.4, prec_cur: 288.8, etp: 93.4, arm: 96.8, exc: 76.3,  def: 0.0 },
          { city: "muzambinho",     sup: null, temp_hist: 21.6, temp_cur: 21.0, prec_hist: 248.5, prec_cur: 236.8, etp: 76.8, arm: 97.6, exc: 106.1, def: 0.0 }
        ]
      },
      "2023-05": {
        hist_label: "74/22",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 17.9, temp_cur: 17.8, prec_hist: 49.4, prec_cur: 17.6, etp: 49.2, arm: 44.8, exc: 0.0, def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 16.6, temp_cur: 15.5, prec_hist: 42.9, prec_cur: 41.0, etp: 35.8, arm: 89.1, exc: 0.0, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 19.0, temp_cur: 18.7, prec_hist: 41.9, prec_cur: 10.6, etp: 56.1, arm: 0.0,  exc: 0.0, def: 2.0 },
          { city: "muzambinho",     sup: null, temp_hist: 17.0, temp_cur: 16.9, prec_hist: 51.2, prec_cur: 19.0, etp: 43.4, arm: 66.9, exc: 0.0, def: 0.0 }
        ]
      },
      "2023-06": {
        hist_label: "74/22",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 16.8, temp_cur: 16.4, prec_hist: 33.3, prec_cur: 22.4, etp: 37.9, arm: 29.3, exc: 0.0,  def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 16.0, temp_cur: 14.4, prec_hist: 33.7, prec_cur: 36.4, etp: 27.3, arm: 87.0, exc: 11.1, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 17.9, temp_cur: 17.2, prec_hist: 27.4, prec_cur: 18.4, etp: 42.7, arm: 0.0,  exc: 0.0,  def: 26.3 },
          { city: "muzambinho",     sup: null, temp_hist: 16.7, temp_cur: 15.3, prec_hist: 27.8, prec_cur: 51.0, etp: 32.3, arm: 83.3, exc: 2.4,  def: 0.0 }
        ]
      },
      "2023-07": {
        hist_label: "74/22",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 16.4, temp_cur: 17.2, prec_hist: 16.2, prec_cur: 16.6, etp: 44.0, arm: 1.9,  exc: 0.0, def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 15.7, temp_cur: 14.9, prec_hist: 22.0, prec_cur: 9.4,  etp: 31.1, arm: 65.3, exc: 0.0, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 17.7, temp_cur: 18.3, prec_hist: 9.5,  prec_cur: 4.4,  etp: 52.0, arm: 0.0,  exc: 0.0, def: 73.9 },
          { city: "muzambinho",     sup: null, temp_hist: 15.8, temp_cur: 16.0, prec_hist: 12.2, prec_cur: 9.0,  etp: 37.5, arm: 54.8, exc: 0.0, def: 0.0 }
        ]
      },
      "2023-08": {
        hist_label: "74/22",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 18.4, temp_cur: 19.6, prec_hist: 18.8, prec_cur: 30.0, etp: 62.7, arm: 0.0,  exc: 0.0, def: 30.8 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 17.0, temp_cur: 18.0, prec_hist: 18.9, prec_cur: 20.0, etp: 51.7, arm: 33.6, exc: 0.0, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 19.3, temp_cur: 20.5, prec_hist: 11.3, prec_cur: 27.2, etp: 70.6, arm: 0.0,  exc: 0.0, def: 117.3 },
          { city: "muzambinho",     sup: null, temp_hist: 17.3, temp_cur: 18.5, prec_hist: 19.6, prec_cur: 23.0, etp: 55.0, arm: 22.8, exc: 0.0, def: 0.0 }
        ]
      },
      "2023-09": {
        hist_label: "74/22",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 20.3, temp_cur: 23.3, prec_hist: 71.8, prec_cur: 17.2, etp: 98.5,  arm: 0.0,  exc: 0.0, def: 112.1 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 19.2, temp_cur: 20.2, prec_hist: 72.4, prec_cur: 32.4, etp: 51.7,  arm: 14.3, exc: 0.0, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 22.1, temp_cur: 24.6, prec_hist: 48.7, prec_cur: 13.0, etp: 112.5, arm: 0.0,  exc: 0.0, def: 216.8 },
          { city: "muzambinho",     sup: null, temp_hist: 20.5, temp_cur: 22.8, prec_hist: 69.6, prec_cur: 29.0, etp: 95.0,  arm: 0.0,  exc: 0.0, def: 43.2 }
        ]
      },
      "2023-10": {
        hist_label: "74/22",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 21.1, temp_cur: 23.0, prec_hist: 107.8, prec_cur: 186.6, etp: 103.1, arm: 0.0,   exc: 0.0,   def: 28.6 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 20.0, temp_cur: 20.4, prec_hist: 123.8, prec_cur: 312.2, etp: 77.0,  arm: 100.0, exc: 149.5, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 23.0, temp_cur: 24.6, prec_hist: 110.1, prec_cur: 185.0, etp: 122.0, arm: 0.0,   exc: 0.0,   def: 153.8 },
          { city: "muzambinho",     sup: null, temp_hist: 21.4, temp_cur: 23.2, prec_hist: 147.7, prec_cur: 278.0, etp: 106.4, arm: 96.0,  exc: 32.4,  def: 0.0 }
        ]
      },
      "2023-11": {
        hist_label: "74/22",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 21.9, temp_cur: 23.9, prec_hist: 174.3, prec_cur: 167.2, etp: 117.0, arm: 21.6,  exc: 0.0,   def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 19.7, temp_cur: 21.3, prec_hist: 197.0, prec_cur: 202.6, etp: 87.6,  arm: 100.0, exc: 115.0, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 22.4, temp_cur: 25.5, prec_hist: 186.5, prec_cur: 53.2,  etp: 136.3, arm: 0.0,   exc: 0.0,   def: 236.9 },
          { city: "muzambinho",     sup: null, temp_hist: 20.7, temp_cur: 22.7, prec_hist: 183.6, prec_cur: 256.0, etp: 101.1, arm: 93.6,  exc: 157.4, def: 0.0 }
        ]
      },
      // 2025 reports: baseline 74/24 (1974–2024) and the 4th city is MUZAMBINHO
      // (Guapé replaces it from the 2026 reports on).
      "2025-01": {
        hist_label: "74/24",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 22.5, temp_cur: 22.8, prec_hist: 273.1, prec_cur: 265.4, etp: 107.2, arm: 100.0, exc: 158.2, def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 21.2, temp_cur: 20.3, prec_hist: 295.3, prec_cur: 360.0, etp: 80.4,  arm: 100.0, exc: 279.6, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 23.6, temp_cur: 23.8, prec_hist: 239.4, prec_cur: 163.2, etp: 119.5, arm: 100.0, exc: 43.7,  def: 0.0 },
          { city: "muzambinho",     sup: null, temp_hist: 21.9, temp_cur: 22.6, prec_hist: 249.8, prec_cur: 235.0, etp: 106.1, arm: 100.0, exc: 123.1, def: 0.0 }
        ]
      },
      "2025-02": {
        hist_label: "74/24",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 22.7, temp_cur: 23.9, prec_hist: 189.3, prec_cur: 74.4,  etp: 105.7, arm: 10.3, exc: 58.3,  def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 21.3, temp_cur: 21.2, prec_hist: 178.0, prec_cur: 150.4, etp: 78.3,  arm: 76.0, exc: 96.1,  def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 23.6, temp_cur: 25.2, prec_hist: 161.1, prec_cur: 50.2,  etp: 120.6, arm: 0.3,  exc: 29.3,  def: 0.0 },
          { city: "muzambinho",     sup: null, temp_hist: 21.4, temp_cur: 23.0, prec_hist: 251.8, prec_cur: 119.0, etp: 96.0,  arm: 20.6, exc: 102.3, def: 0.0 }
        ]
      },
      "2025-05": {
        hist_label: "74/24",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 18.0, temp_cur: 18.3, prec_hist: 48.1, prec_cur: 0.0,  etp: 52.5, arm: 0.0,  exc: 0.0, def: 11.9 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 16.6, temp_cur: 15.6, prec_hist: 42.0, prec_cur: 0.0,  etp: 35.3, arm: 61.7, exc: 0.0, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 19.2, temp_cur: 19.6, prec_hist: 37.8, prec_cur: 0.0,  etp: 62.1, arm: 21.2, exc: 0.0, def: 0.0 },
          { city: "muzambinho",     sup: null, temp_hist: 17.2, temp_cur: 17.1, prec_hist: 46.9, prec_cur: 33.0, etp: 45.1, arm: 72.9, exc: 6.8, def: 0.0 }
        ]
      },
      "2025-06": {
        hist_label: "74/24",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 16.8, temp_cur: 16.6, prec_hist: 32.4, prec_cur: 31.4, etp: 38.9, arm: 0.0,  exc: 0.0, def: 19.4 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 15.9, temp_cur: 14.3, prec_hist: 31.6, prec_cur: 30.0, etp: 27.1, arm: 64.6, exc: 0.0, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 17.9, temp_cur: 17.9, prec_hist: 25.1, prec_cur: 20.6, etp: 47.5, arm: 0.0,  exc: 0.0, def: 5.7 },
          { city: "muzambinho",     sup: null, temp_hist: 16.6, temp_cur: 16.4, prec_hist: 27.4, prec_cur: 46.0, etp: 37.9, arm: 81.0, exc: 0.0, def: 0.0 }
        ]
      },
      "2025-07": {
        hist_label: "74/24",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 16.5, temp_cur: 16.3, prec_hist: 16.0, prec_cur: 21.8, etp: 39.2, arm: 0.0,  exc: 0.0, def: 36.8 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 15.6, temp_cur: 14.0, prec_hist: 20.9, prec_cur: 5.0,  etp: 26.7, arm: 42.9, exc: 0.0, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 17.9, temp_cur: 17.6, prec_hist: 8.5,  prec_cur: 2.4,  etp: 46.8, arm: 0.0,  exc: 0.0, def: 50.1 },
          { city: "muzambinho",     sup: null, temp_hist: 16.0, temp_cur: 15.9, prec_hist: 11.7, prec_cur: 16.0, etp: 34.5, arm: 62.5, exc: 0.0, def: 0.0 }
        ]
      },
      "2025-08": {
        hist_label: "74/24",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 18.5, temp_cur: 19.1, prec_hist: 18.7, prec_cur: 3.6,  etp: 60.2, arm: 0.0,  exc: 0.0, def: 93.4 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 17.0, temp_cur: 15.4, prec_hist: 19.7, prec_cur: 19.8, etp: 35.7, arm: 27.0, exc: 0.0, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 19.4, temp_cur: 19.2, prec_hist: 11.6, prec_cur: 5.4,  etp: 60.7, arm: 0.0,  exc: 0.0, def: 105.4 },
          { city: "muzambinho",     sup: null, temp_hist: 17.5, temp_cur: 16.7, prec_hist: 18.5, prec_cur: 7.0,  etp: 43.4, arm: 26.1, exc: 0.0, def: 0.0 }
        ]
      },
      "2025-09": {
        hist_label: "74/24",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 20.4, temp_cur: 21.6, prec_hist: 69.7, prec_cur: 27.2, etp: 81.2, arm: 0.0,  exc: 0.0, def: 147.4 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 19.4, temp_cur: 17.6, prec_hist: 65.2, prec_cur: 56.4, etp: 49.5, arm: 33.9, exc: 0.0, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 22.4, temp_cur: 21.9, prec_hist: 45.4, prec_cur: 23.8, etp: 84.8, arm: 0.0,  exc: 0.0, def: 166.4 },
          { city: "guape",          sup: 4,    temp_hist: 23.5, temp_cur: 22.6, prec_hist: 53.2, prec_cur: 21.4, etp: 90.9, arm: 0.0,  exc: 0.0, def: 291.0 }
        ]
      },
      "2025-10": {
        hist_label: "74/24",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 21.2, temp_cur: 22.0, prec_hist: 111.6, prec_cur: 77.8,  etp: 92.9,  arm: 0.0,   exc: 0.0,  def: 162.5 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 20.1, temp_cur: 18.1, prec_hist: 146.8, prec_cur: 134.4, etp: 35.7,  arm: 100.0, exc: 32.6, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 23.2, temp_cur: 22.5, prec_hist: 122.9, prec_cur: 42.2,  etp: 97.7,  arm: 0.0,   exc: 0.0,  def: 221.9 },
          { city: "guape",          sup: 4,    temp_hist: 24.0, temp_cur: 23.0, prec_hist: 150.8, prec_cur: 71.0,  etp: 103.2, arm: 0.0,   exc: 0.0,  def: 323.2 }
        ]
      },
      "2025-11": {
        hist_label: "74/24",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 21.9, temp_cur: 22.0, prec_hist: 175.1, prec_cur: 254.8, etp: 94.1,  arm: 0.0,  exc: 0.0,  def: 1.8 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 19.8, temp_cur: 18.8, prec_hist: 202.5, prec_cur: 121.0, etp: 63.3,  arm: 84.5, exc: 73.2, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 22.6, temp_cur: 22.9, prec_hist: 178.3, prec_cur: 147.4, etp: 97.7,  arm: 0.0,  exc: 0.0,  def: 172.2 },
          { city: "guape",          sup: 4,    temp_hist: 23.4, temp_cur: 23.3, prec_hist: 186.9, prec_cur: 175.6, etp: 108.1, arm: 0.0,  exc: 0.0,  def: 255.7 }
        ]
      },
      "2025-12": {
        hist_label: "74/24",
        rows: [
          { city: "varginha",       sup: null, temp_hist: 22.2, temp_cur: 23.9, prec_hist: 260.6, prec_cur: 245.4, etp: 122.0, arm: 82.4,  exc: 39.2,  def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 20.8, temp_cur: 20.6, prec_hist: 271.2, prec_cur: 327.8, etp: 84.1,  arm: 100.0, exc: 228.2, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 23.4, temp_cur: 24.3, prec_hist: 242.4, prec_cur: 247.8, etp: 127.5, arm: 0.0,   exc: 0.0,   def: 51.9 },
          { city: "guape",          sup: 4,    temp_hist: 23.9, temp_cur: 24.6, prec_hist: 253.3, prec_cur: 189.0, etp: 130.6, arm: 0.0,   exc: 0.0,   def: 197.3 }
        ]
      },
      "2026-01": {
        rows: [
          { city: "varginha",       sup: null, temp_hist: 22.5, temp_cur: 22.0, prec_hist: 273.0, prec_cur: 300.4, etp: 99.1,  arm: 96.3,  exc: 187.4, def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 21.1, temp_cur: 19.0, prec_hist: 299.3, prec_cur: 426.0, etp: 69.1,  arm: 100.0, exc: 356.9, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 23.6, temp_cur: 22.4, prec_hist: 234.7, prec_cur: 285.6, etp: 103.5, arm: 96.7,  exc: 85.4,  def: 0.0 },
          { city: "guape",          sup: 4,    temp_hist: 24.1, temp_cur: 23.0, prec_hist: 218.6, prec_cur: 244.4, etp: 109.9, arm: 95.9,  exc: 38.7,  def: 0.0 }
        ]
      },
      "2026-02": {
        rows: [
          { city: "varginha",       sup: null, temp_hist: 22.7, temp_cur: 23.1, prec_hist: 187.1, prec_cur: 230.4, etp: 97.9,  arm: 92.1, exc: 136.7, def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 21.2, temp_cur: 20.1, prec_hist: 176.2, prec_cur: 264.0, etp: 68.7,  arm: 97.6, exc: 197.6, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 23.7, temp_cur: 23.5, prec_hist: 154.2, prec_cur: 167.4, etp: 101.6, arm: 69.8, exc: 92.7,  def: 0.0 },
          { city: "guape",          sup: 4,    temp_hist: 23.9, temp_cur: 24.1, prec_hist: 184.4, prec_cur: 156.2, etp: 107.7, arm: 44.3, exc: 100.1, def: 0.0 }
        ]
      },
      "2026-03": {
        rows: [
          { city: "varginha",       sup: null, temp_hist: 22.2, temp_cur: 22.9, prec_hist: 168.2, prec_cur: 155.8, etp: 100.9, arm: 72.6, exc: 74.3,  def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 20.6, temp_cur: 19.5, prec_hist: 159.8, prec_cur: 266.4, etp: 68.0,  arm: 91.6, exc: 204.4, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 23.3, temp_cur: 23.5, prec_hist: 144.6, prec_cur: 202.2, etp: 107.6, arm: 75.0, exc: 89.4,  def: 0.0 },
          { city: "guape",          sup: 4,    temp_hist: 23.8, temp_cur: 23.8, prec_hist: 122.0, prec_cur: 206.8, etp: 110.7, arm: 61.8, exc: 78.6,  def: 0.0 }
        ]
      },
      "2026-04": {
        rows: [
          { city: "varginha",       sup: null, temp_hist: 20.8, temp_cur: 21.6, prec_hist: 73.1, prec_cur: 34.6, etp: 80.4, arm: 26.8, exc: 0.0,  def: 0.0 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 19.0, temp_cur: 18.7, prec_hist: 63.6, prec_cur: 77.0, etp: 56.2, arm: 62.8, exc: 49.6, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 21.9, temp_cur: 22.3, prec_hist: 58.9, prec_cur: 18.6, etp: 87.0, arm: 6.6,  exc: 0.0,  def: 0.0 },
          { city: "guape",          sup: 4,    temp_hist: 22.5, temp_cur: 22.8, prec_hist: 46.4, prec_cur: 52.4, etp: 91.5, arm: 22.7, exc: 0.0,  def: 0.0 }
        ]
      },
      "2026-05": {
        rows: [
          { city: "varginha",       sup: null, temp_hist: 18.0, temp_cur: 20.0, prec_hist: 47.1, prec_cur: 18.8, etp: 66.0, arm: 0.0,  exc: 0.0, def: 20.4 },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 16.5, temp_cur: 17.0, prec_hist: 39.4, prec_cur: 65.2, etp: 44.0, arm: 84.0, exc: 0.0, def: 0.0 },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 19.2, temp_cur: 20.5, prec_hist: 35.4, prec_cur: 17.8, etp: 69.8, arm: 0.0,  exc: 0.0, def: 45.4 },
          { city: "guape",          sup: 4,    temp_hist: 19.9, temp_cur: 21.5, prec_hist: 37.9, prec_cur: 36.8, etp: 78.3, arm: 0.0,  exc: 0.0, def: 18.8 }
        ]
      },
      "2026-06": {
        rows: [
          { city: "varginha",       sup: null, temp_hist: 16.8, temp_cur: 17.1, prec_hist: 32.4, prec_cur: 74.6,  etp: 42.0, arm: 12.2, exc: 0.0,  def: 0.0  },
          { city: "carmo_de_minas", sup: 3,    temp_hist: 15.8, temp_cur: 14.4, prec_hist: 31.5, prec_cur: 112.6, etp: 27.3, arm: 97.2, exc: 72.1, def: 0.0  },
          { city: "boa_esperanca",  sup: 3,    temp_hist: 17.9, temp_cur: 17.4, prec_hist: 24.8, prec_cur: 66.3,  etp: 44.0, arm: 0.0,  exc: 0.0,  def: 23.1 },
          { city: "guape",          sup: 4,    temp_hist: 18.7, temp_cur: 18.5, prec_hist: 13.3, prec_cur: 55.4,  etp: 50.9, arm: 0.0,  exc: 0.0,  def: 14.3 }
        ]
      }
    }
  },

  // Per-city graph data. Baseline = red, then one color per year.
  // temp/precip/water arrays are Jan..Dec (12). Current-year arrays may be
  // shorter (data only up to the latest available month).
  graphs: {
    estimated: true,
    baseline_years: "1974 a 2025",   // shown in baseline legends
    cities: {
      varginha: {
        // Mean temperature (°C)
        temp: {
          baseline: [22.6, 22.7, 22.1, 20.4, 18.1, 16.8, 16.4, 18.3, 20.4, 21.4, 21.9, 22.2],
          "2025":   [22.9, 23.9, 23.2, 20.6, 17.6, 16.6, 16.5, 18.0, 21.7, 22.1, 22.1, 23.9],
          "2026":   [22.8, 23.0, 23.0, 21.5, 19.8, 17.1]
        },
        // Monthly rainfall (mm) — accumulated chart is derived from this
        precip: {
          baseline: [270, 188, 165, 78, 45, 32, 20, 18, 55, 118, 190, 255],
          "2025":   [265, 75, 100, 100, 15, 28, 12, 6, 78, 60, 200, 255],
          "2026":   [300, 200, 155, 30, 18, 74.6]
        },
        // Soil water availability (mm), Thornthwaite & Mather
        // ⚠ source chart is daily & very jagged — this is a MONTHLY approximation
        water: {
          baseline: [120, 110, 80, 55, 45, 50, 40, 5, -25, -20, 40, 95],
          "2025":   [110, 85, -10, 5, 10, -10, -45, -120, -155, -165, -80, 120],
          "2026":   [95, 150, 70, 5, -25, -15, 10]
        }
      }
      // carmo_de_minas, boa_esperanca, guape : pending (send their charts)
    }
  }
};
