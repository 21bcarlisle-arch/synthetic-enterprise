**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# A TTL cannot bound scratch whose maker died in the first hour

Filed 2026-09-04 by the delivery seat. **Partly fixed in the same commit; the residue is measured
and stated here rather than left to read as coverage.**

## What happened

`/tmp` is a 12 GB **tmpfs — which on this box is RAM**. It held ~3.2 GB of abandoned 288 MB
`git archive HEAD` extracts from finished seat turns. The DISK CRITICAL alarm had fired at 383 MB
free against a 2,048 MB floor and said it *"needs a person"*. A person freed 2.0 GB by hand
(83% → 66%). `disk_headroom`'s reaper had already run, and its verdict was:

    "reaped": "nothing reapable (all scratch in use or within TTL)"

True, and useless — the same family as `test_an_empty_git_dir_made_scratch_immortal`, one rule
along. The extracts carry no `.git`, sit in no live process's cwd, and are **younger than the 6 h
`REPO_COPY_TTL`**: measured at 0.7 h, 1.4 h, 2.8 h and 3.9 h. On a box where an OOM kill has
already destroyed a published bound, that is memory pressure, not housekeeping.

**The TTL is a proxy for a question it cannot ask.** Its stated reason is *"a probe that is still
running is not abandoned"*, calibrated against a multi-hour KNIFE or EP6 lane. A seat turn's
comparison stem is dead within the hour, and the proxy has no way to know.

## The fix, and what it deliberately is not

Where the maker is *recorded*, ask whether it is alive instead of waiting out the proxy. The only
record is the directory name (`bisect_daemon_1563179`), so `repo_copy_scratch` now reads a trailing
digit run after a `-`/`_` separator and, if that pid is provably dead, stops treating the TTL as a
reason to spare. Every exclusion above it is unchanged and runs first.

**It is not a shorter TTL.** Moving the number would make the measurement come out and teach
nothing, and it would re-open the case the TTL was written for. The upper bound on "is this a pid"
is the kernel's own `pid_max`, not a number chosen here.

Failure direction unchanged — uncertainty spares: no trailing digits, a recycled pid, an unreadable
`/proc`, or any live process anywhere inside the tree all keep the directory. The rule is
**monotone** (it only ever adds reapability), pinned by its own control, because a rule that started
sparing things would quietly undo the empty-`.git` repair above it.

## Pre-registered, and it held exactly

`SEAT_PREREG_FOUR_SMALL_REPAIRS_MEASURED_NOT_SMUGGLED_2026-09-04.md`, written before the
measurement, predicted the rule would free **exactly one of four** — `/tmp/bisect_daemon_1563179`,
288 MB — and leave `headext`, `headx` and `prereg_3d36` (~865 MB) untouched, because their names
record no owner. Measured against the live filesystem afterwards:

    dead-owner pid 1563179   288 MB  age=4.1h  /tmp/bisect_daemon_1563179
    WOULD FREE: 288 MB across 1 dirs

25% of the population by count and by size, as predicted, including the unflattering half of the
prediction.

## The residue is the finding — and it is a decision, not a bug

Three of the four extracts **record no owner anywhere**. Nothing in the tooling that makes a
`git archive HEAD` stem writes down which process made it, so no rule keyed on ownership can reach
them and they still wait out the full six hours. `test_an_anonymous_extract_still_waits_out_its_ttl`
asserts that gap rather than letting the receipt imply coverage.

The choice this raises, for whoever draws it next: **make the extract record its maker** (a pid in
the name, or a sidecar the reaper reads), which turns the whole population into the covered case —
versus the two bad answers, shortening the TTL (picks a number, re-opens the case the TTL exists
for) or reaping any young `.git`-less repo copy with no live reference (a seat greps its extract by
absolute path, so cwd/fd liveness is absent for most of a live turn — that rule would delete work in
progress).

Recommendation: record the maker at the point the stem is made. Not done here because the makers are
ad-hoc shell `mktemp -d` calls across many lanes, which is a different job from the reaper's.
