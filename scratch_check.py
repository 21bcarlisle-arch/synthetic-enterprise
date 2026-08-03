import numpy as np
from sim import renewable_capacity_trend as rct
from sim import price_engine as pe
from sim import weather_price_chain as wpc

print("== A7/A8/A9/A4-live/A10 on real data ==")
print("  A7 mean-basis reconciles :", rct.check_mean_capacity_reconciles_to_generation())
print("  A8 mean brackets year-end:", rct.check_mean_capacity_brackets_year_end())
print("  A9 mean dominates end    :", rct.check_mean_basis_dominates_year_end_basis())
print("  A4 no coal after 2024    :", rct.check_no_coal_after_retirement_on_real_series())
print("  A10 fleet contracts      :", rct.check_dispatchable_fleet_contracts())
print("  A5 (unchanged, year_end) :", rct.check_capacity_load_factor_reconciles_to_generation())

print("\n== dispatchable re-stacking ==")
for y in range(2016, 2026):
    print(f"  {y}  real={rct.real_dispatchable_capacity_mw(y):9.1f} MW  "
          f"shape={rct.dispatchable_shape(y):.4f}  "
          f"denominator={rct.dispatchable_capacity_mw(y):9.1f} MW  "
          f"coal={rct.real_coal_capacity_by_year()[y]:8.1f}")
mean_denom = np.mean([rct.dispatchable_capacity_mw(y) for y in range(2016, 2026)])
print(f"  window-mean denominator = {mean_denom:.6f} (calibrated const "
      f"{pe.DISPATCHABLE_CAPACITY_MW})")

print("\n== byte-identity of the default path (R12/S8 wall) ==")
a = pe.synthetic_price(60.0, 40000.0, 8000.0)
b = pe.system_margin_price(120.0, 40000.0, 8000.0)
print("  synthetic_price default  :", repr(a))
print("  system_margin default    :", repr(b))
print("  explicit capacity == const:",
      pe.system_margin_price(120.0, 40000.0, 8000.0, 35000.0) == b)
try:
    pe.system_margin_price(120.0, 40000.0, 8000.0, 35000.0, 2016)
    print("  BOTH-named raises        : NO  <-- DEFECT")
except ValueError as e:
    print("  BOTH-named raises        : YES")

print("\n== the re-stacking actually moves price ==")
for y in (2016, 2020, 2025):
    print(f"  synthetic_price(year={y}) = {pe.synthetic_price(60.0, 40000.0, 8000.0, year=y):.3f}")
print(f"  synthetic_price(year=None) = {pe.synthetic_price(60.0, 40000.0, 8000.0):.3f}")

print("\n== whole-record diagnostics (R12: reported, never a target) ==")
d = wpc.chain_vs_real_ssp_mae()
ya = wpc.chain_vs_real_ssp_mae(year_aware=True)
print(f"  default    MAE=£{d['mae']:.3f}/MWh  chain_mean=£{d['chain_mean']:.2f}  n={d['n']}")
print(f"  year_aware MAE=£{ya['mae']:.3f}/MWh  chain_mean=£{ya['chain_mean']:.2f}  n={ya['n']}")
