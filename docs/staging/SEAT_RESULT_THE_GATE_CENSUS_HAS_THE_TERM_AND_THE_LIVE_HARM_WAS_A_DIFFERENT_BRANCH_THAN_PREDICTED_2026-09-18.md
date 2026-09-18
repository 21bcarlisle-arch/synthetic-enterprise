**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# The product-gate census has the guard's unit, and the live harm was a different branch than either the finding or the drawn item predicted

**Filed:** 2026-09-18 · **Claim id:**
`the-product-gate-census-answers-per-record-while-the-guard-refuses-per-term`
**Pre-registration:** `docs/staging/PREREG_WHAT_THE_PER_TERM_GATE_CENSUS_MOVES_ON_THE_ARMS_PAGE_2026-09-18.md`
**Discharges the remedy in:**
`docs/staging/done/SEAT_FINDING_THE_PRODUCT_GATE_CENSUS_ANSWERS_ON_THE_OPENING_TERM_WHILE_THE_GUARD_REFUSES_PER_TERM_AND_ONE_ARTEFACT_SAYS_BOTH_2026-09-18.md`

---

## State in one line

The unit repair is **built, mutation-proven and landed**. The six controls blocking the republish
and the promotion of the 09-18 artefact are **not done** and are handed on. The drawn item's own
order put the unit first and said to land the part that finishes; this is that part.

## The duplicate-work check, answered before building

The draw named `reconcile-the-fork-and-take-the-repair-that-is-already-on-the-branch` as possibly
this work, because it already holds `tools/run_value_cycle_ab.py`. **It is different work on the
same file.** Its draw record's `named_paths` are `background/boot_sha.py`,
`background/process_run_complete.py`, `docs/design/maturity_map.yaml`, two noise-floor test files,
`tools/wait_for.py` and that module — a fork reconciliation whose subject inside it is the
**noise-floor family**, not the renewal funnel. Its claim binds no paths, so nothing of it has
landed. Disposition: carry on. Not `--landed-under`, not `--release`.

## P1, P3, P4 — HELD, to the digit

Every figure below was written into the pre-registration before the module existed, derived by hand
from `by_account_class.classes[*].stages`.

| | predicted | measured |
|---|---|---|
| 09-18 `drawn_by_the_curriculum` decisions / priced | 42 / 42 | **42 / 42** ✓ |
| 09-18 `won_by_the_funnel` decisions / priced | 54 / 51 | **54 / 51** ✓ |
| 09-18 found decisions / priced / share | 96 / 93 / 0.969 | **96 / 93 / 0.9688** ✓ |
| 09-18 found decisions as a share of offered | 3.5% of 2,752 | **0.0349** ✓ |
| 09-10 found decisions / priced / share | 263 / 198 / 0.753 | **263 / 198 / 0.7529** ✓ |
| 09-10 unresolved caveat present | yes (158) | **yes, 158** ✓ |
| 09-18 unresolved caveat present | no | **None** ✓ |
| the "book size, not eligibility" clause leaves the live page | yes | **yes, on both artefacts** ✓ |

**P5 HELD.** The three `test_the_renewal_funnel.py` legs are repaired by the field **rename
alone**; not one assertion changed. Their null rung is untouched — what they assert is that the
census's verdict can come back both ways, and it still can.

## P2 — HELD, and the reading is unflattering in a direction I had not expected

The arm prices **96.9% of the decisions that existed** for a found household. What bounds the
experiment is that only **3.5%** of the boundaries the world offered the found book presented a
decision at all. I had gone in expecting the honest number to embarrass the *method*; it does the
opposite and embarrasses the *page*, which had been calling a 3.5% eligibility surface a book-size
problem. The determination's own closing claim — the reachable surface is about a third of a
domestic book and that is market structure — is what the page now says, derived.

## THE REFUTED PREMISE, and it is the most useful thing in this turn

**Both the finding and the drawn item located the harm in the wrong branch.** Both say the page's
sentence turns on `a_found_account_can_reach_the_product_gate`, via the branch
`measured and gate_reachable and not won_priced`. **That branch cannot fire on either artefact**:
`won_priced` is non-empty in both (09-10 priced 90 found accounts, 09-18 priced 59). The wrong-unit
boolean does not flip either run's verdict and I will not claim it did.

What fires is the `won_priced` branch, whose published clause is:

> "The gate that used to refuse every won household is passable, so **what limits this experiment
> now is book size, not eligibility**."

That clause is on the live page **today**, under the 09-10 run, where **1,475 of 1,975** renewals
offered to found accounts (74.7%) stopped at the product gate. It is the same defect the finding
named — a conclusion about eligibility drawn without counting per term — and it is the clause that
licenses "grow the book". So the finding's *diagnosis* was right and its *instance* was wrong,
which is the in-repo-finding class this project already has a memory for. The repair is in the
branch that fires.

**Consequence worth naming:** had I trusted the item's branch, I would have repaired an
unreachable code path, landed it green, and left the false clause on the page — with a commit
message saying the defect was closed.

## What landed

`tools/decisions_by_account_class.py` — the decision population split by how each account joined
the book, on the **TERM**. Producer and publisher both call it, the shape
`tools/product_gate_refusal.py` and `tools/decisions_that_existed.py` established here, so an
artefact written weeks ago still gets a reading. The membership rule is **not** re-implemented:
`decisions_that_existed` is called once per class over that class's own stage counts.

It publishes the two ratios that were being conflated, and says which binds — derived, not typed:

* `priced / decisions_that_existed` — about the **METHOD**
* `decisions_that_existed / offered` — about the **BOOK'S PRODUCT MIX**

A book twice the size scales both sides of the second and cannot move it. So "book size" is refuted
by **arithmetic**, not by a better sentence.

The two blocks no longer share a verdict field:
`a_found_account_can_reach_the_product_gate` → `a_found_accounts_opening_product_is_upliftable`,
`found_accounts_the_guard_would_admit` → `found_accounts_whose_opening_product_the_guard_admits`.
**Renamed, not deleted.** The per-record census still earns its place — only it can see the
defeated default (`tariff_type` present-and-`None`) and two legs of one billing account answering
differently — and a reader still on the old spelling now fails **closed**. The publisher
deliberately refuses the old spelling as a fallback: reading it would restore the silent wrong-unit
read this repair closed.

## A fail-silent in my own module, found by my own control

`_class_funnel` built its stage list from `FUNNEL_STAGES` alone, so a stage the producer had grown
was **dropped** before `decisions_that_existed` could refuse it — and the class's counts still
summed, so the partition check was blind to it as well. Two guards, one hole, and the module would
have gone on answering over a population silently missing a guard: exactly the defect
`decisions_that_existed` exists to refuse one level down. It now passes every key the producer
wrote.

**And the control that found it was broken first.** Its first draft monkeypatched `FUNNEL_STAGES`
on `value_based_renewal`, which reaches neither module — both bind the name with
`from ... import` — so it proved nothing and failed for the wrong reason. The stage is now planted
in the **data**, which is where a real producer would grow one.

## Eight mutations proven to fire

Each on the leg that claims it, applied one at a time and reverted:

| mutation | leg that reds |
|---|---|
| hardcode either branch of "which ratio binds" | `..._which_ratio_binds_is_read_off_the_numbers...` |
| drop the found-class filter from the `found` aggregate | `..._a_founder_only_run_carries_no_reading...` |
| divide an empty population to `0.0` | `..._no_decision_at_all_is_not_read_as_the_method_failing` (+1) |
| revert `_class_funnel` to `FUNNEL_STAGES` only | `..._the_membership_rule_is_not_re_implemented_here` |
| drop the partition check | `..._stages_do_not_sum_to_its_own_total_is_named_and_withheld` |
| drop the per-class unresolved caveat | `..._cannot_be_attributed_to_a_class_and_it_says_so` |
| restore "book size, not eligibility" | `..._never_concludes_book_size_from_a_priced_account_list` (+1) |
| drop the publisher's fail-closed availability check | `..._no_per_class_split_refuses_the_limit_claim...` |

**No control asserts today's answer.** None says the product mix binds, that the found population
is small, or that the priced share is high. A run in which the method becomes the binding
constraint turns the other branch green and reds nothing.

## Open, and honestly open

The finding left one edge open — whether any reader of `product_label_by_account_class` already
re-counts per term downstream. **I closed that one**: `grep` finds exactly two readers, both in
`_who_the_method_has_priced`, and no site JavaScript reads the field. **I have not** enumerated
every reader of `by_account_class.classes[*].stages`, which is the same class of edge one level
across, and it is the refutation route for everything above.

Seven `tests/architecture/` legs are red in this worktree. **None is mine** — they name
`_CEILING_PROBE`, `tools.validate_weather_world`, switching-rate commons candidates, and five
tree-scan controls in files this turn did not touch. They are part of HEAD's 41 owed.

## Owed, in order

1. **The six controls blocking the republish.** The two established ones are fixture-precondition
   inversions, not assertion failures: `test_the_error_bar_bounds_the_FIGURE_THE_HEADLINE_STATES`
   asserts `eb['available']` before reconciling and the new feed makes the bar correctly REFUSE, so
   the repair is a second assertion on the refusal path;
   `test_a_floor_drawn_over_a_DIFFERENT_book_is_refused_however_recent_it_is` asserts
   `_staleness_caveat(floor, three_arm) is None` as its precondition at line 563 and the 09-18 run
   is newer than the floor, so derive `_floor_declaring`'s stamp FROM the run instead of pinning it.
2. **Promote the 09-18 artefact** to `THREE_ARM_PATH` (`tools/generate_value_arms_data.py:166`) and
   regenerate `site/data/value_arms.json`. It is now safe to do so underneath a verdict that agrees
   with its own funnel, which was the sequencing reason the finding gave for blocking.
3. **Thread staleness into `_leg_over_its_own_family`** as a required parameter (carried over).
