# EventFinds — CHATLOG

*Word-for-word decision trail. Appended after every substantive exchange. This is the source of
truth for "why." Conventions: `~/.claude/CLAUDE.md`. Method: `F:\RapidForge` (the registry).*

---

## 2026-08-29 — Session start: an empty directory and a peer

`F:\EventFinds` was opened as a brand-new session paired with the RapidForge session
(`rapidforge-94`). The directory was empty: no git, no files. Nothing on the machine named
EventFinds — not a RapidForge document, not a TODO inbox, not a memory. The nearest prior art found
by grep was Glizzness's **Midwest Event Finder** (`site/festivals/` on `glizzness.pages.dev/festivals`)
and its **Signal Net** crawler. No files were created and no shape was picked: Stage 0 of the
RapidForge pipeline (the brain-dump) is Lance's.

This session messaged RapidForge announcing itself, what it had read, what it had found, and asked
whether it held a brief.

## 2026-08-29 — The brief, relayed by RapidForge (Build 002)

RapidForge replied that Lance gave it the brief at the start of its turn. **Lance's words, unedited,
as relayed:**

> "RapidForge needs to look at the glizzness.com/festival module and utilize the newly created
> called EventFinds so we can expand on that idea exponentially but not mess up the glizzness's
> intent and possibly improve it over time as it links RapidForge and EventFinds and they can talk
> and work together."

That is the whole of Stage 0. RapidForge's reading, which this session shares: EventFinds is a
spin-out of the Glizzness Midwest Event Finder concept — the *public discovery map*, not the private
Scout board — intended to grow well beyond Glizzness's scope, under two constraints Lance stated:
it must not damage Glizzness's intent (whose written north-star is a paid Midwest event directory),
and improvements should flow back to Glizzness over time via the registry.

**Owner-only, not to be answered by either session:** whether EventFinds is a standalone product, a
shared backend, or Glizzness's north-star realised under a new name.

**Division of labour agreed:**
- RapidForge owns module extraction: six readers mapping `site/festivals` (app, data model, ETL
  chain, intent docs, Signal Net, existing catalogue entries), then an event-finder recipe module
  with Glizzness as the reference implementation — pointers, never copies. Build 002 gets an
  `INTERRUPTIONS.md` entry in RapidForge.
- This session owns Stages 1–2 once that module lands: selection from `modules/README.md` with
  near-misses stated, then the A/B/C parameter split and one batched questionnaire. Only class C
  reaches Lance. RapidForge will send the owner-only questions it already sees, to merge.
- Boundaries from the start: EventFinds gets **its own Supabase project and its own data**.
  Glizzness's anon key is public by design but is Glizzness's. Glizzness's 415 curated events and
  organiser-contact columns are its work product — seeding from them is an owner decision, not a
  default.

**Correction taken:** this session had written that Signal Net was "built 2026-07-16, never
deployed." That came from a stale index line in Glizzness's memory; the memory file itself and
`SIGNAL_NET.md` say LIVE. Verified against `gh run list` — result recorded in the next entry.

## 2026-08-29 — Signal Net verified live; provisional Stage-1 pre-selection sent

**Verification (peer's correction was right):** `gh workflow list` → `crawler.yml` active.
`gh run list --workflow crawler.yml --event schedule` → the ten most recent scheduled runs all
`success`, cadence ~4–6h (GitHub cron drift), latest `2026-08-29T22:24:36Z`. That run's log: seven
sources polled (`tribe:coopers 2, buroak 0, bluenote 10, rosemusichall 10, mizzou 82, missourian 3,
reddit:columbiamo 8`) and `NEW inserted to event_signals: 3`. Schedule fires **and writes**. What was
not checked: the table itself. The wrong claim came from Glizzness's memory *index* line ("repo, not
deployed"), which the memory file beneath it contradicts — a convenient-surface lie of the kind
Tier-1 rule 5 names.

**Provisional pre-selection** (field 2 of all 11 written modules; not committed; awaits RapidForge's
event-finder module):
- *Select regardless of v1 scope:* `static-publication-site`, `supabase-rls-wall`, `rls-probe`,
  `deploy-runbook` (phase 1 at minimum), `applied-state-verification`.
- *Select if v1 ingests:* `ingestion-pipeline`, `scheduled-worker-github-actions`,
  `staleness-detection`, `dead-mans-switch`, `extractor-provenance`.
- *Owner-dependent:* `auth-and-gating` only if a private surface exists.
- *Rejected:* `spend-ledger`, `grounding-database`, `model-routing` — no LLM in the loop.
- *Near-miss to carry forward:* `static-publication-site` field 2 warns that client-side rendering
  bets on crawlers; a public event directory may care about SEO.

**Owner-only questions seen so far, sent to RapidForge for merging:** relationship to Glizzness;
seed from its 415 events or start empty; curated-only vs ingestion in v1; geography; audience
(vendors / attendees / both); launch surface (`*.pages.dev` vs custom domain); monetisation posture
in v1; public submit-an-event intake. Each will carry a recommended default.

Files in this directory at the end of this entry: `CHATLOG.md` only. No git, no shape, no schema.

## 2026-08-30 — The module landed; Stage 1 selection; class B answered; Stage 2 issued

RapidForge delivered `modules/event-finder.md` (`single-source`, Glizzness reference, six readers,
21 traps, 13 parameters) and `docs/BUILD_002_eventfinds.md` (the brief verbatim, the intent
constraints with paths, and a merged class-C list of sixteen lines — this session's eight folded in).
The registry README now lists `event-finder` as a **product shape** module and marks the
`public-directory-gated-admin` archetype as carried by it.

**Stage 1 — selection (on the recommended defaults; revisited if answers change them):**

- *Selected for v1:* `event-finder` (finder page + curated data path; **not** the intake);
  `static-publication-site` in its static-JSON variant (VisibleGov for the page shape, EqualShares
  for `export_site.py` → `site/data/*.json`, `checks.py` gates, `serve_local.py` MIME/header
  parity — the module already names static JSON as the $0 fallback at its §~257);
  `deploy-runbook` phase 1 plus 7.7 origin-vs-git after every push.
- *Deferred, conditional on answers:* `supabase-rls-wall`, `rls-probe`, `applied-state-verification`
  (only if #13 lands on a database); `ingestion-pipeline`, `scheduled-worker-github-actions`,
  `staleness-detection`, `dead-mans-switch` (only if #4 widens to ingestion); `auth-and-gating`
  (only if a private surface exists — a promote form with a DB, or #11 = yes);
  `extractor-provenance` (when a rewritable producer exists; v1's export is a deterministic
  function of one file — field 2's "recomputed from scratch on every read" near-miss applies).
- *Rejected:* `spend-ledger`, `grounding-database`, `model-routing`, `publication-trust-chain` —
  no LLM in the loop, by the reference's own constraint.
- *Near-miss carried to the inbox:* SEO on a client-rendered directory.

**Class B — investigated, not asked:**
- *Paging:* start-empty + static JSON → no PostgREST 1,000-row cap exists; the threshold becomes
  file size, and fetch-once holds to a few thousand rows. No decision needed for v1.
- *What transfers as code vs recipe for a static-JSON v1:* from `Glizzness/site/festivals/app.js`
  the shape and the named sub-units (season-aware predicate `:25-53`, cluster + spiderfy `:55-74`,
  data-built filters `:235-287`, viewport list `:140-171`, conditional drawer + `esc()`
  `:173-211`) transfer as *recipe* — pointed at, re-implemented with traps 6.1/6.2/6.3/6.5 fixed;
  `fetchJSON` becomes a file read; the RLS gate becomes the exporter's `visibility = 'published'
  and lat/lng present` filter, tested as the negative test (7.2). From EqualShares, the
  `export → checks → serve_local` chain transfers as recipe with the same gate names.
- *Public column list for a generic event (from `DATA_MODEL.md`, vendor columns dropped):* `id`
  (uuid), `slug`, `name`, `event_type`, `cadence`, `city`, `state`, `county`, `lat`, `lng`,
  `typical_dates` (display), `attendance_text`, `homepage_url`, `primary_source_url`,
  `description`, `last_verified`, `visibility`, `featured`; schedules: `event_id`, `month`,
  `start_date`, `end_date`. **Excluded:** `contact_name/email/phone`, `application_method`,
  `food_vendor_fee`, `food_truck_friendly` (an optional attribute if the audience answer wants it),
  `distance_from_columbia_mi` (computed at load from the configured home), `needs_confirmation`
  (subsumed by `verified` semantics + `last_verified`).
- *Geocoder:* `Glizzness/vending_circuit_geocode.py` holds a Python dict `C` of city → (lat, lng)
  — count and regions recorded below once measured. Pointed at as the recipe for a centroid table;
  EventFinds keeps **one** table of its own (trap 6.10: two copies already disagree by ~2 km).

**Stage 2 issued** — the form is the NOW section of `TODO.md`. Sixteen of RapidForge's lines plus
one of this session's (#17, the repo). Three genuinely open (#1, #3, #13). One consequence made
explicit rather than hidden: under #13(c) there is no database, so the "owner promote form" in #4's
default cannot exist in v1 — the source file is the truth and curation is edit → export → deploy.

Files at the end of this entry: `CHATLOG.md`, `TODO.md`, `PLAYBOOK_DELTA.md`. No git yet.

*Geocoder measured:* dict `C` at `vending_circuit_geocode.py:11-142` plus dated interior-fill
blocks after it — ~120 city → (lat, lng) entries: Missouri statewide (four sweep batches), then
corridor and interior fills across IL, IN, KY, TN, AR, KS, OK, IA, NE. Adequate as the *recipe* for a
Midwest-centred v1; EventFinds builds its own single table from the towns its own events name, and
an unknown town fails the export (7.6).

## 2026-08-30 — Stage 2 answered. The form is closed; the build is unblocked

**Lance, verbatim:** *"1. Standalone 3. I, Lance McCarter, own everything I can legally own as well
as assume ownership of any unknown owned items 13. C for now"*

No other number was named, and the form's contract was "reply only with the numbers that are
wrong" — so **all fourteen defaults stand**, including #17 (repo `lazrexmc/eventfinds`, private).

**Decisions now frozen for v1:**
1. **Standalone product.** `glizzness.com/festivals` is untouched; nothing shared — no key, project,
   data, or domain. Whether Glizzness later points at EventFinds is a second decision after the
   2026-09-10 demo.
3. **Ownership:** Lance owns the 415 events and their contacts as far as legally ownable. This makes
   a later import *his to make*; it does not change #2 (start empty, no contacts) or #7 (no contact
   columns public) — those are consent and fork decisions, not ownership ones.
13. **Static JSON publication, $0** — "for now." The source file is the truth; the pipeline exports
    `site/data/*.json`; the finder page reads files. No Supabase project. This also answers Build
    001's open interruption (same question, same answer): a recorded "for now" — RapidForge closes
    the entry with it. Consequence accepted: no promote form in v1; curation is edit → export →
    deploy.

Interruptions this build so far: **0** (the form is the scheduled touchpoint, not an interruption).
Next: spec (frozen decisions + contracts) → plan with acceptance criteria → build → review → deploy.

## 2026-08-30 — Reconnect after the PC restart; plan written; execution begins

Peers restarted and renamed (`rapidforge-79`, `glizzness-f1`; this session `eventfinds-12`).
Lance: *"connect to all open peer sessions"* — done; both confirmed their state matches this
repo line for line. RapidForge kept full context; its `23d01d1` closed Build 001's interruption
with Lance's #13 answer. Two messages addressed to RapidForge were misrouted here (Glizzness
remediation COMPLETE, probe 30/0/0/0; VisibleGov's seven-round summary, HEAD `89d9fce`) — both
acknowledged and pointed at `rapidforge-79`; nothing in either changes Build 002. Glizzness noted
the 22:24Z crawler run I cited predates its Phase 5 (honest per-source table starts at `7024e7a`) —
correction accepted. It offered `tools/verify_deploy.py`; taken verbatim with attribution as
`pipeline/verify_deploy.py`, with `ORIGIN`, `MARKERS`, `HEADER_MARKERS` changed for this site —
EventFinds becomes that instrument's second consumer.

**Plan:** `docs/superpowers/plans/2026-08-30-eventfinds-v1.md` — twelve tasks with the code in
them, TDD per task, one commit per task, gates G1–G9 mapped to `event-finder` §7. Execution is
subagent-driven with per-task review; the only stop is a failing gate or the single credentialed
step at the end (Cloudflare Pages connect).

## 2026-08-29 - Browser verification (three states)

Server: started with `python -u pipeline/serve_local.py` (run_in_background, unbuffered so the
startup log could be captured before the first request). Log line, verbatim: `[23:39:01] serving 4
security header(s) from site/_headers on every response`. Confirmed reachable with
`curl -sI http://127.0.0.1:8765/` (200 OK). Stopped at the end of the task (TaskStop); a `curl`
against the port afterward did not connect, confirming shutdown.

**State 1, empty (the committed publication, event_count 0).** Navigated to
`http://127.0.0.1:8765/`. `browser_snapshot`: header text `0 events - verified as of -` (the app's
own separators are a middle dot and an em dash: `0 events · verified as of —`, matching
the brief's expected string exactly); `#status` text `No events listed yet.`. `browser_evaluate`
on the live DOM: `errorBoxHidden: true`, `statusHidden: false`. `browser_console_messages`
(level info): `Total messages: 1 (Errors: 1, Warnings: 0)` - the one error was
`Failed to load resource: the server responded with a status of 404 (File not found) @
http://127.0.0.1:8765/favicon.ico:0`, the ledgered cosmetic favicon 404; no other console messages,
so zero non-favicon console errors. `browser_network_request` on request 1 (`GET /`),
response-headers part, included `content-security-policy: default-src 'self'; img-src 'self' data:
https://tile.openstreetmap.org https://*.tile.openstreetmap.org; script-src 'self'; style-src
'self'; connect-src 'self'; base-uri 'none'; object-src 'none'; form-action 'self'; frame-ancestors
'none'` - the CSP header is present on the `/` response. Matches the brief.

**State 2, loaded (fixture export).** Ran
`python pipeline/export.py --csv pipeline/fixtures/negative.csv --places pipeline/fixtures/places.csv --out site/data`;
output verbatim: `exported 1 event(s) -> site/data  (as_of=2026-08-30, types=1)`. Reloaded.
Header text: `1 event - verified as of 2026-08-30` (the app's own separator is a middle dot,
not a hyphen: `1 event · verified as of 2026-08-30`). One marker rendered on the map; clicked it.
Drawer: heading `Published Fest`, type badge text `festival`, definition list `When` =
`2026-09-12 to 2026-09-13`, `Distance from Columbia, MO` = `0 mi` (zero shown, not hidden or
blank - trap 6.2), `Last verified` = `2026-08-30`, a link `Event page` to `https://example.com/p`
with `rel="noopener"` and `target="_blank"` (checked via `browser_evaluate` reading the anchor's
`rel` attribute directly). `browser_evaluate` over `document.body.innerText` found no match for
`/contact/i`, no `@`, and no phone-number pattern anywhere on the page. Opened `List`: side panel
read `1 in view`. Set Month to `Oct`: header crumb changed to `0 events`, list panel showed
`0 in view` and `No events in this view. Pan or zoom out to see more.`. Clicked `Reset`: crumb
back to `1 event`, list back to `1 in view`. Opened the `All types` panel: exactly one checkbox,
labeled `Festival`, checked. `browser_console_messages` (level info, since the reload navigation):
`Total messages: 0 (Errors: 0, Warnings: 0)` - zero console errors, favicon included (not
re-requested on reload). Matches the brief.

**State 3, error (a file removed).** Ran `mv site/data/meta.json site/data/meta.json.bak`.
Reloaded. `browser_snapshot` showed an `alert` region with `strong` text
`This page could not load its data.` and paragraph text
`Failed to load /data/meta.json — HTTP 404 File not found. Nothing on this page is rendered
from a failed fetch.` - the brief's expected substring `Failed to load /data/meta.json - HTTP 404`
appears verbatim at the start of that text. `browser_evaluate`: `errorBoxHidden: false`,
`statusHidden: true`, and a query for `.leaflet-marker-icon, .marker-cluster` returned 0 elements
(no dots on the map). `browser_console_messages` (level info): `Total messages: 2
(Errors: 2, Warnings: 0)`:
`Failed to load resource: the server responded with a status of 404 (File not found) @
http://127.0.0.1:8765/data/meta.json:0` and
`FetchError: fetch of /data/meta.json failed: HTTP 404 File not found` (stack: `fetchJson` at
`js/data.js:27:11`, `init` at `js/app.js:212:18`). Restored with
`mv site/data/meta.json.bak site/data/meta.json`. Matches the brief.

**Restore and gates.** `git checkout -- site/data` reverted the fixture export back to the
committed empty publication. `python pipeline/checks.py` printed all nine gates as `PASS`
(G1-G9) and ended with `ALL GATES PASS: 0 gate(s) failed`. `git status --short` was empty after
also removing an untracked `.playwright-mcp/` directory that the MCP browser tooling had written
during this session (snapshot and console-log files, not part of the repository and not referenced
by any code). The background server was stopped before this check ran.

## 2026-08-29 - Build 002 v1 built; awaiting the Pages connect

Task 12 (README, live-state documents, a handful of ruled fixes, final checks and push) run per
the controller's supplement ordering: brief Step 1 (README, with the supplement's items 4 and 7
folded in) -> supplement items 1, 2, 3, 5, 6 -> brief Step 3 (TODO/CHATLOG) -> brief Step 4 (final
checks and push, with `npm test` added). Brief Step 2 (whole-branch adversarial review) and Step 5
(the Pages handoff message) were both skipped on the controller's ruling - the review runs after
this task and the handoff is the controller's message, not mine.

**Created `README.md`** from the brief's template with the supplement's items folded in: the local
preview line uses `python -u pipeline/serve_local.py` (stdout is block-buffered when backgrounded,
so without `-u` the startup log appears late); a `## Live` section states the three-rung ladder -
Built (rung one); Cloudflare Pages not yet connected; verification recorded here once it runs; and
the Tests section shows `npm test` first with `node --test "tests/js/**/*.test.mjs"` given as the
literal equivalent, never the bare-directory form.

**Fixes (supplement section A), each verified after applying:**
1. `package.json`: `"test": "node --test tests/js"` failed under Node 24.11.1 with
   `Cannot find module 'F:\EventFinds\tests\js'` (a bare directory is no longer walked as a test
   root; Node resolves it as a module specifier). Changed to
   `"test": "node --test \"tests/js/**/*.test.mjs\""`. `npm test` now passes, 9 tests.
2. `site/index.html`: added `<link rel="icon" href="data:," />` in `<head>` right after the
   viewport meta, so the browser stops requesting `/favicon.ico` (previously a cosmetic 404 seen
   in the Task 11 console log). No other change to the file.
3. `.gitignore`: appended `/.playwright-mcp/` (anchored, matching every existing entry) - the
   browser-tool MCP had written untracked artifacts under that path during Task 11.
4. Plain ASCII punctuation applied to `README.md`, `TODO.md`, `PLAYBOOK_DELTA.md`: em dashes, the
   section sign, arrows and the RESUME heading's rewind emoji replaced with hyphens, "section N",
   `->`, and a bare `## RESUME HERE`. `grep -nP "[^\x00-\x7F]" README.md TODO.md PLAYBOOK_DELTA.md`
   prints nothing.
5. Dates: every `2026-08-30` in `TODO.md` and `PLAYBOOK_DELTA.md` changed to `2026-08-29` (the
   machine's local date; the earlier date was UTC). TODO's RESUME block now reads
   "Live state as of 2026-08-29" and states it outranks every other document in the repo.

**TODO.md RESUME block** rewritten to the live state: v1 BUILT (rung one); all gates green
(`python -m pytest -q` 50 tests, `npm test` 9 tests, `python pipeline/checks.py` ALL GATES PASS
G1-G9); waiting on the one credentialed step - Lance connects Cloudflare Pages (project
`eventfinds`, repo `lazrexmc/eventfinds`, production branch `master` after the merge, root
directory `site`, build command empty, output directory empty); after that,
`python pipeline/verify_deploy.py` must print ALL DEPLOYED (rung two). Build queue items through
"Build" ticked done; the review/deploy and dogfood/deposit items left open since Pages is not yet
connected and the review is the controller's to run.

**PLAYBOOK_DELTA.md**: added Lesson 1 (verify_deploy's `read_bytes()` crashed on a marker file
absent from the repo instead of reporting a verdict; fixed with a `local_bytes()` helper and a
NO-LOCAL verdict - already committed in Task 6, documented here for the first time) and Lesson 2
(`node --test <directory>` resolves as a module specifier on Node 24 instead of walking the
directory; use a quoted glob). The existing memory-index lesson kept as Lesson 3 under the same
numbering, text otherwise unchanged.

**Final checks, all green:** `python -m pytest -q` (50 passed), `npm test` (9 passed),
`python pipeline/checks.py` (ALL GATES PASS, G1-G9), `grep -nP "[^\x00-\x7F]" pipeline/*.py
tests/*.py` (nothing), `grep -n -i -E "glizzness|midwest event finder" -r site pipeline tests data
README.md` (nothing).

Two commits follow: one for the fixes (`package.json`, `site/index.html`, `.gitignore`), one for
the documents (`README.md`, `TODO.md`, `PLAYBOOK_DELTA.md`, `CHATLOG.md`). Branch `v1` pushed to
`origin` (not previously pushed). `verify_deploy.py` was not run against the network, per the
supplement.
