# M3 FRAME: "Discovery and the draw" — C_customer_ops + W2_customer_generator

**Status:** DISCOVER complete, FRAME (this doc). BUILD not started, deliberately.

## What the framing's abstract language actually maps to in real code

Investigated before writing any code (R4 diagnosis discipline). Three
sub-components, each checked against the real code, not assumed from the
framing's prose.

### 1. "Customer belief layer via onboarding/flow events"

**Confirmed still current (re-verified live, not just cited from
EPOCH2_EVIDENCE.md Q4):** `company/portal/app.py:52` still does
`from saas.customers import CUSTOMERS` and builds `_CUSTOMER_INDEX` from it
directly (line 171-ish) — `home_type`, `bedrooms`, `epc_rating`,
`smart_meter`, `eac_kwh` are read as ground truth, not discovered.
`tools/epistemic_verifier.py`'s `FORBIDDEN_SOURCES` (lines 29-36) still only
pattern-matches `sim.`/`simulation.` imports; `saas/` is in
`COMPANY_PATHS` (scanned) but not `FORBIDDEN_SOURCES` (blocked) — a
`company/` file importing from `saas/` is invisible to the tool. Confirmed
by direct read, not inference.

**New finding this pass, not previously surfaced in EPOCH2_EVIDENCE.md — the
same "which pipeline is this actually wired to" trap M1 found for price
data exists here too, in a different shape:** a real, well-built,
event-shaped acquisition/onboarding process already exists, split across
**three separate stage-taxonomies**, only one of which is wired into
anything:

- `simulation/acquisition_funnel.py::run_acquisition_funnel()` — SIM-side,
  **wired** (`simulation/run_phase2b.py:1391`, called once per acquisition
  attempt inside the outer per-term-event loop, same event-shaped loop
  M1's FRAME already found and left alone). Real stages
  (quote→application→credit_check→onboarding→cooling_off), real calendar
  spacing between them (Phase 3 item 5, `_stage_day_offset`), a real
  statutory constant (14-day cooling-off, Consumer Contracts Regs 2013).
  Drives real cost events (`acquisition_spend_events`) and a real
  win/lose outcome. This is genuine, working infrastructure.
- `company/crm/acquisition_journey.py::AcquisitionJourney` — company-side,
  a *different* 8-stage taxonomy (`QUOTE_REQUESTED`...`ONBOARDED`).
  **Zero callers outside its own test file** (`grep` confirms only
  `tests/company/crm/test_acquisition_journey.py` imports it).
- `company/crm/onboarding_journey.py::OnboardingJourneyTracker` —
  company-side, a *third* 9-stage taxonomy, real SLC citations (14.2, 22.1,
  7.5) baked into deadline logic. **Zero callers outside its own test
  file** (same check).

This is the same class the M2 payments audit already named for a
different lane ("18/22 billing-collections modules well-built but
completely unwired — paper compliance"). Here it's narrower (2 of 3
modules) but the shape is identical: real, tested, SLC-anchored logic that
produces nothing any decision or bill ever reads. Neither unwired tracker
computes a company *belief* that can diverge from ground truth — they are
inert.

**What "belief layer" would require, once real:** today, when a customer
is acquired, the win/lose funnel outcome feeds cost accounting only — the
customer's actual attributes (`eac_kwh`, `home_type`, etc.) come from the
hardcoded `saas/customers.py::CUSTOMERS` list literal (31 entries,
confirmed by count), present in full from the moment the customer is
defined, never assembled from anything the funnel or onboarding process
revealed. There is no code path today where the company starts with a
provisional/estimated view of a new customer and corrects it later from
observed events (a meter read, a self-declaration, a bill query) — the
exact mechanism M3's exit test names ("mis-estimates a new customer's
consumption, bills wrong, discovers, rebills").

### 2. "Generation independently anchored from validation (Q5's accident made deliberate)"

`git log --grep=Q5` traces to `b115a6e8` ("[ADVISOR-STAGED] Amend evidence
pass: add Q4... Q5 (generation/validation independent anchoring —
anti-mark-own-homework)...") and `docs/design/EPOCH2_EVIDENCE.md` Q5
(lines 174-206), both read in full.

**Confirmed still current:** `saas/property_model.py`'s docstring (lines
17-22) is unchanged since Q5 was written — `OCCUPANCY_PATTERN_BY_CUSTOMER`/
`ASSET_PROFILE_BY_CUSTOMER` are still explicitly "placeholders pending...
real EPC/Census/Ofgem data," last touched at Phase 4c-1 (`git log` shows no
commits to this file since `843a23e1`). `company/compliance/
domain_invariants.py` still imports only from `company/pricing/
ofgem_price_cap.py`, independent of `saas/property_model.py`.

**"Q5's accident":** the independence between generator (`property_model.py`)
and validator (`domain_invariants.py`) that the director wants holds
*today*, but only because the generator has no real anchor to share in the
first place — there's nothing for the validator to accidentally share a
source with. EPOCH2_EVIDENCE.md's own words: "this appears incidental...
rather than a deliberate anti-mark-own-homework design."

**"Made deliberate" is a two-way-door-blocked instruction, not a
standalone task:** it cannot be actioned in isolation. The dependency
chain is: (a) `property_model.py`'s placeholders get anchored to real
EPC/Census/DESNZ data (a real backlog item, not done here, not scoped by
this FRAME) → (b) *only then* does "deliberate independence" mean
anything — a check must be added at that point confirming generator and
validator still cite different primary sources. Building the check now,
against a generator with no real anchor, would be checking independence
between "real data" and "nothing," which proves nothing.

### 3. "Population draw per run, seeded, hidden"

**Confirmed still current (re-verified live):** `saas/customers.py::
CUSTOMERS` is still a hardcoded Python list literal (31 entries today, up
from 4 at Q6's original writing — book-growth added more, but the
mechanism is unchanged: still authored, not drawn).
`simulation/run_phase2b.py:834` still has `_payment_rng =
random.Random(42 + 7919)` — one fixed seed, not varied per run. Direct
grep for `draw_population`/`generate_population`/`draw_customers`/
`population_draw` across `simulation/`, `saas/`, `company/`, `tools/`
returns **zero matches** — confirmed genuinely greenfield, matching
`maturity_map.yaml`'s own `W2_2_population_draw` (level 0/2, `evidence:
["docs/design/EPOCH2_EVIDENCE.md"]` only — no code evidence because none
exists).

**"Seeded, hidden" is two separate properties, and only one is even a
live question today:**
- *Seeded* (deterministic/reproducible per draw) — trivial once a draw
  function exists; this codebase's own standing convention
  (`random.Random(f"...{customer_id}...")`-style seeding, used throughout
  `household_segments.py`, `meter_reads.py`, `acquisition_funnel.py`)
  is a proven, working pattern to extend to population-level seeding.
- *Hidden from the company* — currently **moot, not violated**: there is
  no population-draw mechanism at all, so there is no seed anywhere for
  company-side code to read. `tools/epistemic_verifier.py`'s
  `EXEMPT_PATHS` (`tests/`, `background/`, `simulation/`, `company/
  interfaces/`, `tools/`) already establishes the pattern that would need
  to apply: a population-draw module belongs in `simulation/` (exempt,
  correct place for it), and its seed/draw parameters must never be
  imported by `company/` or `saas/` — the same `saas/*` blind-spot Q4
  found for customer ground truth is the exact failure mode a population
  seed could fall into if placed carelessly (e.g. in `saas/customers.py`
  itself, which `company/portal/app.py` already imports directly).

## Why this is not a same-day BUILD

All three sub-components genuinely depend on unresolved upstream questions
or other in-flight work — the two-way-door filter's textbook case:

1. **Belief layer** depends on M1's price-history migration pattern (just
   landed) as the nearest working analogue for "an as-of view assembled
   from observed events rather than a direct read" — but building it
   requires first deciding what "observed events" actually are for a new
   customer (self-declaration at signup? a meter-install record? first
   bill query?), which is a real design question, not yet answered
   anywhere in this codebase. Wiring the two *existing* unwired trackers
   in naively would not build a belief layer — they track *process
   stage*, not *customer attribute estimates*; neither carries an
   `eac_kwh`-shaped provisional value that could later be corrected.
2. **Generation/validation independence** is explicitly blocked on the
   `property_model.py` real-anchor backlog item landing first (Q5's own
   conclusion) — building the "stay independent" check now would check
   nothing meaningful.
3. **Population draw** is real greenfield work (zero prior art) that the
   charter (`W2_customer_generator.md`) already explicitly sequences
   behind "the epoch-2 reveal-over-time spine's sequencing" — i.e. M1's
   as-of interface pattern, which only just landed this session and
   hasn't yet been proven at scale. Building a population-draw generator
   before that pattern is proven risks building it against the wrong
   shape (same risk class M1's own FRAME named for materiality gates:
   don't build against an unresolved design question).

Additionally, unlike M1's `hedged_settlement.py` concern, **none of these
three carry ground-truth-corruption risk** — the two unwired trackers are
pure, side-effect-free dataclasses (confirmed: no I/O, no writes to
`saas/customers.py` or any settlement path), and a population-draw
generator would be strictly new/additive code, not a rewrite of the
existing fixed-cast mechanism. The blocker here is design-sequencing, not
risk-of-corrupting-history.

## What each sub-component most plausibly means, once scoped

- **Belief layer:** not "wire the two existing trackers in as-is" (they
  track process stage, not attribute belief). More plausibly: a small
  `PointInTimeView`-shaped extension (following M1's own precedent) that
  gives the company a provisional `eac_kwh`/`home_type` estimate at
  acquisition (from a real proxy signal — declared property type, EPC
  band lookup, whatever a real supplier's onboarding form actually
  captures), corrected once genuine consumption data arrives (first
  meter read / first bill cycle) — exactly mirroring the "billed vs
  settled, provisional then corrected" pattern M2 already built for the
  three-clocks work. The two existing trackers may still be useful for
  *SLC-obligation timing* (welcome pack, first bill deadlines) once wired
  — a separate, smaller, genuinely low-risk wiring task, but not the
  belief-layer itself.
- **Generation/validation independence:** a documentation/test addition
  (assert the two modules cite different primary sources), sequenced
  strictly after the `property_model.py` real-anchor backlog item, not
  before.
- **Population draw:** a new `simulation/`-side generator function
  (`draw_population(seed, n, distribution_params) -> list[customer_dict]`
  shape), built against `W2_1_archetype_layers`'s already-verified real
  DESNZ/Ofgem distributions as the target shape to match statistically,
  with the fixed `CUSTOMERS` cast retained as an explicit named baseline
  (per the charter's own L3 definition) rather than deleted.

## Recommendation

Defer BUILD on all three sub-components. Register this FRAME finding; do
not move `C1_segment_layers`, `C3_satisfaction_heterogeneity`,
`W2_1_archetype_layers`, `C2_discovery_through_interfaces`, or
`W2_2_population_draw`'s levels or loop_stages on the strength of a design
doc alone (the map's own rule: depth is earned, not claimed).

The one item that is genuinely low-risk and could be picked up
independently of the wider sequencing question, if the director wants
momentum here before the belief-layer design question is settled: wiring
`company/crm/onboarding_journey.py`'s SLC-deadline tracking (welcome
pack/first bill/smart-meter-offer deadlines) into the portal or a
compliance surface — pure additive, no epistemic-wall risk, no
ground-truth dependency, and closes a real "paper compliance" gap in its
own right, independent of whether the belief-layer or population-draw
design questions are resolved. Everything else in this FRAME should wait
for the director/advisor's M3 sequencing call, same as M1's materiality
gates waited for the M4 sequencing decision.
