# EventFinds - TODO

*RapidForge Build 002. A public, curated, filterable directory of events - a spin-out of Glizzness's
Midwest Event Finder that must not damage it. Method: `F:\RapidForge\modules\event-finder.md`;
build record: `F:\RapidForge\docs\BUILD_002_eventfinds.md`.*

---

## RESUME HERE

**Live state as of 2026-08-30, re-verified 2026-09-03 21:19 CDT. This block outranks every other document
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
ALL DEPLOYED (rung two). Last check by `python pipeline/verify_deploy.py`, 2026-09-03 21:19 CDT:
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

## Stage 2 questionnaire - ANSWERED 2026-08-29 (kept for the record; answers in CHATLOG)

**Genuinely open - no default can stand in for the owner:**

| # | Question | Recommended | Why |
|---|---|---|---|
| **1** | **Relationship to Glizzness:** standalone product / shared backend / Glizzness's north-star under a new name? | **Standalone.** `glizzness.com/festivals` untouched through the 2026-09-10 demo; whether it later points at EventFinds is a second decision | Two finders over one dataset fork (trap 6.20); touching Glizzness before the demo risks the demo |
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

- **TIME DECAY - the failure mode of this product, three items, all latent today because zero rows are
  published and all real the moment Lance publishes one.** A curated directory of dated things gets
  worse on a schedule with no commit, no failing check and no edit: the JSON stays byte-identical and
  the calendar moves. Raised by LinkedUmp 2026-09-03 after its own public board was found advertising
  nothing but finished tournaments; sharpened by VisibleGov the same hour.

  1. **The header counts published rows, not upcoming ones** (`site/js/app.js:230` reads
     `META.event_count`, which `pipeline/export.py` sets to the published count). If every published
     event has passed, the page says "12 events" in the header while the map shows zero and the status
     line says "No upcoming events match. Try Reset." - it advertises what it cannot show. Fix: export
     an `upcoming_count` computed at export time against the export date, or have the page render the
     count from `visibleEvents()` with the published total beside it. The page already HIDES passed
     events correctly (`isUpcoming`, tested against dated fixtures); only the count lies.
  2. ~~**No gate fails on the data's dates.**~~ **DONE 2026-09-03 - G10 dated-rows-not-all-past.** It
     fires when every published row is dated and every date has passed. Deliberately NARROWER than
     the page's upcoming rule, because re-implementing that predicate in Python would be the second
     copy of a decision this repo forbids: a set of month-only rows whose months have passed is NOT
     caught, and the gate is named for what it checks. Six tests drive both directions per lesson 5.
     The residue - month-only decay - belongs to item 1 below and stays open.
  3. **The freshness header uses `max(last_verified)`, the one aggregate that cannot degrade**
     (VisibleGov, which shipped the same shape): every new verification refreshes it, so a single
     actively-updated row holds the header green while the rest rots, and the display gets BRIGHTER as
     coverage gets worse. A mean would sag, a min would go red, a count would climb. Take the STALE
     COUNT over min-and-max: min-and-max hands the reader two timestamps and leaves them to judge; a
     count publishes the decision ("3 of 41 not verified in 30 days") and can be zero, so "0 stale" is
     a real claim rather than the absence of a bad one.

  **When it is built, lift rather than write:** LinkedUmp shipped `tools/public_surface.py` +
  `tools/surface.json` (LinkedUmp f2b0c02, 2026-09-03) whose `freshness` block IS this red condition -
  point it at the same query the page makes, name the date field, set `min_future`, and it fails when
  published rows exist and none has a future date (its own board prints `0 of 2 rows have ends_on >=
  2026-09-03 (need 1)`). Stdlib, no install, config-driven, no session. It also checks that every path
  returns 200, that referenced assets resolve, and what the edge sends for cache. A pointer, not a
  copy: read it there when the first real rows land.
  **Deliberately NOT built yet, and the reason is a rule, not an excuse:** with zero stale rows a
  staleness counter is untestable by construction - a working counter and one hardwired to zero are
  indistinguishable, which is the same defect as a checker reporting HEALTHY on a response it could not
  parse. Build all three with the first real rows, and force one row stale and one row past first, to
  watch the numbers move before trusting them. (The drawer already shows each row's own last_verified;
  generated_at is deliberately not shown as freshness - last built is not last verified.)

- **Before v2 is specced: what stalled the same feature in the predecessor, and who could have
  unstuck it?** (RapidForge rule 12's restored clause, 2026-09-03 - a search of code registries alone
  finds none of this; the owner's own prose history is one of the places.) This build is a spin-out,
  so it has a predecessor and two of its outcomes are unexplained here. (a) The reference's
  promote-to-public design - the exact shape of my v2 intake - is written and explicitly UNBUILT in its
  spec section 9.5. **Half answered 2026-09-04:** RapidForge verified in the reference's own
  source that `Glizzness/TODO.md:214` carries it as an unchecked box reading "Decide the v1.1
  '-> Event Finder' promote (spec section 9.5)" - it is parked at a DECISION, not at effort. So v2
  inherits a choice nobody made rather than a backlog item nobody had time for, which is a different
  thing to plan around. Recorded here because RapidForge no longer tracks peers' work items (Lance,
  2026-09-04: "Nowhere - each project owns its own"), so this repo is the only place it lives.
  Still open: WHY the decision was never made, and who could make it. (b) Its written north-star, a paid regional event
  directory, was never realised. Neither is a code problem and neither is visible in any registry.
  Answer both before designing v2, and take the amendment with it: not only what killed it, but who
  could have unstuck it and whether the reason they did not is known. If the answer is "nobody had
  time", v2 inherits that constraint rather than solving it.
- v2 intake, before any adapter is designed: probe each candidate source with ONE real unauthenticated request and keep the response (RapidForge Build 003 found Reddit 403 on every path and a trends feed returning the wrong category, forty minutes after the adapters were written; now a stage-1 step in the registry)

- v2: intake - point at `Glizzness/crawler/` and the written-but-unbuilt promote design
  (`event-finder` section 5.8); needs a DB (#13) and the passcode gate (`auth-and-gating` section 9,
  unbuilt)
- Later: per-viewer geolocation (header + JS change, trap 6.13); venue-precision geocoding
  (provider decision); `featured` -> payments (Tier-0 gap, two other consumers already)
- SEO: `static-publication-site` field 2 warns client-side rendering bets on crawlers. A public
  directory may care. Investigable when the first real event list exists - not a question
- `verify-deploy` (Glizzness code candidate): EventFinds could be its third consumer

## STANDING CONSTRAINTS

- Do not damage Glizzness: no shared key, project, data, or domain; nothing on `glizzness.com`
  changes before 2026-09-10; run its own probes if anything is ever shared (`event-finder` 7.9)
- No auto-publish, ever. No LLM in the loop. No framework, no bundler, no server
- Draft-then-apply for anything credentialed; batch it into one handoff
- CHATLOG after every substantive exchange; capture-don't-chase; one project at a time
