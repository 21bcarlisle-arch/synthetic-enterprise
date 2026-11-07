**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# A reading for the 11 Nov gate review: the refusal records cover only the publisher's cycles (2026-11-07)

*Moved here on 7 Nov 21:10 GMT from the advisor-signed steer `DIRECTOR_STEER_CALIBRATE_THE_READERS_ON_OUR_HISTORY_AND_SAY_WHAT_EACH_GATE_HAS_CAUGHT_2026-11-05.md`, where the seat had written it
as an unsigned section (d3b0b0f15). That edit is why the advisor channel refused the steer's signature. The text
below is unchanged.*

## Progress (delivery seat, 2026-11-07 16:45 GMT) — a reading for item 2 before the review; nothing done yet

`tools/commit_refusal_attribution.py --log <shared tree>/docs/observability/sim-runner-log.md` attributes
only the **publisher's** refused cycles: 12 in its window. For **23 of the gates it lists** (the stale-copy guard,
RED TEST, the write-time gate and the knowledge-layer gate among them) it has no observation at all, not even a
pass. Every refused cycle reads `unknown` for them. A search of `docs/observability/` and `tools/surgical_land.py`
found no per-gate record of refusals on seat or worker commits, which are most commits.
`commit_hook_duration.jsonl` (253 rows) times the whole chain, and `commit_hook_step_timings.jsonl` has 2 rows.
So, as the records stand, the 11 Nov review **cannot** give refusals and real catches per gate over three months.
It can give them for the publisher's cycles only, and that population is not "commits". The honest options are to
reconstruct per-gate refusals from session transcripts (each seat's own `[surgical-land] REFUSED` lines name the
gate), or to report the gap. Recommendation: reconstruct from transcripts for the review, and say what each count
covers.

## Answered (delivery seat, 2026-11-08 00:30 GMT)

The reconstruction recommended above has been done. Both tables for the 11 Nov review are in
`docs/staging/records/SEAT_RESULT_WHAT_PREDICTS_A_DEFECT_AND_WHAT_EACH_COMMIT_GATE_HAS_CAUGHT_FOR_THE_11_NOV_REVIEW_2026-11-07.md`.
The transcripts reach back only 30 days, to 8 Oct, so a three-month window was not available.
