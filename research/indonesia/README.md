# Indonesia robusta research

- `robusta_indonesie.html`: analysis note in French (area, yield, weather, 2027/28 forecast chain). Charts are drawn inline with no external library. Data comes from the ministry table (Ditjenbun, 2004–2023), USDA PSD (July 2026) and the USDA FAS Jakarta coffee reports (2009–2026).
- `south_sumatra_weather.py`: NASA POWER rainfall and temperature for the southern Sumatra robusta towns (Pagar Alam, Lahat, Muaradua, Liwa, Kepahiang), compared with ENSO (ONI), the Indian Ocean Dipole (DMI) and the USDA robusta crop. Standard library only.

```
python research/indonesia/south_sumatra_weather.py            # South Sumatra mean, flowering window Aug-Nov
python research/indonesia/south_sumatra_weather.py --city liwa --window 9-11
```

The script writes `research/indonesia/output/`:
- `south_sumatra_weather.html`: charts
- `monthly_<town>.csv`: monthly rain and temperature for each town
- `crop_vs_weather.csv`: one row per USDA crop year, with the weather of its flowering year

Hosts it needs: `power.larc.nasa.gov`, `www.cpc.ncep.noaa.gov`, `psl.noaa.gov`, `apps.fas.usda.gov`. The Claude cloud environment used for this note could reach only `apps.fas.usda.gov`. To run the script there, allow the other hosts in the environment's Network access settings. They take effect in new sessions.
