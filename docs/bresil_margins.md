# Marge des producteurs d'arabica au Brésil — première estimation

Série dans `data/bresil_margins.csv`. Base = campagne N (récolte mai-sept N,
vendue surtout de juillet N à juin N+1).

## Méthode
- **Prix** : indicateur Cepea/Esalq arabica type 6, moyenne de la campagne
  juil N → juin N+1 quand Cepea la publie, sinon reconstituée à partir des
  moyennes mensuelles trouvées (colonne `price_note`).
- **Coût variable** : prix minimum Conab de la campagne. Conab fixe ce prix
  sur le coût variable relevé dans ses panels (dix municipes, dont Guaxupé,
  Patrocínio, Franca, Manhuaçu).
- **Coût total (proxy)** : coût variable × 1,55. Dans les fiches Conab arabica
  le coût total (amortissements, terre, rémunération du capital inclus) vaut
  environ 1,5 à 1,6 fois le coût variable. À remplacer par la ligne
  « custo total por saca » des fiches Conab dès qu'elles sont dans `data/raw/`.
- **Marge cash** = (prix − coût variable) / prix.
- **Marge complète** = (prix − coût total proxy) / prix.

## Résultat (R$ nominaux par sac de 60 kg)

| Campagne | Arabica Conab (M sacs) | Prix Cepea | Coût variable | Coût total proxy | Marge cash | Marge complète |
|---|---|---|---|---|---|---|
| 2018 | 47,5 | 423 | n.d. | ~480 (est.) | n.d. | ≈ −14 % |
| 2019 | 34,3 | 505 | n.d. | ~500 (est.) | n.d. | ≈ 0 % |
| 2020 | 48,8 | ~800 | 364 | 564 | 54 % | 29 % |
| 2021 | 31,4 | 1 326 | 369 | 573 | 72 % | 57 % |
| 2022 | 32,4 | ~1 100 | 607 | 940 | 45 % | 15 % |
| 2023 | ~38,5 | ~950 | 684 | 1 061 | 28 % | −12 % |
| 2024 | ~39,6 | ~1 950 | 638 | 989 | 67 % | 49 % |
| 2025 | ~35,0 | ~2 000 | 662 | 1 026 | 67 % | 49 % |
| 2026 | 45,7 (prév.) | ~1 720 (juil-sept) | 793 | 1 228 | 54 % | 29 % |

Ratio d'échange café/engrais (sacs par tonne de 20-05-20) : ~2,9 en 2023,
1,8 en juillet 2024, 1,1 en avril 2025, 1,6 en mai 2026 ; moyenne 5 ans à
2024 : 4,0. Plus le chiffre est bas, plus le producteur peut fertiliser.

## Faut-il produire ? (septembre 2026)
Prix Cepea ~1 722 R$/sc, coût variable 2026/27 = 793 (prix minimum Conab,
+20 % en un an), coût total proxy 1 228. Marge complète 29 %, marge cash 54 %.
Le prix peut baisser de 40 % avant que le coût total ne soit plus couvert.
Zones de décision (calculées dans `margins.html`) :
- A, prix ≥ 1 413 : intrants complets, renouvellement, plantations. **Situation actuelle.**
- B, 1 228-1 413 : produire et entretenir, pas d'expansion.
- B−, 793-1 228 : maintenir a minima, différer taille et renouvellement.
- C, < 793 : couper les intrants, esqueletamento.
Tendance : prix −23 % sur 13 mois, coût +20 %, ratio café/engrais passé de
1,1 à 1,6 sc/t. La zone A tient mais se rétrécit. 2027 est une année « off »
et le record 2026 pèse sur les prix : le point à surveiller est un passage
sous ~1 400 R$/sc pendant la floraison sept-oct 2026 et la fertilisation
d'été, ce qui ferait basculer les décisions d'intrants pour 2027.

## Lecture marge → production (décalage 1-2 ans)
- 2018-2019 : marge nulle ou négative, prix réel le plus bas depuis 2001/02.
  Récolte 2021 la plus faible de la série (31,4), aggravée par sécheresse et gel.
- 2020-2021 : marges très fortes. 2022 reste faible à cause du gel de juillet
  2021, 2023 rebondit malgré une année « off ».
- 2022-2023 : coût record (engrais +149 % fin 2021, guerre en Ukraine), marge
  complète négative en 2023. 2024 et 2025 médiocres, avec en plus la
  sécheresse fin 2024 et la chaleur de février-mars 2025.
- 2024-2025 : marges à 49 %, meilleur ratio café/engrais de la décennie.
  Récolte 2026 annoncée record (45,7 M sacs arabica).

Le sens est cohérent : les creux de marge précèdent de deux ans les creux de
production, les pics de marge précèdent le record 2026. Mais avec neuf points
et des chocs météo sur 2021, 2022, 2024 et 2025, on ne peut pas séparer les
deux effets statistiquement. C'est le travail à faire avec la série Conab
complète (2003-2023) et les anomalies de pluie du site.

## Limites
- Les prix 2020, 2022 à 2026 sont reconstitués à partir de moyennes
  mensuelles, précision ± 5 à 10 %.
- Le coût total est un proxy. La marge complète bouge d'environ 4 points
  si le facteur passe de 1,45 à 1,65.
- Une marge par sac gonfle en année « on » et s'écrase en année « off »
  (coût fixe divisé par un rendement variable). Colonne `yield_sacas_ha`
  fournie pour passer en marge par hectare lissée sur deux ans.
- Tout est en reais nominaux. Ajouter USDBRL et KC pour une lecture en USD.

## Sources
Cepea/Esalq (bilans de campagne 2018/19, 2019/20, 2021/22, rétrospectives
2023 et 2025, moyennes mensuelles 2024-2026), Conab (prix minimums 2020/21 à
2025/26, levantamentos de safra, rendements), CNA Campo Futuro et Cocapec
(panels de coût 2022-2024), Rabobank Brazilian coffee monthly update (ratio
d'échange, prix physiques juillet 2026), StoneX (enquête récolte 2026/27).

## Annexe — exportations mensuelles de robusta d'Indonésie (Sumatra)
Série publique la plus suivie : exportations de grains de robusta de Sumatra
(bureau du commerce de Lampung, port de Panjang), reprise chaque mois par
Reuters. Partiel : voir `data/indonesia_sumatra_robusta_exports.csv`
(colonne `basis` = reported / derived). Agrégat USDA : avril-août 2025 =
3,5 M sacs (210 kt), +83 % sur un an. National (tous cafés) : 508,8 kt
exportées en 2025 ; cible AEKI 2026 : 330-360 kt.
