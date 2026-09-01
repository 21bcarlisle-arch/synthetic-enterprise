**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `OPS1_process_manifest_reconstruction`

# Two lanes built the same whole-book departure level, and only one of the two numerators is bounded

**Found:** 2026-09-01, reconciling local `main` with `origin/main` after the tree ran as two
histories for a day. Not by a control — by a merge conflict that a textual auto-merge had already
half-hidden.

## What the fork actually cost, measured

Local `main` and `origin/main` diverged at `178bf5a56` (2026-08-31 14:49) and ran as two histories
for roughly ten hours: **17 commits local-only, 20 upstream-only**. `git merge` reports 18
conflicted files; that number understates it, because the interesting collision **merged cleanly**.

`tools/departure_population.py` auto-merged into a module carrying **two implementations of one
quantity** — the whole-book departure level over an account denominator — because each lane added
its own in a different region of the file. Nothing conflicted. Git had no way to notice, and
neither would a reader who only read the conflict list:

| | local (`fd8c78303`) | upstream (9 commits) |
|---|---|---|
| refusal | `BOOK_BLIND_REFUSAL` | `account_denominator_refusal` + `ACCOUNT_DENOMINATOR_PROPERTIES` |
| reading | `book_departure_level` | `union_by_year` |
| caller | `world_book_departure_rate_pct` | `world_book_rate_pct` |
| numerator | `1 − Π(1−p)` per account | `Σp` over accounts |
| partial years | caller windows on `COMPARISON_YEARS` | derived from the capture's own edges |
| realised rate | absent | `realised_rate_pct` beside the expected one |

This is the `VAT_RATE` shape CLAUDE.md names — *one requirement, five implementations, and nothing
anywhere able to notice* — arriving by concurrency rather than by carelessness. **A file that
auto-merges is not thereby reconciled.** The conflict list is the set of places git could not
guess; it is not the set of places where two lanes disagreed.

## Which one won, and it was decided by measurement rather than by seniority

**Upstream, on every path.** The blast radius decided it, not the merge author's preference:

- `tests/architecture/test_switching_rate_commons.py` — the band control, a published gate —
  **auto-merged onto upstream's API** and calls `instrument.world_book_rate_pct()` at two sites.
  Keeping the local API would have left the band control calling a function that no longer exists.
- Local's contribution to the whole five-file cluster is **exactly one commit**, `fd8c78303`.
  Upstream's is nine, across `departure_population`, `population_anchor`,
  `measure_departure_level`, `fit_year_level_anchor` and the population test.

So the five files were taken from upstream wholesale rather than hybridised. A hybrid would have
been the worst outcome available: it keeps both APIs alive and makes the duplication permanent.

## What was given up doing that, stated because it is not nothing

**Upstream's numerator is the additive one, and local had already measured that it is wrong.**

`union_by_year` computes `expected_rate_pct = Σp / accounts`, summing every decision's
`realized_churn_probability` over the account denominator. An account facing several decisions in a
year contributes the sum of its hazards. But **an account can only depart once**, so over an
*account* denominator the numerator has to be the expected number of departing accounts,
`Σ_account [1 − Π(1−p)]`, which is what local's `book_level_from_hazards` computes.

The additive form is not merely a different convention — it is **unbounded above**. An account
facing eleven cap-period decisions can be assigned a departure probability over 1, and the rate can
exceed 100%.

The gap is not hypothetical and was measured before this merge, on the 2026-08-31 two-route
capture, and is recorded in
`WORKER_PREREGISTRATION_WHAT_A_WHOLE_BOOK_DEPARTURE_TARGET_MUST_SHOW_2026-08-31.md`:

| 2022, SVT-only | |
|---|---|
| `Σp` (upstream's landed form) | **12.8024%** |
| `1 − Π(1−p)` (local's, discarded here) | **12.0889%** |

Every SVT floor computed the additive way is ~5% too high and every anchor fitted against it ~12%
too low. **The trunk is currently publishing the higher one.**

## This is filed, not fixed, and the reason is a rule rather than a shortage of time

Repairing the numerator inside the merge that reconciles two histories would make the move
unattributable — a figure would change and two things would have changed. That is the exact failure
CLAUDE.md names, and upstream's own `world_book_rate_pct` docstring invokes it against itself for
the same reason ("moving a control's subject inside the commit that repairs what it measures is how
a moved number becomes unattributable").

**What is owed, on the reconciled trunk and as its own commit:** replace `union_by_year`'s
`expected_rate_pct` numerator with the competing-risks form, keeping upstream's refusal, its
`realised_rate_pct` and its derived `partial_year`. The prediction is already on the record above —
every year's expected rate falls, 2022's SVT-only level moves 12.8024% → 12.0889% — so the commit
that makes the change can be graded against a number written down before it.

The local implementation is not lost: it is `book_level_from_hazards` in `tools/departure_population.py`
at `fd8c78303`, with its own tests, and the repair is a transplant rather than a rebuild.

## The other thing the merge found, and it is the smaller half

`tests/background/test_publish_provenance.py` had a conflict git resolved as "two constants added
at the same line". Both were needed and the union looked correct — and it was still **red**, because
the four local red-count tests call `record_verified` without the `population` upstream started
requiring on 2026-08-31. A union that satisfies the conflict markers can still fail the merged
program, which is the argument for running the tests rather than reading the diff.
