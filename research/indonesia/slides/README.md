# Slides

`Indonesia_robusta_weather_ENSO.pptx`: 14 slides in the house format (production and ENSO, yield by ENSO phase, monthly weather anomalies, temperature and rainfall panels by town, year-on-year by coffee year, rainfall check against GPCC gauges, ENSO and IOD).

`Indonesia_robusta_2027_forecast_chain.pptx`: 15 slides, the 2027/28 forecast chain with the proof for each link. Area: coffee vs cocoa area and revenue per hectare year over year, whether they move together, what moves the robusta area, which links are real, the 2027 productive area. Yield: a normal flowering year, 18 weather factors tested on 45 USDA crops, thresholds, heat and ENSO, on/off years, the 2026 flowering season against a normal year, and the 2027/28 calculation with normal weather after 19 September 2026.

Rebuild with `python3 build_deck.py` and `python3 build_proof_deck.py` (standard library only). `build_deck.py` reads `../weather_data.js` and `deck_series.json` (5-town June–October rainfall, NASA POWER and GPCC). `build_proof_deck.py` reads `proof_series.json` (FAOSTAT, ministry, USDA and NASA POWER series; its `note` field gives the sources and definitions), `../forecast_dataset.csv` and `../weather_data.js`. `ooxml.py` writes the PPTX with native charts; `preview.py deck.pptx out.html` gives a rough HTML preview.
