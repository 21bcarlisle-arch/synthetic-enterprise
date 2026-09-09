**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the published inversion must carry its attribution on the page) · **Class:** measurements_that_mirror

# RESULT — the strata clause is a conditional on the feed's own evidence, so the two lanes merge without a contradiction

Discharges the *"what is next — the reconcile recipe, not a re-build"* section of
`SEAT_FINDING_THE_LANE_0_ITEM_WAS_BUILT_TWICE_AND_THE_TWO_COPIES_CONTRADICT_EACH_OTHER_ABOUT_THE_STRATAS_INTERVAL_2026-09-09.md`
(`992f49745`). No part of either lane's work was rebuilt.

## Why this was done ahead of the drawn item's own subject

The drawn Lane 0 item is *publish the nine-seed floor, then grade the pre-registration*. Its run was
still in flight for the whole of this turn (PID 704091, `longjob-arms-rerun-20260909b.service`, 5h59m
elapsed at the last check, `..._20260909b.json` not yet on disk), so the publish could not be done.
The finding above says the contradiction it names becomes visible **on the first run that carries a
`cross_null`** — which is the run now finishing. Defusing it is therefore work on the item's critical
path and not a detour, and it had to happen before the artefact lands rather than after.

## What was wrong

Two lanes built the same Lane 0 deliverable concurrently. Local `b16281092` composed the strata
caveat as a flat claim:

> "**These strata carry NO interval of their own.** They are terms of the 0.4210 above … so the only
> bound here is the one that figure's own permutation earned, 0.4458–0.5540."

Origin `2df665040` computes `cross_stratum_null_spread` — a real permutation over the cross stratum's
own pairs — and `run_value_cycle_ab._stratum_figure` publishes it as `null_95_low`/`null_95_high` on
that stratum. Both copies are internally consistent, both door controls are green, and neither lane
can see the other's tree. On the first block-carrying run the page prints the denial beside the
interval it denies.

**And two controls were holding the categorical sentence in place**, which is the half the finding
did not name. Both were pinned to today's answer rather than to the property, so they would have gone
on *demanding* the denial after it became false:

* `site/test_...reader.py::test_an_out_of_null_estimand_reaches_the_reader_with_WHICH_PAIRS...` —
  `assert "NO interval of their own" in rendered`.
* `...::test_NO_cut_ANYWHERE_in_the_feed_renders_its_number_without_its_OWN_interval` — the same
  literal, asserted per rendered decomposition term.

This is the shape CLAUDE.md names: *a control pinned to the current state goes red when the code
becomes more honest and stays green when the claim rots.*

## What was built

**1. The clause is a conditional on the feed's own evidence** (`_pair_strata_interval_clause`). It
reads `strata.cross.null_95_low`/`null_95_high` — the two keys `_stratum_figure` emits exactly when a
permutation was computed — and composes the categorical opening when they are absent, or an opening
naming the cross stratum's own interval when they are present. The leverage/clustering clause, which
was the item's own third deliverable, is composed once and appended to **both** openings: it is a
property of how the cross pairs are built, not of whether anybody permuted them.

The discrimination is on the feed and never on which producer wrote it, which is what makes it
correct under both trees without either having to know about the other. A new `of_their_own` field
names the strata that do carry one, so a control can ask the question without parsing prose.

Also fixed in passing: the old guard checked the counts but not `null_95_low`/`null_95_high`, while
formatting both with `:.4f` — a leg with no interval crashed the page rather than withholding the
sentence.

**2. Both controls are re-keyed to the property.** The walker now asserts the producer's *composed*
clause reaches the reader and that the term it speaks for really has no interval of its own; the door
control drives **both branches** — today's feed on the categorical side, and an injected `cross_null`
on the bounded side, asserting the denial is gone, the cross interval reaches the reader, and the
leverage clause survives.

## Recipe step 1 needs no work, and that is measured rather than assumed

The recipe says take origin's `run_value_cycle_ab.py` whole. Local's changes to that file since the
merge base (`8fb7d357e`) are four hunks, all in `book_identity` and `noise_floor`; none touch the
`pair_strata` region. So origin's producer arrives by ordinary merge with nothing to reconcile.

## The poison round — four mutations, each fired

Run before trusting the pass, because *survived* means two opposite things. Both source files were
restored byte-identical afterwards and verified so.

| Mutation | Fired on |
|---|---|
| M1 `bounded = False` — the categorical opening always selected | `of_their_own` does not name the cross stratum |
| M2 `of_their_own` hard-wired to `None` | same leg, from the other direction |
| M3 a decomposition term gains an interval of its own | the walker's new term-level leg, naming `within_settled` |
| M4 opening always categorical, `of_their_own` left correct | *"the clause still denies these strata an interval on a feed that publishes one"* |

M4 exists because M1 was caught by an **earlier** leg, which leaves the sentence leg's own
reachability unestablished. It is the mutation that proves it.

One leg was written and then **deleted**: a check that the rendered term is not named in
`of_their_own`. Under origin's producer the cross stratum carries `decisions` and is classified as a
measured cut, so that leg can only ever pass vacuously, and it parsed the term's name out of a
dotted path to do it. The term-level interval check (M3) holds the same property directly and can
fail. The smaller mechanism is the one kept.

## What did NOT move, and why that is the correct outcome

`site/data/value_arms.json` is byte-identical under the new clause — verified by recomposing it from
the live feed's own published split and comparing, rather than by regenerating. The live feed's cross
stratum has no interval, so the conditional selects the same opening it always did.

A fail-closed conditional cannot change live bytes on a correct feed, so this is what a correct
result looks like here; predicting the page would move would have been predicting a defect.

**Evidence:** `site/test_the_baseline_comparison_reaches_the_reader.py` — 120 passed, 1 skipped.

## What I am NOT claiming

I have not merged the two trees, and I have not run origin's own producer tests. I am claiming the
contradiction cannot reach a reader through this page's clause under either producer, and that the
two controls that would have re-armed it no longer can. Whether origin's door control is green at
origin's HEAD is untested here.

I have also not produced a run carrying a `cross_null` — the bounded branch is driven by injection,
not by an artefact. The nine-seed run in flight is expected to be the first to carry one; if it lands
and the bounded branch still does not fire, that refutes the *urgency* of the finding above but not
this repair, which is keyed to the feed and not to that run.

## What is next

The drawn item's own subject, unchanged and untouched by this: publish `..._20260909b.json` when it
lands (commit it the moment it exists — a floor artefact was eaten by `git clean -qfd` on
2026-09-03), decide the `CURRENT_WORLD_NOISE_FLOOR_PATH` pair move deliberately rather than drifting
into two n's for one quantity, and grade the pre-registration. `SEAT_FINDING_THE_NINE_SEED_FLOORS_
STATED_PUBLISH_PATH_DOES_NOT_REACH_THE_LEG_THE_RUN_EXISTS_TO_SETTLE_2026-09-09.md` is the standing
warning that the item's own stated done-criterion feeds `contrast_bounds` and not the selection leg.
