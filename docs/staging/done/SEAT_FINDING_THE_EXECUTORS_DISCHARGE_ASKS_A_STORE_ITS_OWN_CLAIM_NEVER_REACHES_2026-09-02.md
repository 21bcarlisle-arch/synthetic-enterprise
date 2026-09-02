# [SEAT FINDING] The executor's discharge asks a store its own claim never reaches, so the condition is never false

**Severity:** LATENT (the blast radius is now confined to turns that really landed — see §4 — but
the mismatch itself is untouched) · **Lane:** H_harness
**Epoch:** 3 · **Atom:** none — this is Lane 0 delivery machinery
**Found:** 2026-09-02 by the delivery seat, while building the subject-reading verdict that
`an-exit-code-is-not-a-landing` asked for. Found by the live-ledger guard refusing a test fixture,
not by looking for it.

## Class registration

Belongs to `controls_that_cannot_fail`. The specific shape is R15's fourth: a branch whose
condition is never false, so the verdict is a constant. Same shape as the thirty-two consecutive
stand-downs `background/seat_executor.py` already documents against itself — *"a refusal whose
condition is never false is not a control; it is a disconnected wire that reports itself as
safety"* — arriving through the opposite door: a DISCHARGE whose condition is never false.

## 1. The two stores

`background/seat_executor.py:735`, inside `run_once`, before the session is spawned:

```python
delivery_lane.claims_mod.claim(work_id, note=str(item.get("what") or "")[:200], paths=[])
```

No `path=`. `claims_mod` is `background/seat_work_in_hand.py`, so this writes
`docs/observability/.seat_work_in_hand.json`.

`_still_claimed`, after the session, asks `delivery_lane.held()`, which is

```python
return set(claims_mod.held(path=path or CLAIMS_FILE))   # delivery_lane.CLAIMS_FILE
```

— `docs/observability/.delivery_lane_claims.json`. **Two different files.** The executor writes its
claim into one and reads for it in the other.

## 2. Measured, not inferred

On disk at 2026-09-02 22:1x UTC, with a turn's claim live:

```
.seat_work_in_hand.json    -> ['compose-with-origin-and-land-the-census-repair-that-is-the-publish-wedge']
.delivery_lane_claims.json -> []
```

The claim is in the store nobody asks, and the store that is asked is empty.

## 3. What that makes true

`_still_claimed` returns False for every turn the executor takes by the PROMOTED CONTINUATION
route — which is its busiest route, because `_promote_to_handoff` is how a re-derived focus item
reaches a tick at all, and a promotion never goes through `delivery_lane.draw()`, which is the only
thing that writes the delivery-lane claim.

So the discharge fires unconditionally. `docs/observability/seat-executor-log.md` for 2026-09-02
carries a `DISCHARGED ... the tick released its claim` line after **every single turn** — 15:46,
16:42, 17:56, 18:55, 20:17, 20:48 — and the reason it gives is false in all six: no tick released
anything, because no tick ever held a claim in that store.

The discharge's own comment says what it was for: *"RE-OFFERING IS DELIBERATE while work is
unfinished ... If it did not release, the continuation stands and the next tick continues."* That
sentence describes a mechanism that has never run. Every handoff has been consumed after one turn,
whether or not the work was finished.

## 4. Why this is LATENT rather than BLOCKING, as of this commit

The discharge is now downstream of the subject-reading verdict landed alongside this finding: a
turn that did not move its bound paths on the shared tree returns before reaching
`_still_claimed` at all. So the unconditional discharge can only fire on a turn that genuinely
landed something, where consuming the handoff is at worst premature rather than a silent loss.

That is a narrowing of blast radius, **not a fix**, and it should not be read as one. A piece of
work bigger than one turn still gets its continuation dropped after the first increment lands.

## 5. Why I did not fix it here

Because which store owns which question is a real design call and I could not settle it inside this
turn without guessing:

* `seat_work_in_hand` is the CROSS-LANE PATH GUARD's store. `refuse_if_duplicated` reads it, and
  the executor genuinely needs its work declared there so another writer cannot take the same
  paths. Claiming there is correct.
* `delivery_lane`'s store is where a tick's `python3 -m background.delivery_lane --release <id>`
  goes, and where `draw()` records a handout. Asking it "did the tick say it was done" is correct.

Both halves are individually right. What is missing is anything that makes the executor's OWN
claim visible to the release channel — and note the second-order trap in §6 before choosing the
obvious repair.

## 6. The trap any repair has to clear first

`delivery_lane.PROJECT_DIR` is `Path(__file__).resolve().parent.parent`. The executor's child runs
with its cwd inside the worktree, so `python3 -m background.delivery_lane --release <id>` from
there imports the WORKTREE's copy of the module and writes the WORKTREE's store, which
`ensure_worktree` resets at the start of the next turn. The shared store never hears it.

So "make the executor claim into the delivery-lane store" would move the discharge from
*never false* to *never true* — the mirror-image constant verdict — unless the child is also told
to run its `--release` against the shared tree. The charter landed with this finding now names
that for `--landed`; it does not yet name it for `--release`.

## 7. What would settle it

A control that runs one real turn and asserts the discharge fires when the tick released and does
NOT fire when it did not — i.e. one that exercises both branches. Today no test reaches
`_still_claimed` with a True answer, which is why a condition that has never once been false has
survived in a module whose own docstring is about exactly this failure.

## 8. Prediction, written before the repair

If the repair in §5 is made without §6's clause, `seat-executor-log.md` will stop carrying
`DISCHARGED` lines entirely, and the first symptom will be a continuation re-offered indefinitely
after the work is finished — a livelock, not a silence. If §6's clause is included, the log should
carry `DISCHARGED` on some turns and not others within a day. **Neither has been observed yet.**
