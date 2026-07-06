[PROJECT] PROJECT TAB OVERHAUL -- director critique of all six sub-tabs. Core rule: hand-written content is banned; everything derives or dies.

CRITIQUE FINDINGS (Rich's screenshots, 05 Jul):
- CONSISTENCY BREACH: Overview shows net GBP1,534,757 / treasury GBP3,835,512 / 15,148 tests vs canonical run artifact GBP1,445,258 / GBP3,911,894 / 15,6xx. Two surfaces, two truths -- the QF consistency gate does NOT cover project/ surfaces. "Sim runs: 10" is a dead counter. Diagnose which number is which run and make ONE canonical run feed everything.
- Broken charts: phases-per-day stops 2026-06-25 with one absurd bar; both charts have duplicate x-axis date labels.
- Timeline stops 2026-07-03 (hand-curated) -- missing the entire decision-loop/evidence-surface era.
- Capabilities cards frozen at writing date, no links to the evidence surfaces that now exist.
- Company tab duplicates Overview's About.
- System (agent health) is the hidden gem -- unique content, keep and elevate.

THE STANDING RULES (this is the "stays good and gets better" brief):
R-A. NOTHING HAND-WRITTEN ON THESE SURFACES. Every number, chart, timeline entry and capability card GENERATES from canonical artifacts (run output, phase history, PROJECT_OVERVIEW build log, retro files, module inventory). If a fact cannot be generated, it does not appear. Prose framing paragraphs may be static but carry no numbers.
R-B. CONSISTENCY GATE EXTENDED to project/ (and every future surface): the 8-metric cross-surface check covers Overview investor summary, Capabilities header, and any stat anywhere. Gate failure = NTFY, never silent.
R-C. FRESHNESS STAMP per sub-tab (run_id + generated_at + phase), per the site laws.
R-D. DESIGN LAWS v4 APPLY (light theme, progressive disclosure inline, no popups, UK lens, reconciliation).

PER-TAB DIRECTION:
1. OVERVIEW: investor summary auto-generated from latest run + repo stats; fix both charts (correct date axes, full history); KEY DISCOVERIES stays but each card links inline-expand to its evidence (run data, phase entry); roadmap items derive from PRIORITIES.md status.
2. TIMELINE: auto-appends from the phase/build history -- milestones tagged in phase commits or PROJECT_OVERVIEW entries flow in automatically; DISCOVERY entries from the discoveries register; never ends before the current phase. Test-count chart from the actual per-phase series.
3. SYSTEM: elevate -- add session history (starts/ends/exit reasons from watchdog log), staging queue state, burn line (measured source only), uptime/continuity strip. This page is the autonomous-company org chart; make it a showcase piece.
4. COMPANY: de-duplicate with Overview; repurpose as HOW IT IS BUILT -- the harness story: governance model (tiers, staging, 4h windows), the permanent rules (R1-R6 + design laws), retro practice, links to retrospectives. The durable-IP page.
5. REGULATORY: keep structure (it is good); each scheme row inline-expands to its rates table and links to its board-pack section; WIRED/EXEMPT/NEXT chips derive from the module inventory.
6. CAPABILITIES: cards generate from a capabilities register (name, one-liner, headline numbers FROM THE LATEST RUN, link to evidence surface per EVIDENCE_IN_BUSINESS_SURFACES). New capability phases append their card at phase close automatically -- the tab grows with the build.
7. Future (WEBSITE_AS_SHOWCASE tab 3 lands here): learning ledger + delta-EV-vs-baseline curve + SaaS coverage map + retrospectives join Project as the accumulation story.

Acceptance: advisor verifies cross-surface number agreement via the canonical channel; Rich's eyes for the visual bar. Report "awaiting review", not done.
