**Severity:** LATENT · **Lane:** W3_industry_systems · **Epoch:** 4 · **Atom:** `unminted`

# The deemed and flex settlement writers book no standing charge, so the household is billed one the P&L never sees, and the fixed network share now has nothing recovering it (2026-11-09)

**Found by.** The worker tick building `W3_3_the_network_charge_splits_per_unit_and_per_day`,
9 Nov 2026. Measured by reading the code at the W3_3 landing. No run was made.

## What it is

- `simulation/hedged_settlement.run_hedged_term` adds `standing_charge_gbp` (the cap's nil column
  / 48) to each row's `revenue_gbp` and `margin_gbp`.
- `run_deemed_term` and `run_flex_term` do not. Their rows carry no `standing_charge_gbp` field, and
  their revenue is the unit rate x volume only.
- `saas/bill_generator.py` (around line 360) handles a row set that carries no standing-charge
  field by adding `days_in_period x standing_charge_rate(...)` to the bill. **So the household on a
  deemed or flex term is billed a standing charge, while the settlement P&L (`net_margin_gbp`, the
  portfolio book's `standing_charge_revenue`) never books it.** Revenue and the bill disagree by
  about £0.47–0.60 a day per domestic electricity account at 2023–2026 cap levels.
- Since W3_3 the three writers all charge the cap's fixed network share per supply point per day
  (about £0.25–0.35 a day from April 2022). On the deemed and flex rows nothing books the standing
  charge that recovers it. Those terms now read more loss-making than they are. The direction is
  conservative, but it is wrong.

## Second instance, same class

`sim/customer_state_layer.as_void_row` zeroes `network_cost_gbp` with the volume fields. A vacated
domestic meter still bears the fixed network charge per MPAN per day, so void rows now under-state
network cost by the fixed share. That one runs in the flattering direction.

## Recommendation

- Book the standing charge on deemed and flex rows exactly as `run_hedged_term` does: a
  `standing_charge_gbp` field, added to revenue and margin. The bill then reads it off the rows
  rather than adding its own.
- In `as_void_row`, keep `get_electricity_network_fixed_per_day / 48` as the void row's network
  cost.

Both are world settlement fixes, decided for fidelity. Each moves deemed and void P&L. Pre-register
before the run, then file a control in the W3_3 shape: a nil-consumption deemed day's revenue
equals the standing charge.
