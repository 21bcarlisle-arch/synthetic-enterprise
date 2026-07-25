# Run manifest/ledger + three scores + coverage report — BUILD RECORD (2026-07-25)

Actions the ruling `DIRECTOR_RULING_POPULATION_ACTIVATION_AND_RUN_LEDGER_2026-07-25.md`
(tag: **activate + build manifest/ledger; §6 registered only**). This tick built the
ADDITIVE infrastructure the ruling names — the pieces that must exist *before* the
flag-flip activation, because §1 condition 3 forbids any derived figure publishing until
a coverage report has passed, and §4 cannot judge a run without the ledger row.

## Sequencing (why infra first, not the flag flip)
`live_population.py`'s own docstring already required it: "Downstream entrypoints must be
hardened to tolerate the SYN shape BEFORE the flag is flipped on", and §1.3 requires the
coverage report first. So the honest build order is: manifest/ledger + scores + coverage
report NOW (additive, low-risk, testable in isolation); the flag flip + ~19 entrypoint
rewiring + SYN-shape hardening + downstream re-baseline is the gated held core (below).

## BUILT this tick (additive, tested, epistemic PASS)
- **§3 run manifest/ledger** — `background/run_manifest.py`. `RunManifest`/`RunOutcomes`
  carry every field the ruling names (run_id, code SHA, curriculum version, world scenario
  + true-probability tag, population seed + realised cell counts, outcomes incl. death
  cause/date, EV, £/tCO₂e, worst-cell fidelity). Append-only JSONL ledger
  (`docs/observability/run_ledger.jsonl`). §3 retention policy: every death retained full,
  fidelity-flagged retained full, deterministic survivor sample, else row-only.
- **§4 three scores** — same module. `robustness` (UNWEIGHTED worst-tail EV), `commercial_ev`
  (true-probability-WEIGHTED), `survival` (UNWEIGHTED worst-case: dies anywhere → fail).
  Returned as `ThreeScores` kept **separate — no blended scalar by construction**.
- **§4 R15 guard (mutation-tested both ways)** — `assert_homogeneous_basis` /
  `aggregate_scores` raise `MixedBasisError` the instant scores of differing basis meet;
  `commercial_ev` refuses a ledger containing any row without a true_probability (an
  unweighted row cannot silently enter a weighted score). Proven both ways in
  `tests/background/test_run_manifest.py` — drop the check and the tests go red.
- **§1.3 coverage report + publish gate** — `simulation/population_coverage.py`. Realised
  cell counts per curriculum axis vs the drawn population; thin/absent cells reported, never
  smoothed; `coverage_gate_ok()` returns False for a thin draw so the held activation must
  BLOCK publication. `tests/simulation/test_population_coverage.py`.
- **§5 non-domestic book audit (evidence-based, one line)** — see below.

## §5 — what non-domestic business exists in the book TODAY (evidence)
The live book is **24 accounts: 15 domestic (resi), 4 SME, 5 I&C** (by the `segment` field
on `saas.customers`). Non-domestic = **9 of 24 (37.5% by count)** — a real, non-trivial
presence. Per §5 this must report its P&L **separately** and may never silently carry or
sink the domestic survival story; market-segmented survival criteria are an epoch-2 item,
not built now.

## Coverage report — the report immediately did its job (real finding)
Running the coverage report on the director's N=200 knee (λ≈40 over 2021–25 → **N=198**)
`coverage_gate_ok = False`, because:
- `region` has **one** realised category — `UNKNOWN_SYNTHETIC` (the placeholder;
  a pre-existing, documented R10 gap: `population_draw.py` has "NO anchored population-level
  REGION distribution" and emits a placeholder). The curriculum *does* carry a
  `region_marginal_synthetic_acquisitions`, but the draw path pins the placeholder, so the
  realised region axis is degenerate.
- `heating_fuel:oil` realised **count 1** (thin).

**This is the report working as specified** — a thin/incomplete draw is caught and blocked,
not averaged away. It also surfaces a concrete precondition for activation: the SYN region
draw must be made real (wire the curriculum region marginal through `iter_acquisition_events`)
before an activated run can publish any derived figure. Registered below.

## REGISTERED — held / not built (the gated core + §2 + §6)
1. **Activation core (§1)** — self-drawable BUILD now that the ruling authorises it, but
   gated: (a) make the SYN region draw real so the coverage gate can pass; (b) harden the
   ~19 `run_phase*`/`annual_report` consumers for the SYN key set; (c) parameterise N
   (λ≈40 → N≈198 is the pre-measured recipe for the N=200 knee; a proper `target_n` is
   cleaner); (d) wire `live_population()` into the entrypoints + `coverage_gate_ok()` into
   the publish gate; (e) flip `SE_DRAW_POPULATION=1`; (f) re-baseline downstream, gated by
   the coverage report; historical comparisons that straddle the change marked, not
   silently continued. Director's retained option: an N=50 smoke proving-run first (figures
   publish nowhere).
2. **§2 stratified run rotation** — world scenario × population seed grid; randomness inside
   a cell, never in the choice of cell. Scenario values + the true-probability tags remain
   **R13 director-reserved** — this build wires the *mechanism*, never authors the values.
3. **§6 survival-usefulness** — margin of survival / breaking strain / cause attribution.
   **REGISTERED ONLY**, director-session gated; do not build ahead of his session on it.

## Verification
- 21 new tests green (`tests/background/test_run_manifest.py`, `tests/simulation/test_population_coverage.py`).
- `tools.epistemic_verifier`: PASS (525 files, no barrier violations).
- Real evidence produced: coverage report on N=198 draw (gate=False, finding above);
  three scores on 100 historical `run_history.json` rows (robustness £1.52M worst-decile
  tail, survival 1.0, commercial_ev correctly REFUSES — no true_probability on legacy rows).
