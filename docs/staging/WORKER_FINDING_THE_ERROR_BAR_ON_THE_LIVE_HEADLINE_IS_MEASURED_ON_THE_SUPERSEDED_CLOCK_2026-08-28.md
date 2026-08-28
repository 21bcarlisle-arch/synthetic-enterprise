# WORKER FINDING — the error bar beside the live headline is measured on the clock the run superseded

**Severity:** LATENT · **Lane:** G_data_learning

LATENT and not BLOCKING on purpose: the surface already discloses the mismatch in its own
`clock_caveat`, so no false claim reaches a reader and no lane needs to stop. What is owed is the
re-measurement and the missing control, not a correction.

**Filed** 2026-08-28, delivery-lane tick, after releasing
`rerun-the-three-arm-ab-and-restate-the-headline-on-the-realised-clock`.
**Rank:** after the current top item. Not a blocker — the page already declares the limitation
in its own words. This is the repair of a declared hole, not the discovery of a hidden one.

## The finding

`site/data/value_arms.json` publishes, live at `https://poesys.net/data/value_arms.json`:

- a headline built from the **restated** split — `selection_gbp` **−571.38**,
  `level_share_of_advantage` **1.1224**, clock `settled-realised`;
- an `error_bar` block — `stdev_gbp` **4,401.74**, `sem_gbp` **2,541.35**,
  `distinguishable_from_zero: false`, `spread_to_point_estimate_ratio` **25.2**.

Those two are **not on the same clock**. The error bar is read from
`docs/observability/value_cycle_ab_s1_noise_floor.json`, `generated_at`
**2026-08-27T23:32:17Z** — earlier than the clock repair, which landed in `4d935cb39` at
2026-08-28T01:37:55+01:00. Its nine passes were measured against the **settled-provisioned**
figures, i.e. beside the superseded panel whose point estimate was −174.57, not beside the
−571.38 the page now leads with.

`spread_to_point_estimate_ratio` 25.2 is the clearest instance: it is a ratio of a
provisioned-clock spread to a realised-clock point estimate. Neither leg is wrong on its own;
the ratio is the two clocks divided by each other.

## Why this is a finding and not an alarm

The generator already says so, unprompted, in `error_bar.clock_caveat`:

> "This noise floor carries no clock label of its own and its runs predate the 2026-08-28 clock
> repair, so it is paired with the superseded panel it was measured beside. Read it as the size
> of this instrument's seed sensitivity, not as an error bar on the restated figure --
> re-running it on the corrected clock is owed work."

That is the honest disclosure working exactly as intended — a reader is told, on the surface,
which figure the bar does and does not bound. So this is filed as **owed work already named by
the artefact**, not as a false claim reaching a reader. It is the same standard the last stretch
set when it published a visible hole rather than a number it knew was wrong.

## What done looks like

1. Re-run the noise floor on the landed (post-repair) code:
   `tools/run_value_cycle_ab.py` in its noise-floor mode, 3 seeds × 3 arms, so every pass reads
   `level_vs_selection` on `settled-realised`.
2. Assert the fresh artefact carries a **declared clock of its own** — `clock` is currently
   `null`, which is what let a provisioned measurement be rendered beside a realised headline
   without anything failing. A null clock on a figure that gets divided into a clocked one is
   the defect to close, not just the stale run.
3. Regenerate `site/data/value_arms.json`; `clock_caveat` should become unnecessary and be
   **removed rather than re-worded** — a caveat that outlives its cause is the next reader's
   confusion.
4. R11: fetch the live surface and quote the refreshed `stdev_gbp` and the ratio.
5. R12 in force: the restated spread may be **wider**, and the selection leg may sit even deeper
   inside it. If it does, that is the result. The point estimate is a diagnostic and the bar is
   not a target — do not re-seed until the ratio improves.

## R15 — the control this wants

The reason nothing caught this is that no control asserts **two figures rendered as a ratio share
a clock**. `clock_audit` checks net-margin readings within the A/B artefact; it does not reach
across into the noise-floor artefact the site pairs with it. The mutation that must fail a named
test: stamp the noise floor `settled-provisioned` (or leave it `null`) while the split says
`settled-realised`, regenerate the feed, and require the ratio to be **withheld with its reason**
rather than computed. That is the same "withheld rather than re-stamped" rule
`generate_value_arms_data.py` already applies to the panels — it simply was never extended to
the error bar.

## Evidence

- `docs/observability/value_cycle_ab_s1_noise_floor.json` — `generated_at 2026-08-27T23:32:17Z`,
  keys carry no `clock`.
- `git show -s --format=%cI 4d935cb39` → `2026-08-28T01:37:55+01:00` (the clock repair).
- Live fetch `https://poesys.net/data/value_arms.json` → HTTP 200,
  `realised.split.selection_gbp = -571.3757980000228`, `error_bar.clock = null`,
  `error_bar.spread_to_point_estimate_ratio = 25.21505564300187`.
