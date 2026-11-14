**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Where the seats collide on shared files (pre-registration, then result)

*Delivery seat, seat-executor worktree, 14 Nov 2026, acting on the director's steer
`docs/staging/advisor/DIRECTOR_STEER_ONE_WRITER_PER_SHARED_FILE_MEASURE_WHERE_LANES_COLLIDE_FIRST_2026-11-14.md`.*

## Pre-registration (written before any per-file collision count was run)

**What a collision is.** A *writer* is one Claude session (one transcript jsonl under
`~/.claude/projects/`), or one non-Claude committer (a daemon commit carrying no `Claude-Session`
and no `Co-Authored-By: Claude` line). A *collision hour* for a file is a clock hour in which two or
more distinct writers wrote it: a Write/Edit tool call naming the file, or a commit touching it.
One writer rewriting its own file thirty times is churn and counts zero. Window: 31 Oct 00:00 to
14 Nov 24:00 GMT.

**Contention events** are commits whose subject or body names merge, reconcile, surgical, held
behind origin, sweep, fork, unlanded or stranded. An event is *traced to* a file when the file is
in the commit's diff or named in its message.

**Predictions, mine, beside the advisor's:**

1. P1 (the advisor's): `site/data` and `DIRECTION.yaml` lead; `company/` and `simulation/` are small.
   I agree on direction, and sharpen it: by collision hours, the top file is a generated feed under
   `site/data/` (I guess `publish_provenance.json` or `delivery.json`), and `DIRECTION.yaml` is in
   the top three.
2. P2: `company/` plus `simulation/` together hold under 5% of collision hours.
3. P3: the top three files hold at least 40% of all collision hours. If they hold under 25%, the
   answer is the steer's outcome 3: the cost is spread, paid and known, and no trial is proposed.
4. P4: at least half of contention events trace to a file in the top ten.

The session-time cost estimate is the hardest leg and is graded last: it can only be an
order-of-magnitude reading from transcript timestamps around contention tool calls
(`isolate_hunks`, `surgical_land` refusals, `refresh_to_head`, merge retries).
