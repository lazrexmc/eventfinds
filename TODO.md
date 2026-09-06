# EventFinds - TODO

*RapidForge Build 002. A public, curated, filterable directory of events - a spin-out of Glizzness's
Midwest Event Finder that must not damage it. Method: `F:\RapidForge\modules\event-finder.md`;
build record: `F:\RapidForge\docs\BUILD_002_eventfinds.md`.*

---

## RESUME HERE

**Live state as of 2026-08-30, re-verified 2026-09-06 12:21 CDT. This block outranks every other document
here.** Re-verified by running, not by reading: `python -m pytest -q` 65, `npm test` 10,
`python pipeline/checks.py` 0 of 10 failed with 4 N/A (see below), `python pipeline/verify_deploy.py` 21 markers
HTTP 0 (still not deployed). No fact in this block changed; only the verification date did.

**v1 is BUILT (rung one) and MERGED to `master`, pushed to github.com/lazrexmc/eventfinds (private).**
Twelve plan tasks with a review gate each, a whole-branch adversarial review (0 Critical, 8 Important,
all fixed and re-verified). Checks at HEAD: `python -m pytest -q` (65), `npm test` (10),
`python pipeline/checks.py` (0 of 10 failed). **Four gates report N/A rather than PASS** - G1, G7,
G8 and G10 all key on the published population, which is empty, so they could not have failed and
did not pass. The summary says COVERAGE IS INCOMPLETE and that is correct: publishing the first
real rows is what turns those four on. The page was verified in a browser in four states.
G10 and the N/A outcome were added 2026-09-03; see CHATLOG.
Every controller ruling is in CHATLOG.md (2026-08-30 00:xx CDT entry).

**The ONE thing blocking rung two is Lance's:** connect Cloudflare Pages. Dashboard -> Workers & Pages
-> Create -> Pages -> Connect to Git -> repo `lazrexmc/eventfinds` -> production branch `master` ->
root directory `site` -> build command EMPTY -> build output directory EMPTY -> Save and Deploy.
Project name `eventfinds` (URL https://eventfinds.pages.dev). Trap: the dashboard funnels toward
Workers; choose Pages. Then run `python pipeline/verify_deploy.py` in F:\EventFinds: it must print
ALL DEPLOYED (rung two). Last check by `python pipeline/verify_deploy.py`, 2026-09-06 12:21 CDT:19 CDT:
21 markers HTTP 0 - the origin does not resolve; not connected.
When it is green: record it in README `## Live` and CHATLOG (clock-dated, plain ASCII), commit, push,
and message the RapidForge session with the verify_deploy output. **NOTHING IS WATCHING.** An hourly
origin check ran from 2026-08-30 until 2026-09-04 20:41 CDT, when Lance stopped it ("no heartbeat
required"); the job is cancelled and it was session-only, so it left nothing behind. Whoever next
opens this repo runs `python pipeline/verify_deploy.py` themselves - there is no timer that will
notice the connect and no message that will arrive when it happens.

**Registry state (F:\RapidForge):** `modules/event-finder.md` promotion to `proven` is HELD until
check 7.8 (origin equals git) runs green here; its new section 7b records which of this build's checks
ran and in which form (7.1/7.2/7.3 in the exporter-file form, 7.5/7.6/7.7 exact, 7.4 database-variant
only, 7.9 N/A standalone, 7.8 pending). verify-deploy (pipeline/verify_deploy.py) becomes a code module
on that same run.

**`CLAUDE.md` exists** - Lance approved it 2026-08-30 CDT; it is the rule file a fresh session reads
first, and it carries the Pages connect parameters and this repo's declared deviations. Standing
conventions: plain ASCII punctuation, dates from the
terminal clock with the zone, `F:\RapidForge\docs\PROJECT_STANDARD.md`.

Read order for a cold session: this block -> `README.md` -> `CHATLOG.md` (why) ->
`docs/superpowers/specs/2026-08-30-eventfinds-v1-design.md` -> `F:\RapidForge\modules\event-finder.md`.

## NOW

**Waiting on Lance, two things, neither of them work for this session:**
1. **Connect Cloudflare Pages** (parameters in the RESUME block above) - the only step between
   rung one and rung two.
2. **Which directory is canonical**, EventFinds or the reference? Sharing between peer repos is
   permitted as of 2026-09-06, so ~410 verified rows and a city centroid table are available - but
   importing them makes a second public directory over one dataset, and the two fork at the first
   re-verification pass (`event-finder` trap 6.20). Permission is not the blocker; forking is.

**Designed, not built:** the v2 gather-and-curate layer (a private low-bar store, then human
curation, then the existing publish gate). Decisions D1-D3 with their reasoning are in
`docs/superpowers/specs/2026-09-06-gather-and-curate-design.md`. Nothing starts until item 2 is
answered, because if EventFinds is not canonical the work is wasted.

---

## BUILD QUEUE (v1, on the defaults - reordered if answers change it)

- [x] `git init`; commit the docs; create the remote (#17) on Lance's word
- [x] Spec, then freeze: schema of the source file (columns from the class-B list in CHATLOG),
      `visibility` enum, the export contract (`site/data/events.json` + `schedules.json` +
      `meta.json` with the "as of / N events" line computed, never typed)
- [x] Plan with acceptance criteria = `event-finder` section 7 (7.1, 7.2-as-exporter-test, 7.3, 7.5,
      7.6, 7.7, 7.8) + EqualShares-style `pipeline/checks.py` gates
- [x] Build: `pipeline/` (normalise -> geocode -> export -> checks -> serve_local), `site/` (finder
      page - take the shape and the named sub-units from `Glizzness/site/festivals/app.js`, fix
      6.1/6.2/6.3/6.5 rather than inherit them; vendored Leaflet + markercluster; CSP enumerated)
- [x] Whole-branch adversarial review DONE 2026-08-30 CDT (0 Critical, 8 Important, all fixed and re-verified; v1 merged fast-forward to master and pushed). Next: deploy to
      `*.pages.dev`; verify at the origin (7.8)
- [ ] Dogfood (Lance) -> deposit: promote `event-finder` to `proven`; back-propagate to Glizzness
      via RapidForge (traps fixed here that it still carries)

## INBOX (captured, not chased)

- **UNBLOCKED 2026-09-06: sharing across peer repos is permitted** (Lance, this session: "you can
  share with other peers"). The Glizzness session has offered ~410 published circuit events with
  counties, coordinates, dates, last_verified stamps and provenance, a 373-line city centroid table
  that would fill most of `data/places.csv`, and `DISCOVERY_METHOD.md` - the method behind twelve
  adversarially-verified research passes. **Still gated on ONE owner decision, not on permission:
  which directory is canonical.** Importing ~410 rows creates a second public directory over one
  dataset, and the two fork at the first re-verification pass (`event-finder` trap 6.20). If
  EventFinds is canonical the mapping is worth writing; if it is not, the mapping is wasted work.
  Asked; not assumed. Independent of that answer: contact columns never cross (gate G7), and the
  city table is a clean take because coordinates are public facts with no consent question.

- CLAUDE.md rule 5 is stricter than the decision it came from: "nothing shared with the reference
  project" bars a data row outright, but Lance owns the 415 events and the questionnaire left a
  re-verified import as his to make. Reword to "not without an explicit owner decision recorded in
  CHATLOG" on the next touch of that file (self-reported in the 2026-08-30 consent check)
- A tenth gate for plain ASCII in live documents: rule 9 of CLAUDE.md is the only locked rule with no
  check behind it (G1-G10 are source-valid, negative, export-current, unknown-place,
  publication-committed, no-gate-in-js, named-columns, stale, headers). PostKit enforces its with a
  gate; here it is habit plus a grep. Note: the product surface is ASCII on disk by design - the page
  renders a middle dot and an em dash through \u escapes - so the gate must check documents,
  not site/js
- ~~Counted claims in prose (standard rule 2)~~ - DONE 2026-08-30: the registry adopted this session's
  proposed wording (a number complies by derivation OR by the sentence naming the command that produces
  it), and every counted claim in CLAUDE.md and TODO.md now names its command. PostKit's two conditions
  apply here too: the command sits in the SAME sentence, and a declared substitute must not overstate
  what it covers

- **TIME DECAY - this product's failure mode: the artifact rots on the calendar with no commit,
  no edit and no failing check.** Two of three parts still open, both latent while zero rows are
  published and both real the moment rows exist.
  1. **The header counts published rows, not upcoming ones** (`site/js/app.js:230` renders
     `META.event_count`), so a directory whose events had all passed would print "12 events" above
     an empty map. The page hides passed events correctly; only the count lies.
  2. ~~No gate fails on the data's dates~~ - **DONE 2026-09-03, G10.**
  3. **The freshness header uses `max(last_verified)`, the one aggregate that cannot degrade** - one
     actively updated row holds it green while the tail rots. Replace with a stale COUNT, which can
     be zero and so makes "0 stale" a real claim.
  **Not built, and the reason is a rule:** with zero stale rows a counter hardwired to zero is
  indistinguishable from a working one. Build 1 and 3 with the first real rows, forcing one row past
  and one stale first to watch the numbers move. **Lift, do not write:** LinkedUmp's
  `tools/public_surface.py` + `surface.json` (f2b0c02) already implement the red condition.
  Reasoning and attribution: CHATLOG 2026-09-03.
- **Before v2 is specced: why did the predecessor never build this, and who could have unstuck it?**
  Half answered - `Glizzness/TODO.md:214` parks the promote design at a DECISION, not at effort, so
  v2 inherits a choice nobody made rather than a backlog nobody had time for. Still open: why the
  decision was never taken, and who can take it. The reference's written north-star (a paid regional
  directory) was also never realised, and that is the commercial premise this project inherits.
  Reasoning: CHATLOG 2026-09-03 and 2026-09-04.
- v2 intake, before any adapter is designed: probe each candidate source with ONE real unauthenticated request and keep the response (RapidForge Build 003 found Reddit 403 on every path and a trends feed returning the wrong category, forty minutes after the adapters were written; now a stage-1 step in the registry)

- v2: intake - point at `Glizzness/crawler/` and the written-but-unbuilt promote design
  (`event-finder` section 5.8); needs a DB (#13) and the passcode gate (`auth-and-gating` section 9,
  unbuilt)
- Later: per-viewer geolocation (header + JS change, trap 6.13); venue-precision geocoding
  (provider decision); `featured` -> payments (Tier-0 gap, two other consumers already)
- SEO: `static-publication-site` field 2 warns client-side rendering bets on crawlers. A public
  directory may care. Investigable when the first real event list exists - not a question
- `verify-deploy` (Glizzness code candidate): EventFinds could be its third consumer

## Stage 2 questionnaire - ANSWERED 2026-08-29 (kept for the record; answers in CHATLOG)

**Genuinely open - no default can stand in for the owner:**

| # | Question | Recommended | Why |
|---|---|---|---|
| **1** | **Relationship to Glizzness:** standalone product / shared backend / Glizzness's north-star under a new name? | **Standalone** (Lance's word). The rider about `glizzness.com/festivals` being untouched through a 2026-09-10 demo was NOT his - it traces to a RapidForge Build 002 brief, and the Glizzness session confirmed 2026-09-06 that the freeze was self-imposed and had acquired owner authority by being written down. Corrected here rather than deleted | Two finders over one dataset fork (trap 6.20) is the real constraint and is still open |
| **3** | **Who owns the 415 events and their organiser contacts** - Lance, or the LLC's "business data" carve-out? | *(no default - a fact only Lance knows)* | Decides whether #2's later import is his to make |
| **13** | **Where does the database live?** (a) 4th Supabase project, **$10/mo**; (b) schema in an existing project - couples to Glizzness; (c) **static JSON publication, $0**, as EqualShares does | **(c) for v1.** The curated path emits `site/data/*.json`; the page reads a file | This is Build 001's open interruption returning - one answer closes both. **Consequence:** with no DB there is no promote form in v1; the source file is the truth and curation is edit -> export -> deploy |

**Defaults to confirm - reply only with the numbers that are wrong:**

| # | Question | Default |
|---|---|---|
| 2 | Seed data | **Start empty.** Import a re-verified subset of the 415 later, by explicit act, without contacts - and only if #3 says they are Lance's |
| 4 | v1 scope | **Curated-only:** source file -> normalise -> geocode -> export -> static finder page. Crawler intake is v2 (the reference's is pointed at, not rebuilt) |
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
| 17 | Repo | **`lazrexmc/eventfinds`, private, Cloudflare Pages root `site`** - created only on your word |

---

## STANDING CONSTRAINTS

- Do not damage Glizzness: no shared key, project, data, or domain; nothing on `glizzness.com`
  changes before 2026-09-10; run its own probes if anything is ever shared (`event-finder` 7.9)
- No auto-publish, ever. No LLM in the loop. No framework, no bundler, no server
- Draft-then-apply for anything credentialed; batch it into one handoff
- CHATLOG after every substantive exchange; capture-don't-chase; one project at a time
