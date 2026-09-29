**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# A genuinely red architecture test is absent from the HEAD-red register, and the register that would have to know is two days stale

Found while working the Lane 0 claim
`count-which-of-the-three-ungradable-causes-dominates-the-remaining-27-level-zero-rows`; the draw's
item flagged it as "not mine and not on the register" and that is confirmed, with a coupling the
item did not name. **Not repaired here** — the repair needs a judgement about what
`sems_needed_to_state_a_sign` counts, and that is not a drive-by. Scope stated plainly rather than
scaled down quietly.

## The red, reproduced at `208195dd4`

`tests/architecture/test_a_published_count_gates_on_its_denominators_grade.py::test_the_undeclared_quotient_debt_only_SHRINKS`

```
AssertionError: 2 published counts now carry a measured denominator with neither a withholding
sibling nor a `#: DENOMINATOR BOUNDED:` declaration, against a ceiling of 0.
  tools/fold_noise_floor_family.py:612 margin_required_over_draws_gbp
  tools/fold_noise_floor_family.py:613 margin_required_over_seeds_gbp
```

The grader's own words on why the withholding does not count: *"a sibling key names a withholding
this site … the count is computed on every path, so the reason key sits reassuringly beside a figure
that is always published"*. `tools/fold_noise_floor_family.py:606` is `"unavailable_because": None`,
hardcoded — the withholding sibling exists and is inert at this site.

## The coupling the item did not name, and it is the reason this matters beyond one red

`background/head_red_register`'s observation store holds **37** currently-red nodes and **no row for
this test at all**. Its last run is `2026-09-23T04:31:10+00:00` — the census is
`OnCalendar=*-*-* 03:30:00`, so it has missed two runs.

That register is now load-bearing in a second place. `7db38ae47` (2026-09-25) made
`tools/level_zero_contradicted_by_its_own_controls.reds_at_head` read it to silence a level-0 row
without spending its pytest run, and that is the leg which moved the census from 0 graded to 1. **A
red the register does not know about cannot silence a row**, so a stale register does not merely
under-report the tree: it silently shrinks the only thing that made the map's silence falsifiable at
all. The staleness bound in `reds_at_head` is deliberately loose (seven days, argued at the site
because a tight bound is unsatisfiable exactly when the census slips) — which is right, and it means
the mechanism cannot notice this.

## What done means, for whoever takes it

Two separable pieces, and the second is the one with the leverage:

1. **`tools/fold_noise_floor_family.py:612-613`.** `_margin` is `bar * sem` where
   `bar = sems_needed_to_state_a_sign`. Say what each factor counts before declaring anything: if
   `bar` is itself computed over `sem`, the product cancels and there is no unbounded denominator —
   in which case the honest answer is a `#: DENOMINATOR BOUNDED:` declaration naming that
   cancellation, not a withholding. If it is not, the figure needs a real withholding, and
   `unavailable_because: None` at line 606 has to stop being a literal.
2. **The register missed two scheduled runs and nothing said so.** `Persistent=true` means a box
   that was off still measures on return, so two missed runs is not a late census — it is a timer
   nothing is watching. Ask what ENDS the condition before writing a screen for it.

## Why it is BLOCKING and what it currently costs

Gate selection is by subject module stem, so every lane that touches
`tools/fold_noise_floor_family.py` — or that test module — inherits this red and cannot land until it
is fixed. That is the live tax, and it is paid by whichever lane arrives first rather than by anyone
who chose it.
