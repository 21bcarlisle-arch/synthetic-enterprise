**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the unbounded quotient is a class of sixteen, not a fifth instance, and my first two
drafts of the control over it could not fail

**Filed:** 2026-09-22. Drawn as Lane 0 delivery,
`the-unbounded-quotient-is-caught-as-a-class-by-a-control-not-as-a-fifth-instance-by-hand`.
Pre-registration:
`docs/staging/records/SEAT_PREREG_THE_UNBOUNDED_QUOTIENT_CENSUS_BY_SHAPE_2026-09-22.md`,
filed before any candidate site was read.

## The premise, re-measured

All four cited commits (`06e316ae4`, `5742edb1c`, `964036259`, `949f80894`) are ancestors of
origin/main, as the draw said. **That does not spend the item**: those commits are the four
INSTANCES, and the item asks for the CLASS CONTROL none of them built. The one live rival claim is
this same id held by this draw. Nothing to release. The draw's `[stale-copy]` caveat named a base
three commits behind; this worktree measured `0 0` against origin/main, so no door named there was
walked.

## P1 confirmed, and by a wider margin than it predicted

`tools/unbounded_quotient_census.py` censuses `tools/`, `saas/` and `company/` **by shape** — an
AST walk for published keys in the plan grammar (`*_needed*`, `*_required*`, `*_must_offer*`) whose
value resolves back to a quotient. It finds **23 sites: 4 GATED, 3 BOUNDED, 16 DEBT.**

The fifth instance predicted by P1 is not one site but a file. **`tools/inference_claim.py` carries
six**, under names sharing no vocabulary with the four hand-found ones:

| site | key |
|---|---|
| `inference_claim.py:857` | `decisions_needed_for_the_observed_effect` |
| `inference_claim.py:858` | `accounts_needed_for_the_observed_effect` |
| `inference_claim.py:862` | `settled_accounts_needed_for_the_observed_effect` |
| `inference_claim.py:918` | `decisions_needed_for_the_observed_effect` |
| `inference_claim.py:790`, `:819`, `:820` | `accounts_needed`, `decisions_needed` |

It is the same rule exactly. `detectability()` computes `decisions_for(excess) =
ceil((k / excess) ** 2)` where `k` is the null's scale — the BAR — and `excess` is
`abs(observed - 0.5)`, the ESTIMATE. The same function's headline publishes
`observed_share_of_what_was_detectable`, which IS the grade; the docstring says in its own words
that the flagship figure sat inside its null. So the count is asked in exactly the state where its
denominator's interval contains zero, and the only guard on it is `observed_excess > 0` — the
degenerate point, not the interval. Its `floor` rows over the FIXED `FLOOR_EXCESSES` are **not**
this defect and are correctly bounded; only the `is_the_observed_effect` row and
`the_book_this_would_need` have an estimate downstairs.

The other ten: `tools/run_value_cycle_ab.py` (3), `tools/generate_value_arms_data.py` (3, around
`priced_renewals_needed`), `tools/fit_year_level_anchor.py` (3).

**P3 confirmed** — `billing_axis_coverage.py`'s `n_for_tolerance = ceil((Z_95/TOLERANCE)**2 * var)`
is the ordinary sample-size formula with a CHOSEN denominator and is correctly graded BOUNDED, as
are two sites in `published_route_split.py`. Distinguishing these was indeed the hard half.
**P4 resolved:** every site is in `tools/`. `saas/` and `company/` are clean of the shape today.

## The part worth more than the census: my control could not fail, twice

**First draft.** Graded a site GATED if a sibling key named the withholding. Un-gating the repaired
`rosters_needed_to_state_a_sign` from `point if clears_bar else None` to a bare `point` **left it
green** — because `price_at` returns `None` when the distance is exactly zero, and a
"can this be `None`" test cannot tell a divide-by-zero guard from a withholding on a failed bar.
A guard against a measure-zero input nobody meets and a refusal across the whole state a reader
asks the question in collapsed into the flattering one. The repair is `withheld_on_a_grade`: the
condition controlling the `None` must NAME the grade.

**Second draft.** Adding **one word** to the grade vocabulary — a degenerate-guard name — left all
six tests green. Every consequence of a too-wide classifier moves the DEBT count DOWN: the ratchet
only catches increases, the repaired set is a subset and stays satisfied, and the synthetic DEBT
case has no gate at all so its grade is vocabulary-independent. **A classifier that breaks open
reports the debt paid and every leg stays quiet.** This is the same failure
`test_a_domain_constant_carries_its_origin` records having built into its own first draft, and I
built it again while writing a control against a class of defect I had just read four instances of.
The repair is `test_a_DEGENERATE_guard_is_not_a_withholding`, which pins the DISTINCTION over the
real shape that caused it rather than any count.

Neither draft was caught by thinking. Both were caught by mutation, and the second only because
the first survivor made me distrust a green sweep.

## What landed

* `tools/unbounded_quotient_census.py` — the census, the rule stated once, and the closed set of
  two honest declarations (GATED / BOUNDED). Modelled on `tools/domain_constant_origins.py`,
  including its "why a count and not a register".
* `tests/architecture/test_a_published_count_gates_on_its_denominators_grade.py` — eight legs.
  Mutation-proven: four mutations, each firing on the leg written for it —
  un-gate a repaired site → `EXACT_SET`; classifier breaks open → `REACHABLE`; scan loses its
  subjects → `SUBJECTS`; vocabulary widened by one word → `DEGENERATE_guard`.

Keyed to the property, not to today's answer: repairing a DEBT site lowers the debt and does not
red anything. The control reds when a repaired site stops being repaired.

## What is NOT done, and it is the larger half

**The 16 DEBT sites are un-repaired.** The ratchet makes the 17th impossible and does not pay the
16. `tools/inference_claim.py` is the next piece and is handed off: its six sites are one function,
the established published form is two worked examples away (`_seed_price_interval`,
`_rosters_to_state_a_sign`), and the repair is mechanical now that the form is settled — gate on
the grade, name the withholding, rename the arithmetic out of the grammar of a plan.

**Two limits of the scan, stated so a green ratchet is not misread as "every count is bounded":**
it does not decide whether a denominator's interval ACTUALLY contains zero — no scan can, that is
a fact about data — and it resolves names within one function, so a count assembled across two
functions or through a dict round-trip is invisible. `_auc_against_the_money_legs_price`
republishes a count it never computes and this census cannot see it.
