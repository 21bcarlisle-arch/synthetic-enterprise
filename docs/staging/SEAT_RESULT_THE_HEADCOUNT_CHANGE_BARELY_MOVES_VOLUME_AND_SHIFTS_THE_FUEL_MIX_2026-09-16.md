**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0
delivery

# The headcount change is a FUEL-MIX change, not a volume change — both my predictions were wrong, and one of them I "confirmed" off a number smaller than its own noise

Delivery seat, 2026-09-16. Grades
`docs/staging/records/SEAT_PREREG_WHAT_THE_CENSUS_HEADCOUNT_MOVES_IN_THE_BOOK_2026-09-16.md`,
written before any of this could be known. The prediction is kept beside the result, uncorrected.

Subject: `fa4f2ea40`. One variable — same premises, same households, same weather (real Open-Meteo
C1, 2022), same seed, same shipped `build_fabric_series`. The control arm is the real
`behaviour_profile_for` with `people_count` dropped, which is exactly the state the tree was in
before the commit. Harness: `tools/headcount_counterfactual.py`.

---

## The measurement, at four sample sizes

| | n=60 | n=150 | n=600 | n=1200 |
|---|---|---|---|---|
| headcount move | — | −4.91% | −9.06% | **−11.65%** |
| **electricity** | −6.54% | −2.41% | −3.80% | **−5.55%** |
| gas | −0.49% | +0.30% | +0.10% | **−0.046%** |
| total kWh | (in band) | −0.49% | −1.00% | **−1.54%** |

`draw_premise_population(n, …)` takes a different SAMPLE at each n, not a subset, so the treatment
strength itself varies: −4.9% at n=150 against −11.65% at n=1200, approaching the −13.7% measured
over the full population. Ratios, not levels, are what compare.

**Electricity elasticity to headcount: 0.49, 0.42, 0.48** at n=150/600/1200. Stable. That is the
finding.

## The verdicts

**P1 — REFUTED, robustly.** I predicted total book demand falls 2%–8%. Total elasticity to headcount
is **0.13**; scaled to the population's −13.7% that is about **−1.8%**, less than half the bottom of
my band, and the three usable sample sizes agree.

**P3 — REFUTED, and not in the way I'd have guessed.** I predicted gas per home would **rise** as
metabolic gains fall. It does not move: **−0.046% at n=1200**, converging to zero as n grows
(+0.30 → +0.10 → −0.046). The mechanism is real in `premise_trace` — fewer people is fewer free
watts against the heat load — and it is **cancelled** by the other direction: fewer people is also
less hot water and less cooking gas. Two opposite effects inside one fuel, both small, netting to
nothing measurable.

**P2 — NOT GRADED.** Margin needs the money path. It is not inferred from volume here and must not
be read off this document.

## The mistake I made reading my own result, recorded because it is the whole lesson

At n=600 gas per home read **+0.098%** and I wrote **"P3 HOLDS"**. That was wrong, and it was wrong
before n=1200 disagreed with it: the quantity had already read +0.302% at n=150 and **−0.489% at
n=60**. A number that changes sign across the samples you have in hand is not evidence of a sign.
I took the one reading that matched my prediction and called it confirmation.

**A reading of chance has two causes**, and I checked for neither. The honest statement available at
n=600 was *"the gas leg is inside this instrument's noise floor and P3 is not gradable here"* — and
n=1200 has now turned that into a real verdict only because the convergence toward zero is itself
the evidence.

**The instrument has a floor and it is about n=500.** At n=60 BOTH verdicts invert: P1 reads HOLDS
and P3 reads REFUTED, on the same code, for no reason but the draw. Any future run of this harness
below ~500 premises is reporting its sample, not the world.

## Why P1 was wrong: I summed two legs with opposite signs

**Total kWh across two fuels is not a quantity that could answer the question I asked of it.** Fewer
occupants means less electricity — appliances, lighting, hot water — while gas barely moves at all.
Electricity −5.5% against gas −0.05% reads, in the sum, as a book that hardly changed. The book
changed a great deal; its **composition** changed.

This is *before dividing two numbers, say out loud what each one counts*, committed by me, in a
prediction filed two hours after I wrote a stretch entry about that same class. The aggregate was
chosen because it was the obvious headline, not because anything about the mechanism suggested the
two fuels would respond alike — and the mechanism was in `premise_trace`'s own source, which I had
read that afternoon.

**My kill line was on the wrong quantity too, and it fired.** *"If total book kWh moves by less than
0.5%, the change did not reach the settled book at all."* At n=150 it moved 0.491% and the kill line
declared the wiring control worthless. That was **false** — the per-commodity split shows the change
arriving plainly — and it was false for two independent reasons: a cancelling aggregate, and a
sample too small to carry the verdict. Only one of those would have been caught by running more
premises.

**The correct kill line, for whoever reads this next:** the change reached the book iff
**electricity** volume moves with headcount, at n ≥ 500. Gas is the wrong leg — fabric-driven and
insensitive — and the total is the worst of the three.

## What this means for the supplier

**The headcount fix is a fuel-mix change.** On a gas-heated book priced under separate cap legs per
fuel, at different unit rates and different standing charges, −5.5% electricity against flat gas is a
real margin and carbon effect that a volume-only reading records as nothing happening.

It also sharpens why the original defect mattered. One-person households were the band we were
missing, and what makes them distinctive is **not** how much they consume — it is the composition:
proportionally much less electricity, the same fabric-driven heat, and a far larger standing-charge
share of the bill. **A world with a third of them was wrong about the mix, not mainly about the
size.** That is a different and more consequential error than the one the 2026-09-08 finding
described, and it is the reason this counterfactual was worth running rather than assuming.

## What remains

- **P2 is owed.** Margin and carbon need a run through the money path, one variable, reported
  whichever way it goes. Not in this document and not inferable from it.
- **The 0.46 electricity elasticity is measured, not explained.** Whether it is the right
  sensitivity is a question for `demand_model.occupancy_volume_factor` and its published anchor, not
  for this harness.
- **The gas cancellation is asserted from the code, not measured.** I have not separated the
  metabolic-gain rise from the hot-water-and-cooking fall; I have only shown their sum is ~0. Two
  effects netting to zero and one effect being absent look identical here, and I am not claiming to
  have told them apart.

## Class registration

Belongs to `measurements_that_mirror`.
