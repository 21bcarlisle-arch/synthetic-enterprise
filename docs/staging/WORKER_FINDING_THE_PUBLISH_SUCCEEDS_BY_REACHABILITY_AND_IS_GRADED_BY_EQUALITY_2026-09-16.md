**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the publisher has never recorded a clean publish in this episode)

# The publish now succeeds by reachability and is still graded by equality, so a disjoint publish-while-behind can never record a clean publish

**2026-09-16, scheduled tick, worker seat.** A publish commit reached `origin/main` today
(`05add41ab`, confirmed by `git merge-base --is-ancestor`) and the publisher recorded it as
`push_did_not_reach_origin`. `episode_clean_publishes` is still 0 and `last_clean_publish` is still
null, six days into a wedge that is, in fact, over.

## The two halves of the publish path now disagree

`770497ddd` widened the **commit** gate. `_publish_surface_collisions` established that `ahead > 0`
is a state and not a collision: a publish commit whose paths are disjoint from what origin is
bringing may be created, because *"`origin_reconcile` absorbs it on the next cadence"*. That
sentence is the mechanism's own, and it is correct — the reconciler did exactly that today.

The **push** verdict was not widened with it:

    def _push_reached_origin(push_rc, remote_head, local_head) -> bool:
        return push_rc == 0 and bool(remote_head) and remote_head == local_head

Equality with origin. A publish created *while behind* cannot make `remote_head == local_head` —
origin is ahead by construction, that is what "behind" means. So the exact case the commit gate was
widened to admit is the case the push verdict refuses **every time, structurally**, no matter what
happens on the remote.

The widening admits a commit into a state whose success the next predicate cannot express.

## Why equality is there, and why it is the wrong shape rather than a wrong value

It is not arbitrary. The 2026-07-24 incident: a bare `git push` returned rc=0 while origin did not
advance — a phantom "Everything up-to-date" — and the caller recorded a push time anyway, so
`_push_due()` stayed False and every real push deferred behind a success that never happened, for
3.5 hours. Equality against `ls-remote`'s ground truth killed that, and the docstring says so.

Equality was a correct **proxy** for the property while every publish was a fast-forward. Once a
publish may legally be created behind origin, the proxy and the property come apart. The property
was always *"the publish commit reached origin"*; equality only ever coincided with it.

This is `CLAUDE.md`'s own rule — *key a control to the property, not to today's answer* — and the
failure direction is the diagnostic one: it goes red when the system becomes more capable.

## The honest predicate, and what it does NOT cost

Reachability: **is this publish commit an ancestor of `origin/main`?** Tested against the sha
`ls-remote` returns, so the evidence is still the real remote and not the local tracking ref.

It does not weaken the anti-phantom guard. On a phantom rc=0 with origin standing still at an older
commit, our commit is *not* an ancestor of it, so the verdict is still False and the throttle is
still left untouched. The guard keeps its whole strength on the case it was written for, and stops
refusing the case it was never about.

## But reachability alone would not have flipped the counter today, and that is the second half

Measured, not assumed. At the instant the publisher pushed, `05add41ab` was **not** on origin — the
reconciler carried it there several minutes later, after the publisher had exited. An ancestry test
evaluated at that instant would also have returned False.

So the finding has two legs and both are needed:

1. **The predicate is the wrong shape** (equality where the property is reachability).
2. **The verdict is taken too early.** The publisher declares its outcome before the mechanism its
   own narrowing names — `origin_reconcile` — has run. A publish designed to be absorbed on the
   next cadence is graded before that cadence.

The smallest thing that closes both: on a push rejected non-fast-forward where the fork is
*disjoint* (`_publish_surface_collisions() == []`, already computed on that path), run the
reconciler, then re-verify by ancestry against a fresh `ls-remote`. Today that would have recorded a
clean publish, because that is the sequence that actually happened — just with the grading done by
hand afterwards instead of by the publisher.

## Why it is filed rather than built

Not size alone: it is a change to the success criterion of the publish path, and it must arrive with
a control that can fail. The mutation is available and cheap — grade the disjoint-publish-while-
behind scenario under both predicates and require them to disagree — but a half-gated edit to this
particular path is how this episode reached 39 failures. It is the next turn's first item, and it
is specified above closely enough to start from.

**Do not read `episode_clean_publishes: 0` as evidence the surface is dark.** It is not: origin
carries the run and `docs/status/LATEST.md` is stamped 2026-09-16T13:28:42Z. The counter is
measuring the publisher's opinion of its own push, and on this class of publish that opinion is
wrong by construction.
