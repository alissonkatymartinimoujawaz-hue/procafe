# Network reachability (ihcafe_docs5)

UTC 2026-09-25 23:26:08. One request each, curl -L -m 30, browser UA.

| URL | HTTP code | final URL / error |
|---|---|---|
| https://ihcafe.hn/ | 000 | https://ihcafe.hn/ curl: (56) CONNECT tunnel failed, response 403 |
| https://www.bch.hn/ | 200 | https://www.bch.hn/  |
| https://perfectdailygrind.com/ | 000 | https://perfectdailygrind.com/ curl: (56) CONNECT tunnel failed, response 403 |
| https://www.ico.org/ | 000 | https://ico.org/ curl: (56) CONNECT tunnel failed, response 403 |
| https://temp.ine.gob.hn/ | 000 | https://temp.ine.gob.hn/ curl: (56) CONNECT tunnel failed, response 403 |
| https://tnh.gob.hn/ | 000 | https://tnh.gob.hn/ curl: (56) CONNECT tunnel failed, response 403 |
| https://sag.gob.hn/ | 000 | https://sag.gob.hn/ curl: (56) CONNECT tunnel failed, response 403 |
| https://www.latribuna.hn/ | 403 | https://www.latribuna.hn/  |
| https://exportadoresdecafe.com/ | 000 | https://exportadoresdecafe.com/ curl: (56) CONNECT tunnel failed, response 403 |
| https://www.hondudiario.com/ | 000 | https://www.hondudiario.com/ curl: (56) CONNECT tunnel failed, response 403 |
| https://icndigital.com/ | 000 | https://icndigital.com/ curl: (56) CONNECT tunnel failed, response 403 |
| https://stonex.digital/ | 000 | https://stonex.digital/ curl: (56) CONNECT tunnel failed, response 403 |
| https://banadesa.hn/ | 403 | https://banadesa.hn/  |
| https://archive-api.open-meteo.com/v1/archive?latitude=14.6&longitude=-87.8&start_date=2026-09-01&end_date=2026-09-02&daily=precipitation_sum&models=era5 | 429 | https://archive-api.open-meteo.com/v1/archive?latitude=14.6&longitude=-87.8&start_date=2026-09-01&end_date=2026-09-02&daily=precipitation_sum&models=era5  |

Follow-up checks (single retry each):
| URL | HTTP code | note |
|---|---|---|
| https://www.ihcafe.hn/?mdocs-file=5360 | 301 | redirects to https://ihcafe.hn/?mdocs-file=5360 (host ihcafe.hn blocked by proxy, CONNECT 403) |
| Open-Meteo test URL (retry) | 200 | returned data (precipitation_sum 8.70, 6.50); first request was 429 |

Steps skipped because host blocked by proxy: 1 (ihcafe.hn), 2 (perfectdailygrind.com), and in 4 all hosts except www.latribuna.hn (site-level 403, tried once).
