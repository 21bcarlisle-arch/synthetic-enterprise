**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the renewal arm prices no gas) · **Class:** figures_on_a_superseded_clock

# FINDING — the net-negative surcharge is flat in pounds, and so varies 5.7x in what it charges

`company/crm/customer_profitability.NET_NEGATIVE_UPLIFT_GBP_PER_MWH = 5.0` is writer 3's whole
policy: if the prior term was net-negative, add £5/MWh at renewal. It was inert until 2026-09-07 —
0.0 on 78 of 78 calls — and the `term_start` stamp landed in `99b2700de` made it live. It now
fires 51 times and moves real money, so its magnitude stopped being academic on that commit and
not before.

## Measured over all 51 firings (`docs/reports/run_output_latest.json`)

```
basis / magnitude   gbp_per_mwh 5.0, 51 of 51        (flat, as designed)
commodity           46 gas, 5 electricity
rate_before         min 50.7   median 128.9   max 287.4   GBP/MWh
surcharge as a share of the rate it modifies:
                    min 1.74%  median 3.88%   max 9.86%
```

**A flat £/MWh surcharge is not a flat policy.** The same "penalty" is 1.7% of one renewal's unit
rate and 9.9% of another's — a 5.7x spread across the book that nobody chose, that no reader of
`= 5.0` could predict, and that is invisible in the run output because every log line honestly
reports the same `magnitude: 5.0`. The number is uniform; the charge is not.

Worse, it is **uncorrelated with the deficit it is levied for.** `compute_profitability_uplift`
reads only the SIGN of the prior term's margin, never its size. So the surcharge neither recovers
a large loss nor stays proportionate to a small one, and the account that lost us the most and the
account that lost us a penny are charged identically.

## What the published record does and does not settle

Established, and it is the smaller half — **the permission.**
`docs/domain_artefact_library/regulatory/pricing_differentiation_permissions.md` reads the
consolidated supply licence and finds no prohibition on pricing expected cost into a contract unit
rate (D2). Three live constraints: SLC 27.2A binds only differences BY PAYMENT METHOD, and this is
not one; SLC 7.4's undue-onerousness test binds DEEMED contracts and carries a comparator — a
class margin significantly above the book's general margin — which a surcharged class would
eventually meet; SLC 0.3 forbids a material imbalance in the supplier's favour.

**Not established — the magnitude.** That register marks D2 `UNSOURCED`: no Ofgem view on
risk-priced domestic tariffs was found. Nothing in the commons, `docs/market_research/` or the
knowledge map establishes a rate for a loss-recovery surcharge, and that is not an omission —
it is not a regulated instrument. It is a supplier's own commercial policy, so the honest origin
is a labelled belief and never a citation. **Landed as exactly that**, with this measurement
beside it, rather than left as a bare `5.0` that reads as established.

The price cap's EBIT allowance is **not** a bound on it and is not used as one:
`docs/domain_artefact_library/regulatory/price_cap_ebit_allowance.md` §E says in its own words
that it is not this company's cap and must never become a number our margin is tuned toward, and a
fixed-term contract a customer chose is not a default tariff. Quoted for scale only, with its
clock: £45.16 per customer per year, dual fuel, benchmark consumption, direct debit, cap period
11a.

## Against the mission

The pair that landed writer 3 measured **+£881.10 revenue against +£0.45 cost** — the margin gain
is essentially all revenue charged to customers. By construction this policy moves value without
creating any. That is not an argument for switching it off: a policy that returns `0.0`
indistinguishably from "this account is profitable" is worse than one that fires, and the repair
was right. It is an argument that **the £882 must never be published as value created**, and that
the shape should price the cost rather than the sign.

## Recommendation — and it is the director's, not the seat's

The register's own instruction (§F.1) is *"expected cost, not a floor"*: price what the loss
actually cost and let the answer emerge. That points at a surcharge proportionate to the measured
deficit, or expressed as a percentage of the rate it modifies, instead of a flat £/MWh. Both are
**pricing policy**, which `company/pricing/value_based_renewal.py` already establishes is the
director's call and not the seat's — its own `CANDIDATE_MARGINS_GBP_PER_MWH` note declines to
extend a grid for exactly this reason.

So: recorded, not changed. The constant carries its belief label and this measurement; the shape
question goes to him. **Nothing should publish the 51-firing count or the £882 as a result until
he has ruled**, because both are counts of a policy whose unit is arguably the wrong one.

## What would refute this

A published source establishing a loss-recovery surcharge rate for GB domestic supply. None was
found in the commons or the market-research layer; if one exists the belief label is wrong and the
constant should be cited instead.
