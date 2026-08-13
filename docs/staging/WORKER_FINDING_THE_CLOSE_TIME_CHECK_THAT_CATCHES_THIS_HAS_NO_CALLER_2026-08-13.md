# [WORKER-FINDING] A whole KNIFE step's record said LANDED while its five files sat untracked — and the check written for exactly that has no caller (2026-08-13)

**Severity:** OPEN · **Lane:** H_harness · **Status:** the instance is repaired (step 21 is
committed in `357f8fa77`); the CLASS is owed — `tools/wall_crossing_dispositions.py --at-head`
still has no automated caller.

**This is a SECOND INSTANCE of a class another lane filed the same day, and it CORRECTS that
finding's generalisation.** `WORKER_FINDING_A_REGISTERS_LANDED_IS_CHECKED_AGAINST_ANOTHER_RECORD_NEVER_THE_TREE_2026-08-13.md`
(H27 Expert Hour #23) reaches this: *"a register entry is a claim about what LANDED, and no control
compares that claim to what is committed."* On the evidence below the second half is **false, and
that is worse**: for this register a control that compares the claim to the committed tree already
exists, is proven against real history, and carries 12 R15 tests. It has no caller. A class where
the control is missing needs building; a class where the control exists unwired needs one line and
has been failing anyway — which is the sharper form of the same finding, not a milder one.

## How it was found

Not by looking for it. KNIFE3 step 22 was drawn, and the working tree it started from carried
step 21's entire change set as **untracked and unstaged files**:

```
company/crm/customer_experience_desk.py            (untracked)
company/interfaces/customer_experience.py          (untracked)
tests/company/interfaces/test_customer_experience_seam.py  (untracked)
docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md  (modified, unstaged)
tests/architecture/test_epistemic_wall_ratchet.py  (modified, unstaged)
simulation/run_phase2b.py                          (modified, unstaged)
```

Meanwhile the atom's own `map_records.exit_evidence`, written by step 21 on the same day, states:

> "4 EDGES CUT, 28 -> 24 LIVE … verified by `tools/wall_crossing_dispositions.py` rc=0 against THE
> WORKING TREE … a KNIFE step is not done at green, it is done at LANDED-AND-RECORDED."

`observed-with-evidence`: the record was true about the working tree and false about the repo. The
step's own sentence names the standard it then failed. Nothing outside this machine could see step
21 at all.

## Why this is not "someone forgot"

The register's §0a exists for this exact class, and says so at length:

> "Every instrument in this programme read the working tree. That is correct for a GATE … and
> useless for a CLAIM, because the tree under your feet is not the tree anyone else gets."

§0a was written on 2026-08-10 **after the third instance in two days**, and it built the remedy:
`tools/wall_crossing_dispositions.py --at-head`, which replays the working-tree register against a
`git archive HEAD` export and reds on a `cut` row whose import is still in HEAD. It is proven
against real history (four findings at `d06df9514`) and carries 12 R15 tests.

**And it recurred anyway, one step later, from the inside.** The control is real, it works, it
would have fired — and nothing ran it.

## The defect, stated as a control property

`--at-head` is invoked only when a human (or an agent following prose) types it. That is R15's
third killer pattern, **fail-silent**: a check that passes by not being available is a failed check,
and a check nobody runs is permanently unavailable. Every other rung of this programme is
mechanised — the ratchet reds on a new crossing, the write-time gate refuses an unrecorded module,
`wall_crossing_dispositions.py` (working-tree mode) reds on an unruled edge. The one rung that
distinguishes *claimed* from *landed* is the one left as an instruction.

The general shape is worth naming beyond this atom: **a control built to catch "the record outran
the code" cannot itself be invoked by the record.** It has to be invoked by the thing that makes the
code real — the commit.

## The fix this finding proposes, and why it is not applied in this tick

**Recommendation:** wire `wall_crossing_dispositions.py --at-head` into `tools/pre_commit_test_gate.py`
as a POST-commit or commit-time check scoped to commits touching
`docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md`, fail-closed on an unimportable module or an
exploding check — the exact shape `f4b504e6c` used to wire the finding-class checker two hours
earlier, and for the same reason ("had no automated caller … an invitation to type a command nobody
typed").

Two design questions the wiring has to answer, and they are why this is queued rather than done on
sight (SELF-INTERRUPT DISCIPLINE — the supply of harness findings is infinite):

1. **Ordering.** `--at-head` is asymmetric by design: working-tree register against HEAD's code. Run
   at *pre*-commit it measures the tree the commit is replacing, so it would red on precisely the
   commit that fixes the divergence. It needs the `surgical_land` treatment — gate the tree the
   commit WOULD create — or a post-commit hook that reds the NEXT commit.
2. **Scope.** A register edit and its code cut may legitimately land in separate commits within one
   tick. The check must be keyed to something that survives that, or it becomes a rule that punishes
   an honest split.

## What is repaired already

Step 21 and step 22 landed together in `357f8fa77`, pushed. `--at-head` was run by hand against the
resulting HEAD and returns rc 0: *"measured against HEAD (the committed tree): 22 live crossings (20
direct, 2 indirect); 91 ruled (cut 69, owed 22, grandfathered 0)."* The step-22 record in
`docs/design/simplifications/KNIFE3_wall_crossing_paydown.yaml` states the miss rather than
smoothing it over.

`inferred`, and flagged as such: I cannot tell from the repo whether step 21's tick was interrupted
before its commit or whether it believed it had committed. Both are consistent with the evidence,
and the mechanism owed is the same either way.
