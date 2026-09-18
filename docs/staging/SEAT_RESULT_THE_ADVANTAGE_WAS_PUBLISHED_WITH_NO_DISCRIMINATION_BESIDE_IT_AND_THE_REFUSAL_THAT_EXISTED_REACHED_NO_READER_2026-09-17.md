**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery (`the-level-selection-split-cannot-be-read-and-that-is-the-thesis-question`)

**Knowledge:** none new. No domain constant moves. This carries a refusal an artefact already
computed onto the surface beside the figure it qualifies.

# The advantage was published with no discrimination beside it, and the refusal that existed reached no reader

Delivery seat, 2026-09-17. Scores
`docs/staging/records/SEAT_PREREG_DOES_THE_FAMILYS_DISCRIMINATION_READING_REACH_THE_PAGE_BESIDE_THE_ADVANTAGE_2026-09-17.md`,
written before any measurement below and unedited. Continues today's
`SEAT_RESULT_THE_LEVEL_LEGS_SIGN_IS_DETERMINED_AND_POSITIVE...` and the two worker results that
carried the three legs onto the page. All three stand.

---

## What the direction asked, and which half was left

The item has two bars, not one:

> *report the sign with the bound the draw count earns* — **discharged this morning.** The level
> leg is positive at 18 draws, 63.0 sems from zero, sign test p = 7.6 × 10⁻⁶; the selection leg is
> unstateable at 1.80 of the 2.11 its own sample earns. Both now reach the page.

> *`discrimination_auc` must be reported beside the advantage on every run* … *A re-run that
> reports a new advantage figure without `discrimination_auc` beside it is NOT done.* — **this
> was not discharged, and it was not discharged in the way that is hardest to see.**

`tools/fold_noise_floor_family.py` has computed `discrimination_auc_across_seeds` since this
morning. The folded family carries it, `available: false`, with an exact reason naming which rows
could not answer. **`tools/generate_value_arms_data.py` contained no reference to that key** —
grep returned nothing — so `error_bar` published the 18-draw advantage, all three legs and their
verdicts, and no discrimination reading of any kind.

This is the shape this panel was repaired for eight hours ago, one level up. Then it was *a leg
nobody summarises is indistinguishable from a leg with nothing in it*. Here it is **a refusal
nobody summarises**, which is worse: the page did not read as though the question was hard, it read
as though nobody had asked it.

**The feed does carry a discrimination figure** — `decisions.discrimination_auc`, 0.615 — and
pairing it with this advantage would have been the defect, not the fix. It is **one run's**, against
a bound over **eighteen**. That mispairing is the one every other block in this file refuses by
name, and the retraction already on the page is what it costs: *the same estimator scored 0.646,
0.672, 0.465, 0.465 and 0.130 across five runs in four days.*

## The prereg, scored

| # | predicted | measured | |
|---|---|---|---|
| P1 | the raw nine-seed floors carry **no** `discrimination_auc_across_seeds` key; the fold carries it with a reason | `_20260910` and `_20260910b`: absent. `folded18`: present, `available: false` | ✅ |
| P2 | a `get(key) or {}` publisher would render those two states identically | confirmed — and **the mutation proving it did not fire on my first attempt**; see below | ✅ (with a correction) |
| P3 | the block is purely additive — no existing feed field moves | **7 keys added, 0 removed, 0 changed** but `generated_at` | ✅ |
| P4 | no page renders any AUC beside the three legs | the page's only AUC rendering is the `decisions` block, ~220 lines away and a different population | ✅ |
| P5 | the family's AUC is unavailable on 18 of 18, so the honest publication is a refusal and not a number | 0 of 18 carry a figure; nothing published this turn is an AUC | ✅ |

The refutation check the prereg required first — *if a page already states this beside the
advantage, land nothing* — was run first and came back negative.

**P3 named the way it would cost if it failed** (a control pinned to `error_bar`'s exact key set
going red on an additive block). It did not fail: no existing control pins that key set.

## The correction worth keeping: my own mutation did not fire, and the flattering reading was wrong

The control for the P2 collapse is the centre of this repair. Its mutation — swapping the key-
presence test for `not floor.get(KEY)` — **passed**. The comfortable conclusion was "equivalence,
the states are distinct anyway". It was not:

Both my test's inputs used a *non-empty* unavailable block, which is **truthy**, so both readings
agreed on both of them. The implementations part on exactly one input: **a key that is present and
falsy** — the producer emitted the field and put nothing in it. My test never built that.

It was a **missing test**, and the missing case is the one that matters, because the two refusals
prescribe opposite remedies. `never_asked` tells a reader *re-run these seeds under today's
producer and this becomes answerable*. For a family whose producer already recorded the field and
still yielded nothing, that is the one remedy that cannot help. The leg is added, and the mutation
now fires.

## What landed

1. **`_family_discrimination` in the publisher, with four states, not two.** `measured`,
   `asked_and_unanswerable`, `never_asked`, `no_floor`. The middle two are both "unavailable" and
   are kept apart deliberately: one cannot be fixed by re-running those rows at any sample size,
   the other can. It **republishes the fold's refusal verbatim** — reason and both counts — and
   never derives its own, because `_auc_across_seeds` already refuses a spread over whichever rows
   happen to answer, and a second implementation here would be the permissive one.

2. **It renders, on every branch including the empty one**, in amber, in the same panel as the
   legs. A block that appeared only when it resolved would put "measured and unavailable", "nobody
   asked" and "the producer stopped emitting" into one set of pixels.

3. **Nothing numeric is published for an absence.** 0.5 is a real reading meaning *the belief knows
   nothing* — which on this page is a finding against the company — and an unmeasured AUC rendered
   as 0.5 would make those two opposite conclusions the same figure.

4. **Ten controls, each named for its defect; six mutations run and every one fires.** The state
   partition is asserted **reachable over the real function** before any control is allowed to mean
   anything by a single branch. The wiring control drives the real `_error_bar` rather than the
   helper — a correct function nothing calls is precisely the state this repair found.

## What the page now says beside the advantage

> **DISCRIMINATION BESIDE THIS ADVANTAGE — CANNOT BE READ** (0 of 18 draws carry a figure). This
> family WAS asked and cannot answer… So the legs above say how much the arm won and this page
> cannot yet say whether it won by knowing anything. That is not a caveat on the finding — it is
> the half of the thesis this instrument has not measured, and it cannot be recovered from these
> rows at any sample size.

That is the direction's stated alternative to a determined sign — *"a published 'we cannot tell'
naming the draw count and what would settle it"* — now attached to the discrimination half, where
this morning's result attached it to the selection half.

## What is still owed, in order

1. **A floor family drawn under the producer that records the AUC per seed.** One leg is ~1h10m and
   6.4 GB; it cannot finish inside a turn and was deliberately not faked. Until one runs, every
   advantage in this family states its discrimination as unavailable — which is honest and is not
   an answer. When one lands, `state` moves to `measured` and the page renders the figure with no
   edit: that branch is built and tested.
2. **Five more draws would settle the selection leg** at today's mean and sd (n=23 against 18).
   Arithmetic at today's numbers, not a forecast — new draws move both.

## Reversal

One publisher function, one renderer, two test blocks. Reverting the commit drops the block and no
other feed field moves — which is P3 restated and measured.
