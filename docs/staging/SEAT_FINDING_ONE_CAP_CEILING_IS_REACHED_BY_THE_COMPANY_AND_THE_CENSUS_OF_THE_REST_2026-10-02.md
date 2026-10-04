**Severity:** LATENT · **Lane:** W3_industry_systems · **Epoch:** 2 · **Atom:** `W3_1b_intra_year_price_cap_granularity` · **Claim:** `retire-the-sixth-cap-implementation` (Lane 0 delivery)

# One cap ceiling is reached by the company. This is the census of the others.

## What was done

`company/compliance/domain_invariants.check_sold_unit_rate_within_cap` is **deleted**, not rewired.

- It had no production caller. Its only callers were two tests.
- It read `get_cap_unit_rate_for_date` with the default `net_of_epg=True`. That made `min(cap, EPG)` the ceiling, so it would have called every lawful EPG-window SVT segment unlawful. An SVT segment is paid up to the Ofgem level: the household pays the EPG and HM Treasury pays the difference.
- It had no metering-arrangement argument, so it could not express the SLC 28AD.4 multi-register test.
- Rewiring it would not have fixed any of that. A check "where a sold rate is struck" that reads `renewal_rate_chain.cap_ceiling_ex_vat` would grade the chain against itself. Writer 4 already clamps at that ceiling, so the check could not fail. Every caller that exists already reads the chain's helper.

The `SOLD_UNIT_RATE_WITHIN_CAP_EX_VAT` invariant record stays, because the obligations register traces to it. Two things changed in it:
- It now names `cap_ceiling_ex_vat` as its enforcement.
- Its description no longer says "the binding EPG level where it applied". That was the same misreading, written as law.

Its two controls now read the chain's ceiling. Dropping the VAT division in `cap_ceiling_ex_vat` reds both of them; this was run.

## The census: every function that computes or compares against a cap ceiling (2026-10-02, HEAD `6aa3653d7`)

| Function | Reached from production? | Agrees with the chain? |
|---|---|---|
| `company/pricing/renewal_rate_chain.cap_ceiling_ex_vat` | **yes**: writer 4 and the value arm, through `decide_renewal_rate` | **this is the chain** (ex-VAT, `multi_register=`, `net_of_epg=`) |
| `company/pricing/ofgem_price_cap.get_cap_unit_rate_for_date` / `get_multi_register_cap_unit_rate_for_date` | yes, but only as the published *source* the chain de-VATs | n/a: a published lookup, not a ceiling. The inc-VAT basis is stated in the docstring |
| `company/pricing/ofgem_price_cap.get_cap_unit_rate_gbp_per_mwh` (annual blend) | yes: `crm/market_conditions` (cap year-on-year movement, a ratio, so VAT cancels), `pricing/switching_recommendation` (a p/kWh advice reference), and the `domain_invariants` 150% plausibility band | **not a ceiling** in any of these uses; nobody clamps against it |
| `company/interfaces/dd_review_outcome` (`get_cap_unit_rate_for_date`) | yes | **not a ceiling**: the inc-VAT cap used as a DD *estimate rate* when no contracted rate is known |
| `company/regulatory/compliance.check_price_cap_compliance` | **no** (its own tests only) | **DISAGREES**: the caller supplies one p/kWh cap with no VAT basis, no date, no EPG leg and no multi-register leg. Filed here; deletion recommended |
| `company/regulatory/price_cap_tracker.PriceCapTracker` (`is_*_compliant`, `*_excess`) | **no** (its own tests only) | **DISAGREES**: a hand-registered quarterly table compared `<=` with no VAT basis and no multi-register leg. Filed here; deletion recommended |
| `company/crm/solr_intake.SoLRBatch.is_priced_above_cap` | no | not a ceiling: reads a supplied percentage |
| `tools/run_price_ladder.published_default_tariff` (`get_cap_unit_rate_for_date`) | tool | not a ceiling: the counterfactual SVT reference |
| `saas/reporting/annual_report._section_price_cap_headroom` | report | not a ceiling. It reads `rate_vs_svt_pct`, which has been VAT-correct since 2026-10-01. **Labelling defect:** a fixed term "above SVT" is counted as "above cap", but since `9cfb1817f` a chosen fixed renewal is outside the cap |
| `simulation/price_cap_enforcement.binding_cap_unit_rate_gbp_per_mwh_{inc,ex}_vat`, `ofgem_cap_…_inc_vat`, `hmt_epg_receipt_…` | yes (world) | **the world's own reading, independent by design (B3)**. The household-charged binding ceiling and the supplier-receipt Ofgem level are different questions; they are closed by `ofgem = binding + hmt_receipt`. The ToU SVT priced at the single-rate cap is already filed in `SEAT_FINDING_THE_IN_FORCE_28AD_…_2026-10-01.md` |
| `simulation/hedged_settlement` deemed-resi clamp (`binding_cap_…_ex_vat`) | yes (world) | **CANDIDATE DISAGREEMENT, not measured:** in Oct 2022 – Jun 2023 it clamps deemed domestic *revenue* at the EPG with no HM Treasury receipt leg. `svt_product` carries that leg. Whether any deemed domestic account settles in that window has not been counted |

**DONE as defined:** exactly one cap-ceiling implementation, `cap_ceiling_ex_vat`, is reachable from company production code. On the world side, the deemed-resi clamp above is the only open question.

## Not done

- `check_price_cap_compliance` and `PriceCapTracker` are unreached and disagree with the chain. Deleting them, with their tests, is a small follow-on. It is not done here, to keep this landing to the one function the item named.
- The deemed-resi EPG receipt in `hedged_settlement` needs a count before anyone acts on it.
