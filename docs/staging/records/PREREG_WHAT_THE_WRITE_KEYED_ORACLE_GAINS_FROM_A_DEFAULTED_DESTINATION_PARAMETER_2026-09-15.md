# PREREG — what the write-keyed oracle gains from following a DEFAULTED destination parameter

**Written 2026-09-15 by the delivery seat, BEFORE the post-change set was computed.** The
pre-change set was measured first and is stated below as the baseline; the prediction is about the
DELTA, whose answer was not known when this file was written.

Lane 0. Claim `the-write-keyed-oracle-cannot-follow-a-path-into-a-method`.

---

## Why this prereg is not about the thing the item asked for

The drawn item directed the seat to follow a path constant into a method called as
`self._write(...)` — named as "the largest door left open by the helper frame landed in
`a2d130044`". **That premise is measurably false in this tree**, and the measurement is cheap
enough that it is recorded here rather than argued:

| Question, asked over `tools/ background/ simulation/ saas/ company/` | Answer |
|---|---|
| Classes | 2,058 |
| Classes with a method whose scope contains a write destination | 7 |
| …of those 7, methods with a bindable parameter reaching the write | **2** (`PublishStepLedger.write`, `ObservableTrace.save`) |
| Call sites of the shape `self.<writer>(...)` anywhere in this tree | **0** |

Five of the seven are `str.replace(old, new)` matching `DESTINATION_ARG` — already documented in
the module as a filter-not-safety case, and they resolve to nothing.

So the `self._write(...)` frame would be machinery with no live instance: a control that cannot
fire, which this project's own rule forbids building. The door is recorded as measured-empty in
the module beside the claim that named it, rather than being built and left green forever.

**The door that IS open was found by the same sweep**, and it is larger than the helper frame's
eight: a destination parameter with a **default** that is a module-level path constant, written
when the caller passes nothing. `PublishStepLedger.write(self, path=None)` falls back to
`self.project_dir / "site" / "data" / "publish_steps.json"`; `background/process_run_complete.py`
calls it as bare `_ledger.write()`. 36 `def`s in the scanned trees write a parameter that has a
default; the defaults that resolve to a static path are the population under test.

---

## Baseline, measured before the change

- `_write_reached_paths()` — **155** repo-relative paths.
- `written_artefacts()` (after the `WRITTEN_BUT_NOT_REPRODUCIBLE` carve-out) — **151**.

Two spot checks confirming the door is open, both absent from the 155:
`site/data/capabilities_door.json` (`tools/generate_capabilities_door.generate(out=OUT_PATH)`) and
`docs/observability/cohort_coverage_realised.json`
(`tools/generate_cohort_coverage.write_artifact(path=_ARTIFACT_PATH)`).

## The change under test

1. A `def`'s parameter DEFAULT is resolved by `_static_paths` against what the `def` INHERITS
   (module scope for a module-level function; for a method, what the CLASS inherited — never the
   class body, which is the trap the module already names), and seeded as that parameter's value
   before the scope's own assignments are read.
2. A parameter REBOUND in the body is refused, for the same reason `_module_helpers` refuses one:
   after `path = DEFAULT_OTHER` the write no longer goes where the signature said.
3. A nested `def` no longer inherits an enclosing name its OWN signature shadows. This is a
   pre-existing hole that seeding parameter names makes reachable, so it is closed in the same
   change rather than left for the defect to find.

## Predictions, recorded before running it

| # | Prediction | Falsified by |
|---|---|---|
| P1 | The raw set grows by **20 paths, and I will accept 12–28**. | A delta outside 12–28. |
| P2 | `site/data/capabilities_door.json` and `docs/observability/cohort_coverage_realised.json` are both in the added set. | Either absent. |
| P3 | Leg 3 (shadow-stripping) removes **0** paths from the pre-change 155. | Any path present before and absent after that is not explained by leg 3 being right. |
| P4 | **At most one** addition needs a new `WRITTEN_BUT_NOT_REPRODUCIBLE` carve-out. `docs/design/maturity_map.yaml` is reached by five of the migration tools and is already carved out, so it does not count. | Two or more additions that a run cannot reproduce. |
| P5 | Every added path is attributable by reading the signature's default and one call site — **no addition is a path the module only reads**. | Any added path whose module never writes it. |

P5 is the one that matters. An addition is a path `origin_reconcile` will start advising REVERT
on, so a false positive costs a lane its work, while a miss costs a warning. If P5 fails the change
does not land.

## What done means

The added set is enumerated in the finding with, for each path, the `def` and the default that
reaches it. Not "the count went up".
