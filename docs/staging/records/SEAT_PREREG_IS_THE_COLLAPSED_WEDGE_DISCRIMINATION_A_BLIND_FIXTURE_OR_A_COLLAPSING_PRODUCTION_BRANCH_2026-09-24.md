**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: is the collapsed wedge/hot-origin discrimination a BLIND FIXTURE or a COLLAPSING PRODUCTION BRANCH?

Claim id: `the-one-red-the-publish-gate-cites-collapses-both-legs-of-its-own-discrimination`.
Written before the fixture was changed, so that the answer cannot be chosen to fit.

## The red, as it stands at `f59a7d475` (= `origin/main`)

`tests/background/test_the_liveness_surfaces_refusals_left_only_an_orphaned_log_line.py::
test_a_wedged_tree_and_a_hot_origin_are_told_apart_in_the_record` fails on its FIRST assertion,
`wedged["evidence"] != hot["evidence"]`. Both records end:

> …whether this is a dirty-tree collision was NOT established (AssertionError: this fixture has no
> answer for `git rev-list --count`…), so this names the refusal and not its cause

## The two candidate causes the drawn item names

* **BLIND INSTRUMENT** — the fixture cannot answer three git commands the production branch issues,
  so production never reaches the code that discriminates.
* **COLLAPSING PRODUCTION CODE** — production genuinely renders one string for both states, and the
  fixture's blindness merely hides a second, real defect behind the first.

They are not exclusive. The honest outcome may be "blind instrument AND a production defect the
blindness was hiding", and that is the outcome this pre-registration is most at risk of missing,
because clearing the first is the flattering place to stop.

## The prediction

**BLIND INSTRUMENT, and specifically at ONE of the three commands, not all three.**

The mechanism I predict, traced but not yet run:

1. `_refused_advance_cause` (`background/process_run_complete.py:6021`) imports and calls
   `origin_reconcile.commits_ahead(project)` INSIDE its `try`. The test patches
   `orc.paths_blocking_fast_forward` but NOT `commits_ahead`.
2. `commits_ahead` shells `git rev-list --count origin/main..HEAD` (`origin_reconcile.py:1348`),
   which the fake refuses.
3. The refusal is an `AssertionError`, caught by the function's own broad `except Exception`, which
   returns the "NOT established" verdict with `clause=""` — **before `_blocking_clause` renders the
   blocking list at all**. So the `blocking` argument, the one input that differs between the two
   legs, is discarded on both.

The other two unanswered commands (`git merge-tree --write-tree` at `origin_reconcile.py:216`, and
`git fetch --quiet` at `process_run_complete.py:6155`) are predicted to be **upstream noise for this
test**: they sit in `_publish_surface_collisions` and `_advance_to_origin_or_say_why`, both of which
already fail closed to a refusal, and neither contributes to the recorded `evidence` string's tail.
Modelling them should change the log lines and NOT the verdict.

### What each outcome would look like, decided now

| Observation after the fixture answers all three | Reading |
|---|---|
| Test goes GREEN | Blind instrument alone. The production discrimination works and was never reached. |
| First assertion still RED (`wedged == hot`) | Production collapses the two states. The repair is in `process_run_complete.py`, not the test. |
| First assertion GREEN, a LATER assertion red (the holder path / the KIND / "NOTHING local collides") | Blind instrument PLUS a real production gap in what the record names. Report both. |

### The falsifier I am most likely to be wrong about

That `commits_ahead` must be modelled to return **0**. `_refused_advance_cause` asks divergence
FIRST and returns the DIVERGED sentence on any `ahead > 0` — a sentence that is identical for both
legs, because on a fork no path is the cause. So a fixture that answers `rev-list --count` with a
non-zero number would leave the test red **for a second, different reason** and would look like
confirmation of the production-defect branch. If that happens it is a fixture error, not a finding,
and it must be reported as one.

## What done means for the drawn item

`last_clean_publish` moving past 2026-09-21T18:15Z is the item's own done condition and it is NOT
in this seat's gift — it needs a publish cycle on the shared tree. What IS in this seat's gift and
is what will be claimed: the cited red green at HEAD, the cause named, and the finding appended to
the publish-outage series as its fifth cause.

---

## THE RESULT, recorded beside the prediction rather than above it

**CONFIRMED: blind instrument, at `git rev-list --count` alone.** The one-variable controls are in
the series document (`docs/staging/done/WORKER_FINDING_SEVENTEEN_GREEN_SUITES_...`, §"A fifth
cause"): removing only the `rev-list` modelling reproduces the identical red; removing only
`merge-tree`/`diff` does not. Production's discrimination renders correctly the moment it is
reached — wedged 900 chars naming the holder and the KIND, hot origin 728 chars saying nothing
local collides. No production defect in the discrimination.

**PARTIALLY REFUTED: the reason I gave for the other two commands was wrong.** I predicted
`merge-tree`/`fetch` were "upstream noise… neither contributes to the recorded evidence string's
tail". The verdict was right and the mechanism was not. They contributed nothing because a THIRD
blindness was short-circuiting them first: `_drive` passed the publish path relative where both
production callers pass it absolute, so `_our_publish_paths` returned `None` and
`_publish_surface_collisions` never consulted the arriving set at all. I had read "changes no
verdict" as "not load-bearing" when it actually meant "unreachable" — the same inference error the
R15 catalogue files under a green mutation having a third cause.

That was caught only by the decision table's third row being taken seriously: the leg that requires
an ADMISSION rather than a refusal. It is now
`test_a_behind_origin_publish_origin_is_NOWHERE_NEAR_is_admitted_not_refused`, and it is what makes
the `merge-tree`/`diff` modelling load-bearing.

**The falsifier did not fire.** `commits_ahead` is modelled at 0 and the DIVERGED branch was not
taken, so the green is not the fixture-error case this document named in advance.
