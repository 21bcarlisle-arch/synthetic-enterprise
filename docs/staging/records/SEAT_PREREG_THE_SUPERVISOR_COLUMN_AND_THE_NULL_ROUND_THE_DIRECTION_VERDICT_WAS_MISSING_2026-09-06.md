**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# PRE-REGISTRATION: the supervisor column and the null round, the two things `direction`'s verdict never had

**Written 2026-09-06 08:47, delivery seat, shared tree at `d75b57f94`. Claim id
`direction-battery-supervisor-column-at-the-node-grain-fingerprint`. Battery fingerprint
`b2f590060521`, results `/var/tmp/direction_battery_b2f590060521.json`, run under
`systemd-run --user --unit=direction-battery-b2f5`. Every prediction below is fixed BEFORE the run
returns and this file is landed ahead of the result.**

---

## 1. What was actually missing, and it was not only the supervisor column

The published verdict — *seven of `direction`'s eight contracts are proved only by tests of the
subject itself* — was graded at fingerprint `ef6ece4e233b`. The newest results file on disk is
`2d872733982b`. **Neither is the fingerprint of the spec in the tree**, because `190d968cb` moved
`test_the_decision_log_is_APPEND_ONLY` from `MIXED_NODES` into `DIRECT_NODES`, and the node-grain
split is hashed. So the state before this run is not "three columns graded and one missing". It is
**nothing graded at the fingerprint the spec now describes.**

That is worth saying plainly because the drawn work described the narrower thing, and the narrower
thing is what a reader of the results file would have concluded too: `2d872733982b` reads
`survived_all: null` with `ungraded_callers: ["tests/background/test_supervisor.py"]` on all eight
rows, which is an honest report of a partial run and says nothing at all about being one
fingerprint stale. **A results file names the spec that scored it; it cannot name the spec that
has since replaced it.**

Two gaps, then, and both are closed by one run because the expensive suite is the same one:

1. **The supervisor column**, ungraded on all eight rows. The published caller verdict rests for
   that column on a transfer argument — `background/direction.py` and
   `tests/background/test_supervisor.py` are byte-identical at `cfd4a5d4c`, at HEAD and on disk,
   and `test_supervisor.py` declares zero `direct_nodes` so nothing about its cell changed. **That
   argument is sound and it is still an argument.** It is also now weaker than it reads: the
   fingerprint moved, so what the cell would be transferred *from* was never scored under this
   spec either.
2. **The null round**, which this subject has never had. Every prior run ended on its own last
   line saying so: *whether any kill came from a suite reading `direction.py`'s TEXT rather than
   running it is UNKNOWN, not ruled out.* `NULL_OLD`/`NULL_NEW` are added in the same commit as
   this file, which is what moved the fingerprint to `b2f590060521`.

## 2. The predictions

Fixed before the run returns. Each names what would refute it.

**P1 — `test_supervisor.py` reddens under the poison floor.** It imports `background.supervisor`,
which imports `direction` at module scope, so an import-time raise must reach it.
*Refuted by:* a green cell in the poison round, which would mean the column is BLIND and every
survival below it means unreachable rather than unproved.

**P2 — all eight mutations SURVIVE `test_supervisor.py`, and the suite is stamped
`imports_but_proves_nothing`.** The mechanism is on the spec already: the suite's only reference to
the subject is a fixture's `monkeypatch.setattr(DIRECTION_PATH, ...)` pointing at a file nothing
writes, so `read_direction` returns `None`, `focus_weights` short-circuits and `focus_multiplier` is
never called. This is the middle state the engine warns is more dangerous than blindness, because it
reads as the good answer.
*Refuted by:* any kill in that column — which would be the first evidence the supervisor exercises
a `direction` contract at all, and would make the transfer argument's conclusion right for a reason
nobody had.

**P3 — the null round leaves all five suites green.** No suite here reads the subject's source.
**This is the prediction most at risk and it is the one to watch**, for a reason that has nothing to
do with the four columns: `NULL_NEW` introduces a module-scope name, `_NULL_ROUND_MARKER`, and this
tree has static-quality controls over module-scope constants. If any of the five suites transitively
runs one, it reddens for the marker and not for `direction` — a null round that reddens for its own
instrument, which would be this class of defect committed by the instrument that finds it.
*Refuted by:* any red. If it is red, the round is void and must be re-cut against a marker with no
new binding, not read as "these suites grade text".

**P4 — the three cheap columns reproduce `2d872733982b` exactly:** M8 killed by
`test_the_self_audit_declared_a_correction_and_nothing_carried_it.py`, M1–M7 surviving every caller.
The node-grain move affects `test_delivery_seat.py`'s deselection only, and no published cell was
attributed to the node that moved.
*Refuted by:* any change in `killed_by` on the three cheap columns — which would mean the node-grain
correction changed a verdict, not just a population.

**P5 — the headline survives with a real verdict under it.** All eight rows carry a non-null
`survived_all`; seven read `true`; M8 reads `false`. The published sentence — seven of eight proved
only by the subject's own tests — is then a measurement rather than three measurements and an
argument.
*Refuted by:* any row still null (the run did not finish), or a count other than seven.

## 3. What "done" means for this claim

This is direction, not an atom, so it carries no exit test and the definition is the seat's. **Done
is: a results file at `b2f590060521` with all five columns and the null round in it, the eight rows
carrying a non-null `survived_all`, and the published verdict either confirmed against it or
corrected beside it.** A run that returns only the supervisor column would satisfy the drawn wording
and leave the verdict standing on two stale fingerprints, which is why the run grades all five.

## 4. The hazard this run carries, and what holds it

The battery patches `background/direction.py` **in place** in the SHARED tree and restores it from an
`atexit` handler. `atexit` does not run on `SIGKILL`, and the publish daemon commits from this tree.
Two things hold it: the run is under its own `systemd-run --user` cgroup rather than the seat's
(`setsid` is irrelevant to the actual killer, and an earlier `contract_battery` round died at ~18
minutes proving it), and `/var/tmp/direction_battery_watchdog.sh` — adapted from the watchdog a
previous lane wrote for the `se-seat-executor` worktree — waits on the unit and restores the pristine
copy the moment it is gone, mutated or not, logging which it found.
