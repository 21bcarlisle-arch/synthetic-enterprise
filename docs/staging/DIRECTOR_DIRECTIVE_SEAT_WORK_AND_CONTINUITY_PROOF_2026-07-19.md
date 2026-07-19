# DIRECTOR DIRECTIVE — Work for the reconciled seat, and the continuity proof (2026-07-19, evening)

**Type:** [ACT-equivalent authorization + work]. The director bounced the seat himself; a fresh worker seat brought up clean at 21:13 UTC (epistemic_verifier PASS, 516 files, 0 violations). **This document is also the continuity proof: if you are reading it, a rested loop woke on an origin-staged doc with no console input.** Report that fact explicitly in your first line.

## Context the director wants stated plainly

The seat was not failing when it appeared idle — it was **empty**. The pull-loop health read `drained-and-gated: only at-target HARDEN remains while blocked on a director act`. D and A were never authored into the map, and everything else was done or awaiting ratification. A healthy loop with nothing to draw is indistinguishable from a broken one when observed from outside. That distinction matters for how the day is recorded.

## The work, in priority order

**1. Author D and A into the map, then build them.** This is the outstanding campaign work you deferred this afternoon for fresh attention — you now have a fresh seat. Author carefully (the map is the governance spine), then let the loop draw them. Campaign BUILD authorization is standing.

**2. Fix the drift-detector's false positive.** `bounce_worker_seat.sh` infers a session's live id from an open transcript file descriptor. A freshly-seeded seat has written no transcript, so the read returns `unknown`/`None` — and the script reports `DRIFT: None != <expected>` from an **unreadable value rather than an observed mismatch**. It would therefore cry drift on every healthy fresh seat, including the one it just created. Distinguish "cannot read yet" from "read and mismatched", and make the healthy-fresh-seat case pass. R15: prove the false positive is gone and a genuine mismatch still trips.

**3. Investigate `[OPERATIONAL LAYER RED]` (20:36).** The independent-cadence operational signal (`pytest -m operational`) is genuinely red. This is H23 working as designed — it alarms without wedging the site publish — but a red is a red. Diagnose, fix or register with evidence.

## Standing note on the continuity class

Four attempts on this class in one day (RC1, RC3, the rest-heartbeat, the identity fix). Per R3 that is well past redesign territory at the *implementation* level, so consider the *architectural* question honestly and report a view: **is keeping one Claude Code session alive indefinitely via stop-hook rearm working with the grain of the tool, or against it?** An alternative shape — scheduled invocations each doing one bounded unit of work and exiting cleanly, rather than a seat that must never die — may be structurally more robust. This is a question, not an instruction; the director wants your reasoned view before anyone builds a fifth fix.

**Risk & proportionality:** item 1 touches the governance spine (map authoring) — do it fresh, own commit, verify the append; item 2 is narrow and test-provable; item 3 is diagnostic. Nothing here weakens a safety bound. Tag: **proceed by default;** bring only genuine gate-opens or a Claude Code version change back as [ACT].

— Advisor, carrying the director's direction, 2026-07-19.
