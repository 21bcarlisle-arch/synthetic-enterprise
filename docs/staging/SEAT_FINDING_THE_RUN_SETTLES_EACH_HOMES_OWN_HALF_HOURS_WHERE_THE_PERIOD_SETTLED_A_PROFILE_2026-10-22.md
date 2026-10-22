**Severity:** LATENT · **Lane:** W3_industry_systems · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `front-door-four-domain-points-from-the-cold-read` (Lane 0 delivery)

# The run settles each home's own half hours, where 2016–2025 settled a profile

**Found by** the delivery seat on 22 Oct 2026, checking the energy cold reader's settlement point
(`docs/market_research/four_front_door_domain_points_from_the_energy_cold_read_2026-10-22.md` §1).

## What is wrong

In 2016–2025, a GB domestic meter was settled non-half-hourly. Elexon's TOR gives 98.54% of SVA
metering systems as Measurement Class A on 25 May 2022, smart meters included. The supplier was
charged for EAC × the Elexon Profile Class 1/2 coefficients, then GSP Group Correction.
Reconciliation corrected the annual volume, never the shape. MHHS went live centrally on
24 Sep 2025, after `REPORT_END`.

The run settles each home's OWN modelled half hours. `simulation/run_phase2b.py` builds a
per-customer `shape_fn`: the fabric trace, with battery dispatch, where the weather store covers
the home, or the PC1 shape weather-adjusted and levelled to the home's EAC. That shape is priced at
the real system price, period by period. That is MHHS-era settlement applied to a pre-MHHS decade.

## Why it matters, and which way

For a legacy home the gap is small, because its shape IS the PC1 profile, rescaled. For a fabric
home, a battery, or any load the company shifts, the run's wholesale and imbalance cost carry a
timing difference that a real supplier of the period was not charged for and could not have
banked. Any value the per-customer engine draws from WHEN a home uses power is therefore available
here and was not available then. That direction favours the thesis (F11).

I cannot yet say how large it is. No measurement has been made.

## What done means

1. Pre-registered first: the cost difference, per home and per book-year, between settling the
   home's own shape and settling EAC × PC1/PC2 (with a group-correction stand-in), on one seed,
   split by legacy and fabric provider.
2. If it is material, the settled volume of a home without an elective-HH registration becomes the
   profiled one. The company's carbon instrument already makes the same split (measured against
   profiled) and is not affected.

The front door now says plainly that domestic meters of the period were settled on a profile
(Settlement line, "Not yet").

## Measured (22 Oct 2026, one seed, HEAD book)

Done-means step 1 is done. See
`docs/staging/records/SEAT_RESULT_SETTLING_EACH_HOMES_OWN_SHAPE_AGAINST_THE_PROFILE_IS_NEAR_ZERO_FOR_THE_BOOK_AND_TENS_OF_POUNDS_FOR_AN_ELECTRICALLY_HEATED_HOME_2026-10-22.md`
(tool: `tools/profile_settlement_timing_probe.py`).

**Correction to "Why it matters, and which way" above: the direction does not hold for the book.**
With each home on its right profile class, the whole book's timing difference is +0.23% of SSP
cost: the run charges slightly MORE than the period did. Across domestic homes only it is −0.08%.
Legacy and gas-heated homes (517 of 572) sit within ±£4 a year. Per home, though, it is material:
an electrically heated home reads ±£35–150 a year and an SME about +£100. The pre-registered rule
makes it material, so step 2 stands.

Step 2 needs two things first: a PC2 table in `sim/data/`, and a rule that registers a storage or
E7-shaped home on PC2. Today every domestic home is PC1, and against PC1 a storage-heated home
shows a spurious −£91 a year.

## Registration built (22 Oct 2026, later)

The two prerequisites are in: `sim/data/profile_class_2_gad.csv` (UKERC, verbatim; provenance
`docs/data-sources/profile-class-2.md`) and `run_phase2b.registered_profile_class`, which registers
a home the world drew with `ELECTRIC_STORAGE` heating on PC2. The registration keys on the drawn
household, not on `build_properties`. That record defaults to `electric_storage` for every home
without a gas account, and at HEAD it says `electric_storage` for 85 homes the world drew with gas,
communal, oil or heat-pump heating. Census at HEAD: 36 of 568 non-HH resi homes are drawn
storage-heated.

**Prediction, written before the re-run of `tools/profile_settlement_timing_probe` with the rule
in place:**

- R1. Between 5 and 17 legacy-path homes move to PC2. The rest of the 36 are fabric homes.
- R2. A legacy home that moves to PC2 still shows mean |Δ| under £5 a year, because on the legacy
  path both arms are its profile.
- R3. The book Δ moves from −0.54% to between 0.0% and +0.5% of SSP cost. Registration by heating
  system is not the same cut as the earlier "night-heavy ≥ 38%" one, so it will not land exactly on
  +0.23%.

**Graded (same day, 12-minute re-run at the rule, one seed, HEAD book):**

- R1 **holds, at its top edge.** 17 legacy homes move to PC2. The other 19 storage homes are the 19
  night-heavy fabric homes the first measurement found by shape. The heating rule and the shape
  cut agree home for home, and the 9 day-heated electric homes stay on PC1, which is right.
- R2 **holds.** Legacy PC2 mean |Δ| is £1.1 a year (−0.38%).
- R3 **holds.** The book is +0.24% (£3,096 on £1.306m). The night-heavy fabric homes now read
  −£16.9 a year against their own class, not −£91.
- **What the rule changes in the run itself:** the 17 legacy storage homes' settled SSP cost
  falls from £37,420 to £34,838 (−6.9%, about −£18 per home-year), because their legacy shape is
  now night-loaded. Fabric homes are unchanged: they still settle their own trace, which is what
  step 2 is for.

Step 2 is not built. `hedged_settlement.run_hedged_term` uses one `consumption_shape` for
revenue, wholesale cost, levies and billed kWh, so settling on the profile needs a second,
settled shape. That shape goes to the wholesale and imbalance legs only, trued up to the home's
own volume over the term. It is handed off as a continuation.

## Step 2 built (22 Oct 2026, evening)

A fabric home without HH settlement is now billed on its own trace and bought on its registered
profile, trued up to its own volume over each term (`hedged_settlement._settled_volumes`, passed
from the fabric branch of `run_phase2b` to `run_hedged_term` and `run_deemed_term`). Legacy homes,
HH and I&C sites, time-of-use terms and a mover's carried term keep their own shape, each for the
reason in the pre-registration
(`docs/staging/records/SEAT_PREREGISTRATION_A_PROFILED_HOME_SETTLES_ITS_OWN_VOLUME_ON_ITS_REGISTERED_PROFILE_2026-10-22.md`).
P15a and P15b held at full book. The run-level effect after hedging is ungraded until a run
publishes. The PC3 SMEs' +£100 a year does not move: it is the weather adjustment against the raw
1997 table, which the profile's missing temperature regression leaves as a GAP. This finding's
done-means is met. It stays open only until that run is graded.
