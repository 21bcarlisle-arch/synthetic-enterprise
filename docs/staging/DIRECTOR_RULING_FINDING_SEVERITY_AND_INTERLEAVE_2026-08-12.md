# [DIRECTOR-RULING] — Findings get severity; severity gates progress; blockers jump the queue (2026-08-12)

**Type:** [DECISION]. Replaces the count-based interleave trigger in DIRECTOR_PRIORITY_BACKLOG_TRIAGE_AND_INTERLEAVE_2026-08-10. Mechanisms are the worker's; the properties below are the director's.

**The problem, measured this morning:** staging root at 111 files, 103 of them self-generated findings, 45 filed on one day. The interleave was gated on that count dropping under 20 — a number that measures the rate of self-scrutiny, not the state of the project, and which has grown every day since the rule was made. A crude instrument, and mine; withdrawn.

**Also measured: the pile has families, not 111 distinct problems.** Clustering by subject gives at least five: publish-gate/wedge (~18), controls that cannot fail — vacuous, fail-open, blind (~9), measurements that mirror the thing they measure (~7), uncommitted/orphaned work (~7), no-caller/never-runs (~5). Roughly 46 documents are five classes with instances.

## Ruling

**1. Consolidate by class.** Where findings share a class, they become one class document with an instance list and a cumulative cost line, superseding the individuals (archived, not deleted). A class with a live instance list is the artefact that can win a draw; twenty siblings filed separately cannot. Campaign findings (e.g. an Expert Hours sweep) are filed as one document with instances, not one per instance.

**2. Every finding carries a severity, and severity is the gate — not the count.**
- **BLOCKING** — a control or instrument in this area is untrustworthy, or a published figure may be wrong. **New level-raises in the affected lane are refused until it is repaired, or until the limitation is explicitly recorded and accepted.** Progress in every other lane continues untouched.
- **LATENT** — real defect, does not invalidate anything published or any control's verdict.
- **RECORDED** — known limitation, accepted, no work owed.
Unclassified findings default to LATENT only if the finding's own text supports it; where the finding says an instrument is wrong, it is BLOCKING by construction. Deciding one's own finding is not BLOCKING to keep a lane open is the anti-pattern this clause exists to forbid.

**3. Blockers outrank housekeeping.** A BLOCKING finding draws ahead of the general disposition queue, ahead of latent findings, and ahead of new feature work in its own lane. The drain proceeds around it.

**4. The product interleave arms NOW, unconditionally.** One world/customer/product atom per harness atom, every session, regardless of staging depth. It is no longer coupled to a document count. It remains subject to clause 2: a lane with a live BLOCKING finding takes the repair as its product-side draw until cleared.

**Rationale, for the record:** building on top of a known-broken instrument means the new work is certified by something we already know is lying. That is the one thing this project cannot afford, since its entire claim rests on published figures being checkable.

## WORK THIS CREATES (canonical, in-document)
1. The severity field, applied across the existing staging root — one pass, every finding classified. 2. Class consolidation for the five named families, with instance lists and cumulative cost. 3. The lane-level refusal mechanism for BLOCKING findings, provably failable. 4. Blockers wired ahead of the disposition queue. 5. The interleave armed and its draws visible in the tick digest.

— Ruled 2026-08-12; staged by the advisor; the count-based trigger is withdrawn by the same hand that proposed it.
