# SURFACE_FRESHNESS_CLASS_FIX — kill the stale-website class for good (P1, queued not urgent)

**Staged:** 2026-07-11 by advisor, director-decided. **Do not interrupt** the
current spike queue (Doors 1-2, margin Step 4, digest) — take this at the next
natural boundary. **Map cell:** Lane H (HARDEN) + every company lane's surface.

## The class (not the instance)
The director has now caught stale/wrong website surfaces FOUR times in five
days: (1) stale phase/test stamps, (2) midnight dashboard.json behind "fixed"
graphs, (3) roadmap section outdated, (4) today: the Platform/agent-health page
reads "Status updated 1.5d ago" — daemon statuses, session history (stops
07-09) and the build-cadence chart (ends 07-10, missing yesterday's 114 commits
and today's 59) all frozen. Each was fixed as an instance. The class is alive.

**The real failure is not the stale page — it is that the freshness invariants
mandated in CLAIM_EQUALS_PIXEL did not alarm on a 1.5-day-old stamp.** A
detector that misses a day-and-a-half-old surface is not a detector.

## Requirements
1. **Complete coverage, provable.** Enumerate EVERY rendered surface and every
   data file behind them (site/**, all JSON, all charts, every panel). Produce
   the inventory. Any surface not covered by a freshness invariant fails the
   suite. No exceptions, no opt-outs.
2. **Root-cause the miss.** Why did the invariants not cover the agent-health/
   platform page? Report which OTHER surfaces were silently outside coverage —
   that list is the evidence the sweep was real.
3. **Regeneration is not optional.** Every surface must have a defined
   generator + trigger (run complete / deploy / daemon cycle). A surface whose
   data cannot be regenerated on demand is a defect. Wire the ones that aren't:
   agent-health/daemon statuses, session history, build cadence, and anything
   else the sweep finds.
4. **Tolerances by class**, alarm on breach: live ops data (minutes), run data
   (per run), narrative copy (days). Breach = NTFY, not a silent log line.
5. **Orphan-transition audit** (rule already exists, evidently not enforced):
   every generator/publish path must have a test proving its trigger fires and
   the surface changes. Deploy without regeneration = failing test.

## Definition of done
Inventory committed; every surface invariant-covered (prove with a deliberately
staled artefact caught within one cycle); the four historical instances all
re-verified live and fresh; the "other uncovered surfaces" list reported; one
digest line. Pixel rule applies. R10: this closes as a CLASS fix — instance
patches do not satisfy it.
