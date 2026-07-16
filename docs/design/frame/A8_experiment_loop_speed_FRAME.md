# A8 — Experiment-loop speed (FRAME)

**Atom:** `A8_experiment_loop_speed` (lane `H_harness`, epoch 2, L2→3, `loop_stage: idle`)
**Stage:** FRAME (Lane-3 DISCOVER/FRAME, doc-only, **NO LEVEL MOVE** — an idle/BUILD-gated atom's
gap to L3 is closed by BUILT code the epoch gate defers; a doc cannot move it. Level **HELD at 2**.)
**Depends on:** `ARCH1_internal_seams` (the typed wall seam must be wired into the real run path before
A8's biggest lever is buildable — see §4).
**Author:** H17 Lane-3 governed fork, 2026-07-16. Grounded by reading `tools/tournament_runner.py`,
`tests/tools/test_tournament_runner.py`, `docs/observability/experiment-cycle-profile.md`, and re-verifying
the ARCH1 wiring state on disk this turn (R7): `grep -rn build_sim_interface saas/ company/ sim/ tools/`
returns only the definition + a tournament_runner docstring — **zero run-path callers**; and
`saas/reporting/annual_report.py` (what each tournament life subprocess actually runs) has **zero**
`SimInterface`/`build_sim_interface` references. No BUILD code; no map edit (F1 — level recorded via
`docs/design/atom_status/A8_experiment_loop_speed.yaml`).

**Why this FRAME now (the named gap it fills):** A8 is heavily worked — three landed in-scope levers,
a rich simplifications log — but it has **no consolidated FRAME artefact and no explicit L3
Definition-of-Done**. The atom's own log states it directly: *"No explicit L3 DoD text exists for this
atom to check off; per the honesty wall, level_current is left at 2."* That missing DoD is a real
framing gap, not treadmill churn: without it, every A8 BUILD re-draw re-derives "what does done mean
here?" from scratch (it has done so ~4× on 2026-07-16 alone, each concluding "held at 2"). This FRAME
fixes the DoD in one place so the next BUILD — once ARCH1 unblocks it — can close cleanly against a
written bar. That is the loop-shortening contribution (COMPOUNDING_WORK_FIRST): the atom whose whole
purpose is making experiments cheap should not itself be expensive to close.

---

## 1. The gap this atom owns (one sentence)

A full single-threaded sim life costs ~500s, so a 10,000-life Epoch-4 evolutionary tournament is
~58 days of wall-clock; feasibility (10k lives in a week) needs ~60s/life — an **~8–10× cycle-time
reduction** — and until that gap closes the Epoch-4 fitness function is arithmetically un-runnable
(`docs/observability/experiment-cycle-profile.md`, MEASURE-FIRST per R4).

## 2. Why it is distinct from its neighbours (no overlap)

- **ARCH1_internal_seams** owns the *typed wall interface* (`company/interfaces/sim_interface.py`,
  `build_sim_interface()` → `RecordedSimInterface` on `SIM_RECORDED_TRACE`). ARCH1 owns the **seam and
  its wiring into the run path**. A8 owns **consuming** that seam to replace a full sim run with a
  mock/replay in the tournament inner loop. A8 cannot build its biggest lever until ARCH1 wires the
  seam — this is the `depends_on` edge, verified unwired this turn.
- **The Epoch-4 fitness function** (director-reserved, one-way door, values decision) owns *what the
  tournament optimises for*. A8 owns only *how fast a life runs*, and is fail-closed against ever
  touching fitness: a fast/mock run may never publish, promote an atom, or feed the board pack, and
  cycle time is a diagnostic never gamed by deleting tests (R15 stands, R12 anti-goal-seek).
- **CI / the test suite** owns correctness gating. A8's tiered-test lever culls *tournament candidates*
  cheaply before the expensive tier; it never culls the *correctness* suite (which runs in full once
  per integration, unchanged).

## 3. The lever inventory — what A8 owns, and its status (grounded on disk this turn)

A8's own registered simplification names four levers. Their honest state:

| # | Lever | Owner / scope | Status (2026-07-16) |
|---|-------|---------------|---------------------|
| 1 | **Parallel sim + self-calibrating worker cap** | A8 (`tools/tournament_runner.py`) | **LANDED.** Probe wave measures real child RSS via `getrusage(RUSAGE_CHILDREN)`, recomputes worker cap from the measurement (no manual `per_life_rss_bytes` tuning). Measured 1→3 workers, 3.5× wall-clock on this box; byte-identical fitness. Named limitation (R10): `ru_maxrss` is a per-process monotonic high-water mark — accurate for the first life a fresh process/worker reaps, not for a later same-process life; a long-lived in-process caller calibrates only on its first call and otherwise fails closed to the caller's figure (never a false low). |
| 2 | **Tiered tests (SCREEN → FULL)** | A8 (`tools/tournament_runner.py::run_tiered_tournament`) | **LANDED** (`87f84f4a8`, folded `65136bc04`). A cheap SCREEN tier culls the bottom candidates before the expensive FULL tier; fail-closed R15 (survive_fraction ∉ (0,1] refused; a screen-failed life can never reach FULL; publish-path output-dir guard fires); deterministic C-S2 (pure score-desc/id-asc sort, no RNG). E2E verified: screen culled 4 of 6, FULL ran only 2. |
| 3 | **Mock-interface composition (capture-once, replay-per-life)** | ARCH1 seam + A8 consumer | **BLOCKED on ARCH1.** The single biggest lever (500s → seconds). Unbuildable until `build_sim_interface()` is wired into the `annual_report` run path — currently a no-op on the real path (verified this turn). |
| 4 | **Deterministic-stage caching** | run-path (`saas.reporting.annual_report`) | **OUT OF A8's file_scope.** Caching a shared deterministic prefix across lives requires `annual_report` to accept/read a cache input — a run-path change like lever 3, not in `tools/background/tests`. |

**Rejected (SIMPLICITY GUARD, logged so it is not re-proposed):** a persistent in-process worker pool
to avoid per-life interpreter startup — it would trade away the subprocess isolation that guarantees
C-S2 per-life RNG determinism and clean `RUSAGE_CHILDREN` measurement. Correctness-wall regression, not
a clean win.

## 4. Why the level is HELD at 2 (the honesty wall)

The two in-scope levers (1, 2) are built, mutation-tested, and settled. But A8's headline is the
~8–10× feasibility gap, and levers 1+2 together do **not** close it: parallelism gives ~3–4× bounded by
cores/RAM, and tiering cuts *N* for the expensive tier without turning a 500s full life into seconds.
The two levers that *would* close it (3 mock composition, 4 caching) are **wholly outside A8's
`tools/background/tests` file_scope** and blocked on ARCH1 wiring the seam into `annual_report`. So no
honest in-scope L2→L3 move exists; the level stays 2. This is a **technical dependency, not a one-way
door** — no escalation; A8 stays DISCOVER/FRAME-workable while parked (EPOCH_GATING), and re-opens to
BUILD the moment ARCH1 wires `build_sim_interface()` into the `annual_report` run path.

## 5. The explicit L3 Definition-of-Done (the missing bar this FRAME supplies)

L3 ("Working / real, tested through the coupled loop") for A8 is met when **all** hold:

- **D1 — feasibility met, measured not asserted:** a genuinely-fresh end-to-end measurement shows
  effective per-life cost ≤ ~60s (equivalently: a 10k-life tournament projects to ≤ ~1 week on this
  box), reproduced before/after in the same before/after style already used for lever 1. The number is
  a measured `wall_clock_s`, never a target tuned toward (R12).
- **D2 — the mock lever is actually wired and consumed:** the tournament inner loop obtains its
  exogenous world through the `SimInterface` seam (ARCH1 wired), and a life can `capture-once` + replay
  without a full sim run — proven by a run-path test, not a docstring.
- **D3 — fidelity preserved (fail-closed, R15):** a mocked/fast life produces **byte-identical
  fitness** (`total_net_gbp` / whatever the Epoch-4 fitness reads) to the full life for the same seed,
  or the divergence is a named, bounded, R10-registered simplification — never a silent one. A
  mutation test proves the fast path cannot publish, promote an atom, or feed the board pack.
- **D4 — determinism + replay (C-S2):** the same tournament seed reproduces identical survivor sets
  and identical per-life fitness across serial, parallel, and tiered modes (already true for 1+2;
  must remain true with the mock path added).
- **D5 — the coupled triad is closed (COUPLED_TRIAD):** the speed-up is demonstrated *on the actual
  Epoch-4 tournament shape it exists to enable*, not only on a synthetic micro-bench — i.e. A8 has
  faced the workload that can defeat it and the belief-vs-truth gap (projected vs realised wall-clock
  at tournament scale) is reported.

**Anti-DoD (what does NOT count as L3, per R15/R12):** deleting or thinning the correctness suite;
lowering fidelity to hit D1; a projected/extrapolated speed-up not measured end-to-end; a green mock
path that was never wired into the real run path (D2 is the guard against exactly the current no-op
state).

## 6. Coupled-triad framing

A8 is a HARNESS-lane atom, so its "world" is the **experiment workload itself**. The triad reads:
SIM/COMPANY add the depth that makes a life expensive (population, weather physics, billing) →
the tournament must run 10k such lives → A8 measures and closes the **cycle-time gap** between the
naive cost and the feasible budget. The gap reported each digest is *projected-vs-realised wall-clock
at tournament scale* (D5). A8 completing lets Epoch-4 exist; Epoch-4's fitness function (director's)
is what defeats or validates it.

## 7. Scale-readiness / portability notes (constraint, not build)

- **C-S2 (idempotency + deterministic replay):** central to A8 — the subprocess-per-life isolation is
  *kept precisely because* it guarantees per-life RNG substream determinism and clean RSS measurement
  (the reason the in-process pool was rejected, §3).
- **C-S5 (time-scale invariance):** A8's logic is a per-life cost measurement — time-scale invariant by
  construction; no exception to register.
- **Portability:** the tournament runner hardcodes no counterparty and no clock speed; the mock lever
  (when wired) consumes the same typed seam a real endpoint would sit behind, so a second
  market/product fits the harness unchanged.

## 8. What a future BUILD does with this doc

When ARCH1 wires `build_sim_interface()` into the `annual_report` run path, re-open A8 (`loop_stage
idle → build`) and BUILD lever 3 (capture-once + replay-per-life) against the §5 DoD. Close only when
D1–D5 all pass with quoted measured evidence. Deterministic-stage caching (lever 4) is a separate
run-path atom, not A8's, unless its file_scope is widened by the director.

---

*Sources: `tools/tournament_runner.py` + `tests/tools/test_tournament_runner.py` (levers 1–2, landed);
`docs/observability/experiment-cycle-profile.md` (the ~8–10× measurement); `docs/staging/done/
COMPOUNDING_WORK_FIRST.md` (why A8 was the one authorised past the moratorium); A8's own simplifications
log (four 2026-07-16 turns); `company/interfaces/sim_interface.py` + `saas/reporting/annual_report.py`
(ARCH1 wiring state, re-verified unwired this turn per R7).*
