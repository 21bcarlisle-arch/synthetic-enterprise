**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** none · **Claim:** `four-value-arms-reds-already-red-at-head` (Lane 0 delivery)

# Four value-arms reds: two debts landed past a gate that never ran, two controls keyed to the day's answer

Premise re-measured at `513d2a4b6`: all four were red. The duplicate-work note named this claim's own
id, so there was no second piece of work to defer to.

| Red | Turned red by | Cause | Disposition |
|---|---|---|---|
| `test_the_undeclared_quotient_debt_only_SHRINKS` (fold margins) | `f9c1bf956` (09-24) | `margin_required_* = t(n-1)*stdev/sqrt(n)`: the bar restated in pounds, divided only by a count. The census could not reach a `DENOMINATOR BOUNDED` declaration because the dict also held a block-wide `unavailable_because`, so the site was graded against a gate that was never its gate. | **Census fixed:** it now accepts the declaration on the branch where the sibling gate is not read. That branch only, so no GATED site is regraded. Site declared, and pinned in `DECLARED_BOUNDED`. |
| same test (`seeds_needed_at_this_depth`) | `d678f063a` (09-27) | A real unbounded quotient, `(t*sd/|mean|)^2`, published as a plan. Its own docstring said it had no upper bound. | **Gated:** published only where the family mean clears its own bar. The arithmetic moved to `seeds_needed_at_the_point_estimate`, with a named `_unavailable_because`. Pinned in `REPAIRED`. |
| `the_sentence_cannot_say_MEASURED_when_the_measurement_REFUSED` | `f243bd573` (today, budget 1,200 → 1,050) | The test hard-coded 425 customer-years as the reachable side, and 425 × 2.82 = 1,198 is now over capacity. The code is right. | **Re-keyed:** the two books now sit at ±25% of `capacity / multiple`, with capacity read off the verdict. |
| `the_published_key_no_longer_asks_for_work_...` | world-D retake (`c3939e7b1`) | All three redraws on the live selection leg came out negative, so `sign_determined: true` and the remedy block correctly refuses. The test treated the refusal as "cannot run". | **Re-keyed:** when the leg's sign is determined, the test asserts that the block refuses *for that reason*. Otherwise its checks are unchanged. |
| `the_requirement_is_stated_in_both_units_...` | artefact retake, on top of `08c696269`'s gate | The test read the plan-named keys, and those are withheld when the reading fails its null. It got `None ** 2`. | **Re-keyed:** the test now reads `*_at_the_point_estimate`, which is published in both states, and asserts that both units are gated together. |

Mutations: removing the census's new leg fails 2 tests, ungating the depth count fails 2, and
un-squaring the pairs multiple fails the units test.

**The class behind the first two rows:** both debts landed because the gate selects tests by subject
module stem, so a commit to `fold_noise_floor_family` or `selection_residual_decomposition` never
runs a census that lives in `tests/architecture/`. That cause was already filed on 2026-09-25
(`done/SEAT_FINDING_A_GENUINELY_RED_ARCHITECTURE_TEST_IS_ABSENT_...`). I am not re-filing it. This
is its second and third instance.
