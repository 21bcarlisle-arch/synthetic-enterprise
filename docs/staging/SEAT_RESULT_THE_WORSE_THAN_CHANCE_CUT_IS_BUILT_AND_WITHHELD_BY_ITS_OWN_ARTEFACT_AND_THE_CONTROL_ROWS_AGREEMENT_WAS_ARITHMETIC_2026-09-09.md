**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the-worse-than-chance-cut-must-reach-the-reader-beside-the-cannot-tell-one) · **Class:** figures_on_a_superseded_clock

# RESULT — the worse-than-chance cut is built and withheld by its own artefact, and the control row's agreement was arithmetic published as a second opinion

The drawn item asked for four things. Three were already landed before this tick and I checked each
against the code rather than against the doorbell. The fourth — the one nobody had built — is landed
here. What stops a reader meeting the number is not the generator, the page or the control: it is the
**artefact the page reads**, and clearing that needs a run that is now in flight.

---

## What the item asked for, against what is at HEAD

| the item's ask | state | evidence |
|---|---|---|
| `method_skill` carries all four legs, each with own n, own permutation interval, own p | **built** | `_horizon_leg_published` (`tools/generate_value_arms_data.py:1836`) — no interval on a leg's own points, no number from that leg |
| the estimand NAMED as the estimand | **built** | `_skill_fixed_horizon` promotes `every_priced_decision_pounds_outcome` to the block's headline and withholds the whole block if it has no bound of its own |
| the page's prose states the estimand's reading rather than leading with the leg that cannot tell | **built** | `verdict()` in `site/capabilities/index.html`; controlled by `test_the_page_tells_WORSE_THAN_CHANCE_apart_from_WE_CANNOT_TELL` over the whole three-state partition |
| a reader-door control going red when the page says `cannot_tell` while a leg reads below its own null | **built** | same control, plus the poison round in the test above it, which strips a leg's interval and asserts the page refuses the bare number |
| record that leg 0's null and `method_skill.null_spread` agree because they are **one computation twice** | **NOT built — landed in this tick** | below |

## The piece that was missing, and why it is the same class as the rest

The bridge's first row is labelled *"the figure above, rebuilt here as a control"*, and on the 09-09
run its interval is `[0.44939285714285715, 0.5503571428571429]` — identical to `method_skill.null_spread`
to the last bit. It is the same permutation: 20,000 draws, seed 20260828, the same 168 decisions,
performed twice. A reader meeting two identical intervals a few hundred pixels apart counts two
samples agreeing. The agreement is guaranteed by construction and is evidence of nothing but that the
two code paths meet.

`_control_leg_agreement` derives it from the run's own fields rather than asserting it, so the block
is keyed to the property and not to today's answer, over three states:

* **one computation, intervals identical** — every run so far. Not corroboration, and the page says so.
* **one computation, intervals DIFFER** — same seed, same draws, same n, two answers. A defect in one
  of the two code paths, reported as one and not softened into a caveat about sample size.
* **independently permuted** — the seeds, draws or populations differ, so the agreement is a real
  check and the page stops calling it arithmetic. Nobody edits the file for that to happen.

Control: `site/test_the_control_rows_AGREEMENT_is_not_published_as_corroboration` (in
`site/test_the_baseline_comparison_reaches_the_reader.py`), driving **both** producers end to end and
all three branches, plus the styling — amber for the two states that qualify the table, muted for the
one where agreement means something.

One harness repair fell out of it: `_fixed_horizon_feed` passed `{"fixed_horizon": produced}` where
production passes the whole `method_skill` block. Every control over the legs was blind to the
survivor cut beside them, in the harness only. It now passes what `_method_skill` passes.

## Why the number still does not reach a reader, and it is not the code

`THREE_ARM_PATH` is the 09-08b run (`2026-09-08T21:01:30Z`). **None of its legs carry a `null_spread`** —
the leg permutation landed after it. So `_horizon_leg_published` withholds the estimand, correctly, and
the whole `fixed_horizon` block goes out as a refusal. The run that has the bounds is
`value_cycle_ab_s1_three_arm_20260909.json` (`01:24:34Z`, same world `39a192ce04c1eda8`):

> `0.4210` on 161 decisions across 88 accounts, against `[0.4458, 0.5540]`, `p = 0.0045`,
> `inside_the_null: false` — **worse than chance**, the ranking real and INVERTED.

I generated the feed from it to a scratch path to measure the promotion rather than argue about it.
It publishes exactly what the item asks. **It also costs the headline its direction**, and that is why
this tick did not promote:

| | 09-08b (published) | 09-09 (measured, not landed) |
|---|---|---|
| estimand | withheld — no interval of its own | `0.4210`, bounded, `p=0.0045`, reading rendered |
| `error_bar.staleness_caveat` | `None` | fires — floor `2026-09-08T23:29:22Z` is **older** than the point estimate `2026-09-09T01:24:34Z` |
| `contrast_bounds` | available, 3 seeds | **unavailable** — "no contrast on this page can have its direction stated until the noise floor is re-run" |
| headline | states £17,453 clearing ±£1,457, and £324 INSIDE ±£2,292 | states the staleness caveat and no direction at all |

`_staleness_caveat` is right and must not be weakened: it compares two stamps, and the same weakening
was tried and reverted on 2026-09-08 when it republished a headline 7.6x larger with no error bar.
Promoting the arms alone trades one honest refusal for another. The pair moves together or not at all.

## What is in flight

`longjob-arms-rerun-20260909b` — `tools.run_arms_rerun --stamp 20260909b --leg floor-all`, the
undecomposed floor, seeds 11111/22222/33333, `--redraw-mode all`: the same measurement as the floor it
replaces, launched at `2026-09-09T07:02:12Z` into a cgroup of its own with a liveness record. Its
artefact will be stamped **after** `01:24:34Z`, which is the one thing the promotion needs.

**The next tick's work, and it is one commit:** when
`docs/observability/value_cycle_ab_s1_noise_floor_20260909b.json` exists and carries world
`39a192ce04c1eda8` — check it, do not assume it — promote the **pair**: `20260909.json` onto
`value_cycle_ab_s1_three_arm.json` and `..._noise_floor_20260909b.json` onto
`value_cycle_ab_s1_noise_floor.json`, in ONE commit, then regenerate the feed and run
`site/test_the_baseline_comparison_reaches_the_reader.py`. Moving either alone is the defect the pair
exists to prevent, in both directions.

Do not re-derive any of the first four rows of the table at the top. They are at HEAD.
