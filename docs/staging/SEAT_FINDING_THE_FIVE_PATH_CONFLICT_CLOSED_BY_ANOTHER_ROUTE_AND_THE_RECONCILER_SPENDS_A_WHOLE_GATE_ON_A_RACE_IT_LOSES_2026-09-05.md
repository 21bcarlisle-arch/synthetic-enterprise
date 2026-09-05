**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# FINDING: the five-path conflict closed by another route, and the reconciler spends a whole gate on the one race it has no retry for

**Measured 2026-09-05 09:32–09:45 BST, delivery seat, from an isolated worktree.
Shared tree `/home/rich/synthetic-enterprise`; `origin/main` = `53c46519e` at the close.**

Drawn against claim `resolve-the-shared-trees-five-path-conflict-with-origin-2026-09-05`, whose
own draw-time premise check had already flagged all five cited commits as ancestors of origin.
This document is the "say so in staging and release" that the draw asked for — plus the one thing
the re-measurement turned up that was not already known.

---

## 1. The drawn premise is spent, and so is its successor

The item asked me to resolve a 5-ahead/32-behind fork across five conflicted paths with
`surgical_land --merge origin/main --resolve <path>=<file>`. Re-measured before starting:

| what the item said | what is true at 09:32 |
|---|---|
| shared tree 5 ahead, 32 behind | **2 ahead, 6 behind** |
| `88d493ac9` `7b3134f86` `5b4e5602e` `f459f9895` `aab6fb990` not on origin | **all five are ancestors of `origin/main`** (`git merge-base --is-ancestor`, five for five) |
| 5 conflicted paths needing a side decided | **`git merge-tree --write-tree HEAD origin/main` exits 0 — no conflict** |

So the fork the item names was resolved by another route before I was drawn, and the fork that had
replaced it was a *clean* divergence, not a conflict. The two commits standing in it — `f994aa6fb`
and `52b51bb22`, both `background/delivery_lane.py` / `background/seat_work_in_hand.py` work — had
no counterpart on origin touching the same hunks.

**Nothing in the drawn work was done, because there was nothing left to decide.** No side of any
path was chosen by me.

### The resolution that did happen was correct, checked rather than assumed

A fork closing is not the same as the paths being right, so I checked the resolution rather than
inferring it from the absence of conflict. All five formerly-conflicted paths are present on
`origin/main`, none carries a conflict marker, and the item's own stated checkable claim for
`background/process_run_complete.py` holds exactly:

```
git show origin/main:background/process_run_complete.py | grep -c 'THE DIVERGENCE WAS NOT THE ONLY THING THE ADVANCE INVALIDATED'  -> 1
git show origin/main:background/process_run_complete.py | grep -c 'AND THE SAME ADVANCE AT THE OTHER COMMIT SITE'                  -> 1
```

One occurrence each — not zero (side dropped), not two (both sides concatenated). Origin's side won
on that path, which is the answer the item said was already established.

### What closed the remaining 2/6, during this turn

`git reflog` on the shared tree: `surgical-land` at **09:38:57 BST** moved it `f994aa6fb → 53c46519e`,
and `origin/main` is that same sha. Another lane's merge, by the sanctioned door. The shared tree
finished this turn at **0 ahead, 0 behind** — the wedge the finding of record
(`…FIVE_PATH_CONFLICT_NOTHING_UNATTENDED_WILL_RESOLVE_2026-09-05.md`, BLOCKING) described is closed,
and the publisher's `_divergence_refusal` no longer has a fork to refuse on.

---

## 2. The thing the re-measurement DID turn up

Before the tree reached 0/0 I ran `python3 -m background.origin_reconcile` against the live 2/6
divergence. Its whole output:

```
ERROR: merge gated clean but the push was rejected: To https://github.com/.../synthetic-enterprise.git
 ! [rejected]            HEAD -> main (non-fast-forward)
error: failed to push some refs to '...'
hint: Updates were rejected because a pushed branch tip is behind its remote
```

**The merge was built. The gate ran on it and came back clean. Then the push was refused because
origin had moved underneath, and every minute of that gate was discarded** —
`background/origin_reconcile.py:785-789`:

```python
pushed = (pusher or _push)(worktree)
if pushed.returncode != 0:
    return {"status": ERROR, "behind": behind, "pushed": False,
            "detail": "merge gated clean but the push was rejected: {}".format(...)}
```

There is no retry. `grep -nE 'attempts|retry|retries|re-gate' background/origin_reconcile.py`
returns nothing.

### Why this is the interesting half, not just bad luck

The module already knows this race exists and guards it *in the other direction only*.
`gate_is_running()` at `background/origin_reconcile.py:657` carries the director's 2026-09-02 rule
verbatim — *"NEVER MOVE ORIGIN UNDER A RUNNING GATE … a push that lands while it runs turns a green
gate into a non-fast-forward refusal at the last step, so the whole run is spent and discarded"* —
and refuses to act while `process_run_complete` holds its lock.

That protects **the publish gate from the reconciler**. Nothing protects **the reconciler from
anyone else**. The failure the comment describes is precisely the failure I observed, with the
reconciler on the losing end of it, and the module that wrote the comment is the one it happened to.

The obvious-looking mitigation one level down does not reach it: `surgical_land --attempts N`
("re-gate against the new base up to N times when HEAD moves under the gate", default 3) keys on
**HEAD** moving. In the reconciler's fresh isolated worktree nothing else moves HEAD, so `--attempts`
can never fire there. The race that actually happens is **`origin/main` advancing between the merge
and the push**, and that one is unguarded.

### Two distinct defects, and the second is the one that costs

1. **The spent gate.** One reconcile cycle's gate work is thrown away on each lost race. Bounded —
   the next cadence re-fetches, re-merges on the new base and gates again — so the cost is latency
   plus one gate, not a wedge.
2. **The status lies about its kind.** A lost race and a genuinely broken push both return `ERROR`
   with only free-text to tell them apart. This is the same shape as
   `SEAT_FINDING_AN_UNATTRIBUTED_PUBLISH_FAILURE_NAMED_NO_REASON_ON_THREE_OF_ITS_FOUR_BRANCHES_2026-09-04.md`:
   a refusal that does not name its reason cannot be counted, so a benign, self-healing race is
   indistinguishable in the record from a reconciler that is actually broken. **That is what makes
   this worth a status rather than a comment** — CLAUDE.md's *"write refusals that name their
   reason"* is exactly the rule the `ERROR` branch fails.

Why LATENT and not BLOCKING: nothing on any surface depends on it, every control's verdict stands
untouched, and the condition is self-clearing on the next cadence. It is a real defect that wastes
real compute and pollutes the failure record — not an untrustworthy instrument.

---

## 3. What is owed

- **Nothing on the five paths.** Resolved correctly by another route; verified above, not assumed.
- **The BLOCKING finding of record describes a state that no longer exists** —
  `SEAT_FINDING_THE_SAME_REPAIR_LANDED_TWICE_AND_THE_SHARED_TREES_COPY_IS_NOW_A_FIVE_PATH_CONFLICT_NOTHING_UNATTENDED_WILL_RESOLVE_2026-09-05.md`:
  0 ahead, 0 behind, no conflict, no marker.

  **CORRECTION, written beside the claim rather than over it.** An earlier draft of this line said
  that finding "can be discharged". **It cannot, and I was wrong to write it.** A discharge under
  `background/finding_severity.py` is a claim that the defect *cannot recur*, and it is fail-closed:
  it requires at least one named test node that exists and is runnable. No such falsifier exists
  here, because what was fixed was the **instance** and not the **class** — `origin_reconcile` still
  refuses on conflict, by design and correctly, and there is still no unattended resolver for a
  *conflicted* fork. The severity stands on the class claim, which is unchanged and still true.
  Discharging on "the state is gone" would have been exactly the false discharge that
  `false_discharges()` exists to surface. **The fork closing is not the finding being answered.**
- **Owed, and handed on:** a distinct non-fast-forward outcome in `reconcile()`, separate from
  `ERROR`, so the record can count races apart from failures. Done means a status that a lost push
  race yields and a genuinely-failed push does not, with a control that can fail on the distinction
  — inject a `pusher` returning a non-fast-forward stderr and assert the status is NOT `ERROR`, and
  a second leg injecting an unrelated push failure and asserting it IS. Both legs, or the guard
  passes by refusing everything.

## What I would have got wrong

Had I taken the draw at face value I would have re-resolved five paths that were already resolved,
and `--resolve` would have written *my* choice of side over a merge another lane had already reasoned
through and landed — turning a closed fork back into an open one. The premise check at draw time is
what stopped that, and the hazard re-measurement is what stopped me from treating "the commits are
ancestors" as "there is nothing here at all": the successor fork was real at 09:32, and the
reconciler defect above only became visible because I ran the mechanism against it while it was.
