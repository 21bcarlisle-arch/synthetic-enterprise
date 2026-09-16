**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Class:** publish_gate_and_wedge · **Atom:** (Lane 0 delivery — `publish-gate-last-clean-publish-survives-an-episode-close`)

# Pre-registration: which controls move when `last_clean_publish` takes the stamp on BOTH exits

**Filed 2026-09-16, delivery seat, BEFORE running anything.** The change is one line in
`record_publish_gate_success`. The thing I do not know is *which controls it makes red*, and that
is exactly the number a turn is tempted to report after it has seen it.

The finding this discharges:
`docs/staging/done/SEAT_FINDING_LAST_CLEAN_PUBLISH_IS_CLEARED_AT_THE_INSTANT_IT_BECOMES_TRUE_SO_A_RECOVERED_PUBLISHER_IS_INDISTINGUISHABLE_FROM_A_PLACEHOLDER_2026-09-16.md`

## The change

`background/process_run_complete.py`, `record_publish_gate_success`:

```python
"last_clean_publish": None if episode_closed else stamp   ->   "last_clean_publish": stamp
```

`episode_clean_publishes` keeps resetting to 0 on close. It is a counter and episode-scoped by
name; the timestamp is not, and does not accumulate.

## What is asserted from the code and needs no measurement

**A1 — the alarm sentence cannot change.** `_episode_phrase` enters its intermittent-wedge branch
on `isinstance(clean_publishes, int) and clean_publishes > 0` and reads `last_clean_publish` only
*inside* that branch. `episode_clean_publishes` still resets on close, so no reading with
`clean_publishes == 0` can render the timestamp. Refuted by: any change to
`test_the_alarm_stops_calling_a_broken_streak_consecutive`,
`test_a_genuinely_unbroken_outage_still_reads_as_one`, or
`test_an_unrecorded_publish_time_is_declared_not_guessed`.

**A2 — a stale timestamp can never be rendered as a publish inside the wrong episode.** The
counter and the timestamp are written by the SAME statement, so `clean_publishes > 0` implies the
timestamp is that episode's own publish. The cross-episode carry is therefore invisible to the
only renderer. Refuted by: finding a reader of `last_clean_publish` that does not first gate on
`episode_clean_publishes`. Searched: the field is read in `_episode_phrase`'s caller
(`record_publish_gate_failure`, which passes both together) and nowhere else in `background/`,
`tools/`, `site/` or `saas/` — every other hit is prose.

## The prediction whose answer I do not have

**P1 — exactly ONE assertion in the whole suite goes red**, and it is
`tests/background/test_an_episode_held_open_by_its_queue_is_not_an_unbroken_outage.py
::test_draining_the_queue_to_zero_closes_the_episode_and_forgets_the_publishes`, on its final line
`assert st["last_clean_publish"] is None`.

*Refuted by*: any second red in `tests/background/`, or a red in
`tests/background/test_the_liveness_surfaces_refusals_left_only_an_orphaned_log_line.py`
(whose `test_a_liveness_publish_is_not_recorded_as_a_CONTENT_publish` also asserts
`last_clean_publish is None` — I claim it never reaches the content-success path, so it is
untouched), or a red anywhere else that names this field.

**P2 — the `if not episode_closed` carry in `_write_publish_gate_state` stays load-bearing and is
NOT deleted by this change.** The success path now proposes a stamp on every exit, so the carry no
longer serves the success path — but it still serves every FAILURE write, which proposes `None`
and must keep the prior. *Refuted by*: deleting the `not episode_closed` condition from the carry
leaves `test_the_next_failure_cannot_forget_the_publish_that_happened` green.

## What the replacement control must be, so the fix is not unprovable

The moved assertion cannot simply be flipped to `is not None` and left there — that is a control
keyed to today's answer. It is replaced by the property the finding is about:

**a cleanly closed episode must be DISTINGUISHABLE from a publisher that has never run.** The
comparison subject is the real tracked placeholder's bytes (`{"alerted_at": null,
"failures": []}`), read through `_read_publish_gate_state`, not a hand-written dict.

And the null control the old assertion was carrying stays, on the field it actually belongs to:
`episode_clean_publishes == 0` after a close, plus a partition assertion that a record which has
only ever seen failures still reads `last_clean_publish is None` — so "always non-null" is not a
way to pass.

## Done means

1. `record_publish_gate_success` writes `stamp` on both exits.
2. The old assertion is replaced by the distinguishability control above, and that control is
   mutation-proven red against the one-line revert — proven by running it, not asserted.
3. `episode_clean_publishes` still resets; the alarm sentence is byte-identical (A1).
4. Landed and bound.

---

# RESULT, written beside the predictions and not over them

## P1 — **CONFIRMED.** Exactly one assertion went red, and it is the one named.

```
FAILED ...::test_draining_the_queue_to_zero_closes_the_episode_and_forgets_the_publishes
E       assert st["last_clean_publish"] is None
E       assert 1800021600.0 is None
1 failed, 80 passed        # the four files named above
1 failed, 583 passed, 1 skipped    # tests/background/ (fail-fast, stopped at the same one)
```

`test_a_liveness_publish_is_not_recorded_as_a_CONTENT_publish` stayed green, as claimed: it never
reaches the content-success path.

## P2 — **CONFIRMED, both halves, and the second half changed the remedy.**

Measured by two mutations rather than argued:

| mutation | result |
|---|---|
| delete the `last_clean_publish` carry from `_write_publish_gate_state` entirely | `test_the_next_failure_cannot_forget_the_publish_that_happened` RED — the carry is still load-bearing for every failure write |
| delete only `not episode_closed and` from that carry | **9 passed** — the condition is now an equivalence, not a missing test |

**The condition is kept anyway, and the reason is the direction it fails in**, which the
pre-registration did not think through and the measurement forced: without it, a future writer
that proposes `None` on a close gets the PRIOR episode's stamp carried silently into the new
record — the field would read non-null with no publish having written it. That is this field's
fail-open direction, and it would blunt the new control into passing on manufactured evidence.
With the condition, the same mistake writes `null` and the control fires. The invariant bought:
**`last_clean_publish` only ever holds an instant a real publish stamped.** The comment that said
"only an evidenced episode close clears it" — now false — is replaced by this.

## A1, A2 — held. No alarm-sentence control moved, at any point, under any of the five mutations run.

## The control I first wrote was one that could not fail, and the mutation caught it in one run

`test_a_closed_episode_is_distinguishable_from_a_publisher_that_never_ran` was first written as
*do the two records differ at all*, over the union of their fields. **It was green with the defect
installed** — the two records differ on `red_at_head_reason` regardless, because the success path
rewrites it. Differing is not the property; differing **on the evidence that a publish happened**
is. Narrowed to `{last_clean_publish, episode_clean_publishes}`, it reds:

```
E  AssertionError: a recorded publisher and one that has NEVER RUN carry the same evidence of
   publishing — which is none.
E  assert set()
```

Recorded here rather than quietly narrowed, because the green version looked exactly as
convincing as the red one. This is the R15 catalogue's fail-open shape reached through a new door:
a control whose subject is a SUPERSET of the property it is named for.

## What landed

- `background/process_run_complete.py` — `last_clean_publish` takes `stamp` on both exits; the
  carry's comment corrected to state the invariant above.
- `tests/background/test_an_episode_held_open_by_its_queue_is_not_an_unbroken_outage.py` — the old
  assertion's null-control duty split onto the two fields it was conflating: the counter keeps its
  reset control (renamed `..._forgets_the_COUNT`), and the timestamp gets the partition it never
  had — survives a close, AND stays absent when nothing ever published. Both mutation-proven.
