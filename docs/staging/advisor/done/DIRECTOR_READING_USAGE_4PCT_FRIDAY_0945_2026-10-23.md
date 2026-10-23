**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-READING] Usage 4% at 09:45 on Friday, the first reading on the new tier (23 Oct 2026)

**Type:** usage reading, relayed by the advisor. The director's words, from chat on Fri 23 Oct:

- 09:45 BST: "4%"

**The first data point for the recalibration.** `DIRECTOR_READING_PLAN_TIER_LOWERED_USAGE_0PCT_2026-10-23.md` asked for this fit:
- 0% at 06:55 BST.
- 4% at 09:45 BST.
- So 4 points in 2 h 50 min, about 1.4 points an hour.

**Fit USD per point now.** Use the weighted spend between 06:55 and 09:45 BST (`tools/tick_burn_rate.py weighted_usd_between`). Record it beside the old tier's about USD 26.5 a point. One interval is a thin fit, so carry it as a provisional figure with its band until the next reading.

**Projection.** At 1.4 points an hour, the 66 hours to the assumed Monday 04:00 BST reset would add about 93 points. That lands near 97%, about 3 points over the 94% reserve line, so the morning ran slightly hot. The morning also carried a heavy site load: the front-door, other-pages and Explore steers.
- **Hold width roughly where it is.** Don't widen.
- **Aim to land at about 94% at the reset.** That works out at about 1.35 points an hour on average.
- **Re-project at the next reading.** The director will be asked for one this evening.
- **Spend the time well.** If the site work finishes and the rate falls, use the room on the best feature work. Don't save it (R1).

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
