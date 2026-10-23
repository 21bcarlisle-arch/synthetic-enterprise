**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-READING] The weekly reset is Monday 03:00 UK time, so spend this window (2026-10-23)

**Type:** pacing fact, relayed by the advisor. The director's words, from chat on Fri 23 Oct, answering the reset-time question in `DIRECTOR_READING_USAGE_8PCT_FRIDAY_1520_2026-10-23.md`:

- 15:31 BST: "It's still Monday 03:00"

## The reset

- **The time.** The weekly reset is Monday 03:00 UK time, not the 04:00 BST you assumed. UK clocks go back on Sunday 25 Oct, so this coming reset is **Mon 26 Oct 03:00 GMT (03:00 UTC)**, and the same time each Monday after that. Correct the reset constant in `tools/tick_burn_rate.py` and in every projection that uses it.
- **This window.** From 15:31 BST Friday to the reset is about 60.5 hours. 8% is spent. Landing about 6 points short of the reset leaves about 86 points, which is **about 1.4 points an hour**: twice the rate since 09:45.

## What to do

1. **Speed up to about 1.4 points an hour now, through to the reset.** This replaces the "hold about 0.7" line in the 15:20 reading file. Spend it on the best work, in the priority order (P1, R1):
   - the Explore feature-demo steer, which is still undrawn and due for Monday's publish;
   - the rest of the site steers;
   - Monday's publish itself;
   - the Sonnet 5.5 pilot and the cost levers, because the pilot needs volume to grade;
   - the payment-engine sequence.
2. **From the reset, pace each week to land about 6 points short of the next Monday 03:00.** At your fitted cost of about USD 7.9 a point, a full week is about 88 points, or about 0.52 points an hour on average. Re-project at each relayed reading.
3. **Keep the fit going.** Use the 06:55, 09:45 and 15:20 BST readings and the next one. Report USD per point with its band in the stretch log.

— Advisor, relaying the director's reading on the director's standing delegation of 15 Oct.

## Done

**The fit (seat executor, 23 Oct 17:0xZ, `tools.tick_burn_rate.weighted_usd_between`, every transcript and subagent).** Readings are whole percentages, so each interval carries ±1 point.

| Interval (BST) | Points | Weighted USD | USD per point | Band |
|---|---|---|---|---|
| 06:55–09:45 (the 13:44 value) | 4 | 31.5 | **7.9** | 6.3–10.5 |
| 09:45–15:20 (refit) | 4 | 50.8 | **12.7** | 10.2–16.9 |
| 06:55–15:20 pooled | 8 | 82.2 | **10.3** | 9.1–11.7 |

The afternoon point cost about 60% more priced USD than the morning one. The two bands only just overlap. I cannot yet say whether that is rounding, a mix shift the meter weights differently from list price, or something else; the next reading will separate them. Until then, carry the pooled 10.3 (9.1–11.7), not 7.9. At 10.3 a full week to 94% is about USD 970, not the 88 points × 7.9 ≈ USD 695 the reset file assumed. The 15:20 reading is now in `POINT_READINGS`, so `usd_per_point()` returns the refit.

**The pace.** The 15:31 reset reading arrived before this was drawn, so the "hold about 0.7" line is superseded: about 1.4 points an hour to Mon 26 Oct 03:00 GMT. The dial has no setting between words and `normal` is its fastest, so I set `python3 -m background.tick_mode normal --until 2026-10-26T03:00Z --then normal` (16:58Z, logged in `~/.cache/synthetic-enterprise/tick_mode_history.jsonl`). **To reverse:** `python3 -m background.tick_mode slow --until 2026-10-26T03:00Z` (or `normal` with no `--until`). The weekly 0.52 points an hour from the reset onwards needs the next reading before it can be set.

**The reset constant.** There is no allowance-reset constant in `tools/tick_burn_rate.py` or anywhere else in `background/` or `tools/`. The Monday 04:00 figures in `sim_runner` and `process_run_complete` are the publish window, not the allowance, so nothing was corrected there.
