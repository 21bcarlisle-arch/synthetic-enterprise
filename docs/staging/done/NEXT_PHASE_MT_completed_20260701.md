Phase MT -- I and C Triad Demand Curtailment

Wire Triad notifications to actual demand reduction in the settlement run.

Motivation: triad_notification_book records alerts when Triad periods are
expected, but sim/demand_model.py and the settlement loop ignore them.
Industrial and commercial customers never reduce load in Triad windows.
This means the sim overstates I and C consumption (and hence costs) during
Triad periods, and the Triad management benefit is never realised.

Scope:
1. sim/demand_model.py: add a triad_response_factor(account, settlement_period)
   function. For I and C accounts with triad notification active, apply a
   demand reduction of 20-30% during notified Triad settlement periods.
   Response rate should be calibrated to industry data (Ofgem/NESO Triad avoidance).
2. Settlement run: pass active Triad alerts into demand calculation.
   Use triad_notification_book.get_active_alerts(date, period) to check.
3. triad_notification_book: expose a query method for active alerts by date/period.
4. Run 2016-2025 full simulation. Verify Triad periods show reduced I and C demand.
5. 15+ tests: demand reduction active/inactive, response rate bounds, PIT safety.

Expected outcome: I and C customers reduce demand by 20-30 percent during
the 3 Triad settlement periods per winter season. Triad charges decrease.
The triad_exposure_register will show lower demand_t1 values for I and C
customers who received notifications.
