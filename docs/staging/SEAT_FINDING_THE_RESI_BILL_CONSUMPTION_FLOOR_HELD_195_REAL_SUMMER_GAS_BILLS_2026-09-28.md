**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_payment_channel_dd_consistency_invariant`

# FINDING — the per-bill resi consumption FLOOR had no source and held 195 real summer gas bills forever

Claim: `the-held-resi-gas-bills-are-never-issued-and-the-floor-that-holds-them-is-unsourced`. Follows
`SEAT_FINDING_THE_LEDGER_AND_THE_PNL_WRITE_OFF_DISAGREE_ON_HELD_AND_CREDIT_BILLS_2026-09-28.md`.
Duplicate-work note at draw: the "other" live claim is this very id — the draw's own write, same work.

## Measured before any change (2026-09-28, HEAD `2bb03a094`, run output of 2026-09-27 on the shared tree)

`validate_bills` over 10,681 bills holds **203**:

| fuel | side of envelope | reasons | count |
|---|---|---|---:|
| gas | BELOW the floor (`low=100` kWh/30.44 d) | `slc_6_7_billing_accuracy` only | **195** |
| electricity | above the ceiling | `slc_6_7` + `vat_by_segment` | 7 |
| gas | above the ceiling | `slc_6_7` + `vat_by_segment` | 1 |

The 195: 38 accounts, 116 of them July/August, 0.0–~99 kWh per ~31 days, **£2,570.48** of bills.
*(Corrected: the first draft of this line said £7,091.09 — that is all 203 held bills, measured over the
wrong population; the 8 ceiling bills alone carry £4,520.61. Caught by R2 below.)* Typical shape: `SYN-2016-005` gas
Jan 463, Feb 933 … Jun 115, **Jul 42, Aug 42**, Sep 139 kWh — an ordinary seasonal gas curve whose
summer trough the floor cuts off.

### Does the P&L book revenue on a held bill? — NO, the opposite

The double-entry ledger (`company.finance.accounting_close` → `build_ledger(settled, issued_bills)`)
bills only issued bills: `_ledger_headline.total_billed_gbp` **£940,801.21 = £947,892.30 (all bills)
− £7,091.09 (held)**, to the penny. The energy behind a held bill is still settled and costed. So a held
bill is not "100% collection by omission" — it is **energy bought and never billed**: a pure loss on
the management accounts, while the settlement-based commodity figure `total_revenue_gbp` (a separate,
commodity-only measure) does include it. The item's WHY predicted the wrong sign.

### Is the floor established? — NO

- `RESI_CONSUMPTION_ENVELOPE_GAS_MONTHLY.low=100.0` (and elec `low=15.0`) carry
  `source="Calibrated against observed sim population + headroom"` — the sim's own 2026-07-09 minimum
  with a margin. Not a published figure. The comment's stated purpose — catch "an SME-scale account on a
  resi record" — is a CEILING purpose; nothing names what the floor is for.
- The only published lower threshold in the knowledge layer is NEED's **1,000 kWh/YEAR** validity cut
  (`docs/market_research/need_domestic_gas_high_tail.md`), and it is a STATISTICS filter: DESNZ blanks
  those homes from its tables because they exist (cooking-only / not gas-heated), not because a supplier
  refuses to bill them. Scaled per month it is ~83 kWh — and it is an annual floor, not a monthly one.
- Published shape (`docs/market_research/gas_demand_what_drives_it_and_the_term_the_model_is_missing.md`):
  space heating ~75% of domestic gas, hot water 12–25%, cooking 5–10%. A summer month is the non-heating
  base only; a heating-only boiler home with an electric shower has almost none. A void home has zero.
- Practitioner side: a supplier issues a low or zero-consumption bill (standing charge + whatever was
  used). A low read may be queued for a read check; the bill is not withheld forever. **Director: say
  if that is wrong** — it is the one premise here that is industry knowledge rather than published.

## Decision

No published per-bill floor exists, so the code carries none: `low=0.0` on both monthly envelopes,
meaning "only negative consumption is impossible", with the source saying so. The ceilings (the SME
mislabel control) are untouched. Electricity's floor held nothing on this run; it goes for the same
reason (a void home), as a class.

Not done, filed: the model's summer gas base itself (`hot water` term) — the 3 kWh months may be the
SIM missing its hot-water base, which is a fidelity question for the world, not a reason to hold bills.

## Pre-registration (written before the changed gate is run over the real book)

- R1: held 203 → **8** (exactly the 7 elec + 1 gas ceiling/VAT bills).
- R2: issued bills gain **£7,091.09**. *(Registered on the wrong population — see the correction above.)*
- R3: `balance_write_offs` total and the ledger still agree per account (same gate on both sides).
- R4: bad debt rises by more than £0 and at most £500 (≈2% of bills fail, over £7k of small bills).

## Result (same run file, changed gate, one variable)

- R1 **held**: 203 → 8.
- R2 **refuted**: issued bills gain **£2,570.48**, not £7,091.09. The prediction used the all-203 total;
  the 195 floor bills are small (a summer gas month is mostly standing charge).
- R3 **held**: ledger write-off £17,408.04 = P&L £17,408.04; no account disagrees.
- R4 **held**: bad debt +£48.79 (£17,359.26 → £17,408.05), 182 → 187 cases.
- Committed book (`docs/reports/run_output_latest.json`, 2026-09-09): 14 held → 3, so the real-book
  control's held-bill leg is still exercisable.
- Mutations: restoring gas `low=100` reds `test_a_low_or_zero_resi_month_is_issued_not_held_and_only_the_ceiling_holds`;
  restoring elec `low=15` reds it too (the zero-electricity leg). The characterization test that froze
  "a zero-kWh resi bill is held as implausible" is inverted, deliberately.
- Unrelated red seen on the way: `test_the_vat_charged_on_every_catchup_bill_matches_the_NET_base_across_the_real_book`
  (774 < 900 catch-up bills) fails identically with this change reverted — not this change.

## Still open

- The 8 ceiling holds remain never re-issued. They are correct holds (SME-scale load on a resi label);
  re-issue after correction is the unbuilt follow-up named in `company/billing/pre_bill_validation.py`.
- Whether the SIM's 3 kWh summer gas months are the missing hot-water base — a world-fidelity question.
