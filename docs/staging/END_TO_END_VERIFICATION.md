# END_TO_END_VERIFICATION — R11 + the synthetic user (P1 class fix)

**Staged:** 2026-07-10 by advisor, from the director's question "what can we
learn — I keep having to spot these myself."
**Capability cells:** H (harness verification) + F (sanity daemon). Small,
immediate; do after the graph-data regeneration in flight.

## The class (pattern across every director catch this week)
Each layer verifies its own claim; nothing verifies the path to the user's
eye. Committed/pushed/deployed all green while the DATA was never regenerated
(today). Internally-consistent but domain-absurd bill (C6). Correct hedge maths
on future-leaked data. Tests green asserting the wrong thing. Every failure
lived in a JOINT between links. The director is currently the only end-to-end
verifier — that is the thing to fix, not his vigilance to rely on.

## R11 (permanent rule, CLAUDE.md): verify to the rendered value
For any user-visible change, "done" means: fetch the LIVE deployed surface and
assert the actual rendered value/content changed as intended — not the code,
not the file on origin, not the deploy log. If the change is data-driven,
assert the data stamp AND the visible value. Playwright-level checks (as done
well on the C1 fix) are the norm for UI claims. A completion NTFY for
user-visible work must state what was checked ON THE LIVE SITE.

## The synthetic user (extend the sanity daemon)
The daemon already checks artefacts for domain sense. Extend it to walk the
LIVE site on its cycle with freshness invariants:
- Every data artefact carries generated_at (most already do). Invariant: a
  surface's data stamp must be newer than the last state-change that should
  have moved it (sim run processed, publish authorised/hold released, phase
  closed touching that surface). Staleness beyond a lane-appropriate tolerance
  = alert with the specific surface + expected-vs-actual stamp.
- Spot-check a small rotating sample of rendered values against origin truth
  (the number on the page equals the number in the data).
This makes staleness machine-detectable. Today's failure mode ("hold released
but nothing regenerated") must be one of the explicitly simulated test cases.

## Also close today's instance-class properly
Releasing any hold must itself trigger republication of the held artefacts
(authorisation must never be a no-op). Verify per R11 on the live site.

## DoD
R11 in CLAUDE.md; synthetic-user checks live in the daemon with the hold-release
case simulated; today's graphs verified fresh ON poesys.net (stamp + values);
one NTFY stating what the live checks now cover. The measure of success, stated
plainly: the director's future catches should be judgement questions, not
plumbing failures.
