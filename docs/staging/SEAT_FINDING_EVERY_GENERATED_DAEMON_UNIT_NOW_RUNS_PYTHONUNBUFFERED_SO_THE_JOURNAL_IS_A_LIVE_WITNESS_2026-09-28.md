**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Every generated daemon unit now runs PYTHONUNBUFFERED=1, so the journal is a live witness once each daemon restarts

**2026-09-28.** Lane-0 item `daemon-stdout-line-buffered-fleet-wide`. The duplicate-work note named
this same id in `.seat_work_in_hand.json`. That was the draw's own write, not a rival, so I did the
work rather than disposing of the item.

**Done:** `background/generate_units.py` emits `Environment=PYTHONUNBUFFERED=1` in every unit, and
all 11 committed units under `background/systemd/` are regenerated from it. The control is
`test_every_unit_makes_its_daemons_stdout_reach_the_journal_live`. It went red when the generator
line was removed and green when it was restored.

**Measured before building:** I predicted 40/40. Under `systemd-run --user -p
Environment=PYTHONUNBUFFERED=1`, 40 × 610 B unflushed prints reached the journal while the process
was still alive: 41 lines matched. The earlier probe (finding `..._STDOUT_BUFFER_IS_128_KIB_...`)
got 0 without the setting.

**Not yet live:** this lands the declaration and the committed units only. Two steps remain:

1. Copy the units to `~/.config/systemd/user/` (`install_schedule.sh` does this) and run
   `systemctl --user daemon-reload`.
2. Restart each daemon. The environment is read only at exec.

Until both are done, every `log_silence` row that reads "unflushed stdout" in
`background/process_manifest.yaml` is still true. Those rows should be re-read after the restart,
not before.

**Re-read, 2026-09-28 19:40Z** (item `manifest-log-silence-rows-reread-after-unbuffered`). I read
each unit's MainPID environ, and counted journal lines by `_PID`:

| daemon | environ has it | own journal lines this run |
|---|---|---|
| supervisor, deadmans-switch, staging-watcher, naive-organ, sanity-daemon, background-worker, sim-runner | yes | 988 / 26 / 80 / 1 / 5 / 5 / 2 |
| dispatcher (up since 09-27), ntfy-responder (up since 09-25), worker-seat-manager (up since 09-27) | no | 0 |

**Why stale rows are worse than misleading.** The brief moves a mute daemon that has a
`log_silence` cause out of its actionable list. So a row still reading "unflushed stdout" would
have filed the next real silence as already explained. I deleted the rows for the five daemons
that now speak: supervisor, deadmans-switch, naive-organ, sanity-daemon and background-worker.

I rewrote the other three:

- **worker-seat-manager** is still mute by construction, and the setting cannot change that.
- **dispatcher** still has nothing to classify. Its cause does not depend on buffering, and its
  row now says what would count as a real fault.
- **ntfy-responder**'s row now says it expires at the next restart.

After the change, `declared_daemon_health` reads 3 mute, all with a cause on file, and 7 speaking
with no cause. **Still open:** delete ntfy-responder's row once its environ carries the setting.
If its lines then land, block-buffering was the cause that row left "not established".
