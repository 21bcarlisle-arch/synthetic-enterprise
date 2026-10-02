**Severity:** LATENT · **Lane:** W2_customer_generator (world side: `simulation/departure_risks.py`) · **Epoch:** 3 · **Atom:** `unminted`
**Evidence:** `docs/market_research/svt_rates_active_passive_2016_2025.md` §4a

# The end-of-fix spike is worth two to four exits a run, so it stays a named gap

**2026-10-02, autonomous worker, Lane 0 claim `size-the-end-of-fix-passive-roll-spike-gap`.**

## The question

§4a found that in the six weeks after a fix ends, Ofgem's 2019 End of Fixed Term trial control arm
switched externally at **6%**. C1b gives the same household about 2%. That gap is only worth a
mechanism if the world produces enough such rolls for it to matter.

## What a passive roll is here

A domestic household's fixed term ends and its next segment on the same account is the default
(`svt`), with no new contract. The count is per household, not per fuel leg, because C1b decides
on the decision leg once per household. There are two ways in:

- **Scheduled.** The schedule builders put the household on the default at term end. Every one of
  these has **no** renewal-point event at that boundary. In val_on, 101 of the 101 leg boundaries
  carry no `customer_events` row. C1b's first segment is the household's only exit there.
- **Declined.** The household stayed and refused a fix above the default
  (`departure_occasion == "declined_fix"`, `departure_rolled` True). This route had a renewal
  roll before the end date, so it matches the trial's population, which had not acted by then.

## Measured

Runs: `/var/tmp/decline-grade-822/{def,val}_on.json`, at 822218441 with `DECLINE_A_FIX_ABOVE_THE_DEFAULT`
on. That is still the current pin: 757c8cada, the switch itself, is the only `simulation/` commit
since. C1b over 42 days is `1-(1-p)^(42/segment_days)` on the first segment's
`realized_churn_probability`, which already includes propensity and the level anchor. "Scaled" multiplies the
6% by `market_switching_multiplier(y)/market_switching_multiplier(2019)`, the same re-referencing
C1b uses. Scaling matters here because there were no fixes to switch to in 2022 (0.20×).

| | default world | value arm |
|---|---|---|
| domestic households rolling fix → default | **105** (102 scheduled, 3 declined) | **84** (73 scheduled, 11 declined) |
| of which in 2017 (the opening book's first terms ending) | 41 | 47 |
| C1b expected exits, first 42 days | 1.86 (mean 1.8%) | 1.45 (mean 1.7%) |
| EFTC 6% flat | 6.30 → **+4.4** | 5.04 → **+3.6** |
| EFTC 6% × world switching multiplier | 4.70 → **+2.8** | 3.65 → **+2.2** |
| C1b first-segment exits actually rolled | 1 | 0 |
| accounts churned in the run | 78 | 72 |
| EFTC ~14% internal re-fix (no route in the world) | ≈15 | ≈12 |

In 2 default-world households (PROS-2016-0046 2017-02-11, PROS-2019-0240 2021-08-10) the default
segment is on a gas leg with no C1b row, because the decision leg is elsewhere. They are excluded.

## Disposition

**A named gap, not a mechanism.** The spike would add +2 to +4.5 exits per run. That is 3–6% of churned
accounts, spread over ten years, and smaller than one run's binomial noise on ~100 trials at 6%
(sd ≈ 2.3). A mechanism would also need numbers the trial does not give: how fast the spike decays,
and how it behaves outside a pre-cap March. Those would be invented to fill a slot. No constant
changes.

Two things to carry:

1. **The internal ~14% is the larger omission, and it is about margin, not exits.** In the six weeks
   after rolling, about 12–15 households per run would re-fix with the same supplier. The world has no
   route for that until the next SVT anniversary conversion, so these households sit on the default
   rate for up to a year. That flatters margin, because the default rate is above the fix they
   would have taken. This route already belongs to `decline_versus_leave_share`
   (`knowledge_map.md`) and is not re-filed here.
2. **The 2017 cluster.** Almost half of each run's rolls are the opening book's first terms ending
   in early 2017. If the spike is ever wired, the value it moves is concentrated in one year.

The value arm's −9 is unaffected, as the predecessor finding established: those nine are
long-tenure stock.
