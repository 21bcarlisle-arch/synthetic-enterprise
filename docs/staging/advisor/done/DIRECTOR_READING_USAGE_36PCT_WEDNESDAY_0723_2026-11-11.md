**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-READING] Usage at 36% on Wed 11 Nov, 07:23 GMT: about a day short at this burn

**Type:** READING, through the advisor channel. The director's words, from chat:

- Wed 11 Nov, 07:23 GMT: "36% used. Is it doing. Productive work? What progress, what next? Who is the balance between clearing backlogs, fixing the harness and feature build for sim and for supplier?"

## The reading

- Plan usage was **36%** at Wednesday 07:23 GMT, 52.4 hours after the Monday 03:00 reset. That is about **0.69 points an hour** [derived].
- At that rate the remaining 64 points run out around **Sun 15 Nov, 04:00**, about a day before the Mon 16 Nov 03:00 reset [derived]. The rate that lasts the week is about **0.55 points an hour** [derived].
- Trim about a fifth. Do not trim correctness or the publish path. Cheaper targets:
  - The model-comparison arms are done: Fable 5.2 used 2.4x the tokens and the advisor arm 1.85x the cost, for the same result. Run no more arms this week unless the director asks.
  - Fewer full books in parallel. One at a time, each pre-registered.
- Re-read at the next director reading. If the burn is still over 0.65, say what was cut.

## His question about balance

He asked how the work divides between backlog and correctness, harness, and feature build for the world and for the supplier. The advisor is answering him in chat with origin's last 18 hours, and will relay his decision. No action is asked here beyond the trim.

## Done

Actioned on 11 Nov by the worker tick, on the two cuts the reading names. It did not use a dial, because
`tick_mode slow` would also slow correctness and the publish path, which the reading excludes.

- **No more model-comparison arms this week.** I checked every machine flag that runs one, and all
  are closed: `advisor_trial.yaml` is disabled, `executor_tier_pilot.yaml` ended 6 Nov, and
  `model_tier_pilot.yaml` ended 19 Aug. `model_tier.advisor_trial()` and `_executor_pilot_window()`
  both return None. The cut is recorded in `DIRECTION.yaml` `not_now`, so that no session starts a
  hand-run arm. It lifts at Mon 16 Nov 03:00Z or when he asks.
- **One full book at a time, each pre-registered.** This is the same `not_now` row. The seat's focus
  item 3 already says "Do not launch a second book while it is armed".
- **Re-read.** At his next reading, if the burn is still over 0.65 points an hour, say what was cut.
  The new weekly balance review now reads the usage curve every Friday (see the 11 Nov ruling's Done).

To reverse: delete that `not_now` row.
