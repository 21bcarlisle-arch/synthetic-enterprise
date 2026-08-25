**Severity:** RECORDED · **Lane:** H_harness

# Director console — verbatim record, 2026-08-25

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

Source: `c6cee6e9-62fb-45a2-8e17-d45aa524771f.jsonl` · 8 turn(s).

### 2026-08-25T06:49:10.759Z

> /compact

### 2026-08-25T06:51:39.000Z

> This session is being continued from a previous conversation that ran out of context. The summary below covers the earlier portion of the conversation.
>
> Summary:
> 1. **Primary Request and Intent:**
>
>    This session continues an autonomous run under the director's (Rich's) standing mandate from his most recent instruction turn, quoted verbatim from the pre-compaction summary:
>
>    > "Keep going. Don't stop after each piece and don't come back to me unless something is genuinely reserved: curriculum values, a one-way door, money, or a real person. Everything else is reversible and cheap to undo, so act and record it — I'll read what you did and correct you afterwards. That's my job, not gating yours."
>
>    His priority queue ("in rough priority but yours to reorder if your measurements say otherwise"):
>    1. **200 residential earned through the funnel**, now the fold has bought the room
>    2. **The win-rate loop**, so the company can see it is losing and act on it — "five years winning nothing isn't a market, it's a company with no feedback"
>    3. **Explore's remaining stages with real data**
>    4. **Read the 117 harness atoms and delete what shouldn't exist; the map should be half the size and true**
>
>    **Two spending constraints, verbatim:**
>    > "Tokens: my weekly allowance has run out twice, and the tick spawn is the whole of it — keep the cadence honest, don't draw work that cannot change a level, and don't file a finding where a class document already covers it."
>    > "RAM: the headroom I bought is already 94% spent, so treat memory as a budget you're spending rather than a problem that was solved."
>    > "If something blocks you and it isn't on my reserved list, unblock it yourself and tell me why afterwards."
>
>    **Earlier standing constraints still in force:**
>    - **The half-hourly spine is the market**: "GB settlement is half-hourly and that is not an implementation detail, it is the market. So the half-hourly spine stays half-hourly. Aggregate in the reporting and ledger layers if that's where the memory goes, but the settlement and metering record keeps its grain."
>    - **Serial work**: "Do these one at a time, not in parallel. Concurrent work in the shared tree has cost us more than it has bought."
>    - **Four reserved classes only** (never act unilaterally): curriculum values (R13), one-way doors, real money, real people/safety, and an irretractable public claim under Poesys's name.
>    - **Security constraint (from CLAUDE.md, unchanged):** the agent may NEVER alter its own sandbox/security profile, `--dangerously-skip-permissions` scope, credentials, or egress allowlist — director-console-only. `--no-verify` and hand-built `commit-tree`/`merge-tree` merges are a WALL; `tools/surgical_land.py` is the only legal path.
>    - **Company (`company/`, `saas/`) may not open a socket, ever, directly or transitively.**
>
> 2. **Key Technical Concepts:**
>    - **Epistemic wall**: SIM/world (`simulation/`, `sim/`) vs company (`company/`, `saas/`); only sanctioned crossing is `company/interfaces/sim_interface.py` and `company/interfaces/growth_desk.py`.
>    - **R-rules**: R2 (committed ≠ running), R4 (diagnosis discipline — name the nearest working analogue, or build the smallest closed-loop test first), R10 (class fix not instance fix), R11 (verify to the rendered value), R12 (metrics are diagnostics never targets), R13 (baseline vs curriculum split), R14 (every financial figure carries its clock/basis), R15 (controls must be able to FAIL — mutation-tested; three killer patterns: TAUTOLOGY, FAIL-OPEN, FAIL-SILENT), R16 (the ledger is the record).
>    - **`tools/surgical_land.py`**: the only legal commit path; gates the tree the commit *would* create. Signature: `surgical_land.py [-m MSG] [--verify COMMIT] [--attempts N] [--content REPOPATH=SRCFILE] [--content-remove REPOPATH] [paths ...]`. **Positional paths are ALWAYS required**, even with `--content`. There is no `--message-file`. Only `BaseMoved` retries.
>    - **Pre-commit gates** (`tools/git-hooks/pre-commit`): pre_commit_test_gate, level_promotion_gate, site_lane_gate, moap_coherence_gate, ruling_archive_question_gate, consolidation_rhythm, size_ratchet_gate, orphan_ratchet, company_network_isolation, file_scope_generated_paths, annual_report_import_ratchet, GATE 13 half_hourly_dependency_ratchet, GATE 14 running_total_order, **GATE 15 scope_evidence_ratchet (new, mine)**.
>    - **Gate test selection**: `tools.pre_commit_test_gate.select_targets([paths])` — pre-run it to see failures fast (commits take >10 min).
>    - **Level recording (R16)**: `background.gate_authorization.record_level_up_self_certified(atom, level, provenance)` and `record_level_correction_self_certified` for downward moves. `refuse_level_raise_if_lane_blocked(atom)` fires first.
>    - **Finding classes**: `python3 -m background.finding_classes --render|--check`. Five classes: publish_gate_and_wedge, controls_that_cannot_fail, measurements_that_mirror, uncommitted_and_orphaned_work, no_caller_and_never_runs.
>    - **The five-tabs ruling (`03dd8c49e`, 2026-08-20)**: eleven pages deleted; the site is now `/`, `/knowledge/`, `/capabilities/`, `/explore/`, `/harness/` (+ `/privacy/`). Its "WHERE THE CONTENT WENT" table: world+company→Capabilities; proof+evidence→Harness; customers→Explore ("which supersedes it"); now→Home; glossary→Knowledge; director+shadow→Harness/deleted. All 38 redirects deleted. Its own lesson: "a generator that outlives its page is how a deleted surface returns."
>    - **RC7 (director ruling 2026-07-24)**: "no cohort-derived pound aggregate may lead a public surface — a share of revenue and an account count, never a total."
>    - **NTFY env lives at `/home/rich/.config/synthetic-enterprise/.env.ntfy`** (resolved via `background.secrets_location.resolve_secret_file('.env.ntfy')`), NOT `background/.env.ntfy`.
>
> 3. **Files and Code Sections:**
>
>    - **`simulation/net_new_acquisition.py`** — the priority-1 deliverable. Landed as `6474e3cc1`. The docstring was rewritten to carry BOTH measured rows rather than one measured and one extrapolated:
>      ```python
>      #:     at  600:  elapsed 433.8s (7.2 min)   peak RSS 2,011 MB    454.4 customer-years
>      #:     at 1200:  elapsed 746.8s (12.4 min)  peak RSS 3,117 MB    796.1 customer-years
>      #:
>      #: Both rows are MEASURED, not the second extrapolated from the first — and the extrapolation
>      #: would have been wrong in the pessimistic direction: cost per customer-year FELL from 4.43 MB
>      #: to 3.91 as the book grew...
>      SETTLEMENT_CUSTOMER_YEAR_BUDGET = 1200.0
>      ```
>      Result: book 81 → **264 accounts (257 residential, 2 SME, 5 suspended I&C legacy)**. No year is `settlement_engine`-bound; binding is `growth_rate` then `capital`. Win rate stable 0.169–0.184 (was decaying 0.169 → 0.051 with five zero-win years).
>      **Known staleness left behind:** the settlement-bound `notes` string at ~line 641 still says "60% of the 465 measured in AO12's scale probe", which no longer fires but is untrue.
>
>    - **`tools/surgical_land.py`** — landed as `c3163bdd1`. Import changed to `from background.tree_lock import TreeLockTimeout, tree_lock`. New:
>      ```python
>      COMMIT_SWAP_LOCK_TIMEOUT_SECONDS = 900.0
>
>      @contextmanager
>      def _write_lock(root: Path):
>          if root.resolve() != ROOT:
>              yield
>              return
>          held = False
>          try:
>              with tree_lock(timeout=COMMIT_SWAP_LOCK_TIMEOUT_SECONDS):
>                  held = True
>                  yield
>          except TreeLockTimeout as exc:
>              if held:
>                  raise
>              raise LandingRefused(
>                  "the gate PASSED and the commit was NOT made: another writer held the tree lock for "
>                  "the whole {:.0f}s wait ({}). Nothing is wrong with the change. ...".format(
>                      COMMIT_SWAP_LOCK_TIMEOUT_SECONDS, exc)) from exc
>      ```
>
>    - **`tests/tools/test_surgical_land.py`** — 4 tests appended: `test_the_commit_swap_waits_far_longer_for_the_lock_than_the_daemon_default` (asserts `seen["timeout"] >= 600.0`, the independent check), `test_a_lock_that_never_frees_refuses_by_saying_the_CHANGE_IS_FINE`, `test_MUTATION_a_lock_that_frees_lands_normally`, `test_a_timeout_raised_AFTER_the_lock_was_held_is_not_dressed_up_as_contention`. Uses `_lock_stub(raise_timeout, seen)` and `monkeypatch.setattr(sl, "ROOT", repo.resolve())`.
>
>    - **`tools/generate_explore_hh_day.py`** + **`site/explore/index.html`** + tests — landed as `27a9d16b6`. New:
>      ```python
>      _HALF_HOURLY_CAPABLE_METERS = frozenset({"smart", "hh"})
>      def _is_smart(detail: dict) -> bool:
>          return str(detail.get("meter_type") or "").strip().lower() in _HALF_HOURLY_CAPABLE_METERS
>      ```
>      `smart_without` built as a SUBSET inside the same loop via `_no_reads(customer, account_id, detail, why)`; output gains `smart_meter_but_no_hh_reads`, `counts`, `meter_types_seen`, and `_coverage_statement(with_reads, smart_without, households)` which **drops the smart clause entirely when the count is zero**. Live figures: 7 with reads, 3 smart-but-unread (C1, C2, C4), 65 without a capable meter, 75 households.
>
>    - **`tests/tools/test_e2_revenue_reconciliation_surfaces.py`** — landed as `9a07fd5c5`. Was RED for four days. Replaced the literal five-page tuple with:
>      ```python
>      EXPECTED_NET_MARGIN_DOORS: tuple[str, ...] = ()
>      EXPECTED_EMPTY_REASON = (
>          "RC7 (director ruling, 2026-07-24): no cohort-derived pound aggregate may lead a public "
>          "surface -- 'a share of revenue and an account count, never a total'. ...")
>      def _door_to_page(door: str) -> str:
>          return (door.strip("/") + "/index.html").lstrip("/")
>      EXPECTED_NET_MARGIN_SURFACES = tuple(_door_to_page(d) for d in EXPECTED_NET_MARGIN_DOORS)
>      ```
>      New tests: `test_discovery_and_the_registry_agree_about_which_doors_report_margin`, `test_the_registry_can_only_name_doors_the_IA_REGISTER_STILL_ADVERTISES` (imports `ia_register`, checks against `CANONICAL_NAV_AREAS`), `test_an_EMPTY_registry_must_say_why_rather_than_pass_quietly`. `test_control_fires_on_stripped_disclosure` now BUILDS its subject and carries its null half.
>
>    - **`tools/scope_evidence_ratchet.py`** (NEW, GATE 15) + **`tests/tools/test_scope_evidence_ratchet.py`** (14 tests) — landed as `9fe17a9d6`. Core:
>      ```python
>      DELETED = "deleted"
>      UNCOMMITTED = "uncommitted"
>
>      def parse_atoms(text: str) -> list[dict]:   # uses yaml.safe_load
>      def _tracked_paths(root: Path) -> frozenset[str] | None:   # git ls-files, None if unaskable
>      def _in_git(rel: str, tracked: frozenset[str]) -> bool:    # directory scopes via prefix match
>
>      def violations(text, root=ROOT, tracked=None) -> list[tuple[str, int, str, str]]:
>          if tracked is None: tracked = _tracked_paths(root)
>          out = []
>          for a in parse_atoms(text):
>              level = a["level_current"]
>              if not isinstance(level, int) or level <= 0: continue
>              for rel in a["file_scope"]:
>                  on_disk = (root / rel).exists()
>                  if not on_disk: out.append((a["id"], level, rel, DELETED))
>                  elif tracked is not None and not _in_git(rel, tracked):
>                      out.append((a["id"], level, rel, UNCOMMITTED))
>          return out
>      ```
>      Rule keys on `level_current > 0` (17 level-0 proposals naming files they'd create stay silent). No frozen baseline. Fails closed on unreadable/unparseable map.
>
>    - **`docs/design/maturity_map.yaml`** — 13 atoms re-pointed (landed `9fe17a9d6`), two levels moved (landed `07c7b49ff`). Notable re-points: E2 → `["tests/tools/test_e2_revenue_reconciliation_surfaces.py", "site/ia_register.py", "site/index.html"]`; SITE_EH1/EH3 `site/company/`+`site/world/` → `site/capabilities/`; SITE_EH2/D44/G13 `site/proof/` → `site/harness/`; D36/D_printed_figure_rederivation `site/customers/index.html` → `site/explore/index.html`; KNIFE1 `simulation/run_segments.py` → `tools/run_segments.py`; both OPS1 atoms dropped `background/session_watchdog.py` (their own work deleted it, commit `c468b5ad2`); SITE2 → Explore; SITE_director_window_delta_view → `[tools/generate_director_data.py, site/harness/index.html]`; SITE10 → `['site/explore/', 'tools/generate_explore_hh_day.py', 'tests/tools/test_generate_explore_hh_day.py']`.
>
>    - **`tests/tools/test_bill_correctness_addendum_defect4.py`** — landed as `a8df2e995`:
>      ```python
>      def billed_total_by_customer_year(ledger: dict, *, net_of_catchup: bool = False) -> dict:
>          ...
>          amount = inv["total_amount_gbp"]
>          if net_of_catchup and inv.get("catchup_applied"):
>              amount -= inv.get("catchup_adjustment_gbp") or 0.0
>      ```
>      Four new tests: null control (netting leaves a catch-up-free year identical), the repair on PROS-2018-0002 2019's real numbers (−169.09 → +3.77), a fail-open guard, and `test_EVERY_negative_invoice_in_the_live_ledger_is_catchup_explained` (90 of 90).
>
>    - **`docs/staging/WORKER_FINDING_THE_PRICE_CAP_IS_ENFORCED_AGAINST_A_RATE_ON_THE_WRONG_SIDE_OF_VAT_2026-08-24.md`** (NEW) — landed as `467943976`. Severity BLOCKING, lane W1_market_weather.
>
>    - **`simulation/hedged_settlement.py:319`** (read, NOT modified) — the defect:
>      ```python
>      _cap = binding_cap_unit_rate_gbp_per_mwh(commodity, current_date)
>      if _cap is not None:
>          billed_rate_gbp_per_mwh = min(uncapped_rate_gbp_per_mwh, _cap)
>      ```
>      Rate is EX-VAT; cap is INC-VAT at 5%. Same error at `company/pricing/renewal_rate_chain.py:265-276`.
>
>    - **`docs/observability/gate_authorizations.jsonl`** — two `LEVEL_UP_SELF_CERTIFIED` rows for SITE7 and SITE10, both `authorized_by=agent_self_certified`, `channel=self`, with full evidence and stated deviations.
>
> 4. **Errors and fixes:**
>
>    - **`--message-file` unrecognized** → `surgical_land` only takes `-m/--message`. Used `-m "$(cat file)"`.
>    - **"REFUSED: no paths given"** → `--content` does not substitute for positional paths; `land()` takes `args.paths` separately. Passed the path positionally.
>    - **`TreeLockTimeout` after a green 13-min gate, twice** → `--attempts` doesn't help because only `BaseMoved` retries. Fixed at source in `surgical_land` (900s wait + friendly refusal). This was an "unblock it yourself and tell me why afterwards" case.
>    - **My hand-rolled yaml parser was wrong** — cross-checked against `yaml.safe_load` on the real map, disagreed on 4 records: `level_current: 1   # comment` defeated the scalar regex, and an inline list wrapped across lines yielded an **EMPTY** `file_scope`, meaning three atoms would have been silently exempt on day one (R15 fail-silent built into the control). The premise was also wrong: `level_promotion_gate` and `orphan_ratchet` both already import yaml in the same hook. Switched to yaml and added `test_the_parser_agrees_with_yaml_on_every_atom`.
>    - **GATE 15 refused my own commit** on `docs/design/PB2_INVERSION_BUILD.md` — on disk, never committed, backing an L3 claim. Added the `UNCOMMITTED` kind with its own message, and landed the doc (another lane's finished build record, its sibling `PB2_JOIN_KEY_BUILD.md` already committed; landing a design doc sweeps nobody's in-flight code).
>    - **`file_scope_generated_paths` refused my re-point** of `site/data/director_delta.json` with a better reason than I had: "a path a generator rewrites. The unmerged-work guard will deprioritise this atom on every tick it is dirty, so it will never be drawn and nothing will say so. Scope the GENERATOR, not the generated." Dropped the generated path.
>    - **GATE 15 caught my own SITE10 level move** — `site/customers/` was correct scope at L0 (the atom's own gain text calls it "the substrate") and became a false claim at L2. Re-pointed to Explore.
>    - **Explore tests failed on `LandingRefused: already at HEAD`** — the `repo` fixture ships `code.py = VALUE = 1`; gave each test a distinct value.
>    - **NTFY `RuntimeError: SE_NTFY_TOPIC is not set`** — `background/.env.ntfy` does not exist; the file resolves to `/home/rich/.config/synthetic-enterprise/.env.ntfy`.
>    - **Four customer-years billed NEGATIVE** — initially looked like the pipeline break the gate names. Diagnosed as correct catch-up credits; **the oracle was wrong, not the ledger**. Measured 90/90 negative invoices catchup-explained before changing anything.
>
> 5. **Problem Solving:**
>    - Priority 1 delivered and landed: 257 residential earned through the funnel, engine no longer binding in any year, win rate stable.
>    - Diagnosed the map's real defect as truth, not clutter: 13 claimed levels resting on deleted evidence, 11 from one commit. Fixed all 13 and armed a class control with no baseline.
>    - Found and repaired a control red for four days that nothing selected (E2). Named the underlying issue without claiming to fix it: path-based test selection means a control outside every recent commit's selection "is not a control; it is a file."
>    - Read the SITE atoms rather than pattern-matching the sitemap: closed 2, deliberately left 5 open with per-atom reasons (SITE6's protected glossary LAYER was itself deleted; SITE8 has a director editorial call the atom flags as "not the worker's to silently pick"; SITE1 is held by an Expert Hour FAIL whose every blocker names a deleted page; SITE2/SITE3/SITE11 are superseded and named as delete-candidates for a separate pass).
>    - Found and filed the VAT-basis price-cap defect with both bases established empirically.
>    - **R2 not yet satisfied on the headline claim:** the budget raise is committed but no run has picked it up (last run 22:40, `run_output_latest.json` has 80 accounts, `site/data/customers.json` has 75). `sim_runner.run_simulation()` uses `subprocess.run(...)`, so a fresh process picks up the constant with no daemon restart. Run timeout is 7200s (vs 12.4 min); declared publisher budget 4700s. Both comfortable.
>
> 6. **All user messages:**
>    - Only one user-role message in this session: the continuation prompt instructing me to resume from the compacted summary without acknowledging it, preface, or recap — "Resume directly." (The six prior director instruction turns are recorded in the pre-compaction summary reproduced in section 1 above; they were not re-sent by the user this session.)
>
> 7. **Pending Tasks:**
>    - **Priority 2, the win-rate loop / price lever** — the company still has no price lever: `simulation/acquisition_funnel.QUOTE_TO_APPLICATION = {"resi": 0.24, "SME": 0.28}` is a per-segment constant, and `PRICE_DIFFERENTIAL_PCT = 0.0` is hard-coded in `simulation/customer_events.py:38`, `simulation/run_phase4c_on_phase2b.py:106`, `tools/run_phase4b_on_phase2b.py:33`. Design researched: pass the offered rate in through `company/interfaces/growth_desk.py` (mirroring the `total_amount_gbp` precedent), derive the differential world-side against the published cap, and reuse `simulation/market_switching_propensity._savings_to_rate`'s DESNZ-calibrated curve rather than inventing an elasticity. Home atoms exist: `B10_competitor_switching_response` (L0→3, idle, `sim/competitor_field.py`), `B4_competitor_field`, `W2_3_competitor_field`.
>    - **The VAT-basis fix**, per the finding's own four owed items: an R14 measurement (one interpreter, one tree, one minute, variable swapped); a count of how often the clamp binds (sum over `cap_bound`); fix the WORLD only and leave the company's reading wrong so the gap becomes visible; a class control.
>    - **Delete the superseded SITE atoms** (SITE2, SITE3, SITE11) — named but deliberately not deleted, since "removing an atom is a bigger act than moving a level and it deserves its own pass."
>    - **SITE1_expert_doors** needs its Expert Hour re-taken against the site that exists.
>    - **Verify the budget raise on a real run (R2/R11)** — confirm 264 accounts reach the published figures.
>    - Stale string in `simulation/net_new_acquisition.py` settlement-bound `notes` ("60% of the 465 measured in AO12's scale probe") — no longer true after the raise.
>
> 8. **Current Work:**
>
>    The last substantive act was landing the VAT-basis finding as `467943976` and pushing it, completing an eight-commit session:
>
>    | sha | subject |
>    |---|---|
>    | `6474e3cc1` | sim: raise settlement customer-year budget 600 -> 1200 so the funnel, not the engine, decides the book |
>    | `c3163bdd1` | tools: a fifteen-minute green gate must not be discarded because a publisher held the tree lock for sixty seconds |
>    | `27a9d16b6` | explore: three households were told they have no smart meter, and they do |
>    | `9a07fd5c5` | E2's control has been red for four days: its five expected surfaces were the five pages the director deleted... |
>    | `9fe17a9d6` | map: thirteen atoms claimed a level on evidence that had been deleted, and now a gate refuses the fourteenth |
>    | `a8df2e995` | billing: four customer-years billed NEGATIVE and the gate was right to shout -- it was the oracle that was wrong, not the ledger |
>    | `07c7b49ff` | map: Capabilities and Explore have been live for days and the map still had them at zero -- two atoms closed, and seven read and deliberately NOT closed |
>    | `467943976` | finding: the domestic price cap is enforced against a rate on the wrong side of VAT, so the ceiling sits 5% above the law |
>
>    All pushed to `origin/main`. An NTFY (id `GyIuZVKQh1sa`) went to the director summarising the session and raising the one reserved-class item — SITE9's `block_reason` says "no commit may remove /director/ from INTERNAL_DOORS... until the director has read the page's RENDERED content", yet `INTERNAL_DOORS` is now `()` and `site/director/` is deleted — with the recommendation to read it as overturned by the later categorical five-tabs ruling and rebuild the delta as a section on `/harness/` rather than restoring a hidden door. Related fact flagged: `tools/generate_director_data.py` still writes `site/data/director_delta.json` every cycle and no page renders it.
>
>    Working tree state: only `CLAUDE.md` shows modified (another lane's uncommitted work, deliberately untouched). All gates green; `scope_evidence_ratchet` rc=0; `finding_classes --check` PASS.
>
> 9. **Optional Next Step:**
>
>    Verify the budget raise on a real run (R2/R11), which is the outstanding obligation on the session's headline claim. The director's priority-1 words were *"200 residential earned through the funnel, now the fold has bought the room"*, and the commit message states plainly that *"PUBLISHED FIGURES MOVE, MATERIALLY AND ON PURPOSE (R14). The book triples..."* — but as of 23:37 no run had picked it up: `run_output_latest.json` still holds 80 accounts and `site/data/customers.json` 75, both from the 22:40 run at budget 600. `sim_runner` invokes the sim via `subprocess.run(...)`, so the new constant takes effect on the next cycle without a daemon restart; the run timeout is 7200s against a measured 12.4 min, and the declared publisher budget is 4700s. The step is to confirm the next run publishes 264 accounts and that the `engine_bound_statement` flips from naming six years to naming none, then move to priority 2 (the price lever) per the researched design.
>
> If you need specific details from before compaction (like exact code snippets, error messages, or content you generated), read the full transcript at: /home/rich/.claude/projects/-/c6cee6e9-62fb-45a2-8e17-d45aa524771f.jsonl
> Continue the conversation from where it left off without asking the user any further questions. Resume directly — do not acknowledge the summary, do not recap what was happening, do not preface with "I'll continue" or similar. Pick up the last task as if the break never happened.

### 2026-08-25T06:51:39.486Z

> Yes — clear. That session is at 384k after a twelve-hour night, and everything it needs is short enough to restate.
>
> ```
> Fresh session. You are the autonomous builder on Poesys. It's
> Tuesday morning, 25 August.
>
> Where things stand. Overnight you earned 257 residential customers
> through the funnel — book 81 to 264, settlement budget raised to
> 1200 customer-years on measured cost, no year engine-bound, win
> rate steady at 0.169-0.184 instead of decaying to zero. You
> repaired 13 atoms claiming levels on evidence deleted by the
> five-tabs commit and armed GATE 15 so it can't refill. The site is
> five tabs, publishing on its own, currently fresh. Staging is
> around 15. The half-hourly spine is protected by GATE 13 and the
> daily fold is wired and dormant behind it.
>
> I've ruled: SITE9's director-record block is overturned. Rebuild
> the delta as a section on /harness/.
>
> Three things this morning. Your tick loop has been resting beside
> drawable work since 00:35Z — the same two alerts every hour for
> six hours, three self-drawable mints undrawn; your own alert names
> the two possibilities, so find out which and fix it. There were 30
> newly failing tests at HEAD at 02:21Z and a publish gate wedge at
> 02:26Z. And you filed but didn't fix the VAT ceiling — the world
> clamps an ex-VAT rate against an inc-VAT cap, so a published
> ceiling sits 5% above the law. Take the measurement and land it.
>
> Then the week's real target. 257 residential on half-hourly data
> means the carbon score is finally measurable, and the site still
> says NOT YET MEASURED. That number is the entire point of this
> project. Wire the carbon ledger to live meter reads and grid
> intensity, publish it with its provenance, and say plainly what it
> does and does not yet include. Explore's remaining stages and the
> 117 harness atoms come after.
>
> How we work. You do the work, we review. Never wait on me for
> anything reversible — act, record the reason, tell me afterwards.
> On figures you have three lawful outcomes: correct, caveat, or
> withdraw; freezing is not one of them. Measuring is never
> publishing. Reserved to me: curriculum values, one-way doors,
> money, real people. Don't report between pieces — keep going.
>
> Two budgets to respect. My weekly token allowance has run out
> twice and the tick spawn is most of it, so don't draw work that
> cannot change a level and don't file a finding where a class
> document already covers it. And memory: the headroom the WSL raise
> bought is largely spent, so treat RAM as a budget you're spending
> rather than a problem solved.
> ```

### 2026-08-25T14:42:28.987Z

> Read this as the thesis, and check your work against it from here.
>
> The point of the project is a faithful SIM, and inside it a
> supplier that makes commercial and operational decisions
> customer-by-customer on lifetime value — using only what it can
> actually know. It should behave like an average player by default,
> and beat average precisely to the degree it understands and
> predicts the truth behind the SIM better than average. That holds
> for acquisition, retention, tariff, debt, service, everything.
>
> Two consequences I want you to hold as constraints.
>
> The advantage must come from inference, never from access. If the
> company ever performs better because it was handed something
> rather than because it predicted it, the result is worthless and
> the wall has failed. Every performance claim needs to survive the
> question: could a real supplier have known this, and did it work
> it out?
>
> And there has to be a baseline to beat. Average behaviour is the
> control — the same book run by a supplier applying flat rules with
> no per-customer view. Without that comparison, "it performed well"
> means nothing.
>
> Measured against that, what exists today is rules, not decisions:
> a dunning ladder, a churn estimate, a price. Nothing yet chooses
> per customer on what that customer is worth. Say plainly where the
> gap is largest, then close it — starting where inference could
> most change an outcome.
>
> Everything I said before stands: meter mix, then carbon, then the
> fidelity gap. This is the frame they sit inside, not a
> replacement.

### 2026-08-25T15:37:33.962Z

> ```
> do the meter mix
>
> Then change how you're treating price and risk, and don't take my
> word for the rules — read them.
>
> Real suppliers already differentiate on payment risk. Direct debit
> discounts exist and are permitted; the cap itself sets separate
> levels for direct debit, standard credit and prepayment because
> the costs genuinely differ. Withholding a low-margin fixed tariff
> from a credit risk is ordinary practice. For non-domestic there is
> statutory late payment interest and charges, and a different rules
> regime again.
>
> So the shape isn't "never price up a vulnerable household". It's
> that pricing follows expected cost — and default risk, collections
> cost and bad debt are part of that cost. Put them inside the EV
> arithmetic and let the answer emerge rather than imposing a floor.
>
> Establish what's actually allowed rather than assuming, and use
> the sources: the regulation commons in the repo, the licence
> obligations register, and your read access to Ofgem and
> legislation. SLC 0 and SLC 27, the ability-to-pay and
> self-disconnection duties, the microbusiness and deemed-contract
> rules, and the commercial debt interest legislation. Record what
> is explicitly permitted, what is prohibited, and what is
> tolerated-but-unwritten, with citations. That register is what the
> pricing arm should be constrained by — not my recollection and not
> yours.
>
> Keep the floor as a backstop only until that's done.
>
> Then keep going. No stopping, ever. Not between pieces, not to
> report, not to check, not to ask. When something finishes, start
> the next thing. When you run out of the work I've named, go to the
> thesis: a faithful world, and a supplier that decides
> customer-by-customer on what it can infer, beating a flat-rules
> baseline only through better prediction. There is always work in
> that direction and you don't need my permission to find it. I'll
> read what you did and correct you afterwards — that is my job, and
> it does not require you to wait.
> ```

### 2026-08-25T16:41:30.517Z

> /compact

### 2026-08-25T16:44:01.167Z

> This session is being continued from a previous conversation that ran out of context. The summary below covers the earlier portion of the conversation.
>
> Summary:
> 1. **Primary Request and Intent:**
>
>    Three genuine director (user) turns in this conversation, each building on the last.
>
>    **Turn 1 — the morning brief** (delivered as a quoted fresh-session brief): Overnight, 257 residential customers were earned through the funnel; the site is five tabs and publishing; staging ~15. A ruling was issued: *"SITE9's director-record block is overturned. Rebuild the delta as a section on /harness/."* Three morning items: (a) the tick loop "has been resting beside drawable work since 00:35Z — the same two alerts every hour for six hours, three self-drawable mints undrawn; your own alert names the two possibilities, so find out which and fix it"; (b) "There were 30 newly failing tests at HEAD at 02:21Z and a publish gate wedge at 02:26Z"; (c) "you filed but didn't fix the VAT ceiling … Take the measurement and land it." Then the week's target: *"257 residential on half-hourly data means the carbon score is finally measurable, and the site still says NOT YET MEASURED. That number is the entire point of this project. Wire the carbon ledger to live meter reads and grid intensity, publish it with its provenance, and say plainly what it does and does not yet include."* Working rules stated verbatim: *"Never wait on me for anything reversible — act, record the reason, tell me afterwards. On figures you have three lawful outcomes: correct, caveat, or withdraw; freezing is not one of them. Measuring is never publishing. Reserved to me: curriculum values, one-way doors, money, real people. Don't report between pieces — keep going."* Two budgets: *"My weekly token allowance has run out twice and the tick spawn is most of it, so don't draw work that cannot change a level and don't file a finding where a class document already covers it. And memory: the headroom the WSL raise bought is largely spent, so treat RAM as a budget you're spending rather than a problem solved."*
>
>    **Turn 2 — the thesis**: *"The point of the project is a faithful SIM, and inside it a supplier that makes commercial and operational decisions customer-by-customer on lifetime value — using only what it can actually know. It should behave like an average player by default, and beat average precisely to the degree it understands and predicts the truth behind the SIM better than average. That holds for acquisition, retention, tariff, debt, service, everything."* Two constraints held as absolute: *"The advantage must come from inference, never from access. If the company ever performs better because it was handed something rather than because it predicted it, the result is worthless and the wall has failed. Every performance claim needs to survive the question: could a real supplier have known this, and did it work it out?"* and *"there has to be a baseline to beat. Average behaviour is the control — the same book run by a supplier applying flat rules with no per-customer view. Without that comparison, 'it performed well' means nothing."* Instruction: *"Measured against that, what exists today is rules, not decisions: a dunning ladder, a churn estimate, a price. Nothing yet chooses per customer on what that customer is worth. Say plainly where the gap is largest, then close it — starting where inference could most change an outcome."* Plus: *"Everything I said before stands: meter mix, then carbon, then the fidelity gap. This is the frame they sit inside, not a replacement."*
>
>    **Turn 3 — the rules and the non-stop mandate**: *"do the meter mix. Then change how you're treating price and risk, and don't take my word for the rules — read them."* Substance: real suppliers differentiate on payment risk; DD discounts are permitted; the cap sets separate levels for DD/standard credit/prepayment; withholding a low-margin fixed tariff from a credit risk is ordinary practice; non-domestic has statutory late-payment interest. *"So the shape isn't 'never price up a vulnerable household'. It's that pricing follows expected cost — and default risk, collections cost and bad debt are part of that cost. Put them inside the EV arithmetic and let the answer emerge rather than imposing a floor."* Sources named: *"the regulation commons in the repo, the licence obligations register, and your read access to Ofgem and legislation. SLC 0 and SLC 27, the ability-to-pay and self-disconnection duties, the microbusiness and deemed-contract rules, and the commercial debt interest legislation. Record what is explicitly permitted, what is prohibited, and what is tolerated-but-unwritten, with citations. That register is what the pricing arm should be constrained by — not my recollection and not yours. Keep the floor as a backstop only until that's done."* Final standing instruction: *"Then keep going. No stopping, ever. Not between pieces, not to report, not to check, not to ask. When something finishes, start the next thing. When you run out of the work I've named, go to the thesis: a faithful world, and a supplier that decides customer-by-customer on what it can infer, beating a flat-rules baseline only through better prediction. There is always work in that direction and you don't need my permission to find it. I'll read what you did and correct you afterwards — that is my job, and it does not require you to wait."*
>
> 2. **Key Technical Concepts:**
>    - **Epistemic wall**: `simulation/`+`sim/` (world) vs `company/`+`saas/`; sole sanctioned crossing `company/interfaces/sim_interface.py`; `tools/` sits outside the wall and is the ONLY layer permitted to hold belief and truth side by side (COUPLED_TRIAD_DESIGN 1.3).
>    - **R-rules**: R2 (committed ≠ running), R4 (diagnosis discipline), R9 (observed-with-evidence vs inferred), R10 (class fix not instance fix), R11 (verify to the rendered value), R12 (metrics are diagnostics never targets), R13 (baseline vs curriculum split — baseline changes only for fidelity-to-reality reasons, decided blind to company P&L), R14 (every financial figure carries its clock/basis), R15 (controls must be able to FAIL; three killer patterns: TAUTOLOGY, FAIL-OPEN, FAIL-SILENT), R16 (the ledger is the record), C-S2 (RNG substream discipline).
>    - **`tools/surgical_land.py`**: the only legal commit path; gates the tree the commit *would* create. Positional paths always required. Long-running (10–70 min). Must be launched `setsid nohup … &` with NO `timeout` wrapper — three attempts were killed by their launchers.
>    - **Pre-commit gates**: pre_commit_test_gate, level_promotion_gate (OPS11 lane-blocking), site_lane_gate (runs `site/**` tests against the WORKING TREE), orphan_ratchet, segment_case_guard, grid_intensity_guard, scope_evidence_ratchet (GATE 15), record_landing_claim_check, simplifications-count invariant.
>    - **Regulation commons doctrine**: regulatory TEXT is a shared commons readable by every lane; each lane's READING is independently owned.
>    - **Security/operational constraints still in force** (from CLAUDE.md): the agent may NEVER alter its own sandbox/security profile, `--dangerously-skip-permissions` scope, credentials, or egress allowlist — director-console-only. `--no-verify` and hand-built `commit-tree`/`merge-tree` merges are a WALL. `company/`+`saas/` may not open a socket, ever, directly or transitively. HARNESS may fetch published sources; the bytes may become documentation/design records/Knowledge and NEVER a runtime input the company reads (except via the sanctioned commons).
>    - NTFY env at `/home/rich/.config/synthetic-enterprise/.env.ntfy`.
>
> 3. **Files and Code Sections:**
>
>    - **`background/seat_continuity.py`** (landed `7f58ef606`) — `_uncommitted_paths()` rewritten to delegate to `tree_divergence.changed_paths` minus `docs/staging/`; subject changed from session-id to held-work areas via new `_held_areas()`/`SUBJECT_AREAS = 4`.
>    - **`background/alarm_repetition.py`** — added UUID pattern FIRST in `_VARIABLE`: `re.compile(r"\b[0-9a-f]{4,}(?:-[0-9a-f]{2,}){2,}-?")`. Root cause: `{7,40}` hex rule ate 8/12-char groups, 4-char groups too short, number rule ate digits, letters survived as a per-session fingerprint.
>    - **`simulation/price_cap_enforcement.py`** (landed `b3e41f95b`) — `binding_cap_unit_rate_gbp_per_mwh` split into `..._inc_vat` / `..._ex_vat`; `DOMESTIC_VAT_RATE = 0.05`.
>    - **`sim/grid_carbon_intensity.py`** (NEW, `8f15b78c1`) — dimensionless half-hourly shape, demand-weighted mean 1.0; `MUST_RUN_EMISSIONS_RATE_T_PER_MWH = MUST_RUN_BIOMASS_SHARE * BIOMASS_G_CO2_PER_KWH / 1000.0`; must-run taken against DEMAND not residual.
>    - **`company/carbon/half_hourly_footprint.py`** (NEW) — MEASURED/PROFILED/UNCOVERED; profiled accounts get `co2e_kg_timed=None` and `timing_effect_pct` RAISES.
>    - **`tools/generate_grid_intensity_feed.py`**, **`tools/generate_explore_carbon.py`** — wired into `background/process_run_complete.py` in ORDER (hh_day → feed → carbon).
>    - **`simulation/premise_population.py`** (landed `f8dc54ef8`) — `smart_meter_penetration(year)` lifted out of `smart_read_share`, which now returns `smart_meter_penetration(year) * _SMART_COMMUNICATING_RATE`. Constants `_SMART_SHARE_2016 = 0.106`, `_SMART_SHARE_2024 = 0.689`, `_SMART_COMMUNICATING_RATE = 0.90` (DESNZ Q4 2024 Table 5a).
>    - **`simulation/population_draw.py`** — `SyntheticCustomer` gains `smart_meter: bool = False` (placed AFTER `premise: Optional["DrawnPremise"] = None`); rendered in `to_customer_dict()` (unlike `cohort`/`premise`). New:
>      ```python
>      _MANDATED_HH_SEGMENTS = (INDUSTRIAL_AND_COMMERCIAL,)
>      def _draw_smart_meter(customer_id, base_seed, year, segment) -> bool:
>          if normalise_segment(segment, default=None) in _MANDATED_HH_SEGMENTS:
>              return True
>          from simulation.premise_population import smart_meter_penetration
>          roll = _cohort_substream(customer_id, base_seed, "smart_meter").random()
>          return roll < smart_meter_penetration(int(year))
>      ```
>      Import added: `from simulation.segment_vocabulary import INDUSTRIAL_AND_COMMERCIAL, normalise_segment`.
>    - **`docs/domain_artefact_library/regulatory/pricing_differentiation_permissions.md`** (NEW, `5064540c7`) — the permissions register. Sections A (permitted: SLC 27.2A cost-reflective payment-method differences; 1998 Act statutory interest/recovery sums; SLC 27.3/27.4 security deposits), B (prohibited: over-large payment-method differences; restricting payment-method availability SLC 27.1; charging for 27.6 services per 27.5A; unduly onerous deemed terms SLC 7.3/7.4; SLC 7.6 no termination fee on deemed; SLC 7A.3 microbusiness), C (required: SLC 27.8 ability-to-pay on INSTALMENTS; 27.8A(a)(ii) incentives to outcomes not repayment value; 27.5B proactive-contact triggers; SLC 0.3 Standards of Conduct; SLC 27A self-disconnection), D (tolerated-but-unwritten, 5 rows), E (fidelity gap: the tree's cap artefact has one level per fuel, the real cap has DD/standard-credit/prepayment levels), F (how the pricing arm must use it).
>    - **`company/regulatory/pricing_permissions.py`** (NEW) — `UNDULY_ONEROUS_CLASS_MARGIN_MULTIPLE = 2.0` (named "NOT THE LAW"), `STATUTORY_INTEREST_OVER_BASE = 0.08`, `STATUTORY_RECOVERY_SUMS_GBP = ((1_000.0, 40.0), (10_000.0, 70.0), (inf, 100.0))`, `COMMERCIAL_DEBT_SEGMENTS = ("SME", "I&C")`, `check_payment_method_difference` (two-sided, on magnitude), `check_class_margin` (deemed-only, unknown comparator = FAILED check), `INSTALMENTS_ARE_NOT_PRICED_HERE`.
>    - **`company/pricing/value_based_renewal.py`** (`133d9992c`, reworked `5064540c7`) — `FLAT_RULES`/`VALUE_BASED` arms; `CANDIDATE_MARGINS_GBP_PER_MWH` widened to 0.50…200.00; `max_supported_rate_increase_pct()` derived from `company.pricing.ofgem_price_cap._CAP_WINDOWS` (largest published single-step rise = +83.1%); `ExpectedAnnualCosts` (cost_to_serve, bad_debt, collections, carrying, fixed_revenue, unsourced); `expected_annual_costs(...)` with bad debt on the WHOLE bill via `saas.payment_behaviour.bad_debt_provision_gbp`; `expected_value_gbp(...)` now `p_retain * (margin*eac + fixed_revenue - costs) * annuity`; the vulnerability floor REMOVED and replaced by `check_class_margin`; `MarginDecision` gains `costs`, `withheld_reason`, `endpoint_bound`, `ceiling_bound`, `extrapolation_bound`.
>    - **`simulation/customer_events.py`** (`baec3efb2`, `fbe8b0ab6`) — new `_price_differential_vs_market(new_rate, term_start)` returning a fraction vs the published SVT or `None`; churn chain now:
>      ```python
>      differential = _price_differential_vs_market(new_rate_gbp_per_mwh, term_start_str)
>      if differential is None:
>          differential = price_differential_pct
>      if differential:
>          p_churn_price = (1.0 - effective_p_retain) * churn_position_multiplier(differential)
>          effective_p_retain = 1.0 - min(p_churn_price, WORLD_MAX_CHURN_PROBABILITY)
>      ```
>      Event now records `price_differential_vs_svt`, `offer_position_multiplier`, `churn_position_multiplier`.
>    - **`simulation/market_switching_propensity.py`** (`fbe8b0ab6`) — new `churn_position_multiplier(d)`: reciprocal of the win leg below the calibrated ceiling; above it continues at `_LAST_INFORMED_SLOPE_PER_GBP = (_MAX_RATE - 0.13) / (400.0 - 250.0)`. Win leg's saturation untouched.
>    - **`tools/couple_value_based_pricing.py`** (`133d9992c`, extended `5064540c7`, `61a6620cc`) — two-arm comparison over the live book; wires credit risk/payment delay/standing charge; `belief_versus_truth(...)` and `_belief_summary(...)`; `_verdict(...)` reports `fit_to_run`.
>    - **Test files created**: `tests/sim/test_grid_carbon_intensity.py` (15), `tests/company/carbon/test_half_hourly_footprint.py` (14), `tests/tools/test_grid_intensity_feed_and_explore_carbon.py` (16), `tests/company/pricing/test_value_based_renewal.py` (21), `tests/company/regulatory/test_pricing_permissions.py` (16), `tests/simulation/test_drawn_smart_meter.py` (12), `tests/simulation/test_price_position_churn.py` (22), `tests/tools/test_couple_value_based_pricing.py` (10).
>
> 4. **Errors and fixes:**
>    - **My "0.05 vs NESO's 0.16" was a recollection written as a measurement** — a tick fetched the real series and measured 32x vs 11.4x. **Director-relevant**: this was my error, caught by the machine, and it had been cited as evidence in a level certification. Fixed by publishing the measured comparison on the page (`145b90074`).
>    - **First carbon spread grid clipped every decision at its ceiling (0.50–8.00)** — widened; added `endpoint_bound`.
>    - **A test of mine passed on its own mis-read** — read `versus_published` off an account row while the generator wrote it under `grid`; took the "unavailable" branch and passed while the page rendered nothing. Fixed by asserting the key exists before the absent branch is reachable.
>    - **Publish outages I caused**: (a) a `site/**` edit without its test update (07:15–08:05Z); (b) a level raise left in the shared INDEX while held out of its commit — the publisher commits by pathspec, the level gate reads the tree (09:25–11:20Z, `total_red: 0` throughout). Lesson recorded: **work held out of a commit must be held out of the TREE, not out of the pathspec.**
>    - **Stale `.git/index.lock`** (twice) — `git add` rc unchecked, surfacing as a misleading "pathspec did not match any file(s) known to git". Removed after verifying no git process; filed.
>    - **EP1 landing killed three times by its launcher** (`timeout 4000`; a killed wrapper taking its process group; a "detached" launch reaped with a bounded tick). Fixed by `setsid nohup … &` with no wrapper.
>    - **`--freeze` on orphan_ratchet froze 368 orphans** — reverted immediately; too blunt to use.
>    - **Segment-case guard refused `("I&C", "IC")`** — replaced with `normalise_segment` + `INDUSTRIAL_AND_COMMERCIAL`.
>    - **My `git apply` of the EP13 map patch consumed the `premise:` field line** — restored.
>    - **Omitted the standing charge** in the EV, making every customer look value-negative; then **falsely claimed it cancels between arms** — the test refused: the value-maximising margin FELL from £80 to £60 because fixed revenue sits inside the retention term. Corrected the module docstring and the test.
>    - **Reciprocal assertion was wrong arithmetic** (`win * (1/churn) == 1` asserts `m(d)² == 1`) — corrected to `churn * win == 1` below saturation, plus separate symmetry and monotonicity assertions.
>    - **Director correction accepted**: my vulnerability floor was "a stronger rule than the licence supports" — SLC 27.8 governs INSTALMENTS, not the unit rate. Floor removed.
>
> 5. **Problem Solving:**
>    Diagnosed the tick loop as neither wedged nor resting but occupied by its own alarms. Delivered and R11-verified the carbon instrument (252 residential published, 108% timing effect on C9's hardest day). Located the thesis blocker precisely: `PRICE_DIFFERENTIAL_PCT` reached the churn code and was used at exactly one site (home-move win rate), so the company could not price itself out of the market — which made a flat-rules baseline neither beatable nor losable. Fixed, then measured the resulting saturation at +25% and extended the loss leg. Then measured the belief-vs-truth gap for the first time: median −8.6pp, 156 of 263 accounts under-estimating departures.
>
> 6. **All user messages:**
>    - **(continuation prompt)** "Resume directly — do not acknowledge the summary, do not recap what was happening, do not preface…"
>    - **Turn 1**: "Yes — clear. That session is at 384k after a twelve-hour night, and everything it needs is short enough to restate." followed by the fresh-session brief quoted in full in §1 above, including verbatim: *"Never wait on me for anything reversible — act, record the reason, tell me afterwards. On figures you have three lawful outcomes: correct, caveat, or withdraw; freezing is not one of them. Measuring is never publishing. Reserved to me: curriculum values, one-way doors, money, real people. Don't report between pieces — keep going."* and *"My weekly token allowance has run out twice and the tick spawn is most of it, so don't draw work that cannot change a level and don't file a finding where a class document already covers it. And memory: the headroom the WSL raise bought is largely spent, so treat RAM as a budget you're spending rather than a problem solved."*
>    - **Turn 2**: The thesis message, quoted in full in §1.
>    - **Turn 3**: "do the meter mix / Then change how you're treating price and risk, and don't take my word for the rules — read them…" quoted in full in §1, ending *"Then keep going. No stopping, ever… I'll read what you did and correct you afterwards — that is my job, and it does not require you to wait."*
>
> 7. **Pending Tasks:**
>    - **SITE9 ruling, still not done**: *"SITE9's director-record block is overturned. Rebuild the delta as a section on /harness/."* `tools/generate_director_data.py` writes `site/data/director_delta.json` every cycle and nothing renders it. A draft section was written to `scratchpad/harness_section.html` but never applied.
>    - **The churn-cap finding** (`WORKER_FINDING_THE_CHURN_MODELS_CAP_MAKES_THE_PROFIT_MAXIMISING_PRICE_UNBOUNDED_2026-08-25`) remains BLOCKING; the value arm is deliberately NOT wired to the renewal desk.
>    - **`CREDIT_RISK_BY_CUSTOMER` segments only 4 of 263 accounts** — the differentiation just built is almost entirely uninformed.
>    - **The realised two-arm comparison** (same book, same world, one run per arm, scored on outcomes) — the only honest earnings test; needs two full runs.
>    - **`docs/domain_artefact_library/regulatory/ofgem_default_tariff_cap_windows.json` has one level per fuel**; the real cap differentiates by payment method (register §E).
>    - **Collections cost is unsourced** anywhere in the tree; the term is present and named in `unsourced`.
>    - Never verified HEAD-green against the "30 newly failing tests at 02:21Z" claim.
>
> 8. **Current Work:**
>    Immediately before this summary I landed and pushed `61a6620cc` — the belief-vs-truth measurement in `tools/couple_value_based_pricing.py`. The measurement added:
>    ```python
>    def belief_versus_truth(*, offered_rate, current_rate, tenure_years, eac_kwh, segment, term_start) -> dict | None:
>        differential = _price_differential_vs_market(offered_rate, term_start)
>        if differential is None:
>            return None
>        believed = float(enriched_churn_estimate(current_rate, offered_rate, tenure_years, float(eac_kwh), segment=segment))
>        base = float(enriched_churn_estimate(current_rate, current_rate, tenure_years, float(eac_kwh), segment=segment))
>        actual = min(base * churn_position_multiplier(differential), WORLD_MAX_CHURN_PROBABILITY)
>        return {"price_differential_vs_svt": round(differential, 4),
>                "company_believes_p_leave": round(believed, 4),
>                "world_would_p_leave": round(actual, 4),
>                "belief_error_pp": round(100.0 * (believed - actual), 1)}
>    ```
>    Live result: 263 accounts scored, **median belief error −8.6pp, mean −7.8pp, 156 of 263 under-estimating departures**. The epistemic verifier passes on 583 files. This turn's five commits, all pushed to `origin/main`: `f8dc54ef8` (meter mix), `5064540c7` (register + expected cost + floor removed), `baec3efb2` (price lever in the churn chain), `fbe8b0ab6` (loss-leg extrapolation so the world can kill an over-pricing supplier), `61a6620cc` (belief-vs-truth gap).
>
> 9. **Optional Next Step:**
>    Per the standing instruction — *"Then keep going. No stopping, ever… When you run out of the work I've named, go to the thesis"* — and the one item from the named work still outstanding, the next step is the **SITE9 ruling**: *"SITE9's director-record block is overturned. Rebuild the delta as a section on /harness/."* The draft section HTML is already prepared in `scratchpad/harness_section.html`; it needs the JS renderer for `site/data/director_delta.json` (which must state honestly that `last_look_recorded_by` is `"bootstrap-at-build-time (not a director read receipt)"` and `last_look_at` is 2026-08-03), a render-path test in `site/`, and SITE9's map entry updated with a `**Discharged:**` line naming a test node. **Caution learned this session**: `site/**` edits must land with their tests in the same pass, and nothing may be held in the working tree or index between edit and commit — the producer runs the working tree and the level gate reads the tree, which caused two publish outages today.
>
> If you need specific details from before compaction (like exact code snippets, error messages, or content you generated), read the full transcript at: /home/rich/.claude/projects/-/c6cee6e9-62fb-45a2-8e17-d45aa524771f.jsonl
> Continue the conversation from where it left off without asking the user any further questions. Resume directly — do not acknowledge the summary, do not recap what was happening, do not preface with "I'll continue" or similar. Pick up the last task as if the break never happened.

### 2026-08-25T16:44:14.599Z

> Better — a self-written handover is prose it has to reconstruct from; a compact keeps the working state. And it's already told us everything the next session needs, so the context can go in the paste.
>
> ```
> /compact
> ```
>
> Then paste:
>
> ```
> Fresh context. You are the autonomous builder on Poesys. It's
> Tuesday evening, 25 August.
>
> Where you got to. You wired the price signal into the churn chain
> — it had reached the code but was used at exactly one site, the
> home-move win rate, so the churn model never read the company's
> own price. That meant the supplier could price itself anywhere and
> lose nobody, and a flat-rules baseline could be neither beaten nor
> lost to on the only lever a supplier holds. With both sides moving,
> the belief error is real for the first time: 263 accounts scored,
> median −8.6pp, under-estimating departures on 156 of them. C3 sits
> 21% below SVT and cannot tell "I raised your price 10%" from "I am
> still the cheapest available". You predicted the value arm would
> lose to the flat control if wired today, and left it unwired. The
> churn-cap finding is BLOCKING — a market-wide switching ceiling
> bounding an individual's response, third instance of that shape.
>
> Also landed: meter mix drawn at acquisition off the DESNZ series
> (14 to 143 half-hourly capable, 54.2% blended); the licence
> register in the commons with SLC 27.2A, 7.3/7.4, 27.8A and the
> 1998 Act cited verbatim; and expected cost inside the EV — bad
> debt on the whole bill, which showed the flat £2 margin was a
> ~£40/year cross-subsidy from reliable payers to unreliable ones.
>
> Next: fix the churn model, then run both arms. Publish the result
> honestly whichever way it goes — a company whose prediction is
> worse than its arithmetic is the finding, not a failure.
>
> Then keep going. No stopping, ever — not between pieces, not to
> report, not to ask. When something finishes, start the next thing.
> When you run out of what I've named, go to the thesis: a faithful
> world, and a supplier deciding customer-by-customer on what it can
> infer, beating a flat-rules baseline only through better
> prediction. Nothing here is irreversible — no money, no customers,
> no licence — so decide and act, and record what you chose and what
> you rejected. That record is what I review, and it replaces asking.
>
> Don't panic about the website. Nobody is reading it. Keep it
> honest when you touch it and let the banner do its job when it's
> behind, but never interrupt real work to chase it.
> ```
