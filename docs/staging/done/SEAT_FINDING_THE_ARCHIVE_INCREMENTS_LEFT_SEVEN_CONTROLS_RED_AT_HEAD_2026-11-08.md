**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The archive increments left floor controls red at head (2026-11-08)

The seat executor's finding of this name was drawn as delivery-lane direction
(`the-archive-increments-left-five-floor-controls-red-at-head`), but its own file never reached
origin or `/var/tmp/se-seat-executor`. This record is written from the direction text and
from what the run found at origin `9dfbf9f960`.

## What was red at origin 9dfbf9f960

| Control | Live | Floor |
|---|---|---|
| `test_a_cited_constant_has_a_caller::test_the_walker_still_sees_the_repo` | 118 money constants | 150 |
| `test_a_domain_constant_carries_its_origin::test_the_whole_domain_named_population_is_still_in_scope` | 233 | 319 |
| `…::test_the_unsourced_domain_constant_debt_only_SHRINKS` | 126 debt | floor 208 |
| `…::test_the_scan_has_not_lost_its_SUBJECTS` | 171 | 263 |
| `test_published_row_scalar_census::test_the_poison_is_the_most_specific_collision_the_commons_can_produce` | specificity 2 | == 1 |

## Cause, measured with the live scanners at each commit

The first four come from the archive. Archive increments 1–4b (`745a5fd27d`, `19cd6bfd5d`,
`640bcd13e5`, `13ce18d9e3`, `83a213f854`, `6b70382ded`) moved the populations out of `company/`, and
archive/ holds exactly what left:

| | before 745a5fd27d | 745a5fd27d | 19cd6bfd5d | 640bcd13e5 | 13ce18d9e3 | 83a213f854 | 6b70382ded | archive/ holds |
|---|---|---|---|---|---|---|---|---|
| literal | 302 | 274 | 203 | 198 | 171 | 171 | 171 | 131 |
| promoted | 68 | 68 | 64 | 64 | 63 | 62 | 62 | 6 |
| unsourced | 246 | 220 | 154 | 149 | 126 | 126 | 126 | 120 |
| money | 185 | 175 | 136 | 132 | 120 | 120 | 118 | 67 |

Live plus archive/ equals the pre-archive count exactly, for all four populations.

The poison red has a different cause. `faf7b1a7e4` published the cap composition's gas
cross-check, and its row 11 has `derived_gbp_per_mwh = 75.06`. That agrees with 75.0 to three
significant figures, but it measures something else: GBP/MWh of gas, against GBP/kW/yr of capacity.

## Done

- Each floor is now `pre-archive floor − what archive/ holds`, counted by the same scanner. The
  unsourced-debt CEILING drops by the archived debt as well. Left at 255 over a live 126, it would
  have let 129 new unsourced numbers land without a red. A new leg in each file shows the shelf
  is seen (non-empty), the live walk skips it (no constant counted twice), and a planted pair at the
  same relative path splits correctly.
- The poison test now checks a property, not a count: the poison's only collision in its own
  unit is the Capacity Market clearing-price row. The census docstring that said "exactly ONE row"
  has been corrected beside the claim.
- Mutation probes. Each one made the named control red, and each was reverted:
  - 10 unsourced `_RATE` constants planted in `company/pricing/tariff_engine.py` → debt ceiling
    red. At origin these would have passed.
  - A cited, unreached GBP constant planted there → the caller test goes red.
  - Scanner `SCOPE=()` → all three population floors and the exclusion leg go red.
  - Shelf unreadable → every floor and both exclusion legs go red.
  - Live walk descending into archive/ → both exclusion legs and the debt test go red.
  - `units_agree` → False → the poison test goes red.
- The shared tree's staged index carries the next archive increment, and the controls stay green on
  it. The floors do not need retyping per increment.
- A sixth archive red turned up in the cheap gates: `tests/design/test_maturity_map_contract.py::
  test_file_scope_names_every_name_attributable_module` was charging atom C2 for
  `archive/unhooked_supplier/tests/company/crm/test_c2_discovery_wired.py`, which `6b70382ded`
  shelved. archive/README.md already says nothing in archive/ is collected, linted or indexed, so
  `repo_program_files` now excludes it, and a new leg shows the exclusion is taken: archive/ tracks
  .py files and none of them reach the list.
- Not checked: the original title says SEVEN controls. Six are accounted for above. The seventh was
  not named anywhere I could read, and no full-suite run was made to find it.
