**Severity:** RECORDED · **Lane:** F_risk_compliance · **Epoch:** unassigned · **Atom:** `unminted`

**Discharged:** `tests/architecture/test_cm_levy_commons.py::test_every_published_row_reproduces_its_own_derivation`, `docs/domain_artefact_library/regulatory/capacity_market_supplier_levy.json` — the artefact now carries Annex 9's cap-period rows verbatim and every levy row is re-derived from them (duration weighting, division, rounding), so a figure that does not reproduce its own publication cannot sit in the commons unnoticed. Was BLOCKING; the 2018 diagnosis is refuted and the real defect it led to (2024/25 at a half-year reading) is corrected.

# The CM levy artefact's stated derivation does not reproduce its own 2018 row

> **SETTLED 2026-09-07, LATER THE SAME DAY, BY READING ANNEX 9. The headline above is WRONG and
> is kept unedited because it is the claim that was filed.** The 2018/19 row was correct. The
> derivation STATEMENT beside it was incomplete, and running it against a rounded figure in a
> prose note manufactured a defect that was never in the data. Chasing it did, however, find a
> real one in a different row — see **What was actually wrong** below.

The original finding is preserved verbatim in git history at `f4a645402`. Its arithmetic was
right: `11.36/3.1 = 3.66` against a tabulated `3.67`, with every other year implying a divisor
of 3.100 and only 2018 implying 3.095. Its conclusion — "it is one row, and one of its two
numbers is wrong" — did not follow, and this document is the correction filed beside the claim.

## Why the diagnosis was wrong

**Annex 9 does not publish a per-customer-per-year figure at all.** It publishes an *annualised*
level in force during each **cap period**: six-month periods to Sep 2022, quarterly after. An
obligation year is the **duration-weighted mean** of the cap periods overlapping Apr–Mar.

For 2018/19 that is `mean(11.652403 [Apr–Sep 2018], 11.077106 [Oct 2018–Mar 2019]) = 11.364754`,
and `11.364754 / 3.1 = 3.6661 → **3.67**`. The row was right.

The £11.36 the finding divided was a **rounded display value** sitting in the row's prose `note`.
`11.36/3.1 = 3.66`; `11.364754/3.1 = 3.67`. **Double rounding.** It bit at 2018 and nowhere else
because 2018 is the only year whose mean lands near enough to a 2dp boundary for the lost digits
to change the answer — which is exactly why "every other year implies 3.100" felt like such
strong evidence and was none.

The general shape, and it is the reusable part: **the finding ran a derivation against the
artefact's own rounded output and treated the disagreement as evidence about the input.** A
displayed figure is not the figure. When a stated derivation fails on one row out of nine, the
precision of the inputs is a likelier suspect than a transcription in the one row.

## What was actually wrong — obligation year 2024/25

Not £0.01 on 2018. **£0.28/MWh on 2024/25**, and it was load-bearing in both lanes.

| | £/cust/yr | £/MWh |
|---|---|---|
| was (Annex 9 v1.8, Apr–Sep 2024 only) | 22.542 | **7.27** |
| is (v1.11, all four quarters) | 21.670 | **6.99** |

The H2 level (£20.798 for both Oct–Dec 2024 and Jan–Mar 2025) is well below H1 (£23.470,
£21.614), so a half-year reading **overstated the obligation year by 4.0%**.

**The artefact had labelled it honestly** — *"H1 ONLY -- Oct 2024 onward is not yet in Annex 9,
so this is the least settled figure here"* — and that label was true when written. It did not
help: the caveat travelled as prose while the number travelled as law, and nothing re-read Annex 9
when v1.11 published the missing quarters. **An honest caveat on a figure is not a control over
it.** That is the transferable lesson here, and it is a more expensive one than the 2018 row
would have been.

Also settled: **2025/26 is now established at £8.64/MWh** (mean £26.799). The artefact's
`what_is_not_established` said "2025/26 onwards. Annex 9 has not published it" — true of v1.8,
false of v1.11. **A not-established claim in the commons is itself a dated reading and rots
exactly like a figure**; it now names v1.11 and is enforced by a control rather than promised.

## The pre-registration, and it was refuted

Written before the lookup, in full:

> **PREDICTION:** £11.36 is correct (it is the figure Annex 9 actually PUBLISHES) and £3.67 is
> the slip; the derived column should read £3.66. Reasoning: the per-customer figure is the
> primary read and the £/MWh is our own derived column, so an arithmetic/rounding error is
> likelier in the derived one. **CONFIDENCE: low.**

Wrong, and interestingly so. The half about *which figure Annex 9 publishes* was right — £11.36
is the primary read. The half that mattered was wrong: I assumed the two figures were a
**pair to choose between**, because the finding framed them that way, and never asked whether
the derivation connecting them was stated correctly. Both were right. **The error was in the
relation, not in either operand** — and no amount of confidence about the operands could have
reached it.

## What changed

* `docs/domain_artefact_library/regulatory/capacity_market_supplier_levy.json` → **v2**. Carries
  all 28 Annex 9 cap-period rows verbatim (`annex9_cap_periods`), a structured
  `gbp_per_customer_year` at 6dp per row, `basis.benchmark_mwh`, and `months_published`. 2024
  corrected to 6.99; 2025 added at 8.64. `derivation` now states the duration weighting and the
  unrounded division. Seven of nine existing rows are unchanged, which is the diff being
  attributable.
* `tests/architecture/test_cm_levy_commons.py` — **new**, and it is step 2 of the original
  finding. Re-derives every row from the cap periods: duration weighting, division, rounding.
  Ten poison rounds, all fired (below).
* `docs/market_research/capacity_market_levy_2016_2024.md` — same corrections; the finding was
  right that fixing one home and not the other would let it be re-promoted. It is now marked as
  a write-up rather than a source of record.
* `tests/simulation/test_phase30a_cm_levy.py` — `test_clamps_post_2024` was **keyed to today's
  answer** and went red because the record became *more complete*. Re-keyed to the property and
  renamed `test_clamps_past_the_published_record`; `test_all_years_defined` re-keyed from
  `range(2016, 2025)` to contiguity over the whole record.
* `tests/architecture/test_year_keyed_rate_table_census.py` — its levy docstring cited this
  finding as a known-live defect. Corrected in place.

## Reach, measured not assumed

`test_every_published_row_reproduces_its_own_derivation` **found the 2024 defect on its first
run against real data**, which is better reach evidence than any poison. Ten mutations, each
verified present before patching and each checked by exit code, not parsed output:

| # | Mutation | Result |
|---|---|---|
| 1 | revert 2024 to 7.27 | FIRED |
| 2 | round 2018's per-customer figure to 2dp (the "tidy-up") | FIRED |
| 3 | `benchmark_mwh` 3.1 → 3.0 | FIRED |
| 4 | drift one cap-period level | FIRED |
| 5 | null a `primary` row's per-customer figure | FIRED |
| 6 | promote the partial 2026/27 year | FIRED |
| 7 | forget the completed 2025/26 year | FIRED |
| 8 | misstate `months_published` | FIRED |
| 9 | drop a cap period from the middle | FIRED |
| 10 | duration weighting → plain average | FIRED (at 2022/23, £3.37 vs £3.50) |

Mutation 10 first "fired" at 2018 on float noise, because the per-customer tolerance was 5e-7 —
a kill for the wrong reason, which is a survival wearing a kill's clothes. Loosened to 1e-5
(still 500× tighter than the 0.005 that could move the 2dp result) so it now fires at 2022/23,
the row that genuinely discriminates weighted from unweighted.

One assertion was **withdrawn before landing**: the first re-key of the clamp test asserted
`_CM_LEVY_BY_YEAR[max(_CM_LEVY_BY_YEAR)]`, which is the expression `get_cm_levy_per_mwh`
itself computes — a tautology that would have passed as a control by accident. It now takes the
boundary from the artefact and goes through the public reader on both sides, and a `max → min`
mutation of the clamp fires it.

## What is next

1. **The pattern, not the instance.** `ccl_main_rates.json` carries `recalled` rows fetched from
   no source, and `ro_obligation_and_buyout.json` and `capacity_market_auction_results.json` have
   no derivation control at all. The 2024 defect was not a transcription slip — it was **a
   correct reading of a superseded publication**, and every artefact in the commons citing a
   versioned source has that exposure. There is no control anywhere that asks *has the source
   been revised since we read it?*
2. **Re-run the book.** 2024 moves −4.0% and 2025 stops carrying forward 2024's rate, so run
   outputs and any published CM figure change. Not done here.
3. `simulation/policy_costs.py` still carries other year-keyed literal tables (FiT, CCL) in
   `_UNVERIFIED_TABLES`. FiT's own note back-derives a 245 TWh denominator from one
   reconciliation — the same class of exposure, unheld.
