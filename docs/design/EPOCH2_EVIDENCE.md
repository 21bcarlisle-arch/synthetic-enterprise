# EPOCH2_EVIDENCE — architecture evidence pass for "The Value Cycle"

Desk work only, per docs/staging/done/EPOCH2_EVIDENCE_PASS.md and
EPOCH2_INTENT_RIDER.md. No fixes, no refactors made. Every claim below is
labelled `observed-with-evidence` (file:line cited) or `inferred` (chain
stated), per R9.

## Q1. How are retail tariffs actually set today?

**observed-with-evidence:** Pricing IS decided ex-ante via a real six-component
cost stack, not back-calculated from outcomes. `saas/tariff_pricing.py::price_fixed_tariff()`
(lines 36-101) sums: (1) `forward_price` — synthetic forward wholesale cost;
(2) `expected_capital_cost_per_mwh` — VaR collateral cost, using the regulatory
sigma floor not current-market sigma (tariff_pricing.py:70-77); (3)
`TARGET_MARGIN_GBP_PER_MWH` — flat £2/MWh (tariff_pricing.py:30); (4)
`policy_cost_per_mwh` — RO+CfD levy pass-through; (5) `network_cost_per_mwh` —
DUoS+TNUoS pass-through; (6) `profitability_uplift_per_mwh` — a binary
net-negative repricing signal from `company/crm/customer_profitability.py::compute_profitability_uplift()`
(lines 176-189), called at renewal (simulation/run_phase2b.py:1396 area, gas
tariff-schedule build at ~line 466). Cadence: every contract term (acquisition
+ renewal, `run_phase2b.py`'s `_build_gas_tariff_schedule` loop, term_start
driven). Owner: `saas/tariff_pricing.py`, called from `simulation/run_phase2b.py`.

**inferred:** the margin component itself is NOT a governed decision — it is a
hardcoded module constant with no versioning, no cadence, no explicit
competitive positioning at pricing time (SVT rate is fetched only for
post-hoc churn-risk estimation, `_build_churn_basis_risk()` at run_phase2b.py:483-497,
never fed back into the price itself). The "ex-post margin bridge" the rider
names (decompose realised margin against volume/price/shape/churn/debt/
true-up variance) does not exist — `compute_profitability_uplift()` is a
binary net-negative/not-negative signal, not a decomposition.

**Epoch 2 implication: evolution.** The cost-stack skeleton is real, correct,
and already anchored (regulatory sigma floor, real policy/network
pass-throughs) — this is not "no pricing decision exists." The gap is
governance and decomposition layered on top of already-sound infrastructure,
not a replacement. **Biggest risk:** treating this as "no pricing logic
exists" (the director's stated suspicion) and building a parallel pricing
engine would duplicate real, working infrastructure rather than extending it.

## Q2. What is the event model, and could truth arrive late?

**observed-with-evidence:** `simulation/settlement.py::run_settlement()`
(lines 22-40) computes one settlement record per (customer, half-hourly
period) in a single batch pass over `system_price_records` — real, already-
historical Elexon SSP data, known at generation time. There is no provisional/
corrected two-phase computation at the settlement level; it is atomic,
single-pass, computed once per period from already-resolved data.

**observed-with-evidence:** `simulation/meter_reads.py` (built this session,
Phase 3) IS a genuine two-clock mechanic at the BILL-DOCUMENT layer: a bill
can carry an "estimated" flag now, with the real reading arriving and
correcting the *displayed* consumption figure later (`ESTIMATE_TRAILING_WINDOW`,
`MAX_CONSECUTIVE_ESTIMATED_PERIODS` back-billing cap). But the module's own
docstring (meter_reads.py lines 24-29) states explicitly: "this module does not
alter settlement-based revenue recognition... this phase is purely about the
document a customer would see, not the numbers behind it." The underlying
revenue/margin figure is never restated once computed.

**inferred:** there is currently exactly one clock (settlement, computed once,
authoritative) with a cosmetic second clock bolted onto the bill *display*
only. The rider's "three clocks (billed, settled, banked) that converge" do
not exist as separate trackable states today — there is no append-only
correction ledger anywhere in the settlement/billing pipeline.

**Epoch 2 implication: foundational rework.** Carrying two real timestamps
per FINANCIAL fact (not just a display flag) means every downstream consumer
of settlement/bill data (P&L, CLV, margin) would need to consume a
point-in-time-queryable ledger instead of a single computed value — this is
an architectural change to the compute model itself, not a contained
addition. **Biggest risk:** underestimating this as "just add a
timestamp field" when the real cost is redesigning how P&L/margin/CLV
read state at all.

## Q3. What do compute and storage actually scale with?

**observed-with-evidence:** Real full 10-year run timings, `docs/observability/sim-runner-log.md`
(2026-07-09 14:01/14:10 UTC entries): `elapsed_s: 477` and `476` seconds
(~8 minutes) per full run, producing a `run_output_*.json` of `size_kb: 2506`
(~2.5MB), for the current population (`saas/customers.py::CUSTOMERS`, 27
literal entries incl. gas twins/I&C/successors — confirmed via
`grep -c '"customer_id":'`).

**observed-with-evidence:** population size is NOT a runtime parameter today.
`simulation/run_phase2b.py::main()` (line 653) takes `report_end`,
`sim_interface`, `policy` — no population/count argument. `CUSTOMERS` is
imported directly as a fixed list literal (run_phase2b.py:32); `ELEC_CUSTOMERS`/
`GAS_CUSTOMERS` (lines 140-141) are pure filters over that fixed list. The
only population growth is `ACQUIRED_CUSTOMERS` (Phase 8a growth mandate),
appended during a run, not a start-of-run size choice.

**inferred:** storage scales with customers × settlement periods (half-hourly,
2016-2025 ≈ 175,000 periods/customer) — 27 customers × ~175k periods already
produces ~2.5MB/run; this is compute-bound (8 min wall-time) more than
storage-bound at current scale. Directionally, a 10-100x population increase
would scale settlement compute roughly linearly (no evidence of a
super-linear per-customer cost found) but the *bigger* risk is the JSON-blob-
per-run storage model itself — at 100x customers the ~2.5MB run_output would
become ~250MB, and this file is read wholesale by nearly every `tools/generate_*.py`
consumer (confirmed pattern all session: `json.loads(Path(run_json_path).read_text())`),
which does not scale to repeated full-history reruns (the tournament scenario).

**Epoch 2 implication: partial rebuild.** The settlement/compute core likely
scales acceptably; the "read the whole JSON blob every time" consumption
pattern does not, and population size needs to become a real constructor
parameter before 10-100x is meaningfully testable at all (today it cannot be
tested — there is no lever). **Biggest risk:** discovering the JSON-blob
bottleneck only after building the tournament infrastructure on top of it.

## Q4. Customer truth: read from the SIM, or discovered through interfaces?

**observed-with-evidence:** `company/interfaces/sim_interface.py`'s `SimInterface`
class (lines 23-56) exposes only observable outputs: `get_settlement_data()`
returns `{mpan, period, consumption_kwh, unit_rate_gbp_per_mwh}`;
`get_customer_status()` returns a coarse `'active'|'churned'|'unknown'`. This
is a correctly-designed observable seam.

**observed-with-evidence:** `tools/epistemic_verifier.py`'s `FORBIDDEN_SOURCES`
(lines 29-36) only pattern-matches `from sim.`/`from simulation.` imports —
`saas.*` is not forbidden. Three `company/` files import directly from `saas/`:
`company/portal/app.py:52` (`from saas.customers import CUSTOMERS`),
`company/crm/enriched_churn_estimate.py:26` and
`company/crm/payment_churn_model.py:24` (`from saas.churn_model import ...`).
`company/portal/app.py:171` builds `_CUSTOMER_INDEX = {c["customer_id"]: c for c in CUSTOMERS}`
and looks customers up directly from this dict throughout the file (the exact
mechanism this session's own C1 smart-meter fix touched) — `CUSTOMERS` entries
carry `home_type`, `bedrooms`, `epc_rating`, `smart_meter`, `eac_kwh`: physical-
property ground truth, not data a real supplier would have via a discovery
process (onboarding form, meter install record, EPC register lookup).

**inferred:** the epistemic wall as *enforced by tooling* is narrower than the
wall as *stated in CLAUDE.md's architectural law* ("Could a real UK energy
supplier know this?", worded generally, not scoped to the literal `simulation/`
package). `saas/` sits in an ambiguous middle layer that the verifier
currently treats as safe by omission, not by design review.

**Epoch 2 implication: foundational rework.** This is the most severe finding
in this pass: the company's own customer-facing portal reads simulation-
adjacent ground truth directly, not through any interface/discovery layer.
Closing this needs the two-layer model the rider names (hidden SIM truth vs.
company belief, gap closed only through interface events) — a structural
change to how `company/portal/app.py` and the two churn-model consumers get
customer data, not a patch. **Biggest risk:** this exact gap already produced
a real, live bug this session (C1's `smart_meter` flag silently defaulting
wrong because the "truth" it read had a missing field) — the class recurs
until the read path itself changes, matching R10's own logic applied one
level up the stack.

## Q5. Are customer generation and validation independently anchored?

**observed-with-evidence:** `company/compliance/domain_invariants.py` (built
this session, Phase 2) imports only from `company/pricing/ofgem_price_cap.py`
(line 33) and hardcodes constants sourced from `docs/market_research/ASSUMPTIONS.md`
/ `ons_consumption_profiles.md` (real Ofgem/DESNZ/ONS publications, cited in
each invariant's `source` field) — independent of `saas/property_model.py` or
`saas/household.py`'s own generation logic. No shared-anchor "marking its own
homework" risk found in this module.

**observed-with-evidence:** `saas/property_model.py`'s own docstring (lines
17-22) states its `ASSET_PROFILE_BY_CUSTOMER`/`OCCUPANCY_PATTERN_BY_CUSTOMER`
constants are "placeholders pending... real EPC/Census/Ofgem data" — i.e. the
GENERATOR itself is not currently anchored to any real distribution at all
(hand-picked per-customer constants), while the new validator IS anchored to
real TDCV/ONS data.

**inferred:** generation and validation are independently sourced today, but
this appears incidental (the generator simply isn't anchored to anything, so
there is nothing for the validator to share) rather than a deliberate
anti-mark-own-homework design. Wall direction confirmed clean by omission:
neither `domain_invariants.py` nor `obligations_register.py` imports
`simulation.*` or `saas.property_model`/`saas.household` (checked directly).

**Epoch 2 implication: evolution.** The independence property the director
wants already holds, but for the wrong reason (generator has no anchor to
share, not "we deliberately kept these separate"). Once `property_model.py`'s
placeholders get anchored to real EPC/Census data (already flagged as
backlog, PRIORITIES.md), a deliberate check must be added confirming the two
stay independent — today's accidental independence would not survive that
change unmonitored. **Biggest risk:** the anchoring backlog item lands without
this check, and the generator silently starts sharing a source with its own
validator.

## Q6. Is the customer population fixed across runs, or drawn per run?

**observed-with-evidence:** `saas/customers.py::CUSTOMERS` is a hardcoded
Python list literal (confirmed this session building `obligations_register.py`
and `domain_invariants.py`, which both read live customer data all session) —
identical every run, no RNG, no per-run variation of composition, mix, or
count. `simulation/run_phase2b.py:814`: `_payment_rng = random.Random(42 + 7919)`
— a fixed, hardcoded seed, confirmed for payment-behaviour randomness; the
same fixed-seed pattern is the norm throughout this codebase (every
deterministic-dispatch RNG this session's own new modules used, e.g.
`simulation/meter_reads.py`'s `random.Random(f"meterread_{customer_id}_{period_end}")`,
follows this same seeded-not-varied convention).

**inferred:** every run plays the identical customer cast with identical
stochastic outcomes end to end — this is, in the rider's own framing, "a
demonstration," not "an experiment." No mechanism exists to vary
population mix/skew/meter-ratio/vulnerability-incidence per run, and no
run-level seed parameter was found that would let one.

**Epoch 2 implication: partial rebuild.** The individual customer records and
their generation logic (property_model.py, household.py) are real and
detailed — the gap is purely at the population-ASSEMBLY layer: there is no
"draw N customers with distribution X" function, only a fixed list. Building
one is additive (a new population-generator module) rather than a rewrite of
existing per-customer physics. **Biggest risk:** this blocks the epoch-4
tournament precondition entirely today — there is no lever to pull, so
"drawn population" work must land before any tournament design work is
worth starting.

---

**Summary for Epoch 2 framing:** two questions land as evolution (Q1, Q5),
two as partial rebuild (Q3, Q6), two as foundational rework (Q2, Q4). The
single largest finding is Q4 — the epistemic wall gap is real, already
caused a live bug this session, and is enforced more narrowly by tooling than
the architectural law states. The rider's two named deficiencies (estimated-
billing/rebilling as a real cycle; ex-ante pricing + ex-post margin bridge)
are both confirmed real gaps, not findings to debate, matching the rider's
own framing — Q1 shows real pricing infrastructure that needs governance, Q2
shows genuinely no restatement mechanism at the financial level.
