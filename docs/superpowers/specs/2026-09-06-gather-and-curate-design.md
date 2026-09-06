# EventFinds v2 intake - the gather-and-curate layer (design, 2026-09-06)

*Design record, not a plan and not a build. Written when the decisions were made rather than when
the code is written, so that the reasoning survives the session that had it. The v1 spec
(`2026-08-30-eventfinds-v1-design.md`) is frozen and describes a system with no crawler; this
document is what would change that, and nothing here is implemented.*

*Moved out of `TODO.md` on 2026-09-06: it is a design record, and a live-state document should say
what is next, not carry the argument for it.*

---

Lance, 2026-09-06: *"continue working with glizzness as needed, you have full permission, you have
the design intent and ending goal."* He had stopped the Glizzness session mid-design on a research
crawler with *"this is what the EventFinds repo is, back up and analyze before I duplicate work."*
The brief: discover gatherings of every kind - Pokemon Go meetups, card tournaments, college football,
baby-shower expos, car shows - and gather continuously while he brainstorms what to build on it.

**The layer that is missing is not the crawler.** Verified verbatim at
`Glizzness/docs/superpowers/specs/2026-07-16-signal-net-design.md:179`: *"the crawler cannot and must
not auto-publish raw finds to it - a find has no coordinates, no region/market, no valid event_type
enum value, and hasn't been verified."* Three layers: crawler -> PRIVATE low-bar store -> human
curation -> PUBLIC gated directory. The crawler exists in the reference; the destination exists here
and is idle. **The unbuilt layer is the middle one**, which is also my v2 intake and also the parked
spec 9.5 decision. Three names for one component.

### D1 - the gathering store is SEPARATE from the publication contract, and lives here as ignored state

Decided on evidence, not preference. The cheap option - raw finds as `draft` rows in
`data/events.csv` - **is barred by this repo's own row contract**, tested 2026-09-06:

    validate_row({name, source_url, visibility=draft, rest blank})
    -> REJECTED: line 2: id is blank

`id`, `name`, `event_type`, `cadence`, `city` and `state` are required for EVERY row regardless of
visibility (`model.py:102-114`); only `source_url` and `last_verified` are conditional on publication.
A raw find has none of them - that is what makes it raw. So a draft row cannot hold a find without
either weakening the contract or fabricating values, and the contract is the thing that makes the
publication trustworthy. **The low-bar store must be permitted to hold what the strict store forbids;
that is the point of a two-tier design, not an accident of it.**

Shape: a `gather/` store inside this repo, **gitignored local state** with committed code around it -
the pattern Build 001 already uses (`equalshares/data/rollcall.db` ignored, `site/data/` committed).
No new repo, no new project to keep alive, the publication tree stays clean, and unverified
third-party text never enters git. Rejected: a separate repo (a second home to maintain for one
consumer) and Glizzness's `event_signals` (breaches the no-sharing constraint and ties a
general-purpose dataset to a hot-dog-cart project - its session recommended against it too).

### D2 - `event_type` stays a closed FILTER axis; a free-text `subtype` carries the truth

Converged on independently by both sessions, which is the strongest evidence available here. The enum
is a closed 23 and a brief of "wherever people gather" cannot be enumerated; widening it without bound
makes a taxonomy nobody maintains, and letting `other` absorb the tail destroys the filtering the
directory exists for. So: **the enum stays small and closed and remains what a user filters by**, and
one new column `subtype` is captured always and filtered never, preserving what the source actually
said. A research pass never has to stop and ask which of 23 a Pokemon raid is; it records the truth
and curation maps it. The closed list then **grows by evidence** - a value earns a slot when several
real events want it, the way a module here earns promotion, never by anticipation.

**This amends a frozen contract and is stated rather than done quietly:** the CSV header goes from 18
columns to 19, `EVENT_KEYS` gains `subtype`, and gate G7 (exact keys) moves with it. **Implemented
with its first consumer, not now** - a column no row uses is speculation, and this repo has argued
that position all week.

### D3 - no auto-publish, unchanged and absolute

The curation step is the ONLY path from the gather store into `data/events.csv`. A human sets
`visibility`. That was a locked rule before tonight and the brief does not touch it.

### Open, and Lance's

- **Scale.** D1's shape holds whether the store is hundreds of rows or millions, so nothing waits on
  this - but if he means "continuously" literally at national scale, the curation step becomes the
  bottleneck and the design needs a triage view before it needs more crawling.
- **Whether the reference's crawler is pointed at or rebuilt.** Its adapters are live and proven; my
  standing inbox rule says probe every candidate source with one real request before designing around
  it (RapidForge Build 003 lost forty minutes to sources that answer 403 to an unauthenticated fetch).
