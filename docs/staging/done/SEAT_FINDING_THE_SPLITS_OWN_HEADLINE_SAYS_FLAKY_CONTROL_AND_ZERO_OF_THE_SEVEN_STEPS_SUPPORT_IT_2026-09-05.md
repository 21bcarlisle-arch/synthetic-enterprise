**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** measurements_that_mirror

# The split's own headline says "flaky control", and zero of the seven steps support it

Fifth and final turn on the Lane 0 direction *"split the RED TEST bucket by failing node id"*.
Full measurement: `docs/observability/commit_refused_attribution_2026-09-05.md`, section
*RED TEST, split by WHICH test*. Instrument: `tools/commit_refusal_attribution.py`
(`red_test_report` / `red_test_tally`), re-derived with
`python3 -m tools.commit_refusal_attribution --log <shared tree>/docs/observability/sim-runner-log.md`
— **not** from a clean tree, where the committed log was truncated to 2026-07-17 on 2026-08-31 and
the module refuses with exit 2 rather than printing a comfortable zero.

## What the direction asked, and the answer

`RED TEST` names the *gate*. An established re-arrival of it was two findings wearing one label:
one control re-breaking (a contended or flaky test, go and find it) or different tests in turn
(arrival traffic from other lanes, no control at fault). Opposite remedies.

17 established re-arrival steps across 5 episodes; 15 splittable. **SAME TEST 7 (46.7%)**,
SHARED 4, DIFFERENT 4, FIRST RED 2.

**And the headline is the wrong answer.** An identical node-id set demonstrates a *re*-break only
where the gate was observed to pass between the pair; without that observation the cheaper
explanation is persistence — one standing red the publisher retries into on its own rhythm. **Zero
of the seven SAME TEST steps carry the between-observation.** All three steps that do carry it are
DIFFERENT (2) or SHARED (1). There is no case in this log of one control demonstrably re-breaking
after passing, and the subject analysis corroborates it from the other direction: 47 of 59
same-gate `RED TEST` pairs are the *same* complaint.

## The finding is not the answer — it is that the answer was published behind its own refutation

The measurement was built, run and written up correctly. What it *published* was a table whose
loudest row said the opposite of its conclusion, with the correction four lines below in prose.
Anyone quoting `SAME TEST 7 (46.7%)` — a future mechanism-builder, a doorbell, a summary of this
lane — would have carried away "a flaky control, go and find it" from evidence that says the
hunt has no supporting case. Three steps is the entire strong-observation sample, and this
project's own rule is that a figure published without the bound it earned is worse than no figure.

This is the recurring shape, not a new one: [78% of re-refusals are the identical
complaint](SEAT_FINDING_78_PERCENT_OF_RE_REFUSALS_ARE_THE_IDENTICAL_COMPLAINT_AND_ONE_RED_WAS_RETRIED_24_TIMES_2026-09-05.md)
and [the firing order conceals re-arrivals rather than faking
them](SEAT_FINDING_THE_FIRING_ORDER_CONCEALS_RE_ARRIVALS_RATHER_THAN_FAKING_THEM_AND_82_PERCENT_OF_THE_COST_IS_A_GATE_THAT_RE_BROKE_2026-09-05.md)
both turn on a count that means nothing until you say what it counts. Here the count was right and
its *reading* was unbounded.

## What was done about it

`red_test_tally` now returns `same_test_rebroke` and `same_test_persisted` alongside
`counts[SAME TEST]`, and `main()` prints them **on the row** — `7  46.7% of splittable  SAME TEST
[0 demonstrably re-broke, 7 persistence]`. The published table gained the same column, named for
the *observation* (`gate observed to PASS between the pair`) rather than for the conclusion,
because the conclusion differs by row: on SAME TEST its absence demotes a re-break to persistence,
on DIFFERENT TESTS its presence is what makes the step arrival traffic.

Keyed to the property, not to today's zero: the day a re-break is demonstrated the row reports it
as one. Control: `test_the_same_test_count_never_travels_without_the_two_halves_that_invert_it`,
one assertion over a partition carrying both a persistence step and a demonstrated re-break.
Mutation-proven **both** directions — `same_test_rebroke = len(same)` (fail-open, every identical
set a re-break) and `same_test_persisted = len(same)` (fail-closed) each fire it, where a
single-branch assertion would survive one of them.

## What this does NOT establish, and no pre-registration was written

There is no pre-registration for this turn and there should not be: the measurement had already
run and landed before this turn opened, so anything filed now would be a prediction written after
its answer, which this project does not count as one. The four earlier turns on this direction each
carry theirs in `docs/staging/records/`.

Three steps does not license a rate, a threshold or a mechanism. What it establishes is a
*direction*: the evidence for the flaky-control reading is not weak, it is **absent**, and a
mechanism built to hunt a re-breaking control would have been built to find something no
observation here supports. The pre-registered action on the re-arrival finding was deliberately
NOTHING, and it stays nothing — but now for a reason that has been measured rather than deferred.

## What follows

The remaining question is whether the cost is the **retry-into-a-standing-red** behaviour rather
than the redness itself. That is a question about the publisher's retry rhythm and not about any
test, and it is the one this direction hands on.
