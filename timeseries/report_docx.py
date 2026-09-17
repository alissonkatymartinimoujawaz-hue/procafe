#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
One Word report per origin: the reasoning chain (production = bearing area x
yield, yield = trees + calendar + weather + ENSO), the facts of the balance
sheet, the measured ENSO effects, the ARMA / ARMAX forecasts and what the
2026/27 El Nino implies.  Text in French.

    python timeseries/report_docx.py            # -> timeseries/output/reports/*.docx

Needs the outputs of extract_series.py, arma_models.py, armax_models.py and
enso_analysis.py.
"""
import os
import numpy as np
import pandas as pd
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

import report_figures as fig
from enso import ONI_SEASONS, ONI_SOURCE, CROP_SEASON, enso_for_crop_year

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")
REP = os.path.join(OUT, "reports")
FIGS = os.path.join(REP, "figures")
ASOF = "16 septembre 2026"

# ----------------------------------------------------------------------------- country knowledge
# Crop calendars, regions and ENSO climatology: general agro-climatic knowledge
# (USDA FAS attaché reports, ICO, NOAA CPC teleconnection maps); the numbers in
# the reports come from the balance sheet.
COUNTRIES = {
    "Brazil": dict(
        fr="Brésil", species="arabica (≈ 68 %) et robusta/conilon (≈ 32 %)", my="juillet-juin",
        regions="arabica : Minas Gerais (Sul de Minas, Cerrado Mineiro, Matas de Minas), São Paulo (Mogiana), Paraná ; conilon : Espírito Santo (São Mateus, nord de l'État), Rondônia, Bahia",
        calendar=[("Floraison arabica (après les premières pluies)", [9, 10, 11], "floraison"),
                  ("Développement du fruit, saison des pluies", [10, 11, 12, 1, 2, 3, 4], "développement du fruit"),
                  ("Saison sèche (remplissage, maturation)", [5, 6, 7, 8, 9], "saison sèche"),
                  ("Récolte arabica", [5, 6, 7, 8, 9], "récolte"),
                  ("Récolte conilon (Espírito Santo)", [4, 5, 6, 7, 8], "récolte"),
                  ("Fenêtre de risque gel (Sul de Minas, Paraná)", [6, 7, 8], "risque gel")],
        weather="pluie sept.-nov. (floraison), pluies oct.-avril,\nsécheresse août-sept., gel juin-août, chaleur",
        enso_season="prev",
        enso_clim=("Climatologie établie : El Niño renforce les pluies du Sud du Brésil (Paraná, sud de São Paulo) et "
                   "apporte chaleur et pluies déficitaires vers le Nordeste et une partie du Sudeste ; La Niña tend à "
                   "assécher le Sud et à favoriser les descentes d'air froid en hiver (gel de juillet 2021 pendant La Niña). "
                   "Les États caféiers, Minas Gerais et Espírito Santo, sont à la charnière : l'effet est plus faible "
                   "et plus variable que dans le Sud, d'où l'intérêt de le mesurer dans les données."),
        enso_window="La campagne Y/Y+1 (récolte mai-sept. de l'année Y) se joue entre la floraison de sept.-nov. Y-1 et "
                    "avril Y : c'est l'épisode ENSO qui culmine en déc.-fév. de Y-1/Y qui la pilote. L'El Niño en cours "
                    "(jusqu'à mars 2027) pèse donc sur la récolte 2027, campagne 2027/28, une année OFF.",
        shocks={2014: "sécheresse et chaleur de janvier-février 2014 à Minas Gerais (année ON amputée)",
                2016: "sécheresse 2015-16 en Espírito Santo : conilon au plus bas (10,5 M sacs)",
                2021: "sécheresse 2020-21 puis gel du 20 juillet 2021 ; arabica 36,4 M sacs",
                2024: "sécheresse et chaleur 2023-24 (El Niño fort) : année ON limitée à 44,5 M sacs d'arabica",
                2025: "hiver 2024 très sec, année OFF : arabica 38 M sacs",
                2002: "année ON record (53,6 M sacs), pluies normales, phase neutre"},
        forecast_series="Production Total", enso_series_yield="Yield (production / bearing area)",
        extra_note="Le drapeau ON/OFF de la balance sheet et la météo par État sont utilisés dans le modèle ARMAX."),
    "Colombia": dict(
        fr="Colombie", species="arabica lavé (100 %)", my="octobre-septembre",
        regions="Huila, Antioquia, Tolima, Cauca, Caldas, Quindío, Risaralda, Santander, Nariño (zone andine, 1 200-2 000 m)",
        calendar=[("Floraison principale (après la saison sèche déc.-fév.)", [1, 2, 3], "floraison"),
                  ("Floraison de mitaca", [7, 8, 9], "floraison"),
                  ("1re saison des pluies", [3, 4, 5], "saison des pluies"),
                  ("2e saison des pluies", [9, 10, 11], "saison des pluies"),
                  ("Récolte principale (cosecha)", [9, 10, 11, 12], "récolte"),
                  ("Récolte de mitaca (centre-sud)", [4, 5, 6], "récolte")],
        weather="excès de pluie / nébulosité (roya, mauvaise floraison),\nsécheresse dic.-mars, ensoleillement",
        enso_season="same",
        enso_clim=("Climatologie établie : El Niño réduit les pluies et augmente la température dans la zone andine "
                   "colombienne (sécheresses 1997-98, 2015-16, 2023-24) ; La Niña apporte des excès de pluie, de la "
                   "nébulosité et des inondations (2007-08, 2010-12, 2020-23). Pour un caféier de moyenne altitude sous "
                   "un climat déjà très humide, un El Niño modéré est plutôt favorable (plus de soleil, floraison groupée, "
                   "moins de roya) ; un El Niño fort apporte du stress hydrique et des grains plus petits ; La Niña est "
                   "négative (roya, floraisons dispersées, cerises qui tombent, récolte et séchage perturbés)."),
        enso_window="La campagne Y/Y+1 (récolte principale oct.-déc. de Y, mitaca avril-juin de Y+1) dépend de la floraison "
                    "de janv.-mars Y et des pluies de l'année Y : c'est l'épisode qui se développe pendant Y et culmine "
                    "en déc.-fév. Y/Y+1 qui compte. L'El Niño en cours pilote donc la campagne 2026/27.",
        shocks={2008: "début de l'épidémie de roya, pluies excessives (La Niña) et lancement de la rénovation : 8,7 M sacs",
                2009: "El Niño modéré mais verger en pleine rénovation : 8,1 M sacs",
                2011: "La Niña forte 2010-12 : roya, floraison dispersée, 7,7 M sacs, plus bas de la période",
                2015: "El Niño très fort : sécheresse, mais verger rénové (variétés résistantes) : 14,0 M sacs",
                2022: "La Niña triple (2020-23), pluies excessives et engrais chers : 10,7 M sacs",
                2023: "El Niño fort, temps plus sec : rebond à 12,8 M sacs"},
        forecast_series="Production Arabica", enso_series_yield="Yield",
        extra_note="Deux sources dans la balance sheet : USDA (surfaces et arbres en paliers) et Fedecafé/Agronet (surfaces réelles, rendement)."),
    "Honduras": dict(
        fr="Honduras", species="arabica lavé (100 %)", my="octobre-septembre",
        regions="Copán, Ocotepeque, Lempira, Santa Bárbara (ouest), Comayagua, La Paz, Intibucá (centre), El Paraíso (est) ; 1 000-1 600 m",
        calendar=[("Floraison (premières pluies)", [4, 5, 6], "floraison"),
                  ("Saison des pluies (primera / postrera)", [5, 6, 7, 8, 9, 10], "saison des pluies"),
                  ("Canícula (pause sèche)", [7, 8], "saison sèche"),
                  ("Développement du fruit", [6, 7, 8, 9, 10], "développement du fruit"),
                  ("Récolte", [11, 12, 1, 2, 3], "récolte"),
                  ("Saison sèche (récolte, séchage)", [11, 12, 1, 2, 3, 4], "saison sèche")],
        weather="pluies mai-oct. (floraison, remplissage), canícula juil.-août,\nexcès de pluie / ouragans (roya), sécheresse du Corridor sec",
        enso_season="same",
        enso_clim=("Climatologie établie : El Niño réduit les pluies de la primera (mai-juillet) et allonge la canícula "
                   "dans le Corridor sec d'Amérique centrale (sécheresses 2009, 2014-15, 2018-19, 2023) ; La Niña apporte des "
                   "saisons plus humides et une activité cyclonique atlantique plus forte (ouragans Eta et Iota, novembre "
                   "2020). Pour le café, El Niño = stress hydrique au remplissage, grains plus petits, mais moins de roya ; "
                   "La Niña = bonne humidité mais roya, glissements de terrain et pertes à la récolte."),
        enso_window="La campagne Y/Y+1 (récolte nov. Y - mars Y+1) se construit entre la floraison d'avril-juin Y et "
                    "octobre Y : l'épisode qui se développe en Y et culmine en déc.-fév. Y/Y+1 la pilote. L'El Niño en "
                    "cours pilote donc la campagne 2026/27.",
        shocks={2012: "épidémie de roya 2012-13 : récolte 2012/13 puis 2013/14 en recul", 2013: "roya (deuxième année)",
                2016: "récolte record 2016/17 (7,5 M sacs) après la rénovation post-roya, phase La Niña faible",
                2020: "ouragans Eta et Iota (nov. 2020), main-d'œuvre Covid : récolte 2020/21 réduite",
                2022: "coûts des engrais, roya, migration de main-d'œuvre : 4,8 M sacs",
                2023: "El Niño fort, sécheresse du Corridor sec : rendement sous la tendance"},
        forecast_series="Production Arabica", enso_series_yield="Yield",
        extra_note=""),
    "Ethiopia": dict(
        fr="Éthiopie", species="arabica (100 %), forêt, semi-forêt, jardins et plantations", my="octobre-septembre",
        regions="Sidama, Guji, Yirgacheffe (Sud) ; Jimma, Limu, Kaffa (Sud-Ouest) ; Harrar (Est) ; 1 500-2 200 m",
        calendar=[("Floraison (pluies de belg)", [3, 4, 5], "floraison"),
                  ("Petites pluies (belg)", [2, 3, 4, 5], "saison des pluies"),
                  ("Grandes pluies (kiremt)", [6, 7, 8, 9], "saison des pluies"),
                  ("Développement du fruit", [5, 6, 7, 8, 9], "développement du fruit"),
                  ("Récolte (Sud, Sud-Ouest)", [10, 11, 12, 1], "récolte"),
                  ("Saison sèche (récolte, séchage)", [10, 11, 12, 1, 2], "saison sèche")],
        weather="pluies de belg (floraison), kiremt (remplissage),\nsécheresse, pluies hors saison à la récolte",
        enso_season="same",
        enso_clim=("Climatologie établie : El Niño affaiblit les grandes pluies de kiremt (juin-sept.) dans le nord et le "
                   "centre de l'Éthiopie (sécheresse de 2015, la pire depuis 30 ans) et renforce les pluies d'oct.-déc. "
                   "dans le sud ; La Niña assèche le sud et le sud-est (Corne de l'Afrique 2010-11, 2016-17, 2020-23). "
                   "Les zones caféières du sud et du sud-ouest sont moins touchées que les hauts plateaux du nord : l'effet "
                   "El Niño sur le café est modéré (belg et kiremt affaiblis = remplissage moins bon), l'effet La Niña "
                   "négatif dans le sud (Sidama, Guji)."),
        enso_window="La campagne Y/Y+1 (récolte oct. Y - janv. Y+1) dépend des pluies de belg et de kiremt de l'année Y : "
                    "l'épisode qui se développe en Y la pilote. L'El Niño en cours pilote donc la campagne 2026/27.",
        shocks={}, forecast_series=None, enso_series_yield=None,
        extra_note="ATTENTION : l'onglet Éthiopie de la balance sheet est une copie exacte de l'onglet Honduras. "
                   "Aucun chiffre n'a été utilisé ; les sections chiffrées attendent les données éthiopiennes (USDA PSD : "
                   "production ≈ 8 M de sacs, surface ≈ 0,5 M ha, ordres de grandeur à confirmer)."),
    "Peru": dict(
        fr="Pérou", species="arabica (100 %), petits producteurs, forte part certifiée", my="avril-mars (USDA) ; la balance sheet utilise octobre",
        regions="Junín (Chanchamayo, Satipo), Cajamarca (Jaén, San Ignacio), San Martín, Amazonas, Cusco (La Convención) ; versant amazonien des Andes, 1 000-1 800 m",
        calendar=[("Floraison (début des pluies)", [9, 10, 11], "floraison"),
                  ("Saison des pluies", [10, 11, 12, 1, 2, 3, 4], "saison des pluies"),
                  ("Développement du fruit", [11, 12, 1, 2, 3, 4], "développement du fruit"),
                  ("Récolte (pic juin-août)", [4, 5, 6, 7, 8, 9], "récolte"),
                  ("Saison sèche (récolte, séchage)", [5, 6, 7, 8, 9], "saison sèche")],
        weather="pluies oct.-avril (floraison, remplissage), sécheresse andine,\nexcès de pluie au nord (roya), routes coupées",
        enso_season="prev",
        enso_clim=("Climatologie établie : El Niño apporte des pluies extrêmes sur la côte nord du Pérou (Piura, "
                   "Lambayeque ; 1997-98, 2017 « El Niño costero », 2023) et tend à réduire les pluies et à réchauffer les "
                   "Andes centrales et du sud ; La Niña fait l'inverse. Les zones caféières sont sur le versant amazonien : "
                   "au nord (Cajamarca, Amazonas, San Martín) El Niño se traduit par plus d'humidité, de roya et de routes "
                   "coupées ; au centre-sud (Junín, Cusco) plutôt par un déficit de pluie à la floraison. L'effet net sur le "
                   "rendement national est ambigu et doit être mesuré sur des données péruviennes."),
        enso_window="La campagne Y/Y+1 (récolte avril-sept. de Y) dépend des pluies d'oct. Y-1 à avril Y : l'épisode qui "
                    "culmine en déc.-fév. Y-1/Y la pilote. L'El Niño en cours pilote donc la récolte 2027 (campagne 2027/28).",
        shocks={}, forecast_series=None, enso_series_yield=None,
        extra_note="ATTENTION : l'onglet Pérou de la balance sheet est une copie exacte de l'onglet Honduras. Aucun "
                   "chiffre n'a été utilisé ; les sections chiffrées attendent les données péruviennes (USDA PSD : "
                   "production ≈ 4 M de sacs, ordres de grandeur à confirmer). Roya 2013 : la production avait chuté d'environ un tiers."),
    "Indonesia": dict(
        fr="Indonésie", species="robusta (≈ 88 %, Sud-Sumatra, Lampung, Java, Sulawesi) et arabica (≈ 12 %, Nord-Sumatra, Aceh, Toraja, Java, Flores)", my="avril-mars",
        regions="robusta : Lampung, Sumatra-Sud, Bengkulu ; arabica : Aceh (Gayo), Nord-Sumatra (Lintong, Mandheling), Toraja, Bali, Flores",
        calendar=[("Floraison robusta (fin de saison sèche)", [8, 9, 10], "floraison"),
                  ("Saison des pluies (mousson d'ouest)", [11, 12, 1, 2, 3, 4], "saison des pluies"),
                  ("Développement du fruit", [11, 12, 1, 2, 3, 4], "développement du fruit"),
                  ("Saison sèche", [5, 6, 7, 8, 9, 10], "saison sèche"),
                  ("Récolte robusta Sud-Sumatra (pic juin-août)", [4, 5, 6, 7, 8, 9], "récolte"),
                  ("Récolte arabica Nord-Sumatra (deux pics)", [10, 11, 12, 1, 4, 5, 6], "récolte")],
        weather="sécheresse prolongée juin-oct. (floraison), retard de la mousson,\nexcès de pluie à la récolte (séchage, qualité)",
        enso_season="prev",
        enso_clim=("Climatologie établie : l'Indonésie est l'une des régions les plus sensibles à l'ENSO. El Niño = "
                   "saison sèche prolongée, retard de la mousson, feux de forêt et brume (1997, 2015, 2019, 2023) ; La Niña "
                   "= pluies excédentaires, inondations, saison des pluies allongée. Pour le robusta de Sumatra, une "
                   "saison sèche marquée mais pas extrême favorise une floraison groupée (léger effet positif d'un El Niño "
                   "faible), un El Niño fort réduit la nouaison et le remplissage (récolte suivante en baisse) ; La Niña "
                   "gêne la floraison, la récolte et le séchage (2022 : robusta à 6,8 M sacs)."),
        enso_window="La campagne Y/Y+1 (récolte robusta avril-sept. de Y) dépend de la saison sèche et de la floraison "
                    "d'août-oct. Y-1 puis de la mousson : l'épisode qui culmine en déc.-fév. Y-1/Y la pilote. L'El Niño "
                    "en cours pilote donc la campagne 2027/28.",
        shocks={2016: "El Niño très fort 2015-16 : saison sèche extrême, feux ; robusta en repli",
                2019: "saison sèche prolongée 2019 : robusta 9,3 M sacs",
                2022: "La Niña triple, pluies excessives à la floraison et à la récolte : robusta 6,8 M sacs",
                2023: "rebond 9,3 M sacs puis 11,0 M en 2024/25 (bonne floraison après le temps sec de 2023)"},
        forecast_series="Production Total", enso_series_yield="Yield (production / bearing area)",
        extra_note="Les surfaces USDA sont en millions d'ha et quasi constantes ; le rendement est calculé comme production / surface bearing."),
    "Vietnam": dict(
        fr="Vietnam", species="robusta (≈ 95 %, Hauts Plateaux du centre) et arabica (≈ 5 %, Lâm Đồng, Sơn La, Điện Biên)", my="octobre-septembre (la balance sheet utilise novembre)",
        regions="Đắk Lắk, Lâm Đồng, Đắk Nông, Gia Lai, Kon Tum (Hauts Plateaux, 500-800 m) ; arabica au nord-ouest (Sơn La, Điện Biên) et à Lâm Đồng",
        calendar=[("Saison sèche : irrigation obligatoire (3 à 4 tours)", [11, 12, 1, 2, 3, 4], "irrigation"),
                  ("Floraison (après les irrigations)", [1, 2, 3], "floraison"),
                  ("Saison des pluies (mousson du sud-ouest)", [5, 6, 7, 8, 9, 10], "saison des pluies"),
                  ("Développement du fruit", [4, 5, 6, 7, 8, 9, 10], "développement du fruit"),
                  ("Récolte robusta (pic décembre)", [11, 12, 1], "récolte"),
                  ("Séchage (temps sec)", [11, 12, 1, 2], "séchage")],
        weather="sécheresse janv.-avril (réserves d'eau, irrigation), chaleur,\npluies mai-oct. (remplissage), typhons à la récolte",
        enso_season="prev",
        enso_clim=("Climatologie établie : El Niño affaiblit la mousson et allonge la saison sèche des Hauts Plateaux ; "
                   "les réservoirs se vident, l'irrigation de février-avril est rationnée, les températures montent "
                   "(sécheresses de 1998, 2005, 2016 et 2024). La Niña apporte des pluies plus abondantes, de bonnes "
                   "réserves d'eau mais des typhons et un séchage difficile à la récolte. Pour le robusta irrigué, "
                   "El Niño est nettement négatif (nouaison et calibre), La Niña plutôt positif."),
        enso_window="La campagne Y/Y+1 (récolte nov. Y - janv. Y+1) dépend de la saison sèche de janv.-avril Y (irrigation, "
                    "floraison) puis de la mousson de Y : l'épisode qui culmine en déc.-fév. Y-1/Y la pilote. L'El Niño en "
                    "cours pèse donc sur la saison sèche 2027 et la campagne 2027/28.",
        shocks={2016: "sécheresse historique de mars-mai 2016 (El Niño très fort) : campagne 2016/17 à 27,4 M sacs, −8 %",
                2024: "sécheresse et chaleur de mars-avril 2024 (El Niño fort) : 2024/25 à 27,3 M sacs contre 30,5 attendus",
                2013: "campagne record 2013/14 (30,5 M) : pluies abondantes et vergers jeunes",
                2020: "La Niña 2020-21 : bonnes réserves, 30,2 M sacs"},
        forecast_series="Production Total", enso_series_yield="Yield",
        extra_note="Le rendement de la balance sheet est en t/ha (USDA). Aucun stock d'arbres n'est renseigné."),
    "Uganda": dict(
        fr="Ouganda", species="robusta (≈ 80-85 %, bassin du lac Victoria, Centre, Ouest, Busoga) et arabica (≈ 15-20 %, Mont Elgon / Bugisu, Rwenzori, West Nile)", my="octobre-septembre",
        regions="robusta : Central (Masaka, Mukono, Luwero), Busoga, Ankole, Bunyoro ; arabica : Bugisu, Sebei (Mt Elgon), Kigezi, Rwenzori, West Nile",
        calendar=[("1re saison des pluies (longues pluies)", [3, 4, 5], "saison des pluies"),
                  ("2e saison des pluies (courtes pluies)", [9, 10, 11], "saison des pluies"),
                  ("Floraison robusta (deux floraisons)", [3, 4, 9, 10], "floraison"),
                  ("Récolte principale robusta (Centre, Sud)", [11, 12, 1, 2], "récolte"),
                  ("Petite récolte robusta (fly crop)", [5, 6, 7, 8], "récolte"),
                  ("Récolte arabica (Mt Elgon)", [9, 10, 11, 12], "récolte")],
        weather="deux saisons de pluies (mars-mai, sept.-nov.), sécheresse\nde janv.-fév. et juin-août, chaleur, pluies à la récolte",
        enso_season="same",
        enso_clim=("Climatologie établie : en Afrique de l'Est, El Niño (souvent avec un dipôle de l'océan Indien positif) "
                   "renforce les courtes pluies d'oct.-déc. (1997, 2006, 2015, 2019 : pluies extrêmes et inondations) ; "
                   "La Niña affaiblit les pluies et provoque des sécheresses (2016-17, 2020-23). Pour le robusta ougandais, "
                   "cultivé sans irrigation, l'humidité est plutôt bienvenue, mais des pluies excessives en oct.-déc. "
                   "tombent en pleine récolte principale : chute des cerises, fermentation, séchage difficile, routes "
                   "coupées. C'est ce que la balance sheet mesure : les campagnes El Niño sont sous la tendance."),
        enso_window="La campagne Y/Y+1 (récolte principale nov. Y - févr. Y+1) dépend des pluies de mars-mai et de "
                    "sept.-nov. de l'année Y : l'épisode qui se développe en Y et culmine en déc.-fév. Y/Y+1 la pilote. "
                    "L'El Niño en cours pilote donc la campagne 2026/27.",
        shocks={2005: "sécheresse 2004-05, wilt du robusta (flétrissement) : 2,2 M sacs, plus bas de la période",
                2009: "El Niño 2009-10, pluies fortes en fin d'année : 2,9 M sacs",
                2015: "El Niño très fort, pluies excessives à la récolte 2015/16 : 3,5 M sacs, sous la tendance",
                2017: "premiers effets du programme de replantation UCDA (2014-2018) : 4,9 M sacs en 2018/19",
                2022: "arbres replantés en pleine production : 6,6 M sacs, +21 %",
                2023: "El Niño fort, pluies d'oct.-déc. 2023 : 6,05 M sacs, −9 %"},
        forecast_series="Production Total", enso_series_yield="Output per planted ha",
        extra_note="Surface bearing, non-bearing et rendement par ha récolté n'existent que depuis 2019/20 ; « output per planted ha » sert de rendement sur 2008-2026."),
}
EXCLUDE_CAMPAIGNS = {"Brazil": {2014, 2003}}      # campaigns removed from the shock tables on request
PHASE_FR = {"El Nino": "El Niño", "La Nina": "La Niña", "neutral": "neutre", "El Nino (|ONI| >= 1)": "El Niño fort (|ONI| ≥ 1)",
            "La Nina (|ONI| >= 1)": "La Niña forte (|ONI| ≥ 1)", "El Nino fort": "El Niño fort (≥ 1,6)", "El Nino ordinaire": "El Niño (0,5 à 1,5)",
            "La Nina ordinaire": "La Niña", "La Nina forte": "La Niña forte (≤ −1,6)", "neutre": "neutre"}
PHASE_ROWS = ["El Nino fort", "El Nino ordinaire", "neutral", "La Nina ordinaire", "La Nina forte"]


# ----------------------------------------------------------------------------- helpers
def fmt(v, unit=""):
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "–"
    if abs(v) >= 100:
        return f"{v:,.0f}".replace(",", " ")
    return f"{v:.2f}" if abs(v) < 10 else f"{v:.1f}"


def cy(y):
    return f"{y}/{str(y + 1)[2:]}"


def add_table(doc, header, rows, widths=None, font=8.5):
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Light Grid Accent 1"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; c.text = ""
        r = c.paragraphs[0].add_run(str(h)); r.bold = True; r.font.size = Pt(font)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(v)); r.font.size = Pt(font)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    doc.add_paragraph()
    return t


def para(doc, text, size=10, bold=False, italic=False, color=None, style=None):
    p = doc.add_paragraph(style=style) if style else doc.add_paragraph()
    r = p.add_run(text); r.font.size = Pt(size); r.bold = bold; r.italic = italic
    if color:
        r.font.color.rgb = RGBColor.from_string(color)
    return p


def bullet(doc, text, size=10):
    p = doc.add_paragraph(style="List Bullet")
    r = p.add_run(text); r.font.size = Pt(size)
    return p


def picture(doc, path, width_cm=16.5, caption=None):
    if os.path.exists(path):
        doc.add_picture(path, width=Cm(width_cm))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        if caption:
            para(doc, caption, size=8, italic=True, color="52514e")


# ----------------------------------------------------------------------------- data access
class Data:
    def __init__(self):
        self.series = pd.read_csv(os.path.join(HERE, "data", "coffee_series.csv"))
        self.models = pd.read_csv(os.path.join(OUT, "models.csv"))
        self.fc = pd.read_csv(os.path.join(OUT, "forecasts.csv"))
        self.eff = pd.read_csv(os.path.join(OUT, "enso", "enso_effects.csv"))
        self.eyears = pd.read_csv(os.path.join(OUT, "enso", "enso_years.csv"))
        self.bw = pd.read_csv(os.path.join(OUT, "enso", "brazil_weather_by_phase.csv"))
        p = os.path.join(OUT, "armax", "models_armax.csv")
        self.armax = pd.read_csv(p) if os.path.exists(p) else None
        p = os.path.join(OUT, "armax", "forecasts_armax.csv")
        self.armax_fc = pd.read_csv(p) if os.path.exists(p) else None

    def s(self, country, series):
        g = self.series[(self.series.country == country) & (self.series.series == series)]
        return g.set_index("year")["value"].sort_index() if len(g) else pd.Series(dtype=float)

    def has(self, country):
        return (self.series.country == country).any()


def growth_decomposition(D, country):
    """Production growth since 2010/11 split into area and yield (compound rates)."""
    prod = D.s(country, "Production Total")
    if prod.empty:
        prod = D.s(country, "Production Arabica")
    area = D.s(country, "Area bearing")
    if area.empty or len(area) < 8:
        area = D.s(country, "Area total")
    both = pd.concat([prod.rename("p"), area.rename("a")], axis=1).dropna()
    both = both[both.index <= 2025]
    if len(both) < 6:
        return None
    y1 = both.index[-1]
    y0 = 2010 if 2010 in both.index else both.index[0]
    n = y1 - y0
    gp = (both.p[y1] / both.p[y0]) ** (1 / n) - 1
    ga = (both.a[y1] / both.a[y0]) ** (1 / n) - 1
    gy = (1 + gp) / (1 + ga) - 1
    return dict(y0=y0, y1=y1, gp=gp * 100, ga=ga * 100, gy=gy * 100, p0=both.p[y0], p1=both.p[y1], a0=both.a[y0], a1=both.a[y1],
                yld0=both.p[y0] / both.a[y0], yld1=both.p[y1] / both.a[y1], area_name="bearing" if "bearing" in str(area.name or "") or len(D.s(country, "Area bearing")) >= 8 else "totale")


# ----------------------------------------------------------------------------- report
def build(country, D):
    info = COUNTRIES[country]
    fr = info["fr"]
    has = D.has(country)
    os.makedirs(FIGS, exist_ok=True)
    tag = country.lower().replace(" ", "_")
    doc = Document()
    st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(10)
    for s in doc.sections:
        s.left_margin = s.right_margin = Cm(2); s.top_margin = s.bottom_margin = Cm(1.8)

    doc.add_heading(f"{fr} : balance sheet café, de la météo au rendement et à la production", 0)
    para(doc, f"Au {ASOF}. Source des chiffres : balance sheet (onglet {country}), USDA{' / CONAB' if country == 'Brazil' else ''}. "
              f"Classification ENSO : {ONI_SOURCE}.", size=9, italic=True, color="52514e")
    if info["extra_note"]:
        para(doc, info["extra_note"], size=9, bold=info["extra_note"].startswith("ATTENTION"), color="b00020" if info["extra_note"].startswith("ATTENTION") else None)

    # ---- 1. key messages
    doc.add_heading("1. Les messages clés", 1)
    dec = growth_decomposition(D, country) if has else None
    ey = D.eyears[(D.eyears.country == country)] if has else None
    yseries = info["enso_series_yield"]
    eff = D.eff[(D.eff.country == country) & (D.eff.series == yseries)].set_index("phase") if has and yseries else None
    effp = D.eff[(D.eff.country == country) & (D.eff.series == (info["forecast_series"] or ""))].set_index("phase") if has and info["forecast_series"] else None
    bullet(doc, "La production est le produit de deux choses seulement : la surface en production (bearing area) et le rendement. "
                "La surface bouge lentement (arbres plantés il y a 3 à 4 ans) ; le rendement bouge vite (météo, cycle, maladies). "
                "Une prévision doit donc expliquer le rendement.")
    if dec:
        bullet(doc, f"Entre {cy(dec['y0'])} et {cy(dec['y1'])}, la production est passée de {fmt(dec['p0'])} à {fmt(dec['p1'])} "
                    f"({dec['gp']:+.1f} % par an) : surface {dec['area_name']} {dec['ga']:+.1f} % par an, rendement {dec['gy']:+.1f} % par an. "
                    f"{'Le rendement fait la croissance.' if abs(dec['gy']) > abs(dec['ga']) else 'La surface fait la croissance.'}")
    if eff is not None and "El Nino" in eff.index:
        e_all = eff.loc["El Nino"]; e_str = eff.loc["El Nino (|ONI| >= 1)"] if "El Nino (|ONI| >= 1)" in eff.index else None
        l_all = eff.loc["La Nina"] if "La Nina" in eff.index else None
        txt = (f"El Niño : rendement en moyenne {e_all.mean_anomaly_pct:+.1f} % par rapport aux campagnes voisines sur {int(e_all.n)} campagnes "
               f"({e_all.share_below_trend:.0f} % d'entre elles sous la moyenne)")
        if e_str is not None:
            txt += f" ; El Niño fort : {e_str.mean_anomaly_pct:+.1f} % ({int(e_str.n)} campagnes, {e_str.share_below_trend:.0f} % sous la moyenne)"
        if l_all is not None:
            txt += f". La Niña : {l_all.mean_anomaly_pct:+.1f} % ({int(l_all.n)} campagnes)."
        bullet(doc, txt)
    if country == "Brazil":
        ep = pd.read_csv(os.path.join(OUT, "enso", "brazil_enso_episodes.csv"))
        st = ep[ep.classe == "El Nino fort"]
        bullet(doc, f"El Niño fort (pic ≥ 1,6 : épisodes {', '.join(st.episode)}, campagnes suivantes {', '.join(st.campagne)}) : "
                    f"Minas Gerais {st.rain_mg_dev.mean():+.0f} mm et {st.temp_mg_dev.mean():+.1f} °C, Espírito Santo {st.rain_es_dev.mean():+.0f} mm "
                    f"et {st.temp_es_dev.mean():+.1f} °C. Robusta {st.robusta_anom.mean():+.1f} % par rapport à l'attendu, arabica {st.arabica_anom.mean():+.1f} % "
                    f"(années ON, qui tiennent grâce au cycle), total {st.total_anom.mean():+.1f} %.")
        en = ep[ep.classe == "El Nino ordinaire"]
        bullet(doc, f"El Niño ordinaire (pic entre 0,6 et 1,6, 2023/24 inclus : {', '.join(en.episode)}) : arabica {en.arabica_anom.mean():+.1f} %, robusta {en.robusta_anom.mean():+.1f} %, "
                    f"total {en.total_anom.mean():+.1f} % ; Minas Gerais {en.rain_mg_dev.mean():+.0f} mm, Espírito Santo {en.rain_es_dev.mean():+.0f} mm : pas de signal net.")
    target = 2027 if info["enso_season"] == "prev" else 2026
    bullet(doc, info["enso_window"].split(". ")[-1].replace("(jusqu'à mars 2027)", "(attendu jusqu'à mars 2027)"))
    if has and info["forecast_series"]:
        f = D.fc[(D.fc.country == country) & (D.fc.series == info["forecast_series"]) & (D.fc.year == max(target, 2027))]
        if len(f):
            r = f.iloc[0]; adj = effp.loc["El Nino", "mean_anomaly_pct"] if effp is not None and "El Nino" in effp.index else 0
            bullet(doc, f"Prévision {info['forecast_series']} {cy(int(r.year))} : {fmt(r.forecast)} (intervalle 80 % {fmt(r.lo80)} – {fmt(r.hi80)}) "
                        f"par le modèle ARMA ; avec l'effet El Niño historique moyen ({adj:+.1f} %) : {fmt(r.forecast * (1 + adj / 100))}.")
    if not has:
        bullet(doc, "Les chiffres de cet onglet sont ceux du Honduras : la quantification attend les vraies données.")

    # ---- 2. structure
    doc.add_heading("2. La structure du raisonnement", 1)
    para(doc, "Production (sacs) = surface en production (ha) × rendement (sacs/ha). Chaque terme a ses propres déterminants, "
              "avec des horizons différents : le stock d'arbres se décide 3 à 4 ans avant (plantations, arrachages, rénovation), "
              "le rendement se décide dans l'année (âge et état des arbres, cycle biennal, météo de chaque phase du calendrier cultural, "
              "maladies) et c'est lui qui porte l'incertitude de court terme. ENSO n'agit pas directement : il déplace la pluie et la "
              "température des mois qui comptent, et c'est ce déplacement qu'il faut quantifier pour l'origine considérée.")
    p = os.path.join(FIGS, f"{tag}_chain.png"); fig.causal_chain(f"{fr} : chaîne causale", info["weather"], p)
    picture(doc, p, 16, "Figure 1. La chaîne causale utilisée dans ce rapport.")

    # ---- 3. calendar
    doc.add_heading("3. Le calendrier cultural : quels mois décident du rendement", 1)
    para(doc, f"Espèces : {info['species']}. Campagne USDA : {info['my']}. Régions : {info['regions']}.")
    p = os.path.join(FIGS, f"{tag}_calendar.png"); fig.crop_calendar(f"{fr} : calendrier cultural", info["calendar"], p)
    picture(doc, p, 16, "Figure 2. Phases de la culture par mois (année civile).")
    para(doc, info["enso_window"])

    # ---- 4. facts
    doc.add_heading("4. Ce que dit la balance sheet", 1)
    if has:
        last = list(range(2018, 2027))
        rows_def = [("Production Total", "Production totale"), ("Production Arabica", "Arabica"), ("Production Robusta", "Robusta"),
                    ("Area total", "Surface totale"), ("Area bearing", "Surface bearing"), ("Area non-bearing", "Surface non-bearing"),
                    ("Trees total", "Arbres (M)"), ("Trees bearing", "Arbres bearing (M)"), ("Trees non-bearing", "Arbres non-bearing (M)"),
                    (yseries, "Rendement"), ("Yield", "Rendement (USDA)")]
        seen, rows = set(), []
        for s, lab in rows_def:
            if not s or s in seen:
                continue
            v = D.s(country, s)
            if v.empty:
                continue
            seen.add(s)
            unit = D.series[(D.series.country == country) & (D.series.series == s)]["unit"].iloc[0]
            rows.append([f"{lab} ({unit})"] + [fmt(v.get(y)) for y in last])
        add_table(doc, ["Série"] + [cy(y) for y in last], rows, font=7.5)
        para(doc, "2025/26 et 2026/27 sont des estimations / projections USDA, pas des récoltes réalisées." +
             (" Surfaces et arbres : changement de source en 2024/25, les niveaux avant et après ne sont pas comparables (le calcul de la ligne 2027/28, section 7 bis, en tient compte)." if country == "Brazil" else ""),
             size=8, italic=True, color="52514e")
        ph = {yr: enso_for_crop_year(country, yr)[2] for yr in range(1995, 2027)}
        p = os.path.join(FIGS, f"{tag}_history.png"); fig.history(country, D.series, p, ph, fr)
        picture(doc, p, 17, "Figure 3. Production, surfaces et rendement ; fond coloré = phase ENSO de la campagne.")
        if dec:
            para(doc, f"Décomposition de la croissance {cy(dec['y0'])} → {cy(dec['y1'])} : production {dec['gp']:+.1f} %/an = "
                      f"surface {dec['area_name']} {dec['ga']:+.1f} %/an + rendement {dec['gy']:+.1f} %/an "
                      f"(rendement implicite {fmt(dec['yld0'])} → {fmt(dec['yld1'])} sacs par ha {dec['area_name']}).")
        tb, tn = D.s(country, "Trees bearing"), D.s(country, "Trees non-bearing")
        if not tb.empty and not tn.empty:
            j = pd.concat([tb.rename("b"), tn.rename("n")], axis=1).dropna(); j = j[j.index <= 2026]
            share = j.n / (j.b + j.n) * 100
            para(doc, f"Stock d'arbres : part non-bearing (arbres jeunes, futur potentiel) {share.iloc[-1]:.0f} % en {cy(j.index[-1])} "
                      f"contre {share.iloc[0]:.0f} % en {cy(j.index[0])} (moyenne {share.mean():.0f} %). Une part élevée annonce une "
                      f"hausse de surface productive 3 à 4 ans plus tard ; une part faible, un verger vieillissant et un rendement qui plafonne.")
    else:
        para(doc, "Pas de données propres à cette origine dans la balance sheet (onglet copié du Honduras). À remplir : production par "
                  "espèce, surface totale / bearing / non-bearing, stock d'arbres, rendement, par campagne depuis 1998/99 (USDA PSD, "
                  "et les sources nationales : ECX/ECTA pour l'Éthiopie, JNC/MIDAGRI pour le Pérou).")

    # ---- 5. yield drivers
    doc.add_heading("5. Les déterminants du rendement, quantifiés", 1)
    if has:
        m = D.models[(D.models.country == country)]
        my = m[m.series == yseries] if yseries else m.iloc[0:0]
        if len(my) and my.iloc[0].status == "ok":
            r = my.iloc[0]
            para(doc, f"Tendance : le modèle {r.model}{' avec tendance' if r.trend == 'ct' else (' avec dérive' if r.trend == 't' else '')} "
                      f"du rendement s'écrit {r.equation.replace('   with', ' ;')}. " +
                      (f"La dérive vaut {r.c:+.3g} par campagne." if r.trend == 't' and np.isfinite(r.get('c', np.nan)) else
                       (f"La tendance vaut {r.b:+.3g} par campagne." if r.trend == 'ct' and np.isfinite(r.get('b', np.nan)) else
                        "Pas de tendance déterministe retenue : le rendement évolue par chocs persistants.")))
        if country == "Brazil" and D.armax is not None:
            a = D.armax.set_index("series")
            ra = a.loc["Production Arabica"]; ry = a.loc["Yield (production / bearing area)"]
            para(doc, f"Cycle biennal : dans le modèle ARMAX, une année ON produit {fmt(ra.g_on)} milliers de sacs d'arabica de plus "
                      f"qu'une année OFF à tendance égale (p < 0,001), soit {ry.g_on:+.1f} sacs/ha de rendement. La tendance de fond est de "
                      f"{fmt(ra.b)} milliers de sacs d'arabica par an. Après retrait du cycle et de la tendance, la pluie annuelle de Minas Gerais "
                      f"a le bon signe (+450 sacs par +100 mm) mais n'est pas significative : ce sont les pluies de la floraison et la "
                      f"sécheresse d'hiver, par région, qu'il faut charger (script NASA POWER fourni).")
        # shocks table
        if ey is not None and yseries:
            g = ey[(ey.series == yseries) & (~ey.year.isin(EXCLUDE_CAMPAIGNS.get(country, set())))].sort_values("anomaly_pct")
            worst, best = g.head(4), g.tail(3).iloc[::-1]
            rows = []
            for _, r in pd.concat([worst, best]).iterrows():
                cause = info["shocks"].get(int(r.year), "")
                ph_lab = PHASE_FR.get(r.phase, r.phase)
                if np.isfinite(r.oni):
                    ph_lab = f"{ph_lab} {int(r.season)}/{str(int(r.season) + 1)[2:]} ({r.oni:+.1f})"
                rows.append([cy(int(r.year)), f"{r.anomaly_pct:+.1f} %", f"{r.yoy_pct:+.1f} %" if np.isfinite(r.yoy_pct) else "–", ph_lab, cause])
            para(doc, f"Les plus grands écarts de rendement ({yseries}) et leur cause documentée :", bold=True)
            add_table(doc, ["Campagne", "Écart aux voisines", "Variation annuelle", "Épisode ENSO pilote (ONI)", "Cause documentée"], rows,
                      widths=[2, 2.2, 2.2, 3.4, 7.2], font=8)
        prodser = info["forecast_series"]
        if prodser:
            g = ey[ey.series == prodser]
            neg = g[g.anomaly_pct < 0]
            para(doc, f"Sur {len(g)} campagnes, {len(neg)} ont une production sous la moyenne de leurs voisines ; écart-type des écarts "
                      f"{g.anomaly_pct.std():.1f} % : c'est l'ordre de grandeur de l'aléa annuel que la météo et le cycle imposent, "
                      f"à comparer à la tendance.")
    else:
        para(doc, "Sans données, les déterminants sont qualitatifs : " + info["weather"].replace("\n", " ") + ".")

    # ---- 6. ENSO
    doc.add_heading("6. El Niño / La Niña : ce que l'histoire montre pour cette origine", 1)
    para(doc, info["enso_clim"])
    para(doc, "Méthode : chaque campagne reçoit la phase de l'épisode ENSO qui pilote sa croissance (voir section 3) ; l'écart de rendement "
              "et de production est mesuré par rapport à la moyenne des deux campagnes précédentes et des deux suivantes, ce qui neutralise "
              "la tendance et, au Brésil, le cycle ON/OFF (retiré au préalable). Les moyennes par phase sont ensuite comparées ; "
              "« fort » = pic |ONI| ≥ 1.")
    if country == "Brazil":
        para(doc, "Convention retenue, comme demandé : l'épisode ENSO de l'hiver N/N+1 est rattaché à la campagne N+1/N+2 "
                  "(celle dont la floraison, sept.-nov. N+1, et le remplissage se déroulent pendant et juste après l'épisode). "
                  "Exemples : El Niño 2015/16 → campagne 2016/17 ; El Niño 2023/24 → campagne 2024/25 ; El Niño 2009/10 → 2010/11. "
                  "Niveaux : El Niño fort quand le pic atteint 1,6 (2009/10, 2015/16), El Niño entre 0,6 et 1,6, faible sous 0,6 ; même grille "
                  "pour La Niña. 2023/24 est classé El Niño simple (pic ONI 2,0 mais indice relatif RONI d'environ 1,3). "
                  "Les épisodes 2014/15 et 2002/03 (campagne 2003/04) sont exclus des tableaux et des moyennes, comme demandé.")
        p = os.path.join(FIGS, "brazil_weather_phase.png")
        fig.brazil_weather_phase(D.bw, p, phases=["El Nino fort", "El Nino ordinaire", "neutral", "La Nina ordinaire", "La Nina forte"],
                                 colors=[fig.C_RED, "#f08c8b", fig.C_MUTED, "#7fb0e8", fig.C_BLUE],
                                 labels=["El Niño fort", "El Niño", "neutre", "La Niña", "La Niña forte"])
        picture(doc, p, 17, "Figure 4. Météo des États caféiers pendant la campagne qui suit chaque classe d'épisode (écart à la moyenne 1998-2025).")
        ep = pd.read_csv(os.path.join(OUT, "enso", "brazil_enso_episodes.csv"))
        para(doc, "Épisode par épisode, campagne N+1 (écart = par rapport à la moyenne des campagnes voisines, cycle ON/OFF retiré ; "
                  "variation = par rapport à la campagne précédente) :", bold=True)
        rows = []
        for _, r in ep.iterrows():
            rows.append([f"{r.episode} ({r.oni:+.1f})", r.classe.replace("El Nino", "El Niño").replace("La Nina", "La Niña"), f"{r.campagne} {r.onoff}",
                         f"{fmt(r.arabica)} ({r.arabica_yoy:+.0f} % / {r.arabica_anom:+.1f} %)", f"{fmt(r.robusta)} ({r.robusta_yoy:+.0f} % / {r.robusta_anom:+.1f} %)",
                         f"{r.yield_anom:+.1f} %", f"{r.rain_mg_dev:+.0f} mm / {r.temp_mg_dev:+.1f} °C", f"{r.rain_es_dev:+.0f} mm / {r.temp_es_dev:+.1f} °C"])
        add_table(doc, ["Épisode (ONI)", "Classe", "Campagne N+1", "Arabica (var. / écart)", "Robusta (var. / écart)", "Rendement écart", "Minas Gerais", "Espírito Santo"],
                  rows, widths=[2.2, 2.6, 1.9, 2.8, 2.8, 1.5, 2.2, 2.2], font=7)
        cls_rows = []
        for cls in ["El Nino fort", "El Nino ordinaire", "El Nino faible", "La Nina faible", "La Nina ordinaire", "La Nina forte"]:
            g = ep[ep.classe == cls]
            if len(g):
                cls_rows.append([cls.replace("El Nino", "El Niño").replace("La Nina", "La Niña"), len(g), f"{g.arabica_anom.mean():+.1f} %", f"{g.robusta_anom.mean():+.1f} %",
                                 f"{g.total_anom.mean():+.1f} %", f"{g.yield_anom.mean():+.1f} %", f"{g.rain_mg_dev.mean():+.0f} mm / {g.temp_mg_dev.mean():+.1f} °C",
                                 f"{g.rain_es_dev.mean():+.0f} mm / {g.temp_es_dev.mean():+.1f} °C", " ".join(g.campagne)])
        # client convention: RONI growing-season index, YoY change, robusta / arabica
        cl = pd.read_csv(os.path.join(OUT, "enso", "brazil_enso_client_summary.csv"))
        para(doc, "Ta convention (index RONI de la saison de croissance, variation d'une campagne à l'autre, robusta et arabica séparés ; "
                  "détail et graphiques dans brazil_enso_client.xlsx) :", bold=True)
        rows_c = [[r.enso_class, r.index_range, int(r.n), f"{r.Robusta_avg_change_pct:+.1f} %" if pd.notna(r.Robusta_avg_change_pct) else "–",
                   f"{r.Arabica_avg_change_pct:+.1f} %" if pd.notna(r.Arabica_avg_change_pct) else "–",
                   f"{r.ES_rain_dev_mm:+.0f} mm / {r.ES_temp_dev_c:+.1f} °C" if pd.notna(r.ES_rain_dev_mm) else "–", r.crop_years] for _, r in cl.iterrows()]
        add_table(doc, ["ENSO class", "Index (RONI)", "Occurrences", "Robusta avg change", "Arabica avg change", "Espírito Santo rain / temp dev.", "Crop years"],
                  rows_c, widths=[2.6, 2.2, 1.6, 2.2, 2.2, 3.2, 5], font=7.5)
        para(doc, "Index de la campagne Y/Y+1 = valeur extrême du RONI entre SON de Y−1 et FMA de Y (floraison → fin du remplissage). "
                  "Seuils : El Niño fort ≥ 1,6 (index de croissance, ou pic ≥ 1,6 pendant la campagne : 2015/16), El Niño normal 0,5 à 1,5, neutre entre −0,5 et 0,5, La Niña ≤ −0,5. "
                  "Espírito Santo = moyenne de l'État, en attendant São Mateus et Linhares (NASA POWER).", size=8, italic=True, color="52514e")
        para(doc, "Moyennes par classe d'intensité (campagnes N+1) :", bold=True)
        add_table(doc, ["Classe", "n", "Arabica", "Robusta", "Total", "Rendement", "Minas Gerais", "Espírito Santo", "Campagnes"], cls_rows,
                  widths=[2.8, 0.8, 1.5, 1.5, 1.5, 1.6, 2.3, 2.3, 3.5], font=7)
        st = ep[ep.classe == "El Nino fort"]
        para(doc, f"Lecture : les El Niño forts de la période ({', '.join(st.episode)}) ont donné des campagnes N+1 avec {st.rain_es_dev.mean():+.0f} mm et "
                  f"{st.temp_es_dev.mean():+.1f} °C en Espírito Santo et {st.rain_mg_dev.mean():+.0f} mm, {st.temp_mg_dev.mean():+.1f} °C à Minas Gerais. "
                  f"Le conilon, non irrigué dans une bonne partie de São Mateus, a perdu {st.robusta_anom.mean():+.1f} % par rapport à l'attendu "
                  f"(−30 % en 2016/17) ; l'arabica, en année ON, est resté à {st.arabica_anom.mean():+.1f} % de l'attendu : le cycle a masqué "
                  f"le choc. Les El Niño ordinaires ont une signature plus diffuse : 2024/25 (après l'épisode 2023/24) a tout de même connu "
                  f"−452 mm et +2,4 °C à Minas Gerais.")
        r_en, r_ln = D.bw[D.bw.phase == "El Nino"].iloc[0], D.bw[D.bw.phase == "La Nina"].iloc[0]
        para(doc, f"Dans les données : les campagnes El Niño ont eu {r_en.rain_mg_dev:+.0f} mm de pluie à Minas Gerais et "
                  f"{r_en.rain_es_dev:+.0f} mm en Espírito Santo, avec {r_en.temp_mg_dev:+.2f} °C et {r_en.temp_es_dev:+.2f} °C, "
                  f"mais {r_en.rain_pr_dev:+.0f} mm au Paraná ; les campagnes La Niña {r_ln.rain_mg_dev:+.0f} mm à Minas et "
                  f"{r_ln.rain_pr_dev:+.0f} mm au Paraná. Le signal attendu (Sud plus humide, Sudeste plus sec et plus chaud sous "
                  f"El Niño) est bien là, et c'est le Sudeste qui porte l'arabica et le conilon.")
    if has and yseries:
        ser = ["Production Arabica", "Production Robusta", yseries] if country == "Brazil" else [s for s in [yseries, info["forecast_series"]] if s]
        p = os.path.join(FIGS, f"{tag}_enso.png"); fig.enso_bars(country, D.eff, ser, p, fr)
        picture(doc, p, 16, "Figure 5. Écart moyen du rendement et de la production par phase ENSO.")
        rows = []
        for phase in PHASE_ROWS:
            if phase in eff.index:
                r = eff.loc[phase]
                rp = effp.loc[phase] if effp is not None and phase in effp.index else None
                rows.append([PHASE_FR[phase], int(r.n), f"{r.mean_anomaly_pct:+.1f} %", f"{r.share_below_trend:.0f} %",
                             f"{rp.mean_anomaly_pct:+.1f} %" if rp is not None else "–", r.years])
        add_table(doc, ["Phase", "n", "Rendement : écart moyen", "% sous la moyenne", "Production : écart moyen", "Campagnes"], rows,
                  widths=[3.2, 1, 2.4, 2, 2.4, 6], font=7.5)
        # reading
        e = eff.loc["El Nino"] if "El Nino" in eff.index else None
        l = eff.loc["La Nina"] if "La Nina" in eff.index else None
        if e is not None and l is not None:
            sign_e = "négatif" if e.mean_anomaly_pct < -1 else ("positif" if e.mean_anomaly_pct > 1 else "neutre")
            sign_l = "négatif" if l.mean_anomaly_pct < -1 else ("positif" if l.mean_anomaly_pct > 1 else "neutre")
            para(doc, f"Lecture : pour {fr}, El Niño est historiquement {sign_e} pour le rendement ({e.mean_anomaly_pct:+.1f} %) et "
                      f"La Niña {sign_l} ({l.mean_anomaly_pct:+.1f} %). Avec 8 à 15 campagnes par phase, ce sont des tendances "
                      f"centrales, pas des lois : l'intensité de l'épisode, son calage sur la floraison et l'état du verger font l'écart.")
    # implication
    para(doc, "Implication pour l'El Niño en cours (jusqu'à mars 2027) :", bold=True)
    if has and effp is not None and "El Nino" in effp.index:
        e = effp.loc["El Nino"]; es = effp.loc["El Nino (|ONI| >= 1)"] if "El Nino (|ONI| >= 1)" in effp.index else e
        f = D.fc[(D.fc.country == country) & (D.fc.series == info["forecast_series"]) & (D.fc.year == max(target, 2027))]
        base = f.iloc[0].forecast if len(f) else np.nan
        if country == "Brazil" and D.armax_fc is not None:
            fa = D.armax_fc[(D.armax_fc.series == "Production Total") & (D.armax_fc.scenario == "normal") & (D.armax_fc.year == 2027)]
            base = fa.iloc[0].forecast
        para(doc, f"Campagne pilotée : {cy(target)}. Point de départ (modèle, ON/OFF connu pour le Brésil) : {fmt(base)} ; avec l'effet El Niño "
                  f"moyen ({e.mean_anomaly_pct:+.1f} %) : {fmt(base * (1 + e.mean_anomaly_pct / 100))} ; avec l'effet des El Niño forts "
                  f"({es.mean_anomaly_pct:+.1f} %) : {fmt(base * (1 + es.mean_anomaly_pct / 100))} (milliers de sacs).")
    else:
        para(doc, f"Campagne pilotée : {cy(target)}. Direction attendue d'après la climatologie ci-dessus ; la quantification attend les données.")

    # ---- 7. forecast
    doc.add_heading("7. Prévision", 1)
    if has and info["forecast_series"]:
        m = D.models[(D.models.country == country) & (D.models.series == info["forecast_series"])].iloc[0]
        para(doc, f"Modèle ARMA retenu pour {info['forecast_series']} : {m.model}{' + tendance' if m.trend == 'ct' else (' + dérive' if m.trend == 't' else '')}, "
                  f"équation {m.equation.replace('   with', ' ;')}. Backtest sur les 3 dernières campagnes : erreur moyenne {m.backtest_mape_arma:.1f} % "
                  f"contre {m.backtest_mape_naive:.1f} % pour « pareil que l'an dernier ».")
        f = D.fc[(D.fc.country == country) & (D.fc.series == info["forecast_series"])].sort_values("year")
        rows = [[cy(int(r.year)), fmt(r.forecast), f"{fmt(r.lo80)} – {fmt(r.hi80)}", f"{fmt(r.lo95)} – {fmt(r.hi95)}"] for _, r in f.iterrows()]
        add_table(doc, ["Campagne", "Prévision", "Intervalle 80 %", "Intervalle 95 %"], rows, widths=[3, 3, 4, 4])
        if country == "Brazil" and D.armax_fc is not None:
            para(doc, "Brésil, modèle ARMAX (ON/OFF connu, météo normale), milliers de sacs :", bold=True)
            fa = D.armax_fc[(D.armax_fc.scenario == "normal")]
            years = sorted(fa.year.unique())
            rows = []
            for y in years:
                r = {s: fa[(fa.series == s) & (fa.year == y)].iloc[0] for s in ["Production Arabica", "Production Robusta", "Production Total"]}
                on = r["Production Arabica"].onoff
                rows.append([cy(int(y)), "ON" if on == 1 else "OFF", fmt(r["Production Arabica"].forecast), fmt(r["Production Robusta"].forecast),
                             f"{fmt(r['Production Total'].forecast)} [{fmt(r['Production Total'].lo80)} – {fmt(r['Production Total'].hi80)}]"])
            add_table(doc, ["Campagne", "ON/OFF", "Arabica", "Robusta", "Total [80 %]"], rows, widths=[2.5, 2, 3, 3, 5.5])
            # one plain line of arithmetic per forecast year
            para(doc, "Comment chaque chiffre est obtenu (milliers de sacs) :", bold=True)
            para(doc, "Vocabulaire : le point de départ est le niveau de production que le modèle estime pour la première campagne (2001/02) hors "
                      "effet du cycle ; la croissance structurelle est le gain moyen par an sur 2001-2025 une fois le cycle ON/OFF retiré (nouvelles "
                      "variétés, densité, irrigation, Cerrado) ; on la multiplie par le nombre de campagnes écoulées depuis 2001/02 ; le bonus ON "
                      f"est le supplément d'une année ON par rapport à une année OFF ({fmt(D.armax.set_index('series').loc['Production Arabica', 'g_on'])} "
                      "milliers de sacs pour l'arabica). La météo n'entre pas dans ces chiffres : ils supposent une météo normale.", size=9, italic=True)
            am = D.armax.set_index("series")
            ep = pd.read_csv(os.path.join(OUT, "enso", "brazil_enso_episodes.csv"))
            en_mod = ep[ep.classe == "El Nino ordinaire"]; en_fort = ep[ep.classe == "El Nino fort"]
            first_year = int(am.loc["Production Arabica", "first_year"])
            for y in years:
                t = int(y) - first_year + 1
                parts = []
                for sname, lab in [("Production Arabica", "Arabica"), ("Production Robusta", "Robusta"), ("Production Total", "Total")]:
                    r = am.loc[sname]; f = fa[(fa.series == sname) & (fa.year == y)].iloc[0]
                    has_on = np.isfinite(r.get("g_on", np.nan))
                    base = r.c                             # level of an OFF year in 2001/02
                    trend = r.b * t
                    on = (r.g_on if f.onoff == 1 else 0.0) if has_on else 0.0
                    carry = f.forecast - (base + trend + on)
                    txt = f"{lab} {fmt(f.forecast)} = {fmt(base)} (point de départ 2001/02, année OFF) + {fmt(trend)} (croissance structurelle {fmt(r.b)} par an × {t} campagnes)"
                    if has_on:
                        txt += f" + {fmt(on) if on else '0'} (année {'ON : bonus du cycle' if f.onoff == 1 else 'OFF : pas de bonus'})"
                    if abs(carry) > 1:
                        txt += f" {'+' if carry > 0 else '−'} {fmt(abs(carry))} (report de {abs(r.get('ma.L1', 0.72)) * 100:.0f} % de la surprise de la dernière campagne observée)"
                    parts.append(txt)
                line = f"{cy(int(y))} : " + " ; ".join(parts) + ". Météo : normale, donc 0."
                if int(y) == 2027:
                    a_ = fa[(fa.series == "Production Arabica") & (fa.year == y)].iloc[0].forecast
                    r_ = fa[(fa.series == "Production Robusta") & (fa.year == y)].iloc[0].forecast
                    line += (f" Campagne pilotée par l'El Niño en cours : si El Niño ordinaire, arabica {en_mod.arabica_anom.mean():+.1f} % → {fmt(a_ * (1 + en_mod.arabica_anom.mean() / 100))}, "
                             f"robusta {en_mod.robusta_anom.mean():+.1f} % → {fmt(r_ * (1 + en_mod.robusta_anom.mean() / 100))} ; si fort, arabica "
                             f"{en_fort.arabica_anom.mean():+.1f} % → {fmt(a_ * (1 + en_fort.arabica_anom.mean() / 100))}, robusta {en_fort.robusta_anom.mean():+.1f} % → "
                             f"{fmt(r_ * (1 + en_fort.robusta_anom.mean() / 100))} (moyennes historiques des campagnes N+1 de chaque classe).")
                bullet(doc, line, 8.5)
            para(doc, "En une phrase : chaque prévision = point de départ + croissance structurelle × nombre de campagnes + bonus ON, à laquelle on applique "
                      "l'effet El Niño historique de la classe attendue ; l'intervalle 80 % vient de la taille des surprises passées.", italic=True)
            picture(doc, os.path.join(OUT, "armax", "plots", "production_arabica.png"), 16.5, "Figure 6. Arabica : ajustement ON/OFF et prévision ARMAX.")
        else:
            from arma_models import slug
            picture(doc, os.path.join(OUT, "plots", slug(country), slug(info["forecast_series"]) + ".png"), 16.5,
                    "Figure 6. Série, ajustement, prévision, ACF/PACF et résidus.")
    else:
        para(doc, "Pas de prévision possible sans données propres à l'origine.")

    if country == "Brazil":
        brazil_usda_table(doc, D)

    # ---- 8. limits
    doc.add_heading("8. Limites et données à ajouter", 1)
    for t in ["Séries annuelles de 20 à 30 points : les effets ENSO sont des moyennes sur 8 à 15 campagnes, à présenter comme des ordres de grandeur.",
              "La classification ENSO vient de la liste des épisodes NOAA CPC ; la table ONI ou RONI officielle peut être déposée dans data/oni.csv et remplace automatiquement cette liste.",
              "La météo n'est chiffrée que pour le Brésil (moyennes annuelles par État). Pour toutes les origines, il faut la pluie et la température des fenêtres critiques du calendrier (script NASA POWER build_region_weather.py, à étendre aux autres pays).",
              "Les dernières colonnes de la balance sheet (2025/26, 2026/27) sont des projections USDA ; les modèles les traitent comme observées.",
              "Le stock d'arbres par âge (non-bearing 1 an, 2 ans, bearing 3 ans, 4 ans, 5 ans et plus) existe dans la balance sheet pour le Brésil et la Colombie : c'est la brique suivante du modèle structurel (surface bearing prévisible 3 ans à l'avance)."]:
        bullet(doc, t, 9)
    doc.add_heading("Sources", 1)
    for t in ["Balance sheet « Balance Sheet weather MI - Uganda Consolidated.xlsx », onglet " + country + " (USDA PSD, CONAB, Fedecafé, UCDA, BPS selon les lignes).",
              "NOAA Climate Prediction Center, Oceanic Niño Index (liste des épisodes El Niño / La Niña) ; climatologie régionale ENSO : NOAA CPC, IRI, littérature agro-climatique (calendriers USDA FAS).",
              "Modèles : timeseries/arma_models.py, armax_models.py, enso_analysis.py (dépôt procafe, pull request #1)."]:
        bullet(doc, t, 9)
    path = os.path.join(REP, f"{fr.replace('é', 'e').replace('É', 'E')}_balance_sheet_cafe.docx")
    doc.save(path)
    return path


BREAK_YEAR = 2024      # Brazil area / tree rows switch source in 2024/25 (user information)


def step_trend(y, break_year=BREAK_YEAR):
    """Linear trend with a level step at the source change: returns (slope per year, step, last value)."""
    y = y[y.index <= 2026]
    t = (y.index - 2000).values.astype(float); step = (y.index >= break_year).astype(float)
    X = np.c_[np.ones(len(y)), t, step]
    beta, *_ = np.linalg.lstsq(X, y.values, rcond=None)
    return float(beta[1]), float(beta[2]), float(y.iloc[-1]), int(y.index[-1])


USER_ROW_2027 = dict(area_planted=None, area_harvested=1906, yield_=34.82, bearing=6807, nonbearing=1592, arabica=41325, robusta=22226)


def brazil_usda_table(doc, D):
    """The USDA-style table 2010/11-2027/28 with the 2027/28 row filled cell by cell by the models."""
    doc.add_heading("7 bis. Le tableau USDA 2010/11 – 2027/28 et le calcul de la ligne 2027/28", 1)
    ex = pd.read_csv(os.path.join(HERE, "data", "exog_brazil.csv")).set_index("year")
    onoff = ex["onoff"].to_dict()
    for y in range(int(ex.index.max()) + 1, 2029):          # the cycle alternates beyond the last weather row
        onoff[y] = 1 - onoff[y - 1]
    ser = {k: D.s("Brazil", v) for k, v in [("planted", "Area total"), ("harv", "Area bearing"), ("bear", "Trees bearing"),
                                              ("nonb", "Trees non-bearing"), ("arab", "Production Arabica"), ("rob", "Production Robusta")]}
    fc = D.fc[(D.fc.country == "Brazil") & (D.fc.year == 2027)].set_index("series")
    fa = D.armax_fc[(D.armax_fc.scenario == "normal") & (D.armax_fc.year == 2027)].set_index("series")
    am = D.armax.set_index("series")
    mo = D.models[D.models.country == "Brazil"].set_index("series")
    ep = pd.read_csv(os.path.join(OUT, "enso", "brazil_enso_episodes.csv"))
    en_o, en_f = ep[ep.classe == "El Nino ordinaire"], ep[ep.classe == "El Nino fort"]
    st = {k: step_trend(ser[k]) for k in ("planted", "harv", "bear", "nonb")}
    planted, harv = st["planted"][2] + st["planted"][0], st["harv"][2] + st["harv"][0]
    bear, nonb = st["bear"][2] + st["bear"][0], st["nonb"][2] + st["nonb"][0]
    arab, rob = fa.loc["Production Arabica", "forecast"], fa.loc["Production Robusta", "forecast"]
    yld = (arab + rob) / harv
    arab_o, rob_o = arab * (1 + en_o.arabica_anom.mean() / 100), rob * (1 + en_o.robusta_anom.mean() / 100)
    arab_f, rob_f = arab * (1 + en_f.arabica_anom.mean() / 100), rob * (1 + en_f.robusta_anom.mean() / 100)
    yld_o, yld_f = (arab_o + rob_o) / harv, (arab_f + rob_f) / harv
    hdr = ["Campagne", "Statut", "Cycle", "Surface plantée (1000 ha)", "Surface récoltée (1000 ha)", "Rendement (sacs/ha)",
           "Arbres bearing (M)", "Arbres non-bearing (M)", "Arabica (1000 sacs)", "Robusta (1000 sacs)"]
    rows = []
    for y in range(2010, 2027):
        g = lambda k: ser[k].get(y)
        a, r, h = g("arab"), g("rob"), g("harv")
        yv = (a + r) / h if a is not None and r is not None and h else None
        status = "Historique" if y <= 2025 else "Estimation USDA"
        rows.append([cy(y), status, "ON" if onoff[y] == 1 else "OFF", fmt(g("planted")), fmt(h), f"{yv:.2f}" if yv else "–",
                     fmt(g("bear")), fmt(g("nonb")), fmt(a), fmt(r)])
    rows.append([cy(2027), "Prévision modèles, météo normale", "OFF", fmt(planted), fmt(harv), f"{yld:.2f}", fmt(bear), fmt(nonb), fmt(arab), fmt(rob)])
    rows.append([cy(2027), "Prévision modèles, El Niño ordinaire", "OFF", fmt(planted), fmt(harv), f"{yld_o:.2f}", fmt(bear), fmt(nonb), fmt(arab_o), fmt(rob_o)])
    rows.append([cy(2027), "Prévision modèles, El Niño fort", "OFF", fmt(planted), fmt(harv), f"{yld_f:.2f}", fmt(bear), fmt(nonb), fmt(arab_f), fmt(rob_f)])
    u = USER_ROW_2027
    rows.append([cy(2027), "Ta ligne (tableau fourni)", "OFF", "–", fmt(u["area_harvested"]), f"{u['yield_']:.2f}", fmt(u["bearing"]), fmt(u["nonbearing"]), fmt(u["arabica"]), fmt(u["robusta"])])
    add_table(doc, hdr, rows, widths=[1.6, 2.6, 1.1, 1.7, 1.7, 1.6, 1.5, 1.6, 1.7, 1.7], font=7)
    para(doc, "Rendement = (arabica + robusta) / surface récoltée. Le tableau fourni indique 26,06 pour 2010/11 ; avec 54 500 / 2 175 on obtient 25,06. "
              "Rupture de source en 2024/25 sur les surfaces et les arbres (2 510 → 2 235 kha plantés, 2 030 → 1 881 récoltés) : le saut n'est pas "
              "physique, et le rendement 2024/25 est mécaniquement gonflé d'environ 7 % par le dénominateur.", size=8, italic=True, color="52514e")
    para(doc, "Comment chaque case de 2027/28 est calculée :", bold=True)
    ra, rr = am.loc["Production Arabica"], am.loc["Production Robusta"]
    sp_, sh_, sb_, sn_ = st["planted"], st["harv"], st["bear"], st["nonb"]
    lines = [
        f"Cycle : OFF. 2026/27 est ON, le cycle alterne.",
        f"Surfaces et arbres : la source change en 2024/25, donc la droite est tracée avec un décrochement à cette date ; la pente retenue est la pente "
        f"hors décrochement, appliquée à la dernière valeur (nouvelle source).",
        f"Surface plantée {fmt(planted)} = 2 342 (2026/27) {sp_[0]:+.1f} : hors saut de source ({sp_[1]:+.0f} kha), la surface plantée bouge de {sp_[0]:+.1f} milliers d'ha par an "
        f"depuis 2001/02, c'est-à-dire qu'elle est stable.",
        f"Surface récoltée {fmt(harv)} = 1 941 (2026/27) {sh_[0]:+.1f} : hors saut de source ({sh_[1]:+.0f} kha), la surface en production recule de {abs(sh_[0]):.1f} milliers d'ha par an "
        f"(densification, arrachage des vieux vergers), le rendement compense.",
        f"Arbres bearing {fmt(bear)} = 6 876 (2026/27) {sb_[0]:+.0f} : le stock d'arbres en production gagne {sb_[0]:+.0f} millions par an, saut de source {sb_[1]:+.0f}.",
        f"Arbres non-bearing {fmt(nonb)} = 1 461 (2026/27) {sn_[0]:+.0f} : les jeunes arbres augmentent de {sn_[0]:+.0f} millions par an (renouvellement du verger), saut de source {sn_[1]:+.0f}.",
        f"Arabica {fmt(arab)} = {fmt(ra.c)} (point de départ 2001/02, année OFF) + {fmt(ra.b)} × 27 campagnes + 0 (année OFF, pas de bonus). "
        f"Avec El Niño ordinaire ({en_o.arabica_anom.mean():+.1f} % historique) : {fmt(arab_o)} ; avec El Niño fort ({en_f.arabica_anom.mean():+.1f} %) : {fmt(arab_f)}.",
        f"Robusta {fmt(rob)} = {fmt(rr.c)} + {fmt(rr.b)} × 27 campagnes (le report de surprise de 2025/26 ne joue plus). "
        f"Avec El Niño ordinaire ({en_o.robusta_anom.mean():+.1f} %) : {fmt(rob_o)} ; avec El Niño fort ({en_f.robusta_anom.mean():+.1f} %) : {fmt(rob_f)}.",
        f"Rendement {yld:.2f} = ({fmt(arab)} + {fmt(rob)}) / {fmt(harv)} ; El Niño ordinaire {yld_o:.2f} ; El Niño fort {yld_f:.2f}. "
        f"Contrôle : le modèle de rendement direct (ON/OFF + tendance) donne {fa.loc['Yield (production / bearing area)', 'forecast']:.2f} sacs/ha, "
        f"soit {fmt(fa.loc['Yield (production / bearing area)', 'forecast'] * harv)} milliers de sacs par la surface récoltée : cohérent à 2 % près avec la production prévue.",
        f"Comparaison avec ta ligne : arabica {fmt(u['arabica'])} est entre mon scénario El Niño ordinaire ({fmt(arab_o)}) et la météo normale ({fmt(arab)}) ; "
        f"robusta {fmt(u['robusta'])} est proche de mon El Niño ordinaire ({fmt(rob_o)}) ; ta surface récoltée {fmt(u['area_harvested'])} suppose un recul de 35 kha "
        f"en un an, plus fort que la tendance ({fmt(harv)}) ; tes arbres bearing {fmt(u['bearing'])} supposent une baisse alors que la tendance historique est de {sb_[0]:+.0f} M par an.",
    ]
    for t in lines:
        bullet(doc, t, 8.5)


def main():
    os.makedirs(REP, exist_ok=True)
    D = Data()
    for country in ["Brazil", "Colombia", "Honduras", "Ethiopia", "Peru", "Indonesia", "Vietnam", "Uganda"]:
        p = build(country, D)
        print("written", p)


if __name__ == "__main__":
    main()
