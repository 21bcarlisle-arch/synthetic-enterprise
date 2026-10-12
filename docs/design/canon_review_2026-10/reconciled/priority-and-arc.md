# priority-and-arc: consolidated

Inputs: 72 theme extracts plus October words R-L-01..64. All dates 2026. Standing-page flags re-checked by grep on CLAUDE.md, DIRECTOR_CANON.md, THE_MODEL_ON_A_PAGE.md (MOAP) and OPERATING_MODEL.md.

## 1. Standing principles (what still governs)

**1. The order from here.** "1. Knowledge, now and wide" (debt and collections; unbilled energy and revenue assurance; home moves; next best action; communications, sentiment and NPS; upsell and cross-sell; EV, solar and batteries as products), which "runs in parallel with everything below rather than waiting its turn". "2. Unbilled energy and billing accuracy" ("This finishes billing correctly"). "3. Forward CLV" ("the spine every lever is judged against", tested on held-back history). "4. Per-customer decisions" ("Continues alongside"). "5. The levers, in merit order" (debt cashflow forecasting and negotiating tools; home moves; next best action; margin and risk; value-add). "6. Forward simulation" ("a hypothesis that longer runs add value", "after the levers deliberately"). "7. Communications, sentiment and NPS" ("Last"). Director: "It's the order from here and it supersedes the 4 September re-ranking where they differ." Amended the same day: treat next best action "as the decision that spans debt, retention, upsell and carbon advice, judged by CLV, rather than as a fixed ranking of measures"; "their benefit first, then ours".
sources: R-D-42, R-L-37, R-L-38, R-L-39 (all 10-05)
on standing pages: CLAUDE.md no; DIRECTOR_CANON.md no (machine copy: docs/direction/priority_order.yaml)

**2. The order is expected to change, by evidence.** "Doing what this document says after learning it is wrong is the failure, not departing from it." When the knowledge work changes the order, "propose it with the evidence and keep going"; the director rules. "Escalate with a proposal, and don't wait."
sources: R-L-28 (10-04), R-D-42, R-L-37, R-L-38 (10-05)
on standing pages: CLAUDE.md partly (the generic rule is at CLAUDE.md:156, not tied to the order); DIRECTOR_CANON.md no

**3. Within a step.** "Within a step, sequence by four tests: whether other work rests on it; where it sits in the merit order (pays, stays, margin, value-add); whether the world contains what it needs yet; and whether the knowledge exists." The CLV merit order is "pays, then stays, then margin, then value-add" and is still the director's frame ("the first rung of my CLV merit order"). For billing: "Where it disagrees, the validator wins."
sources: R-F-80 (09-05), R-L-22 (10-03), R-D-45 (10-05)
on standing pages: CLAUDE.md no; DIRECTOR_CANON.md no (merit order is on no page)

**4. The draw must follow the order.** "Verify the draw follows this order, not just the dials. On 4 September a re-ranking changed the weights and the work did not move, because the dials were not what was choosing." "In-flight work finishes first." "Build nothing that forecloses forward simulation." The sequence is "a weight" ("A gate can empty the feasible set"); "Everything else is a dial that orders work but never zeroes it." The recurring failure is a declared priority not drawn: R-B-98, "I can't see the two queued items" (R-L-18), "How far: not very" (R-L-25), "I can't see any work on it yet" (R-L-43). The checker (tools/draw_follows_the_order.py) is reported on origin, absent from the W/repo copy.
sources: R-B-98 (07-23), R-S-32 (08-28), R-F-81 (09-05), R-L-18 (09-29), R-L-25 (10-03), R-D-44, R-L-37 (10-05), R-L-43 (10-07)
on standing pages: CLAUDE.md partly (dial wording only, CLAUDE.md:193); DIRECTOR_CANON.md no

**5. A portfolio, supplier-weighted.** "A queue drains, and a drained queue leaves only polishing" (R-B-173). Spread "across all four areas rather than letting one absorb the week" (Knowledge, World, Supplier, Interfaces; R-L-27). "My priority order is mostly supplier work": every stretch carries "at least two supplier items from the priority order"; "World fidelity work continues, but only where it blocks a supplier result"; report "the world/supplier/other split of commits in each stretch log" (R-L-57). Where the world does block, it goes first: "build the household side before the supplier side"; "Calibrate and fix the world's behaviour... before testing any supplier solution against it" (R-L-62); bill-shock response before grading the engine (R-L-64). Guard against "depth without breadth" (R-C1-33).
sources: R-S-140 (undated), R-B-173 (07-29), R-C1-33 (08-19), R-L-27 (10-03), R-L-50 (10-08), R-L-57 (10-10), R-L-62 (10-11), R-L-64 (10-12)
on standing pages: CLAUDE.md no; DIRECTOR_CANON.md no (partly for R-C1-33)

**6. Product first; machinery only on breakage or as a named dependency.** "Machinery from here: only on breakage, or as an explicit named dependency of an item above, stated as such in the commit." "verdicts must land as product changes, not further meta." "product does not wait for the machinery that guarantees product." Under pressure: "draw only product work or anything that genuinely blocks a landing"; "Machinery only when nothing can land." Structural debt waits: "Raise it again when it next costs real work." If lanes contend, the top product items "win the draw". The mix is watched: "half the model-driven work is product, against 7 in 100 last week."
sources: R-A-70, R-A-79, R-B-98 (07-23), R-L-02 (09-25), R-L-18 (09-29), R-L-27 (10-03), R-L-47 (10-08)
on standing pages: CLAUDE.md no (grep finds no such rule; the extract said partly); DIRECTOR_CANON.md no

**7. Breakage and wrongness go first.** "A BLOCKING finding draws ahead of the general disposition queue, ahead of latent findings, and ahead of new feature work in its own lane." "504s first." "That's wrong on a live surface, so it goes first." A wrong public banner: "Fix both" (R-L-05). A crash: "Stop what you're doing and fix this first" (R-L-54). "Landings come before experiments." "When your own machinery blocks you, fix the scheduling and carry on. Stop only for decisions reserved to me." "A report about a class that keeps getting outranked should not itself be outranked."
sources: R-C2-28 (08-09), R-C1-137 (08-12), R-C1-57 (08-20), R-C1-111 (08-31), R-L-05 (09-26), R-L-51, R-L-54 (10-09)
on standing pages: CLAUDE.md no (partly for R-C1-57, R-C1-111); DIRECTOR_CANON.md no (partly for the same two)

**8. Knowledge before build.** "Addendum, standing from now on: knowledge before build. Before building or changing any supplier capability, write or amend the relevant knowledge page first." "Publish it on the site, and cite the page in the build commit." "A question to me comes only after that page shows the answer isn't published"; on regulation, "search Ofgem's licence conditions and decisions before asking me." "The page must genuinely explain, and if the mechanics threaten the content, the content wins."
sources: R-D-77 (09-05), R-L-59, R-L-60 (10-11)
on standing pages: CLAUDE.md partly (CLAUDE.md:56 "Knowledge first is a RULE" covers numbers, not page-before-build or the commit citation); DIRECTOR_CANON.md no

**9. Priority is his; sequencing is the machine's.** "This ruling sets priority, not order of operations." A list "is not a sequence and must not be executed as a list. The delivery seat sequences it." "Sequence it all yourself and start. Don't come back for permission on the shape." A ledgered ruling is itself the authorisation (R-B-49). A blocked item of rank "must not sit silent again", and no item is left blocked on an unstated level (R-A-85, R-B-152). Visible surfaces: "his review is NEVER a gate and the loop NEVER waits for it."
sources: R-E-30 (07-16), R-B-49 (07-22), R-A-85, R-B-152 (07-28), R-C1-118 (08-28), R-C1-101 (08-30), R-L-22 (10-03)
on standing pages: CLAUDE.md no (partly for R-C1-118); DIRECTOR_CANON.md no

**10. Method: ceiling first, proposal before build, cost governs.** "Measure the ceiling before the programme rather than after six passes." "Proposal before build." "Nothing is deleted until its replacement is live"; rollback, "not to push forward through a red site." "Cost is the governor." "Every run should answer a stated question with the smallest run that can answer it."
sources: R-C2-81 (08-11), R-C2-49 (08-17), R-F-71, R-D-26 (09-04), R-L-46 (10-08)
on standing pages: CLAUDE.md no (partly for R-C2-49); DIRECTOR_CANON.md no

**11. Epochs: finish, don't start; scouting is licensed, dissolving the arc is not.** "Opening a new epoch is a deliberate category-6 decision the director will make when fresh, with proper framing — not a reflex at the end of a long session." "Until then: finish, don't start." "Crossing an epoch boundary to scout or to type an interface is fine... What I'm not licensing is the arc dissolving." "Epoch 3 is re-ranked, not cancelled"; "The ranking is a statement about value, not a prohibition." E2-E5 commitment sets are "the floor, not the ceiling". Whether the gates still bind is open (section 3, item 5).
sources: R-E-32 (07-16), R-C1-140 (08-08), R-C2-23 (08-09), R-C1-33 (08-19), R-D-23, R-D-26 (09-04)
on standing pages: CLAUDE.md no ("epoch" appears 0 times); DIRECTOR_CANON.md partly (11 mentions, stale)

**12. Look ahead only for constraints on the present.** Forward discovery is ranked by certainty and mission-criticality; contingent policy is "one line, never a build". Tracks F1-F5 are DISCOVER-only and yield to core until one graduates by explicit steer (F1 did, 07-22).
sources: R-B-8 (07-19), R-B-43, R-B-44 (07-21), R-B-49 (07-22)
on standing pages: CLAUDE.md no; DIRECTOR_CANON.md no

**13. Book composition and size are his.** "Suspend I&C from the book. Keep the capability built and tested, don't delete it, but stop the company serving business accounts for now." Founder ceiling and prospect cap: "Those two numbers stay my decision"; 10-08: founders 400 (ceiling 500), prospect cap 400, count set by the 400-founder run.
sources: R-C1-69 (08-24), R-L-46, R-L-48, R-L-49 (10-08)
on standing pages: CLAUDE.md no; DIRECTOR_CANON.md no

## 2. Supersession chains (what replaced what)

- Arc: M1-M4 under Epoch 2 (07-12, R-E-15, R-S-91) -> epochs open only by director act (07-16, R-E-32) -> Epoch 2 open, value cycle released (08-26, R-F-24) -> R1-R5 first, then Epoch 3 (09-04, R-D-23, R-F-71) -> SIM, then bill, then supplier (09-05, R-F-80) -> phase one = believable meter data (09-08, R-F-114) -> seven-step order (10-05, R-D-42, R-L-37, GOVERNS NOW).
- Stage gate: "No use case gets built until those two stages are done" (09-06, R-F-88) -> "the rest of stage 1" still current (09-25, R-L-01; 10-03, R-L-27) -> pricing may see payment history, "Pricing changes are allowed for this" (10-03, R-L-22) -> per-customer decisions "alongside" (10-05, R-D-42) -> "My priority order is mostly supplier work" (10-10, R-L-57, GOVERNS NOW). Evident only: R-D-42 names the 09-04 canon, not R-F-80 or R-F-88.
- Dials to check: "a change of weights, not of machinery" (09-04, R-D-26) -> "Leave the sequence as a weight... tell me and I'll rule" (09-05, R-F-81) -> "Verify the draw follows this order, not just the dials" (10-05, R-D-44, R-L-37, GOVERNS NOW). The 09-04 re-rank did not move the work (R-D-26 note).
- Levers: a fixed merit-order list (10-05, R-D-42) -> next best action as one CLV-judged decision across debt, retention, upsell, carbon advice (10-05, R-L-39) -> debt merged with a personal payment plan, then one engine on a forward cash forecast (10-11, R-L-59, R-L-61) -> world bill-shock response first, supplier-controlled levers first, one consumption forecast after the engine's first result (10-12, R-L-64, GOVERNS NOW).
- Balance: five-category portfolio (07-29, R-B-173) -> four areas (10-03, R-L-27) -> two supplier items a stretch, world only where it blocks (10-10, R-L-57) -> world first for the payment engine, freeze then solve (10-11, R-L-62) -> (10-12, R-L-64, GOVERNS NOW).
- Depth and years: R5 book depth (09-04, R-D-23) -> the director's own hypothesis, "book depth" (09-26, R-L-06) -> depth, width, flow brief and "Wire SPINE_1 and run past 2025" (10-03, R-L-22, R-L-27) -> per-decision probe "the right instrument" (10-03, R-L-26) -> forward simulation at step 6 (10-05, R-D-42) -> smallest run that answers (10-08, R-L-46, GOVERNS NOW). (Corrects the extract note that R5 never returned.)
- Site: SITE V5 pages first (07-23, R-A-70) -> 504s outrank an incomplete page (08-20, R-C1-57) -> "Don't panic about the website. Nobody is reading it." (08-25, R-C1-87) -> a wrong public banner still goes first (09-26, R-L-05) -> site is where knowledge is published and cited (10-11, R-L-60, GOVERNS NOW). The site is a step nowhere in the 10-05 order.
- Knowledge: parallel, never waiting its turn (10-05, R-D-42) -> knowledge before build (10-11, R-L-60, GOVERNS NOW): parallel became a precondition for supplier builds.

## 3. Unreconciled conflicts (needs the director)

1. **The carbon score.** R-D-23 (09-04): R3 is the £/tCO₂e score, "the number the whole project exists to produce"; R-S-115 (07-23): "Carbon becomes the headline" (MOAP lines 223-224 still say so). R-D-42 (10-05) has no score step; R-L-38 (10-05): carbon's "main job is to show customers what they've saved and could save in CO2". A ruling must say whether the £/tCO₂e score is still a deliverable, at which step, and whether MOAP's headline is withdrawn.
2. **Billing first or payment first.** R-D-55 (09-05) rations effort "1. Payment, collections and vulnerability dynamics" first and bill accuracy third. R-D-42 (10-05) puts "Unbilled energy and billing accuracy" before debt work but names only the 09-04 canon as superseded. R-L-61 (10-11): "Payment, credit risk and forward cash forecasting are the heart of this business." A ruling must say whether R-D-55's ladder is retired or still governs world-side fidelity effort beneath the step order.
3. **Law A against a graded order.** R-S-86 (07-12): "the provisional plan is a diagnostic and tie-breaker, never a target"; R-F-81 (09-05): "A gate can empty the feasible set". R-D-44 (10-05) checks the draw against the order; R-L-57 (10-10) sets a floor of two supplier items per stretch. A ruling must say whether the order is a target the draw is graded against (Law A amended) or a diagnostic (grading and floor softened). The R-S-86 note only guesses that the "provisional plan" is now the order.
4. **The fitness function.** DIRECTOR_CANON.md reserves "Values decisions defining what the company is FOR (e.g. the Epoch-4 fitness function)" (line 38) and holds A5 "awaiting the director's choice" (lines 83-84) (R-C1-140 and R-S-125 notes: the one open values decision). R-S-115 (07-23, MOAP line 226) states the endgame as "the evolutionary tournament where EV is fitness and mortality is selection". A ruling must say whether EV-as-fitness is decided, under which definition of enterprise value (the R-C1-140 note says the 08-28 mission partly answers it), or whether MOAP's endgame line is withdrawn.
5. **Do epoch gates still bind?** R-E-32 (07-16): opening an epoch is "a deliberate category-6 decision the director will make"; R-C2-23 (08-09): "Do not pull the rest forward"; R-C1-33 (08-19): "the epochs still exist as commitment sets with their gates". The extracts disagree on whether this stands: R-E-32's note says gating is "abolished", R-C1-33's says it passed to the machine on 08-24, R-C2-23's says canon section 5 still states it. The 10-05 order has no epochs, and DIRECTOR_CANON.md still says "Epoch 2 is the current open epoch". A ruling must say whether gates are retired in favour of the seven steps, and whether step 6 inherits the Epoch-4 gate.

## 4. Lapsed (standing rulings that nothing seems to hold)

- R-D-42, R-D-44, R-D-45, R-L-37, R-L-39, R-L-57, R-L-60 (10-05..10-11): on neither CLAUDE.md nor DIRECTOR_CANON.md (grep).
- R-L-03, R-L-04 (09-25): product-only mode control, measure-first; the director could not see it on 09-29 (R-L-18); no later entry shows it landed.
- R-C1-33 (08-19): the lane-formation guard has no visible owner since gating passed to the machine (08-24, per note).
- R-B-54, R-E-8 (07-22): axes file still Version 1; rotation is "a versioned edit here" (R-E-8), yet billing rotated in via R-D-42; the three axes are nowhere in the order.
- R-E-30 (07-16): the P-4 repeal never reached PRIORITISATION_RULES.md (per note).
- R-F-54 (08-30): "say what an anchor means beyond the record" is unanswered; R-L-36 (10-04) answered it for carbon only; it gates step 6.
- R-F-88 (09-06): reserved items "which use cases per epoch" and "the hedging risk envelope" sit on no open register.
- R-C1-69 (08-24): the I&C suspension is on no standing page; suspended I&C accounts were still in the book on 08-25 (per note).
- R-B-81 (07-23): MC-1 mechanism-or-script re-grading never mentioned again. R-B-174 (07-29): "release the 27 director-blocked mints", TF2 to atoms and show-the-working left open; the audit "stalled" (per note). R-B-44 (07-21): F3 volunteer programme HELD since 07-22, no movement.
- R-C1-137 (08-12): whether a BLOCKING finding still jumps the queue is unverified (the 08-28 staging order ranks by kind, then age); R-C2-28 (08-09): nothing mechanises it.
- R-S-90, R-S-91 (07-12, 07-13): DIRECTOR_CANON.md lines 57, 61 still say Epoch 2 is current; plain staleness the machine may correct (R-L-28, 10-04) once section 3 item 5 is ruled.

## 5. Good ideas that dropped out of sight

1. R-S-128 (Jun): the Transition Test, five conditions after which replacing simulation interfaces "is an integration task, not a rebuild"; in no canon, and nobody is named to declare it met.
2. R-S-138: the 80/20 ranking after every run, "the 20% of dimensions that drive 80% of value variance become the design brief"; it would tell the "automated method" what to automate.
3. R-E-15, R-S-91 (07-12): the M2-M4 exit tests are step 2's missing acceptance language: "a bill can be lawfully wrong then corrected"; "recognises a real supplier's life".
4. R-F-114 (09-08): the phase-one test as a standing believability check: "look at a household's half-hourly gas and electricity for a year and believe it, and be able to say why it looks like that", across a spread "not a set of rescaled copies of one profile".
5. R-B-43 (07-21): certainty times mission-criticality ranks forward discovery; contingent policy is "one line, never a build".
6. R-B-107 (07-23): the locational breadcrumb: value re-enters at the personalisation layer through distribution red-band avoidance, where it meets the £/tCO₂e thesis.
7. R-B-173 (07-29): re-verifying at-target work "must never be what fills a day"; R-L-57's supplier floor is the first mechanism since.
8. R-C1-118 (08-28): P5, "£ or % is unresolved and systematically distorting", still unanswered; P3, "Draw genuine within-household variance, not a subgroup mean shift".
9. R-F-121 (09-10): the settlement budget as "the constraint we argue about rather than the one that silently refused 409 wins", and "don't draw work that can't change a level"; relevant now to the 5,000 customer-year budget (R-L-48).

## 6. One-offs now done (safe to retire from canon)

R-A-85, R-B-11, R-B-17, R-B-40, R-B-49, R-B-98, R-B-152, R-C1-19, R-C1-78, R-C1-101, R-C1-126, R-C2-10, R-C2-58, R-E-33, R-E-39, R-E-44, R-F-24, R-F-47, R-F-103, R-F-108, R-F-117,
R-S-105, R-S-151, R-L-01, R-L-02, R-L-05, R-L-54, R-L-63.
