**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0
delivery

# Pre-registration: what the census headcount moves in the book

Delivery seat, 2026-09-16, **written before any run under `fa4f2ea40` exists**. The change it grades
is already landed; the effect is not yet measured and is not yet knowable from anything on disk.

Subject: `fa4f2ea40`, which makes `fabric_demand_path.build_fabric_series` draw its headcount from
the ONS TS017 marginal instead of from bedrooms. Mean headcount over the drawn population moves
**2.71 → 2.34**; one-person households **11.0% → 30.1%**.

The change was made on fidelity grounds and decided blind to P&L (R13). **This document exists so
that the P&L reading, when it arrives, cannot be mistaken for the reason** — and so that a wrong
prediction stays visible beside the result.

---

## The predictions

**P1 — book demand falls.** Total settled kWh across the fabric-driven book falls. A 13.7% fall in
mean headcount does not map one-for-one onto volume — space heat is fabric-driven and barely moves
with occupancy, while hot water, cooking, appliances and metabolic gains all do — so the fall is
**materially smaller than 13.7%**. Stated range: **2%–8%**. Outside that range in either direction
refutes my understanding of which loads occupancy actually drives, and the per-component split
(`space heat / hot water / cooking / electricity`) is what says which.

**P2 — net margin falls, and by less than volume.** Less volume sold is less gross margin, but the
standing charge is per-account and does not move at all, and a one-person household's bill is a
larger standing-charge fraction. So margin falls by **less, proportionally, than kWh**. If margin
falls by MORE than volume proportionally, something is wrong with the standing-charge leg and that
is the finding, not the headcount.

**P3 — metabolic gains fall and heating demand therefore RISES per home.** `premise_trace` credits
`_METABOLIC_GAIN_KW_PER_PERSON * people_count * occupancy` against the heat load. Fewer people is
fewer free watts, so **space-heat kWh per home rises** even as total book volume falls. This is the
prediction most likely to be wrong in sign, and it is stated deliberately because a sign error here
would otherwise hide inside an aggregate that moved the way I expected.

**P4 — the direction is NOT flattering.** I expect this change to make the company look slightly
worse, not better. Recorded because it is the honest expectation and because a fidelity change that
happened to flatter would deserve more scrutiny, not less.

## How it will be graded, fixed now

**One variable.** Two runs at the same seed, same window, same book, differing only in whether
`build_fabric_series` passes `people_count`. Not `fa4f2ea40` against the last published run — there
are dozens of commits between those and the comparison would be unattributable. If only a
head-to-head against a published figure is available, the answer is **"I cannot yet say"**, and that
is a result.

**Reported whichever way it goes**, with this document beside it, corrected in place rather than
revised.

## The kill line

If total book kWh moves by **less than 0.5%**, the change did not reach the settled book at all and
the wiring leg of
`tests/simulation/test_the_settled_book_draws_its_headcount_from_the_census_and_not_from_bedrooms.py`
is passing on something that does not matter. That would be a finding about the control, not about
the world.
