<!-- SUPERVISOR_DRAW: self-drawable -->
# [PLANNER-MINTED] — Bad-debt reconciliation bridge (report-first) (2026-07-25)

**Type:** RUNG-7 planner mint (propose-then-proceed), authorised by `DIRECTOR_RULING_WORK_IS_THE_DEFAULT_2026-07-23`
(minting the next step of a ratified goal is expected; resting instead is the breach).

## What ratified goal / ledger row / campaign this serves

- **Ratified steer:** `docs/staging/in_progress/DIRECTOR_STEER_DUNNING_DEBT_PROVISIONING_2026-07-25.md`
  (director design-session output, 2026-07-25). This mint is its **§5 sequencing step-1** — the single
  dependency-forced, non-walled, buildable-now next step. Steer §5: *"Reconcile before building … the
  four expected-loss numbers must be brought into one place and their disagreement quantified — as the
  revenue bridge did — before any new provisioning mechanism is chosen."*
- **Steer decisions absorbed:** **D3** (bad debt requires a three-clock reconciliation bridge on the
  same standing as the revenue bridge; R14 already binds "no figure without its clock") and **D2**
  (the provision-to-realised-loss **variance** is a first-class measured quantity — same status as the
  coupled-triad gaps: measured, published, never tuned away).
- **Fidelity-ledger row served:** the ledger today carries `live_payment_detection_gap` but **no**
  bad-debt / provisioning-variance row. Steer §F3: *"Revenue has a bridge. Bad debt has none."* This
  mint closes that by (a) building the bridge and (b) registering the provision-vs-realised variance as
  a new fidelity-ledger row.
- **Structural precedent (proven pattern, not new construction):**
  `docs/staging/done/MARGIN_REALISM_E2_TWO_PIPELINES_FINDING.md` — the two-revenue-pipelines defect
  (26–52%/yr disagreement) closed by a reconciliation bridge. Bad debt is the same defect class, unbridged.

## Real-world fidelity gained

A UK supplier's published bad-debt line is only meaningful as **estimate-vs-realised variance across
the settled/billed/banked clocks**. Today the live method is a flat contra-revenue haircut
(`saas/payment_behaviour.py::bad_debt_provision_gbp`) that is *structurally incapable of being wrong*
(steer §F1): the estimate sits on the billed clock, the realised outcome
(`simulation/arrears_engine.py::compute_emergent_bad_debt`) sits on the settled clock, cash sits on the
banked clock, and **nothing reconciles them** (§F3). After this step the P&L's bad-debt figure carries
its clock and its measured error — the same honesty the revenue bridge already gives revenue.

## Scope (report-first; no published figure moved in this step)

1. **Locate the four expected-loss numbers** (steer §F3): (1) flat haircut — live, billed clock;
   (2) aging matrix `company/finance/bad_debt_provision.py` — unwired; (3) stage recovery probabilities
   `company/finance/debt_collection.py` — unwired; (4) `arrears_engine.compute_emergent_bad_debt` /
   `apply_emergent_bad_debt` — the realised outcome, settled clock, carried through treasury.
2. **Quantify their disagreement** per year across the three clocks and publish it *before changing any
   figure that feeds a surface* (steer §6 inline mitigation: "a bridge that explains the gap is safe; a
   corrected number that moves the front door is not, until the gate is green").
3. **Register the provision-vs-realised variance as a fidelity-ledger row** (D2) — measured, R12
   diagnostic-not-target, never tuned toward a benchmark.
4. **R15 both ways:** the variance control must be able to FAIL — a mutation that zeroes realised loss,
   or that makes the estimate track the outcome tautologically, must trip it (a company that *believes*
   it provisions perfectly is a wider hidden gap wearing a better number — steer §D2).

## Explicit non-scope (walls — do NOT cross in this mint)

- **No provisioning-method selection** (IFRS-9 simplified vs incurred-loss, fixed baseline vs R13
  curriculum dial) — steer **R-1**, director-reserved.
- **No dunning harm-cost ratio** (R-2), **no write-off-timing policy** (R-3), **no
  disengaged-majority curriculum call** (R-4), **no holdout/uplift machinery** (R-5) — all reserved.
- **No collections action** — steer **D5**, detection stays sensing-only.
- **No wiring of the aging matrix or dunning ladder as the live method** yet — that is §5 step-2/3,
  two-way-door downstream of this reconciliation landing and being read. Retire-or-wire the unwired
  modules (**D4**) is decided *by* the reconciliation, not ahead of it.
- **No change to a published financial figure** in this step — report the disagreement first; moving
  `net_margin_gbp` / EV / the margin-bridge remainder waits until the gate is green (steer §6 blast-radius).

## Propose-then-proceed window

Report-first reconciliation + a fidelity-ledger row + an R15-failable variance control is the steer's
own **"just do it"** proportionality tag (§6: "reconciliation and measurement = just do it"). It touches
no one-way door, moves no published figure, and crosses no reserved wall. **Proceed by default**;
proceed-window closes if a director ruling on R-1 (method) lands first and reframes the base. Expect the
publish-gate stale-test wedge pattern on ledger dependents (steer §6) — run the full gate, treat the
four-wedge pattern as anticipated, not a surprise.

*RUNG-7 planner mint, 2026-07-25. One mint, not a padded batch: §5 steps 2-4 are dependency-blocked
downstream (two-way-door filter) and R-1..R-5 are director-reserved — the reconciliation bridge is the
sole clean un-minted non-walled next step, so LAW A / R12 forbid minting duplicative downstream docs to
hit a count.*
