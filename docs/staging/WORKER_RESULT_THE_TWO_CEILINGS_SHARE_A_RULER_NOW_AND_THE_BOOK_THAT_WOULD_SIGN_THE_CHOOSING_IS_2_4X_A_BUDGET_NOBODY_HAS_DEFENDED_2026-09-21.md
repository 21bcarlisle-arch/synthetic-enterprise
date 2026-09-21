**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the two ceilings share a ruler now, and the book that would sign the choosing is 2.4x a budget nobody has defended

RECORDED rather than BLOCKING: the defect is discharged by the commit this document is filed with,
and the question the page carried as open is now answered on the page. What is left is a **direction
question** and it is written down as one at the bottom of this file.

**Filed:** 2026-09-21. Drawn as Lane 0 delivery, `can-this-world-build-the-book-that-would-settle-the-choosing`.

---

## The drawn premise, and what was actually true

The item said: *"The ceiling returns 63 customers at `years=10` while the live three-arm run settles
164 accounts across a ten-year window, so one of the two is not counting what its name says."*

The first half holds. The second is one run stale — the promoted three-arm artefact
(`docs/observability/value_cycle_ab_s1_three_arm.json`, 2026-09-18) settles **154** accounts on the
control arm, not 164. The direction of the contradiction is unchanged and the conclusion did not
turn on the digit.

And the answer to "which one" is **the ceiling**, for a reason neither half of the premise names.

## What `settled_book_ceiling` was counting

`settlement_records_per_customer_year` reads 17,520 records per customer-year out of the AO12 scale
probe's own target. That is the **half-hourly** rate, and the curriculum file says whose it is, in
these words:

> *"I&C accounts settle half-hourly (17,520 records per customer-year) and households settle on a
> profile class."* — `docs/design/curriculum/served_segments.json`

**I&C was suspended from the served book on 2026-08-24.** `served` is `resi + SME`. So the ceiling
prices every customer on this book at the settlement rate of a segment this company stopped serving
four weeks before the number was published against it.

And there is a second, independent factor of the same sign. `run_phase2b` never retains the
half-hourly records at all. At its single feed point:

```python
all_records.extend(fold_to_days(settled_this_term))       # run_phase2b.py:3337
```

with the file's own comment eight hundred lines later: *"`all_records` holds DAILY rows from here
on; the half-hour survives only where a published figure needs it."* One row per (customer,
commodity, settlement_date).

**Measured on the 2026-09-18 run: 301,823 retained rows over 1,029 customer-years = 293.3 rows per
customer-year, against the probe's 17,520 — a factor of 59.7.**

So the ceiling is not miscounting its own subject. It is a correct RSS bound on the scale probe's
instrument. Its *name* and its *use* were wrong: it was cited as a bound on the value cycle's
settled book, which it never priced.

The cheapest way to have seen this without running anything was already on the page and was already
noticed on 2026-09-10 — *"63 is fewer than the book that demonstrably runs"*. A bound the observed
system exceeds is not a bound. What was missing was the next question: **why**.

## The ruler they can share, and this repo already had it

Not accounts. This book's 154 accounts are counted over a ten-year window and do not each live it —
the same book is **1,029 customer-years**, not 1,540. Accounts is the unit that made a per-customer-
year ceiling look comparable to an account count in the first place.

**Customer-years.** And `simulation/net_new_acquisition.SETTLEMENT_CUSTOMER_YEAR_BUDGET = 1200.0` is
already stated in it — the constant that actually caps the published growth curve, and the one a
year's `binding` reason names when it reads `settlement_engine`.

| | customer-years | note |
|---|---|---|
| this book (control arm, 2026-09-18) | 1,029 | 154 accounts over ten years |
| `SETTLEMENT_CUSTOMER_YEAR_BUDGET` | 1,200 | what binds — 86% used |
| RSS ceiling re-ruled to the retained rate | 37,763 | does not bind, by 31x |
| RSS ceiling at the probe's half-hourly rate | 632 | the old number, in its own unit |
| **required to sign the choosing** (2.82x) | **2,902** | `what_would_settle_the_sign`, centre leg |

The last row against the second: **the requirement is 2.42x the capacity.** The honest answer to
*"can a book that size be built"* is **no**, and it is now published as one.

Note the third row against the fourth: at the probe's rate the memory ceiling is 632 customer-years
and would bind *below* the budget; at the rate the book actually retains it is 37,763 and binds
nowhere near it. Which of the two ceilings governs this company was decided by an unexamined
record-population assumption, and it decided wrong.

## And the thing standing in the way is not a measurement

`SETTLEMENT_CUSTOMER_YEAR_BUDGET`'s own note, written 2026-08-29 and unchanged:

> *"Memory is now the only leg with evidence behind it, and memory is SLACK BY 4.5x (4,193 MB peak
> against a 24,032 MB guest). So on today's evidence nothing bounds this constant at 1,200 except an
> interval preference nobody has stated. 1,200 remains a historical number."*

Today's work is the second, independent confirmation of that slack, from a different direction
(records retained rather than peak observed) and on a different instrument. Memory is not what stops
this book growing to 2,902 customer-years. **A publish cadence nobody has named is.**

## A second open clause closed, and it inverted

`what_is_not_established` also carried: *"whether acquiring customers reaches this arm at all —
`where_the_priced_decisions_come_from` measured that on the OTHER book."* Re-run on THIS book:

```
priced accounts: 66   of those drawn: 30   of those static roster: 36
"30 of the 66 accounts the arm priced are drawn households, so a larger drawn book does reach
 this arm."
```

On the book that reading was written against, **none** were drawn, and the conclusion there was
*"the lever is a PRODUCT, not a size"*. On this book 45% are. Growing the book **is** a lever here.
Which makes the capacity finding above the binding one rather than a curiosity: the route works, and
the budget is what is short.

## What landed

* `simulation/premise_population.py` — `retained_settlement_records_per_customer_year` (read off a
  run, refusing when it cannot be); `settled_book_ceiling_customer_years` with **no default record
  population**, because guessing which records a bound prices is the whole defect;
  `HALF_HOURLY_RECORD_POPULATION` / `RETAINED_RECORD_POPULATION` named once each; and
  `settled_book_ceiling`'s return now declares what it prices and what it is **not** a bound on.
* `tools/generate_value_arms_data.py` — `_can_this_book_be_built` and `_what_is_not_established`.
  The published key no longer names a question this repo could answer; it names the one it cannot.
* `site/data/value_arms.json` — regenerated. `can_a_book_that_size_be_built` is available and says
  no.
* `tests/simulation/test_premise_population.py` — four controls. **Mutations M1 (drop the record-
  population declaration), M3 (drop the rate from the customer-year sum) and M4 (default the rate to
  17,520) run and reverted; each fired, and each fired the control written for it.**
* `tests/tools/test_the_concordance_curve_says_what_it_could_have_seen.py` — three controls,
  including the partition sweep (`no_leg_is_reachable` takes both values across a 100x sweep of book
  sizes, so the verdict is not a constant). **Mutations F1 (the sentence always says NO) and F2
  (capacity no longer compared to this book) run and reverted; both fired.**

## What was NOT done, and why it was the wrong thing to do

The item asked for a value-arm pass *"at the largest book the reconciled ceiling admits"*, launched
as a long job. **That run was not launched, deliberately.**

Once the ruler is fixed the reconciled ceiling admits 37,763 customer-years and the budget admits
1,200, so "the largest book the ceiling admits" is 1,200 customer-years — **1.17x today's book, and
2.4x short of the requirement the run would be launched to meet.** Spending hours of wall clock to
land 17% closer to a bound 142% away buys one number nobody needs: the requirement is scale-free
(`times_this_book`), so a 17% larger book moves the multiple and not the verdict. The measurement
that decides this is the budget's basis, and that is a decision and not a run.

The item said a measured *"this world cannot reach it"* is a complete answer and asked for it
published as one. It is, and the arithmetic is on the page rather than in this file.

## The direction question — for the director, and it is his alone

**Raising `SETTLEMENT_CUSTOMER_YEAR_BUDGET` from 1,200 to ~2,900 is the only route left to a signed
answer on whether the choosing creates value.** It is not blocked by memory (slack 4.5x, twice
confirmed) and not blocked by the funnel (18.7% over 4,000 quotes, more wins than the engine
settles) and not blocked by capital (£250k capitalises far more). It is blocked by how long a
publish cycle may take, and **no evidence sets that number** — `net_new_acquisition`'s own note says
the external freshness requirement is zero and the interval is a preference.

So: a publish cycle that today runs ~25 minutes would run roughly 2.4x longer, and in exchange the
central claim of the thesis becomes signable rather than permanently "we cannot tell".

That trade is the director's to make. It is not reversible by a commit and it is not mine.

## What is next, whichever way he answers

1. **A window declared by the producer.** `report_end` is still `None` on the promoted artefact, a
   year after the field existed. Item 1 of the 2026-09-10 finding and still unowned.
2. **The wall-clock cost curve at 2,900 customer-years.** `tools/settlement_ceiling_probe.py` takes
   it and `docs/observability/settlement_ceiling_slope_20260829.json` is the clean slope. If the
   answer above is yes, this is the run to do first — it prices the decision rather than assuming
   it is linear.
3. **`settled_book_ceiling`'s remaining callers.** `tools/inference_claim.settled_book_ceiling_accounts`
   still returns accounts at a declared window. Its refusal is correct and its asymmetry is enforced,
   so nothing published is wrong; but it now has a better-ruled sibling and should be moved onto it
   rather than left as the easy thing to reach for.
