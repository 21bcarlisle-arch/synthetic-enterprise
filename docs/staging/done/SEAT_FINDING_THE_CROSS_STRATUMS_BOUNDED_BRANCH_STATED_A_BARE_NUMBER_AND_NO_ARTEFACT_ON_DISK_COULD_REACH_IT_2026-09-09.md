**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — grade the per-leg conditioning pre-registration) · **Class:** controls_that_cannot_fail

**Subject:** `tools/run_value_cycle_ab.py::_pair_strata_reading`, the `bounded` branch.

# FINDING — the cross stratum's bounded branch stated a bare number, and no artefact on disk could reach it

Found by driving the capabilities door with the first run that carries
`method_skill.fixed_horizon.pair_strata`. Not my block — it landed this morning at `2df665040`,
closing the attribution item — and my run is the first thing that could execute half of it.

## The defect

`_pair_strata_reading` composes the sentence beside the estimand. Two branches:

| branch | fired by | what it said |
|---|---|---|
| withheld | no interval on the cross stratum | *"...whose own concordance is **withheld** here for want of an interval computed on this run's own signals"* |
| bounded | the run supplies one | *"...which read **0.2686**: in 73% of departure-against-survivor pairs the arm had given the DEPARTURE the higher margin."* |

The bounded branch quotes the number **and not the interval**, while the spread that made the
branch reachable at all — `null_95_low` 0.4105, `null_95_high` 0.5887 — sits unused in
`cross_null` three lines up. A concordance reaching a reader without the bound its own pairs earn
is the exact rule `_stratum_figure` holds the *payload* to, four lines above in the same file, and
the same rule `_horizon_leg_published` and the page's `row()` hold the bridge legs to. The
sentence was the one place it was not enforced.

**The refusing branch was fail-closed and the stating branch was not.** That is the harder half to
notice: a refusal gets read twice and a number looks finished.

## Why it shipped invisible, and this is the general part

`pair_strata` landed on 2026-09-09 and **every artefact on disk predated it**. So
`generate_value_arms_data._skill_pair_strata`'s identity fallback served the **withheld** branch to
every reader on every feed, and nothing in the tree could execute the other one. A block landed
with its own controls, published fail-closed, correct in the payload — and half its prose had never
run anywhere.

The page's own door control caught it in one line the moment a feed could reach it:

```
site/test_the_baseline_comparison_reaches_the_reader.py::
test_the_attribution_of_the_inversion_reaches_the_reader_BESIDE_the_figure
E  AssertionError: the cross stratum's number is on the page without the interval that let it be published
```

That control was written correctly and had never had a feed that could make it fire. **A control
green against every artefact in the tree is not evidence about a branch no artefact reaches** — and
"green today" and "reachable today" are the two facts a producer landing ahead of its first run
cannot tell apart on its own.

## What landed

`_pair_strata_reading` takes the cross stratum's own spread and states the interval with the
number, on its own pair count so a reader cannot mistake it for the estimand's:

> *"The departure is carried by the 4,588 cross pairs, which read 0.2686 against the 0.4105–0.5887
> a no-information signal reaches on this stratum's own 4,588 pairs: in 73% of
> departure-against-survivor pairs the arm had given the DEPARTURE the higher margin."*

A third branch is added and it is the fail-open one level down: a spread that says
`available: True` and carries no interval now **withholds** rather than stating a number against
nothing. Before this it would have fallen through to the bounded branch and printed the figure
bare, which is the same defect wearing a different hat.

**Three mutations, each run and reverted, each killed** — restore the bare bounded branch; fall
through to it when the interval is absent; quote the *estimand's* interval beside the cross figure
(the borrowed-bound error the whole block exists to prevent). Reachability over all three branches
is asserted before any of them, because a composer that withheld on every input would satisfy every
"does not state a bare number" assertion anybody could write.

## What is not claimed

The payload was never wrong — `_stratum_figure` withheld correctly throughout, and every control on
it was right. This is the sentence only. And the fix is in the producer, so **it reaches a reader
only through a run that carries it**: the artefact produced at 13:15Z today carries the old
sentence, and `..._20260909c.json` is the re-run that carries the repaired one.

Severity **LATENT**: nothing on the live page is wrong today, because the live feed is on the
identity fallback and takes the withheld branch. It is one promotion away from mattering, and that
promotion is deferred for a different reason —
`SEAT_FINDING_THE_NOISE_FLOOR_CARRIES_NO_BOOK_IDENTITY_SO_THE_PAIRING_RULE_IS_A_STAMP_PROXY_WRONG_IN_BOTH_DIRECTIONS_2026-09-09.md`.
