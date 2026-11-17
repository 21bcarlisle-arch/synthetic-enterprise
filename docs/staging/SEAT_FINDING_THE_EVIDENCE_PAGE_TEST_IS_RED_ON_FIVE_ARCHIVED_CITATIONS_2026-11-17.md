**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 4 · **Atom:** `unminted`

# The evidence-page test is red at origin because the maturity map still cites five modules that were archived (2026-11-17)

`tests/tools/test_evidence_pages.py::test_unresolved_citations_are_the_known_set_and_no_more` fails at
origin/main (a625b6aec0, checked from an isolated worktree). Five citations in the published evidence
payload are MISSING and are not in its `KNOWN_UNRESOLVED_CITATIONS` ratchet:

- `company/crm/decarb_recommender.py`, `company/crm/home_registry.py`, `company/crm/onboarding_journey.py`.
  These were moved to `archive/unhooked_supplier/` by archive increment 4b (6b70382ded).
- `company/market/tariff_benchmarking.py`, `company/pricing/renewal_pricing_engine.py`. These are also
  under `archive/unhooked_supplier/` now.

**Why this matters now.** The commit gate's new assembled-path route
(`tools/assembled_path_readers.py`) found that `tools/published_feed_regeneration_check.py` reads
`docs/observability/*.json` through `PROJECT / "docs" / "observability" / f"{name}.json"`. That module's
importers include this test. With the route in force, every daemon commit of
`docs/observability/open_question_register.json` (17 in the last 7 days) would be refused on this red.
So `ASSEMBLED_ROUTE_EXCLUDED = ("docs/observability/",)` in `tools/pre_commit_test_gate.py` keeps that
one directory off the route until this test is green.

**What done means.** The map rows that cite the five paths either cite live evidence or the five paths
are pinned in the ratchet with the reason, which is the precedent the test sets for deleted site doors.
Re-pointing them at `archive/` would be a false citation, because archived code is not evidence of a live
level. Then delete `ASSEMBLED_ROUTE_EXCLUDED` and its test leg.

Not fixed here: the map rows belong to the level lane, and choosing between re-citing and pinning is a
judgement about those atoms' levels.

## Resolved (2026-11-17, delivery seat)

The five are cited by the rehomed evidence records, not by the map rows themselves:
`docs/design/simplifications/C2_discovery_through_interfaces.yaml` (the trio, as C2's L2 evidence) and
`B4_competitor_field.yaml` (the pair, where the record itself calls them "orphaned"). C2's `file_scope`
already names the archive paths. Regenerating `site/data/evidence.json` does not change the five
MISSING, so the red does not come from a stale payload.

Pinned in `KNOWN_UNRESOLVED_CITATIONS` with that reason, which follows the deleted-door precedent.
`ASSEMBLED_ROUTE_EXCLUDED` is deleted. Its test leg is replaced by a positive control: a
`docs/observability/` commit must select `tools/published_feed_regeneration_check.py`. Putting the
exclusion back makes that control fail (mutation checked).

**Still open, for the level lane:** C2_discovery_through_interfaces sits at L2/L2, and the evidence
for that L2 is code now archived as unhooked. Whether C2 holds L2 is a level judgement, and this
change does not make it.
