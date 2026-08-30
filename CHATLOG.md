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

---

## 2026-08-30 - Final fix wave: eight Important findings plus three folded-in minors

Controller-ruled fixes from the whole-branch adversarial review, worked item by item from
`.superpowers/sdd/2026-08-30-eventfinds-v1/final-fix-brief.md` against branch `v1` at 777f64c.
Every ruling in the brief was followed as written; nothing beyond it was changed.

**F1** - `site/js/app.js`: a Leaflet load failure used to throw at module top level, before
`init()`'s try ever ran, so the page rendered a blank map with no error box and no console error.
Moved the map construction (`L`, `map`, the tile layer, the cluster group, `dotIcon`) and the DOM
event wiring (drawer close, list-toggle, list-panel close, the list-row click handler, and
`map.on("moveend", ...)`) into a new `boot()` function, called as the first statement inside
`init()`'s try, before either fetch. `boot()` opens with a check that throws a named `Error` when
`window.L` or `window.L.markerClusterGroup` is missing. `describeError`'s existing fallthrough to
`err.message` needed no change. Verified in a browser (Playwright, via `python -u
pipeline/serve_local.py`): the normal empty state shows "0 events - verified as of -" with the map
rendered and zero console errors; after renaming `site/assets/vendor/leaflet/leaflet.js` and
reloading, the error box appeared reading "This page could not load its data." / "the map library
did not load (assets/vendor/leaflet)" (console showed the expected 404, the vendored
markercluster.js's own `ReferenceError: L is not defined`, and our thrown Error logged by
`renderFatal`'s `console.error(err)` - all expected, not a regression). The file was renamed back
and `git status --short` showed no diff on it afterward. Covering: `node --check site/js/app.js`;
gate G6.

**F2** - `pipeline/verify_deploy.py`: the static `MARKERS` list named 8 of the 19 files actually
under `site/`, so a stale file drifting at the origin (e.g. a CSS or vendored JS file nobody
remembered to add to the list) would never be caught. Replaced `MARKERS` with a `markers(site_dir)`
function that walks `site_dir` recursively, skips names in a new `SKIP = {"_headers"}` constant,
and returns `(local_rel, url_path)` pairs sorted by relative path; `local_rel` is always
`"site/" + relposix` regardless of the directory's actual name, `index.html` maps to `/`, every
other file maps to `/<relpath>`. `main()` now calls `markers(ROOT / "site")`. `compare()`,
`fetch()`, `local_bytes()`, `HEADER_MARKERS` unchanged. Replaced
`test_markers_cover_the_publication_and_the_page` in `tests/test_verify_deploy.py` with a new test
against a temp tree (four files including `_headers`; asserts the exact three-item sorted list with
`_headers` absent) plus an updated version of the same-named test against the real `site/` that
checks for `site/data/meta.json`, `site/js/app.js`, and
`site/assets/vendor/leaflet/leaflet.markercluster.js`. Covering: `python -m pytest -q
tests/test_verify_deploy.py` (4 passed).

**F3** - No `.gitattributes`: a fresh clone with `core.autocrlf=true` would check out CRLF line
endings, and gate G3 (byte comparison of a fresh export against the committed `site/data/*.json`)
would then fail spuriously. Added `.gitattributes` at the root with `* text=auto eol=lf` and
`*.png binary`, then ran `git add --renormalize .`. The brief expected this to touch nothing but
the new file; in fact one file, `site/assets/vendor/leaflet/leaflet.css` (a vendored third-party
file), was still CRLF and got renormalized to LF by that command - confirmed by diff to be a pure
line-ending change with no content difference. Every other tracked file was already LF, so nothing
else changed. `git status --short` after renormalizing showed exactly that one modified file plus
the new `.gitattributes`.

**F4** - Gate G5 only proved `site/data/events.json` was not gitignored, i.e. that it *could* be
committed, not that it *was* committed together with the CSV it was exported from. Rewrote
`g5_publication_committed()` in `pipeline/checks.py` as two checks: (a) `git check-ignore -q
site/data/events.json` from the repo root - returncode 0 fails naming it "gitignored", returncode 1
passes, any other returncode fails naming the returncode; (b) reads `data/events.csv` and
`site/data/meta.json` at HEAD via `git show`, fails naming whichever path is absent, then compares
the CSV's sha256 to `meta.json`'s `source_sha256`, failing "the last commit's publication does not
match its source CSV - commit data/ and site/data/ together" on a mismatch. Pass message: "not
ignored; HEAD's meta.source_sha256 matches HEAD's data/events.csv". Added
`test_g5_publication_committed_on_this_repo` asserting `checks.g5_publication_committed()[0] is
True` on this repo. Making that test pass under pytest on this Windows machine required adding
`stdin=subprocess.DEVNULL` to all three `subprocess.run(...)` calls in `g5_publication_committed`:
without it, `git ...` spawned from inside a pytest-captured test raised `OSError: [WinError 6] The
handle is invalid` while `subprocess.Popen` tried to duplicate pytest's (invalid, under capture)
stdin handle for inheritance - reproduced with and without `-s`, fixed by not inheriting stdin at
all. Updated the G6-line docstring reference to G5. Covering: `python -m pytest -q
tests/test_checks.py` (was 4, now 7 passed); `python pipeline/checks.py` (G5 PASS).

**F5** - `pipeline/assign_ids.py` `main()` let a `ValidationError` from a bad CSV header propagate
as a raw traceback. Wrapped the `assign_ids(...)` call in `try/except (ValidationError, OSError) as
e: print("ERROR: %s" % e); return 1`, importing `ValidationError` from `model`. Added
`test_bad_header_is_an_error_line` in `tests/test_assign_ids.py`: a CSV with header `id,name` makes
`main(["--csv", str(p)])` return 1 with stdout starting `ERROR:`. Covering: `python -m pytest -q
tests/test_assign_ids.py` (3 passed).

**F6** - `pipeline/export.py`: `write_publication(...)` was called outside `main()`'s try block, and
wrote `events.json` then `meta.json` directly with `Path.write_text`, so a failure partway through
(e.g. disk full on the second file) could leave a new events list beside a stale meta, or a
half-written file. Moved the `write_publication(...)` call inside the try (the existing `except
(..., OSError)` already covers it). `write_publication` now writes each file to `<name>.tmp` in the
same directory via a new `_dump_atomic()` helper and `os.replace()`s it into place, meta.json FIRST
then events.json, per the ruling. Added `test_write_publication_leaves_no_tmp_files` asserting only
`events.json` and `meta.json` exist in the output directory afterward. Covering: `python -m pytest
-q tests/test_export.py` (11 passed).

**F7** - The drawer rendered a "Featured" badge, contradicting frozen decision 12 ("`featured`
boolean column reserved and exported, not rendered specially in v1"). Removed the `if (e.featured
=== true) badges.push(badge("Featured", "b-gold"));` line from `openDrawer` in `site/js/app.js`;
badges are now type and one-time only. Removed the now-dead `.b-gold` CSS rule from
`site/css/app.css` (the `--gold` custom property itself was left, since the brief named only the
rule). `featured` remains untouched in the export contract. Amended
`docs/superpowers/specs/2026-08-30-eventfinds-v1-design.md`: section 7's drawer bullet now reads
"two badges max (type, one-time); `featured` is exported but not rendered (decision 12)"; section
2's decision 15 now reads "Name EventFinds; no reference-project brand or the string Midwest Event
Finder in the product surface (`site/`, `pipeline/`, `data/`, `README.md`); decision records may
name the reference project" (per the brief, this is a decision record naming the reference project
by its old working phrase, not the product surface, so the phrase is allowed here). Covering:
`node --test "tests/js/**/*.test.mjs"`; gate G6; `grep -c b-gold site/css/app.css` (0).

**F8** - A published row with no dates and no months is upcoming forever and matches every month
filter - this was already the coded behaviour (`predicates.isUpcoming` returns `true` for exactly
this shape) but was undocumented and looked like a bug. Ruling: keep it (deliberate, for year-round
events) and document it. Amended spec section 7's Upcoming bullet with: "no date, no months ->
always shown and matches every month filter (a year-round or undated event); the curator opts into
this by leaving both blank." Added a sentence to README.md workflow step 1: "Leave both dates and
months blank only for a year-round event: such a row is always shown and appears under every month
filter." Added a node test `monthless undated row is intentionally shown under every month` to
`tests/js/predicates.test.mjs` asserting `passesFilter` on a dateless, monthless row returns true
for both month "1" and month "12". Covering: `npm test` (was 9, now 10 passed).

**M1** - `README.md`'s Tests section described `npm test` as "pipeline's page layer: predicates and
fetch," backwards (predicates and fetch are the page's, not the pipeline's). Changed to "the page's
predicates and fetch layer".

**M2** - Gate G6 only scanned `site/js/*.js` for the publish-gate vocabulary; an inline `<script>`
or an `onclick=`-style handler in `site/index.html` would be a second, unaudited place for page
logic to live and gate G6 would never see it. Extended `g6_no_gate_in_js` to
`g6_no_gate_in_js(site_js_dir=None, index_html=None)` (defaults from `config`); it now collects
`sorted(site_js_dir.rglob("*.js"))` once, then scans `index.html` line by line for a `<script>` tag
with no `src=` attribute and for an inline `on[a-z]+=` handler attribute, failing and naming the
line for either. Added `test_g6_flags_inline_handler_in_index_html` (a temp `index.html` with
`<button onclick="x()">` fails) and `test_g6_passes_a_clean_index_html` (a clean temp `index.html`
with only a `src=`-bearing `<script>` passes) to `tests/test_checks.py`.

**M3** - `site/js/app.js` constructed the map with a second literal copy of the HOME coordinates
(`[38.9517, -92.3341]`, also in `pipeline/config.py`). `boot()` now creates the map with
`setView([0, 0], 2)`; `init()` already re-centers on `META.home` after the data loads, so the real
HOME coordinate now lives in exactly one place.

**Final checks, all green:** `python -m pytest -q` (56 passed, up from 50); `npm test` (10 passed,
up from 9); `python pipeline/checks.py` (ALL GATES PASS, G1-G9); `node --check site/js/app.js`
(no output = success); `grep -nP "[^\x00-\x7F]" pipeline/*.py tests/*.py README.md TODO.md
PLAYBOOK_DELTA.md` (empty); `grep -rn -i -E "glizzness|midwest event finder" README.md site
pipeline data tests` (empty). `git status --short` clean after committing.

Full per-finding detail (file:line, covering test, command output) is in
`.superpowers/sdd/2026-08-30-eventfinds-v1/final-fix-report.md`.

## 2026-08-30 00:40 CDT - Build 002 v1 complete on the branch; rulings made on the owner's behalf

The subagent-driven build ran twelve plan tasks with a review gate after each (six fix rounds in total,
every one re-reviewed), then a whole-branch adversarial review (0 Critical, 8 Important, all fixed in one
wave and re-verified). Final state: pytest 56, node tests 10, nine gates ALL PASS, page verified in a browser
in three states plus the script-load failure state. The branch merges to master fast-forward next; the one
credentialed step (Cloudflare Pages connect) is batched for the morning.

Every ruling the controller made without the owner, verbatim from the build ledger, so nothing was decided
in secret (the ledger itself is scratch and is deleted after this entry):

- - Ruling: work on branch `v1` in F:\EventFinds rather than a separate worktree - the plan's commands,
- - Ruling: Task 10 status text "No events published yet." -> "No events listed yet." - the plan's own
- - Ruling: Task 6 test fixture local `<html></html>` -> `<html>\n</html>` - compare() collapses
- - Ruling: Task 10 drop unused `isUpcoming` import - YAGNI; if wrong, one import is missing (no,
- Ruling: reviewer is right; spec's controlled-failure rule outranks the plan's line placement; fix = move parse into try + one test - costs one line if wrong.
- Ruling: fix - add local_bytes() returning None, verdict NO-LOCAL (fails the run cleanly); compare()/fetch() untouched - costs one helper if wrong.
- Task 7: Ruling: plan's passesFilter test fixture lacked lat/lng while the mandated implementation hides null coords; implementer added lat/lng to the fixture - correct, the spec's null-coords rule outranks the fixture text; costs nothing if wrong.
- Ruling: plan defect, not app.js; fix in Task 12: package.json script -> node --test "tests/js/**/*.test.mjs", README/plan wording likewise - costs one line if wrong.
- Task 11: review: 1 Important: State 2 header quoted with a hyphen where the page renders a middle dot, undisclosed (State 1 disclosed it). Ruling: fix the sentence to the exact rendered string - the verbatim-quote rule (playbook: copy, never retype) is binding; costs one sentence if wrong.
- Ruling: CLAUDE.md is NOT created on a peer's relay (PROJECT_STANDARD s4.2: a rule file is configuration, added on the owner's word in the project's own session); a draft goes in the morning handoff for Lance to approve. Costs one file's delay if wrong.
- Ruling: Task 12 scope widened by exactly these items (all defects or owner-relayed rules, no new features): package.json test script glob; favicon data: link; /.playwright-mcp/ in .gitignore; TODO/PLAYBOOK_DELTA ASCII sweep + local date re-stamp (2026-08-29); README ## Live section on the three-rung ladder; serve_local -u note. CHATLOG history left as written (standard rule 3/15).
- Task 12: Ruling: the reference project's name in TODO.md's questionnaire record is a factual decision record, not a product string; spec #15 binds site/, pipeline/, data/, README - allowed in TODO/CHATLOG/spec/plan. Costs nothing if wrong (a doc edit).
- Task 12: review: 1 Important claimed (50 vs 49 tests). Ruling: REFUTED - `python -m pytest -q` collects and passes 50 (test_model.py = 26: 11 + 15 parametrised; the reviewer counted 14). Documents stand. Costs nothing if wrong (a number in a doc).
- Ruling F1: fix - Leaflet construction inside init()'s try with an explicit library check (a script-load failure must reach the error box).
- Ruling F2: fix - verify_deploy walks site/ (spec s9 says every file); compare/fetch untouched.
- Ruling F3: fix - .gitattributes eol=lf (G3 would fail spuriously on autocrlf clones).
- Ruling F4: fix, NOT as proposed - reviewer's `git diff --quiet HEAD` breaks export-then-commit; instead G5 verifies HEAD's own pair (sha256(HEAD:data/events.csv) == HEAD:site/data/meta.json.source_sha256) and treats check-ignore rc>1 as FAIL. Costs a gate rewrite if wrong.
- Ruling F5: fix - assign_ids controlled failure (same principle as Task 4).
- Ruling F6: fix - write_publication inside try; tmp+os.replace, meta first.
- Ruling F7: frozen decision 12 wins over spec s7 badge list - Featured badge removed, spec s7 amended; decision 15 wording narrowed to the product surface (matches the Task 12 ruling). Costs a badge if wrong.
- Ruling F8: behaviour kept (year-round events), stated in spec s7 + README + one node test.
- Ruling: leaflet.css CRLF->LF renormalisation accepted (vendored file; compare() ignores line endings; no byte of code changed). Ruling: stdin=DEVNULL on G5 git calls accepted (Windows pytest stdin-handle quirk).
- Ruling: merge v1 -> master fast-forward and push master - Lance's standing convention is continuous push to his own private repo, his overnight instruction was to run through to the credentialed step, and Pages builds from master; costs a revert if wrong.

## 2026-08-30 00:57 CDT - RapidForge confirms the Build 002 deposits landed

RapidForge: the two verify_deploy findings are module traps 6.6 and 6.7 credited to EventFinds, with the canonical reference file named and its owner session messaged; the 8-of-19 finding went into MASTER_PLAYBOOK as a general rule (derive what to verify from the thing itself; a hand-maintained list rots with it); Build 003 (PostKit) was written with the walk and the NO-LOCAL verdict from birth. The node --test trap, the HEAD-aware source hash, and .gitattributes eol=lf landed too. Interruptions across three builds: 1, 0, 0. One lesson captured to the inbox, not chased: probe a source with one real request before designing around it. Rung two still waits on the Pages connect.

## 2026-08-30 01:51 CDT - Registry audit taken: module text widened, promotion held until 7.8

RapidForge landed the audit at its a4695a5: the assign_ids row now says a blank id gets a UUID4 and is never regenerated (identity naming is the slug's job); the export row carries the one-gate property; event-finder section 7 is variant-aware (7.1 names the SQL and exporter forms, 7.2 says invisible at the published surface - endpoint or exported file, 7.3 covers select list / key list / asserting gate, 7.4 database-variant only, 7.9 N/A for a standalone consumer and explicitly not passed); a new section 7b records which of this build's checks ran, in which form, which are N/A, and that 7.8 is pending. Promotion to proven is HELD until verify_deploy runs green against the origin. The rule that came out of it, now in the master playbook: when evidence satisfies the property but not the wording, fix the text, not the evidence - an acceptance check that names a mechanism instead of a property fails every consumer that differs from the reference. RapidForge also confirmed the "section 7 records your checks" line in its earlier message was written from intention, not from the file; noted here because the trail should know which claims were checked.

## 2026-08-30 06:23 CDT - Shutdown prep

Machine powering off. RESUME block rewritten for a cold session (rung one, merged, the Pages connect spelled out, promotion held at RapidForge until 7.8, section 7b). Heartbeats 01:45-05:45 CDT all found the origin unresolved (21 markers HTTP 0). Checkers run, committed, pushed.

## 2026-08-30 13:45 CDT - Peer mesh completed on Lance's instruction

Lance (via rapidforge-07): "tell all peers to connect to all open peers so all VS code sessions are linked." This session is now eventfinds-b8. Announced to all nine live peers in one line each (rapidforge-07, Glizness, equalshares-ef, visiblegov-e4, linkedump-42, league-f5, postkit-30, duarte-izer-72, inoculated-by-the-phoenix-ec); state given as: rung one, merged at add60c4, blocked only on the Cloudflare Pages connect, event-finder promotion held until 7.8. Queued for EqualShares only: tmp+os.replace meta-first writes, and page construction inside the init try so a missing vendored script reaches the error box. Replies so far ask nothing. Glizzness corrections recorded: the marker-coverage defect was 8 of 19 here and 6 of 43 there, both fixed (its canonical verify_deploy sha 0ffcee70); its filter entry point is `const applyFilters = () => render(true)` (app.js:138), which a `function name(` grep misses - a mechanical "absent" is a candidate, not a finding, until the raw string is grepped; its Task 4.3 stays parked until after 2026-09-10. EqualShares now runs its local server on ROLLCALL_PORT because this repo holds 8765.

## 2026-08-30 13:46 CDT - VisibleGov caveats checked against this repo

visiblegov-e4 (clean at b3bcb84, 2,792/0) sent two lessons behind the pointers this build took. One-predicate: already structural here - gate G6 fails if the gate vocabulary or an inline handler reappears in the page, and tests/test_checks.py plants each form and asserts the guard fires; no change. Freshness: the header reads max(last_verified), which is the newest row's date, not a claim about every row; captured to the inbox as a display candidate (min and max, or a stale count), not chased. last-built is not shown as freshness by design.

## 2026-08-30 14:16 CDT - CLAUDE.md created on Lance's approval

RapidForge relayed Lance's instruction ("rapidforge needs to send the instructions to update the claude.md
files and I'll approve them at each session if that's what we need to do") and the verify_standard row:
CLAUDE.md, AUDIT_LOG.md, REBUILD.md and a claim checker absent. A draft was written in this session and
shown to Lance; he approved it here ("rapidforge will request an update to the claude.md file, I approve"),
which is the owner's word in his own session, not a peer relay. The file is the draft verbatim: read order,
ten locked standing rules, the honest three-rung status with the Cloudflare Pages connect parameters spelled
out and the held event-finder promotion, a pointer to F:\RapidForge\docs\PROJECT_STANDARD.md rather than a
copy, and five declared deviations (checks.py IS the claim checker; no RLS probe or migration ledger with no
database; AUDIT_LOG.md and REBUILD.md owed at the next touch per the standard's own rule; no PII guard
because the closed header admits no contact data). Gates re-run after the file landed.

## 2026-08-30 14:28 CDT - Consent check on the rules (Lance, via RapidForge)

Lance: "ask each session if the session agrees with the rules for it's session then check if each
projects rules can exist with the overall Lazrex Enterprise of softwares rules", corrected an hour
later with "the smaller bodies can override rules when needed but usually when owner approval states
so... We don't need our small projects going no where because big brother doesn't understand the need."
PROJECT_STANDARD section 3b (3e8faa7) supplies the test: a rule is federal only if RapidForge needs it
uniform to work across projects; everything else is local; when in doubt the project ships.

Answered, with the facts checked in this repo first rather than recalled:

(1) Agree with all ten locked rules, with three caveats reported rather than hidden. Stdlib-only is the
one this build would break first when v2 adds an intake, and that will be declared if it happens.
Rule 5 is wrong as written - it bars a data row outright while the owner owns the reference data and
the questionnaire left a re-verified import to him; reworded on the next touch (inbox). Two of the ten
have never been tested (no-auto-publish, nothing-shared) and are claims rather than rules until an
intake or an import exists. Rule 9 (plain ASCII) is the only one of the ten with no gate behind it, so
it is the one most likely to break by accident; a tenth gate is in the inbox.

(2) One real conflict with the standard: rule 2 says a counted claim is derived or deleted, and this
repo types "56 pytest + 10 node tests, nine gates" (CLAUDE.md:44) and "21 markers" (TODO.md:24).
Proposed resolution offered to the registry: derivation OR the sentence naming the command that
produces the number. Recorded as a conflict with two answers rather than resolved unilaterally.
Recorded as NOT a conflict: rule 15 against the rendered page - site/js and index.html hold zero
non-ASCII bytes; the middle dot and em dash the page shows are six \u escapes, so the rule
governs documents and prose, not rendered output.

(3) Offered as federal: "failure is not emptiness" (verb: control - an instrument can only measure a
project whose states it can tell apart) and "one decision, one place, with a structural guard that
fails when a copy returns" (verb: build - VisibleGov derived the same rule independently, and its
sharp half is that a test asserting two copies agree is theatre). Kept local: the closed header, the
contact-column ban, no-auto-publish, stdlib-only, nothing-shared - a project with no publish surface
would carry them dead.

(4) No override requested. Nothing in the standard blocks this build.

A note on method, since it cost a minute here: the first attempt wrote this entry through a heredoc
and Python read the backslash-u in its own prose as an escape. The playbook rule already covers it -
write the patch to a file and run the file - and it applies to prose about escapes, not just code.

## 2026-08-30 14:37 CDT - Round 2: which standard rule has never checked this project

Registry (4784a50): both federal candidates from this session were adopted - F5 failure is not
emptiness (verb control, jointly with PostKit, which added that a declared state must reach the
interface) and F6 one decision one place WITH a structural guard (verb build, folded into rule 11).
This session's rule-2 wording was adopted verbatim after four of eight sessions hit the same conflict
in one evening, and verify_standard gained a third state, `dec`, for an absence the rule file declares.
Applied here at once: CLAUDE.md's status line and TODO's origin-check line now name the command that
produces every number in the same sentence. TODO's RESUME already did.

PostKit's round-2 question, answered honestly - which existing standard rule has never once been
checked against this project, given that the sharper half of the federal test is deletion:

ONE CANDIDATE FOR DEMOTION, rule 12, the pre-work anti-repeat protocol (check the five named places -
the script inventory, the trail, the TODO, the registry, the last session's handoff - and report what
you found). It has never run as a protocol here and on day one it could not have: this repo was an
empty directory, so four of its five places did not exist. What served its purpose was a machine-wide
grep for prior art, which found the reference project's finder and its crawler and is why nothing was
rebuilt. The rule is written for a mature repo with accumulated scripts; for a greenfield build it is
vacuous, and a rule satisfied vacuously teaches a session nothing. Proposal: scope it to repos with
prior work, or restate it as its purpose - check what already exists, in the places that exist here,
before generating anything.

THREE THAT ARE UNTESTED BUT SHOULD NOT BE DELETED, because untested-by-me is not evidence against a
rule, and this repo is a day old:
- Rule 8, an expected-failures list with an expiry condition. Never had one - and this build hit
  exactly its case: gates G6 and G9 were red BY DESIGN for four tasks, because the site they check did
  not exist yet. That was handled in a commit subject and a dispatch brief rather than a list with an
  expiry, which is the ad-hoc form the rule exists to replace. So rule 8 has never checked this
  project, and it should have. That is evidence for the rule, not against it.
- Rule 4, a retraction quotes what it retracts. No claim published from this repo has ever needed
  retracting. The nearest thing was a reviewer catching a hyphen typed where the page renders a middle
  dot, fixed before the document was trusted - a correction, not a retraction.
- Rule 3's correction mechanism specifically (strikethrough in place, original bytes intact, a dated
  entry quoting the false sentence). The append-only half is exercised every session; the strikethrough
  half never has been.

ONE HALF-RULE THAT HAS NEVER BEEN CHECKED AND COULD BE: rule 11's second clause, "and the pointers are
checked". This repo points at F:\RapidForge\docs\PROJECT_STANDARD.md and at modules/event-finder.md
from CLAUDE.md, and at the reference by path from PLAYBOOK_DELTA. Nothing here fails if any of them
moves. The first clause is checked constantly; the second is decoration until an instrument reads it.
Also worth stating plainly: this repo holds one deliberate COPY, pipeline/verify_deploy.py, attributed
in its docstring - a code module is a copy by design, which is the edge the rule should name.

## 2026-08-30 14:40 CDT - Session closing

Lance closed this session. Final state: v1 built (rung one) and merged to master, clean and in sync at
11cf795 before this entry; `python -m pytest -q` 56, `npm test` 10, `python pipeline/checks.py` ALL GATES
PASS at that commit. Blocked on one owner step, the Cloudflare Pages connect, whose parameters are in
CLAUDE.md and in the RESUME block. The hourly origin check was a session-only timer and dies with this
session, so the RESUME now says a later session must run verify_deploy itself rather than expecting a
watcher. Open and carried in the inbox, none of it blocking: a tenth gate for plain ASCII in documents,
the rule 5 rewording (an owner-approved import must not require breaking the rule), narrowing the
claim-checker deviation so it does not overstate what the gates cover, and the freshness display showing
only the newest verification date. RapidForge notified.
