**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` — Lane 0 delivery

# The first publish after the capabilities fix passed its gate, then was refused for being behind origin

Item: `confirm-the-publish-after-the-capabilities-door-deadlock-fix`.

## What the marker showed

`run_complete_20261005T163623Z` was run at `4e4637853`, so it contains `5e766f3c3`. The publisher
picked it up at 16:54Z. Its scoped publish suite ran and passed: the log reaches "Committing and
pushing (net=£104,663)" at 17:29Z, and `test_status_matches_the_record_for_every_entry` named no
red. **The capabilities-door deadlock did not recur.**

The commit was then refused before staging at 17:30Z with outcome `behind_origin` (rc=77). The seat
executor had landed `f1cbb15ca` at 17:25Z, and the shared tree could not fast-forward onto it. Three
paths blocked the fast-forward:

| Path | Against origin | Kind |
|---|---|---|
| `docs/design/BLOCKED_ATOM_VISIBILITY.md` | byte-identical | twin (the publisher's own derived-artefact repair) |
| the executor's `SEAT_FINDING_A_STALLED_FOCUS_ATOM_…` | byte-identical (untracked) | twin |
| `background/delivery_seat.py` | differs from HEAD and origin | **stranded hand work**, mtime 04:03 |

The `delivery_seat.py` hunk is `keeps_all_of`. It lets the seat's append-only guard accept an entry
inserted under the stretch log's header. Its test hunk sits in
`tests/background/test_the_direction_record_lands_on_origin.py` (mtime 2026-10-04 12:18). The
finding `WORKER_FINDING_A_BEHIND_SHARED_TREE_STOPS_THE_SEAT_LANDING…` (done/, 2026-10-05) already
named it as uncommitted and left it alone. Nobody has held it for about 30 hours, and it is now what
stops the publish.

## What this item did

It landed that pair as written, applied to origin rather than to the behind HEAD. Both mutations in
the test's docstring were run, and each turned it red:

- putting back `startswith` reds the prepended leg;
- an always-true `keeps_all_of` reds the dropped leg and one older test.

The proposal in that finding still stands and is not built here. `keeps_all_of` does not stop an
orientation written while the tree is behind from keeping the tree behind.

## Done means

A `site/data/dashboard.json` commit by the publisher, dated 2026-10-05 or later, is on origin/main.
That has not happened yet. The publisher's next cycle is at about 18:48Z. Reading for the next
session: if that cycle is refused again, read `.publish_gate_state.json` `failures[-1].cause`. If
the cause is `behind_origin`, the reconcile/fast-forward leg is the subject, not the gate.

**Settled 2026-10-06 (worker):** the done-means is met. Publisher commit `a88fb2436`
(`Auto-process run complete`, 2026-10-05 23:00 +0100) is on origin/main through `556b24b4e`. Two
further refusals stood between this note and that landing:

- the deletion-twin reconciler defect (`998814330`);
- the wall-census refusal on the refreshed run-output keys (`eaa94ed5f`).

Both have their own findings. The `keeps_all_of` proposal above is still unbuilt and still stands.
