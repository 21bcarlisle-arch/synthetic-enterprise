**Knowledge:** payments-and-direct-debit

# Why households pay the way they do: Ofgem's CIM Wave 3 tables, derived (2026-11-02)

The first D-graded piece of the customer-needs domain the 30 Oct corpus steer asks for
(`docs/staging/advisor/DIRECTOR_STEER_BUILD_THE_CUSTOMER_KNOWLEDGE_CORPUS_AND_PROPOSE_THE_NEXT_SIM_ADDITIONS_2026-10-30.md`,
Ask 1 and the 16:51 data addendum). It answers one question from the primary tables, not from a summary:
**when a GB household says why it pays by direct debit, standard credit or prepayment, what does it say, and
which of its attributes moves the answer?** It informs both sides. The world's hidden payment-method choice
should reproduce these shares, and a real supplier can ask the same question of its own customers.

**Data.** Ofgem, Consumer Impacts of Market Conditions, Wave 3, fieldwork 21 Nov - 11 Dec 2022, Table 13
(question A15), stored raw with provenance at `data/lake/ofgem_cim_wave3_2022/`. Unweighted base: 3,447 bill
payers on DD, SC or PPM. Every percentage below is the table's weighted column percentage. Every interval is
a 95% normal interval on the table's own **effective** sample size, which allows for the weighting.

**Grades** (16:51 addendum). **D** = derived here from the table. **P** = reported by the body that holds the
data. **S** = a secondary summary. **A** = an assumption, given with a range.

**Not pre-registered.** These tables were read before any prediction was written down, so nothing below is a
test of a prediction. The challenges in section 3 are claims checked against data read after the fact. A
claim this page "corrects" is corrected on this one survey question, not refuted in general.

---

## 1. What each method's payers say (D)

| Reason (multiple allowed) | DD | SC | PPM |
|---|---|---|---|
| Unweighted base | 2,498 | 414 | 530 |
| More convenient | 49.2% | 35.8% | 24.9% |
| Easier to budget | 42.6% | 31.1% | 41.9% |
| Gives me more control | 26.0% | **41.2%** | 33.2% |
| Cheaper than other methods | 24.2% | 14.1% | 10.2% |
| It was the default | 12.3% | 10.9% | **22.0%** |
| My supplier made me | 6.6% | 10.2% | 10.7% |
| Don't know how to change it | 2.8% | 4.4% | 7.0% |
| **Positive reasons (Ofgem's net)** | **88.6%** | **84.5%** | **72.2%** |
| **Negative reasons (Ofgem's net)** | 19.7% | 23.9% | **36.4%** |

This **confirms** the table in `docs/design/CUSTOMER_NEEDS_BEYOND_THREE_CURRENCIES.md` section 2.1, which was read
from the report PDF, to within a point on every cell. **One correction:** that note gives the PPM base as 553. The
data table's unweighted PPM base is **530**, and its weighted base is 521.3.

## 2. GAP-1 closed: how many standard-credit payers knowingly pay for control (D)

The framing note's GAP-1 asked for the joint "SC payer, knows SC costs more, and still chooses it for control". It
called that the cleanest measure of control bought knowingly. Table 13 carries it as two crossbreak columns, and
they are two different definitions, so both are given:

| Definition | Share of SC payers (weighted) | Of them, cite control | So: share of all SC payers |
|---|---|---|---|
| Knows SC is **not the cheapest** method | 33.5% (138.5 of 413.7) | 43.4% ± 8.8 (eff. n 121) | **≈ 14.5%** |
| Knows SC is **the most expensive** method | 13.0% (53.7 of 413.7) | 30.2% ± 13.8 (eff. n 43) | **≈ 3.9%** |
| All SC payers | 100% | 41.2% ± 5.1 (eff. n 361) | 41.2% |

Knowing SC costs more does **not** lower the share citing control. The difference is +2.2pp ± 10.2, so no
measurable effect either way. Between about **one in twenty-five and one in seven** SC payers knowingly pay a
premium they cite control for, depending on what "knowingly" means. For the world, that bounds N4 (control) as a
deliberately bought trait: if it is ever drawn, its share among SC payers lies in that range (D), not at the
41% who merely cite control.

## 3. The advisor's synthesis, checked on this question

| Claim (advisor, 30 Oct packs) | On A15 | Verdict |
|---|---|---|
| **Precarity drives spend control.** Low income and difficulty with bills go with valuing control. | Citing control is flat with income: 28.2% under £16k against 30.1% at £80k+ (−1.9pp ± 8.8), and 28.2% against 29.3% split at £16k (−1.1 ± 4.2). It is **lower** for those behind on bills: 22.5% against 29.7% with no difficulty (−7.3 ± 5.7). | **Corrected for stated control.** On this question precarity does not raise control. It raises *passive* reasons (next row). **Restated 2026-11-02 after Waves 4-6:** the "lower when behind on bills" half was Wave 3 only (Waves 4-6: +2.4 ± 5.4, -1.6 ± 5.8, -0.8 ± 4.9). The stable form is "not higher when behind on bills", in all four waves. |
| **Precarity drives imposed rather than chosen methods.** | Passive ("negative") reasons: 37.4% behind on bills against 18.0% with no difficulty (+19.4 ± 6.1). By income: 23.9% under £16k against 21.2% at £80k+ (+2.6 ± 8.0). | **Confirmed, if precarity is read as difficulty with bills, not income.** Income alone shows no gradient. |
| **Life stage outweighs income.** | Passive reasons are 34.0% at 16-24 against 12.3% at 65-74 (+21.7 ± 6.3), and "more convenient" is 29.7% against 59.5% (−29.8 ± 6.7). Income moves neither measurably. | **Confirmed on this question, with a confound.** Method mix differs by age (the young are more often on PPM), and these are column percentages, not controlled for method. |
| **Trust is a moderator.** | Passive reasons are 28.9% among those who do not trust their supplier to treat them fairly, against 20.3% who do (+8.7 ± 4.2). Positive reasons are 80.3% against 88.5%. | **Supported as an association.** Direction of cause unknown: being put on a method may cause the distrust. |
| **Price is a minor reason** (Ofgem 2024, para 3.19). | "Cheaper" is 20.8% overall, and 10-24% by method. It rises with age (18% at 16-24, 28% at 65-74). | **Confirmed** (D; Ofgem's sentence is P). |

**What this changes for the parsimony ruling.** Of the three candidate latent factors, **life stage** and a
**difficulty-with-bills** form of precarity separate these answers. **Income** does not, on this question. If
the world draws a precarity factor to drive chosen-against-imposed payment, these tables say its observable signal
is arrears and bill difficulty, not income band. One question in one wave is not enough to fix the factor
structure. That needs the cross-tabs on cost, worry and switching (Ask 1, step 3), and it stays open.

## 4. What this page does not establish

- **Causation.** These are cross-sectional column percentages. No cell is controlled for any other.
- **Wave stability.** Wave 3 is the crisis winter of 2022. Waves 4-7 carry the same question and are not read here.
  Whether the shares moved after the EPG is a GAP until they are. **Read 2026-11-02:** see `the_customer_needs_framework_cost_worry_switching_cim_waves_3_6_2026-11-02.md` section 5. Levels are not comparable across Waves 3-4 (the answer list grew by six options); the age, bill-difficulty and passive-reason gradients keep their sign in all four waves and shrink; the trust gradient shrinks from +8.7 to +2.0.
- **Behaviour.** A15 is a stated reason. The stated-against-revealed gap (corpus page 5) applies: a household that
  says "control" may not pay anything for it, and section 2 is the nearest this survey comes to revealed.

## 5. Who reads this

- **World:** a future payment-method draw (the "chosen against imposed prepayment" candidate in Ask 2's roadmap)
  should hit section 1's shares by method and section 3's age and bill-difficulty gradients. Nothing in the world
  reads this page today, and no world value is changed by it.
- **Supplier:** the same question can be asked of its own book (observable). Section 2's 4-15% bounds how many SC
  payers a cheaper-DD nudge is working *against*, rather than merely failing to reach.
