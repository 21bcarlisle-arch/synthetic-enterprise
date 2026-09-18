**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, the
residual's third voice

# The residual's third voice: a `git log` that never ran was published as "a genuine miss"

**Filed:** 2026-09-18 · **Claim id:** `the-residual-cannot-tell-a-failed-git-from-an-empty-one`
**Subject:** `background/delivery_lane.py::_window_hits`, `::_git`
**Established against:** `1cbf684ed` (worktree HEAD at the draw)

The defect and its repair are one commit, so this is RECORDED rather than BLOCKING. What it carries
that the commit message cannot is the **two premise corrections** below, both of which were believed
by the item, by the leg that measured it, and by the test fakes.

---

## 1. The premise check and the duplicate-work check, both re-measured

The item cited `2984864c7` as already an ancestor of `origin/main`. It is, and that was never the
premise: `2984864c7` gave the residual its first two voices and the item is explicitly about the
route that still picks the flattering one *after* that repair. **The premise was live**, and
measured live: `test_A_SILENT_GIT_LEAVES_THE_RESIDUAL_LOUD` asserted `looked_and_found_nothing`
against a `_git` stubbed to `None` — a failed git, reported in the answered voice — at HEAD.

The duplicate-work check named one live claim, `the-residual-cannot-tell-a-failed-git-from-an-empty-
one`, which is **this item's own id**. Not a rival under another name; the same claim, held by this
draw. No disposition was owed and the work was not built-and-unlanded: nothing in the worktree
touched `_window_hits`.

## 2. FIRST CORRECTION: the two were never indistinguishable at the wrapper

The drawn item said *"`_git` returns None BOTH for a git command that FAILED and for one that
matched nothing"*, and told me to fix it at `_git`. The leg's own docstring said the same, filed as
an **honest limit**:

> `_git` returning None is a git that failed and a git that matched nothing, and the two are
> indistinguishable AT THE WRAPPER — this leg's own docstring says so.

**It was false, and nobody asked the wrapper.** `_git` has returned `out.stdout` on `rc == 0` —
which is `""` when `git log` matched nothing — and `None` on everything else, since it was written.
`git log -- <paths>` with no matches exits **0**. The distinction was already there.

What threw it away was one line in `_window_hits`, ten lines below:

```python
out = _git("log", ...)
if not out:
    return paths, []        # `None` and `""` collapse here
```

So the repair is not at `_git` after all; it is at the **point of use**, and the item's instruction
to fix it at the seam rather than at `_nothing_answered` was still right about the layer. This is
the memory class *"an in-repo finding's factual claim about the tree can be wrong, instance wrong /
mechanism right"* — and the mechanism was exactly as described and exactly as expensive.

The honest-limit sentence is the more interesting half. A limit **recorded** rather than asserted
away is supposed to be the safe shape; here it was a wrong reading of the code, written in good
faith, that then licensed a control to assert the flattering voice **and call that rigour**. A
recorded limit is a claim with a shelf life like any other.

## 3. SECOND CORRECTION: two test fakes encoded the same conflation

`_fake_git` in `test_every_disposition_names_what_was_checked.py` and in
`test_a_window_that_closed_before_its_own_subject_existed_says_so.py` both ended:

```python
return "\n".join(lines) or None
```

— i.e. **`None` for "no matches"**, which real git never does. A fake wrong about its subject in
exactly the direction the subject was wrong is invisible while the subject collapses the two
anyway: both sides of the lie produced the same branch, so no leg could see either. They were found
by the repair, not by a review — three legs went red naming rows nobody had touched.

Both now return `""`. The "we looked and found nothing" legs in those two suites are consequently
exercised for the first time through a git that actually answered.

## 4. What landed

`_git_or_raise` raises `GitUnavailable` where `_git` returns `None`, and **returns `""` unchanged**,
so a caller cannot collapse the two in one falsy test without writing the `except` that says so.
`_window_hits` uses it; the three `except`s `_disposition` already had turn the raise into
`could_not_ask`. `_raised` puts the exception's own sentence beside its type, so the evidence names
`git log` rather than leaving the reader "something broke".

Mutation-proven, each fired and was caught by the leg written for it:

| mutation | leg that reds |
|---|---|
| `_git_or_raise` → `_git` + `if not out` (the defect restored) | `..._SILENT_GIT_LEAVES_THE_RESIDUAL_LOUD` **and** `..._NAMES_THE_COMMAND_IT_COULD_NOT_RUN` |
| `_raised` drops the exception's sentence, keeps the type | `..._NAMES_THE_COMMAND_IT_COULD_NOT_RUN` only |
| `if out is None` → `if not out` inside `_git_or_raise` (the **mirror**: everything reads unavailable) | `..._SILENT_GIT_LEAVES_THE_RESIDUAL_LOUD` **and** the partition |

The third is why the leg asserts both inputs in one statement. A leg that asserted only the failed
half would be green under a reader that says CANNOT ANSWER to everything, which is just as useless
to the seat reading the brief.

## 5. STILL OPEN — the same class, one layer up, and a smaller defect

The item predicted this was *"the ONLY place left where an unavailable check reads as a clean bill
of health"*. Re-asked over every `_git` caller in the module, the prediction **holds for a clean
bill of health** and **fails for a truthful reason**:

`_tracked_files` is `{... for ln in (_git("ls-files") or "").splitlines() ...}`. A git that will not
answer yields an empty set → `_paths_named_in` keeps nothing → `_claim_paths` is `[]` → the residual
publishes:

> CANNOT ANSWER, not 'nothing landed': this item's prose names no tracked path (in `named_paths` or
> either store holding its text), so no commit query could be built and git was never asked

The **voice is right** (`could_not_ask`, so no clean bill of health) and the **reason is a lie**: it
sends a reader to recover the item's prose when the actual fault is git. Misdirection, not a
fail-open, which is why it is recorded here rather than folded into this landing.

Not fixed in this commit deliberately. `_claim_paths` is also called bare in `tree_verdict` (no
`try`), so making `_tracked_files` raise changes the blast radius of a shared module that four
readers and the sweep depend on — a separate, measurable change, not a rider on this one.

**Remedy when drawn:** give `_tracked_files` the same treatment (`_git_or_raise("ls-files")`), then
handle the raise at `tree_verdict`'s `_claim_paths` call as well as inside `_window_hits`, and key a
leg to the *reason* — an unavailable `ls-files` must not be reported as an item with no prose.
