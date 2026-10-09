**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** W2_20_mains_gas_is_drawn_not_inferred_from_the_heating_system

# The supply fact is drawn, but the gas register still follows the boiler, and a sixth of gas boilers have no gas supply

## What was measured

Measured on the production path (`net_new_acquisition.STOCK_FROM_FITTED_JOINT = True`, so
`draw_premise_from_joint`), with 6,000 premises, seed 42, as_of 2023-06-01:

| `has_mains_gas_supply` | individual gas boiler | share of homes |
|---|---|---:|
| True | yes | 75.4% |
| True | no | 7.6% |
| **False** | **yes** | **15.3%** |
| False | no | 1.7% |

The supply flag's own marginal is right: 17.0% have no supply, against DESNZ's published 16%
(2023, GB, which DESNZ says is an underestimate) and NEED's raw 19.1% (a ceiling). That is now
held by `tests/simulation/test_the_mains_gas_marginal_recovers_the_published_off_grid_share.py`.
The supply flag reaches nothing, though. `DrawnPremise.commodity`
(`simulation/premise_population.py`) picks the gas register from `heating_system`. So the
direction this atom set out to reverse, supply inferred from the system, is still the direction
the world bills on.

## Why it cannot be fixed by conditioning heating on supply alone

`published_heating_weights()` drops oil, LPG and district heat (5.2%) and renormalises what is
left. That puts gas boilers at **90.7%** of homes, above the **83%** supply share. If a gas boiler
required a supply, both marginals could not hold. The ruling for this atom says a shift in the
heating marginals is a fidelity decision taken blind to P&L, not a side effect. So this is filed
and not absorbed.

Some of the 15.3% is real:

- NEED's "no supply" includes meters it could not match to an address;
- it includes connected homes using under 1,000 kWh a year;
- EHS's 86% "gas-fired" includes communal gas.

None of those is an individual combi or system boiler with no gas meter. The real share of that
combination is not established anywhere this repo holds.

## Proposal

1. **Knowledge first.** Find the published conditional: EHS main heating fuel by gas-grid
   connection (the EHS physical survey records both), or the census 2021 central-heating type
   cross-tabulated against DESNZ's meter-based off-grid share at LSOA level. Until one is found,
   P(individual gas boiler | no individual gas meter) is a named `None`, not a guess.
   *Done 2026-10-07, same day. Correction to "not established anywhere" above: EHS 2017-18
   Annex Table 3.5 publishes main fuel by gas-meter presence from the physical survey. 0.72% of
   gas-fired homes have no meter, and its note 3 says those are LPG or bottled gas. So a mains-gas
   boiler with no gas supply is **0 by measurement**, against the world's 15.3%. With oil and
   communal heat restored, the published stock is consistent: gas-fired 83.6% at DESNZ's 16%
   off-gas, electrical 9.3%, oil 4.4%, communal 2.1%, solid fuel 0.6%. The conditionals table and
   the pre-registered joint are in
   `docs/market_research/mains_gas_is_a_meter_fact_not_a_grid_fact_need_2026.md`. Step 2 is
   now a build against a published joint, not a fidelity judgement waiting for a number.*
2. **Then build** heating conditional on supply. Restore oil/LPG and district heat as drawable,
   non-billable heating so the renormalisation stops inflating the gas share. Pre-register what
   it moves first: the share of the book on a gas register falls by up to about 15 points, which
   moves every gas P&L figure. Decided blind to those figures.
3. `commodity` then reads the supply flag. The test
   `test_the_meter_fact_is_not_folded_into_the_heating_system` stays as it is: it refuses a
   FOLD, and conditioning is not a fold.

## Level

W2_20 is recorded at **L1**: the attribute is built and on the production path, and its
marginal is held against the published share. L2 waits on step 2. Until the supply reaches the
register, "drawn, not inferred" is true of the attribute and false of the bill.

## Step 2 is bigger than a heating-weight swap (worker, 2026-10-07)

Read on origin's base before building. Conditioning the draw is the smallest part. The world has
nowhere to put the restored stock:

- **No oil, LPG or solid-fuel system exists.** `HeatingSystem` (`simulation/household.py`) has
  `DISTRICT_HEAT` and `NONE`, and nothing for a home heated by a fuel no supplier meters.
- **`DISTRICT_HEAT` is billed on electricity at 1:1.** `fabric_physics` returns `heat_kwh` as
  fuel, and `premise_trace` sets `heating_commodity = "electricity"` for anything not gas-heated.
  So drawing communal heat today would put a flat's heat on its electricity meter, which is the
  same error as the 15.3% with the fuel changed.
- The interim of drawing off-gas homes as electric only (no new system) puts ~16% of homes on
  electric heat against the published 9.3%. It swaps one wrong bill for another, so it is not
  taken.

So the build is: (a) a heating system whose heat reaches **no** register (oil, LPG, solid fuel,
communal), with fabric tables and the trace's heat and DHW legs reading it as unmetered;
(b) heating drawn from EHS AT3.5's P(fuel | meter) given `has_mains_gas_supply`; (c) `commodity`
reads the supply flag. Then (d) the value arms get re-taken, because the world digest moves.

**Pre-registered, before any measurement (n=6,000, seed 42, as_of 2023-06-01, production path):**

| quantity | today | predicted after (a)-(c) |
|---|---:|---:|
| homes with a gas boiler and no supply | 15.3% | 0.0% exactly |
| homes on a gas register | 90.7% | 81.5-84.5% (0.987 x 83%, plus nothing for LPG) |
| homes on electric heat | ~8.4% | 8.5-10.5% |
| homes whose heat reaches no register | 0% | 6.0-8.0% |
| `has_mains_gas_supply` marginal | 17.0% | 17.0%, unchanged (a different substream) |

If the gas-register share lands outside 81.5-84.5, the prediction failed and the cause gets
named before anything is tuned.

## The builder's own arithmetic, filed before the build was measured (worker, 2026-10-07)

The table above was written against DESNZ's 16% off-gas. The world draws 17.0% (`s`), so the
AT3.5 conditionals predict, before any run:

- gas register: (1 - s) x 0.987 = **81.9%**, inside 81.5-84.5;
- electric heat: (1 - s) x 0.0094 + s x 0.534 = **9.9%**, inside 8.5-10.5;
- heat on no register: (1 - s) x 0.0038 + s x 0.467 = **8.2%**, which is **above the 6.0-8.0 band**.
  At n=6,000 the standard error is about 0.35 points, so I expect that row to fail narrowly. The
  band was set at s = 0.16 (7.8%) with little margin. If it fails, the cause is the world's 17%
  against DESNZ's 16%, and nothing gets tuned.

Choices made in the build, stated before the measurement:

- Two new systems, not one: `NON_MAINS_FUEL_BOILER` (oil, LPG, solid fuel; an individual boiler)
  and `COMMUNAL_HEAT` (a heat network billed by the building). Their fabric tables are
  **inherited** from the system boiler and from district heat. They are not sourced.
- `DISTRICT_HEAT` stays as it was. It is the authored warehouse's system, still billed on
  electricity. Changing it would move commercial bills in the same commit.
- Electrical splits into heat pump and resistive in the existing ratio (0.008 : 0.08). Gas-fired
  splits combi to system at 0.70, as before.
- A gas-metered home heated by oil, communal heat or solid fuel (0.4% of metered homes) has no gas
  burner. Its `commodity` is electricity, so no gas account goes on a register that burns nothing.

## Measured after (a)-(c) (worker, 2026-10-07)

Production path, n=6,000, seed 42, as_of 2023-06-01, ids `PSTK-W220-00000..05999`.

**A correction to "today" first.** On these ids the unmodified origin code (`067493aa4`) draws
**16.6%** with no supply and **15.0%** with a gas boiler and no supply. It does not draw 17.0% and
15.3%. Those figures came from a different id set. The supply marginal is **16.6% before and after**
the build, as pre-registered: it is drawn from the joint cell, which the build does not touch.

| quantity | pre-registered | builder's arithmetic at s=0.166 | measured | verdict |
|---|---:|---:|---:|---|
| gas boiler, no supply | 0.0% exactly | 0.0% | **0.0%** | PASS |
| on a gas register | 81.5-84.5% | 82.3% | **82.2%** | PASS |
| electric heat | 8.5-10.5% | 9.6% | **9.7%** | PASS |
| heat on no register | 6.0-8.0% | 8.1% | **8.07%** | **FAIL, by 0.07 pt** |
| no supply | unchanged | unchanged | **16.6% both** | PASS |

**The failed row's cause, named before anything was tuned.** The band was set at DESNZ's 16%
off-gas: 0.84 x 0.0038 + 0.16 x 0.467 = 7.8%, with 0.2 points of headroom. The world draws 16.6%
off-gas, inside the published bracket of 16% to 19.1%, and that alone gives 8.1%. The measurement
matches the conditionals the build applies, so it is the band's arithmetic that missed. The
conditionals are not wrong. Nothing was changed in response.

Drawn mix: gas combi 3,479, gas system 1,454, non-mains boiler 366, storage 301, direct 223,
communal 118, air-source heat pump 59.

**Controls:** `tests/simulation/test_heat_that_reaches_no_register.py`. The partition is asserted
first: all three heat routes are drawn. Mutations, each applied and reverted:

- billing unmetered heat on electricity again: 2 of 5 red;
- drawing heating independently of supply: 2 of 5 red;
- `commodity` ignoring the supply flag: 1 of 5 red.

`test_the_mains_gas_marginal_recovers_the_published_off_grid_share.py` needed a new refused
arm. Inferring supply from the drawn heating now lands near the supply by construction, so the
refused arm is the unconditioned heating weights (9.3% off-gas), and it still falls outside the
bracket.

**Not built here, and named:**

- An oil or LPG boiler's pump and fan draw electricity. `boiler_pump_kw` gives a pump only to gas
  boilers, so those homes' electricity is understated by about the same amount it was overstated
  for gas homes before 2026-10-06.
- The supplementary electric heater is drawn only for gas-heated homes.
- `fabric_demand_path`'s comfort-constraint bill reads an unmetered home's electricity as its
  heating bill. An oil home's fuel bill exists and is not modelled.
- Step (d), re-taking the value arms in the new world, is owed. The `homes` and `demand` digests
  move with this build.

## The level: L2 is earned, and recording it needs a seat decision (worker, 2026-10-07)

By the map's definition, `81732ffe2` earns L2: the drawn supply reaches the bill, and the controls
can fail. The level move was written and then refused at the gate by
`tests/test_coupled_triad_gate.py::test_no_live_world_atom_stepping_to_l3_is_refused_for_want_of_a_twin`.
A world atom at L2 that aims at L3 needs a company twin registered in
`background/coupled_triad._AUTHORITATIVE_COUPLING`, and W2_20 has none. So the row stays at **L1**.

Two ways out, both the seat's call. I am not taking either from a bounded tick, because W2_20's L3
comes from a director ruling.

1. **Recommended: retarget to L2**, on the `6314e5bc8` precedent (W1_7, W1_10 and others). A
   supplier holds the MPRN, so whether a home has a gas supply is something it reads, not
   something it infers. No company belief about it can be wrong in the way a twin measures.
   Restore condition: a company grade that reads an off-gas belief. One candidate is C14's
   `couple_fabric` run on the production draw (`draw_premise_from_joint`); today it draws through
   `draw_premise_population`, the sibling draw, so its gap does not move with W2_20.
2. Couple it to C14, the fabric inference. C14 fits a home's fabric from the register its heat
   is on, and an oil home's heat is now on no register. That pairing is only real once (1)'s
   restore condition is met.

The value-arms re-take (step d) is handed on as
`w2-20-retake-the-value-arms-in-the-world-where-heat-follows-the-gas-meter`, and it is needed
whichever way the level goes.

## Step (d): the value arms re-taken in the world 81732ffe2 made (worker, 2026-10-07)

**Premise, re-measured at draw (07:40Z).** No `run_value_cycle_ab` is running (`ps`). The published
current-world pair is `20261005c`, produced at `a9e6f2144`. That commit does not contain
`81732ffe2`, and `simulation/premise_population.py`, `household.py`, `fabric_physics.py` and
`premise_trace.py` all moved under it. So the step is not spent. The C29 retention arms that another
seat has queued are a different runner (`tools/_c29_retention_engagement_arm.py`) on a different
question, so one re-take cannot cover both.

**The run.** Worktree `/var/tmp/se-w220-arms` at origin `8af70203f`, locked, with its owner written.
It uses the same producer and the same two legs as `20261005c`:

1. `--level-arm`, writing `value_cycle_ab_s1_three_arm_20261007w.json`;
2. `--noise-floor-seeds 11111,22222,33333 --redraw-mode all`, writing
   `value_cycle_ab_s1_noise_floor_20261007w.json`.

**Not one variable.** Between `a9e6f2144` and `8af70203f`, more substrate moved than W2_20. That
includes `bfe428ef6` (the dual-fuel departure belief) and the PB4 drift gradient. So the moves below
are graded as written, but no move is credited to W2_20 alone. The landing lists
`git diff --name-only a9e6f2144 8af70203f` over `ARMS_SUBSTRATE_PATHS`.

**Pre-registered at 07:41Z, before either leg started.** The baseline is `20261005c`: value minus
level £18,541; floor spread £2,229; selection leg £3,229, withheld; control-arm gross margin
£342,591; 64 of 127 billing accounts with a gas leg.

| # | quantity | prediction | confidence |
|---|---|---|---|
| P1 | billing accounts with a gas leg (control arm) | **down**, from 64 to 52-62. Mechanism: about a tenth of drawn domestic gas boilers lose their register. SME gas is untouched. | ~0.75 |
| P2 | control-arm gross margin | **down**, by 1-8%. Mechanism: lost gas legs. An oil home's electricity is only its non-heat load. Electric-heat homes gain only about 1 point of the stock. | ~0.6 |
| P3 | value minus level (headline contrast) | **no sign predicted**. The change stays inside twice the new floor spread. | ~0.6 |
| P4 | floor spread | inside £1,500-£3,500. Book size barely changes, and the spread tracks departures, not commodity. | ~0.6 |
| P5 | selection leg | no sign predicted | n/a |

If P1 comes back unchanged at 64, the arms book does not pass through `draw_premise_from_joint`'s
heating draw. W2_20 would then not reach the arms at all, and the re-take bounds nothing about
W2_20. The landing says so before it grades anything else.

**Launched** at 07:41:32Z as `longjob-w220-arms-retake`, running `/var/tmp/se-w220-arms-handoff.sh`.
The log is `/var/tmp/longjob-w220-arms-retake.log`, with a declared peak of 11,200 MB (from the
`20261005c` run). Expected durations: leg 1 about 70 minutes, leg 2 about 3h20. Grading and
publishing are handed on as `w2-20-land-the-value-arms-retaken-in-the-heat-follows-meter-world`.

## The level is recorded, and leg 2 of the re-take died and is relaunched (worker, 2026-10-07 ~10:40Z)

**Level.** I took the seat's decision in `DIRECTION.yaml` (option 1). W2_20 now stands at **L2 with target L2**,
filed to the closed half of the map. The self-certified record cites `81732ffe2` and its two controls,
which were re-run at origin `742685492` (6 passed). The restore condition is on the simplification
record: a company grade that reads an off-gas belief on `draw_premise_from_joint`, registered in
`_AUTHORITATIVE_COUPLING`. `file_scope` gains `simulation/premise_population.py`, where `commodity` reads
the flag.

**Leg 2.** Leg 1 finished cleanly at 09:42Z (`value_cycle_ab_s1_three_arm_20261007w.json`). Leg 2 died at
09:54Z on `ValueError: No price records found in the lookback window [2020-07-03, 2020-09-30]`. The cause
is in two parts:

- `/var/tmp/se-w220-arms` has no `sim/cache/elexon_ssp_full.json`, because the cache is gitignored. Every
  run in it live-fetched SSP from Elexon.
- `sim/system_prices_history.get_system_prices_range` read a non-200 day as zero records. Leg 1's three
  fetches each returned **168,026** records. Leg 2's returned **144,361**, a different price world that
  nobody was told about. It failed only because one redrawn SVT segment then had no lookback.

So **leg 1 is unaffected.** The shared cache yields exactly 168,026 over the same window, the same count
leg 1 fetched. Leg 2 alone was relaunched at 10:33Z as `longjob-w220-arms-leg2`, on a read-only copy of
that cache, and its script refuses to start unless the cache yields 168,026. Grading is re-issued as
`w2-20-grade-the-value-arms-once-leg-two-reruns-on-the-ssp-cache`, which retires the old continuation.
The fetcher now retries a non-200 and then refuses the range, naming the day. That fix lands in a separate
commit. An empty day is a 200 with no data (probed: 2015-11-04 returned 200 with 0 records), so it is
unaffected.

## Step (d) graded: the `20261007w` pair measured a different book, so it bounds nothing about W2_20 (seat, 2026-10-07 ~16:40Z)

Leg 2 ended `END leg2 DONE` at 16:21Z, rc 0, on the cache that yields 168,026. Both artefacts are now in
`docs/observability/` (`value_cycle_ab_s1_{three_arm,noise_floor}_20261007w.json`, both producing commit
`8af70203f`).

**A correction to the pre-registration's baseline label first.** The £18,541 it calls "value minus level" is
`level_vs_selection.value_advantage_gbp`, which is the value arm minus the **control** arm. Value minus
level is the selection leg, £3,229. P3 is graded on the quantity the number names: value minus control.
"Floor spread £2,229" is the stdev of `value_advantage_gbp` across the floor's three seeds, which is what
the site publishes as `stdev_gbp`.

| # | prediction | `20261005c` | `20261007w` | verdict |
|---|---|---:|---:|---|
| P1 | control-arm gas legs down, 64 to 52-62 | 64 of 127 | **183 of 272** | **FAIL** |
| P2 | control-arm gross margin down 1-8% | £342,591 | **£669,988 (+96%)** | **FAIL** |
| P3 | value minus control moves less than 2x the new floor spread | £18,541 | **£5,089** (moved £13,452; 2x spread = £2,599) | **FAIL** |
| P4 | floor spread inside £1,500-£3,500 | £2,229 | **£1,300** | **FAIL, by £200** |
| P5 | selection leg: no sign predicted | £3,229, not distinguishable | £11,258; floor 6.6 SEMs from zero, **distinguishable** | recorded, not graded |

**Why none of this is W2_20.** The book more than doubled. Billing accounts settled in the window went
from 127 to 272. All of the growth is acquired prospects: `PROS-*` accounts went from 52 to 197. The 64
founder accounts (`SYN-*`) and the 11 SME accounts are unchanged. Gas share **rose**, from 50% to 67%, and
dual fuel went from 38% to 61%. W2_20 can only take a gas register away from a home. It cannot add 145
acquired accounts or raise the gas share. Some other change between `a9e6f2144` and `8af70203f` (40 commits
over `ARMS_SUBSTRATE_PATHS`) changed how many prospects convert. **I cannot yet say which.** Candidates,
ranked by mechanism and not yet measured: the PB4 shopping commits (`f71fcc176` woken default-tariff
households choosing by their own elasticity, `beb4f8533` drift off the default tariff, `4ff093bb0` a contact
wakes households). These raise switching in the whole market, so they raise acquisition. Second come B7's
change-of-tenancy accounts (`8359d5acd`), if a move-in's new account is minted under a `PROS-*` id. I have not checked that. The P1 escape clause ("unchanged at 64 means
W2_20 does not reach the arms") is not triggered either. The count moved, but not because of W2_20. So
whether W2_20 reaches the arms is still unmeasured.

**A second oddity, named and not explained.** In `20261005c` the three-arm headline (£18,541) sat inside its
own floor's three seeds (£17,277-£21,464). In `20261007w` it does not: £5,089 against seeds of
£9,225-£11,621, 3.9 floor stdevs below their mean of £10,132. The two legs read SSP from different sources.
Leg 1 live-fetched 168,026 records, and leg 2 read the shared cache, which also yields 168,026. An equal
count is not equal values. The other explanations the evidence allows: the leg-1 default draw is a genuine
tail draw, or the redraw scope does not cover what moved. I have not tested any of them.

**Not published.** The `20261007w` pair is not moved onto `CURRENT_WORLD_*` and the site is not
regenerated. Fifteen substrate paths moved between `8af70203f` and origin `b2ec5147a`: retention-guard
bad-debt netting, W2_36 smart-mode reads, the C32 moratorium, and the non-DD miss vocabulary among them.
They are not exemptable without measurement. A prior invocation of this claim therefore relaunched both legs
at origin `b2ec5147a` at 15:04Z as `longjob-w220-head-arms` (script `/var/tmp/se-w220-head-arms.sh`, log
`/var/tmp/longjob-w220-head-arms.log`, worktree `/var/tmp/se-w220-head-arms`), writing the `20261007h` pair.
Both legs read the shared cache, and the script refuses to start unless that cache yields 168,026. That run
is the one to publish. The `w` pair stays as the evidence for the grading above.

**Pre-registered at ~16:40Z, before `20261007h` leg 1 finished (it started 16:21Z):**

| # | quantity | prediction | confidence |
|---|---|---|---|
| H1 | `h` control-arm billing accounts | within 245-300 (272 ±10%). None of the 15 moved paths is acquisition. | ~0.7 |
| H2 | `h` leg-1 `value_advantage_gbp` | inside its own floor seeds' [min - 1 stdev, max + 1 stdev]. If it is inside, the `w` gap is consistent with the SSP-source split and not proven by it. | ~0.55 |

**Owed, one variable each, after `longjob-w220-head-arms` ends.** This machine has 12.2 GB available, the
running re-take peaks at 11.2 GB, and 287 OOM kills are on record, so nothing runs beside it.
(i) W2_20 alone: leg 1 at `b2ec5147a` with `81732ffe2` reverted, against `h` leg 1. That is the only
reading that says what W2_20 moved.
(ii) The doubled book: which commit in `a9e6f2144..8af70203f` converts 145 more prospects. A truncated
`--end-year 2017` control arm is enough, since `PROS-2016` alone went from 10 to 19 and `PROS-2017` from 4 to 18.

## H1 and H2 graded: the `20261007h` pair is published, and the leg-1 gap is not the SSP source (seat, 2026-10-08 ~02:45Z)

`longjob-w220-head-arms` ended `END both legs DONE` (leg 1 rc 0 at 18:22Z on 10-07, leg 2 rc 0 at 00:19Z
on 10-08). Both artefacts name producing commit `b2ec5147a` and world `cdba75ebb9197b33`. The log shows leg 1
read the shared cache too (`Cache hit: 168,026 SSP records`). So in `h` both legs read **one** SSP source.

| # | prediction | `20261007w` | `20261007h` | verdict |
|---|---|---:|---:|---|
| H1 | control-arm billing accounts within 245-300 | 272 | **272** (gas 183, dual fuel 167, `PROS-*` unchanged) | **PASS** |
| H2 | leg-1 `value_advantage_gbp` inside floor [min - 1 sd, max + 1 sd] | £5,089 vs £7,925-£12,921 | **£5,134 vs £7,970-£12,965** (seeds £11,666 / £9,596 / £9,269, sd £1,300) | **FAIL** |

**What H2 failing rules out.** The `w` gap was put down, tentatively, to the two legs reading SSP from
different places. In `h` both legs read the same cache, and the gap is the same size: £5,134 against a floor
mean of £10,177, 3.9 floor sds below it. **The SSP-source explanation is refuted.** By arm, leg 1's
value-arm net (£241,404) sits inside the floor seeds, and its control-arm net (£236,270) is above every
seed (£230,194-£231,716). The level leg shows the gap only because the control arm is subtracted from it
too. The worker's base-seed placebo (`90cd946ed`, `WORKER_FINDING_W2_20_THE_BASE_SEED_PLACEBO_2026-10-08.md`) reads it the same way: the seeded floor
is the default draw's own family, and the gap is the control arm's draw.

**The 15 paths between `8af70203f` and `b2ec5147a` are nearly inert on the arms.** `h` minus `w`: control
net +£58, value arm +£103, level arm +£125, `value_advantage_gbp` +£44. Each floor seed moved by the same
+£44 to +£67. This is a reading of the arms only. It does not exempt those paths for any other quantity.

**Published.** `CURRENT_WORLD_THREE_ARM_PATH`, `CURRENT_WORLD_NOISE_FLOOR_PATH` and
`CURRENT_WORLD_CHANGED_SINCE_THE_LAST_READING` in `tools/generate_value_arms_data.py` now point at the `h`
pair, and `site/data/value_arms.json` is regenerated. The current-world block reads £5,134, down from
£18,541. **It is still not HEAD's code.** Sixteen substrate paths moved between `b2ec5147a` and the
publishing HEAD, `simulation/arrears_engine.py`'s register recovery (`212c6396a`) among them, and none is
exempted. Exempting them would be a claim made without a measurement, so the generator withdraws the
currency claim and the `resolved` verdicts and keeps the measured figures. `value_arms_substrate_exemptions.json`
is left untouched on purpose. The register-recovery re-take is carried by
`w2-20-retake-the-arms-on-the-register-recovery`.

**Owed (i) and (ii) are not launched here.** Each is already a live continuation:
`w2-20-own-effect-with-81732ffe2-reverted` and `w2-20-attribute-the-doubled-book-by-truncated-bisection`.
Launching either from this claim would put a second copy over the same seeds, with too little memory for
two. They stand, in that order, one at a time.

**A red that was not this work, fixed in the same landing.** `tests/tools/test_value_cycle_ab_noise_floor.py`
was red on origin, with 35 of 96 failing, and every one passed when run alone. The cause is H50's autouse
teardown (`5941e47a9`). It empties `ACQUIRED_CUSTOMERS` after each test, and that wiped the file's
module-scoped registration of its stand-in accounts. The registration is now made per test, and all 96
pass. Seen, not mine: `tests/simulation/test_net_new_acquisition.py::test_the_ceiling_still_fits_the_peak_systemds_own_journal_reports_today`
is red because the journal's sim-runner peak (5,324.8 MB) now supports 1,437 customer-years, against the
constant's 1,750.

## (ii) The doubled book, bisected on a 2017-truncated run: pre-registration (worker, 2026-10-08 02:45Z)

**Instrument.** The count is the `PROS-*` keys of `control_arm.net_by_billing_account_gbp`. Re-read on the
two published artefacts, it gives 127/52 (`20261005c`) and 272/197 (`20261007w`), so it is the counter the
grading above used. At origin `27af1a461`, the `--end-year 2017` default draw (`/var/tmp/se-w220-placebo-out/A_default.json`)
gives PROS-2016 19 and PROS-2017 18. Those are the `w` figures, so truncation keeps the signal at the HEAD end.
Each probe is the default (control plus value) `tools.run_value_cycle_ab --end-year 2017` in a worktree whose
`sim/cache/*` is symlinked to the shared cache. A probe that live-fetches is void. `git bisect` runs over
`a9e6f2144..8af70203f`, limited to `ARMS_SUBSTRATE_PATHS` as of `8af70203f`.

**Predictions, written before the first probe:**

| # | prediction | confidence |
|---|---|---|
| B0 | endpoints at 2017: `a9e6f2144` gives 14 PROS (10+4), and `8af70203f` gives 37 (19+18) | ~0.75 |
| B1 | the first commit that moves the count is one of the PB4 trio (`f71fcc176`, `beb4f8533`, `4ff093bb0`) | ~0.40 |
| B2 | ...or one of the B7 move slices (`d22754a36`, `93e79c6e5`, `8359d5acd`) | ~0.35 |
| B3 | one commit carries at least 80% of the 23-account gap, so the move is a step and not a drift | ~0.50 |

If B0 fails at the `a9e6f2144` end, truncation does not preserve the old book. The bisect then runs on
whatever endpoint gap is measured, and says so. If any probe falls outside [endpoint low, endpoint high],
the count is not monotone, and the bisect's answer stands only as "a commit that crosses the midpoint".

## (ii) graded: the book doubled because the settlement budget went from 1,050 to 1,750 customer-years (`358d59a42`), not because of the world or the company (worker, 2026-10-08 ~04:00Z)

**Probes** (`--end-year 2017`, default draw, shared cache symlinked in, 0 live-fetch lines in every log;
artefacts are in `/var/tmp/se-w220-bisect-out/`):

| commit | PROS-* | of which 2016 / 2017 | billing accounts | control gross margin |
|---|---:|---|---:|---:|
| `a9e6f2144` (good end) | 14 | 10 / 4 | 87 | £52,917 |
| `33a051c9b` | 14 | 10 / 4 | 87 | |
| `b2a3845b6` | 14 | 10 / 4 | 87 | |
| `beb4f8533` (PB4 drift) | 14 | 10 / 4 | 87 | |
| **`358d59a42`** (first bad) | **36** | 18 / 18 | 109 | £69,818 |
| `29de32469` | 36 | 18 / 18 | 109 | |
| `8af70203f` (bad end) | 37 | 19 / 18 | 110 | £65,909 |
| **`8af70203f` with only `SETTLEMENT_CUSTOMER_YEAR_BUDGET = 1050.0`** | **15** | 11 / 4 | 88 | £52,536 |

`git bisect run` over `ARMS_SUBSTRATE_PATHS` named `358d59a42` ("The settlement budget is re-priced on
the fixed code's live peak: 1,050 to 1,750 customer-years"). The one-variable revert at the bad end then
takes the count from 37 back to 15. So the budget alone carries 22 of the 23-account gap. The remaining one
account, and a three-id difference in which prospects settle (`PROS-2016-0042`, `-0090`, `-0112`), come from
the rest of the range. The settlement chooser picks for spread over the demand axes, so changes to world
demand can change which prospects it picks. That residual is not attributed further.

**Why +67% budget gave +279% prospects.** `settle_within_budget` charges the founders' customer-years first
and gives the campaign only `budget - committed`. With roughly 75 founder and SME accounts over a nine-year
window committed first, the campaign's headroom roughly triples when the budget rises by 700. That is
consistent with 52 to 197, but it is not measured here: neither artefact records `customer_years_committed`.

**Grades.** B0 PASS (14 and 37). B1 FAIL and B2 FAIL: neither the PB4 trio nor B7 moves the count, and
`beb4f8533` is measured clean. B3 PASS: one commit carries 22 of 23 (96%). The candidate list in the grading
above ranked world mechanisms and missed an engineering dial. The dial's own commit message said what it
did: "A run's wall time rises by about 2.2 s per added customer-year". It did not say the published book
would move.

**What this means for the readings.**
- `20261005c` against `20261007w` (and `h`) is a comparison of two books sized by two machine budgets.
  Every P1-P5 move in the step (d) table carries the budget, so none of them bounds W2_20. That was already
  the conclusion. It now has a cause.
- `h` and `w` share the 1,750 budget, so the owed W2_20-alone reading (i), `b2ec5147a` with `81732ffe2`
  reverted against `h` leg 1, compares like with like on this axis.
- The value-arms book's acquired half is a sample sized by our memory budget. A figure published from it
  should name that budget. Until this landing the artefact could not.

**Landed with this:** `tools/run_value_cycle_ab.book_at_run` now snapshots the budget and sample rate the
campaign actually used (from `live_population.LAST_CAMPAIGN`), and `book_identity` publishes them per arm:
`settlement_customer_year_budget`, `settlement_sample_rate`, and a named `None` when no campaign was
resolved. They are kept out of `BOOK_DECLARED_FIELDS`, so artefacts written before this still pair. The
control is `test_the_book_names_the_settlement_budget_its_campaign_used_or_says_it_cannot`, over both
branches. A mutation that reads the module constant instead of the campaign's figure turns it red.
Verified on a real run: `origin/main` `20719d272` with this diff, `--end-year 2017`
(`/var/tmp/se-w220-bisect-out/head_with_budget.json`). Both arms read `settlement_customer_year_budget`
1750.0 and `settlement_sample_rate` 0.4188, so even this truncated book settles 42% of its own campaign wins.

## (i) W2_20 alone, `81732ffe2` reverted at a 2017-truncated control arm: pre-registration (seat, 2026-10-08, written before either probe started)

**Instrument.** `book_identity.control_arm` of `tools.run_value_cycle_ab --end-year 2017` (default draw,
control plus value). It reports `with_a_gas_leg`, `dual_fuel`, `dual_fuel_share_of_accounts` and
`billing_accounts_settled_in_window`, plus `control_arm.total_net_gbp`. Two probes, serial, each in its
own worktree with `sim/cache/*` symlinked to the shared cache. A probe that live-fetches is void.
- U: origin `ad43a298a` as it is.
- R: the same commit with `81732ffe2`'s code paths reverted (`simulation/premise_population.py`,
  `household.py`, `fabric_physics.py`, `premise_trace.py`, `background/fabric_gap_ledger.py`). The revert
  applies cleanly to code. Only this staging file conflicts, and it is not substrate. One variable.

Both share the 1,750 budget, so the bisect's dial is held. The last unreverted 2017 reading
(`20719d272`, `head_with_budget.json`) was 110 accounts, 49 gas legs, 33 dual fuel, share 0.30.

| # | quantity (R against U) | prediction | confidence |
|---|---|---|---|
| Q0 | billing accounts settled | within ±3 | ~0.6 |
| Q1 | accounts with a gas leg | **up** in R, by 3-9. Mechanism: with the revert, gas-boiler homes with no gas meter hold a gas account again. That is about 9 points of the drawn stock on a gas register (82.2% to 91.1%). | ~0.55 |
| Q2 | dual-fuel share | up, by 0.02-0.08 | ~0.5 |
| Q3 | control `total_net_gbp` | moves by less than 5% of U's net, in either direction | ~0.6 |

**Escape clause (the finding's P1).** If Q1 comes back with identical gas-leg counts, the arms book does
not pass through the drawn supply flag, and W2_20 does not reach the arms book. Then Q2 and Q3 are
read only for drift through the chooser.

## (i) graded: on its own, W2_20 takes 3 of 52 gas legs and £4,044 of gross margin off the 2017 control arm. It reaches the arms book through the prospects alone (seat, 2026-10-08 ~04:55Z)

Unit `longjob-w220-own-effect` ran R from 04:36Z and U from 04:40Z. Both exited rc 0. Their logs hold no
data live-fetch: the "live" lines are the retired committee's refusal and the coupled-triad diagnostics,
and they appear in both logs alike. Both read world `cdba75ebb9197b33` and budget 1,750. Artefacts:
`/var/tmp/se-w220-own-out/{R,U}.json`. They are not committed. **R's `producing_commit` reads
`ad43a298a` and has no field for an uncommitted revert,** so the file cannot say it is not HEAD's code.
This note is its only label.

| control arm, `--end-year 2017` | R: `81732ffe2` reverted | U: origin `ad43a298a` | U - R | prediction | verdict |
|---|---:|---:|---:|---|---|
| Q0 billing accounts settled | 109 | 110 | +1 | within ±3 | **PASS** |
| Q1 with a gas leg | 52 | 49 | **-3** | R up by 3-9 | **PASS** (at the bottom edge) |
| Q2 dual-fuel (count / share) | 36 / 0.330 | 33 / 0.300 | -3 / **-0.030** | R up by 0.02-0.08 | **PASS** |
| Q3 control `total_net_gbp` | £19,680.06 | £19,304.97 | **-£375.09 (-1.9%)** | under 5% | **PASS** |
| control gross margin | £69,953.49 | £65,909.04 | -£4,044.45 (-5.8%) | (not registered) | |
| `PROS-*` accounts | 36 | 37 | +1 | | |
| electricity legs | 93 | 94 | +1 | | |

U equals the earlier unreverted 2017 readings to the penny: net £19,304.97 and gross margin £65,909.04 at
`20719d272` (`head_with_budget.json`), and net £19,304.97 in placebo A at `27af1a461`, seven commits before
`ad43a298a`. None of those seven commits moves the 2017 control arm.

**The escape clause does not fire.** The gas legs move, so W2_20 reaches the arms book. Q1 landed at the
bottom of its band. Q1 assumed every drawn household passes the drawn supply flag. In fact only
prospects do (`simulation/live_population.py:1346` reads `prospect.premise.commodity`). Every one of the
34 accounts whose net moved is a `PROS-*` id. No founder or SME account moved. **The founder book does not
pass through W2_20 at all.** That half of P1's mechanism was wrong, and the move is smaller for it.

**Where the £375 comes from.** One account settles only in U (`PROS-2016-0112`, £344.08). 34 common prospects
move by a net +£719.18 in R. The largest moves are `PROS-2016-0075` +£234, `-0098` +£211, `-0092` +£191,
`-0090` +£172 and `-0042` -£139. Gross margin falls ten times as far as net (-£4,044 against -£375).
So most of the lost gas margin was offset in R by costs that also go with a gas leg. I have not split
which costs. Read the bridge (`gross_to_net_bridge`) in R and U before reasoning about it.

**Not a reading of the arms' contrast.** `value_advantage_gbp` is £502.43 in R and £361.62 in U. Both sit
inside the 2017 elasticity floor ([£133, £636], placebo note). So this does not show that W2_20 moves the
value-vs-control contrast. It shows that W2_20 moves the book that contrast is taken on.

**What this establishes for the W2_20 L2 record.** It cited a bill-side effect that no arms reading had
isolated. At 2017 it is now isolated. With one variable changed, 3 of 52 control-arm gas legs disappear
(6%), dual-fuel share falls 3 points, and control gross margin falls 5.8%. Over the full window the size
is not measured. That is the `b2ec5147a`-reverted leg 1 against `h` leg 1 (about 2 h). It is handed on and
not run here, because it would size an effect whose sign and route are now known. It would not decide
whether one exists.

## The register-recovery re-take: pre-registration (worker, 2026-10-08 ~05:00Z, before launch)

**Premise re-measured.** Both cited commits are on origin, which is why this re-take is owed and not spent:
the published `h` pair ran at `b2ec5147a`, before `212c6396a`. `site/data/value_arms.json` at origin still
reads `is_heads_code: false`, with 16 unexempted substrate paths. Prerequisite (ii) is met: `9bff74814` names
the budget dial (`358d59a42`). That dial is an engineering choice and not a defect, and it is unchanged at
1,750 between `b2ec5147a` and origin. So there is no fix to fold in, and `h` against this re-take holds the
book's budget fixed.

**Launch.** `longjob-w220-recov-arms` runs both legs (`--level-arm`, then `--noise-floor-seeds
11111,22222,33333 --redraw-mode all`) at origin `45122d156` in the locked worktree `/var/tmp/se-w220-recov-arms`
(script `/var/tmp/se-w220-recov-arms.sh`). It writes the `20261008r` pair. The SSP cache is byte-identical to
`h`'s, so the SSP source is held fixed. It waits behind the head-green census, because 11.2 GB will not fit
beside it. Expect roughly 2 h for leg 1 and 6 h for leg 2.

**More than one thing changed.** 16 substrate paths moved between `b2ec5147a` and `45122d156`, and the
register recovery is only one of them. A move from `h` to `r` therefore cannot be attributed to the
recovery alone. It is a reading at heads code, not a reading of `212c6396a`.

| # | quantity, `r` against `h` | prediction | confidence |
|---|---|---|---|
| R1 | control, value and level arm settled nets | each falls. Lower recovery raises realised net bad debt in every arm (by about 6% on the recovery commit's own estimate). | ~0.75 |
| R2 | `value_advantage_gbp` (h: £5,134) | moves by less than one `h` floor sd (£1,300). The recovery change hits both arms' bad debt alike. | ~0.65 |
| R3 | sign of R2's move | negative. The value arm prices part of the book above control, so it carries slightly more realised bad debt. | ~0.55 |
| R4 | control-arm billing accounts (h: 272) | unchanged within ±5%. Recovery is post-write-off and does not touch acquisition. | ~0.7 |
| R5 | H2's shape | persists: leg 1 `value_advantage_gbp` is below its own floor's [min - 1 sd]. | ~0.6 |

## (i) over the full window: W2_20 alone, `b2ec5147a` with `81732ffe2` reverted, against `h` leg 1: pre-registration (seat, 2026-10-08 06:19Z, before launch)

**Premise re-measured.** The two cited commits are on origin. That is why the reading is owed, not why it is
spent: no artefact anywhere is `b2ec5147a` with `81732ffe2` reverted over 2016-2025. The draw's "held
under this very id" note was this draw's own claim, and no other process runs this reading.

**Instrument.** `book_identity.control_arm` and `control_arm` of `tools.run_value_cycle_ab` (default draw,
control plus value, no `--level-arm`), full window. R is the locked worktree `/var/tmp/se-w220-full-R` at
`b2ec5147a`, with `81732ffe2`'s five code paths reverted (`simulation/premise_population.py`, `household.py`,
`fabric_physics.py`, `premise_trace.py`, `background/fabric_gap_ledger.py`; `git apply -R` is clean). Its
SSP cache is `h`'s own file (168,026 records). U is `h` leg 1 as published
(`value_cycle_ab_s1_three_arm_20261007h.json`, `b2ec5147a`, world `cdba75ebb9197b33`, budget 1,750). Running
U with `--level-arm` and R without it is not a second variable for the control arm. At 2017, `ad43a298a`
without the level arm and placebo A with it gave the same control net to the penny (£19,304.97).

U, control arm: 272 billing accounts (197 `PROS-*`), 183 gas legs, 167 dual fuel (share 0.614), net
£236,270.14, gross margin £669,987.94.

**Scaling from 2017.** At 2017, 3 gas legs were lost among 37 prospects (8%), and the founders did not move.
`h` has 197 prospects, so about 16 gas legs.

| # | quantity, U - R | prediction | confidence |
|---|---|---|---|
| F0 | billing accounts settled | within ±14 (5%) | ~0.6 |
| F1 | accounts with a gas leg | between -25 and -8 | ~0.5 |
| F2 | dual-fuel share | between -0.09 and -0.02 | ~0.5 |
| F3 | control gross margin | down, by 3-12% of R's | ~0.5 |
| F4 | control `total_net_gbp` | moves by under 5% of U's net (£11.8k); sign negative | ~0.6 / ~0.55 |
| F5 | accounts whose net moves by more than 1p | all `PROS-*`, no founder or SME | ~0.6 |

**Launched 06:19Z** as `longjob-w220-full-own-effect`, writing `/var/tmp/se-w220-full-out/R.json`. It runs beside `longjob-w220-recov-arms`, not alone as the item asked. The launcher admitted it: 13.4 GB resident plus a 6.5 GB declared peak, against 23.0 GB. Sharing the machine moves memory, not figures: the 2017 placebo's P1 showed the run is deterministic across processes. Waiting for the recovery re-take's 6 h leg 2 would cost a day to protect nothing.

**How to read it.** If F1 is near 0, the 2017 route does not scale, and the full-window book is not where
the bill-side effect lives. If F5 fails, something couples the founders to the prospects' draw over a
longer window (shared hedging, treasury, capital), and that coupling is a finding of its own.
`value_advantage_gbp` is reported, not graded. A single draw against a three-seed floor cannot bound it
(the placebo note).

## (i) over the full window: graded (seat, 2026-10-08, after `longjob-w220-full-own-effect` exited at 07:40Z)

R is `/var/tmp/se-w220-full-out/R.json`: producing commit `b2ec5147a` with the revert, world
`cdba75ebb9197b33`, the same as U. The grader is `/var/tmp/se-w220-full-out/grade.py`, written before
the result.

| quantity, U - R | R | U | U - R | prediction | graded |
|---|---:|---:|---:|---|---|
| F0 billing accounts | 272 | 272 | 0 | within ±14 | **pass** |
| F1 accounts with a gas leg | 195 | 183 | **-12** | -25 to -8 | **pass** |
| F2 dual-fuel share | 0.658 | 0.614 | **-0.044** | -0.09 to -0.02 | **pass** |
| F3 control gross margin | £725,508 | £669,988 | **-£55,520 (-7.7%)** | down 3-12% | **pass** |
| F4 control net | £242,356 | £236,270 | **-£6,086 (-2.6% of U)** | under 5%, negative | **pass** |
| F5 only `PROS-*` move by more than 1p | | | 56 non-`PROS` move | none | **fail**, see below |

**Size over 2016-2025.** On its own, W2_20 takes 12 gas legs off the control book. That is 6.2% of R's 195,
against 3 of 52 (5.8%) at 2017. It also takes 5.8 points off the dual-fuel share, 7.7% off control gross
margin and 2.6% off control net. The scaling guess of ~16 lost legs was high. Net moves much less than gross
because most of what leaves is pass-through. Of the £55.5k of gross margin, network (-£25.8k), policy and
levies (-£16.1k), bad debt (-£6.3k) and capital (-£1.2k) leave with it, and £6.1k reaches net. Revenue falls
£102.9k and volume falls 0.74 GWh (-7.3%). Swaps in the settled set: three `PROS-*` accounts are only in U and
three only in R. The `PROS-*` accounts carry -£5,997 of the -£6,086.

**F5 failed. The coupling is the company's own learning, not a leak.** 56 of 75 non-`PROS` accounts move,
by between 1p and £17 each, -£89 in total (1.5% of the net move). No founder or SME account changes a
renewal outcome, a departure date or a bill count. What moves is `p_retain`, in the fourth decimal
(SYN-2016-045 0.7616 → 0.7613), and `pre_4c_net`, by pennies. The route is `decide_renewal_rate`'s portfolio
learning premium (`company/pricing/renewal_rate_chain.py` writer 1). A renewing account's rate reads the
supplier's own realised margin rate across its book, and the book lost twelve gas legs. A real supplier
can see that, so it does not cross the epistemic wall. My F5 prediction missed it because the 2017
window ended before the premium had a lookback that differed between R and U. The prediction was wrong
about the mechanism, not about where the money is. **Correction to the 2017 reading's phrasing:** "through
`PROS-*` only" is true of the drawn legs. It is not true of pricing, which shares a premium across the book.

`value_advantage_gbp`, reported and not graded: value minus control is £12,217 in R and £5,134 in U. A
single draw against a three-seed floor cannot bound that difference (the placebo note), so this reading
does not say W2_20 halves the value advantage.

**What this settles for the published `h` headline.** The bill-side effect that the W2_20 L2 record cites
is now sized. Over the full window, h's control arm has 12 fewer gas legs, £55.5k less gross margin and
£6.1k less net than the same code without the supply-conditioned heating draw. The headline should carry
it as "-2.6% control net, -7.7% gross margin from W2_20 alone, one seed", not unsized.

## The size is on the `h` headline (seat, 2026-10-08)

`R.json` is committed as `docs/observability/value_cycle_ab_s1_control_w220_reverted_20261008.json`.
`tools/generate_value_arms_data._w2_20_own_effect` differences it against `CURRENT_WORLD_THREE_ARM_PATH`
and publishes `current_world.w2_20_own_effect`, which `/capabilities/` renders under the "what changed"
sentence: 12 gas accounts, -7.7% gross margin (£55,520), -2.6% net (£6,086), one draw. No figure is typed.
The size pairs by producing commit and world digest, so it is withdrawn, with its reason in amber, the day
the published pair moves off `b2ec5147a`. The "what changed" sentence also stopped saying the doubled book is
unattributed: (ii) found the cause (the 1,750 settlement budget, `358d59a42`). Controls:
`tests/tools/test_the_heating_changes_own_size_is_differenced_not_typed.py` and
`site/test_the_heating_changes_own_size_reaches_the_reader.py`. Both were mutated, by disabling the pairing
guard and the render, and both went red.

## R1-R4 graded on `r` leg 1; leg 2 has not run (seat, 2026-10-08 ~10:20Z)

Leg 1 (`value_cycle_ab_s1_three_arm_20261008r.json`, still in the locked worktree `/var/tmp/se-w220-recov-arms`)
ran 05:24Z-06:55Z. Its producing commit is `45122d156` and its world is `cdba75ebb9197b33`, the same as `h`.
Leg 2 was refused at 06:55Z for memory: it needed 11,200 MB and 10,704 MB was free. It has not run. A lane
queued `longjob-w220-recov-leg2-handoff` at 07:59 BST to relaunch it. That job is waiting on
`longjob-e2e-400-founders` (14 GB declared). This seat had queued a second relaunch under the same job name.
It stopped that duplicate within a minute, before it started. If both had stayed, they would have deadlocked
the `w220-nine-seed` chain or run the leg twice.

| # | `h` | `r` | `r - h` | prediction | graded |
|---|---:|---:|---:|---|---|
| R1 control net | £236,270.14 | £235,588.43 | -£681.71 | falls | **pass** |
| R1 value net | £241,403.98 | £240,832.43 | -£571.55 | falls | **pass** |
| R1 level net | £230,168.26 | £229,487.67 | -£680.59 | falls | **pass** |
| R2 `value_advantage_gbp` | £5,133.84 | £5,244.00 | +£110.16 | under 1 floor sd (£1,300) | **pass** |
| R3 sign of R2's move | | | **positive** | negative | **fail** |
| R4 control billing accounts | 272 | 272 | 0 | within ±5% | **pass** |

> **Rests on the pre-correction world (arrears ~10x too high); re-graded by the 400-founder end-to-end run on the corrected world.** *(Marked 2026-10-09; corrections 23fca0567, 54dbd5650.)*

**The whole move is realised bad debt.** In every arm, gross margin, capital cost and the provisioned
clock agree with `h` to within 1e-4 GBP. Each arm's net falls by exactly its rise in realised bad debt.
Control bad debt rises £11,971 → £12,653 (+5.7%), close to the recovery commit's ~6% estimate. So the
pre-registration's warning that "16 substrate paths moved, so a move cannot be pinned on the recovery"
turns out to be moot for leg 1: no other path moved any settled figure.

**R3 failed because the mechanism ran the other way.** The value arm's realised bad debt rises *less*
(+£572) than control's (+£682). The value arm's book therefore holds less written-off debt for the lower
recovery to bite on. I had argued that pricing above control would leave more debt to write off. That
argument was wrong on this book. The size, £110, is a twelfth of one floor sd, so the sign carries no
weight as evidence about selection.

R5 waits for leg 2. Publication follows R5. The `h` headline's `w2_20_own_effect` pairs to `b2ec5147a`, so
it will be withdrawn, with its reason, when the published pair moves to `r`. That withdrawal is expected,
not a regression.

## R5 graded, and the `r` pair is published (worker, 2026-10-08 ~18:50Z)

Leg 2 (`value_cycle_ab_s1_noise_floor_20261008r.json`) finished at 16:48Z, producing commit `45122d156`, world
`cdba75ebb9197b33`, the same as leg 1.

| seed | `h` `value_advantage_gbp` | `r` | `r - h` |
|---|---:|---:|---:|
| 11111 | £11,665.57 | £11,766.20 | +£100.63 |
| 22222 | £9,596.04 | £9,696.67 | +£100.63 |
| 33333 | £9,269.11 | £9,375.00 | +£105.89 |
| floor mean / sd | £10,176.91 / £1,299.54 | £10,279.29 / £1,297.71 | |
| band [min - 1 sd, max + 1 sd] | £7,969.57 - £12,965.11 | **£8,077.30 - £13,063.90** | |
| leg 1 | £5,133.84 | **£5,244.00** | +£110.16 |

> **Rests on the pre-correction world (arrears ~10x too high); re-graded by the 400-founder end-to-end run on the corrected world.** *(Marked 2026-10-09; corrections 23fca0567, 54dbd5650.)*

**R5: pass.** Leg 1 sits £2,833 below the `r` band's floor and 3.88 floor sds below its mean. That is the same
distance as `h`, to two decimal places. The register recovery moved every seed and leg 1 by +£101 to +£110, so it
shifted the whole family and left H2's gap where it was. The gap is still the control arm's draw, and this run does
not explain it.

**Published.** `CURRENT_WORLD_THREE_ARM_PATH`, `CURRENT_WORLD_NOISE_FLOOR_PATH` and
`CURRENT_WORLD_CHANGED_SINCE_THE_LAST_READING` now point at `r`, and `site/data/value_arms.json` is regenerated
from origin `6987325ae`. Front door: `value_advantage_gbp` £5,244. `is_heads_code: false`. Every verdict is
withheld for "which code drew the bound": 22 imported paths moved between `45122d156` and `6987325ae`. Those
commits include home moves (`ada37371c`), voids (`5531ef8a6`), gas cooking (`92d39bf60`, `a41cf3fc0`), electronics
(`6987325ae`), vulnerability (`d29dcddc3`) and acquisition selection (`2338f13ff`, switch off). No arms
measurement covers any of them, and most are built to move the book. **So `value_arms_substrate_exemptions.json`
is left untouched.** Exempting them would be a claim with no measurement behind it. `current_world.w2_20_own_effect`
withdrew as predicted ("measured against the run at b2ec5147a, and the published run is at 45122d156").

**What is owed for a verdict on the page:** an arms re-take at a HEAD that includes the world changes above. It
should come once the home-move and cooking/electronics lanes settle, so it is not stale on arrival.
