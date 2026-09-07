**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the renewal arm prices no gas) · **Class:** no_caller_and_never_runs

# RESULT — the reporting reduction dropped three logs, not one, and two of them nobody was chasing

## First, the drawn premise: SPENT, and I did not do it twice

The tick drew the writer-3 billing-account repair in `company/crm/customer_profitability.py` plus
the one-variable A/B pair and the graded prediction. **All of it is already at HEAD.** Measured on
real git state before starting, not assumed:

| The drawn deliverable | Where it landed |
|---|---|
| match by billing account, not `household_of` | `28ba48dd4` — `_billing_account_id(r["customer_id"]) == cid` is live at `company/crm/customer_profitability.py:156` with its reasoning beside it |
| the settled book carrying `term_start` | `99b2700de` |
| the one-variable A/B pair, prediction graded | `eb7b26f27`, written up in `SEAT_RESULT_WRITER_3_NOW_FIRES_51_TIMES_AND_EVERY_POUND_OF_IT_IS_TRANSFER_2026-09-07.md` — 0 → 51 firings, residue exactly 0, four legs of five confirmed and the refuted leg kept beside the result |

So the item's own instruction applied: *if the premise is spent, say so and release the claim rather
than doing the work twice.* This document is that, and the turn went to the first item of that
result's **"What is next"** instead — item 2, writer 3's log never reaching the saved payload,
filed as
`SEAT_FINDING_WRITER_3S_OWN_LOG_IS_DROPPED_AT_THE_REPORTING_REDUCTION_SO_ITS_PUBLISHED_SECTION_CANNOT_EVER_RENDER_2026-09-07.md`.

## What the census found, and it is not what was filed

The finding named one dropped log. **I wrote the guard first and ran it as the census, and it named
three.**

```
DROPPED (run returns it, a section reads it, extract_report_data omits it):
  ['profitability_uplift_log', 'triad_log', 'volume_tolerance_log']
carried: 8
```

Confirmed against the committed artefact, not inferred:

```
$ python3 -c "import json; d=json.load(open('docs/reports/run_output_latest.json')); \
              print([(k, k in d) for k in ['profitability_uplift_log','triad_log',
                                           'volume_tolerance_log','margin_feedback_log']])"
[('profitability_uplift_log', False), ('triad_log', False),
 ('volume_tolerance_log', False), ('margin_feedback_log', True)]
```

`_section_volume_tolerance` (I&C volume tolerance, Phase 27c) and `_section_triad_exposure` (TNUoS
Triad, Phase 27d) have **never rendered either**, by the identical mechanism and with nobody
looking for them. `extract_report_data`'s forwarding is opt-in, and its own comment says so in as
many words — a key it does not name is silently empty in every published run. The comment was
there; the control was not.

**This is the whole argument for writing the AST guard before the manual pass.** A control pinned to
writer 3 — the instance that was reported — would have gone green on the repair and left Triad and
volume tolerance exactly as they were, for the next reader to find twice more.

Field shapes were checked across the seam before carrying the two extra keys, because a rename
across an artefact seam is invisible to the suites on both sides of it:
`compute_term_volume_tolerance` and `compute_triad_exposure` return exactly the fields their
sections index, so neither section crashes now that it can reach data.

## The repair

1. **`saas/reporting/annual_report.py`, `extract_report_data`** — all three keys forwarded.
2. **`_section_profitability_uplift` now has three states, not two.** It returned `""` for both
   "writer 3 fired on nothing" and "writer 3's record was dropped before publication", and those
   are the two facts this class keeps confusing — the same shape as `compute_profitability_uplift`
   returning `0.0` both for a profitable account and for a book it cannot see. A missing key now
   says **"Cannot be reported for this run"** on the page, with its reason, and an empty log says
   it is a measured zero. *We cannot tell* is a result and belongs on the surface.
3. **The control is the census**, keyed to the relationship and not to today's count:
   `tests/saas/reporting/test_a_log_the_run_makes_and_a_section_reads_survives_the_reduction.py`.
   It goes red the moment a new `*_log` gets a section without getting a forwarding line, which is
   the only way this defect has ever arrived.

### Poison round, before believing any of it

| Poison | Result |
|---|---|
| remove the three forwarding lines | **RED**, naming all three by name |
| collapse the section's three states back to `""` | **RED** on the partition control |
| reachability floor (`>= 4` logs under census; 11 today) | asserted **before** the property, because a census that selects nothing passes by construction |

`tests/saas/reporting/` — 1003 passed.

## Recorded, not fixed: the ratchet was red before I arrived

`tests/architecture/test_static_quality_ratchet.py::test_ruff_no_rule_exceeds_baseline` is red
(I001 1315 against a frozen baseline of 1314). **It is not mine** — proved in a clean extract
rather than argued:

```
HEAD 92aa394dd: 1315   eb7b26f27: 1315   99b2700de: 1315   9d9e6f064: 1318   a56c157cb: 1318
```

My two files add **zero** I001 (the new test file is clean; `annual_report.py` is 15 at HEAD and 15
after my edit). The working tree reads 1316 because of another lane's untracked
`tools/tou_extreme_day_concentration.py`. Every lane has been landing through this red for several
commits, so it is a standing tree condition and not a wedge I introduced — filed here rather than
silently widened into an import-sorting pass across sixteen files I do not own.

## The landing

`saas/reporting/annual_report.py` was held **dirty by another lane** — an uncommitted
`svt_departures`/`svt_decisions` block dated 2026-08-31 sat in the working-tree copy. A pathspec
land would have carried it inside mine. Landed via `tools/isolate_hunks.py --keep 2 --keep 3` and
`surgical_land --content`, and the isolated bytes were re-run through the census (0 dropped, 11
under census) before landing rather than after.

## What is next

1. **Still open, and it is the biggest of the three:** two writers, one question, two populations
   (127 against 51) and two thresholds (5% of revenue against any loss). *Which one the supplier
   means is a definition question*, and CLAUDE.md names that shape as this project's most expensive
   recurring failure. **Neither count should reach a page before it is settled** — and now that
   writer 3's section can render, that is no longer hypothetical.
2. **`NET_NEGATIVE_UPLIFT_GBP_PER_MWH = 5.0` still has no sourced origin.** A placeholder now
   load-bearing on 51 real repricings and £882 of pure transfer. Exactly the shape the
   knowledge-first rule exists for: it needs a published anchor or an honest `None` with a named
   reason.
3. **Triad and volume tolerance can now be read for the first time.** Both are I&C-only, so they
   may well be genuinely empty on a domestic book — but that is now a measurable fact rather than
   an artefact of the reduction, which is the entire point of the repair.
