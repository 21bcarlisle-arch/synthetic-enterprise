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

---

## THE BLOCKER ON OWED ITEM 1 IS GONE — the £14 was the journal discarding a sign (2026-08-24, worker tick, RUNG 1c blocking draw)

**Severity stays BLOCKING: the published drawdown count is still the artefact.** Nothing about
the count moved here. What moved is the thing owed item 1 was WAITING ON — "the daily fold's one
undiagnosed ~£14 ledger movement" — which turns out not to have been the fold's defect at all.

### The diagnosis, measured on the window it was measured on

One real end-2019 run (1,909,710 records), the SAME book each time, the ledger built over it two
ways. Held constant so the record book is the only variable: the bills, the payment model, the
opening treasury.

| where the £14 is, and is not | result |
|---|---|
| ledger over the two books with the SAME bills | every figure identical |
| the bills themselves | 5 of 1,510 totals move, £0.03 in all |
| `derive_pnl` over the two books | ≤ £0.05 on every key |
| `annual_management_pack` — cash, equity, assets | **2019 cash £1,039,946.12 -> £1,039,960.20, +£14.08** |

The pack is the only consumer that goes through `company/finance/double_entry.py`, and that is
where the sign was being thrown away:

```python
amount = abs(event["amount_gbp"])          # then the account pair, by event TYPE alone
```

Every maker in `saas/ledger.py` signs the same way — cash out negative, cash in positive — so an
event whose real value is negative was booked as its own opposite, wrong by twice the value:

* a **negatively-priced half-hour** — the supplier is PAID to take the energy, real and
  increasingly common on the GB system — posted as a wholesale COST. This run: 6 half-hours in
  2018 (£5.48 of credit, £10.95 of overstatement) and 2 in 2019 (£1.52, £3.04).
* a **credit bill** — 21 of them here, £2,673.47 in total — posted as REVENUE.

`abs(x + y) != abs(x) + abs(y)`, so the published journal depended on how finely the book was
cut, while every signed figure (portfolio gross, net, treasury) stayed identical to the penny.
£10.95 + £3.04 = £13.99 of it is the wholesale credits; the remaining £0.09 is item 3 below.

### What the repair moves in the published figures (R14)

`to_journal_entry` now reads the sign and reverses the SAME two accounts when the amount opposes
its normal direction. Nothing new is invented, nothing is dropped, and an ordinarily-signed event
of every one of the ten recognised types maps exactly where it always did. Measured on the same
end-2019 run, magnitude-only journal -> signed journal:

| figure | published today | repaired | move |
|---|---|---|---|
| 2019 total equity / total assets | £1,211,357.90 | £1,206,024.95 | **−£5,332.95** (−0.44%) |
| 2019 cash | £1,039,946.12 | £1,034,720.12 | −£5,226.01 |
| 2019 revenue | £1,612,762.50 | £1,611,470.84 | −£1,291.66 |
| 2019 corporation tax | £117,888.50 | £117,643.66 | −£244.84 |
| 2018 wholesale cost | £177,195.88 | £177,184.92 | −£10.95 |

The dominant term is the credit bills, not the negative prices: booking £2,673.47 of credits as
revenue put roughly twice that on the balance sheet. **The balance sheet has been overstating
equity by 0.44%, and that is a repair, not a movement to be explained away** — the next full run
publishes the lower figures.

### And the £14.08 is gone

The same end-2019 fold comparison, re-run on the signed journal: **no figure moves by more than
£0.02.** What remains is a rounding tie in `simulation/meter_reads.py` — an unread month is
estimated as `round(mean(trailing actual reads), 2)`, those reads are sums of ~1,440 floats, and
re-associating a sum moves them by 5.8e-11 kWh, which is enough to decide a penny when the mean
lands on an exact half-penny tie (428.82500000000005 -> 428.83 one way, exactly 428.825 ->
428.82 the other). 19 of 158 estimates flipped, worth £0.03 on £3.05M billed. Left alone
deliberately: both answers are defensible and the exact-tie one is arguably truer.

### Controls, R15-proven

`tests/company/finance/test_the_journal_keeps_the_sign.py` — 7 tests. Four named mutations were
applied and the fires recorded, not asserted: restoring `abs` fires 4 tests; an unconditional
swap fires 3; swapping on the sign alone (ignoring the entry's normal direction) fires 4; letting
a zero amount swap fires 1. Two of them are NULL CONTROLS that state the pre-repair answer and
assert it does not come back. `test_double_entry_characterization.py` had frozen this exact
defect under the name `test_negative_amount_is_absolutised_flipping_a_credit_note_into_revenue`
("characterized, not endorsed"); it is now
`test_the_absolutised_credit_note_surprise_is_repaired`, quoting what it used to say.

### What this does NOT discharge

The drawdown count. Owed item 1 above is no longer BLOCKED, but it is not DONE: wiring the
register and deleting the `_drawdown_events` fallback is the next act, and it lands with its own
before/after. Note also the director's 2026-08-24 console ruling, which outranks the memory
saving and changes where the fold may be used at all: "the half-hourly spine stays half-hourly.
Aggregate in the reporting and ledger layers if that's where the memory goes." The signed journal
is the ledger-layer half of that instruction — an aggregation there is now safe by construction,
because a sum of signed amounts does not care what order it was added in.

One observation left for whoever takes the register: with the sign kept, 2020 trade receivables
close at **−£53.47**. A negative receivable is money the company owes its customers and probably
belongs in account 2200 (Customer Credit Balances Held) rather than as a negative asset. Small,
real, and not repaired here.
