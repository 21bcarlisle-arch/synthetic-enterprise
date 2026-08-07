# [ADVISOR-SCOPE-BRIEF] — Change of tenancy, deemed contracts, and voids (2026-08-07)

**Type:** [SCOPE BRIEF — domain-first, written before reading the code]. ~10% of households move each year. The meter stays, supply never stops, and the supplier's counterparty simply changes overnight — often without telling anyone. CoT is where the customer lifecycle, the credit-balance invariant, back-billing, and the estimation gap all collide, and industry data barely helps: registration systems know MPANs and suppliers, not occupiers. `~` = verify current. Refute with evidence.

## The physics
- **CoT ≠ CoS.** Change of tenancy is supplier-internal — no switching flow, no CSS message. The incumbent keeps the meter; the person changes. Industry-wide, nobody is told.
- **The deemed contract:** the moment a new occupier takes supply without agreeing terms, a deemed contract arises with the incumbent under the ~licence deemed-contract scheme, at deemed/SVT rates, cap-protected. There is no lawful gap: every kWh after the tenancy start has a liable counterparty, discovered or not.
- **Liability follows the occupier, not the premises.** Debt does NOT transfer to the incoming occupier's account — it stays with the outgoing person. The one physical exception: **legacy PPM debt programmed into the meter**, which the new occupier inherits at the till until the meter is reset — a classic harm path that must be modelled or register-simplified, never silently absent.
- **The reads problem:** opening/closing reads are the whole financial boundary. Agreed reads are rare; estimates are the norm; the same estimated read closes one account and opens another, so an estimation error is a zero-sum transfer between strangers — and the seed of most CoT disputes.
- **Dates are contested:** "I moved in later than that" is also a debt-avoidance move. Resolution runs on an evidence hierarchy (tenancy agreement, council tax, reads), not assertion.
- **The outgoing account:** final bill to a forwarding address that often doesn't exist → debt tracing or write-off; credit balances on closed accounts must refund or trace — the credit-balance anniversary invariant applies with extra force here, because closed-account credit is the easiest money to silently keep.
- **Voids:** between occupiers the premises still has standing charge and possibly consumption (landlord works, heating on frost-protect). Void liability sits with the landlord/owner under deemed terms — a distinct counterparty class, not a phantom customer and not free energy.
- **Special paths:** bereavement (estate liability, handled under a distinct care standard), joint tenants (several liability), name-change-only (same household, no financial boundary), erroneous CoT (fraudulent or mistaken — reversal mechanics).
- **Back-billing interplay:** the CoT date anchors the billing window; a late-discovered CoT can make months retrospectively unbillable to the wrong party and re-billable to the right one — the back-billing limit runs per person, per liability period.

## SIM & company hooks
The life-event stream must emit moves at realistic rate and seasonality (~summer/quarter-day peaks); the population draw needs tenure mix (owner/rented/social) since churn and void behaviour differ; deemed-rate revenue and void-ledger accrual are real P&L lines; discovery latency (occupier tells us in week 1 vs month 6) is itself a distribution with financial consequences.

## Simplification candidates (register, never hide)
Instant discovery at current rung (register it — reality is a latency distribution). Collapse bereavement/joint-tenant into standard CoT with a flag. NOT simplifiable: the deemed contract's automatic formation, person-not-premises liability, the shared estimated read at the boundary, closed-account credit disposition, the void counterparty class.

## Disqualification battery
- **B1 No contractless energy:** every settled kWh at every MPAN maps to a liable counterparty (named occupier, deemed occupier, or void/landlord) for every day — an orphan-supply day disqualifies.
- **B2 Debt stays with the person:** engineer a CoT over an indebted account — the incoming account opens clean; any balance transfer to the new occupier disqualifies (legacy-PPM meter debt excepted only if explicitly modelled or registered as a simplification).
- **B3 The boundary read is shared:** outgoing closing read == incoming opening read, always; a discrepancy between the two sides of the same moment disqualifies.
- **B4 Closed credit resolves:** a closed account's credit refunds, traces, or carries a dated reason within the anniversary invariant — closed-account credit sitting silently past it disqualifies.
- **B5 Voids bill the right class:** void-period standing charge accrues to the void/landlord ledger; booking it to the departed customer, the future customer, or nowhere all disqualify.
- **B6 Dates resolve by evidence:** a disputed move-in date resolves through the evidence hierarchy and re-anchors the back-billing window per person; assertion-wins disqualifies.
- **B7 The stream is alive:** across a decade replay, CoT events occur at census-plausible rates with seasonality, and discovery latency is a distribution, not zero.

— Advisor scope brief, 2026-08-07; `~` items verify-current before hard-coding.
