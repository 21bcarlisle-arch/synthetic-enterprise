# Agent report: Extract rulings: August part 1

## Brief given

Read the brief at /tmp/claude-0/canon/brief.md and follow it exactly. Your batch list is /tmp/claude-0/canon/batches/C1_august.txt (26 files, paths relative to /tmp/claude-0/canon/repo/). Your batch code is C1. Write your extract to /tmp/claude-0/canon/extracts/C1_august.md. Read every file in full. Reply with only the batch summary section.

## Report


## Batch summary
- files read: 26 (all read in full; none unreadable. DIRECTOR_CONSOLE_2026-08-20.md is 746 lines and was read in two passes. The repo extract is docs-only — zero .py files — so "enforced in code" cannot be verified here; reflection was judged against CLAUDE.md and DIRECTOR_CANON.md only, as briefed.)
- rulings extracted: 143
- most important / most likely forgotten (by id, one line each why):
  - R-C1-13 / R-C1-14 / R-C1-15 — the world validation ladder (bottom-up generation, no aggregate ever a target, never clamp to pass a check): the director calls it "the crux of what we are doing" and CLAUDE.md contains none of it — no "aggregate", "ladder" or "rung".
  - R-C1-75 — "the half-hourly spine stays half-hourly … it is the market": the clearest domain wall in the batch, from the director's own expertise, absent from CLAUDE.md and the canon; a future memory optimisation could re-fold the spine with nothing in prose to stop it.
  - R-C1-23 — CORRECT / CAVEAT / WITHDRAW, "freezing is not one", "measuring is never publishing": repeated verbatim in three fresh-session briefs, then dropped by the 08-28 rewrite; CLAUDE.md now has only "correct factual errors".
  - R-C1-22 — the harness clause of the three-lane egress ruling ("fetched bytes may become documentation, design records and Knowledge, never a runtime input the company reads"): the most checkable lane and the one the rewrite lost; CLAUDE.md keeps only "the company has no route".
  - R-C1-82 / R-C1-83 — the CLV thesis ("average by default, beat average precisely to the degree it predicts the truth better"; "inference, never access — and did it work it out?"; a flat-rules baseline is mandatory): the operational half of the mission, not in the mission block of CLAUDE.md.
  - R-C1-7 — "where the evidence is ambiguous, choose the option that makes the company's advantage harder to demonstrate … Erring against our own thesis is the safe direction": a standing calibration tie-break that has already been applied (the churn anchor) and is written only in the choice-and-channel brief.
  - R-C1-81 vs R-C1-120 — carbon: "that number is the entire point of this project" (08-25) and "deliberately out of scope for now, by director decision" (08-28) both stand unreconciled; CLAUDE.md says only "Carbon is designed and unwired."
  - R-C1-61 / R-C1-63 — the 75-minute gate ("put a limit on the absolute duration that fails loudly") and "an edit to an existing file with a control in it should face the same questions a new one does": both lapsed; the gate count grew from ten to twenty and CLAUDE.md still gates only new modules.
  - R-C1-142 vs R-C1-28 / R-C1-66 — epoch unblocking as a director-only door (08-08) was overtaken by the 08-19 and 08-24 grants but never withdrawn, and DIRECTOR_CANON.md §3a/§5 still state the old position ("the twin is the standing approver", "never self-promoted to BUILD").
  - R-C1-69 — I&C suspended from the book, "keep the capability built and tested, don't delete it": a book-composition ruling with no record in CLAUDE.md and no stated return condition.
  - R-C1-110 — "where the real signal is unavailable it should run rather than skip — a false stop costs more than a false start": a director-ruled fail-OPEN exception that CLAUDE.md's "Fail closed" default would silently reverse.
  - R-C1-139 — the 72-hour ageing clause: the director still had to say "read … now rather than waiting to draw it" on 08-28 and 08-30, and "three July mints still undrawn" is its exit test failing six weeks on.
- contradictions between documents in this batch (one line each):
  - Carbon priority: DIRECTOR_CONSOLE_2026-08-25 ("the entire point … wire it, publish it") vs DIRECTOR_GUIDANCE_THE_WORLD_MUST_PRESS_2026-08-28 ("deliberately out of scope for now").
  - Mission sentence: the 08-28 guidance protects the older sentence ("see-and-correct applies to everything except the mission sentence itself") while the 08-28 09:49 console supersedes it; both are dated 2026-08-28 and the guidance was never amended.
  - Epoch unblocking: DIRECTOR_RULING_FUTURE_COMMITMENT_SETS_2026-08-08 ("director's word only, never silence") vs DIRECTOR_CONSOLE_2026-08-19 ("authority to promote idle atoms") and 2026-08-24 ("how epochs gate — all yours to change"); DIRECTOR_CANON.md still states the 08-08 position.
  - Proof redirects: 08-19 ("Keep the redirect safety on Proof; that risk is real") and 08-20 06:45 ("must keep landing somewhere real") vs 08-20 09:19 ("Delete the redirects outright") — reversed on evidence the same day.
  - Site priority: 08-19 "Stop … one outcome", 08-20 "504s first", 08-24 "reader-visible by Friday" vs 08-25 "Don't panic about the website. Nobody is reading it … never interrupt real work to chase it."
  - The reserved list: the console's four (curriculum values, one-way doors, money, a real person) vs CLAUDE.md's RESERVED_CATEGORIES (real money, real-world commitment, irretractable public claim, real customer/market, live credential — curriculum is a wall, not a reservation) vs DIRECTOR_CANON.md §3's seven; "destroying work" (08-19 21:47) appears in none.
  - Delivery seat scope: 08-25 16:54 ("decides and writes direction rather than code, so it never becomes a second writer") vs 08-25 19:36 ("the delivery seat may act, not only point") — explicitly lifted by the director as his own error.
  - Context handling: 08-20 ("write the handover so the next session starts sharp") vs 08-25 ("a self-written handover is prose it has to reconstruct from; a compact keeps the working state").
  - Fail direction: CLAUDE.md / 08-30 constants review ("fail closed") vs 08-31 runner ruling ("run rather than skip — a false stop costs more than a false start").
  - Reporting cadence: 08-20 "one report at the end of the day" vs 08-22/24 "report when something is done, not between pieces" vs 08-25 "No stopping, ever … not to report" — successive tightenings never consolidated.
  - Verification vs shipping: 08-19 ("no new controls, no new tests, no new findings until that is true") vs 08-21 ("Pushback accepted … the looking is what produced what stuck; judge by whether the investigation converges on a change").
  - Interleave: 08-12 ("one world/customer/product atom per harness atom, every session, unconditionally") vs 08-24 (draw rules handed to the machine; lane-formation measure in its place) — never formally withdrawn.
  - Constants gate scope: the director's 08-30 examples (0.95 churn cap, 53p standing charge) live partly in simulation/, but the ruled gate covers company/ and saas/ only.
  - Annual report: 08-19 06:04 ("make it true … a rendering of data") narrowed by 08-19 11:53 to one production violation plus recorded debt — an explicit narrowing, recorded here so the broader instruction is not re-read as still owed.

Extract written to `/tmp/claude-0/canon/extracts/C1_august.md` (143 entries, all 10 fields present on each, all 26 source files covered).
agentId: a1c9245ece6a0209a (use SendMessage with to: 'a1c9245ece6a0209a', summary: '<5-10 word recap>' to continue this agent)
<usage>subagent_tokens: 367664
tool_uses: 44
duration_ms: 1335557</usage>
