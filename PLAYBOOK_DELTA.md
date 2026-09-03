# PLAYBOOK_DELTA - EventFinds

*The running list of traps and lessons **this project** earned. It is a delta, not a copy: the
trunk is `F:\RapidForge\MASTER_PLAYBOOK.md` (read section 4 traps before building) and the index of
every lesson on this machine is `F:\RapidForge\docs\PLAYBOOK_INDEX.md` (Tier 1 in ten minutes).
Pointers, never copies - copies fork (proven twice on this machine).*

## 0. Lineage

Glizzness `REPLICATION_PLAYBOOK.md` -> LinkedUmp `PLAYBOOK_DELTA.md` -> VisibleGov
`PLAYBOOK_DELTA.md` -> RapidForge `MASTER_PLAYBOOK.md` (the trunk) -> **this file**.

The traps specific to this product's shape live in `F:\RapidForge\modules\event-finder.md` section 6
(twenty-one, every one cited from `Glizzness/site/festivals/` and its data path). They are not
repeated here. When one of them bites *here*, or a new one is found, it goes below **with the
failure narrative**, and at the deposit gate it goes back to the module.

## 1. Earned here

### Lesson 1 - verify_deploy crashed instead of reporting on a missing local marker (2026-08-29)

Failure: `pipeline/verify_deploy.py` read each marker file straight off disk with `read_bytes()`
before the corresponding site file existed yet in the build order. A missing local file raised
`FileNotFoundError` and stopped the whole run instead of reporting one row's verdict. Diagnosis:
the reference instrument (copied from the RapidForge `verify-deploy` code candidate) had a verdict
for every origin-side failure (404 -> MISSING, byte mismatch -> STALE) but none for a marker whose
local half does not exist. Rule: any file read used to build a report verdict must be wrapped so
"the input doesn't exist" is itself a verdict, not an exception - fixed here with a `local_bytes()`
helper that returns `None` for a non-file path and a `NO-LOCAL` verdict instead of a crash.

### Lesson 2 - `node --test <directory>` treats a bare directory as a glob on Node 24 (2026-08-29)

Failure: `package.json`'s `"test": "node --test tests/js"` failed with
`Cannot find module 'F:\EventFinds\tests\js'` under Node 24.11.1 - zero tests collected, non-zero
exit, the whole point of the command lost silently until someone read the output. Diagnosis: Node
24 no longer walks a bare directory argument to `--test` as a test-file root the way earlier Node
versions did; it resolves the argument as a module specifier and a directory with no `index.js`
fails to resolve. Rule: pass an explicit quoted glob (`node --test "tests/js/**/*.test.mjs"`), never
a bare directory, and keep the same pattern everywhere the command is repeated (package.json,
README).

### Lesson 3 - A memory index line contradicted the memory file beneath it (2026-08-29)

Failure: Glizzness's `MEMORY.md` said Signal Net was "(repo, not deployed)"; `project_signal_net.md`
underneath it said LIVE, and `gh run list` confirmed scheduled runs writing rows. Diagnosis: the
index is a convenient surface; the file is closer to the source; the run log is the source - three
layers, each further from the truth than the last, and the outermost one is what gets skimmed.
Rule: read one level deeper than the summary before repeating a status. (Tier-1 rule 5, sighted at
session start.)

### Lesson 4 - "Gates green" did not yet mean the origin serves what the CSV says (2026-08-30)

Failure: a whole-branch review found three gaps that each passed on their own while the end-to-end
claim they exist to prove was never actually checked: `verify_deploy.py`'s `MARKERS` list named 8
of 19 files under `site/`, so an unlisted file could drift at the origin forever undetected; gate G5
proved `site/data/events.json` was merely not gitignored, not that it was committed together with
the CSV it was exported from; no `.gitattributes` meant a fresh clone with `core.autocrlf=true`
would fail gate G3 on line endings alone. Diagnosis: each check verified a necessary but
insufficient condition, and nobody asked whether passing all of them together actually proved the
claim until an adversarial pass did. Rule: when a gate's name promises an end-to-end guarantee (the
origin matches git; the publication is committed with its source), trace the claim to its weakest
link - a hand-maintained list, a check that proves possibility rather than fact, an unwritten
environment assumption - before trusting the gate's green.

### Lesson 5 - A new instrument's first red is as likely to be the instrument (2026-09-03)

During the 2026-09-03 documentation audit, the first check run against PLAYBOOK_DELTA was
`grep -c '^## Lesson '` and it returned **0** for a file holding four lessons - they are `### Lesson N`
under `## 1. Earned here`. Reported as written, that would have been a fabricated defect in this
project's own trail. Two peers hit the same thing the same day from the other direction: RapidForge's
new lessons column flagged ten headings across three repos as malformed and all ten were false, its
fourth new check to do this on a first run; LinkedUmp's new `public_surface.py` reported five failures
of which four were its own ignore-prefix bug.

**Diagnosis.** A new check is written against the format its author imagines rather than the corpus
that exists, so its first disagreement with reality is evidence about the check. The false-positive
form (flagging good input) is the one everyone names; the false-negative form is more dangerous and is
what happened here - a count of zero looks like a clean, quiet fact rather than an accusation, so
nobody interrogates it.

**Rule.** A new instrument's first run is a calibration pass, never findings. Before believing any
result, prove it can produce the other answer: point it at input you know is bad and watch it go red,
and at input you know is good and watch it go green. A zero counts as a red for this purpose. This is
the same discipline as the deferred staleness counter in `TODO.md` - a guard whose passing state has
never been distinguished from a broken one is not yet a guard.
