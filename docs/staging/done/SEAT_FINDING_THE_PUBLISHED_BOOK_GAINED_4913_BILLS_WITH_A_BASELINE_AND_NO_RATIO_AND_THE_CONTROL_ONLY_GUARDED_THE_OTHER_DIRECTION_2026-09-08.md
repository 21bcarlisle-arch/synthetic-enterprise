**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** a-published-bill-shock-can-be-recomputed

# The published book gained 4,913 bills with a baseline and no ratio, and the control was armed for the other direction

**2026-09-08, found in passing** while running the bill-shock suites against the HMT receipt leg
(`docs/staging/SEAT_RESULT_THE_WORLD_CAN_NOW_SAY_WHO_PAID_THE_BILL_AND_THE_TAUTOLOGY_WAS_IN_MY_OWN_DRAFT_2026-09-08.md`).
**Not my change**, and the proof is below rather than asserted, because "it isn't mine" is the
easiest thing in this repository to be wrong about.

---

## The red

    tests/saas/test_a_published_bill_shock_can_be_recomputed.py
      ::test_the_baseline_is_present_exactly_when_the_shock_is
    AssertionError: 4913 bill(s) publish a baseline with no ratio

## It is the artefact, not the code, and here is which copy

`docs/reports/run_output_latest.json` is a publisher output on its own cadence. The working-tree
copy was written **2026-09-08 08:25**, eleven minutes before this turn began. Read both copies
without touching the tree (`git show HEAD:...` against the file on disk):

| copy | bills | shock, no baseline | baseline, no ratio |
|---|---|---|---|
| HEAD (committed) | 10,906 | 10,655 | **0** |
| working tree (08:25) | — | — | **4,913** |

The committed book fails nothing. The freshly published one fails on the *opposite* leg from the
one the test's own docstring was written about. My diff is confined to `simulation/` and
`tools/run_price_ladder.py` and touches no `saas/` billing code; no edit of mine can retroactively
alter a JSON file on disk.

## Why nothing caught it — the control is armed in one direction only

The test's `_bills()` docstring records a deliberate, correct decision: the artefact legs SKIP
while no bill carries a baseline, because on the commit that landed the repair the book was still
written by the pre-repair generator, and a control red for a reason its own commit cannot fix is
the landing-order defect this repository has already paid for.

That self-arming is keyed to `shock without baseline` — the stale-book direction. The new publisher
produces the **mirror**: baseline present, ratio absent. There is no skip for it and no explanation
for it, so it lands as a hard red on every lane in the shared tree.

This is the shape the register already has a row for: *a control keyed to today's answer goes red
when the code becomes more honest*. Here the producer got MORE complete (it now emits a baseline
broadly) and the consistency leg reads that as a defect.

## What is not yet established

**Which is wrong — the generator or the control.** Two readings, and I did not run the one-variable
version because it is another lane's producer and I hold no claim on it:

1. The generator now publishes a baseline for bills whose shock ratio is legitimately `None`
   (a first bill, no prior period). If so the CONTROL is wrong: a baseline without a ratio is not
   an inconsistency, it is a bill with nothing to compare to, and the assertion should be one-sided.
2. The generator computes a baseline and then drops the ratio somewhere downstream. If so the
   control is right and the producer regressed on 4,913 bills.

The tell that separates them is whether those 4,913 are first-bills-per-account. That is one
grouping over the artefact and it is the next step, not a guess to publish.

## What this costs right now

It is a **BLOCKING** red in the shared working tree: the gates read the whole tree, so every lane's
commit is refused by it until it is resolved or the artefact is republished. This turn's own
landing goes through `tools.surgical_land`, which gates HEAD-plus-my-hunks and therefore does not
carry the other lane's artefact — the legal route, and it does nothing for anyone else.

## What is next

1. Group the 4,913 by account and test reading (1) against reading (2). One query.
2. Whichever way it falls, the self-arming skip needs to cover **both** directions or neither —
   a mirror leg with no skip beside a leg with one is how this became a whole-tree wedge instead
   of a note.
