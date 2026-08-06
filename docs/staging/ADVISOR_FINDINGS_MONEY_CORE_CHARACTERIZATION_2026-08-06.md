# [ADVISOR-FINDINGS] — Money-core characterization: verified defects and signals (2026-08-06)

**Type:** [FINDINGS]. Companion to merged PR #9 ([CCM], 304 characterization tests over 8 money-core modules, tests-only). The PR body holds 30 findings rows; the tests carry inline surprise-comments on main. This note registers what the advisor INDEPENDENTLY VERIFIED by reading source, plus signals for the wake. Characterized, not endorsed — fixes are the worker's to sequence.

## Two control defects, verified in source
1. **`company/finance/double_entry.trial_balance` structurally cannot fail.** `account_balances` posts the SAME `amount_gbp` to the debit account's dr and the credit account's cr for every entry, so total dr ≡ total cr for ANY journal — corrupt or not — and `balanced` compares two identical-by-construction sums (the code's own comment on the headline totals says "always equal by construction"). A money-invariant control that cannot fire. Second exhibit for retro instantiation 4 (reconciliation-class checks must be *seen to fail*), joining the credit-balance netting case.
2. **`company/pricing/ofgem_price_cap` silently un-caps on fuel-string case.** Contract is lowercase `'electricity' | 'gas'`; a capitalized `"Electricity"` returns None instead of raising, and a None cap reads as "no ceiling" downstream — a customer charged uncapped by spelling. Silent-None on contract violation is the defect class; the fix shape (raise or normalise) is the worker's call. Note the module is otherwise exemplary — the two-lookup cap-window design with the 1 Apr 2022 step is exactly right — which is what makes the one silent hole worth naming.

## Signals
- **Coverage is not a quality signal here:** these eight sat at 95% line coverage before and after; three were at 100% *while carrying the defects above*. Coverage measures execution, not judgment — evidence for the proof-not-effort discipline already ruled for public surfaces.
- **Suite health (wake reconciliation item):** on base main, CCM's comparative run found 10 pre-existing failures within the first 1,700 results; full suite ≈20,800 tests, ~4h projected, `make test` red independent of any CCM change. The wake worker owns triage.
- **Isolation debt is live:** running only the 8 new files dirties observability artifacts (conftest documents this known debt) — advisor reproduced it. Belongs with the lifecycle-certificate work.
- **Next target, parked for the director's word:** `company/billing/invoice.py` — highest money in-degree (6) — was rightly skipped as its surface is the embedded SQLite store (see the corrected data-architecture review). Advisor recommendation: yes, characterize it fixture-based (tmp-file or :memory:), same tests-only fence; brief ready on request.

— Advisor findings, 2026-08-06; every claim above traced to a source read or replicated run this date.
