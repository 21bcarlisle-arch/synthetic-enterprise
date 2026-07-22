# C2_discovery_through_interfaces — HARDEN / red-team pass (2026-07-22)

Atom: `C2_discovery_through_interfaces` (lane=C_customer_ops, level_current=2, level_target=2, loop_stage=idle),
maturity_map.yaml ~line 213. Doc-only investigation. **No production code changed** (one scratch
mutation applied to `company/crm/home_registry.py` and immediately reverted — `git status` clean, verified).

Core law under test: the company/portal layer must discover a customer's physical-property truth
(EPC, floor area, bedrooms, tenure, solar/EV) through OBSERVABLE events, never a direct read of the
ground-truth record. Per C2's own module docstrings, the ground-truth property record lives in
`saas/property_model.py` / `saas/customers.py` (the customer roster carries the seeded true
`epc_rating`/`bedrooms`).

---

## 1. Exit tests — re-verified, they hold as written

**observed-with-evidence.** Ran the C2-backing tests:

```
$ python3 -m pytest tests/company/crm/test_c2_discovery_wired.py -q
.........                                                                [100%]
9 passed in 0.04s
```

The wired suite genuinely exercises the belief layer end-to-end across the seam: onboarding opens a
belief from signup disclosure at the right confidences (EPC always starts unconfirmed-default, never
known at signup), an EPC-lookup event arriving later upgrades confidence and changes the actual decarb
recommendation, and the consumer (`decarb_recommender.recommend_from_registry`) acts on the belief at
the confidence held, not on any "true" value. These are good behavioural tests of the mechanism.

**The wall-specific guards are three import-text scans** (observed-with-evidence, source read):
- `test_property_discovery.py::test_property_discovery_never_imports_saas_ground_truth` — greps the
  module source text for `"saas.property_model"`, `"saas import"`, `"import sim"`, `"import simulation"`.
- `test_c2_discovery_wired.py::test_decarb_recommender_imports_no_ground_truth` — scans **import lines
  only** of `decarb_recommender` for `saas`/`simulation`/`from sim`/`import sim`.
- `test_c2_discovery_wired.py::test_onboarding_journey_imports_no_ground_truth` — same, for `onboarding_journey`.

**Coverage gap (inferred from the above, verified below):** of C2's five `file_scope` files, only
THREE have any wall guard, and only `property_discovery.py` scans its whole source. `home_registry.py`
and `property_model.py` — the files that actually CONSTRUCT and STORE the belief — have **no wall test
of any kind.** The two import-line scans (decarb/onboarding) do not see reads reached via an
already-imported company module.

---

## 2. R15 mutation test — the control does NOT fire (FAIL-SILENT / incomplete-coverage)

**Mutation (scratch, reverted):** in `home_registry.register_from_signup` — a file inside C2's
`file_scope` and the true construction point of the belief — I injected a raw ground-truth read that
bypasses the discovery events entirely:

```python
from saas.property_model import build_properties   # ground-truth read
from saas.customers import CUSTOMERS
gt = build_properties(CUSTOMERS)
if account_id in gt:
    prop = replace(prop, epc_rating=EPCRating(gt[account_id]["epc_rating"]))
```

This is the exact defect C2 exists to prevent: the company reading the household's true EPC directly
instead of discovering it via an EPC-register lookup event.

**Result — NOT CAUGHT (observed-with-evidence):**

```
$ python3 -m pytest tests/company/crm/test_c2_discovery_wired.py \
      tests/company/crm/test_property_discovery.py \
      tests/company/crm/test_home_registry.py -q
52 passed in 0.09s

$ python3 -m tools.epistemic_verifier company/crm/home_registry.py
PASS
Summary: Scanned 488 company/ + saas/ file(s). No epistemic barrier violations found.

$ python3 -m pytest tests/ -k "home_registry or property_model or discovery or epistemic or c2 or wall" -q
258 passed, 19329 deselected
```

Every C2 test, the whole `tests/company/crm/` suite, the epistemic_verifier, and 258 wall-adjacent
tests across the repo **all stayed green** with a live raw ground-truth read in the belief-construction
path. The control does not fire on its own named defect.

**R15 pattern exhibited:** FAIL-SILENT / structural-coverage-gap. The guard is not a tautology and is
not fail-open on empty input — it simply does not look where the defect lands. The three text-scans
watch three specific modules; the mutation lives in a fourth (`home_registry.py`) that no guard covers,
and it reaches ground truth through a fresh in-function import that the two import-*line* scans on the
OTHER modules never see.

---

## 3. Red-team of the invariants — accessor-enforced, NOT read-enforced

The suspected latent gap (from W4_1 HARDEN) is **confirmed as real.**

**The seam only guards ITSELF, not the wall.** `tools/epistemic_verifier.py`:
- `FORBIDDEN_SOURCES` (observed-with-evidence, lines 56-63) lists ONLY `^from sim.` / `^import sim.` /
  `^from simulation.` / `^import simulation.`. **`saas` is not forbidden.**
- `COMPANY_PATHS = ["company/", "saas/"]` (line 75) — the verifier treats `saas/` as being on the SAME
  (company) side of the wall as `company/`, and scans both only for `sim`/`simulation` imports.

So the project-wide mechanised control has NO concept that `saas/property_model.py` is ground truth for
the property record. C2's wall (company ↛ saas property ground truth) is invisible to it. The wall is
therefore **accessor-enforced only**: `sim_interface.py` happens to expose no property observables, and
convention says "don't read saas ground truth" — but nothing structurally stops a `company/` module
importing `saas.property_model` / `saas.customers` and reading a raw field. The mutation in §2 proves it.

**It is already happening in a sibling file (observed-with-evidence).** Grep of `company/` for direct
ground-truth imports:

```
company/portal/app.py:52:  from saas.customers import CUSTOMERS
company/portal/app.py:49:  from saas.capital.solvency import compute_solvency_signal, MCR_FLOOR_GBP_PER_CUSTOMER
```

The portal reads `saas.customers.CUSTOMERS` directly — this is exactly the "portal still reads
saas.customers.CUSTOMERS directly" gap the atom's own 2026-07-11 M3 DISCOVER note flagged as still live
(Q4/Q5/Q6). `company/portal/app.py` is NOT in C2's `file_scope`, so C2's guards would never see it even
if they scanned imports properly. The belief layer (`home_registry`) is a clean island; the actual
customer-facing portal still bypasses it.

**Is there a scan for the bypass class? No — only convention.** No test scans `company/` broadly for
`saas.property_model` / `saas.customers` / `build_properties` reads (grep of `tests/` for those symbols
returns only the sim-side tests that legitimately use them plus C2's own three narrow scans). The
class-level guard R10 would require does not exist.

---

## 4. Recommendation — C2 does NOT legitimately hold at L2; QUEUE a finding

C2's *mechanism* is real, well-designed, and its behavioural tests are honest. But under R15, a control
is evidence for a level only if a mutation proves it fires on its own named defect — and here it does
not. The wall that names the atom ("...through observable interfaces, **not a direct read**") is
convention + three narrow import-text scans, not a structural or class-level guard; the defect it
exists to catch passes the entire suite silently, and a real instance of that defect already exists
uncaught in `company/portal/app.py`.

**QUEUE (do not fix on sight) — proposed finding/atom:**

> **`C2_WALL_READ_ENFORCEMENT_GAP`** (HARDEN finding on C2) — The C2 property-discovery wall is
> accessor-enforced, not read-enforced. Extend the invariant library so the CLASS fails automatically
> (R10): a test/verifier check that scans all `company/` modules (at minimum C2's full `file_scope`,
> ideally company-wide with a curated allowlist) for any read of the ground-truth property record —
> imports of `saas.property_model` / `saas.customers` / calls to `build_properties()` — reaching the
> belief layer. Two concrete sub-items: (a) `home_registry.py` and `property_model.py` have no wall
> test at all — add one; (b) resolve the definitional conflict that `epistemic_verifier` classifies
> `saas/` as company-side while C2 treats `saas/property_model.py` as ground truth (either add the
> property record to a forbidden-source set for the belief layer, or move/relabel the ground-truth
> record). Until this lands, C2 is a mechanism-built L1½ resting on a control that cannot fail; the L2
> claim rests on theatre for the wall dimension specifically.

Note (LAW/queue discipline): this is a QUEUED finding, not a fix. The mutation was scratch and reverted;
no production code was changed by this pass.
