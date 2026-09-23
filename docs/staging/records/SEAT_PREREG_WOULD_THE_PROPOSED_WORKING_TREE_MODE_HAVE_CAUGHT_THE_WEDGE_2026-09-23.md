**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
**Class:** `publish_gate_and_wedge` (primary) · `control_cannot_fail` (secondary)

# Pre-registration: would the remedy a live continuation names have caught the wedge that is standing?

**Claim:** `the-publisher-cycle-the-withdrawal-item-still-owes-after-its-continuation-was-retired`
**Written BEFORE the measurement below was run.**

## The question

The live continuation
`the-regeneration-check-clones-at-head-so-it-cannot-see-the-producer-edit-that-wedges-the-publisher`
states its remedy as:

> Give `tools/published_feed_regeneration_check.py` a WORKING-TREE mode, and add the
> `churn_belief_size` chain to whatever it walks.

That remedy is written as settled. It is not measured. If it is wrong, the next seat spends a turn
building a control that would have been green throughout the outage it was built to catch — and a
control that cannot fail is this project's most expensive recurring shape.

## What I predict, and why

**Prediction 1 — the working-tree mode alone would NOT have caught this wedge.**

The wedge's staleness is not between `site/data/value_arms.json` and its generator. It is one link
further up, between `tools/churn_belief_size_response.py` (dirty, carries the new origin sentence)
and `docs/observability/churn_belief_size_response.json` (clean, stale, written 06:40 — BEFORE the
producer edit at 07:25).

`tools/generate_value_arms_data.py:15295` reads the stored intermediate and copies
`the_thresholds_own_origin` onto the feed. If that copy is a **pass-through** — no independent
derivation — then regenerating `value_arms.json` in ANY tree, from ANY standpoint, reads the same
stale intermediate and reproduces the same stale bytes. Feed and generator **agree**. The check
goes green while the publisher stays wedged.

So the mode is not the binding constraint. The binding constraint is WHICH RELATION is checked.

**Prediction 2 — the module cannot express the relation that is actually broken.**

`COVERED_FEEDS` maps `site/data/<name>.json` → generator, and `_committed_feed` reads
`HEAD:site/data/<name>`. `FEED_DIR` is `site/data`. `docs/observability/churn_belief_size_response.json`
is not under it. The broken relation is therefore not merely unlisted — it is outside the module's
addressable space, and "add the chain to whatever it walks" understates what the fix costs.

**Prediction 3 — `value_arms.json` is not in `COVERED_FEEDS` today.** (Weakest of the three; stated
so it can be wrong.)

## What would refute each

1. **Refuted** if `the_thresholds_own_origin` is derived in `generate_value_arms_data` from
   anything other than the stored intermediate — a re-read of the producer, a recomputation, a
   fallback that consults `churn_model`. Then a working-tree regeneration WOULD diverge and the
   continuation's remedy is sufficient.
2. **Refuted** if `COVERED_FEEDS`/`_committed_feed` already accept a path outside `site/data`.
3. **Refuted** if `value_arms.json` appears in `COVERED_FEEDS`.

## What I will NOT conclude

That the continuation's author was careless. A bounded tick cannot see the whole chain — that is
the stated reason this seat exists. The finding, if it lands, is about the REMEDY SENTENCE being
load-bearing and unmeasured, not about who wrote it.

## Disposition this prereg does not prejudge

Whether the instance (the standing red) is dischargeable from an isolated worktree at all. It is
measured separately; the answer there is already known to be "not without writing another lane's
uncommitted bytes", and this prereg is about the CLASS control, not the instance.
