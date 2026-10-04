**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The heartbeat-off-main item was drawn 19 minutes after it landed

Drawn 13:21 BST as `the-heartbeat-leaves-main-per-the-directors-steer`, the director's 09:35 steer.
It was already spent: `3373f3523` (13:02, "The idle heartbeat leaves main") is on origin and does
the whole ask. I took the disposition, not the work: `--release`. `--landed --commit 3373f3523`
correctly refused, because that commit predates the draw.

**Checked live, not from the commit message (13:20 BST):**
- The shared tree's HEAD contains `3373f3523`. The running `process_run_complete` beat at 13:16:50
  into the ops repo (`~/synthetic-enterprise-ops`, `b8fde9f48 liveness: …`). It also force-pushed
  the public `liveness` branch (`4bcb45019`, one parentless commit). It made no commit on main.
- raw.githubusercontent.com serves the branch's `tick_heartbeat.json` with HTTP 200 and
  `access-control-allow-origin: *`, so the site banner's fetch (`site/assets/freshness-banner.js:82`)
  works from the browser.
- No commit on origin since 13:02 touches only `agent_status.json` or `tick_heartbeat.json`.
- Readers: `background/deadmans_switch.py` and `tools/generate_dashboard_data.py` read neither
  file on origin. The banner reads the deployed copy and the branch copy, and treats the newer one
  as live. It judges "this page is not arriving" on the deployed copy only.

**Still open, from the DONE line:** "no heartbeat-only commit in the following stretch" can only be
read after the stretch. Monday's merge-pressure census (proposal item 4) is where that reading
lands.

**For the seat:** release has tombstoned the focus row. Drop it from `DIRECTION.yaml`'s focus at
the next orientation, or it will be offered again.
