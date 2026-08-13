# FINDING — a coupling stated in a comment as fact is false a quarter of the time, and nothing enforces it

**Severity:** LATENT · **Lane:** H_harness · **Disposition:** QUEUED (not fixed on sight)

**Atom:** `D35_the_render_site_sweep_stops_at_this_processs_edge` (LANE 3 idle draw, DISCOVER/FRAME, 2026-08-13)
**Class:** a load-bearing sentence asserts a coupling between two published artefacts that no
mechanism maintains and no control checks

Full derivation and every number: `docs/design/simplifications/D35_the_render_site_sweep_stops_at_this_processs_edge.yaml`.

## The sentence

`background/gap_ledger_reconciler.py`, in the design comment that justifies why that module grades
the COMMITTED ledger rather than the working-tree one:

> The door renders a COMMITTED artefact: `site/data/proof.json` is built from the ledger and both
> are committed and pushed.

The comment is right about its own subject — grading the working tree was fail-open, and reading
HEAD fixed it. What is asserted in passing, and is load-bearing for anyone reading this file as
authority on the seam, is the *and*: that the two published artefacts move together.

## Observed, with evidence

Measured 2026-08-13. For each of the 66 commits since 2026-08-06 touching either
`docs/observability/coupled_gap_ledger.json` or `site/data/proof.json`, both blobs were read **as
committed at that commit** and every pair compared by `repr` — i.e. what a reader fetching that
published tree would have got, against the ledger of record sitting beside it.

```
DIVERGING COMMITS: 17 of 66   (26%)
```

Longest continuous divergence run per pair over that commit series (commit-granularity, so each is
a LOWER bound on wall-clock):

| pair | runs | worst |
|---|---|---|
| `W2_11_payment_behaviour_source` | 2 | **33.4h** |
| `W1_11_fabric_physics_core` | 1 | 7.7h |
| `W1_12_premise_trace_generator` | 3 | 7.7h |
| `WORLD_recontracting_relationship_start` | 1 | 3.8h |
| `W2_5_life_event_stream` | 1 | 2.0h |
| `W2_8_self_rationing` | 1 | 0.9h |

Two of the 17 are a worse shape than a stale value. At `677a7f7bf` and `7d01fffba`,
`WORLD_recontracting_relationship_start` is a measured ledger row **absent from the door's pair
list entirely** — the panel published `pair_count: 13` against a 14-row ledger.

**Current state is clean** (`observed-with-evidence`): at HEAD, at `origin/main` and in the working
tree, all 14 pairs agree bit-for-bit. This is a base rate, not a live incident.

**Nothing checks it.** Six modules mention both `proof.json` and the gap ledger
(`tools/generate_proof_data.py`, `background/gap_ledger_reconciler.py`, `background/gap_metric.py`,
`background/supervisor.py`, `tests/test_gap_metric_misapplication_class.py`,
`tests/tools/test_site_lane_gate.py`); in every one the co-occurrence is a comment, a docstring or a
path-routing string. No module opens the published door and compares its value with the ledger.

## Why it is LATENT and not BLOCKING

It does not invalidate the reconciler's verdict. That module grades ledger-vs-HEAD-**code** drift
(has the producing tool moved since the reading) and never reads a door value, so its output is not
computed from the false premise. No published figure is currently wrong. What is wrong is a sentence
that will be read as establishing a guarantee, in the file most likely to be treated as authority on
this seam — while the guarantee is a publish-ordering coincidence that failed 17 times in a week.

## What it does NOT license

It does not license a hard ledger-vs-door gate. Landed hard against this history such a control
would have redded roughly one publishing commit in four, none of them a defect in the thing being
gated — the gate-wedging class this repo already has memory of. The disposition belongs to D35's
published-bytes stage, which is specified REPORTED-first for exactly this reason, and which now has
this census as the fixture it should reproduce. Two statuses, not one: a **set** comparison (the
absent-row failure above, which a value-only check scores clean) before a **value** comparison.

The minimal repair to the sentence itself is to state the coupling as what it is — an ordering the
publish cycle happens to produce and nothing enforces — with the measured rate beside it, so the
next reader does not build on it as a guarantee.

## Provenance

`tools/couple_w2_11_d5.py` and its test are modified-uncommitted in the shared tree by another lane,
so all source claims here are read from `git show HEAD:`. No published number was moved, nothing was
tuned, and nothing in any atom's `file_scope` was edited (R12).
