# PB4: the Expert Hour re-take fails, and a disengaged household's elasticity is almost never consulted

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity` · **Claim:** `pb4-retake-the-expert-hour-on-the-drift-gradient-world` (Lane 0)

The blind Expert Hour was re-taken on the drift-gradient world, after `beb4f8533` (gradient),
`27d39e8a9` (re-capture), `f65cf9422` (D1 filed, D4 on the page) and `d24ba9703` (page republished).
**Verdict: FAIL, held at L2.** The three blockers from `789083280` are closed or filed. The reviewer
raised a different set. Two of those are new and buildable, and one of them goes to the claim itself.

## Premise, re-measured at draw

All three cited commits are ancestors of origin/main. The re-capture on origin is the post-`beb4f8533`
one (`docs/reports/pb4_departure_factors.json`, `"commit": "beb4f8533"`). The live claim the draw
flagged under this id belongs to this draw's own process. No rival seat or `surgical_land` is working PB4.
So the premise is live and the work had not been done.

## How it was run

- Packet: `tools/blind_review.py --packet`, with the plain words RESTATED to cover the drift gradient,
  the emerged pattern and the D6 statement. The persona was unchanged.
- One fresh fork, given no tools and no files. A first fork received a literal placeholder instead of the
  packet; it saw nothing, wrote nothing to the ledger, and was discarded.
- 16 questions came back, 9 of them disqualifying. They are recorded in
  `docs/observability/blind_review_ledger.jsonl`, and `--audit` reports the blindfold intact in all 8
  recorded reviews. The reviewer did not raise independence.

**A correction, kept beside the claim.** The packet said *"about 65% of fixed-term ends roll to the default,
31% re-fix and 4.5% leave."* That is D1's figure from the earlier live run: 13/101 choosers leaving,
2017-21. The current capture says otherwise. Of the households that reached the renewal roll in
2017-21, **18 of 62 left (29%)**. At the ~35% engagement share, that gives about **65% roll, 25%
re-fix and 10% leave**. The two runs disagree on P(leave | chose) by more than 2x, and nothing has
reconciled them. The ledger entry keeps the packet as it was shown. *(Reconciled below: both runs give
18/62. 13/101 was a miscount. With the 6 declined fixes counted as staying on the default, the split
is 68 / 21.5 / 10.2.)*

## The nine disqualifiers, graded against the tree

**R1. Departures per household (0.55) against the switching series (1.0-1.3). OPEN, a page defect.**
The reviewer divided by the wrong exposure, and the page invited it. 0.55 is per household **over its
time on the book**; the book grows through the run. It is not per account over ten years.
`fit_whole_book` (C2) fits each year's departure level to DESNZ QEP. But the page publishes no
per-household-year rate, so a reader cannot tell the two quantities apart. The fix is to publish that
rate beside the published annual series.

**R2/R3. Re-fix against leave among choosers, and term-end leave in 2017-19. OPEN, unidentified, already filed.**
The current capture has 71% of choosers staying, at the edge of the reviewer's 50-70%. Term-end leave
in 2017-19 comes out at about 10% (13 of 44 choosers left × ~0.35), below the reviewer's 20-35%.
Neither side of that comparison is a published number:
- φ (`EXTERNAL_SHARE_OF_ACTIVE_RENEWALS`) is a declared `None`
  (`gb_domestic_switcher_split_cim_2022_2025.md` §3).
- The EFTC arm is a lower bound (D1, `f65cf9422`).
- The unconditional small-supplier split is the director question already filed in
  `first_renewal_departure_rate_small_gb_supplier.md`.

The reviewer's numbers are a prior, not evidence. The run-to-run disagreement in the correction above
is the actionable part.

**R4. Disengaged-to-active ratio 0.61, against an expected 0.1-0.4. OPEN, knowledge.** The reviewer's
comparison is "never switched" against serial switchers, and both groups are defined by the outcome:
a never-switcher's departure rate is zero by definition. The world's types are dispositions. The one
sourced gradient on a non-outcome measure is CMOL's non-readers (≤0.43-0.54x on drift, at fixed
tenure). No published multi-year ratio on a disposition measure is on file. That is the knowledge pass.

**R5. Why 0.61 is above both route ratios. CLOSED HERE, BY ARITHMETIC ON THE PUBLISHED FEED, and it is a finding.**

| | SVT-years per household | drift hazard per cap period | drift departures per household | renewal-route departures per household |
|---|---|---|---|---|
| active | 124.2/56 = 2.22 | 0.0288 | ≈0.32 | 55 × 0.339 / 56 ≈ 0.33 |
| disengaged | 112.7/25 = 4.51 | 0.0138 | ≈0.33 | ≈5 × 0.35 / 25 ≈ 0.07 |

The disengaged spend **2.03x** as long on the default tariff. At **0.48x** the hazard, their drift
departures per household come out equal to the active ones (≈0.97x). **So the sourced drift
gradient from `beb4f8533` cancels out per household, and the whole 0.61 comes from the renewal gate
(≈0.21x).** The mechanics are right: in the real market the disengaged also sit on the default
longer. But the page shows the gradient without the exposure that undoes it. The decomposition belongs
on the page, next to R1's denominator.

**R6. Collective-switch reproduction. OPEN, BUILDABLE, AND IT GOES TO THE CLAIM.**
`departure_risks.svt_inertia_hazard` takes tenure, the market multiplier and the archetype, with **no
saving and no elasticity term**. Engagement is consulted only at a fixed-term end. So a disengaged
household's elasticity weight reaches behaviour only on the renewal roll: **5 decisions across 25
disengaged households over the whole run**. The headline *"a disengaged household is not assumed to
be price-insensitive"* is true of the weight, but it is almost never observed in the world's
behaviour. In this world, a frictionless offer to a dormant default-tariff household (Ofgem's 2018
collective switch: about 22% against about 1-2% in control) has no route to land on.
`how_households_respond_to_supplier_contact.md` §4 item 4 already lists *"the woken share for
default-tariff stock between boundaries (CMOC, collective switch)"* as unbuilt. That is the build,
and it gives the separation something to show beyond the weight itself.

**R7. When fixed deals are treated as unavailable; SoLR. START DATE OPEN, knowledge; SoLR CLOSED.**
`FTC_WITHDRAWAL_WINDOW` begins 2022-01-01. The end date is sourced (Ofgem SotM 2025, "re-emergence in
H2 2023"). **The start date has no source written beside it.** The reviewer puts the withdrawal from
about September 2021. In the capture, the 9 renewal decisions in 2021 (3 left) may include boundaries
where no deal existed. SoLR moves sit in `_CRISIS_FLOOR_RATE` as a non-choice floor and are not
engagement.

**R8. What the felt saving is measured against. MOSTLY CLOSED IN THE TREE.**
`churn_position_multiplier` works in pounds on the household's own bill, against a market reference
that varies over time. Whether that reference is the best available offer, rather than a market
average, and whether a comparison site's consumption figure should replace the household's own, were
not graded in this pass.

**R9. Prepayment debt barrier. OPEN, the residual already named under D7.** The Debt Assignment
Protocol covers prepayment debt below GBP 500 only. The world treats every prepayment household as
unblocked. The access/engagement split carries a statement of its direction of bias (D6), not a model.

## The run-to-run disagreement: RECONCILED. 29% is right; the 13% was a miscount, not a second run

*Claim `pb4-two-runs-disagree-on-the-renewal-roll-leave-share`, 2026-10-07.* Both figures were
re-derived from their artefacts. The two runs do not disagree.

**What 18/62 counts (the capture, `docs/reports/pb4_departure_factors.json`).** It counts every call of
`roll_lifecycle_event` in 2017-21. That is one row per ROLLED renewal decision, on both legs (57
electricity, 5 gas), across 39 billing accounts. The rows are the whole book, before
`tools/engagement_separation`'s resi-on-the-live-roster filter. That filter takes the whole-run count
to 13/58, and the 2017-21 subset to fewer still. World `cdba75ebb9197b33`, captured at `beb4f8533`,
default seed. 18 left.

**What 13/101 counted (D1 in `789083280`, "the live run").** No artefact was named beside it. It reproduces
exactly from any `docs/reports/run_output_*_2026100[67]*.json`, e.g. `c6b8217d1` at 16:17Z on
2026-10-06, the latest before D1 was written. The filter that gives it: `customer_events`, 2017-21,
`commodity == "electricity"`, `is_active_renewal` true, **with every `departure_occasion`
included**. The 101 are:

| occasion | rows | can leave here? |
|---|---|---|
| `renewal` (rolled) | 49 (13 left) | yes |
| `svt_conversion` | 39 | **no**: no roll, `realized_churn_probability` 0.0 by construction (`customer_events.svt_conversion_event`) |
| `declined_fix` | 13 | rolled on a fixed-to-fixed term only; most here are conversions off the default, with no roll |

So the 101 is the electricity leg's term-boundary rows, not its choosers. Its denominator is about
half rows that cannot depart. The `svt_conversion_event` docstring already says a reader whose
denominator is rolled decisions must *"select by occasion (or by `departure_rolled`) and exclude this
by name"*. D1 then multiplied 13/101 by P(active) 0.351 to get 4.5% leaving. That applies the
engagement gate a second time, on top of a denominator that was not choosers either.

**The live run, counted the capture's way, is the capture.** Rolled decisions only
(`departure_occasion == "renewal"` or `departure_rolled`), both legs, 2017-21, in the run at
`f07af3845`: **18/62**, row-for-row the same (customer, date, outcome) keys as the capture, and the same
39 accounts. The years match too: 23 / 13 / 8 / 9 / 9 for 2017-21. Every run output on 2026-10-06/07
gives the same 18/62, which says the renewal roll does not move with the drift gradient.

**Prediction, kept beside the result.** Before re-deriving, I expected a world change between the two
artefacts to explain at least part of the gap. That was wrong. None of the gap is world: all of it is
counting.

**The corrected split at a fixed-term end** (2017-21, P(active) 0.351 as D1 used). Of the 62 choosers,
18 left, 6 declined a fix priced above the default and so stayed onto it, and 38 re-fixed. The world
therefore sends **about 68% to the default, 21.5% to a re-fix with us and 10.2% out**. That replaces
both D1's 65/31/4.5 and this finding's own 65/25/10, which counted the 6 declined fixes as re-fixes.
Against the EFTC control arm (81/14/6, a lower bound on re-fix per D1 `f65cf9422`), the re-fix gap
narrows from about 2x to about 1.5x, and the external share now sits above the arm's. The figure
13 of 44 for 2017-19 under R2/R3 is re-derived unchanged at this counting.

**What this does to R6 (`f71fcc176`).** R6 can now be graded against one figure. Nothing in R6 was
built on 13/101.

**Not done here: the per-household-year rate beside DESNZ QEP (R1).** It was not cheap enough to do
honestly in this turn. Its denominator, household-years on the book, has to be stated before it is
divided, and it is a page change with a door test. It stays item 2 below.

## Next, in order

1. **R6:** the woken share for default-tariff stock between boundaries. This is a world build, sourced
   from the collective-switch and CMOC trials, and the only thing that gives the disengaged's elasticity
   a route to behaviour.
2. **R1 + R5 on the page:** a per-household-year rate beside DESNZ QEP, and the exposure
   decomposition. Both are cheap and use data already in the feed.
3. ~~**The run-to-run disagreement** in P(leave | chose): 29% in the capture against 13% in the live run.~~
   Reconciled above: 18/62 in both. The 13/101 was a denominator of term-boundary rows, not choosers.
4. **Knowledge:** the start date of `FTC_WITHDRAWAL_WINDOW` (R7), and a multi-year switching ratio on
   a disposition measure (R4).

Then re-take the Expert Hour.
