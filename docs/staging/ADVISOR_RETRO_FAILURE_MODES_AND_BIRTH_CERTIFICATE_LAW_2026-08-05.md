# [ADVISOR-RETRO] — Failure modes of the last few days, and one law that prevents the class (2026-08-05)

**Type:** [RETRO — findings, patterns, candidate laws]. Director-commissioned: "these all feel like quite basic errors — prevent the same failure modes and think laterally." Evidence base: the structural audit, missing-test-tier review, credit-balance research, data-architecture review, taxonomy audit, and the harness's own July record. Candidate laws are for CC to **adopt / adapt / reject with evidence**, the established pattern. Nothing here duplicates fixes already in flight — those are credited and pointed at.

## What was found, clustered by failure mode

**FM-1 Write-time blindness** (create without checking what exists): duplicate billing ledger (2×2.4MB), duplicate atom numbers (two H23s, H24s, H27s), hand-rolled working-day calculator while `holidays`/`workalendar` exist, 22 lane prefixes with no registry, B9=E5. *Already in flight:* the ARCHITECTED-OUT programme's write-time gate + capability index + ecosystem question + mint number registry. This mode is covered — the retro adds nothing to it.

**FM-2 Stores born without lifecycles** (everything that accumulates, rots): done/ drawer at 4,909 files burying 78 real instructions; map spine 89% eaten by embedded simplifications; site snapshots accumulating with no retention rule; historical run outputs turning the repo into a database; the naive organ's 10.7MB log = 94% of the entire append-log estate. Five independent instances, one shape: **at birth, nothing declared how it would grow or die.**

**FM-3 Fields without contracts** (schema drift in governance data): file_scope holding whole directories so the lane wall cannot arbitrate; dependency edges holding prose sentences; the same field string-or-list by mood; provenance carrying zero dates while the company layer underneath is scrupulously bitemporal. The map has 18 fields and no validator — governance data is not held to the standard the codebase holds itself to.

**FM-4 Checks that pass emptily** (silence is the failure mode): credit-note netting made the billing reconciliation succeed while a −£202 balance sat unreleased for 3.5 years; 14 guards untested; two hooks went silently inert; 1,109 unit tests passing while every serious failure was parts-pass-system-fails (10 e2e, 1 integration). *Partly in flight:* NET join tests, mutation-test atoms (H12/H18). The uncovered residue: **reconciliation-class checks** — nobody has ever forced one to fail on a planted defect.

**FM-5 Migrations without a definition of done:** seven daemons systemd-AND-tmux for weeks; the bitemporal event log built but joined to nothing while persistence runs beside it un-logged; charter debt (H at 13 atoms past the earn-threshold). Starting is recorded; finishing is nobody's field.

**FM-6 Artefacts without a designed reader:** the map unreadable by its one human reader — now fixed by the naming law; LATEST carrying ~100 near-duplicate organ questions no one could consume. The site already had the didactic rule; internal surfaces didn't.

**Advisor's own ledger (same standard applies):** consumed a whole context window by reading documents into chat instead of to disk; read PROJECT_OVERVIEW for state when canon says LATEST; drafted approval gates into a see-and-correct project; first H cut grouped by method not subject; a truncated diagnostic once cost a day. Corrections adopted: fetch-to-disk, canon-first for state, gate-after language, subject-not-method, never-truncate. Recorded so drift from these is checkable.

**Credit where the system caught itself:** the naive organ and the structural audit *surfaced* several of these; the stall-class register, double-launch guard, and cutover atom already existed for FM-5's daemon case; the director caught B9=E5 and the taxonomy unreadability. Discovery organs work. What's missing is not detection — it's **contracts at creation time.**

## The lateral move: one law, not five patches

Every failure mode above is the same event at a different layer: **something persistent was born without a contract.** A store without a lifecycle, a field without a schema, a check without a proven failure, a migration without a finish line, a surface without a reader. The codebase's *code* has contracts (tests, gates); everything *around* the code was born contractless.

**Candidate law — the Birth Certificate:** anything that persists declares, at creation: its **reader** (who consumes this and can they), its **writer** (single-writer named), its **bound** (how it grows: capped / rotated / archived — "unbounded" must be written down to be chosen), its **death** (retention or retirement criterion), and — for checks — its **proven failure** (the planted defect it has caught at least once). Enforced where creation already passes a gate: the write-time gate checks the certificate exists; the housekeeping sweep audits reality against certificates instead of guessing what matters.

Concrete instantiations for adopt/adapt/reject, in evidence order:
1. **Lifecycle certificates for the five known rotters** (done/, map simplifications → sibling store per taxonomy review, snapshots, run outputs, organ logs) — retro-issue certificates, sweep enforces. (FM-2)
2. **The registry is code:** a schema + one validating test for `maturity_map.yaml` and sibling governance YAMLs; type, id-grammar, edge-must-be-id, dated provenance. Runs in the existing gate. (FM-3)
3. **Organ output budgets:** every writing organ gets a dedup key and a daily byte/item budget in its certificate; the naive organ first. (FM-2/6)
4. **Reconciliations must be seen to fail:** extend the mutation-test discipline to reconciliation-class checks — plant one defect per reconciliation (the credit-balance case is the first planted defect, already specified in the credit research). (FM-4)
5. **A migration ledger with finish lines:** every cutover records its retirement criterion at start; the process reconciler already reports drift — it gains the ledger and reports "started, not finished" as a standing class. (FM-5)

## What this is not
Not a refactor mandate, not new organs, not process ceremony — five certificates and one small validator, attached to gates and sweeps that already run. If CC finds a cheaper mechanism achieving the same contracts, that is an adapt verdict and welcome. Reject verdicts need evidence, per the standing pattern.

— Advisor retro, 2026-08-05, machine offline; lands with the Saturday batch.
