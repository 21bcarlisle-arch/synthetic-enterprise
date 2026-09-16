**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — read the departure run's answer) · **Class:** figures_on_a_superseded_clock

# The value-arms page publishes a book from an objective the company no longer runs

**2026-09-10. Found while landing the departure run's grading (`dd9dc9451`).** It is the reason the
drawn item's third leg — "carry the reading to `site/data/value_arms.json`" — was not done as
written, and this is what is actually wrong there.

---

## What is true on disk

`tools/generate_value_arms_data.py` reads
`THREE_ARM_PATH = docs/observability/value_cycle_ab_s1_three_arm.json`. That canonical artefact was
generated **2026-09-09T13:58:12Z** by producing commit **`8b846013e`**.

```
git show 8b846013e:company/pricing/value_based_renewal.py | grep -c departure_cost_gbp   ->  0
```

**Zero.** At `8b846013e` the renewal objective was `p × C × A` and a departure cost exactly
nothing. The departure term landed at `e1895d6c8`, which `8b846013e` precedes, and `e1895d6c8` is
an ancestor of HEAD. So:

* **HEAD's arm** charges the sourced £27.50 replacement cost for a departure.
* **The page's book** was priced by an arm that charged nothing for one.

Every figure on that page produced from the three-arm run — the realised net, the level/selection
split, the decision shape, the funnel — describes a pricing rule **the company has stopped
running**. Nothing on the page says so.

## Why this is the real defect and "carry the reading" is not the remedy

The item asked for the departure reading to be stated beside the leg it explains, as one draw
inside the ±£1,810.50 nine-seed spread. **A sentence about the departure run added to a page whose
figures come from the pre-departure run would be a pointer with two homes, false in one of them** —
the reader would meet a caveat about a book the page does not publish. That is the shape
`SEAT_FINDING_A_POINTER_SENTENCE_WITH_TWO_HOMES_IS_FALSE_IN_ONE_OF_THEM_2026-09-08.md` names.

The honest remedies are two, and both are bigger than a caveat:

1. **Promote the departure run to canonical** and regenerate. This moves EVERY figure on the page,
   not one leg, and it is a promote-by-copy with its own census and its own refusals
   (`SEAT_FINDING_THE_PROMOTE_BY_COPY_CENSUS_REFUSES_ON_THE_RECORD_OF_THE_DEFECT_IT_EXISTS_TO_CATCH_2026-09-09.md`).
   It is a decision, not a side effect of a grading commit.
2. **Or make the page name the objective its book was priced under**, so a reader can tell that the
   arm described is not the arm running. That is the smaller change and it is the one that fails
   closed.

**Recommendation: (2) first, then (1).** Naming the objective is a one-leg change that makes the
staleness visible immediately; promoting is the larger move and it should not be what makes the
page honest.

## Why LATENT and not BLOCKING

The page's `current_world.selection_leg` already withholds its verdict, publishes the nine-seed
family, and states that the quantity carries no sign. **The claim a reader takes away is not
currently wrong — it is "we cannot tell", which survives the objective changing underneath it.**
What is wrong is that the surrounding figures are attributed to a live arm and are not. That is
real and live; it is not refusing anything, and lane A already carries seven BLOCKING findings.
Filing it BLOCKING would stop the drain over something whose remedy is a run and a decision that
are both already ranked.

## What would settle it

`site/data/value_arms.json` naming the producing commit of the book it publishes **and** whether
that commit's objective is HEAD's. Both facts are already on disk — `producing_commit.commit` is in
the artefact, and the comparison is one `merge-base`. The page has the harder half already.

## The generalisable shape, since this is the second instance

An artefact records the commit that produced it — `producing_commit` exists precisely so a consumer
can tell which code a figure describes. **Nothing checks that the recorded commit's behaviour is
still the behaviour the reader will assume.** A run is stamped, promoted, and then the code it
measured is changed underneath the stamp, and the stamp keeps reading as provenance rather than as
an expiry. The stamp is not wrong; it is being read as a freshness claim it never made.
