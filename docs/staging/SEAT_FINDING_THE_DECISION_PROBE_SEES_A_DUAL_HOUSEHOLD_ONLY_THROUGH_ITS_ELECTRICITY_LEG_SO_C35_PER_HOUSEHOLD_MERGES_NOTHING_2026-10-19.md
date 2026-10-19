**Severity:** RECORDED · **Lane:** C_customer_ops · **Epoch:** 4 · **Atom:** `C35_the_supplier_finds_the_share_of_value_it_prices_by_optimising_joint_value_against_the_households_response` — measurement instrument; direction item `switch-on-nba-per-household-after-the-c35-grade`

# The decision probe sees a dual household only through its electricity leg, so C35 per household merges nothing

Grade and figures: §8 of
`docs/staging/records/SEAT_PREREG_B11_C35_C34_ON_THE_FIRST_PUBLISHED_DUAL_FUEL_RUN_2026-10-18.md`.

**What was measured.** `tools.decision_probe` at `8b6fea024` (the 19 Oct publish run's sha) writes 182
renewal rows: 178 electricity and 4 gas. The 4 gas rows are opening founders'. None is a dual
household's gas leg. 129 of the 178 electricity rows belong to dual households. No
`(billing_account, term_start)` holds two rows, so `retention_rise_count --per-household` gives 182
decisions and the same 144/546 as off, to the digit.

**Why.** The probe writes a row inside its wrapper of `runner.roll_lifecycle_event`. The world draws a
dual household's renewal once, on electricity (the 18 Oct worker finding §5), so the gas leg never
reaches a roll. The run output agrees: its lifecycle stream holds 370 electricity events and 13 gas
events, and no `…g` id. The probe does key its offers by `(customer_id, term_start, commodity)`, so a
gas leg's offer, if one is priced, is held and never popped.

**What this means.**
- C35 and C34 on the dual book (144/546 rescued, 543/546 refused by C34's floor) are a
  **per-household decision costed on the electricity leg alone**. The gas leg's margin is missing,
  and so is its headroom under the gas default. They are neither the per-leg count the old rows
  were nor a household count.
- `next_best_action_decides_per_household` cannot be graded on this instrument. Off and on read the
  same because the instrument has no pair, not because the switch does nothing.
- The prediction that the gas leg's larger headroom would lower "above the headroom" refusals was
  never tested. Its leg is not in the instrument.

**What would fix it (instrument, not world).** At an electricity roll, the probe would also write the
gas leg of the same billing account. That means the gas leg's annual MWh, its offer, its base and the
gas default on that date, taken from the held offer the probe already keys by commodity. Then
`--per-household` would have a pair to merge, and C35 on/off becomes a real one-variable reading.
That is a harness change and needs no world change. It is not built here. **Next item:** whoever
builds it pre-registers the on-against-off difference first, using the prediction in
`SEAT_PREREG_SWITCHING_NBA_PER_HOUSEHOLD_ON_THE_STANDING_POLICY_CHANGES_NO_DECISION_IN_ANY_RUN_2026-10-19.md`
(N3).
