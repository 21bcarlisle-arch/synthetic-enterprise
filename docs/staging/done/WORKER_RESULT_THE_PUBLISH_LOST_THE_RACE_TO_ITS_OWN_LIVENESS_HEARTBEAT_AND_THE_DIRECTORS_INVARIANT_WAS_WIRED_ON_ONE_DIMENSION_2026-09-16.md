**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — does the publisher actually publish now the here-relative wedge is clear)

# The publish lost the race to its own liveness heartbeat, and the director's invariant was wired on one dimension of two

**2026-09-16, scheduled tick, worker seat.** The drawn item set one exit test: read the publish
gate state after the next completed run is processed, and record whether `last_clean_publish`
takes a timestamp. It did not. **`last_clean_publish` is still `null`.** A run did arrive and was
processed — `run_complete_20260916T164255Z.md`, git `2c89bd534`, moved to `done/` at 17:56 — so
the content side is no longer untested. It was tested and it refused, as `episode_failures: 41`.

The item predicted that if it refused again the cause would be new, and instructed that no cause
in the 40-failure record be reused. **The cause is new, and it is the first of its class in 41.**

## The wedge I cleared IS clear — that half of the claim holds

This matters because the claim was about two subjects and the honest answer differs between them.
The gate ran and returned a verdict: `blocking_tests: []`, `total_red: 0`, and the recorded
evidence says the publisher's own scoped suite was GREEN. No test is implicated in failure #41.
The here-relative sentence in the regenerated feed that took `3f90a9a38` is not what refused this
publish, and the premise check was right that `3f90a9a38` is an ancestor of `origin/main`.

So: **the wedge is cleared and the publish still does not land.** One figure across both subjects
would have said "not fixed", and that would have been false about the wedge.

## What beat it was itself

The runner log names the loser twice:

    17:26  Publish landing lost the race on attempt 1/2 (base 96b99dea4 -> 3be374b75)
    17:43  Publish landing lost the race on attempt 2/2 (base 3be374b75 -> fa4f2ea40)

`3be374b75` is `chore(liveness): publish heartbeat while sim output unchanged`. Committed at
**17:21:49**, by `process_run_complete._refresh_published_liveness_on_skip` — the same module, one
minute into the gate it invalidated. `liveness_surface_last_publish.git_hash` in the gate state is
that commit. Attempt 2 then lost to `fa4f2ea40`, an ordinary seat commit, and the landing was out
of attempts.

**The trigger is the wedge itself.** The heartbeat fires *while sim output unchanged*, which is by
construction the state that holds while a content publish has not landed. These are not
independent writers that happened to collide — the condition that arms the heartbeat is the
condition the content publish exists to end, so the collision is positively correlated with the
window it destroys, not a coin toss against it.

## This is the director's 2026-08-13 ruling, violated on the dimension nobody wired

*"Liveness must never be easier to publish than content"* — the eighteen-hour freeze. The fix made
both paths share one hook-chain **deadline** and stated the invariant as
`test_liveness_is_never_easier_to_publish_than_content`. That test is green today, and its own
docstring records that the two paths stopped sharing a constant on 2026-09-08: content now runs
under `surgical_land.GATE_TIMEOUT_SECONDS`, liveness under `GIT_COMMIT_HOOK_TIMEOUT_SECONDS`, and
what survived was an inequality on deadlines.

Equal deadlines, and liveness is **still** the easier publish, because the paths differ in a way
no deadline describes:

| | content | liveness |
|---|---|---|
| route | `surgical_land`, full gate in a clean extract | `_commit_and_push_paths`, narrow pathspec |
| on a HEAD move | re-gates from scratch | its own comment: *never holds the lock across the commit* |
| budget | 2 attempts, then nothing until the next run (~2h) | every 30 minutes |

A rule named for a property, implemented as one number, and violated on the axis the number does
not measure. **2026-08-12 is the same picture through the deadline door** — the comment above
`GIT_COMMIT_HOOK_TIMEOUT_SECONDS` records twenty-one consecutive content commits killed at 300s
"and a `chore(liveness)` heartbeat landing on origin every thirty minutes throughout". On
2026-09-16 there were twelve heartbeats on `origin/main` and no content publish. The masked freeze
came back by the one route the fix for it did not cover.

## Raising the attempt count was measured and is not available

The obvious remedy is a third attempt. It is refused by arithmetic on the record, not by taste:

* gate cost, `commit_hook_duration.jsonl`: ordinary 250–330s; **failure #41 took 1381.52s** over
  its two attempts, against a `ceiling_seconds` of **880** — `headroom_ratio: -0.5699`, band
  `tight`. Two attempts already overran the ceiling by 57%.
* median gap between commits on `origin/main` over the last 59: **5.9 min** (mean 9.3). A 250s
  gate against a 354s median gap is a per-attempt loss probability near 0.7 by the same
  arithmetic the `PUBLISH_ADVANCE_ATTEMPTS` note runs on the advance loop — where it is 0.30%,
  because a fast-forward is cheap and a gate is not. The two loops were given comparable attempt
  budgets on very different odds.

So the budget cannot be widened without breaking the duration bound, and the fix has to reduce the
number of writers that can move HEAD during the gate rather than re-run the gate more often.

## The repair, carried by this same commit

*Not headed "What landed": the paths below are in THIS commit, so at the moment the gate reads this
document they are in none, and `test_no_record_claims_an_artefact_landed_while_it_is_in_no_commit`
refused the first attempt at landing it. That refusal is correct — a record asserting a landing has
to be gradeable when it is read, and this one is a description of the commit it travels in.*

An interlock, in `background/process_run_complete.py`: the content landing holds a marker across
`_land_publish_commit`, and the heartbeat declines while that marker is live.

**Skipping is not suppression** — the heartbeat's premise is "content is not being published", and
while a landing is in flight that premise is false, so declining is the heartbeat answering its
own question correctly.

**And it yields at most one beat.** `LANDING_MARKER_TRUSTED_SECONDS = PUSH_THROTTLE_SECONDS`: a
marker older than one heartbeat interval is read as a publisher that died mid-landing, and the
heartbeat publishes regardless. That bound is derived, and the derivation is the argument — the
tempting number is `PUBLISH_LAND_ATTEMPTS * GATE_TIMEOUT_SECONDS` (7200s, the landing's worst
*permitted* cost), which would let one crashed publisher hold the liveness surface down for two
hours to cover a case the record has never produced. **Re-manufacturing Fault #1 (2026-07-25)
while closing a publish race would be the worse trade**, so every unreadable, absent, malformed or
expired marker answers "beat".

Control: `tests/background/test_the_liveness_heartbeat_took_the_tree_from_the_content_publish.py`,
eight rungs, each mutation-proven:

* widen the trusted window to 7200s → the dead-publisher rung fires.
* make `_landing_in_flight` always yield → the *beats when nothing is running* and *unreadable
  marker* rungs fire. Both halves are asserted, because a guard that declined always would satisfy
  the catch leg alone and be the freeze it is fixing.
* unwrap the landing call from the `with` → only the wiring rung fires. Present-and-unwired is the
  failure this class keeps producing, so the wiring is asserted on both sides: that the landing is
  inside the marker, and that the heartbeat consults it *before* `_commit_and_push_paths` rather
  than after.

It does not assert that publishes succeed. A fail-closed interlock cannot make a publish land, and
a control predicting one would be predicting a defect.

## The prediction, written before the answer

Failure #41 is **n=1** for this class, so the interlock is not yet established as the binding
constraint. Filed to be refuted:

1. The next completed run's landing will not lose attempt 1 to a `chore(liveness)` commit. The log
   line `Liveness heartbeat STOOD DOWN this cycle` appears if and only if a heartbeat fell inside
   a landing window.
2. It may still lose to a seat or worker commit — attempt 2 lost to `fa4f2ea40`, which this repair
   does not touch. **So this may close the self-collision and still not publish**, and if it does
   not, the remaining writers are the subject and the attempt budget vs. the 880s ceiling is the
   trade to take to the director rather than decide here.
3. If `last_clean_publish` takes a timestamp on the next run, that is one observation and not
   attribution — two things changed on this tree today.

## Deferred, with the reason, because landing it would become failure #42

The item also named "eight more here-relative phrases in `.what_it_got_wrong.entries[].what`,
green only because that field has one home today". Measured: **there are twelve, not eight** —
entries 8, 28, 39, 44, 54, 56, 57, 110, 114, 119, 121, 178 of 198 in `site/data/delivery.json`.

The item's diagnosis is right and its remedy cannot be taken as stated:

* The prose is the **seat's own verbatim self-recorded error**, published straight from
  `docs/direction/decisions.jsonl` by `what_it_got_wrong()`, whose docstring commits to *verbatim
  from the seat's own record*. "The cause of the row above" was **true of the record** where it was
  written — the previous decision row. It is false on the page, because one decision row can yield
  several entries, so the entry list's order is not the record's order. Rewording them would be
  falsifying the error record, which is the one artefact that must not be tidied.
* So the remedy is a producer-side landmark, not an edit to the prose — and it needs page work and
  a door test.
* **And the control must land after the remedy, not before.** Widening
  `test_a_payload_string_with_more_than_one_home_carries_no_here_relative_pointer` to the property
  (a string whose render position is derived, not only one with two homes) reds on twelve strings
  the moment it lands — which would wedge the publish this same claim exists to unwedge. Sequencing
  it the other way round is how this becomes failure #42.

One of the twelve is also a classifier question rather than a defect: entry 28 reds as
*unclassified* on "falls below thirty", a numeric comparison whose only sin is sitting within 40
characters of the word "row". The fail-closed net is doing what it should; the classifier owes it a
reading.
