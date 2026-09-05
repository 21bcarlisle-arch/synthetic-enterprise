**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# FINDING: the stand-down was never the binding constraint, and the fast-forward was refusing on files it was about to write back unchanged

**Written 2026-09-04, delivery seat, from the deadman's own 24h log.** The drawn direction named two
candidate remedies and asked which to cost. The measurement says both were aimed at a cost that is
mostly not there, and names a third that is.

---

## What the direction assumed

> *"the reconciler stands down for the gate, the publisher stands down for the fork, and each
> publish cycle re-opens the fork the next reconcile must close. Nobody is wrong and the reader goes
> stale."*

and from that, two candidates: **(a)** let the publisher commit-but-not-push at `ahead>0`; **(b)**
give `origin_reconcile` a window the publish cadence cannot close.

Both are remedies for *the reconciler not getting a window*. So the first thing to measure was
whether it gets one.

## It gets one. 129 times out of 165.

`journalctl --user -u deadmans-switch --since "24 hours ago"`, counting the reconciler's own verdict:

| verdict | count |
|---|---|
| `LEVEL` (nothing to do) | 117 |
| `GATE_RUNNING` (**stood down for the gate**) | 36 |
| `PUSHED` | 6 |
| `NOT_ADVANCED` | 4 |
| `REFUSED_GATE` | 1 |
| `FAST_FORWARDED` | 1 |

`GATE_RUNNING` is 36 of 165 cadences — **22%**. The reconciler reached a window on the other 78%.
Candidate (b) buys a window that is already there, and candidate (a) reverses a documented refusal
to solve a starvation that the log does not show. **Neither is the binding constraint.**

## What the binding constraint is

`NOT_ADVANCED`, and its own detail string had been naming the cause since the `blocking_paths` work
went in:

```
ORIGIN FORK (NOT_ADVANCED): the merge gated clean and was pushed, but the shared tree did NOT
advance and is still 2 commit(s) behind. Refused by 2 path(s):
  background/process_run_complete.py  (modified here, and origin changes it too);
  docs/staging/SEAT_PREREGISTRATION_HOW_WIDE...md  (untracked here, and origin adds its own copy)
```

The reconciler gates its merge, pushes it, origin advances — **and then the shared tree will not take
what was just pushed.** So origin moved, this tree did not, the publish path read `behind_origin` and
threw away a completed cycle, and the next cadence started one commit deeper. That is the loop, and
the gate stand-down is not in it.

## And a third of the refusal was protecting files from being replaced by themselves

Measured on the live shared tree, the two paths then holding the fast-forward:

```
docs/staging/SEAT_FINDING_THE_SEND_ONCE_MEMORY...md
    local  git hash-object      792088eca625b2ef646fe57716d478f44aca6d2f
    origin rev-parse origin/main:  792088eca625b2ef646fe57716d478f44aca6d2f   ← IDENTICAL

docs/staging/SEAT_FINDING_THE_THREE_CARRIERS...md
    local  70bdf5664...   origin  c3967d950...                                ← genuinely differs
```

Git refuses to clobber an **untracked** file whatever its content. So the first path's refusal was
protecting a file from being overwritten by a byte-for-byte copy of itself, and it was holding the
publish path stale to do it.

**`paths_blocking_fast_forward` already said this**, in its own docstring, and only a human could act
on the sentence:

> *"`FF_UNTRACKED` — an untracked file here that origin ADDS. Usually byte-identical, and then
> nobody's work is at stake at all: `git hash-object` against `git rev-parse origin/main:<path>`
> settles it in one command."*

It settled it for a reader and for nothing else. The module knew the answer and could not use it.

## What was built

`origin_reconcile.advance_shared_tree()` — one advance, called by **both** of `reconcile`'s
fast-forward legs rather than hand-rolled beside each. It tries the fast-forward; on refusal it asks
which paths blocked it, hashes each untracked one against origin's blob at the same path, removes
only those that match, and retries once.

**The safety argument is the hash equality and nothing else.** If the bytes at `P` equal origin's
blob at `P`, the content is already on origin: removing the local copy cannot lose it, and the very
fast-forward this unblocks writes those same bytes back to that same path. The file goes from
untracked to tracked and its content never changes.

**All-or-nothing, and that is a safety property.** Nothing is removed unless removing the twins would
leave the fast-forward with nothing else to refuse on. A tree holding one `FF_MODIFIED` path cannot
advance however many untracked files are cleared, so clearing them there would be a deletion bought
for no advance — the one shape in which this could cost a lane real work. On the live state above it
does exactly that: two blockers, one twin, one genuine difference → **removes nothing**.

Anything not byte-identical stays refused. That judgement is not what this automates.

## What it does NOT do, stated plainly

It does **not** answer the direction's actual question — what the publisher may do at `ahead>0 AND
behind>0`. That case still refuses, and `_advance_to_origin_or_say_why` still hands it to
`origin_reconcile`'s gated merge door. What changed is that the gated merge door can now finish:
its merge-push-then-advance sequence was the leg failing most often in the 24h log, and it was
failing on twins.

Whether the real fork still needs a publisher-side answer is now measurable rather than assumed —
the loop that was manufacturing forks out of lossless collisions is closed, so what remains is
whatever is left when that stops. **I am not carrying candidate (a) or (b) further until a day of
log says the residue is real.** Reversing a documented refusal to fix a 22% stand-down, before
removing a cause that fired on the majority leg, is how a cure becomes the next cause here — this
module's own 29-empty-merge incident is the precedent.

## What this discharges elsewhere

`SEAT_PREREGISTRATION_WHETHER_A_MECHANICAL_ADVANCE_AT_THE_REFUSAL_LETS_A_DRAINED_QUEUE_CLOSE_ITS_EPISODE_2026-09-04.md`
predicted its own **P1** would most likely be refuted by exactly this, and named it in advance:

> *"the one blocking path was an untracked lossless twin — **which is the OTHER lane's repair, not
> mine**, and if theirs has not landed the ff still refuses and P1 fails on a cause I did not fix.
> That is the most likely way this is refuted and I am saying so in advance."*

That prediction was right and this is the repair it named. P1 is now testable on its own terms.

## The control, and the mutation that survived

`tests/background/test_the_advance_refused_on_files_it_was_about_to_write_back_unchanged.py`.

The reachability control is the load-bearing one: every other test in the file asserts the advance
**refuses**, and an `advance_shared_tree` that refused unconditionally would pass all of them. It
asserts all four outcomes are attainable from the same function.

**One mutation survived the first draft and it was the informative one.** Making the
`blocking is None` branch unreachable changed nothing: `None` is falsy, so it fell through to
`if not blocking:` one line below and returned the same `False`/`[]` by the other route. Same values,
opposite meanings — *"I could not look"* versus *"I looked and nothing collides"* — which is a
distinction `paths_blocking_fast_forward` says in its own docstring is deliberate. The assertion was
keyed to the values, so it graded a fail-open as fail-closed. Re-keyed to the reason string, the
mutation fires. Recorded here rather than quietly fixed, because it is the same shape this project
keeps paying for: *two routes to one value make a value assertion a tautology.*

## One control was keyed to today's answer, and this change proved it

`test_the_shared_tree_is_only_ever_FAST_FORWARDED_and_git_may_refuse` read
`inspect.getsource(orc.reconcile)` for the literal `"merge", "--ff-only"`. Hoisting the advance into
a shared function so both legs could use the repair turned it red **while the property it guards was
untouched** — a control that goes red when the code gets better. Re-keyed to the property: every
`git merge` in the module is `--ff-only`, and `reconcile` reaches the shared advance. `--force` is
not banned module-wide, because `git worktree remove --force` on a throwaway checkout is legitimate
and unrelated — it is banned in the one function that writes the shared tree.

## Class registration

Belongs to `uncommitted_and_orphaned_work`.

*Declared 2026-09-05 by the delivery seat, on the director's instruction to fold findings into the class registers rather than leave them as individual documents. Classified on the MECHANISM THIS DOCUMENT DESCRIBES (its body), not on its title: the registered classifier greps titles, and the titles have outgrown its vocabulary — which is why 92 findings sat `unclassed` while the six classes held 138 instances. The body carries 6 matches for `uncommitted_and_orphaned_work` against 1 for the runner-up, which is the threshold used; anything below it was left for a reader rather than graded from a sibling.*
