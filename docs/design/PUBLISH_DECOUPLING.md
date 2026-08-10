# The site breathes — publish freshness decoupled from HEAD perfection

**Ruling:** `docs/staging/done/DIRECTOR_RULING_PUBLISH_DECOUPLING_2026-08-10.md`
**Sequencing:** `docs/staging/DIRECTOR_PRIORITY_BUILD_THE_BREATHING_2026-08-10.md` ("stop winning
wedges, change the game" — items 1 and 3, before any other draw)
**Built:** 2026-08-10. **Modules:** `background/publish_scope.py`,
`background/publish_provenance.py`, `site/assets/freshness-banner.js`, wiring in
`background/process_run_complete.py`.

## PURPOSE — why this exists at all

Publishing asked one question — *is the entire repo green at HEAD?* — and used the answer to a
different one: *may the site update?* In a repo this size something is always red, so
"publish iff everything is green" is in practice "publish rarely", and the published stamp sat
at **2026-08-09T12:41:51Z for 25 hours** while ~18 distinct causes were each cured and each
re-wedged within the hour. Curing wedges one at a time is structurally unwinnable; the
conflation is the defect, not any individual red.

Worse than the staleness was the **silence**. From outside, a site frozen because verification
is paused, a site frozen because the machine is dead, and a site that is simply current are the
same page.

## GUARANTEES — what a reader of the live site can now rely on

1. **Newest-verified always flows.** The site serves the most recent snapshot that passed its
   scoped verification, stamped with run id, verifying commit and verification time — rendered
   on the page, not buried in a log.
2. **The gate is scoped to what it protects.** Publishing blocks on the tests that transitively
   import the code producing or rendering a published number. Reds elsewhere **annotate**
   ("published with N open findings … the suite that produces and renders these figures is
   green") and never block.
3. **Behind, never frozen, never silent.** When the scoped gate is red, the content commit is
   still refused — but the banner alone is pushed, so the page says *"verification paused since
   T · showing run R (last verified …)"*. A visitor can always tell what they are looking at and
   how current it is.

## THE WHOLE, not three patches

Three parts, each with one job, no shared state beyond one JSON file:

| part | owns | may not |
|---|---|---|
| `publish_scope.py` | which tests may BLOCK | silence anything; it narrows blocking only |
| `publish_provenance.py` | what the page SAYS about freshness | advance freshness outside a completed verified publish |
| the remainder pass (`process_run_complete.run_remainder_annotation_step`) | measuring what no longer blocks | affect the publish it follows |

`site/data/publish_provenance.json` is deliberately **not** a key inside `dashboard.json`: the
banner must reach origin on exactly the cycles the dashboard must not. Sharing a file would make
publishing the banner mean publishing the unverified numbers with it.

## WHY DERIVED, NOT LISTED

The blocking scope is computed every run from a declared list of **source modules** (the publish
path) through the static import graph in `tools/select_impacted_tests.py` — not from a
hand-written list of test paths. A name-keyed list goes blind the moment a test is renamed or
moved, and goes blind *silently*: it still resolves, just to less than it used to
(`feedback_control_keyed_to_one_syntactic_form`). Selection follows imports, so a renamed test
stays selected and a new test that exercises the dashboard generator is selected the day it
lands.

Measured 2026-08-10: **130 blocking test files of 1,190** (11%).

## R15 — HOW EACH CONTROL FAILS

Every failure path of the scoping degrades to **today's behaviour** (the full gate). The worst
case of this machinery breaking is the wedge we already had, never a broken surface published
quietly. Mutation-proven in `tests/background/test_publish_scope.py`:

* **unmappable / missing declared source → full suite** — a rotted declaration cannot narrow;
* **vacuity guard (< 20 files) → full suite** — a collapsed scope is green over nothing, which
  reads exactly like green over everything (`feedback_population_control_needs_a_vacuity_guard`);
* **selector unavailable → full suite** — an unavailable check is a FAILED check;
* **the differential** — a publish-path test *is* in the scope, and a doc-drift test is not.

The provenance recorders are proven against the ruling's named **cardinal sin, fake-fresh**
(`tests/background/test_publish_provenance.py`): `record_paused` called forty times leaves
`showing_run`/`last_verified` byte-identical, and `paused_since` is stamped at the *transition*
only — a banner reading "paused since 30 seconds ago" for 25 hours is the same sin wearing the
opposite coat. A corrupt or missing file reads as PAUSED, never VERIFIED.

The banner layer **fails loud**: a fetch/parse failure renders "Freshness unknown — provenance
unavailable" and records the fault on `window.PoesysFreshness.error`, because the natural
failure of a freshness widget is to render nothing while the page looks confidently current.

## R11 — NO ORPHAN TRANSITIONS

Narrowing what blocks is only honest if the rest keeps being measured. The remainder pass runs
the **full gate unchanged** after the publish, on an hourly self-throttle, and writes its reds
into the published annotation. Deselected from the blocking gate never means covered by no gate
(`feedback_deselecting_a_marker_orphans_the_tier`). It is deliberately *not* computed as "full
minus scoped": that would make the scope's blind spot the annotation's blind spot too, so an
over-narrow scope would be invisible in both.

The pause has a tested RELEASE: recovery clears `paused_since` and advances the served run.

## EXIT TEST (the director's own)

*"A deliberately-injected unrelated red (e.g., a doc-drift) produces a PUBLISHED site with an
honest annotation — never a frozen stamp."* — `tests/background/test_publish_decoupling_exit.py`,
both halves: the unrelated red cannot reach the blocking argv but IS in the remainder and on the
page; a publish-path red still blocks the content and publishes the banner alone (asserted on the
committed pathspec, so no figure can travel with it).

## WHAT THIS DELIBERATELY DOES NOT CHANGE

The heavy ignores (speed) and the `operational`/`join_report_only`/`scale_report_only` marker
deselections (scope) are untouched and apply to both runs. The gate's subject is still a clean
checkout of HEAD (`DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09`). Nothing here can turn a red
publish-path test green.

## KNOWN BOUND, stated rather than papered over

The banner commit runs the repo's **pre-commit hook chain**, like every other commit. Two of
those hooks can refuse it:

* `site_lane_gate.py` fires on `site/data/**` and runs `pytest site/`. This one is *coherent*,
  not hostage-taking: the banner is itself a site surface, and a red site suite means the thing
  that renders the banner may be broken. Measured green, 586 passed, 2026-08-10.
* `pre_commit_test_gate.py` lints the working tree, so an unrelated lane's uncommitted work can
  in principle refuse the banner too (`feedback_gate_lints_working_tree_so_uncommitted_wedges_
  everyone`).

So the guarantee is honestly stated as: **when the banner commit is refused, the publisher says
so in the log with the hook's own stderr** (`_publish_provenance_banner` logs anything that is
not the expected "nothing to commit"). It does not fail silently, and it never takes the publish
down with it. Making the banner's own path hook-independent is the obvious follow-on and is
NOT done here — hook bypass is a WALL (2026-08-09 ruling), so it needs a designed narrow path,
not a `--no-verify`.

## FOLLOW-ON (normal priority, per the sequencing doc)

Ruling item 2's full annotation panel (a `/health` surface the banner links to) and polish.
