# procafe — notes pour Claude Code

## Le projet
Site statique (HTML/JS, pas de build) qui affiche les données climat des régions
café du Brésil. `config.js` liste les régions/villes, `data/*.js` contient les
tables mensuelles (retapées depuis les rapports Procafé) et les courbes
digitalisées, `build_data.py` régénère `data/sul_de_minas_graphs.js` depuis
NASA POWER. Ouvrir `index.html` dans un navigateur suffit pour tester.

## Chantier en cours : marges des producteurs brésiliens vs production
Branche : `claude/bresil-profit-margin-analysis-6xkhjy`.

Question de départ : au-delà de la météo, les fluctuations de production
d'arabica au Brésil sont-elles liées à la marge des producteurs ?

### Conclusion provisoire (session cloud du 2026-09-07, sans Bloomberg)
- Le premier facteur reste la biennalité physiologique (+/- 5 à 10 M sacs),
  le second la météo (sécheresse 2014, sécheresse 2020 + gel juillet 2021,
  chaleur/sécheresse fin 2024 et fév-mars 2025).
- La marge agit sur l'amplitude et la tendance, avec retard :
  - intensité de fertilisation (engrais ~43 % du coût variable), effet à 1-2 ans ;
  - taille/renouvellement : prix hauts -> on saute la taille -> verger vieilli
    (StoneX 2026/27), effet à 2-4 ans ;
  - nouvelles plantations, effet à 3-4 ans, élasticité mesurée faible.
- Le producteur raisonne en BRL : le change USDBRL fait partie de la marge.
- Une marge par sac est biaisée par le cycle (coût fixe / rendement variable).
  Préférer la marge par hectare sur 2 ans et le ratio d'échange café/engrais.

### Données déjà trouvées (R$ nominaux / sac 60 kg, indicateur Cepea arabica type 6)
Voir `data/bresil_margins.csv` et `docs/bresil_margins.md` (méthode, tableau, limites).

### Ce qu'il faut tirer de Bloomberg dans le terminal local
1. `KC1 Comdty` et `KCA Comdty` : arabica ICE NY, moyennes annuelles et par
   campagne (juil-juin), en USc/lb.
2. `USDBRL Curncy` : moyennes annuelles, pour convertir en R$/sac
   (1 sac = 60 kg = 132,28 lb).
3. Indices engrais Green Markets / CRU (urée, KCl, MAP, ou blend 20-05-20 si
   disponible) : vérifier les tickers avec FLDS/ALLX avant usage, ne pas les
   inventer. Objectif : ratio sacs de café par tonne d'engrais, série annuelle.
4. Chercher si l'indicateur Cepea/Esalq arabica existe sur Bloomberg (ECST,
   recherche "CEPEA"). Sinon le télécharger sur cepea.org.br (série depuis 2001).
5. Optionnel : BI coffee dashboard pour les coûts par pays s'ils y sont.

### Ce qui n'est PAS sur Bloomberg et doit venir de sources publiques
- Coûts de production Conab par municipe (Guaxupé, Patrocínio, Franca,
  Manhuaçu, etc.), série 2003-2023+, R$/ha et R$/sac, coût variable /
  opérationnel / total : conab.gov.br > Custos de Produção > Café arábica.
- Production et rendement Conab par année et par UF :
  portaldeinformacoes.conab.gov.br/safra-serie-historica-cafe.html.
Les fichiers Excel Conab se déposent dans `data/raw/` (créer le dossier).

### Livrable visé
Un onglet "Marges" dans le site (ou une page `regions/margins.html`) avec :
- production arabica Conab par année ;
- prix Cepea moyen par campagne, en R$ et converti USD ;
- coût Conab total par sac et par ha ;
- marge par sac, marge par ha lissée sur 2 ans, ratio café/engrais ;
- superposition avec les anomalies de pluie du site pour séparer météo et marge.

## Conventions
- Pas de framework, pas de bundler : JS vanilla, fichiers `data/*.js` qui
  posent un objet sur `window`.
- Les valeurs digitalisées sont approximatives et signalées comme telles dans l'UI.
- Ne pas mettre d'identifiant de modèle dans les commits ni dans le code.
