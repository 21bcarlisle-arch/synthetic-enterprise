**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# N19 item (3): the five two-register default bills still over the cap are two mixed-term bills graded as all-SVT, and three EPG bills graded against an EPG level nobody published (2026-11-04)

*LATENT, not BLOCKING: N19 holds the block until a fresh book shows the page note gone, and this file carries the two fixes it owes.*

**What this answers.** Owed item (3) of BLOCKING N19
(`SEAT_FINDING_THE_EIGHTH_COLD_READ_FINDS_TWO_REGISTER_DEFAULT_BILLS_GRADED_AGAINST_THE_SINGLE_RATE_CAP_SO_THE_PAGE_PRINTS_FALSE_CAP_BREACHES_2026-11-04.md`).
After the N19 re-grade, five Economy 7 default bills on the 4669d77ddd run output were still over. None of
them was attributed.

**Read on.** These come from the run output `docs/reports/run_output_4669d77ddd_20261104T132452Z.json`, its
ledger `/var/tmp/n15-post-ba86/ledger.json`, and the shared tree's in-flight
`default_tariff_invoice_excess_p_per_kwh`. All amounts are ex-VAT unless marked.

## Pre-registered before measuring (15:55 GMT), kept beside the result

| | Prediction | Result |
|---|---|---|
| P1 | PROS-2021-0282, Apr–Jun 2023: the EPG-scaled ceiling sits under what the world charged. | **Right, but for a reason I did not name.** See class B. |
| P2 | SYN-2016-592, Dec 2023: the bill straddles 1 Jan 2024. | **Wrong.** It straddles a term change on 13 Dec, not a cap window. See class A. |
| P3 | SYN-2016-380, Aug 2024: best guess a straddled window or a mid-period term change. | **Right** (a term change). |

## Class A, 2 bills: a bill that straddles SVT then fixed is graded as if it were all SVT

**SYN-2016-592, 1–31 Dec 2023, 0.48p over.**
- The bill holds two terms: the SVT to 12 Dec, then a fixed tariff from 13 Dec.
- The SVT part is 24.241p Day and 7.153p Night. Weighted 58/42 that is 17.064p, plus 8.000p non-commodity,
  giving 25.064p.
- The multi-register cap for Oct–Dec 2023 is 26.318p inc VAT, which is 25.065p ex-VAT. The SVT part is **at
  the cap**.
- The fixed part (Day 33.33p / Night 15.66p all-in) lifts the whole bill. A fixed tariff is not a default
  tariff, and the cap does not bind it.

**SYN-2016-380, 1–31 Aug 2024, 0.33p over.**
- Same shape: the SVT runs 1 Jul to 19 Aug, then a fixed tariff starts on 20 Aug.
- The SVT term's 58/42 rate is 19.958p, against a cap of 20.956p inc VAT (19.958p ex-VAT). It is **at the
  cap** exactly.

**Cause.** The grade takes the bill's single `term_tariff_type` from `term_of_bill`
(`tools/generate_billing_ledger.py:622`) and divides the WHOLE bill's charge by the whole bill's kWh.
- The bill already carries `rate_lines`, one per term. It prints them, and the run output records each
  line's `term_start`, kWh and charge.
- Graded per default-term rate line, both bills pass.
- This is the same class as the 626: the right ceiling, the wrong quantity in the numerator.

**Fix owed.** Grade only the default-term rate lines of a mixed-term bill. A rate line carries one blended
unit charge and no per-register split, so an E7 line is graded through its term's
`tou_unit_rates` at 58/42. The other reading is to leave a mixed-term bill ungraded (None), named as such.
This goes in `company/compliance/domain_invariants.py`, after the in-flight N19 landing has landed.

## Class B, 3 bills: under the EPG an E7 household is charged the SINGLE-RATE guarantee at its 58/42 blend

**PROS-2021-0282, Apr, May and Jun 2023, each 0.56p over.**
- The SVT term is Day 60.211p and Night 28.299p, a blend of 46.808p.
- The household is charged Day 37.784p + 8.000p and Night 5.872p + 8.000p.
- Weighted 58/42 that is **32.381p ex-VAT, 34.00p inc VAT: exactly the single-rate EPG.**
- The EPG discount is the same 14.427p on both registers. That is the term's blend less the single-rate EPG.
- The company's multi-register ceiling under the EPG is the EPG scaled by the cap's multi/single ratio,
  33.438p inc VAT. That scaling is `ofgem_price_cap.get_multi_register_cap_unit_rate_for_date`, an
  unwitnessed reading and said so in its comment.

**Where it happens.** `saas/bill_generator.tou_registers` subtracts the bill's EPG receipt from each band
at one flat per-kWh rate. So the receipt alone decides where the E7 blend lands, and it lands on the
single-rate guarantee.

**The page shows the same thing worse.** In Jan–Mar 2023 the same rule prints a **Night energy rate of
−0.587p/kWh** on PROS-2021-0282's bills (`site/data/customers/PROS-2021-0282.json`, Feb and Mar 2023). The
all-in Night rate is positive (about 7.4p), because the 8.0p non-commodity line is carved out after the
discount. A pricing reader will still object to a negative energy rate on a bill.

**What decides it, and the prediction refuted.**
- This seat predicted class B was a real overcharge of an E7 household under the EPG. **The blind row
  refutes that.**
- `INV_DEFAULT_TARIFF_TWO_REGISTER_INVOICE_WITHIN_MULTI_REGISTER_CAP` was written by an agent that opened
  only the commons, the market research and the knowledge pages. It found **no published multi-register
  or Economy 7 EPG level**:
  - `ofgem_default_tariff_cap_windows.json` carries only the single-rate `elec_epg`;
  - `ofgem_cap_multi_register_unit_rates.json#basis.epg` says the level "is not carried here";
  - GOV.UK, quoted in `a_storage_heated_homes_default_tariff_is_two_rate.md` R4, says suppliers set the
    E7 discounts themselves and publishes single-rate figures only.
- The row therefore grades EPG windows against the multi-register cap alone. On that bound,
  PROS-2021-0282's 32.38p sits well under 47.12p: **within**.
- So the company's own ceiling, `ofgem_price_cap.get_multi_register_cap_unit_rate_for_date`
  (the EPG scaled by the cap's ratio), is a **constructed bound stricter than anything published**. Its
  own comment says it is unwitnessed.

**Fix owed (class B).** Inside 2022-10-01..2023-06-30, the household grade of a multi-register bill uses
the multi-register cap, with no EPG bound. A named GAP replaces the scaled EPG.
- **Not done here.** That function also feeds `renewal_rate_chain`, so the change is a pricing change
  and needs K8 first: amend `a_storage_heated_homes_default_tariff_is_two_rate.md`.
- The negative printed Night energy rate is a separate page-quality objection. It stays open.

## The blind rows, as wired (this landing)

Both rows are measured over the published 0a6391d186 pages and their ledger, `docs/state/billing_ledger.json`.
They were pre-registered at /var/tmp/n19trace/PREREG.md before the run.

**`INV_DEFAULT_TARIFF_TWO_REGISTER_INVOICE_WITHIN_MULTI_REGISTER_CAP`: CLEAN.**
- 881 bills graded, 0 breached, 0 flagged.
- Not graded: 573 not on a default term, 268 pre-cap, and 81 spanning a term change.
- Predicted: 0 breaches. **Held.**

**`INV_PAGE_CAP_BREACH_NOTE_AGREES_WITH_THE_MULTI_REGISTER_GRADE`: BREACHED 31, FLAGGED 50.**
- The pages print 86 notes on E7 SVT bills:
  - 31 are on bills within the multi-register cap: case (a), a false note;
  - 50 are within the ceiling's 1.5% derivation band: case (d);
  - 5 are on bills not graded.
- **None agrees with the multi-register grade.**
- Predicted: case (a) "in the hundreds". **Wrong on size.** These pages print 86 notes; the 626 was the
  b3ce2a4e73 book's count of flagged bills, not of printed notes.
- This is the page defect the cold reader found, and the row now catches it. It should read 0 on the
  first book graded after the N19 household fix lands.

## Reverse

Delete this file. Nothing outside `docs/staging/` was touched.

## Progress (worker, 2026-11-04): class A fixed; class B and one post-publish read still owed

- **Class A is fixed.** `tools/grade_svt_invoices_over_ceiling.bill_excess(b, type, terms)` returns None for a
  bill a fixed term starts inside. Both the ledger and the book grader pass the terms.
  - The owed spec named rate-line grading as the alternative. It was not taken: a rate line carries no
    register split.
  - A ledger replay of 4669d77ddd records **3** excesses, all class B.
  - Control: `tests/tools/test_grade_svt_invoices_over_ceiling.py::test_a_bill_a_fixed_term_starts_inside_is_not_graded_as_all_svt`.
- **Still owed:**
  - (B) The EPG-window multi-register ceiling, K8 first, as specified above.
  - On the first publish after this landing, read three things: the cast's renewal slot (SYN-2016-592), the
    storage slot (PROS-2020-0189), and `INV_PAGE_CAP_BREACH_NOTE_AGREES_WITH_THE_MULTI_REGISTER_GRADE`. All
    three should read 0, except notes on class B bills.

## Progress (delivery seat, 2026-11-07): class B fixed in the company's grade

- `company.compliance.domain_invariants.default_tariff_invoice_excess_p_per_kwh` now grades a two-register
  bill against `get_multi_register_cap_unit_rate_for_date(on, net_of_epg=False)`: the published
  multi-register cap, with no scaled EPG. A single-register bill keeps min(cap, EPG). The change was
  scoped to the grade alone, so `ofgem_price_cap` and `renewal_rate_chain` are untouched and no price moves.
  K8: the choice and the GAP are on `a_storage_heated_homes_default_tariff_is_two_rate.md`, in the 7 Nov
  section.
- Control: `test_an_economy_7_bill_under_the_epg_is_graded_against_the_published_multi_register_cap`
  names PROS-2021-0282's Apr 2023 bill. It was red before the change and is green after it. Its leg 3% over
  the cap shows the branch can still refuse.
- Replay on the 8c7489e0d9 run output, predicted before it was run: the household-ceiling excesses go from
  3 to 0 (PROS-2021-0282, Apr, May and Jun 2023, 0.562p each). No other bill's grade moves, out of 23,783
  graded. The ledger's page note reads this function through `bill_excess`, so the cap-note row should
  read 0 on the next fresh book.
- **Still open:** PROS-2021-0282's printed negative Night energy rate in Feb and Mar 2023, and the
  post-publish read of the three slots named above.
