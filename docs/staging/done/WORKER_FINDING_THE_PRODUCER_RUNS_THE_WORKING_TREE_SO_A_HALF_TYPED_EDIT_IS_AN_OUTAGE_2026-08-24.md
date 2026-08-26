**Severity:** LATENT · **Lane:** H_harness

# The producer runs the working tree, so a half-typed edit is a production outage — twice today

**Found by:** worker tick 2026-08-24 14:26–14:35 BST, drawn on the RUNG-1d "PRODUCER SILENT
(PRIORITY ZERO)" doorbell.
**Not repaired here**, and the reason is itself evidence: the repair needs a gated commit, and
at the time of writing a 31-minute run was resident at 10.6 GB with 3.0 GB available. Starting
a pytest gate into that is the collision `background/resource_headroom.py` exists to prevent.
Declared and deferred rather than collided — see "Why this was not landed in its own tick".

## What this adds to the door that was already surveyed

`docs/staging/done/WORKER_FINDING_THE_PRODUCER_IS_NOT_DEAD_IT_IS_OOM_KILLED_TWELVE_TIMES_TODAY_2026-08-24.md`
established that the producer is OOM-killed rather than dead, and made four recommendations.
Three are now closed, and this tick verified each rather than assuming it:

| rec | status | evidence |
|---|---|---|
| 1. Raise the WSL2 allocation | **the director's, now unblocked** | no `.wslconfig` existed on the host at all, so the guest was taking WSL2's 50%-of-host default. Written this tick with `memory=24GB`; it is inert until `wsl --shutdown`, which is his because it closes every session on the box. NTFY sent. |
| 2. Correct the 32 GB figure | **DONE** | `CLAUDE.md` now reads "32GB DDR4 on the HOST but ~15GB in the WSL2 guest … (12 sim-runner OOM kills, 2026-08-24)" |
| 3. Give the OOM door a control | **DONE** | `background/oom_watch.py` (14:01) + `tests/background/test_oom_watch.py` (14:02), wired as `_oom_clause()` in both limbs of the RUNG-1d detector |
| 4. `MemoryHigh` on the unit | not taken | the surveyed finding recommended against it alone, and nothing here changes that |

So the OOM door is worked to the boundary of what a tick can land. **This finding is about the
other door the surveyed finding named in one sentence and left without a control.**

## The observation (R9: observed with evidence)

The surveyed finding recorded one instance and called it "the durable point":

> The producer runs the working tree, so any lane's partially-written multi-file edit is a
> production outage for as long as it takes to finish typing.

It has now happened **twice in seven hours**, and the second instance was not known when that
was written:

| time | run died with | elapsed | the split |
|---|---|---|---|
| 12:07 | `ValueError: drawn household 'PSTK-2021-0401' handed to customer 'SYN-2021-001'` | 7 s | premise-id split written; `live_drawn_households` relabel not yet |
| **13:54:29** | `TypeError: _resolve_campaign.<locals>.<lambda>() got an unexpected keyword argument 'quotes_issued_to_date'` | **4 s** | caller passing the new kwargs written; callee lambda not yet |

**Neither was a defect in any commit.** For the second, both halves landed together in
`dcba2f2e2` at 14:04:33 — ten minutes *after* the run they killed:

```
-        quote_budget_fn=lambda net_assets_gbp, accounts_held: vars(
+        quote_budget_fn=lambda net_assets_gbp, accounts_held, quotes_issued_to_date=0, wins_to_date=0: vars(
```

and `git show HEAD:simulation/net_new_acquisition.py` carries the matching call site in that
same commit. Every endpoint is self-consistent. Only the minutes between the two keystrokes
were broken, and the producer sampled exactly those minutes.

## Why the existing mitigation did not fire

This project already knows this class. The standing mitigation is **"default the callee first"**
— and here the callee *was* defaulted (`quotes_issued_to_date=0, wins_to_date=0`). The defaults
were written correctly and still did not help, because defaults only protect the
**callee-lands-first** ordering, and this edit went caller-first. A defaulted parameter makes an
old caller safe against a new callee; nothing makes an old callee safe against a new caller.

That is the sharp point: the mitigation is real, it was applied, and it is **order-dependent in
a way nobody states when they cite it**. Half the orderings it is invoked for, it does nothing.

## What it costs, and why it is LATENT not BLOCKING

Two lost runs today, ~11 minutes of producer time, and a contribution to the same staleness the
OOM kills caused. Nothing published is wrong — every figure still carries the clock it was
computed at (R14) — so no control's verdict is invalidated. It is LATENT for that reason, not
because it is rare: it is the *second* instance in one working day, and the rate is rising with
the number of concurrent lanes.

There is also a second-order cost that is easy to miss. `.sim_producer_state.json` records only
failures that reach Python, so at 13:54 it recorded a **4-second `TypeError`** as the standing
condition while the real pattern was **30-minute runs killed at 10–13 GB**. That is the exact
mirror of the failure `oom_watch` was built to fix, in the opposite direction: the OOM clause
now stops the state file hiding a kill behind silence, but nothing stops it presenting a
transient half-typed-tree error as the durable diagnosis. The next reader of that file gets a
name for the wrong door — as this tick's doorbell did.

## Recommended

1. **A pre-run coherence smoke check in the producer.** Before committing to a 30-minute run,
   `sim_runner` imports the modules the run entrypoint touches and skips the cycle (retrying on
   the next tick) if the import raises. Cost is ~2 s against a 30-minute run; it converts a lost
   run into a skipped one, and it is the whole class rather than either instance (R10). It also
   catches the case neither instance had: a tree that is broken for longer than one cycle.
2. **State the ordering rule when the mitigation is cited.** "Default the callee first" is
   incomplete; the rule that holds is **land the callee before the caller** — the defaults are
   what make that ordering safe, not a substitute for it.
3. **Give the state file a transience discriminator.** A failure with `elapsed_s` in the single
   digits, on a run whose predecessors ran for minutes, is a tree-state error and not the
   standing condition. Recording that distinction is what would have stopped this tick's
   doorbell naming a resolved `TypeError` while a 10 GB run was live.

R15 applies to item 1: the smoke check must be mutation-tested against a tree with a genuinely
broken import, and against a healthy one, or it is another control that cannot fail.

## Why this was not landed in its own tick

Stated plainly because a deferral that is not stated reads as an oversight. At 14:35 the live
run was 31 minutes in at 10.6 GB resident with 3.0 GB available and swap 95% full, and the
lifetime `oom_kill` counter stood at 265. A pre-commit gate runs the test suite; on this box
that is the fourteenth kill and the loss of the only run standing between the site and a fifth
hour of staleness. The producer's memory decision is the director's and is not yet applied, so
nothing this tick could do would have made the gate safe.

This document is therefore left in `docs/staging/` as a doorbell for the next tick, which should
land it once either a run artefact has been written or the guest has been restarted at 24 GB.
