/**
 * Gera docs/veille_meteo_cafe.docx: uma pagina por pais (Colombia, Brasil) com
 * as fontes de meteorologia a consultar, para que serve cada uma, com que
 * frequencia olhar, e o calendario das janelas criticas do cafe.
 */
const fs = require("fs");
const path = require("path");
const docx = require("/tmp/claude-0/-home-user-procafe/bcbe7d70-5524-5da9-b23b-ad96b9b67263/scratchpad/node_modules/docx");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, ShadingType, BorderStyle, AlignmentType, HeadingLevel,
  PageBreak, ExternalHyperlink, LevelFormat, convertMillimetersToTwip,
} = docx;

const FONT = "Arial";
const NAVY = "1B2A41";
const BLUE = "4472C4";
const ORANGE = "C55A11";
const GREY = "595959";
const LINE = "D9D9D9";

// A4 retrato, margens de 18 mm -> largura util
const MARGIN = convertMillimetersToTwip(18);
const CONTENT = 11906 - 2 * MARGIN;
const COLS = [1650, 3500, 1750, CONTENT - 1650 - 3500 - 1750];

const t = (text, o = {}) => new TextRun({ text, font: FONT, size: o.size || 17, bold: o.bold, italics: o.italics, color: o.color || "262626" });

const cell = (children, o = {}) =>
  new TableCell({
    width: { size: o.width, type: WidthType.DXA },
    shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: "auto" } : undefined,
    margins: { top: 40, bottom: 40, left: 90, right: 90 },
    children,
  });

const para = (runs, o = {}) =>
  new Paragraph({
    children: runs,
    spacing: { before: o.before || 0, after: o.after === undefined ? 10 : o.after },
    alignment: o.alignment,
  });

function sourcesTable(rows) {
  const head = new TableRow({
    tableHeader: true,
    children: ["Source", "Ce que tu y trouves", "Quand y aller", "Lien"].map((h, i) =>
      cell([para([t(h, { bold: true, color: "FFFFFF", size: 16 })], { after: 0 })], { width: COLS[i], fill: NAVY })
    ),
  });
  const body = rows.map((r, idx) =>
    new TableRow({
      children: [
        cell([para([t(r.name, { bold: true, color: NAVY })], { after: 0 })], { width: COLS[0], fill: idx % 2 ? "F5F7FA" : undefined }),
        cell([para([t(r.what)], { after: 0 })], { width: COLS[1], fill: idx % 2 ? "F5F7FA" : undefined }),
        cell([para([t(r.when, { color: ORANGE })], { after: 0 })], { width: COLS[2], fill: idx % 2 ? "F5F7FA" : undefined }),
        cell([para([new ExternalHyperlink({
          link: "https://" + r.url,
          children: [new TextRun({ text: r.url, font: FONT, size: 16, color: BLUE, underline: {} })],
        })], { after: 0 })], { width: COLS[3], fill: idx % 2 ? "F5F7FA" : undefined }),
      ],
    })
  );
  return new Table({
    columnWidths: COLS,
    width: { size: CONTENT, type: WidthType.DXA },
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color: LINE },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: LINE },
      left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
      right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 4, color: LINE },
      insideVertical: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
    },
    rows: [head, ...body],
  });
}

const CAL_COLS = [2200, CONTENT - 2200];
function calendarTable(rows) {
  const head = new TableRow({
    tableHeader: true,
    children: ["Période", "Ce qui se joue / ce que tu surveilles"].map((h, i) =>
      cell([para([t(h, { bold: true, color: "FFFFFF", size: 16 })], { after: 0 })], { width: CAL_COLS[i], fill: NAVY })
    ),
  });
  const body = rows.map((r, idx) =>
    new TableRow({
      children: [
        cell([para([t(r.when, { bold: true, color: ORANGE })], { after: 0 })], { width: CAL_COLS[0], fill: idx % 2 ? "F5F7FA" : undefined }),
        cell([para([t(r.what)], { after: 0 })], { width: CAL_COLS[1], fill: idx % 2 ? "F5F7FA" : undefined }),
      ],
    })
  );
  return new Table({
    columnWidths: CAL_COLS,
    width: { size: CONTENT, type: WidthType.DXA },
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color: LINE },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: LINE },
      left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
      right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 4, color: LINE },
      insideVertical: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
    },
    rows: [head, ...body],
  });
}

const h1 = (text, sub) => [
  new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { after: 60 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: BLUE, space: 6 } },
    children: [new TextRun({ text, font: FONT, size: 26, bold: true, color: NAVY })],
  }),
  para([t(sub, { italics: true, color: GREY, size: 17 })], { after: 200 }),
];

const h2 = (text) =>
  new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 160, after: 70 },
    children: [new TextRun({ text, font: FONT, size: 20, bold: true, color: BLUE })],
  });

const routine = (items) =>
  items.map((it) =>
    new Paragraph({
      numbering: { reference: "puces", level: 0 },
      spacing: { after: 40 },
      children: [t(it.label + " : ", { bold: true }), t(it.text)],
    })
  );

/* ----------------------------------------------------------- COLOMBIE ---- */
const COL_SOURCES = [
  { name: "IDEAM", what: "Service météo national : prévisions, radar, pluie par station, alertes, bulletins ENSO officiels.", when: "Quotidien", url: "www.ideam.gov.co" },
  { name: "Cenicafé (FNC)", what: "Stations situées dans les zones caféières + bulletin agroclimatique café (floraison, roya, broca). La source la plus fine.", when: "Mensuel", url: "www.cenicafe.org" },
  { name: "Fed. Nac. de Cafeteros", what: "Production et exportations mensuelles, état de la récolte.", when: "Mensuel (vers le 5-10)", url: "federaciondecafeteros.org" },
  { name: "Windy", what: "ECMWF / GFS / ICON comparés sur un même point, 1 à 15 j. Le meilleur pour voir si les modèles divergent.", when: "Quotidien", url: "www.windy.com" },
  { name: "Meteoblue", what: "Meteogram multimodèle 14 j par municipe, relief fin — décisif entre 1 200 et 2 000 m.", when: "2-3 fois/semaine", url: "www.meteoblue.com" },
  { name: "Zoom Earth", what: "Satellite GOES-16 quasi temps réel : convection de l'après-midi.", when: "Pendant un épisode", url: "zoom.earth" },
  { name: "NOAA CPC", what: "ENSO Diagnostic Discussion (statut officiel El Niño / La Niña) + anomalies saisonnières.", when: "Mensuel (2e jeudi)", url: "www.cpc.ncep.noaa.gov" },
  { name: "IRI Columbia", what: "Probabilités ENSO par trimestre, prévisions saisonnières en cartes.", when: "Mensuel", url: "iri.columbia.edu" },
  { name: "CHIRPS", what: "Anomalies de pluie par décade et par mois : dit si le déficit est vraiment anormal.", when: "Mensuel", url: "www.chc.ucsb.edu/data/chirps" },
  { name: "Open-Meteo", what: "API gratuite sans clé : prévision 16 j + historique. Pour automatiser dans procafe.", when: "Intégration", url: "open-meteo.com" },
  { name: "NASA POWER", what: "Historique quotidien depuis 1981 (latence ~4 j) : bilan hydrique, écart à la normale.", when: "Mensuel", url: "power.larc.nasa.gov" },
];

const COL_CAL = [
  { when: "Déc. - févr.", what: "Période la plus sèche. Surveiller le déficit cumulé : il conditionne la floraison qui suit." },
  { when: "Févr. - mars", what: "FLORAISON PRINCIPALE. Il faut des pluies de reprise ; un démarrage sec ampute la récolte d'octobre-janvier." },
  { when: "Mars - mai", what: "1re saison des pluies, remplissage des grains de la mitaca. Excès = roya, déficit = petits grains." },
  { when: "Avril - juin", what: "RÉCOLTE MITACA (30-40 % du volume). L'excès de pluie pénalise la cueillette et surtout le séchage." },
  { when: "Août - sept.", what: "FLORAISON SECONDAIRE : elle détermine la mitaca de l'année suivante." },
  { when: "Sept. - nov.", what: "2e saison des pluies : remplissage des grains de la récolte principale, phase très sensible au déficit." },
  { when: "Oct. - janv.", what: "RÉCOLTE PRINCIPALE (60-70 %). Excès de pluie = qualité, séchage, glissements, logistique." },
  { when: "Toute l'année", what: "ENSO : El Niño = déficit de pluie et chaleur (broca) ; La Niña = excès de pluie, floraisons noyées, roya." },
];

/* ------------------------------------------------------------- BRESIL ---- */
const BRA_SOURCES = [
  { name: "INMET", what: "Service météo national : prévisions, stations automatiques, cartes d'anomalies, avisos de geada.", when: "Quotidien", url: "portal.inmet.gov.br" },
  { name: "CPTEC / INPE", what: "Modèles régionaux, prévisions étendues, satellite, prévision de gelée.", when: "Quotidien", url: "www.cptec.inpe.br" },
  { name: "Somar Meteorologia", what: "Suivi agro-météo orienté café : cartes de pluie et bulletins. Lecture de référence du trade.", when: "Quotidien / hebdo", url: "www.somarmeteorologia.com.br" },
  { name: "Rural Clima", what: "Analyses agro-météo café (Marco Antônio dos Santos), commentaires par région.", when: "Quotidien", url: "www.ruralclima.com.br" },
  { name: "Climatempo", what: "Prévisions par municipe, cumuls de pluie, tendances 30 jours.", when: "Quotidien", url: "www.climatempo.com.br" },
  { name: "Fundação Procafé", what: "Bulletins techniques par région, vus du terrain : floração, granação, dégâts de gelée ou de sécheresse.", when: "Mensuel", url: "www.fundacaoprocafe.com.br" },
  { name: "CONAB", what: "Estimations officielles de récolte (levantamentos) : surfaces, rendements, volumes.", when: "Janv., mai, sept., déc.", url: "www.conab.gov.br" },
  { name: "Monitor de Secas (ANA)", what: "Carte mensuelle officielle de l'intensité de la sécheresse par État.", when: "Mensuel", url: "monitordesecas.ana.gov.br" },
  { name: "Windy / Meteoblue / Zoom Earth", what: "Comparaison de modèles, meteogram par ville, satellite temps réel — même usage qu'en Colombie.", when: "Quotidien", url: "www.windy.com" },
  { name: "NOAA CPC / IRI", what: "Statut ENSO : le pilote principal des sécheresses du Sud-Est brésilien.", when: "Mensuel", url: "www.cpc.ncep.noaa.gov" },
  { name: "NASA POWER", what: "Source déjà utilisée par procafe : historique quotidien depuis 1981, bilan hydrique.", when: "Mensuel", url: "power.larc.nasa.gov" },
];

const BRA_CAL = [
  { when: "Mai - sept.", what: "Saison sèche : récolte et séchage. Des pluies hors saison provoquent des défauts (fermentation, moisissures)." },
  { when: "Juin - juillet", what: "GELÉE (geada) : Sul de Minas, Mogiana, Paraná. Alerte après un front froid, nuit claire et sans vent — avisos INMET / CPTEC." },
  { when: "Sept. - oct.", what: "FLORAISON, déclenchée par les premières pluies. Des pluies en pointillé donnent plusieurs floraisons et une maturation hétérogène." },
  { when: "Oct. - déc.", what: "Nouaison (pegamento, chumbinho) : un veranico de 10-15 jours fait avorter les jeunes fruits." },
  { when: "Déc. - févr.", what: "GRANAÇÃO (remplissage) : phase la plus sensible au déficit hydrique, elle fixe le calibre. Sec = grains petits / moka." },
  { when: "Janvier", what: "Fenêtre classique de veranico : à surveiller de très près, c'est là que se perdent les récoltes." },
  { when: "Toute l'année", what: "ENSO : La Niña = tendance sèche sur le Sud-Est et le Cerrado ; El Niño = plus de pluie, mais risque de pluie sur la récolte." },
];

/* ------------------------------------------------------------- DOC ------- */
const doc = new Document({
  creator: "procafe",
  title: "Veille météo café — Colombie et Brésil",
  description: "Où regarder, pour quoi, à quelle fréquence.",
  numbering: {
    config: [{
      reference: "puces",
      levels: [{
        level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 340, hanging: 200 } } },
      }],
    }],
  },
  styles: { default: { document: { run: { font: FONT, size: 17 } } } },
  sections: [{
    properties: { page: { margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN } } },
    children: [
      ...h1("Veille météo café — COLOMBIE", "Où regarder, pour quoi, à quelle fréquence. Régime bimodal, deux récoltes par an."),
      h2("1. Les sources, par ordre d'utilité"),
      sourcesTable(COL_SOURCES),
      h2("2. Ta routine"),
      ...routine([
        { label: "Chaque jour", text: "Windy (comparer les modèles sur Huila / Eje Cafetero) + prévisions IDEAM." },
        { label: "Chaque semaine", text: "Meteoblue sur 3-4 municipes témoins ; cumuls de pluie des 7 derniers jours." },
        { label: "Chaque mois", text: "Bulletin Cenicafé, ENSO Diagnostic Discussion du CPC, anomalies CHIRPS, production FNC." },
      ]),
      h2("3. Les fenêtres critiques"),
      calendarTable(COL_CAL),
      para([t("Zones à suivre : Huila, Nariño, Tolima, Cauca, Antioquia, Santander et l'Eje Cafetero (Caldas, Quindío, Risaralda). À 1 200-2 000 m, deux municipes voisins peuvent avoir des pluies très différentes : garder 3-4 points témoins plutôt qu'une moyenne nationale.", { italics: true, color: GREY, size: 17 })], { before: 200 }),

      new Paragraph({ children: [new PageBreak()] }),

      ...h1("Veille météo café — BRÉSIL", "Où regarder, pour quoi, à quelle fréquence. Une récolte par an, cycle biennal ON/OFF."),
      h2("1. Les sources, par ordre d'utilité"),
      sourcesTable(BRA_SOURCES),
      h2("2. Ta routine"),
      ...routine([
        { label: "Chaque jour", text: "Rural Clima ou Somar (lecture agro) + Windy pour la pluie à 10 jours ; de mai à août, avisos de geada INMET / CPTEC." },
        { label: "Chaque semaine", text: "Cumuls de pluie par région (Sul de Minas, Cerrado, Mogiana, Matas de Minas) et écart à la normale." },
        { label: "Chaque mois", text: "Bulletin Fundação Procafé, Monitor de Secas, ENSO du CPC ; CONAB à chaque levantamento." },
      ]),
      h2("3. Les fenêtres critiques"),
      calendarTable(BRA_CAL),
      para([t("Régions à suivre : Sul de Minas, Cerrado Mineiro, Mogiana, Matas de Minas (arabica), Espírito Santo et Rondônia (conilon). Le cycle biennal amplifie tout : une année ON amputée par un veranico coûte bien plus qu'une année OFF.", { italics: true, color: GREY, size: 17 })], { before: 200 }),
      para([t("Note : les adresses ci-dessus sont données de mémoire — la politique réseau de l'environnement de génération n'a pas permis de les tester une par une. Vérifie-les au premier usage et corrige ce document si l'une a bougé.", { italics: true, color: GREY, size: 16 })], { before: 160 }),
    ],
  }],
});

const out = path.join(__dirname, "veille_meteo_cafe.docx");
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(out, buf); console.log("ok ->", out); });
