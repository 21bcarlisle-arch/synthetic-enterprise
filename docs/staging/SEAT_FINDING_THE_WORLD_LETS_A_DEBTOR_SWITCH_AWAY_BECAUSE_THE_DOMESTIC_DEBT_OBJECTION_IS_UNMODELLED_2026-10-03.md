# The world lets a debtor switch away, because the domestic debt objection is unmodelled

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

## What is true in the published record

A GB supplier may object to the transfer of a domestic credit customer who owes it money, and an
objection legally stops the transfer (Ofgem, *Decision on review of domestic objections*, 2016;
summarised in `docs/market_research/svt_drift_by_payment_behaviour.md` §"Domestic debt
objections"). So "worse payment record -> less able to leave" is ESTABLISHED in direction. The
2016 impact assessment's objection rates by debt band are NOT extracted: both PDFs returned
compressed streams (same file, line 55).

## What the world does instead

No code path in `simulation/` blocks a household's departure on its own arrears. The departure
draw is the churn roll against the world's P(stay), whatever the account owes, and on departure
`simulation/arrears_engine.compute_emergent_bad_debt` writes off the unpaid balance at close.

## Why it matters now

The value arm's worst seed (61002, selection -GBP 12,726) is dominated by one account,
PROS-2016-0098, which ran to about GBP 12k of arrears. The 2026-10-03 pricing fix made arrears
move the arm's bad-debt cost: money owed is priced at Centrica's live provision rate if the
household stays, and at the final-bill rate if it leaves. Both of the company's leave-branch
beliefs, the churn hazard and the final-bill write-off, assume a debtor CAN leave. Under the real
objection right, a domestic credit debtor mostly cannot, so the world currently rewards a pricing
belief a real supplier would not hold. That is a fidelity gap on the world side, to be decided
blind to company results, and not a reason to change the company's belief.

## What closing it needs

1. The objection rate by debt age or amount: extract the 2016 impact assessment's tables (the
   fetch failed on compression, not on access).
2. Who it applies to: domestic credit (not prepayment, where the Debt Assignment Protocol moves
   the debt), and the 28-day threshold.
3. A world-side draw that blocks a departure the objection would stop, with the household staying
   on supply.

Until then, read any A/B result that turns on a debtor's departure as carrying this gap.

## Update 2026-10-03 (delivery seat): step 1 is done; the rates are extracted

Both Ofgem 2016 PDFs extract cleanly with `pdftotext -layout`; the earlier "compressed streams"
failure was tooling. Full tables: `docs/market_research/domestic_debt_objection_rates_gb.md`.
- **Indebted credit customer who attempts to switch: about 28-30% blocked** (Ofgem's own ratio,
  ~170k blocked vs ~430k allowed a year, 2013-2015).
- **Statutory threshold:** debt unpaid 28 days after written notice.
- **Prepayment debt** moves with the customer under the DAP (GBP 500 from 2016), so the block does
  not apply there.
- **About half of blocked customers repay.** Most blocked customers are still with the supplier a
  year later. That is a derived composite and is labelled as one.

Applying 2013-2015 rates to 2016-2025 (including after CSS) is a named gap: no later figure is
published.

Why this is now load-bearing (stated plainly, because the world must change for fidelity and
not for results): in the 2026-10-03 capped-learned probe runs, the value rule's whole remaining
gap to the best flat price in hindsight is one 2017 decision, this account. The finding was
filed earlier the same day on the published law alone. That rule is the reason to build the draw.
The result only sets its priority.

## Resolved 2026-10-03: the world draws the SLC 14 objection at the renewal roll

`simulation/debt_objection.py`, wired into `customer_events.roll_lifecycle_event` and the
`run_phase2b` renewal call site.

- **Rate.** `DEBT_OBJECTION_BLOCKED_SHARE = 170,000 / (170,000 + 430,000) = 0.283`, computed from
  Ofgem's two counts. It is not typed in as a number.
- **Who.** The predicate is `WorldDebtBook.owes_objectionable_debt`. It is true for a domestic
  household with a bill on a credit-meter leg that is still unpaid more than 28 days after its due
  date at the renewal date. It reads the triad's world-side `PeriodRecord` truth, never the
  company ledger. Prepayment is never eligible.
- **Effect on the roll.** P(stay) becomes `p + (1 - p) * share`, inside the returned
  `effective_retention_probability`, so `tools/decision_probe.py` sees it. The block takes the
  bottom `share` of the departure tail on the same roll, and `roll <= P(stay)` still decides the
  outcome. The event carries `debt_objection_eligible` and `departure_blocked_by_debt_objection`.
  Both are on the company-wall guard.
- **Switch.** `SE_DEBT_OBJECTION=0` turns it off. It is on by default because it is the published
  law.

**Measured, full default run (to 2025-06-07), ON vs OFF, single seed, about 24 min and 5.2 GB
each:**

| | OFF | ON |
|---|---|---|
| rolled renewal decisions | 83 | 84 |
| decisions with an eligible debtor | 0 | 47 (56%) |
| departures blocked | 0 | 6 |
| renewal departures | 28 | 23 |
| SVT-route departures | 46 | 48 |
| churned billing accounts | 74 | 71 |
| total bad debt (GBP) | 23,154 | 23,769 |

> **Re-graded 2026-10-09 on the corrected world (23fca0567, 54dbd5650):** the ON leg only, at origin `46951a0ee`, same default seed, `PYTHONPATH=<tree> python3 -c 'from simulation.run_phase2b import main; r = main()'` counting `customer_events` with `debt_objection_eligible` (52 min wall on a contended box, queued behind landings; not the minutes tier). **Decisions with an eligible debtor 47 of 84 (56%) -> 27 of 110 (25%); departures blocked 6 -> 1.** Churned billing accounts 71 -> 116, SVT-route departures 48 -> 74, and `total_bad_debt` GBP 23,769 -> 58,007 are NOT comparable: the book is a different size (110 rolled decisions, not 84; the settlement budget and other world changes landed since `bf0d37c2f`), so the arrears correction is one of several variables and I cannot attribute those moves to it. The short window the control uses (`run_phase2b(report_end="2017-06-30")`, 88 s): eligible 8 of 15 (2026-10-03) -> 6 of 15 (2026-10-04, cure) -> **2 of 16, 0 blocked**. The 28.3% blocked share is Ofgem's ratio and does not move; what moved is its reach. 25% is still above the rough 10-15% reading of Ofgem's counts, so the reach stays an upper bound, but it is now within about 2x rather than 4-5x.

**The eligible share is not credible. Read it before using any of these numbers.** In this world,
56% of renewal decisions carry an objectionable debt. Ofgem's counts give about 600k indebted
switch attempts a year. Electricity switches were about 4.8m in 2016. That rough comparison
(different years, and fuels de-duplicated on one side only) puts real indebted attempts on the
order of 10-15% of switches. The reason is upstream of this draw. In the triad's truth, a failed
or disputed bill is never paid afterwards, because re-presentation and arrangement paydown are not
modelled. So once a debt is 28 days old it stays objectionable for the rest of the run. Real
blocked customers repay about half the time (IA §1.38). Until repayment is modelled, the block's
reach here is an upper bound.

**Level.** `departure_level_anchor` is fitted to published realised switching. That record
already nets out blocked switches, so with the block on the world departs below the record until
the anchor is re-fitted. The re-fit was not done here; it is a separate decision. The world digest
covers only the anchor values, so it does not move. 8 `test_switching_rate_commons` controls are
red, and they are red identically at the HEAD this was built on, so this change did not cause
them.

**Gaps still open:**
- The 2013-2015 rates are applied to 2016-2025, including after CSS.
- The objection is the losing supplier's decision. This draw stands in for industry practice until
  EP12's CSS objection window lets the company decide it.
- C1b SVT-route exits are not blocked.
- There is no repay-and-leave-later route.
- `interface/contracts/registration_loss_seam.GAPS["failed_switch_outcomes"]` still says no failed
  switch exists. A blocked departure is now one, and that text belongs to the interface steward.
