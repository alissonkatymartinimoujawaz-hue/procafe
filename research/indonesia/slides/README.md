# Slides

`Indonesia_robusta_weather_ENSO.pptx`: 13 slides in the house format (production and ENSO, yield by ENSO phase, monthly weather anomalies, temperature and rainfall panels by town, year-on-year by coffee year, rainfall check against GPCC gauges, ENSO and IOD).

Rebuild with `python3 build_deck.py` (standard library only). It reads `../weather_data.js` and `deck_series.json` (5-town June–October rainfall, NASA POWER and GPCC). `ooxml.py` writes the PPTX with native charts; `preview.py deck.pptx out.html` gives a rough HTML preview.
