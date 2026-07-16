# A4_sim_approver — FRAME (canonical per-atom, doc-only)

**Atom:** `A4_sim_approver` · lane `A_strategy_governance` · epoch 4 · `provenance: proposal`
· `level_current: 0` → `level_target: 2` · `loop_stage: idle` · `dial_inherited: 1`
· `depends_on: [A3_approval_interface]`.

**Turn:** H17 Lane-3 FRAME (doc-only, no BUILD code — EPOCH_GATING Rule 1; no map edit — F1,
level reported via `docs/design/atom_status/A4_sim_approver.yaml`).

---

## Why this doc exists (and why it is NOT churn)

A4 had **no canonical per-atom FRAME terminus**. Its thinking existed only as scattered
registration prose in `docs/design/maturity_map.yaml`'s own `simplifications` list (the
2026-07-12 `GOVERNED_COMPANY_AND_THREE_LANES.md` entry) plus two verbatim "honesty discipline"
paragraphs duplicated across `company/governance/decision_rights.py` and
`company/governance/approval_interface.py`'s module docstrings, and a downstream mention as an
`A5_tournament_fitness_mortality_FRAME.md` dependency. None of those is A4's own FRAME — the
intrinsic frame-saturation guard (`background/supervisor.py::_is_frame_saturated`) correctly
does not recognise scattered registration prose or another atom's FRAME file as this atom's
terminus, so A4 kept being (correctly) re-offered to the idle DISCOVER/FRAME draw as genuinely
un-FRAMEd. This doc is that missing terminus: it **consolidates** (does not re-derive) the
registration prose, A3's now-completed build history (a live worked example of the exact
pending-decision pattern A4 must eventually resolve), and A5's own dependency framing, into A4's
own FRAME with its single BUILD-unblock gate stated once. Per MAKE_IT_STICK, saturation is
computed from disk on the next cycle — no marker to remember, no re-emission needed once this
lands. That is the honest end state: A4's FRAME work IS complete once consolidated; the only
remaining path to `level_target: 2` is BUILT, epoch-gated code.

---

## 1. WHAT the sim-approver is

A4 is a **policy agent that plays the role of the human approver** (the director, or a
director-delegated reviewer) during **tournament** evaluation — the epoch-4 mode where many
candidate company strategies run across many generated-future scenarios
(`W1_2_generate_futures`, `A5_tournament_fitness_mortality`). Every one of those runs will, at
some point, hit a governance decision that A2's decision-rights register
(`company/governance/decision_rights.py`) flags as requiring approval (a pricing move above
the non-routine threshold, a hedge-mandate change, a credit-collections policy exception, …).
In a live single-run simulation that request goes to the real director via A3's
requests-awaiting-decision surface. A tournament cannot do that: it needs to resolve the same
class of decision **thousands of times, autonomously, and consistently**, without the director
present for each one — the identical problem a real company solves by delegating routine
approvals down a authority ladder rather than escalating every one to the board. A4 is that
delegated authority, mechanised for the SIM.

Named registration source (`maturity_map.yaml`, `A4_sim_approver.simplifications[0]`,
2026-07-12 director-decided conversation, `GOVERNED_COMPANY_AND_THREE_LANES.md` Part 1 item 3):
*"for the SIM an invisible agent acting as that human; turns forking into a benefit not a
risk."* `real_world_twin`: *"a real board member reviewing a submitted paper, not an auditor
with database access."* That phrase is load-bearing for §2 below — a board member reviews the
paper **submitted to them**, they do not go and pull the underlying data themselves.

## 2. The seam to A3_approval_interface

A4 does not invent its own request/response contract. It is a **second resolver plugged into
the same pending-decision mechanism A3 already exposes** — the human-operable
requests-awaiting-decision surface built on A2's bitemporal `DecisionEvent` log:

- `company/governance/approval_interface.py::request_governance_approval()` builds a
  link-shaped `ContextPack` (structured `ContextLink`s + the company's own recommendation —
  "links, not prose", hard-gated by `ContextPack.validate()`) and calls
  `submit_decision_request()`. This is unchanged by A4's existence: the company still submits
  the same pack whether a human or A4 will resolve it.
- Today only one resolver exists: the director, reading `approval_queue_as_of()` (or, before
  Door 7 is built, the raw pending list) and calling
  `record_governance_decision(approved, rationale, resolved_at, actual_effort_minutes=...)`.
- A4's build adds a **second caller of the identical `record_governance_decision()` /
  `resolve_decision_request()` entry point** — a policy function that reads a pending
  `ApprovalRequestView` (decision class, the submitted `ContextPack`, elapsed `pending_seconds`,
  `sla_breached`) and produces the same `(approved, rationale, resolved_at,
  actual_effort_minutes)` tuple a human would, on a director-authored policy schedule instead of
  a human's clock. **No new schema, no new wall crossing** — A4 is a new writer against an
  interface A3 already built and proved end-to-end (`tests/simulation/
  test_renewals_approval_routing.py`, A3 now at `level_current: 2`, confirmed live-caller +
  outcome-neutral).

This is exactly the **C-S3 asynchronous wall contract** already resolved once for this whole
mechanism (`docs/design/GO_LIVE_SEAM_AND_INTERNAL_SEAMS_DESIGN.md` §1.1: *"A3_approval_interface
already found its own 'schema cannot represent pending latency' defect — CLAUDE.md states
explicitly these are the same law, build one mechanism"*): request and response are separate
events in time (`submitted_at` → later `resolved_at`), never same-step. A4 does not get to
special-case this into a synchronous call just because it is a machine, not a human, on the
other end — the whole point of A3's async-shaped contract was that the *resolver* is
swappable (human today, A4 in tournaments, a real go-live endpoint later) **without touching
the request side**. `actual_effort_minutes`/`actual_elapsed_seconds` are honestly `None`
throughout A3's build precisely because there is no A4 yet to draw a realistic actual from
(`decision_rights.py` module docstring) — A4's build is what finally lets those fields carry a
real, non-fabricated value in a tournament run, drawn from the director-authored policy's own
declared timing, not invented.

## 3. The DISTINCTION from DIRECTOR_TWIN — get this right, it is the crux of the FRAME

CLAUDE.md's `DIRECTOR_TWIN` (`background/director_twin.py`, Law B) and A4 look superficially
similar (both are "an agent standing in for a human decision-maker") and **must not be
conflated**:

| | `DIRECTOR_TWIN` (`director_twin.py`) | `A4_sim_approver` |
|---|---|---|
| **What it stands in for** | The real director, for the real build's own blocking/one-way-door questions (`route_blocking_decision`) | The human strategy-approver, for a **simulated tournament company's** governance decisions |
| **Whose canon governs it** | `docs/design/DIRECTOR_CANON.md` — the director's own, versioned; changes ONLY by his explicit overturn | A director-authored **curriculum policy** for the approver ROLE inside the sim — same "written, versioned, his" discipline, but scoped to what a fictional board approves, not to the real build's process |
| **May it learn from outcomes?** | **NEVER** (Law B, verbatim: *"must NOT learn from outcomes and must NOT optimise toward unblocking the agent — a twin that learns from the builder's success becomes a rubber stamp"*) | **NEVER either** — but for a distinct reason: the same two honesty disciplines apply verbatim (`decision_rights.py`/`approval_interface.py` docstrings): *"the sim-approver's policy is DIRECTOR-AUTHORED CURRICULUM — written, versioned, his — never learned/tuned by the agent from outcomes."* Two different actors (real build vs. tournament company), same law, for the same underlying reason: an approver that adapts to please the thing it approves stops being a check. |
| **Is it itself under evaluation?** | No — the twin is a fixed, canon-bound oracle for the *real* build | **Yes, in one narrow sense**: which company variant wins a tournament round depends in part on how that variant *responded to* the approver's decisions (did it request sensible things, live within its mandate) — the approver's **policy schedule** is director-set and fixed for a given tournament, but tournament OUTCOMES (which company strategies survive) are naturally sensitive to it, the way a real company's fortunes are sensitive to how permissive its actual board is. This is a property of what A4 sits inside (a search process, per `A5_tournament_fitness_mortality_FRAME.md`'s own alignment-risk analysis), not licence for A4 to tune itself toward outcomes — the fixed-per-tournament policy still comes from the director, versioned, exactly like the twin's canon. |
| **May it ever answer a real one-way door?** | Answers everything except a genuine one-way door (routes those to the real director) | **NEVER anything outside the sim.** A4 only ever resolves `DecisionEvent`s inside a simulated company/tournament run — it has no path to a real one-way door (spending real money, real-world commitments, security posture, …) because it has no access to anything outside the run it is scoring. This is a stronger, simpler boundary than the twin's — not "escalate the hard ones", but "structurally cannot reach them at all" (see §4). |
| **Read-only or does it act?** | Read-only / advisory — *"a voice, not a hand"* (`director_twin.py` docstring; proven by a real failed-write test) | A4 **does act** — `record_governance_decision()` is a real write to the bitemporal log, exactly as the real director's own call is. It is not a voice-only advisor; it is a genuine substitute resolver, because a tournament run has no human to advise. |

The shared thread, stated once so neither doc has to re-derive it: **both are director-authored
curriculum that must never learn from the thing it is judging.** Where they differ is *scope*
(real build vs. simulated tournament) and *mode* (advisory-only vs. a real acting resolver) —
get the scope wrong and A4 either (a) starts adjudicating real one-way doors (a Tier-1 safety
violation) or (b) gets built as a read-only advisor that can't actually unblock a tournament run
(defeats its entire purpose, per §1).

## 4. The epistemic wall — A4 approves on company-observable state only

A4 is a resolver *outside* the company's own wall, exactly like the human approver it replaces
(`approval_interface.py` docstring: *"the approver sits OUTSIDE the company's wall like a real
board: it sees ONLY the submitted context pack, never SIM ground truth, never company internals
beyond what is submitted. A board that can grep the codebase is not a board."*). Concretely, A4
must be built so that its policy function's ONLY inputs are:

- The submitted `ContextPack` (structured `ContextLink`s + the company's own recommendation).
- The `ApprovalRequestView`'s own metadata (`decision_class`, `pending_seconds`,
  `sla_seconds`, `sla_breached`) — latency the request has already accrued, itself an
  observable of the governance mechanism, not of the SIM.

A4 must **never** import `sim.*`/`simulation.*` internals, never read the tournament's
generated-future ground truth, never read a company variant's true fitness score to decide
whether to approve it. The epistemic-verifier gate that already scans every commit
(`tools/epistemic_verifier`) applies to A4's build exactly as it does to any other
`company/governance/**` file. A4's "curriculum" (§3) is a *policy over context-pack shapes and
elapsed latency* — e.g. "approve any `PRICING_MOVE` context pack whose recommendation cites a
loss-making customer segment within N hours" — never a policy conditioned on SIM-internal
knowledge of what the "right" tournament answer would be.

## 5. What L1/L2 mean for A4 in `A_strategy_governance` terms

A3's own build history is the direct precedent to read L1/L2 against (both atoms share the
lane, the mechanism, and the same `level_target: 2`):

- **L1 (module-level, real code, no live caller):** A4 exists as a real, tested Python module —
  a policy function (or small set of named policies) that reads an `ApprovalRequestView` and
  returns a decision, exercised end-to-end by tests against A3's real
  `submit_decision_request()`/`resolve_decision_request()` pair, but not yet invoked by an actual
  tournament run (because `W1_2_generate_futures`/`A5_tournament_fitness_mortality` don't exist
  yet to run one). Directly analogous to A3's own L1 (`approval_interface.py` built and tested,
  but the workflow "NOT yet triggered by the live simulation pipeline").
- **L2 (target, live-caller):** A4 is the resolver a **real tournament run** actually calls —
  every non-routine decision a company variant raises during that run is resolved by A4's
  policy, not left pending or hand-waved, and `actual_effort_minutes`/`actual_elapsed_seconds`
  carry real (director-authored-policy-derived) values instead of `None`. This mirrors A3's own
  L1→L2 step exactly (wiring `simulation/renewals.py::_route_pricing_move` as the first live
  caller) — A4's L2 is "wire A4 as the resolver on that same live path, when a tournament run
  exists to drive it."
- **L3 (not this atom's target, named for contrast):** would need the harder, honestly-flagged
  work A3's own build log already named as still open even at A3's L2 — e.g. an independent
  Expert-Hour on the now-live mechanism, and (A4-specific) evidence that A4's policy schedule is
  genuinely being exercised across a real range of tournament scenarios, not just one.

## 6. Known simplifications (R10)

- **No tournament exists yet to call A4.** `W1_2_generate_futures` (epoch 3) and
  `A5_tournament_fitness_mortality` (epoch 4, itself listing A4 as a dependency) are both still
  `loop_stage: idle`. A4's L2 is structurally unreachable until at least one of them can drive a
  real run — named here, not hidden.
- **The fitness-function/mortality-rule choice is explicitly NOT A4's to make**
  (`A5_tournament_fitness_mortality_FRAME.md` reserves that to the director) — A4 only resolves
  governance-approval decisions, it is not itself the tournament's scoring or culling mechanism.
  Conflating "the approver that lets a run proceed" with "the judge that scores the run" would
  be a scope violation of the director's own reservation on A5.
- **A4's curriculum policy is not designed here.** Per §3's shared discipline, the actual
  approve/reject rules A4 will run are the director's authored artefact when BUILD opens — this
  FRAME states the seam and the boundary, not the policy content (same discipline A5's FRAME
  already applies to fitness functions: options may be scoped, the choice is reserved).
- **A4 vs. A3's carried-forward maker-checker gap:** A3's own L1 build note flags that
  `record_governance_decision()` has no `resolved_by`/role check against the register's approver
  field (RBAC/identity enforcement deliberately out of scope for A3). A4's build inherits that
  same open gap — when A4 becomes a second caller of the identical function, nothing yet
  distinguishes "the director resolved this" from "A4 resolved this" at the schema level. Worth
  naming for BUILD (perhaps A4 stamps a `resolved_by` tag once that field exists), not a defect
  of this FRAME to fix now.

---

## 7. The single BUILD-unblock gate (the epoch-sequencing intelligence — HELD at L0)

| Atom | Epoch | Level (held) | Single BUILD-unblock gate | Gate class |
|------|-------|--------------|---------------------------|------------|
| `A4_sim_approver` | 4 | **0 (→2)** | `A3_approval_interface`'s real map level is **already `2/2` (target met)** — checked directly against `maturity_map.yaml`, not assumed: A3's live pending→resolve mechanism exists, is exercised end-to-end, and has a genuine live caller (`simulation/renewals.py::_route_pricing_move`). The dependency the map lists is therefore **satisfied today**. What still gates A4's own BUILD is **epoch/tournament readiness, not A3**: (1) Epoch-4 BUILD-open (TWIN, within the open epoch, per `route_blocking_decision`); AND (2) a real caller to exercise A4 against — either `W1_2_generate_futures` or `A5_tournament_fitness_mortality` landing far enough to drive at least one real tournament run (both currently `loop_stage: idle`, epoch 3/4). Until one of those exists, A4 could be built at L1 (module + tests against A3's real interface, per §5) with no live caller to reach L2 — so the gate that matters is **a real tournament-run caller existing**, not A3's level. | DIAL (epoch sequencing; the map's own `depends_on: [A3_approval_interface]` edge is stale in one respect — worth a future map correction that A4's binding blocker is now the tournament engine, not A3 — flagged here, not corrected, per F1: no map edit from this fork) |

**Pre-BUILD action items (named, not done here — out of this Lane-3 doc-only scope):**
- Build A4 as a second resolver against A3's existing `submit_decision_request()`/
  `resolve_decision_request()` pair — no new wall crossing, no new schema (§2).
- Author the director-set curriculum policy content for A4's approve/reject/timing rules when
  BUILD opens (§3, §6) — an explicit, versioned artefact, never agent-invented.
- When a tournament-run caller exists, wire A4 as its resolver (the L1→L2 step, §5) and stamp
  `resolved_by` provenance if that field is added to close the maker-checker gap A3 already
  carries forward (§6).

**Disposition:** level **HELD at 0** (proposal atom; FRAME complete ≠ built; BUILD-gated,
EPOCH_GATING Rule 1). This FRAME is A4's canonical terminus; the next idle draw reads A4 as
frame-saturated and yields to genuinely-un-FRAMEd work instead. No BUILD code, no map edit (F1).

---

*Sources consolidated (not re-derived): `docs/design/maturity_map.yaml` (`A4_sim_approver`'s own
registration prose, `A3_approval_interface`'s full build history L0→L2, checked live rather than
assumed), `company/governance/approval_interface.py` + `company/governance/decision_rights.py`
(the real A3/A2 seam code and their shared verbatim honesty disciplines),
`docs/design/A5_TOURNAMENT_FITNESS_MORTALITY_FRAME.md` (the tournament A4 serves, and the
director's fitness-function reservation A4 must not encroach on),
`docs/design/GO_LIVE_SEAM_AND_INTERNAL_SEAMS_DESIGN.md` §1.1 (the C-S3 async contract A3 and A4
share, "same law, build one mechanism"), `background/director_twin.py` (`route_blocking_decision`,
Law B) contrasted in §3. Domain framing checked against real code, not invented; the
fitness-function/policy CONTENT remains director-reserved throughout.*
