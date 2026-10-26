**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Every Explore example must make sense to an energy reader, and the examples become a standing check (2026-10-26)

**Type:** STEER, through the advisor channel. The director's words, from chat on Mon 26 Oct:

- 18:24 GMT: "Can you check the explore examples make sense? And can you get it to check them. We seem to be finding errors often when we look at what's actually happening as examples of functionality"

He pasted the published Explore page as read at about 18:20. The advisor checked it against `site/data/explore_cast.json`, `customer_sample.json` and `customers.json` at 67a893e7.

**Seven of the eight feature slots are filled, and five of those seven tell a story an energy professional would reject.**

The pattern matters more than any single defect. The slot rules select on a number, such as "moved its use the most" or "longest run". They never check that the household they pick is a valid instance of the feature. So each published example is chosen for being the most extreme case the run produced, and the extremes are where the model's errors live.

## What is wrong, slot by slot

1. **The EV home (SYN-2016-476): wrong in four ways.**
   - **The household is gas-only.** The page says "the supplier sees it only as more electricity on the meter", but Poesys supplies no electricity here.
   - **The "EV effect" is −65%** (1,353 → 473 kWh/mo). An EV adds load. This is a gas winter-to-summer drop around 16 Apr 2022, read as the car's effect. The rule compares raw before/after averages without any seasonal or weather normalisation, and it does not restrict to the electricity leg.
   - **It moved to prepayment on 14 Mar 2022 with 0 missed payments.** Why does a fuel-poor household that never missed a payment move to prepayment, and on what basis? A prepayment household is also shown monthly bills on estimated reads, "£42.73 to pay" and "£42.73 owed". Prepayment is paid in advance at the meter, so it has no estimated bills and no arrears balance in this form. Either the payment model treats prepayment as a credit account, or the label is wrong.
   - **Its gas price through the crisis looks far under the cap.** The Jan 2022 bill is 1,622 kWh for £74.46. That is about 3.9p/kWh before the standing charge, and `annual_pnl` 2021 shows a tariff max of £38.76/MWh. The cap's gas unit rate for Oct 2021–Mar 2022 was about 7.4p. "0 bills over the cap" is the wrong test for this: a Standard Variable tariff priced at half the cap during the crisis is just as wrong. **Check whether every SVT in Oct 2021–Mar 2022 was priced this far under the cap.** If it was, the crisis P&L is understated, and so is the headline that it lived through 2021–22.
2. **Storage heating (C1): not a storage-heating home.**
   - Its first electricity bill is 100 kWh in January (£18.31). A storage-heated home uses well over 1,000 kWh in January.
   - The span runs 1 Jan to 20 Apr 2016, and the slot has no story text, so the page shows the heading with nothing under it.
   - `C1` is not the public ID format. The six-stage section's default account is the same C1, with "4 bills issued" and "since 2016", so it is also a weak default.
   - On 25 Oct the advisor recorded that the run has no two-rate meters. Check whether a real PC2 Economy 7 home exists. If not, the slot should be honestly empty and not filled with this one.
3. **The 2022 shock (PROS-2017-0336): a usage error and an estimate presented as a shock.**
   - The household uses 3,129 kWh of electricity a month, about 37,500 kWh a year, roughly ten times a typical home.
   - The January bills in both years are the same 3,129 kWh and the 2022 one is estimated. The "same use, 63% more" story is a repeated estimate, not observed use.
   - The gap panel lists "Bill of £1,080.02" as what the supplier *believed* and billed use as the *truth*. That is not a belief/truth contrast.
4. **The estimate trap (SYN-2016-587): the example contradicts a capability claim.**
   - It shows 33 estimated bills in a row, with no read from 30 Apr 2021 to 29 Feb 2024.
   - The home page states the supplier "instructs a meter visit when a year passes on estimates, as the read duty requires (SLC 21B.4)". Either the duty did not fire here, or the example shows that it is not enforced.
   - A £7.03 catch-up after 33 months of estimates is also improbably exact. Check whether the estimate is being fed the true consumption.
5. **The debt journey (SYN-2016-356): plausible, but it needs one check.**
   - The account leaves in Aug 2018. Arrears go £71.73 → £147.56 → £866.50, and it is written off as statute-barred on 28 Jun 2024. Confirm that the six-year limitation clock runs from the last payment or acknowledgement in the record.
   - Show amounts as "£", not "GBP".
6. **The mover: empty, while the home page says households move.**
   - The slot says the record carries no move-out event or final-bill marker. Either the claim "households move" comes off the home page until moves reach the record, or the run must produce one.
   - The page footer says "7 of 8 slots filled" while showing two slots without a story. That count should match what is on screen.
7. **The household count is inconsistent across pages.** Explore says the book is "all 752 households", and the home page says "750 households served over the whole run". Use one count, defined once.

The switch-in and renewal slots were not challenged in this read.

## Tonight, before the externals visit

- **Fix what can be fixed safely.** Any slot that still tells a story an energy reader would reject at the end of today should show as **empty with its reason**, for example: "No household in this run passes this example's checks yet; the check that failed is …". Do not leave it published as it is. An honest empty slot costs nothing, and a gas-only EV home costs credibility.
- This applies at least to the EV home, storage heating and the 2022 shock. Change the default six-stage account from C1 to a household with a full, ordinary record.

## The standing check the director asked for: "can you get it to check them"

Examples are the best test the project has. They are the only place where the whole system's behaviour is visible on one household, end to end. Make them a gate, in two layers.

1. **A validity predicate per slot, run at publish.**
   - Each rule selects only among households that pass its feature's sanity checks, and then ranks by the extreme.
   - Minimum checks:
     - **fuel matches feature:** an EV or storage-heating home holds an electricity leg, and a storage-heating home is profile class 2 with winter use in its band;
     - **direction and size match the physics:** an EV raises electricity use by a weather-normalised amount in the published band, compared like-for-like on the same season;
     - **payment method matches billing:** a prepayment household has no estimated credit bills and no arrears balance shown as a bill;
     - **price is within a band:** an SVT unit rate sits between the period's wholesale cost and the cap, not just under the cap;
     - **use is plausible:** monthly use falls within the population's 1st–99th percentile for its fuel and segment, or the slot says why it is extreme;
     - **duties are consistent with the capability claims:** no run of estimates longer than 12 months without the read duty firing;
     - **the gap panel is a belief set against a truth**, never a figure set against another figure;
     - **IDs are in the public format;**
     - **counts match the screen.**
   - A slot that finds no valid household shows as empty with the failing check named. That is a finding about the run, and it is filed as one.
2. **A cold domain read of every published example, each publish.**
   - After each Monday publish, a fresh reader agent reads each Explore story as a GB retail-energy professional, with no access to the code or this steer, and answers one question: "Would an energy professional believe this? If not, what is wrong?"
   - Every objection becomes a finding, and every confirmed finding becomes a new predicate in layer 1, so the same error cannot be published twice.
   - Track the hit rate. If the reader stops finding anything for several weeks, widen it to the six-stage section and to a random household as well as the extremes.

The same principle should extend beyond Explore. **Any figure the site shows as "an example of it working" is a test case first.** Run the cold read over the home page's capability claims against what the examples actually show; the estimate trap against SLC 21B.4 is the model case.

## Ask

- Tonight: fix or honestly empty the failing slots, and change the default account.
- File each numbered defect above as its own finding, with its owner lane. The SVT-far-under-the-cap question (1, last bullet) is a model correctness finding, not a site one, and it may move published P&L. Check it first among the model findings.
- Build layer 1 as a publish gate and layer 2 as a post-publish reader, and report both in the next reading.

## Done

*Autonomous worker, 26 Oct 2026, about 19:30 GMT, on origin/main 89ba56215f.*

### Tonight's step, landed

`tools/generate_explore_cast.py` now ranks each slot by its extreme only among households that pass its
checks. Each check is named in the code with its source. A slot with no passing household is shown
empty, with the number of households that matched its rule and the checks they failed.

The rebuilt cast fills 5 of the 8 slots:

- **EV home:** empty. 21 households match the rule and none passes. SYN-2016-476 fails on "holds no
  electricity supply with us". The next candidate stated +17%, about 370 kWh a year.
- **Storage heating:** empty. All 96 two-register homes are smart Peak/Off-peak meters on a standard
  variable tariff, and none names a profile class 2 meter.
- **2022 shock:** now PROS-2019-0246, on actual reads, £311.08 to £596.06. The gap panel is removed.
- **Estimate trap:** now PROS-2017-0264, 12 gas estimates and then a £45.43 credit, inside the read-duty year.
- **Debt:** SYN-2016-356 stays. Its last payment was 28 Jun 2018 and the write-off was 28 Jun 2024,
  exactly six years later. "GBP" now shows as "£".
- **Default account:** the six-stage section now opens on SYN-2016-434, chosen by a stated rule. It used
  to open on C1.
- **Slot count:** the footer's count is now the true one, 5 of 8. The empty slots carry their reasons.

### Defects filed as findings

Each numbered defect is filed with its owning lane:

- `SEAT_FINDING_AN_EV_LIFE_EVENT_...`
- `SEAT_FINDING_A_PREPAYMENT_HOUSEHOLD_...`
- `SEAT_FINDING_THE_2022_SHOCK_...`
- `SEAT_FINDING_A_THIRD_OF_HOUSEHOLDS_...`
- `SEAT_FINDING_A_STATUTE_BARRED_...`

These defects are open in the summary finding, `SEAT_FINDING_EXPLORES_SLOTS_PICKED_THE_EXTREME_...`:

- storage heating, on the 23 Oct cast finding
- the mover and the home page's "households move"
- 752 households against 750
- the non-public ids

### Correction, beside the claim (point 1, last bullet)

The cap in force in Jan 2022 was **4.07p/kWh** for gas, from the Oct 2021–Mar 2022 window. 7.37p is
the April 2022 cap. SYN-2016-476's bill is about 4.6p all-in including the standing charge. The book's
standard variable bills sit at the cap in every window from 2021 to 2023: the median ratio is 1.00. So
standard variable tariffs were not priced at half the cap, and the crisis P&L does not move on this
account.

The floor side, "above wholesale", is a GAP. The generator has no wholesale cost per period.

### Not done here

Layer 1 as a standing suite over every household, and layer 2, the post-publish cold reader, are
carried by the ruling's steps 4 to 6 (`DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`,
still open). Tonight's per-slot checks are the start of layer 1: they run at publish, with
`generate_explore_cast`, but only on the cast.

The page goes live when the publisher next writes the site. This commit rewrites
`site/data/explore_cast.json` and the page's static block in the tree.
