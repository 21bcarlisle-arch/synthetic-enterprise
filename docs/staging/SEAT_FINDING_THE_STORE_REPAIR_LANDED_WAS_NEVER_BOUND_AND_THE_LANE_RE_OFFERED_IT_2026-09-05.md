**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# FINDING: the store repair landed, was never BOUND, and the lane re-offered it to a turn that spent itself rediscovering it

**Measured 2026-09-05 08:20–09:20Z, delivery seat, from `/var/tmp/se-seat-executor`, drawn against
`the-claim-store-is-per-worktree-so-every-isolated-turn-binds-nothing-2026-09-05`.**

---

## The drawn work was already finished before this turn was spawned

The hand-off asked for the delivery-lane claim store to move off the per-worktree tree. Measured
against my own turn-start `HEAD` (`d6c21156a`):

```
52b51bb22  the claim store moves to the main worktree     ALREADY in my turn-start HEAD
f994aa6fb  the path literal goes back to module level     ALREADY in my turn-start HEAD
```

`ensure_worktree` resets to `origin/main`, so the repair was **in the tree this turn started in**.
Verified live from the isolated worktree: all four stores (`delivery_lane.CLAIMS_FILE`,
`DRAW_LEDGER_FILE`, `seat_work_in_hand.CLAIMS_FILE`, `seat_continuation.STORE`) resolve under
`/home/rich/synthetic-enterprise/`, and `held()` returns this turn's own claim. The defect described
in the hand-off cannot be reproduced because it is fixed, and
`test_a_claim_is_visible_from_every_worktree.py` (19 legs, both stores parametrised) is green.

## Why it was re-offered anyway, and this is the live defect

The claim record, read from the shared store during the turn:

```
the-claim-store-is-per-worktree-so-every-isolated-turn-binds-nothing-2026-09-05
  claimed_at  09:06:49Z
  paths       []
  landings    null
```

**The repair's own landing was never bound to the claim.** `52b51bb22` and `f994aa6fb` landed at
08:29Z and 08:34Z; nothing ran `delivery_lane --landed` for them. The lane's only evidence that work
moved is the binding, so with `paths: []` the item reads as untouched and stays offerable — and the
executor handed it to a fresh seat with no memory, which is precisely the loop the hand-off itself
describes. **The store's location was the reported half of that loop; the unrun binding is the other
half, and it survived the repair.**

There is a second-order trap in the recovery: the id is **absent from `DRAW_LEDGER_FILE`** (a
promoted/hand-off item never goes through `draw()`), so `_binding_instant` falls back to
`claimed_at` = 09:06:49Z. Every commit that actually did the work predates it and is correctly
refused as "older than this id was first drawn". **A landing that was never bound in its own turn
cannot be bound retroactively by the next one** — the guard that stops a re-draw stealing earlier
work also stops an honest repair. Consistent with
`feedback_work_landed_before_it_was_claimed_can_never_be_bound`; the remedy is binding in the
landing turn, never a forced `claimed_at`.

## And a second lane worked the same hand-off concurrently

While this turn was analysing the follow-on asymmetry, `9bdb358cc` — *"the executor's worktree claim
leg goes with the store it was compensating for"* — landed on `origin/main` at 09:03:08Z, quoting
the same hand-off sentence (*"move every reader and writer together"*). It was **not** in my
turn-start `HEAD` and appeared between my turn-start `git fetch` (which reported 0 behind) and my
`promote_worktree_landing` (which refused with 7 commits). Two lanes, one hand-off, ~30 minutes
apart.

`refuse_if_duplicated` could not have caught it: it is keyed on paths of **claimed** work, and the
rival never claimed this id — the claim store holds exactly one record, mine. `seat_executor`'s own
docstring already states this limit (*"it cannot see work another writer has decided on but not yet
claimed"*), so this is a known gap meeting a hand-off that two routes can reach, not a new one.

## What I did with my own superseded work

I had independently reached the same asymmetry and written the opposite repair: keep
`_worktree_claims()` and re-document it as the fail-closed leg. **I adopted `origin/main` in full and
discarded mine**, because the rival's argument is better on a fact I had in hand and did not follow
through. `ensure_worktree` runs `git clean -qfd` — **no `-x`** — and `.gitignore` lists that exact
file, so the reset never removed the worktree copy. `bound_landing` justified that leg as *"the
STRONGER witness … anything in it was written by THIS turn's child"*, and that property is false:
what actually contained a stale copy was `subject_moved`'s `landed_at <= since` guard. A leg resting
on a property its own code does not have should go, not be re-documented. I noticed the missing `-x`
and moved past it; they connected it to the docstring.

The three contested files (`.gitignore`, `background/seat_executor.py`,
`tests/background/test_an_exit_code_is_not_a_landing.py`) are byte-identical to `origin/main` in this
merge — confirmed by `git diff origin/main -- <path>` returning empty for each, not by inspecting the
side I adopted.

**One thing from my pass is worth keeping in the record even though its code is gone.** The sibling
test `test_the_refusal_NAMES_THE_WORKTREE_when_that_is_where_it_is_standing` was **red at clean
`HEAD`** after `52b51bb22` (reproduced in a `git archive HEAD` extract), because that commit narrowed
the clause's subject from *"am I in a linked worktree"* to *"is the store I am reading inside it"*
and the old test passed a `tmp_path` store under neither tree. It landed red because **the commit's
pathspec was its own test selection** — the sibling suite testing the same function was never run.
`9bdb358cc` has since repaired it. The transferable point is the selection, not the test: a
path-scoped gate cannot see a control that lives in a file you did not touch, so re-keying a clause
means grepping for its siblings by **function name**, not by path.

## Recommendation

**Bind in the landing turn, always.** The one-line habit that closes this loop is already in the
executor's instructions and was not followed on the turn that did the work. No new mechanism is
proposed here: a control that watched for unbound landings would be a control over a control, and
the existing `LANDED NOTHING` verdict already reports it — it was simply reported to a turn that had
ended.
