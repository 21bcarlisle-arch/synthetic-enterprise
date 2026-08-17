# WORKER FINDING — the final-year CLV snapshot is empty, and the report publishes it as a £3.3m fall

**Severity:** BLOCKING · **Lane:** B_commercial · **Disposition:** QUEUED (not fixed on sight)

**Found:** 2026-08-17 worker tick, LANE 3 DISCOVER/FRAME draw on `EP1_clv_three_horizon`,
while reading `clv_snapshots` for the ex-post gap measurement (that pass's other finding is
`WORKER_FINDING_THE_BOOK_IS_VALUED_ON_A_MARGIN_THAT_EXCLUDES_THREE_QUARTERS_OF_THE_COST_STACK_2026-08-17.md`).
**Subject:** `saas/reporting/annual_report.py::_build_clv_snapshots` (the `as_of` it passes)
and `_section_clv_evolution` (what it then publishes).
**Measured at:** HEAD 4276a179b. `observed-with-evidence` throughout (R9).

## What is published

`docs/reports/ANNUAL_REPORT.md:1776-1795`, verbatim:

    | Year | Accounts | Total CLV £ | Avg CLV £ | Δ CLV £ |
    | 2024 | 9 | £3,255,946 | £361,772 | +£89,680 |
    | 2025 | 0 | £0         | £0       | £-3,255,946 |

    **Peak portfolio CLV: 2020 (£4,203,770)** | **Earliest/lowest: 2025 (£0)**
    **Largest YoY fall: 2025 (£-3,255,946)**

The report states that the portfolio's forward lifetime value fell by £3,255,946 to zero in
2025. It did not. The same run publishes `enterprise_value_gbp 6,304,202.92` across nine
accounts and `still_supplied: true` on eight of the thirteen billing accounts, and eleven
accounts settle in 2025 (`years["2025"]["per_customer"]`).

## Why the snapshot is empty — mechanism, executed

`_build_clv_snapshots` iterates the years and, for each, passes the CALENDAR year end as the
observation edge:

    cutoff = f"{year}-12-31"
    clv_to_year = build_clv(..., excluded_accounts=ceased_billing_accounts(records_to_year, as_of=cutoff))

`ceased_billing_accounts` reads an account as ceased when its most recent settlement is more
than `SUPPLY_CONTINUITY_DAYS` (35) before `as_of`. For the 2025 snapshot:

    as_of                       2025-12-31
    as_of − 35 days             2025-11-26
    newest settlement anywhere  2025-06-07   (`book_as_of` on every account is 2025-06-07)

Every account's last settlement precedes the cutoff, so EVERY account reads as ceased and the
valued population is empty — `clv_snapshots["2025"] == {}`, confirmed in
`docs/reports/run_output_latest.json`. The grace period is doing exactly what it was built to
do; what is wrong is the date it is measured against. `ceased_billing_accounts`' own default
is `max(last_seen.values())` — the observation edge — and this call site overrides that
default with a date the run has not reached.

**This is not a data-thin year.** It is structural: any run that ends more than 35 days before
31 December publishes an empty final-year snapshot. The 2025 row is not a late-year dip, it is
the whole book disappearing 6 months and 24 days after the last settled period.

## What the empty row then does downstream

`_section_clv_evolution` treats the empty year as a real observation:

* `worst_yr` = `min(rows, key=total)` = 2025 at £0, printed as **"Earliest/lowest: 2025 (£0)"**
  — a label that is wrong twice, since 2025 is neither the earliest year nor a low reading.
* `biggest_drop_yr` = `min(deltas)` = 2025, printed as **"Largest YoY fall"** with the entire
  prior-year total as its magnitude. The largest movement the CLV series reports is an artefact
  of its own cutoff, and it is the one a reader's eye goes to.
* `_avg` guards `if year_clv:` at line 1237, so the per-year "Average CLV (Point-in-Time,
  year-end 2025)" line is correctly ABSENT — the same emptiness is handled in one consumer and
  not in the other. That asymmetry is why this survived: the guard exists, one site has it.

Not affected, checked rather than assumed: `enterprise_value_gbp` and `by_billing_account` do
not read `clv_snapshots`, so the site's headline valuation is untouched by this one. The
trailing-margin section at line 2338 reads `snapshots[sorted_years[-1]]` — the empty 2025 —
into `latest_snap`, which it then does not use for any published value on the current path.

## Why it is filed rather than fixed

`SELF_INTERRUPT_DISCIPLINE` — queue by default. And the repair is BUILD code in the CLV
valuation series, on an atom (`EP1_clv_three_horizon`, level 0, `loop_stage: idle`) whose BUILD
is epoch-gated; this tick's draw is DISCOVER/FRAME, which may not write it
(EPOCH_GATING_AND_ATOM_AUTHORSHIP rule 1). It is also not a one-line change to be swept in
silently: it moves a published series, so it owes a regenerated report and an R11 check on the
rendered value, not just a passing test.

## What would close it — recommendation, not an ask

1. **Recommended: clamp the snapshot's `as_of` to the observation edge**, not the calendar year
   end — `as_of=min(f"{year}-12-31", max_settlement_date(records_to_year))`. Point-in-Time is
   preserved (the edge is derived from the truncated window itself, nothing later is consulted)
   and the final year values the book the supplier can actually see.
2. **Then decide what a partial final year IS**, and say so in the row rather than in prose: a
   snapshot at 2025-06-07 is a mid-year reading and its Δ against a year-end reading is not a
   like-for-like YoY move. Either label the row with its own as-of date or exclude it from the
   Δ/extremum arithmetic — silently ranking it against full years is what produced the £3.3m
   headline.
3. **R10 — close the class, not the row.** The invariant: *no derived headline (extremum, Δ,
   ranking) may be computed over a period the run does not fully cover.* The detectable shape
   is a series whose final element's population count is zero while the same run reports a
   non-zero population for that period — checkable over every per-year series the report
   publishes, of which this is one.
4. **R15 — the control must be able to fail.** Mutation: truncate the run's records to
   mid-year, and the CLV evolution section's `Largest YoY fall` must NOT name the truncated
   year. On today's code it does, so the test is red before the repair and green after. Second
   direction, so the clamp cannot fail open: an account that genuinely goes quiet for more than
   35 days before a mid-year edge must still be excluded from that snapshot.
