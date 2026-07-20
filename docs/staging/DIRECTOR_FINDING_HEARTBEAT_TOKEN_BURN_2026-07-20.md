# DIRECTOR FINDING — The rest-heartbeat burns tokens while resting (2026-07-20)

**Type:** [STEER] — a defect with a measurement requirement. Absorb; do not interrupt in-flight work.

## Observed

At ~09:04 BST the director's window showed the seat in the rest-heartbeat, cycling:

> `● Resting. Stopping.` → `Ran 1 stop hook` → `[REST HEARTBEAT -- you are correctly resting... Do NOTHING and STOP IMMEDIATELY]` → `● Resting. Stopping.` → repeat

with the session line reading **`running stop hook · 2h 16m 41s · ↓ 293.3k tokens`**.

**A rest mechanism that consumes hundreds of thousands of tokens while doing nothing is the opposite of rest.** Each beat appears to cost a full model round-trip: the hook fires, the model is invoked, it reads the instruction, replies "Resting. Stopping.", the hook fires again. The keep-alive is paid for in inference.

## Why this matters beyond tidiness

1. **It consumes the exact budget the director wants spent on forward discovery.** The standing direction is that spare token headroom should fund optional forward-looking work. Tokens spent proving the loop is asleep are tokens not spent discovering anything.
2. **It scales with idleness.** The longer the seat correctly rests, the more it costs — precisely inverted from what a healthy design does.
3. **It is the THIRD independent failure of the persistent-seat design**, after (a) the heartbeat blocking director input for 27 minutes, and (b) death on a transient API error with no self-recovery (~6 hours dead overnight). Three distinct failure classes from one architectural choice.

## Requirements (mechanism yours)

- **Quantify it first.** Measure the actual cost per beat and per resting hour, using the `rate_limits` sensor whose availability you confirmed at step-zero last night. An unmeasured cost cannot be traded off.
- **Resting must be structurally cheap.** A rest state should cost approximately nothing. Whether that means fewer, longer beats, a non-inference keep-alive, or something else is your design — but paying model inference per beat is not it.
- **Do not trade away the wake property or the input-responsiveness property** already required. Cheap rest that cannot be woken is worse than expensive rest.
- **Then answer the architectural question with evidence, not preference.** Three failure classes now point the same way, and your own `CONTINUITY_ARCHITECTURE_VIEW` already recommends scheduled bounded invocations, where an idle period costs literally nothing because no process exists. If the honest conclusion is that in-hook polling cannot be made cheap, safe *and* interruptible simultaneously, say so plainly and propose the migration — the director would rather change the shape once than patch it a fifth time.

**Risk & proportionality:** touches the Stop-hook path, which is currently load-bearing for continuity. Measure before changing; do not destabilise the working wake path; prove all three properties together (cheap at rest, wakes on staged doc, never blocks input). Tag: **contract-touching — measure first, then propose.**

— Advisor, recording the director's observation, 2026-07-20.
