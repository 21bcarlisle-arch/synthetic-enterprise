<!-- [CC PROCESSING STATUS — 2026-07-23 NIGHT] STEP 1 DONE (the target), steps 2–4 OPEN.
  STEP 1 (characterise the real tail, read-only, blind to P&L — R13): LANDED. `sim/ssp_tail_target.py`
  computes the empirical real SSP tail over the MODEL's own window (2016-03-01..2025-06-07, n=162,507)
  directly from the ingested Elexon record; emitted to `docs/design/spike_tail_real_target.json`.
  Confirms + extends the G4 ledger: max £4,037.80, frac_negative 0.02218 (ledger 0.02241 ✓), p95 £227
  (ledger 220 ✓), AND the exceedance curve the ledger lacked (>£200: 6.6%, >£500: 0.38%, >£1000: 0.044%,
  >£2000: 0.023%). R15 on the TARGET itself (tests/sim/test_ssp_tail_target.py, 5 tests): FAIL-CLOSED —
  an empty/uncomputable distribution RAISES (never a silently-zero pass); shape maths proven on a
  synthetic; ledger-consistency asserted on the real cache. This gives T1 its missing numeric target.
  STEP 2 (locate the truncation) — recon done: the ~£574 ceiling is NOT a clip to remove; it is the
  emergent ceiling of the OLS 3-feature (gas/demand/wind) regression (run_phase3b) with no scarcity/BM-
  spike term and no explicit negative-price process. The structural scarcity multiplier that would lift
  the tail already exists but is GATED OFF (sim/price_engine.py:162). STEPS 3–4 (reshape the generator +
  prove the residual bites, T1/T2/T3) — NOT blind-landed in an unsupervised night tick (the ruling's
  "tired mega-turn" bar): a baseline-world generator change (R13) deserves a supervised build. Defect
  stays `open` and drawable (register invariant: a characterised target does NOT close the gap). -->

# [PROPOSE-THEN-PROCEED] Spike-tail attack plan — the SSP residual settled at the wrong tail

**Minted:** 2026-07-23, RUNG 4 (declared-defect backlog) of the WORK-SOURCE HIERARCHY
(DIRECTOR_RULING_WORK_IS_THE_DEFAULT + NIGHT_ENFORCEMENT). Seed ordered by the night ruling §2.
**Register entry:** `docs/design/DECLARED_DEFECTS_REGISTER.yaml` → `SPIKE_TAIL_SSP_RESIDUAL` (priority 1, open).
**Window:** propose-then-proceed, normal window; reversible SIM machinery (curriculum values stay director-gated, R13).

## The gap (belief vs truth — grounded, not asserted)

The imbalance-price (SSP) distribution the residual position settles against is understated in the tail:

| metric | model | real (Elexon Insights) |
|---|---|---|
| max SSP | **£574/MWh** | **£4,038/MWh** (peak £4,000.00 exactly, 8 Jan 2021 SP39) |
| negative-price fraction | **0.013%** | **2.241%** |

Source: G4's fidelity ledger; SSP peak confirmed against the Elexon Insights API to ~1%.
**Why it matters (the roadmap item served):** the company hedges in blocks and consumes a half-hourly shape;
the residual is settled at SSP — *where the spike tail becomes commercially real*. A too-thin tail means the
world **cannot bite the company the way 2021–22 bit real suppliers** (cash-not-P&L collateral shock, the mode
that actually killed suppliers). This is the load-bearing WVC/scenario-spine coupling; it is not cosmetic.

## The attack (proposed sequence — smallest closed loop first, R4)

1. **Characterise the real tail** (read-only, no world change): from the Elexon SSP record already ingested,
   compute the empirical tail — max, the negative-price fraction, and the shape between (e.g. the 99th/99.9th
   percentiles and the exceedance curve above ~£200/MWh). This is the *target*, blind to company P&L (R13/R12).
2. **Locate the truncation in the generator**: find where the SIM's imbalance/SSP path is formed and identify
   the mechanism capping it at ~£574 and starving negatives (a clipped distribution, a missing scarcity term,
   or a smoothing step). Name the nearest working analogue and state the diff (R4).
3. **Fix the tail's SHAPE, not a number** (R10, R12): extend the generator so max, negative-fraction, and the
   exceedance curve match real *within the ledger's stated tolerance* — because the physics produces a heavier
   tail (scarcity pricing / negative-price surplus floor), never tuned toward the figure. Ties to `SPINE_5_tail_machinery`.
4. **Prove the company feels it**: show the company's residual-at-SSP exposure MOVES under the corrected tail
   (a coupled-triad measurement — belief-vs-truth gap on the residual P&L, not just the price series).

## R15 obligations (failable controls, built WITH the fix — a control that cannot fail is worse than none)

- **T1 tail-fidelity test** — asserts model {max, neg-fraction, exceedance-above-£200} match the G4 ledger
  within tolerance. **Killer mutation:** re-introduce the ~£574 clip → T1 FAILS. FAIL-OPEN guard: a missing/empty
  ledger figure is a FAILED check, never green.
- **T2 no-goal-seek guard (R12)** — the tail parameters load from the physics/calibration path only; a test that
  a value derived from a company-P&L run is REJECTED (no write-back path). The R13 wall made mechanical.
- **T3 residual-bites test** — a fixed-seed run shows the company's SSP-residual exposure is materially different
  (non-trivially larger tail risk) under the corrected vs the truncated tail. **Killer mutation:** neutralise the
  tail in the residual path → T3 FAILS.
- **C-S2 replay:** the corrected generator draws from its own named seeded substream; a fixed-seed history replays
  byte-identical outside the changed tail (no accidental cross-subsystem RNG shift).

## Closes the register entry when

`SPIKE_TAIL_SSP_RESIDUAL` moves to `status: closed` ONLY when T1 passes (tail re-measured within tolerance)
AND T3 passes (residual exposure shown to move) — never on this plan existing. Until then the defect stays
drawable as rung 4; the loop is idle beside it at its peril (ruling).

**Risk & proportionality:** reversible SIM generator change with named failable tests; baseline-fidelity reason
only, decided blind to P&L (R13). Tag: **proceed, tests-first.**
