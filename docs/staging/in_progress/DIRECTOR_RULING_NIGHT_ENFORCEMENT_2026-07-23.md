<!-- [CC PROCESSING STATUS -- 2026-07-23 NIGHT] IN PROGRESS. Actioned this tick:
  §1 hierarchy+planner: RUNG 4 (declared-defect backlog) BUILT + R15-proven + LIVE (flip demonstrated:
     all-empty/REST-LEGITIMATE -> defect_backlog=Y/MUST-DRAW). supervisor.py::_declared_defect_backlog_draw
     + docs/design/DECLARED_DEFECTS_REGISTER.yaml + tests/background/test_defect_backlog_draw.py (7 tests).
  §2 seeds MINTED (3 propose-docs in docs/design/proposals/): spike-tail attack plan; premise-demand
     publish Spec-003; scenario follow-ons ranked (= the rung-5 data source).
BLOCKING / STILL OPEN (drawn next ticks, named honestly per the ruling's own "honest reds credited"):
  §1 RUNG 5 (follow-ons draw rung) + RUNG 7 (PLANNER rung). Rung 7 deferred on a REAL FINDING, not
     caution: maybe_emit_graduation_proposal fires only in the quiet-rest branch, so a planner that makes
     rest unreachable would silence the forward-discovery graduation [ACT] to the director -- that must be
     decoupled first. Blind-landing it in an unsupervised night tick is the forbidden "tired mega-turn."
  §3 campaign (diagram front door / evidence / RC6) -- not touched this tick; drawn next.
  §4 whole-set enumeration in the status line -- ALREADY LIVE (authorized_set_enumeration_line), now
     with defect_backlog included.
Parent ruling: docs/staging/in_progress/DIRECTOR_RULING_WORK_IS_THE_DEFAULT_2026-07-23.md. -->

# [DIRECTOR-RULING] — Night enforcement: the hierarchy gets BUILT tonight; the seeds get MINTED tonight; the 07:00 note is pass/fail (2026-07-23)

**Type:** [DIRECTOR-RULING] via advisor bridge. Finding on the record (R9, advisor-verified against the ledger): the WORK_IS_THE_DEFAULT ruling was consumed at ~14:55Z and its mechanism has produced **zero commits in six hours** — no hierarchy/planner build, and none of the three seeded proposals minted (spike-tail attack plan: six days untouched; premise-demand publish; scenario follow-ons ranked doc). Rung-1/2 work was excellent all evening; rungs 4–7 exist only on paper. Consumed is not absorbed. The advisor's share: reported consumption without verifying the build — logged in the advisor column.

## Tonight, in this order, before any further campaign polish

1. **Build the work-source hierarchy + planner rung** per the ruling — the R15 pair (populated-goals-with-empty-tasks ⇒ MINT not rest, reproduced as the failing test first; genuinely-empty ⇒ rest with the full enumeration published) plus the existing mutation tests. This is the class-of-classes fix; it does not slip another day.
2. **Mint the three seeds** as propose-docs with their windows: spike-tail attack plan; premise-demand publish (Spec-003 two-level bar); scenario follow-ons ranked. These were ordered this afternoon; minting them is drawable work under the ruling they came from.
3. **Then** the campaign continues: diagram-led front door (director's v4 asset is the reference), evidence pages, RC6 unit-economics pass.
4. Every rest tonight publishes the **whole-set enumeration** in the status line. An unenumerated gap >45 min in tonight's window is, per the director's standing ruling, an automatic R10 breach — the daily note names it as such without being asked.

## The 07:00 note is pass/fail on this list

PASS requires: hierarchy+planner live with tests; three seeds minted; diagram front door landed or its turn evidenced; ≥2 evidence/RC6 items; F1 levels twin-ratified ledger-backed; zero unenumerated >45-min gaps. Anything missed is named with its rung and reason — honest reds credited, silent misses are the breach.

**Risk & proportionality:** enforcement + sequencing of already-ratified work; no new scope. Tag: **proceed, order fixed.**

— Advisor bridge, carrying the director's challenge verbatim: "You are condoning doing nothing all night?" — No. 2026-07-23.

---

## ADDENDUM (same evening) — the mechanical finding: the parked-into-blind-spot bug

Advisor-verified from the ledger: at 20:00Z the campaign's remaining items were parked into `docs/staging/in_progress/` — **the directory the work scanner deliberately excludes** — after which the scanner found "nothing drawable" and the tick idled 56+ minutes with an open campaign. The system filed its own to-do list into its own blind spot. This is tonight's named failing test alongside the hierarchy R15s: **parked-campaign-with-open-items must be drawable** (either the classifier reads open items wherever they are parked, or open campaign items are never parked into the excluded directory — pick the mechanism, prove it both ways). Additionally: full-day utilisation computed at ~26% (3.9h active / 15.3h, seven >45-min idle windows) — tonight's note reports its own number against this baseline.

---

## SAFETY RAILS (director + advisor, added before the granted-turn revival) — how tonight's odds get improved

The night's largest risk is precisely the ordered work: the hierarchy build modifies find_work — **the component that just crash-looped from its own last self-edit.** Four rails, mandatory tonight:

**RAIL 1 — Shadow-then-swap for ANY scanner/draw edit.** The new hierarchy draw logic is built as a parallel module, never an in-place edit. Each tick runs the OLD scanner for real draws and the NEW one in dry-run, logging divergence. Swap only after ≥10 clean shadow cycles AND the R15s pass; keep the previous scanner file for one-command revert. If shadow shows divergence that can't be resolved quickly: **HOLD on the old scanner overnight** — seeds and campaign remain drawable on it — and swap at coffee. A held swap is a pass, not a miss.

**RAIL 2 — Crash-loop immunity in the tick.** Wrap the scanner call: on exception, (a) page immediately — "SCANNER EXCEPTION: <error>" — and (b) fall back to the last-known-good scanner copy for that tick. Tonight's silent hour becomes a loud minute, and a bad edit degrades to noise instead of death. Build this BEFORE touching the scanner.

**RAIL 3 — Advisor-checkable heartbeat.** Every tick writes one line (timestamp · drew/rested/exception · the whole-set enumeration) to a status file **shipped by the existing auto-publish** — so liveness is verifiable from origin every ~6 minutes without SSH, by director or advisor. The supervisor pages if the heartbeat stalls or shows exceptions for >5 min.

**RAIL 4 — Risk-first sequencing.** Rails 2–3, then the shadow build, all in the FIRST hours while the director and advisor are still on watch; one NTFY when the shadow verdict is in ("shadow clean, swapped" or "divergent, holding on old scanner"). Routine work (seeds, campaign) fills the rest of the night on whichever scanner is live. Nothing structural after that NTFY until morning.

— Addendum 2, same evening.
