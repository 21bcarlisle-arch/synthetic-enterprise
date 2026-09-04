**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# The fixture pin was never the blocker, and the alarm text had half the guards the state file had

Filed 2026-09-04 by the delivery seat, closing the piece
`SEAT_FINDING_A_ZERO_START_TIME_RENDERED_AS_AN_ESTABLISHED_1970_EPISODE_ON_THE_DIRECTORS_OWN_SURFACE_2026-09-04.md`
left open, and **correcting that finding's own account of what stood in the way.** Both the
correction and the thing it corrects are kept, because a prediction filed after the answer is not a
prediction.

## What was asked, and what was actually true

The direction named one repair — `record_publish_gate_failure` adopts a persisted `wedge_since`
with the same `isinstance`-accepts-0 shape the renderer had just had fixed — and named one cost:
`tests/background/test_publish_gate_blocking_payload.py::
test_the_state_the_supervisor_draw_reads_carries_the_blocking_test` pins
`persisted["wedge_since"] == 0.0`, so *"this is not a free repair"*. Its recommendation was to
change the fixture rather than the semantics, and it said explicitly that whoever took it should
**test that recommendation rather than assume it**.

Pre-registered before any measurement, with what would refute each prediction:
`docs/staging/records/PREREG_WHETHER_THE_FIXTURE_PIN_IS_ACTUALLY_THE_BLOCKER_ON_THE_ZERO_ADOPTION_2026-09-04.md`.

**The recommendation was aimed at the wrong obstacle.** Applying the adoption repair alone and
printing the value:

    persisted wedge_since = 0.0

The named control stayed **green**. The fixture pin was never load-bearing, because the repair it
was supposed to block was a no-op. `_write_publish_gate_state` runs every write through
`episode_monotonic.guard_episode`, where an episode start is a **LOW-water** field — and
`0.0 <= anything`, so the guard wrote the zero straight back on every honest restamp, forever.
A persisted zero was not merely accepted; it was *unbeatable*.

The control that actually reddened was the sibling from the same finding —
`test_a_persisted_zero_does_not_reach_the_alarm_text` — because its fixture drove the writer at
`now=1800`, and an honest restamp of a fake clock renders an honest `1970-01-01T00:30`. **A
fixture's clock has to be a possible clock**, which is the same defect as the pinned `0.0` one
file over, in the file written to complain about it.

## The repair: two changes, each dead without the other

1. **`background/process_run_complete.py`** — `_is_episode_start()`, one definition of "an instant
   an episode could have started at", called by the adoption clause. Positive, and not a `bool`.
2. **`background/episode_monotonic.py`** — `_is_start_to_remember()`, screening the **prior** side
   of a `since_field`. Asymmetric on purpose: of the proposal the guard asks *can I order this?*
   (a call-site property, and a misdeclared field must still raise); of the prior it asks *is there
   a start here to remember?*, and an instant at or before the epoch answers no. Screening at the
   prior rather than inside `_episode_key` keeps `_refuse` firing on genuine type errors alone, so
   this cannot raise inside the failure path of the pipeline it monitors.
3. `episode_age_seconds` takes the same screen, so the centralised reader answers "no start
   recorded" instead of "500,000 hours".

Printed across the whole partition at real inputs before the tests were written:

| persisted `wedge_since` | persisted after a failure at `now` |
|---|---|
| `0.0` | `now` (restamped) |
| `-1.0` | `now` (restamped) |
| `None` | `now` (cold start) |
| `now - 7h` | `now - 7h` — **remembered** |

## What mutation found that no reasoning did

Seven mutations, each a revert or a tautology. Six fired. **One survived, and it was a missing test
rather than an equivalence** — established rather than assumed, because the flattering reading was
available and wrong.

Replacing the writer's entire adoption clause with `wedge_since = now` left all ten new legs green.
The persisted field is guarded **twice** — the writer's screen and the monotonic guard — so the
state file was still correct. But `_episode_phrase` is handed the writer's **local** variable, not
the guarded persisted one, so the alarm the director reads said:

    CURRENT:  EPISODE: wedged since 2027-01-15T01:00 UTC -- 7h00m and 4 consecutive failures
    MUTATED:  EPISODE: wedged since 2027-01-15T08:00 UTC -- 0h00m and 4 consecutive failures

**That is the 2026-08-09 defect verbatim** — a 10h26m outage paging as 14 minutes — the exact
failure the whole `episode_monotonic` module exists to cure, live on the NTFY path, and no control
in this repository could see it. The state file was protected twice and the sentence a person acts
on was protected once. `test_the_alarm_text_reports_the_open_episodes_real_age_not_a_fresh_one` is
that leg; it asserts what is **sent**, where the others assert what is **written**, and they are
different values read from different variables.

## Still open, named rather than left for the reader

`background/supervisor.py::_publish_gate_wedge_active` (~L3791) reads `wedge_since` and
`alerted_at` with its own hand-rolled `isinstance(v, (int, float))` and takes `min()` over them
together with the raw failure timestamps. A zero there dates the wedge to 1970 — always older than
any threshold — so the RUNG-1 draw fires permanently. **Not fixed here, and the reason is that
fixing the two state keys would not fix it**: the `failures[].ts` entries feed the same `min()` and
carry no screen at all, so this is a different subject (a failure timestamp, not an episode start)
and deserves its own measurement rather than a clause smuggled in beside this one. It is now
unreachable from the writer — no zero can persist — but a legacy state file on disk still reaches
it, which is what makes it worth writing down instead of closing silently.

## The tooling gap this turn reproduced on itself, and it is the parent finding's own class

The parent finding added `site/data/director_reserved.json` to
`tests/production_surface_guard.PROTECTED_FILES` — the *sink* level of its three-level fix. While
measuring the partition table above I drove `record_publish_gate_failure` from ad-hoc
`python3 - <<EOF` probes rather than from pytest, and **evicted the director's live one-way-door
escalation from that exact file**, replacing it with a fixture's alarm carrying the `0h00m` phrase
from a mutation.

The guard did not fire, and could not: it is a pytest fixture, so it protects the surface from
TESTS and not from anything else that imports the writer in the same tree. That is a fail-open on
the same sink the parent finding had just closed, found by walking into it. Restored explicitly
from `HEAD` (`git show HEAD:<path> > <path>`; `git checkout <path>` is banned here and I used it
once by reflex earlier in this turn, which silently reverted a completed edit to
`episode_monotonic.py` — the ban is well earned).

**Filed as its own subject, not fixed here**, because the honest fix is at the writer
(`action_needed._mirror_reserved_to_site` refusing to write a live surface when its own state is
fixture-shaped) and that is a design question, not a clause.
