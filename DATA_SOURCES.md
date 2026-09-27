# Sources météo : CHIRPS, Open-Meteo, NASA POWER

Tout est en Python standard (aucune installation) sauf l'export Excel/graphiques,
fabriqué par GitHub Actions.

## Ce qui est le plus juste (mesuré contre les stations INMET)

Comparaison 2007–2026 avec 6 stations automatiques INMET des zones caféières de Minas
Gerais (Varginha, Maria da Fé, Passa Quatro, Formiga, Patrocínio, Manhuaçu), chaque
source lue au point exact de la station, plus un second contrôle contre les tableaux
des rapports mensuels du site. Détail : `validation/metrics.json` et l'onglet
*Validation* de l'Excel.

| Variable | Meilleure source | Erreur mensuelle moyenne (6 stations) | Autres |
|---|---|---|---|
| Pluie (mois, année) | **CHIRPS v3** | 21 % (année : 7 %), r = 0,95 ; −3,5 % face aux rapports | NASA 29 % (année 25 %, −27 % face aux rapports) ; Open-Meteo 30 % |
| Température moyenne | **Open-Meteo ERA5-Land** (corrigé à l'altitude) | 0,58 °C, r = 0,97 ; −0,03 °C face aux rapports | NASA 1,02 °C (+0,9 °C, trop chaud) |
| Température minimale | **Open-Meteo + correction INMET** | 0,93 °C (testé station exclue) | NASA 1,11 °C ; Open-Meteo brut 1,48 °C |
| Température maximale | **Open-Meteo + correction INMET** | 0,47 °C (testé station exclue) | NASA 1,30 °C ; Open-Meteo brut 1,85 °C |
| Humidité de l'air | **Open-Meteo ERA5-Land** | 3,2 %, r = 0,88 | NASA 3,7 % |
| Humidité du sol | **Open-Meteo ERA5-Land** (non vérifiable) | — aucune station ne la mesure | NASA GWETROOT (humidité relative, autre unité) |

Les modèles lissent les extrêmes du jour : maximales trop froides (~2 °C), minimales trop
chaudes (~1–2 °C). La correction ajoute, mois par mois, l'écart moyen mesuré aux 6 stations
(tableau dans l'onglet *Validation*) ; testée en excluant chaque fois la station évaluée.

## CHIRPS v3 — `chirps.py`

* CHIRPS v2 s'arrête fin 2026 : on lit **v3.0** directement sur
  `data.chc.ucsb.edu` (fichiers « latam » : mensuel, décadaire, pentades préliminaires).
* Lecture ciblée par requêtes HTTP Range : seules les lignes de pixels des villes sont
  téléchargées (~0,3 Mo par fichier au lieu de 4 Mo).
* Le serveur coupe les requêtes « multi-plages » et les rafales de connexions :
  le lecteur utilise des plages simples sur une connexion persistante.
* Définitif ~3e semaine du mois suivant ; préliminaire ~2 jours après chaque pentade.
* Cache : `cache/chirps/`.

```python
import chirps
pluie, info = chirps.months_at({"varginha": (-21.5667, -45.4061)}, "cache/chirps", first_year=2006)
```

## Open-Meteo — `openmeteo.py`

* API gratuite **non commerciale**, limites par adresse IP : 600 appels/min, 5 000/h,
  10 000/jour. Une requête de plus de 14 jours compte pour plusieurs appels :
  1981 → aujourd'hui pour UNE ville ≈ 1 200 appels.
* « Daily API request limit exceeded » = quota de l'IP épuisé (fréquent sur les
  machines cloud partagées). Depuis ta connexion ça passe ; sinon réessayer le
  lendemain. Le client ralentit tout seul sous les limites et comprend les
  réponses 429.
* Modèle `era5_seamless` (ERA5-Land 0,1°), température corrigée à l'altitude de la
  ville (`elevation`). ~5 jours de retard ; `recent_daily()` donne les derniers jours
  (provisoires) via l'API de prévision.

## Reproduire

```sh
python tools/extract_inmet.py <clone de WeatherRecord>   # vérité terrain INMET
python tools/fetch_reference.py --job nasa                # (GitHub Actions)
python tools/validate_sources.py                          # -> validation/metrics.json
# Excel + graphiques : workflow « Build Excel export » -> exports/
```
