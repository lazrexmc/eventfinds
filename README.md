# EventFinds

A public, curated, filterable map-and-list directory of events. Static JSON published from one
CSV; no database, no server, no framework, $0/month. RapidForge Build 002.

## Live

Built (rung one). Not yet viewable: Cloudflare Pages is not connected. Verification at the origin
is recorded here when it is. When the site is later deployed, this section is where the origin
verification (verify_deploy output, headers, URL semantics) gets recorded.

## Add or change an event (the whole workflow)

1. Edit `data/events.csv` (header is fixed - 18 columns; see `pipeline/model.py` for the rules).
   Leave `id` blank for a new row. If the town is new, add it to `data/places.csv` first
   (`city,state,lat,lng` - city centroid; pins show the city, not the venue).
2. `python pipeline/assign_ids.py`     - gives new rows a permanent UUID
3. `python pipeline/export.py`         - writes `site/data/events.json` + `meta.json`; exits 1 naming
                                         any bad row or unknown town
4. `python pipeline/checks.py`         - nine gates; must print ALL GATES PASS
5. `python -u pipeline/serve_local.py` - view at http://127.0.0.1:8765/ (production MIME + headers).
                                         Use `-u`: stdout is block-buffered when the process is
                                         backgrounded, so without it the startup log appears late.
6. Commit `data/` AND `site/data/` together; push to `master`. Pages deploys.
7. `python pipeline/verify_deploy.py`  - the origin serves what git holds; exit 0 or it did not deploy

A row is public only when `visibility` is `published` (which also requires `source_url` and
`last_verified`). Draft and retired rows never leave the CSV. The page hides events whose date has
passed (or whose last month has passed when no date exists); it never dims them.

## Tests

    npm test                                       # pipeline's page layer: predicates and fetch
    node --test "tests/js/**/*.test.mjs"           # the equivalent, spelled out
    python -m pytest -q                            # pipeline

## Deploy

Cloudflare Pages, project `eventfinds`, connected to `lazrexmc/eventfinds`, production branch
`master`, root directory `site`, build command empty, output directory empty. Headers come from
`site/_headers`. There is no custom domain in v1.

## Method

Built from the RapidForge registry: `modules/event-finder.md` (the shape and its 21 traps),
`static-publication-site`, `deploy-runbook`. Decisions and the questionnaire that froze them are in
`CHATLOG.md`; the frozen spec is `docs/superpowers/specs/2026-08-30-eventfinds-v1-design.md`.
