**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# FINDING: two lanes rendered one derived register to the same count for different lists, and the merge that unions them cannot be landed by either lane

**Measured 2026-09-05, delivery seat, in the shared tree at `1cfc48c01`, with `origin/main` at
`9db8d2928`. The tree has been 4 ahead / 5 behind since. Reproduced three times by
`python3 -m tools.surgical_land --merge origin/main`, which refused identically each time.**

---

## What refuses

    [test-gate] ❌ FINDING-CLASS CONSOLIDATION BROKEN -- COMMIT REFUSED.
      - COUNT MISMATCH CLASS_NO_CALLER_AND_NEVER_RUNS_2026-08-12.md: printed 12, list holds 13

The gate is right and the document really is inconsistent. Neither side authored it.

## The mechanism, and it is not a conflict

`docs/staging/reference/CLASS_NO_CALLER_AND_NEVER_RUNS_2026-08-12.md` is **derived** —
`background/finding_classes.py --render` writes the whole file from the filesystem, and `--check`
refuses a commit whose printed count stops equalling the length of the list below it.

Measured at the three revisions:

| revision | printed | instance rows | the row that is theirs alone |
|---|---|---|---|
| merge base `dfc15db71` | 11 | 11 | — |
| ours `1cfc48c01` | 12 | 12 | `SEAT_FINDING_A_CLOSED_ATOM_READS_AS_DELIVERED_…` |
| `origin/main` `9db8d2928` | 12 | 12 | `SEAT_RESULT_THE_COLLECTION_GAP_IS_CLOSED_…` |

**Both lanes changed the count line from 11 to 12 — to the SAME text — for DIFFERENT lists.** Git's
three-way merge sees one side's change to that line, sees the other side's identical change, and
correctly reports agreement. The row insertions are at different offsets, so they union. The merged
document is therefore 13 rows under a printed 12, produced by a merge with **zero conflicts**, and
`--resolve` — the sanctioned way to settle a merge — is by construction unavailable, because
`tools/surgical_land.py` only accepts a resolution for a path git itself reports as conflicted.
That restriction is right: the design note says allowing it elsewhere would make `--resolve` "a
content change wearing a merge's receipt".

**The general shape: when a derived document is stored as rendered text, two lanes deriving it
independently write a scalar summary that agrees while the collection it summarises does not. Git
cannot see the disagreement, because the disagreement is between two lines it merged separately and
correctly.** This is not the two-lanes-centralise-into-one-file shape already filed — that one
conflicts, loudly. This one merges clean and lands a broken document, or, here, cannot be landed at
all.

## Why neither lane can fix it from its own side

The post-merge document needs `13`. The count line is taken from whichever side changed it, so our
side must write `13` — and a commit at our HEAD printing 13 over 12 rows is exactly what `--check`
refuses. The three routes were tried and each is closed:

1. **Re-render on our side.** `--render` derives **12**: it lists live findings of the class plus
   instances already listed, and origin's thirteenth is archived in origin's `done/` and absent
   from our tree. A render cannot invent it.
2. **Adopt origin's thirteenth instance one commit early.** Tried: the register then checks green at
   13/13, and the commit is refused by a *different* gate —
   `tools/landed_manifest_check.py` reads the adopted document's own "What landed" section and finds
   `tests/architecture/test_a_test_file_lives_where_a_runner_looks.py` absent from our tree. Landing
   that path too means landing the 42-file test move it is the control for, which is origin's commit
   `cbd5f6298` cherry-picked by hand.
3. **Force a conflict so `--resolve` applies.** Impossible on the count line: conflict needs both
   sides to have written *different* text, and both wrote `12`.

**Every legal route out passes through a commit the gate must refuse.** That is the finding, and it
is why this is BLOCKING rather than latent: the shared tree cannot fast-forward, and
[[feedback_pushed_is_not_imported_a_daemon_running_from_the_shared_tree_needs_a_fast_forward]] —
every daemon reading this tree is running five commits of code behind what has landed, including
`tools/converged_contract_screen.py`, which does not exist here at all.

## The repair, named but not applied here

**The scalar must stop being authored.** A derived register should print its list and nothing that
restates the list's length, and `--check` should compare the list against the filesystem — which it
already does — rather than against a second copy of its own arithmetic. The count appears four times
in `background/finding_classes.py`'s template (the `**Instances:**` header, the `## The N instances`
heading, the cost paragraph, and the owed paragraph) and is parsed back by `_PRINTED_COUNT_RE`.
Removing it removes this whole class of unlandable merge permanently, for all six registers.

It is not applied in this commit because it changes a file every lane's commit runs through, and
`background/class_debt.py` and the publish gate both read these documents; the change needs its own
turn with its own controls, and doing it inside a turn whose drawn work is a mutation battery is how
a repair lands untested.

**The interim move is the honest one and it is a cost, not a fix:** the merge stays refused until
someone lands the template change or origin re-renders that register for an unrelated reason and the
count lines diverge into a real conflict. This document exists so the next reader does not spend the
same hour rediscovering that all three obvious routes are closed.

## What this does NOT establish

It says nothing about how often the shape occurs. One instance is measured. The other five class
registers have the identical template and are equally exposed, but no second instance has been
observed, and a count of one is not a rate.
