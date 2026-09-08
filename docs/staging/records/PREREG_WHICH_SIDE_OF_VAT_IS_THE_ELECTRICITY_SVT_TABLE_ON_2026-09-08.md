**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a-scalar-copy-of-one-row-of-a-published-series-is-invisible-to-every-census

# Pre-registration: which side of VAT is the electricity SVT table on?

**Written 2026-09-08, BEFORE the measurement, and the answer is not known when this is written.**

## Why this is being asked at all

The scalar-copy census (`tools/published_row_scalar_census.py`, landed b6c06a4f0) ranked four
`simulation/svt_rates.py:21 _SVT_ELEC_PENCE_PER_KWH` values as units-agreeing specificity-1
collisions with `ofgem_cap_unit_rate_composition.json`. Every one of the four matched a field
whose name ends **`unit_rate_p_per_kwh_ex_vat`**:

| table key | table value | published row |
|---|---|---|
| (2021, 4) | 18.95 | standard_credit period 13 = 18.965 **ex-VAT** |
| (2021, 7) | 18.95 | standard_credit period 13 = 18.965 **ex-VAT** |
| (2022, 10) | 51.89 | standard_credit period 16 = 51.869 **ex-VAT** |
| (2025, 7) | 25.73 | direct_debit period 26 = 25.742 **ex-VAT** |

The census was built to find a *copy of a published row*, and it found one. But the collision
carries a second question the census does not ask, because the census compares values and not
bases: **`simulation/svt_rates.py` states, in its own gas block, that both fuels are on the
inc-VAT basis.** Verbatim, lines 139–143:

> BASIS: £/MWh INCLUDING VAT at the domestic 5% rate, excluding standing charge — the published
> basis, the same one the electricity series above is on \[…] Both fuels on one basis is the whole
> point: this field is differenced against a unit rate downstream, and a spread between two bases
> is a number rather than a quantity.

`get_svt_gas_rate_gbp_per_mwh` delivers that by calling
`binding_cap_unit_rate_gbp_per_mwh_inc_vat`. The electricity leg is a hand-written table, so
nothing enforces its basis, and the only evidence about which side of VAT it is on is the values
themselves.

## The prediction

**PREDICTED: the post-cap rows of `_SVT_ELEC_PENCE_PER_KWH` are on the EX-VAT basis**, and the
comment's claim that the electricity series is on the same basis as the gas leg is false. So
`svt_rate_gbp_per_mwh` is inc-VAT for a gas account and ex-VAT for an electricity account — a
~5% basis split inside one field, of exactly the class the comment names as the thing to avoid.

Stated as a falsifiable number, over the post-cap rows (2019-01 onward) for which the commons
carries a published electricity unit rate:

* **If EX-VAT:** `mean(table / published_ex_vat)` ≈ 1.00 and `mean(table / published_inc_vat)`
  ≈ 0.952.
* **If INC-VAT:** the reverse — ≈ 1.05 and ≈ 1.00. The comment stands, the four census hits are
  a coincidence of the composition artefact also publishing ex-VAT, and there is nothing to fix.
* **If NEITHER:** the table is a third reading (a different payment method, a different regional
  blend, or a mix), and the finding is that its basis is undeclared rather than wrong.

I expect the third outcome to be partially true regardless, because the four hits name **two
different payment methods** (standard_credit in 2021/2022, direct_debit in 2025) and a cap unit
rate is published per payment method. A table that tracks one method in one year and another in
another has no single basis to state.

## What will be measured

Every `(year, quarter)` key of `_SVT_ELEC_PENCE_PER_KWH` from 2019-01 to the end of the published
record, against `binding_cap_unit_rate_gbp_per_mwh_inc_vat("electricity", …)` and its ex-VAT twin,
plus the per-payment-method rows of `ofgem_cap_unit_rate_composition.json`. Ratio per row, and the
mean and spread of each.

## What follows from each answer, decided now

* **EX-VAT confirmed** → the electricity leg reads the commons on the inc-VAT basis the way the
  gas leg does, and the pre-2019 table stays (there was no cap to read before January 2019). This
  is the finding's own next-item 2, with the basis defect as its reason.
* **INC-VAT confirmed** → I write the refutation beside this prediction, the four census hits are
  dispositioned as NOT A DEFECT, and next-item 2 is closed as already correct.
* **NEITHER** → the table's basis is stated in the module rather than inferred, and the repair is
  named but not made in this turn, because choosing a payment method is a reading.

Whatever the answer, it is recorded in the result file beside this text, not in place of it.
