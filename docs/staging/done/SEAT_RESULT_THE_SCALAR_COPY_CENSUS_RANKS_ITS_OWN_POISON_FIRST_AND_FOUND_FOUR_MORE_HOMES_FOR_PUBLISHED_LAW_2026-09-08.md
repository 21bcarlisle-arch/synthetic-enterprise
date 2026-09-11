**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a-scalar-copy-of-one-row-of-a-published-series-is-invisible-to-every-census

# The scalar-copy census ranks its own poison first, and found four more homes for published law

**2026-09-08. Lane 0 delivery.** Claim:
`a-scalar-copy-of-one-row-of-a-published-series-is-invisible-to-every-census`.

Built: `tools/published_row_scalar_census.py`. Controlled:
`tests/architecture/test_published_row_scalar_census.py` (7 tests, 3 mutations killed).

---

## What was asked, and what "done" was taken to mean

The steer: *build the AST pass that flags a module-level numeric constant in `company/`, `saas/`
or `simulation/` whose value matches, within rounding, any row of any series held in
`docs/domain_artefact_library/`, and RUN IT AS THE CENSUS before writing any control over it.*

Done was taken to be: the pass exists, the population is measured rather than assumed, the
ranking is proved to rank the motivating case FIRST, and every hit in the top stratum carries a
disposition. It is not taken to be "the code changes have landed" — those are named below and are
the next increment.

## The population

```
1,982 published rows (9 JSON artefacts)  x  3,508 module-level numbers in company/, saas/, simulation/
  EXACT matches:   10,023 pairs
  SCALED matches:  23,627 pairs   (a unit conversion away)
  UNITS AGREE:         64 distinct bindings   <- the ranked population
  units agree AND specificity 1:  20 rows     <- dispositioned in full below
```

Specificity-1 across the whole population (before the unit rank) is **368 bindings — 179 bare
scalars and 189 held inside a module-level container.**

## The instrument had to be built twice before it measured anything

Recorded because the shape will be reached for again, and because it is the argument for the
steer's own instruction to run the census before writing the control.

**Draft 1 read "within rounding" as half a unit in the published row's last decimal place.** A row
published as the integer `15` then admitted every constant in [14.5, 15.5]; that one row accounted
for 4,356 of 14,769 hits. The population was mostly the instrument.

**Draft 2 compared at whichever side claimed fewer decimal places.** The same defect mirrored — a
constant written `3.0` claims none, so it admitted everything in [2.5, 3.5]. The population went
UP, to 63,653.

Decimal places were the wrong dimension both times. What a rounded copy preserves is *significant
figures*, so the comparison is relative. Both failed drafts are pinned as refusals in
`test_within_rounding_admits_a_transcribed_copy_and_refuses_a_different_number`.

## The ranking axis was chosen by the poison round, not by argument

The first candidate rank was **significant figures** — a collision on `0.006948` is a fingerprint,
one on `3` is a coincidence. It was rejected by feeding the historical defect back in:
`_CAPACITY_MARKET_GBP_PER_KW_YR = 75.0` carries **two** significant figures, so any floor at three
would have hidden the exact case the pass exists for. **That is the defect being closed —
discovery narrower than the thing it governs — reappearing one level up as a rank.**

The axis that survives is **specificity**: how many distinct published rows a value collides with
across the whole commons. `75.0` collides with exactly one —
`capacity_market_auction_results#clearing_prices/6/t1_gbp_per_kw_year`. `0.9` collides with dozens.
The poison round ranks top, and `test_the_poison_is_the_most_specific_collision_the_commons_can_produce`
holds that shut.

A second axis was needed because specificity alone does not rank far enough:
`_MINUTES_RETENTION_YEARS = 10` is also a specificity-1 collision, against a published
`awarded_cmu_years = 10`, and has nothing to do with it. So both sides are asked **what the number
counts** — CLAUDE.md's "before dividing two numbers, say out loud what each one counts", applied to
comparing them. Reported, never filtered: a pair where either side names no unit is UNRANKED, so a
copy named `_X = 75.0` still reaches the reader.

## Disposition of the top stratum — all 20 units-agree, specificity-1 rows

### SOURCED (4 bindings, 2 modules confirmed, 2 strong)

| Constant | Published row | Reading |
|---|---|---|
| `company/finance/vat_book.py:25 SME_ELEC_THRESHOLD_KWH_PER_DAY = 33.0` | `vat_fuel_and_power_de_minimis.json#de_minimis_by_fuel/electricity/kwh_per_day = 33` | **The same law.** Cited only in a code comment ("HMRC concession"), while the commons holds the published figure. |
| `company/finance/vat_book.py:26 SME_GAS_THRESHOLD_KWH_PER_DAY = 145.0` | `…/gas/kwh_per_day = 145` | Same. |
| `simulation/svt_rates.py:21 _SVT_ELEC_PENCE_PER_KWH` (4 keys) | `ofgem_cap_unit_rate_composition.json#…/unit_rate_p_per_kwh_ex_vat` | **Same quantity, same unit.** And the module's own docstring already states the rule: *"GAS is not [a table here] … the published gas cap already has a home in the regulation commons, and this module reads it rather than restating it."* The electricity leg restates it, in the file that documents why not to. |
| `company/pricing/ofgem_price_cap.py:66 _ELEC_CAP_GBP_PER_MWH` (2019, 2023) | `ofgem_cap_unit_rate_composition.json#cross_check_against_published_cap_levels/rows/*/derived_gbp_per_mwh` | A further home for the cap, as hand-commented annual averages ("~17p/kWh … conservative"). Two of seven rows agree within rounding; the rest are an annual mean of a quarterly series, so the disagreement is a basis difference nobody wrote down. |

**This is the VAT shape again** — the one CLAUDE.md names as the canonical case: one legal
requirement, several implementations, and nothing able to notice they disagree.

### REFUSED, with the reason named (15 bindings)

* **"Years" is the same word for two different things** (7): `_CERT_PERIOD_YEARS`,
  `_MINUTES_RETENTION_YEARS`, `EPC_VALIDITY_YEARS` against `awarded_cmu_years = 10`. A meter
  certification period is not a count of Capacity Market CMU-years.
* **`by_year` is a KEY, not a unit** (5): `_NON_COMMODITY_ELEC_RESI_BY_YEAR`,
  `_NON_COMMODITY_GAS_RESI_BY_YEAR`, three tables in `simulation/policy_costs.py`. These rank as
  units-agreeing only because both names contain "year" — **a real weakness in the instrument's
  own unit vocabulary, and it is written here rather than quietly patched**, because suppressing
  the token would also suppress `gbp_per_customer_year`, which is a genuine unit.
* **Same unit, different quantity** (3): `DCC_COMMS_CHARGE_GBP_PER_YEAR = 14.32` against the CM
  levy's `gbp_per_customer_year = 14.3086`; `PUBLISHED_EPC_BAND_SHARE['C'] = 0.448` against a
  commodity share of a unit rate.

### NOT A DEFECT — the collision is agreement (1 binding)

`company/market/market_report.py:59 _UK_SWITCHING_RATE_PCT[2021] = 18.2` collides with
`gb_domestic_switching_rate.json#values_refuted_by_the_publisher/comparison/1/published_rate_pct
= 18.195`. The pointer looks alarming and the reading is the opposite: 2021 is one of the two
years in ten where this table **agrees** with the publisher. Filed as a refusal so the next reader
does not re-open it.

## The comment at line 254 stays, and gains a pointer

The steer said the comment in `tests/architecture/test_year_keyed_rate_table_census.py:254` "comes
out when it stops being true". **It has not stopped being true.** It says *that* census discovers
year-keyed dicts and is therefore blind to a scalar copy — which correctly bounds itself and is
still exactly right. What changed is that something else now covers the hole. Deleting a true
self-bound to record that a different file exists would make the year-keyed census read as wider
than it is. A pointer is added instead.

## What is next, in order

1. **`company/finance/vat_book.py` loads the de minimis thresholds from the commons.** Smallest,
   clearest, and it is the VAT class the director has already paid for twice.
2. **`simulation/svt_rates.py` electricity leg reads the commons**, the way its own gas leg
   already does.
3. **`company/pricing/ofgem_price_cap.py`** — needs the basis stated (annual mean of a quarterly
   published series) before it can be sourced or refused; that is a reading, not a lookup.
4. **The `by_year` token.** The unit vocabulary needs to distinguish a keying word from a unit.
   Named above; not fixed here, because the fix is a judgement about five constants and the
   census should be read before it is tuned again.
5. **The 189 container-held specificity-1 bindings and the 348 unranked ones** are measured and
   undispositioned. That is the honest state, not a backlog claim.
