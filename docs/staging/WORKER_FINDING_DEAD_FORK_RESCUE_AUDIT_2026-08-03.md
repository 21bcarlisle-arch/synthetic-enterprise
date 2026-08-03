<!-- SUPERVISOR_DRAW: self-drawable -->
# [WORKER FINDING] — ~2,566 lines of built work were sitting UNCOMMITTED in dead fork worktrees (2026-08-03)

**Provenance:** worker tick, 2026-08-03. The tick drew `SITE1_expert_doors`. Auditing git reality before
building anything (rather than rebuilding) turned up seven unmerged fork branches. This is what they held.

## Why this was nearly a silent loss, not a tidy-up

Three of the seven worktrees held **uncommitted** source changes — not on a branch, not in any commit,
present only as files in a `.claude/worktrees/` directory. `background/stall_class_register.py` and its
447-line test were **untracked**: one `git worktree prune` or `rm -rf` from being gone with no trace in
any reflog. They have now been preserved as RESCUE commits **on their own branches only**; nothing was
merged to main, so `--no-verify` on those preservation commits landed no untested code on a shared surface.

| worktree | rescued as | content | verdict |
|---|---|---|---|
| `agent-a5555b1e8256de0e4` | `448c2dee5` | `background_worker.py` +266, `process_run_complete.py` +27, 2 test files (+346) | **RIVAL A** for `OPS_run_marker_sweep_livelock` |
| `agent-ad14ac1d4858a473f` | `f50b4cc26` | `background_worker.py` +277, `process_run_complete.py` +70, `test_run_marker_sweep.py` +423 (NEW) | **RIVAL B** for the same atom |
| `agent-ab2bd7adb8d3e2305` | `5bb96b5cb` | `stall_class_register.py` +693 (NEW), its test +447, `daily_self_note.py` +13 | **UNIQUE**, no rival, no home atom |

None of these files exists on main: `background/stall_class_register.py`,
`tests/background/test_stall_class_register.py` and `tests/background/test_run_marker_sweep.py` all return
"No such file or directory" on the main tree.

## The four already-superseded branches — audited, NOT reaped on a guess

| branch | claim | evidence checked | verdict |
|---|---|---|---|
| `ac55b4bffa0425237` | SITE1 proof door MAJOR-7 / MINOR-9 / MINOR-10 | `site/proof/index.html` byte-identical to main; main's `test_site1_proof_citations.py` is a **superset** (+85 lines) | ABSORBED |
| `a6ad9f2b324019a71` | SITE_EH2 + SITE1 proof door | its `_dedupe_consecutive` / `_bound_inconclusive` exist on main in more developed form as `_dedupe` / `INCONCLUSIVE_HORIZON_DAYS`; `robots.txt`, `sitemap.xml` already tracked | SUPERSEDED |
| `abdcad5f797657eb3` | SITE_EH1 segment disclosure | its `_check_front_door_segment_claim`, `_book_population_class`, `_population_gate`, `_anchors_runtime` are all **live on main** | LANDED (this rival won) |
| `a416449f398f3b333` | SITE_EH1 rival implementation | its `extract_segment_mix`, `_check_segment_disclosure`, `_population_verdict`, `_check_anchor_populations` are absent from main | **LOSING RIVAL — one idea worth keeping, below** |

**The one idea in the losing rival that main does not have.** `a416449f`'s `_population_from_source` +
`_POP_PATTERNS` derive an anchor's population (domestic / I&C / all-supply / undeclared) by parsing the
**benchmark source text**. Main's winner derives it from the **dashboard**. Under R15 that difference is
not cosmetic: reading the population from the same artefact the anchor is checked against is closer to the
TAUTOLOGY pattern, whereas parsing the published source is an **independent oracle**. Recorded here rather
than built, so the idea survives the branch (SELF_INTERRUPT_DISCIPLINE: queue, don't fix on sight).

## Disposition

- **Nothing reaped.** The doorbell's "no orphaned branches" rule is satisfied by *disposition*, and the
  disposition for four is "absorbed/superseded, safe to delete once someone confirms this audit", and for
  three it is "holds unique work, MUST NOT be deleted". Reaping the dirty three on the standing lifecycle
  rule would have destroyed 2,566 lines. Auditing before pruning is the rule that saved it.
- **Two rivals for one atom is a reconciliation, not a merge.** `OPS_run_marker_sweep_livelock` now carries
  a note naming both branches. Blind-merging either would silently pick a winner.
- `stall_class_register` had no home atom; one is minted so it stops being invisible.
- **Verified SITE1 is not blocked by any of this:** 142 proof-door tests pass on main
  (`site/proof/` + `tests/tools/test_site1_proof_citations_resolve.py` + `..._crawlability.py`).

## The class

This is the same defect as the `in_progress/` doorbell, one layer down: **work that was DONE but not
VISIBLE as work**. There it was designed BUILD halves parked in staging; here it is built code parked in
dead worktrees. A fork that dies between "wrote the code" and "committed it" leaves no git trace at all,
so no draw, no register and no gap reader can see it. The `reaper` named in the draw-blindness work is
still not built — until it is, this audit is the manual stand-in and must be repeated before any prune.
