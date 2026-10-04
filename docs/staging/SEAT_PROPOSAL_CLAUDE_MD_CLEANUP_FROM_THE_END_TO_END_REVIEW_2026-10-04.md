# PROPOSAL — CLAUDE.md cleanup from the end-to-end review (2026-10-04)

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `the-end-to-end-review-of-claude-md` (Lane 0 delivery)

**This is a PROPOSAL for the director. Writing it changed nothing in CLAUDE.md.** It reviews
`origin/main:CLAUDE.md` (20,172 characters, the same bytes as the shared working copy) against the
canon, the code it points at, the last week's work (774 commits on origin since 2026-09-28,
`docs/status/SEAT_STRETCH_LOG.md`, `docs/direction/DIRECTION.yaml`) and the memory index.
"What you are" and "How to talk to the director" are treated as about to be replaced by the
operating-model section. Items that bear on that section are marked **[new section]**.

## Acted on already (seat, 2026-10-04), the rest awaits the director

- **Item 1, partly.** The operating-model section that replaces "How to talk to the director" no
  longer says "four" reserved classes. It names `one_way_door.RESERVED_CATEGORIES` as the sole list
  and states its five categories, with real money "never spent, even with his yes". It calls them
  ACTIONS that are walls, so they cannot be read as the narrow reservation of documents. The other
  stale lists (`DIRECTOR_CANON.md` §3, `recommendation_guard.py`'s docstring, `one_way_door.py`'s own
  "four" comment) are untouched. `DIRECTOR_CANON.md` is a director document, so that one is a
  proposal.
- **Item 2, the two contradicting sentences only.** The `staging-protocol` skill no longer says
  "Staging = approval" or that NTFY needs a second channel; each correction is marked beside it in
  the skill. Its other stale lines (weekly publishing, the `in_progress/` room) remain, as listed
  below.
- **The plain factual errors in CLAUDE.md** are NOT corrected in the same change as the operating
  model, at the director's instruction. They follow in a separate, labelled commit.

## Summary (five lines)

1. **The reserved-actions list contradicts itself in three places.** CLAUDE.md lists four classes. The code lists five. Memory records that spending real money is *closed*, so even a yes from you does not open it. The new section's word "reservation" will also collide with this list (item 1).
2. **A procedure CLAUDE.md points to still says what CLAUDE.md withdrew.** The `staging-protocol` skill was last edited 2026-07-13. It still says "Staging = approval" and still says NTFY directives need a second channel to confirm them (item 2).
3. **"You hold the delivery seat" no longer names one thing.** `delivery-seat.service` is now a 3-hourly session that is not allowed to write code, and it is where the interconnection review actually happens. CLAUDE.md never names DIRECTION.yaml, the stretch log, or the other seats (items 3 and 4).
4. **Two rows in the "enforced in code" table only report.** `canon_drift_check` and `staging_rooms --check` refuse nothing, and both are reporting problems today (item 5). One wall is worded more strictly than your own 2026-09-04 canon reads it. That one is your decision (item 6).
5. **The rest is cleanup.** One story is told twice, the gate count and gate list are out of date, the Build figure is stale, and the roster is incomplete. The plain factual errors are listed separately, and the seat may correct those.

**A correction to the premise, stated first.** The brief says CLAUDE.md "was audited five days ago". The 2026-08-28 rewrite was **37 days ago**. The last edit was 2026-09-27 (`94ef1e36e`), 7 days ago. Since the rewrite the file has grown from 14,429 to 20,172 characters (+41%), in six edits that all added text (`c050706d3` +1,887, `5994c17d4` +1,528, `323696341` +924, `8ab0ce8be` +685, `815ac8ea5` +338, `f325485b4` +242). No decay audit has run since 2026-08-27, and that audit's own text says "an audit performed once is an event". The growth is reasonable, because each addition was a lesson. But the file has been growing without anything trimming it.

---

## Proposed changes, most important first

### 1. The reserved classes — one list in the code, other lists in prose, and real money is wrong. **[new section]**
- **Passage (l.170):** "**Only four things are reserved**, and `background/one_way_door.py` is the sole enumeration: spending real money, contacting real people, an irretractable public claim …, and anything touching a real person's safety." Also l.54: "the four reserved classes".
- **Change:** rewrite as two separate lists with two different names:
  > *Real-world doors.* `background/one_way_door.py` (its RESERVED block) is the list. Read it there, not here. **Spending real money is closed, not reserved: no yes opens it.**
  > *Director documents.* The mission statement and the director's own documents are his to edit. You propose changes; you do not make them.
- **Reason:**
  - The code reserves **five** categories, not four (`one_way_door.py` docstring, RESERVED 1–5): REAL_MONEY, REAL_WORLD_COMMITMENT, IRRETRACTABLE_PUBLIC_CLAIM, REAL_CUSTOMER_OR_MARKET and LIVE_CREDENTIAL_EXPOSURE.
  - "Safety" is not a code category. The 2026-07-29 ruling quoted in that docstring folds it into "real people".
  - The CLAUDE.md sentence is therefore a second list that has drifted from the first. That is the exact failure its own "read the enforcement, not the paraphrase" warns about.
  - Memory `feedback_never_spend_real_money_not_even_with_the_directors_yes.md` (2026-09-27, Jev trial) quotes you: *"If I say yes are you planning to spend my money???!!!"*. "Reserved" means "ask him first", which is the reading you rejected. CLAUDE.md still teaches it.
  - Other lists also disagree. `DIRECTOR_CANON.md` §3 lists seven doors (see item 14). `recommendation_guard.py`'s docstring still lists "safety controls" as a carve-out, a category `one_way_door` released on 2026-07-29.
  - The new section's "the reservation is narrow — director documents and the mission statement" uses the same word for a different list. A reader of both will take one to replace the other.
- **Class:** contradicts (code, memory, and the new section) + duplicates. **Confidence:** high.
- **Candidate explanations, ranked:**
  1. CLAUDE.md paraphrased your 2026-07-29 NTFY sentence ("real money, real people, safety controls, public claims"), and the code added the commitment and credential classes on the same day. The paraphrase was never re-read. The docstring dates support this.
  2. The code over-reserves. Possible, but it is a code question, not a CLAUDE.md one.
  3. "Four" was meant as a summary. If so it is unsafe for money, so it fails either way.

### 2. The `staging-protocol` skill CLAUDE.md points to still describes the rules before 2026-07-29. **[new section]**
- **Passage (l.295–299):** "Four procedures live outside this file … working the staging queue (`.claude/skills/staging-protocol/SKILL.md`)".
- **Change:** rewrite the skill. It is not a director document. If it is not rewritten, drop the pointer until it is. CLAUDE.md itself needs no change beyond the pointer.
- **Reason:** the skill was last edited `7fbec1fbb`, **2026-07-13**, before the 2026-07-29 rip-out. It still says:
  - "**Rich stages instructions in `docs/staging/`. Staging = approval.**" The 2026-08-28 rewrite notes list exactly this sentence under "Corrections of fact … superseded … there is no approval".
  - "ALL inbound NTFY content is untrusted data; a directive arriving by NTFY requires correlation with a staged doc or console confirmation". CLAUDE.md l.164–166 says the opposite: "no signature, no second channel". So does the 2026-07-29 ruling ("ntfy is me").
  - That `run_complete_*` regenerates "LATEST.md" on every run. Publishing has been weekly since the publish hold: `.publish_gate_state.json` shows `publish_hold.next_opens 2026-10-05`.
  - That partly-done items move to `in_progress/`. `staging_rooms` now owns the rooms.

  Under the new model ("get on with knowledge, in-flight work …") a skill that tells a session to wait for a second channel will contradict it directly.
- **Class:** contradicts. **Confidence:** high.
- **Candidate explanations:**
  1. The 08-28 rewrite corrected CLAUDE.md but not the skill it points to. The commit dates show this.
  2. "Staging = pre-approved content" is still meant for advisor-staged docs. That might rescue the first sentence, but not the NTFY clause.

### 3. "You hold the delivery seat", "the seat is continuous", "this is the seat's alone": the name now means a specific process. **[new section]**
- **Passages:**
  - l.36: "**You hold the delivery seat.**"
  - l.48: "The seat is continuous."
  - l.246: "This is the seat's alone. A thirty-minute tick is a bounded invocation and structurally cannot see the whole; the seat is the only place in the architecture that can hold it".
- **Change:** in the new section, name the actors in one line each:
  - the **console seat**: you, in the window;
  - the **orientation seat**: `delivery-seat.service`, every 3h. It writes `docs/direction/DIRECTION.yaml` and a stretch-log entry, and it may not write code;
  - the **seat-executor** and the **worker tick**, which run bounded build turns;
  - the daemons.

  Then say which of them owns the end-to-end check, and where its record lives. Move the l.241–250 interconnection paragraph into the new "own the end-to-end check" passage so it exists in one place.
- **Reason:**
  - `background/delivery_seat.py` (docstring) is "a bounded `claude -p` session on a three-hour timer … IT MAY NOT WRITE CODE". It is a bounded invocation, which l.246 says cannot see the whole. Yet the interconnection review now happens there. The 2026-10-04 stretch entry reads "THE INTERCONNECTION FAILURE IS THE NEXT ITEM": ba320e2d2 changed the default price under two running probes.
  - Every one of these sessions loads CLAUDE.md, so "you" currently tells a session that is barred from writing code that it should "design, build, review".
  - Continuity is carried by the record (DIRECTION.yaml plus the stretch log), not by a continuous session. CLAUDE.md names neither.
  - The stretch log's 2026-10-04 "What went wrong" lists 23 items, of which 21 are "NOT corrected". So the review finds problems and the record carries them forward. That is worth the new section saying plainly.
- **Class:** no longer holds + unstated assumption + duplicates (with the new section). **Confidence:** high.
- **Candidate explanations:**
  1. `delivery-seat.service` landed 2026-08-25. The 08-28 rewrite described a role, not the processes, and was written for the console session.
  2. It was deliberate: one role spread across several processes. If so, the file should say so.

### 4. "Orient first": the queue and the live state have moved.
- **Passage (l.237):** "**Orient first.** Poll `docs/staging/` — the root is the work queue, ranked. `docs/status/LATEST.md` is live state."
- **Change:** rewrite as:
  > **Orient first.** Read the newest entry in `docs/status/SEAT_STRETCH_LOG.md` and the `focus` in `docs/direction/DIRECTION.yaml`: that is where the last orientation left things. The root of `docs/staging/` is the inbox; `background/staging_rooms.py` ranks it. `docs/status/LATEST.md` is the weekly published state, not live state.
- **Reason:**
  - `origin/main:docs/status/LATEST.md` says "Last updated: 2026-09-28T03:49:00Z". That is by design, because publishing is weekly (`.publish_gate_state.json` `publish_hold`).
  - The staging root holds 87 files. `python3 -m background.staging_rooms --check` is red today: 22 archivals are moved on disk but still sit in the root at HEAD, and the root grew by a net 14 files in 7 days.
  - The ranking the machine actually acts on is the DIRECTION focus, which multiplies the supervisor's draw weights (`delivery_seat.py`: "IT MAY NOT GATE THE DRAW").
- **Class:** no longer holds. **Confidence:** high.
- **Explanation:** both the weekly hold and the orientation seat arrived after the file was written. Nothing is wrong with either; the sentence is just old.

### 5. The rules table says "Each of these is enforced in code". Two rows only report.
- **Passage (l.209):** "Each of these is enforced in code." Rows: "The canon page still matches the code | `tools/canon_drift_check.py` …" and "Staging is a work queue … | `background/staging_rooms.py --check`".
- **Change:** rewrite the header as "Each of these is enforced or reported in code; the two marked *(reports)* refuse nothing." Mark those two rows.
- **Reason:**
  - Neither tool is in `tools/git-hooks/pre-commit` or `commit-msg`.
  - `canon_drift_check` is called from `background/daily_self_note.py:448`. Run this session, it reports **"14 claims checked · 1 drifting — OVER_CLAIM MISSION_the_pricing_arm_is_electricity_only"** (on `THE_MODEL_ON_A_PAGE.md`), and nothing is blocked.
  - `staging_rooms --check` is red (item 4), and commits land anyway.

  A reader who trusts "enforced" will assume a green tree means the canon matches the code. Today it does not.
- **Class:** no longer holds / over-claim. **Confidence:** high.
- **Candidate explanations:**
  1. The rewrite compressed "enforced or reported" into one word. The rewrite notes' "least sure about": "Whether the enforcement table is too terse".
  2. They were gates once and were demoted. I did not check their history, and either way the fix is the same.
  3. "Enforced" was meant as "exists in code". That is too weak a reading for the word.

### 6. The baseline/curriculum wall is worded more strictly than your 2026-09-04 canon reads it. **DIRECTOR DECISION. This is a wall.**
- **Passage (l.193):** "The world changes only for fidelity reasons, decided blind to company results. Which world the company lives through is the director's".
- **Proposed wording (for you to decide):**
  > The world changes only for fidelity reasons, justified by published evidence and never by the change's effect on company results. A *correction* that leaves our position unchanged or worse is made and said afterwards; only a genuine *choice* of curriculum is the director's.
- **Reason:**
  - `DIRECTOR_CANON_RERANKING_THE_ARC_2026-09-04.md` §4 gives this test in your words: *"where a curriculum-adjacent change is a correction rather than a choice, and the honest version leaves our position unchanged or worse, make it and say so afterwards."*
  - Practice follows the canon, not the CLAUDE.md wording. The SLC 14 debt objection (`bf0d37c2f`, sourced from Ofgem 2016 in `bcd886d59`) was *found because* the company lost on one debtor (PROS-2016-0098), and was then fixed from published evidence. DIRECTION.yaml's thesis reading endorses that order: "find where the world cannot press back, fix the world, then re-ask".
  - Read literally, "decided blind to company results" makes that legitimate sequence a breach of the wall.
- **Class:** contradicts (CLAUDE.md vs later canon). **Confidence:** medium-high.
- **Candidate explanations, ranked:**
  1. The wording predates the 09-04 refinement.
  2. Practice is breaching the wall. This is less likely, because each change cites a publisher and makes the company's position harder, not easier.
  3. "Blind" was always meant to cover the justification, not how the problem was discovered. That is the same fix as (1).

### 7. The knowledge-first rule and its story are told twice.
- **Passages:** l.69–85 ("**Knowledge first is a RULE** … £150 CAC …") and l.252–260 ("**Then read the knowledge layer, and read it BEFORE you make a number up.** … `saas/opex_ledger.py` held a sourced £55 …").
- **Change:** keep the rule and your quote in "How to behave". In "Working here" keep only the list of where knowledge lives (knowledge map, market research, regulation commons, Knowledge pages) and "follow the thread". Delete the second telling of the £55/£150 story (~550 characters).
- **Reason:** it is one rule with one anecdote, stated in two sections. The 2026-08-30 commit `c050706d3` added the first without trimming the second. This is the shape the 08-27 decay audit §3 named: "a reader who obeys one has no way to know whether the other adds anything".
- **Class:** duplicates. **Confidence:** high.

### 8. "Knowledge has three sides … say so and ask. Do not build on it." will read as "wait". **[new section]**
- **Passage (l.108):** "When a reading is odd against how the industry actually works, say so and ask. Do not build on it."
- **Change:** rewrite as:
  > …say so on NTFY with your best reading and what you will do meanwhile. Build nothing that depends on the odd frame until it is answered, and carry on with everything else.
- **Reason:** the new model says "escalate … with a proposal and never wait on them". As written, the passage is a bare ask followed by an implied stop. The rest of CLAUDE.md, and `recommendation_guard.py` on NTFY, already refuse a bare ask.
- **Class:** will contradict the new section. **Confidence:** medium.

### 9. Commit mechanics describe the shared-tree commit. Practice is worktree plus `surgical_land`.
- **Passages:**
  - l.263: "**Commits take more than ten minutes** — nine gates … Pre-run the cheap gates first: `background/finding_classes --check`, `background/finding_severity`, `tools/write_time_gate.py --explain …`, `ruff …`, `pytest tests/design/ …`".
  - l.278: "**Commit by pathspec, never `-A`.** Other lanes have work staged in this tree…"
- **Change:**
  - Replace the gate count and the hand-written list with: "the gates and their order are `tools/git-hooks/pre-commit` and `commit-msg` — read them. The two `commit-msg` gates need a REUSE block for a new module and a `NEXT:` trailer that is a bare atom id or `none -- <reason>`."
  - Rewrite the pathspec paragraph to lead with how work actually lands: a scratch worktree with a declared owner, landed by `tools/surgical_land` or `promote_worktree_landing`. Keep pathspec and `isolate_hunks` as the rule for the times you do commit in the shared tree.
- **Reason:**
  - The pre-commit hook has **19** blocking `|| exit 1` gates and `commit-msg` has 2 more, not "nine". Counted in `tools/git-hooks/`, which matches origin.
  - The list leaves out the `NEXT:` gate. Memory records it as a repeated trap (`feedback_the_next_step_gate_trailer_must_be_a_bare_atom_id…`). Memory also records that "CLAUDE.md's list omits" `test_a_control_reads_python_as_code`.
  - `background/finding_classes --check` is not runnable as typed; it needs `python3 -m background.finding_classes --check`. Run that way it is **red on origin today** ("check: FAIL (2 failures)"), so a session that pre-runs it sees a red it did not cause.
  - Last week origin carried 95 "advance the base under a … landing" merges, the signature of `surgical_land`, and CLAUDE.md mentions `surgical_land` only as the fix for a dirty index. Memory has about 40 lessons on worktree ownership, locks and promotion that CLAUDE.md never hints at.
- **Class:** no longer holds + unstated assumption. **Confidence:** high for the count and the list; medium for the paragraph rewrite.

### 10. Your 2026-09-05 rule "machinery work must earn its place" is not in CLAUDE.md. *(An addition, so offered, not pressed.)*
- **Passage (l.87):** "**Build the smallest mechanism that can fail, and prefer doing the work to building the thing that watches the work.**"
- **Change:** append one sentence:
  > Machinery work earns its place only when something a reader or customer depends on is broken, or the machine cannot land work; otherwise file it and move on.

  Cite `DIRECTOR_CANON_PRODUCT_AND_MACHINERY_2026-09-05` §3.
- **Reason:** that canon says the rule "has only ever existed as prose", and it is not in the file every session reads. The 2026-10-04 stretch entry has 21 of 23 "What went wrong" items labelled "THE MACHINE'S". Last week also had 75 liveness heartbeats and 24 direction commits among 774.
- **Class:** unstated / absent. **Confidence:** medium.

### 11. The Build paragraph is mostly history.
- **Passage (l.322–327):** "…It sat at 26,731 for 20 days and 1,440 commits while the real count reached 36,838 … Re-collected 2026-09-27 in a HEAD extract: 38,426."
- **Change:** keep the figure, the parser warning and "correct it at each phase close (phase-close step 5)". Delete the history (~350 characters). Add one clause: "`startup_anchor_freshness` floors it; it cannot catch it lagging."
- **Reason:**
  - The file's own habit says "Write for the next session, not for the record".
  - The floor (`tools/startup_anchor_freshness.py:89`: "floors the figure and does NOT cap it") counts test *functions*, which is far below the collected count. So the stated 38,426 is 976 behind the real 39,402 (item F1) and the gate is green. That is by design, so CLAUDE.md should not imply the floor keeps the figure current.
- **Class:** no longer holds (record, not instruction). **Confidence:** high.

### 12. `tools/wait_for.py` "never hand-roll `pgrep`" assumes every wait fits in 6 hours.
- **Passage (l.221):** "| A waiter names its subject and carries a deadline | `tools/wait_for.py` — never hand-roll `pgrep` |"
- **Change:** append "(it caps at 6h — `MAX_DEADLINE_SECONDS`; a longer wait is a named gap, not a hand loop)". Alternatively, file the cap as the gap the stretch log already carries.
- **Reason:**
  - `wait_for.py:79` sets `MAX_DEADLINE_SECONDS = 6 * 3600`.
  - A three-seed value-arm pass takes about 8h (memory `project_a_value_cycle_level_arm_pass_takes_53_minutes…`).
  - The 2026-10-04 stretch entry: "launch_after_width.sh loops four 6h rounds by hand because wait_for caps at 21600 s. Still not a mechanism."

  The rule is being broken because it cannot be followed, which is worth saying where the rule is.
- **Class:** unstated assumption. **Confidence:** medium.

### 13. The roster sentence. *(Factual. See F3.)* It belongs in the new section's actor list (item 3).

### 14. Director documents that point at CLAUDE.md text which no longer exists. **DIRECTOR DOCUMENTS. Reserved, so proposed only.**
- **`docs/design/DIRECTOR_CANON.md`:**
  - §2 says of R1–R15 "see CLAUDE.md for full text". The R-list was deleted from CLAUDE.md on 2026-08-28.
  - §3 lists seven one-way doors (item 1).
  - §3a makes the twin the "standing approver". `director_twin_log.jsonl`'s last entries are dated 2026-07-16, and under the new model there is no approver at all.
- **`docs/design/DIRECTOR_AXES.md`:**
  - It cites "activity-based, per CLAUDE.md pricing law". The 08-28 rewrite notes list "activity-based pricing" as dropped.
  - Its verdict history has been empty since v1 (2026-07-22).
- **Proposal:** mark `DIRECTOR_CANON.md` historical (twin retired), or retire it. In `DIRECTOR_AXES.md`, re-point or drop the CLAUDE.md citation. CLAUDE.md itself needs no change.
- **Class:** contradicts (canon vs CLAUDE.md). **Confidence:** high on the facts; the disposition is yours.

### 15. Memory duplicates CLAUDE.md, and has itself gone over its limit. *(Not CLAUDE.md. The seat may prune.)*
- `MEMORY.md` is 28KB against a 24.4KB load limit, so its last 21 lines are cut off in every session.
- Three index entries are duplicated ("a census grouped by its SUBJECT'S SHAPE…", "a differential that INJECTS git env…", "a frozen census red can live in the BASELINE file…").
- "Before differencing, SAY WHAT THE THING IS" and "Hook-bypass is a WALL. PATHSPEC, never -A" restate CLAUDE.md word for word.
- **Change:** prune memory, not CLAUDE.md. **Class:** duplicates. **Confidence:** high.

---

## Plain factual errors — the seat may correct these without asking

| # | Passage | Correct to | Evidence |
|---|---|---|---|
| F1 | l.322 "**Build:** 38,426 tests collected" | **39,402 tests collected** (re-collected 2026-10-04 in an `origin/main` extract) | `pytest --collect-only -q` in a `git archive origin/main` extract: "39402 tests collected in 62.29s" |
| F2 | l.263 "nine gates" | "nineteen pre-commit gates and two commit-msg gates" (or drop the number, per item 9) | `grep -c '|| exit 1' tools/git-hooks/pre-commit` = 19; `commit-msg` runs `write_time_gate` and `next_step_gate` |
| F3 | l.314–315 "`process_run_complete`, the executor, the supervisor's ticks … `background/process_manifest.yaml` is the roster" | Name the orientation seat (`delivery-seat.timer`, 3-hourly), `seat-executor`, `worker-tick` and `reconcile-watch`, and say the manifest lists the long-running daemons only | The manifest has 16 entries and omits all of those (installed in `~/.config/systemd/user/`); its `executor-daemon` is `dark` |
| F4 | l.237 "`docs/status/LATEST.md` is live state" | "is the weekly published state" | `origin/main` LATEST.md "Last updated: 2026-09-28T03:49:00Z"; `publish_hold.next_opens 2026-10-05` |
| F5 | l.266 "`background/finding_classes --check`, `background/finding_severity`" | `python3 -m background.finding_classes --check`, `python3 -m background.finding_severity` | As typed these are paths and do not run |
| F6 | l.215 "`site/test_*_door.py`" | `site/**/test_*door*.py` | The root glob matches only `site/test_home_door.py`; `site/capabilities/test_capabilities_door.py` and others are missed |
| F7 | Canon, `THE_MODEL_ON_A_PAGE.md` "Method: … R1–R17, twin approvals …" and the pricing-arm sentence `canon_drift_check` flags | Remove "twin approvals" (none since 2026-07-16); bring the electricity-only claim into line with the code | `canon_drift_check` OVER_CLAIM, this session. *Under the new model the seat may make this correction and say so. The canon's intent is not touched.* |

---

## Checked and holding (so nobody re-checks them)

- **Every backticked path CLAUDE.md names exists on `origin/main`.** Bare `MATURITY_MAP.md` resolves to `docs/design/`, and §8a is present.
- **`background/recommendation_guard.py` does refuse a bare ask.** It raises `RecommendationRequired`, wired at `background/ntfy_utils.py:429`. It covers the NTFY path only, which is what CLAUDE.md claims.
- **`background/claude_md_integrity.py`:** `MAX_CHARS = 35_000` counts characters, there is no line limit, and it reports OK. The file is at 20,172, leaving 14,828 of headroom.
- **`one_way_door.classify_action` is the only list in code.** `action_needed` and `recommendation_guard` both call it rather than keeping their own. The duplication is in prose (item 1).
- **The `.claude/rules/` wall reminders exist** for `company/**`, `saas/**`, `sim/**` and `simulation/**`.
- **All four skill files exist.** `phase-close` and `incident-retro` agree with CLAUDE.md. `staging-protocol` does not (item 2).
- **`tools.maturity_map_store` prints the headroom line** as claimed: 375,326 of 409,600.
- **No-socket wall:** `company_network_isolation --gate` is in pre-commit.
- **Ollama:** no live caller. `background/discovery_agent.py:30` keeps a dead `OLLAMA_URL` in a module nothing imports.
- **"Time does not exist" and "carbon designed and unwired" still hold.** C31 confirms time is absent. E5 is at L1, idle. EP13 is world-side intensity, not a company decision input.
- **The mission block is unchanged and not reviewed for change.** It is your decision.

## Not proposed, deliberately

- **Merging "Before measuring a thing, say what it is" with "Before dividing two numbers…".** They are siblings, not duplicates: one is about definition, the other about ratio.
- **Re-adding R-rules, the gate atlas, or a memory digest to CLAUDE.md.** That would reverse the 08-28 decision. Items 9–12 point at the enforcement instead.
- **Raising the 35,000-character limit.** Not needed. Items 7, 11 and 9 together recover about 1,200 characters, against the new section's additions.
