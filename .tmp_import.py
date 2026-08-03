import importlib, traceback
mods = """company.billing.credit_refund
company.billing.dd_indemnity
company.billing.deemed_contract
company.billing.energy_theft_book
company.crm.change_of_tenancy_register
company.crm.onboarding_journey
company.crm.service_log
company.crm.service_ticket
company.market.bsc_performance_assurance_register
company.market.bsc_settlement_dispute_register
company.market.css_performance_register
company.market.dcc_meter_registration
company.market.erroneous_transfer
company.market.meter_technical_investigation_register
company.market.mop_appointment_register
company.market.mpas_standing_data_correction_register
company.market.transfer_objection_register
company.regulatory.annual_compliance_attestation_register
company.regulatory.gsop
company.regulatory.gsop_tracker
company.trading.bsc_credit_register
company.trading.emir_reporting_register
simulation.bacs_rails
simulation.credit_refund_events""".split()
bad = 0
for m in mods:
    try:
        importlib.import_module(m)
    except Exception:
        bad += 1
        print("FAIL", m)
        traceback.print_exc()
print(f"{len(mods)-bad}/{len(mods)} import OK")
