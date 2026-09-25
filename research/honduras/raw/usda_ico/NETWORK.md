# Network reachability — usda_ico environment

Date (UTC): 2026-09-25 23:43:04. One request each, curl -L -m 60 -A Mozilla/5.0.

| URL | result |
|---|---|
| https://ihcafe.hn/ | 200  |
| https://www.ihcafe.hn/ | 000 curl: (56) CONNECT tunnel failed, response 403  |
| https://www.ico.org/ | 000 curl: (56) CONNECT tunnel failed, response 403  |
| https://ico.org/ | 200  |
| https://apps.fas.usda.gov/psdonline/app/index.html | 200  |
| https://fas.usda.gov/ | 000 curl: (56) CONNECT tunnel failed, response 403  |
| https://www.fas.usda.gov/ | 000 curl: (56) CONNECT tunnel failed, response 403  |
| https://perfectdailygrind.com/ | 000 curl: (56) CONNECT tunnel failed, response 403  |
| https://www.bch.hn/ | 000 curl: (56) CONNECT tunnel failed, response 403  |
| https://temp.ine.gob.hn/ | 000 curl: (56) CONNECT tunnel failed, response 403  |
| https://sag.gob.hn/ | 000 curl: (56) CONNECT tunnel failed, response 403  |
| https://tnh.gob.hn/ | 000 curl: (56) CONNECT tunnel failed, response 403  |
| https://exportadoresdecafe.com/ | 000 curl: (56) CONNECT tunnel failed, response 403  |
| https://www.latribuna.hn/ | 000 curl: (56) CONNECT tunnel failed, response 403  |
| https://icocoffee.org/ | 000 curl: (56) CONNECT tunnel failed, response 403  |
| https://www.icocoffee.org/ | 000 curl: (56) CONNECT tunnel failed, response 403  |

Reachable: ihcafe.hn, ico.org (no www), apps.fas.usda.gov. All others blocked by the egress proxy (CONNECT 403).
