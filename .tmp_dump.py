import ast, pathlib
files = """company/crm/service_ticket.py
company/crm/service_log.py
company/billing/credit_refund.py
company/crm/change_of_tenancy_register.py
company/market/bsc_settlement_dispute_register.py
company/market/bsc_performance_assurance_register.py
company/trading/emir_reporting_register.py
company/market/mop_appointment_register.py
company/regulatory/gsop.py
simulation/credit_refund_events.py
company/billing/energy_theft_book.py
company/market/dcc_meter_registration.py
company/billing/dd_indemnity.py
company/crm/onboarding_journey.py
company/market/mpas_standing_data_correction_register.py
company/regulatory/gsop_tracker.py
company/billing/deemed_contract.py
company/market/erroneous_transfer.py
company/market/meter_technical_investigation_register.py
company/market/css_performance_register.py
simulation/bacs_rails.py""".split()
NAMES = {"_add_working_days", "_working_days_between", "working_days_open", "working_days_to_pay"}
for f in files:
    src = pathlib.Path(f).read_text()
    tree = ast.parse(src)
    lines = src.splitlines()
    print("=" * 70)
    print(f)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in NAMES:
            print("\n".join(lines[node.lineno - 1 : node.end_lineno]))
            print("-" * 30)
