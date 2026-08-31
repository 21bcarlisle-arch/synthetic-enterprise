**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `OPS1_process_manifest_reconstruction`

# The uncommitted guard I was told to decide on had already landed on origin, and local `main` is 20 commits behind

**Found:** 2026-09-01, working the LANE 0 delivery item *what-runs-this-machine-must-be-in-a-commit*.
Not by a control — by checking the premise before acting on it.

## What I was told, and what was true

The drawn direction said, of `tests/production_surface_guard.py`:

> carries an **uncommitted** widening of `docs/observability` from nine hand-listed files to a whole
> protected surface … **Either land it with the reds repaired, or take it out of the tree as a patch
> file** — never with `git checkout`, and never by leaving it where it is, because a change that reds
> ~1,760 tests and belongs to no commit wedges every lane that touches any of those files.

Both options were wrong, because the premise was. The widening **belongs to a commit**:

```
22aaaa494  docs/observability becomes a protected surface, and six production writers
           were stamping the record from inside test runs
```

`git merge-base --is-ancestor 22aaaa494 origin/main` → **yes**. It is on `origin/main` and has been.

## Why it looked uncommitted

Local `main` does not have it. At the time of writing:

| | |
|---|---|
| commits on local `HEAD` not on `origin/main` | **11** |
| commits on `origin/main` not on local `HEAD` | **20** |

`git diff` compares against the local HEAD, and the local HEAD is 20 commits behind the branch that
carries the change. So a landed, pushed, reviewed change renders in `git status` as one lane's
uncommitted draft. **Every reader of `git status` on this machine is reading it against a stale
base, and nothing on the surface says so.**

## The two copies are the same code and different prose

The working-tree copy is an *earlier draft* of what landed — the landed one is tighter ("Until this
landed…" where the draft says "Until today…"). Parsed rather than eyeballed, the part that acts is
byte-identical:

```
origin/main            PROTECTED_SURFACES = ('docs/staging', 'docs/observability', 'docs/status')
                       PROTECTED_FILES    = ('site/data/publish_provenance.json',)
working tree           PROTECTED_SURFACES = ('docs/staging', 'docs/observability', 'docs/status')
                       PROTECTED_FILES    = ('site/data/publish_provenance.json',)
```

So there was never a decision to take. There is no argument to weigh and no patch worth parking:
the change is in, upstream, with better wording than the copy I was asked to rule on.

## The reds are real, and they are the *absence* of the rest of that branch

The direction named a specific casualty — `tests/sim/test_cache_store.py::test_log_cache_access_does_not_raise`,
"green at HEAD and red in the tree". Checked it in a worktree at `origin/main`, which has the
widening:

```
$ git reset --hard origin/main && pytest tests/sim/test_cache_store.py
13 passed in 0.03s
```

**Green, with the widening active.** The ~1,760 local reds are not the cost of the widening. They
are the cost of holding the widening *without the twenty commits of repair that landed beside it*.
The repair the direction priced at "the cost is the repair, not the argument" has already been paid
by another lane; this machine just cannot see it.

## What this is an instance of

The class tonight's Lane 0 item is about is **the record and the code disagreeing about what exists**
— an executor that ran but was in no commit, a published capture from code in no commit, a manifest
citing `delivery_lane.draw(claim=False)` before that code landed. This is the same disagreement with
the sign flipped: work that IS committed, and pushed, presenting locally as work that is not.

It is the more dangerous direction. An uncommitted-looking change invites someone to "finish" it —
to re-derive, re-argue, and re-land a decision already taken. I was one step from writing a parked
patch file and a decision record for a change that needed neither, which would have put a
superseded draft into the repository as though it were a live question.

## What I did

Nothing to the guard. There is no land-or-park action, because there is no undecided change. The
working-tree draft is redundant with `22aaaa494` and I left it in place rather than reverting it:
reverting would make the local tree differ from `origin/main` in the opposite direction, and the
real repair is reconciliation, not another edit.

## What is owed, and it is not mine to do in a bounded tick

**Local `main` and `origin/main` have diverged 11/20 and need reconciling.** That is a genuine piece
of work with a real failure mode — a careless `git merge` on a shared tree with several lanes' dirt
in it is precisely what `tools.surgical_land` exists to prevent — and it is too big to do safely
inside a tick that is already holding three landings. Filed rather than attempted.

**The cheap half is worth doing first:** nothing anywhere tells a reader that `git status` on this
machine is answering against a base 20 commits stale. Every orientation, every doorbell and every
"uncommitted work" alarm in `background/` is computed against that base. The
`uncommitted_and_orphaned_work` finding class currently stands at 19 instances; an unknown number
of them may be this same artefact rather than real orphans, and no one can tell which without
checking each against `origin/main`.

## Prediction, recorded before anyone checks

If someone re-derives the `uncommitted_and_orphaned_work` instances against `origin/main` rather
than against local `HEAD`, **I expect a material fraction — I will say more than a quarter — to
resolve to "already landed upstream", and I expect the whole 19 to be reported again unchanged on
the next tick if they are not.** I have not checked, and I am writing the number down first so the
result can refute it.
