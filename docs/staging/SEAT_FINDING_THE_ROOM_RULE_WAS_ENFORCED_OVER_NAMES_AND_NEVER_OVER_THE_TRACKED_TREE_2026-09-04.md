**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# The room rule was enforced over names and never over the tracked tree

Filed 2026-09-04 by the delivery seat, working the priority-zero publish-gate wedge.

## What the wedge actually was

The doorbell named `behind_origin` and prescribed `surgical_land --merge origin/main`. That cause
was already discharged: `HEAD == origin/main`, 0 ahead and 0 behind, reconciled by `b0ba91858`.
Acting on the doorbell's prescription would have been a no-op against a repaired state.

The live cause at HEAD was failure #12, `non_test_gate_refusal`, and the publisher had already
named it in its own log: *"The gate that refused is the finding-class consolidation: running the
test suite will not clear it."* Reproduced directly:

```
finding_classes --check
TWO ROOMS SEAT_PREREG_FOUR_SMALL_REPAIRS_MEASURED_NOT_SMUGGLED_2026-09-04.md:
  present in records AND root
check: FAIL (1 failures)
```

**No test was ever red.** Running the gate's pytest argv would have cost ~10 minutes and come back
green, which is how this episode repeats.

## The loop, and why it had already been "fixed" twice

`staging_rooms.room_for(KIND_PREREGISTRATION)` says a preregistration lives in `records/`. A
disposition moves it there. The root path is still **tracked**, so the next operation that
restores a tracked-but-deleted path brings it straight back, and `room_collisions` then refuses
every commit in the tree until someone sweeps the duplicate by hand.

`4a4ac598b` (13:32) diagnosed this exactly — from the mtime column, since the `records/` copy kept
arriving carrying the root copy's *previous* mtime, and a rewrite carries a fresh clock where a
move preserves it. Its own commit message says *"The fix is not another repair: it is to stop the
root path being tracked."* It then untracked **the one path it had in front of it**.

Fifty-six minutes later `197261a2d` (14:28) committed a **new** preregistration into the same
tracked root, and the identical wedge came back. Two more (`..._WAS_THE_NAMED_BLOCKING_TEST_...`,
`..._WHICH_SITE_TOUCHING_COMMITS_...`) were sitting in the index staged to land the same way when
this was written — byte-identical to copies already tracked at HEAD in `records/`, with no
worktree file, so unstaging them lost nothing.

## The gap that let it recur

`tests/background/test_only_work_is_in_the_work_channel.py` already asserted
`room_for(kind_of(name)) == RECORDS_DIRNAME`. It asserted it **over names, in the abstract**.
Nothing anywhere applied that rule to what git actually **tracks** — so the rule was right,
published, tested, and unenforced against the only state that can cause the loop.

That is the whole class: a property proven about a function and never asked of the tree.

## The repair

`finding_classes.self_refuelling_root_documents(names)` returns the names tracked in the staging
root whose kind sends them to a room `room_collisions` treats as mutually exclusive with it, and
`test_no_document_is_TRACKED_in_the_staging_root_that_a_disposition_will_move_out` runs it over
`git ls-files`.

**The subject is the index, deliberately.** `surgical_land` gates a standalone extract whose HEAD
is the *parent* sha but whose index is the tree the commit would create. A control reading
`git ls-tree HEAD` would grade every commit against its predecessor and go green one commit late —
letting through the very commit that reintroduces the defect.

**Scoped to `ROOM_DIRNAMES`, not to every room `room_for` can name.** A root-tracked document only
becomes publish-gate fuel when `room_collisions` can see the pair, and that walk covers
`ROOM_DIRNAMES` alone. Keying to that tuple rather than to today's list means a new room added to
it widens this control on the same commit.

## Mutation evidence

* Predicate returns `[]` → kills the reachability leg.
* Inject the defect into the index (`git update-index --add --cacheinfo`) → kills the real-tree
  leg, with the injected entry verified present before the run and cleaned after.

Both legs are asserted because the real-tree leg alone asserts an **empty list**, and an empty list
is what a predicate that flags nothing returns — it would pass against a defective tree forever.

**An honest note on the mutation run.** A first scripted attempt at the second mutation reported
SURVIVED. Re-run with the index state printed at each step it reported KILLED. I could not
attribute the discrepancy to a cause and am not guessing at one; the run with verified state at
each step is the evidence, and the earlier one is the one I distrust.

## The loop caught in the act, by the commit that closes it

The first landing attempt was refused (by the pre-existing red below). The refusal's own cleanup
**restored the tracked root path**, and the duplicate came straight back:

```
docs/staging/SEAT_PREREG_..._2026-09-04.md          5185 bytes  15:00:56   <- restored
docs/staging/records/SEAT_PREREG_..._2026-09-04.md  5185 bytes  14:34:52   <- the move, untouched
```

A fresh clock on the root copy and a preserved clock on the `records/` copy — the exact signature
`4a4ac598b` reasoned from, reproduced here by an ordinary refused commit. This is the mechanism,
not an inference about it: **any** operation that restores tracked-but-deleted paths refuels the
loop, and a refused landing is one of them. It is also why sweeping the working tree can never end
this and only untracking the root path can.

## The pre-existing red this had to clear first, and what it turned out to be

`test_a_PREREGISTRATION_is_not_work_whatever_channel_wrote_it[SOME_NEW_CHANNEL_...]` was red at
HEAD before this work (proved in a clean `git archive HEAD` extract) and is in
`HEAD_RED_REGISTER.md`. Editing this test file brought it into the gate's path-scoped selection,
so it had to be resolved to land.

It was not stale — it was correct and unfixed. `kind_of` tested the preregistration token in the
**first two underscore-segments only**, a 2026-09-03 narrowing made to stop
`SEAT_FINDING_A_PREREGISTRATION_...` routing into `records/`. That narrowing assumes every channel
names itself in one segment, so it is a positional tuple wearing an offset — the same failure as
the prefix tuple it replaced, and the one the test's own docstring says a new channel must not have
to remember. `SOME_NEW_CHANNEL_PREREGISTRATION_OF_SOMETHING` fell through to UNKNOWN and drew as
WORK.

What separates the two cases is **order, not depth**: a document is whichever kind its FIRST type
token names. `SEAT_FINDING_A_PREREGISTRATION_...` carries FINDING at segment 1 and PREREG at
segment 3, so it is a finding about a preregistration; a name carrying PREREG and no FINDING token
is a preregistration whatever its prefix. Two composed removal filters gave the weaker one;
precedence gives the right one.

Measured before shipping, over all 7,506 documents under `docs/staging/`: **zero** kind changes.
A pure widening for the case not yet on disk, reclassifying nothing that is. Mutation: restore the
positional rule → the leg fires.

## What is NOT fixed, and why it is out of scope rather than forgotten

`DIRECTOR_CONSOLE_2026-08-30.md` is tracked in the staging root and `room_for(KIND_CONSOLE)` names
`console/`. It is **not** a duplicate to delete: the root copy is the live 32KB console carrying
the director's own 2026-08-30 rulings across 9 turns, and `docs/staging/console/` holds a stale
2.5KB one-turn stub from 09-01. Deleting the root copy would destroy his rulings.

It cannot wedge a commit — `ROOM_DIRNAMES` is `(done, in_progress, records)` and `console/` is not
in it, so `room_collisions` never sees the pair. That omission is itself worth a look:
`room_collisions` is blind to `console/` and `reference/` duplicates entirely, which is the same
shape as the `records/` omission that left it blind for a day and is recorded in its own docstring.

Resolving it means deciding which console copy is canonical and fixing whatever writes the stub —
a content decision on the director's own channel, not a silent rider on a wedge fix.
