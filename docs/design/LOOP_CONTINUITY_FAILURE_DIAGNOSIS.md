# Diagnosis — "running continuous" broke (09:12→10:44 idle; origin-staged doc unconsumed)

**Provenance:** director, 2026-07-19: *"checkpointed at 09:11 saying 'running continuous' then idled 93 minutes. An advisor doc unconsumed in docs/staging/ since 10:32 didn't wake you… second occurrence today."* Evidence-based (R9), not reconstruction.

## What actually happened (evidence)
- `docs/observability/pull-loop-log.md` last entry: **`[09:12:04 UTC] drained-and-gated -> allow stop (quiet wait)`**. No entries after. The loop went dormant at 09:12 and never re-drew.
- `find_work(False)` called live now returns **`(None, False)`** — the treadmill-quiet third state — with its own log: `THREE-LANE self-refill: BUILD=0, SITE=0, DISCOVERY=0` · `all 30 idle atoms are FRAME-saturated — returning []` · `DRAINED-AND-GATED quiet wait … a genuinely new signal wakes it`.
- The advisor doc `DIRECTOR_AMENDMENT_TOKEN_RESOURCE_DIMENSION_2026-07-19.md` was committed to **origin** at 10:32 (`1c3baea28`, `[ADVISOR-STAGED]`) but was **never in the local working tree** `find_work` reads. Separately, the local `process_run_complete` daemon had made **7 auto-process commits (10:19–11:51) never pushed** — the local↔origin trees had drifted in *both* directions.

## Three stacked root causes (all necessary for the observed failure)

**RC1 — the loop went quiet because there was no mechanically-drawable work.**
All 30 idle atoms (including the gate-after-authorized Epoch-2 campaign A–G) sit at `loop_stage: idle`, which the draw treats as BUILD-gated (offers them for DISCOVER/FRAME only, never BUILD). Their DISCOVER/FRAME is saturated (done). So the draw correctly found zero below-target work and rested. **The gate-after directive authorized campaign BUILD as POLICY but it was never MECHANIZED into the draw** — the atoms were never flipped to a drawable stage and there's no `FRONT_OPEN` in `gate_authorizations.jsonl` for the campaign. I compounded this by building campaign work via *manual fork dispatch* rather than through the draw — so the moment I stopped hand-dispatching, `find_work` had nothing and the treadmill-quiet mechanism (correctly, given the map state) rested.

**RC2 — a dormant loop has no re-arm.**
The pull-loop is driven ONLY by Stop-hook events, which fire when the interactive session ends a turn. A quiet allow-stop makes the session **dormant**; a dormant session produces no Stop events, so `find_work` is never re-invoked. The treadmill-quiet log claims *"a genuinely new signal wakes it"* — **this is false: no wake path exists for a dormant session.** `staging_watcher` notifies Rich, not the agent (by design). Nothing re-pokes a rested seat. So the mechanism I built to reduce doorbell noise rests *forever* until a human messages the session — which is exactly what unblocked it at 10:44.

**RC3 — even a live loop would not have seen the doc.**
Advisor docs arrive via the staging bridge as commits to **origin**. The local working tree does not auto-pull, and `find_work` reads the LOCAL `docs/staging/`. So an origin-committed advisor doc is invisible to the local loop until someone pulls (the same sync-latency that hid the Epoch-2 campaign earlier this session). The 7 unpushed local daemon commits are the mirror image.

## Not the same failure as this morning
The 06:28→08:32 stall was **hold-behind-heavy** (I kept a turn open synchronously for a validation) — addressed by `RESOURCE_AWARE_SCHEDULING_PROPOSAL.md`. This 09:12→10:44 stall is **quiet-dormancy-with-no-rewake (RC2) + origin-sync-gap (RC3)**, a different mechanism. "Running continuous" was an overclaim: it holds only while `find_work` keeps returning work; there is no mechanism keeping it alive once it legitimately rests.

## Fix proposal (contract-touching — the loop spine; sequence measure→propose→adopt, one change per turn, R15 each)
- **RC1 → the amendment's OPTIONAL lane is the director's own answer.** Give the treadmill-quiet loop *forward-discovery* to draw when idle + headroom (CORE/OPTIONAL from `DIRECTOR_AMENDMENT_TOKEN_RESOURCE_DIMENSION`), so it rarely goes fully quiet — "something genuinely valuable to reach for instead of busywork or nothing." AND mechanize authorized campaign BUILD into the draw (flip the A–G atoms to a drawable stage — needs the campaign `FRONT_OPEN` recorded; that record is director-console-only, so it is flagged for the director, not self-written).
- **RC2 → a heartbeat re-arm.** A periodic re-invocation of `find_work` independent of Stop-hook events (a systemd timer, or the already-running `supervisor` daemon re-poking the seat) on a cadence — so a rested loop re-checks for work every N minutes instead of dying. The re-arm must itself be R15-failable (prove it fires a draw when a new staged doc appears during dormancy). AND `staging_watcher` should poke the agent loop, not only Rich, on a new doc.
- **RC3 → the loop must see origin.** The pull-loop's work-check should `git fetch` and include origin's `docs/staging/` (or the staging bridge commits to the local tree), and local daemon commits must push. Bidirectional sync, so neither an origin-staged directive nor a local daemon commit sits invisible.

**Interim mitigation in force:** I am keeping the loop alive this turn by actively working (two campaign/throughput forks + main-seat consumption) and will not claim "continuous" again until the RC2 re-arm exists — because until it does, "continuous" depends on there always being drawable work, which is not guaranteed.
