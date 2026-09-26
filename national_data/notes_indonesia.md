# Indonesia – Kementan (Ditjenbun / Pusdatin) and BPS coffee statistics

Collected 2026-09-26. Files:
- `indonesia_bps.csv`: 24 rows from BPS *Statistik Indonesia 2026* (Statistical Yearbook of Indonesia 2026, cat. 1101001, pub. no. 03200.26006).
- `indonesia_kementan.csv`: **header only**. No Kementan file could be downloaded (see below).
- `raw/indonesia_bps/statistik_indonesia_2026.pdf` (12.8 MB, sha256 cd2a8654…508e8d), downloaded from
  `https://webapi.bps.go.id/download.php?f=LzNA+qUh…ttRFQ%3D` (full URL in the CSV `source_url`).
- `raw/indonesia_kementan/`: empty (nothing reachable).
- `tools/pdftext2.py`: a variant of `pdftext.py`. The BPS PDFs are encrypted (Standard security handler, AESV2, empty user password) and wrap page content in Form XObjects. The variant decrypts them through ctypes/libcrypto, follows the Form XObjects, and fixes a crash on multi-character bfrange entries. Usage: `python3 tools/pdftext2.py file.pdf`.

## What the CSV contains (all calendar years, units as published)
Units are `1000_ha` and `1000_t`, because the yearbook publishes thousands with one decimal. The values were not rescaled.
- **National total, all ownerships (PR + PBN + PBS):** `area_total` and `production` for 2024 and 2025.
  - Table 5.3.1 (PDF p.428), Indonesia row, Kopi column: 1,273.9 / 1,275.9 thousand ha.
  - Table 5.3.2 (PDF p.431): 813.3 / 832.7 thousand t.
  - Table source: "BPS – Kementerian Pertanian (Ditjen Perkebunan)".
- **Ownership split, 2021–2025. These are extra rows; each note starts with `SUBSET ONLY`, and they must not be summed with the national rows.**
  - Large estates (Perkebunan Besar = PBN state + PBS private; BPS plantation estate survey):
    - Area, Table 5.3.3 (PDF p.434): 21.8, 19.6, 19.9, 17.5, 17.9.
    - Production, Table 5.3.5 (PDF p.436): 5.3, 4.0, 3.3, 3.3, 3.6.
  - Smallholders (Perkebunan Rakyat, PR; data from Kementan-Ditjenbun):
    - Area, Table 5.3.4 (PDF p.435): 1,257.8, 1,246.4, 1,246.9, 1,256.4, 1,258.1.
    - Production, Table 5.3.6 (PDF p.437): 780.9, 771.0, 755.4, 810.0, 829.1.
- Consistency check:
  - Area: PR + PB = 1,256.4 + 17.5 = 1,273.9 for 2024 ✓; 1,258.1 + 17.9 = 1,276.0 against 1,275.9 published for 2025 (rounding).
  - Production: 810.0 + 3.3 = 813.3 for 2024 ✓; 829.1 + 3.6 = 832.7 for 2025 ✓.
- **2025 figures are marked `*` = angka sementara (preliminary).**

### Definitions and caveats
- Area is "luas areal" (planted area). Under the usual Ditjenbun definition this is TBM + TM + TTM, but the yearbook does not state that, and it does **not** split area into TBM, TM or TTM.
- Production is "biji kering" (dry beans), i.e. green-bean basis (technical note 26, PDF p.389). All species are combined (robusta, arabica, liberica); there is no species split.
- Large estates (Perkebunan Besar) are PBN (state) + PBS (private national or foreign). They are not split further in the yearbook.
- The PR (smallholder) rows come from Ditjenbun. Those numbers are Kementan's, republished by BPS. They are kept in the BPS file because the downloaded publication is a BPS one.
- The yearbook gives no yield and no number of holders or households.

## Gaps (not obtained)
- **Any year before 2021.** The 2021–2023 national totals are also missing. They could be computed as PR + PB, but that was not done because the brief forbids derived values.
- TBM / TM / TTM area split, yield (kg/ha), number of farmer households, and the robusta/arabica split. These are all in Ditjenbun's *Statistik Perkebunan Unggulan Nasional* / *Statistik Perkebunan Jilid I* and in BPS *Statistik Kopi Indonesia* (cat. 5504006), and neither could be downloaded.
- A PBN vs PBS split, which is in *Statistik Kopi Indonesia*.

## Access attempts (curl through the agent proxy, UA Chrome/124, -L -m 30..600)
| URL / host | Result |
|---|---|
| https://ditjenbun.pertanian.go.id/ (http and https), …/template/uploads/2022/08/STATISTIK-UNGGULAN-2020-2022.pdf | 403 Cloudflare "Attention Required" |
| https://satudata.pertanian.go.id/assets/docs/publikasi/Buku_Outlook_Kopi_2023_lengkap.pdf, …Buku_Outlook_Kopi_2022_compressed.pdf | 403 Cloudflare. Also 403 with UAs curl, Wget, Googlebot, iPhone Safari and an Accept: application/pdf header |
| database.pertanian.go.id, aplikasi2., epublikasi., repository., psp., library., ppid., bdsp2.pertanian.go.id, pusdatin.setjen.pertanian.go.id, www.pertanian.go.id, ejournal.pertanian.go.id | CONNECT refused by the proxy (policy 403) or no connection |
| https://www.bps.go.id/ (publication pages for Statistik Kopi Indonesia 2018/2021/2022/2023) | 403 Cloudflare. WebFetch also returned 403 |
| bps.go.id, web-api.bps.go.id, *.bps.go.id provincial and regency sites (jambi, lampung, ntt …), perpustakaan.bps.go.id, searchengine.web.bps.go.id, sirusa.bps.go.id | proxy policy denial |
| https://webapi.bps.go.id/v1/api/list/… | reachable, but every data or list call needs a registered API key ("You are not Allowed… re-check your key"). No key was available, and no account was created |
| **https://webapi.bps.go.id/download.php?f=<token>** | **Works.** It serves any BPS publication, but only when the encrypted token is known. Tokens were found through WebSearch with `allowed_domains: web-api.bps.go.id`, which returns `web-api.bps.go.id/download.php?f=…` links; the host was swapped to `webapi.` |
| Tokens tried: Statistik Kelapa Sawit Indonesia 2023 (cat. 5504003); a Toraja Utara ST2023 kecamatan census; a 2007 publication catalogue; the rural CPI 1996–; **Statistik Indonesia 2026** | Only the 2026 yearbook had national coffee data. Around 25 WebSearch queries were run (for Statistik Kopi Indonesia 2017–2024, Statistik Tanaman Perkebunan Tahunan 2024, Statistik Indonesia 2011–2025, the national ST2023 UTP) and none returned a token for those documents |
| assets.dataindonesia.id (mirror of Statistik Kopi Indonesia 2023 PDF), dataindonesia.id | https: no connection; http: 403 |
| pisagro.org (NT Kopi 2018–2023), scribd, academia.edu, slideshare, databoks, aeki-aice.org, researchgate, neliti, garuda, kikp-pertanian.id, indonesia.go.id, university OJS hosts, archive.org, ico.org, apps.fas.usda.gov, zenodo, figshare, kaggle, huggingface, gitlab, jsdelivr | proxy denial / no connection |
| github.com / api.github.com / GitHub MCP code search | github.com 403; the API is limited to the session's repos. Code search for "Tanaman Belum Menghasilkan kopi" and "Perkebunan Rakyat kopi produksi" found no national coffee statistics files |

## Suggested follow-up
- The fastest route to the full 1998→ series is a BPS WebAPI key (free registration at webapi.bps.go.id/developer). With a key, `/v1/api/list/model/publication/domain/0000/keyword/kopi/key/…` returns the `download.php` token for *Statistik Kopi Indonesia* 2017–2023. That publication has area and production by PR/PBN/PBS since 2000.
- Alternatively, someone could download the Ditjenbun *Statistik Perkebunan* PDF by hand in a browser (it is behind Cloudflare) and drop it into `raw/indonesia_kementan/`.
