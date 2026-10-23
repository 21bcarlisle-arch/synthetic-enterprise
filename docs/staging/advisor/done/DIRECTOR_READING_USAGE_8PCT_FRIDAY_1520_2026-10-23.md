**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-READING] Usage 8% at 15:20 on Friday, the second reading on the new tier (23 Oct 2026)

**Type:** usage reading, relayed by the advisor. The director's words, from chat on Fri 23 Oct:

- 15:20 BST: "8%. How is pace and progress?"

**Readings so far on the new tier:**
- 0% at 06:55.
- 4% at 09:45.
- 8% at 15:20.

The last interval is 4 points in 5 h 35 min, about 0.72 points an hour, half the morning's rate. Your 13:44 proposal put a point at about USD 7.9. Refit it on the 09:45–15:20 interval and report both values.

**The reset time is not known, and it decides the pace.** The plan change may have given the account a new weekly reset, possibly Friday morning rather than Monday 04:00 BST. The advisor has asked the director to read it from Settings › Usage.
- If the reset is **Monday 04:00**, 0.72 points an hour lands near 52% at the reset, far under the reserve line. You could run at about 1.4 points an hour until then.
- If the reset is **about a week from this morning**, 0.72 points an hour runs past 100% before it.
- **Until the advisor relays the reset time, hold about 0.7 points an hour.** It is safe either way. When the time arrives, set the pace that lands about 6 points short of that reset.

**Also relayed to the director at this reading:**
- your 13:44 correction: last week used about 42 old-tier points, so the cut needed is 1.3 to 1.7 times, not 4;
- the opening context per turn halved, from 21,517 to 10,721 tokens;
- connectors stripped from unattended spawns;
- the Sonnet 5.5 pilot pre-registered;
- the finding that 250 of 250 worker-tick doorbells were forced to Opus;
- your recommendation to stay on the new tier, raised for him.

The Explore feature-demo steer has not been drawn yet. It is due for Monday's publish, so draw it next. This morning's 4% reading file is also still undrawn. Its projection is superseded by this one.

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
