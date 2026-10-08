**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# SEAT PROPOSAL — acquisition selects on each prospect's own responsiveness (2026-10-08)

**For the director's ruling. No world change has been made.** His question (2026-10-08): does the
world hide real correlations between price responsiveness and what a supplier can observe, which
would rig targeting to fail? Evidence and code reading:
`docs/market_research/observable_correlates_of_price_responsiveness.md`.

## What the evidence says, in short

- **The large published correlates are of SHOPPING, not of price weight, and the world already
  carries them.** Fixed against variable 7.0% vs 2.5% switched in six months (2.8×); credit against
  traditional prepayment 3.4× (Ofgem CIM wave 6); a meter read sent 1.3% vs 0.3% (CMOL trial, 2017).
  The engagement axis (`simulation/household_segments.py`) carries payment method, active renewal,
  time on the default tariff (0.50 against CMOL's 0.54) and contact volume.
- **Price weight on its own is near-homogeneous**, supporting the 27 Aug ruling: Ofgem's 2024
  tariff-choice research gives a 1.26× spread, and spend against switching correlates at −0.07 to
  +0.05.
- **Past switching does not carry over** in the only randomised evidence: earlier switchers
  re-switched at 31% vs 33% in Ofgem's 2018 trial control arm.
- **Acquisition channel does**, but Ofgem attributes the effect to the comparison site re-prompting
  people, not to the people: collective-switch joiners re-switched at 69% vs 38%.
- **GAPs:** price response given a household is shopping, split by tariff, past switching, channel or
  contact; churn by channel (the CMA redacted every cell); churn by complaints.

## What the world gets wrong

**A customer won by switching in is no more engaged or price-led than anyone else.** The acquisition
funnel prices every prospect off one population response, so the book a supplier wins is an average
draw. In reality the act of switching in selects the shoppers, so a won book is more responsive than
the market, and that is observable through how and at what price it was won.

## Proposal

1. **Acquisition selects (recommended).** The funnel's price stage reads each prospect's OWN
   sensitivity, as renewals already do, and prospects enter the market weighted by their own
   chance of shopping. No new number is introduced. The correlation with acquisition route and win
   price emerges from the draw. The company still sees only its own quotes, prices and channels:
   the latent value never crosses the seam.
2. **Optional, both arms reported:** draw the high/medium/low sensitivity level by rank on
   engagement instead of independently, keeping the 2% variance share and the 1.26× spread. Run
   fully independent and fully linked and report both, without choosing a middle.
3. **Not recommended:** a past-switching carry-over term. The only randomised trial gives ×0.94.

**What would show it mattered, pre-registered first.** On fresh seeds 101 and 202, in the B8
coin-drawn decision set, add a price-legal read by acquisition route, time on default or
ever-actively-renewed. Change 1 matters if:
- one group reaches break-even on a save offer;
- the learned decision offers only to that group, and beats both flat rules beyond seed noise;
- with change 1 off, it falls back to offering nothing.

## The one question that is yours alone

Your 2026-09-23 ruling ("a price keyed to the meter may not") bars price variation keyed to the
meter. **Does the same bar apply to a retention or save offer keyed to acquisition route or time on
the default tariff?** The FCA banned tenure pricing in insurance in 2022. Whether that is acceptable
in GB energy is a practitioner and regulatory judgement this note cannot settle. My recommendation
is to allow it for save offers made on a loss notice, which respond to the customer's own act, and
to bar it for renewal prices.
