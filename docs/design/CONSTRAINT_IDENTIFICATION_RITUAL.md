# CONSTRAINT IDENTIFICATION RITUAL — name the ONE binding constraint each cycle

**Atom:** `G8_constraint_identification_ritual` (maturity_map.yaml, epoch 2,
L0→1, lane H_harness, size S). This is a **FRAME pass, doc-only** — no BUILD
code (the atom is BUILD-gated per `EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1).
**Provenance:** authored as proposal #2 of the Theory-of-Constraints row in
`docs/design/METHOD_LENS_AUDIT.md` §3.

**What this doc is:** a specification for a lightweight Theory-of-Constraints
(ToC) ritual — each cycle, NAME the single current binding constraint on
end-to-end throughput of *landed, verified* work, and state how the other lanes
SUBORDINATE to it — adapted for a one-director + AI-executor shop.

**What this doc is NOT:** it does not build the mechanism. Whether/how this
becomes a recurring digest line is a named, later BUILD slice (§6).

---

## 0. Why this exists — the diagnosis, in this repo's own words

`METHOD_LENS_AUDIT.md` §1 row 3 recorded the gap this atom closes, verbatim:

> We do steps 1 (identify) and 3 (subordinate) *reactively*, per-incident.
> There is no **standing** mechanism that continuously re-asks "what is the
> current constraint"... There is also no **elevate → repeat** ritual: once a
> constraint breaks... nothing formally re-asks "what's the *next* constraint
> now that this one is gone" — it's discovered by the next incident rather than
> by design.

The same audit named the pattern under which we keep re-learning this:
**"bottlenecks are onions"** (`RETRO_WHY_WE_MISSED_IT.md` F4) — "empty
draw→cap1→livelock→BUILD-gated→map-contention, each fix revealed the next; the
first diagnosis of a slow system is almost never the real one." Every one of
those layers was discovered **by injury** — a stall the machine walked into —
not by a standing question asked before the stall. Goldratt's Theory of
Constraints is the named discipline that already solved this class of problem:
a system's throughput is governed by exactly one binding constraint at a time,
and improving anything else is motion without throughput.

This ritual adopts the **principle** (name the constraint, subordinate to it,
elevate, repeat) and rejects the **ceremony** (Drum-Buffer-Rope scheduling
meetings, buffer-management dashboards for human shift planning). Per
`METHOD_LENS_AUDIT.md` §2, the ToC ceremony rejected is "formal DBR scheduling
meetings, buffer-management dashboards for human shift planning"; the principle
adopted is "the Five Focusing Steps as a standing *query*, not a meeting."

---

## 1. The five focusing steps, adapted for one director + AI executors

Goldratt's five focusing steps, translated to a single-principal, AI-executor
shop. There is no team to synchronise, no stand-up, no shift hand-off — so each
step is a **per-cycle question answered in one line**, not a meeting.

| # | Goldratt's step | Original (factory) | Adapted (this shop) |
|---|---|---|---|
| 1 | **IDENTIFY** the constraint | Find the machine with the largest queue in front of it | Name the ONE thing that, if removed, most increases end-to-end throughput of **landed, VERIFIED** work (not started work, not lines of code — work that passed its exit test and is banked). |
| 2 | **EXPLOIT** the constraint | Make the bottleneck machine never starve or idle | Extract maximum throughput from the current constraint with resources already in hand — before spending anything new. Is the constraint atom actually being worked every cycle it *can* be? Is it blocked on something reversible we could do now? |
| 3 | **SUBORDINATE** everything else to it | Pace non-bottleneck machines to the bottleneck's rhythm | ORDER the other lanes so their effort feeds (or at minimum does not obstruct) the constraint. Prefer work that unblocks or de-risks the constraint. **Subordination ORDERS effort; it never zeros a lane** (see §4 guardrail — this is the Rule-0 wall). |
| 4 | **ELEVATE** the constraint | Add capacity (buy a machine, add a shift) | If exploit + subordinate have not broken it, invest to lift the ceiling: decompose the constraint atom, open a dependency it is blocked on, add a fast path. Elevation is the expensive step — reached only after exploit is exhausted. |
| 5 | **REPEAT** — do not let inertia become the constraint | Once broken, go back to step 1; the constraint has MOVED | The moment the named constraint breaks, **re-ask step 1 immediately** — the constraint is now somewhere else (the "onion" peels). Never keep subordinating to yesterday's constraint out of habit; that inertia is itself the failure mode F4 named. |

**The ritual, in one sentence:** each cycle, answer *"what single thing most
limits landed-verified throughput right now, are we extracting everything we
can from it before spending, and how is other work ordered relative to it?"* —
and when it breaks, ask again.

**Ceremony explicitly rejected** (so it does not creep back in): no stand-up, no
recurring meeting, no buffer dashboard, no DBR shift schedule. This is a
**query answered against state we already hold** (the maturity map's
`loop_stage`/`depends_on`/`blocked` fields, the digest), not a synchronisation
event. A single principal has nothing to synchronise.

---

## 2. What counts as "the constraint" — definition discipline

To keep this a diagnostic and not a vibe, the constraint each cycle is named by
a checkable test, in priority order:

1. **The atom whose completion unblocks the most downstream work** — measured by
   `depends_on` edges in `maturity_map.yaml` pointing INTO it, weighted toward
   items on the current epoch's critical path (the exit test that gates the
   next epoch).
2. **On a tie, the item with the longest age-in-stage** — the raw material G5's
   `tools/effort_calibration.py` already mines from git-timestamped level
   transitions (`METHOD_LENS_AUDIT.md` §1 row 2). The thing that has sat longest
   without moving is the strongest bottleneck candidate.
3. **On a further tie, the reversible-cost-to-remove tiebreak** — prefer naming
   the constraint whose removal is cheapest to attempt, so exploit/elevate can
   start this cycle rather than being deferred.

There is **exactly one** named constraint per cycle. Naming two is a refusal to
do step 1 (a real factory has one binding machine; a system with "several
bottlenecks" has not found its real one yet — F4). If the honest answer is
"the constraint is the single human reviewer's attention" (which CLAUDE.md's
BUDGET_UNCONSTRAINED note already identifies as the real limiter), that is a
**valid and important** naming — subordination then means *minimise
director-hours spent on this constraint*, exactly the MAKE_IT_STICK objective.

---

## 3. WORKED EXAMPLE from real current state (2026-07-16)

The live map contains a textbook binding constraint. This is not hypothetical —
it is what the map reads today.

### IDENTIFY — today's binding constraint

**`A8_experiment_loop_speed`** is the named throughput constraint on **Epoch-4
tournament feasibility**. Its own registered simplification states the arithmetic
plainly (maturity_map.yaml, A8):

> at ~500s/full-sim-run single-threaded, a 10,000-life evolutionary tournament =
> ~58 days; feasibility (10k lives in a week) needs ~60s/life = ~8–10x too slow
> today.

The Epoch-4 fitness function is a director-reserved values decision (one-way
door #6), and the *tournament that evaluates it cannot be run at all* until the
inner loop is ~8–10x faster. So A8 sits directly on the critical path to Epoch 4:
remove it and the largest downstream capability unblocks. It wins step 1 by test
#1 (most downstream-unblocking) — and `H17_autonomous_build_executor` literally
carries `depends_on: [A8_experiment_loop_speed, ARCH1_internal_seams]`, a
concrete downstream edge.

### EXPLOIT — extract everything from A8 with resources in hand

Before spending on the big lever, take the throughput available now. On
2026-07-16 A8's *in-scope secondary lever* was exploited: `run_tournament()`
gained a self-calibrating worker cap (a probe wave measures real child RSS via
`getrusage(RUSAGE_CHILDREN)` and recomputes the worker count). Measured result:
1→3 workers, **3.5x wall-clock reduction** on a 4-life run, zero manual tuning,
fitness/determinism byte-identical. That is exploit: maximum throughput from the
constraint using only what A8 already owns (`tools/tournament_runner.py` + its
tests), **before** paying for the expensive lever.

Honesty wall held: A8's `level_current` stayed at 2. Exploit bought a real,
measured slice (~3.5x) but not the ~8–10x feasibility gap — because A8's
*biggest* lever is not in A8's own file_scope.

### SUBORDINATE — order the other work relative to A8's real blocker

A8's own simplification names the biggest lever and its owner: a **typed mock
interface** (`RecordedSimInterface`) that replays the recorded exogenous world
so a life runs against a mock instead of a full ~5.67 GB sim — inner loop
500s → seconds. That lever is owned by **`ARCH1_internal_seams`**, and the
2026-07-16 verification found it **unwired**: `build_sim_interface()` honours
`SIM_RECORDED_TRACE → RecordedSimInterface`, but `grep -rn build_sim_interface
company/ saas/ sim/ tools/` returns **zero run-path callers** — the life
subprocess (`saas.reporting.annual_report`) constructs no `SimInterface` at all,
so setting the env var on a life is currently a no-op.

So subordination this cycle reads: **the highest-leverage move on the whole map
is wiring `annual_report`'s exogenous-world access through the `SimInterface`
seam (ARCH1's BUILD), because that is what unblocks A8's ~8–10x win.** ARCH1
subordinates to A8's constraint not by decree but because the map's dependency
structure already says A8 `depends_on` ARCH1. When a cycle asks "what should
BUILD width go to first," the answer is ordered by this: the ARCH1 wiring
outranks a same-lane atom that unblocks nothing downstream.

### ELEVATE / REPEAT — the next onion layer

Elevate here = open the ARCH1 measured-L2 wiring slice as its own BUILD atom
(the 2026-07-16 ARCH1 finding recommends exactly this: "BUILD decompose
measured-L2 as its own opened slice with A8-serialisation"). Once that lands and
A8 captures-once-replays-per-life, **step 5 fires**: re-ask step 1. The
constraint will have moved — plausibly to the single reviewer's attention, or to
H17's activation gate (director-reserved), or somewhere the onion has not yet
revealed. The ritual's whole value is asking *then*, by design, instead of
waiting for the next stall to reveal it.

---

## 4. GUARDRAIL — the constraint name is a DIAL, never a target, and NEVER a reason to hold

Two walls bind this ritual. State them prominently because a ToC practice
imported carelessly violates both.

### 4a. Dial, not target (R12 anti-goal-seek)

The named constraint is a **DIAGNOSTIC** — it *informs* where effort is ordered,
exactly like `size:` (S/M/L/XL) informs decompose (R12/G5) and margin informs
sanity (R12). It is **never a target or a gate.** The moment "reduce the named
constraint's cycle time" becomes a number to hit, it reintroduces the deadline
pressure that manufactures self-certified false-L3s — the identical failure mode
R12 was written to stop (`METHOD_LENS_AUDIT.md` §0 already extended R12 to
process metrics for exactly this reason). Naming A8 as the constraint must never
license shortening A8's verification, deleting a test to make the loop "faster,"
or promoting A8 to hit a forecast (LAW A: the plan is a diagnostic, dates yield
to tests). A8's own 2026-07-16 build proves the discipline: a real 3.5x measured
win, and `level_current` still held at 2 because no honest L3 DoD was met.

### 4b. Subordination NEVER zeros an idle-capable lane (Rule 0, a WALL)

This is the load-bearing guardrail. **RULE 0 (the PRIME DIRECTIVE):** the default
state of the company is WORKING; holding at a wall while any idle-capable lane
(FRAME, DISCOVER, SITE, red-team, hardening) has work is *itself* a Rule-0
violation; "an empty feasible set is a DEFECT IN THE DIALS, not a reason to
hold."

Subordination is a **DIAL** — it ORDERS work; it must never zero the feasible
set. Naming a constraint answers *"what should I prefer first,"* NOT *"what is
the only thing allowed."* Concretely:

- **Lane-3 DISCOVER/FRAME, Lane-2 SITE, red-team, and hardening keep drawing
  work every cycle**, even while A8/ARCH1 is the named build constraint. This
  very FRAME doc is proof: it landed as Lane-3 doc-only work *while* A8/ARCH1 is
  the standing build constraint — subordination ordered BUILD width toward the
  ARCH1 wiring; it did not idle Lane-3.
- Subordination that starves an idle-capable lane must **automatically yield**:
  per Rule 0, dials yield in reverse priority order until work exists. If naming
  a constraint would leave a capable lane with nothing to do, the correct move is
  to widen scope (draw the next-ranked idle atom), not to hold. The constraint
  name loses to Rule 0 every time they conflict.
- A single BUILD constraint never justifies Lane-2/Lane-3 idle
  (`THREE_LANES.md`: "L1 narrowness never justifies L2–L3 idle").

**Composition, not gating.** This ritual composes with the digest as an
**observability line** — "current binding constraint: `<atom>` — <why> —
subordination: <ordering>" — read alongside the WIP/cycle-time numbers G7 would
surface. It is **not** a gate on the draw, not a hold, not an approval. The
supervisor's draw logic (`supervisor.py`, Rule-0 self-refill) is unchanged by
this atom; the constraint line *annotates* what the draw is already doing, it
never overrides it. A constraint line whose effect were "stop other lanes" would
be an R11 orphan-transition / Rule-0 defect, not a feature.

---

## 5. Where it composes (relationship to already-tracked atoms — not re-litigated)

- **`G7_wip_and_cycle_time_dashboard`** (METHOD_LENS_AUDIT §3 proposal 1) — the
  age-in-stage / WIP / arrival-rate numbers G7 surfaces are the *inputs* to this
  ritual's step-1 tie-breaks (§2). G8 names the constraint; G7 supplies the
  measurements it reasons over. Build order: G7's data feed is the natural
  substrate, but G8's ritual can run today against the map's `depends_on` +
  `loop_stage` fields even before G7 lands (identify-by-dependency-structure
  needs no new instrument).
- **`G4_unified_failure_register`** — the cross-retro strike register is where a
  *repeatedly-recurring* constraint (the same bottleneck class peeling back
  every few cycles) would be flagged as a class defect (R3/R10), rather than
  re-named fresh each cycle.
- **Rule 0 / `supervisor.py` self-refill** — the mechanism that already yields
  dials to keep the feasible set non-empty. G8 is the *diagnostic* that names
  WHY one atom is preferred; Rule 0 is the *wall* that guarantees preference
  never becomes exclusion. They are complementary: G8 without Rule 0 could
  starve a lane; Rule 0 without G8 has no standing name for the constraint.

---

## 6. Honest "not built here" — the named later BUILD slice

**This is a FRAME pass. It specifies the ritual; it does not mechanise it.** Per
`MAKE_IT_STICK.md`, a rule lives "in CLAUDE.md AND as enforced code, or not at
all" — a ritual left as prose-only will decay. So the mechanisation is named
explicitly here as a **later, BUILD-gated slice**, not silently deferred:

> **Later BUILD slice (BUILD-gated, not opened by this doc):** add a single
> **constraint line to the recurring digest** — a function (candidate home:
> alongside the existing digest builders in `background/effort_digest.py` /
> `background/sanity_daemon.py`, reference-only, NOT edited by this FRAME) that,
> each digest, computes the current binding-constraint candidate from the map's
> `depends_on` graph + `loop_stage` + G7's age-in-stage data, emits ONE
> observability line ("current binding constraint: <atom> — <why> —
> subordination: <ordering>"), and re-emits only on *change* (R5:
> transition-only, no repeated unchanged status). It must be an **observability
> line, never a gate** — mutation-testable that it cannot hold a lane (R15: a
> planted "constraint present ⇒ block idle lane" must FAIL the test). file_scope
> for that slice: `[background, tools, tests]`.

Until that slice is opened and built, this atom reaches **L1 (FRAME landed,
design specified)** and no further. The ritual is *runnable by hand today*
(§3 demonstrates it against real state), which is the L1 value — but it is not
yet a standing mechanism, so it does not claim to have converted policy to
mechanism. That conversion is the L1→L2/L3 BUILD move, director-twin-openable
within the open epoch, and it is registered as this atom's own open work, not
this doc's.

---

## 7. DoD checklist (self-audit against the atom brief)

- [x] Five focusing steps adapted for one-director + AI-executor shop, ceremony
      rejected — §1.
- [x] The ritual: name the single binding constraint each cycle + how lanes
      subordinate WITHOUT starving — §1, §2, §4b.
- [x] Worked example from real current state (A8/ARCH1, identify→exploit→
      subordinate) — §3.
- [x] Guardrail stated prominently: dial-not-target (R12) + never-hold-an-
      idle-lane (Rule 0), composes as an observability line not a gate — §4.
- [x] Honest "not built here": FRAME only; mechanisation as a digest line named
      as a later BUILD slice — §6.
- [x] No BUILD code, no map edit, writes only under `docs/design/` — this atom's
      file_scope.
