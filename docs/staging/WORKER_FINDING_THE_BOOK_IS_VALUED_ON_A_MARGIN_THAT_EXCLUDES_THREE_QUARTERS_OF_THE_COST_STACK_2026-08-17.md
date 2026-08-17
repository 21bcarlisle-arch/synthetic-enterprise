# WORKER FINDING — the book is valued on a margin that excludes three quarters of the cost stack

**Severity:** BLOCKING · **Lane:** B_commercial · **Disposition:** QUEUED (not fixed on sight)

**Found:** 2026-08-17 worker tick, LANE 3 DISCOVER/FRAME draw on `EP1_clv_three_horizon`
(level 0, `loop_stage: idle`, BUILD-gated — no BUILD code written this tick).
**Subject:** `saas/clv_model.build_clv` (the `avg_annual_net_margin_gbp` input),
`saas/cost_to_serve.build_cost_to_serve` (`net_margin_gbp`), and the published
`enterprise_value_gbp` + `enterprise_value_basis` that descend from them.
**Measured at:** HEAD 4276a179b, against the published `docs/reports/run_output_latest.json`
and the LIVE surface. Everything below is `observed-with-evidence` unless labelled
`inferred` (R9).

## The published figure, fetched from the live surface (R11)

    $ curl -s https://poesys.net/data/company.json
    generated_at            2026-08-17T10:54:43Z   git 0a3b39ee9
    enterprise_value_gbp    6304202.92
    settled_net_margin_gbp  1547113.39
    enterprise_value_basis  {"clock": "settled", "provisional": true,
                             "derived_from": "net_margin_gbp",
                             "note": "Derived from the settled-clock net margin above ..."}

`/company/` renders it as a tile: `"Enterprise value", gbp(f.enterprise_value_gbp, …)`
captioned `"settled clock · derived · scales with drawn book"`.

## What the valuation is actually built on

`build_clv` values each account as `avg_annual_net_margin_gbp × annuity_factor(expected
lifetime, 10%)`. That margin input is

    Σ over the account's fuel legs of cost_to_serve["by_customer"][cid]["net_margin_gbp"]
    ────────────────────────────────────────────────────────────────────────────────────
                        len(churn_risk[account])        # renewal points

and `saas/cost_to_serve.py:148,181` defines `net_margin_gbp = margin_gbp − cost_to_serve`,
where `margin_gbp` is — the module's own docstring says so — "revenue minus wholesale cost
only" (`simulation/portfolio_pnl.py`).

**Verified to the penny, not inferred.** For all eight accounts the published book names,
`by_billing_account[a]["avg_annual_net_margin_gbp"]` equals
`(Σ legs lifetime gross_gbp − Σ legs cost_to_serve_gbp) / renewal points` exactly:

    acct     published avg/yr   (gross − cts)/renewals   net/yr (run's own P&L)   net−cts/yr
    C2               671.76             671.76                    210.10             109.00
    C7              1201.15            1201.15                     11.78             -40.13
    C8              1290.64            1290.64                    209.40             158.85
    C9              1373.80            1373.80                    249.42             200.24
    C_IC1         235930.21          235930.21                  96090.74           95622.06
    C_IC2         130789.33          130789.33                  55725.35           55260.58
    C_IC3         405403.30          405403.30                  27801.38           26881.74
    C_IC4         220512.62          220512.62                   5370.11            4917.02

## The excluded stack, reconciled exactly

Portfolio-wide, from the same run output:

    gross margin (revenue − wholesale)   6,437,882.60
    net margin (the settled clock)       1,547,113.39
    difference                           4,890,769.21   = 75.969% of gross

and that difference reconciles to the penny against the run's own per-year cost lines:

    policy_cost_gbp        3,404,188.65   (RO 1,722,321.54 · CfD 262,856.80 · CM 336,419.95
                                           · FiT 466,836.80 · CCL 458,497.10 · mutualisation
                                           157,256.46)
    network_cost_gbp         869,332.79
    gas_policy_cost_gbp      171,108.84
    gas_network_cost_gbp     393,759.19
    capital_gbp               51,554.84
    bad_debt_gbp                 824.90
    ────────────────────────────────────
    total                  4,890,769.21   (residual 0.00)

None of those lines reaches the valuation. Cost-to-serve (£23,349.26 portfolio-wide, 0.36%
of gross) is the *only* cost below wholesale that does. A UK supplier's network charges and
policy levies are not overheads to be allocated later — they are per-unit costs incurred by
the specific customer's specific consumption, which is exactly the population `build_clv`
values.

## Two consequences, one of them the constraint this atom was minted under

**1. An account whose own P&L is negative is published as an asset.** C7 is valued at
`clv_gbp 7771.10` on a believed £1,201.15/yr and `expected_lifetime_periods 10.928`, and it
is one of the nine accounts inside the live £6,304,202.92. The same run's per-customer P&L
gives C7 a lifetime net margin of £117.83 across ten years — £11.78/yr — and −£401.30 once
its own cost-to-serve is charged, i.e. −£40.13/yr. `still_supplied: true`, so it stays in the
book. CLAUDE.md's activity-based-pricing rule ("flat margin makes some customers net-negative;
any pricing model must account for cost-to-serve at the customer level") and this atom's own
`origin_note` ("a CLV that ignores cost-to-serve at the customer level reproduces the exact
error the constraint names") are met on their letter — cost-to-serve *is* subtracted — and
missed on their substance: the costs that actually make C7 negative are the levies and network
charges, and they are not.

**2. The published basis line states a parentage that is false.** `enterprise_value_basis`
says "Derived from the settled-clock net margin above", and the tile two above it is
`settled_net_margin_gbp 1,547,113.39`. The figure is not derived from that number. Its parent
is the per-account `margin_gbp − cost_to_serve` line, whose portfolio total is
£6,414,533.34 — 4.15× the stated parent. The mislabel is what makes the number *look* sane:
£6.3m reads as ~4× a £1.55m annual net margin, a plausible multiple for a customer book,
where it is in fact ~1.0× a margin line that excludes 76% of the cost stack. This is R14's
subject one level down — the figure carries its clock and misstates its basis.

**Restatement magnitude (`inferred` — a counterfactual, not a valuation).** Holding every
`expected_lifetime_periods` and the 10% annuity exactly as published and swapping only the
margin input for the run's own net-of-cost-to-serve margin per year, the eight named accounts
total **£1,138,265.43** against the **£6,298,818.09** they contribute today — **18.1%**. Two
sign-changers inside that: C7 goes to −£259.63 and C_IC4 from £1,427,298.78 to £31,826.11.
The direction is not in doubt even where the magnitude is: every excluded line is a cost.

## Two smaller things found in the same read, recorded here rather than filed separately

* **The divisor is renewal points, not years of margin.** `avg = lifetime margin / len(churn_risk[a])`.
  C2 has ten years of margin and nine renewal points (+11%); C_IC4 has six and five (+20%).
  A cumulative total divided by a count of a different thing is a unit error, small beside the
  basis error and real.
* **The published per-account table omits a valued account.** `enterprise_value_account_count`
  is 9; `by_billing_account` names 8 accounts carrying a `clv_gbp`. The residual is
  £5,384.83 (`inferred`: SYN-2021-001, the drawn successor, which appears in `clv_snapshots`
  2022-2024 and not in `by_billing_account`).

## Why it is filed rather than fixed

`SELF_INTERRUPT_DISCIPLINE` — queue by default. And the fix is estimator surgery on the
valuation formula inside `EP1_clv_three_horizon`'s own subject matter: LANE 3 DISCOVER/FRAME
may not write BUILD code for a BUILD-gated atom (EPOCH_GATING_AND_ATOM_AUTHORSHIP rule 1).
Being BLOCKING on `B_commercial`, this refuses new level-raises in that lane until repaired
or until the limitation is explicitly recorded and accepted — which is the correct state: the
lane's headline published figure is the thing in question.

## What would close it — recommendation, not an ask

1. **Recommended: value the account on the margin the account actually leaves behind.** Give
   `build_clv` a per-account margin net of everything attributable to that account's
   consumption — policy, network, capital, bad debt, cost-to-serve — and publish the
   composition beside the figure. The per-year, per-customer lines already exist in the run
   output; this is an input change, not a new model.
2. **If the contribution-margin basis is kept deliberately**, then it must say so: rename the
   field away from `net_margin`, correct `enterprise_value_basis`'s parentage, and publish the
   net-basis figure beside it so a reader can see both. Keeping the label as it stands is not
   one of the options.
3. **R10 — close the class, not the instance.** The invariant: *a published valuation names
   the margin line it is built on, and that line is one the P&L also publishes.* The
   detectable shape is a derived figure whose `basis.derived_from` names a field whose
   portfolio total does not reconcile with the figure's own parent — checkable arithmetically,
   over every basis-labelled figure, not just this one.
4. **R15 — the control must be able to fail.** Two mutations, both cheap: (a) delete one levy
   line from a customer's cost stack and the valuation must MOVE — today it cannot, because no
   levy is in it; (b) hand `build_clv` an account whose net-of-all-cost margin is negative and
   the published `clv_gbp` must be negative or absent, never positive. Today's code passes
   neither, and both are red on it before any repair.
