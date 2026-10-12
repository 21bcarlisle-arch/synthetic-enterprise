# product-vs-machinery: consolidated

## 1. Standing principles (what still governs)

**P1. Product is what a real supplier or market would have; machinery exists only because a harness builds this.** "if a real energy supplier or a real market would have it, it is product"; machinery is publishers, gates, alarms, reconcilers, the map, the seat. The website "publishes product but is not product" and counts as neither; "The bill validator is product"; "'the metric itself' does not count as product."
sources: R-A-69 (2026-07-23), R-A-80 (2026-07-23), R-D-27 (2026-09-05), R-D-28 (2026-09-05)
on standing pages: CLAUDE.md no; DIRECTOR_CANON.md no

**P2. The test for any piece of work.** "What can the director SEE or JUDGE today that he could not yesterday?" ("nothing" means the day failed); "Will this let the company do something it could not do before? Yes → do it. No, but something is genuinely broken → fix it. No → it is housekeeping. Batch it, do it rarely"; "what did today produce that a customer or a domain reader would notice?"
sources: R-A-69 (2026-07-23), R-A-105 (2026-07-29), R-F-123 (2026-09-16)
on standing pages: CLAUDE.md partly; DIRECTOR_CANON.md no

**P3. Do the work, not the watcher.** "Build the smallest mechanism that can fail, and prefer doing the work to building the thing that watches the work"; "R6 board sections are never the primary work." Harness work without a falsifiable end "will consume every available day indefinitely"; HARDEN re-verification "never outranks real work" and never counts toward the split.
sources: R-S-76 (2026-07-12), R-B-139 (2026-07-27), R-B-145 (2026-07-27), R-S-11 (2026-08-28), R-C1-12 (2026-08-31)
on standing pages: CLAUDE.md partly; DIRECTOR_CANON.md no

**P4. "rules held as mechanisms survive and rules held as sentences decay, so it needs both."** Each promise carries a named mechanism; agent descriptions get a check "so descriptions can't rot again."
sources: R-L-19 (2026-09-29), R-L-28 (2026-10-04)
on standing pages: CLAUDE.md partly (footer: "the sentence explains, the mechanism is the rule"); DIRECTOR_CANON.md no

**P5. Machinery earns its place** only "if something a reader or a customer depends on is broken, or if the machine genuinely cannot land work", never because it is "loud, adjacent, newly discovered": "file it and move on." Product must win against machinery items: "Being reachable isn't the same as being chosen." Latest form: "Machinery only when nothing can land." A stretch with no product progress "outranks the machinery item that displaced it." The follow-on must already be queued as an atom outranking self-filed work, else "say so plainly and tell me what would make it achievable." He "will not accept another machinery-before-product inversion."
sources: R-A-80 (2026-07-23), R-D-29 (2026-09-05), R-F-72 (2026-09-05), R-F-74 (2026-09-05), R-F-85 (2026-09-06), R-L-27 (2026-10-03)
on standing pages: CLAUDE.md no; DIRECTOR_CANON.md no

**P6. When machinery stops landing, fix it and go back.** "If something in the machinery breaks, fix it and go back; don't let it become the week." "Other lanes' reds are not yours unless they block you." "Landings come before experiments"; "When your own machinery blocks you, fix the scheduling and carry on. Stop only for decisions reserved to me." One memory budget for the box; what does not fit queues. After an outage: what would make the machine repair it itself?
sources: R-A-45 (2026-07-27), R-F-70 (2026-09-04), R-F-124 (2026-09-17), R-L-45 (2026-10-07), R-L-50 (2026-10-08), R-L-51 (2026-10-09), R-L-52 (2026-10-09), R-L-54 (2026-10-09)
on standing pages: CLAUDE.md no; DIRECTOR_CANON.md no (see conflict 3)

**P7. Measure the split; a bad ratio files itself.** "A number that is watched changes behaviour; a sentence in a document has now failed to, a dozen times"; it "must not become machinery about machinery." His tallies: 7 product in the last 100 commits on 25 Sept (46 machinery, 27 merges, 20 publish or chores); "about half" by 30 Sept; 13 of 67 commits since his 3 Oct brief. He left threshold and window open; no extract shows him setting the 25% in `PRODUCT_SHARE_FLOOR`.
sources: R-D-30 (2026-09-05), R-L-02 (2026-09-25), R-L-18 (2026-09-29), R-L-20 (2026-09-30), R-L-25 (2026-10-03)
on standing pages: CLAUDE.md no; DIRECTOR_CANON.md no (tools/product_machinery_split.py and its test exist on origin; neither it nor the 25% floor is in CLAUDE.md or any docs/operations page)

**P8. Stretch composition: all four areas, supplier first.** "spread the rest across all four areas rather than letting one absorb the week" (knowledge, world, supplier, interfaces). The 5 Oct priority order is "the order from here." "every stretch's focus carries at least two supplier items… World fidelity work continues, but only where it blocks a supplier result." "Report the world/supplier/other split of commits in each stretch log."
sources: R-L-27 (2026-10-03), R-L-37 (2026-10-05), R-L-57 (2026-10-10)
on standing pages: CLAUDE.md no; DIRECTOR_CANON.md no

**P9. Pacing is the director's word.** "I'd rather spend it slowly than stop dead." A slowdown raises the tick interval, will "draw only product work or anything that genuinely blocks a landing," ends at the reset; otherwise "Spend more of the week; don't save it" and "stop short of the wall." At 98%: land or park, start no long runs, hand off in the stretch log, stop. "Don't make it infer my budget… the modes are mine to set." Requested: one control with named modes (normal, slow, fold-only, off) that "handles the cadences and the restore itself," plus a product-only mode, built after "measure which routes actually spend tokens — not which commit most" (reactive work bypasses a draw filter); a weekly burn review where the machine may "propose changes and enact them unless I disagree."
sources: R-L-02 (2026-09-25), R-L-03 (2026-09-25), R-L-04 (2026-09-25), R-L-15 (2026-09-27), R-L-17 (2026-09-27), R-L-18 (2026-09-29), R-L-27 (2026-10-03), R-L-63 (2026-10-11), R-L-64 (2026-10-12)
on standing pages: CLAUDE.md no; DIRECTOR_CANON.md no

**P10. Merge waste: runtime state stays out of main; measure first; ask why a class recurs.** "Move the heartbeat out of main… Write it to the ops repository instead"; runtime state beside source is "a standard anti-pattern." "Build that measurement first: which files drive merges, which merges are clean and which conflict, and what they cost in time and tokens," including whether merges are "mostly noise in the commit list." Evidence: 27 merges in 100 commits (25 Sept); 12 reconciliations and 12 heartbeats in 31 overnight commits on untouched timers; 417 merges beside 1,167 work commits in a fortnight. "when a class of wasted work keeps recurring, ask why it recurs… if you can't answer because nothing measures it, the missing measurement is the first thing to build"; "Don't patch it again."
sources: R-F-85 (2026-09-06), R-L-02 (2026-09-25), R-L-04 (2026-09-25), R-L-20 (2026-09-30), R-L-35 (2026-10-04), R-L-46 (2026-10-08), R-L-54 (2026-10-09), R-L-58 (2026-10-10)
on standing pages: CLAUDE.md no; DIRECTOR_CANON.md no ("heartbeat" is on none of the three pages)

**P11. Mothball cleanly; retire what nothing reads or carries.** "When you mothball or fold a section, check what work is still being done to feed it and stop the parts that no longer earn their keep"; "remember to mothball properly" (he worries about "[out] of date and not cleanly mothballed activities"); "nothing maintained on a maybe"; "a surface no reader can reach must never be able to block publishing"; the map "half the size and true." Parked work keeps its findings, worktree path and state on record. Carried items: "Count distinct items, not rows"; triage once (fix, fold into a class register, or accept with a stated reason and retire); one carried unchanged for a week "must be triaged rather than copied forward again."
sources: R-C1-41 (2026-08-19), R-C1-46 (2026-08-20), R-C1-50 (2026-08-20), R-C1-77 (2026-08-24), R-L-12 (2026-09-27), R-L-15 (2026-09-27), R-L-36 (2026-10-04), R-L-42 (2026-10-07), R-L-63 (2026-10-11)
on standing pages: CLAUDE.md no; DIRECTOR_CANON.md no ("mothball" is on none of the three pages)

**P12. The public site.** It exists "so that an intelligent stranger can understand the project, believe it, interrogate it, and follow its progress — without learning our vocabulary"; "It is not my observability tool"; "The five tabs are the site," nothing hidden. No internal vocabulary on public pages (Harness tab excepted); figures carry date and provenance; few cross-links, links checked; publishing weekly, anchored to Monday. "Say what a reader needs in one plain sentence or say nothing."
sources: R-C2-39 (2026-08-17), R-C2-46 (2026-08-17), R-C2-47 (2026-08-17), R-C2-17 (2026-08-18), R-C1-41 (2026-08-19), R-C1-48 (2026-08-20), R-D-28 (2026-09-05), R-L-05 (2026-09-26), R-L-06 (2026-09-26)
on standing pages: CLAUDE.md no; DIRECTOR_CANON.md no

## 2. Supersession chains (what replaced what)

- Pacing: R-L-02 (2026-09-25, slow to the reset) -> R-L-16 (2026-09-27, end the slowdown sooner?) -> R-L-18 (2026-09-29, restore; "don't save it") -> R-L-27 (2026-10-03, "Go hard"; stop short of the wall) -> R-L-63 (2026-10-11, GOVERNS NOW: at 98% hand off and stop; R-L-64, 2026-10-12, resumes).
- Machinery test: R-D-29 / R-F-72 (2026-09-05, breakage or cannot land) -> R-F-74 (2026-09-05) -> R-F-124 (2026-09-17, "or a reader's page is broken") -> R-L-27 (2026-10-03, GOVERNS NOW: "Machinery only when nothing can land"; reader's-page limb not restated).
- Product measure: R-A-69 (2026-07-23, daily split; site counted as product) -> R-D-30 (2026-09-05, measure it; site neither, R-D-28) -> R-L-57 (2026-10-10, GOVERNS NOW: world/supplier/other split in every stretch log).
- Harness investment: R-B-139 (2026-07-27, "CONTINUES") -> R-A-44 (2026-07-27, exit counter; "not yet a control", R-B-159, 2026-07-28) -> R-A-105 (2026-07-29) -> R-S-11 (2026-08-28, GOVERNS NOW for work selection); "method is the IP" survives only in R-S-114 (conflict 1).
- Lane order: R-F-70 (2026-09-04) -> R-F-71 / R-F-80 (2026-09-04/05, cited in R-F-70) -> R-L-37 (2026-10-05, supersedes the 4 Sept re-ranking "where they differ") -> R-L-57 (2026-10-10, GOVERNS NOW: two supplier items per stretch).
- Site's job: R-E-5 (2026-07-22, "operational window for him") -> R-C1-48 (2026-08-20, "not my observability tool") -> R-D-28 (2026-09-05, neither product nor machinery) -> R-L-05 (2026-09-26, GOVERNS NOW: nothing internal on a public page). R-E-5 is not shown as amended; his reading surface is the stretch log (R-F-124, 2026-09-17).
- Site structure: R-C2-40 (2026-08-17) -> R-C1-40 (2026-08-19) -> R-C1-48 (2026-08-20, GOVERNS NOW: "The five tabs are the site"). R-C2-41 (2026-08-17, Knowledge before deletion) -> 2026-08-20 console quoted in R-C2-41 (GOVERNS NOW: "holes beat wrong or unintelligible content").
- Redirects: R-C2-14 (2026-08-18, redirects protected) -> R-C1-50 (2026-08-20, GOVERNS NOW: delete redirects and their checks; R-C2-15's three-state register goes "if two states now cover it").

## 3. Unreconciled conflicts (needs the director)

1. **Is the harness a product?** R-B-139 (2026-07-27: harness, methodology and CLAUDE.md discipline are "the durable IP"; method first of "the three products") and R-S-114 (2026-10-04: the harness is "the third product") against R-D-27 (2026-09-05: of machinery, "A real supplier has none of it"), R-D-29 and R-L-27. A ruling must decide whether "product" in the pitch sense and the work-split sense are different, and whether harness work ever counts toward the floor.
2. **A dial that never zeroes vs a product-only draw.** CLAUDE.md, The walls: "Everything else is a dial that orders work but never zeroes it", against R-L-02 (2026-09-25: "draw only product work or anything that genuinely blocks a landing"), R-L-03 (2026-09-25: product-only mode) and R-L-27 (2026-10-03). A ruling must decide whether those are sanctioned exceptions or machinery keeps a guaranteed minimum.
3. **Other lanes' reds.** R-F-124 (2026-09-17: "Other lanes' reds are not yours unless they block you") and R-L-51 (2026-10-09) against CLAUDE.md "an unwired module or an unfiled finding from any lane blocks every commit" (flagged in R-F-124's note). A ruling must decide whether the commit gate is lane-wide or lane-local, and what "block you" means.
4. **Who stops the machine at the wall.** R-L-03 (2026-09-25: "Don't make it infer my budget") and R-L-15 (2026-09-27: guessing gave "false excuses to stop"; "Better to hit the limit") against R-L-02 (2026-09-25: "rather spend it slowly than stop dead") and R-L-27 (2026-10-03: "stop short of the wall"); R-L-17 (2026-09-27) lets the machine enact burn changes "unless I disagree". A ruling must decide whether any allowance reading may drive the machine, and who triggers the stop when he is away.
5. **Floor level.** R-D-30 (2026-09-05) left threshold and window open; the 25% is the machine's (R-D-29 note). R-L-20 (2026-09-30) calls "about half" a good mix; R-L-57 (2026-10-10) finds about 30% world-or-supplier short on supplier. A ruling must set the number, the window, and whether it counts product overall or supplier items.
6. **Rule numbering.** R-S-114 (2026-10-04) says "R1–R17"; DIRECTOR_CANON.md §2 says "R1–R15 + Laws A/B"; R16 (R-C2-39, R-C2-47, 2026-08-17) and R17 (R-C2-63 note) are cited as director vocabulary but defined on neither page. A ruling must say which is canon.

## 4. Lapsed (standing rulings that nothing seems to hold)

- R-A-44 (2026-07-27): harness "done for now" counter never built; R-A-45's demotion of speculative harness work hung on it (R-B-159, 2026-07-28).
- R-A-69 (2026-07-23): PRODUCT/MACHINERY daily metric lapsed; the question survived as prose.
- R-D-29 (2026-09-05): the floor was "a log() line nobody read"; 4.7–7.3% product against 25% on 2026-09-16; October readings mixed (R-L-25, R-L-57).
- R-C2-59 (2026-08-10), R-C1-138 (2026-08-12): 1:1 interleave; no document records it enforced.
- R-C1-41 (2026-08-19): feed-stopping broken within days; R-C1-46 (2026-08-20): written where no gate author reads.
- R-C1-77 (2026-08-24): reading the 117 harness atoms; not evidenced done.
- R-B-145 (2026-07-27): HARDEN mothball "blocked on backlog-atom wiring"; unclear if done.
- R-L-03, R-L-04 (2026-09-25): mode control and token-route measurement; R-L-18 (2026-09-29) asked "Where are they?"; no later director entry shows either built, and R-L-27 (2026-10-03: "Lift the cadence back up") shows the restore again by hand.
- R-L-17 (2026-09-27), R-L-19 (2026-09-29): weekly "Friday burn review"; on no standing page.
- R-L-35 (2026-10-04), R-L-42 (2026-10-07): merge-cost measurement, heartbeat move, carried-item triage; no outcome in his October words, nothing on a standing page.

## 5. Good ideas that dropped out of sight

- R-A-105 (2026-07-29): the three-way test ("Tidying as the day's work" is the failure), the natural successor to the lapsed split metric; CLAUDE.md has only a softer sentence.
- R-F-123 (2026-09-16): "what did today produce that a customer or a domain reader would notice?"
- R-C2-59 (2026-08-10): never gate product work on a harness-health number, which "measures the rate of self-scrutiny, not the state of the project."
- R-F-85 (2026-09-06): "say so plainly and tell me what would make it achievable" as the standing escalation shape.
- R-L-04 (2026-09-25) with R-L-02: gate token spend, not CPU; measure routes by tokens, not commits.
- R-L-35 (2026-10-04): "the missing measurement is the first thing to build"; runtime state beside source is an anti-pattern.
- R-L-42 (2026-10-07): count distinct items, not rows; triage anything carried unchanged for a week.
- R-L-47 (2026-10-08): name structural debt with what it blocks; raise it "when it next costs real work."
- R-E-40 (2026-07-09): TIME_REPLAY, a replay slider over the event log; registered, then lost with its register.
- R-F-70 (2026-09-04): Epoch 3's walled interfaces as "the go-live seam and the most valuable unbuilt thing we have"; re-ask whether it keeps that rank.

## 6. One-offs now done (safe to retire from canon)

R-B-140, R-B-159, R-C1-40, R-C2-14, R-L-01, R-L-13, R-L-14, R-L-16, R-L-56.
Not director words, excluded: R-L-23, R-L-24, R-L-30, R-L-31 (machine continuation prompts); R-L-41 (machine report pasted).
