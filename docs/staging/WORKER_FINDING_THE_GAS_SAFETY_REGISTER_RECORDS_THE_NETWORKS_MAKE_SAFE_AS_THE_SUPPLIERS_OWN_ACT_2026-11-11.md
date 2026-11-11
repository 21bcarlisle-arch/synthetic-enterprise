**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** unassigned · **Atom:** `unminted`

# The gas safety register records the network's make-safe as the supplier's own act (2026-11-11)

**Where this comes from.** Item 4 of `DIRECTOR_STEER_KNOWLEDGE_FIRST_FRONT_LINE_GAPS_2026-11-10.md`. Its knowledge
page is `docs/market_research/who_does_what_in_a_gas_escape_or_co_incident_2026-11-11.md`, written from the
statute on legislation.gov.uk.

**What landed with that page.** `company/billing/gas_safety_incident_register.py`'s docstring now states the
statutory split. The advisor's belief is confirmed: for network gas, the make-safe is the conveyor's duty
(GSMR 7(4)/(5)), and the supplier's GSIUR 37(1) duty is disapplied by 37(7). The RIDDOR clock is now 14 days
(RIDDOR 11(1)(b)), not 15, and the docstring says that report is the conveyor's. The "3 years (GSIUR Reg 35)"
retention claim is withdrawn: reg 35 is the employer's maintenance duty.

**What is still wrong.**
- **The state machine.** `dispatch_engineer`, `isolate_supply` and `mark_made_safe` still model the network's
  acts as supplier transitions. The supplier's own record would be:
  - passed to the emergency service (GSMR 7(3), "forthwith");
  - CO advice given (GSIUR 37(8));
  - the conveyor's make-safe and RIDDOR report, held as reports it has received (GSMR 7(15));
  - the 7(14) investigation opened, HSE told, and the report sent (7(16)).
- **Close-gating.** `close_incident` gates closing on `MADE_SAFE` or `RIDDOR_NOTIFIED`. It should gate on the
  supplier's own duties having been discharged.
- **The cost of the rebuild.** 89 tests across `test_gas_safety_incident_register.py`,
  `test_phase_hc_gas_safety.py` and `test_obligations_register.py` are built on the current shape.

**Why LATENT.** The module is not wired into a run. It is reached only by name, from `obligations_register.py`
(row `gas_safety_incidents`). No book figure, page or published claim reads it, so nothing published is wrong
today.

**The GAPs the page names:**
- the supplier's investigation clock (GSMR 7(14) says "as soon as is reasonably practicable"; HSE's L80 guidance
  has not been read);
- the supplier's retention period for incident records;
- whether the gas supply licence adds a safety duty.

**Recommendation.** Rebuild when gas safety is wired into the world. That needs the world to generate escapes and
CO incidents, which no atom does today. Until then, the corrected docstring is the honest state, and a rebuild
would be a feature the correctness stretch holds.

## Reverse

Delete this file.
