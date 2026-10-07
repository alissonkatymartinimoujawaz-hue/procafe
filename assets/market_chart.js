// SVG charts for the market page (daily time series, season bars, scatter).
// Same look as assets/chart.js: white card, dark text, hover read-out.
//
//   MarketCharts.time(host, spec)     daily dates, left/right axes, line / area / step
//   MarketCharts.combo(host, spec)    season bars (left) + lines (right) — "stocks / consumption & price"
//   MarketCharts.scatter(host, spec)  x/y points coloured by year (+ optional bucket line)
(function () {
  const esc = s => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
  const ok = v => v !== null && v !== undefined && !Number.isNaN(v);

  function nice(min, max, n) {
    if (!(max > min)) { max = min + 1; }
    const raw = (max - min) / (n || 6), p = Math.pow(10, Math.floor(Math.log10(raw)));
    const step = [1, 2, 2.5, 5, 10].map(m => m * p).find(s => s >= raw);
    return { min: Math.floor(min / step) * step, max: Math.ceil(max / step) * step, step };
  }
  function axisFor(cfg, values) {
    const v = values.filter(ok);
    if (cfg.min !== undefined && cfg.max !== undefined) return { ...cfg, step: cfg.step || nice(cfg.min, cfg.max).step };
    const lo = cfg.min !== undefined ? cfg.min : Math.min(...v), hi = cfg.max !== undefined ? cfg.max : Math.max(...v);
    return { ...cfg, ...nice(lo, hi, cfg.ticks) };
  }
  const fmtN = (v, d) => v.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });

  function frame(W, H, m, spec, L, R, xticks) {
    const x0 = m.l, x1 = W - m.r, y0 = m.t, y1 = H - m.b;
    let g = `<rect width="${W}" height="${H}" fill="#fff"/>`;
    const yL = v => y1 - (v - L.min) / (L.max - L.min) * (y1 - y0);
    for (let v = L.min; v <= L.max + 1e-9; v += L.step) {
      g += `<line x1="${x0}" x2="${x1}" y1="${yL(v).toFixed(1)}" y2="${yL(v).toFixed(1)}" stroke="#e3e3e3"/>`;
      g += `<text x="${x0 - 7}" y="${(yL(v) + 4).toFixed(1)}" font-size="11.5" fill="#333" text-anchor="end">${L.fmt ? L.fmt(v) : fmtN(v, L.dec || 0)}</text>`;
    }
    if (R) {
      const yR = v => y1 - (v - R.min) / (R.max - R.min) * (y1 - y0);
      for (let v = R.min; v <= R.max + 1e-9; v += R.step)
        g += `<text x="${x1 + 7}" y="${(yR(v) + 4).toFixed(1)}" font-size="11.5" fill="#333">${R.fmt ? R.fmt(v) : fmtN(v, R.dec || 0)}</text>`;
      if (R.zero && R.min < 0 && R.max > 0)
        g += `<line x1="${x0}" x2="${x1}" y1="${yR(0).toFixed(1)}" y2="${yR(0).toFixed(1)}" stroke="${R.zeroColor || "#999"}" stroke-dasharray="4 3"/>`;
      if (R.label) g += `<text x="${W - 14}" y="${(y0 + y1) / 2}" font-size="12" fill="#333" text-anchor="middle" transform="rotate(90 ${W - 14} ${(y0 + y1) / 2})">${esc(R.label)}</text>`;
    }
    if (L.zero !== false && L.min < 0 && L.max > 0)
      g += `<line x1="${x0}" x2="${x1}" y1="${yL(0).toFixed(1)}" y2="${yL(0).toFixed(1)}" stroke="#777"/>`;
    if (L.label) g += `<text x="16" y="${(y0 + y1) / 2}" font-size="12" fill="#333" text-anchor="middle" transform="rotate(-90 16 ${(y0 + y1) / 2})">${esc(L.label)}</text>`;
    xticks.forEach(t => {
      g += `<line x1="${t.x.toFixed(1)}" x2="${t.x.toFixed(1)}" y1="${y1}" y2="${y1 + 5}" stroke="#888"/>`;
      g += `<text x="${(t.lx ?? t.x).toFixed(1)}" y="${y1 + 19}" font-size="11.5" fill="#333" text-anchor="middle">${esc(t.label)}</text>`;
    });
    g += `<line x1="${x0}" x2="${x1}" y1="${y1}" y2="${y1}" stroke="#888"/>`;
    g += `<text x="${W / 2}" y="22" font-size="15" font-weight="700" fill="#1a1a1a" text-anchor="middle">${esc(spec.title || "")}</text>`;
    if (spec.subtitle) g += `<text x="${W / 2}" y="40" font-size="12" fill="#555" text-anchor="middle">${esc(spec.subtitle)}</text>`;
    return g;
  }

  function legend(items, W, y) {
    // centred row(s) of legend entries
    const widths = items.map(it => 34 + esc(it.label).length * 6.3 + 18);
    let rows = [[]], rw = [0];
    items.forEach((it, i) => {
      if (rw[rw.length - 1] + widths[i] > W - 80) { rows.push([]); rw.push(0); }
      rows[rows.length - 1].push(i); rw[rw.length - 1] += widths[i];
    });
    let g = "";
    rows.forEach((r, ri) => {
      let x = (W - rw[ri]) / 2; const yy = y + ri * 18;
      r.forEach(i => {
        const it = items[i];
        g += it.box
          ? `<rect x="${x}" y="${yy - 6}" width="22" height="11" fill="${it.color}" opacity="${it.opacity || 1}"/>`
          : `<line x1="${x}" x2="${x + 24}" y1="${yy}" y2="${yy}" stroke="${it.color}" stroke-width="3" ${it.dash ? `stroke-dasharray="${it.dash}"` : ""}/>`;
        g += `<text x="${x + 30}" y="${yy + 4}" font-size="11.5" fill="#222">${esc(it.label)}</text>`;
        x += widths[i];
      });
    });
    return g;
  }

  function tooltipBox(svg, W) {
    const ns = "http://www.w3.org/2000/svg";
    const g = document.createElementNS(ns, "g"); g.setAttribute("pointer-events", "none"); g.style.display = "none";
    const line = document.createElementNS(ns, "line"); line.setAttribute("stroke", "#444"); line.setAttribute("stroke-dasharray", "3 3");
    const box = document.createElementNS(ns, "rect"); box.setAttribute("fill", "#fff"); box.setAttribute("stroke", "#999"); box.setAttribute("rx", "5"); box.setAttribute("opacity", ".95");
    const txt = document.createElementNS(ns, "text"); txt.setAttribute("font-size", "12"); txt.setAttribute("fill", "#111");
    g.append(line, box, txt); svg.appendChild(g);
    return {
      show(x, yTop, yBot, rows) {
        g.style.display = "";
        line.setAttribute("x1", x); line.setAttribute("x2", x); line.setAttribute("y1", yTop); line.setAttribute("y2", yBot);
        txt.innerHTML = rows.map((r, i) => `<tspan x="0" dy="${i ? 16 : 0}" ${i ? "" : 'font-weight="700"'}>${r.color ? `<tspan fill="${r.color}">■ </tspan>` : ""}${esc(r.text)}</tspan>`).join("");
        const w = Math.max(...rows.map(r => r.text.length)) * 6.7 + 30, h = rows.length * 16 + 10;
        const bx = x + 12 + w > W - 10 ? x - 12 - w : x + 12;
        box.setAttribute("x", bx); box.setAttribute("y", yTop + 6); box.setAttribute("width", w); box.setAttribute("height", h);
        txt.setAttribute("transform", `translate(${bx + 8},${yTop + 21})`);
        txt.querySelectorAll(":scope > tspan").forEach(t => t.setAttribute("x", "0"));
      },
      hide() { g.style.display = "none"; }
    };
  }

  function mount(host, W, H, inner, label) {
    host.innerHTML = `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" class="chart-svg" role="img" aria-label="${esc(label || "")}">${inner}</svg>`;
    return host.querySelector("svg");
  }
  function svgX(svg, ev, W) {
    const r = svg.getBoundingClientRect();
    return (ev.clientX - r.left) / r.width * W;
  }

  // ------------------------------------------------------------ time series
  // spec: {title, subtitle, dates:[iso], series:[{label, values, color, axis:'left'|'right',
  //        type:'line'|'area', width, dash, fmt}], left:{label,min,max,dec,fmt}, right:{...},
  //        from:'2008-01-01', to:'2026-12-31', events:[{date,label}]}
  function time(host, spec) {
    const W = spec.width || 1100, H = spec.height || 460, m = { l: 66, r: spec.right ? 66 : 24, t: 64, b: 84 };
    const x0 = m.l, x1 = W - m.r, y0 = m.t, y1 = H - m.b;
    const t = spec.dates.map(d => Date.parse(d));
    const from = spec.from ? Date.parse(spec.from) : t[0], to = spec.to ? Date.parse(spec.to) : t[t.length - 1];
    const idx = t.map((v, i) => i).filter(i => t[i] >= from && t[i] <= to);
    if (!idx.length) { host.innerHTML = `<div class="placeholder">No daily data in market_inputs/daily.csv yet.</div>`; return; }
    const vals = side => spec.series.filter(s => (s.axis || "left") === side).flatMap(s => idx.map(i => s.values[i]));
    const L = axisFor(spec.left || {}, vals("left").concat(spec.series.some(s => s.type === "area" && (s.axis || "left") === "left") ? [0] : []));
    const R = spec.right ? axisFor(spec.right, vals("right")) : null;
    const X = v => x0 + (v - from) / (to - from) * (x1 - x0);
    const Y = (v, ax) => { const a = ax === "right" ? R : L; return y1 - (Math.max(a.min, Math.min(a.max, v)) - a.min) / (a.max - a.min) * (y1 - y0); };

    const y0yr = new Date(from).getUTCFullYear(), yEnd = new Date(to).getUTCFullYear();
    const every = Math.max(1, Math.ceil((yEnd - y0yr + 1) / 20));
    const xticks = [];
    for (let y = y0yr; y <= yEnd + 1; y++) {
      const tt = Date.UTC(y, 0, 1);
      if (tt < from || tt > to || (y - y0yr) % every) continue;
      xticks.push({ x: X(tt), label: String(y) });
    }
    let g = frame(W, H, m, spec, L, R, xticks);
    (spec.bands || []).forEach(b => {
      const a = X(Math.max(from, Date.parse(b.from))), z = X(Math.min(to, Date.parse(b.to)));
      if (z > a) g += `<rect x="${a.toFixed(1)}" y="${y0}" width="${(z - a).toFixed(1)}" height="${y1 - y0}" fill="${b.color || "#f3ece4"}"/>`;
    });
    spec.series.forEach(s => {
      const ax = s.axis || "left";
      let d = "", pen = false, first = null, last = null;
      idx.forEach(i => {
        const v = s.values[i];
        if (!ok(v)) { pen = false; return; }
        const px = X(t[i]).toFixed(1), py = Y(v, ax).toFixed(1);
        d += (pen ? "L" : "M") + px + " " + py; pen = true;
        if (first === null) first = px; last = px;
      });
      if (!d) return;
      if (s.type === "area") {
        const base = Y(Math.max((ax === "right" ? R : L).min, 0), ax).toFixed(1);
        g += `<path d="${d.replace(/M/g, "L").replace(/^L/, "M")} L${last} ${base} L${first} ${base}Z" fill="${s.color}" opacity="${s.opacity || 0.85}"/>`;
      } else {
        g += `<path d="${d}" fill="none" stroke="${s.color}" stroke-width="${s.width || 1.6}" stroke-linejoin="round" ${s.dash ? `stroke-dasharray="${s.dash}"` : ""}/>`;
      }
    });
    // band labels on top of the series (white halo keeps them legible)
    (spec.bands || []).forEach(b => {
      const a = X(Math.max(from, Date.parse(b.from))), z = X(Math.min(to, Date.parse(b.to)));
      if (z - a > 120 && b.label) g += `<text x="${((a + z) / 2).toFixed(1)}" y="${y0 + 14}" font-size="11" fill="#8a6d52" text-anchor="middle" stroke="#fff" stroke-width="3" paint-order="stroke">${esc(b.label)}</text>`;
    });
    // event markers; labels alternate between two rows so close events don't collide
    let lastX = -1e9, row = 0;
    (spec.events || []).forEach(e => {
      const tt = Date.parse(e.date); if (tt < from || tt > to) return;
      const xv = X(tt), x = xv.toFixed(1);
      row = xv - lastX < 80 ? 1 - row : 0; lastX = xv;
      g += `<line x1="${x}" x2="${x}" y1="${y0}" y2="${y1}" stroke="#b05" stroke-dasharray="2 3" opacity=".7"/>` +
        `<text x="${x}" y="${y0 - 4 - row * 12}" font-size="10.5" fill="#b05" text-anchor="middle">${esc(e.label)}</text>`;
    });
    g += legend(spec.series.map(s => ({ label: s.label + (spec.right ? (s.axis === "right" ? " (rhs)" : " (lhs)") : ""), color: s.color, box: s.type === "area", dash: s.dash, opacity: s.opacity })), W, H - 38);
    g += `<rect class="hit" x="${x0}" y="${y0}" width="${x1 - x0}" height="${y1 - y0}" fill="#000" fill-opacity="0"/>`;
    const svg = mount(host, W, H, g, spec.title);
    const tip = tooltipBox(svg, W);
    svg.addEventListener("mousemove", ev => {
      const xv = from + (svgX(svg, ev, W) - x0) / (x1 - x0) * (to - from);
      let lo = 0, hi = idx.length - 1;
      while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (t[idx[mid]] < xv) lo = mid; else hi = mid; }
      const i = idx[Math.abs(t[idx[lo]] - xv) < Math.abs(t[idx[hi]] - xv) ? lo : hi];
      tip.show(X(t[i]), y0, y1, [{ text: spec.dates[i] }].concat(spec.series.map(s => ({
        color: s.color, text: `${s.label}: ${ok(s.values[i]) ? (s.fmt ? s.fmt(s.values[i]) : fmtN(s.values[i], 2)) : "–"}` }))));
    });
    svg.addEventListener("mouseleave", () => tip.hide());
  }

  // ------------------------------------------------------------ season bars + lines
  // spec: {title, cats:[season], bars:[{label,values,color,fmtLabel, forecast:[bool]}],
  //        lines:[{label,values,color,dash}], left:{}, right:{}}
  function combo(host, spec) {
    const W = spec.width || 1100, H = spec.height || 460, m = { l: 66, r: 66, t: 52, b: 96 };
    const x0 = m.l, x1 = W - m.r, y0 = m.t, y1 = H - m.b, n = spec.cats.length;
    const L = axisFor({ min: 0, ...(spec.left || {}) }, spec.bars.flatMap(b => b.values));
    const lv = spec.lines.flatMap(l => l.values).filter(ok);
    const R = axisFor({ min: 0, ...(spec.right || {}) }, lv.length ? lv : [0, 1]);
    const slot = (x1 - x0) / n, Xc = i => x0 + (i + 0.5) * slot;
    const YL = v => y1 - (v - L.min) / (L.max - L.min) * (y1 - y0), YR = v => y1 - (v - R.min) / (R.max - R.min) * (y1 - y0);
    const xt = spec.cats.map((c, i) => ({ x: Xc(i), label: c + (spec.bars[0].forecast?.[i] ? "*" : "") }));
    let g = frame(W, H, m, spec, L, R, xt);
    const bw = slot * 0.62 / spec.bars.length;
    spec.bars.forEach((b, bi) => b.values.forEach((v, i) => {
      if (!ok(v)) return;
      const x = Xc(i) - slot * 0.31 + bi * bw, y = YL(v);
      g += `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${(bw * 0.94).toFixed(1)}" height="${(YL(L.min) - y).toFixed(1)}" fill="${b.color}" opacity="${b.forecast?.[i] ? 0.55 : 1}"/>`;
      if (b.fmtLabel) g += `<text x="${(x + bw * 0.47).toFixed(1)}" y="${(y - 5).toFixed(1)}" font-size="10.5" fill="#333" text-anchor="middle">${b.fmtLabel(v)}</text>`;
    }));
    spec.lines.forEach(l => {
      let d = "", pen = false;
      l.values.forEach((v, i) => { if (!ok(v)) { pen = false; return; } d += (pen ? "L" : "M") + Xc(i).toFixed(1) + " " + YR(v).toFixed(1); pen = true; });
      if (d) g += `<path d="${d}" fill="none" stroke="${l.color}" stroke-width="2.4" ${l.dash ? `stroke-dasharray="${l.dash}"` : ""}/>`;
      l.values.forEach((v, i) => { if (ok(v)) g += `<circle cx="${Xc(i).toFixed(1)}" cy="${YR(v).toFixed(1)}" r="2.6" fill="${l.color}"/>`; });
    });
    g += legend(spec.bars.map(b => ({ label: b.label + " (lhs)", color: b.color, box: true }))
      .concat(spec.lines.map(l => ({ label: l.label + " (rhs)", color: l.color, dash: l.dash }))), W, H - 38);
    g += `<rect class="hit" x="${x0}" y="${y0}" width="${x1 - x0}" height="${y1 - y0}" fill="#000" fill-opacity="0"/>`;
    const svg = mount(host, W, H, g, spec.title), tip = tooltipBox(svg, W);
    svg.addEventListener("mousemove", ev => {
      const i = Math.max(0, Math.min(n - 1, Math.floor((svgX(svg, ev, W) - x0) / slot)));
      tip.show(Xc(i), y0, y1, [{ text: spec.cats[i] + (spec.bars[0].forecast?.[i] ? " (forecast)" : "") }]
        .concat(spec.bars.map(b => ({ color: b.color, text: `${b.label}: ${ok(b.values[i]) ? (b.fmt || (v => fmtN(v, 2)))(b.values[i]) : "–"}` })))
        .concat(spec.lines.map(l => ({ color: l.color, text: `${l.label}: ${ok(l.values[i]) ? fmtN(l.values[i], 1) : "–"}` }))));
    });
    svg.addEventListener("mouseleave", () => tip.hide());
  }

  // ------------------------------------------------------------ scatter
  // spec: {title, points:[{x,y,year,label}], x:{label}, y:{label}, curve:[{x,y}], curveLabel}
  function scatter(host, spec) {
    const W = spec.width || 540, H = spec.height || 440, m = { l: 62, r: 20, t: 52, b: 82 };
    const x0 = m.l, x1 = W - m.r, y0 = m.t, y1 = H - m.b;
    const pts = spec.points.filter(p => ok(p.x) && ok(p.y));
    if (!pts.length) { host.innerHTML = `<div class="placeholder">${esc(spec.empty || "Not enough data yet.")}</div>`; return; }
    const XA = axisFor(spec.x || {}, pts.map(p => p.x)), YA = axisFor(spec.y || {}, pts.map(p => p.y));
    const X = v => x0 + (v - XA.min) / (XA.max - XA.min) * (x1 - x0), Y = v => y1 - (v - YA.min) / (YA.max - YA.min) * (y1 - y0);
    const xt = []; for (let v = XA.min; v <= XA.max + 1e-9; v += XA.step) xt.push({ x: X(v), label: XA.fmt ? XA.fmt(v) : fmtN(v, XA.dec || 0) });
    let g = frame(W, H, m, spec, YA, null, xt);
    g += `<text x="${(x0 + x1) / 2}" y="${H - 44}" font-size="12" fill="#333" text-anchor="middle">${esc(XA.label || "")}</text>`;
    const yrs = pts.map(p => p.year), ymin = Math.min(...yrs), ymax = Math.max(...yrs);
    const col = yr => { const k = ymax > ymin ? (yr - ymin) / (ymax - ymin) : 1; return `hsl(${210 - 190 * k},70%,${45 - 5 * k}%)`; };
    pts.forEach(p => g += `<circle cx="${X(p.x).toFixed(1)}" cy="${Y(p.y).toFixed(1)}" r="${p.r || 2.2}" fill="${col(p.year)}" opacity="${p.r ? 0.95 : 0.45}">${p.label ? `<title>${esc(p.label)}</title>` : ""}</circle>`);
    pts.filter(p => p.tag).forEach(p => g += `<text x="${(X(p.x) + 7).toFixed(1)}" y="${(Y(p.y) + 4).toFixed(1)}" font-size="10.5" fill="#333">${esc(p.tag)}</text>`);
    if (spec.curve && spec.curve.length) {
      const d = spec.curve.map((c, i) => (i ? "L" : "M") + X(c.x).toFixed(1) + " " + Y(c.y).toFixed(1)).join("");
      g += `<path d="${d}" fill="none" stroke="#111" stroke-width="2.4"/>`;
      spec.curve.forEach(c => g += `<circle cx="${X(c.x).toFixed(1)}" cy="${Y(c.y).toFixed(1)}" r="3.5" fill="#111"/>`);
    }
    // year colour key
    const kx = x0, ky = H - 22, kw = 160;
    for (let i = 0; i < 20; i++) g += `<rect x="${kx + i * kw / 20}" y="${ky - 6}" width="${kw / 20 + 0.5}" height="9" fill="${col(ymin + (ymax - ymin) * i / 19)}"/>`;
    g += `<text x="${kx - 4}" y="${ky + 2}" font-size="10.5" text-anchor="end" fill="#333">${ymin}</text><text x="${kx + kw + 4}" y="${ky + 2}" font-size="10.5" fill="#333">${ymax}</text>`;
    if (spec.curveLabel) g += `<line x1="${kx + kw + 50}" x2="${kx + kw + 74}" y1="${ky - 2}" y2="${ky - 2}" stroke="#111" stroke-width="2.4"/><text x="${kx + kw + 80}" y="${ky + 2}" font-size="11" fill="#222">${esc(spec.curveLabel)}</text>`;
    mount(host, W, H, g, spec.title);
  }

  window.MarketCharts = { time, combo, scatter };
})();
