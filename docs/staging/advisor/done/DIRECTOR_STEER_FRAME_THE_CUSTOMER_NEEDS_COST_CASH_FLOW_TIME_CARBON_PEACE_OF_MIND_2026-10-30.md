**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Frame the customer needs a supplier serves (cost, cash flow, time, carbon and peace of mind, above a comfort and health floor), and bring back the canon wording (2026-10-30)

**Type:** STEER, through the advisor channel. These are the director's words from chat on Fri 30 Oct:

- 13:08 GMT: "I wonder if money, time, carbon and worry (risk and uncertainty) arr the mix of customer needs that are being optimised by energy products and services?"
- 13:09 GMT: "What about control? Or cash low? Or is that part of money? I'm thinking why do some people pay more deliberately by cash or prepayment rather than have DD discount and smoothing?"
- 16:13 GMT, on the advisor's proposal to frame it and bring back canon wording: "Yes"

**Why this matters.** Canon M3 names three currencies: money, time and carbon. The director is asking whether that is the whole set of needs that energy products and services serve. Some behaviour cannot be explained by money, time or carbon:

- people fix their tariff above the expected variable price;
- people pay more by cash or standard credit, or choose prepayment, when a DD discount is on offer;
- people accept level DDs that build summer credit.

**This is a canon question, and only the director edits canon.** So the ask is to frame it and propose wording. Do not change M3 yourself.

## The advisor's working proposal (test it; reshape it)

1. **Money splits in two.**
   - **Cost** is the total paid.
   - **Cash flow** is when, and how much at once.

   A household with no buffer, or with weekly, fortnightly or irregular income, weights the two very differently from a comfortable one. A fixed-date DD that lands before payday can bring bank charges that outweigh the DD discount. Summer credit from level DDs is an interest-free loan to the supplier: cheap for some households, expensive for others.
2. **Peace of mind** covers two related needs, measured separately.
   - **Certainty (worry).** People will pay to avoid uncertainty and shocks: the fix premium, bill shock, the fear that switching goes wrong.
   - **Control.** People want to see and decide when money leaves, avoid debt building up, and keep the supplier out of their bank account. Some prepayment and cash payers accept more cost, and more risk of running out, to have control.
3. **Time** stays as M3 defines it: household minutes by activity class (C31).
4. **Carbon** stays as it is.
5. **Comfort and health are a floor, not a currency.** Warmth above safe levels is not traded away for money. This is already ruled in the comfort and health-floors steer of 25 Oct.

Units must not be converted to £, as with time (M3, 12 Oct). Candidates to evaluate:
- **Certainty:** the spread of monthly outgoings against what the household expected, the chance of a bill well above expectation, and the number of shock events a year.
- **Control:** whether the household's payment and visibility match its preference, plus self-disconnection and rationing events as a harm signal.
- **Cash flow:** the timing mismatch between payments and income, failed payments and bank charges, and credit held by the supplier.

## Why it matters for "created, then shared" (M2)

- **Carrying risk can create value, not only move it.** A supplier that pools many customers and hedges can carry price risk more cheaply than any one household. If it sells certainty for less than the household's own cost of the worry, that is value created, and the margin on it is a fair share.
  - Today the fix premium is booked as value moved.
  - Under this framing, part of it may be value made.
  - The test is whether the supplier's hedging really lowers the cost of carrying the risk. This connects to the hedging and value-test work.
- **Payment design can create value without removing control.** Some ways to give a cash-short household the DD price without the costs that keep it off DD:
  - a DD date chosen to match payday;
  - weekly or fortnightly DD;
  - a variable DD for smart homes, so no credit is held;
  - smart PAYG with budget alerts and friendly-credit periods;
  - fast refunds of credit.

## The world must hold the truth

The supplier never sees the following hidden traits per household; it infers them from behaviour or asks:
- **Cash-flow traits:** buffer size, and the timing and regularity of income.
- **Uncertainty aversion:** higher for households on tight budgets.
- **Control preference and trust in suppliers.**

These traits drive:
- the choice of payment method and tariff (fix or variable);
- the reaction to a DD change or a shock bill;
- prepayment top-up behaviour and self-disconnection;
- switching.

**Not all prepayment is chosen.** Some is inherited with the property or fitted for debt; the 2023 forced-fitting findings are the reference. The world must distinguish chosen prepayment from imposed prepayment.

## Ask

1. **Frame it** in a DISCOVER/FRAME note, `docs/design/CUSTOMER_NEEDS_BEYOND_THREE_CURRENCIES.md`, in the style of C31. It should cover:
   - the GB evidence for each need, including how many payment-method choices are deliberate and why (Ofgem and Citizens Advice prepayment and standard-credit research, the 2023 PPM review, the FCA Financial Lives survey on buffers and income volatility, and the evidence on paying a premium to fix);
   - units;
   - household heterogeneity;
   - how a supplier creates each need and shares in it;
   - how the improvement-loop scorecard changes;
   - fairness, since the households with the highest cash-flow and control needs are often the vulnerable ones.
2. **Bring back canon wording** for M3, or a new M-rule, as one `for_the_director` row with your recommendation. Read in two minutes.
3. **Sequencing.** The framing is reading-only and can be drawn now, beside C31. The build follows the correctness exit test and sits within the improvement-loop design. Wording on the site that says pricing only moves value already says "in money terms", per today's time steer.

## Done

2026-10-30, the delivery seat.

1. **Framed.** `docs/design/CUSTOMER_NEEDS_BEYOND_THREE_CURRENCIES.md` is a DISCOVER/FRAME note,
   reading-only, in C31's style. It covers seven needs, each with its own unit and none summed:
   cost, cash flow, certainty, control, time, carbon, and a comfort and health floor.
   - **GB evidence.** In Ofgem's 2022 survey, 89% of DD, 85% of standard credit (SC) and 72% of
     prepayment (PPM) users give an active reason for their method. Control is SC payers' top reason
     and budgeting PPM payers'. Only 55% know costs vary by method. FCA Financial Lives 2024 puts 24%
     of adults at low resilience.
   - **Imposed PPM** is a separate population: 1,925 wrongful installs in Ofgem's review, against
     Citizens Advice's 600,000, on different definitions and not reconciled.
   - **The fix premium.** A three-leg test separates value made from value moved (section 6.1). The
     premium stays booked as moved until the test is run.
   - The note also covers the scorecard and fairness.
   - **Ten GAPs** are named with no number guessed. The largest are GB willingness to pay for price
     certainty and the share of households on irregular income.
   - Drafted by a research agent that read published sources and the repo's knowledge pages, not the
     code.
2. **Canon wording.** One `for_the_director` row,
   `m3-names-three-currencies-money-time-carbon`, recommends amending M3 rather than adding a rule,
   with the wording verbatim. Canon is not edited.
3. **Sequencing as steered.** No build is drawn. It follows the correctness exit test, inside the
   improvement-loop design.
