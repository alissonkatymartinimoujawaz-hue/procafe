# Honduras

- `excel/Honduras_weather_by_ENSO_season.xlsx`: monthly temperature and rainfall by July–June season for Comayagua, Ocotepeque and Copán (and their mean). It uses the same seasons, months and ENSO classes as the Sumatra file. Rain comes from rain gauges (NOAA CPC daily analysis), because NASA rain reads 30–40 % too wet here after 2020. Temperature comes from NASA POWER. Built by `excel/build_weather_xlsx.py`.
- `excel/Honduras_area_drivers.xlsx`: bearing and non-bearing area, trees and density, production, arabica and fertiliser prices, fertiliser use, land use, labour, an indicative margin, 2011–2013 rust weather, and quotes from the USDA reports. Built by `excel/build_drivers_xlsx.py` from the files in `data/`.
- `raw/`: NASA POWER daily, GPCC monthly, and CPC and GHCN_CAMS station grids (`independent/`). Also FAOSTAT (`faostat/`) and the USDA attaché coffee reports (`usda_gain/`). Each folder has a fetch log.
- Check any workbook with `python3 ../indonesia/excel/verify_xlsx.py <file.xlsx>`. It recomputes every formula and compares the result with the stored value.
