**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Eight ideas from the director's simulator spec: one for this week's need-weights page, seven for the backlog

**Type:** STEER, through the advisor channel. Finish what you're doing first, then take this next.

**The director's words,** chat, Mon 16 Nov. He shared a condensed spec of ideas for a world and supplier simulator, written for other work, and asked "Anything new and worth adding to our thesis and road map?" The advisor checked it against origin and proposed eight. He replied "Yes and yes": send them as one batch, item 1 into this week's need-weights page, the rest into the backlog for Friday's balance review.

**Provenance and IP.** These are general actuarial and behavioural ideas. The source is the director's own notes for separate employment work, and this repo is public. Do not quote that source, name its employer or its products, or add anything client-specific. Cite published literature instead. Out of scope here and **not** to be raised: SME and C&I customers, brokers, team incentive design, cross-client data pooling, and other markets (knowledge only, per his earlier ruling).

**How to read this.** Each item is a problem with the director's concern. The machine owns the design, the ordering inside the lanes, and whether an item is already covered better than this note thinks. The advisor's coverage check was one keyword pass, not a full read. Where an item is already built, say so in the Done section and close it. Knowledge comes first, with GAPs labelled, and nothing is added as a fixed percentage.

## 1. This week: hygiene needs and motivator needs do not trade off (into the household need-weights knowledge page, due 23 Nov)

The hidden weighted utility ruled on 13 Nov is, read plainly, a weighted sum. A weighted sum is compensatory: enough carbon pride or delight can cancel worry or a money shortfall. The director's view is that it cannot. Base-layer needs (worry or certainty, money, time) behave as hygiene factors. A deficit drives leaving, complaints and debt, and a surplus does little. Upper-layer needs (carbon, feeling good) are motivators. A surplus drives engagement, referral and product take-up, but has little effect while the base layer is in deficit. Comfort and health are already a floor. This extends that idea to the base layer as an asymmetry, not a hard floor.

- Before the page settles the utility's form, research the evidence: Herzberg's two-factor theory, Kano-style asymmetric satisfaction, loss aversion, and lexicographic or non-compensatory choice models. Record what supports a non-compensatory shape for household energy and what does not.
- Let the page decide the utility's functional form, not only its weights. Name the cost if it changes the planned run sequence.

## 2. Each need as a stock that decays at its own rate (world lane)

Each household's standing on each need should be a stock: a balance, its momentum, and its volatility. Events add to it or debit it, and each kind of event decays at its own rate. Bill shock lingers for months, and a slow web page fades in days. Background friction acts as a multiplier on the effect of a new shock (hypothesis: friction multiplies shocks). This is the mechanism for the director's own hypothesis that brand and reputation are a durable stock (30 Oct). It must build on the existing activation-energy and resentment mechanics, not start a parallel module. Decay rates are mostly not published, so carry them as stated beliefs with ranges.

## 3. Churn that needs a trigger (world lane)

The concern: the price gap may only matter once something triggers a household to shop. The staged form is P(trigger) × P(shop | trigger) × P(switch | gap). Triggers include renewal or fix expiry, bill shock, a bad service event, a home move, or a press or comparison-site campaign, and campaigns cluster in contagion. The 2021–22 lesson goes with it: bill pain with no gap to escape to shows up as debt and complaints, and bill pain with a gap shows up as switching. Test this as an alternative mechanism against the current stack of multipliers. The test is the world validation ladder, especially whether it carries the record's year-to-year switching movement, which the current level does not reach honestly. Do not fit it to the band. Test step, linear and arctan shapes for the gap response, with a threshold.

## 4. Credibility blending for per-customer inference (supplier lane)

The thesis's sore point: there is still no graded evidence that per-customer inference beats the flat-rules baseline, and price sensitivity was measured as structurally unlearnable on the current book. The actuarial answer is to blend. Each estimate = Z × the individual's own evidence + (1 − Z) × its lookalike group, with Z = n / (n + k), applied hierarchically (household → postcode area → region → whole book). The concern is that "per-customer beats flat" is the wrong first test, and "a credibility blend beats flat" is the fair one. Every group must be built only from what a real supplier could observe (the wall).

## 5. Adverse selection (world and supplier)

There is no trace of this in the repo. Good payers leave first, because they have options. Selling at the cheapest position on the market attracts the most price-sensitive and riskiest households. Hypothesis: cheapest-position acquisitions have negative lifetime value. This sits on the merit order of pays, then stays. The world must produce it from drawn traits, not as a rule, and the supplier must be able to discover it.

## 6. Cost to serve that rises in steps (supplier lane, with the epoch-2 cost-to-serve item)

There is no trace of this either. Staff cost comes in steps, not per contact. Below the next step the marginal cost is near zero (summer troughs). At the winter peak it is high. Automation only saves money when it avoids a step or frees capacity for valuable work. Hypothesis: savings cases built on handle time × hourly rate overstate. This matters to the mission, because the enterprise value is the automated method, and this is how to price it honestly. It is related to the quiet-period hypothesis: outbound conversations in troughs may lower churn and debt rather than wake sleeping dogs.

## 7. Three CLV additions and one book-level check (supplier lane)

- The customer's free option to leave a fix when the market falls.
- Hedge sell-back gain or loss in the cost of a churn. It moves with the market, so a churn can be a gain.
- The option value of a household's future EV, heat pump, solar or flexibility take-up.
- A book-level check: total contribution must cover fixed costs plus a target return. Hypothesis: retention judged on fully costed CLV under-invests, and pricing on contribution alone fails to cover fixed costs (the death spiral).

These are consistent with the canon that per-customer CLV is on a contribution basis with no fixed overhead. The fixed-cost check sits at book level only.

## 8. Hard guardrails before any optimiser or tournament can evolve the supplier

Encode these as constraints the optimiser cannot trade:

- Never use a life-event forecast (death, separation, pregnancy) to target, price or reduce service.
- Fix overcharges as readily as undercharges.
- Never nudge a household out in order to cash in a hedge.
- Never steer a vulnerable household out.
- Pass the equivalent-new-customer (loyalty penalty) test.
- Contact caps, a kill switch per action type, and holdouts always on.

Reason: the profit maximiser found cap-pricing on its own. A tournament that selects for fitness will find these exploits too. Each guardrail must be provably failable: a test that shows it refusing.

## Pre-registration

The spec carries testable hypotheses. Those in scope here, to pre-register where the work reaches them:

- the price gap only matters once a trigger fires;
- acting inside the trigger window beats better targeting;
- retention deadweight is large;
- absence of engagement leads churn and debt;
- collectability of a held bill falls sharply with its age and size;
- a meaningful share of account ends are life events, and survival CLV with competing risks values the book better;
- quiet-period conversations lower churn and debt rather than waking sleeping dogs;
- the fully costed versus contribution pair (item 7);
- cheapest-position acquisitions have negative lifetime value;
- lower-layer deficits dominate churn and upper-layer surplus drives engagement;
- friction multiplies shocks;
- personal weights and choice fit predict better than price-only models.

## Risk

- **Touches:** knowledge pages and backlog entries now. Later, world response functions (items 2, 3, 5), the supplier's estimator (item 4), CLV (item 7) and the optimiser's constraints (item 8).
- **Blast radius:** this week, item 1 only, which can change the form of the hidden utility before it is built. That is cheap now and expensive later. Everything else is ranked, not built.
- **Probable failure mode:** a new mechanism (item 3 especially) is tuned until it hits a published band. That is the clamping the validation ladder forbids. Or a decay or trigger rate is invented to fill a GAP.
- **Mitigation, inline:** each world item clears the ladder's four rungs, with published figures used as tests and never as targets. Unpublished rates are stated beliefs with ranges. Item 8's guardrails ship with tests that show them refusing.

**Proportionality:** item 1 is reversible and narrow, a knowledge page, so just do it. Items 2 to 8 are ranked in Friday's balance review under the correctness stretch and its feature share. None of them is for this week.

## Seat note, 16 Nov

Not drawn. At draw time the seat executor refused it for missing attribution. The chat words carry
a day ("Mon 16 Nov") but no time, and nothing else gives the file authority. It was not moved to
done/, because the open-question gate holds the director's quoted question open, and archiving an
unactioned steer would close it silently. **To make it drawable,** re-stage it with the time of his
words, as the sibling EP11 ruling does ("09:27 GMT"). Nothing in it was judged on its merits. Item 1
is due 23 Nov.
