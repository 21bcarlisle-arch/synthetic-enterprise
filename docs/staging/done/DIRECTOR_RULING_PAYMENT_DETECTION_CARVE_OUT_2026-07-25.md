# [DIRECTOR-RULING] — Payment-failure detection: irreducibility REJECTED; narrow sensing carve-out AUTHORIZED; dunning/debt/provisioning RESERVED to a director session (2026-07-25)

**Type:** [DIRECTOR-RULING] via advisor bridge. Answers the wall on `PLANNER_MINTED_payment_truth_detection_gap` (W2_11).

## 1. The irreducibility claim is REJECTED — it is a LATENCY, not a blind spot

The DISCOVER/FRAME work is excellent and its conclusion is wrong in one load-bearing way. It measured that non-DD failures emit no `WallResponse` (no ARUDD/Bacs event exists for a payment nobody pushed) and concluded the company therefore *cannot* observe them.

**A real supplier observes them by expected-collection reconciliation:** it knows what it billed and when it fell due, it knows what cash arrived, and **the absence of expected cash by due date is itself the observable.** No rail message is required to notice that an expected payment did not turn up. The mint already names this mechanism in its own propose-half; it must not be registered as an irreducible gap.

**What IS honest, and what gets registered (R10):** the **detection latency** — DD failures are observable within rail-return time; non-DD failures are observable at due-date + grace. Register the latency **with its measured distribution**, not a permanent gap. The lag is real-world faithful and valuable in its own right: arrears build during it, and a company acting on stale collection beliefs is exactly the kind of realistic failure the SIM should produce. Do not compress the lag to zero to make the number look better (R12).

## 2. Carve-out AUTHORIZED — sensing only

The Billing+CRM front **stays roadmap-gated**. This ruling authorizes one narrow build:

**IN SCOPE:** the expected-collection reconciliation detector — expected vs received cash by due date and grace, producing observed payment-failure events for all channels, through-the-wall observables only (billing records and the company's own cash/bank feed; never sim internals). Re-measure and update the `live_payment_detection_gap` ledger row.

**EXPLICITLY OUT OF SCOPE — build none of it:** dunning sequences or any collections action, vulnerability/PSR flagging logic, SoLR risk machinery, arrears-driven pricing or service changes, bad-debt provisioning policy, write-off rules. **Detection is a sensing organ; it does not license an acting organ.** If the detector's output makes an action look obvious, that is precisely the thing reserved below.

**R15 both ways:** the detector must raise `believed_failures` toward `true_failures` on cell A1_G2 (fires on the fix), and a mutation must prove it can still miss — it may never fail open to "all detected", which would be a wider hidden gap wearing a better number. The honesty target is a smaller **measured** gap, never a company that believes it catches everything.

## 3. RESERVED — the dunning, debt and provisioning design session

The director is convening a dedicated design session on **dunning, debt discovery and provisioning**, and has flagged that **provisioning method is materially P&L-relevant** (the choice of expected-credit-loss vs incurred-loss recognition, aging-bucket structure, write-off timing and their interaction with the three clocks — billed / settled / banked). 

**Do not build, propose, or frame ahead of that session.** Register the following as awaiting it, and nothing more: collections physics (cannot-pay vs will-not-pay), dunning ladders and their real regulatory constraints, debt discovery at change-of-tenancy (already a registered DISCOVER atom — it feeds this session, do not pre-empt it), bad-debt provisioning method and its P&L consequences, and the arrears-to-write-off pipeline. The detection organ built under §2 is the **substrate** that session will design on top of; building the actions first would foreclose its choices.

**Sequencing note:** SOURCE 2 (grid-attribution approximation) was already built and closed on the 2026-07-24 night tick; this ruling concerns SOURCE 1 only.

**Risk & proportionality:** a sensing organ over existing billing and cash data, with an explicit no-action wall and a fail-open mutation test; the collections/CRM front remains closed. Tag: **proceed, sensing only.**

— Advisor bridge, carrying the director's ruling, 2026-07-25.
