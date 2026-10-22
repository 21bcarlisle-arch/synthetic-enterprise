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
