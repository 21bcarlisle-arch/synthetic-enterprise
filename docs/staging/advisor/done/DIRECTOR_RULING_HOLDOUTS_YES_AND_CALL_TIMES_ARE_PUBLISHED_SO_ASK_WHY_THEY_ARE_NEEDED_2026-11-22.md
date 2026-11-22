**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-RULING] Retention holdouts: yes. Call times are published, so research them, and say why the supplier needs them

**Type:** RULING and STEER, through the advisor channel. It answers two `for_the_director` rows. The director's words, from chat, Sun 22 Nov 07:48 GMT:

- "Yes to holdbacks. On average call waits, has it properly researched this? This is published by often and citizens advice etc. also why does it need to know it?"

("often" is Ofgem.)

## 1. `b8-s-retention-holdout-needs-two-practitioner`: yes

Build B8's retention holdout default-off at the derived share, as the row recommended. Close the row.

## 2. `practitioner-number-needed-how-long-is-a`: not answered, and sent back

**The research missed published sources.** The row says it searched Ofgem guidance and the data portal, the NI Utility Regulator and supplier reports. It did not search **Citizens Advice**. Citizens Advice publishes supplier performance quarterly, including **average call waiting time** by supplier, with historic star-rating data downloadable. The advisor confirmed that today on citizensadvice.org.uk (Historic Star Rating Data; How the scores are worked out). **Ofgem** has also published supplier customer-service and call-answering data, including during its 2023 customer service work.

Under K4, a question to the director comes only after the page shows the answer is not published. Here that had not been established.

**The director also asked why the supplier needs it.** Answer that first, before any more research. The advisor's reading, for the machine to test:

- **The household's time (M3).** What a household spends on a call is waiting time plus talk time, in household minutes, and it is part of the value created or destroyed. **Waiting time is published.** Use it, by supplier and by year, from Citizens Advice. Talk time is a smaller share and can be a stated range.
- **The supplier's cost to serve.** Handle time times contacts drives staffing. But the price cap's operating-cost allowance already gives a published, sourced cost to serve per customer. **Unless a supplier decision being tested now turns on call staffing, do not build a staffing model.** Use the cap allowance, and leave handle time a labelled GAP.
- **Contacts per customer per year.** Check what Citizens Advice and Ofgem publish: complaints per 10,000, contact volumes in the customer service reviews. Use what is published and leave the rest a GAP.

## What is asked

1. Re-research call waiting, contact rates and handle time against Citizens Advice's historic star-rating data and Ofgem's customer-service publications. Record what each gives.
2. State in one paragraph which current decision needs a call-level figure, if any. If none does, keep the call queue unwired, use published waits for household time and the cap allowance for cost, and close the GAP as "not needed yet", with the condition that would reopen it.
3. **Learning-loop entry:** "a practitioner question raised before the obvious public source was searched". Add Citizens Advice's supplier performance data, and the customer-voice sources in the 21 Nov steer, to the standard search list a GAP must clear before a question reaches the director.

Close the row with this resolution.

## Addendum, Sun 22 Nov 07:49 GMT: assume call time for tricky problems

The director's words: "Ok. I like the idea of assuming call time for tricky problems."

So the household's time is not one average call. It depends on the problem.

- **Tricky problems take much more household time.** Examples: billing errors, catch-up bills, disputed reads, debt and payment plans, smart meter faults, home-move and final-bill mix-ups, refunds. They cost repeat contacts, long waits and long calls, often over weeks. Simple ones cost little: a read, a tariff question, a change of details.
- **Hold it as a stated belief with a range, per problem type:** contacts per problem, wait time from Citizens Advice (published), talk time, and days to resolve. Where nothing is published, the range is the belief. Do not invent a point value.
- **Ground it in the customer-voice coding.** Its "time and effort spent" field records what customers say a problem cost them. Ombudsman cases often state how many contacts preceded escalation. Use those to set and check the ranges.
- **It feeds M3's time need directly,** as household minutes by kind of activity. That makes a supplier that fixes things first time create real value in time, even when no money moves. It is also the evidence behind "how the issue is handled then affects the likelihood to churn".
- **Still no staffing model** unless a current decision needs one. Cost to serve stays on the cap allowance.

## Done

Actioned by a worker tick, 22 Nov 2026.

**1. Holdouts: closed `yes`** in `docs/direction/DIRECTION.yaml`. The commitment is the B8 item
`seat-finding-b8-no-retention-desk-holds-anyone-out-in-the-standing-run-and-the-book-now-says-so-per-desk-and-year`,
due 4 Dec. Done means the blind holdout, drawn before treatment, lands default-off at
`competitive_pressure.save_holdout_share`, withholds the proactive approach only, and a test shows
the switch can be taken.

**2. Call times: closed `returned`, then resolved.** The work is in
`docs/market_research/contact_centre_staffing_cost_and_call_wait_gb_energy_2026-11-21.md` §5a.
- **Why it is needed: nothing needs it now.** The staffing desk and the world's `phone_queue` have
  no caller in any run. The GAP is closed as "not needed yet". It reopens when a decision under
  test varies agent hours or contact-centre spend. Household time uses the published waits, and
  cost to serve uses the cap's operating-cost allowance.
- **The re-search.** Citizens Advice's historic data (charts 1–5 and 8–13) and the methodology
  page, plus Ofgem's customer-service data page, give the wait and complaints but no call volumes,
  contacts per customer or handle time.
- **A correction beside the ruling's premise.** The page had already used Citizens Advice's
  per-supplier call wait since 21 Nov (§2). What it had not done was search Citizens Advice for the
  two figures it asked him for, or say which decision needed them. That second omission was the
  real defect.
- **Learning-loop entry: `docs/institutional/ways_of_working.md` W5.** The standard search list a
  GAP must clear (§5a) adds Citizens Advice's supplier data and the customer-voice sources. The
  question must also name the decision that needs it.
- **The 07:49 addendum: household time per problem type**, tricky problems costing most, held as
  stated ranges. It is placed as commitment `household-time-per-problem-type-ranges`, due 4 Dec.
  It is in the knowledge share of the 23 Nov review, with no staffing model.

The second row is coded `returned` in `DIRECTION.yaml`.

Decision: outside_source yes
