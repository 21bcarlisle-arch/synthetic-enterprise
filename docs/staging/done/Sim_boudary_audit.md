[SIM] Close the boundary audit -- three violations still open, unaddressed since the June 30 audit

docs/architecture/sim_boundary_audit_20260630.md found: verifier doesn't scan saas/, and two reporting modules read sim-internal state directly (simulation.segments in segment_report.py, sim.scenario.bimodal_generator in annual_report.py, simulation.tou_periods MEDIUM). Nothing in the build history since has addressed this -- it's been open for 3 days while other work proceeded.

Fix all three now, before anything else:
1. Extend the boundary verifier to scan saas/ (and any other company-adjacent directory currently missed). Priority -- a verifier with a blind spot creates false confidence in every future audit.
2. Replace simulation.segments in segment_report.py with the company-observed equivalent (event ledger / CRM registry -- segment data the company already tracks from its own customer records).
3. Replace sim.scenario.bimodal_generator in annual_report.py the same way -- source scenario/segment composition from what the company has actually observed and recorded, not sim internals.
4. Re-run the fixed verifier against the full tree. Confirm zero violations. Add a named phase entry to PROJECT_OVERVIEW.md build history confirming closure.

Proceed on your own design. This has sat open long enough -- close it now.