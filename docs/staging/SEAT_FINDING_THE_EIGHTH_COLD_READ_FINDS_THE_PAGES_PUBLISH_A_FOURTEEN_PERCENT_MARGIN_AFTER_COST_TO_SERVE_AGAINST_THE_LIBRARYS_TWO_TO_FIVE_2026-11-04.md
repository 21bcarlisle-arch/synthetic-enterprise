**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `unminted`

# N21. The household pages publish a margin after cost to serve of 14.5% of revenue, three to seven times the 2–5% the invariant library itself states (2026-11-04)

**Source.** Reader objection O35 in the eighth cold read, raised by an Ofgem price-cap analyst
(`records/SEAT_READING_THE_EIGHTH_COLD_READ_ON_THE_B3CE2A4E73_BOOK_2026-11-04.md`). The seat confirmed it over all
1,289 domestic page files of the b3ce2a4e73 book.

**What the pages show.** Each household's "For them" stage prints revenue, gross, net and "net after cost to serve".
- **Book-wide**, `lifetime_net_after_cts_gbp` over `lifetime_revenue_gbp` is **14.5%**. The median account is 12.9%,
  p10 −0.9% and p90 22.6%.
- SYN-2016-531, for example: revenue £4,856.02, gross £3,255.76 (67%), net £1,521.28 (31%), net after cost to serve
  £1,050.96 (21.6%).
- The page also labels the figure before cost to serve as "Net margin" (O35's second half).
- `annual_pnl` carries `revenue_gbp: 0` in every year, beside a non-zero gross and net, on the pages checked.

**Why it is wrong, or needs a definition before it can be read.**
- `company/compliance/domain_invariants.py` holds `NET_MARGIN_PCT_OF_REVENUE` at 0.02–0.05 ("Ofgem Retail Market
  Report; Cornwall Insight").
- The cap's EBIT allowance is about 1.9–2.4% (`docs/domain_artefact_library/regulatory/price_cap_ebit_allowance.md`).
- A supplier billing at the cap, as this book's default tariffs are (named check (a): median 1.000 of the cap),
  cannot keep 14.5% after cost to serve unless a cost line is missing or booked too low.
- The reader also saw booked wholesale of about 6p/kWh on a summer 2023 account (O32), against an energy component
  of 24.36p on the same page.

**I cannot yet say** which of two causes it is:
- "net" omits a cost line: network, policy, the EPG pass-through, or bad debt. That is this project's known
  "net margin" definition failure, now on the page.
- The booked costs themselves are too low.

The first measurement is one account's revenue taken apart line by line against the cap's allowances for the
same periods.

**Say what it is before differencing (CLAUDE.md).** "Net after cost to serve" has to be defined line by line on the
knowledge layer before any bound is set. The library's 2–5% may be a different quantity.

**The row this owes (ruling step 6).** Once the definition is written down, it must be written blind from it and
from the Ofgem Retail Market Report: the book's margin on that definition sits in a sourced two-sided band per
year.

**Reverse.** Delete this file. Nothing outside `docs/staging/` was touched.
