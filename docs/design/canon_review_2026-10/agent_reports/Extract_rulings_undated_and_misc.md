# Agent report: Extract rulings: undated and misc

## Brief given

Read the brief at /tmp/claude-0/canon/brief.md and follow it exactly. Your batch list is /tmp/claude-0/canon/batches/E_undated.txt (13 files, paths relative to /tmp/claude-0/canon/repo/). Your batch code is E. Write your extract to /tmp/claude-0/canon/extracts/E_undated.md. Two of these files are standing design documents (docs/design/DIRECTOR_AXES.md and docs/design/DIRECTOR_CANON.md): for those, extract every rule or claim they state as current canon, kind=standing, and in the note say whether it looks stale (dates, references to things that may have been retired, numbers). One is docs/staging/in_progress/DIRECTOR_INPUT_LOG.md which may be long and log-like: skim it for director decisions only, and say how long it is. One is an advisor reference on CLV drivers: extract only the director's thesis statements it records (quoted or attributed to the director), not the advisor's analysis. Read every file in full. Reply with only the batch summary section.

## Report


## Batch summary
- files read: 13 (all read in full; none unreadable). Note: the on-disk snapshot contains only `CLAUDE.md` and `docs/`, so code files and `docs/observability/` ledgers named by these rulings could not be checked for existence. DIRECTOR_INPUT_LOG.md is short (76 lines / 4.3 KB), not log-like — a status banner plus the staged requirement.
- rulings extracted: 57 (written to `/tmp/claude-0/canon/extracts/E_undated.md`)
- most important / most likely forgotten (by id):
  - R-E-12 / R-E-13 / R-E-16 — DIRECTOR_CANON.md is stale by its own law: it still names the twin as standing approver, BUILD approval, epoch-gated BUILD and a seven-item one-way-door list, all abolished 2026-07-29; nothing has bumped it since v3 (2026-07-18) because the only mechanism that amended it (twin overturn) died with the twin (last acted 2026-07-16). DIRECTION.yaml has an open 2026-10-04 request for the director's wording.
  - R-E-12 / R-E-31 — the reserved "values decision defining what the company is FOR (the Epoch-4 fitness function) — above all others" has dropped out of every later one-way-door list (the 07-29 four, CLAUDE.md's five) while A5 remains undecided (R-E-18).
  - R-E-3 / R-E-8 — DIRECTOR_AXES.md: the director's one-line-score verdict loop was never used once ("none yet" since 2026-07-22), the roadmap was never rotated by versioned edit, and it cites a CLAUDE.md pricing law that no longer exists.
  - R-E-7 — the 20-year-veteran smell test as the believability acceptance bar is named nowhere in current canon, though CLAUDE.md's "third side is a practitioner" is its cousin.
  - R-E-19 — the runaway signature "sustained turns with zero level-transitions" (churn alarm, not a turn count) has no trace after 2026-07-15.
  - R-E-40 — TIME_REPLAY (slider to replay the passage of time on site pages, a view over the event log) was registered-not-built and then lost with PRIORITIES.md.
  - R-E-45 — "PRIORITIES.md remains the sole arbiter" lapsed silently; the file is gone and three things now claim the role.
  - R-E-56 / R-E-57 — the director's CLV merit order (Pays → Stays → size of the margin bet → value-add) is in no canon document, and the two curriculum values he reserved (discount rate, terminal-value method) are still advisor placeholders.
  - R-E-37 — "Pursuit must be earned by confidence" was to be featured on the Proof door; no publication is evidenced.
  - R-E-30 — P-4 was repealed for visible surfaces on 2026-07-16 but PRIORITISATION_RULES.md still states it unamended.
  - R-E-47 — "Public repo keeps zero message-traffic mirrors" is unstated in CLAUDE.md while pre-amendment `from_rich_*.md` director messages remain in the public tree.
- contradictions between documents in this batch:
  - One-way-door predicate enumerated four different ways: DIRECTOR_CANON §3 (7 items), DIRECTOR_TWIN (6), DELEGATE_AND_PREDICATE_FIX Part 2 (8, incl. "platform-admin"), and — outside the batch but governing — the 2026-07-29 ruling (4) and CLAUDE.md (5).
  - DIRECTOR_TWIN "Uncertain whether something is a one-way door? Escalate" vs DELEGATE_AND_PREDICATE_FIX "if uncertain AND reversible, it PROCEEDS" (later ruling wins; CLAUDE.md follows it).
  - DIRECTOR_CANON §6 "the tiered approval model is RETIRED" vs §3a "The approval STEP stays — it is company fidelity, not friction".
  - DIRECTOR_CANON §5 "director ranks, never self-promoted to BUILD" / "Epoch gating gates BUILD" vs CLAUDE.md "A level move is recorded, never authorised" and the 2026-07-29 abolition of `director_build_open`.
  - SEQUENCE_AND_TOKEN_ECONOMY (2026-07-08) "weigh every autonomous action for token cost" vs ANSWERS_C7 (2026-07-15) "Tokens are not the constraint; a tight cap re-invents goal-seeking" (reconcilable as waste-vs-spend, but unstated).
  - ANSWERS_C7 "ONE switch governs ALL autonomous execution... no second flag" vs STOP_CONTROL_GAP.md's second independent flag `.sim_runner_hold`.
  - DIRECTOR_CANON "Epoch 2 is the current open epoch" vs the CLV reference header "Epoch: 3" (2026-09-05) and EPOCH3_DIRECTION.md.
  - DIRECTOR_CANON "R1–R15 ... see CLAUDE.md for full text" vs THE_MODEL_ON_A_PAGE "R1–R17" and a rewritten CLAUDE.md with no numbered R-list.
  - CLV reference (2026-09-05) uses £150 acquisition cost as "the project's anchor" vs CLAUDE.md's director statement of 2026-08-30 that the £150 CAC was an invented number and the sourced figure was £55.
  - DIRECTOR_AXES axis 2 cites "CLAUDE.md pricing law" (activity-based cost-to-serve) which the 2026-08-28 CLAUDE.md no longer contains.
  - DIRECTOR_OVERRIDE_SKIP_PERMISSIONS_QUARANTINED.md (R-E-41) is an unauthenticated, quarantined claim of a director instruction, never actioned as such; the same policy later became reality via a console-confirmed Tier-1 (per AUTONOMOUS_EXECUTOR_SPEC.md) — the canon should cite that confirmation, not this document.
agentId: a6a3ad46523fa6e0b (use SendMessage with to: 'a6a3ad46523fa6e0b', summary: '<5-10 word recap>' to continue this agent)
<usage>subagent_tokens: 189866
tool_uses: 38
duration_ms: 718767</usage>
