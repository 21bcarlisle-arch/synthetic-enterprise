**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** W2_30_per_household_half_hourly_electricity_and_seasonal_gas_shape

# The gas heating fraction spans 0.25 to 0.95, and every household was handed 0.70

**2026-09-08. Scheduled tick, LANE 1 BUILD draw:
`W2_30_per_household_half_hourly_electricity_and_seasonal_gas_shape` (level 0 → 3, loop_stage
build).**

---

## The electricity half was already built, wired and measured — I did not build it again

W2_30 names two deliverables. The atom's own note says the world "rescales one national profile, so
every household has the same time-of-use cost profile". **That is no longer true of electricity and
has not been for some time.** `fabric_demand_path.fabric_providers_for_book` drives every eligible
premise's half-hourly electricity from W1_11 fabric physics and W1_12 behaviour, and
`run_phase2b` settles real money off it (`simulation/run_phase2b.py:1222`).

`tools/book_shape_spread.py` — which had no caller and no test, and which I ran rather than rewrote
— measures the property the director actually set: normalise every premise-day by its own total, so
the level is divided out and only the shape is left.

| 2022-01, cells C1–C4 | mean abs. half-hourly share difference | closest pair | identical pairs |
|---|---|---|---|
| fabric path, electricity (5,778 pairs) | **0.006463** | 0.00294885 | 0 |
| fabric path, gas (5,778 pairs) | 0.014140 | 0.00346243 | 0 |
| legacy path, electricity (36 pairs) | 0.003446 | **0.00015818** (family1 vs single1) | 0 |

The legacy path's closest pair sits at 1.6e-4 — the collapse the switch exists to remove, and the
one the director spotted himself ("identical to four decimals is the tell"). The fabric path's
closest pair is twenty times further apart. **So the electricity deliverable is done, and the
correct action on it was to establish that and stop.** Building a second copy under a new name is
this project's recurring defect and I was one search away from it.

## The gas half was not built, and `run_phase2b` says why in its own words

> "GAS IS DELIBERATELY NOT SWITCHED. `run_gas_term` takes an AQ, not a shape_fn ... Driving gas
> demand from fabric while the AQ belief stays frozen at its declared value would lock in a
> permanent 4x hedge mismatch no real supplier could carry, which is an absurdity, not a gap."

**That objection is correct, and it answers a question the canon did not ask.** It assumes switching
gas means replacing the AQ *level* with fabric volume. DIRECTOR_CANON_THE_DEMAND_VECTOR_2026-09-07
sets the two resolutions from the PRICE, not the physics: electricity needs half-hourly because that
is where the price and the settlement live; **gas needs only a seasonal shape, because the price
does not move within a month.** A seasonal shape says WHEN the year's volume is consumed, not how
much of it there is. The level never moves, so the mismatch that stopped the switch cannot arise.

## What was actually wrong, and how big it is

`gas_settlement` split every domestic customer's gas the same way: 70% space heating scaling with
the day's HDD, 30% DHW and cooking flat. `_GAS_BOILER_HEATING_FRACTION = 0.70` is properly sourced
(DUKES Table 4.3, calibrated to a Jan:Jul ratio of ~5.3x) and it is **a population average being
used as a per-household parameter**.

I fitted each household's own fabric-physics daily gas series onto exactly that two-term form —
27 households crossing build era × insulation × property type, C1 weather, calendar 2021:

```
POST_2000/PARTIAL/FLAT1     frac=0.250   r2=0.211   annual= 1,614 kWh
POST_2000/POOR/FLAT1        frac=0.371   r2=0.494   annual= 1,798
ERA_1965/FULL/FLAT1         frac=0.393   r2=0.418   annual= 2,376
...
PRE_1919/PARTIAL/DETACHED5  frac=0.874   r2=0.920   annual=34,804
PRE_1919/FULL/DETACHED5     frac=0.913   r2=0.864   annual=19,376
ERA_1965/FULL/DETACHED5     frac=0.945   r2=0.785   annual=10,164

n=27  min=0.250  p10=0.371  median=0.746  p90=0.885  max=0.945
```

**The fraction spans 0.250 to 0.945. Every one of them was settled at 0.70.** A modern insulated
flat spends a quarter of its gas on space heating and three quarters on hot water and cooking; a
draughty pre-1919 detached is the other way round by a factor of four. Under the shipped code those
two homes had the same seasonal shape to every decimal place.

**The population figure is not refuted — it is confirmed, and that is the point.** The median of the
fitted distribution is 0.746 against DUKES's 0.70. The constant was right about the population and
wrong about almost every household in it, which is precisely the atom's real-world twin.

## What landed

- `simulation/household_demand_shape.py` — fits a household's own daily gas onto settlement's
  two-term form and reports the fraction it implies. It **fits, it does not generate**: the physics
  is W1_11/W1_12's and the parameterisation is `gas_settlement`'s.
- `simulation/gas_settlement.py` — `resi_daily_gas_kwh` is now the ONE implementation of the daily
  two-term form; `run_gas_term` gained `heating_fraction=None`, which defaults to the population
  constant and is byte-identical to the shipped behaviour (23 existing gas tests pass unchanged).
- `simulation/run_phase2b.py` — builds one reference year per domestic gas household, fits its
  split, and passes it. Households that keep the population constant are printed **with their
  reason**, the same discipline the electricity side already uses.
- `tests/simulation/test_household_demand_shape.py` — 21 controls, each naming its defect.

**The controls are keyed to the property, not to today's answer.** `test_the_fit_recovers_the_
fraction_the_series_was_built_at` is parameterised over 0.35/0.55/0.70/0.85: a fit hard-wired to the
population constant passes a single-value test and fails this one at 0.35. The spread control gets
its poison round first — `test_a_book_of_identical_fractions_fires_the_spread_control` asserts the
control REFUSES a book where everyone got 0.70, so its pass on a real book means something.

**An honest None, never a plausible number.** A window with no cold days cannot tell the two terms
apart, and any fraction fits it equally well; that returns a `SeasonalGasRefusal` naming its reason
and the household keeps the population constant. Same for a window under 60 days, and for gas that
does not rise with cold — which is refused rather than given `0.0`, because "this home does no
heating" is a claim and "we cannot tell" is the result.

**Fit quality is reported and never filtered on (R12).** r² runs from 0.211 to 0.946. The two-term
form describes a lossy pre-1919 house well and a modern flat badly. That is a finding about the
form, not a reason to drop the household so the book looks tidier.

## Not validated, and that is a director decision

Canon section 6: the only household shape artefact available is Elexon Profile Class 1 — one
population-average curve on a 1997 reference year — and SERL's half-hourly panel is
accredited-access and is NOT pursued. Every split carries `validated == False` permanently:
there is no argument that sets it and no code path that returns True, and
`test_no_split_can_ever_claim_it_was_validated` fires the moment one appears.

## What is next, in order

1. **`NOT_VALIDATED_STATEMENT` reaches no reader-facing surface yet.** It exists, it is tested for
   content, and the run prints "MODELLED AND NOT VALIDATED" beside the household list — but the
   atom's exit asks for it on the page, not in a log. That is the outstanding half of exit criterion
   two and it is the next item.
2. **W2_29's acceptance has not been re-run over the full vector with this in it.**
   `simulation/population_coverage.py` still declares `blind_to=("seasonal_gas_shape",
   "half_hourly_electricity_shape")` — both components now exist, and the coverage claim has not
   been re-measured against them. Exit criterion three.
3. **`tools/book_shape_spread.py` has no caller and no test.** It is the measurement that decides
   this atom and nothing runs it. It is in the `no_caller_and_never_runs` population today.
4. **The gas split is fitted on one reference year and reused for the whole window.** Justified —
   the split is a property of fabric and occupancy — but not measured. Whether it drifts across a
   ten-year window with life events in it is unasked.

**Level moved 0 → 2, not 3.** The mechanism is built, wired into the run that settles money, and its
controls have had their poison round. It is not at target because two of the three exit criteria are
outstanding and named above. A row claiming 3 here would be claiming a reader can see something no
reader can currently see.

## One thing I could not clear, and it is not mine

`tests/architecture/test_static_quality_ratchet.py` is red on `I001: 1309 → 1308`. Proved against a
clean `git archive HEAD` extract: the single differing file is
`tests/tools/test_generate_maturity_map_data.py`, which another lane has fixed in the shared working
tree and not committed. My own contribution to the delta was one file
(`gas_settlement.py`, reordered by `ruff --fix`) and it is restored, so the census now differs from
the baseline only by that other lane's improvement. Banking a baseline from this tree would freeze
their uncommitted state and wedge every lane, so I did not.
