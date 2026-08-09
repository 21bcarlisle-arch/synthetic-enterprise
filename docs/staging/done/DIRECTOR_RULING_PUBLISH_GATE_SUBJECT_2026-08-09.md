# [DIRECTOR-RULING] — The publish gate's subject is committed truth (2026-08-09)

**Type:** [DECISION — ratified in conversation 17:40 BST, delivered to the acting session by pane; this document is the record for canon and every other lane].

**Ruling:** the run-complete publish gate tests a clean checkout of HEAD (worktree or archive extraction), never the shared working tree. Publishing is the act of verifying and rendering committed truth; the living tree belongs to the lanes. Effective immediately with a minimal implementation tonight; the polished mechanism gets its own atom.

**Evidence that decided it (the acting session's own):** episode 4's final diagnosis — one cause, KNIFE pass 2's 19 staged-uncommitted files wedging every publish since 12:56Z while "a fresh checkout of origin/main passes all three" blocking tests. HEAD was clean for the entire outage. The morning's first cause was the same mechanism at one file. Gate-on-HEAD converts this class from a publisher outage into, at most, the owning lane's own commit failure.

**Explicitly not ruled tonight:** the pass-2 seam contradiction (decided at pass-2 review, not under outage pressure); per-lane worktree isolation for large refactors (registered for the parallelism programme).

## WORK THIS CREATES (canonical, in-document)
1. Tonight's minimal gate-on-HEAD implementation, deployed to the publish path. 2. The polished atom (proper worktree lifecycle, cleanup, R15 both ways). 3. The first post-ruling publish landed and stated plainly, markers drain-superseded, the £1,526,252.39 candidate baseline printed and adopted per the standing recommendation.

— Ruled 2026-08-09; staged by the advisor as record; the acting session implements from the pane instruction.

## Counterweight (added pre-delivery, on the director's challenge)
Freeing publishing from the tree must not license silent squatting. Therefore, paired with the gate change: a standing **tree-divergence measure** — count and AGE of staged-or-modified files versus HEAD, attributed to their owning lane where derivable — published each cycle and alarmed past a threshold with the same episode-memory discipline as the publish alarm. The forcing function moves from "the public site dies" to "the squatting lane is named daily." Existing teeth already pointing the same way, for the record: the tracked-and-clean promotion gate (uncommitted work cannot claim done), the orphan census and adoption path, the queued tick-exit check, and the cutover proposal's uncommitted-age alarm. A broken lane is thus detected by its divergence age, not by the mission's outage.

---

## MINT DISPOSITION 2026-08-09 (worker tick) — all four are covered, none re-minted

Per §2+§4 of `DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27`, one atom per named
deliverable in WORK THIS CREATES, and a deliverable already covered is stated rather than re-minted.
Verified against real disk/git state, not against a claim:

| # | deliverable | disposition |
|---|---|---|
| 1 | tonight's minimal gate-on-HEAD, deployed to the publish path | **LANDED** — `14fbd32cd`, then `576105747`, `3cc852aff` (untracked-DATA overlay). `run_fast_tests()` materialises HEAD via `git archive` into a throwaway dir; `tests/background/test_publish_gate_head_checkout_is_a_repo.py` covers it. No atom: shipped code is not a queue item. |
| 2 | the polished atom (worktree lifecycle, cleanup, R15 both ways) | **ALREADY MINTED** — `OPS2_publish_gate_head_worktree` (H_harness, L0→L2, `loop_stage: build`), spec `PLANNER_MINTED_publish_gate_head_checkout_polish_2026-08-09.md`. Not re-minted. |
| 3 | the first post-ruling publish landed and stated, markers drain-superseded, the £1,526,252.39 candidate baseline printed and adopted | **ALREADY MINTED** — `OPS3_first_post_ruling_publish` (H_harness, L0→L2, `depends_on: [OPS2_publish_gate_head_worktree]`). Not re-minted. |
| — | the **Counterweight**: a standing tree-divergence measure, by lane, published each cycle and alarmed past a threshold with episode-memory discipline | **LANDED AND WIRED** — `background/tree_divergence.py` + `tests/background/test_tree_divergence.py`, called from `process_run_complete._publish_tree_divergence()` at the pre-gate point, alarming through `notify(transition_key="tree_divergence", re_escalate_after=24h)` so a standing squat is named daily and an unchanged one does not re-page. Returns `None` by construction, so the publish path has no value to block on. |

Both minted atoms are drawable now (`loop_stage: build`) and neither is opened by anyone —
PROPOSE/RECORD/ACT. The spec doc is archived to `docs/staging/done/` with this one and the map's
references follow it, so the reference stays resolvable.
