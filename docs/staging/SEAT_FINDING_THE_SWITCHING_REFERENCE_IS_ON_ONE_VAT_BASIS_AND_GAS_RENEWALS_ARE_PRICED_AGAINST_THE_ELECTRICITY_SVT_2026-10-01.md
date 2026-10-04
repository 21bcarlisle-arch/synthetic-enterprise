**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `unminted` — Lane 0 delivery

# The switching reference is on one VAT basis, and gas renewals are priced against the electricity SVT

Claim `compare-the-switching-reference-on-one-vat-basis`. These are results against
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_PUTTING_THE_SWITCHING_REFERENCE_ON_ONE_VAT_BASIS_MOVES_2026-10-01.md`,
which was written before either run. The parent is handed-on item 2 of
`SEAT_FINDING_THE_SVT_SEGMENT_NOW_BILLS_EX_VAT_AND_NO_FIRST_TERM_SITS_ABOVE_THE_EX_VAT_CAP_2026-10-01.md`.

The duplicate-work note at draw time named this same id as "already held". It was the draw's own
write: no other seat or `surgical_land` process carried the item. So the work was done, not
disposed of.

## What changed

There is one helper, `simulation/price_cap_enforcement.household_price_inc_vat(ex_vat)`, which
returns `ex_vat × (1 + DOMESTIC_VAT_RATE)`. Six sites now take the gross-up from it:

1. `customer_events._price_differential_vs_market`: the churn roll's offer.
2. `customer_events._reference_level_gbp_per_mwh`: the ledger's ex-VAT position, before it reaches
   the rival.
3. `competitor_reference.competitor_reference_rate_gbp_per_mwh`: the rival's ex-VAT cost floor.
4. `customer_events._svt_position`: the logged `price_differential_vs_svt`.
5. `tools/run_price_ladder._svt_position_pct`: the reconciler of site 4.
6. `run_phase2b._build_churn_basis_risk`: `rate_vs_svt_pct`.

The item named only site 1. Fixing only that would have left sites 4–6 5% apart from it, with no
rival present, under names the 2026-08-28 reconciliation requires to agree.

## The controls

- **Twelve controls were re-keyed.** They fed an ex-VAT offer of `SVT × f` and expected `f − 1`.
  Each now feeds the ex-VAT rate a household sees as `SVT × f`. The re-keyed set was run against
  HEAD's code: **all 12 go red**, so each of them controls a gross-up.
- **One new control:**
  `test_price_cap_vat_basis::test_every_logged_SVT_position_reads_a_struck_rate_on_the_published_basis`.
  Sites 4–6 had no control. Each of its three legs was mutated separately (HEAD's code at that one
  site only), and each went red on its own leg: −0.0476, −4.76 and −4.76.
- **Wider run:** 1,395 tests pass across the reference, churn, price-ladder, value-pricing,
  `run_phase2b` and `saas/reporting` suites.

## Results: one variable, two runs of the default world from origin/main `50bde35ab`

Both runs are `git archive` extracts of the same commit; one adds exactly this diff. The world
had 256 customers, 107 renewal events in each run, and all 107 matched one-to-one.

| prediction | base | with change | verdict |
|---|---|---|---|
| P1: `vs_svt` = `(1+base)·1.05 − 1`; same for `rate_vs_svt_pct` | | **0 of 107 mismatches**, both fields | HOLDS |
| P2: reference never falls; mean +0–2% | 162.96 | 166.32 (+2.07%); 0 fell, 99 rose | direction HOLDS, size **just over the band** |
| P3: mean differential vs market rises by 3.0–5.5 pp | −13.14% | −10.78% (**+2.36 pp**) | **REFUTED**, low |
| P4: mean realized churn probability rises 10–40% | 0.3299 | 0.3342 (**+1.3%**); 0 fell | **REFUTED**, far low |
| P5: renewal churned count rises 10–45% | 38 | **38** | **REFUTED** |
| P6: share of offers reading cheaper than the SVT falls | 98.1% | 90.7% | HOLDS |
| P7: more churn, never less | | 0 of 107 fell | HOLDS |

Rows are in `/var/tmp/se-vatref-{base,new}/vatref_rows.json`; the comparison script is
`/var/tmp/se-vatref-compare.py`.

### Why P3 came in low

The rival absorbed part of the 5%. It now reads the company at its real, dearer price, so it
chases it less far down. Its floor also rose by the same 5%, so every event that sat on the floor
in base moved its offer and its reference together, and its differential did not change at all.

### Why P4 and P5 came in far low, and what this says about the curve

My prediction took the curve's ratio to reach the decision nearly whole. It does not. Over the
94 electricity renewals whose differential moved:

- `churn_position_multiplier` rose by a median **+16.9%**;
- the realized churn probability rose by a median **+0.87%** (mean +1.8%);
- so pass-through is about **6.5%**.

`_price_response` scales one cause among the competing risks in `build_departure_risks`. The
dilution is consistent with that cause being a small share of the total, but I have not
decomposed it, so I cannot yet say that is the whole of it.

With the probability shifting about one point, no roll in a 107-renewal world crossed. Zero
churn change is what a world this size gives for a 1% move. It is not evidence the change is
inert.

This bears on PB3's premise that price is "the largest lever". At the book's real positions, a
5-point repricing of every offer moved realized churn by about 1%. That is worth a deliberate
look rather than an assumption.

## Found on the way: gas renewals are priced against the electricity SVT

`_price_differential_vs_market` has no commodity argument. `_reference_level_gbp_per_mwh` reads
`get_svt_elec_rate_charged_to_household_gbp_per_mwh` for every leg. So each **gas** renewal sets a
gas £/MWh offer against the electricity SVT. All 6 gas renewals in both runs read
**−0.77 to −0.85**: about 80% cheaper than the market.

That is past the curve's saturation at −0.30. So every gas household's price factor is pinned at
the curve's minimum, 0.2273, whatever the company charges for gas. Gas pricing has no
consequence on the departure side.

`svt_rates` has carried gas accessors since 2026-09-06, so the fix is a commodity argument
threaded to the reference. It will move gas churn substantially, upwards, so it needs its own
pre-registration. `_svt_position`, `run_price_ladder._svt_position_pct` and
`_build_churn_basis_risk` have the same shape for gas legs. Handed on as
`price-the-gas-renewal-against-the-gas-svt`.

## Not touched

`company/` and `saas/` hold their own SVT comparisons, which are the company's beliefs. A wrong
belief there is a belief-versus-truth gap, not a world defect. They were not changed.
