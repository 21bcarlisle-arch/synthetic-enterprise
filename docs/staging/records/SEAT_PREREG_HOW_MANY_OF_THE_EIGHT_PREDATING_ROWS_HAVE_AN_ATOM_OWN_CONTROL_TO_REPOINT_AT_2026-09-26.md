**Severity:** INFO · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: how many of the eight CONTROL_PREDATES_ROW rows have an atom-own control to repoint at?

Written BEFORE running the discovery query. Subject: the eight live members of
`CONTROL_PREDATES_ROW` in `tools.level_zero_contradicted_by_its_own_controls`, the class whose
printed repair reads *"repoint the row at a control this atom's own build wrote, or leave the row
at zero because it is right"*. That repair offers two exits and the row cannot tell you which one
it is owed; the query decides it per row.

## The population, as the grader reports it at `origin/main` (`--budget 0`, so no row runs)

`D27_belief_window_saturates_on_this_book`, `D9_worse_than_blind_chip_is_metric_blind`,
`H41_the_map_ratchet_has_no_ongoing_drain`, `A50_the_supplier_use_case_register_is_published_with_a_status_per_item`,
`W2_31_people_phase1_the_physical_layer_stands_alone`, `W2_non_dd_miss_vocabulary`,
`W2_18_the_housing_joint_the_sample_and_the_ceiling`,
`W2_19_who_lives_where_money_and_composition`.

**The drawn item named FIVE and the live class holds EIGHT.** The item's count is recorded here as
what it was, not corrected silently: the three it does not name are `W2_non_dd_miss_vocabulary`,
`W2_18` and `W2_19`. A count written into an item's prose is a prediction about an instrument, and
this one is stale by three.

## The query, stated before it is run

For each row: date the row by `-S<atom_id>` over both map halves (the grader's own `_oldest_commit_epoch`,
so the dating leg cannot disagree with the thing it is describing), then ask git for every
`test_*.py` path touched by a commit whose subject or body mentions the atom id, and keep those
whose own birth (`--follow`) is LATER than the mint. That is the grader's exact definition of
"atom-own", asked through the grader's own oracle.

## What I predict

**Between 3 and 5 of the 8 yield at least one atom-own control.** The reasoning: `H41`'s shape is
worked through in the module docstring as the case where BOTH named suites predate and the atom
genuinely extended existing stores — I expect it to yield nothing. `A50` names a `site/` door,
and the site lane tends to extend one door file rather than write a new one per atom — I expect
nothing there either. The three `W2_*` population rows sit on `test_population_draw.py` and
`test_household*.py`, long-lived suites, but those atoms are recent and likely wrote a named
suite of their own. `D27` and `D9` name coupling/proof controls I have not looked at.

**Zero would be the interesting result**, and it would mean something specific rather than
"nothing to do": that the repair string's FIRST exit is unreachable on this map and every member
of the class is owed the SECOND — the row left at zero with the reason written into it. I would
then be repairing the repair string, not the rows.

**Eight would be equally interesting** and would mean the class is pure map defect, which is what
the drawn item assumes without having asked.

## What I will do either way

Rows that yield: repointed at the atom-own control, and delisted from
`LEGACY_UNGRADABLE_BUILD_ROWS` if listed — a repointed row that stays allowlisted reds every lane.
Rows that yield nothing: left at zero with the reason recorded, not repointed at a filename picked
to make a count move. **A row leaving the ungradable count by getting vaguer is the failure this
whole sequence exists to avoid.**

Result filed beside this document whichever way it lands.
