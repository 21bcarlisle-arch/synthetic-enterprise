**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
**Knowledge:** unbilled-energy-and-revenue-assurance

# D48's flat estimated share is the book's meters, not the read model: no meter is ever exchanged after acquisition, so in 2024 the book is 29% smart against about 69% nationally (2026-10-21)

*Worker tick, 2026-10-21. This is the "measure first" step of
`docs/staging/done/SEAT_FINDING_D48_THE_ESTIMATED_SHARE_FALLS_ONLY_TEN_POINTS_THROUGH_THE_SMART_ROLL_OUT_2026-10-14.md`
(Expert Hour disqualifier #5). The pre-registration was written before any figure was read:
`docs/staging/records/SEAT_PREREG_D48_THE_ESTIMATED_SHARE_SPLIT_BY_METER_TYPE_2026-10-21.md`.*

## Measured

The published run is `run_output_8b6fea024_20261019T033010Z`, read through `tools/run_output_store`. Its 38,005 bills
are joined to its `meter_read_log` on (customer, period end). The join is one-to-one with no unmatched rows. The meter
type is the log's per-period `meter_type`, which is what the company sees.
**0 of 945 accounts change meter type over their life.**

Estimated share of billed kWh, by period-end year. The count of bills is in brackets.

| Year | Elec: smart accounts | Elec: smart est. | Elec: traditional est. | Gas: smart accounts | Gas: smart est. | Gas: traditional est. |
|---|---|---|---|---|---|---|
| 2016 | 14.3% | 12.5% (259) | 80.6% (1,403) | 13.7% | 16.1% (191) | 80.4% (1,154) |
| 2018 | 14.2% | 8.8% (323) | 78.8% (2,117) | 14.2% | 6.5% (224) | 79.8% (1,641) |
| 2020 | 17.7% | 15.7% (360) | 79.4% (1,815) | 13.6% | 9.0% (236) | 80.9% (1,424) |
| 2022 | 19.1% | 9.6% (394) | 80.9% (1,762) | 15.3% | 7.2% (234) | 76.4% (1,357) |
| 2024 | 29.1% | 7.4% (643) | 80.0% (1,750) | 27.5% | 8.3% (452) | 75.3% (1,377) |
| 2025 H1 | 31.7% | 8.5% (385) | 80.1% (865) | 28.9% | 13.5% (272) | 77.5% (685) |

The odd years sit inside the same bands. To re-run: load the gz, key `bills` and `meter_read_log` by
(`customer_id`, `period_end`), and sum `total_consumption_kwh` by (commodity, year, `meter_type`) and by
`billing_basis == "estimated"`. It takes under a minute.

**Graded against the pre-registration.**
1. HELD. From 2016 to 2024 the smart share rises by 15 points for electricity and 14 for gas. Both are under 25.
2. HELD. Smart accounts bill 6-16% of kWh on estimates in every year, against the CA/BEIS 6% for smart customers. Traditional accounts bill 75-82% in every year.
3. HELD. The read model treats a smart meter as smart. The flat total is the book's composition.

## The cause, in code

- `simulation/population_draw._draw_smart_meter` draws the meter **at acquisition** against
  `premise_population.smart_meter_penetration(acquisition_year)`. That is the DESNZ installed share, 10.6% (2016) to
  68.9% (2024), and it is sourced.
- After acquisition nothing changes it. `life_events.smart_meter_installed` is handled by `apply_events` but never
  emitted. The module docstring has said so since the W2_5 Expert Hour of 2026-07-13: "a real smart-meter-rollout
  event generator is a separate, not-yet-built piece". In any case `meter_reads.meter_type_for_customer` reads the
  acquisition stamp, not the life-event state.
- So a household acquired in 2016 keeps 2016's 10.6% chance of being smart for the whole decade. The book's 2024
  share of 29% is a mix of its cohorts. The national installed share was 68.9%, and about 64% of domestic
  electricity meters were in smart mode (the knowledge note's K2 row: 35.8% of electricity meters and 45.3% of gas
  meters dumb or in traditional mode, end 2024, DESNZ).

## What this means for D48

- The company's measure is honest. It reports what the book's meters let it bill. Disqualifier #5 is a
  **world-fidelity** failure, and the company half cannot fix it.
- At the national smart-mode mix, the rates measured here (about 9% smart, about 79% traditional) would give an
  electricity 2024 estimated share of about 0.64 × 9% + 0.36 × 79% ≈ 34%. That is inside the reviewer's prior
  band for the period (10-20% was its end-point, 35-45% its start). This is arithmetic on the measured rates, not
  a run, and the rates themselves may move once meters are exchanged mid-life.

## The world build it routes (W2, held behind the lane's BLOCKING finding)

A meter-exchange generator for households already on supply. Each year a traditional meter becomes smart with
the hazard that carries the installed stock along `smart_meter_penetration`. Conditioned on still being
traditional, that is (p(y) − p(y−1)) / (1 − p(y−1)). It emits the `smart_meter_installed` event that already
exists, and `meter_type_for_customer` reads the meter type in force at the period, not at acquisition. The
company sees the change as a meter exchange on its own supply point, because the meter type is on the national
metering database. So it crosses the seam as an observable, as the acquisition stamp already does.
- It is a world change for fidelity, decided blind to company results.
- It moves the world digest, so the value-arms re-take is part of its cost.
- **GAP:** no published series says how a supplier's in-book installs differ from the national stock (for
  example, whether switchers are installed faster). The national hazard is the stated belief.
- Not built here. W2 is drawing its BLOCKING bad-debt finding ahead of new feature work, and the change reds the
  arms' digest controls. It needs its own turn.

**Status:** OPEN. Disqualifier #5 is attributed. The world build is routed to W2 as described above.

## Company half, built (worker, 2026-10-21)

The published K2 is now split per fuel and year by meter type, with the book's share of accounts on
a traditional meter beside DESNZ's end-2024 national share of meters
(`billing_accuracy.estimated_share_by_year_and_meter`, the /capabilities/ panel `billacc-k2split`,
knowledge note §2 K2). A reader sees the reading rates hold and the book's meters stay traditional.
It reaches the page at the next publish: the committed run gz is a different book from the
published feed, so the feed was not hand-regenerated. Until then the panel names its absence.
The world build above is unchanged and still routed to W2.


## World build, landed behind a switch (worker, 2026-10-21)

Knowledge first: `unbilled_energy_and_revenue_assurance.md` §4e (the DESNZ stock, the conditional
hazard, and the GAP that no published series separates in-book installs from the national stock).
`life_events.smart_meter_installed_event` emits the existing event per premise at
h(y) = (p(y) − p(y−1)) / (1 − p(y−1)), 8.2% (2017) to 19.0% (2024), and 0 in 2025 where the series is held flat.
`meter_reads.SimulatedReadFeed` reads each period with the meter in force at its end. A dual-fuel
home's two legs are exchanged in one visit. The control is
`tests/simulation/test_a_meter_already_on_supply_is_exchanged_for_a_smart_one.py`: every
acquisition cohort from 2016 to 2023 reaches DESNZ's 68.9% within four binomial standard errors.
Without exchanges a 2016 cohort sits outside that band. Four of five mutations go red. The fifth
(re-exchanging a meter already smart at acquisition) stays green, and that is an equivalence: the
feed returns "smart" for such a meter whatever the event says.

**`meter_reads.SMART_METER_EXCHANGE` is False.** PARKED, not handed off: turn it on only once the
per-customer, opex-credit, bad-debt and retention-netting arms are graded, and re-take the value
arms in the same piece of work, because the flip moves the world digest. A continuation written now would expire
(6 h) long before that trigger. Whoever closes the last of the four grades picks this up.
