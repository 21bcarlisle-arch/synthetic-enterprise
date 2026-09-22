# WORKER RESULT — the floor rows now carry their rosters, and the null that graded them was borrowed from another instrument

**Severity:** RECORDED · **Lane:** A_strategy_governance

Lane: A_strategy_governance · 2026-09-19 · autonomous worker, Lane 0
Claim: `floor-rows-carry-their-scored-decisions`
Subject: `tools/run_value_cycle_ab.py`, `tools/generate_value_arms_data.py`,
`tests/tools/test_value_cycle_ab_noise_floor.py`, `tests/tools/test_generate_value_arms_data.py`

The one line named as owed in
`docs/staging/done/SEAT_RESULT_THE_AUC_DOES_NOT_CLEAR_ITS_OWN_NULL_AND_THE_RANK_LEG_COSTS_FOUR_ROSTERS_AGAINST_THE_MONEY_LEGS_HUNDRED_AND_TWO_SEEDS_2026-09-19.md`
§2, filed there as the next item and deliberately not done in that turn.

---

## What landed

**The producer carries the roster.** The floor seed-row writer in
`run_value_cycle_ab.noise_floor` recorded `discrimination_auc`, `auc_population` and
`auc_scored_share_of_priced` off each seed's `belief_vs_outcome` and dropped `scored_decisions`.
It now writes the roster too — `account`, `term_start`, `believed_p_retain`, `retained`, per
decision, taken from the run block's own list rather than rebuilt here.

**The consumer grades each row by that roster.** `_auc_rows` now asks `_auc_roster_null` for the
row's ruler. Where the row carries a roster that reproduces its own published AUC, the ruler is
the **tie-corrected** Mann-Whitney null over that roster:
`[(N+1) - Σ(t³−t)/(N(N−1))] / (12·n1·n2)`. Where it does not, the ruler is the untied closed form
the page has always used, with the reason on the row.

**Three states, never two.** `own_roster`, `no_roster` (every artefact written before today), and
`disagrees` — a roster that does not reproduce its row's AUC or its row's counts. The third is a
defect and not an absence: one is a producer that predates the field, the other is two
implementations that have come apart, and a two-state summary would bury the second in the first.
`nulls_from_their_own_rosters` publishes the count in all three, so a page reading a pre-field
artefact says so rather than going quiet about which ruler it used.

## The borrowed ruler this retires, stated plainly

`_auc_against_its_own_null`'s own docstring recorded the closed form being validated against a
roster in `value_cycle_ab_s1_three_arm_20260918.json` — **a different instrument, a different
run**. That is the two-artefact mispairing this module refuses everywhere else
(`_auc_against_the_money_legs_price` refuses it by name in the block immediately above), arriving
through the one door nobody had looked at, because the floor producer threw away the only evidence
that could have closed it. No floor artefact on disk carried a roster, for any seed, at any
commit.

**Confirmed on that same three-arm roster, as a check on the new code path rather than a reuse of
it.** 104 decisions, 60 retained / 44 departed, 83 distinct beliefs:

| | value |
|---|---|
| AUC recomputed from the roster | 0.5566287878787879 |
| `discrimination_auc` as published | 0.5566287878787879 |
| tie-corrected null sd (new) | 0.0575517293614433 |
| untied closed form (old) | 0.0575707733089798 |
| tie correction to the null **variance** | 0.066% |

The seat result of 2026-09-19 §3 derived 0.057552 and "0.066%" independently, by 200,000-shuffle
Monte-Carlo permutation. The closed form reaches the same two figures from the roster's tie
structure. **Ties are immaterial on this belief** — which is a result, not a reason the correction
was not worth making: it is the first time anything on disk could establish it for a floor row,
and the branch fails closed the day a belief with a coarser grid arrives.

## The prediction, written before it was run, and the answer

**Nothing on the published page moves.** Every row of the twelve-seed next12 family predates the
producer field, so all twelve fall back to the untied form. Measured: mean 0.5628958676569616 at
**1.0840310412082572** null SDs, **0 of 12** clearing — byte-for-byte what the page carried this
morning, and `graded_by_their_own_roster: 0`. A ruler repair that silently moved a published
verdict on an artefact it cannot have re-measured would be the defect and not the fix. The reading
changes when a run carrying rosters lands, which is the correct time.

**A leg pins that prediction** (`test_the_published_family_on_disk_is_unmoved_by_the_roster_repair`)
and it is keyed to the property — the on-disk family reports zero own-roster grades — not to
today's answer, so it goes red if a later artefact quietly starts claiming a roster it has not got.

## The silent failure that was one line away

`closed_form_agrees_with_the_exact_null` asserts the closed form against `_auc_null`'s exact
enumeration within 0.005. **`_auc_null` models no ties and says so in its own docstring.** Pointing
that leg at the new tie-corrected `null_sd` would have gone on printing `true` for ever, on every
real family, about a comparison it was no longer making — the tie term moves the sd by ~0.03% on a
real belief, two orders of magnitude inside the tolerance. So the row carries **both** rulers:
`null_sd` is what every distance is stated in, `null_sd_untied` is what the enumeration is graded
against. Each ruler checked against the thing it is a ruler for.

The control for it is exercised on a deliberately heavy-tied 40×40 fixture where the two rulers are
**0.017 apart** against the 0.005 tolerance — a fixture sized to the real 0.07% correction would be
a control that cannot fail. A twelve-decision version was tried first and red for the wrong reason:
at 36 ordered pairs the discreteness of the exact null is itself larger than the tolerance, so the
enumeration agreed with neither form. That is recorded on the fixture.

## Controls, each mutation run and reverted

Mutations were applied **in memory** — the module source patched and exec'd as a second module —
never to the shared tree, because other lanes are reading these files right now.

Producer (`tests/tools/test_value_cycle_ab_noise_floor.py`, 3 legs):

| mutation | leg that red |
|---|---|
| drop the key entirely | carries-the-roster |
| narrow to the three keys the direction literally named (drop `term_start`) | term-half-survives |
| write `[]` instead of `None` where no belief was measured | fails-closed |
| keep only the retained side of the roster | carries-the-roster |

Consumer (`tests/tools/test_generate_value_arms_data.py`, 6 legs):

| mutation | leg that red |
|---|---|
| always use the untied form | tie-corrected-from-own-roster |
| grade the enumeration against the tie-corrected sd | untied-stays-for-the-enumeration |
| accept a roster without checking it reproduces the row's AUC | disagreement-refused-by-name |
| accept a roster whose counts contradict `auc_population` | disagreement-refused-by-name |
| collapse `disagrees` into `no_roster` | the-page-counts-the-bases |
| drop the tie term from the variance | tie-corrected-from-own-roster |
| narrow the null even when the roster disagrees | disagreement-refused-by-name |

**Every mutation fired, and each fired the leg written for it** rather than a different one.

## Two judgement calls, named

1. **Four keys, not the three the direction named.** `term_start` is on the row because the roster
   is keyed by `(account, term_start)`: one account renews many times, so an account-only row makes
   two distinct decisions indistinguishable and a reader counting rows per account reads a
   duplicate where there is a second renewal. `chosen_margin_gbp_per_mwh` — which the run block
   does carry — is dropped: it is the arm's price, neither the belief nor the outcome, and no null
   needs it.

2. **The fallback is the wider ruler, and the direction is stated.** Ties can only shrink the null
   variance, so a row that cannot be graded by its own roster keeps a reading that is harder to
   clear, never easier. `what_a_fallback_costs` says so on the page, because a fallback whose
   direction is not stated is a fallback a reader has to assume went the flattering way.

## The duplicate-work check, decided

The draw flagged `value-arms-error-bar` as possibly this work under another name, on the ground
that it already holds `tools/generate_value_arms_data.py`. **It is genuinely different work on the
same subject, and the claim is carried on rather than disposed.** That claim is the error-bar work
of the seat result above — landed at `e00bbac25`, which moved `AUC_FAMILY_FLOOR_PATH` to the
twelve-seed family and added the per-seed bound, the pooled bound and the price of a sign. This
item is the line that result filed as **owed and deliberately not done in that turn**, in its own
§2. Disposing it under the other id would have retired an owed item nobody had done.

## What is now unblocked, and what is not

The rank leg was priced at about four independent rosters against the money leg's 102 seeds. That
price is unchanged. What changes is that **the next floor run produces a reconstructible answer**:
whatever unblocks the route — the ruling on `EP17_varied_population_draw`, or anything else — the
producer already carries the field, so the run does not have to be paid for twice. This project has
paid seventeen hours of box time twice for getting a producer right after the run rather than
before it.

**Not done, and not claimed:** the page does not yet render which ruler graded it.
`nulls_from_their_own_rosters` is in the feed and no renderer reads it, so a reader still cannot
see from the page that today's twelve are all on the untied fallback. That is a reader-side line on
`site/capabilities/index.html` plus a leg in
`site/test_the_baseline_comparison_reaches_the_reader.py`, and it is the next item on this claim.

## What would refute this

A floor run that lands rows carrying rosters whose per-seed tie-corrected null comes out materially
**below** 0.058 — which would mean the untied form has been overstating the bar and the twelve-seed
verdict was harder on itself than it needed to be. Nothing here predicts that: on the one real
roster measurable today the correction is 0.07% of the variance. Or a `disagrees` row on a freshly
written artefact, which would say the writer and the run block have come apart and would be a
producer defect rather than a reading.
