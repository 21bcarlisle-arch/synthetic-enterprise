**Severity:** BLOCKING · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** `SITE13_the_baseline_comparison_carries_its_bound` — Lane 0 delivery

*BLOCKING because a published figure stated a direction it had not earned — the ruling's first
clause, and grading it LATENT to keep the lane open is the anti-pattern `finding_severity` names
in its own docstring. REPAIRED in the commit that files this, which is the release condition the
same clause gives; the residual it does not close is named at the end.*

# The two AUC nulls state a resolved direction from the one run the page says cannot name its world

**Class:** `figures_on_a_superseded_clock` (primary), `controls_that_cannot_fail` (secondary)
**Filed:** 2026-09-04, delivery seat, Lane 0, claim
`selection-leg-carries-its-live-world-floor`
**Subject:** `tools/generate_value_arms_data.py::_auc_null` and its two call sites
(`_method_skill.churn_auc_null`, `_auc_attribution.null_bound`), and the sentence
`_auc_reading` composes from the second of them.

## What the reader sees today

`site/capabilities/index.html` renders, in `var(--amber)` — the colour that page reserves for
"the figure actually clears its own null":

> The arm's own belief that a renewal would survive the price it chose scored **0.655** on the
> usual rank measure. Measured on 32 departures and 88 retentions — 120 decisions on 120
> accounts. A signal carrying no information at all scores between 0.38 and 0.62 on a population
> this size (exact null, two-sided 95%). **The observed value is OUTSIDE it and above the null
> (two-sided p 0.009), so on this population the belief carried real information about who stays.**

That is a RESOLVED DIRECTION, in the flattering direction, about whether the company knows
anything. It is computed entirely from the three-arm run — and `world_provenance`, on the same
page, names that run in `runs_that_cannot_name_their_world`:

```
"runs_that_cannot_name_their_world": [
  "the noise floor (2026-08-31T07:05:53Z)",
  "the three-arm run (2026-08-31T03:47:57Z)"
]
```

…under a headline whose first sentence is *"no contrast below may have its direction read as
resolved."* The page contradicts itself, and it is the same contradiction `_seed_spreads`
documents in its own docstring one block over.

## Why this survived the walk that was meant to catch it

The 2026-09-04 pass walked the direction's second clause — *"no bound on that page is
unstamped"* — and repaired four blocks: `contrast_bounds`, `error_bar`, all three
`current_world` legs, and `_svt_drift_belief` (whose comment records the walk by name). It
missed these two because they are not seed spreads: an AUC null is a *combinatorial* interval,
a function of 88 retained and 32 departed and of nothing else, so it reads as world-invariant
and it is — **but the comparison is not**. The observed 0.655 is a statement about how much
churn signal exists at a particular departure level, and the departure level is exactly what
moved. `world_provenance` puts the size of that move on the same page: +19.06pp of whole-book
expected departure, against published bands 0.5–3.6pp wide.

So the guard cannot be keyed to "is this bound derived from a floor". It has to be keyed to
"does this block read a DIRECTION off a run whose world is unknown".

## The asymmetry, kept

`_svt_drift_belief` already settled how this cuts, and its rule is followed here rather than
re-invented:

- `inside_the_null is True` → the words are *"we cannot tell"*. Left alone. Withholding a
  refusal because its world is unknown replaces a caveat with a silence, and that reading
  cannot mislead upward. `method_skill.inside_the_null` is `true` today and is untouched.
- `inside_the_null is False` → the figure CLEARS its null, which is a direction. Withheld
  when no world is named. Both AUC blocks are in this state today.

The numbers all stay. `null_95_low`, `null_95_high`, `null_point`, `p_two_sided`, `basis` and
the observed value are what was measured; only the direction read off them needs a world to
stand in. That is `_leg_in_this_world`'s grammar, not a new one.

## The fail-open that the naive repair walks straight into

`_auc_reading` branches on `if bound.get("inside_the_null")`. Setting the flag to `None`
without touching that function sends the withheld case down the falsy edge into

> "The observed value is OUTSIDE it and above the null … the belief carried real information
> about who stays."

— the exact sentence being withheld, printed *because* it was withheld. This is the same
two-branch-ternary-over-a-tri-state defect `_error_bar` records against itself on 2026-08-29
("THREE BRANCHES, BECAUSE THERE ARE THREE STATES"), and it is why the flag and the sentence
move in one change.

## Disposition

Repaired in this claim. `_auc_null` takes the world it was measured in, publishes it, and
withholds `inside_the_null` with a named reason when the comparison resolves and the world is
unknown; `_auc_reading` grows the third branch. Control:
`test_an_auc_null_from_a_run_that_names_no_world_withholds_its_direction_and_keeps_its_numbers`.

**What is NOT repaired here, and is the honest residual:** the withheld verdict clears itself
only when the three-arm run behind this panel is re-run in a tree that stamps `world_identity`.
That run exists already — `current_world` reads it — but this panel is the SUPERSEDED one,
published beside the live one on purpose, so the fix is not to point this block at the live
run. It is to let the superseded panel say plainly that its skill verdict is unplaceable, which
is what it now does.
