<!-- SUPERVISOR_DRAW: blocked -->
<!-- BLOCK_RELEASE: director_level_up -- intra-year price-cap granularity BUILD blocked on director_level_up (R16), pending sub-annual cap-window discovery -->
# [PLANNER-MINTED] — sub-annual (quarterly) Ofgem price-cap table granularity (2026-07-28)

> **CLOSED 2026-07-28 (DISCOVER done): analysis published at `docs/design/INTRA_YEAR_PRICE_CAP_GRANULARITY_DISCOVER.md`.**
> Gap confirmed in code: `simulation/hedged_settlement.py::run_deemed_term` clamps deemed/SVT against
> `get_cap_unit_rate_gbp_per_mwh(commodity, current_date.year)` — year granularity. A Jan–Mar 2022 deemed customer
> clamps against the full-year-2022 blend (elec 305 / gas 95 £/MWh) instead of the pre-Apr-2022 cap that actually
> applied (elec ≈208, gas ≈41.7 £/MWh; Oct-2021 cap ran to 31 Mar 2022). **Sized bound: ~£343 over-stated dual-fuel
> revenue per deemed customer for the crisis quarter** (elec ~£87 + gas ~£256); direction softens the very squeeze the
> atom models. All Ofgem figures cited (HoC Library CBP-9714), none fabricated. **Two discoveries:** (1) a quarterly cap
> table already exists (`company/regulatory/price_cap.py::_PRICE_CAP_QUARTERLY`) — most data-sourcing done; (2) BUT it
> mis-places the Apr-2022 step at calendar-Q1 (labels `2022-Q1` at the post-step £1,971), so a naive calendar-quarter
> re-thread still mis-clamps — BUILD must key on real cap-change windows (6-monthly Oct/Apr → quarterly from Oct-2022),
> honour the EPG override (Oct-2022→Jun-2023, ceiling = min(cap, EPG)), and correct that row. **Recommendation: BUILD
> the sub-annual cap-window table** (fallback: register the ~£343 bound as a declared+measured simplification in W3_1).
> R15 shape + R13/R12 walls specified. **BUILD blocked_on director_level_up (R16 — no self-bump).** No production code touched.

**finding_key:** `expert_hour:W3_1_price_cap_binding` (adjudicated-real, ledger 2026-07-11).

**Source:** `docs/design/SANITY_FINDING_COVERAGE_MAP.md` row 10 — the P2 audit found the Expert-Hour REAL
GAP is **neither covered nor a declared simplification**. The existing atom `W3_1_price_cap_binding` (L2,
HARDEN-saturated) closes cap-*binding* (the cap is now applied at all); its own `simplifications:` list
records only the build + two Rule-0 HARDEN re-verifies — **not** this intra-year granularity gap. So this
is uncovered residue, not a W3_1 re-mint.

**Provenance:** RUNG-7 planner mint (a fidelity fix on an acknowledged-but-unregistered gap = `mint`-direction,
GAP2 §2, autonomous). Net-new capability (sub-annual cap table) distinct from W3_1 (cap binds at all).

**The gap (from the Expert-Hour verdict, "PASS with one real gap").** The cap table is **annual granularity**
(one £/MWh per calendar year), but the real Ofgem Default Tariff Cap updates 2–4× per year and moved sharply
mid-year in the exact crisis period this atom exists to model — the real cap rose ~54% in a single step at
Apr-2022 (~£1,277→£1,971 typical bill). A Jan–Mar 2022 deemed customer is therefore clamped in-sim against
the **full-year-blended** 2022 rate (305 £/MWh elec) rather than the lower rate that actually applied those
months — an **intra-year off-by-period gap**, explicitly *different* from the year-on-year ballpark the
module's own docstring already declares as an accepted simplification.

**Serves:** DIRECTOR_AXES v1 **#3 Believability** + the crisis-fidelity mission (this atom exists to model
the 2021–22 cap dynamics — an annual blend erases the very mid-year step that defined the crisis for
deemed/SVT customers).

**Fidelity gained (one sentence):** deemed/SVT customers in a cap-step quarter are clamped against the real
period cap that applied, so intra-year cap dynamics (the Apr-2022 step) are modelled rather than blended away.

## Exit criteria (falsifiable, R11 + R15) — OR a declared simplification (no silent closure)
- **DISCOVER (self-drawable now):** source the real sub-annual Ofgem cap schedule (6-monthly pre-2022 →
  quarterly from Oct-2022) from published Ofgem data (cite; never fabricate a date); measure the £ impact
  of the annual-blend vs period-cap on the crisis-window deemed customers to size the gap.
- **BUILD (gated):** `company/pricing/ofgem_price_cap.py` cap lookup keyed by the settlement period's
  effective cap window (not `current_date.year` alone); R15 — a Jan–Mar 2022 deemed period clamps against
  the pre-Apr-2022 cap, a May-2022 period against the post-step cap (mutate to the annual blend → the test
  FIRES). Portability: keyed by cap-window schedule, not hardcoded to 2022.
- **Legitimate alternative outcome:** if the builder judges period-granularity **not-worth-the-complexity**,
  register it as a **declared + measured-bound** simplification in W3_1's `simplifications:` (the sized £
  impact from DISCOVER is the bound) — a credited, argued outcome, NOT a silent closure (§3).

## Lane / rank / walls
- **Lane:** `company/pricing` + `simulation/hedged_settlement` (W3 industry-systems, SUPPLIER front).
  **DISCOVER self-drawable now; BUILD blocked_on the relevant front/level (director_level_up, R16).**
- **Rank:** among product-lane atoms per ratified GAP2; PRODUCT-FIRST guard applies.
- **Walls:** R13 — the cap *values* are external-reality (Ofgem-published), a fidelity-to-reality change
  decided blind to company P&L, NOT a curriculum/difficulty move; R12 — cap accuracy is a fidelity target
  vs the external source, never tuned to make company margin look right.
