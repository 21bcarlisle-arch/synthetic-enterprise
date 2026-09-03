# WORKER FINDING — the error bar beside the live headline is measured on the clock the run superseded

**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** `SITE13_the_baseline_comparison_carries_its_bound`

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

---

## UPDATE 2026-08-28 (delivery seat) — it is worse than a clock, and item 3 no longer applies

Three things changed after this was filed, and the finding is stronger, not weaker.

**1. The mismatch is now a different WORLD, not only a different clock.** The three-arm run was
re-taken at 2026-08-28T10:47:24Z against a market that can DEFEND (`5f50408c6`, 08:25). The noise
floor is still 2026-08-27T23:32:17Z, from a market that could not react. A seed spread measured
where nothing responds is not a confidence interval on a figure measured where it does — and unlike
the clock, that is not a labelling problem that a basis note can settle.

**2. The point estimate has left the band.** `selection_gbp` moved to **−5,223.56** against a
measured band of **−3,705.27 to +5,075.85**. The sentence the surface rendered — *"the point
estimate sits inside that band and so does zero"* — became **false**. It was a fixed string
asserting a relationship the generator never checked, and
`tests/tools/test_generate_value_arms_data.py` caught it by reddening on its own `stdev >
|selection|` assertion, whose message said the rendered sentence must be re-read rather than kept.

**3. Both are now DERIVED rather than written down** (`039f202ce`). `error_bar.staleness_caveat`
is computed by comparing the two artefacts' own `generated_at` stamps, so it will keep firing for
the next world change instead of naming this one; `error_bar.point_estimate_inside_the_measured_band`
drives which reading renders. Both are on `/capabilities/` and mutation-proven — delete the render
and `site/test_the_baseline_comparison_reaches_the_reader.py::test_an_error_bar_older_than_its_figure_says_so_on_the_page`
reds.

**Item 3 of "what done looks like" is superseded.** It said the caveat should be *removed rather
than re-worded* once the noise floor is re-run. That is right for the CLOCK caveat and wrong as a
general rule: the staleness caveat must not be removable by hand at all, because it is derived —
it disappears by itself when the two runs are contemporaneous, and re-appears without anyone
noticing when they are not. A caveat that a person can delete is the defect this finding is about.

**Items 1, 2, 4 and 5 stand and are still owed.** The re-run now costs more than when this was
filed: 3 seeds × 3 arms on the full window, and a full three-arm pass is ~35 minutes as measured
today, so ~105 minutes of wall clock. It is the next long-running job after the chase-off
counterfactual (`WORKER_PREREGISTRATION_WHAT_THE_CHASE_OFF_RUN_MUST_SHOW_2026-08-28`), and it must
run AFTER it — re-measuring the noise floor before knowing whether the chase moves the book would
spend 105 minutes on a spread for a world that is about to be explained.
