# The publish surface gate — the content publish stops being gated on repo hygiene

**Status:** gate BUILT and R15-proven (2026-08-17); WIRING pending, see §5.
**Provenance:** director ruling, 2026-08-17 console, approving the R3 redesign proposed after the
three-day content freeze (2026-08-14T07:04Z → 2026-08-17T10:50Z).

## 1. The ruling

> *"Eliminate the whole-repo hook from the content publish path — on one condition: whatever
> replaces it takes as its subject exactly the surfaces that ship, is provably failable, and fails
> closed if it can't run."*

Three clauses. They are the acceptance criteria and they are each mechanised, not asserted:

| Clause | Mechanism | Proof |
|---|---|---|
| Subject = what ships | scope derived from the STAGED shipping paths; `subject_is_the_commits_tree()` refuses on index/worktree drift | `test_a_staged_surface_modified_after_staging_is_refused_as_unjudgeable` |
| Provably failable | a corrupted published figure turns the derived consumer red | `test_a_red_surface_test_refuses_the_publish`, preceded by `test_the_honest_surface_is_green` |
| Fails closed | every unavailability returns `EXIT_CANNOT_RUN` (2), distinct from red (1) | five refusal tests, each driven by removing what the branch depends on |

## 2. Why the old arrangement froze the site for three days

`git_commit_push` committed with a bare `git commit`, firing the whole-repo hook chain.
`pre_commit_test_gate.py` maps STAGED PATHS to tests — and **the publish staged far more than it
shipped**: `docs/design/maturity_map.yaml` (the pre-gate atom_status inbox fold, `git add -A`), the
derived design artefacts, and `docs/staging/done/`. Measured on the real index, the map's derived
answer alone is 50 test files; the whole publish selected ~780.

So the content publish was gated on the repo's **design hygiene**. Of the six reds that held it:

- 2 — an atom mint's `notes_rehomed:` declaration disagreeing with a store file
- 1 — a stale design projection (`BLOCKED_ATOM_VISIBILITY.md`)
- 2 — a lint import-sort ratchet, whose own repair had been staged-and-never-committed since the
  exact instant the freeze began
- 1 — a control that went red *because the map improved*

**Not one was about whether the published figures were correct.** The site was three days stale
because a YAML declaration the reader never sees disagreed with a YAML file the reader never sees.

## 3. The orphan this closes, which was already written down

`pre_commit_test_gate.PUBLISHED_OUTPUT_ROOTS = ("site/", "docs/reports/", "docs/status/")` skips
test derivation for those roots, commented *"regenerated output, gated elsewhere"*.

- `site/` — really is gated elsewhere (`tools/site_lane_gate.py`, broad trigger on `site/data/**`)
- `docs/reports/` — **gated by nothing**
- `docs/status/` — gated only by `status_honesty`, which checks the LATEST.md header narrative

Two of the three shipping roots had no "elsewhere". That is an R11 orphan transition: an exclusion
whose promised counterpart does not exist. `PUBLISH_SURFACE_ROOTS` is asserted by
`test_this_gate_covers_every_root_the_sibling_gate_excludes_from_derivation` to cover every
excluded root, so adding a sixth to that tuple without adding it here now fails at commit time.

## 4. What the gate is

`tools/publish_surface_gate.py`. Scope is **derived, never listed** — the repo is asked which of
its own `tests/**/test_*.py` files NAME each staged shipping path, by full path and by basename
(unioned, for the same reason the sibling gate unions them). On a full publish that is ~62 test
files against ~780 today.

A **floor** of five surface-integrity controls always runs (`SURFACE_FLOOR_TESTS`): provenance
reality, publish freshness, website integrity, site reachability. A missing floor control is a
REFUSAL — an unavailable check is a failed check.

The **vacuity guard** tests the DERIVED half only. The first draft unioned the floor in before
asking whether the scope was empty, which made the refusal unreachable code pretending to be a
control — the exact R15 pattern, authored by accident inside the gate written to honour R15. It is
recorded here because the class matters more than the instance: *a refusal that cannot be reached
is a control that cannot fail.*

**Deliberate asymmetry** with `data_surface_tests`: there, an erroring `git grep` returns nothing
and is bounded by other surfaces. Here the derivation is the only thing between a bad figure and
the public site, so it has **no fail-open branch at all**.

## 5. Wiring — what remains, and why it is a separate step

The gate does not yet sit in the publish path. Landing it first, proven, is deliberate: the live
publish path had just been unwedged after three days and must not be the place a new mechanism is
debugged.

The wiring has two halves, and the FIRST is the one that matters:

1. **Split the publish commit.** Content commit = shipping surfaces only. Bookkeeping commit = the
   map fold, the derived design artefacts, the done-markers — with the normal whole-repo gate,
   unchanged. This alone removes the ~780→62 test load, because the load came entirely from the
   bookkeeping riding along.
2. **Route the content commit through `tools/surgical_land`**, so the hook runs in a clean extract
   of the tree the commit creates. `--no-verify` remains a WALL and is not used: the hook stays in
   the path, and `pre_commit_test_gate` learns to delegate to this gate when every staged path is
   a shipping surface.

## 6. What this deliberately does NOT weaken

The safety-control set, the level surface, the store contract, the lint ratchets and the design
projections still gate every commit that stages a code or design path — **including the
publisher's own bookkeeping commit**. Repo hygiene is no less gated than it was. What changes is
that shipping correct figures to a reader is no longer contingent on it.
