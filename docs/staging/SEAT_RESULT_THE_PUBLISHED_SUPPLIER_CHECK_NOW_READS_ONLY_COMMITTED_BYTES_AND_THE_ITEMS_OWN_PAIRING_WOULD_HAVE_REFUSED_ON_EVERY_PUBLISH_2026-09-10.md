# SEAT RESULT — the published-supplier check reads only committed bytes, the pairing the item asked for would have refused on every publish, and a HEAD red none of it caused is why the reader still cannot see it

**Severity:** RECORDED · **Lane:** H_harness

> **Status, up front, because the filename says "now reads" and the tree does not.** The repair is
> built, green on its own suite (183 passed) and mutation-proven six of six. **It is not landed.**
> `surgical_land` refused on three tests that are red at `38051c0c0` with none of it applied. What
> follows is true of the bytes, not of the published site. The section *THE CODE DID NOT LAND* has
> the evidence and the next move.

**Date:** 2026-09-10 (delivery seat, lane 0 draw)
**Claim:** `the-published-supplier-check-should-read-the-committed-dashboard-not-the-unpublished-run-output`
**Follows:** `docs/staging/SEAT_FINDING_THE_PUBLISHED_SUPPLIER_CHECK_INFERRED_ITS_SUBJECT_FROM_TWO_FIGURES_AGREEING_2026-09-10.md`
(items 2 and 3 of its STILL OPEN section)

---

## What was asked, and what is different about what was built

The item said: point `is_the_published_supplier` at artefacts that are actually committed —
**identity** from `site/data/publish_provenance.json` (`showing_run.git_commit` / `run_id`),
**net margin** from `site/data/dashboard.json` (`portfolio.net_margin_gbp`).

The money half is exactly that. **The identity half is not, and the reason is an ordering fact that
the pairing cannot survive.**

`value_arms.json` is generated inside `process_run_complete.generate_dashboard_json`
(`background/process_run_complete.py:4287`). `publish_provenance.record_verified` is stamped
**later in the same cycle** (`background/process_run_complete.py:8030`). So at the moment this feed
runs, the provenance still names the **previous** run. It is visible in the committed record, in one
commit:

| in `dceedff0f` | says |
|---|---|
| `site/data/value_arms.json` → `run_identity.showing_run_id` | `run_output_36e3ee8c4_20260909T210648Z.json` |
| `site/data/dashboard.json` → `meta.source_file` | `run_output_258720283_20260910T005624Z.json` |
| `site/data/publish_provenance.json` → `showing_run.run_id` | `run_output_258720283_20260910T005624Z.json` |

A gate keyed to `dashboard.meta` and `showing_run` **agreeing** would therefore have withheld the
claim on every publish — a guard that refuses everything, which is the control defect this project
has walked into by more doors than any other. It passes every test that asks whether it refuses
correctly.

**So the subject is `dashboard.json` alone**, which is the stronger artefact anyway: it carries the
figure and the run it came from (`meta.source_file`, `meta.git_commit`, `meta.git_commit_source`) in
**one committed file, written by one producer in one pass**. The money and the identity cannot be a
cycle apart. That is precisely the property the old pairing —
`docs/reports/run_output_latest.json` against `publish_provenance.json` — lacked.

**What survives the lag is the ORDER of the two runs**, and that is the one leg the provenance is
still read for: the dashboard's run must not have **started before** the last verified run. That is
lag-proof (a run stamped earlier is old however many cycles behind the provenance is), and it is
what makes item 3 of the finding **visible instead of silent** — see below.

## The oscillation is dead, and here is the control that proves it

`RUN_OUTPUT_PATH` is **gone from the module**, not demoted: the parameter, the plumbing through
`build()` and `generate()`, and the 54 test call-sites that passed it. The name now survives in
exactly one place in the producer's tests — a line of prose explaining why it is not a path any
more.

## The two defects the landing round found in the work it was landing

Both were in the build this turn inherited, both are the same shape, and **neither would have been
found by reading it** — a comment stated the property and the line under it did the opposite.

**1. A leg nothing could ask was published as a leg that passed.** Under the comment
`NOT ASKED IS NOT PASSED, AND IT IS ALSO NOT A REFUSAL`, the not-asked branch of
`_same_run_verdict` returned `"not_older_than_verified": True`. So a site that has never recorded a
verified run — and a dashboard whose run name carries no start time — published an unqualified pass
on the freshness leg. It is `None` now, with `order_not_asked_because` naming which of the two
cases it met. Caught by the poison round, by the build's own
`test_a_site_with_no_verified_run_says_the_ORDER_WAS_NOT_ASKED_rather_than_passing_it`, which had
never been run against the code it grades.

**2. The control on the central property was keyed to a proxy that passes for the exact path it
exists to refuse.** `test_every_input_to_the_published_supplier_claim_IS_IN_THE_PUBLISH_SURFACE`
ran `git ls-files --error-unmatch` over the inputs. But `docs/reports/run_output_latest.json` **is
tracked and is not gitignored** — it was committed once and is simply never re-committed, which is
the entire defect. Tracked-ness cannot tell "committed every publish" from "committed in March and
stale ever since". **Pointing `DASHBOARD_PATH` back at the run artefact SURVIVED the first
battery** — the mutation this whole repair exists to prevent, against the control written to catch
it. The control now reads the file list `process_run_complete.git_commit_push` actually builds, out
of its AST rather than by substring, because a path that merely appears in that source is not a path
that gets committed. It has a non-vacuity leg: an empty surface fails rather than passing everything.

## A third file was in the landing and was not in the build

`generate()` no longer reads `RUN_OUTPUT_PATH`, and
`tests/tools/test_the_value_arms_pages_undriven_pointers.py::_real_inputs` still named
`gva.RUN_OUTPUT_PATH`. Landing the producer without it is an `AttributeError` at collection for
every lane. Repairing it surfaced a second thing: that helper's docstring says *"The SIX artefacts
`generate()` reads, in its order. ALL SIX, and the count is load-bearing"* — and `generate()` has
read **seven** since `DEPARTURE_TERM_RERUN_PATH` landed on 2026-09-09. It was supplying six of
seven while asserting it named them all, so `_departure_statement`'s branches were being judged with
their own input absent. Both are fixed; the count is six again and now true.

## What the page WOULD say, and why it does not say it yet

Regenerated from the isolated bytes, against the committed `dashboard.json` and
`publish_provenance.json`, in a clean worktree at `38051c0c0`:

> The published run's net margin (£147,886.78) is NOT the baseline arm's (£147,954.26) — they
> differ by £67.48. The comparison below is between three arms of one A/B run and is no longer a
> statement about the supplier this site publishes elsewhere.

That is item 4 of the finding — **the £67.47** — and the committed feed today still says the
withheld sentence instead, citing a **£16,597.44** gap that was an artefact of the stale path and
not a divergence between anything.

**It is not on the page, because the code did not land.** See the next section. Everything above
this line is measured and reproducible; the reader has not met any of it.

## The precision caveat the item told me to check first, and it is NOT sound as stated

`dashboard.json`'s figure is `generate_dashboard_data._fmt`-rounded to 2dp; the tolerance is £0.01;
the baseline arm is full precision. Written out:

    published ∈ [true − 0.005, true + 0.005]    ⇒    observed gap o ∈ [d − 0.005, d + 0.005]

* `d ≤ 0.005` → always reads *same*. Sound.
* `d > 0.015` → always reads *different*. Sound.
* `d ∈ (0.005, 0.015]` → **the verdict is decided by which way the site's figure happened to
  round.** Not sound: a distinction neither figure carries.

**The repair is a third answer, not a wider tolerance.** Widening `SAME_SUPPLIER_TOLERANCE_GBP` to
swallow the band would buy agreement by knowing less, which is what the item warned against and what
this file's own history says never to do. Instead the two verdicts are stated only where the
rounding cannot change them, and the band between is published as its own result — *"the two differ
by £X, and the site publishes its own figure rounded to the penny, so a gap that small is inside
what this comparison can resolve"*. It costs nothing on the live question: the arms sit £67 apart.

## Item 3 — the mtime glob — is now DETECTABLE, though not repaired

`generate_dashboard_data._find_latest_run_json()` still globs gitignored
`run_output_*[0-9Z].json` and sorts by **mtime**, so outside the shared tree it can pick a June 2026
artefact for the site's headline. That is unchanged and remains a separate finding.

What changed: the order leg **catches it and names it**. A dashboard built from a run that started
before the last verified run now withholds the claim and says the mtime rule is why, instead of
comparing the baseline arm against a three-month-old figure in silence.

## Item 1 — the 27 MB question — no longer needs answering

The finding held it open as the director's call: add `run_output_latest.json` to the publish surface
at ~2.8 MB packed × 19 publishes/week ≈ 2.8 GB/year, on a figure no reader opens. **This route costs
nothing and removes the need**, which is why it was taken instead.

## Controls — poison round first, then the mutation battery

Poison round, in a clean `git worktree` at `38051c0c0` and never in the shared tree: **183 passed,
0 failed** on the producer's own suite before any mutation, because "survived" means two opposite
things and only a green baseline tells them apart. The two git-dependent controls cannot be graded
in a `git archive` extract at all — they read `HEAD` — and reading their failure there as a defect
is the measurement error this round started with.

| # | mutation | verdict |
|---|---|---|
| M1 | not-asked order leg published as `True` | **killed** — `..._says_the_ORDER_WAS_NOT_ASKED_rather_than_passing_it` |
| M2 | order leg written as equality (`mine != theirs`) | **killed** — `test_a_dashboard_NEWER_than_the_last_verified_run_is_the_ORDINARY_case_and_passes` |
| M3 | resolution collapsed to zero (third answer removed) | **killed** — `..._cannot_resolve_is_not_answered_either_way`, `test_a_penny_of_divergence_is_still_the_same_supplier`, `..._VERDICTS_are_stated_only_where_the_rounding_cannot_change_them` |
| M4 | subject moved back to the uncommitted run artefact | **SURVIVED first**, then killed — `..._IS_IN_THE_PUBLISH_SURFACE`, after the control was re-keyed off tracked-ness |
| M5 | `_run_started_at` fails open on `run_output_latest.json` | **killed** — `test_run_output_latest_is_NOT_A_RUN_and_the_order_leg_refuses_to_sort_it` (+1) |
| M6 | unresolvable band answered as *same supplier* | **killed** — `..._cannot_resolve_is_not_answered_either_way`, `..._VERDICTS_are_stated_only_where_the_rounding_cannot_change_them` |

The rows that matter most are M4 and M2. **M4 is the one that survived**, and it survived against
the control named for the property it violates — recorded here rather than quietly re-run, because a
battery reported only after it is green is not evidence the control was ever able to fail. M2 is
what reddens if the order leg is written as equality — the shape that would have refused on every
publish — and `test_the_two_VERDICTS_are_stated_only_where_the_rounding_cannot_change_them` is one
control over the whole three-way partition rather than a leg per branch, so a gate that returns
"unresolved" for everything cannot pass it.

## THE CODE DID NOT LAND, and the reason is a HEAD red that wedges this whole lane

`surgical_land` refused, correctly, and **not on anything this work broke**:

    [test-gate] ❌ TESTS FAILED -- COMMIT REFUSED.
    3 failed, 569 passed
    tests/tools/test_the_value_arms_pages_undriven_pointers.py

Those three are red **at `38051c0c0` with nothing of this landing applied**, and the two runs are
the same defect symbol for symbol — measured in two clean worktrees:

| | recipes missing | misdirected pointer | field no door renders |
|---|---|---|---|
| pure `HEAD` | `_against_the_panels_figure`, `_against_the_superseded_panel`, `_current_world_contrast`, `_publisher_bound_statement` | `_world_clause` | `_current_world_bound:5424` |
| `HEAD` + this landing | *identical four* | `_world_clause` | `_current_world_bound:5489` (same line, moved) |

**The coupling is what makes it a wedge, and it is worth stating plainly.** Removing
`RUN_OUTPUT_PATH` forces a change to `_real_inputs`, which lives in
`test_the_value_arms_pages_undriven_pointers.py`. The gate is path-scoped, so it selects that file,
and that file has been red at HEAD since before this claim existed. Other lanes land because they
never touch it. **So the published-supplier repair cannot reach the reader until that HEAD red
clears, however green its own suite is** — 183 passed, six of six mutations killed, and none of it
publishable.

**Why I did not clear it in this turn, which is a judgement and not an omission.** Three of the four
missing `_RECIPES` rows are the subject of another lane's uncommitted work in that same file
(`the-value-arms-page-must-stop-claiming-per-household-inference-it-cannot-evidence` adds
`_against_the_superseded_panel`, `_against_the_panels_figure` and `_bucket_reading`, with matching
`_REFERENTS` rows and a producer prose correction from "below" to "above"). Verified by running
their working copy with only the `_real_inputs` repair applied: it clears
`test_every_undriven_pointer_is_true_from_the_region_it_lands_in` and leaves the other two. Writing
my own rows for those three would be the fourth instance of *two lanes fixing one defect
concurrently* in this cluster, and a `_RECIPES` row asserted without understanding its branch is a
control that passes vacuously — the one outcome this project treats as worse than the red.

`_current_world_bound:5489` and the two genuinely unclaimed symbols (`_current_world_contrast`,
`_publisher_bound_statement`) are nobody's in-flight work and are the landable part of the remedy.

**The validated bytes are not in the tree and will not survive this turn.** They are
`/tmp/iso_producer.py`, `/tmp/iso_tests.py`, `/tmp/iso_pointers.py` and
`/tmp/regen_value_arms.json`, built by `tools/isolate_hunks.py` from `38051c0c0` — 10 of 24 producer
hunks, 58 of 60 test hunks. Rebuilding them is the same mechanical selection, and this document is
what makes that cheap rather than a re-derivation: **the two defects in the section above are the
part that cost the turn, and they are recorded here rather than in the bytes.**

## Reds that are NOT this landing's, proved rather than asserted

Three in `test_the_value_arms_pages_undriven_pointers.py`
(`test_every_untied_here_relative_literal_has_a_recipe_that_drives_its_branch` and two beside it,
all naming `_current_world_bound`), and two in
`site/test_the_baseline_comparison_reaches_the_reader.py` (the current-world mutation rungs, which
refuse because `current_world.is_the_later_run` is `False` on the committed runs). **All five
reproduce at `38051c0c0` with HEAD's own bytes**, in a clean worktree, with none of this landing
applied — the door pair re-checked with HEAD's `value_arms.json` written back over the regenerated
one. The regenerated feed drops nothing: `current_world.available` is `True` and
`is_the_later_run` is `False` in both the committed and the regenerated copy.

## What this landing deliberately did NOT carry

Four files in the value-arms cluster hold a **second lane's** uncommitted work
(`the-value-arms-page-must-stop-claiming-per-household-inference-it-cannot-evidence`): the
within-year concordance, the permutation null, `_renewal_objective_moved`, `_bind_asymmetry`, the
`WITHDRAWN_CLAIMS` row dated 2026-09-10 and the two test hunks that go with them. A pathspec commit
would have swept all of it into this claim. This was built through `tools/isolate_hunks.py` and
offered to `surgical_land --content` — HEAD plus this lane's hunks only, 10 of 24 in the producer
and 58 of 60 in its tests — which is the remedy
`SEAT_FINDING_THE_WHOLE_VALUE_ARMS_CLUSTER_IS_TWO_LANES_IN_FIVE_FILES_AND_A_PATHSPEC_LAND_DELETES_EITHER_HALF_2026-09-08.md`
asks for, on its fifth instance. `site/data/value_arms.json` was regenerated **from the isolated
bytes in that worktree**, never from the shared tree, because regenerating it here would have run
the other lane's uncommitted producer.

## What is NOT closed

1. **The subject is now SELF-stated.** `dashboard.json` says which run its figure came from and
   nothing independent corroborates that within this cycle. Stated rather than glossed: it is a real
   weakening against a two-witness test, and it is the strongest test available while the provenance
   lags. Moving `value_arms.json`'s generation to **after** `record_verified` in the publish cycle
   would restore the second witness; that is a pipeline change and is not made here.
2. **`_find_latest_run_json`'s mtime glob** — detectable now, still unrepaired.
3. **The £67.47 itself.** With the subject settled on every tree, the answer is that the supplier
   this site publishes is NOT the baseline arm — £67.48 on ~£148k (0.046%). Small enough to be
   re-run nondeterminism, 6,748× the feed's own tolerance. Nothing here establishes which. Still
   handed on.
4. **`_current_world_bound`'s unrendered here-relative pointer**, red at HEAD before this landing
   and red after it. Not this claim's, and now named in one place so the next lane to meet it does
   not re-diagnose it as their own.
