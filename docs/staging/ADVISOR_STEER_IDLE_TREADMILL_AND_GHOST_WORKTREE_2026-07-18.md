# ADVISOR STEER — Two noise sources: idle self-refill treadmill, and the persistent ghost worktree (2026-07-18, evening)

**Type:** [STEER] — absorb and carry on. Both are noise-reduction; neither changes what the company builds.

---

## 1. The idle self-refill treadmill (you registered this yourself as the H1 gap)

**The problem, from your own words tonight:** *"the self-refill keeps cycling verified atoms with no cooldown."* When the map is genuinely drained of below-target work and the loop is gated on a director decision, RULE 0's self-refill keeps offering at-target HARDEN/red-team re-verification. You have correctly DECLINED it repeatedly ("declining treadmill; resuming on a genuinely new signal") — that judgment is right and should be preserved. But the doorbell keeps firing anyway, which produces: repeated `[LOOP BROKEN] 31 continuations, no commit` alarms (three times today, always the same signature — that's a mechanical bound, not a coincidence), a stop-hook that blocked turn-end 9 consecutive times until Claude Code's own cap overrode it, and a large token burn for zero output.

**The requirement (mechanism yours):** when the map is genuinely drained AND work is gated on a director act, the loop should settle into a quiet, low-frequency wait rather than re-offering at-target work every cycle. Your existing judgment ("decline the treadmill") becomes the *mechanism's* default rather than something you must re-decide every wake. A drained-and-gated state is a legitimate resting state, not a failure — and it should not page or thrash. Genuinely new signals (a staged doc, a director act, a real alarm, new below-target work) wake it immediately, as now.

**Note the honest tension to resolve in your design:** RULE 0's "the to-do list is never empty" exists to prevent idleness-as-avoidance. That is right when real work exists. It is wrong when the *only* remaining work is re-verifying finished atoms while blocked on a human. Distinguish the two states; keep the anti-idleness pressure for the first.

## 2. The persistent ghost worktree

`agent-a857b050bba7ca9c6` shows MERGED and has been re-pinged ~20 times today (roughly half of all WORKTREE UNDECLARED alarms). It is dead litter, not live work, and it has survived every reconcile cycle. Clean it up (safely, honoring the new locked-worktree refusal guard — merged-and-dead is exactly the case the guard permits), and confirm the H24_worktree ping-hygiene fix is DEPLOYED in the running reconciler, not merely committed (the committed-not-deployed class has bitten three times today). Expected outcome: healthy transients stop paging; genuine accretion still pages loudly.

---

**Why both tonight:** the director's phone should be quiet overnight. Neither of these is a real fault; both are alarms firing where nothing needs a human — which is precisely what erodes the value of the alarm channel.

**Risk & proportionality:** (1) touches the RULE 0 self-refill path — behavioural, reversible, own commit; keep the anti-idleness pressure intact and prove the drained-and-gated case with a test. (2) worktree cleanup is a single dead directory + confirming a deploy; narrow. Tag both: reversible/narrow — just do it, no [ACT] needed.

— Advisor, via the staging channel, at the director's instruction ("stage them").
