**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** W2_21_the_premise_joint_is_fitted_not_drawn_independently

**Knowledge:** none -- the housing knowledge page is deliverable 4 of the housing ruling and is not
yet written. These are the association rows it will publish; the declaration is replaced when the
page lands.

# The tilt table had a direction wrong, and a direction was the only thing it claimed

**Measured 2026-09-07**, delivery seat, `W2_21`. Reproduce with
`python3 tools/need_stock_joint.py --lifts`.

The housing ruling, section 3.1, wants the joint fitted *"WITH THEIR PUBLISHED CORRELATIONS"*, and
names the failure mode to refuse: *"an invented correlation matrix where a published cross-tab
exists"*.

`simulation/premise_population.py` built its seed joint as the independent product of three
published marginals times two hand-written tilt tables, and said so in its own docstring:

> **THE TILT MAGNITUDES ARE NOT ANCHORED. Only their direction is.**

DESNZ NEED carries `PROP_TYPE × PROP_AGE_BAND × EPC` on one row per dwelling for **34,914 rated
dwellings**. So the magnitudes were measurable all along — and one of the directions is wrong.

---

## What the cross-tab says against what was assumed

Lift is observed ÷ (row × column); 1.00 means no association.

| cell | hand table | measured | |
|---|---:|---:|---|
| pre-1919 × F, G | 5.0, 8.0 | **2.78** | up to 2.9× too harsh |
| pre-1919 × C | 0.30 | **0.59** | 2.0× too harsh |
| post-2000 × C | 1.90 | **1.00** | post-2000 is exactly average for band C |
| **detached × A/B** | **0.90** | **1.21** | **the direction is wrong** |

**Detached is bimodal and the hand table could not see it.** Old rectories and new large houses sit
in the same category, so detached homes are over-represented at *both* ends — 1.21× in A/B and 1.81×
in F/G. The hand table had them slightly *less* likely to be A/B. Nothing short of the cross-tab
would have caught it, because the error is in the one property the table claimed to have.

The rest of the structure is strong and was directionally right:

| age band | A/B | C | D | E | F/G |
|---|---:|---:|---:|---:|---:|
| before 1930 | 0.04 | 0.59 | 1.39 | 2.12 | **2.78** |
| 1930–1972 | 0.06 | 1.00 | 1.34 | 1.16 | 0.89 |
| 1973–1999 | 0.13 | 1.49 | 1.05 | 0.56 | 0.26 |
| 2000 or later | **3.85** | 1.00 | 0.14 | 0.06 | 0.01 |

## Two mappings, both arithmetic rather than judgement

**NEED's age bands are coarser than this project's eras** — 1 = before 1930, 2 = 1930–1972,
3 = 1973–1999, 4 = 2000 or later, per DESNZ's own metadata. Three of the six eras sit inside one
band; three straddle a boundary. A straddling era takes the **year-weighted average** of the bands it
spans: 1919–1944 is eleven years in band 1 and fifteen in band 2, so 0.423 / 0.577. That is
arithmetic on two published sets of boundaries, and every alternative is an opinion about where a
1919–1944 house "really" belongs.

**A/B and F/G are reported as pairs** and their lift applies to both members. Splitting inside a
bracket the source does not resolve would be precisely the invention the ruling refuses.

## The exit criteria, met

**1. Every existing marginal recovers.** All 40 pre-existing tests in
`tests/simulation/test_premise_population.py` pass unchanged. Raking is what makes this true: the
seed changed, the published marginals it is fitted onto did not.

**2. A correlation the independent draw could not produce.** An independent product has lift
**exactly 1.00 in every cell by construction** — that is asserted as its own control, so "the fitted
joint shows a correlation" is falsifiable rather than decorative.

| | independent | fitted | measured |
|---|---:|---:|---:|
| detached × A/B | 1.000 | **1.299** | 1.207 |
| flat × A/B | 1.000 | 1.310 | 1.317 |
| detached × F | 1.000 | 1.726 | 1.811 |
| pre-1919 × F | 1.000 | 2.549 | 2.785 |
| post-2000 × A/B | 1.000 | **6.244** | 3.854 |

## Where it does not reproduce, and why

**Post-2000 × A/B comes out 62% over.** Raking is the cause and it is not a bug: the published GB
A/B marginal is **3.3%**, while A/B is **15.2%** of NEED's rated dwellings. Squeezing the marginal
down by a factor of 4.6 concentrates what remains into the cells with the strongest lift, so the
sharpest association is amplified. Where the sample's marginal and the published marginal agree, the
fitted lift lands within 10% of measured; where they disagree by 4.6×, it does not.

That is a general property of raking a measured association onto a disagreeing marginal, and the
control is keyed to direction and order of magnitude rather than to a tolerance the method cannot
hold.

## The residual, declared

**30.2% of NEED's dwellings have no EPC, and they are not missing at random.** An EPC exists because
a home was sold, let or newly built:

| | rated | unrated | ratio |
|---|---:|---:|---:|
| flat | 29.2% | 11.4% | **0.39** |
| detached | 13.3% | 20.8% | 1.56 |
| built 2000+ | 24.5% | 5.9% | **0.24** |

What this damages and what it does not: these are **conditional** lifts and the seed is raked onto
the published marginals afterwards, so a biased marginal composition washes out. What does not wash
out is an unrated home rating differently from a rated home of the **same type and age** — and NEED
cannot answer that, because an unrated home has no rating. It would need a linked EPC register.

## Limits

- **England and Wales only.** NEED is a DESNZ product and carries no Scottish dwellings; the
  association is assumed to hold in Scotland, which is not tested here.
- **Two-way association only.** The lifts are type × EPC and age × EPC, applied multiplicatively.
  The three-way interaction — whether a pre-1919 flat rates differently from what its two lifts
  imply — is in NEED and is not used. That is the next refinement and it is not made here.
- **Floor area, mains gas and region are in the same file and are not fitted yet.** This atom's
  scope is the EPC association; `W2_22`'s space-filling sample is where the rest of the joint gets
  exercised.
