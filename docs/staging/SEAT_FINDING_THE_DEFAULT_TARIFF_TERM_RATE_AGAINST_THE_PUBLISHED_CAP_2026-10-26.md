**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** `price-cap` -- `docs/market_research/default_tariff_cap_and_epg_on_the_bill.md`

# SEAT FINDING: the default-tariff term rate, checked against the published cap

Follows `SEAT_FINDING_THE_PRINTED_RATE_AGAINST_THE_CONTRACTED_TARIFF_2026-10-26.md`. That check
proved each bill charges its term's rate. The term record is ours, so a mis-set term rate passed it.
For a default tariff the published cap is the one outside source that bounds the rate. This is the
cap side of the correctness ruling's step 2. The wholesale floor is the other side and is not done here.

## What the thing is, before measuring it

- **The term rate**: `contracted_terms[].unit_rate_p_per_kwh` on the raw export. It is the all-in,
  EX-VAT p/kWh the term was struck at, from `account_state_log`.
- **The ceiling**: Ofgem's published level for the cap window, read in the curtained validator from
  the commons and nothing else.
  - Single-register: `ofgem_default_tariff_cap_windows.json` `elec`/`gas` (GBP/MWh incl VAT) / 10,
    divided by (1 + VAT). The VAT is 5%, or the `uk_vat_rates.json` dated exception (0%) for
    electricity from 2026-10-01.
  - Multi-register electricity: `ofgem_cap_multi_register_unit_rates.json`
    `multi_register_p_per_kwh_ex_vat`.
- **Which level in an EPG window**: the Ofgem level, not the EPG. The cap still bounded what the
  supplier could charge. The EPG was a Treasury discount to the household, and the term rate
  includes the Treasury's share (the receipt line on the bill). The direction said to fail closed in
  EPG windows. For single-register, the commons carries the Ofgem level there, so I do not. For
  multi-register, the Ofgem model's rows also cover Oct 2022 – Jun 2023, so those are checked too.
- **Fails closed (UNCHECKABLE, with the reason)** in these cases:
  - multi-register from 2026-01-01 (P15b). The model does not state the new benchmark, so the
    commons carries no level.
  - any date past the last published window. The company carries the last window forward. That is
    a reading, and the validator does not make it.
- **Not applicable**: a non-domestic account, a fixed term (lawfully above the cap), or a date
  before 2019-01-01.
- **What it cannot see**:
  - Region and payment method. This world bills at GB-average, direct-debit-basis levels. A
    standard-credit term lawfully above the DD figure would read as a breach here.
  - The cap is a total at the benchmark consumption. A supplier could lawfully trade unit rate
    against the standing charge. A unit-rate ceiling is the cap model's own construction
    ((benchmark - nil) / kWh), and it is a reading.

## Pre-registration (written 2026-10-26 before any measurement)

On the published 4ae8da9b0f book. That run started at 02:26Z on 26 Oct, after 4bc21e9209 (23 Oct),
the `_is_domestic_leg` fix for incoming occupants:

- **P1.** No domestic SVT term period sits above its window's single-register ceiling by more than
  0.01 p/kWh. If any do, I expect them to be OCC accounts, from a run older than the fix.
- **P2.** The Oct 2021 – Mar 2022 gas SVT terms sit at the ceiling: median ratio 0.99–1.00.
- **P3.** Across all domestic SVT term periods, at least 90% sit within 2% below the ceiling. The
  world strikes SVT at the cap, so they should not be "materially under" it (ruling step 2).
- **P4.** Fewer than 5% of SVT periods are UNCHECKABLE. Most of those would be post-P15b
  multi-register periods, if the book has any.

## Result

Measured 2026-10-26 on 4ae8da9b0f. The ledger was regenerated into /tmp and is not committed.
Scripts: `default_tariff_rate_against_cap` over `raw_account` for every account.

| periods | |
|---|---|
| graded (CAP_CHECKED) | **27,197** (28,439 term-windows) |
| above the ceiling | **0** |
| uncheckable | 0 |
| not applicable | 25,585 |
| total | 52,782, the ledger's invoice count |

The 25,585 not applicable split into:
- 10,024 SVT periods before 2019 (no cap existed);
- 552 fixed+SVT periods before 2019;
- 14,985 fixed;
- 24 on the two SME accounts.

None of them is a domestic default term from 2019 on that the check skipped.

**The predictions, graded as written:**
- **P1 held.** 0 above, and no OCC accounts either, so the 23 Oct fix is in this run.
- **P2 held.** The 971 Oct 2021 – Mar 2022 gas term-windows have a median ratio of 1.0000.
- **P3 held, more strongly than predicted.** Every one of the 28,439 graded term-windows has a
  ratio of exactly 1.0000 (min = max). The world strikes every domestic SVT at the cap ex-VAT, and
  each term is cut at the window boundary. For the ruling's step 2, no SVT term is under the cap.
  That agrees with `SEAT_FINDING_EXPLORES_SLOTS_PICKED_THE_EXTREME_WITH_NO_VALIDITY_CHECK...`: the
  Jan 2022 cap was 4.07p, and 7.4p was the April 2022 level.
- **P4 held.** 0 uncheckable. The book ends in 2025, and no SVT period prints two registers, so
  both fail-closed legs are reached only by the fixtures.

**The check can fail.** Raising every graded default term by 1% fails all 27,197. The tests cover:
the partition, an EPG window, the 2026 zero-rated VAT, a term across a cap change, the
multi-register level, and both fail-closed legs.

**An error of mine, corrected before landing.** The first draft graded a term up to and including
its `tariff_effective_to`. That is the next term's first day: on this book, all 15,280 successive
pairs start on the previous term's end. A bill crossing a cap fall would then hold the old rate to
the new window for one day. The measurement was unchanged after the fix, because these bills turn
at month starts, so no graded bill crosses a window change. A test now holds the exclusive end.

**What agreement here does not prove.**
- **A shared input.** The company's clamp (`company/pricing/renewal_rate_chain.cap_ceiling_ex_vat`)
  reads the same `ofgem_default_tariff_cap_windows.json`, so the two agree by sharing the published
  record, not by sharing code. A wrong row in the commons fails both together. The pre-2026 rows
  are still on a third-party compilation, corroborated at two points.
- **The floor.** A rate set too low passes. The ruling's other side, the period's wholesale cost,
  is not built.
- **One divergence, recorded but not exercised.** In an EPG window the company scales the
  single-rate level by the multi-register ratio, a step its own docstring calls "unwitnessed". The
  validator reads the model's multi-register level directly. The two agree wherever the model's
  ratio is the scale, but this book has no multi-register SVT period, so the divergence is untested.

**Next.** The wholesale-floor side of step 2: each SVT term's rate against its window's wholesale
cost. That is the ruling's domain-invariant suite, item 4.
