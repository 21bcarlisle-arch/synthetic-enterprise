# [WORKER FINDING] The published final treasury is on a superseded clock beside a realised net margin, and the site's own arithmetic is GBP 39,962.17 out

**Severity:** LATENT · **Lane:** H_harness · **Raised:** 2026-08-28 · **Rank:** after the current Lane 0 claim

LATENT and not BLOCKING because nothing is wedged: the run publishes, the site renders, and the
figure is internally traceable. It is a published financial figure on the wrong clock, which is
an R14 defect in the accounts and not an obstruction to any lane.

**One line:** `docs/reports/run_output_latest.json` publishes `total_net_gbp` re-summed from the
post-arrears rows and `final_treasury_gbp` read from the pre-arrears frozen scalar, so
`starting_treasury_gbp + total_net_gbp` does not equal `final_treasury_gbp` in the file the site
renders — and the gap is the same GBP 39,962.17 the A/B artefact was just repaired for.

## Class registration

This finding does not belong to any of the five consolidated classes
(`publish_gate_and_wedge`, `controls_that_cannot_fail`, `measurements_that_mirror`,
`uncommitted_and_orphaned_work`, `no_caller_and_never_runs`). It is a **published figure on the
wrong clock (R14)**, and it is filed live rather than archived because there is no class for it
yet and one instance is not a class. If a second instance of the same shape appears — a figure
re-summed from mutated rows published beside a sibling read off the frozen summary — that is the
point to register `figures_on_a_superseded_clock` and consolidate both.

## Observed, with evidence

`docs/reports/run_output_latest.json`, read 2026-08-28:

```
starting_treasury_gbp = 250000.0
final_treasury_gbp    = 363282.6171350135
total_net_gbp         = 153244.792035
total_bad_debt_gbp    = 6466.41
```

250,000 + 153,244.792035 = **403,244.792035**, not 363,282.617. The published treasury is
GBP 39,962.17 below its own starting balance plus its own net margin.

`site/data/supplier.json:9` carries `"final_treasury_gbp": 363283.0` — so this is on the live
surface, not only in an intermediate file. `site/data/agent_status.json:146` carries the same
figure as `treasury_gbp`.

## The mechanism, traced to the code

`saas/reporting/annual_report.py`, the block that builds the run output:

```
915:  "starting_treasury_gbp": phase2b["starting_treasury"],
916:  "final_treasury_gbp":    phase2b["final_treasury"],          # FROZEN SCALAR
...
920:  "total_bad_debt_gbp":    sum(r.get("bad_debt_gbp", 0.0) for r in all_records),   # ROWS
921:  "total_net_gbp":         sum(r["net_margin_gbp"] for r in all_records),          # ROWS
```

`simulation/run_phase2b.py:2499-2503` computes `total_net`, `total_bad_debt` and
`final_treasury` at the end of the settlement loop and returns them unchanged from line 2820.
`simulation/run_phase4c_on_phase2b.py:290-306` then mutates `phase2b["all_records"]` IN PLACE:
`apply_emergent_bad_debt` replaces the flat-rate `get_bad_debt_rate()` provision in each row
with the arrears model's realised write-offs, `apply_debt_recovery` credits back the DCA
proceeds, and `simulation/arrears_engine.py:604-608` carries the whole correction forward
through each later row's `treasury_cash_balance_gbp`. Nothing refreshes the three scalars.

So lines 920 and 921 see the corrected world and line 916 does not. The mutated rows are
internally consistent: `all_records[-1]["treasury_cash_balance_gbp"]` would be 403,244.79, which
is exactly `starting + total_net_gbp`. Only the scalar is stale.

This is the same defect, in the same run dict, that
`WORKER_FINDING`-adjacent Lane 0 work repaired inside `tools/run_value_cycle_ab.py` on
2026-08-28 (commit message: *"the two net margins the A/B published for one arm are one clock
and one stale read"*). The A/B was one consumer of those scalars. `annual_report.py` is the
other, and it is the one on the site.

## Why it is filed rather than fixed on sight

Repairing line 916 changes a **published headline figure** — final treasury moves from
GBP 363,283 to GBP 403,245 on the next run, and the treasury-change line beside it from
+GBP 113,283 to +GBP 153,245. That is a visible-surface change to a financial figure and wants
its own draw with R11 verification against the live page, not a drive-by inside a claim about a
different artefact (SELF_INTERRUPT_DISCIPLINE: queue by default).

`tools/run_frozen_baseline.py:60` is a third consumer of the same stale scalar
(`phase2b.get("total_net", 0.0)`) and should be dispositioned in the same pass — note it also
carries the fail-open default this project has already been bitten by.

## What done looks like

1. `final_treasury_gbp` published from the rows the rest of the block is summed from, with its
   clock declared beside it (R14) — not from `phase2b["final_treasury"]`.
2. `tools/run_frozen_baseline.py:60` on the same clock as whatever it is compared against, and
   its `.get(..., 0.0)` fallback removed.
3. A control that fails when a published run output's `starting + net` does not reconcile with
   its `final_treasury` — R15-proven by mutating one of the three. This is the invariant, and it
   is what makes the class fail automatically rather than this instance (R10).
4. R11: the live site fetched and the rendered treasury figure asserted to have moved.

## The trap to avoid

Do NOT close this by relabelling the treasury figure "banked". This world has no banked clock:
`treasury_cash_balance_gbp` is a running total of settled net margin, so
`final_treasury - starting_treasury` reproduces settled net exactly and measures nothing about
when cash arrived. A "banked" label here would be a name invented for a clock that does not
exist, which is the more comfortable of the two available wrong answers.
