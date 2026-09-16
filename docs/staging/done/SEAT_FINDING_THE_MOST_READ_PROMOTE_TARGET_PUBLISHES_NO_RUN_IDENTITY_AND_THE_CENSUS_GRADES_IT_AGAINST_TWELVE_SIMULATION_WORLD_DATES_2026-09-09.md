**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# FINDING — the most-read promote target published no run identity, and the leg that exists to say so reported nothing because twelve simulation-world dates were standing in for it

LATENT and not BLOCKING: no published figure is wrong, and the census's refusing leg (STALE) still
works on the four targets that do carry a header. It is LATENT and not RECORDED because the
fail-open is live and unconditional — the leg that grades claims about `run_output_latest.json`
cannot fail on that target today, whatever anyone writes about it.

## The direction, and the half of its premise that was spent

The Lane 0 item said: `docs/reports/run_output_latest.json` is *"the only promote-by-copy target in
the tree that publishes no run identity at all"*, and *"`tools/promoted_artefact_claim_census`
reports the whole target as 'we cannot tell', its own category kept out of both the defects and the
passes."*

**The first half is true. The second half is false, and it is false in the more expensive
direction.** Measured on this tree, 2026-09-09:

```
census --json:  ungradable_targets: []      cannot_tell: 0 rows
```

The `cannot_tell` category is empty. `run_output_latest.json` is not in it, because
`_artefact_dates` does not return an empty set for it — it returns **17 run-identity tokens**:

| tokens | where they come from | what they are |
|---|---|---|
| `2016-12-31` … `2024-12-31`, `2025-06-07` | `clv_snapshot_as_of.*` | **simulation-world** year ends |
| `2021-12-31`, `2025-06-07` | `wholesale_credit_exposure.peak_sample_date`, `.mark_date`, `mc2_collateral_death_test.*`, `margin_call_book.accounts_population` | **simulation-world** portfolio and stress dates |
| `2019-07-01` | `won_successor_activations.C3_2` | a **simulation-world** contract activation |
| `2026-09-01`, `2026-09-01T05:42:21Z`, `2026-09-01T05:42:23Z`, `05:42:21Z`, `05:42:23Z`, `20260901` | `scenario_analysis.generated_at`, `.portfolio_as_of` | **another producer's artefact** |

**Not one of the seventeen is this run's identity.** Twelve are dates inside the simulated world —
2016 to 2025, the historical record the company lives through. The other five belong to
`scenario_analysis`, which `saas/reporting/annual_report._load_scenario_analysis` **reads off disk**
from `site/state/scenario_analysis_latest.json`, written by `tools/run_live_decisions`. It is a
different producer's stamp, folded into this payload by an `extract_report_data` key.

So a sentence in `tools/` or `site/` claiming *"the 2021-12-31 run"* of this target grades as
**SUPPORTED** against a collateral stress test's mark date, and a claim citing *"the 2026-09-01
run"* grades as supported against a scenario file's clock. The census cannot currently be wrong
about this target in the direction that would show.

## The claim in the control's own docstring, which was true when written

`tools/promoted_artefact_claim_census._artefact_dates` records the repair that made the leg
non-vacuous, and states its result:

> `three_arm.json` goes from 131 tokens to its handful of stamps; `run_output_latest.json` goes to
> **none**, which is the correct answer and not a failure […] `_UNGRADABLE` names that on the
> surface rather than letting an unanswerable question read as a pass.

`none` is now **seventeen**. This is the shape memory already carries twice over — a control keyed
to today's answer, and a recorded measurement that rots without anything going red. Nothing in the
tree could notice, because the leg's output going from "we cannot tell" to silence looks exactly
like the problem being fixed.

## What this turn did about it

**The root cause, repaired at the producer.** `tools/run_annual_report.reconcile_and_stamp` now
writes `generated_at`, `producing_commit` and `world_identity` at the **top** of every run output —
the same header the other four promote targets already publish. `_cache_meta` stays exactly as it
was (three consumers and the versioned filename read it), and both slots are bound to one set of
locals so they cannot drift.

`_cache_meta` was not already the answer, for three reachability reasons rather than content ones:

1. its stamp is `20260901T054223Z`, and `_RUN_IDENTITY`'s compact alternative requires a word
   boundary after the date — the `T` is a word character, so the pattern **cannot fire inside it**;
2. its world digest sits at `_cache_meta.world_level.digest`, at depth 3, and `_artefact_dates`
   stops at depth 2 because run identity is supposed to be shallow; and
3. it was absent from every artefact written before 2026-09-04 — including the one on disk.

Four mutations, each killing its named leg and no other (poison round run first, all seven legs
green at HEAD):

| mutation | leg that dies |
|---|---|
| header never applied | `..._carries_the_run_identity_header` (+3) |
| `generated_at` written in `_cache_meta`'s compact shape | `..._is_readable_by_the_census_that_grades_it` |
| `_git_commit_hash`'s `"unknown"` sentinel passed through | `..._publishes_no_sha_at_all` |
| header clock resolved separately from `_cache_meta`'s | `..._cannot_disagree` |

The second is the one worth having: the compact shape is *already in the file* and is the obvious
thing for the next writer to copy, and the census cannot read it at all.

**The bytes on disk, backfilled fail-closed.** The artefact at `docs/reports/run_output_latest.json`
is byte-identical to the blob landed by `0247f3061` (2026-09-01T06:08:25Z) and unchanged since. It
now carries the same three-key header with every slot `null` and each naming its reason, plus one
extra key, `run_identity_unavailable_because`, whose *presence* is the signal that this artefact
was stamped after the fact rather than by its own run.

**What was established:** the blob identity above. **What was not, and was therefore not written:**
when the run ran, and at which commit. `0247f3061` is the tree the bytes were *committed* in, not
the tree that *produced* them — the exact confusion `producing_commit` exists to prevent — so it is
stated as evidence inside `unavailable_because` and deliberately not promoted into `commit`. The
`scenario_analysis` clocks bound when the run assembled; they are a different producer's stamp and
publishing one as `generated_at` would be a number picked because a number was needed. The world
digest is not recoverable at all: `simulation/departure_level_anchor.py` has been re-fitted since,
so computing one now would name today's world, not the one these figures were measured in.

## The same class, one layer over, found by the wall-channel census refusing this landing

`tools/wall_channel_census` refused the first attempt: adding a top-level `generated_at` created a
new channel-F member, `generated_at -> saas/reporting/annual_report.py`. Channel F joins the
artefact's top-level key set against business-side modules that read a key of that **name** by
literal, so a new top-level key can surface a read that already existed.

What it surfaced is the same defect as the one this turn is about.
`saas/reporting/annual_report.py:10717` reads `sa.get("generated_at", "unknown")` where
`sa = data["scenario_analysis"]`, and renders it into the annual report as:

```
Generated: {generated_at}
```

That label is bare. The stamp under it belongs to `site/state/scenario_analysis_latest.json`,
written by `tools/run_live_decisions` — **not** to the run, and not to the report. A reader of the
annual report is told when it was generated and is given a different producer's clock. It is the
same shape as the census grading run claims against `scenario_analysis`'s stamp: a foreign
artefact's identity standing in for this one's, because both were folded into one payload and
nothing labelled the seam.

Not fixed here — it is a report-rendering change with its own reader, and absorbing it would put
two unrelated repairs behind one revert. Ruled and recorded in
`docs/design/wall_channel_census_baseline.json`, which now carries the member with its reason: no
import moved, no envelope changed, and the business side reads exactly what it read before.
The row is carried as a real member rather than narrowed away, because a narrowing that made it
disappear could only hide.

## PRE-REGISTRATION — the second half, written before it is measured

The producer repair does not close the fail-open, and it makes one corner of it marginally worse:
`_artefact_dates` walks *every* shallow scalar, so the prose inside my own `unavailable_because`
fields contributes its date literals to the target's identity set. **The census must read the
identity an artefact DECLARES, not any date it happens to carry shallowly** — which is what its own
docstring already says it does.

**Measured after the backfill, and stated because it is a cost my own change added: the target's
token count goes 17 → 20.** The three new ones (`06:08:25Z`, `2026-09-01T06:08:25Z`, `2026-09-09`)
are dates in the prose that explains why the artefact cannot name its run — the control reading the
refusal as the answer. It moved no graded row: `rows` 14 → 14, `stale` 1 → 1 (the same
`generate_value_arms_data.py:5757` row, byte-identical), `cannot_tell` 0 → 0, `ungradable []` → `[]`.
Writing those dates in a shape the regex cannot match was available and was not done: that is
gaming the control, and the control is what is wrong.

Predictions, recorded before running the narrowed census. Written to be refutable:

1. `run_output_latest.json` → **0 tokens**, so it enters `ungradable_targets` and its rows move to
   `cannot_tell`. This is the state the direction's premise described and the tree did not have.
2. `value_cycle_ab_s1_noise_floor.json` → **unchanged at 7 tokens**; every one of them already
   comes from the header.
3. `value_cycle_ab_s1_three_arm.json` → **loses `2026-08-28`** (which comes from some other shallow
   string) and keeps the other 7.
4. `site/data/snapshots/LATEST.json` and `site/state/live_decisions_latest.json` → **I do not know**,
   because I have not read their top-level shapes. If either publishes identity under a different
   field name, narrowing to a fixed name list would silence real grading — that is the
   narrowing-that-can-only-hide shape, and it is the thing to check before shipping, not after.
5. The `stale` count → **unchanged at 1** (`tools/generate_value_arms_data.py:5757`, token
   `2026-08-31`, target `three_arm`). That token is not in three_arm's set either way.

If (4) comes back with a target that declares identity under other names, the narrowing must be
keyed to *"a field the artefact declares as its own identity"* and those names admitted — not
excused with an allowlist row, which would be an allowlist excusing the mechanism the control
points at.

## RESULT — prediction 4 is REFUTED, and it kills the narrowing as drafted

Measured immediately after the landing above, and kept here beside the prediction rather than
replacing it. **Both targets publish run identity, and neither uses any of the three field names.**

| target | its identity fields |
|---|---|
| `site/data/snapshots/LATEST.json` | `snapshot_ts`, `snapshot_label`, and `dashboard.meta.generated_at` / `.git_commit` |
| `site/state/live_decisions_latest.json` | `decision_run_at`, `portfolio_as_of` |

Narrowing `_artefact_dates` to `{generated_at, producing_commit.*, world_identity.digest}` would
have taken **all 15 tokens** off these two and made both `ungradable` — silencing grading that is
real and currently working. That is precisely the narrowing-that-can-only-hide shape, and the only
reason it did not ship is that the prediction was written down before the measurement instead of
after it. Predictions 1, 2, 3 and 5 stand and are untested until the repair exists.

**So the repair is not a narrowing.** Four producers name the same fact five ways
(`generated_at`, `snapshot_ts`, `decision_run_at`, `_cache_meta.generated_at_utc`), and no rule
over field *names* can separate "when this artefact was made" from "a date inside the simulated
world" — `portfolio_as_of` and `wholesale_credit_exposure.mark_date` are the same English and
opposite populations. **The definition has to come from the producer, not be inferred by the
consumer**: each promote target declares which of its fields are its identity, and the census reads
that declaration. Anything else is the census guessing, which is what it does today.

## What is next

**A run-identity declaration, producer-side, across the four promote targets.** Done means: each
target names its own identity fields in its payload; `_artefact_dates` reads only what is declared
and returns nothing for a target that declares nothing; `run_output_latest.json` lands in
`ungradable_targets` with its rows in `cannot_tell`, which is the state this finding's premise
described and the tree has never had. It is a separate landing from this one because it changes how
five targets are graded and touches three producers this turn did not.

Explicitly **not** the next step: narrowing to a name list. It is refuted above.
