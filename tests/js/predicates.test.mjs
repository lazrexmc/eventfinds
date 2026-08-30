import { test } from "node:test";
import assert from "node:assert/strict";
import { isUpcoming, haversineMiles, passesFilter, esc, distinctSorted, countyKey, firstMonth }
  from "../../site/js/predicates.js";

const T = "2026-08-30", M = 8;
const ev = (o) => ({ cadence: "annual", start_date: null, end_date: null, months: [], ...o });

test("7.5 dated fixtures: dates win, for annual and one_time alike", () => {
  assert.equal(isUpcoming(ev({ start_date: "2026-08-29", end_date: "2026-08-29" }), T, M), false); // ended yesterday
  assert.equal(isUpcoming(ev({ start_date: "2026-08-30" }), T, M), true);                          // today
  assert.equal(isUpcoming(ev({ cadence: "one_time", start_date: "2026-08-30" }), T, M), true);
  assert.equal(isUpcoming(ev({ cadence: "one_time", start_date: "2026-08-29" }), T, M), false);
  assert.equal(isUpcoming(ev({ start_date: "2026-08-02", end_date: "2026-08-03", months: [8] }), T, M), false); // trap 6.3: month alone would say upcoming
});

test("month fallback only when no date exists; recurring always", () => {
  assert.equal(isUpcoming(ev({ months: [9] }), T, M), true);
  assert.equal(isUpcoming(ev({ months: [7] }), T, M), false);
  assert.equal(isUpcoming(ev({ months: [6, 8] }), T, M), true);
  assert.equal(isUpcoming(ev({}), T, M), true);
  assert.equal(isUpcoming(ev({ cadence: "recurring", months: [1] }), T, M), true);
});

test("haversine: Columbia to Kansas City is about 125 miles", () => {
  const d = haversineMiles(38.9517, -92.3341, 39.0997, -94.5786);
  assert.ok(d > 118 && d < 132, String(d));
  assert.equal(haversineMiles(38.9517, -92.3341, 38.9517, -92.3341), 0);
});

test("passesFilter: one object, one predicate", () => {
  const base = ev({ event_type: "festival", county: "Boone", state: "MO", months: [9], distance_mi: 0, lat: 38.9517, lng: -92.3341 });
  const all = { month: "all", distance: "all", county: "all", types: null };
  assert.equal(passesFilter(base, all, T, M), true);
  assert.equal(passesFilter(base, { ...all, types: new Set(["rodeo"]) }, T, M), false);
  assert.equal(passesFilter(base, { ...all, types: new Set(["festival"]) }, T, M), true);
  assert.equal(passesFilter(base, { ...all, month: "9" }, T, M), true);
  assert.equal(passesFilter(base, { ...all, month: "10" }, T, M), false);
  assert.equal(passesFilter(ev({ ...base, months: [] }), { ...all, month: "10" }, T, M), true); // no months = any month
  assert.equal(passesFilter(base, { ...all, county: "Boone|MO" }, T, M), true);
  assert.equal(passesFilter(base, { ...all, county: "Boone|IA" }, T, M), false);
  assert.equal(passesFilter({ ...base, distance_mi: 0 }, { ...all, distance: "50" }, T, M), true);   // trap 6.2: zero is a distance
  assert.equal(passesFilter({ ...base, distance_mi: 80 }, { ...all, distance: "50" }, T, M), false);
  assert.equal(passesFilter({ ...base, distance_mi: undefined }, { ...all, distance: "50" }, T, M), false); // unknown hidden under a cap
  assert.equal(passesFilter(ev({ ...base, months: [7] }), all, T, M), false); // passed events are absent
});

test("esc escapes the five characters", () => {
  assert.equal(esc(`<a href="x">&'</a>`), "&lt;a href=&quot;x&quot;&gt;&amp;&#39;&lt;/a&gt;");
  assert.equal(esc(null), "");
  assert.equal(esc(0), "0");
});

test("distinctSorted, countyKey, firstMonth", () => {
  const es = [ev({ event_type: "rodeo" }), ev({ event_type: "festival" }), ev({ event_type: "rodeo" }), ev({ event_type: null })];
  assert.deepEqual(distinctSorted(es, "event_type"), ["festival", "rodeo"]);
  assert.equal(countyKey({ county: "Boone", state: "MO" }), "Boone|MO");
  assert.equal(countyKey({ county: null, state: "MO" }), null);
  assert.equal(firstMonth(ev({ months: [11, 3] })), 3);
  assert.equal(firstMonth(ev({})), 99);
});
