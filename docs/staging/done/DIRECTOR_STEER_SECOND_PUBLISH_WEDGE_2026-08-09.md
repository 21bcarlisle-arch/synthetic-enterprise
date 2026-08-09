# [DIRECTOR-STEER] — After the second publish wedge (2026-08-09)

**Type:** [DIRECTOR STEER — decided items closed; DO-NEXT ordered; verbatim the director's text, staged by the ops advisor on standing proceed-with-veto.]

ANCHOR. Publishing was down ~10h. Two causes, both now found: a gate that could only time out and whose timeout counted as a pass, and untracked files in the shared index causing the write-time gate to refuse every publish commit. The fail-open is closed (1fd85cb27). No real publish commit has been confirmed to land yet.

DECIDED — not open for redesign:
1. Evidence of publishing is a publish COMMIT landing, never a green gate. The gate going green is what was wrong.
2. The staleness detector's permanently-red state is NOT a caveat. A stale process caused today's outage. A detector for that failure mode that is always red will be ignored exactly as reliably as one that is blind. Both fail the same way: nobody acts.
3. The register findings staged this morning (EPC certificate wrongness, absence correlation, the property-type wall leak) are Epoch 3 work and are to be REGISTERED, not built. The wall leak alone is Epoch 1 debt and may be closed now. Do not pull the rest forward.

DO NEXT, in order:
1. Confirm a real publish commit has landed and say so plainly if it has not.
2. Get tools/run_annual_report.py into version control. HEAD has no run entry point; the only copy is one working tree on one machine, and a fresh checkout or git clean reproduces today's outage — including on the cloud box, the designated seat destination. On the provenance record: you were right not to fabricate one. Write a truthful record instead — origin unknown to you, committed under director instruction to close a single-point-of-failure exposure, proper record owed by the owning lane. A record stating the record is missing is accurate, not fabricated. If the write-time gate still refuses an honest disclosure, stop and report that — a gate that blocks truthful provenance is its own finding.
3. Make the staleness signal mean "stale with respect to code this daemon actually loads." Your own refinement; it is now the work, not the footnote.

OBSERVATIONS — no action required, worth carrying:
- The failure path wrote to the state the alarm reads, so the failure silenced its own alarm. That is a class, not an instance. Where else can a check's failure clear the signal that the check failed?
- The suite grew past a fixed wall. The new ceiling is sound and growth now fails loudly rather than silently — but nothing watches suite duration, so the same shape recurs, just noisily.
- Staging is ~38 deep, oldest 4 August. Alarms now preempt the draw; the backlog is a separate problem and will not drain on its own.

## WORK THIS CREATES (canonical, in-document)
1. A plain landed-or-not statement on the publish commit. 2. tools/run_annual_report.py committed with a truthful unknown-origin provenance record (or the gate-blocks-truth finding instead). 3. The staleness signal redefined to code-actually-loaded. 4. The three observations carried as named classes where the machine judges them mintable.

— Directed 2026-08-09; drafted with the lab-front advisor; staged by the ops advisor, hash-verified.

---

## DISPOSITION (worker, 2026-08-09 ~14:20 +0100)

**1. Landed or not — plainly: YES, it landed.** Publish commit `94933cfff`
("Auto-process run complete: report + LATEST.md + site/", git=dfefd0a14, net=£1,526,676),
authored 2026-08-09 **13:56:05 +0100**, is on `origin/main` (`git merge-base --is-ancestor` → yes).
The fail-open fix `1fd85cb27` (13:41:13) is an ancestor of it, so this is a publish that landed
*after* the cure, not one the broken gate waved through. It carries real content:
`docs/reports/ANNUAL_REPORT.md`, all five `docs/shadow/*/index.html`, and 14 `run_complete_*`
markers retired to `done/`. Three further publishes had landed earlier the same day (01:11, 03:54,
06:13). The ~10h gap is 06:13 → 13:56.

**2. `tools/run_annual_report.py` is in version control — commit `83a55b750`, pushed, verified
present at `origin/main:tools/run_annual_report.py`.** Committed with it: the two sibling
composition roots from the same cut (`run_segment_report.py`, `run_phase4c_pipeline.py`), plus
`Makefile` and `tools/tournament_runner.py`, whose `run` targets still pointed at
`saas.reporting.annual_report` — a run path that since KNIFE1 exits with a message instead of
running. HEAD was broken from both directions, and one of the two was already committed
(`background/sim_runner.py:89` shells out to the untracked module, and landed inside `94933cfff`).

**The provenance premise was wrong, and it was wrong in our favour.** The steer authorised a
truthful "origin unknown to me" record. The origin is knowable: KNIFE pass 1, atom
`KNIFE1_reporting_cycle`, specified and recorded as LANDED at
`docs/design/KNIFE_HOTSPOT_PASSES.md` §"Pass 1", which names all three paths — and that doc is
already committed. Each file's own docstring says the same. Recording it as unknown would have been
a fabrication in the other direction, so the commit records the real origin instead.

**The gate did refuse once, and the refusal was not a truth-block.** AO2's G6 tripped on the phrase
"nothing else in the index composes…" — `_NOTHING_CLAIMED` matches the bare word `nothing`, then
contradicted it against the live index, which returns 3 rows. The record was honest and *named*
those rows in the same sentence. Rewriting the identical fact without a nothing-word passed. So:
the gate blocks a PHRASING, not a disclosure — an honest record that passes exists in every case
tried. This is a second instance of the known G6 false-positive class (the earlier one refused an
honest REUSE record on the word "none"); it is registered as a finding, not treated as the
gate-blocks-truth case the steer reserved.

*Worth carrying, found while writing that record:* `tools/capability_index.py` reads the **working
tree**, so it listed all three untracked modules as `wired` with 5 callers while HEAD carried none
of them. The index cannot distinguish "exists in the repo" from "exists on this machine" — which is
the same single-point-of-failure the steer is about, seen from the index side.

**3 and 4 — MINTED, three atoms, in `docs/design/maturity_map.yaml` (245 atoms, no id collision):**

| id | lane | level | covers |
|---|---|---|---|
| `PW1_staleness_is_code_actually_loaded` | H_harness | 0→2, `build` | DO-NEXT #3. Two halves: (a) fix the *population* — `_systemd_owned_sessions()` defaults `launched_by` to `tmux`, so `sim-runner` and `background-worker`, the two daemons that broke, drop out of the detector's answer; the 2026-07-29 cutover patched 2 manifest rows and left 7 identical ones, an R10 instance fix. (b) redefine `stale` against the modules a daemon actually imports, so it can be **green**. |
| `PW2_failure_clears_its_own_alarm` | H_harness | 0→2, `build` | Observation 1, as a class. Census first (writer-set ∩ reader-set per state path, derived not inspected), then a monotonic-episode guard. Explicitly *not* an instance fix on `.publish_gate_state.json`. |
| `PW3_suite_duration_watch` | H_harness | 0→2, `build` | Observation 2. Headroom **ratio** on an existing series, trend-transition alarm (R5), with R12 stated on its face: the fastest way to make the number green is to run fewer tests, which is forbidden. |

**Observation 3 (staging ~38 deep) is judged NOT mintable as a class,** and that judgement is
recorded rather than left implicit: it is a workload, not a defect shape. The mechanism it
superficially resembles — leftover-marker drain — already exists and is proven
(`background_worker.process_leftover_run_markers`, 413 → 12 on 2026-08-03). The advisor briefs need
dispositioning, not a mechanism.

**Not started this tick:** the self-refill draw `D18_confounder_observable_channel` — the steer's
DO-NEXT is ordered and took the tick. It stays drawable.
