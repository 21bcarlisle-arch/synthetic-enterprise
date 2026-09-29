**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Python 3.14's stdout buffer is 128 KiB, not 8 KiB, so an unflushed daemon is mute for days rather than minutes, and sanity-daemon is alive and inaudible

**2026-09-28.** Lane-0 item `sanity-daemon-log-silence-cause`. The claim in `.seat_work_in_hand.json`
was stamped 17:09:01Z, seconds before this turn started. That is this draw's own write, not a
rival, so the work was done rather than disposed of.

**Cause, now on file** as `log_silence` on the `sanity-daemon` row of
`background/process_manifest.yaml`: the daemon is alive and working. Its log file advanced at
15:40, 16:10 and 16:40Z. `wchan` is `hrtimer_nanosleep`. Its only `print()` is unflushed, and the
128 KiB buffer takes about 4 days of output to fill. No run since 2026-09-24 has lived that long,
and SIGTERM discards the buffer. The journal confirms it: the one 7-day run spoke once, as a single
129,559-byte burst of 3-day-old lines.

**What this corrects.** The `supervisor`, `deadmans-switch` and `background-worker` rows said
Python block-buffers at 8 KiB. On this box `/usr/bin/python3` is 3.14.4 and
`io.DEFAULT_BUFFER_SIZE` is 131072. This was controlled under `systemd-run --user`:

| probe | journal lines |
|---|---|
| 40 × 610 B unflushed (24 KB) | 0 alive, 0 after stop |
| one 131 KB print + 2 small | 0 alive |
| 500 × 610 B unflushed (300 KB) | ~419 alive |
| 40 × 610 B `flush=True` | 40 / 40 |

The corrected figure strengthens those rows' conclusions. Only `background-worker`'s mechanism
is now open. Its row says it is "sometimes verbose enough to cross the buffer" in a ~10-minute
run, and crossing 128 KiB that fast is not yet established. That row now says so beside the claim.

**Not done, deliberately:** no daemon behaviour changed. The one-line remedy is
`sys.stdout.reconfigure(line_buffering=True)` at daemon start, or `PYTHONUNBUFFERED=1` in the
generated units. It would make every journal-mute row audible at once. It is a behaviour change
across the fleet, and it belongs to its own item.
