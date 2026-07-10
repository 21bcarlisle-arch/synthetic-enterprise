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

**Audit refresh, 2026-07-10 (Maturity Map W4_1_typed_adapters self-refill draw,
FRAME-stage work per the map's own Hardening Loop):** re-verified this sketch's
own table against current code -- all 5 rows still accurate (`generate_meter_
read_log`, `simulate_contact`/`generate_contact_centre_log`, `FunnelStageEvent`
all unchanged since 2026-07-08). Found a SIXTH already-typed example this
sketch's table omitted: `tools/market_data_port.py::MarketDataPort` (a
`runtime_checkable` Protocol, predates `credit_bureau_port.py` per its own
docstring, "Phase PV") -- and its shape is directly relevant to the separate
W1_reveal_over_time DISCOVER finding (`docs/design/MARGIN_REALISM_W1_
DISCOVER_FINDING.md`): every method takes an explicit `as_of: Optional[date]`
parameter, matching the "self-contained, safe at the source" point-in-time
pattern that finding recommended generalising, NOT the caller-trusted
anti-pattern found in `estimate_price_volatility()`. `MarketDataPort` is
therefore the codebase's most mature existing example of BOTH target
properties at once (typed adapter shape AND point-in-time-safe by
construction) -- the natural reference implementation if/when the W1 finding's
structural snapshot-object recommendation is ever built, rather than a
separate design from scratch.

## Candidate typed flows (draft, not final)

| Flow | Real-world analogue | Current shape | Target shape |
|---|---|---|---|
| Settlement/meter reads reaching billing | D0010 (actual read) / D0086-class flows | Direct dict from `simulation/meter_reads.py` into `run_phase4c_on_phase2b.py` | Versioned `MeterReadMessage {read_id, mpan, value, status, timestamp, schema_version}` |
| Smart-meter comms/DCC-style service requests | DCC Service Request/Response | Implicit (penetration curve lookup) | `SmartMeterServiceRequest/Response` pair, even if synchronous today |
| Customer contact in/out | Contact-centre message bus (omnichannel) | `simulation/contact_centre.py` return dict | `CustomerMessage {channel, direction, customer_id, correlation_id}` |
| Credit-bureau check | Real bureau API (Experian/Equifax-shaped) | `tools/credit_bureau_port.py` (already a Protocol/port — closest existing example of the target shape) | Extend the same adapter pattern to the other three flows |
| Acquisition funnel stage transitions | Supplier switch process (industry Switching Programme messages) | In-process function returns | `FunnelStageEvent` (already a dataclass, Phase 3) → versioned message wrapper |
| Market/forward price reads | Real market-data vendor feed (Bloomberg/ICIS-shaped) | `tools/market_data_port.py::MarketDataPort` (already a `runtime_checkable` Protocol, predates `credit_bureau_port.py`, "Phase PV") — the MOST mature existing example: typed adapter shape AND every method takes an explicit `as_of` date, point-in-time-safe by construction (see the separate W1_reveal_over_time DISCOVER finding) | Already at target shape — reference implementation for the other rows, not a gap |

## Sequencing (director's proposed placement: after core-fidelity block, before RY and scale-up)

1. **Adapter pattern audit** — catalogue every current SIM/company crossing (grep `company/interfaces/`, every direct `simulation.*` import from `company/**`/`saas/**` the epistemic verifier already tracks) and classify: already-typed (e.g. `credit_bureau_port.py`) vs plain-call (the majority).
2. **One reference flow, end to end** — pick ONE flow (meter reads, since Phase 3 already produces `meter_read_log` as structured dicts — smallest conversion delta) and build the versioned-message adapter, including a schema-version field and a real-endpoint-shaped interface the same adapter could target unchanged.
3. **Generalize the pattern** — apply to the remaining flows in the table above, one at a time, each independently testable/revertable (two-way-door: this is explicitly reversible, no data-model rewrite).
4. **Retire the informal `sim_interface.py` observable-only contract** into the typed-message layer, or keep both (observable-only stays the epistemic *rule*; typed-message is the *transport* it rides on).

## What this is NOT

Not a data-model rewrite, not a scale change, not a new epistemic rule (the
rule — company sees observables only — already holds; this only changes
*how* an observable crosses the wire). CLAUDE.md's Tier 1 category (a) is
narrower than "any SIM/company boundary mention" (2026-07-10 narrowing): it
is reserved for changes to the epistemic law itself — data-flow/timing that
could leak future information, not the mechanical shape of an already-correct
crossing. This sketch's own reasoning holds: the *first* reference-flow
conversion (step 2) is Tier 3 (novel, reversible) under the current
recalibrated model (2026-07-10: no opt-out wait — record the reasoning,
choose the reversible path, flag it, and proceed) — even though this sketch
itself is pre-registered, the actual first code change is not pre-approved
by this document alone, so it should still be flagged on its own turn, just
not blocked on a timer.

## Estimated scope

Each flow conversion: small (1-2 files, a dataclass/schema + adapter,
existing call sites updated to construct/consume the message instead of a
raw dict) — this is a shape change to already-correct data, not new
business logic. Total programme: 5 flows × small = a multi-phase but not
multi-week effort once ranked.
