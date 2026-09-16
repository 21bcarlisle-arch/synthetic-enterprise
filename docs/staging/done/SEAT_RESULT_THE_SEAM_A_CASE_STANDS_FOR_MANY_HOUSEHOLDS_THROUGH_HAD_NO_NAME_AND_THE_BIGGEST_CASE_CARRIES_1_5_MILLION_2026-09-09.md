<!-- SUPERVISOR_DRAW: self-drawable -->

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
`W2_33_a_weighted_case_can_still_be_inflated_into_a_small_population`

# The seam a case stands for many households through had no name, and the biggest chosen case carries 1.58 million

**Built 2026-09-09**, delivery seat, on the LANE 1 BUILD draw of `W2_33`
(`W2_customer_generator`, dial 50, L0 → L2, `loop_stage: build`). The atom is item 5 of
`DIRECTOR_CANON_WHAT_THE_SYNTHETIC_BOOK_IS_2026-09-07`, §3.

---

## What the canon asked for, and why it is a control rather than a build

> *"Two things must remain reversible, and nothing may be built that forecloses them: a weighted
> case can later be **inflated into a small population** with within-group variation, once the
> physics is settled; the count on high-volume cases can be **raised** where a use case makes that
> worth doing. Neither is built now. Both must stay possible."*

A negative deliverable. Nothing is to be built, and what is asked is that nothing **else**
forecloses it — which an intention cannot hold, because the foreclosure does not arrive as a
decision to foreclose. It arrives as another lane's reasonable simplification, with a green suite,
in a lane that has never read this canon: an integer count, a 1:1 case-to-account join, a uniqueness
assumption on the roster. Every one of those looks like tidying up.

## The finding: there was no seam to guard

The canon's claim is that "a single household may carry the mass of tens of thousands". Measured
this tick, **the conversion that claim rests on did not exist anywhere in the tree.**
`demand_vector_coverage.fit_weights` solves for each chosen case's *share* of the population, and
that share reached `weighted_ks` and `accepts_weighted` and stopped. Nothing multiplied it by a
household count. So the property the canon rules reversible had no place it could be foreclosed
**and no place it could be asserted** — a case's household count was neither one nor many, it was
absent, and an absent quantity cannot be defended by a control.

That is why the first half of this work is a build after all: the seam had to be named before it
could be kept open.

## What was built

`tools/demand_vector_coverage.py`:

- **`case_household_counts(weights, households)`** — the seam. Weight → share → the number of
  households the case stands for. Four properties are stated in its docstring as the things that
  must stay true: a case's count is **not one**; the count is **linear in `households`**, so raising
  the count on a high-volume case is a change to one argument rather than to the design; the count
  is a **float, not an integer roster**, because rounding is the foreclosure wearing a tidy-up's
  clothes (0.4 households rounds either to 0 and vanishes from the aggregate, or to 1, which is the
  assumption the seam exists to keep open); and the **within-group variation slot is carried and
  empty**.
- **`WITHIN_GROUP_VARIATION_IS_UNSET_BECAUSE`** — the slot's honest reason. No published source
  resolves two households sharing a NEED row and a weather cell; the survey collapses them, which is
  the same limit that makes near-duplicates unchoosable in `choose_for_difference`. `None` with a
  named reason, not a spread invented to fill the slot.
- **`gb_households()`** — **27,291,846**, *counted* rather than transcribed:
  `weather_cell_weights.read_households` merges Census 2021 TS041 (England and Wales) with
  Scotland's Census 2022 over 235,243 output areas, and this sums it. Returns an honest `None` when
  the tables are off the machine, and `case_household_counts` propagates that `None` rather than
  defaulting — a machine without the census gets a stated absence, never a plausible count.
- **Wiring, so the seam is a path and not a docstring.** `smallest_n_chosen`'s verdict now carries
  `households_the_biggest_case_stands_for`, and `measurement()` publishes
  `gb_households_the_book_stands_for`, `within_group_variation` and its reason. The reversibility
  properties are on the report's own surface, so a rival mapping built elsewhere would be a visible
  second home rather than the only one.

## The number, printed at real inputs before the control was written

At `points=3,000`, `k=40`, seed 0, against HEAD's axis set:

| | |
|---|---|
| GB households counted | **27,291,846** |
| Cases carrying weight | 48 chosen, 44 with weight > 1e-9 |
| **Households the biggest case stands for** | **1,575,773** |

The canon says "tens of thousands". It is **millions** — at this k the biggest case carries 5.8% of
GB. That is the design working, and it is also the size of the mistake anyone makes who reads a case
as a household.

## The control, and its poison round

`tests/architecture/test_a_weighted_case_can_still_be_inflated.py`. The predicate `forecloses(rows,
doubled)` is keyed to the **property**, never to today's counts: it does not care how many
households the biggest case carries, only that a case is *permitted* to carry more than one and that
the total it is read against can be raised. Four reasons — `SLOT_ABSENT`, `SLOT_UNEXPLAINED`,
`ONE_HOUSEHOLD_PER_CASE`, `COUNT_NOT_RAISABLE`.

The atom's exit demanded a poison round, on the ground that *a control over a property nobody
violates today passes vacuously and "survived" would mean two opposite things*. It ran, against the
real fitted weights and not a fixture:

| Poison applied to the seam | Verdict |
|---|---|
| a case is one household (`households = 1.0`) | **KILLED** — 2 legs red |
| the variation slot deleted | **KILLED** — 3 legs red |
| the count rounded to an integer roster | **KILLED** — 1 leg red |
| an absent household total defaulted to 27,291,846 instead of `None` | **KILLED** — 1 leg red |
| the production call removed from `smallest_n_chosen` | **KILLED** — `test_production_reaches_the_seam` |

Five mutations, five kills, none survived. `test_POISON_every_way_of_foreclosing_is_refused` also
asserts the poison set is **onto** the reason set rather than merely that each poison is caught — a
reason added later without a poison reds immediately, so the partition cannot rot into a control
that refuses everything.

## What this control cannot see, stated because a blind spot read as coverage is worse than no control

It guards **this** seam. A lane that builds a *second, private* case-to-household mapping elsewhere,
rather than changing this one, forecloses the property without reding anything here. The only
defence is that the seam is now named and reported on `measurement()`'s own surface, so a rival
mapping is discoverable as a second home. That is the same class as
`SEAT_RESULT_THE_SCALAR_COPY_CENSUS_RANKS_ITS_OWN_POISON_FIRST_AND_FOUND_FOUR_MORE_HOMES_FOR_PUBLISHED_LAW_2026-09-08`,
and if it recurs here the answer is that census, not a wider regex.

## Landing note: the file carried two lanes

`tools/demand_vector_coverage.py` held **11 hunks against HEAD** when this work began; seven were
another lane's uncommitted `seasonal_swing` removal (2026-09-09), and four were mine. A pathspec
commit would have carried their unlanded work inside mine. Landed via
`tools.isolate_hunks --keep 8..11` into HEAD-plus-my-hunks-only bytes and
`surgical_land --content`, and the control was run against **those exact bytes** before landing
(all five legs green, biggest case 1,575,773) rather than against the shared tree — a green test in
the shared worktree measures several lanes, not this change.

## What is next

Not folded into this atom, named here instead:

1. **`tools/stock_joint_generator.py` still has no test file at all** — carried forward from
   `PLANNER_MINTED_the_synthetic_book_canon_is_two_thirds_built_...`, which named it and declined to
   fold it into 4 or 5. It belongs to deliverable 1's own row.
2. **The inflation itself is still unbuilt, correctly.** When a use case makes it worth doing, the
   remainder rule for turning a float count into an integer roster is the decision this seam
   deliberately does not make for whoever inflates.

— Delivery seat, 2026-09-09.
