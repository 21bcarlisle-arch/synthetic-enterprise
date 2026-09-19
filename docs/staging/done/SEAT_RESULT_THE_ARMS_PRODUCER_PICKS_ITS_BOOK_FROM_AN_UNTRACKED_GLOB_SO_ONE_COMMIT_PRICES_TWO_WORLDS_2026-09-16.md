**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
"the-arms-artefact-cannot-name-the-book-or-the-world-it-priced"

*LATENT, not BLOCKING: the stamping landed with this file and nothing published is retracted. What
remains — that the INPUT SELECTION itself is non-deterministic across checkouts — is real, is now
visible in every artefact this producer writes, and is handed on rather than wedged.*

# The arms producer picks its book from an untracked glob, so one commit prices two worlds

Delivery seat, 2026-09-16, against `5a63cb3a3`. Discharges the Lane 0 item
"the-arms-artefact-cannot-name-the-book-or-the-world-it-priced". Evidence for the item:
`2bc442bab`; discipline propagated from `f9866cd2a`.

---

## Premise check

Both commits the item cites were already ancestors of `origin/main` at draw time. **The premise was
NOT spent**: `f9866cd2a` stamped `tools/run_value_cycle_ab.py` and `2bc442bab` recorded the
consequence of the gap — neither touched `tools/couple_value_based_pricing.py`, which still carried
no `generated_at`, no `producing_commit`, no `world_identity` and no `book_identity` at any depth.

## The root cause, measured

`latest_run_output()` selects the lexical max of a glob over `docs/reports/run_output_*.json`
restricted to names containing `"2026"`. **Those files are untracked.** Run from two checkouts of
the same commit, on the same machine, on the same day:

| checkout | candidates | selected | size | accounts |
|---|---|---|---|---|
| `/home/rich/synthetic-enterprise` (shared) | **6,219** | `run_output_edded3973_20260916T085959Z.json` | 27.5 MB | tens of thousands |
| `/var/tmp/se-seat-executor` (linked worktree) | **4** | `run_output_f5808bd_20260618T054253Z.json` | 205.9 KB | **14** |

Same code. Same commit. Same command. A run from this morning against a run from June. **Nothing in
the output said which**, so the published 397-account reading and a 226-account re-run presented
as rival calibrations of one book when they were two books, two worlds and two producer vintages —
which is precisely what cost a full Lane 0 invocation to establish by hand in `2bc442bab`.

The book side is no better: `site/data/customers.json` is regenerated independently, and the join is
on `customer_id`, which **is not a stable key across runs** (`C1` appears in two artefacts with
different `eac_kwh`). The published 397-account artefact joins only **81** of its accounts to the
book now on disk.

## What landed

`tools/couple_value_based_pricing.py` now stamps every artefact it writes, above the figures:

- **`producing_commit`** — resolved at **import**, never at assembly, with `unavailable_because` as
  the fail-closed leg. Never the assembly tree's sha: the whole use of the field is telling those
  two trees apart.
- **`world_identity`** — the departure-level digest. Load-bearing *here specifically*, because
  `belief_versus_truth` reads the world's own response curve, so a re-fit of the anchor moves every
  belief figure in the artefact without touching a line of this module.
- **`book_identity`** — households not meters (dual-fuel legs collapsed on the `-g` suffix), plus
  `read_from`, which names **both input files**, their size, mtime, the run's own `_cache_meta`
  stamp, **and how many candidates the glob chose from**. A candidate set of 4 and one of 6,219 are
  different questions and looked identical before.
- **`run_identity_fields`** — so `tools/promoted_artefact_claim_census` can grade a claim about
  which run sits at this path.
- The snapshot is taken **beside the read** and passed down, never re-resolved at assembly. That
  difference is the control, not a style point — it is the half of `f9866cd2a` that condition 1
  originally landed wrong.
- The gap ledger's `run_git_commit` now reads the same constant. Two answers to "which commit" in
  one file would be two facts that drift.

**HEAD's artefact is deliberately NOT retro-stamped.** Per `f9866cd2a`'s own ruling, a superseded
reading cannot have its book established after the fact — and in this worktree a regeneration would
price 13 accounts and destroy the published 397-account reading.

## The control that was deliberately NOT propagated

The item asked for `same_book_across_arms`. **It is not propagated, and that is the finding's most
important line.** There, two arms are two phase-4c passes that can genuinely serve two books. Here
both arms are decided inside **one loop over one list** — they cannot differ, so a cross-arm book
check compares a value with itself: a control whose FAIL branch does not exist. Shipping it would
have looked exactly like discharging this item while guarding nothing.

The reachable control in this file is the **input join**, and `inputs_agree_on_the_book` is it:
tri-state, `None` for "cannot tell", keyed to the property (*are the run's accounts mostly absent
from the book?*) rather than to today's coverage figure.

## A fail-open I shipped and my own test caught

The first draft measured the join as `accounts_priced + accounts_skipped` over the run's account
count. `accounts_skipped` counts an account the book has **never heard of** in the same bucket as
one the book holds without consumption — so the denominator tracked its own numerator and the ratio
was `1.0` whatever the book was. The control could not fail. It is recorded in the code comment at
the fix, and pinned by `test_the_input_join_control_CAN_FAIL_and_does_on_a_mismatched_pair`, which
asserts **both** branches in one test because a guard proven only on the case it rejects is not
proven.

## Evidence the controls can fail

Six mutations, each firing exactly one test:

| mutation | test that caught it |
|---|---|
| `book_identity` resolves segments itself instead of using the caller's snapshot | `…NAMED_absence_and_never_todays_resolver` |
| join control defaults to agreement instead of tri-state `None` | `…is_TRI_STATE_and_cannot_tell_is_not_agreement` |
| `producing_commit` falls back to the assembly tree's sha | `…NONE_with_a_reason_never_a_placeholder` |
| provenance appended below the figures | `…names_its_code_and_its_world_ABOVE_the_figures` |
| dual-fuel legs not collapsed | `…COLLAPSED_so_the_book_counts_households_not_meters` |
| join re-derived from `compare()` output (the original fail-open) | `…CAN_FAIL_and_does_on_a_mismatched_pair` |

52 tests in `tests/tools/test_couple_value_based_pricing.py`, green. `tests/design/`,
`tests/architecture/test_static_quality_ratchet.py`, the domain-constant origin gates, the promoted
artefact census and `site/test_the_baseline_comparison_reaches_the_reader.py` all green.

## What is owed next, and is NOT fixed here

1. **The selection itself is still non-deterministic.** Stamping makes it *visible*; it does not
   make it *reproducible*. The producer should take the run output as an argument, or the run
   outputs should be addressable by something a second checkout can resolve. This is the next piece
   and is handed on.
2. **The EAC clamp** — see
   `SEAT_RESULT_THE_ARMS_ENDPOINT_BOUND_COUNT_IS_A_STUB_PERIOD_COHORT_NOT_A_CONSTANT_AND_P1_IS_REFUTED_2026-09-16.md`.
   An account with two bills is presented to the pricing arm as consuming 6× less than it does.
3. The site feed does not yet surface the provenance to a reader of the page; the artefact carries
   it and `generate_value_arms_data` passes through unchanged.
