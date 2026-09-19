**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, the
write-keyed generated-path oracle

# The write-keyed oracle's named door has no instance in this tree, and the one that does is a signature default

**Filed 2026-09-15 by the delivery seat.** Claim
`the-write-keyed-oracle-cannot-follow-a-path-into-a-method`.
Prereg: `docs/staging/records/PREREG_WHAT_THE_WRITE_KEYED_ORACLE_GAINS_FROM_A_DEFAULTED_DESTINATION_PARAMETER_2026-09-15.md`.

**What the prereg's provenance actually is, stated because it is weaker than it first looks.**
It was landed as `7a6684226` before the post-change set was computed, which is the ordering that
makes a prediction a prediction. Origin then moved to `f4b8d2c6b` under this worktree, that commit
is orphaned, and the same bytes were re-gated and landed as `91bee21f5` — the parent of this
finding's commit. So what survives on origin is the DAG order (prereg commit, then result commit)
and not a timestamp proving the prediction preceded the measurement. `promote_worktree_landing`
refuses a landing while other tracked changes are uncommitted, so the two could not be pushed as
separate promotions; the ordering is real and its evidence is one step weaker than intended.

---

## What was asked, and why it could not be built

The Lane 0 item directed the seat to follow a path constant into a method called as
`self._write(...)` — "the largest door left open by the helper frame landed in `a2d130044`". The
premise came from this module's own docstring, which listed that shape as the next gap.

**Asked of the tree instead of assumed:**

| Over `tools/ background/ simulation/ saas/ company/` | |
|---|---|
| Classes | 2,058 |
| …with a method whose scope holds a write destination | 7 |
| …of those, with a bindable parameter reaching the write | 2 |
| Call sites anywhere of the shape `self.<writer>(...)` | **0** |

Five of the seven are `str.replace(old, new)` landing in `DESTINATION_ARG` and resolving to
nothing — the filter-not-safety case the module already documents. The two real ones are
`PublishStepLedger.write` and `ObservableTrace.save`, and neither is ever called on `self`.

So the frame would have been machinery no tree state can exercise: a control that cannot fire,
green forever, indistinguishable from one that works. It was not built. **The measurement is the
deliverable**, and it is recorded in the module beside the sentence that sent someone looking —
not deleted, because a claim quietly revised leaves no evidence the question was asked.

## The door that IS open, found by the same sweep

A destination parameter whose **default** is a module-level path constant, written when the caller
passes nothing: `def generate(out=OUT_PATH)` with `__main__` calling `generate()`. There is no
argument at the call site, so the helper frame binds nothing and takes its early exit — the path
is invisible to every route the oracle had.

Thirty-six `def`s in the scanned trees write a parameter carrying a default.

## What landed

`_default_destinations` seeds a parameter from its own signature default, resolved by
`_static_paths` against what the `def` **inherits** — the module for a module-level function, and
for a method what the CLASS inherited, never the class body. Python would allow the class body;
this does not take it, because narrower is the direction that cannot manufacture a path.

Two guards came with it, both mutation-proven:

- A parameter **rebound** in the body is refused. `_scope_path_names` accumulates rather than
  replaces, so seeding a default that the body overwrites reports **both** — and the mutation
  shows exactly that: `WALL_CROSSING_DISPOSITION_REGISTER.md`, a document this tree only reads,
  offered a REVERT.
- A nested `def` no longer inherits an enclosing name its **own signature shadows**. This hole
  pre-existed; putting parameter names into the map for the first time is what makes it
  reachable, and `out`/`path`/`dest` repeat across nested defs throughout this tree. Closed in the
  same change rather than left for the defect to find.

## Result, against the predictions

| # | Predicted | Actual | |
|---|---|---|---|
| P1 | raw set grows by 20 (accept 12–28) | **+9** | **FALSIFIED** |
| P2 | `site/data/capabilities_door.json` and `docs/observability/cohort_coverage_realised.json` both added | both added | held |
| P3 | shadow-stripping removes 0 existing paths | 0 removed | held |
| P4 | at most one new `WRITTEN_BUT_NOT_REPRODUCIBLE` carve-out | **three** | **FALSIFIED** |
| P5 | every added path attributable; none a path the module only reads | 9 of 9 attributed | held |

155 → 164 raw; 151 → 157 offered, after three carve-outs.

**Why P1 was wrong, and it is the more useful half.** I counted the *def* population (36) and
predicted from it, when the quantity is the *incremental path* population. Most of the 36 default
to `None`, resolve outside the repo, or name a constant the oracle already reached at module scope
— five of them default to `MATURITY_MAP_YAML`, which was already in the set and already carved
out. **A count of the sites a mechanism touches is not a count of what it adds**, and the two were
conflated here in the one place this project keeps being expensive: before dividing or
differencing, say what each number counts.

**Why P4 was wrong.** Three of nine are read-modify-rewrite of an accumulated record — a higher
proportion than the helper frame's two in eight, and in hindsight predictable in the opposite
direction from the one I guessed: **a default is how a module spells "the one place I keep my
running record"**, so the door that finds defaults finds disproportionately many of them.

## The nine, attributed

Every one is a `def` whose signature default names exactly the added path, and whose body writes
that parameter. Each is a path `origin_reconcile` will now advise REVERT on, so each was read.

| Added path | `def` | default |
|---|---|---|
| `site/data/capabilities_door.json` | `tools/generate_capabilities_door.generate` | `OUT_PATH` |
| `site/data/knowledge_review.json` | `tools/generate_knowledge_review.generate` | `OUT` |
| `site/state/frozen_policy_baseline.json` | `tools/run_frozen_baseline.generate` | `OUTPUT_PATH` |
| `docs/observability/cohort_coverage_realised.json` | `tools/generate_cohort_coverage.write_artifact` | `_ARTIFACT_PATH` |
| `docs/observability/substring_source_scan_baseline.json` | `tools/substring_source_scan_census.freeze` | `BASELINE_PATH` |
| `sim/weather_cells/occupied_land_cells.csv` | `simulation/weather_cell_siting._write_land_cells` | `LAND_CELLS` |
| `docs/design/visited_corner_ledger.json` | `tools/space_filling_sample.record_visit` | `LEDGER` |
| `docs/observability/edge_traffic.jsonl` | `tools/edge_traffic_capture.append` | `OUT` |
| `docs/market_research/haduk_grid_pull_receipt.json` | `tools/fetch_haduk_grid.write_receipt` | `RECEIPT` |

The first six are whole rewrites from tree-derived inputs: photographs of a run, and a revert
costs nothing a re-run cannot make again. **The last three are carved out.** Each reads what is on
disk, merges one run's contribution and writes the whole back — an append wearing a rewrite's
clothes, which `WRITING_MODE_CHARS` cannot see. The corner ledger's own docstring says coverage is
a property of the ENSEMBLE of runs; the traffic capture accumulates hourly rows from an external
feed a re-run cannot re-observe; the receipt's docstring says a death mid-write must cost "the
newest checkpoint and never the record of the 10 GB already bought", and a REVERT costs exactly
that — with no route from here to buy it again.

## What is still out, and the one that matters

`PublishStepLedger.write(self, path=None)` falls back to
`self.project_dir / "site" / "data" / "publish_steps.json"`, and
`background/process_run_complete.py:4525` calls it bare as `_ledger.write()`. So
**`site/data/publish_steps.json` is a real generated artefact the oracle still misses** — and it is
missed for a reason neither the item's premise nor this change names: the destination is built
from an **instance attribute**, not from a parameter or a module constant.

That is the door the `self._write(...)` search should have found. It needs `self.<attr>` resolved
from `__init__`, which is a different mechanism from parameter binding and is not half-done here.
Also still out and on purpose: a helper in another module; two frames of reach.

All degrade the same safe way — the path stays classified authored, so the consumer offers a
landing where a revert would have done, rather than the reverse.

## What is next

1. **`self.<attr>` destinations, resolved from `__init__`.** One live instance
   (`site/data/publish_steps.json`) is one more than the door this item named had, and the
   population is unmeasured — the scan for it is ten minutes.
2. **The premise chain, not the instance.** This item's premise was a sentence in a docstring that
   nobody had asked the tree about. It was written in good faith by the lane that landed
   `a2d130044` and repeated verbatim into a Lane 0 draw. A "still out" list is a *prediction about
   the tree*, and nothing in this repository re-asks one. Worth a line in the next orientation:
   where else does a docstring's gap list steer a draw?
