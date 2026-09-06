**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# The R1 ceiling counted a household's gas leg as a second household, and invented its elasticity

**Found and fixed:** 2026-09-06, delivery seat, claim `r1-ceiling-needs-coverage-not-correction`.
Drawn as lane-0 direction: *"populate the R1 pair-rung observables on every household so the ceiling
stops being a function of which household dropped out."* I went looking for the households that had
dropped out and found that a third of the ones that had not were never households.

---

## The defect

A run output's `customer_id` is a **supply point**, and a household's gas leg is registered under its
electricity point's id plus a suffix — `C1` and `C1g` are one property, and `simulation/household.py`
says so in as many words. The instrument's `observable_rows` keyed its feature vector on the raw
`customer_id`.

Two families of log key on different halves of that split, which is why nothing joined up:

| writes the supply point | writes the household (`run_phase2b`'s billing account) |
|---|---|
| `dynamic_pricing_log`, `rate_decomposition_log` | `churn_journey_log`, `churn_basis_risk`, `demand_estimation_log` |

On `run_output_f53c90b85` the instrument reported **213 households. There were 149.** 82 of the 213
rows were gas legs — 64 the second copy of a dual-fuel household already in the book, 18 the only row
of a gas-only account.

**And every one of the 82 was then graded against an elasticity that belongs to nobody.**
`price_elasticity_for_customer` is a hash of the id with no roster to consult: it answers for
`NOT_A_REAL_ID` with 1.4223, in range and the right shape. So `C1g` came back with 0.5255 while the
1.6043 the world actually gave that household sat in a different row. **38% of the target column was
noise correctly matched to nothing** — and nothing downstream could see it, because a fabricated
elasticity is indistinguishable from a real one at every rung below.

The full-coverage rung has read *cannot tell*, p=0.85, on every run since it was built. That was
never a coverage result. It was 38% noise in the thing being predicted.

## What the fix moves, and what it does not

`observable_rows` keys on `household_of(customer_id)`; `true_traits` refuses any id that is a leg of
another household; `leg_fold_census` puts the fold on the artefact and `households_in_the_book` on
`/harness/`, so the denominator can never move again without a reader seeing it.

| | before | after |
|---|---|---|
| book | 213 | **149** |
| pair-rung ceiling | +0.6127 | **+0.6308** (p 0.0249, still clears) |
| full-coverage rung | +0.0509, p=0.8507 | +0.0537, p=0.8657 |
| full-coverage honest point estimate | +0.0641, band −0.3174 to +0.2350 | **+0.1975, band −0.0276 to +0.3153** |

The point estimate roughly tripling with a band half as wide is the reading to keep: that is what
removing noise from a target column does, and it is the only figure here that moved for a reason
rather than by a rounding.

**The verdict did not change and the step did not close.** Re-run over the same 32 consecutive run
outputs as `613f9bd17`, the corrected instrument still returns 19 *clears* and 13 *cannot tell*, with
no scatter inside either group. So the direction's premise stands: **only coverage will move this.**

## What DID change is that the step is now attributable

`613f9bd17` measured the step and correctly refused to name its cause, because the rung and the book
moved together — 71-in-rung/214-in-book against 69/213, perfectly confounded.

**That confound was the defect.** The book only appeared to move because gas legs were being counted
as households. Keyed on the household the book is a **constant 149 on all 32 runs** while the rung
still steps 71 → 69. Nothing else moved. So the cause is now named rather than disclaimed, and the
sentence that disclaimed it is derived from the window instead of asserted — as is the denominator,
which read *"a book of over two hundred"* against a book of 149 for as long as the miscount stood.

**Two households, on a book that did not change, decide whether A49's gate is open.**

## Controls, each proven by a poison round before being trusted

| control | poisons that red it |
|---|---|
| `test_a_gas_leg_and_its_electricity_point_are_ONE_household_not_two` | key on the raw supply point |
| `test_the_target_column_REFUSES_a_supply_point_leg_rather_than_hashing_it_an_elasticity` | delete the refusal; refuse *everything* |
| `test_the_fold_is_reported_so_a_book_that_shrank_by_a_third_is_visible` | census counts points as households |
| `test_the_confound_is_carried_and_the_cause_is_NOT_attributed` (third leg added) | silence the attribution branch; restore the literal denominator |

The refusal test asserts the defect is **reachable** before asserting the refusal — the lookup really
does hand back a plausible elasticity for `C1g` — and carries `C3_2` as the leg that must *pass*. A
book-membership test was written first and deleted: a successor registration after a home move is a
household this run created that the drawn book has never heard of, so membership would have refused a
real household and shrunk the very coverage this measurement is short of.

## What is still owed, in order

1. **`perceived_bill_saving_gbp` is the binding constraint at 69 of 149** and it is half the winning
   pair. It is emitted only inside the renewal branch (`term_index >= 1`, electricity, non-indexed),
   yet it is computed entirely from company observables — the rate just set, the rate before it, and
   the company's own EAC. **59 households have two or more electricity terms and no journey row.**
   That is not a structural gap; it is an emitter that runs in one branch. Closing it is the coverage
   the honest point estimate is asking for: it refuses at 69 and names 72 as the number it needs.
2. **A verified alias would take `unit_rate_gbp_per_mwh` from 100 to 135**, measured this turn:
   `unit_rate_contracted` on electricity rows is the same quantity (n=110 overlap, max disagreement
   5e-5, pure rounding). `unit_rate_after` (max 145.8) and `price_differential_vs_svt` against
   `rate_vs_svt_pct` (max 39.1) are **not** the same quantity and any alias mechanism must refuse
   them — build it as an alias that earns its use by agreeing on the overlap, never as a rename.
3. 18 gas-only households can carry no electricity rate at all. That is a real `None`, not a gap.
