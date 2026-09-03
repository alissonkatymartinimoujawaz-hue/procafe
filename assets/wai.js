/* Irrigation / Water Availability Index — Central Highlands (Tay Nguyen), Vietnam.
 *
 * Everything the page shows is computed here, from raw NASA POWER daily series,
 * so the pre-built snapshot (build_water_index.py) and a live browser fetch
 * always produce identical numbers.
 *
 * Inputs per station:  p (mm/day), gt/gr/gp (soil wetness 0-1 at surface /
 * root zone / whole profile), t, tx, tn (degC).
 *
 * Outputs: rainfall totals + anomalies, soil-moisture percentiles, a modelled
 * groundwater reservoir, a 0-100 composite index, and an irrigation signal.
 */
(function () {
  "use strict";

  var C = {
    BASE_FROM: 1991, BASE_TO: 2020,          // WMO normal used as the reference
    W_RAIN: 0.35, W_SOIL: 0.35, W_RES: 0.30, // composite weights
    RES_TAU: 150,        // linear-reservoir recession time constant, days
    RES_P_MIN: 5,        // rain below this is assumed lost to ET/interception, mm
    RES_GATE_LO: 0.55,   // profile wetness below which no deep percolation occurs
    RES_GATE_HI: 0.90,   // profile wetness at which percolation is unimpeded
    RES_FRAC: 0.5,       // share of gated excess rain reaching the slow store
    KC: 0.90,            // crop coefficient, mature robusta
    ROUND_MM: 44,        // one irrigation round: 400 L/tree x 1100 trees/ha
    DRY_START: [11, 15], // dry-season anchor (15 Nov) for the deficit count
    TRIG_GR: 0.40,       // root-zone wetness triggering a round
    CATS: [
      { max: 20,  key: "severe",  label: "Severe deficit" },
      { max: 40,  key: "deficit", label: "Deficit" },
      { max: 60,  key: "normal",  label: "Near normal" },
      { max: 80,  key: "comfort", label: "Comfortable" },
      { max: 101, key: "surplus", label: "Surplus" }
    ]
  };

  /* ---------------- dates ---------------- */
  var MS = 86400000;
  function ymdToUTC(s) { return Date.UTC(+s.slice(0, 4), +s.slice(4, 6) - 1, +s.slice(6, 8)); }
  function fmt(ms) {
    var d = new Date(ms), p = function (v) { return (v < 10 ? "0" : "") + v; };
    return d.getUTCFullYear() + p(d.getUTCMonth() + 1) + p(d.getUTCDate());
  }
  function dateAxis(start, n) {
    var t0 = ymdToUTC(start), y = [], m = [], d = [], ymd = [], doy = [];
    for (var i = 0; i < n; i++) {
      var dt = new Date(t0 + i * MS), yy = dt.getUTCFullYear();
      y.push(yy); m.push(dt.getUTCMonth() + 1); d.push(dt.getUTCDate());
      doy.push(Math.floor((dt.getTime() - Date.UTC(yy, 0, 1)) / MS) + 1);
      ymd.push(fmt(t0 + i * MS));
    }
    return { t0: t0, y: y, m: m, d: d, doy: doy, ymd: ymd };
  }

  /* ---------------- small stats ---------------- */
  function rolling(a, n, minFrac) {
    var out = new Array(a.length), sum = 0, cnt = 0, i, v, o;
    minFrac = minFrac == null ? 0.8 : minFrac;
    for (i = 0; i < a.length; i++) {
      v = a[i]; if (v != null) { sum += v; cnt++; }
      if (i >= n) { o = a[i - n]; if (o != null) { sum -= o; cnt--; } }
      out[i] = (i >= n - 1 && cnt >= n * minFrac) ? sum : null;
    }
    return out;
  }
  function quantiles(sorted) {                 // 21 points: 0, 5, ... 100 %
    var q = [], i, x, lo;
    if (!sorted.length) return null;
    for (i = 0; i <= 20; i++) {
      x = (sorted.length - 1) * i / 20; lo = Math.floor(x);
      q.push(lo >= sorted.length - 1 ? sorted[sorted.length - 1]
        : sorted[lo] + (sorted[lo + 1] - sorted[lo]) * (x - lo));
    }
    return q;
  }
  function pctOf(q, v) {                       // value -> percentile of the baseline
    if (q == null || v == null) return null;
    if (v < q[0]) return 0;
    if (v > q[20]) return 100;
    var lo = -1, hi = -1, i;                  // plateau of equal quantiles = tied values
    for (i = 0; i <= 20; i++) {
      if (q[i] === v) { if (lo < 0) lo = i; hi = i; }
    }
    if (lo >= 0) return 2.5 * (lo + hi);       // mid-rank of the tie (5 * (lo+hi)/2)
    for (i = 0; i < 20; i++) {
      if (v < q[i + 1]) {
        var span = q[i + 1] - q[i];
        return 5 * (i + (span > 0 ? (v - q[i]) / span : 0.5));
      }
    }
    return 100;
  }
  /* Seasonal baseline. The reference is built on 36 nodes of ~10 days (each fed by a
     +/-15-day window of the 1991-2020 years) and interpolated between node centres, so
     percentiles move smoothly through the season instead of jumping on the 1st of a month. */
  var NODES = 36, NODE_LEN = 365 / NODES;
  function nodeOf(doy) { return Math.min(NODES - 1, Math.floor((doy - 1) / NODE_LEN)); }
  function nodeBlend(doy) {
    var x = (doy - 1) / NODE_LEN - 0.5, a = Math.floor(x), w = x - a;
    return [((a % NODES) + NODES) % NODES, (((a + 1) % NODES) + NODES) % NODES, w];
  }
  function seasonClim(vals, ax) {
    var buckets = [], i, k, o;
    for (i = 0; i < NODES; i++) buckets.push([]);
    for (i = 0; i < vals.length; i++) {
      if (vals[i] == null || ax.y[i] < C.BASE_FROM || ax.y[i] > C.BASE_TO) continue;
      k = nodeOf(ax.doy[i]);
      for (o = -1; o <= 1; o++) buckets[((k + o) % NODES + NODES) % NODES].push(vals[i]);
    }
    var q = [], mean = [];
    for (k = 0; k < NODES; k++) {
      buckets[k].sort(function (a, b) { return a - b; });
      q.push(quantiles(buckets[k]));
      mean.push(buckets[k].length
        ? buckets[k].reduce(function (a, b) { return a + b; }, 0) / buckets[k].length : null);
    }
    return { q: q, mean: mean, nodes: NODES };
  }
  function blendQ(qs, bl) {
    var qa = qs[bl[0]], qb = qs[bl[1]], i, out;
    if (!qa) return qb;
    if (!qb) return qa;
    out = new Array(21);
    for (i = 0; i <= 20; i++) out[i] = qa[i] + (qb[i] - qa[i]) * bl[2];
    return out;
  }
  function blendMean(means, bl) {
    var a = means[bl[0]], b = means[bl[1]];
    if (a == null) return b;
    if (b == null) return a;
    return a + (b - a) * bl[2];
  }
  function pctSeries(vals, clim, ax) {
    var out = new Array(vals.length), i;
    for (i = 0; i < vals.length; i++)
      out[i] = pctOf(blendQ(clim.q, nodeBlend(ax.doy[i])), vals[i]);
    return out;
  }
  /* Smooth daily normal for the "normal" reference lines on the charts. */
  function normalSeries(means, ax, i0, n) {
    var out = new Array(n), i;
    for (i = 0; i < n; i++) out[i] = blendMean(means, nodeBlend(ax.doy[i0 + i]));
    return out;
  }
  function normalAt(means, ax, i) {
    var v = blendMean(means, nodeBlend(ax.doy[i]));
    return v == null ? null : Math.round(v);
  }
  function climQAt(clim, ax, i) { return blendQ(clim.q, nodeBlend(ax.doy[i])); }
  /* Rank-based SPI equivalent: percentile -> normal deviate (Acklam, central branch). */
  function invNorm(p) {
    p = Math.min(0.9995, Math.max(0.0005, p));
    var a = [-39.69683028665376, 220.9460984245205, -275.9285104469687,
             138.3577518672690, -30.66479806614716, 2.506628277459239],
        b = [-54.47609879822406, 161.5858368580409, -155.6989798598866,
             66.80131188771972, -13.28068155288572],
        c = [-0.007784894002430293, -0.3223964580411365, -2.400758277161838,
             -2.549732539343734, 4.374664141464968, 2.938163982698783],
        d = [0.007784695709041462, 0.3224671290700398, 2.445134137142996, 3.754408661907416],
        pl = 0.02425, q, r;
    if (p < pl) {
      q = Math.sqrt(-2 * Math.log(p));
      return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) /
             ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1);
    }
    if (p > 1 - pl) {
      q = Math.sqrt(-2 * Math.log(1 - p));
      return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) /
              ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1);
    }
    q = p - 0.5; r = q * q;
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q /
           (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1);
  }

  /* ---------------- physics ---------------- */
  function hargreaves(t, tx, tn, lat, ax) {     // reference ET0, mm/day
    var phi = lat * Math.PI / 180, out = new Array(t.length), i;
    for (i = 0; i < t.length; i++) {
      if (t[i] == null || tx[i] == null || tn[i] == null) { out[i] = null; continue; }
      var doy = Math.floor((Date.UTC(ax.y[i], ax.m[i] - 1, ax.d[i]) -
                            Date.UTC(ax.y[i], 0, 1)) / MS) + 1,
          dr = 1 + 0.033 * Math.cos(2 * Math.PI * doy / 365),
          de = 0.409 * Math.sin(2 * Math.PI * doy / 365 - 1.39),
          x = Math.max(-1, Math.min(1, -Math.tan(phi) * Math.tan(de))),
          ws = Math.acos(x),
          Ra = 1440 / Math.PI * 0.0820 * dr *
               (ws * Math.sin(phi) * Math.sin(de) + Math.cos(phi) * Math.cos(de) * Math.sin(ws));
      out[i] = Math.max(0, 0.0023 * (t[i] + 17.8) *
               Math.sqrt(Math.max(0, tx[i] - tn[i])) * Ra * 0.408);
    }
    return out;
  }
  /* Groundwater proxy: a linear store fed by gated deep percolation.
     Recharge only happens once the soil profile is already wet, which is how
     the basalt aquifers of the Central Highlands actually refill. */
  function reservoir(p, gp) {
    var k = Math.exp(-1 / C.RES_TAU), S = 0, out = new Array(p.length), i, gate, rech;
    for (i = 0; i < p.length; i++) {
      gate = gp[i] == null ? 0 : Math.max(0, Math.min(1,
        (gp[i] - C.RES_GATE_LO) / (C.RES_GATE_HI - C.RES_GATE_LO)));
      rech = (p[i] == null ? 0 : Math.max(0, p[i] - C.RES_P_MIN)) * gate * C.RES_FRAC;
      S = S * k + rech;
      out[i] = Math.round(S * 10) / 10;
    }
    return out;
  }

  function category(v) {
    if (v == null) return { key: "na", label: "No data" };
    for (var i = 0; i < C.CATS.length; i++) if (v < C.CATS[i].max) return C.CATS[i];
    return C.CATS[C.CATS.length - 1];
  }

  /* ---------------- irrigation signal ---------------- */
  function irrigation(p, pet, gr, ax, i) {
    if (i == null || i < 0) return null;
    // dry-season anchor: 15 Nov of the current or previous year
    var yr = (ax.m[i] > C.DRY_START[0] ||
             (ax.m[i] === C.DRY_START[0] && ax.d[i] >= C.DRY_START[1])) ? ax.y[i] : ax.y[i] - 1,
        anchor = Date.UTC(yr, C.DRY_START[0] - 1, C.DRY_START[1]),
        j0 = Math.max(0, Math.round((anchor - ax.t0) / MS)),
        seasonEnd = Math.round((Date.UTC(yr + 1, 3, 30) - ax.t0) / MS),
        jn = Math.min(i, seasonEnd),
        def = 0, rain = 0, etc = 0, j, dry = 0, lastRain = null;
    for (j = j0; j <= jn; j++) {
      var pp = p[j] == null ? 0 : p[j], ee = (pet[j] == null ? 0 : pet[j]) * C.KC;
      def = Math.max(0, def + ee - pp);
      rain += pp; etc += ee;
    }
    for (j = i; j >= 0 && j > i - 90; j--) {
      if (p[j] != null && p[j] >= 10) { lastRain = i - j; break; }
      dry++;
    }
    var wet = ax.m[i] >= 5 && ax.m[i] <= 10;
    return {
      seasonStart: fmt(anchor),
      seasonEnd: fmt(ax.t0 + jn * MS),
      seasonClosed: jn < i,
      deficit: Math.round(def),
      rain: Math.round(rain),
      etc: Math.round(etc),
      rounds: Math.round(def / C.ROUND_MM * 10) / 10,
      daysSinceRain: lastRain == null ? dry : lastRain,
      gr: gr[i],
      wetSeason: wet,
      urgency: gr[i] == null ? "na"
        : gr[i] < 0.30 ? "critical"
        : gr[i] < C.TRIG_GR ? "due"
        : gr[i] < 0.50 ? "watch" : "ok"
    };
  }

  /* ---------------- monthly roll-up ---------------- */
  function monthlyRollup(st, ax) {
    var by = {}, order = [], i, key;
    for (i = 0; i < ax.ymd.length; i++) {
      key = ax.y[i] + "-" + (ax.m[i] < 10 ? "0" : "") + ax.m[i];
      if (!by[key]) { by[key] = { ym: key, year: ax.y[i], month: ax.m[i], days: 0, rain: 0,
                                  nRain: 0, gr: 0, nGr: 0, gp: 0, nGp: 0, res: 0, nRes: 0,
                                  wai: 0, nWai: 0 }; order.push(key); }
      var b = by[key];
      b.days++;
      if (st.p[i] != null) { b.rain += st.p[i]; b.nRain++; }
      if (st.gr[i] != null) { b.gr += st.gr[i]; b.nGr++; }
      if (st.gp[i] != null) { b.gp += st.gp[i]; b.nGp++; }
      if (st.res[i] != null) { b.res += st.res[i]; b.nRes++; }
      if (st.wai[i] != null) { b.wai += st.wai[i]; b.nWai++; }
    }
    var rows = order.map(function (k) {
      var b = by[k], dim = new Date(Date.UTC(b.year, b.month, 0)).getUTCDate(),
          full = b.days >= dim && b.nRain >= dim * 0.9;
      return {
        ym: k, year: b.year, month: b.month, complete: full, days: b.nRain, dim: dim,
        rain: b.nRain ? Math.round(b.rain * 10) / 10 : null,
        gr: b.nGr ? b.gr / b.nGr : null,
        gp: b.nGp ? b.gp / b.nGp : null,
        res: b.nRes ? b.res / b.nRes : null,
        wai: b.nWai ? Math.round(b.wai / b.nWai * 10) / 10 : null
      };
    });
    // baseline distribution of monthly rainfall totals -> anomaly, % of normal, SPI
    var buckets = [], m;
    for (m = 0; m < 12; m++) buckets.push([]);
    rows.forEach(function (r) {
      if (r.complete && r.rain != null && r.year >= C.BASE_FROM && r.year <= C.BASE_TO)
        buckets[r.month - 1].push(r.rain);
    });
    var qs = [], means = [];
    for (m = 0; m < 12; m++) {
      buckets[m].sort(function (a, b2) { return a - b2; });
      qs.push(quantiles(buckets[m]));
      means.push(buckets[m].length
        ? buckets[m].reduce(function (s, v) { return s + v; }, 0) / buckets[m].length : null);
    }
    rows.forEach(function (r) {
      var nrm = means[r.month - 1];
      r.rainNorm = nrm == null ? null : Math.round(nrm * 10) / 10;
      r.rainAnom = (r.rain == null || nrm == null) ? null : Math.round((r.rain - nrm) * 10) / 10;
      r.rainAnomPct = (r.rain == null || !nrm) ? null : Math.round((r.rain / nrm - 1) * 100);
      r.rainPct = r.rain == null ? null : pctOf(qs[r.month - 1], r.rain);
      r.spi = r.rainPct == null ? null : Math.round(invNorm(r.rainPct / 100) * 100) / 100;
      r.resPct = null; r.grPct = null;
    });
    return { rows: rows, norm: means };
  }

  /* ---------------- station state ---------------- */
  function computeStation(raw, meta) {
    var v = raw.vars, n = v.p.length, ax = dateAxis(raw.start, n);
    var pet = hargreaves(v.t, v.tx, v.tn, meta.lat, ax),
        rain30 = rolling(v.p, 30), rain90 = rolling(v.p, 90),
        res = reservoir(v.p, v.gp);

    var clim = {
      rain30: seasonClim(rain30, ax), rain90: seasonClim(rain90, ax),
      gt: seasonClim(v.gt, ax), gr: seasonClim(v.gr, ax),
      gp: seasonClim(v.gp, ax), res: seasonClim(res, ax)
    };
    var pct = {
      rain30: pctSeries(rain30, clim.rain30, ax), rain90: pctSeries(rain90, clim.rain90, ax),
      gt: pctSeries(v.gt, clim.gt, ax), gr: pctSeries(v.gr, clim.gr, ax),
      gp: pctSeries(v.gp, clim.gp, ax), res: pctSeries(res, clim.res, ax)
    };

    var wai = new Array(n), i, rs, ss, es;
    for (i = 0; i < n; i++) {
      rs = (pct.rain30[i] == null || pct.rain90[i] == null)
        ? (pct.rain90[i] != null ? pct.rain90[i] : pct.rain30[i])
        : 0.5 * pct.rain30[i] + 0.5 * pct.rain90[i];
      ss = pct.gr[i]; es = pct.res[i];
      wai[i] = (rs == null || ss == null || es == null) ? null
        : Math.round((C.W_RAIN * rs + C.W_SOIL * ss + C.W_RES * es) * 10) / 10;
    }

    var st = { p: v.p, gt: v.gt, gr: v.gr, gp: v.gp, t: v.t, pet: pet,
               rain30: rain30, rain90: rain90, res: res, wai: wai };
    var last = n - 1;
    while (last >= 0 && wai[last] == null) last--;
    var mon = monthlyRollup(st, ax);

    // 30-day trend of the reservoir, in percentile points
    var resTrend = null;
    if (last >= 30 && pct.res[last] != null && pct.res[last - 30] != null)
      resTrend = Math.round((pct.res[last] - pct.res[last - 30]) * 10) / 10;

    var i0 = last, now = i0 < 0 ? null : {
      date: ax.ymd[i0], idx: i0,
      wai: wai[i0], cat: category(wai[i0]),
      rain30: rain30[i0] == null ? null : Math.round(rain30[i0]),
      rain30Norm: normalAt(clim.rain30.mean, ax, i0),
      rain30Pct: pct.rain30[i0],
      rain90: rain90[i0] == null ? null : Math.round(rain90[i0]),
      rain90Norm: normalAt(clim.rain90.mean, ax, i0),
      rain90Pct: pct.rain90[i0],
      gt: v.gt[i0], gtPct: pct.gt[i0],
      gr: v.gr[i0], grPct: pct.gr[i0],
      gp: v.gp[i0], gpPct: pct.gp[i0],
      res: res[i0], resPct: pct.res[i0], resTrend: resTrend,
      irrigation: irrigation(v.p, pet, v.gr, ax, i0)
    };
    if (now && now.rain30Norm) now.rain30AnomPct = Math.round((now.rain30 / now.rain30Norm - 1) * 100);
    if (now && now.rain90Norm) now.rain90AnomPct = Math.round((now.rain90 / now.rain90Norm - 1) * 100);

    return { meta: meta, ax: ax, n: n, series: st, pct: pct, clim: clim,
             monthly: mon.rows, monthNorm: mon.norm, now: now };
  }

  /* ---------------- regional aggregate ---------------- */
  function wmean(vals, ws) {
    var s = 0, w = 0;
    for (var i = 0; i < vals.length; i++)
      if (vals[i] != null) { s += vals[i] * ws[i]; w += ws[i]; }
    return w ? s / w : null;
  }
  function aggregate(states, meta) {
    var ws = states.map(function (s) { return s.meta.weight || 1; });
    // align on the shortest common window, anchored on the latest start
    var t0 = Math.max.apply(null, states.map(function (s) { return s.ax.t0; })),
        tEnd = Math.min.apply(null, states.map(function (s) {
          return s.ax.t0 + (s.n - 1) * MS; })),
        n = Math.round((tEnd - t0) / MS) + 1,
        off = states.map(function (s) { return Math.round((t0 - s.ax.t0) / MS); }),
        ax = dateAxis(fmt(t0), n);

    function mix(get) {
      var out = new Array(n), i, k;
      for (i = 0; i < n; i++) {
        var vals = [];
        for (k = 0; k < states.length; k++) vals.push(get(states[k])[i + off[k]]);
        out[i] = wmean(vals, ws);
      }
      return out;
    }
    var series = {
      p: mix(function (s) { return s.series.p; }),
      gt: mix(function (s) { return s.series.gt; }),
      gr: mix(function (s) { return s.series.gr; }),
      gp: mix(function (s) { return s.series.gp; }),
      t: mix(function (s) { return s.series.t; }),
      pet: mix(function (s) { return s.series.pet; }),
      rain30: mix(function (s) { return s.series.rain30; }),
      rain90: mix(function (s) { return s.series.rain90; }),
      res: mix(function (s) { return s.series.res; }),
      wai: mix(function (s) { return s.series.wai; })
    };
    var pct = {};
    ["rain30", "rain90", "gt", "gr", "gp", "res"].forEach(function (k) {
      pct[k] = mix(function (s) { return s.pct[k]; });
    });
    var mon = monthlyRollup(series, ax), last = n - 1;
    while (last >= 0 && series.wai[last] == null) last--;

    /* Regional reference = weighted mean of the station quantile tables, so the
       normal bands and normal lines are available on the aggregate too. */
    var clim = {}, norms = {};
    ["rain30", "rain90", "gt", "gr", "gp", "res"].forEach(function (k) {
      var mean = [], q = [], m, j;
      for (m = 0; m < NODES; m++) {
        mean.push(wmean(states.map(function (s) { return s.clim[k].mean[m]; }), ws));
        var row = [];
        for (j = 0; j <= 20; j++)
          row.push(wmean(states.map(function (s) {
            return s.clim[k].q[m] ? s.clim[k].q[m][j] : null; }), ws));
        q.push(row[0] == null ? null : row);
      }
      clim[k] = { q: q, mean: mean, nodes: NODES };
      norms[k] = mean;
    });
    var resTrend = (last >= 30 && pct.res[last] != null && pct.res[last - 30] != null)
      ? Math.round((pct.res[last] - pct.res[last - 30]) * 10) / 10 : null;

    var i0 = last;
    var now = i0 < 0 ? null : {
      date: ax.ymd[i0], idx: i0,
      wai: Math.round(series.wai[i0] * 10) / 10, cat: category(series.wai[i0]),
      rain30: Math.round(series.rain30[i0]), rain30Norm: normalAt(norms.rain30, ax, i0),
      rain30Pct: pct.rain30[i0],
      rain90: Math.round(series.rain90[i0]), rain90Norm: normalAt(norms.rain90, ax, i0),
      rain90Pct: pct.rain90[i0],
      gt: series.gt[i0], gtPct: pct.gt[i0],
      gr: series.gr[i0], grPct: pct.gr[i0],
      gp: series.gp[i0], gpPct: pct.gp[i0],
      res: series.res[i0], resPct: pct.res[i0], resTrend: resTrend,
      irrigation: irrigation(series.p, series.pet, series.gr, ax, i0)
    };
    if (now) {
      now.rain30AnomPct = now.rain30Norm ? Math.round((now.rain30 / now.rain30Norm - 1) * 100) : null;
      now.rain90AnomPct = now.rain90Norm ? Math.round((now.rain90 / now.rain90Norm - 1) * 100) : null;
    }
    return { meta: meta, ax: ax, n: n, series: series, pct: pct, clim: clim,
             monthly: mon.rows, monthNorm: mon.norm, now: now, isRegion: true };
  }

  /* ---------------- NASA POWER access (live refresh / first-run bootstrap) ---------------- */
  var PARAMS = "PRECTOTCORR,GWETTOP,GWETROOT,GWETPROF,T2M,T2M_MAX,T2M_MIN",
      PKEYS = { p: "PRECTOTCORR", gt: "GWETTOP", gr: "GWETROOT", gp: "GWETPROF",
                t: "T2M", tx: "T2M_MAX", tn: "T2M_MIN" };

  function powerURL(lat, lon, start, end) {
    return "https://power.larc.nasa.gov/api/temporal/daily/point?parameters=" + PARAMS +
      "&community=AG&latitude=" + lat + "&longitude=" + lon +
      "&start=" + start + "&end=" + end + "&format=JSON";
  }
  function fetchPower(lat, lon, start, end) {
    return fetch(powerURL(lat, lon, start, end)).then(function (r) {
      if (!r.ok) throw new Error("NASA POWER HTTP " + r.status);
      return r.json();
    }).then(function (j) {
      var par = j.properties.parameter, days = Object.keys(par.PRECTOTCORR).sort(),
          vars = {}, k;
      for (k in PKEYS) {
        vars[k] = days.map(function (d) {
          var x = par[PKEYS[k]][d];
          return (x == null || x <= -999) ? null : x;
        });
      }
      return { start: days[0], end: days[days.length - 1], n: days.length, vars: vars };
    });
  }
  /* Splice a freshly fetched tail onto a stored series (overlap wins from the tail). */
  function mergeTail(base, tail) {
    var b0 = ymdToUTC(base.start), t0 = ymdToUTC(tail.start),
        off = Math.round((t0 - b0) / MS), k, i, n = base.vars.p.length;
    if (off < 0 || off > n) return tail;             // disjoint: keep the newer block
    var total = Math.max(n, off + tail.vars.p.length), vars = {};
    for (k in base.vars) {
      var col = base.vars[k].slice();
      while (col.length < total) col.push(null);
      for (i = 0; i < tail.vars[k].length; i++)
        if (tail.vars[k][i] != null) col[off + i] = tail.vars[k][i];
      vars[k] = col;
    }
    return { start: base.start, end: tail.end, n: total, vars: vars };
  }
  function todayMinus(days) {
    return fmt(Date.now() - days * MS);
  }

  window.WAI = {
    C: C, category: category, fmt: fmt, dateAxis: dateAxis, rolling: rolling,
    computeStation: computeStation, aggregate: aggregate,
    normalSeries: normalSeries, climQAt: climQAt,
    fetchPower: fetchPower, mergeTail: mergeTail, todayMinus: todayMinus,
    pctOf: pctOf, invNorm: invNorm
  };
})();
