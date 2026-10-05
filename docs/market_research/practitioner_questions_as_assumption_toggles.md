# The step-1 practitioner questions, owned: research, derivation, toggles and sensitivity

**Knowledge:** none -- a register of assumption toggles across the step-1 areas; each toggle is cited from its area's page

*Written 2026-10-05 under the director's ruling of the same day: "The four questions. Own them. Most
can be researched, derived by logic or estimated. Where the truth isn't published, make it an
assumption toggle: a parameter with a plausible range, and test whether the answer changes across
it. If it doesn't change any decision, the question doesn't matter. If it does, dig harder — and
only bring it to me if it's both decision-changing and unresolvable."*

The machine-readable register is `docs/market_research/assumption_toggles.yaml`. An atom that needs
one of these quantities reads it there and never types its own number. The sensitivity results
below came from a read-only analysis script that is NOT in the tree, because its inputs are not:
it re-scored the decision probe's saved rows `/var/tmp/se-probe-out/probe_attr_{default,61001,61002,61003}.json`,
four reference paths on one book, about 81 renewal decisions each, written 2026-10-04.

Source grades follow the area pages: **[H]** read in the primary document this pass; **[M]** a
secondary or summarised source, or a figure recalled and not re-read; **[derived]** arithmetic shown
here.

**Headline.** Five questions, nine toggles and no escalation. Four results matter most:

- **Q2's persistence does not change the size of back-billing losses.** It cancels out exactly: a
  calibrated read process loses the same share of consumption to the 12-month rule whether or not
  non-reading persists. What sets that share is the size of the estimate error.
- **Q5 is resolved, and it exposes a defect in published code.** The carbon footprint reports a
  household that moved its gas to another supplier as cutting 2,173 kg a year. That is a bigger
  cut than a real heat pump gives in the same test (1,738 kg).
- **Q1, Q3 and Q4 do not change any renewal-price decision.** Each was tested at both ends of its
  plausible range.
- **Q4's binding constraint is the size of the book.** At ~80 decisions, a holdout of any size
  cannot measure a retention effect.

---

## How the sensitivity test reads

**What counts as "a decision".** The decision probe makes four decisions from its rows. Each is
compared before and after a toggle:

1. the hindsight flat margin level;
2. the ex-ante flat level for each decision year, chosen from the decisions closed before that year;
3. the sign of `value_capped − flat`;
4. the sign of `value_capped − ex-ante flat`.

A toggle acts only through a quantity the scorer already reads: a row's true P(stay), or its
bad-debt share.

**The harness runs a placebo arm each time.** This is the same transform at a negligible setting,
and it moved nothing on any path. **One decision is a knife-edge of the instrument and is excluded:**
the 2018 ex-ante level (`ex-ante[2]`). Its closed book is **2 decisions** on every path (the harness
prints the book sizes: 0, 0, 2, 25, 39, 53, 76, 76). It flips between 15 and 95 under any material
perturbation, in either direction. A level chosen from two rows is not a decision.

**What a "no" means.** "No decision changes" means no level and no sign moved on any of the four
paths, other than that knife-edge. It does **not** mean the £ totals are unchanged. They move, and
the harness prints them.

---

## Q1. Home moves: how a supplier learns of a move, and how long an unnamed account runs

### Research

- **Move-out: the customer tells the supplier, and that notification is the binding channel.**
  Ofgem's *summary of responses* to the home-moves call for input (OFG1164, June 2026, ¶2.2):
  "accounts often remain unnamed for extended periods due to delays in receiving move out and move
  in notifications from consumers, resulting in consumption being charged to interim accounts that
  may not ultimately be recoverable." [H]
  - The same document (¶2.4) says the consumer bodies had no quantitative data.
  - The second channel in the private rented sector is the **landlord or letting agent**. The
    response filed as `EN25-01` in Ofgem's zip of non-confidential responses maps the sequence:
    "Landlord/Letting Agent Notifies Energy Supplier of New Tenant / CoT Event & Requests Final
    Bill". The landlord is liable in a void, and "the interim period could in some cases be days,
    but in others could be weeks or months." [H]
  - The supplier's other signals are the ones in `home_moves.md` §3: a bounced final bill, a
    cancelled DD, returned mail, a new occupier's call.
- **Move-in: two industry-visible routes and one letter cycle.**
  - The new occupier contacts the incumbent (case B′, supplier-internal).
  - A gaining supplier's switch carries the CSS Change of Occupier indicator (case B″; Ofgem CSS
    Service Definition, cited in `home_moves.md` §3).
  - Otherwise the supplier writes to "the occupier".
  - The water-sector comparator uses CRA footprints (Ofgem CfI Dec 2025, Information Box 1).
  - No published source ranks these channels by share.
- **How long an unnamed account runs: not published, and Ofgem asked for it and did not publish
  any.** The CfI asked for "the average length of unnamed accounts" (Q1) and "the average duration
  for a new householder to set up an account" (Q2). The June 2026 summary reports none: suppliers
  "reported high volumes of unnamed or unverified accounts, with associated high debt levels that
  had accumulated over prolonged periods" (¶2.1). [H] So Spring 2026 has come and gone, and this
  stays a **GAP in the public record**.
- **A new figure that sizes it.** Energy UK's response to the same CfI:
  - "On a 1-year timeline … the largest 5 suppliers accrued **£740 million of debt resulting from
    change of tenancy** and **£1.17bn of debt resulting from closed accounts**." [H]
  - So Energy's response: "the 20-40% estimate is within the range of our reasonable estimates". [H]

### Derivation: an average change of tenancy carries about 3 to 5 months of a typical bill in debt

- **The suppliers' debt.** £740m a year is the five largest suppliers' change-of-tenancy debt.
  Their share of domestic accounts is about 78% (Ofgem retail market indicators, end-2024 [M]: not
  re-read this pass). So the market is about **£949m a year** [derived].
- **The number of tenancy changes.** Households that move: EHS 2024-25 gives 1.8m for England
  (`simulation/arrival_route.py`). Scaled by households (GB about 27.8m [M] against England's
  25.0m), that is about **2.0m a year** in GB [derived].
- **The result.** £949m ÷ 2.0m ≈ **£474 per change of tenancy** [derived].
  - The typical dual-fuel direct-debit bill under the Oct–Dec 2024 cap was about £1,717 a year
    [M, recalled, not re-read]. That is £143 a month, so £474 is about **3.3 months** of it.
  - Movers, mostly renters in smaller homes, likely use less than the typical home. At 70% of
    typical use, £474 is **4.7 months**.
- **What this bounds.** CoT debt per move ≈ (share of move-ins that go unnamed × mean months
  unnamed × share never recovered) + the departing occupier's unpaid final bill. So the expected
  unnamed, unrecovered months per move is **at most about 3 to 5**.
- **Caveat.** "Debt resulting from change of tenancy" is the suppliers' own classification. Its
  definition is not given, and Ofgem's 20–40% may be on a different base. This is an
  order-of-magnitude bound, not a calibration.

### Toggles

- `q1_move_out_notice_share`
  - **Meaning:** of move-outs at a premises we supply, the share where the departing occupier (or
    the landlord) tells us by move day. The rest we learn of later, from a bounced final bill, a
    cancelled DD or a new occupier.
  - **Values:** default **0.7**; low 0.5; high 0.9.
  - **Basis:** the industry's own description is that suppliers depend on consumer notification,
    and that it is often late (Ofgem SoR ¶2.2). No published share exists, so the range is wide.
    - Low end: the consumer bodies' case evidence and the 20–40% debt share.
    - High end: owner-occupier sales, where conveyancing creates the date and the read.
- `q1_unnamed_months_per_cot`
  - **Meaning:** the expected unnamed months per change of tenancy. That is the probability a
    move-in is not named by move day, times the mean months until it is named. This is the
    product, because only the product is bounded.
  - **Values:** default **3**; low 1; high 6.
  - **Basis:** the derivation above (3.3 months at typical use, 4.7 at 70%).
    - Low end: a few weeks for most moves, consistent with Citizens Advice's 48-hour guidance
      being mostly followed.
    - High end: all £474 is unnamed and unrecovered at 70% use, and some named accounts later pay.
  - **Control:** the world's **CoT debt per move must land in about £300–£650** at 2024-25 prices.
    The atom grades it against that.

### Sensitivity

- **Renewal pricing.** The deciding code exists (`tools/decision_probe.py`). The harness adds a
  price-insensitive annual move hazard by tenure to every row's true P(stay):
  - the rates are EHS 2024-25 moves-in over households (owner 3.8%, private rent 17.5%, social
    4.6%);
  - tenure is assigned by EHS household shares under three seeds;
  - the multipliers are ×0.5, ×1 and ×2.

  Results:

  | multiplier | paths whose decisions moved (of 4) |
  |---|---|
  | ×0.5 | 0, under all three seeds |
  | ×1 (EHS) | 0, under all three seeds |
  | ×2 | 1 path, under 2 of 3 seeds: one ex-ante year moved one grid step (2021 45→35, or 2019 30→35) |

  £ totals shrink because fewer customers are kept, but no sign flips. **The move hazard does not
  change the pricing decision across its range.** A uniform hazard cannot change it at all, because
  it scales every price's outcome by the same factor. Only a hazard correlated with price
  sensitivity could, and EHS gives no such link.
- **Debt and CoT handling.** The deciding code does not exist: B7, W2_38, EP4, and
  `TenancyChangeCoupler` has no caller. Acceptance criterion for B7 (and W2_38 for the debt half):
  1. The world draws move-outs and move-ins by tenure. Notice-on-time and unnamed duration are read
     from the two toggles above, never typed in.
  2. At default, low and high of each toggle, B7 prints:
     - CoT debt per move (it must sit in £300–£650);
     - CoT debt as a share of all debt (it must sit in 10–40%, the union of Energy UK's 10–15% and
       Ofgem's 20–40%);
     - every company decision the atom builds: the occupier-letter cadence, the provision rate on
       unnamed accounts, whether to buy CRA footprints.
  3. A decision that moves between the ends goes back to this register with the evidence; one
     that does not move is recorded as **DOESN'T MATTER**.

### Verdict

- **How a supplier learns of a move-out: RESOLVED.** Mostly the customer tells it, often late. In
  private rented homes the landlord or agent is a second channel. Ofgem SoR ¶2.2; EN25-01.
- **How it learns of a move-in: RESOLVED in kind, not in share.** The occupier calls, a
  CoO-flagged switch arrives, or the occupier answers the "occupier" letter cycle.
- **How long an unnamed account runs: MATTERS AND RESOLVABLE.** It is bounded by derivation at
  about 3 to 5 unnamed-and-unrecovered months per move. It does not change the renewal decision
  (tested). It feeds the debt atoms, whose acceptance criterion grades the world against the £/move
  band. Not for the director.

---

## Q2. Persistent non-reads: are a minority unread year after year?

### Research

- "**In the first half of 2017, just over 7% of domestic consumers went more than a year without
  getting an accurate bill**" (Ofgem, *Protecting consumers who receive backbills*, statutory
  consultation, 16 Nov 2017, ¶1.1, from Citizens Advice data). [H] The median supplier was 94.8% /
  94.4% (Ofgem decision, 5 Mar 2018, p.10). [H]
- **Back-bills in complaints.** Median domestic back-bill **£1,160**; **median length 24
  months**; extremes over £10,000. The sample was 203 Citizens Advice consumer-service cases,
  Oct 2016–Mar 2017, so it is a complaint-selected population (same consultation, ¶2.1 and fn 16).
  [H]
- **Catch-up bills across the population.** "As many as **2.1 million households** could have been
  hit by large late bills in the last year", averaging **£206**, with 15% over £250 (Citizens
  Advice press release, 29 Feb 2016). [H for the quote; the survey method is not given]
- **The read duty.** SLC 21B: take all reasonable steps to obtain a reading at least once a year
  (Billing Regulations 2014; the consultation's fn 33). [H] It is a duty of effort, not a guarantee.
  The world's forced read at 12 months models it as a guarantee.
- **Elexon's settlement curve.** NHH energy settled on actual reads is **30 / 60 / 80 / 97%** at
  R1 / R2 / R3 / RF = **2 / 4 / 7 / 14 months** (Elexon *Settlement Timetable* 2014, in
  `elexon_settlement_run_timetable_verified.md`). [H]

### Derivation (the arithmetic is in the harness)

**1. The settlement curve is close to memoryless, and matches the 7%.** Under independent monthly
reads with probability p, the share of a day's energy still unread t months later is (1−p)^t:

| run | months | observed actual | implied p |
|---|---|---|---|
| R1 | 2 | 30% | 0.163 |
| R2 | 4 | 60% | 0.205 |
| R3 | 7 | 80% | 0.205 |
| RF | 14 | 97% | 0.222 |

- The hazard **rises** slightly with time. That is the annual read effort, plus the lag of the
  first run. A persistent never-read class would make the hazard **fall** with time.
- At p = 0.2 the 12-month no-read share is 0.8¹² = **6.9%**. That is Ofgem's "just over 7%".
- So the 1/6 in `simulation/meter_reads.py` is too slow: (5/6)¹² = 11.2%. A 0.20–0.22 rate fits
  both published figures without any persistence.

**2. That bounds how many homes can be persistent non-reads.** A class making up a share π of
homes, read at monthly probability p_h ≈ 0.02 (about once in four years), leaves at least
π × 0.98¹⁴ unread at RF. RF leaves 3% unread, so **π ≤ 0.04**. The calibrated mixtures in the
harness push the 14-month unread share above Elexon's 3% as π grows (0.033 at π = 0; 0.040 at
π = 0.03; target 5.4%). That argues for the **low** end.

**3. A small persistent class must exist, but it is weakly evidenced.**
- Under pure independence at p = 0.2, only 5–7% of the gaps that pass 12 months reach 24 months.
- The complaint sample's **median** is 24 months. Complaints select for large bills, and size
  grows with length, so this does not prove persistence. But it is hard to get a 24-month median
  from a population where only 1 in 15 long gaps reaches 24 months.
- With π = 0.01, the share of 12-month gaps reaching 24 months rises to about 15%.

**4. The key result: persistence does not change how much revenue the 12-month rule bars.**
- For a geometric read process, the share of consumption older than 12 months when the catch-up
  bill lands is E[max(0, L−12)] / E[L] = (1−p)¹². That is exactly the 12-month no-read share.
- Any mixture calibrated to the published 12-month share therefore bars **the same share of
  consumption**, whatever π is. The harness prints it constant (0.054 or 0.07) across π from 0 to
  0.05.
- **Barred revenue = 12-month no-read share × the mean under-estimate on those reads.**
  Persistence reshapes only the distribution: "rare and large" against "common and small".
- The estimate error comes from `how_far_a_settled_eac_sits_from_next_years_use.md`: half of homes
  move by more than 14% year on year, and EACs show no systematic bias. So the mean positive part
  is about 0.10, with a range of 0.05–0.20 [derived, approximate].
- **Barred revenue ≈ 0.27%–1.4% of a traditional-meter household's revenue.**

### Toggles

- `q2_persistent_unread_share` (π)
  - **Meaning:** the share of read-exposed credit meters (traditional, or smart in traditional
    mode) in a hard-to-read state, with a monthly actual-read probability around 0.02. The rest
    are read memorylessly at the rate that reproduces the 12-month no-read share.
  - **Values:** default **0.01**; low 0.0; high 0.03.
  - **Basis:**
    - Low end: the Elexon curve fits a memoryless process.
    - High end: the Elexon RF bound (π ≤ 0.04), less a margin, because the RF fit worsens with π.
    - Default: enough to make a 24-month gap ordinary among complaint cases (derivation 3).
- `q2_easy_class_monthly_read_probability`
  - **Meaning:** not free. It is solved from π and the 12-month target, and the register names the
    solver.
  - **Values:** 0.20–0.25 across the box.
- `q2_no_read_12m_share`
  - **Meaning:** the published moment the read process is calibrated to.
  - **Values:** default **0.07** (H1 2017, all domestic); low 0.054 (the 2017 median supplier).
- `q2_mean_under_estimate_on_a_catch_up`
  - **Meaning:** the mean positive part of (actual − estimated) / estimated over an unread stretch.
  - **Values:** default **0.10**; low 0.05; high 0.20.
  - **Basis:** the year-on-year EAC spread (median |Δ| 14%, no systematic bias).

### Sensitivity

**Renewal pricing.** The deciding code exists. The harness charges the barred revenue as an extra
loss share on each stayer's bill:

| barred revenue added | paths whose decisions moved, knife-edge excluded (of 4) |
|---|---|
| low, 0.27% | 0 |
| default, 0.35% | 0 |
| high, 1.4% | 1. On `default`: hindsight level 45→50, and four ex-ante years +5 (30→35, 45→50 ×3). Neither sign flips. |
| stress, 5% (beyond the plausible box) | 4. Levels +5, and value_capped loses to the ex-ante flat level on 3 paths |

Only the **magnitude** toggle (the under-estimate) reaches the high end, and only through the
aggregate. **π cannot move this decision at all**, because the aggregate does not depend on it
(derivation 4). At the high end the renewal decision moves by one grid step on one of four paths.
That is the size of the probe's own path-to-path spread: the hindsight level is already 45 / 50 /
50 / 55 across the four reference paths. The high end also overstates the exposure, because it
applies to traditional-meter homes only, under half the book by 2024.

**Billing accuracy, complaints and read-chasing.** The deciding code does not exist: W2_36, D48,
W2_37. Acceptance criterion for W2_36:
1. Remove the forced 12-month read. Draw reads from the two-class process, with π read from the
   register and the easy-class rate solved to `q2_no_read_12m_share`.
2. The world must reproduce, within tolerance:
   - the 12-month no-read share;
   - Elexon's 30/60/80/97% at 2/4/7/14 months;
   - a positive count of catch-up bills covering 24+ months.
3. At π = 0, 0.01 and 0.03, D48 and W2_37 print:
   - the count and size distribution of catch-up bills;
   - the £ barred under 21BA (this must be invariant in π: that is the control on derivation 4);
   - complaint volume;
   - the value of a read-chasing rule targeted on the company's **observed** long gaps against an
     untargeted one. Targeting only pays if persistence exists, and the company can see
     persistence in its own read history.

The decision is the company's rule, learned from observables. It is not a world constant the
company needs told.

### Verdict

**Persistence: DOESN'T MATTER for the size of back-billing losses or for renewal pricing.** It is
proven invariant, and the harness shows it. **MATTERS AND RESOLVABLE for the shape:** the count and
size of back-bills, complaints, and the value of targeted read-chasing.
- It is bounded to π ∈ [0, 0.03] by Elexon's curve and Ofgem's 7%.
- It is resolved by W2_36's acceptance criterion. Read-chasing is learned by the company from its
  own read history.
- The next published read that would narrow it is Citizens Advice's per-supplier quarterly
  billing-accuracy data, published and not yet extracted. Supplier-level spread says how much
  non-reading is a supplier trait and how much a household trait.

**One correction to the code, from this work:** the world's 1/6 monthly read rate is too slow
against both published moments. It should be about 0.20–0.22. Not for the director.

---

## Q3. Debt: plan take-up and keep rates, recoveries after write-off

### Research

- **Take-up.** No published flow of offers and acceptances exists
  (`domestic_repayment_plan_take_up_and_keep_rates.md`). The nearest figures:
  - **Ofgem's own cost-neutral DRS scenario**, from E.ON Next's Winter Support Scheme, assumes
    **32% engagement and 20% changed payment behaviour** (DRS impact assessment, Nov 2025, fn 11;
    in `debt_and_collections.md` §4). [H, a supplier's own scheme, not a trial]
  - The stock ratio 2.9 / (2.9 + 4.0) = **42%** of over-91-day debtors on an arrangement (Ofgem
    debt indicators, Q2 2026). That is a stock, not a take-up rate, and the research page says why.
- **Keep.** Ofgem's 2015 social-obligations report, Fig. 13: **23%** of large-supplier credit
  plans had at least one failed payment in the year at under £3/wk, rising to **41%** at over
  £9/wk. [H, read off the chart]
- **Recoveries after write-off.**
  - Centrica Note 17: £3m (2025) and £10m (2024) recovered, against £135m and £160m written off.
    That is **2–6%** [derived; cohorts differ].
  - **Debt-sale price:** Lowell Group, *Year-end report 2013*, May 2004 – Sep 2013: 715
    portfolios, face value about £11.0bn, £597m invested, "**an average price paid of 5.4 pence per
    pound** sterling of the debt's face value". The same report names "utilities" as a new sector
    it bought from. [H, all sectors, not energy alone]
  - Still no energy-specific sale price.
  - The world's `DEBT_SALE_HAIRCUT_PCT = 0.12` is more than twice Lowell's all-sector average.
    `DCA_RECOVERY_RATE` 20–30% is four to fifteen times Centrica's post-write-off recovery.

### Derivation: a per-instalment keep rate from Ofgem's annual "at least one miss"

If misses were independent across instalments, P(≥1 miss in a year) = 1 − (1−q)ⁿ:

| annual share with a miss | per monthly instalment (n = 12) | per weekly instalment (n = 52) |
|---|---|---|
| 23% (under £3/wk) | q = 2.2% | q = 0.50% |
| 41% (over £9/wk) | q = 4.3% | q = 1.0% |

Persistence (a minority who miss repeatedly) would make the typical household's q **lower** than
this. These figures are an upper bound on the typical miss rate, and a lower bound on the typical
keep rate.

### Toggles

- `q3_plan_take_up_share`
  - **Meaning:** P(the household agrees an arrangement | the supplier offers one at the SLC 27
    ability-to-pay step).
  - **Values:** default **0.32**; low 0.20; high 0.42.
  - **Basis:**
    - Default: Ofgem's DRS assumption (32% engagement, E.ON Next).
    - Low end: the DRS's 20% "changed behaviour".
    - High end: the stock ratio, an upper reference, since a stock over-weights long plans.
- `q3_instalment_miss_probability_monthly`
  - **Meaning:** P(a single monthly instalment on an agreed plan fails, by the SOR's 10-working-day
    definition).
  - **Values:** default **0.03**; low 0.02; high 0.045.
  - **Basis:** the derivation above.
  - **Note:** the company's "default after 2 misses" is a separate company rule. It is not this
    toggle.
- `q3_post_write_off_recovery_share`
  - **Meaning:** £ recovered after write-off ÷ £ written off. This means recovery by any route:
    DCA net of commission, or sale proceeds.
  - **Values:** default **0.05**; low 0.02; high 0.10.
  - **Basis:**
    - Low and default: Centrica 2025 / 2024.
    - Default and high: Lowell's 5.4p average, and fresher debt sells for more.
  - **Note:** the world's 0.12 sale and 20–30% DCA constants sit above this range and carry no
    source.

### Sensitivity

**Renewal pricing.** The deciding code exists. The harness nets each row's true bad-debt share by
(1 − r):

| r | paths whose decisions moved, knife-edge excluded (of 4) |
|---|---|
| 0.02 | 0 |
| 0.05 | 0 |
| 0.255 (the world's own DCA constant) | 0 |
| 1.0 (stress: all bad debt recovered) | 0 |

Bad debt sits on only 8–10 of about 81 rows per path, so even removing it entirely moves no level.
**DOESN'T MATTER for renewal pricing.**

**Collections decisions.** None exist that these toggles could move:
- The plan offer is a licence duty (SLC 27.8), not a choice.
- `company/billing/collections_journey.py` is a fixed ladder whose plan answers are honestly
  `None`.
- DCA against sale is decided world-side by archetype (`simulation/arrears_engine.py`). It is not
  a company decision.

Acceptance criterion for EP4 / W2_38:
1. The world reads take-up, miss probability and post-write-off recovery from the register.
2. The world's arrears stock is graded against Ofgem's quarterly debt indicators: the
   repaying-to-arrears ratio, about 42% of over-91-day debtors on an arrangement, and its 2019–2026
   path. This **jointly** pins take-up × keep, which is how the pair is resolved.
3. EP4's debt cashflow forecast and any **company** DCA-vs-sell or plan-term decision it builds are
   printed at the low and high ends of each toggle.
4. A decision that moves comes back here with the evidence.

### Verdict

**DOESN'T MATTER for any decision that exists today** (tested on renewal pricing; no collections
decision exists). **MATTERS AND RESOLVABLE for the debt forecast:** take-up × keep is pinned
jointly by W2_38's grading against Ofgem's published stock series. Recovery after write-off is
bounded at 2–10% by Centrica and Lowell. Not for the director.

**A code finding that needs no ruling:** the world's DCA and sale constants are above every
published signal. Each should read `q3_post_write_off_recovery_share` instead.

---

## Q4. Offers: do GB suppliers run holdouts, and how is PECR's "similar products" read?

### Research

**Holdouts.** GB suppliers have run **randomised control groups on exactly these communications,
with the regulator** (Ofgem, *Insights from Ofgem's consumer engagement trials*, Sept 2019, in
`next_best_action_and_cross_sell.md` §3.1). [H]
- The Cheaper Market Offers Letter ran at two suppliers, against a 1.0% control.
- The End of Fixed-Term prompt ran with about 20,000 customers at one supplier: 19% control against
  28% treated.
- The collective switch ran at one large supplier.

What is not published is whether suppliers hold out a group from their **own** retention offers
routinely. There are vendor claims only (§3.5 of that page). The BAT market-wide derogation
*permits* retention-only tariffs at fixed-term end; it does not require them (Ofgem, 13 Nov 2025,
§3). So holding a random group back from an optional offer does not deny anyone a right. The
licence renewal notice (SLC 22C/31I) must still reach everyone.

**PECR "similar products".** ICO, *How do we comply with the PECR electronic mail marketing
rules?* [H, read 2026-10-05]:
- "The key question is whether, based on previous interactions, people **reasonably expect** direct
  marketing about your product or service."
- The soft opt-in "only covers **your own** similar products and services. You must not use it to
  send messages about other organisations or their products."
- The worked example: a supermarket customer may expect emails about groceries and "other products
  commonly sold in supermarkets", but is "unlikely to expect emails about banking or insurance
  products because they are not bought and sold in a similar context", and those are often not
  "the same organisation".

Applied to an energy supplier, by the ICO's own test:
- **Inside:** its tariffs, including EV, ToU and export tariffs. They are its own product, sold
  in the same context.
- **Outside, or at best contested:** boiler cover (usually insurance, often written by a different
  legal entity), broadband and insurance, which are the supermarket's "banking or insurance" case.
- **Separately, and regardless of PECR:** marketing that uses consumption data needs SLC 47
  consent (`next_best_action_and_cross_sell.md` §4.5).

### Derivation: the binding constraint is book size, not holdout share

The standard error of a measured uplift is √(p(1−p)(1/n_t + 1/n_h)), at a base churn of 0.30.

| renewal decisions | h = 5% | 10% | 20% | 50% |
|---|---|---|---|---|
| 80 (this simulation's whole probed book) | 23.5 pp | 17.1 | 12.8 | 10.3 |
| 500 | 9.4 | 6.8 | 5.1 | 4.1 |
| 5,000 | 3.0 | 2.2 | 1.6 | 1.3 |
| 50,000 | 0.9 | 0.7 | 0.5 | 0.4 |

The effects to detect are the Ofgem EFTC prompt (+9 pp, any switching) and Ascarza et al. (2016)
(+4 pp churn, a sleeping dog). At the current book **no holdout share can measure either**. Even
at 50% held out, the error is larger than the largest published effect. From about 5,000
decisions a year, a 10–20% holdout separates +9 pp from zero, and +4 pp only marginally.

### Toggles

- `q4_retention_holdout_share`
  - **Meaning:** the share of retention-eligible customers randomly held back from an optional
    retention offer.
  - **Values:** default **None**. This is deliberate: it is a **derived design parameter**, not a
    world fact. C34/B8 must compute it from the power formula above at the book's real decision
    count and the smallest effect worth detecting.
  - **Range:** 0.05–0.50.
  - **Basis:** the table above.
- `q4_pecr_soft_opt_in_scope`
  - **Meaning:** which cross-sell products may be emailed or texted to an existing customer without
    fresh consent.
  - **Values:** default **`own_energy_tariffs_and_energy_services`**; low `own_energy_tariffs_only`;
    high `own_energy_and_home_services_same_entity`.
  - **Basis:** the ICO "reasonably expect" test and the supermarket example. The high end is
    contested and requires the same legal entity. It never reaches third-party insurance or
    broadband.

### Sensitivity

- **Holdouts.** No deciding code exists (C34 and B8 are unbuilt). Whether other suppliers run
  holdouts changes nothing we would do: a holdout is the only way to estimate uplift (§2 of the NBA
  page), and the regulator's own trials show it is lawful and done. The *share* is set by power at
  the book's size, which the table shows is the binding constraint.

  Acceptance criterion for C34 / B8:
  1. Log a randomised holdout on **whether** to offer.
  2. Compute the share from `uplift_se`, at the run's real decision count, for the smallest effect
     the decision cares about.
  3. Report "uplift not measurable at this book size" (fail closed) when the standard error exceeds
     that effect.
  4. Grade the company's uplift estimate against `tools/decision_probe.py`'s true counterfactual.
- **PECR scope.** No deciding code exists (no consent state; `ancillary_products.py` has no
  callers). The scope only changes the reachable population of the **last-ranked** lever (non-energy
  cross-sell, §8 of the NBA page). The first-ranked lever, EV/ToU tariff upsell, is inside the soft
  opt-in at every setting.

  Acceptance criterion for C34: a consent state per customer, reading the scope from the register.
  The NBA's ranking is printed at the low and high scope; a change in the **top** action for any
  customer comes back here.

### Verdict

- **Holdouts: RESOLVED.** Randomised control groups on supplier retention-type communications are
  established GB practice with the regulator (Ofgem 2019). Whether rivals do it routinely does not
  change our decision. The share is derived by power, and the binding constraint is book size
  (≈80 decisions here). That is a finding for C34/B8 and the director's curriculum, not a question.
- **PECR "similar products": RESOLVED to the ICO's test.** Own energy tariffs and services are
  inside. Insurance-type cover and broadband are outside unless consented. **DOESN'T MATTER** for
  the current NBA order. Not for the director.

---

## Q5. Carbon: can a supplier tell a gas meter removal from a switch away?

### Research

**Yes. The two arrive by different industry routes, and the supplier commissions one of them
itself.**

- **A meter removal is a job the registered supplier orders.**
  - Cadent: "You need to discuss your disconnection plans with your **existing supplier and
    arrange for your gas meter to be removed**". The network's service-pipe disconnection is a
    separate, chargeable job (*Gas Disconnections*, cadentgas.com). [H]
  - The supplier's meter asset manager does the work and reports the physical change to Xoserve
    through the **RGMA** flows (`ONJOB` / `ONUPD`). The supply meter point's status moves to **DE /
    EX** (dead, extinct). [H for the codes]
  - CSS then shows the registrable measurement point as **Terminated**: "no longer capable of
    off-taking gas i.e. the Meter Point Status is DE or EX". It can only be de-registered (Xoserve,
    *CSS SPA FAQs*, Q on RMP status). [H]
  - The supplier "needs to de-activate their registration through the new CSS process" (same FAQ,
    Q23). [H]
- **An isolation without removal** (the meter capped and left in place) sets the isolation flag,
  and the RMP status is **Dormant** (same FAQ). [H] This is the ambiguous case: a void, a
  demolition pending, or a heat pump with the meter left in.
- **A switch away arrives as a CSS loss** on an RMP that stays **Operational**. The gaining
  supplier's registration supersedes ours (CSS registration process; see `home_moves.md` §3 for the
  CSS data items). [M for the message name]
- **What the supplier cannot see:** a household that switched its gas away and *later* had the
  meter removed by the new supplier. To us that is a switch.

### Sensitivity

The deciding code exists: `company/carbon/half_hourly_footprint.py`, published through
`tools/generate_explore_carbon.py`. The harness gives the same 2023 household (3,000 kWh of
electricity, 11,500 kWh of gas) a gas account closed in June 2023 by two different causes:

| cause | change in the footprint | `net_fall` |
|---|---|---|
| switched gas to another supplier; electricity unchanged | **−2,173 kg** | True |
| meter removed for a heat pump; +3,300 kWh electricity | **−1,738 kg** | True |

**The page reports the household that only changed supplier as cutting more carbon than the one
that installed a heat pump.** In truth the switcher's emissions did not fall at all. `gas_leg`'s
reason string honestly says the record "does not say whether the gas was disconnected or moved".
But the *record does say*: the supplier's own RGMA job and RMP status distinguish the cases. The
change figure and `net_fall` are published regardless.

There is no toggle. This is not an unknown, it is an unread observable.

Acceptance criterion for the carbon atom (and a code finding to file):
1. `gas_leg` takes a **closure cause** from the company's own registration events:
   - `meter_removed`: own removal job, RMP Terminated;
   - `isolated`: RMP Dormant;
   - `lost_on_switch`: a CSS loss on an Operational RMP.
2. `household_change` **refuses** a `net_fall` (or reports the gas leg as "not ours since") when
   the cause is `lost_on_switch` or `isolated`.
3. A control asserts that the switch case can no longer read as a fall.

This needs world-side support: the world must emit removal and switch as distinct observables.
Today a closure is only `closed_on`.

### Verdict

**RESOLVED.** A supplier can tell its own meter removal (RGMA job, SMP DE/EX, RMP Terminated, its
own CSS deactivation) from a switch away (a CSS loss on an Operational RMP). Capped-in-place
isolation (RMP Dormant) stays ambiguous. **It matters**, because the published footprint today
turns a switch into the largest carbon saving on the page. **It is resolvable without the
director**, through the acceptance criterion above.

---

## All toggles

| id | question | default | low | high | feeds | sensitivity | verdict |
|---|---|---|---|---|---|---|---|
| `q1_move_out_notice_share` | Q1 | 0.7 | 0.5 | 0.9 | B7, W2_38 | acceptance criterion (B7) | MATTERS AND RESOLVABLE |
| `q1_unnamed_months_per_cot` | Q1 | 3 | 1 | 6 | B7, W2_38, EP4, B11 | acceptance criterion (B7 £/move band) | MATTERS AND RESOLVABLE |
| `q1_move_hazard_multiplier` | Q1 | 1.0 (EHS 2024-25 by tenure) | 0.5 | 2.0 | B7, B11 | tested: renewal pricing unchanged at 0.5 and 1; one step on one path at 2 | DOESN'T MATTER (pricing) |
| `q2_persistent_unread_share` | Q2 | 0.01 | 0.0 | 0.03 | W2_36, D48, W2_37 | tested: barred £ invariant in π (proved); acceptance criterion for shape | DOESN'T MATTER (aggregate) / MATTERS AND RESOLVABLE (shape) |
| `q2_no_read_12m_share` | Q2 | 0.07 | 0.054 | 0.07 | W2_36, D48 | calibration target (published) | RESOLVED |
| `q2_mean_under_estimate_on_a_catch_up` | Q2 | 0.10 | 0.05 | 0.20 | W2_36, D48, B11 | tested: pricing unchanged at low and default; one step on one path at high | DOESN'T MATTER (pricing) |
| `q3_plan_take_up_share` | Q3 | 0.32 | 0.20 | 0.42 | EP4, W2_38, B11 | acceptance criterion (W2_38 grading) | MATTERS AND RESOLVABLE |
| `q3_instalment_miss_probability_monthly` | Q3 | 0.03 | 0.02 | 0.045 | EP4, W2_38 | acceptance criterion (W2_38 grading) | MATTERS AND RESOLVABLE |
| `q3_post_write_off_recovery_share` | Q3 | 0.05 | 0.02 | 0.10 | EP4, W2_38, B11 | tested: pricing unchanged even at r = 1 | DOESN'T MATTER (pricing) |
| `q4_retention_holdout_share` | Q4 | None (derived by power) | 0.05 | 0.50 | C34, B8, W2_39 | acceptance criterion (power at book size) | RESOLVED (design parameter) |
| `q4_pecr_soft_opt_in_scope` | Q4 | own energy tariffs and services | own tariffs only | own energy and home services, same entity | C34 | acceptance criterion (top action invariant) | DOESN'T MATTER (current NBA order) |

Q5 has no toggle. It is RESOLVED, and its code defect is in the Q5 section.

## Escalate to the director

**None.** No question is both decision-changing and unresolvable:
- Q1's latency and Q3's take-up and keep are pinned by derivation, or by grading against published
  series inside the atoms that use them.
- Q2's persistence is invariant where it would have mattered most.
- Q4 and Q5 are resolved by published guidance and industry flows.

**Two findings for the seat, neither a question:**
1. The carbon footprint publishes a supplier switch as a carbon saving (Q5).
2. The simulated book (~80 renewal decisions) is too small for any holdout to measure retention
   uplift (Q4). This bears on C34/B8 and on the curriculum question of a larger book, which is
   already the director's (`EP17_varied_population_draw`).

## Sources read this pass

- Ofgem, *Tackling Energy Debt in the Supplier Home-Move Process — Call for Input: Summary of
  Responses*, OFG1164, June 2026,
  https://www.ofgem.gov.uk/sites/default/files/2026-06/Home-Moves-CFI-Summary-of-Responses.pdf
  (¶2.1–2.4).
- Ofgem, non-confidential responses to the same CfI,
  https://www.ofgem.gov.uk/sites/default/files/2026-06/COT-CFI-non-confidential-responses.zip:
  - Energy UK (Q1 answer: £740m CoT and £1.17bn closed-account debt, five largest suppliers);
  - So Energy;
  - EN25-01 (the landlord and letting-agent sequence);
  - RECCo;
  - Money Advice Trust;
  - EFPC.
- Ofgem, *Protecting consumers who receive backbills — statutory consultation*, 16 Nov 2017,
  https://www.ofgem.gov.uk/sites/default/files/docs/2017/11/protecting_consumers_who_receive_backbills_-_statutory_consultation.pdf
  (¶1.1, ¶2.1, fn 16, fn 33).
- Citizens Advice, *Millions of energy customers hit by back-bills*, press release, 29 Feb 2016,
  https://www.citizensadvice.org.uk/about-us/about-us1/media/press-releases/millions-of-energy-customers-hit-by-back-bills/
- Lowell Group, *2013 annual financial results*,
  https://www.lowell.com/hubfs/lowell-group-2013-annual-financial-results.pdf
- ICO, *How do we comply with the PECR electronic mail marketing rules?*,
  https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guidance-on-direct-marketing-using-electronic-mail/how-do-we-comply-with-the-pecr-electronic-mail-marketing-rules/
- Xoserve, *Central Switching Service (CSS) Supply Point Administration (SPA) FAQs*,
  https://www.xoserve.com/media/43581/css-spa-faqs-final.pdf (RMP status; Q23–25).
- Cadent, *Gas Disconnections*,
  https://cadentgas.com/services/household-customer/disconnections
- Carried from the area pages, not re-read:
  - Elexon *Settlement Timetable* (2014);
  - Ofgem 2015 social-obligations report, Fig. 13;
  - DRS impact assessment (Nov 2025);
  - Centrica ARA 2025, Note 17;
  - EHS 2024-25;
  - Ofgem consumer-engagement trials (2019);
  - Ascarza et al. (2016).

*Not re-read and marked [M]:* the big-five market share (~78%), GB household count (~27.8m), the Oct–Dec
2024 cap level (~£1,717), and the CSS switch-loss message name.
