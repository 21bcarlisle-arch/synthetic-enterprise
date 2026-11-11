**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Record: the first D1 book (e1587ec5b) is refused by the publisher's gate, so the eleventh cold read does not run (2026-11-11)

Graded against `docs/staging/records/SEAT_PREREGISTRATION_THE_ELEVENTH_COLD_READ_ON_THE_D1_E1587EC5B_BOOK_2026-11-11.md`
(landed 1d25b4526c before the book finished). Lane-0 item `the-eleventh-cold-read-on-a-book-the-publishers-gate-passes`.

**The book.** `run_output_e1587ec5b_20261111T012324Z.json`, finished 03:11 UTC. Its pages were built in a scratch tree at
origin **3cb902dc8f** with the publisher's customer-page chain, then `generate_explore_hh_day` and
`generate_explore_carbon` (`/var/tmp/eleventh-read/scripts/build.sh`). All 8 Explore slots filled. Graded by
`background.process_run_complete._domain_invariant_gate_permits_publish` from that tree (`scripts/gate.py`). Outputs are in
`/var/tmp/eleventh-read/` (`gate.txt`, `checks.txt`, `closed.txt`, `fixmove.txt`, `tree/docs/reports/domain_invariants.json`).

**Deviation from the prereg, stated before the grade was read.** The prereg named origin 45e531f233. Origin moved before
the book finished. 3cb902dc8f adds one checkable row, `INV_REFUND_WITHIN_THE_PAGE_CREDIT`. ff5dc18dcc is a pure
refactor of the walk. The build used origin as the script says, because the publisher would too. P2 is graded on the
rows that existed when it was written. The new row is reported separately.

## The gate: REFUSED

> 208 unexcepted breach(es) across 2 invariant(s); 8 excepted. ENFORCED: the publish is refused.
> INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO 3 (3 breaches exceed the exception's max_breached 2);
> INV_REFUND_WITHIN_THE_PAGE_CREDIT 205 (no exception)

The closed-account row breaches on the same three legs as on 068b5e3cc8: PROS-2016-0263g -1.65, PROS-2017-0351 -21.86,
SYN-2016-493 -11.56. The refund row breaches 205 of 238 refund lines, the same count 3cb902dc8f measured on 068b5e3cc8.
D1 does not touch how the close sizes a refund. The fix for both rows is the close-refund item
(`the-close-refund-is-sized-from-the-balance-after-the-final-bill`), which was being landed from
`/var/tmp/wt-close-refund-sizing` when this was graded. Its own grade on 068b5e3cc8 leaves the refund row at 12, still
refused.

## Predictions graded

| # | prediction | result |
|---|---|---|
| P1 | gate refuses, p(pass) ≈ 0.35 | **Held.** Refused |
| P2 | closed-account row, 3 breaches, the same three legs; no other row from clean or excepted to unexcepted | **Held** on the rows that existed when P2 was written. The refund row is new to origin since then, so it is not a move |
| P3 | D1 moves ≥1 row's count by >10% against the tenth read's gate | **Held.** `INV_OVERDUE_WITHIN_PAGE_BALANCE` 22 → 0 (of 6,385). That was D1's own target. Every other row reads exactly as on 068b5e3cc8, except for a handful of checked counts that moved by 3 |
| P4 | N25: fixed runs with standing charge moving >1% between 600 and 800 | **Held.** 711 (electricity 335, gas 376) over 862 runs |
| P5 | closed a year on, ≥GBP 5: credit under 1k, debt 1k-10k | **Held.** Credit GBP 11.56 (1, SYN-2016-493), debt GBP 3,635.90 (66) |
| P6, P7 | the read itself | **Not graded.** The read did not run |
| P8 | exit legs one, two, three not met | **Held.** Leg one is not met, because the gate refuses. Leg two is not met, because the N28 cast templates are unfixed. Leg three is not graded, because there was no read |

The seat's checks a-c (`checks.txt`) read the same as on the tenth book in every line compared.

## What changed in the register, in the same commit

`INV_OVERDUE_WITHIN_PAGE_BALANCE`'s exception (max 22, SYN-2016-549) is **retired**. Its own `retired_by` asked for "graded 0
on a fresh run" of the one rule for what a bill asks after a credit. That is D1 (b47832f7e), and this book grades it 0
of 6,385. Retiring the exception means a regression of that row now refuses the publish instead of sitting under a
ceiling of 22. Reverse: restore the block from git history.

## Slack ceilings, not touched here

Five more exceptions read 0, or far under their ceiling, on both 068b5e3cc8 and e1587ec5b. Each still lets a regression
through silently, up to its ceiling.

| row | ceiling | both books |
|---|---|---|
| `INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE` | 1 | 0 |
| `INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL` | 14 | 0 |
| `INV_BACK_BILLING_ON_RECEIPT_FROM_ISSUE` | 16 | 0 |
| `INV_CAST_TARIFF_LABEL_IS_THE_BILLED_TERM` | 42 | 0 breached (flagged) |
| `INV_PLAN_REOFFER_FOLLOWS_A_MISSED_BILL` | 4,610 | 19 |

None of these names a `retired_by` that D1 meets. Whether each reads 0 because it was fixed, or only because the
scratch chain does not reach it, is not established here. That is the next item, handed off: retire or re-base each
one against its own `retired_by`, with that question answered per row.

## What the item now waits on

A book the gate passes. The closest candidate is the first book that carries the close-refund fix, and that fix's own
grade already predicts a refusal on 12 refund lines. The eleventh read's brief, trade and Section B seed stand as
pre-registered and are re-used unchanged on that book.
