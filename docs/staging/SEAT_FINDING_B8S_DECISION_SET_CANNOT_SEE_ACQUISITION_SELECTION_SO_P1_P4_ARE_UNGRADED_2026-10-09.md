**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout` · **Claim:** `grade-acquisition-p1-p4-on-fresh-seeds-101-and-202`

# B8's decision set cannot see acquisition selection, so P1-P4 for option 1 are not graded on it

The pre-registration is `docs/staging/records/SEAT_PREREG_ACQUISITION_SELECTS_ON_EACH_PROSPECTS_OWN_RESPONSIVENESS_2026-10-08.md`.
Its predictions and its test are not changed here.

## The answer

**This instrument cannot answer the question, so no P1-P4 verdict is recorded. B8's level is unchanged.**
The test asks whether a supplier that selects on each prospect's own responsiveness can then make a
save decision that beats both flat rules. B8's coin-drawn decision set (`simulation.coin_drawn_decision_set`)
cannot test that, for two reasons:

1. **It never goes through the acquisition funnel.** `draw_households` takes households straight
   from `population_draw.draw_population`. Option 1 acts only in the growth campaign's funnel
   (`live_population._resolve_campaign` → `net_new_acquisition`): it changes the order prospects
   are quoted in and the price stage's response. Nothing the decision set draws passes through
   either.
2. **It carries none of the observables P1 groups by.** Its rows hold `payment_method`, `opened_on`,
   bills, billed kWh and the offer. They have no acquisition route, no time on the default tariff
   and no ever-actively-renewed flag. Every household joins at the default and is offered the
   default at every renewal, so "time on default" is not a variable in this set at all.

## Measured, at origin `20c67bb66`, cut £7.5/MWh, 100 households drawn per acquisition year

| seed | switch | arm | decisions | rows digest | true effect |
|---|---|---|---|---|---|
| 101 | off | independent | 1,434 | `eae76df11b9ddd7c` | +0.011436 |
| 101 | on | independent (I) | 1,434 | `eae76df11b9ddd7c` | +0.011436 |
| 101 | on | linked (L) | 1,434 | `131efc2d211ef301` | +0.011392 |
| 202 | off | independent | 1,490 | `2e31a6a39c568f04` | +0.011581 |
| 202 | on | independent (I) | 1,490 | `2e31a6a39c568f04` | +0.011581 |
| 202 | on | linked (L) | 1,490 | `b04581ddf25915dd` | +0.011557 |

- **Option 1 off and option 1 on (arm I) give byte-identical sets on both seeds.** So on this
  instrument, P4's control would be the same run as arm I. Its result would show nothing about
  selection.
- **Arm L does change the set**, because option 2 re-levels every household, founders included.
  This is the placebo leg: it shows the digest can move, so the identical result above is not
  the probe failing to look. Arm L changes the true effect by under 0.4%. That is a change in the
  world's trait draw, not selection at acquisition.
- I did not run the full `decide` at `--fresh-per-year 850`. Its option-1-off and arm-I outputs
  would have the same digests, and the rows have no column P1 could group by.

## Against the predictions (kept, not revised)

- *"P1-P3 hold in arm L on at least one seed, and fail in arm I on both."* **Not graded.** The
  instrument cannot see option 1.
- *"P4 holds in both arms."* **Not graded.** On this instrument the control and arm I are the same
  run.
- The build check on 2026-10-08 had already **refuted** prediction 1 at the shipped price. Winners
  were ~1.00× the market, against a predicted 1.1-1.4×, because the price half scales a market
  differential that is zero at the market-average quote. That result stands. It means that even an
  instrument that does pass through the funnel would draw a book about as responsive as the market
  while the campaign quotes at the market price.

## What would grade it (the seat's recommendation)

The graded subject has to be households the funnel **won**, carrying the three observables the
director named on 2026-10-08:

- **(a) Recommended.** Give `build_decision_set` a source of households taken from the campaign's
  winners (`net_new_acquisition`), each with its acquisition route. Then add `acquisition_route`,
  `days_on_default` and `ever_actively_renewed` to `HOLDOUT_OBSERVABLE_FIELDS`, and walk renewals
  where a household can roll off a fix onto the default. Pre-register on that instrument before
  running it. **Prediction, written now:** with the campaign at the market-average quote, P1 fails
  in both arms on both seeds, because the selection the build check measured is ~1.00×.
- **(b)** Grade on the settled run, which does go through the funnel. A settled customer-year
  costs ~2.7 MB, and earlier work (`3811342db`) found the settled book supplies about 31 decisions
  in band over ten years. That is far short of the ~27,700 per arm the pooled effect needs.

(a) is reversible and adds no number, so it is the next piece of work and does not need a decision
first. The director should know the ruling-2 test was set on an instrument that could not see the
change, and that it has not yet been graded.
