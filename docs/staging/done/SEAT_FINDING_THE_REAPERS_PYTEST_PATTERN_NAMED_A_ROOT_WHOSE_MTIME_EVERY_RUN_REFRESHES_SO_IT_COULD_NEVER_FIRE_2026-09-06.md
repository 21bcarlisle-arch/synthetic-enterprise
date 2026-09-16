**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted

*Filed BLOCKING and downgraded to LATENT in the same turn, deliberately: it WAS blocking — `/tmp`
stood at 100% of a 12 GB tmpfs, a full-suite run was failing on ENOSPC, and this seat's own stdout
capture was broken — and the reap plus the fix below cleared it. The severity tracks the condition
after the fix, not the alarm it caused.*

# The reaper's pytest pattern named a root whose mtime every run refreshes, so it could never fire

**Found:** 2026-09-06, delivery seat, by a command dying with *"the temp filesystem is full (0MB
free)"* mid-turn while grading level-zero rows. Not by an alarm.

---

## The measurement

`background/disk_headroom.SCRATCH_PATTERNS` carried `("pytest-of-*", 6 * 3600)` with the comment
*"pytest's own root; it keeps the last 3, this bounds everything older"*. **Both halves were
false.**

```
  /tmp                        12G   12G    8.0K   100%
  /tmp/pytest-of-rich                      4.4G
      pytest-13   1.5G      pytest-16   852M
      pytest-15   849M      pytest-17   850M      pytest-18   373M   (7 children, not 3)
  dh.reapable()   ->  []
```

`Path("/tmp").glob("pytest-of-*")` matches **exactly one directory** — the shared root
`/tmp/pytest-of-rich`. Its mtime is refreshed every time pytest creates a new child, so on a box
that runs tests continuously its measured age rounds to zero against a six-hour TTL. It cannot
reach any TTL.

*The TTL is written in words there on purpose, and it is not style.* `finding_classes.cost_evidence`
bills any `<digits>h` with a cost word in its window to this class's cumulative episode-hours, and
the first draft of this document put **6 recorded episode-hours** into the
`controls_that_cannot_fail` register out of the phrase "a 6h TTL" — a threshold read as damage. The
narrowing in that function exists to stop exactly this (its docstring names the ruling's own "72
hours" ageing threshold as the case it was built for) and it does not cover a TTL. Recorded here
rather than in a register of its own: it is one sentence of evidence, the class it belongs to is the
one this document is already filed under, and no lane is blocked by it.
The four stale children holding 4.05 GB were never enumerated at all, because the pattern names
their parent.

## Why moving the TTL was not the fix

There is no age at which reaping the root is safe. It is shared by every run *including the one in
flight*, so an entry that fired would have deleted the live suite's tmpdir. The old entry was not
merely inert — it was **unusable at the grain it named**, in both directions at once.

So the grain moved down, to `pytest-of-*/pytest-[0-9]*`. `[0-9]` excludes the `pytest-current`
symlink, which names the run in flight and is not scratch.

## The second half: the stated safety property did not hold for this population

The module promises *"a directory that is in use by a live process is never reaped"*. Measured with
a full-suite run in flight:

```
  pytest-19   age_h=0.01   in_use=False        <-- the live run's own directory
```

That is structural, not a race. `in_use_dirs()` reads `/proc/<pid>/cwd`, and a pytest temporary
directory is somewhere pytest **writes**, never somewhere it **stands**. Once the grain moves down
so the TTL actually bites, a TTL is the only thing left standing between the reaper and a run
longer than six hours — and a TTL is a statement about likelihood, not about use.

`current_run_dirs()` closes it by positive identification, the same doctrine as the rest of the
module: pytest maintains a `*-current` symlink beside each run, so the live run names itself at a
grain the cwd scan cannot reach.

## What this is an instance of

The director's ruling of 2026-08-19 that created this module said *"I don't want a third
instance"*. **This is the third instance**, and it arrived through the mechanism built to stop the
second. The class is `CLASS_CONTROLS_THAT_CANNOT_FAIL`: this module's own docstring already records
`head-checkout-*` as a pattern that matched nothing, and records the typed list being blind to 22
ad-hoc repo copies. That is now three patterns-that-cannot-fire in one tuple, found one at a time,
each by the exhaustion it was supposed to prevent.

The generalisable shape, and it is not about pytest: **a TTL applied to a shared root is a TTL
applied to nothing, because the root's mtime is the newest child's arrival.** Any `(pattern, ttl)`
pair in this tuple whose pattern can match a directory other programs keep writing into has the
same defect.

## Class registration

Belongs to `controls_that_cannot_fail`. Declared rather than left to the title, which names the
mechanism (a glob and an mtime) and carries no token of the family — the exact fail-open the
declaration channel exists for.

## Fixed in this commit

- `SCRATCH_PATTERNS` reaps `pytest-of-*/pytest-[0-9]*`, not the root.
- `current_run_dirs()` protects the run a `*-current` symlink names, at any age.
- `reapable()` skips symlinks — `is_dir()` follows them, so the link would otherwise be listed as a
  victim and its target's bytes charged to a receipt that freed nothing.

Five controls in `tests/background/test_disk_headroom.py`, each naming its own defect. Poison round
run before the battery: four mutations (root grain restored, current-link guard dropped, symlink leg
dropped, and the premise leg) each **killed by the test aimed at it**, target-present asserted
before each patch, and the unmutated baseline (30 passed) run through the identical command.

## Not fixed, and deliberately left

`REAP_ROOTS` is `(/tmp, /var/tmp)` and this box's `/tmp` is a **12 GB tmpfs — i.e. RAM**. The disk
governor and the memory governor are watching the same bytes through two instruments that do not
know it, and `PRESSURE_FLOOR_MB = 2048` was argued against disk cycles, not against a box whose
RAM the same 2 GB is competing for. That is a separate finding and is not asserted here.
