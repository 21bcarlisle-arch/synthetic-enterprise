**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none (HEAD red register, `tests/harness/test_premise_two_level.py`)

# The eight premise two-level reds are two fidelity corrections the harness was never re-read against

**2026-09-30.** Found by a scheduled-tick worker drawing the HEAD red register.

## What was run

`tests/harness/test_premise_two_level.py` was run in clean `git archive` extracts, so no other
lane's working-tree edits could reach it. Results at each commit:

| commit | what it is | red |
|---|---|---:|
| `bde2514dc` and its parent | one-person household share (2026-09-08) | 0 |
| **`affc29e03`** | **hot water corrected to SAP 36+25N L/day with a 30.1 K rise, and cooking gas added. Director's decision, 2026-09-08** | **5** |
| `8f315e53f` | the register's last census (2026-09-23 02:58) | 5 |
| `263b57ac0~1` | | 5 |
| **`263b57ac0`** | **the fabric path asks the property record's own function (2026-09-23 15:51)** | **8** |
| `7b792426d`, `c08932808`, `f0ba399a4~1`, HEAD `217da4fc6` | | 8 |

Both steps are world-fidelity changes, and both are the right kind: sourced and decided blind to
results. Neither re-read this harness. The register lists only the first five because its last
census predates `263b57ac0`.

## The eight, by what kind of red each is

**Pinned to the old world's measured answer.** Re-deriving these on the new world is a re-baseline,
not a repair:
- `test_MEASURED_population_values`: the worst home is now P0000 (0.1526), not P0036.
- `test_the_L1_1_BREACH_WAS_the_WATER_HEATER...`: P0008's water heater is 29.7% of what L1.1 called
  behaviour, against a 30% floor. The hot-water correction shrank it, which is the expected
  direction.
- `test_the_worst_L1_1_cell_is_the_worst_MARGIN...`: this test's own PREMISE no longer holds. The
  heat-pump home's raw value is 0.1159 against gas 0.1139. It needs a population where that premise
  holds, not a looser assertion.
- The `0.292 ± 0.02` pin, which now reads 0.2348.

**The ones that could be a real signal. Do not re-pin these until they are understood:**
- `test_L2_3n_a_REAL_population_passes_at_EVERY_window`: the real panel no longer beats its own
  re-deal null at 40 days (0.724) or 60 days (0.854). It does at 90 and 120.
- `test_L1_1_FIRES_when_the_SWITCHED_LOADS_are_made_CONTINUOUS_again`: that mutation no longer
  re-opens L1.1, and only L2.4 fires. Either the switching is no longer what holds the cell open,
  or the smaller hot-water term took the headroom the mutation needed.
- `test_the_REPAIR_ITSELF_fires_its_own_named_defect` and `test_the_WATER_HEATER_netting_is_a_LOAD_SET_repair_and_not_a_LOOSENING`
  (electric homes fire at 0.110 to 0.165 against a gas median of 0.306, and the bound is under a
  third): these are the control's own mutation legs. If a mutation leg goes green, the control
  is either missing a test or the mutation is now an equivalence. Which one is not yet established.

## What I did not do, and why

I did not re-pin anything. Half of the eight are this harness's own mutation legs. Re-pinning them to
whatever the new world reads would turn a control that has stopped firing into one that cannot fire.
The next step is the sim lane's: for each mutation leg, establish whether it is a missing test or an
equivalence on the corrected world, then re-derive the four measured pins in one commit that names
both causes.

## Now blocking every coupled-gap ledger write (2026-10-01, autonomous worker)

The test selection names this file, and `tests/tools/test_couple_fabric.py`, for any commit that
changes `docs/observability/coupled_gap_ledger.json`. At origin `5e02bbdda` there are ten reds
across the two files: these eight, plus `test_couple_fabric`'s
`test_the_TEXTURE_CELL_BREACH_CLOSED_when_the_LOAD_SET_WAS_REPAIRED` (worst home S9, pinned D7) and
`test_the_money_consequence_is_AFFINE_in_the_unit_rate_for_a_fixed_decision`. A surgical landing of
EP1's re-graded row (gap 2.364 to 1.081) was refused on exactly those ten. No lane can publish a
coupled gap until they are resolved, so this item is ahead of new ledger work. The way through is
unchanged: decide whether each mutation leg is a missing test or an equivalence, then re-derive
the measured pins in one commit.
