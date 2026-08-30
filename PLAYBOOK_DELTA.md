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
