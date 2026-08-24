**Severity:** BLOCKING · **Lane:** H_harness

# The published treasury-drawdown count is an artefact of re-sorting a running balance that was never a time series — 6,747 "events" in a year the treasury never drew down

**Found by:** the before/after diff of a real end-2019 report while folding the settlement book
to daily rows, 2026-08-24. Not looked for; the fold made the old figure impossible to reproduce
and the reason turned out to be that it should never have been produced.

## Observed, with evidence (R9) — measured, not read

`simulation/run_phase2b.py` accumulates settlement records **term by term**: it settles one
customer's whole contract term, appends it to `all_records`, then moves to the next customer.
`treasury_cash_balance_gbp` is a **portfolio-level running total** stamped onto each record as
it is produced, so it is meaningful in ACCUMULATION order and in no other.

`saas/reporting/annual_report.py` then sorts by `(settlement_date, settlement_period)` before
walking it into `_drawdown_events`. That sort interleaves balances produced at completely
different points in the term loop.

Run at `report_end=2017-12-31`, the same records, the same function, two orderings:

| year | records | drawdown events, ACCUMULATION order | drawdown events, SORTED order |
|---|---|---|---|
| 2016 | 199,522 | **0** | 0 |
| 2017 | 330,366 | **0** | **6,747** |

The published report prints the second column. Its own rendered output shows what those
"events" are — thousands of copies of one swing, each a penny apart:

```
Treasury drawdown events (>=10% threshold): 5611 -- £282,588.74 -> £250,962.13 (11.2%);
£282,588.75 -> £250,962.14 (11.2%); £282,588.76 -> £250,962.14 (11.2%); ...
```

That single line is **202,048 characters** in the 2026-08-24 end-2019 report. Three such lines
are two-thirds of the file's bytes.

## What is actually true

In accumulation order — the order the balance genuinely took — the 2017 treasury has **no
drawdown at all** at the 10% threshold. The number is not "too high"; the phenomenon it reports
did not happen.

## Why it is BLOCKING rather than latent

It is on a published surface, it is a risk figure, and it is wrong in the direction that
matters: a reader is being told this supplier's cash position collapsed by 11–24% thousands of
times a year. The RAG rating beside it (`GREEN = drawdown <25% | AMBER = 25-50% | RED = >50%`)
is computed from the same artefact.

## The repair, and its status: BUILT, DORMANT, NOT YET LANDED LIVE

`simulation/settlement_daily.py::TreasuryDrawdown` folds the drawdown during the run, in
accumulation order, and is landed with this finding — but **nothing calls it yet**. It is part
of the daily-settlement fold, which is deliberately unwired (see that module's docstring) until
one unexplained figure movement is diagnosed. So the published count is STILL the artefact
today; what exists is the instrument that will replace it, with the test that proves it
reproduces `_drawdown_events` exactly on a real path.

When the fold is wired, this figure MOVES — from thousands of events to the true count — and
that must be stated in the landing commit rather than left for a reader to notice.

What is NOT repaired, and is why this document stays open: **nothing checks that a balance
stamped in accumulation order is only ever read in accumulation order.** The same shape is
available to any future consumer that sorts `all_records` and reads a running total off it, and
there are other running totals on those records (`gross_margin_ytd_gbp`, `net_margin_ytd_gbp`,
`capital_costs_ytd_gbp`). Those have not been checked. The class fix is a control that names
running-total fields and refuses a re-sorted read of them (R10) — not built here.
