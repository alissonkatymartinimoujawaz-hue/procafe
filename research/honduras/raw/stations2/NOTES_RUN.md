# stations2: run notes (2026-09-25, environment Honduras)

Command: `python3 research/common/fetch_hn_stations.py research/honduras/raw/stations2` (log of every request in `FETCH_LOG.md` / `fetch_log.jsonl`).

- **NOAA ISD/GSOD**: OK. Daily files for 787170 Santa Rosa de Copán, 787180 Nueva Ocotepeque, 787190 La Esperanza, 787210 Palmerola (Comayagua). 787185 returned no years (404s).
- **GHCN-Daily**: only HO000078714 (Catacamas) within the station list's reach.
- **CHIRPS (IRI Data Library)**: host reachable, but every request is redirected (HTTP 302) to the IRIDL login page (`dlauth`), so the script saved HTML instead of data. Those three files were deleted. Five URL variants were tried by hand (0p05 `daily-improved` with the table:/text export; 0p05 `daily`; 0p25 `daily-improved`; 0p25 `daily`; monthly): all 302 to login. **No CHIRPS data.** A free IRIDL account/cookie, or the CHC files on data.chc.ucsb.edu (reachable, but global per-year netCDF files of ~1 GB), would be needed.
- **Open-Meteo**: `era5_land` for all three towns and `era5` for Copán came in on the first run; `era5` for Comayagua and Ocotepeque got HTTP 429 (rate limit). They were re-fetched with `fetch_openmeteo_fixed.py` (same request, date range split in two calls, halves merged): 16 697 days each, 1981-01-01 to 2026-09-18.
