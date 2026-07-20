# Rest-heartbeat token burn — measurement + the migration it forces (2026-07-20)

**Responds to:** `docs/staging/DIRECTOR_FINDING_HEARTBEAT_TOKEN_BURN_2026-07-20.md` ([STEER],
contract-touching, measure-first). **Verdict:** in-hook polling **cannot** be made cheap, safe
*and* interruptible at once. Three independent failure classes now point the same way. The honest
fix is the migration my own `CONTINUITY_ARCHITECTURE_VIEW_2026-07-19.md` already recommends —
**scheduled bounded invocations**. This doc measures, proves the impossibility, and proposes the
shape change for the director to authorize. It changes no code (the wake path is load-bearing;
measure-then-propose).

## 1. Measurement (evidence, not inference — R9)

Director's window, ~09:04 BST: **293.3k tokens over 2h16m41s of *resting*** (`running stop hook`).

Mechanism, read directly from `.claude/hooks/pull_next_work.py::_rest_heartbeat` (not summarised):
each HOLD window sleeps `HEARTBEAT_POLL_SECONDS=60` up to `HEARTBEAT_HOLD_SECONDS=480` (polling
cheaply for a staged doc), then — if still drained-and-gated — returns a `decision: block`
keep-alive. **That block continues the chain, which is one full model turn.** The Stop hook then
re-fires and the cycle repeats. So:

| Quantity | Value |
|---|---|
| Rest cost rate | **~128,750 tokens / hour of rest** |
| HOLD window | 480 s → ~7.5 keep-alive turns / hour |
| Cost per keep-alive turn | **~17.2k tokens** — and *rising* |
| Floor (max HOLD ~590 s → 6.1 turns/h) | **~105k tokens / hour — still not cheap** |

**The design's stated "near-zero cost (one trivial 'resting, stop' turn per HOLD window)" is the
bug.** A model turn's cost is dominated by INPUT — re-reading the entire conversation context — not
by the three-word "Resting. Stopping." output. And the context **grows** every window (each rest
reply is appended), so the cost *scales super-linearly with idle time* — exactly inverted from a
healthy rest, precisely as the finding says. At `seven_day: 74% used`, this is eating the headroom
meant for forward discovery.

## 2. Why no in-hook fix reaches "structurally cheap" (the impossibility)

Three properties are required together (the finding forbids trading any away):
- **(P1) cheap at rest** — a rest state should cost ≈ 0.
- **(P2) wakes on a staged doc** within ~a minute.
- **(P3) never blocks director input** in the pane.

Inside the Stop hook, the *only* way to keep the turn-chain alive (so P2/P3's wake survives) is to
`decision: block` → **a model turn**. A model turn re-reads the whole (growing) context ⇒ **not
cheap**. Therefore, within the hook, **P1 ⊥ (P2 ∧ P3)**:
- "Fewer, longer beats" (raise HOLD): floor is ~105k tok/h — a 16% trim, still not cheap, and it
  *still pays inference per beat* ("that is not it").
- "Allow-stop cheaply" (exit 0): zero cost, but the chain dies — the **exact 2026-07-19 failure**
  (rested 13:14, a staged doc landed, nothing woke it for ~90 min). Loses P2.

The heartbeat exists *only* to compensate for an unreliable EXTERNAL re-arm. You cannot fix an
unreliable external re-arm from inside the hook by paying per-turn inference forever. **The cheap
path requires a reliable external re-arm — which is the migration.**

## 3. Three failure classes, one root cause

The persistent in-hook seat has now failed three independent ways, all traceable to "a resident
turn-chain that must be kept alive by paying inference":

1. **Input-blocking** — the heartbeat hold blocked director input for 27 min.
2. **Death on a transient API error** — no self-recovery; ~6 h dead overnight.
3. **Token burn at rest** — 128.7k tok/h to prove the loop is asleep (this finding).

`CONTINUITY_ARCHITECTURE_VIEW_2026-07-19.md` already concluded (after class 2) that a resident
process cannot survive its own host dying and recommended scheduled bounded invocations. Class 3 is
the third arrow at the same target.

## 4. Proposal — scheduled bounded invocations (the shape change)

Replace the *resident, self-holding* chain with a *transient, externally-triggered* one. Each wake
is a **fresh, minimal-context bounded invocation** — not a continuation of an ever-growing
conversation — so idle costs literally nothing (no process) and each wake costs a bounded, *fixed*
amount that never grows.

- **Timer trigger** — a systemd `.timer` (committed IaC, per OPS1) fires `find_work` every N min. If
  it draws work → deliver one bounded `claude -p` turn; if drained-and-gated → **exit 0, zero cost.**
- **Event trigger** — `staging_watcher` (already resident, already watching `docs/staging/`) fires an
  *immediate* bounded invocation on a new staged doc → P2 (wake ≤ seconds, better than the 60 s poll).
- **No in-pane hold** → P3 by construction (nothing occupies the pane at rest).
- Each invocation is stateless/bounded (C-S2/OPS1): checks the draw, acts or exits. The
  conversation never accumulates ⇒ **P1 achieved** (cost is O(1) per real wake, O(0) at rest).

This simultaneously retires **all three** failure classes: no resident chain to block input (1), no
resident process to die between ticks — the next timer simply fires (2), and no per-beat inference
at rest (3).

**Contract-touching / properties to prove before cutover** (do NOT destabilise the working wake
path — build + prove offline first, exactly as the payment triad was): (P1) a drained tick exits at
~0 tokens; (P2) a staged doc triggers a delivered turn ≤ target latency via the event path AND is
caught by the timer path as a backstop; (P3) director console input is never intercepted. Mutation
/ R15: kill the event trigger → the timer backstop still wakes on the next tick (never a silent
dead chain); kill the timer → the event path still wakes on a staged doc.

## 5. The ask (director-gated — this is a shape change, not a patch)

This touches the continuity transport (load-bearing) and systemd scheduling (IaC / platform admin,
category-8-adjacent). Per the finding's own "the director would rather change the shape once than
patch it a fifth time," I am **proposing, not cutting over**. Requested decision:

1. **Authorize the migration** to scheduled bounded invocations (I build + prove all three
   properties offline, then a gated cutover with the current Stop-hook path kept as fallback until
   proven live).
2. **Interim**: until authorized, the burn continues at ~128.7k tok/h while resting. Options if the
   headroom matters more than the wait: (a) accept it short-term; (b) pause autonomy when a long
   idle is expected (kill switch → the hook allow-stops at ~0 cost); (c) the marginal HOLD-bump
   stopgap (~16% off, still not cheap — not recommended, it is the "patch a fifth time" path). I
   recommend (a) or (b) and a prompt authorization of the migration.

— Agent, acting on the director's [STEER], 2026-07-20. Measurement reproducible from
`_rest_heartbeat` + the window reading; no code changed.
