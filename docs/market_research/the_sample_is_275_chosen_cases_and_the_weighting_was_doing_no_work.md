**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `unminted`

**Knowledge:** none -- the housing knowledge page is deliverable 4 of the housing ruling and is not
yet written. These are the sample-design rows it will publish; the declaration is replaced when the
page lands.

# The sample is 275 chosen cases, and the weighting was doing no work

**Measured 2026-09-07**, delivery seat, against the clarified
`DIRECTOR_CANON_THE_DEMAND_VECTOR_2026-09-07` (a257cc65). Reproduce with
`python3 -m tools.demand_vector_coverage --measure`.

**This supersedes the 8,500 figure published earlier today. The director wrote the tell into the
canon and it fired: *"if N comes out at the scale a random sample would need, the weighting is doing
no work."* It was doing none, because there was none.**

---

## The answer

| tolerance | **cases chosen and weighted** | random sample (the comparator) | factor |
|---:|---:|---:|---:|
| 0.10 | **125** | 1,597 | 12.8× |
| 0.05 | **275** | 8,500 | 30.9× |
| 0.02 | **2,315** | 30,000 | 13.0× |

**275 deliberately-chosen, weighted households reproduce the observed distribution of the full
vector — gas, electricity, seasonal swing and both intervention ceilings — as well as 8,500 randomly
drawn ones.** Fuel-stratified, so the 18.5% non-gas stock passes in its own right.

## What was actually running

The acceptance test drew `rng.choice(len(values), size=n, replace=False)` — a uniform random sample
of the population — and compared it to the population. **No weight entered the test at any point.**
The word "weight" appeared six times in the module: five in building the population, and once in the
docstring *quoting the canon's requirement that the code did not implement*.

So the module claimed the weighted design in prose and ran its opposite. 8,500 was the honest answer
to a question nobody had asked.

## The design, and the first version of it was worse than random

**Choose for difference, then weight by the mass each case stands for.** Both halves had to be got
right and the first attempt got the first half wrong in an instructive way.

**Maximin choosing failed and failed loudly.** Greedy farthest-point selection — right for spanning
a space — puts every case in the sparse outskirts. The dense bulk where most households live ends up
represented by a handful of atoms carrying enormous weight, so the weighted distribution steps
coarsely exactly where the mass is. Measured against a random draw at the same size it was **worse**:
0.4159 against 0.1445 at 55 cases. *No weighting can rebuild a bulk-heavy distribution from a set of
extremes.*

**What works is cluster medoids plus deliberate tails.** One real household per distinct region of
behaviour — so two near-identical households can never both be chosen, which is the canon's
near-duplicate rejection — plus the extreme of every axis, plus the extremes *within each fuel*,
because the minority fuel's tail is not the population's tail.

**And the weights are solved, not assigned.** Non-negative least squares against the population's own
CDF. Assigning each case its Voronoi mass — the obvious reading of "the mass it stands for" — was
still no better than random (0.1148 against 0.1176 at ~150). Fitting the weights is what makes the
design work, and it is what the canon's "the weights carry the representativeness" actually requires.

Non-negativity is not a solver convenience: **a case that must be subtracted to make the
distribution work is a case that should not have been chosen.**

## Why this is not fitting to the answer

The weights are solved on **32 directions and the marginals**; the acceptance scores **64 different
directions**. A design that passed only on what it was fitted to would have learned the test rather
than the population. A control asserts the two sets are disjoint, and the reported figures are all
held-out.

## What this buys, in the director's terms

A random sample of 8,500 would pass the same test and be, in his words, *a faithful crowd of
near-identical households*. 275 chosen cases pass it while every one of them is a distinct
behaviour, every axis extreme is present by construction, and each carries the household mass it
stands for. **The sample is 31× smaller and it is the one that teaches the company something.**

## Named, not smoothed

- **The distribution-only figure came out at 389, above the full-vector 275.** Adding axes made it
  easier, which should not happen. The two runs cluster in different dimensions and force in
  different numbers of tail cases (6 against 10 plus per-fuel), so the ladders land on different case
  counts — but I have not established that this is the whole cause, and it is reported unexplained
  rather than presented as a result.
- **Half-hourly electricity shape is still absent**, so this remains a floor. It is the one axis
  `W2_19` is genuinely needed for.
- **Shape is modelled and not validated**, by the director's decision; SERL is not pursued.
- **Gas and electricity are observed; the heat model is not validated against them.** That is the
  validation step, which the director has ordered after `W2_19`.
- **England and Wales only** — NEED carries no Scottish dwellings.

---

## AMENDED 2026-09-07 — 275 is a FLOOR for a PARTIAL vector, not the size of the book

Director, refusing the figure: *"It's the number for a partial vector... the number has moved an
order of magnitude every time an axis arrived... I'd rather carry thousands and know why than carry
275 and find out later."*

He is right and the figure is republished as a floor. Since this was written the population is
GENERATED rather than selected, Scotland is reachable, and weather sensitivity is an axis:
**275 -> 273 (Scotland) -> 243 (weather sensitivity)**.

The mechanism, and it sharpens rather than softens his point: **strata multiply, correlated axes do
not.** The non-gas stratum multiplied the figure sevenfold; Scotland and weather sensitivity moved
it by ~12% between them. Payment method, read pattern and arrears are STRATA, so the prediction --
filed before they are built -- is low thousands.

Full account: `the_sample_size_is_a_floor_and_strata_are_what_multiply_it.md`.
