# A held lane crash wakes the interactive session, by a waiter the session arms itself

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `a-broken-lane-wakes-the-interactive-session` (Lane 0)

Item 4 of the interactive lane's 13:57Z answer (`docs/staging/console/SEAT_REPLY_2026-10-09.md`).
Items 1–3 are on origin (`470f2a746`, `17b474e2b`; see
`SEAT_FINDING_A_LANE_UNIT_THAT_CRASHES_TWICE_IS_SEEN_AND_REPAIRED_2026-10-09.md`).

## Premise, re-measured at draw

The two cited commits are the prevention leg and the detect/repair leg. Neither delivers anything
to the interactive session: a held crash reaches NTFY, the seat brief and
`docs/observability/.lane_unit_crash.json`, and the 13:57Z reply's own point 4 is that nothing
puts any of those into that session. So the premise is not spent. The duplicate claim the draw
named has the same id; it is this draw's own write. No rival seat or `surgical_land` was running.

## The ask as written cannot be built, and what was built instead

"Send it to the interactive session as a message, which wakes it": nothing that runs outside the
session can do that here. Only two routes put text into a live session. The first is typing into
its pane, which was deleted on 2026-07-15 on the director's go (`background/tmux_relay.py`;
`tests/controls/test_no_pane_injection.py` refuses its return). The second is a Stop hook, which
fires only when a turn ends, so it cannot wake an idle session. `pull_next_work.py` also refuses
the console by design (G-L1).

What is left is a pull that wakes the session. Claude Code re-invokes a session when a background
command it started exits. So the session subscribes:

    python3 -m background.lane_unit_crash --wait-held --deadline 21600    # run_in_background

The waiter is `tools/wait_for.wait` with a named subject and a mandatory deadline (6 h ceiling).
Its probe reads the crash record that `reconcile_watch` writes every five minutes.

| state when it looks | exit | what the session reads |
|---|---|---|
| no held streak it has not already been woken for | keeps waiting; **1** at the deadline | re-arm |
| a hold appears while armed, or one is already there when armed | **0** | unit, exception line, the hold's reason, what to do |
| the crash record cannot be parsed | **3** | `UNREADABLE`, never read as quiet |

Each streak wakes the session **once**. The keys it has delivered go to
`docs/observability/.lane_unit_crash_woken.json`. A `REPAIRED` streak does not wake it: the machine
fixed it, and NTFY already said so.

Also corrected: `.lane_unit_crash.json` from the 10-09 landing was not git-ignored, and every other
machine-state file in that directory is. It is now ignored, and so is the new woken file.

## Controls

Three tests in `tests/background/test_a_lane_unit_that_crashes_twice_is_seen_and_repaired.py`:
the partition (a hold wakes it, a second arm on the same streak does not, a repair does not); a
waiter armed while healthy that wakes when the hold is written between two polls; and an unreadable
record. Four mutations, all red: drop the `HELD` filter; drop the woken write; map `FINISHED` to
the deadline exit; read a corrupt record as empty.

At real inputs, in a worktree with no crash record: `--wait-held --deadline 3` exits 1 after 3 s
with "no lane crash is held". With no `--deadline` it is refused and names why.

## The gap left open, stated rather than papered over

**The waiter delivers nothing unless the session has armed it.** Nothing re-arms it after a
restart or after it fires. It works the way the session's own "check the lanes between long waits"
habit works, except that it does the checking. The reminder is a memory note in the interactive
session's own memory index, which is loaded every session. A SessionStart hook that tells the
console to arm it would close the gap. That hook would be a mechanism acting on the director's
console, so it is his call, not the seat's. It is not raised as a concern: this note is the
proposal, and nothing waits on it.
