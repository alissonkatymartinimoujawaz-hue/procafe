// Observed groundwater levels — OPTIONAL overlay for regions/central_highlands.html.
//
// The index's "groundwater store" is MODELLED (rain that falls on an already-wet
// profile, drained by a 150-day recession). If you have real well levels — NAWAPI
// (Trung tâm Quy hoạch và Điều tra tài nguyên nước quốc gia) monitoring bulletins,
// a provincial DONRE series, or your own farm wells — drop them here and the page
// plots them on top of the modelled curve, in the daily and the monthly view.
//
// Format: percentile 0-100 of that well's own record, per month.
//   0   = the lowest level ever recorded for that well
//   100 = the highest
// Percentiles (not metres) so wells of different depths stay comparable, and so an
// observed series can be read against the modelled one on the same axis.
//
// To convert a depth-to-water reading d (metres below ground, so BIGGER = drier):
//   percentile = 100 * (d_max - d) / (d_max - d_min)   over that well's history.
//
// Keys: a station id from window.CH_STATIONS, or "region" for a Central-Highlands
// average applied to every view that has no station-specific series.
//
// Example (delete the comment markers and put your own numbers in):
// window.CH_WELLS = {
//   region: { "2025-11": 62, "2025-12": 55, "2026-01": 41, "2026-02": 28, "2026-03": 19 },
//   buon_ma_thuot: { "2026-01": 38, "2026-02": 25, "2026-03": 14 }
// };
window.CH_WELLS = {};
