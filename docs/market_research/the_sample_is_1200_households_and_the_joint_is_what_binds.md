**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `unminted`

**Knowledge:** none -- the housing knowledge page is deliverable 4 of the housing ruling and is not
yet written. These are the sample-design rows it will publish; the declaration is replaced when the
page lands.

# The sample is 1,200 households, and the joint is what binds

**Measured 2026-09-07**, delivery seat, against `DIRECTOR_CANON_THE_DEMAND_VECTOR_2026-09-07`.
Reproduce with `python3 -m tools.demand_vector_coverage --measure`.

The canon replaces variance coverage with a weighted distributional acceptance test, asks for two
numbers with the second treated as the real one, and asks for answers as price lists rather than
single numbers.

---

## The answer

| tolerance | N to reproduce the distribution | **N to also span intervention response** | dominated by |
|---:|---:|---:|---|
| 0.10 | 233 | **377** | JOINT |
| 0.05 | 800 | **1,200** | JOINT |
| 0.02 | 5,400 | **5,400** | JOINT |

**Tolerance is the accuracy demanded of the sample**: no point of any distribution misplaced by more
than that share of population mass. At 0.05 — half a decile — **the sample is 1,200 households.**

**The binding constraint is the JOINT at every accuracy, never a single margin.** That is the
canon's own claim, measured: what makes the sample expensive is not any one quantity being varied
but the *combinations* that have to appear together.

## What is measured, and what is named absent

Per the director's sequencing decision, the heat-driven axes: modelled annual gas, seasonal swing,
the insulation ceiling and the turn-down ceiling. **Annual electricity and its half-hourly shape are
absent** until `W2_19` supplies a non-heat electrical base — for the 81% of households on gas that
is appliances, lights and EV rather than fabric. **So every N here is a floor**; adding axes can only
raise it.

**Shape is modelled and not validated**, by the director's decision. The only household shape
artefact available is Elexon Profile Class 1 — one population-average curve on a 1997 reference year
— and NEED is annual. SERL is accredited-access and is not being pursued.

## The population is NEED rows crossed with cells, not aggregated cases

The earlier work bucketed the stock into 274 (type, age, area, EPC) cases. That was right for a
variance question and wrong here: **the intervention axes depend on what is already installed**, and
NEED carries `LI_FLAG`, `CWI_FLAG` and `PV_FLAG` per dwelling. Bucketing averages those away —
precisely the two-households-one-bucket collapse the canon names. A household here is one of 39,502
NEED dwellings crossed with a weather cell, so the joint of fabric with existing measures is the
observed one rather than a product of marginals.

The ceiling is therefore **what is left to do**, not what a bare fabric would gain. A dwelling with
loft and cavity already done has had the cheap measures; crediting it the full retrofit is exactly
how a sample comes to rank two very different customers identically.

## Two defects committed inside the fix, both kept

**A criterion whose bar loosened as the sample shrank.** The first version accepted a sample when its
KS distance fell under the two-sample *critical value* — and that value grows as n shrinks, so a
13-case sample passed trivially because a test that size has almost no power to fail. It returned
**N = 13 and N = 21**, the two smallest sizes on the ladder, which is the answer that criterion will
always give. Replaced with an absolute tolerance, stated as a Choice, with the detectable-discrepancy
reported beside every row so a size too small to verify its own claim is flagged rather than counted
as a pass.

**A test that compared margins while the thing it exists to catch lives in the joint.** The second
version tested each axis separately and returned **the same N with and without the response axes** —
because two households with identical consumption and opposite ceilings differ in the joint and in
neither margin. That is the canon's own complaint, committed one level up, inside its own repair.
Fixed by projecting the standardised vector onto 64 fixed random directions and taking the worst KS
over all of them; the coordinate axes are kept, so the marginal test is not lost. The control uses
two populations with *identical marginals by construction* — the same values paired differently —
and asserts the marginal test cannot tell them apart while the joint test can.

## The prediction, graded

I filed **"thousands to low tens of thousands, dominated by the tail requirement"** before measuring.

**Partly refuted, in the direction of being too high.** At the natural accuracy the floor is 1,200,
not thousands-plus; only at 0.02 does it reach 5,400. And the dominant term is **not** the tail — it
is the joint. The tail intuition came from the earlier space-filling work, where one tail failed to
close at 2,584 houses; that was a *span-the-support* criterion, and this is a *reproduce-the-
distribution* one, which the canon is right to say are opposed. The number can still rise when
electricity lands, so the prediction is not settled — but the evidence so far points lower than I
said, and the reason I gave was wrong.

## Limits

- **England and Wales only** — NEED carries no Scottish dwellings.
- **Modelled gas, not metered.** The population's distribution is the model's; validating it against
  NEED's observed `Gcons2024` (median 10,000 kWh over 39,502 dwellings) is a separate question this
  does not answer, and the canon's "observed distribution" is only fully honoured once it is.
- **PV headroom is not an axis.** `PV_FLAG` is read but roof geometry is not in the premise joint,
  so a PV ceiling would be invented rather than computed.
- **The AST census control** — refusing any coverage, ceiling or sufficiency claim that does not
  declare the dimension it reduces over — is commissioned by the canon and is not built here.

---

## SUPERSEDED 2026-09-07 — the population was missing 18.5% of the stock

**Every number above is wrong and the corrected measurement is in
`the_sample_is_8500_households_once_electricity_and_the_non_gas_stratum_are_in.md`.**

`_need_rows` filtered on `Gcons2024` being present, which keeps only dwellings with a gas meter --
39,502 rows, every one of them `MAIN_HEAT_FUEL = 1`. The entire non-gas stratum, 8,547 dwellings,
was absent. Annual electricity was also declared absent on a `W2_19` dependency it does not have:
NEED carries it per dwelling, and only the half-hourly SHAPE waits on the people joint.

Corrected: 8,500 at tolerance 0.05, against the 1,200 below. **The grading of my prediction as
"partly refuted, too high" is withdrawn with it** -- 8,500 is inside the range I predicted, and a
refutation published from an instrument missing a fifth of its population is worse than none.

Kept rather than deleted, because a wrong prediction beside its correction is the only evidence the
measurement was designed before its answer was known.
