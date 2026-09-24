**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The declared boot stamper has stamped nothing since 2026-09-04, so no daemon's running code version is known — and the drift detector read the twenty-day-old stamps as valid

Claim id: `a-landed-change-inside-a-running-daemon-is-inert-until-restart-and-nothing-measures-the-gap`.
Pre-registration: `docs/staging/records/PREREG_HOW_MANY_DAEMONS_ARE_STALE_VERSUS_NEVER_STAMPED_2026-09-24.md`.

## The premise was NOT spent

The draw flagged `465a0dfca` as already an ancestor of `origin/main`. It is — but that commit is
the *evidence* this item cites, not its deliverable. The item asks for a mechanism relating a
landed commit to the code a running daemon actually holds. That mechanism was not built. The
duplicate live claim is this very id (the seat's own), so there was nothing to release.

## What the item asked for already existed, and had been dead for twenty days

The item proposed "each daemon recording the git sha it booted at, and one control asking whether
any live daemon's boot sha predates the newest commit touching its own source." That is
`background/boot_sha.py` + `process_reconciler.evaluate_boot_sha_drift`, built 2026-07-17 and
rebuilt 2026-08-09. Looking for the parked atom found it. It was not working.

**Measured, in this order:**

1. `background/boot_sha.py` had **no `__main__` block**. Every generated unit declares
   `ExecStartPre=-/usr/bin/python3 -m background.boot_sha <session>`
   (`background/generate_units.py:53`) — ten units in the repo, ten installed copies under
   `~/.config/systemd/user/`.
2. Running that exact declared command on the shared tree **exited 0 and wrote nothing**.
   `docs/observability/.daemon_boot/staging-watcher.json` kept its mtime of 2026-09-17 10:27:42.
3. The block was deleted by **`3ecf355d8`** (2026-09-04) while fixing an unrelated `dirty_blobs`
   defect. `boot_sha.stamp()` was left with **zero production callers**; its only callers were
   tests, all of which monkeypatch `BOOT_DIR` — so they proved the function while the invocation
   was dead.
4. systemd started `staging-watcher.service` at 2026-09-24 03:30:22 BST (journal, `NRestarts=0`,
   `ExecMainStartTimestamp`). The stamp still read `2026-09-17T09:27:42Z`. A confirmed systemd
   start did not move it.
5. `evaluate_boot_sha_drift()` reported **9 of 12** daemons `stale`, permanently.

The leading `-` in the unit tells systemd to ignore the result, so the failure was silent by
design. Nothing else could notice: the only checks that existed
(`test_generated_units_stamp_boot_sha_before_execstart`) asked whether the *declaration* was
present and correctly ordered — and the declaration is exactly what had not broken.

## Why this made the 2h48m window invisible, which is the item's actual subject

`465a0dfca` landed `reask()` into `staging_watcher` at 2026-09-23 23:12:02Z; the running watcher
applied it at 2026-09-24 02:00:23Z when something restarted it. Nothing could see the gap because
`staging-watcher` read **`stale` on both sides of the restart** — its stamp was from 2026-09-17,
and a stamp that old makes `changed_paths_since` report the daemon's own source as changed
whatever it is actually running. The state did not transition, so there was no event.

This is the **ALWAYS-RED** failure that the 2026-08-09 rebuild (`55899dc99`) was explicitly written
to abolish: *"a detector for that failure mode that is always red will be ignored exactly as
reliably as one that is blind."* It regressed three weeks later, from a commit about something
else, and stayed red for twenty days.

`loaded_code_drift`'s three fail-safe rules could not cover it. `unstamped` asks whether a stamp
EXISTS. **Nothing asked whether the stamp describes the process running now** — and "the code moved
under a running daemon" and "nothing stamped this boot" have opposite remedies (restart it / repair
the stamper) behind one indistinguishable verdict. `deploy_restart` was acting on the first reading
while the second was true.

## The prediction, and how it was wrong

Pre-registered: of the 9 sessions reported `stale`, **9 of 9** flip to `stamp-predates-process`,
0 remain honestly stale.

Measured: **11 of 11**. The prediction was right about the nine and **under-scoped** — the
condition covers the entire running population, including `token-proxy` and `worker-seat-manager`,
which the old detector reported **green**. Those two were falsely green: their stamps predate their
processes too, and they read clean only because the diff from their stale boot sha happened not to
intersect their closure. Not one daemon on this box has a stamp describing its current process.

| session | stamp | process start | predates |
|---|---|---|---|
| background-worker | 09-18 02:19:39Z | 09-24 02:40:25Z | yes |
| deadmans-switch | 09-18 02:19:40Z | 09-24 02:40:25Z | yes |
| dispatcher | 09-17 09:27:35Z | 09-24 02:40:25Z | yes |
| naive-organ | 09-18 02:19:42Z | 09-24 02:40:25Z | yes |
| ntfy-responder | 09-17 09:27:38Z | 09-24 02:40:25Z | yes |
| sanity-daemon | 09-17 09:27:39Z | 09-24 02:40:25Z | yes |
| sim-runner | 09-18 02:19:44Z | 09-24 02:20:24Z | yes |
| staging-watcher | 09-17 09:27:42Z | 09-24 02:40:25Z | yes |
| supervisor | 09-18 02:19:46Z | 09-24 02:40:25Z | yes |
| token-proxy | 09-15 12:47:55Z | 09-16 03:25:11Z | yes (was reported GREEN) |
| worker-seat-manager | 09-17 09:27:45Z | 09-18 00:04:51Z | yes (was reported GREEN) |

## What landed

1. **`background/boot_sha.py`** — `__main__` restored (with the seat guard it had before), so the
   declared `ExecStartPre` stamps again. Verified: the command now writes a record with a real SHA.
   New `read_boot_ts(session)`. `BOOT_DIR` is overridable by `SE_BOOT_DIR` solely so a control can
   run the declared command as a real subprocess without touching real state — nothing in
   production sets it.
2. **`background/process_reconciler.py`** — a fourth fail-safe rule, `stamp-predates-process`, and
   `process_start_time(pid)` reading `/proc/<pid>/stat` field 22 against `/proc/stat` `btime`.
   `boot_ts` and `started_at` are **required keyword arguments**, not optional ones, because a rule
   a caller can forget to feed is a rule that stays green for twenty days. A session with either
   value unknown makes no new claim and falls through — that can never turn a red into a green.
3. **`tests/background/test_boot_sha_deployment.py`** — five controls. The load-bearing one is
   `test_the_units_own_declared_stamp_command_stamps`: it parses the `ExecStartPre` argv **out of
   the generated unit text** rather than retyping it, and runs it as a subprocess against a tmp
   `SE_BOOT_DIR`. Keyed to the property ("whatever the unit declares, stamps"), not to today's
   spelling.

**Mutation-proven, both directions** (31 tests, all green unmutated):

| mutation | result |
|---|---|
| delete `__main__` again, exactly as `3ecf355d8` did | 1 failed — `test_the_units_own_declared_stamp_command_stamps`, and only that one |
| delete the fourth rule | 2 failed — the named replay + the distinctness partition |
| make the fourth rule fire unconditionally (`if True:`) | 9 failed, incl. `..._still_reaches_the_stale_verdict` — the guard-that-refuses-everything shape is caught |

## Unresolved, recorded rather than guessed

The stamps are dated 2026-09-17 and 2026-09-18 and carry the `dirty_blobs` field that `3ecf355d8`
introduced on 2026-09-04 — so they were written by the post-deletion code, which has no entrypoint
and no production caller. **I could not establish what wrote them.** It does not affect the repair
(the repair is that the declared command must stamp, and a control now proves it does), but it
means some route writes boot records that nobody has enumerated.

## What is still owed

- **The stamps on the box are still stale.** The repair only takes effect at each daemon's next
  restart, because that is when `ExecStartPre` runs. Until then all 11 read
  `stamp-predates-process` — which is now the honest verdict rather than a wrong one, but it is not
  yet a working signal. The mass restart that makes it live is a shared-tree operational act and is
  deliberately not being done from this worktree turn.
- **Nothing yet publishes this.** The verdict is computed and readable via `evaluate_boot_sha_drift`
  and consumed by `health_check` and `deploy_restart`; it does not reach a page. The item asked to
  "make the gap readable" and this makes it *answerable and honest* — a surface is the next
  increment.
- `deploy_restart.restart_plan` restarts on `stale` and should learn that
  `stamp-predates-process` is not a restart-able condition — restarting clears it only incidentally
  (by re-running `ExecStartPre`), and it is the second time this project has restarted daemons in a
  loop to clear a condition a restart could not address (`3ecf355d8`'s own subject).
