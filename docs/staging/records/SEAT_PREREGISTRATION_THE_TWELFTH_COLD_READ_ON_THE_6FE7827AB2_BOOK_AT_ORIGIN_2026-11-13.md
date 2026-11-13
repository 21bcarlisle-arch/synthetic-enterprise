**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Preregistration: the twelfth cold read, on the 6fe7827ab2 book with its pages rebuilt at origin, by a billing-engine test analyst (2026-11-13)

Written at about 03:05 GMT on 13 Nov. This comes before the gate is graded on this build, before the seat's checks
run, before the Section B draw and before any brief exists. Lane-0 item `a-cold-read-ahead-of-the-16-nov-book`.

**The premise, re-measured.** All three cited commits are on origin. 6fe7827ab2 is the book, 5fdf9c106 is the tenth
read and ab2700c1e3 is the eleventh. The eleventh read's new serious class, N29, is filed with an owner
(`SEAT_FINDING_A_CLOSING_DUAL_FUEL_HOUSEHOLD_IS_REFUNDED_ON_ONE_FUEL_WHILE_IT_OWES_ON_THE_OTHER_2026-11-11.md`,
`EP4_collections_journey`). It is fixed in 3af02a2dd1. N28 is fixed in 7d43952ff7. The eleventh read's "Next" said the
twelfth read should wait for a book carrying both fixes. No such book exists before 16 Nov. This read runs now because
the item asks for it: a class found today can be fixed before the 16 Nov book.

**What is already measured, so these are not predictions.**
- Book: `run_output_6fe7827ab2_20261111T140730Z.json`, the same book the eleventh read used.
- The pages are rebuilt at origin 1d86d8e71f, in `/var/tmp/twelfth-read/tree`, by the publisher's chain plus hh_day and
  carbon. Since the eleventh read's build (3cb902dc8f), origin has changed `generate_explore_cast.py` (N28),
  `generate_billing_ledger.py` and `generate_payment_ledger_data.py` (N29's page half), and the dashboard and carbon
  generators. These pages therefore carry the N28 fix and the page half of N29 over a run that does not carry the
  world half.
- **The known cross arm.** The 12 Nov replay (`SEAT_PREREG_THE_16_NOV_BOOK_ON_THE_N29_ROWS_2026-11-12.md`) shows four
  closed legs whose page credit is an artefact. The run sized each refund with the older engine, and the page walks it
  at HEAD. Any objection on PROS-2019-0318, PROS-2021-0117, SYN-2016-047 or SYN-2016-142g's closing balance is graded
  against that class first.

## Order, fixed now

1. **The gate.** `scripts/gate.py` runs in the scratch tree. If it refuses only on the four known cross-arm legs, the
   read still runs. The refusal is an artefact of reading an old book with new page code, not a company defect. This
   read cannot then claim exit leg one, and the record says so. If it refuses on anything else, I trace that first, and
   the read runs only if the trace names a known class.
2. **The seat's named checks, over every page file,** from triage row `a-cold-reader-sees-only-what-its-trade-looks-for`:
   - meter identity across supply points, `checks.py` (b);
   - reads repeating to the decimal, `checks.py` (b);
   - payment method on the bill's date, `checks.py` (c);
   - **new:** gas billed with a volume, `gasvol.py` (e);
   - plus `closed.py` (d) and `fixmove.py` (N25).
3. **The draw.** Section B is `random.Random(20261113).sample(pool, 10)`. The pool is the picker's households, less
   every id drawn or cast in an earlier read, and less this cast.
4. **The trade, new to these reads:** a billing-engine test analyst from a GB supplier's billing-systems team. They run
   user-acceptance tests on bill calculation. That covers day counts and proration, price changes splitting a bill
   period, standing-charge days, VAT at 5% and its rounding, read-to-consumption arithmetic, gas volume-to-kWh
   conversion, two-rate registers, due dates, catch-up and back-billing arithmetic, and how a statement carries a
   balance from one bill to the next.
   - Earlier trades: the generalist (1 to 5), metering and settlement (6), consumer protection and collections (7), the
     price-cap analyst (8), the revenue-assurance auditor (9), registration and meter data quality (10), and the Energy
     Ombudsman investigator (11).
5. **The reader** sees only a `tools/blind_worktree.py` tree that `--check` reports clean, and reads BRIEF.md only.

## Predictions

| # | prediction |
|---|---|
| R1 | The gate **refuses**, on `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO`, and only on cross-arm legs. p ≈ 0.6. Otherwise it permits |
| R2 | `checks.py` gives the same counts as the eleventh read on the same book, because no page change since touches reads, serials or payment methods: `b_first_read_zero` 1,302, electricity same-month median 0.73%, gas 13.03%, 451 electricity actual repeats, and 214 serials on two or more accounts |
| R3 | `gasvol.py`: **some gas bills carry no volume**. p ≈ 0.7, from four volume-bearing bills seen in one file of a run 6 weeks older. Where a volume is printed, volume × CF × CV / 3.6 gives the billed kWh on at least 95% of bills. The CV basis is a fixed stand-in on every bill (the fifth read's class) |
| R4 | `closed.py`: credit a year after closing is 0 accounts. The debt is between GBP 2k and 5k |
| R5 | N25 `fixmove.py`: between 600 and 800 |
| R6 | Cast 8 of 8 filled. No N28 sentence is contradicted by its own bills |
| R7 | At least one new class. p(none) ≈ 0.3. The trade is new, but eleven reads have taken the obvious classes |
| R8 | The trade's lens: at least one objection on proration or a bill split across a price change. p ≈ 0.6 |
| R9 | 20 to 40 objections |
| R10 | Exit leg two **MET or nearly**: the N28 templates are fixed on this build. p(MET) ≈ 0.5. Leg three NOT MET, p ≈ 0.7 |

## Reverse

Delete this file. Nothing outside `docs/staging/` is touched.
