## E2_revenue_reconciliation L3 EARNED (live-verified) + W1 Expert Hour PASS + W2_7 DISCOVER
Last updated: 2026-07-12T21:28:19Z

**Status:** self-refill cycle (idle-tier DISCOVER/FRAME + dial-weighted BUILD), all changes pushed
and live-verified where R11 applies. Epistemic PASS throughout.

**E2_revenue_reconciliation (level 2->3, TARGET REACHED, live-verified):** the front page
(poesys.net) already discloses which clock a net-margin figure reads (settlement vs bill-derived
ledger, R14 basis labelling). A DISCOVER pass found three other authored surfaces --
site/supplier, site/project, site/customers -- rendered a net-margin figure with zero such
disclosure. Built and shipped: supplier + project reuse the same real `portfolio.basis` data
object the front page uses (no new fetch); customers (a separate data file with no basis object)
gets an honest static clock-disclosure sentence instead, flagged as lower-rigor than the other two.
Verified against the LIVE deployed site (not just the code): confirmed the Cloudflare Pages deploy
completed, then curl-fetched all three live pages (cache-busted) and found the new
code/text genuinely present in the deployed source, plus re-confirmed live dashboard.json still
carries the real basis objects the code reads. All four surfaces with a net-margin figure now
carry a clock disclosure -- this atom's own charter bar is met.

**W1_reveal_over_time Expert Hour: PASS.** Fresh-context review (phase-close-evaluator, no memory
of the build) independently verified the L2 claim against the real diff/code/tests: dual-time-axis
is real not a stub, both hedge-decision call sites are genuinely migrated with the old wrapper
retired, both exit-test halves pass and assert what's claimed, the M4 deferral is a real recorded
director decision. One low-severity finding recorded (not a blocker): same-day-price visibility at
the boundary -- `transaction_time == valid_time` means a hedge term starting on date D sees D's own
daily-mean price, diverging slightly from the sibling `calculate_sigma_recent()`'s strictly-before
window. Negligible magnitude, now documented as a genuine side effect for the next real touch of
that path.

**W2_7_willingness_classification DISCOVER (epoch 3, BUILD still gated):** found the can't-pay/
won't-pay framing is a live, contested UK political issue right now (Ofgem's interim CEO publicly
criticised for a "reductive" framing; End Fuel Poverty Coalition: "it's a can't-pay crisis, not a
won't-pay one") -- real evidence against anchoring this atom's eventual build to a naive/arbitrary
willingness split. Quantified anchor found with an honest caveat: StepChange H1 2024 (41% of
energy-bill clients in arrears, 47% of that group with a negative budget) anchors a self-selected
distressed sub-population, not the whole customer book. No precise won't-pay percentage found --
named as an open gap for the eventual build or a director-set curriculum assumption (R13).

**Prior:** BILL_CORRECTNESS_ADDENDUM closed in full (Defects 1-4) -- see
docs/claude/phase-history.md for the full write-up. THE SUPERVISOR architecture rebuild -- see
docs/retrospectives/2026-07-09-doorbell-failure-4-supervisor.md.

**Latest simulation results (2016–2025)** — auto-processed (498s / 8 min):
- Net margin: £1,524,057.56 | Gross: £6,477,859.06 | Capital: £51,377
- Treasury: £2,466,636 → £3,902,095 | 38 committee interventions | 1588 bills issued
- Enterprise value: £7,730,031.11 | Net after CTS: £6,407,919
- Retention: 12 offers, 12/12 retained | 5 no-offer churns | 5 total churned accounts