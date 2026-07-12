# CHARTER — W2 Affordability Cluster: L3/L4 Concretisation

**Purpose of this document.** `docs/staging/done/AFFORDABILITY_AS_SIM_PHYSICS.md` registered the
W2 affordability atom cluster (household budget sketch, life-event stream, SME/I&C distress twin,
wall discipline, regulated debt path, plus the director's attitudinal/self-rationing/T&C/DD-confound
addendum) and it is now live in `docs/design/maturity_map.yaml` as atoms `W2_4_household_budget`
through `W2_10_dd_attribution_confound` — registered, `level_current: 0`, not yet built, riding M3
with the population draw (`W2_2_population_draw`). This charter does the FRAME-stage work the map's
own rule calls for (`MATURITY_MAP.md` §4: "the charter is FRAME's output... what L2/L3/L4 mean in
this lane's terms, the named best-practice references") **specifically for this cluster**, taking
each atom from the registration's necessarily-compressed spec language to concrete, buildable,
citation-backed acceptance criteria — matching the depth already established by
`docs/design/charters/W2_customer_generator.md` for `W2_1`-`W2_3`. It does not replace that file;
it is the deepening pass for the seven newer atoms that file does not yet cover. **Nothing in this
document is a build authorization** — the cluster stays `loop_stage: idle` pending M3, per the
director's own decision; this is DISCOVER+FRAME only. **Read-only w.r.t.** `maturity_map.yaml`,
`company/compliance/`, and `docs/observability/sanity_adjudication_ledger.json` — those are being
actively written by a concurrent registration pass; nothing here edits them.

**Confidence tagging (this project's own convention):** every anchor below is either a **directly
verified real figure/source** (cited with a fetchable title/URL) or tagged **[L]** where I am
asserting a general-knowledge pattern, a directional magnitude, or an inference not pinned to a
specific verified figure this session. No precise number is fabricated; where I don't have a
verified figure I say so and tag it, per `AFFORDABILITY_AS_SIM_PHYSICS.md`'s own instruction ("tag
[L] and verify before encoding").

---

## Cross-cutting real-world twin: UK household/business debt in 2025-26

Before the per-atom detail, the shared backdrop all seven atoms sit inside, so "realistic" has a
concrete anchor: **Ofgem's own Debt and arrears indicators** (`ofgem.gov.uk/data/debt-and-arrears-indicators`)
report domestic customer debt and arrears reaching **~£4.48bn in Q3 2025**, the twelfth consecutive
quarterly rise, with average arrears of **£1,716 (electricity) / £1,489 (gas)** in Q2 2025 (up
~11-12% YoY), and **~1.1m electricity / ~927k gas domestic accounts (~3.8% of each fuel's customer
base)** more than 91 days in arrears with **no repayment plan** as of Q2 2025. Nearly three-quarters
of the total debt sits with customers with no plan at all — this is the real population this
cluster's mechanism must be capable of producing, not a benchmark to tune toward (R12 applies
throughout this document, restated per atom below where it matters most).

---

## W2_4_household_budget — household budget sketch as hidden SIM state

### (a) Real-world twin, concrete enough to build against

- **Income band.** Two real, named, fetchable UK datasets, not a generic "income distribution":
  - HMRC's **"Percentile points from 1 to 99 for total income before and after tax"** (Table 3.1a,
    part of the Statistics on Personal Incomes series, derived from the Survey of Personal
    Incomes), `gov.uk/government/statistics/percentile-points-from-1-to-99-for-total-income-before-and-after-tax`
    — gives an actual percentile ladder (1st-99th) for individual income, before and after tax,
    updated annually; this is the natural draw distribution for an individual/household income band.
  - ONS's **Effects of Taxes and Benefits on Household Income (ETB)** release
    (`ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth`),
    derived from the Living Costs and Food Survey (~5,000 households/year), publishing income by
    quintile/decile group including regional breakdowns — the better-suited dataset if the draw is
    keyed to *household* (not individual) equivalised income, which is the unit the budget sketch
    actually needs. **[L]** exact reconciliation between the two datasets' unit-of-measure
    (individual taxpayer vs. equivalised household) is not something I verified this session — flag
    for whoever builds this to resolve before wiring either dataset in, rather than blending them
    naively.
- **Essential-cost floor.** The right-shaped real anchor is the **Joseph Rowntree Foundation /
  Loughborough University Centre for Research in Social Policy (CRSP) Minimum Income Standard
  (MIS)** — an annually-updated, publicly negotiated basket of what the UK public agrees is needed
  "to live with dignity," published every year since 2008
  (`lboro.ac.uk/research/crsp/minimum-income-standard/`; the 2025 edition,
  `jrf.org.uk/a-minimum-income-standard-for-the-united-kingdom-in-2025`, reports **a single person
  needs ~£30,500/year and a couple with two children ~£74,000/year** to reach MIS). This is a far
  better real twin than an invented "essential cost floor" constant: it is household-composition-
  aware (single/couple/children), inflation-tracked annually, and is the actual instrument UK
  poverty researchers and JRF itself use for "living below a minimum standard" analysis
  (`jrf.org.uk/households-living-below-a-minimum-income-standard-2008-2024`).
- **Savings buffer.** The **FCA Financial Lives survey** (`fca.org.uk/publication/financial-lives/`)
  is the real, regulator-run, nationally-representative UK source for this: the 2024/2025 wave
  reports **~1 in 10 UK adults have no cash savings at all**, another **~21% have less than £1,000**
  to draw on in an emergency, and (2022 wave) **~41% of all UK adults could not cover 3 months of
  living expenses** from savings if they lost their main income, rising to **~78% among those with
  low financial resilience**. This gives a real, citable shape for the savings-buffer draw: a
  long right-skewed distribution with a large mass at or near zero, not a smooth/normal one — a
  concrete, testable shape claim (see L3 below).
- **Priority-of-debts ordering.** Anchored to **StepChange's** own published guidance,
  *"Priority Debts & Which Bills To Pay First"*
  (`stepchange.org/debt-info/dealing-with-debt-problems/what-debts-to-pay-first.aspx`) and the
  equivalent **MoneyHelper** guidance *"How to prioritise your debts"*
  (`moneyhelper.org.uk/en/everyday-money/credit/how-to-prioritise-your-debts`), both of which
  converge on the same UK debt-advice-sector taxonomy: **priority debts** = rent/mortgage arrears,
  council tax arrears, magistrates' court fines, child maintenance arrears, gas/electricity
  arrears, TV licence arrears, and (for the self-employed) income tax/VAT/NI arrears — because
  non-payment carries the most severe *consequence* (eviction, repossession, loss of essential
  supply, imprisonment for fines); **non-priority debts** = credit cards, personal loans,
  overdrafts, catalogue/store cards, buy-now-pay-later, unsecured family loans. **Important
  nuance the atom's own registration text (a flat ordered list: "rent/mortgage, council tax, food
  before energy") slightly oversimplifies**: the real debt-advice framework is not a strict total
  order but a **consequence-severity ranking** — StepChange and MoneyHelper both frame it as "what
  happens if you don't pay this one," not a fixed priority-1/2/3 list. Energy sits inside the
  priority tier alongside rent/council tax/court fines, not strictly beneath all of them — the
  ordering between *those* is itself somewhat household-specific (e.g. a renter facing imminent
  eviction may rationally deprioritise a supplier that is regulatorily constrained from
  disconnecting them, per the PPM-as-last-resort protections already in the regulatory oracle). This
  is the single most useful concrete correction this pass makes to the atom's build spec (see
  closing summary).

### (b) L3 concrete meaning

L3 ("fails like reality") for this atom is **not** "a plausible-looking number comes out" — it is:

1. A household drawn into the **bottom decile of the HMRC/ETB income distribution** with a MIS-
   anchored essential-cost floor for its actual composition (single/couple/children) produces
   **near-zero or negative discretionary margin** in at least one modelled month per year *without*
   any explicit rule saying "poor households miss payments" — the shortfall must be the arithmetic
   consequence of income minus the floor, not a separately-coded probability.
2. When a price shock (crisis-era unit-rate rise) is applied, households whose discretionary margin
   was already thin **cross into negative margin at a materially higher rate than households in the
   top income decile** — a testable, measurable population-level claim (a stratified before/after
   comparison across income bands), not just "some households miss payments."
3. The savings-buffer distribution, when sampled, reproduces the **FCA-anchored shape**: a
   measurable fraction of the drawn population (order-of-magnitude consistent with ~10% zero /
   ~30% under ~£1,000, **[L]** on exact calibration against a *simulated* population vs. the FCA's
   real adult population) has near-zero buffer, so a shock hits them with **no cushion at all** —
   testable as a distributional assertion on the draw, not eyeballed.
4. The debt-stack allocation, under a binding budget constraint, pays down debts in **consequence-
   severity order** (see the nuance above) — testable directly: construct a household with income <
   total-debts-due, assert the priority-tier debts (rent/council tax/energy/fines) are serviced
   before any non-priority debt (credit card etc.) is serviced at all.
5. **R12/Law A discipline as a testable property, not just a policy statement:** a unit test that
   asserts the module contains no free parameter directly keyed to "target bad-debt rate" or
   similar — the crisis-era bad-debt step-up must be checkable as an *emergent* consequence of
   re-running the same budget-allocation code against crisis-era prices, not a coefficient tuned to
   reproduce the Ofgem 2025 figures above.

### (c) What a genuine Expert-Hour review would need to check

- Pull the actual drawn population's income-band histogram and essential-cost-floor values and
  compare them directly against the cited HMRC percentile table and the JRF/CRSP MIS figures for
  the matching household composition and year — not "looks about right," an actual side-by-side
  number check, the same discipline this project's own Expert Hour passes already apply elsewhere
  (e.g. `W2_1_archetype_layers`'s 2026-07-10 pass, which pulled real population distributions
  against DESNZ/Ofgem anchors and found one real small-sample-noise false positive by checking the
  rng/expected-count directly rather than assuming a bug).
- Check the debt-stack ordering logic against the consequence-severity framing above, specifically:
  does a household facing eviction-risk-plus-energy-arrears service rent first uniformly, or does
  the model account for the real regulatory asymmetry (a supplier facing PPM-as-last-resort/winter
  disconnection protections is a *weaker* creditor threat than a landlord pursuing eviction) — this
  is exactly the kind of "veteran recognises the mechanics" test the Expert Hour bar names.
- Verify the wall discipline holds under adversarial reading: grep the company-side code paths for
  any read of the hidden budget/income-band/savings-buffer state, not just trust the registration's
  prose — this is a Tier-1-adjacent property (epistemic law) even though the atom itself is not
  Tier 1, so it deserves the same scrutiny `tools/epistemic_verifier.py` would apply.
- Confirm the crisis-era step-up is genuinely emergent by re-running `company/compliance/
  crisis_bad_debt_validator.py::validate_run_output()` (already built, currently and expectedly
  FAILING) against output generated *after* this atom lands, and reading the actual before/after
  numbers rather than accepting a "now passes" claim at face value (R1: consumer-verified
  completion).

---

## W2_5_life_event_stream — shared life-event generator

### (a) Real-world twin, concrete enough to build against

The atom names five event types (job loss, illness, divorce, retirement, new child) explicitly as
**one shared substrate** serving both this cluster and the adoption-journey's key-moment conversion
windows (`C5_key_moment_conversion`) — a genuinely good design constraint (don't build two event
generators for the same real phenomena) that this pass does not need to relitigate. What needs
concretising is the anchor for each event's **incidence rate**, so the generator draws at a
population-plausible frequency rather than an invented one:

- **Job loss / unemployment flow rate** — ONS's own **Labour Force Survey** unemployment/
  redundancy rate series (`ons.gov.uk`, published monthly as part of the labour market statistics
  bulletin) is the standard real anchor; **[L]** I have not pulled a specific current figure this
  session — the next pass that actually builds this atom should fetch the live LFS redundancy rate
  rather than use a stale or invented one.
- **Illness (long-term sickness)** — ONS again publishes **economic inactivity due to long-term
  sickness** as a headline labour-market series; **[L]** same caveat, fetch live at build time.
- **Divorce/separation** — ONS **Divorces in England and Wales** annual statistics publish a
  divorce rate per 1,000 married population; **[L]** not fetched this session.
- **Retirement** — DWP State Pension age population combined with ONS labour-market
  economic-inactivity-due-to-retirement figures; **[L]** not fetched this session.
- **New child** — ONS **Birth characteristics**/live births statistics give a real per-household
  incidence rate directly; **[L]** not fetched this session.

None of these five rates were independently re-verified this pass (time-boxed to the atoms already
registered); every one is flagged **[L]** rather than asserted with invented precision, per this
project's own convention — the DISCOVER step for this atom, when it opens, should fetch each one
specifically rather than inherit this charter's placeholders as if they were verified figures.

### (b) L3 concrete meaning

1. Each event type fires at a population rate that is **directly traceable to a named, dated ONS
   (or equivalent) series** the way `W2_1_archetype_layers`'s existing anchors already are — not a
   round invented number like "5% per year."
2. An event, once fired, produces a **measurable, mechanistically-linked** change in the *same*
   household's budget state from `W2_4` (income drop for job loss, cost increase for illness,
   household-composition and cost-floor change for divorce/new child) — testable as a direct
   before/after state diff on the specific household, not a population-level statistical nudge
   applied independently of any individual household's actual budget object.
3. The **same event instance** is consumable by both this cluster's payment-difficulty trigger *and*
   `C5_key_moment_conversion`'s adoption-window logic without duplication — testable as: one event
   generator module, two distinct consumers, zero second implementation of "job loss" anywhere else
   in the codebase (a structural/grep-able test, not just a design intention).
4. Event co-occurrence/clustering is handled honestly: a real household can face more than one event
   in a period (illness *and* job loss together is a real, more severe case) — L3 requires this not
   be structurally prevented by the generator (e.g. a naive "one event per household per year" cap
   that would silently understate the compounding cases most likely to drive genuine arrears).

### (c) What a genuine Expert-Hour review would need to check

- For each of the five event types, an actual fetch of the current ONS (or DWP) series and a
  side-by-side comparison against the rate the generator actually draws at — closing every **[L]**
  tag above with a real citation before claiming L2, let alone L3.
- Confirm by reading the code (not the docstring) that `C5_key_moment_conversion` and the payment-
  difficulty trigger genuinely share one generator instance/module, per the DoD's own "do not build
  two" instruction — a structural check, the same class of check that caught the D3 atom's
  duplicated-`simulate_read()`-call issue in this project's own build history.
- Sample a handful of generated households by eye (this project's own R10/0c "read one instance as a
  human" discipline) and ask whether the sequence of life events over a 5-10 year customer lifetime
  reads as a plausible human life, not a Poisson-process curiosity (e.g. retirement firing for a
  25-year-old archetype would be an immediate, obvious failure worth catching before any automated
  test would).

---

## W2_6_sme_distress_twin — SME/I&C distress twin

### (a) Real-world twin, concrete enough to build against

- **Insolvency incidence and sector shape** — the **Insolvency Service's Company Insolvency
  Statistics** (published monthly/quarterly on GOV.UK, e.g.
  `gov.uk/government/statistics/company-insolvencies-november-2025`) give real, current, sector-
  broken-down figures: in the 12 months to October/November 2025, the highest-insolvency sectors
  were **Construction (~3,973 cases, ~17% of cases with industry captured)**, **Wholesale/retail
  trade incl. motor vehicle repair (~3,768, ~16%)**, **Accommodation and food service (~3,423,
  ~14%)**, **Administrative and support services (~2,459, ~10%)**, and **Manufacturing (~1,991,
  ~8%)** — together with the overall rate, **~1 in 189 companies on the Companies House effective
  register (52.9 per 10,000) entered insolvency** in that period. This is directly usable: if the
  SME/I&C customer population is drawn with sector labels, the insolvency-event rate per sector
  should be anchored to these real, sector-differentiated figures rather than one flat SME
  insolvency rate applied uniformly — a construction-sector I&C customer is a meaningfully different
  distress risk from a professional-services one, and the real data says so directly.
- **Late-payment culture** — **[L]**: I have not this session pulled a specific, current, named
  survey (e.g. a Bacs/Federation of Small Businesses late-payment survey) quantifying UK B2B
  late-payment incidence/duration; this is a real gap to close at DISCOVER time rather than a figure
  to invent now. What *is* directly load-bearing and already anchored elsewhere in this cluster is
  the **statutory** late-payment regime itself (see `W2_9` below) — the culture/incidence rate is
  the missing piece, not the legal mechanism.
- **The "bad debt PLUS lost supply point" framing** (the atom's own text) is the correct real
  mechanic to build against: a real SME/I&C insolvency is not merely a write-off, it is Supplier of
  Last Resort (SoLR) territory from the *other* side (a competitor's insolvent customer becomes this
  company's SoLR gain, or vice versa) — worth explicitly cross-referencing `W2_3_competitor_field`'s
  own charter note that Centrica's real FY2025 results disclosed **+91,000 customers gained via the
  SoLR process following two competitor supplier failures** (`docs/design/charters/
  W2_customer_generator.md`'s own citation chain traces to Centrica's FY2025 PR) — i.e. this atom's
  "lost supply point" is the mirror image of a real, already-cited phenomenon this codebase has
  independently anchored on the company side.

### (b) L3 concrete meaning

1. Insolvency events fire at **sector-differentiated rates matching the real Insolvency Service
   sector spread** (construction/hospitality meaningfully higher than the population-wide average;
   see figures above), not one flat SME rate — testable as a stratified-by-sector comparison against
   the cited real figures.
2. An insolvency event produces **both** a bad-debt write-off (the AR balance at time of failure)
   **and** a supply-point loss (the meter point exits this company's book, structurally, the same
   way a domestic churn event does) — testable as: does the event handler touch both the ledger
   *and* the customer/portfolio roster, not just one.
3. Late-payment behaviour for surviving (non-insolvent) SME/I&C customers is **distinct from and
   less severe than** the insolvency-triggered event — i.e. the model must not conflate "pays late"
   with "is about to fail," which real late-payment-culture research (once anchored, per the [L]
   flag above) would be expected to show as two overlapping but distinct populations.
4. The SME/I&C population's late-payment/distress signature is measurably **different in shape**
   from the domestic household budget mechanism in `W2_4` (an insolvency is closer to a discrete
   failure event than a gradually-tightening budget) — a testable structural difference, not the
   same mechanism relabelled for a different customer segment.

### (c) What a genuine Expert-Hour review would need to check

- Fetch the *current* Insolvency Service statistics at review time (not this charter's July 2025/26
  snapshot) and re-verify the sector rates the model uses are still a reasonable match, since these
  figures move monthly and this document's citation will age.
- Confirm the "lost supply point" mechanic actually removes the meter point from the book in the
  same code path domestic churn uses, rather than a parallel, possibly-inconsistent implementation
  (the DD-attribution-confound atom below names exactly this class of "two pipelines, never
  cross-referenced" bug as a recurring real risk in this codebase).
- Check whether the late-payment-culture anchor (once found) is actually distinguishable in the
  model's own output from the insolvency event — i.e. can a company-side analyst, looking only at
  observable signals, tell the difference between "a slow payer" and "a company about to fail"? A
  real credit-risk veteran would expect these to be different signatures with overlapping but
  distinguishable signals, not the same thing at two severities.

---

## W2_7_willingness_classification — can't-pay vs won't-pay 2x2

### (a) Real-world twin, concrete enough to build against

This is the atom where the honest answer is: **the "can't-pay/won't-pay" framing itself is
contested in the real UK energy-debt policy debate, not a settled classification the industry
agrees on** — a genuinely important finding for this charter to surface rather than paper over.
Ofgem's interim chief executive (Tim Jarvis) publicly linked energy arrears to a "can't pay, won't
pay" framing, and was directly challenged by the **End Fuel Poverty Coalition**, which disputes the
evidential basis for treating non-payment as often deliberate rather than near-universally
ability-driven (reported in *Utility Week*, "Ofgem chief blasted for 'reductive' view of people in
energy debt," `utilityweek.co.uk/ofgem-chief-blasted-for-reductive-view-of-people-in-energy-debt/`).
**This matters directly for the atom's own build**: the director's registration already anchors
willingness incidence to "Ofgem debt research / industry sources... tag [L] and verify" — this
search confirms that even Ofgem's own leadership stating a willingness-incidence view has been
publicly contested on evidential grounds, so any specific numeric split this atom eventually encodes
(e.g. "X% of non-payment is won't-pay") should be treated as **actively disputed**, carrying an
explicit [L] tag and probably a documented range/uncertainty band rather than a single number, and
ideally sourced to more than one side of this live debate rather than Ofgem's framing alone.

### (b) L3 concrete meaning

1. The hidden 2x2 (ability × willingness) genuinely generates all **four** quadrants in the drawn
   population, not just the two "obvious" ones (can't-pay+unwilling-doesn't-apply, can-pay+willing)
   — testable directly as a population-level check that all four cells have non-zero occupancy.
2. The company-side classifier's accuracy is measured **against the hidden truth** (the harness's
   own "answer-key pattern," per the registration) and is **structurally incapable of being 100%
   correct** — if a test ever shows the classifier perfectly recovers the hidden quadrant, that is
   itself a defect (it means the observable signals leak the hidden state, an epistemic-wall
   violation in spirit even if not in the literal import-scan sense) rather than a success to
   celebrate.
3. **Mis-classification cost is asymmetric and both-directional, and both directions are separately
   testable**: a can't-pay household classified as won't-pay must trigger a distinct, measurable
   harm/compliance-exposure signal (the ability-to-pay rules this household should have received
   were denied); a won't-pay household classified as can't-pay must show up as a measurable loss/
   moral-hazard signal (concessions granted to someone who didn't need them). Two separate test
   paths, not one generic "accuracy score."
4. Given the contested real-world evidence above, the model's willingness-incidence rate is encoded
   as an explicit, named, versioned parameter with its [L] tag and source dispute visible in code
   comments/`ASSUMPTIONS.md` — not silently picked and hidden, so a future director/advisor review
   can see exactly what was assumed and revisit it as better evidence emerges (this is itself a
   CURRICULUM-adjacent question under R13's logic: how much willingness-driven non-payment to model
   is close to a director-owned calibration decision precisely because the real number is disputed).

### (c) What a genuine Expert-Hour review would need to check

- Read the actual willingness-incidence constant/distribution in the code and confirm it is (i)
  tagged [L], (ii) traceable to a named source, and (iii) does not silently overstate confidence
  given the contested evidence base found above — this is exactly the kind of thing this project's
  own Qwen-skeptic pass and phase-close-evaluator are built to catch.
- Verify the classifier is built from **company-observable signals only** (payment history, plan
  adherence, engagement, disclosure) and never reads the hidden ability/willingness state directly
  — an epistemic-wall check specific to this atom, worth an explicit grep pass even though the atom
  is not formally Tier 1.
- Confirm both mis-classification harm signals (Consumer Duty/ability-to-pay-rule breach; loss/moral
  hazard) are wired to something a real compliance/finance function would actually look at — a
  metric that exists only in a test assertion and never reaches a business surface would fail
  CLAUDE.md's own 0b rule (evidence lands on business surfaces, not specs).

---

## W2_8_self_rationing — pay-but-don't-heat

### (a) Real-world twin, concrete enough to build against

- **The phenomenon itself is Ofgem's own named, decided policy area**: *"Self-disconnection and
  self-rationing: decision"* (`ofgem.gov.uk/sites/default/files/docs/2020/10/self-
  disconnection_and_self-rationing_decision.pdf`) — Ofgem's **2019 Consumer Survey found ~1 in 7**
  of the ~4 million UK prepayment-meter households had self-disconnected in the past 12 months, and
  the resulting licence changes require suppliers to **identify** self-disconnecting/self-rationing
  customers and offer **emergency credit, friendly-hours credit, and additional support credit** —
  i.e. detection is a real, named, licence-level supplier obligation, not a novel invention of this
  project.
- **Enforcement is live and recent**: Ofgem's investigation and settlement with **OVO** for failing
  to consistently support customers who self-disconnected (`ofgem.gov.uk/press-release/ovo-agrees-
  settlement-relation-ofgems-investigation-its-monitoring-prepayment-meter-customers`) is a directly
  citable real incident of a supplier *missing* exactly the detection duty this atom's registration
  names — good evidence that "missed detection is a harm event" (the atom's own phrasing) is not
  hypothetical.
- **"Plausible living level" floor**: the atom's registration correctly points at reusing the
  existing **Ofgem TDCV (Typical Domestic Consumption Value) bands already encoded in
  `company/compliance/domain_invariants.py`** (Low/Medium/High bands for electricity and gas,
  sourced "Ofgem TDCV 2026 review") rather than re-deriving a floor from scratch — confirmed by
  reading that file directly this session: `TDCV_ELEC_LOW` (1400-1800 kWh/yr), `TDCV_GAS_LOW`
  (5500-6500 kWh/yr) etc. already exist as `RangeInvariant` objects. A self-rationing household's
  consumption dropping **meaningfully below the Low band's own floor** (not just "below Medium") is
  the concrete, already-anchored trigger condition.

### (b) L3 concrete meaning

1. Generated self-rationing households have a **perfect or near-perfect payment record** (this is
   the defining, counterintuitive feature named in the registration) — testable directly: filter the
   population for consumption below the TDCV Low-band floor with zero missed payments, and confirm
   the generator actually produces non-zero occurrence of this combination (a naive
   propensity-linked model would likely conflate low consumption with payment difficulty, which is
   precisely the wrong correlation to encode here).
2. The detection capability (company-side, C/F atom) is tested **against this atom's generated
   ground truth** with an explicit false-negative rate — a missed detection is logged as a harm
   event with the same rigor as the willingness-misclassification harms in `W2_7`, not merely a
   silent gap.
3. The consumption floor is anchored to the **existing** `domain_invariants.py` TDCV constants
   (reused, not re-derived) — testable as: the self-rationing trigger threshold literally imports/
   references those same constants rather than a second, possibly-drifting copy.
4. Self-rationing is distinguishable in the model from ordinary low consumption (e.g. a genuinely
   small, efficient household) — L3 requires the *generation* mechanism to carry the true label
   (vulnerable-self-rationing vs. genuinely-low-need) even though the company can only see the
   consumption pattern, so the detection-accuracy test in point 2 has a real ground truth to check
   against rather than an ambiguous population.

### (c) What a genuine Expert-Hour review would need to check

- Confirm by reading the code that the self-rationing consumption floor literally imports
  `domain_invariants.TDCV_ELEC_LOW`/`TDCV_GAS_LOW` (or the equivalent) rather than a second
  hardcoded threshold — the exact "two pipelines never cross-referenced" bug class this project has
  hit before (`W2_10` below, and the D2/E2 two-pipelines findings already in the map).
- Check the detection atom's harm-event logging actually reaches a business surface (Customer
  Ops/Compliance tab) per CLAUDE.md 0b, not just a test assertion.
- Sample one generated self-rationing household by eye (R10/0c discipline) and ask: does a payment
  ledger showing zero missed payments alongside a winter gas consumption collapse read as a
  recognisable, real vulnerability pattern to someone who has worked energy-supplier debt/
  vulnerability operations? This is squarely the kind of thing the Expert Hour's "veteran walks the
  surface" test is built to catch, and squarely the kind of thing automated invariants alone would
  likely miss (the exact class R10 was written to close).

---

## W2_9_segment_debt_tnc — segment T&C / regulatory overlay on debt

### (a) Real-world twin, concrete enough to build against

- **Business (statutory, precise, already have a real citable rate):** the **Late Payment of
  Commercial Debts (Interest) Act 1998**, as amended, sets the default statutory interest rate for
  B2B late payment at the **Bank of England base rate (fixed at the rate in force on the preceding
  30 June or 31 December) plus 8 percentage points** — simple interest, not compounded, running from
  the day after the payment becomes overdue, and displaceable only by a contractually-agreed
  "substantial remedy" (`gov.uk/late-commercial-payments-interest-debt-recovery/charging-interest-
  commercial-debt`; the Act's own text at `legislation.gov.uk`). This is a precise, directly
  encodable real formula, not a range — no [L] tag needed for the rate itself; **[L]** on whether
  UK energy I&C supply contracts as a matter of common commercial practice actually invoke this
  default or displace it with a bespoke contractual rate (worth verifying at build time rather than
  assumed).
- **Domestic (regulatory exclusion, already registered correctly):** Ofgem's Standard Licence
  Conditions and Consumer Duty framework restrict late-payment *charges* on domestic accounts far
  more than commercial norms would otherwise allow — the atom's own registration text states this
  correctly; the citable regulatory home for this is the Ofgem Standard Licence Conditions
  themselves (SLC — the same regulatory-oracle infrastructure this codebase already encodes
  Top-20-style obligations against, per `REGULATORY_RULES_AS_FIDELITY_ORACLE.md`'s own precedent).
- **Payment-conditioned tariff eligibility (DD-discount, good-payer gating):** this is standard,
  observable, real UK commercial practice — Direct Debit dual-fuel tariffs priced below cash/
  cheque-payment equivalents is visible on every UK supplier's public tariff sheet; the atom's own
  instruction to model this as a **company-side policy object with fairness/oracle constraints**
  (not a free-floating discount parameter) is the right shape, and should sit next to
  `W2_10_dd_attribution_confound`'s own finding that the DD cohort's apparent "better payer" quality
  is partly a selection artefact — a policy object that prices DD-discount off a *biased* apparent
  payment-quality signal is itself a fairness-oracle-relevant risk this atom should be built to
  expose, not just to price.

### (b) L3 concrete meaning

1. A business account in arrears accrues interest calculated with the **actual BoE base rate in
   force on the correct reference date (30 June or 31 December preceding)** plus 8pp, simple, from
   the day after due date — testable as an exact arithmetic reproduction of the statutory formula
   against a hand-worked example, the same rigor this codebase already applies to the Ofgem price
   cap and VAT invariants.
2. A domestic account in arrears is **structurally incapable of accruing a late-payment charge**
   that the current SLC/Consumer Duty regime would prohibit — testable as a negative assertion (no
   such charge object is ever created for a domestic account), not merely "the number happens to be
   zero."
3. DD-discount tariff eligibility is modelled as a **named policy object** (not an inline
   `if payment_channel == 'dd': discount` conditional) with an explicit, checkable fairness
   constraint tied to the actual payment-quality signal it uses — and that signal's own known bias
   (the `W2_10` selection effect) is visible/queryable from the object, not hidden inside it.
4. The asymmetry itself — business accrues statutory interest, domestic largely doesn't but can lose
   tariff eligibility instead — is asserted as a structural test: run the same arrears scenario
   through both a business and a domestic account and assert the *consequences* genuinely differ in
   kind, not just in magnitude.

### (c) What a genuine Expert-Hour review would need to check

- Hand-verify the statutory interest calculation against a real worked example (a specific overdue
  invoice amount, days overdue, and the actual BoE base rate on the correct reference date) — this
  project's own bill-correctness discipline (R10, 0c) already sets the precedent of hand-verifying
  arithmetic against domain law rather than trusting a formula was implemented correctly by
  construction.
- Confirm no domestic-account code path can construct a late-payment-charge object at all (not just
  that current tests don't exercise one) — a structural/exhaustive check, not a sampled one.
- Check the DD-discount policy object's fairness constraint against the actual `W2_10` finding once
  that atom is built — does the policy object correctly flag that its own eligibility signal is
  contaminated by the DD-attribution confound, or does it price off the naive (biased) signal
  uncritically? This is the direct cross-atom consistency check a real veteran (or the fresh-context
  `phase-close-evaluator`) would ask for.

---

## W2_10_dd_attribution_confound — the DD attribution trap (first of a named class)

### (a) Real-world twin, concrete enough to build against

The mechanism itself needs no external citation — it is a structural selection-bias argument, not an
empirical claim: **failing payers migrate off Direct Debit before they fail** (DD mandates get
cancelled by the bank on repeated failed collection, or customers proactively switch to cash/cheque
once they anticipate trouble), so the surviving DD cohort is disproportionately clean **by
construction**, not because DD itself causes better payment behaviour. This is a well-known
methodological trap in credit-risk/marketing analytics generally (survivorship bias applied to a
payment channel rather than to firms/funds) — **[L]**: I have not this session found a UK-energy-
specific published study naming this exact trap for DD-discount tariffs (the atom's own registration
already flags "Ofgem payment-method debt research [L]" as unverified); the mechanism's *logic* is
sound and does not depend on that citation existing, but the specific magnitude of the effect in the
real UK energy market remains unanchored and should stay flagged rather than assumed.

This project's own build history already surfaced a **live, present-day instance of the underlying
class of bug** this atom formalises: `coldwalk:payment_channel_dd_fail_contradiction` (adjudicated-
real, per the atom's own evidence trail) — `payment_channel` and `dd_fail` state were computed by
two independent pipelines never cross-referenced. That is direct, in-codebase evidence that this
trap is not a hypothetical concern for this project specifically.

### (b) L3 concrete meaning

1. The SIM's ground truth genuinely contains the **migration event** (a customer moving off DD
   shortly before/around a failure), not just the eventual bad-debt outcome — testable as: pick a
   sample of SIM-truth failing accounts and confirm a channel-migration event exists in their
   history at a materially higher rate than in the surviving population.
2. A company-side analytics function computing "DD accounts have X% lower bad debt than non-DD"
   using **only observable data** must be capable of reproducing the naive, confound-contaminated
   conclusion — if the company-side number always came out correctly attributed, the trap isn't
   really modelled; L3 requires the naive analysis to be **plausible-looking but wrong**, matching
   the "should be capable of being wrong" language in the registration.
3. The harness independently computes the **true** channel-attributable effect (controlling for the
   migration) from SIM ground truth and scores the company's naive attribution against it — the
   same "answer-key pattern" already named for `W2_7`, reused rather than re-invented (this project's
   own reuse discipline, e.g. reusing `BAD_DEBT_RATE_RESI` rather than re-deriving a duplicate
   constant).
4. This is registered and built as the literal **first entry** of a named class ("selection-bias
   traps the company must discover") without inventing separate trap-register infrastructure — L3
   for *this atom* does not require the class-level registry to exist yet, only that this instance
   is built and correctly scored; a future second trap instance is what would justify generalising
   the pattern into shared infrastructure (YAGNI discipline, consistent with this project's own
   "note it clearly rather than invent infrastructure" instruction already in the registration).

### (c) What a genuine Expert-Hour review would need to check

- Directly reproduce the naive company-side DD-discount business case (the same kind of analysis a
  real commercial/pricing analyst would run) against SIM output and confirm it *actually* looks
  favourable to DD before being told the true, confound-corrected answer — the review needs to feel
  the trap, not just read that it exists.
- Cross-check this atom's fix against the already-adjudicated real bug
  (`coldwalk:payment_channel_dd_fail_contradiction`) to confirm the SAME root cause (two
  uncross-referenced pipelines) doesn't recur elsewhere in the channel-attribution code once this
  atom is built — this project's own R3 (two-strike redesign) logic applies if a second instance of
  this exact class shows up post-fix.
- Check whether `W2_9`'s DD-discount policy object (above) actually consumes this atom's corrected
  signal once both exist, rather than the two atoms shipping independently and leaving the policy
  object still pricing off the naive, biased view — a cross-atom wiring check, not just a per-atom
  one.

---

## Named best-practice references (consolidated)

- HMRC, *Percentile points from 1 to 99 for total income before and after tax* (Table 3.1a),
  `gov.uk/government/statistics/percentile-points-from-1-to-99-for-total-income-before-and-after-tax`
- ONS, *Effects of taxes and benefits on household income*,
  `ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth`
- Joseph Rowntree Foundation / Loughborough University CRSP, *A Minimum Income Standard for the
  United Kingdom in 2025*, `jrf.org.uk/a-minimum-income-standard-for-the-united-kingdom-in-2025`
- FCA, *Financial Lives* survey (2022/2024 waves), `fca.org.uk/publication/financial-lives/`
- StepChange, *Priority Debts & Which Bills To Pay First*,
  `stepchange.org/debt-info/dealing-with-debt-problems/what-debts-to-pay-first.aspx`
- MoneyHelper, *How to prioritise your debts*,
  `moneyhelper.org.uk/en/everyday-money/credit/how-to-prioritise-your-debts`
- Ofgem, *Debt and arrears indicators*, `ofgem.gov.uk/data/debt-and-arrears-indicators`
- Ofgem, *Self-disconnection and self-rationing: decision* (2020),
  `ofgem.gov.uk/sites/default/files/docs/2020/10/self-disconnection_and_self-rationing_decision.pdf`
- Ofgem, press release re: OVO prepayment-meter monitoring settlement,
  `ofgem.gov.uk/press-release/ovo-agrees-settlement-relation-ofgems-investigation-its-monitoring-prepayment-meter-customers`
- Insolvency Service, *Company Insolvency Statistics* (monthly/quarterly), e.g.
  `gov.uk/government/statistics/company-insolvencies-november-2025`
- Late Payment of Commercial Debts (Interest) Act 1998 (as amended); summary at
  `gov.uk/late-commercial-payments-interest-debt-recovery/charging-interest-commercial-debt`
- *Utility Week*, "Ofgem chief blasted for 'reductive' view of people in energy debt,"
  `utilityweek.co.uk/ofgem-chief-blasted-for-reductive-view-of-people-in-energy-debt/` — evidence
  that the can't-pay/won't-pay framing itself is contested, load-bearing for `W2_7`'s [L] tagging.
- Existing in-codebase anchors reused, not re-derived: `company/compliance/domain_invariants.py`
  TDCV bands (`W2_8`); `docs/market_research/ASSUMPTIONS.md` `BAD_DEBT_RATE_RESI`/`BAD_DEBT_RATE_SME`
  and the Centrica FY2025 bad-debt-driver citation (cross-cutting backdrop).

## Simplifications register (this charter itself)

- Every life-event incidence rate in `W2_5` is flagged **[L]** — none was fetched live this session;
  this is the single largest remaining DISCOVER gap in the cluster.
- `W2_6`'s late-payment-culture incidence (as distinct from the statutory late-payment *rate*, which
  is precisely anchored) is **[L]** — no specific current UK B2B late-payment survey was located
  this session.
- `W2_7`'s willingness-incidence split is **[L]** and, per the Utility Week finding, **actively
  disputed** in the real UK debt-policy debate, not merely unverified — this is a stronger caveat
  than a simple missing-citation flag and should be carried forward as such.
- `W2_10`'s real-world magnitude (how much bad debt actually migrates cohorts via this exact
  mechanism in the UK energy market specifically) is **[L]** — the structural logic is sound and
  independently evidenced in-codebase (the adjudicated `payment_channel_dd_fail_contradiction` bug),
  but no external UK-market-specific study was found quantifying it.
- The HMRC vs. ONS income-dataset unit-of-measure reconciliation for `W2_4` (individual taxpayer vs.
  equivalised household) was not resolved this session — flagged for the atom's actual DISCOVER
  pass, not silently assumed compatible.
