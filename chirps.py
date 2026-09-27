#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CHIRPS v3.0 rainfall at town points — Python standard library only (no GDAL).

CHIRPS (Climate Hazards Center, UCSB) is a 0.05° (~5.5 km) satellite + rain-gauge
grid, 1981 to near-real time. CHIRPS v2.0 production ends after December 2026, so
this reads v3.0. We read the "latam" (Mexico -> South America) GeoTIFFs straight
from the CHC server with HTTP Range requests: every file stores one image row per
LZW-compressed strip, so a few towns cost ~70 KB per file instead of ~4 MB.

Products (https://data.chc.ucsb.edu/products/CHIRPS/v3.0/):
  dekads/latam/tifs/chirps-v3.0.YYYY.MM.D.tif         FINAL 10-day totals, D = 1..3
                                                      (days 1-10, 11-20, 21-end),
                                                      published ~3rd week of next month
  prelim/pentads/latam/tifs/chirps-v3.0.YYYY.MM.P.tif PRELIMINARY 5-day totals,
                                                      P = 1..6, ~2 days after the pentad
Dekad D = pentads 2D-1 + 2D, so prelim pentads extend the final dekads to ~2 days ago.

Cache: cache/chirps/*.json keeps every value already read (keyed by grid pixel),
so a re-run only downloads new or re-published files.
"""
import json, math, os, re, struct, time, zlib
import urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = "https://data.chc.ucsb.edu/products/CHIRPS/v3.0"
PRODUCTS = {
    # name: (directory, filename regex -> (year, month, index))
    "dekads": (BASE + "/dekads/latam/tifs/", r"chirps-v3\.0\.(\d{4})\.(\d{2})\.([1-3])\.tif"),
    "prelim_pentads": (BASE + "/prelim/pentads/latam/tifs/", r"chirps-v3\.0\.(\d{4})\.(\d{2})\.([1-6])\.tif"),
}
# latam grid (checked against every file read): upper-left corner 120°W 35°N, 0.05° pixels
GRID_X0, GRID_Y0, GRID_RES = -120.0, 35.0, 0.05
HEADERS = {"User-Agent": "procafe-weather/1.0 (CHIRPS point reader)"}
TAIL = 24576            # latam files keep their IFD + strip tables in the last ~16 KB
WORKERS = 6             # parallel downloads (be polite to the CHC server)


def pixel_of(lat, lon):
    """(row, col) of the 0.05° CHIRPS latam pixel containing lat/lon."""
    return (int(math.floor((GRID_Y0 - lat) / GRID_RES + 1e-9)),
            int(math.floor((lon - GRID_X0) / GRID_RES + 1e-9)))


# ---------------------------------------------------------------- HTTP ------
def _http(url, ranges=None, tries=6):
    """GET (optionally several byte ranges). Returns (status, headers, body)."""
    headers = dict(HEADERS)
    if ranges:
        headers["Range"] = "bytes=" + ",".join(ranges)
    last = None
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=90) as r:
                return r.status, r.headers, r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise FileNotFoundError(url)
            last = e
            if e.code < 500 and e.code != 429:
                break
        except Exception as e:                      # timeouts, resets, proxy hiccups
            last = e
        time.sleep(min(30, 2 ** k))
    raise RuntimeError(f"CHIRPS download failed: {url}: {last!r}")


def _parts(status, headers, body):
    """Split a (multi)range response into [(start, bytes)] and the file size."""
    if status == 200:                               # server ignored Range: whole file
        return [(0, body)], len(body)
    ctype = headers.get("Content-Type", "")
    if ctype.startswith("multipart/byteranges"):
        m = re.search(r'boundary="?([^";]+)"?', ctype)
        delim, parts, pos, total = b"--" + m.group(1).encode(), [], 0, None
        while True:
            i = body.find(delim, pos)
            if i < 0 or body[i + len(delim):i + len(delim) + 2] == b"--":
                break
            h_end = body.find(b"\r\n\r\n", i)
            cr = re.search(rb"content-range:\s*bytes\s+(\d+)-(\d+)/(\d+)", body[i:h_end], re.I)
            a, b, total = int(cr.group(1)), int(cr.group(2)), int(cr.group(3))
            parts.append((a, body[h_end + 4:h_end + 4 + b - a + 1]))
            pos = h_end + 4 + b - a + 1
        return parts, total
    m = re.match(r"bytes (\d+)-(\d+)/(\d+)", headers.get("Content-Range", ""))
    return [(int(m.group(1)), body)], int(m.group(3))


# ---------------------------------------------------------------- TIFF ------
def _lzw_decode(data):
    """TIFF LZW (MSB-first codes, 'early change' width switch)."""
    out, table, width, prev = bytearray(), None, 9, None
    bitbuf = nbits = pos = 0
    n = len(data)
    while True:
        while nbits < width:
            if pos >= n:
                return bytes(out)
            bitbuf = ((bitbuf << 8) | data[pos]) & 0xFFFFFFFF
            pos += 1
            nbits += 8
        nbits -= width
        code = (bitbuf >> nbits) & ((1 << width) - 1)
        if code == 256:                             # CLEAR
            table = [bytes((i,)) for i in range(256)] + [b"", b""]
            width, prev = 9, None
            continue
        if code == 257:                             # end of information
            return bytes(out)
        if prev is None:
            entry = table[code]
        else:
            entry = table[code] if code < len(table) else prev + prev[:1]
            table.append(prev + entry[:1])
            if len(table) + 1 in (512, 1024, 2048):
                width += 1
        out += entry
        prev = entry


def _unpredict_float(buf, width, bo):
    """Undo TIFF predictor 3 (floating point) row by row for float32 samples."""
    row_bytes, out = width * 4, bytearray()
    for r in range(len(buf) // row_bytes):
        row = bytearray(buf[r * row_bytes:(r + 1) * row_bytes])
        for i in range(1, row_bytes):
            row[i] = (row[i] + row[i - 1]) & 0xFF
        be = bytearray(row_bytes)                   # byte planes are most-significant first
        for i in range(width):
            be[4 * i:4 * i + 4] = row[i], row[width + i], row[2 * width + i], row[3 * width + i]
        out += be if bo == ">" else b"".join(be[4 * i:4 * i + 4][::-1] for i in range(width))
    return bytes(out)


_TYPES = {1: "B", 2: "B", 3: "H", 4: "I", 5: "I", 6: "b", 7: "B", 8: "h", 9: "i",
          10: "i", 11: "f", 12: "d", 16: "Q", 17: "q", 18: "Q"}
_SIZES = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 1, 7: 1, 8: 2, 9: 4, 10: 8, 11: 4, 12: 8, 16: 8, 17: 8, 18: 8}
_WANTED = {256, 257, 258, 259, 273, 277, 278, 279, 284, 317, 322, 323, 324, 325, 339, 33550, 33922}


class _RemoteTiff:
    """Just enough GeoTIFF to read single float32 pixels over HTTP."""

    def __init__(self, url):
        self.url = url
        parts, self.size = _parts(*_http(url, ["0-15", f"-{TAIL}"]))
        self.segs = parts
        head = self._read(0, 16)
        self.bo = "<" if head[:2] == b"II" else ">"
        self.big = struct.unpack(self.bo + "H", head[2:4])[0] == 43
        ifd = struct.unpack(self.bo + ("Q" if self.big else "I"), head[8:16] if self.big else head[4:8])[0]
        self.tags = self._ifd(ifd)

    def _read(self, off, n):
        for a, data in self.segs:
            if a <= off and off + n <= a + len(data):
                return data[off - a:off - a + n]
        parts, _ = _parts(*_http(self.url, [f"{off}-{off + n - 1}"]))
        self.segs += parts
        return self._read(off, n)

    def _ifd(self, off):
        bo, big = self.bo, self.big
        count = struct.unpack(bo + ("Q" if big else "H"), self._read(off, 8 if big else 2))[0]
        esz, inline = (20, 8) if big else (12, 4)
        raw = self._read(off + (8 if big else 2), count * esz)
        tags = {}
        for k in range(count):
            e = raw[k * esz:(k + 1) * esz]
            tag, typ = struct.unpack(bo + "HH", e[:4])
            cnt = struct.unpack(bo + ("Q" if big else "I"), e[4:12] if big else e[4:8])[0]
            if tag not in _WANTED or typ not in _TYPES:
                continue
            val = e[12:20] if big else e[8:12]
            size = _SIZES[typ] * cnt
            if size > inline:
                val = self._read(struct.unpack(bo + ("Q" if big else "I"), val)[0], size)
            n = cnt * (2 if typ in (5, 10) else 1)
            tags[tag] = struct.unpack(f"{bo}{n}{_TYPES[typ]}", val[:size])
        return tags

    def check_grid(self):
        sx, sy = self.tags[33550][:2]
        i, j, _, x, y, _ = self.tags[33922][:6]
        x0, y0 = x - i * sx, y + j * sy
        if max(abs(x0 - GRID_X0), abs(y0 - GRID_Y0), abs(sx - GRID_RES), abs(sy - GRID_RES)) > 1e-6:
            raise ValueError(f"unexpected CHIRPS grid in {self.url}: origin {x0},{y0} res {sx},{sy}")

    def pixels(self, rowcols):
        """{(row, col): mm or None} — one multi-range request for all needed strips/tiles."""
        t = self.tags
        width, height = t[256][0], t[257][0]
        if t[258][0] != 32 or t.get(339, (1,))[0] != 3 or t.get(277, (1,))[0] != 1:
            raise ValueError(f"{self.url}: expected single-band float32")
        comp, pred = t.get(259, (1,))[0], t.get(317, (1,))[0]
        if 324 in t:                                  # tiled (COG)
            tw, th = t[322][0], t[323][0]
            across = -(-width // tw)
            offs, cnts, bw = t[324], t[325], tw
            loc = {rc: ((rc[0] // th) * across + rc[1] // tw, (rc[0] % th) * tw + rc[1] % tw) for rc in rowcols}
        else:                                         # stripped
            rps = t.get(278, (height,))[0]
            offs, cnts, bw = t[273], t[279], width
            loc = {rc: (rc[0] // rps, (rc[0] % rps) * width + rc[1]) for rc in rowcols}
        blocks = sorted({b for b, _ in loc.values()})
        parts, _ = _parts(*_http(self.url, [f"{offs[b]}-{offs[b] + cnts[b] - 1}" for b in blocks]))
        raw = {}
        for a, data in parts:                         # map returned byte ranges back to blocks
            for b in blocks:
                if a <= offs[b] and offs[b] + cnts[b] <= a + len(data):
                    raw[b] = data[offs[b] - a:offs[b] - a + cnts[b]]
        decoded = {}
        for b in blocks:
            if b not in raw:
                raw[b] = self._read(offs[b], cnts[b])
            if comp == 1:
                buf = raw[b]
            elif comp == 5:
                buf = _lzw_decode(raw[b])
            elif comp in (8, 32946):
                buf = zlib.decompress(raw[b])
            else:
                raise ValueError(f"{self.url}: unsupported TIFF compression {comp}")
            if pred == 3:
                buf = _unpredict_float(buf, bw, self.bo)
            elif pred != 1:
                raise ValueError(f"{self.url}: unsupported TIFF predictor {pred}")
            decoded[b] = buf
        out = {}
        for rc, (b, idx) in loc.items():
            v = struct.unpack_from(self.bo + "f", decoded[b], idx * 4)[0]
            out[rc] = None if (v != v or v < -1.0) else round(v, 2)   # -9999 = no data
        return out


def read_points(url, rowcols):
    tif = _RemoteTiff(url)
    tif.check_grid()
    return tif.pixels(rowcols)


# ------------------------------------------------------------ listings ------
def list_files(product):
    """[(name, (year, month, index), stamp)] from the server's directory listing."""
    url, pattern = PRODUCTS[product]
    _, _, body = _http(url)
    html = body.decode("utf-8", "replace")
    rows = re.findall(r'href="(' + pattern[:-len(r"\.tif")] + r'\.tif)".*?class="date">([^<]+)<', html)
    out = []
    for name, y, m, i, stamp in rows:
        out.append((name, (int(y), int(m), int(i)), stamp.strip()))
    return sorted(out, key=lambda r: r[1])


# --------------------------------------------------------------- cache ------
def _load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return {}


def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"), sort_keys=True)
    os.replace(tmp, path)


def fetch_product(product, rowcols, cache_dir, first_year=1981, log=print):
    """Read every file of `product` (from first_year) at the given pixels.
    Returns {(year, month, index): {"row,col": mm}} and uses/updates the cache."""
    path = os.path.join(cache_dir, product + ".json")
    cache = _load(path)
    keys = [f"{r},{c}" for r, c in rowcols]
    files = [f for f in list_files(product) if f[1][0] >= first_year]
    todo = [f for f in files
            if f[0] not in cache or cache[f[0]]["stamp"] != f[2]
            or any(k not in cache[f[0]]["v"] for k in keys)]
    log(f"  CHIRPS {product}: {len(files)} files on server, {len(todo)} to download")

    def job(f):
        name, _, stamp = f
        vals = read_points(PRODUCTS[product][0] + name, rowcols)
        return name, stamp, {f"{r},{c}": v for (r, c), v in vals.items()}

    done = 0
    with ThreadPoolExecutor(WORKERS) as pool:
        for name, stamp, vals in pool.map(job, todo):
            entry = cache.get(name) if cache.get(name, {}).get("stamp") == stamp else None
            cache[name] = {"stamp": stamp, "v": {**(entry or {}).get("v", {}), **vals}}
            done += 1
            if done % 100 == 0:
                _save(path, cache)
                log(f"    {done}/{len(todo)}")
    _save(path, cache)
    return {period: cache[name]["v"] for name, period, _ in files}


def dekads_at(points, cache_dir, first_year=1981, log=print):
    """Rainfall per dekad for each point.

    points: {point_id: (lat, lon)}
    Returns ({point_id: {"YYYY-MM-D": mm}}, {"final_through": "YYYY-MM-D",
             "prelim_through": "YYYY-MM-P" or None, "partial": ["YYYY-MM-D", ...]})
    Final dekads first; after the last final dekad, prelim pentads are paired into
    dekads (a dekad with only one of its two pentads is kept but listed as partial)."""
    px = {pid: pixel_of(lat, lon) for pid, (lat, lon) in points.items()}
    rowcols = sorted(set(px.values()))
    final = fetch_product("dekads", rowcols, cache_dir, first_year, log)
    out = {pid: {} for pid in points}
    for (y, m, d), vals in final.items():
        for pid, (r, c) in px.items():
            out[pid][f"{y}-{m:02d}-{d}"] = vals.get(f"{r},{c}")
    last_final = max(final) if final else (first_year, 1, 0)
    info = {"final_through": "%d-%02d-%d" % last_final if final else None,
            "prelim_through": None, "partial": []}

    # prelim pentads strictly after the last final dekad
    prelim = fetch_product("prelim_pentads", rowcols, cache_dir, last_final[0], log)
    groups = {}
    for (y, m, p), vals in prelim.items():
        d = (p + 1) // 2
        if (y, m, d) > last_final:
            groups.setdefault((y, m, d), {})[p] = vals
    for (y, m, d), pents in sorted(groups.items()):
        key = f"{y}-{m:02d}-{d}"
        if len(pents) < 2:
            info["partial"].append(key)
        for pid, (r, c) in px.items():
            vs = [pv.get(f"{r},{c}") for pv in pents.values()]
            out[pid][key] = None if any(v is None for v in vs) else round(sum(vs), 2)
        info["prelim_through"] = "%d-%02d-%d" % (y, m, max(pents))
    return out, info
