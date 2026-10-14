**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** `how-many-synthetic-households` -- the page whose full-vector N this leaves owed

# The stranded seasonal-swing deletion lands, and it moves no settlement figure (2026-10-14)

*Delivery seat, LANE 0 draw `the-unlanded-demand-vector-edit-is-dispositioned-before-mondays-publish`.*

## Fate: live work, landed

The shared tree's `tools/demand_vector_coverage.py` (55+/19-, mtime 2026-09-24 15:02) is NOT a stale copy.
It is the code half of `SEAT_RESULT_THE_PUBLISHED_SAMPLE_SIZE_WAS_INFLATED_BY_AN_INVENTED_AXIS_2026-09-09`.
That document reached origin through the 09-16 staging sweep (92e8c0f96). The code never did, and nothing
anywhere carries the deletion text (`git log --all -S` returns nothing). Its paired test edits were dirty
beside it, with the same mtime:
`tests/tools/test_demand_vector_coverage.py` (per-column RNG streams, plus a guard that `seasonal_swing` is
not in `AXES`) and `tests/tools/test_gas_carries_a_hot_water_term.py` (the swing pairs come off
`_KNOWN_COLLINEAR`). b1145fe4a (09-08) called the *computed* swing real, and its own table shows the
*invented* one at |r| = 1.0000 with weather sensitivity. 3957ba848 (09-11) kept the axis because it was
built on a base without the deletion. It did not decide anything about the axis. So neither commit supersedes the edit.

All three files land together, as one package. Every test file that imports `demand_vector_coverage`,
`settlement_choice` or `reduction_dimension` passes: 10 files, 155 passed.

## Does it move a published figure? No, and by construction rather than by a seed run

`simulation/settlement_choice.py` uses its own `CHOICE_AXES` and imports only `choose_for_difference`,
`fit_weights`, `_Reference` and `accepts_weighted`. The transitive closure of those over the module's
AST is those four plus `weighted_ks`. It reads `A`, `FIT_SLICES`, `FIT_GRID`, `DISTRIBUTION_TOLERANCE` and
`JOINT_SLICES`, and never `AXES`, `DISTRIBUTION_AXES` or either population builder. The edit changes no
line in any of them. So the settlement choice behind `run_output_2248e3baf_*` and `run_output_6ab998ad7_*`
ran byte-identical logic with or without the edit, and the figures on the live page are unchanged.
What was wrong was only the stamp, and after this landing the stamp is right.

## What this leaves owed (downstream now disagrees)

`site/data/knowledge_topics.json` (`how-many-synthetic-households`) still publishes the full-vector N
as **6,816 against 20,000 and 8,822 against 120,000**. Both were measured with the duplicate axis. The
09-09 bridge gives **5,215** at 20,000 without it. The 120,000 re-measurement that document called
"running" never landed. The page is now behind its own code. That is a re-measure and a page edit,
handed on as a continuation. It is not done here, because the 120k run is not a one-turn job.

## Falsifiers

- `python3 -c "from tools.demand_vector_coverage import AXES; print('seasonal_swing' in AXES)"` at origin -> `False`.
- `imports_off_commit("tools/run_annual_report.py", <origin head>)` on the shared tree lists no
  `tools/demand_vector_coverage.py` code entry once the shared copy is refreshed.
