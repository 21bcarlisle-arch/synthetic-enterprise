# ADVISOR_STEER — idle-hole #8 audit + auto-clear + overnight draw (P1)

**Staged:** 2026-07-11 ~23:55Z by advisor. Director is asleep; proceed
without him. Three items, in order:

## 1. Idle-hole #8 audit (R3 territory — 8th instance)
Window: 21:09Z (five-doc closeout) -> 23:58Z (run_complete SKIP). Nearly
three hours, queue non-empty in the map (M2 estimated-billing, freshness
class fix, PRODUCTION_READINESS Parts B/C, M2_FRAME hierarchy work), zero
commits, no escalation to the director. From the supervisor decision log:
were turns granted in that window? If granted: what did the draw select and
why did it produce nothing? If not granted: why did the dial-weighted draw
report empty with those atoms open? This is the 8th idle variant — apply R3:
if the answer is another phrase/state-matching gap in the draw or the
"legitimate idle" test, redesign that test, don't patch it. The escalation's
silence through the window is part of the audit.

## 2. Implement the ALREADY-AUTHORIZED supervisor auto-clear
Authorized in-console 2026-07-11 morning (confirmed in the injection-
resolution message): context > ~400k AND clean boundary (turn ended, work
pushed, nothing in flight) -> supervisor injects /clear then re-grants with
the standard boot. Tonight the session sat at 649k begging for a manual
/clear — the feature was never built. Build it, log each auto-clear, test it
on the next boundary.

## 3. Overnight draw (explicit, so the night is not wasted)
After 1-2: proceed per dials — M2 estimated-billing/catch-up-rebilling
movement (D3, now quantified at 425 bills) is the hot-lane build;
SURFACE_FRESHNESS_CLASS_FIX and PRODUCTION_READINESS Parts B/C are the
background lane. Twice-daily digest cadence continues; morning digest to
include the item-1 audit answer.
