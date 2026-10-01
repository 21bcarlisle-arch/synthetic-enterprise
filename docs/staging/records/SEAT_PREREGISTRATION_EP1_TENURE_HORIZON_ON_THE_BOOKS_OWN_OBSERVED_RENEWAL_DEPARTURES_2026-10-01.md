**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon — Lane 0 delivery

# PRE-REGISTRATION — EP1's tenure horizon on the book's own observed renewal departures

Filed 2026-10-01, before the change below has been run on a real book. The finding it serves is EP1
pass 20 (store note, 2026-10-01). That pass showed the gap's whole excess over 1 is the LEVEL of the
lifetime term: a 0.05 published hazard against 0.36 realised at renewal.

## The change being measured

H2 `tenure_expected` stops reading its hazard from the account's latest bill-shock belief
(`saas.churn_model`, base 0.05). It reads the BOOK's observed per-renewal departure frequency,
`departures / decisions`, pooled over every billing account. It is derived only from the company's
own settled records, truncated at each snapshot's cutoff:

- an anniversary the account went on settling PAST counts as **stayed**;
- a ceased account (`ceased_billing_accounts`) whose last settled month IS an anniversary month, or
  is the month before one, counts as **left at that renewal**;
- an anniversary in the account's last settled month while it is still supplied is **undecided**
  (censored) and is not counted;
- a cessation nowhere near an anniversary is not a renewal decision and is not counted.

No world record is read. `customer_events`, which pass 20's diagnostic arm used, carries
`random_roll` and `sim_*` truth and does not cross.

**The prior is `None`, and that is the research result, not a gap in the work.** The only
route-conditioned published instrument is Ofgem's *End of Fixed Term Communications Trial* (2019).
It was run on one LARGE supplier's one-year fixes ending 2019-02-28, with mean tenure 17 years.
Customers who had already acted were excluded. In the control arm, 6% switched EXTERNALLY within six
weeks of term end, 14% switched internally, and 19% switched overall. That is a floor for an
incumbent's residual inert book. It is not a prior for a small supplier whose customers were all
acquired by switching. Ofgem's 2024 *Understanding Consumers' Energy Tariff Choices* survey reports
6% switched supplier over six months, but on ALL households, not conditioned on term end. While the
book has seen no renewal decision, H2 is blank under the named reason `no_book_renewal_decisions`,
and nothing is shrunk toward a picked number.

## Predictions, written before the run

1. **Decision counts.** Over the full window the derived record holds 60–110 decisions, with a
   pooled departure frequency in **0.28–0.45**. Pass 20 counted the world's per-COMMODITY events at
   38/106 = 0.358. The derived record is per BILLING ACCOUNT, so dual-fuel households count once,
   and the count should come out lower than 106.
2. **Agreement with the world, as a check on the derivation and not a target.** The derived
   frequency for each snapshot year sits within ±0.08 of the frequency pass 20 computed from
   `customer_events` at the same cutoff (0.414, 0.333, 0.373, 0.392, 0.414, 0.414 for 2017–2022). A
   larger disagreement means the cessation-to-anniversary mapping is wrong. It does NOT mean the
   world is wrong.
3. **The 2016 snapshot is blank on H2** for every account (`no_book_renewal_decisions`). The book
   was acquired in 2016, and no anniversary can have been decided by 2016-12-31 except month-end
   anniversaries.
4. **Gap.** After `couple_clv --write-ledger`, the gap is 1.0–1.3 (pass 20's arm gave 1.076).
   Spearman between belief and realised moves by at most ±0.05 from +0.110, because one pooled
   number per date carries no per-account information.

If (2) fails, the derivation is the defect and it gets fixed before any ledger row is written.
