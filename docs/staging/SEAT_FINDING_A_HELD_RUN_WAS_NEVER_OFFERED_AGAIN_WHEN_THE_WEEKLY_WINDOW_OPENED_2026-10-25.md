# SEAT FINDING: a run held mid-week was never offered again when the weekly window opened

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

## What was found (re-measured 25 Oct, against the shared tree)

The four 904a091f7b markers of 24-25 Oct sit in `docs/staging/done/`. Each was HELD by the weekly
window: they carry no did-not-land tag and no publish tag, and `staging/` holds no marker. Neither
`process_leftover_run_markers` nor anything else ever looked at them again. The premise was not
spent. 904a091f7b being on origin says nothing about whether its runs were offered.

## What landed

The HOLD branch tags the archived marker `publish-held`. The worker's sweep offers the newest held
run once, when the window is open and nothing is pending. Design and guards:
`docs/design/PUBLISH_DECOUPLING.md` "A HELD RUN WHEN THE WEEKLY WINDOW OPENS". Control:
`tests/background/test_a_held_run_is_offered_once_when_the_weekly_window_opens.py`. Four mutants
were tried and all four fire: the offer call removed, the once-only guard removed, the window
guard removed, and the hold tag write removed.

## Read at real inputs, and the one surprise

Run read-only over the shared done/, the selector refuses with "not held", because the legacy
markers predate the tag. Given a tagged copy of the 03:16Z marker and an open window, it still
refuses: **`run_output_latest.json` is not any 904a091f7b run.** It is byte-identical to
`run_output_b2bc3d8da5_20261025T1230Z.json` (13:31Z), and that run has no marker. This mechanism is
right to refuse, because offering the 03:16Z marker would publish a mix of two runs. For this
Monday, the one-shot timer `mondays-window-marker-20261026` keys on latest's own commit and stays
the route. Leave it armed.

## Still open, not fixed here

- The supersession frontier counts a held marker as published. That is harmless for ordering,
  because the newest marker dominates. It is not a true statement, and it shares a root with the
  re-arm doc's filed frontier fault.
- ~~A run that writes `run_output_latest.json` without a marker is invisible to every publish
  route.~~ **Closed 25 Oct, see below.**

## What wrote latest without a marker (25 Oct, re-measured)

No daemon did it. `longjob-mondays-run-b2bc3d8da5` (`launch_long_job`, 12:27-13:32Z) ran
`tools.run_annual_report` in a clean worktree. The seat then copied its output onto
`run_output_b2bc3d8da5_20261025T1230Z.json` and onto latest by hand, as recorded in commit
294c5286f1. In `background/sim_runner.py`, the byte copy onto latest and the marker write were two
statements in the loop, so any promotion made outside the loop had only the copy to imitate.

The fix makes `sim_runner.promote_run` the one writer of latest, and it writes the marker in the
same call. The loop goes through it. A run made outside the loop is promoted with
`python3 -m background.sim_runner --promote docs/reports/run_output_<sha>_<stamp>.json`. That door
refuses, with the reason named, a file that is not a timestamped run output, or one whose header
carries no `producing_commit`. Control:
`tests/background/test_a_run_promoted_to_latest_is_named_by_a_marker.py`. Two mutants were tried
and both fire: the marker write removed, and the commit read replaced by a guess.

A hand `cp` onto latest still cannot be refused. The door makes the right route the obvious one;
it does not wall off the wrong one. Promoting this Monday's run is left to the one-shot timer,
which is already armed for 26 Oct 04:05Z. Running `--promote` now as well would write a second
marker for the same run.

## What the 26 Oct one-shot did (re-measured 08:15Z)

**The prediction was wrong.** The item said the one-shot would offer
`run_output_b2bc3d8da5_20261025T1230Z`. It did not. At 03:28Z the basics run at 4ae8da9b0f took
`run_output_latest.json`, and the window held it. So at 04:05Z `drop_marker.py` wrote
`run_complete_20261026T040501Z.md` for `run_output_4ae8da9b0f_20261026T022647Z.json`, as
`/var/tmp/mondays-window-marker/out.log` records. b2bc3d8da5 is an ancestor of 4ae8da9b0f, so the
four billing fixes are in the run that was offered. The b2bc3d8da5 run itself is superseded, and
nothing should offer it again.

The marker did its job: the run was re-offered at the window. Publishing it failed four times,
each time for a publisher defect and not for the run:

| marker | outcome |
|---|---|
| 040501Z (one-shot) | did not land: `behind_origin` 05:14Z |
| 051730Z (`--promote`) | did not land: `commit_refused` 05:46Z |
| 064020Z (`--promote`) | did not land: `behind_origin` 06:59Z |
| 070039Z (`--promote`) | did not land: `commit_refused` 07:40Z (19-page stale-copy refusal) |
| 080604Z (`--promote`) | did not land: `commit_refused` 08:28Z. The publisher races are fixed; two billing gates refuse the run's own book, see `SEAT_FINDING_THE_MONDAY_RUN_4AE8DA9B0F_IS_REFUSED_BY_TWO_BILLING_GATES_ON_ITS_OWN_BOOK_2026-10-26.md` |

The later markers came through `sim_runner --promote`, so this one-shot was the last of its kind,
as intended. The publisher defects are owned by `the-publish-lands-from-a-trunk-worktree-not-the-primary-checkout`
and the stale-copy commits ae03a6317 and 78a6dfacc. This claim does not duplicate them.
