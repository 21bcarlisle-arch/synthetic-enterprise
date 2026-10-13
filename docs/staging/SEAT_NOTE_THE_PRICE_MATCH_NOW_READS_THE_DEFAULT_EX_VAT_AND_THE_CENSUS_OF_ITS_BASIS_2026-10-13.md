**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** acquisition-and-retention-economics -- no new number; the default is the chain's own `cap_ceiling_ex_vat`

# The price match now reads the published default ex VAT; the census of who reads which basis

**Item:** `the-price-match-compares-an-inc-vat-default-with-an-ex-vat-renewal` (found by the floor
recount, 95b3a38d2). **Premise re-measured at origin c3bf385b9: live.** `_price_match_inputs` handed
`_account_state_svt_rate` (inc VAT; and the GROSS cap through the EPG, 2022-10..2023-06) to a match
compared against an ex-VAT re-fix and floor.

## Census: every consumer of a "published default", and its basis

| Consumer | Fed by | Basis assumed | Basis received |
|---|---|---|---|
| `crm/save_offer.price_match_save_rate` (save) | `run_phase2b._price_match_inputs` | ex VAT (re-fix, floor) | **inc VAT -- fixed** |
| `growth_desk.retention_cut_share_at_price_match` (cut) | same | ex VAT | **inc VAT -- fixed** |
| `value_based_renewal` → `enriched_churn_estimate` → `discovered_price_sensitivity.own_move` | `renewal_rate_chain` L529, `cap_ceiling_ex_vat` | ex VAT, EPG-net | ex VAT, EPG-net -- right |
| `renewal_rate_chain._stayer_default_ex_vat` | `own_default_tariff_inc_vat_per_mwh` ← `_account_state_svt_rate` | inc VAT, converted in the chain | inc VAT -- right (named and converted) |
| `account_state_log.rate_vs_svt_pct` (run_phase2b L3150, L3701, L3779) | `_account_state_svt_rate` | — | **ex-VAT unit rate over inc-VAT SVT: NOT fixed here** (see below) |
| `tools/save_on_loss_notice_arms.py` | the save log's `published_default_rate` | ex VAT | ex VAT from the next run on |

## The one seam

`company.crm.save_offer.published_default_rate_ex_vat`, exported through the save door
(`company/interfaces/save_offer.py`), and it IS the churn belief's own reading
(`cap_ceiling_ex_vat`, single-rate). So the save, the cut and the churn belief read one figure.

## Printed at real inputs (re-fix at the ex-VAT default, floor 85%)

| Day | Gap | Cut before | Cut after |
|---|---|---|---|
| 2021-01 elec | 17.6% | 13.5% | 17.6% |
| 2024-01 elec | 9.1% | 4.6% | 9.1% |
| 2024-07 elec/gas | 3.7% | **None (no offer)** | 3.7% |
| 2025-04 elec | 14.0% | 9.7% | 14.0% |
| 2019-07 | 32.5% | floor binds | floor binds |

A re-fix at the default is now cut by exactly the published gap, which the control asserts as a property
(`tests/simulation/test_the_price_match_reads_the_default_ex_vat.py`; reverting the seam reds 13/14;
the `heat` leg is an equivalence: None either way).

## Not done, and why

`rate_vs_svt_pct` in `account_state_log` divides an ex-VAT unit rate by the inc-VAT SVT, so a rate
AT the cap reads -4.8%. That is a world-side record with its own readers (`tools/r1_inference_ceiling.py`,
`run_price_ladder`, three saas reports, `tests/simulation/test_price_cap_vat_basis.py`). Changing it
moves a published diagnostic and the R1 ceiling, so it is a separate item and not part of this fix.
**Business accounts** also still get the domestic default in the match (they did before as well).
The chain gives them none, so their price match is reading a cap that does not apply to them. That is
a segment question, not a VAT one, and is left as it was.
