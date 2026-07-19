# Test Throughput — Measurement and Restructuring Proposal

**Status:** MEASURED + PROPOSED, not yet adopted. Per the director's steer
(`docs/staging/DIRECTOR_STEER_TEST_THROUGHPUT_2026-07-19.md`), this turn does **measure → propose**
only. No gate, marker, or selection logic in the repo is changed by this document. The only new
artefact besides this doc is `tools/profile_test_suite.py`, a read-only profiling helper (it only
ever invokes `pytest --collect-only` / `pytest --durations`; it writes nothing except an optional
JSON report you point it at).

**Why this matters (director's framing):** *"Testing is key to this. But we want to grow the
segments and the duration. Testing starts to become rate determining and possibly limit the scope
of the programme."* The Epoch-2 fidelity programme (ablation-with-CRN, lift-over-naive, worst-cell
grids) requires running the same world many times with one thing changed. If a cycle costs an
hour, that programme is unaffordable; if it costs minutes, it's a research instrument. **This
proposal's job is to make the fidelity programme affordable without losing the safety net.**

---

## 1. Measured profile

Environment: 16 cores (`nproc`), 15GiB RAM (≈4.3GiB available at the time of measurement — the
box was already busy), Python 3.14, pytest 9.0.3. No `pytest-xdist`, no `coverage`/`pytest-cov`
installed. `pytest-xdist==3.8.0` **is** downloadable from PyPI in this environment (verified with
`pip download --no-deps`), so network access to add it is not a blocker.

**GPU/CUDA check (steer note, verified rather than assumed):** the only `nvidia`/`torch`/`cuda`
reference in the entire repo is `background/ntfy_responder.py` calling `nvidia-smi` to report
Ollama's GPU utilisation in a status line. No test, no `sim/`/`company/`/`saas/`/`simulation/`
module imports torch or touches CUDA. **The GPU plays no role in test wall-clock.** This whole
programme is CPU-bound Python, confirmed directly (§1.2 below shows a heavy test process pinned at
100% of a single core).

### 1.1 Total size and where tests live

```
19,082 tests collected in 5.9–10.4s   (collection itself is NOT the bottleneck)
```

| Area | Test files | Tests collected | Share |
|---|---|---|---|
| `tests/company/` | 566 | 12,262 | 64.3% |
| `tests/simulation/` | 89 | 1,566 | 8.2% |
| `tests/saas/` | 86 | 1,588 | 8.3% |
| `tests/tools/` | 98 | 1,364 | 7.1% |
| `tests/background/` | 67 | 1,181 | 6.2% |
| `tests/sim/` | 33 | 675 | 3.5% |
| `tests/interface(s)/`, `tests/controls/`, `tests/design/`, `tests/hooks/` | 11 | 11 dirs → 910 (incl. `tests/sim`) | — |
| loose files directly under `tests/` | 11 | ≈434 | 2.3% |

`tests/company/` is nearly two-thirds of the whole suite by count. This matters for §2: **test
count and wall-clock are almost uncorrelated in this repo.**

### 1.2 Where the wall-clock actually goes — it is NOT spread evenly

Directly timed samples (`pytest <target> --durations=N -q --tb=no`):

| Sample | Tests | Wall time | Slowest single test |
|---|---|---|---|
| `tests/company/billing` + `tests/company/compliance` | 2,076 (+1 xfail) | **2.64s** | 0.29s |
| `tests/sim` + `interface(s)` + `controls` + `design` + `hooks` | 910 (+1 xfail) | **9.52s** | 0.42s |
| `tests/simulation` fast sample (acquisition funnel, household segments, gas policy costs) | 94 | **0.34s** | 0.05s |
| `tests/simulation/test_run_phase2b.py` (1 of the 8 files already gate-excluded, see §1.3) | 20 | **185.69s** | **184.87s** (one test) |
| `tests/tools` + `tests/background` + `tests/saas` (`-m "not real_subprocess"`) | 4,128 (+5 skip, 1 deselect) | **191.15s** | **116.61s** (one test) |

This is the headline finding: **the tail is not "many slow tests," it is a handful of individual
tests each invoking a real, multi-year end-to-end simulation run.** Company (64% of the suite)
runs 2,076 tests in 2.64s — about **1.3ms/test**. Two single tests, picked essentially at random
by sampling two directory groups, together account for **301 of the 377 seconds** measured above
(80%). Everything else in both of those batches — 6,209 other tests — shares the remaining 76
seconds.

**Root cause #1 — `tests/simulation/test_run_phase2b.py::test_retention_log_includes_acq_cost_saved`
(184.87s of the file's 185.69s, 99.6%):**
```python
def test_retention_log_includes_acq_cost_saved():
    """Retention log entries include acq_cost_saved_gbp for traceability (Phase 15b)."""
    from simulation.run_phase2b import main
    result = main()                       # <-- NO report_end truncation
    rl = result.get("retention_log", [])
    if rl:
        assert "acq_cost_saved_gbp" in rl[0]
```
`main()` (default `report_end=REPORT_END`) replays the **full 2016–2025 (10-year) half-hourly
settlement history**, deterministically (no LLM — `SIM_FAST_MODE=1` only skips the Ollama risk
committee, it does not truncate the sim clock) — to check a single dict key's presence on the
first retention-log entry.

**The proven fix already lives right next to it.** The sibling file
`tests/simulation/test_run_phase2b_event_log.py` (2nd file on the same `PUBLISH_GATE_HEAVY_IGNORES`
list) solves exactly this problem: a `scope="module"` fixture calls `main(report_end="2017-12-31",
sim_interface=stub)` **once**, and 22 tests assert against the cached result. Timed directly:
**22 tests in 21.58s**, of which the shared fixture's one truncated sim run is 10.89s — i.e.
truncating from 10 years to ~2 already buys roughly **9× the wall-clock** even before eliminating
the redundant call. (One test in that same file, `test_sim_interface_none_still_works`, still
calls `main()` outside the shared fixture — 9.85s of the file's 21.58s — showing the pattern isn't
even fully applied where it already exists.) This is not a hypothetical recommendation: it is an
existing, working template one file away from the worst offender, unused by its neighbour. This is
the textbook case for requirement 4 ("simulate once, assert many" / "verify on a small world").

**Root cause #2 — `tests/tools/test_website_integrity_fix.py::test_generate_dashboard_json_returns_gate_status`
(116.61s of a 191.15s batch, 61%) — a test-isolation GAP, not a genuine full-suite need:**
```python
def test_generate_dashboard_json_returns_gate_status(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr("tools.generate_dashboard_data.generate", lambda json_path: False)
    result = prc.generate_dashboard_json(tmp_path / "run.json")
    assert result is False
```
The test explicitly stubs the dashboard generator to a no-op — its *intent* is O(1). But
`generate_dashboard_json()` unconditionally calls `tools.run_frozen_baseline.generate()` **first**,
which is documented in `background/process_run_complete.py` (line 648) as replaying "the full
decade TWICE under CURRENT_POLICY vs NAIVE_POLICY," gated by a weekly `should_refresh_baseline()`
check. That gate isn't stubbed here, so under a fresh/no-state test environment it refreshes for
real — a mocked-to-be-cheap test silently inherits a 116-second unmocked dependency. **This is a
new finding: a 9th heavy test not on the existing `PUBLISH_GATE_HEAVY_IGNORES` list** (§1.3). It
does not currently wedge the publish gate only because that gate already runs from `tests/` with
the 8 known files ignored and this one wasn't identified before — it's exactly the class the R10
class-closure rule exists for.

**CPU vs I/O, single-core vs available cores (verified by `ps` during the `test_run_phase2b.py`
run):** the pytest process ran at **100% of one core**, ~3.2GB RSS, for the full 185s — i.e. the
dominant cost is **single-core-bound CPU compute**, not I/O/network (no test-time network calls
exist — the point-in-time-blindfold architecture doesn't allow it, and `background/notify.py`'s
send is mocked globally in tests per `tests/conftest.py`). With 16 idle cores sitting next to that
one pinned core, **this workload is a textbook parallelisation candidate** — but see the RAM
caveat in §3.4.

### 1.3 The existing tiering machinery (do not rebuild — extend it)

Two partition mechanisms already exist and already prove the pattern works:

1. **`PUBLISH_GATE_HEAVY_IGNORES`** (`background/process_run_complete.py:115`) — 8 named files
   (`test_run_phase2b.py`, `test_run_phase2b_event_log.py`, `test_run_phase4c_on_phase2b.py`,
   `test_phase40b_gas_pass_through.py`, `test_phase24a_ic_customer.py`,
   `test_phase40a_pass_through.py`, `test_phase40c_deemed_rate.py`, `test_phase41a_flex.py`), 158
   tests total, `--ignore`'d from the publish gate for **speed**. Root cause #2 above shows this
   list is already stale by at least one file.
2. **`@pytest.mark.operational`** (`tests/conftest.py:32`) — 833 tests across 43 files (all in
   `tests/background/` + `tests/hooks/test_pull_next_work.py`), deselected from the publish gate
   for **scope** (daemon-lifecycle machinery, not published content) via `-m "not operational"`,
   with its own independent-cadence green signal
   (`run_operational_layer_signal`/`OPERATIONAL_LAYER_*`, hourly-throttled, pages only on
   *persistent* red — R5) that never touches the publish gate's own state. **This is the exact
   shape §4 below reuses for the new `full_fidelity` tier** — same author, same file, proven in
   production, mutation-tested already (`tests/background/test_publish_gate_scope.py`).

So: `publish_gate_pytest_argv()` today runs **18,249 tests** (`-m "not operational"`) minus the 158
in the ignore list = **≈18,091 tests**, once per publish cycle, with `-x` (stop on first failure).
That is the gate the director experiences as the multi-minute-plus wall on every publish. Separate
from that: the "single fork's sim+simulation validation ran ~1h24m today" the steer cites is **not**
a formal gate at all — it's an ad hoc `pytest tests/sim tests/simulation` a fork runs to
self-verify before merging. §1.2 shows `tests/sim` itself is ~10s; the 84 minutes is almost
entirely a small number of known-heavy full-simulation tests in `tests/simulation` being re-run
**serially, on one core, from scratch**, every time any fork touches that area — there is no
cheaper alternative today than "run everything."

**How many heavy tests, precisely?** Two are directly timed (§1.2's two root causes, 185s and
117s). A `grep` pass across the remaining 6 of the 8 `PUBLISH_GATE_HEAVY_IGNORES` files (excluding
`test_run_phase2b_event_log.py`, which already uses the shared-fixture fix per §1.2) shows the
**same untruncated-`main()`-call pattern recurs**: `test_phase40a_pass_through.py`,
`test_phase40c_deemed_rate.py`, `test_phase40b_gas_pass_through.py`, and `test_phase41a_flex.py`
each have one such call; `test_phase24a_ic_customer.py` has two;
`test_run_phase4c_on_phase2b.py` has **three** (`simulation.run_phase4c_on_phase2b.main()`, a
different heavy function, at lines 186/196/207). A direct timed run of these four remaining files
together did not complete inside a 580s bound (i.e. this batch alone is *at minimum* another
~10 minutes) — consistent with there being more like **12–20 individual heavy test functions**
across the ignore list, not a clean 9. **This is a known-incomplete count, stated as such rather
than rounded to a tidier number:** Step 1 below (`pytest --collect-only -m full_fidelity` once the
marker is applied) is the mechanism that turns this from a grep-based estimate into an exact,
inspectable list before Step 3 relies on it.

### 1.4 Deterministic vs stochastic population (the codebase's specific trap, per requirement 3)

Heuristic file-level scan (`tools/profile_test_suite.py --classify`, grep-based — a starting point
for manual triage, not an exact classifier):

| Class (heuristic) | Files | Note |
|---|---|---|
| Direct stochastic-input signal (`np.random`, `random.seed(`, `import random`) | 48 / 961 | genuine chance-can-make-it-fail candidates |
| Distributional/tolerance-style assertion (`pytest.approx`, `assert abs(...) <`) with **no** randomness signal | 536 / 961 | **heuristic is over-broad** — `pytest.approx` is also the idiomatic way to compare ordinary floats for rounding, which is fully deterministic; this bucket needs a human pass, not a mechanical count, before any bound gets attached |
| Neither signal (plain exact-value assertions) | 377 / 961 | deterministic-in-the-strict-sense candidates |

No project-wide global RNG seeding (`np.random.seed(...)`/`random.seed(...)`) was found in
`sim/`/`company/`/`saas/`/`simulation/` production code — consistent with CLAUDE.md's C-S2 named
substream discipline (each stochastic subsystem draws from its own seeded generator instance,
never a shared global), which is good news for reproducibility but means the "is this test
actually seeded, or genuinely sampling-without-control" question can't be answered by grep alone —
it requires reading each of the 48 stochastic-signal files. **Recommendation below (§4 Step 1)
is to do that triage as a small, explicit, one-file-at-a-time labelling pass, not a mechanical
sweep** — mislabelling a flaky test as deterministic-signal is worse than not labelling it.

Observed today: the `large_sample_*`/`*_close_to_anchor` tests already sampled in §1.2
(`tests/sim/test_w2_10_dd_attribution.py` etc.) run in **0.3–0.4s each** even though they assert
on population-level statistics — they already use small, fast synthetic populations, not a
full-history sim. That's the right existing pattern; it just isn't labelled or protected as a
population yet.

---

## 2. Top 3 throughput levers, ranked by payoff

**#1 — Close the "9 heavy tests" gap and stop them being re-run by default (highest payoff, lowest
effort).** These heavy tests (§1.3 — likely a dozen-plus individual test functions, not a clean round number) are responsible for essentially all of the measured minutes-long
tail; the other ~19,000 tests are collectively cheap (company alone: 12,262 tests in ~3s). Tiering
these out of the default/fork-verification path — while giving them their own scheduled, still-
mutation-provable green signal (exactly the `operational` marker's proven shape) — turns an
84-minute ad hoc validation into something close to the ~10-second `tests/sim` baseline, with zero
loss of the actual safety check (it still runs, just on a cadence instead of on every touch).

**#2 — Fix the two named isolation bugs at the root, not just the tier boundary.** Root cause #1
(`test_run_phase2b.py`'s one untruncated `main()` call) and root cause #2 (the dashboard test's
unmocked frozen-baseline dependency) are each a few-line fix that removes ~185s and ~116s
respectively **without needing any gate change at all** — the R10 "class closure" the project
already has a name for. This is cheaper than tiering and should land first/alongside it (they're
not alternatives — tier as the structural backstop, fix as the actual cost removal).

**#3 — Bounded-concurrency parallelism (`pytest-xdist`), applied differently to the two
populations.** The cheap bulk — effectively all but a literal handful of individual test
*functions* (§1.2: one dominant test per heavy file, not the whole file) — is already fast enough
serially (ms-to-low-seconds per thousand tests, measured) that `-n auto` mostly buys headroom, not
urgency. The **heavy tier** is where parallelism has real
payoff for the Epoch-2 fidelity programme specifically: running N same-world variants (ablation/
CRN/lift-over-naive) concurrently instead of serially is the direct mechanism that makes "a cycle
costs minutes not an hour" true for that programme. The RAM ceiling measured (~3.2GB RSS per heavy
process, ~4.3GB available headroom at time of measurement on a 15GiB box already running the
LLM/background stack) caps safe heavy-tier concurrency at roughly **2 at a time** on this specific
box — a real, named constraint, not a reason to skip parallelism, just a reason to cap it
separately per tier rather than blanket `-n 16`.

Test-impact-analysis / predictive selection (steer item 2's third and fourth mechanisms) is
**not** in the top 3: it requires `coverage`/`pytest-cov` (not installed) and, more importantly,
is solving a problem this repo doesn't yet have — given company's 12k tests already run in ~3
seconds, a coverage-mapped subset saves little relative to the effort of building and maintaining
the map. The project already has a *cheaper*, proven version of the same idea —
`tools/pre_commit_test_gate.py::tests_for()` and `tools/site_lane_gate.py::site_tests_for()` both
do filename-convention changed-file→test mapping today. Extending that convention (§4 Step 5) gets
most of the benefit of "run what the change touches" without a new dependency.

---

## 3. Tiering design

### 3.1 The three cadences, mapped onto what already exists

| Tier | Cadence | Existing mechanism it extends | New tests it must cover |
|---|---|---|---|
| **Fast / per-commit** | every `git commit` | `tools/git-hooks/pre-commit` → `tools/pre_commit_test_gate.py` (targeted: `CONTROL_TESTS` + changed-file mapping) + `tools/site_lane_gate.py` (site/) | unchanged — already targeted and fast |
| **Integration / on-merge or publish** | every publish cycle | `background/process_run_complete.py::publish_gate_pytest_argv()` — currently `tests/` minus `operational` minus the 8 `PUBLISH_GATE_HEAVY_IGNORES` files (`-x`, ≈18,091 tests) | add the new `full_fidelity` marker (§4 Step 3) as a second deselection term, replacing the hardcoded file-ignore list |
| **Full-fidelity / nightly or at level-promotion** | scheduled, or triggered by an Epoch/level-promotion event | new — same shape as `run_operational_layer_signal`/`OPERATIONAL_LAYER_*` (own state file, own throttle, pages only on *persistent* red, R5) | the known-heavy tests (§1.3 — count TBD exactly by Step 1's collect-only check), the Epoch-2 ablation/CRN/lift-over-naive/worst-cell battery, and any test the `@pytest.mark.stochastic` triage (§3.2) decides needs a full population run |

The integration tier is where "stop running everything for every change" actually lands: a fork
doing atom-level work in `tests/sim`/`tests/simulation` should run the **fast tier** for its own
loop and let the **integration tier** (already wired to the publish gate, already gated per
publish, not per edit) be the safety net for anything broader — not manually invoke
`pytest tests/sim tests/simulation` and eat 84 minutes.

### 3.2 Deterministic/stochastic separation, concretely

- Add `@pytest.mark.stochastic` (registered in `tests/conftest.py::pytest_configure`, same pattern
  as `operational`/`real_ntfy`/`real_subprocess`) to the manually-triaged subset of the 48
  direct-randomness-signal files that are genuinely sampling without a fixed seed.
- Any test carrying that marker must assert with a **statistical bound** (a tolerance/CI/percentile
  band anchored to an external source, per R12's existing anchoring discipline), never an exact
  expected value — this is a review criterion for new tests from this point, not a mass rewrite of
  the 536 `pytest.approx` files (most of which are ordinary float-tolerance, not statistical).
- A test that fails intermittently under re-run gets quarantined (`@pytest.mark.flaky` +
  routed to its own "noise" bucket, excluded from any future flake/impact-prediction signal) —
  never silently retried, never treated as evidence for or against a real regression. This is a
  new marker to add at the point a real flake is caught, not speculatively now (no known flakes
  were surfaced by this measurement pass).
- **The one hard rule that must never be violated regardless of tier:** a stochastic-marked test's
  failure can never gate the fast or integration tier — same DECOUPLING shape `operational`
  already proves (§1.3), so it inherits the same proof obligation (§4 Step 3's R15 mutation test).

### 3.3 Allocate by exposure, not frequency

The fidelity grid (`docs/design/CORE_FIDELITY_PHASES.md` family) already ranks where commercial
consequence lives. Concretely: the heavy full-decade tests exist because a handful of surfaces
(retention economics, gas pass-through, deemed rates, flex/battery capital) are judged worth a real
end-to-end replay. That judgement is *right* — the fix is cadence and isolation, not deleting the
coverage. Lower-exposure properties (e.g. "does this dict key exist") do not need a full-decade
replay to verify — root cause #1 is exactly a case where the assertion's actual exposure (one
struct field) was mismatched to the world size used to produce it (ten years of settlement data).

### 3.4 RAM/CPU capacity constraint on parallelism (measured, not assumed)

`free -h` at time of measurement: 15GiB total, ~4.3GiB available (11GiB already in use by the
Ollama/background stack this box also runs). A single heavy full-simulation test process peaked at
~3.2GB RSS. **Unconstrained `-n 16` on the heavy tier would thrash swap** (4GB swap configured, 1GB
already in use) rather than help. Recommended caps: bulk/cheap tier `-n auto` (safe — these
processes are lightweight, confirmed by the ms-scale per-test cost); heavy/full-fidelity tier
capped explicitly (e.g. `-n 2`) until a future re-measurement on a less loaded box justifies more.

---

## 4. Incremental adoption sequence

Each step is its own commit, independently revertible, and states its own R15 proof. **None of
these steps are taken in this turn** — this is the sequence proposed for subsequent, separately
reviewed turns, per the director's explicit "sequence it: measure → propose → adopt incrementally."

**Step 1 — Label, don't change behaviour.**
Add `@pytest.mark.full_fidelity` to the 8 existing `PUBLISH_GATE_HEAVY_IGNORES` files' heavy
test(s) plus the newly-found `test_website_integrity_fix.py::test_generate_dashboard_json_returns_gate_status`,
and `@pytest.mark.stochastic` to the manually-triaged subset of the 48 stochastic-signal files.
Zero gate change — pure annotation. *Revert:* delete the marker lines. *R15 proof:* none owed yet
(no control reads the marker until Step 3) — this step's own correctness check is simply that
`pytest --collect-only -m full_fidelity` returns exactly the intended set, and that count is recorded here as the first EXACT (not grep-estimated) figure.

**Step 2 — Fix the two named isolation bugs at the root.**
(a) `test_generate_dashboard_json_returns_gate_status`: also monkeypatch
`tools.run_frozen_baseline.generate` (mirroring the existing `generate_dashboard_data.generate`
stub) so the test's own stated intent (a no-op dashboard call) is actually true.
(b) `test_retention_log_includes_acq_cost_saved`: pass a truncated `report_end` (`main()` already
accepts the parameter; the sibling file `test_run_phase2b_event_log.py` already demonstrates the
pattern at `report_end="2017-12-31"`) since the assertion only needs the retention log's shape, not
ten years of it.
*Revert:* each is a one-file, one-line-ish diff; git revert restores the slow-but-correct original.
*R15 proof:* for each fix, temporarily reintroduce the real defect the test guards (drop
`acq_cost_saved_gbp` from the retention-log entry construction in `simulation/run_phase2b.py`;
force `generate_dashboard_json` to swallow a `False` gate result) and confirm the now-fast test
still goes red — the speed-up must not have silently narrowed what's checked.

**Step 3 — Give `full_fidelity` its own independent-cadence signal, replacing the hardcoded ignore
list.**
`publish_gate_pytest_argv()` changes its marker expression from `"not operational"` to
`"not operational and not full_fidelity"` and drops `PUBLISH_GATE_HEAVY_IGNORES` (the marker now
carries what the file-path list used to). A new `run_full_fidelity_signal()` is added next to
`run_operational_layer_signal()` in `background/process_run_complete.py` — same state-file/throttle/
persistent-red-pages-once shape, own cadence (nightly, or triggered at a level-promotion event per
`docs/design/MATURITY_MAP.md`). *Revert:* restore the marker expression and the ignore list; delete
the new signal function — the publish gate's behaviour is provably identical to today's (same tests excluded, same reason). *R15 proof:* mirror `tests/background/test_publish_gate_scope.py`'s
existing pattern — inject a defect into one `full_fidelity`-marked test's underlying logic and
confirm (a) the publish gate stays green and un-wedged, (b) the new nightly signal goes red and
pages on persistence, (c) recovery re-golds and pages once. This is the direct mutation proof that
the decoupling is real, not just declared — same bar `H23_publish_gate_scope_marker` already
cleared for `operational`.

**Step 4 — `pytest-xdist` for the bulk (non-`full_fidelity`, non-`operational`) tier.**
Add `pytest-xdist==3.8.0` to `requirements.txt` (dev-only). Nothing invokes `-n` by default —
plain `pytest tests/` is unchanged; `-n auto` becomes an opt-in flag any lane (interactive fork
verification, the integration-tier publish gate itself once proven stable) can add. *Revert:*
remove the requirements line; without the flag, behaviour is untouched regardless of whether the
package is installed. *R15 proof:* pick one deliberately-broken company/ test (mutate a real
assertion) and confirm the exact same test is reported red under `-n auto` as under serial — the
parallel runner must not swallow, reorder-hide, or race a real failure.

**Step 5 — Bounded-concurrency parallel lane for the `full_fidelity` tier, sized to the RAM
ceiling (§3.4).**
`pytest -m full_fidelity -n 2` (or the re-measured safe cap on whatever box runs it) as the
mechanism the Epoch-2 ablation/CRN/lift-over-naive/worst-cell programme uses to run same-world
variants concurrently instead of serially. *Revert:* drop back to `-n 0`/serial; same tests, same
assertions, just slower. *R15 proof:* run a paired-seed ablation (baseline vs one deliberately
mutated parameter) both serially and under `-n 2`; confirm the measured lift/delta is bit-identical
either way (parallelism must not perturb CRN pairing).

**Step 6 — "Simulate once, assert many," applied at next touch (not retrofitted wholesale) — using
the template that already exists in this codebase.**
`tests/simulation/test_run_phase2b_event_log.py::sim_result_2017` (§1.2's root-cause-#1 callout) is
already a working, `scope="module"`, truncated (`report_end="2017-12-31"`) shared-fixture pattern
one file away from the worst offender. Step 6 is: apply that same template — verbatim pattern, not
a new design — to any other module where several tests each want their own fresh `main()` call but
could share one, including finishing the job in its own file (the one remaining un-shared caller,
`test_sim_interface_none_still_works`, 9.85s of that file's 21.58s). Same remediation-on-touch
precedent already set for the typed-flow-seam and portability constraints (CLAUDE.md) — apply at
next real touch, don't retrofit speculatively. *Revert:* fixture removal, tests fall back to their
own calls. *R15 proof:* same shape as Step 2(b) — reintroduce the specific defect each assertion
guards and confirm the shared-fixture version still catches it.

**Step 7 (later, larger investment — only if Steps 1–6 prove insufficient) — changed-file test
mapping, extended.**
Before reaching for `coverage`/`pytest-cov`-based test-impact analysis, extend the convention-based
mapping the repo already has proven twice (`pre_commit_test_gate.py::tests_for()`,
`site_lane_gate.py::site_tests_for()`) to cover `simulation/`↔`tests/simulation/` and
`saas/`↔`tests/saas/` the same way. Only escalate to real coverage mapping if the convention-based
approach demonstrably misses regressions a coverage map would have caught — named, evidenced, not
spec'd speculatively.

---

## 5. Safety-net statement (requirement 6)

At every step above, the **full suite still runs on a cadence** — nothing in this proposal removes
a test, only changes *when* it runs and *what blocks on it*. The `full_fidelity` tier's own R15
proof (Step 3) is the concrete demonstration that a real regression hidden behind the new tiering
is still caught, on its own cadence, exactly as `operational` already proves for daemon-lifecycle
regressions today. No step is adopted without its own passing R15 mutation proof; a step whose
proof fails is not merged, full stop.

---

## 6. Artefacts from this turn

- This document.
- `tools/profile_test_suite.py` — read-only profiler used to produce every number in §1. Modes:
  `--collect-only` (test counts, seconds), `--classify` (deterministic/stochastic heuristic scan,
  sub-second), `--profile` (durations on the known-heavy files + a fast sample, minutes — opt-in,
  not run by default), `--full` (whole-tree profile, requires `--i-understand-this-is-slow`,
  deliberately hard to trigger by accident). Complements the existing composition-only
  `tools/generate_test_mix_data.py` (counts per area) with duration (time per area / dominant
  tests) — neither tool changes any gate.
