/* Minimal SVG charts for the Water Availability Index page.
   Same white-card look as assets/chart.js, but with a free x-axis (daily or
   monthly windows instead of a fixed 12-month year) and a hover readout. */
(function () {
  "use strict";
  var W = 920, H = 400, mL = 58, mR = 58, mT = 46, mB = 46;
  var x0 = mL, x1 = W - mR, y0 = mT, y1 = H - mB;
  var esc = function (s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  };
  var f = function (v, d) { return (Math.round(v * Math.pow(10, d)) / Math.pow(10, d)).toFixed(d); };

  function niceRange(vals, padFrac) {
    var v = vals.filter(function (x) { return x != null && isFinite(x); });
    if (!v.length) return { min: 0, max: 1, step: 0.5 };
    var lo = Math.min.apply(null, v), hi = Math.max.apply(null, v);
    if (lo === hi) { lo -= 1; hi += 1; }
    var pad = (hi - lo) * (padFrac == null ? 0.08 : padFrac);
    lo -= pad; hi += pad;
    if (lo > 0 && lo < (hi - lo)) lo = 0;
    var span = hi - lo, raw = span / 5, mag = Math.pow(10, Math.floor(Math.log10(raw))),
        norm = raw / mag, step = (norm <= 1 ? 1 : norm <= 2 ? 2 : norm <= 5 ? 5 : 10) * mag;
    return { min: Math.floor(lo / step) * step, max: Math.ceil(hi / step) * step, step: step };
  }

  function build(spec) {
    var n = spec.n, dec = spec.yDec == null ? 0 : spec.yDec;
    var all = [];
    (spec.series || []).forEach(function (s) { all = all.concat(s.values); });
    if (spec.bars) all = all.concat(spec.bars.values);
    var r = (spec.yMin != null && spec.yMax != null)
      ? { min: spec.yMin, max: spec.yMax, step: spec.yStep || (spec.yMax - spec.yMin) / 5 }
      : niceRange(all, spec.pad);
    var yAt = function (v) { return y1 - (v - r.min) / (r.max - r.min) * (y1 - y0); };
    var xAt = function (i) { return n <= 1 ? (x0 + x1) / 2 : x0 + i / (n - 1) * (x1 - x0); };
    var g = '<rect x="0" y="0" width="' + W + '" height="' + H + '" fill="#ffffff"/>';

    (spec.bands || []).forEach(function (b) {
      var a = yAt(Math.min(b.y1, r.max)), c = yAt(Math.max(b.y0, r.min));
      g += '<rect x="' + x0 + '" y="' + a.toFixed(1) + '" width="' + (x1 - x0).toFixed(1) +
           '" height="' + Math.max(0, c - a).toFixed(1) + '" fill="' + b.fill + '"/>';
    });
    for (var v = r.min; v <= r.max + 1e-9; v += r.step) {
      var y = yAt(v);
      g += '<line x1="' + x0 + '" y1="' + y.toFixed(1) + '" x2="' + x1 + '" y2="' + y.toFixed(1) +
           '" stroke="#e2e2e2"/>' +
           '<text x="' + (x0 - 7) + '" y="' + (y + 3.6).toFixed(1) +
           '" font-size="11" fill="#444" text-anchor="end">' + f(v, dec) + '</text>';
      if (spec.y2 && spec.y2.scale)          // right-hand scale for a second, scaled quantity
        g += '<text x="' + (x1 + 7) + '" y="' + (y + 3.6).toFixed(1) +
             '" font-size="11" fill="#6a86a3" text-anchor="start">' +
             f(v / spec.y2.scale, spec.y2.dec || 0) + '</text>';
    }
    (spec.xTicks || []).forEach(function (t) {
      var x = xAt(t.i);
      if (t.grid !== false)
        g += '<line x1="' + x.toFixed(1) + '" y1="' + y0 + '" x2="' + x.toFixed(1) +
             '" y2="' + y1 + '" stroke="#f0f0f0"/>';
      g += '<text x="' + x.toFixed(1) + '" y="' + (y1 + 16) +
           '" font-size="10.5" fill="#444" text-anchor="middle">' + esc(t.label) + '</text>';
    });

    if (spec.bars) {
      var bw = Math.max(1, (x1 - x0) / Math.max(n, 1) * (spec.bars.width || 0.8)),
          base = yAt(Math.max(r.min, Math.min(0, r.max)));
      spec.bars.values.forEach(function (val, i) {
        if (val == null) return;
        var yv = yAt(val), top = Math.min(yv, base), h = Math.max(0.6, Math.abs(yv - base)),
            col = val < 0 ? (spec.bars.neg || "#c0603c") : (spec.bars.pos || "#3f7fbf");
        g += '<rect x="' + (xAt(i) - bw / 2).toFixed(1) + '" y="' + top.toFixed(1) +
             '" width="' + bw.toFixed(1) + '" height="' + h.toFixed(1) + '" fill="' + col + '"/>';
      });
    }
    if (r.min < 0 && r.max > 0)
      g += '<line x1="' + x0 + '" y1="' + yAt(0).toFixed(1) + '" x2="' + x1 + '" y2="' +
           yAt(0).toFixed(1) + '" stroke="#666"/>';

    (spec.series || []).forEach(function (s) {
      if (s.area && s.lo) {                 // shaded envelope between s.lo and s.values
        var up = [], dn = [];
        for (var i = 0; i < n; i++) {
          if (s.values[i] == null || s.lo[i] == null) continue;
          up.push(xAt(i).toFixed(1) + "," + yAt(s.values[i]).toFixed(1));
          dn.unshift(xAt(i).toFixed(1) + "," + yAt(s.lo[i]).toFixed(1));
        }
        if (up.length)
          g += '<polygon points="' + up.concat(dn).join(" ") + '" fill="' + s.color +
               '" fill-opacity="' + (s.opacity || 0.18) + '"/>';
        return;
      }
      var d = "", pen = false;
      for (var k = 0; k < n; k++) {
        var val = s.values[k];
        if (val == null) { pen = false; continue; }
        d += (pen ? "L" : "M") + xAt(k).toFixed(1) + " " + yAt(val).toFixed(1) + " ";
        pen = true;
      }
      if (d) g += '<path d="' + d + '" fill="none" stroke="' + s.color + '" stroke-width="' +
                  (s.width || 1.8) + '"' + (s.dash ? ' stroke-dasharray="' + s.dash + '"' : "") +
                  ' stroke-linejoin="round"/>';
    });

    g += '<rect x="' + x0 + '" y="' + y0 + '" width="' + (x1 - x0).toFixed(1) + '" height="' +
         (y1 - y0).toFixed(1) + '" fill="none" stroke="#9a9a9a"/>';
    g += '<text x="' + (W / 2) + '" y="20" font-size="14.5" font-weight="700" fill="#1a1a1a" ' +
         'text-anchor="middle">' + esc(spec.title) + '</text>';
    if (spec.subtitle)
      g += '<text x="' + (W / 2) + '" y="37" font-size="11.5" fill="#555" text-anchor="middle">' +
           esc(spec.subtitle) + '</text>';
    if (spec.yLabel)
      g += '<text x="14" y="' + ((y0 + y1) / 2) + '" font-size="11.5" fill="#444" ' +
           'text-anchor="middle" transform="rotate(-90 14 ' + ((y0 + y1) / 2) + ')">' +
           esc(spec.yLabel) + '</text>';
    if (spec.y2Label)
      g += '<text x="' + (W - 14) + '" y="' + ((y0 + y1) / 2) + '" font-size="11.5" fill="#444" ' +
           'text-anchor="middle" transform="rotate(90 ' + (W - 14) + ' ' + ((y0 + y1) / 2) +
           ')">' + esc(spec.y2Label) + '</text>';

    var lx = x0, ly = H - 12;
    (spec.legend || []).forEach(function (it) {
      var w = 30 + String(it.label).length * 6.0;
      if (lx + w > x1 && lx > x0) { lx = x0; ly += 15; }
      g += it.box
        ? '<rect x="' + lx + '" y="' + (ly - 7) + '" width="15" height="10" fill="' + it.color + '"/>'
        : '<line x1="' + lx + '" y1="' + ly + '" x2="' + (lx + 20) + '" y2="' + ly +
          '" stroke="' + it.color + '" stroke-width="2.6"' +
          (it.dash ? ' stroke-dasharray="' + it.dash + '"' : "") + '/>';
      g += '<text x="' + (lx + (it.box ? 19 : 24)) + '" y="' + (ly + 4) +
           '" font-size="11" fill="#333">' + esc(it.label) + '</text>';
      lx += w;
    });
    g += '<g class="wai-cursor" style="display:none"><line y1="' + y0 + '" y2="' + y1 +
         '" stroke="#333" stroke-dasharray="3 3"/></g>';
    g += '<rect class="wai-hit" x="' + x0 + '" y="' + y0 + '" width="' + (x1 - x0).toFixed(1) +
         '" height="' + (y1 - y0).toFixed(1) + '" fill="transparent"/>';
    return { svg: g, xAt: xAt };
  }

  /* host: element. spec.hover(i) -> {title, rows:[{label,value,color}]} */
  function render(host, spec) {
    var b = build(spec);
    host.innerHTML =
      '<div class="wai-chart">' +
      '<svg class="chart-svg" viewBox="0 0 ' + W + ' ' + H + '" ' +
      'preserveAspectRatio="xMidYMid meet" role="img" aria-label="' + esc(spec.title) + '">' +
      b.svg + '</svg><div class="wai-tip" hidden></div></div>';
    if (!spec.hover) return;
    var wrap = host.firstChild, svg = wrap.querySelector("svg"),
        tip = wrap.querySelector(".wai-tip"), cur = svg.querySelector(".wai-cursor"),
        line = cur.firstChild;
    function move(ev) {
      var rect = svg.getBoundingClientRect(),
          px = (ev.touches ? ev.touches[0].clientX : ev.clientX) - rect.left,
          ux = px / rect.width * W,
          i = Math.round((ux - x0) / (x1 - x0) * (spec.n - 1));
      i = Math.max(0, Math.min(spec.n - 1, i));
      var info = spec.hover(i);
      if (!info) { leave(); return; }
      cur.style.display = "";
      line.setAttribute("x1", b.xAt(i).toFixed(1));
      line.setAttribute("x2", b.xAt(i).toFixed(1));
      tip.hidden = false;
      tip.innerHTML = '<b>' + esc(info.title) + '</b>' + info.rows.map(function (r) {
        return '<span><i style="background:' + (r.color || "#999") + '"></i>' + esc(r.label) +
               ' <b>' + esc(r.value) + '</b></span>';
      }).join("");
      var left = b.xAt(i) / W * rect.width;
      tip.style.left = Math.max(4, Math.min(rect.width - tip.offsetWidth - 4, left + 12)) + "px";
    }
    function leave() { cur.style.display = "none"; tip.hidden = true; }
    svg.addEventListener("mousemove", move);
    svg.addEventListener("mouseleave", leave);
    svg.addEventListener("touchstart", move, { passive: true });
    svg.addEventListener("touchmove", move, { passive: true });
  }

  /* Half-circle gauge, 0-100. */
  function gauge(host, o) {
    var w = 240, h = 140, cx = w / 2, cy = 118, R = 92, cats = window.WAI.C.CATS,
        fills = { severe: "#c0392b", deficit: "#e08a3c", normal: "#c9b458",
                  comfort: "#7a9e5e", surplus: "#3f8f7a", na: "#bbb" };
    function pt(v) {
      var a = Math.PI * (1 - v / 100);
      return [cx + R * Math.cos(a), cy - R * Math.sin(a)];
    }
    function arc(v0, v1, rad, col, wdt) {
      var a = pt(v0), c = pt(v1), sc = rad / R;
      return '<path d="M' + (cx + (a[0] - cx) * sc).toFixed(1) + ' ' + (cy + (a[1] - cy) * sc).toFixed(1) +
        ' A' + rad + ' ' + rad + ' 0 0 1 ' + (cx + (c[0] - cx) * sc).toFixed(1) + ' ' +
        (cy + (c[1] - cy) * sc).toFixed(1) + '" fill="none" stroke="' + col +
        '" stroke-width="' + wdt + '" stroke-linecap="butt"/>';
    }
    var g = '<rect width="' + w + '" height="' + h + '" fill="#fff"/>', lo = 0;
    cats.forEach(function (c) {
      var hi = Math.min(100, c.max);
      g += arc(lo, hi, R, fills[c.key], 16); lo = hi;
    });
    var v = o.value == null ? null : Math.max(0, Math.min(100, o.value));
    if (v != null) {
      var p = pt(v);
      g += '<line x1="' + cx + '" y1="' + cy + '" x2="' + (cx + (p[0] - cx) * 0.82).toFixed(1) +
           '" y2="' + (cy + (p[1] - cy) * 0.82).toFixed(1) +
           '" stroke="#2b2320" stroke-width="3.4" stroke-linecap="round"/>';
    }
    g += '<circle cx="' + cx + '" cy="' + cy + '" r="5" fill="#2b2320"/>';
    g += '<text x="' + cx + '" y="' + (cy - 26) + '" font-size="30" font-weight="700" ' +
         'fill="#1a1a1a" text-anchor="middle">' + (v == null ? "—" : Math.round(v)) + '</text>';
    g += '<text x="' + cx + '" y="' + (cy - 10) + '" font-size="11" fill="#666" ' +
         'text-anchor="middle">/ 100</text>';
    g += '<text x="10" y="' + (cy + 14) + '" font-size="10" fill="#888">0</text>';
    g += '<text x="' + (w - 10) + '" y="' + (cy + 14) +
         '" font-size="10" fill="#888" text-anchor="end">100</text>';
    host.innerHTML = '<svg class="chart-svg gauge" viewBox="0 0 ' + w + ' ' + h +
      '" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Water availability index ' +
      (v == null ? "unavailable" : Math.round(v)) + ' out of 100">' + g + '</svg>';
  }

  window.WAICharts = { render: render, gauge: gauge, niceRange: niceRange };
})();
