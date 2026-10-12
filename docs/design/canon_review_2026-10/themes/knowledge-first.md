# Theme: knowledge-first (37 entries)

### [R-A-3] Claim-status discipline applies to the pitch itself
- date: 2026-07-28
- source: docs/staging/done/DIRECTOR_CANON_PITCH_V7_2026-07-28.md
- kind: ruling
- theme: knowledge-first
- ruling: Any figure or finding the pitch cites "must be derivable from primary state at publication time, and a citation that has since been overturned or closed is a claim-status defect — the same class as an aspiration written in the present tense on the site." Reconcile line-by-line against primary state: verified / stale / contradicted / not-checkable, with citation; future-state claims in the conditional are exempt.
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: partly ("The canon page still matches the code" → canon_drift_check + canon_claims.yaml; the pitch is not named)
- reflected_in_DIRECTOR_CANON_md: no
- note: The four advisor-found defects (payment blind-spot bullet contradicting f6238fd7f; stale spike-tail "blocking defect"; "two disciplines" listing three; footer "Draft v5") were one-off work; PITCH_V7_RECONCILIATION_2026-07-28.md exists. Whether the pitch body was ever corrected is unclear — the header says the body is "unedited".

### [R-A-51] A gap list is not a page; if there is not enough understanding, ship a STUB
- date: 2026-07-28
- source: docs/staging/done/DIRECTOR_RULING_KPILOT_DECOMPOSITION_2026-07-28.md
- kind: ruling
- theme: knowledge-first
- ruling: "It updated. But mostly just wrote a list of things it hasn't yet done. This is not done." Rule: "named gaps live in the residuals rung, never in the body. The body contains explanation of what we do understand. If there is not enough understanding to fill a body, ship a STUB — identity, place in the graph, and 'not yet written' ... A page that is mostly its own to-do list is a stub in costume, and it is worse than a stub because it claims depth it does not have."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: no
- reflected_in_DIRECTOR_CANON_md: no
- note: Knowledge-layer rule; CLAUDE.md names the knowledge layer but none of its content rules.

### [R-A-52] The scope brief must be independent — transcription is not scoping
- date: 2026-07-28
- source: docs/staging/done/DIRECTOR_RULING_KPILOT_DECOMPOSITION_2026-07-28.md
- kind: ruling
- theme: knowledge-first
- ruling: "The updated page's gap list is substantially the director's off-the-cuff list. That is assembly-first displaced one level ... Neither is the domain." A scope brief asks "what must a complete treatment of this topic contain, for a reader who needs to understand it? — answered from the domain, from practitioner expectation, from the structure of the market itself." Evidence of independence: "the brief contains material neither the director nor the repo supplied."
- scope: standing
- superseded_by: none seen (KPILOT_SCOPE_INDEPENDENCE_EVIDENCE.md exists)
- reflected_in_CLAUDE_md: partly ("Knowledge first is a RULE"; "Knowledge has three sides")
- reflected_in_DIRECTOR_CANON_md: no
- note: none

### [R-A-53] Gas and electricity wholesale are separate topics; coupling is an EDGE, never a merger; the decomposition is the deliverable
- date: 2026-07-28
- source: docs/staging/done/DIRECTOR_RULING_KPILOT_DECOMPOSITION_2026-07-28.md
- kind: ruling
- theme: knowledge-first
- ruling: "gas wholesale and electricity wholesale are treated separately" — they differ in products, mechanisms and drivers; "They are coupled, not merged: gas price drives electricity price for most GB hours. Coupling is an EDGE (drives), never a merger." General test for every topic: "do these things share products, mechanisms and drivers? Shared → one topic. Different → separate topics with a typed edge." "This is why I'm talking about the importance of knowledge data structure." "The DECOMPOSITION is now the deliverable, not the page." Map first, then ONE node to depth ("product structure and shape is possibly the most important thing we use"), rest as stubs, existing page re-scoped not deleted, charts bind.
- scope: standing (the topic test and graph principle); one-off (the wholesale map)
- superseded_by: none seen (KPILOT_WHOLESALE_DOMAIN_TOPIC_MAP.md exists)
- reflected_in_CLAUDE_md: no
- reflected_in_DIRECTOR_CANON_md: no
- note: The shared products/mechanisms/drivers test is a general knowledge-graph design rule with no canon home; Oct-2026 ADVISOR_FINDINGS on the knowledge layer having "no link to its consumers" suggests the graph structure question is still live.

---

## docs/staging/done/DIRECTOR_RULING_KPILOT_SCOPE_FIRST_2026-07-28.md

### [R-A-54] Scope-first, permanently, for every knowledge page; the brief-vs-assembly delta is the primary finding
- date: 2026-07-28
- source: docs/staging/done/DIRECTOR_RULING_KPILOT_SCOPE_FIRST_2026-07-28.md
- kind: ruling
- theme: knowledge-first
- ruling: "assembling from existing material can only reproduce existing material, gaps included, because the material does not know what it is missing." RULING: "1. Write the scope brief FIRST, independently of what we hold ... 2. Then assemble against it ... 3. The DELTA between brief and assembly is the primary finding — the named gaps in our own understanding, published as such. That delta is worth more than the page. 4. Blind where possible" (the board-spec pattern). "The ~80%-derivation thesis is WITHDRAWN as a design goal. It was a cost claim wearing quality clothes."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: partly (knowledge-first rule; not the scope-first method)
- reflected_in_DIRECTOR_CANON_md: no
- note: Director's domain checklist for GB price formation (recorded as his practitioner expectation): traded product structure and shape (baseload/peak, seasons, quarters, months, day-ahead, within-day) — "possibly the most important thing we use"; gas as the global anchor (NBP/TTF, LNG); weather into demand and generation; interconnectors; CfDs and their effect on the merit order and consumer price; negative prices; seasonality.

### [R-A-97] "Let the data guide us rather than just guess": no a priori weights; any unavoidable weight is chosen, declared, sensitivity-tested; iterate
- date: 2026-07-20
- source: docs/staging/done/DIRECTOR_STEER_SEGMENTATION_LEARNING_VALUE_REFRAME_2026-07-20.md
- kind: ruling
- theme: knowledge-first
- ruling: "this is going to be iterative and we need to let the data guide us rather than just guess." "hand-assigned weights are a guess dressed as precision." Derive segment importance from data (variance explained, decision-sensitivity, distinctness); "Where a weight or threshold is unavoidable, it is chosen, declared, and sensitivity-tested"; re-derive the ~12-segment knee — "It may move — that is information, not error."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: yes in spirit ("A number you need is a question to research, never a value to pick"; "Prefer measuring to arguing")
- reflected_in_DIRECTOR_CANON_md: no
- note: none

### [R-B-14] Market and cost logic must be DISCOVERED, not handed over; wholesale price is an output, a supplier's cost is a weighted average of prior purchases
- date: 2026-07-19
- source: docs/staging/in_progress/DIRECTOR_CAMPAIGN_EPOCH2_COUPLED_WORLD_2026-07-19.md
- kind: canon
- theme: knowledge-first
- ruling: "National wholesale price is an output at a national level of global energy prices and weather. Itself driven by industrial and residential demand and interconnection. This drives the supplier to price for retail products bought now. But otherwise, if fixed prices bought before, the actual price doesn't change." The advisor supplies no causal chain because "a sketched chain becomes a specification"; discover from real sources.
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: partly ("Knowledge first is a RULE… A number you need is a question to research")
- reflected_in_DIRECTOR_CANON_md: no
- note: The advisor's hedged-supplier volume-coupling hypothesis is explicitly "to be tested or refuted, not built". Later WHOLESALE_VALUE_CHAIN (07-22) and SCENARIO_SPINE (07-23) build on exactly this distinction.

### [R-B-42] W1_8 zonal pricing is closed: "REMA is a waste of time. It isn't live policy. Why are we researching things that don't exist."
- date: 2026-07-21
- source: docs/staging/in_progress/DIRECTOR_STEER_FORWARD_DISCOVERY_REGISTER_2026-07-21.md
- kind: ruling
- theme: knowledge-first
- ruling: The government rejected zonal pricing in July 2025; W1_8 models a future explicitly declined. Close the atom (retire or one-line watching brief); the earlier console line opening W1_8 DISCOVER is superseded.
- scope: one-off
- superseded_by: none seen
- reflected_in_CLAUDE_md: no
- reflected_in_DIRECTOR_CANON_md: no
- note: Done — FORWARD_DISCOVERY_REGISTER.md carries zonal as a contingent-policy watching brief. Note the KEEP_BUILDING directive of the same day still lists "W1_8 zonal (epoch-console schema gate)" among the director's gates — the two 07-21 docs disagree; this ruling is the later word.

### [R-C1-2] Knowledge → discovery → roadmap, never a constant chosen because a number was needed
- date: 2026-08-30
- source: docs/staging/done/DIRECTOR_BRIEF_CHOICE_AND_CHANNEL_2026-08-30.md
- kind: canon
- theme: knowledge-first
- ruling: "Knowledge from published sources → discovery against what we have built → a roadmap. Never a constant chosen because a number was needed." "Where the published record runs out — and it will, the CMA redacts per-supplier CAC — say so rather than filling the gap with a plausible number."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: yes
- reflected_in_DIRECTOR_CANON_md: no
- note: Same ordering ruled on 2026-08-28 (console, acquisition economics) and 2026-08-30 (console, constants review). CLAUDE.md carries it as "Knowledge first is a RULE, not a preference."

### [R-C1-5] Simplify, but record what you simplified and what it would take to do properly
- date: 2026-08-30
- source: docs/staging/done/DIRECTOR_BRIEF_CHOICE_AND_CHANNEL_2026-08-30.md
- kind: canon
- theme: knowledge-first
- ruling: "A crude version of the whole loop is worth more than a perfect version of one part. Simplify wherever necessary — but record what was simplified, what it would take to do properly, and what it would change if done."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: partly
- reflected_in_DIRECTOR_CANON_md: no
- note: CLAUDE.md's constants-origin rule accepts "a named simplification with what it would take to do properly" as a valid origin, and docs/design/simplifications/<atom>.yaml exists as a home. The general design habit ("the roadmap should tell us what is next, rather than leaving us to discover it when a result looks wrong") is not stated.

### [R-C1-6] Write choice and channel as a Knowledge layer, not only as code
- date: 2026-08-30
- source: docs/staging/done/DIRECTOR_BRIEF_CHOICE_AND_CHANNEL_2026-08-30.md
- kind: canon
- theme: knowledge-first
- ruling: "Treat this as a Knowledge layer in its own right, in the same shape as the wholesale-formation, price-cap, metering and cost-stack pages: what the published evidence establishes, what it does not, what we have assumed and why, and what would settle it." "Of all our domain areas this is the one where published understanding is thinnest and most contested — which makes it the place where the project might say something rather than merely explain something."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: partly
- reflected_in_DIRECTOR_CANON_md: no
- note: CLAUDE.md points at the knowledge layer as a place to read; it does not say that every new mechanic must be written up as a Knowledge page in this four-part shape (establishes / does not / assumed / what would settle it). That page-shape standard is a good idea that appears only here.

### [R-C1-21] Knowledge pages: pilot first; badge must distinguish "written, awaiting check" from "stub, never touched"; a director check against source moves a page to verified
- date: 2026-08-18
- source: docs/staging/done/DIRECTOR_CONSOLE_2026-08-18.md
- kind: console
- theme: knowledge-first
- ruling: "structural half first, then one pilot page for my review before the other eight." "Yes to the badge change: distinguish 'written, awaiting check' from 'stub, never touched', now rather than after eight repetitions." Director verified the price-cap page's two claims against Ofgem: "Record that as a check against source and move the page to verified — and note the checking route that worked, since your tooling can't render those pages."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: no
- reflected_in_DIRECTOR_CANON_md: no
- note: The review-state model (stub / unchecked / due / fresh with per-subject thresholds) was built that day. Whether Knowledge pages still carry a verification state, and whether anything re-checks them when due, is not visible here.

### [R-C1-25] The commons wins over a director document; a doc is the origin of a question, not the authority on its answer
- date: 2026-08-18
- source: docs/staging/done/DIRECTOR_CONSOLE_2026-08-18.md
- kind: console
- theme: knowledge-first
- ruling: "If what you now hold from the commons contradicts any of those, the commons wins — treat the doc as the origin of the question, not the authority on the answer, and tell me what differs."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: partly
- reflected_in_DIRECTOR_CANON_md: partly
- note: CLAUDE.md's operating model allows "correcting plain factual errors anywhere, canon included" and the canon has the regulation-commons doctrine; the explicit precedence rule (published commons > director document on a factual rate) is implied rather than stated. Good standing rule; applied here to RO buy-out 33.06 and electricity CCL 7.75 for 2025/26.

### [R-C1-105] Three structural changes: knowledge first is a rule; refuse unsourced domain constants at the door; the seat reviews interconnection, not only priority
- date: 2026-08-31
- source: docs/staging/done/DIRECTOR_CONSOLE_2026-08-31.md
- kind: ruling
- theme: knowledge-first
- ruling: "The pattern: a short-term fix that answers today's request, with a number picked because a number was needed, that comes undone when it meets the rest of the system. £150 CAC. A 0.95 churn cap. A standing charge that matches neither fuel. … That isn't carelessness — a bounded invocation can't see the whole, and we asked you for speed. So the fix is structural. One: knowledge first is the rule, not a preference. A number you need is a question to research, never a value to pick. … If nothing establishes it, that's a finding to file, and the code carries the gap explicitly rather than a placeholder that looks like an answer. Two: refuse unsourced domain constants at the door. Every rate, price, probability, threshold or cap in company/ and saas/ carries its origin — a citation, or a labelled belief the company holds and something grades, or a named simplification with what it would take to do properly. … Same name may not carry two values anywhere; a duplicated constant is refused too. Baseline the existing 263 uncommented ones as debt that only shrinks, and work it down. Three: the delivery seat reviews interconnection, not only priority. … of what landed since the last orientation, what else assumes it, and does that assumption still hold. … When the answer is 'something downstream now disagrees', that's the next item, ahead of new work."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: yes
- reflected_in_DIRECTOR_CANON_md: no
- note: All three are in CLAUDE.md with the director's quote. The 08-31 summary notes the scope is company/ and saas/ only; simulation/ constants (where the churn cap and standing charge also live) are not covered by the gate — the director's examples straddle both sides of the wall and the gate covers one. The constants debt was 197 (not 263) once scoped; "a ratchet only catches increases" needed a floor to be a real control.

### [R-C2-43] Knowledge pages carry a last-reviewed date and flip to "review due"
- date: 2026-08-17
- source: docs/staging/in_progress/DIRECTOR_BRIEF_WEBSITE_STRUCTURE_2026-08-17.md
- kind: ruling
- theme: knowledge-first
- ruling: "Every page carries a last-reviewed date, and flips to a visible 'review due' state past a threshold. Staleness must be visible on the page, not discovered by a reader." Depth pages: wholesale price formation, the cap, settlement and its clocks, the non-commodity stack, metering and reads. Built first.
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: partly (`site/knowledge/` named as where knowledge publishes; no review-date rule)
- reflected_in_DIRECTOR_CANON_md: no
- note: Same freshness property as R-C2-6/R-C2-8 for a different surface.

### [R-C2-51] "A published figure may not move without him being told first" — the three verified 2025/26 rates held
- date: 2026-08-14
- source: docs/staging/in_progress/DIRECTOR_DECISION_PENDING_RATE_REBASELINE_AND_SPLIT_APPROVAL_2026-08-14.md
- kind: ruling
- theme: knowledge-first
- ruling: "The director's condition, restated 2026-08-14: a published figure may not move without him being told first." So RO 2025 31.8→33.06 (Ofgem/DESNZ), electricity CCL 7.35→7.75 (HMRC), gas CCL unchanged were "fetched, verified, cited, and deliberately not committed until he says go." Lesson cited: the 21.9h freeze ended with £1,526,252→£1,547,113 landing unflagged.
- scope: one-off (the condition is superseded; see below)
- superseded_by: DIRECTOR_CONSOLE_2026-08-18 — "a new standing rule replacing the notify-first condition on figures: never wait for me... three lawful outcomes: CORRECT... CAVEAT... WITHDRAW... Freezing and waiting for me is not one of the three... Keep notify-first only for changes of method or basis, where the judgement is genuinely mine. Apply it now: land the three verified 2025/26 rates."
- reflected_in_CLAUDE_md: partly (operating model "Get on with... correcting plain factual errors"; the three-outcome rule itself is not stated)
- reflected_in_DIRECTOR_CANON_md: no
- note: Lapsed park: the file's 2026-08-18 header says it "Unblocks on his explicit reply" — the reply arrived the same day (18:4xZ) and the file still sits in in_progress/ parked on it. Whether the three rates then landed is not evidenced here (EP14 2026-08-19 source-checked the RO table "EXACT, twenty of twenty inputs"). The egress note — transcribing a public figure is not runtime egress; "If the director reads that distinction differently, the three rates above should be dropped, not the allowlist widened" — reflects CLAUDE.md's sandbox-profile wall.

### [R-C2-52] CCL history: two published years may be wrong (0.775 p/kWh 2023–2025 vs table 7.26/7.35)
- date: 2026-08-14
- source: docs/staging/in_progress/DIRECTOR_DECISION_PENDING_RATE_REBASELINE_AND_SPLIT_APPROVAL_2026-08-14.md
- kind: other (finding routed to the director; his instruction followed on 08-18)
- theme: knowledge-first
- ruling: "If the HMRC figure is right, the published history is wrong for at least two years, not merely missing for 2025... Not touched. It is a bigger revaluation... a fidelity correction under R13 (decided blind to P&L, and it moves cost UP, i.e. margin DOWN), and it deserves its own measurement and its own heads-up." Director (08-18 console, outside batch): "take the CCL history question as its own review... verify against HMRC and tell me the size of it."
- scope: one-off
- superseded_by: none seen
- reflected_in_CLAUDE_md: partly (knowledge-first rule; "A rate/price/probability/threshold/cap declares its origin" row)
- reflected_in_DIRECTOR_CANON_md: partly (R13)
- note: Likely forgotten: no document in this batch records the CCL history review being done. A correct instinct recorded here — R13 corrections that move margin DOWN get the same blind treatment as ones that move it up.

### [R-C2-53] Low Carbon reconciliation: reconcile to one sourced mix (asked, not done)
- date: 2026-08-14
- source: docs/staging/in_progress/DIRECTOR_DECISION_PENDING_RATE_REBASELINE_AND_SPLIT_APPROVAL_2026-08-14.md
- kind: ruling
- theme: knowledge-first
- ruling: "The director asked for the same treatment on the Low Carbon disagreement... Clause 1 is what he is asking for: reconcile to one sourced mix." Source identified (DESNZ Fuel mix disclosure data table; 2024: low carbon 64.7% vs in-tree 64% / 65.5%); nine years not transcribed — "doing that badly is worse than the disagreement."
- scope: one-off
- superseded_by: none seen
- reflected_in_CLAUDE_md: partly (knowledge-first)
- reflected_in_DIRECTOR_CANON_md: no
- note: "This is the item the director asked for that I did not complete" — recorded 2026-08-14; no completion seen in this batch. Probably still open.

### [R-D-6] Knowledge first before building satisfaction's rationale — "the £150 shape again if we skip it"
- date: 2026-09-01
- source: docs/staging/done/DIRECTOR_CONSOLE_2026-09-01.md
- kind: steer
- theme: knowledge-first
- ruling: "Before you build satisfaction's rationale, do the knowledge first — this is the £150 shape again if we skip it." Establish from published sources what drives domestic satisfaction (Ofgem complaints, consumer survey, billing accuracy, contact handling, resolution time) and what bill shock actually is. "Establish the rest, then build."
- scope: standing (the rule) / one-off (the instance)
- superseded_by: none seen
- reflected_in_CLAUDE_md: yes
- reflected_in_DIRECTOR_CANON_md: no
- note: Same shape recurs on 2026-10-11 ("knowledge-before-build is now his standing rule", R-D-98) after the reactive save was built before its knowledge page — i.e. the rule was in CLAUDE.md and still had to be re-issued. That repeat is the subject of R-D-97.

### [R-D-10] Before measuring a thing, say what it is — a CLAUDE.md habit beside knowledge-first
- date: 2026-09-01
- source: docs/staging/done/DIRECTOR_CONSOLE_2026-09-01.md
- kind: canon
- theme: knowledge-first
- ruling: "Before measuring a thing, say what it is. If the definition splits into several distinct experiences, measure them separately or state plainly which one you mean. Average unit rate, net margin, and the journey's end having two homes are the same failure — a concept nobody defined, differenced, published and then treated as a driver. Put it in CLAUDE.md as a habit alongside knowledge-first."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: yes (verbatim habit)
- reflected_in_DIRECTOR_CANON_md: no
- note: Fully reflected. One of the few rulings in this batch that reached its named home.

### [R-D-11] Knowledge has a third side — the practitioner; when a reading is odd against the industry, ask rather than build
- date: 2026-09-01
- source: docs/staging/done/DIRECTOR_CONSOLE_2026-09-01.md
- kind: canon
- theme: knowledge-first
- ruling: "That's the third side of the loop: published evidence for what's established, discovery for what our code does, and a practitioner for what's obvious to anyone in the industry and therefore never written down. When something reads oddly against how the industry actually works, say so and ask rather than building on it."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: yes
- reflected_in_DIRECTOR_CANON_md: no
- note: Fully reflected. Sits in mild tension with "Escalate on NTFY, never in the window" and "Silence is validation" — the reconciled canon should say that a practitioner question is an NTFY with a recommendation, not a stall.

### [R-D-46] Proper knowledge work, not a toggle re-check, on back-billing and liability, read access and theft duties, and bad debt provisioning; then set the toggles from what you find
- date: 2026-10-07
- source: docs/staging/done/DIRECTOR_STEER_KNOWLEDGE_AND_SCALE_2026-10-07.md
- kind: steer
- theme: knowledge-first
- ruling: "Don't stop what you're doing — take this as the next work after the current piece." "Back-billing and liability, read access and theft duties, and bad debt provisioning each deserve proper knowledge work, not a re-check of a toggle value. Treat them like the step-1 areas: sources, what's established, what isn't, written up as knowledge. Then set the toggles from what you find."
- scope: one-off
- superseded_by: none seen (itself supersedes the "re-check the toggles" part of the 2026-10-06 console message)
- reflected_in_CLAUDE_md: yes (knowledge first)
- reflected_in_DIRECTOR_CANON_md: no
- note: CHANGES the 2026-10-06 instruction (toggle re-check → knowledge work). The knowledge half landed (`fbe24afea` per the header note).

### [R-D-84] Knowledge-before-build is the director's standing rule (re-issued after the reactive save shipped before its knowledge page)
- date: 2026-10-11
- source: docs/staging/ADVISOR_FINDINGS_A_DIRECTOR_CORRECTION_IS_NARRATED_ONCE_AND_NEVER_COUNTED_2026-10-11.md
- kind: standing
- theme: knowledge-first
- ruling: "the reactive save went live as a supplier capability before its knowledge said whether matching the best deal had any published basis; the director caught it; it is recorded as a design choice; and knowledge-before-build became his standing rule. That sentence is the whole record." (Stretch log 2026-10-11: "The director has made knowledge-before-build standing from 04:21.")
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: yes ("Knowledge first is a RULE, not a preference")
- reflected_in_DIRECTOR_CANON_md: no
- note: A rule that was already in CLAUDE.md had to be re-made standing by the director on 2026-10-11 — the clearest evidence in the batch that CLAUDE.md prose is not holding on its own. The only record of the re-issue is a stretch-log sentence.

### [R-F-14] Rate tables: fetch real published rates rather than extrapolate; mark anything still extrapolated on the surface that shows it
- date: 2026-08-14
- source: docs/staging/console/DIRECTOR_CONSOLE_2026-08-14.md
- kind: ruling
- theme: knowledge-first
- ruling: "The 13 rate tables clamping past 2024 — fetch the real published rates rather than extrapolating, and mark anything still extrapolated as such on the surface that shows it. Same for the Low Carbon source."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: partly
- reflected_in_DIRECTOR_CANON_md: no
- note: Possibly lapsed: the 08-26 and 08-27 summaries still carry "£391,531.72 of published 2025 stack, 8.09%, priced on silently clamped tables" as a red test needing a decision; no later turn in this batch closes it. Knowledge-first in CLAUDE.md covers constants, not the "mark extrapolation on the surface" half.

### [R-F-41] Marginals come from published evidence, never from what makes the arm look good
- date: 2026-08-27
- source: docs/staging/console/DIRECTOR_CONSOLE_2026-08-27.md
- kind: ruling
- theme: knowledge-first
- ruling: "On the marginals: derive them from published evidence, not from what makes the arm look good. Ofgem's consumer surveys, switching rates by segment, engagement data — take the distribution from what's published and cite it. If the honest distribution leaves little to infer, that's the finding."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: yes
- reflected_in_DIRECTOR_CANON_md: partly
- note: The precursor to the 08-30 "knowledge first is the rule" trio. "If the honest distribution leaves little to infer, that's the finding" — the R1 ceiling later found exactly that (elasticity not recoverable from observables).

### [R-F-55] Knowledge first is the rule, not a preference: a number you need is a question to research, never a value to pick
- date: 2026-08-30
- source: docs/staging/console/DIRECTOR_CONSOLE_2026-08-30.md
- kind: standing
- theme: knowledge-first
- ruling: "One: knowledge first is the rule, not a preference. A number you need is a question to research, never a value to pick. Check the knowledge layer, the commons and the published record before writing any domain constant. If nothing establishes it, that's a finding to file, and the code carries the gap explicitly rather than a placeholder that looks like an answer." Context: "a short-term fix that answers today's request, with a number picked because a number was needed … £150 CAC. A 0.95 churn cap. A standing charge that matches neither fuel. … That isn't carelessness — a bounded invocation can't see the whole, and we asked you for speed. So the fix is structural."
- scope: standing
- superseded_by: refined 2026-09-08 (R-F-112): omission is not neutrality — near-certain relationships are modelled as stated beliefs, not left out
- reflected_in_CLAUDE_md: yes
- reflected_in_DIRECTOR_CANON_md: no
- note: CLAUDE.md carries this verbatim but NOT the 09-08 refinement; see contradictions.

### [R-F-56] Refuse unsourced domain constants at the door; one name may not carry two values; baseline the debt and shrink it
- date: 2026-08-30
- source: docs/staging/console/DIRECTOR_CONSOLE_2026-08-30.md
- kind: standing
- theme: knowledge-first
- ruling: "Two: refuse unsourced domain constants at the door. Every rate, price, probability, threshold or cap in company/ and saas/ carries its origin — a citation, or a labelled belief the company holds and something grades, or a named simplification with what it would take to do properly. A constant with none of those is refused, the way an unsourced money constant already is. Same name may not carry two values anywhere; a duplicated constant is refused too. Baseline the existing 263 uncommented ones as debt that only shrinks, and work it down."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: yes
- reflected_in_DIRECTOR_CANON_md: no
- note: Enforced (test_a_domain_constant_carries_its_origin). The "same name may not carry two values anywhere" clause is not in the CLAUDE.md table row. The 09-08 correction (R-F-112) narrows what "unsourced" means.

### [R-F-79] Domain understanding lands in the Knowledge layer with sources and gaps; findings about the machine go to registers
- date: 2026-09-05
- source: docs/staging/console/DIRECTOR_CONSOLE_2026-09-05.md
- kind: standing
- theme: knowledge-first
- ruling: "It should be a Knowledge page — the merit order, the £150-200 reconciliation, elasticity and churn travelling together, smart metering's value being collectability rather than cost. That's domain understanding a reader could learn from and it isn't written anywhere else here. And make that the rule rather than an instruction each time: when a piece of work produces domain understanding, it lands in the Knowledge layer with its sources and its gaps stated. Findings about the machine go to the registers. Right now we have ten knowledge pages against six class registers and hundreds of findings, which is the wrong way round for a project whose value is the domain."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: no
- reflected_in_DIRECTOR_CANON_md: no
- note: Built as knowledge_layer_gate for research docs; extended to canon on 09-07 (R-F-107) after the gap bit again. CLAUDE.md tells the seat to READ the knowledge layer first but never states the WRITE rule. "Smart metering's value being collectability rather than cost" is itself a domain insight worth a knowledge row.

### [R-F-107] Knowledge page: "How many synthetic households does it take to represent Britain, and why"; a canon document establishing domain understanding reaches the Knowledge layer like a research document
- date: 2026-09-07
- source: docs/staging/console/DIRECTOR_CONSOLE_2026-09-07.md
- kind: ruling
- theme: knowledge-first
- ruling: "The sampling design, the strata-versus-correlated-axes finding, the plausibility measurement, the cell count being derived — all of it is in canon, findings and stretch reports, and none of it is a Knowledge page. Your own gate makes a research document declare a Knowledge topic or say why not; it wasn't watching canon, and canon is where this landed. Write it up. 'How many synthetic households does it take to represent Britain, and why' is the most publishable thing here — an outsider can learn something rather than check us. Include the mechanism, not just the number: strata multiply and correlated axes don't, and here's the evidence for each. Include the floor and the seven uncounted axes, because the honest version is more persuasive than a clean one. And close the gap that let it happen: a canon document that establishes domain understanding should reach the Knowledge layer the same way a research document does."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: no
- reflected_in_DIRECTOR_CANON_md: no
- note: Gate extended to DIRECTOR_CANON_/DIRECTOR_RULING_ prefixes; 51 canon documents found undeclared (backlog of 49 noted 09-08). "The honest version is more persuasive than a clean one" is a standing publication principle. The page itself was "written and unlanded — site lane red" at 09-07 20:19 and again at 09-08; whether it reached the site is not evidenced here (he explicitly asked to verify it does).

### [R-F-112] Omission is not neutrality — it asserts zero: a near-certain relationship is modelled as a stated, movable, graded belief
- date: 2026-09-08
- source: docs/staging/console/DIRECTOR_CONSOLE_2026-09-08.md
- kind: standing
- theme: knowledge-first
- ruling: "You've over-applied a rule I helped write, and I want to correct it. 'Don't invent a constant' was aimed at unsourced numbers presented as fact — the £150 CAC, the 53p standing charge. It was never meant to forbid a relationship that physics or strong logic makes near-certain. Four people take more showers than two. That's arithmetic with a per-person volume, not a guess. DESNZ declining to confirm the relationship isn't evidence against it … And a flat base per household is itself an assumption: it asserts occupancy has exactly zero effect, which is less defensible than a stated elasticity. So the real choice is a named parameter versus a hidden one … make hot water scale with occupancy, as a labelled parameter with its basis stated … Wire it to whatever grades it so being wrong is measurable. And build the ability to vary it, because a parameter we can move is worth more than a number we're confident in. The general rule, so this doesn't recur: where physics or strong logic makes a relationship near-certain, model it as a stated belief rather than omitting it. Omission is not neutrality — it asserts zero, and zero is usually the one value we know is wrong."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: no
- reflected_in_DIRECTOR_CANON_md: no
- note: THE most important unreflected correction in the batch. CLAUDE.md carries the 08-30 rule verbatim ("An honest None with a named reason is worth more than a plausible number") with no trace of this refinement, so the standing page currently teaches exactly the over-application the director corrected. Also: "a parameter we can move is worth more than a number we're confident in" is a design principle in its own right.

### [R-S-9] Prefer measuring to arguing
- date: 2026-08-28
- source: CLAUDE.md
- kind: standing
- theme: knowledge-first
- ruling: "If a question can be settled by running something, run it. Most disagreements here are about a number nobody has looked at yet."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: yes (is the source)
- reflected_in_DIRECTOR_CANON_md: no
- note: [habits] Undated habit; file rewrite date used. Not stale.

### [R-S-10] Knowledge first is a RULE; a needed number is a question to research, never a value to pick
- date: 2026-08-30
- source: CLAUDE.md
- kind: standing
- theme: knowledge-first
- ruling: "Knowledge first is a RULE, not a preference. A number you need is a question to research, never a value to pick." If nothing establishes it, file the finding and carry the gap as an honest `None` with a named reason, never a placeholder. Director, 2026-08-30: "a short-term fix that answers today's request, with a number picked because a number was needed, that comes undone when it meets the rest of the system. £150 CAC. A 0.95 churn cap. … So the fix is structural."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: yes (is the source)
- reflected_in_DIRECTOR_CANON_md: no
- note: [habits] Not stale; enforced by the domain-constant-origin test in the rules table. Step 1 of the 2026-10-05 priority order ("knowledge, now and wide") rests on this rule but neither the order nor the step is named in CLAUDE.md.

### [R-S-50] A money constant citing a source must be reached
- date: 2026-08-28
- source: CLAUDE.md
- kind: standing
- theme: knowledge-first
- ruling: "A money constant citing a source must be reached" — `test_a_cited_constant_has_a_caller.py`.
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: yes (is the source)
- reflected_in_DIRECTOR_CANON_md: no
- note: [rules-table] Born of the £55-vs-£150 CAC episode. Not stale; the capital-target focus item (2026-10-11: "a module default is not the production constant") is the same class.

### [R-S-51] A rate/price/probability/threshold/cap declares its origin
- date: 2026-08-28
- source: CLAUDE.md
- kind: standing
- theme: knowledge-first
- ruling: "A rate/price/probability/threshold/cap declares its origin" — `test_a_domain_constant_carries_its_origin.py` + `tools/domain_constant_origins.py`.
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: yes (is the source)
- reflected_in_DIRECTOR_CANON_md: no
- note: [rules-table] The code form of R-S-10. Not stale.

### [R-S-56] Read the knowledge layer BEFORE making a number up; the answer is usually already here
- date: 2026-08-28
- source: CLAUDE.md
- kind: standing
- theme: knowledge-first
- ruling: "`docs/institutional/knowledge_map.md` is what we know and what we have not established; `docs/market_research/` holds the sourced anchors; the regulation commons (`docs/domain_artefact_library/`) holds the published law, readable by every lane; `site/knowledge/` … publish it. The answer is usually already here. … When something does not add up, follow the thread rather than routing around it."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: yes (is the source)
- reflected_in_DIRECTOR_CANON_md: partly (§1 regulation-commons doctrine)
- note: [working-here] Not stale. The 2026-10-05 priority order's step 1 says knowledge pages live "in their own folder; drawn as Lane 0 work" — the folder is not named here.

### [R-S-144] Research ownership — the agent owns the design; research real sources, challenge the design, validate against supplier data, propose via NTFY before building
- date: unknown
- source: docs/vision/HUMAN_SIMULATION_LAYER.md
- kind: standing
- theme: knowledge-first
- ruling: "This document is a starting point, not a specification. The agent should own the design of the human simulation layer — researching, challenging, and improving on what is described here before building." Research EPC API, ONS Census, BEIS, DVLA, academic literature; challenge the four-dimension decomposition; validate against Ofgem Consumer Confidence Survey, Citizens Advice, vulnerability registers. "After research, propose any changes to the model design via NTFY before building. The research findings go to docs/market_research/HUMAN_SIMULATION_RESEARCH.md and ASSUMPTIONS.md."
- scope: standing
- superseded_by: none seen
- reflected_in_CLAUDE_md: partly (knowledge-first rule; `docs/market_research/` named)
- reflected_in_DIRECTOR_CANON_md: no
- note: The earliest form of "knowledge first" and of "propose before building". `HUMAN_SIMULATION_RESEARCH.md` is not in the snapshot's `docs/market_research/` — the named output may never have been written. "Propose via NTFY before building" is stricter than the 2026-10-04 operating model (get on with knowledge and in-flight work; escalate only intent).

### [R-S-163] ANSWERED — practitioner question at an annual DD review (strategy) → SLC 27.15 as strengthened August 2022; DD shape set
- date: 2026-10-10 (answered 2026-10-11T04:20Z)
- source: docs/direction/DIRECTION.yaml
- kind: ruling
- theme: knowledge-first
- ruling: Director: "Your DD review question was answerable. Ofgem's August 2022 decision strengthened SLC 27.15: a fixed DD must be set on the best and most current information in all cases, taking account of reads and of customer and third-party information, and reassessed when new information would change it materially. Close the practitioner question with this." Shape: "the DD amount comes from the company's own twelve-month forecast for the property, priced at known rates where fixed and forecast rates beyond, plus the balance to be cleared."
- scope: standing (the DD-setting design)
- superseded_by: none seen
- reflected_in_CLAUDE_md: no
- reflected_in_DIRECTOR_CANON_md: no
- note: A director correction of the machine's knowledge method: it was a published-record question misfiled as practitioner knowledge. The "one forecast" design (DIRECTION thesis_read: "recentred on one engine and its forward cash forecast") stems from this and is in no standing surface. The seat's own figure in this row was corrected beside the claim (−£11k → £3.4k), per R-S-24.


