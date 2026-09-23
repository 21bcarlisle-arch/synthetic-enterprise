**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
"the run ledger is tracked and never committed so HEAD's copy is 64 days stale"

# The published series was FRESH, the KPI was CAPPED, and the page that rendered it was deleted a month ago

**Delivery seat, 2026-09-19, claim
`the-run-ledger-is-tracked-and-never-committed-so-heads-copy-is-64-days-stale`. Predictions in
`SEAT_PREREGISTRATION_IS_THE_PUBLISHED_RUN_HISTORY_BUILT_FROM_THE_STALE_HEAD_LEDGER_2026-09-19.md`,
written before the measurement and left uncorrected beside these results.**

---

## 1. The duplicate-work note, disposed of first

The draw named one live claim that "may be this work under another name":
`the-run-ledger-is-tracked-and-never-committed-so-heads-copy-is-64-days-stale` — **this item's own
id**, reported as already held because `.seat_work_in_hand.json` is not written by the draw. The
file holds one unrelated entry (`PB3_book_growth_as_earned_outcome`). Not a rival, and the third
consecutive Lane 0 draw to report itself this way. Carried on.

## 2. The decision the item asked for: TRACKED, and committed by the publisher

`docs/observability/run_history.json` is now committed by `process_run_complete.git_commit_push`
with the rest of the publish surface, together with its sibling `run_insights.json`, which was in
exactly the same state and which nobody had noticed.

**Why not the other shape.** Untracked machine-local state, with `HEAD`'s copy deleted, is the
other way to stop the file being *both* — and it loses. `count_run_history_total` would publish
**0** from any fresh checkout. Its own docstring correctly argues that 0 is *honest*; honest and
wrong is still wrong on a surface that is built and committed automatically. A published
artefact's source belongs in the commit that publishes it. `detect_t6` names the ledger as its own
raw data for the same reason.

**Why the class, not the instance.** Every `files.append` block in `git_commit_push` closes
"regenerated every cycle, committed by none" — for `site/data/*.json` (a glob, after three files
recurred it one at a time), for `site/state` (a tracked-file census, after three more), for the
derived-artefact register. This is the same class on the **inputs** instead of the outputs, so it
is closed the same way: `insights_artefact_paths()` reads the paths off
`tools.generate_insights`'s own module constants, so a third output added there tomorrow is
committed without anyone remembering to edit the publisher. **No glob**, deliberately —
`docs/observability/` also holds ~40 gitignored locks and registers and a 47MB log, and `git add`
is all-or-nothing, so one ignored path would stage nothing and the cycle would commit no content
at all.

The 64-day divergence is discharged in this commit: the ledger and the insights file are landed at
their live bytes (`52f572916`, `2026-09-19T21:39:56Z`, £158,278.48), so `HEAD` and the shared tree
agree for the first time since 2026-07-17 and every fork now reads September's book.

## 3. The measurement the item asked for, against the predictions

**The question (§5 of the prior finding): are the site's published run-history series and the
"Sim runs" KPI built from the stale `HEAD` ledger?** Three answers, and only the first was
predicted.

| | predicted | measured |
|---|---|---|
| **the published series** | fresh | **fresh** — `HEAD:site/data/dashboard.json` carries 10 entries ending `2026-09-19T19:24:56Z`, git `87c485285` |
| **the publish gate rebuilding it** | does not | **does not** — `publish_scope` scopes *tests*; no generator runs in the `HEAD` checkout |
| **the "Sim runs" KPI** | > 100 on the fresh copy | **100, on BOTH copies, and for neither's reason** |

**P1 is half right and the wrong half is the finding.** I predicted the KPI would read >100 on the
shared tree because the live ledger is fresh there. It reads **100 on both**, because
`append_run_history` ends `history = history[-100:]`. The count is capped, so it is
*vintage-independent* — which is exactly why 64 days of staleness could never have surfaced it,
and why a framing built entirely on `HEAD`-vs-working-copy was structurally unable to ask the
question. **The stale-ledger frame found the stale ledger and would never have found this.**

Measured, not inferred: the committed ledger has held exactly 100 entries since **2026-06-30**
(`39c15c1b5`, the first commit at the cap) — 81 days — and `count_run_history_total` has returned
exactly 100 on every dashboard build in that window. The function exists to replace a dead counter
pinned at 10. It is a dead counter pinned at 100.

**And `HEAD`'s ledger was worse than stale, it was disjoint.** All ten runs in the committed
dashboard's series are absent from the committed ledger (10/10), and all ten are present in the
live one. The published series and its committed source had no run in common.

**P4 held: the shape was very nearly determined before the measurement, and I said so in
advance.** What the measurement changed was the severity and the second finding, not the choice.
**P5 (the refutation condition — "nothing published reads the file") did not fire as written, but
came closer than I expected**, and §4 is why.

## 4. THE FINDING UNDERNEATH — the KPI's renderer was deleted on 2026-08-20 and three live comments still describe it as published

`site/project/` and its `renderKpis()` went in `03dd8c49e` ("the five tabs are the site now:
eleven pages deleted"). Measured: **nothing under `site/` reads `run_history` or
`run_history_total`.** `site/index.html` is `dashboard.json`'s only consumer and reads five keys —
`portfolio`, `meta`, `customers`, `financial`, `selection_leg`. The field is computed on every
cycle, committed into `dashboard.json` on every cycle, and rendered by nobody.

Until this commit, **three live comments in two publish-path modules** and two lines of
`PROJECT_OVERVIEW.md` described it as the Project tab's live KPI — including one written
2026-09-05, sixteen days after the page was deleted, and
`PROJECT_OVERVIEW.md`'s *"currently 100 entries and growing"*, written while the ledger was
already sitting on its cap. **That is what cost this turn its frame**: the drawn item, the
prior finding's §5, and my own pre-registration all reasoned about a live published KPI on the
strength of a comment. A comment naming a surface is a claim about the tree, and it rots exactly
like a stamped literal.

Repaired beside the claim in `count_run_history_total` and `append_run_history` — what the number
is (a **floor**, not a total), why (the cap, stated beside the line that does it), and that its
page is gone.

**What is NOT decided here, deliberately.** Whether `run_history_total` should carry its bound
(`"≥100"`), be recomputed from a source that is not truncated, or be deleted from the payload with
the series, is a question about what the site's surface should contain. Nothing renders it today,
so nothing is wrong on the live site and nothing is urgent; deleting a published field on my own
judgement is the wrong direction to be decisive in. **Filed.**

## 5. The control, and why the old one could not have caught this

Three legs in
`tests/background/test_the_published_series_and_the_ledger_it_came_from_are_committed_together.py`,
each mutation-proven, each caught by the leg written for it:

| mutation | leg that fired |
|---|---|
| ledger restored to `HEAD`'s July bytes | `..._every_run_the_committed_dashboard_publishes_is_in_the_committed_ledger` |
| `insights_artefact_paths()` → `[]` | `..._the_publisher_names_every_insights_artefact_a_published_figure_is_built_from` |
| the `_publish_insights_artefacts(files)` call deleted | `..._the_publish_commit_actually_reaches_that_list` |

**Keyed to the property.** *A run the committed dashboard publishes can be found in the committed
ledger.* Not "the ledger has 100 entries" (green the day the file is deleted) and not "the last
entry is `52f572916`" (red the day a run succeeds). It tolerates the ledger being **ahead** — one
cycle's benign skew, which is the live state right now — and fails when it is **behind**, which is
the entire defect.

**Read off disk, not through `git show`**: `surgical_land` gates an extract with no `.git`, and
the tree the commit would create is the subject. Absent or unparseable is a **failure**, not a
skip — a `return None` would make every leg vacuous in precisely the tree where the question
matters.

**And the leg's membership test comes from two OTHER modules**, never from the helper under test:
a path is in scope when `generate_insights` declares it as an output **and**
`generate_dashboard_data` declares it as an input.

**The control that was already there, and was green throughout.**
`test_count_run_history_total_counts_full_history_not_truncated` — whose name is a direct claim
about this defect — passes on a **37-entry fixture**, below the cap. It pins the *reader*; the
truncation is in the *writer*. A control whose subject is narrower than the class its name claims,
and its fixture size is what hid it: any fixture at or above 100 would have failed to distinguish
the two, which is the other half of why nobody saw it.

## 6. What was NOT done

- `run_history_total`'s own shape (bound, recompute, or delete) is filed in §4, not decided.
- `build_info.json` is a third `docs/observability` input the dashboard build reads, last
  committed 2026-07-08. Its committed copy and its working copy **agree** — it is manually
  maintained, not regenerated, so it is not this class. Noted so the next reader does not have to
  re-establish it.
- `PROJECT_OVERVIEW.md`'s two stale lines about the KPI are left as written. They are phase
  history — a record of what was believed on the day — and §4 is the correction beside them.
