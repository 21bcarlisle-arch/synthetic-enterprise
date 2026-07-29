# OPS1 — Launcher Cutover Completion (DISCOVER + FRAME)

**Atom:** `OPS1_launcher_cutover_completion` (lane `H_harness`, dial 5, `loop_stage: idle`)
**Lane:** L3 DISCOVERY — doc only. No code changed, no unit touched, no `systemctl` state command run.
**Author:** LANE-3 DISCOVER/FRAME fork, 2026-07-29.
**Parent design:** `docs/design/OPERATIONAL_LAYER_DESIGN.md` (OPS1 sub-step 4), `docs/design/SUBSTEP4_SUPERVISOR_HYBRID.md`, `docs/design/OPS1_DEPLOY_RUNBOOK.md`.
**Ruling this obeys:** one-at-a-time cutover with a verify between (director-ruled 2026-07-17, recorded in `background/process_manifest.yaml`'s `launched_by` header and `process_reconciler.startlist()`'s docstring).

---

## 0. Purpose, guarantee, why — stated BEFORE the mechanism (DON'T ACCRETE)

**Purpose.** Finish the tmux→systemd migration so that **every declared daemon has exactly one
launcher**, and so that the repo alone — not an accident of which units happen to be inactive —
is what makes that true.

**Guarantee sought (the invariant, §2).** For every declared daemon: the number of *armed*
launchers is exactly one, where "armed" counts a launcher that *would* start it, not only one
that *has* started it.

**Why this is one system and not seven patches.** The seven daemons are not seven bugs. They are
one defect with seven instances: the repo carries **two derivations of the same fact** — "who
launches this daemon" — and they disagree.

- `process_reconciler.startlist()` derives the tmux launch set from **`launched_by`**.
- `install_schedule.sh` derives systemd **boot-start arming** from **`state`** alone
  (`background/install_schedule.sh:53`: `if [ "$state" = "enabled" ]`), ignoring `launched_by`.

So `bash background/install_schedule.sh` on a clean checkout arms a systemd boot-start for all
seven daemons that `start_worker.sh` also tmux-launches. **Reconstruct-from-repo currently
reproduces the defect.** That is the whole finding, and it is why the fix is a single predicate
plus a single guard, applied through seven ordered, individually-verified steps — not seven
one-line manifest edits.

---

## 1. DISCOVER — verified live state (2026-07-29 ~19:50 UTC, this box)

All rows below are from commands run in this pass. Nothing is taken from the atom description.

### Commands used
```
systemctl --user list-unit-files --type=service --no-pager
systemctl --user is-enabled <s> ; systemctl --user is-active <s>
systemctl --user show -p SubState -p MainPID --value <s>
ls -la ~/.config/systemd/user/default.target.wants/
python3 -m background.process_reconciler startlist
tmux ls
ps -eo pid,ppid,lstart,cmd
diff background/systemd/<s>.service ~/.config/systemd/user/<s>.service
```

### The seven — evidence table

`unit file` = present in `~/.config/systemd/user/`. `boot-armed` = symlink present in
`~/.config/systemd/user/default.target.wants/` (this is what makes it start at boot).
`in tmux startlist` = returned by `python3 -m background.process_reconciler startlist`.
`live PIDs` = `ps` rows that actually RUN the daemon (a python interpreter whose argument
basename equals the match token) — deliberately distinguishing RUNNING from MENTIONING, per the
`liveness OR can't count launchers` precedent. My own `grep` invocations appeared in `ps` and were
excluded on exactly that test.

| # | daemon | unit file | `is-enabled` | boot-armed symlink | `is-active` / SubState | in tmux startlist | live PIDs (ppid) | double NOW? |
|---|---|---|---|---|---|---|---|---|
| 1 | background-worker | yes | `enabled` | yes (Jul 20 12:03) | `inactive` / `dead` (MainPID 0) | YES | 1 — 419015 (ppid 886926 = tmux server) | **no** |
| 2 | dispatcher | yes | `enabled` | yes (Jul 20 12:03) | `inactive` / `dead` | YES | 1 — 419024 (ppid 886926) | **no** |
| 3 | discovery-daemon | yes | `enabled` | yes (Jul 20 12:03) | `inactive` / `dead` | YES | 1 — 419027 (ppid 886926) | **no** |
| 4 | sim-runner | yes | `enabled` | yes (Jul 20 12:03) | `inactive` / `dead` | YES | 1 — 419030 (ppid 886926) | **no** |
| 5 | sanity-daemon | yes | `enabled` | yes (Jul 20 12:03) | `inactive` / `dead` | YES | 1 — 419033 (ppid 886926) | **no** |
| 6 | naive-organ | yes | `enabled` | yes (Jul 20 12:03) | `inactive` / `dead` | YES | 1 — 893592 (ppid 886926) | **no** |
| 7 | token-proxy | yes | `enabled` | yes (Jul 20 12:03) | `inactive` / `dead` | YES | 1 — 893599 (ppid 886926) | **no** |

**VERDICT: the seven-daemon claim HOLDS, exactly and without correction.** All seven have a unit
file installed, all seven are `enabled` with a live `default.target.wants` symlink, all seven are
`inactive`, and all seven are still returned by `startlist()`.

**Nothing is double-running right now.** Every one of the seven has exactly one live process and
it is a child of the tmux server (ppid 886926). The five already-migrated daemons
(`supervisor` 2411141, `staging-watcher` 3081438, `ntfy-responder` 480298, `deadmans-switch`
479222, `worker-seat-manager` 2715694) each have exactly one process, all children of ppid 305
(`systemd --user`). `python3 -m background.process_reconciler` therefore reports no
`DOUBLE_LAUNCH` — correctly, today.

### Control rows (checked, not at risk — recorded so the count is honest)

| daemon | unit | `is-enabled` | boot-armed | in startlist | status |
|---|---|---|---|---|---|
| executor-daemon | yes | `disabled` | **no symlink** | YES (state `dark`) | **8th startlist entry, NOT at risk** — unit unarmed, and the daemon is a self-exiting no-op without `.build_executor_enabled`. Must still be flipped for `startlist()` to reach empty, but it cannot double. |
| supervisor / staging-watcher / ntfy-responder / deadmans-switch / worker-seat-manager | yes | `enabled` | yes | no (`launched_by: systemd`) | Cutover COMPLETE. Single launcher confirmed by ppid 305. |

### Committed units vs installed units
`diff background/systemd/<s>.service ~/.config/systemd/user/<s>.service` — **IDENTICAL for all
thirteen**. The unit *contents* are faithfully reconstructed from the repo. It is the
**arming decision**, not the unit text, that the repo gets wrong.

### CORRECTION to the atom's wording (DISCOVER refutes one clause)

The atom says *"each DOUBLES at the next boot."* Precisely, it does not — and the difference
matters for the exit test.

- Nothing on this box runs `start_worker.sh` at boot. `crontab -l` is **empty**; no user or system
  unit has `start_worker` in `ExecStart` (grepped `~/.config/systemd/user/`, `/etc/systemd/system/`,
  `~/.bashrc`, `~/.profile`).
- At boot: the tmux server dies, so the seven tmux copies vanish; systemd starts the seven armed
  units. Result is **one** launcher, not two.
- The double arrives at the **next `start_worker.sh` run after that boot** — because
  `_start_session` skips only on `tmux has-session`, and a systemd-launched daemon holds no tmux
  session, so it starts a second copy. `start_worker.sh` is the documented stack-restart procedure
  (`MAINTENANCE.md`) and was run today at 18:20.
- **A reboot is not even required.** `docs/design/OPS1_DEPLOY_RUNBOOK.md` step 3 literally offers
  `systemctl --user restart <session>.service  # e.g. worker-seat-manager, supervisor,
  deadmans-switch, sim-runner, …` — naming **sim-runner**. Running that line today doubles
  sim-runner immediately, alongside the live tmux copy 419030.

So the exposure is **larger** than "at the next boot", not smaller: it is *boot + any stack
restart*, **or** any single `systemctl --user start` of one of the seven, including one the
project's own runbook suggests. Registered honestly rather than repeating the atom's phrasing.

---

## 2. The invariant, stated precisely

> **SINGLE-LAUNCHER INVARIANT (SL).** For every entry in `background/process_manifest.yaml`
> whose `state` is `enabled` or `dark`, the set of **armed launchers** has cardinality exactly 1.
>
> A launcher is **armed** for daemon *D* iff it would start *D* without further human decision:
> - **systemd is armed for D** iff `D.service` is installed AND boot-start-enabled
>   (`systemctl --user is-enabled D.service == enabled`, i.e. a `default.target.wants` symlink),
>   **or** its unit is currently active.
> - **tmux/start_worker.sh is armed for D** iff `D ∈ process_reconciler.startlist()`.
>
> `retired` entries have cardinality 0. The interactive seat (`match: __worker_seat__`) is
> exempt — it is owned by `worker-seat-manager`, not by a unit.

Three consequences that the current code does not have:

1. **Arming, not running, is the quantity.** The existing `DOUBLE_LAUNCH` status counts
   *running* launchers (`unit_active and tmux_present`). SL counts *armed* ones. Today all seven
   satisfy "running == 1" and violate SL — which is exactly why the reconciler is silent about a
   defect that is fully present.
2. **`launched_by` is the single fact.** Both derivations — the tmux startlist AND the systemd
   enable decision — must read it. Today only one does.
3. **The cutover crosses through DOWN, never through DOUBLE** (§3). Cardinality 0 for a few
   seconds is a loud, harmless transient. Cardinality 2 for a few seconds is the defect itself, and
   for the message-consuming daemons (dispatcher, background-worker, sim-runner) it can execute a
   duplicate act that outlives the window.

---

## 3. The ordered cutover plan

### 3.0 Step ZERO — close the hole before flipping anything (the class fix)

Doing the seven flips without this leaves the repo able to re-arm them on the next
`install_schedule.sh`. Step zero is a prerequisite, not a nicety.

- **Z-a.** `install_schedule.sh` arms boot-start on `state == "enabled"` **and**
  `launched_by == "systemd"`. A daemon still owned by tmux gets `install`-without-`enable` —
  the same treatment `held`/`dark` already get. One predicate, one place, whole class.
- **Z-b.** Add the SL guard as a reconciler status (`LATENT_DOUBLE_LAUNCH`) alongside
  `DOUBLE_LAUNCH`, reading the *arming* side independently (§4).
- **Z-c.** Disarm the seven already-armed units so the machine matches the corrected repo. This is
  the only step that touches live systemd for a daemon that is *not* being cut over in that step,
  and it is strictly safety-increasing: it removes a launcher, never adds one.
  *(Alternative, if disarming seven at once is judged too wide: fold Z-c into each daemon's own
  step as sub-step 1. Slower, strictly one-at-a-time, and I would take this if the director
  prefers literal adherence to the 2026-07-17 ruling. The FRAME states both; the executor picks
  one and records which.)*

**Z exit test:** `install_schedule.sh` re-run on this box changes nothing (idempotent), and no
un-migrated daemon is `is-enabled == enabled`. **Z rollback:** revert the commit;
`systemctl --user enable` restores the prior arming exactly (the units themselves are untouched).

### 3.1 Order of the seven, and why

Ordered by **blast radius of a duplicate act, ascending** — prove the procedure on daemons where a
mistake is cheap, then spend the proven procedure on the ones where it is not. Downtime cost is
near-zero for all seven (each is a poll loop with a period ≥ 30 s), so downtime does not reorder
the list.

| step | daemon | why here |
|---|---|---|
| 1 | **token-proxy** | Safest possible first: a port-bound singleton (`:8801`). A second copy **cannot** silently coexist — it fails to bind and dies loudly. So a procedure defect is discovered as a crash, not as silent duplication. Pure local metering; no external side effect. |
| 2 | **naive-organ** | Timer-driven skeptic writing `naive_organ_log.jsonl`. A duplicate produces duplicate log rows — visible, harmless, non-acting. |
| 3 | **sanity-daemon** | Read-only statistical checks; its only output is an NTFY that already flows through the transition-only `notify.py` contract, so a duplicate is deduped by an existing mechanism. |
| 4 | **discovery-daemon** | 6 h cycle: the longest period, so both the double window and the down window are almost certainly unobserved. Writes research docs, takes no operational action. |
| 5 | **background-worker** | First daemon that **acts**: sweeps leftover `run_complete` markers and spawns `process_run_complete.py`. A duplicate can double-publish. Procedure must be proven by now. |
| 6 | **dispatcher** | Classifies `from_rich_*.md` as URGENT/NORMAL/FYI — **the exact organ whose duplication turned one director NTFY into two queued instructions.** Highest fidelity to the original incident; done with a proven procedure and full attention. |
| 7 | **sim-runner** | Last: largest blast radius in both directions. A duplicate produces two concurrent simulation runs writing competing `run_complete` markers into the publish chain; downtime stops the company's clock. Cut over deliberately, between runs. |
| 8 | *(follow-on)* **executor-daemon** | Not part of the defect (unarmed + dark), but required for `startlist()` to reach empty and `start_worker.sh`'s tmux launch to retire. Do it after the seven, as its own small step. |

### 3.2 The per-daemon procedure (identical for all seven)

**Rule: cross through DOWN, never through DOUBLE.**

1. **Announce + verify precondition.** `python3 -m background.process_reconciler` → 0 alarms.
   `ps` shows exactly one live process for *D*, ppid = tmux server.
2. **Flip the declaration first.** Set `launched_by: systemd` on *D* in
   `background/process_manifest.yaml`, with the dated cutover comment (matching the
   ntfy-responder/staging-watcher precedent already in the file). Commit via `tree_lock`.
   *Declaration leads reality*: from this instant `startlist()` excludes *D*, so a concurrent
   `start_worker.sh` — the resurrection risk — can no longer re-add the tmux copy. Reconcile still
   reads OK here (tmux copy alive).
3. **Kill the tmux launcher.** `tmux kill-session -t <D>`. Reconcile now reads **MISSING** for *D*.
   This is correct and expected: a loud, bounded, seconds-long gap.
4. **Start the systemd launcher.** `systemctl --user start <D>.service`.
5. **Verify (all four must hold before the next daemon is touched):**
   - `ps` shows **exactly one** process running *D*, and its **ppid is 305** (`systemd --user`),
     not the tmux server. Verified by the RUNNING-not-MENTIONING test, never by a bare substring
     `grep`.
   - `systemctl --user is-active <D> == active`, `is-enabled == enabled`, SubState `running`.
   - `tmux ls` has **no** `<D>` session.
   - `python3 -m background.process_reconciler` → **0 alarms**; *D* reads `OK`, no
     `DOUBLE_LAUNCH`, no `LATENT_DOUBLE_LAUNCH`, no `MISSING`.
   - *D*'s own log file advances (it is doing work, not merely up).
6. **R15 evidence for this daemon, both directions** (per the atom's own R15 requirement — a green
   suite is not acceptable, because the suite injects `tmux_running` directly and the live
   PID-aware reader is precisely what the tests missed the first time):
   - **Fires on the defect:** *before* step 3, with the unit started alongside the tmux copy,
     the live reconciler must report `DOUBLE_LAUNCH` for *D*. (Do this deliberately for
     **token-proxy only** — the port-bound one, where a real overlap is self-limiting — and take
     it as the class evidence. For the other six, reproduce the same assertion against injected
     live-reader outputs rather than a real overlap, and say so; manufacturing a real duplicate
     dispatcher to prove a point is the defect, not a test.)
   - **Silent when healthy:** after step 5, no alarm, sustained across two reconcile-watch ticks
     (10 min) — so a control that cries wolf on healthy input is ruled out. This is the shape that
     already false-positived on all five migrated daemons on 2026-07-29.
7. **Wait one reconcile-watch cycle (5 min) before the next daemon.** That is what "verify
   between" means operationally.

### 3.3 Per-step rollback

Every step is reversible in under a minute, and the rollback is the mirror of the step:

| failure at | rollback |
|---|---|
| step 2 (declaration flipped, tmux copy still up) | `git revert` the manifest commit. Nothing about the running world changed. |
| step 3 (killed tmux, unit won't start) | `git revert` the manifest commit, then `bash background/start_worker.sh` — with `launched_by` back to `tmux`, *D* returns to the startlist and is relaunched. Recovery is the ordinary documented procedure, not a bespoke one. |
| step 4/5 (systemd copy misbehaves) | `systemctl --user stop <D>`, `git revert`, `start_worker.sh`. |
| anything, catastrophically | `docs/observability/.stack_disabled` is the durable everything-down escape hatch; it survives a cron tick and a restart. |
| step Z | revert the commit; re-`enable` restores prior arming. Units untouched. |

**No step is a one-way door.** Nothing here spends money, binds anything outside the repo, touches
a real customer, or changes a security posture or what the machine is permitted to do. It changes
*which supervisor* starts a process this repo already starts.

### 3.4 Atom-level exit test (all seven done)

1. `python3 -m background.process_reconciler startlist` returns **only** `executor-daemon`
   (then, after step 8, **empty**).
2. No entry violates SL: no daemon is both boot-armed in systemd and in the startlist —
   asserted by the new independent guard (§4), not by `launched_by` alone.
3. Every one of the seven: exactly one live process, ppid 305.
4. `install_schedule.sh` re-run is a no-op on this box, and on a *fresh* checkout arms exactly the
   `launched_by: systemd` set — i.e. **reconstruct-from-repo no longer reproduces the defect**.
5. `start_worker.sh`'s tmux-launch loop is empty and can be retired with a dated RETIRED banner
   (per `MAINTENANCE.md`'s own convention).

---

## 4. R15 — the guard, and the three shapes it must survive

**The guard.** A new reconciler status `LATENT_DOUBLE_LAUNCH`: daemon *D* is boot-armed in systemd
**and** `D ∈ startlist()`. It is the *arming*-time sibling of the existing run-time
`DOUBLE_LAUNCH`. Without it, the seven-instance defect is fully present and fully silent — which is
today's actual state.

### 4.1 TAUTOLOGY — the checked value must not derive from the source it checks

**There is a live tautology in the existing suite.**
`tests/background/test_process_reconciler.py::test_no_declared_daemon_has_two_launchers_in_the_committed_manifest`
computes `startlist() ∩ {e : launched_by == systemd}` and asserts it is empty. But `startlist()` is
*defined* as excluding `launched_by == systemd`. The intersection is empty **by construction, for
every possible manifest**. The test cannot fail. It is presented as "the declaration-level half" of
the DOUBLE_LAUNCH fix and it is theatre.

**Requirement.** The new guard reads the arming side from a source **independent of
`launched_by`**: the installed unit's boot-start state (`systemctl --user is-enabled`, i.e. the
`default.target.wants` symlink), and/or `install_schedule.sh`'s own enable predicate — never the
manifest field that the tmux side already derives from.

**Mutation test.** Flip `launched_by: systemd` for one daemon in a fixture manifest while leaving
its unit *armed*. The tautological test stays green (proving it is a tautology — assert that
explicitly, so the tautology is pinned rather than quietly deleted). The new guard must go **RED**
with `LATENT_DOUBLE_LAUNCH`. Second mutation, opposite direction: leave `launched_by: tmux` and
*disarm* the unit — guard must be green (fires on the defect only).

### 4.2 FAIL-OPEN — it must not pass on missing / empty / malformed input

The arming reader shells out. Every degenerate return must be treated as **ARMED** (fail-closed),
because "I could not tell whether a second launcher is armed" is not evidence of safety.

**Mutations, each of which must make the guard RED (never green):**

| mutation | why |
|---|---|
| `is-enabled` returns `("", rc=1)` | unknown unit / systemd busy — the default `!= "enabled"` reading would silently mean "not armed". |
| `is-enabled` returns `"Failed to get unit file state for x.service: No such file or directory"` | garbled text; must not be parsed as absence-of-arming. |
| `is-enabled` returns `"\n"` / whitespace | empty read. |
| `is-enabled` returns `"enabled-runtime"` / `"alias"` / `"indirect"` | a non-`enabled` value that still results in boot-start; string-equality against `"enabled"` is too narrow. |
| the manifest is missing a `launched_by` key entirely | must default to `tmux` (armed), matching `startlist()`'s own default — not to "migrated". |
| a daemon has a unit file on disk but no manifest entry | must be reported, not skipped. |

Prior art on this exact box: `schedule_reconciler._process_manifest_unit_names()` wraps its load in
a bare `except Exception: return set()`. That direction happens to be noisy-not-silent, but it is
the same shape and should be checked while the guard is built.

### 4.3 FAIL-SILENT — an unavailable or unreached check is a FAILED check

**Mutations, each of which must make the suite RED:**

| mutation | why |
|---|---|
| `systemctl` binary absent / non-zero on every call | the guard must report `UNKNOWN`-as-armed and alarm, not return "no violations". |
| delete the guard's call from `reconcile()`'s report path | a guard nobody invokes is the file-api-32,707 shape. The test must assert the status appears in a **live** `python3 -m background.process_reconciler` report, not only in a unit-tested pure function. |
| remove `LATENT_DOUBLE_LAUNCH` from `ALARM_STATUSES` | a status that never sets `alarm: True` never pages and never reaches `reconcile-watch`'s NTFY. |
| run the guard's test module under the publish gate's selector | **already-present risk:** that module carries `pytestmark = pytest.mark.operational`, and the publish gate runs `-m 'not operational'`. The guard must additionally execute in a lane that actually runs it — the 5-minute `reconcile-watch.timer`, whose armed-ness is itself declared in `schedule_manifest.yaml`. Assert both. |
| replace `boot_announce`'s reconcile with a stub | the boot-time report is the one that would have caught the arming before a `start_worker.sh` run. |

**Also, a brittleness note, not a shape:** the existing
`test_live_readers_cannot_exclude_a_migrated_daemon_from_double_detection` asserts on
`inspect.getsource(...)` **string literals**. It is genuinely non-tautological and it does pin a
real regression, but a behaviour-level assertion (inject a half-migrated daemon, assert both live
readers see it) would survive a rename. Prefer behaviour for the new guard; keep the source-string
test as a belt if desired.

---

## 5. IaC gap list — what is behaviour-determining and NOT declared in the readable repo

IaC is OPS1's core: reconstruct-from-repo-alone is the test. Ranked by severity.

1. **[BLOCKING — this atom's root cause] Boot-start arming of the seven is machine state that the
   repo derives from the WRONG predicate, and that NO reconciler checks.**
   `install_schedule.sh:53` arms on `state` alone. `process_reconciler` reads unit `active`, never
   `enabled`. `schedule_reconciler` *does* read `enabled` — but only for `schedule_manifest.yaml`
   units (file-api, boot-announce, reconcile-watch, worker-tick); it touches process-manifest units
   solely via `_process_manifest_unit_names()` to *suppress* `UNDECLARED_UNIT`. Net effect: the
   seven `default.target.wants/*.service` symlinks (created 2026-07-20 12:03) are
   behaviour-determining state that nothing in the repo declares and nothing reconciles.
   **Reconstructing from the repo today reproduces the defect.** Closed by §3.0 Z-a + Z-b.

2. **`/etc/systemd/system/claude-tmux.service` — hand-installed, root-owned, undeclared, invisible
   to every reconciler.** Installed 2026-06-11; `enabled`, `WantedBy=multi-user.target`;
   `ExecStart=/usr/bin/tmux new-session -d -s claude '.../claude --dangerously-skip-permissions'`.
   The `claude` session it creates is *declared in `process_manifest.yaml`* as owned by
   `worker-seat-manager` — so **two mechanisms are armed to create the worker seat**, one of which
   the repo has never heard of. `schedule_reconciler._installed_se_units()` globs
   `~/.config/systemd/user/*.service` only, so a *system*-level unit can never be flagged
   `UNDECLARED_UNIT`. This is the same class as the invisible cron the blackout came from, one
   directory up.
   **Out of scope for this atom** (it is the seat, not the seven; and it involves a root-owned
   file, i.e. platform administration) — **REGISTER as a sibling atom** with two parts: (a) widen
   the undeclared-unit scan to `/etc/systemd/system` so system-level SE units are visible at all;
   (b) decide the seat's single launcher and declare it. Part (b) may be director-reserved.

3. **`start_worker.sh`'s retirement is undeclared.** The manifest header states that when the last
   daemon flips, "start_worker's tmux-launch is empty and retired" — but nothing asserts it, and
   the script's launch loop over an empty startlist is a silent no-op rather than a stated end
   state. Add the assertion as part of the atom exit test (§3.4.5).

4. **The `state`↔`launched_by` relationship is undocumented in the manifest schema.**
   `_validate()` enforces `reason`+`flip` for non-`enabled` states but knows nothing of
   `launched_by`: an entry with `launched_by: systemd` and no installed unit, or a typo like
   `launched_by: systemD`, loads cleanly and silently means "still tmux". Add `launched_by` to the
   loader's validation (`∈ {tmux, systemd}`) — cheap, and it removes a silent-typo path into the
   exact defect this atom exists to close.

5. **Minor, for completeness:** `install_schedule.sh` says it "deliberately does not start
   anything — starting is the gated migration" and the runbook repeats "install+enable is inert
   until `systemctl start`/boot". **The `/boot` clause is false.** `enable` at boot *is* the start.
   Fix the comment with the predicate — a doc that misstates the guarantee is how this survived
   nine days.

---

## 6. Level proposed

**0 → 1.** DISCOVER done against live state (the seven-row table is verified, not asserted), the
root cause is located to one line, the invariant is stated, the whole cutover is designed with
order/exit-test/rollback, and the R15 guard is specified including a live tautology found in the
existing suite. **No code is written and nothing is deployed**, so level 2 would be dishonest —
this atom's value is entirely in the seven flips actually landing.

**Ready for BUILD-open.** `file_scope` should widen from `[background/process_manifest.yaml]` to
`[background/process_manifest.yaml, background/install_schedule.sh, background/process_reconciler.py,
tests/background/test_process_reconciler.py]` — the §3.0 class fix and the §4 guard cannot be built
inside the manifest alone.
