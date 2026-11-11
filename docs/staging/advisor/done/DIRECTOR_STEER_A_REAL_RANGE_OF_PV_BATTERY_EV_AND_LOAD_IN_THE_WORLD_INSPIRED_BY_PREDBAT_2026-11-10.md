**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] A real range of PV, battery, EV and load in the world, with Predbat as inspiration (2026-11-10)

**Type:** STEER, through the advisor channel. The director's words, from chat on Tue 10 Nov:

- 19:24 GMT: "We are a theoretical commercial not a real one"
- 19:26 GMT: "I don't want to copy it's code. Just create short cuts and be inspired by it and learn from it. I also want to make sure we have a range of customers with different configurations of PV, battery, EV mileage and load size and shape."

## 1. Predbat: learn from it freely, copy none of its code

Poesys is a simulation, not a trading company, so his reading is that it is non-commercial. Predbat's licence still forbids redistribution, and our repository is public. So:
- **Fine:** read its documentation and code to understand it; take its ideas and approach as shortcuts; reimplement in our own words.
- **Not fine:** no Predbat code in the repository.

Its documented practices are a ready-made starting point for how a battery or EV household optimises against a tariff:
- a 48-hour look-ahead re-planned every few minutes;
- end-of-horizon value for stored energy;
- a pessimistic blend on the solar forecast;
- planning against a do-nothing baseline;
- load learned from history.

Cite it as a source in the knowledge page.

## 2. The outcome wanted: the world's households span the real range

What the advisor read in the code (check it):
- `simulation/premise_population.py` says "Solar PV and EVs are OFF for every drawn premise", by deliberate one-variable discipline. Switching them on, anchored to EHS 2023-24 (solar 5.9%, EV 7.4%), "is the next change".
- Where PV exists it takes one inherited size (`INHERITED_DOMESTIC_PV_KWP = 3.8`).
- Drawn homes have `has_battery=False, battery_kwh=0.0` and `ev_charger_kw=0.0`.
- The heat-pump share (0.008) is marked unanchored.

So today the world cannot show the households where personalisation matters most.

Wanted: a population whose homes span the real GB range, and whose combinations are realistic, not independent coin flips:
- **PV:** presence and size (kWp), orientation where known, and install vintage, which bears on export terms.
- **Battery:** presence and capacity, and how it is run (self-consumption, tariff-optimised, or idle).
- **EV:** presence, annual mileage, charger power, and when and where it charges (home, smart or dumb, workplace or public).
- **Load:** annual size, and the shape of the day and the year; with heat pumps and electric heating as part of the shape.
- **Joint patterns:** solar with battery, EV with a driveway, all of these with tenure, income and property type. The W11 amendment of 3 Nov lets licensed survey microdata inform these joint patterns, with only aggregates leaving Skynet.
- **The tails must be present,** not averaged away: a high-mileage EV with no solar, a big array with a big battery, a small flat with storage heaters. The 23 Jul scenario canon's discipline applies: oversample rare combinations, keep the true-probability weights, and never conflate the two.

## How

- **Knowledge first (K8).** Before any constant, a knowledge page sets out what the published record establishes and what is GAP:
  - PV sizes: MCS and the feed-in-tariff register;
  - battery uptake and size;
  - EV ownership and mileage: DfT and the National Travel Survey, and DVLA;
  - charging behaviour;
  - consumption distributions and daily shapes: SERL smart-meter data, Elexon profile classes, Ofgem's typical consumption values;
  - heat-pump uptake.

  Grade each. Where nothing establishes a figure, carry the gap explicitly.
- **One variable at a time,** as the code itself says. Switch on and anchor one asset at a time, and say what each change moved.
- **The invariant gate holds.** Every new combination must pass the domain invariants before any example is published, for example an EV whose charging exceeds its charger's power, or export above generation.

## Where it ranks

This is world fidelity. It is the director's priority, but it sits inside the 3 Nov world-additions order and the correctness exit test. Say where it lands in that order and why. If it should jump the queue, raise that with a recommendation.

## Risk

Touches: the population draw, household demand, the premise trace, and their knowledge pages.
Blast radius: every run's population. Re-baselining is expected and must be stated.
Probable failure modes:
- Independent draws producing impossible or implausible combinations, such as a battery without solar at improbable rates, or an EV without off-street parking charging at home. Draw jointly, and test the co-ownership rates against the published record.
- Averages that hide the tails, which is the collapse failure.

Proportionality: contract-touching — implement with the named mitigations (knowledge first, one asset at a time, invariants before publish).

— Director steer, 10 Nov 2026, his words above; the code reading and drafting are the advisor's.

## Done

(seat executor, 10 Nov ~20:50 GMT.) **Seen; moved on the executor's instruction.** The executor refused this file:
its header names lane `W`, which is not a known lane. The director's words above are quoted all the same, so
the steer was filed rather than shelved. It is asset-world fidelity, which is priority step 8 ("the personalised
asset world, drawn per home"), held behind the correctness stretch (`ahead_of_steps: [6..13]`). It goes in
`held_behind_the_exit_test` in `docs/direction/priority_order.yaml`, first among the three asset steers of 10 Nov,
because the other two build on it. **Where it lands, as the steer asks:** at the head of step 8 when the exit test
clears. It should not jump the queue. Nothing in the current book's breaches comes from the asset range, and the
ruling of 26 Oct names the asset world as held work. Knowledge first (K8): the range's sourced distributions come
before any draw. Predbat is read for ideas only, and its personal-use licence keeps its code out.

(Corrected 11 Nov: the header lane read `W`, which is not a lane in `background/finding_severity.py`; it now reads `W2_customer_generator`, as the advisor asked in the 11 Nov forward-weather steer.)
