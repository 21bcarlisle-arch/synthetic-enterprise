# [WORKER FINDING] The channel carried what went wrong and nothing of what got done

**Severity:** RECORDED (fixed in the same turn) · **Lane:** H_harness · **Epoch:** 3
**Atom:** unminted — the notification model (`background/notify.py`, G-N2/G-N3)
**Found:** 2026-09-01, on the director's console instruction: *"the channel under-reports you. Eight
commits this evening produced no message, while divergence and publishing alarms filled the mirror.
I've read that as a stall twice today when you were working normally. Real work should reach the
channel and routine noise shouldn't crowd it out."*

## Class registration

Belongs to `no_caller_and_never_runs` — the SILENCE half is a declared routing class with no
producer for three weeks. The NOISE half belongs to `alarm_identity_is_the_declared_key`.

## Measured first, from the outbound mirror and the digest queue

| 2026-09-01 | |
|---|---:|
| outbound messages | **64** |
| …one tree-divergence condition | **27** (42%) |
| …publishing | 20 |
| commits landed | **19** |
| **landing notifications, instant or batched** | **0** |

Digest queue over its whole life: 718 finding announcements, 693 divergence, 358 drift,
**1 routine landing** — and that one is a health check's `director_echo`.

Evening only (17:00+): ten outbound messages — three divergence, three publishing, two echoes of his
own message, one digest, one instruction-queued. **None of the fourteen landings.** His reading is
not an impression; working normally and being stuck were byte-identical from his phone.

## SILENCE — `routine_landing` had no producer, and the KINDS set is why

`routine_landing` is one of the four deferrable categories *he named himself* on 2026-08-12. It has
never had a producer. Not batched-and-delayed: never sent.

The reason it could not have one is upstream of any caller. `notify.KINDS` was a closed set of four
— `real_alarm | digest | director_echo | test_fixture` — every member of which is a thing that went
wrong, a batch of things that went wrong, a reply, or a fixture. **There was no kind meaning "the
machine finished a piece of work."** A landing had to masquerade as an alarm or not be sent, and it
was not sent.

Masquerading would not have worked either: an unkeyed `real_alarm` auto-keys on its own message with
numbers normalised away (G-N4), so two landings with similar subjects would dedup each other and the
second would vanish. Work done is never a repeat of other work done.

**Fixed:** a fifth kind, `work_done`, with its own tag so he can tell "I did something" from
"something is wrong" at a glance; and `tools.surgical_land.announce_landing`, at the one door — bypass
is a wall, so every landing this project makes passes through `land()`. Batched, per his own
instruction, because a landing is not action-needed.

## NOISE — a transition state that contained a clock

`_publish_tree_divergence` passed `top_squatters(m)` as its transition `state`. That string carries
`oldest_age_hours`. So one unchanging condition — the same file, ageing 92.6h → 110.4h across the day
— was a **new state on every publish cycle**. Transition-only (G-N1/R5) was fully engaged and had
nothing to compare, because no two firings were ever equal. 27 pages of one squat.

Worse than the volume: `alarm_repetition`'s escalation — the mechanism that turns a nagging alarm
into a DRAWN WORK ITEM and then stops re-telling him — counts repeats of an *unchanged* state. **A
state that never repeats never escalates.** The one condition that most deserved to become work was
structurally the one condition unable to.

The author's intent was already right and stated at the call site: *"keying state on the lane table
rather than the raw counts means the generated-file churn that moves the total every cycle does not
re-page."* The implementation then used a function containing both a clock and the counts.

**Fixed:** `tree_divergence.divergence_state` — the state is the lane set and nothing else. A lane
starting or finishing pages at once; a standing squat is named daily by `re_escalate_after` and
becomes a work item after three repeats. Every number stays in the message, none in the identity.

## CROWDING — the digest elided the work before it existed

`compose()` rendered classes in `sorted()` order and spent a 25-line budget greedily in that order.
`routine_landing` sorts LAST of the four, behind divergence, drift and finding_announcement. With 42
findings and 13 drift notices queued against 25 lines, **every landing would have been elided in
full even once it had a producer** — a digest of everything filed and nothing finished.

**Fixed:** what was DONE leads, and every class gets a floor of the budget before any class takes
more. Same discipline as a population floor on a scanning control: guarantee the small population is
represented, then let volume have the remainder. Verified at the real numbers — all 8 landings
shown, every class represented, elision still named.

## One more, created and closed in the same change

`send_ntfy` has had a hard pytest guard since the director's phone spammed with test pages. The
DEFERRAL path reaches neither it nor the guard. Harmless until landings became notifications —
`tests/tools/test_surgical_land.py` lands real commits into fixture repos, dozens per run, and every
one would have appended a `[LANDED]` row to the live queue and ridden the next real digest to his
phone. The same ledger would then have been cited back as evidence of what the machine had done,
which is `feedback_telemetry_a_test_can_write_is_not_telemetry` exactly.

**Fixed:** a structural guard in `defer()`, both directions testable (an unredirected queue under
pytest is a no-op; a monkeypatched one exercises the real body), and its test lives in
`tests/tools/` because `tests/background/conftest.py` pins the queue for its whole directory and the
guard would be unreachable from there.

## What this finding does not claim

Not that the batching design is wrong — it is his own instruction and it works; the digest flushed
on schedule tonight. Not that the divergence alarm should be quieter in general: the magnitude
escalation added 2026-08-26 is correct and stays. The claim is that **the channel's taxonomy had a
slot for work done and no kind that could fill it, and its loudest sender was loud for a reason that
had nothing to do with the condition being worse.**
