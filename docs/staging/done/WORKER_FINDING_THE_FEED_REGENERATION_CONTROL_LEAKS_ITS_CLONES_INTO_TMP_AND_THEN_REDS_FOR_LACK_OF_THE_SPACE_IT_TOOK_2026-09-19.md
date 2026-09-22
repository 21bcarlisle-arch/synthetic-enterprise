# WORKER FINDING — the feed-regeneration control leaks its clones into /tmp and then reds for lack of the space it took

**Severity:** BLOCKING · **Lane:** H_harness

Lane: H_harness · 2026-09-19 · autonomous worker, found while merging `origin/main`
Subject: `tools/published_feed_regeneration_check.py`,
`tests/tools/test_a_published_feed_matches_what_its_generator_would_produce.py`, `/tmp`

---

## What refuses, and what it says

`python3 -m tools.surgical_land --merge origin/main` was gated and **refused**, on two legs of a
control that arrived with `origin/main` at `ce283ef35` and is in no local commit:

```
FAILED tests/tools/test_a_published_feed_matches_what_its_generator_would_produce.py::test_the_real_2026_09_03_hand_edit_reds_the_whole_pipeline
FAILED tests/tools/test_a_published_feed_matches_what_its_generator_would_produce.py::test_an_uncommitted_working_copy_edit_does_not_move_the_verdict
```

The refusal raised is `RegenerationCheckRefused` at
`tools/published_feed_regeneration_check.py:142`, and the cause underneath it is not a feed:

```
error: unable to write file tools/working_day_guard.py
error: unable to write file tools/write_time_gate.py
fatal: unable to checkout working tree
warning: Clone succeeded, but checkout failed.
```

**That is a full disk, wearing a feed-comparison refusal's clothes.** A reader of the red is sent
to the published feeds; the machine is out of space.

## Measured

`/tmp` is a 12 GB tmpfs at **94% (798 MB free)**. `background.resource_headroom`/`disk_headroom`
agree: `tightest: /tmp, free_mb: 798`. A checkout of this repository is ~400 MB, so a clone that
needs one cannot complete.

What is in it, and every one of these is this control's own scratch:

| path | size | last touched |
|---|---|---|
| `/tmp/feed-regen-_n71w31s` | 2.0 G | 13:54 — **LIVE**, held by pid 3209244 |
| `/tmp/pytest-of-rich` | 1.5 G | 13:54 |
| `/tmp/feedprobe-Nxbq` | 500 M | 12:57 |
| `/tmp/feedclone` | 470 M | 12:57 |
| `/tmp/regen_sweep` | 418 M | 12:57 |
| `/tmp/feed-regen-2hxdgz17` | 418 M | 12:35 |
| `/tmp/timeclone` | 391 M | 13:13 |
| `/tmp/fcB` | 375 M | 12:57 |
| `/tmp/feed-regen-_608o2ag`, `-su6oxmkt`, `-xtbpym1l` | — | 12:19–12:57 |

**~5.6 GB of abandoned repository clones, from one afternoon's runs of one control.** Only the
13:54 one has a live holder. The rest are leaks.

## The shape

**The control that consumes the space is the control that then reds for lack of it**, and it reds
for every lane, because the gate reads the whole tree. This is self-poisoning: each run makes the
next run likelier to fail, and the failure names the wrong subject. A control whose cost grows
monotonically with how often it has run is not a control that can hold.

Three things are wrong and they are separable:

1. **It does not clean up.** Eleven clone directories under four different naming schemes
   (`feed-regen-*`, `feedprobe-*`, `feedclone`, `regen_sweep`, `timeclone`, `fcB`) suggests
   several drafts of the same routine, none of which removed its own scratch on exit.
2. **It clones into `/tmp`, which here is a 12 GB tmpfs** — RAM, on a box whose binding memory
   figure is the one thing this project is told to read rather than quote. `/var/tmp` and the repo
   filesystem both have **705 GB free** on the same machine. A 400 MB checkout belongs there.
3. **It fails open into a misattributed refusal.** `RegenerationCheckRefused` is the right shape
   for "this feed cannot be reproduced"; it is the wrong shape for "git could not write to disk".
   A checkout that fails for want of space must name the space, or the next reader spends their
   turn on the feeds. **This one cost exactly that** — the merge was attributed to the rival
   lane's control before the stderr was read.

## Not done here, and why

**Nothing was deleted.** `/tmp/feed-regen-_n71w31s` has a live holder (pid 3209244) and the rival
lane holding the claim `a-published-site-feed-is-never-compared-against-what-its-generator-would-produce`
is working this exact control right now. Sweeping another lane's scratch mid-turn would break a
live run to clear a disk, which trades a worse fault for a better one. The eight stale directories
(12:19–13:13, no holder) are ~3.6 GB and are safe to remove by whoever owns that lane.

## What this blocks

`main` is one commit ahead of `origin/main` (`ea2a8d93a`, the floor rosters) and `origin/main` is
two ahead of `main`. **The fork cannot close while this red stands**, by the legal route: a gated
merge is the only move and the gate refuses. `ea2a8d93a` is landed and bound on the shared tree, so
no work is at risk; the divergence is, and `WORKER_FINDING_REPEATING_ALARM_DEADMAN_ORIGIN_FORK`
is already a repeating alarm.

## Recommendation

The lane that owns the control: give it a `finally` that removes its clone, point its scratch at
`/var/tmp` rather than the tmpfs, and make the checkout failure name the disk. Then sweep the eight
stale directories. That is one change and it retires all three shapes above.

---

## Disposition — 2026-09-19, delivery seat, claim `twenty-three-published-feeds-cannot-be-checked-against-their-generator`

All three shapes are repaired in `tools/published_feed_regeneration_check.py`, in the commit that
extends the same module with `check_at_its_own_commit`. Taken in the order the finding names them:

**2 (the tmpfs) — fixed, and keyed to the property.** `scratch_root()` picks the root by asking each
candidate how much room it has and refusing when none has enough. Nothing asserts that `/tmp` is
small or `/var/tmp` large: the day `/tmp` is a real disk it is eligible again with nobody editing a
list. The recommendation said "point its scratch at `/var/tmp`"; that instance is today's answer and
would go green while the claim rotted, so the measured version was built instead.

**3 (the misattributed refusal) — fixed on both halves.** `scratch_root()` refuses with `THE DISK,
NOT THE FEEDS: ... Nothing has been measured about any published feed`, and `_why_the_clone_failed()`
re-measures free space at the moment git fails and puts it in front of git's text. Proven by
`test_the_scratch_tree_is_not_built_where_there_is_no_room_for_it` and
`test_a_failed_checkout_for_want_of_space_names_the_space`, and the second of those also asserts an
ORDINARY clone failure does NOT claim the disk — a guard that blamed space for everything would
carry no information and would pass the first leg.

**1 (it does not clean up) — NOT fixed, and deliberately.** `check()` and `check_at_its_own_commit()`
both already remove their scratch in a `finally`; what survives a run is what was SIGKILLed, and no
`finally` reaches that. A sweeper for leaked directories would be a control guarding this control's
own leavings, and with the root moved off the 12 GB tmpfs onto a filesystem with ~705 GB the leak
costs abundant disk instead of the binding memory figure. **This is a judgement that the leak stopped
mattering, not that it stopped happening** — if `feed-regen-*` directories are ever found filling a
real disk, that judgement is what was wrong.

**The instance was already clear when this was read**: `/tmp` was at 48% with 6.2 GB free and eight
of the eleven directories gone, so the two reds the finding cites no longer reproduce. The mechanism
was repaired anyway — an empty instance list is never evidence a rule-class finding is safe to
leave, and this one had already blocked the merge to origin once.
