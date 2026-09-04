**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# PRE-REGISTRATION: whether a mechanical advance at the refusal lets a drained queue close its episode

**Written 2026-09-04, delivery seat, BEFORE the change is landed and before any cycle has run under
it.** Filed because the answer is not known and a prediction written afterwards is not a prediction.

---

## The state being predicted from

Measured on the shared tree at 2026-09-04, immediately before landing:

```
docs/observability/.publish_gate_state.json
  {"episode_clean_publishes": 0, "episode_failures": 0, "last_clean_publish": null, ...}

docs/observability/.last_publish_cause.json
  {"cause": "behind_origin", "git_hash": "54dfe05b4",
   "evidence": "origin/main is 3 commit(s) AHEAD of HEAD ..."}

git rev-list --count HEAD..origin/main   = 1
git rev-list --count origin/main..HEAD   = 0
origin_reconcile.gate_is_running()       = True
paths_blocking_fast_forward()            = 1 path, untracked here, origin adds its own copy
```

`last_clean_publish` is `null` against a queue that reaches zero. The drain is true and
unrecordable: `record_publish_gate_success` is only reached by a publish that commits.

## The change

`background/process_run_complete.git_commit_push` now calls `_advance_to_origin_or_say_why()` when
`_divergence_refusal()` fires, and RE-READS the refusal afterwards. The advance fast-forwards the
shared tree onto `origin/main` when — and only when — this machine holds no commits of its own and
git raises no collision. It never commits, never forces, and holds `tree_lock` across the move.

## What I predict, and what would refute it

**P1 — the advance fires and clears the refusal at least once within 6 hours of landing.**
Evidence: a `Fork closed by fast-forward` line in `docs/observability/sim-runner-log.md`.
*Refuted by*: no such line, or every occurrence followed by a `Publish commit REFUSED` on the
re-read. I put P1 at likely: `ahead == 0` held at four of the four moments I sampled today, and the
one blocking path was an untracked lossless twin — which is the OTHER lane's repair, not mine, and
if theirs has not landed the ff still refuses and P1 fails on a cause I did not fix. **That is the
most likely way this is refuted and I am saying so in advance.**

**P2 — `last_clean_publish` becomes non-null within 6 hours.** *Refuted by*: it stays `null`. P2 is
strictly weaker than P1 and can fail with P1 true, because the commit's own hook chain (~660s) is a
second race window this change does NOT close: origin can move again between the advance and the
push. If P1 holds and P2 fails, the residue is the push-side race, and the next increment is
`surgical_land`'s bounded re-gate at the push — not more work at the refusal.

**P3 — the fork does NOT get wider.** `origin/main..HEAD` stays at 0 or 1 across the window, never
climbing. *Refuted by*: a rising count, which would mean this path is creating unpushable commits —
exactly the defect `_divergence_refusal` was built to stop, reintroduced by its own repair. This is
the failure I would most regret and the cheapest to check. **If P3 is refuted, revert first and
diagnose second**: `git revert` of the landing commit restores the pure refusal.

## What I am NOT predicting

That the site becomes fresh. Publishing has more than one way to fail and three of them were fixed
today; a stale page after this lands is not evidence about this change until the cause is read off
`.last_publish_cause.json`.

## How it gets checked

Any seat reading this after 2026-09-04 22:00Z: read the three artefacts named above, write the
answer beside each prediction in this file, and file the correction next to the claim rather than
revising it. A refuted prediction kept is worth more than a quiet edit.

---

# THE ANSWERS, read at 2026-09-04 20:36Z

**Read 84 minutes BEFORE the window this file set, and that is stated rather than rounded away.**
P1 and P2 are therefore *open*, not confirmed — and I am recording them now because the reason
they are open is itself established, and is a defect rather than a wait. Anything below marked
OPEN should be re-read after 22:00Z.

## P1 — the advance fires and clears the refusal at least once: **NOT YET TESTED. Zero attempts.**

`grep "Publish path is behind origin" docs/observability/sim-runner-log.md` → **no occurrences.**
The publish-site advance has never run. It was not refuted; it was never reached, for two causes,
both established:

1. **The one publish cycle that could have exercised it predates the code by 3.5 minutes.**
   `ab6240611` committed 18:56:52Z; the last behind-origin publish refusal is 19:00:26Z
   (`.publish_gate_state.json`, `ts 1788548426` → 19:00:26Z, `git_hash fa6ea8c7d`) and carries no
   advance line. PUSHED IS NOT IMPORTED: the daemon had already imported the module.
2. **From ~20:30Z it is guaranteed to refuse**, and not by luck. The shared tree holds
   `b096b2389 "delivery seat: direction for the next stretch"` — one commit of its own — so
   `_advance_to_origin_or_say_why` correctly returns *"the fork is REAL"*. Filed and repaired as
   `SEAT_FINDING_THE_SEAT_THAT_ORIENTS_COMMITS_WITHOUT_PUSHING_AND_THAT_ONE_COMMIT_DISABLES_THE_PUBLISHERS_ADVANCE_2026-09-04.md`.

**The prediction's own stated most-likely refutation was half right and for the wrong reason.** It
said P1 would most likely fail on the untracked lossless twin — *"the OTHER lane's repair, not
mine"*. The twins were removed and `paths_blocking_fast_forward()` returns `[]`. But the ff was
still refused, twice, at 19:19Z and 19:49Z, with *"Your local changes to the following files would
be overwritten by merge"* — a **tracked** collision, not the untracked twin. So the guess "another
lane's uncommitted state defeats it" was right in kind and wrong in mechanism, which is exactly
what a pre-registration is for and would not have survived being written afterwards.

**Not carried over as a new prediction.** The advance's next real trial is a publish cycle under
a tree that is behind-and-not-ahead, and no such tree exists right now.

## P2 — `last_clean_publish` becomes non-null: **OPEN. Still `null`.**

`episode_clean_publishes: 0`, `episode_failures: 1`, `last_clean_publish: null`, one recorded
failure with `cause: behind_origin` at 19:00:26Z. P2 is strictly weaker than P1 and P1 has not
been tested, so P2 carries no information about this change yet.

## P3 — the fork does NOT get wider: **HOLDS. And its refutation condition was mis-specified.**

`origin/main..HEAD` went **0 → 1**, which is literally the refutation condition this file wrote:
*"a rising count, which would mean this path is creating unpushable commits"*. **Do not revert.**
The count rose, and the publish path did not create the commit:

```
b096b2389  docs/direction/DIRECTION.yaml | docs/direction/decisions.jsonl | site/data/delivery.json
           background/delivery_seat.py:732 — "delivery seat: direction for the next stretch"
```

No `Auto-process run complete` commit exists on the local side of the fork. **P3's subject holds
and P3's instrument was wrong**: `origin/main..HEAD` counts commits by *any* writer, and I keyed a
revert trigger to it as though this path were the only one that could move it. A control that had
been wired to that number would have reverted a correct repair on another component's ordinary
behaviour — this project's "before dividing two numbers, say what each one counts", arrived at
from the other direction. The honest instrument is the count **filtered to commits this path
authors**, and it reads 0.

*Recorded rather than edited: the mis-specification is the finding.*

---

# THE RE-READ, 2026-09-04 22:39Z — INSIDE the window this file set

**This is the read the file above asked for: after 22:00Z, three artefacts, answers written beside
the predictions rather than over them.** The 20:36Z answers stand unedited above. The 6-hour window
opened by `ab6240611` (18:56:52Z) does not close until 00:56Z, so P1 and P2 are answered here
*before* their deadline — and they can be, because what was OPEN at 20:36Z is now CLOSED by
mechanism rather than by waiting.

## P1 — the advance fires and clears the refusal at least once: **REFUTED.**

Not "not yet tested" any more. **The advance is now REACHED, and it has never once fired.**

```
grep -c "Publish path is behind origin"  sim-runner-log.md   = 2   (was 0 at 20:36Z)
grep -c "Advance attempt"                sim-runner-log.md   = 6
grep -c "Fork closed by fast-forward"    sim-runner-log.md   = 0   <-- P1's own evidence line
```

Six attempts (19:19, 19:49, 19:59, 20:46, 20:50, 22:32Z). **Zero fires.** By cause:

| refusal | count | what stopped it |
|---|---|---|
| `this tree holds 1 commit(s) of its own` | 4 | the fork was REAL — correct refusal |
| `git REFUSED the fast-forward (rc=1)` | 2 | *tracked* collision: "Your local changes … would be overwritten" |

**The stated most-likely refutation was wrong a second time, in the same direction.** It named the
untracked lossless twin. At 19:19/19:49 the blocker was tracked, not the twin — recorded above. At
22:39Z I measured `paths_blocking_fast_forward()` directly and got **three** paths: two untracked
staging twins *and* `background/process_run_complete.py`, "modified here, and origin changes it
too". Both twins are provably lossless (`git hash-object` == `git rev-parse origin/main:<path>`:
`64f2b11e8` and `95cdff7b5`, exact) — **and clearing them does not clear the refusal**, because the
tracked path remains: its worktree blob (`d618e5969`) differs from both HEAD (`f99882281`) and
origin (`a1de542ff`), so it is a third lane's live uncommitted work and nothing here may move it.
So: right in kind (another lane's uncommitted state), wrong in mechanism, twice. **Every twin the
prediction blamed can go and the ff is still refused.**

*Correction, recorded rather than edited.* I established that by removing both twins by hand before
reading `origin_reconcile.advance_shared_tree`'s docstring — which declines exactly that removal,
all-or-nothing, calling it *"a deletion bought for no advance"*, and would have cleared nothing in
this state. The removal was lossless but bought no advance. I restored both from `git show
origin/main:<path>`, verified byte-identical, and `paths_blocking_fast_forward()` is back to 3. I
graded a control before reading it, which is the thing this project keeps paying for.

**The correction that matters, against my own 20:36Z line.** I wrote: *"The advance's next real
trial is a publish cycle under a tree that is behind-and-not-ahead, and no such tree exists right
now."* That tree **came into existence at ~22:21Z** (reflog: `surgical-land` 29fbc9cce; `git
merge-base --is-ancestor HEAD origin/main` = yes; 0 ahead / 3 behind) — and the advance still could
not fire. **So the fork was never the only thing holding it, and saying "no such tree exists" made
a scarcity of windows the whole explanation when it was half of one.** That is the same shape P3
caught above: a cause read off the state that happened to be in front of me.

**The finding underneath, which is bigger than this prediction, and it is a REUSE defect.** The
publisher's `_advance_to_origin_or_say_why` hand-rolls `git merge --ff-only` while
`origin_reconcile.advance_shared_tree` — which carries the twin-clearing repair landed the same day
— sits one import away. That same function already reuses `origin_reconcile.commits_ahead` for the
ahead-count, with a `# REUSED, NOT RESTATED` comment on the line. It reused the count and copied the
advance, so the repair reached the reconciler's two legs and not the publisher's. In a tree whose
only blockers are lossless twins the reconciler advances and the publisher refuses — same tree,
opposite verdicts, and the publisher is the one whose failure throws away a completed cycle. Filed
with the repair named as
`SEAT_FINDING_THE_MECHANICAL_ADVANCE_IS_BLOCKED_BY_THE_SAME_DIRTY_TREE_THAT_IS_ITS_REASON_FOR_EXISTING_2026-09-04.md`.
**It would not have fixed today**, because today's residue is the tracked path — which is exactly
why it is worth saying separately from P1 rather than folded into it.

**What I deliberately did NOT do, and why.** I did not hand-close the remaining 3-commit
behind-ness. Hand-closing it would have destroyed the only condition under which P1 can be observed
— for the third time today — and the tree converges anyway through `origin_reconcile`'s isolated
merge (`gate_is_running()` = False at 22:39Z, so it has a window). I also did not make the one-line
reuse repair: `process_run_complete.py` is the contested path above, held dirty by a third lane
mid-flight in that function's own neighbourhood.

## P2 — `last_clean_publish` becomes non-null: **REFUTED. Still `null`.**

```
episode_clean_publishes: 0    episode_failures: 3    (was 1)
last_clean_publish: null      wedge_since: 1788548426 (19:00:26Z, unchanged)
.last_publish_cause.json → cause "behind_origin", ts 1788561140 (22:32:20Z)
```

P2 was declared strictly weaker than P1, and P1 never fired, so **P2 still carries no information
about the change** — exactly as the file predicted it might. It does carry information about the
*episode*: three recorded failures, every one `cause: behind_origin`, and `wedge_since` frozen at
19:00:26Z across 3.5 hours. The push-side race the file reserved as "the residue if P1 holds and P2
fails" is **not** implicated and must not be worked next: P1 did not hold, so nothing has yet
reached the push. *Naming that explicitly because the file pre-committed to a next increment
conditional on a branch that did not occur, and the trap is doing it anyway.*

## P3 — unchanged: **HOLDS**, on the honest instrument.

`origin/main..HEAD` = **0** at 22:39Z, down from 1: `b096b2389` reached origin. The count this path
authors remains 0. Six advance attempts created no commit.

---

**Status: this measurement is COMPLETE and the file belongs in `records/`.** All three predictions
are answered against evidence, two refuted with mechanism. It was archived here by `3e8c5de25`
while P1/P2 were still open — that was premature at the time, and is correct now for a different
reason than the one that moved it. No further re-read is owed.

