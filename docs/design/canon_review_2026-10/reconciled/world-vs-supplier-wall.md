# world-vs-supplier-wall: consolidated

Inputs: 28 extracts, the October console log (R-L-<n>) and the machine's 12 Oct audit (section 7). Page marks come from grep of CLAUDE.md, DIRECTOR_CANON.md, MOAP (THE_MODEL_ON_A_PAGE.md) and HSL (HUMAN_SIMULATION_LAYER.md).

## 1. Standing principles (what still governs)

**1. The wall and its test.** The company "may only know what a real UK supplier could know": "could a real UK energy supplier have known this, at that moment? Without that wall, a simulated company learns to cheat, and everything it teaches you is worthless." "Ground truth never crosses; observables do"; `company/interfaces/sim_interface.py` is the seam, the only route. Not relaxed for Epoch 2 or for book growth ("non-negotiable"); a run "must never look ahead".
sources: R-S-127 (2026-06, day unknown), R-E-10, R-S-69 (2026-07-12), R-B-16 (2026-07-19), R-A-6 (2026-07-28), R-C2-80 (2026-08-11), R-S-33 (2026-08-28), R-L-53 §4 (2026-10-09) | on standing pages: CLAUDE.md yes; DIRECTOR_CANON.md yes. CLAUDE.md names only `company/` and `saas/` lines, so the simulation-side hedge crossing was not covered (R-S-33 note, audit section 7); "at that moment" is only in MOAP's Point-in-Time Blindfold.

**2. The gap is the product.** "The SIM holds the hidden why. The company sees only what a real supplier could see. Value comes from inferring the gap, never from access." The supplier "must not be designed from knowledge of what's behind the curtain". It sees consequences, not events, and infers the cause; the cost of imperfect information is "a standing metric".
sources: R-S-127 (2026-06), R-S-139 (undated), R-B-16 (2026-07-19), R-D-41 (2026-09-07), R-L-62 (2026-10-11) | on standing pages: CLAUDE.md partly; DIRECTOR_CANON.md partly (HSL and MOAP carry the inference duty; no page publishes the metric).

**3. Hidden state is drawn as state and found by behaviour.** "Every household is drawn as prior plus residual, and the epistemic wall falls between the two": layer one is public data, "guessable by the company from an address"; layer two is "private, hard to observe", found "from the meter shape, the payment record, contacts, and by asking". Cohort labels, green stance, price sensitivity and channel preference stay unreadable across the seam. A trait with no observable channel gets one or is marked hidden. Vulnerability is "a hidden household state rather than by rule"; complaints are "a floor on dissatisfaction, not a measure of it", so "model the silent unhappy"; hidden finances, job loss and pay-or-heat sit in the world.
sources: R-A-27 (2026-07-27), R-F-45 (2026-08-27), R-D-66 (2026-09-05), R-L-39 (2026-10-05), R-L-48 §4, R-L-49 §4 (2026-10-08), R-L-59 §5, R-L-61 (2026-10-11) | on standing pages: CLAUDE.md no; DIRECTOR_CANON.md no (MOAP carries the hidden-traits statement; only the generic wall is yes).

**4. The wall is two-way, and latency is physics.** "Everything else is an interface flow in one of two directions." "A bill is outbound, never an observable — the inbound observable is the payment or complaint that answers a bill"; settlement arrives late. Non-DD payment failure is a detection latency, not a blind spot, seen "by expected-collection reconciliation"; "Do not compress the lag to zero to make the number look better."
sources: R-B-62, R-S-107 (2026-07-23), R-A-60 (2026-07-25) | on standing pages: CLAUDE.md partly (one-way only); DIRECTOR_CANON.md no (MOAP states it in full).

**5. Beliefs and forecasts belong to the company.** "recency, sentiment, adaptive expectations are properties of the COMPANY's belief formation, not of the true process — model them company-side and score them." "No downstream consumer ever decides on outturn"; forecast error is "the natural epistemic wall on the future". Forecasts are "genuinely public (company-knowable)", as is NESO's carbon series, "what a real supplier would use for any customer offer" (R-L-36). The company is to hold one consumption forecast, "the best against held-back actuals" (R-A-104's note counts six; R-L-64 says four).
sources: R-A-100 (2026-07-22), R-A-104 (2026-07-23), R-L-36 (2026-10-04), R-L-59 §2 (2026-10-11), R-L-64 (2026-10-12) | on standing pages: CLAUDE.md partly; DIRECTOR_CANON.md no.

**6. The seam is the only route; the company has no route to the real world.** "The supplier doesn't seek approval — it's refused by construction"; `company/` and `saas/` "may not open a socket, ever, directly or transitively". Three lanes: company refused; "the SIM using real-world sources isn't a loophole, it's the job"; harness-fetched bytes "may become documentation, design records and Knowledge, never a runtime input the company reads". "The wall is the go-live seam: switching from simulated endpoint to real endpoint is the launch, not a rewrite." No real money: "Simulation is different to real money of mine."
sources: R-C2-44 (2026-08-17), R-C1-22 (2026-08-18), R-S-34 (2026-08-28), R-L-08 (2026-09-27) | on standing pages: CLAUDE.md partly (lane one and real money yes; lanes two and three and the go-live seam no); DIRECTOR_CANON.md no (real money yes; "go-live" appears only for the director seat, line 52).

**7. The four principles of 11 October.** (1) "World first": build "the household side before the supplier side ... from research, with no reference to any supplier policy. Where evidence is missing, carry a labelled range, not a number." (2) "Freeze, then solve": fix the world "with its predictions filed, before testing any supplier solution against it. Don't change the world after seeing supplier results unless new evidence requires it, and say so". (3) "Separate the work": world behaviour and supplier policy "in separate lanes"; the supplier "reads only through the seam"; strategies "graded on fresh seeds and across the world's uncertainty ranges". (4) "Truth stays an instrument": the decision probe and holdout truth "are for grading only, never inputs to a supplier decision." R-L-64 sets the order: audit, household payment-behaviour world, then supplier engine.
sources: R-D-56 (2026-09-05), R-L-50 §3 (2026-10-08), R-L-62 (2026-10-11), R-L-64 (2026-10-12) | on standing pages: CLAUDE.md partly (only half of 2: "decided blind to company results", line 204); DIRECTOR_CANON.md no.

**8. Unpublished behaviour is a labelled range, checked and never fed.** "Where the truth isn't published, make it an assumption toggle: a parameter with a plausible range, and test whether the answer changes across it. If it doesn't change any decision, the question doesn't matter." Customer-chosen levers with no published take-up run "only as sensitivities across a take-up range, never as findings." Published rates are "a reality check on the world rather than an input"; the world's own price response decides who is saved, and the world is handed the discounted rate, not a flat constant (R-L-52 §1). Knowledge before build, unknowns labelled GAP.
sources: R-L-39 (2026-10-05), R-L-49 §1 (2026-10-08; R-L-58 does not carry this text), R-L-52 §1, R-L-55 (2026-10-09), R-L-59 §5, R-L-60 (2026-10-11), R-L-64 (2026-10-12) | on standing pages: CLAUDE.md partly (knowledge-first, lines 56-65); DIRECTOR_CANON.md no.

**9. Change the book, not the world.** "Change the book, not the world, and not the measurement." I&C stays in the world; "the segment choice belongs at the company's acquisition decision, not in the world's draw", because a dial that alters which households exist "invalidates every comparison across it".
sources: R-F-30 (2026-08-26), R-F-48 (2026-08-30) | on standing pages: CLAUDE.md partly (baseline/curriculum split, line 204; not these words); DIRECTOR_CANON.md no (grep; the extracts said partly).

**10. Independent anchors.** Generation and validation anchors come from disjoint sources ("standing anti-marking-own-homework rule"); the company never validates against SIM ground truth; prior art is mined, and each domain's "NOT credible" battery joins the fidelity oracle.
sources: R-B-36 (2026-07-20), R-A-100 (2026-07-22), R-A-104 (2026-07-23) | on standing pages: CLAUDE.md partly; DIRECTOR_CANON.md no.

**11. The uncommon are over-represented.** Customers who do not fit the average "are over-represented rather than rounded away. A million customers cannot be simulated and need not be."
sources: R-D-41 (2026-09-07) | on standing pages: CLAUDE.md no; DIRECTOR_CANON.md no.

**12. The site shows both sides of the wall, structurally, and fails closed.** "The side-declaration must be structural, not prose. A control that cannot fail is not a control." Explore keeps "one persistent element showing world-truth against company-belief"; "'we cannot tell' is a result, it belongs on the page"; "Absence stated plainly is credibility, not weakness."
sources: R-C2-20 (2026-08-12), R-C2-44, R-C2-45 (2026-08-17), R-C2-38 (2026-08-31) | on standing pages: CLAUDE.md partly (fail-closed yes; exhibit no); DIRECTOR_CANON.md no.

Coverage: no extract, October entry or standing page carries a no-personal-microdata ruling.

## 2. Supersession chains (what replaced what)

- Wall direction: canon-doc wall sentence listing "bills" among what the company sees (no id) -> R-B-62 (2026-07-23) bills outbound, settlement a late inbound gate -> R-S-107 (2026-07-23, GOVERNS NOW) fullest statement; CLAUDE.md still has the one-way half.
- Population: R-A-27 (2026-07-27) labels and sensitivities unreadable -> R-D-66 (2026-09-05, GOVERNS NOW) public prior guessable, private residual hidden. R-L-48 §5 (2026-10-08) reopens it, unruled (section 3).
- Segment choice: R-F-30 (2026-08-26) -> R-F-48 (2026-08-30, GOVERNS NOW) a dial that altered which households existed is repaired, not accepted.
- Exhibit: R-C2-20 (2026-08-12) household page as wall exhibit -> R-C2-45 (2026-08-17, GOVERNS NOW) the same exhibit as Explore's persistent element; completion not seen.
- Reach of the wall: R-S-33 (2026-08-28) asked of `company/` and `saas/` lines -> R-L-62 §3 (2026-10-11, GOVERNS NOW) supplier policy and world behaviour in separate lanes, the supplier reads only through the seam, wherever the code sits.
- Collections placement: R-D-56 (2026-09-05) -> R-L-62 (2026-10-11, GOVERNS NOW) re-issued after the failure recurred.
- Payment engine order: R-L-59 §5 (2026-10-11 04:20) design the supplier levers and bring them -> R-L-61 (07:41) one engine on a forward cash forecast -> R-L-62 (10:30) "Before the payment and debt engine goes further", world first -> R-L-64 (2026-10-12, GOVERNS NOW) audit, household world, then supplier engine; supplier-controlled levers first, customer-chosen ones later as sensitivities.
- Truth as instrument: R-B-36 (2026-07-20) company never validates against SIM truth -> R-L-26 (2026-10-03) per-decision probe "the right instrument" -> R-L-62 §4 (2026-10-11, GOVERNS NOW) probe and holdout truth for grading only.
- Practitioner figures: R-L-48 §3 (2026-10-08 06:46) director's save-rate experience as a toggle -> R-L-49 §1 (08:52, GOVERNS NOW) "I'm not giving figures"; published switching-process data sets ranges, as a reality check; R-L-55 (2026-10-09) repeats it.
- Forecasts: R-A-104 (2026-07-23) -> R-L-59 §2 (2026-10-11) one or several? -> R-L-64 (2026-10-12, GOVERNS NOW) unify the four into one, after the engine's first result.

## 3. Unreconciled conflicts (needs the director)

**3.1 Should the world expose real correlations? (R-L-48 §5, 2026-10-08, ruling awaited.)** "My 27 Aug ruling made per-household price sensitivity nearly independent of anything a supplier can observe ... If the world hides correlations that are real, targeting is rigged to fail. Propose the change and I'll rule." Against it stand R-A-27 (2026-07-27), R-F-45 (2026-08-27) and R-D-66 (2026-09-05): the residual is private and found by behaviour. MOAP records price sensitivity at a 1.26x spread, "structurally unlearnable", with green stance and channel preference read by no response function. R-L-49 §2 (same day, later) already rules, for acquisition, "No past-switching carry-over term." No ruling seen. A ruling must decide how far responsiveness may correlate with signals the supplier holds (past switching, channel, fixed vs SVT, contact history) without making the trait readable, and whether the past-switching bar stands.

**3.2 No sockets ever, or the wall as go-live seam?** R-S-34 (2026-08-28) and R-C1-22 (2026-08-18): the company has no route to a real endpoint, and "a rule that must be relaxed at go-live is a rule that fails at the worst moment". R-C2-44 (2026-08-17): "switching from simulated endpoint to real endpoint is the launch, not a rewrite". The R-S-34 note finds no document saying how the wall is ever lowered. A ruling must decide where the real-endpoint adapter lives at go-live and what "refused by construction" then means.

**3.3 May the company learn from outside its own book? (R-S-159, open since 2026-10-09.)** The machine: "I will not let the company price offers on evidence from outside its own book, because that changes what a supplier this size is allowed to know. If you would rather it use published retention trials, say so." Pulling the other way: R-C1-22 (fetched bytes may become Knowledge), R-L-49 §1 and R-L-60 (design from published evidence), R-L-45 (2026-10-07: the coin-drawn decision set shows an offer's effect is learnable). Holding it back: R-L-62 §4, holdout truth is for grading only. A ruling must decide whether published trial results are design-time Knowledge a real supplier would have, and whether the company may run its own randomised holdout and read the result.

**3.4 Supplier quota or world first? (apparent.)** R-L-57 (2026-10-10): every stretch carries "at least two supplier items", world fidelity "only where it blocks a supplier result". R-L-62 and R-L-64 (2026-10-11, -12) put the household payment world before the supplier engine. A ruling must decide whether that world work counts as blocking, and what fills the quota meanwhile.

## 4. Lapsed (standing rulings that nothing seems to hold)

- R-C1-22 (2026-08-18): lanes two and three (SIM may ingest published sources; harness bytes never a company runtime input) dropped out of CLAUDE.md in the 2026-08-28 rewrite; grep confirms only lane one remains. The harness clause was the most checkable of the three.
- R-D-56 (2026-09-05): policy in world files recurred (DD review rule and cadence, world-side dunning; audit section 4); re-issued as R-L-62.
- R-A-104 and R-S-107 (2026-07-23): decisions on outturn: true settled kWh reached the hedge volume and the mover offer, and the trailing sum on estimate-billed months. Closed for that one input by `77cc6a9a9`; the shape that let it through is not (audit section 5).
- R-F-30 (2026-08-26): violated within four days (R-F-48).
- R-S-127 (2026-06): the standing belief-against-truth metric has no named surface.
- R-C2-45 (2026-08-17): Explore's wall element still "pending" on 08-20 and 08-25; completion not seen.
- R-C2-38 (2026-08-31): director-facing records on live pages (`site/data/delivery.json`) go false when a measurement lands; nobody owns correcting them.

## 5. Good ideas that dropped out of sight

- R-L-62: the four principles have no home on CLAUDE.md or DIRECTOR_CANON.md beyond a half-echo at CLAUDE.md line 204; they are what the 12 Oct audit's six queued remedies enforce.
- R-C2-44: "The wall is the go-live seam", the strongest architectural claim he named; in neither page.
- R-C1-22: the harness clause, fetched bytes become Knowledge "never a runtime input the company reads"; the most checkable lane, lost from CLAUDE.md.
- R-F-30, R-F-48: "Change the book, not the world, and not the measurement", the cleanest wall rule for segment choice.
- R-D-66: public prior guessable but not given, private residual found by behaviour, geography as the coherence key "not from an invented correlation matrix".
- R-D-41: "What must be simulated is every way a customer can differ from the average"; a candidate mission-block sentence.
- R-S-127: publish the cost of imperfect information, belief against truth, as a standing metric.
- R-L-39: complaints as "a floor on dissatisfaction"; model the silent unhappy.
- R-A-104: forecast error as the natural wall on the future, "no artificial blinding needed".
- R-A-60: non-DD failure is a detection latency with a measured distribution; "Do not compress the lag to zero".
- R-L-59 §5, R-L-49 §1: unpublished take-up is a sensitivity, never a finding; published rates check the world and are never fed to it.

## 6. One-offs now done (safe to retire from canon)

R-B-62 (MOAP amended); R-C2-38 (the repair only, the rule stands); R-L-62's closing check and R-L-64's first instruction (the audit, landed 2026-10-12).

## 7. The machine's 12 Oct audit against the four principles

Re-read at origin `2b005a8f6` on 2026-10-12; no code changed. No capability reads a truth probe or holdout truth at decision time, so principle 4 holds where asked directly. It broke one level down: the world loop (`run_phase2b.py`) computes the supplier's inputs and hands them in as plain values, which is how true settled kWh reached the hedge volume and the mover offer (closed for that input by `77cc6a9a9`; the shape remains). The reactive save, renewal cut and mover offer each break principles 2 and 3 (the mover offer also 1): world and supplier landed together, each graded on one seed. The payment world lagged most on principle 1; `f853cd2ff` is the first work under the principles. Supplier policy still sits in world files (DD review rule and cadence; world-side dunning). Queued, six seat continuations: a typed seam record for run-loop inputs (first); the best-deal gap as a published observable through the seam; world predictions filed at range ends; save, mover and renewal cut re-graded on fresh seeds across ranges; provision measured only on the frozen payment world; DD review and dunning moved to the supplier.
