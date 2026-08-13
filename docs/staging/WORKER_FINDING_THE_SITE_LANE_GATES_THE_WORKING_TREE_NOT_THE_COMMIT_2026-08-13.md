# WORKER FINDING — the site lane gates the WORKING TREE, not the commit it is refusing

**Severity:** LATENT · **Lane:** H_harness
**Found:** 2026-08-13, during KNIFE3 step 26 (the `saas.demand_response` module move).
**Rank:** after the current KNIFE3 sequence; it blocks a lane, it does not corrupt one.

> **Severity header repaired 2026-08-13 (18th draw of `H_GAP_fabric_belief_truth_gap`).** This read
> `**Severity: HIGH**` — a word outside the `BLOCKING / LATENT / RECORDED` vocabulary, and in a
> format the parser cannot read either — so it classified UNCLASSIFIED, and an unclassified document
> holds *every* lane's level recording repo-wide. That is the filed one-typo-holds-every-lane class.
>
> **Disclosed because it unblocked the editor's own commit:** the H_GAP L2→L3 move was refused by
> the OPS11 rung naming this document. LATENT was not chosen to clear that path. It is what this
> document's own `Rank` line already says — *"it blocks a lane, it does not corrupt one"* — and
> `background.finding_severity.by_construction_evidence` returns `[]` on this text, i.e. nothing here
> claims an instrument or a published figure is wrong, which is the BLOCKING test. If a later reader
> judges the gate itself an instrument of this lane, raise it back to BLOCKING; the finding is
> unchanged and still open.

## The finding, in one sentence

`tools/surgical_land` rebuilds the tree the commit **would create** and runs the `tests/` gate against
it — but `tools/site_lane_gate.py::main` runs `pytest site/` with `cwd=ROOT`, which is the **real
working tree**, so a site-touching commit is refused for reds that belong to other lanes' uncommitted
state and are not in the change set at all.

## Evidence — observed, not inferred

`tools/site_lane_gate.py`:

```python
r = subprocess.run(
    [sys.executable, "-m", "pytest", *run_args, "-q", "--no-header", ...],
    cwd=str(ROOT),          # <-- the live repo, not the rebuilt tree
    env=_gitless_env(os.environ),
)
```

Compare the line the same run prints immediately above it, from the `tests/` half:

```
[test-gate] ✓ wall crossings reconcile at the tree this commit creates (13 live, 91 ruled)
```

One half says "the tree this commit creates". The other silently means "whatever is on disk right
now".

**Three reds refused KNIFE3 step 26's first landing. None of them was in its change set.**

| test | in a clean `HEAD` checkout | cause |
|---|---|---|
| `site/proof/test_predictions_ledger_can_fail.py::test_live_surface_renders_the_derived_headline` | **also fails** | pre-existing |
| `site/proof/test_predictions_ledger_can_fail.py::test_live_surface_states_the_horizon_and_names_the_stale_snapshot` | **also fails** | pre-existing |
| `site/proof/test_coupled_gaps_panel.py::test_R15_the_control_fires_on_the_pre_repair_depth_limit` | **passes** | another lane's uncommitted `docs/observability/coupled_gap_ledger.json` |

Baseline method (`observed-with-evidence`): `git archive HEAD | tar -x -C /tmp/headco`, then run the
three tests there — a clean HEAD checkout rather than the dirty shared tree, because a baseline taken
in the working tree blames your change for tree dirt.

The third one is the interesting one, and it is worth stating precisely because it looks like a
regression and is not. `_live_coupled_gaps()` reads `docs/observability/coupled_gap_ledger.json`,
which is **modified and uncommitted**. Diffing the `unreadable` set the control computes, HEAD vs
working tree, ten entries move and every one is `W2_11_payment_behaviour_source`:

```
- ...measures.ageing.mean_bucket_displacement.actual   | 1.741935
+ ...measures.ageing.mean_bucket_displacement.actual   | 0.75
- ...measures.arrears_view.unpursued_arrears_rate      | 0.580645
+ ...measures.arrears_view.unpursued_arrears_rate      | 0.25
```

which moves the control's pinned count **53 → 54**. No numeric *path* was added or removed (712 both
sides) — the **values** moved, so numbers that were previously readable elsewhere on the page no
longer are.

## Why this is HIGH and not a nuisance

**It converts every unrelated red into a repo-wide wedge, and it does so invisibly.** The site lane is
red at HEAD *today*. Any commit whose change set contains a `site/data/*` file or a `generate_*_data`
producer is therefore currently unlandable, for reasons its author cannot see in their own diff and
cannot fix without adopting someone else's in-flight work. That is the same shape as the publish-gate
wedge already on file (`CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md`), one lane over.

**It is also fail-open in the other direction, which is the worse half.** Because the suite runs
against the working tree, a site change that is *broken in the commit* but *green on disk* — because a
fixing edit is present but unstaged — passes the lane and lands red. The gate cannot tell the two
apart. R15's own vocabulary: the checked subject is not the subject the check is about.

Note the file is otherwise carefully R15-shaped — it refuses to run when `node` is absent rather than
letting the `.mjs` harnesses skip silently, on the explicit ground that "an unavailable check is a
FAILED check". The subject defect sits underneath that care, which is why it survived.

## The fix, recommended and named

Run the site lane in the **same rebuilt tree** the `tests/` gate already builds — pass that path down
as `cwd` instead of `ROOT`. `surgical_land` constructs it (`/tmp/wall-head-*/tree`); the site lane just
has to be told about it. That is one plumbing change, not a redesign, and it makes both halves of the
gate answer the same question.

**Its R15 control must be the mutation that is currently impossible:** stage a site fix, leave a
*breaking* edit unstaged in the working tree, and assert the lane still **passes** (it is judging the
commit); then stage the breaking edit and assert it **fails**. Today the first of those reds and the
second is indistinguishable from it — which is precisely the proof the control is about the wrong tree.

## What this finding does NOT claim

It does not claim the two pre-existing `predictions_ledger` reds are caused by this. They are separate,
they reproduce at clean HEAD, and they are about a stale `site/state/live_portfolio.json` snapshot
timestamp. They are named here only because they are what makes this defect *bite* right now.

## Owed, carried out of KNIFE3 step 26

Step 26 landed without two files, deliberately and stated in its commit message rather than smuggled,
because both are site-lane broad triggers and neither is load-bearing for the wall cut:

- `tools/generate_saas_coverage_data.py` — one path string, `saas/demand_response.py` →
  `simulation/demand_response.py`, stale from the moment the module moved.
- `site/data/saas_coverage.json` — the regenerated artefact (one field; `modules_exist` correctly
  reports `exists: true` at the new path).

Both are **present and correct in the working tree, unstaged**. That is the same orphaned-work shape
step 26 caught in step 25, so it is recorded here rather than trusted to memory: whoever repairs the
site lane should land these two with it. Until then the coverage map reports `exists: false` for one
module — cosmetic, self-healing on the next regeneration, and not a red.

## Related

- `CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md` — same class, adjacent lane.
- `CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md` — the step-25 orphan and the two files above.
