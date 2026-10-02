**Pre-registration, filed before any code or run.** Claim `an-svt-household-can-decline-the-fix-and-stay-on-default`.
**Graded in:** `docs/staging/WORKER_FINDING_AN_SVT_HOUSEHOLD_CAN_DECLINE_THE_FIX_DESIGN_AND_BASELINE_2026-10-02.md`, and by the run that lands the code.

# A household that stays never contracts a fix above the default it would otherwise pay

**2026-10-02, autonomous worker, base origin/main `0a410a961`.**

## The premise, re-measured

The draw named `2f6a9ea05`. It is an ancestor of origin/main, but it is a measurement, not a fix.
At `0a410a961` an SVT conversion still accepts unconditionally:

- `departure_rolled_at_renewal` is False when the previous term was SVT, so `roll_lifecycle_event`
  is not called (`simulation/run_phase2b.py`, renewal block).
- `svt_conversion_event` logs `renewed` with `realized_churn_probability` 0.0.
- In both builders (`renewals.build_renewal_schedule`, `_build_gas_renewal_schedule`), conversion
  is `rolls_active_renewal`, which reads no price.

Nothing in the world reads the offered rate at a conversion. A dual-fuel gas leg has no decision
of its own at any boundary. The premise stands.

## The baseline, measured on the 2f6a9ea05 harness

Source: `/var/tmp/se-churn-belief-out/value_{base,nofixed}.json`, the value-arm runs at `ed7e89d0e`.
*base* has `fixed` in `CAPPED_TARIFF_TYPES` and *nofixed* does not. The position is
`customer_events._svt_position(contracted, term_start, commodity)`: the offer inc-VAT against the
default tariff the household's own fuel was charged that day.

| domestic fixed decision at term_index ≥ 1 | base: n / above default | nofixed: n / above default |
|---|---|---|
| SVT → fixed (conversion) | 40 / **16** (all elec) | 38 / **36** (28 elec, 8 gas) |
| fixed → fixed | 55 / 26 (22 elec, 4 gas) | 53 / 44 (38 elec, 6 gas) |

Conversions above the default, by year: base `2017 4/4, 2018 12/12`, none after; nofixed
`2017 4/4, 2018 12/12, 2019 4/4, 2020 2/4, 2021 5/5, 2023 1/1, 2024 8/8`.

**The reading looks odd and is not a world defect.** In 2017–18 every value-arm conversion sat
+12% to +59% above the SVT, while real fixes then ran £200–350 below it. I checked the components.
The company's base strike is £120–161/MWh ex-VAT against an SVT of £140–152 inc-VAT, so it sits
near or below the default. The excess is `portfolio_premium` plus `value_arm`, and before 2019
there is no cap to clamp them. This is the transfer the item asks the world to refuse.

## The rule, and where it comes from

**One dominance rule: a household that stays with the supplier never contracts a fix priced above
the default tariff it would otherwise be on. It stays on the default, or rolls to it.**

- **The destination is sourced.** If a household takes no new contract at fixed-term end, it goes
  to the supplier's default tariff (commons `powertac_2020_followup.md`, SLC 22/23 rollover; SLC
  22A forbids auto-rollover to a new fix; knowledge map *Retention offers* row). At an SVT
  anniversary, declining means staying where it already is.
- **The threshold is not an invented size.** Parity with the default is the point at which taking
  the fix costs more than doing nothing with the same supplier. Doing nothing carries no exit fee.
  No number is chosen.
- **The decline-versus-leave split is NOT established, and this change sizes nothing.**
  `svt_rates_active_passive_2016_2025.md` §2 gives active/passive (35/65) at expiry. The CIM
  internal/external figures (13.18% vs 9.32%, knowledge map) split switchers between tariff changes
  with the same supplier and changes of supplier. Neither says, of the households who reject an
  incumbent's fix, how many stay on default and how many leave. **Declared gap:
  `decline_versus_leave_share = None`, reason: no published series conditions on the incumbent's
  renewal offer being rejected.** The rule leaves the world's existing leave routes exactly as
  they are, and only reprices stayers:
  - **conversion:** no roll today, so none is added. The decliner's exits stay with C1b's SVT
    inertia hazard, the route every SVT household already has.
  - **dual-fuel gas leg:** the household's leave decision stays on the electricity leg. That leg
    sorts first, `(term_start, cid)` with `X` < `Xg`. A gas leg whose household stayed declines a
    gas fix above the gas default.
  - **fixed → fixed on the decision leg:** the price-aware departure roll fires first, against the
    offer, unchanged. A retained household whose offer is above the default rolls to it.

**Directions stated, not modelled.** (1) Unit rate only, the same basis as every differential in
`customer_events`. Standing charges are not compared. (2) Some real households took fixes above
the cap for certainty in late 2022 to 2023. The rule says never, which is harsher on the company.
Most of that window is already forced passive (`FTC_WITHDRAWAL_WINDOW`). (3) A decliner moves onto
C1b, a hazard that runs all through the year. Over the year that adds exposure an accepted fix does
not carry, so departures may rise slightly.

## The design

The rate a household faces is decided in the run loop by `decide_renewal_rate` (the value arm's
uplift lives there), not in the builders. So the decline has to be taken in the loop. The schedule
is a static sorted `all_terms`, so a declined term has to be **replaced by SVT segments from
`build_svt_schedule`** for the same window: term start to the day before the anniversary, the
product's own fuel. Three hazards, named before the build:

1. **Seed alignment.** The loop's `rolls_active_renewal(term_start, f"{acct}_{term_index}")` must
   agree with the builder's `f"{household}_{len(terms)}"` (PB6, 2026-09-29). The declined term has
   already advanced `term_indices`. Spliced segments must not advance it again, or every later
   boundary for that account re-rolls on a different seed.
2. **State the declined offer must not leave behind.** `prev_{elec,gas}_unit_rates`, the
   bill-shock count, `_competitor_position_ledger.observe` and `_last_tariff_type` must read as for
   a household on the default. The builder already clears `prev_fixed_unit_rate` on an SVT stint
   for this reason.
3. **Iteration.** The loop becomes a heap keyed `(term_start, cid, seq)`, so spliced segments
   process in date order. With no decline it must emit byte-identical output: an R13 control
   comparing default-world outputs.

**Records.** A decline is an event with its own occasion (`declined_fix`), `event_type`
`renewed` (the household stayed with the supplier), `departure_rolled` as it was, and the declined
rate and `_svt_position` on the row. Readers counting retentions keep the household.

**Control.** One partition control over a fixture where the offer is set at known positions. It
asserts that accept, decline-and-stay and leave are all reached
(`assert outcomes >= {"accepted", "declined_fix", "churned"}`) before it asserts what each does,
and it is mutation-proven: removing the decline branch must red it.

## Predictions

Run serially after `longjob-arms-floor-d-head-1002b` has exited and item one
(`restore-the-journey-decision-for-an-svt-conversion`) has landed. Base and change are one commit,
with the rule switched in-process.

- **P1 (value arm).** At least half of the value arm's SVT conversions decline, and every 2017–18
  conversion declines.
- **P2 (default world, flat policy).** Fewer than a quarter of conversions decline. The flat strike
  sits near the SVT.
- **P3 (default world).** Churned billing accounts move by 0 to +4. Exits are untouched, and
  decliners only gain C1b exposure.
- **P4 (value arm).** Total net falls against the same commit without the rule. The refused
  transfer is larger than the cap-level margin the decliners keep paying.
- **P5.** After the change, no domestic fixed contract at term_index ≥ 1 for a retained household
  has `_svt_position` > 0. This is the DONE condition, read off the run's own decision rows.
- **P6 (R13).** With the rule switched off, the default world is byte-identical to base.
