# Does a bill-shock EVENT raise the odds a GB household shops? No published source gives the amplitude

**Knowledge:** how-households-choose

*Filed under choosing because the question is whether a household enters a choice process, which
is engagement rather than price response (PB4's title). It is deliberately not filed under the
bill-shock page: that page defines what the event IS, and this document asks what the event DOES.*

**Research completed 2026-09-29, autonomous worker on a scheduled tick.** Subject:
`simulation/household_segments.BILL_SHOCK_ENGAGEMENT_MULTIPLIER`, a declared `None` since
`2cb273bca` (2026-09-24), which refuses a shocked household and names this gap rather than hand
back the unmodified probability. The PB4 `level_hold_note` puts residual (b) as *"the amplitude,
which is a RESEARCH question and not a build one. Do not close it by picking a number to clear the
refusal."* This is the pass that went looking.

**Outcome: NOT ESTABLISHED, and now searched.** The constant stays `None`. Nothing below may be
used to fill it, and §3 says why each near-miss fails.

---

## 1. What the quantity is, stated before anything was looked up

It is a **within-household response to an event**: the probability that a household shops (compares
or switches) in a window after a bill shock, divided by the probability that the same kind of
household shops in a window with no shock. `what_bill_shock_is.md` settles that the event is
different for different populations, so there are really two amplitudes:

| Population | The event | Share of book (that doc) |
|---|---|---|
| Level direct debit | a material change in the DD payment, or a balance the household does not understand | ~74% |
| Standard credit | the bill itself | ~13% |

It is **not** any of these, and evidence for them cannot stand in for it:
- a ratio over a standing **state** (in arrears, finds bills hard, pays by DD). CIM w6 Table 56's
  1.6×/1.7× are this, and are already rejected in the gap string;
- the **level** of a bill. Refuted 2026-09-22 (`is_there_a_bill_level_at_which_switching_rises.md` §6);
- the **between-household spread** of a lasting trait (`household_switching_response_amplitude.md`);
- the **share of shoppers who name** an event as their prompt. That is P(event | shopped), the
  opposite conditional from the one we need (§3.1).

## 2. Where we looked

| # | Source | What it measures | Result |
|---|---|---|---|
| 1 | Ofgem, *Consumer Engagement in the Energy Market 2017*, §5.7 pp.55–57 (n=4,001, fieldwork Mar–Apr 2017) | what prompted households that engaged in the last 12 months (they recall and name it themselves) | wrong conditional (§3.1) |
| 2 | same survey, p.57 | how often households switched, split by other kinds of contact | right direction, wrong events (§3.2) |
| 3 | He & Reiner, *Why Do More British Consumers Not Switch Energy Suppliers?*, EPRG WP 1515 (Sept 2015), GB survey, logit | who switches, from one survey snapshot, by attitude, payment method and bill size | no event variable (§3.3) |
| 4 | Energy UK / ElectraLink monthly switching series; supplier price-rise announcements (e.g. British Gas, Nov 2013 and 2017) | total switching volume over time | cannot identify the effect (§3.4) |
| 5 | already searched by earlier passes: Ofgem CIM w6 Table 56; Ofgem/BMG *Understanding Consumers' Energy Tariff Choices* 2024; DESNZ QEP 2.7.1 | states, bill level, whole-market volume | rejected by those passes; not reopened |

A targeted search for a household-level event study of UK energy price notices or bill changes on
switching turned up none.

## 3. Why each near-miss cannot supply the number

### 3.1 The 2017 prompt shares: the wrong conditional, with no denominator for turning it round

Of those who engaged, 52% said supplier communications prompted them: **end of fixed-term notice
18%, price increase notice 17%, a bill or statement 12%**. Among supplier switchers the price
increase notice was the most common prompt (17%). Among tariff switchers, the end-of-term notice
was named by 36%.

Each of these is P(named prompt | engaged). The amplitude needs P(engaged | event) against
P(engaged | no event). Bayes can turn one into the other only with P(event received in 12 months),
and the survey does not publish it. Supplying that figure ourselves would be exactly the invented
number the refusal is there to stop. There are two further mismatches even with a denominator:
- a *price increase notice* is a supplier's tariff event. It is not the DD-payment change that
  `what_bill_shock_is.md` defines for the 74%, although the two often arrive together;
- *a bill or statement* is any bill. For the standard-credit 13% the bill is the shock, but the
  survey does not separate a shocking bill from an ordinary one.

The survey's own footnote 19 backs the definition we already use and does not size it: *"many
consumers focus purely on their monthly (weekly/quarterly) payment."*

### 3.2 The 2017 conditional switching rates: the right direction, but other events and no causal separation

These are P(switched | contact) against P(switched | no contact), which is the shape we want:

| Contact in the last 12 months | Switched | Did not have the contact |
|---|---|---|
| complained | 33% | 16% |
| contacted by another supplier | 24% | 17% |
| read any communication from own supplier | 21% | 16% |
| recommendation from family or friends | 28% | 16% |

None of these is a bill shock. All four come from one survey snapshot, and the causation can run
backwards: someone switching reads more communications and is more likely to be contacted, so the
contact can be a result of the switch rather than its cause. A ratio of about 1.3–2× for *other*
events should not be carried over to this one. Doing so would repeat the Table 56 mistake with a
different table.

### 3.3 He & Reiner (2015): cross-sectional states only

Their significant predictors are attention to the energy-price debate (an attitude), finding bills
hard to understand, paying by direct debit (more likely to switch than standard credit), and a
larger monthly electricity bill (a level). There is no event variable. Their bill-size result is a
level effect, and the larger 2024 Ofgem/BMG sample has already put spend-to-switching close to
zero, so it does not reopen the refuted knee.

### 3.4 The aggregate series: no identification

Monthly switching moves with supplier price-rise announcements, but a whole-market series cannot
separate the letter from the media coverage around it or from the price-cap headline, and it has
no household-level denominator. 2022 shows the series can run the opposite way to bills (QEP 2.7.1:
switching 15.57% → 3.06% while every bill rose), because the market had nothing cheaper to switch
to. That also backs the PB4 brief's design choice that the gate takes the **comparison offer** as
an argument: a shock with nothing better available should move nothing.

## 4. What this changes

- **Code: nothing.** `BILL_SHOCK_ENGAGEMENT_MULTIPLIER` stays `None` and the refusal stands. Its
  gap string's claim *"no source gives it"* is now backed by a search rather than asserted.
- **The residual narrows to two routes, both outside the published record:**
  1. **Practitioner (the third side).** A supplier's retention team would see this directly: the
     rate of outbound switch requests in the 30–60 days after a DD-review letter that raised the
     payment, compared with letters that did not. This is ordinary in-house data that nobody
     publishes. Put to the director as a practitioner question, not as a number to adopt.
  2. **The company's own book, company-side.** This is the PB7 pattern. The company sees its own DD
     reviews and its own losses, so it can learn the response from its own ledger once the world
     carries one. That is circular until the world has an amplitude, which is why the world side
     has to stay a declared gap rather than be seeded from the company's estimate.
- **Do not** close the gap with any figure in §3. Every one of them measures a different quantity.

## Sources

- Ofgem (2017), *Consumer Engagement in the Energy Market 2017*, Ipsos MORI for Ofgem, §5.7 —
  https://www.ofgem.gov.uk/sites/default/files/docs/2017/10/consumer_engagement_survey_2017_report.pdf
- He, X. and Reiner, D. (2015), *Why Do More British Consumers Not Switch Energy Suppliers? The
  Role of Individual Attitudes*, EPRG Working Paper 1515 —
  https://www.jbs.cam.ac.uk/wp-content/uploads/2023/12/eprg-wp1515.pdf
- Prior passes whose sources are not repeated here: `what_bill_shock_is.md`,
  `is_there_a_bill_level_at_which_switching_rises.md`,
  `what_a_supplier_can_observe_about_switching_propensity_cim_w6.md`.
