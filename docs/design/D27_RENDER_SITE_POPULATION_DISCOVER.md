# DISCOVER — D27: the census sees neither of the two constants that pick the render sweep's books, and the headline's carrier is piecewise constant in book size

**Atom:** `D27_belief_window_saturates_on_this_book` (lane D_billing_metering, L0, `loop_stage: idle`)
**Stage:** DISCOVER only. **No BUILD code was written** — the atom is epoch-parked and BUILD-gated
(`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1). Nothing here is landed in `tools/couple_w2_11_d5.py`.
**Date:** 2026-08-15 (worker tick, DISCOVER/FRAME lane; third DISCOVER pass on this atom)
**Takes:** `docs/design/D27_SCORING_SIDE_CONSTANT_CENSUS_DISCOVER.md` §4 criterion 1 — *"The census's
subject includes the scoring side. `scenario_constants()` gains a sibling deriving the constants the
published-figure path reads — off the AST, never hand-listed."* That criterion was written with a
**worked AST rule** attached (§6, `ast.Assign` + `isupper()` + `not startswith("_")`). This pass ran
that rule against the module before anyone builds it, per the standing lesson that *a finding's
proposed control may be false because of a sibling defect*. It is false here, in two ways, and the
second one leads to a measured defect in a shipped control.

---

## 1. The proposed subject rule cannot see 50 of the module's 71 constants (R9: observed)

The rule the previous pass wrote out walks `tree.body` for `ast.Assign` whose target is a `Name` that
`isupper()` and does not start with `_`. Measured on the shipped module, AST only, nothing scored:

| | count |
|---|---|
| `ast.Assign` module constants (UPPER, incl. `_`-prefixed) | 44 |
| `ast.AnnAssign` module constants (UPPER, incl. `_`-prefixed) | **27** |
| visible to the proposed rule (`ast.Assign`, public) | 21 |
| today's census subject (`scenario_constants()`) | 8 |

Two independent blind spots, both of which the proposed criterion inherits:

* **Annotated assignment.** `X: Tuple[...] = (...)` is `ast.AnnAssign`, not `ast.Assign`. Twenty-seven
  module constants are declared that way — including `DIMENSION_DRIFT_RESOLUTION`, `ORGAN_QUERY_GRID`,
  `PUBLISHED_GAP_CONSUMERS`, `COUNTERFACTUAL_KNOB_ROUTE` and, with a straight face,
  **`SCENARIO_CONSTANT_CENSUS` itself**: the census's own register is invisible to the subject rule
  proposed to extend the census.
* **The leading underscore.** Twenty-three UPPER constants are `_`-prefixed. The rule drops them by
  name convention, which is a statement about *audience* and not about *whether the published path
  reads them*.

Neither is a hypothetical filter. The two constants that decide the population of the D35/D36 render
sweeps sit one on each side of the pair:

* `_RENDER_SITE_SEEDS = (7, 11)` — private (`ast.Assign`), invisible to the rule.
* `_PUBLISHED_BOOK_SPECS: Tuple[Dict[str, int], ...] = ({"n_customers": 150, "months": 6},
  {"n_customers": 170, "months": 6})` — private **and** annotated, invisible twice over.

## 2. `_RENDER_SITE_SEEDS` is dead in the shipped path and alive in the R15 mutation

Grepped over the whole tree: `_RENDER_SITE_SEEDS` is **read at exactly one call site, and it is a
test** (`tests/tools/test_couple_w2_11_d5.py:6624`). No shipped function reads it. Its comment block
still narrates the design it was named for — *"a literal only counts as a render of THIS figure if it
CHANGES WITH THE FIGURE — measured on two seeds"* — and that population was replaced under D36
(Hour #20) by `_PUBLISHED_BOOK_SPECS`, which are **hand-built books driven through
`LivePaymentTriad.measure_and_write`, not `build_scenario` draws, and carry no seed at all.** A reader
auditing *"which population discriminates the render sites"* reads the constant that answers, and the
answer is four decisions out of date.

The one live reader is the R15 mutation that proves the reader walk's epsilon control can fail
(`test_a_carrier_read_as_text_collapses_every_epsilon_to_the_doubles_width`). It builds its own two
populations from `_resolution_population(300, s)` for `s in _RENDER_SITE_SEEDS`. So **the mutation
proving the control can fail is run on a population the control never runs on** — the shipped walk's
books are 150×6 and 170×6 through the composer; the mutation's are n=300 seeds 7 and 11 through
`score_triad`. The mutation fires; what is unproven is that it fires *on the artefact the control
grades*. Same shape as the standing lesson *a harness's convenience chose the control's subject*.

## 3. The discrimination rule assumes the carrier moves with the book. The headline's does not.

Both render sweeps (`measure_component_render_sites`, `measure_reader_render_sites`) reject any
precision at which the two books print the same digits — correctly, because at that precision a
constant that spells the figure cannot be told from a render of it. The rule is sound. What is
unstated is its premise: **it needs the two books to produce different figures**, and the headline
carrier does not vary continuously in book size.

Measured 2026-08-15, shipped `_publish_one_book` / `published_books` / `measure_*_render_sites`
unmodified, only the book specs substituted (which is the shipped parameter, never a monkeypatch),
61 books at `n_customers` 140…200, `months=6`, 69s total:

**`detection` — the headline, the only figure `measure_and_write` hands downstream as a number and
therefore the only one that reaches the Proof door — takes 17 distinct values across those 61 books,
in runs of 2 to 8 consecutive sizes.** It is a small-integer ratio and it is piecewise constant:

| value | as a fraction | book sizes |
|---|---|---|
| 0.115384615 | 3/26 | 142–146 |
| 0.113207547 | 6/53 | 147–149 |
| **0.118181818** | **13/110** | **150–156** |
| 0.116071429 | 13/112 | 157–164 |
| 0.129310345 | 15/116 | 167–171 |

The shipped first book, `n_customers=150`, sits in a run of **seven**. Any second book drawn from
inside its own run makes the two carriers bit-identical, the discrimination rule rejects *every*
precision 1…12, and the sweep credits the headline with no render site at all.

## 4. What that does to the shipped control, run rather than reasoned about

`published_books(specs=(150×6, 151×6))` — one customer's difference from the shipped pair — through
the **unmodified** `measure_component_render_sites` / `check_component_render_sites` and
`measure_reader_render_sites` / `check_reader_render_sites`:

```
detection  sites=()          (ageing/belief/belief_population_mix/detection_latency unchanged)

check_component_render_sites:
  detection: declares a 4dp render into `note` that this scoring does not produce --
             a render site nobody can find cannot be what set this figure's epsilon
check_reader_render_sites:
  `div.gap-row[0]/.../div.gap-val[0]` is declared a searched region and renders the SAME text
             on both books -- ... this region can never credit any figure with a site
  detection: declares a 3dp reader site `door:coupled-gaps#gap-val` that this walk cannot find
  detection: declares a 4dp reader site `door:coupled-gaps#note` that this walk cannot find
  detection: declares a 4dp reader site
             `renderer:background/gap_metric.py::format_detection_summary` that this walk cannot find
  detection: is rendered at NO site either sweep can find, so the 4dp its epsilon is set from
             has never been confronted with an artefact -- it is an AST read of
             `format_detection_summary` and nothing else, which is the shape of the defect D34 and
             D35 were both minted to close
```

**The control fails CLOSED, which is right, and it names the wrong side, which is the finding.** Five
violations, every one of them phrased as a debt in the *register* — *"a render site nobody can
reach"*, *"has never been confronted with an artefact"* — when the register is correct and unchanged
and the entire cause is that the measurement's two books landed in one quantisation cell. The
instrument's own most severe message, the one it reserves for a figure whose epsilon rests on nothing
but an AST read, is reachable by a **one-customer edit to a private annotated constant that no census
sees and no test pins.** The module's `raise` backstop does not catch it either: it fires only when
*no* dimension has *any* site, and the other four still do.

The blindness is not confined to `detection`. Over all 1,830 pairs drawable from 140…200, **403
(22.0%) lose at least one shipped render site** (`detection_latency` 277, `detection` 118, `ageing`
38, `belief` 19, `belief_population_mix` 8), and 118 pairs make `detection` bit-identical, i.e.
invisible at every precision. Anchored on the shipped 150, the six nearest available partners all
break something: 151–155 lose `detection`, 156 loses `detection` *and* `detection_latency`, 157 loses
`detection_latency`, 158 loses `ageing`. The shipped 170 is the fourth safe value above 150 and there
is no recorded reason it was picked.

**On the shipped pair the blindness does not bite, and that is stated rather than buried.** At
(150, 170) the sweeps are blind at 1dp for all five dimensions and additionally at 2dp for `ageing`,
and no published string renders any figure at a blind precision — measured with `_rendered_at` over
all 27 shared published string keys. Today's sites (`ageing` 3dp, `detection_latency` 2dp, the other
three 4dp) are all found. The margin on `detection_latency` is **one decimal place**.

## 5. Why this is D27's class and not a fix on sight (R12, self-interrupt discipline)

D27's complaint is *a design note standing in for a measurement*: `DD_FAILURE_WINDOW_DAYS = 400` was
chosen for a stated reason and the cost of that choice to the instrument's resolution was never
measured. This is the same shape with the note missing entirely — `_PUBLISHED_BOOK_SPECS` has **no
stated reason at all** (the `unstated` class that was already the largest in the first DISCOVER's
provenance census), and its cost is not resolution in days but *whether the headline has any render
evidence*. It is the fourth constant in this module found to set an instrument's resolution while
sitting outside every census built to find such constants.

**No value change is proposed.** 150/170 is not defended by its output and no other pair is
recommended; the finding is that the choice is unrecorded, unpinned, uncensused, and load-bearing on
the headline. Choosing a pair *because* it gives `detection` a site would be selecting the population
to green the control, which is the R12 shape this atom exists to name.

## 6. What a BUILD would land, and the mutation that proves each control can fail (R15)

Not built here (epoch-gated). D27 owns the census **shape**; the register declarations remain D28's
and the undefined-reading witness D31's. Handed over in writing:

1. **The census subject is derived over `ast.Assign` *and* `ast.AnnAssign`, public and private.** The
   previous pass's criterion-1 rule is amended before it is built. *Mutation:* restrict the walker to
   `ast.Assign` → `SCENARIO_CONSTANT_CENSUS`, `PUBLISHED_GAP_CONSUMERS` and `_PUBLISHED_BOOK_SPECS`
   must disappear from the subject, i.e. today's blindness is visible as a failure. *Second
   mutation:* restore the `startswith("_")` filter → `_PUBLISHED_BOOK_SPECS` alone must be enough to
   fire, because a private constant read by the published path is a choice regardless of who was
   meant to read it.
2. **A constant that selects the scored POPULATION owes a measured discrimination reading, on the
   property the rule that consumes it actually needs.** `_PUBLISHED_BOOK_SPECS` declares, measured by
   running the sweep and not asserted, that its two books put every dimension's carrier in different
   quantisation cells — i.e. for each dimension the pair is discriminating at least to that
   dimension's declared render precision. *Mutation:* substitute the second book with any member of
   the first's own run (151…156 today) → must fire, and must fire naming the **population**, not the
   register. *Second mutation:* freeze the recorded reading instead of measuring it → must fire (the
   D20/D21 shape: a declaration that restates itself).
3. **A "site nobody can find" violation must distinguish an undischarged register from an
   undiscriminating population.** Today one message covers both and only ever accuses the register.
   The check first asks whether the pair could have seen a render of this figure at this precision at
   all; if not, the violation is against the book specs. *Mutation:* remove the discrimination
   pre-check → the 150/151 pair must go back to blaming the register, so the improvement is visible
   as a failure of the weaker control.
4. **The R15 mutation for a control runs on the control's own population.** The epsilon-collapse
   mutation moves from `_resolution_population(300, seeds)` to `published_books()`, and
   `_RENDER_SITE_SEEDS` — dead in the shipped path — goes with the move. *Mutation:* point the test
   back at a `build_scenario` population → must be refused by name, because a mutation on a substitute
   population proves the mutation fires somewhere and not that the shipped control can fail.

## 7. What this DISCOVER does not settle

* **Whether `months=6` carries the same exposure as `n_customers`.** Only the customer count was
  swept; the two books share `months=6` and it was never varied, so the second axis of the same
  constant is unmeasured.
* **Whether a third book would discharge the class or move it.** Three books make the rule stricter
  (a precision must discriminate all three), which shrinks the blind set but also makes a lost site
  more likely; not measured, and the cost is ~1.2s per book, so it is cheap and merely undone.
* **The other four measurement functions on outside seeds.** The previous DISCOVER's §5 first and
  second bullets — `measure_organ_query_grid_saturation`, `measure_own_drift_resolution`,
  `measure_published_figure_caveat_coverage`, `measure_published_resolution_floor` were confirmed here
  to default to `RESOLUTION_SEEDS` (grep, §1 of that doc stands) but none was swept. Still open, still
  ~33s per seed.
* **Whether `n_customers=300` on the `RESOLUTION_SEEDS` side quantises the same way.** The
  piecewise-constant carrier found here is a property of a small-integer ratio over a book, and the
  resolution sweeps score a different book at a different size. Untested.

## 8. Reproducing the measurement

From the repo root with `PYTHONPATH=.`; drives the shipped composer into a `TemporaryDirectory`,
writes nothing to the repo, ~1.2s per book.

```python
from tools import couple_w2_11_d5 as C
reg = C.PUBLISHED_GAP_CONSUMERS
def carrier(res, dim):
    kind, key = tuple(reg[dim]["carrier"]); g = res[dim]
    return g.gap if kind == "gap" else g.components.get(str(key))

# §3 -- the headline is piecewise constant in book size
{n: carrier(C._publish_one_book({"n_customers": n, "months": 6})["result"], "detection")
 for n in range(140, 201)}                       # 17 distinct values, 150..156 identical

# §4 -- the shipped controls on a one-customer-different pair
books = C.published_books(specs=({"n_customers": 150, "months": 6},
                                 {"n_customers": 151, "months": 6}))
m = C.measure_component_render_sites(books=books)
C.check_component_render_sites(m)                                    # 1 violation, detection
C.check_reader_render_sites(C.measure_reader_render_sites(books=books), m)   # 4 more

# §1 -- the subject rule's blind spots
import ast, inspect, sys
tree = ast.parse(inspect.getsource(sys.modules[C.__name__]))
len([n for n in tree.body if isinstance(n, ast.AnnAssign)
     and isinstance(n.target, ast.Name) and n.target.id.lstrip("_").isupper()])   # 27
```

## 9. Level

**Stays L0, and that is correct rather than a hold.** L1 is *"been BUILT in any form"*
(`MATURITY_MAP.md` §3) and this atom's deliverable is a reshape of `tools/couple_w2_11_d5.py`, which
is epoch-gated. The doc is not this atom's deliverable, so DISCOVER cannot move the level.
