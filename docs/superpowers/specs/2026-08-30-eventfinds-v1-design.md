# EventFinds v1 — design spec (FROZEN 2026-08-30)

*RapidForge Build 002. Frozen after the Stage 2 questionnaire (answers verbatim in `CHATLOG.md`).
Method: `F:\RapidForge\modules\event-finder.md` (the shape, its wiring, its 21 traps);
constraints: `F:\RapidForge\docs\BUILD_002_eventfinds.md`. This spec does not repeat those; it
records what THIS build fixed and the contracts the plan implements.*

## Amendments since freeze (2026-09-06)

*This spec is a record of what was decided on 2026-08-30 and its sections below are NOT edited - a
dated design document that gets quietly updated stops being a record. Everything the build has since
changed is listed here instead, newest facts first, so a reader knows which sentences below to
distrust.*

| Where | The spec says | What is true now |
|---|---|---|
| section 3 (file structure) and section 8 (heading) | `pipeline/checks.py ... exit 0 only on all-pass` | **False in both places.** The checker has four outcomes - PASS, FAIL, WARN and N/A - and exits 0 while gates report N/A. A gate whose eligible population is empty could not have failed, so it does not pass; the summary refuses the words ALL GATES PASS while any gate is N/A. Added 2026-09-06 |
| section 8 (gate table) | nine gates, G1-G9 | **Ten.** G10 `dated-rows-not-all-past` fails when every published row is dated and every date has passed. Deliberately narrower than the page's upcoming rule, because re-implementing that predicate in Python would be a second copy of a decision this repo forbids. Added 2026-09-03 |
| section 8 (G5) | `git check-ignore site/data/events.json` says NOT ignored | **Two checks now.** Also verifies that HEAD's committed `meta.json` carries the sha256 of HEAD's committed `data/events.csv` - proving the publication and its source were committed together, not merely that git would allow it. Changed 2026-09-03 |
| section 8 (dev-time tests) | `node --test tests/js` | **That command fails on Node 24**, which imports the bare directory as a module. Use `npm test`, or `node --test "tests/js/**/*.test.mjs"`. `package.json` and `README.md` both carry the corrected form. Fixed 2026-08-30 |
| section 1 | "no crawler" | **Still true of v1 and still the shipped scope.** A v2 gather-and-curate layer is designed but not built: `docs/superpowers/specs/2026-09-06-gather-and-curate-design.md`. Nothing in it is implemented |

**Section 9 needs no amendment, and should not be "corrected".** It says `verify_deploy.py` checks
every file under `site/` except `_headers`. That was aspirational when frozen - the marker list was
eight hand-written entries - and became true on 2026-09-03 when the list was replaced by a recursive
walk. The spec was wrong at freeze and is right now.

---

## 1. What v1 is

A **public, curated, filterable map-and-list directory of events**, published as static JSON from a
CSV that one person edits, hosted on Cloudflare Pages at `eventfinds.pages.dev`, $0/month. No
database, no server, no framework, no bundler, no LLM, no crawler, no accounts, no payments.

**Standalone.** Nothing is shared with Glizzness — no key, project, data, domain, brand, or string.
`glizzness.com/festivals` is untouched.

## 2. Decisions (from the questionnaire; do not re-open)

| # | Decision |
|---|---|
| 1 | Standalone product |
| 2 | Start empty — no rows imported from Glizzness |
| 3 | Lance owns the reference data; irrelevant to v1 because of #2 |
| 4 | Curated-only: `data/events.csv` → validate → geocode → export → static page. Intake is v2 |
| 5 | One configurable home per deployment (`pipeline/config.py`); v1 = Columbia, MO; straight-line distance computed **in the browser at load** from `meta.json`'s home — never stored per row |
| 6 | Generic event directory; attendee-shaped columns; no vendor columns in v1 (a `vendor_friendly` attribute is an inbox item, not a column) |
| 7 | No organiser name/email/phone anywhere in the source file — the header is a closed list and the validator rejects any other column |
| 8 | Lance publishes. `visibility = published` requires `last_verified` and `source_url`. The page states "N events · verified as of <max last_verified>" computed from data |
| 9 | City-centroid geocoding from `data/places.csv` (one table, owned here); deterministic ring offset for same-city rows; **an unknown (city, state) fails the export naming the row** |
| 10 | `id` = UUID4 (required, assigned once by `pipeline/assign_ids.py`); `slug` = derived from (name, city, state) at export, collision fails the export; `visibility` enum column; no id ranges anywhere |
| 11 | No public intake |
| 12 | No monetisation; `featured` boolean column reserved and exported, not rendered specially in v1 |
| 13 | Static JSON publication; `site/data/*.json` is **committed** (it is the publication) |
| 14 | `eventfinds.pages.dev` only |
| 15 | Name EventFinds; no reference-project brand or the string Midwest Event Finder in the product surface (`site/`, `pipeline/`, `data/`, `README.md`); decision records may name the reference project |
| 16 | Passed events are hidden; no dimmed/"returns ~Month" path exists (trap 6.1) |
| 17 | `github.com/lazrexmc/eventfinds`, private, Pages root `site`, no build command |

## 3. Repository layout

```
data/events.csv            SOURCE OF TRUTH (committed; public data; closed header)
data/places.csv            city,state,lat,lng — the one geocoding table
pipeline/config.py         HOME, paths, STALE_DAYS, PIPELINE_VERSION
pipeline/model.py          columns, enums, validation, slug, months
pipeline/geocode.py        places table, lookup, ring offset
pipeline/export.py         CSV -> site/data/events.json + meta.json (CLI, fixture flags)
pipeline/assign_ids.py     fills blank id cells with uuid4, once
pipeline/checks.py         the gates (CLI; exit 0 only on all-pass)
pipeline/serve_local.py    local server with production MIME + header parity
pipeline/verify_deploy.py  origin-vs-git after every push (deploy-runbook 7.7)
tests/*.py                 pytest for the pipeline
tests/js/*.test.mjs        node --test for the page's pure predicates
site/index.html            the shell (no inline style, no inline script)
site/css/app.css
site/js/predicates.js      pure: isUpcoming, passesFilter, haversineMiles, esc, distinct*
site/js/data.js            fetchJson + FetchError (typed; never resolves to emptiness)
site/js/app.js             Leaflet + DOM wiring
site/assets/vendor/leaflet/  Leaflet 1.9.4 + Leaflet.markercluster (third-party, vendored)
site/data/events.json, meta.json   THE PUBLICATION (committed)
site/_headers              CSP from an enumeration; no 'unsafe-inline'
```

## 4. Source file contract — `data/events.csv`

Header is **exactly** this list, in this order; any other column is a validation error:

```
id,name,event_type,cadence,city,state,county,start_date,end_date,months,dates_text,attendance_text,homepage_url,source_url,description,last_verified,visibility,featured
```

| Column | Rule |
|---|---|
| `id` | UUID4, lowercase, required, unique |
| `name` | required |
| `event_type` | one of `EVENT_TYPES` (§6) |
| `cadence` | `annual` · `one_time` · `recurring` |
| `city`, `state` | required; `state` is a 2-letter US code |
| `county` | optional |
| `start_date`, `end_date` | ISO `YYYY-MM-DD`; `end_date` needs `start_date`; `end >= start`; **`one_time` requires `start_date`** |
| `months` | `;`-separated ints 1–12, unique; optional. When blank and dates exist, the export derives it from the date range |
| `dates_text` | free display text ("2nd weekend of June") |
| `attendance_text` | optional free text |
| `homepage_url`, `source_url` | if present must start `http://` or `https://`; **`source_url` required when published** |
| `description` | optional |
| `last_verified` | ISO date; **required when published** |
| `visibility` | `published` · `draft` · `retired` |
| `featured` | `true` · `false` · blank (= false) |

Slug is not a column. `slugify(name, city, state)`: lowercase; runs of non-alphanumerics → `-`;
trimmed; two rows with the same slug fail the export.

## 5. Export contract — `site/data/`

**The publish gate is one predicate, in `pipeline/export.py`, and nowhere else:**
`visibility == "published"` and the row geocoded. The page carries no copy of it (checked by gate G6).

`events.json`:
```json
{"events": [ { "id", "slug", "name", "event_type", "cadence", "city", "state", "county",
               "lat", "lng", "start_date", "end_date", "months", "dates_text",
               "attendance_text", "homepage_url", "source_url", "description",
               "last_verified", "featured" } ... ]}
```
Sorted by `slug`. Exactly these keys per event (gate G7). Empty strings become `null`; `months` is
an array; `featured` a boolean; `lat`/`lng` numbers rounded to 5 dp.

`meta.json`:
```json
{"generated_at": "<UTC ISO>", "as_of": "<max last_verified or null>", "event_count": N,
 "home": {"name": "Columbia, MO", "lat": 38.9517, "lng": -92.3341},
 "event_types": ["..."], "source_sha256": "<sha256 of data/events.csv>", "pipeline_version": "1"}
```
Deterministic: a re-run over the same CSV is byte-identical except `generated_at`.

**Failure is not emptiness — the export exits 1 and names the row for:** any validation error;
blank `id`; slug collision; unknown place; a `one_time` row without `start_date`. Zero published
rows is **not** an error (a directory may honestly be empty) — it writes `event_count: 0`.

**Warning (not failure):** a published row whose `end_date` (or `start_date`) is more than
`STALE_DAYS = 60` days in the past — printed with the slug, counted in the checks (G8).

## 6. Vocabularies (`pipeline/model.py`)

`EVENT_TYPES` (starting set; add by editing the list):
`state_fair county_fair festival food_truck_rally farmers_market oktoberfest craft_fair art_fair
music_fest bbq_fest balloon_fest holiday_market cultural_fest sports_tournament rodeo car_show
air_show winery concert market parade race other`

The page builds its type filter from the values **present** in `events.json`, never from this list.

## 7. Page behaviour — `site/`

- **Loads** `data/meta.json` and `data/events.json` with `cache: "no-cache"`; any failure renders
  the error box naming the file — never an empty map.
- **Upcoming** (`predicates.isUpcoming(e, todayISO, nowMonth)`), computed from the browser date:
  `recurring` → always; a row with `end_date ?? start_date` → shown iff that date `>= todayISO`
  (dates win, for annual and one_time alike); no date + `months` → shown iff `max(months) >= nowMonth`;
  no date, no months -> always shown and matches every month filter (a year-round or undated
  event); the curator opts into this by leaving both blank. Passed events are **absent**, not dimmed.
- **Distance** = haversine miles from `meta.home` to the row, computed at load; filter buckets
  50 / 100 / 150 / 250 mi; a row with no distance is hidden under a cap.
- **Filters** built from data: month (1–12), distance, county (`county|state` composite, one option
  per value present), event types (one checkbox per present value, All/None, `k/n` label). One
  `FILT` object, one pure `passesFilter`, every control writes and re-renders.
- **Map:** one `L.markerClusterGroup` (`zoomToBoundsOnClick:false, spiderfyOnMaxZoom:true,
  chunkedLoading:true`); `clusterclick`: `<= 5` children → `spiderfy()`, else `zoomToBounds()`;
  rebuilt on every filter change, then `fitBounds` (maxZoom 12). Dot is a `divIcon` with a **class**,
  no inline style. Tiles from `tile.openstreetmap.org`. Legend: "Pins show the city, not the venue."
- **List panel:** events in the current viewport, sorted by first month then name; row click pans
  and opens the drawer. **Drawer:** conditional rows via `add(label, value)` testing `!= null && !== ""`,
  two badges max (type, one-time); `featured` is exported but not rendered (decision 12), homepage
  link with scheme normalised and `rel="noopener"`, every interpolation through `esc()`.
- **Freshness line** in the header: `"{event_count} events · verified as of {as_of}"` from
  `meta.json`; `"0 events"` and `"as of —"` are honest states.
- **CSP** (`site/_headers`): `default-src 'self'; img-src 'self' data: https://tile.openstreetmap.org
  https://*.tile.openstreetmap.org; script-src 'self'; style-src 'self'; connect-src 'self';
  base-uri 'none'; object-src 'none'; form-action 'self'; frame-ancestors 'none'` plus
  `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`,
  `Permissions-Policy: camera=(), microphone=(), geolocation=()`. No `<base>`; root-relative paths.

## 8. Gates — `pipeline/checks.py` (exit 0 only on all-pass)

| Gate | Proves | Module §7 |
|---|---|---|
| G1 source-valid | `data/events.csv` parses and every row validates; ids and slugs unique | — |
| G2 negative-gate | On a fixture with one `published`, one `draft`, one `retired` row, the export contains **only** the published id | 7.2 |
| G3 export-current | A fresh export of the committed CSV equals `site/data/*.json` (ignoring `generated_at`) | 7.7 |
| G4 unknown-place | A fixture row in a town absent from places exits 1 and names `"<City>, <ST>"` | 7.6 |
| G5 publication-committed | `git check-ignore site/data/events.json` says NOT ignored | — |
| G6 no-gate-in-js | `site/js` contains none of `visibility`, `published`, `draft`, `retired` | 7.1 |
| G7 named-columns | every event in `events.json` has exactly the contract keys; no key contains `contact`, `email`, `phone` | 7.3 |
| G8 stale (WARN) | count of published rows dated > 60 days past; never fails | — |
| G9 headers | `site/_headers` has a CSP with no `'unsafe-inline'`, `nosniff`, `Referrer-Policy` | — |

Plus dev-time tests: `pytest` (pipeline) and `node --test tests/js` (predicates, incl. 7.5's dated
fixtures). Browser verification: `serve_local.py` + Playwright — the empty state, the loaded state
with a fixture export, and the error state with `meta.json` removed.

## 9. Deploy

1. Push to `master`. **The one credentialed step, batched to the end:** Lance connects
   `lazrexmc/eventfinds` to Cloudflare Pages — root `site`, build command empty, output empty.
2. `python pipeline/verify_deploy.py https://eventfinds.pages.dev` — every file under `site/`
   (except `_headers`) byte-matches the origin and the CSP header is served. Exit 1 on drift.
3. Rung two = the URL resolves and verify_deploy is green. Rung three = Lance adds real events and
   uses it.

## 10. Out of scope (captured in `TODO.md` inbox)

Intake/crawler and the promote form (need a DB); per-viewer geolocation; venue-precision geocoding;
payments/`featured` rendering; a `vendor_friendly` attribute; SEO for a client-rendered page;
custom domain.
