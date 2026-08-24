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

---

## THE DRAWDOWN COUNT ITSELF IS REPAIRED — 6,747 published events in 2017 become 0 (2026-08-24, worker tick, RUNG 1c blocking draw)

**Severity: this document's own discharge condition is now met.** Owed item 1 — the last ratchet
entry, the named instance, the figure the whole finding is about — is repaired and measured. The
ratchet is 1 → 0 and `KNOWN_READS` is empty.

### What was wired

`simulation/settlement_daily.py::TreasuryDrawdown` had no caller. It now has exactly one, fed at
the **same single point** `SettlementFold` is fed (`all_records.extend(settled_this_term)` in
`run_phase2b`), for the same stated reason: fed anywhere else it would see records the book has
not. The run emits it as `treasury_drawdown_points`, and `annual_report.extract_report_data`
walks it.

The `sorted(yr_records, key=(settlement_date, settlement_period))` read is gone.

### The published figure this moves (R14)

A real `simulation.run_phase2b.main(report_end="2017-12-31")` — the same window this finding was
originally measured on:

| year | records | drawdown events PUBLISHED | drawdown events AFTER | deepest published |
|---|---|---|---|---|
| 2016 | 199,522 | 0 | 0 | — |
| 2017 | 330,366 | **6,747** | **0** | 11.0% |

**Said out loud, as this document asked:** the annual report will stop reporting that the
treasury drew down by 11% thousands of times in 2017. It never drew down at all that year. The
RAG rating beside it was computed from the same artefact, and the rendered line was 202,048
characters of near-duplicate events in the end-2019 report — three such lines were two-thirds of
that file's bytes.

Two independent checks on the same run, both green: the register the run emitted is byte-equal
to one folded independently over the run's own book, and its events equal the accumulation-order
walk of that book in both years.

### The one deviation from the stated discharge condition, and why

This document asked for "the fallback deleted rather than left reachable". What is deleted is the
**re-sorted** read. What remains when no register is present is a read of the book in
**accumulation order** — `yr_records` is an order-preserving filter, so it is the same path the
register folded, just unfolded.

Deleting the branch outright would make an absent register publish "no drawdowns", which is the
FAIL-OPEN pattern (R15) this project keeps catching: passes on missing. The clause's purpose was
that no WRONG path stays reachable, and none does. `test_an_absent_register_reads_the_book_in_
accumulation_order` carries the second half that makes it more than a preference — the same code
path on a book that genuinely does contain a 50% drawdown, so a function that returns `[]` always
would fail it.

### Controls, R15-proven — four named mutations applied, fires recorded not asserted

`tests/saas/reporting/test_annual_report.py`, four tests. The unmutated tree is green; then:

| mutation | tests fired |
|---|---|
| M1 restore the re-sorted read (the named defect) | 2 |
| M2 ignore the register, always read the book | 1 |
| M3 fail-open: an absent register becomes no drawdowns | 1 |
| M4 sort only when the register is absent | 2 |

M2 is the one that mattered: the first draft of these controls had a fixture on which the
register and the book gave the SAME answer, so **nothing proved the register was consulted at
all** — M2 fired zero tests and the hole was invisible until the mutation was run. The fixture is
now the case the register exists for: three identical daily closes in the retained book, and a
balance that fell to a tenth and recovered between two of them in the register.

`tests/simulation/test_run_phase2b.py::test_the_run_emits_a_treasury_drawdown_register` proves
the emitting half against a REAL run (reusing the existing module-scoped end-2017 fixture, no new
run cost), with its own null control asserting that the two orderings genuinely disagree on that
book — otherwise the equality it checks would be a fact about the window, not about the register.

`tests/tools/test_running_total_order.py::test_the_live_scan_still_finds_the_named_instance`
asserted the defect was STILL PRESENT — correct while the debt was outstanding, the defect's own
expected answer once it was not. It is now
`test_the_named_instance_is_repaired_and_the_live_scan_is_clean`, quoting what it used to say,
and a new null control drives the old line through the scanner in a scratch tree so that "the
live scan is clean" is a fact about the repository rather than about a scanner that stopped
looking.

### What is still owed

**The live published figures.** `docs/reports/run_output_latest.json` and the site still carry
the old drawdown count and the old `treasury_end_gbp`: both are baked at run time. Nothing was
regenerated here. The next full run's report generation is what moves them, and it moves the
balance-sheet line by the amounts in the section above as well.

Also still open, and unrelated to the count: the negative 2020 trade receivable (−£53.47) noted
at the end of the previous section.

---

## THE NEGATIVE RECEIVABLE IS REPAIRED — a credit balance on 1100 is a liability, not a minus-fifty-three-pound asset (2026-08-24, worker tick, RUNG 1c blocking draw)

**Severity stays BLOCKING for the one reason it has stayed BLOCKING since the count itself was
repaired: the LIVE published figures are still the old ones.** Nothing here regenerates them. What
this tick closes is the second of the two items left open above — "the negative 2020 trade
receivable (−£53.47) noted at the end of the previous section".

### What was wrong

Account 1100 is debit-normal, so once the journal keeps its signs (the repair two sections up), a
book whose customers have collectively paid ahead of what they were billed nets NEGATIVE.
`balance_sheet()` read that net straight through into `trade_receivables_gbp` and added it to
`total_assets_gbp`. Money owed BACK to customers was therefore published as an asset of minus
fifty-three pounds — understating assets and hiding a liability in the same stroke.

### The repair

A presentation split, not a journal entry: the debit balance stays the receivable, the credit
balance is reported as `customer_accounts_in_credit_gbp` and joins `total_liabilities_gbp`. No
account balance moves, so `balance_sheet_with_held_credit`'s augmented journal composes unchanged,
and assets and liabilities rise by the same amount so `equation_holds` is untouched. The annual
report renders the new row only when it is non-zero — a £0.00 row on every ordinary year teaches a
reader to stop looking at it.

### The figures (R14), and what is measured versus derived

**Measured (cited, not re-run):** the BEFORE figure is the one the section above measured on a real
end-2019 run — 2020 trade receivables closing at **−£53.47**.

**Derived, not measured (R9 label):** the AFTER figures follow arithmetically from that BEFORE,
because the split is deterministic given the net:

| figure | before | after |
|---|---|---|
| `trade_receivables_gbp` | −£53.47 | £0.00 |
| `customer_accounts_in_credit_gbp` | (did not exist) | £53.47 |
| `total_assets_gbp` | X | X + £53.47 |
| `total_liabilities_gbp` | Y | Y + £53.47 |
| `treasury.working_capital` | W | **W — unchanged** |

**Why the run was not repeated to measure it directly, stated rather than hidden:** at the time of
this tick `background.resource_headroom.sample()` reported 3,875 MB available of 24,032 MB with the
live producer (`background/sim_runner.py`) holding the rest, against 8 recorded OOM kills. A second
full-window run would have been a real risk to the running producer for a £53 presentation figure
whose after-value is arithmetic. The working-capital invariance is not asserted as arithmetic — it
is proven by a test that reconstructs the pre-split formula from the post-split fields.

### Controls, R15-proven — four named mutations applied, fires OBSERVED and recorded

`tests/company/finance/test_a_credit_balance_on_receivables_is_a_liability.py`, 8 tests, green on
the unmutated tree:

| mutation | tests fired |
|---|---|
| M1 restore the netted read (the named defect) | 5 |
| M2 clamp the receivable but drop it from liabilities | 2 |
| M3 fail-open: `customer_accounts_in_credit = 0.0` always | 3 |
| M4 over-reach: apply the same clamp to cash (1001) | 1 |

One of the eight is a NULL CONTROL stating the pre-repair answers (−£20.00 receivables, £1,100.00
total assets on the fixture) and asserting they do not come back. Another asserts that an ordinary
debit balance — the overwhelmingly common case — publishes every field exactly as before, so this
repair moves the years that are in credit and no others.

**M4 is the one that earns its place.** The split is deliberately NOT applied to cash: a negative
cash balance is a real overdraft and its sign is what every consumer of `cash_gbp` needs, so
clamping it would report an overdrawn company as holding zero cash. Without a test saying so, that
exclusion is indistinguishable from an oversight and a later reader "completing the pattern" would
introduce the worse defect. If an overdraft facility is ever modelled it is a bank liability and
belongs in the 2xxx chart as a posted entry, not in this presentation split.

### Two things named here rather than fixed here

1. **`customer_accounts_in_credit_gbp` is NOT `customer_credit_held_gbp`.** DD3's held credit is a
   positive-balances-only aggregate from the direct-debit balance book, booked by an actual journal
   entry; this one is whatever 1100 itself owes, derived from billing and payment. They describe
   overlapping economics from two different books. A supplier reporting both would say so, and the
   code now does; reconciling them is a separate question and is not answered here.
2. **`company/finance/treasury.py::working_capital` double-counts VAT** — it adds
   `vat_payable_gbp` to `total_liabilities_gbp`, which already includes it. Observed-with-evidence
   that this is INERT today: no branch of `to_journal_entry` posts to 2100 at all (a
   `vat_remittance_event` posts DR 4001 / CR 1001), so `vat_payable_gbp` is £0.00 in every journal
   this company produces. It is a fail-open waiting for the first entry that ever credits 2100.
   Registered as its own latent finding rather than fixed on sight (SELF_INTERRUPT_DISCIPLINE).

### What is still owed on this document — unchanged, and it is one thing

**The live published figures.** `docs/reports/run_output_latest.json` and the site still carry the
old drawdown count, the old `treasury_end_gbp`, the magnitude-only journal's balance sheet and the
netted receivable. All four are baked at run time by a run whose git stamp is `53ceb2008`, which
predates every repair in this document. `python3 -m saas.reporting.annual_report` cannot move them:
that CLI renders from already-extracted data, and the figures were reduced before they were saved.
The next full run through `python3 -m tools.run_annual_report` is what republishes them, and when it
does it moves the drawdown count to the true count, `treasury_end_gbp` by roughly +£1.8k, equity
down 0.44%, and any in-credit year's receivable off the asset side.

---

## THREE OF THE FOUR PUBLISHED FIGURES HAVE MOVED — and verifying that turned up a residual of the same class (2026-08-24, worker tick, RUNG 1c blocking draw)

**Severity stays BLOCKING, and the reason has changed.** It is no longer "the live published
figures are all still the old ones" — three of the four moved on the run that published at
19:41 UTC. It is now the residual named in the second half of this section, which is on the same
published risk figure and is not yet measured.

### What is now published, checked at HEAD rather than on disk (R11)

`docs/reports/ANNUAL_REPORT.md` is **git-clean**, so the rendered values below are HEAD's:

| owed item | was | published now | status |
|---|---|---|---|
| the drawdown count | 6,747 events in 2017 | `Treasury drawdown events (>=10% threshold): none` in 8 of 10 years | **MOVED** |
| the rendered line length | 202,048 chars | longest line in the whole report is **7,916** | **MOVED** |
| `treasury_end_gbp` | a re-sorted `max()` | 2025 = £1,745,358.49, agreeing to the penny with the report's own "Treasury peak: 2025 (£1,745,358)" | **MOVED** |
| the signed journal | magnitude-only | run stamp `4b3086b1f` **is** the signed-journal commit | **MOVED** |
| the netted receivable | −£53.47 (end-2019 window) | still published: `Trade Receivables £-200.29`, `customer_accounts_in_credit_gbp: null` | **NOT YET** |

**Why the receivable alone is behind, measured not guessed.** `sim-runner-log.md` records
`[2026-08-24 19:11 UTC] Starting run — git=4b3086b1f`, and the report was extracted at ~19:41 UTC.
The receivable repair is commit `94c9b4123`, authored **20:04 UTC** — 23 minutes after the
extract. It is one run behind, not un-landed. `sim_runner` stamps HEAD at run start and runs on a
~30–90 min cadence, so the next run carries it with no intervention; nothing here forces one.

### The residual, and it is the same root property one level down

The register was **absent** from this run output (`treasury_drawdown_points` is not a key — the
run predates `f0c5d2865`), so the published count came from the **fallback**: the
accumulation-order read of `yr_records`. That is a real exercise of the fallback on a 10-year
book, and it is the first one. It returned two events:

```
2022   peak £1,169,284.6555   trough £1,035,944.824   11.4035%
2023   peak £1,169,284.6953   trough £1,035,932.012   11.4046%
```

**Observed-with-evidence:** those two "different years" have peaks **4 pence apart** and troughs
£12.81 apart, on a book whose treasury grew £250k → £1.75M. Two independent swings landing that
close is not a coincidence worth entertaining.

**Inferred (R9 label), and this is the mechanism I could not check here:** a year's treasury
series is a *subsequence* of the portfolio running total, sampled at the moments the term loop
happened to emit records dated in that year. Between two consecutive samples the balance travels
through other customers' whole terms. So one stretch of the term loop that emitted both 2022- and
2023-dated records would show the **same** swing in both buckets — which is what the numbers look
like.

**This is not a fallback-versus-register disagreement.** `TreasuryDrawdown.add` partitions on
`day[:4]` and folds turning points *within each year's bucket*, exactly as the fallback does.
They agree — which is why this document's own byte-equality test passed — and they share the
property. The comment at `annual_report.py:468` says the fallback is "the same path the register
folded, just unfolded", and that is true; what neither says is that **year-partitioning a
portfolio running total breaks accumulation order for the same reason re-sorting did**, just
2,000× more gently. This document's opening sentence — "meaningful in ACCUMULATION order and in
no other" — applies to the repair as well as to the defect.

**What would settle it, stated because I could not run it:** walk the full book once in
accumulation order with no year partition, and attribute each completed drawdown to the year of
the record at its trough. If 2022 and 2023 collapse to one event, the published count is 1 and
not 2. `all_records` is not retained in the run output (`extract_report_data`'s own docstring
says so — ~1M rows), so this needs a real bounded run and is a BUILD draw, not a read.

**Not fixed on sight (SELF_INTERRUPT_DISCIPLINE).** Filed here rather than as a new staging-root
document deliberately: it is the same figure, the same class and the same document's own repair,
and a new class member would have to re-render `CLASS_MEASUREMENTS_THAT_MIRROR` in its own commit
against a `--check` that passes today.

### What discharges this document now

1. The receivable reaching the published balance sheet on the next run (mechanism live, no act needed).
2. The residual above measured — one full-book accumulation-order walk — and the published count
   corrected to whatever that says, with its before/after stated (R14).

---

## THE RESIDUAL IS REPAIRED — a year's records are a SUBSEQUENCE of the portfolio balance, not a series of their own (2026-08-24, worker tick, RUNG 1c blocking draw)

**Severity stays BLOCKING for one reason and it is the same one: the published figure has not
moved yet.** What this tick closes is the mechanism behind it — the residual the section above
could only label INFERRED, because settling it was said to need a full-book run and the memory
headroom to take one did not exist at the time.

It did not need one. The claim was about a MECHANISM, and a mechanism can be built.

### What was wrong

The count repair replaced `sorted(yr_records, key=(settlement_date, settlement_period))` with an
accumulation-order read — and then walked **the year's own records** as though they were a series.
They are not. `treasury_cash_balance_gbp` is a PORTFOLIO running total stamped record-by-record
during the term loop, so a year's records are a *subsequence* of it, sampled at the moments the
loop happened to emit records dated in that year; between two consecutive samples the balance
travels through other customers' whole terms. Filtering preserves ORDER. It does not preserve the
SERIES.

So one swing straddling a stretch of the loop that emitted both 2022- and 2023-dated records was
published as **two events, one in each year** — each year seeing its own sample of the same peak
and the same trough. `TreasuryDrawdown` had the identical property one level down: it partitioned
on `day[:4]` and kept a separate peak per bucket, which is why the register and the fallback
agreed and this document's own byte-equality test passed. They agreed because they shared the
defect.

The finding's opening sentence — "meaningful in ACCUMULATION order and in no other" — was always
the whole rule. `sorted()` broke it loudly (6,747 events). The year partition broke it quietly
(2 events for 1).

### The mechanism, DEMONSTRATED rather than inferred (R9)

`tests/saas/reporting/test_a_year_bucket_is_not_a_treasury_series.py::test_the_year_partition_reports_one_swing_as_two_events`
builds the interleave the mechanism requires — one swing, records of two years straddling it —
and reproduces the real signature to the penny: the two "events" come out with **peaks 0.04 apart
and troughs 12.81 apart**, which are the two gaps this document measured on the live book. That is
the same claim as a full-book walk, without the £1.7M book: two independent swings do not land
four pence apart, and now there is a fixture saying exactly which construction does.

### The repair

One walk of the whole path, each completed drawdown dated by the year of the record at its
**trough** — the year the treasury was actually at its lowest.

* `simulation/settlement_daily.py::TreasuryDrawdown` folds ONE path for the book and tags each
  turning point with its year (`points()` -> `[balance, year]` pairs). The year is a TAG, not a
  bucket. `points_by_year()`/`series_for()` are gone: a partition-shaped accessor is the defect's
  own shape, and leaving one is an invitation.
* `simulation/run_phase2b.py` emits it as `treasury_drawdown_path` (was `treasury_drawdown_points`).
* `saas/reporting/annual_report.py::_drawdown_events_by_year` walks it once; the per-year loop now
  only looks its year up. A run output predating the register falls back to
  `_treasury_path_from_book` — the retained book in the order the book holds it, whole, **not**
  filtered per year, so the fallback no longer carries the defect either.

### The figures (R14), and which are measured

**Measured, from the published artefact at HEAD** (`docs/reports/run_output_latest.json`, run
stamp `4b3086b1f`) — the BEFORE, exactly as this document's residual section reported it:

| year | peak | trough | pct |
|---|---|---|---|
| 2022 | £1,169,284.6555 | £1,035,944.8242 | 11.4035% |
| 2023 | £1,169,284.6953 | £1,035,932.0121 | 11.4046% |

**Derived, not measured (R9 label):** the AFTER is **one** event, at the higher of the two peaks
and the lower of the two troughs — £1,169,284.6953 -> £1,035,932.0121, 11.4046%, dated **2023**
by its trough. That follows from the two rows above IF they are one swing, which is what the
fixture establishes and what a full-book walk would confirm directly.

**Why no full run was taken here, stated rather than hidden:** headroom recovered to 21,922 MB of
24,032 MB mid-tick, so it was no longer impossible — but `background/sim_runner.py` is live on a
~30-90 min cadence and a second concurrent full-window run is how this host collected its 10 OOM
kills. The next cycle reads this working tree and republishes the figure with no intervention.
What WAS run against real data is `tests/simulation/test_run_phase2b.py::test_the_run_emits_a_treasury_drawdown_register`,
which takes a genuine 2017 run and asserts the register is a lossless compression of that run's
own book (same events, fewer points) with a null control proving the window distinguishes
accumulation order from date order.

### Controls, R15-proven — five named mutations, fires OBSERVED in scratch worktrees

`tests/saas/reporting/test_a_year_bucket_is_not_a_treasury_series.py`, 8 tests:

| mutation | tests fired |
|---|---|
| M1 reorder the path year-by-year before the walk | 3 |
| M2 attribute an event to the year of its PEAK instead of its trough | 2 |
| M3 fail-open: `_drawdown_events_by_year` returns `{}` always | 3 |
| M4 drop the year tag from the register (`points()` returns bare balances) | 8 |
| M5 the genuine pre-repair shape — one INDEPENDENT walk per year bucket | 3 |

### The CLASS control (R10), because an instance fix would not close this

A static scanner cannot catch a bucketed walk — it names no `sorted`. So the control is a
PROPERTY of the published figure. Every event now carries `sequence`, its position in the one
walk, which makes two facts checkable by any consumer:

* the sequences across all years are exactly 0..n-1, no repeats — **a partition restarts its
  count in every bucket**, so a duplicate `sequence` IS the partition;
* ordered by `sequence` the peaks strictly increase — a drawdown completes only when the balance
  takes out the previous peak, so **only a bucket that restarted its own peak can publish a later
  event at a lower one**, which is precisely what the real pair did (1,169,284.6555 then
  1,169,284.6953 in year order, the second event's peak *above* the first's).

`test_the_published_events_are_one_walk_and_say_so` asserts both on the published dict. M5 — the
genuine pre-repair shape — reds it on duplicate sequences. `tools/running_total_order.py`'s
doctrine note carried the clause that authorised this ("filtering preserves accumulation order,
and a bucket is CORRECT"); it now states the distinction it was missing — that is true of a LAST
VALUE and false of a SERIES — and points at this control.

### What is still owed on this document, and it is one thing

**The published figure.** `docs/reports/ANNUAL_REPORT.md` at HEAD still prints the two events
(lines 4941 and 5120), because they were baked by a run that predates this repair. Nothing here
regenerates them and no run was forced. The next `sim_runner` cycle reads this working tree and
republishes; when it does, the two lines become one event in 2023 and 2022 joins the eight years
already reading "none". Also still one run behind, unchanged from the section above: the netted
receivable.

### What discharges this document now

The next published report showing **one** 2022/2023 drawdown event rather than two, verified on
the rendered artefact (R11), together with the receivable reaching the balance sheet. Both are
one run away and neither needs an act.
