# Owned-Quantity Registry — DISCOVER half (2026-07-28)

**Status:** DISCOVER only. No code changed, no registry built, no gate wired. The BUILD half
(the registry module + the gate) is `blocked_on: director_build_open` per
`docs/staging/in_progress/PLANNER_MINTED_owned_quantity_registry_gate_2026-07-28.md`. This
document is the archaeology that half needs: for each of the six mandatory quantities (net
margin, treasury, EV, bad debt, cost-to-serve, carbon), the true owning module, every other
module that also computes it (file:line + how it diverges), and where ownership is
undeclared/ambiguous today.

**Method:** grep-driven code archaeology across `company/`, `saas/`, `sim/`, `simulation/`,
`site/` (tests excluded), reading each hit in context, checked against what actually feeds a
published surface (`site/data/*.json`, `docs/reports/ANNUAL_REPORT.md`) versus what is wired
but dormant. Every claim below is `observed-with-evidence` (file:line cited); none is inferred.

---

## 1. Net margin

**True owner:** `saas/ledger.py::derive_pnl()` (lines 463–540) — the SIM/company wall's
canonical accrual P&L, built purely from ledger events (`billing_event`, `settlement_event`,
`capital_charge_event`, `vat_remittance_event`, `non_commodity_cost_event`, …). It is the only
one of the candidates that is (a) pure, (b) event-sourced, and (c) explicitly the interface the
other modules' docstrings reference as the reconciliation target.

**Second sources found: 4.**

1. **`simulation/run_phase2b.py:1918-1926`** — per-settlement-period net margin is first produced
   by `sim/risk_engine.py::compute_net_margin()` upstream (gross − capital), then **mutated a
   second time in-place**: `rec["net_margin_gbp"] = round(rec["net_margin_gbp"] - _bad_debt, 6)`
   using a flat historical bad-debt rate (`saas/cost_to_serve.py::get_bad_debt_rate`), and
   accumulated into `treasury`. This is the figure that becomes `total_net_gbp` /
   `total_gross_gbp` on the dashboard — i.e. it is the one actually reaching the headline
   published number, not `derive_pnl()`.
2. **`company/finance/pnl.py::company_income_statement()`** (lines 16–60) — an independent
   cash-basis recomputation from the same ledger events. Its own docstring states: *"The result
   should agree with saas.ledger.derive_pnl() for the energy-margin components... but may differ
   on the revenue line because the company sees cash collected while the simulation sees
   billed."* A deliberate, documented divergence — but still a second live computation of a
   field named `net_margin_gbp`.
3. **`company/finance/double_entry.py::income_statement()`** (lines 211–259) — a THIRD,
   independently-derived net margin, computed from double-entry account balances
   (`net_profit = gross - capital - opex`, line 234) rather than event-type pattern matching.
   Feeds `management_accounts[year].income_statement.net_margin_gbp`, which is what
   `tools/generate_dashboard_data.py::extract_management_accounts()` (lines 748–781) publishes.
4. **`simulation/run_phase2a.py:219`, `run_phase2a_repriced.py:181`, `run_segments.py:403`** —
   three more near-identical `treasury += rec["net_margin_gbp"]` accumulators, structurally
   close enough to be part of §3's clone ratchet but semantically the same "running net margin"
   computation as #1, once more.

**Owner is not just ambiguous — it is live-confirmed disagreeing today.**
`tools/generate_dashboard_data.py:224-251` already documents this as a KNOWN, ~4x divergence and
partially mitigates it with a `basis` label rather than a fix:
> *"net_margin_gbp is settlement-derived (total_net_gbp) and diverges materially (~4x) from the
> bill-derived ledger view — see tools/generate_margin_bridge.py / site/data/margin_bridge.json
> for the quantified reconciliation."*
This is almost certainly the ruling's cited *"three disagreeing net-margin figures ~4.2x apart
on one published surface"* — the surface is `site/data/dashboard.json`, and the three figures
are (1) `total_net_gbp` (source #1 above), (2) `_ledger_headline.net_margin_gbp`
(`derive_pnl()`), (3) `management_accounts[yr].net_margin_gbp` (`double_entry.income_statement()`).
The divergence is currently handled by *labelling* (a basis note + a reconciliation bridge
file), not by declaring one owner — which is exactly the gap this registry needs to close. The
label is evidence the team already knows about the defect; it is not a fix.

---

## 2. Treasury

**True owner (candidate, contested):** `simulation/run_phase2b.py` — the running
`treasury_cash_balance_gbp` produced by `treasury += rec["net_margin_gbp"]` (line 1923), which
feeds `sim/risk_engine.py::is_administration_triggered(treasury_balance_gbp)` (line 180) — i.e.
the figure that actually gates a real simulation consequence (administration/insolvency).

**Second sources found: 3, plus 4 duplicate call sites of the "owner" computation itself.**

1. **Duplicate call sites of the same accumulation** (not a different quantity, but a
   structurally-repeated owner-computation — flagged because the registry gate must decide
   whether "owner" means one module or one call site): `simulation/run_phase2a.py:219`,
   `simulation/run_phase2a_repriced.py:181`, `simulation/run_segments.py:403`,
   `simulation/run_phase2b.py:1923` — four independent `treasury += rec["net_margin_gbp"]` loops.
2. **`saas/ledger.py::derive_cash_position()`** (lines 547-549) — `starting_treasury +
   sum(event["amount_gbp"] for event in events)`. A genuinely different computation: it sums
   *all* ledger event amounts (including bad debt write-offs, acquisition spend, fixed costs —
   whatever events exist), not just per-period net margin. Will not equal #1 unless the event
   stream and the settlement-record stream are provably reconciled — no such reconciliation was
   found.
3. **`company/finance/double_entry.py`, account `"1001"` (cash)**, read via
   `company/finance/treasury.py::cash_flow_by_year()` (lines 23-30) — a THIRD cash balance, this
   one emergent from the double-entry journal's cash account, feeding `project_treasury()` and
   `treasury_health()`.

**Ambiguity note:** "treasury" is used for at least two semantically different things under one
name — the **trading/collateral treasury** that gates administration (owner candidate above,
architecturally separated from ops per `run_phase2b.py`'s own comment: *"Fixed costs flow
through the ledger only — not deducted from the energy trading treasury (trading vs. ops
architectural separation)"*) versus the **company cash/bank balance** (`derive_cash_position`,
`double_entry` account 1001). The registry cannot cover "treasury" as one quantity until this
split is named explicitly — likely two registry entries (`trading_treasury_balance_gbp`,
`company_cash_position_gbp`) rather than one, or the BUILD half will itself become a fail-open
(a real second source waved through because it "isn't really the same treasury").

---

## 3. Enterprise value (EV)

**True owner:** `saas/enterprise_value.py::build_enterprise_value()` (lines 84+) — portfolio-wide
sum of home-move-adjusted CLV, itself built from `saas/clv_model.py` + `saas/cost_to_serve.py` +
`saas/home_move_win_rate.py`.

**Second sources found: 0.** This is the one clean quantity of the six. Every other hit
(`tools/generate_company_data.py:116-117`, `tools/generate_dashboard_data.py:214-251`,
`tools/generate_insights.py:124-148`, `tools/generate_shadow_html.py:224`,
`tools/generate_supplier_json.py:43`, `tools/run_frozen_baseline.py:50-51,77`,
`saas/reporting/annual_report.py:656-657,912-918`, `company/finance/board_dashboard.py:59,77-78`)
is a **reader**, not a recomputer — each pulls `enterprise_value_gbp` (or
`enterprise_value.by_customer` / `.portfolio`) from the one `build_enterprise_value()` output, no
alternate formula found anywhere. No ambiguity, no divergence. Note for the registry design:
this is the reference case for what "owner-only, no gate trip" should look like — useful as the
R15-negative control (the gate must NOT flag any of the above as a violation; a gate that
red-flags a passthrough read would itself be a false positive worth mutation-testing against).

---

## 4. Bad debt

**True owner:** `simulation/arrears_engine.py::compute_emergent_bad_debt()` /
`apply_emergent_bad_debt()` (lines 306, 347) — explicitly built and wired
(`simulation/run_phase4c_on_phase2b.py:582-592`) to **replace** an earlier flat-rate figure, per
its own comment: *"Phase QD: replace the flat get_bad_debt_rate() formula baked into all_records
by run_phase2b's real-time settlement loop with the real, emergent bad debt from the same
payment/arrears model... so the board-reported bad_debt_gbp is an outcome of simulated payment
behaviour, not a calibrated assumption."*

**Second sources found: 2, one of them live and load-bearing until overwritten.**

1. **`saas/cost_to_serve.py::get_bad_debt_rate(year, segment)`** (line 92) — a static
   year×segment historical-benchmark table, still executed inline at
   `simulation/run_phase2b.py:1919`: `_bd_rate = get_bad_debt_rate(...) * _stress_bd_mult` →
   `rec["bad_debt_gbp"] = _bad_debt`. This is a genuine, currently-live second computation of the
   *same field name* on the *same record* — it is only overwritten later, in a separate phase
   run (`run_phase4c_on_phase2b.py`), and only if that phase actually executes on the record set.
   **Fail-open risk:** any consumer reading `all_records` between `run_phase2b.py` and
   `run_phase4c_on_phase2b.py`, or any path where phase4c is skipped, silently gets the flat
   placeholder standing in as "real" bad debt with no marker that it is unreconciled.
2. **`saas/payment_behaviour.py::bad_debt_provision_gbp(credit_risk, revenue_gbp)`** (line 58) —
   a third, independent provisioning formula (`revenue_gbp * rate_by_credit_risk_segment`,
   `DEFAULT_PROBABILITY_BY_CREDIT_RISK` table) used for per-bill provisioning display. Plausibly
   a *different* quantity (forward-looking provision vs. settled write-off) rather than a
   duplicate — but it shares the name-shape closely enough (`bad_debt_*_gbp`) that a registry
   entry must either declare it a distinct quantity (`bad_debt_provision_gbp`, separately owned)
   or fold it in; leaving it unaddressed is exactly the ambiguity the gate needs to close.

---

## 5. Cost to serve

**True owner:** `saas/cost_to_serve.py::build_cost_to_serve()` / `cost_to_serve_for_period()`
(lines 101, 121) — fixed-overhead-per-segment-per-period table, single source.

**Second sources found: 0.** Checked every other hit
(`saas/ledger.py::make_cost_to_serve_event` — wraps a passed-in value into an event, does not
compute one; `company/finance/annualised_revenue_report.py::cost_to_serve_ratio` — a ratio
computed *on top of* an already-supplied `cost_to_serve_gbp`, not a recomputation;
`company/finance/customer_lifetime_revenue.py::build_summary()` — takes
`lifetime_cost_to_serve_gbp` as a plain constructor argument, never derives it). Clean like EV,
for the same reason: every consumer is a passthrough.

---

## 6. Carbon

**True owner:** ambiguous/undeclared, and the worst offender of the six by a wide margin.

**Second sources found: at least 5 independent emission-factor tables**, three of which
compute a semantically identical "grid carbon intensity by fuel source, gCO2/kWh" quantity and
materially disagree:

1. **`company/regulatory/carbon_emissions.py::_EMISSION_FACTORS_G_CO2_PER_KWH`** (line 10-18) —
   plain-string-keyed table: coal 820, gas 490, nuclear 12, wind 11, solar 41, hydro 24, biomass
   230, imports 300. **This is the module actually wired into the published surface** —
   `saas/reporting/annual_report.py:5162-5163` imports `FuelMixRecord` from it directly for the
   `_section_carbon_emissions()` report section (the only one of the five with a confirmed live
   caller among non-test code).
2. **`company/sustainability/carbon_intensity_register.py::_CARBON_INTENSITY_G_CO2_PER_KWH`**
   (lines 44-54) — its own `FuelSource(str, Enum)` (defined at line 31, NOT imported from
   anywhere else), its own table: natural_gas 394, coal 820, nuclear 12, wind_onshore 11,
   wind_offshore 12, solar 41, hydro 24, biomass 230, imports 300, other 200. Agrees with #1 on
   coal/nuclear/wind/solar/hydro/biomass/imports (same DESNZ-ish source), diverges by having a
   more granular gas split. **No caller found anywhere outside its own file** (dormant).
3. **`company/regulatory/fuel_mix_disclosure.py::_CARBON_INTENSITY`** (lines 46-56) — a THIRD,
   independently-defined `FuelSource(str, Enum)` (line 31, again not shared with #2's enum of
   the same name), with materially different values: wind_onshore **7.0** (vs 11.0 in #1/#2),
   solar **33.0** (vs 41.0), hydro **4.0** (vs 24.0 — a 6× divergence), biomass **120.0** (vs
   230.0 — ~2×), gas_ccgt 394 / gas_ocgt 610 (finer split again). **No caller found outside its
   own file** (dormant) — but a real numeric disagreement with the live #1 table, not just a
   different shape.
4. **`company/billing/carbon_footprint.py::_ELECTRICITY_INTENSITY_G_CO2E_PER_KWH`** (year-keyed,
   2016-2025) + `_GAS_KG_CO2E_PER_KWH = 0.18316` (lines 14-27) — a different quantity (per-year
   national grid average for customer bill carbon footprint), live-wired via
   `company/portal/app.py`. Legitimately a different question ("what did this customer's usage
   emit this year") from #1-3's ("what's the intensity of the supply mix we bought") — but it
   uses its own gas factor, **0.18316 kg/kWh**, which disagrees with:
5. **`company/sustainability/environmental_impact.py::_GAS_EMISSION_FACTOR = 0.18253`** (line
   30) + `_GRID_ELECTRICITY_FACTOR = 0.2104` (single fixed 2023 DEFRA value, not year-varying) —
   used for SECR/TCFD Scope 1/2/3 reporting (`EnvironmentalImpactRegister`). **No caller found
   outside its own file** (dormant). Its gas factor (0.18253) differs from #4's (0.18316) — a
   small but real, unreconciled numeric disagreement between two live-vs-dormant modules
   nominally computing the same DEFRA gas conversion factor.

**`company/carbon/carbon_ledger.py`** is structurally different from the above five: it is
explicitly **factor-agnostic** by design (its own docstring: *"NET and £/tCO2e are DERIVED VIEWS
over an append-only CarbonEvent stream... factor-agnostic (tCO2e values are handed in; the
emissions-factor set... [is] someone else's job)"*). It is the carbon analogue of
`saas/ledger.py` — an aggregation/P&L layer, not a source of the raw factor. No caller found
outside its own file (dormant), but architecturally it is a strong candidate to be the
**declared owner of the aggregate quantity** (`net_tco2e`, `£/tCO2e`) while one of #1-3 above is
declared the owner of the **upstream factor table** it should be fed from. Today nothing feeds
it — it and the five factor tables are unconnected.

**Verdict:** carbon has no declared owner today, live and dormant modules disagree numerically
on the same real-world DEFRA/grid figures, and two independently-defined `FuelSource` enums
exist with the same name and different membership. This is the strongest case in the six for why
the registry is needed — a structural clone detector would find none of this (every table is
differently shaped/keyed), exactly per §4's problem statement.

---

## 7. Registry schema (design, not built)

```
# One entry per domain quantity. Declared by a human/director-authored table,
# not inferred — inference is exactly the mechanism that lets a second owner
# sneak in by "looking similar enough".

OWNED_QUANTITIES: dict[str, QuantityOwnership] = {
    "net_margin_gbp": QuantityOwnership(
        owner_module="saas.ledger",
        owner_symbol="derive_pnl",
        status="CONTESTED",   # see §1 -- do not BUILD-close until re-declared
    ),
    "trading_treasury_balance_gbp": QuantityOwnership(
        owner_module="simulation.run_phase2b",   # candidate; needs consolidation (§2)
        owner_symbol=None,      # inline accumulation, not yet a named function
        status="CONTESTED",
    ),
    "company_cash_position_gbp": QuantityOwnership(
        owner_module="saas.ledger",
        owner_symbol="derive_cash_position",
        status="DECLARED",
    ),
    "enterprise_value_gbp": QuantityOwnership(
        owner_module="saas.enterprise_value",
        owner_symbol="build_enterprise_value",
        status="DECLARED",     # clean -- §3
    ),
    "bad_debt_gbp": QuantityOwnership(
        owner_module="simulation.arrears_engine",
        owner_symbol="compute_emergent_bad_debt",
        status="DECLARED",
    ),
    "cost_to_serve_gbp": QuantityOwnership(
        owner_module="saas.cost_to_serve",
        owner_symbol="build_cost_to_serve",
        status="DECLARED",     # clean -- §5
    ),
    "carbon_intensity_g_co2_per_kwh": QuantityOwnership(
        owner_module=None,     # UNDECLARED -- §6, director/architect call needed
        owner_symbol=None,
        status="UNDECLARED",
    ),
    "carbon_net_tco2e": QuantityOwnership(
        owner_module="company.carbon.carbon_ledger",
        owner_symbol="CarbonLedger.net",
        status="CANDIDATE",    # architecturally right shape, currently unfed
    ),
}
```

Each entry: `owner_module`, `owner_symbol` (function/class — narrower than module-level where
the module hosts more than one quantity), `status` ∈ {`DECLARED`, `CONTESTED`, `UNDECLARED`}. A
`CONTESTED` or `UNDECLARED` entry is **still covered** by the gate (see fail-open guard below) —
it just gates against *every* computing module until a human resolves which one wins, rather
than picking one silently. This matters directly for net margin, treasury, and carbon, all three
of which this DISCOVER found to be genuinely contested or undeclared, not just theoretically at
risk.

## 8. Gate semantics

- **Trigger:** on a diff (or full-tree scan), find every function/module whose output feeds a
  key matching one of `OWNED_QUANTITIES` (name-based static detection to start — matching the
  computed dict key / dataclass field name against the registry key; AST-level "computes a value
  assigned to this key" is the fidelity upgrade once the naive version is proven).
- **Pass condition:** every writer of an owned quantity is either the declared `owner_module` (or
  a documented passthrough — reads and republishes the owner's value unchanged, does not
  re-derive it) or is itself the `CONTESTED`/`UNDECLARED` set already on record above (frozen at
  DISCOVER time — the gate reds on any *new* writer, not on the pre-existing, already-logged
  ones, otherwise this DISCOVER's own findings would instantly red the gate on day one).
- **Red condition:** a module NOT in the owner/passthrough/pre-existing-contested set computes
  (assigns a new value to, not merely reads) an owned quantity's key.
- **FAIL-OPEN GUARD (mandatory, per the exit criteria):** the registry's covered-key set is
  matched with **default-closed** semantics — an unrecognised quantity name is not silently
  treated as "owned by nobody, anything goes". Concretely: the gate does not use "matches a
  known owned-quantity key → check ownership" as its only rule; it also flags any *newly
  introduced* key that looks like a domain-quantity computation (heuristic: `*_gbp`, `*_tco2e`,
  `*_margin*`, `*_treasury*`, `*_ev*` naming, or an AST body resembling one of the six's existing
  shapes) that is **not yet in the registry at all**, as a WARN (not a hard red, to avoid
  blocking unrelated work) requiring the quantity be either added to the registry or explicitly
  exempted. This is the guard against the tautology-adjacent failure mode: "covered set is empty
  today, so nothing computes an owned quantity, so the gate always passes" would be a FAIL-OPEN
  the moment the registry itself has a gap — which §6 (carbon) proves is not a hypothetical, it
  is the observed current state.
- **Independence (R15 tautology guard):** the gate module itself must compute **zero** domain
  quantities — it only reads AST/text and a static registry table. It must not import
  `saas.ledger`, `sim.risk_engine`, or any of the owner modules to "double check" a value; doing
  so would make the checker and the checked derive from the same source, the exact pattern R15
  forbids. This DISCOVER note is itself evidence the gate needs external test fixtures (a
  synthetic "planted second computation" file), never the real owner modules, to prove itself.

## 9. R15 both-ways plan (for BUILD, not executed here)

- **Fail direction:** copy `saas/ledger.py::derive_pnl`'s net-margin arithmetic (or any of the
  four already-found net-margin second sources above) into a NEW, throwaway test-fixture module
  not in the registry, assign its result to a field literally named `net_margin_gbp`. Gate must
  RED, citing the new module + the existing owner it collides with.
- **Pass direction:** delete the fixture (or make it a documented passthrough that only reads
  `derive_pnl()`'s output and republishes it, never re-derives). Gate must PASS.
- **Fail-open check specifically:** plant a computation of a quantity name that is deliberately
  ABSENT from the registry (e.g. `working_capital_ratio_gbp`, not currently one of the six).
  Confirm the WARN-level uncovered-quantity guard fires rather than the gate silently passing —
  proves the "default closed on the covered set" property rather than "silently open on anything
  not explicitly listed".
- **Independence check:** temporarily break/stub the gate's own import of the registry table
  (simulate the checker being unavailable). Confirm the surrounding CI step FAILS closed (an
  unavailable checker must count as a failed check, not a skip-and-pass) — R15's third killer
  pattern (FAIL-SILENT).

## 10. Anti-Goodhart

Per the ruling's §7 and this atom's own exit criteria: the count of quantities covered, the
count of second-sources found (11 total across the six above: 4 net margin + 3 treasury + 0 EV +
2 bad debt + 0 cost-to-serve + 5 carbon, tallied as *reported facts* in this document, not a
score), and any future "second-sources eliminated" delta are diagnostics only. None of these
numbers may be used as a target, a fitness input, or a promotion gate on their own — closing this
DISCOVER by reducing the count (e.g. deleting the dormant carbon modules just to make the tally
look better) without actually declaring one owner and reconciling the real numeric disagreement
(hydro 24 vs 4 g/kWh; gas 0.18316 vs 0.18253 kg/kWh) would be exactly the gaming this clause
forbids.
