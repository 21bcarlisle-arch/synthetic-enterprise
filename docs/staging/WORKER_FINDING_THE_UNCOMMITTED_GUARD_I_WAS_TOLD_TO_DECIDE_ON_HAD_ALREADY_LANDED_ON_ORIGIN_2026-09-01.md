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

---

## The prediction, graded — 2026-09-01, by the tick that drew the Lane 0 item

**REFUTED, and not narrowly.** The prediction was *"more than a quarter"* of the 19
`uncommitted_and_orphaned_work` instances resolve to "already landed upstream" when re-derived
against `origin/main` instead of local `HEAD`. The threshold is 5 of 19. The answer is **0 of 19**.

Re-derivation, mechanical rather than eyeballed: for each of the 19 instance documents listed in
`docs/staging/reference/CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md`, extract every source
path it names, and ask of each whether it exists on `origin/main` and *not* at local `HEAD`.

| | |
|---|---|
| instances | **19** |
| instances naming at least one source path | 19 |
| instances with an artefact present upstream and absent at HEAD | **0** |
| instances naming a path whose upstream *content* differs from HEAD | 9 |

The 9 are not the prediction's claim and must not be read as a partial score. "The trunk has also
edited this file" is true of most files under active work in both directions; "the thing this
finding says is uncommitted is in fact committed upstream" is what was predicted, and it holds for
none of them.

**Why it was wrong, which is the part worth keeping.** The divergence begins at `178bf5a56`,
2026-08-31 14:49. All 19 instances are dated 2026-08-09 … 2026-08-29 — every one of them predates
the fork, so every artefact they name is on both sides of it. The prediction generalised from a
sample of one (`22aaaa494`, the `production_surface_guard` widening) to a population whose members
could not, by date, contain the artefact. That the one instance was vivid and self-inflicted is
exactly why it read as representative. **A finding that discovers a mechanism has not thereby
measured its extent, and the fact that its own case is the newest thing in the class was checkable
before the number was written down.**

## What the mechanism *does* account for, established the same pass

The prediction pointed at the wrong population, not at a wrong mechanism. The mechanism is live and
was costing something measurable on the day it was written down:

- **The four paged reds in `tests/background/test_autonomous_runner.py`** — RED across two
  consecutive operational-layer signals, carried as "known" — are this artefact exactly.
  `background/autonomous_runner.py` and its test in the working tree are **byte-identical to
  `origin/main`** (`git diff origin/main --` on both paths is empty); they landed upstream in
  `7a995e2b1`. Two of the four named tests —
  `test_a_verified_limit_carries_the_line_it_read` and `test_the_skip_is_logged_with_its_evidence` —
  **do not exist at local `HEAD` at all**, so the publish gate, which grades a checkout of HEAD,
  reports them as reds. In the working tree all five collect and pass. They are not real, they were
  never anyone's uncommitted work, and they cannot be cleared by any edit — only by the
  fast-forward.
- **21 of the 245 files** the tree-divergence measure was naming as squatting are byte-identical to
  `origin/main`, measured this pass with the leg below.

## The leg, and it is proven able to fail

`background/tree_divergence` is the surface that answers "how much uncommitted work is in this
tree" — the daily naming, the publish-path log line, `docs/observability/tree_divergence.json`. It
measured against `HEAD` and said nothing about what `HEAD` is. It now:

- reads `origin/main...HEAD` and **refuses the count** when the base cannot be resolved — the same
  fail-closed shape the module already applies to an unanswerable `git status`, for the same
  reason: a count that cannot tell "not committed yet" from "committed, and this base is stale" is
  an unavailable measure, not a clean bill;
- partitions the count, publishing `already_on_origin` — the files whose working-tree bytes are
  identical to the trunk's — and names the stale base in `breaches()` **whether or not** the file
  count breaches, because the reader who goes and re-decides a landed decision is reading a *small*
  number.

Compared by **hash, not by `git diff`**: `git diff origin/main -- <path>` ignores an untracked path
and returns "no difference", so the commonest shape of this artefact — added upstream, absent from
the stale HEAD — would be counted as already-landed with nothing having been compared.

The first version of this leg was REFUSED by the gate, and the refusal was right. It treated a
repo with no `origin/main` at all as unreadable, so it refused the count inside the publish gate's
own archive checkout — which has no remote — and `KeyError`'d an existing consumer. That is a
control whose scope is wider than its claim: there is no trunk there to be stale against. It now
separates three answers, and only the third is a refusal: the trunk read; **no** trunk in this repo
(reported as `no_remote_base`, never as `behind: 0`, which would read as up to date); and the trunk
present but unreadable, which is the refusal.

Mutation-proven, five mutants, each red on the test that names its defect and green elsewhere
(run in an isolated worktree so no other lane saw a manufactured red):

| mutant | red |
|---|---|
| unreadable base falls back to `{behind: 0}` | `test_a_base_that_exists_but_cannot_be_read_refuses_the_count` |
| a missing remote reported as `behind: 0` | `test_a_checkout_with_no_trunk_at_all_still_reports_its_count` |
| `paths_already_on_origin` always `[]` | the identical-to-trunk test, and the untracked test |
| stale-base sentence keyed to the count breach | `test_the_stale_base_is_named_even_when_the_count_is_under_the_threshold` |
| `git diff` instead of hashing | `test_an_untracked_path_that_is_tracked_upstream_is_compared_not_skipped` |

Live output on the shared tree this pass:

```
tree divergence: 245 source file(s) vs HEAD ... — HEAD is 20 behind / 16 ahead of origin/main,
                 21 of the 245 already on the trunk
  BREACH: HEAD is 20 commit(s) behind origin/main (and 16 ahead), so this count is measured
          against a stale base: 21 of the 245 are byte-identical to the trunk and are not
          uncommitted work
```

## The orphan-ratchet decision was already taken, and the direction's premise for it is false

The Lane 0 item said the publish is wedged by the orphan-ratchet refusing
`tools.promote_worktree_landing`, and asked for a decision between wiring and freezing. Neither is
owed:

- **It is already frozen, on both sides.** `tools.promote_worktree_landing` is in
  `docs/design/orphan_baseline.json` at local `HEAD` (`0bc78cf14`) *and* at `origin/main`. The
  ratchet run this pass reports `new_orphans: []`, `orphans now: 379 | baseline: 380`, **rc=0**. It
  is not refusing anything and is not what is wedging the publish. (It does report one baseline
  orphan now wired — `tools.wait_for` — i.e. the floor can be lowered, which is the opposite
  problem.)
- **The stated justification for wiring it is not true.** The direction says
  `background/seat-executor.service` "invokes it as a subprocess the ratchet's import graph cannot
  follow". The unit's only `Exec` line is `ExecStart=/usr/bin/python3 -m background.seat_executor
  --once`. Every reference to `promote_worktree_landing` in `seat_executor.py` is prose: a module
  docstring, a comment, and step 2 of the `CHARTER` **prompt string** handed to an agent. No
  committed code runs it. The ratchet's import graph is not failing to follow a subprocess edge —
  there is no subprocess edge.

So the honest reading is a third thing the ratchet's grammar cannot say: the module is neither
wired nor dormant, it is **run by an agent under written instruction**. Freezing it records
"deliberately dormant", which is false; wiring the charter string as an edge would make every
module merely *named* in a prompt read as called, which is the false-caller defect already filed.
The freeze stands because it is what is committed and re-deciding it changes nothing that runs;
the mislabel is recorded here rather than corrected, because the correction worth making is to the
ratchet's vocabulary and that is not this item.

## The reconciliation has no sanctioned route, and that is the finding

I did not make the histories one, and it is not a matter of care or time. Measured this pass:
`origin/main...HEAD` = **20 behind / 16 ahead**, merge base `178bf5a56` (2026-08-31 14:49).

- `tools/promote_worktree_landing._refuse_if_not_fast_forward` promotes **only** a fast-forward,
  correctly and by design — "never `--force`, ever".
- `tools/surgical_land`'s receipt names the **parent sha and the result tree**, and `--verify`
  falsifies on either. So a rebase of the 16 local commits onto the trunk falsifies all 15 of their
  receipts, and `_refuse_if_ungated` — which checks *every* commit a push would add — then refuses
  the lot.

Fast-forward is impossible while local is ahead; rebase destroys the receipts that make promotion
legal. **The moment the shared tree makes one local commit while an unattended writer pushes to
`origin`, the two histories can never be reunited by any route this project sanctions.** That is
why the fork only ever grows, and it is not a tidy-up defect — it is a hole in the route that was
landed the same day the executor was armed.

The one shape that survives both constraints is a **merge commit**: it leaves every existing
commit's parent and tree untouched, so all 15 receipts still verify. It is refused today only
because the merge commit itself carries no receipt. The repair is therefore in
`_refuse_if_ungated` — an integration commit whose own tree is the gated result — and it is a
change to the promotion route, which wants its own turn rather than being improvised at the end of
this one. **Filed, named, not attempted.**
