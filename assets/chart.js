// SVG chart renderer — reproduces the monthly report style.
// Charts render on a WHITE card with dark text (identical in light/dark mode).
//
// window.renderLineChart(spec) and window.renderBarChart(spec)
// Shared: title, subtitle, yLabel, yMin, yMax, yStep, yDecimals(=0), xLabels(12 months)
(function () {
  const W = 720, H = 478, mL = 60, mR = 20, mT = 56, mB = 104;
  const x0 = mL, x1 = W - mR, y0 = mT, y1 = H - mB;
  const DIM = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  const CUM = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]; // day-of-year at each month start
  const YR = 365;
  const esc = s => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");

  function frameAndAxes(spec, xticks) {
    const yAt = v => y1 - (v - spec.yMin) / (spec.yMax - spec.yMin) * (y1 - y0);
    const dec = spec.yDecimals || 0;
    let g = `<rect x="0" y="0" width="${W}" height="${H}" fill="#ffffff"/>`;
    for (let v = spec.yMin; v <= spec.yMax + 1e-9; v += spec.yStep) {
      const y = yAt(v);
      g += `<line x1="${x0}" y1="${y.toFixed(1)}" x2="${x1}" y2="${y.toFixed(1)}" stroke="#d9d9d9"/>`;
      g += `<text x="${x0 - 7}" y="${(y + 3.6).toFixed(1)}" font-size="11" fill="#333" text-anchor="end">${v.toFixed(dec)}</text>`;
    }
    xticks.forEach(t => {
      const x = x0 + t.x * (x1 - x0);
      if (t.grid !== false)
        g += `<line x1="${x.toFixed(1)}" y1="${y0}" x2="${x.toFixed(1)}" y2="${y1}" stroke="#ececec"/>`;
      g += `<text x="${(x0 + t.lx * (x1 - x0)).toFixed(1)}" y="${y1 + 16}" font-size="11" fill="#333" text-anchor="middle">${esc(t.label)}</text>`;
    });
    g += `<rect x="${x0}" y="${y0}" width="${(x1 - x0).toFixed(1)}" height="${(y1 - y0).toFixed(1)}" fill="none" stroke="#8a8a8a"/>`;
    if (spec.yMin < 0 && spec.yMax > 0)
      g += `<line x1="${x0}" y1="${yAt(0).toFixed(1)}" x2="${x1}" y2="${yAt(0).toFixed(1)}" stroke="#555"/>`;
    return g;
  }

  function titlesAndLegend(spec, legendItems) {
    let g = `<text x="${W / 2}" y="22" font-size="15" font-weight="700" fill="#1a1a1a" text-anchor="middle">${esc(spec.title)}</text>`;
    if (spec.subtitle)
      g += `<text x="${W / 2}" y="40" font-size="12.5" font-weight="700" fill="#1a1a1a" text-anchor="middle">${esc(spec.subtitle)}</text>`;
    if (spec.yLabel)
      g += `<text x="15" y="${(y0 + y1) / 2}" font-size="12" fill="#333" text-anchor="middle" transform="rotate(-90 15 ${(y0 + y1) / 2})">${esc(spec.yLabel)}</text>`;
    let lx = x0, ly = H - 42;
    legendItems.forEach(it => {
      const w = 22 + 8 + esc(it.label).length * 6.1 + 22;
      if (lx + w > x1 && lx > x0) { lx = x0; ly += 18; }
      if (it.box && it.hover) {
        g += `<g class="sline legend" data-label="${esc(it.label)}">` +
          `<rect x="${lx - 2}" y="${ly - 9}" width="${(w - 18).toFixed(0)}" height="18" fill="#fff" fill-opacity="0"/>` +
          `<rect x="${lx}" y="${ly - 6}" width="16" height="11" fill="${it.color}"/>` +
          `<text x="${lx + 20}" y="${ly + 4}" font-size="11.5" fill="#222">${esc(it.label)}</text></g>`;
      } else if (it.box) {
        g += `<rect x="${lx}" y="${ly - 6}" width="16" height="11" fill="${it.color}"/>`;
        g += `<text x="${lx + 20}" y="${ly + 4}" font-size="11.5" fill="#222">${esc(it.label)}</text>`;
      } else {
        // legend entry participates in hover-highlighting (same data-label as its line)
        g += `<g class="sline legend" data-label="${esc(it.label)}">` +
          `<rect x="${lx - 2}" y="${ly - 9}" width="${(w - 18).toFixed(0)}" height="18" fill="#fff" fill-opacity="0"/>` +
          `<line x1="${lx}" y1="${ly}" x2="${lx + 22}" y2="${ly}" stroke="${it.color}" stroke-width="3"/>` +
          `<text x="${lx + 30}" y="${ly + 4}" font-size="11.5" fill="#222">${esc(it.label)}</text></g>`;
      }
      lx += w;
    });
    return g;
  }

  function svg(inner, label) {
    return `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" class="chart-svg" role="img" aria-label="${esc(label)}">${inner}</svg>`;
  }

  // ---- Line chart. spec.mode: 'monthly' (12 pts, x=i/11) or 'daily' (x=i/365) ----
  // Each series is wrapped in <g class="sline" data-label> with an invisible wide
  // "hit" path so hovering highlights the line and shows its label (see listeners below).
  window.renderLineChart = function (spec) {
    const daily = spec.mode === "daily";
    const xOf = i => daily ? i / YR : i / 11;
    const yAt = v => y1 - (v - spec.yMin) / (spec.yMax - spec.yMin) * (y1 - y0);
    const xticks = spec.xLabels.map((lab, m) => daily
      ? { x: CUM[m] / YR, lx: (CUM[m] + DIM[m] / 2) / YR, label: lab }
      : { x: m / 11, lx: m / 11, label: lab });
    let g = frameAndAxes(spec, xticks);
    spec.series.forEach(s => {
      let d = "";
      s.values.forEach((v, i) => {
        if (v === null || v === undefined) return;
        const cv = Math.max(spec.yMin, Math.min(spec.yMax, v)); // never draw outside the frame
        const px = x0 + xOf(i) * (x1 - x0), py = yAt(cv);
        d += (d ? "L" : "M") + px.toFixed(1) + " " + py.toFixed(1) + " ";
      });
      if (d) g += `<g class="sline" data-label="${esc(s.label)}">` +
        `<path class="vis" d="${d}" fill="none" stroke="${s.color}" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"/>` +
        `<path class="hit" d="${d}" fill="none" stroke="#000" stroke-opacity="0" stroke-width="11"><title>${esc(s.label)}</title></path>` +
        `</g>`;
    });
    g += titlesAndLegend(spec, spec.series.map(s => ({ color: s.color, label: s.label })));
    g += `<text class="hover-label" x="${x1 - 4}" y="${y0 + 16}" text-anchor="end" font-size="14" font-weight="700" fill="#111"></text>`;
    return svg(g, spec.title);
  };

  // ---- Hover interactivity (delegated once for all charts on the page) ----
  document.addEventListener("mouseover", e => {
    const gEl = e.target.closest && e.target.closest("g.sline");
    if (!gEl) return;
    const svgEl = gEl.closest("svg");
    const label = gEl.getAttribute("data-label");
    svgEl.classList.add("hovering");
    svgEl.querySelectorAll("g.sline").forEach(x =>
      x.classList.toggle("hover", x.getAttribute("data-label") === label));
    const hl = svgEl.querySelector(".hover-label");
    if (hl) hl.textContent = label;
  });
  document.addEventListener("mouseout", e => {
    const gEl = e.target.closest && e.target.closest("g.sline");
    if (!gEl) return;
    const svgEl = gEl.closest("svg");
    svgEl.classList.remove("hovering");
    svgEl.querySelectorAll("g.sline.hover").forEach(x => x.classList.remove("hover"));
    const hl = svgEl.querySelector(".hover-label");
    if (hl) hl.textContent = "";
  });

  // ---- Grouped bar chart (e.g. rust infection index: 12 groups × N series) ----
  // spec.series: [{label, color, values[12]}] — each series is a hoverable
  // g.sline group (same interaction as line charts: highlight + label).
  window.renderGroupedBarChart = function (spec) {
    const nG = spec.xLabels.length, nS = spec.series.length;
    const yAt = v => y1 - (v - spec.yMin) / (spec.yMax - spec.yMin) * (y1 - y0);
    const xticks = spec.xLabels.map((lab, m) => ({ x: m / nG, lx: (m + 0.5) / nG, label: lab }));
    let g = frameAndAxes(spec, xticks);
    const slot = (x1 - x0) / nG, bw = slot * 0.8 / nS, y0v = yAt(Math.max(0, spec.yMin));
    spec.series.forEach((s, si) => {
      let bars = "";
      s.values.forEach((v, m) => {
        if (v === null || v === undefined) return;
        const gx = x0 + m * slot + slot * 0.1 + si * bw;
        const yv = yAt(v);
        // bar + a full-height invisible hit strip so tiny bars stay hoverable
        bars += `<rect x="${gx.toFixed(1)}" y="${Math.min(y0v, yv).toFixed(1)}" width="${(bw * 0.92).toFixed(1)}" height="${Math.max(0.5, Math.abs(yv - y0v)).toFixed(1)}" fill="${s.color}"/>`;
        bars += `<rect class="hit" x="${gx.toFixed(1)}" y="${y0}" width="${(bw * 0.92).toFixed(1)}" height="${(y1 - y0).toFixed(1)}" fill="#000" fill-opacity="0"><title>${esc(s.label)}</title></rect>`;
      });
      if (bars) g += `<g class="sline" data-label="${esc(s.label)}">${bars}</g>`;
    });
    g += titlesAndLegend(spec, spec.series.map(s => ({ color: s.color, box: true, label: s.label, hover: true })));
    g += `<text class="hover-label" x="${x1 - 4}" y="${y0 + 16}" text-anchor="end" font-size="14" font-weight="700" fill="#111"></text>`;
    return svg(g, spec.title);
  };

  // ---- Bar chart for the decadal SALDO (36 bars, 3/month). spec.values, spec.posColor/negColor ----
  window.renderBarChart = function (spec) {
    const n = 36;
    const yAt = v => y1 - (v - spec.yMin) / (spec.yMax - spec.yMin) * (y1 - y0);
    const xticks = spec.xLabels.map((lab, m) => ({ x: (m * 3) / n, lx: (m * 3 + 1.5) / n, label: lab }));
    let g = frameAndAxes(spec, xticks);
    const slot = (x1 - x0) / n, bw = slot * 0.7, y0v = yAt(0);
    spec.values.forEach((v, j) => {
      if (v === null || v === undefined) return;
      const cx = x0 + (j + 0.5) * slot, yv = yAt(v);
      const top = Math.min(y0v, yv), h = Math.abs(yv - y0v);
      const color = v >= 0 ? (spec.posColor || "#2f6fbf") : (spec.negColor || "#c0392b");
      g += `<rect x="${(cx - bw / 2).toFixed(1)}" y="${top.toFixed(1)}" width="${bw.toFixed(1)}" height="${Math.max(0.5, h).toFixed(1)}" fill="${color}"/>`;
    });
    g += titlesAndLegend(spec, [
      { color: spec.posColor || "#2f6fbf", box: true, label: spec.posLabel || "precipitation > evapotranspiration (mm)" },
      { color: spec.negColor || "#c0392b", box: true, label: spec.negLabel || "evapotranspiration > precipitation (mm)" }
    ]);
    return svg(g, spec.title);
  };
})();
