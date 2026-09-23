**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

> **CLOSED 2026-09-23 — §5's three open items are all discharged, which is what this was BLOCKING
> on.** §5.1: the ghosts are out of the shared index — **134 of them, not 107**, and the 107 was
> exact when written; the other 27 were minted by `6bd209c0b`, this document's own landing, because
> an archival that removes a root copy at HEAD converts every root copy still staged into an `AD`
> ghost. §5.2: **3 deletions survive nowhere, not 10** — the other 7 are on disk at their own paths,
> byte-identical to HEAD, and "survives nowhere" turned out to name three absences that come apart.
> The 3 are restored, and `RECORDS_DIRNAME` had already ruled on them, so no exception was recorded.
> §5.3 was spent before the draw by the reconcile merge `fd5301b3f`.
>
> Severity dropped here rather than in the successor, so this document and the lane's books cannot
> disagree. Measurements, the per-file content-direction check that licensed the reset, and one new
> BLOCKING defect found on the way (the `records/` floor was keyed to the literal `38` against a room
> of 377, and printed `0 violation(s)` while three documents were missing — fixed in `57229702e`):
> `SEAT_RESULT_THE_GHOST_COUNT_IS_MINTED_BY_THE_LANDING_THAT_FIXES_IT_AND_SURVIVES_NOWHERE_WAS_THREE_ABSENCES_2026-09-23.md`.

*Lane, stated because the choice is load-bearing and the alternative was available. This document
classifies into `uncommitted_and_orphaned_work`, whose register is `H_harness`. It is filed
`A_strategy_governance` instead, so it appears under that register's* `Refused consolidation — out
of lane, still live` *rather than being folded in. The reason is the subject, not the routing: the
gate here was RIGHT —* `staging_rooms --check` *printed the correct count of 27 on every commit.
What was wrong was the drawn item's claim about the tree, which is how work is directed rather than
how it is tested. The effect is also that §5's three open items keep a live reader, and that is
stated rather than left to be noticed, because a consolidated instance carries no queue presence of
its own.*

The Lane 0 item `nineteen-staging-dispositions-are-done-and-uncommitted` asked for one thing:
*"Commit the staged staging-root deletions and archival moves already sitting in the index by
pathspec `docs/staging/`."* Both halves of that sentence are wrong about the bytes, and carrying
it out literally would have un-archived 107 findings and destroyed 10 documents that survive
nowhere else. 27 genuine archival moves were landed instead. This is BLOCKING on the 107 — the
shared index still carries them and the next lane to run `git add docs/staging/` or commit that
index inherits the same trap.

## 1. What the item claimed, and what was there

| | item's claim | measured on the shared tree, 2026-09-23 |
|---|---|---|
| count | 19 | 116 staged entries under `docs/staging/` |
| kind | "deletions and archival moves" | **107 `AD`** + 9 `D ` staged; 31 ` D` and 66 `??` unstaged |
| net effect of committing the index | census −19 | **107 findings un-archived**, 6 documents destroyed |

The "19" matches nothing in the tree. It is not the staged count (116), the deletion count (40),
the move count (27), or the discard count (10).

**And the repo's own instrument already said 27.** `background/staging_rooms.py --check` prints
`STRANDED ARCHIVAL: 27 document(s) are archived into a sub-room ON DISK and still sit in the root
at HEAD`, and names the same 27 this landing moves — arrived at independently, by a different
route, from the same tree. The item's 19 was stale against a gate that runs on every commit. The
count was available for the asking and the item did not ask it.

## 2. The 107 — an index that would run the archive backwards

`git status` grades all 107 `AD`: **A**dded to the index, **D**eleted from the working tree. Every
one is a `SEAT_*`/`WORKER_*` document dated 2026-09-16..19, and for every one:

* it is **not** on disk at the staging root (`on_disk=0, missing=107`);
* its twin **is** on disk at `docs/staging/done/` (`done_twin_on_disk=107`);
* HEAD already has it at `docs/staging/done/` and **only** there (`also_at_root_in_HEAD=0`).

So the archival move for all 107 **already landed**. The index entries are residue: a tool staged
the root copies, the move then removed them from the working tree, and nothing has re-read the
index since. They are not a disposition awaiting a commit — they are the ghost of a disposition
that completed.

**Committing that index adds 107 root copies back beside their `done/` originals.** The queue would
gain 107 items overnight, every one of them already dispositioned, and the census the item was
raised to repair would be wrong by 107 in the opposite direction. The item's stated door —
pathspec `docs/staging/` — is what fires it.

The saving grace is narrow and worth naming, because it is why this has not already happened: a
*pathspec* commit refreshes the index from the working tree, so `git commit -- docs/staging/`
resolves the `AD` entries to absent and drops them. A bare `git commit` after any `git add`, or any
door that commits the index as it stands, does not. **The hazard is live and it is one command
away.**

## 3. The 10 that survive nowhere, and why they were NOT landed

Of the 40 deletions under `docs/staging/`, ten have no surviving copy anywhere in `docs/` — not in
`done/`, not in any other room:

```
SEAT_FINDING_ARCHIVING_A_FINDING_FALSIFIES_A_COMMONS_ARTEFACTS_POINTER_...2026-09-22.md
SEAT_FINDING_THE_SITE_LANE_REFUSED_ON_TWO_DOORS_PINNED_TO_THE_SHAPE_...2026-09-22.md
SEAT_RESULT_THE_CEILING_IS_THE_PROBABILITY_THE_DICE_USED_...2026-09-23.md
SEAT_RESULT_THE_PAGE_STOPPED_COPYING_THE_SEED_PRICE_...2026-09-22.md
SEAT_RESULT_THE_SEED_PRICE_CAN_ONLY_BE_ASKED_IN_THE_STATE_WHERE_IT_HAS_NO_ANSWER_2026-09-22.md
SEAT_RESULT_THE_STALE_KNOWLEDGE_MAP_IS_DISCARDED_...2026-09-23.md
records/PREREG_WHAT_SHAPE_IS_THE_SEED_PRICES_INTERVAL_ON_A_MEAN_OF_UNDETERMINED_SIGN_2026-09-22.md
records/PREREG_WHAT_THE_REPUBLISHED_SEED_PRICE_LOOKS_LIKE_WHEN_IT_IS_DERIVED_INSTEAD_2026-09-22.md
records/SEAT_RESULT_THE_FLAT_CHURN_BELIEF_NOW_REACHES_A_READER_...2026-09-22.md
records/WORKER_PREREG_W1_14_HOW_MUCH_OF_THE_HOUSEHOLD_POPULATION_THE_CELL_STORE_ALREADY_SERVES_2026-09-20.md
```

Six of the ten are **already staged** (`D `), so they are inside the item's pathspec and a pathspec
commit lands them. They were not landed, because `background/staging_rooms.py` states the protocol
in its own docstring:

> *"WHY A ROOM AND NOT A DELETION... Every file this module relocates stays inside `docs/staging/`
> and stays committed. That is not timidity: this project has twice found a control go QUIET rather
> than loud when the structure..."*

**An outright deletion is not a disposition this repo recognises.** Three of the ten are
pre-registrations — the artefact class whose whole value is that it cannot be revised after the
answer is known. Landing their deletion on the strength of a bare index read destroys the only
evidence that those experiments were designed before their results. The working-tree deletions
stand; HEAD still holds every one of the ten, and this document is the record of why they were
left there rather than a decision to discard them.

## 4. What WAS landed — 27 archival moves

Root/`records/` → `done/`, destination untracked on the shared tree, content preserved:

* **24** byte-identical to HEAD (pure moves, reproduced from HEAD bytes in an isolated worktree —
  no other lane's bytes were read);
* **3** where the archive copy differs, each difference a genuine disposition annotation.

The three needed their direction established one at a time, and **one of them ran backwards**:

| document | shared tree's `done/` copy | direction taken |
|---|---|---|
| `SEAT_RESULT_THE_CEILING_COST_CURVE_IS_CONVEX_...` | 209L, `BLOCKING`, **no addendum** | HEAD's root copy (364L) — it carries the `DISCHARGED`/`RECORDED` header and a 142-line addendum the archive copy predates |
| `WORKER_RESULT_THE_TWO_CEILINGS_SHARE_A_RULER_...` | 228L, additions only | `done/` copy — adds a `CORRECTION` block |
| `run_complete_20260922T064617Z.md` | 21L, additions only | `done/` copy — adds the `Superseded (not published)` stamp |

**The first one is the finding inside the finding.** Its archive copy is a *stale snapshot* taken
before the document was discharged. An archival move implemented as "take the `done/` bytes" —
which is what "commit the moves already in the index" means — would have silently reverted a
severity discharge and deleted a 142-line self-correction, and the diff would have read as a
routine file move. **A move is only content-neutral once you have checked that it is; the direction
has to be established per file, and here it was not the same for all three.**

## 5. What this leaves open

1. **The 107 ghosts are still in the shared index.** They need dropping (`git reset -- <paths>`),
   which is a shared-tree index operation and cannot be done from an isolated worktree. Until then
   any door that commits the index rather than a pathspec un-archives them.
2. **The 10 deletions are undecided**, not resolved. Either they are archived to `done/` like
   everything else, or someone states in the record why these ten are the exception. The three
   pre-registrations should not be the case that establishes the exception.
3. **The census still will not balance**, and this document is why: the number it is short by was
   never 19, and 10 of the 40 outstanding deletions should not be landed at all. Any repair keyed
   to "filed minus dispositioned" needs to decide first whether a deleted-and-unarchived document
   counts as dispositioned. It currently counts as neither.

## 6. The class

**An item's count is a claim about the tree, and a claim about the tree is an un-re-asked
prediction.** This one named a number (19), a kind ("deletions and archival moves") and a door
("pathspec `docs/staging/`"), and the bytes refuted all three — the count by 6x, the kind by
inversion (107 of the 116 staged entries run the archive *backwards*), and the door by consequence.
None of that cost anything to check: four `git status` reads and a basename join, before any of it
was believed.

---

# ADDENDUM — the door I said was hypothetical has a name, and the flag that arms it has been on since July

Everything above was written before the 27 landed. §2 ended on a hedge — *"a bare `git commit`
after any `git add`, or any door that commits the index as it stands, does not [drop the ghosts].
The hazard is live and it is one command away"* — and named no such door. **I then went and asked
whether one exists. It does, and "one command away" understates it: it is a daemon step on an armed
path, and the flag has been present since 2026-07-18.**

## The door

`background/executor_governor.py::_default_fold()`, the F1 atom_status fold, lines 304–313:

```python
subprocess.run(
    ["git", "add", "--", "docs/design/maturity_map.yaml", "docs/design/atom_status"],
    check=True, capture_output=True,
)
subprocess.run(
    ["git", "commit", "-m", f"Fold atom_status inbox -> map (F1): {', '.join(folded)}"],
    check=True, capture_output=True,
)
```

**The `add` is scoped and the `commit` is not.** A pathspec on the `add` scopes what that one
command stages; it does nothing about what is *already* staged. `git commit` with no pathspec
commits the index as it stands — so this commits the two map paths it meant to, **and all 107 `AD`
ghosts with them**, under a message that reads `Fold atom_status inbox -> map (F1): <atom ids>`.

That message is the whole of the harm. A reader of the log, or of the commit's own subject, has no
route to the fact that it re-added 107 dispositioned findings to the staging root. The queue would
grow by 107 overnight and the commit that did it would be filed under the maturity map.

## It is not gated behind anything that is currently off

I expected to close this as reachable-but-dark, because `tools/executor_cli.py` says so in its own
docstring: *"`--daemon` ... DARK by default — it dispatches nothing unless the director's
console-only enable flag (`docs/observability/.build_executor_enabled`) is present."* **The flag is
present.** `-rw-rw-r-- 183 Jul 18 09:37 docs/observability/.build_executor_enabled` — two months.

And the ordering inside `run_loop` puts nothing else in the way: `kill_switch()` is checked at line
418, `fold_fn()` fires at 439, and the fold's own docstring places it *"TOP of each cycle, BEFORE
the F2 reconcile check"*. With the flag on, the only remaining condition is that a foldable
atom_status inbox exists — which is the routine case the fold was built for, not an edge.

The honest bound on this: I have not caught the loop in the act, and no `executor_governor` process
was running when I looked. What is established is that the code path is live, the flag that arms it
is on, and nothing between the two would stop it. **That is enough. A hazard whose every
precondition is satisfied does not need to have fired yet to be worth closing.**

## The class, which is the reason this is an addendum and not a separate finding

CLAUDE.md states the rule as **"Commit by pathspec, never `-A`."** This is that defect wearing a
shape the rule's wording does not cover: there is no `-A` here, and the author plainly knew the rule
— **the scoping is right there, it is just attached to the wrong command.** A scoped `git add`
followed by an unscoped `git commit` is not a scoped commit, and it reads like one at a glance.
The remedy is one token: `"commit", "-m", msg, "--", "docs/design/maturity_map.yaml",
"docs/design/atom_status"`, which is exactly what `background/process_run_complete.py:8057` already
does (`["git", "commit", "-m", msg, "--"] + list(paths)`). The two doors sit in the same tree and
disagree.

**Correcting §2 rather than revising it:** "one command away" is what I wrote before asking, and it
is wrong in the direction that flatters the tree. The question cost one `grep` and one `ls`, and I
had already published the hedge by the time I ran either. A finding whose own subject is *an
un-re-asked prediction about the tree* had one of those in it.

## What this adds to §5

4. **`background/executor_governor.py::_default_fold()` commits the whole index.** Fix is the
   pathspec, and it is owed independently of the 107 — the next lane to leave anything staged
   inherits the same door. Not landed here because it is a `background/` code change with its own
   gate selection, and this document's landing is the staging tree.

> **Owed item 4 is DISCHARGED in `9c0cd2934`, later the same turn, and the sentence above is left
> standing rather than edited: it was true when written and the turn did not end where it said it
> would.** `_default_fold()` now carries `"--", *_FOLD_PATHS` on the commit as well as the add.
>
> **Controlled by** `test_the_f1_fold_commits_only_its_own_paths_and_never_the_rest_of_the_index`,
> which is behavioural rather than a source grep — it stages a bystander file, runs the real fold,
> and asserts the fold committed its OWN paths before asserting the bystander is absent and still
> staged. Mutation run and reverted: dropping the pathspec reds it with `another_lanes_file` listed
> among the fold's own committed paths.
>
> **And writing that control found a second defect, which is the more general one.** The autouse
> `_isolate` fixture rebinds `executor_governor._default_fold` to `lambda: []`, so a test calling it
> through the module attribute gets the STUB — and the stub returns `[]`, which is exactly what the
> fold's error path returns. `test_default_fold_swallows_errors_and_returns_empty` was asserting
> `[] == []` against the stub and **stayed green with the real function mutated to raise
> unconditionally.** Established as a MISSING TEST rather than an equivalence: the real error path
> had no coverage at all. Both fold tests now go through `_ORIG_DEFAULT_FOLD`, captured at module
> level before the fixture — the idiom this file already used for `_ORIG_DEFAULT_RECONCILE`, one
> name above the defect, for exactly this reason.
>
> *The shape, because it is the reusable part: **a control whose subject an autouse fixture stubs
> proves the stub**, and it is worst when the stub's return value coincides with the real function's
> expected one. Nothing about that test looked wrong. It took mutating the real function to see it,
> and I only mutated it because I needed the same function for a different control.*
>
> **Still open after this: §5 items 1–3.** The 107 ghosts remain in the shared index — the repair
> above removes the daemon route by which they could have landed, and does **not** remove them.
