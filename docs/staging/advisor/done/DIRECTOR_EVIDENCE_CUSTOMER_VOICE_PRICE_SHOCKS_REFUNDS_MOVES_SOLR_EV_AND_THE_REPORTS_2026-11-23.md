**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-EVIDENCE] Customer voice: price shocks, refunds, home moves, supplier failures, EV tariffs, and the reports behind gaps V1, V2, V3 and V6

**Type:** EVIDENCE, through the advisor channel. These are three research passes the advisor ran on Mon 23 Nov. They answer §6 of `docs/market_research/customer_voice_theme_map_gb_energy_2026-11-21.md` ("the advisor's offered pass after the 23 Nov reset").

The director's words that set it:
- Sat 21 Nov 07:20 GMT: "I'd imagine this can be researched and this should be a key part of the knowledge base. I'd have thought that customer review sites are full oft his kind reaction"
- 07:23 GMT: "Shouldn't these be trawled for other themes and insights ?"
- 07:24 GMT, to the advisor's offer to run the first sweep: "Yes"

## How to use it

**This is secondary evidence, gathered by advisor sub-agents through WebFetch summaries.**
- Verify each figure against its primary source before it feeds the world, the supplier or the site. That is the data standard, and the 22 Nov curiosity steer's "second view".
- The coded accounts are self-selected. They show which responses exist and how they chain, not how often. Rates come only from the P-graded representative sources.
- Accounts are paraphrased, with no names (W11).

**Trustpilot was not read** in any pass. Its terms forbid automated access, and the forum threads fitted better.

**The advisor's own reading:**
1. **Pack C corrects two lines in the theme map's §1.2.** The "22% told it could not be resolved or passed on" is an inference, and "smart meter problems are the most common complaint" is not stated by Ofgem. Fix those first.
2. **Pack A's end-of-fix accounts show defaulting as a rational choice in 2021-22, when fixes were priced above the cap.** The "inert default" assumption fails in that period, and the world's end-of-fix behaviour must allow it.
3. **Pack B's home-move accounts answer V4: the move itself seeds the problem.** Ofgem's figure that unnamed (change of tenancy) accounts hold **20-40% of domestic debt** makes this a first-order world item, not an edge case.
4. **Across all three packs, every recovery in full came only after outside pressure,** such as an MP, the Ombudsman, a bank reversal or a court threat. That supports "how the issue is handled then affects" outcomes. Customer Service is 33-50% of front-line complaints at four large suppliers, but 7-14% of Ombudsman disputes. Front-line and escalated populations differ, and the world should not treat them as one.

---

## Pack A: price shocks and end of fix; final bills and credit refunds

# Price-shock and final-bill/refund accounts, coded for the customer-voice theme map

I coded 27 accounts: 12 price-shock (P1–P12) and 15 final-bill/refund (R1–R15). Every forum, MSE-news and review-style account is self-selected, so these show which responses exist and how they chain, not how often.

- **Not read:** I did not fetch Trustpilot, because the terms forbid automated access and I spent the budget on forum threads. No Citizens Advice case box on price shock was reached either.
- **Not paraphrased:** none. Quotes are under 10 words. Names and usernames are dropped.
- **Moment** is coded as `ann` (announcement), `eff` (effective date) or `dd` (when the direct debit changed). `EoF` marks end of fixed term.

## (a) Coded accounts

All rows below are self-selected unless marked "(P-source)".

### Theme 1: price shocks and end of fix

| id | theme / trigger | pay / meter | circumstance | first response > chain | supplier handling | outcome | time / effort | tone | source and date |
|---|---|---|---|---|---|---|---|---|---|
| P1 | price_rise_svt / dd (price cap +54% Apr 2022, DD set by supplier email, moment=dd) | DD, credit | Shell Energy; paid £227 a month, notified of about £486, lowest self-serve option £340 | read email > logged in > phoned > negotiated | `dd_negotiable_by_phone` (agent agreed £250) | DD reset to about 10% above old level, stayed | one call | angry then satisfied | [MSE forum, 11 May 2022](https://forums.moneysavingexpert.com/discussion/6356605/mse-news-30-of-british-gas-octopus-shell-energy-customers-say-their-direct-debits-have-doubled) |
| P2 | price_rise_svt / ann+eff (cap rise, annual cost about £3,000 against published cap figures) | not stated | Scottish Power | cannot reconcile bill > asks forum how to find unit rate and standing charge | none stated | unresolved | not stated | confused, self-doubting | same thread, 11 May 2022 |
| P3 | price_rise_svt / standing_charge (standing charge nearly doubled, moment=eff) | not stated | supplier not named | asks forum why > told about SoLR costs, inflation and storm damage | none | unresolved, explanation only | not stated | curious | same thread, 11 May 2022 |
| P4 | end_of_fix / renewal_offer_above_SVT (Jan 2022) | not stated | Scottish Power, fix ends end of Jan 2022, renewal offered above SVT | asks forum > advised "do nothing and sit on SVT" > chose to wait | `renewal_offer_priced_above_default` (SVT cheaper in Dec 2021) | rolled onto SVT by choice | days | uncertain then resigned | [MSE forum, 1 and 29 Dec 2021](https://forums.moneysavingexpert.com/discussion/6316731/scottish-power-end-of-fixed-term-energy-tariff) |
| P5 | end_of_fix / retention_fix_taken (Mar 2022) | not stated | same thread, a Scottish Power-style offer: about £68 a month to £98, exit fee £30 | took the retention fix on a low-risk judgement | retention fix offered | fixed for 13 months, then judged "right" because prices rose | minutes | triumphant (hindsight) | same thread, 11 Mar 2022 |
| P6 | end_of_fix / renewal_vs_SVT (Jan 2022) | not stated | Scottish Gas, fix ends 31 Jan 2022; renewal quote £920 to £2,119 a year, SVT £1,337 | asks forum > told to do nothing and watch the April cap | none | rolled onto SVT (advice) | same day | worried, "a bit lost" | [MSE forum, 5 Jan 2022](https://forums.moneysavingexpert.com/discussion/6324249/help-energy-crisis-bill-query) |
| P7 | end_of_fix / renewal_dearer_than_SVT (Mar 2022) | DD | British Gas; cheapest fix £1,005 a year, SVR £771; auto-rollover to SVR if no choice by 9 May 2022 | asks forum if SVR is the right call > advice "stick with SVR" | fix priced above default | not reported | not stated | puzzled | [MSE forum, 21 Mar 2022](https://forums.moneysavingexpert.com/discussion/6344234/british-gas-svr-cheaper-than-fix) |
| P8 | end_of_fix / retention_fix_forced (Jan 2022) | not stated | British Gas Evolve, electricity only; £23 to £47 a month | accepted a fix to 2024 because no better deal was visible | `retention_fix_taken_with_no_alternative` | locked in at double the monthly cost | one thread | resigned, "expected rise, not this" | [MSE forum, 12 Jan 2022](https://forums.moneysavingexpert.com/discussion/6326169/electric-bill-will-be-double) |
| P9 | end_of_fix / dark_pattern_UX (Aug 2022) | not stated | Shell Energy; renewal flow only offered "switch now", forfeiting 3–4 weeks of the cheaper tariff | stopped at the web step > will wait until the last week | `UX_forces_immediate_switch` | delayed; a reply says SVT applies automatically anyway | not stated | suspicious | [MSE forum, 5 Aug 2022](https://forums.moneysavingexpert.com/discussion/6377145/shell-energy-beware-easy-to-switch-to-more-expensive-variable-before-fixed-term-ends) |
| P10 | price_rise_svt / ann (npower, Feb 2017; unit rate +5%, new standing charge about £60 a year) | not stated | npower; poster says own bill rose about 80% | read press release > recalculated > posted | headline "15% average" hid the standing-charge effect (poster's claim) | none reported | one post | angry | [MSE forum, 19 Feb 2017](https://forums.moneysavingexpert.com/discussion/5596973/npower-average-10-price-rise-march-16th/p4) |
| P11 | price_rise_svt / ann (npower, Feb 2017) | not stated | one-bedroom bungalow, poster's mother; about +33% with the standing charge | calculates the rise > questions fairness | none | none reported | one post | upset | same thread, 15 Feb 2017 |
| P12 | price_rise_svt / ann (npower, Feb 2017) | not stated | poster's father, long-standing customer, about £20 a month overpaying | stays; a sibling had a bad switch years ago | none | stayed (inertia plus switching memory) | none | resigned | same thread, 19 Feb 2017 |

P-codes by theme: P1–P3 and P10–P12 are price-rise announcements or direct-debit moments; P4–P9 are end-of-fix. P5 (took the retention fix and it paid off) and P9 (suspected obstruction) are the two chains where handling shaped the choice.

### Theme 2: final bills and credit refunds

| id | theme / trigger | pay / meter | circumstance | first response > chain | supplier handling | outcome | time / effort | tone | source and date |
|---|---|---|---|---|---|---|---|---|---|
| R1 | final_bill_refund / credit_withheld (2018) | not stated | Economy Energy; £362 credit | chased > over 10 weeks > wrote to bosses > contacted MP | `internal_process_change_blamed`; apologies without a date | got the refund only after MP and executive contact (`escalated_won`) | over 10 weeks | angry | [MSE news, 7 Jan 2019](https://www.moneysavingexpert.com/news/2019/01/economy-energy-customers-furious-over-credit-refund-delays-/) |
| R2 | same / credit_withheld (Oct 2018 switch, £141.80 credit) | not stated | Economy Energy | called early Nov > got final bills > told "within 10 days" > still unpaid on 3 Jan | `promise_repeated_not_kept` | unresolved at publication (Ofgem later ordered 28-day payment of refunds) | about 11 weeks | frustrated | same article |
| R3 | same / credit_withheld_DD_kept_collecting (Aug 2018) | DD | Together Energy; final statement £509 credit | switched to Avro > supplier kept taking DD > bank reversed DDs > complained > Ombudsman | `promised_28_days_missed` | refund plus £84 goodwill after Ombudsman | months | irritated | [Which?, Apr 2019](https://www.which.co.uk/news/2019/04/energy-switching-complaints-on-the-rise/) (P-source) |
| R4 | same / credit_then_disputed_reads (GB Energy, Sep 2017) | not stated | £183 credit falling to £59 after new readings | asked if refundable > told refund follows verified reads | `final_bill_waits_for_new_supplier_read` | pending | not stated | frustrated | [MSE forum, 14 Sep 2017](https://forums.moneysavingexpert.com/discussion/5706835/how-to-get-your-credit-back-from-gb-energy/p2) |
| R5 | same / late_final_bill (GB Energy, Jul–Oct 2017) | not stated | left 31 Jul; no bill at 8 and 10 weeks | sent meter photo > asked new supplier > told "disputed read" | `disputed_reads_process_cited` | waiting | 10 weeks and counting | sceptical | same thread, 19 Sep and 5 Oct 2017 |
| R6 | same / DD_stopped_then_bailiff_letters (GB Energy) | DD | left 10 Aug 2017; two bailiff-threat letters, no bill at 3 months | paid by card > got apology | `erroneous_demand_then_apology` | no final bill at 3 months | over 3 months | calm, bemused | same thread, 21 Nov 2017 |
| R7 | same / credit_withheld, persistence won (GB Energy) | not stated | about 3 months | matched closing read to new supplier's opening read | read supplied by customer unlocks the bill (`self_evidence`) | credit returned | 3 months | resigned, satisfied | same thread, 21 Nov 2017 |
| R8 | same / mass_backlog (Utility Point, Oct 2020–Jan 2021) | not stated | £308–£524 credits | repeated emails > MSE and social media | `staff_sickness_and_auto_switch_surge_blamed` | not reported; several still waiting after months | 3+ months | angry | [MSE news, 15 Jan 2021](https://www.moneysavingexpert.com/news/2021/01/former-utility-point-customers-struggling-to-get-credit-refunds-/) (6 accounts) |
| R9 | same / refund_after_move (Bristol Energy, 2021) | not stated | credit unpaid about 4 months | emailed > phoned > agent said "answering service" | `no_one_could_help` | unresolved; replies advise formal complaint, £30 GSOP, Ombudsman at 8 weeks | 4 months | suspicious | [MSE forum, 2 Jun 2021](https://forums.moneysavingexpert.com/discussion/6272245/credit-balances) |
| R10 | same / waiting_period_query (2020) | not stated | emailed at 2 weeks, was told up to 6 weeks | asked forum | none | none reported; replies cite the 6-week bill plus 2-week refund and £30 | 2+ weeks | anxious | [MSE forum, 23 Nov 2020](https://forums.moneysavingexpert.com/discussion/6218156/how-long-to-get-refund) |
| R11 | same / late_final_bill_after_Big_Switch (2014–15) | not stated | EDF to E.ON, credit about £800 | emailed new supplier > final bill appeared overnight, estimated | `estimate_despite_customer_reads` | final bill appeared; credit status not stated | about 2 months | suspicious | [MSE forum, 13 Jan 2015](https://forums.moneysavingexpert.com/discussion/5152146/edf-failure-to-produce-final-bill) |
| R12 | same / final_reading_not_exchanged (Octopus, year not shown on the page; probably 2024) | not stated | old supplier says it did not get the final read from the new one | daily emails to both > asked about Ombudsman | `blamed_third_party` (reading exchange); one reply says a 5-week refund is normal, another got a bill within 10 days after sending a photo | unresolved in thread | about 2 weeks and counting | worried | [MSE forum, "Energy refund heartache", 10 Sep](https://forums.moneysavingexpert.com/discussion/6682790/energy-refund-heartache) |
| R13 | same / credit_after_home_move (British Gas, Oct 2024) | not stated | left flat Oct 2024; about £1,700 credit | complained > Ombudsman ruled for her Feb 2025 > supplier did not carry out ruling > prepared small claims | `ignored_ombudsman_ruling` | paid in full about 15 months after move, days before a hearing | about 15 months | critical | [BBC via AOL](https://www.aol.com/news/british-gas-took-15-months-013521352.html) (press, one case) |
| R14 | same / deposit_plus_credit_after_switch (OVO, Aug 2024) | DD | security deposit plus credit; DD still taken after leaving | contacted repeatedly > took legal advice > asked about Ombudsman | `refund_date_moved_repeatedly`; OVO moderator says a live DD is needed for refunds | final bill pending, included standing charges after leaving | months | distrustful | [OVO forum, 13 Aug 2024](https://forum.ovoenergy.com/my-account-140/ovo-not-refunding-my-credit-and-still-taking-direct-debit-though-i-left-18153) |
| R15 | same / prepay_final_bill_dispute (OVO, SSE to OVO, Feb 2024) | prepay gas | final statement claimed about £1,000 owed, £614 in one month | repeated chat and calls > emailed CEO complaints team > paid the debt before switching | `refused_to_log_complaint_as_debt`; later agent called the figure "unusual" | complaint opened, no resolution by late Feb | months | at "breaking point" | [OVO forum, 14 Feb 2024](https://forum.ovoenergy.com/my-pay-as-you-go-account-159/pay-as-you-go-final-bill-claiming-i-owe-1000-and-ovo-refuse-to-let-me-complain-17234/index2.html) |

Three further reads from the same OVO thread (prepay debts inherited or passed to collections) are not coded separately.

## (b) Representative rates

| Rate | Value | Source | Grade |
|---|---|---|---|
| MSE survey, Apr–May 2022: in-credit price-capped customers whose DD at least doubled | 25% (median rise 66% against 54% cap rise); 4,177 in the analysed sample from 41,000+ responses; self-selecting | [MSE news, May 2022](https://www.moneysavingexpert.com/news/2022/05/energy-direct-debit-hikes-mse-survey) | S |
| Same survey: share of those doubled who had not challenged the rise | 46% | same | S |
| Same survey: share doubled after fix ended and moved to cap | 38% (median +87%); after fix ended and fixed again, 46% (+96%) | same | S |
| Same survey: share doubled by supplier | 33% British Gas to 15% OVO and SSE | same | S |
| Ofgem 2016 survey: of those who recalled an end-of-fixed-term notice, read in detail / looked at tariffs with same supplier / looked at switching supplier | 51% / 32% / 25% (bills: 40% / 11% / 10%) | [Ofgem 2017 default-tariff decision](https://www.ofgem.gov.uk/system/files/docs/2017/08/default_tariffs_for_domestic_customers_at_the_end_of_fixed-term_contracts.pdf), citing TNS BMRB 2016 | P |
| Ofgem 2019 end-of-fix notice trial (6 weeks, n about 19,553): any switching | 19% control, 28% treated; external switching 6% in both arms; the gain was internal | [Ofgem trial report](https://www.ofgem.gov.uk/system/files/docs/2019/09/end_of_fixed_term_communication_trial_report.pdf) | P |
| Default share, April 2019 (non-prepay) | 53% of electricity and 51% of gas accounts on default tariffs; about 46% of customers on fixed terms | same | P |
| Before Aug 2021: about 40% fixed, 60% not; 25% on a default over 3 years | stable 2019 to price shock | [Ofgem 2022 competition review](https://www.ofgem.gov.uk/sites/default/files/2022-08/Outcome%20of%202022%20review%20into%20whether%20conditions%20are%20in%20place%20for%20effective%20competition%20in%20domestic%20supply%20contracts1659537006802%20%281%29.pdf) | P |
| Switching during the 2021–22 crisis | "fell by over 80%"; 25% searched for a tariff in 8 months after Aug 2021 without switching; meter reads on 31 Mar–1 Apr 2022 reached 5.7m, double the previous year | same | P |
| 2016 switching, with SVT rises announced | 7.7m switches in 2016, +28%; rolling switching rate about 15.8% (electricity), 15.9% (gas). Ofgem links this to announced SVT rises but not as a stated cause | [Ofgem, 27 Feb 2017](https://www.ofgem.gov.uk/press-release/switches-nearly-30-millions-go-energy-shopping) | P |
| Big Six after 2017 rises | record 163,000 lost in one month (September, year not printed; British Gas +12.5% electricity from 15 Sep, so likely 2017); about 1.1m left the Big Six year to date, +18% | [Yahoo Finance](https://uk.finance.yahoo.com/news/big-six-energy-firms-lose-141148926.html), citing Jefferies | S |
| Ombudsman switching complaints 2018 | 3,352; over half were billing, refund or credit-balance problems | [Which?, Apr 2019](https://www.which.co.uk/news/2019/04/energy-switching-complaints-on-the-rise/) | P |
| Final-bill timing rules | final bill within 6 weeks; refund within 10 working days of the final bill; £30 if missed, plus £30 if that is paid late; phased in from May 2019 (refund) and May 2020 (final bill) | [MSE news, Jan 2021](https://www.moneysavingexpert.com/news/2021/01/former-utility-point-customers-struggling-to-get-credit-refunds-/); [Ofgem E.ON Next decision](https://ofgem.gov.uk/decision/eon-next-pay-total-ps145m-former-prepayment-meter-customers-due-failure-issue-final-bills) | P |
| E.ON Next late prepay final bills, Feb 2021–Sep 2023 | 248,000+ accounts, about 100,000 in credit, average £51; £14.5m paid (£4.7m credit, £6.6m GSOP, £3.2m redress) | same Ofgem decision, 20 Nov 2024 | P |
| Ofgem note on credit balances, end Dec 2023 | £8.1bn gross; £3.76bn policy measure; £357m on closed accounts; no timeframe for closed-account refunds beyond "timely" | [Ofgem explanatory note](https://www.ofgem.gov.uk/sites/default/files/2024-03/Customer%20credit%20balance%20explanatory%20note.pdf) | P |
| Recent engagement, Oct 2023–Mar 2024 (n=3,235) | compared or switched in last 6 months 62%; same-supplier tariff switch 13%; active supplier switch 6%; passive 4% | [Ofgem tariff-choices research](https://www.ofgem.gov.uk/sites/default/files/2025-07/understanding-consumers-energy-tariff-choices-%20research-report-2024.pdf) | P |
| MSE Feb 2023 note on E.ON fixed-deal rollover | fix £1,971 a year; SVT £2,500 (+27%, about £529); April rise to £3,000 expected | [MSE news, 14 Feb 2023](https://www.moneysavingexpert.com/news/2023/02/switched-to-the-e-on-one-year-fixed-deal-last-february--it-s-end/) | S |

**Corrections to existing notes.** The Ofgem 2016 notice survey is from 2016, so it is outside any 2016–2025 "post-announcement" window only on its edge. No supplier-level end-of-fix rollover rate was found in any of these documents, though one [Ofgem trial report](https://www.ofgem.gov.uk/system/files/docs/2019/09/end_of_fixed_term_communication_trial_report.pdf) states 53% and 51% defaults in aggregate.

## (c) Recurring chains

1. **Price cap announcement > DD jump > phone > negotiated down (P1).** Only one account negotiated the DD down, but the MSE survey says 46% of those who doubled did not challenge. So where the self-serve route offers no low option, the unchallenged DD becomes the cash-flow shock.
2. **End of fix, renewal priced above SVT > "do nothing" > rolled onto default (P4, P6, P7).** Forum advice, not a supplier nudge, drove the default roll in 2021–22. This runs the opposite way to pre-2021 default behaviour and shows default as a rational choice in a cap-below-fix market.
3. **End of fix, retention fix taken and it paid off (P5) or was forced by lack of alternatives (P8).** Taking the retention offer held the customer; hindsight turned P5 into praise, P8 into resentment.
4. **Obstructive renewal UX > suspicion > delay (P9).** A "switch now" only flow cost a household weeks of cheaper tariff. Handling here fed distrust but no recorded switch.
5. **Headline rise understates the household rise > anger without switching (P10–P12).** Unit-rate framing hid a standing-charge rise; the one stayer cites a past bad switch.
6. **Final bill stalls > customer chases > supplier cites a third party or process > refund only after outside pressure (R1, R2, R3, R9, R12, R13).** Every account that records an eventual payment in full (R1, R3, R7, R13) got it only after an MP, Ombudsman, bank reversal, customer-supplied read or court threat. This extends the map's §3.3 handling-failure-before-escalation pattern to the refund theme.
7. **Customer-supplied reading unlocks the bill (R5 > R7, R12's reply).** This is the `self_evidence` chain already named in the map.
8. **Billing continues after exit (R3, R6, R14).** DD collections after leaving appear in three separate cases and were reversed by the bank in one.
9. **Handling versus churn.** No account here records a switch caused by bad handling at the time of a price rise. Switching shows up in volume data instead (2016 Ofgem figures, Big Six 2017 losses), and in the account of the one household that stayed because of a past bad switch (P12). All refund accounts are post-churn by definition, so they show the cost of leaving rather than a reason to leave.

## (d) What I could not find

- **Trustpilot.** Not read, so no review-style accounts for any supplier.
- **Prepay price shock, 2022–23.** No first-person prepay account for the cap rises; the one prepay case (R15) is a final-bill debt. Citizens Advice's prepayment reports are located but not read, so V3 stays open.
- **DD change moment.** Only P1 and the MSE survey give the date a DD changed. No account separates announcement from effective date from DD change within one household.
- **Share rolling onto default at end of fix.** Not published at supplier level in anything I read. The only figure is stock (53%/51% default, April 2019).
- **Switching in announcement months for 2017–18 and 2022–23.** Ofgem's monthly switching series was not fetched; the Energy UK switching page failed to load. The 80% fall and the doubled meter reads are annual or two-day figures, not announcement-month shares.
- **Refund timeliness performance.** No Ofgem or Citizens Advice share of final bills or refunds issued on time. Only enforcement cases (E.ON Next, and listings for Octopus and Good Energy not opened).
- **SLC 27.17.** The Ofgem E.ON decision cites it for final bills within 6 weeks. I could not find a separate refund clause number, so the 10-working-day refund rule rests on MSE, Which? and forum statements.
- **Dates.** R12's thread year and the Yahoo 163,000 article's year are not shown on the pages.

---

## Pack B: home moves, supplier failure (SoLR), green and EV tariffs

# Customer voice sampling: home moves, supplier failures/SoLR, green and EV tariffs

I coded 26 accounts: 8 on home moves, 10 on supplier failure and 8 on EV and export tariffs. I did not find one usable account of a green tariff being misunderstood (see d).

- **Method:** I read each page through WebFetch summaries, not verbatim. Every row is paraphrased and carries no names, usernames or account numbers.
- **Self-selection:** All H, S and G rows are self-selected forum posts, press or Which?/Citizens Advice case boxes. They show which reactions exist, not how often.
- **Outcomes:** Most forum threads end without a reported outcome. Where I could not see one, the column says `not_stated`.
- **Trustpilot:** I did not fetch any Trustpilot pages. The searches returned forum threads that fitted better.
- **Dates:** The "Date" column is the date the poster or article published. Thread numbers and dates are the evidence trail; one year is inferred (G4).

## (a) Coded table

### Home moves (theme H, answers gap V4)

| id | theme / trigger | pay / meter | circumstance | first response > chain | supplier handling | outcome | time / effort | tone | source, date |
|---|---|---|---|---|---|---|---|---|---|
| H1 | home_move / other:liability_gap_between_old_owners_leaving_and_new_owner_moving_in (completion delayed about 3 months) | not_stated / not_stated (photos taken) | recent_move, Scotland | received bill > questioned liability > posted | `not_listening` (the previous owners' supplier held the buyer liable for about £150 of void-period use) | not_stated | not_stated | frustrated | [MSE 6323959](https://forums.moneysavingexpert.com/discussion/6323959/moved-home-saddled-with-previous-owners-debt), 4 Jan 2022 |
| H2 | home_move, billing_error / wrong_opening_read (bill used an opening read about 300 kWh below the customer's photographed total; two-register meter suspected) | not_stated, no DD set up / electricity, likely 2-register | recent_move; empty property using about 400 kWh a year | sent photo evidence > supplier went silent > threatened third-party collection > complained > asked for third-party help | `went_silent`, `threatened_collection` (letter posted to the empty property) | not_stated (forum advice: deadlock letter, then Ombudsman) | weeks:about 9; `self_evidence` (photos, written reads) | frustrated, urgent | [MSE 6082637](https://forums.moneysavingexpert.com/discussion/6082637/incorrect-starting-readings), 16 Dec 2019 |
| H3 | home_move / bills and collection demands addressed to "the occupier" after moving in (flat empty about a year; the new supplier was in place) | not_stated / not_stated | recent_move, rented | sent day-one reads and tenancy documents > old supplier kept billing > collectors wrote > Ombudsman complaint | `ignored_evidence`, then `reversed_after_ombudsman_accepted` (a later email read by commenters as accepting the debt was not the customer's) | pending; the Ombudsman accepted the case, final decision not stated | months:about 3 | frustrated | [MSE 6652015](https://forums.moneysavingexpert.com/discussion/6652015/ovo-energy-demands-for-payment-for-previous-occupier-i-am-an-octopus-customer/p3), posted Jan 2026 |
| H4 | home_move, billing_error / closing read disputed (£139 bill for 8 days; smart reading on completion day, "actual" read 7 days later; no photo) | not_stated / smart_credit (SMETS2) | recent_move, bought | switched after completion > old supplier sent small matching bill > second larger bill weeks later > asked to prove read | `demanded_customer_evidence`, late-fee threat (customer says the late-fee threat came before the due date shown on the bill) | not_stated | not_stated | anxious | [MSE 6419739](https://forums.moneysavingexpert.com/discussion/6419739/help-moved-in-to-new-home-and-have-had-a-large-bill-from-old-supplier), 24 Jan 2023 |
| H5 | home_move / `other:domestic_account_treated_as_business`; change of tenancy not recognised for about 7 months, then backdated | not_stated / register read 37,963 vs supplier record 16,178 (conflict) | recent_move, domestic customer | new supplier's switch rejected on an old unpaid bill > supplier asked for business documents > disconnection letter > £500 "visit" fee > complaint | `repeated_documents_request`, `fees_added_during_dispute` (seven £50 late fees; 25% upfront payment plan) | not_stated (considering Ombudsman) | months:about 10; `self_evidence` | distressed | [MSE 6613710](https://forums.moneysavingexpert.com/discussion/6613710/being-charged-5500-from-electricity-company-help), 19 Jun 2025 |
| H6 | home_move, final_bill / £57 "occupier" final bill from the supplier the vendor had left in place; customer had switched by an effective date after completion | not_stated / non-smart | recent_move, bought | ignored letters > letters said debt in collection > phoned | `fobbed_off` (payment plan, no breakdown) | not_stated | about 11 weeks to contact | frustrated | [MSE 6654658](https://forums.moneysavingexpert.com/discussion/6654658/british-gas-rip-off-final-bill-completed-on-new-house), 10 Feb 2026 |
| H7 | home_move, switching_onboarding / electricity switch blocked by a previous occupier's unpaid bill | not_stated / not_stated | recent_move, bought (property empty since April) | gave reads > gas switch went through, electricity blocked > new supplier said open an account with the old supplier first | `passed_between_suppliers` (new supplier told customer to contact the old one) | not_stated | not_stated | anxious, then reassured | [MSE 6575590](https://forums.moneysavingexpert.com/discussion/6575590/house-purchase-completed-but-previous-owner-owed-electricity-bill), 17 Dec 2024 |
| H8 | home_move / old supplier still billing 3+ months after move-out despite a dated photo of the last read | not_stated / not_stated | recent_move | sent photo > kept being billed > Ombudsman | `account_not_closed` | pending (Ombudsman) | months:3+ | not_stated | [MSE 5807834 p2](https://forums.moneysavingexpert.com/discussion/5807834/dispute-over-opening-reading/p2), 27–28 Mar 2018 |

### Supplier failure and SoLR (theme S)

| id | theme / trigger | pay / meter | circumstance | first response > chain | supplier handling | outcome | time / effort | tone | source, date |
|---|---|---|---|---|---|---|---|---|---|
| S1 | supplier_failure_solr, credit / final bill showed about £380 credit; Igloo failed 3 Oct 2021 | not_stated / not_stated | had switched away 21 Oct 2021 | claimed credit > old supplier said it transferred to the SoLR > SoLR said no record | `passed_between_suppliers` (neither would talk to the other) | not_stated; other posters in the thread were still waiting in March 2023 | months:2+ | frustrated, polite | [MSE 6325456](https://forums.moneysavingexpert.com/discussion/6325456/problem-getting-igloo-credit-balance-refunded-by-e-on-next), 10 Jan 2022 |
| S2 | supplier_failure_solr / three-hop chain: Avro, then PFP (switched 18 Aug 2021), then SoLR to British Gas. Avro's about £200 closing credit never reached the next supplier | not_stated / not_stated | recent_switch | asked forum > emailed the Avro successor | n/a, forum advice only | not_stated | months:3+ | polite, seeking guidance | [MSE 6321435](https://forums.moneysavingexpert.com/discussion/6321435/sorry-tale-was-with-avro-but-switched-to-pfp-then-solrd-to-british-gas), 21 Dec 2021 |
| S3 | supplier_failure_solr / SoLR (Green Network to EDF, Feb 2021): credit not visible on the new system; account not fully set up before a planned house move | not_stated / not_stated | `circumstance:house_move_pending` | waited > asked for reads and credit | `blamed_third_party` (data arrived in batches from the failed supplier) | not_stated | months:4+ | not_stated | [MSE news](https://www.moneysavingexpert.com/news/2021/06/gne-customers-left-waiting-edf-transfers), 3 Jun 2021 (three anonymised accounts) |
| S4 | supplier_failure_solr / SoLR to British Gas, Sept 2021: no tariff information, no credit repaid; gas moved but dual-fuel electricity did not | not_stated / not_stated | none_stated | received uninformative letters > no credit > chased | `silent` | not_stated | months:4+ | uninformed | [MSE news](https://www.moneysavingexpert.com/news/2022/03/bust-energy-suppliers-credit-delays-survey), 7 Mar 2022 (survey case box) |
| S5 | supplier_failure_solr / early contact, then months of silence, then an overdue-bill notice | not_stated / not_stated | none_stated | waited > overdue notice | `went_silent` | not_stated | months | dissatisfied | same page as S4 |
| S6 | supplier_failure_solr / no working account months after transfer, despite writing to administrators, the regulator and the new supplier | not_stated / not_stated | none_stated | wrote to three bodies > no response | `passed_between_bodies` | not_stated | months; high effort | frustrated | same page as S4 |
| S7 | supplier_failure_solr, estimates_and_reads / Bulb to Octopus: Bulb's estimates ran below the customer's own read for months. A reading submitted after the transfer used about £750 of credit, then Octopus credited back about £700 | not_stated / not_stated | recent_move_to_new_supplier | submitted read > credit consumed > credits appeared > asked Octopus to reverse "false" credits | `credit_swing_then_rate_rise` | not_stated | not_stated | frustrated, suspicious | [MSE 6451256](https://forums.moneysavingexpert.com/discussion/6451256/bulb-octopus-billing-problem), 6 Jun 2023 |
| S8 | supplier_failure_solr, dd_change / Bulb under administration: estimated usage nearly doubled against falling actual use; DD would cover a year's electricity in 7 months. Separately, DD raised about 60% with contact unanswered | not_stated / not_stated | `circumstance:administration_pending` | declined revision > switched; one customer cancelled DD > threatened surcharge and collection | `unresponsive`, `threatened_collection` | switched away | not_stated | angry (DD case); wry (estimate case) | [MSE 6398462 p6](https://forums.moneysavingexpert.com/discussion/6398462/bulb-energy-customers-will-be-moved-to-octopus-energy/p6), 31 Oct–11 Nov 2022 (two accounts, coded together) |
| S9 | supplier_failure_solr, debt / administrator pursued old debt: a customer who always paid on time got a collection letter for almost £800 of 2020 usage | not_stated / not_stated | none_stated | collection letter > contested | `back_billing` (administrators can backbill up to 6 years; active suppliers 12 months) | not_stated | not_stated | not_stated | [Citizens Advice, Back from the brink](https://www.citizensadvice.org.uk/Global/CitizensAdvice/Energy/Back%20from%20the%20brink_pub.pdf), Jun 2022 (case box; selected by an advocacy body) |
| S10 | supplier_failure_solr, dd_change / duplicate payments taken by the new supplier; four complaints unanswered, earliest over 4 months old | not_stated / not_stated | none_stated | complained 4 times | `silent` | not_stated | months:4+ | not_stated | same report as S9 |

### Green and EV tariffs (theme G)

| id | theme / trigger | pay / meter | circumstance | first response > chain | supplier handling | outcome | time / effort | tone | source, date |
|---|---|---|---|---|---|---|---|---|---|
| G1 | green_ev, eligibility / bought a charger about £545 in 2021 on a supplier's assurance it worked with a 2015 plug-in hybrid; the car manufacturer later said it never could | not_stated / smart | EV owner | complained > again > goodwill offer | `apologised_goodwill_only` (£150, no charger help) | `partial` | years | frustrated | [MSE 6614377](https://forums.moneysavingexpert.com/discussion/6614377/octopus-ev-smart-charger-misleading-compatibility-info-and-incomplete-resolution), Jun 2025 |
| G2 | green_ev, eligibility / paid about £500 for an approved charger on phone advice; the EV rate needed a two-rate meter that could not be fitted. £60 exit fee and loss of a two-year fix undisclosed | not_stated / non-EV single-rate | EV about to be bought, solar; bill about £632/month | phoned (45 min of transfers) > complaint with 5-day promise > specialist team > possible goodwill | `bad_advice`, `lapsed_promise` | not_stated | weeks; high effort | frustrated | [MSE 6360576](https://forums.moneysavingexpert.com/discussion/6360576/bad-advice-from-ovo-regarding-drive-tariff-cost-me-money-is-there-anything-i-can-do), 25 May 2022 |
| G3 | green_ev, tariff_terms / charger paid about £964 via the supplier; support for that charger withdrawn from the EV tariff from 15 Jul 2025, so rate rises from about 7p to about 24p per kWh | not_stated / smart | EV owner | asked about compatibility before buying > told car OR charger would do > notice of withdrawal | `told_to_switch` | not_stated (penalty-free exit reported) | months | frustrated, polite | [MSE 6610758](https://forums.moneysavingexpert.com/discussion/6610758/ev-and-ovo-charge-anytime), 3 Jun 2025 |
| G4 | green_ev, time_of_use_surprise / charging slot moved about 20 minutes after plug-in, so household use hit the higher "bump" rate; announced 6-hour-a-day smart-charging cap | not_stated / smart | secondhand: a friend's experience relayed by a prospective switcher | plugged in, ran appliances > slot moved > higher rate | n/a (forum users say the terms cover it, but note they are complex) | not_stated | not_stated | felt misled | [MSE 6653605 p1](https://forums.moneysavingexpert.com/discussion/6653605/octopus-go-intelligent-tariff-recent-changes/p1), Feb (year inferred from thread number as 2026) |
| G5 | green_ev, billing_error / about 3,600 kWh billed against about 1,800 kWh used; charger drawing apparently counted twice in half-hourly data (SMETS1 firmware suspected) | not_stated / smart (SMETS1 suspected) | EV owner, switched July 2023 | complained Aug 2023 > Ombudsman Nov 2023 > Ombudsman asked for readings (supported customer) > bounced between the two | `bounced_between_bodies`, `promised_callbacks_not_made`; "meter is accurate" | not_stated | months:6 | frustrated, polite | [MSE 6501366](https://forums.moneysavingexpert.com/discussion/6501366/eon-next-ev-tariff-over-charging-issue), 25 Jan 2024 |
| G6 | green_ev, billing_error / overnight EV rate not applied to bills for months; over £200 overcharge estimated from the customer's own charger data | not_stated / not_stated | EV owner who switched end of 2021 | sent readings > supplier went silent > Which? intervened > refunded, plus £100 compensation (two payments) | `went_silent`, then `apologised_goodwill` (missing estimated-consumption data on the account) | `escalated_won` (refund over £230 plus £100) | months | frustrated | [Which?](https://www.which.co.uk/news/article/bulb-cant-get-my-electricity-bill-right-can-you-help-aasCt3R53yur), 14 Nov 2022 (press case; selected by a consumer-advice body) |
| G7 | green_ev, export_payment / SEG paid only from approval date; about 900 kWh exported in the gap between install and approval was unpaid | not_stated / solar export | new solar owner | asked forum | n/a (peers say no supplier pays pre-approval; some say delay was on documents) | `not_recovered` | months | curious, somewhat frustrated | [MSE 6631782](https://forums.moneysavingexpert.com/discussion/6631782/smart-export-guarantee-no-payment-during-set-up-time), 1 Oct 2025 |
| G8 | green_ev, tariff_terms / app stopped making a schedule once the car was full; supplier reportedly tightening charger-only integrations | not_stated / smart, 850–1,000 kWh a month | EV owner, 3 months on tariff | rebooted, unlinked > charger option vanished | no contact with support yet | not_stated | days | puzzled | [MSE 6637529](https://forums.moneysavingexpert.com/discussion/6637529/octopus-intelligence-go-tariff-issues), 2 Nov 2025 |

**Read on the home-move rows (gap V4).** In seven of the eight accounts, the move itself seeded the problem. It showed up in three ways: a bad opening or closing read (H2, H4, H8), a missing or late account (H3, H5, H7), or a void-period charge between occupiers (H1, H6). All seven are mismatches between the two occupiers' records and who is liable, not isolated billing mistakes. The eighth (H4) is a closing-read dispute. All eight are self-selected, so none says how often a move seeds a bad opening read or a missing account.

## (b) Representative rates

Grades: **P** published from a census or weighted sample, **S** single or self-selected source, **A** analyst arithmetic. Several figures are modelled estimates, not measurements, and I say so against each.

**Home moves**

| Rate | Value | Grade | Source |
|---|---|---|---|
| Household moves per year | about 1.8m in England (2024-25); about 2.1m across GB | S, extrapolated from the English Housing Survey | [Ofgem moving-home consultation](https://www.ofgem.gov.uk/sites/default/files/2026-10/moving-home-process-guidance-consultation.pdf), 5.17 and Table 2 |
| Share of moves where the supplier is told in advance | about 65% | S, supplier estimate on "limited data" | same, 5.18 |
| Average days before an unnamed occupier first contacts the supplier | about 90 days (about 2 weeks under an existing move process) | S, supplier evidence | same, 5.23 |
| Debt linked to unnamed accounts (change of tenancy) | 20–40% of all domestic energy debt | S, stated as stable since before the crisis | [Ofgem call for input](https://www.ofgem.gov.uk/sites/default/files/2025-12/Tackling-energy-debt-in-home-moves-process-call-for-input.pdf), 9 Dec 2025, sections 2.5 and p.4 |
| Total domestic debt and arrears | £4.43bn (Jun 2025); about £4.79bn (Q1 2026) | P | call for input; consultation 5.14 |
| Average arrears per account without a repayment plan | £1,872 electricity, £1,613 gas | P | consultation 1.5, footnote 1 |
| Illustrative debt avoided per successful change of mode | £814; modelled £84m / £242m / £493m a year (low / mid / high) | A, modelled, not measured | consultation 5.43, Table 2 |

- **Not found:** the share of home moves with billing problems, deemed-contract volumes, and Ombudsman or complaint counts for home moves. Neither Ofgem document gives any. The consultation also contains internal inconsistencies, listed in (d).

**Supplier failure and SoLR 2021-22**

The sources disagree on counts, so I give each as stated.

| Rate | Value | Grade | Source |
|---|---|---|---|
| Suppliers failed | 28 | P | [NAO press release](https://www.nao.org.uk/press-release/the-energy-supplier-market/), Jun 2022; [Ofgem press release](https://ofgem.gov.uk/press-release/ofgem-announces-tough-new-financial-measures-ensure-energy-suppliers-can-withstand-future-shocks-including-protection-customers-credit-balances), 20 Jun 2022 |
| Customers moved by SoLR | NAO: nearly 2.4m, with Bulb's 1.6m separate. Ofgem: "over 2 million" protected in 2021. Citizens Advice: over 4m affected | P (NAO, Ofgem), S (Citizens Advice) | same, plus [Back from the brink](https://www.citizensadvice.org.uk/Global/CitizensAdvice/Energy/Back%20from%20the%20brink_pub.pdf), Jun 2022 |
| Cost to bill payers | £94 per customer (Ofgem, NAO, on £2.7bn); Citizens Advice puts total failure costs at £4.6bn, up to £164 per bill | P / S | same |
| Customer credit balances in £ | **not found** | n/a | Ofgem pages did not state it |
| Time the SoLR process takes | up to 14 days; a deemed contract lasts 6 months | P | [Ofgem blog](https://ofgem.gov.uk/blog/how-youre-protected-when-energy-firms-collapse) |
| Share of customers still waiting for credit months after transfer | 57% across big transfers; at least 20% of Sept–Oct 2021 transfers still waiting after 3+ months; about 93% of the PFP/People's to British Gas transfer after about 4 months | S, self-selected survey of 12,373, Jan–Feb 2022, credit-holders only | [MSE news](https://www.moneysavingexpert.com/news/2022/03/bust-energy-suppliers-credit-delays-survey), 7 Mar 2022 |
| Over a quarter still waiting for final bills past 6 weeks | the 6-week guaranteed standard does not apply to SoLR | S | same |
| Accounts moved | PFP 82,000 and People's 350,000 to British Gas; British Gas over 700,000 from eight failed suppliers; Shell about 500,000 from five; EDF over 600,000 | S (press-reported) | same |
| Net experience score by new supplier | British Gas -56; Shell -32; EDF -29; E.on Next +10; Octopus +17. Ease of contact: British Gas 34%, Octopus 80% | S | same |
| GNE to EDF, Feb 2021 | about 360,000 households moved; about 3% (about 10,800) not yet transferred by Jun 2021; separately up to 2,000 customers of two other failed suppliers (about 200,000 combined) waiting 6+ months | S (press-reported) | [MSE news](https://www.moneysavingexpert.com/news/2021/06/gne-customers-left-waiting-edf-transfers), 3 Jun 2021 |
| Administrators pursuing debt | 43% of Citizens Advice supplier-failure contacts in May 2022 (10% in Nov 2021); median debt chased £370 (87 recorded cases of 276 sampled) | S | Back from the brink |

**Green, EV and export tariffs**

| Rate | Value | Grade | Source |
|---|---|---|---|
| Customers expecting a "green" tariff to supply 100% renewable electricity to their home | about a third; 11% expect the supplier to generate some of it; 8% all of it. Tariff share claiming green credentials: over half of 355 tariffs (Jun 2019), up from 9% three years earlier | S (sample size not stated) | [Which?](https://www.which.co.uk/news/article/how-green-is-your-energy-tariff-aSmQB4h2x61x), 27 Sep 2019 |
| Ombudsman share of disputes on EV tariffs, home moves or SoLR | **no figure published** | n/a | the 2023–25 [biennial review](https://www.ofgem.gov.uk/sites/default/files/2026-11/energy-ombudsman-biennial-review-2023-to-2025.pdf) lists sampled case themes (billing incl. back-billing, customer service, metering incl. smart, Feed-in Tariff, sales and supplier transfer) with no counts |
| Ombudsman appeal rate and speed | about 11% of cases appealed; 25 days average to resolve a domestic dispute; 84% satisfaction (2025) | P (74-case sample for the theme list) | same |

## (c) Recurring chains

1. **Customer's own reading against the supplier's record.** The move or transfer creates two different numbers. The customer holds a photo or meter total, and the supplier's opening or closing read differs. The supplier asks the customer to prove it, goes quiet, and threatens collection. Examples: H2, H4, H8, S7, G5. Forum replies keep giving the same advice: send a written complaint, ask for a deadlock letter, wait 8 weeks, then go to the Ombudsman. This extends the existing `self_evidence` code.
2. **"The occupier" debt escalating by post.** A bill addressed to "the occupier" goes unanswered and escalates to collection letters. Examples: H3, H6, plus the debt-on-previous-occupier cases H1, H5, H7. The Ofgem consultation corroborates the mechanism: about 90 days before an unnamed occupier first contacts the supplier. What the customer can do is call and supply an opening read and a completion or tenancy date. Several commenters advise that liability starts from that date, not from move-in.
3. **Credit lost between two suppliers.** The failed supplier says it passed the credit on, and the SoLR says it has no record. Examples: S1, S2, S3. The 57% still waiting in the MSE survey is the rate counterpart. This is `passed_between_suppliers` again.
4. **Administrator debt after failure.** Collection letters for old usage, backdated well beyond the 12-month cap that applies to an active supplier. Examples: S9, S10. Citizens Advice put these at 43% of its failure contacts in May 2022.
5. **The eligibility trap on EV tariffs.** The customer buys a charger or car on supplier advice. The tariff later turns out not to cover it, through meter type, charger support withdrawal or car incompatibility. The supplier offers goodwill or tells the customer to switch. Examples: G1, G2, G3, G8. This is the same shape as O8: `apologised_goodwill_only`.
6. **Time-of-use terms read as a promise.** The customer expects a continuous cheap window and the app moves a slot, or only part of a window is cheap. Examples: G4, G8. It is hard to tell misunderstanding from mis-selling here; the forum splits on it, and the Ombudsman page the theme map cites says the same about tariff terms.
7. **Billing from half-hourly data not matching the meter.** Examples: G5, G6. Both involved a supplier saying the meter is accurate. In both the customer's own charger data was the evidence.
8. **Handling failure before escalation.** Where the handling is visible (H2, H3, H5, S10, G2, G5, G6), a handling failure precedes every escalation or goodwill offer. This matches the §3.3 hypothesis on the existing map, and the sample is still too small to say more.

## (d) What I could not find

- **Credit balances protected, in £.** No total for 2021-22. Ofgem's press release and blog do not state one. The Ofgem SoLR levy true-up decisions (sept and nov 2022) or the Ofgem Annual Report 2021-22 are the likely homes. I found them in the search results but did not read them.
- **Customer counts disagree.** NAO says nearly 2.4m (plus Bulb's 1.6m separately) and Ofgem says over 2m, while Citizens Advice says over 4m affected. I did not reconcile them. The NAO and Ofgem dates differ, and I read the summaries rather than the full documents.
- **Share of home moves with billing problems, and deemed-contract volumes.** Neither Ofgem document gives any. The 20–40% of debt on unnamed accounts is the only rate on this theme, and it is a supplier-reported range.
- **The Ombudsman's category shares for moves, SoLR and EV tariffs.** No source gives a split. The biennial review gave sampled themes, not counts. The Ombudsman's own 2016–2022 history is also still missing (gap V6).
- **A green tariff account.** I found no account of a customer misunderstanding a green tariff. Searches returned the 2019 Which? survey and greenwashing coverage, not household stories.
- **Consumer accounts for 2016–2020 on moves, and 2016–2020 SoLR.** The earliest home-move accounts are 2018 (H8) and 2019 (H2). I coded no SoLR account before 2021. A real gap for the 2016–2020 SoLR failures.
- **Outcomes.** Most forum threads end without a reported result. Only G6 and G1 have a recorded outcome, which means resolution rates cannot be read from this sample.
- **Trustpilot.** I read none by hand.
- **Ofgem consultation inconsistencies** (so use its numbers with care):
  - The tenancy shares in 3.25 add to 123%.
  - The recurring-cost figures differ between 5.35 and Table 2.
  - The exhausted-credit mid case exceeds the high case.
  - The consultation states about 72% smart-meter penetration, and the earlier call for input said 64%. These are separate documents with different bases.
- **G4 date.** The thread says "3 February" with no year. I inferred 2026 from the thread number, so treat it as approximate.
- **S8 coding.** I coded two separate Bulb forum accounts together as one row to save space. Split them if the map wants one account per row.

**Candidate new codes for the map:** `account_not_closed` (H8), `fees_added_during_dispute` (H5), `repeated_documents_request` (H5), `bad_advice` (G2), `lapsed_promise` (G2), `told_to_switch` (G3), `back_billing` (S9). None of the other codes were new.

**Memory:** nothing from user memory was used, and no new facts worth saving to it came out of this.

---

## Pack C: the reports behind gaps V1 (ECSS), V2 (supplier top-five complaints), V3 (forced prepayment) and V6 (Ombudsman 2016-2022)

# Customer-voice research: gaps V1, V2, V3 and V6

Researched 23 Nov 2026. Primary documents were read through WebFetch, because curl to ofgem.gov.uk was refused with 403 from the proxy. WebFetch passes each page through a summariser, so figures are summariser output, not hand-read. Two details already disagree between passes, noted below. Grades: P is primary published, S is secondary, A is analyst arithmetic.

## V1. Ofgem Energy Consumer Satisfaction Survey (ECSS)

### What the Jan 2026 findings report says (P)

URL: https://www.ofgem.gov.uk/sites/default/files/2026-05/Energy-Consumer-Satisfaction-Survey-Findings-Report-January-2026.pdf

- **Fieldwork and sample:** 5 Jan to 3 Feb 2026. n=3,911, ±1.57%.
- **Contact window is the last 3 months, not 12 months.**
  - 33% contacted their supplier, and a further 4% tried but did not get through.
  - The reasons base is n=1,473.
- **Reasons for contact (Fig. 25, p.37 in the first pass):**

| Reason | Share |
|---|---|
| Meter reading | 16% |
| Bill query | 15% |
| Smart meter query | 14% |
| Help paying bills | 12% |
| Tariff change | 11% |
| Products or services | 11% |
| Credit refund | 9% |
| Change of circumstances | 9% |
| Direct debit problem | 8% |
| Faulty meter | 7% |
| Change how they pay | 7% |
| Complaint | 6% |
| Switching | 5% |
| Gas leak | 4% |
| Energy cut off | 4% |

  - "Any payment query" nets to 44%.
- **Complaints:** 6% of contacts, about 2% of all respondents. The base is n=96, below 100, so the report cautions on it.
- **Reasons for complaint (Fig. 39, p.52):**

| Reason | Share |
|---|---|
| Net billing | 70% |
| Smart meter problem | 31% |
| Bill problem | 29% |
| Pricing | 29% |
| Managing payments | 26% |
| Discount not applied | 22% |
| Prepayment top-up problem | 22% |
| Staff attitude | 19% |
| Direct debit problem | 18% |
| Not getting financial support | 18% |
| Refund problem | 15% |
| Disconnected | 15% |
| Mis-selling | 14% |
| Switching | 12% |
| Missed appointment | 7% |

- **Complaint handling (Fig. 40):**
  - Dissatisfied with time taken: 38%, up from 25% in Jul/Aug 2025.
  - Dissatisfied with overall handling: 31%, up from 18%.
  - Both remain below Jan 2025 (55% and 50%).
- **Resolution (Fig. 33, n=1,473):** fully resolved 67%, not resolved 9%, up from 7%.
- **Effort:**
  - Ease of contact is 78% easy and 11% difficult (n=3,339).
  - At least one difficulty: 51%.
  - Needing to contact more than once: 11%.
- **Smart meters (pp.61–63, n=2,723 smart households):**
  - 34% reported at least one issue in the last six months.
  - Most common issues: no automatic readings 12%, in-home display stopped 10%, meter stopped showing information 8%, inaccurate bill 8%.
  - Of 1,150 issues, 74% led to supplier contact and 21% were never made known to the supplier.
  - Outcomes where contact was made (Fig. 49, p.62 or 63, base ambiguous):
    - Resolved by supplier: 49%, down from 55%.
    - Passed to another organisation: 10%.
    - Still being looked into: 9%.
  - Time to resolve (n=414): under 1 month 64%, 1–2 months 15%, 2–3 months 6%, 3+ months 12%, up from 8%.
- **First-contact resolution is not measured directly.** The nearest proxies are "issue fully resolved" at 67% and "more than one contact needed" at 11%.

**Corrections to the theme map's §1.2:**

- **The 22% claim is not stated in the text.**
  - The Citizens Advice figure appears to be 10% "passed to another organisation" plus about 12% "couldn't be resolved at the moment".
  - The chart labels were not cleanly mapped. The summariser gave 16%, 12% and 4% for three categories (including "couldn't be resolved at the moment") with the labels unmapped, so 22% is an inference. Keep it S.
- **"Smart meter problems are the most common complaint" is not a stated finding.**
  - Smart meter problems are second in the Jan 2026 complaint reasons: 31%, behind net billing at 70%.
  - Among contact reasons the most common is meter reading, at 16%.
  - Citizens Advice's reading may rest on "Smart meter problem" being the largest single named reason.
  - Do not carry the claim as P.
- **Page numbers are unreliable.** The two passes gave different pages for the same figures (complaints p.51–53, smart outcomes p.62–63). Cite by figure number.

### The ECSS series, as far as read (P)

| Wave | Contacted (3 mo) | Complained | Top complaint reasons | Handling satisfied / dissatisfied | Fully resolved |
|---|---|---|---|---|---|
| Aug/Sep 2023 (wave 17, fieldwork 30 Aug–18 Sep, n=3,742) | 32% | 10% of contacts, about 4% of all (n=149) | bills 32%, smart 27%, cost 26%, staff 17%, DD 16% | 41% satisfied / 44% dissatisfied (29% satisfied in Nov/Dec 2022) | 54% |
| Jan/Feb 2024 (wave 18, 18 Jan–10 Feb, n=3,855) | 32% | 7% of contacts, 2% of all (n=101) | bills 47%, smart 26%, staff 18%, cost 17% | 36% satisfied | 57% |
| Jan 2025 (6–31 Jan, n=3,854) | 32% | 6% of contacts, 2% of all (n=89) | smart 30%, bills 27%, pricing 21%, staff 17% | 44% satisfied / 50% dissatisfied | 67% |
| Jan 2026 (n=3,911) | 33% | 6% of contacts, 2% of all (n=96) | net billing 70%, smart 31% | 31% dissatisfied overall, 38% dissatisfied on time | 67% |

Further points on the series:

- **Reasons for contact:** meter reading, bill query and smart meter query lead in every wave. Meter reading was 22% in Aug/Sep 2023, 18% in Jan/Feb 2024, 19% in Jan 2025 and 16% in Jan 2026.
- **Difficulty:** any difficulty was 63% in Aug/Sep 2023 (long waits 28%) and 54% in Jan/Feb 2024. It was 47% in Jan 2025 and 51% in Jan 2026. These are not clean like-for-like, because the Jan 2025 and Jan 2026 reports define difficulty slightly differently.
- **Unresolved by query type:** complaints and smart queries were the least resolved. In Aug/Sep 2023 both were 22% unresolved. In Jan/Feb 2024 complaints were 28% and smart 27%.
- **The tracker began in 2018.** The Aug/Sep 2023 report calls itself wave 17 of a tracker running since 2018.
- **Wave-to-wave comparability:** the series is not clean, because the base for the complaint questions is only 89–149 in every wave.

### 2018–2022 predecessor series (P)

The 2018–2022 series is Ofgem and Citizens Advice's "Consumer Perceptions of the Energy Market". I read one issue: https://www.ofgem.gov.uk/sites/default/files/2022-05/Q3%202021%20Ofgem%20and%20CA%20-%20Consumer%20Perceptions%20of%20energy%20markets%20v1.0_0.pdf

- **Customer service satisfied / dissatisfied (p.16):** Q4'18 75/7, Q4'19 74/8, Q2'20 75/7, Q4'20 73/6, Q1'21 69/9, Q3'21 71/9.
- **Contact "easy / difficult" (p.17):** Q4'18 73/13, Q4'19 73/15, Q4'20 72/15, Q3'21 66/18. Phone was the hardest channel, at 58% easy in Q3'21.
- **Complaining in the past 3 months (p.20):** 10% in Q3'21 and 12% in Q2'21. No earlier years are given in the text.
- **Complaint handling in Q3'21:** 41% satisfied, 32% dissatisfied (n=130). This was the first time since Q1'20 that satisfied exceeded dissatisfied.
- **Not reported in that issue:** share contacting, reasons for contact, first-contact resolution. Other Consumer Perceptions issues were surfaced in search but not read: Q4 2020, Q2 2021, Q1 2022, Q3 2022, Q4 2022.
- **Not reached:** the Ofgem Customer Satisfaction Survey and Complaints Handling Survey reports for 2016–2018, such as the 2018 Quadrangle research report.

### Still open for V1

- Waves 1–16 (2018 to mid-2023) of the ECSS series itself.
- The Jul/Aug 2025 findings report, only surfaced in search.
- The "What drives consumer satisfaction" report 2025/26.
- A like-for-like complaint-reason series, which would need a matched base.

## V2. Suppliers' published "top 5 complaint reasons" pages

Suppliers publish the top five under Ofgem's SLC 5 data request. The reason categories come from an 18-category template (B5–B22) in Ofgem's guidance.

- **Guidance:** https://www.ofgem.gov.uk/sites/default/files/2025-11/Guidance%20on%20submitting%20domestic%20customer%20complaints%20data.pdf
- **Complaint definition (para 3.1):** "any expression of dissatisfaction made to an organisation, related to any one or more of its products, its services". It has no time limit, covers how a complaint was handled, and applies even to customers the supplier does not supply.
- **Publication:** suppliers must publish quarterly data within one week of submitting it (para 3.14). The guidance does not say top reasons must be published.

| Supplier | URL | Period | Ranked reasons | Shares |
|---|---|---|---|---|
| British Gas | https://britishgas.co.uk/complaints/performance.html | Q2 2026 (1 Apr–30 Jun) | Billing 51% (46% in Q2 2025), Payments 20%, Credit Management 12% (6% in Q2 2025), Customer Service 8% (11%), Metering 4% (10%) | Stated, as a share of complaints received |
| EDF | https://www.edfenergy.com/help-support/complaints-performance | Q2 2026, 46,534 domestic complaints | Customer Service 33%, Billing and meter reading 17%, Payments 12%, Debt and disconnections 9%, Meter install or not working 7% | Stated; the five total 78% |
| E.ON Next | https://www.eonnext.com/our-performance | Page says Q3 2026 | Customer Service 33.23%, Payments 13.94%, General billing 10.68%, Smart billing 10.05%, Debt 7.58% | Stated; the page gives no exact dates for the quarter |
| Octopus | https://octopus.energy/policies/quarterly-performance-reporting/ | "Last quarter", probably Q2 2026 (67,547 complaints), unconfirmed | Customer Service 12,520; Billing, non-smart 11,881; Billing, smart 9,752; Payments 9,105; Meter install or fault 7,042 | Counts only |
| OVO | https://www.ovoenergy.com/our-complaints-performance | Oct 2024–Sep 2025 | Customer Service, Payments, Smart billing, Debt, General billing | Rank only |
| Utilita | https://utilita.co.uk/contact/complaints | Not stated | Customer Service 50%, Payments 18%, Smart billing 11%, Smart PPM metering 8%, Pricing 3% | Stated, but the date is not (the page's performance table runs Apr 2023–Jun 2025) |
| "E" (e.org) | https://e.org/assets/pdf/Complaint performance_Q2_2026_which.pdf | Q2 2026, 460 complaints (172 per 100k) | Prepay debt, smart PPM meter, classic PPM meter, billing, Customer Service | Order only; the page says nothing about whether it is ranked |

Notes on the V2 table:

- **Customer Service is its own category at EDF, E.ON Next, Octopus, OVO and Utilita.** At British Gas it is only 8%. EDF itself says its category is broad and may include generic issues.
- **British Gas and the Ombudsman data differ.** British Gas shows billing at 51%, in the same range as Ombudsman Billing (48–65% in Q1 2025 per the theme map). Customer Service is 33–50% at four other suppliers, against 7–14% in Ombudsman disputes. The two measure different populations: front-line complaints against disputes that reached the Ombudsman.
- **Octopus's 74% (A):** about 74% of 67,547 if the five counts relate to Q2 2026. The page does not say so.
- **Not reached:**
  - ScottishPower: no page found. Its Ofgem submission was surfaced in search only (https://www.ofgem.gov.uk/sites/default/files/2026-09/Scottish-Power-response.pdf).
  - Utility Warehouse and So Energy: no complaints-performance pages surfaced. https://www.so.energy/unhappy/ appeared in search but was not fetched.
- **Consumer Scotland check:** https://consumer.scot/publications/consumer-experience-customer-complaints-a-comparison-of-published-customer-complaint-data-across-uk-communication-energy-financial-services-and-water-sectors-html/ says suppliers do not consistently publish top reasons. I read only the first 100,000 characters.
- **Prior-year pages:** the pages shown are the current quarter only. Only British Gas gives a year-on-year comparison, and no supplier gave a back series.
- **Citizens Advice complaints handling performance:** https://www.citizensadvice.org.uk/Global/CitizensAdvice/Energy/Domestic%20complaints%20handling%20performance%20(Updated%20September%202023).pdf holds weighted complaints per 10,000 by supplier, quarterly 2012 to Q2 2023. It has no reasons.

## V3. 2022–23 forced prepayment installs

### Volumes (P)

- **DESNZ, 27 Mar 2023:** https://www.gov.uk/government/news/just-three-energy-suppliers-making-up-over-70-of-all-forced-installation-of-prepayment-meters
  - 94,201 meters installed under warrant in calendar 2022, about 7,500 a month.
  - British Gas 25,000, Scottish Power 24,320, OVO 16,867. Together that is 66,187, about 70%.
  - Scottish Power's rate was over 500 per 100,000 meter points.
  - Source: supplier responses to DESNZ requests in Jan/Feb 2023. Coverage is most but not all domestic suppliers, and the page says figures may differ slightly from Ofgem's.
- **Ofgem press release, 28 May 2025:** https://www.ofgem.gov.uk/press-release/suppliers-commit-further-ps186million-customer-compensation-and-debt-write-following-ofgems-prepayment-meter-review
  - More than 150,000 involuntary installs reviewed, including warrant installs and remote switches to prepay mode.
  - Assessment period 1 Jan 2022 to 31 Jan 2023.
  - Warrant installs where fitting was not safe or reasonably practicable: estimated at under 1% of cases.
  - New commitment £18.6m: £5.6m compensation to at least 40,000 customers plus £13m debt write-off. About £55m of hardship payments and write-off came earlier.
  - New rules require at least 10 contact attempts and a welfare visit before installing a prepay meter.
- **Ofgem Market Compliance Review, published 3 Jun 2026:** https://www.ofgem.gov.uk/sites/default/files/2026-06/Market-Compliance-Review-prepayment-meter-installations.pdf
  - Over 150,000 accounts reviewed.
  - 1,925 accounts where a prepay meter was wrongly installed (under 2%).
  - 46,027 customers identified for compensation, £7,037,003 (the report says £7m).
  - Compensation by category:

| Category | Customers | Paid |
|---|---|---|
| Inappropriate installation, switch or unsafe use | 1,925 | £1,629,865 |
| Vulnerability not considered | 805 | £295,276 |
| Unfair customer treatment | 9,933 | £2,680,332 |
| Insufficient debt support | 2,382 | £556,834 |
| Process misalignment | 30,982 | £1,874,695 |

  - Tariff of payments per head: £1,000, £500, £250, £250, £40–60.
  - £13m of debt written off.
  - Timeline: review launched January 2023, stricter rules November 2023, first restarts January 2024.
  - Enforcement: Utilita investigation opened November 2024, OVO's extended May 2025.
  - The page gives no per-supplier counts of warrant or forced installs, no share of vulnerable customers and no remote-switch counts. British Gas was never part of the review.
- **Ofgem Phase 1 process evaluation:** https://www.ofgem.gov.uk/sites/default/files/2026-10/PPM-Process-Evaluation-Report_0.pdf (data cut-off early 2026).
  - Debt-related prepay installs peaked at about 45,000 a quarter for electricity and 30,000 for gas before the moratorium. This is involuntary and voluntary combined, and remote switches are excluded.
  - Post-rule counts, warrant counts and remote-switch counts: not given.
  - The share of debt repaid via prepay fell from above 50% in early 2023 to about 40% by end-2025.
  - Self-disconnection is defined as supply lost for over 3 hours. Severe self-disconnection fell 36%, indicative only and not attributable to the policy.
  - Satisfaction for consumers in vulnerable situations rose from 61% to 72%.
  - The text dates the new rules as both September and November 2023 without explaining the gap.
- **Ofgem PPM discussion paper, 28 Oct 2026:** https://www.ofgem.gov.uk/sites/default/files/2026-10/PPM-discussion-paper-2026.pdf
  - Smart PAYG is 81% of prepay installs, Jan 2024 to Aug 2026.
  - 34% of prepay consumers say budgeting is easier, 32% cite greater control, 21% better understanding.
  - Typical annual cost at the Oct–Dec 2026 cap: £1,723 direct debit, £1,678 prepay, £1,861 standing charge.
  - It has no self-disconnection rates, no prepay customer total and no group breakdowns.

### Citizens Advice (P where read)

- **"Future of Prepayment: Discussion Paper", 25 Jun 2026**
  - Page: https://www.citizensadvice.org.uk/policy/publications/future-of-prepayment-discussion-paper/
  - **Not reached.** The PDF (assets.ctfassets.net, `Future_of_Prepayment_-_Discussion_Paper_June_2026_FINAL.pdf`) is off WebFetch's allowlist, and a search did not surface it.
  - The page itself holds only £3,285 average arrears where no repayment plan exists, described as an all-time high and up 86% in three years. It has no self-disconnection or rationing figures.
- **"Hitting the Rationing Wall", 26 Aug 2026**
  - Page: https://www.citizensadvice.org.uk/policy/publications/hitting-the-rationing-wall/
  - **PDF not reached** (same allowlist block).
  - BMG Research for Citizens Advice, n=4,556, fieldwork 23–28 Jul 2026, all GB households and not prepay only.
  - 74% took at least one action in the past year to save energy or cut bills.
  - 63% used less heating and hot water.
  - 47% cut appliance and light use.
  - 33% cut food spending.
  - 37% worried about affording energy this winter.
  - If prices rise again: 23% would turn off heating or hot water, 31% would cut food, 20% would run down savings.
  - Energy prices 43% above 2021 in real terms. Half of debt clients are in a negative budget. The average debt-client deficit rose 45% from £276.02 to £388.92 a month.
  - **No prepay or self-disconnection figures and no group breakdowns on the page.**

### Still open for V3

- Self-disconnection rates, and self-rationing among prepay customers, by group. These are probably in the two Citizens Advice PDFs, which I could not fetch.
- Per-supplier forced-install counts and vulnerability shares for the Ofgem review.
- Counts of remote switches to prepay mode.
- The Ofgem 2023 investigation and market review documents themselves. Only the press-release and MCR summaries were read.
- Earlier Ofgem self-disconnection evidence: https://www.ofgem.gov.uk/system/files/docs/2020/06/self-disconnection_and_self-rationing_-_draft_impact_assessment_0.pdf and Citizens Advice "Topping up or dropping out", "Staying Connected" and "Kept in the dark" were surfaced but not read.
- Ofgem Consumer impacts of market conditions survey (Feb–Mar 2026), surfaced but not read.

## V6. Energy Ombudsman category shares and volumes, 2016–2022

### Energy sector reports by year (P)

Source: Ombudsman Services, "Annual Report [year] Energy sector report". The Energy Ombudsman annual reports page lists the 2016–2019 sector PDFs: https://www.energyombudsman.org/reports-and-data/annual-reports

| Year | Initial contacts | Resolved | In scope or outcome | Categories | Shares |
|---|---|---|---|---|---|
| 2016 | 88,255 (54% in scope, 46% out) | 41,622 (label unclear) | Not reliably extractable | Billing, Transfers, Customer service, Other | Not matched |
| 2017 (p.4) | 88,423 (54% in scope, 46% out) | 48,737 | 63% upheld, 8% not upheld, 8% settled, 21% maintained | Billing, Customer service, Switching | Not matched |
| 2018 (p.7) | 108,349 (50% in scope) | 45,667 | 64% upheld, 6% not, 11% settled, 19% maintained | Billing, service quality, contract issues | Billing over 60% (p.3) |
| 2019 (pp.5, 20) | 68,523 | 56,978 | 57% upheld, 9% not, 23% settled, 11% maintained; 99.2% resolved within 8 weeks | Billing, payments and debts, customer service | None |

URLs:

- https://tag-craft.files.svdcdn.com/production/assets/assets/Annual-Report-2016-Energy-sector-report.pdf
- https://tag-craft.files.svdcdn.com/production/assets/assets/Annual-Report-2017-Energy-sector-report.pdf
- https://tag-craft.files.svdcdn.com/production/assets/assets/Annual-Report-2018-Energy-sector-report.pdf
- https://tag-craft.files.svdcdn.com/production/assets/assets/Annual-Report-2019-Energy-sector-report.pdf

Cautions on the table:

- **The 2019 contacts figure is described as "actionable energy complaints" in the Energy Ombudsman's own news item.** The sector report has no definition of that term, only an asterisk reading "inside terms of reference". The two 2019 figures (68,523 contacts and 56,978 resolved) may be of different kinds.
- **The 2018 contacts, 108,349, are all initial contacts.** About half were outside terms of reference.
- **The 2019 jump to 68,523 is not comparable to 108,349 in 2018.** I cannot say whether 2019 contacts are only the in-scope ones.
- **Complaint definitions:** none given in the reports. The Ombudsman's scheme rule: a complaint can be accepted only after the supplier has had 8 weeks to resolve it or has issued a deadlock letter. https://www.energyombudsman.org/complaints-data/explaining-our-complaints-data
- **Category shares:** only 2018 gives one (billing over 60%). The 2016 and 2017 pages' layout meant percentages could not be paired to categories.

### 2019–2022 totals (P)

- **Ofgem biennial assessment, July 2019 to June 2021:** https://www.ofgem.gov.uk/sites/default/files/2022-05/Energy%20Ombudsman%20performance%20for%20the%20period%202019-2021.pdf
  - 216,262 disputes received, 134,068 within scope.
  - Two-year totals only. No category split and no definition.
- **Ofgem biennial assessment, 2021–2023:** https://www.ofgem.gov.uk/sites/default/files/2024-07/Energy_Ombudsman_performance_for_the_period_2021-2023.pdf
  - 206,000 received and 88,375 within scope for calendar 2022.
  - 213,612 received and 126,426 within scope for Jul 2022 to Jun 2023.
  - No category data. Treat these with caution, for two reasons:
    - The 88,375 and 206,000 figures appear in the Trust Alliance Group 2022 report as all-sector, where 206,000 is "consumer enquiries".
    - The Ofgem review's use of them as energy "disputes received" is not clearly consistent with that.
- **2020 annual report (p.07):** https://tag-craft.files.svdcdn.com/production/assets/assets/Annual-Report-2020.pdf
  - Energy disputes fell 11% in 2020. No absolute figure and no category split.
  - Two other figures in the same report disagree: 65,593 disputes resolved in total (p.07) and 92,172 dispute resolutions for energy plus communications (p.16). The report does not reconcile them.
- **2022 annual report (p.9, p.22):** https://tag-craft.files.svdcdn.com/production/assets/assets/2022-Annual-Report-v2.pdf
  - Energy disputes up 24% in 2022. No absolute number and no category split.

### Still open for V6

- **2021 report:** the TAG 2021 report is listed on the annual reports page but not surfaced in search, so not fetched.
- **Energy sector reports for 2020–2022:** none exist on the annual reports page (the sector reports stop at 2019).
- **Absolute accepted-case counts and category shares for 2020–2022:** not found anywhere. The oldest quarterly pack remains 2023.
- **Category shares for 2016–2017, and for 2019:** the PDFs may print them as chart text the summariser did not pair. A local pdftotext extraction would settle this. Curl cannot reach the host, so this needs another route.
- **Energy Ombudsman "Reports and Data" quarterly data for 2023 Q1 onward** are already covered by §1.1 of the theme map.

## What each gap now has and what remains open

**V1**
- Has: the full Jan 2026 findings with contact reasons, complaint reasons, handling and resolution, and a four-wave complaint-reason and handling series (Aug/Sep 2023 to Jan 2026). It also has a 2018–2021 series on customer service satisfaction and ease of contact (Q4'18 to Q3'21).
- Corrected: the 22% figure is an inference, and "smart meter problems are the most common complaint" is not stated in the report.
- Open: the ECSS waves before Aug 2023, the Jul/Aug 2025 report, and any like-for-like series.
- Caution: every complaint base is 89–149.

**V2**
- Has: the top-five lists and shares from British Gas, EDF, E.ON Next, Octopus (counts), OVO (rank only), Utilita (undated) and "E". It also has Ofgem's complaint definition and the 18-category template.
- Open: ScottishPower, Utility Warehouse and So Energy pages, and back series.
- Note: Customer Service is 33–50% at four suppliers, against 7–14% in Ombudsman disputes.

**V3**
- Has: 94,201 warrant installs in calendar 2022 with supplier shares (DESNZ), and the Ofgem review scope (over 150,000 reviewed, assessment period 1 Jan 2022 to 31 Jan 2023). It also has the compensation by category (46,027 customers, £7,037,003) and the post-rule picture. That picture is a 36% fall in severe self-disconnection (indicative), smart PAYG at 81% of installs and satisfaction of 72%.
- Open: self-disconnection and rationing rates by group (probably in the two Citizens Advice PDFs, which I could not fetch), per-supplier warrant and remote-switch counts, and the Ofgem 2023 investigation documents.

**V6**
- Has: contacts, resolved counts and upheld shares for 2016–2019, a billing share above 60% for 2018, ranked top categories for 2017–2019, and total volumes for 2019–2022.
- Open: category shares for most years, absolute 2020–2022 accepted counts, and the TAG 2021 report.

## Possible items for memory

- **Where the primary sources can and cannot be reached:** curl to ofgem.gov.uk is blocked by the proxy (403), so WebFetch is the route for Ofgem PDFs.
- **Citizens Advice PDFs:** assets.ctfassets.net is off WebFetch's allowlist, which blocked the Future of Prepayment and Hitting the Rationing Wall PDFs.
- **Ombudsman Services energy sector reports:** they sit on tag-craft.files.svdcdn.com and were fetchable only after a web search surfaced each URL.

I did not save any of this.
## Done

2026-11-23, delivery seat. The advisor's reading, acted on in order:
1. **The two §1.2 lines are corrected** in `docs/market_research/customer_voice_theme_map_gb_energy_2026-11-21.md`
   (and the three places that repeated them, §2.2, §3 and §3.1): "smart meter problems are the most common
   complaint" is not stated (smart is 31%, second to net billing 70%, Fig. 39, n=96; meter reading 16% leads
   contact reasons, Fig. 25), and the 22% is an inference graded S; the P figure for "passed to another
   organisation" is 10% (Fig. 49). §6 now points here for V1-V6.
2. and 4. **Filed** as `end-of-fix-default-is-rational-when-fixes-price-above-the-cap` in
   `customer_outcomes_candidates` (`docs/direction/priority_order.yaml`), carrying the front-line versus
   Ombudsman population point.
3. **Filed** as `a-home-move-seeds-an-unnamed-account-and-its-debt` in the same list. The 20-40% is graded S
   in Pack B's own table (supplier-reported, quoted in an Ofgem call for input), not P.
No world or supplier parameter rests on any figure here yet: each is verified against its primary first.
