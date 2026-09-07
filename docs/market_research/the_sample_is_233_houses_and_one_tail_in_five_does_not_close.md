**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
W2_22_the_sample_is_space_filling_and_rejects_on_outputs

**Knowledge:** none -- the housing knowledge page is deliverable 4 of the housing ruling and is not
yet written. These are the sample-design rows it will publish; the declaration is replaced when the
page lands.

# The sample is 233 houses, and one tail in five does not close

**Measured 2026-09-07**, delivery seat, `W2_22`. Reproduce with
`python3 -m tools.space_filling_sample --measure`.

The housing ruling asks for a sample drawn **for difference rather than for proportion**, with the
similarity test judged on outputs, and for the two coverage curves that set N. It also sets the
target: *"99% of variance, including tails. The tail is where the money and the risk are, and
marginal houses are cheap."*

**N is 233 for the variance half of that target. Four of the five tails close at 610 houses and the
fifth does not close at any affordable size** — and that fifth is the finding, not a caveat on it.

---

## The population and the space

24,662,309 England-and-Wales households, 143,511 occupied 1 km weather cells and the 274 distinct
house cases NEED resolves — 39.3 million (cell, house) pairs, sampled to 200,000 with household
weight. Five output axes, each computed from the closed form validated in
[the demand-case coverage work](thirteen_cases_cover_demand_and_that_is_only_half_an_answer.md)
(r² = 0.9978 against the full 2R2C model):

| axis | what it is |
|---|---|
| `annual_kwh` | the level |
| `kwh_per_degree_day` | the weather gradient |
| `solar_offset_share` | the share of gross heat loss the sun already removes |
| `insulation_ceiling_kwh` | what retrofitting this fabric to FULL would save |
| `turndown_ceiling_kwh` | what one degree off the set-point would save |

**Shape is not among them and that is a gap, not an omission.** The closed form is annual and
carries no half-hourly or intra-year profile, so a shape axis computed from it would be a function
of level and gradient wearing a third axis's name. **Five of the seven phase-1 levers are absent for
the same reason**: PV, battery, EV and flow-temperature ceilings need roof geometry, parking and a
heating circuit the premise joint does not carry, and the ruling itself expects roof geometry to be
a gap. Insulation and turn-down are the two that are computable from published fabric physics today.

## Curve one: distinct houses against variance covered

| houses | maximin draw | k-means ceiling | fill radius |
|---:|---:|---:|---:|
| 8 | 0.7285 | 0.9336 | 2.06 |
| 21 | 0.9075 | 0.9812 | 1.32 |
| 55 | 0.9671 | **0.9936** | 0.76 |
| 144 | 0.9874 | 0.9975 | 0.46 |
| **233** | **0.9925** | 0.9984 | 0.37 |
| 377 | 0.9955 | 0.9989 | 0.28 |

**233 houses for 99% of household-weighted variance in the five outputs.** The optimal partition
gets there at 55, so **drawing for difference costs 4.2× the houses** — and that is the price the
ruling is knowingly paying, because k-means puts its centres where the mass is and the ruling's
whole point is that the mass is not where the money is.

**Fill radius is reported beside it because it is what the draw actually maximises.** Greedy maximin
minimises the worst-covered household's distance to its nearest drawn house; k-means minimises
within-cluster variance. Judging the draw only on the variance column reads as maximin doing badly
at its own job when it is doing well at a different one. At 233 houses, no household in England and
Wales is more than **0.37 standardised units of behaviour** from a house the sample contains.

## Curve two: the tails, and four of the five close

Tail coverage is the share of the population's top 1% on an axis that a drawn house actually sits
in — the tail cut into ten equal-mass bands, a band represented when a drawn house falls in it.

| houses | level | gradient | solar offset | insulation ceiling | turn-down |
|---:|---:|---:|---:|---:|---:|
| 21 | 0.30 | 0.20 | **0.10** | 0.20 | 0.20 |
| 55 | 0.60 | 0.50 | **0.10** | 0.40 | 0.50 |
| 144 | 0.80 | 0.80 | **0.20** | 0.90 | 0.80 |
| **233** | 1.00 | 0.80 | **0.30** | 1.00 | 0.80 |
| 377 | 1.00 | 0.90 | **0.30** | 1.00 | 0.90 |
| **610** | 1.00 | **1.00** | **0.40** | 1.00 | **1.00** |
| 987 | 1.00 | 1.00 | **0.50** | 1.00 | 1.00 |
| 1597 | 1.00 | 1.00 | **0.60** | 1.00 | 1.00 |
| 2584 | 1.00 | 1.00 | **0.70** | 1.00 | 1.00 |

**Four of the five tails are complete at 610 houses.** The fifth — `solar_offset_share` — reaches
**0.70 at 2,584** and is still climbing. Its rate is about one band per 1.6× the sample, so 90%
would arrive somewhere near **6,700 houses**: an order of magnitude more than the variance target,
spent to cover a tenth of one axis.

**That is not a size problem and buying size will not fix it.** The solar offset share is a ratio
bounded by the fabric, and its top 1% is a thin structured set — small, well-insulated homes in the
sunniest cells. A draw whose distances are computed across five standardised axes has no reason to
spend houses inside a thin set, however many it has. **The fix is a stratified top-up that draws
deliberately into each tail band, and it is not built here.**

So the sample has two numbers rather than one:

| target | houses |
|---|---:|
| 99% of household-weighted variance in the five outputs | **233** |
| every tail covered to 90%, unstratified | **not reached; four of five at 610** |

**233 is what this atom reports as N**, and it is reported next to the tail column rather than
instead of it, because a sample sized on the variance curve alone would read as complete while
covering three tenths of one of its tails.

## The ruling's premise, measured rather than assumed

The ruling names its own worst failure mode: *"the similarity test run on inputs instead of outputs,
producing a sample that matches every marginal and misses the joint corners."* Same algorithm, same
households, same size — the only difference is whether the distance is computed on what a house
**is** (its five fabric parameters and its cell's three drivers) or on what it **does**:

| at 233 houses | drawn on inputs | drawn on outputs |
|---|---:|---:|
| output variance covered | **0.9926** | **0.9925** |
| output fill radius | 1.62 | **0.37** |
| corners visited (of 23) | 20 | **23** |
| level tail | 0.60 | **1.00** |
| insulation-ceiling tail | 0.80 | **1.00** |
| solar-offset tail | **0.50** | 0.30 |

**The ruling is right about why it matters and wrong that it shows up in the aggregate.** Variance
covered is identical to four decimal places — an input draw and an output draw both cover the bulk,
because the bulk is where most households are either way. What the input draw loses is exactly what
the ruling cares about: a hole **4.4× wider** at its worst point, three corners it never visits, and
40% of the level tail and 20% of the insulation-ceiling tail missing.

**And it is not a clean win.** The input draw covers the solar-offset tail *better* — 0.50 against
0.30 — because that tail is a thin structured set that the input space happens to separate and the
output space does not. Reported rather than smoothed over: the correct reading is that the two draws
miss different things, and the output draw misses less of what the ruling asked to be covered.

## Which corners of the output space Britain actually contains

A corner is a conjunction: a household in the top or bottom 5% on **two axes at once**. There are 40
such conjunctions across five axes. **Britain occupies 23 of them.** Seventeen are empty — not rare,
empty — because the axes are functions of the same fabric and the output space is a thin surface
inside a five-dimensional box rather than the box itself.

That is what makes 233 a small number. A sample that tried to fill the box would spend most of its
draws on houses that do not exist. The largest occupied corners are the ones a supplier would
recognise:

| corner | share of households |
|---|---:|
| low gradient & low insulation ceiling | 6.9% |
| low gradient & low turn-down ceiling | 5.3% |
| high gradient & high turn-down ceiling | 5.0% |
| high solar offset & low insulation ceiling | 4.9% |
| high level & high insulation ceiling | 4.2% |

**The 233-house draw visits all 23.** The across-runs ledger (`docs/design/visited_corner_ledger.json`)
records which ones each life reaches, because the ruling is explicit that coverage is a property of
the ensemble of runs and not of any one of them.

## The three tail measures, two of which were wrong

Recorded because each looked right and neither was fail-open in the obvious way.

**"Some drawn house is nearest to it"** is fail-open: a mid-range house is nearest to every tail
household when the draw contains no tail house at all, so a tail nothing covers reads as covered.

**"The share of tail mass whose nearest drawn house is itself in the tail"** fixes that and is **not
monotone** — an ordinary house can take nearest-ness away from a tail house, so the figure *falls* as
the draw grows. On this population it went 0.997 at five houses to 0.025 at fifty-five, and the rule
reading N off it reported **five**. A quantity that moves in both directions cannot set N.

**"The share of the tail's own variance captured by drawn tail houses"** is monotone and sorts two
states backwards: with one centre at the edge of a tail, within-tail scatter exceeds the tail's
variance about its own mean, so the figure goes negative — and a draw with a badly placed tail house
scores *below* a draw with no tail house at all.

The banded version is monotone under a nested draw, bounded, zero when no tail house is drawn, and
says in the ruling's own words what share of the top 1% a drawn house sits in.

## What is not covered

- **England and Wales only.** NEED carries no Scottish dwellings, so there is no measured stock
  composition to compose with a Scottish cell; the coldest 8% of the book is out.
- **Shape, and five of the seven levers**, as above.
- **The sample is a household-weighted 200,000 of 39.3 million pairs**, so a corner rarer than one
  in two hundred thousand households reads as empty here whether or not Britain contains it. That
  is a limit of the sampling, not of the draw.
- **The draw is not yet wired into `simulation/population_draw.py`.** This measures the sample and
  reports N; the run loop still draws for proportion. Wiring it is the second half of this atom and
  is where the marginals-preserving requirement has to be met.
- **A tail-stratified top-up is not built.** It is the named fix for the solar-offset tail and the
  reason `n_for_90pc_of_every_tail` is reported as unreached rather than papered over.

## What this creates next

- **The stratified tail top-up.** Named above, not built. Without it `solar_offset_share` is covered
  to 30% at the reported N and the page must say so.
- **Wiring the draw into `simulation/population_draw.py`**, marginals-preserving, which is the half
  of this atom that changes what a run contains rather than what we know about it.
- **A shape axis**, once the observation layer gives a profile the draw can be different about.
- **The five absent lever ceilings**, each blocked on a premise attribute rather than on method.
