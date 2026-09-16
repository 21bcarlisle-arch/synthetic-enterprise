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

---

## DISCHARGED 2026-09-16, scheduled tick, worker seat

Both legs built, both mutation-proven, in
`tests/background/test_the_publish_verdict_asks_reachability_and_not_equality.py` (13 controls,
each shown red under its own mutation).

**Leg one.** `_push_reached_origin` now asks reachability against the sha `ls-remote` returns.
Equality is kept only as the first leg, because a commit is an ancestor of itself and the ordinary
fast-forward should not pay for a subprocess. Measured on the live instance: with `origin/main` at
`c9c4339b8`, the old predicate grades `05add41ab` `push_did_not_reach_origin` and the new one
grades it reached. The 2026-07-24 guard is unchanged and proven unchanged — on a phantom rc=0
against an origin standing still at an older commit, ours is not an ancestor of it, the verdict is
still False and the throttle is still untouched.

**Leg two.** On a push rejected non-fast-forward where `_publish_surface_collisions() == []`, the
publisher now runs `origin_reconcile` and re-takes the verdict against a FRESH `ls-remote`. The
recovery is deliberately OUTSIDE the tree lock: `advance_shared_tree` takes the same flock, and
flock is per open-file-description, so a second acquisition from this process would block against
itself. `test_neither_leg_alone_would_have_recorded_the_clean_publish` replays the real sequence
and shows ancestry answering False at the instant of the push — which is what makes the timing a
second defect rather than a restatement of the first.

**The second reader.** `publish_freshness.last_published_ts` was our own stamp, written only when
the publisher graded its own push True — so `describe()` told the brief *"figures reached origin
159.8h ago"* five hours after `05add41ab` put them there. It now also asks git when `CONTENT_PATHS`
last moved in a commit `origin/main` has, and takes the newer of the two: each source can only MISS
a publish, never invent one. Measured after the change: `content publishing: live -- figures
reached origin 5.0h ago`. The 2026-08-21 guard is re-asserted and still holds — a fresh stamp over
frozen figures still reads `stale`, because `snapshot` takes the OLDER of its two clocks.

**No value was hand-written.** `.publish_gate_state.json` still reads `last_clean_publish: null`
and will until the next publish the publisher grades correctly for itself, which is the point.

### The blocking red this ran into, and what it was

Every commit in the tree was being refused by
`test_the_deadline_has_headroom_over_what_THIS_MACHINE_actually_costs_today`, and it was the same
class of defect one door along. `GIT_COMMIT_HOOK_TIMEOUT_SECONDS` (880s) is the `timeout=` on ONE
`git commit`. Since 2026-09-08 the content path lands through `surgical_land.land(attempts=
PUBLISH_LAND_ATTEMPTS)`, which that constant does not bound and which RE-GATES on a lost
compare-and-swap — the race is detected after the gate has returned a verdict, so a lost attempt
ran a full chain. `2c89bd534` recorded 1381.52s that way and the publisher's own failure record
names it: *"the surgical landing lost the race to another writer on all 2 attempt(s)"*. The control
read that as one chain and demanded 1727s of a deadline that
`test_the_deadline_leaves_room_for_the_publish_path_after_the_gate` caps at 900s. **The
intersection of the two controls was empty**, and no deadline existed that could satisfy both.

Repaired at the READER, with no schema change, because the row already carries the contradiction: a
bounded chain that exceeds its deadline is KILLED and recorded `outcome: timeout`, so a row that
exceeded `ceiling_seconds` and still returned a verdict proves from its own fields that it was not
produced under that ceiling. `_recent_hook_chain_seconds` drops exactly those rows and keeps
everything else, so the control loses no teeth: a genuine kill is still graded, a slow chain under
its ceiling is still graded and still reds at 1.25x, and a window with nothing gradeable in it
skips rather than passes. A multi-chain row whose total fits under the ceiling is kept and
over-reported, which is the conservative direction for a headroom control.

### Left standing, deliberately

`tests/background/test_suite_duration_watch.py::test_the_cadence_is_read_from_a_measurement_not_an_aspiration`
is red at HEAD — `PUBLISH_CADENCE_SECONDS` is 1500s against a measured 5403s median marker
inter-arrival, so run cadence has slowed ~3.6x since that constant was calibrated on 2026-08-26.
It is a live-measurement red in a different lane and re-deriving that constant is a judgement about
what the run cadence now is, not a repair to this one. It is NOT in this commit's test selection.
An earlier draft of this repair added a `chains` field to `suite_duration_watch.record`, which
would have pulled that red into this commit for no gain over the reader-side fix; the draft was
reverted rather than carried.
