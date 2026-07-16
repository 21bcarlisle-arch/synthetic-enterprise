# C5_key_moment_conversion — FRAME (canonical per-atom, doc-only)

**Atom:** `C5_key_moment_conversion` · lane `C_customer_ops` · epoch **4** (Epoch-4-gated —
"for Epoch 4, do not start" per `ADOPTION_JOURNEY_REGISTER.md`) · `level_current: 0` →
`level_target: 2` · `loop_stage: idle` · dial 1 · `depends_on: [C4_adoption_physics,
W1_reveal_over_time]`.

**Turn:** H17 Lane-3 FRAME (doc-only, no BUILD code — EPOCH_GATING Rule 1; no map edit — F1,
level reported via `docs/design/atom_status/C5_key_moment_conversion.yaml`).

---

## Why this doc exists (and why it is NOT churn)

C5 had accumulated three real DISCOVER-stage findings as `simplifications` entries on the
map atom itself (registration, shared-substrate note, precise per-moment source mapping —
2026-07-11/12/13) but **no canonical per-atom FRAME terminus** — no file under `docs/design/`
with `FRAME` in its filename that the intrinsic saturation guard
(`background/supervisor.py::_atom_has_frame_doc`) recognises as C5's own. The only doc
carrying C5's scope, `ADOPTION_JOURNEY_REGISTER.md`, is a **shared** registration doc for the
whole adoption-journey cluster (C4 + C5 + the loyalty/incentive billing strand) — correctly
read as un-saturating, because it is not this atom's own FRAME. This is why the idle draw
kept correctly re-offering C5.

This doc **consolidates** (does not re-derive) the register's key-moment list and C5's own
prior DISCOVER findings — most importantly the 2026-07-13 finding that of the six named
moments, only three ride the shared `W2_5_life_event_stream` substrate, and the other three
are separate real mechanisms already in the codebase — into one FRAME with a single stated
BUILD-unblock gate. Writing this makes `_is_frame_saturated(C5)` return `True` on the next
cycle (computed from disk, MAKE_IT_STICK — no marker to remember). The honest end state:
C5's FRAME work is complete once consolidated; the only remaining path to `level_target` is
BUILT, coupled, epoch-gated code. Re-emitting FRAME content beyond this point is the churn
SELF_INTERRUPT_DISCIPLINE + R12 forbid.

A sibling Lane-3 fork is concurrently authoring `C4_adoption_physics`'s own FRAME in the same
session. This doc references C4 **conceptually** (the bother-threshold/friction-sensitivity/
trust/reward-responsiveness trait vector C4 owns) and cites the shared
`ADOPTION_JOURNEY_REGISTER.md`, never C4's own FRAME file, so the two forks do not race on
each other's output.

---

## 1. The six key moments as conversion windows

Per `ADOPTION_JOURNEY_REGISTER.md` scope + C5's own 2026-07-13 DISCOVER correction (checked
directly against real code, not assumed):

| Key moment | Latent life-event (SIM-internal) | Company-observable SIGNAL | Real source in this repo |
|---|---|---|---|
| EV purchase | `ev_acquired` event, `simulation/life_events.py` | Step-change in metered consumption profile (new evening/overnight peak); customer discloses at contact | `W2_5_life_event_stream` (real, generated) |
| House move | none — genuinely unmodeled today | Change-of-tenancy notification; new-connection/MPAN re-registration; customer self-declares moving-in date | **Gap**: no event exists yet; BUILD must author a new event, not reuse one |
| Boiler failure | `boiler_replaced` (a replacement, not necessarily triggered by a *failure* specifically) | Sudden gas-consumption discontinuity; customer contact citing a breakdown; near-term switch to heat-pump enquiry | `W2_5_life_event_stream` (real, generated — imperfect semantic match, named simplification) |
| Smart-meter install | `smart_meter_installed` type exists in the `EventType` literal | A meter-technology-change record reaching the company via the meter-install job itself | **Defined but never emitted** by the generator loop (`life_events.py` docstring, W1_reveal_over_time's own 2026-07-13 Expert Hour finding) — consumed-but-not-produced gap C5 would inherit |
| Bill shock | large actual-vs-expected bill delta | The bill itself + any resulting inbound contact/complaint | `simulation/bill_shock_tracker.py` (real, separate, already-existing mechanism) |
| Renewal | contract-end date reached | Renewal notice sent/received; tariff-comparison contact; retention-offer response | `simulation/renewals.py` (real, separate, already-existing mechanism) |

**Consolidated correction carried forward from the map's own 2026-07-13 note:** "consume
`W2_5`, do not spin up a parallel event stream" is correct only for the adoption-type moments
(EV/boiler/solar/insulation); a full C5 BUILD needs **three separate real sources**
(`W2_5_life_event_stream` for EV/boiler, `bill_shock_tracker.py` for bill shock,
`renewals.py` for renewal), must **fix** the smart-meter-install emission gap, and must
**author a genuinely new** house-move event (none exists). This FRAME does not re-derive that
finding; it restates it as the terminus so it is not lost between map-simplification prose
and this doc.

## 2. The mechanism — a key moment as a transient conversion window

A key moment does not itself decide adoption. It **transiently modulates C4's hidden trait
vector** for the affected customer:

- **Bother-threshold** (C4) is *temporarily lowered* — the customer is already dealing with
  change (new EV, new boiler, new address, a shocking bill, a renewal decision), so the
  marginal cognitive cost of also considering a ToU tariff/DER offer is lower than in steady
  state.
- **Reward-responsiveness** (C4) is *temporarily raised* — a customer mid-purchase (EV,
  boiler) is already comparison-shopping and price-sensitive; a renewal is a structurally
  forced comparison moment.
- The effect **decays over a bounded window** after the triggering signal — this is a
  *conversion window*, not a permanent trait shift. The width and decay shape of that window
  is real BUILD-time parameter work (no numeric value asserted here, per R10 — C4's own
  DISCOVER pass found shape anchors, not point-in-time parameters).

Net effect: `P(convert | key moment, t)` spikes at the signal and decays back toward the
customer's steady-state C4-driven baseline — the company's targeting problem is exactly
**when** to act (inside the window) and the SIM's honesty constraint is that most customers'
baseline flexibility value sits *below* their bother threshold even during a window (the
window narrows the gap, it does not universally clear it — Law A: no tuning adoption rate
toward a target).

## 3. The epistemic wall

| Company CAN observe (through the wall) | Company CANNOT observe (SIM-internal) |
|---|---|
| A consumption-profile discontinuity (new peak shape, sudden drop/rise) | The latent event itself (`ev_acquired`, `boiler_replaced`, job-loss-adjacent life events) |
| A meter-technology-change record from the install job | The scheduling/queue internals of the install process |
| The bill itself and any resulting inbound contact | The SIM's bill-shock-tracker computation of "how shocking" a bill truly is against a counterfactual |
| A renewal-window date and the customer's actual response to a renewal offer | The customer's true churn-propensity distribution behind that response |
| A customer's own self-declaration (at contact, at signup) that they have moved / bought an EV / had a boiler replaced | Ground truth confirming that declaration is accurate (a real customer can mis-declare, matching `C2_discovery_through_interfaces`'s own discovery-error framing) |
| C4's population-level bother-threshold/reward-responsiveness **distributions** (baseline fidelity, not per-customer) | Any individual customer's own hidden threshold/responsiveness value |

The company's job is **detecting/inferring** that a key moment has occurred from the signal
column, never reading the event column directly — this is the atom's own registered
non-negotiable and matches `C7_life_event_detection`'s coupled-triad framing (§5 below) for
the affordability-side siblings of the same life-event substrate.

## 4. RNG substream discipline (C-S2)

`simulation/life_events.py` already implements the required discipline: each event type
(`ev_acquired`, `boiler_replaced`, `job_loss`, `illness`, `divorce`, …) draws from its **own
named, deterministically-seeded substream** (`_substream(base_seed, name)` /
`_LIFE_EVENT_SUBSTREAMS`), the structural fix for the real 01:09Z incident where adding
illness/divorce draws to a single shared econ RNG shifted every downstream (job_loss/
new_baby/retirement) draw. Any new key-moment machinery C5's BUILD adds must honour the same
discipline:

- The **not-yet-emitted** smart-meter-install event, once BUILD adds emission, needs its own
  named substream (`smart_meter_installed`), not a reuse of an adjacent one.
- The **new** house-move event (no existing representation) needs its own named substream
  from first authorship — it must never share a substream with any of the five events already
  in `_LIFE_EVENT_SUBSTREAMS`, by the same proof obligation the 01:09Z incident established as
  necessary and every sibling FRAME in this family (`W1_10_FRAME.md`,
  `NATIONAL_WEATHER_SIGNAL_FRAME.md`, `REGIONAL_WEATHER_FIELD_FRAME.md`) has since repeated.
- `bill_shock_tracker.py` and `renewals.py` are separate mechanisms outside `life_events.py`'s
  substream registry — BUILD must confirm (not assume) each already carries its own isolated
  RNG state before wiring C5's conversion-window logic to consume their outputs, so that
  wiring a new consumer never becomes a vector for a second 01:09Z-shaped incident.

## 5. Coupled-triad framing

C5 is the company's **response** leg of a triad whose SIM leg is the six key-moment sources
above (three inside `W2_5_life_event_stream`, three separate mechanisms) and whose gap is:
**belief `b`** = which customers/windows the company's targeting model flags as converting
key moments, computed only from the signal column of §3; **hidden truth `θ`** = the SIM's
actual per-customer key-moment occurrence and C4's actual (never company-visible) threshold/
responsiveness state at that moment. `raw_gap` = a miss-rate/harm measure over "did the
company act inside a real window, on a real signal, without leaking the latent event";
`g0` = a no-skill baseline that never targets key moments at all (uniform blind offers).
This is directly analogous to `C7_life_event_detection`'s own coupled framing in
`COUPLED_TRIAD_DESIGN.md` §"W2_5 ⇄ C7" (same substrate, different consuming atom: C7 detects
*distress*, C5 detects *conversion opportunity* — two distinct company-side reads of the one
SIM-side life-event stream, matching the "one architecture, not two" discipline the map's own
2026-07-13 note already applied when it pointed C4 at `nudge_physics.py`/`nudge_discovery.py`
as the template pairing). Neither this atom's own gap formula's exact loss function nor its
`g0` baseline is settled here — genuine BUILD-time judgement, named as open rather than
invented.

## 6. What L1/L2 mean for C5 in `C_customer_ops` terms

- **L1:** a company-side detector exists that maps at least one observable signal (§3) to a
  candidate key-moment flag per customer, using only crossed-the-wall data — proof that the
  detection mechanism runs against real signal columns, not yet integrated with any
  conversion action.
- **L2 (this atom's `level_target`):** the detector's output is wired to an actual
  conversion-window action (an offer, a targeted contact, a tariff nudge) that measurably
  differs in timing/content from the company's steady-state behaviour, and that action is
  demonstrably confined to the transient window (§2), not applied unconditionally — matching
  the atom's own registered scope ("acting within the window").
- L3/L4 (loyalty-mechanic integration, SIM-side discovery-error injection at key moments) are
  out of this atom's own `level_target` and belong to the wider adoption-journey cluster's
  later phases per `ADOPTION_JOURNEY_REGISTER.md`.

## 7. Known simplifications (R10)

- The house-move event has **zero existing representation** — this FRAME does not invent one;
  BUILD must author it as new, named work, not retrofit an adjacent event.
- `boiler_replaced` is a **replacement** event, not a semantically exact **failure** trigger —
  carried forward as a named imprecision, not corrected here.
- `smart_meter_installed` is defined but never emitted — a real, pre-existing gap this atom
  inherits rather than causes; fixing emission is BUILD-time scope, not FRAME scope.
- No numeric conversion-window width/decay shape is asserted — C4's own DISCOVER pass found
  real shape anchors (segment-varying adoption, friction sources) but no ready-to-encode
  parameter values; the same honesty applies here by extension.
- The gap formula's exact loss function and `g0` baseline (§5) are named as open, not decided.

---

## 8. The single BUILD-unblock gate (the epoch-sequencing intelligence — HELD at L0)

| Atom | Epoch | Level (held) | Single BUILD-unblock gate | Gate class |
|------|-------|---------------|---------------------------|------------|
| `C5_key_moment_conversion` | 4 | **0 (→2)** | (1) `C4_adoption_physics` reaches a built, L-usable hidden-trait state (bother-threshold/friction-sensitivity/trust/reward-responsiveness populated and observable-side lift-measurement wired, per C4's own FRAME) — C5's conversion-window mechanism (§2) has nothing to modulate until C4 exists; (2) `W1_reveal_over_time` stays met (already L3/3, idle/hardened — trivially satisfied, confirmed against the map's own dependency-met rule); (3) **Epoch-4 BUILD-open** (director/TWIN, within the open epoch, per `EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1). Then BUILD wires the three real sources (`W2_5_life_event_stream`, `bill_shock_tracker.py`, `renewals.py`), fixes the smart-meter-install emission gap, authors the new house-move event with its own RNG substream, and registers the C5 coupled pair in `background/coupled_triad.py::_AUTHORITATIVE_COUPLING`. | DIAL (depends_on + epoch sequencing) |

**Disposition:** level **HELD at 0** (`loop_stage: idle`; FRAME complete ≠ built; BUILD-gated,
EPOCH_GATING Rule 1). This FRAME is C5's canonical terminus; the next idle draw reads C5 as
frame-saturated and yields to genuinely-un-FRAMEd work instead. No BUILD code, no map edit
(F1).

---

*Sources consolidated (not re-derived): `docs/staging/done/ADOPTION_JOURNEY_REGISTER.md`
(the shared cluster registration), `docs/design/maturity_map.yaml`'s own C5 `simplifications`
entries (2026-07-11/12/13 registration, shared-substrate note, precise per-moment source
mapping), `docs/market_research/adoption_physics_c4.md` (C4's DISCOVER anchors for the
bother-threshold mechanism this atom modulates), `simulation/life_events.py` (RNG substream
pattern, 01:09Z incident precedent), `docs/design/COUPLED_TRIAD_DESIGN.md` (gap-formula
family, the paired `C7_life_event_detection` example on the same substrate). C4's own FRAME
is referenced conceptually only, per the sibling-fork non-dependency instruction — its file is
not assumed to exist.*
