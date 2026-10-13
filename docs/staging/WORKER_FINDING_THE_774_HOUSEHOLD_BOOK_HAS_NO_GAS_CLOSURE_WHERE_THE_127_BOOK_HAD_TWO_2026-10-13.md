**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# The 774-household book has no gas closure; the 127-household book had two

*Worker tick, 2026-10-13 ~18:40Z. Found while clearing the publish gate. Not yet explained.*

**What was measured.** `tools/generate_explore_carbon.py::household_years` treats a household as a gas closure when
its gas leg's last bill ends before its electricity leg's last bill. I counted these over two published books.

| Book | Households | Dual-fuel households | Gas closures |
|---|---|---|---|
| HEAD feed (`customers.json` of 2026-10-05) | 127 | 64 | 2 |
| Run `run_complete_20261013T134447Z` (`customers.json` of 2026-10-13T18:22Z) | 774 | 215 | 0 |

- Both closures in the old book have cause `unknown`: C1 (2018) and PROS-2016-0024 (2021).
- In the new book, 212 dual-fuel households end gas and electricity on the same date, and 3 end gas *after*
  electricity.

**How unusual is zero.** Take the old rate with a Jeffreys prior, Beta(2.5, 62.5). The predictive probability of no
closures in 215 dual-fuel households is about 2%. That is suspicious, but two events is too few to settle it.

**What it cost.** `site/test_explore_second_clock.py::test_an_unexplained_gas_closure_is_shown_plainly_and_claims_nothing`
required the live book to contain a closure. On this run it refused the publish commit. The test now builds a closure
from the generator's own legs when the book has none, so the page branch is still exercised. Whether the world should
produce closures is a separate question, and it is open.

**Explanations to rank. None has been tested yet.**
- (a) The world or company now moves a dual-fuel household's two legs together, so a gas-only loss can no longer
  happen. A real supplier does see gas-only losses: a household moves its gas elsewhere, or has its gas capped off.
  If (a) is true, it is a fidelity gap.
- (b) The old two were artefacts, for example a gas leg cut short by a run boundary, and the new book is right.
- (c) Chance.

**The test that decides it.** In the run's event log, count `churned` events on gas legs whose household's
electricity leg stays on the book. Run the same count at the commit that produced the 127-household book. If (a) is
true, the new count is zero by construction, and the departure code says why.
