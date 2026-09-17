# PREREG — does the simulated ImportError actually raise, and does that test write the LIVE draw ledger?

*Written 2026-09-17 ~09:25 UTC, BEFORE the measurement. Lane 0, claim
`lane-0-consulted-the-focus-list-zero-times-in-three-hours`.*

## Why this, and not the thing the item named

The drawn item named a suspect and asked me to confirm it **by counting, not by reading**. I
counted first, and the count refutes it.

The item says: *"the eight consecutive rows in `.delivery_lane_claims.draws.json` stamped
`source: continuation` / `source_self_issued: False` advanced the chain by nothing and the limit was
never reached."*

Three of its factual claims are wrong against the real ledger:

1. **The path does not exist.** There is no `background/.delivery_lane_claims.draws.json`. The live
   ledger is `docs/observability/.delivery_lane_claims.draws.json` (359 rows).
2. **There is no such run of eight.** Across all 359 rows, `(continuation, self_issued=False)`
   occurs 11 times, never consecutively. The eight rows stamped `source_self_issued: False` with
   `source_named_by_direction: True` are `source: focus` rows — focus draws, not continuations. The
   recent continuation run is stamped `self_issued: **True**`, which is the opposite of the premise.
3. **The limit IS reached.** Replaying `_self_issued_chain` at each of today's draws:
   03:05→0, 04:29→1, 04:38→2, 05:06→3, 06:07→0, 06:38→1, 07:04→2, 07:36→3, 08:24→4, 08:39→5.
   It crossed `SELF_HANDOFF_CHAIN_LIMIT = 3` at 05:06 and again at 07:36, and kept climbing.

So the chain counter works and the swap fires. The question the item *meant* to ask is still open:
why does the focus list not win when it does?

## What I actually found, and what I have not yet established

The 08:39 draw is a row whose id is **`some-id`**, stamped `source: focus`, with neither
`source_self_issued` nor `source_named_by_direction`. `some-id` is not work. It is a **test fixture
id**, and it appears exactly once in the repository:
`tests/background/test_dispatch_is_the_claim.py:200`, inside
`test_a_lane_that_cannot_import_does_not_take_the_tick_down`.

That test monkeypatches `builtins.__import__` with a `_boom` that raises only when
`name == "background.delivery_lane" or name.endswith("delivery_lane")`, then calls `wt.run_tick()`
on a doorbell reading `"LANE 0 DELIVERY -- ... --landed some-id"`. Unlike the file's `lane` fixture,
it takes only `_isolate` — it does **not** redirect `delivery_lane.CLAIMS_FILE`.

## PREDICTIONS (recorded before running anything)

**P1 — the simulated failure never happens.** `from background import delivery_lane` calls
`__import__("background", ..., fromlist=("delivery_lane",))`. The name handed to `_boom` is
`"background"`, which neither equals `"background.delivery_lane"` nor ends with `"delivery_lane"`.
So `_boom` re-dispatches to the real import and it **succeeds**. The test's stated mutation ("drop
the `try/except` in `_claim_dispatched` and this reddens") therefore **cannot fire** — the except
arm is never entered. It is a control that cannot fail, asserting `outcome == "SPAWNED"`, which is
true on both sides of the branch it claims to test.

**P2 — so the test takes the real path, and writes the LIVE stores.** `_claim_dispatched` calls
`delivery_lane.claim_dispatched(reason)` with no `path=`, so it resolves
`delivery_lane.CLAIMS_FILE` — unredirected in this test — and `record_draw` writes
`docs/observability/.delivery_lane_claims.draws.json`. I predict running this one test in an
isolated extract writes a `some-id` row into that extract's ledger.

**P3 — and that write is what postpones the focus list.** A phantom row stamped `source: focus`
with no `source_self_issued` **breaks the run** in `_self_issued_chain`, which walks newest-first
and stops at the first falsy flag. The live chain went 5 at 08:39 → **0** at 08:49. So every run of
the background suite in the shared tree silently **resets the chain to zero**, and the continuation
source keeps winning for another three draws. The item's symptom is real; its named cause is not.

**What would refute me.** P1 fails if `_boom` does fire (then the except arm is live and the test is
honest). P2 fails if something else redirects `CLAIMS_FILE` for this test — `_isolate` in
`test_worker_tick.py` is the candidate I have not yet read. P3 fails if `record_draw` is not
reached, or if the phantom row does not break the chain in a replay.

If P2 fails, P3 is untouched as a *property* — a `source: focus` row with no authorship flag resets
the chain whatever wrote it — but the test would not be the writer, and I would owe a different
answer to "who wrote `some-id` at 08:39 today and again on 2026-09-06".

## Done means

A control, keyed to the property and written over the whole partition rather than a leg per branch,
that goes red if a dispatch-time claim can write a store the test did not choose; the polluting
test made able to fail; and the phantom row's effect on the chain stated in the record beside the
claim.
