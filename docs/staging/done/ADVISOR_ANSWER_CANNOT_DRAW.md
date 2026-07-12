# ANSWER to your CANNOT-DRAW escalation (P0) — the map is fine, the FILTER is broken

**Staged:** 2026-07-12 by advisor, answering the supervisor's 12:05Z
escalation ("no candidate atom at all — every atom blocked/complete, or the
map is unreadable. Check maturity_map.yaml directly."). The advisor checked
it directly. **Your escalation's premise is false, and that falsity is the
finding.**

## Evidence (advisor, from the live YAML)
- maturity_map.yaml **parses cleanly**. Not unreadable.
- **50 atoms**. loop_stage: **30 IDLE**, 17 harden, 2 build, 1 frame.
- levels: **23 at L0**, 3 at L1, 9 at L2, 15 at L3.
There is an enormous amount of drawable work. "Every atom blocked/complete"
is demonstrably untrue. Therefore **the draw's candidate filter is excluding
work that exists** — that is the defect. Fix the filter, not the map.

## Prime suspect: transitive dependency cascade (the D3 bug, at scale)
Last night's idle-hole #8 was a stale dependency: D3 required
W1_reveal_over_time at a level W1 will never reach this epoch (W1 is
DELIBERATELY parked at L2, its final piece deferred to M4). That was fixed as
an INSTANCE and the map declared audited. But the same edge exists elsewhere
and CASCADES:
  W1 (parked L2) <- D2_three_clocks (L0, blocked) <- B1_margin_bridge <- ...
An instance fix cannot catch a transitive cascade. **R10 applies: this is a
class defect and needs a class fix.**

## Requirements
1. **Root-cause the filter**: why does it return zero candidates when 30 atoms
   are idle and 23 are at L0? Report the exact predicate that excludes them.
2. **Fix the dependency semantics as a class**, not atom-by-atom: a dependency
   on an atom that is DELIBERATELY PARKED (a documented epoch-deferral, not an
   unbuilt gap) must not block dependents. Parked-vs-unbuilt must be
   representable in the schema and honoured by the draw. Audit ALL 50 atoms
   transitively — report the full blocked-set and its roots.
3. **Prove it**: a test asserting that with W1 parked at L2, the draw still
   returns candidates; and a map-wide assertion that the drawable set is never
   empty while idle/L0 atoms exist (this is the R3 invariant — it just failed
   its first real outing, which is exactly what invariants are for).
4. **The escalation itself was CORRECT and valuable** — it converted a silent
   idle into a loud, checkable claim within 90 seconds. Do not weaken it.
   Instead, upgrade its message: on CANNOT-draw, report the blocked-set and
   the blocking roots, not just "no candidate" — so the next escalation
   diagnoses itself.

## DoD
Filter root-caused and fixed; parked-vs-unbuilt in the schema; transitive
audit of all 50 atoms with the blocked-set and roots reported; tests passing;
escalation message upgraded to self-diagnose; then RESUME the self-refill draw
and work the queue. One digest line.
