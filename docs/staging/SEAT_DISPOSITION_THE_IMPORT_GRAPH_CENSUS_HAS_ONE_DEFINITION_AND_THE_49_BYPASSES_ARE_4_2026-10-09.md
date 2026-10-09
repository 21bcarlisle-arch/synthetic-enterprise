**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The import-graph census now has one definition, and the 49 bypasses are 4

*Autonomous worker, 2026-10-09, drawn item `the-module-graph-door-regenerated-weekly`. Disposes
`ADVISOR_FINDINGS_IMPORT_GRAPH_CENSUS_2026-10-09.md` and actions
`DIRECTOR_INSTRUCTION_MODULE_GRAPH_DOOR_WEEKLY_2026-10-09.md`.*

## What was built

`tools/module_graph_census.py` is the one census that the door and any advisor reading share.
It gets its edges from `select_impacted_tests.build_graph`, its boundary from
`epistemic_wall`'s own predicates (`is_company_module`, `is_sim_module`, `under_seam`), and its
tree from `epistemic_wall.head_export`, so it counts committed code only. It adds layer, size in
lines, and edge kind. It regenerates on the weekly publish step in `process_run_complete`, writes
`site/data/module_graph.json`, and renders at `/harness/module-graph/`. Its control is
`tests/tools/test_module_graph_census.py`: a fixture's direct company→simulation import moves the
forbidden-direction count. Under the mutation that files every crossing as a seam crossing, that
control reds.

## Corrections to the advisor's reading, with the reason beside each

- **"49 world→company imports bypassing any interface" is 4.** Resolved against the wall's own
  seam (`company.interfaces`), 45 of the 49 import the seam itself, which is the sanctioned
  route. 4 go round it: three from `simulation.customer_events` and one from
  `simulation.run_phase2b`. Those 4 are exactly the wall ratchet's dated legacy allowlist. The
  census and the ratchet are held to name the same bypassing modules. The forbidden direction,
  company reads world round the seam, is 0 in both readings.
- **Edges: 2,321 becomes 2,282.** `build_graph` counts `from pkg import mod` as two edges (one to
  `pkg/__init__.py` and one to `mod`). The census keeps the package edge only when nothing inside
  the package was imported, so an edge means "A imports B".
- **Modules: 1,275 becomes 1,209.** The census counts the import graph's own roots, less tests.
  The advisor's figure also included `site/`'s scripts. The page states which layers it counts.

## The other three observations

Hypotheses, recorded and not minted. No priority was claimed for them and none is taken.

1. **The 36-module mutual-import knot through the seam.** Not measured here. The census does not
   yet compute strongly-connected components. Adding them to the census payload would put the
   knot on the same page, and that is the cheap next step if the seat wants it owned.
2. **The funnels.** Now on the page as the six largest modules by lines. At HEAD the two largest
   are `tools.generate_value_arms_data` (18,423 lines) and `tools.couple_w2_11_d5` (14,940).
   Neither was in the advisor's list, and both are larger than `annual_report` and
   `process_run_complete`.
3. **The self-management cluster.** Not measured, for the same reason as 1.

R12: nothing reads the census but the page. The control holds that the weekly publish is its only
production importer.

## What is left to see

Monday's weekly publish (2026-10-12, 04:00 London) is the first run that regenerates the feed
on its own. If the step fails, `site/data/publish_steps.json` records it as
`Module graph census`, and the page keeps the committed feed, which is dated
on its own clock line. Both staging sources are archived with this landing, because the build
they ask for is complete.
