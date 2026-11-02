**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** none — Lane 0 `a-gas-read-is-a-volume-and-the-bill-converts-it`

# Pre-registration: the gas volume build on a replay of the cd4fc5b8d8 gas legs, and on the next fresh run (2026-10-30)

Under the correctness stretch (`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`),
for N11. The build is C1-C3 of `docs/market_research/a_gas_read_is_a_volume_and_the_bill_converts_it.md`. Written
before either replay below was read.

## What the build does

- **World (C1).** `simulation.meter_reads.SimulatedReadFeed` keeps each gas meter's cumulative volume index. Each
  period advances it once by the period's energy as volume, V = kWh x 3.6 / (CV x 1.02264), at the world's CV
  (`simulation.live_population.GAS_CV_FACTOR`, 39.5). An actual gas read carries `read_unit` and `register_volume`.
  An imperial meter reads in hundreds of cubic feet. No household is drawn imperial, because the share is not
  published (G2).
- **Supplier (C2).** `company/billing/gas_volume_conversion.py` converts. On an actual gas read,
  `monthly_bill_assembly` bills the converted advance. Where that disagrees with the settled kWh by more than
  0.005 kWh, it rescales the settled records to the converted figure. Every gas bill carries the CV, the correction
  factor and `calorific_value_basis: fixed_stand_in`, because the daily series (G1) is not transcribed.
- **Bill (C3).** The ledger prints the register in its unit (opening, closing, advance), the CV and the factor
  beside the kWh. The raw export carries them, and `INV_GAS_READ_IS_A_VOLUME_CONVERTED_AT_CV_AND_CF` is now
  checkable.

## A correction to the page's prediction, beside it

The page predicts gas energy down **about 0.13% on average, and never more than 0.26% on any bill**. That holds
only once the supplier averages a daily CV series and truncates the average (R5). In this build both sides use
the same fixed 39.5, and truncating 39.5 to 0.1 MJ/m3 leaves it at 39.5. The round trip V -> kWh is therefore an
identity up to floating point. **The 0.13% is not what this build should show; it is the prediction for the build
that lands G1.** It stays filed against that build.

## Predictions for this build

1. **Replay of the gas bill assembly.** The run's settled records and its default roster are replayed for the 474
   of 586 gas legs on the default roster. The 112 occupier legs are registered only inside a run. Each leg is
   replayed once at cd4fc5b8d8 and once with the build:
   - every bill's `total_consumption_kwh` and `total_amount_gbp` are equal to within 0.005 kWh and £0.01;
   - the rescale branch fires on **0** bills;
   - total gas kWh moves by **less than 0.001%**;
   - every actual gas bill with the build carries a volume register, and no electricity bill does.
2. **The blind row on the cd4fc5b8d8 ledger** reads **BREACHED** on every gas period with two reads, as the fifth
   cold read found on the 3dc5a92948 book (a kWh register with no volume).
3. **The blind row on a ledger built from the replayed bills** reads **0 breached**, CLEAN.
4. **The next fresh run** (DIRECTION's item 4, not launched here) carries the build. On it:
   - the row reads 0 breached;
   - gas billed energy and gas revenue match a run without the build bill for bill, within the same 0.005 kWh;
   - a move above 0.26% on any bill means something other than the conversion changed, as the page says;
   - any move at all before G1 lands is a finding about the build, not about R5.

## What would refute it

- A bill whose kWh moves. That would mean the world's volume and the supplier's conversion disagree on more than
  floating point: a CV or factor mismatch, or a period advanced twice. The world advances once per `period_end`
  however many reads are asked for it (ordinary, instructed, final).
- The row breaching on the replayed ledger. That would be a print-precision tolerance too tight, or an estimated
  register that does not mirror the kWh one.

## Grade (read after the above was written, same day)

The replay used `/var/tmp/n11-replay/replay.py`. It ran the run's `p2b__all_records` through
`simulation.run_phase4c_on_phase2b.build_monthly_bills`, with the default roster as the registry, once in the run's
own worktree (`/var/tmp/fresh-run-wt-cd4fc5b8d8`) and once with the build. Churned legs are those whose last bill
ends before the book's last month. That is an approximation of the run's set, and it is the same on both sides.

1. **Held.** There are 19,651 replayed gas bills (5,449 actual, 11,688 estimated, 2,514 prepayment), aligned bill
   for bill.
   - The largest |change| in `total_consumption_kwh` is **0.0**, and in `total_amount_gbp` it is **0.0**.
   - The rescale branch fired on 0 bills. Total gas kWh is 17,095,956.881 on both sides.
   - All 5,449 actual bills carry the meter's volume register, and all 19,651 carry the CV and the factor.
2. **Held.** On the cd4fc5b8d8 book's own ledger the row reads **BREACHED 23,745 of 23,745**: every gas record has
   a kWh register and no volume.
3. **Held.** On the ledger rebuilt with the replayed gas bills (the 112 occupier legs dropped, every other bill the
   run's), the row reads **CLEAN, 0 of 19,651**.
   - At real inputs, SYN-2016-001g in Nov 2016 reads 382.267 -> 446.778 m3, an advance of 64.511 m3. That is
     64.511 x 1.02264 x 39.5 / 3.6 = 723.85 kWh, against a printed 723.8.
   - Its actual bill of Feb 2017 after an estimated run spans 22.858 m3 = 256.48 kWh. That is the printed usage of
     643.6 kWh less the catch-up of 387.1 kWh.
4. Open: graded on the next fresh run.

The row is now checkable and the exceptions register lifts nothing for it, so **any book built before this
build will refuse to publish on it**. That is the truth about those books. No run was in flight when this landed.
