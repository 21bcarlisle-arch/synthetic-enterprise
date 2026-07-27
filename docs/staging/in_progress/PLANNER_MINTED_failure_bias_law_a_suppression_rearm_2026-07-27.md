<!-- SUPERVISOR_DRAW: self-drawable -->
# [PLANNER-MINTED / PROPOSE-THEN-PROCEED] — LAW A: every suppression is time-bounded and re-arms (2026-07-27)

**Provenance:** RUNG-7 planner refill (director ruling `WORK_IS_THE_DEFAULT_2026-07-23`). Minted from a ratified goal, not a doorbell: `docs/staging/in_progress/DIRECTOR_RULING_FAILURE_BIAS_LAWS_2026-07-27.md` **names** LAW A but leaves it un-drawn (no atom, no mint). This doc makes that named next-step drawable (R16: a fix named only in a ruling body is invisible to the draw).

**Serves:**
- **DIRECTOR_RULING_FAILURE_BIAS_LAWS LAW A** — "Failure modes bias to noise, never to silence. Every suppression, throttle, fold or gate is time-bounded and re-arms, regardless of any self-declaration. No component may indefinitely silence an independent check."
- **R17 (THE TICK NEVER RESTS)** and **[[project_eighth_class_pending_batch_deadlock_2026_07_27]]** — the 42h/18-dead-hour stalls whose common cause was a suppression that never re-armed (the H2 proven-rest fold silenced the STALL watchdog indefinitely).
- **Operational robustness (OPS1 / MAKE_IT_STICK)** — the machine's load-bearing property that the director's window stays honest: a false page costs a glance, a silent stall cost a weekend.

**Robustness gained (one sentence):** no suppression, throttle, fold or gate in the harness can silence an independent check indefinitely — each carries an explicit expiry and re-arms after it, so the *default* behaviour on any unresolved condition returns to noise (page) rather than decaying to silence.

---

## Scope — BUILD (harness lane; director-ruled, drawable now)

1. **Enumerate the suppressions.** From the ruling's named five + the sweep (see the R10-sweep mint): the H2 proven-rest fold, the pending-batch gate, `.harden_cooldown.json`, the rest-legitimacy suppression (advisor-requested 2026-07-22), any enumeration false-empty fold. Locate each in `background/supervisor.py`, the deadman's switch, and the daily-self-note generator.
2. **Add a time-bound + re-arm primitive.** Every suppression records `suppressed_at` and a max age; past the age the suppression is void and the underlying check fires **regardless of any self-declaration of legitimate rest**. Prefer one shared primitive over per-site patches (SIMPLICITY GUARD).
3. **R15 both ways (binding — R15):** (a) set a suppression, advance the clock past its bound, prove the independent check FIRES; (b) within the bound with the condition resolved, prove it stays quiet (no false page). A suppression that cannot expire is the defect this law forbids — mutation-prove the expiry.

## Walls untouched (director-reserved)
- One-way doors: none — git-reversible harness change, no real market/money/secrets.
- L3 level moves stay `blocked_on: director_level_up` ([[feedback_levels_are_proposals]]).
- Curriculum values / generator ground truth: untouched.

## Window
Director already ruled the mechanism; no design-ambiguity propose window. Drawable now as harness BUILD. Disjoint file_scope from LAW B (gate cluster-scoping) and LAW C (watchdog/note derivation) — the three may build concurrently per MULTI_ATOM_DRAW.

— Planner mint, RUNG-7 refill, 2026-07-27.

<!-- LANDED-PARTIAL (2026-07-27 worker tick): the BINDING LAW A requirement -- "no component may
     indefinitely silence an independent check" -- is now MECHANISED as an R10-style class-fix gate.
     background/suppression_register.py::validate_suppression_register REQUIRES every `silent`-biased
     entry to DECLARE its re-arm: a numeric `max_age_seconds` (time-bound / Law A) and/or a non-empty
     `rearm_trigger` (independent counterpart / Law C -- the R10-sweep remedy verbatim). A silent
     suppression declaring NEITHER fails the gate (fail-closed); a `law_a` token with no time-bound or
     a `law_c` token with no trigger fails too (the register cannot claim a remedy it does not encode);
     status:compliant does NOT exempt (LAW A "regardless of any self-declaration"). All 10 silent live
     entries populated with their re-arm; gate green. R15 BOTH WAYS in
     tests/background/test_suppression_register.py (live passes; 5 mutants -- no-rearm / law_a-without-
     bound / law_c-without-trigger / compliant-without-rearm red, noisy-exempt stays green) + a live-
     strip code mutation. suppression_register.json carries a `law_a_gate` note.

     STILL SELF-DRAWABLE (optional remaining scope, NOT the binding requirement): scope item 2's
     shared RUNTIME `suppressed_at`-recording primitive was NOT built -- the per-site runtime
     time-bounds it would consolidate (the 2h rest-proof cap, the 6h HARD_REST_CAP, the harden 6h/
     content-sha cooldown, the LAW C independent reads) ALREADY EXIST and are now enumerated+gated, so
     a shared primitive is refactor-not-capability (SIMPLICITY GUARD: no adapters-for-future-adapters).
     A future tick may consolidate them behind one primitive if the director wants it; the class-fix
     that LAW A binds on is landed. SCOPE HONESTY (R9/consumed-not-absorbed): what is ABSORBED is the
     gate + declarations, live + R15-proven; the runtime-consolidation is DEFERRED, not claimed. -->
