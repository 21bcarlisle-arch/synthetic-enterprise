# WORKER FINDING — the book is valued on a margin that excludes three quarters of the cost stack

**Severity:** BLOCKING · **Lane:** B_commercial · **Disposition:** REPAIRED 2026-08-17

**Discharged:** `tests/saas/test_clv_margin_basis.py::test_mutation_removing_a_levy_moves_the_valuation`, `tests/saas/test_clv_margin_basis.py::test_mutation_an_account_that_loses_money_is_not_published_as_an_asset`, `tests/tools/test_derived_basis_parentage_gate.py::test_mutation_the_published_defect_fails_the_gate`, `tests/tools/test_derived_basis_parentage_gate.py::test_mutation_valuing_the_book_on_the_old_line_reaches_the_gate`

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


---

# REPAIRED — 2026-08-17 worker tick

Recommendation **1** taken (value the account on the margin it actually leaves behind), with
recommendation **2**'s labelling obligation met anyway: both margin lines are now named for
their basis, so neither can be read as the other.

## The cut

`saas/cost_to_serve.py` published ONE margin line, `net_margin_gbp`, whose value was
`margin_gbp - cost_to_serve_gbp` — a contribution margin wearing the name of a net one. It now
publishes two, each named for its basis:

    margin_gbp                    revenue - wholesale (GROSS, unchanged)
    contribution_margin_gbp       margin_gbp - cost_to_serve_gbp       (the old VALUE)
    net_of_all_costs_margin_gbp   the record's own net margin - cost_to_serve_gbp

`net_margin_gbp` is **deleted, not redefined**. Rebinding the name would have handed every
existing reader a silently different number; deleting it makes an un-migrated reader raise
`KeyError` — the fail-closed half of the same choice. Two production readers existed
(`tools/run_phase4b_on_phase2b.py`, `simulation/run_phase4c_on_phase2b.py`); both printed the
contribution line under a "net margin" label and both now print the basis they mean.

`saas/clv_model.py` values the book on `CLV_MARGIN_BASIS`, indexed directly (never `.get`).
That one symbol is BOTH the key the valuation reads AND the label published all the way to the
site's basis line, via `build_enterprise_value`'s `margin_basis` ->
`enterprise_value_margin_basis` in the run output -> `extract_portfolio`'s
`basis.enterprise_value_gbp.cost_basis`. A future edit that values the book on a different
line therefore MOVES ITS OWN LABEL, and the gate below fails on the mismatch. That is what
makes the published parentage unforgeable rather than merely correct today — the old sentence
("Derived from the settled-clock net margin above") was hand-written beside a number computed
somewhere else, which is exactly why it could be false for the whole life of the defect.

## R11 — the restated figure, on a real regenerated run

`python3 -m tools.run_annual_report` re-run on the repaired tree, against the same window:

    enterprise_value_gbp     £6,304,202.92  ->  £1,296,786.28   (20.6%)
    enterprise_value_margin_basis            net_of_all_costs_margin_gbp

    acct     old avg/yr   new avg/yr        old clv        new clv
    C2           671.76       121.12       4,384.23         790.47
    C7         1,201.15       -44.59       7,771.10        -288.48   <- sign change
    C8         1,290.64       176.50       8,423.35       1,151.94
    C9         1,373.80       222.49       8,947.20       1,449.04
    C_IC1    235,930.21   107,574.82   1,458,518.07     665,026.39
    C_IC2    130,789.33    63,154.95     808,962.71     390,628.18
    C_IC3    405,403.30    31,362.03   2,574,512.66     199,164.49
    C_IC4    220,512.62     5,900.43   1,427,298.78      38,191.33

C7 — the account this finding named — is no longer published as an asset. **The P&L did not
move**: `total_gross_gbp`, `total_net_gbp`, `total_revenue_gbp`,
`cost_to_serve_portfolio_gbp` and `net_margin_after_cost_to_serve_gbp` are all identical to
the penny across the two runs. The repair moved the valuation, not the world — which is the
right shape for a defect that was always a basis error and never a belief error.

The restatement magnitude the finding INFERRED was £1,138,265.43 (18.1%) over the eight named
accounts; the measured figure over those same eight is £1,296,113.37 (20.6%), the run total
differing by the ninth account's £672.91 (SYN-2021-001, still absent from
`by_billing_account` — see the open items below). The finding's counterfactual divided by
years rather than by each account's own renewal-point count; the code's divisor is unchanged
by this repair, so the measured number is the one that reconciles.

## R10 — the class, not the row

The invariant, as the finding stated it: *a published valuation names the margin line it is
built on, and that line is one the P&L also publishes.*

`tools/generate_dashboard_data._check_derived_basis_parentage` runs over EVERY `derived_from`
in the published basis block — not over enterprise value specifically — and fails the publish
when a derived figure's cost basis disagrees with the basis of the parent it names. A future
derived figure is checked by the act of declaring a parent at all.

The gate that was already running over this same block (`_check_basis_labels_present`, R14)
passed throughout the defect's life, because a label being PRESENT and a label being TRUE are
two different checks. That is the generalisable half of this finding.

**Independence (R15 anti-tautology):** the child's basis comes from the RUN — the field the
valuation code actually indexed; the parent's is declared against the P&L line. Two sources
that can genuinely disagree, and did.

**Fail-closed:** a missing `cost_basis`, the `unknown` sentinel, an unpublished parent, a
parent with no basis, and a margin field the publisher has no vocabulary entry for all FAIL.
An unavailable check is a failed check.

## R15 — mutations RUN, each killing a named test

    CLV_MARGIN_BASIS -> "contribution_margin_gbp"   (the defect, restored)
      kills test_mutation_removing_a_levy_moves_the_valuation
            test_the_levy_move_is_not_merely_a_constant_haircut
            test_mutation_an_account_that_loses_money_is_not_published_as_an_asset

    entry[CLV_MARGIN_BASIS] -> entry.get(CLV_MARGIN_BASIS, entry["net_margin_gbp"])
      (the natural compatibility shim; would have reinstated the defect silently on
       exactly the inputs most likely to be stale)
      kills the three above PLUS
            test_a_view_carrying_only_the_old_line_raises_rather_than_valuing_on_it

    enterprise_value_margin_basis -> "contribution_margin_gbp" through the real publisher
      kills test_mutation_valuing_the_book_on_the_old_line_reaches_the_gate

Both of the finding's own specified mutations are among these, and both are red on the
pre-repair code for the reason the finding gave. The anti-fail-open direction is pinned too:
`test_the_levy_move_is_not_merely_a_constant_haircut` fixes the SIZE of the response against
the figure's own annuity factor, so a hardcoded haircut cannot pass the move test.

## R11 on the live surface — what is NOT yet true

The live `/company/` tile still renders £6,304,202.92: `docs/reports/run_output_latest.json`
is written by the publish pipeline (`sim_runner.py` -> `process_run_complete.py`), not by this
commit, and the newest published run predates the repair. **This is left deliberately rather
than hand-patched** — installing a manually-produced run output would publish several other
lanes' uncommitted working-tree changes along with it, which is the sweep hazard this project
has a standing rule against.

The interim state is correct rather than merely tolerable: `_check_derived_basis_parentage`
FAILS on the stale run (its valuation cannot state a basis -> `unknown`), so the pipeline now
refuses to republish the figure this finding proved false. Verified both directions:

    STALE (published)      cost_basis unknown            parentage gate FALSE
    REPAIRED (this run)    cost_basis net_of_all_costs   parentage gate TRUE

A consistency-gate failure NTFYs and does not block `generate_site`, so this is an alarm, not
a wedge, and it self-heals on the next scheduled run — which produces the field because the
code is committed. **If it has not cleared within two run cycles, that is a real defect and
this finding should be reopened**, not silenced.

## Open, and deliberately not swept in here

The two smaller items this finding recorded in its own read are NOT repaired, and are carried
forward rather than lost — each moves published numbers again and owes its own evidence:

1. **The divisor is renewal points, not years of margin** (`avg = lifetime margin /
   len(churn_risk[a])`). Unchanged by this repair, so the restated figures above inherit it.
2. **`enterprise_value_account_count` is 9 while `by_billing_account` names 8 CLV-carrying
   accounts** — the £672.91 residual above.

Filed as `WORKER_FINDING_THE_BOOK_VALUES_NINE_ACCOUNTS_AND_PUBLISHES_EIGHT_AND_DIVIDES_BY_
RENEWALS_2026-08-17`.
