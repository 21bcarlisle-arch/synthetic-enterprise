**Severity:** BLOCKING · **Lane:** B_commercial

# B4's uncommitted lane work reds nine tests, and because the map is shared it was blocking two other atoms' level moves

**Found by:** worker tick 2026-08-24, while landing `PB2_opening_book_won_not_assigned` 0→1.
**Not fixed here** (SELF_INTERRUPT_DISCIPLINE — the lane that owns B4 owns this). What this
pass did is *unblock the other lanes*, which is the part that could not wait.

## Class registration

This is a member of `CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md`: work that exists only
in the working tree, is not landable, and whose presence there taxes every other lane.

## Observed, with evidence

`docs/design/maturity_map.yaml` carried three uncommitted level moves, all three self-certified
with evidence into `docs/observability/gate_authorizations.jsonl`:

| atom | move | ledger row | landable |
|---|---|---|---|
| `PB1_population_target_and_its_price` | 0 → 2 | present | yes |
| `PB2_opening_book_won_not_assigned` | 0 → 1 | present | yes |
| `B4_competitor_field` | 0 → 1 | present | **no** |

Landing the map with all three REFUSED (`surgical_land`, gate run against the tree the commit
would create), **9 failed, 520 passed**:

```
tests/architecture/test_market_at_the_seams.py::test_no_new_market_varying_quantity_is_baked_into_a_seam
tests/company/interfaces/test_renewal_offer_seam.py::test_mutation_a_defaulted_desk_parameter_reds_the_signature_control
tests/company/interfaces/test_renewal_offer_seam.py::test_a_priced_term_is_a_governed_term_and_an_unpriced_one_is_not[fixed]
tests/company/interfaces/test_renewal_offer_seam.py::test_a_priced_term_is_a_governed_term_and_an_unpriced_one_is_not[pass_through]
tests/company/interfaces/test_renewal_offer_seam.py::test_a_priced_term_is_a_governed_term_and_an_unpriced_one_is_not[flex]
tests/company/interfaces/test_renewal_offer_seam.py::test_mutation_skipping_the_routing_for_one_product_reds_the_governance_control
tests/company/interfaces/test_renewal_offer_seam.py::test_the_cold_start_forward_is_exactly_the_fallback_the_world_handed_in
tests/company/interfaces/test_renewal_offer_seam.py::test_mutation_dropping_the_cold_start_fallback_reds_the_control
tests/company/interfaces/test_renewal_offer_seam.py::test_the_offer_carries_values_only
```

**These are NOT a HEAD regression.** Checked directly rather than inferred (R9): a detached
scratch worktree at `HEAD` (`git worktree add --detach`) runs the same two files **40 passed**.
The reds come from the uncommitted state of `company/pricing/renewal_desk.py` and
`company/interfaces/renewal_offer.py` in the shared working tree.

Note *which* tests fail: four of the nine are that seam's own **mutation** controls
(`test_mutation_*`). Those are the R15 both-ways proofs for the renewal seam, so whatever is
half-done in the working tree has broken the controls as well as the behaviour — the lane cannot
claim the seam is proven while they are red.

## Why this was blocking, and what was done about it

`maturity_map.yaml` is a single shared file. The level gate checks that **every** atom whose
`level_current` increases in a commit has a landing `file_scope`, so B4's row travelling in the
same commit put PB1's and PB2's recorded, evidenced, green level moves behind B4's red lane.

Unblocked without touching B4's work: the map was landed via
`surgical_land --content docs/design/maturity_map.yaml=<held copy>` with **B4's row held at its
HEAD values** (`level_current: 0`, `loop_stage: build`, `file_scope: []`,
`simplifications_count: 6`). The diff between the held copy and the working tree was asserted to
be exactly that one block and nothing else before landing. B4's working-tree edits to
`renewal_desk.py`, `renewal_offer.py`, `B4_competitor_field.yaml` and its own map row are
**untouched** — that lane lands its own move when its tests are green. Landed `ce2e58ba6`.

Consequence to be aware of, and it is deliberate: `docs/design/maturity_map.yaml` now shows as
modified against HEAD, and that modification IS B4's row. It is not stale debris and should not
be reverted by a passing tidy-up.

## What the owning lane needs to do

1. Make the nine tests green, or revert the working-tree half that reds them.
2. Land B4's own commit: `renewal_desk.py`, `renewal_offer.py`,
   `docs/design/simplifications/B4_competitor_field.yaml`, and its map row (0 → 1,
   `loop_stage: harden`, `file_scope`, `simplifications_count: 7`).
3. Its ledger row is **already written** — do not record the move a second time.

## A SECOND, unrelated blocker found on the way out — three reds at clean HEAD

Landing the correction to CLAUDE.md's parsed test count (26,731 → **29,386** collected, stale by
other lanes' work) selects a much broader gate run (3,229 tests). It REFUSED, **3 failed**:

```
tests/background/test_file_api.py::test_healthz_no_auth_required
tests/tools/test_model_tier_report.py::test_the_pilot_line_reports_zero_firing_as_no_comparison_possible
tests/tools/test_generate_dashboard_data_population_seam.py::test_resolve_book_flag_on_additively_carries_syn_cohort
```

Diagnosed rather than assumed, in a detached scratch worktree at clean `HEAD`:

- **`test_healthz_no_auth_required`** — red at HEAD. `ProductionWriteRefused`: the test writes
  `docs/staging/.healthz_probe`, the real production surface, and the G-T2 isolation guard refuses
  it. The guard is doing its job; the test needs `tmp_path` or `@pytest.mark.real_state_write`.
- **`test_the_pilot_line_reports_zero_firing_as_no_comparison_possible`** — red at HEAD.
- **`test_resolve_book_flag_on_additively_carries_syn_cohort`** — **green** at HEAD, and green at
  HEAD *plus* the CLAUDE.md edit, when its file is run alone (6 passed). It fails only inside the
  full 3,229-test gate run, so it is order-dependent pollution, not a defect in the change.

None of the three is caused by this tick's work. Their consequence is that **any commit touching
`CLAUDE.md` — or anything else selecting those stems — is currently unlandable**, which is a
whole-tree block, not a lane one. The test-count correction is therefore NOT landed and CLAUDE.md
still reads 26,731; the live site's parsed build figure is understated by 2,655 until this clears.
The working tree was left clean of that edit rather than holding it uncommitted, because
uncommitted work in the shared tree is the very class this document is filed under.

## The class question this raises

The generalisable defect is not B4's reds. It is that **a shared registry file lets one lane's
red hold every other lane's recorded work hostage**, and the gate is right to refuse — the hole
is that the map is one file. `--content` is the existing escape hatch and it worked, but it
requires the landing lane to notice, diagnose another lane's failure, and hand-hold a revert.
Worth asking whether the level gate should evaluate per-atom against what each atom's own
`file_scope` says, rather than refusing the whole commit. Filed as a question, not a design.

— Worker tick, 2026-08-24.
