"""One-off migration helper: remove local working-day helper, import canonical."""
import ast, pathlib, re, sys

ADD = {
    "company/crm/change_of_tenancy_register.py": ("_add_working_days", "add_working_days"),
    "company/crm/onboarding_journey.py": ("_add_working_days", "add_working_days"),
    "company/crm/service_log.py": ("_add_working_days", "add_working_days"),
    "company/crm/service_ticket.py": ("_add_working_days", "add_working_days"),
    "company/market/bsc_performance_assurance_register.py": ("_add_working_days", "add_working_days"),
    "company/market/bsc_settlement_dispute_register.py": ("_add_working_days", "add_working_days"),
    "company/market/css_performance_register.py": ("_add_working_days", "add_working_days"),
    "company/market/dcc_meter_registration.py": ("_add_working_days", "add_working_days"),
    "company/market/meter_technical_investigation_register.py": ("_add_working_days", "add_working_days"),
    "company/market/mop_appointment_register.py": ("_add_working_days", "add_working_days"),
    "company/market/mpas_standing_data_correction_register.py": ("_add_working_days", "add_working_days"),
    "company/regulatory/gsop.py": ("_add_working_days", "add_working_days"),
    "simulation/bacs_rails.py": ("_add_working_days", "add_working_days"),
    "simulation/credit_refund_events.py": ("_add_working_days", "add_working_days"),
    "company/market/transfer_objection_register.py": ("_add_wd", "add_working_days"),
    "company/regulatory/annual_compliance_attestation_register.py": ("_add_wd", "add_working_days"),
    "company/billing/dd_indemnity.py": ("_working_days_between", "working_days_elapsed"),
    "company/billing/deemed_contract.py": ("_working_days_between", "working_days_elapsed"),
    "company/billing/energy_theft_book.py": ("_working_days_between", "working_days_elapsed"),
    "company/billing/credit_refund.py": ("_working_days_between", "working_days_elapsed"),
}


def migrate(rel, old, new):
    p = pathlib.Path(rel)
    src = p.read_text()
    tree = ast.parse(src)
    lines = src.splitlines(keepends=True)

    target = None
    last_import_end = None
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            last_import_end = node.end_lineno
        if isinstance(node, ast.FunctionDef) and node.name == old:
            target = node
    if target is None:
        print(f"  !! {rel}: no top-level def {old}")
        return False
    if last_import_end is None:
        print(f"  !! {rel}: no imports found")
        return False

    # blank out the def (plus any immediately-preceding decorator-free blank padding)
    start = target.lineno - 1
    end = target.end_lineno
    # swallow trailing blank lines that separated it
    while end < len(lines) and lines[end].strip() == "":
        end += 1
    del lines[start:end]

    # re-derive insertion point after deletion (imports precede the def)
    insert_at = last_import_end
    imp = f"from regulation_commons.working_days import {new}\n"
    lines.insert(insert_at, imp)

    out = "".join(lines)
    # rename call sites (word-boundary)
    out = re.sub(rf"(?<![\w.]){re.escape(old)}\(", f"{new}(", out)
    p.write_text(out)
    return True


ok = 0
for rel, (old, new) in ADD.items():
    if migrate(rel, old, new):
        print(f"  migrated {rel}: {old} -> {new}")
        ok += 1
print(f"{ok}/{len(ADD)} migrated")
