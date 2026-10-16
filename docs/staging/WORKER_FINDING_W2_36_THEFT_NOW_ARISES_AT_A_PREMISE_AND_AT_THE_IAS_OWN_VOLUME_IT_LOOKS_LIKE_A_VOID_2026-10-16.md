**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality`

# W2_36: theft now arises at a premise, and at the IA's own volume it looks exactly like a void

**Fate (2026-10-16):** ATOM -- the next W2_36 slice grades the company's screen
(`company/billing/theft_indicator.py`) against the world's thefts and voids together.

## What was built

This is the third item in the order for the director's ruling 4 of 2026-10-08
(`SEAT_PROPOSAL_THE_ORDER_FOR_VOIDS_VULNERABILITY_AND_THEFT_2026-10-08.md`): theft as a
premise-level study in the minutes tier. The new code is in `simulation/meter_reads.py`:

- `premise_theft_months` gives a premise a theft state as a two-state chain held stationary at
  `q6_theft_prevalence_domestic_electricity`, with turnover set by `q6_theft_months_before_detection`.
- `premise_theft_study` returns true use, what the meter registers, and the stolen kWh.

No run reads either function, by design: 52,000 customer-years buy about 30 detections.
Knowledge: `unbilled_energy_and_revenue_assurance.md` K4 and §5, plus a new register row,
`q6_theft_share_of_premise_use_unregistered`.

## Printed at real inputs (20,000 premises, 120 months, 333 kWh a month)

| Quantity | Value | Against |
|---|---|---|
| Theft stock, months 0 / 60 / 119 | 0.84% / 1.01% / 1.22%; mean 0.99% | register 1% |
| Stolen share of throughput | 0.99% | TEM 0.5–0.9%, AUG studies 1–2.5% (all sectors) |
| Premises that steal at some point in ten years | 5.8% | not published |

## The finding

**At the volume the IA implies, a domestic theft registers nothing.** The 2014 IA's case counts
are "consistent with" £250m only if each domestic case takes all of an average home's use. At its
own Table 4 inputs that gives £248m; at half the use it gives £166m. So the register's default is
1.0, and its partial-tamper end is a GAP.

At 1.0 a theft premise shows the company the same actual/EAC ratio of 0 as a B7 void, which the
world now also draws. A ratio screen alone cannot tell the two apart, whatever threshold is
chosen. What separates them in reality is outside the ratio:
- a void has no occupier, so letters go unanswered and a change of tenancy follows;
- a theft has someone living there, often paying.

Grading that is the next slice. **I cannot yet say** how many voids a ratio screen would send to
investigation for each theft it finds. That needs the world's void rate and theft rate on one
population. Prediction, written before it is run: at the defaults, voids outnumber thefts among
the screen's zero-ratio premises, because 1% of premises are stealing at any time while every
move-out opens a void.

## Mutation record

Each of these was run on a copy loaded into `sys.modules`, so the shared tree's file was never
mutated. Every one turned the theft tests red:
- theft never starts;
- theft never ends;
- the meter ignores the hidden share;
- the refusal of a zero share is removed.

A placebo run with the source unchanged stayed green.

## Graded: thefts outnumber voids in an empty month, and the window does the separating (worker, 2026-10-16)

**Correction beside the prediction above.** I predicted "voids outnumber thefts among the screen's
zero-ratio premises". **That is refuted.** Probe: `tools/theft_void_screen_probe.py`, using the
world's own moves, voids and thefts on one population. Control:
`tests/tools/test_theft_void_screen_probe.py`, mutation-proven over four arms plus a placebo.
Grades: `records/WORKER_PREREG_W2_36_WHAT_A_RATIO_SCREEN_FINDS_AMONG_VOIDS_AND_THEFTS_2026-10-16.md`.

The ratio cannot tell a void from a theft. **Length can.** A void runs 0.7 to 1.15 months and a
theft about 24. So what a screen flags depends on its window and its cut. The ratio itself decides
nothing.

| Flags per 10,000 premise-years | thefts | private voids | social voids |
|---|---|---|---|
| Month empty (ratio under 0.05) | about 1,100 | 0.2 | 112 |
| Month under 0.4 | about 1,100 | 848 | 430 |
| Month under 0.65 | about 1,100 | **1,740** | 669 |
| Year under 0.65 | 84–107 | 0 | 0 |

- An empty month is a theft about nine times in ten in a social let (1,166 of 1,278), and almost always in a private
  let. A private void (about 21 days) cannot empty a calendar month.
- Voids outnumber thefts only at a loose monthly cut, and only in private lets. That is where a
  ratio screen would send investigators to empty homes.
- An annual screen flags almost only thefts, but it sees about a tenth as many. It needs a theft to
  cover most of a calendar year, so it detects late.

**What this cannot say, carried as GAPs:**
1. **The void tail.** The world's void is one fixed length per tenure (the register gives a
   centre and a range, not a distribution). Empty-month voids come entirely from long voids. At
   the social high end (2.0 months) they rise from 112 to 502. A real tail of months-long voids
   (probate, empty-at-sale) is unpublished, so 112 is a floor.
2. **Owner voids** are a GAP (`q1_void_months_owner`). Owner rows show thefts only.
3. **Low-use occupied homes.** Use here is flat at the EAC, so the third source of flags is not
   priced. That is the next slice: run the same probe over the world's own household demand, so
   the screen's false positives include homes that simply use little.

**Fate (2026-10-16, after grading):** ATOM -- W2_36's next slice prices the third source (low-use
occupied homes, from the world's household demand) in the same probe.
