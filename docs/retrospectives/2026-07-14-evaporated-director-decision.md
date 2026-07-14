# Retro — A director decision evaporated with no channel record (2026-07-14)

## What happened (observed-with-evidence)
- **2026-07-13 11:08Z:** `[ACTION NEEDED]` registered `W2_2_population_draw` —
  a curriculum question (R13), which acquisition profile A/B/C/D to model from 2021.
- The director answered **B** (trickle ~1/yr) **yesterday** (his testimony,
  2026-07-14 in-console).
- **The answer left zero trace in every persisted channel:**
  - `action_needed_register.json` → still `resolved: false`, kept re-pinging
    (last_pinged 2026-07-14 11:09Z — that ping is what resurfaced it).
  - No `from_rich_*.md` since 2026-07-12.
  - Nothing in `director_input_log`, `director_twin_log`, or `decision_log.jsonl`.
  - `ntfy-mirror.md` shows **no `[IN]` inbound at all** on 2026-07-13 — only `[OUT]`.
- **2026-07-14:** director re-issued the same decision, noting it "got lost in the jam."

## The defect class (director's framing, verbatim)
> "A director decision that evaporates unnoticed is its own defect class — decision
> delivery needs the same landed-verification as alarms and injections."

Alarms (deadman) and injections (tmux) were both hardened this week to verify the
signal **landed at its destination**, not merely that it fired. **Director decisions
are the same shape and were never given that treatment.** This is a fire-and-forget
gap, identical in structure to the deadman/tmux incidents — the shared lesson is
**landed-verification**, not the specific channel.

## Evidenced contributing mechanisms (observed, not asserted as the sole cause)
1. **`ntfy_responder.py:179` drops messages `< 25` chars silently** ("no action —
   message too short"). Curriculum answers are inherently short (`B`, `Profile B`).
   A terse director reply is discarded with no record and no alert.
2. **`action_needed.resolve_item()` stores no answer** — it only flips a boolean.
   Even the *intended* happy path loses the decision *content*; there is nowhere
   structured for "what did he decide" to land. (Fixed this instance by writing an
   `answer`/`resolved_at` field into the entry; the mechanism still needs it.)
3. **No receipt loop:** the register re-pings the director forever but never
   confirms an answer was *received and applied*. A decision can be given and still
   never close the loop — exactly what happened.

## The fix (this class, folded into the landed-verification family)
Same class as `THE_NAIVE_ORGAN` (expected-output-absent) and the deadman/tmux
landed-verification work. Registered as QUEUE atom(s), not fixed on sight:
- Every director decision must have a **landed-verification**: the answer is
  captured verbatim, written to a durable structured record, AND a confirmation is
  surfaced back ("recorded your decision: W2_2 = B") so a silent drop is impossible.
- Remove the silent `< 25`-char drop for anything correlated to an open
  `[ACTION NEEDED]` item (a short reply to an open question is the *expected* shape,
  not noise).
- `resolve_item()` gains a required `answer` argument — you cannot resolve without
  recording what was decided.

## Immediate action taken (this incident)
- W2_2 = Profile B recorded 3 ways: register (`resolved:true` + `answer` stored),
  `decision_log.jsonl`, and the versioned R13 artifact
  `docs/design/curriculum/W2_2_acquisition_curriculum.md`.
