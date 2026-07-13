# Retro: the tmux pane-injection saga — R3 two-strike, and the fix that held

**Closed 2026-07-13, director-confirmed** ("Injection fix CONFIRMED — no [Pasted text] accumulation since").

## The incident
The director's Claude Code console filled with 300+ `[Pasted text #NNN]` chips accumulating in the input box during long turns — background daemons injecting turn-grants while the session was mid-turn, the text piling up unsubmitted.

## The three strikes (observed, with evidence)
- **Strike 1 — pattern-list fix (self-caught).** Broadened `is_busy_content` to catch "Waiting for background agent" / "Levitating" / "esc to interrupt". Helped the fork-wait case; did not stop it.
- **Strike 2 — spinner-regex fix, live-verified, claimed CLOSED — symptom persisted.** Root-caused a real bug: Claude Code now appends a token counter *inside* the spinner parens (`(19m 43s · ↓ 64.5k tokens)`), so the end-anchored `\)\s*$` regex stopped matching. Fixed it, live-verified `is_session_idle=False` on a busy pane, sent "FIXED at the source." **But the director still saw accumulation.** The instrumentation log proved why: the supervisor kept injecting every ~2 min, all "sent" — a single-snapshot pane read returns idle at poll instants *regardless of the spinner format*.
- **Strike 3 — the R3 redesign that held.** Eliminated the mechanism (idleness *guessing*) rather than patch it again, per R3. A format-INDEPENDENT gate, `_safe_to_inject`, requiring ALL of: (1) **input-box occupancy** — never inject while a `[Pasted text]` chip is unconsumed, so accumulation is structurally impossible; (2) **byte-stability** — a processing pane MUTATES every second because the spinner's elapsed-timer ticks, *whatever the text format is*, so instability is a format-proof "busy" signal; (3) the known-busy patterns as a belt. Verified against R1: zero injections across a ≥30-min continuous-busy window (through a session crash), then director confirmation.

## Lessons
1. **Pane-scrape-plus-regex guessing of an external TUI's busy state is fundamentally fragile** — it chases a format the codebase does not control, and the format moved twice in one day. The robust fix keys on INVARIANTS: a processing pane *mutates* (the timer ticks) regardless of format; unconsumed input is *directly visible* as chips. Prefer an invariant over a pattern whenever gating on someone else's UI.
2. **"Live-verified" ≠ "holds over a window."** `is_session_idle=False` at one instant did not mean the gate held across every poll instant of a long turn. A flaky-timing fix is only validated by a *sustained* observation (R1: ≥30 min + the consumer's own confirmation), never a single spot-check. "Defect closed" language was rightly banned until the director confirmed.
3. **R3 worked as designed.** The second false completion on the same component forced ELIMINATE-the-mechanism, not a third patch of the same heuristic. Two-strike redesign is load-bearing.
4. **The instrumentation was the hero.** The director's ask #5 (source-attributable injection logging: script + timestamp + payload hash) turned "an hour of SIGSTOP forensics" into a seconds-long diagnosis on strikes 2→3. Instrument the choke point *before* theorising.
