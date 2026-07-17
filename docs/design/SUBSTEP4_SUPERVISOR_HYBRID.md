# OPS1 Sub-step 4 — Design: systemd owns lifecycle, our layer owns governance

**Status:** DESIGN (approval-gated; no code until the director approves this).
**Decision (approved 2026-07-17):** HYBRID. systemd is the single lifecycle owner of every
standard daemon; our thin governance layer rides above. No bespoke supervisor is built —
anything bespoke must justify itself *against* systemd, and only the worker-seat and the
governance *policies* clear that bar.

Implements G-L3 (authority + health-gate), G-L4 (single supervisor), G-R1 (fail-closed
recovery) from `OPERATIONAL_LAYER_DESIGN.md` §2.1/§2.5.

---

## 1. The seam (the single line)

| Layer | Owner | Why |
|---|---|---|
| Process lifecycle — start/stop/restart/boot/order/logs | **systemd** (adopt) | prior art; boring standard tool a newcomer reads; proven on file-api |
| The worker **seat** (interactive, tmux, seeded) | **our thin manager** (bespoke-justified) | systemd can't monitor a claude process embedded in a tmux server; interactive TTY isn't a service |
| Governance *policy* — sanctity, seeding-by-id, gated advance, HELD, turn-granting, escalation | **ours** (the IP) | no systemd analog; no prior art |

G-L4 is satisfied by **disjoint** ownership: systemd is the sole lifecycle owner of each
standard daemon; the worker-seat manager is the sole owner of the seat. No process has two
owners — that overlap was the accretion pattern, and it is gone.

---

## 2. Unit set + template

Every daemon with `owner: start_worker.sh` in `process_manifest.yaml` becomes one systemd
`--user` unit. `start_worker.sh`'s tmux launch is **deleted** (no parallel path); the stack
starts via `systemctl --user start` of the enabled units.

**Single source, no drift:** units are **generated from `process_manifest.yaml`** by a committed
generator (`background/generate_units.py`) and the generated `.service` files are committed under
`background/systemd/` — so they are *readable standard systemd* (relatable IP) AND derived from the
one declaration. A test asserts the committed units equal what the generator emits from the manifest
(anti-drift, the sub-step-2/3 pattern). `command` → `ExecStart`; `state` → enable/disable (§4).

**Template (standard daemon):**
```ini
[Unit]
Description=Synthetic Enterprise <name>
After=network.target
# --- G-L3: a crash-loop must go to `failed`, never restart silently forever ---
StartLimitIntervalSec=120
StartLimitBurst=5            # >5 failures in 120s -> unit enters `failed`, systemd stops trying

[Service]
Type=simple
WorkingDirectory=/home/rich/synthetic-enterprise
EnvironmentFile=-/home/rich/.config/synthetic-enterprise/.env.ntfy   # out-of-tree secret (Option-2)
ExecStart=/usr/bin/python3 background/<script>.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```
(`StartLimit*` live in `[Unit]` on current systemd.) EnvironmentFile via `-` prefix = start even if
the secret is absent, rather than crash-loop — the file-api lesson, applied to all. journald gives
logs for free; ExecStart re-reads disk so a restart deploys current code (G-D1-adjacent).

**Retro-fix, from the 32,707 finding:** `file-api.service` currently has `Restart=on-failure` with
**no** StartLimit — which is exactly why it crash-looped 32,707 times silently. Add `StartLimitIntervalSec`
/`StartLimitBurst` to it too. Restart-without-limits is itself a silent-failure mode.

---

## 3. Worker-seat manager + seeding-wrapper contract

The seat is the one thing systemd can't own: an interactive claude inside a tmux server. So a
**thin manager** (`background/worker_seat.py`, itself a systemd unit) owns the seat's liveness —
this is the justified-bespoke piece, and it is *thin*: it seeds and keeps-alive, nothing else.

**Contract (what the manager MUST and MUST NOT do):**
- MUST create-or-resume the tmux `claude` session against the **dedicated `WORKER_SESSION_ID`**
  (`--session-id` first time, `--resume` after) — **never `claude -c`** (the console-latch bug).
- MUST keep it alive: if the seat process dies (crash/usage-limit), re-seed it — bounded by the
  same StartLimit discipline (N re-seeds in a window → stop + ALARM, never infinite).
- MUST NOT auto-advance director-gated work: the resume seed **brings-up-and-reports, then STOPS**
  (G-R4). Advancing is the supervisor's job (governed turn-granting), never the seed's.
- MUST NOT reap anything. The reaper is deleted (§6). systemd/the manager never kill the director's
  console — the console-kill vector is removed by construction, not guarded against.
- Runs under systemd (`worker-seat-manager.service`) so its *own* lifecycle is standard; what it
  manages (the interactive seat) is the bespoke part.

This replaces `session_watchdog.py`, slimmed: seeding + keep-alive only. Turn-granting stays in the
supervisor; reaping is gone; usage-limit handling stays (process-level, no pane injection).

---

## 4. HELD ↔ unit mapping

The `process_manifest.yaml` `state` maps directly onto systemd unit state — one declaration, two
readers (the reconcile + systemd):

| state | systemd | reconcile expectation |
|---|---|---|
| **enabled** | `enable` + `start` (boot-start, running) | active → OK; inactive → **MISSING** (fault) |
| **held** | `disable` + `stop` (declared down, reason in manifest) | inactive → HELD (silent); active → **HELD_VIOLATED** (fault) |
| **dark** | installed, `disable` + `stop` (started only when the director sets its flag) | inactive → DARK; active → DARK_ACTIVE (report) |
| **retired** | no unit | any unit present → **UNDECLARED_UNIT** |

The reconcile stops reading tmux panes and reads **systemd unit state** (`is-active`/`is-enabled`/
`SubState`) — absorbing `process_reconciler`'s tmux-pane detection into systemd (the old path is
deleted). `health_check.EXPECTED_PANES` → derives from enabled units' expected `active` state.

---

## 5. G-L3 made real: crash-loops become visible, never silent

Two mechanisms, both from the file-api finding:
1. **Unit config:** `StartLimitBurst`/`StartLimitIntervalSec` on every unit → a crash-loop enters
   `failed` after the burst, instead of retrying forever. systemd's own fail-closed.
2. **Reconcile ALARMS on failure states:** the reconciler adds `UNIT_FAILED` (SubState=`failed`) and
   `UNIT_CRASHLOOPING` (`activating (auto-restart)` seen across two samples) as **alarm** statuses.
   A silent systemd crash-loop is the same disease as the invisible cron — so it is now detectable
   by the same reconcile, forever. (Had this existed, file-api would have alarmed at failure #5, not
   looped 32,707 times.)

---

## 6. Marker re-scope (director-ruled): delete the reaper, keep the contract + invariant

- **DELETE the reaper** entirely: `session_watchdog.reap_orphan_interactive_claude` and its call in
  the restart path. No parallel path — systemd + the thin manager have no kill-the-duplicate logic,
  so exit-143 is impossible by construction, not by inference.
- **RE-SCOPE `console_sanctity`, do NOT orphan it.** A consumer-less mechanism is accretion-in-waiting;
  but the exit-143 *class* recurs (future cleanup scripts, resource guards, agent kill-tools). So
  `console_sanctity.is_sanctified()` becomes the **standing kill-path contract**: recorded as a
  **design law — "every process-kill path MUST consult sanctity before killing"** — enforced at each
  future kill-path's review, so the next one is *born safe*, not born-dangerous-then-patched.
- **KEEP the mutation test** as the permanent invariant of the exit-143 class (incident-stays-tested),
  even though its current consumer is gone — it guards the contract.
- **Honest demotion:** the marker is now **belt-and-suspenders contract, not load-bearing defense**.
  The load-bearing fix is the reaper's *absence*.
- *Considered outright deletion (director offered it):* rejected — deletion lets the next kill-path
  repeat exit-143 (born dangerous), which is the exact accretion cycle the mandate breaks. A standing
  contract + retained invariant is the mechanism that pre-empts it. (If a future review finds no
  kill-path has appeared in, say, an epoch, revisit.)

---

## 7. What gets deleted (no parallel path)

- `session_watchdog.py` → replaced by the thin `worker_seat.py` (seeding + keep-alive); the reaper,
  the tmux-singleton logic, and the spawn-into-`claude`-tmux path are deleted.
- `start_worker.sh`'s daemon-launch loop → replaced by `systemctl --user start` of enabled units
  (install via `install_schedule.sh` extended to the generated unit set).
- `process_reconciler`'s tmux-pane detection → systemd unit-state reads.

---

## 8. Release sequencing (approved) — each its own visible verify, never a batch flip

Design approved (this) → build units + `worker_seat.py` + reconcile changes → exit-test → **then
re-enable the held layer one unit at a time:**
1. **worker-seat** (`worker-seat-manager.service` + seat) → verify **seeding-by-id live** (process
   carries `--session-id`, not `-c`), and **reaper confirmed retired** (console sanctity now
   structural-by-absence: no kill-path exists to spare it from).
2. **supervisor** unit → verify **turn-granting** to the seat works under the new model.
3. **deadmans** unit **last** → against a **fresh commit clock**.

---

## 9. Exit test for the BUILD (what will prove sub-step 4)

- Units generated from the manifest == committed units (anti-drift test).
- HELD↔unit mapping mutation-tested: enabled-down → MISSING; held-up → HELD_VIOLATED; dark; retired.
- **G-L3:** a unit forced to fail >burst enters `failed`; reconcile ALARMS `UNIT_FAILED`/`UNIT_CRASHLOOPING` (the 32,707 case, now caught).
- Reaper gone: grep proves no `os.kill`/reap of interactive claude anywhere; the exit-143 mutation
  test still passes against `console_sanctity` (invariant survives).
- Live: worker-seat seeded-by-id, supervisor grants a turn, deadmans sees a fresh clock — verified
  one at a time.

---

## 10. Open questions for the director (before build)

1. **Boot-start policy:** should the *enabled* daemons auto-start on reboot (units `enable`d), or
   only file-api + the manager, with the autonomy layer started deliberately by you? (I lean:
   enabled = boot-start; HELD = not; you control autonomy by the manifest state, not by boot.)
2. **Generator vs hand-written units:** I propose generate-from-manifest + commit the output (DRY +
   readable + no drift). Confirm you'd rather that than 13 hand-written unit files.
3. **Worker-seat manager as a unit** is the one bespoke process. Confirm that's the right boundary
   (vs. trying to make systemd own the interactive seat, which I believe it can't do cleanly).
