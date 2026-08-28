**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `SITE13_the_baseline_comparison_carries_its_bound`

**Discharged:** `tests/tools/test_generate_value_arms_data.py::test_a_run_artefact_that_is_not_the_published_figure_WITHHOLDS_the_claim` — the independence half. The publish-lane question this document raises is NOT discharged and is restated below.

# The "supplier on this site IS the baseline" check passes only against a file the A/B run itself wrote

**Rank:** after the current Lane 0 delivery item. **Class:** R15 TAUTOLOGY, plus a pre-existing red
that wedges every commit touching `tools/generate_value_arms_data.py`.

**Found:** 2026-08-28, while landing the household side onto `/capabilities/`. Not fixed on sight
(SELF-INTERRUPT DISCIPLINE) — queued, with the evidence, because the fix is a judgement about which
run the site publishes and that is not the delivery item I was drawing.

## One line

`generate_value_arms_data._is_the_published_supplier` compares the A/B's control arm against
`docs/reports/run_output_latest.json` — and in the state where the two match, that file is the
A/B run's own output, so the check reads as independent and is not.

## Observed, with evidence

Working tree, 2026-08-28T14:2xZ:

```
docs/observability/value_cycle_ab_s1_three_arm.json   control arm net   159,423.497394
docs/reports/run_output_latest.json  (WORKING TREE)   total_net_gbp     159,423.497394   -> "same supplier"
docs/reports/run_output_latest.json  (HEAD, tracked)  total_net_gbp   1,529,288.583406   -> a 1.37M divergence
```

`git status` reports `docs/reports/run_output_latest.json` as **M** — the tracked file at HEAD is the
last *verified* published run (£1,529,289, the figure the shadow board and the front door carry), and
the working-tree copy is an A/B pass's output. Commit `466a47b9c` (14:17Z) states the publish lane's
position in terms: *"the site keeps serving the last VERIFIED run … no unverified figure published."*

So two things are true at once:

1. **The check is a tautology in the state that makes it pass.** `simulation.run_phase4c_on_phase2b`
   is the same entry point the A/B calls once per arm; when its output lands in
   `run_output_latest.json`, the "published run" the check reads IS the arm it is checking. The
   sentence the page renders — *"The net margin this site publishes for the company is the same
   figure, to the penny, as the flat-rules baseline arm below"* — is then true by construction rather
   than by measurement, which is the independence failure R15 names first.
2. **Against the run the repo actually publishes, the claim is false**, by £1.37M.

## Why nothing fired

`tests/tools/test_generate_value_arms_data.py::test_the_published_supplier_claim_is_true_today_and_checked`
does assert the match — and takes the WORKING TREE as its subject, so it passes on the overwritten
file and cannot see either reading above. In `tools/surgical_land`'s built tree (HEAD + the committed
pathspec, which is the tree the commit would create) it fails, along with the null rung inside
`test_a_divergent_published_run_is_reported_as_a_divergence`. That is the control working correctly
in the only tree where its subject is the published one.

## Consequence, and what it wedged

Any commit touching `tools/generate_value_arms_data.py` runs that file (`tests_for` maps a module to
`tests/**/test_<stem>*.py`) and is refused. The household-side work landed its producer, its renderer
and its render controls; the FEED half — `_household()`, its tests and the regenerated
`site/data/value_arms.json` — is held behind this red rather than landed by fixing someone else's
control or by committing an unverified 31 MB run output to make a test green. Neither of those is
mine to do.

## What the repair has to decide (not decided here)

- **Which run is "the published run"** for this check: the last verified publish (HEAD) or the newest
  pass on disk. The answer is the publish lane's, not this generator's.
- **An independent subject.** Whatever it reads must not be a file the A/B run can write. The nearest
  candidate is the publish provenance record (`site/data/publish_provenance.json`) naming the verified
  run's commit, with the net margin read from that commit's artefact — a figure the experiment cannot
  overwrite.
- **The test's subject** must move with it: a control over live state that reads the working tree can
  pass while the tree the commit would create is red, which is exactly what happened here.

## Left running, for whoever draws this next

A three-arm A/B (`--level-arm`) was launched detached at 2026-08-28T14:07Z writing to
`docs/observability/value_cycle_ab_s1_three_arm_rerun_2026-08-28.json`, log `/tmp/ab_household_rerun.log`.
It is the first run carrying `household_side` per arm, so it is what fills the column
`/capabilities/` now has a slot for. It was written to a NEW path rather than over
`..._s1_three_arm.json` deliberately: promoting it should follow a comparison of the control arm's
net against the live artefact's £159,423.50, not a blind overwrite of the figures the site
publishes.

Sequence when it lands: compare, promote if the control arm agrees, then land the held feed half
(`_household()` in `tools/generate_value_arms_data.py`, its tests, and a regenerated
`site/data/value_arms.json`) — which needs the red above resolved first, because the gate runs
`tests/tools/test_generate_value_arms_data.py` for both that module and the noise-floor artefact.

---

## CORRECTION AND CONFIRMATION from a second lane, 2026-08-28 (delivery seat)

**The independence failure is real and I had relied on it.** I re-ran the A/B this morning to
"resolve" a divergence, reported that the control arm reproduced the published run to 6.75×10⁻⁹,
and put that in a commit message and two NTFY messages. The file it reproduced was one my own run
had just written. **That inference was circular and I withdraw it.**

**One premise here is wrong, and correcting it changes the repair.** This document says
£1,529,289 is "the figure the shadow board and the front door carry". It is not. Fetched live:

```
https://poesys.net/data/dashboard.json   portfolio.net_margin_gbp   153,244.79
                                         generated_at               2026-08-28T06:59:27Z
HEAD  site/data/dashboard.json           portfolio.net_margin_gbp   153,244.79
HEAD  docs/reports/run_output_latest.json  total_net_gbp          1,529,288.58
```

**The site does not publish £1.53M anywhere.** It publishes £153,244.79 — this morning's A/B
control arm. So `run_output_latest.json` is not "the last verified published run" either; it is a
third figure that neither the site nor the A/B matches, and the check has been reading a file that
is not the published figure at all.

**Which makes the answer to "which run is published" available without the publish lane:** it is
whatever `site/data/dashboard.json` renders, because that is the number on the page. What is NOT
available without them is which run *should* be, and this change does not touch that.

## What landed here

`_is_the_published_supplier` now **withholds** the claim when the run artefact it reads disagrees
with the figure the site publishes, naming both numbers and the gap. Not answered from whichever
file is nearer — a third state, beside match and divergence. An unreadable dashboard leaves the
original comparison alone, because the refusal must fire only on a mismatch it can PROVE and
inventing one from a missing file is the opposite failure.

**Five controls had to move with it, and all five were pinned to today's answer rather than to the
property** — the same shape found twice elsewhere the same day:
`test_the_published_supplier_claim_is_true_today_and_checked` asserted `same_supplier is True` as
LIVE STATE and reddened on a feed that had become *more* honest; the two branch tests were driving
the match/divergence cases without saying what the site publishes, so they were exercising the new
refusal instead; and the reader-side control pinned one of what are now three answers. Each now
checks that the feed says the matching thing in whichever state it is in.

**Still open, and still the publish lane's:** which run the site *should* publish, and whether
`run_output_latest.json` at HEAD (£1.53M) is a stale artefact or a real supplier the site has
stopped reporting. This document is the record of that question; the change above only stops a
claim being made while it is unanswerable.

## Reversal

Nothing was changed. This document is the whole of the action taken.
