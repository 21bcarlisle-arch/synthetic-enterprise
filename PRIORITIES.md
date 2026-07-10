# PRIORITIES.md -- Synthetic Enterprise
# last director review: 2026-07-10 (MARGIN_REALISM.md, advisor-staged/director-decided)
#
# === HARNESS_BEST_PRACTICE_ADOPTION.md -- P2, IN PROGRESS (2026-07-10, advisor-staged,
#   arrived mid-session via a git merge; docs/design/HARNESS_BEST_PRACTICE_ASSESSMENT.md).
#   Picked up while the maturity-map queue is genuinely exhausted (see entry above) -- legitimate
#   non-displacing work per the staged instruction's own sequencing note. Validation-first
#   confirmed: supervisor/maturity-map/R7-R8 already independently match the published
#   long-running-agent patterns the advisor found. All 6 candidates assessed (adopt/adapt/reject
#   + reasons). Technical verification (via claude-code-guide agent, no network access here to
#   check the docs directly) confirms all three real: lifecycle hooks (PreToolUse/PostToolUse,
#   .claude/settings.json), fallbackModel resilience chaining, and Routines (schedule/API/
#   GitHub-trigger cloud sessions) -- exact schemas recorded in the assessment doc. Item 5
#   (environment hardening) written up as a recommendation only (Tier-1-adjacent, no build).
#   Item 6 (harness pruning ritual) adopted directly into CLAUDE.md's phase-close checklist
#   (6a). Item 3 (fallbackModel) DONE 2026-07-10: .claude/settings.json now sets
#   "fallbackModel": ["claude-sonnet-5", "claude-haiku-4-5-20251001"], no cost/preference change,
#   fires only on genuine primary unavailability. Item 1 (b)+(c) DONE 2026-07-10:
#   .claude/hooks/block_sudo.py (PreToolUse/Bash, exit 2 on any sudo invocation) and
#   .claude/hooks/block_unevidenced_claim.py (PreToolUse/Bash, blocks a send_ntfy(...) call
#   whose message claims fixed/live/deployed/confirmed/verified unless
#   docs/observability/.last_live_verification exists and is <30min old -- the R11 evidence
#   contract, `touch` the marker right after a real curl/fetch live-check). Both individually
#   demonstrated per the DoD (blocked-sudo, allowed-normal, blocked-unevidenced-claim,
#   allowed-with-fresh-marker, allowed-non-claim-message -- see
#   tests/tools/test_claude_hooks.py, 12 new tests) and wired live in .claude/settings.json
#   (confirmed real: my own test bash command tripped the live hook mid-session before I
#   switched to file-redirected stdin to test cleanly). Item 1(a) (point-in-time-blindfold
#   hook) DELIBERATELY NOT BUILT: it's the same detection class as the still-open
#   EPISTEMIC_VERIFIER_TIMING_DETECTION_TIER1.md gate (data-flow/timing violation detection)
#   -- building a parallel enforcement mechanism for the same class while that gate sits open
#   and unanswered would pre-empt the director's own pending decision. Holds until that gate
#   closes. Item 4 (Routines pilot) BLOCKED, not built: RemoteTrigger's real `create` schema
#   (probed live: name -> job_config -> job_config.ccr -> requires
#   ccr.environment_id or ccr.self_hosted_runner_pool_id) needs a cloud environment already
#   configured in Rich's claude.ai account -- not something I can fabricate or discover by
#   further trial-and-error against the live API. Needs Rich to either point me at an existing
#   environment_id or set one up. Item 2 (evaluator subagent) sequenced after item 1 fully
#   lands (1a still open) -- not started. 16,554 tests collected (full suite via collect-only;
#   1,362 passed directly in tests/tools/+tests/background/), epistemic PASS.
#
# === MATURITY-MAP QUEUE STATUS: EXHAUSTED, CORRECTLY (2026-07-10, nineteenth dial-weighted
#   draw): every remaining atom with a real level gap is now either genuinely idle-blocked
#   (W1_reveal_over_time and its dependents D2/D3/E2/B1/E3/G2/C2, all pending the epoch
#   sequencing from the closed POINT_IN_TIME_SNAPSHOT_TIER1.md gate; B2_opex_cost_to_serve,
#   pending the director's own answers on AI-compute costing basis + oversight rate;
#   W4_2_verifier_timing_extension, pending the still-open EPISTEMIC_VERIFIER_TIMING_
#   DETECTION_TIER1.md gate) or director-ratified-idle-by-design (A/G/W3-lane items per the
#   original MATURITY_MAP.md Section 8 equaliser). B2's investigation (whether re-enabling
#   background/token_proxy.py routing could unblock part (b)) found the answer is NO --
#   autonomous_runner.py deliberately stopped routing through it after a documented past
#   incident ("the single point of failure that silently killed all overnight autonomous
#   turns") -- correctly left alone rather than reintroducing known risk. This queue-exhaustion
#   ALSO surfaced (and got fixed at the root) a third live instance of the same self-
#   referential false-positive class in the PRIORITIES.md-backlog fallback path --
#   background/supervisor.py::_actionable_backlog_item() now anchors to a real line-start
#   "## Backlog" heading (re.search with re.MULTILINE) instead of a raw substring find, which
#   had been locking onto a prose mention of the heading name earlier in this very file. 2 new
#   tests, 454/454 background tests pass, 16,542 tests collected (full suite), epistemic PASS.
#   NEXT real self-refill work requires either: the one open Tier 1 gate being decided
#   (EPISTEMIC_VERIFIER_TIMING_DETECTION_TIER1.md -- corrected 2026-07-10, this line previously
#   said "two", stale since POINT_IN_TIME_SNAPSHOT_TIER1.md closed), the epoch sequencing naming
#   W1/D2's turn, or B2's two open cost-basis questions being answered.
#
# === E1 CORPORATION TAX -- BUILT 2026-07-10 (eighteenth dial-weighted draw,
#   docs/design/E1_CORPORATION_TAX_FINDING.md): balance_sheet() genuinely balances for every real
#   year 2016-2025 (verified, not assumed). Real gap found + closed against the real_world_twin
#   (a real supplier's statutory accounts): UK Corporation Tax was entirely absent -- net_margin_gbp
#   is pre-tax operating profit, not the post-tax "Profit for the year" a real Companies House
#   filing headlines. Built as a genuinely NEW, additive triplet (profit_before_tax_gbp/
#   corporation_tax_gbp/profit_for_year_gbp) via company/finance/double_entry.py::
#   uk_corporation_tax_gbp() -- real UK rates (19% flat pre-April 2023, then 19%/25%/marginal-relief
#   via HMRC's own 3/200 Standard Fraction, verified continuous at both the £50k and £250k
#   thresholds). net_margin_gbp itself is UNCHANGED (verified with a direct with/without-year test)
#   -- the EBIT% anchors already used throughout MARGIN_REALISM (EDF/British Gas CSS, Ofgem cap)
#   are BY DEFINITION pre-tax, so that field must keep meaning exactly what it always has; the new
#   fields are None unless a year is explicitly passed (only annual_management_pack()'s real call
#   site was updated). Deliberately did NOT touch the balance sheet -- no real anchor for CT
#   payment timing (~9 months after period end in reality) -- registered as a known, honest scope
#   limit rather than invented. 14 new tests, 16,540 tests collected (full suite), epistemic PASS.
#   SELF-CAUGHT PROCESS GAP (same turn): several recent doc-only CLAUDE.md entries this session
#   omitted the required "N tests collected" phrase (rule 2a), which broke
#   tools/generate_phases_json.py's _derive_build_from_claude_md() parser (test_derive_build_
#   from_claude_md_parses_current_state started failing, test_count came back None) -- fixed by
#   ensuring THIS entry properly states the true full-suite figure; not retroactively editing past
#   commits.
#
# === E2 REVENUE RECONCILIATION -- REAL PROGRESS, DEEPER ISSUE FOUND (2026-07-10, first
#   dial-weighted maturity-map self-refill draw, docs/design/MARGIN_REALISM_E2_TWO_PIPELINES_
#   FINDING.md): audited every surface reading revenue_gbp/a margin %. fra_ratio_series was
#   already correct (my own earlier maturity-map note was an unverified assumption --
#   corrected rather than left standing). tools/generate_insights.py had a REAL live
#   instance of the Step 1 class of bug -- compared a commodity-only revenue % against a
#   real external 2-5% TOTAL-margin benchmark (Ofgem/CMA), feeding every run-completion
#   NTFY via run_insights.json, uncaught by the dashboard's consistency gate (which only
#   checks absolute £ fields, never a %). Fixed: sums management_accounts' real total
#   revenue across years as the denominator. 1 new test, epistemic PASS.
#   PRIORITY RAISED 2026-07-10 (B1_margin_bridge DISCOVER finding, docs/design/
#   MARGIN_REALISM_B1_DISCOVER_FINDING.md, third dial-weighted draw): the SAME root cause
#   had a LIVE, user-visible symptom too -- docs/reports/ANNUAL_REPORT.md renders TWO
#   adjacent margin-bridge sections (Phase BE ledger-based, Phase NT years[]-based) whose
#   gross-margin deltas for the same year transition genuinely disagree (2016-2017:
#   +116,919 vs +116,417), unlabelled.
#   ROOT CAUSE TRACED 2026-07-10 (eighth dial-weighted draw, third time this atom was drawn
#   -- traced rather than deferred again): saas/bill_generator.py bills non-commodity cost
#   via a SINGLE BLENDED £/MWh rate (saas/non_commodity.py, Phase 9a/78) while
#   simulation/hedged_settlement.py computes the SAME real cost category per-levy,
#   per-settlement-period (RO/CfD/CCL/CM/FiT + DUoS/TNUoS individually, Phases 21a/27b/30a/
#   31a) -- two independently-built, never-reconciled models of the same real-world cost.
#   Confirmed via the wholesale-cost cross-check: wholesale cost matches almost exactly
#   between both pipelines (2016: ledger £3,594.97 vs years[]-implied £3,594.96) -- the
#   ENTIRE gross-level divergence traces to the non-commodity side only. The gap is
#   BIDIRECTIONAL and non-monotonic across years (+27.7% 2016, -25.3% 2017, -3.2% 2018,
#   +4.4%/+4.5%/+0.3% 2019-21, -14.9%/-9.7% 2022-23, +10.1%/+34.5% 2024-25) -- NOT a simple
#   missing-component bug, consistent with a genuine volume/timing mismatch between when
#   energy is settled vs billed (the same real phenomenon D2_three_clocks already names).
#   RECOMMENDATION (not built): do not pick one pipeline as authoritative -- reconcile via
#   D2_three_clocks (its natural home, real evidence now feeds that atom directly) rather
#   than resolve within E2/B1's own scope. E2/B1's OWN scope (gauge fix, legibility, driver
#   set) is now closed on its own terms -- full numerical reconciliation is D2's job.
#   IMPLICATION: Step 1's "~12.5% -> ~8.9%" figure used years[].net_gbp (the smaller
#   numerator) -- may need a second pass once D2 resolves; not restated as broken, no
#   longer assumed fully closed either.
#
# === B1 MARGIN BRIDGE -- DISCOVER-STAGE FINDING (2026-07-10, second dial-weighted draw,
#   docs/design/MARGIN_REALISM_B1_DISCOVER_FINDING.md): the bridge's own residual reconciles
#   to ~£0 every year (internally self-consistent). Real DISCOVER-stage gaps found: (1) see
#   E2's "PRIORITY RAISED" note above -- two report sections disagree, same root cause;
#   (2) gross_delta is a single lump, no price/volume split -- external FP&A convention
#   research dispatched (discovery-agent, appending to ASSUMPTIONS.md under "B1 margin
#   bridge (Maturity Map DISCOVER)", non-blocking); (3) portfolio_change (active customer
#   count delta) is informational only, not an attributed £ driver -- same research checking
#   whether a real supplier report quantifies new/lost-customer contribution separately.
#   No opex/cost-to-serve driver yet -- correctly NOT a gap, blocked on Step 3.
#   RESEARCH LANDED: price/volume/mix split is real FP&A convention (Corporate Finance
#   Institute) but NOT energy-retail-specific; Centrica plc's actual FY2025 results use
#   sector-specific named drivers (weather £80m headwind, EPG/FiT reconciliations, bad debt
#   quantified directly by the CFO) much closer to this bridge's existing driver set --
#   VALIDATES the current design, no price/volume rebuild needed. Customer count as
#   informational-only is ALSO validated (Centrica discloses it as a standalone KPI, not
#   inside the £ bridge). Ofgem/CMA's own methodology doesn't use a bridge/waterfall
#   convention at all (levels-and-trends instead) -- useful negative finding. NEXT: once
#   E2's root cause resolves (the real remaining gap), re-assess whether level 2->3 is
#   earned -- the driver-set question is now closed, don't re-open it.
#
# === W1 REVEAL-OVER-TIME -- DISCOVER-STAGE FINDING, TIER 1 ADJACENT (2026-07-10, fourth
#   dial-weighted draw, docs/design/MARGIN_REALISM_W1_DISCOVER_FINDING.md): audited how
#   price-history data flows into decision-making, following up the recent hedge-volatility
#   review-gate fix. Found a real architectural inconsistency: sim/risk_engine.py::
#   calculate_sigma_recent() is self-contained/safe "at the source" (takes reference_date,
#   filters internally); company/trading/hedge_decision.py::estimate_price_volatility() has
#   NO date parameter at all -- caller-trusted, made safe only by an external wrapper
#   (_price_history_as_of()) at its one known call site, patched after the original bug was
#   found. No live second violation found (only one production call path exists and it IS
#   patched), but the unsafe function itself remains a template a future call site or
#   refactor could copy without noticing. Design sketch registered, NOT built (Tier 1 --
#   touches the SIM/company boundary, requires explicit director approval before any code
#   change): a single structural point-in-time snapshot/as-of-view object all reads go
#   through, replacing per-call-site patches. RESEARCH LANDED: "look-ahead bias" is the
#   confirmed standard term (QuantConnect/LEAN glossary); QuantConnect names its own
#   enforcement boundary the "Time Frontier", Zipline uses event-driven/streaming delivery --
#   both real, named precedent for a structural approach. The MORE mature pattern than a
#   simple as-of-filter is a shared, uniformly-enforced access layer every caller must route
#   through -- named "point-in-time join" (Feast, open-source ML feature store) and
#   "bitemporal history" (Martin Fowler); Lopez de Prado's "Advances in Financial Machine
#   Learning" (Wiley 2018) implements this as a reusable PurgedKFoldCV class with "purging"/
#   "embargo" concepts. Real quantified precedent for the COST of getting this wrong exists
#   for the sibling bias (survivorship bias: Elton/Gruber/Blake 1996, ~0.9%/yr overstated
#   returns) though no case study was found naming look-ahead bias specifically from
#   inconsistent per-function enforcement -- stated as an honest negative finding, not
#   invented. TIER 1 REVIEW GATE OPENED 2026-07-10 (eleventh dial-weighted draw):
#   docs/review_gates/POINT_IN_TIME_SNAPSHOT_TIER1.md -- decision needed: build a structural
#   point-in-time snapshot object now, or register/sequence after current work, or do nothing
#   beyond documenting the pattern. Recommendation given (register, sequence after
#   MARGIN_REALISM Steps 3-6 + D2_three_clocks -- no live bug driving urgency, purely
#   preventive value), but this is the director's decision, not a default to proceed on.
#   GATE CLOSED 2026-07-10 (director, in-console via staged NTFY from_rich_20260710_165627.md):
#   "Approved as recommended: register, don't build now." PLACEMENT CORRECTION (director): this
#   is Epoch-2 CORE, not a standalone W1-lane item -- the COMPANY-SIDE face of the reveal-over-
#   time spine, sibling to D2_three_clocks (the BILLING-side face), ONE architecture not two.
#   Sequencing left to the advisor's epoch framing -- not decided here. Standing interim
#   instruction: keep patching individual call sites only if a live bug actually surfaces
#   (matching the hedge-volatility precedent), no proactive build before the epoch sequencing
#   names its turn. Both W1_reveal_over_time and D2_three_clocks now cross-reference this
#   closed gate and each other; both set to loop_stage=idle. Gate moved to
#   docs/review_gates/done/POINT_IN_TIME_SNAPSHOT_TIER1.md.
#
# === SANITY DAEMON FOLLOW-UPS (2026-07-10, director NTFY -- "sanity daemon findings
#   ...all seem similar and repetitive, is there a broader fix needed" -- YES, fixed
#   the alerting bug live (background/sanity_daemon.py's audit-NTFY dedup was keyed
#   on the Qwen skeptic's randomly-sampled customer/date, which changes almost every
#   cycle by construction -- 49/49 cycles fired an NTFY over 21h; now keyed on a
#   normalised finding CATEGORY, tests + epistemic PASS, daemon restarted live).
#   TWO follow-ups NOT done, registered rather than rushed:
#   (1) the 3 population-sanity findings themselves (C1_2 129kWh/2020, C1g 42.6
#   GBP/MWh/2019, C4 ~320.5 GBP/MWh/2024) have been the IDENTICAL customer/year for
#   21h+ across 50 cycles -- a real, still-unfixed data anomaly, not just an
#   alerting question. Needs its own R4 diagnosis (nearest working analogue: the
#   other ~7 customers in the same segment/year that DON'T trip the band).
#   (2) the Qwen skeptic prompt (company/compliance/internal_audit.py) has no memory
#   of categories already adjudicated false-positive project-wide (gas-billed-in-
#   kWh is correct GB practice; VAT-mismatch and I&C-high-consumption have each
#   been manually verified correct at least once -- CLAUDE.md 2a, BILL_CORRECTNESS_
#   ADDENDUM) -- it will keep re-manufacturing the same non-findings forever even
#   with the NTFY fix above (they'll just log silently instead of spamming). A
#   "known non-issues" reference the prompt or a post-filter could consult is a
#   real design decision (what counts as adjudicated, who updates it) -- not a
#   one-line patch.
#
# === MARGIN_REALISM -- P1, IN PROGRESS (2026-07-10, docs/staging/done/MARGIN_REALISM.md,
#   advisor-staged, director-decided from a real observation: net margin % by year 10.2/13.6/23.3/
#   19.5/10.5/4.4/9.8/5.6/15.9/12.5, real UK domestic retail ~1-3% net with negative years --
#   levels ~5x too high, volatility far too high). Two permanent method laws adopted verbatim into
#   CLAUDE.md as R12 (anti-goal-seek: margin is a diagnostic, never a target) and R13 (baseline/
#   curriculum split: the real-history baseline only changes for fidelity reasons, the director's
#   curriculum is his own instrument, never silently tuned by the agent).
#   STEP 1 (fix the gauge, immediate) -- REAL PROGRESS, not fully closed: confirmed and evidenced
#   (docs/design/MARGIN_REALISM_STEP1_DIAGNOSIS.md) that `years[yr].revenue_gbp` (commodity-only,
#   settlement-based) and `management_accounts[yr].income_statement.revenue_gbp` (real double-
#   entry total revenue, net of VAT) disagree 26-52% every year -- neither is wrong, but the
#   percentages the director cited were computed against the smaller, commodity-only denominator,
#   inflating every year's reported margin. Fixed for the Financial tab specifically:
#   `tools/generate_dashboard_data.py::extract_financial()` now carries `total_revenue_gbp` +
#   `net_margin_pct` computed against it (10-yr average moves from ~12.5% to ~8.9% -- a real,
#   mechanically-explained correction, not a tuned output), surfaced on `site/supplier/index.html`'s
#   Annual P&L table with both revenue definitions clearly labelled. NOT YET DONE: reconciling
#   every OTHER surface that shows a revenue/margin figure against the same ambiguity, adding this
#   to the consistency gate, and the genuinely open question of which figure a real UK supplier's
#   own "net margin %" claim would be built on (total revenue almost certainly, but confirm before
#   treating this as final).
#   STEP 2 (per-year margin decomposition) -- CLOSED 2026-07-10:
#   docs/design/MARGIN_REALISM_STEP2_DECOMPOSITION.md. Gross margin (24.7-44.4%) is
#   plausible, not the problem. The single largest, clearest gap: saas/cost_to_serve.py's
#   opex model exists but is ONLY ever consumed per-customer/cumulative for CLV, NEVER
#   subtracted from the portfolio annual net_gbp -- a real missing cost line, matching
#   Step 3's mandate exactly. Cross-checked sim net% year-by-year against real EDF/British
#   Gas CSS EBIT% + Ofgem's own cap EBIT allowance (1.9%) already in ASSUMPTIONS.md --
#   2024 (11.6% sim vs 1.9-5.4% real) is the cleanest read, ~2-3x too high, consistent with
#   the missing opex line. FLAGGED for Step 4, not investigated further: hedge value-add is
#   negative every year 2016-2025, worst (-97.5% of gross) in 2022 -- the actual UK gas
#   crisis year, when a hedged supplier should show its BEST relative performance (naked
#   suppliers went bust in 2021-22, not hedged ones) -- backwards from expected shape,
#   unexplained, seeded for Step 4 rather than root-caused now (recently-touched
#   hedge-decision code, own sequenced turn).
#   STEP 3 (opex/cost-to-serve mechanism) -- IN PROGRESS 2026-07-10. Split into (a) true
#   third-party/industry costs charged fully and anchored (metering, DCC, payment
#   processing, print/postage, debt-collection, Elexon/Xoserve charges) -- REAL-ANCHOR
#   RESEARCH LANDED 2026-07-10 (docs/market_research/ASSUMPTIONS.md "MARGIN_REALISM Step 3"
#   section): DCC smart-meter comms charge, H-confidence, live-fetched from Smart DCC's own
#   RY26/27 Charging Statement -- £19.01/yr per domestic electricity smart meter, £14.32/yr
#   per gas smart meter (same rate domestic/non-domestic). Ofgem price-cap "operating, debt
#   and industry costs" allowance, H-confidence -- £297.92/yr (Direct Debit) / £441.10/yr
#   (Standard Credit) / £308.04/yr (Prepayment) per dual-fuel domestic customer, but
#   explicitly BUNDLED (opex+bad-debt+industry charges together) -- a double-counting risk
#   against separately-built industry-cost lines, flagged not silently used. GoCardless DD
#   processing fee (1%+20p, capped £4) and Royal Mail postage (91p/£1.80) as SME/retail-rate
#   benchmarks. Honestly-logged gaps, not invented: Elexon BSC + Xoserve UK Link charges
#   (sites blocked this session), MOP/DC/DA meter-service rates, bulk credit-check pricing.
#   NEXT: build (a) using the DCC figure now (clean, real, not bundled); use the Ofgem
#   bundled figure ONLY for the benchmark ledger (c), never inside the true (a+b) ledger,
#   per its own double-counting caveat. (b)
#   AI-compute + director-oversight hours at TRUE metered cost -- data-source check found
#   a REAL GAP: background/token_proxy.py's usage log (docs/observability/token-usage-
#   log.jsonl) only covers 2026-06-21 to 2026-06-25 (stopped 2+ weeks ago, ~$69.81 total --
#   not representative) and never captured THIS interactive session at all (no
#   ANTHROPIC_BASE_URL routing through it here) -- plus a genuine pricing-basis question
#   the agent should not silently resolve: Anthropic list/metered $/token price vs the
#   actual flat Max-20x subscription fee Rich pays (near-zero true marginal cost per extra
#   token under a flat plan) -- and the director's own oversight-hours rate is his call,
#   not a number to invent. (c) DUAL ledger (true vs benchmark-loaded with lower-quartile
#   incumbent labour cost per segment) -- anchors also part of the dispatched research.
#   BUILT 2026-07-10 (saas/opex_ledger.py, wired into tools/generate_dashboard_data.py +
#   site/supplier/index.html Financial section, sixth dial-weighted draw): (a) DCC comms
#   charge only (£19.01/yr elec, £14.32/yr gas per smart-metered account) -- other real
#   cost lines left at £0, not estimated, per R12 (payment processing/postage were
#   explicitly flagged SME-scale, not a real incumbent's unit cost; credit-check/debt-
#   collection/Elexon/Xoserve are genuine unresolved gaps). (b) hard 0.0, NOT silently
#   defaulted -- the two open questions (token-usage-log representativeness/costing basis;
#   director's own oversight rate) remain genuinely unresolved and are not the agent's to
#   invent, even under Tier 3 -- a placeholder $ figure feeding an "investor thesis" number
#   is exactly the kind of invented number R12 exists to prevent, so this stayed at 0
#   rather than picking a default. (c) Ofgem bundled allowance per household, NETTED of (a)
#   to avoid double-counting DCC (per the research's own recommendation) -- a partial, not
#   full, de-duplication (bad debt/other industry costs remain bundled inside it), honestly
#   documented. Real live portfolio result: true opex £99.99/yr vs benchmark £4,488.87/yr,
#   gap £4,388.88/yr -- the investor thesis, quantified, though understated on the true
#   side pending (b). 26 new tests (module + dashboard extraction), epistemic PASS, verified
#   via scratch generation (canonical dashboard.json untouched) + a Node harness for the new
#   HTML section (no undefined/NaN, degrades gracefully when opex_ledger is absent).
#   NEXT: (b)'s two open questions still need either director input or a genuinely
#   defensible default -- not invented by self-refill.
#   STEP 4 (hedge-tariff alignment) -- CLOSED 2026-07-10 (seventeenth dial-weighted draw,
#   docs/design/B3_HEDGE_TARIFF_ALIGNMENT_FINDING.md): verified, not assumed, that Step 4's own
#   goal ("cost locked when price is locked") is substantially ALREADY BUILT. Fixed/pass-through
#   tariffs: hedge decided once per term, held constant to the next renewal -- confirmed via real
#   2020 data (start_hf == avg_hf for the large majority of customers). Deemed (SVT-adjacent):
#   spot+premium, correctly NO forward hedge. Flex: weekly re-hedge at rolling reference, matching
#   its own short commitment horizon. One honest exception flagged, not glossed over: a few I&C
#   customers show hf changing within a year, plausibly genuine multiple real-world 3-6-month
#   renewals rather than a bug -- NOT independently re-verified against the raw per-term log
#   (not retained in the report-extracted shape this session worked from).
#   STEPS 5-6 (price-cap-binds mechanism, pressure-roadmap registration) -- NOT STARTED (the
#   price cap becoming binding is a baseline-fidelity change). Side-tagging rule (every commit:
#   SIM-BASELINE/CURRICULUM/SUPPLIER/WALL/REPORTING) applies going forward.
#   FOLLOW-UP found live via R11 (2026-07-10): the Step 1 code fix landed and passed tests but
#   was NOT reflected in the deployed dashboard.json -- process_run_complete.py's change-detection
#   fingerprint gate correctly treats "same underlying run figures" as skip-worthy, but has no
#   concept of "the CODE computing derived fields changed even though the run didn't." Manually
#   regenerated+deployed this once (verified live via curl, not committed-only). General fix
#   NOT built: needs a trigger that also fires on generator-script changes (e.g. hash
#   tools/generate_dashboard_data.py alongside the run fingerprint), registered here rather than
#   guessed at inline -- same class as the FORCE_REPUBLISH_FLAG hold-release mechanism, distinct
#   trigger condition.
#
# === MATURITY MAP v1.1 -- NOW THE GOVERNING FRAMEWORK, PARTIALLY INSTALLED (2026-07-10,
#   docs/staging/MATURITY_MAP_CANONICAL.md + MATURITY_MAP_v1.1.md, director-ratified
#   in-conversation with the advisor after two review rounds). "This IS the arc's territory --
#   all future phases name the capability cell(s) they move." Canonical doc installed at
#   docs/design/MATURITY_MAP.md (verbatim). NOT YET DONE, real remaining scope, each a
#   substantial phase in its own right, deliberately not rushed in the same stretch as the
#   install: (1) seed docs/design/maturity_map.yaml -- v1 SEED LIVE 2026-07-10 (director audit,
#   "is the dial-weighted draw actually wired -- evidence, not intent"): 30 real, evidence-backed
#   atoms across all 12 lanes (dials copied verbatim from Section 8's ratified equaliser), NOT
#   yet the full 60-120 target -- honestly a v1 starter set, expand incrementally at phase close
#   rather than fabricate the rest up front; (2) wire background/supervisor.py's self-refill to
#   draw from the YAML's dials -- DONE 2026-07-10, `_maturity_map_draw()` is now the PRIMARY
#   self-refill source (dial-weighted random.choices over atoms with level_current < level_target),
#   the old PRIORITIES.md-backlog-prose heuristic demoted to fallback-only. This was itself an R3
#   redesign: the demoted heuristic was found to be the root cause of a real 2h40m empty-agenda
#   idle hole (2026-07-10 11:00-14:40) -- it only scanned text after "## Backlog" for the exact
#   substring "NOT YET STARTED", which no real backlog bullet used verbatim by that date, and
#   was structurally blind to every "# ===" section above that heading (including everything
#   registered earlier this same session). 12 new tests, 443/443 background tests pass,
#   epistemic PASS. (3) render
#   the four views (function matrix / value-stream flow / campaign / activity) as toggles on the
#   Project tab, replacing the epoch-storytelling section built earlier today (2026-07-10) per
#   the map's own instruction ("replaces/absorbs... rather than duplicating it"); (4) adopt the
#   map's section-9 operating rules into CLAUDE.md verbatim (cells move only at phase close with
#   evidence past the loop; every staged phase names a capability id; silent simplification is an
#   R10-class defect); (5) retro-tag current in-flight work (segments, hedge-fix aftermath,
#   comments-box backlog) with capability ids; (6) start DISCOVER/FRAME for the two hot lanes
#   (W1 Market & Weather, D Billing & Metering) per the map's section 8 dials -- background-lane
#   research only, explicitly NOT epoch-2 BUILD work yet.
#
# === REGISTERED FOR NEXT P-5 RE-RANK, NOT STARTED (2026-07-08, docs/staging/BACKGROUND_LANE_AND_WALL.md
#   Part C, advisor-staged/director-approved): WALLED_INTERFACES programme -- full enforcement of
#   Architectural Law #2: every SIM/company crossing becomes a typed, versioned message through a
#   real-protocol-shaped adapter (simulated D-flows, DCC service request/response, customer message
#   bus). Strategic framing: the wall IS the go-live seam -- going live becomes swapping sim adapters
#   for real endpoints behind unchanged interfaces. Proposed sequencing: after the core-fidelity
#   block (CORE_FIDELITY_PHASES.md), before RY and scale-up. One-page decomposition sketch filed at
#   docs/design/WALLED_INTERFACES_SKETCH.md (candidate flows table, sequencing, explicitly NOT a
#   data-model rewrite or new epistemic rule -- a transport-shape change to already-correct data).
#   Awaiting director rank -- do not start the first reference-flow conversion without it.
#   AUDIT REFRESHED 2026-07-10 (seventh dial-weighted draw, W4_1_typed_adapters level 1->2,
#   FRAME-stage work per the map's Hardening Loop -- doc-only, no code touched): re-verified
#   all 5 candidate flows against current code, still accurate. Found a 6th already-typed
#   example the original sketch omitted: tools/market_data_port.py::MarketDataPort -- already
#   AT target shape (typed Protocol + every method takes an explicit as_of date,
#   point-in-time-safe by construction), directly cross-referencing the separate
#   W1_reveal_over_time DISCOVER finding as its natural reference implementation. Confirmed
#   the sketch's own tier reasoning still holds under the current recalibrated Tier 3 model
#   (no opt-out wait, but still flag-and-proceed, not build-without-flagging): the first
#   reference-flow conversion remains a real BUILD action still awaiting director rank per
#   this section's own standing instruction -- NOT started this turn.
#
# === CORE FIDELITY BEFORE LOOPS (2026-07-08, docs/staging/CORE_FIDELITY_BEFORE_LOOPS.md,
#   director-direct, in-conversation -- Tier 2, proceed, no opt-out window). THIS IS NOW P1,
#   AHEAD OF PHASE RY. Director's observation: the customer portal bill is still poor, the sim
#   has no unhappy-path errors/delays, customers have no household segments/psychology -- the
#   project has been going deeper into refinement loops (reputation, feedback, gap analyses)
#   while core SIM/software aspects remain undeveloped. Two of the missing items are
#   already-decided Epoch Three mission clauses never built ("time as a random variable" /
#   latency+unhappy-paths first-class; "brand as behavioural physics", which presupposes
#   customers with psychology). RY's reputation->acquisition loop would act on a homogeneous,
#   psyche-less population -- mechanically real but behaviourally hollow. Build the substrate
#   first.
#   PHASE RY IS DEFERRED, NOT CANCELLED -- re-enters the queue after this block closes.
#   Phase decomposition (agent-designed per the instruction's own delegation): see
#   docs/design/CORE_FIDELITY_PHASES.md.
#     Phase 1 (audits, cheap, no sim runs) -- DONE 2026-07-08: unhappy-path audit (5 confirmed
#       gaps: meter-read arrival/estimation/failure -- zero code, highest priority; bill
#       generation/delivery issued same-day as period-end with no lag; refund processing --
#       company/billing/credit_refund.py has a real SLA mechanic but is NEVER CALLED anywhere in
#       simulation/, dead code; contact-centre first-response time -- no module; switching-funnel
#       stage-to-stage calendar spacing -- all 5 stages resolve against one term_start date).
#       Household-segment archetype design (dimensions + psychology parameters + which existing
#       mechanisms each feeds) filed. Bill-artefact gap audit against the real UK-bill checklist
#       (standing charge/VAT/network pass-through/waterfall already present; meter serial,
#       actual-vs-estimated flag, per-bill payment method + running balance, back-billing
#       context, TDCV framing all absent).
#     Phase 2 (A implementation: household segments & psychology) -- Layer 1 CLOSED 2026-07-08
#       (Phase SC, PROJECT_OVERVIEW.md Section 4): simulation/household_segments.py gives each
#       customer a persistent ACTIVE/PASSIVE/DISENGAGED engagement archetype (Ofgem 2018 Consumer
#       Engagement Survey proxy shares, calibrated to preserve the existing anchored ~35% aggregate
#       active-renewal rate), replacing the flat per-renewal coin-flip in
#       company/crm/churn_model.py::is_active_renewal. 15 new tests, 16,129 collected, epistemic
#       PASS. Layers 2+ (fuel-poverty/income band, tenure, occupancy, payment-method mix,
#       complaint-propensity threading) remain backlog -- real anchors already registered in
#       docs/market_research/ASSUMPTIONS.md's "Household Segment & Psychology" section (ONS Census
#       2021, EHS 2023-24, DESNZ fuel poverty/payment-method releases), not yet threaded through
#       switching_propensity.py/feedback_survey.py/arrears_engine.py::payment_method(). A newer
#       Ofgem Oct 2025 active-share figure (~45%, vs the ~35% baseline preserved this pass) is
#       flagged for a separate director recalibration decision, not actioned unilaterally.
#     Phase 3 (B implementation: unhappy paths & time-as-random-variable, meter-reads first since
#       Phase 4 depends on it) -- CLOSED IN FULL 2026-07-08 (Phase RZ, PROJECT_OVERVIEW.md Section
#       4): all 5 audit gaps built and wired (meter-read arrival/estimation/failure --
#       simulation/meter_reads.py; SLC 14 credit-refund activation --
#       simulation/credit_refund_events.py; bill generation/delivery lag --
#       tools/generate_billing_ledger.py; contact-centre first-response time --
#       simulation/contact_centre.py; switching-funnel stage-to-stage calendar spacing --
#       simulation/acquisition_funnel.py). Evidence on the Sim tab (meter-read delay histogram).
#       47 new tests, 16,071 collected, epistemic PASS.
#     Phase 4 (C implementation: UK-compliant bill artefact) -- substantially CLOSED via a separate
#       staged doc rather than this queue entry (BILL_CORRECTNESS_ADDENDUM.md Defects 1-4, 2026-07-09,
#       CLAUDE.md Current state): billing period + opening/closing meter reads with A/E type + meter
#       serial + MPAN/MPRN now on every bill; consumption restructured as a `registers` list (ToU-
#       ready schema, ToU itself not built). Did NOT wait on Phase 2 Layers 2+ (household psychology)
#       -- the bill-artefact defects were structural/data-plumbing, independent of segment psychology.
#       Remaining Phase 4 scope: none identified: Defect 5 (I&C billing model) stays backlog per its
#       own doc, alongside WALLED_INTERFACES.
#   TOKEN ECONOMY CONSTRAINT RETIRED (2026-07-09, BUDGET_UNCONSTRAINED.md, actioned): director lifted
#   the token-conservation framing entirely (~44 days after the constraint above was first stated) --
#   frontier budget is to be used against the weekly allowance, not hoarded; the "weigh every action
#   for token cost" framing throughout this block is SUPERSEDED. Delegate to Qwen/GPU for quality and
#   speed, not to save tokens (see also CLAUDE.md's velocity-and-tokens guidance).
#   ALSO CLOSED SINCE THIS BLOCK WAS WRITTEN (2026-07-08/09, not yet reflected below at the time):
#   DOMAIN_SENSE_AND_COMPLIANCE.md (P1 compliance programme, 7 phases: obligations register, domain-
#   invariants library, pre-bill validation gate, risk-tiered compliance report, sanity daemon,
#   internal audit, phase-close audit) -- CLOSED IN FULL. THE SUPERVISOR (turn-granting architecture
#   rebuild, doorbell failure #4) -- CLOSED. Doorbell failure #5 (busy-spinner regex false positive)
#   -- CLOSED. Dead-man's switch (background/deadmans_switch.py, independent BLOCKED alert) --
#   CLOSED. DIRECTOR_COMMENTS_BOX.md (per-page feedback widget, PIN-authenticated) -- CLOSED.
#   EPOCH2_EVIDENCE_PASS (Q1-Q6 verdicts delivered) -- CLOSED, with one headline finding logged but
#   deliberately NOT fixed yet: a confirmed epoch-2 target that customer population must become a
#   per-run DRAW (not a fixed cast) discovered through company-observable interfaces only, never
#   read from SIM ground truth -- see docs/design/EPOCH2_EVIDENCE.md's headline section.
#   Phase 2 Layer 2 dimension 1 (payment-method mix) CLOSED same day (2026-07-09,
#   PROJECT_OVERVIEW.md Section 4 "payment-method-mix archetype" entry) --
#   simulation/household_segments.py::payment_channel_for_customer() (DESNZ DD-share anchors
#   72%/75% elec/gas), wired through arrears_engine.py/credit_refund_events.py/
#   generate_billing_ledger.py, verified live (72.8% observed DD share, Statement view shows
#   Standard credit for the non-DD population). Dimension 2 (fuel poverty / income band) ALSO
#   CLOSED same day (2026-07-09, PROJECT_OVERVIEW.md Section 4 "fuel-poverty archetype" entry) --
#   simulation/household_segments.py::fuel_poverty_for_customer() (DESNZ LILEE anchors 8.8% DD /
#   20.4% non-DD blend), wired as a bounded modifier into arrears_engine.py::payment_outcome();
#   new population-sanity check + SIM-tab evidence column. Dimension 3 (tenure) ALSO CLOSED
#   (2026-07-10, PROJECT_OVERVIEW.md Section 4 "tenure archetype" entry) --
#   simulation/household_segments.py::tenure_for_customer() (EHS anchors 65%/19%/16% owner/
#   private-rent/social-rent), wired into switching_propensity.py (renters switch less) and
#   customer_events.py. Dimension 4 (occupancy) ALSO CLOSED (2026-07-10, PROJECT_OVERVIEW.md
#   Section 4 "Occupancy archetype" entry) -- household_segments.py::occupancy_for_customer()
#   (ONS Census 2021 anchors), wired into feedback_survey.py's complaint propensity. ALL of
#   Layer 2's originally-named dimensions (payment-method mix, fuel poverty, tenure, occupancy)
#   are now CLOSED -- only complaint-propensity-as-its-own-archetype remains (arguably redundant
#   now that occupancy already feeds complaint propensity directly).
#   Genuine remaining front-of-queue: NUDGE_PHYSICS remaining mechanisms (P-5 item a) -- a fork
#   scoped this 2026-07-10 and recommends collections-letter tone/framing next (anchor already
#   cited in docs/market_research/NUDGE_PHYSICS_BENCHMARKS.md, extends arrears_engine.py's
#   already-built fuel-poverty modifier pattern, smaller scope than Layer 1). Already-approved
#   backlog item (Tier 2), not a novel proposal.
#   (Token-economy note retired -- see BUDGET_UNCONSTRAINED entry above.)
#   Event-driven wake (2026-07-08, director-direct, in-conversation, same reorientation
#   conversation): background/staging_watcher.py now injects one batched tmux turn into the live
#   session for genuinely-new staged files (ADVISOR-STAGED commits included, via the existing
#   Remote Staging Bridge) -- replaces the retired autonomous-runner's idle-poll wake with an
#   event-driven one. No new process, single-writer preserved, zero turns when nothing happens.
#   Live-tested using this exact CORE_FIDELITY_BEFORE_LOOPS.md arrival as the test case
#   (tmux capture-pane confirmed the injected text landed correctly, queued, no disruption).
# ADOPTED 2026-07-07 (docs/staging/done/STRATEGIC_HORIZON_DECISIONS.md, [ADVISOR-STAGED] fba4ae94, 2026-07-06): condition met -- P2 completed in full at Phase RW. Post-P2 ordering to adopt: S1 proof-first (shadow-live track record, public scorecard from day one, misses included), S2 depth-before-scale (customer physics/psychology -- feedback/reputation, nudge physics, life-event dynamics -- before population scale-up), S3 then scale (295->thousands, perf engineering, market-flows choreography), S4 products (casebook first, dataset second), S5 go-live routes memo (analysis only, advisor-owned). Also records Rich's latency-and-fidelity tiered-access commercial model hypothesis for the casebook/Platform/Method design once S4 opens.
# PENDING FOR NEXT WEEKLY RE-RANK (docs/staging/done/EPOCH3_DIRECTION.md, [ADVISOR-STAGED], 2026-07-06,
# arrived on this tree 2026-07-07): Part 1 (P1 visual approval recorded, P2 released in order) is
# moot -- P2 was already completed in full at Phase RW before this file was pulled. Part 2 (EPOCH
# THREE direction) is explicitly re-rank input only, NOT active queue now -- five mission clauses
# (mortality/longevity tournament as terminal-state endgame, brand as behavioural physics via
# causal cashflow channels + terminal-value multiple only, regulated experimentation within
# licence/consumer-duty limits, anchored-noise dual calibration, temporal realism as first-class
# latency distributions/doom-loops) plus the S2 "depth" build content (EPC/Census world texture,
# the Belief Book hypothesis register + time-to-truth convergence dashboard, multi-objective
# survive-and-compound function, capital allocation as a per-pound ROI budget) -- to be folded into
# S2's scope definition at the next weekly re-rank, recorded verbatim per the file's own instruction.
#   (2026-07-08 triage: a re-staged fuller copy, docs/staging/EPOCH_THREE_DIRECTION.md, was reviewed
#   and confirmed to carry the same director direction as the already-recorded EPOCH3_DIRECTION.md
#   above -- same re-rank input, no new active-queue item; archived to done/. Nothing here jumps the
#   queue per the file's own sequencing guidance.)
# Last refreshed: 2026-07-06 (PRIORITY RESET, docs/staging/PRIORITY_RESET_PUBLIC_SITE.md,
# [ADVISOR-STAGED] 5fa9a0cf -- Tier 2, pre-approved). Rich's direct verdict: the public site
# (poesys.net's four top-level tabs) is still structurally pre-overhaul despite backend depth
# (SIM tab QY-RC, Project generators RD/RG, portal design tokens QO) shipping. THE PUBLIC SITE
# IS NOW P1, ahead of further backend depth (CTS reconciliation, frozen-policy baseline,
# FEEDBACK_AND_REPUTATION, NUDGE_PHYSICS, SAAS_COVERAGE_MAP all demoted to P2, resume after P1
# lands + Rich confirms visually). "Overhaul" means structure/nav/tab-order/layout/per-fuel
# separation on the REAL site (site/{index,sim,customers,project} + the portal), not the shadow
# mirror, not a CSS palette flip.
#
# NEW ORDER (work top-down, single-writer, each Tier 2/pre-approved):
# P1a. CUSTOMER 360 v4 (docs/staging/CUSTOMER_360_REDESIGN.md) -- CLOSED IN FULL (Phase RL,
#   2026-07-06). Household w/ TWO first-class accounts (elec MPAN + gas MPRN, own tariff/meter/
#   consumption/bills/P&L each), combined roll-up OPTIONAL only; tabbed IA (Overview/Accounts/
#   Consumption/Billing/Timeline/Risk); usage viz (volume+shape+weather overlay); bill equation +
#   why-different waterfall; QP event ledger as timeline; progressive disclosure; UK lens (MPAN/
#   MPRN/p-kWh/EAC/PSR). GAS/ELEC SEPARATED AT EVERY STAGE, the specific repeated complaint, done
#   throughout. (Phase RI: v3 item 1 usage-chart rendering. Phase RJ: tabbed IA + account
#   separation. Phase RK: item 2, bill equation + why-different waterfall, real billing_ledger.json
#   data wired in place of the old fabricated seasonal-weight invoices. Phase RL: items 3-4, real
#   per-event effects on the Timeline (renewal rate steps / usage before-after / income-stress
#   drift) + a reaction-chain panel reusing decision_event_ledger.build_customer_ledger.)
#   AWAITING RICH'S VISUAL CONFIRMATION per the P1 acceptance rule below -- report as such, not "done".
#   REOPENED (2026-07-06, docs/staging/BILLING_AND_PAYMENTS_LEDGER.md, [ADVISOR-STAGED] 8a8f2e81,
#   Tier 2, Rich's own directive labels it "P1a scope, continue on the 360" after live review --
#   P-2 director-repeat rule applies): Billing tab -> BILLING & PAYMENTS.
#   CLOSED IN FULL (confirmed live in site/customers/index.html during the 2026-07-09 PRIORITIES.md
#   freshness pass -- shipped in an earlier phase without a matching queue update, caught by phase-
#   close checklist step 0): (1) bill equation renders inline (`billEquationHtml()`); (2) STATEMENT
#   view (`renderStatementView()`, BILL_VIEWS tab) -- chronological ledger with running balance; (3)
#   CASHFLOW panel (`renderCashflow()`/`renderCashflowShell()`) with a page-level `reconciliationLine()`
#   tying collected cash to lifetime_revenue minus outstanding balance; (4) payment-method shown on
#   the statement. AWAITING RICH'S VISUAL CONFIRMATION per the P1 acceptance rule -- report as such.
# P1b. SUPPLIER TAB IA (docs/staging/SUPPLIER_TAB_OVERHAUL.md) -- CLOSED IN FULL (Phase RM,
#   2026-07-06). Phase RH closed the core IA regroup (grouped nav + Query FAB); RG closed
#   Capabilities->Project + Regulatory RAG + Worst-Shock-Month annotation; RM closed the
#   remainder: portfolio event stream as the Commercial group's centerpiece tab (real, 122
#   live events), Recommended Actions elevated to Overview ("What the Board Should Do Next"),
#   heatmap click-through to customer 360 + year (site/customers/index.html deep-linking).
#   AWAITING RICH'S VISUAL CONFIRMATION per the P1 acceptance rule below -- report as such, not "done".
# P1c. SIX-SECTION NAV + STORY (docs/staging/NAV_STORY_PLATFORM_METHOD.md) -- CLOSED IN FULL
#   (Phases RO/RQ, 2026-07-06). Home/Story landing + Platform section (Phase RO); METHOD section
#   (operating model, R1-R6 + forging incidents, live staging-loop view, retro library) + PROJECT
#   tab slim-down (Company->Method, Capabilities->Platform) (Phase RQ). AWAITING RICH'S VISUAL
#   CONFIRMATION per the P1 acceptance rule below -- report as such, not "done".
# P1a/b/c ALL CLOSED IN FULL as of Phase RQ, 2026-07-06. WEBSITE_AS_SHOWCASE.md tab 4
#   (case-study recommender) CLOSED (Phase RR, 2026-07-06) -- new tools/generate_case_study_recommender.py
#   auto-curates 5 real "interesting customers" (most eventful / largest churn-model divergence /
#   retention-save-then-churned-anyway / heaviest arrears cascade / notable life event) onto
#   site/customers/index.html's login page, linking into each household's Timeline. WEBSITE_AS_SHOWCASE.md
#   tabs 2 (frozen-policy baseline) and 3 (learning ledger) remain open, gated behind Rich's visual
#   confirmation of P1a-c below -- not started. Phase RR also archived 4 staged docs
#   (CUSTOMER_360_REDESIGN.md, SUPPLIER_TAB_OVERHAUL.md, NAV_STORY_PLATFORM_METHOD.md,
#   PROJECT_TAB_OVERHAUL.md) to docs/staging/done/ that were already CLOSED IN FULL above but never
#   moved out of the active queue -- a hygiene gap, not a scope gap.
# P2 -- CLOSED IN FULL (2026-07-07, Phase RW). Started 2026-07-06 21:05 BST on Rich's visual
#   confirmation via NTFY: "I like the live site a lot. It's a big improvement" (satisfies the
#   P1a-c acceptance rule below). Five items, all closed: (1) CTS £0/£91,780 reconciliation --
#   CLOSED (Phase RS, 2026-07-06): account 6100 posts a real monthly cost-to-serve figure. (2)
#   frozen-policy baseline -- CLOSED (Phase RT, 2026-07-07): swappable DecisionPolicy struct,
#   delta-EV £159,745 on the live book, "The Value of Learning" on Supplier Overview. (3)
#   FEEDBACK_AND_REPUTATION.md Layer 1 -- CLOSED (Phase RU, 2026-07-07): solicited CSAT/NPS
#   survey + complaint dispatch engine, evidence on all 3 surfaces. Layer 2 (public reviews,
#   regulator star-rating, funnel feedback loops) NOT built -- FEEDBACK_AND_REPUTATION.md stays
#   open in docs/staging/ for it. (4) NUDGE_PHYSICS.md Layer 1 -- CLOSED (Phase RV, 2026-07-07):
#   hidden per-customer loss-aversion susceptibility modulates retention-offer effectiveness,
#   company discovers the lift empirically. 7 of 8 NUDGE_PHYSICS_BENCHMARKS.md mechanisms remain
#   backlog. (5) SAAS_COVERAGE_MAP.md -- CLOSED (Phase RW, 2026-07-07): docs/architecture/
#   SAAS_COVERAGE_MAP.md maps 22 SaaS categories to an eliminated(A)/recreated(B)/interfaced(C)
#   taxonomy (5 A / 10 B / 7 C), rendered on site/platform/index.html. Backlog items (debt-sale/
#   DCA-placement economics, credit bureau as a collections-strategy feed) explicitly deferred.
# Next (adopted 2026-07-07, Phase RW close -- see PENDING FOR NEXT WEEKLY RE-RANK note above:
#   "P2 completes first as already agreed", condition now met): S1 proof-first (shadow-live
#   track record, public scorecard from day one, misses included) -- CLOSED by Phase RX
#   (2026-07-08, Options A rolling live Elexon fetch AND B two decoupled clocks).
#
# === DIRECTOR SEQUENCE + P-5 RE-RANK (2026-07-08, docs/staging/DIRECTOR_SEQUENCE_AND_TOKEN_
#   ECONOMY.md, director-confirmed "I agree"). Token economy is a P1 CONSTRAINT this week: ~48%
#   of the weekly usage allowance already spent by Wednesday morning (partly the identical-result
#   auto-process loop). Weigh every autonomous action for token cost; prefer bounded/cheap/
#   verifiable work; defer expensive novel work toward the weekly reset. ===
#   Sequence (director-set, executed this session unless noted):
#     1. Runner true-retirement (R2) + change-detection gate on the auto-process pipeline.
#        DONE 2026-07-08: change-detection gate live + tested (background/process_run_complete.py
#        fingerprints each run's headline figures + UTC date; identical => skip regen/test/commit;
#        dozens of identical £1,535,308 commits/day eliminated). Runner: launcher already commented
#        out (no respawn); orphaned autonomous_runner process killed as this session's final act.
#     2. WEBSITE_FRESHNESS_AND_DEDUP.md (P1, director-repeat) -- DONE 2026-07-08: single generator-
#        owned build stamp derived live from CLAUDE.md (no page carries its own phase/test/date
#        literal); Supplier reputation collapsed to one 3-step narrative; em-dash escaping; LATEST.md
#        narrative brought current RU->RX. Remaining (reported to Rich): consistency-gate extension
#        to phase/test/financials incl shadow-vs-live (item 2); RX scorecard placement on Sim/
#        Supplier tab (item 5, currently on Method page).
#     3. Phase RY (FEEDBACK_AND_REPUTATION Layer 2, reputation feedback loop) -- ENDORSED but
#        DEFERRED start: proceed only after 1+2 are consumer-verified, and PREFER starting after
#        the weekly reset given the 48% burn. Scope/design approved as filed (NEXT_PHASE.md); no
#        new opt-out window needed.
#   P-5 re-rank of the POST-RY backlog (director-set order):
#     (a) NUDGE_PHYSICS remaining mechanisms (Layer 2 breadth).
#     (b) Hedge-outcome grading -- PARKED until enough shadow-live entries accumulate to grade;
#         re-propose with the entry count as evidence of readiness.
#     (c) Live NBP gas source -- BLOCKED pending a Tier 1 director decision on the external endpoint;
#         prepare the decision brief (candidate sources, cost, verification plan), connect nothing.
#   S2 (depth-before-scale: customer physics/psychology) through S5 (go-live routes memo) follow
#   per STRATEGIC_HORIZON_DECISIONS.md's sequencing.
# Acceptance for every P1 item: Rich's eyes on the live public page -- report "awaiting Rich's
# visual review", never "done" outright.
# Already-staged infra fixes (SERIALIZE_WORKERS.md, FLAG_ALL_LAUNCHERS.md, PAGES_CONCURRENCY_FIX.md)
# were actioned prior to this reset -- see docs/staging/done/.

## COMPLETED
- P1 (process model, acquisition funnel): PROCESS_NOT_EVENTS.md's quote->application->
  credit_check->onboarding->cooling_off funnel (simulation/acquisition_funnel.py,
  tools/credit_bureau_port.py + synthetic_bureau adapter -- all pre-existing from an
  interrupted session, completed and wired this phase) replaces the flat coin-flip roll
  in run_phase2b.py's home-move replacement acquisition. Evidence on all 3 surfaces: Sim
  tab per-year stage leakage + win rate + population-anchoring RAG check; Customers tab
  one named won attempt, preferring a real credit-bureau-vs-ground-truth divergence case;
  Supplier tab portfolio stage leakage + real blended CAC. 11 new tests, full slow
  integration suite re-run clean. Epistemic: PASS.
- P1 (billing depth): Arrears states + dunning cycles + emergent bad debt -- DONE (Phase QD).
  simulation/arrears_engine.py: arrears_stages()/ic_arrears_stages() model the full missed-payment
  -> FIRST_NOTICE -> SECOND_NOTICE -> RESOLVED|WRITTEN_OFF cascade per customer (resi + I&C dispute
  variant); compute_emergent_bad_debt()/apply_emergent_bad_debt() replace the flat get_bad_debt_rate()
  formula with real written-off arrears. KEY FINDING: flat-rate bad debt was £92,550.88; real emergent
  figure is £3,051.07 -- confirms the PP/PW/NU infrastructure PRIORITY 1's note flagged was already
  most of the way there; QD closed the remaining "bad debt emerges from arrears, not a formula" gap.
- P1a: PROJECT_STATE.txt auto-sync -- FIXED (Phase PT; GH Pages fix 2026-07-04)
- P1b: customer_sample.json + customers.json + supplier.json at stable fetchable paths -- DONE (Phase PT)
- P1c: Shadow HTML site (4 sections) -- DONE (site/shadow/* auto-regenerating on every run)
- P2 (billing): Billing & Payment Infrastructure -- DONE (Phases PP/MW/MX/MY/NH)
- P2 (network): Network Charge Year-Indexed Actuals -- DONE (Phase 78; PROJECT_OVERVIEW.md Sec 9 gap closed)
- P3: Population Anchoring -- DONE (Phases NS/PQ/PR/PS: switching, churn, complaints, arrears)
- P4: Shadow Live Operation -- DONE (Phases PU/PV: live decisions + market adapter)
- Correlated market generator: Correlated Synthetic Market Generator -- DONE (Phase PX: bivariate OU adapter; Phase PY: equivalence gate PASS)
- Scenario stress testing: Phase PZ -- 4 scenarios; QUANTIFIES residual regime-change exposure for the board
  (correction 2026-07-04: PZ does NOT close regime-change blindness -- the 85% hedge floor closed it
  historically; PZ adds board-facing visibility into residual exposure. Claims must match artifacts.)
- P1 (churn recalibration): DONE (Phase QA fixed the churn_estimate_error_pct ground-truth comparison bug;
  Phase QB added market_conditions_multiplier so passive estimates vary 3-22% by year instead of pinning
  at a flat 5-10% floor). Residual: I&C estimates still hit the 0.95 ceiling -- noted as a follow-on, not
  blocking.
- Churn model validation loop rerun (2026-07-04, WEEKEND_ACCELERATION.md Q4): reran recall/precision/F1
  on the live production run (docs/reports/run_output_latest.json) with QA+QB in place. Result: TP=0,
  FP=6, FN=6, recall=precision=F1=0.0 at the 0.30 threshold -- UNCHANGED from the structural limitation
  Phase NK already documented (passive SVT-rollers capped at PASSIVE_CHURN_CAP=0.10 pre-multiplier in
  company/crm/churn_model.py:estimate_passive_churn_probability). ROOT CAUSE CONFIRMED: the market
  multiplier is applied AFTER that cap, and its max value (2.17x, year 2016) can only lift the passive
  estimate to ~0.217 -- structurally below the 0.30 classification/RETENTION_THRESHOLD regardless of
  market conditions, so the multiplier fix cannot move recall for this segment without either raising
  the cap or lowering the threshold. company/analytics/threshold_sensitivity.py (already wired, Phase NO)
  independently confirms this: optimal_threshold=0.00 (flag everyone) with F1=0.176 vs current threshold
  0.30 with F1=0.000 -- no positive threshold currently separates churners from renewers at all.
  NOT auto-fixed: lowering RETENTION_THRESHOLD to chase recall means offering paid discounts to the
  ~34 false-positive renewals the 0.05 threshold would also flag (precision 0.081 there) -- a real
  spending-policy tradeoff, not a mechanical bug. Flagged for Rich, not actioned autonomously. NOT a
  regression -- Phase NK predicted exactly this ("passive churns are below detection threshold by
  design"); QB improved estimate accuracy (mean error 1.25->1.00 per Phase QB) without ever being able
  to move TP/FP/FN counts for this segment. Q4 in WEEKEND_ACCELERATION.md CLOSED on this measurement;
  no code changed.
- Website data integrity Part A: DONE (Phase QC, staged WEBSITE_INTEGRITY_AND_DESIGN.md) -- fixed the
  step-ordering bug that put a stale Executive Summary next to correct 10-Year Totals on the same page, and
  replaced the hardcoded phase/test-count site header with docs/observability/build_info.json.
- Shadow-live decision log persistence: DONE (Phase QE) -- append_decision_log() writes
  site/state/live_decisions_log.jsonl, one immutable entry per UTC calendar day, closing the gap where
  run_decisions() silently overwrote the same dated snapshot every cycle and no track record accumulated.
- Website data integrity Part C (permanent per-run wiring): DONE (Phase QF) -- widened the Part A
  consistency gate from a single net-margin check to 8 headline metrics (net/gross margin, enterprise
  value, bills, committee interventions, retention offers/retained, churn count) compared across the
  dashboard totals vs run_insights.json exec-summary source; a mismatch now NTFYs Rich immediately instead
  of only printing to a log nobody watches in real time (generate() propagates the gate result instead of
  discarding it). Freshness stamps (git commit + phase, not just a timestamp) added to every shadow page
  footer. KEY FINDING: the widened gate immediately caught a real, pre-existing gross-margin discrepancy
  (dashboard £6,452,603 vs exec-summary £6,467,309, ~£14.7k / 0.2%) caused by tools/generate_insights.py
  preferring the _ledger_headline subtotal over total_gross_gbp -- the same class of bug Part A fixed for
  net margin, just never applied to gross. Fixed at root (precedence flipped to match net margin's and
  extract_portfolio's convention). Part B (design system + customer portal per-fuel legs) is the only
  remaining scope from the staged instruction.
- GitHub Pages advisor-verification mirror: DONE (Phase QG, docs/staging/ADVISOR_GITHUBIO_MIRROR.md) --
  poesys.net (Cloudflare Pages) proven persistently stale on the advisor's own fetch path specifically
  (cache-busted fetch still returned an 08:35Z generation while CC's direct fetch of the same URL at
  17:58 returned the current one), independent of any CD incident. tools/mirror_github_pages.py copies
  site/shadow/ -> docs/shadow/ and the 4 named state JSONs (customer_sample, billing_ledger,
  population_anchoring, sim_data) -> docs/state/ every run (same generator pass, no regeneration);
  wired into process_run_complete.py's site-generation + git_commit_push staging list. docs/status/
  PROJECT_STATE.txt Key Files section now lists the github.io URLs as the advisor-verification channel,
  poesys.net kept as the visitor-only surface. Also fixed a related bug found while touching this file:
  generate_project_state.py::_parse_phase_and_tests() picked the phase with the HIGHEST reported test
  count rather than the most recent one -- since the fast-suite total isn't monotonic across phases,
  this had silently regressed PROJECT_STATE.txt's "Current Phase" label to an older phase (PZ instead
  of the actual QF) whenever a later phase reported a smaller count.

## ORDERING NOTE (2026-07-04, advisor steer)
Phase PZ (scenario stress testing) jumped the queue: ADVISOR_CONFIRM_STATE_FRESH.md released the
correlated-generator hold WITH explicit conditions -- it stays BACKLOG behind P1 below until it's
DELIVERED, not just listed. No further generator/scenario phases until P1 below is complete.

## COMPLETED (cont.)
- Website Integrity Part B (Professional Design System): DONE (Phase QN + Phase QO, 2026-07-05).
  QN closed the per-fuel-legs data-completeness half -- Customers tab no longer drops gas legs
  (`if cid.endswith("g"): continue` removed), both fuel legs shown as separate accounts, a
  "Combined Roll-Up" table added as an explicit optional secondary view, and a per-fuel case study
  (C_IC3/C_IC3g) shows real invoice/arrears/failed-payment history per leg from billing_ledger.json
  -- live run shows the gas leg carrying a real -GBP89,641 arrears balance the electricity leg (0
  failed payments, 0 arrears) has none of, proving why the legs must stay separate.
  QO closed the design-system half -- company/portal/templates/base.html centralizes design tokens
  (palette/spacing/typography) and shared components (kpi-card, rag-chip, banner, btn, consistent
  nav with active-page highlighting) across all 19 customer portal templates, replacing 19
  independent inline <style> blocks; matching kpi-card/rag-chip CSS added to the shadow mirror
  (dark advisor-verification theme, kept intentionally distinct from the portal's light customer
  theme); population_anchoring.json (computed since Phase PQ, never rendered anywhere) now surfaces
  as real rag-chips on the Sim tab. See docs/staging/done/WEBSITE_INTEGRITY_AND_DESIGN_PARTA_DONE.md
  for the full original staged instruction.

## COMPLETED (cont. 2)
- Decision Event Ledger Part 5: DONE (Phase QP, 2026-07-05, docs/staging/DECISION_LOOP_AND_EVENT_LEDGER.md).
  company/analytics/decision_event_ledger.py unifies the per-topic case studies built independently
  across QI/QJ/QL/QM (behavioral signal, renewal decision, churn journey, retention deferral) into
  one real chronological timeline per customer (Customers tab: C_IC1, the flagship divergence case --
  2018-01-31 retention decision, company believed 95% churn risk / EV GBP139,477, immediately followed
  by the real outcome, SIM truth 4%, in one ordered feed) plus a portfolio-wide feed (Supplier tab:
  most recent 150 decisions/outcomes, filterable by event type, plain JS). FOUND AND FIXED EN ROUTE:
  Phase QL's churn_journey_log was computed by run_phase2b but never forwarded through
  saas/reporting/annual_report.py::extract_report_data() -- had been silently empty in every
  production run since QL shipped. 17 new tests.

## COMPLETED (cont. 3)
- Decision Event Ledger Part 4 + 0.95-ceiling calibration fix: DONE (Phase QQ, 2026-07-05,
  docs/staging/DECISION_LOOP_AND_EVENT_LEDGER.md, remaining scope). company/crm/churn_model.py:
  hard clamp at MAX_CHURN_PROBABILITY replaced with an asymptotic saturating curve above
  CHURN_SATURATION_ELBOW=0.90 (identity below it -- every previously-unclamped estimate
  unchanged); genuinely different elevated risk levels (60% vs 150% I&C rate rise) now read
  as distinguishable values instead of both collapsing to the same 95% ceiling -- the exact
  C_IC1-class bug. company/analytics/counterfactual_retention.py: compute_counterfactual_lift_by_class()
  classifies every no-offer churn as detection_gate (model problem) or uneconomical_{high,medium,low}
  (economics problem), each scored under H3 (effectiveness scales 0.04 per discount point,
  anchored so the medium tier reproduces the old flat 0.20 assumption); produces real
  lift-per-pound per class, wired into the board's Counterfactual Retention & Threshold
  Optimisation section. 26 new tests, 15,498 collected.

## COMPLETED (cont. 4)
- PROCESS_NOT_EVENTS.md: FULLY DELIVERED, all three items in its declared sequence (2026-07-05).
  Churn journey (Phase QL) -> acquisition funnel (Phase QR) -> debt-branch (Phase QS: DCA
  placement/recovery/sale past WRITTEN_OFF, with debt_archetype() OVERWHELMED/AVOIDANT/NEUTRAL
  behavioural split generalizing QD's arrears pattern). SAAS_COVERAGE_MAP.md item 3
  (DCA-placement/debt-sale) folded into QS as designed. Staged instruction archived
  (docs/staging/done/, "Archive PROCESS_NOT_EVENTS.md" commit 56df5f86). SAAS_COVERAGE_MAP.md
  item 4 (credit bureau as boundary feed) partially done -- QR wired credit bureau into
  acquisition credit checks; the collections-strategy half is not yet fed by the same feed
  (minor backlog item, not blocking).

## PRIORITY 1 -- WEBSITE_AS_SHOWCASE.md design wave (six staged Tier-2 directives)
Staged 2026-07-05: NAV_STORY_PLATFORM_METHOD.md, WEBSITE_AS_SHOWCASE.md, SIM_TAB_OVERHAUL.md,
SUPPLIER_TAB_OVERHAUL.md, PROJECT_TAB_OVERHAUL.md, CUSTOMER_360_REDESIGN.md -- all Tier 2,
structure pre-approved by the directives themselves; Rich's eyes are the acceptance test for
each visual landing, not a code review.
Front of queue per WEBSITE_AS_SHOWCASE.md's own sequencing note: **Part 0** -- Phase QO
(design-system unification) styled company/portal/templates/ (the internal Flask portal)
instead of site/ (poesys.net, the four public tabs Rich actually looks at) -- a verification
failure, redo on the correct surface. Paired with **tab 1** (SIM tab living-world: event
frequency panels, journey-stage flows, correlation panels) since the underlying data already
exists (QL journey states, population anchoring, income-stress/satisfaction trajectories) --
no new SIM capability needed, only surfacing what is already computed.
STARTED 2026-07-05 (Phase QT, in progress): while auditing the SIM tab against
SIM_TAB_OVERHAUL.md's critique ("header cards say 0 moderate-stress while the table shows
C7/C8 moderate; Tenure and Satisfaction columns are dead -- every row a dash"), found the
root causes go deeper than styling -- three separate JS bugs on site/sim/index.html's
Customers sub-tab: (1) case-sensitivity (SIM emits lowercase 'low'/'moderate'/'high', JS
compared against uppercase literals -- silently broke the KPI header count, the stress
distribution chart, AND the per-row colour coding, not just the header/table contradiction
Rich saw), (2) `payment_behaviour_analytics.current_score` read a field that has never
existed (real key: `.score`) -- broke the Payment Behaviour Score Distribution chart, every
customer defaulting to GOOD, (3) `tenure_years` and `satisfaction_score` read fields that
don't exist on the customer record at all -- Tenure/Satisfaction columns were structurally
incapable of showing data. Root-caused (3): satisfaction had never been retained as a
per-year history, only a rolling current scalar (company/crm/satisfaction_accumulator.py) --
tools/generate_customer_sample.py hardcoded satisfaction_score_trajectory to None with a
"pending_sim_emission" status. Fixed at root: accumulator gains record_year_snapshot()/
get_trajectory(); simulation/run_phase2b.py snapshots at each renewal's term_start_str year;
generate_customer_sample.py wires the real trajectory through; site/sim/index.html computes
tenure from acquisition_date (fixed SIM_END_DATE=2025-12-31 reference, matching the 10-year
sim window) and reads the last trajectory point for satisfaction. 6 new/updated tests
(satisfaction accumulator trajectory + generate_customer_sample field passthrough), fast
suite re-run clean. NOT YET DONE: needs a fresh production sim run to emit real trajectory
data end-to-end (verified via unit tests only so far -- the live site/data/customer_sample.json
still shows the old null until the next natural sim_runner cycle regenerates it), and the
rest of WEBSITE_AS_SHOWCASE Part 0 + tab 1 (event frequency panel, journey-stage flows,
correlation panels, light-theme completion started by a prior ADVISOR-STAGED commit but not
finished) remains open.
CONTINUED 2026-07-05 (Phase QT, same session resumed after a restart): verified the trajectory
fix end-to-end against a fresh production run that completed mid-session (git 03fa5747) --
site/data/customer_sample.json now carries real per-year satisfaction history (e.g. C1: 2016
0.7, 2017 0.7, 2018 0.65) instead of null, closing the "NOT YET DONE" item above. Also shipped
JOURNEY STAGES LIVE (first slice of the "journey-stage flows" item): new "Customer Journey
Stages -- the Behavioural Pulse" section on the Customers sub-tab reads QL's journey_log
(already computed, dashboard.json, 92 entries/15 customers/4 states -- content/irritated/
in_market/comparing) and shows (a) current stage distribution as KPI cards (live run: 12
content, 1 irritated, 0 in-market, 2 comparing) and (b) a stacked bar chart of stage counts
per year 2016-2025, visibly showing in_market appearing in the 2022 crisis year. Verified with
a node harness executing the real data-transform functions against the live dashboard.json
(no browser tool available in this session) plus `node --check` for syntax -- both clean.
CONTINUED 2026-07-05 (Phase QU, same wave): shipped the remaining two of the four
"distributions" dimension -- Satisfaction Score Distribution (5 bands, critical/poor/fair/
good/excellent, stacked per year 2016-2025 from satisfaction_score_trajectory, already
computed by the Phase QT accumulator fix) and Switching Propensity Distribution ("the
Vulnerability Trap": each customer's income-stress trajectory point mapped through
simulation/switching_propensity.py's fixed multiplier -- LOW x1.10, MODERATE x0.85, HIGH
x0.65 -- no new SIM field, purely derived client-side from data the Income Stress chart
already displays). All four distribution dimensions (income stress, payment score,
satisfaction, switching propensity) are now live on the Customers sub-tab. Verified by
reimplementing both binning functions in Python against the live site/data/customer_sample.json
and confirming sane, crisis-consistent output (e.g. satisfaction "fair" band rises and "good"
drops in 2021-2022; switching-propensity "high" count dips exactly in the 2022-2024 stress
years) -- no node available in this session, `python3 -m tools.epistemic_verifier` PASS
(no company/saas files touched, site/ is presentation-only). Epistemic verifier PASS.
CONTINUED 2026-07-05 (Phase QX, same wave): event frequency panel was already shipped in QV.
This phase closes the remaining three tab-1 bullets: correlation panels (income stress vs
payment delay rate, and wholesale price vs journey-log in-market entries -- both from data
already computed; satisfaction vs complaints left as an explicit honest gap, complaints still
not wired into the live sim), per-customer click-to-expand trajectory sparklines (Customer 360
link honestly noted as pending CUSTOMER_360_REDESIGN.md -- that page doesn't exist yet, no dead
link fabricated), and a portfolio-scale Both-Sides-of-the-Wall strip (churn_accuracy_by_renewal's
sim vs company-estimated churn probability, aggregated per year -- shows the divergence narrowing
after Phase QQ's calibration fix). Tab 1 (SIM tab living-world) is now DONE except items 1-3
(Prices/Weather/BM sub-tab rebuilds, not part of item 4) and item 5 (site-wide consistency gate +
light theme). Rich's eyes are the acceptance test -- awaiting visual review.
Tab 2 (Supplier: frozen-policy-baseline delta-EV) needs its own Tier 3 design note first
(policy snapshot/replay is one-way-door-adjacent) -- do not start implementation before that
review lands. Tab 3 (Project: learning ledger) assembles as 1/2 land.
CONTINUED 2026-07-05 (Phase QY): SIM_TAB_OVERHAUL.md item 1 (PRICES -> MARKET) DONE -- selectable
price-chart overlay (HDD/Short%/Gas NBP), negative-price-hours/year chart, and a real year->month->
day progressive-disclosure drill-down on the annual table (daily rows built lazily, not pre-baked).
8 new tests, 15,595 collected, epistemic PASS. Tab 1 (SIM tab) now has only items 2 (Weather physics
chain), 3 (BM axis legibility), and 5 (consistency gate + light theme) remaining.
CONTINUED 2026-07-05 (Phase QZ): item 2 (Weather -> Physics Chain) DONE -- band chart replaces
spaghetti temp chart, new episode panel chains HDD -> price -> Short% for two named crisis
episodes. 4 new tests, 15,591 collected, epistemic PASS. Tab 1 now has only items 3 (BM axis
legibility) and 5 (consistency gate + light theme) remaining.
CONTINUED 2026-07-05 (Phase RA): item 3 (BM axis legibility) DONE -- both BM charts' x-axis fixed
to match the Prices/Weather convention, plain-language Short%/NIV explainer added, Crisis Zone
band added to the SSP-vs-Short% chart matching the Prices tab's same window, real cross-tab link
added. Presentation-only, no new tests, epistemic PASS. Tab 1 (SIM tab) now has only item 5
(site-wide consistency gate + light theme) remaining -- the last item before Tab 1 is fully DONE.
CONTINUED 2026-07-05 (Phase RB): freshness stamp (git_hash/phase) threaded into sim_data.json
metadata + an orphaned Customers sub-tab consistency-gate test committed. Item 5 partial --
freshness stamp still missing on Weather/BM/Customers sub-tabs, light theme unconfirmed.
CONTINUED 2026-07-05 (Phase RC): item 5 CLOSED -- freshness stamp extended to the three remaining
sub-tabs (shared freshnessSpan() helper reusing sim_data.json's metadata for Weather/Customers,
new buildBmMeta() for BM); weather.json's own generator now carries git_hash/phase too. Light
theme confirmed already shipped site-wide on site/sim/index.html, no work needed. SIM_TAB_OVERHAUL.md
now CLOSED IN FULL. Tab 1 (SIM tab) DONE. Found, not actioned: site/shadow/{index,customers,
supplier,project}/index.html still on the pre-v4 dark terminal-monospace theme -- WEBSITE_AS_SHOWCASE.md
Part 0 / PROJECT_TAB_OVERHAUL.md / SUPPLIER_TAB_OVERHAUL.md scope, front of queue next.

## COMPLETED (cont. 5)
- PROJECT_TAB_OVERHAUL.md R-A/consistency partial + WEBSITE_INTEGRITY_AND_DESIGN QW Part 2:
  DONE (Phase RD, 2026-07-05). site/data/phases.json regenerated from docs/PROJECT_OVERVIEW.md
  Section 4 via new tools/generate_phases_json.py (was hand-curated, frozen since 2026-07-03 at
  latest_phase OL) -- wired into process_run_complete.py so it self-updates every run. Fixes
  the stale Timeline, frozen Capabilities cards, and the corrupted Test Progression/
  Phases-per-day charts (duplicate x-axis labels). Also fixed the Project tab's "Sim runs"
  dead counter (always showed 10, the truncated run_history list length) via new
  count_run_history_total(). 9 new tests, 14,470 fast suite passed, epistemic PASS. Remaining
  PROJECT_TAB_OVERHAUL.md scope (R-D light-theme/visual polish, Company/Overview dedup, per-tab
  direction items 3-7) folds into the WEBSITE_AS_SHOWCASE.md Part 0 design wave below.

## COMPLETED (cont. 6)
- WEBSITE_AS_SHOWCASE.md Part 0: CLOSED (Phase RE, 2026-07-06). The shadow-mirror light-theme
  rewrite of tools/generate_shadow_html.py (flagged as remaining work at the end of Phase RC)
  had already been written by an interrupted prior session and its output already regenerated
  and committed by a live sim run -- but the generator source itself was never committed, a
  silent output-ahead-of-source gap. Verified complete (no dark-palette colors remain) and
  correct (new guard test `test_shadow_page_uses_v4_light_design_system` passes), then
  committed. Confirmed live in both site/shadow/ and docs/shadow/ committed HTML, all 4 pages.
  Also recovered tools/generate_customer_consumption.py (CUSTOMER_360_REDESIGN.md item 1 data
  layer: real per-fuel monthly/daily/load-shape kWh into site/data/customers/{cid}.json --
  frontend rendering still open). 1 new test, 15,739 collected, fast suite 14,477, epistemic
  PASS.

## Backlog
- **Supervisor self-refill CLOSED, then SUPERSEDED (2026-07-10, SELF_DIRECTION_AND_
  PARALLELISM.md Problem 1, PROJECT_OVERVIEW.md Section 4 entry)**: background/supervisor.py
  originally granted a turn from an unblocked PRIORITIES.md backlog line (matching a
  since-retired trigger phrase, not BLOCKED/REVIEW GATE) when the agenda was empty and nothing
  was staged, instead of going idle. That mechanism is now the FALLBACK ONLY --
  _maturity_map_draw() (dial-weighted, docs/design/maturity_map.yaml) is the primary self-refill
  source as of the same day's R3 redesign; see supervisor.py's own module docstring. This bullet
  is deliberately reworded (2026-07-10, nineteenth dial-weighted draw self-audit) to stop
  containing the old fallback's own literal trigger substring unguarded -- the exact same
  self-referential false-positive class already fixed once before in this file, found again by
  directly testing find_work() when the maturity map returned zero live candidates. Problem 2 of
  the original doc (recalibrate one-way doors) deliberately NOT actioned -- Tier 1 safety-control
  change, needs the director's own in-console confirmation, flagged via NTFY. Problem 3
  (parallel-lanes proposal) still registered below, not yet drafted.
- **REVIEW GATE CLOSED (Tier 1) -- hedge-decision volatility lookback uses future data**:
  docs/review_gates/done/HEDGE_VOLATILITY_LOOKBACK_FORESIGHT_BUG.md (2026-07-10, from a real
  director page comment on /supplier/ Trading & Market). Director authorized the fix in-console,
  reviewed the re-derivation, then closed the gate with "publish corrected figures now, drop the
  old naked-hedging claim." Sim-runner hold removed; the "Regime-Change Blindness" discovery card
  and the hedge-fraction chart caption both rewritten to honestly reflect the re-derivation
  (population hedge cover stays 0.80-0.90 throughout, the old naked-hedging story does not hold in
  the current build). Next full sim-runner cycle publishes the corrected canonical figures.
- **Segmented financials -- PARTIALLY CLOSED (2026-07-10, director page comments, /supplier/
  Performance tab, twice in the same session -- P-2 director-repeat)**: revenue-by-segment +
  %-net-margin-by-segment shipped -- `saas/reporting/annual_report.py`'s `segment_split` now
  carries `revenue_gbp`, threaded into `tools/generate_dashboard_data.py::extract_financial()`
  (`net_margin_pct` per segment, `segments` list), new table + line chart on the Performance >
  Financial tab (`site/supplier/index.html::renderFinancial()`). Cash flow per segment and ROCE
  (incl. collateral) per segment deliberately NOT built -- neither concept exists anywhere in
  the codebase yet (`ROCE`/`capital_employed`/`cash_flow` all zero hits on grep); building them
  now would mean fabricating an undefined "capital employed" denominator rather than surfacing
  real computed data, unlike the revenue/%-margin piece which was a straightforward 2-line
  re-aggregation of an already-computed field. NEEDS A DIRECTOR DEFINITION DECISION, not
  mechanically self-refillable (same class the supervisor's self-refill heuristic is meant to
  exclude, per its own docstring: a director-decision-pending item, not real self-startable
  work) -- what "capital employed" and "cash flow" (vs. accrual net margin) should mean at
  segment level for this business, before any chart gets built on top of it.
- **Trading & Market tab redesign (director page comment, 2026-07-10, /supplier/)**: monthly
  buying/position-seeking activity, seasonal % cover over time by segment/product type, VaR --
  BLOCKED on the review gate above (fixing the volatility-lookback bug first, so this isn't built
  against known-wrong numbers). A research fork found: no per-decision/monthly hedge-event log
  exists yet (would need a new one in run_phase2b.py); VaR is already computed internally in
  company/trading/hedge_decision.py (VAR_Z_95/VAR_REVENUE_LIMIT) but never surfaced -- cheap to
  expose once the lookback bug is fixed.
- **Operations tab -- full value chain (director page comment, 2026-07-10, /supplier/
  Operations)**: "very narrow compared to the full operational reporting and scope of processes
  ... across resi, sme & I&C... the full value chain. Might need sub levels." NOT YET SCOPED --
  needs a proper investigation of what real energy-retailer operational reporting actually
  covers (acquisition, onboarding, billing ops, contact centre, arrears/collections, meter
  operations, complaints, regulatory returns) vs what's currently shown, before sizing a build.
- **Project tab roadmap -- epoch storytelling CLOSED (2026-07-10, director page comment, /project/)**:
  "I don't like the roadmap. It's very static. Where are my epochs. Tell the true story of all
  the cool work we have have planned." The static "Roadmap" checklist on the Overview tab
  (`site/project/index.html`) is now "The Epochs" -- three cards: Epoch 1 (Built, the existing
  checklist preserved as history), Epoch 2 (Closing the Wall, grounded in `docs/design/
  EPOCH2_EVIDENCE.md`'s director-confirmed headline finding -- the portal reads customer
  physical-property truth directly instead of through a discovery interface, and population is a
  fixed cast with no per-run draw lever), Epoch 3 (The Company That Can Die, the five mission
  clauses from `docs/staging/done/EPOCH3_DIRECTION.md` -- mortality/longevity tournament, brand as
  behavioural physics, regulated experimentation, anchored noise, temporal realism -- explicitly
  labelled "director-decided direction, re-rank input, not yet queued" per that doc's own framing).
  Deliberately did NOT touch the existing "Regime-Change Blindness" discovery card on the same
  page -- that claim is directly implicated by the open hedge-decision review gate above and stays
  untouched pending director review, per the explicit hold. Qwen phase-close audit sampled the new
  section: 3 flags, all false positives on manual check (a category mismatch -- the "grumpy real-
  supplier" auditor persona flags forward-looking vision language as implausible when it is
  director's own verbatim wording, correctly labelled as future vision not current operations).
  Presentation-only (site/ only), epistemic PASS.
- **SIM tab -- more model-complexity flavour CLOSED (2026-07-10, director page comment,
  /sim/)**: "Many being 70% satisfied looks suspicious. And none in fuel poverty. No info on
  smart meters. Duel fuel. House type. Business type consumption etc." Smart-meter status,
  dual-fuel indicator, and house/business type now surface on the SIM Customer Sample table
  (`tools/generate_customer_sample.py` reads real per-customer_id fields from `saas/customers.py`
  -- `home_type` doubles as the business-premises-type signal for I&C/SME accounts, segment-aware
  label on the render side; `dual_fuel` derived by checking whether a household's
  `base_account_id` has both an electricity and gas leg). 5 new tests, verified against real data
  via a Node harness executing the actual table-render logic. The "70% satisfaction looks
  suspicious" half CONFIRMED a real finding (67%/28% of all satisfaction datapoints sat at exactly
  one of two shared values, zero per-customer heterogeneity) -- discovery-agent found a real Ofgem/
  Citizens Advice anchor (Wave 20, May 2025, n=3,854): real GB energy-consumer satisfaction is a
  continuous distribution at every level, never a shared point value. Fixed in `simulation/
  sim_satisfaction.py::sim_satisfaction_score()`: a real payment-method gap (DD 82% vs Standard
  Credit 76%, closing a previously-flagged unwired archetype) plus an honestly-flagged per-customer
  heterogeneity term (+/-0.04, direction anchored, exact magnitude a calibration choice -- no
  source publishes individual-level variance within one cohort). 7 new tests incl. a direct
  regression test for the clustering; full `tests/simulation/` suite (1343 tests) + the real-
  pipeline `test_run_phase2b.py`/`test_run_phase4c_on_phase2b.py` regression (39 tests, ~12min real
  run) both pass. Epistemic PASS.
- **Cumulative tests EXECUTED metric CLOSED (2026-07-10, director page comment, /project/)**:
  "Don't we want cumulative tests run, not the growth in the standard test set." Forward-only
  instrumentation, not a fabricated historical backfill: `tests/conftest.py::pytest_sessionfinish`
  now appends one line per real pytest session (full suite or a partial/targeted run -- every
  invocation counts, matching the metric's intent of showing continuous verification activity) to
  `docs/observability/test_execution_log.jsonl` via `tools/test_execution_metric.py`. New
  "Test executions" KPI card on the Project tab (`site/project/index.html::renderKpis()`), honestly
  labelled with a tooltip stating the "since" date rather than implying a full-project total. 10
  new tests. Same phase: found and fixed a THIRD recurrence of the documentation-convention-drift
  class (R10) -- `tools/generate_dashboard_data.py::_derive_build_from_claude_md()` also silently
  broke once recent CLAUDE.md Current-state entries lost their literal "Phase XY" tag, AND its
  test-count extraction landed on the same "221 tests passing" partial figure the chart-regression
  fix already found once. Fixed by decoupling test_count extraction from phase-code presence and
  preferring "collected" phrasing (MAX across matches) over ambiguous "passing" phrasing. Added a
  durable phase-close checklist line (CLAUDE.md step 5) requiring every Current-state entry to
  state the true full-suite count as "N tests collected." 6 new tests, epistemic PASS.
- **TIME_REPLAY (Epoch-2 dividend, registered 2026-07-09 per DIRECTOR_COMMENTS_BOX.md's
  forward registration -- registration only, no design/build done)**: director wants a
  run-button/slider on most site pages to visualise the passage of time -- events, actions,
  reactions replayed. Canonical placement: this is a VIEW OVER THE EVENT LOG, a named
  dividend of the Epoch-2 event-primitive/bitemporal architecture (see
  docs/design/EPOCH2_EVIDENCE.md Q2 -- foundational rework, no event ledger exists yet) --
  enters the epoch-2 programme statement when that is framed. An optional cheap precursor
  (animating existing period snapshots, no real event ledger needed) may be proposed for the
  director to rank separately.
- **Bill calculation breakdown + real PDF, PARTIALLY CLOSED (2026-07-10, director page comment
  + direct NTFY decision, /customers/)**: "Days x standing charges" now shown --
  `saas/bill_generator.py::generate_bill()` exposes `days_in_period`/`standing_charge_gbp_per_day`
  (both already computed locally to derive the total, just never returned), threaded through
  `tools/generate_billing_ledger.py` AND `tools/generate_invoice_data.py` (the actual customer-
  portal-facing mapping layer -- found and fixed a second pass-through gap here, the ledger fix
  alone was not sufficient) to the persisted invoice, rendered as "N days x £X/day" on the Bill
  Equation, gracefully falling back to the old plain label for bills computed before this fix.
  Director picked "a real downloadable PDF" (NTFY "2. A") over an on-page mockup: real per-bill
  PDF generation shipped via client-side jsPDF (CDN, matching this site's existing Chart.js
  convention) -- a "Download PDF" button on each expanded bill renders account, invoice, billing
  period, the full charge breakdown incl. the new days x rate line, meter/MPAN/MPRN, and total,
  using the exact same invoice object already on the page (numbers can never drift from what's
  shown on-screen). Verified end-to-end with real data through the full real pipeline
  (bill_generator -> ledger invoice -> frontend invoice mapping -> PDF render logic, via a Node
  harness stubbing jsPDF) -- no browser available in this environment to see the literal PDF file,
  stated honestly as the verification ceiling. 12 new tests (5 bill-generator/ledger, 7 invoice-
  mapping + regression). REMAINING, genuinely deferred: "prices x days at that price" / full
  TOU-readiness (multiple rate bands per day) -- the tariff engine has no multi-rate-per-day
  concept at all yet, a real architecture gap (the invoice's existing `registers` list structure
  already anticipates this without a schema change, per BILL_CORRECTNESS_ADDENDUM.md Defect 3, but
  the tariff-pricing/settlement side does not yet produce more than one register).
- **Consumption page with fuel toggle -- ALREADY EXISTS, CLOSED (2026-07-10, director NTFY
  steer)**: "I don't mind kWh for gas. You just need to be careful not to add to electricity as
  this makes no sense. Maybe a page on the website with a toggle." Checked live: no bug existed
  (`combinedTotals()` only ever sums £, never kWh) -- and on closer check, the requested SURFACE
  already exists too: `site/customers/index.html`'s Consumption tab (`renderConsumptionTab()`,
  dual-fuel accounts only) has a real Electricity/Gas toggle (`setConsFuel()`), rendering usage
  for the selected fuel only via `renderUsage()` -- kWh is never combined across fuels anywhere
  in this view. No new page built; would have been redundant. Told Rich directly rather than
  building something that already exists.
- SAAS_COVERAGE_MAP.md item 4 remainder: credit bureau feed into collections strategy
  (currently only feeds acquisition credit checks)
- FEEDBACK_AND_REPUTATION.md, NUDGE_PHYSICS.md: explicitly queued behind the current design
  wave per their own staged text -- do not jump ahead of PRIORITY 1 above
- Further correlated-generator scenarios, extended stress suites, shadow-live index page
- C2/C3/C4 resi EAC benchmarking vs Ofgem TDCV by dwelling type
- Smart meter customers on real HH shapes for segment model
- EPC-calibrated consumption distributions (requires GOV.UK data access)
- BSUoS year-indexed actuals

## 2026-07-10 director page comments -- CLOSED (Home chart, /customers/ nav + HH-consent claim, C9 data-sense check)
- **Home page chart still looked flat, 3rd occurrence -- CLOSED**: "I thought you changed these
  graphs. They look like the old flat ones still." NOT a data bug this time (data was already
  correct and live) -- a real visual-scaling issue: an early one-time bulk jump (1,290 -> 15,314
  tests in the first ~6 days) dominates the linear y-axis for the whole history, so a full week of
  genuinely real recent progress (15,314 -> 16,471) occupied only ~7% of the visible range and
  read as flat. Fixed with a "Recent (7d)" / "All time" toggle on the Home page Learning Curve
  (`site/index.html::renderLearningCurve()`), defaulting to Recent so real day-to-day movement is
  visible; neither series altered, only the default window. Verified via a Node harness against
  real phases.json data.
- **Home page charts "go up fast then look flat", 4th occurrence -- CLOSED, director gave concrete
  guidance**: "I want to pick metrics, such as cumulative ones that show the growth we creating."
  Root cause this time is structural, not fixable by rewindowing alone: test-SUITE SIZE
  mathematically must look like deceleration once the total is large, since each new test is a
  shrinking relative share -- no amount of chart-scaling fixes that. Added a genuinely different
  metric with the property the director asked for: cumulative git commits by day
  (`tools/generate_phases_json.py::cumulative_commits_by_day()`), a running total that has stayed
  high (60-400+/day) across the WHOLE 31-day project history with no flat stretches, because it
  counts ongoing work rather than a saturating total -- 9 -> 3,104 commits, real, monotonic,
  verified via a Node harness. New "Cumulative Work -- The Growth We're Creating" chart section on
  the Home page, alongside (not replacing) the existing Learning Curve. 5 new tests, epistemic
  PASS.
- **`/customers/` nav: keep tab across customer-cycling + move arrows left -- CLOSED**: "Please
  keep the same tab when we scroll between customers. Can you move the scroll to left hand side?"
  `cycleCustomer()` was resetting `ACTIVE_TAB="overview"` on every navigation -- removed (fuel/
  bill-view sub-state still resets, since that's genuinely per-household). Prev/next arrows moved
  from the right (grouped with Sign out) to the left, ahead of the account id.
- **HH data-sharing "opt-in" claim -- CORRECTED, director was right**: "Please make sure opt in is
  the default option for most customers as we see. They can opt out but few do." Dispatched
  discovery-agent research rather than just flipping the code on assertion: confirmed the
  director's framing for the mechanism that actually matters (a DCC-enrolled smart meter sends
  reads to its OWN supplier for BILLING by default, ~90% of installed smart meters, DESNZ Q4
  2024 -- NOT opt-in-gated as the old docstring claimed). A separate, genuinely narrower
  settlement-purpose HH-consent regime does exist (Ofgem, 2019) but its real uptake is unpublished
  and Ofgem/Elexon's MHHS programme is retiring it entirely by 2027. Corrected both
  `tools/generate_customer_consumption.py`'s docstring and the matching user-facing note on
  `site/customers/index.html` -- full findings in `docs/market_research/ASSUMPTIONS.md`.
- **"Is C9 really residential household?" -- answered, found and fixed a real label bug**: yes,
  genuinely modelled as residential (segment=resi, 2-bed Glasgow tenement flat) -- but it's an
  all-electric household (no gas service, EPC D) with correspondingly high consumption (~12,500
  kWh/year), which is why its numbers look larger than a gas-heated resi customer; a plausible
  real-world archetype, not a bug. Investigating this DID surface a real bug from earlier today's
  SIM tab work: the House/Business Type label map (`site/sim/index.html`) was missing
  `tenement_flat` entirely and had two WRONG values that don't exist in the real data
  (`rural_cottage`/`detached_house` instead of the real `rural_detached`) -- fixed to match the
  actual `home_type` values in `saas/customers.py`.

## R1/R11 class fix -- CLOSED (2026-07-10, director-caught live incident + advisor-staged docs)
Full detail in CLAUDE.md's Current-state entry + `docs/review_gates/done/HEDGE_VOLATILITY_LOOKBACK_FORESIGHT_BUG.md`.
Core DoD items from `CLAIM_EQUALS_PIXEL.md`/`END_TO_END_VERIFICATION.md` closed: today's specific
incident fixed + pixel-verified live; the class fixed (`FORCE_REPUBLISH_FLAG` mechanism, hold
release can never again be a no-op); R11 added to CLAUDE.md. NOT built in this pass, registered as
separate future scope: the daily automated Expert Hour walk (a new background daemon walking the
live site as a fresh visitor, reconciling claims vs pixels); the sanity daemon's broader freshness-
invariant extension (checking every artefact's stamp against its expected trigger, not just this
one incident's mechanism); a full audit+retrofit of every OTHER hold/gate/flag in the codebase for
the same orphan-transition risk (only sim-runner's hold was fixed, others -- e.g. the exception
queue release, agenda refill -- were not audited this pass).

## DOMAIN_ARTEFACT_LIBRARY.md -- registered, NOT built (2026-07-10, advisor-staged, background-lane discovery)
A large external-codification research programme (UK market specs, regulatory process
codifications, open-source domain models like PowerTAC/Kill Bill/ERPNext, process taxonomies like
APQC PCF/eTOM) to mine rather than reinvent, feeding the invariant library, ASSUMPTIONS.md lineage,
and Epoch 2/3/4 framing. Explicitly background-lane, must not displace DOMAIN_SENSE_AND_COMPLIANCE
or BILL_CORRECTNESS_ADDENDUM. Genuinely multi-session scope -- registered for a dedicated future
phase rather than started alongside everything else in flight today.
