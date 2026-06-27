Phase 304 -- Climate Change Levy (CCL) Ledger

Status: PROPOSED (2026-06-27T00:47 BST)
4h opt-out window: expires 2026-06-27T04:47 BST

Context:
CCL (Climate Change Levy) is the UK main carbon tax on business energy consumption,
collected by energy suppliers and remitted to HMRC quarterly. It applies to SME and I&C
customers -- residential customers are fully exempt. Suppliers must also handle LECs
(Levy Exemption Certificates) for customers on 100%% renewable tariffs.

Currently ZERO CCL is tracked for business customers in the company layer. The
cost_to_serve (Ph294) has 7 levy components but excludes CCL. This is a material gap:
CCL is 0.775p/kWh electricity and 0.465p/kWh gas (2022 rates) for business customers.

2019 was a pivotal year: HMRC raised CCL 45%% (elec) and 67%% (gas) to shift UK
tax policy from NIC (employment) to carbon. This regime change should be captured.

Design:
- company/regulatory/ccl_ledger.py (new)
- CCLFuel (ELECTRICITY/GAS)
- CCLExemptReason (RESIDENTIAL/LEC_COVERED)
- CCLCharge (frozen): account_id/fuel/year/consumption_kwh/rate_p_per_kwh/
  exempt_reason (Optional); properties: charge_gbp (0 if exempt)/is_exempt
- CCLQuarterlyReturn (frozen): quarter_end/electricity_kwh/gas_kwh/
  electricity_due_gbp/gas_due_gbp/total_due_gbp/filed
- CCLLedger: rate_for_year/record_charge/charges_for_account/charges_for_year/
  total_due_gbp/quarterly_return/ccl_summary

Real HMRC rates 2016-2025:
  Electricity: 0.554->0.583 (2016-18), 0.847 (2019 spike), 0.775 (2021-25) p/kWh
  Gas:         0.195->0.203 (2016-18), 0.339 (2019), 0.465 (2021-25) p/kWh

Connects to: cost_to_serve (Ph294), invoice (billing), desnz_returns (regulatory).
Estimated: ~14 tests, ~160 lines
