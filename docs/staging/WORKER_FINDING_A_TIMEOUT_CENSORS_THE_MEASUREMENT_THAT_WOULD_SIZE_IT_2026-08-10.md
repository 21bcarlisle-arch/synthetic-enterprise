# [WORKER-FINDING] A timeout censors the very measurement that would size it — 28 kills in 3 days read as a tidy distribution (2026-08-10)

**Severity:** LATENT · **Lane:** H_harness

**Found:** fixing today's tick decapitation (director-flagged: "three ticks were killed by
TimeoutStartSec mid-work"). The instance is fixed. The **class** is that the number you would
naturally reach for is manufactured by the defect.

## Observed, with evidence

`worker-tick.service` carried `TimeoutStartSec=1800`. Its own journal, three days to 2026-08-10:

```
timeout kills: 28
wall-clock:    n=31   min 5.0min   median 30.0min   p90 30.0min   max 30.0min
               29 of 31 invocations over 25 min
```

**Median == p90 == max == exactly the bound.** That is not a distribution with a fat tail; it is a
**right-censored** one. Every invocation that wanted longer was truncated to the bound and then
recorded as though 30 minutes were its duration.

## Why this is a class, not an instance

The obvious repair — "raise it a bit above the observed maximum" — sets the new bound from a number
**the old bound produced**. The observed max *is* the defect, so anything derived from it inherits
it. This is the same shape as `feedback_never_pin_generated_values_in_controls` and the
`as_of`-population artefact: a statistic computed under the constraint cannot be used to size the
constraint.

Worse, the censored series looks *healthier* than the truth. A reader of "median 30 min" concludes
the bound is generously sized with room to spare, when in fact ≥28 runs hit the wall. The failure is
invisible in exactly the summary a monitor would publish.

The kill was never costless: systemd tears down the whole cgroup, so it also killed Agent forks with
uncommitted work — the 2026-08-03 incident that produced 8 "RESCUE" branches and 2,566 stranded
lines is this same mechanism. An undersized bound here destroys BUILT WORK, so the error directions
are not symmetric.

## What was done

`TimeoutStartSec` 1800 → **7200**, in `background/worker-tick.service` (IaC source) and reconciled
to `~/.config/systemd/user/` with `daemon-reload`; effective value confirmed `2h`. This is set
deliberately far above any plausible honest tick **to uncensor the measurement**, and the unit now
says so in its own comments — it is an over-estimate, documented as one, not a fitted value dressed
up as calibrated.

## Proposed atom (queued, not built — SELF_INTERRUPT_DISCIPLINE)

**`OPS_rederive_tick_timeout`** — once ≥2 weeks of uncensored ticks exist, re-derive the bound from
the real distribution at a stated percentile, and add the generalisable guard: **any duration/size
series whose max clusters on a configured limit must be reported as CENSORED, never summarised as
if the limit were the data.** R15: the guard must fire on the 31-sample series above and stay quiet
on a genuinely uncensored one.

**Recommendation:** normal priority, after the headroom governor (`MEMORY_CLEANSE` step 2) — the two
interact, since 6.4GB tick memory peaks against a 15.9GB box are part of why ticks ran long.
