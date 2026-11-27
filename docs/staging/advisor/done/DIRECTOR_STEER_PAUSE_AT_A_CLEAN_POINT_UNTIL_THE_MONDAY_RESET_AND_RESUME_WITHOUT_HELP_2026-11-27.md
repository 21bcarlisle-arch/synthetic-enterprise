**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Pause at a clean point until the Monday reset, and resume without help

**Type:** STEER, through the advisor channel. The director's words, from chat, Fri 27 Nov 14:24 GMT:

- "80%, am doing some other research, so let's pause for the reset if this week, once at a decent point. Make sure we can pick straight back up."

## The reading

- Plan usage was **80%** at Friday 14:24 GMT. The reset is **Mon 30 Nov 03:00 GMT**. He wants the remaining points for his own research, so **the machine stops spending tokens until the reset.**

## What is asked

1. **Reach a decent point, then stop.**
   - Land what is mid-landing.
   - Start nothing new.
   - Do not abandon a half-done change in the tree. Land it, or park it with its state written down.
   - Aim to be quiet within about **2 hours**.
   - Long jobs that use machine time but no session turns, such as a book run already under way, may finish. Their grading waits for Monday.
2. **Declare the quiet window** through the existing mechanism, `docs/observability/.usage_pause.json`, which the supervisor and the dead-man's switch already read. Set it until **2026-11-30T03:00Z**, with the reason quoting him, so nothing alarms or restarts work during the pause. Delete it, or let it lapse, at the reset.
3. **Make the restart automatic and clean.** Before going quiet, write a short resume note into the seat's direction record:
   - what is in flight;
   - what the first three draws after the reset are: the s.12g fidelity check and re-grade (the 26 Nov ruling), the knowledge-first gas page, and the next book;
   - anything that needs a human.

   At 03:00Z Monday the machine picks up from that note with no input from him. The weekly balance review for the week of 30 Nov is still owed, either before the pause from today's state, or as the first act after the reset.
4. **The four open `for_the_director` rows stay open.** The advisor has put them to him with recommendations. Answers will arrive through the advisor channel. Nothing waits on them during the pause.

The advisor is suspending its cloud stall check until Monday morning, so the pause does not page him.

## Done

- Actioned 2026-11-27 ~14:30 GMT by the worker tick, as pacing under the 15 Oct delegation.
- Started nothing new: the drawn finding (worker-finding-a-blind-reading-reviewer-found-three-defects-live-at-head) was left untouched.
- Quiet window declared twice: `python3 -m background.tick_mode off --until 2026-11-30T03:00Z --then normal` holds worker-tick, seat-executor, delivery-seat and two-reader-review, and reverts by itself at the reset; `docs/observability/.usage_pause.json` (gitignored) carries `resume_at: 2026-11-30T03:00:00+00:00` and his words, read by the supervisor and the dead-man's switch, and lapses at the same instant.
- Resume note: `resume_after_pause` in `docs/direction/DIRECTION.yaml`, covering in-flight long jobs, the held seat claim, the first three draws (s.12g fidelity check and re-grade, the K8 gas page, the next book), the weekly balance review as the first act after the reset, and the one residual spender (`background.naive_organ` reads neither control).
- Four open `for_the_director` rows left open.
- To reverse: `python3 -m background.tick_mode normal`, then delete `docs/observability/.usage_pause.json`.

Decision: none -- a pacing request from chat, answering no recommendation.
