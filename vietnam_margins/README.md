# Vietnam – marges comparées robusta / poivre / cajou / durian (substitution)

Collecte du 2026-09-27. But : comparer la rentabilité des quatre cultures et documenter la substitution
(notamment poivre → durian, et durian intercalé dans le café).

## Fichiers et niveau de fiabilité

| Fichier | Contenu | Fiabilité |
|---|---|---|
| `faostat_vietnam.csv` | FAOSTAT 2008–2024 : prix producteur (VND/t, USD/t), surface récoltée, production, rendement pour café, poivre et cajou | **Officiel**, téléchargé (`raw/`). Le durian n'est pas isolé dans FAOSTAT. |
| `secondary_sources.csv` | 23 chiffres : prix bord-champ 2023–2026, coûts de production, surfaces de durian, investissement, rendements | **Non vérifiés.** Ils viennent des résumés de recherche web (USDA GAIN, VnExpress, vietnam.vn, Dantri, giacaphe…) car ces pages ne sont pas téléchargeables ici. L'attribution à une URL précise peut être approximative. À vérifier avant citation. |
| `margin_comparison.csv` | Marge nette/ha = (prix − coût) × rendement | **Calcul dérivé.** Il utilise les points médians des fourchettes, pour un verger adulte, hors foncier et hors coût d'installation. |

## Résultat (millions VND par ha et par an, verger en production)

| Culture | Période | Prix (k VND/kg) | Coût (k VND/kg) | Marge nette/ha | Marge % |
|---|---|---|---|---|---|
| Robusta | 2023/24 | 94 | 40 | ~158 M | 57 % |
| Robusta | 2024/25 | 118 | 40 | ~232 M | 66 % |
| Robusta | sept. 2026 | 92,6 | 40 | ~156 M | 57 % |
| Poivre | 2020 | 64 | 50 | ~33 M | 22 % |
| Poivre | 2024 | 105 | 75 | ~81 M | 29 % |
| Poivre | 2026 | 152,5 | 75 | ~206 M | 51 % |
| Cajou | 2026 | 35,5 | ? | recette brute ~38 M, coût non sourcé | – |
| Durian Ri6 | 2024 | 61 | 26 | ~525 M | 57 % |
| Durian Monthong | 2024 | 103,5 | 26 | ~1 160 M | 75 % |
| Durian Ri6 | mai 2025 | 37,5 | 26 | ~173 M | 31 % |
| Durian Monthong | mai 2025 | 65 | 26 | ~585 M | 60 % |
| Durian Ri6 | mai 2026 | 22,5 | 26 | **−53 M (perte)** | −16 % |

Rendements utilisés : robusta ~2,9–3,0 t/ha, poivre ~2,4–2,7 t/ha et cajou ~1,1 t/ha (FAOSTAT) ; durian 15 t/ha (fourchette publiée 14–20).

## Ce que les données disent sur la substitution

1. **La substitution était justifiée en 2022–2024.** Par hectare adulte, le durian rapportait 2,5 à 7 fois plus que le robusta, et 5 à 15 fois plus que le poivre (dont la marge était faible, voire nulle, en 2019–2021). Les surfaces de durian sont passées d'environ 70 000 ha en 2020 à 131 000 ha en 2023, ~180 000 ha en 2024 et ~195 000 ha fin 2025.
2. **Le poivre est la culture réellement remplacée.** D'après FAOSTAT, sa surface culmine à 111 793 ha en 2021 puis descend à 98 616 ha en 2024 (−12 %). La profession estime même la surface réelle à 60–70 000 ha. Le café, lui, **n'a pas reculé au niveau national** : 637 563 ha en 2020 et 678 569 ha en 2024 selon FAOSTAT. Pour le café, la substitution passe surtout par l'**intercalage** (>163 000 ha d'arbres fruitiers dans les caféières), pas par l'arrachage.
3. **L'avantage du durian s'est inversé en 2025–2026.** Le prix du Ri6 a chuté (15–30 k VND/kg en mai 2026, sous le coût de 25–27 k) à cause des contrôles chinois sur le cadmium, de la concurrence thaïe et de la hausse de l'offre. Le robusta reste à ~57 % de marge et le poivre est remonté à ~50 %.
4. **Coûts cachés du durian** : 4 à 6 ans sans récolte, pour un investissement de ~250–300 M VND/ha (jusqu'à 1–2 Md VND/ha en intensif). Si l'on arrache du café pour planter du durian, on renonce aussi à ~150–230 M VND/ha/an de marge café pendant ces années, soit ~0,6–1,1 Md VND/ha. Au prix de 2024 (Ri6), le durian rembourse cela en 2 à 3 récoltes. Au prix de 2026, il ne le rembourse pas.

**Conclusion pour argumenter :** convertir le poivre en durian était rationnel sur 2021–2024. Pour le café, la stratégie qui tient le mieux dans le temps est l'intercalage, qui garde la marge café tout en ajoutant du durian. La conversion totale n'est plus justifiée aux prix de 2025–2026.

## Limites

- **Sites inaccessibles depuis cet environnement** (bloqués par le proxy, y compris via WebFetch) : GSO/NSO, MARD/MAE, VICOFA, VPA, VINACAS, USDA GAIN, et la presse vietnamienne. Seul FAOSTAT a pu être téléchargé.
- **Anomalies FAOSTAT** :
  - Le prix producteur du café en 2022–2024 (14–18 M VND/t) est incohérent avec le marché (~40–94 k VND/kg). C'est probablement une rupture de série, et ces lignes sont signalées dans les notes.
  - Le prix du cajou en 2022–2024 (46–49 M VND/t) est supérieur aux prix bord-champ rapportés par la presse (30–36 k VND/kg).
- **Hors calcul** :
  - Aucun coût de production sourcé n'a été trouvé pour le cajou, donc pas de marge calculée.
  - Il manque des coûts sourcés par année : le coût du café (~40 k VND/kg) est appliqué à toutes les années de robusta.
- **Variabilité** : les marges varient de ±10–20 points selon la région, l'irrigation, l'âge du verger et la qualité (export ou local).
