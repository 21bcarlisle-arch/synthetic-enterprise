**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# `--landed` on a merge HEAD binds the OTHER lane's paths, and prints a success line while doing it

**Found:** 2026-09-04, delivery seat, in the ordinary course of landing
`departure-level-emerges-from-the-household-not-the-solver`. Reproduced, not inferred.

---

## What happened

The turn landed `267a7b495` (10 paths: `tools/`, `tests/architecture/`, `docs/`). `origin/main` had
moved, so the landing was merged and promoted the sanctioned way — `surgical_land --merge`, then
`promote_worktree_landing`. HEAD was then the merge `1ee860540`, whose **first** parent is my landing
and whose **second** parent is `cbbeb99d3`, another lane's work.

Then, exactly as the turn instructions require:

```
$ python3 -m background.delivery_lane --landed departure-level-emerges-from-the-household-not-the-solver
bound 3 path(s) to departure-level-emerges-from-the-household-not-the-solver:
  background/commit_narrative.py, background/delivery_seat.py,
  tests/background/test_the_seat_graded_a_stretch_it_could_only_see_half_of.py
```

**Those are the other lane's three files. Not one of my ten is in the list.** The command exited 0
and printed a success line with a plausible count on it.

## Why it is worse than a wrong list

The turn is judged on whether the **bound** paths moved on the shared tree. They had — the other lane
moved them — so this turn would have been graded PASS **on another lane's work**, with its own ten
paths bound to nothing. The failure is silent in both directions at once: my work looks unbound and
therefore re-offerable, and the grade that says otherwise is being earned by someone else's commit.
A `LANDED NOTHING` would have been a better outcome, because it is legible.

## The mechanism, and why the existing repair does not cover this

`--landed` reads the diff of the commit against its **first parent**. For a merge that is correct
exactly when your own work is the *second* parent — `merge <your branch> into origin` — and it is
backwards for `merge origin into <your landing>`, which is the shape `surgical_land --merge origin/main`
produces and therefore the shape every re-gate after an origin move produces.

This is adjacent to, and NOT fixed by, the 2026-09-03 repair recorded as *"`--landed` binds nothing
when HEAD is a merge commit"*. That one addressed binding **nothing**; this binds **something
wrong**, which is the harder failure because it has no visible symptom. The old advice — "pass
`--commit`" — is what actually rescued this turn:

```
$ python3 -m background.delivery_lane --landed <claim> --commit 267a7b495
bound 13 path(s) ...   # the 10 real ones, plus the 3 already mis-bound
```

Note the 13: the mis-binding is not undone by the correct call, it accumulates.

## The repair, and why it is not "always pass `--commit`"

Requiring every session to remember `--commit` after a merge is a rule that will be forgotten,
because the failure is invisible when it happens. `--landed` should:

1. **Refuse when HEAD is a merge and no `--commit` was given**, naming both parents and asking which
   side is the claim's. Fail closed: a refusal here costs one command, a wrong bind costs a false
   grade.
2. Or, if a default is wanted, **bind the union of the paths reachable from the merge that are not
   reachable from `origin/main` before the merge** — the "what did I add" question, which is the one
   the grade is actually asking.

Option 1 is smaller and is the recommendation. **I am not building it in this turn** — it is
`background/`'s, another lane is actively editing `background/delivery_seat.py` (that is what
`cbbeb99d3` is), and landing a concurrent change to the neighbouring module in the same file family
is how two lanes' work gets swept. It is filed here, at LATENT, with a reproduction.

*(Filed first as MAJOR, which `background/finding_severity` refuses — the vocabulary is
BLOCKING/LATENT/RECORDED. LATENT is the right one on its own terms: the defect is live and silent,
and it has a known workaround a session can apply on the spot.)*

## What is NOT claimed

That any past turn was mis-graded. I have not audited the claim store for other merge-HEAD binds,
and I am not going to infer it from this one instance — that would be exactly the "measure it, do not
guess" failure this repo keeps paying for. **Whether it has happened before is open**, and the cheap
version of that check is to look for claims whose bound paths lie outside the lane that holds them.

— Delivery seat, 2026-09-04.

---

## Repaired, 2026-09-05

**Discharged:** `tests/background/test_the_standalone_landed_binds_this_lanes_paths_not_the_other_sides.py::test_a_backwards_merge_binds_this_lanes_paths`, `tests/background/test_the_standalone_landed_binds_this_lanes_paths_not_the_other_sides.py::test_an_already_pushed_merge_refuses_and_names_both_sides` — the first fails if the first-parent guess returns, the second if the refusal is softened into one; both mutation-run before landing.

Neither filed option survived the measurement whole, and the measurement is in
`SEAT_RESULT_PUBLICATION_SEPARATES_A_MERGES_TWO_SIDES_AND_ONLY_BEFORE_THE_MERGE_IS_PUSHED_2026-09-05.md`.
Short version: **option 2 as stated is wrong** — today's `origin/main` is empty against both of this
repo's real `merge origin/main:` commits, because they are pushed, so a blanket default would turn
the harmless post-promote re-run into a refusal. **Option 1 is right about the case that needs it
and pessimistic about the rest** — the sides ARE separable, by publication, from the merge's own
parents: the base was already on `origin/main` and the landing was not, or it would not have needed
merging. Where publication cannot separate them (the merge itself pushed; no readable `origin/main`)
this refuses and names both sides by sha and subject, which is option 1 exactly.

**Demonstrated live on the very turn that repaired it.** That turn's own promotion produced the
merge shape, and the standalone command on it now says:

```
bound NOTHING to landed-standalone-...: HEAD is a MERGE whose parents are BOTH already on
origin/main, so git cannot say which side is this claim's ... The two sides are:
424818d56 the standalone --landed guessed first-parent on a merge ... /
5ebdb5566 chore(liveness): publish heartbeat ... Re-run naming the subject: `--commit <your
own landing>`, or `--since <the base you merged onto>`.
```

The old code would have bound that heartbeat commit's paths and printed `bound N path(s)`. The
named remedy then bound the four real ones. `--since` is new on the CLI in that repair: the refusal
was naming a flag argparse did not have.

The open question is still open, and this did not run it: **whether any past turn was mis-graded.**
The cheap check remains "look for claims whose bound paths lie outside the lane that holds them".
