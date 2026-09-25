# RESULT — the checkout advanced, it was not by merge, and the item's central claim was refuted by the mechanism it said could never run

**SEVERITY: HIGH** — a commit carrying neither a `surgical_land` receipt nor a hook-gate mark reached
`origin/main` today, through a door that does not check for either, while the seat's door was
refusing the same leg for lacking them.

Claim id: `advance-the-shared-checkout-by-merge-because-ff-only-can-never-pass-a-diverged-tree`.
Predictions in `PREREG_ADVANCING_THE_CHECKOUT_BY_MERGE_IS_A_DIFFERENT_OPERATION_WITH_A_DIFFERENT_BLOCKING_SET_2026-09-25.md`,
written before any of this was measured and kept unedited beside the answers.

## The state the item asked for was reached, and not by me

    shared HEAD  c0c5f1fcb      origin/main  c0c5f1fcb      0 ahead / 0 behind
    live_hook_drift: "the hook chain git will run IS origin/main's, byte for byte"

Done-condition 1 of the pre-registration is met. It was met by `background/origin_reconcile.py`'s
ordinary merge leg — isolated worktree, `surgical_land --merge origin/main`, push, then the
`--ff-only` advance, which by then WAS a fast-forward. The divergence closed from the ahead side, in
exactly the words `advance_shared_tree`'s own refusal gives: *"The fork closes by landing those
commits on origin (the reconciler's own merge leg)"*. **That sentence was correct and the mechanism
worked.** The item said it could not run, forever.

## WHY THE ITEM BELIEVED OTHERWISE, and this is the finding

The item's reasoning: the ahead leg cannot promote because `6a422ea0f` carries neither a receipt nor
a mark, and `promote_worktree_landing` refuses the whole leg on it — so the ff-only advance refuses
forever. Every step of that was verified at its own oracle and the conclusion is still false, because
**there are two push doors and they apply different rules.**

    promote_worktree_landing   grades EVERY ahead commit for a receipt or a mark   (the seat's door)
    origin_reconcile._push     `git push`                                          (the daemon's door)

Measured now, after the fact: `git merge-base --is-ancestor 6a422ea0f origin/main` → **TRUE**.
`6a422ea0f` has `receipt=0 mark=0`. It is on the trunk. The seat's door would still refuse to put it
there.

This is not new as a class — `SEAT_FINDING_THE_SEATS_PUSH_DOOR_REFUSES_UNGATED_ANCESTORS_AND_THE_RECONCILER_PUSHES_THEM_ANYWAY_2026-09-24.md`
names it. What is new is that the class was load-bearing in a drawn item's premise: the item reasoned
from the seat's door about what the daemon's door would do, and the queue carried that reasoning as
established fact. **A rule enforced at one of two doors is not a rule, and its second door was the
one that moved.**

AND THE HONEST OTHER HALF, which the finding above does not say and which decides what to do about
it: the reconciler's merge leg runs `surgical_land --merge`, so **the merged TREE was gated**. The
content on the trunk passed the chain; what it lacks is per-commit evidence on each ancestor. Those
are two different proofs, both real, and the stricter one is the one pointed at the human. Closing the
asymmetry by adding the receipt check to the daemon's push would recreate exactly the permanent wedge
this item was drawn for — so it is NOT the remedy, and the remedy is not obvious. Parked as a finding
rather than guessed at.

## THE PREDICTIONS, EACH KEPT BESIDE ITS ANSWER

**P1 — REFUTED, and it was my reading that was wrong, not the code.** I predicted the ff blocking set
would be computed as `git diff HEAD origin/main` and would be strictly larger than the merge's, and
measured 32 paths against 12, with 6 of 7 named blockers innocent. `_arriving_paths` does not use that
formula. It diffs HEAD against the **merge-result tree** from `git merge-tree --write-tree` — the
correct question — and was fixed to do so on 2026-09-11 for this exact reason; its docstring says so.
Recomputed with the live formula against the shas as they stood (`git diff --name-only 025b2793c
00e0982f2`): **12 arriving paths** — and independently corroborated after the fact by the reconciler's
own receipt on `c0c5f1fcb`, which records `paths: 12` for the same merge, and the blocking set the reader would actually have been shown was
**one path** — an untracked staging note, which is class 4 and which `advance_shared_tree` can clear
on its own. My 7 was the superseded formula's answer. **A repair I was about to write was not owed,
and the pre-registration is the only reason I know that**: I had the number before I had read the
function.

**P2 — CONFIRMED, and it refutes a sentence this module is built on.** With a staged change at
`site/data/publish_provenance.json`, a path the merge does NOT touch, `git merge --no-ff origin/main`
answered *"error: Your local changes to the following files would be overwritten by merge"* and
changed nothing. Git refuses a merge on ANY dirty index entry, involved or not. So the 2026-09-02
justification in `origin_reconcile`'s docstring — *"57 index entries belonging to another lane ... a
`git merge` there would have swept every one"* — **is false for staged entries: git refuses rather
than sweeps.** The fear is real for the isolation argument generally and wrong in the specific shape
it is written in. Left as a finding, not edited into the docstring, because the isolation conclusion
it supports is right for other reasons and I have not measured those.

**P3 — CONFIRMED, and it was the actual blocker.** `commit-msg` runs on a merge commit; `pre-commit`
does not (git runs `pre-merge-commit`, which this repo has not got). And the `commit-msg` chain
**refused the merge**: `write_time_gate` read `tools/live_hook_drift.py` — arriving from the second
parent, authored and recorded by the trunk commit that landed it — as a module this merge had written,
and demanded a REUSE record for it. `staged_additions` asked `git diff --cached --diff-filter=A`,
which compares against `HEAD`, and for a merge HEAD is only the FIRST parent.

The only two shapes that satisfied it were both defects: a REUSE record asserting an authorship that
did not happen, or `--no-verify`, which is a wall. **So the hand merge this item prescribed was itself
impossible, and nothing anywhere said so.** Fixed and landed: a path present in ANY parent is not
added by the commit, keyed to `MERGE_HEAD` rather than to a word in the message, with three controls
and three source mutations, and `None` (never `set()`) on an unreadable parent so the exemption cannot
fail open behind one broken subprocess.

**P4 — resolved in a direction I did not offer.** I wrote *"I cannot yet say whether the shared tree
can be merged today"*. It never needed to be: the ahead leg reached the trunk and the advance became
an ordinary fast-forward. The staged set moved from 4 paths to 3 between two reads three minutes
apart while I was measuring it, which is the same minutes-wide window the module documents.

### AND THE SCOPE OF THAT REFUSAL, CORRECTED BESIDE MY OWN LANDING MESSAGE

`592e84cd0`'s message says the refusal *"held the live hook chain behind the trunk"*. That overstates
it and the qualification is this: **`surgical_land` commits with `commit-tree` + `update-ref`, so
`commit-msg` — and therefore `write_time_gate` — NEVER runs for it.** It runs `pre-commit` in a clean
extract instead. A plain `git merge` runs `commit-msg` and never runs `pre-commit`. Two doors, two gate
chains, which is the finding `bfa285755` already landed.

So the gate defect blocked the **hand** merge door — the one this item prescribed, and the only one
available to a seat merging the shared tree in place — and never touched the reconciler. The wedge's
actual cause was divergence alone, and the reconciler closed it through the door the defect could not
reach. The repair is still real and still owed: it is what makes the prescribed remedy possible at
all. It was not what was holding the tree.

## THE DECISION I AM TAKING, and it is a decision and not an omission

**`advance_shared_tree` does NOT get a merge leg.** The item asked for one. Against it:

* The route that exists reached the state today, unattended, in the words its own refusal predicts.
* A merge leg in the shared tree is a **second commit door into that tree that `pre-commit` does not
  gate** — git does not run it for merges (P3). The module's entire design argues the merge belongs in
  isolation, gated, and today is evidence for that design, not against it.
* The one path that blocked the ff was in a class the existing five-class machinery already clears
  (P1). There was no path the machinery could not take.
* Build the smallest mechanism that can fail. The mechanism that was missing was one line in a
  message gate, and it is now there.

What was genuinely structural — that **advancing the CHECKOUT and authoring code are two operations,
and one gate read the first as the second** — is repaired as a class, at the gate, where it belongs.

## AND THE TWO DOORS LEAVE TWO MUTUALLY EXCLUSIVE KINDS OF EVIDENCE, WHICH EXPLAINS THE DISJUNCTION

`surgical_land` runs ONE thing: `sh tools/git-hooks/pre-commit`, in a clean extract (`run_gate`, and
its own receipt line says so). It contains no reference to `commit-msg`, `write_time_gate` or
`next_step_gate`, and it commits with `commit-tree` + `update-ref`, so git never invokes them. The
`git commit` door is the mirror image: `commit-msg` runs, and for a MERGE `pre-commit` does not.

I had this backwards for part of the turn: I assumed the REUSE gate ran on every landing because
`CLAUDE.md` lists it as enforced and tells the seat to pre-run it. It is enforced — on one door.

Measured over the last 16 commits on `origin/main`, headers matched exactly
(`^\[surgical-land receipt\]`, `^\[hook-gate mark\]`):

    14 commits   receipt=1  mark=0     (every surgical_land landing)
     2 commits   receipt=0  mark=1     (e18f85222, 8e40bb205 -- the `git commit` door)
     0 commits   both
    6a422ea0f    receipt=0  mark=0     (neither: it predates the mark mechanism)

**Receipt XOR mark, exactly, by construction — a commit cannot carry both.** That is why
`promote_worktree_landing` accepts either one: they are not two independent checks of the same thing,
they are the two doors' signatures, and "receipt OR mark" means "came through a door".

**THIS IS NOT MINE AND IS ALREADY FILED.**
`SEAT_FINDING_A_RECEIPTLESS_COMMIT_IS_A_HOOK_GATED_ONE_AND_THE_DOOR_ACCUSED_EVERY_DAEMON_COMMIT_OF_A_BYPASS_2026-09-24.md`
(BLOCKING, H_harness) established a day ago that a receiptless commit is a hook-GATED commit and that
`RECEIPT_HEADER` is written only by `surgical_land`. What this adds is the census — the partition is
exact over 16 consecutive commits, with no member carrying both — and the corollary below, which that
finding does not draw. **And it is a third instance of the same class in one item**: the seat's push
door, the two gate chains, and now the two evidence kinds. `6a422ea0f` reaching the trunk today is
that class being paid for.

*(Corrected in passing: my first pass at this grepped `^\[hook-gate\]` and scored mark=0 on all 16,
and an earlier pass counted prose mentions and scored mark=3 and mark=5 on commits that are ABOUT the
mark. `MARK_HEADER` is `[hook-gate mark]`. The XOR above is the third reading and the first correct
one; the two wrong ones are named here because either would have supported a different conclusion.)*

### THE CONSEQUENCE, AND IT IS A HIGH GAP OF ITS OWN

`write_time_gate` is the REUSE gate CLAUDE.md lists as enforced, and `next_step_gate` beside it.
Both live in `commit-msg`. **Neither runs on the sanctioned landing door.** On the sample above that
is 14 of 16 landings on which a new capability module owes no REUSE record and nothing notices — and
`CLAUDE.md` tells the seat *"A new module needs a REUSE block in the commit message"* for landings
made through the door that does not read it.

I am NOT wiring them in this turn, and that is a decision. `next_step_gate` would begin refusing
every `surgical_land` landing in every lane that does not carry a `NEXT:` line, mid-flight, including
other writers' — a blast radius well outside an item about a checkout advance, and the kind of change
that wants its own turn and its own measurement of how many live landings it would refuse. Filed.

## WHAT IS STILL OPEN

1. The two push doors and their two proofs (above). Needs a judgement about whether a gated merge
   commit covers its ungated ancestors, which is a wall question and not a cadence's to make.
2. `origin_reconcile`'s docstring carries the refuted sweeping sentence (P2) as live justification.
3. **The REUSE and next-step gates do not run on the `surgical_land` door** (above). The measurement
   is done; the repair is not, and it needs a census of how many landings it would refuse first.
4. The item's own premise is spent. Anything drawn from *"the reconciler refuses every run, forever"*
   should re-ask `git rev-list --left-right --count HEAD...origin/main` before believing it.
