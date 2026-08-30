# EventFinds — TODO

*RapidForge Build 002. A public, curated, filterable directory of events — a spin-out of Glizzness's
Midwest Event Finder that must not damage it. Method: `F:\RapidForge\modules\event-finder.md`;
build record: `F:\RapidForge\docs\BUILD_002_eventfinds.md`.*

---

## ⏮ RESUME HERE

**Live state as of 2026-08-30. This block outranks every other document here.**

**Stage 2 ANSWERED 2026-08-30** (verbatim in `CHATLOG.md`): #1 **standalone**, #3 **Lance owns
everything ownable**, #13 **static JSON ($0) "for now"** — all fourteen defaults stand. Build is in
Stage 3: spec → freeze → plan → build → review → deploy. Interruptions so far: **0**.

Read order for a cold session: this block → the form → `CHATLOG.md` (why) →
`F:\RapidForge\modules\event-finder.md` §5 and §6 (how, and the traps) →
`F:\RapidForge\docs\BUILD_002_eventfinds.md` (the constraints verbatim).

---

## Stage 2 questionnaire — ANSWERED 2026-08-30 (kept for the record; answers in CHATLOG)

**Genuinely open — no default can stand in for the owner:**

| # | Question | Recommended | Why |
|---|---|---|---|
| **1** | **Relationship to Glizzness:** standalone product / shared backend / Glizzness's north-star under a new name? | **Standalone.** `glizzness.com/festivals` untouched through the 2026-09-10 demo; whether it later points at EventFinds is a second decision | Two finders over one dataset fork (trap 6.20); touching Glizzness before the demo risks the demo |
| **3** | **Who owns the 415 events and their organiser contacts** — Lance, or the LLC's "business data" carve-out? | *(no default — a fact only Lance knows)* | Decides whether #2's later import is his to make |
| **13** | **Where does the database live?** (a) 4th Supabase project, **$10/mo**; (b) schema in an existing project — couples to Glizzness; (c) **static JSON publication, $0**, as EqualShares does | **(c) for v1.** The curated path emits `site/data/*.json`; the page reads a file | This is Build 001's open interruption returning — one answer closes both. **Consequence:** with no DB there is no promote form in v1; the source file is the truth and curation is edit → export → deploy |

**Defaults to confirm — reply only with the numbers that are wrong:**

| # | Question | Default |
|---|---|---|
| 2 | Seed data | **Start empty.** Import a re-verified subset of the 415 later, by explicit act, without contacts — and only if #3 says they are Lance's |
| 4 | v1 scope | **Curated-only:** source file → normalise → geocode → export → static finder page. Crawler intake is v2 (the reference's is pointed at, not rebuilt) |
| 5 | Home / distance | **One configurable home per deployment; v1 home = Columbia, MO; distance computed at load.** Per-viewer geolocation later |
| 6 | Audience | **Generic event directory, attendee-shaped columns; vendor fit an optional attribute, never the gate** |
| 7 | Public columns | **No organiser name/email/phone.** Homepage URL only |
| 8 | Publish authority | **Lance publishes; `verified` = he checked the primary source on a recorded date; page shows "as of"** |
| 9 | Geocoding | **City-centroid table, labelled honestly ("pins show the city, not the venue"); an unknown town fails the export** |
| 10 | Identity | **UUID + `(name, city, state)` slug; `visibility` column; never an id range** |
| 11 | Public submit-an-event in v1 | **No** |
| 12 | Monetisation in v1 | **None; reserve a `featured` column.** No payments module exists anywhere yet |
| 14 | Launch surface | **`eventfinds.pages.dev` first; custom domain later** |
| 15 | Name / brand | **"EventFinds"; no Glizzness brand; no "Midwest Event Finder" string** |
| 16 | Passed events | **Hide** (a finder shows what you can still catch) |
| 17 | Repo | **`lazrexmc/eventfinds`, private, Cloudflare Pages root `site`** — created only on your word |

---

## BUILD QUEUE (v1, on the defaults — reordered if answers change it)

- [ ] `git init`; commit the docs; create the remote (#17) on Lance's word
- [ ] Spec, then freeze: schema of the source file (columns from the class-B list in CHATLOG),
      `visibility` enum, the export contract (`site/data/events.json` + `schedules.json` +
      `meta.json` with the "as of / N events" line computed, never typed)
- [ ] Plan with acceptance criteria = `event-finder` §7 (7.1, 7.2-as-exporter-test, 7.3, 7.5,
      7.6, 7.7, 7.8) + EqualShares-style `pipeline/checks.py` gates
- [ ] Build: `pipeline/` (normalise → geocode → export → checks → serve_local), `site/` (finder
      page — take the shape and the named sub-units from `Glizzness/site/festivals/app.js`, fix
      6.1/6.2/6.3/6.5 rather than inherit them; vendored Leaflet + markercluster; CSP enumerated)
- [ ] Whole-branch adversarial review, then deploy to `*.pages.dev`; verify at the origin (7.8)
- [ ] Dogfood (Lance) → deposit: promote `event-finder` to `proven`; back-propagate to Glizzness
      via RapidForge (traps fixed here that it still carries)

## INBOX (captured, not chased)

- v2: intake — point at `Glizzness/crawler/` and the written-but-unbuilt promote design
  (`event-finder` §5.8); needs a DB (#13) and the passcode gate (`auth-and-gating` §9, unbuilt)
- Later: per-viewer geolocation (header + JS change, trap 6.13); venue-precision geocoding
  (provider decision); `featured` → payments (Tier-0 gap, two other consumers already)
- SEO: `static-publication-site` field 2 warns client-side rendering bets on crawlers. A public
  directory may care. Investigable when the first real event list exists — not a question
- `verify-deploy` (Glizzness code candidate): EventFinds could be its third consumer

## STANDING CONSTRAINTS

- Do not damage Glizzness: no shared key, project, data, or domain; nothing on `glizzness.com`
  changes before 2026-09-10; run its own probes if anything is ever shared (`event-finder` 7.9)
- No auto-publish, ever. No LLM in the loop. No framework, no bundler, no server
- Draft-then-apply for anything credentialed; batch it into one handoff
- CHATLOG after every substantive exchange; capture-don't-chase; one project at a time
