# Held work — built, tested, and deliberately not in the tree

Work that is **finished enough to run** and is being kept out of the shared working tree because
landing it would leave other lanes red. Each entry says what blocks it and what restores it.

A held patch is not a shelf. It is a claim that the work is done and the *decision* is not.

---

## DISCHARGED 2026-08-28 — `founder_book_*` (the 80-founder book)

Landed in HEAD. The three artefacts this directory carried are deleted because they are now the
tree: `simulation/live_population.py`, `docs/design/FOUNDER_BOOK.yaml`,
`tests/simulation/test_founder_book.py`.

**What unblocked it was a measurement, not a decision.** The hold said four campaign tests were red
on a question rather than a stale fixture — whether a campaign that keeps paying for quotes after
the budget stops converting is a company defect or fidelity. Running it one variable at a time
showed the question was malformed: the funnel converts at 18.2% against 18.8%, and 335 of the 380
wins were refused by THIS MACHINE's settlement ceiling rather than lost in the market. The ruling,
the split now reported on every `by_year` row, and the wall fix that followed are in
`simulation/net_new_acquisition.py` at `SETTLEMENT_CUSTOMER_YEAR_BUDGET`.

**The lesson for the next hold:** this one was correctly opened and then sat. A held patch is a
claim that the work is done and the decision is not — so the thing that discharges it is usually
the measurement nobody has taken, not more argument about which answer is right.

**And a second lesson, which cost more than the first.** "Done enough to run" was not true, and the
hold is what hid it. While the patch sat out of the tree nobody ran the one measurement that
mattered — *is the thing the director bought actually delivered?* — because the tests it shipped
with all passed. They passed because they pinned `_pre_growth_book`, which is what the campaign
PLANS against, and nothing pinned `live_population`, which is what the company SERVES. So 67 of the
80 founders were charged for (800 of 1,200 customer-years, refusing 335 of the campaign's own
funnel wins) and never reached the book: the act bought to make the book deeper was making it four
times shallower (398 → 100) for six extra deep accounts. **A held patch's tests are the
least-reviewed in the repository** — written against a tree nobody else is running — and the exit
measurement for a curriculum act is the DELIVERABLE, not the mechanism.

---

*Nothing is currently held.*
