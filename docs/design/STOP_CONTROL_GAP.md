# Stop-control gap characterisation (SPEC_005 §7.13 material-safety)

**Provenance.** DISCOVER-half of `docs/staging/PLANNER_MINTED_stop_control_gap_characterisation_2026-07-28.md`
(source: `docs/design/FIRST_RANKED_GAP_LIST.md` §2 machinery row M2). **Doc-only, inventory + characterisation.
No safety control is added, modified, wired, or removed by this atom.** Adding/altering a run-hold/kill/governor
control is a category-5 one-way door (safety-control change, `CLAUDE.md` PROCEED-BY-DEFAULT list item 5) —
director-console-only, never self-authorised. R12: this is a diagnostic, not a score.

---

## 1. Control inventory

Every existing hold/kill/governor affordance found by reading `background/executor_governor.py`,
`background/executor_daemon.py`, `background/sim_runner.py`, `.claude/hooks/pull_next_work.py`,
`background/worker_tick.py`, `background/build_executor.py`, and `background/deadmans_switch.py`.

| # | Control | What it halts | Trigger | Release tested? |
|---|---|---|---|---|
| 1 | **`.build_executor_enabled`** (`docs/observability/.build_executor_enabled`), read via `executor_governor.kill_switch_enabled()` → `_pull_hook._autonomous_execution_enabled()` | The **one durable kill switch for all autonomous execution** (DIRECTOR_ANSWERS_C7 #6): gates (a) the headless `executor_governor.run_loop` before every cycle, (b) `executor_daemon.run_forever`'s outer `while kill_switch()`, (c) the interactive Stop-hook pull loop (`.claude/hooks/pull_next_work.py`), (d) `worker_tick.decide_tick`'s systemd-tick spawn gate. Director removes/renames the file (console-only; the agent may only read it — `test_governor_never_writes_the_enable_flag` asserts the source contains no write verb against `ENABLE_FLAG`). | File **absence/non-file** = OFF (fail-closed); presence of a readable regular file = ON. | **YES, but only at the loop/cycle boundary, not mid-turn.** `test_run_loop_continues_until_kill_switch_flips` (tests/background/test_executor_governor.py:575) proves: flag removed after cycle 3 → loop stops with `kill_switch_off` after exactly 3 cycles — the *next* cycle never dispatches. `test_kill_switch_disabled_no_spawn` / `test_autonomy_enabled_fail_closed` (tests/background/test_worker_tick.py) prove the same for the tick spawn gate. **No test (and no code path) proves it terminates an already-dispatched, in-flight `claude -p` subprocess** — see §3. |
| 2 | **`docs/review_gates/.sim_runner_hold`** (`sim_runner.HOLD_FLAG`) | New simulation runs in `background/sim_runner.py`'s `while True` loop — director hold on publishing new results. | File presence checked at top of every loop iteration (`_check_hold`); presence → skip run, sleep 120s. | **YES, including the release side-effect.** `test_check_hold_flag_present_skips_and_marks_held`, `test_check_hold_flag_still_present_stays_held_no_relog`, and critically `test_check_hold_cleared_transition_touches_force_republish_flag` (tests/background/test_sim_runner.py:223) prove the hold→clear transition forces the next publish through (no orphan transition, R11/OPS1-compliant). **Only halts the *next* run being started — does not kill an in-flight `subprocess.run(..., timeout=7200)` annual-report simulation already executing** (no `.kill()`/`.terminate()` call anywhere in `sim_runner.py`; confirmed by grep). |
| 3 | **R3 two-strike (`MAX_CONSECUTIVE_FAILURES=2`)**, `executor_governor.run_loop` | The headless loop itself, after 2 consecutive failed/errored turns. | Automatic (no human trigger) — `consecutive_failures >= max_consecutive_failures` → `stop_reason="repeated_failure"`, alerted via NTFY. | Yes as an automatic halt (covered by the loop's own test suite), but this is a **self-diagnosed halt, not a human-triggered stop control** — out of scope for §7.13's "reach a stop control" requirement, included here for completeness of the inventory. |
| 4 | **`TurnBudget`** (`executor_governor.TurnBudget`) | New turn dispatch once the sliding-window turn/token cap is full. | Automatic, config-driven (`max_turns_per_window`), fail-closed if unconfigured. | Rate-limiter, not a stop control — a full budget self-clears as the window slides; not director-triggered. Included for completeness. |
| 5 | **`code_stale` self-staleness re-exec**, `executor_daemon.run_forever` | The daemon's *own process*, when its on-disk source has drifted from what it imported. | Automatic (`source_fingerprint()` mismatch), not human-triggered. | Not a human stop control — a self-healing re-exec. Included for completeness. |
| 6 | ~~**`docs/observability/.comment_intake_locked`**, `background/director_comments.py`~~ — **NOT A CONTROL. Falsified 2026-08-03 by `background/stop_control_audit.py`.** | **Nothing.** | — | The 2026-07-28 pass listed this as an existing director-only halt flag, on a user-memory citation, and marked it "not audited in this pass". Auditing it refutes it: the page-comment channel was **retired permanently** on 2026-07-24 (`DIRECTOR_RULING_RETIRE_PAGE_COMMENT_CHANNEL_2026-07-24.md`), `background/director_comments.py`'s intake path is *deleted* and its `main()` is a permanent safe no-op, **no source in the repo references `.comment_intake_locked` at all**, and `background/process_manifest.yaml` declares `director-comments` `state: retired`. A lock over a process that must never run halts nothing. Row kept, reclassified — see §6. |
| 7 | **Per-turn timeout kill**, `background/build_executor.py::reap_turn` / `_reap_surplus_child` | One already-dispatched `claude -p` child process, when its own per-turn deadline (`timeout`) elapses, or once landed evidence makes it surplus. | Automatic (`monotonic() >= deadline` or landed-evidence detected) — calls `proc.kill()`. | This **is** a mechanism that can terminate a live subprocess — but it fires on an internal timer/landed-evidence condition, **not on a director stop request**. It proves the *capability* to kill a live child exists in the codebase (so a director-triggered version is a small delta, not new invention — relevant to §4 below), but it is not itself reachable by a human. |
| 8 | **Dead-man's switch**, `background/deadmans_switch.py` | Nothing directly — it is a detector/alarm (NTFY `[BLOCKED]`/`[STALL]`), external to the tmux/supervisor stack, keyed on the meaningful-git-commit clock. | Automatic, on elapsed thresholds. | It is **not a stop control at all** — it never halts anything, only alerts. Listed to rule it out explicitly: it is sometimes informally described as a "safety net" but does not satisfy "reach a stop control — a way to halt autonomous operation" (§7.13). |

---

## 2. The SPEC_005 §7.13 requirement

From `docs/design/BOARD_SPEC_005_RECONCILIATION.md` (line-by-line reconciliation of
`docs/staging/BOARD_SPEC_005_WEBSITE_2026-07-22.md`), battery row **§7.13**:

> **7.13** — "can see a problem but must go elsewhere to act, **or stop control >1 screen away**" — reconciles to
> 3.PAIR + 3.DO.stop — **verdict: ABSENT** — evidence: "Read-only site → must use the console; no stop control at
> all" — notes: "Core conflict + material safety gap (Director Findings #2)."

And the underlying §3 row it derives from, **3.DO.stop**:

> "reach a stop control — a way to halt autonomous operation — never more than one screen away" — verdict
> **ABSENT** — evidence: "grep for stop-control/halt/kill-switch/pause across all `site/**.html` = none" — note:
> "Material safety gap in the window; advance = an authenticated stop control ≤1 screen from the landing
> (note: writing a live control is one-way-door cat 5/8, director-reserved)."

The requirement is explicitly a **director-window / public-surface reachability** requirement: a stop
affordance discoverable and actuable from the director's window (`site/director/` or `site/now/`) within one
screen, without dropping to a terminal/console.

---

## 3. The TRUE RESIDUAL GAP — named with evidence

The board's own §7.13 evidence line ("no stop control at all") is **accurate for the site/window surface it
grepped, and only that surface** — confirmed independently: `grep -ri "stop-control\|kill-switch\|halt\|pause"
site/**/*.html` (re-run this session) returns no reachable director-facing affordance anywhere under `site/`.

But the board's phrasing ("no stop control at all") is **broader than the evidence supports** when read against
the backend, and §1 above shows real governor coverage exists there. The true residual, precisely:

- **What the existing governor already stops:** *starting new autonomous work.* Removing/renaming
  `docs/observability/.build_executor_enabled` (or creating `docs/review_gates/.sim_runner_hold`) reliably
  prevents the **next** headless turn / tick spawn / simulation run from beginning, and — for the sim-runner
  hold specifically — the release transition is tested end-to-end including its no-orphan-transition
  side-effect (control #2, §1). This is real coverage of the *"halt autonomous operation going forward"* half
  of §7.13's requirement.

- **What it does NOT stop (the residual):**
  1. **No director-facing surface.** Both real kill mechanisms are bare filesystem flags manipulated only via
     a terminal/console (`docs/observability/.build_executor_enabled`, `docs/review_gates/.sim_runner_hold`).
     There is no affordance reachable from `site/director/` or `site/now/` — confirmed by the board's own grep
     and independently re-confirmed this session. §7.13's "≤1 screen from the landing" bar is unmet **not
     because no kill mechanism exists, but because the existing mechanism is console-only** — this is the
     3.PAIR / F2 canon conflict already logged in `BOARD_SPEC_005_RECONCILIATION.md` (read-only rendering vs.
     an acting window), not a fresh finding.
  2. **No mid-flight kill.** Every tested release path (control #1, control #2) acts at a **loop/cycle
     boundary** — it prevents the *next* iteration, it does not terminate a currently-executing `claude -p`
     turn or a currently-executing `subprocess.run(..., timeout=7200)` simulation. `sim_runner.py` contains no
     `.kill()`/`.terminate()` call reachable from the hold flag at all (grep-confirmed). `build_executor.py`
     **does** contain `proc.kill()` (control #7), proving the codebase already has the primitive to terminate a
     live child — but it is wired only to an internal timeout/landed-evidence condition, never to a
     director-triggered stop. So "halt autonomous operation" is true in the *"stop starting more"* sense and
     false in the *"stop what's running right now"* sense — the board's "halt autonomous operation" language
     (§3.DO.stop) most naturally reads as the latter.
  3. **Coverage is fragmented, not unified.** There is no single "stop control" — there are at minimum two
     independent flags (execution-wide `.build_executor_enabled`, sim-runner-specific `.sim_runner_hold`) plus
     an unrelated comment-intake lock, each with its own semantics, tested independently, with no single
     authenticated action that halts "autonomous operation" as one concept.

**One-line true residual:** *the project already has console-only, cycle-boundary-effective, independently-
tested kill flags that reliably stop new autonomous work from starting — the gap is a director-window-reachable,
authenticated, single stop affordance capable of halting an in-flight turn, which does not exist anywhere in the
codebase today.*

**Coverage verdict: PARTIAL**, with evidence:
- Backend/process-level coverage of "prevent further autonomous work" = substantial and tested (controls #1, #2
  above, both with cited passing tests including a release-transition test for #2).
- Director-window-reachable / authenticated / mid-flight coverage (what §7.13 actually names) = **none** — this
  slice of the board's "ABSENT" verdict stands unrefuted by anything found in this pass.

---

## 4. Minimal compliant stop-control SKETCH (design only — not built)

A design sketch only, to let the director scope the category-5 decision from an honest baseline. **Nothing
below is implemented by this atom.**

**Guarantees a minimal compliant control would need:**
1. **Reachable ≤1 screen from the director landing** (`site/director/` or wherever the operator window's
   default lands) — an authenticated affordance, not a public one (5.CONTROL / 5.SECRETS must stay MET: no
   write/steer/auth channel becomes publicly reachable or enumerable).
2. **Actuation writes the SAME durable flag the existing governor already reads** (`.build_executor_enabled`
   OFF, or a new equally fail-closed sibling) — reuses control #1's fail-closed semantics and its existing test
   coverage, rather than inventing a second definition of "autonomy enabled" (the project's own standing rule:
   "ONE flag governs the pull loop AND any future headless executor — no second flag").
3. **A tested release path**, matching control #2's bar: flipping the control back ON must have a *defined,
   tested* re-arm effect (no orphan transition, per OPS1 / R11) — not just an inert flag flip.
4. **Mid-flight reach**, closing residual gap 3.2 above: extending the existing `proc.kill()` primitive
   (control #7) so a live turn/simulation subprocess can be terminated on-demand, not only on its own internal
   timeout — this is the one net-new mechanism the sketch requires; everything else is wiring onto what already
   exists.
5. **Authentication equivalent to the existing PIN-gated director-comments channel** (`site/shared/director-comments.js`
   + `background/director_comments.py`), so the actuation path does not become a new, weaker write surface.
6. **Auditable**: every actuation logged (mirrors `background/decision_log.py` / gate_authorizations discipline)
   so a stop is part of the record, not silent.

This sketch deliberately reuses existing tested primitives (#1's flag semantics, #2's release-transition
pattern, #7's kill capability) rather than proposing new machinery — the residual is narrower than "build a stop
control from scratch."

---

## 5. [ACT] escalation to the director

> **SUPERSEDED 2026-08-03 — the premise of this section is dead, and the section is kept only so the
> record shows why.** It reads that the BUILD is "category-5 safety-control work, `director_build_open` /
> console-only". Both halves of that are gone. `director_build_open` was **abolished 2026-07-29** and swept
> 2026-08-03 (PROPOSE, RECORD, ACT — "there is no such thing as a BUILD being opened"). And the reserved
> list is now exactly four items, none of which this is: `CLAUDE.md` states plainly that **"a 'safety
> control' that stops a *simulation* is NOT one of these"**, and the only real-world control left reserved
> is *the agent's own sandbox profile* — which a stop control does not touch, since it **narrows** what this
> machine can do rather than widening it. **The §4 build is therefore drawable now, on the agent's own
> authority, recorded not asked.** It is not built here because this atom is the characterisation; it is
> unblocked, not reserved. Do not re-derive a gate from the paragraph below.

The original text, for the record: *the BUILD of any new or modified stop control is category-5
safety-control work (`CLAUDE.md` PROCEED-BY-DEFAULT one-way-door list, item 5) — `director_build_open` /
console-only, never self-authorised.* This DISCOVER atom performs inventory and characterisation only; it
adds, wires, or modifies no control — that part still holds.

**For the director:** the sketch in §4 is ready to scope as a BUILD atom. Two sub-decisions worth separating:
- (a) whether the director-window-reachable affordance is worth building now given F2's already-logged
  read-only-rendering-vs-acting-window canon conflict (the site would need an authenticated app surface, not a
  static render, to host it) — this is the same conflict already flagged for the whole DO battery, not new to
  this atom;
- (b) whether the narrower, backend-only "kill a live subprocess on command" primitive (§4 point 4) is worth
  building independently of the window question, since it closes the more safety-material half of the residual
  (mid-flight halt) without waiting on the window-architecture decision.

Per the mint's own marker, this DISCOVER half closed 2026-07-28. (The marker flip it asks for is moot —
the block it names was abolished; see the superseding note at the head of this section.)

---

## 6. The audit — this document is falsifiable, 2026-08-03 (L0→L2)

Sections 1–5 are prose, and prose about what can be stopped **decays silently**: a control gets retired, a
cited test gets renamed, a daemon this doc claims to halt goes `retired` in the manifest — and the document
keeps reading as reassurance. The atom's own mint note set the bar in R15's outcome-test form: *"the artefact
must be checkable against the live process set, so a later reader can falsify it by finding a stop it claims
exists that does not."*

`background/stop_control_audit.py` is that checker; `tests/background/test_stop_control_audit.py` (30 tests)
is its R15 proof. Every row of §1 is a machine-readable claim, and **no claim is checked against itself** —
each resolves against a source the registry does not control:

| Claim | Independent oracle | Fires as |
|---|---|---|
| the module implementing the control exists, and still defines its symbols | the real file's real source text | `MODULE_MISSING` / `SYMBOL_MISSING` |
| the durable flag is actually *read* by the modules said to read it | the flag's literal name in each reader's source | `FLAG_UNREFERENCED` / `UNREAD_FLAG` / `READER_MISSING` |
| the "Release tested?" citations are real tests | `def <name>(` in the real test file | `TEST_MISSING` / `TEST_FILE_MISSING` / `UNTESTED_CLAIM` |
| **a control can actually reach what it claims to halt** | `background/process_manifest.yaml`'s declared state | `UNKNOWN_PROCESS` / **`DEAD_TARGET`** |
| §1's table has not grown a row nobody checks | the `\| N \|` rows parsed from this document | `DOC_ROW_UNCHECKED` / `REGISTRY_ROW_UNDOCUMENTED` |
| the **PARTIAL** verdict below still matches reality | verdict re-derived from every live control's `reach` + `mid_flight` | `VERDICT_STALE` |

**It has already fired on real state.** Row 6 above was falsified by this audit on its first run, not by
inspection: the inventory claimed a live director-only halt flag over a daemon the manifest declares
`retired`. That is the `DEAD_TARGET` check, and `test_control_over_a_retired_process_is_a_dead_target`
pins the original claim so it can never be re-asserted silently.

Failure directions, per R15's three killers:
- **FAIL-OPEN** — an empty registry, or one where every row has been quietly reclassified as inert, is a
  `VACUOUS` violation. A population control that passes because the population is empty proves nothing.
- **FAIL-SILENT** — a missing/malformed doc or process manifest, or a doc stating no parseable coverage
  verdict, **raises**. An unavailable check is a failed check; it never returns a pass.
- **TAUTOLOGY** — `test_dead_target_reads_the_manifest_not_the_registry` flips the *manifest* while holding
  the registry fixed and asserts the verdict changes, which a registry-vs-registry check could not do.

**The release side (R11, no orphan transition).** The residual in §3 is now *measured*, not asserted: if
anyone ever builds the §4 control, a live entry with `reach="window"` and `mid_flight=True` makes the derived
verdict **MET**, and this document's `Coverage verdict: PARTIAL` immediately fails the audit as
`VERDICT_STALE`. The doc cannot survive its own gap being closed —
`test_verdict_goes_stale_when_a_window_reachable_midflight_stop_appears` proves it.

Run it: `python3 background/stop_control_audit.py` (exit 0 pass / 1 violations / 2 unavailable).

**What this does NOT do:** it adds, wires, and modifies no stop control. The residual named in §3 — a
director-window-reachable, authenticated, mid-flight stop — is still open, and is now the thing this audit
watches for rather than something a reader has to take on trust.
