// Time-series SVG chart for the volumes page (same white-card look as chart.js).
// window.renderTimeChart({ title, subtitle, yLabel, labels[], series[], unit })
//   series item: { label, color, kind: 'line' | 'bar', values[], dots[] (optional bool per point) }
// Hover highlighting reuses the g.sline / data-label mechanism from assets/chart.js.
(function () {
  const W = 720, H = 478, mL = 68, mR = 20, mT = 56, mB = 104;
  const x0 = mL, x1 = W - mR, y0 = mT, y1 = H - mB;
  const esc = s => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
  const fmt = v => Math.round(v).toLocaleString("en-US");

  function niceStep(span, target) {
    const raw = span / target, p = Math.pow(10, Math.floor(Math.log10(raw || 1)));
    for (const m of [1, 2, 2.5, 5, 10]) if (m * p >= raw) return m * p;
    return 10 * p;
  }

  window.renderTimeChart = function (spec) {
    const n = spec.labels.length;
    let lo = 0, hi = 0;
    spec.series.forEach(s => s.values.forEach(v => { if (v != null) { lo = Math.min(lo, v); hi = Math.max(hi, v); } }));
    if (hi === lo) hi = lo + 1;
    const step = niceStep(hi - lo, 6);
    const yMin = Math.floor(lo / step) * step, yMax = Math.ceil(hi / step) * step || step;
    const yAt = v => y1 - (v - yMin) / (yMax - yMin) * (y1 - y0);
    const slot = (x1 - x0) / Math.max(n, 1);
    const cx = i => x0 + (i + 0.5) * slot;

    let g = `<rect x="0" y="0" width="${W}" height="${H}" fill="#ffffff"/>`;
    for (let v = yMin; v <= yMax + 1e-9; v += step) {
      const y = yAt(v);
      g += `<line x1="${x0}" y1="${y.toFixed(1)}" x2="${x1}" y2="${y.toFixed(1)}" stroke="#d9d9d9"/>`;
      g += `<text x="${x0 - 7}" y="${(y + 3.6).toFixed(1)}" font-size="11" fill="#333" text-anchor="end">${fmt(v)}</text>`;
    }
    const every = Math.max(1, Math.ceil(n / 12));
    for (let i = 0; i < n; i += every) {
      const x = cx(i);
      g += `<line x1="${x.toFixed(1)}" y1="${y0}" x2="${x.toFixed(1)}" y2="${y1}" stroke="#ececec"/>`;
      g += `<text x="${x.toFixed(1)}" y="${y1 + 16}" font-size="10.5" fill="#333" text-anchor="middle">${esc(spec.labels[i])}</text>`;
    }
    g += `<rect x="${x0}" y="${y0}" width="${(x1 - x0).toFixed(1)}" height="${(y1 - y0).toFixed(1)}" fill="none" stroke="#8a8a8a"/>`;
    if (yMin < 0) g += `<line x1="${x0}" y1="${yAt(0).toFixed(1)}" x2="${x1}" y2="${yAt(0).toFixed(1)}" stroke="#555"/>`;

    const bars = spec.series.filter(s => s.kind === "bar");
    const bw = slot * 0.78 / Math.max(bars.length, 1);
    bars.forEach((s, si) => {
      let b = "";
      s.values.forEach((v, i) => {
        if (v == null) return;
        const gx = x0 + i * slot + slot * 0.11 + si * bw, yv = yAt(v), yz = yAt(Math.max(0, yMin));
        b += `<rect x="${gx.toFixed(1)}" y="${Math.min(yz, yv).toFixed(1)}" width="${(bw * 0.9).toFixed(1)}" height="${Math.max(0.5, Math.abs(yv - yz)).toFixed(1)}" fill="${s.color}"><title>${esc(spec.labels[i])} — ${esc(s.label)}: ${fmt(v)}</title></rect>`;
      });
      if (b) g += `<g class="sline" data-label="${esc(s.label)}">${b}</g>`;
    });

    spec.series.filter(s => s.kind !== "bar").forEach(s => {
      let d = "", dots = "";
      s.values.forEach((v, i) => {
        if (v == null) { d += ""; return; }
        const px = cx(i), py = yAt(v);
        d += (d && s.values[i - 1] != null ? "L" : "M") + px.toFixed(1) + " " + py.toFixed(1) + " ";
        if (s.dots && s.dots[i])
          dots += `<circle cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="3.6" fill="#fff" stroke="${s.color}" stroke-width="2"><title>${esc(spec.labels[i])}: ${fmt(v)} (measured)</title></circle>`;
        else
          dots += `<circle cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="5" fill="#000" fill-opacity="0"><title>${esc(spec.labels[i])} — ${esc(s.label)}: ${fmt(v)}</title></circle>`;
      });
      if (d) g += `<g class="sline" data-label="${esc(s.label)}">` +
        `<path class="vis" d="${d}" fill="none" stroke="${s.color}" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"/>` +
        `<path class="hit" d="${d}" fill="none" stroke="#000" stroke-opacity="0" stroke-width="11"><title>${esc(s.label)}</title></path>${dots}</g>`;
    });

    g += `<text x="${W / 2}" y="22" font-size="15" font-weight="700" fill="#1a1a1a" text-anchor="middle">${esc(spec.title)}</text>`;
    if (spec.subtitle) g += `<text x="${W / 2}" y="40" font-size="12.5" fill="#1a1a1a" text-anchor="middle">${esc(spec.subtitle)}</text>`;
    if (spec.yLabel) g += `<text x="15" y="${(y0 + y1) / 2}" font-size="12" fill="#333" text-anchor="middle" transform="rotate(-90 15 ${(y0 + y1) / 2})">${esc(spec.yLabel)}</text>`;
    let lx = x0, ly = H - 42;
    spec.series.forEach(s => {
      const w = 30 + esc(s.label).length * 6.1 + 22;
      if (lx + w > x1 && lx > x0) { lx = x0; ly += 18; }
      const mark = s.kind === "bar"
        ? `<rect x="${lx}" y="${ly - 6}" width="16" height="11" fill="${s.color}"/>`
        : `<line x1="${lx}" y1="${ly}" x2="${lx + 22}" y2="${ly}" stroke="${s.color}" stroke-width="3"/>`;
      g += `<g class="sline legend" data-label="${esc(s.label)}"><rect x="${lx - 2}" y="${ly - 9}" width="${(w - 18).toFixed(0)}" height="18" fill="#fff" fill-opacity="0"/>${mark}<text x="${lx + 28}" y="${ly + 4}" font-size="11.5" fill="#222">${esc(s.label)}</text></g>`;
      lx += w;
    });
    g += `<text class="hover-label" x="${x1 - 4}" y="${y0 + 16}" text-anchor="end" font-size="14" font-weight="700" fill="#111"></text>`;
    return `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" class="chart-svg" role="img" aria-label="${esc(spec.title)}">${g}</svg>`;
  };
})();
