**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `clear-the-unguarded-observability-writer-ratchet-red-at-head`) · **Class:** controls_that_cannot_fail

# RESULT — the un-guarded writer ratchet is armed again at 56, and the number I first published was my own dirty tree

Discharges the BLOCKING finding `SEAT_FINDING_THE_UNGUARDED_LEDGER_WRITER_RATCHET_HAS_BEEN_RED_AT_
HEAD_FOR_TWO_WEEKS_AND_ITS_OWN_MESSAGE_SAYS_DO_NOT_DO_THE_EASY_THING_2026-09-09.md`.

## The bound was not raised. The writers were guarded.

`tests/background/test_live_ledger_guard.py::test_the_narrowing_to_measurement_ledgers_is_measured_
not_assumed` was red at HEAD against a bound of **74** frozen on 2026-08-26. The finding measured
86 on 2026-09-08, and a clean HEAD extract at `8c53c35e5` reads **86** today.

**30 write sites across 17 modules now route through `guard_live_ledger_write`. 86 → 56.** The
floor moves DOWN to 56, eighteen below where it was frozen, so the ratchet is armed again with
headroom nobody has to take on trust.

## THE FIRST DRAFT OF THIS PAGE PUBLISHED 87 → 57, AND BOTH NUMBERS WERE MY OWN DIRTY TREE

That draft censused the SHARED WORKING TREE, which carries four other lanes' uncommitted
modules — `boot_sha`, `delivery_seat`, `disk_headroom`, `self_clearing_alarm_census`, plus an
untracked `standing_red.py`. So it counted writers that are not at HEAD, will not be at HEAD when
this lands, and belong to nobody in this lane. The "one more had landed overnight" sentence above
was the same mistake reasoning about itself: nothing had landed overnight, I was reading another
lane's in-flight work and calling it drift.

**A ratchet frozen against a number only the author's dirty tree can reproduce is a bound no other
lane can meet** — every other lane inherits a floor set by work they cannot see, and the first one
to land a legitimate writer eats a red that is not theirs. That is the same class as the defect
this finding is about, one turn later and pointing the other way.

Re-measured in a clean HEAD extract carrying this lane's hunks and nothing else: HEAD **86**,
guarded **56**, delta **30** across 17 modules, and the newly-guarded set is a strict subset of the
HEAD set — no writer appeared that HEAD did not already have.

Modules touched: `autonomous_runner`, `background_worker`, `boot_announce`, `daily_self_note`,
`deploy_restart`, `long_job`, `notify`, `ntfy_utils`, `process_run_complete` (8 sites — the 14 the
finding named, minus the five whose destination is not an observability path), `publish_freshness`,
`reconcile_watch`, `retro_cadence_check`, `sanity_daemon`, `supervisor` (6), `trust_ledger`,
`worker_seat`, `worker_tick` (2).

## Selection was by DESTINATION, not by the census's own proxy

The census counts a function when its **module** mentions `observability` and the function calls
`write_text`. That is a proxy, and taking it at face value would have produced decoration: guarding
`(checkout / ".git" / "HEAD").write_text(...)` lowers the number and protects nothing.

So each candidate write was resolved to its actual target through the module-level constant, and
guarded only where that target lands inside `docs/observability/`. Five of the fourteen the finding
named in `process_run_complete.py` were left alone on that test — three writes to
`docs/status/LATEST.md` and two to a scratch checkout's `.git/`. **They are still counted.** A
proxy that over-counts is the safe direction for a ratchet to be wrong in, and narrowing the census
to remove them would have been the bound-raise wearing a better hat.

## What is deliberately still owed, and why

`agent_status.py`'s two write sites read as un-guarded and are **contained harder than the guard
would contain them**: an `in_test_process() and is_live_record_path()` early return that NO-OPS
instead of raising, decided by measurement on 2026-08-31 — 32 of the whole suite's 84 refusals were
that one call, in tests that were not about agent status. Raising there reds every daemon test in
the repo to protect a dashboard field. `_calls_the_guard` recognises one spelling of containment
and not that one, so this is a **false negative of the census**, left visible in the count rather
than excused by an allowlist row.

## The poison round, because "57" means two opposite things

Reachability first, and re-run in the clean extract after the re-measurement above. One extra
un-guarded observability writer was appended to `background/notify.py`; the test went **red at 57,
naming `notify.py::_poison_probe_writer`**, and went green again the moment it was reverted. The
bound is exactly tight at 56 — a single un-guarded observability writer reds it — so the green is a
measurement, not a vacuum.

## The exiled guard came home

`guard_site_publish_pipeline` was written in `live_ledger_guard.py` on 2026-09-09, then moved into
`process_run_complete.py` for one commit purely because this red made its proper module untouchable:
the commit gate selects any test that NAMES a staged path. It is now back beside its twin, with
`PUBLISHED_FEED_DIRS` and `SitePublishUnderTest`. Its docstring, the containment test's docstring
and this test's docstring all carry the round trip rather than quietly forgetting it.

One test moved with it and had to: `test_outside_a_test_process_the_site_publish_is_permitted`
patched `prc.in_test_process`. The guard resolves that name from the module it is **defined** in,
so after the move the old line patches a name nothing reads. It now patches `live_ledger_guard`.
The failure mode was loud (the refusal fires and the test reds), not silent — which is the only
reason the move was safe to make without re-proving the whole control.

## A second population the census cannot see at all

`_functions_that_write` matches `write_text` and nothing else. **35 functions in the same scope
append through `open(..., "a")` and are not members of the population** — not counted, not owed,
absent from the failure output a reader works from. It is not theoretical: three live narration
logs in this working tree carry `pytest-of-rich` lines right now, none of them present at HEAD.
Measured and filed as `SEAT_FINDING_THE_LIVE_RECORD_CENSUS_ONLY_SEES_WRITE_TEXT_AND_THIRTY_FIVE_
WRITERS_APPEND_THROUGH_OPEN_2026-09-09.md` — LATENT, because `tests/test_isolation_guards.py` does
catch that class, after the fact, by reading the bytes.

## What is NOT answered here

The finding's third item, and the more general defect: **why nothing selected this test for two
weeks.** A ratchet that is red at HEAD and blocks nothing reads exactly like a control that is
holding, and the same silence would cover any ratchet in `tests/background/`. That is a separate
subject with a separate cost, and it is left filed rather than half-answered — clearing this
instance does nothing about the class.
