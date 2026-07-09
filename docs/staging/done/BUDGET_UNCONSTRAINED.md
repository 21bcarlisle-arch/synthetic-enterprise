# BUDGET_UNCONSTRAINED — token economy retired for 44 days (standing note)

**Staged:** 2026-07-09 by advisor, director-confirmed from the live usage meter.
**Tier:** 2, small standing update. Does not change the current phase order —
DOMAIN_SENSE_AND_COMPLIANCE continues; this changes the ECONOMY assumptions the
agent plans under.

## Fact
Director is on Max (20x). Live meter: 0% of weekly allowance used this week,
resets Monday. The recent heavy days sat inside a rounding error of budget.
Conclusion: **token cost is not a binding constraint through ~mid-August.**
Any prior instruction that throttled work "for token economy" (e.g. background
lane deferring to avoid burn, sampling instead of full verification to save
tokens) is suspended for this period.

## What changes
1. **Background lane runs at full parallelism.** It no longer waits on the
   foreground to conserve budget — only genuine file-scope conflict (tree-lock)
   or a Tier-1 pause should hold it. Run the epoch-2 evidence pass, discovery-
   agent anchor gathering, clustering, and Qwen summarisation concurrently with
   the compliance build where scopes are disjoint.
2. **Verification deepens as the default.** Browser-level checks (Playwright, as
   done well on the C1 fix today) and population-level statistical checks become
   standard per phase, not occasional. Spend the headroom on catching errors,
   not on speed alone.
3. **Coordination and reviewer attention are now the real limiters** — not
   tokens. So: do NOT respond by opening many concurrent BUILD phases. This
   week's failures came from work running ahead of verification and ahead of the
   single human reviewer who catches domain-absurd output. More budget must buy
   depth and parallel *analysis/verification*, not a wider unreviewed build
   front. Let the compliance/domain-sense immune system land first; it is what
   relieves the reviewer bottleneck, and only then does a wider build front
   become safe.

## Non-negotiables unchanged
Historical Ground Truth, epistemic wall, R1-R10, REVIEW_GATE, push-before-notify,
0b evidence on surfaces, single-writer per file. Speed and volume never override
these. "Too much good-quality work" is welcome; work that outruns verification
or the wall is not.

## DoD
Economy assumptions updated wherever they gate work (CLAUDE.md / agenda /
background-lane config); background lane confirmed running concurrently with the
compliance build. One NTFY noting what was un-throttled.
