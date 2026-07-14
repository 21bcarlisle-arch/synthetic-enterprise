# ARCH1_internal_seams — FRAME: the typed mock-interface at the sim/company seam

**Status:** FRAME (Lane-3, doc-only). **NO production code changed by this doc; no tests run.**
**Atom:** `ARCH1_internal_seams` (`docs/design/maturity_map.yaml` L942), `level_current: 0`, `level_target: 2`, `loop_stage: build`, `file_scope: []` (scopeless — this doc gives it one).
**Purpose (this FRAME's remit):** make ARCH1 BUILD-ready for its **highest-return slice** — a **typed mock interface at the sim/company seam** so a company "life" runs at LOW memory footprint. This is the biggest single lever on the Epoch-4 tournament (A8 `depends_on: [ARCH1_internal_seams]`) and directly cuts OOM risk.
**Source requirements:** `docs/observability/experiment-cycle-profile.md` (the ~10× gap); `tools/tournament_runner.py` (A8's parallel runner, at L2); `docs/design/GO_LIVE_SEAM_AND_INTERNAL_SEAMS_DESIGN.md` (ARCH1's DISCOVER — the async envelope, the four crossings); `company/interfaces/sim_interface.py` (the seam); CLAUDE.md WALLS (epistemic wall, Historical Ground Truth + determinism), C-S1..C-S5, typed-flow-seam preference, R10/R14/R15, COUPLED_TRIAD.
**Author:** FRAME fork, 2026-07-14.
**What was out of scope, and why** (G3 Finding-2 discipline): this FRAME does **not** design the four *inner* domain seams (pricing/billing/settlement/collections) — that is the broader ARCH1 already DISCOVER'd in `GO_LIVE_SEAM_AND_INTERNAL_SEAMS_DESIGN.md` and remains a later slice. It scopes only the **outer sim/company seam mock**, because that is the slice A8 needs and the one that moves the memory number. It does not design the Epoch-4 fitness function, does not touch the sim side's world-generation physics, and writes no code.

---

## 1. The problem in one paragraph (from the measured profile)

`tools/tournament_runner.py` already fans N "lives" across cores as subprocesses — but its own comment records the wall: **a `--fast` FULL-window life ≈ 5.67 GB RSS (~351 s)**, and at ~8 GB available that is **one** concurrent life. The tournament is therefore **memory-bound, not core-bound**: `memory_safe_worker_cap()` degrades to 1 worker, so the parallel runner cannot use the cores it has. The 5.67 GB is dominated by **reconstructing the exogenous world every life** — weather physics over 2016–2025, the forward-curve/price history, the settlement baseline — none of which the company can see inside anyway (epistemic wall). The company only ever touches that world through `SimInterface` observables. **If the expensive exogenous world is recorded once and replayed through the seam at low memory, per-life RSS collapses and the memory cap stops throttling parallelism.** That is ARCH1's job, and it is pure seam work.

---

## 2. The seam(s) to mock — and the exogenous/endogenous split (the load-bearing decision)

The mock is a **third `SimInterface` implementation** alongside the existing `StubSimInterface` and `LiveSimInterface` in `company/interfaces/sim_interface.py`. It implements the *same* Protocol, so **the company sees observables only, never internals — the epistemic wall is preserved by construction** (the mock lives on the sim side of the seam; nothing in `company/**` outside `company/interfaces/` changes, and `tools/epistemic_verifier.py` still passes).

The seam methods (`sim_interface.py`) split cleanly into two classes, and the split is the whole design:

| Class | Methods | Depends on company's own actions? | Mock treatment |
|---|---|---|---|
| **EXOGENOUS** | `get_forward_price`, market/price curve, weather-driven consumption *baseline*, regulatory publications | **No** — a real supplier's decisions don't move the wholesale curve or the weather | **Pure replay** from a recorded trace. Faithful. This is where the 5.67 GB lives, and where the memory win comes from. |
| **ENDOGENOUS** | `get_customer_status`, `get_churn_estimate`, `get_settlement_data` (volumes reflecting the company's actual book), `notify_*` (the company's own writes back to the sim) | **Yes** — churn responds to *this variant's* pricing; settled volume reflects *this variant's* book | **Fixed-world approximation** in the mock; the feedback loop the company closes on its own small state still runs live. Named simplification (R10), gap measured (COUPLED_TRIAD, §6). |

**Decision:** the mock records and replays the **EXOGENOUS** world (the expensive, company-invariant part) and leaves the **ENDOGENOUS** loop running live in-process (it is cheap — it is the company's own book state, kilobytes, not gigabytes). This is honest: for observables a real supplier cannot influence, replay is exact; for reactive observables, the mock is a *fixed-world* run whose divergence from a full sim is **measured, bounded, and declared**, never hidden. A pure-replay-everything mock would silently break the price→churn→volume→settlement feedback loop and quietly lie about what the company achieved; this split refuses that.

---

## 3. The typed trace format (record once, replay cheaply)

`ObservableTrace` — an **append-only recorded log of exogenous seam responses**, captured from one seeded `LiveSimInterface` run. It reuses the go-live envelope shape already settled in `GO_LIVE_SEAM_AND_INTERNAL_SEAMS_DESIGN.md §1.2` (same shape at two radii — one mechanism), so ARCH1 does not invent a second envelope:

```
ObservableRecord (frozen):
  request_type: str          # e.g. "forward_price.v1"
  request_key: str           # canonical hash of (method, args EXCLUDING as_of)
  as_of: datetime            # point-in-time decision clock (blindfold; WALL)
  observed_at: datetime      # when this answer became knowable (bitemporal)
  valid_time: date | None    # what period the answer is ABOUT
  status: OK | NOT_KNOWABLE_YET | ERROR
  payload: <observable value, EXACTLY what the real interface returns>
```

- **The payload is only ever an observable** (a price float, a consumption baseline, a regulatory digest) — never a sim internal. A trace that recorded, say, a churn *parameter* would be a wall breach; the capture tool records **only the return values of `SimInterface` methods**, which is what makes the wall structurally safe (§5).
- **Storage behind the interface (C-S4):** the trace is the append-only event-log abstraction; on-disk form (JSONL now) is swappable without touching replay logic. SIMPLICITY GUARD: a JSONL file, not a repository-pattern cathedral.

---

## 4. Composition with A8's parallel runner (zero edit to A8's file — itself a proof of the seam doctrine)

A8's `tools/tournament_runner.py` is already built to receive this without modification:

1. **Activation by env var, not by a code edit.** `_run_one_life()` passes `extra_env` into each life subprocess. ARCH1 adds one env read — `SIM_RECORDED_TRACE=<path>` — inside `build_sim_interface()` (`company/interfaces/sim_interface.py`): if set, return the mock bound to that trace; else the current behaviour. The tournament caller puts the trace path in `extra_env`. **No edit to `tournament_runner.py`.**
2. **The memory cap is already a parameter.** `default_worker_count(per_life_rss_bytes=...)` and `run_tournament(..., per_life_rss_bytes=...)` already accept the per-life RSS estimate. The mock's much lower measured RSS is passed by the caller as `per_life_rss_bytes=<mock_rss>`; `memory_safe_worker_cap()` then permits many workers. **No edit to `tournament_runner.py`.**

That ARCH1 and A8 compose through **one env var + one existing parameter** — with disjoint `file_scope` — is exactly the "two agents cannot collide in meaning if the seam is typed" claim from the ARCH1 DISCOVER, demonstrated on A8. It also keeps the two atoms concurrency-safe under THREE_LANES (disjoint file_scope).

**Non-negotiable, carried from A8/profile (R15, fail-closed):** a mock/recorded run is a DEVELOPMENT tool — it may **never** publish, promote an atom, or feed the board pack. The `--fast`/`SIM_FAST_MODE` guard already blocks board-pack side effects; the mock inherits it and adds a `SIM_RECORDED_TRACE`-set → **hard-refuse any publish path** assertion (mutation-tested: a recorded run that reaches `process_run_complete` must fail closed).

---

## 5. How it preserves the WALLS (epistemic wall + Historical Ground Truth + determinism)

These are physics, not approvals — the mock must not weaken any of them.

- **Epistemic wall.** The mock is a `SimInterface` implementation; the company still reaches the world only through the seam. The trace contains **only observable return values**, so nothing in it could leak a sim internal even in principle. `tools/epistemic_verifier.py` runs unchanged and must still PASS on the ARCH1 diff (all new code sits in `company/interfaces/**`, the EXEMPT sanctioned crossing, plus a harness capture tool + tests).
- **Point-in-Time Blindfold (WALL).** Every `ObservableRecord` carries `as_of`/`observed_at`. **Replay refuses to serve any record whose `observed_at > as_of` of the query** — the future is unreachable through the mock exactly as through the real interface. This is the single most important safety test and is **mutation-tested**: inject a trace row with `observed_at` in the query's future → replay must raise/return `NOT_KNOWABLE_YET`, never the value (R15 killer pattern: FAIL-OPEN forbidden).
- **Historical Ground Truth (WALL).** The trace is captured from the *real* seeded `LiveSimInterface` over real Elexon/NESO history; it is a *recording* of ground truth, not a re-generation or a tuned surrogate. Capture is blind to company P&L (R13 baseline discipline): the trace records what the world *did*, never adjusted because a variant's results look wrong.
- **Determinism (WALL).** Replay is a **pure function of `(trace, request_key, as_of)`** — it draws **no RNG** (C-S2 substream discipline: a subsystem that consumes zero RNG can never shift another subsystem's draws; this is strictly *safer* than the live path). Given the same trace, every life sees byte-identical exogenous observables. Determinism test: two replays of the same trace produce identical `ObservableRecord` streams; a full run and a mock run seeded identically produce identical *exogenous* observables (the endogenous divergence is the measured gap, §6, not nondeterminism).

**C-S1..C-S5 conformance:**
- **C-S1** (arrival tolerance): replay answers queries one at a time, in any order, keyed by `request_key` — no assumption of batch completeness. Test: shuffled query order → identical answers.
- **C-S2** (idempotency + deterministic replay + RNG substreams): replaying a request twice returns the identical record; zero RNG consumed (above).
- **C-S3** (async wall contracts): the mock honours the same envelope; a recorded `NOT_KNOWABLE_YET` stays `NOT_KNOWABLE_YET` on replay (pending latency is representable, not collapsed to same-step).
- **C-S4** (persistence behind an interface): trace is the append-only log abstraction; JSONL form swappable.
- **C-S5** (time-scale invariance): **declared** — exogenous replay logic is time-scale invariant (it is keyed by `valid_time`/`as_of`, not by step index). The **fixed-world endogenous approximation is the registered exception** (named simplification per R10; see §6).

---

## 6. The gap is the score (COUPLED_TRIAD) — the fidelity limitation, named not hidden

The mock's fixed exogenous world breaks the world→company→world feedback **for endogenous observables**: a variant's aggressive pricing would, in a full sim, raise churn and cut settled volume; against a fixed trace it does not. This is a real fidelity limitation and it is the **gap ARCH1 must measure**, not paper over:

- **Coupled pair:** ARCH1-mock (company runs against a recorded world) ↔ the full `LiveSimInterface` run (company runs against the reactive world). The **gap = |fitness(mock) − fitness(full)|** for the same variant, reported per COUPLED_TRIAD each digest.
- **Use rule (fail-closed):** the mock is licensed for **inner-loop selection/ranking** where relative ordering of variants is what matters and the gap is bounded; it is **never** licensed for a headline/published figure (§4 non-negotiable). If the measured gap exceeds a declared tolerance for a variant class, that class falls back to a full run — the mock reports its own untrustworthiness rather than silently mis-ranking.
- **R10 closure:** the fixed-world approximation is registered as a class-level simplification in the ARCH1 map entry (see FRAME NOTE below), not an instance caveat.

---

## 7. Proposed `file_scope` (disjoint from A8's `[tools, background, tests]` where it matters)

```
file_scope: ["company/interfaces", "tools/observable_trace_capture.py",
             "tests/interfaces"]
```
- `company/interfaces/recorded_sim_interface.py` — the mock (`RecordedSimInterface(SimInterface)`) + `ObservableTrace`/`ObservableRecord` replay. New file.
- `company/interfaces/sim_interface.py` — **one hook only**: `build_sim_interface()` reads `SIM_RECORDED_TRACE`. Minimal, additive.
- `tools/observable_trace_capture.py` — the capture CLI (records a trace from one seeded `LiveSimInterface` run). Harness tool; a **distinct file** from anything A8 touches (A8 owns `tournament_runner.py`, `sim_runner.py`, `autonomous_runner.py`), so the two atoms stay logically disjoint even though both nominally list `tools`. Name this coordination explicitly in the map so the orchestrator serialises only if both are open at once.
- `tests/interfaces/test_recorded_sim_interface.py`, `.../test_observable_trace.py` — wall/blindfold/determinism/idempotency/gap tests.

**No edit to `tools/tournament_runner.py`** (composition via env var + existing parameter, §4) — this is the deliberate disjointness that lets ARCH1 and A8 run concurrently.

---

## 8. Level definitions (L1 / L2 / L3) — `level_target: 2`

**L1 — the mock exists and is wall-safe (single life).**
- `RecordedSimInterface` implements the full `SimInterface` Protocol; `build_sim_interface()` returns it when `SIM_RECORDED_TRACE` is set.
- `tools/observable_trace_capture.py` captures a deterministic exogenous trace from one seeded `LiveSimInterface` run.
- One `--fast` life run against the mock **completes and writes the same fitness JSON shape** as a full life, at **materially lower measured RSS** (the number is the L1 evidence — target: well under the ~5.67 GB full-life figure, into the sub-GB range that lets ≥ (cores) workers fit).
- WALL tests PASS: blindfold mutation test (future `observed_at` → `NOT_KNOWABLE_YET`), determinism (two replays identical), idempotency (C-S2), arrival-order tolerance (C-S1), epistemic_verifier PASS on the diff.
- Fail-closed guard: a recorded run that reaches any publish path refuses (R15 mutation test).

**L2 — the mock composes with A8's runner and moves the memory number (TARGET).**
- The tournament passes `SIM_RECORDED_TRACE` via `extra_env` and `per_life_rss_bytes=<measured mock RSS>`; `memory_safe_worker_cap()` now admits **N > 1** workers where it previously admitted 1 — **measured** worker-count and wall-clock improvement on a real multi-life tournament, no edit to `tournament_runner.py`.
- The exogenous/endogenous split is implemented and the **COUPLED_TRIAD gap is measured** (mock vs full fitness for a sample variant set) and reported.
- The fixed-world approximation is registered as an R10 class simplification; C-S5 exception declared.
- DoD evidence: a before/after tournament run showing worker count > 1 and reduced wall-clock, plus the gap figure, plus green wall/determinism suite.

**L3 — gap-characterised and hardened (aspirational, beyond target).**
- Gap tolerance per variant class calibrated; mock auto-falls-back to full run when a class exceeds tolerance (self-reporting untrustworthiness).
- Trace capture wired to refresh deterministically at world/baseline changes (R13-safe, blind to P&L).
- Expert-Hour / mutation-test coverage on every WALL control (R15). Not required for `level_target: 2`.

---

## 9. Ordered BUILD task list (for when the twin opens ARCH1 BUILD)

1. Define `ObservableRecord`/`ObservableTrace` (frozen, envelope-shaped §3) in `company/interfaces/recorded_sim_interface.py`.
2. Implement `RecordedSimInterface(SimInterface)` — exogenous methods replay from trace (blindfold-gated), endogenous methods run the live fixed-world path. Zero RNG in replay.
3. Add the `SIM_RECORDED_TRACE` hook to `build_sim_interface()` (one branch).
4. Build `tools/observable_trace_capture.py` — seeded capture of one `LiveSimInterface` run to JSONL; records only observable return values.
5. WALL/determinism/idempotency/arrival tests (§5, §8-L1), incl. blindfold + publish-refusal mutation tests.
6. Measure RSS of a mock life vs full life → set `per_life_rss_bytes` used by the tournament caller.
7. Compose with A8: run a multi-life tournament with the trace in `extra_env`; measure workers > 1 and wall-clock (§8-L2).
8. Implement + report the COUPLED_TRIAD gap; register the R10 simplification. → L2 DoD.

## 10. Open questions (for BUILD)

1. **Endogenous boundary precision.** `get_settlement_data` is partly exogenous (metered baseline consumption) and partly endogenous (which MPANs are on *this* variant's book). Split it at the MPAN-membership line: replay the per-MPAN consumption baseline (exogenous), compute the book membership live (endogenous). Confirm at BUILD against `settlement_reconciler.py`.
2. **Trace scope vs. variant space.** One trace covers one world (one seeded history). A tournament that varies the *world* (curriculum, R13 director-owned) needs one trace per world, not per variant — captured deterministically, versioned. Confirm the tournament's world-vs-variant axis before mass capture.
3. **Gap tolerance number.** L3 needs a declared tolerance; L2 only needs the gap *measured*. Defer the threshold to the director/twin (it shades toward a curriculum/fitness value call).
4. **Overlap serialisation with A8.** Both list `tools`; files are disjoint (`observable_trace_capture.py` vs `tournament_runner.py`/`sim_runner.py`). If both atoms are BUILD-open simultaneously, orchestrator serialises on the `tools` prefix out of caution until `H9_map_write_serialisation` lands — note in the map entry.

---

## FRAME NOTE (proposed append to the ARCH1 map `simplifications`, doc-only)

> 2026-07-14 FRAME LANDED (Lane-3, doc-only, `docs/design/ARCH1_FRAME.md`): scoped ARCH1's highest-return slice as a **typed mock at the sim/company seam** (the outer wall), owned lever for A8. Design: a third `SimInterface` impl (`RecordedSimInterface`) that **replays a recorded EXOGENOUS observable trace** (market/weather/regulatory — the ~5.67 GB the company can't see anyway) while the cheap **ENDOGENOUS** book loop runs live; per-life RSS collapses → `tournament_runner`'s memory cap stops throttling parallelism. Composes with A8 via **one env var (`SIM_RECORDED_TRACE`) + the existing `per_life_rss_bytes` parameter — zero edit to `tournament_runner.py`** (disjoint file_scope, itself a proof of the seam doctrine). WALLS preserved: mock is a seam impl (epistemic wall intact, verifier unchanged); replay is blindfold-gated (`observed_at>as_of`→`NOT_KNOWABLE_YET`, mutation-tested) and draws **zero RNG** (determinism strictly safer, C-S2). **Named class simplification (R10):** the fixed exogenous world breaks the price→churn→volume feedback for endogenous observables — licensed for inner-loop ranking only, NEVER publish (R15 fail-closed), with the mock-vs-full **gap measured per COUPLED_TRIAD**. C-S5 exception: fixed-world endogenous approximation. Proposed `file_scope: ["company/interfaces", "tools/observable_trace_capture.py", "tests/interfaces"]`; L1=wall-safe single life at sub-GB RSS, L2 (target)=composes with A8 + gap measured, L3=gap-characterised auto-fallback. BUILD-ready; twin can open.
