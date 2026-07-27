# [DIRECTOR-RULING] — Harness exit criterion RATIFIED. N=3. Two decisions attached, one problem returned. (2026-07-27)

**Type:** [DIRECTOR-RULING] via advisor bridge. Ratifies `docs/design/HARNESS_EXIT_CRITERION_PROPOSAL_2026-07-27.md`.

## 1. RATIFIED as proposed

> **The harness is "done for now" when THREE consecutive product-content atoms each reach their next director-ratified level with their declared exit criterion landed, across a span in which the STALL-class intervention count is ZERO — director DECISION-class touches unrestricted.**

Ratified with its content definition (product lane **and** a moved fidelity row against an unchanged baseline, or a passing spec-tied acceptance test, or an R11-verified live-surface change) and its falsification rule (any stall-class event, or any claimed advance lacking its exit-criterion delta, resets the counter to zero).

**N = 3 is RATIFIED.** The count is not the binding constraint — *zero stall-class events across the span* is, and on the last four days' record that is a hard bar. Three is the smallest count that distinguishes a pattern from a single lucky run, which is the right test for "may harness investment resume."

**The proposal is better than the advisor's starting point and the reasoning is recorded as the better one**, particularly on the stall/decision split: counting decision-class touches as failures would have taught the system to stop escalating correctly, when routing curriculum calls and one-way doors to the director is exactly what the architecture is *for*.

## 2. Two decisions attached (transmitted as decisions)

**(a) Breakage stays drawable — the criterion may not deadlock.** Harness work diagnosed as the cause of a stall-class reset is **breakage**, not speculative machinery, and remains drawable under PRODUCT-FIRST's existing exception ("machinery only on breakage, or as a named dependency"). Otherwise a stall-causing defect could become unfixable precisely because harness is demoted, guaranteeing further resets. Speculative harness improvement stays demoted until the counter is met.

**(b) The three atoms are whatever the ratified priority order yields.** They may not be selected for ease. Satisfying the criterion with three cheap product atoms while higher-ranked work sits untouched would be an R12 breach — optimising the gate rather than passing it. If the priority order is genuinely being followed this is automatic; state it so it cannot drift.

## 3. Returned as a PROBLEM, not a prescription

Four events **that actually happened in the last four days** may or may not be caught by the stall detectors as currently specified. **For each: confirm it is already detected, add a detector, or argue with evidence that it is not stall-class.** Your call — you know the detectors.

1. **An emergency console rescue** — a granted turn at the terminal because the machine could not recover otherwise. Arguably the single strongest stall signal available; the proposed set names "the director hand-typing the next atom", which may not cover it.
2. **A publish-gate wedge lasting over an hour.** Four occurred; each blocked publication and, on two occasions, correlated with the tick going quiet behind it.
3. **An origin freeze or push failure over thirty minutes** — the phantom-push incident froze origin for 3.5 hours while the machine believed itself healthy.
4. **An advisor ruling whose purpose is restarting stalled work.** This one binds the advisor: if the machine has to be doorbelled awake by a staged document, the counter resets. Consistent with §4 of the coherence ruling, which binds the advisor equally.

## 4. Coherence requirements (non-negotiable)

- **Computed from primary state, per LAW C** — git history, the maturity map, the gate-authorizations ledger, the fidelity register and the backlog surface. Never from the tick's own enumeration; the whole point is a verdict the machine cannot assert about itself.
- **Published in the daily self-note** alongside the PRODUCT/MACHINERY split already ruled: current count, and the cause of the last reset.
- **Per coherence-by-derivation:** if any surface — site, diagram or report — ever states that the harness is "done for now", that claim must be **derived from this counter**, never hand-written. A hand-written claim is a publish-gate failure like any other disagreement.
- **This is the single answer** to "is the harness done for now." Any other informal test is superseded.
- **R12:** the counter is a gate on a decision, not a quality score. It must not appear in any fidelity, maturity or product-quality claim.

## 5. One question owed back

`merit_order` is reported drawable only from **2026-07-28**. State plainly why: an epoch or front gate, a dependency, or a scheduling artifact. **If it needs a director act to open, say so and it will be opened** — a date is not a reason, and a decision hiding inside a schedule is exactly the class that cost 42 hours at the weekend.

## WORK THIS CREATES

1. Mechanise the ratified criterion with its R15 pair (a synthetic stall must reset the counter; three clean content advances must satisfy it).
2. Stall-set coverage verdict on the four named events — detected, detector added, or argued out with evidence.
3. Counter and last-reset-cause published in the daily note and derivable by any surface that would claim harness completion.
4. One-line answer on the merit_order date.

Acceptance: the counter is computable from primary state by a third party with repository access and no machine access, and its current value is visible without asking the machine.

**Risk & proportionality:** ratification plus a coverage problem; mechanisms are the machine's to choose. Tag: **proceed.**

— Advisor bridge, carrying the director's ratification, 2026-07-27.
