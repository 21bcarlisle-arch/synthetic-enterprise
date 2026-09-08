**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The stale-copy census — this class's own acceptance test — crashes for every lane in the shared tree, because the modules it imports are on origin and were never written to disk

**Filed 2026-09-08 by the delivery seat (lane 0). Found by running the check the previous finding
named as "the check, not this document", and having it raise instead of answer.**

## What was measured

`WORKER_FINDING_EIGHT_WORKING_COPIES_...` ends by telling the next reader to regenerate its table:

> `python3 -m tools.stale_copy_refusal --census --root /home/rich/synthetic-enterprise` regenerates
> this table; **it is the check, not this document.**

Run in the shared tree, on 2026-09-08:

    File "/home/rich/synthetic-enterprise/tools/stale_copy_refusal.py", line 475, in door_verdicts
        from tools import landing_pair, refresh_to_head  # deferred: see the docstring
    ImportError: cannot import name 'landing_pair' from 'tools' (unknown location)

`tools/landing_pair.py` and `tools/refresh_to_head.py` **do not exist on disk and are not tracked in
this tree.** Both are on `origin/main`, added by `a9f3288c8`. So are their two test files.

## The mechanism, and it is the one this repo already has a name for

`git rev-list --left-right --count HEAD...origin/main` → **`0	7`**. Not a divergence: the shared
tree is seven commits *behind*, nothing local is unpushed, and a fast-forward is the whole repair.

Of the 18 paths those seven commits change, **four are pure additions that are simply absent from
disk** — the two modules above and their two test files. The other fourteen are present at their
older content. `git ls-files` does not list the four, so every census, ratchet and orphan scan in
this tree is blind to them; they are not stale copies, they are *nothing at all*.

`background/origin_reconcile.py` says exactly why, in its own docstring, and it is working as
designed:

> **WHAT IT CANNOT DO.** It cannot fast-forward the shared tree past uncommitted work, and it does
> not try: it asks git for `--ff-only` and lets git's own refusal stand. A shared tree that will not
> advance is REPORTED, never forced.

`--check` reports `{"behind": 7}`. Three paths block the `--ff-only`, and all three are genuine
third content — a lane's live uncommitted work, not a stale twin:

| path | worktree | HEAD | origin |
|---|---|---|---|
| `site/data/evidence.json` | `492092f61` | `3210a88c7` | `f84a80f4d` |
| `tests/tools/test_stale_copy_refusal.py` | `d934ef790` | `26fbc5c60` | `f717973a7` |
| `tools/stale_copy_refusal.py` | `4328f8507` | `2b1874f6f` | `f333032a6` |

## Why this one is worth a finding and not a shrug

**The third row is the census itself.** The lane holding it wrote the `refresh_to_head` /
`landing_pair` wiring, landed it to origin through `surgical_land` — which *never writes the working
tree*, deliberately, and that is the property that makes it safe for a two-lane file — and then kept
working in the shared tree. So the shared tree holds a copy of `stale_copy_refusal.py` that
**imports modules the same tree has never received**, and will keep holding it until the
fast-forward that three other files are blocking.

That is `PUSHED IS NOT IMPORTED` with the failure landing on the class's own instrument. The chain:

1. a landing goes to origin from an isolated worktree, correctly;
2. the shared tree cannot fast-forward, because three unrelated lanes hold live bytes, correctly;
3. so a module that imports its new siblings is on disk and its siblings are not;
4. and the census that every seat is told to run as *the check* raises `ImportError`.

Nothing in that chain is a defect on its own. The composition is, and no single control can see it,
because each step is another lane's correct behaviour.

## What I did instead, which is the durable workaround and should be written down

Ran **origin's own code against the shared tree**, which the tool already supports and nobody had
used this way:

    git worktree add --detach /tmp/wt origin/main
    cd /tmp/wt && python3 -m tools.stale_copy_refusal --census --root /home/rich/synthetic-enterprise

`--root` names the repository holding the rival copies, and it is independent of which checkout
supplies the code. That returns the real table — five rival copies, graded — with no write to the
shared tree at all. **This is the move whenever a shared-tree instrument is behind origin: run the
newer code from a detached worktree, pointed at the older tree.** It needs no fast-forward, no
lock, and cannot touch another lane's bytes.

## What is next

1. **The fast-forward is already another lane's live item** — a seat is landing the four-file
   cluster (`tools/surgical_land.py`, `tools/stale_copy_refusal.py`,
   `tests/tools/test_stale_copy_refusal.py`, `site/data/evidence.json`) precisely so
   `origin_reconcile`'s advance leg can fire. Its landing was in flight while this was written. I
   did not touch those paths and this finding is not a second attempt at them.
2. **A census that cannot import its own siblings should say so, not raise.** The deferred import at
   `door_verdicts` line 475 is inside the function that grades the doors; a `try/except ImportError`
   that degrades to "paths listed, doors ungraded, and here is why" turns a crash that stops every
   lane into a partial answer plus a named reason. That is `fail closed, and say so on the surface`,
   and it is about six lines. Recorded rather than built: the file is one of the three blocking the
   fast-forward and is held dirty by another lane right now, so writing into it is the exact hazard
   the previous finding in this series exists to describe.
3. **The four absent files are invisible to every scan keyed to `git ls-files`.** Worth asking once
   whether anything else the seven commits added is being counted as "does not exist" rather than
   "has not arrived" — the orphan ratchet's census reads `git ls-files`, and an untracked module is
   invisible to it by construction.
