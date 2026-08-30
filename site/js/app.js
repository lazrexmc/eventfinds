// app.js - Leaflet + DOM wiring for EventFinds. All decisions live in predicates.js; this file
// only moves data to the screen. No copy of the exporter's gate exists here (gate G6).
import { haversineMiles, passesFilter, esc, distinctSorted, countyKey, firstMonth } from "./predicates.js";
import { fetchJson, FetchError, DataShapeError, assertShape } from "./data.js";

const $ = (id) => document.getElementById(id);
const errorBox = $("error-box"), statusEl = $("status"), crumbEl = $("crumb"), freshEl = $("fresh");
const drawer = $("drawer"), drawerBody = $("drawer-body");
const listPanel = $("listpanel"), listBody = $("list-body"), lpCount = $("lp-count");

const NOW = new Date();
const pad2 = (n) => String(n).padStart(2, "0");
const TODAY_ISO = `${NOW.getFullYear()}-${pad2(NOW.getMonth() + 1)}-${pad2(NOW.getDate())}`;
const NOW_M = NOW.getMonth() + 1;
const MONTH_NAMES = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

let META = null, EVENTS = [], eventsById = {}, listOpen = false;
const FILT = { month: "all", distance: "all", county: "all", types: null };

// ---------- error rendering: loud, named, never an empty map ----------
function describeError(err) {
  if (err instanceof FetchError) return "Failed to load " + err.path + " \u2014 " + err.detail + ". Nothing on this page is rendered from a failed fetch.";
  if (err instanceof DataShapeError) return err.message;
  return err && err.message ? err.message : String(err);
}
function renderFatal(err) {
  errorBox.replaceChildren();
  const strong = document.createElement("strong");
  strong.textContent = "This page could not load its data.";
  const p = document.createElement("p");
  p.textContent = describeError(err);
  errorBox.append(strong, p);
  errorBox.hidden = false;
  statusEl.hidden = true;
  console.error(err);
}
function setStatus(msg) { statusEl.textContent = msg; statusEl.hidden = !msg; }

// ---------- map: built by boot(), which init() calls before it fetches anything, so a script
// that failed to load (window.L missing or incomplete) is a named error, never a blank map ----------
let L, map, clusterGroup, dotIcon;

function boot() {
  if (!window.L || typeof window.L.markerClusterGroup !== "function") {
    throw new Error("the map library did not load (assets/vendor/leaflet)");
  }
  L = window.L;
  map = L.map("map", { zoomControl: true }).setView([0, 0], 2);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19, attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);
  clusterGroup = L.markerClusterGroup({
    maxClusterRadius: 55, showCoverageOnHover: false, spiderfyOnMaxZoom: true,
    zoomToBoundsOnClick: false, chunkedLoading: true,
  }).addTo(map);
  clusterGroup.on("clusterclick", (a) => {
    if (a.layer.getChildCount() <= 5) a.layer.spiderfy();
    else a.layer.zoomToBounds({ padding: [40, 40] });
  });
  dotIcon = L.divIcon({ className: "evt-dot", iconSize: [16, 16], iconAnchor: [8, 8], html: "<span></span>" });

  document.querySelector("#drawer .close").addEventListener("click", () => drawer.classList.remove("open"));
  listBody.addEventListener("click", (ev) => {
    const r = ev.target.closest(".lp-row");
    if (!r) return;
    const e = eventsById[r.dataset.id];
    if (!e) return;
    map.setView([e.lat, e.lng], Math.max(map.getZoom(), 13));
    openDrawer(e);
  });
  $("list-toggle").addEventListener("click", () => toggleList());
  document.querySelector("#listpanel .lp-close").addEventListener("click", () => toggleList(false));
  map.on("moveend", renderList);
}

const visibleEvents = () => EVENTS.filter((e) => passesFilter(e, FILT, TODAY_ISO, NOW_M));

function render(fit) {
  clusterGroup.clearLayers();
  const vis = visibleEvents();
  const markers = [], pts = [];
  for (const e of vis) {
    const mk = L.marker([e.lat, e.lng], { icon: dotIcon }).bindTooltip(esc(e.name), { direction: "top" });
    mk.on("click", () => openDrawer(e));
    markers.push(mk);
    pts.push([e.lat, e.lng]);
  }
  clusterGroup.addLayers(markers);
  crumbEl.textContent = `${vis.length} event${vis.length === 1 ? "" : "s"}`;
  if (fit && pts.length) map.fitBounds(pts, { padding: [40, 40], maxZoom: 12 });
  renderList();
}
const applyFilters = () => render(true);

// ---------- list panel: events in the current viewport ----------
function whenText(e) {
  if (e.dates_text) return e.dates_text;
  if (e.start_date) return e.end_date && e.end_date !== e.start_date ? e.start_date + " to " + e.end_date : e.start_date;
  const ms = Array.isArray(e.months) ? e.months : [];
  return ms.length ? ms.map((m) => MONTH_NAMES[m]).join("/") : "";
}
function renderList() {
  if (!listOpen) return;
  const b = map.getBounds();
  const vis = visibleEvents().filter((e) => b.contains([e.lat, e.lng]));
  vis.sort((x, y) => firstMonth(x) - firstMonth(y) || x.name.localeCompare(y.name));
  lpCount.textContent = `${vis.length} in view`;
  listBody.innerHTML = vis.length
    ? vis.map((e) => {
        const when = whenText(e);
        const one = e.cadence === "one_time" ? ` \u00b7 <span class="lp-onetime">one-time</span>` : "";
        return `<button type="button" class="lp-row" data-id="${esc(e.id)}">
          <div class="nm"><span class="lp-dot"></span>${esc(e.name)}</div>
          <div class="sub">${esc(e.city)}, ${esc(e.state)}${when ? " \u00b7 " + esc(when) : ""}${one}</div>
        </button>`;
      }).join("")
    : `<div class="lp-empty">No events in this view. Pan or zoom out to see more.</div>`;
}
function toggleList(open) {
  listOpen = open === undefined ? !listOpen : open;
  listPanel.classList.toggle("open", listOpen);
  $("list-toggle").classList.toggle("active", listOpen);
  renderList();
}

// ---------- detail drawer ----------
const badge = (text, cls) => `<span class="badge ${cls}">${esc(text)}</span>`;
function openDrawer(e) {
  const badges = [badge((e.event_type || "").replace(/_/g, " "), "b-grey")];
  if (e.cadence === "one_time") badges.push(badge("One-time event", "b-blue"));
  const rows = [];
  const add = (label, val) => { if (val != null && val !== "") rows.push(`<dt>${esc(label)}</dt><dd>${esc(val)}</dd>`); };
  add("When", whenText(e));
  add("Size / attendance", e.attendance_text);
  add("Distance from " + META.home.name, typeof e.distance_mi === "number" ? Math.round(e.distance_mi) + " mi" : null);
  add("About", e.description);
  add("Last verified", e.last_verified);
  let home = "";
  if (e.homepage_url) {
    const url = /^https?:\/\//.test(e.homepage_url) ? e.homepage_url : "https://" + e.homepage_url;
    home = `<a class="home" href="${esc(url)}" target="_blank" rel="noopener">Event page</a>`;
  }
  const src = e.source_url ? `<a class="src" href="${esc(e.source_url)}" target="_blank" rel="noopener">Source</a>` : "";
  const countyTxt = e.county ? " \u00b7 " + esc(e.county) + (/county$/i.test(e.county) ? "" : " County") : "";
  drawerBody.innerHTML = `
    <h2>${esc(e.name)}</h2>
    <div class="loc">${esc(e.city)}, ${esc(e.state)}${countyTxt}</div>
    <div>${badges.join("")}</div>
    <dl>${rows.join("")}</dl>
    ${home}${src}`;
  drawer.classList.add("open");
}

// ---------- filters, built from the data ----------
function wireFilters() {
  const monthSel = $("f-month");
  for (let i = 1; i <= 12; i++) {
    const o = document.createElement("option");
    o.value = String(i); o.textContent = MONTH_NAMES[i];
    monthSel.appendChild(o);
  }
  const countySel = $("f-county");
  const keys = [...new Set(EVENTS.map(countyKey).filter(Boolean))].sort((a, b) => {
    const [ca, sa] = a.split("|"), [cb, sb] = b.split("|");
    return sa === sb ? ca.localeCompare(cb) : sa.localeCompare(sb);
  });
  for (const key of keys) {
    const [cty, st] = key.split("|");
    const o = document.createElement("option");
    o.value = key; o.textContent = `${cty} (${st})`;
    countySel.appendChild(o);
  }
  const pretty = (t) => t.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  const ALL_TYPES = distinctSorted(EVENTS, "event_type");
  FILT.types = new Set(ALL_TYPES);
  const msBtn = $("ms-btn"), msPanel = $("ms-panel"), msList = $("ms-list");
  const msLabel = () => {
    msBtn.textContent = FILT.types.size === ALL_TYPES.length ? "All types"
      : FILT.types.size === 0 ? "No types" : `${FILT.types.size}/${ALL_TYPES.length} types`;
  };
  for (const t of ALL_TYPES) {
    const lab = document.createElement("label");
    const cb = document.createElement("input");
    cb.type = "checkbox"; cb.checked = true;
    cb.addEventListener("change", () => { cb.checked ? FILT.types.add(t) : FILT.types.delete(t); msLabel(); applyFilters(); });
    lab.append(cb, document.createTextNode(" " + pretty(t)));
    msList.appendChild(lab);
  }
  const msSetAll = (on) => {
    FILT.types = on ? new Set(ALL_TYPES) : new Set();
    msList.querySelectorAll("input").forEach((cb) => { cb.checked = on; });
    msLabel(); applyFilters();
  };
  $("ms-all").addEventListener("click", () => msSetAll(true));
  $("ms-none").addEventListener("click", () => msSetAll(false));
  msBtn.addEventListener("click", () => {
    const willOpen = msPanel.hasAttribute("hidden");
    msPanel.toggleAttribute("hidden", !willOpen);
    msBtn.setAttribute("aria-expanded", willOpen ? "true" : "false");
  });
  document.addEventListener("click", (ev) => {
    if (!$("ms-type").contains(ev.target) && !msPanel.hasAttribute("hidden")) {
      msPanel.setAttribute("hidden", ""); msBtn.setAttribute("aria-expanded", "false");
    }
  });
  msLabel();
  const bind = (elId, key) => { const el = $(elId); el.addEventListener("change", () => { FILT[key] = el.value; applyFilters(); }); };
  bind("f-month", "month"); bind("f-distance", "distance"); bind("f-county", "county");
  $("f-reset").addEventListener("click", () => {
    FILT.month = "all"; FILT.distance = "all"; FILT.county = "all";
    monthSel.value = "all"; $("f-distance").value = "all"; countySel.value = "all";
    msSetAll(true);
  });
}

// ---------- boot ----------
(async function init() {
  try {
    boot();
    setStatus("Loading\u2026");
    const meta = await fetchJson("/data/meta.json");
    const doc = await fetchJson("/data/events.json");
    assertShape(meta, doc);
    META = meta;
    EVENTS = doc.events;
    for (const e of EVENTS) {
      if (typeof e.lat === "number" && typeof e.lng === "number") e.distance_mi = haversineMiles(META.home.lat, META.home.lng, e.lat, e.lng);
    }
    eventsById = Object.fromEntries(EVENTS.map((e) => [String(e.id), e]));
    freshEl.textContent = `${META.event_count} event${META.event_count === 1 ? "" : "s"} \u00b7 verified as of ${META.as_of || "\u2014"}`;
    map.setView([META.home.lat, META.home.lng], 7);
    wireFilters();
    setStatus("");
    render(true);
    if (!EVENTS.length) setStatus("No events listed yet.");
    else if (!visibleEvents().length) setStatus("No upcoming events match. Try Reset.");
  } catch (err) {
    renderFatal(err);
  }
})();
