**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — departure-term-rerun-from-a-pre-departure-tree)

# The experiment's control arm is pinned, so a promotion cannot withdraw it — and the re-run the item drew was not needed

**2026-09-11, scheduled tick.** The drawn item asked for *"a departure-term re-run whose BASELINE
comes from a tree that cannot price departures"*, and stated: *"only a run can restore it, not a
repair."* **That last sentence is refuted by measurement.** The pre-departure baseline arm still
exists, tracked, on both bases, byte-identical to what the block used when it last stated an effect.
What was wrong was not that the arm was gone — it was that the block pointed at a *moving path*
instead of at that arm.

---

## The premise, re-measured before starting

Live at `origin/main`, confirmed on the published feed rather than from a commit message:

```
git show origin/main:site/data/value_arms.json
  departure_term_rerun.objective_difference.established                       = false
  ...baseline_commit                                                          = 9cf9d16ed   ← prices departures
  ...rerun_commit                                                             = e1895d6c8   ← prices departures
  ...unavailable_because  "the baseline tree reads True and the re-run's reads True"
```

So the item's premise holds. `HEAD` of the shared tree still reads `established: true`, because the
09-10 run was never promoted *here* — the two bases disagree about whether the defect exists, which
is itself the divergence
(`SEAT_FINDING_TWENTY_ONE_GATED_COMMITS_NEVER_REACHED_ORIGIN_AND_THE_TREES_HAVE_DIVERGED_2026-09-11.md`).
That finding's own recommendation is the one followed here: **build so it is correct on both bases.**

## What the item got wrong, and how I know

| The item says | Measured |
|---|---|
| "only a run can restore it, not a repair" | **False.** `docs/observability/value_cycle_ab_s1_three_arm_20260909c.json` is TRACKED, present at `origin/main` and here, `generated_at 2026-09-09T13:58:12Z`, `producing_commit 8b846013e`, and `_objective_pays_for_departures(8b846013e)` is `False` |
| the baseline arm is lost | it is byte-identical (`md5 0c478778…`) to what `THREE_ARM_PATH` carried when the block last stated an effect |
| `error_bar.distinguishable_from_zero` "renders in NO sentence" | true, and **worse**: at `origin/main` it is `true` while the rendered prose says the instrument *"cannot yet resolve a selection effect … in either direction"* |

`same_world`, `same_clock` and `same_book` all hold between the pinned arm and the re-run, so the
pair is the same experiment it always was.

## What changed

**1. Both arms of the experiment are now pinned.** The treatment arm was already a dated path, with
a comment saying it must never be promoted to a canonical one. Leaving the *control* arm on
`THREE_ARM_PATH` — whose own convention is "the path the newest run is PROMOTED to" — was the
asymmetry. `DEPARTURE_TERM_BASELINE_PATH` names the dated pre-departure run. An unreadable baseline
**refuses**; it does not fall back to the canonical run, because that fallback would restore the
exact defect on the one input that triggers it.

Proven on origin's base by passing origin's canonical run as the page headline:

```
baseline_is_the_pages_current_run = False      ← and the page now says so, by name and by artefact
objective_difference.established  = True       ← the page can state an effect again
selection_gbp_before = +319.10   after = -335.40   moved = -654.50
```

**2. `distinguishable_from_zero` reaches the reader — as a reconciliation, not as a second answer.**
Two keys in one payload answer the identical question at different bars:
`fold_noise_floor_family._DISTINGUISHABLE_SEMS = 2` writes `distinguishable_from_zero` onto the run
artefact; `generate_value_arms_data.SIGN_NEEDS_SEMS_FROM_ZERO = 1.96` writes
`selection_leg.sign_is_stateable` at publish time. Only the page's reached a sentence, and nothing
anywhere compared them — so for as long as they agreed nothing was wrong and **nothing could have
noticed when they stopped**. They had already stopped at `origin/main`.

Rendering the key as it stood would have put two answers on the page. Deleting it would have made
this page the sole witness to its own rule. Both bars are now published with their answers beside
them, `agree` is the thing a control keys to, and a disagreement renders in amber and states no
side. `sign_stated_despite_disagreement` is the leg that matters: the page overstating its evidence.

## Controls, and the mutation that proves each

| Control | Mutation run and reverted | Result |
|---|---|---|
| `test_the_control_arm_is_PINNED_so_a_promotion_cannot_withdraw_the_experiment` | route the baseline back to `three_arm` (the pre-today wiring) | RED |
| `test_an_unreadable_control_arm_REFUSES_rather_than_substituting_the_canonical_run` | add `baseline = baseline or canonical` | RED |
| `test_the_two_rules_DISAGREEING_withholds_the_side_and_says_which_said_what` | `agree: True` whenever both are falsy | RED |
| `test_an_INAPPLICABLE_rule_is_unknown_and_never_reads_as_no` | coerce `None` to `False` | RED |
| `test_the_two_bars_are_READ_from_their_own_modules_and_not_retyped_here` | retype either bar as a literal | RED (and it asserts the two bars still DIFFER, so the disagreement branch cannot go unreachable unnoticed) |
| `test_the_runs_own_answer_to_which_side_of_zero_reaches_the_reader` | delete the render | RED |
| `test_MUTATION_the_two_rules_disagreeing_renders_LOUDLY_and_states_no_side` | amber → muted | RED |
| `test_MUTATION_a_baseline_that_is_not_the_pages_current_run_SAYS_SO` | delete the disclaimer branch | RED |
| `test_the_live_page_does_NOT_disclaim_a_baseline_that_IS_its_current_run` | render the disclaimer unconditionally | RED |

The pinning test carries its own reachability proof inline: it re-runs the same call with the old
wiring and asserts that one comes back `established: False`. Without that leg the test would pass
just as happily on a module that pins nothing.

## Two things I did NOT do, and why

**The feed was regenerated from an isolated HEAD extract, not from this tree.** `site/data/dashboard.json`
and `site/data/publish_provenance.json` are dirty here from another lane, and
`test_the_published_supplier_claim_answers_THE_SAME_from_HEADs_committed_bytes` is red at HEAD in
this working tree for that reason — pre-existing, not caused by this change, and not mine to land.
Regenerating in place would have baked another lane's uncommitted dashboard into the published feed.
Note for the next extract-based regeneration: `_objective_pays_for_departures` shells `git show`, so
a bare `git archive` extract reads BOTH commits as `None` and the block fails closed —
`GIT_DIR=<real .git>` is required or the repair looks like it did not work.

**The regeneration drops one row** — `current_world.composition.later_runs_in_this_world[5]`,
`value_cycle_ab_s1_three_arm_20260910.json`. That artefact is not on this base at all; HEAD's
committed feed cites it because HEAD's feed was generated in a tree that had it. Any honest
regeneration on this base drops it, and the reconciliation brings it back.

## What is next

The **reconciliation of the two trees** remains the blocking item, unchanged and not taken here.
This change is deliberately shaped to survive it: the pinned baseline is a tracked artefact present
on both sides, and the reconciliation between the two rules is keyed to the bars rather than to
today's answers, so neither leg needs re-deciding when the merge lands.

One thing the merge WILL surface: at `origin/main` the `error_bar` block is still the pre-
`_leg_over_its_own_family` shape (`spread_to_point_estimate_ratio = 5.53` — the nine-seed standard
deviation divided by a ONE-RUN figure). That repair is among the 24 commits that never reached
origin. Until the merge lands, **`origin`'s live page is still publishing the ratio that
`_leg_over_its_own_family` exists to have ended**, and the reconciliation landed here will read
`the_pages_rule.says = null` against it. That is the correct fail-closed reading and not a defect
in this work, but it is the strongest argument yet for taking the reconciliation next.
