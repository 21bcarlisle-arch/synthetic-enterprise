**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** publish_gate_and_wedge

# PRE-REGISTRATION: the publish gate's own five blocking files, written before I change a line

Delivery seat, 2026-09-17. Claim
`the-publish-gates-own-tests-are-red-at-head-and-the-finished-repair-is-unlanded`.

## What is already established, without measurement

**Leg (b) of the drawn item is SPENT.** The item asks me to land 207 uncommitted insertions in
`background/process_run_complete.py` implementing reachability-not-equality, and to `git mv` the
finding into `docs/staging/done/`. Both are already at HEAD:

    git log --oneline -3 -- docs/staging/done/WORKER_FINDING_THE_PUBLISH_SUCCEEDS_BY_REACHABILITY_...
      -> 9c4ce323f  the publish verdict asks REACHABILITY, and asks it after the cadence that
                    absorbs the commit

The finding is in `done/`, committed. This worktree is clean at `f0af86639`, so there are no
uncommitted insertions here to isolate — the premise check's warning that "the work may have landed
by another route" is correct for leg (b), and `tools/isolate_hunks.py` has no subject. I am not
re-doing it.

**Leg (a) is live and reproduces exactly.** Five files, one cause, in a clean tree at HEAD:

    14 failed, 56 passed
    background/live_ledger_guard.LiveLedgerWriteUnderTest:
      process_run_complete._landing_in_flight_marker refused: ... .publish_landing_in_flight.json
      is a LIVE observability record

The item says 17; it is 14. The count moved because `9c4ce323f` landed between the item being
written and drawn. **I record the discrepancy rather than the item's number**, because the item's
figure is an un-re-asked prediction about a tree that has since moved.

## The diagnosis, and why the obvious repair is the wrong one

The guard is RIGHT to refuse, and this is worth saying because the tempting fix is to carve the
marker out of `is_live_record_path`. `.publish_landing_in_flight.json` is not a measurement ledger,
so the carve-out is superficially arguable — but a marker written by a test process makes
`_landing_in_flight()` answer "live" to the real heartbeat, which **suppresses the liveness
publish for up to `PUSH_THROTTLE_SECONDS`**. That is Fault #1 (2026-07-25) re-manufactured through a
new door. A test must not be able to write this path. The guard stays as it is.

The guard's own error names the remedy — an injected path. The parked mechanism for exactly this
already exists: `tests/background/conftest.py::_LEAKING_STATE_CONSTANTS`, whose docstring defines
its population as *"constants a test writes as an INCIDENTAL SIDE-EFFECT of exercising something
else, so the live file is nobody's subject and re-rooting it costs no control"*, and which closes
with *"A new leak is one line plus a re-run of this directory; do not re-derive the wide version
without reading the 43."*

That docstring imposes ONE admission test, and I checked it before predicting: **is the live
artefact any control's subject?** Measured, not assumed — one constant, one module, one test:

    LANDING_IN_FLIGHT_FILE          -> background/process_run_complete.py only
    .publish_landing_in_flight.json -> tests/background/test_the_liveness_heartbeat_took_the_tree_
                                       from_the_content_publish.py:46, which already points it at
                                       `tmp_path` in its own body

So the one file whose subject IS this marker has already re-rooted it itself, and its body-level
`monkeypatch` runs after the autouse fixture and wins. Nothing asserts a test cannot write the live
marker. The admission test passes. This is a one-line addition to an argued register, not new
machinery.

## The predictions, made before running anything

**P1.** Adding `("background.process_run_complete", "LANDING_IN_FLIGHT_FILE")` to
`_LEAKING_STATE_CONSTANTS` turns all 14 failures green, with no other edit to any of the five files.

**P2.** It costs ZERO other controls: a full re-run of `tests/background/` shows no test red that
was green before. This is the leg the docstring's "43 other controls" warns about, and the only
reason I expect to pay nothing is that this constant's sole subject-control re-roots it already.

**P3.** `test_the_liveness_heartbeat_took_the_tree_from_the_content_publish.py` stays green
entirely — all of it, including the lexical control at line ~146 asserting the
`_land_publish_commit(...)` call sits inside a `with _landing_in_flight_marker(...)` block.

**P4.** The re-root is harmless to the guard: `_reroot` preserves the repo-relative path, so the
destination becomes `tmp_path/docs/observability/.publish_landing_in_flight.json`, which is NOT
under the real `LIVE_RECORD_DIR`, so `guard_live_ledger_write` returns it unchanged and the write
proceeds. **The guard is still called on every one of these paths** — I am moving the destination,
never removing the check.

**Falsifier for each:** any of P1–P4 false. If P2 fails I do NOT widen the redirect to buy the
green; I report which control lost its subject, because that is the 43-control trade the docstring
measured and I would be re-making it blind.

## What I am NOT claiming

The item's own warning stands and I expect it to SURVIVE this repair:
`.publish_gate_state.json`'s last `liveness_surface_refusal` ends `fatal: cannot lock ref 'HEAD':
is at aff4b153f but expected 56d746816` — the publisher losing the HEAD ref lock to another lane
mid-commit. **That is a different fault and nothing here touches it.** If the gate is still not
green after this lands, that is the reason, and it is not evidence P1 was wrong.

I also do not predict I can make `.publish_gate_state.json` carry a non-null `last_clean_publish`
within this turn: that figure must be graded by the publisher on a real cycle, not typed in, and
whether a cycle runs and wins the ref-lock race inside my turn is not mine to control.
