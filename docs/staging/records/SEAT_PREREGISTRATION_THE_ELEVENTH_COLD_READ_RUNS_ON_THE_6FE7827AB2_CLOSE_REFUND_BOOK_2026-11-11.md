**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Preregistration addendum: the eleventh cold read runs on the 6fe7827ab2 close-refund book, which the publisher's gate passes (2026-11-11)

Written at about 16:20 GMT, before the seat's checks run on this book, before the Section B draw, and before any brief
exists. It amends `SEAT_PREREGISTRATION_THE_ELEVENTH_COLD_READ_ON_THE_D1_E1587EC5B_BOOK_2026-11-11.md` (1d25b4526c).
That record's order, trade (an Energy Ombudsman case investigator), seed (`random.Random(20261112)`) and method stand.
Only the book changes. Lane-0 item `the-eleventh-cold-read-once-the-close-refund-book-passes-the-gate`.

**What is already measured, so these are not predictions.**
- The D1 book e1587ec5b was refused by the gate (dc3e7dfeb).
- The book is `run_output_6fe7827ab2_20261111T140730Z.json`, the first carrying cab13bbd18's close-refund fix.
- Its pages were built at 6fe7827ab2 with the publisher's chain plus `generate_explore_hh_day` and
  `generate_explore_carbon`, in `/var/tmp/crbook/arm/tree` (`crbook-scripts/grade_one.sh`).
- `_domain_invariant_gate_permits_publish` returned **PERMITS True**: 0 unexcepted breaches and 7 excepted
  (`/var/tmp/crbook/arm/gate.txt`, 15:59).
- `git diff 6fe7827ab2 origin/main` (50315088fb) touches nothing under `site/`, `tools/`, `background/`,
  `company/compliance/` or `DOMAIN_INVARIANTS.yaml`. So these pages are origin's page code, and the read uses them
  as built. A rebuild would reproduce them.
- `tools/generate_explore_cast.py:619` still prints "Your first {fuel} bill is ready" unconditionally, so N28 is
  unfixed.

## Predictions

| # | prediction |
|---|---|
| Q1 | Seat check (d), `closed.py` at as-of 2025-07-04: **0** accounts a year closed holding credit of at least GBP 5 (the D1 book had 1, SYN-2016-493 at GBP 11.56). The debt side is between GBP 2k and 5k (the D1 book had GBP 3,636) |
| Q2 | N25, `fixmove.py`: fixed runs moving their standing charge by more than 1% are still between 600 and 800 (the D1 book had 711) |
| Q3 | `checks.py`: `b_first_read_zero` = 1,302 of 1,302. Electricity median same-month change under 1%. Gas between 8% and 18% |
| Q4 | Cast 8 of 8 filled |
| Q5 (was P6) | Control on the reader: unaided, it objects that some page's ledger sentence does not add up to the balance printed (N26). p ≈ 0.5 |
| Q6 (was P7) | At least one new class. p(no new class) ≈ 0.2: ten reads out of ten have found one, and the trade is new |
| Q7 | 20 to 40 objections |
| Q8 | The trade's own lens: at least one objection on a closing account's final bill or refund timing (SLC 27 refund, final bill within six weeks). p ≈ 0.6 |
| Q9 | Exit legs: **leg one MET** (measured above). **Leg two NOT MET**, p ≈ 0.85, because the N28 templates are unfixed. **Leg three NOT MET**, p ≈ 0.8 |

## Reverse

Delete this file. Nothing outside `docs/staging/` is touched.
