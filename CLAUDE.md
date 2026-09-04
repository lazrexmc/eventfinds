# EventFinds - rule file

A public, curated, filterable map-and-list directory of events, published as committed static
JSON from one CSV. Python 3 stdlib pipeline; vanilla JS ES-module page; vendored Leaflet; no
database, no server, no framework, no build step, no LLM. $0/month. RapidForge **Build 002**,
built 2026-08-29/30 CDT.

**Standard:** this repo follows `F:\RapidForge\docs\PROJECT_STANDARD.md`.

## Read order

1. `README.md` - what it is, the workflow, the `## Live` ladder
2. `TODO.md` -> **RESUME HERE** - the live state; it outranks every other document here
3. `PLAYBOOK_DELTA.md` - what this build cost to learn (Lessons 1-6)
4. `docs/superpowers/specs/2026-08-30-eventfinds-v1-design.md` - the frozen decisions
5. `F:\RapidForge\modules\event-finder.md` - the shape, its 21 traps, and section 7b's record
   of which acceptance checks ran here and in which form
6. `CHATLOG.md` - the trail, if you need the why (questionnaire answers verbatim; every ruling)

## Standing rules (locked)

- **The publish gate lives in exactly one place**: `is_published()` in `pipeline/export.py`.
  The page carries no copy; gate G6 fails the build if the gate vocabulary or an inline handler
  reappears in the page.
- **No contact columns, anywhere.** The CSV header is a closed 18-column list; gate G7 fails any
  exported key containing contact, email or phone.
- **No auto-publish, ever.** A human sets `visibility`; machines only propose.
- **Failure is not emptiness.** A bad row or unknown town exits 1 naming it and writes nothing;
  a failed page load renders the error box naming the file; zero published rows is an honest
  `event_count: 0`, never a symptom.
- **Nothing is shared with the reference project**: no key, project, data row, domain, brand, or
  its name in the product surface (`site/`, `pipeline/`, `data/`, `README.md`).
- **Stdlib only** in the pipeline; the page's only dependency is vendored.
- **Draft-then-apply**: credentialed steps (the Pages dashboard) are Lance's, batched into one
  sitting. An agent never performs them.
- **Dates and times come from the terminal clock** (`date +'%Y-%m-%d %H:%M %Z'`), never from
  context, and carry their zone. Commit times come from `git log --date=iso`.
- **Plain ASCII punctuation in live documents** (standard rule 15); CHATLOG history stays as
  written.
- Commit trailer: `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`. (Commits up to
  f1e7d33 carry `Claude Fable 5`, which was the correct trailer when they were made; history
  stays as written.)

## Honest status

**BUILT** (rung one): `python -m pytest -q` 65, `npm test` 10, `python pipeline/checks.py`
0 of 10 gates failed - but 4 report N/A on an empty publication (G1, G7, G8, G10 have nothing to
check until rows are published), so coverage is honestly incomplete until Lance adds events; page
verified in a browser in four states; merged to `master`.
**NOT VIEWABLE**: Cloudflare Pages is not connected. The connect parameters, so no session
reconstructs them: repo `lazrexmc/eventfinds`, production
branch `master`, root directory `site`, build command EMPTY, output directory EMPTY, project
`eventfinds` -> https://eventfinds.pages.dev. After connecting, `python pipeline/verify_deploy.py`
must print ALL DEPLOYED (rung two). `event-finder`'s promotion to proven is HELD at RapidForge
until that check (7.8) runs green here.

## Deviations from the standard (declared, each with its reason)

- **No `verify_claims.py` of the usual kind.** `pipeline/checks.py` is the claim checker: G3
  derives the publication from the source, G5 proves the committed pair is self-consistent, G9
  checks the headers. A second checker would be a second place for the same rules to drift.
- **No RLS probe, no migration ledger.** There is no database; the exporter's filter is the wall
  and gates G2/G4 are its probe.
- **No `AUDIT_LOG.md` yet.** The whole-branch review and its eight findings are in `CHATLOG.md`
  (2026-08-30) with verdicts; the log file is owed at the first post-deploy audit, per the
  standard's next-touch rule.
- **No `REBUILD.md` yet.** Rebuild is currently `git clone` + the README's seven steps; the file
  is owed when there is deployed state a clone does not capture (the Pages project settings).
- **No PII guard.** The repo holds no contact data by construction (see the closed header). If a
  contacts table is ever added, add the guard first.
