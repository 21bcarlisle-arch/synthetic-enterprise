<!-- PARKED in_progress 2026-07-23 ~19:45Z (worker tick). OPEN SUB-ITEMS ONLY:
  §1 UNWEDGE — DONE. Cause: SITE_V5 surface-1 rebuild (eb94267b1) dropped the /method/ nav
     link from site/index.html; Phase-RQ invariant test_every_site_page_links_to_method blocked
     the content publish gate. Fixed (Method restored on the secondary 'also' line, dd45de549),
     gate green (18695 passed), committed 1a29fe3b0, pushed live.
  §2 PROVE LIVE — DONE (R11): poesys.net renders <a href="./method/">The Method ></a>; five-door
     nav intact; surfaces world/company/proof/now all 200 live. (/method/ 301->/proof/ = the
     deliberate "Method folds into Proof" fold; link lands on a real 200 page.)
  §3 MECHANISE (OPEN) — director part 3: a publish-gate wedge >60min = priority-zero rung-1
     DRAWABLE work (R15 failing-test-first reproducing today's gate-red/tick-idle state).
     PLUS the class defect this exposed: the site-lane PRE-COMMIT scope (test_home_door,
     front_door_brand, evidence_links, expert_doors_mobile) does NOT include
     test_nav_story_platform_method_rq, so a front-door rebuild lands green-locally while
     wedging the publish gate (R2 scope gap). Class fix: site-lane pre-commit must run the
     nav-story reachability invariant (or the publish-gate content-test set).
  §4 NTFY [STATUS] — DONE this tick.
  UNBLOCKS-ON: §3 built + R15-proven. Everything else is closed. -->

# [DIRECTOR-RULING] — Publish gate wedged 3.5h and escalating: PRIORITY ZERO. Diagnose, fix, republish, prove live. (2026-07-23)

**Type:** [DIRECTOR-RULING] via advisor bridge.

## 1. Unwedge, with the harder questions answered (R9 — evidence, not narrative)

The run-complete publish gate has failed 12+ consecutive times since ~15:55Z and the tick has been silent since 16:53Z. Diagnose and fix now, and answer three things with evidence: **(a)** the cause — and whether it is the same class this morning's R10 commit-time-gate fix addressed; if same class, why the fix did not prevent recurrence (R2 deployment gap? bypass path? different entry point); if new class, name it. **(b)** the 16:53Z→now tick silence — were turns attempted and dying at the gate (enumerate them), or did the draw rest; either answer feeds the enumeration. **(c)** whether any queued publish backlog will flush cleanly or needs replay.

## 2. After the unwedge: prove the rebuild is LIVE

The director must not judge stale pages. Republish, then **R11 pixel-verify on poesys.net**: front-door iteration 2, surfaces 3/4/5, and the canon-fed lay page state. One [STATUS] NTFY listing exactly which surfaces are now visible live, with their row-scored self-claims against the axis-1 verdict doc.

## 3. Standing rule (mechanise): a wedged publish gate is rung-1 work

A publish-gate wedge older than 60 minutes is **priority-zero drawable work at the top of the hierarchy** — alarms alone do not fix gates. R15: reproduce today's state (gate failing, alerts firing, tick idle) as the failing test; the draw must produce a diagnosis turn, not silence.

## 4. Also in the same [STATUS]

The sanity daemon's 18:11Z NEW category finding, reported in full (advisory class, verify-before-acting). And today's daily note carries this wedge window explicitly in the utilisation and product/machinery split — 3.5 wedged hours are not neutral.

**Risk & proportionality:** gate diagnosis + fix with failing-test-first; republish is standard pipeline. Tag: **priority zero; proceed.**

— Advisor bridge, 2026-07-23.
