# WORKER FINDING — a perturbation control's fidelity cannot be its compound effect, and its disclosure cannot live in the branch that never fires

Filed 2026-08-11 by the worker tick that drew `H_GAP_fabric_belief_truth_gap` (L2->L3).
Landed: `696dcf06e` (mechanism + 6 R15 mutations), `bc0d65735` (ledger re-stamp).
Rank: backlog. Nothing here blocks; it is a CLASS worth applying at the next touch of any
control shaped like a mirror.

## The shape, in one line

A control that perturbs a world and reads what moves must state how much of the movement
was **the instrument**. If that statement is computed over the whole effect, it is large
exactly when the control WORKS — and if it is rendered only in the branch where the
control fired, it is missing in the only case that occurs.

## What was actually wrong (observed, with evidence — run, not read)

`background/fabric_gap_ledger.py` mirrors the fabric panel three ways and asks whether the
money verdict survives. The **panel mirror** reflects SIM truth through the company's EPC
register: same error magnitudes, opposite signs. Its disclosed fidelity figure was
`panel_mirror_accuracy_drift` = how far the *improvement* (epc gap − inferred gap) moved.

1. **The compound.** Reflecting the truth is *meant* to wreck the posterior arm — an
   inference that stepped the right way on this panel steps the wrong way in a stock that
   fails the other way; that is the finding, not the noise. So the disclosed number is
   large precisely when the mirror is working (0.1579 authored, 0.0717 drawn) and it can
   never come out small. Read as "how much the instrument disturbed the measurement", it
   made a working mirror look broken — which is exactly how the previous Expert Hour read
   it, filing the mirror as a weak instrument.
   The artefact is the **register arm alone** — the arm the reflection is built around,
   whose error the mirror claims to preserve: 0.0065 / 0.1104 under the old reflection.

2. **A design justification nobody measured.** The reflection was `pivot**2/value`
   (log-preserving), defended in its own docstring because the level-preserving
   `2*pivot − value` "goes non-positive whenever the reflected quantity exceeds twice its
   pivot, which is common in a register — a mirror that raises on a third of real panels
   is a control nobody can run." Measured on the two populations this atom publishes:
   **0 of 15 and 0 of 200 premises infeasible.** A register that under-states by 13–20%
   does not under-state by more than half. `prediction_gap`'s numerator is a mean ABSOLUTE
   error, so the log form left the register arm's own numerator moving under a mirror
   whose whole claim is "same magnitudes". Switching: numerator identical to 6 decimals
   (0.020202 / 0.044774 before and after), drawn artefact 25.9% -> 1.9% of its gap.
   The entire remaining residual is the **no-skill denominator** — a property of the truth
   population the reflection moves. That is a statement about the metric, and it is now a
   named one instead of the word "approximately".

3. **The orphaned disclosure.** The fidelity figure was rendered only inside the
   `COMPOSITION-DECIDED` caveat — which prints only when the mirror FLIPPED the verdict.
   It flips on **neither** published population. So every reader of both real rows saw two
   headline numbers, no composition caveat, and an invitation to conclude that composition
   had been ruled out, while on the authored panel the mirror had disturbed the register
   arm by 14.1% and its null meant nothing. *A null result from an uncalibrated instrument
   is not evidence of no effect.*

## The generalisation (R10 — apply at next touch, do not retrofit speculatively)

Any control of the form "perturb X, see whether the verdict survives" needs three things
its author will not miss the absence of, because a green test says nothing about them:

* **Split intended from artefact.** The perturbation is designed to move something; the
  fidelity statement must be computed on the part it is designed NOT to move. Pin it with
  a test that moves ONLY the intended part and asserts the artefact term does not move.
* **Preserve the quantity the downstream metric consumes.** A reflection that preserves
  the log error feeding a metric built on absolute error is faithful to a quantity nobody
  reads. Check what the metric divides by, too: normalising by a property of the perturbed
  population puts an irreducible residual in the control, and it should be named.
* **Render the fidelity on the NULL branch.** A control whose self-assessment appears only
  when it fires is silent in the case a reader is most likely to over-interpret.

## Mechanised here (not exhortation)

`panel_mirror()` returns the reflection it used and the infeasible count (whole-panel
fallback, never per premise — a panel reflected two ways on two subsets is two
instruments); `panel_mirror_epc_gap_drift` / `panel_mirror_relative_infidelity` /
`panel_mirror_is_attributable` ride in the ledger row unconditionally; the 2x2 of
flip x fidelity is complete and each cell is pinned, including the silent one.
R15 both ways on the two REAL populations — the caveat fires on the authored 15 (14.1%,
above the 5% band) and stays silent on the drawn 200 (1.9%) — plus six source mutations
each firing their own named test with md5 byte-clean restore.

## What was NOT fixed, and is not a defect to fix

The panel mirror is only readable where the register's error is small against the truth's
spread; the artefact scales with that ratio, so a high-error population self-reports
inconclusive (the suite's own ±25% fixture measures 28.0%). That is a true limit of
reflecting a truth population through a belief, not a band to widen. Recorded on the atom.
