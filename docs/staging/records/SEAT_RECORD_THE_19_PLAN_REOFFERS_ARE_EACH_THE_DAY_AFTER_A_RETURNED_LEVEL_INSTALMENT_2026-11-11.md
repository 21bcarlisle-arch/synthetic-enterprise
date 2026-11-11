**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Record: each of the 19 plan re-offers with no bill due is the day after a returned level instalment (2026-11-11)

Lane-0 item `the-19-plan-reoffers-with-no-bill-due-are-traced-to-their-trigger`, handed off by b4ddeade03's record
(`SEAT_RECORD_THE_SLACK_DOMAIN_INVARIANT_CEILINGS_ARE_RETIRED_OR_REBASED_2026-11-11.md`). It serves step 4 of the
director's ruling of 26 Oct, which requires zero unexplained breaches. It does not discharge that ruling.

**Premise re-measured at draw.** 068b5e3cc8 and e1587ec5b are on origin/main. The exception still stood at 19 on
origin/main (b4ddeade03), so the work was not spent.

**What "done" means.** Trace each of the 19 to its trigger day, then settle which hypothesis holds:
- (i) the row is too narrow;
- (ii) the desk re-offers on a day it should not.

Then correct the side that is wrong, grade it, and retire the exception.

## The trace

For each breach I joined the journey to the payment records of both fuel legs, on the e1587ec5b ledger
(`/var/tmp/eleventh-read/tree/docs/state/billing_ledger.json`). The probe is `/tmp/reoffer19/probe.py`.

- **19 of 19 re-offers fall the day after a level-DD collection of the household returned failed.** That is the
  desk's `returns` set in `collections_journey.advance`: `missed_on` of the collection date.
- **Each is a new month's instalment.** Each has its own invoice number. None is a re-presentation of an instalment
  that had already failed.
- **No re-offer comes from a missed closing statement or leg statement.** Statements feed `missed`, and so they can
  open a journey, but they are not in `unpaid_on`. So they cannot fire a re-offer.
- **Example:** SYN-2016-549 gas. Its instalments of 24 Dec 2018 and 24 Jan 2019 were returned. The desk re-offered
  on 25 Dec and 25 Jan.

## Which side was wrong: the row

SLC 27.5B counts "missed monthly scheduled payments", not bills. A level instalment is a monthly scheduled payment,
so its return is fresh reason to believe under 27.5, and the 27.6 offer is owed again. This is written as a K8
section in `docs/market_research/company_debt_management.md`, "A returned level instalment is a missed scheduled
payment, and the bill it pays is not (2026-11-11)". The section was written before the row was amended, and it
carries its prediction: 0 of 1,248.

The desk was right in all 19, and its code is unchanged. GAP A1 still stands: a second contact one to nine days
after an offer is not ruled out by anything published. Whether a supplier would make it is a practitioner question.

## The row, amended blind

A fresh agent amended `ev_reoffer_follows_a_missed_bill` and the YAML row from that section alone. It did not open
`company/billing`, `simulation/` or the page builders.

**What the amended row reads.** A failed level instalment dated between the previous offer and the re-offer now
counts as a further miss. A failure of the same leg and invoice within 30 days of its first failure is a
re-presentation, and is not counted again (the Bacs passage). An instalment is missed when its paid part is short
of what it asked.

**How the tests were checked.** There are five new test legs, plus a control over all three outcomes. Three
mutations were made, and each went red:
- the outcome test dropped;
- the re-presentation skip dropped;
- the part-paid comparison forced.

## Graded

| book | before | after |
|---|---|---|
| e1587ec5b | 19 of 1,248 | **0 of 1,248** |
| 068b5e3cc8 | 19 of 1,248 | **0 of 1,248** |

The prediction held. The exception is retired. Both books' publisher-gate verdicts are unchanged: the 19 were
excepted before, and they read 0 now.

**Reverse:** restore the exception block and the evaluator from git history.
