**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** W2_21_the_premise_joint_is_fitted_not_drawn_independently

**Knowledge:** none -- the housing knowledge page is deliverable 4 of the housing ruling and is not
yet written. This is the row that justifies the fitted joint on it; the declaration is replaced
when the page lands.

# Drawing the axes independently invents one house in five that the stock does not contain

**Measured 2026-09-06**, delivery seat, `W2_21`. Source: DESNZ NEED `anon2026_50k.csv`, 50,000
dwellings, the same file behind the floor-area and mains-gas anchors.

---

## The question

The machine's own D-SEGMENT pass found twenty-one trait axes drawn **overwhelmingly
independently**, with two couplings built. The housing ruling wants the joint fitted with its
published correlations instead. That is a cost/benefit claim, and until now nobody had put a number
on the cost.

## Every axis pair is associated. None of them is independent.

Cramér's V over the 50,000 rows:

| V | pair |
|---:|---|
| **0.474** | property type × floor-area band |
| **0.453** | property type × mains gas |
| **0.383** | floor-area band × mains gas |
| 0.269 | property type × age band |
| 0.235 | age band × mains gas |
| 0.163 | region × property type |
| 0.158 | region × mains gas |
| 0.132 | age band × floor-area band |
| 0.122 | region × floor-area band |

An independent draw asserts every one of these is **zero**. The strongest is the pair the ruling
names first.

## What that costs, in houses

Comparing an independent draw's expected cell counts against the observed stock:

| cell | independent draw | observed | ratio |
|---|---:|---:|---:|
| Detached ≤50 m² | 1,303 | **0** | 0.00× |
| Semi detached ≤50 m² | 2,109 | 5 | 0.00× |
| Flat >200 m² | 352 | 4 | 0.01× |
| Flat 151–200 m² | 630 | 8 | 0.01× |
| End terrace ≤50 m² | 722 | 17 | 0.02× |
| Flat 101–150 m² | 3,082 | 87 | 0.03× |

**1,303 detached houses under 50 m². The stock contains none.** And the error runs both ways — the
cells it starves are the ones that matter most:

| cell | independent draw | observed | ratio |
|---|---:|---:|---:|
| Detached 101–150 m² | 2,012 | 3,999 | 1.99× |
| Flat ≤50 m² | 1,995 | 8,100 | 4.06× |
| Detached 151–200 m² | 411 | 1,742 | 4.24× |
| **Detached >200 m²** | 230 | **1,182** | **5.15×** |

**Total: 9,779 houses per 50,000 — 19.6% — land in cells the stock effectively does not have.**

## Why the second table is the more serious one

The invented houses are visible: a 40 m² detached house is absurd on sight and someone would
eventually notice. The **missing** ones are not. An independent draw produces the large detached
house — the top consumption band, the biggest margin bet, the case the CLV reference puts at
£1,200 or −£4,700 depending on the hedge — at **one fifth** of its real frequency.

So a sample drawn independently is not merely noisy. It systematically under-represents the tail
where the money and the risk are, while matching every marginal perfectly. That is failure mode (a)
in the ruling's own §6, measured: *"a sample that matches every marginal and misses the joint
corners."*

## What this settles for the build

- The joint is **fitted**, not raked axis by axis. The correlations above are measured from a
  published source, so the ruling's prohibition on inventing a correlation matrix costs nothing —
  there is nothing to invent.
- The existing marginals must still recover. Fitting the joint changes which *combinations* are
  drawn, not how many of each type — and a marginal that moves is a fidelity finding decided blind
  to P&L, not a side effect to absorb.
- The four axes fitted here are property type, floor-area band, age band and mains gas, plus region.
  Every one is present in the NEED rows, so this joint needs no new source.

## Limits

Region is NEED's own coarse region, not small-area geography; the people ruling's layer-one joint
needs the latter and this does not supply it. Floor area is banded with an open top. And these are
**generation** figures — validating the SIM's consumption against NEED after fitting its stock to
NEED would be a tautology, so validation needs different lineage.
