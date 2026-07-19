# DIRECTOR STEER — Test throughput is becoming the rate-determining step; restructure it (2026-07-19)

**Type:** [STEER] — a problem with requirements. The strategy is yours to propose and design.

---

## The problem (director's framing)

*"Testing is key to this. But we want to grow the segments and the duration. Testing starts to become rate determining and possibly limit the scope of the programme."*

Evidence it is already binding: a single fork's sim+simulation validation ran ~1h24m today; the suite is ~18,000 tests; the four publish-gate wedge episodes were all caused by unrelated tests blocking unrelated work. The Epoch-2 fidelity programme makes this worse by design — ablation-with-common-random-numbers, lift-over-naive, and worst-cell grids all require running the SAME world many times with one thing changed. If a validation cycle costs an hour, that programme is unaffordable; if it costs minutes, it is a research instrument. **Test throughput is now a constraint on the scope of the enterprise, not a housekeeping concern.**

Under the standing draw-mix balance this qualifies as legitimate foundation work: it is not harness polish, it is the blocker on product ambition.

## Requirements (the what — not the how)

1. **Measure before restructuring.** Where does the wall-clock actually go: test suite vs full simulation runs; CPU vs I/O; single-core vs available cores; which tests dominate the tail. Report the profile. (Note for scope: nothing in the repo references CUDA/torch/nvidia — the GPU appears to serve only local LLM inference, so it is likely NOT the bottleneck. Verify rather than assume.)

2. **Stop running everything for every change.** The programme currently validates the whole world on every commit. Well-trodden industry answers exist and should be evaluated on their merits for this codebase: parallel execution across cores; **tiering by cadence** (fast checks per commit, integration on merge, full fidelity validation nightly or at level-promotion — the existing `@pytest.mark.operational` partition proves the machinery); **test impact analysis** (run what the change actually touches, via coverage mapping); **predictive test selection** (learn from historical failure data which tests are most likely to fail given a change — Meta/Google/Microsoft all run variants; tests cluster by coverage, so a small selected subset catches most real breakage); and **test prioritisation** (order so real failures surface in seconds, not at minute 84).

3. **Separate the two test populations — this codebase's specific trap.** A simulation programme contains DETERMINISTIC tests (a failure is signal) and STOCHASTIC tests asserting on distributions (a failure is sometimes chance). Their variance differs by orders of magnitude — heteroscedastic in the strict sense — and mixing them corrupts any failure-prediction or flake-detection model, because the noisy population dominates. Requirements: classify the populations explicitly; give distributional assertions statistical bounds rather than exact expectations; quarantine genuinely flaky tests as noise, never as signal; and never let a stochastic failure wedge a deterministic pipeline (the publish-gate lesson, generalised).

4. **Cheap structural wins to consider:** simulate once and assert many times against the snapshot rather than re-running a world per test; verify scale-invariant properties on small worlds (10 customers, 3 months) and reserve full population × full duration for genuinely distributional claims; property-based and metamorphic testing (assert relationships — "double the price, margin moves this way" — rather than hand-computed exact outputs) for coverage per second.

5. **Allocate test budget by exposure, not frequency.** The fidelity grid already ranks where value lives: test hard in the cells that carry commercial consequence; sample elsewhere. Same principle as the rest of Epoch 2.

6. **Safety must not degrade.** Selection can miss things. Whatever is adopted, the full suite still runs on a cadence as the safety net; the gates that catch real regressions must still catch them, and that must be demonstrated (R15 — prove a real regression is still caught under the new regime, by mutation).

## Success criterion

The programme can grow segments and duration without validation time becoming the limit — and the director never again waits an hour to learn whether one change was sound.

**Risk & proportionality:** touches the test/CI machinery (blast radius: everything, since every gate depends on it) — so sequence it as measure → propose → adopt incrementally, each step with its own commit and revert path, and prove no safety loss at each step before the next. Do NOT restructure the gates and the selection logic in one turn. Tag: **contract-touching — implement with named mitigations; bring only genuine one-way doors as [ACT].**

— Advisor, carrying the director's steer, 2026-07-19.
