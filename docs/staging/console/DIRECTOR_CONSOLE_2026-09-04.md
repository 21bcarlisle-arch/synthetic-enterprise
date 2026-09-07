**Severity:** RECORDED · **Lane:** H_harness

# Director console — verbatim record, 2026-09-04

> **The director did not write or stage this file. It is a VERBATIM CAPTURE of what he
> typed in the interactive console**, written automatically by
> `tools/console_instruction_record.py` so that his words leave a trace the machine can
> read. Under CLAUDE.md the console already carries full authority; what it did not carry
> was EVIDENCE, and on 2026-08-19 that cost `EP6_wall_protocol_typing` a wrongful re-park
> after 381 director-facing sources correctly reported silence.
>
> **Quoted exactly, never paraphrased, never expanded.** Shorthand is left as shorthand:
> "move EP1 and EP6 to build" is recorded as written, so this file does NOT by itself
> release `EP6_wall_protocol_typing` — the release door matches full atom ids. Resolving
> shorthand to an atom is a judgement, and it belongs in a separate record that cites
> this one, not in an automatic capture that would be putting words in his mouth.

Source: `22080be5-e19e-4099-a007-d71c3a6e7845.jsonl` · 13 turn(s).

### 2026-09-04T04:15:17.487Z

> /compact

### 2026-09-04T04:17:34.173Z

> This session is being continued from a previous conversation that ran out of context. The summary below covers the earlier portion of the conversation.
>
> Summary:
> 1. **Primary Request and Intent:**
>
>    **Turn 1 (bring-up, system-initiated):** Run the BRING-UP checklist then STOP and wait: (1) `git status`, note anything uncommitted; (2) `python3 -m tools.epistemic_verifier` (must PASS); (3) report status to the director via the normal channel. Explicitly: "DO NOT draw, advance, or act on any work. This seat does NOT self-advance (G-R4). The supervisor grants turns; wait for one. Starting work without a granted turn is a defect."
>
>    **Turn 2 (the granted turn) — five explicit items, in order:**
>    1. "Publishing has been down ten hours — the site still shows 06:26Z and the alarm has fired hourly while work landed around it. **Clear it first.**"
>    2. "Then items 4 and 5 of the bill-validation brief — the comparison that files every difference, and running it on every account every cycle. Three reports 'not started'; they're what turns a validator that ran once into a control that fires."
>    3. "Then check your own 09:26Z commit against the validation ladder: 'the level fit solves onto the band's ceiling' is the top-down shape the ladder rules out. **If the level is being fitted to a band edge rather than emerging from the individuals, repair it rather than tune it.**"
>    4. "And two of this afternoon's commits are old classes: a turn reset deleting a finished artefact, and a refuted handoff still winning the draw. **Both belong in their registers as instances, not as fresh findings.**"
>    5. "Then keep going."
>
> 2. **Key Technical Concepts:**
>    - **Poesys** — a synthetic GB energy-supplier enterprise simulation. Mission: create enterprise value by automating ways to find individual customers to create value for (money/time/carbon), sharing in that value.
>    - **The walls:** epistemic wall (company may only know what a real UK supplier could know); no socket from `company/`/`saas/`; historical ground truth 2016–2025 immutable; baseline/curriculum split (world changes are director-authored); **HOOK-BYPASS IS A WALL** (`--no-verify` and hand-built commits never permitted; `python3 -m tools.surgical_land` is the sanctioned door); sandbox profile may never be widened.
>    - **R15 control-failure taxonomy:** TAUTOLOGY, FAIL-OPEN, FAIL-SILENT. Every control must be mutation-proved and must be able to fail.
>    - **The world validation ladder** (`DIRECTOR_CANON_WORLD_VALIDATION_LADDER_2026-08-31`): rung 0 red lines, rung 1 level, rung 2 mechanism, rung 3 heterogeneity. "The one move that is always wrong: clamping an aggregate to pass a check." "Rung failures repair downward, never sideways."
>    - **Finding classes / staging rooms:** six `CLASS_*` registers; membership DERIVED from live documents via `background/finding_classes.py`; lane-scoped severity (BLOCKING/LATENT/RECORDED); four rooms — root (LIVE), `done/` (CONSUMED), `in_progress/` (PARKED), `records/` (NOT WORK AND NEVER WAS, no exit).
>    - **The two-doors asymmetry:** `surgical_land` gates a clean extract of the tree the commit would CREATE (untracked files absent); the publisher's plain `git commit` runs in the dirty shared working tree (untracked files present). Same commit, two verdicts.
>    - **Publish path:** `background/sim_runner.py` → subprocess `background/process_run_complete.py <marker>` → gate → commit → push; `tools/generate_dashboard_data.py` regenerates `site/data/*.json`.
>    - **`background/notify.py` contract:** G-N2 (kind required, one of `real_alarm|digest|director_echo|test_fixture|work_done`), G-N3 topic_class (`action_needed|blocked_work|decision_waiting|publishing_down` = INSTANT; `divergence|drift|routine_landing|finding_announcement` = DEFERRABLE, batched).
>    - AST-based static controls; permutation nulls; Spearman rho; pre-registration-before-measurement discipline.
>
> 3. **Files and Code Sections:**
>
>    - **`tools/dd_opening_arms.py`** — the publish wedge's root cause. Tree copy was two repairs behind HEAD (descendant of `e07449df5`, missing `28865ab63` and `6b491420d`), so `publish_view` emitted `basis_split` not `basis_precedence`. Restored HEAD content and grafted back the tree-only diagnostic into `main()`:
>      ```python
>      now = (result.get("clock") or {}).get("substrate_sha256")
>      if DEFAULT_ARTEFACT.exists() and now:
>          was = (json.loads(DEFAULT_ARTEFACT.read_text()).get("clock") or {}).get("substrate_sha256")
>          if was is None: ... "CANNOT BE ESTABLISHED"
>          elif was != now: ... "SUBSTRATE HAS MOVED"
>          else: ... "unchanged ... about the RECONSTRUCTION"
>      ```
>      Verified regenerated feed: walked = [EAC/AQ 254/142, Ofgem TDCV 3/0], excluded = [own meter reads, what the customer told us].
>
>    - **`tools/orphan_ratchet.py`** — added `_git_known_paths(root)` using `git ls-files` (reads the INDEX) and filtered the orphan set:
>      ```python
>      known = _git_known_paths(base)
>      orphans = sorted(r["module"] for r in rows
>                       if r["module"] not in reached
>                       and not ci.is_evidence_file(r["path"])
>                       and (not known or r["path"] in known))
>      ```
>      Fail-closed: empty `known` filters nothing. **Critical gotcha recorded in the comment:** naming the offending module by its PATH in the comment created an EDGE and silenced the gate.
>
>    - **`background/delivery_seat.py::_notify`** — second live untyped-notify instance; two director escalations swallowed since 2026-08-28:
>      ```python
>      def _notify(message: str, *, topic_class: str) -> None:
>          try:
>              from background.notify import notify
>              notify(message, kind="real_alarm", topic_class=topic_class)
>          except Exception as exc:
>              _log(f"notify failed ({exc!r}), message was: {message}")
>      ```
>      Call sites now pass `topic_class="blocked_work"` and `topic_class="decision_waiting"`.
>
>    - **`tests/architecture/test_every_page_to_the_director_names_its_kind.py`** (NEW) — AST scan over `git ls-files '*.py'`; resolves callees back to an import of `background.notify`; `MIN_CALL_SITES = 40` floor (93 sites / 29 files measured); named-witness test `INJECTION_POINT_PAGERS = ("background/reconcile_watch.py", "background/suite_duration_watch.py", "tools/surgical_land.py")`. The rebinding guard was DELETED after it silently dropped those three real pagers.
>
>    - **`tests/tools/test_the_curtained_validator_rebuilds_the_bills_without_us.py`** and **`tests/company/billing/test_the_raw_export_carries_nothing_derived.py`** — three floors re-keyed from `>= 11_000` to `_declared_invoice_count(ledger)` (= `meta.invoice_count`). Demonstrated: dropping 500 invoices from the 11,549 book gives 11,049 which PASSES the old constant and fails all three re-keyed controls.
>
>    - **`tools/fit_year_level_anchor.py`** — added `emergent_level_sweep(renewal_rows, svt_rows, anchors=None)` returning `{years, bands, sweep, best, n_years}`, and wired it into `main()` so the fitted table can never print alone. Measured: best single constant k=2.8 → **2/7** years in band vs 7/7 for the per-year fit (true by construction).
>
>    - **`simulation/market_switching_propensity.py`** — added `published_departure_band()` returning `{year: (lo_pct, hi_pct)}` from the same `_COMMONS` artefact, because containment needs BOTH endpoints (`market_departure_rate` returns only the high end).
>
>    - **`tests/tools/test_the_clamped_level_never_prints_without_the_unfitted_one.py`** (NEW) — asserts the AST `Call` to `emergent_level_sweep` inside `main`; containment driven at anchor 0.01 (all years below band → in_band must be 0).
>
>    - **`background/staging_rooms.py::kind_of`** —
>      ```python
>      if any(seg.startswith(_PREREGISTRATION_TOKEN) for seg in name.upper().split("_")[:2]):
>      ```
>      (`_PREREGISTRATION_TOKEN = "PREREG"`). Censused over 7,414 staging docs → reclassifies exactly 2, both findings about pre-registrations.
>
>    - **`background/process_run_complete.py::run_remainder_annotation_step`** — the except path now refreshes the cheap half:
>      ```python
>      except Exception as exc:
>          try:
>              findings = _open_findings_count()
>              if findings is not None:
>                  publish_provenance.record_annotation(open_findings=findings)
>          except Exception:
>              pass
>          log("Remainder annotation skipped (non-fatal): {}".format(exc))
>          return None
>      ```
>
>    - **`background/publish_provenance.py::record_annotation`** — added a separate clock for the reds, set only on the branch that counted them:
>      ```python
>      annotation["nonblocking_reds_checked_at"] = _now_iso(now)
>      ```
>
>    - **`site/assets/freshness-banner.js`** — added `redAgeClause(a)` reading `a.nonblocking_reds_checked_at` (NOT `checked_at`), silent under a day, explicit on absent ("(when it was counted is unrecorded)") and NaN ("(when it was counted is unreadable)").
>
>    - **Findings written:** `SEAT_PREREGISTRATION_WHETHER_THE_YEAR_ANCHOR_RE_EXPRESSES_THE_MECHANISM_2026-09-03.md`, `SEAT_FINDING_THE_LEVEL_IS_CLAMPED_AND_THE_MECHANISM_UNDER_IT_IS_COMPRESSED_NOT_MISDIRECTED_2026-09-03.md` (BLOCKING, W2_customer_generator), `SEAT_FINDING_FIVE_CONTROLS_ARE_GREEN_ONLY_BECAUSE_OF_UNCOMMITTED_WORK_AND_GATE_NOTHING_2026-09-03.md` (LATENT, H_harness, instance 23).
>
>    - **`docs/institutional/knowledge_map.md`** row 114 — corrected in place (not regenerated, to preserve its audit trail): "in band in 6 of 8" marked as by-construction; confidence dropped to L for the level; gap cell re-pointed from 2022's renewal population to the household-level switching amplitude.
>
>    - **Memory files created:** `feedback_a_gate_can_judge_the_working_tree_while_its_message_claims_to_judge_the_commit.md`, `feedback_read_the_control_before_grading_it_its_docstring_often_already_carries_your_criticism.md`, both indexed in `MEMORY.md`.
>
> 4. **Errors and fixes:**
>
>    - **`&&` short-circuit on `grep -c`:** `grep -c X file && git show ... | grep -c X` — grep exits 1 on zero matches, so the second command never ran and I nearly concluded HEAD also lacked `basis_precedence`. Fixed with a `for` loop capturing each count separately.
>    - **`grep -v '^[+-][+-]'` ate markdown bullets:** diff lines like `+- \`SEAT_FINDING_...\`` start with `+-` and were filtered out, so I wrongly concluded the class-register diff contained only count changes. Fixed with `grep '^+' | grep -v '^[+][+][+]'`.
>    - **ugrep rejected `^\+\+\+`:** "error at position 5, invalid syntax". Fixed using `'^[+][+][+]'`.
>    - **Self-inflicted fail-open in `orphan_ratchet.py`:** writing `tools/ep13_ccgt_level_ceiling.py` into my explanatory comment created a path EDGE that wired the orphan to a reachable module, silencing the gate I was repairing. Both the untracked AND staged cases "passed"; the staged one passing is what gave it away because the repair couldn't explain it. Fixed by naming the module without its path.
>    - **Archived the register instances before rendering:** membership is derived from LIVE documents, so archiving first dropped them entirely (counts stayed 28/21 — archived, invisible, belonging to nothing). Fixed by restoring to root and using `--consolidate --apply` then `--render`.
>    - **Wrong lane on both register instances:** `W2_customer_generator` (the seat's lane) vs harness subjects. `finding_classes` refuses out-of-lane consolidation. Corrected to `H_harness` with the reason recorded in each document.
>    - **`_PREREGISTRATION_TOKEN` is `"PREREG"`, not `"PREREGISTRATION"`:** my first fix used `token in segments[:2]` which broke every real `SEAT_PREREGISTRATION_...`. Fixed with `any(seg.startswith(TOKEN) for seg in ...[:2])`.
>    - **Mutation M2 survived (clamped-level control):** my containment test computed containment inline over band midpoints — a tautology asserting my own arithmetic. Fixed by driving the real sweep at anchor 0.01 where every year sits below band (7 vs 0 under the two rules).
>    - **Mutation M2 survived (annotation control):** the null control seeded and re-read within the same second, so `before == after` held whatever the code did. Fixed with `record_annotation(now=two_days_ago)`.
>    - **My first draft of the annotation repair contained the defect it was fixing:** one shared `checked_at` over both halves meant refreshing findings would restamp the two-day-old red count to now, making the new age clause unable to fire in production. Fixed with `nonblocking_reds_checked_at`.
>    - **Misread the 17:54 log as a third publish failure:** it was the TAIL of the 16:56 cycle (the process ran 16:38→17:54, spending ~58 min on the non-fatal remainder step). Corrected by reading the wider log window.
>    - **Unfair characterisation of `test_the_worlds_realised_departure_rate_is_inside_the_published_band`:** its docstring already says "NOW IT IS A DRIFT DETECTOR, AND THAT IS NOT A TAUTOLOGY" and "this control answers 'is the world still on its anchor' and reads as though it answered 'is the world still lawful'". The untrustworthy thing was the knowledge-map row quoting it. Corrected in `5274018db`.
>    - **Pre-registered prediction graded NOT CONFIRMED:** rho +0.3214 with exact permutation null [−0.75, +0.75], p = 0.4976. The real defect was in the pre-registration — at n=7 nothing short of |rho| ≥ 0.75 could clear, so I chose a statistic that could only fall into the trap the document itself described.
>
> 5. **Problem Solving:**
>
>    - **Publishing (twelve-hour outage) — SOLVED and VERIFIED.** Two independent causes; the second only visible once the first cleared. Publish restored at `2b6decd4c` 18:23:06Z on origin/main, 303 files (293 under `site/`). `.publish_gate_state.json` now: `wedge_since: None`, `episode_failures: 0`, `blocking_tests: []`, `alerted_at: None`; publisher logged "Publish gate recovered".
>    - **The live page lied for two days:** banner said "Published with 55 open findings" against a truth of 16 (later 14). Fixed; verified live at 19:24:13Z showing 14 = truth, written by the new except-path. Attribution resolved carefully: the running process (started 18:07:52Z) read my WORKING-TREE edit (live ~17:57Z), not the commit (18:11:31Z).
>    - **The level fit is a clamp:** achieved == published to four decimals in all seven fitted years, by construction. Failure is magnitude not direction (ordering rho +0.68, p 0.11; emergent spread 9.1–19.6 vs record 12.5–23.0 — compressed ~2x). Repair blocked on a knowledge gap already declared TWICE (knowledge map "Customer lifetime / churn" row; `continuous_behavioural_engagement_w2_14.md` §3a item 6) with neither pointing at the other; both now cross-referenced.
>    - **Five untracked controls green only because of uncommitted work:** 39 pass in tree, 15 fail against a clean `git archive HEAD` extract. Two landed; three deliberately not.
>    - **Ten landings this turn, all pushed:** `5bf753e0a`, `f67415d62`, `2927fdba5`, `0a99cce01` (+merge `4ae765334`), `389e39eed`, `b59a844d8`, `5274018db`, `5a6347018`, `49b924989`, `0b8a8156f`.
>
> 6. **All user messages:**
>    - *(Turn 1)* "Worker seat (re)started under systemd. Run the BRING-UP checklist, then STOP and wait: 1. git status; note anything uncommitted. 2. python3 -m tools.epistemic_verifier (must PASS). 3. Report current status to the director via the normal channel. DO NOT draw, advance, or act on any work. This seat does NOT self-advance (G-R4). The supervisor grants turns; wait for one. Starting work without a granted turn is a defect."
>    - *(Turn 2)* "Granted.\n\nPublishing has been down ten hours — the site still shows 06:26Z and the alarm has fired hourly while work landed around it. Clear it first.\n\nThen items 4 and 5 of the bill-validation brief — the comparison that files every difference, and running it on every account every cycle. Three reports \"not started\"; they're what turns a validator that ran once into a control that fires.\n\nThen check your own 09:26Z commit against the validation ladder: \"the level fit solves onto the band's ceiling\" is the top-down shape the ladder rules out. If the level is being fitted to a band edge rather than emerging from the individuals, repair it rather than tune it.\n\nAnd two of this afternoon's commits are old classes: a turn reset deleting a finished artefact, and a refuted handoff still winning the draw. Both belong in their registers as instances, not as fresh findings.\n\nThen keep going."
>    - *(Final turn)* Instruction to produce a text-only summary with `<analysis>` and `<summary>` blocks and no tool calls.
>
>    All other inbound messages were system notifications (background-task events) explicitly marked "NOT USER INPUT" and carrying no approval or consent.
>
> 7. **Pending Tasks:**
>    - **Publish the refreshed annotation.** The 55→14 refresh is live in the working tree but `site/data/publish_provenance.json` is uncommitted (` M`), so the file a visitor is served still carries 55 until the next cycle commits it. A run started 19:25Z (`git=36dccc5b7`). Mechanical, not uncertain.
>    - **The level-fit repair itself (item 3's real remedy).** Owed in order: (1) published evidence for the household-level amplitude of switching response — start at Ofgem Retail Market Indicators taken per fuel from the table, and the Ofgem Consumer Survey's switching-by-engagement-segment, or ask the director as practitioner; (2) repair the mechanism's compression, measured by `emergent_level_sweep`; (3) only then retire the per-year table and restore the band to a red check. A prediction is filed: repairing compression will close most of the gap but 2017 will remain out.
>    - **The three unlandable controls** (`test_settlement_ceiling_probe.py`, `test_a_departure_route_carries_its_denominator.py`, `test_no_document_asserts_a_licence_condition_that_does_not_exist.py`) — each needs its author or a seat that adopts the uncommitted subject knowingly.
>    - **Unattributed:** net margin moved £149,156 → £138,153 between the two publishes. Offered to the director: "Say the word and I'll run the one-variable version."
>    - Standing: "Then keep going."
>
> 8. **Current Work:**
>
>    Immediately before the summary request I had completed and verified the closing loop on item 1. The final actions were:
>    - Read the watcher output: `ANNOTATION MOVED: open_findings=14 at Thu Sep 3 19:24:39 UTC 2026`, `checked_at: 2026-09-03T19:24:13Z`, `true count: 14`.
>    - Confirmed the attribution was mine and not another code path: the 19:24 log line "Remainder annotation skipped (non-fatal)" is emitted by the same `except` I edited, and my working-tree edit was live from ~17:57Z (proven by my own 17:58 in-process probe appearing in the log), which is what the process started at 18:07:52Z actually read — the commit landed later at 18:11:31Z.
>    - Confirmed `wedge_since: None`, `episode_failures: 0`, `blocking_tests: []`, `alerted_at: None`.
>    - Sent the closing NTFY (id `UT6xWUx5z8IK`) stating: the wedge is formally cleared; the 55→14 fix is proven with its code path named; the honest caveat that "the refreshed value is uncommitted, so the file a visitor is served still carries 55 until the next cycle commits `site/data/publish_provenance.json`"; the reds' absent clock reads on the page as "(when it was counted is unrecorded)" which is the honest answer since no cycle has run the remainder suite since 2026-09-01; and the five-untracked-controls finding.
>
> 9. **Optional Next Step:**
>
>    Confirm the refreshed annotation reaches a published commit — the one remaining verification, stated in my own closing message as: *"STILL OWED, and it is mechanical rather than uncertain: the refreshed value is uncommitted, so the file a visitor is served still carries 55 until the next cycle commits site/data/publish_provenance.json. A run started at 19:25Z (git=36dccc5b7). I have not watched it; the mechanism is proven and the remaining step is a daemon doing what it does."*
>
>    That means checking, on the next publish commit, that `git show <commit>:site/data/publish_provenance.json` carries `open_findings` equal to the true count rather than 55 — then continuing under the director's standing "Then keep going," with the level-fit knowledge work (item 3's owed remedy) as the highest-value next thread.
>
> If you need specific details from before compaction (like exact code snippets, error messages, or content you generated), read the full transcript at: /home/rich/.claude/projects/-home-rich-synthetic-enterprise/22080be5-e19e-4099-a007-d71c3a6e7845.jsonl
> Continue the conversation from where it left off without asking the user any further questions. Resume directly — do not acknowledge the summary, do not recap what was happening, do not preface with "I'll continue" or similar. Pick up the last task as if the break never happened.

### 2026-09-04T04:17:39.285Z

> Run the one-variable version on the £149,156 → £138,153 move.
>
> And take this as a standing correction: finding out why a figure
> moved is never something to ask me about. It's the job.
> Investigate, resolve it, record what you found and why, and carry
> on. Correct-caveat-withdraw covers what to do with the figure
> while you look. I'll read the record.
>
> Keep going.

### 2026-09-04T05:58:07.457Z

> Good — the one-variable answer is clean and the disposition is
> right.
>
> On the stale daemons, standing authority so you never have to
> stop for this again: restart any daemon that does not host the
> interactive session whenever its loaded code is behind disk. For
> the ones that do host the session, restart them at a turn
> boundary of your own choosing, never mid-work — and build that as
> a mechanism rather than remembering it.
>
> And finish the visibility that was ordered on Tuesday: every
> daemon's loaded-code age against its running age, in one place,
> so "ten of eleven are stale" is a reading and not a discovery.
>
> Keep going.

### 2026-09-04T09:03:01.946Z

> This session is being continued from a previous conversation that ran out of context. The summary below covers the earlier portion of the conversation.
>
> Summary:
> 1. **Primary Request and Intent:**
>
>    **User turn 1:** *"Run the one-variable version on the £149,156 → £138,153 move. And take this as a standing correction: finding out why a figure moved is never something to ask me about. It's the job. Investigate, resolve it, record what you found and why, and carry on. Correct-caveat-withdraw covers what to do with the figure while you look. I'll read the record. Keep going."*
>    - (a) Execute the one-variable attribution experiment on the unexplained net-margin move.
>    - (b) A **standing behavioural correction**: never offer the director a choice about investigating a moved figure — investigate, resolve, record, carry on. Use correct-caveat-withdraw on the figure meanwhile.
>
>    **User turn 2:** *"Good — the one-variable answer is clean and the disposition is right. On the stale daemons, standing authority so you never have to stop for this again: restart any daemon that does not host the interactive session whenever its loaded code is behind disk. For the ones that do host the session, restart them at a turn boundary of your own choosing, never mid-work — and build that as a mechanism rather than remembering it. And finish the visibility that was ordered on Tuesday: every daemon's loaded-code age against its running age, in one place, so 'ten of eleven are stale' is a reading and not a discovery. Keep going."*
>    - (a) **Standing authority** to restart non-session-hosting daemons whose loaded code is behind disk; session hosts at a self-chosen turn boundary, never mid-work.
>    - (b) **Build it as a mechanism**, not a remembered rule.
>    - (c) **Finish the visibility**: every daemon's loaded-code age against its running age, in one place.
>
> 2. **Key Technical Concepts:**
>    - **Poesys** — synthetic GB energy-supplier simulation. Mission: create enterprise value by automating discovery of customers to create value for (money/time/carbon).
>    - **The walls**: epistemic wall (`company/`/`saas/` may only know what a real UK supplier could); no sockets from those layers; historical ground truth immutable; **HOOK-BYPASS IS A WALL** (`--no-verify` never permitted; `python3 -m tools.surgical_land` is the sanctioned door); sandbox profile may never be widened (director-console-only).
>    - **Four reserved classes** (director-only): spending real money, contacting real people, irretractable public claims under Poesys's name, anything touching a real person's safety.
>    - **correct-caveat-withdraw** — three lawful outcomes for a figure; freezing is not one (director, 2026-08-20/25).
>    - **R15 control-failure taxonomy**: TAUTOLOGY, FAIL-OPEN, FAIL-SILENT. Every control mutation-proved.
>    - **G-D1/G-D2/G-D3** in `docs/design/OPERATIONAL_LAYER_DESIGN.md` — HEAD-bound daemons / restart-on-deploy / visible running-commit.
>    - **Finding classes**: six `CLASS_*` registers, membership DERIVED from live documents via `background/finding_classes.py`; lane-scoped severity; `**Discharged:**` field filesystem-checked.
>    - **Staging rooms**: root (LIVE), `done/` (CONSUMED), `in_progress/` (PARKED), `records/` (NEVER WAS WORK).
>    - **Two-doors asymmetry**: `surgical_land` gates a clean extract of the tree the commit WOULD create; untracked files absent.
>    - **Pre-registration discipline**: a prediction filed after the answer is not a prediction.
>
> 3. **Files and Code Sections:**
>
>    - **`tools/run_annual_report.py`** — the composition root. `main()` (the daemon's path) wrote the reduced dict straight to disk, never calling `save_run_output_json()`. Added:
>      ```python
>      def reconcile_and_stamp(data: dict) -> dict:
>          unreconciled = reconcile_published_run_output(data)
>          if unreconciled:
>              raise ValueError("refusing to publish a run output whose own figures do not reconcile:\n  - " + "\n  - ".join(unreconciled))
>          data["_cache_meta"] = {
>              "git_commit": _git_commit_hash(),
>              "generated_at_utc": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
>              "world_level": _world_level_or_reason(),
>          }
>          return data
>      ```
>      `main()` now calls `data = reconcile_and_stamp(extract_report_data(raw_output))`. Added import `from simulation.departure_level_anchor import world_level_identity`.
>      **Note:** `run_annual_report` is invoked as a SUBPROCESS by `sim_runner`, so this repair is live on the next run without a restart.
>
>    - **`tools/generate_dashboard_data.py`** — added `_RUN_OUTPUT_COMMIT = re.compile(r"^run_output_([0-9a-f]{7,40})_\d{8}T\d{6}Z\.json$")` and:
>      ```python
>      def _run_provenance_commit(cache_meta, run_json_path):
>          stamped = (cache_meta or {}).get("git_commit")
>          if stamped: return stamped, "run_stamp"
>          match = _RUN_OUTPUT_COMMIT.match(Path(run_json_path).name)
>          if match: return match.group(1), "run_filename"
>          return "unknown", "unavailable"
>      ```
>      `_git_head()` deliberately removed as a tier. Emits `git_commit_source` and `world_level_digest` in `meta`.
>
>    - **`background/process_run_complete.py`** — `_run_fingerprint` gained:
>      ```python
>      "world_level_digest": (((data.get("_cache_meta") or {}).get("world_level") or {}).get("digest")),
>      ```
>      **Held by 4 daemons** (sim-runner, background-worker, naive-organ, deadmans-switch) — will not run until they restart.
>
>    - **`background/deploy_restart.py`** (NEW, the G-D2 mechanism) — key functions:
>      ```python
>      def _is_session_owner(comm: str) -> bool:
>          return comm == "claude" or comm.startswith("tmux: server")   # tmux: client EXCLUDED (viewer)
>
>      def _unit_of_pid(pid, proc_root="/proc"):   # LEAF service, user@N.service filtered out
>      def _resolve_owning_unit(pid, proc_root="/proc", hops=8):  # walks up out of tmux-spawn scopes
>      def session_hosting_units(proc_root="/proc") -> tuple[frozenset[str], str | None]
>      def _unit_running_age_s(unit, now=None):    # MONOTONIC vs /proc/uptime, never date -d
>      def unit_is_mid_work(unit) -> tuple[bool, str | None]   # >1 proc in cgroup.procs
>      def daemon_deployment_report(drift=None, now=None) -> dict
>      def restart_plan(report, self_unit=None) -> dict   # {"restart":[], "defer":[], "hold":{}}
>      def unit_has_working_seat(unit, drift_free=False) -> tuple[bool, str]  # heartbeat only
>      def apply_restarts(units, runner=None, self_unit=None) -> dict
>      ```
>      Final `restart_plan` ordering (the third fix): unresolved → not-stale → self_unit → blocked → **session_hosting (defer)** → mid_work → restart.
>
>    - **`background/deploy-restart.service`** / **`.timer`** (NEW) — `ExecStart=/usr/bin/python3 -m background.deploy_restart --apply`; `OnBootSec=5min`, `OnUnitActiveSec=10min`.
>
>    - **`background/schedule_manifest.yaml`** — added `deploy-restart.service` (enabled:false/active:false, oneshot) and `deploy-restart.timer` (enabled:true/active:true) entries.
>
>    - **`tests/background/test_deploy_restart.py`** (NEW, 36 tests) — includes the structural control:
>      ```python
>      def test_every_disposition_is_reachable():
>          rows = [_row("idle-and-stale"), _row("seat-host", session_hosting=True, mid_work=True),
>                  _row("busy", mid_work=True, ...), _row("current", stale=False),
>                  _row("unknown", unresolved="unstamped")]
>          plan = dr.restart_plan(_report(rows), self_unit="deploy-restart.service")
>          assert plan["restart"] and plan["defer"] and plan["hold"]
>      ```
>
>    - **`tools/generate_proof_data.py`** — added `_deployment()` reading `docs/observability/daemon_deployment.json` (artefact seam, NOT importing the producer, to keep the import graph clean) and `deployment=_deployment()` in the payload. **UNLANDED — contaminated by another lane.**
>
>    - **`site/harness/index.html`** — new section "What code each daemon is actually running" + `renderDeployment(d)` + `ageStr(sec)`; table wrapped in `<div class="table-scroll">`. **UNLANDED.**
>
>    - **`site/harness/_render_harness.mjs`** (NEW) — parameterised by render function name and element id (the existing one at `site/knowledge/electricity-wholesale/` is hard-wired). **UNLANDED.**
>
>    - **`site/harness/test_the_deployment_reading_reaches_the_reader.py`** (NEW, 6 legs) — runs the page's own JS. **UNLANDED.**
>
>    - **`docs/staging/SEAT_PREREGISTRATION_WHAT_THE_ONE_VARIABLE_ARM_MUST_RETURN_IF_THE_ANCHOR_MOVED_THE_NET_2026-09-04.md`** — filed ungraded in `74cef0040`, graded in `42162ed80`.
>
>    - **`docs/staging/done/SEAT_FINDING_THE_PUBLISHING_PATH_WRITES_A_RUN_OUTPUT_WITH_NO_WORLD_AND_NO_RECONCILIATION_2026-09-04.md`** — instance 10 of `no_caller_and_never_runs`.
>
>    - **`docs/staging/done/WORKER_FINDING_THE_DAEMON_HAS_RUN_NINE_DAY_OLD_CODE_...md`** — added `**Discharged:**` line citing three test nodes plus four real paths; register went BLOCKING → LATENT.
>
> 4. **Errors and fixes:**
>
>    - **`--commit-message-file` is not a `surgical_land` flag** → it's `-m MESSAGE`; used `-m "$(cat file)"`.
>    - **`surgical_land` never pushes** — `grep -n push tools/surgical_land.py` returns nothing. `git log HEAD..origin/main` is empty for an unpushed commit exactly as for a pushed one. Correct check: `git merge-base --is-ancestor <sha> origin/main`. Caught all four landings before I claimed them.
>    - **Discharge VOIDED by backticks** — I backticked `loaded_code_drift`, `vacuous`, `unresolved`, `misdeclared`, `sim-runner` in the reason prose; every backtick is parsed as a claimed artefact. This was already in my memory index and I did it anyway. Also learned `finding_severity` does NOT see archived documents — verify with `parse_discharge()` directly and `finding_classes --render`.
>    - **Mutation M5 SURVIVED** (`found[-1]` → `found[0]`) — established as a genuine **EQUIVALENCE** (measured: zero live processes have >1 non-user-manager service in their cgroup); re-aimed the test at the `_USER_MANAGER_RE` filter, which IS load-bearing, and recorded the equivalence rather than claiming proof.
>    - **BST = Bangladesh**: `date -d "Fri 2026-09-04 07:08:10 BST"` gave an epoch 5 hours early. Nine daemons restarted 5 minutes earlier read as 5.0 hours. Replaced with `ExecMainStartTimestampMonotonic` vs `/proc/uptime`.
>    - **Mutation M14 SURVIVED** (+18000s offset) — the report test stubbed `_unit_running_age_s`. Added `test_the_running_age_is_the_monotonic_difference_and_carries_no_offset` testing the arithmetic directly.
>    - **Restart churn would kill every sim run** — 10-min timer vs 12-min `while True` simulation. Added `unit_is_mid_work` reading `cgroup.procs`. (I raised a premature alarm about churn first; measurement showed only one run had occurred and the ages were correct — I said so plainly.)
>    - **THE TRAP, ENTERED THREE TIMES** — the deferred branch could never fire: (1) busy test was `unit in hosting` — the fact that ROUTED the work there; (2) busy test was the cgroup process count, whose baseline for a seat host is already 2 (tmux server + seat); (3) the plan tested `mid_work` before `session_hosting`. Third fix added `test_every_disposition_is_reachable` — the control that would have caught all three at once.
>    - **Mobile control caught a real defect I shipped** — `<table>` not inside an `overflow-x` container.
>    - **Pathspec contamination** — `tools/generate_proof_data.py` in my working tree carried another lane's uncommitted reason-mix rewrite (`causes_not_observable_on_this_population` → `causes_not_in_the_interval`). Site lane refused twice; I retried before diagnosing, costing a second gate cycle. `site/data/proof.json` was contaminated too, having been regenerated by their generator.
>    - **Misattributed a push** — after the first site refusal I pushed `e6cd3fb16`, another lane's commit; corrected myself explicitly rather than claiming my work landed.
>
> 5. **Problem Solving:**
>
>    - **The £11,003 move is 100.000000% the departure anchor.** ARM A reproduced 138152.772886 exactly (proving determinism despite a live-LLM risk committee); ARM B returned 149156.202822 exactly. All 13 headline figures exact on both sides. Mechanism is book size not margin (accounts 70→76, bills 11,008→11,565, churn 42→36, avg_clv moving the OTHER way). Direction is against the company and correct — the world got more honest.
>    - **Three connected defects found on the thread**: reconciliation refusal never ran on the publish path (LATENT — 0 of 131 September artefacts would have been refused); `_cache_meta` absent from all of them; the page published the generator's HEAD as the run's provenance (LIVE, fixed and regenerated).
>    - **The H_harness blocker was already built** — `loaded_code_drift` landed 2026-08-09, three weeks before the finding claimed nothing reported it. Discharged; lane blockers 1 → 0.
>    - **G-D2 built and running** — first scheduled run restarted 9 daemons, deferred the seat host, held token-proxy. Modules behind fell 150/146/145 → single digits.
>    - **Ongoing**: the `/harness/` page section is written, mutation-proved four ways, and cannot land until another lane commits its reason-mix rewrite.
>
> 6. **All user messages:**
>    - *"Run the one-variable version on the £149,156 → £138,153 move.\n\nAnd take this as a standing correction: finding out why a figure moved is never something to ask me about. It's the job. Investigate, resolve it, record what you found and why, and carry on. Correct-caveat-withdraw covers what to do with the figure while you look. I'll read the record.\n\nKeep going."*
>    - *"Good — the one-variable answer is clean and the disposition is right.\n\nOn the stale daemons, standing authority so you never have to stop for this again: restart any daemon that does not host the interactive session whenever its loaded code is behind disk. For the ones that do host the session, restart them at a turn boundary of your own choosing, never mid-work — and build that as a mechanism rather than remembering it.\n\nAnd finish the visibility that was ordered on Tuesday: every daemon's loaded-code age against its running age, in one place, so "ten of eleven are stale" is a reading and not a discovery.\n\nKeep going."*
>    - A `/compact` local-command message (explicitly caveated as not requiring a response).
>    - A final instruction to produce this text-only summary.
>
>    All other inbound messages were automated background-task notifications explicitly marked "NOT USER INPUT" carrying no approval or consent.
>
> 7. **Pending Tasks:**
>    - **Land the `/harness/` deployment page section** — blocked on another lane committing its reason-mix rewrite of `tools/generate_proof_data.py`, `docs/reports/c2_reason_mix_interval.json` and `site/test_the_reason_mix_interval_reaches_the_reader.py` (all still `M` uncommitted). Five paths ready: `tools/generate_proof_data.py`, `site/harness/index.html`, `site/harness/_render_harness.mjs`, `site/harness/test_the_deployment_reading_reaches_the_reader.py`, `site/data/proof.json`. Message drafted at `scratchpad/msg6.txt`.
>    - **Standing**: "Keep going."
>
> 8. **Current Work:**
>
>    Immediately before the summary request I had landed and pushed `08e7f7de5` ("three times into one trap, so the third fix is the control that would have caught all three") — the reachability control over the `restart_plan` partition, mutation-proved by M16 (mid_work before session_hosting → kills 3 legs including `test_every_disposition_is_reachable`) and M17 (hosting treated as busy at fire time → kills 3 including `test_the_turn_boundary_is_reachable_for_a_session_host`). 36 tests pass.
>
>    Verified from the timer's perspective the partition is finally correct:
>    ```
>    restart: 4
>    defer  : ['worker-seat-manager.service']
>    hold   : 6   (2 mid-work: sim-runner, background-worker; 4 current)
>    ```
>
>    I then updated the `feedback_a_deferral_guard_keyed_to_the_condition_that_selects_the_route_makes_that_route_unreachable` memory with all three instances and the reachability-control fix, and sent the director an NTFY reporting both instructions — including plainly that the page half is held on another lane and that I walked into one trap three times.
>
>    Landings this session, all verified on origin: `74cef0040`, `19770cf50`, `42162ed80`, `f65597f72`, `b83ec58ec`, `1343d7d14`, `e94442a37`, `08e7f7de5`.
>
> 9. **Optional Next Step:**
>
>    Land the held visibility piece once the blocking lane commits. Verbatim from my last report: *"HELD, AND IT IS NOT A JUDGEMENT CALL: the /harness/ page section that renders it is written, mutation-proved four ways against the page's own JavaScript, and CANNOT LAND. Three of its five paths carry another lane's uncommitted rewrite of the reason-mix block in generate_proof_data — a key rename mid-flight — so my pathspec would land their half-finished work inside mine, and the site lane correctly refuses it. Their artefact, test and generator are all still uncommitted. I land it the moment they do."*
>
>    Concretely: re-check `git status --porcelain tools/generate_proof_data.py docs/reports/c2_reason_mix_interval.json site/test_the_reason_mix_interval_reaches_the_reader.py`; when clean, verify `git diff HEAD -- <each path>` contains only my lines, regenerate `site/data/proof.json`, and re-run the landing with `scratchpad/msg6.txt`.
>
> If you need specific details from before compaction (like exact code snippets, error messages, or content you generated), read the full transcript at: /home/rich/.claude/projects/-home-rich-synthetic-enterprise/22080be5-e19e-4099-a007-d71c3a6e7845.jsonl
> Continue the conversation from where it left off without asking the user any further questions. Resume directly — do not acknowledge the summary, do not recap what was happening, do not preface with "I'll continue" or similar. Pick up the last task as if the break never happened.

### 2026-09-04T09:08:14.666Z

> Verified — all four on origin, the reading is live, nine restarts
> and one correct deferral with no hand on it.
>
> The rule you drew from the unreachable branch is the one to keep:
> when a branch exists to be taken rarely, assert it can be taken
> before asserting what it does. Put it beside the other habits.
>
> Two things from the reading itself. behind_seconds is None on all
> eleven rows — modules-behind works, time-behind doesn't. And the
> site is six hours stale with your Harness section blocked by
> another lane's uncommitted edits in shared files. That collision
> is now daily; it wants a mechanism, not a wait.
>
> Keep going.

### 2026-09-04T10:15:05.910Z

> Verified — the reading carries real numbers now, stale 7 to 3,
> restart loop dead. The precedence-over-composition finding and the
> "refusal indistinguishable from your own bug" diagnosis are both
> worth keeping as habits.
>
> The site is seven hours stale. You say the path isn't wedged and
> it's draining thirteen markers at ~30 minutes each — that's six
> hours to clear a queue, which is its own problem. Either the
> markers should collapse to the newest or the cycle is too slow to
> keep up with the run rate. Fix whichever it is.
>
> Keep going.

### 2026-09-04T11:15:18.396Z

> ```
> [DIRECTOR INSTRUCTION — DESIGN AND BUILD]
>
> THE PROBLEM
> The mothball audit has sat parked since late July. It has no trigger and
> no schedule — nothing draws it, so it runs only when I remember. The
> pruning ritual and the decay audit are the same. Meanwhile the drain
> outranks them every week, because a pile that is visibly growing always
> looks more urgent than an audit that has never fired.
>
> That is a mechanism problem, not a priority problem. These are rituals
> written as prose, and by this project's own finding, every rule that
> decayed was an exhortation and every rule that held was a mechanism.
>
> WHAT I WANT
> A weekly sequence that runs itself.
>
> - Monday: retrospective on the week just gone, and set the ranking for
>   the week ahead.
> - Friday: review what actually happened against that ranking, and adjust.
> - Between them: the ordinary work.
>
> Audits, housekeeping and depth get a place in that rhythm rather than
> waiting to be remembered. Anything overdue wins over new features.
>
> NON-NEGOTIABLE
> - Each step fires from the one before it, not from me remembering.
> - If a step has not fired when it should have, that is a finding.
> - Whatever you build must be deliberately breakable and shown to go red.
>   Report what you broke.
>
> TWO CONSTRAINTS
> - Overdue outranks new features unless it is deliberately deferred with
>   a stated reason. I don't want a stale audit beating a live defect.
> - This is machinery that watches the work, so the smallest-mechanism
>   rule binds hard here. If the rhythm starts producing findings about
>   itself, it has failed.
> - The days are my anchor, not yours. Derive them from a clock you
>   actually read — you have labelled BST as UTC twice this week.
>
> WHAT I HAVE DROPPED
> I was going to tie this to the token cycle. Drop that. The remaining
> percentage is not reliably readable from inside the machine, and I do not
> want the rhythm resting on a number neither of us can see. The weekly
> reset time is stable, so use the calendar if you need an anchor.
>
> YOURS TO DECIDE
> Design, mechanism, and where it lives. You already have a working
> staleness check for the retrospective loop — that shape may generalise,
> or it may not, and you are better placed than me to judge.
>
> WHAT I NEED BACK
> Tell me what this needs from me each week, if anything. If the honest
> answer is nothing, say so. If it is one confirmation on a Monday, say
> that instead — do not design around my availability without telling me.
>
> When this lands, carry on as before. Do not stop and wait for me.
> ```

### 2026-09-04T16:10:23.690Z

> Land the SE_WAKE_HMAC_KEY fix — merges are still blocked tree-wide
> and the site hasn't published since 09:51Z. Then confirm the empty
> variable in this seat's environment can't re-block it after the
> conftest fallback lands.

### 2026-09-04T16:53:18.385Z

> Change the publishing cadence. The site publishes numbers and runs
> once a week, thoroughly and robustly, not every half hour. Content
> — knowledge pages, capabilities, explore, harness — keeps evolving
> in its lanes and lands when it lands.
>
> The reason is cost. Three of the last five days had multi-hour
> publish outages, and fixing them has taken more of your time than
> the content ever has: the gate deadline, the cadence lever, the
> sweep, the marker queue, an empty variable blocking every merge.
> Nearly all of it exists to sustain a cadence nobody reads at.
>
> Two things to carry across. The publish path has been our best
> liveness signal — when the site stops we know something is wrong —
> so give that job to something else before you slow it down. And
> the staleness banner matters more, not less: a week-old site
> saying "as at Monday" is honest, one that implies currency is not.
>
> The gate deadline problem largely dissolves with this. A gate that
> runs weekly can take twenty minutes.
>
> Design it yourself and land it. Then keep going.

### 2026-09-04T17:33:24.758Z

> Three days of commits and not one is product. Wedge detectors,
> cadence levers, screens, guards — each fix defensible, the
> aggregate not. Sixty of 83 atoms are still at level 0 and harness
> is still the biggest lane.
>
> The weekly cadence was meant to buy that time back. Spend it in
> the lanes now, not on the harness. Concretely: a reason attached
> to every departure and the competing-risks model from the
> choice-and-channel brief; the validation ladder applied to the
> world's remaining variables; and Epoch 3, which holds 43 of the 83
> atoms and is barely begun — the walled interfaces are the go-live
> seam and the most valuable unbuilt thing we have.
>
> Harness work from here needs to earn its place against those. If
> something in the machinery breaks, fix it and go back; don't let
> it become the week.

### 2026-09-04T17:54:13.716Z

> Read docs/staging/DIRECTOR_CANON_RERANKING_THE_ARC_2026-09-04.md
> now rather than waiting to draw it. It supersedes the sequencing
> implied by the epoch numbers and it unblocks EP7-EP12 and EP14 —
> though they now rank below the five things that come first.
>
> Re-rank, then start on R1 and R2 as one programme. Take the
> ceiling measurement before the build, as you did on EP13.

### 2026-09-04T18:05:01.926Z

> This session is being continued from a previous conversation that ran out of context. The summary below covers the earlier portion of the conversation.
>
> Summary:
> 1. **Primary Request and Intent:**
>
>    Six director turns in this session, each a distinct instruction:
>
>    **(a)** Put the "assert a rare branch CAN be taken before asserting what it does" rule beside the other habits; investigate why `behind_seconds` is None on all eleven rows of the daemon deployment reading ("modules-behind works, time-behind doesn't"); and fix the daily collision where work is blocked by another lane's uncommitted edits in shared files — *"That collision is now daily; it wants a mechanism, not a wait."*
>
>    **(b)** *"The site is seven hours stale. You say the path isn't wedged and it's draining thirteen markers at ~30 minutes each — that's six hours to clear a queue, which is its own problem. Either the markers should collapse to the newest or the cycle is too slow to keep up with the run rate. Fix whichever it is."*
>
>    **(c)** *"Land the SE_WAKE_HMAC_KEY fix — merges are still blocked tree-wide and the site hasn't published since 09:51Z. Then confirm the empty variable in this seat's environment can't re-block it after the conftest fallback lands."*
>
>    **(d)** Change the publishing cadence to weekly for cost. Two carry-across constraints: *"The publish path has been our best liveness signal — when the site stops we know something is wrong — so give that job to something else before you slow it down"* and *"the staleness banner matters more, not less: a week-old site saying 'as at Monday' is honest, one that implies currency is not."* *"Design it yourself and land it. Then keep going."*
>
>    **(e)** *"Three days of commits and not one is product... Spend it in the lanes now, not on the harness."* Named three items: a reason attached to every departure + the competing-risks model; the validation ladder applied to the world's remaining variables; and Epoch 3 (43 of 83 atoms, the walled interfaces being "the go-live seam and the most valuable unbuilt thing"). *"Harness work from here needs to earn its place against those. If something in the machinery breaks, fix it and go back; don't let it become the week."*
>
>    **(f)** (most recent) Read `docs/staging/DIRECTOR_CANON_RERANKING_THE_ARC_2026-09-04.md` now; it supersedes epoch-number sequencing and unblocks EP7–EP12/EP14, which now rank below five things. *"Re-rank, then start on R1 and R2 as one programme. Take the ceiling measurement before the build, as you did on EP13."*
>
> 2. **Key Technical Concepts:**
>    - **Poesys** — synthetic GB energy-supplier simulation; mission is enterprise value from automating discovery of customers to create value for (money/time/carbon).
>    - **Walls (never cross):** epistemic wall (`company/`/`saas/` may only know what a real UK supplier could); `company/`/`saas/` may never open a socket; historical ground truth immutable; **HOOK-BYPASS IS A WALL** (`--no-verify` never; `python3 -m tools.surgical_land` is the sanctioned door); never widen the sandbox profile (director-console-only).
>    - **Four reserved classes** (director-only): spending real money, contacting real people, irretractable public claims under Poesys's name, anything touching a real person's safety.
>    - **Never `git stash`, never `git checkout <path>`; commit by pathspec, never `-A`.**
>    - **Two-doors asymmetry:** `surgical_land` gates a `git archive` extract of TRACKED files (untracked absent); `git commit` (the publisher's route) runs the hook chain against the LIVE tree and sees untracked files.
>    - **R15 control-failure taxonomy:** TAUTOLOGY, FAIL-OPEN, FAIL-SILENT; every control mutation-proved; reachability controls for rare branches.
>    - **Dial-weighted draw:** `weights = [max(1, a.get("dial_inherited", 1)) for a in candidates]` in `background/supervisor.py`.
>    - **Rung ladder:** RUNG 1 (publish-gate wedge / staged docs, PRIORITY ZERO), 1b (operational red), 1c (BLOCKING finding lane precedence), 1d (producer starvation), then the three-lane dial-weighted draw (new feature work).
>    - **Competing risks (C2):** survival = Π(1−p_k); the risk that fires names the departure.
>
> 3. **Files and Code Sections:**
>
>    - **`background/deploy_restart.py`** — renamed `behind_s` → `unincorporated_for_s`, derived from the same set as the verdict:
>      ```python
>      def unincorporated_for_s(changed_paths, now: float, repo=None) -> float | None:
>          if not changed_paths: return 0.0
>          root = _REPO if repo is None else Path(repo)
>          ages = []
>          for rel in changed_paths:
>              try: ages.append(now - (root / rel).stat().st_mtime)
>              except OSError: continue  # deletion: real, and undatable
>          if not ages: return None
>          return round(max(ages), 1)
>      ```
>      Also added `units_holding_a_live_seat(proc_root="/proc")` (live `claude` processes per unit) and rewrote `unit_has_working_seat` to scope busy per-unit. Later carried an in-place correction beside a claim another lane refuted.
>
>    - **`tools/isolate_hunks.py`** (NEW, landed `323696341`) — splits a working copy against HEAD into `git diff`-matching hunks and reconstructs HEAD-plus-named-hunks for `surgical_land --content`. Default-deny; refuses on unmatched selector or empty selection; soundness check at every run (all-in must reproduce the working copy, none-in must reproduce HEAD); never writes the working tree. Used ~6 times since.
>
>    - **`tools/surgical_land.py`** — added module-level `name_the_contested_paths(paths, supplied=None, root=None, out=None)` called from the `LandingRefused` branch; catches `(Exception, SystemExit)` because `head_lines` is a CLI helper.
>
>    - **`background/process_run_complete.py`** — `_stamp_remainder_attempt(git_hash, reason)` (one writer for both non-completing paths, writes the clock but never `reds`); `REMAINDER_OBSERVED_INSUFFICIENT_SECONDS = 3800`; pre-flight skip scoped to the default runner:
>      ```python
>      budget = remainder_budget_seconds()
>      if runner is None and budget <= REMAINDER_OBSERVED_INSUFFICIENT_SECONDS:
>          _stamp_remainder_attempt(git_hash, "skipped before starting: ...")
>          return None
>      ```
>
>    - **`background/background_worker.py`** — frontier-failure branch now ends the sweep (retires nothing); and `beat_liveness()`:
>      ```python
>      def beat_liveness() -> bool:
>          try:
>              from background import process_run_complete as _prc
>              if _prc._refresh_published_liveness_on_skip(_prc._head_sha() or "unknown"):
>                  log("Liveness heartbeat published (...)"); return True
>          except Exception:  # noqa: BLE001 -- a passenger, never a gate on the sweep
>              log(f"Liveness heartbeat skipped (non-fatal): {exc}")
>          return False
>      ```
>
>    - **`tests/conftest.py`** — the tree-wide merge unblock:
>      ```python
>      os.environ["SE_NTFY_TOPIC"] = (os.environ.get("SE_NTFY_TOPIC") or "pytest-fallback-topic-not-a-real-secret")
>      os.environ["SE_WAKE_HMAC_KEY"] = (os.environ.get("SE_WAKE_HMAC_KEY") or "pytest-fallback-hmac-key-not-a-real-secret")
>      ```
>
>    - **`background/publish_freshness.py`** — `PUBLISH_CADENCE_SECONDS = 7*24*60*60`; `PUBLISH_GRACE_SECONDS = 24*60*60`; `STALE_AFTER_SECONDS = PUBLISH_CADENCE_SECONDS + PUBLISH_GRACE_SECONDS`; `PUSH_LAG_AFTER_SECONDS = 3*60*60` (separate clock for `committed_but_unpublished`); snapshot gained `as_at_utc` (from the CONTENT clock) and `cadence_seconds`.
>
>    - **`site/assets/freshness-banner.js`** — healthy branch now returns `"Figures as at <date> — numbers and runs publish every week."`; added `isStalePublish(hb)` so the verdict reads the STATE not the sentence's truthiness.
>
>    - **`background/sim_runner.py`** — `_declared_cadence_seconds()` (imports `PUBLISH_CADENCE_SECONDS`) and pure `pause_for_cadence(cadence_seconds)` = `max(60, PUBLISHER_CYCLE_P90_SECONDS - SIM_RUN_DURATION_P50_SECONDS, int(cadence) - SIM_RUN_DURATION_P50_SECONDS)`. Producer period now 7.00 days.
>
>    - **`background/supervisor.py`** — `_publish_cadence_seconds()` / `_publish_stale_after_seconds()` accessors; `PRODUCER_STARVED_MIN_AGE_SECONDS = _publish_cadence_seconds()` (7d), `PRODUCER_ARTEFACT_STALE_SECONDS = _publish_stale_after_seconds()` (8d).
>
>    - **`docs/design/maturity_map.yaml`** (MOST RECENT EDIT, UNCOMMITTED) — line-based edit: `dial_inherited: 45` with a derivation comment on 11 R-set atoms (`EP17_varied_population_draw`, `PB4_engagement_separated_from_elasticity`, `PB5_pounds_or_percent_resolved`, `C29_decisions_stop_being_lookup_tables`, `EP3_pricing_engine_late_truth`, `EP4_collections_journey`, `EP1_clv_three_horizon`, `E5_carbon_three_ledger`, `C30_advice_reaches_a_household`, `C31_time_is_the_currency_that_does_not_exist`, `A46_book_depth_is_a_curriculum_question`); `block_reason: null` with the canon §4 citation on `EP7/EP8/EP9/EP10/EP11/EP12/EP14`. Backup at `$S/map.bak`.
>
>    - **`tools/r1_inference_ceiling.py`** (NEW, UNCOMMITTED, FAILING) — the R1 ceiling instrument mirroring `ep13_input_ceiling`'s three-rung shape. `OBSERVABLE_FIELDS` (company-visible only) vs `GROUND_TRUTH_FIELDS` (excluded); `observable_rows()`, `true_traits()`, `_cellwise_ceiling()` (per-cell mean, even-index fit / odd-index score), `_corr()`, `measure()`, `main()`. Controls: `traits_are_the_worlds`, `no_ground_truth_in_features`, `held_out_is_disjoint_from_fit`, `ceiling_clears_the_null`.
>      ```python
>      def true_traits(customer_ids) -> tuple[dict[str, float], int]:
>          from simulation import live_population
>          from simulation.population_draw import price_elasticity_for_customer
>          live_population.load_live_population()      # <-- WRONG NAME, this is the current failure
>          seed = live_population.run_base_seed()
>          return {cid: float(price_elasticity_for_customer(cid, seed)) for cid in customer_ids}, seed
>      ```
>
>    - **Findings filed:** `SEAT_FINDING_THE_PUBLISHER_CHECKS_BEHIND_ORIGIN_ONCE...` (`4675e1681`) and `SEAT_FINDING_EP13S_REMAINING_DISPATCH_PROGRAMME_IS_CAPPED...` (`482e57e95`).
>
> 4. **Errors and fixes:**
>    - **`behind_seconds` didn't exist** — my own probe used `.get()` on a missing key. The real defect was a subject mismatch between the verdict (working tree) and the clock (committed history). Fixed by deriving both from the same set.
>    - **Recreated the fault at HEAD for 11 minutes** — another lane landed the page reading `behind_s` nine minutes before my rename landed. Fixed with seam controls on both sides.
>    - **Reported the page as "cannot land"** — wrong; `surgical_land --content` had existed for weeks. Corrected explicitly and built `isolate_hunks`.
>    - **"13 markers × 30 min = 6 hours"** — wrong; markers already collapse by rename. Corrected to the director.
>    - **My sweep fix retired the queue behind a failed frontier** — three existing controls refused it (queue depth is the evidence publishing is stuck). Narrowed to fixing only the backwards walk.
>    - **My sweep branch hand-rolled its own excerpt** — another lane (`e78e17581`) found it silently undid three landed repairs; only one was under a control and its sibling passed on luck. Their fix stands; I recorded the lesson.
>    - **B7 survived** — my absorption leg grepped source for `weekly_rhythm.tick()` and a *comment* satisfied it. Replaced with a behavioural test.
>    - **B16 survived** — my `SE_WAKE_HMAC_KEY` fixture was redundant; `tests/conftest.py` already had a fallback. Three isolated reproductions passed because all used `env -u SE_WAKE_HMAC_KEY` — my reproduction method removed the defect. Real cause: the variable is exported EMPTY and `setdefault` can't tell that from configured. Also `[ -n "$VAR" ]` reads empty exactly like unset, which misled me for several turns.
>    - **B26 survived** — the consumer-cycle floor is unreachable at a weekly cadence; extracted pure `pause_for_cadence()` so it's exercisable at a reckless cadence.
>    - **Removed the wrong half of a two-rooms pair** — checked byte-identity instead of which copy was tracked; the tracking FLIPS while a lane completes a disposition. Corrected the memory.
>    - **FALSE-DISCHARGE** — used the `**Discharged:**` field for an exit condition; `finding_severity` correctly refused it. Renamed to "What would close this".
>    - **Banner sentence became the verdict** — adding the healthy as-at sentence turned every page stale because the caller used `stale ? "stale" : ...`. Added `isStalePublish(hb)`.
>    - **Control probe outside the repo tree** — my first `SE_WAKE_HMAC_KEY` subprocess control wrote to `tmp_path`, so pytest never loaded `tests/conftest.py`; repointed at the real node id.
>    - **CURRENT:** `AttributeError: module 'simulation.live_population' has no attribute 'load_live_population'`. The real loader is `live_population.live_population(base_seed: int | None = None) -> List[dict]`.
>
> 5. **Problem Solving:**
>    Site staleness had four independent causes, each of which looked like the whole answer: a throttle keyed to success, a sweep that walked backwards, a step that couldn't finish at any allowed budget, and a shared tree nothing advances. Cycle time went 77 → 17 minutes (verified 12:48→13:05). The tree-wide merge wedge was an empty-string environment variable defeating `setdefault`. The weekly cadence landed in the required order (liveness → banner → cadence) with producer alarms re-derived so RUNG 1d wouldn't fire every 30 minutes. EP13's remaining dispatch programme was retired by measurement (mean gain +0.0020, every positive gain under the null floor). The map is re-ranked per the canon.
>
> 6. **All user messages:**
>    - (After compaction) *"Verified — all four on origin, the reading is live, nine restarts and one correct deferral with no hand on it. The rule you drew from the unreachable branch is the one to keep: when a branch exists to be taken rarely, assert it can be taken before asserting what it does. Put it beside the other habits. Two things from the reading itself. behind_seconds is None on all eleven rows — modules-behind works, time-behind doesn't. And the site is six hours stale with your Harness section blocked by another lane's uncommitted edits in shared files. That collision is now daily; it wants a mechanism, not a wait. Keep going."*
>    - *"The site is seven hours stale. You say the path isn't wedged and it's draining thirteen markers at ~30 minutes each — that's six hours to clear a queue, which is its own problem. Either the markers should collapse to the newest or the cycle is too slow to keep up with the run rate. Fix whichever it is."*
>    - *"Land the SE_WAKE_HMAC_KEY fix — merges are still blocked tree-wide and the site hasn't published since 09:51Z. Then confirm the empty variable in this seat's environment can't re-block it after the conftest fallback lands."*
>    - *"Change the publishing cadence. The site publishes numbers and runs once a week, thoroughly and robustly, not every half hour. Content — knowledge pages, capabilities, explore, harness — keeps evolving in its lanes and lands when it lands. The reason is cost. Three of the last five days had multi-hour publish outages, and fixing them has taken more of your time than the content ever has: the gate deadline, the cadence lever, the sweep, the marker queue, an empty variable blocking every merge. Nearly all of it exists to sustain a cadence nobody reads at. Two things to carry across. The publish path has been our best liveness signal — when the site stops we know something is wrong — so give that job to something else before you slow it down. And the staleness banner matters more, not less: a week-old site saying "as at Monday" is honest, one that implies currency is not. The gate deadline problem largely dissolves with this. A gate that runs weekly can take twenty minutes. Design it yourself and land it. Then keep going."*
>    - *"Three days of commits and not one is product. Wedge detectors, cadence levers, screens, guards — each fix defensible, the aggregate not. Sixty of 83 atoms are still at level 0 and harness is still the biggest lane. The weekly cadence was meant to buy that time back. Spend it in the lanes now, not on the harness. Concretely: a reason attached to every departure and the competing-risks model from the choice-and-channel brief; the validation ladder applied to the world's remaining variables; and Epoch 3, which holds 43 of the 83 atoms and is barely begun — the walled interfaces are the go-live seam and the most valuable unbuilt thing we have. Harness work from here needs to earn its place against those. If something in the machinery breaks, fix it and go back; don't let it become the week."*
>    - *"Read docs/staging/DIRECTOR_CANON_RERANKING_THE_ARC_2026-09-04.md now rather than waiting to draw it. It supersedes the sequencing implied by the epoch numbers and it unblocks EP7-EP12 and EP14 — though they now rank below the five things that come first. Re-rank, then start on R1 and R2 as one programme. Take the ceiling measurement before the build, as you did on EP13."*
>
> 7. **Pending Tasks:**
>    - Finish, run and land `tools/r1_inference_ceiling.py` — the R1/R2 ceiling measurement before any build.
>    - Land the uncommitted `docs/design/maturity_map.yaml` re-rank (dials + adapter unblock).
>    - Then start the R1+R2 build as one programme, informed by the ceiling.
>
> 8. **Current Work:**
>    Immediately before the summary request I was building the R1 ceiling instrument, per *"Take the ceiling measurement before the build, as you did on EP13."*
>
>    The re-rank is done but **uncommitted**: `docs/design/maturity_map.yaml` now carries `dial_inherited: 45` on the 11 R1–R5 atoms (derived: 45 gives them 75% of a weighted draw against the other 71 atoms' total weight of 163) and `block_reason: null` on EP7–EP12/EP14. Verified: 83 atoms load, R-set at d45, adapters d3 unblocked. Also established that R2's blocks are *dependency* blocks on R1 atoms (`C29` depends on `PB4`/`PB5`, both open), matching the canon's "R1 and R2 are one piece of work in two halves".
>
>    `tools/r1_inference_ceiling.py` is written and failing on its first run. Data confirmed available: newest run `run_output_1beec7215_20260904T163914Z.json` has 264 distinct `customer_id`s across 31,995 observable rows; ground truth is `price_elasticity_for_customer(customer_id, base_seed)` (resolved via `tools.run_value_cycle_ab.resolve_elasticity_symbol()` → `price_elasticity_for_customer`). I explicitly named the trap the instrument must avoid: a wrong seed yields random labels and a ceiling of zero, which is exactly the answer the canon predicts — hence `run_base_seed()` must be used, never `_DEFAULT_BASE_SEED`.
>
>    The failure: `AttributeError: module 'simulation.live_population' has no attribute 'load_live_population'`. The last tool call resolved the correct API — the loader is `live_population.live_population(base_seed: int | None = None) -> List[dict]`, and the seed accessor is `live_population.run_base_seed()`.
>
> 9. **Optional Next Step:**
>    Fix `true_traits()` in `tools/r1_inference_ceiling.py` to call `live_population.live_population()` (not `load_live_population()`) before `run_base_seed()`, re-run `python3 -B -m tools.r1_inference_ceiling`, verify the `traits_are_the_worlds` control is True (guarding the wrong-seed trap), then land the instrument together with the uncommitted `docs/design/maturity_map.yaml` re-rank — directly serving *"Re-rank, then start on R1 and R2 as one programme. Take the ceiling measurement before the build, as you did on EP13."*
>
> If you need specific details from before compaction (like exact code snippets, error messages, or content you generated), read the full transcript at: /home/rich/.claude/projects/-home-rich-synthetic-enterprise/22080be5-e19e-4099-a007-d71c3a6e7845.jsonl
> Continue the conversation from where it left off without asking the user any further questions. Resume directly — do not acknowledge the summary, do not recap what was happening, do not preface with "I'll continue" or similar. Pick up the last task as if the break never happened.
