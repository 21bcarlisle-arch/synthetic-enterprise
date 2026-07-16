# FRAME — H17_autonomous_build_executor

**Atom:** `H17_autonomous_build_executor` — "Autonomous build-executor: a governed headless-turn
executor that CONSUMES the Rule-0 self-refill draw and lands work (the map moves without the
interactive session as sole executor); ALSO the Epoch-4 tournament substrate."
**Lane:** H_harness · **dial:** 3 · **level_current:** 0 · **level_target:** 3 ·
**loop_stage:** idle (BUILD-gated)
**Stage:** DISCOVER/FRAME (Lane-3, doc-only). **No BUILD code written. No level move.**

> This is a framing artifact only. It does NOT authorize a level change and does NOT modify the
> executor, its governor, or its daemon. Reading the executor sources for this FRAME was
> read-only. Per EPOCH_GATING_AND_ATOM_AUTHORSHIP.md Rule 1 the atom is BUILD-gated; DISCOVER/FRAME
> is available now, BUILD is not.

---

## 1. Current state (grounded in the actual code, read 2026-07-16)

Unusually for a FRAME, the substrate this atom describes **already exists and is running** — this
document is being produced *inside* one of its headless turns. The DISCOVER observation is therefore
not "what would we build" but "what is already built, what is its honest maturity, and what does
L0→L3 actually have left to prove". The three layers:

- **`background/build_executor.py`** — `run_once()`: lands ONE governed headless turn. It renders
  the Rule-0 self-refill draw into a turn prompt, dispatches a `claude -p` headless turn under the
  governance walls (one-way-doors → director, twin for the reversible rest, gate-verified push,
  atomic level-write via the `atom_status/` inbox), reaps the result, and reconciles the reported
  level against what was actually pushed to origin. The turn's structured JSON footer
  (`{atom_id, action, claimed_commit_sha, level_before, level_after, gate_status}`) is verified
  **independently against origin** — an unpushed or fabricated SHA fails the gate. This is the
  "committed code and reported level can never disagree" contract (F1 / `merge_atom_status`).
- **`background/executor_governor.py`** — `run_loop()`: wraps `run_once` in a self-continuing loop
  with a tripwire. It **refuses to run unless the director's durable enable-flag is present**
  (`docs/observability/.build_executor_enabled`, DIRECTOR_ANSWERS_C7 #6) — the one non-repo,
  director-owned switch (kill-switch / DARK-gate). Stop reasons observed live: `budget_exhausted`,
  `map_unreconciled`, `repeated_failure`, `kill_switch_off`. A one-way-door escalation NO LONGER
  stops the loop (ESCALATION_IS_NTFY_NEVER_WINDOW.md): it NTFYs async and keeps drawing other atoms.
- **`background/executor_daemon.py`** — `run_forever()`: keeps `run_loop` running with zero human
  nudge (continuation is a MECHANISM, not an exhortation — MAKE_IT_STICK). It RESTARTS run_loop on
  an unexpected crash (resilience, with anti-crash-loop backoff) but STAYS DOWN on a terminal
  human-needs-to-act reason (a genuine wall the loop already NTFY'd, or the kill flag off).

Evidence it is live: `docs/observability/build-executor-log.md` shows real dispatched/reaped turns
(e.g. `run_once SUCCESS: write-landed sha=08e20d9…` 2026-07-15 08:04Z) and real terminal reasons
(`map_unreconciled`, `budget_exhausted`, `kill_switch_off`), plus per-turn transcripts under
`docs/observability/build-executor-turns/`.

**So why is the atom at level 0?** Because it was authored as a `proposal` atom and has never been
run through a formal level gate — the substrate matured ahead of its map registration. The honest
map level is a DEFECT of un-reconciled bookkeeping, not of missing capability. Closing it is a
BUILD-gated act (formal level-gate + Expert-Hour), not this FRAME's to do.

## 2. The two jobs this atom serves (and why they are the same substrate)

**Job A — move the map without the interactive session as sole executor.** Before H17, the
maturity map only advanced when the human-facing Opus session personally ran a build. That makes
the single human reviewer's attention the throughput limiter (the real scarce resource,
BUDGET_UNCONSTRAINED.md). H17 lets the Rule-0 draw be CONSUMED by a governed headless turn so the
map moves unattended — while every WALL still holds (the turn cannot self-authorize past a
one-way-door, cannot alter its own security profile, cannot push red).

**Job B — the Epoch-4 tournament substrate.** The Epoch-4 evolutionary tournament needs to run
thousands of governed "lives" unattended. The same primitive — "dispatch a bounded, governed,
gate-verified headless turn and reconcile its result against ground truth" — is exactly what a
tournament generation needs per candidate. H17 is where A8's cheap-inner-loop work (see §5) cashes
out: A8 makes one life cheap; H17 makes running N of them governed and unattended.

## 3. The walls this atom lives behind (non-negotiable, already mechanised)

1. **One-way doors → director, never the executor** (`background/one_way_door.py`): real money,
   real-world commitments, unretractable public claims, irrecoverable data loss, security/secrets/
   safety-control changes, values/curriculum decisions, a real customer/market, platform admin.
   The executor escalates via NTFY and keeps drawing; it never decides one.
2. **Escalation is NTFY, never the window** (ESCALATION_IS_NTFY_NEVER_WINDOW.md, P0 WALL): a
   window-ask is a silent stall. Decompose walls — do the reversible parts autonomously, escalate
   only the irreducible core, keep drawing.
3. **Gate-verified push**: blast-radius tests for touched files + the epistemic verifier must both
   pass before commit+push (via `background/tree_lock.py`). Never push red.
4. **Atomic level-write (F1)**: a fork records its level in `docs/design/atom_status/<id>.yaml` in
   the SAME commit as its code; the integrator folds it via `merge_atom_status`. Committed code and
   reported level can never disagree — no free-text level left to a separate judgment step.
5. **Director's durable enable-flag is the only ignition** (kill-switch / DARK-gate). The executor
   can NEVER set its own enable flag — that is a safety-control change (one-way-door #5), console-
   authenticated only (the authentication convention for safety-reducing changes).
6. **Honesty wall is physics, not a dial**: the executor may not move a level it cannot prove
   (R15 controls-that-can-fail, R11 verify-to-the-rendered-value). A false completion is worse than
   an honest hold; the treadmill of atoms is infinite, so there is never pressure to fake one.

## 4. Coupled-triad framing (COUPLED_TRIAD_DESIGN.md — the gap is the score)

H17 is a HARNESS atom, so its triad role is to MEASURE a gap, not to be believed:
- **SIM/world** does not apply — H17 is machinery, not a world capability.
- **The belief-vs-truth gap H17 measures is its OWN**: the gap between what a headless turn
  *claims* it landed (its JSON footer) and what origin *actually* holds. `run_once`'s
  independent-against-origin verification IS the gap measurement — a turn that claims a SHA that
  isn't on origin is a measured, caught divergence, not a trusted success. The design invariant:
  **no self-report is ever trusted; every claim is reconciled against ground truth (origin / the
  folded map).** That is the harness measuring the executor, exactly as the triad requires a
  verdict-organ to be outcome-tested (R15: a judge whose passes later fail is bad).

## 5. Dependency / composition map (for whoever opens the BUILD)

- **A8_experiment_loop_speed** (cheap inner loop) — H17 is where a cheap life is run N times.
  A8's own note flags "a future H17 in-process frontend" as a distinct usage shape from the CLI's
  fresh-process-per-invocation: if H17 ever runs `run_tournament()` repeatedly inside ONE long-lived
  process, the RSS self-calibration only measures on its first call and fails closed thereafter (a
  real, named remaining gap A8 disclosed for exactly this seam). The BUILD that wires A8↔H17 owns
  closing that.
- **`background/executor_governor.py` / `executor_daemon.py`** — already the loop + resilience.
- **The mock composition** (A8's biggest lever, `SIM_RECORDED_TRACE` → `RecordedSimInterface`) is
  UNWIRED into the annual_report/sim run path (`build_sim_interface()` has zero run-path callers as
  of 2026-07-16). Until it is wired, a tournament life is a full-fidelity sim run; H17 can run lives
  unattended but not yet *cheaply* at Epoch-4 scale. That wiring is ARCH1/company-owned, not H17's.

## 6. What L0→L3 would have to prove (NOT built here — the BUILD's checklist)

1. **Reconcile the map bookkeeping**: register the existing substrate at its honest level with the
   evidence above, via a formal level-gate (not a self-declaration).
2. **Mutation-test the governance controls** (R15): prove `run_once`'s origin-reconciliation FIRES
   on a fabricated/unpushed SHA; prove the kill-switch gate FIRES when the flag is absent; prove a
   one-way-door draw ESCALATES rather than lands. A control that cannot fail is worse than none.
3. **Expert Hour** (cold-eyes + skeptic) across the governor/daemon/executor seam, focused on the
   two named risk shapes: a headless turn that self-authorizes past a wall, and a self-report the
   integrator trusts without reconciling.
4. **Time-scale-invariance declaration** (C-S5) for the tournament-substrate usage.

Only after all four does the level move — and the level-move itself is a BUILD-gated act plus (for
the Epoch-4 fitness-function coupling) a director-reserved values decision, neither of which this
DISCOVER/FRAME turn performs.
