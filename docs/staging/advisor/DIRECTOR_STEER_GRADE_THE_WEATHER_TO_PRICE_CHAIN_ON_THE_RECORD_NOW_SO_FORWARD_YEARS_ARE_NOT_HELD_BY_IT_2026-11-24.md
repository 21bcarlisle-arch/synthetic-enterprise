**Severity:** BLOCKING · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Grade the weather-to-price chain on the record now, so forward years are not held by it

**Type:** STEER, through the advisor channel. The director's words, from chat, Tue 24 Nov:

- 05:32 GMT: "How far are we away from being stable and accurate enough to start simulating new years of weather and prices and not just history?"
- 05:33 GMT, to the advisor's recommendation to check the price chain now: "Yes"

## What the advisor told him

- Forward years are planned and approved (the 25 Oct six choices, and the 25 Oct and 11 Nov steers). They wait on the correctness exit test. Legs 1 and 3 are not met. The newest book is refused on 9 breaches against a maximum of 8. The eleventh and twelfth reads each found one serious class, converging from three or four.
- The advisor's estimate: one or two clean books and one clean read, about 1-2 weeks, then the forward-years build at up to about 15 points of a week in pieces, about 1-2 weeks inside the feature third. That puts the first forward futures around early to mid December.
- **The concern he accepted:** `sim/weather_price_chain.py` prices the daily mean with a **£24/MWh MAE against a real mean of £78** (FORWARD_YEARS_RECOMMENDATION §0, §3). That is about 30%. Forward years will form price from this chain, and hedging will be judged on it.

## What is asked

1. **Grade the chain on the 2016-2025 record now.** This is grading on the record, not a forward run, so it is allowed before the exit test (FORWARD_YEARS_RECOMMENDATION §8, "holding position"). Use his two steers as the acceptance frame:
   - **Volatility at every scale:** half-hourly, daily, weekly and seasonal distributions and the extremes, against the record.
   - **Weather and price move together, and spells last:** the cold-and-still premium, spell length and autocorrelation, and the joint distribution of weather and price.
   - Report the error **by regime**: pre-crisis, 2021-23, post-crisis. A single MAE across a gas-price shock hides where it fails.
2. **Pre-register the acceptance bands first.** What error is good enough for the questions forward years will answer? For hedging and pricing, that means a forward's value and a supplier's cost of supply. Answer that question before the run, under R5. A per-day MAE may matter less than whether the monthly and seasonal costs a hedge book sees are right.
3. **If it fails, find out why (the 22 Nov curiosity steer).** Candidates:
   - the gas floor;
   - the residual-demand-to-price mapping;
   - missing interconnector or outage terms;
   - the fleet changing over 2016-2025.

   Fix the largest cause, or state plainly the error that forward figures will carry, beside every figure (§3, "known error").
4. **Place it first in the feature third** in Sunday's weekly review, or earlier if the third has room this week. It must be done before the exit test is met, so that the price model is not the next hold.
