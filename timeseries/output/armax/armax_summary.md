# Brazil ARMAX: ON/OFF cycle and weather

Weather source: balance-sheet state weather (Minas Gerais for arabica, Espirito Santo for robusta).

Regression with ARMA errors: X_t = c + b·t + g_on·ON_t + g_rain·RAIN_{t−L} + g_temp·TEMP_{t−L} + u_t, u_t ~ ARMA(p, q). RAIN and TEMP are production-weighted state anomalies (100 mm, °C) around the 1998–2025 mean; the fit uses the crop years with observed weather (1998/1999 – 2025/2026). Selection by AICC over regressor sets, weather lag (0/1) and p, q ≤ 2.

## Production Arabica (1000 60-kg bags)

**ARMAX(0,0) + onoff (weather lag 0) + trend**, fitted on 25 crop years (2001/2002 – 2025/2026). AICc 493.6 (plain ARMA of the same grid: 503.2). Ljung-Box p = 0.95.

| parameter | value | std. error | p-value |
|---|---|---|---|
| c (intercept) | 2.642e+04 | 2.05e+03 | 0.000 |
| b (trend / year) | 618.4 | 112 | 0.000 |
| g_on (ON year, level) | 7443 | 1.69e+03 | 0.000 |
| sigma2 | 1.514e+07 | 6.91e+06 | 0.028 |

Backtest 2023–2025 (MAPE): ARMAX 10.8 % · plain ARMA 12.9 % · naive 8.9 %.

Top 8 candidates by AICc:

| regressors | lag | p | q | trend | AICc |
|---|---|---|---|---|---|
| onoff | 0 | 0 | 0 | ct | 493.6 |
| onoff+rain | 0 | 0 | 0 | ct | 495.5 |
| onoff+temp | 0 | 0 | 0 | ct | 495.8 |
| onoff+temp | 1 | 0 | 0 | ct | 496.1 |
| onoff | 0 | 1 | 0 | ct | 496.6 |
| onoff | 0 | 0 | 1 | ct | 496.7 |
| onoff+rain | 1 | 0 | 0 | ct | 496.7 |
| onoff+rain+temp | 0 | 0 | 0 | ct | 498.9 |

Forecasts (ON/OFF known, weather scenarios; sd rain = 207 mm, sd temp = 0.72 °C):

| crop year | ON/OFF | normal [80 %] | dry-hot | wet-cool |
|---|---|---|---|---|
| 2026/2027 | ON | **49,944** [44,957; 54,930] (USDA in sheet: 47,500) | 49,944 | 49,944 |
| 2027/2028 | OFF | **43,119** [38,132; 48,106] | 43,119 | 43,119 |
| 2028/2029 | ON | **51,180** [46,194; 56,167] | 51,180 | 51,180 |
| 2029/2030 | OFF | **44,356** [39,369; 49,342] | 44,356 | 44,356 |
| 2030/2031 | ON | **52,417** [47,430; 57,404] | 52,417 | 52,417 |
| 2031/2032 | OFF | **45,593** [40,606; 50,579] | 45,593 | 45,593 |

## Production Robusta (1000 60-kg bags)

**ARMA(0,1) + none (weather lag 0) + trend**, fitted on 25 crop years (2001/2002 – 2025/2026). AICc 450.5 (plain ARMA of the same grid: 450.5). Ljung-Box p = 0.55.

| parameter | value | std. error | p-value |
|---|---|---|---|
| c (intercept) | 7813 | 1.31e+03 | 0.000 |
| b (trend / year) | 569.8 | 76.3 | 0.000 |
| ma.L1 | 0.7225 | 0.105 | 0.000 |
| sigma2 | 2.542e+06 | 7.31e+05 | 0.001 |

Backtest 2023–2025 (MAPE): ARMAX 6.1 % · plain ARMA 6.1 % · naive 8.0 %.

Top 8 candidates by AICc:

| regressors | lag | p | q | trend | AICc |
|---|---|---|---|---|---|
| none | 0 | 0 | 1 | ct | 450.5 |
| onoff+temp | 0 | 2 | 0 | ct | 450.9 |
| none | 0 | 1 | 1 | ct | 451.0 |
| none | 0 | 2 | 0 | ct | 451.5 |
| rain+temp | 0 | 2 | 0 | ct | 452.5 |
| none | 0 | 1 | 0 | ct | 452.8 |
| rain+temp | 0 | 1 | 1 | ct | 453.2 |
| onoff+rain | 0 | 2 | 0 | ct | 453.4 |

Forecasts (ON/OFF known, weather scenarios; sd rain = 223 mm, sd temp = 0.63 °C):

| crop year | ON/OFF | normal [80 %] | dry-hot | wet-cool |
|---|---|---|---|---|
| 2026/2027 |  | **24,710** [22,666; 26,753] (USDA in sheet: 24,400) | 24,710 | 24,710 |
| 2027/2028 |  | **23,196** [20,675; 25,717] | 23,196 | 23,196 |
| 2028/2029 |  | **23,766** [21,245; 26,287] | 23,766 | 23,766 |
| 2029/2030 |  | **24,336** [21,815; 26,857] | 24,336 | 24,336 |
| 2030/2031 |  | **24,905** [22,384; 27,426] | 24,905 | 24,905 |
| 2031/2032 |  | **25,475** [22,954; 27,996] | 25,475 | 25,475 |

## Production Total (1000 60-kg bags)

**ARMAX(0,0) + onoff (weather lag 0) + trend**, fitted on 25 crop years (2001/2002 – 2025/2026). AICc 495.0 (plain ARMA of the same grid: 504.8). Ljung-Box p = 0.60.

| parameter | value | std. error | p-value |
|---|---|---|---|
| c (intercept) | 3.423e+04 | 2.23e+03 | 0.000 |
| b (trend / year) | 1178 | 118 | 0.000 |
| g_on (ON year, level) | 7479 | 1.64e+03 | 0.000 |
| sigma2 | 1.589e+07 | 7e+06 | 0.023 |

Backtest 2023–2025 (MAPE): ARMAX 5.4 % · plain ARMA 3.7 % · naive 3.5 %.

Top 8 candidates by AICc:

| regressors | lag | p | q | trend | AICc |
|---|---|---|---|---|---|
| onoff | 0 | 0 | 0 | ct | 495.0 |
| onoff+rain | 0 | 0 | 0 | ct | 496.3 |
| onoff+temp | 0 | 0 | 0 | ct | 496.9 |
| onoff+temp | 1 | 0 | 0 | ct | 497.5 |
| onoff+rain | 1 | 0 | 0 | ct | 498.0 |
| onoff | 0 | 1 | 0 | ct | 498.2 |
| onoff | 0 | 0 | 1 | ct | 498.7 |
| onoff+rain+temp | 0 | 0 | 0 | ct | 499.7 |

Forecasts (ON/OFF known, weather scenarios; sd rain = 180 mm, sd temp = 0.65 °C):

| crop year | ON/OFF | normal [80 %] | dry-hot | wet-cool |
|---|---|---|---|---|
| 2026/2027 | ON | **72,338** [67,230; 77,447] (USDA in sheet: 71,900) | 72,338 | 72,338 |
| 2027/2028 | OFF | **66,038** [60,929; 71,146] | 66,038 | 66,038 |
| 2028/2029 | ON | **74,694** [69,586; 79,803] | 74,694 | 74,694 |
| 2029/2030 | OFF | **68,394** [63,285; 73,502] | 68,394 | 68,394 |
| 2030/2031 | ON | **77,051** [71,942; 82,159] | 77,051 | 77,051 |
| 2031/2032 | OFF | **70,750** [65,641; 75,858] | 70,750 | 70,750 |

## Yield (production / bearing area) (bags/ha)

**ARMAX(0,0) + onoff (weather lag 0) + trend**, fitted on 25 crop years (2001/2002 – 2025/2026). AICc 119.9 (plain ARMA of the same grid: 127.8). Ljung-Box p = 0.54.

| parameter | value | std. error | p-value |
|---|---|---|---|
| c (intercept) | 14.68 | 1.09 | 0.000 |
| b (trend / year) | 0.7024 | 0.0757 | 0.000 |
| g_on (ON year, level) | 3.516 | 1.1 | 0.001 |
| sigma2 | 4.749 | 1.74 | 0.006 |

Backtest 2023–2025 (MAPE): ARMAX 5.7 % · plain ARMA 2.4 % · naive 8.2 %.

Top 8 candidates by AICc:

| regressors | lag | p | q | trend | AICc |
|---|---|---|---|---|---|
| onoff | 0 | 0 | 0 | ct | 119.9 |
| onoff+rain | 0 | 0 | 0 | ct | 122.6 |
| onoff | 0 | 1 | 0 | ct | 122.9 |
| onoff | 0 | 0 | 1 | ct | 122.9 |
| onoff+rain | 1 | 0 | 0 | ct | 123.0 |
| onoff+temp | 1 | 0 | 0 | ct | 123.0 |
| onoff+temp | 0 | 0 | 0 | ct | 123.0 |
| onoff+rain | 1 | 2 | 2 | ct | 124.3 |

Forecasts (ON/OFF known, weather scenarios; sd rain = 180 mm, sd temp = 0.65 °C):

| crop year | ON/OFF | normal [80 %] | dry-hot | wet-cool |
|---|---|---|---|---|
| 2026/2027 | ON | **36.46** [33.67; 39.25] (USDA in sheet: 37.04) | 36.46 | 36.46 |
| 2027/2028 | OFF | **33.65** [30.85; 36.44] | 33.65 | 33.65 |
| 2028/2029 | ON | **37.87** [35.07; 40.66] | 37.87 | 37.87 |
| 2029/2030 | OFF | **35.05** [32.26; 37.85] | 35.05 | 35.05 |
| 2030/2031 | ON | **39.27** [36.48; 42.06] | 39.27 | 39.27 |
| 2031/2032 | OFF | **36.46** [33.66; 39.25] | 36.46 | 36.46 |
