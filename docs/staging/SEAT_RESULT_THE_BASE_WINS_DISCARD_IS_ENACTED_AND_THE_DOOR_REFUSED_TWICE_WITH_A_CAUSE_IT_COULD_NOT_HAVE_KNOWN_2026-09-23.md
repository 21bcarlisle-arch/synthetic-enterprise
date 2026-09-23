**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — the enactment the hand-off directed, plus one finding it turned up

# The base-wins discard is enacted, and the door refused it twice with a cause it could not have known

**The work is done.** Both ladder-churn working copies on the shared tree are discarded, the base
won, and the bytes are preserved. On the way there the door refused the same enactment twice with a
verdict about CONTENT, and the only mechanism I can find that produces that verdict does not know
anything about content. That second part is the finding.

## What was enacted

    docs/reports/ladder_churn_factors.json                        3,022 lines discarded
    docs/reports/ladder_churn_factors_svt_segment_decisions.json  11,916 lines discarded

`git status --porcelain` on both paths on `/home/rich/synthetic-enterprise` is now **empty** — the
working copies match HEAD, which is what "the base won" means for a copy no landing door applies to.

Preserved first, on a ref, before a byte was written:

    refs/preserved/refresh-to-head/probe-a   979a198f6

Recoverable with `git show 979a198f6:<path>`. I verified the recovery path works — the finding
below was measured by restoring those exact bytes out of it.

*(The slug is `probe-a` and not the descriptive one I intended. That is residue of the refusal
below: the run that succeeded was one of three I fired back-to-back to isolate the cause, and the
naming discipline `--slug` exists to serve — "findable by name by someone who does not already know
what to search for" — is not served by `probe-a`. A ref cannot be renamed usefully after the fact
without breaking the pointer this document just gave it, so it stays, named here instead.)*

## The hand-off's precondition was real about the tree and inert about the work

The hand-off and the draw both said: advance the shared tree to `origin/main` first, because the
tree is behind and every verdict asks the wrong base. True of the tree. **Not a precondition of
this item**, and the reason is not a judgement:

    HEAD:docs/reports/ladder_churn_factors.json          66d57f4d91a2574b37ca34595b3e7799503f9a7a
    origin/main:docs/reports/ladder_churn_factors.json    66d57f4d91a2574b37ca34595b3e7799503f9a7a
    HEAD:..._svt_segment_decisions.json                  6c367b541a027bb19f8fd9eb751b21cc95d06f85
    origin/main:..._svt_segment_decisions.json            6c367b541a027bb19f8fd9eb751b21cc95d06f85

Same blob both sides. The two commits the shared tree was behind by (`c85e65f0d`, `58ce30050`) touch
the *door*, not the *reports*. I ran the survey both ways as a one-variable control and the outputs
are **identical modulo the base's own name in the prose** — prediction 1 of the pre-registration
holds. Prediction 2 (`--base-wins` admits both) and prediction 3 (still stale on arrival: mtime
2026-08-31 16:44:43, 23 days) also hold.

So the risky move — merging `origin/main` into a shared tree with 741 dirty files and other lanes
committing into it live — was never on this item's critical path, and I did not make it. **The tree
still needs it; this item did not.** The door itself did not need to be on the shared tree either:
`tools/refresh_to_head.py` takes `--root`, so the post-door code ran from an isolated worktree
against the shared tree's copies. The shared tree's own checkout of that tool is still the pre-door
version, and that did not matter.

## The finding: an UNAVAILABLE clock is rendered as a CONTENT verdict

Between an admitting survey and a refusing write, nothing about the files changed — same sha1, same
mtime, and on the second attempt `git rev-parse HEAD` was **identical either side of the run**, so
the moving trunk is ruled out as the cause. Both refusals read:

> `[refused_supplies_names_head_lacks]` this copy supplies 2706 JSON leaf/leaves origin/main does
> not have … **Decide which document wins and land it deliberately.**

That sentence tells the operator the door has looked at the two documents and found contested
content. The correct response to it is to go and adjudicate 2,706 leaves by hand. Meanwhile
`judge_copy` called in-process against the same tree, three times in a row, returned `refreshable`
every time.

**I could not attribute the two live refusals and I still cannot.** What I could do is ask which
mechanisms are *capable* of producing that exact verdict on a copy the clock would otherwise admit.
Measured, not argued — restoring the preserved stale bytes into an isolated worktree, resetting the
mtime to the original, and disabling one oracle at a time:

    CONTROL: clock oracle fully available                -> refreshable
    distinctive_lines() empty (transient git / filters)  -> refused_supplies_names_head_lacks
    committed_at() None (git will not answer)            -> refused_supplies_names_head_lacks

My first hypothesis was **refuted** by its own control and is recorded here because it was: I
guessed an unresolvable base, and that returns `refused_no_base` — a different, honest verdict. The
route that reproduces what I actually saw is the *clock oracle being unable to answer*.

The mechanism is a collapse of two different `None`s:

- `committed_at()` documents its own `None` as **"git will not answer"** — a declared
  unavailability.
- `distinctive_lines()` returning empty is **"cannot tell"**, and its own docstring already says
  "every filter here is also a silent fail-open".
- `clock_judge()` folds both into one bare `return None`, alongside the genuine
  *the-clock-has-no-complaint* `None`.
- `refresh_to_head.judge_copy()` reads that single `None` as "the clock did not admit it" and falls
  through to the **content** branch, which then describes leaf counts it computed for a different
  purpose as though they were the reason.

`_git` is `check=False` throughout, so a git invocation that fails on a busy shared checkout returns
empty stdout and is indistinguishable from a real negative answer.

**This is fail-closed on BYTES and fail-silent on CAUSE.** Nothing was destroyed — that part is
right, and it is why this is LATENT and not BLOCKING. But the operator is handed a definitive
content verdict manufactured from an availability failure, on a door whose entire job is *discarding
bytes*, and the remedy it names ("decide which document wins") is the one remedy that cannot help.
The honest output for this state is a third verdict — `refused_clock_unavailable`, saying so and
saying re-run — not the content one wearing its clothes.

**Not fixed here, deliberately.** The fix is a new verdict state in a door that discards bytes, and
adding one on the back of a refusal I cannot attribute is how a door acquires a branch nobody can
reach. What the fix needs first is a capture of the failing `git` call — which means `_git`'s
`check=False` growing somewhere to record a non-zero return, and that is its own small piece of
work. It is written up rather than half-built.

## What this cost, and the shape worth keeping

Three back-to-back runs to isolate an intermittent refusal, and the successful one carries a
throwaway slug into a permanent ref. **A door that refuses with the wrong cause does not just
mislead — it changes how the next operator runs it**, from one deliberate invocation into a volley,
and the volley is what left `probe-a` on the record.
