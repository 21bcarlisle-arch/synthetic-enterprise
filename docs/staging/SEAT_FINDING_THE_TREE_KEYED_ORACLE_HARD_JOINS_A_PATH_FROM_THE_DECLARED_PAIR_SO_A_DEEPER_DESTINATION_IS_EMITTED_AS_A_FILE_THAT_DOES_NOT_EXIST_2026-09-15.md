**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — split out of `generated-tree-declarations-are-exactly-two-segments-so-a-deeper-or-shallower-generated-tree-cannot-be-expressed`)

# The tree-keyed oracle hard-joins the path from the DECLARED prefix, not from what the module wrote — so a deeper destination is emitted as a file that does not exist, and a cross-product is emitted for two trees named in one assignment

**Filed 2026-09-15, delivery seat.** Found while measuring the depth-2 declaration limit; predicted
in advance as Q4 of
`docs/staging/records/PREREG_WHAT_THE_DEPTH_TWO_SHAPE_OF_A_GENERATED_TREE_DECLARATION_EXCLUDES_2026-09-15.md`,
including the instance, and **filed separately rather than folded into that repair** — they have
different causes, and a reader who saw the declaration generalised must not conclude this was fixed
with it. It was not.

---

## 1. The mechanism

`tools/file_scope_generated_paths.generated_artefacts()` decides by **membership** and then builds
the path by **hard-joining the declared prefix** to any artefact-suffixed constant in the same
assignment:

```python
for segs in GENERATED_TREES:
    if all(seg in parts for seg in segs):
        prefix = "/".join(segs)
        found.update(f"{prefix}/{s}" for s in parts if s.endswith(ARTEFACT_SUFFIXES))
```

`parts` is every string constant in one assignment, **unordered** — it comes from `ast.walk`, which
is breadth-first over the `/`-chain and does not preserve source order. So the join cannot use what
the module actually wrote; it uses what was declared. Two consequences, and neither is the
expressiveness limit:

**(a) A DEEPER destination is flattened.** An intermediate directory segment carries no artefact
suffix, so it is dropped from the join and the emitted path skips it.

**(b) TWO declared trees named in ONE assignment emit the CROSS PRODUCT.** Every artefact name in
the assignment is emitted under *both* prefixes, whichever tree each one actually belongs to.

## 2. The count

Seven assignment sites in the scanned trees satisfy a declared prefix while holding a directory
segment the join drops, or holding two declared prefixes at once:

| site | prefix matched | segment dropped | artefact names in scope |
|---|---|---|---|
| `simulation/premise_population.py:1189` | `docs/observability` | `scale_probe_10k` | `report.json` |
| `tools/mirror_github_pages.py:22` | `site/data` | `state` (×3) | 4 names, emitted under **both** trees |
| `tools/mirror_github_pages.py:22` | `site/state` | `data` | same 4 names, again |
| `tools/generate_grid_intensity_feed.py:101` | `site/data` | `market_data`, `docs` | `explore_hh_days.json`, `consumption_feed.json` |
| `tools/generate_grid_intensity_feed.py:101` | `docs/market_data` | `data`, `site` | the same two, again |
| `tools/couple_value_based_pricing.py:499` | `docs/reports` | `2026` | `run_output_*.json` |
| `tools/r1_inference_ceiling.py:182` | `docs/reports` | `latest` | `run_output_*.json` |

The named instance is confirmed: `docs/observability/report.json` is in the oracle and is **not a
file**. So are `site/data/sim_data.json`, `site/data/billing_ledger.json`,
`site/data/population_anchoring.json`, `site/data/consumption_feed.json`,
`docs/market_data/explore_hh_days.json`, `docs/reports/ledger_latest.json` and
`docs/reports/run_output_*.json` — the last of which is a glob pattern being carried as if it were
a path.

**`generated_artefacts()` holds 222 members and 55 are not on disk.** That number is *not* the
fabrication count and is deliberately not reported as one: most of the 55 are gitignored state
files (`docs/observability/.rate_limits.json` and thirty siblings) that legitimately do not exist in
a fresh worktree. "Not on disk" is a noisy proxy; the seven sites above are the measured class.

## 3. What it costs, and what it does not

**It cannot move the commit gate, and that is established rather than hoped.** `offends()` decides
a `file_scope` entry by tree PREFIX, and every member this function emits is under a declared
prefix by construction — so membership is SUBSUMED and `gate_violations()` is byte-identical
whatever this set contains. `test_the_gate_half_is_SUBSUMED_by_the_prefix_test` already holds that.

**The consumer that pays is `origin_reconcile._split_generated`**, which reads exact membership and
whose remedy for a generated path is `git show HEAD:<path> > <path>`. Two distinct harms:

- **A fabricated member is inert but misleading.** A path that does not exist never arrives at the
  reconciler, so no lane's work is reverted by it today. It is dead weight that makes the oracle
  look wider than it is — and it would stop being inert the moment anything created a real file at
  that name. `site/data/consumption_feed.json` and `site/data/billing_ledger.json` are plausible
  names for real future artefacts in a tree that is actively generated into.
- **The MISSING half is the live one.** The flattening does not merely add a wrong path, it fails to
  add the right one. `docs/observability/scale_probe_10k/report.json` and
  `prediction_register.json` were in **neither** oracle, so the reconciler classified AO12's own
  output as somebody's work and led with how to LAND it. Declaring
  `("docs", "observability", "scale_probe_10k")` recovered the first; the second is still out,
  because `tools/scale_probe_10k.py` binds the directory and joins the filename in a *separate*
  expression, which no membership test over one assignment can see.

## 4. The fix this needs, and why it is not in that commit

The honest repair is to stop membership-testing and **reconstruct the path in order** from the
`/`-chain — which is exactly what `_static_paths` already does for the write-keyed oracle in the
same module. That would fix both halves at once: no flattening, no cross-product, and a destination
whose segments the module actually wrote.

It is not folded into the declaration change for two reasons, both of which are the project's own
rules rather than caution:

1. **Attribution.** The declaration change is coverage-preserving and measured to move the gate by
   zero. Rewriting the matcher in the same commit would change several things at once, and a
   green/green/red across three trees is not attribution.
2. **It is a different risk.** Ordered reconstruction makes the oracle *stricter*: paths currently
   emitted on a loose membership coincidence would disappear, and each disappearance is a path the
   reconciler starts offering a landing on. That needs its own prereg with the before/after
   membership diff, not a paragraph in someone else's.

**Prediction filed before that work, so it can refute me:** ordered reconstruction removes between
8 and 25 members from `generated_artefacts()` and adds between 1 and 4 (the nested destinations it
recovers, `scale_probe_10k/prediction_register.json` not among them — that one needs cross-expression
reach, which is a third thing again). `gate_violations()` stays empty throughout, because membership
is subsumed.

## 5. Why it was invisible for eight weeks

A grep for `scale_probe_10k` finds it in `simulation/premise_population.py` and in the two FROZEN
entries, and every one of those readings says the path is known to the system. It is: it is known to
the **gate**, by prefix. The oracle that the reconciler reads had never contained it, and nothing
anywhere prints the difference between "this prefix refuses your `file_scope`" and "this exact path
is in the generated set". **A grep for a name is blind to the mechanism** — the two oracles answer
different questions and only one of them was ever asked about this path.
