# [WORKER FINDING] The census timeout repair never reached the unit systemd reads, and it inverted the ordering it was written to fix

**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`
**Discharged:** `tests/tools/test_head_green_census.py::test_the_bound_systemd_will_apply_is_the_one_this_repo_wrote`, `background/head-green-census.service` — the installed unit is now read by a control, so the two files crossing is a red rather than a thing nobody looks at.
**Found:** 2026-09-02 12:55 UTC, doing the Lane 0 instruction's *first* clause — *"before running it, deal with the second half of `2112a1f03`'s own finding: check what that timeout is now and whether it has headroom"*. It had headroom in the file I was pointed at. systemd was reading a different file.

## Class registration

Belongs to `controls_that_cannot_fail`. The sub-shape is the live one this project keeps paying
for: a control whose subject is a repo copy of an artefact rather than the artefact the machine
loads, so it grades a number that kills nothing.

## What was true

`2112a1f03` raised two numbers to fix an ordering: the census's own
`SUITE_TIMEOUT_SECONDS` 3300 → **7200**, and `TimeoutStartSec` in
`background/head-green-census.service` 3600 → **7500**, so the suite's clock fires first and the
census can report UNPROVEN instead of being SIGTERMed into silence. It added
`test_the_census_timeout_clears_the_duration_it_has_observed`, which holds both directions and
went green.

That test reads `background/head-green-census.service`. Measured, not inferred:

```
$ systemctl --user show head-green-census.service -p TimeoutStartUSec -p FragmentPath
FragmentPath=/home/rich/.config/systemd/user/head-green-census.service
TimeoutStartUSec=1h
$ ls -l ~/.config/systemd/user/head-green-census.service
-rw-r--r-- 1 rich rich 813 Aug 31 18:12 ...
```

**`TimeoutStartSec=3600`, unchanged since 31 August.** The repair edited the repo's copy. Nothing
installed it, and `systemctl --user daemon-reload` was never run, so the unit systemd actually
loads never moved.

## Why this is worse than the state it replaced, and not merely unfixed

Before `2112a1f03`: suite 3600, systemd 3600. A tie — systemd usually won, and the census usually
vanished on a long night. That is the defect the commit describes.

After `2112a1f03`, **on the box**: suite 7200, systemd **3600**. systemd now wins
*unconditionally* on every run past the hour. The run that motivated the repair took **58:57**.
The `except TimeoutExpired` branch that reports UNPROVEN became structurally unreachable in the
live environment, by the commit that was written to make it reachable — and the tree said green,
because both numbers the test compares live in files systemd does not open.

The next firing was `Thu 2026-09-03 03:34 BST`, fourteen hours out. The nightly census — the
control that certifies HEAD for every other claim here — would have been killed at 03:34+1h with
no verdict and no alarm, for a second consecutive night.

## Scope: it is this unit and no other

Every `background/*.service` and `*.timer` was diffed against its installed copy. Twenty-five are
byte-identical. Two were not: this one (behavioural, 3600 vs 7500) and `seat-executor.timer`
(a `Description=` string only, no behavioural difference). So this is not systemic install drift —
it is one repair that stopped one `cp` short of its own subject, which is why nothing systemic
noticed.

## Repaired

1. Both stale units copied to `~/.config/systemd/user/` and `daemon-reload` run. Verified live:
   `TimeoutStartUSec=2h 5min` (7500s) > `SUITE_TIMEOUT_SECONDS` 7200. Reversible with one `cp`.
2. `test_the_bound_systemd_will_apply_is_the_one_this_repo_wrote` reads the **installed** unit,
   asserts it exists, asserts it equals the repo's copy, and asserts it clears the suite's own
   clock. Its MUTATION is the state this box was in an hour ago: write `TimeoutStartSec=3600`
   into the installed unit and it fails on the second assertion, while the test next door stays
   green — which is the whole content of this finding, expressed as a falsifier.

The path constant deliberately points OUT of the checkout, against the grain of every other test
in that file. Those want isolation from the box; this one wants the box, because a bound that is
only true in the tree stops no SIGTERM.

## What is not repaired, and is a real hole

Nothing refuses the general case: a repo unit file may drift from its installed copy at any time
and only this one unit now has a control. The cheap mechanism is one test over the whole
`background/*.service` + `*.timer` set asserting each is either absent from
`~/.config/systemd/user/` or identical to it. It is not built here — this document's own class
disposition says the next work on `controls_that_cannot_fail` is the missing-falsifier mechanism
rather than a further instance, and building a second one-off would be the shape that register is
complaining about. Filed as the gap, not papered over.

## The instruction this discharges

Lane 0 asked whether the timeout has headroom for a full ~24,000-test run, and said *"if it does
not, give it headroom and say what you set and why — that is a run-duration allowance, not a claim
about the code"*. Stated plainly: **I set nothing.** The numbers `2112a1f03` chose (7200 against a
worst observed 3537s, on this repo's own `bound > 2 × worst measured` rule; 7500 in the unit,
keeping 300s for checkout, teardown and report) are right and I left them alone. What was missing
was not headroom — it was that one of the two numbers was written somewhere systemd could read it.
