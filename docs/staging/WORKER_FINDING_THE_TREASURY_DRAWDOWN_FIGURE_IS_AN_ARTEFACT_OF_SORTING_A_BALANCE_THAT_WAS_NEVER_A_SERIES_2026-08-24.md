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

---

## THE CLASS FIX IS BUILT AND WIRED — and it was sitting uncommitted (2026-08-24, worker tick, RUNG 1c blocking draw)

**Severity stays BLOCKING. The published figure is still the artefact**, and that — not the
missing class control — is what this document's own "why BLOCKING" paragraph is about. What has
changed is that the sentence above ("not built here") is no longer true.

`tools/running_total_order.py`, `tests/tools/test_running_total_order.py` and GATE 14 in
`tools/git-hooks/pre-commit` existed **only in the shared working tree**: 16 KB of control,
15 green R15 tests and thirty wired lines of hook, none of it in any commit, and therefore
enforcing nothing on anybody. That is the same class as
`docs/staging/CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md` — a control that is not
committed is not a control — so this tick's contribution is to LAND it rather than to build it
again.

### What the control actually does, and what it found

It names the four fields stamped as portfolio running totals during the term loop
(`treasury_cash_balance_gbp`, `gross_margin_ytd_gbp`, `net_margin_ytd_gbp`,
`capital_costs_ytd_gbp` — sourced from the producers, not invented) and refuses three AST
shapes of re-sorted read across `simulation`, `saas`, `company`, `sim`, `tools` and
`background`. Reordering is the defect; slicing is not, so an order-preserving `yr[-1][field]`
over a filtered bucket stays silent, which is how `run_phase2b` prints its own treasury.

It found **two instances this document did not know about**, both `treasury_end`, both a
published balance-sheet figure:

| module | shape | why it is wrong |
|---|---|---|
| `saas/reporting/annual_report.py` | comprehension-over-reordering | the named instance — the `_drawdown_events` fallback, still live for a pre-register run output |
| `saas/reporting/annual_report.py` | subscript-of-reordering | `max(yr_records, key=(date, period))` is the balance of the latest-DATED record, not the balance the year closed at |
| `saas/reporting/segment_report.py` | comprehension-over-reordering | the same defect, and worse: this copy has no register fallback at all, so it is unconditionally the artefact |

The `read-of-reordered-binding` shape has **zero** instances and is checked anyway, because a
control that only catches the shapes already committed is a control that can only ever be green.

### Why this does not discharge the finding

The three reads above are frozen as a shrink-only RATCHET with their counts, so a new one fails
and a second read of an already-frozen (module, shape, field) fails rather than hiding inside
the baseline. **Frozen is not fixed.** `--gate` ignores them so the tree is not held hostage;
the tool's default mode reports them and is the standing red. Each repair moves a published
figure, so each lands with its before/after measured (R14) rather than as a drive-by edit — and
the first of them is still blocked on the daily fold's one undiagnosed ~£14 ledger movement.

Discharging on the strength of a control that freezes the defect it names would be the
fail-open shape this project keeps catching: the class is now checkable, the instances are still
published, and the severity follows the published figure.

**What discharges this document:** the fold wired, `_drawdown_events` reading the register in
accumulation order with the fallback deleted rather than left reachable, the two `treasury_end`
reads repointed to `yr_records[-1]`, all three ratchet entries removed with their before/after
figures stated — and the published count moving from thousands of events to the true count, said
out loud in the landing commit rather than left for a reader to notice.

---

## TWO OF THE THREE ARE REPAIRED AND MEASURED — the ratchet is 3 → 1 (2026-08-24, worker tick, RUNG 1c blocking draw)

**Severity stays BLOCKING for the same reason as before:** the published drawdown count is still
the artefact, because its repair is the register and the register is still unwired. What has
moved is the OTHER defect the class control found — `treasury_end`, a published balance-sheet
figure, wrong in both report generators.

Both now read `yr_records[-1]` (accumulation order). Filtering preserves the order the balance
was accumulated in; re-sorting does not.

| where | was | now |
|---|---|---|
| `saas/reporting/annual_report.py` | `max(yr_records, key=(settlement_date, settlement_period))[…]` | `yr_records[-1][…]` |
| `saas/reporting/segment_report.py` | a `sorted(…)` series, then `[-1]` | `yr_records[-1][…]` |

### The figure this moves, measured (R14)

A real bounded run, `simulation.run_phase2b.main(report_end="2017-12-31")` — the same window the
original finding measured on:

| year | records | published BEFORE | published AFTER | move |
|---|---|---|---|---|
| 2016 | 199,522 | £250,807.39 | £252,386.55 | +£1,579.16 |
| 2017 | 330,366 | £281,285.30 | £283,078.93 | +£1,793.63 |

**The check that makes this more than a preference:** the AFTER figures agree to the penny with
what `run_phase2b` prints for those same years in its own "Portfolio P&L by calendar year" table
(`252386.55`, `283078.93`), and that print never went near a re-sort — it reads `yr[-1]`. The
BEFORE figures agreed with nothing. 2017's AFTER is also the run's final treasury, which a
year-end balance for the last year must be and the old one was not.

Two tests encoded the defect as their expected answer and were rewritten with it named
(`test_annual_report.py::test_extract_report_data_splits_by_year`, whose comment said "picked
from the chronologically latest record… not list order"; and `test_segment_report.py`'s
treasury-end test, which asserted a 2016 close BELOW four balances the treasury had already
reached — a running total cannot go backwards). Both now carry a null control asserting the old
re-sorted answer does NOT come back.

### What is still owed

1. **The drawdown count itself** — one ratchet entry left, `annual_report.py`'s
   `_drawdown_events` fallback. Blocked on the daily fold's one undiagnosed ~£14 ledger
   movement; when that clears, wire the register and delete the fallback rather than leaving a
   wrong path reachable.
2. **The live published `treasury_end_gbp`** is still the old value on the site and in
   `docs/reports/run_output_latest.json`: those figures are baked at run time and this repair
   takes effect on the next full run's report generation. Nothing was regenerated here, and the
   next publish moves the balance-sheet line by roughly the amounts above.
