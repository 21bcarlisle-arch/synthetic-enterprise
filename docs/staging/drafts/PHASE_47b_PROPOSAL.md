# Phase 47b — Cap-Aware Acquisition Gate

**Status:** Draft proposal — REVIEW_GATE. Will auto-proceed after 4h if no redirect.

---

## Context

Rich flagged: zero acquisitions 2021-2025 despite 5 churns. Investigation found:
- 5 acquisition attempts fired correctly (1 per churn)
- 0/5 won — 32.8% probability with static 20% win rate (not a bug)
- **Model gap identified:** win rate is static regardless of economics

In reality, UK resi acquisition economics become unfavourable during the cap era:
- 2021-2023: Ofgem cap makes every new resi customer loss-making at signing
- Real suppliers paused new domestic customer acquisition (Octopus, EDF, BG all did this)
- CLV of a new resi customer acquired in 2022 at cap-constrained unit_rate = highly negative

The current model fires acquisition attempts at the same 20% rate in 2022 (loss-making) as in 2018 (profitable). This is economically unrealistic.

---

## Proposed Change

**One-way-door check:** This is a two-way door — we can adjust the win rate logic without
breaking existing deterministic outputs (the seeds remain unchanged; we're adding a gate
before the roll, not changing the roll itself).

### Approach

Add an acquisition gate to `simulation/run_phase2b.py`:

Before calling `roll_acquisition(segment, acq_seed)`, compute:
1. `projected_resi_margin = expected_unit_rate - company_fwd - (policy + network + capital)`
2. If `projected_resi_margin < 0` and `segment == "resi"` → skip acquisition attempt entirely
3. Log the gate decision: `{date, cid, reason: "cap_constrained", projected_margin: X}`

This means:
- 2016-2020: acquisition proceeds normally (profitable resi)
- 2021-2023: cap bites → projected margin often negative → gate fires → no acquisition attempt
- 2024+: cap loosens, wholesale normalises → margin recovers → acquisition resumes

**Why margin-based rather than year-based:**
- The company doesn't "know" the cap era is happening — it observes its own economics
- If cap is £305/MWh (2022) but company_fwd + costs = £340/MWh, projected margin = -£35/MWh
- Company wouldn't acquire a customer it expects to lose money on
- This is the company deciding based on observable economics, not SIM internals

### Files

- `simulation/run_phase2b.py`: add gate before `roll_acquisition()` in churn block
- `saas/growth_mandate.py`: add `should_attempt_acquisition(projected_margin, segment)` helper
- `tests/simulation/test_phase47b_acquisition_gate.py`: 6-8 tests

### Expected outputs

- 2021-2023: zero resi acquisition attempts during cap years (gate fires)
- 2024+: attempts resume as margins recover
- `acquisition_spend_events` still records gate decisions with reason field
- No change to non-resi (I&C, SME) acquisition logic

---

## Test plan

1. Gate fires when projected margin < 0 (resi only)
2. Gate does NOT fire for positive-margin years
3. Gate does NOT fire for I&C/SME customers
4. `acquisition_spend_events` records gate reason
5. Determinism: same seed always produces same gate/roll outcome

---

## Fidelity delta

During the energy crisis (2021-2023), UK suppliers stopped acquiring domestic customers
because the economics were negative under the cap. The SIM now reflects the rational
company decision not to pursue loss-making acquisition. Crisis → portfolio shrinks
(churns with no replacement). Recovery → acquisition resumes naturally.

**Rich's steer:** "ballpark + components right" — this achieves realistic acquisition pause
during the cap era as an emergent property of economics, not a hard-coded rule.
