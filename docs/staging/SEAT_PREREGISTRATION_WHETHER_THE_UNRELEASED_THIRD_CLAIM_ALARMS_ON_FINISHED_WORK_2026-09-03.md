# [SEAT PRE-REGISTRATION] Does the executor's unreleased third claim alarm on finished work?

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery machinery
**Filed** 2026-09-03, by the delivery seat, in the worktree, **before any measurement of the alarm
record**. Subject: `background/seat_executor.py` `run_once`, as landed in `b095fadf8`.
**Graded below, in this file, in the commit that carries the repair. P1 CONFIRMED.**

Related: `docs/staging/done/SEAT_FINDING_THE_EXECUTORS_DISCHARGE_ASKS_A_STORE_ITS_OWN_CLAIM_NEVER_REACHES_2026-09-02.md`
(§9.5 repair A, §10.2's added clause) — this is the residual that repair left.

---

## 1. What I have already established by reading, and is not in question

Not predictions. Both are plain reads of the code at `HEAD` = `2635bf7fe`.

`run_once` acquires the claim in **three** stores:

```python
for store in (None, delivery_lane.CLAIMS_FILE, _worktree_claims()):
    delivery_lane.claims_mod.claim(work_id, ..., paths=[], path=store, now=claimed_at)
```

`_hand_back` releases from **one**:

```python
rec = delivery_lane.claims_mod._load(delivery_lane.CLAIMS_FILE).get(work_id)
if isinstance(rec, dict) and float(rec.get("claimed_at", 0)) == claimed_at:
    delivery_lane.claims_mod.release(work_id, path=delivery_lane.CLAIMS_FILE)
```

`None` is `seat_work_in_hand.CLAIMS_FILE`. **Nothing in `run_once` ever releases it.** The
worktree copy is reset by `ensure_worktree`, so that third store self-clears; the first does not.

The record is written with `paths=[]`, and `record_landing` binds paths into the delivery-lane
store only, so the `seat_work_in_hand` record carries **no paths for its whole life**. Therefore
`last_progress(rec) == claimed_at` — `_last_commit_time_touching([])` is `0.0` — and the claim's
idle clock starts at the claim and never restarts, no matter what the turn lands.

`STALE_AFTER_SECONDS = 45 * 60`. `overlapping_claims` calls `sweep(path=store)` on **both** stores
before reading them, and `sweep` calls `alarm_repetition.escalate(...)` for every stale claim.
`refuse_if_duplicated` calls `overlapping_claims`, and is called by `run_once` itself (line ~808)
and by `tools/promote_worktree_landing.py` (line ~199).

## 2. The mechanism I predict from that, stated before looking

Forty-five minutes after any executor turn begins, the **next** unattended writer to call
`refuse_if_duplicated` — the next tick, or any promotion — sweeps `seat_work_in_hand`, finds the
finished turn's claim idle, and escalates:

```
[SEAT] <work-id> was claimed and has not moved for 0.8h
NO PATHS WERE EVER BOUND to this claim, so nothing about it could be observed …
```

**About a turn that finished, and possibly landed and promoted, three quarters of an hour earlier.**
This is R15's fail-silent shape wearing an alarm's clothes: not an instrument that cannot fire, but
one whose firing carries no information about its subject, because its subject's paths were never
bound into the store it reads.

It is also the exact shape the finding itself names one door along — the repair made acquire reach
three stores and left release reaching one, so the claim loop **gained a store and its release did
not**.

## 3. Predictions — the answers I do not have

**P1 (falsifiable, the load-bearing one).** The alarm record contains at least one
`seat-claim:<lane-0-slug>` escalation for a delivery-lane work id whose turn really landed a
commit. I predict **YES**, and that the ids will be the 2026-09-02/03 slugs
(`an-exit-code-is-not-a-landing`, `the-landing-verdict-can-never-say-yes-on-a-promoted-item`, or
their siblings).

*Refuted by:* no `seat-claim:` key for any lane-0 slug in the alarm store or in
`docs/staging/`. If refuted, the most likely reason is that the sweep has not yet been reached
since `b095fadf8` landed (about 12 hours), and the prediction becomes forward-looking rather than
wrong — I will say which of those it is rather than reclassifying it.

**P2.** After the repair, running a turn's claim/hand-back cycle leaves **no** record for the work
id in `seat_work_in_hand.CLAIMS_FILE`. I predict YES. *Refuted by:* the id still present after
`_hand_back`.

**P3 — the one that could make the repair wrong, and is why this is not a one-line diff.**
Releasing the `seat_work_in_hand` claim at hand-back could re-open the cross-lane path guard the
claim exists to close. I predict **NO harm**, because the record is written with `paths=[]` and
`overlapping_claims` skips records with no informative paths — so this claim never guarded a path
in the first place and dropping it removes no protection. *Refuted by:* any caller that reads
`seat_work_in_hand.held()` (rather than the paths) and would change its answer. `delivery_lane`
does not; `seat_continuity` reads the store for a post-mortem, which is a reason to release
truthfully, not a reason to leave a false claim standing.

**P4 — the release must be conditional in the same way `_hand_back` already is.** Releasing
unconditionally would let this turn drop a claim another writer re-took mid-turn. I predict the
`claimed_at` match is required in both stores and that a control mutating it away dies.

## 4. What I will NOT count as success

* `--release` printing anything. §10 is precisely about that.
* A test that claims into the store directly and then releases it. That passes under the defect —
  the defect is which stores `run_once` reaches, so the control must drive `run_once`.
* The three stores collapsing to two when `run_once` is imported **from a worktree**
  (`_worktree_claims()` and `delivery_lane.CLAIMS_FILE` are then the same file). That is a real
  observation, recorded here so it is not mistaken later for a finding: the executor runs from the
  shared tree, where the three are distinct. It is only a defect if something ever runs `run_once`
  from a worktree, and nothing does.

## 5. Grading — 2026-09-03, same turn, beside the predictions

### P1 — CONFIRMED, and by a stronger route than predicted

I predicted a `seat-claim:` escalation for a lane-0 slug and guessed it would be a per-slug
document. It is not: escalation is keyed on the *family*, so every seat-claim alarm appends to one
document, `docs/staging/WORKER_FINDING_REPEATING_ALARM_SEAT_CLAIM_2026-08-26.md`. Its tail ends:

```
- `land-the-dd-inference-organ-and-unwedge-every-lanes-publish` (first seen 2026-09-02)
- `compose-with-origin-and-land-the-census-repair-that-is-the-publish-wedge` (first seen 2026-09-02)
- `an-exit-code-is-not-a-landing` (first seen 2026-09-02)
```

Three consecutive executor turns, all three of which the executor's own log records as `FINISHED`.
The last is the strongest case available: `seat-executor-log.md` for the same turn reads

```
[2026-09-02 22:36 UTC] FINISHED an-exit-code-is-not-a-landing: rc=0 -- 1 of 1 bound path(s) moved
on the shared tree, including docs/staging/done/SEAT_FINDING_…_2026-09-02.md
```

**Two instruments on one turn, disagreeing.** The lane says the landing was bound and moved on the
shared tree; the alarm says nothing has moved. The alarm reads the only store the turn's paths are
never bound into, so it had no way to be right — and it reaches the director's queue, which the
log line does not. It fails in the *loud* direction, unlike the defect it descends from.

The prediction was right and the guess about the document shape was wrong; both are left standing
rather than the second being tidied away.

### P2 — CONFIRMED

`test_a_FINISHED_turn_leaves_no_claim_in_ANY_store_it_took_one_in`, both routes, asserts against
the three store files after a real `run_once`. Green.

### P3 — CONFIRMED, and the reasoning held for the reason given

Nothing was lost. The record carries `paths=[]` and `overlapping_claims` filters on informative
paths, so this claim never guarded a path and dropping it at hand-back removes no protection.

What P3 did *not* anticipate is the direction the risk actually ran in, found by mutation: removing
the store from the acquire as well (mutation B below) **also** removes the alarm, so the harm test
alone cannot tell the repair from a deletion. The store does earn its place, but for readers P3
did not name — `delivery_lane.release_refusal_reason` reads it to tell a tick that its release
could never have found the claim, and `seat_continuity` reads it for what a live seat thought it
was doing. Both want the claim present *during* the turn and absent after, which is exactly what
landed. **This is a correction to P3's stated reason, not to its answer.**

### P4 — CONFIRMED

`claimed_at` matching is per store; `test_the_hand_back_releases_only_the_claim_THIS_turn_took`
still passes with the loop widened, so a concurrent re-claim mid-turn still outlives the turn.

### Mutations run — three, two dead and one established as an equivalence

| # | Mutation | Result |
|---|---|---|
| A | `_hand_back` releases `(delivery_lane.CLAIMS_FILE,)` alone — the exact pre-repair code | **DIES** (3 tests). Both legs of the harm test checked separately: the sweep releases `['the-item']` *and* files `WORKER_FINDING_REPEATING_ALARM_SEAT_CLAIM_2026-09-03.md` into the staging dir |
| B | `_claim_stores()` drops `claims_mod.CLAIMS_FILE` from **both** ends | **SURVIVED the harm test — an equivalence there, established by running it.** No claim written is no claim orphaned. Killed by the mid-turn leg added for exactly this, which is the honest place for it |
| C | `_hand_back` releases `_claim_stores()[:2]` — the worktree store orphaned instead | **DIES** (2 tests) |

Green at rest: 29 passed.

### What is NOT claimed

The live log's next `FINISHED` line is not evidence for this until a real turn runs under the
repair and the sweep is reached 45 minutes later. That is forward-looking and recorded as
ungraded, as `SEAT_PREREGISTRATION_WHETHER_CLAIMING_IN_BOTH_STORES…` recorded its own.

### A process note against my own turn

I ran `git checkout <path>` on the test file to undo a scratch mutation and it reverted the
control I had just written along with it. CLAUDE.md names that command as one never to use here
and the reason is exactly this. Re-applied from context and re-proven from scratch — the mutation
table above is the second run, not the first.

---

## GRADED 2026-09-03 00:11 UTC — *"What is NOT claimed"* is now claimed

The forward-looking clause above ("the live log's next `FINISHED` line is not evidence for this
until a real turn runs under the repair and the sweep is reached 45 minutes later") is **closed,
and the prediction holds.** The real turn was `grade-the-repaired-writer-on-a-real-executor-turn`:
claimed 23:36 UTC in all three stores by one loop, released at 00:08, and absent from all three
stores when read at 00:11 — so the 00:21 deadline was never armed and no `seat-claim:` alarm can
fire for it. Evidence, including the check that the alarm writer was live and the pre-fix contrast
case at 22:53 UTC, is in §13.6 of
`docs/staging/done/SEAT_FINDING_THE_EXECUTORS_DISCHARGE_ASKS_A_STORE_ITS_OWN_CLAIM_NEVER_REACHES_2026-09-02.md`.
