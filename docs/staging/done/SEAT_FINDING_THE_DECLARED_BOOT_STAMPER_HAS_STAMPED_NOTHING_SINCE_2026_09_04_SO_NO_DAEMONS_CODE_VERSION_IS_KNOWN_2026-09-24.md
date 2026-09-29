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

## ADDENDUM, measured after the landing: the repair is itself inert, by the mechanism it describes

The landing (`7c77466ce`) is on `origin/main`. **The shared tree's checkout does not contain it**,
so `background/boot_sha.py` on the box that actually runs the daemons still has no `__main__`, and
running the declared `ExecStartPre` there still writes nothing. Restarting every daemon right now
would repair nothing.

Measured over ~400s, spanning two `reconcile-watch` cycles (the timer is every 5 minutes):

| | at 03:57Z | after ~400s |
|---|---|---|
| shared tree HEAD | `1b1e820cb` | `b26362f94` (advanced — other lanes' own commits) |
| behind `origin/main` | 5 | **5** |
| contains `7c77466ce` | no | **no** |

The checkout moved forward the whole time and never merged `origin/main`. This is the shape
already recorded twice in this seat's memory — `reconcile-watch` exits `success` without advancing
the shared tree, so its exit code is not evidence; `git merge-base --is-ancestor` is.

**This is the same defect class as the finding above, one layer out.** The boot stamper was dead
because a declaration (`ExecStartPre=…`) was believed instead of its effect. The reconciler is
believed the same way: it reports success, and nothing asks whether the checkout actually contains
what was promoted. A daemon's running code version has *two* gaps between it and a landed commit —
the restart (which this landing now measures) and the checkout (which nothing measures). Fixing
only the first still leaves the commit inert.

Not repaired from this turn on purpose: advancing the shared tree is a write to the shared tree,
and this turn's isolation is the reason it was allowed to run. Handed on instead.

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

  > **WRONG, and corrected beside the claim rather than revised away (2026-09-24, the successor
  > turn).** `restart_plan` already holds it. `unresolved` is tested BEFORE `stale`, and the
  > fourth rule routes its verdict through `unresolved`, so this landing discharged its own owed
  > item and I did not notice. Measured by running the function over a four-row report:
  > `stamp-predates-process` → HOLD, `unstamped` → HOLD, honestly-stale → RESTART. No change was
  > needed and none was made. What WAS missing is that nothing pinned it — the correct behaviour
  > rested on the order of two branches. That control now exists. See
  > `records/SEAT_RESULT_THE_CHECKOUT_GAP_IS_MEASURED_AND_A_RESTART_WOULD_HAVE_HIDDEN_IT_2026-09-24.md`.

## ADDENDUM 2, the successor turn: the restart this finding asks for would HIDE the gap

The bullet above says the stamps "stay stale until each daemon's next restart" and treats that
restart as the remedy. **Measured 2026-09-24 and it is the wrong way round.** Restarting re-runs
`ExecStartPre` against a checkout that still has no `__main__` in `boot_sha.py`, so it delivers
nothing — and to the extent it stamps at all it moves each stamp to the shared HEAD, which is the
state in which **17 of the 28 paths `origin/main` has and the checkout lacks go INVISIBLE** to
`changed_paths_since` (11 are invisible today; the sets differ because visibility is decided by
stamp age and working-tree dirt, neither of which is about the gap).

So a mass restart would clear all eleven `stamp-predates-process` verdicts and deliver not one line
of the repair. **A restart closes gap 2 and blinds the detector to gap 1 in the same act.** The
restart is correct only after the checkout advances. `deploy_restart.checkout_drift` now measures
that ordering and the report says it out loud.

## ADDENDUM 3, the scheduled worker (2026-09-24 18:10): the command stamps; the reason no stamp has moved is a POPULATION DISJUNCTION, and the "Unresolved" section above is now resolved BY THE STAMPS THEMSELVES

Asked one variable at a time, on the shared tree, without restarting any daemon.

**Premise re-measured first, and ADDENDUM 2's is SPENT.** `ec1012c01` is an ancestor of
`origin/main`, *and* the checkout now carries it: `git hash-object background/boot_sha.py`,
`HEAD:background/boot_sha.py` and `ec1012c01:background/boot_sha.py` are all
`5ee6e0728`. ADDENDUM 2 said "a restart re-runs `ExecStartPre` against a checkout that still has no
`__main__`". That is no longer true, so the ordering it demanded is satisfied and a restart is now
the correct act rather than a blinding one.

**1. The declared command works, in both arms.** The installed units match the declaration —
all 12 `~/.config/systemd/user/*.service` copies that carry it read
`ExecStartPre=-/usr/bin/python3 -m background.boot_sha <session>`, exactly
`generate_units.py:53`, and `NeedDaemonReload=no`.

| arm | how | exit | wrote |
|---|---|---|---|
| bare shell | `SE_BOOT_DIR=$T /usr/bin/python3 -m background.boot_sha sanity-daemon` | 0 | stamp, `sha=ffa14f065`, 435 dirty blobs |
| under systemd's own environment | `systemd-run --user --wait --working-directory=/home/rich/synthetic-enterprise --setenv=SE_BOOT_DIR=$T …` | 0 | stamp, `sha=ffa14f065`, 435 dirty blobs |

The second arm is the one that mattered: it rules out "it works in a shell and something about
systemd's environment (no `HOME`, a refusing seat guard) swallows it". It does not. Both arms wrote
to an isolated `SE_BOOT_DIR`; no real state was touched and no daemon was restarted.

**2. It ran at today's restarts and wrote nothing, and systemd records that it ran.**
`systemctl --user show sanity-daemon -p ExecStartPre` reports
`start_time=[Thu 2026-09-24 07:10:33 BST] … code=exited ; status=0`. The cause is not the `-`
prefix swallowing a failure — there was no failure. **The working copy did not yet carry the
restored block:** `background/boot_sha.py` has mtime `2026-09-24 07:17:51`, **7m18s after** the
07:10:33 start. The daemons restarted into the no-op version, seven minutes before the repair
reached the disk they read.

**3. THE LIVE REASON, and it is not a defect in `boot_sha` at all.** Census of all 24 installed
units, `ExecMainStartTimestamp` against the 07:17:51 fix:

- **12 units carry the stamper.** The newest start among them is **07:10:34** — *not one has
  started since the repair reached the disk*. (`token-proxy` 09-15, `worker-seat-manager` 09-17,
  the other ten 09-24 07:00–07:10.)
- **7 units started this evening** — `deploy-restart` 18:01, `bill-validation` 18:04,
  `edge-traffic-capture` 18:04, `reconcile-watch` 18:05, `seat-executor` 18:06, `worker-tick`
  18:07, `delivery-seat` 15:21 — and **not one of them carries an `ExecStartPre` stamp line.**

So the item's "daemons have restarted many times since" is **true of the box and false of the
stamped population**. The two sets are disjoint: the units that stamp are long-lived daemons that
restart rarely, and the units that restart constantly are short jobs that do not stamp. A signal
that can only refresh on a restart, over a population that almost never restarts, goes dark by
construction — and `deploy_restart.restart_plan` correctly HOLDs on `stamp-predates-process`
rather than restarting, so **nothing in the system will ever restart these 12 on account of this
signal.** That is the standing mechanism, and it outlives today's seven-minute miss.

**4. RESOLVED — what wrote the 2026-09-15/17/18 stamps.** The section above records "I could not
establish what wrote them". The stamps answer it themselves, because a stamp records a content hash
for every file dirty at boot, including its own source. In `staging-watcher.json` (09-17),
`supervisor.json` (09-18) and `token-proxy.json` (09-15), `dirty_blobs["background/boot_sha.py"]`
is `56648a39ac60d2664943bf9f40698866aa48b30d` in all three. That blob:

- is in **no commit** — `git log --all --find-object=56648a39a` is empty;
- contains **both** `def dirty_blobs` (added by `3ecf355d8`, 2026-09-04) **and** the `__main__`
  block (deleted by `3ecf355d8`, the same commit).

A working-copy-only hybrid. **The stamper did not die on 2026-09-04 when HEAD lost the block — it
kept running for two more weeks off an uncommitted copy that still had it, and stopped when the
CHECKOUT was refreshed to HEAD, some time after 2026-09-18 03:19:46.** So this finding's own
headline is wrong and is corrected here rather than revised away: not *"stamped nothing since
2026-09-04"* but *"stamped until 2026-09-18 03:19:46 off a copy in no commit, then nothing"*. The
deployment was tracking a dirty working copy rather than HEAD, and that was invisible because the
only evidence of it was inside the artefact the mechanism itself writes.

**5. Latent, one line, not repaired here.** `docs/observability/.daemon_boot/--report.json`
(2026-08-14) is a stamp whose session name is `--report`: `stamp(sys.argv[1])` takes any argv
without validation, so a caller passing a flag mints a junk session that then sits in the boot
directory looking like a daemon.

### Owed, and pre-registered so the next turn can refute it

The item's "DONE when a stamp file's mtime moves on a real daemon start" is **not discharged**, and
deliberately: the item forbids restarting a daemon to test it, and no stamper-carrying unit has
started naturally since 07:17:51. Prediction, written before the answer is known: **the next start
of any of those 12 units will write `<session>.json` with `ts` ≈ that start and `sha` = the
checkout's HEAD at that moment**, with a `dirty_blobs` map of a few hundred entries. If a stamp
mtime does not move on the next such start, arm 2 above is refuted and the cause is somewhere this
turn did not look. Checking it costs one `stat`.

## ADDENDUM 4, the scheduled worker (2026-09-24, later): arm 2 checked FIRST and still UNTESTED; the `-` STAYS and the absence is now reported

**The pre-registered check, run before anything was built, because it costs one `stat`.**
ADDENDUM 3 predicted: *the next start of any of those 12 stamper-carrying units writes
`<session>.json` with `ts` ≈ that start.* Measured now:

- No stamp mtime has moved. Newest is `supervisor.json` at 2026-09-18 03:19:46.
- **No stamper-carrying unit has started since the fix reached disk at 07:17:51.** Newest start
  among the 12 is `sim-runner`/`staging-watcher`/`supervisor` at 07:10:34.

So the prediction is **neither confirmed nor refuted — it is still untested**, and recorded as
untested rather than quietly dropped. The population disjunction of ADDENDUM 3 §3 is exactly why:
the prediction can only be settled by an event that does not happen. That is the finding, not an
obstacle to it.

Two rows are *corroborating* evidence, noticed while doing the `stat` and not predicted: for the
only two units whose last start predates the 2026-09-04 deletion window's end, the stamp mtime
equals `ExecMainStartTimestamp` **to the second** — `token-proxy` 09-15 13:47:55 / 09-15 13:47:55,
`worker-seat-manager` 09-17 10:27:45 / 09-17 10:27:45. The stamper did write at those starts,
which is ADDENDUM 3 §4's "it kept running off an uncommitted copy" seen from a second angle.

### The `-` decision, settled by measurement rather than argument

Ran `3ecf355d8:background/boot_sha.py` — the `__main__`-less blob — exactly as the unit declares
it, into an isolated `SE_BOOT_DIR`: **exit 0, zero files written.**

`ExecStartPre=` without the `-` promotes only a NON-ZERO exit into a start failure. There was no
non-zero exit at any point in the twenty days. **So removing the `-` would not have caught one
minute of this defect** — and it would convert any future stamper fault into twelve daemons that
refuse to boot, trading an observability gap for an outage while still missing this one. The `-`
stays. The generated unit's comment already says why it is there and remains correct.

### What landed instead: `probe_declared_stamper`, which needs no restart

`background/process_reconciler.py` — reads the **installed** units under
`~/.config/systemd/user/`, parses the stamp argv **out of the unit text** (systemd's `-@+!:`
prefixes stripped), collapses the 12 spellings to the 1 distinct shape, and **runs it** against a
throwaway `SE_BOOT_DIR`. The oracle is *a file appearing*, never the exit status — grading the
exit status is precisely what was green for twenty days.

Verdicts, one per remedy: `works` · `silent` (exit 0, wrote nothing — **the defect that had no
name**) · `failed` · `sha-unknown` · `unreadable` · `unprobed` · `undeclared`. `ok` is derived
from `works` alone, so a verdict added later is not-ok **by construction** rather than fail-open
until someone remembers to extend a list.

Why the *installed* side and not the generated text: the commit gate already proves the generated
unit stamps, and it still could not see 2026-09-24, when the repair was at HEAD and the daemons
restarted **7m18s before it reached the disk they read**. Installed-vs-repo is the only side that
drifts without a commit.

**Why a probe rather than another stamp rule.** `stamp-predates-process` can only tell a dead
stamper from a live one *at a restart*, and ADDENDUM 3 §3 established that the stamping population
and the restarting population are disjoint. `restart_plan` correctly HOLDs on
`stamp-predates-process`, so nothing will ever restart those 12 on its account. A probe runs on
its caller's cadence and would have gone red on 2026-09-04, the day of the regression.

`background/health_check.py` — the verdict reaches `run_health_check` as a **problem line**, not a
footnote, and says the thing that matters: *every staleness verdict above is derived from stamps
nothing is writing*. Guarded with `"stamper" in _bd`, not truthiness, so a caller passing an older
report is silent rather than read as a PASS.

### Demonstrated, not argued — both arms, live

| arm | probe | health surface |
|---|---|---|
| real installed units, real stamper | `works`, 12 declaring units, 1 probe, `stamped … at 430e5b00e` | `✓ … the declared boot stamper stamps` |
| units declaring the `3ecf355d8` no-op blob | **`silent`**, `exited 0 and wrote no boot record` | **`✗ deployment drift: THE BOOT STAMPER THE UNITS DECLARE DOES NOT STAMP (silent)`** |

**Mutation-proven** (39 green unmutated; each mutation reds the test written for it):

| mutation | result |
|---|---|
| `ok` unconditionally `True` (fail-open) | 3 failed, incl. the named `…_is_named_silent` |
| grade the exit code, not the written file (the historical blindness) | 4 failed, incl. the named one |
| verdict unconditionally `silent` (the guard that refuses EVERYTHING) | 3 failed, incl. the live arm |
| delete the health_check surfacing | 1 failed — the surface control |
| warn unconditionally (anti-tautology arm) | 1 failed — same control, opposite leg |
| truthiness instead of `"stamper" in` (legacy report reads as a fault) | 1 failed — same control, third leg |

### Still owed, and narrowed

- Arm 2 remains open and now has a cheaper settlement: the probe answers *"is the stamper alive"*
  without waiting for it. What a natural restart would still settle is whether `ExecStartPre`
  fires at all under systemd for these units — a strictly smaller question.
- The 11 `stamp-predates-process` verdicts stand until those units next restart. Honest, not
  wrong, and ADDENDUM 2's ordering constraint is spent (§ADDENDUM 3), so a restart is now correct.
- ~~**Not repaired, still one line:** `docs/observability/.daemon_boot/--report.json`.~~
  **REPAIRED in the follow-on commit, and corrected here beside the claim rather than revised
  away.** `boot_sha.is_session_name()` + a NAMED refusal at the entrypoint: a flag or a path
  reaching argv now exits 2 saying *"refusing to stamp '--report' -- not a session name (a flag or
  path reached argv where a unit name was meant)"* and writes nothing, while `sanity-daemon` and
  the no-argv `unknown` fallback still stamp. Demonstrated per-arm in fresh directories, because
  the first run of the demo counted a file the PREVIOUS arm had written and read as though the
  refusal had stamped. Still non-blocking: the unit's leading `-` means a refusal never stops a
  daemon booting. Mutation-proven — accept-everything reds 2, refuse-everything reds 4, and
  **making the entrypoint stop consulting the guard reds the entrypoint arm specifically**, which
  is the correct-but-uncalled shape that let `stamp()` sit with zero production callers for twenty
  days.
- The junk stamp `--report.json` and the retired `discovery-daemon.json` are still ON DISK; the
  guard stops new ones, it does not sweep old ones. Censused while here: of the 12 units declaring
  the stamper, `executor-daemon` has never stamped (it has never started), and 2 stamp files
  belong to no declaring unit.
- The ruff frozen census reds in this shared worktree (`{'I001': 1304} != 1306`) from another
  lane's uncommitted work; my three files emit zero `I001` at HEAD and on disk alike. Already
  filed as `WORKER_FINDING_THE_RUFF_CENSUS_REDS_IN_THE_SHARED_WORKTREE_AND_IS_CLEAN_AT_HEAD_2026-09-24.md`.
