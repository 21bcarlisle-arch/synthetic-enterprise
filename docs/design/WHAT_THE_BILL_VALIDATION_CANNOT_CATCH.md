# What the independent bill validation cannot catch

*Work item 6 of `DIRECTOR_BRIEF_INDEPENDENT_BILL_VALIDATION_2026-09-02`: "a plain statement of what
the design cannot catch". Written 2026-09-02, the same day items 1–3 were built, deliberately
before anyone has had time to over-read the result.*

---

## The result this document exists to bound

On the real book, 2026-09-02:

| | |
|---|---:|
| periods where energy + standing charge were rebuilt from raw facts and agree to the penny | **11,549 / 11,549** |
| bills whose VAT matches the rate the published law gives | **11,549 / 11,549** |
| bills whose stored total equals the sum of its own printed components | **11,549 / 11,549** |
| accounts whose event-walk closing balance equals the ledger's own | **251 / 251** |

Read carelessly that says *the bills are right*. It does not say that. It says **two of five money
lines were recomputed independently, one rate was confirmed against the published record, and two
internal consistency properties hold.** What follows is everything that sits outside those four
rows.

---

## 1. The rates are ours, so a wrong rate is invisible

The reconstruction is fed `unit_rate_p_per_kwh` and `standing_charge_gbp_per_day` from our own
export, because a bill cannot be rebuilt without knowing what the account was contracted to pay.
So it validates **the arithmetic over the rates, not the rates**. A tariff whose unit rate was
mis-set by a factor of ten reconstructs perfectly.

This is the brief's own §3 concern and it is the largest hole in the design. Nothing here closes
it. Two things would narrow it, neither built:

* **check the rates against the published record.** Only partly possible: the Ofgem default tariff
  cap is in the commons (`ofgem_default_tariff_cap_windows.json`) and bounds an SVT account's unit
  rate and standing charge in a cap window. A fixed-tariff account has no published rate to check
  against, ever — that price was a commercial decision, not a published fact.
* **conservation checks that use no rates at all** — volume in equals volume billed, money billed
  equals money owed plus money paid. They encode no domain knowledge, so they cannot share a
  domain error with the biller. This is the strongest unbuilt idea in the design and it is not in
  items 1–5.

## 2. The largest pass-through line is not checked at all

`non_commodity_amount_gbp` bundles DUoS, TNUoS, BSUoS, RO, FiT, CfD, CM and smart metering. The
bill does not record the rate it used, and the commons carries only two of those components
(`ro_obligation_and_buyout.json`, `ccl_main_rates.json`). Our own source cites *"Ofgem Retail
Market Monitoring / Cornwall Insight"* — a named source, not a fetchable artefact.

The validator reports this line `UNCHECKABLE`. On a typical resi bill it is roughly a fifth to a
quarter of the pre-VAT total, so **a material fraction of every bill in the book has never been
independently checked and cannot be with what is on this machine.**

And because VAT's base includes that line, the VAT **amount** is unreconstructible too. Only the
**rate** is checked. A VAT error that is a rate error would be caught; one that is a base error
would not.

## 3. What the internal checks are, and are not

*Total equals the sum of its parts* and *the event walk closes where the ledger says* are checks of
**self-consistency**. They would pass unchanged on a book that was uniformly wrong — every bill
computed with the same mistaken rate is perfectly self-consistent. They catch a broken adder, a
dropped line, a mis-ordered ledger. They cannot catch a wrong premise.

Their value is real but narrow: they are the floor that made the *first* draft of the statement
export report 966 phantom failures, and the floor that would catch a regression tomorrow.

## 4. The reconstruction cannot do restatements, and does not pretend to

966 bills carry a catch-up correction: a real read arrives, a run of estimated bills is
re-billed, and the difference is folded into the current bill. A reconstruction from meter
readings must reproduce that by **re-billing the earlier periods**, not by adding a line — it has
to model when an estimate was superseded and by how much. The validator does not, so those 966
bills are checked only on their period charges.

Two traps live here and both are documented in code rather than left as knowledge:

* the catch-up amount is **VAT-inclusive** (a difference of gross totals), while the four period
  charges are net. A reconstruction assuming a single basis reports a VAT shortfall on all 966.
* the Ofgem SLC 31A back-billing cap means some money the meter says was used **may not lawfully be
  recovered**. A reconstruction that rebuilt from consumption alone would "find" that money missing
  and be wrong about it.

## 5. Assumptions that are true today and are not guaranteed

* **Single-register meters.** All 11,549 bills carry one register. Readings are recorded per
  invoice and registers per bill line, so with two registers there is no way to attribute a reading
  to a register. The export declares that case `unattributable` and exports no readings rather than
  guessing — so a multi-register book would silently lose reconstruction coverage rather than fail
  loudly. **The count of `volume_basis: reads` periods is the thing to watch**, and it is asserted
  with a floor.
* **Readings are exact.** `closing - opening == consumption` on 11,549 of 11,549 today. If that
  ever stops holding, the readings have become something other than cumulative indices and the
  export is no longer raw. Asserted.
* **One ledger.** Everything here reads `docs/state/billing_ledger.json`, which is generated from a
  run. A defect in the *generation* of that ledger — as opposed to in the billing — is upstream of
  every check in this design and is invisible to all of them.

## 6. What the curtain does and does not prove

`tools/independent_bill_validator.py` imports no repository code, checked from its own AST
including function-local imports, mutation-proven. That proves the second computation does not
*inherit* the first one's implementation.

It does not prove independence of **belief**. The same author wrote both, on the same reading of
how a bill works, in the same afternoon. A shared misunderstanding of the domain — the half-month
direct debit is this project's own recent example — passes through a curtain untouched. The third
side of knowledge (`feedback_knowledge_has_a_third_side_a_practitioner`) is the only guard against
that, and it is a person, not a control.

## 7. Not yet built

Items 4 and 5 of the brief: the comparison that files every difference with the validator winning
by default, and running it on every account on every run rather than by hand. Until item 5 lands,
**these figures are a measurement taken once, not a control that fires** — and this document is the
only thing standing between that fact and a reader who sees 11,549 / 11,549.
