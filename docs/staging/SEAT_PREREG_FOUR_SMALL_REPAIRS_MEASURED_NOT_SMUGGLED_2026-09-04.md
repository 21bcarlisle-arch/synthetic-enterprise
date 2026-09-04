**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** measurements_that_mirror

# Pre-registration: two predictions before the measurements that judge them

Filed 2026-09-04 by the delivery seat, before running either measurement, for the Lane 0 claim
`three-small-repairs-measured-2026-09-04-and-deliberately-not-smuggled-into-other-commits`.

This exists because the two questions below are the ones where I could otherwise read the answer
back as though I had expected it. The other two items in the same claim (the epoch guard and the
worktree-local hand-off store) are **not** pre-registered: their answers were already established
by reading code before this file was written, and a prediction filed after the answer is not a
prediction. What was established for those is recorded in the findings themselves.

## P1 — the blast radius of protecting the director-reserved mirror

`tests/production_surface_guard.py` keeps `site/data/` **file-scoped** on a 2026-08-10 measurement
that several generator tests legitimately rewrite `site/data/*.json`. Adding
`site/data/director_reserved.json` to `PROTECTED_FILES` therefore has to be measured, not argued.

**Prediction: ZERO tests go red across the whole suite.**

The basis, established by reading before predicting: the file has exactly **one writer** —
`background/action_needed._mirror_reserved_to_site`, which writes `SITE_RESERVED_PATH`.
`tools/generate_director_data.py` names `director_reserved.json` in `FEED_FILES`, but `load_feeds`
only **reads** it; that generator's single `out_path.write_text` writes `DELTA_NAME`. So the
2026-08-10 "generator outputs" argument does not reach this path at all, and the one test module
that drives the mirror already redirects `SITE_RESERVED_PATH` to `tmp_path`.

**What refutes it:** any red at all. If the count is not zero, the writers are not the ones I
found, and the addition waits until they are named.

**What I will not do if it is refuted:** add a `real_state_write` marker to whatever went red.
That marker is for a test that genuinely must write the surface, and the whole point of this path
is that no test may.

## P2 — how much the dead-owner rule actually frees

`background/disk_headroom` reported *"nothing reapable (all scratch in use or within TTL)"* while
`/tmp` (a 12 GB **tmpfs** — this is RAM) sat at 83%. The abandoned population is `git archive HEAD`
extracts from finished seat turns: no `.git`, ~288 MB each, all **younger than the 6 h
`REPO_COPY_TTL`**, so the TTL cannot reach them however dead their maker is.

**Prediction: a dead-owner rule keyed to a pid embedded in the directory NAME frees exactly one of
the four (`/tmp/bisect_daemon_1563179`, 288 MB) and leaves the other three (`headext`, `headx`,
`prereg_3d36`, ~865 MB) untouched, because their names record no owner.**

This prediction is deliberately unflattering: it says in advance that the fix reaches **25% of the
population by count and 25% by size**, and that the residue is not a bug in the rule but the
absence of any record of who made those directories. If I write it down only after the measurement,
"it worked" and "it worked on a quarter of it" are indistinguishable in the record.

**What refutes it:** a different count either way. More than one means a name I did not read as a
pid is one; fewer means the pid I read is live, or an exclusion above it (`.git`, in-use, project
containment) fires first.

---

# RESULTS, written in beside the predictions rather than in a separate document

Both were run after this file was written and before the commit that carries them. Kept here, next
to the claims, because a prediction filed away from its result is not checkable.

**P1 — HELD.** `768 passed, 1 skipped, 2 xfailed, 0 failed` in 556s, with
`site/data/director_reserved.json` already in `PROTECTED_FILES`. The population was the complete
one by construction, not a sample: every test module referencing `action_needed`,
`director_reserved` or `SITE_RESERVED` (25 modules), which is exhaustive because the path has a
single writer and that writer lives in `action_needed`. The reachability half is covered too —
`test_the_sink_refuses_the_director_feed_whatever_writes_it` passed in the same run, so the guard
demonstrably refuses the path rather than passing by not being reached.

**P2 — HELD, exactly, including the unflattering half.** Against the live filesystem:

    dead-owner pid 1563179   288 MB  age=4.1h  /tmp/bisect_daemon_1563179
    WOULD FREE: 288 MB across 1 dirs

One of four, 288 MB of ~1,153 MB. `headext`, `headx` and `prereg_3d36` record no owner and were
untouched, as predicted. The residue is written up as a decision, not a bug, in
`SEAT_FINDING_A_TTL_CANNOT_BOUND_SCRATCH_WHOSE_MAKER_DIED_IN_THE_FIRST_HOUR_2026-09-04.md`.

---

**The residue is the finding, not the rule.** If P2 holds, the honest statement is that the reaper
still cannot free anonymous scratch inside its TTL, and that is a separate decision about whether
extracts should record their maker — not something to fix by loosening the TTL, which would be
picking a number to make a measurement come out.
