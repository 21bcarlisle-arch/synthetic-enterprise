# [WORKER-FINDING] The pre-commit test gate maps ZERO tests to a non-`.py` file, so behaviour-determining IaC commits untested (2026-08-09)

**Severity:** BLOCKING · **Lane:** H_harness

**Found during:** the second publish-wedge unwedge — *by causing it*. My own manifest change passed
the pre-commit gate and wedged the publish gate on the very next cycle.
**Disposition:** REPAIRED 2026-08-12. Was QUEUED — small, precise, with a working implementation to
borrow from.
**Discharged:** `tests/tools/test_pre_commit_test_gate.py::test_a_data_file_selects_the_tests_of_the_modules_that_READ_it__mutation_proof`, `tests/tools/test_pre_commit_test_gate.py::test_the_data_surface_reaches_the_wider_class_not_just_the_named_instance`, `tools/pre_commit_test_gate.py` — a staged non-Python file now selects the tests that name it plus the convention tests of the modules that read it, derived by asking the repo rather than by a sixth hand-kept surface list.

The named mutation is what proves it, run rather than reasoned: the wiring test was RED at the parent
commit with exactly the evidence below — a staged manifest selected the ten-file control set and never
`tests/background/test_process_reconciler.py` — and is green here. Four source mutations each red it:
deleting the branch, making the grep fail-silent, dropping the basename route, and emptying the
output-root exclusion.

**Discharged with one recorded limitation, not wholly repaired:** the publisher's own output roots are
excluded on measured cost (see *What was NOT closed*), which is the clause-2 "limitation explicitly
recorded and accepted", not a silent narrowing.

## Observed, with evidence

`tools/pre_commit_test_gate.py::tests_for()`:

```python
def tests_for(path: str) -> list[str]:
    p = Path(path)
    if p.suffix != ".py":
        return []
    ...
```

A changed non-`.py` file selects **no tests at all**. `background/process_manifest.yaml` is such a
file — and it is not incidental data. Its own header calls it *"the SINGLE authoritative manifest of
what SHOULD be running"*, the thing everything else DERIVES from, and the OPS1 design rule is that
**no behaviour-determining state may live outside the readable repo**. It is IaC by declaration.

`tests/background/test_process_reconciler.py` asserts **exact sets** computed from that file
(`test_systemd_owned_sessions_are_only_the_migrated_ones`, `test_startlist_is_enabled_dark_and_not_yet_migrated`).
So the manifest has real, tight test coverage that the gate will never select when the manifest is
what changed.

**The two selections, same session, as the discriminator:**

| commit | staged | gate selected |
|---|---|---|
| `6fb27763f` (changed `process_manifest.yaml`) | manifest + 7 `.py`/`.md` | 12 files — **`test_process_reconciler.py` absent** |
| `bafcfbfef` (changed `test_process_reconciler.py`) | that test file | 10 files — **`test_process_reconciler.py` present** |

The gate went green on the first, and the publish gate went red on it at 12:22 UTC
(`Publish-gate failure #1 (test_regression, rc=1)`), one cycle after I had cleared a ten-hour wedge.

## The fix already exists in this repo

`tools/select_impacted_tests.py` gets this exactly right, and says so in its own docstring (§33-34):

> *A changed file that is NOT a mappable repo `.py` module (a JSON/data/config/site file …) makes
> the selection UNSAFE-TO-NARROW -> it returns the [full suite]*

That is the correct policy — **cannot prove impact ⇒ do not narrow** — and it is R15's own doctrine
applied to test selection: a check that cannot answer must fail toward safety, not toward silence.
The pre-commit gate simply does not use it; it uses the shallow filename-convention `tests_for()`.

## What closing it looks like

1. Make `tests_for()` (or its caller) treat an unmappable staged path the way
   `select_impacted_tests` does: refuse to narrow. Reusing that module outright is the honest move —
   it is the same question, already answered and mutation-proven.
2. **R15 — the mutation it must fire on is this exact one:** stage a `process_manifest.yaml` edit
   that breaks `test_process_reconciler.py` and assert the gate refuses. Today it passes, so the
   control cannot fail on its own named defect.
3. Note the gap is **wider than YAML**: every `.json` config, every `docs/design/*.yaml` the code
   loads, and `maturity_map.yaml` are all in the same blind spot.

## Why it belongs with today's other two findings

All three are the same shape — a control whose *scope* was derived from a convenient proxy rather
than the real question:

* boot-SHA drift: population = a **declaration** (`launched_by`) instead of an observation.
* GHOST PUSHER: verdict = an **inference** (HEAD moved) instead of an attribution.
* this: coverage = a **filename suffix** instead of "what does this file actually affect".

Each is individually small. Together they are why a ten-hour outage alarmed as a fresh hour.

## What closing it ACTUALLY looked like (2026-08-12, written after the build)

Step 1 landed differently from how this document proposed it, and the difference is the part worth
keeping. **Reusing `tools/select_impacted_tests.py` outright — which §41-50 above calls "the honest
move" — was measured and rejected.** Its answer for an unmappable path is the FULL SUITE, and its
import-graph answer for the one module this finding names is 53 test files off a 2.6s graph build.
Correct for a fork's inner loop; unaffordable on every commit. What was taken is its DOCTRINE
(cannot prove impact → do not fall silent) at a cost the commit path can pay: two `git grep` calls,
~0.1s, and zero work when the staged data file is one no module reads.

Two things the fires-test caught that reading would not have:

* **The basename route cannot be a fallback.** Written as "try the repo path, fall back to the
  basename", the selection found every doc-string that CITES the manifest and missed
  `background/process_reconciler.py`, which loads it as `_HERE / "process_manifest.yaml"` and so is
  only ever findable by basename. The fix's first draft therefore missed this finding's own
  instance. The routes are unioned.
* **A basename is only a name if it names one file.** Unconditional basename matching pulled 13
  unrelated test files into a `docs/design/simplifications/README.md` commit. The route is now
  conditional on the repo holding exactly one tracked file with that basename; ambiguity drops the
  ambiguous route, never the precise one.

Step 3's wider class is closed with it: any `.json`, `.yaml`, `.jsonl`, `.sh` or `.md` that a module
reads is on the same footing as the manifest, not just the instance that filed this.

## What was NOT closed, and is recorded rather than glossed

`site/`, `docs/reports/` and `docs/status/` are EXCLUDED from the derivation. These hold artefacts
the repo regenerates, and they are read very widely: measured, a staged `site/data/dashboard.json`
selects 29 test files / 583 tests / **111 seconds**, on the most frequent commit in the loop. This
gate's premise is that it is cheap enough never to be worth bypassing, and a two-minute pre-commit
gate is one someone reaches for `--no-verify` against — a WALL in CLAUDE.md. So the expensive,
more-correct version would buy a worse fail-open than the one it closes.

The exclusion is bounded, and the bound is asserted rather than asserted-about:
`tests/tools/test_pre_commit_test_gate.py::test_the_published_output_exclusion_is_bounded_by_another_gate`
reds if `tools/site_lane_gate.py` or the whole-tree site-surface trigger stops covering that root.
What genuinely remains open is narrow and stated: a commit that lands a bad PUBLISHED artefact is
still caught by the publish gate minutes later rather than at commit time.

## Related

* `WORKER_FINDING_THE_STALENESS_DETECTOR_CANNOT_SEE_THE_DAEMONS_THAT_GO_STALE_2026-08-09.md`
* `WORKER_FINDING_THE_GHOST_PUSHER_GUARD_FIRES_ON_A_CONCURRENT_WRITER_2026-08-09.md`

— Worker finding, 2026-08-09, self-inflicted during the second publish-wedge episode.
