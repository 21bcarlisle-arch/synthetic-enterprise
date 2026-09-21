# The Pages root publishes a named manifest, not the `docs/` tree

**Severity:** BLOCKING
**Lane:** H_harness
**Class:** publish_gate_and_wedge

BLOCKING is lane-scoped. It blocks here because the GitHub Pages workflow serves internal findings,
design documents and observability logs at a public root right now, and the repo's own model of what
a reader can reach disagrees with what the workflow does.

Claim: `pages-root-serves-more-than-anyone-checked`. Drawn 2026-09-20 as LANE 0 DELIVERY.

## Class registration

`publish_gate_and_wedge`. Declared rather than left to the title regex: the family is defects in the
publish path itself, and this is the publish path's *subject* being wrong — the artefact contains
things nobody decided to publish. The sibling class `figures_on_a_superseded_clock` owns the
`docs/shadow/` instance (80e363721); that was a frozen page, this is the surface that served it.

## PREMISE RE-MEASURED AT DRAW TIME — STANDING, NOT SPENT

The draw warned that `80e363721` is already an ancestor of `origin/main` and the work may have landed
by another route. It has not. That commit deleted the *instance* (`docs/shadow/`) and says so in its
own closing section: *"Left open, deliberately, and it is the bigger subject: the Pages upload is
`path: docs`, whole."* Measured in this worktree:

| Leg the item asserts | Measured at `80e363721` | Verdict |
|---|---|---|
| The workflow uploads `docs/` whole | `.github/workflows/github-pages.yml` → `upload-pages-artifact` with `path: docs` | STANDS |
| `docs/staging/` is served | present in the artefact root, 8,600 tracked files | STANDS |
| `docs/design/` is served | 909 files | STANDS |
| `docs/observability/` is served | 282 files, 47 MB of logs | STANDS |
| `docs/instructions/`, `docs/review_gates/`, `docs/state/` served | all present | STANDS |
| Three places read `paths-ignore` as a publish filter | workflow comment; `startup_anchor_freshness._UNPUBLISHED`; the same module's docstring holding the opposite truth | ONE REPAIRED, TWO STAND — 80e363721 corrected the `_UNPUBLISHED` comment to say `paths-ignore` is a trigger filter, but the list is still *used* as the publish filter at `discover_maintained_surfaces`, and the workflow comment is untouched |

The duplicate-claim warning names `pages-root-serves-more-than-anyone-checked` — **this very id**,
held with `paths: []` in `.seat_work_in_hand.json`. It is this item, claimed and undelivered, not a
rival under another name. No disposition is owed; the work is owed. Carried on.

## THE DECISION, AND IT IS MINE TO TAKE

The prior finding filed this as "the director's call, not a delivery one". I disagree and am acting,
for the same reason the `docs/shadow/` deletion was taken rather than asked. The four reserved
classes are money, real people, an irretractable public claim under Poesys's name, and safety.
**Narrowing what is published removes claims; it is the opposite of the third.** What is
irretractable is leaving 8,600 internal findings — including BLOCKING ones naming defects in our own
figures — served at a public root under Poesys's name. Every part of this is reversible by
`git revert`. Notified, not asked.

**The decision: the Pages artefact is built from a named manifest. `docs/` stops being the artefact.**

A path under `docs/` is published if and only if `tools/pages_publish_manifest.PUBLISHED` names it.
A new directory added to `docs/` tomorrow is **not published by default** — which is the direction
the failure needs, because the defect was a surface that grew silently.

The manifest is what the repo demonstrably links to at the Pages root, and nothing else. Its content
is derived, not chosen: every `https://21bcarlisle-arch.github.io/synthetic-enterprise/…` URL in the
tree was enumerated first and the manifest covers all of them.

**And the trigger becomes the same list.** `paths-ignore` is replaced by an inclusive `paths:`
naming exactly the manifest roots plus the two files that can change the artefact (the workflow and
the manifest module). Trigger and publish then cannot disagree, because they are one list, and a
control says so. That also repairs a live second defect nobody had noticed: `docs/state/**` is in
`paths-ignore` *and* is a deliberate publish target (`mirror_github_pages`, `PUBLISH_SURFACE_ROOTS`),
so a push touching only the advisor's state mirror publishes nothing today.

## WHAT DONE MEANS

No exit test was written for this item, so: done is

1. `tools/pages_publish_manifest.py` exists, is the only home for the fact, and builds the artefact.
2. The workflow uploads what that module builds, and triggers on the same list.
3. `startup_anchor_freshness` asks the manifest instead of carrying a hand-copied list, so
   *"a reader cannot be sent here"* becomes true again rather than being corrected in a comment.
4. A control that can fail for the right reason, mutation-proven, with a non-vacuity leg.

## PRE-REGISTRATION — written before any of it was measured

Two questions whose answers I do not know. Recorded here before running anything; the results are
appended below the line, right or wrong.

**Q1 — how much does the trigger change?** Over the last 500 commits on `main`, on what fraction
would the *current* `paths-ignore` filter fire, and on what fraction would the proposed inclusive
`paths:` filter fire?

> **Prediction.** The current filter fires on **more than 85%** of pushes. The reason is a
> misreading I expect to find in its own rationale: `paths-ignore` lists only `docs/` subdirectories,
> so every push touching `company/`, `tools/`, `tests/` or `site/` — which is nearly all of them —
> passes the filter and deploys. The 2026-07-11 audit that added it measured ~4,120 runs/month and
> attributed the churn to `docs/`; I predict the dominant term was never `docs/` at all.
> The proposed filter fires on **30–60%**: the publish cycle rewrites `docs/status/LATEST.md` and
> `docs/state/` on every run, and those are in the manifest by necessity.

**Q2 — what breaks that the URL scan cannot see?** How many *relative* markdown links inside the
published set point at a path the manifest excludes?

> **Prediction.** Between 5 and 20, concentrated in `docs/PROJECT_OVERVIEW.md` pointing into
> `docs/design/` (`design/ONE_FRAMEWORK.md` is visible on line 41 already). I expect none in
> `docs/status/` or `docs/reports/`, which are machine-generated from templates that use absolute
> URLs.

**Q3 — the control's non-vacuity, stated as a prediction because the prior finding's control shipped
green twice before it could fail.** I predict the "every referenced URL is inside the manifest" leg
passes on the first draft and is therefore worthless on its own, and that the leg which can actually
fail is the builder run over a fixture tree containing an unlisted directory. I will restore a real
excluded path and check the builder omits it before claiming the control works.

---

### RESULT (appended after measuring)

**Both quantitative predictions were refuted, one in each direction, and the second refutation is
what kept the manifest small enough to be worth having.**

**Q1 — REFUTED BOTH WAYS.** Over the last 500 commits on `main` (408 with a file list; merge commits
list none under `--name-only`, and are excluded rather than counted as zero):

| Filter | Fires on |
|---|---|
| current `paths-ignore` | **286 / 408 — 70.1%** |
| proposed inclusive `paths:` | **35 / 408 — 8.6%** |

I predicted >85% and 30–60%. The mechanism I predicted was right and the size was wrong on both
sides. `paths-ignore` names only `docs/` subdirectories, so every push touching `company/`, `tools/`
or `tests/` deploys a byte-identical artefact — that is the dominant term, exactly as predicted, and
it is 70% rather than 85% because more pushes than I expected touch nothing but ignored `docs/`
paths. The proposed filter is 8.6% rather than 30–60% because I assumed the publish cycle's
`docs/status/LATEST.md` rewrite lands in most commits; it does not — publish commits are a small
minority of the tree's commits. **An 8× reduction in workflow runs falls out of this landing as a
side effect, against a quota the 2026-07-11 audit measured at 206% of the free tier.** I did not
predict that and would not have claimed it.

**Q2 — REFUTED, in the direction of overstating.** I predicted 5–20 relative links escaping the
manifest. Measured across all **146** published markdowns: **exactly one** —
`docs/PROJECT_OVERVIEW.md` → `design/ONE_FRAMEWORK.md`, the file and target I named. So
`docs/design/ONE_FRAMEWORK.md` is a single named entry in the manifest and the other 908 design
documents are not published. Had the count been 20 the honest move would have been publishing
`docs/design/` whole, and the manifest would have been almost worthless.

**Q3 — CONFIRMED.** Every leg passed on its first draft, including the URL-coverage leg, which is
worth nothing on that evidence alone. Six mutations, each aimed at one leg:

| Mutation | Result | Caught by |
|---|---|---|
| builder copies `docs/` instead of the list | RED | `..._the_builder_omits_a_directory_the_manifest_does_not_name` |
| drop `docs/institutional/` from the manifest | RED | `..._every_published_link_is_in_the_manifest` |
| drop the relative-link target | RED | `..._every_relative_link_in_a_published_markdown_resolves` |
| workflow uploads `docs` again | RED | `..._the_upload_step_ships_the_built_artefact_not_the_docs_tree` |
| workflow trigger drifts from the manifest | RED | `..._the_workflow_trigger_is_the_manifest` |
| `trigger_paths()` collapses to `[]` | RED | `..._the_workflow_trigger_is_the_manifest` |

Every one was caught by the leg written for it, so none is the flattering reading where a different
leg happens to cover the mutation.

## THE SURPRISE, AND IT IS THE PART WORTH CARRYING FORWARD

**The sibling control landed four hours earlier went red — because this change made the code more
honest.** `test_a_stamped_page_at_the_pages_root_has_a_live_writer` derives the Pages root from the
workflow's own `path:` value, deliberately, and its docstring says why: *"so that narrowing the
upload (the open question in the finding above) moves this control's subject with it"*. It did
exactly that — `pages_root()` now answers `_pages` — and the control broke, because two of its legs
had quietly pinned today's answer underneath the derivation:

- `assert pages_root() == "docs"`, at the end of a leg whose actual subject is the three REFUSALS
  above it. Repaired to `assert pages_root()`: the leg's job is "and the real workflow is not one of
  them", and which directory it names has one home now, in the new control's build-step check.
- `frozen_pages(ROOT / pages_root(), ...)` — walking the repo tree, correct only while the artefact
  WAS a directory.

The second repair made the control *sharper*, which is the thing to notice. It now builds the
artefact the way CI does and walks that, so it measures what a reader gets rather than what happens
to sit in the tree. Checked at real inputs rather than by argument: a stamped orphan planted in
`docs/status/` (published) is **caught**, naming `_pages/status/ghost_pnl.html`; the identical file
in `docs/design/` (not published) is **correctly ignored**. Under the old arrangement the control
could not have told those apart, because both were served.

*A control keyed to the property goes red when the code improves only if something inside it is
still keyed to the answer.* Both offending lines predate this landing by four hours.

## THE SECOND SURPRISE: I HAD THE EVIDENCE AND READ THE WRONG OUTPUT

The first landing attempt was refused by `test_a_control_reads_python_as_code`, naming three new
census rows in the new control. I had run the census before committing, and I ran it **twice**:

- `census(REPO, paths=[<the two new files>])` — returned the three rows. Correct, and I read it.
- `check()` — returned `ADDED 0`. It walks `git ls-files`, and both files were still UNTRACKED.

I trusted the second. The first was on screen and said the opposite. *The substring census only
walks tracked files, so a new file's row first appears in the gate* is a known shape here, and
knowing it was not enough: what defeated it was a second reading that looked more authoritative
because it was the one the gate runs.

The remedy was a SHRINK in both places, never a `freeze()`:

1. `_referenced_pages_urls` now launders every file through `python_code_text.searchable()`, which
   **makes the leg truer rather than merely compliant**. A Pages URL in a Python comment is not a
   promise to a reader — `tools/couple_w2_11_d5.py` has one in a tombstone about a page that no
   longer exists — and counting it would let prose about a dead link demand the link be published.
   That is the identical fail-open that silenced the sibling control in 80e363721, where a log
   sentence describing a copy that had stopped happening counted as a live writer. Coverage measured
   after: 34 URLs, unchanged — the retrospective links survive via the generated `site/data/method.
   json` feed even though the generator's own f-string is now correctly read as code.
2. The two scopes reading the workflow collapsed into one `_spec()` helper. Two scopes doing one
   read is two rows saying one thing.

All six mutations were re-run against the rewritten control. Each is still caught by the leg written
for it. Dropping a manifest entry now also reds the trigger-drift leg, which is the mechanism
working rather than a flattering second catch: removing an entry changes `trigger_paths()`, and the
workflow's copy is then genuinely stale.

## WHAT LANDED

1. `tools/pages_publish_manifest.py` — the one home. `PUBLISHED`, `is_published()`,
   `trigger_paths()`, `build()`. Eleven entries, each carrying who sends a reader to it.
2. `.github/workflows/github-pages.yml` — `path: docs` → a build step plus `path: _pages`;
   `paths-ignore:` → an inclusive `paths:` derived from the manifest. Both old comments replaced
   with what the workflow actually does.
3. `tools/startup_anchor_freshness.py` — `_UNPUBLISHED` deleted, `is_published` imported. The third
   of the three misreadings, and the only one that was wired into a control. The 80e363721
   correction had rewritten its comment to be honest about being a churn list; that left the
   sentence true and the mechanism wrong, which is the worse half.
4. `tests/tools/test_the_pages_artifact_is_the_manifest_not_the_docs_tree.py` — eight legs.
5. `tests/tools/test_a_stamped_page_at_the_pages_root_has_a_live_writer.py` — the two legs above.
6. `tests/tools/test_startup_anchor_freshness.py` — its mirror of the prefilter walk follows.

**Measured at the landing: 179 files, 26 MB, from 10,068 tracked files and 273 MB.** No longer
served: 8,600 internal findings, 909 design documents, 282 observability logs, `docs/instructions/`,
`docs/review_gates/`, `docs/claude/`, `docs/snapshots/`, `docs/market_data/`,
`docs/domain_artefact_library/`, `docs/context-handshake-latest.md`.

## WHAT THIS DELIBERATELY DOES NOT DO

It does not judge whether the eleven published entries should each be public — only that they are
the ones the repo already points a reader at. `docs/direction/decisions.jsonl` and
`docs/status/SEAT_STRETCH_LOG.md` are internal-voiced documents that the front door links by name;
narrowing **that** is a content judgement about the anchor block, not about the transport, and it is
a different piece of work. Filed here rather than taken, because taking it would mean deleting
anchors the director reads.

It also cannot see a bare reference-style markdown link or an HTML `<a href>` inside a published
markdown. Stated in the module docstring rather than left for the next reader to trust.
