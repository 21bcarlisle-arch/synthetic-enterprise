**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `unminted`

**Knowledge:** none -- the housing knowledge page is deliverable 4 of the housing ruling and is not
yet written. These are the sample-design rows it will publish; the declaration is replaced when the
page lands.

# The sample is 8,500 households once electricity and the non-gas stratum are in

**Measured 2026-09-07**, delivery seat, against `DIRECTOR_CANON_THE_DEMAND_VECTOR_2026-09-07`.
Reproduce with `python3 -m tools.demand_vector_coverage --measure`.

**This supersedes `the_sample_is_1200_households_and_the_joint_is_what_binds.md`, published two
hours earlier. Both its headline number and its grading of my own prediction were wrong, for one
reason, and the correction is at the foot of this document rather than folded away.**

---

## The answer

| tolerance | N to reproduce the distribution | **N to also span intervention response** | dominated by |
|---:|---:|---:|---|
| 0.10 | 1,597 | **1,597** | JOINT |
| 0.05 | 8,500 | **8,500** | JOINT |
| 0.02 | 30,000 | **30,000** | JOINT |

Over 46,234 NEED dwellings crossed with the household-weighted 1 km cell space, 120,000 sampled
points. Tolerance is the accuracy demanded: no point of any distribution misplaced by more than that
share of population mass. At 0.05 — half a decile — **the sample is 8,500 households.**

**The binding constraint is the JOINT at every accuracy**, never a single margin.

**The two numbers are equal, and that is the honest report.** The response axes are harder at some
sizes (KS 0.4597 against 0.4202 at n = 55) but not by enough to move a geometric ladder. What
dominates is reproducing the fuel-stratified joint of gas and electricity; against that, the two
ceilings cost nothing extra. The canon asks for the second number to be treated as the real one — it
is, and today it happens to coincide with the first.

## What was wrong with the earlier figure

**The population was 100% gas-heated and I had not noticed.** `_need_rows` filtered on `Gcons2024`
being present, which keeps only dwellings with a gas meter: 39,502 rows, every one of them
`MAIN_HEAT_FUEL = 1`. **The entire non-gas stratum — 8,547 dwellings, 18.5% of the stock — was absent
from a measurement whose own canon says "gas-heated and electrically-heated households at the same
total are not the same case at all".** The measurement could not see the distinction it was built to
size for.

**And annual electricity had been deferred on a dependency it does not have.** I had declared it
absent "until `W2_19` lands", reasoning that there is no non-heat electrical base in the demand
model. That bundled two axes with different dependencies:

- the **half-hourly shape** needs a presence pattern and genuinely waits for `W2_19`;
- **annual electricity** is carried per dwelling by NEED — 46,234 observed rows, median 2,600 kWh,
  and it separates by fuel (gas-heated 2,500, non-gas 3,200) — and waits for nothing.

The director's words: *"don't defer the axis that turns a floor into a number."* He was right, and
the reason I gave for deferring was not a dependency but a conflation.

Selecting on electricity rather than gas fixes both at once: electricity is near-universal, so both
fuels are kept, and gas becomes a **quantity that is zero for a home without it** — which is what a
home without gas actually consumes.

**Fuel is now a stratum, not a coordinate.** "How far is gas from electric" is not a quantity, so it
cannot be an axis a distance is measured along. The acceptance runs within each fuel stratum and
every stratum must pass, which is what stops the 18.5% being swamped by the 81%. A draw that puts
fewer than two households in a stratum fails closed rather than scoring it.

## The prediction, re-graded — and the earlier grading withdrawn

I filed **"thousands to low tens of thousands, dominated by the tail requirement"** before measuring.

Two hours ago I graded that **"partly refuted, in the direction of being too high"**, on a figure of
1,200. **That grading is withdrawn.** At 8,500 the magnitude is squarely inside what I predicted. The
prediction was refuted on a measurement that was missing 18.5% of the stock and one of its axes, and
publishing a refutation from a defective instrument is worse than publishing no grading at all.

What was genuinely wrong in the prediction is the **reason**: I said the tail requirement would
dominate and it is the joint. That half stands, and it stands more clearly now.

## Limits

- **England and Wales only** — NEED carries no Scottish dwellings.
- **Half-hourly electricity shape is still absent**, so this remains a floor — but a much smaller
  gap than the one it replaces. It is the one axis `W2_19` is genuinely needed for.
- **Shape is modelled and not validated**, by the director's decision; SERL is not pursued.
- **Gas and electricity are observed; the heat model is not validated against them.** The population
  carries NEED's metered values on both fuels and the modelled space-heat demand alongside. Whether
  the model reproduces the meter is a separate question, and the canon's "observed distribution" is
  only fully honoured once it is answered — which is the validation step, now correctly ordered
  after `W2_19` rather than before it.
- **PV headroom is not an axis** because roof geometry is not in the premise joint.
