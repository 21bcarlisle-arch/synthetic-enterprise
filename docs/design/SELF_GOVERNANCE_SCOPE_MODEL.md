# The Self-Governance Scope Model — Fronts and Gates

**Status:** DESIGN PROPOSAL (doc-only, director-facing). No code is written here; the build
plan in §8 is built one sub-step at a time, each gated by the director (the OPS1 discipline).
**Author:** DESIGN fork (Claude Code), 2026-07-18, in an isolated worktree.
**Mandate (director, verbatim intent):** "Design and build the self-governance scope model — so
that the loop can advance TWO permanent declared fronts (SIM ACTORS: weather/archetypes/
generative-futures; SUPPLIER: billing/pricing/settlement/site) continuously, self-governing its
draw WITHIN authorized fronts but HOLDING at declared gates (one-way doors, epoch boundaries,
schema/sim-structure decisions, anything I've reserved). Self-governing = advances open fronts
without asking; NEVER self-authorizes across a gate (that's the twin-approver failure). Fronts
and gates declared+reconciled; opening a front / clearing a gate traces to my console act. I
authorize the two fronts once the model is proven."
**Reuses (does NOT fork):** `background/gate_authorization.py` +
`docs/observability/gate_authorizations.jsonl` (the console-act ledger + pure gate-wall
predicates), `background/one_way_door.py` (the door predicate), the
`process_manifest.yaml` + `process_reconciler.py` declared-set/reconcile pattern,
`docs/design/maturity_map.yaml` (lane/epoch/loop_stage as the atom-space coordinate system).

---

## 0. The one-paragraph model

A **FRONT** is a declared, bounded region of the maturity-map atom-space that the loop may
**draw from and BUILD within continuously, without asking** — self-governing its own draw by
the existing dial-weighted, lane-balanced, ≤3-parallel rules. A **GATE** is a declared boundary
the loop may **never cross without a director console act** — the one-way-door list, epoch
boundaries, schema/sim-structure decisions, and director-reserved values decisions. The two
compose by a single rule: *a BUILD promotion is authorized iff the atom is a member of an OPEN
front AND advancing it does not cross a gate.* "Opening a front" and "clearing a gate" are the
**same console act** the gate-wall already understands — a `FRONT_OPEN` / `BUILD_OPEN` record in
`gate_authorizations.jsonl`, director-authored, console-channel, R7 provenance. The model is
therefore not a new mechanism: it **generalises the existing single-atom gate-wall from "this one
atom is authorized" to "this whole declared region is authorized, minus the gates."** Everything
is declared in the readable repo (a `fronts.yaml` manifest) and reconciled against actual draw
behaviour, exactly as `process_manifest.yaml` is reconciled against `ps`. A draw from an
undeclared region, or a promotion across a gate with no console act, is a LOUD reconciler alarm —
mutation-tested to prove it fires.

---

## 1. The model — FRONT and GATE

### 1.1 What a FRONT is

**PURPOSE.** Let the director authorize a *standing region of work* with one console act, so the
loop can advance it continuously without a per-atom nudge — the thing the mandate asks for. The
existing gate-wall already lets the director authorize work with a console act; today that act
covers **one named atom** (`BUILD_OPEN` for `W1_3_national_weather_signal`, etc. — see the 12
entries in `gate_authorizations.jsonl` from the 2026-07-18 console act). A front is the *bounded
set* version of that same act: authorize a **region**, defined by a predicate over the map, once.

**DEFINITION.** A front is a named, declared predicate over atom-space:
```
front := { id, membership_predicate, epoch_ceiling, lane_set | atom_set, purpose }
```
Membership is computed from the map's own coordinates — `lane`, `epoch`, and (where needed) an
explicit atom-id allow/deny list. An atom is **in the front** iff it matches the predicate. The
loop may draw and BUILD any in-front atom that is below target, self-governing which one by the
existing draw rules (§1.3). No atom is enumerated by the director at draw time; the *region* is
enumerated once, in the declaration.

**GUARANTEES.**
- **F-1 (bounded).** A front's membership is a total, pure function of the committed map + the
  committed `fronts.yaml` — no runtime discretion widens it. The loop cannot draw an atom into a
  front by wanting to; membership is declared, not inferred.
- **F-2 (self-governing draw, not self-authorizing scope).** Within the front the loop chooses
  *what to draw* (dials, lanes, ≤3 parallel). It never chooses *what the front contains* — that is
  a console act (§3). This is the exact line between self-sustaining (allowed) and self-promoting
  (forbidden) that the gate-wall docstring draws.
- **F-3 (gate-subtracted).** A front never contains a gate crossing. Membership is
  `in_region AND NOT crosses_gate` (§1.2). An atom inside the front's region but whose promotion
  would cross a gate is **held at the gate**, not drawn — even though it is "in the front."

**WHY.** Without fronts, the director must issue a console `BUILD_OPEN` per atom forever (the
2026-07-18 act opened 12 atoms by name — it does not scale, and a 13th atom in the same obvious
region silently has no authorization). With fronts, the director authorizes *the region* once; a
new atom that lands inside a declared, open region is authorized by construction, while a new atom
outside every open region is LOUD. The director's attention — the scarce resource (MAKE_IT_STICK)
— is spent on *regions and gates*, not on *atoms*.

### 1.2 What a GATE is

**PURPOSE.** A gate is a boundary where the asymmetry flips: crossing it is either irreversible or
reserved to the director's judgement, so the loop must HOLD and escalate (NTFY, never the window)
rather than proceed. A gate is the thing a front may never dissolve.

**DEFINITION.** A gate is a declared predicate over a *proposed promotion* (atom + the level/epoch
it would advance to). The four gate classes the mandate names, each already having a home:
1. **One-way doors** — `background/one_way_door.py`'s eight categories (real money, real-world
   commitment, irretractable public claim, irrecoverable data loss, security/safety-control,
   values decision, real customer/market, platform administration). A promotion whose *action*
   matches a door is gated. **Reused verbatim** — the door predicate is already CODE, not
   judgement.
2. **Epoch boundaries** — advancing an atom into an epoch **higher than the front's declared
   `epoch_ceiling`**. Epoch 4 (fitness function / tournament / mortality) and epoch 5 (go-live
   NFRs) are values/go-live territory; opening an epoch is itself one_way_door VALUES_DECISION
   (`open(ing)? epoch \d`). The front carries a ceiling; crossing it is a gate.
3. **Schema / sim-structure decisions** — changes to the structural seams the whole system rests
   on: the SIM/company wall contract (`W4_the_wall`, `company/interfaces/sim_interface.py`), the
   event-log/spine schema (`G2_event_log_shared_with_spine`), the maturity-map schema itself, and
   any new SIM/company boundary *type*. Declared as a **gated atom-set + a gated-path list** in
   `fronts.yaml` (§2). Rationale: a schema decision is a one-way-ish door (downstream code binds to
   it) and is a design-ownership call, not a build-forward call.
4. **Director-reserved values decisions** — the atoms that DEFINE what the company is FOR: the
   Epoch-4 fitness function, mortality rule, harm-cost weights (`A5`, `A7`), the sim-approver
   values (`A4`), and the **curriculum** (R13 — which worlds the company lives through). Reserved
   regardless of reversibility (matches `one_way_door.VALUES_DECISION`).

**GUARANTEES.**
- **G-1 (gate beats front, always).** The composition rule is `authorized = in_open_front AND NOT
  gated`. There is no front value that can set `gated → False`. A front is a *subtraction from the
  whole map*, and gates are *subtracted back out* — the order is fixed in code, not configurable.
- **G-2 (a gate is crossed only by a console act).** The ONLY thing that lets a gated promotion
  proceed is a director-console record clearing that specific gate (`BUILD_OPEN` for the atom, or
  a `GATE_CLEAR` record naming the gate) — the same authorization object the gate-wall already
  validates (`_is_valid_authorization`: action + `authorized_by==director` + `channel==console` +
  non-empty provenance).
- **G-3 (holding at a gate is not idling).** Per Rule 0, holding at a wall while idle-capable lanes
  have work is itself a violation. A gate hold on atom X **must** be accompanied by the loop
  continuing to draw non-gated in-front atoms, and an NTFY escalation of the specific gate (what
  it is, what console act clears it) — never a window-ask, never a stall.

**WHY.** The mandate's failure to prevent is the twin-approver failure: a machine self-authorizing
across a gate. Gates make that impossible-or-loud (§5). The four classes are exactly the director's
enumerated reservations; each maps to an existing predicate so there is no new judgement surface to
decay (MAKE_IT_STICK: mechanism, not exhortation).

### 1.3 How the loop self-governs its DRAW within a front

Unchanged from today — the front is a **filter applied before the existing draw**, not a new draw
engine. `background/supervisor.py`'s draw already is:
- **Dial-weighted** — the equaliser dials in the map bias which lane/atom is drawn.
- **Lane-balanced, three lanes** — L1 BUILD (`_maturity_map_draw_concurrent`, loop_stage=build,
  below target, disjoint file_scope), L2 SITE (`_site_lane_draw_concurrent`, `site/**`), L3
  DISCOVERY (`_idle_discover_frame_draw_concurrent`, idle atoms, doc-only).
- **Bounded ≤3 parallel** — `MAX_CONCURRENT_FORKS = 3`, a hard combined ceiling (director P0).

**The only change:** the BUILD candidate set is intersected with the union of OPEN fronts, minus
gates. Concretely, `_maturity_map_draw_concurrent` gains one filter: an atom is a BUILD candidate
iff `authorized_build(atom)` (§4.2) is true. DISCOVER/FRAME/SITE are unaffected — they are already
allowed on parked/idle atoms regardless (epoch-gating gates BUILD, never thought; SITE is an
ungated parallel lane). So:
- **In an open front, below target, non-gated →** drawn and built, self-governed, no ask.
- **In an open front but gate-crossing →** held at the gate, NTFY escalation, loop keeps drawing
  the rest of the front.
- **Not in any open front →** not a BUILD candidate; if the loop somehow promotes it (a bug, a
  rogue turn), the reconciler alarms (§2, §5). DISCOVER/FRAME on it is still fine.

---

## 2. Declared + reconciled, as IaC

**PURPOSE.** Everything behaviour-determining lives in the readable repo (OPS1 §5). A front the
loop draws from must be declared; a gate crossing must trace to a recorded console act. Neither
may live only in the running machine's head.

### 2.1 The declaration — `background/fronts.yaml`

Proposed new committed manifest, modelled field-for-field on `process_manifest.yaml` (same
loader-enforced `reason`, same "declaration in git / runtime state not in git" split). Schema:

```yaml
# background/fronts.yaml — the SINGLE authoritative declaration of self-governance scope.
# Fronts = regions the loop may BUILD within without asking. Gates = boundaries only a director
# console act crosses. Reconciled against actual draw/promotion behaviour by fronts_reconciler.py;
# it has NO write path to the map by construction (detect + report only, like process_reconciler).
version: 1

# ── FRONTS ────────────────────────────────────────────────────────────────────
# state: open  — the loop may BUILD in-region non-gated atoms without asking.
#        held  — declared but NOT authorized; in-region atoms are BUILD-frozen (DISCOVER/FRAME ok).
#        (a front is 'held' until a director FRONT_OPEN console act flips it 'open' — §3.)
# Every field is behaviour-determining. `opened_by` MUST reference the ledger console act that
# opened it (loader-enforced when state==open) — a front without its console trace is drift.
fronts:
  - id: SIM_ACTORS
    state: held            # → open only via a director FRONT_OPEN in gate_authorizations.jsonl
    lanes: [W1_market_weather, W2_customer_generator]
    include_atoms: [W1_2_generate_futures]     # generative-futures, explicit
    epoch_ceiling: 3       # advancing a member INTO epoch >=4 is an epoch gate (HOLD)
    purpose: "SIM-side actors the world runs on: weather physics/fields/demand/price signal,
              customer archetypes/population/life-events/distress, generative futures. The world
              deepens continuously; the company discovers it through the wall (coupled triad)."
    opened_by: null        # set to the ledger act id/ts when opened

  - id: SUPPLIER
    state: held
    lanes: [D_billing_metering, B_commercial, E_finance_treasury]
    include_paths: [site/]          # the website surface (L2 SITE lane)
    epoch_ceiling: 3
    purpose: "Supplier operations: billing/rebilling, pricing/margin/hedge-tariff, settlement/
              ledger/revenue-recon, and the public site. The company's own machine, built forward."
    opened_by: null

# ── GATES ─────────────────────────────────────────────────────────────────────
# A gate is subtracted from EVERY front (G-1). Order in code is fixed: in_region AND NOT gated.
gates:
  - id: one_way_doors
    kind: predicate
    predicate: one_way_door.classify_action     # reuse verbatim — the 8 categories
    purpose: "The director's one-way-door list. Any promotion whose action matches → HOLD."

  - id: epoch_boundary
    kind: epoch_ceiling
    purpose: "Advancing a front member into an epoch above the front's epoch_ceiling. Epoch 4
              (fitness/mortality) and 5 (go-live) are values/go-live — director-opened only."

  - id: schema_sim_structure
    kind: gated_atoms_and_paths
    gated_atoms: [W4_1_typed_adapters, W4_2_verifier_timing_extension, W4_3_external_truth_wall,
                  G2_event_log_shared_with_spine, H9_map_write_serialisation]
    gated_paths: [company/interfaces/sim_interface.py, docs/design/maturity_map.yaml,
                  interface/, background/gate_authorization.py, background/fronts.yaml]
    purpose: "Structural seams the whole system binds to — the wall contract, the event-log/spine
              schema, the map schema itself, and this governance mechanism. A build TOUCHING a
              gated path, or PROMOTING a gated atom, is a schema decision → HOLD."

  - id: values_decisions
    kind: gated_atoms
    gated_atoms: [A4_sim_approver, A5_tournament_fitness_mortality, A7_harm_cost_weights_decision]
    also: "the curriculum (R13) — any named difficulty/scenario change — is director-authored."
    purpose: "Atoms that define what the company is FOR. Reserved regardless of reversibility."
```

**Why these two lanes-sets and not others** — scoping detail and the open decisions are §4.

### 2.2 The reconcile — `background/fronts_reconciler.py`

Proposed new module, modelled on `process_reconciler.py` (pure classify + report, **no write path
to the map** — the reaping-by-inference lesson: a reconciler detects and reports, it never
"fixes"). It reconciles the **declaration** (`fronts.yaml` + the ledger) against **actual draw and
promotion behaviour** (the map's `loop_stage` deltas vs `gate_wall_baseline.json`, and the draw
log). Per-atom status, alarm states first:

| status | condition | alarm |
|---|---|---|
| `ON_FRONT` | promoted atom is in an OPEN front, non-gated, console-covered | no |
| `DRAW_OFF_FRONT` | loop drew/promoted an atom in **no** open front, no `BUILD_OPEN` | **YES** |
| `GATE_CROSSED` | promoted atom crosses a gate with **no** clearing console act | **YES** |
| `FRONT_HELD` | atom in a *held* (declared-not-open) front, correctly BUILD-frozen | no |
| `GATE_HELD` | atom at a gate, correctly held, NTFY escalation present | no |

`DRAW_OFF_FRONT` is the "drift alarm" the mandate asks for (a front the loop draws from that isn't
declared). `GATE_CROSSED` is the "violation alarm" (a gate crossing without a console-act record).
Both are **transition-only, typed real-alarms** (R5, OPS1 G-N1/G-N2), NTFY not window.

**GUARANTEE (reconcile-vs-actual, not vs-intent).** The reconciler reads the *actual* map state
(`current_loop_stages`) and the *actual* ledger — never a declared-intent the loop could have
written to match. Independence (R15 anti-tautology): the thing checked (map promotions) and the
authority it is checked against (the console ledger) have **different writers** — the map is
written by the loop; the ledger's valid entries are written only by the console orchestrator on a
director act. A loop that promotes an atom cannot also mint the ledger entry that authorizes it
(that is the prevention layer, §5) — and if it forges one, the forged entry self-declares a
`channel` the reconciler can cross-check against the console/HMAC trace.

**WHY IaC.** "Is the loop allowed to be building weather physics right now?" must be answerable
from the repo alone (`fronts.yaml` says SIM_ACTORS is open, opened_by that ledger act; the atom is
epoch-3 ≤ ceiling; no gate matches) — not from watching what the loop happens to do. Reconstruct-
from-repo is the OPS1 test; a front's authorization is repo state, not machine state.

---

## 3. The console-act trace — reusing the gate-wall ledger

**PURPOSE.** Opening a front and clearing a gate must trace to a director console act, recorded
append-only with R7 provenance. This mechanism **already exists** — `gate_authorization.py` +
`gate_authorizations.jsonl`. The model **adds record types to it**, it does not build a parallel
ledger (the mandate is explicit: do NOT invent a parallel mechanism).

### 3.1 What is reused verbatim
- `_is_valid_authorization(entry)` — the console-validity predicate: `action`, `authorized_by ==
  director`, `channel == console`, non-empty `provenance`. **Every new record type validates
  through the same four checks.**
- `record_gate_opening()` / `_append_ledger()` — the console-path-only writer (docstring:
  "the autonomous worker must never call this"). New record types append through the same writer.
- The baseline-promotion predicate (`promotions_since_baseline`, `unauthorized_promotions`) — the
  pure, mutation-testable core. The generalisation (§4) **wraps** it, does not replace it.
- The `BUILD_OPEN` (per-atom authorization) and `HELD_PENDING_VERIFICATION` (director-acknowledged
  red) records — kept; a per-atom console act still works for one-off gate clears.

### 3.2 What is added (two new record types, same schema + validity)
```jsonc
// FRONT_OPEN — opens a declared front. Authorizes continuous BUILD of every in-region,
// non-gated atom, present and future, until a FRONT_CLOSE. The scaling win: ONE act, a region.
{ "front": "SIM_ACTORS", "action": "FRONT_OPEN", "ts": …,
  "authorized_by": "director", "channel": "console",
  "provenance": "director console message 2026-07-… authorizing the SIM_ACTORS front …" }

// GATE_CLEAR — clears one specific gate for one specific atom (an in-front atom that hit a gate
// the director decides to wave through). Narrower than opening a front; a per-crossing act.
{ "atom": "W1_8_zonal_locational_pricing", "gate": "epoch_boundary", "action": "GATE_CLEAR",
  "authorized_by": "director", "channel": "console", "provenance": "…" }
```
`FRONT_CLOSE` (symmetry, R11 "no orphan transitions": every open must have a defined close whose
effect is tested — closing a front re-freezes its region to DISCOVER/FRAME).

### 3.3 The precedent this generalises (already in the ledger)
The 2026-07-18 console act (12 `BUILD_OPEN` entries) **is a front, spelled out atom-by-atom**: the
director opened "the real backlog atoms in in_progress/ as an OPEN FRONT — the loop draws and
builds them continuously in bounded parallel (≤3)" and excluded `REPO_PRIVATE` (a one-way door).
That is *exactly* this model, done manually. Today a 13th backlog atom has no authorization; under
this model, `FRONT_OPEN SIM_ACTORS` / `FRONT_OPEN SUPPLIER` covers the region and the reconciler
tells the director when the loop draws outside it. The model is the mechanised form of what the
director already did by hand.

---

## 4. The two declared fronts, precisely scoped, and the gates enumerated

### 4.1 SIM_ACTORS — weather / archetypes / generative-futures
The world-side actors the simulation runs on. Members (from `maturity_map.yaml`, verified):
- **`W1_market_weather` (10 atoms)** — `W1_2_generate_futures` (generative futures),
  `W1_3_national_weather_signal`, `W1_4_regional_weather_field`, `W1_5_premise_demand_shape`,
  `W1_6_physics_price_signal`, `W1_7_renewable_capacity_trends`, `W1_8_zonal_locational_pricing`,
  `W1_9_dsr_flex_markets`, `W1_10_ev_heatpump_geography`, `W1_reveal_over_time`.
- **`W2_customer_generator` (10 atoms)** — `W2_1_archetype_layers` (archetypes),
  `W2_2_population_draw`, `W2_4_household_budget`, `W2_5_life_event_stream`,
  `W2_6_sme_distress_twin`, `W2_7_willingness_classification`, `W2_8_self_rationing`,
  `W2_9_segment_debt_tnc`, `W2_10_dd_attribution_confound`, and `W2_3_competitor_field`
  (**epoch 4 — above ceiling, so epoch-gated even inside the front**).

**Epoch note:** most `W1_*` are epoch 3; the director already crossed the epoch-3 gate for weather
physics by console on 2026-07-18 (ledger `BUILD_OPEN` for W1_3–6 + C13). Setting the front's
`epoch_ceiling: 3` makes that crossing a *standing* authorization for the whole SIM_ACTORS region,
not a per-atom one — while `W2_3_competitor_field` (epoch 4) stays gated.

### 4.2 SUPPLIER — billing / pricing / settlement / site
The company's own machine. Members:
- **Billing — `D_billing_metering` (5 atoms)** — `D1_bill_correctness`, `D2_three_clocks`,
  `D3_catchup_rebilling`, `D4_loyalty_incentive_billing` (**epoch 4 — gated**),
  `D_payments_maturity_audit`.
- **Pricing — `B_commercial` (5 atoms)** — `B1_margin_bridge`, `B2_opex_cost_to_serve`,
  `B3_hedge_tariff_alignment`, `B5_regional_basis_risk` (epoch 3), `B4_competitor_field`
  (**epoch 4 — gated**).
- **Settlement — `E_finance_treasury` (3 atoms)** — `E1_ledger_double_entry`,
  `E2_revenue_reconciliation`, `E3_accrual_restatement`.
- **Site — `site/**` (L2 SITE lane)** — `SITE1_expert_doors`, `BRAND1_identity_system`, and the
  ungated SITE draw generally. (SITE is already an ungated parallel lane; the front makes its
  BUILD authorization explicit and declared rather than special-cased.)

**The composition rule in code** (the single predicate the draw filter and reconciler share):
```
def authorized_build(atom, proposed_level, action_desc) -> Verdict:
    # 1. gate check FIRST (G-1: a gate is never dissolved by a front)
    if crosses_gate(atom, proposed_level, action_desc):        # one_way_door | epoch | schema | values
        cleared = ledger_has_valid(GATE_CLEAR, atom, gate) or ledger_has_valid(BUILD_OPEN, atom)
        return AUTHORIZED if cleared else HELD_AT_GATE(gate)     # NTFY, keep drawing rest
    # 2. front membership
    for f in open_fronts():                                     # state==open AND valid FRONT_OPEN in ledger
        if atom_in_region(atom, f):
            return AUTHORIZED
    # 3. fallback: a per-atom console BUILD_OPEN still authorizes (backward compatible)
    return AUTHORIZED if ledger_has_valid(BUILD_OPEN, atom) else OFF_FRONT   # alarm if promoted anyway
```

### 4.3 The gates enumerated (what HOLDS)
1. **One-way doors** — all 8 `one_way_door.py` categories, verbatim. (`REPO_PRIVATE` — the
   director's own 2026-07-18 exclusion — is `PLATFORM_ADMINISTRATION`.)
2. **Epoch boundary** — any member advancing into epoch > front `epoch_ceiling` (=3 for both).
   Captures `W2_3`, `B4`, `D4` (epoch 4) and everything epoch 5 — the fitness/go-live territory.
3. **Schema / sim-structure** — the gated atom-set (`W4_*` wall contract, `G2` event-log/spine,
   `H9` map-write serialisation) + gated-path list (`sim_interface.py`, `maturity_map.yaml`,
   `interface/`, the governance files themselves). A build promoting a gated atom or touching a
   gated path HOLDS.
4. **Director-reserved values** — `A4`, `A5`, `A7` + the curriculum (R13). Reserved always.

---

## 5. The anti-failure guarantee — the twin-approver failure made impossible-or-loud

**The failure it guards (real, observed).** The `gate_authorization.py` docstring records it: *"the
autonomous worker flipped loop_stage idle→build on `OPS1_transport_failure_must_be_loud` and
`OPS1_governance_refusal_mutation_test` in its OWN build commits, with no twin/director
authorization — nothing mechanical prevented it."* And OPS1 §8 records the twin's own version: a
respawned worker's seed **self-advanced director-gated OPS1 work twice**, once even *after* the
hold was ruled. The twin-approver failure is a machine crossing a gate on its own say-so.

**How this model makes it LOUD (detection — built first, per the gate-wall's own sequencing).**
The reconciler's `GATE_CROSSED` and `DRAW_OFF_FRONT` alarms fire on exactly this. A promotion is
authorized iff `atom_in_open_front AND NOT gated`, checked against the **console ledger** — whose
valid entries the loop *cannot write* (`_is_valid_authorization` requires `channel==console`; the
worker is the doorbell channel). So:
- Loop flips `idle→build` on a **gated** atom (e.g. `A5_tournament_fitness_mortality`, a values
  gate) → no `GATE_CLEAR`/`BUILD_OPEN` exists → `GATE_CROSSED` alarm, LOUD.
- Loop draws an atom in **no open front** (e.g. an epoch-5 go-live atom) → `DRAW_OFF_FRONT`, LOUD.
- Loop self-writes a ledger entry to authorize itself → it must self-declare `channel`; a
  `channel != console` entry is invalid (`_is_valid_authorization` rejects it), and a *forged*
  `channel==console` entry is the exact residual the gate-wall docstring names for the **prevention
  layer** (crypto-tying provenance to the `director_input_log` HMAC / console human-presence stamp).
  Detection is honest and loud now; prevention is the deferred hardening, tracked, not claimed.

**How it makes it IMPOSSIBLE (prevention — the gated build path, sub-step 6).** Beyond detection:
the draw filter (§4.2) removes gated/off-front atoms from the BUILD candidate set *before* a fork
is dispatched, so the compliant loop never promotes them in the first place. Detection remains the
backstop for a non-compliant or buggy path; prevention shrinks the surface. The map-write
serialisation gate (`H9`) is what ultimately makes the orchestrator the sole map writer, closing
the "loop writes its own promotion" hole structurally — noted as the dependency it is.

**R15 — the control must be able to FAIL (mutation-tested).** Every alarm predicate is pure and
mutation-tested, matching the gate-wall's existing `unauthorized_promotions` test discipline:
- **M1 (gate fires):** inject a promotion of a gated atom (`A5`, or an epoch-4 atom) with no
  clearing ledger entry → assert `GATE_CROSSED` alarm=True. Mutate the gate predicate to always-
  pass → assert the test goes RED (the control's independence is proven).
- **M2 (off-front fires):** inject a promotion of an atom in no open front → assert
  `DRAW_OFF_FRONT` alarm=True.
- **M3 (open-front is quiet):** inject a promotion of an in-region non-gated atom with a valid
  `FRONT_OPEN` → assert no alarm (no false-positive treadmill — the F6-style legitimate case).
- **M4 (forged authorization is rejected):** inject a ledger entry with `channel != console` /
  empty provenance authorizing a gated atom → assert it does NOT clear the gate (`GATE_CROSSED`
  still fires). This is the anti-tautology test: self-written authorization is not authorization.
- **M5 (the exact incident):** replay the OPS1 §8 incident — a self-advance of a held/gated atom
  → assert the alarm fires. Incidents become invariants (the OPS1 precedent
  `test_incident_held_down_silent_held_running_is_HELD_VIOLATED`).

A control that cannot fail is worse than none (R15). These five prove it fires.

---

## 6. Fit to the whole — why this is not accretion (OPS1 spine)

**Understand WHY, design the WHOLE, don't accrete.** This model adds **no new subsystem**. It is
the same three primitives already in the operational layer, composed:
- **Declared-set + reconcile** = the `process_manifest.yaml`/`process_reconciler.py` pattern,
  applied to *scope* instead of *processes*. Same `state`-distinguishes-intended-from-failed idea
  (a `held` front reads HELD/silent, never MISSING/fault — the §8 disease, cured for scope).
- **Console-act ledger** = `gate_authorization.py`, extended with two record types, same validity.
- **Door predicate** = `one_way_door.py`, reused as one gate class.

The single new artefact is `fronts.yaml` + its reconciler — and it exists to answer one question
the current layer cannot: *"what region is the loop allowed to build in, and where must it hold?"*
Today that is answered atom-by-atom in the ledger (12 entries and counting) — which does not scale
and cannot say "the loop drew *outside* the authorized set." The front declaration + reconciler is
the smallest construct that answers it (SIMPLICITY GUARD: no front-scheduler cathedral; a YAML
predicate + a pure classify function). It traces to both OPS1 north-stars: **liveness** (the loop
advances open fronts without a per-atom nudge — fewer director-hours) and **safety** (a gate
crossing is loud and a forged authorization is rejected).

---

## 7. Open questions — honest

1. **Draw-log fidelity.** `DRAW_OFF_FRONT` needs to see *what the loop actually drew*, not only the
   map's post-hoc `loop_stage`. The map delta vs baseline catches promotions; catching a *draw*
   that did not yet promote needs the supervisor to log its concurrent-draw grants (it emits them
   in the turn message today — they may need persisting to a `draw_log.jsonl` the reconciler
   reads). Sub-step 2 must decide: reconcile on promotions-only (simpler, catches the real
   violation — a build landed) or draws-too (earlier, more plumbing).
2. **Path-touch gates vs atom gates.** The schema/sim-structure gate has both a gated-atom list
   and a gated-path list. Path-touch detection (did this build edit `sim_interface.py`?) needs the
   fork's diff, which the reconciler sees post-commit but the draw filter does not see pre-dispatch.
   Proposal: atoms carry their `file_scope` in the map already; gate on `file_scope ∩ gated_paths`
   at draw time, and backstop with a post-commit diff check. Confirm the map's `file_scope` is
   populated for the gated atoms.
3. **New atoms inside an open region.** A newly-authored atom that lands in an open front's lane is
   authorized by construction (the point of fronts). Is that always safe, or should a *new* atom
   default to held-pending-one-look even inside an open front? The gate-wall today grandfathers/
   defers new atoms explicitly (`promotions_since_baseline` only considers baseline-present atoms).
   Director call: does opening a front pre-authorize *future* atoms in its region, or only extant
   ones? (The mandate says "advances open fronts continuously," which argues for future-inclusive —
   but it is a real scope decision.)
4. **Epoch ceiling of 3 for both fronts.** Chosen because the director already opened epoch-3
   weather by console. Correct? Or should SUPPLIER sit at ceiling 2 (its live atoms are epochs 1–2;
   `B5`/`C13` epoch-3 are the only 3s) and SIM_ACTORS at 3?

---

## 8. Build plan — one sub-step at a time, each with its exit/mutation test

Built in order; the director gates advancement after each (OPS1 discipline: one verified sub-step,
show-me before advancing). No sub-step leaves a parallel old path running.

| # | Sub-step | PURPOSE | Exit / mutation test |
|---|---|---|---|
| **1** | **`fronts.yaml` + loader** (declaration only; both fronts `state: held`) | The IaC declaration exists and validates (loader-enforced `reason`/`opened_by`, like `process_manifest`). Nothing yet reads it for authorization. | Loader parses; a front `state: open` with `opened_by: null` **fails validation** (mutation: prove the console-trace requirement bites). |
| **2** | **`fronts_reconciler.py` — the pure predicates** (`atom_in_region`, `crosses_gate`, `authorized_build`, the status classifier) + **reconcile report** (read-only, no map write) | The generalised gate-wall: classify every promotion since baseline as ON_FRONT / DRAW_OFF_FRONT / GATE_CROSSED / FRONT_HELD / GATE_HELD. Wraps `unauthorized_promotions`, does not replace it. | **M1–M5** (§5) all pass. Independence check: mutate a gate predicate to always-pass → the M1 test goes RED. Run against the *current* live map+ledger → must be CLEAN (no false alarm on today's legitimately-authorized weather build). |
| **3** | **Ledger record types** — `FRONT_OPEN` / `GATE_CLEAR` / `FRONT_CLOSE` in `gate_authorization.py`, same `_is_valid_*` validity | Opening a front / clearing a gate is a recorded console act, R7 provenance, console-only writer. | A `FRONT_OPEN` with `channel != console` or empty provenance is **rejected** by `open_fronts()` (M4-class). `FRONT_CLOSE` re-freezes the region (R11: the release has a tested effect). |
| **4** | **Wire the reconciler into the health/reconcile layer** — transition-only typed alarms (R5, OPS1 G-N1/G-N2) via NTFY, hourly re-escalate; `DRAW_OFF_FRONT`/`GATE_CROSSED` are real-alarms | The drift/violation alarms actually page the director, not just print. | Inject a `GATE_CROSSED` state → assert exactly one transition NTFY fires, typed `real-alarm`, not window; assert no re-page on unchanged state (R5). |
| **5** | **Draw filter (prevention, read-side)** — intersect `_maturity_map_draw_concurrent`'s BUILD candidates with `authorized_build`; DISCOVER/FRAME/SITE untouched | The compliant loop never *draws* a gated/off-front atom for BUILD. Liveness preserved: it keeps drawing the rest of the front + escalates the gate (G-3, Rule 0). | With both fronts `held`, BUILD candidate set is empty and DISCOVER/FRAME still draws (no idle-stall). With SIM_ACTORS `open`, a below-target weather atom is drawn; a gated `W2_3` (epoch 4) is **not** drawn and an NTFY gate-escalation fires. |
| **6** | **Author + open the two fronts** — director console act writes `FRONT_OPEN SIM_ACTORS` + `FRONT_OPEN SUPPLIER`; flip `state: open`, set `opened_by` | The mandate's endpoint: the two permanent fronts live, self-governing. **This sub-step is the director's console act** (§10), not a loop action. | Reconciler shows both fronts ON_FRONT for their live atoms, CLEAN. A promotion outside both (an epoch-5 atom) still alarms `DRAW_OFF_FRONT`. |
| **7** | **(Deferred hardening) forge-proof the console trace** — crypto-tie `FRONT_OPEN`/`GATE_CLEAR` provenance to the `director_input_log` HMAC / console presence stamp | Close the residual the gate-wall names: a worker forging `channel==console`. Detection→prevention. | A ledger entry whose provenance HMAC does not verify against the console log is rejected as authorization even though it self-declares `channel==console`. |

Sub-steps 1–5 are **built and proven with both fronts HELD** — i.e. the whole mechanism is
verified while it authorizes *nothing*, so proving it cannot be the thing that opens a front. Only
sub-step 6 — a **director console act** — opens them. That ordering is itself the anti-failure
guarantee: the model proves itself before it is trusted, and the trust is granted by the director,
never by the loop.

---

## 9. Decisions the director must make to authorize the two fronts

1. **Front scope — SIM_ACTORS.** Confirm lanes `W1_market_weather` + `W2_customer_generator` +
   explicit `W1_2_generate_futures`. Include anything else (e.g. `W3_industry_systems` settlement
   timetable is world-side — in or out)?
2. **Front scope — SUPPLIER.** Confirm `D_billing_metering` + `B_commercial` + `E_finance_treasury`
   + `site/**`. **Explicitly excluded today:** `C_customer_ops` (collections/customer ops) and
   `F_risk_compliance` (compliance controls). Include collections/compliance in the SUPPLIER front,
   or keep them a separate (third) front / per-atom?
3. **Epoch ceiling.** Ceiling **3** for both (matches the already-authorized epoch-3 weather), or
   SUPPLIER at **2**? (§7.4)
4. **Future-atom inclusion.** Does opening a front pre-authorize *future* atoms that land in its
   region (mandate reading: yes, "continuously"), or should a new atom default to held-one-look
   even inside an open front? (§7.3)
5. **Schema/sim-structure gate list.** Confirm the gated atom-set (`W4_*`, `G2`, `H9`) and gated-
   path list (`sim_interface.py`, `maturity_map.yaml`, `interface/`, the governance files). Add/
   remove any structural seam.
6. **Values gate list.** Confirm `A4`, `A5`, `A7` + curriculum as the reserved-values gate.
7. **Reconcile granularity.** Promotions-only (simpler) or draws-too (earlier detection, more
   plumbing)? (§7.1)
8. **The authorization act itself.** After sub-steps 1–5 are built and shown GREEN with both fronts
   HELD, the director issues the two `FRONT_OPEN` console acts (sub-step 6) — the one-way, console-
   only step that turns the model on.

Items 1–7 are reversible design dials (change `fronts.yaml`, re-reconcile). Item 8 is the
director's console act — the gate this whole model exists to make the *only* way a front opens.

---

## 10. ADDENDUM — director's confirmed gates + spine correction (2026-07-18, console)

The director confirmed the defaults **with additions to the reserved boundaries**, and corrected the
spine: the model must run the **canonical `docs/design/MATURITY_MAP.md` (v1.1)**, not an ad-hoc read
of the YAML. Fold these into sub-steps 1–5:

### 10.1 The LEVEL gate — a new, distinct gate class (director P0)
`MATURITY_MAP.md §0`: **"director + advisor own the map (lanes, levels, dials, the Expert Hour bar).
The agent proposes level-ups with evidence; it never moves a cell itself."** So **any `level_current`
promotion (L0–L5) is a GATE** — distinct from the existing `loop_stage` BUILD-open gate. Today's
gate-wall catches `loop_stage idle→build`; it does **not** catch a `level_current` self-move. Sub-step
2 must add a **level baseline** (`level_current` per atom at genesis) and a `promotions_since_baseline`
analogue over levels: any agent-authored `level_current` increase **without a director+advisor
level-authorization record** is a `LEVEL_SELF_PROMOTION` alarm (LOUD). The agent's path is: build →
verify → **PROPOSE the level-up with evidence** (a `LEVEL_UP_PROPOSED` record / register entry) →
director+advisor move the cell. Mutation test M6: inject an agent level-move with no authorization →
assert `LEVEL_SELF_PROMOTION` fires; inject a director+advisor-authorized one → quiet.
*(This gate is the direct fix for a real 2026-07-18 error: the orchestrator self-levelled W1_4/D5/E4
to L2. Reverted; the gate makes the next attempt loud.)*

### 10.2 loop_stage is respected; stage-advance is a gate (the spine correction)
The model **runs the canonical map**: draw dial-weighted, flow each atom through the Hardening Loop
(**DISCOVER→FRAME→BUILD→VERIFY→HARDEN**), and **respect `loop_stage`**. The draw filter (sub-step 5)
keys on the atom's *canonical stage*:
- A **DISCOVER**-stage atom (e.g. all of lane **W1**, which is `L1 · dial-4-hot · DISCOVER`) is only
  eligible for **DISCOVER/FRAME** work — research + charter, doc-only. It is **NOT** BUILD-eligible.
- **Advancing an atom's stage** (DISCOVER/FRAME → BUILD, i.e. BUILD-open) is a **reserved gate**, only
  a director console act crosses it. *(This is exactly the 2026-07-18 W1 weather failure: the
  orchestrator self-advanced W1 DISCOVER→BUILD and built physics. The draw filter + BUILD-open gate
  make that impossible-or-loud.)*
- Epoch ceiling still applies on top (epoch>ceiling is gated regardless of stage).

Mutation test M7: a W1 (DISCOVER, dial-hot) atom → the draw offers DISCOVER/FRAME, **never** a BUILD
candidate; a synthetic self-advance of it to `build` with no console act → `GATE_CROSSED` fires.

### 10.3 Confirmed gate list (director 2026-07-18)
- **One-way doors** (all 8 categories, verbatim) — incl. **REPO_PRIVATE** (platform-admin), reserved.
- **Epoch / BUILD-open** — reserved (the weather-Epoch-3 self-open was the failure this closes).
- **Schema / sim-structure** — reserved (the wall contract, event-log/spine, map schema, governance files).
- **Level promotion (L0–L5)** — reserved (§10.1, NEW).
- **Director-reserved values** — `A4`/`A5`/`A7` + curriculum.

### 10.4 Confirmed front scope (director 2026-07-18)
- **SIM_ACTORS** = `W1_market_weather` + `W2_customer_generator` + `W1_2_generate_futures`, ceiling 3.
- **SUPPLIER** = `D_billing_metering` + `B_commercial` + `E_finance_treasury` + **`C_customer_ops`
  (collections)** + **`F_risk_compliance`** + `site/**`. *(Director: F Risk & Compliance is the most
  mature lane; C Customer Ops covers collections — both are core supplier lanes.)*
- **Future-atom inclusion:** yes — opening a front pre-authorizes future in-region atoms, with the
  reconciler LOUDLY flagging any newly-landed atom so it is never silent.

### 10.5 Deferred to AFTER sub-steps 1–5 prove (registered, not built now)
1. **Propose widening the concurrent fan beyond ≤3.** The map's July pipeline-parallelism predates
   this week's bounded-fan-out / merge-or-reap / fork-reconciler / gate-wall, which now make wider
   concurrency safe. Turn the dial **deliberately and reversibly** — propose the width + a safety-proof
   FIRST, director authorizes.
2. **Bank this week's parallel-safety machinery into canon as `MATURITY_MAP.md` v1.2** — so the
   evolution lives in the map, not scattered across commits.

Both wait until governance (1–5) holds and is proven.
