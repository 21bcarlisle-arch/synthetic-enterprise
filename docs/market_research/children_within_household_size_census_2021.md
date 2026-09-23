# Dependent children WITHIN household size — ONS Census 2021, England and Wales

**Knowledge:** how-many-synthetic-households

That page's argument is that the sample size depends on STRATA rather than on variety, and it is
already reviewed against "NEED + Census + HadUK". This adds a Census-derived stratum to exactly
that population — the composition the synthetic book is drawn from and measured against.

**Fetched** 2026-09-23. **Closes** R10 GAP (a)'s POPULATION half, filed as
`R10-DISTRIBUTION-CANDIDATE` in `occupancy_consumption_volume_shape_w2_13.md` §3.
**Lands at** `simulation.demand_model.CHILDREN_WITHIN_SIZE_REFERENCE`.
**Does NOT close** the RESPONSE half — `CHILD_ADULT_EQUIVALENT_RANGE` is still a sampled
interval, because NEED still publishes no adults-×-children consumption cross-tabulation.

## The question

How many dependent children does a household of a given size contain? The volume response
divides by a centre computed over a reference population; with no children distribution, the
only centre available read every household as all adults, and scoring a book that declares
children against it cut the aggregate silently.

**"Dependent child" is the Census definition** and it is not the obvious one: a person aged 0–15
in the household, or 16–18 in full-time education and living with a parent. A 19-year-old living
at home is a NON-dependent child and counts here as an ADULT — which is the right reading for
NEED, whose gradient is per adult consumer, not per bedroom occupant.

## No published table states this

Checked before deriving anything, by listing all 45 dimensions of the Census `HH` population type:

| Candidate | Why it cannot answer |
|---|---|
| `hh_size_9a` × `hh_adults_and_children_11a` | **Refused by the API** — ONS blocks the pair |
| `hh_dependent_children_3a` (household base) | presence INDICATOR, no count |
| `hh_adults_num_3a` | splits only "1 adult" from "no adults, or more than 1" |
| `hh_family_composition_37a` | one / two-or-more only, and no adult count for "other" types |

## What was used, and the conversion

`UR_HH` (all usual residents in households, 58,555,848 people) cross-tabulated
`hh_size_9a` × `hh_dependent_children` (21 categories: none / all non-dependent / one / two /
three-or-more, each by youngest child's age):

```
api.beta.ons.gov.uk/v1/population-types/UR_HH/census-observations
    ?area-type=nat&dimensions=hh_size_9a,hh_dependent_children
```

That is a PERSON base, converted to households exactly — every household of size *n* contributes
exactly *n* residents to its cell, so `households(n, d) = persons(n, d) / n`.

**The conversion is controlled, not asserted.** Summed back over *d* it reproduces the household
counts published on the separate `HH` population type (24,783,195 households):

| size | from `UR_HH`/n | published `HH` | diff |
|---|---|---|---|
| 1 | 7,481,786 | 7,481,788 | −2 |
| 2 | 8,451,404 | 8,451,404 | −0.5 |
| 3 | 3,955,168 | 3,955,168 | −0.3 |
| 4 | 3,182,251 | 3,182,247 | +4 |
| 5 | 1,112,752 | 1,112,750 | +2 |
| 6 | 373,957 | 373,959 | −2.5 |
| 7 | 130,727 | 130,726 | +1 |
| **8** | **106,769** | **95,153** | **+11,616** |

Seven bands agree to within five households out of 24.8 million. Size 8 does not, and the reason
is stated rather than smoothed: the band is "8 **or more**", so dividing by 8 overcounts
households whose true size is larger. It is 0.4% of the population.

## What is assumed, once

The Census stops at **"three or more dependent children"**. Those cells are published here as
**three** — the only count the source asserts. This understates the tail.

- **4.674%** of households sit in those cells.
- Resolving every one at the opposite extreme instead (every remaining member a child, one adult
  left) moves the electricity centre by **0.268%**.

Two clamps, both named and both measured: `d ≤ n−1`, because `adult_equivalents` refuses a
household with no adult (this removes 3,606 one-person households recorded with a dependent
child — Census cell-key perturbation artefacts); and the "8 or more" band is represented at 8.

## The size marginal is the world's own draw

Only the CONDITIONAL `P(children | size)` is taken from the table above. It is multiplied by
`dwelling_records.HOUSEHOLD_SIZE_SHARE_ONS_TS017` — the 1…8+ distribution the world actually
draws households from.

**That choice does not confound the comparison, and it was checked rather than assumed.** Reading
the reference as all adults reproduces the all-adult centre EXACTLY at full precision (to 9e-08
after the published shares are rounded to 7 dp), because `need_volume_index` is flat at and above
five adults — so how the 5+ band is split cannot move the all-adult centre at all. The difference
between the two centres is therefore attributable to children alone.

The same flatness is why the finer tail is worth carrying in the children reference and not in
the all-adult one: six adults sit in the flat region, but six people including three children do
not (3 + 3w adult-equivalents, below 5). Pooling 6/7/8 onto 5 is an exact equivalence for the
all-adult centre and a **0.272%** error for the children centre.

## Independent cross-checks

Two *household-based* products, a different population type from the one the reference is derived
from, pin the d=0 and d=1 mass at every size:

| | source | worst disagreement |
|---|---|---|
| `P(any dependent child \| size)` | `HH` × `hh_dependent_children_3a` | **1e-6** at sizes 2–7 |
| `P(exactly one dependent child \| size)` | `HH` × `hh_family_composition_37a` | **0.24pp** (0.11pp excluding size 8) |

Only the split *within* "two or more" is left unpinned, which is exactly the assumption named
above. `test_the_conditional_children_split_agrees_with_two_INDEPENDENT_census_products` is the
control, and it exists because mutation testing found that every *other* control was invariant to
moving mass between children counts inside a size band.

## The numbers

Mean dependent children per household **0.4927** — 12.2m across 24.8m households, against the
~12.3m the Census counts in England and Wales. It reads low by construction, because
"three or more" is published here as three.

| | all-adult centre | children centre | move |
|---|---|---|---|
| electricity | 1.4456452584044155 | 1.4047186533 | **−2.83%** |
| gas | 1.2512721741165458 | 1.2246798208 | **−2.13%** |

`P(any dependent child)` by size: 0.0005, 0.087, 0.569, 0.806, 0.864, 0.878, 0.894, 0.894 for
sizes 1…8+.

## What this changes downstream

`population_mean_volume_factor` and `volume_factor_is_unbiased` no longer refuse a book that
declares children — they centre it on this population. The refusal survives, re-keyed to the
property it was always about: withdraw the source and a book with children refuses again.

On the live 144-home book, with the children `premise_trace` already draws for itself:

| | against the all-adult centre | against this centre |
|---|---|---|
| electricity | 0.98458 | **1.01601** |
| gas | 0.98678 | **1.01150** |

The same book read as ALL ADULTS against the all-adult centre is **1.01799**. So of the original
1.5% "cut", **1.3 points were the centre and 0.2 points were the children** — the book was never
being cut by declaring children; it was being measured against the wrong population.

## What remains owed

`dwelling_records.DEFAULT_CHILDREN_COUNT` still cannot be wired, and the reason has changed.
It is no longer the population — it is the DRAW. `premise_trace` draws `randint(0, n−1)`, uniform
and uncited, which puts a child in half of all 2-person homes where the Census puts one in 8.7%.
The remaining work is one sourced draw from this conditional, answering in both places.
