**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Class:** publish_gate_and_wedge · **Atom:** (Lane 0 delivery — the publisher has never recorded a clean publish in this episode)

# RESULT — the episode close cleared the evidence a publish ever happened, and the repair is landed

**Turn:** scheduled worker tick, 2026-09-16 ~10:00–10:40Z. HEAD at start `4187c7d9a`; HEAD at
write time `2ec310fd8`.

## The drawn premise was spent, and in three separate ways

The item cited four commits and asked me to take `background/process_run_complete.py` to a
recorded clean publish "now that HEAD and origin are level at c2d8ac167". Measured at draw time
rather than assumed:

1. **HEAD was not at that commit and the trees were not level.** HEAD was `4187c7d9a`, origin
   `5a63cb3a3`, two behind. `behind_origin` — the cause the item said "cannot fire" — was live.
2. **The hypothesised cause was not the live one.** The item predicted the refusal would be the
   `cannot lock ref 'HEAD'` commit race already recorded once in `liveness_surface_refusal`. That
   field reads `null`. The live cause was one red test:
   `tests/background/test_an_exit_code_is_not_a_landing.py::test_the_channel_reads_the_SHARED_trees_log_not_the_importing_trees`.
3. **That red was already cured on origin** by `8997932d2`, which the previous seat turn
   diagnosed, repaired and mutation-proved. Verified independently here, not taken on the commit
   message: a clean `origin/main` extract runs that file **31 passed**.

So the steer's subject was wrong for the third stretch running, and each time for a different
reason. The wedge has not persisted — it has MOVED, three times, and each steer named where it
had just been.

## The exit test as drawn is unsatisfiable, and this is a property of the code

The item set, and explicitly refused to soften, `episode_clean_publishes != 0`. A prior seat
pre-registered this as unsatisfiable before the answer was known
(`SEAT_PREREG_WHAT_THE_IN_FLIGHT_PUBLISH_CYCLE_WRITES_AND_WHETHER_THE_DONE_CONDITION_CAN_EVER_READ_MET_2026-09-16.md`).
I re-derived it from the code rather than adopting it:

    episode_clean = 0 if episode_closed else (prev_clean + 1)

`episode_closed` is `pending_run_complete_markers() == 0`. So the field is non-zero **only while
the queue has not drained** — i.e. only for a publisher that publishes but cannot keep up, which
`_episode_phrase` itself calls a THROUGHPUT fault. A fully recovered publisher that drains the
queue reads `episode_clean_publishes: 0`.

**The exit test is satisfiable only by a partially-broken publisher.** It is keyed to today's
answer rather than to the property — the shape CLAUDE.md names — and waiting for it is what
burned the previous two stretches.

## What was actually wrong, and is now repaired

`last_clean_publish` was set to `None` on the episode-close branch, and its carry-forward in
`_write_publish_gate_state` was gated on `not episode_closed`. So **at the instant the claim
"this publisher has published cleanly" became most true — the cycle that drains the queue and
ends a 150-hour wedge — the field recording it was erased.**

A closed episode read `failures: []`, `alerted_at: null`, `last_clean_publish: null`. That is
byte-for-byte what a publisher which has never run once reads, and byte-for-byte what a fresh
worktree reads off the two-month-old tracked placeholder. **A recovered publisher and a never-run
one were indistinguishable**, and only the absence of failures said otherwise — which is exactly
what the placeholder also asserts.

Two fields had been merged into one reset, answering different questions:

| field | question | on a close |
|---|---|---|
| `episode_clean_publishes` | how many passes INSIDE this episode | resets — correct, unchanged |
| `last_clean_publish` | when did this publisher last publish cleanly, EVER | **now survives** |

Its own comment already called it "a LATEST-wins timestamp", which is precisely what an
episode-scoped reset is not.

**This was landed BEFORE the next cycle deliberately.** The marker
`run_complete_20260916T085959Z.md` is still pending and the gate is green at HEAD, so the next
cycle should publish and drain it — and without this repair, the first clean publish in 150 hours
would have recorded nothing.

## Mutation-proven, and one mutation did NOT fire

Run against the 82 tests over these two fields, each mutation applied and reverted:

| mutation | result |
|---|---|
| restore `None if episode_closed else stamp` in `record_publish_gate_success` | **1 failed** — fires |
| restore the `not episode_closed and` gate on the `last_clean_publish` carry | **8 passed — DID NOT FIRE** |
| gate `_episode_phrase`'s intermittent branch on `last_clean_publish` too | **1 failed** — fires |
| none | 8 passed / 82 passed |

**The surviving mutation is an established EQUIVALENCE, not a missing test**, and establishing
which was required rather than optional. Reaching that clause needs a caller passing
`episode_closed=True` while proposing `None`; in production `record_publish_gate_success` is the
only path that passes `episode_closed=True` at all, and it now always proposes a float. The gate
was removed anyway — for meaning, not behaviour: leaving it would go on asserting the field is
episode-scoped, the misreading the defect was made of. **It is recorded in both the code and the
test header as an equivalence so that "two mechanisms guard this field" cannot survive a review.**
The flattering reading was available and is false.

The third mutation is the **null control** for the carve-out. The old assertion's stated reason —
a field that only ever accumulates would make every later episode read as intermittent — is real
and was not dismissed. What makes keeping the timestamp safe is that `_episode_phrase` gates the
intermittent branch on `clean_publishes > 0` ALONE and only renders `last_clean_publish` inside
it. That is a property of the phrase, not of the state write, so it is now asserted by
`test_a_surviving_publish_time_does_not_make_the_next_episode_read_as_intermittent` rather than
argued in a comment.

## PRE-REGISTRATION — the cycle in flight while this was written

**Written 10:33Z, before the outcome was known and before any state file was re-read.** A publish
cycle (pid 2859982, started 11:25:32 local / 10:25Z) is live on
`run_complete_20260916T085959Z.md` — the same marker — and is inside its gate now. I am waiting
for it rather than landing underneath it: a commit created now could take HEAD out from under its
own commit step, which is the `cannot lock ref 'HEAD': is at X but expected Y` shape the drawn item
itself named. Its gate builds a `/var/tmp/publish-gate-head-*` extract from HEAD, so my
uncommitted repair is NOT in what it is testing.

**PREDICT it publishes.** The one named blocking test is green at HEAD, HEAD is a descendant of
the commit that cured it, and `behind_origin` is the only other recently-live cause.

**PREDICT, if it publishes, that it drains the marker to `pending == 0`, the episode CLOSES, and
the state therefore reads `episode_failures: 0`, `failures: []`, `wedge_since: null`,
`episode_clean_publishes: 0` and `last_clean_publish: null`** — because HEAD does not yet carry
this repair. That is the counter-intuitive leg and the one worth being wrong about: **the cycle
that ends a 150-hour wedge leaves no positive record that it happened.** If that is what the file
says, the defect this commit repairs will have been observed live, once, on the exact cycle it was
predicted for — rather than argued from the source.

**If instead it fails again**, `episode_failures` goes to 37 and the record names a new
`git_hash`, and the repair below is still correct but its motivating event will not have been
observed. The finding filed beside this one (the red measured before the advance that cures it)
predicts this is the more likely branch while the tree keeps moving under each cycle.

**Either way this commit's content does not change** — it is keyed to the property, not to this
cycle's answer.

### RESULT — appended after measuring, beside the prediction and not instead of it

*(To be completed by this turn if the cycle resolves inside it; left explicitly open otherwise so
the next reader can see the prediction was filed first.)*

## What I did NOT do

I did not chase `episode_clean_publishes` into being non-zero to satisfy the literal exit test.
That field is episode-scoped by name and design, and bending it would be keying the code to
today's answer — the same defect one level up. The honest replacement for the exit test is in the
prereg and I endorse it: **the publisher has recovered when `last_clean_publish` is non-null**,
which is now a reading a close cannot erase.

I also measured, but did not repair, an ordering defect that is the live cause of failure #36 —
filed separately as
WORKER_FINDING_THE_PUBLISH_GATE_MEASURES_ITS_RED_BEFORE_THE_ADVANCE_THAT_CURES_IT_AND_RECORDS_A_FAILURE_ABOUT_A_TREE_IT_HAS_LEFT_2026-09-16.md.
