**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `DD_seasonal_cashflow_physics`

# The DD design pile is in the console seat's landing sequence, so this tick did not land a rival copy

**Fate (2026-10-15):** ATOM -- folds into `DD_seasonal_cashflow_physics` (re-pointed 2026-10-15; an ATOM fate names its atom).
**Fate (2026-10-13, clear-the-decks):** ATOM -- 8c7f8c7c3 (this note's own landing) P2 -- note itself landed (disposition only); hands off real open work "dd-own-forecast-forward-split-wired-after-the-pile-lands" (term_end_iso/forward_rate_per_mwh_ex_vat still unwired in tools/dd_book_legs.py, confirmed absent).

*2026-10-13, autonomous worker tick, claim
`the-dd-amount-is-set-from-the-companys-own-twelve-month-forecast-plus-the-balance`.*

**What the draw asked:** land the staged DD hunks (`company/billing/dd_review.py`,
`company/interfaces/dd_review_outcome.py`, the new test, the K8 section) with `isolate_hunks` +
`surgical_land --content`, then wire `build_dd_balance_book`, add a control, file a prediction and
measure.

**What `ps` showed at draw time:** the interactive console session (`22080be5`, alive) is running
`surgical_land` from `/var/tmp/se-hedge` on the first of four staged supplier changes. It is doing
this under the director's 2026-10-13 instruction to finish them. Its commit message says: "One of four finished supplier changes left staged in the shared tree
... the capital, value-arm and DD changes follow, one at a time." It also left the DD's own hunk of
`simulation/run_phase2b.py` out of the hedge landing on purpose ("The third is the DD design's,
which lands on its own"). If I landed the same paths now, two landers would contend for one pile.
The landing is that seat's job.

**What the staged pile already holds (index, read just now; the working tree has no further
unstaged change on these paths):**
- `simulation/dd_balance_book.py` already passes `balance_to_clear_gbp=-balance_entering[w]`
  (from `simple_balance_after_window`) to `reviewed_standing` under `own_forecast_plus_balance`.
  The sign is flipped on purpose, with a comment explaining why. So **the balance leg of the
  caller wiring is built, not owed.**
- `tools/dd_book_legs.py` adds a `balance_recovery` leg and calls the shared
  `priced_annual_inc_vat_at_rates` instead of a mirrored formula.
- **Not wired:** `term_end_iso` / `forward_rate_per_mwh_ex_vat`. Neither caller passes them, so
  the known-to-forward split still degrades to the rates-in-force price on every book the run
  builds. That is the remaining half of the draw's caller ask, and it is not in anyone's pile.

**Disposition:** the landing stays with the console seat. The unwired forward split, its
both-legs-taken control, the review-lag prediction and the three-way measurement are handed off
as `dd-own-forecast-forward-split-wired-after-the-pile-lands`. That item cannot start until the DD
pile is an ancestor of origin/main, because it edits the same two files. This claim is released.
