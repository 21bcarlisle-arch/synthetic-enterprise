**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `A45_the_canon_is_a_standing_subject`

# `surgical_land` cannot commit from a git worktree — so isolation and the only legal door are mutually exclusive

**Found:** 2026-08-31, testing the load-bearing assumption of an architecture before building on
it. The assumption was false, and finding that out cost one command instead of a day.

## The repro, in full

```
$ git worktree add --detach /tmp/.../seat-wt HEAD
$ cd /tmp/.../seat-wt && python3 -m tools.surgical_land -m "probe" <path>
[surgical-land] REFUSED: git read-tree <sha> failed rc=128:
error: unable to normalize alternate object path: /tmp/.../seat-wt/.git/objects
fatal: failed to unpack tree object <sha>
```

**Cause.** A linked worktree's `.git` is a *file* containing `gitdir: <path>`, not a directory.
`surgical_land` builds the tree the commit *would* create — which is the whole reason it is the
sanctioned door — using a temporary index against a repo layout it assumes is normal, so
`read-tree` resolves `$PWD/.git/objects` as an alternate object store, finds a file where a
directory should be, and refuses.

**It refuses rather than mis-committing, which is the right failure.** Nothing is corrupted and no
partial commit is made. This is a capability gap, not a data hazard.

## Why this is worth a finding rather than a shrug

**It makes two of this project's own rules mutually exclusive**, and neither is optional:

* *"HOOK-BYPASS IS A WALL. `--no-verify` and hand-built `commit-tree`/`merge-tree` merges are
  never a judgement call, and no sanctioned bypass shape exists. The legal move is
  `python3 -m tools.surgical_land`."* (CLAUDE.md)
* *"Other lanes have work staged in this tree; the pathspec, not the tree lock, is what stops you
  sweeping it."* — the shared working tree is a known collision surface, and `git worktree` is the
  standard remedy. This repository already carries twelve `worktree-agent-*` branches and a
  `salvage/*` tag convention for exactly that pattern.

So **any writer that isolates itself into a worktree has no legal way to commit.** It must either
come back onto the shared tree or cross a wall. Today that is invisible because every writer works
on the shared tree — and pays for it there instead.

## What it cost today, measured

All six of this session's collisions were **working-tree** collisions, not commit collisions.
`surgical_land` handled the commit layer perfectly across **twelve landings**: one lost a race to
another lane mid-gate, re-gated against the new base automatically, and landed; every receipt
verified; nothing swept.

| what happened | where |
|---|---|
| C1b's uncommitted work across 5 files blocked a sim change from landing, all day | shared tree |
| a 430-line extension appeared mid-turn and reddened a landed control tree-wide | shared tree |
| the ruff baseline moved twice mid-measurement | shared tree |
| `git stash` nearly popped another lane's parked work | shared tree |
| `cd` drift wrote edits into the wrong repo copy, twice | shared tree |
| a duplicate finding was filed because neither writer could see the other's claim | (needs a claim, not a worktree) |
| **commit-layer collisions** | **none** |

**The evidence points one way: the commit door is solved and the working tree is not.** Worktree
isolation is the obvious remedy and it is the one thing that cannot currently be combined with the
only legal door.

## What this blocked, concretely

The director asked (2026-08-31) whether the delivery seat can self-advance safely, given that
`surgical_land`, tree locks, pathspec commits and LANE 0 now exist. **The answer would have been
yes** — seat in its own worktree, landing through the sanctioned door, every control preserved and
the collision surface removed. It is no, and this is the entire reason. The work moved into the
ticks instead (`background/seat_continuation.py`), which needs no second writer at all.

## What would fix it

`surgical_land` needs to resolve the real gitdir rather than assume `$PWD/.git` is a directory —
`git rev-parse --git-dir` / `--git-common-dir` give both, and the temporary index and `read-tree`
should be run against the common dir with `GIT_DIR` set explicitly.

**Not attempted here, deliberately.** `surgical_land` is the door every lane commits through and
three sessions were landing through it while this was found. A change to it wants its own turn, its
own mutation proof against a real worktree, and a tree that is not being written by two other
writers at the time. Filed with the repro so that turn starts from a working reproduction rather
than from a rediscovery.

## Severity

**LATENT.** Nothing published is wrong and nothing is at risk. No writer uses a worktree to commit
today, precisely because it does not work — so the gap is currently costing capability rather than
correctness. It becomes BLOCKING the moment anything is designed on the assumption that isolation
is available, which is exactly what nearly happened here.
