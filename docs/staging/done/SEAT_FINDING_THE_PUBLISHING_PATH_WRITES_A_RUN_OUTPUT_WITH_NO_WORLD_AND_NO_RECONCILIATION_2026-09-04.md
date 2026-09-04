# [SEAT FINDING] The publish path writes a run output that says neither which world it ran in nor whether it adds up

**Severity:** LATENT (the refusal has never fired on 131 artefacts; the provenance half is live and
wrong on the page today)
**Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted
**Found:** 2026-09-04, following the thread from the director's standing instruction to attribute a
moved figure rather than offer to: *"Finding out why a figure moved is never something to ask me
about. It's the job."* Net margin fell **£149,156 → £138,153** across the 2026-09-03 publish
outage. Attributing it meant asking what a run output records about the world that produced it. The
answer is nothing, and the reason is one function with two writers.

## Class registration

Belongs to `no_caller_and_never_runs` — the cause is a control whose only caller is off the publish
path. Its consequence lands in `figures_on_a_superseded_clock`, cross-referenced rather than
double-filed: the page's `git_commit` is not the commit the figures were made at.

## One function, two writers, and only one of them was doing the work

A published run takes exactly this path:

```
background/sim_runner.py
  └─ python3 -m tools.run_annual_report --save-json ... --output ...
       └─ tools/run_annual_report.main()
            └─ args.save_json.write_text(json.dumps(extract_report_data(raw_output)))
```

`tools/run_annual_report.save_run_output_json()` — which reconciles and stamps — is reached from
**`tools/run_phase4c_pipeline.py` only**, and nothing on the publish path calls it. So on every
published run:

| what `save_run_output_json` does | what the publish path did |
|---|---|
| `reconcile_published_run_output(data)`, raising on failure | never ran |
| `data["_cache_meta"] = {git_commit, generated_at_utc}` | never written |

Measured, not inferred: **`_cache_meta` is absent from all 131 September run outputs** in
`docs/reports/`.

## The reconciliation half: a control that could not fire

The refusal carries its own account of why it must raise — *"It RAISES rather than warning. A run
that cannot state a consistent treasury has nothing publishable to say about its own solvency, and
the failure mode this replaces was two silent days."* It was written on 2026-08-28 after
`starting_treasury_gbp + total_net_gbp` was published £39,962.17 above `final_treasury_gbp` for two
days. It has never executed against a published artefact.

**And it would have caught nothing.** Applying `reconcile_published_run_output` retrospectively to
all 131 September run outputs: **0 refused.** This is a control that could not fire, not a defect it
failed to catch, and grading it the other way would be the flattering read. That is why the severity
is LATENT.

The author's comment reasoned carefully about *where* the check belonged — "the check lives HERE and
not in `saas/reporting/annual_report.py` because `saas/` never imports `simulation/`" — and put it
in the function the publisher does not call. The wall reasoning was right; the caller was never
checked.

## The provenance half: this one is live, and it is on the page now

`tools/generate_dashboard_data.py` reads:

```python
git_commit = cache_meta.get("git_commit") or _git_head() or "unknown"
```

With the first branch dead, **the site's published provenance names the commit HEAD happened to be
at when the DASHBOARD was generated, not the commit the RUN executed at.** Checked today:

- `site/data/dashboard.json` → `meta.git_commit = cbbeb99d38839b9256a93bd0b06a9a0a46638856`
- `ls docs/reports/run_output_cbbeb99d3*.json` → **no such file.** No simulation run has ever been
  produced at that commit.

The comment above that line says it exists to stop exactly this: *"Real HEAD, or the honest string
'unknown' — never a filename fragment dressed as a SHA."* It closed one fail-open and the dead
branch above it opened a quieter one, because **a real SHA belonging to a different thing satisfies
every presence check exactly as well as a fake one did.**

Two other consumers take their fallback silently for the same reason:
`tools/generate_customer_sample.py` (falls back to parsing the filename — the very thing the
dashboard comment forbids) and `saas/reporting/annual_report.py` (its staleness warning is keyed to
`cached_commit and ...`, so an absent stamp means the warning can never print).

## The world half: why this was the thread worth following

`simulation.departure_level_anchor.world_level_identity()` was built on 2026-09-03 (`dda5a27b2`) for
one question — *is the world this was measured in still the world?* — with its own docstring saying
*"every control in this area asks whether a figure is arithmetically right and none asked whether
its world still existed."* It was wired to the value-arms surface and to the fit tooling. **The
headline figures never got it.**

**A concurrent lane found the other end of this today.**
`SEAT_FINDING_THE_TWO_AUC_NULLS_STATE_A_RESOLVED_DIRECTION_FROM_A_RUN_THAT_NAMES_NO_WORLD_2026-09-04.md`
(G_data_learning, BLOCKING, repaired in the commit that filed it) is the same absence seen from the
page: `/capabilities/` lists two runs under `runs_that_cannot_name_their_world` and then reads a
resolved direction off one of them. That finding had to key its guard to *"does this block read a
direction off a run whose world is unknown"* — a question the artefacts could not answer about
themselves. This one supplies the answer at the source, so a future guard can ask the run instead of
inferring from a list. Filed separately because the subjects are disjoint: that one is a published
sentence on one page, this one is every run output written since the stamp existed.

The cost is the move this finding started from. Between the two publishes either side of the outage
the departure anchor was re-fitted twice (`712ae5323`, `8242dcc25`), and those two commits are the
**only** changes to `simulation/`, `company/` or `saas/` in eighty commits. Net margin fell 7.4% and
nothing on the publish path could say the world had moved underneath it. A commit hash cannot answer
it — it moves for every reason. A timestamp cannot answer it — two runs an hour apart either side of
a re-fit are different worlds. The digest answers it about the quantity.

## The repair

One function, `tools/run_annual_report.reconcile_and_stamp()`, used by both writers. It refuses
before anything is written, stamps the commit and the timestamp, and adds `world_level` — the
digest, the anchors, and a named reason if the accessor cannot answer.

Control: `tests/tools/test_the_published_run_output_names_its_world_and_adds_up.py`. It runs
`main()` with the world stubbed and reads what lands on disk, rather than asserting that a function
is *named* — a control that asserts a call is present cannot tell whether it was obeyed, which is
the defect being repaired restated as a test.

Mutation-proved, each leg against its own defect:

| mutation | legs that died |
|---|---|
| M1 `main()` writes the raw reduction again (the exact pre-repair line) | all 3 |
| M2 stamp kept, `world_level` dropped | 2 (world, digest) |
| M3 digest pinned to today's literal | 1 (digest) |
| M4 the `raise` downgraded to a warning | 1 (fail-closed) |

M1 killing all three is the point: it is the state the tree was in this morning.

## What this does NOT repair

`_run_fingerprint` in `background/process_run_complete.py` keys the change-detection gate on
headline figures and the UTC date, and not on the world. A re-fit that moved the world without
moving those figures enough to break the fingerprint would still be skipped as "pure burn" and
never publish its own disclosure. Recorded here rather than fixed, because the stamp has to exist
before anything can key to it, and it did not exist until this commit.
