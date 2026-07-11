# C — Customer Operations: lane charter

**Dial reached 3 (hot) 2026-07-11** (docs/design/MATURITY_MAP.md Section 8) — charter earned
per the map's own rule ("a lane earns its charter when its dial reaches 3+").

## Mission

The company must know its customers the way a real UK energy supplier does: segmented by real
CRM-style attributes, satisfied (or not) in a distribution matching real survey data, and —
critically, the lane's one genuinely open gap — discovered through observable interfaces, never
by reading simulation ground truth directly. "A real supplier only learns a property's true
attributes via meter install/survey/customer disclosure" (`C2_discovery_through_interfaces`'s own
`real_world_twin`, `docs/design/maturity_map.yaml`).

## Sub-capability tree

- **C1_segment_layers** — customer segment flavour fields (smart meter, dual-fuel, home/business
  type) — AT TARGET (level 3/3).
- **C2_discovery_through_interfaces** (this lane's genuine gap) — portal discovers customer
  physical-property truth through observable interfaces, not a direct read.
- **C3_satisfaction_heterogeneity** — per-customer satisfaction heterogeneity (payment-channel
  gap + individual variation) — AT TARGET (level 3/3).
- Shares its epistemic-wall concern with **W2_customer_generator** (lane W2, population-side
  generation) and rides the same wall enforcement `tools/epistemic_verifier.py` implements for
  `simulation.*` imports — C2's gap is specifically that `saas.*` imports are NOT covered by that
  tool today (see below), a related but distinct enforcement seam.

## What L2/L3/L4 mean in this lane's terms

**C2_discovery_through_interfaces (the open gap, most of this charter's depth):**
- **L1 (current state, confirmed real via `docs/design/EPOCH2_EVIDENCE.md` Q4):**
  `company/portal/app.py` imports `saas.customers.CUSTOMERS` directly and looks customers up from
  a dict built over that import (`_CUSTOMER_INDEX`) — `CUSTOMERS` entries carry `home_type`,
  `bedrooms`, `epc_rating`, `smart_meter`, `eac_kwh`: physical-property ground truth, not data
  reaching the company through any discovery process. Two churn-model consumers
  (`company/crm/enriched_churn_estimate.py`, `company/crm/payment_churn_model.py`) have the same
  shape. `tools/epistemic_verifier.py`'s `FORBIDDEN_SOURCES` only pattern-matches
  `sim.`/`simulation.` imports — `saas.*` is invisible to it, so this gap has never once been
  caught by the tool built to catch exactly this class of violation. This already caused a real,
  live bug in a prior session (C1's `smart_meter` flag silently defaulting wrong because the
  "truth" it read had a missing field).
- **L2:** a real observable-interface layer exists (analogous to the real UK MPAS/ECOES system —
  see references below) that infers/discovers property attributes from what a real supplier
  could actually observe — meter-install records, customer self-declaration at signup, a survey
  event — rather than reading `saas.customers.CUSTOMERS` ground truth directly. `company/
  portal/app.py` and the two churn-model consumers read from this layer instead.
- **L3:** the portal's own decisions (tariff eligibility, risk scoring, any segment-conditional
  logic) demonstrably use only the discovered/observed view, never the ground truth — proven by
  a real divergence test showing the two CAN differ and the company's decision follows the
  observed view when they do.
- **L4:** the SIM side can inject a genuine "discovery error" (e.g. a wrong self-declared property
  type, matching how a real customer sometimes mis-declares their own property at signup) and the
  company visibly reacts to its own imperfect discovery — not to the silently-corrected ground
  truth — closing the loop the epistemic wall exists to enforce.

**C1_segment_layers / C3_satisfaction_heterogeneity (both AT TARGET — what "harden" means here):**
continued fidelity auditing against fresh real-world anchors as they're published (e.g. each new
Ofgem Energy Consumer Satisfaction Survey wave), and — for C1 specifically — staying alert to
whether its segment fields silently drift out of sync with `C2`'s discovery layer once that lands
(a segment field sourced from ground truth today must migrate to the discovered view alongside
everything else `company/portal/app.py` reads).

## Named best-practice references

- **Ofgem's own domestic/non-domestic customer classification** — a domestic customer is "an
  individual within Domestic Premises... for non-commercial purposes"; non-domestic customers
  (including SMEs, who lack the negotiating leverage of larger businesses and the cap protection
  domestic customers get) are regulated separately.
  [Ofgem: Non-domestic energy supply](https://www.ofgem.gov.uk/energy-regulation/domestic-and-non-domestic/non-domestic-energy-supply),
  [Ofgem: Classification of premises decision letter](https://www.ofgem.gov.uk/sites/default/files/docs/2012/03/class_of_premises_decision_letter.pdf) —
  directly grounds `C1_segment_layers`'s home/business type field in a real regulatory
  distinction, not an invented one.
- **MPAS / ECOES (Meter Point Administration Service / Electricity Enquiry Service)** — the real
  UK mechanism by which a supplier or authorised party looks up meter/property technical data
  (address, meter details, energisation status, appointed parties) via a national register keyed
  on the MPAN, rather than having private ground-truth access to the property itself. This is the
  single best real-world architectural analogue for what `C2`'s L2 observable-interface layer
  should look like: a queryable service over industry-held records, not a direct property read.
  [UK Power Networks: Who is my electricity supplier and what's my MPAN?](https://www.ukpowernetworks.co.uk/who-is-my-electricity-supplier-and-what-is-my-mpan),
  [Wikipedia: Meter Point Administration Number](https://en.wikipedia.org/wiki/Meter_Point_Administration_Number).
- **Ofgem/Citizens Advice Energy Consumer Satisfaction Survey, Wave 20 (January 2025)** —
  confirmed real (this project's existing anchor, independently re-verified live): run by BMG
  Research for Ofgem and Citizens Advice, 3,854 domestic bill-payers surveyed 6-30 January 2025;
  overall satisfaction 81% (record high), dissatisfaction 6% (record low), customer-service
  satisfaction 71%→74%, billing-accuracy satisfaction 80%.
  [Ofgem: Energy Consumer Satisfaction Survey, January 2025](https://www.ofgem.gov.uk/research/energy-consumer-satisfaction-survey-january-2025).

## Lane roadmap

1. **DONE (prior phases):** `C1_segment_layers` and `C3_satisfaction_heterogeneity` both built
   and hardened to target — real CRM-style segment fields (`tools/generate_customer_sample.py`,
   `saas/customers.py`) and real satisfaction-distribution modelling
   (`simulation/sim_satisfaction.py`) anchored to Ofgem/Citizens Advice survey data.
2. **DISCOVER/FRAME this phase (this charter):** the C2 gap formally registered and framed, with
   a real external architectural reference (MPAS/ECOES) to build against. No code touched.
3. **Next (not this phase):** design and build the observable-interface discovery layer itself —
   sequencing (which call site migrates first: `company/portal/app.py` vs the two churn-model
   consumers) is an Epoch-2 question, most naturally sequenced alongside `W1_reveal_over_time`'s
   own point-in-time discipline (both are "stop reading ground truth directly" fixes, just for
   different data classes) — full campaign sequencing arrives via the advisor's epoch framing,
   per the director's standing instruction on this exact class of work this session. Not started
   here.
4. **L4:** the SIM-side discovery-error injection capability (a self-declared property type that
   can genuinely be wrong) — depends on L2/L3 landing first.

## Simplifications register

- `tools/epistemic_verifier.py` does not check `saas.*` imports today — only `sim.*`/
  `simulation.*` — meaning the C2 gap is a real, live, currently-undetected violation class, not
  a hypothetical one. Registered here explicitly rather than left as an implicit assumption that
  "the verifier would have caught it."
- C2's real_world_twin frames discovery as "meter install/survey/customer disclosure" — this
  charter cites MPAS/ECOES as the closest real analogue found, but did not verify whether EPC
  register lookups specifically are a live part of any real supplier's onboarding flow (the
  search for this returned MPAS/ECOES results but no direct EPC-discovery-process source) —
  registered as an open citation gap, not glossed over.
- No population-level treatment here of `W2_2_population_draw` (lane W2's own atom) even though
  it shares the "stop reading a fixed ground-truth list" shape with C2 — that atom belongs to
  W2's own charter, cross-referenced but not duplicated.
