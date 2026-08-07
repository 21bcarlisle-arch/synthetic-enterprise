# [ADVISOR-SCOPE-BRIEF] — The prepayment estate (2026-08-07)

**Type:** [SCOPE BRIEF — domain-first, written before reading the code]. Roughly ~4M GB households pay before they consume. This is where affordability physics stops being a distribution parameter and becomes minute-by-minute mechanics — and where the harshest unhappy paths in the market live. The W2 affordability cluster and the collections lane both dead-end without it. `~` = verify current. Refute with evidence.

## The estate and its two technologies
**Legacy PPM:** key/card meters, top-up at PayPoint/Payzone/PO, token carries credit physically; no remote anything; readings by visit or customer. **Smart PAYG:** SMETS meters in prepay mode — remote top-up (UTRN vend codes), remote credit↔prepay mode switching by service request, near-real-time balance telemetry. Estate mix shifts by year; any population draw must carry an era-consistent technology split — a 2019 book that is mostly smart-PAYG is a fiction.

## The mechanics that must exist (each is an event class, not a parameter)
- **Vend lifecycle:** purchase → UTRN issued → entered/redeemed → balance credited. Vends can fail, arrive late, or be re-entered — a replayed UTRN must not double-credit (idempotency by vend id).
- **Balance decomposition:** credit + emergency credit + debt-recovery allocation. The standing charge accrues **even at zero consumption** — a self-disconnected customer's debt grows while their lights are off. This single fact drives most PPM harm and must be reproducible.
- **Self-disconnection:** balance ≤ 0 outside protected windows → supply off. Detection matters as much as occurrence: a real supplier must identify it (smart: telemetry/zero-load; legacy: inference from vend gaps) because ~Ofgem requires monitoring and support offers.
- **Friendly credit / non-disconnect windows:** ~evenings, weekends, public holidays — running out at Friday 18:00 must NOT cut supply until the window closes. Calendar-driven, era-dependent.
- **Emergency credit:** opt-in buffer (~£5–£10 class) repaid from next vend before normal credit.
- **Debt recovery through the meter:** weekly recovery rate capped (~affordability-assessed, £/week class); recovery pauses/priorities interact with emergency credit.
- **Mode switching & involuntary PPM:** ~post-2023 rules gate involuntary switches and warrant installs hard — prohibited categories of vulnerability, mandatory checks, compensation for wrongful installs. In the SIM: a vulnerability/PSR flag must be able to BLOCK a remote mode-switch; the blocked attempt is itself an auditable event.
- **The cap variant:** PPM historically paid more; ~levelised with direct debit via the cap methodology (EPG bridge then permanent). The tariff engine needs the payment-method dimension with an era switch at the right cap version.
- **Unbilled-energy risk:** meter-clock drift, missed vend files, estate migration errors — the PPM flavour of the estimation gap.

## Data dependencies & artefacts
Vend transaction files (PayPoint/Payzone acquirer feeds), UTRN registers, meter balance reads (SRV class on smart), friendly-credit calendars, PSR register, debt-recovery schedules, ~Ofgem self-disconnection RFI returns. Counterparties: payment acquirers, DCC (smart PAYG), scheme bodies.

## Simplification candidates (register, never hide)
Collapse acquirer settlement timing to same-day at current rung (register it — real money clears T+n). Single emergency-credit value across the book. NOT simplifiable: standing-charge accrual at zero vend, friendly-credit calendar, debt-recovery cap, the vulnerability gate — these ARE the harm physics the mission exists to see.

## Disqualification battery
- **B1 Self-disconnection is observable:** the company can count and date self-disconnections per account from its own data; a book where nobody ever self-disconnects, or where it happens invisibly, is disqualified.
- **B2 The calendar holds:** engineer a zero balance at Friday 18:00 — supply continuing through the protected window, cutting only at its close, or the window physics is fake.
- **B3 Debt grows in the dark:** a self-disconnected month still accrues standing charge into debt; a model where disconnection freezes the account is disqualified.
- **B4 Recovery is capped:** meter debt recovery never exceeds the weekly cap regardless of balance; emergency credit repays first per the priority order.
- **B5 Vend idempotency:** replaying a vend file changes nothing; a duplicated UTRN crediting twice is disqualified.
- **B6 The gate blocks:** a PSR-flagged vulnerable account rejects an involuntary mode-switch and LOGS the rejection; silent success or silent failure both disqualify.
- **B7 Era-true books:** cap variant, levelisation date, and estate technology mix all match the simulated year; a 2021 PPM customer on levelised rates is disqualified.

— Advisor scope brief, 2026-08-07; `~` items verify-current before hard-coding.
