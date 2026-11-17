# CLAUDE.md, one lineage line per rule

*Director steer, 17 Nov 2026 ("Yes", 19:16 GMT):
`docs/staging/advisor/done/DIRECTOR_STEER_EVERY_CLAUDE_MD_RULE_CARRIES_ITS_LINEAGE_AND_EVERY_TRIAL_ITS_MODEL_2026-11-17.md`.
This file sits beside trial E-e (`EFFICIENCY_E_E_MINIMAL_CLAUDE_MD_DRAFT.md`, `EFFICIENCY_E_E_GOLDEN_SET.yaml`).
It is appended to, never rewritten. A rule added to CLAUDE.md later carries its line here in the same commit.*

**How each line was established.** For each rule, `git log --reverse -S'<its words>' -- CLAUDE.md` finds the
commit that first carried the words. Where the 28 Aug rewrite (`3d83edffb6`) only re-worded an older rule,
the older rule's own dated stamp in `git show 3d83edffb6^:CLAUDE.md` is cited, then the commit that first
carried it. **The model** is the `Co-Authored-By` trailer on that commit. Where the commit has none, the
line says `unrecorded`, then in brackets what the other commits that day were signed with. That is context,
not the record. From 4 Sept to 4 Oct no commit carries a trailer, so those lines say `GAP: unrecorded`.
The **incident** column names a path or commit only where one says it. Otherwise it says **GAP: origin unknown**.
The 28 Aug rewrite notes say the eleven habits were "taught by hand in the console" and name no incident for
most of them (`docs/design/CLAUDE_MD_REWRITE_NOTES_2026-08-28.md`). That console record is not in the repo.

Model shorthand: S4.6 Sonnet 4.6 · S5 Sonnet 5 · O4.8 Opus 4.8 · O5 Opus 5 · O5-1M Opus 5 (1M context) ·
O5.5 Opus 5.5. **Minimal arm** (the E-e draft): K kept verbatim, C condensed, D dropped.

**A note the steer's hazard already has in the record.** On 24 Sept a prompt audit found that "a rule
deleted without its reason is one a later session re-adds as an obvious omission — which is how the 200-line
limit outlived its" own deletion (`f325485b4f`). That is the paper's claim, observed here before the paper.

## The mission

| # | Rule | Problem it targets | Introduced by | Model then | Predicted to prevent | Min |
|---|---|---|---|---|---|---|
| 1 | Mission statement | Fidelity was the goal; the line it replaced said so | Director verbatim, 28 Aug; `039f202cec` 2026-08-28 | O5-1M | Work that improves the world without a customer to create value for | K |
| 2 | M2 "Value is created and THEN shared" | Charging the cap counted as value | Same; canon M2 (28 Aug), quoted from canon `6a64ec2750` 2026-10-12 | O5-1M (canon quote: unrecorded) | Transfer booked as creation | K |
| 3 | M3 "Money, time and carbon, above a floor" | Only money had been optimised; time and carbon absent | Mission 28 Aug; amended 31 Oct (`83f5525c6f` 2026-11-02) and 14 Nov (`9a1cfc5a9b`, his words 13 Nov) | unrecorded (2 Nov day: O5.5; 14 Nov day: O5.5) | Pounds-only scoring; a needs vector converted at a rate we choose | K |
| 4 | M4 "The enterprise value is the automated METHOD" | The book read as the asset | `039f202cec` 2026-08-28 | O5-1M | Optimising the book instead of the method | K |
| 5 | "Fidelity is not the goal — it is the precondition" | The mission seemed to demote fidelity | Old file: "Fidelity is not demoted by this; it is given its reason" (`039f202cec`); current words `3d83edffb6` 2026-08-28 | O5-1M | A world that cannot press back | K |

## What you are

| # | Rule | Problem it targets | Introduced by | Model then | Predicted to prevent | Min |
|---|---|---|---|---|---|---|
| 6 | "You hold the delivery seat" | Sessions read 18 rules and inferred they were task-takers | Rewrite notes §"What I added"; `3d83edffb6` 2026-08-28 | unrecorded (day: O5, O5-1M) | Interrupting the director with what the seat should decide | C |
| 7 | "You are not the only writer" | One writer's staged files swept into another's commit | Old "Concurrent writers" (2026-07-05 incident), `390d816e6e` 2026-07-05 | S5 | Sweeping another lane's work; surprise at mid-turn landings | C |
| 8 | "Finishing a piece of work is not the end of your turn" | "say go and I start at R1" stopped the machine | Director's addition 1, rewrite notes; `3d83edffb6` 2026-08-28 | unrecorded (day: O5, O5-1M) | Turns that end on an offer instead of the next step | D |

## How to behave when no rule applies

| # | Rule | Problem it targets | Introduced by | Model then | Predicted to prevent | Min |
|---|---|---|---|---|---|---|
| 9 | "Prefer measuring to arguing" | Disagreements about an unlooked-at number | `3d83edffb6` 2026-08-28. **GAP: origin unknown** (console teaching, no incident named) | unrecorded (day: O5, O5-1M) | Reasoned answers to measurable questions | D |
| 10 | "Knowledge first is a RULE" | Constants picked because a number was needed | Director, 30 Aug, on £150 CAC, a 0.95 churn cap, a standing charge matching neither fuel; `c050706d33` 2026-08-30 | unrecorded (day: O5) | Invented constants that become load-bearing | C |
| 11 | "a finding to file, and the code carries the gap" (honest None) | Placeholders read as established | `c050706d33` 2026-08-30 | unrecorded (day: O5) | A plausible number standing for an unknown | C |
| 12 | K2 "Omission is not neutrality" | The honest-None rule over-read as "leave it out" | Canon K2 (8 Sept, "corrects an over-reading of K1"); in CLAUDE.md `6a64ec2750` 2026-10-12 | unrecorded (day: O5.5) | A near-certain relationship modelled as zero | C |
| 13 | Director's 30 Aug "why this became a rule" paragraph | — (it records why rule 10 exists) | `c050706d33` 2026-08-30 | unrecorded (day: O5) | Re-litigating rule 10 as a preference | D |
| 14 | "Build the smallest mechanism that can fail" | "117 harness atoms and 34 alarm documents" | Director's addition 3, rewrite notes; `3d83edffb6` 2026-08-28. Same hour: a five-leg register became one leg (`test_a_cited_constant_has_a_caller.py`) | unrecorded (day: O5, O5-1M) | Controls that guard controls; registers instead of work | D |
| 15 | "Before measuring a thing, say what it is" | Undefined concepts differenced and published (bill shock, average unit rate, net margin) | Director 1 Sept, half-month DD correction; `5994c17d47` 2026-09-01; canon F11 | unrecorded (day: O5) | A measure of two experiences published as one percentage | D |
| 16 | "Knowledge has three sides" | A correctly sourced measurement in a wrong frame | Same, `5994c17d47` 2026-09-01 (no published source says a half-month DD does not exist) | unrecorded (day: O5) | Trusting published plus code evidence where only a practitioner knows | D |
| 17 | K4 "the practitioner starting point"; "search Ofgem ... before asking me" | Questions to the director that the published record answers | Canon K4 (1 Sept; 6–11 Oct); `6a64ec2750` 2026-10-12 | unrecorded (day: O5.5) | Asking him what Ofgem publishes | D |
| 18 | K8 "knowledge before build" | Capabilities built with no knowledge page | Canon K8 (11 Oct, standing); `6a64ec2750` 2026-10-12 | unrecorded (day: O5.5) | Builds whose rules and gaps nobody wrote down | C |
| 19 | F11 "erring against our own thesis is the safe direction" | Ambiguous evidence read the flattering way | Canon F11 (27 Aug to 9 Sept); `6a64ec2750` 2026-10-12 | unrecorded (day: O5.5) | Flattering tie-breaks | D |
| 20 | R5 "Every run should answer a stated question" | Runs launched without a question | Canon R5 (8 Oct); `6a64ec2750` 2026-10-12 | unrecorded (day: O5.5) | Large runs that answer nothing in particular | D |
| 21 | "Print the numbers at real inputs before you ship a formula" | Formulas wrong across the real range | `3d83edffb6` 2026-08-28. **GAP: origin unknown** (console teaching) | unrecorded (day: O5, O5-1M) | A formula shipped whose table would have shown the error | D |
| 22 | "When a result moves and more than one thing changed" | Attribution of a two-variable move | `3d83edffb6` 2026-08-28. **GAP: origin unknown**. The same commit kept a refuted founder-book inference beside its result | unrecorded (day: O5, O5-1M) | Claims of cause after a confounded change; post-hoc predictions | D |
| 23 | "A mutation that does not fire" | Assuming the flattering equivalence | Descends from R15, CONTROLS_THAT_CANNOT_FAIL (2026-07-13), `a0f1a8853a`; current words `3d83edffb6` | O4.8 (R15) | Untested controls left as "equivalent" | D |
| 24 | "When a branch exists to be taken rarely" | A guard that refuses everything passes every refusal test | "the same trap three times in one afternoon through three different doors"; `1b98c83609` 2026-09-04 | GAP: unrecorded | Unreachable rare branches whose logs read like the mechanism working | D |
| 25 | "Key a control to the property" | Controls pinned to today's answer | Rewrite notes: a probe keyed reachability to a constant's spelling and would have shipped four wrong repairs; `3d83edffb6` 2026-08-28 | unrecorded (day: O5, O5-1M) | Controls that go red on honesty and stay green on rot | D |
| 26 | "Before dividing two numbers" | Ratios that are not quantities | `7bb9daa465` 2026-08-28: "the page had been dividing a renewal count by an account count". The spread-over-estimate case: **GAP: origin unknown** | O5-1M | Misleading published ratios | D |
| 27 | "Write refusals that name their reason" | Refusals that cannot be checked | `3d83edffb6` 2026-08-28. The refusal that was wrong "within an hour of shipping": **GAP: origin unknown**, not found in the records searched | unrecorded (day: O5, O5-1M) | A wrong refusal that nobody can see is wrong | D |
| 28 | "Fail closed, and say so on the surface" | Fail-open and fail-silent controls; unbounded figures | R15's killer patterns (2026-07-13), `a0f1a8853a`; current words `3d83edffb6` | O4.8 (R15) | Figures published without the bound their sample earns | D |
| 29 | "Look for the parked atom before minting" | Duplicate atoms; work parked on abolished blockers | `67a2584214` 2026-08-28: the atom for "the director's biggest problem was parked with nothing blocking it" | O5-1M | Minting what the map already holds | D |
| 30 | "Finish the file before you commit" | Gates read the whole tree | `3d83edffb6` 2026-08-28. **GAP: origin unknown** (no incident named) | unrecorded (day: O5, O5-1M) | One lane's unwired module blocking every commit | D |
| 31 | "Correct yourself plainly ... beside the claim" | Quietly revised predictions | `3d83edffb6` 2026-08-28. Same commit: "My pre-registered inference was wrong and is kept in the finding beside the result" | unrecorded (day: O5, O5-1M) | Losing the evidence an experiment was designed blind | D |
| 32 | "Write for the next session, not for the record" | Comments that recite rules | `3d83edffb6` 2026-08-28. **GAP: origin unknown** | unrecorded (day: O5, O5-1M) | Comments that cost reading and explain nothing | D |

## The operating model

| # | Rule | Problem it targets | Introduced by | Model then | Predicted to prevent | Min |
|---|---|---|---|---|---|---|
| 33 | "Get on with, without asking" (an hour of compute against his attention) | Stalls on reversible work | MAKE_IT_STICK (2026-07-12, "please make it stick this time"), `2b7d1465d1`; operating model `7f736d383c` 2026-10-04 | S5 (MAKE_IT_STICK); unrecorded on 4 Oct | Asking about what the seat should decide | C |
| 34 | "Escalate with a proposal, and don't wait" | Questions that block the queue | Operating model, director 4 Oct; `7f736d383c` | GAP: unrecorded | A stall waiting on an answer | C |
| 35 | "Never ask without recommending" (`recommendation_guard.py`) | Bare "which would you like?" asks | Director NTFY 2026-07-29, `docs/design/NEVER_ASK_WITHOUT_RECOMMENDING.md`; `fe51476cd7` 2026-07-29 | unrecorded (day: O4.8, O5) | Bare asks (also refused in code) | D |
| 36 | "The reservation is narrow" (director documents) | Every file mentioning a goal treated as his | Operating model; `7f736d383c` 2026-10-04; `tools/director_document_gate.py` `a18939f9d` | GAP: unrecorded | Freezing ordinary files; silent edits to his documents | C |
| 37 | G5 "one list" of reserved actions | Seven, then four, then five lists in code disagreed | Canon G5 (ruled 12 Oct, decision 8); predecessor ONLY FOUR THINGS ARE RESERVED (2026-07-29), first carried `102c297909`; current `6a64ec2750` 2026-10-12 | O5-1M (the four); unrecorded on 12 Oct (day: O5.5) | Real-world acts; and gating routine acts like `git reset --hard` | C |
| 38 | G9 "designs that would change something he ruled ... wait for his go" | Builds over his rulings | Canon G9 (ruled 12 Oct, decision 10); `6a64ec2750` | unrecorded (day: O5.5) | Overturning a ruling by building | C |
| 39 | "Own the end-to-end check" | Canon, logic and findings read apart | Operating model, director 4 Oct; `7f736d383c` | GAP: unrecorded | Surprises explained by the convenient cause | D |
| 40 | "Be transparent in something he can read in a few minutes" | Status scattered where he does not read | `7f736d383c` 2026-10-04 | GAP: unrecorded | Work he cannot see | D |
| 41 | G8 "his words carry full authority"; "'yes' and 'go' are complete" | Invented authority checks on his path | NTFY IS THE DIRECTOR (2026-07-29), first carried `102c297909` 2026-08-03; canon G8 `6a64ec2750` 2026-10-12 | O5-1M | PINs, ceremonies or second channels for his yes | D |
| 42 | "NTFY is mothballed" | Pushes he never read | His words 15 Oct 14:08 BST; `565bd6303b` 2026-10-15 | unrecorded (day: O5.5) | Escalating into a dead channel | D |
| 43 | "Silence is validation" | Waiting for approval nobody owes | THE STANDARD (2026-07-29), first carried `102c297909` 2026-08-03 | O5-1M | Holds awaiting an approval | D |
| 44 | "Proposing a new gate or ceremony on his path is itself a defect" | Authority checks added to his path | NTFY IS THE DIRECTOR (2026-07-29); current words `3d83edffb6` | O5-1M (2026-08-03 carrier) | New ceremonies for him | D |
| 45 | "Escalate in `for_the_director`, never in the window" | A question in the pane is a silent stall | ESCALATION_IS_NTFY_NEVER_WINDOW (2026-07-16, P0 wall), `dd81f2cca6`; re-routed `565bd6303b` 2026-10-15 | O4.8 (2026-07-16) | Unattended turns that stop on a question | D |

## The walls

| # | Rule | Problem it targets | Introduced by | Model then | Predicted to prevent | Min |
|---|---|---|---|---|---|---|
| 46 | The epistemic wall | The company reading simulation internals | "company cannot see inside the SIM", `fd7534fefc` 2026-06-20; "Could a real UK energy supplier know this?" `04acaf7916` 2026-06-23 | S4.6 | Ground truth crossing the seam | K |
| 47 | "The company has no route to the real world" (W6) | An egress allowlist presented as a boundary it was not | Director ruling 2026-08-18, `docs/design/COMPANY_HAS_NO_ROUTE_TO_THE_REAL_WORLD.md`; `394bd63229` 2026-08-18 | unrecorded (day: O5, O5-1M) | A socket in `company/` or `saas/` | K |
| 48 | W7 four principles | **GAP: origin unknown** in CLAUDE.md's history; canon dates it 11 Oct (W7 "of 11 October") | `6a64ec2750` 2026-10-12 | unrecorded (day: O5.5) | World and supplier builds that skip freeze-then-solve | K |
| 49 | W11 no personal microdata | Survey microdata in the repo or world | Canon W11; amended 3 Nov on his words; in CLAUDE.md `6a64ec2750` 2026-10-12 | unrecorded (day: O5.5) | Disclosive data leaving the licensed store | K |
| 50 | "Historical ground truth" | Treating 2022 as a scenario | "Historical Ground Truth", `c43b5d37f2` 2026-06-07 (Phase 0a) | S4.6 | Rewriting what happened | K |
| 51 | Baseline/curriculum split | Tuning the world because company results looked wrong | R13 (2026-07-10, MARGIN_REALISM), `63ea04734d` 2026-07-10 | S5 | Goal-seeking the world | K |
| 52 | "HOOK-BYPASS IS A WALL" | Interim bypass shape | 2026-08-09 ruling, `docs/design/SURGICAL_LANDING.md`; exception retired `2de572e72d` 2026-08-10 (OPS5) | unrecorded (day: O5) | `--no-verify` and hand-built merges | K |
| 53 | "Your own sandbox profile" | The agent widening its own permissions | Security profiles (2026-07-11, director in-console), `d942291d9f`; stamp 2026-07-05, rescoped 2026-08-03 | S5 | Self-widened permissions | K |

## Where the rules live, and the two prose-only rules

| # | Rule | Problem it targets | Introduced by | Model then | Predicted to prevent | Min |
|---|---|---|---|---|---|---|
| 54 | The enforcement table as a whole | Paraphrased rules that went stale | Rewrite, on his instruction ("Convert policy to mechanism", MAKE_IT_STICK 2026-07-12); `3d83edffb6` | unrecorded (day: O5, O5-1M) | Prose rules drifting from code | K |
| 55 | Row: a control must be able to fail | Controls that cannot fail | R15, CONTROLS_THAT_CANNOT_FAIL (2026-07-13, director P0), `a0f1a8853a` | O4.8 | Green controls that prove nothing | K |
| 56 | Row: done means the rendered value changed | Claimed-done pages that had not changed | R11, CLAIM_EQUALS_PIXEL (2026-07-10), `dab0edccc7`; retro `2026-07-04-verification-week.md` (R1) | S5 | False completion claims | K |
| 57 | Row: every financial figure carries its clock | Basis-less money figures | R14, CLOCK_TRUTH_AND_THE_BRIDGE (2026-07-12), `2957ecbb88` | S5 | Mixed settled/billed/banked figures | K |
| 58 | Row: a level move is recorded, never authorised | A commit message claiming a level | R16 (2026-07-21), retro `2026-07-21-ledger-is-authority-not-commit-messages.md`; rescoped `102c297909` 2026-08-03 | O5-1M | Unbacked level bumps | K |
| 59 | Row: an absurdity is fixed as a class | Instance fixes of absurdities | R10, DOMAIN_SENSE_AND_COMPLIANCE (2026-07-09), `6152a7fc6d` | S5 | The same absurdity recurring | K |
| 60 | Row: outputs are diagnostics, never targets | Tuning toward a benchmark | R12, MARGIN_REALISM (2026-07-10), `63ea04734d`; retro `2026-08-03-a-diagnostic-pinned-as-a-target-wedged-publishing-four-days.md` | S5 | Goal-seeking | K |
| 61 | Row: the world must be able to defeat the company | Capabilities never tested against a hostile world | COUPLED TRIAD (2026-07-13, atom A6), `1a25fbbee7` | O4.8 | Untested company capabilities | K |
| 62 | Row: a waiter names its subject and carries a deadline | `until ! pgrep -f` matched its own cmdline (12 h burned) | R18 (director 2026-08-27, `docs/design/WAITERS_NAME_THEIR_SUBJECT.md`), `71cdda78a5` | unrecorded (day: O5) | Waiters that never exit | K |
| 63 | Row: the permission machinery stays deleted | Machinery that outlived its deletion | Retro `2026-08-03-the-permission-machinery-outlived-its-own-deletion.md`; `102c297909` | O5-1M | Permission gates returning | K |
| 64 | Rows: canon drift, staging rooms | **GAP: origin unknown** (the rows enter with the rewrite and the mission commit; no incident named) | `3d83edffb6`, `039f202cec` 2026-08-28 | O5-1M (`039f202cec`) | Canon page and code drifting; staging piling up | K |
| 65 | Row: a cited money constant must be reached | A sourced £55 CAC unreached beside an invented £150 | Rewrite notes; test pinned to `a1aefccaf`; `3d83edffb6` 2026-08-28 | unrecorded (day: O5, O5-1M) | Sourced constants with no caller | K |
| 66 | Row: a domain constant declares its origin | £150 CAC, 0.95 churn cap | `c050706d33` 2026-08-30 | unrecorded (day: O5) | Unsourced rates and caps | K |
| 67 | Row: this file's size limit, in characters | A line limit that paid for 1,000-character lines; `wc -c` counts bytes | 35k limit `04acaf7916` 2026-06-23; MAX_LINES deleted `3d83edffb6` 2026-08-28 | S4.6 (limit) | Unbounded CLAUDE.md | K |
| 68 | Routine creation | A live Routine got full Bash/Write/Edit against its report-only constraint | ADVISOR_STEER_ROUTINE_SCOPE (2026-07-11), `6ca6ac553f` 2026-07-10, `adbc40db5d` 2026-07-11 | S5 | Over-scoped Routines | K |

## Working here

| # | Rule | Problem it targets | Introduced by | Model then | Predicted to prevent | Min |
|---|---|---|---|---|---|---|
| 69 | "Orient first" (poll staging) | Unread staged work | Staging watcher `11071de938` 2026-06-12; current words `3d83edffb6` | unrecorded (06-12) | Starting on something other than the ranked queue | C |
| 70 | "review INTERCONNECTION" | A VAT defect fixed in one of five implementations, still live in another a month later | Director 2026-08-30; `c050706d33` | unrecorded (day: O5) | Downstream disagreement unnoticed after a landing | D |
| 71 | "read the knowledge layer BEFORE you make a number up" | No pointer to the knowledge layer; £55 unreached for seven weeks | Director's addition 2, rewrite notes; `3d83edffb6` 2026-08-28 | unrecorded (day: O5, O5-1M) | Invented constants | C |
| 72 | "Commits take more than ten minutes"; pre-run the cheap gates | Four gate cycles lost on 28 Aug | Rewrite notes ("That cost me four cycles today"); `3d83edffb6`; gate count corrected `aef0e939c4` 2026-10-04 | unrecorded (day: O5, O5-1M) | Serial gate refusals, each a full cycle | C |
| 73 | "Writing a map row ... ask its headroom" | 693 bytes of headroom, below a median commit; six paragraphs pasted thirty times | `8ab0ce8be9` 2026-09-17 | GAP: unrecorded | Reddening `tests/design/` for every lane | C |
| 74 | "Commit by pathspec, never `-A`" | Sweeping other lanes' staged work | Concurrent writers (2026-07-05); pathspec words `52693115b9` 2026-08-03 | O5-1M | Sweeps | C |
| 75 | `isolate_hunks` / `surgical_land --content` | Another lane's in-place edit inside your pathspec, twice on 4 Sept | `3236963419` 2026-09-04 | GAP: unrecorded | Waiting hours on another lane; wrong "cannot land" reports | C |
| 76 | "A new module needs a REUSE block" | **GAP: origin unknown** for the gate itself (not traced here); words enter with the rewrite | `3d83edffb6` 2026-08-28 | unrecorded (day: O5, O5-1M) | Duplicate modules | C |
| 77 | "Cache reads are the bill"; serial by default; never poll | 18% of the weekly allowance in under 10 h; 1.23B cache-read tokens; 54 forks; 33 poll exits | TOKEN BUDGET IS BINDING AGAIN (2026-08-03), `52693115b9`; "Don't wait" `05c12b959f` 2026-08-27 | O5-1M | Fork and poll spend | D |
| 78 | "Route the ones you do spawn by what they do" (haiku/sonnet for search) | Opus contexts spent on search | Director 2026-09-24 prompt audit; `f325485b4f` | GAP: unrecorded | Search on the dearest model | D |
| 79 | "Four procedures live outside this file" | A moved-out procedure nobody points at is never run | HARNESS_SKILLS_AND_RULES (2026-07-12), `61c6f7243d` | S5 | Skipped phase-close and staging steps | C |
| 80 | Who and what: the roster of concurrent daemons and timers | Manifest read as the whole roster | `aef0e939c4` 2026-10-04 (F3) | GAP: unrecorded | Surprise at timer-driven writers | D |
| 81 | "No local model" | CLAUDE.md said qwen did triage and discovery seven weeks after its eviction | `94ef1e36ef` 2026-09-27 | GAP: unrecorded | Routing work to a dead endpoint | D |
| 82 | Memory figure "read it, never quote it" | 14 sim-runner OOM kills; the host's 32 GB quoted for the guest's | Director mid-outage 2026-08-24; `46d17865a8` 2026-08-26 | unrecorded (day: O5) | Sizing runs from a stale figure | C |
| 83 | Build line kept, with its parser note | A past audit deleted it as stale and broke the site's parser | Build figure `2d405ff79e` 2026-07-10; parser keyed to the figure in `3d83edffb6` | S5 | An unstamped live site | K |

**Counts.** 83 lines: 34 dropped (D) in the minimal arm, 20 condensed (C), 29 kept verbatim (K). Ten lines
carry **GAP: origin unknown** for the rule or its named incident (9, 21, 22, 26, 27, 30, 32, 48, 64, 76; 22 and 26
in part). On 49 lines the cited commit carries no model trailer. **No line records a model the rule was tested
on**, because none was tested on any model before it was written. That is the dimension the steer says goes
stale. Trial E-e is the first test of any of them on a named model (Opus 5.5).

## Appended lines

*New and changed rules go below, one line each, in the commit that changes CLAUDE.md.*
