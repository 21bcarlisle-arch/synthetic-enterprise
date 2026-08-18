# EP3_pricing_engine_late_truth — DISCOVER passes 1–2

*Pass 1 (2026-08-17) is the body below. Pass 2 (2026-08-18) is appended at the end and **corrects pass
1's live-path census**: the census seeded from one door and missed the other, so pass 1's headline
"the decided margin is 1.0%" measured one of two live legs. Read pass 2's F5 before citing pass 1's F1.*

**DISCOVER/FRAME ONLY.** `level_current` stays 0, `loop_stage` stays `idle`, no BUILD code written,
nothing in `file_scope` touched (it is empty). EPOCH_GATING_AND_ATOM_AUTHORSHIP rule 1 makes
DISCOVER/FRAME available on a parked atom while BUILD is not.

Measured at HEAD `38d1ede94`, with `docs/design/maturity_map.yaml`, this atom's simplifications store
and `docs/design/frame/` all clean in the shared tree at draw time. Every claim below is labelled
`observed-with-evidence` (command + output) or `inferred` (chain stated), per R9.

The atom's contract, from its own record: *"ex-ante cost stack (wholesale, losses, network, policy,
cost-to-serve, bad debt, capital) plus an explicit margin decision, priced against ESTIMATED costs and
then reconciled as true-ups arrive."* Its `gain`: *"Tariffs stop being back-calculated and become a
decision with an owner, inputs and an audit trail."* Its cited evidence is `EPOCH2_EVIDENCE.md` Q1,
which tested the director's suspicion that prices are back-calculated and concluded **evolution, not
replacement**, naming as the *biggest risk*: "treating this as 'no pricing logic exists' and building a
parallel pricing engine would duplicate real, working infrastructure."

**This pass's headline: that risk has already materialised.** The parallel engine exists, it is the one
module in the repo holding EP3's contract verbatim, and it has never been called by anything but its
own tests. EP3's first step is an adjudication, not a build.

---

## F1 — The struck rate does not depend on the customer. `eac_kwh` is a dead parameter.

`observed-with-evidence.` `saas/tariff_pricing.py::price_fixed_tariff` takes `eac_kwh: int` in its
signature and documents a per-customer capital charge. Run over a 100× consumption range (fwd £80/MWh,
`term_start` 2024-04-01, `naked_fraction` 0.15 = the live renewal desk's value, live 2024 policy and
network pass-throughs):

| EAC (kWh) | 500 | 1,000 | 2,000 | 3,000 | 4,000 | 8,000 | 12,000 | 50,000 |
|---|---|---|---|---|---|---|---|---|
| struck rate £/MWh | 196.761 | 196.761 | 196.761 | 196.761 | 196.761 | 196.761 | 196.761 | 196.761 |

**Distinct rates across the whole range: 1.** The module's own docstring says why — in
`expected_capital_cost_per_mwh = (Z × σ × naked_mwh × fwd × WACC) / eac_mwh`, `eac_mwh` cancels. It is
stated there as a property ("independent of customer size"); what is not stated is that it is the *last*
size-dependent term, so the whole function is size-blind and the parameter is inert.

Component decomposition of that £196.76/MWh (resi elec, 2024-04-01):

| # | component | £/MWh | share |
|---|---|---|---|
| 1 | wholesale (forward) | 80.000 | 40.7% |
| 2 | capital (VaR collateral) | 2.961 | 1.5% |
| 3 | **margin — `TARGET_MARGIN_GBP_PER_MWH`, a module constant** | **2.000** | **1.0%** |
| 4 | policy (RO+CfD pass-through) | 42.800 | 21.8% |
| 5 | network (DUoS+TNUoS pass-through) | 69.000 | 35.1% |
| 6 | profitability uplift (default) | 0.000 | 0.0% |

Six of EP3's seven named components. **Missing: losses, cost-to-serve, bad debt.** Two thirds of the
rate (policy + network, 56.9%) is pass-through the company does not decide; the decided margin is 1.0%.

## F1b — The obvious inference from F1 is FALSE. Under-recovery is refuted, and I checked before writing it.

`observed-with-evidence.` The tempting reading of F1 — "cost-to-serve is £55/yr fixed per account, worth
£27.50/MWh at 2,000 kWh and £4.58/MWh at 12,000, i.e. 2.3×–13.8× the entire margin term, and it is not in
the rate, therefore small accounts are structurally under-priced" — does not survive the next check. Real
suppliers recover fixed overhead in the **standing charge**, not the unit rate, and so does this company:

| year | resi elec SC | → per year | resi gas SC | → per year | CTS (`FIXED_OVERHEAD_GBP_PER_YEAR['resi']`) |
|---|---|---|---|---|---|
| 2016 | £0.2400/day | £87.60 | £0.2200/day | £80.30 | £55.00 |
| 2020 | £0.2700/day | £98.55 | £0.2500/day | £91.25 | £55.00 |
| 2024 | £0.6100/day | £222.65 | £0.3100/day | £113.15 | £55.00 |

The standing charge covers the £55/yr overhead with room in every year sampled, on either fuel alone.
**EP3 must not be built as "add a cost-to-serve term to the unit rate"** — that double-recovers a cost
already billed, and it would land as an R12-shaped tuning move dressed as a fidelity fix. Recorded here
because the wrong version of this finding is one grep away and reads well.

## F1c — The real defect is *where* the recovery sits: the fixed-cost line on the bill is not a company decision at all.

`observed-with-evidence.` The standing charge is a year-keyed table in `simulation/policy_costs.py`
(`_ELEC_SC_PENCE_PER_DAY_BY_YEAR`, `get_electricity_standing_charge_per_day`) — the **world** side — with a
flat fallback in `saas/non_commodity.py::standing_charge_rate`, which documents itself as "FALLBACK ONLY".
No module in `company/` decides it. Its own docstring says it covers "metering costs, network fixed
capacity, **and supplier admin**" — so the supplier's own overhead recovery is set by a published table
the company reads.

`inferred` (chain: F1 table + the SC table above): on a 3,000 kWh resi elec account in 2024 the company
decides **£6.00/yr** of margin (3 MWh × £2.00) against **£222.65/yr** of standing charge it does not decide.
The explicit margin decision is 2.7% of the undecided fixed-recovery line on the same bill.

This is the precise, defensible sense in which the director's suspicion holds — and it is **not** the sense
`EPOCH2_EVIDENCE` Q1 framed. Q1's `inferred` paragraph says the *margin constant* is not a governed
decision (true, and still true). It never examined the standing charge, which is the larger undecided
number and sits on the same bill. **EP3's target should be restated as: the company decides one term of
its own price and inherits the rest — including a fixed-cost line larger than its margin.**

`observed-with-evidence` on the atom's own `origin_note` constraint ("the cost stack keyed by REGIME
rather than implicitly Ofgem, or a second market never fits behind this seam"): unmet today, at a named
signature. `get_electricity_standing_charge_per_day(date_str, segment)` has no regime parameter; a grep
for `regime` across `policy_costs.py`, `tariff_pricing.py` and `non_commodity.py` returns exactly one hit
and it is an unrelated comment (`policy_costs.py:406`, "similar pre-cap regime").

## F2 — EP3's deliverables are already built. Ten pricing-lane modules have zero non-test importers.

`observed-with-evidence.` AST import graph over **2,310 `.py` files** (resolving `import` and `from … import`,
prefix-matched, so submodule imports count), not a name grep:

| module | lines | non-test importers | test importers |
|---|---|---|---|
| `company/pricing/renewal_pricing_engine.py` | 192 | **0** | 2 |
| `company/pricing/price_transparency_register.py` | — | **0** | 1 |
| `company/billing/tariff_change_log.py` | — | **0** | 1 |
| `company/pricing/tariff_smoothing.py` | — | **0** | 1 |
| `company/pricing/price_elasticity.py` | — | **0** | 1 |
| `company/pricing/cost_to_serve.py` | — | **0** | 1 |
| `company/pricing/segment_profitability.py` | 153 | **0** | 1 |
| `company/finance/segment_profitability.py` | 154 | **0** | 1 |
| `company/crm/portfolio_repricing.py` | 181 | **0** | 1 |
| `company/market/llf_register.py` | — | **0** | 1 |

The live pricing path, by contrast, is exactly four modules:
`company/interfaces/renewal_offer.py` → `company/pricing/renewal_desk.py` → `saas/tariff_pricing.py`
(plus `company/interfaces/tou_offer.py` → `company/pricing/tou_desk.py` for ToU), with
`company/pricing/tariff_engine.py` (4 non-test importers) supplying the company's own forward view.

Three of the dark modules are EP3's own named deliverables:

- **`renewal_pricing_engine.py` holds EP3's contract verbatim.** Its docstring: *"Cost-to-serve floor:
  price must cover wholesale + non-commodity + CTS · SVT ceiling · Price elasticity · Expected margin:
  maximize conversion × margin_per_customer."* That is the cost-stack-plus-explicit-margin-decision the
  atom exists to build. 192 lines, two test files, never called.
- **`price_transparency_register.py` is the "audit trail"** in EP3's `gain` line.
- **`tariff_change_log.py` is the versioning** whose absence Q1's `inferred` paragraph named ("a hardcoded
  module constant with no versioning, no cadence").

`inferred`: EP3 as filed reads as a build (`level_target: 3`). Measured, its first step is an
**adjudication over ten modules — wire, fold, or delete each** — and only then a build of what is genuinely
missing. Q1 warned against building a duplicate; the duplicate is already on disk. Two of the ten are
literally the same module name in two packages (`pricing/` and `finance/segment_profitability.py`,
different content, 153 vs 154 lines), so the adjudication has a de-duplication half as well as a wiring half.

This also has a live consequence beyond EP3: **the pricing lane's test count is not evidence of pricing
behaviour.** Ten modules' worth of tests pass against code no run executes.

## F3 — The "late truth" half has no implementation, and the map does not record the dependency the atom's own name asserts.

`observed-with-evidence.` `grep -rn "true_up|trueup|true-up" --include=*.py company saas simulation sim`
returns **2 lines, both prose in docstrings**, neither a mechanism:
`company/regulatory/seg_export_estimator.py:9` and `saas/ledger.py:300` ("accounts would carry until the
true-up lands"). There is no module that compares a struck price against realised cost as truth arrives.

`observed-with-evidence.` The atom that owns that half, `EP5_settlement_true_ups`, is
`level_current: 0`, `loop_stage: idle`, `epoch: 2`, `depends_on: []`, `couples_with:
[W3_2_settlement_timetable]`. EP3's own row is `depends_on: []`, `couples_with: []`. **Neither row names the
other**, though EP3's title is "Prices decided ex-ante, then met by **late cost truth**" and its body says
"reconciled as true-ups arrive".

**QUEUED, not taken** (per SELF-INTERRUPT DISCIPLINE — editing another atom's row is outside this pass's
declared touch): EP3 should carry EP5 in `depends_on`, or the two should be a `couples_with` pair. Decided
by whoever opens either for BUILD. Stated so the next drawer does not re-derive it.

## F4 — Side finding, QUEUED not fixed: a named path in the carbon guard has moved, and the guard's own fail-silent control cannot see it.

`observed-with-evidence.` `tests/company/test_carbon_not_a_target.py::_SURFACE_GLOBS` names
`company/crm/renewal_pricing_engine.py`. That file does not exist — the module is at
`company/pricing/renewal_pricing_engine.py`. `_surface_files()` drops a non-existent named path silently.

The anti-fail-silent control sitting directly beside it, `test_decision_surfaces_exist`, asserts
`len(files) >= 5` — but the `company/pricing/*.py` glob alone resolves about ten files, so **no individually
named path can ever make that assertion fire by vanishing.** R15 class: a per-item FAIL-OPEN hiding behind
a population-level count. (The carbon guard still covers this module in practice, via the `company/pricing/*.py`
glob — so this is a control-integrity defect, not a live coverage hole.)

Not fixed on sight: outside `file_scope`, and it is a harness item rather than an EP3 item. Registered here
for the harness queue.

---

## What the next pass should do

1. **Adjudicate the ten dark modules before writing any pricing code** (F2). For each: wire / fold / delete,
   with the reason. `renewal_pricing_engine.py` is first — it already states EP3's contract, so the question
   is whether EP3 is "wire this" plus its gaps, and `level_target: 3` may be wrong on the high side.
2. **Restate the atom's target per F1c** — the gap is not a missing cost-stack term (F1b refutes that), it is
   that the company decides £6.00/yr of margin and inherits a £222.65/yr fixed-recovery line set by a world
   table. That reframing changes what a falsifier would even measure.
3. **The falsifier is named AND already run** — not proposed for a later pass (the standing lesson from the
   EP17 pass-2/pass-3 cycle: run the exit test, do not re-propose it). The test: *the struck rate must respond
   to a change in a per-account cost input.* **Run against HEAD `38d1ede94` in F1 above: RED.** One distinct
   rate (£196.761/MWh) across a 100× EAC range, because `eac_kwh` cancels out of the only term that used it.
   So this is a real exit test that fails on today's code — not a criterion already green on unbuilt code, and
   not one that needs a population the book cannot supply. It runs on a pure function with no fixtures.
   Its honest limit, stated rather than discovered later: it is necessary, not sufficient — it would go green
   on *any* size-sensitive term, including a wrong one, so it must be paired with F1b's constraint (no
   double-recovery against the standing charge) or it will reward the exact defect F1b refutes.

---
---

# DISCOVER pass 2 — 2026-08-18

**DISCOVER/FRAME ONLY.** `level_current` stays 0, `loop_stage` stays `idle`, no BUILD code written,
nothing in `file_scope` touched (it is empty). Measured at HEAD `7c933dbcf`, with
`docs/design/maturity_map.yaml`, this atom's simplifications store and `docs/design/frame/` all clean
in the shared tree at draw time. R9 labels throughout.

Pass 1 closed by naming three things for the next pass: adjudicate the ten dark modules, restate the
target per F1c, and note that the falsifier was already run. This pass started on the adjudication and
found that **the thing being adjudicated was measured against the wrong live baseline**, so the
adjudication's premise had to be re-established first. Everything below is that re-establishment.

## F5 — Pass 1's live-path census was too narrow. There are TWO live pricing legs, not one, and pass 1 measured the smaller.

`observed-with-evidence.` Pass 1 recorded *"the live path is four modules: `interfaces/renewal_offer`
-> `pricing/renewal_desk` -> `saas/tariff_pricing` (+ `tou_offer` -> `tou_desk`)"*. Re-running the
closure from those seeds reproduces exactly that. But the seeds were the wrong set: an AST import
census over 4,546 `.py` files (`.claude/worktrees/` excluded) shows
`simulation/run_phase2b.py` — the published-run entry point — imports **two** company pricing doors at
`run_phase2b.py:61` and `run_phase2b.py:65`:

  * `company.interfaces.renewal_offer` — the STRIKE, which is what pass 1 measured; and
  * `company.interfaces.renewal_rate_chain` — **five further writers that move that struck rate**,
    which pass 1 did not see at all.

`observed-with-evidence.` The second door reaches the published artefacts:
`company/interfaces/renewal_rate_chain.py` <- `simulation/run_phase2b.py` <-
`simulation/run_phase4c_on_phase2b.py` <- `tools/run_annual_report.py` and `tools/run_frozen_baseline.py`
<- `background/process_run_complete.py`. This is not a dark module: it is on the path that writes the
annual report and the frozen baseline.

`observed-with-evidence.` The chain's own docstring
(`company/pricing/renewal_rate_chain.py:20-31`) names its five writers and their order: *"The term is
struck at one rate; the premium multiplies it; the surcharge multiplies that; the profitability uplift
adds to that; the cap clamps the result."*

**Consequence for the atom's record.** Pass 1's F1 conclusion — *"56.9% is pass-through the company
does not decide; the decided margin is 1.0%"* — is arithmetic about the STRIKE only. It stands as a
statement about `saas/tariff_pricing.price_fixed_tariff`, and it is not a statement about what the
company decides, because four more company-side writers fire afterwards. Measured spans in F6.

## F6 — Measured on the published run: the company's decided writers move the rate by −59.9% to +38.0%, and a third of their firings are set by a hard-coded bound rather than by any input.

`observed-with-evidence.` `docs/reports/run_output_latest.json` carries `rate_decomposition_log`
(n=118), `dynamic_pricing_log` (n=118) and `margin_feedback_log` (n=31) — the audit trail EP3's gain
line asks for **already exists and is already published**. Decomposing all 118:

| writer | firings | at a hard-coded bound |
|---|---|---|
| `portfolio_premium` | 118 / 118 | **33** (19 at `PORTFOLIO_PREMIUM_MIN` −5.00%, 14 at `PORTFOLIO_PREMIUM_MAX` +15.00%) |
| `margin_surcharge` | 31 / 118 | **18** (all at `FEEDBACK_MAX_SURCHARGE` = 20.00%) |
| `price_cap` | 18 / 118 | n/a (the clamp *is* the bound) |
| `profitability_uplift` | **0 / 118** | — see F7 |

Total move against the struck rate: min −59.90%, median −1.44%, max +38.00%; no renewal is left
unmoved (0 of 118 has zero move). **51 of the 167 premium/surcharge firings (30.5%) land exactly on a
free literal**, so for roughly a third of the decisions the clamp, not the model, is the price.

`observed-with-evidence.` The premium is a proportional controller on the company's OWN realised
margin: `compute_portfolio_premium(recent_margin_rates, target=PORTFOLIO_TARGET_MARGIN_RATE)`,
constants at `company/pricing/tariff_engine.py:72-76` — target `0.08`, half-life `0.50`, bounds
`−0.05`/`+0.15`. Driving the live door with a struck rate of £196.761/MWh and a flat portfolio outturn:

```
portfolio_margin=-0.20 -> 224.3075     +0.08 -> 196.7610 (no move; setpoint)
portfolio_margin=+0.00 -> 204.6314     +0.20 -> 186.9229 (saturated)
portfolio_margin=+0.05 -> 199.7124     +0.40 -> 186.9229 (same; saturated)
```

**This is the mechanism form of the director's Q1 suspicion, and it is sharper than the prose version.**
The price is not merely correlated with outturn margin — it is a feedback term whose setpoint is a
margin number, closing half the gap per cycle. Whether that is a defect is a judgement EP3 has to make
rather than inherit: a real supplier does reprice after under-earning. What is *not* a judgement call
is that `PORTFOLIO_TARGET_MARGIN_RATE = 0.08` is a free literal with a comment and no cited source, on
a quantity Ofgem sets an EBIT allowance for; and that it is the only explicit margin decision on the
live path, which means EP3's "plus an explicit margin decision" is **already built, as a controller**.

`observed-with-evidence.` The per-account writer is one-sided: sweeping `prior_term_margin_gbp` at
`prior_term_revenue_gbp=1000`, losses above the 5%-of-revenue threshold add a surcharge (−£200 →
£226.28, −£500 → £236.11) while every non-negative value leaves the rate untouched. Profits never
reduce a customer's rate; losses always raise it.

`observed-with-evidence.` At `term_index=0` **no writer in the chain fires at all** (verified across
the sweep). A first-term customer's contracted rate is therefore exactly pass 1's strike — one distinct
rate across a 100× EAC range. Pass 1's F1 and this pass's F6 compose: the rate is size-blind for the
acquisition term and outturn-driven thereafter.

## F7 — Writer 3 of the five is structurally dead in production, and it fails open through three layers. Mutation-proved.

`observed-with-evidence.` `profitability_uplift` fires **0 times in 118 published renewals**, while the
writer beside it answering a near-identical question (was this account's prior term a loss?) fires 31
times. The cause is a field that does not exist:

  * `company/crm/customer_profitability.py:165` — `estimate_prior_term_net_margin` groups the
    supplier's settled records by `r.get("term_start")` and returns `None` when that set is empty.
  * The production settlement records carry no such key. `simulation/hedged_settlement.py:195-217`
    (and the deemed/flex/gas producers beside it) emit `customer_id`, `settlement_date`,
    `settlement_period`, `consumption_kwh`, `revenue_gbp`, `margin_gbp`, `net_margin_gbp`,
    `capital_cost_gbp` … and **no `term_start`**. `grep -n '"term_start"' simulation/hedged_settlement.py
    simulation/gas_settlement.py` returns nothing.
  * So `prior_term_starts` is empty for every account in every year → `None` → `compute_profitability_uplift`
    maps `None` to `0.0` → `renewal_unit_rate_uplift` returns `0.0` → the chain's `if pnl_uplift > 0`
    never fires.

`observed-with-evidence.` **Mutation proof**, one call, one key of difference:

```
production-shaped records (net_margin_gbp = -20 × 4, no term_start key): uplift = 0.0
same records + "term_start": "2018-04-01":                              uplift = 5.0
```

`observed-with-evidence.` The tests are green because the fixtures supply the missing key:
`tests/company/test_customer_profitability.py:23` builds records with `"term_start": term_start`, and
`tests/company/interfaces/test_customer_profitability_seam.py:71,78,170` hard-code
`"term_start": "2018-04-01"`. **The graded record shape is not the shipped record shape.**

`inferred (chain stated).` R15 class: FAIL-OPEN, and it is fail-open at three levels rather than one.
Each layer's docstring documents its zero as legitimate — *"Returns None if: no matching records
exist"*, *"Returns 0.0 — not an error, and not a raised exception — for every renewal the policy does
not apply to"* — so a silently-absent input is indistinguishable from a correctly-declined one at every
boundary. No control anywhere asserts that this writer ever fires. The honest limit on this finding: it
proves the writer cannot fire, not that firing it would improve the run; the P&L effect of a
£5.00/MWh uplift on the ~31 loss-making prior terms is unmeasured here and is BUILD work.

## F8 — The atom's own named falsifier is satisfiable by the back-calculation EP3 exists to remove.

`inferred (chain stated, from F6's measurements).` Pass 1 named and ran the exit test *"the struck rate
must respond to a change in a per-account cost input"*, RED at the strike. Applied to the **live chain**
instead of the pure strike function, it goes GREEN at `term_index >= 1` — F6 shows a per-account number
(`prior_term_margin_gbp`) moving the contracted rate by up to +20%. But that number is realised outturn
margin, not a forward cost. So the falsifier as worded would be discharged by precisely the mechanism
the atom's gain line says it wants removed.

**Restatement for whoever opens EP3 for BUILD** — the criterion needs both halves, or it grades the
defect as the fix:

  1. run it at `term_index = 0`, where F6 shows no chain writer fires, so only the strike is under test; and
  2. name a FORWARD cost input (a per-account cost-to-serve or loss factor), not any quantity derived
     from a completed term — otherwise outturn feedback discharges it.

Pass 1's own pairing constraint still applies on top: any size-sensitive term must not double-recover
the standing charge (pass 1 F1b).

---

## What pass 3 should do

1. **The ten-module adjudication is still owed** — pass 2 spent itself re-establishing the baseline it
   was to be measured against. Re-confirmed at HEAD `7c933dbcf`: all ten still have zero non-test
   importers (`renewal_pricing_engine` 192 lines, `price_elasticity` 217, `price_transparency_register`
   181, `portfolio_repricing` 181, `llf_register` 172, `finance/segment_profitability` 154,
   `pricing/segment_profitability` 153, `cost_to_serve` 138, `tariff_change_log` 101,
   `tariff_smoothing` 86). The adjudication is now a THREE-way question per module, not two: wire /
   fold / delete **against a live chain that already does more than pass 1 credited**.
2. **F7 is the cheapest real thing in this atom** — one absent key, mutation-proved, in company code on
   the published path. It is recorded here rather than minted as a separate staged finding
   (SELF-INTERRUPT DISCIPLINE: queue, and the atom's own record is where an EP3-subject finding
   belongs) — but it does not need EP3 to be opened, and whoever touches `renewal_rate_chain` next
   should take it.
3. **F1c's restatement is still owed and is now cheaper to state**: the company decides a £2.00/MWh
   margin term plus a controller bounded at ±5/15%, and inherits a £222.65/yr standing charge set by a
   world table. Both halves are now measured.
4. **Pass 1's queued FINDING 2 is half-wrong as worded, and this pass can say which half.** It offered
   "EP3 should carry EP5 in `depends_on`, **or** the two should be a `couples_with` pair". The second
   option is not available: `couples_with` in this map is a **world↔company** topology, validated by
   `tests/design/test_maturity_map_facets.py` against a hard-coded `EXPECTED_PAIRS` authority
   (§ "(b) couples_with topology (C5) … present and SYMMETRIC"), and EP3 and EP5 are both company-side
   atoms. So the only available form is `depends_on`. Still not taken here, for a reason pass 1 did not
   have: `EP5_settlement_true_ups` is itself level 0 / idle, so `EP3 depends_on EP5` is a *sequencing
   claim* — it would say EP3 cannot build until EP5 does — and that is a BUILD-order decision, not a
   DISCOVER one. Whoever opens either atom takes it with that consequence stated.
