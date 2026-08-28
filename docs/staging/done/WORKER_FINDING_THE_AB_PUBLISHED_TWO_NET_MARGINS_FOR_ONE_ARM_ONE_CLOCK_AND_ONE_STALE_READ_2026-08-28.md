# [WORKER FINDING] The value-cycle A/B published two net margins for one arm — one clock and one stale read, GBP 39,962.17 apart

**Severity:** LATENT · **Lane:** H_harness · **Raised:** 2026-08-28 · **Rank:** consolidated, no independent rank

LATENT and not BLOCKING: nothing was wedged, the artefact wrote and the run published. It was a
published financial figure on the wrong clock, which is an R14 defect in the accounts and not an
obstruction to any lane.

**One line:** `docs/observability/value_cycle_ab_s1_three_arm.json` published
`control_arm.total_net_gbp` = GBP 113,282.62 and
`gross_to_net_bridge.control_arm.net_margin_gbp` = GBP 153,244.79 for the SAME arm on the SAME
run, GBP 39,962.17 apart, under a basis label claiming both came from the settled records.

## Class registration

Belongs to `figures_on_a_superseded_clock`.

**This document is written after its own repair, and that is deliberate.** The defect was found
and fixed inside a Lane 0 claim on 2026-08-28 (commit `4d935cb39`), so it existed only as a
commit message. When the SECOND instance of the identical shape appeared the same day on the
live site
(`WORKER_FINDING_THE_PUBLISHED_TREASURY_IS_ON_A_SUPERSEDED_CLOCK_BESIDE_A_REALISED_NET_MARGIN_2026-08-28`),
R10 required registering the class rather than fixing the second file — and a class needs its
instances as documents, not as commit archaeology. Writing it up is what makes the family
countable. It is filed at the severity it had when it was found; the repair is recorded below
under *What repaired it*, and the class's remaining obligation is carried by the second
instance, not by this one.

## Observed, with evidence

`docs/observability/value_cycle_ab_s1_three_arm.json`, as published before the repair:

```
control_arm.total_net_gbp                            = 113282.62
gross_to_net_bridge.control_arm.net_margin_gbp       = 153244.79
```

Difference: GBP 39,962.17. Both were published under a basis label stating they came from the
settled records, so a reader had no way to tell that only one of them did.

## The mechanism, traced to the code

`simulation/run_phase2b.py:2506-2510` folds `total_gross`, `total_capital`, `total_bad_debt`,
`total_net` and `final_treasury` out of `all_records` at the end of the settlement loop.
`simulation/run_phase4c_on_phase2b.py` then mutates `phase2b["all_records"]` IN PLACE:

* `apply_emergent_bad_debt` replaces the flat-rate `get_bad_debt_rate()` provision in each row
  with the arrears model's realised write-offs;
* `apply_debt_recovery` credits back the DCA proceeds;
* `simulation/arrears_engine.py:604-608` and `:709-710` carry the whole correction forward
  through every later row's `treasury_cash_balance_gbp`.

Nothing refreshed the scalars. The arm blocks read the frozen scalars; the bridge walked the
mutated rows. The gap is the bad-debt line to the penny — GBP 46,428.5849 provisioned against
GBP 6,466.41 realised.

There is no *banked* clock in this world, and inventing one would have been the comfortable
wrong answer: `treasury_cash_balance_gbp` is a running total of settled net margin, which is
exactly why `final_treasury` was 250,000 plus the frozen net.

## What repaired it

Commit `4d935cb39`, `tools/run_value_cycle_ab.py`:

* `realised_metrics` sums net, bad debt and treasury from the rows and keeps the frozen scalars
  as `provisioned_*` under their own declared clock.
* `CLOCK_DEFINITIONS` is published once at the top of the artefact and each figure carries its
  clock in the block the reader is holding.
* `clock_audit` refuses an artefact publishing two net margins for one arm without a declared
  clock on each, or two figures sharing a clock that disagree. It reads the artefact's own
  labels, never the module constants that wrote them (R15 tautology), and fails closed on no
  definitions / no arms / one figure per arm. R15-proven by four mutations plus a null rung.

That repair was an INSTANCE fix, and it is why this class exists: it left
`saas/reporting/annual_report.py`, `saas/reporting/segment_report.py` and
`tools/run_frozen_baseline.py` reading the same stale names, and the second instance reached the
live site within the day.

## What the class repair added, and where the source fix landed

`simulation/settlement_clocks.refresh_settlement_scalars`, called by
`run_phase4c_on_phase2b` immediately after the last stage that mutates `all_records`: the bare
scalar names are re-derived from the rows and the settlement loop's fold is preserved under
`provisioned_*`. No consumer, present or future, can read a superseded value out of an
unprefixed name.

This artefact's own `provisioned_*` figures were re-pointed at those preserved names in the same
pass — left alone, they would have started publishing REALISED figures under a PROVISIONED
label, which is this class again in the file that documents it.
