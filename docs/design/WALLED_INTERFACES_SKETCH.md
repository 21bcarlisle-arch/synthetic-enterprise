# WALLED_INTERFACES — one-page decomposition sketch

Desk-work sketch per `docs/staging/BACKGROUND_LANE_AND_WALL.md` Part C
(director-registered, not started — awaiting P-5 re-rank). Strategic framing
from that directive: **the wall IS the go-live seam** — full enforcement of
Architectural Law #2 (the company cannot see inside the SIM) means every
SIM/company crossing becomes a typed, versioned message through a
real-protocol-shaped adapter, so going live is swapping sim adapters for real
endpoints behind unchanged interfaces, not a rewrite.

## Current state

`company/interfaces/sim_interface.py` already exposes observables only
(no internals) — the epistemic *rule* is enforced (see
`tools/epistemic_verifier`). What's NOT yet true: most crossings are direct
Python function calls / plain dicts, not typed messages shaped like a real
industry protocol. `interface-steward` is the existing role guarding this
seam; WALLED_INTERFACES is a scope *expansion* of what that seam covers, not
a new mechanism.

## Candidate typed flows (draft, not final)

| Flow | Real-world analogue | Current shape | Target shape |
|---|---|---|---|
| Settlement/meter reads reaching billing | D0010 (actual read) / D0086-class flows | Direct dict from `simulation/meter_reads.py` into `run_phase4c_on_phase2b.py` | Versioned `MeterReadMessage {read_id, mpan, value, status, timestamp, schema_version}` |
| Smart-meter comms/DCC-style service requests | DCC Service Request/Response | Implicit (penetration curve lookup) | `SmartMeterServiceRequest/Response` pair, even if synchronous today |
| Customer contact in/out | Contact-centre message bus (omnichannel) | `simulation/contact_centre.py` return dict | `CustomerMessage {channel, direction, customer_id, correlation_id}` |
| Credit-bureau check | Real bureau API (Experian/Equifax-shaped) | `tools/credit_bureau_port.py` (already a Protocol/port — closest existing example of the target shape) | Extend the same adapter pattern to the other three flows |
| Acquisition funnel stage transitions | Supplier switch process (industry Switching Programme messages) | In-process function returns | `FunnelStageEvent` (already a dataclass, Phase 3) → versioned message wrapper |

## Sequencing (director's proposed placement: after core-fidelity block, before RY and scale-up)

1. **Adapter pattern audit** — catalogue every current SIM/company crossing (grep `company/interfaces/`, every direct `simulation.*` import from `company/**`/`saas/**` the epistemic verifier already tracks) and classify: already-typed (e.g. `credit_bureau_port.py`) vs plain-call (the majority).
2. **One reference flow, end to end** — pick ONE flow (meter reads, since Phase 3 already produces `meter_read_log` as structured dicts — smallest conversion delta) and build the versioned-message adapter, including a schema-version field and a real-endpoint-shaped interface the same adapter could target unchanged.
3. **Generalize the pattern** — apply to the remaining flows in the table above, one at a time, each independently testable/revertable (two-way-door: this is explicitly reversible, no data-model rewrite).
4. **Retire the informal `sim_interface.py` observable-only contract** into the typed-message layer, or keep both (observable-only stays the epistemic *rule*; typed-message is the *transport* it rides on).

## What this is NOT

Not a data-model rewrite, not a scale change, not a new epistemic rule (the
rule — company sees observables only — already holds; this only changes
*how* an observable crosses the wire). Given CLAUDE.md's Tier 1 list flags
"SIM/company boundary changes" as a one-way-door category, the *first*
reference-flow conversion (step 2) should be classified Tier 3 (novel,
opt-out window) even though this sketch itself is pre-registered — the
sketch is desk work, the actual first code change is not pre-approved by
this document alone.

## Estimated scope

Each flow conversion: small (1-2 files, a dataclass/schema + adapter,
existing call sites updated to construct/consume the message instead of a
raw dict) — this is a shape change to already-correct data, not new
business logic. Total programme: 5 flows × small = a multi-phase but not
multi-week effort once ranked.
