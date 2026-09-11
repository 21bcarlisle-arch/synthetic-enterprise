**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a-scalar-copy-of-one-row-of-a-published-series-is-invisible-to-every-census

# My prediction was wrong, and the measurement found something four times larger

**2026-09-08. Lane 0 delivery.** Claim:
`a-scalar-copy-of-one-row-of-a-published-series-is-invisible-to-every-census`.

Pre-registration: `docs/staging/PREREG_WHICH_SIDE_OF_VAT_IS_THE_ELECTRICITY_SVT_TABLE_ON_2026-09-08.md`,
written before the measurement and left unedited.

---

## The item was drawn on a spent premise

The steer asked for the AST pass that would have found GBP 930 without a human reading the file.
**It already exists** — `tools/published_row_scalar_census.py`, landed b6c06a4f0 on 2026-09-08,
with its 7-test control, its poison round, and its population measured before any control was
written. The census re-runs clean from this worktree: 1,982 published rows × 3,513 module-level
numbers, 64 units-agreeing bindings, and the historical defect still ranked first.

So the work of this turn is where the landed finding said it would be — its **"What is next, in
order"** list, items 1 and 2, which the census dispositioned as SOURCED but did not repair.

## Item 1, done: `vat_book` stops being a second home for the VAT de minimis

`company/finance/vat_book.py` carried `SME_ELEC_THRESHOLD_KWH_PER_DAY = 33.0` and
`SME_GAS_THRESHOLD_KWH_PER_DAY = 145.0` as literals, while
`docs/domain_artefact_library/regulatory/vat_fuel_and_power_de_minimis.json` held the same two
figures as published law and `company/billing/dual_fuel_bill` already read them from it. Both are
now derived from that same public load — imported, not re-read, because a second loader against
one file is the same defect one level up.

**And the census hit was hiding a live one.** `classify_vat_category` took
`max(elec_limit, gas_limit)` and applied it to every fuel, so a business ELECTRICITY supply
anywhere in the 33–145 kWh/day band was reduced-rated where VAT Notice 701/19 §5.2 says standard.
That is the *same defect* `dual_fuel_bill._sme_vat_rate` carried until 2026-08-31 — the one the
artefact was created for, whose own text says the limits "are NOT the same for the two fuels" —
mirrored into a second module and still live in it eight days later. **This is the VAT shape
CLAUDE.md names, found a fifth time, and it was found by the value, not by the name.**

The function now takes `fuel=`, and with no fuel named it answers only outside the band where the
two fuels agree and refuses inside it with the reason stated. Mutation-proven: fuel-blind `max()`
(5 red), fail-open on an unnamed fuel (1 red), and — after a first pass where it survived —
literals restored in place of the commons load (1 red).

**That survival is worth recording.** Restoring `33.0`/`145.0` passed every value assertion,
because today the literals and the publication agree. It was an equivalent mutation, not a missing
defect, and it is precisely the state the module sat in for months while being wrong in principle.
A value check cannot see provenance. The control that kills it moves the published limit and
asserts the module follows.

## Item 2: the prediction, and its refutation

The census ranked four `_SVT_ELEC_PENCE_PER_KWH` values as specificity-1 collisions with fields
named `unit_rate_p_per_kwh_ex_vat`. **I predicted the electricity table was on the EX-VAT basis**,
contradicting the module's own claim that both fuels are inc-VAT, and I wrote down the numbers
that would show it: `mean(table/published_ex_vat) ≈ 1.00`.

**REFUTED, and not marginally.** Over the 28 post-cap rows the commons publishes:

```
mean(table / published_INC_vat) = 0.9989      <- and exactly 1.0000 on 24 of 28 rows
mean(table / published_EX_vat)  = 1.0489
```

The table is inc-VAT. The module's comment is correct, the gas and electricity legs are on one
basis, and the four census hits were coincidence — the composition artefact happens to publish
ex-VAT figures per payment method, and 18.965 ex-VAT for standard credit lands near 18.95 inc-VAT
for direct debit. **Filed as NOT A DEFECT so the next reader does not re-open it.**

I also predicted a partial "NEITHER" outcome, on the grounds that the four hits named two
different payment methods. That was wrong for the same reason and by the same evidence.

## What the measurement found instead

Comparing the whole table against the published binding rate — which was only worth doing because
the basis question sent me to compare every row rather than the four the census named — gives
**11 divergences in 32 rows inside the published record**, in four classes:

| Class | Rows | Worst | What it is |
|---|---|---|---|
| **Blind to the EPG** | 2022-10, 2023-01, 2023-04 | **+33.00p/kWh** | Carries the Ofgem CAP where the Energy Price Guarantee bound at 34.0p |
| **Extrapolated over a published series** | 2026-01/04/07/10 | −1.69p/kWh | The table says "Extrapolated 2026+"; the commons publishes 2026 |
| **A window late** | 2024-01 | −1.22p/kWh | Carries the Oct-2023 cap over the Jan-2024 change |
| **Transcription noise** | 2020-01, 2023-07, 2023-10 | 0.05p/kWh | Typed rather than derived |

**2023-01 is the expensive one: a reference rate 97% above what an SVT household was actually
charged**, in the quarter the cap peaked at GBP 4,279 and the EPG held the typical bill at
GBP 2,500. This value is the competitor anchor and the pricing ceiling
(`simulation/competitor_reference.py`, `simulation/svt_product.py`, `simulation/renewals.py`).

The commons **predicted this failure in writing**. `ofgem_default_tariff_cap_windows.json`'s
`epg_note` says both instruments are published separately "so that a lane which fails to notice
the EPG is a lane that MISREAD the law rather than a lane that was handed a different law." A lane
did. The artefact was right that it would happen and there was nothing able to notice.

The 2026 class is this atom's own thesis, four rows wide: **an invented number standing exactly
where an established one exists**, with a comment ("moderate decline as renewables penetration
rises") that reads as reasoning and is load-bearing.

## What this change carries, and what deliberately did not

**In this change:** the `vat_book` repair with its controls, and
`tests/simulation/test_the_elec_svt_table_agrees_with_the_published_cap.py` — 5 tests, 4 mutations
killed (a new divergence, a fail-open tolerance, a fail-silent window filter, a units slip; each
caught by at least two tests).

The control asserts **`divergent ⊆ named`**, not equality: repairing a row shrinks the set and
stays green, a twelfth divergence goes red. Keyed to the property, not to today's answer — a
control pinned to the exact set would go red when the code became more honest.

**Deliberately NOT attempted here: the repair itself.** Making the electricity leg read the commons is
right and is what the gas leg already does, but it moves the world — three of the four classes
change historical values, one by 33p/kWh, and `svt_rates` is the competitor anchor and the pricing
ceiling. That is an R13 baseline change for a fidelity reason, and it deserves its own increment
with the book measured before and after, not a same-turn ride-along on a control.

## What is next, in order

1. **The electricity leg reads the commons**, the way the gas leg does. Pre-register the book move
   before running it: three classes shift historical rates, and if the result moves and all of
   them changed at once it cannot be attributed. The EPG rows alone are the one-variable version.
2. **The EPG is a live reading, not just a table defect.** Whether an SVT reference rate should be
   the cap or the binding instrument is a question the whole `svt_rates` family answers implicitly
   and nowhere states. Ask it once, in the module, in words.
3. **Item 3 of the census finding is still open** — `company/pricing/ofgem_price_cap.py` needs its
   basis stated before it can be sourced or refused.
4. **The census's `by_year` token weakness** and the 189 container-held specificity-1 bindings
   remain measured and undispositioned, exactly as the census finding recorded them.
