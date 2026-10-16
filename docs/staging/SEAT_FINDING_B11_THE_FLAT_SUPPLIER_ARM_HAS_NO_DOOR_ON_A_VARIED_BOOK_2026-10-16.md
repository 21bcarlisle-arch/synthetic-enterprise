**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history` · **Subjects:** `EP17_varied_population_draw` · **Claim:** `b11-the-flat-baseline-is-pre-registered-for-the-ep17-switch` (Lane 0 delivery)

# The flat-supplier arm has no door on a varied book, and the value cycle's "flat" control still targets per customer

Found 2026-10-16, while writing
`docs/staging/records/PREREG_B11_PER_CUSTOMER_AGAINST_FLAT_ON_VARIED_DRAWS_2026-10-16.md`, at
origin `a1d34f30f`. Everything below was read from the code. Nothing was run.

## What is true

1. **No policy expresses "a supplier with no per-customer view".** `CURRENT_POLICY`, the control
   in every value-cycle A/B, still holds two per-customer views:
   - It sends retention offers only where the company's per-customer churn belief exceeds
     `RETENTION_THRESHOLD = 0.30` (`simulation/run_phase2b.py:3396`), sized by belief tiers.
   - It sets framing and tone by `ab_test` per segment.

   `NAIVE_POLICY` is no substitute. It keeps the belief gate (offering a flat 5% above it) and
   also changes VaR hedging and the anniversary rule.
2. **Fields alone can express the flat posture.** `retention_discount_mode="flat"`,
   `flat_discount_pct=0.0` and `retention_tiers=()` reach `retention_cut_share_at_risk_tiers`
   with a share of 0. That returns None (`company/interfaces/growth_desk.py:452`), so no
   retention offer is made. With `framing_mode="gain_framed"` and `tone_mode="firm_toned"`, no
   per-customer view is left among the decision-policy fields.
3. **No runner takes a policy on a varied book.** `tools/seed_family.py` (the authorised
   40-founder analysis book) has no policy argument. `tools/run_value_cycle_ab.py --book-seeds`
   hard-codes `CURRENT_POLICY` against `VALUE_ARM_POLICY`.
4. **The per-home table cannot carry three of the measures.** `tools/seed_family.COLUMNS` has no
   household saving in GBP (M4), no kWh (M6) and no gas leg (the gas-heated edge group).
5. **Every authorised book seed has been read.** 61101–61112 are used (61108 possibly not), so
   fresh seeds need the director's listing in `varied_population_draw_activation.json`.

## Consequence

The standing realised A/B measures **per-customer renewal pricing against flat renewal
pricing**, inside a company that targets retention per customer in both arms. That is a narrower
claim than "per-customer beats flat", and no published figure should be read as the wider one.
Until the door below exists, EP17's switch has nothing to run its baseline through.

## The smallest change that would produce the flat arm (company code, then harness)

1. **`company/policy/decision_policy.py`:** add `FLAT_SUPPLIER_POLICY = replace(CURRENT_POLICY,
   name="flat_supplier", retention_discount_mode="flat", flat_discount_pct=0.0,
   retention_tiers=(), framing_mode="gain_framed", tone_mode="firm_toned")`. Add a control that
   pins its differing-field set against `CURRENT_POLICY` as exactly those five fields. Add a
   reachability control asserting that a run under it makes **zero** retention offers. Then
   mutate that control to prove it can fail: an arm that still offered would go green on a
   test that only checks the field values.
2. **`tools/seed_family.py`:** add `--policy {current,value_arm,flat_supplier}` (default
   `current`, so every existing family is byte-identical), entered with `policy_scope(...)` and
   passed as `policy=`. That is the pattern `run_value_cycle_ab` follows, so the run loop's
   chimera refusal applies. Stamp the policy name into each member's output, and have `readout`
   refuse to pool members whose policies differ.
3. **`tools/seed_family.COLUMNS`:** add `household_saving_gbp`
   (`build_household_value_share`, already used by `run_value_cycle_ab`), `kwh_elec`,
   `kwh_gas`, `has_gas_leg` and `company_vulnerability_flag`. These read only the run's own
   rows and the company's register.
4. **A flat-at-level arm on a seed family** needs the level from the same seed's value-arm member.
   That is a two-pass member, so it comes after 1–3, and the prereg's M1s waits on it.

Items 1 and 2 alone produce the flat arm. Item 3 is needed for M4, M6 and the edge groups.

**Not company-epistemic risk:** every new field reads only the company's own decisions and
observables. The mislabel class is read in the harness only.

## Raised to the director

The fresh seeds 61113–61118 need listing in the activation record. The recommendation goes to
`for_the_director`, and the build of items 1–3 does not wait on it.
