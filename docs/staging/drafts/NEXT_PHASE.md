Phase 146 -- Change of Tenancy (COT) Management

Status: PROPOSED (2026-06-26)

UK suppliers handle tens of thousands of COT events per year. When a customer moves
out of a property, the supplier must:
1. Accept the move-out notification, take a final meter read, issue a final bill
2. Hold the property as "void" (no named occupant) and bill "The Occupier" at deemed rates
3. Accept a move-in from the new occupant, start a new deemed contract
4. After 28 days void, switch to a named SVT contract (regulatory obligation)

The current model has no mechanism for this. Customers just persist indefinitely on the
same metering point. This is a significant fidelity gap: ~3% of UK electricity meter points
change occupancy each year.

Design: company/billing/cot.py

COTType enum: MOVE_OUT / MOVE_IN / VOID

COTEvent(customer_id, mpan_or_mprn, cot_type, date, meter_read_kwh, new_occupant_id=None)
- Move-out: triggers final read acknowledgement  
- Move-in: opens a deemed contract at deemed_rate
- Void: property with no named occupant

COTBook:
- record_move_out(customer_id, date, final_read_kwh) -> COTEvent
- record_move_in(mpan, new_customer_id, date, opening_read_kwh) -> COTEvent
- void_properties() -> list[str] MPANs/MPRNs with no current occupant
- void_days(mpan, as_of_date) -> int days since last move-out
- deemed_rate_gbp_per_kwh(date) -> SVT unit rate + 20% uplift (Ofgem cap-aware for domestic)
- overdue_for_nomination(as_of_date) -> void properties >28 days (regulatory trigger)
- portfolio_summary() -> total_voids, avg_void_days, total_deemed_revenue_gbp

2022 dynamic: spike in property voids as customers fell into arrears and abandoned properties.
Deemed rate capped at Ofgem price cap for domestic properties.

~11 tests. Closes the metering-point lifecycle gap: property changes hands but company has
no model for what happens between occupants.
