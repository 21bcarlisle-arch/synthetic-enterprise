**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — resolve the selection leg by seeds because the ranking cut already names its sign) · **Class:** `publish_gate_and_wedge`

# The two-rooms repair's recorded cause is refuted, and the root copy comes back from origin

**2026-09-09, scheduled tick.** `background/finding_classes --check` is one of the cheap gates every
commit runs, and the gates read the whole tree rather than a pathspec. So a single document in two
rooms refuses **every lane's landing** — including the 9-seed floor publish this box is three hours
into computing. It was red when this tick started, and it is red again now.

---

## What the repair module says, and why it is no longer true

`background/staging_two_rooms_repair.py` is explicit that it never identified the writer, and it
records the one observation it had:

> What is observed: the file reappeared at 10:20 and 11:25, and **stopped reappearing once its
> deletion was COMMITTED** rather than merely made in the working tree. That is consistent with
> something restoring a tracked-but-deleted path from HEAD…

and, in its own design notes:

> IT STAGES THE DELETION, which is the half that makes it stick. Removing the file from the working
> tree alone leaves the path tracked at HEAD, and every operation that restores a tracked path can
> bring it back.

**That cause is refuted.** The deletion is now committed — `8903ae99a` moved
`SEAT_PREREG_RECONCILING_THE_TWO_VALUE_ARMS_CONSTANT_SETS_ONTO_THE_PROMOTED_ONE_2026-09-09.md`
from the staging root to `records/`, and git recorded it as an `R100` rename, so **HEAD does not
track the root path at all**:

```
$ git ls-tree -r HEAD --name-only | grep SEAT_PREREG_RECONCILING_THE_TWO_VALUE_ARMS
docs/staging/records/SEAT_PREREG_..._2026-09-09.md        <- one room, records/ only
```

The root copy came back anyway, **at 11:35:28, ninety seconds after the repair cleared it**, with
the path untracked at HEAD. Nothing can restore a tracked-but-deleted path that is not tracked.

## The mechanism that IS available, stated as what it is

`surgical_land` never pushes. So:

```
$ git rev-list --left-right --count origin/main...HEAD
1       2                      <- origin is 1 ahead of us; we are 2 ahead of origin
$ git ls-tree -r origin/main --name-only | grep SEAT_PREREG_RECONCILING_THE_TWO_VALUE_ARMS
docs/staging/SEAT_PREREG_..._2026-09-09.md                <- the ROOT path, still tracked on origin
```

**`origin/main` still tracks the root copy**, and both the rename (`8903ae99a`) and the commit
before it (`ac41c7c6e`) are unpushed. Any lane that checks out, refreshes or reconciles against
`origin/main` re-creates the root copy in this tree — and several daemons do exactly that on a
timer.

**What is established and what is not.** Established: HEAD does not track the path, origin/main
does, and the file reappears within minutes of every deletion. That is enough to refute the
module's recorded cause, which is the load-bearing claim here. **Not established: I did not catch
the writer in the act and I am not naming one.** Origin-restore is the mechanism the evidence makes
available; it is not a process I observed writing the file. The module's own refusal to name a
cause it could not show is the right standard and this document keeps to it.

## Why this matters more than one stuck document

The repair exists so nobody clears this by hand four times in six hours. It still clears the state
correctly — `--repair` removed the copy and `--check` went to PASS. But its **stopping condition is
wrong**, and a repair whose recorded cure does not end the recurrence will be run, believed, and
re-run forever. The failure is in the module's model of the world, not in its delete.

There is also a state the repair cannot reach on its own. Once the move is *committed*, the
leftover root copy is **untracked**, and `_git_rm` is a `git rm` — the one call that has nothing to
remove. It happened to succeed here because the shared index still carried the other lane's staged
entry for that path. On a clean index the same repair would report a CONFLICT on a file that is
provably redundant, which is the timid direction and therefore safe, but it is not the behaviour
the docstring describes.

## What is next

1. **Push, or reconcile deliberately.** While `origin/main` carries the root path and this tree does
   not, the two disagree and the tree loses. Origin is 1 ahead, so this is the moved-origin
   reconciliation, not a fast-forward — `reset --mixed` and re-land, never a plain `git merge`,
   which lands without a receipt. **Not done in this tick on purpose:** a 3.9-hour floor run
   (`longjob-arms-rerun-20260909b.service`, PID 704091) is live in this tree and the shared index
   holds 13 of another lane's staged files. Reconciling under both is how a lane's work gets swept.
2. **Correct the module's observation in place**, beside the claim it refutes — the docstring says
   committing the deletion ends it, and it does not.
3. **Decide whether `_git_rm` should fall back to a plain unlink** for the provably-redundant
   untracked case. It is the state that completing an archive move now produces.

## What this tick did land

`8903ae99a` — the move completed, `records/` chosen as the room because every other
pre-registration lives there, including this Lane 0 item's own
`SEAT_PREREGISTRATION_WHAT_SIX_MORE_SEEDS_DO_TO_THE_SELECTION_LEGS_SIGN_2026-09-09.md`. All three
copies were byte-identical at md5 `24f04f563fed7a1a3a61468f4e57bf58`, so no content was chosen
between and none was at risk.

The first landing attempt was **refused, correctly**, and the refusal is worth keeping: passing the
root path positionally with the file already gone from disk does **not** land a deletion. The gate
ran on the tree the commit *would* create, found TWO ROOMS still live in it, and refused.
`--content-remove` **and** the positional path are both required. A working tree that passes while
the resulting tree does not is exactly what landing this way exists to catch.
