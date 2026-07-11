# ADVISOR_STEER — browser verification regression (R4, Tier 2)

**Staged:** 2026-07-11 by advisor. Non-interrupting; next boundary.

Tonight's digest states "no browser automation available in this
environment" — but Playwright browser verification demonstrably WORKED on
2026-07-08/09 (the C1 render check). A capability present three days ago and
absent today is a REGRESSION, not an environment fact. R4 differential
diagnosis, prime suspects in order:
1. Today's Option-2 security work (egress allowlist / secrets relocation)
   breaking chromium launch, download, or its cache path — check what the
   allowlist actually blocks and whether the browser binary/cache moved.
2. The fix work having been delegated to a subagent whose tool grant lacks
   the browser — in which case the MAIN session still has it; verify there.
3. A genuine breakage (version, missing binary) — reinstall/rewire under the
   Developer profile floor.

Then: run the pixel checks yourself on the thesis chart + C1 pages (real
rendered canvas/DOM, not curl), close both in_progress docs per their DoD,
and add a standing invariant: the pixel-verification capability itself is
part of the harness baseline — if it breaks, that is an alarmed failure, not
a caveat in a digest. The director's manual look becomes optional
double-cover, not the only path. One digest line with the root cause.
