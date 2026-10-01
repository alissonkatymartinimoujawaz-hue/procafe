# Cours quotidiens KC1 et DF1 (copie publique)

Utilisés pour la question « qui bouge en premier ? » (section 8 du rapport `Recherche_STU_prix_cafe.docx`, onglet `9_Quotidien` de l'Excel).

## Fichiers

| Fichier | Contenu | Lignes | Période |
|---|---|---|---|
| `kc_df_quotidien_2021_2026.csv` | KC1 (c/lb) et DF1 ($/t), jours communs aux deux marchés | 1233 | 2021-06-01 → 2026-05-29 |
| `kc_quotidien_2016_2026.csv` | KC1 seul (c/lb) | 2514 | 2016-10-03 → 2026-10-01 |
| `usd_brl_quotidien_2020_2026.csv` | réals par dollar | 1507 | 2020-10-01 → 2026-10-01 |

## Provenance

- Copie du fichier `docs/data/market-data.json` du dépôt public https://github.com/axelcohen75/coffee-dashboard (commit `8334fe3fba23fdb2ffe4d4b71ce09fad758bd6d8`, fichier généré le 2026-10-01 18:05 UTC).
- KC1 : Yahoo Finance `KC=F` (ICE New York, café « C », contrat le plus proche), clôture quotidienne.
- DF1 : export Investing.com « London Robusta Coffee Futures » (ICE Londres, contrat le plus proche), colonne « Dernier ». Le fichier CSV d'origine du dépôt (`data/robusta_futures_price_history.csv`) a été comparé au JSON : identiques sur les 1 261 jours.
- USD/BRL : Yahoo Finance.
- Les séries ne sont pas ajustées des changements de contrat. Les sites de prix (stooq, Yahoo, FRED, ICE, Investing.com) sont bloqués depuis l'environnement de travail ; d'où le recours à cette copie publique.

## Contrôle

Moyennes mensuelles des cours quotidiens comparées aux moyennes ICO (`ice_prix_mensuels_ico.csv`, 2e position) :

- KC1 : 119 mois, corrélation des niveaux 0.9987, écart médian -0.8 %.
- DF1 : 60 mois, corrélation des niveaux 0.9997, écart médian +0.6 %.

## À savoir

- Jours extrêmes (0,5 % des plus fortes variations de chaque marché, changements de contrat probables), retirés dans les tests de robustesse : 2021-07-22, 2021-07-26, 2021-07-30, 2022-05-11, 2024-01-16, 2024-05-02, 2024-12-02, 2025-07-14, 2025-09-02, 2025-09-17, 2025-09-19, 2025-12-17.
- Heures de clôture : New York 13h30 (heure de New York), Londres 17h30 (heure de Londres). Le KC clôture donc une heure après le DF, sauf de mi-mars à fin mars et de fin octobre à début novembre (89 jours sur la période), quand les deux clôtures tombent au même instant.
- Début juillet 2026, le KC1 de Yahoo montre des allers-retours de ±10 à 14 % (bascule entre contrats) : hors de la période commune avec le DF1, donc sans effet sur l'analyse.
