# FRAME — the `site/**` test coverage seam (Campaign A debt E)

**Stage:** FRAME (off-front harness item — DISCOVER/FRAME only until a harness front opens; no BUILD here).
**Provenance:** surfaced by the Campaign A cross-door audit (`CAMPAIGN_A_DOOR_AUDIT_FINDING.md`, debt E) and by a real regression THIS session. **Lane:** H_harness.

## The defect (observed, with evidence)
Two gates guard commits/publishes, and **neither runs `site/**` tests**:
1. **Publish gate** — `background/process_run_complete.py::publish_gate_pytest_argv(test_root="tests/")` runs `pytest tests/ -x -q …`. `site/**/test_*.py` are outside `tests/`, so a red site-door test **cannot wedge the publish gate** and goes unseen by the director's window pipeline.
2. **Pre-commit gate** — maps changed files → *targeted* tests under `tests/` (observed: a `tools/generate_simplified_data.py` change correctly pulled in `tests/tools/test_generate_simplified_data.py`). But a change to a `site/` value has no established mapping to its `site/**/test_*.py`.

**Concrete failure this session:** wiring the W2_11↔D5 8th coupling pair took the Proof-door coupled-gaps panel to 8 pairs; `site/proof/test_coupled_gaps_panel.py` still asserted 7 → **RED on the Proof door (a director-facing surface)**. I updated the `tests/tools/…` copy but missed the `site/proof/…` copy, and **nothing caught it** — the full publish gate ran green because it never sees `site/`. It surfaced only because a later Campaign-A audit fork happened to run `pytest site/`. Absent that fork, a red director-facing door test would have shipped silently. (Same class also let a stale hardcoded figure sit un-tested — see the two drift catches, 62→63 modules, hedge 0.80-0.90→0.81-0.89.)

## Why it matters / fit to the whole
The site IS the director's load-bearing window (operating model). A gate that can't see the window's own tests is a fail-open control (R15 doctrine: a control that cannot fire on its own named defect is worse than none). `pytest site/` is **fast (~6s, 164 tests)** — there is no cost reason to exclude it; it was simply never wired in.

## Design options
- **A — add `site/` to the publish gate root** (`pytest tests/ site/`). Simplest coverage, but couples the heavy publish gate to `site/`'s node/`.mjs` render-harness dependencies and lengthens every publish; a flaky mjs harness could then wedge publishing (the exact fail-mode H23 partitioned away for daemon tests). **Rejected** — wrong blast radius.
- **B — a dedicated fast site-lane check** run on any `site/**` OR `site/data/**` OR `site/**`-consuming change: `pytest site/ -q` (~6s). Runs at pre-commit (targeted) and/or pre-push (full). Isolated from the publish gate; a site-test failure alarms the site lane without touching publishing. **Recommended.**
- **C — extend the pre-commit changed-file→test mapping** so a `site/` file change pulls in its sibling `site/**/test_*.py`. Necessary-but-insufficient alone: it catches direct site edits, but NOT the case that bit this session — a change to a **shared derived value** (`docs/observability/coupled_gap_ledger.json`, a `site/data/*.json`, a coupling count) that a `site/` page *consumes*. **Adopt B as the backstop, plus C for direct edits.**

## Recommended mechanism (B + C)
1. A site-lane gate step that runs `pytest site/ -q` whenever the change set touches `site/**`, `site/data/**`, or a known site-data producer (`tools/generate_*_data.py`, `background/*` that writes a `site/`-consumed ledger). Fast, isolated, fail-closed.
2. Pre-commit mapping extension: a changed `site/X/foo.html`/`foo.py` pulls in `site/X/test_*.py`.
3. Doctrine note appended where the shared-surface rule lives: "a change to a value a `site/` page consumes is not done until `pytest site/` is green — the publish gate is blind to `site/`."

## R15 — the fix must be able to FAIL (mutation test, required before any L2+ claim)
The new gate is itself a control, so it must be mutation-proven both directions:
- **Fires:** introduce a red `site/**/test_*.py` (e.g. re-break the 7-vs-8 pair assertion) in a change set that touches a `site/`-consumed value → the site-lane gate must go RED and block. Neutering the gate (skip `site/`) must let the red through (proving the gate was load-bearing).
- **Doesn't false-fire:** a change touching only `tests/`/`company/` with no `site/` impact must NOT trigger the (slower) site run needlessly — scope the trigger to the site-touching change set.
- **Fail-closed:** if `pytest site/` can't run (missing node for `.mjs` harnesses), that's a FAILED check (unavailable ≠ pass), surfaced loud — never silently skipped.

## Open questions for BUILD-open (director/harness-front)
1. Pre-commit vs pre-push vs CI placement — pre-commit adds ~6s to every site-touching commit; pre-push is lighter but lets a bad local commit exist briefly. (Recommend pre-commit for `site/` direct edits, pre-push full `site/` sweep.)
2. The `.mjs` render harnesses need `node` present; is it guaranteed in every commit environment? If not, the fail-closed branch must degrade to a loud "site tests unavailable" marker, not a silent pass.
3. Whether to fold this into the existing pre-commit hook or add a sibling — depends on H9/H10 map-write + hook architecture decisions.

**No BUILD here** — this is the design. Building it is a harness-lane BUILD (off-front); it opens when the director opens a harness front or BUILD_OPENs this item. Until then the mitigation is procedural (recorded in memory: "a `site/`-consumed change is not done until `pytest site/` is green").
