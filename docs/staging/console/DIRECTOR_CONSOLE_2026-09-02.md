**Severity:** RECORDED · **Lane:** H_harness

# Director console — verbatim record, 2026-09-02

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

Source: `650509ea-4293-4a86-beb1-cb466ee395d8.jsonl` · 6 turn(s).

### 2026-09-02T06:21:10.101Z

> 830 newly failing tests at HEAD at 03:29Z, 760 of them OSError.
> That's the biggest red this month and the shape says environmental
> rather than logical. It appeared hours after the reaper ran for
> the first time and cleared six worktrees. Check that adjacency
> first — the reaper is the one thing on the box that deletes
> directories, and it had never run before last night.
>
> If it isn't the reaper, say so and find what it is. Either way
> that outranks the level-anchor work.
>
> Then the class-debt understatement you filed: sample the 116
> title-matched archives before folding them, as you said, but don't
> leave the draw ordering wrong for long — a class repaired on sight
> twenty times reading as zero debt is the exact thing the measure
> exists to prevent.

### 2026-09-02T07:48:54.611Z

> Read docs/staging/DIRECTOR_BRIEF_INDEPENDENT_BILL_VALIDATION_
> 2026-09-02.md now. It comes out of the journey walk and the
> bill-shock work: our arithmetic has never been checked against
> anything outside itself. Six properties are fixed; the rest is
> yours to improve. Sequence it yourself.

### 2026-09-02T08:28:44.384Z

> Your objection on the bill export was right — corrected in the
> staged document with the correction recorded, and the severity
> header added. The unclassified block was my defect three times
> over; it won't recur.
>
> Reconcile-on-the-deadman-cadence is a better design than the one
> I asked for. Take it.
>
> The conflict door needs its design pass, as you say — the next
> time two lanes touch one file there's no legal route, and that's
> a wall with a hole in it. Sequence it yourself.
>
> Then the validation brief, and keep going.

### 2026-09-02T17:54:06.972Z

> /compact

### 2026-09-02T17:56:33.363Z

> This session is being continued from a previous conversation that ran out of context. The summary below covers the earlier portion of the conversation.
>
> Summary:
> 1. **Primary Request and Intent:**
>
>    **Message 1 (housekeeping, two items):** (a) *"Six undeclared worktrees are accreting and being reported rather than cleared — that's the isolation machinery working with nothing tidying up behind it. Give them a lifetime."* (b) *"the channel under-reports you. Eight commits this evening produced no message, while divergence and publishing alarms filled the mirror. I've read that as a stall twice today when you were working normally. Real work should reach the channel and routine noise shouldn't crowd it out."*
>
>    **Message 3 (the 830):** *"830 newly failing tests at HEAD at 03:29Z, 760 of them OSError. That's the biggest red this month and the shape says environmental rather than logical. It appeared hours after the reaper ran for the first time and cleared six worktrees. Check that adjacency first — the reaper is the one thing on the box that deletes directories, and it had never run before last night. If it isn't the reaper, say so and find what it is. Either way that outranks the level-anchor work."* Plus: *"Then the class-debt understatement you filed: sample the 116 title-matched archives before folding them, as you said, but don't leave the draw ordering wrong for long — a class repaired on sight twenty times reading as zero debt is the exact thing the measure exists to prevent."*
>
>    **Message 4 (fix the route):** *"Why hasn't the 830 been fixed? My reading: the HEAD-green census reports and nothing draws it. Twelve, seventeen, thirty-three and now 830 — each announced, none worked, while everything with a route into the draw gets done. Same shape as the reaper built in July and never called. Two things make it worse. The baseline is a file from 12 August, so 'newly failing' means 'not in a three-week-old list' — a number that drifts up and can never reach zero, and nothing that cannot be done gets prioritised. And it's reported as a count with no named test, so there's nothing to fix, only a number to worry about. Fix the route, not just the instance. Red tests at HEAD need a way into the queue with the same standing as a class register — a named subject, a live baseline, and an end state where zero means zero."*
>
>    **Message 5 (not on origin):** *"Nothing from that report is on origin — the last commit there is 06:11Z, before the daemon restart, the TMPDIR fix and the red register. Push, and verify against origin before saying landed. One cause may be mine: I staged a document at 07:45Z, which moved origin ahead of your local HEAD, and your origin-ahead guard then refuses your commit until you pull. If that's what's happening, make the pull automatic rather than a refusal — a staged document arriving should never block your landing. The site is also four hours stale."*
>
>    **Message 6 (current, sequencing):** *"Your objection on the bill export was right — corrected in the staged document with the correction recorded, and the severity header added. The unclassified block was my defect three times over; it won't recur. Reconcile-on-the-deadman-cadence is a better design than the one I asked for. Take it. The conflict door needs its design pass, as you say — the next time two lanes touch one file there's no legal route, and that's a wall with a hole in it. Sequence it yourself. Then the validation brief, and keep going."*
>
> 2. **Key Technical Concepts:**
>    - Worktree lifecycle: create → lease → salvage → reap; `OWNER_MARKER` claims; `salvage/detached-*` tags
>    - The deadman cycle (`background/deadmans_switch.run_cycle`) as the home for periodic checks
>    - Mutation-proven controls (a mutation that does not fire is either a missing test or an equivalence — establish which)
>    - Fail-closed vs fail-open; positive-only identification; dated population floors
>    - The notification contract: `notify.KINDS` (G-N2), `topic_class` routing (G-N3), transition-only (G-N1/R5)
>    - `surgical_land` as the only sanctioned commit door; receipts; `--verify`; hook-bypass is a wall
>    - Shared index vs worktree index (why `git merge` is forbidden on the shared tree)
>    - The epistemic wall (`company/`, `saas/` vs `sim/`, `simulation/`), `tools/epistemic_verifier`
>    - Orphan ratchet (`no_caller_and_never_runs` class), shrink-only ratchets
>    - Pre-registration discipline: file predictions before the run, keep wrong ones beside results
>    - Unit-declaring export schema (MEASURED / CONTRACTED / MOVED / IDENTIFIER / EVENT vs forbidden GBP_COMPUTED)
>
> 3. **Files and Code Sections:**
>
>    - **`background/seat_executor.py`** — added the lease. `OWNER_LEASE_SECONDS = SESSION_TIMEOUT_SECONDS + 30 * 60` and `_claim_age_seconds()`; `worktree_is_live` now requires both legs:
>      ```python
>      if pid_is_alive(marker) and age is not None and age < OWNER_LEASE_SECONDS:
>          return True
>      ```
>      Reason: five markers named **pid 215 — the tmux server**, alive since 2026-08-24.
>
>    - **`background/fork_reconciler.py`** — `_LIVE_REFUSALS` gained `"live writer"` then `"declared daemon"`; new `advance_stranded()`, `_why_stranded()`, `declared_daemon_homes()`, `_git_dir_may_hold_work` counterpart in disk_headroom. `classify_worktree_reap` gained `declared_homes` param. Enforce branch gained the STRANDED status (the 2026-08-03 fail-silent fix had landed on the report-first branch only).
>
>    - **`background/deadmans_switch.py`** — added `_check_worktree_reap()` and `_check_origin_fork()` to `run_cycle`; keys `_WORKTREE_REAP_KEY`, `_ORIGIN_FORK_KEY`. Note the import block must keep its `# noqa: E402` shape (ruff --fix broke it once, raising E402 above baseline).
>
>    - **`background/head_red_register.py`** (NEW) — observation store `docs/observability/head_red_observed.json`, register `docs/staging/reference/HEAD_RED_REGISTER.md`, `record()` (writes no file), `owed()`, `oldest_first()`, `render()`, `drawable()`. Split: machine writes OBSERVATION, only a person writes ACCEPTANCE.
>
>    - **`background/staging_rooms.py`** — `KIND_HEAD_RED = "head_red"` at `ORDER` rank 37; `_STANDING_REGISTERS = frozenset({"HEAD_RED_REGISTER.md"})`; `_with_the_head_red_register()` splices only while something is owed.
>
>    - **`tools/head_green_census.py`** — `verdict()` no longer says "newly failing"; `_record_observation()`; `SUITE_TIMEOUT_SECONDS = 3300` (was 3600 = systemd's); TMPDIR fix:
>      ```python
>      env = dict(os.environ)
>      env.setdefault("TMPDIR", str(prc.HEAD_CHECKOUT_ROOT))
>      proc = subprocess.run(pytest_argv(), cwd=str(subject), env=env, ...)
>      ```
>
>    - **`background/class_debt.py`** — `recurrence`, `recent_recurrence` fields; `recurrence_paths()` (root + archive, minus externally-authored and self-clearing-alarm prefixes); `FLOOR_RECURRENCE = 212`; `still_accruing` uses `max(...)`; re-arm uses `seen = max(self.instances, self.recurrence)`. `order_key` deliberately unchanged.
>
>    - **`background/disk_headroom.py`** — `_git_dir_may_hold_work()` replacing the blanket `if (path / ".git").exists(): continue`. Returns True (spare) for: `.git` FILE, refs present, HEAD resolves, any exception. Found `/var/tmp/head-verify-4161726` (146 MB, 450 h) on first run.
>
>    - **`background/origin_reconcile.py`** (NEW) — `fork_state()` (the ONE seam), `commits_behind()`, `commits_ahead()`, `reconcile()` returning LEVEL / RECONCILED / PUSHED / REFUSED_CONFLICT / REFUSED_GATE / UNREADABLE / ERROR. Merges in `/var/tmp/se-origin-reconcile` via `surgical_land --merge`; shared tree only ever `--ff-only`.
>
>    - **`background/staging_watcher.py`** — `AUTO_CHAIN_LANE = "A_strategy_governance"`, `auto_chain_header()`, `auto_chain()`; called in the new-file loop BEFORE the announcement.
>
>    - **`tools/surgical_land.py`** — the conflict door:
>      ```python
>      def build_merge_tree(root, parent, other, resolutions: Mapping[str, bytes] | None = None) -> str:
>      ```
>      plus `_overlay_on_tree()`, `_conflicted_paths()` (stops at the blank line), `--resolve REPOPATH=SRCFILE` CLI (refuses sources INSIDE the repo), receipt line `conflicts-resolved:`, and `parse_receipt` returning `conflicts_resolved`. Also `announce_landing()` earlier in the session.
>
>    - **`company/billing/raw_account_export.py`** (NEW, brief item 1) — `FIELDS: dict[str, tuple[str, str]]` declaring unit + why-raw for every field; `GBP_COMPUTED` forbidden; `derived_leaks()` recursing into lists/dicts; `export_account()` refusing on the way out with `DerivedFieldLeaked`. Docstring states the limit verbatim: *"validates the ARITHMETIC over the rates, not the RATES."*
>
>    - **Test files created:** `tests/background/test_a_worktree_claim_expires_and_the_reaper_has_a_caller.py`, `test_real_work_reaches_the_channel_and_noise_does_not_crowd_it.py`, `test_red_at_head_has_a_route_into_the_draw.py`, `test_a_class_fixed_on_sight_still_recurred.py`, `test_an_empty_git_dir_made_scratch_immortal.py`, `test_a_staged_document_no_longer_blocks_every_landing.py`, `test_an_arriving_document_chains_itself.py`, `tests/tools/test_a_landing_notification_cannot_be_written_by_a_test.py`, `tests/tools/test_the_conflict_door.py`, `tests/company/billing/test_the_raw_export_carries_nothing_derived.py`.
>
> 4. **Errors and fixes:**
>    - **Reaper adjacency (director's hypothesis) — REFUTED.** `ps` showed the deadman started Mon Aug 24 15:16:32 and `grep -c "WORKTREE REAP"` = 0. Told him plainly the fix was "wired in git and absent in the running machine".
>    - **`_LIVE_REFUSALS` missing "live writer"** — would have made `advance_stranded` commit into a live writer's tree. Caught while writing the guard.
>    - **First `--resolve` token mismatch:** `"declared home"` vs a reason reading `"a declared daemon's home worktree"` — my own class control caught it.
>    - **`order_key` lexicographic units** and **read-before-write** (`recent_recurrence` read `recent_instances` before assignment) — both caught by inspection.
>    - **Pre-registration P1/P2 refuted:** I predicted `instance_names()` where the code reports `instances` (which includes out-of-lane), and my hand table omitted the RECORDED-in-root leg my own prose specified. So my *correction* ("the order is identical") was also wrong. Kept both beside the result.
>    - **Landing producer shipped SILENT** — `background.notify` unimportable without `SE_NTFY_TOPIC`; the `except` swallowed it. Fixed with `load_secret_env()` + stderr. First draft of `load_secret_env` leaked `SE_WAKE_HMAC_KEY`; added an `only=` allowlist with `MODEL_FACING_FORBIDDEN_SECRETS` as a hard floor.
>    - **`origin_reconcile` shipped BEHIND-only** — its own landing sat unpushed within the hour. Found by running `git merge-base --is-ancestor`.
>    - **Conftest pin went partial** — pinned `commits_behind`, then added `commits_ahead`; 28 deadman tests red twice. Fixed by introducing `fork_state()` as one seam.
>    - **`merge-tree --name-only` parse defect** — took everything after the tree sha, so a one-file conflict read as "4 conflicted path(s)" with `Auto-merging …` as a filename. Harmless as prose, fatal once matched against a resolution set.
>    - **Vacuous/brittle assertions I wrote and removed:** `assert ... or True`; `"amount_gbp\":" not in flat` (matched `payment_amount_gbp`); `git cat-file -e "HEAD"` resolving against the main repo (a check that could not fail); source-slicing assertions replaced with behavioural tests.
>    - **cwd drift near-miss:** the hand merge ran in the worktree only because an earlier `cd` persisted; had it persisted the other way it would have committed another lane's 57 staged entries. Recorded; used `git -C` thereafter.
>    - **Evidence destroyed:** reclaimed 1.03 GB of /tmp before capturing the reaper's per-directory verdict. Recorded as my error.
>
> 5. **Problem Solving:**
>    Cleared six accreting worktrees via three stacked defects (no caller, immortal pid claim, dead-end refusals). Rebuilt the notification channel in both directions. Refuted the reaper adjacency and traced the 830 to tmpfs exhaustion amplified by four autouse `tmp_path` fixtures (errno still an inference — the repro timed out). Built the HEAD-red route into the draw. Corrected my own class-debt claim twice. Closed the origin fork and automated it. Built the conflict door and used it on its own subject. Started brief item 1.
>
> 6. **All user messages:**
>    - *"Two housekeeping things, neither urgent. Six undeclared worktrees are accreting and being reported rather than cleared — that's the isolation machinery working with nothing tidying up behind it. Give them a lifetime. And the channel under-reports you. Eight commits this evening produced no message, while divergence and publishing alarms filled the mirror. I've read that as a stall twice today when you were working normally. Real work should reach the channel and routine noise shouldn't crowd it out."*
>    - `/compact` (local command, not a request)
>    - *"830 newly failing tests at HEAD at 03:29Z, 760 of them OSError. That's the biggest red this month and the shape says environmental rather than logical. It appeared hours after the reaper ran for the first time and cleared six worktrees. Check that adjacency first — the reaper is the one thing on the box that deletes directories, and it had never run before last night. If it isn't the reaper, say so and find what it is. Either way that outranks the level-anchor work. Then the class-debt understatement you filed: sample the 116 title-matched archives before folding them, as you said, but don't leave the draw ordering wrong for long — a class repaired on sight twenty times reading as zero debt is the exact thing the measure exists to prevent."*
>    - *"Why hasn't the 830 been fixed? My reading: the HEAD-green census reports and nothing draws it. Twelve, seventeen, thirty-three and now 830 — each announced, none worked, while everything with a route into the draw gets done. Same shape as the reaper built in July and never called. Two things make it worse. The baseline is a file from 12 August, so 'newly failing' means 'not in a three-week-old list' — a number that drifts up and can never reach zero, and nothing that cannot be done gets prioritised. And it's reported as a count with no named test, so there's nothing to fix, only a number to worry about. Fix the route, not just the instance. Red tests at HEAD need a way into the queue with the same standing as a class register — a named subject, a live baseline, and an end state where zero means zero."*
>    - *"The report is excellent, but none of it is on origin. The last machine commit there is 07:11 — before the reaper restart, the TMPDIR fix and the red register. Same shape as this morning: landed in the tree, reported as landed, not pushed. And I may be causing part of it. My staging push at 08:45 moved origin forward, and it built a guard yesterday that refuses to commit while origin is ahead. So every time I stage a document, its local HEAD falls behind and its own guard blocks it until it pulls. That would explain why its landings keep failing to appear right after I've sent something. [...] Nothing from that report is on origin — the last commit there is 06:11Z, before the daemon restart, the TMPDIR fix and the red register. Push, and verify against origin before saying landed. One cause may be mine: I staged a document at 07:45Z, which moved origin ahead of your local HEAD, and your origin-ahead guard then refuses your commit until you pull. If that's what's happening, make the pull automatic rather than a refusal — a staged document arriving should never block your landing. The site is also four hours stale."*
>    - *"Read docs/staging/DIRECTOR_BRIEF_INDEPENDENT_BILL_VALIDATION_2026-09-02.md now. It comes out of the journey walk and the bill-shock work: our arithmetic has never been checked against anything outside itself. Six properties are fixed; the rest is yours to improve. Sequence it yourself."*
>    - *"Your objection on the bill export was right — corrected in the staged document with the correction recorded, and the severity header added. The unclassified block was my defect three times over; it won't recur. Reconcile-on-the-deadman-cadence is a better design than the one I asked for. Take it. The conflict door needs its design pass, as you say — the next time two lanes touch one file there's no legal route, and that's a wall with a hole in it. Sequence it yourself. Then the validation brief, and keep going."*
>
>    **Security/constraint instructions in force (from CLAUDE.md, must be preserved):** HOOK-BYPASS IS A WALL — `--no-verify` and hand-built `commit-tree`/`merge-tree` merges are never a judgement call; the legal move is `python3 -m tools.surgical_land`. The company has no route to the real world — `company/` and `saas/` may not open a socket, ever. The epistemic wall: the company may only know what a real UK supplier could know; `company/interfaces/sim_interface.py` is the seam. You may never widen the sandbox profile (director-console-only). Only four reserved classes: spending real money, contacting real people, an irretractable public claim under Poesys's name, anything touching a real person's safety. Commit by pathspec, never `-A`. `SE_WAKE_HMAC_KEY` must never reach a model-facing process. `--content`/`--resolve` source files must live outside the repository.
>
> 7. **Pending Tasks:**
>    - Brief item 2: the statement export (issued bills as documents, calculation line by line, balance after each event)
>    - Brief item 3: the curtained validator (cannot import billing code, curtain proved by mutation)
>    - Brief item 4: the comparison, filing every difference, validator wins by default
>    - Brief item 5: one account first, then every account on every run, scheduled
>    - Brief item 6: a plain statement of what the design cannot catch
>    - My proposed improvements to the brief, stated to the director but not yet built: conservation checks that encode no domain knowledge; the reconstruction hashed before the statement is opened (§4.3 as an artefact); per-rule commons citations
>    - The site was still reported DOWN (figures last moved 3.8h ago) — I owed a confirmation rather than an assumption
>    - The 830 errno remains an inference; tonight's scheduled census with TMPDIR on real disk is the test
>
> 8. **Current Work:**
>    Immediately before the summary request I had, in the final segment: chained the director's corrected brief by hand one last time; built and landed `staging_watcher.auto_chain` (9b2474c59); built and landed the conflict door in `tools/surgical_land.py` (908726d24); used it on its own subject producing merge `e3730c4e9` with receipt line `conflicts-resolved: docs/staging/DIRECTOR_BRIEF_INDEPENDENT_BILL_VALIDATION_2026-09-02.md` and `--verify` clean; filed the conflict-door finding (b7aa75e1c); and built brief item 1, `company/billing/raw_account_export.py` plus 20 tests, landed as 145d48345 after the orphan ratchet correctly caught it and I froze the baseline (382 → 376, a shrink — `fork_salvage` and `seat_executor` left the orphan list because today's work wired them). `origin_reconcile.reconcile()` reported LEVEL and all four commits were verified ON ORIGIN with `git merge-base --is-ancestor`. I sent the director an ntfy and wrote the memory `feedback_a_wall_needs_a_door_for_every_state_it_forbids.md`, adding its index line to MEMORY.md. Another lane was concurrently landing the DD/EAC repair.
>
> 9. **Optional Next Step:**
>    Continue the brief in sequence: build **item 2, the statement export** — *"The statement export — what we claim. The issued bills as documents, exactly as the customer saw them; every bill's calculation shown line by line; and the balance after each event across the account's life — the transaction history a real supplier gives a customer, and a bill that shows how it reached its number. This is what the validator's reconstruction is compared against."* This is directly in line with the director's *"Then the validation brief, and keep going"* and with my own message to him: *"Next from me: the statement export, then the curtain."*
>
> If you need specific details from before compaction (like exact code snippets, error messages, or content you generated), read the full transcript at: /home/rich/.claude/projects/-/650509ea-4293-4a86-beb1-cb466ee395d8.jsonl
> Continue the conversation from where it left off without asking the user any further questions. Resume directly — do not acknowledge the summary, do not recap what was happening, do not preface with "I'll continue" or similar. Pick up the last task as if the break never happened.

### 2026-09-02T18:00:52.966Z

> Stop the reconcile daemon and look at what it's doing. Twelve
> commits in the last hour, every one "merge origin/main: automatic
> reconciliation", one every six minutes, no real work among them.
> Publishing has been down 13 hours, the gate is wedged, two mints
> have been blocked for three hours and a drawable item sits
> untouched.
>
> My reading — check it rather than take it: a merge landing every
> six minutes moves HEAD faster than any gate can complete, so every
> publish gate run is invalidated before it finishes. The reconcile
> you built to stop the behind-origin refusal is now manufacturing
> the HEAD-moved refusal on a loop. Cure became the next cause,
> same shape as the banner on the 20th.
>
> Fix the mechanism, not the instance: reconcile only when there is
> something of ours to land, never on a cadence, and never while a
> gate is running. Then clear the wedge, publish, and take the
> blocked mints.
>
> Then the reason you didn't see it, because that matters more than
> this loop. Every instrument you have counts commits, gates them or
> receipts them. None reads them. Twelve identical titles in an hour
> was visible at a human glance and invisible to you by
> construction, because nothing asks whether a commit carries any
> work — so a daemon producing empty merges lit up every liveness
> surface you have. Give the delivery seat that vantage: every
> orientation reads the last stretch of commits as a list a person
> would read — what landed, what it was, whether the shape is
> right — and treats a run of identical commits, or a stretch with
> nothing substantive, as a finding about the machine rather than
> a sign of health. That would have caught this in ten minutes.
>
> Then keep going.
