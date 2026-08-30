// predicates.js - pure functions, no DOM, no Leaflet. Tested with node --test.
// "Upcoming" is computed from the browser date, from real dates where they exist;
// months are the fallback, never the override. Passed events are absent, not dimmed.

export function isUpcoming(e, todayISO, nowMonth) {
  if (e.cadence === "recurring") return true;
  const last = e.end_date || e.start_date;
  if (last) return last >= todayISO;
  const ms = Array.isArray(e.months) ? e.months : [];
  if (ms.length) return Math.max(...ms) >= nowMonth;
  return true;
}

export function haversineMiles(lat1, lng1, lat2, lng2) {
  const R = 3958.7613, rad = (d) => (d * Math.PI) / 180;
  const dLat = rad(lat2 - lat1), dLng = rad(lng2 - lng1);
  const a = Math.sin(dLat / 2) ** 2
    + Math.cos(rad(lat1)) * Math.cos(rad(lat2)) * Math.sin(dLng / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}

export function countyKey(e) {
  return e.county ? e.county + "|" + (e.state || "") : null;
}

export function firstMonth(e) {
  const ms = Array.isArray(e.months) ? e.months : [];
  return ms.length ? Math.min(...ms) : 99;
}

// filt = { month: "all"|"1".."12", distance: "all"|"50"|"100"|"150"|"250",
//          county: "all"|"<county>|<ST>", types: Set|null }
export function passesFilter(e, filt, todayISO, nowMonth) {
  if (e.lat == null || e.lng == null) return false;
  if (!isUpcoming(e, todayISO, nowMonth)) return false;
  if (filt.types && !filt.types.has(e.event_type)) return false;
  if (filt.distance !== "all") {
    const d = e.distance_mi;
    if (typeof d !== "number" || !Number.isFinite(d) || d > Number(filt.distance)) return false;
  }
  if (filt.county !== "all" && countyKey(e) !== filt.county) return false;
  if (filt.month !== "all") {
    const ms = Array.isArray(e.months) ? e.months : [];
    if (ms.length && !ms.includes(Number(filt.month))) return false;
  }
  return true;
}

const ESC = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
export function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ESC[c]);
}

export function distinctSorted(events, key) {
  return [...new Set(events.map((e) => e[key]).filter((v) => v != null && v !== ""))].sort();
}
