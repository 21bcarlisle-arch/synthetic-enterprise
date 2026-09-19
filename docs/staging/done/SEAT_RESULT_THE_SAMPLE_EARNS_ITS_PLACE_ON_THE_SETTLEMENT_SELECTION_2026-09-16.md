**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, director's Stage 1: *"the sample earning its place on the settlement selection"*

# The sample earns its place on the settlement selection — 1.66x on the worst axis — and the evidence is now keyed to the world it was measured in

Delivery seat, 2026-09-16. Supersedes the world-mismatch half of
`SEAT_RESULT_P1B_IS_STILL_UNGRADEABLE_BECAUSE_THE_FILED_EVIDENCES_WORLD_IS_GONE_2026-09-15.md`,
whose refusal was correct and whose diagnosis is unchanged.

---

## The answer, on the world we actually run

| | count cull | chosen + weighted | |
|---|---|---|---|
| settled accounts | 90 | **83** | the sample costs 7 accounts |
| committed customer-years | 1195.4 | 1199.2 | the budget, not the count, is the constraint |
| worst-axis KS vs population | 0.09765 | **0.05878** | **1.66x better** |

**§A's P1b HOLDS**, and holds by more than it did on the world it was filed against (1.66x against
the filed 1.55x). It also holds on §A's named-and-existing pair.

Per-axis gain, chosen against cull:

| axis | gain |
|---|---|
| `raw_infiltration_ach` | **4.54x** |
| `floor_area_m2` | 2.64x |
| `fabric_w_per_k` | 1.37x |
| `customer_years` (cost) | 0.22x |

A **20.7x spread** across the axes. The choosing is doing nearly all of its work on infiltration and
very little on the heat-loss coefficient, and it *loses* on cost — which is the shape §A predicted
(gain concentrated on the fabric axes rather than on cost) and is now graded rather than inferred
from a maximum.

**What this buys, in supplier terms.** The settled book is ~83 accounts drawn from ~502 campaign
wins, and it is the only population margin, carbon and the intervention ranking are summed over. A
sample that reproduces the population's count by year but not its distribution over the demand axes
biases every one of those figures in a direction nobody had measured. This says the bias on the
worst axis is now about two fifths of what the old count rule left, for the price of seven accounts.

## The repair that made it gradable, and it is not a tolerance

The filed evidence could not grade anything for five days. `--check` refused with five
disagreements, and the refusal was **right**: the 2026-09-11 record was measured at base
`3957ba848`, which does not contain `0d86d6dfe` — *"the world's homes are drawn from the fitted
joint now"*. The funnel was identical (502 candidates, the cull settling the same 90 at the same
1195.3895 cy); the homes were not (105 distinct fabric vectors against 109). A KS over the fabric
axes is a statistic about the homes.

So: **a correct refusal is not a population.** It correctly excluded a grading on the wrong world,
and it was then read as though the claim itself were unavailable. The claim was fine; the evidence
had no home.

**What I did not do:** re-point the single filed record at today's numbers. That passes immediately
and re-creates the identical staleness the next time the stock moves — a control keyed to today's
answer, which goes red when the code becomes more honest and stays green when the claim rots.

**What I did:** keyed each filed record to the world it was measured in, by the two digests that
already exist for exactly this — `departure_level_anchor.world_level_identity` (the departure
surface) and `world_home_identity.home_stock_identity` (the fabric of the stock). `--check` grades
against the record whose world is live. A stock change now produces *"this world has no filed
evidence — re-file"* instead of five numbers that read as the method disagreeing with itself.

Three properties, each with a leg that can fail:

- **A null stamp never matches.** The 09-11 entry carries `home_digest: None` because the digest
  post-dates it; its mismatch was established by *cause*, which is stronger than a digest. `None`
  must not compare equal to a live digest — that would restore the whole defect, quietly.
- **It fails closed.** An unreadable digest refuses and says which one; it does not fall through to
  the newest entry. *"I cannot tell which world this is"* and *"this is the newest world"* are
  different states.
- **The refuted prediction is kept.** The 09-11 entry stays beside the 09-16 one. A wrong
  prediction next to its result is the only evidence the experiment was designed before its answer
  was known.

Controls:
`tests/tools/test_settlement_evidence_is_graded_only_against_the_world_it_was_measured_in.py`, 8
legs. Mutation-proven: letting a null home digest match anything reds three of them.

## One published key was renamed, because it had become a false sentence

`profile_on_THIS_base_which_is_NOT_the_filed_one` → `profile_on_THIS_base`. The old name was true
on 2026-09-15 and became a lie the moment this world got its own filed record — the two keys now
hold identical objects by construction. **A key that asserts a state rather than naming a quantity
rots into a false claim the first time the state changes.** No code read it; the 09-15 result
document and the artefact did, and both are superseded here.

## What remains, and it is the honest limit

The 4.54x on infiltration against 1.37x on `fabric_w_per_k` is not explained. The chooser is
spanning the axis the population is most spread on, which is the expected behaviour of a
space-filling criterion, but *expected* is not *measured* — and `fabric_w_per_k` is the axis the
demand model is most sensitive to. Whether choosing harder on the axis that matters most beats
choosing on the axis that spreads most is a real question and it is unasked. **It is not answered by
this run and I am not going to infer it from this table.**

Next on Stage 1: the people layer, then the half-hourly shape reaching the book.

## Class registration

Belongs to `figures_on_a_superseded_clock`.

The defect this records is evidence outliving the world it was measured in, and the repair is a
stamp that makes the mismatch nameable. That is this class in its "the figure is fine, the clock
under it moved" shape, not a control that could not fail — the control here refused correctly for
five days.
