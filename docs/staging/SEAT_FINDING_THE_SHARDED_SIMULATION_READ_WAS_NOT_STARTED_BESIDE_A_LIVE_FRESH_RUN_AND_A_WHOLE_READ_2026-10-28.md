# The sharded simulation-suite read was not started: a fresh run and a whole read of the same suite were already live

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

*Delivery seat, 2026-10-28 07:55 GMT. Disposition: released as a duplicate of `the-simulation-suite-is-read-whole-at-origin-head`.*

## What was seen at draw time

- `/var/tmp/fresh-run-out-20e7d66234/` has no `DONE.json` and its `launch_long_job` wrapper (pid 996490) is alive.
  The item says never to read beside a fresh run.
- `pytest tests/simulation` (pid 745483, cwd `/var/tmp/simsuite-2cf3201c5c`, 1h58m old) is already reading the same
  suite whole, serially, for the other claim. A sharded read beside it would be the same work twice.
- Headroom: `available_mb` 10,242, `swap_free_mb` 11.7, `oom_kills_total` 38. A 4-6 shard read (several GB each) beside
  a 4.8 GB full-suite census would put the fresh run at OOM risk.

## Disposition

No shards launched and no code changed. The claim is released. Whoever picks up `the-simulation-suite-is-read-whole-at-origin-head`
should read the junit from pid 745483's run first. Shard only if it has not finished or fails to finish, and only once the fresh run has a `DONE.json`.
