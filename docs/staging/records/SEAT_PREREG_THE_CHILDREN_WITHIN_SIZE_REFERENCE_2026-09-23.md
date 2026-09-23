# PRE-REGISTRATION — the children-within-size reference population

**Filed** 2026-09-23, BEFORE any observation was fetched from the ONS API and before any centre
was computed. Claim id `children-within-size-reference-is-owed-a-source`.

## What is being established

`simulation.demand_model.CHILDREN_WITHIN_SIZE_REFERENCE` is an explicit `None` carrying R10 GAP
(a)'s **population half**: how many dependent children a household of a given size contains.
Without it `population_mean_volume_factor` and `volume_factor_is_unbiased` refuse any book that
declares children — deliberately, because `premise_trace` draws children as an uncited
`randint(0, people_count - 1)` and centring the response on that draw would normalise a gap
against itself.

## The source, named before it is read

ONS **Census 2021** (England & Wales), household-level population type `HH`, via the custom
dataset API `api.beta.ons.gov.uk/v1/population-types/HH/census-observations`. The two dimensions
that exist and could carry the joint structure, established by listing all 45 `HH` dimensions
before any observation was requested:

- `hh_size_9a` — Household size (9 categories): 0,1,…,7, "8 or more people".
- `hh_adults_and_children_11a` — Adults and children in household (11 categories), bands such as
  "Two adults: One or two children", "Two adults: Three or more children", "Three or more adults:
  One or more children".

`hh_dependent_children_3a` is a presence INDICATOR only (no count) and `hh_adults_num_3a` splits
only "1 adult" from "no adults, or more than 1 adult" — neither can carry the count, which is why
the cross-tab above is the instrument rather than a single ready-made table.

**The cross-tab does not state a children count directly.** It has to be DERIVED per cell from
(size, band). Most cells are exact — "Two adults: One or two children" at size 3 is one child and
at size 4 is two — and some are not: "Three or more adults: One or more children" at size ≥ 5
admits more than one split. That residual ambiguity is the thing to measure and bound, not to
average away silently.

## Predictions

Numbered so a refutation can be pinned to one of them. None of these numbers has been looked at.

**P1 — the zero-children mass.** At least 65% of England & Wales households will have zero
dependent children in the derived reference.

**P2 — the direction and size of the centre move.** The children-aware electricity normaliser
will be **strictly LOWER** than the all-adult centre `1.4456452584044155`, and by **less than
4%** — i.e. in `[1.3878, 1.4456)`. Lower because replacing an adult with a child at weight
`w ∈ (0.35, 0.85)` can only reduce adult equivalents, and small because most households have no
children at all (P1).

**P3 — the one worth being wrong about. Which side of 1.0 the live book lands on.**
Recomputing the live 144-home book's mean volume factor against the ONS-sourced centre (instead
of the all-adult centre, where it measured 0.9846 electricity), I predict it stays **BELOW 1.0,
and below 0.995**. The reasoning: `premise_trace` draws `randint(0, n-1)` children, mean
`(n-1)/2`, which is far MORE children than the ONS population carries, so the book is
child-heavy against a correctly-sourced centre and its raw need index sits below that centre.
If it lands above 1.0 I have the sign of the uniform draw's bias backwards, and the remedy
changes: the draw would be understating children, not overstating them.

**P4 — how much of the population the ambiguity touches.** Households falling in cells where
(size, band) does not determine a unique children count will be **under 10%** of all households.

**P5 — what the ambiguity is worth.** Resolving every ambiguous cell at its MINIMUM children
versus its MAXIMUM children will move the electricity centre by **less than 1%** — so the
reference can be published with the ambiguity resolved one way and the other way named as a
bound, rather than the whole thing being refused.

## What done means for this claim

1. `CHILDREN_WITHIN_SIZE_REFERENCE` carries a sourced distribution with its origin declared, or a
   `None` with a BETTER-STATED reason than it has today. Either is a result; only a plausible
   invented number is a failure.
2. A research record in `docs/market_research/` with the fetched observations, the derivation,
   and the residual ambiguity measured rather than described.
3. A control that can fail: the centre over the reference must make the reference's OWN mean
   volume factor an identity at 1e-12 — the finding's own lesson, that neutrality is an identity
   over the reference population and only an estimate over a book.
4. What is NOT in scope this turn and why: delegating `dwelling_records.DEFAULT_CHILDREN_COUNT`
   needs a per-household children DRAW from this distribution, not the uniform `randint`. That is
   the next increment; landing the reference without it is still useful, because the reference is
   what the refusal is waiting on.
