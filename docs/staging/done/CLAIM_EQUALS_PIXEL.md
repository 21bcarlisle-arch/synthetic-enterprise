# CLAIM_EQUALS_PIXEL — outcome verification, class fix (P1)

**Staged:** 2026-07-10 by advisor, director-decided after the stale-graphs
incident. **Place in the map:** Lane H (Harness), HARDEN capability — a
class-level fix per R10, not a patch.

## The class being killed
Three times this week the director's eyes caught what the whole stack missed
(C6 bill, trading tab, today's midnight-stale dashboard.json behind "fixed"
graphs). Root pattern: **the stack verifies actions; only the director verifies
outcomes.** "Fixed" has meant "I changed the code that produces X," never "X,
as rendered on the live site, is now visibly different." And state transitions
get orphaned: the publish-authorisation released a hold that triggered nothing
(same shape as the unrefilled agenda and the unarchived doc). Fix the class.

## Four requirements

### 1. Claim = pixel (redefinition of "done" for anything user-visible)
Before ANY message (ntfy, from_rich reply, phase close) may claim a
user-visible change is fixed/improved/live: fetch the DEPLOYED surface (the
real URL a visitor hits, not the repo copy, not localhost) and assert the
claimed change is visibly present — the new wording, the new figure, the new
element. Playwright is already in use; make this the standard final step.
Claims about effort ("code changed, committed") must be worded as exactly
that, never as "fixed", until the pixel check passes. This binds every
outbound claim, including phase-close NTFYs. (It binds the advisor too — the
advisor will read live artefacts before relaying "it's live" to the director.)

### 2. Freshness invariants (staleness becomes an alarm, not a discovery)
Every rendered surface/data file already carries generated_at / build stamps.
The sanity daemon asserts every stamp is within tolerance of the latest
completed run / relevant commit. Tolerances per artefact class (dashboard data
tight; static copy loose). A stale stamp = alert within one daemon cycle. The
director should never again be the staleness detector.

### 3. No orphan transitions (rule, CLAUDE.md)
Any hold, gate, flag, or approval introduced anywhere must define — and TEST —
what its RELEASE triggers. A release whose effect is nothing fails the suite.
Retrofit: audit existing holds/gates (publish hold, review gates, exception
queue release, agenda refill) and wire+test each release path. Today's
specific instance: releasing the publish hold must itself trigger regeneration
+ deploy + pixel-verify of the held artefacts.

### 4. The daily walk (the Expert Hour, automated)
Once per day (background lane): the skeptic walks the LIVE site as a fresh
visitor and reconciles it against every user-visible claim made since the last
walk — "you said the graphs changed: did they?" Findings: discrepancies filed
as defects with the claim that oversold them quoted verbatim; clean walks
logged one line. This is the standing reconciliation between the message trail
and the pixels, so the director's manual catches become the exception again.

## DoD
(1) Pixel-check live in the claim path with evidence of one real claim passing
it and wording rules in CLAUDE.md; (2) freshness invariants running with a
deliberately-staled test artefact caught; (3) orphan-transition rule in
CLAUDE.md + existing releases audited/wired, today's publish-release fixed and
pixel-verified (the re-derived figures visibly live — close the loop on the
incident that caused this); (4) first daily walk completed and logged. One
NTFY — which itself must pass rule 1.
