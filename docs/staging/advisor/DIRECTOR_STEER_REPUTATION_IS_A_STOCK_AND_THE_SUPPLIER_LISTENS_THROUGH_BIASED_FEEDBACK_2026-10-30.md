**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Reputation is a stock and a durable price and value elasticity, and the supplier listens through biased feedback, Trustpilot included (2026-10-30)

**Type:** STEER, through the advisor channel. These are the director's words from chat on Fri 30 Oct:

- 16:53 GMT: "my own hoyothesis on brand and reputation is that it is a form of long term and durable price and value elasticity. So if you repeated overcharge customers may not move instantly but you lose stock of brand equity attributes. ? Do we have knowledge on the range and importance of energy supplier brand equity and and attributes?"
- 16:59 GMT: "Yes do some research. And we want to allow the supplier to ask for feedback and get it from engaged (or enraged!). Or maybe simualte trust pilot? This allows a feedback loop that is what real suppliers try to do"

## What already exists (advisor's read of origin)

- **`simulation/resentment_ledger.py`.** Each customer carries a resentment stock that decays over time. Past a personal threshold the customer churns irreversibly. The event weights (+15 for a billing error, +18 for bill shock, and so on) come from early CTO guidance, not from evidence.
- **`simulation/reputation_index.py`.** A world-side Global Reputation Index scales activation energy across the whole book. As far as the advisor can see, it affects churn only.
- **`simulation/feedback_survey.py`.** Solicited CSAT/NPS with a U-shaped response propensity, suppressed under income stress, and noisy answers. The company sees only the responses. The parameters are placeholders: base rate 0.08, extreme bonus 0.12.
- **`docs/market_research/communications_sentiment_and_nps.md`.** Knowledge on sentiment, NPS, and the link from complaints to departure.

The architecture is right: hidden truth sits on the world's side, and the supplier holds its own measurements. **What is missing is evidence, a public review channel, and reputation effects beyond churn.**

## What the evidence says (pack beside this file)

1. **The hypothesis holds in shape. Brand acts as a stock, and the overcharging penalty arrives late and durably.**
   - British Gas lost about 1.38m accounts in 2017 and 742k in 2018, after SVT rises, while its brand NPS stayed flat. NPS did not warn of the churn.
   - npower's billing failure ran about 7–9 years from shock to brand exit.
   - ScottishPower has stayed bottom of the rankings about 10 years after its 2013–15 failures.
2. **It does not hold everywhere.** After the 2023 forced-prepayment scandal, British Gas's whole-base satisfaction *rose*. Damage concentrated on a vulnerable minority does not necessarily reach the whole book. It hits prospects, regulators and the affected households.
3. **Inertia, not trust, keeps overcharged customers.** Only 38% trust their supplier to charge a fair price, yet "current supplier satisfactory" is the leading reason for staying. Resentment builds silently and crystallises at **triggers**: a price-rise letter, a fix ending, a bill shock, press coverage.
4. **Reputation drives acquisition about as much as price does.** Of customers who actively chose a supplier, 33% chose on reputation and 45% on price (Which? 2025).
5. **Feedback is a heavily mediated signal.**
   - Reviews are J-shaped, driven by people who had an extreme experience.
   - Octopus's Trustpilot spread (90% 5-star, 3% 1-star) matches its Ofgem survey dissatisfaction closely.
   - British Gas's spread (66% 5-star, 20% 1-star) shows about 4× its survey dissatisfaction.
   - A supplier's **invitation policy** largely decides how far its reviews track the truth.
   - NPS predicts churn no better than CSAT, and can stay flat while churn spikes.
6. **Two kinds of trust.** Trust to treat customers fairly and trust to charge a fair price differ by 7 points (45% against 38%). Separately, trust in your *own* supplier runs 10–25 points above trust in the *sector*.

## Asks (you own the design; these are prompts)

1. **Calibrate from data.** Replace the placeholder resentment weights, decay rates, the GRI dynamics and the feedback response parameters with evidence-graded values. Use the pack's parameter table (E1) as a starting point, and apply the 16:51 data standard: verify, re-derive, grade D/P/S/A, and give a range wherever a value is A. Keep the parsimony ruling: model only the strong links.
2. **Split the stocks.**
   - Fast advertising goodwill.
   - Slow portfolio reputation, which decays asymmetrically: damage decays more slowly than gains.
   - Category or sector trust, hit by sector events such as the 2021 failures and the 2022 crisis.
   - The per-customer ledger.

   Add **salience triggers** to the churn hazard, so resentment crystallises at triggering events rather than leaking out as smooth churn.
3. **Extend reputation's effects beyond churn.**
   - Acquisition conversion and cost per acquisition.
   - Referrals: high-reputation suppliers grow through them.
   - Price tolerance, split into brand equity and fragile inertia.
   - Uptake of advice and products, moderated by trust (this links to the customer-needs trust moderator).
4. **Add the public review channel the director asked for, a Trustpilot-like platform.**
   - Organic reviews come mainly from strongly negative experiences and are spiked by events.
   - Invited reviews appear where the supplier chooses to invite.
   - The public score feeds prospects' choices.
   - **Invitation policy is a supplier decision.** Selective invitation should be tempting, and visible to a regulator or the platform.
   - Add a regulator channel: an unbiased random panel, plus a Citizens Advice-style star rating, as the closest thing to shared ground truth.
5. **Let the supplier run the real feedback loop.** Ask, listen, reply, fix root causes, and track whether its scores, complaints and churn improve. Grade it against the hidden truth: does the supplier's reading of its own reputation match the world's, and does acting on feedback create value? This is the coupled-triad gap the reputation module was designed to score.
6. **Test the director's hypothesis directly.** Pre-register a supplier strategy of repeated small overcharges against a fair-pricing strategy. Measure the short-run margin gain against the delayed, durable losses through churn, acquisition, cost per acquisition and price tolerance, across the world's uncertainty ranges.

**Sequencing.** The calibration and knowledge pages are drafting work and can run now. The world build follows the correctness exit test and sits inside the improvement-loop design and the next-SIM-additions roadmap, where this candidate should be ranked against the others.

## Addendum, 17:20 GMT: what is competitive waits for the competition topic

The director's words, 17:20 GMT: "This starts to get into competitive simulation which is a next not now topic. So some of this should wait for that perhaps?"

**Split the asks along that line.**

- **Now** (behind the correctness exit test, as above). These involve only our supplier and its own customers:
  - calibrating the per-customer resentment ledger;
  - separating our own reputation stock from its decay;
  - salience triggers on churn from our own book;
  - the solicited-feedback engine;
  - organic and invited reviews *about us*;
  - the regulator's random panel and star rating for us;
  - the supplier's own feedback loop: ask, listen, reply, fix root causes, and the coupled-triad gap;
  - trust moderating uptake of our advice.
- **Next, with the competitive simulation, and not before:**
  - reputation moving prospects' choice *between* suppliers;
  - cost of acquisition relative to rivals;
  - referrals as a share-gaining channel;
  - price tolerance measured *relative to the market*;
  - sector or category trust shocks across suppliers;
  - the overcharge-vs-fair-pricing test of the director's hypothesis, because its losses run through switching to rivals and acquisition against them.

  Record these as named items under the competition topic, with this evidence pack as their knowledge base. Do not build them now.

Where today's world already produces switching-away without modelled rivals, keep it as it is. Do not extend it into a competitor field under this steer.

