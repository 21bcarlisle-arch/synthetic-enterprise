**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# FINDING: the "272 commit refusals" are 175 cycles, the rate is 39.6% not 9.2%, and a red test is a minority cause

**Found:** 2026-09-05, delivery seat, working the Lane 0 direction *"measure and attribute
commit_refused, which is where publish cycles ACTUALLY die"*. Pre-registered before counting:
`docs/design/PREREGISTRATION_COMMIT_REFUSED_ATTRIBUTION_2026-09-05.md`. Full measurement:
`docs/observability/commit_refused_attribution_2026-09-05.md`. Re-derive:
`python3 -m tools.commit_refusal_attribution`.

**The direction's conclusion stands and its arithmetic does not.** Refusals really are where
publish cycles die, and really are ~10× the fork branch two directions were spent on. But all four
figures it carried are sums of two different line shapes about the same cycle.

## Three defects, in the order they were found

**1. `272` is not a count of anything.** It is 175 occurrences of `Commit/push failed
(commit_refused)` plus 97 of `DID NOT LAND (outcome: commit_refused)`. The second line was added
2026-08-19, so it exists for late cycles and not early ones: the sum double-counts every cycle
after that date and single-counts every one before it. The same error is in all four figures
(behind_origin 34→17, commit_timeout 19→14, push_did_not_reach_origin 13→7). This is the
before-you-divide-two-numbers rule, one level earlier — before you *add* two numbers, say what
each counts.

**2. The lifetime denominator is blind over 77% of itself, so 9.2% is not a rate.** Named publish
outcomes began 2026-08-13 22:23. Before that, every failure — refused and empty-index alike —
logged the identical `Commit/push failed (possibly nothing changed)`, 177 times. So all 175
refusals falling after 2026-08-13 reads as *"the problem started then"* and is really *"the
instrument was installed then"*. Over the answerable window: **175 of 442 cycles refused, 39.6%**
— 4.3× the implied figure. A control keyed to the 9.2% would have been keyed to an artefact of
retention.

**3. A red test is a minority cause: 40%.** Non-test governance gates are 48% — finding-class 31,
site-lane 20, orphan-ratchet 16, level-promotion 13 — and 12% is unattributable and reported as
its own bucket, never folded onto a side to clean up the split. The gates in that 48% judge
whole-tree state the publisher did not create and cannot fix: the daemon commits regenerated site
data and is refused because another lane left a finding unclassified or a module unwired.

**4. It is not a per-cycle hazard.** 46 contiguous runs; the longest is **41 consecutive refused
cycles**, 23.4% of every refusal in the span, one cause nothing cleared. Runs of ≥5 hold 61%. So
39.6% is a true share and a misleading hazard: the publisher fails totally for hours and then
works. **The unit is the episode, not the cycle.**

## Predictions, scored honestly

P1 (>50% non-test) **REFUTED** — 48%, and its stated reasoning ("a red test is fixed once") is
contradicted in its own terms by a 26-long red-test streak. P2 (largest run ≥15%) **CONFIRMED** at
23.4%. P3 (recent > lifetime) **CONFIRMED on the wrong mechanism** — I predicted the gates were
added over the span; the real cause is the vocabulary was. Recorded because a confirmation reached
by wrong reasoning would have licensed a false next inference.

## What was NOT done, deliberately

No mechanism, no alarm, no threshold. The distribution was unknown until today and a control
written before it would be keyed to today's answer. **The next question is episode duration by
cause**, which converts this share into a cost and decides whether the 48% governance-gate share
is a problem or the gates working correctly. That is in the same log.

## What landed

`tools/commit_refusal_attribution.py` (+ 9 controls in
`tests/tools/test_commit_refusal_attribution.py`). The derivation is a script and not a number in
a document precisely because the number this direction carried rotted — the controls are keyed to
the measurement's properties (blind denominator reported separately; unattributable never folded
in; the partition asserted whole with every branch reachable; the publisher's own banner table is
the only gate vocabulary) rather than to today's counts, so they stay green as the numbers move
and go red when the measurement starts lying.
