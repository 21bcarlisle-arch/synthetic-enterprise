# The company learns a retention offer's effect from a coin-drawn holdout, at about 30,000 decisions per arm

**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout`

Claim `b8-the-coin-drawn-decision-set-is-built-and-graded`, 2026-10-07. This is the build the seat
promised the director at 14:54: the second measurement, where the company learns from its own
holdout. The predictions were filed before the graded runs:
`SEAT_PREREG_B8_THE_COIN_DRAWN_HOLDOUT_GRADED_AGAINST_THE_WORLD_2026-10-07.md`.

## The answer

**The company can learn the offer's effect from its own coin, and the estimate is right.** On
every arm, at both sizes and on every seed, the 95% interval covers the world's true effect: 13 of
13 arms. The null arm never claims an effect. The planted arm is found on every seed.

**The size the reply named was too small for this offer, and the seat's own figure was wrong.**
The reply said 3,000–6,000 decisions per arm. That figure assumed a stay share near 0.15. In this
world the stay share at renewal is about 0.60, and a £7.5/MWh cut is worth +0.0115 in P(stay). So
80% power needs **about 28,500 decisions per arm**. At 6,300 per arm the real arm was undecided on
two seeds out of three. At 34,700 per arm it was decided.

**And that size costs minutes, not memory.** A decision costs 4–8 ms and about 380 day-records of
history. 69,000 decisions took 9 minutes, with a traced peak of 139 MB that scales with the rows
kept. A settled customer-year costs 2.7 MB. So per decision, the lean history is roughly 1,000
times cheaper than settlement.

## What was built

- **`simulation/coin_drawn_decision_set.py`, the world side.** It draws domestic households and
  registers them as a run registers its drawn points. It takes them back off the book when it is
  done. At each anniversary it asks `roll_lifecycle_event` for the world's P(stay) at the default
  and at the default minus the cut. That is the probe's question, with the same roll. It then
  flips the coin on the frame's substream `B8_holdout::assignment`. A household that stays renews
  a year later on the rate it agreed, and is drawn again.
- **`company/interfaces/sim_interface.holdout_decision_observations`, the seam.** An allow-list:
  account, date, arm, offered rate, stayed, payment method, and the last twelve bills. The
  world's P(stay) at either offer and the roll never cross.
- **`company/pricing/discovered_price_sensitivity.estimate_offer_effect`, the company side.** It
  reads only those rows. The estimate is the treated stay share minus the held-out one, with
  Newcombe's hybrid-score interval. That interval reproduces Newcombe's published worked example
  (0.0524, 0.3339). The verdict comes from the interval, and an empty arm is refused.
- **`tools/grade_coin_drawn_holdout.py`, the grader.** It runs the real, null and planted arms and
  grades each against the truth.

## The graded runs

The real arm offers the treated household £7.5/MWh below the world's default. The null arm has
no cut. The planted arm adds +0.05 to the world's held-out P(stay).

| size | seed | arm | per arm (T / H) | truth | estimate | 95% interval | verdict |
|---|---|---|---|---|---|---|---|
| S | 42 | real | 6,296 / 6,277 | +0.0115 | +0.0114 | −0.0057, +0.0285 | undecided |
| S | 42 | null | 6,230 / 6,207 | 0 | +0.0005 | −0.0167, +0.0178 | undecided |
| S | 42 | planted | 6,508 / 6,500 | +0.0470 | +0.0492 | +0.0325, +0.0658 | raises staying |
| S | 7 | real | 6,256 / 6,385 | +0.0114 | +0.0112 | −0.0058, +0.0283 | undecided |
| S | 7 | null | 6,200 / 6,312 | 0 | +0.0007 | −0.0165, +0.0178 | undecided |
| S | 7 | planted | 6,470 / 6,560 | +0.0470 | +0.0465 | +0.0298, +0.0631 | raises staying |
| S | 11 | real | 6,620 / 6,505 | +0.0115 | +0.0222 | +0.0056, +0.0389 | raises staying |
| S | 11 | null | 6,540 / 6,431 | 0 | +0.0121 | −0.0048, +0.0289 | undecided |
| S | 11 | planted | 6,775 / 6,715 | +0.0470 | +0.0594 | +0.0431, +0.0757 | raises staying |
| L | 42 | real | 34,674 / 34,792 | +0.0115 | +0.0117 | +0.0044, +0.0189 | raises staying |
| L | 42 | null | 34,371 / 34,491 | 0 | +0.0020 | −0.0053, +0.0093 | undecided |
| L | 42 | planted | 35,785 / 35,894 | +0.0470 | +0.0471 | +0.0400, +0.0542 | raises staying |

### Graded against the pre-registration

1. **Real arm, size S. Held.** The truth was between +0.0114 and +0.0115 on every seed, inside
   the predicted +0.008 to +0.020. The verdict was undecided on two of three seeds, and every
   interval covered the truth.
2. **Real arm, size L. Held.** The verdict was "raises staying", and the interval covered the
   truth.
3. **Null arm, both sizes. Held.** Undecided every time, and every interval covered 0.
4. **Planted arm, size S. Held.** The truth was 0.0470, just under 0.05 because the cap at 1
   binds. The verdict was "raises staying" on every seed, covering the truth.
5. **Cost. Held.** It ran at 3.7–8.0 ms and about 380 day-records per decision. The traced peak
   was 16–44 MB at size S and 108–139 MB at size L, so memory grows with the rows kept and
   nothing else. It is at least 100 times cheaper than settlement, as predicted, and in fact
   about 1,000 times.

**One reading I would have got wrong without the null arm: seed 11.** The real arm says "raises
staying" at +0.022, nearly twice the truth. On one seed, the real and null arms share their
households, their coin and their rolls. Seed 11's null arm reads +0.012 on no effect at all. So
half of that "detection" is the coin's chance imbalance in who stays, which the real arm inherits
as well. Real minus null on seed 11 is +0.0102, against a truth of +0.0115. The interval was still
honest, because it covered the truth. But one 6,000-per-arm holdout that "found" the effect would
have overstated it by about 2 times. That is what being underpowered looks like when it happens to
come out positive.

## What this does not establish

- **The world's curve could be wrong.** The truth here is the churn curve we wrote. This shows the
  company can learn the curve from a holdout. It does not show the curve is the real one. That is
  for full settlement and the published evidence, as the director said.
  [EFTC](../../market_research/how_households_respond_to_supplier_contact.md) found no effect of a
  supplier contact on external switching. A rate cut is a different offer, and nothing published
  sizes its effect.
- **The history is thinner than settlement**, and each gap is named in the module and in B8's
  simplification record:
  - electricity only, flat at EAC/365 a day;
  - no gas leg in the felt bill;
  - the competitor ledger, the wholesale forward, satisfaction, the passive cap and the debt
    objection are held at the world's neutral.

  One check came out consistent. On the 2026-10-03 full-engine probe (`probe_full.json`, 82
  settled decisions), a £5 cut raised P(stay) by 0.011 on average. The lean set gives about 0.0077
  per £5 at offers on the default. The probe's grid sat above the default, where the curve is
  steeper, so the two agree in order and not in level. The mean stay share is 0.613 on the full
  engine and 0.60 here.
- **The offer is a rate cut only.** The run loop's other retention route,
  `RETENTION_EFFECTIVENESS = 0.20`, is unsourced and is not used. `3811342db` declined to adopt it.
- **The company does not use the estimate yet.** No guard or price reads it. Two things wait for
  L2:
  - the effect per payment channel, which needs about 28,500 decisions per channel arm;
  - the misclassification cost the B8 frame names.

## Reproducing it

```
PYTHONPATH=. python3 -m tools.grade_coin_drawn_holdout --seeds 42 7 11 --per-year 850 --out S.json
PYTHONPATH=. python3 -m tools.grade_coin_drawn_holdout --seeds 42 --per-year 4700 --out L.json
```

Size S takes about 9 minutes, and size L takes about 20.

## Controls

Every control in `tests/simulation/test_coin_drawn_decision_set.py` (7) and the three new ones in
`tests/company/test_discovered_price_sensitivity.py` went red under its own mutation:

- a coin that never holds out;
- a stay that is not the world's;
- a truth field on the allow-list;
- a set that leaves its households on the book;
- a cut that reaches no offer;
- a verdict read off the point;
- the arms swapped.
