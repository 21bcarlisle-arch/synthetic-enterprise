**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, claim `twenty-three-named-refusals-and-their-control-are-finished-and-uncommitted`

# The item was delivered and bound 11 minutes before it was drawn, and the only thing still owed was a push

*The drawn item described eleven dirty files and an untracked control. By the time it was handed
out, all fourteen paths were in a gated commit and every one of them was bound to the claim. What
was genuinely outstanding was not a commit — it was a push, and `origin_reconcile` made it four and
a half minutes into this turn. **I did not land this work and I am not claiming it.** What this turn
adds is the verification, the disposition, and one mechanical fact neither filed doc on this class
names: for the whole window between a local gated landing and the reconciler's push,
`--premise-spent` is structurally unable to say the premise is spent.*

---

## 1. The premise, re-measured before touching anything

The item's factual claims about the tree, against the tree:

| the item says | measured | verdict |
|---|---|---|
| "eleven dirty files under `company/`" | `git status -- company/` on the shared tree: **empty** | stale |
| "the UNTRACKED control `tests/company/test_a_register…py`" | tracked and clean | stale |
| "the untracked result doc" | tracked, inside the commit | stale |
| "the draw ledger records as `not_done`" | `last_landing_at` 22:24:14 ≥ `last_drawn_at` 22:17:15 — **DELIVERED** | stale |
| "the claim is bound to the commit" — the ask | already bound, all 14 paths | **already done** |
| the eleven files and the control are **on origin** | **not** on `origin/main` at draw time | the one live clause |

All fourteen paths sit in `d933508ff` *fix(company): twenty-three registers name the key, the book
and the registrar*, gate-rc 0, 1067 tests. Nothing was dirty and nothing was untracked.

## 2. The timeline, and the 11m33s

| time (BST, 2026-09-21) | event |
|---|---|
| 11:29:24 | `name-the-35-…` first drawn |
| 15:36–15:38 | the eleven `company/` files written — the state the item describes |
| 22:17:15 | `name-the-35-…` re-drawn |
| **22:24:14** | **`d933508ff` committed *and* bound — all 14 paths on the claim** |
| **22:35:47** | **this item drawn, describing the 15:38 state** |
| 22:40:16 | `8ea931ace` — `origin_reconcile`'s merge pushes it to `origin/main` |

The item was 11m33s behind the commit and ~7h behind nothing at all: the description it carried had
been false since 22:24.

## 3. What this turn actually did

Verified, rather than rebuilt. `origin/main`'s five commits touch **none** of the fourteen paths,
and `git merge-tree --write-tree d933508ff origin/main` produced tree `b1a019af7` with no conflict —
so the merge was clean and the reconciler (then 10 minutes into its gate) would carry it. **Landing
the same fourteen paths from this worktree would have refused that push as a lost race and delayed
the work further**, so the correct move was to wait on it by name — `tools.wait_for --pid 1845949`,
deadline 900s — and then check.

After `8ea931ace`, all fourteen paths are byte-identical between `d933508ff` and `origin/main`:

```
git rev-parse origin/main:<path> == git rev-parse d933508ff:<path>    14 of 14 OK
```

`d933508ff` is an ancestor of `origin/main`. The item's FINISHED condition — *the eleven files and
the control are on origin, the claim is bound, the result doc is filed rather than untracked* — is
met on all three clauses.

## 4. The disposition, and the verb that refused

The duplicate-work check said to take `--landed-under <this id> <that id>` if the work had already
landed. It had. **It refused:**

```
credited NOTHING to twenty-three-named-refusals-…: … was never drawn --
the ledger has no row for it, so there is no draw for a landing to reach
```

This id is in `.seat_work_in_hand.json` and in `.delivery_lane_claims.json`, and is **not** among
the 400 rows of `.delivery_lane_claims.draws.json`. That is precisely the clause
`SEAT_RESULT_THE_DRAWN_ITEM_WAS_SPENT_BEFORE_IT_WAS_DRAWN_AND_NO_DISPOSITION_COULD_REACH_IT_2026-09-21.md`
filed as BLOCKING today — *"the draw that handed it out wrote the claims store and not the draw
ledger"*. **This is a second, independent instance of it, hours later, on a different id.** That doc
owns the class and nothing is re-filed here; this is corroboration, and it raises the instance count
from one to two.

The disposition taken is therefore `--release`, recorded here as the item asks.

## 5. A prediction filed before measuring, and the conclusion I drew from it that was wrong

> *Predicted (written to `~/.cache/seatpred/prereg_2026-09-21.txt` before reading the function):
> `--landed` performs no `merge-base --is-ancestor <commit> origin/main` check, so a claim can read
> "landed, 14 paths bound" while `origin/main` has none of them.*

**Confirmed.** `record_landing` enumerates its refusals exhaustively — unclaimed id, unreadable
commit, heartbeat republish, commit older than first draw — and origin-ancestry is not among them.
`d933508ff` sat in exactly that state from 22:24:14 to 22:40:16.

**And the remedy I was reaching for is wrong, which the measurement itself showed.** I went looking
for this expecting an asymmetry worth closing, because `--premise-spent` twenty lines away *does*
refuse a non-ancestor. It should not be closed. `--landed`'s job is to stop a sweep on a tick that
did real work; requiring the commit to be on origin would sweep every landing whose promote lost a
race — including this turn's. The two verbs answer different questions and are right to differ:
`--premise-spent` makes a durable claim about *another* item's premise, `--landed` a local claim
about *this* tick's progress. Recorded here rather than quietly dropped, because a prediction filed
before the answer and then corrected is the only evidence the question was asked honestly.

## 6. The one thing neither filed doc names

`--premise-spent` refuses a spender that is not an ancestor of `origin/main`
(`background/delivery_lane.py:2567`), for a stated and correct reason: *"an unpublished spender is a
claim about the future, and it may still be rebased away."*

A `surgical_land` landing is not on `origin/main` until `origin_reconcile` pushes it on its cadence.
**So there is a window — 16 minutes here, 22:24:14 to 22:40:16, and as long as the cadence at worst —
in which an item's premise is demonstrably spent and no verb can record that it is.** A worker drawn
inside it (this one was, at 22:35:47) sees a live-looking item, a refusing disposition, and work
that appears uncommitted because the census asks the filesystem.

**The remedy is not to weaken the guard.** It is that the right move inside that window is to *push
the spender* and then dispose — which is what happened here, and what the next worker drawn into
this window should do rather than rebuild. Filed as the observation; no mechanism is proposed,
because a guard over a daemon's cadence is the kind of control that only watches other controls.

## 7. What is left

1. The two items §7 of
   `WORKER_RESULT_TWENTY_THREE_REGISTERS_NAME_THEIR_REFUSAL_AND_THE_THIRTEEN_LEFT_CANNOT_REFUSE_AT_ALL_2026-09-21.md`
   already owns, and they are unaffected by any of this: widen
   `_membership_guarded` to see the early-return/early-raise idiom (until then the survey's BARE
   count has a floor of 13 that no repair can move), and decide whether
   `TriadNotificationBook.issue_alert` and `HedgingSchedule.add_contract` should carry the full
   three-part message.
2. `name-the-35-…` still holds a claim whose work is delivered, bound and pushed. Its own worker
   (pid 1812972) was still live at the end of this turn, so releasing it is left to that writer
   rather than raced; its draw-ledger row already reads DELIVERED, so it is not re-offered as
   unstarted in the meantime.
