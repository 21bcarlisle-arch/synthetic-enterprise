**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** delivery-lane-residual-voices

# The fourth voice landed, and the fixture that hid it was asserting the lie as correct

**Filed:** 2026-09-18 · **Drawn as:** `the-tracked-files-join-publishes-the-right-voice-with-a-lying-reason` (LANE 0 DELIVERY)
**Found by:** doing the drawn work, then asking the one question the item told me to ask — *does any
other `_git` caller in this module read an unavailable check as a clean bill of health?* — of the
**test fixtures** as well as the module.

---

## The premise check was a false alarm, and the item was still live

The doorbell warned that `38a8241f3` is already an ancestor of `origin/main` and the work may have
landed by another route. It has, and that is **expected rather than spent**: `38a8241f3` is the
commit that landed the *third* voice, which this item explicitly builds on ("the same class as the
third voice just landed in `38a8241f3`, one layer up"). A cited commit is context here, not premise
— exactly the shape `premise_note`'s own docstring says it annotates without suppressing. Re-measured
before starting: `_tracked_files` still read `_git("ls-files") or ""` at HEAD. The work was undone.

## The drawn work

`_git` has always distinguished a git that FAILED (`None`) from a git that answered nothing (`""`).
`_tracked_files` threw that apart away with `or ""`, so an unanswerable `git ls-files` produced an
empty tracked set → `_paths_named_in` kept nothing → `_claim_paths` returned `[]` → the residual took
its NO-PATHS branch and published:

> CANNOT ANSWER, not 'nothing landed': this item's prose names no tracked path (in `named_paths` or
> either store holding its text), so no commit query could be built and git was never asked

**The voice was right and the reason was a lie.** `could_not_ask` is the correct disposition and was
already being published — which is precisely why no existing control caught this. The four suites
sharing `residual_voices.could_not_ask` were all green. What was fabricated is the **cause**, and the
reader it lies to goes hunting for an item's prose that was never missing.

Landed: `_tracked_files` now calls `_git_or_raise("ls-files")`. The raise propagates through
`_paths_named_in` → `_claim_paths` → `_window_hits`, lands in the three `except`s `_disposition`
already had, and arrives at the residual's FIRST branch as
`the unbound-commit join raised GitUnavailable: \`git ls-files\` would not answer`.

## Three callers needed an answer, not one

The item named two (`_window_hits`, `tree_verdict`). Grepping `_paths_named_in` found **three**
production callers, and the third was a regression waiting to happen:

| Caller | Handling | Why |
|---|---|---|
| `_claim_paths` → `_window_hits` | propagates | the point of the repair; reaches `could_not_ask` |
| `tree_verdict` | catches → `None` | its docstring already promised `None` covers "a git that would not answer"; before this the promise held *by accident* |
| **`record_draw`** | catches locally → no stamp | **`record_draw`'s outer `except` RETURNS.** An uncaught raise there would have dropped the whole row — losing `last_drawn_at`, the instant every window, sweep and disposition downstream keys off. The draw would not have been remembered at all, and no control on the residual's wording could ever have noticed, because the row would not be there to dispose of. |

`rival_claims` reaches `_paths_named_in` too and is already wrapped by `rival_note`'s declared
fail-open (an annotation, never a refusal) — consistent with its own docstring, left alone.

## The other `_git` callers: the item's "this is the last one" claim holds

Re-asked over all thirteen. Nine were already safe **and said so in their own prose**:
`_merge_base_side` refuses with a named reason; `_commit_facts` tests `is None`; `_cited_commits`
tests `is not None` with a docstring explaining why truthiness inverts it; `_stranded_paths` returns
`[]` where empty is never a finding; `premise_note` is a *declared* fail-open with its reason given.

`_direction_history_text` was the one that looked like a second instance — an unavailable git empties
it to `{}`, which reaches `_paths_named_in` as empty *text*. It is closed by the same stroke and not
by a second fix: **`_tracked_files` is asked before the text is looked at**, so the raise fires on
that route too rather than the emptied reach-back being mistaken for a quiet item.

## The finding: the fixture was asserting the lie as correct

Landing the repair reddened one sibling leg —
`test_a_window_that_closed_before_its_own_subject_existed_says_so.py::test_THE_RESIDUAL_PARTITION_...`
— and the red was the valuable part of this turn.

That test's branch 2 carries the comment *"the item's prose named no tracked path, so no query could
be built"*. Its fake answered `None` to everything that was not `log`. So the tracked set came back
**empty for every input**, and branch 2 was reached by **git's silence**, never by the road its own
comment claims. The leg asserted `"no tracked path" in evidence` — it was **asserting the defective
sentence as the correct answer**, and it read green for as long as the subject collapsed the two.

A fake more permissive than its subject, holding open the exact conflation the subject was being
repaired to close. Both copies of the helper now answer `ls-files` honestly. In the twin
(`test_every_disposition_names_what_was_checked.py`) the same change is **inert today — an
equivalence established by reading the rows, not assumed**: every row there carries `named_paths`, so
`_claim_paths` is answered from the ledger and never asks git. Fixed as a class anyway; the first row
added there without a stamp is where that copy would have inherited the defect.

## What done means here, and the mutations that prove it

No exit test was written for this item, so: **the residual names GIT when git is the fault, names the
ITEM when the item is, and both roads stay reachable.**

`tests/background/test_an_unanswerable_ls_files_is_not_published_as_prose_naming_no_path.py`, 5 legs.
The partition leg is one statement over both branches, per the rare-branch rule. Mutation-proven in
both directions, via a patched-in copy of the old implementation rather than a shared-tree write:

* **restore `or ""`** → partition leg fires, reproducing the exact lying sentence; the seam leg fires
  (`DID NOT RAISE GitUnavailable`).
* **raise unconditionally** → partition leg fires *on its other half* ("the NO-PATHS branch must stay
  reachable when git ANSWERED"); the empty-`ls-files`-is-an-answer leg fires.

The second mutation is the one that matters: a subject that raised on everything would have passed
the defect leg on its own. The empty-is-an-answer leg is an **equivalence** under mutation 1 and
fires only under mutation 2 — that is stated rather than left to the flattering reading.

Green: 69 across the seven affected suites; `finding_classes --check` PASS; `finding_severity` 0
unclassified; `ruff` clean.

## Incidental: a 13-day-old stranded file reds the ratchet in the worktree only

`tests/architecture/test_static_quality_ratchet.py` went red while I was pre-running the cheap
gates, on `I001: 1308 → 1307` — the count **improved**, which is the ratchet's stale-baseline leg
doing its job. It is not mine and it is not new. The single file responsible is
`tests/tools/test_generate_maturity_map_data.py`, uncommitted with **mtime 2026-09-05** — thirteen
days, so a dead invocation's leavings rather than a live lane's in-flight repair.

Measured rather than assumed, because "reds far from your change" has two readings here: I rebuilt
HEAD in a `git archive` extract (1308, matching the frozen baseline), copied **only my five files**
in, and re-counted — still 1308, and both ratchet legs pass there. So the red is the stranded file
alone and my commit does not carry it.

**It is not a wedge.** The gate grades a throwaway HEAD checkout, not the worktree, so no lane's
commit is blocked by this; what it costs is every lane that pre-runs the ratchet in the shared tree
being handed a red that names a file they never touched. Left for its owner rather than committed by
me — landing another lane's two-week-old bytes under my claim is how attribution gets buried — but
recorded here because the next seat to hit it will otherwise spend the same twenty minutes I did
establishing that it is not theirs.

## Still owed

Nothing on this item — it is the last of the four voices, and the re-ask over every `_git` caller is
recorded above rather than left as a claim. **Note for whoever reads this next:** the two sentences
above about the other nine callers are a measurement taken at this commit, not a standing property.
A new `_git` caller written with `or ""` re-opens the class, and nothing in the module refuses it —
the only control is `_git_or_raise` existing and being the obvious thing to reach for.
