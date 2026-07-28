# Scope brief — GB wholesale price formation (written BEFORE assembly)

**Deliverable #1** of `DIRECTOR_RULING_KPILOT_SCOPE_FIRST_2026-07-28.md`. This brief states what a
*complete* reader-facing treatment of GB wholesale electricity price formation must contain — the
sections, the questions each answers, and the phenomena that MUST appear. It is written **before and
independently of** the current page. Assembly fills this brief; it does not define it (ruling §1–2).

The brief-versus-assembly DELTA (deliverable #5) is measured against THIS document, not against what
we already hold. Where the assembly cannot fill a required item, that item becomes a **named gap on
the page** (ruling §3) and a backlog mint-source (`DIRECTOR_RULING_PUBLISHED_GAPS_ARE_THE_BACKLOG`).

---

## Method & provenance (blind-ish, per ruling §1.4)

- **Anchor:** `BOARD_SPEC_004_PRICE_FORMATION` (docs/staging/done/…_2026-07-22.md) — a blind
  practitioner statement of what matters about GB price formation, with a 12-item disqualification
  battery. Spec 004 was drafted by an instrument (the board) that **cannot see the built page or the
  price engine** (§13 of the spec: "The Board has not examined any price engine as built"). Extending
  it into a reader-facing brief inherits that blindness — this is the board-spec pattern the ruling
  endorses as a worked precedent.
- **Second blind input:** the director's own named-gap list (ruling §3), given as a reader who found
  the page failed on scope. Explicitly "not exhaustive — the scope brief governs" (§3), so this brief
  is allowed to require *more* than §3, never less.
- **Blindness discipline (exit criterion):** this brief is NOT reverse-engineered from
  `site/knowledge/wholesale-price-formation/index.html`. The required-scope list below is derived from
  Spec 004 + §3 + domain fundamentals. What the page currently contains is scored SEPARATELY in
  deliverable #2 (the reconciliation) and subtracted in #5 (the delta) — it does not appear here.
- **Why blind-ish and not fully blind:** a fully blind brief (a fresh board sitting with no prior
  artefacts) is available and stronger, but Spec 004 already *is* a blind sitting on exactly this
  topic with a disqualification battery. Reusing it is cheaper and loses little; a fresh blind pass is
  registered as an optional deepening (a candidate atom), not a blocker for #3/#5.

---

## Reader model — what "complete" is measured against

**Target reader:** someone who knows nothing about how GB electricity is priced but needs to
understand it — a new joiner, a curious customer, a non-specialist board member. The acceptance test
(ruling): *"a reader who knows nothing can learn from the page what the scope brief says they should
learn — and where they cannot, the gap is named on the page."*

**After reading, the reader must be able to answer, in their own words:**

1. Why is the electricity price the running cost of the *most expensive* plant needed, not the average
   cost of all generation? (marginal pricing)
2. What is actually *bought and sold* — what is "the wholesale price" a price *of*? (traded-product
   structure: baseload/peak, seasons/quarters/months, day-ahead/within-day)
3. Why does the price follow the **gas** price even on a windy day with lots of cheap renewables?
4. Why does building more renewables not straightforwardly make the price low all the time?
5. When and why does the price go **negative**, and how often does that really happen?
6. When and why does the price **spike** into the hundreds or thousands of £/MWh?
7. Why is the price different in **winter** than in **summer**, and different **year to year**?
8. Why did prices rise five- to tenfold in **2021–22** and stay there — and could a model have called
   it impossible?
9. What is a **forward** price, and why is it *not* a forecast of what spot will turn out to be?
10. How is the **structure itself changing** as the grid decarbonises?

A treatment that leaves any of these unanswerable — or answers it wrongly — is incomplete on scope.

---

## Required sections

Each required section states: **must contain**, **questions answered**, **phenomena that MUST
appear**, and the **disqualifier** (the Spec 004 battery item it defends against). Sections are the
scope unit; the decomposition (deliverable #3) decides which become the hub, children, or stubs.

### S1 — The marginal-price principle
- **Must contain:** the price everyone is paid in a settlement period is the short-run cost of the
  *marginal* (last, most-expensive) unit dispatched, not the average generation cost.
- **Answers:** Q1, Q4.
- **Phenomena that MUST appear:** cheapest-first dispatch; zero-marginal-cost generation (wind, solar,
  nuclear, must-run) filling first; the marginal plant setting the clearing price for all.
- **Disqualifier defended:** battery #1 (power unanchored from marginal-unit arithmetic).

### S2 — The structure of wholesale prices (the traded product set) — *director: "possibly the most important thing we use"*
- **Must contain:** what is actually traded — **baseload vs peak** blocks; **seasons, quarters,
  months** as forward delivery periods; **day-ahead** and **within-day** markets; and **why shape
  matters** (a flat "average price" hides that peak hours and winter cost far more). This is the scope
  gap the director named first and the page did not mention at all.
- **Answers:** Q2.
- **Phenomena that MUST appear:** the ladder of delivery granularity (annual → seasonal → quarterly →
  monthly → day-ahead → within-day/imbalance); baseload vs peak price differential; why a supplier
  buys *shaped* volume, not a single number.
- **Disqualifier defended:** a treatment that presents "the wholesale price" as one scalar with no
  product structure has not explained what is priced. (New required item beyond the battery; sourced
  from §3 and Spec 001's desk framing.)

### S3 — The merit order and residual demand (the SRMC stack)
- **Must contain:** each plant offers near its short-run marginal cost (SRMC); the stack is built
  cheapest-first; **residual demand** (demand minus renewable output) determines how far up the stack
  the marginal unit sits.
- **Answers:** Q1, Q3, Q4.
- **Phenomena that MUST appear:** SRMC = fuel/efficiency + carbon + variable O&M; the spark spread;
  residual demand as the swing variable; high wind pushing the marginal unit *down* the stack.
- **Disqualifier defended:** battery #1, #4 (wind uncorrelated with price).

### S4 — Gas as the global anchor
- **Must contain:** gas plant (CCGT) sets the GB power price in the large majority of hours, so
  **power price ≈ gas price × heat rate + carbon**; and the gas price itself is set at the margin of a
  **global** market — **NBP/TTF**, **LNG** as the marginal cargo since 2021–22 pricing GB against Asian
  demand, pipeline supply, storage stocks, and interconnector flows.
- **Answers:** Q3, Q8 (partly).
- **Phenomena that MUST appear:** gas-set hours as the majority; the global LNG channel; storage as
  the buffer that creates the winter–summer spread; why GB is exposed to a global gas market it cannot
  control.
- **Disqualifier defended:** battery #1, #6 (storage absent from gas formation).

### S5 — Carbon pricing
- **Must contain:** the carbon cost added to every tonne burned — **UK Carbon Price Support** (a fixed
  top-up) *plus* the **traded ETS price** (EU ETS to 2020, UK ETS after) — and how carbon moves the
  spark/dark spreads and therefore the **ordering** of the stack (gas vs coal).
- **Answers:** Q3 (secondary driver).
- **Phenomena that MUST appear:** carbon as a genuine input to marginal cost, not a footnote; carbon's
  effect on gas-vs-coal merit ordering.
- **Disqualifier defended:** battery #1 (carbon channel present in the arithmetic).

### S6 — Weather → demand AND generation (the joint driver)
- **Must contain:** the *same* weather draw moves demand up, wind output down, power-sector gas burn
  up, and gas and power prices up **together** — weather is not just a demand story.
- **Answers:** Q3, Q7.
- **Phenomena that MUST appear:** cold-still days as the compounding case; wind's route into
  generation as well as demand's route through heating/cooling; the correlation, not two independent
  effects.
- **Disqualifier defended:** battery #8 (the severed joint driver — the shared disqualifier of Specs
  001/002/004).

### S7 — Interconnectors and imports
- **Must contain:** interconnectors couple GB to continental prices when uncongested; imports/exports
  flex with the price differential; foreign-fleet events reach GB through this channel.
- **Answers:** Q6 (partly), Q8 (the French channel).
- **Phenomena that MUST appear:** the 2022 French nuclear availability crisis becoming a GB price
  event "without a single GB plant failing"; interconnectors as marginal-price setters at the ends of
  the stack.
- **Disqualifier defended:** battery #11 (interconnector/foreign-fleet shocks inexpressible).

### S8 — CfDs and renewable support
- **Must contain:** Contracts for Difference and legacy renewable support, and — crucially — the
  **two distinct effects**: what they do to the **merit order** (subsidised/must-run output bidding
  low or negative) versus what they do to **what consumers actually pay** (the CfD top-up/clawback and
  policy levies land on the bill, so cheap-to-dispatch is not the same as cheap-to-the-customer).
- **Answers:** Q4.
- **Phenomena that MUST appear:** CfD-backed generation as a price-taker in the stack; the split
  between dispatch cost and consumer cost; why "we have lots of cheap renewables" does not translate
  into a low wholesale price at the margin.
- **Disqualifier defended:** the "cheap renewables ⇒ cheap price" fallacy; §3 named gap.

### S9 — Negative prices
- **Must contain:** when (high renewables, low demand, must-run output exceeding demand), why
  (must-run/subsidised generators would rather pay to keep running than shut down), and **how often**
  (a low-single-digit percentage of settlement periods in recent years — a real, quantified figure,
  not "sometimes").
- **Answers:** Q5.
- **Phenomena that MUST appear:** the frequency stated numerically; the growth trend as renewables
  rise; the mechanism (avoided shutdown/restart cost, subsidy retention).
- **Disqualifier defended:** battery #3 (negative prices at token frequency, or absent).

### S10 — Scarcity pricing and the hockey stick
- **Must contain:** the other end of the stack — low wind + high demand climbs through peakers,
  interconnector imports and demand response into scarcity pricing; a **convex** price–load–wind
  surface where the last gigawatts cost multiples; the regulatory **cash-out ceiling** (£6,000/MWh) as
  a hard wall.
- **Answers:** Q6.
- **Phenomena that MUST appear:** the hockey-stick convexity; spike magnitude/frequency/duration
  inside the observed settlement record; the cash-out ceiling as an approached-but-not-exceeded wall.
- **Disqualifier defended:** battery #2 (no hockey stick), #7 (Gaussian returns — jumps/fat tails),
  #10 (flat volatility).

### S11 — Seasonality across the year
- **Must contain:** why winter prices exceed summer (higher demand, lower solar, tighter gas storage),
  the **winter–summer spread** and its link to gas storage injection/withdrawal, and how seasonality
  shows up in the forward curve.
- **Answers:** Q7.
- **Phenomena that MUST appear:** the annual shape; storage's intertemporal logic (injection season
  priced against withdrawal season); seasonal volatility differences.
- **Disqualifier defended:** battery #6, #10.

### S12 — Regimes and 2021–22 (reversion to a level that jumps)
- **Must contain:** spot mean-reverts with fast half-lives (spikes collapse in days, weather anomalies
  in weeks) — **but the mean itself is a regime variable that jumps discontinuously**. 2021–22 as the
  permanent exhibit: level moved 5–10×, held for over a year; a process calibrated to placid
  2015–2019 called it a many-sigma impossibility continuously.
- **Answers:** Q8.
- **Phenomena that MUST appear:** mean reversion *within* a regime; the regime layer where level,
  volatility and correlations move jointly; government intervention (caps/subsidies) entering the
  price mechanism itself; the "containable-after-onset, not perpetually many-sigma" standard.
- **Disqualifier defended:** battery #5 (reversion to a fixed mean), #12 (a static regime).

### S13 — Forwards, risk premia and sentiment
- **Must contain:** a **forward price is not a forecast** — it is a traded, risk-adjusted expectation;
  realised spot routinely lands far from it in both directions. Risk premia widen after crises and
  compress after long calm; sentiment moves *physical* decisions (the 2021 storage panic as fear
  expressed as injection demand) so belief becomes flow becomes fundamental — converging onto
  fundamentals-dominated spot at delivery.
- **Answers:** Q9.
- **Phenomena that MUST appear:** the forward-is-not-a-forecast creed; term structure of risk premium;
  premium dynamics around stress; the short-end discipline (spot settles on physics).
- **Disqualifier defended:** battery #9 (forwards that forecast).

### S14 — The structural transition
- **Must contain:** the machinery is being rewritten — more zero-marginal generation ⇒ fewer gas-set
  hours, more zero/negative periods, **and** sharper scarcity when the wind stops; the distribution is
  becoming **bimodal**, both tails growing at the expense of the middle.
- **Answers:** Q10.
- **Phenomena that MUST appear:** the shrinking middle; growing zeros and growing spikes together; why
  a model calibrated to yesterday's unimodal world ages in real time.
- **Disqualifier defended:** battery #12 (a static regime blind to the transition).

---

## S15 — Live evidence (rung 5, MANDATORY — ruling §5)

Not a content section but a hard definition-of-done: an explanation of price formation **without
charts is not an explanation** (the director is a visual reader). The complete treatment MUST render,
from the live pipeline (never static images), at minimum:

- **a real GB price series** (Elexon system-price / day-ahead history);
- **a merit-order stack** (the cheapest-first dispatch curve);
- **a seasonal shape** (the within-year price profile);
- **a negative-price frequency** (how often, over time).

Deliverable #4 builds these plus a DoD gate that **fails a chartless page**. Listed here so the
scope brief itself records charts as in-scope, not optional decoration.

---

## Director §3 named-gap → required-section map (completeness check)

Every gap the director named in ruling §3 maps to a required section above; none is orphaned:

| Director §3 named gap | Required section |
|---|---|
| Structure of wholesale prices (baseload/peak, seasons, quarters, months, day-ahead, within-day; shape) | **S2** |
| Gas as the global anchor (NBP/TTF, LNG, gas sets power for most hours) | **S4** |
| Weather → demand AND generation | **S6** |
| Interconnectors and imports | **S7** |
| CfDs and renewable support (effect on merit order AND on consumer cost) | **S8** |
| Negative prices (when, why, how often) | **S9** |
| Seasonality across the year | **S11** |

Spec 004's battery items not in §3 but still required: mean-reversion/regime (S12), forwards/risk
premia (S13), the structural transition (S14), scarcity/hockey-stick (S10), carbon (S5). The brief
requires more than §3, never less, per the ruling's "the scope brief governs."

---

## Acceptance (restated from the ruling)

A reader who knows nothing can learn from the page what this brief says they should learn (S1–S14
answered, S15 shown), **and every place they cannot is a named gap on the page** — the gap, not the
silence, is the deliverable. The delta between this brief and the assembly (deliverable #5) is the
pilot's primary finding.

---

*Provenance: deliverable #1, blind-ish, anchored on Board Spec 004 + ruling §3. Doc-only, no
maturity-map level claimed. Blocks deliverable #3 (decomposition) and #5 (delta). 2026-07-28.*
