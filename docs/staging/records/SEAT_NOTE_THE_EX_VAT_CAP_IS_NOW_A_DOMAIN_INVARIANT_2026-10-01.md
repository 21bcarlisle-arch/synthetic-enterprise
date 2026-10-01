**Severity:** LATENT · **Lane:** B_commercial · Lane 0 delivery

# The ex-VAT cap is now a domain invariant, and this draw was the same claim re-drawn

Claim `the-company-ceilings-an-ex-vat-strike-at-the-ex-vat-cap`. It was drawn again while its
holder's work was already on origin:

- `18592fd03`: `cap_ceiling_ex_vat` feeds writer 4's clamp and the value arm's
  `max_offered_rate_gbp_per_mwh`. Its control is mutation-proven.
- `0485b09ca`: the measurement. 28 → 6 above the ex-VAT cap. All 6 are the world's SVT-origin
  first stint. That answers the `simulation/svt_product.py` question: it is the same defect on the
  world's side, not a deliberate basis. It was recorded, left unchanged, and handed on.

The one leg still open was "fix the class": `company/compliance/domain_invariants.py` had no rule
that a sold ex-VAT rate sits at or under the cap de-VATed. Its only cap check was the plausibility
band, which allows up to 150% of the cap, so it could not see a 5% breach. This commit adds
`SOLD_UNIT_RATE_WITHIN_CAP_EX_VAT` with `check_sold_unit_rate_within_cap`. It de-VATs with the
library's own `vat_rate_for_segment("resi")`, so no new VAT rule is written. The control refuses a
rate at the published cap, passes the de-VATed cap, and refuses one penny over it. Dropping the
division reds the control. The renewal chain's own control now also asserts the invariant over
the chain's real output, so the two implementations are held against each other.

Disposition: the claim is finished and released. The SVT world-side basis stays with the hand-off
filed in `0485b09ca`.
