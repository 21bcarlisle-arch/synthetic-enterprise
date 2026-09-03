# [WORKER FINDING] The census reports and nothing draws it, and "newly failing" was never a delta

**Severity:** RECORDED (the route is built; the 830 themselves are now DRAWN, not fixed)
**Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted
**Found:** 2026-09-02, on the director's console instruction: *"Why hasn't the 830 been fixed? My
reading: the HEAD-green census reports and nothing draws it. Twelve, seventeen, thirty-three and now
830 — each announced, none worked, while everything with a route into the draw gets done. Same shape
as the reaper built in July and never called."*

## Class registration

Belongs to `no_caller_and_never_runs`. His diagnosis was right and the shape is the same one three
times over in two days.

## "Newly failing" has been false in every message this control has ever sent

`docs/observability/head_red_baseline.json` was written **2026-08-12** and its content is:

```json
"known_red": []
```

`verdict()` reports `new_red = failures − baseline`. With an empty acceptance list that is *every
failure*. So **"830 test(s) newly failing" meant "830 tests are failing"**, and 12, 17 and 33 meant
the same thing on earlier nights. The word `newly` carried no information on any of them, and the
four numbers the director listed back are not a rising delta — they are four absolute counts wearing
a delta's word.

Worse, the design intends that word to be load-bearing: the module's own docstring argues *"alarm on
the DELTA, not the absolute count… a standing red set that nobody has dispositioned becomes wallpaper
within a week."* It became wallpaper anyway, because the mechanism that was supposed to prevent it
was never populated.

## And a count with no subject is not work

The census names **ten** tests in its page, out of 830. The complete list went to the systemd
journal, which nothing reads and no artefact keeps. So there has never been anything to pick up —
only a number to worry about, which is exactly what the director said he was doing with it.

## What the 830 actually are, and it is not 830 defects

Recovered from the journal (the census discarded its own output, so this is the only copy):

| | |
|---|---:|
| red at HEAD, 2026-09-02 04:30 | **830** |
| in `tests/background/` alone | **820** |
| `OSError` | **760** |

`tests/background/conftest.py` has **four autouse fixtures and every one of them takes `tmp_path`**,
so every test in that directory allocates a temp directory unconditionally. When temp allocation
fails, the whole directory dies at fixture setup. Reproduced in shape: pointing `--basetemp` at an
unwritable path errors **every** test in a module with an `OSError` subclass, at setup, exactly as
observed. `/tmp` on this box is a **12 GB tmpfs — RAM** — and currently holds ~3.4 GB of abandoned
`git archive HEAD` clean-stem checkouts (a dozen of them, up to 117 hours old), 1.7 GB of retained
pytest roots and 2.5 GB of session scratch.

**Not yet proven, and stated as such:** the exact errno. A bare `OSError` (rather than
`FileNotFoundError` or `PermissionError`) is consistent with `ENOSPC`, which is one of the few errnos
with no dedicated subclass — but that is an inference and a full census re-run is in flight to
establish it. The environmental reading is not in doubt; the specific resource is.

## What was built — a route, not a repair

Per the director's three properties, and each is enforced rather than promised:

* **A named subject.** `docs/staging/reference/HEAD_RED_REGISTER.md` names every owed test, with its
  age and its module grouping, and says so when it must elide.
* **A live baseline.** `docs/observability/head_red_observed.json` is machine-written on every census
  run and carries, per test, `first_seen`, `last_seen` and `runs_red` — the recurrence signal the
  census could not express, and the same argument `class_debt` makes for instance count.
* **Zero means zero.** The register is spliced into `work_queue()` at rank 37 — below a class
  register, above a finding — **only while something is owed**. Nothing owed, no queue item. That is
  enforced in the splice, so the end state is reachable by work being done.

**The one property that had to survive** is the acceptance list staying human-written: *"a control
that absorbs its own new failures into its own baseline cannot fail."* So the design splits in two —
the machine writes what it SAW (observation), only a person writes what is FORGIVEN (acceptance) —
and `record()` is structurally unable to write any file at all. An UNPROVEN run records nothing, so
an outage can never be booked as 830 tests fixed.

There is deliberately **no blanket Disposition** on this register, unlike a class register. A class
is a judgement about a pattern; a red test is not. One paragraph must not be able to retire 830
subjects, so the only two exits are per-test: fix it, or accept it by name with a reason.

## What this finding does not claim

Not that the census is a bad control — its subject (a clean HEAD checkout, unscoped, no `-x`) is
right and hard-won, and it is the only thing on this box that measures HEAD as a whole. Not that the
830 are fixed: they are DRAWN. And not that the empty baseline was carelessness — it is the correct
initial state for an acceptance list. The defect is that nothing ever put anything in front of it,
so an acceptance list that should have been a short, argued set of exceptions instead silently
turned the delta into an absolute count.
