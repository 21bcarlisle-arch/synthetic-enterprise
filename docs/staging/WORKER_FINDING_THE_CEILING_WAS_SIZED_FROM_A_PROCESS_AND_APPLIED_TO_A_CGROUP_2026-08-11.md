# WORKER FINDING — the ceiling was to be sized from a PROCESS peak and applied to a CGROUP

**Date:** 2026-08-11 · **Atom:** `OPS2_publish_gate_head_worktree` (owed item 1, the re-derivation)
**Lane:** H_harness
**Class:** R15 — a measurement in a different unit from the thing it is used to bound.
**Status:** ceiling now derived from measured demand and ratcheting; instrument landed; the
in-tree baseline phase relaunched under it.

## The instruction this was to carry out, and why carrying it out literally would have been wrong

`WORKER_FINDING_THE_CEILING_KILL_WAS_BANKED_AS_A_SIGTERM_2026-08-11` closed with a
recommendation I had made and the tool's own comment had made before me: *"size the peak first,
then derive the ceiling from it … `tools/sample_gate_rss_premium.py` is measuring the real peaks;
when it reports, this ceiling should be re-derived from them rather than left at a round number."*

The sampler HAS reported (`docs/observability/gate_x_premium_rss.json`):

```
"without_x": { "max_single_process_hwm_gb": 5.34, "peak_tree_rss_gb": 5.28 }
```

Deriving the new ceiling from 5.34G — the literal instruction — would have set it **BELOW a
demand already observed**. The kernel had killed this phase's scope with `oom_memcg=` that scope,
one child at 6.13G, having reached the **8192MiB cgroup limit**:

* `max_single_process_hwm` is a **per-process** high-water mark;
* `MemoryMax` applies to the **cgroup** — the whole process tree, and the `without_x` side had
  three processes in it;
* so the two numbers are not the same quantity, and only the second is in the ceiling's unit.

A fourth truncation was one obedient re-derivation away. **Observed-with-evidence**, both files
quoted above; the kill line is in the prior finding.

## The repair — the ceiling is derived, and it ratchets

`PHASE_MEMORY_MAX_MB` is no longer a literal.

* **Evidence** (`_measured_demand_floor_mb`): the largest demand the record has evidence for —
  a phase's sampled `scope_peak_mb`, and the `memory_max_mb` of any phase whose
  `hit_memory_ceiling` is true, because a cgroup kill proves demand reached the limit. A
  completed phase with no peak sample contributes **nothing**: not knowing a phase's peak is not
  evidence that it was small.
* **Rule** (`_derive_phase_ceiling_mb`): measured demand × `CEILING_HEADROOM` (1.25), capped by
  what this box can spare with the `MIN_MEMORY_HEADROOM_MB` start reserve intact — the same
  figure the phase already refuses to start without, not a second number meaning the same thing.
* **Live value:** floor 8192MB (the kill) → **ceiling 10240MB**, cap 11816MB on a 15912MB box.
  10240 is not chosen; it is 8192 × 1.25. 8192 is not chosen either — it is what the kernel
  measured as insufficient.
* **Terminus** (`_ceiling_is_sufficient` + `_bounded_argv`): when the derived ceiling stops
  clearing the box-safe cap, the phase is **REFUSED**, not clamped to the cap and re-run.
  Clamp-and-rerun is the shape that funded launches 12, 13 and 14. If this launch dies at 10240,
  the next derivation wants 12800 > 11816 and the harness says so instead of trying again.

## The instrument — measure the subject the ceiling bounds

`_ScopePeakSampler` reads `memory.peak` on the phase's **own scope** from the parent, while the
phase runs, because the scope is torn down at exit (the same fact that sent `_scope_oom_killed`
to the journal). Banked per phase: `scope_peak_mb`, `scope_peak_source`, `scope_peak_samples`,
`scope_peak_read_after_exit`, `scope_peak_is_lower_bound_on_demand`, `scope_peak_basis` — and
`memory_max_demand_floor_mb` + `memory_max_basis` beside the ceiling, so the next reader meets a
derivation rather than a round number.

**A peak that cannot be exact says so.** Exact only when the run ended on its own AND a read
landed after the child exited; otherwise a lower bound (a killed phase never used more than its
limit however much it wanted). Measured while building: reading *after* joining the sampler
thread made `read_after_exit` **False on every run** — systemd tears the scope down inside that
join — so the final read now comes first and the exact branch is reachable.

## R15, both ways — 8 mutations, all red (115 passed)

| mutation | test that reds |
|---|---|
| ceiling returns the old constant | `..._moves_with_the_demand_the_record_measured` |
| a killed phase's ceiling not read as demand | `..._banks_that_ceiling_as_measured_demand` |
| clamp to the cap and run | `..._refuses_the_phase_rather_than_clamping_it` |
| unknown box size reads as room enough | `..._refuses_rather_than_assuming_a_large_one` |
| unreadable cgroup returns 0 | `..._reads_as_unknown_rather_than_as_zero` |
| scope found by globbing the unit stem | `test_another_scopes_memory_is_not_this_scopes_peak` |
| killed phase's peak presented as its peak | `..._is_labelled_a_lower_bound` |
| ceiling pinned back at the measured demand | `..._clears_every_demand_the_live_record_has_evidence_for` |

Two of those mutations **survived the first pass** and are recorded because the surviving shape
is the lesson: the zero-peak mutation was unreachable from a test that only ever hit the
`cgdir is None` guard at the top of the reader (a hollow-scope case now covers the bottom), and
the loose-match mutation only bites when the glob is built on the unit **stem** rather than after
`.scope` is appended. A mutation that cannot reach the code is not a proof.

Two real-cgroup tests spend real seconds rather than asserting about strings: 400MB inside a
1024MB scope reads back 404MB labelled `observed`, and a paced 900MB allocation inside a 512MB
scope dies with its peak at the ceiling labelled `lower bound`.

## One defect this uncovered on the way

The basis sentences quoted the module constant. The moment the constant could MOVE, a phase
banked at 8192 re-derived as *"killed against its own 10240MB ceiling"* — and
`test_the_banked_record_agrees_with_the_basis_written_beside_it`, which is in the publish gate's
scope, went red. A healthy ratchet would have wedged publishing on every move. Both basis helpers
now take the ceiling **that phase ran under** (`memory_max_mb`, banked per phase); the population
control asks in the phase's own terms.

## What is still owed

The in-tree baseline itself — the tax number. Relaunched under the derived ceiling with the
sampler live, so this launch either **completes** (and banks a true peak, from which the ceiling
can come back DOWN) or **dies alone at 10240** (and banks a floor that makes the next derivation
exceed this box, which the harness then refuses rather than retries). Both are terminal; neither
is a fourth blind relaunch.
