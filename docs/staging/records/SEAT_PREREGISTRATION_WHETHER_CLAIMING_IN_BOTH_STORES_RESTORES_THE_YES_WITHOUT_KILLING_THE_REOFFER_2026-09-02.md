# [SEAT PRE-REGISTRATION] Whether claiming in both stores restores the verdict's *yes* without killing the re-offer

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery machinery
**Filed:** 2026-09-02, BEFORE the repair and before its measurement, by the seat turn that drew
`an-exit-code-is-not-a-landing` and found the direction's code already landed and its two follow-on
defects filed but unfixed.

## Why this is filed at all

`docs/staging/done/SEAT_FINDING_THE_EXECUTORS_DISCHARGE_ASKS_A_STORE_ITS_OWN_CLAIM_NEVER_REACHES_2026-09-02.md`
§9.5 recommends **repair A** — `run_once` claims into the delivery-lane store as well — and §10.2
adds the clause that `--release` must report what it actually did. Both are right. But A as stated
has a second-order consequence the finding does not name, and it is in the same class as the defect
being repaired, so it is written down here BEFORE the repair rather than discovered after it.

## The consequence the finding does not name

`delivery_lane.next_item` filters on `held(store)`:

```python
taken = held(store)
for item in seat_continuation.live(now=now):
    if item.get("id") and item["id"] not in taken:
        return item
```

**A claim in the delivery-lane store is exactly what stops an item being offered again.** So repair
A, applied naively, buys the verdict's *yes* at the cost of the re-offer that
`an-exit-code-is-not-a-landing` exists to protect: a `LANDED NOTHING` turn would leave its own claim
standing, `next_item` would skip the continuation, and the item would wait for the 100-minute sweep
instead of the next tick. The mirror-image constant again, one door further along — the verdict
would say *no* correctly and the item would not come back.

This is the whole reason the repair below is not the one-line diff §9.5 describes.

## The repair being measured

1. `run_once` claims into the delivery-lane store — **both copies**: the shared tree's (so a
   concurrent draw cannot hand the same item out mid-turn) and the worktree's (so the child's
   `--landed` and `--release`, which import the worktree's `delivery_lane`, find something to bind
   and something to remove).
2. The executor **hands its own claim back** after the verdict is read, and only its own —
   matched on `claimed_at`. This is what keeps the re-offer alive, and it is why 1 does not cost
   what this pre-registration says it would otherwise cost.
3. `_still_claimed` asks **both** delivery-lane stores and is read BEFORE the hand-back, so the
   tick's release and the executor's own hand-back cannot be confused for one another.
4. `seat_work_in_hand.release` returns whether a record was actually removed; the `--release` CLI
   prints the refusal and names the store when it removed nothing (§10.2).

`delivery_lane.CLAIMS_FILE` is deliberately **not** given §9.4's shared-tree resolution. Both
readers now union the two stores, so it is unnecessary — and pointing that module-level constant at
the shared tree would have every worktree child writing the live shared records, which is the
opposite of what the worktree is for.

## Predictions, written before any of it was run

1. **The verdict can say yes on the promoted route.** A promoted item taken through a turn that
   binds a landing scores `FINISHED`, not `LANDED NOTHING`. This is §9.7's prediction and it is
   the one this repair exists to move.
2. **The re-offer survives.** After a `LANDED NOTHING` turn, the work id is ABSENT from the shared
   delivery-lane store, so `next_item` offers the continuation again on the next tick. If I am
   wrong about the hand-back, this is where it shows, and the symptom is a silence — an item that
   simply stops being offered — not an error.
3. **`--release` on an unclaimed id prints a refusal and exits non-zero.** Today it prints
   `released <id>` unconditionally and exits 0 (§10).
4. **Both branches of the discharge become reachable.** §7 asked for this and §9.6 added the clause
   that it must be exercised on both ROUTES. If only one route is exercised the control passes
   whichever repair is chosen, which is the trap §9.6 names.

## What would refute the repair rather than confirm it

A test that claims directly into a fixture store and asserts the verdict says yes. That passes
under the OLD code too if the fixture happens to write the store `_still_claimed` reads, which is
precisely how `test_the_verdict_is_not_the_exit_code` stayed green and honest while the production
path was a constant. **The control has to drive `run_once` and let the ROUTE choose the store.**

## Discharge

**Discharged 2026-09-02 by the commit that lands the repair.** Full grading, with every mutation
run, is §12 of the finding this pre-registers against. In short:

* Prediction 1 — **held.** test_the_verdict_can_say_YES_on_the_PROMOTED_route, which dies to
  dropping the worktree store from run_once's claim loop.
* Prediction 2 — **held.** test_a_LANDED_NOTHING_turn_leaves_the_item_DRAWABLE_AGAIN, which dies to
  deleting the hand-back. The consequence this document was filed to name is real and is paid for.
* Prediction 3 — **held, and landed by another lane rather than by me.** A concurrent seat landed
  the same §10.2 repair as 551d1aadf while this turn was building. Its version is equivalent and
  slightly richer (it separates the causes in the refusal reason), so it was ADOPTED and my
  duplicate dropped rather than merged. Its controls are
  test_release_reports_whether_a_record_WAS_ACTUALLY_REMOVED and
  test_the_release_CLI_REFUSES_instead_of_printing_success.
* Prediction 4 — **held.** Both routes and both discharge branches are exercised, and both
  _still_claimed and release die to a constant in EITHER direction.

Ten mutations run, ten died. The one thing this document got wrong about its own repair: it
expected to need §9.4's shared-tree resolution of the delivery-lane store, and that turned out to
be unnecessary and harmful — see §12.2. Recorded here rather than quietly dropped.
