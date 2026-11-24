**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: the desk's expected terms remaining against the world's realised tenure (24 Nov 2026)

**Filed before the table exists.** Before writing this I had read only the sidecar's key layout and one
renewal record from `/var/tmp/vtn-out/A/member_13131_14141.json`, plus its pooled `auc_population`
(value arm, seed 13131: 765 retained, 40 left at priced renewals). No per-year figure had been computed.
Origin: the BELOW branch's step 2 of `SEAT_PREREG_WHAT_THE_SUPPLIER_DOES_ON_EACH_S12G_OUTCOME_2026-11-23.md`.

## What is measured

Per year 2017-2025, on the value arm of the A, cut and twin runs (book 61118, churn pair 13131/14141):

1. **Desk, renewal-only.** r = renewed / (renewed + left) over the trailing 12 months of the desk's own
   closed renewals; expected terms remaining including the current one = 1 / (1 - r). This is the rule
   the s.12g record names ("learned from its closed renewals").
2. **Desk, every exit.** The same geometric form, but r is one minus the share of accounts the desk lost
   in the trailing 12 months for ANY reason it can see (a renewal departure, a mid-term switch-away, a
   move-out), over the accounts it held. A real supplier sees every loss on its own book.
3. **World, instrument only.** The mean of the world's `p_retain` at the year's renewals (ground truth,
   never a desk input), turned into terms the same way; and the terms each renewing account actually
   went on to complete, flagged where the window censors it.

## Predictions

- **E1.** Desk renewal-only r is above 0.90 in every year with at least 30 closed renewals, so its
  expected terms remaining exceed 10.
- **E2.** Desk every-exit expected terms are below the renewal-only figure in every year, by a factor of
  at least 2 in a majority of years: the book loses more households between renewals than at them.
- **E3.** The renewal-only estimate exceeds the world's `p_retain`-based figure in most years, because
  the renewals the desk closes are the survivors of mid-term exits (selection), not because the desk
  mis-reads them.
- **E4.** 2021-2022 is the lowest year for every column (the crisis).

**Refuted by:** each line read against the printed table. A miss is kept here beside its line.

**Reverse:** nothing to reverse. A record; it changes no code.

## Graded (24 Nov 2026, after the table was printed)

The table and its reading are in `docs/market_research/what_a_kept_household_is_worth_beyond_one_term_2026-11-24.md`
§4 (3,108 closed renewals, A + cut + twin value arms, both seeds; `/var/tmp/kept-hh/table.py`).

- **E1, REFUTED.** r was 0.880 in 2017 and 0.889 in 2018, below 0.90 in 2 of the 7 years that had at
  least 30 closed renewals. In 2019–2025 it held: r was 0.945–1.000.
- **E2, UNGRADEABLE.** No every-exit column can be built from these files. The sidecar counts
  default-tariff segments (`svt_segment_decisions`) but dates no exit except a priced-renewal departure.
  So the desk's every-exit view could not be reconstructed. The nearest reading is the realised
  bracket's LOW. The gap is filed as a GAP on the page (§5), not guessed.
- **E3, NOT GRADED as written.** The world's `p_retain` was not used. On offered events it is a
  post-offer figure whose roll semantics do not reduce to a stay probability: SYN-2016-001 renews at
  roll 0.3631 above p_retain 0.1891. The instrument used instead is realised tenure as a bracket. Read
  against that bracket, the renewal-only estimate does exceed the bracket's LOW in every year 2017–2024,
  so E3's *mechanism* (the desk sees only survivors of exits it cannot see) is consistent. It is not
  established, because HIGH contains the estimate.
- **E4, REFUTED.** 2022 has no closed renewals at all, so it has no rate to be lowest. 2021's r (0.950)
  is among the highest. The crisis shows as the absence of fixes, not as a low retention rate.

Unpredicted and load-bearing: 46% of the intervals between one household's successive fixes are
longer than a term. The unit the s.12g record names ("terms remaining") is therefore wrong for step 2.
The page's §6 names the replacement: the company's own tenure-year life table.
