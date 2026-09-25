**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The live-hook report says "the hook chain git will run IS origin/main's, byte for byte" while 2 of the 25 modules that chain invokes are NOT origin/main's

**Class:** `controls_that_cannot_fail` — the instrument's subject is two FILES; its printed claim is
about the CHAIN. Both legs of the gap are live on the shared tree right now, from two different
causes, and the verdict is green for both.

BLOCKING under clause 2: this is a statement that an instrument in this area is untrustworthy, and
the consequence is that a lane about to trust a green gate is told the live chain is the trunk's when
it is not. Sibling, and deliberately not a duplicate:
`docs/staging/SEAT_FINDING_THE_LIVE_HOOK_REPORT_READS_CLEAN_ON_A_HAND_PATCH_AND_ITS_STATED_REMEDY_DESTROYS_IT_2026-09-25.md`
(RECORDED) is about what the BYTES verdict is read to mean. This one is about the SUBJECT SET being
narrower than the sentence.

## Measured on the shared tree, 2026-09-25

`tools/live_hook_drift.py` compares `TRACKED_HOOKS` — `tools/git-hooks/pre-commit` and
`tools/git-hooks/commit-msg` — against `origin/main`, and parses the chain's `python3` invocations to
compare the invocation LIST. It does not compare the modules those invocations run. Using the
module's own parser (`hook_invocations` + `invocation_subject`) over the reference texts:

    invocations parsed from the two chains : 25
      resolve to a module file            : 25
      DIFFER from origin/main on disk      : 2
        tools/level_promotion_gate.py
        tools/live_hook_drift.py

    hook FILES differing from origin/main  : 0

And the report, verbatim, in that state:

    [live-hook] the hook chain git will run IS origin/main's, byte for byte
               (/home/rich/synthetic-enterprise/tools/git-hooks/pre-commit).

**The two stale modules are stale for different reasons, and that is the finding's shape:**

* `tools/live_hook_drift.py` — disk **==** HEAD, HEAD **behind** `origin/main`. The stale-checkout
  cause. (Caused by my own `f0968c077`, landed an hour earlier; the checkout is 1 ahead / 3 behind,
  so `--ff-only` cannot close it, which the report DOES say correctly on its own line.)
* `tools/level_promotion_gate.py` — HEAD **==** `origin/main`, disk **differs from HEAD**. Another
  lane's uncommitted working-copy edit. **A gate module that is in no commit is gating every commit
  on this machine right now**, and nothing says so. This one is not mine and is not a checkout lag;
  no advance of any kind will clear it.

## Why the narrow subject is the defect and not an oversight to widen casually

`core.hooksPath` is the shared tree's WORKING COPY, so every `python3 -m tools.X` in the chain
resolves from that working copy — 25 modules of gate logic, none of them in the instrument's subject.
The hook files change rarely; the modules change daily. So the subject set is the half that almost
never moves, and the verdict is therefore green almost always, including in the condition the module
exists to catch. That is the same shape as the module's own hand-patch leg, one layer down.

**A landed gate change is inert until the checkout advances, and a gate change that was never
committed is live until someone notices.** Both are invisible behind the sentence above.

## The remedy, and the reason it is filed rather than fixed on sight

One honest line in `report()`: *"the chain's FILES are the trunk's; N of the M modules it invokes are
not (`<paths>`)"*, with the two causes distinguished — behind-HEAD vs differs-from-HEAD, because the
remedies are opposite (advance the checkout / find whose edit that is). The parser is already there;
this needs a per-subject byte comparison and one report line.

It is NOT wired in this pass because `Drift.clean` and `Drift.needs_reader` are pinned by controls in
`tests/tools/test_live_hook_drift.py` and read by `surgical_land`'s own
`_say_which_hook_chain_the_other_door_runs`, so adding a term to either is a change to a control
several lanes depend on — and the claim that produced this measurement was already released. Add a
new field and a new line; do not redefine `clean`, which is a statement about the invocation list and
is correct as it stands.

## Falsifiers

* Re-run the census above. If it returns 0 stale modules, the instance is gone — but the gap is not:
  plant a one-character change in any module the chain invokes, in the working copy only, and the
  report must still say the chain is the trunk's byte for byte. That is the control.
* `git diff --quiet HEAD -- tools/level_promotion_gate.py` — if it is now quiet, someone committed or
  reverted that edit, and the second cause needs a fresh instance to stand on.
