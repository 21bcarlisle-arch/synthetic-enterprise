**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PRE-REGISTRATION — what moves when `load_whole_run_rss_curve` stops anchoring on one child

**Filed:** 2026-09-22, BEFORE the edit and before any regeneration. Claim
`confirm-the-producer-runs-at-1250-without-an-episode-and-anchor-the-published-ceiling-on-the-cgroup`.

## The change being pre-registered

`simulation/premise_population.load_whole_run_rss_curve` returns
`anchor_peak_rss_mb = 5507.4`, which is `ru_maxrss` of the ONE child
`tools/settlement_ceiling_probe.py` spawns. Production runs that child under the
`sim_runner.py` daemon, and both the kernel and `resource_headroom.admit()` count the pair.
The correction is an additive offset on the anchor only.

## State read before the edit (so the deltas are attributable)

```
curve.anchor_customer_years          1197.0          (probe point 1, clean)
curve.anchor_peak_rss_mb             5507.4  MB      child ru_maxrss
curve.mb_per_customer_year           4.3402115
weight_drift("sim_run").observed_peak_mb   5734.4 MB   systemd MemoryPeak, cgroup, 8 runs
sample()["total_mb"]                 24032.1 MB
budget = total_mb x 0.25             6008.025 MB
settled_book_ceiling_customer_years  1312            <- published today
SETTLEMENT_CUSTOMER_YEAR_BUDGET      1250.0
```

## Predictions, written down before the answers are known

1. **The published ceiling becomes 1,260**, not the 1,263 the 2026-09-22 result doc quotes.
   The doc anchored the arithmetic at the *budget* 1,200; the curve anchors at the probe's own
   *committed* 1,197.0, which is the honest x because it is what the run actually did. The 3.0
   customer-year difference is 13.0 MB of y and I expect it to show up exactly there.
2. **`mb_per_customer_year` does NOT move.** A constant parent offset cancels in a difference of
   two peaks. If the slope moves, the offset has been applied to the wrong term and the edit is
   wrong. This is the leg I most expect to catch a mistake.
3. **`test_the_settlement_ceiling_does_not_outrun_the_measured_memory_curve` stays GREEN**, with
   its margin falling from 62.3 to 10.0 customer-years. It is green today only because it
   hand-carries `CGROUP_PEAK_MB_AT_THE_ANCHOR = 5734.4` — the correction, copied into the test
   because the loader did not have it. **After this edit that literal is a second home for a
   quantity that now has one, so it is deleted and read off the curve.** If deleting it reds the
   test, the loader and the test disagree about the anchor and I want to see that rather than
   keep two numbers agreeing by hand.
4. **`memory_slack_multiple_over_the_budget` in `site/data/value_arms.json` falls from 1.0498 to
   ~1.008.** The published ceiling stops exceeding the 6,008.0 MB budget it was derived to
   respect; the 4.7% disagreement with the constant becomes 0.8%, still with the constant on the
   conservative side.
5. **No other consumer of the curve reds.** `tests/simulation/test_premise_population.py` asserts
   the slope and `anchor_customer_years`, neither of which moves, and never asserts
   `anchor_peak_rss_mb`. I am not confident about consumers outside these two files and expect
   the gate to be the instrument that tells me.

## The one I cannot settle in this turn, stated so it is not later claimed

Clause (1) of the drawn item — *observe a producer cycle at 1,250.0* — **cannot be observed
today** and I predicted nothing about it before looking, because looking was the task. What I
found is recorded as a finding rather than a prediction: the shared tree `sim-runner.service`
executes from is diverged from `origin/main` and still carries `1200.0`.
