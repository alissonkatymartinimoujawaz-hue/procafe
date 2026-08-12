// Site configuration — Brazil / coffee regions
// One region = several towns. lat/lon feed the NASA POWER requests.
window.SITE_CONFIG = {
  country: "Brazil",
  updated: null, // filled by the Python script when data is generated
  regions: [
    {
      id: "sul_de_minas",
      name: "Sul de Minas",
      type: "Arabica",
      blurb: "The historic heart of Brazilian arabica: 900–1200 m altitude, a marked dry season (May–Sep), harvest May–August.",
      cities: [
        { id: "varginha",       name: "Varginha",       lat: -21.5667, lon: -45.4061, alt: 940,  latDMS: "21°34'00\"S", lonDMS: "45°24'22\"W" },
        { id: "carmo_de_minas", name: "Carmo de Minas", lat: -22.1753, lon: -45.1508, alt: 1080, latDMS: "22°10'31\"S", lonDMS: "45°09'03\"W" },
        { id: "boa_esperanca",  name: "Boa Esperança",  lat: -21.0664, lon: -45.5769, alt: 830,  latDMS: "21°03'59\"S", lonDMS: "45°34'37\"W" },
        { id: "guape",          name: "Guapé",          lat: -20.7344, lon: -46.0853, alt: 788,  latDMS: "20°44'03.88\"S", lonDMS: "46°05'07.02\"W" },
        { id: "muzambinho",     name: "Muzambinho",     lat: -21.3464, lon: -46.5344, alt: 1033, latDMS: "21°20'47\"S", lonDMS: "46°32'04\"W" }
      ]
    },
    {
      id: "cerrado",
      name: "Cerrado",
      type: "Arabica",
      blurb: "Cerrado Mineiro (Triângulo Mineiro / Alto Paranaíba), a Denomination of Origin terroir: 900–1000 m plateaus, a very clear dry season, heavy mechanization and irrigation.",
      cities: [
        { id: "araxa",      name: "Araxá",      lat: -19.5558, lon: -46.9689, alt: 960, latDMS: "19°33'21\"S", lonDMS: "46°58'08\"W" },
        { id: "patrocinio", name: "Patrocínio", lat: -18.9931, lon: -46.9836, alt: 961, latDMS: "18°59'35\"S", lonDMS: "46°59'01\"W" },
        { id: "araguari",   name: "Araguari",   lat: -18.5561, lon: -48.2069, alt: 933, latDMS: "18°33'21.9\"S", lonDMS: "48°12'25\"W" }
      ]
    },
    {
      id: "mogiana",
      name: "Mogiana",
      type: "Arabica",
      blurb: "Mogiana Paulista, on the SP/MG border: 900–1100 m hills, volcanic soils, smooth full-bodied coffees.",
      cities: [
        { id: "franca",      name: "Franca",      lat: -20.539, lon: -47.401 },
        { id: "altinopolis", name: "Altinópolis", lat: -21.023, lon: -47.373 },
        { id: "cravinhos",   name: "Cravinhos",   lat: -21.340, lon: -47.729 },
        { id: "batatais",    name: "Batatais",    lat: -20.891, lon: -47.588 },
        { id: "pedregulho",  name: "Pedregulho",  lat: -20.258, lon: -47.477 }
      ]
    },
    {
      id: "matas_de_minas",
      name: "Matas de Minas",
      type: "Arabica",
      blurb: "Zona da Mata, rugged terrain: small family farms, more spread-out rainfall, a wide range of microclimates.",
      cities: [
        { id: "manhuacu",     name: "Manhuaçu",     lat: -20.257, lon: -42.033 },
        { id: "caratinga",    name: "Caratinga",    lat: -19.790, lon: -42.139 },
        { id: "espera_feliz", name: "Espera Feliz", lat: -20.651, lon: -41.907 },
        { id: "carangola",    name: "Carangola",    lat: -20.730, lon: -42.029 },
        { id: "muriae",       name: "Muriaé",       lat: -21.130, lon: -42.366 }
      ]
    }
  ]
};
